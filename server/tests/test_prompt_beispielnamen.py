"""Waechter: kein Name aus einem echten Gespraech in Prompts oder Tests.

Ziel: Kein Prompt-Baustein und kein Test im Repo traegt einen Namen aus einem
echten Gespraech.

Das Repo ist oeffentlich. Namen von Angehoerigen, Haustieren und Wohnorten sind
die intimsten Daten im System — sie gehoeren ins Protokoll ausserhalb des Repos,
nicht in einen Few-Shot-Block. Beispiele brauchen Namen, also traegt das Repo
einen erfundenen Cast.

WARUM DIE PRUEFUNG UMGEDREHT IST: Eine Liste der zu schuetzenden echten Namen
im Test waere genau die Preisgabe, die sie verhindern soll. Der Test kennt
deshalb nur die ERLAUBTEN Namen und schlaegt bei jedem anderen an.

GRENZE DER PRUEFUNG, ausdruecklich: Erkannt wird ein Name nur in den unten
gelisteten Einfuehrungs-Konstruktionen. Das ist keine allgemeine PII-Suche.
Die Konvention dazu lautet: Beispiele fuehren Personen-, Tier- und Ortsnamen
NUR ueber diese Konstruktionen ein. Wer eine neue braucht, traegt sie hier
nach — sonst prueft der Waechter an der neuen Stelle nicht mit.
"""

import re
import unittest
from pathlib import Path

# Der erfundene Cast. Alles andere in einem Namens-Slot ist ein Fund.
ERLAUBTE_BEISPIELNAMEN: frozenset[str] = frozenset({
    "Merten",   # der Nutzer in Beispielsaetzen
    "Ilva",     # die Schwester
    "Rufus",    # der Hund
    "Ostheim",  # der Wohnort
})

# Generische Woerter, die der "aus X"-Slot mitnimmt und die keine Namen sind.
# Waechst diese Liste, ist das ein Anlass hinzusehen, kein Automatismus.
KEINE_NAMEN: frozenset[str] = frozenset({
    "Kontext", "Session", "Notiz", "Prompt", "Vor", "Sicht", "Redis",
    "Worker",   # "aus Worker-Thread" in den Model-Service-Tests
    "Konzept",  # "aus Konzept §7.5" in test_synapsen_kanten
    "Cohen",    # "aus Cohen (1960)" — die Quelle der Kappa-Formel, kein Gespraechsname
    "Chat",     # "aus Chat 116" — Sitzungsverweis, wie ihn jedes Dokument traegt
    "Postgre",  # "aus PostgreSQL" — der Slot bricht nach dem ersten
                # Kleinbuchstaben-Block ab. Zwilling zu "Redis" darueber.
    "Pfad",     # "aus Pfad 1" — die beiden Graph-Pfade heissen so. Der
                # Ausdruck steht in Doku, Kommentaren und Tests und waechst
                # mit jeder Stelle, die ueber die Graphgrenze schreibt.
    "Gespraechen",  # "aus Gespraechen abgeleitete Recherchen" — die Formel,
    "Gesprächen",   # mit der die Veroeffentlichungsgrenze des Wissensspeichers
                    # begruendet wird (F-WISSEN-1). Sie steht in beiden
                    # Schreibweisen im Bestand und wiederholt sich in jedem
                    # Dokument und jeder Datei zur Bibliothek.
})

# Einfuehrungs-Konstruktionen. Erweitern, wenn ein Beispiel eine neue braucht.
NAMENS_SLOTS: tuple[str, ...] = (
    r"\bheisst\s+([A-ZÄÖÜ][a-zäöüß]{2,})",
    r"\bnamens\s+([A-ZÄÖÜ][a-zäöüß]{2,})",
    r"\bSchwester\s+([A-ZÄÖÜ][a-zäöüß]{2,})",
    r"\bBruder\s+([A-ZÄÖÜ][a-zäöüß]{2,})",
    r"\baus\s+([A-ZÄÖÜ][a-zäöüß]{2,})",
    r"\bFakt ueber\s+([A-ZÄÖÜ][a-zäöüß]{2,})",
)

