"""Regieanweisungen: aus dem Antworttext den Text, den der Mund spricht.

Der Chat setzt Hervorhebung mit `*…*` oder `_…_` kursiv; was dort kursiv steht, sind
Regieanweisungen (»*Sie lacht kurz.*«) und wird nicht gesprochen. Fettdruck `**…**`
bleibt, nur ohne die Sternchen; `***…***` (fett und kursiv) fällt weg. Unterstriche im
Wort (`snake_case`) und ein einzelnes Sternchen ohne Gegenstück (`5 * 3`, ein
abgeschnittenes `*Sie lacht`) bleiben, wie sie sind.

Die Stelle einer Regieanweisung wird zu einem Leerzeichen, damit die Wörter davor und
danach nicht zusammenwachsen. Ein Text ohne Hervorhebung kommt zeichengleich heraus.
Die Wahl fiel auf reguläre Ausdrücke statt Python-Markdown: Das Modul bleibt frei von
Fremdbibliotheken, und die Regeln sind die der Hervorhebung, nicht die des ganzen Markdown.
"""

import re

# Innerhalb eines Absatzes darf die Hervorhebung über einen Zeilenumbruch gehen,
# nicht über eine Leerzeile.
BODY_PATTERN = r"(?:(?!\n[ \t]*\n).)+?"

BOLD_ITALIC = re.compile(
    rf"(?<!\*)\*\*\*(?=[^\s*]){BODY_PATTERN}(?<=[^\s*])\*\*\*(?!\*)", re.DOTALL
)
BOLD = re.compile(rf"(?<!\*)\*\*(?=[^\s*])({BODY_PATTERN})(?<=[^\s*])\*\*(?!\*)", re.DOTALL)
STAR_ITALIC = re.compile(
    rf"(?<!\*)\*(?=[^\s*]){BODY_PATTERN}(?<=[^\s*])\*(?!\*)", re.DOTALL
)
UNDERSCORE_ITALIC = re.compile(
    rf"(?<!\w)_(?=[^\s_]){BODY_PATTERN}(?<=[^\s_])_(?!\w)", re.DOTALL
)


def spoken_text(text: str) -> str:
    """Der Text, den der Mund spricht: der Antworttext ohne die kursiv gesetzten Stellen.

    Vorbedingung: `text` ist ein str.
    Nachbedingung: ein str, nie länger als `text`; ohne Hervorhebung zeichengleich mit
    `text`, sonst an den Rändern von Leerraum befreit. Ein Text ganz aus Regieanweisungen
    ergibt den leeren Text.
    Fehlerfälle: `TypeError`, wenn `text` kein str ist.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(text, str):
        raise TypeError(f"spoken_text: Text ist kein str: {type(text).__name__}")

    # ── Verarbeitung ──
    result = BOLD_ITALIC.sub(" ", text)
    result = BOLD.sub(r"\1", result)
    result = STAR_ITALIC.sub(" ", result)
    result = UNDERSCORE_ITALIC.sub(" ", result)
    if result != text:
        result = result.strip()

    # ── Ausgabe-Verifikation ──
    if len(result) > len(text):
        raise RuntimeError(f"spoken_text: Ergebnis länger: {len(result)} > {len(text)}")
    return result
