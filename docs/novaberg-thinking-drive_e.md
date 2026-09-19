# Novaberg — Antrieb (Entscheidungen)

**Teil 3 von 3 — Diskussion, Entscheidungen, offene Fragen.** Absicht und Planung: [`novaberg-thinking-drive_k.md`](novaberg-thinking-drive_k.md) · Umsetzung: [`novaberg-thinking-drive_t.md`](novaberg-thinking-drive_t.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 1. Entschieden

Beide Entscheidungen stehen mitten in einem Abschnitt, den sie tragen, und bleiben dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_k` §5.7, Absatz *„Zur Funktionszeile, entschieden …“* unter der Tabelle *Abgrenzung zur Ziel-Gravitation* | Die emotionale Gravitation färbt die Haltung **und lenkt mit**; die ursprüngliche Trennung *Ziele lenken, Erinnerungen färben* ist aufgegeben | 28.07.2026 (der Tag der Messung im Absatz *Wirkort* desselben Abschnitts) |
| **E2** | `_t` §7, Kasten *„Widerlegt am 02.08.2026“* | Ein Ziel gehört einer Beziehung, nicht Nova allein; die Tabelle `ziele` trägt das Gegenüber | 02.08.2026 |

Der Wortlaut der Entscheidungen steht in keinem der beiden Abschnitte; beide geben sie als Ergebnis wieder.

---

## 2. Offen beim Meister

Keine. Das Konzept stellt keine Frage an den Meister.

**Offen ohne Frage an den Meister** — Kalibrierungen, die das Konzept selbst als Startwerte führt:

- `_k` §5.7, *Mechanismus*: die Gewichtung der vier Kräfte auf Novas Emotion (Startwerte 0.4 / 0.3 / 0.2 / 0.1).
- `_t` §11, Absatz unter der Tabelle: alle Schwellwerte, besonders die Gravitationsschwelle und die Empathie-Faktoren; Zielmetrik 0,5–2,0 aktivierte Zielsätze je Turn.

---

## 3. Diskussion und verworfene Varianten

Die verworfenen Fassungen stehen durchgestrichen an ihrer Stelle, mit Grund:

- `_k` §3.3 — der Gesprächsvektor als kurzfristiges Ziel; ersetzt durch einen eigenen Zielhorizont (28.08.2026).
- `_k` §5.7, *Wirkort* — die emotionale Gravitation in EI-Calc; ersetzt durch einen eigenen Node zwischen Enricher und Reducer.
- `_t` §5.3 — die Addition `salienz_basis + gravitationsterm`; ersetzt durch die Auffüllregel (09.09.2026).
- `_t` §7.1 — `aktualisiert_am` als Anker des Verfalls; ersetzt durch `motivation_basis` / `motivation_basis_am`.
- `_t` §7.1 — `motivation` als materialisiertes Feld, das jede Abfrage liest; widerlegt am 28.08.2026, seither beim Lesen gerechnet.

---

## 4. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder den Meister prüfen — das ist ein eigener Schritt.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_k` §8.2 | §8.2 rechnet weiter `salienz_final = salienz_basis + gravitationsterm`; `_t` §5.3 und der bisherige Kopf führen diese Addition als am 09.09.2026 durch die Auffüllregel ersetzt | `[gelesen 19.09.2026]` |
| **B2** | `_t` §7.1, Tabelle, Zeile `ziel_typ` | Die Spalte kennt nur `langfristig` oder `mittelfristig`; `_k` §3.3 und der Text unter derselben Tabelle führen seit dem 28.08.2026 auch `kurzfristig` | `[gelesen 19.09.2026]` |
| **B3** | `_t` §7.1, *Abfrage-Pattern* | Die Abfrage filtert nur `aktiv` und `user_id = 'nova'`, ohne `character_id`; der Kasten in `_t` §7 und die Spalte `character_id` sagen, dass ein Ziel einem Paar gehört | `[gelesen 19.09.2026]` |
| **B4** | `_t` §11, Absatz unter der Tabelle | Der Absatz nennt `GRAVITATIONS_SCHWELLE` mit 0.3; die Tabelle darüber führt den Default 0.40 | `[gelesen 19.09.2026]` |
| **B5** | `_k` §13.3, Tabelle | Die Zeile verweist auf `novaberg-thinking-drive.md`, ohne `_k`; die Datei heißt `novaberg-thinking-drive_k.md` | `[gelesen 19.09.2026]` |
| **B6** | `_k` §6, §8.4 | Das Konzept sagt nicht, ob die zweiseitige Emotion (Nova und Nutzer getrennt) und das Konfliktsignal `emotion_konflikt` gebaut sind; §6.1 spricht im Präsens von *„Heute hat Nova keine eigene Emotion“*, während `_k` §5.7 die Nova-Emotion (Pfad 2) als bestehende Formel ergänzt | `[gelesen 19.09.2026]` |
| **B7** | `_k`, ganzes Konzept | Keine Reihenfolge und keine Phasen der Bauteile, kein `ZIEL` / `TEST` / `MESSUNG` je Bauteil; ein Abnahmekriterium nur teilweise (`_t` §11: 0,5–2,0 aktivierte Zielsätze je Turn); offene Fragen nur als *„Startwerte kalibrieren“* | `[gelesen 19.09.2026]` |
