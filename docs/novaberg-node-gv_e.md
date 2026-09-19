# Novaberg — Node: Gesprächsvektor (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen.** Absicht und Kopfblock: [`novaberg-node-gv_k.md`](novaberg-node-gv_k.md) · Ausarbeitung: [`novaberg-node-gv_t.md`](novaberg-node-gv_t.md) · Bauplan und Umstellung: [`novaberg-node-gv_b.md`](novaberg-node-gv_b.md) · Messungen: [`novaberg-node-gv_m.md`](novaberg-node-gv_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## A. Entschieden

Alle drei Entscheidungen stehen in dem Abschnitt, den sie tragen, und bleiben dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_t` §8.0a, Tabellenzeile `[SITUATION]` | Der situative Farbton beschreibt den Raum aus beiden Seiten — *„Nova ist offen und zugewandt, der Nutzer haelt Abstand“* — statt einer Aussage über den Nutzer aus Novas Werten. Der Text führt es als Setzung mit Datum | 10.09.2026 |
| **E2** | Abschnitt D unten, §11, Punkt *JSON vs. Freitext* | *„Natürlichsprachliche Hypothese. Kein JSON. Landschaft statt Route.“* | Konzeptphase; der Abschnitt nennt kein Datum |
| **E3** | Abschnitt D unten, §11, Punkt *Kosten vs. Nutzen* | *„Ein LLM-Call pro Turn ist akzeptabel. Der Vektor wird nur bei Länge > 0 destilliert.“* | Konzeptphase; der Abschnitt nennt kein Datum |

Den Wortlaut der Entscheidung selbst enthält das Konzept bei keiner der drei; es gibt sie als Ergebnis wieder.

**Im Text als entschieden geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_t` §10.1a: *„Die Absicht dahinter, entschieden am 14.08.2026“* — ein Impuls wird nicht noch einmal umgeformt; Landschaft und Strategie entfallen auf einem Impuls-Turn nicht.
- `_t` §10.1a, Absatz *Offen und ausdrücklich nicht in diesem Zug geändert*: ob die emotionale Gravitation auf Impuls-Turns hingehört, *„ist entschieden (nein), aber nicht gebaut“*.
- `_t` §8.1: dass die emotionale Gravitation die Lage färbt, bevor der Knoten läuft — *„das ist so entschieden und in `novaberg-thinking-drive_k.md` §5.7 begründet“*.
- `_t` §10.1, Schluss: *„Architektur-Entscheidung: Der Vektor beschreibt Landschaft, nicht Route.“*

**Wörtliche Aussagen aus der Konzeptphase — nicht gezählt:** das Zitat am Schluss von `_k` §2.7 und die sieben Zitate in §12 (Abschnitt D unten), vier davon mit Urheber. Sie formulieren die Absicht, sie entscheiden keine Frage.

---

## B. Offen beim Meister

Zwei Fragen der Absicht, die das Konzept selbst als offen führt:

| | Stelle | Frage |
|---|---|---|
| **O1** | `_m`, *Aus §10*, Absatz *„Was hier nicht entschieden ist“* | ob die Decke 2 der Vektorlänge in den drei fachlichen Modi gewollt ist. Derselbe Unterabschnitt meldet die Rundung als am 12.09.2026 behoben (Befund B3 unten) |
| **O2** | `_m`, *Aus §8.1*, *Ergebnis des Vollaudits* | die Richtung steht bei `plateau`, dem häufigsten Emotions-Vektor, auf „abwärts“ — *„kein Codefehler, sondern eine offene Konzeptfrage“*; `novaberg-node-gv_l.md` §5 hat sie benannt |

**Offen ohne Frage der Absicht** — Punkte, die das Konzept selbst als offen führt:

- Abschnitt D unten (§11): *Token-Budget* und *Fehlleitung* — ohne Stand (Befund B5).
- `_t` §8.2, *Offene Frage*: ob strukturiertes und natürlichsprachliches Format koexistieren (Befund B6).
- `_t` §10.1a: die emotionale Gravitation auf Impuls-Turns — entschieden, *„aber nicht gebaut“*.
- `_b` §10: GV5 und GV6 stehen auf ⬜.

