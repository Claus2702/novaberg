# Nova — Gedächtnis: Session

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Modul Session-Gedächtnis
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/nova-mem-session.md
**Quellen:** nova-02-m-a.md
**Datei:** `memory/session.py`

---

## 1. Aufgabe

Das Session-Gedächtnis ist Novas Arbeitsgedächtnis für das laufende Gespräch. Es speichert jeden Turn (User + Assistent), reichert User-Turns nachträglich mit Salienz-Metadaten an und fasst ältere Turns zusammen, wenn der Stapel zu groß wird. Es lebt in Redis mit TTL — nach 2 Stunden Inaktivität verschwindet es.

> **Kognitionswissenschaftliche Analogie:** Das Arbeitsgedächtnis nach Baddeley (1974) hat eine begrenzte Kapazität und hält Informationen nur aktiv, solange sie gebraucht werden. Novas Session ist das Äquivalent: Begrenzt auf die letzten ~20 Turns, mit einer „phonologischen Schleife" (Summary) für ältere Inhalte.

---

## 2. Speicherung in Redis

### 2.1 Schlüssel

| Key | Typ | TTL | Beschreibung |
|-----|-----|-----|-------------|
| `session:{user_id}:turns` | List | 7200s (2h) | Geordnete Liste aller Turns |
| `session:{user_id}:summary` | String | 7200s (2h) | Zusammenfassung älterer Turns |

### 2.2 Turn-Format

Jeder Turn ist ein JSON-Objekt in der Redis-Liste:

```json
{
    "rolle": "user|assistant",
    "inhalt": "Der Wortlaut des Turns",
    "zeit": 1711234567.89,
    "intentionen": ["information_teilen", "emotionaler_ausdruck"],
    "emotion": "begeisterung",
    "modus": "alltag",
    "kern": "Destillierte Zusammenfassung des Inhalts",
    "arousal": 0.7,
    "emotions_vektor": "plateau",
    "sprach_stil": "locker",
    "beziehungs_dynamik": "vertrauen",
    "tone": "empathisch",
    "aktion_erledigt": true,
    "aktion_erfolgreich": true
}
```

**Drei Zustände eines User-Turns:**
1. **Frisch gespeichert:** `intentionen`, `emotion`, `modus`, `kern` sind leer — die Salienz hat noch nicht annotiert.
2. **Annotiert:** Die Salienz hat den Turn nachträglich angereichert (`session_turn_annotate`). Der Enricher sieht dann den destillierten `kern` statt des rohen `inhalt`.
3. **Aktions-markiert (Chat 43):** Nach Agent-Dispatch via `session_turn_mark_action`. Felder `aktion_erledigt` + `aktion_erfolgreich` gesetzt.

---

## 3. Kernfunktionen

### 3.1 session_turn_store

Speichert einen Turn (User oder Assistent) am Ende der Liste. Setzt die TTL bei jedem Schreibvorgang zurück — solange gesprochen wird, lebt die Session.

Optional mit Metadaten (Intentionen, Emotion, Modus, Kern) — wird aber typischerweise erst nachträglich via `session_turn_annotate` befüllt.

### 3.2 session_turn_annotate

Sucht den letzten User-Turn ohne `kern`-Annotation (von hinten nach vorne) und reichert ihn an. Wird von der Salienz nach der Analyse aufgerufen.

**Warum nachträglich?** Die Salienz läuft nach dem Responder — erst dann ist die Analyse des User-Turns abgeschlossen. Der Turn wird beim Eingang gespeichert (für den Responder als Kontext), aber erst nach der Salienz-Analyse vollständig annotiert.

**Felder:** `intentionen`, `emotion`, `modus`, `kern`, `arousal`, `emotions_vektor`, `sprach_stil`, `beziehungs_dynamik`, `tone` — alles aus dem Salienz-Ergebnis des Segments mit der höchsten Salienz. Die letzten vier Felder werden nicht von der Salienz selbst berechnet, sondern aus dem State durchgereicht (Enricher/Perzeption → State → Salienz → Session).

### 3.3 session_summarize_if_needed

Wenn die Turn-Liste über `SESSION_SUMMARIZE_AT` (25) Turns wächst, werden die ältesten 10 Turns zusammengefasst:

1. Älteste 10 Turns aus der Liste lesen
2. Bisherige Summary laden (falls vorhanden)
3. LLM-Call: „Fasse zusammen, behalte Namen, Fakten, Orte, Zahlen bei"
4. Neue Summary speichern, alte 10 Turns entfernen (`ltrim`)

**Fallback:** Bei LLM-Fehler wird auf `SESSION_MAX_TURNS` (20) getrimmt — lieber Turns verlieren als die Session aufblähen.

### 3.4 session_turns_retrieve

Gibt alle Turns der aktuellen Session als Liste von Dicts zurück. Wird vom Enricher verwendet, um den Gesprächskontext zu laden.

### 3.5 session_reset

Löscht alle Session-Daten eines Users: Turns, Summary, Stack, Pending.

### 3.6 session_turn_mark_action (Chat 43)

Markiert den letzten User-Turn mit dem Ergebnis einer Agent-Aktion. Wird nach dem Agent-Dispatch aufgerufen, analog zu `session_turn_annotate`.

Zwei Flags:
- `aktion_erledigt`: Agent hat Verarbeitung abgeschlossen (true bei `abgeschlossen` und `fehler`)
- `aktion_erfolgreich`: Aktion wurde umgesetzt (true nur bei `abgeschlossen`)

Nicht aufgerufen bei Rückfragen (`status=rueckfrage`) — der Turn ist noch offen.

### 3.7 Turn-Marker in format_session_turns_numbered (Chat 43)

Turns mit `aktion_erledigt=true` bekommen einen Marker im Header:
- `aktion_erfolgreich=true`: `[ERLEDIGT]`
- `aktion_erfolgreich=false`: `[FEHLGESCHLAGEN]`

Format: `[3] USER (neutral, a=0.3) [ERLEDIGT]: Lösch die Einkaufsliste`

Der Marker verhindert, dass Classify-Nodes erledigte Anweisungen als aktive Aufträge interpretieren (KONTEXT1).

---

## 4. Konstanten

| Konstante | Wert | Beschreibung |
|-----------|------|-------------|
| `SESSION_MAX_TURNS` | 20 | Maximale Turns bei Fallback-Trimming |
| `SESSION_TTL` | 7200 (2h) | Inaktivitäts-Timeout |
| `SESSION_SUMMARIZE_AT` | 25 | Ab diesem Füllstand wird zusammengefasst |

---

## 5. Zusammenspiel mit anderen Nodes

| Node | Interaktion |
|------|-------------|
| **API-Layer** (`api/chat.py`) | Speichert User- und Assistenten-Turns via `session_turn_store` |
| **Enricher** | Liest Turns via `session_turns_retrieve`, destilliert sie, blendet Shadow-Impulse aus |
| **Salienz** | Annotiert den letzten User-Turn via `session_turn_annotate` |
| **API-Layer** (`api/chat.py`) | Markiert User-Turns nach Agent-Dispatch via `session_turn_mark_action` |
| **Responder** | Sieht die destillierten Turns (über den Enricher, nicht direkt) |

---

## 6. Designentscheidungen

**Kein LLM-Call im Normalbetrieb:** Die Session speichert und liest — reine Redis-Operationen. Nur die Zusammenfassung (`session_summarize_if_needed`) braucht einen LLM-Call, und die wird nur bei langen Gesprächen (> 25 Turns) getriggert.

**TTL statt explizites Löschen:** Die Session verfällt automatisch nach 2 Stunden Inaktivität. Das ist bewusst: Ein neues Gespräch am nächsten Tag soll nicht von den Turns des Vortags kontaminiert werden. Das KZG und LZG halten die wichtigen Inhalte — die Session ist nur für den aktuellen Dialog.

**Annotation nachträglich, nicht beim Speichern:** Der Turn muss gespeichert werden bevor die Salienz analysiert, weil der Responder den Turn als Kontext braucht. Die Salienz läuft aber erst nach dem Responder. Deshalb: Speichern → Responder sieht den Turn → Salienz analysiert → `annotate` reichert nach → beim nächsten Turn sieht der Enricher die Annotation.

---

→ Enricher (nutzt Session): nova-node-enricher.md
→ Salienz (annotiert Turns): nova-node-salience.md
→ Gedächtnis-Konzept: nova-memory.md
