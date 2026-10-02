# Novaberg — Emotions-Avatar: Diskussion und Ergänzungen

**Teil von:** `novaberg-avatar_k.md` — dort Absicht, Kopfblock und die Tabelle „§ → Datei“
**Stand:** 02.10.2026
**Inhalt:** Entscheidungen, offene Punkte (§11), Annahmen (§12), die Änderungen der Fassungen 0.1 bis 0.5, der Kopf der übernommenen Fassung 0.10 und die Befunde der Aufteilung.

---

## Entscheidungen

| Datum | Entscheidung | Steht in |
|---|---|---|
| 29.09.2026 | Zähne als feste Kieferebenen, sie skalieren und verformen sich nicht mit dem Mund (Vorgabe Meister) | `_t` §13.1, Punkt 5 |
| 01.10.2026 | O11: die Form eines Ausdrucks am Arousal festmachen — zwei Schlüsselbilder je Sektor | `_t` §6.1, `_m` §13.7 |
| 01.10.2026 | Brauen bei Freude bewusst abweichend von FACS leicht angehoben | `_b` §13.8 |
| 02.10.2026 | Mund in Muskelkanäle nach FACS aufteilen (Vorgabe Meister) | `_t` §13.13 |
| 02.10.2026 | Featureliste: *„Die Feature-Liste ergänzen wir, wenn Novaberg ein neues Feature hat. Noch ist es nicht soweit.“* | Kopfblock `_k` |

Die Feinabstimmungen nach Sichtprüfung (*Hinweis Meister*) stehen an ihrer Stelle in `_b` §13.8, §13.10, §13.11 und `_t` §13.12.

## Offen beim Meister

O6, O7, O8, O9 und der Rest von O10 (§11), dazu aus `_m` §13.16: ob die Öffnung bei Konsonanten ein Persönlichkeitsparameter Novas wird statt eines festen Tabellenwerts.

---

## 11. Offene Punkte

### Audit-abhängig (Fakten über den bestehenden Code)

| Nr | Frage | Doku sagt |
|---|---|---|
| O1 | Stimmen Kanon, Sektor-Map und Bezeichner im Code mit `novaberg-ei-plutchik.md` §3 überein? | 16 + neutral, `EMOTION_SEKTOR_MAP`, `EMOTION_KANON` in `config.py` |
| O2 | Struktur von Novas Emotionszustand im Code: Felder, Wertebereiche, Arousal pro Eintrag? | `nova_emotions_verlauf: list[dict]`, Dominante = 1.0 |
| O3 | Erreichen `nova_emotion`, `nova_arousal`, ggf. der Verlauf den Client? Über welchen Weg? | in `GespraechAntwort` ergänzt, Client offen |
| O4 | Panel-Basisklasse, Registrierung, UNIQUE/CATEGORY; Referenz-Panel mit DrawingArea/Cairo? | — |
| O5 | Wo sind die Plutchik-Farben definiert (Gravitationsgraph)? | — |

**Hinweis Doku-Drift:** `novaberg-ei-plutchik.md` §9 beschreibt für
`client/ui/emotionen_tab.py` einen „QPainter-Umbau“. Qt ist laut Projektstand
aufgegeben (GTK4). Der Abschnitt ist vermutlich veraltet und sollte im Audit
mit geprüft werden.

### Designentscheidungen

| Nr | Frage |
|---|---|
| O6 | Lineare oder nichtlineare Arousal-Kennlinie für die Gesichtsausprägung? → **teilweise beantwortet** durch O11: stückweise linear über zwei Schlüsselbilder je Sektor (`_t` §6.1); offen für Sektoren und Kanäle ohne moderates Schlüsselbild (W5) |
| O7 | Vollen Verlauf mischen oder nur die Dominante zeigen? |
| O8 | Darstellung von `nova_emotion_konflikt` als sichtbare Ambivalenz? |
| O9 | Quelle für die Sprechschicht: existiert TTS mit Pegel oder Visemen? ~~Falls nicht, entfällt Schicht 3 in v1.~~ → Der Prototyp spricht ohne TTS, mit Lautzeiten aus dem Text (`_t` §13.12, §13.14); mit TTS startet der Mund 0,10–0,14 s vor dem Ton (`_m` §13.15, §13.16). Offen bleibt, ob v1 ohne Tonausgabe spricht (W4) |
| O10 | ~~Figurendesign~~ — teilweise beantwortet: Figur aus Bleistiftvorlage, siehe Abschnitt 13. Offen bleibt, ob die Merkmale in Stil und Detailgrad weiter an die Vorlage angeglichen werden müssen (Sichtprüfung). |

---

## 12. Annahmen

| Nr | Annahme | Status |
|---|---|---|
| A1 | ~~16 Emotionen = 8 Primäre + 8 Dyaden~~ | **widerlegt** (Doku): 8 Sektoren × 2 Intensitäten |
| A2 | Novas Emotionszustand ist im Client verfügbar oder dorthin transportierbar | Doku bejaht teilweise, Code offen (O3) |
| A3 | Kalibrierwerte aus dem Prototyp sind ein brauchbarer Startpunkt für 7 der 8 Sektoren | nicht validiert |
| A4 | `ω ≈ 5 /s` ergibt einen als natürlich empfundenen Übergang von ca. 1 s | nicht gemessen |

