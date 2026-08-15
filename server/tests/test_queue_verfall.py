"""Tests fuer den Verfall der Shadow-Queue (`novaberg-queue-verfall_k.md`).

Der Lebenszyklus eines Auftrags hat drei Ausgaenge, und nur zwei davon sind ein
Loeschen:

    erledigt    -> die Zeile wird entfernt
    gescheitert -> nach drei Versuchen entfernt
    verfallen   -> aktiv = FALSE, die Zeile bleibt und ist weckbar

Diese Datei haelt die Zusicherungen fest, an denen das haengt.

Die Zeugen:

  * **Der Verfall loescht nicht.** Das ist die Entscheidung, die dieses
    Bauteil von seiner ersten Fassung unterscheidet — dort war hartes
    Loeschen vorgesehen. Ein Zeuge zaehlt die Zeilen vor und nach dem Lauf.
  * **Die Rangfolge ist Dringlichkeit.** Der juengste Auftrag gewinnt, weil der
    Verfall die Dringlichkeit ueber die Zeit senkt. Das kehrt die Ordnung der
    Redis-Fassung um, und der Zeuge haelt die neue Richtung fest.
  * **Ein leeres Thema ist kein Gegenstand.** Ohne diese Ausnahme
    verschmoelzen 141 unverwandte Auftraege zu einem einzigen (§6.2).
  * **Die Halbreaktivierung liegt ueber der Schwelle.** Sonst deaktivierte der
    Weckvorgang den Auftrag im selben Zug.
  * **Die Rueckrechnung ist exakt invers.** An ihr haengt die Uebernahme des
    Bestands: Wer den Rohwert falsch rueckrechnet, verschiebt jede spaetere
    Verstaerkung.

Die DB-Tests bringen ihr Fixture selbst mit (eigenes Paar-Tripel), lesen
ausschliesslich darin und raeumen es in tearDown ab: Die Suite laeuft gegen die
Produktiv-Datenbank.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
import uuid

import psycopg2
from config import POSTGRES_URL, QUEUE_SCHWELLE
from memory.repositories.shadow_auftrag_repository import (
    ShadowAuftrag,
    ShadowAuftragRepository,
    halbreaktivierungs_wert,
    salienz_absolut_berechnen,
    salienz_roh_zurueckrechnen,
)

MENSCH:    str = "test_verfall_mensch"
CHARAKTER: str = "test_verfall_nova"


def _auftrag(thema: str, salienz: float = 0.9764, aufgabe: str = "recherche") -> ShadowAuftrag:
    """Ein gueltiger Auftrag des Fixture-Paares."""
    return ShadowAuftrag(
        user_id=MENSCH, character_id=CHARAKTER, beobachter="user",
        aufgabe=aufgabe, thema=thema, salienz=salienz,
        intentionen=["recherche_vertiefen"], emotion="neugierig",
        modus="fachgespraech",
    )


class DieKurveIstUmkehrbarTest(unittest.TestCase):
    """Aufbau und Rueckrechnung sind exakt zueinander invers."""

    def test_rueckrechnung_trifft_den_ausgangswert(self) -> None:
        """Jeder Rohwert kehrt durch Daempfung und Rueckrechnung zu sich selbst zurueck."""
        for roh in (0.03, 0.1, 0.3, 0.5, 0.8048, 1.0):
            with self.subTest(roh=roh):
                self.assertAlmostEqual(
                    roh, salienz_roh_zurueckrechnen(salienz_absolut_berechnen(roh)),
                    places=9,
                )

    def test_die_kzg_marken_reproduzieren_sich(self) -> None:
        """Die Kurve ist dieselbe wie im KZG — belegt an dessen drei Marken.

        `config.py` fuehrt KZG_SALIENZ_MINIMUM/MID/HIGH mit dem Kommentar
        "roh 0.3 / 0.5 / 0.7". Trifft die Rueckrechnung diese Rohwerte, ist
        belegt, dass Queue und KZG dieselbe Kurve benutzen.
        """
        for absolut, erwartet_roh in ((0.67378, 0.3), (0.84089, 0.5), (0.94393, 0.7)):
            with self.subTest(absolut=absolut):
                self.assertAlmostEqual(
                    erwartet_roh, salienz_roh_zurueckrechnen(absolut), places=4,
                )

    def test_saettigung_bremst_am_oberen_ende(self) -> None:
        """Wer oben ist, gewinnt durch eine weitere Verstaerkung fast nichts.

        Das ist der Zweck der Kurve (§12.2) und keine Schwaeche: Ein
        Dauerthema soll den Verfall nicht aushebeln.
        """
        roh: float = salienz_roh_zurueckrechnen(0.9764)
        zugewinn: float = salienz_absolut_berechnen(roh + 10 * 0.03) - 0.9764
        self.assertLess(
            zugewinn, 0.05,
            "Zehn Verstaerkungen duerfen den Anker nur um Bruchteile heben — "
            "sonst waere die Saettigung wirkungslos.",
        )


class DieHalbreaktivierungTest(unittest.TestCase):
    """Ein geweckter Auftrag liegt ueber der Schwelle und unter seinem Anker."""

    def test_liegt_zwischen_schwelle_und_anker(self) -> None:
        """Der Weckwert ist echt groesser als die Schwelle und echt kleiner als der Anker."""
        for anker in (0.5, 0.67378, 0.84089, 0.9764, 1.0):
            with self.subTest(anker=anker):
                wert: float = halbreaktivierungs_wert(anker)
                self.assertGreater(
                    wert, QUEUE_SCHWELLE,
                    "Ein geweckter Auftrag darf nicht sofort wieder unter die "
                    "Schwelle fallen.",
                )
                self.assertLess(wert, anker, "Wecken ist kein Verstaerken.")

    def test_ist_die_haelfte_des_bandes_ueber_der_schwelle(self) -> None:
        """Der Weckwert liegt exakt in der Mitte zwischen Schwelle und Anker."""
        for anker in (0.5, 0.9764, 1.0):
            with self.subTest(anker=anker):
                anteil: float = (
                    (halbreaktivierungs_wert(anker) - QUEUE_SCHWELLE)
                    / (anker - QUEUE_SCHWELLE)
                )
                self.assertAlmostEqual(0.5, anteil, places=9)


class RepositoryTest(unittest.TestCase):
    """Die Zusicherungen am laufenden Schema."""

    def setUp(self) -> None:
        """Erzeugt eine testeigene Themenmarke."""
        self.marke: str = f"test_verfall_{uuid.uuid4().hex}"

    def tearDown(self) -> None:
        """Loescht alle Zeilen des Fixture-Paares."""
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM shadow_auftrag WHERE user_id = %s", (MENSCH,))
            conn.commit()
        finally:
            conn.close()

    def _zeile(self, auftrag_id: int) -> dict:
        """Liest eine Zeile roh aus der Tabelle."""
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM shadow_auftrag WHERE id = %s", (auftrag_id,),
                )
                return dict(cur.fetchone())
        finally:
            conn.close()

    def _alter_setzen(self, auftrag_id: int, tage: float) -> None:
        """Verschiebt `verstaerkt_am` in die Vergangenheit.

        Ein echter Auftrag wird erst nach Wochen faellig; die Wirkung ist am
        Bestand nicht zu beobachten, ohne die Uhr zu stellen. Das bleibt ein
        Zeuge und ersetzt die Messung ueber 30 Tage Betrieb nicht (§13).
        """
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE shadow_auftrag SET verstaerkt_am = NOW() - %s::interval "
                    "WHERE id = %s",
                    (f"{tage} days", auftrag_id),
                )
            conn.commit()
        finally:
            conn.close()

    def test_a_einreihen_legt_an(self) -> None:
        """Ein neuer Gegenstand erzeugt eine Zeile mit gesetzten Salienz-Staenden."""
        auftrag_id, vorgang = ShadowAuftragRepository.einreihen(
            POSTGRES_URL, _auftrag(self.marke),
        )
        self.assertEqual("angelegt", vorgang)

        zeile = self._zeile(auftrag_id)
        self.assertAlmostEqual(0.9764, zeile["salienz_absolut"], places=6)
        self.assertAlmostEqual(0.9764, zeile["salienz_decay"], places=6)
        self.assertAlmostEqual(
            salienz_roh_zurueckrechnen(0.9764), zeile["salienz_roh"], places=6,
            msg="salienz_roh muss zurueckgerechnet werden, damit eine spaetere "
                "Verstaerkung auf der Kurve weiterlaeuft.",
        )
        self.assertTrue(zeile["aktiv"])
        self.assertEqual(1, zeile["haeufigkeit"])
        self.assertEqual(["recherche_vertiefen"], zeile["intentionen"])

    def test_b_derselbe_gegenstand_verstaerkt_statt_zu_doppeln(self) -> None:
        """Ein zweiter Auftrag zum selben Gegenstand erzeugt keine zweite Zeile."""
        erste_id, _ = ShadowAuftragRepository.einreihen(POSTGRES_URL, _auftrag(self.marke))
        zweite_id, vorgang = ShadowAuftragRepository.einreihen(
            POSTGRES_URL, _auftrag(self.marke),
        )

        self.assertEqual(erste_id, zweite_id, "Es darf nur eine Zeile geben.")
        self.assertEqual("verstaerkt", vorgang)
        self.assertEqual(2, self._zeile(erste_id)["haeufigkeit"])

    def test_c_leeres_thema_ist_kein_gegenstand(self) -> None:
        """Zwei Auftraege ohne Thema sind zwei Auftraege, nicht einer.

        Ohne diese Ausnahme verschmoelzen die 141 themenlosen `vertiefen`-
        Auftraege des Bestands zu einer einzigen Zeile mit haeufigkeit 141
        (§6.2) — aus einem fehlenden Wert wuerde der wichtigste Eintrag.
        """
        erste_id, _ = ShadowAuftragRepository.einreihen(POSTGRES_URL, _auftrag(""))
        zweite_id, vorgang = ShadowAuftragRepository.einreihen(POSTGRES_URL, _auftrag(""))

        self.assertNotEqual(erste_id, zweite_id)
        self.assertEqual("angelegt", vorgang)

    def test_d_auswahl_nimmt_den_dringlichsten(self) -> None:
        """Der hoechste `salienz_decay` gewinnt — und das ist der juengste Auftrag.

        Die Gegenprobe auf die Richtung: Die Redis-Fassung nahm unter
        Gleichstaenden den aeltesten. Wer den Index versehentlich aufsteigend
        anlegt oder ORDER BY umdreht, faellt hier auf.
        """
        alt_id, _ = ShadowAuftragRepository.einreihen(
            POSTGRES_URL, _auftrag(f"{self.marke}_alt"),
        )
        self._alter_setzen(alt_id, 20)
        ShadowAuftragRepository.verfall_lauf(POSTGRES_URL)

        neu_id, _ = ShadowAuftragRepository.einreihen(
            POSTGRES_URL, _auftrag(f"{self.marke}_neu"),
        )

        gewinner = ShadowAuftragRepository.bester_kandidat(
            POSTGRES_URL, MENSCH, CHARAKTER,
        )
        self.assertIsNotNone(gewinner)
        self.assertEqual(
            neu_id, gewinner["id"],
            "Der juengere Auftrag ist der dringlichere (§12.3).",
        )

    def test_e_verfall_deaktiviert_und_loescht_nicht(self) -> None:
        """Unter der Schwelle wird deaktiviert — die Zeile bleibt.

        Das ist die tragende Entscheidung dieses Bauteils: Die erste Fassung
        des Konzepts sah hartes Loeschen vor.
        """
        auftrag_id, _ = ShadowAuftragRepository.einreihen(POSTGRES_URL, _auftrag(self.marke))
        self._alter_setzen(auftrag_id, 40)

        ergebnis = ShadowAuftragRepository.verfall_lauf(POSTGRES_URL)

        self.assertIsNone(ergebnis["error"])
        self.assertIn(auftrag_id, ergebnis["deaktivierte_ids"])

        zeile = self._zeile(auftrag_id)
        self.assertFalse(zeile["aktiv"], "Der Auftrag muss ruhen.")
        self.assertLess(zeile["salienz_decay"], QUEUE_SCHWELLE)
        self.assertAlmostEqual(
            0.9764, zeile["salienz_absolut"], places=6,
            msg="Der Anker bleibt unangetastet — er ist die Bezugsgroesse der "
                "Halbreaktivierung.",
        )

    def test_f_ein_ruhender_auftrag_verlaesst_die_auswahl(self) -> None:
        """Was ruht, wird nicht mehr gewaehlt."""
        auftrag_id, _ = ShadowAuftragRepository.einreihen(POSTGRES_URL, _auftrag(self.marke))
        self._alter_setzen(auftrag_id, 40)
        ShadowAuftragRepository.verfall_lauf(POSTGRES_URL)

        self.assertIsNone(
            ShadowAuftragRepository.bester_kandidat(POSTGRES_URL, MENSCH, CHARAKTER),
        )

    def test_g_ein_neuer_anlass_weckt_den_ruhenden(self) -> None:
        """Derselbe Gegenstand holt einen ruhenden Auftrag zurueck — auf halbes Band."""
        auftrag_id, _ = ShadowAuftragRepository.einreihen(POSTGRES_URL, _auftrag(self.marke))
        self._alter_setzen(auftrag_id, 40)
        ShadowAuftragRepository.verfall_lauf(POSTGRES_URL)

        gleiche_id, vorgang = ShadowAuftragRepository.einreihen(
            POSTGRES_URL, _auftrag(self.marke),
        )

        self.assertEqual(auftrag_id, gleiche_id)
        self.assertEqual("reaktiviert", vorgang)

        zeile = self._zeile(auftrag_id)
        self.assertTrue(zeile["aktiv"])
        self.assertAlmostEqual(
            halbreaktivierungs_wert(0.9764), zeile["salienz_decay"], places=6,
        )

    def test_h_erledigt_entfernt_die_zeile(self) -> None:
        """Der einzige Loeschpfad, der keiner Begruendung bedarf."""
        auftrag_id, _ = ShadowAuftragRepository.einreihen(POSTGRES_URL, _auftrag(self.marke))

        self.assertTrue(ShadowAuftragRepository.entfernen(POSTGRES_URL, auftrag_id))
        self.assertEqual(
            {"aktiv": 0, "ruhend": 0},
            ShadowAuftragRepository.bestand(POSTGRES_URL, MENSCH, CHARAKTER),
        )

    def test_i_drei_fehlversuche_verwerfen(self) -> None:
        """Der zweite harte Loeschpfad — ein Ausfuehrungsfehler, kein Verfall."""
        auftrag_id, _ = ShadowAuftragRepository.einreihen(POSTGRES_URL, _auftrag(self.marke))

        self.assertEqual(
            "gezaehlt", ShadowAuftragRepository.versuch_zaehlen(POSTGRES_URL, auftrag_id, 3),
        )
        self.assertEqual(
            "gezaehlt", ShadowAuftragRepository.versuch_zaehlen(POSTGRES_URL, auftrag_id, 3),
        )
        self.assertEqual(
            "verworfen", ShadowAuftragRepository.versuch_zaehlen(POSTGRES_URL, auftrag_id, 3),
        )
        self.assertEqual(
            {"aktiv": 0, "ruhend": 0},
            ShadowAuftragRepository.bestand(POSTGRES_URL, MENSCH, CHARAKTER),
        )

    def test_j_ein_junger_auftrag_ueberlebt_den_lauf(self) -> None:
        """Die Gegenprobe zu test_e: Was frisch ist, bleibt aktiv.

        Ohne sie belegte test_e nur, dass der Lauf **irgendetwas**
        deaktiviert — auch ein Lauf, der alles abraeumt, waere gruen.
        """
        auftrag_id, _ = ShadowAuftragRepository.einreihen(POSTGRES_URL, _auftrag(self.marke))
        self._alter_setzen(auftrag_id, 29)

        ergebnis = ShadowAuftragRepository.verfall_lauf(POSTGRES_URL)

        self.assertNotIn(auftrag_id, ergebnis["deaktivierte_ids"])
        self.assertTrue(self._zeile(auftrag_id)["aktiv"])


if __name__ == "__main__":
    unittest.main()
