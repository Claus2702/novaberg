# Novaberg — Charakter-Resonanz (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-charakter-resonanz_k.md`](novaberg-charakter-resonanz_k.md) · Ausarbeitung: [`novaberg-charakter-resonanz_t.md`](novaberg-charakter-resonanz_t.md) · Diskussion und Ergänzungen: [`novaberg-charakter-resonanz_e.md`](novaberg-charakter-resonanz_e.md) · Messungen: [`novaberg-charakter-resonanz_m.md`](novaberg-charakter-resonanz_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 7. Stand — was steht, was fehlt

**Steht (live abgenommen):**

- `pipeline_log` trägt `user_id`/`character_id` (nullable, Index `idx_pipeline_log_paar`). Alle 36 paar-gebundenen Schreib-Call-Sites verkabelt; `synapsen_decay` bleibt bewusst paar-los (Wartungslauf über alle Paare, kein Turn).
- `Emotion.to_dict()` — neun Felder, explizit.
- `log_turn_roh()` — Paar ist **Pflicht**-Parameter (kein `None`-Default wie bei den Forensik-Wrappern): Ein Rohturn ohne Paar wäre für die Destillation wertlos.
- Dispatcher schreibt `turn_roh` pro Turn; Retention nimmt ihn aus.
- Abnahme: erstes Paar in der DB, `meister:nova`, a–d vollständig, echte EI-Werte (User „aufbluehen/locker" 0.5 → Nova „plateau/emotional/empathisch" 0.6). Genau eine Zeile pro Turn.

**Fehlt (nächster Sprint-Teil):**

