"""Markdown zu Matrix-HTML — die Formatierung am Konsumenten.

**Der Server liefert Markdown, jeder Kanal wandelt fuer sein Medium** (Prinzip
aus `docs/novaberg-tool-multi-channel.md` §4). Matrix kennt dafuer ein
eigenes Feld: `formatted_body` mit `format: org.matrix.custom.html`. Fehlt es,
zeigt der Client den rohen Text — aus `**wichtig**` werden vier Sternchen.

**Die Spezifikation erlaubt nur eine begrenzte Menge an Auszeichnungen**, und
ein Client darf alles Uebrige entfernen. Der Wandler hier erzeugt deshalb
absichtlich wenig: die Formen, die Nova wirklich benutzt, und keine, die ein
Client ohnehin verwirft.

**`body` bleibt der Markdown-Text.** Das ist keine Verlegenheit, sondern die
Vorschrift: `body` ist die Rueckfallform fuer Clients ohne HTML, und sie soll
lesbar sein. Markdown ist genau dafuer gebaut.
"""

import html
import re

#: Was die Matrix-Spezifikation als Format erwartet.
MATRIX_FORMAT: str = "org.matrix.custom.html"

# Reihenfolge ist wesentlich: Der Code-Block zuerst, sonst wandelt der
# Fettdruck Sternchen INNERHALB von Code um.
_CODEBLOCK = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)
_CODE      = re.compile(r"`([^`\n]+)`")
_FETT      = re.compile(r"\*\*([^*\n]+)\*\*")
_KURSIV    = re.compile(r"(?<![\*\w])\*([^*\n]+)\*(?!\*)")
_UEBERSCHRIFT = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
_LISTE     = re.compile(r"^[-*]\s+(.+)$", re.MULTILINE)
_ZITAT     = re.compile(r"^>\s?(.*)$", re.MULTILINE)


def nach_matrix_html(markdown: str) -> str:
    """Wandelt Novas Markdown in die Teilmenge, die Matrix-Clients zeigen.

    Vorbedingung: `markdown` ist der kanonische Antworttext des Servers.
    Nachbedingung: HTML mit ausschliesslich zugelassenen Elementen; jedes
    Zeichen, das nicht Teil einer erkannten Auszeichnung ist, ist maskiert.
    Fehlerfaelle: keine — was nicht erkannt wird, bleibt maskierter Text.

    **Maskiert wird zuerst, ausgezeichnet danach.** Andersherum wuerde ein
    `<` im Antworttext als Element gelesen; bei einem Modell, das ueber Code
    und Mathematik spricht, ist das kein Randfall.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not markdown:
        return ""

    # ── Verarbeitung ────────────────────────────
    text: str = html.escape(markdown, quote=False)

    text = _CODEBLOCK.sub(
        lambda m: (f'<pre><code class="language-{m.group(1)}">{m.group(2)}</code></pre>'
                   if m.group(1) else f"<pre><code>{m.group(2)}</code></pre>"),
        text,
    )
    text = _CODE.sub(r"<code>\1</code>", text)
    text = _UEBERSCHRIFT.sub(
        lambda m: f"<h{len(m.group(1))}>{m.group(2)}</h{len(m.group(1))}>", text)
    text = _FETT.sub(r"<strong>\1</strong>", text)
    text = _KURSIV.sub(r"<em>\1</em>", text)
    text = _ZITAT.sub(r"<blockquote>\1</blockquote>", text)
    text = _LISTE.sub(r"<li>\1</li>", text)

    # Aufeinanderfolgende Punkte werden zu einer Liste zusammengefasst —
    # `<li>` ohne `<ul>` ist ungueltig, und ein Client darf es verwerfen.
    text = re.sub(r"(?:<li>.*?</li>\n?)+",
                  lambda m: f"<ul>{m.group(0).strip()}</ul>", text, flags=re.DOTALL)

    # Absaetze bleiben Absaetze; einfache Umbrueche werden zu <br/>.
    absaetze: list[str] = [a.strip() for a in text.split("\n\n") if a.strip()]
    text = "\n".join(
        a if a.startswith(("<h", "<ul", "<pre", "<blockquote")) else f"<p>{a}</p>"
        for a in absaetze
    )
    return text.replace("\n<p>", "\n<p>").replace("\n", "\n")


def inhalt_bauen(markdown: str) -> dict:
    """Baut den `content` einer Textnachricht — mit und ohne Auszeichnung.

    Nachbedingung: `body` traegt den Markdown-Text unveraendert, und
    `formatted_body` kommt **nur dann** hinzu, wenn die Wandlung ueberhaupt
    etwas ausgezeichnet hat. Ein `formatted_body`, das nur den maskierten
    Text wiederholt, kostet Uebertragung und traegt nichts.
    """
    inhalt: dict = {"msgtype": "m.text", "body": markdown}

    formatiert: str = nach_matrix_html(markdown)
    nackt: str = f"<p>{html.escape(markdown, quote=False)}</p>"
    if formatiert and formatiert != nackt:
        inhalt["format"] = MATRIX_FORMAT
        inhalt["formatted_body"] = formatiert
    return inhalt
