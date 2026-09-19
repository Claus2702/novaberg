# Novaberg — Tool: Datei-Operationen (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-tool-dateien_k.md`](novaberg-tool-dateien_k.md) · Ausarbeitung: [`novaberg-tool-dateien_t.md`](novaberg-tool-dateien_t.md) · Messungen: [`novaberg-tool-dateien_m.md`](novaberg-tool-dateien_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Keine. Das Konzept führt keine Entscheidung.

**Im Text als entschieden geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_t` §5, Kasten *„Architektur-Entscheidung“*: Datei-Operationen sind allgemeine Tools (`tools/dateien/`), keine Pixie-Infrastruktur.
- [`novaberg-tool-dateien_m.md`](novaberg-tool-dateien_m.md), *Bisheriger Kopf*: *„Zwei Abweichungen gegenüber diesem Konzept, beide begründet“* — die Wurzel als Pflichtargument ohne Vorgabewert und `str_ersetzen` statt `str_replace_in_block`. Das sind Entscheidungen beim Bauen.

---

## B. Offen beim Meister

**Drei** — die ersten drei Punkte aus §3.4.7 (Abschnitt D unten). Der Abschnitt ist mit *„Was noch zu entscheiden ist“* überschrieben; es sind Entscheidungen über die Absicht des Versionsformats, keine Messungen:

1. Ab wann eine Änderung eine Version ist — *„Die Grenze ist ein Urteil und gehört in die Anweisung, nicht in den Code.“*
2. Wie die Version zählt — *„ist nicht gesetzt“*.
3. Ob der Änderungsblock je beschnitten wird — *„eine Obergrenze wäre denkbar und ist nicht gesetzt“*.

Der vierte Punkt (*Gilt das Format auch für fremde Dateien?*) ist im Abschnitt selbst beantwortet: nein.

**Offen, ohne eine Entscheidung zu verlangen:**

- [`novaberg-tool-dateien_m.md`](novaberg-tool-dateien_m.md), *Bisheriger Kopf*: *„Was fehlt, ist der Aufrufer.“*

---

## C. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, markiert und mit Grund:

- `_k` §1, Kasten — die Prämisse des Abschnitts (32768 Tokens erzwingen den Zoom) gilt seit der Messung vom 04.08.2026 nur noch für den Gesprächspfad; für die Hintergrund-Agenten ist der Zoom eine Wahl. Der Text bleibt als Herkunft stehen.
- `_t` §3.1, Kasten *„Drei Ausgaenge statt zwei“* — der Entwurf mit zwei Ausgängen (Karte oder keine); ersetzt am 20.08.2026, weil eine kürzere Liste aussieht wie eine kürzere Datei.
- `_t` §3.1 — die Erkennung über einen Regex-Automaten; abgelöst am 20.08.2026 durch `markdown-it-py`. Die Zaunbilanz bleibt, weil beide Karten an der defekten Datei falsch waren.
- `_t` §3.1 — eine feste Zuordnung von Zeichen zu Ebenen in RST; verworfen, weil jedes Dokument die Ebene durch die Reihenfolge der Zeichen bestimmt.
- `_t` §3.4.4 — ein Insert ohne Eintrag; verworfen, weil dann ein fehlender Eintrag nicht mehr von einem erlaubten Fall zu unterscheiden wäre.
- `_k` §7, *Erkenntnisse aus den Quellen* — die Edit-Ansätze der Vorbilder (ganze Datei, Diff, Shell-Befehle als Agent-Werkzeuge) mit ihren Nachteilen, dagegen die Blocknavigation als *„fünfter Weg“*.

---

## D. Aus §3.4 — Versionierung im Dokument

Die übrigen Unterabschnitte von §3.4 stehen in [`novaberg-tool-dateien_t.md`](novaberg-tool-dateien_t.md).

### 3.4.7 Was noch zu entscheiden ist

- **Ab wann ist eine Änderung eine Version?** Ein berichtigter Tippfehler soll keine Marke bekommen, eine geänderte Aussage schon. Die Grenze ist ein Urteil und gehört in die Anweisung, nicht in den Code.
- **Wie zählt die Version?** Die Beispiele zeigen `2.2`, `2.3` — ob die zweite Stelle je Änderung steigt und wann die erste, ist nicht gesetzt.
- **Wird der Änderungsblock je beschnitten?** Er wächst monoton. Solange er ein eigener Block ist, kostet er keinen Kontext; eine Obergrenze wäre denkbar und ist nicht gesetzt.
- **Gilt das Format auch für fremde Dateien?** Nein — in freigegebenen Wurzeln wird nicht geschrieben. Es gilt ausschließlich in ihrer eigenen Zone.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code prüfen oder eine Entscheidung einholen — das ist ein eigener Schritt. B1 bis B3 stammen aus der Sichtung, B4 und B5 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | [`novaberg-tool-dateien_m.md`](novaberg-tool-dateien_m.md), *Bisheriger Kopf* | Die Kopf-Struktur ist gebrochen: Der Block *„Bauzustand am 18.08.2026“* steht zwischen **Stand** und **Pfad** / **Quellen** | `[gelesen 19.09.2026]` |
| **B2** | `_t` §3.1 (Docstring von `struktur_analysieren`), `_t` §3.4 (Überschrift *„Entwurf, 17.08.2026“*) | Docstring und Überschrift heißen noch „ENTWURF“ / „Entwurf“; der bisherige Kopf sagt *„Die Operationen dieses Konzepts sind nicht mehr Entwurf“*, `versionierung.py` enthält §3.4 *„vollständig“* | `[gelesen 19.09.2026]` |
| **B3** | `_t` §3 (**Datei:** `tools/dateien/operationen.py`), `_t` §5 (Baum: nur `operationen.py`, *„Alle Funktionen aus Abschnitt 3“*) | Gebaut sind laut bisherigem Kopf vier Module: `operationen.py`, `redaktion.py`, `versionierung.py`, `hand.py`; die Featureliste nennt dazu `schreiben.py` | `[gelesen 19.09.2026]` |
| **B4** | `_t` §3.2, §3.3 gegen den bisherigen Kopf | §3.3 nennt `metadaten_aktualisieren`, der Kopf `metadaten_setzen` — als Abweichung begründet ist nur `str_ersetzen`; `datei_lesen` (§3.2) und `datei_schreiben` (§3.3) stehen in keinem der vier Module des Kopfes | `[gelesen 19.09.2026]` |
| **B5** | bisheriger Kopf, Feld **Stand** | Der Kopf nennt den 18.08.2026; `_t` §3.1 trägt Nachträge vom 20.08.2026 (drei Ausgänge, Parser, Erkenner je Endung) | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen

Keine. Das Konzept hat weder eine Versionshistorie noch eine Schlusszeile.
