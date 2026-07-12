# Novaberg — Pixie-Agent: CharakterAgent (Hash-Destillation)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** CharakterAgent — Charakter-Hash aus KZG/LZG destillieren
**Stand:** 12. Juli 2026, Chat 107 (⚠ Fundament-Warnung nach Gewichts-Reset, siehe Kasten in §3. Kern: Chat 79, P7-Update Chat 103)
**Pfad:** novaberg/docs/novaberg-pixie-character-hash.md
**Quellen:** nova-05-m-a.md, nova-04-m-b.md, nova-04-t-b.md

---

## 1. Aufgabe

Der CharakterAgent destilliert Novas verdichtetes Bild ihres Gegenübers — und von sich selbst. Fünf automatisch destillierte Profile fassen zusammen, wer der Mensch ist, was ihn gerade beschäftigt, wie er kommuniziert, was er fühlt und wie die Beziehung zu Nova steht. Der Hash wächst aus der Interaktion — geformt durch das, was im Langzeitgedächtnis überlebt hat.

**Prinzip:** Der Nutzer prägt den Assistenten durch Gespräche, nicht durch Einstellungen.

**Dateien:** `agents/charakter/agent.py`, `destillation.py`, `AGENT.md`

---

## 2. Scheduling

| Aspekt | Detail |
|--------|--------|
| **Priorität** | `PIXIE_CHARAKTER_PRIORITAET = 0.3` (`config.py`) |
| **Intervall** | `PIXIE_CHARAKTER_INTERVALL_SEKUNDEN = 600` = 10 Minuten (`config.py`) |
| **Bedingung** | NUR bei `hash_dirty:{user_id}` = "1" |
| **LLM-Call** | 5 CPU-Calls pro User (einer pro Profil) |
| **LZG-Limit** | `PIXIE_CHARAKTER_LZG_LIMIT = 50` (max. LZG-Einträge pro Destillation, `config.py`) |
| **KZG-Limit** | `PIXIE_CHARAKTER_KZG_LIMIT = 20` (max. KZG-Einträge für Adaptiv, `config.py`) |
| **context_user** | Iteriert intern über `meister` + `nova` |

Kein dirty Flag → sofort return. Fehlerbehandlung pro Profil (try/except).

---

## 3. Fünf Profile

> **⚠ Fundament-Warnung (Chat 107, 12.07.2026):** Bis zum Gewichts-Reset am 12.07.2026 rechnete die Destillation auf **Zufallsgewichten** — im casing-blinden Embedding-Raum hatten 2910 Skelett-Kollisionen die `gewicht_absolut`-Ordnung bedeutungslos gemacht (EMBEDDING-CASING-BLIND; „Der Nutzer heißt Claus" stand bei 61, „Der Nutzer beobachtet dich" bei 44). Der bestehende `charakter_hash` — insbesondere `kern_hash` und `emotions_profil` — ist auf diesem Fundament entstanden und muss neu destilliert werden. **Der Reset stößt das nicht automatisch an:** Die Destillation läuft nur bei `hash_dirty`, und die Reset-/Re-Embed-Tools setzen das Flag nicht — offener Punkt CHARHASH-RESET-TRIGGER-FEHLT (bugs.md).

### 3.1 Kern-Hash (LZG, Monate)

**Frage:** Wer ist dieser Mensch?
**Quelle:** Langzeitgedächtnis (`lzg_knoten`, PostgreSQL), selektiert und gewichtet nach Anker-Stärke `gewicht_absolut` (nicht nach Präsenz/Decay). Seit Synapsen P7 (Chat 103). Der Kern beschreibt, wer jemand *dauerhaft* ist — die stärkste Verankerung, nicht die momentane Präsenz.
**Stabilität:** Verändert sich langsam.

**Beispiel:**
> "Der Nutzer ist ein analytischer Denker, der komplexe Themen ganzheitlich betrachtet und dabei intuitiv von der Sachebene zur emotionalen Bedeutung wechselt. Ihm ist Wohlbefinden und Qualität wichtiger als reine Effizienz. Er kommuniziert direkt, schätzt fundierte Zwischenbestätigungen und hat ein starkes Interesse an der Schnittstelle von Technologie und menschlichem Erleben."

### 3.2 Adaptiv-Hash (KZG, Tage)

**Frage:** Was beschäftigt ihn gerade?
**Quelle:** Kurzzeitgedächtnis (Redis).
**Stabilität:** Wechselt mit Themen.

**Beispiel:**
> "Quantencomputing, Beziehung zu Nova, Abnehmen, Eis essen."

### 3.3 Intentions-Profil (Kommunikation)

