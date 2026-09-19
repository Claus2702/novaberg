# Novaberg — Konzept: Fachabteilungs-Agenten (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-agent-fachabteilung_k.md`](novaberg-agent-fachabteilung_k.md) · Ausarbeitung: [`novaberg-agent-fachabteilung_t.md`](novaberg-agent-fachabteilung_t.md) · Diskussion und Ergänzungen: [`novaberg-agent-fachabteilung_e.md`](novaberg-agent-fachabteilung_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 6. Konkrete Auswirkungen auf bestehende Bugs

Viele der in Chat 48/49 entdeckten Bugs werden durch das Fachabteilungs-Epic **strukturell** gelöst:

| Bug | Aktuell | Nach Epic |
|-----|---------|-----------|
| CRUD-DESTILL-SUBTRAKT | Negation wird als Anweisung gespeichert | Output-Validation erkennt unsinniges Ergebnis → Rollback + erklärende Rückfrage |
| CRUD-REACTIVATE-COEXIST | Zwei widersprüchliche Charaktere aktiv | Semantik-Check erkennt Widerspruch → differenzierte Rückfrage |
| HALL2-Update | Halluzinierte Bestätigung | Output-Validation prüft ob die Aktion tatsächlich Sinn gemacht hat |
| RESP-CRUD-GENERIC | Corporate-Platitüden nach Agent-Erfolg | Differenzierte Rückfragen/Bestätigungen mit konkretem Inhalt-Bezug |
| CLASSIFY-CONFIRM | In Chat 49 einzeln gefixt | Wäre durch Semantik-Check ebenfalls abgedeckt gewesen |

Der RESUME-REJECT-Bug ist **Voraussetzung** für das Epic, nicht Teil seines Scopes: Ohne funktionierenden "Nein"-Pfad sind die differenzierten Rückfragen nutzlos.

---

## 7. Umsetzungs-Plan

### 7.1 Reihenfolge

1. **RESUME-REJECT fixen.** Der "Nein"-Pfad muss zuverlässig funktionieren, bevor differenzierte Rückfragen eingebaut werden. Dabei die neue Rückfrage-Typen-Architektur mit-designen.

2. **Pilot: CharakterIdentitaetAgent umbauen.** Die neue Pipeline erst an einem Agent erprobt, bevor sie auf alle vier ausgerollt wird. Charakter wurde in Chat 49 als Pilot identifiziert — dort wurden die meisten Fälle beobachtet.

3. **Gemeinsame Infrastruktur bauen.** `agents/crud_validation.py` erweitern um `SemantikCheck`-Klasse, `OutputValidation`-Klasse, und neue Rückfrage-Typen in `crud_validation.py`.

4. **Rollout auf die anderen drei Agenten.** DirektivenAgent, NotizenAgent, TimelineAgent bekommen die neuen Nodes. Agenten-spezifische Semantik-Check-Prompts in den jeweiligen Ordnern.

5. **Doku nachziehen.** `novaberg-agent-character.md`, `novaberg-agent-directives.md`, `novaberg-agent-notes.md`, `novaberg-agent-timeline.md` werden auf den neuen Stand gebracht.

### 7.2 Aufwand

Mehrere Sessions. Nicht wenige. Das ist substantielle Architekturarbeit.

Grobe Schätzung (aus Erfahrung mit ähnlich grossen Epics wie Prompt-Segregation oder CRUD-Härtung):
- RESUME-REJECT + neue Rückfrage-Architektur: 1-2 Sessions
- Pilot CharakterIdentitaetAgent: 2-3 Sessions
- Gemeinsame Infrastruktur: 1 Session
- Rollout auf 3 weitere Agenten: je 1 Session
- Doku: 1 Session

Realistisch: 8-10 Sessions über mehrere Wochen.

### 7.3 Risiken

- **Kontaminierung bestehender Tests:** Die CRUD-Härtung (Chat 42) hat gerade Stabilität gebracht. Der Umbau muss sie erhalten.
- **Prompt-Engineering des Semantik-Checks:** Der neue LLM-Call muss zuverlässig JSON-Output liefern. Erfahrung mit Gemma 4 aus Chat 46/48 hilft.
- **Latenz:** Ein zusätzlicher LLM-Call pro Agent-Operation erhöht die Antwortzeit. Gemma 4 ist schnell, aber nicht kostenlos.
- **Regressions-Risiko bei Rollout:** Jeder Agent bringt eigene Fachsprachen, eigene Daten-Strukturen. Der Pilot muss sauber sein, bevor übertragen wird.

### 7.4 Parallel-Arbeit

Während die Fachabteilungs-Umbauten laufen, können andere Arbeiten parallelisiert werden:
- Pixie-Classifier (unabhängig)
- Träumen + Vertiefen (unabhängig)
- Repo-Vorbereitung und Codeberg-Push (Meta-Arbeit)

Nicht parallel: Andere CRUD-Agent-Änderungen, weil sie mit dem Epic kollidieren würden.

---

## 10. Nächste Schritte

1. **Dieses Konzept lesen lassen.** Im nächsten Chat oder einer dedizierten Planungs-Session mit frischem Kopf.
2. **Einzelne offene Fragen durchdenken** (§8).
3. **RESUME-REJECT fixen.** Erster konkreter Umbau-Schritt.
4. **Pilot starten.** CharakterIdentitaetAgent als erstes umbauen.

---
