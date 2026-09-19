# Novaberg — Cognitive Pipeline (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-thinking-cognitive-pipeline_k.md`](novaberg-thinking-cognitive-pipeline_k.md) · Ausarbeitung: [`novaberg-thinking-cognitive-pipeline_t.md`](novaberg-thinking-cognitive-pipeline_t.md) · Diskussion und Ergänzungen: [`novaberg-thinking-cognitive-pipeline_e.md`](novaberg-thinking-cognitive-pipeline_e.md) · Messungen: keiner. Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

Die Loop-Schritte, auf die der Phasen-Plan mit *Schritt 4.2* bis *Schritt 4.10* verweist, stehen in [`novaberg-thinking-cognitive-pipeline_t.md`](novaberg-thinking-cognitive-pipeline_t.md). Die Entscheidung im *Nachtrag 14.09.2026* ist in [`novaberg-thinking-cognitive-pipeline_e.md`](novaberg-thinking-cognitive-pipeline_e.md), Abschnitt A, als E2 geführt.

## 11. Phasen-Plan

Drei Phasen, alle aufeinander aufbauend.

### Phase A — Cognitive Loop ohne Skills

**Ziel:** Der Loop läuft, Frames werden aktiviert und aufgelöst, Werkzeuge werden gerufen, Ergebnisse werden validiert. Kein Skill-Speicher, kein Lookup, keine Reflexion. Das ist die kognitive Grundausstattung.

**Voraussetzungen:**
- Frame-Konzept implementiert (mindestens Anliegen-Frame).
- Phase 0 aus Frame-Konzept erledigt: M2.5b, TIMELINE-PAIR-MIGRATION, NOTIZEN-PAIR-MISSING, FAKTEN-PAIR-IGNORED.
- CognitiveGraph als neuer Sub-Graph in `graph/cognitive_graph.py`.

**Schritte:**
1. CognitiveGraph-Skelett mit Akutheits-Klassifikation.
2. Frame-Aktivierung (Schritt 4.2) für Anliegen-Frame.
3. Frame-Auflöser (Schritt 4.3) mit Knowledge-Graph-, Notizen-, Timeline-Quellen.
4. Cross-Frame-Validierung und Plausibilitätsprüfung als Sammel-Call (Schritte 4.4 und 4.5).
5. Konflikt-/Lücken-Behandlung (Schritt 4.6).
6. Default-Vorgehen im Skill-Executor (Schritt 4.8 ohne Skill).
7. Werkzeug-Aufruf (Schritt 4.9) mit existierenden Agenten.
8. Ergebnis-Validierung (Schritt 4.10).
9. Migration: NotizenAgent und TimelineAgent als erste Konsumenten des CognitiveGraph; Planner bleibt Fallback für andere Anliegen-Klassen.