**Frage:** Wie kommuniziert er?
**Quelle:** Aggregiert aus Session-Annotationen (Intentionen + Modus + Stil).
**Drei Dimensionen:** Was will er typischerweise (Intentionen)? In welchem Register denkt er (Gesprächsmodus)? Wie drückt er sich aus (Sprachstil)?

**Beispiel:**
> "Der Nutzer kommuniziert sachlich-strukturiert mit vollständigen Sätzen und korrekter Zeichensetzung. Er bevorzugt Fachgespräche und philosophischen Austausch, stellt tiefe Fragen und erwartet fundierte Antworten."

### 3.4 Emotions-Profil (Grundtendenz + Volatilität)

**Frage:** Was fühlt er typischerweise?
**Zwei Dimensionen:** Grundtendenz (dominante Emotionen über Monate) und Volatilität (wie sprunghaft ist er?).

**Beispiel (stabil):**
> "Grundlegend zuversichtlich-neugierig mit Begeisterungs-Peaks. Emotional stabil — bei Belastung baut sich Frustration langsam auf statt zu explodieren."

**Beispiel (volatil):**
> "Emotional lebhaft mit häufigen Richtungswechseln. Schnelle Umschwünge zwischen Begeisterung und Frustration. Braucht bei Absturz schnelle Anerkennung."

### 3.5 Beziehungs-Profil (Vertrauensniveau, Dynamik)

**Frage:** Wie steht er zu Nova?
**Quelle:** Aggregiert aus Beziehungsdynamik-Annotationen.
**Wichtig:** Stil ist nicht Beziehung. "Formell" ist Kommunikation, nicht Distanz.

**Beispiel:**
> "Vertrauensvoll, fast freundschaftlich, warmherzig, humorvoll."

---

## 4. Destillation

5 LLM-Calls auf dem CPU-Modell, einer pro Profil. `hash_dirty:{user_id}` wird für beide User geprüft.

```
hash_dirty = TRUE in Redis?
    │
    Ja → lzg_knoten laden (aktiv = TRUE, sortiert nach gewicht_absolut DESC)
    │    KZG-Einträge laden (für Adaptiv-Hash)
    │
    ▼
    5 LLM-Calls (CPU-Modell) → 5 Profile generieren
    │
    ▼
    charakter_hash-Tabelle aktualisieren (INSERT oder UPDATE)
    │
    ▼
    hash_dirty = FALSE
```

Jedes Profil ist komprimierter Fließtext (2–5 Sätze). Keine Listen, keine Stichworte — natürlichsprachliche Beschreibungen, die direkt in den Responder-Prompt einfließen.

**Getrennte Prompts (seit Chat 45):** Die Destillation verwendet fuer user_id="nova" eigene Prompt-Texte. Alle vier Nova-Prompts haben die gleiche Qualitaetsstruktur wie die User-Prompts — identische Fokus-Dimensionen, Beispiele und Anleitungen, nur mit Nova-Rahmung ("Nova ist..." statt "Der Nutzer ist..."):

- `KERN_HASH_PROMPT_NOVA`: Fokus auf Tiefenwerte, dauerhafte Interessen, Denkweise
- `ADAPTIVE_HASH_PROMPT_NOVA`: Zeitgewichtung [AKUT/PHASE/TREND], Fokus auf aktuelle Themen
- `INTENTIONS_PROFIL_PROMPT_NOVA`: Drei Aspekte (STIL/MODUS/INTENTIONEN) + Beispiel
- `BEZIEHUNGS_PROFIL_PROMPT_NOVA`: Vier Dimensionen (Naehe/Hierarchie/Vertrauen/Ton)

Die User-Destillation (meister) bleibt unveraendert.

**Gewichtung:** Hohe Anker-Stärken (`gewicht_absolut`) dominieren das Profil — was sich als dauerhaft prägend verankert hat, nicht was gerade präsent ist. `aktiv = TRUE` bleibt als Gate: inaktive (decay-deaktivierte) Knoten werden nicht geladen. Präsenz gated, Anker-Stärke ranked. Angezeigtes Gewicht im Kern-/Emotions-Prompt ist `gewicht_absolut` direkt (kein Read-Time-Decay mehr; `effektives_gewicht_berechnen` an diesen Stellen entfernt).

---

## 5. Profil-Pipeline

Die Profile entstehen durch eine mehrstufige Pipeline:

```
Erfassung (Perzeption)
  → intent, tone, emotion, arousal, sprach_stil, beziehungs_dynamik
    │
    ▼
Speicherung (Session → KZG → LZG)
  → 9 Felder pro Turn annotiert, über Salienz ins KZG, über Promotion ins LZG
    │
    ▼
Destillation (Pixie CharakterAgent)
  → 5 Profile aus KZG/LZG-Daten destilliert
    │
    ▼
Nutzung (Enricher → Responder)
  → Hash in System-Prompt injiziert
```

