"""Tests für die Bibliothek als sechste Kontextquelle des Enrichers.

Ziel: Was Nova erarbeitet hat, wird im Gespräch gefunden — über die
Metadaten, mit demselben Suchschlüssel wie KZG und LZG, und nur aus der
eigenen Beziehung.

Die vier Zusicherungen:

  1. **Der Schlüssel kommt aus dem State.** Der Manager rechnet kein
     eigenes Embedding; ohne Schlüssel fragt er gar nicht erst.
  2. **Die Paar-Trennung hält.** Ein Treffer aus einer fremden Beziehung
     ist der Defekt, gegen den das ganze Paar-Schema gebaut ist.
  3. **Nur `typ='wissen'`.** Berichte sind Prozessdokumentation; im
     Gesprächskontext wären sie Rauschen (§7.5).
  4. **Das Gewicht wird auf die Skala des Pools gebracht.** Die Bibliothek
     rechnet bis 10.0, der ContextEntry-Pool bis 1.0 — ungerechnet schlüge
     jeder Bibliothekseintrag im Reducer jeden KZG-Treffer.

Dazu die Zusicherung des Umbaus am Enricher: **Wenn ein Plugin läuft, steht
der Suchschlüssel im State.** Vor dem 04.08.2026 liefen die Plugins, bevor
das Prompt-Embedding überhaupt erzeugt war.

Die Zeugen: Die Embeddings des Fixtures sind Einheitsvektoren von Hand —
`[1,0,0,…]` und `[0,1,0,…]` stehen orthogonal, ihr Kosinus ist 0.0 und 1.0
exakt und nicht ungefähr. Damit ist die Schwelle prüfbar, ohne dass ein
Modell befragt werden muss.

Das Fixture bringt eigene Kennungen mit und räumt sie in tearDown ab: Die
Suite läuft gegen die Produktiv-Datenbank.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
import uuid
from contextlib import ExitStack
from unittest.mock import MagicMock, patch

import graph.nodes.enricher as enricher_mod
import psycopg2
from config import LZG_KNOTEN_GEWICHT_CAP, POSTGRES_URL, WISSEN_RETRIEVAL_SCHWELLE
from plugins.wissen_manager.manager import WissenManager

DIM: int = 768

# Zwei orthogonale Einheitsvektoren. Der Kosinus zwischen ihnen ist exakt
# 0.0, der eines Vektors mit sich selbst exakt 1.0 — beides ohne Modell.
NAH:  list[float] = [1.0] + [0.0] * (DIM - 1)
FERN: list[float] = [0.0, 1.0] + [0.0] * (DIM - 2)

MENSCH:    str = "test_wism_mensch"
CHARAKTER: str = "test_wism_nova"
FREMD:     str = "test_wism_fremder"

PFAD_PRAEFIX: str = "/knowledge/autonomous/test_wism/"


def _vektor_str(vektor: list[float]) -> str:
    """Baut das pgvector-Literal eines Vektors."""
    return "[" + ",".join(str(w) for w in vektor) + "]"


class WissenManagerTest(unittest.TestCase):
    """Der Abruf der Bibliothek über ihre Metadaten."""

    def setUp(self) -> None:
        """Erzeugt eine testeigene Marke."""
        self.marke: str = uuid.uuid4().hex[:10]
        self.manager: WissenManager = WissenManager()

    def tearDown(self) -> None:
        """Loescht alle Zeilen des Fixtures."""
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM autonomous_wissen WHERE dateipfad LIKE %s",
                    (f"{PFAD_PRAEFIX}%",),
                )
            conn.commit()
        finally:
            conn.close()

    def _zeile_anlegen(
        self,
        *,
        vektor:  list[float],
        typ:     str = "wissen",
        user_id: str = MENSCH,
        gewicht: float = 3.96,
        thema:   str = "",
    ) -> str:
        """Legt eine Metadatenzeile per direktem SQL an und gibt ihren Pfad zurueck.

        Bewusst nicht ueber das Repository: Sonst liefe die Erwartung durch
        dieselbe Funktion wie das Ergebnis.

        **Seit Konvention 4 gehoert die Themenzeile dazu.** Der Lesepfad
        vergleicht gegen `autonomous_wissen_thema`, nicht mehr gegen den
        gemittelten Vektor der Zeile; eine Ausarbeitung ohne Themenvektor ist
        fuer ihn unsichtbar. Das Fixture legt beide an — sonst pruefte der
        Zeuge einen Bestand, den es nicht mehr gibt.

        Derselbe Vektor steht in beiden Spalten. Das ist hier richtig und
        anderswo falsch: Der Zeuge misst die Naehe-Logik des Managers, nicht
        die Frage, welcher Text eingebettet wurde.
        """
        pfad: str = f"{PFAD_PRAEFIX}{uuid.uuid4().hex}_{typ}.md"
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO autonomous_wissen
                        (dateipfad, user_id, character_id, beobachter, thema,
                         zusammenfassung, themen_embedding, typ, modus, status,
                         salienz_anfang, gewicht_roh, gewicht_absolut, gewicht_decay)
                    VALUES (%s, %s, %s, 'assistant', %s, %s, %s::vector, %s,
                            'recherche', 'echte_tiefe', 0.7, 1.0, %s, %s)
                    RETURNING id
                    """,
                    (
                        pfad, user_id, CHARAKTER, thema or f"Thema {self.marke}",
                        f"Zusammenfassung {self.marke}", _vektor_str(vektor), typ,
                        gewicht, gewicht,
                    ),
                )
                wissen_id: int = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO autonomous_wissen_thema (wissen_id, thema, embedding) "
                    "VALUES (%s, %s, %s::vector)",
                    (wissen_id, thema or f"Thema {self.marke}", _vektor_str(vektor)),
                )
            conn.commit()
        finally:
            conn.close()
        return pfad

    def _state(self, vektor: list[float] | None = NAH) -> dict:
        """Baut den State, den der Enricher dem Plugin reicht."""
        return {
            "such_vektor":  vektor,
            "user_id":      MENSCH,
            "character_id": CHARAKTER,
        }

    def test_a_treffer_wird_als_context_entry_geliefert(self) -> None:
        """Ein naher Treffer kommt mit Quelle, Inhalt, Gewicht und Herkunft."""
        pfad: str = self._zeile_anlegen(vektor=NAH)

        eintraege = self.manager.enrich_entries(self._state(), POSTGRES_URL)

        self.assertEqual(1, len(eintraege), f"erwartet ein Treffer, bekam {eintraege}")
        eintrag = eintraege[0]
        self.assertEqual("plugin_wissen", eintrag["quelle"])
        self.assertEqual("recherche", eintrag["subtyp"])
        self.assertIn(f"Thema {self.marke}", eintrag["inhalt"])
        self.assertIn(f"Zusammenfassung {self.marke}", eintrag["inhalt"])
        self.assertEqual(pfad, eintrag["meta"]["dateipfad"])
        self.assertAlmostEqual(1.0, eintrag["meta"]["cosine"], places=3)

    def test_b_gewicht_wird_auf_die_skala_des_pools_gebracht(self) -> None:
        """3.96 von 10.0 wird zu 0.396 — nicht zu 3.96.

        Ungerechnet schluege jeder Bibliothekseintrag im Reducer jeden
        KZG-Treffer, weil dort das hoechste Gewicht gewinnt. Das waere eine
        Rangfolge aus zwei Skalen statt aus zwei Bedeutungen.
        """
        self._zeile_anlegen(vektor=NAH, gewicht=3.96)

        eintraege = self.manager.enrich_entries(self._state(), POSTGRES_URL)

        self.assertEqual(1, len(eintraege))
        self.assertAlmostEqual(3.96 / LZG_KNOTEN_GEWICHT_CAP, eintraege[0]["gewicht"])
        self.assertLessEqual(eintraege[0]["gewicht"], 1.0)

    def test_c_ferner_treffer_faellt_unter_die_schwelle(self) -> None:
        """Ein orthogonaler Eintrag (Kosinus 0.0) wird nicht geliefert.

        Der positive Zwilling steht in Fall a — ohne ihn waere dieser Test
        auch dann gruen, wenn die Abfrage grundsaetzlich nichts liefert.
        """
        self._zeile_anlegen(vektor=FERN)

        eintraege = self.manager.enrich_entries(self._state(), POSTGRES_URL)

        self.assertEqual([], eintraege)
        self.assertGreater(WISSEN_RETRIEVAL_SCHWELLE, 0.0,
                           "eine Schwelle von 0.0 wuerde diesen Fall nicht trennen")

    def test_d_fremdes_paar_wird_nicht_geliefert(self) -> None:
        """Wissen aus einer anderen Beziehung bleibt draussen.

        Das ist der Defekt, gegen den das Paar-Schema gebaut ist: Novas
        Wissen ueber den einen darf nicht in ein Gespraech mit dem anderen
        fallen.
        """
        self._zeile_anlegen(vektor=NAH, user_id=FREMD)

        eintraege = self.manager.enrich_entries(self._state(), POSTGRES_URL)

        self.assertEqual([], eintraege)

    def test_e_berichte_gehoeren_nicht_in_den_gespraechskontext(self) -> None:
        """Nur `typ='wissen'` wird geliefert, nicht `typ='bericht'` (§7.5).

        Der Bericht ist Prozessdokumentation fuer die Lagebeurteilung. Im
        Prompt des Responders waere er Rauschen.
        """
        self._zeile_anlegen(vektor=NAH, typ="bericht")

        eintraege = self.manager.enrich_entries(self._state(), POSTGRES_URL)

        self.assertEqual([], eintraege)

    def test_f_ohne_suchschluessel_wird_nicht_gefragt(self) -> None:
        """Fehlt der Schluessel, gibt es keine Abfrage — und keinen Fehler.

        Der Fall tritt bei jedem Kaltstart ein: keine Gedaechtnisschicht hat
        gesucht, also gibt es nichts zu durchsuchen.
        """
        self._zeile_anlegen(vektor=NAH)

        for leer in (None, []):
            with self.subTest(such_vektor=leer):
                self.assertEqual([], self.manager.enrich_entries(
                    self._state(vektor=leer), POSTGRES_URL,
                ))

    def test_g_unvollstaendiges_paar_wird_abgewiesen(self) -> None:
        """Ohne beide Kennungen wird nicht gesucht, sondern laut gemeldet."""
        self._zeile_anlegen(vektor=NAH)

        for fehlend in ("user_id", "character_id"):
            with self.subTest(fehlt=fehlend):
                zustand: dict = self._state()
                zustand[fehlend] = ""
                with self.assertLogs("ki_server.plugins.wissen", level="ERROR"):
                    self.assertEqual([], self.manager.enrich_entries(zustand, POSTGRES_URL))

    def test_h_schreibauftraege_werden_laut_verworfen(self) -> None:
        """Die Bibliothek wird von Pixie geschrieben, nicht aus dem Gespraech."""
        with self.assertLogs("ki_server.plugins.wissen", level="ERROR"):
            self.assertEqual(0, self.manager.execute(
                [{"irgendein": "auftrag"}], MENSCH, MagicMock(), POSTGRES_URL,
            ))