**Stand 28.08.2026:** Die Schritte 1 und 2 sind gebaut — **nicht als CognitiveGraph hinter dem Router, sondern als Sachlage-Knoten vor dem Gesprächsvektor**, für beide Pfade (`novaberg-thinking-lage_k.md` §2a begründet die Abweichung: die Befunde lagen im Konversationspfad). Schritt 1 ist die Akutheit je Objekt, Schritt 2 die Frame-Aktivierung in der Konversationsfassung — Frame-Klasse, gedeckte und offene Slots, die das Modell je Turn erhebt, ohne Frame-Lager. Dazu, im Pipeline-Konzept nicht vorgesehen: ein kurzfristiges Ziel aus der Blase, der Rückfrage-Gegenstand für den Verfasser, das Gedächtnis der Blasen (`sachlage_verlauf`) mit Brücke und Wiederaufnahme (Scheiben 2–5 dort). **Schritt 3 ist seit dem 28.08.2026, spät, in der Konversationsfassung gebaut** (`novaberg-thinking-lage_k.md` §4, Scheibe 6): Die offenen Eigenschaften der akuten Objekte werden nach dem Sachlage-Call in einem eigenen, kleinen Call gegen ein nummeriertes Angebot aus dem Gedächtnis-Pool des Turns gehalten — KZG, LZG, Bibliothek (`autonomous_wissen`), Aufzeichnungen, Kalender —, und eine gedeckte Eigenschaft trägt ihre Quelle (`quellen`). **Abweichungen vom Konzept, gemessen:** Die Quelle 1 (Knowledge Graph, `fakten`) trägt für das Paar 0 Zeilen und wird nicht befragt; Notizen nicht, weil ihr einziger Leser mit Treffersemantik beim Lesen schreibt; ein Frame-Lager gibt es nicht; die Kritikalität einer Lücke wird nicht bewertet. Der Pool ist mit dem Reiz des Turns gesucht, nicht mit der Lücke — die gezielte Suche je offener Eigenschaft ist die Vollfassung. **Schritt 5 ist seit dem 29.08.2026 in der Konversationsfassung gebaut** (`novaberg-thinking-lage_k.md` §4, Scheibe 7): ein eigener Call prüft bei akutem Objekt die Äußerung des Nutzers gegen Weltwissen in den vier Stufen aus dem Frames-Konzept §6.2; nur die drei über `plausibel` stehen im Artefakt (`plausibilitaet`), der Verfasser bekommt sie als Zweifel, die Form bleibt bei Haltung und Vehikel. Im Labor 0/12 Fehlalarme, 18/18 nicht-plausible gemeldet, die Stufe im Mittel eine zu hoch. **Schritt 4 bleibt Konzept**, weil Cross-Frame-Konsistenz Slots aus Fakten oder Lager braucht. **Schritt 6 ist seit dem 29.08.2026, vormittags, in der Konversationsfassung angefangen** (`novaberg-thinking-lage_k.md` §4, Scheibe 8): Jede offene Eigenschaft trägt ihren Wissensträger — `nutzer` (Rückfrage), `welt` (Antwortstoff aus dem Kopf), `nachschlagen` (Antwortstoff mit Websuche); das ist die Lückenbehandlung aus §4.6 ohne Kritikalität. Damit ist auch **Schritt 9** mit einem ersten Werkzeug begonnen: eine Websuche je Turn für die erste `nachschlagen`-Eigenschaft, dieselbe wie im Thinker. Im Labor: Alltag 43 × nutzer / 5 × welt, Wissenschaft 3 / 24 / 15 nachschlagen. **Seit dem 29.08.2026, mittags, trägt jeder gedeckte Slot seinen Sprecher** (`novaberg-thinking-lage_k.md` §4, Scheibe 9: `nutzer` / `nova`) — die Gegenseite des Wissensträgers: dort *wer kann es wissen*, hier *wer hat es gesagt*; im Pipeline-Konzept nicht vorgesehen, aus dem Betrieb (der Verfasser eröffnete mit dem Gedanken des Nutzers als eigener Feststellung). **Seit dem 30.08.2026 ist Schritt 6 vollstaendig** (`novaberg-thinking-lage_k.md` §4, Scheibe 10): Jede offene Eigenschaft traegt neben ihrem Traeger ihr Gewicht — `kritisch`, wenn eine Antwort ohne sie raten muesste, sonst `unkritisch`. Zwei Leser waehlen danach vor, die Rueckfrage und die eine Websuche je Turn; der Block nennt die tragende Luecke, wenn sie beim Nutzer liegt. Im Labor 16 kritisch gegen 34 unkritisch ueber 15 Aeusserungen, kein fehlender Wert, 0 von 18 Objekten mit mehr als einer kritischen Luecke; der Rueckfrage-Gegenstand aendert sich in 2 von 8 Faellen. **Der Abbruch des Loops aus §4.6 ist damit nicht gebaut** — die Konversationsfassung kennt keinen Loop, den sie abbrechen koennte; die kritische Luecke wird vorgezogen, nicht erzwungen. **Offen sind Schritt 4, die Schritte 7 und 8 und die Migration.** **Seit dem 13.09.2026 gibt es einen Teil des Frame-Lagers in Konversationsfassung** (`novaberg-thinking-lage_k.md` §4, Scheibe 11): Die Objekte jedes gerechneten Turns stehen dauerhaft am Paar, je Eigenschaft ihr Wert mit Historie (ein neuer Wert loest ab, statt zu ueberschreiben), das Objekt wird ueber die Magnete des Turns an `entitaeten` gebunden, und Schritt 3 bekommt die gespeicherten Werte der akuten Objekte als eigene Quelle angeboten. Die Abweichung oben — *ein Frame-Lager gibt es nicht* — gilt damit fuer seine Lernmechanik (Konsens, Schema-Aggregat, Decay), nicht mehr fuer die Ablage. **Schritt 4 bleibt trotzdem Konzept:** Es gibt Werte je Objekt, aber keinen Vergleich ueber Objekte hinweg. Die Formpruefung des Artefakts haelt seit demselben Tag jedes Objektfeld, auch die vorige Blase beim Laden (`LAGE-FORMPRUEFUNG-UNVOLLSTAENDIG`, behoben).