---

## C. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Vermerk, und mit Grund:

- `_t` §8.2 und §8.4 — das strukturierte JSON-Format für den Wissensdialog; §11 führt *JSON vs. Freitext* als entschieden für die natürlichsprachliche Hypothese (E2).
- `_k` §2.4 und §3.5 — ein Label wie `"intention": "storytelling"` statt einer Richtung; *„Zwei Sätze natürliche Sprache leisten mehr als fünf JSON-Felder“*.
- `_b` §10, GV1, und `_t` §10.1, Schritt 3 — der Entity-Hop über die Fakten-Tabelle; ersetzt durch den Erinnerungsgraphen, der Block heißt seither `[VERWANDTE ERINNERUNGEN]` statt `[VERWANDTE FAKTEN]`.
- `_t` §10.1a — das Skip-Tor auf Impuls-Turns; die Auswahl *„war keine Regel, sondern ein Nebeneffekt“*, geändert am 14.08.2026.
- `_t` §8.0a, Zeile `[WISSENSLUECKEN]` — *„Semantisch nahe, noch nicht besprochene Konzepte“*; seit dem 12.09.2026 Themen, die der Nutzer nicht berührt hat.
- `_m`, *Aus §10* — die Rundung zur geraden Zahl als Ursache der Decke 2; behoben am 12.09.2026.
- `_t`, Anhang *GV-Panel* — *„Transport: WebSocket (aktuell), geplant Redis/REST“*; beides gebaut, die Rollen vertauscht. Ebenda *„Wissenslücken sagen, was Nova zum Thema nicht weiß“*; seit dem 12.09.2026 zwei Listen.
- `_k` §2.2 und §9.4 — die Abgrenzungen zum Emotions-Vektor und zum Traum-Modus.

---

## D. Aus §11 und §12 — Offene Fragen und Architektur-Zitate

§11 und §12 des ungeteilten Konzepts, ungekürzt.

## 11. Offene Fragen

- **Token-Budget:** Zusätzlicher LLM-Call + Vektor-Block im Prompt verbrauchen Tokens. Muss gegen num_ctx-Limit budgetiert werden.
- **Fehlleitung:** Nova könnte den Vektor falsch erkennen. Braucht es eine Rückkopplung? Der Nutzer widerspricht → Vektor korrigiert sich.
- **Butler-Prinzip:** Nova schlägt die Richtung vor, bestimmt sie aber nicht. Der Nutzer behält die Kontrolle.
- **~~JSON vs. Freitext~~:** ✅ Entschieden Chat 39: Natürlichsprachliche Hypothese. Kein JSON. Landschaft statt Route.
- **~~Wann nicht~~:** ✅ Gelöst Chat 39: Skip-Check bei Begrüßung/Meta + Länge 0 bei Krise.
- **~~Kosten vs. Nutzen~~:** ✅ Entschieden Chat 39: Ein LLM-Call pro Turn ist akzeptabel. Der Vektor wird nur bei Länge > 0 destilliert.

---

## 12. Architektur-Zitate

> **„Nicht auf das Gesagte antworten, sondern auf das Gemeinte."** — Chat 28, über antizipative vs. reaktive Fragen.

> **„Der Kuchen ist nicht der Punkt. Der Kuchen ist das Vehikel."** — Chat 28, über die Differenz zwischen grammatikalischer und intentionaler Analyse.

> **„Ohne den Vektor hat der Responder Daten, aber keinen Kompass."** — Chat 28, über die Rolle des Vektors als Bindeglied zwischen Analyse und Ausdruck.

> **„Ich rede eh nur mit einer Wand, die ein Echo zurückwirft — oder: Jetzt unterhalten wir uns wirklich."** — Meister, Chat 28, über den Unterschied zwischen reaktivem LLM und einem Gegenüber, das mitdenkt und das Gespräch mitführt.