---

## 6. Beide User

Der CharakterAgent iteriert intern über `meister` und `nova`:

| | User (Meister) | Nova |
|---|----------------|------|
| Kern-Hash | Wer ist der Mensch? | Wer ist Nova geworden? |
| Adaptiv-Hash | Was beschäftigt ihn? | Was hat Pixie zuletzt erforscht? |
| Quelle KZG | `kzg:meister:*` | `kzg:nova:*` |
| Quelle LZG | `langzeitgedaechtnis` (user_id=meister) | `langzeitgedaechtnis` (user_id=nova) |

Nova bildet durch ihre eigene KZG-LZG-Pipeline und die Hash-Destillation ein eigenes Selbstbild. Gleicher Mechanismus, getrennte Daten.

### Paar-Schema seit Chat 79

Seit Chat 79 iteriert der CharakterAgent nur noch das kanonische Paar
(user_id, ASSISTANT_USER_ID). Die Perspektiv-Unterscheidung laeuft ueber
das `beobachter`-Feld in `_kzg_laden()`:

- User-Profil: beobachter="user" (Meisters Beitraege)
- Nova-Profil: beobachter="assistant" (Novas Beobachtungen)

Die LZG-Lesepfade (_lzg_kern_laden, _lzg_intentionen_laden,
_lzg_emotionen_laden) filtern seit Chat 79 ebenfalls auf
(kanon_user_id, kanon_character_id, beobachter) statt auf subjekt_user_id
(CHAR-LZG-LEAK Fix).

---

## 7. DB-Schema

Tabelle: `charakter_hash`

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| `user_id` | TEXT | PRIMARY KEY — `meister` oder `nova` |
| `kern_hash` | TEXT | Grundpersönlichkeit (aus LZG) |
| `adaptive_hash` | TEXT | Aktuelle Phase (aus KZG) |
| `kern_aktualisiert_am` | TIMESTAMPTZ | Letzte Kern-Destillation |
| `adaptive_aktualisiert_am` | TIMESTAMPTZ | Letzte Adaptiv-Destillation |
| `intentions_profil` | TEXT | Kommunikationsmuster (aggregiert) |
| `emotions_profil` | TEXT | Emotionale Grundtendenz (aggregiert) |
| `beziehungsprofil` | TEXT | Beziehungsdynamik (aggregiert) |

Kein Auto-Increment — eine Zeile pro User. Der Hash wird nicht versioniert, sondern überschrieben. Die Historie lebt im LZG, nicht im Hash.

---

## 8. Nutzung

### Enricher

Lädt den Hash in zwei Formaten:
- Als String (`charakter_hash_retrieve`) → fließt in den `memory_context`
- Als Dict (`charakter_hash_retrieve_dict`) → fünf Felder: `kern`, `adaptiv`, `beziehungsprofil`, `intentions_profil`, `emotions_profil` (erweitert in Chat 45 und Chat 52)

### Responder — User-Hash

User-Profil wird über `[GEDAECHTNIS]` als `[Charakter]`-Eintrag in den System-Prompt injiziert. Kein eigener `[CHARAKTER]`-Block mehr (seit Chat 45, RESP-CHAR1).

### Responder — Nova-Hash

Der Enricher lädt Novas eigenen Hash. Der Responder injiziert fünf Profile direkt in `[IDENTITAET]`:

```
Schichten in [IDENTITAET] (Primacy-Reihenfolge):
1. "Du bist Nova." (Fundament)
2. Charakter-Anweisung (Saatgut, vom User)
3. "Deine gewachsene Persoenlichkeit:" + nova_kern
4. "Was dich gerade beschaeftigt:" + nova_adaptiv
5. "Deine emotionale Grundstimmung:" + nova_emotions (seit Chat 52)
6. "Deine Art zu kommunizieren:" + nova_intentionen
7. "So siehst du deinen Nutzer:" + nova_beziehung
8. Datum + Rollenklarheit + Web-Zugriff (Recency)
```

Alles Nova-bezogene in einem Block. Der separate `[CHARAKTER]`-Block wurde entfernt — er vermischte Nova-Selbstbild mit User-Beschreibung und verwendete widersprüchliche Labels.

---

Verwandte Dokumente:
- DecayAgent (Ebbinghaus-Gewichtung): `novaberg-pixie-decay.md`
- PromotionAgent (hash_dirty-Setter): `novaberg-pixie-promotion.md`
- KZG-Agent (Datenquelle Adaptiv): `novaberg-pixie-kzg.md`
- Pixie-Agenten-Übersicht: `novaberg-pixie.md`
