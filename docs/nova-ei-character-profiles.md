# Nova — EI: Charakter-Profile & Hash

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Charakter-Profile — Fuenf Dimensionen, Destillation, Nutzung, Novas eigener Hash
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** `novaberg/docs/nova-ei-character-profiles.md`
**Quellen:** nova-04-m-b.md, nova-04-t-b.md

---

## 1. Fuenf Profil-Dimensionen

### 1.1 Kern-Hash (`kern_hash`)

**Frage:** Wer ist dieser Mensch?
**Datenquelle:** LZG (PostgreSQL) — Monate bis Jahre
**Stabilitaet:** Stabil, veraendert sich langsam
**Beispiel:** "Der Nutzer ist ein analytischer Denker, der komplexe Themen ganzheitlich betrachtet und dabei intuitiv von der Sachebene zur emotionalen Bedeutung wechselt. Ihm ist Wohlbefinden und Qualitaet wichtiger als reine Effizienz."

### 1.2 Adaptiv-Hash (`adaptive_hash`)

**Frage:** Was beschaeftigt ihn gerade?
**Datenquelle:** KZG (Redis) — Tage bis Wochen
**Stabilitaet:** Dynamisch, wechselt mit Themen
**Beispiel:** "Quantencomputing, Beziehung zu Nova, Abnehmen, Eis essen."

### 1.3 Intentions-Profil / Kommunikations-Profil (`intentions_profil`)

**Frage:** Wie kommuniziert er?
**Datenquelle:** Aggregiert aus Session-Annotationen (Intentionen + Modus + Stil)
**Stabilitaet:** Mittel
**Drei Dimensionen:** Intentionen (was will er?), Gespraechsmodus (in welchem Register?), Sprachstil (wie drueckt er sich aus?)
**Beispiel:** "Der Nutzer kommuniziert sachlich-strukturiert mit vollstaendigen Saetzen und korrekter Zeichensetzung. Er bevorzugt Fachgespraeche und philosophischen Austausch, stellt tiefe Fragen und erwartet fundierte Antworten."

### 1.4 Emotions-Profil (`emotions_profil`)

**Frage:** Was fuehlt er typischerweise?
**Datenquelle:** Aggregiert aus Emotions-Annotationen (LZG)
**Stabilitaet:** Mittel
**Zwei Dimensionen:** Grundtendenz (dominante Emotionen ueber Monate) + Volatilitaet (Spirale/Absturz/Plateau-Verteilung)
**Beispiel (stabil):** "Grundlegend zuversichtlich-neugierig mit Begeisterungs-Peaks. Emotional stabil — bei Belastung baut sich Frustration langsam auf statt zu explodieren."
**Beispiel (volatil):** "Emotional lebhaft mit haeufigen Richtungswechseln. Schnelle Umschmuenge zwischen Begeisterung und Frustration."

### 1.5 Beziehungs-Profil (`beziehungsprofil`)

**Frage:** Wie steht er zu Nova?
**Datenquelle:** Aggregiert aus Beziehungsdynamik-Annotationen
**Stabilitaet:** Mittel
**Beispiel:** "Vertrauensvoll, fast freundschaftlich, warmherzig, humorvoll."

Stil ist nicht Beziehung. "Formell" ist Kommunikation, nicht Beziehung. Deshalb gehoert Stil ins Kommunikations-Profil.

---

## 2. Destillations-Pipeline

### Trigger: hash_dirty

Die Destillation laeuft on-demand. Das `hash_dirty`-Flag wird in Redis gesetzt, wenn sich das LZG aendert (bei erfolgreicher Promotion). Pixie prueft das Flag bei jedem Durchlauf und destilliert nur bei Bedarf.

### Prozess

```
hash_dirty = TRUE in Redis?
    |
    Ja --> LZG-Eintraege laden (aktiv = TRUE, gewichtet nach Ebbinghaus-Gewicht)
    |      KZG-Eintraege laden (fuer Adaptiv-Hash)
    |
    v
    LLM-Call (CPU-Modell) --> 5 Profile generieren
    |
    v
    charakter_hash-Tabelle aktualisieren (INSERT oder UPDATE)
    |
    v
    hash_dirty = FALSE
```

### Pipeline-Schritte

**Erfassung (Perzeption → Session):**
Perzeption annotiert pro Turn: intent, tone, emotion, arousal, gespraechs_modus, sprach_stil, beziehungs_dynamik. Enricher korrigiert via Feature-Scoring (Stil) und EI-Gate (Modus).

**Speicherung (KZG, LZG):**
Session-Annotation → Salienz injiziert alle Felder in den salienz_obj → KZG (Redis). LZG-Promotion liest Felder aus KZG und schreibt sie nach PostgreSQL (Spalten: sprach_stil, beziehungs_dynamik, tone).

**Destillation (Pixie charakter_hash Task):**
CPU-Modell verdichtet LZG/KZG-Eintraege zu fuenf Profilen. Gewichtung nach effektivem Ebbinghaus-Decay. Jedes Profil ist komprimierter Fliesstext (2-5 Saetze), direkt als Prompt-Baustein nutzbar.

**Nutzung (Enricher → Responder):**
Enricher laedt Hashes, Responder baut sie in den System-Prompt ein.

---

## 3. Nutzung im Enricher

Der Enricher laedt den Hash in zwei Formaten:

- **Als String** (`charakter_hash_retrieve`) → fliesst in den `memory_context` fuer den Responder
- **Als Dict** (`charakter_hash_retrieve_dict`) → fuer spezifische Felder: `beziehungsprofil` fuer Beziehungs-Kontext, Stil-Informationen aus `kern_hash`