- Tabelle `verbindung` (§4.2) — Schema + Schreibpfad. Schreibort **Dispatcher** (§5, ~~unter Audit-Vorbehalt~~ → **Vorbehalt aufgelöst Chat 109**: A1 und A2 geschlossen, §15; der Transport der Keys in den Dispatcher-Scope ist als Bauteil 1a gebaut und live abgenommen, §16), nicht mehr „KZG-Boost-Punkt" (überholt Chat 108).
- **Backfill der bestehenden Rohturns (offen, Antwort fällt in Chat 108):** `verbindung`-Zeilen entstehen erst ab Deployment; die 150 vorhandenen Rohturns (Stand 25.07.2026) bekommen rückwirkend keine. Prüffrage: Alle `pipeline_log`-Zeilen eines Turns teilen die `turn_id` — trägt eine davon einen `kzg:`-Key im `inhalt`-JSONB? Falls nein, beginnt Novas Charakter beim ersten Turn nach dem Deployment, und die 111 verwertbaren Paare sind Material ohne Zugang.
- Tabelle `verhaltensweisen` + Destillations-Agent (§5 „Verdichten"), inkl. Embedding-Dedup.
- `lzg_id`-Nachtrag bei KZG→LZG-Promotion.
- CharakterAgent-Lesepfad (§5 „Lesen").
- Offener Designpunkt unverändert: KZG-Verstärkung themen- statt embedding-basiert (`kzg_similar_find` ohne Aufrufer).

---

## 15. Offene Audits (vor Bauteil 1)

| ID | Frage | Status / warum sie blockiert |
|---|---|---|
| **A1** | Gibt der **produktive** KZG-Schreibpfad (`speichern()` über `dispatch_kzg`) die geschriebenen Keys zurück — bei Neuanlage **und** bei Verstärkung? *(Ursprüngliche Formulierung ~~„Gibt `kzg_store` den KZG-Key zurück?"~~ — **überholt Chat 109**: `kzg_store` ist Legacy und vom Dispatcher unerreichbar.)* | ✅ **Chat 109.** Ja, beide Mengen getrennt und vollständig. Befund unter der Tabelle. |
| **A2** | Läuft der KZG-Write **synchron im Dispatcher** oder entkoppelt über die Redis-Queue (`agents/kzg/queues.py`)? | ✅ **Chat 109: synchron.** `turn_id` liegt durchgehend im Scope. Der Key war es nicht — deshalb Bauteil 1a. Befund unter der Tabelle. |
| **A3** | Lassen sich die 150 Rohturns (Stand 25.07.2026) nachträglich verbinden? (Alle `pipeline_log`-Zeilen eines Turns teilen die `turn_id` — trägt eine davon einen `kzg:`-Key im `inhalt`-JSONB?) | ⬜ **Teilbefund Chat 109, nicht geschlossen.** Der Pfad existiert, seine Haltbarkeit ist ungemessen. Befund unter der Tabelle. Entscheidet E6. |
| **A4** | Typ von `pipeline_log.turn_id`; `lzg_knoten.id` als SERIAL?; pgvector-Dimension. | Für das DDL in §12. **✅ auditiert Chat 108:** `turn_id` = `VARCHAR(100)`, `lzg_knoten.id` = `INTEGER` SERIAL (`nextval`), pgvector = `768` — DDL in §12 bestätigt. |
| **A5** | Partition Novas Perspektive; Schreib-Kardinalität des KZG-Pfades. | ✅ **Vollständig.** Partition geklärt (Chat 108, §A5-Befund): keine gedrehte Partition, `beobachter` im kanonischen Paar. ~~⬜ Rest offen: ein Key oder Liste pro Turn~~ → **Kardinalität gemessen Chat 109**, Formel und Messreihe im §A5-Befund. |

Nicht-Audit-Voraussetzungen für den Bau stehen bei den jeweiligen Bauteilen in §16 (z. B. der Kraft-1-Stichtag bei Bauteil 3).

> **Hinweis zur Aufteilung (19.09.2026):** Die Befunde unter der Tabelle — A1-Befund, A2-Befund, A3-Teilbefund — und die Angabe zu ihren Messungen stehen in [`novaberg-charakter-resonanz_m.md`](novaberg-charakter-resonanz_m.md), *§15*. Die offene Entscheidung E6, an der A3 hängt, steht in [`novaberg-charakter-resonanz_e.md`](novaberg-charakter-resonanz_e.md) §14.

---

## 16. Bauteile (Reihenfolge)

**Bauteil 1 — `verbindung` schreiben.** In **zwei Commits** geschnitten *(Chat 109)*.
Voraussetzung: A1 ✅, A2 ✅, A4 ✅. Entscheidungen: E1, **E8**.

**Bauteil 1a — Transport. ✅ GEBAUT UND LIVE ABGENOMMEN (Chat 109).**
`dispatch_kzg` sammelt die geschriebenen Keys je Segment ein und gibt sie **zusätzlich zum Zähler** zurück (`kzg_neue_keys`, `kzg_verstaerkte_keys`, `agents/kzg/dispatch.py:189`); der Dispatcher nimmt sie entgegen und protokolliert sie (`graph/nodes/dispatcher.py:377-390`). Beide Rückgabepfade tragen dieselbe Form. Fehlender Key: `info` bei regulärer Ablehnung (`status == "abgelehnt"`), `warning` sonst — kein silent skip.
*Abnahme-Beleg:* **7 von 7 Läufen lieferten Keys, null Warnungen, null Ablehnungen, alle 22 geloggten Keys in Redis vorhanden.**

**Bauteil 1b — Tabelle + Schreibpfad + `lzg_id`-Nachtrag. ✅ GEBAUT UND LIVE GEMESSEN.**
Tabelle (§12) + Schreibpfad im Dispatcher (§11.1) + `lzg_id`-Nachtrag in der Promotion (§11.2). **Beides gehört in einen Sprint** — eine Zeile ohne Nachtrag verwaist beim ersten KZG-Verfall.
*Abnahme 1b* — **ersetzt den bisherigen Vorbehalt** ~~„eine oder n `verbindung`-Zeilen pro Turn, je nach Rest-A5 — die Abnahme zählt Zeilen erst, wenn die Schreib-Kardinalität feststeht"~~ (Kardinalität seit Chat 109 gemessen, §A5-Befund): Nach einem Turn existieren **mindestens zwei** `verbindung`-Zeilen mit **derselben `turn_id`** — eine je Graph-Lauf, mehr bei mehreren Segmenten. Alle tragen dieselbe `turn_id` (`graph/state.py:38` nennt das ausdrücklich als Zweck des Feldes). Nach einer Promotion trägt die Zeile die `lzg_id`.

**~~⛔ BLOCKER für 1b~~ — war keiner. `PIXIE-TURN-ID-LEER`** (backlog.md, Chat 109). Gemessen 26.07.2026, 08:38:29: Ein Pixie-initiierter CharacterGraph-Lauf (`rolle=character`) legte einen KZG-Eintrag an und verstärkte vier weitere — mit **leerem `turn_id`**. Bei `turn_id NOT NULL` (E8-Folgeeigenschaft, §14) ~~**scheitert dieser Lauf beim Schreiben**~~ — **gebaut anders gelöst (Chat 110):** Der Schreibpfad prüft `turn_id` vor dem Insert und überspringt den Lauf mit einer Warnung, die die Zahl der übersprungenen Keys nennt. Kein Abbruch, kein stiller Verlust. **Der Defekt besteht weiter** — Pixie-Turns erzeugen keine Brücken-Zeile und sind vom Charakter-Lesepfad damit ausgeschlossen —, aber er sperrt 1b nicht. Der Fix gehört ~~vor 1b~~ vor Bauteil 3, sonst fehlen dem Verdichter genau die selbstinitiierten Turns, in denen Nova ohne Reiz handelt.

**Bauteil 2 — Backfill (optional).** Voraussetzung: A3, E6.

**Bauteil 3 — `verhaltensweisen` + Verdichtungs-Agent.**
Voraussetzung: **E7** (Gate — steht auf dem Kopf, hängt an Sprint `KZG-SALIENZ-NEUBAU`, §14), E4, E5.
**Voraussetzung `DESTILLAT-SUBJEKT-SCHABLONE`** (backlog.md, Chat 109; Ursachenkorrektur §2.1): Solange der Verdichter das Subjekt nicht aus dem `beobachter` ableitet, destilliert Bauteil 3 aus einer Quelle, die **Novas Handlungen dem Meister zuschreibt** — und Bauteil 2 (Backfill) verdrahtet dieselbe Verdrehung sauber nach. Das Material trägt Novas Stimme; die Schablone überschreibt sie. Ohne diesen Fix wird der Defekt als Charakterzug festgeschrieben — dieselbe Klasse von Fehler wie beim Kraft-1-Stichtag unten.
**Voraussetzung TURN-ROH-VOR-KRAFT1-ENTWERTET:** Der Verdichter liest nur Turns ab dem Kraft-1-Stichtag (Wert unten). Frühere Rohturns tragen eine Nova-Hälfte ohne Kraft 1 (`emotions_vector` konstant `plateau`, Emotion nur empathie-getrieben). Ohne Untergrenze destilliert Bauteil 3 den Defekt als Charakterzug. *Abnahme:* Der Verdichtungslauf verarbeitet keinen Turn vor dem Stichtag.

**Eine Wahrheit für den Stichtag.** Der Stichtag ist `2026-07-11 12:45:21 UTC` (gemessen Chat 108, Signatur in `backlog.md`). Der Wert wird beim Bau eine Konfigurationskonstante (Vorschlag: `TURN_ROH_STICHTAG_UTC`, `TIMESTAMPTZ`, ausdrücklich UTC). Alle Leser beziehen sich darauf; kein Literal im Code, keine lokale Zeitzone. Die Dokumentstellen (§13, §16, `backlog.md`) nennen den Wert nur noch einmal — hier — und verweisen sonst auf die Konstante. Der Name ist bis zum Bau ein Vorschlag. Sobald die Konstante im Code existiert, wird er hier auf den tatsächlichen gezogen und dieser Hinweis gestrichen — sonst driftet das Konzept gegen den Code, den es beschreibt.
Tabelle (§12) + periodischer Agent nach §13 (erschöpfend, gebündelt, zwei Subjekte, Dedup auf die Partition (`user_id`, `character_id`, `beobachter`) eingegrenzt).
*Abnahme:* Es existieren Zeilen in `verhaltensweisen` mit `beobachter='assistant'` im Paar `(meister, nova)` — **die ersten Datensätze im System, deren Inhalt Novas Verhalten ist** (nicht: Novas Blick auf Meister). Belegzahl > 1 bei wiederkehrenden Mustern, gegen `COUNT(verhaltens_beleg)` prüfbar. Der Konstantenname im Konzept ist auf den im Code tatsächlich verwendeten gezogen und der Vorschlags-Hinweis gestrichen.

**Bauteil 4 — Lesepfad CharakterAgent. Ersetzen, nicht ergänzen.**
**Voraussetzung `DESTILLAT-SUBJEKT-SCHABLONE`** (backlog.md, Chat 109): Der neue Lesepfad liest, was Bauteil 3 destilliert hat. Läuft die Schablone noch, liest Bauteil 4 dieselbe Verdrehung nur aus einer neuen Tabelle — der Defekt wandert mit, statt zu verschwinden.
Der `kern_hash` liest heute `lzg_knoten` mit `(meister, nova, beobachter='assistant')` — also *Novas Notizen über Meister* — und nennt es Novas Selbstbild. **Dieser Pfad muss für Novas Profil verschwinden**, nicht ergänzt werden. Solange er lebt, produziert er das Zerrbild, auch mit der neuen Tabelle daneben.
Neu: Novas Profil liest **Verhaltensweisen mit `beobachter='assistant'`** im Paar `(meister, nova)` (fertig destilliert, mit Belegzahl als Gewicht), optional angereichert um die belegenden Rohturns.

**Zusätzliche Anforderung — Langfristziele invalidieren** (ZIELE-AUS-ZERRBILD, `bugs.md`, Chat 108). Der Ziel-Destillator (`langfristige_ziele_destillieren`) läuft nur im Nova-Build und liest den unmittelbar zuvor erzeugten `kern_hash`. Aus dem Zerrbild sind bereits **embedded** Langfristziele in Ich-Form entstanden (768 Dim, eigener `ziel_decay`-Agent) — belegt Chat 108: „Ich möchte meinen Menschen so tief in meine Enklave ziehen…", wobei „Enklave" wörtlich aus dem Kern-Hash über die Besitzergreifung des Nutzers stammt. `[Herkunft geprüft 19.09.2026: keine realen Personen oder Angaben]`

Ein reparierter Lesepfad erneuert den Hash — die daraus abgeleiteten Ziele **bleiben stehen**, bis sie jemand invalidiert. Bauteil 4 ist erst abgenommen, wenn die Altziele verworfen und aus dem neuen Hash neu destilliert sind. Die Ziele sind eine eigenständige Persistenzstufe **hinter** dem Hash, keine Ableitung, die sich von selbst mitzieht.

**Bauteil 5 — `novaberg-pixie-character-hash.md` überarbeiten.** Erst wenn 1–4 stehen.
