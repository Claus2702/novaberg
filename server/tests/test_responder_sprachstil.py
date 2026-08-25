"""Tests: Die Stil-Anweisung steht dort, wo sie gegen den Verlauf ankommt.

Ziel: Der Responder erhält die Angabe, wie er klingen soll, am Ende seiner
Nutzer-Nachricht — hinter dem Gesprächsverlauf und hinter dem aktuellen Prompt.

Hintergrund (Chat 114, gemessen): Alles über das WIE stand im System-Prompt,
unmittelbar vor der Generierung lag der Gesprächsverlauf. Ein Turn:

    Cluster=kissenschlacht · Strategie=Im · Vehikel=frage
    EI-Profil — Stil: locker | Modus: spielerisch
    Antwort: "Diese mathematische Eleganz, mit der du unsere Dynamik als
              Resonanzphänomen beschreibst … vor der thermischen Entropie
              zu schützen."

Jedes Registersignal sagte Kissenschlacht, die Sprache kam aus den rund
8.400 Tokens eigener Prosa im Verlauf — gegen 1.376 Zeichen Gesprächsvektor
im System-Prompt.

Zeugen: Die geforderte Reihenfolge (Verlauf → aktueller Prompt → Sprachstil)
stammt aus der Vorgabe, nicht aus dem Code. Die Cluster-Beschreibung wird
gegen die Tabelle in `ei/dreischicht.py` geprüft, die ihrerseits §5 des
Konzepts abbildet.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from ei.dreischicht import CLUSTER_BESCHREIBUNGEN, CLUSTER_FRAGEN
from ei.haltung import GROESSEN, Groessenwert, Haltung
from graph.nodes.responder import _sprachstil_block, _szenenblock
from graph.personality import Emotion, Personality

RESPONDER_LOGGER: str = "ki_server.responder"

# Von Hand gesetzt, nicht aus dem Pruefobjekt gelesen.
AEUSSERUNG: str = "Was macht der Sternhaufen im Perseus so alt?"
# Der Blockname des Regie-Teils, von Hand aus dem Prompt-Baustein uebernommen.
STILMARKE:  str = "[REGIE FUER DIESE REPLIK]"


def _zustand_mit_verlauf(turns: list | None = None) -> dict:
    """Ein Zustand, aus dem `respond` seine letzte Nutzer-Nachricht baut.

    Vorbedingung: keine.
    Nachbedingung: ein Nutzer-Turn (keine eigene Herkunft), mit oder ohne
        Gespraechsverlauf.
    Fehlerfaelle: keine.
    """
    basis: dict = _state()
    basis.update({
        "user_prompt":     AEUSSERUNG,
        "eigener_gedanke": "",
        "event_payload":   {},
        "session_turns":   turns if turns is not None else [
            {"rolle": "user", "inhalt": "Und davor?", "emotion": "", "arousal": 0.0},
            {"rolle": "assistant", "inhalt": "Eine fruehere Antwort."},
        ],
        "user_id": "u", "character_id": "c", "turn_id": "t",
        "memory_context": "", "web_context": "", "task_block": "",
        "antwort_inhalt": "Ein Inhalt.", "gespraechsvektor": "",
        "emotions_verlauf": [], "nova_emotions_verlauf": [],
        "user_intentionen": [], "agent_results": [],
    })
    return basis


def _letzte_nutzer_nachricht(zustand: dict) -> str:
    """Baut den Responder-Auftrag und liefert seine letzte Nutzer-Nachricht.

    Geprueft wird damit der Bauteil und nicht der Quelltext: Eine Reihenfolge
    im Code sagt nichts darueber, was beim Modell ankommt.

    Vorbedingung: `zustand` ist vollstaendig genug fuer `respond`.
    Nachbedingung: der Inhalt der letzten Nachricht in der Rolle des Nutzers.
    Fehlerfaelle: keine — fehlt sie, scheitert der Aufrufer sichtbar.
    """
    from types import SimpleNamespace
    from unittest.mock import patch

    from graph.nodes import responder as modul

    antwort = SimpleNamespace(text="Eine Antwort.", token_total=3, model="m")
    with patch.object(modul.model_service.chat, "submit_sync",
                      return_value=antwort) as ruf:
        modul.respond(zustand)

    nachrichten: list = ruf.call_args.args[0].messages
    nutzer: list = [m for m in nachrichten if m["role"] == "user"]
    return nutzer[-1]["content"]


def _state(cluster: str = "kissenschlacht", stil: str = "locker") -> dict:
    """Ein State, wie ihn der GV-Node und die Perzeption hinterlassen."""
    return {
        "gv_detail": {
            "cluster":   cluster,
            "strategie": "Im",
            "vehikel":   "frage",
            "impuls":    "Die Leichtigkeit halten, nicht erklaeren.",
        },
        "external": Personality(emotion=Emotion(language_style=stil)),
    }


class TestRegieImBlock(unittest.TestCase):
    """Der Block trägt die Haltung — der erste Leser, den sie je hatte.

    `HALTUNG-OHNE-LESER` war seit dem 31.07.2026 offen: Der Zug war gebaut,
    das Kriterium stand, die Zahlen waren gemessen, und keine Antwort änderte
    sich. Diese Klasse ist der Riegel dagegen — sie wird rot, sobald die
    Haltung den Prompt wieder nicht erreicht.
    """

    @staticmethod
    def _mit_haltung(umfang: float = 0.20, waerme: float = 0.90,
                     waerme_grund: float = 0.50) -> dict:
        """Ein State mit gerechneter Haltung; `waerme` weicht ab, der Rest ruht."""
        werte: dict[str, Groessenwert] = {}
        for name in GROESSEN:
            wert: float = umfang if name == "umfang" else (
                waerme if name == "waerme" else 0.50)
            grund: float = waerme_grund if name == "waerme" else wert
            werte[name] = Groessenwert(
                name=name, grundwert=grund, modifikation=wert - grund,
                ergebnis=wert, art="neigung", ausloeser="", ausserhalb=False,
            )
        zustand: dict = _state()
        zustand["haltung"] = Haltung(cluster="kissenschlacht", werte=werte)
        return zustand

    def test_die_zeichenspanne_steht_im_block(self) -> None:
        # **Die Zahl ist der Teil, der bindet** (gemessen 12.08.2026). Ohne
        # sie verfehlte dieselbe Vorgabe den Korridor um das Fünffache.
        block: str = _sprachstil_block(self._mit_haltung(umfang=0.20))

        self.assertIn("0 bis 60 Zeichen", block)
        self.assertIn("einsilbig, wortkarg", block)

    def test_die_spanne_folgt_dem_umfang(self) -> None:
        """Der positive Zwilling: ein anderer Umfang, ein anderer Korridor."""
        block: str = _sprachstil_block(self._mit_haltung(umfang=0.80))

        self.assertIn("350 bis 700 Zeichen", block)
        self.assertNotIn("0 bis 60 Zeichen", block)

    def test_eine_abweichende_groesse_steht_als_wort_im_block(self) -> None:
        block: str = _sprachstil_block(self._mit_haltung(waerme=0.90))

        self.assertIn("herzlich, innig", block)

    def test_ohne_abweichung_kein_haltungswort(self) -> None:
        """Was die Landschaft ohnehin vorgibt, wird nicht wiederholt."""
        block: str = _sprachstil_block(
            self._mit_haltung(waerme=0.50, waerme_grund=0.50))

        self.assertNotIn("herzlich, innig", block)
        self.assertIn("Zeichen", block)      # die Umfangzeile bleibt

    def test_ohne_haltung_meldet_der_knoten_laut(self) -> None:
        # Fail loud: Die alte Längenregel ist entfernt, es gibt keinen zweiten
        # Weg zu einer Umfangsvorgabe. Ein stilles Weglassen wäre von einer
        # Haltung ohne Abweichung nicht zu unterscheiden.
        with self.assertLogs(RESPONDER_LOGGER, level="ERROR") as protokoll:
            block: str = _sprachstil_block(_state())

        self.assertNotIn("Zeichen", block)
        self.assertTrue(
            any("Keine Haltung" in zeile for zeile in protokoll.output),
            f"Keine laute Meldung: {protokoll.output}",
        )

    def test_die_fragenfrequenz_der_landschaft_steht_nicht_mehr_da(self) -> None:
        # Sie kam für jede Nova gleich aus `CLUSTER_FRAGEN`; dieselbe Aussage
        # liefert jetzt die Haltungsgröße `fragen` charakterabhängig. Zwei
        # Quellen für eine Aussage sind die Doppelung, die der Umbau beseitigt.
        block: str = _sprachstil_block(self._mit_haltung())

        self.assertNotIn(CLUSTER_FRAGEN["kissenschlacht"], block)


class TestBlockInhalt(unittest.TestCase):
    """Der Block trägt die Landschaft, den Ton und den Leitgedanken."""

    def test_landschaft_steht_in_der_szene(self) -> None:
        """Seit dem 13.08.2026 traegt `[SZENE]` den Rahmen, nicht die Regie.

        Die Landschaft stand bis dahin am Ende der Nutzer-Nachricht. Mit der
        Drehbuch-Gliederung gehoert sie nach vorn — sie sagt, was **ist**,
        waehrend die Regie sagt, was Nova darin tut. Stuende sie an beiden
        Stellen, saehe das Modell dieselbe Landschaft zweimal.
        """
        szene: str = _szenenblock(_state())

        self.assertIn("Kissenschlacht", szene)
        self.assertIn(CLUSTER_BESCHREIBUNGEN["kissenschlacht"], szene)
        self.assertNotIn("Kissenschlacht", _sprachstil_block(_state()))

    def test_das_werkzeug_bleibt_in_der_regie(self) -> None:
        """Womit Nova arbeitet, ist Anweisung und gehoert ans Ende.

        Der Sprachstil des Nutzers steht dagegen seit dem 13.08.2026 als Lage
        bei Person B: Wie **er** spricht, ist keine Vorgabe an sie.
        """
        block: str = _sprachstil_block(_state())

        self.assertIn("Impuls", block)          # Strategie-Langname
        self.assertIn("als Frage", block)       # Vehikel
        self.assertNotIn("Ton: locker", block)

    def test_kein_leitgedanke_mehr(self) -> None:
        """Der Leitgedanke ist Inhalt und steht seit dem 31.07.2026 beim Verfasser.

        Dieser Block war die **zweite** Tuer: Der GV-Block war schon aus dem
        System-Prompt entfernt, und derselbe Text kam ueber den Sprachstil am
        Ende der Nutzer-Nachricht zurueck. Live beobachtet — der Responder gab
        den Leitgedanken daraufhin woertlich weiter.
        """
        block: str = _sprachstil_block(_state())

        self.assertNotIn("Leitgedanke", block)
        self.assertNotIn("Die Leichtigkeit halten", block)

    def test_fuehrt_hin_statt_zu_verbieten(self) -> None:
        """Die Formulierung fuehrt hin: Der Verlauf ist nicht falsch, nur alt."""
        block: str = _sprachstil_block(_state())

        self.assertIn("loese dich von seiner", block)
        self.assertIn("Verbindlich ist, was hier steht", block)

    def test_ohne_angaben_kein_block(self) -> None:
        """Positiver Zwilling: Ein leerer Block darf nicht erfunden werden."""
        leer: dict = {"gv_detail": {}, "external": Personality()}

        with self.assertLogs(RESPONDER_LOGGER, level="INFO"):
            self.assertEqual(_sprachstil_block(leer), "")

    def test_ohne_lage_bleibt_die_szene_bei_der_zeit(self) -> None:
        """Bei uebersprungenem GV-Node traegt die Szene wenigstens die Lage der Uhr."""
        ohne_gv: dict = {
            "gv_detail": {},
            "external": Personality(emotion=Emotion(language_style="locker")),
        }

        with self.assertLogs(RESPONDER_LOGGER, level="INFO"):
            szene: str = _szenenblock(ohne_gv)

        self.assertIn("[SZENE]", szene)
        self.assertIn("Uhr", szene)
        self.assertNotIn("Landschaft:", szene)


class TestLageVonGrobNachFein(unittest.TestCase):
    """Dieselbe Lage in drei Aufloesungen, von oben nach unten immer genauer.

    **Sie steht seit dem 13.08.2026 in `[SZENE]`** statt am Ende der
    Nutzer-Nachricht. Der Grund ist die Drehbuch-Gliederung: Die Lage ist der
    Rahmen und gehoert vor die Personen; ans Ende gehoert allein, was Nova
    auftraegt. Die Staffelung grob → fein gilt unveraendert und wird hier
    weiter geprueft — nur am neuen Ort.

    Entschieden am 08.08.2026: Die Landschaft geht in den Prompt, und zwar
    gestaffelt — die grobe Beschreibung oben, die genaue Situation unten, wo
    sie am dichtesten am Generierungspunkt steht.

    Landschaft (1 von 14), Sektor (1 von 64) und Achsen (die sechs Bits, aus
    denen beide gebaut sind) sind **nicht drei Angaben, sondern eine in drei
    Koernungen**. Deshalb prueft dieser Block nicht nur, dass sie da sind,
    sondern dass sie in dieser Reihenfolge stehen.
    """

    @staticmethod
    def _mit_lage() -> dict:
        zustand: dict = _state()
        zustand["gv_detail"].update({
            "sektor_name": "Kitzel",
            "achsen": {
                "energie": 1, "richtung_bin": 1, "naehe": 1,
                "valenz_bin": 1, "tiefe": 0, "initiative": 1,
                "initiative_roh": 0.21,
            },
        })
        return zustand

    def test_die_drei_stufen_stehen_von_grob_nach_fein(self) -> None:
        """Die Reihenfolge ist die Aussage, nicht nur die Anwesenheit."""
        block: str = _szenenblock(self._mit_lage())

        self.assertLess(block.index("Landschaft:"), block.index("Genauer:"))
        self.assertLess(block.index("Genauer:"),    block.index("Lage:"))

    def test_die_achsen_stehen_im_klartext(self) -> None:
        """Die feinste Stufe traegt Woerter, keine Bits."""
        block: str = _szenenblock(self._mit_lage())

        self.assertIn("viel Energie im Raum", block)
        self.assertIn("ihr steht euch nah", block)
        self.assertIn("flaches Gespraech", block)

    def test_eine_nicht_messbare_initiative_wird_nicht_behauptet(self) -> None:
        """Bit 1 ist bei fehlendem Mass ein Ausfall, keine Aussage.

        `achsen_berechnen` setzt es und meldet das laut. Wer es trotzdem als
        „du treibst" ausschreibt, macht aus dem Ausfall eine Behauptung —
        genau die Klasse, die `22_STILLE_FEHLER.md` §3 verbietet.
        """
        zustand: dict = self._mit_lage()
        zustand["gv_detail"]["achsen"]["initiative_roh"] = None

        block: str = _szenenblock(zustand)

        self.assertIn("Lage:", block)
        self.assertNotIn("du treibst", block)
        self.assertNotIn("der Mensch treibt", block)

    def test_der_sektor_wiederholt_die_landschaft_nicht(self) -> None:
        """10 der 64 Sektoren heissen wie ihre Landschaft.

        Dort waere die Zeile eine Wiederholung — sie kostet Kontext und
        traegt nichts.
        """
        zustand: dict = self._mit_lage()
        zustand["gv_detail"]["sektor_name"] = "Kissenschlacht"

        block: str = _szenenblock(zustand)

        self.assertIn("Landschaft: Kissenschlacht", block)
        self.assertNotIn("Genauer:", block)

    def test_ein_abweichender_sektor_steht_weiterhin_da(self) -> None:
        """Positiver Zwilling zur Unterdrueckung.

        Ohne ihn koennte die Zeile immer wegfallen und die Zusicherung
        darueber bliebe gruen.
        """
        block: str = _szenenblock(self._mit_lage())

        self.assertIn("Genauer: Kitzel", block)


class TestBlockPosition(unittest.TestCase):
    """Die Anweisung muss hinter dem Verlauf stehen, nicht davor.

    Das ist der eigentliche Eingriff: Im System-Prompt hat sie gegen den
    Verlauf verloren. Ein Test auf den Inhalt allein wuerde bestehen, auch
    wenn der Block wieder nach vorn wanderte.
    """

    def test_reihenfolge_verlauf_prompt_sprachstil(self) -> None:
        """Verlauf, dann Prompt, dann Stil — in der **gebauten Nachricht**.

        **Am 14.08.2026 umgestellt, nicht abgeschwaecht.** Vorher las dieser
        Zeuge die Reihenfolge im Quelltext von `respond`. Das misst zweimal
        das Falsche: Er wird rot, wenn jemand die Zeilen umstellt, ohne die
        Ausgabe zu aendern, und er bliebe gruen, wenn die Reihenfolge im
        Quelltext stimmte und in der Nachricht nicht. Geprueft wird jetzt der
        Bauteil und nicht der Prompt.
        """
        nachricht: str = _letzte_nutzer_nachricht(_zustand_mit_verlauf())

        pos_verlauf: int = nachricht.find("[GESPRAECHSVERLAUF]")
        pos_prompt:  int = nachricht.find("[AKTUELLER PROMPT]")
        pos_stil:    int = nachricht.find(STILMARKE)

        self.assertGreater(pos_verlauf, -1)
        self.assertGreater(pos_prompt, pos_verlauf)
        self.assertGreater(pos_stil, pos_prompt)

    def test_auch_ohne_verlauf_angehaengt(self) -> None:
        """Ohne Verlauf steht der Stil trotzdem hinter der Aeusserung."""
        nachricht: str = _letzte_nutzer_nachricht(_zustand_mit_verlauf(turns=[]))

        self.assertIn(STILMARKE, nachricht)
        self.assertGreater(nachricht.find(STILMARKE), nachricht.find(AEUSSERUNG))


if __name__ == "__main__":
    unittest.main()