> **„Man denkt um Ecken. Zuviel Gedankensprünge kann der User nicht folgen."** — Meister, Chat 28, über die Vektorlänge und kognitive Grenzen.

> **„Die Richtung und Länge des Vektors bestimmen, wo das Gespräch hingeht. Aber wer den Vektor formuliert, das ist Nova — aus ihrem Charakter, nicht aus einem Algorithmus."** — Meister, Chat 28, über den Moment, in dem Nova vom Werkzeug zum Gegenüber wird.

> **„Ich trage den Forschungsgegenstand schließlich schon seit über 50 Jahren mit mir herum."** — Meister, Chat 28, über den Unterschied zwischen gelebter Erfahrung und wissenschaftlicher Terminologie.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code prüfen oder entscheiden lassen — das ist ein eigener Schritt. B1 bis B7 stammen aus der Sichtung, B8 und B9 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_b` §10, Tabelle | GV3 und GV4 stehen auf ⬜; die Anhänge *GV3 — Invertierte Perzeption* und *GV4 — Wissenslücken* in `_t` beschreiben beide als gebaut | `[gelesen 19.09.2026]` |
| **B2** | `_t` §8.0a | Der Einleitungssatz sagt *„acht Blöcke — drei in den System-Prompt, fünf in die User-Nachricht“* und nennt einen neunten aus `ei/dreischicht.py`; der bisherige Kopf (`_m`) spricht von *„die neun Bloecke“*; die Tabelle führt zehn Zeilen, davon sechs für die User-Nachricht | `[gelesen 19.09.2026]` |
| **B3** | `_m`, *Aus §10*, Unterabschnitt *Die Decke ist nicht 3 …* | *„Länge 3 kann dort nicht auftreten“* und *„Was hier nicht entschieden ist“* lesen sich als gültig; der durchgestrichene Absatz davor meldet die Rundung als am 12.09.2026 behoben, danach erreichen alle zehn Modi die 3 | `[gelesen 19.09.2026]` |
| **B4** | `_t` §10.1, Absätze *Design-Grenze* und *Der Faktenpfad schläft* | Die Zahlen 47/411/364 sind als nicht mehr geltend markiert, stehen aber weiter im Absatz davor | `[gelesen 19.09.2026]` |
| **B5** | Abschnitt D, §11 | *Token-Budget* und *Fehlleitung* stehen ohne Stand neben drei als entschieden oder gelöst geführten Punkten | `[gelesen 19.09.2026]` |
| **B6** | `_t` §8.2 und §8.3 | Beide zeigen JSON-Formate; §11 führt *JSON vs. Freitext* als entschieden: *„Kein JSON“*. Die *Offene Frage* in §8.2 steht daneben unverändert | `[gelesen 19.09.2026]` |
| **B7** | `_k`, Verweise am Schluss | `novaberg-ei.md`, `novaberg-node-perception.md` und `novaberg-backlog.md` (*Epic 8*) sind möglicherweise veraltet | `[gelesen 19.09.2026]` |
| **B8** | `_m`, *Aus §8.1*, *Ergebnis des Vollaudits* | Verweise auf *„§10.2 `RICHTUNG_MAP`“*, *„die 64-Sektoren-Tabelle (§6)“*, *„die Repertoire-Matrix (§7)“* und *„die Strategie-Beschreibungstexte (§9.3)“* folgen der Nummerierung von `novaberg-gv-strategie_k.md`, ohne die Datei zu nennen; in diesem Konzept sind §6 die drei Ebenen der Zielführung, §7 die wissenschaftlichen Grundlagen, §9.3 der Unterschied zu heute, und ein §10.2 gibt es nicht. Die Tabelle *„§ → Datei“* führt bei diesen Verweisen in den falschen Abschnitt | `[gelesen 19.09.2026]` |
| **B9** | `_m`, *Bisheriger Kopf*, Feld **Quellen**; `_t` §8.4, Schlusssatz | `nova-09-k.md` und `nova-01-t-d` sind im Repositorium nicht vorhanden (`git ls-files`, 19.09.2026) | `[gelesen 19.09.2026]` |