> **Nachtrag 14.09.2026 — Schritt 9 bekommt einen Zuschnitt.** Scheibe 12 des Lage-Konzepts (`novaberg-thinking-lage_k.md` §4, entworfen, nicht gebaut) macht den TimelineAgent zum ersten Abnehmer der Objekte — **nicht über einen CognitiveGraph hinter dem Router, sondern über den Router selbst**: Der Empfang liest die akuten Objekte der Sachlage, die Anmeldung eines Dienstes trägt ein Objekt-Merkmal, eine gerechnete Nähe entscheidet über die Zuordnung, und die Zustellung trägt den Objektbezug. Das Angebot (*„soll ich ihn anlegen?"*) kommt aus der Haltung, die Zustimmung ist ein Auftrag. Die Werkzeugwahl bleibt damit beim Empfang und nicht bei einem Executor (Schritt 4.8) — eine Abweichung, entschieden vom Eigentümer am 14.09.2026 (Wortlaut im Lage-Konzept).

**Erfolgskriterium:** Die vier Live-Test-Befunde aus Chat 80 (NOTIZEN-VOR-TURN-BEZUG, NOTIZEN-CONTAINER-WECHSEL, NOTIZEN-SKILL-MANIFEST, NOTIZEN-UPDATE-TARGET-LEER) sind gelöst, ohne dass eine einzige Skill-Datei geschrieben wurde.

### Phase B — Skill-Speicher und -Anwendung

**Ziel:** Skills existieren, werden gefunden, modifizieren das Default-Vorgehen.

**Voraussetzungen:**
- Phase A live und stabil.
- Skills-Dokument finalisiert (`novaberg-thinking-skills_k.md`).
- Skill-Speicher-Schema (Datenbank-Tabelle oder Dateisystem-Verzeichnis).

**Schritte:**
1. Skill-Speicher anlegen, Format definieren.
2. Skill-Lookup im Schritt 4.7 (Themen-basiert, embedding-unterstützt).
3. Skill-Executor-Variante mit Skill-Text als zusätzlichem Prompt-Block (Schritt 4.8).
4. Erste handgeschriebene Skills für häufige Aufgabentypen (Wetter, Notiz-Verwaltung, Termin-Anlage).
5. Live-Beobachtung: Wirken die Skills wie erwartet? Welche werden umgangen, welche befolgt?

**Erfolgskriterium:** Drei bis fünf manuelle Skills sind im Speicher, beobachtbar in mindestens 80% der passenden Fälle ausgeführt, ohne Werkzeug-Schicht-Verletzungen.

### Phase C — Selbst-lernende Skills

**Ziel:** Nova schreibt und ändert Skills selbst auf Basis von Negativ-Feedback.

**Voraussetzungen:**
- Phase B stabil.
- Negativ-Feedback-Detektoren live (alle vier Quellen aus §5).
- Pixie-Reflexions-Lauf erweitert um Skill-Pflege.

**Schritte:**
1. Korrektur-Detektor (§5.1) im CognitiveGraph.
2. EI-Frust-Schwellwert-Heuristik (§5.2).
3. Validierungs-Konflikt-Marker (§5.3) bei den Schritten 4.4–4.6.
4. Pixie-Reflexionslauf erweitert um Skill-Edit-Logik.
5. Skill-Erstellungs-LLM-Call: Pixie schreibt aus Korrektur-Material den ersten Skill-Entwurf.
6. Skill-Edit-LLM-Call: Pixie passt existierenden Skill aufgrund Negativ-Feedback an.

**Erfolgskriterium:** Nova schreibt eigenständig mindestens drei Skills aus Praxis-Beobachtung, davon mindestens zwei sinnvoll genug, dass sie nicht beim ersten Anwendungsfall durch erneutes Negativ-Feedback wieder geändert werden müssen.

---
