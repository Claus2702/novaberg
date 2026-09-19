# EMBEDDING-CASING-BLIND (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-embedding-casing-blind_k.md`](novaberg-embedding-casing-blind_k.md) · Ausarbeitung: [`novaberg-embedding-casing-blind_t.md`](novaberg-embedding-casing-blind_t.md) · Diskussion und Ergänzungen: [`novaberg-embedding-casing-blind_e.md`](novaberg-embedding-casing-blind_e.md) · Messungen: [`novaberg-embedding-casing-blind_m.md`](novaberg-embedding-casing-blind_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 5. Sprint-Plan

### Phase 0 — Prompt↔Knoten-Kalibrierung  ✅ teilerledigt Chat 107
Abdeckungsmessung (100 Prompts × 302 Knoten) durchgeführt; `anker_retrieval`
gemessen gesetzt, die übrigen 6 als begründete Startwerte mit
Wachposten-Kommentar (§4.2). Rest-Nachmessung nach Live-Betrieb.

### Phase 1 — Längen-Vorprüfung der übrigen fünf Spalten  ⚠ offen
Nur `lzg_knoten` wurde gegen das 512-Token-Limit geprüft. **`entitaeten`, `fakten`,
`ziele`, `delegations_akten.themen`, `langzeitgedaechtnis` sind ungeprüft.**

```sql
SELECT 'entitaeten' AS t, max(length(name || ' ' || coalesce(zusammenfassung,''))) FROM entitaeten
UNION ALL SELECT 'fakten', max(length(inhalt)) FROM fakten
UNION ALL SELECT 'ziele',  max(length(beschreibung)) FROM ziele;
```
Grenze: ~1500 Zeichen. Alles darüber wird still abgeschnitten.

### Phase 2 — Re-Embedding-Werkzeug bauen
**Es existiert kein Re-Embedding-Pfad.** Der Audit ist eindeutig: *„Kein `UPDATE
lzg_knoten SET embedding` im ganzen Repo."* Vorhandene Backfills laufen nur auf
`WHERE embedding IS NULL`.

Vorlage: `tools/migrate_lzg_synapsen.py` (Dry-Run-Modus, `--commit`, direkter
Embed-Call). Muss abdecken: 6 Postgres-Spalten + KZG-Hashes in Redis (float32-Bytes,
`raw_redis` ohne decode) + Shadow-Stack (JSON).

### Phase 3 — Umschaltung  ⚠ Reihenfolge ist zwingend
Ein **Mischbestand ist schlimmer als der jetzige Zustand**: Alte und neue Vektoren
liegen in verschiedenen Räumen, der Kosinus zwischen ihnen ist bedeutungslos, und
pgvector merkt nichts.

1. **Server stoppen** (kein Turn darf in den Mischzustand fallen)
2. Schwellwerte setzen (Phase 0 + §4.1) — ✅ Code-Commit `3adc682` (Chat 107).
   ⚠ Ab hier gilt: KEIN Server-Neustart vor Schritt 3 (Modellwechsel) — die
   neuen Schwellen gegen den alten Raum ließen das Retrieval komplett tot laufen.
3. `EMBED_MODEL` umschalten an **drei** Orten — ✅ Chat 107 (Commit `0eb1584`):
   - `~/ki-assistent/docker-compose.yml` (**wirksam** — Env schlägt Config-Default!)
     ⚠ Liegt AUSSERHALB des Repos und wurde **von Hand geändert** — im Repo
     nicht zu finden, nicht danach suchen.
   - `novaberg/docker-compose.template.yml` ✅
   - `novaberg/server/config.py` (Default) ✅ — samt Begründungs-Kommentar
     (Casing-Blindheit, keine Task-Präfixe, Pull-Schritt).
   Mitgezogen: READMEs (Architektur, VRAM-Tabelle, `ollama pull`-Block),
   Docstrings embed_worker/registry, Enricher-Kommentar; toter
   `EMBED_MODEL`-Import in `main.py` entfernt.
   ⚠ Phase B muss den Container NEU ERZEUGEN (`docker compose up -d`) —
   ein bloßer Restart liest die Compose-Env nicht neu.
4. Re-Embedding laufen lassen (Dry-Run → Diff prüfen → `--commit`) —
   `python -m tools.reembed_all --commit` (deckt inkl. Shadow-Leerung alles ab;
   Werkzeug ✅ Chat 107, Commit `f866e1b`)
5. **Gewichts-Reset** — `--target reset` (✅ gebaut Chat 107, NICHT in "all"):
   2910 Reinforcements (93 %) entstanden durch Skelett-Kollisionen
   (cosine_max = 1.0000 im pipeline_log); `haeufigkeit` speist
   `gewicht_absolut`, `gewicht_absolut` speist die Charakter-Destillation —
   Nova trägt einen Charakter aus Zufallsgewichten. Der Reset rechnet den
   Anlagezustand EXAKT zurück (`initial_roh = roh − (haeufigkeit−1) × Boost`,
   dann die echte `gewicht_absolut_berechnen`; belegt: einziger Schreiber ist
   `knoten_verstaerken`, Boost seit Einführung unverändert 0.1) und setzt
   `verstaerkt_am := erstellt_am` — der Verfallsanker war von den
   Zufalls-Reinforcements auf „frisch" gezogen. Löscht zugleich alle
   `lzg_kanten` (1378 Stand 12.7.).
6. **Kanten-Neuaufbau** — `--target kanten_rebuild` (✅ gebaut Chat 107,
   NICHT in "all"). ⚠ **Reihenfolge zwingend, kein Stil:**
   `kanten_staerke_berechnen` liest `gewicht_absolut` — ein Aufbau VOR dem
   Reset würde die Zufallsgewichte in die Kantenstärken einfrieren (der
   Zufall wanderte aus den Knoten in die Kanten, wo ihn niemand mehr sucht).
   Also: **Re-Embedding → Reset → Rebuild.** Chronologisch über
   `kzg_erstellt_am` mit den echten Bausteinen (`kandidaten_mit_cosine_laden`
   + Trigger 1). Der bloße Cosine-Refresh (`--target kanten`) bleibt für
   Refresh-OHNE-Reset-Szenarien erhalten, wird in Phase B aber durch den
   Rebuild ersetzt.
7. **Server-Container NEU ERZEUGEN** (`docker compose up -d`, kein blosser
   Restart) → löst nebenbei den `_strategie_embeddings_cache`

### Phase 4 — Abnahme
- Live-Turn: Anker-Retrieval liefert Treffer? Spreading feuert?
- `sim(Matcha, Kakao) < sim(Matcha, Paraphrase)` im Live-System
- Gravitation feuert wieder (war unter v1 immer an, wird jetzt selektiv)
- Wachposten: KZG-Kontext nicht leer, Magnete lösen auf

---

> **Hinweis zur Aufteilung (19.09.2026):** §6 *Offene Punkte / Landminen* steht in [`novaberg-embedding-casing-blind_e.md`](novaberg-embedding-casing-blind_e.md), Abschnitt C.