class PluginReihenfolgeTest(unittest.TestCase):
    """Der Umbau am Enricher: Plugins laufen, nachdem der Schluessel existiert.

    Bis zum 04.08.2026 stand der Plugin-Block **vor** dem Prompt-Embedding.
    Ein Plugin mit Embedding-Suche haette sich dreissig Zeilen vor dessen
    Erzeugung ein zweites rechnen lassen muessen — rund 1,6 Sekunden je Turn
    fuer denselben Vektor.
    """

    def test_beim_plugin_aufruf_steht_der_suchschluessel_im_state(self) -> None:
        """Was ein Plugin vorfindet, wenn es an der Reihe ist.

        Geprueft wird der State **zum Zeitpunkt des Aufrufs**, nicht danach:
        Ein spaeter gesetzter Schluessel waere fuer das Plugin wertlos und
        im Nachhinein trotzdem sichtbar.
        """
        gesehen: dict = {}

        attrappe = MagicMock()
        attrappe.enrich_entries.side_effect = lambda zustand, _url: (
            gesehen.update({
                "such_vektor":      list(zustand.get("such_vektor") or []),
                "prompt_embedding": list(zustand.get("prompt_embedding") or []),
            }) or []
        )

        cursor = MagicMock()
        cursor.fetchone.return_value = (True,)
        verbindung = MagicMock()
        verbindung.cursor.return_value = cursor
        psycopg2_attrappe = MagicMock()
        psycopg2_attrappe.connect.return_value = verbindung

        redis_attrappe = MagicMock()
        redis_attrappe.get.return_value = None
        redis_attrappe.keys.return_value = ["kzg:test:1"]

        state: dict = {
            "turn_id":          "test-reihenfolge",
            "character_id":     "test_charakter",
            "user_prompt":      "Wie entsteht Hawking-Strahlung?",
            "user_intentionen": [],
            "ei_calc_rolle":    "character",
        }

        with ExitStack() as stack:
            p = stack.enter_context
            p(patch.object(enricher_mod, "psycopg2", psycopg2_attrappe))
            p(patch.object(enricher_mod, "get_registry", return_value={"attrappe": attrappe}))
            p(patch.object(enricher_mod, "_load_raw_turns", return_value=[]))
            p(patch.object(enricher_mod, "_create_prompt_embedding", return_value=NAH))
            p(patch.object(
                enricher_mod, "_compute_ziele_und_gravitation", return_value=([], 0.0),
            ))
            p(patch.object(enricher_mod, "_vorturn_cluster_lesen", return_value="foyer"))
            p(patch.object(enricher_mod, "spreading_lesen", return_value=[]))
            p(patch.object(enricher_mod, "kzg_entries_retrieve", return_value=[]))
            p(patch.object(enricher_mod, "emotionale_gravitation_scannen", return_value=[]))
            p(patch.object(enricher_mod, "span_start", return_value=uuid.uuid4()))
            p(patch.object(enricher_mod, "span_end"))
            p(patch.object(enricher_mod, "log_eingang"))
            p(patch.object(enricher_mod, "log_switch"))
            p(patch.object(enricher_mod, "log_ausgabe"))
            p(patch.object(enricher_mod, "log_berechnung"))

            enricher_mod._enrich_character(
                state, redis_attrappe, "postgresql://test", "test_mensch",
            )

        attrappe.enrich_entries.assert_called_once()
        self.assertEqual(NAH, gesehen["prompt_embedding"],
                         "das Prompt-Embedding fehlte, als das Plugin lief")
        self.assertEqual(NAH, gesehen["such_vektor"],
                         "der Suchschluessel fehlte, als das Plugin lief")


if __name__ == "__main__":
    unittest.main()
