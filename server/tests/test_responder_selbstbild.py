"""Tests für Novas Selbstbild in den Aufgaben-Blöcken.

Ziel: Was ihre eigenen Dienste getan haben, erscheint ihr als **ihr**
Handeln — nicht als das einer dritten Stelle.

**Der Anlass ist gemessen, an ihren eigenen Antworten.** In einer Sitzung
am 20.08.2026 sagte sie dreimal *„die Fachabteilung"*: *„Ich habe die
Rückmeldung der Fachabteilung geprüft"*, *„Die Fachabteilung hat die
Operation abgeschlossen"*, *„Die Fachabteilung hat den Auftrag als
unpassend eingestuft."* Die Ursache stand wörtlich in ihrem Prompt — dritte
Person, unbestimmter Artikel, eigenes Fürwort —, und sie gab exakt weiter,
was dastand.

**„Fachabteilung" ist eine Architektur-Metapher aus der Bauperspektive.**
`novaberg-agent-fachabteilung_k.md` benutzt sie, um zu sagen, dass ein Agent
mitdenkt statt CRUD-Maske zu sein. Das ist eine Aussage über die Bauart,
gerichtet an Entwickler — im Prompt der Figur bezeichnet sie, was sie
sprachlich bezeichnet: jemand anderen.

Die Zusicherungen, und die zweite ist die aus `F-PROMPT-1`:

  1. **Die Blöcke sprechen sie als Handelnde an.**
  2. **Sie tun es ohne Verbot.** Ein Satz wie „nicht die einer anderen
     Stelle" nennt das Unerwünschte und macht es zum Gegenstand; vier
     Anläufe dieser Bauart sind im Bestand gescheitert.
  3. **Auch der Datenteil trägt keine Instanz.** Der Rahmen nützt nichts,
     wenn darunter „Agent 'notizen'" steht.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from dataclasses import dataclass

from config import PROMPTS
from graph.format.agent_results import format_success_lines

#: Wörter, die im Prompt der Figur eine dritte Stelle neben sie setzen.
DRITTE_STELLE: tuple[str, ...] = ("Fachabteilung", "Agent '", 'Agent "')

#: Verbotsformen — sie nennen das Unerwünschte (`F-PROMPT-1`).
VERBOTSFORM: tuple[str, ...] = (
    "nicht die einer anderen", "nicht das einer anderen", "keine andere Stelle",
)


@dataclass
class _Ergebnis:
    """Ein AgentResult, so weit die Formatierung es liest."""

    agent_name: str
    ergebnis: str


class SelbstbildTest(unittest.TestCase):
    """Die beiden Aufgaben-Blöcke, die von ihrem Handeln sprechen."""

    BLOECKE: tuple[str, ...] = (
        "responder.aufgabe_erfolg", "responder.aufgabe_ablehnung",
    )

    def test_kein_block_setzt_eine_dritte_stelle_neben_sie(self) -> None:
        """Die tragende Zusicherung."""
        for name in self.BLOECKE:
            text: str = PROMPTS[name]
            for wort in DRITTE_STELLE:
                self.assertNotIn(
                    wort, text,
                    f"{name} nennt {wort!r} — das ist jemand anderes neben ihr",
                )

    def test_beide_bloecke_sprechen_sie_als_handelnde_an(self) -> None:
        """Führung statt Leerstelle: Es reicht nicht, das Wort zu streichen."""
        erfolg: str = PROMPTS["responder.aufgabe_erfolg"]
        ablehnung: str = PROMPTS["responder.aufgabe_ablehnung"]
        self.assertIn("du hast es getan", erfolg.lower())
        self.assertIn("du warst es", erfolg.lower())
        self.assertIn("du hast geurteilt", ablehnung.lower())
        self.assertIn("das urteil ist deins", ablehnung.lower())

    def test_die_fuehrung_kommt_ohne_verbot_aus(self) -> None:
        """`F-PROMPT-1`: Ein Verbot macht das Unerwünschte zum Gegenstand.

        Die zweite Hälfte des Zeugen — ohne sie bestünde er auch dann, wenn
        die Führung **neben** dem Verbot stünde, und genau so entsteht der
        nächste Anlauf.
        """
        for name in self.BLOECKE:
            text: str = PROMPTS[name].lower()
            for form in VERBOTSFORM:
                self.assertNotIn(form.lower(), text, f"{name} verbietet, statt zu führen")

    def test_der_datenteil_traegt_keine_instanz(self) -> None:
        """Der Rahmen nützt nichts, wenn darunter eine Instanz steht."""
        zeilen: str = format_success_lines([
            _Ergebnis("termine", "Termin fuer Freitag 14 Uhr eingetragen."),
            _Ergebnis("notizen", "Notiz gespeichert."),
        ])
        self.assertNotIn("Agent", zeilen)
        self.assertIn("- termine:", zeilen)
        self.assertIn("- notizen:", zeilen)

    def test_gegenprobe_der_bereich_bleibt_unterscheidbar(self) -> None:
        """Belegt, dass die Änderung nichts wegnimmt, was gebraucht wird.

        Der Name unterscheidet die Zeilen, wenn mehrere Dienste gelaufen
        sind — genommen wird die Instanz, nicht die Information.
        """
        zeilen: str = format_success_lines([
            _Ergebnis("termine", "A"), _Ergebnis("notizen", "B"),
        ])
        self.assertEqual(len(zeilen.splitlines()), 2)
        self.assertNotEqual(zeilen.splitlines()[0], zeilen.splitlines()[1])


if __name__ == "__main__":
    unittest.main()
