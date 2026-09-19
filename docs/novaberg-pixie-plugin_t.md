# Novaberg — Pixie-Plugin-Architektur (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-pixie-plugin_k.md`](novaberg-pixie-plugin_k.md) · Bauplan und Umstellung: [`novaberg-pixie-plugin_b.md`](novaberg-pixie-plugin_b.md) · Diskussion und Ergänzungen: [`novaberg-pixie-plugin_e.md`](novaberg-pixie-plugin_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 3. Architektur

### 3.1 Queue-Eintrag fuer User-Auftraege

```json
{
    "aufgabe": "recherche",
    "modus": "auftrag",
    "themen": "Zwiebelanbau",
    "kern": "User will umfassende Recherche zum Thema Zwiebelanbau",
    "context_user": "meister",
    "scope": "umfassend"
}
```

Feld `modus: "auftrag"` signalisiert dem Agenten: Mehrere Durchlaeufe, Zwischenmeldungen, breiterer Scope.

### 3.2 Dispatch vom Router

Neuer Pfad im Router-Output: Wenn die Domain ein Pixie-Agent ist, schreibt der Graph einen Queue-Eintrag statt einen Agent-Dispatch aufzurufen.

```python
# In graph/nodes/router.py (konzeptionell)
if domain in PIXIE_DOMAINS:
    # Asynchron: Queue-Eintrag schreiben
    queue_eintrag = {
        "aufgabe": domain,
        "modus": "auftrag",
        "themen": extrahierte_themen,
        "kern": zusammenfassung,
        "context_user": user_id
    }
    shadow_queue_push(user_id, queue_eintrag)   # seit 15.08.2026: Zeile
                                                # in shadow_auftrag, und
                                                # prioritaet ist Pflicht
    
    # Responder bekommt Hinweis fuer sofortige Antwort
    return {"agent_result": AgentResult(
        agent_name="pixie_dispatch",
        ergebnis="Auftrag angenommen. Recherche laeuft im Hintergrund.",
        status="angenommen"
    )}
```

Der Responder sagt dem User sofort: "Ich recherchiere das fuer dich." Der Pixie-Router nimmt den Queue-Eintrag auf und leitet an den richtigen Agenten weiter.

### 3.3 Erweiterbarkeit

Neue Pixie-Auftraege = neue Domains im Router + neuer Agent-Ordner. Beispiele fuer zukuenftige Pixie-Plugins:

| Domain | Agent | Beschreibung |
|--------|-------|-------------|
| `recherche` | RechercheAgent | Breite Web-Recherche |
| `vertiefung` | VertiefungsAgent | Tiefe Recherche zu bekanntem Thema |
| `zusammenfassung` | ZusammenfassungsAgent (zukuenftig) | Konsolidierung mehrerer Wissen-Dateien |
| `skill` | SkillAgent (Epic 10, zukuenftig) | Code-Skill generieren via Claude API |

Jeder Agent entscheidet selbst, wie viele Durchlaeufe er im Auftragsmodus faehrt. Der Router kennt nur die Domain, nicht die interne Logik — "Die Sekretaerin diagnostiziert nicht."

---

## 4. Responder-Integration

### 4.1 Sofortige Antwort

Wenn der Router einen Pixie-Auftrag dispatcht, muss der Responder dem User sofort antworten — der User wartet nicht 15 Minuten auf eine Recherche:

```
User: "Recherchiere Zwiebelanbau fuer mich, umfassend."
Nova: "Das mache ich! Gib mir etwas Zeit, das ist ein groesseres Thema.
       Ich melde mich mit Ergebnissen."
```

Das `AgentResult` mit `status="angenommen"` gibt dem Responder den Hinweis, eine Bestaetigung zu formulieren.

### 4.2 Zwischenmeldungen

Im Auftragsmodus schickt der Agent nach jedem Durchlauf einen Stack-Push:

```
[Durchlauf 1 abgeschlossen]
Nova: "Erster Ueberblick steht — Sorten, Zeitplanung, Grundlagen.
       Ich vertiefe jetzt Hochbeet-Bau und Bodenqualitaet."

[Durchlauf 3 abgeschlossen]
Nova: "Schaedlinge und Begleitpflanzen sind drin.
       Noch Ernte und Lagerung, dann konsolidiere ich."

[Alle Durchlaeufe abgeschlossen]
Nova: "Fertig! Die Recherche liegt in Obsidian bereit —
       15 Seiten von Sortenauswahl bis Mischkultur."
```

### 4.3 Abbruch durch User

Der User kann jederzeit sagen "Das reicht" oder "Stopp die Recherche." Der Router erkennt das als Abbruch-Signal und schreibt einen Queue-Eintrag mit `aufgabe: "abbruch"`. Der Agent beendet den aktuellen Durchlauf, speichert den bisherigen Stand, und meldet zurueck.

---
