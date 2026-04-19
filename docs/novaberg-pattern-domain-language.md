# Novaberg — Pattern: Domain-Language-Normalisierung

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Pattern — Normalisierung von User-Input durch agenten-spezifische Fachsprache
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** `novaberg/docs/novaberg-pattern-domain-language.md`
**Quellen:** nova-15-k.md (allgemeine Abschnitte)

---

## 1. Problem

Novas interne Verarbeitungskette arbeitet auf Rohdaten — dem unveraenderten User-Prompt. Slang, Emotion und Absicht muessen von jedem Node eigenstaendig interpretiert werden:

- CRUD bekommt mehrdeutige Anweisungen und muss raten
- Verb-Mappings fangen Dialekt ab, aber nicht Kontextabhaengigkeit
- LLM-Klassifikation kann durch emotionale Sprache beeinflusst werden
- Verifikation prueft gegen einen Zustand, den sie nur aus dem Rohtext ableiten kann

**Industrielle Analogie:** Produktionsdaten von externen Lieferanten im Rohformat. Wenn diese ungeprueft in die Produktion fliessen, entstehen unerwartete Fehler. Loesung: Eingangspruefung, Normalisierung, Validierung — erst dann Produktion.

---

## 2. Leitprinzip

> **Rohdaten vollstaendig erhalten, intern nur auf validierten Daten arbeiten.**

| Prinzip | Etabliert | Aussage |
|---------|-----------|---------|
| Daten vollstaendig transportieren | Chat 30 | Keine Middleware darf Daten reduzieren |
| Weniger Input > staerkerer Prompt | Chat 23 | Halluzinationen durch Kontextreduktion loesen |
| **Rohdaten erhalten, validiert verarbeiten** | **Chat 43** | **Interne Prozesse arbeiten auf normalisierter Fachsprache** |

Kein Widerspruch: Die Rohdaten (Emotion, Energie, Slang, Originaltext) bleiben vollstaendig im State fuer den Responder. Aber die Verarbeitungskette (CRUD, Verifikation) arbeitet auf bereinigter, fachsprachlicher Repraesentation.

---

## 3. Zwei Schichten im State

| Schicht | Inhalt | Konsumenten |
|---------|--------|-------------|
| **Rohdaten** | `user_prompt`, Emotion, Arousal, Energie, Slang, Session-Turns | Responder, Salienz, EI, Gespraechsvektor |
| **Validierte Daten** | `normalisiert`, action, target, Domain Language | CRUD, Verifikation, Verb-Mappings, Logging |

Die Trennung ist strikt: Kein CRUD-Code liest `user_prompt` direkt. Kein Responder-Code liest `normalisiert` fuer die Antwortgenerierung.

---

## 4. Architektur — Normalisierung im Classify-Node

### Warum der Classify-Node?

Der Classify-Node macht bereits einen GPU-LLM-Call fuer die Aktionsklassifikation. Die Normalisierung ist ein zusaetzliches Output-Feld — kein Extra-Call, keine zusaetzliche Latenz.

| Alternative | Problem |
|-------------|---------|
| Eigener Node vor dem Router | Extra-LLM-Call auf jedem Turn, auch Smalltalk |
| Im Router | Sekretaerin muesste Fachsprache aller Abteilungen kennen |
| In der Perzeption | Ueberlaestet den Perzeption-Call, falsche Zustaendigkeit |
| **Im Classify-Node** | **Kostenlos: LLM-Call existiert bereits, Domain Language ist lokal** |

### Sekretaerin / Empfang / Sachbearbeiter — Metapher

- **Sekretaerin (Router):** Empfaengt den Kunden, entscheidet welche Fachabteilung zustaendig ist. Diagnostiziert nicht.
- **Empfang der Fachabteilung (Classify-Node):** Nimmt den Kunden auf, fuellt das interne Formular aus — in der Fachsprache der Abteilung.
- **Sachbearbeiter (CRUD):** Arbeitet ausschliesslich mit dem ausgefuellten Formular. Sieht den Kunden nicht direkt.

### Classify-Output (erweitert)

```json
{
    "action": "update",
    "target": "Einkaufsliste",
    "target_typ": "inhalt",
    "konfidenz": "hoch",
    "normalisiert": "remove_content: Bananen von Notiz 'Einkaufsliste' entfernen"
}
```

Die CRUD liest `normalisiert` statt `aufgabe` (den rohen User-Prompt).

---

## 5. Dreiphasenmodell

### Phase 1: Eingabe (verstehen)

- Aufnahme des rohen User-Prompts
- Perzeption: Emotion, Arousal, Intent, Modus, Stil, Beziehungsdynamik
- Router: Fachabteilung bestimmen
- Ergebnis: Alle Dimensionen gemessen, Rohdaten vollstaendig im State

### Phase 2: Verarbeitung (handeln)

- Classify: Normalisierung in Domain Language, Aktionsklassifikation
- CRUD: Arbeitet auf normalisierten, bekannten, berechenbaren Werten
- Verifikation: Prueft gegen erwarteten Zustand
- Ergebnis: Fehleranfaelligkeit niedrig, deterministische Pfade wo moeglich

### Phase 3: Ausgabe (antworten)

- Responder: Arbeitet mit Originaltext, Emotionen, Energie, Stil
- Gespraechsvektor: Richtung und Laenge aus EI-Dimensionen
- Charakter: Ton, Persoenlichkeit, Beziehungsdynamik
- Ergebnis: Antwort spiegelt die volle emotionale Bandbreite des Users

---

## 6. [FACHSPRACHE]-Block

Jeder Agent definiert sein Fachvokabular als Domain Language. Der Classify-Prompt baut daraus einen `[FACHSPRACHE]`-Block:

### Format (generisch)

