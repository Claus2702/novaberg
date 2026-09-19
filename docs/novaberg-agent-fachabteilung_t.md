# Novaberg — Konzept: Fachabteilungs-Agenten (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-agent-fachabteilung_k.md`](novaberg-agent-fachabteilung_k.md) · Bauplan und Umstellung: [`novaberg-agent-fachabteilung_b.md`](novaberg-agent-fachabteilung_b.md) · Diskussion und Ergänzungen: [`novaberg-agent-fachabteilung_e.md`](novaberg-agent-fachabteilung_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 3. Das neue Konzept — Fachabteilungs-Pipeline

### 3.1 Erweiterte Pipeline

```
Validate --> Classify --> Semantik-Check --> HITL-Gate --> CRUD --> Output-Validation --> Antwort
```

Zwei neue Nodes kommen hinzu:

- **Semantik-Check** (vor HITL-Gate): Prüft die geplante Operation gegen den aktuellen Datenbestand auf Kohärenz, Widerspruch, Ergänzung oder Redundanz.
- **Output-Validation** (nach CRUD): Prüft das tatsächlich gespeicherte Ergebnis auf semantischen Sinn.

### 3.2 Semantik-Check — der Input-Prüfer

**Input:**
- Aktuelle aktive Datensätze (aus dem Fachgebiet des Agenten)
- Geplante Operation (Aktion + neue/geänderte Daten)

**Verarbeitung:** Ein LLM-Call mit klarem Prompt: "Ist diese Operation kohärent? Widerspricht sie dem Bestand? Ergänzt sie? Ist sie redundant?"

**Output (strukturiertes JSON):**
```json
{
  "kompatibilitaet": "widerspruch" | "ergaenzung" | "redundanz" | "identisch" | "passt",
  "begruendung": "Kurze Erklärung",
  "empfehlung": "fortsetzen" | "deaktiviere_aktuelle" | "zusammenfuehren" | "ablehnen",
  "rueckfrage_fuer_user": "Optional: differenzierte Rückfrage statt Standard-Ja/Nein"
}
```

**Pfade:**
- `passt` → normaler HITL-Gate mit Standard-Rückfrage ("Soll ich das ausführen?")
- `widerspruch` → erweiterte Rückfrage ("Das passt nicht zu X. Soll ich X deaktivieren?")
- `ergaenzung` → Information ("Ich bin dann X und Y. OK?")
- `redundanz` → Konsolidierungs-Rückfrage ("Das habe ich im Kern schon. Zusammenführen?")
- `identisch` → Ablehnung ohne HITL-Gate ("Das habe ich bereits, nichts zu tun.")

### 3.3 Output-Validation — der Ergebnis-Prüfer

**Input:**
- Das neu gespeicherte Datum (nach CRUD)
- Der ursprüngliche User-Intent

**Verarbeitung:** LLM-Prüfung: "Ergibt das Ergebnis semantisch Sinn im Kontext? Ist es eine sinnvolle Darstellung des User-Intents?"

**Output:**
- `valide` → weiter zur Antwort
- `unsinnig` → Rollback-Signal (die CRUD-Operation wird zurückgenommen, und der User erhält eine erklärende Rückfrage)

Beispiel: Bei einem Update mit subtraktivem Intent produziert der Classify "Nicht mehr das kleine Mädchen sein". Die Output-Validation erkennt: Das ist keine Charakter-Beschreibung, das ist eine Verneinung ohne Basis. → Rollback, zurück an den User: "Ich verstehe, du möchtest das 'kleine Mädchen' aus dem Charakter entfernen. Die aktuelle Beschreibung ist X. Soll der neue Charakter Y sein (X ohne kleines Mädchen)?"

### 3.4 Differenzierte HITL-Gate-Rückfragen

Aktuell ist das HITL-Gate eine Ja/Nein-Frage ("Soll ich das ausführen?"). Mit Fachabteilungs-Semantik werden die Rückfragen kontextspezifisch:

| Situation | Standard-Rückfrage | Neue Rückfrage |
|-----------|-------------------|----------------|
| Create passt | "Soll ich das ausführen?" | "Soll ich das anlegen?" |
| Create widerspricht | "Soll ich das ausführen?" | "Das widerspricht X. Soll ich X deaktivieren?" |
| Update additiv | "Soll ich das ausführen?" | "Ich füge das hinzu und bin dann X und Y. OK?" |
| Update subtraktiv | "Soll ich das ausführen?" | "Aus X wird dann Y. Passt das?" |
| Delete | "Soll ich das ausführen?" | "X entfernen — bist du sicher?" |
| Reactivate + Konflikt | "Soll ich das ausführen?" | "X reaktivieren und aktuellen Y deaktivieren?" |
| Redundanz | — (aktuell nichts) | "Das habe ich im Kern schon. Zusammenführen?" |

Jede Rückfrage-Art braucht ihren eigenen Resume-Pfad. Das hängt direkt mit dem RESUME-REJECT-Fix zusammen — wenn wir den reparieren, bauen wir gleich die Architektur für differenzierte Rückfrage-Typen mit ein.

---