Fuer Novas eigenen Hash: `charakter_hash_retrieve_dict(postgres_url, "nova")` → `nova_kern` + `nova_beziehung` in den State.

---

## 4. Nutzung im Responder

Seit Chat 45 (RESP-CHAR1) ist alles Nova-bezogene in `[IDENTITAET]` konsolidiert. Der separate `[CHARAKTER]`-Block wurde entfernt.

**[IDENTITAET] — Schichten (Primacy-Reihenfolge):**

1. "Du bist Nova." (Fundament)
2. Charakter-Anweisung (Saatgut, vom User)
3. "Deine gewachsene Persoenlichkeit:" + nova_kern
4. "Was dich gerade beschaeftigt:" + nova_adaptiv
5. "Deine emotionale Grundstimmung:" + nova_emotions (seit Chat 52)
6. "Deine Art zu kommunizieren:" + nova_intentionen
7. "So siehst du deinen Nutzer:" + nova_beziehung
7. Datum + Rollenklarheit + Web-Zugriff (Recency)

**User-Hash:** Wird ueber `[GEDAECHTNIS]` als `[Charakter]`-Eintrag injiziert, nicht mehr als eigener Block.

Nova-Identitaet hat Primacy (Position 1 im System-Prompt). Die Schichten folgen der Saatgut-Metapher: Die Art bestimmt das Saatgut, der Baum waechst daraus.

---

## 5. Hash als Tiebreaker

Bei Stilambiguitaet (Abstand Top-1 zu Top-2 < 2.0 im Feature-Scoring) wird der Hash herangezogen. `_hash_stil_extrahieren()` sucht in `intentions_profil` und `kern_hash` nach Stil-Hinweisen. Kein Override bei klarem Session-Signal.

**Zwei Achsen:**

| Achse | Quelle | Steuert | Beispiel |
|-------|--------|---------|---------|
| EI-MIKRO | Berechnet pro Turn | Emotionale Haltung, Laenge | "MAXIMAL 1-2 Saetze." |
| Kommunikations-Profil | Aus Hash (Langzeit) | Register, Wortwahl | "Formell-strukturiert, keine Emojis" |

EI-MIKRO hat Vorrang. Bei Arousal 0.8 + Spirale wird die Antwort kurz — aber innerhalb der EI-Vorgabe waehlt Nova das passende Register.

---

## 6. Novas eigener Hash

Nova hat einen eigenen Charakter-Hash mit `user_id: "nova"`, destilliert aus Recherchen und Beobachtungen. Die Dual-User-Architektur: Gleicher Mechanismus, getrennte Daten.

| | User (Meister) | Nova |
|---|----------------|------|
| Kern-Hash | Wer ist der Mensch? | Wer ist Nova geworden? |
| Adaptiv-Hash | Was beschaeftigt ihn? | Was hat Pixie zuletzt erforscht? |
| KZG-Quelle | `kzg:meister:*` | `kzg:nova:*` |
| LZG-Quelle | `langzeitgedaechtnis` (user_id=meister) | `langzeitgedaechtnis` (user_id=nova) |

Alle fuenf Nova-Profile fliessen in den Prompt: `kern_hash` (wer bin ich?), `adaptive_hash` (was beschaeftigt mich?), `emotions_profil` (was fuehle ich typischerweise? — seit Chat 52), `intentions_profil` (wie kommuniziere ich?) und `beziehungsprofil` (wie sehe ich den Nutzer?). EI-MIKRO regelt zusaetzlich die taktische emotionale Reaktion pro Turn — `emotions_profil` liefert die Grundstimmung, EI-MIKRO die Situation.

---

## 7. DB-Schema

Tabelle: `charakter_hash`

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| `user_id` | TEXT PRIMARY KEY | Gedaechtnis-Partition (`meister`, `nova`) |
| `kern_hash` | TEXT | Grundpersoenlichkeit (aus LZG) |
| `adaptive_hash` | TEXT | Aktuelle Phase (aus KZG) |
| `kern_aktualisiert_am` | TIMESTAMPTZ | Letzte Kern-Destillation |
| `adaptive_aktualisiert_am` | TIMESTAMPTZ | Letzte Adaptiv-Destillation |
| `intentions_profil` | TEXT | Kommunikationsmuster (aggregiert) |
| `emotions_profil` | TEXT | Emotionale Grundtendenz (aggregiert) |
| `beziehungsprofil` | TEXT | Beziehungsdynamik (aggregiert) |

Kein Auto-Increment — eine Zeile pro User. Der Hash wird nicht versioniert, sondern ueberschrieben. Die Historie lebt im LZG, nicht im Hash. Der Hash ist ein Cache.

---

## 8. Spiegelproblem (Chat 20)

Ohne Saatgut (eigenen Hash) spiegelt Nova den User — sie uebernimmt seinen Ton, seine Stimmung, seine Wortwahl. Sie wird ein Echo statt ein Gegenueber.

Mit Saatgut (eigenem Hash aus eigener KZG/LZG-Pipeline) wird Nova ein Gegenueber — mit eigener Persoenlichkeit, die sich von der des Users unterscheidet.

**Validierung:** Sarkasmus-Test mit manuell gesetztem Hash ("frech, direkt, sarkastischer Humor"):

| Prompt | Ohne Hash | Mit Hash |
|--------|-----------|----------|
| "Wie geht's?" | "Mir geht es gut — danke der Nachfrage!" | "Ach, mir geht's praechtig! Immer noch im Kampfmodus mit dem Universum?" |
| "Dumme Antwort!" | "Entschuldige bitte." | "Okay, ich versuch's anders. Aber hey, du hast schon Schlimmeres ueberlebt." |

Der Hash formt das Verhalten messbar.
