"""Zeugen ueber die abstrakte Schicht: entsteht ein Profil, und was liest es?

Ziel: Ein LZG-Knoten, der die Wiederkehr- und Laengenschwelle ueberschritten
hat, traegt eine Bewertung auf den sechs Qualitaetsdimensionen — und der
Merkmalszug macht daraus eine Zahl, ohne dass eine einzelne starke Dimension
im Mittelwert untergeht.

**Diese Zeugen fassen den Produktivbestand nicht an.** Der Erzeuger ruft ein
Sprachmodell und schreibt in `traeger_qualitaet`; beides wird ersetzt. Die
Schreibfunktion sehen sie nur auf ihren Validierungspfaden, und die kehren vor
dem Verbindungsaufbau zurueck. `[gemessen]` 01.09.2026 an der Praegungsschicht:
Eine Suite, die ihren globalen Lauf gegen die echte Verbindung fuhr, faltete
bei jedem Durchgang den Bestand des Messpaars mit.

Drei Ebenen, und die dritte ist die, die an dieser Schicht schon zweimal
gefehlt hat:

  1. **Die Rechnung** — traegt die staerkste Dimension allein?
  2. **Die Annahme der Modellantwort** — wird ein Wert ausserhalb des Rasters
     verworfen oder still gerundet?
  3. **Die Verdrahtung** — ruft der Tageslauf den Erzeuger ueberhaupt? Genau
     diese Frage stellte bei der Faltung kein Zeuge, und die Funktion stand
     einen Tag lang ohne Aufrufer.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from config import MERKMALSZUG_BONUS, POSTGRES_URL, QUALITAET_KANON
from ei.fascination import dominante_dimension, merkmalszug
from memory import quality_profile
from memory.repositories import quality_profile_repository as speicher

REPO: str = "memory.repositories.quality_profile_repository"

AGENT_MODUL: str = "agents.synapsen_decay.agent"
PROFIL_MODUL: str = "memory.quality_profile"

# Ein vollstaendiges Profil, in dem eine Dimension traegt und der Rest schweigt
# — der Zauberer aus §4.3: Sichtbare Fingerfertigkeit ist langweilig, die
# Ungewissheit traegt die Faszination allein.
DER_ZAUBERER: dict[str, float] = {
    "komplexitaet": 0.0,
    "ungewissheit": 1.0,
    "konflikt": 0.0,
    "weite": 0.0,
    "schemasprengung": 0.0,
    "bedrohungsrelevanz": 0.0,
}


class DerMerkmalszugIstEinWeichesOderTest(unittest.TestCase):
    """§10.1 — die staerkste Dimension traegt allein und vollstaendig."""

    def test_eine_dimension_allein_traegt_voll(self) -> None:
        """Der Zeuge gegen den Mittelwert.

        Ein Mittelwert gaebe hier 1/6 = 0,1667, und der Zauberer bekaeme
        keine Faszination — obwohl gerade seine Ungewissheit sie traegt. Die
        Zahl steht ausgeschrieben im Konzept und ist der Grund fuer die Form.
        """
        zug: float = merkmalszug(DER_ZAUBERER)
        self.assertAlmostEqual(1.0, zug, places=6)
        self.assertGreater(
            zug, 0.17,
            "Der Merkmalszug liegt auf Mittelwert-Hoehe — die staerkste "
            "Dimension traegt nicht allein",
        )

    def test_der_zuschlag_steht_auf_dem_wert_des_konzepts(self) -> None:
        """Die Konstante selbst, ausgeschrieben statt importiert.

        **Die Zahlen unten stehen als Literale und nicht als Ausdruck ueber
        `MERKMALSZUG_BONUS`.** `[gemessen]` 03.09.2026: In der ersten Fassung
        bezogen zwei Zeugen ihre Erwartung aus der Konstante, die sie pruefen
        sollten — eine Gegenprobe, die den Bonus auf 0.0 setzte, liess
        **alle 37** gruen. Der Zeuge nahm die Aenderung einfach mit.
        """
        self.assertEqual(
            0.35, MERKMALSZUG_BONUS,
            "Der Zuschlag weicht vom Konzept (§10.1) ab — wurde er bewusst "
            "geaendert, gehoeren die drei Literale unten mitgezogen",
        )

    def test_kombination_ist_ein_zuschlag_keine_bedingung(self) -> None:
        """Fuenf halbe Dimensionen heben den Zug, sie tragen ihn nicht.

        1,0 + 0,35 x 0,5 = 1,175 — ausgerechnet, nicht abgeleitet.
        """
        profil: dict[str, float] = dict.fromkeys(QUALITAET_KANON, 0.5)
        profil["ungewissheit"] = 1.0
        self.assertAlmostEqual(1.175, merkmalszug(profil), places=6)

    def test_die_obergrenze_wird_genau_erreicht(self) -> None:
        """Alle sechs auf 1,0 ergeben exakt 1,35 — konstruiert, nicht gekappt.

        Der Zeuge wird rot, wenn jemand den Zuschlag aendert, ohne die
        Spanne in der Ausgabe-Verifikation mitzuziehen — und
        er wird es nur, weil die Zahl hier steht und nicht gerechnet wird.
        """
        profil: dict[str, float] = dict.fromkeys(QUALITAET_KANON, 1.0)
        self.assertAlmostEqual(1.35, merkmalszug(profil), places=6)

    def test_ein_profil_aus_lauter_nullen_gibt_null(self) -> None:
        """Eine Groesse, die Faszination misst, muss auch Null sagen koennen.

        Vier der 50 von Hand bewerteten Knoten lagen auf allen sechs
        Dimensionen unter 0,5 (§6.2) — und das waren die richtigen vier.
        """
        self.assertEqual(0.0, merkmalszug(dict.fromkeys(QUALITAET_KANON, 0.0)))

    def test_ein_leeres_profil_gibt_null(self) -> None:
        """Ungeprueft und null sind derselbe Zug, aber nicht dieselbe Aussage."""
        self.assertEqual(0.0, merkmalszug({}))

    def test_eine_fremde_dimension_verwirft_das_profil(self) -> None:
        """Ein unbekannter Name ist ein Defekt, kein neuer Fall.

        Die Teilmengen-Falle: Wer nur gegen die sechs bekannten prueft und
        Unbekanntes ueberspringt, kann einen erfundenen Dimensionsnamen nicht
        von einem gueltigen »trifft nicht zu« unterscheiden.
        """
        profil: dict[str, float] = dict(DER_ZAUBERER)
        profil["neuheit"] = 1.0
        self.assertEqual(
            0.0, merkmalszug(profil),
            "Eine Dimension ausserhalb des Kanons wurde stillschweigend "
            "mitgerechnet",
        )

    def test_eine_auspraegung_ausserhalb_der_spanne_wird_verworfen(self) -> None:
        """Verworfen, nicht geklemmt.

        Eine stille Klemme machte einen Rechenfehler von einer Randbedingung
        ununterscheidbar.
        """
        profil: dict[str, float] = dict(DER_ZAUBERER)
        profil["weite"] = 1.4
        self.assertEqual(0.0, merkmalszug(profil))

    def test_eine_nicht_zahl_verwirft_das_profil(self) -> None:
        """Ein `True` ist in Python eine Zahl und hier keine."""
        profil: dict = dict(DER_ZAUBERER)
        profil["konflikt"] = True
        self.assertEqual(0.0, merkmalszug(profil))


class DieDominanteDimensionIstWiederholbarTest(unittest.TestCase):
    """Sie ist die Groesse, an der sich der gesetzte Satz pruefen laesst."""

    def test_die_staerkste_dimension_wird_benannt(self) -> None:
        """§6.2 haelt die Verteilung von Hand fest — hier ist ihr Zugriff."""
        self.assertEqual(("ungewissheit", 1.0), dominante_dimension(DER_ZAUBERER))

    def test_bei_gleichstand_entscheidet_die_kanon_reihenfolge(self) -> None:
        """Bei drei erlaubten Stufen ist der Gleichstand der Regelfall.

        Ohne feste Ordnung gaeben zwei Laeufe ueber dasselbe Profil
        verschiedene Antworten, und die Verteilung aus §6.2 waere nicht
        vergleichbar.
        """
        profil: dict[str, float] = dict.fromkeys(QUALITAET_KANON, 0.0)
        profil["konflikt"] = 1.0
        profil["weite"] = 1.0
        name, staerke = dominante_dimension(profil)
        self.assertEqual("konflikt", name, "Der Kanon gibt `konflikt` vor `weite`")
        self.assertEqual(1.0, staerke)

    def test_ein_leeres_profil_hat_keine_dominante(self) -> None:
        """Kein Name ist eine Antwort; ein erfundener waere keine."""
        self.assertEqual(("", 0.0), dominante_dimension({}))


class DieModellantwortWirdGeprueftTest(unittest.TestCase):
    """Die unzuverlaessigste Quelle im System — eine Modellantwort."""

    def test_ein_sauberes_json_wird_gelesen(self) -> None:
        """Der Normalfall — sonst prueft der Rest der Klasse gegen nichts."""
        antwort: str = (
            '{"komplexitaet": 0.5, "ungewissheit": 1.0, "konflikt": 0.0, '
            '"weite": 0.5, "schemasprengung": 1.0, "bedrohungsrelevanz": 0.0}'
        )
        gelesen = quality_profile._antwort_lesen(antwort)
        self.assertIsNotNone(gelesen)
        self.assertEqual(set(QUALITAET_KANON), set(gelesen))
        self.assertEqual(1.0, gelesen["schemasprengung"])

    def test_ein_codezaun_wird_abgeraeumt(self) -> None:
        """Modelle zaeunen JSON ein, auch wenn man es nicht verlangt."""
        antwort: str = (
            '```json\n{"komplexitaet": 0.0, "ungewissheit": 0.0, '
            '"konflikt": 0.0, "weite": 0.0, "schemasprengung": 0.0, '
            '"bedrohungsrelevanz": 0.0}\n```'
        )
        self.assertIsNotNone(quality_profile._antwort_lesen(antwort))

    def test_eine_leere_antwort_ist_kein_profil_aus_nullen(self) -> None:
        """Der teuerste Verwechslungsfall dieser Schicht.

        Am 01.08.2026 liefen zwei Antworten mit 4936 und 3753 Token und
        **null Zeichen** als Erfolg durch, vier Stufen weit. Ein Profil aus
        lauter Nullen ist eine Aussage; eine leere Antwort ist keine.
        """
        self.assertIsNone(quality_profile._antwort_lesen(""))
        self.assertIsNone(quality_profile._antwort_lesen("   "))

    def test_ein_fehlender_schluessel_verwirft_das_ganze_profil(self) -> None:
        """Alle sechs oder keine.

        Ein Teilprofil ist im Bestand von einem Abbruch nicht zu
        unterscheiden.
        """
        antwort: str = (
            '{"komplexitaet": 0.5, "ungewissheit": 1.0, "konflikt": 0.0, '
            '"weite": 0.5, "schemasprengung": 1.0}'
        )
        self.assertIsNone(quality_profile._antwort_lesen(antwort))

    def test_ein_erfundener_schluessel_verwirft_das_ganze_profil(self) -> None:
        """Gegen den Kanon geprueft, nicht gegen eine Teilmenge."""
        antwort: str = (
            '{"komplexitaet": 0.5, "ungewissheit": 1.0, "konflikt": 0.0, '
            '"weite": 0.5, "schemasprengung": 1.0, "bedrohungsrelevanz": 0.0, '
            '"neuheit": 1.0}'
        )
        self.assertIsNone(quality_profile._antwort_lesen(antwort))

    def test_ein_wert_ausserhalb_des_rasters_wird_nicht_gerundet(self) -> None:
        """0.7 ist keine 0.5.

        Eine stille Rundung machte eine erfundene Skala von der vorgegebenen
        ununterscheidbar — und genau daran haengt die Aussage, dass das
        Modell drei Stufen benutzt und nicht heimlich eine eigene.
        """
        antwort: str = (
            '{"komplexitaet": 0.7, "ungewissheit": 1.0, "konflikt": 0.0, '
            '"weite": 0.5, "schemasprengung": 1.0, "bedrohungsrelevanz": 0.0}'
        )
        self.assertIsNone(quality_profile._antwort_lesen(antwort))

    def test_ein_leerzeichen_im_schluessel_kostet_nicht_das_profil(self) -> None:
        """`[gemessen]` 03.09.2026: 4 von 20 Traegern fielen genau hieran aus.

        Immer derselbe Schluessel, immer dieselbe Stelle — `un gewissheit`.
        Ohne die Normalisierung ist der Traeger dauerhaft verloren: Der
        naechste Lauf sieht ihn ohne Kanten, ruft dasselbe Modell, bekommt
        dasselbe Leerzeichen.
        """
        antwort: str = (
            '{"komplexitaet": 0.5, "un gewissheit": 1.0, "konflikt": 0.0, '
            '"weite": 0.5, "schemasprengung": 1.0, "bedrohungsrelevanz": 0.0}'
        )
        gelesen = quality_profile._antwort_lesen(antwort)
        self.assertIsNotNone(gelesen, "Der Leerraum kostet weiterhin das Profil")
        self.assertEqual(1.0, gelesen["ungewissheit"])

    def test_die_normalisierung_macht_die_kanon_pruefung_nicht_stumpf(self) -> None:
        """Ein erfundener Name faellt weiterhin durch.

        Die Gegenprobe zur Normalisierung: Sie darf Leerraum abraeumen und
        sonst nichts. Ohne diesen Zeugen waere `neu heit` → `neuheit` genau
        der stille Durchlass, gegen den die Kanon-Pruefung steht.
        """
        antwort: str = (
            '{"komplexitaet": 0.5, "ungewissheit": 1.0, "konflikt": 0.0, '
            '"weite": 0.5, "schemasprengung": 1.0, "neu heit": 0.0}'
        )
        self.assertIsNone(quality_profile._antwort_lesen(antwort))

    def test_eine_kollision_beim_zusammenziehen_verwirft(self) -> None:
        """Zwei Schluessel, die zu demselben werden, sind keine Berichtigung."""
        antwort: str = (
            '{"komplexitaet": 0.5, "ungewissheit": 1.0, "un gewissheit": 0.0, '
            '"konflikt": 0.0, "weite": 0.5, "schemasprengung": 1.0, '
            '"bedrohungsrelevanz": 0.0}'
        )
        self.assertIsNone(quality_profile._antwort_lesen(antwort))

    def test_kein_json_wird_verworfen(self) -> None:
        """Freitext statt Objekt — der haeufigste Ausfall."""
        self.assertIsNone(
            quality_profile._antwort_lesen("Der Text ist sehr komplex.")
        )

    def test_eine_liste_ist_kein_profil(self) -> None:
        """Gueltiges JSON und trotzdem die falsche Sorte."""
        self.assertIsNone(quality_profile._antwort_lesen("[0.5, 1.0, 0.0]"))


class DerSpeicherLehntEineWertAussageAbTest(unittest.TestCase):
    """Die Kante ist vorzeichenlos — und das prueft nicht nur das Schema.

    Diese Zeugen erreichen den Verbindungsaufbau nicht: Alle drei kehren auf
    ihrem Validierungspfad zurueck. Der Produktivbestand bleibt unberuehrt.
    """

    def test_eine_negative_auspraegung_wird_verworfen(self) -> None:
        """0,8 — nicht »gut 0,8«. Der Unterschied ist der ganze Punkt (§4.4)."""
        self.assertIsNone(
            speicher.quality_upsert(POSTGRES_URL, 1, 1, -0.5, "zeuge")
        )

    def test_eine_auspraegung_ueber_eins_wird_verworfen(self) -> None:
        """Verworfen, nicht gekappt."""
        self.assertIsNone(
            speicher.quality_upsert(POSTGRES_URL, 1, 1, 1.5, "zeuge")
        )

    def test_ohne_quelle_wird_verworfen(self) -> None:
        """Ohne Herkunft ist eine Auspraegung nicht nachrechenbar."""
        self.assertIsNone(
            speicher.quality_upsert(POSTGRES_URL, 1, 1, 0.5, "")
        )

    def test_ein_wahrheitswert_ist_keine_auspraegung(self) -> None:
        """`True` ist in Python ein `int` und kaeme sonst als 1.0 durch.

        Der Fall ist nicht konstruiert: Ein Modell, das statt einer Zahl ein
        `true` liefert, schriebe damit vollen Ausschlag — und zwar auf dem
        Erfolgspfad, ohne eine einzige Zeile im Log.
        """
        self.assertIsNone(
            speicher.quality_upsert(POSTGRES_URL, 1, 1, True, "zeuge")
        )

    def test_ein_deckel_von_null_wird_verworfen(self) -> None:
        """Ein Deckel <= 0 ergaebe einen Lauf ohne Kandidaten.

        Der saehe aus wie einer, der nichts zu tun fand.
        """
        self.assertEqual([], speicher.candidates_load(POSTGRES_URL, 0))


class DerErzeugerSchreibtAlleSechsOderKeineTest(unittest.TestCase):
    """Ein Teilprofil waere im Bestand von einem Abbruch nicht zu trennen."""

    KANON_IDS: dict[str, int] = {
        name: i + 1 for i, name in enumerate(QUALITAET_KANON)
    }
    GUTE_ANTWORT: str = (
        '{"komplexitaet": 0.5, "ungewissheit": 1.0, "konflikt": 0.0, '
        '"weite": 0.5, "schemasprengung": 1.0, "bedrohungsrelevanz": 0.0}'
    )

    def _modell(self, text: str) -> MagicMock:
        antwort = MagicMock()
        antwort.text = text
        dienst = MagicMock()
        dienst.background.submit_sync.return_value = antwort
        return dienst

    def test_ein_gueltiges_profil_wird_vollstaendig_geschrieben(self) -> None:
        """Sechs Aufrufe des Speichers, einer je Dimension."""
        with patch(f"{PROFIL_MODUL}.model_service", self._modell(self.GUTE_ANTWORT)), \
             patch(f"{PROFIL_MODUL}.speicher.quality_upsert",
                   return_value=42) as geschrieben:
            profil = quality_profile.traeger_profilieren(
                POSTGRES_URL, 4711, "ein hinreichend langer Text", self.KANON_IDS,
            )
        self.assertIsNotNone(profil)
        self.assertEqual(6, geschrieben.call_count)

    def test_ein_teilweise_gescheitertes_schreiben_meldet_und_gibt_none(self) -> None:
        """Der Zeuge gegen die stille Luecke.

        Ein Traeger mit fuenf Kanten wird von der Kandidatensuche **nicht**
        wieder aufgegriffen — er traegt ja Kanten. Ohne diese Meldung bliebe
        er fuer immer unvollstaendig, und `profiles_load` faende ihn erst,
        wenn ihn jemand liest.
        """
        with patch(f"{PROFIL_MODUL}.model_service", self._modell(self.GUTE_ANTWORT)), \
             patch(f"{PROFIL_MODUL}.speicher.quality_upsert",
                   side_effect=[1, 2, 3, 4, 5, None]):
            profil = quality_profile.traeger_profilieren(
                POSTGRES_URL, 4711, "ein hinreichend langer Text", self.KANON_IDS,
            )
        self.assertIsNone(profil)

    def test_eine_unbrauchbare_antwort_schreibt_nichts(self) -> None:
        """Nichts halb geschriebenes — die Pruefung steht vor dem Speicher."""
        with patch(f"{PROFIL_MODUL}.model_service", self._modell("kein JSON")), \
             patch(f"{PROFIL_MODUL}.speicher.quality_upsert") as geschrieben:
            profil = quality_profile.traeger_profilieren(
                POSTGRES_URL, 4711, "ein hinreichend langer Text", self.KANON_IDS,
            )
        self.assertIsNone(profil)
        geschrieben.assert_not_called()

    def test_ein_leerer_inhalt_ruft_kein_modell(self) -> None:
        """Ein leerer Text traegt keine Qualitaeten — und kostet keinen Aufruf."""
        dienst = self._modell(self.GUTE_ANTWORT)
        with patch(f"{PROFIL_MODUL}.model_service", dienst):
            profil = quality_profile.traeger_profilieren(
                POSTGRES_URL, 4711, "   ", self.KANON_IDS,
            )
        self.assertIsNone(profil)
        dienst.background.submit_sync.assert_not_called()

    def test_ein_unvollstaendiger_kanon_ruft_kein_modell(self) -> None:
        """Die Vorbedingung steht oben, nicht mitten in der Verarbeitung."""
        dienst = self._modell(self.GUTE_ANTWORT)
        with patch(f"{PROFIL_MODUL}.model_service", dienst):
            profil = quality_profile.traeger_profilieren(
                POSTGRES_URL, 4711, "ein hinreichend langer Text",
                {"komplexitaet": 1},
            )
        self.assertIsNone(profil)
        dienst.background.submit_sync.assert_not_called()


class DerLaufFuehrtBuchTest(unittest.TestCase):
    """`versucht` = `profiliert` + `gescheitert`, sonst ist der Lauf blind."""

    def test_die_buchfuehrung_geht_auf(self) -> None:
        """Zwei von drei gelingen — die dritte Zahl muss stimmen."""
        kandidaten: list[dict] = [
            {"id": i, "inhalt": "x" * 500, "haeufigkeit": 3, "themen": []}
            for i in (1, 2, 3)
        ]
        with patch(f"{PROFIL_MODUL}.speicher.qualities_load",
                   return_value={n: i for i, n in enumerate(QUALITAET_KANON)}), \
             patch(f"{PROFIL_MODUL}.speicher.candidates_load",
                   return_value=kandidaten), \
             patch(f"{PROFIL_MODUL}.speicher.profile_count", return_value=(7, 42)), \
             patch(f"{PROFIL_MODUL}.traeger_profilieren",
                   side_effect=[{"a": 1.0}, None, {"b": 1.0}]):
            ergebnis = quality_profile.profil_lauf(POSTGRES_URL)
        self.assertEqual(3, ergebnis["versucht"])
        self.assertEqual(2, ergebnis["profiliert"])
        self.assertEqual(1, ergebnis["gescheitert"])
        self.assertIsNone(ergebnis["error"])
        self.assertEqual(7, ergebnis["traeger_gesamt"])

    def test_ein_leerer_kandidatensatz_ist_kein_fehler(self) -> None:
        """Sobald der Bestand aufgeholt hat, ist das der Normalfall."""
        with patch(f"{PROFIL_MODUL}.speicher.qualities_load",
                   return_value={n: i for i, n in enumerate(QUALITAET_KANON)}), \
             patch(f"{PROFIL_MODUL}.speicher.candidates_load", return_value=[]), \
             patch(f"{PROFIL_MODUL}.speicher.profile_count", return_value=(368, 2208)):
            ergebnis = quality_profile.profil_lauf(POSTGRES_URL)
        self.assertEqual(0, ergebnis["versucht"])
        self.assertIsNone(ergebnis["error"])

    def test_ein_unlesbarer_kanon_beendet_den_lauf_laut(self) -> None:
        """Ohne den Satz waere jede Dimension-ID geraten."""
        with patch(f"{PROFIL_MODUL}.speicher.qualities_load", return_value={}), \
             patch(f"{PROFIL_MODUL}.speicher.candidates_load") as gesucht:
            ergebnis = quality_profile.profil_lauf(POSTGRES_URL)
        self.assertIsNotNone(ergebnis["error"])
        gesucht.assert_not_called()


class DerTageslaufRuftDenErzeugerTest(unittest.TestCase):
    """Die Verdrahtung — ohne sie bleibt der Erzeuger gebaut und ungerufen.

    An dieser Schicht ist genau das binnen zwei Tagen dreimal der Befund
    gewesen: eine Rechenfunktion ohne Aufrufer. Der Zeuge ersetzt jeden
    Schritt des Tageslaufs, auch die, um die es hier nicht geht — was nicht
    ersetzt ist, laeuft gegen `POSTGRES_URL`.
    """

    def test_invoke_ruft_den_profillauf(self) -> None:
        """Der achte Schritt, und er darf keinen Modellaufruf ausloesen."""
        from agents.base import AgentState
        from agents.synapsen_decay.agent import SynapsenDecayAgent

        leer: dict = {"error": None, "total_processed": 0, "deactivated_count": 0,
                      "deleted_count": 0, "verarbeitet": 0, "deaktiviert": 0,
                      "gefaltet": 0, "gesamt": 0}
        with patch(f"{AGENT_MODUL}.SYNAPSEN_DECAY_AKTIV", True), \
             patch(f"{AGENT_MODUL}.lzg_knoten.run_node_decay", return_value=leer), \
             patch(f"{AGENT_MODUL}.pipeline_log.delete_expired_entries", return_value=leer), \
             patch(f"{AGENT_MODUL}.ShadowAuftragRepository.verfall_lauf", return_value=leer), \
             patch(f"{AGENT_MODUL}.db_manager"), \
             patch(f"{AGENT_MODUL}.praegung.alle_faeden_nachfuehren", return_value=leer), \
             patch(f"{AGENT_MODUL}.praegung.faeden_ohne_strang_zuordnen",
                   return_value=(0, 0)), \
             patch(f"{AGENT_MODUL}.praegung.alle_einfaerbungen",
                   return_value={"gerechnet": 0, "gesamt": 0, "je_sektor": {},
                                 "abstand_max": 0.0, "error": None}), \
             patch.object(SynapsenDecayAgent, "_richtungen_protokollieren",
                          return_value=0), \
             patch(f"{AGENT_MODUL}.quality_profile.profil_lauf",
                   return_value={"versucht": 2, "profiliert": 2,
                                 "gescheitert": 0, "traeger_gesamt": 2,
                                 "kanten_gesamt": 12, "error": None}) as gerufen:
            zustand: AgentState = SynapsenDecayAgent().invoke(
                AgentState(auftrag="", kontext={}),
            )
        gerufen.assert_called_once()
        self.assertEqual("abgeschlossen", zustand["status"])
        self.assertIn("qualitaet_profil", zustand["ergebnis"])
        self.assertEqual(2, zustand["ergebnis"]["qualitaet_profil"]["profiliert"])

    def test_ein_fehler_im_profillauf_faerbt_den_tageslauf(self) -> None:
        """Ein Schritt, dessen Fehlschlag niemand sieht, ist kein Schritt."""
        from agents.base import AgentState
        from agents.synapsen_decay.agent import SynapsenDecayAgent

        leer: dict = {"error": None, "total_processed": 0, "deactivated_count": 0,
                      "deleted_count": 0, "verarbeitet": 0, "deaktiviert": 0,
                      "gefaltet": 0, "gesamt": 0}
        with patch(f"{AGENT_MODUL}.SYNAPSEN_DECAY_AKTIV", True), \
             patch(f"{AGENT_MODUL}.lzg_knoten.run_node_decay", return_value=leer), \
             patch(f"{AGENT_MODUL}.pipeline_log.delete_expired_entries", return_value=leer), \
             patch(f"{AGENT_MODUL}.ShadowAuftragRepository.verfall_lauf", return_value=leer), \
             patch(f"{AGENT_MODUL}.db_manager"), \
             patch(f"{AGENT_MODUL}.praegung.alle_faeden_nachfuehren", return_value=leer), \
             patch(f"{AGENT_MODUL}.praegung.faeden_ohne_strang_zuordnen",
                   return_value=(0, 0)), \
             patch(f"{AGENT_MODUL}.praegung.alle_einfaerbungen",
                   return_value={"gerechnet": 0, "gesamt": 0, "je_sektor": {},
                                 "abstand_max": 0.0, "error": None}), \
             patch.object(SynapsenDecayAgent, "_richtungen_protokollieren",
                          return_value=0), \
             patch(f"{AGENT_MODUL}.quality_profile.profil_lauf",
                   return_value={"versucht": 0, "profiliert": 0,
                                 "gescheitert": 0, "traeger_gesamt": 0,
                                 "kanten_gesamt": 0,
                                 "error": "Der Kanon ist nicht lesbar"}):
            zustand: AgentState = SynapsenDecayAgent().invoke(
                AgentState(auftrag="", kontext={}),
            )
        self.assertEqual("fehler", zustand["status"])
        self.assertIn("Kanon", zustand["fehler"])


if __name__ == "__main__":
    unittest.main()


class DieAuswahlFolgtDerEchtenWiederkehrTest(unittest.TestCase):
    """Berichtigt am 05.09.2026 — `haeufigkeit` misst Wiederholung.

    Die alte Sortierung waehlte die durch die KZG-Schleife aufgeblaehten
    Knoten: `[gemessen]` tragen die profilierten `haeufigkeit` **56,1** gegen
    **5,5** im Schnitt aller aktiven, und von 36 je Turn gelesenen Knoten
    trugen **zwei** ein Profil.
    """

    def test_die_abfrage_sortiert_nach_beruehrten_turns(self) -> None:
        """Die Zahl verschiedener Turns aus der Bruecke, nicht `haeufigkeit`."""
        with patch(f"{REPO}.psycopg2.connect") as verbindung:
            zeiger = verbindung.return_value.cursor.return_value
            zeiger.fetchall.return_value = []
            speicher.candidates_load(POSTGRES_URL, 20)
            sql = zeiger.execute.call_args[0][0]

        self.assertIn("count(DISTINCT turn_id)", sql)
        self.assertIn("FROM verbindung", sql)
        self.assertIn("ORDER BY COALESCE(b.turns, 0) DESC", sql)

    def test_haeufigkeit_bleibt_zweiter_schluessel(self) -> None:
        """Ein Knoten ohne Bruecke faellt sonst ans Ende — ohne Grund.

        Ueber ihn ist nichts Schlechtes bekannt, sondern nichts.
        """
        with patch(f"{REPO}.psycopg2.connect") as verbindung:
            zeiger = verbindung.return_value.cursor.return_value
            zeiger.fetchall.return_value = []
            speicher.candidates_load(POSTGRES_URL, 20)
            sql = zeiger.execute.call_args[0][0]

        self.assertIn("k.haeufigkeit DESC", sql)
        self.assertIn("LEFT JOIN", sql)
