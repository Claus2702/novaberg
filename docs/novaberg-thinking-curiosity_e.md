# Novaberg — Neugier (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden. Absicht und Kopfblock: [`novaberg-thinking-curiosity_k.md`](novaberg-thinking-curiosity_k.md) · Ausarbeitung: [`novaberg-thinking-curiosity_t.md`](novaberg-thinking-curiosity_t.md) · Bauplan und Umstellung: [`novaberg-thinking-curiosity_b.md`](novaberg-thinking-curiosity_b.md) · Messungen: [`novaberg-thinking-curiosity_m.md`](novaberg-thinking-curiosity_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## A. Entschieden

Keine. Das Konzept führt keine Entscheidung mit Gegenstand, Urheber und Datum.

**Genannt, aber nicht gezählt:**

- Der bisherige Kopf (Abschnitt F, Feld **Quellen**) nennt eine *Traum-Modus-Entscheidung* als Quelle, ohne ihren Inhalt, ihr Datum oder ihren Urheber.
- Der Vermerk in [`novaberg-thinking-curiosity_m.md`](novaberg-thinking-curiosity_m.md): Die Kopfzeile *„Code-Alignment — Konzept unverändert“* beziehe sich auf einen Abgleich, bei dem die Abweichung *„gesehen und bewusst stehengelassen wurde“* — ohne Urheber.
- Die Berichtigung in [`novaberg-thinking-curiosity_m.md`](novaberg-thinking-curiosity_m.md): *„Die zwanzig Formelstellen bleiben unverändert“*; die durchgängige Umbenennung gehört in den Bau — eine Vorgabe für den Bau, ohne Urheber.

---

## B. Offen beim Meister

Keine. Das Konzept stellt keine Frage, die eine Entscheidung verlangt.

---

## C. Offen ohne Frage

Punkte, die das Konzept selbst als offen führt:

- §11 unten: Embedding-Qualität, Häufigkeit des Charakter-Embeddings, Resonanz-Persistenz, Salienz-Kopplung im HumanGraph, Feld-Divergenz.
- `_k`, Vermerk *Übergeordnet seit dem 06.08.2026*: *„Die Überarbeitung dieses Dokuments auf den Zyklus steht aus.“*
- Die Berichtigung in [`novaberg-thinking-curiosity_m.md`](novaberg-thinking-curiosity_m.md): *„Die gebaute Formel braucht einen Leser, und ihre Skala braucht eine Eichung an Messwerten statt an einer Beispieltabelle.“* Dazu die durchgängige Umbenennung beim Bau.
- `_t` §4.7, Tabelle *Wo Reflexion noch fehlt*: vier Instanzen als geplant.

Der Abschnitt §11 des ungeteilten Konzepts folgt unverändert.

## 11. Offene Fragen

- **Embedding-Qualität:** Ist nomic-embed-text fein genug, um "Botanik → Bioakustik" als semantisch nah und "Botanik → Kryptowährung" als semantisch fern zu bewerten? Muss getestet werden.
- **kern_hash-Embedding-Frequenz:** Wie oft wird das Charakter-Embedding neu berechnet? Bei jedem Destillations-Zyklus? Oder nur bei `hash_dirty`?
- **Resonanz-Persistenz:** Entitäten mit Resonanz < 0.3 nach N Zyklen ohne Bestätigung — soll die Resonanz decayen? Oder bleibt sie stabil?
- **Salienz-Kopplung im HumanGraph:** Wenn `_farbe_charakter` Neugier signalisiert, sollte das die Salienz des KZG-Eintrags für `user_id: nova` explizit erhöhen? Oder reicht die implizite Erhöhung durch die Charakter-Hash-Destillation?
- **Feld-Divergenz:** Über Monate könnte Novas Feld so weit wachsen, dass es seine Identität verliert ("interessiert sich für alles"). Braucht es ein Feld-Budget (max N Entitäten mit hoher Resonanz)?

---

## D. Diskussion und verworfene Varianten

Abwägungen und widerlegte Fassungen stehen an ihrer Stelle, mit Grund:

- Der Vermerk in [`novaberg-thinking-curiosity_m.md`](novaberg-thinking-curiosity_m.md) — zwei Sätze durchgestrichen und am 08.09.2026 gegen den Code widerlegt: *„Die Formel … wurde nie gebaut“* und *„Insbesondere fehlt der Neuheits-Faktor vollständig“*.
- `_t` §4.6 — zwei Verfolgungsstrategien nebeneinander: Gap (Traum-Modus, breit, drei Iterationen) gegen Verfolgung (VertiefungsAgent v2, tief, zwanzig Iterationen), mit Vergleichstabelle.
- `_t` §4.7 — zwei LLM-Calls je Iteration statt einem, begründet mit dem Primacy-Bias; Reflexion in Agenten nur bei destruktiven oder ungewöhnlichen Aktionen, *„sonst wäre jede Aktion um einen LLM-Call teurer“*.
- `_t` §5.2 — das Themen-Modell ist *„keine eigene Datenstruktur“*, es entsteht implizit im GV-LLM-Call.
- `_t` §5.3 — der `sozialer_spielraum` ist *„kein separater Python-Wert“*, sondern Kontext im GV-LLM-Call.
- `_t` §6.2 — die toten Pfade sind gewollt: Sie verhindern, dass Nova beliebig wird.
- `_k` §8.2 — was der Traum-Modus ausdrücklich nicht ist.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder gegen eine Entscheidung prüfen — das ist ein eigener Schritt. B1 bis B5 stammen aus der Sichtung, B6 bis B9 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_m`, Berichtigung, letzter Absatz | *„Wer hier `effektive_neugier` liest, meint `neugier_vektor` und findet ihn im Code nicht.“*; die Berichtigung selbst sagt, `neugier_vektor` ist gebaut (erste Tabelle, gebaut am 27.07.2026) und *„gebaut, gerechnet, gespeichert“* (zweite Tabelle) | `[gelesen 19.09.2026]` |
| **B2** | `_t` §3.4, §4.2 (Phase 2), §9 | `TRAUM_NEUGIER_SCHWELLE` (0.25) steht als gültige Konstante da; die Berichtigung in `_m` sagt, sie existiert im Code nicht, und nichts prüft `neugier_vektor` gegen eine Schwelle | `[gelesen 19.09.2026]` |
| **B3** | `_b` §10 | Die Schritte TR1 bis TR9 haben keine Statusspalte; welcher Schritt gebaut ist, sagt die Tabelle nicht | `[gelesen 19.09.2026]` |
| **B4** | `_t` §4.7, Tabelle *Wo Reflexion noch fehlt* | Die Zeile *GV-Node* mit *„⬜ GV3“* ist veraltet | `[gelesen 19.09.2026]` |
| **B5** | `_k`, Vermerk *Übergeordnet seit dem 06.08.2026* | Das Konzept ist dem Erkenntniszyklus untergeordnet; der Textkörper ist nicht auf den Zyklus nachgezogen (der bisherige Kopf nennt ihn unverändert seit dem 17. April 2026) | `[gelesen 19.09.2026]` |
| **B6** | `_t` §5.1, §5.4 bis §5.7 gegen `_m` | Der Vermerk sagt, was das Konzept `effektive_neugier` nennt, sei `neugier_vektor` (`NOVA_NEUGIER × Resonanz × Neuheit`, §3.3); im Gespräch rechnet §5 `effektive_neugier = NOVA_NEUGIER × Resonanz` (§5.3: `× sozialer_spielraum`), ohne Neuheit. Derselbe Name steht für zwei verschiedene Größen | `[gelesen 19.09.2026]` |
| **B7** | `_t` §6.1, §6.2 | Die Neugier-Werte der Beispiele (0.64, 0.61, 0.14, 0.28) sind Resonanz × Neuheit ohne den Faktor `NOVA_NEUGIER`; nach §3.3 mit dem Default 0.5 wären sie halb so groß | `[gelesen 19.09.2026]` |
| **B8** | `_t` §4.6 (*„Der bestehende VertiefungsAgent“*); `_k` §8.3 | Beide setzen einen vorhandenen VertiefungsAgenten voraus; die Featureliste führt *VertiefungsAgent* ⚫ mit *„existiert nicht“* `[gemessen]` | `[gelesen 19.09.2026]` |
| **B9** | `_t` §5.1 gegen §5.4 und §9 | §5.1 nennt vier Stufen der Fragetiefe (unter 0.2, 0.2–0.4, 0.4–0.6, über 0.6); §5.4 und §9 kennen zwei Schwellen (`GV_NEUGIER_LEICHT` 0.2, `GV_NEUGIER_TIEF` 0.4), für *„über 0.6: tiefes Graben“* gibt es keine | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen — bisheriger Kopf

### Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier; der gemessene Stand steht im Vermerk in `_m`. Eine Schlusszeile hatte das Konzept nicht; seine letzte Zeile gehört zu den *Verwandten Dokumenten* in `_k`.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Neugier — Charakter-Resonanz, intrinsische Motivation, Reflexion (Konzept)
**Stand:** 8. September 2026 — der Namens- und Zustandsvermerk ist gegen den Code berichtigt (zwei Sätze widerlegt, `neugier_vektor` ist gebaut); der Textkörper unverändert seit 17. April 2026, Chat 52
**Pfad:** novaberg/docs/novaberg-thinking-curiosity_k.md
**Quellen:** Chat 10 (Traum-Modus-Entscheidung, Resonanz-Modell), Chat 20 (Spiegelproblem, Saatgut), Chat 39 (Gesprächsvektor), Chat 45 (Nova-Destillation), Chat 51 (Neugier-Mechanismus)