Seit der Prompt-Segregation (Chat 46–47) liegt der `[FACHSPRACHE]`-Block pro Agent als eigene Datei unter `prompts/default/`:
- `classify_notizen.fachsprache.txt`
- `classify_timeline.fachsprache.txt`
- `classify_direktiven.fachsprache.txt`
- `classify_charakter.fachsprache.txt`

Der Classify-Node baut den Prompt aus vier Bausteinen zusammen: `{agent}.identity` + `{agent}.task` + `{agent}.fachsprache` + `{agent}.rules`.

Vor der Segregation waren die Domain-Language-Daten als Python-Dict im Classify-Modul definiert — die Struktur war:

```python
DOMAIN_LANGUAGE = {
    "aktionen": {
        "create": "Neuen Eintrag anlegen",
        "read": "Bestehenden Eintrag anzeigen",
        "update": "Bestehenden Eintrag inhaltlich aendern",
        "delete": "Eintrag deaktivieren (Soft-Delete)",
        # ... weitere agent-spezifische Aktionen
    },
    "entitaeten": ["Notiz", "Liste", "Merkzettel", "Entwurf"],
    "format": "{action}: {beschreibung} (betrifft {entitaet} '{name}')",
}
```

### Vokabular-Pattern

Jede Aktion bekommt eine klare Fachsprache-Definition. Das LLM uebersetzt den Rohtext in dieses Vokabular:

| User sagt | Normalisiert |
|-----------|-------------|
| "Hau die Scheisse raus" | "remove_content: Bananen von Notiz 'Einkaufsliste' entfernen" |
| "Schmeiss noch Milch drauf" | "add_content: Milch zu Notiz 'Einkaufsliste' hinzufuegen" |
| "Nenn mich ab jetzt Boss" | "update: Anrede des Nutzers auf 'Boss' aendern" |
| "Hau mir Montag nen Zahnarzt rein" | "create: Termin 'Zahnarzt' am Montag anlegen" |

Dasselbe Prinzip wie der `[ERKENNUNGSHILFE]`-Block aus der CRUD-Haertung — erweitert um die Normalisierungsanweisung.

---

## 7. Abgrenzungen

### Was die Normalisierung NICHT ist

- **Keine Zensur.** Emotionen und Slang werden nicht unterdrueckt — sie bleiben im `user_prompt` fuer den Responder.
- **Keine Vereinfachung.** Der volle Kontext bleibt erhalten; die Normalisierung ist eine parallele Repraesentation, kein Ersatz.
- **Kein Parsing.** Es ist kein regelbasierter Parser, sondern eine LLM-basierte Uebersetzung im bestehenden Classify-Call.
- **Kein Extra-LLM-Call.** Sie ist ein Feld im bestehenden Classify-Output.
- **Kein Ersatz fuer Verb-Mappings.** Verb-Mappings sind deterministisch und user-spezifisch. Normalisierung ist LLM-basiert und agenten-spezifisch. Beide ergaenzen sich.

### Was die Normalisierung IST

- Eine Uebersetzung von natuerlicher Sprache in die Fachsprache des zustaendigen Agenten
- Ein Formular, das der Empfang der Fachabteilung ausfuellt
- Eine Qualitaetssicherungsmassnahme fuer die interne Verarbeitungskette

---

## 8. Verb-Mappings Rollenverschiebung (Chat 44)

Mit der Einfuehrung der Domain Language verschiebt sich die Rolle von Keywords und Verb-Mappings:

| Aspekt | Vorher (Chat 42) | Nachher (Chat 44) |
|--------|-------------------|-------------------|
| Primaere Erkennung | Keywords + Verb-Mappings + LLM | Domain Language ([FACHSPRACHE]-Block) |
| Sekundaere Pruefung | — | Keywords + Verb-Mappings (Konfidenz-Anker) |
| Lern-Schwellwert | 3 (keine Rueckfrage ab Konfidenz >=3) | Unveraendert |
| Funktion | "Was meint der User?" (Verstaendnis) | "Stimmt das LLM mit deterministischer Pruefung ueberein?" (Vertrauen) |

Die `[ERKENNUNGSHILFE]` liefert weiterhin Hints an den Classify, aber die Domain Language im `[FACHSPRACHE]`-Block ist jetzt die primaere Quelle fuer das Verstaendnis umgangssprachlicher Ausdruecke.

---

## 9. Bezug zu bestehenden Konzepten

| Konzept | Bezug |
|---------|-------|
| CRUD-Haertung (nova-14-k) | Normalisierung staerkt Phase 1 (ERKENNEN) und Phase 2 (VALIDIEREN) |
| Dreistufige Erkennung | Keywords + Verb-Mappings liefern [ERKENNUNGSHILFE], Classify nutzt sie + normalisiert |
| Strukturierte Kontextualisierung | Domain Language ist strukturierte Kontextualisierung fuer den Classify-Prompt |
| Daten vollstaendig transportieren | Normalisierung ergaenzt, ersetzt nicht — Rohdaten bleiben erhalten |

---

## 10. Status

Implementiert fuer 4 von 6 Agenten:

| Agent | Chat | Status |
|-------|------|--------|
| NotizenAgent | Chat 43 | Implementiert |
| DirektivenAgent | Chat 44 | Implementiert |
| CharakterIdentitaetAgent | Chat 44 | Implementiert |
| TimelineAgent | Chat 44 | Implementiert |
| FaktenAgent | — | Offen (laeuft ueber Salienz-Pipeline, braucht vermutlich keine Normalisierung) |
| DateienAgent | — | Offen (neuer Agent, geplant) |

**Fallback:** Wenn der Classify das `normalisiert`-Feld nicht oder fehlerhaft liefert, faellt CRUD auf `user_prompt` zurueck — keine Regression.
