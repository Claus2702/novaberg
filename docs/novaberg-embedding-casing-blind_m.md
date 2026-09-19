# EMBEDDING-CASING-BLIND (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-embedding-casing-blind_k.md`](novaberg-embedding-casing-blind_k.md) · Ausarbeitung: [`novaberg-embedding-casing-blind_t.md`](novaberg-embedding-casing-blind_t.md) · Bauplan und Umstellung: [`novaberg-embedding-casing-blind_b.md`](novaberg-embedding-casing-blind_b.md) · Diskussion und Ergänzungen: [`novaberg-embedding-casing-blind_e.md`](novaberg-embedding-casing-blind_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Bisheriger Kopf

Der Kopf des ungeteilten Konzepts, ungekürzt. Er trägt die Messung vom 04.09.2026 und steht deshalb hier.

**Status:** Befund belegt, Sprint offen
**Nachtrag 04.09.2026 — das Bild ist zurueck, die Ursache ist eine andere.** `[gemessen]` heute: **14.947 Reinforcements auf 1.538 Knoten (Faktor 9,7)**, `cosine = 1.0000` in **95,2 %** — gegen 2.910 auf 302 (Faktor 9,6) am 12.07.2026. Das casing-blinde Embedding ist **nicht** die Ursache: Der KZG-Eintrag wird entgegen `novaberg-memory-synapsen_k.md` §7.7 nach der Promotion nicht geloescht und matcht den Knoten, der aus ihm selbst entstand. **Wer diese Zahlen sieht, greife nicht wieder zum Embedding** — die Kennung ist `KZG-EINTRAG-BLEIBT-NACH-PROMOTION`.
**Priorität:** höchste — oberhalb von `broadcast()` / Lügende Logs
**Chat:** 107
**Betrifft:** die Grundschicht des gesamten semantischen Gedächtnisses

---

## Aus §1 — Der Befund

Der Befund selbst (§1) und §1.2 stehen in [`novaberg-embedding-casing-blind_k.md`](novaberg-embedding-casing-blind_k.md).

### 1.1 Beweiskette (11.–12. Juli, Live gemessen)

| Probe | Ergebnis |
|---|---|
| `embed("Hund")` vs. `embed("Katze")` | **768/768 Komponenten bit-identisch**, max. Abweichung `0.000e+00` |
| `embed("Zahnarzttermin")` vs. `embed("Friseurtermin")` | bit-identisch |
| `embed("Katze")` vs. `embed("Bundeskanzler")` | bit-identisch |
| `embed("Dog")` vs. `embed("Cat")` — **englisch, groß** | bit-identisch |
| `embed("hund")` vs. `embed("katze")` — **klein** | verschieden |
| `embed("dog")` vs. `embed("cat")` — **klein** | verschieden |
| Kontrolle: *„Der Zug nach Hamburg…"* vs. *„Die Katze schläft…"* | verschieden (0/768) |

**Ausgeschlossen:** Cache zwischen Requests (Batch in *einem* Request identisch),
`num_ctx`-Overload (2048 wie 8192 identisch), Route (`/api/embed` wie
`/api/embeddings`), defektes Modell (Kontrollpaare sauber verschieden), defekte
Messkette (Identität liefert exakt 1.0, Vektorlänge 768).

**Es ist ausschließlich das Casing. Es ist keine Sprachschwäche des Modells.**

---

## 8. Messwerkzeuge (Chat 107, außerhalb des Repos)

| Skript | Zweck |
|---|---|
| `embed_probe.py` | Triplet-Messung DE/EN, erste Sonde |
| `embed_probe2.py` | Sanity-Check der Messkette + Präfix-Gegentest |
| `embed_compare.py` | Modellvergleich mit Casing-Eingangsprüfung |
| `embed_kalibrierung.py` | Verteilungsmessung am echten 302-Knoten-Korpus |

Reine stdlib (numpy optional). Kein Repo-Kontakt. Aufbewahren — die
Casing-Eingangsprüfung wird bei jedem künftigen Modellwechsel gebraucht.