---

## Befunde der Aufteilung

`[gelesen]` — 02.10.2026, beim Aufteilen der Fassung 0.10. Widersprüche im Text. **Alle elf aufgelöst am 02.10.2026** — markiert an der Stelle selbst, gegen den Text und gegen den Prototyp geprüft (`labor/avatar/index.html`):

| Nr | Stelle | Befund |
|---|---|---|
| W1 | Kopf der Fassung 0.10 | Version 0.10 und Stand 29.09.2026, die Einträge reichen bis zum 02.10.2026; die Änderungsliste endet bei v0.5. |
| W2 | `_t` §5.2 | *„Sektor 6 (Enttäuschung) ist dort nicht enthalten und muss neu entworfen werden“* — `_m` §13.7 nennt Werte für Enttäuschung, `_t` §13.13 ihren Muskelkanal. |
| W3 | `_t` §4 | *„vollständig durch einen Vektor … beschrieben“* — die Kanaltabelle kennt weder die Muskelkanäle aus §13.13 noch die Sprechkanäle `round`, `press`, `fv` aus §13.12. |
| W4 | §11, O9 | *„Falls nicht, entfällt Schicht 3 in v1“* — `_t` §13.12 bis §13.14 und `_m` §13.15, §13.16 bauen und messen die Sprechschicht ohne TTS. |
| W5 | §11, O6, und `_t` §6.1 | O6 fragt nach der Kennlinie; O11 hat sie in §6.1 teilweise beantwortet (stückweise linear über zwei Schlüsselbilder). |
| W6 | `_t` §6.1, Tabelle | Trauer intensiv `mo` 34, `mw` 106 — `_b` §13.11 korrigiert auf `mo` 28, `mw` 96. |
| W7 | `_t` §13.9 | *„Damit entfällt die Grenze aus 13.4“* — die Grenze (Ärger intensiv `mo` 70) steht in `_m` §13.7, nicht in §13.4. |
| W8 | `_t` §13.12 | *„Kalibrierung an einem Video … steht aus“* — derselbe Abschnitt berichtet die Kalibrierung an Video vom 02.10.2026. |
| W9 | `_t` §13.12 | *„Zeitquelle Weg 3 (aus Text)“* — Weg 1 und Weg 2 sind nirgends benannt. |
| W10 | `_t` §8 | Schicht 3 *„Mundöffnung“*, *„addiert auf `mouth_open`“* — seit §13.12 und §13.13 setzt die Sprechschicht Öffnung, Kiefer, Breite und Muskelkanäle. |
| W11 | `_t` §6.1, `_m` §13.7 | Moderate Schlüsselbilder nur für Trauer und Ärger, Enttäuschung `mw`/`mo` 80/6 — der Prototyp führt auch für Enttäuschung ein moderates Schlüsselbild (80/0) und intensiv 84/12 (`labor/avatar/index.html`, `SECTORS`, gelesen am 02.10.2026). |

---

## Änderungen der Fassungen 0.1 bis 0.5

**Änderungen gegenüber v0.4:**
- Neuer Kanal `jaw` (Kieferöffnung) getrennt von `mouth_open` (Lippenöffnung), Abschnitt 4.
- Brauen für Trauer, Enttäuschung und Ärger deutlicher getrennt; abgeleitete Falten (4.1).
- Bereinigung der Vorlage mit engen Masken (13.1, Punkt 1).

**Änderungen gegenüber v0.3:**
- Abschnitt 6.1: Intensität stückweise linear über zwei Schlüsselbilder je Sektor
  (moderat/intensiv), Entscheidung O11 (Meister, 01.10.2026).
- Mundwerte aller Sektoren nach Messung an drei Personen (13.7) übernommen.

**Änderungen gegenüber v0.2:**
- Neuer Abschnitt 13: Figur aus Vorlage (Bleistiftzeichnung von Nova), Pipeline und Befunde aus dem Prototyp.
- O10 teilweise beantwortet: Vorlage-basierte Figur ist machbar.

**Änderungen gegenüber v0.1:**
- Annahme „8 Primäre + 8 Dyaden“ war falsch. Das System nutzt 8 Sektoren × 2 Intensitäten.
  Abschnitt 5 und 6 neu.
- Intensität kommt aus dem vorhandenen Arousal, nicht aus einem eigenen Parameter.
- Offene Frage zur Mischung gegensätzlicher Emotionen (v0.1 O7) entfällt:
  Das entscheidet die bestehende Sektor-Normalisierung, nicht der Avatar.
- Datenquelle präzisiert: Novas eigener Emotionsstrang (Dual-Emotion).

Die Fassungen 0.6 bis 0.10 haben keine Änderungsliste; ihre Änderungen stehen datiert in §13.8 bis §13.16 (W1).

## Kopf der übernommenen Fassung 0.10

**Version:** 0.10
**Stand:** 29.09.2026
**Status:** Konzept. Im Client nichts implementiert; ein HTML-Prototyp liegt unter `labor/avatar/` (Abschnitt 13).
**Suffix:** `_k` (Konzept)
**Grundlagen:** `novaberg-ei-plutchik.md`, `novaberg-ei-dual-emotion_k.md`
