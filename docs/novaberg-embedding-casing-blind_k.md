# EMBEDDING-CASING-BLIND

**Absicht:** Im System ist kein Embedding-Modell im Einsatz, das großgeschriebene Wörter auf `[UNK]` fallen lässt — das blinde Modell wird ersetzt, alle gespeicherten Vektoren werden neu eingebettet, alle Ähnlichkeitsschwellen am echten Vektorraum neu kalibriert, und jedes künftige Modell besteht vor dem Einsatz die Casing-Eingangsprüfung.
**Stand:** 19. September 2026 (am selben Tag in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** keine eigene Zeile in der Featureliste; am nächsten *Embedding-Konsolidierung (ein Pfad)* 🟢 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-embedding-casing-blind_t.md`](novaberg-embedding-casing-blind_t.md) · [`novaberg-embedding-casing-blind_b.md`](novaberg-embedding-casing-blind_b.md) · [`novaberg-embedding-casing-blind_e.md`](novaberg-embedding-casing-blind_e.md) · [`novaberg-embedding-casing-blind_m.md`](novaberg-embedding-casing-blind_m.md)
**Entschieden:** 1 · **Offen beim Meister:** 0 (Liste in [`novaberg-embedding-casing-blind_e.md`](novaberg-embedding-casing-blind_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-embedding-casing-blind_k.md §3` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-embedding-casing-blind_t.md`](novaberg-embedding-casing-blind_t.md), `_b` ist [`novaberg-embedding-casing-blind_b.md`](novaberg-embedding-casing-blind_b.md), `_e` ist [`novaberg-embedding-casing-blind_e.md`](novaberg-embedding-casing-blind_e.md), `_m` ist [`novaberg-embedding-casing-blind_m.md`](novaberg-embedding-casing-blind_m.md).

| § | Datei |
|---|---|
| 1 · 1.2 | `_k` |
| 1.1 | `_m` |
| 2 · 2.1 · 2.2 | `_t` |
| 3 | `_t` |
| 3.1 | `_k` |
| 4 · 4.1 · 4.2 | `_t` |
| 5 (Phasen 0–4) | `_b` |
| 6 | `_e` |
| 7 | `_e` |
| 8 | `_m` |
| bisheriger Kopf (Status, Nachtrag 04.09.2026 mit Messung, Priorität, Sitzung, Betrifft) | `_m` |
| Entschieden, Offen, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## 1. Der Befund

`nomic-embed-text` (v1) trägt im GGUF ein **`bert-base-uncased`-Vokabular**
(30 522 Tokens, `unknown_token_id = 100`). Ein uncased-Vokabular enthält **keinen
einzigen Großbuchstaben** — auch keine großgeschriebenen Einzelbuchstaben, auf die
WordPiece sonst zurückfallen könnte.

Das `do_lower_case`-Flag ist bei der GGUF-Konvertierung **nicht durchgekommen**.

> **Folge: Jedes Wort, das einen Großbuchstaben enthält, fällt vollständig auf
> `[UNK]`.** Im Deutschen sind das **alle Substantive** — der gesamte
> Bedeutungsträger. Übrig bleibt das Funktionswort-Skelett.

> **Hinweis zur Aufteilung (19.09.2026):** §1.1 *Beweiskette (11.–12. Juli, Live gemessen)* steht in [`novaberg-embedding-casing-blind_m.md`](novaberg-embedding-casing-blind_m.md).

### 1.2 Warum es 4 Monate unentdeckt blieb

Bei einem **englischen** Satz trifft `[UNK]` nur das erste Wort und Eigennamen —
der Inhalt überlebt. *„The dentist appointment is on Tuesday"* → `[UNK] dentist
appointment is on [UNK]`.

Bei einem **deutschen** Satz trifft es jedes Substantiv. *„Der Zahnarzttermin ist
am Dienstag"* → `[UNK] [UNK] ist am [UNK]`.

> **In der englischsprachigen Community ist der Bug praktisch unsichtbar. In einer
> deutschen Anwendung ist er tödlich.** Kein Issue dazu auffindbar. Kein Log, kein
> Fehler, keine Exception — das Modell liefert 768 saubere Floats. pgvector rechnet
> brav Kosinus-Ähnlichkeiten aus. Alle Pipelines melden Erfolg.

---

## Aus §3 — Der Nachfolger: `nomic-embed-text-v2-moe`

Der Modellvergleich, die Entscheidung und ihre Nachträge (§3) stehen in [`novaberg-embedding-casing-blind_t.md`](novaberg-embedding-casing-blind_t.md). Hier steht die Konvention, die aus dem Befund folgt.

### 3.1 Neue Konvention: Casing-Eingangsprüfung

> **Jedes Embedding-Modell wird vor Einsatz geprüft: Liefert `embed("Hund")` und
> `embed("Katze")` bit-identische Vektoren → durchgefallen. Kein Datenblatt der Welt
> hilft dann noch.**

Der Fehler saß nicht im Modell, sondern in der GGUF-Konvertierung. Das kann jedem
Modell wieder passieren.

> **§1.1, §2 bis §8 ohne §3.1 stehen nicht in dieser Datei.** Tragweite, Nachfolger und Schwellwert-Landschaft (§2–§4) stehen in [`novaberg-embedding-casing-blind_t.md`](novaberg-embedding-casing-blind_t.md); der Sprint-Plan (§5) in [`novaberg-embedding-casing-blind_b.md`](novaberg-embedding-casing-blind_b.md); die offenen Punkte (§6) und die Lessons (§7) in [`novaberg-embedding-casing-blind_e.md`](novaberg-embedding-casing-blind_e.md); die Beweiskette (§1.1), die Messwerkzeuge (§8) und der bisherige Kopf mit dem Nachtrag vom 04.09.2026 in [`novaberg-embedding-casing-blind_m.md`](novaberg-embedding-casing-blind_m.md). Welche Datei welchen Abschnitt trägt, sagt die Tabelle oben.