# Listen-Literale, in denen Eigennamen als Beispielwerte stehen.
LISTEN_SLOT: str = r'"entitaeten_roh":\s*\[([^\]]*)\]'

BASIS: Path = Path(__file__).resolve().parent.parent


def _namen_aus(text: str) -> set[str]:
    """Sammelt alle Namen, die der Text ueber eine bekannte Konstruktion einfuehrt.

    Vorbedingung: text ist der vollstaendige Dateiinhalt.
    Nachbedingung: Menge der Kandidaten, generische Slot-Treffer bereits entfernt.
    Fehlerfaelle: keine — ein Text ohne Namen liefert die leere Menge.
    """
    # ── Verarbeitung ────────────────────────────
    gefunden: set[str] = set()
    for muster in NAMENS_SLOTS:
        gefunden |= set(re.findall(muster, text))

    for liste in re.findall(LISTEN_SLOT, text):
        gefunden |= set(re.findall(r'"([^"]+)"', liste))

    # ── Ausgabe ─────────────────────────────────
    return gefunden - KEINE_NAMEN


def _dateien() -> list[Path]:
    """Alle Prompt-Bausteine und Testdateien des Servers."""
    return sorted(BASIS.glob("prompts/**/*.txt")) + sorted(BASIS.glob("tests/**/*.py"))


class PromptBeispielnamenTest(unittest.TestCase):
    """Negativ: kein fremder Name. Positiv: der Cast ist wirklich da."""

    def test_kein_name_ausserhalb_des_erfundenen_casts(self):
        funde: dict[str, set[str]] = {}
        for pfad in _dateien():
            fremd: set[str] = _namen_aus(pfad.read_text(encoding="utf-8")) - ERLAUBTE_BEISPIELNAMEN
            if fremd:
                funde[str(pfad.relative_to(BASIS))] = fremd

        self.assertEqual(
            funde, {},
            "Namen ausserhalb des erfundenen Casts gefunden. Stammt einer davon aus "
            "einem echten Gespraech, gehoert er nicht ins Repo — ersetzen. Ist es ein "
            "generisches Wort, das der Slot mitgenommen hat, nach KEINE_NAMEN eintragen.",
        )

    def test_dateien_werden_ueberhaupt_gefunden(self):
        """Ohne Dateien pruefte der Waechter nichts und waere trotzdem gruen."""
        dateien = _dateien()
        self.assertGreater(len(dateien), 40)
        self.assertIn(
            "prompts/default/kzg_verdichtung.task.txt",
            [str(p.relative_to(BASIS)) for p in dateien],
        )

    def test_der_cast_steht_wirklich_in_den_beispielen(self):
        """Positiver Zwilling: sonst waere Loeschen aller Beispiele gruen."""
        erwartet: dict[str, set[str]] = {
            "prompts/default/kzg_verdichtung.task.txt":           {"Merten", "Ilva", "Rufus"},
            "prompts/default/kzg_verdichtung.assistant_task.txt": {"Ilva", "Ostheim"},
            # Chat 112: Der Dimensionen-Block ist aus salienz.task herausgeloest
            # worden, damit die drei Lage-Bloecke ihn teilen. Die Beispielnamen
            # sind mit ihm umgezogen — der Zwilling zieht mit, statt hier auf
            # eine leere Menge zu fallen, die immer gruen waere.
            "prompts/default/salienz.dimensionen.txt":            {"Ilva", "Ostheim"},
            "prompts/default/salienz_segment.task.txt":           {"Ilva"},
        }
        for rel, namen in erwartet.items():
            with self.subTest(datei=rel):
                gefunden: set[str] = _namen_aus((BASIS / rel).read_text(encoding="utf-8"))
                self.assertEqual(gefunden, namen)


if __name__ == "__main__":
    unittest.main()
