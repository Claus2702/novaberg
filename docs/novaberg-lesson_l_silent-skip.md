# Novaberg — Lesson: Silent Skip

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Silent Skip als gefährlichste Bug-Klasse
**Stand:** 11. Mai 2026, Chat 85
**Pfad:** novaberg/docs/novaberg-lesson_l_silent-skip.md
**Kategorie:** Allgemein, nicht modul-bezogen — Grundlagen-Lesson für EVA-Disziplin

---

## 1. Der Vorfall

Am 5. April 2026 schrieb der PromotionAgent zuletzt einen Eintrag in `hintergrund_log`. Sechs Wochen lang danach: nichts mehr. Keine Erfolgs-Meldungen, keine Fehler-Meldungen, kein Audit-Trail. Die Tabelle blieb leer.

Gleichzeitig akkumulierte sich in der Redis-Queue `queue:nova` ein Stapel von 34 Promotion-Aufträgen. Ihre KZG-Quelldaten waren längst per TTL aus Redis verfallen. Pixie startete alle zwei Minuten einen Heartbeat, der Worker pop'te Aufträge, scheiterte stillschweigend an den fehlenden Daten und schrieb nichts. Die CPU lief dauerhaft auf 55%, aber das Langzeitgedächtnis bekam keinen einzigen Eintrag.

Sechs Wochen lang waren alle wertvollen Erinnerungen unwiederbringlich verloren.

Nichts im Log-Stream wies darauf hin. Der Server lief, Pixie war "aktiv", die Heartbeats wurden im APScheduler protokolliert. Aus jeder oberflächlichen Sicht funktionierte das System. Tatsächlich war eine zentrale Pipeline tot.

## 2. Die Ursache

Der Bug bestand aus zwei zusammenwirkenden Code-Stellen in `agents/promotion/agent.py`.

### Anti-Pattern 1: Fallback maskiert Defekt

```python
inhalt: str = _hget("inhalt") or themen
```

Diese Zeile sollte einen defensiven Default gegen fehlende KZG-Hash-Felder bieten. Tatsächlich produzierte sie das Gegenteil: Bei einem TTL-abgelaufenen KZG-Eintrag lieferte `_hget("inhalt")` einen leeren String. Statt das als Defekt zu erkennen, fiel der Code auf den `themen`-String aus dem Queue-Auftrag zurück. Die Promotion lief weiter — mit defekten Daten, ohne dass irgendjemand etwas merkte.

Der Fallback war als Robustheit gedacht. Tatsächlich war er ein perfektes Maskierungsmuster: Defekte Eingangsdaten wurden zu plausiblen Verarbeitungs-Daten umgeformt, der Defekt verschwand aus der Sichtbarkeit.

### Anti-Pattern 2: Silent skip mit `logger.warning`

```python
if not inhalt:
    logger.warning(
        f"Promotion: KZG-Key '{kzg_key}' nicht mehr vorhanden — uebersprungen"
    )
    return
```

Diese Stelle griff nur in dem seltenen Fall, dass sowohl `_hget("inhalt")` als auch `themen` leer waren. Wenn sie griff, schrieb sie eine `warning`-Zeile in den stdout-Log und beendete die Funktion. Kein Eintrag in `hintergrund_log`. Keine Eskalation. Keine Persistenz des Vorfalls.

Das Wort "uebersprungen" ist die Selbst-Anklage des Codes: Er weiß, dass etwas nicht stimmt, und entscheidet, nichts zu tun. Das ist die Definition von silent skip.

### Anti-Pattern 3: Fehlender Audit-Pfad

Der gesamte Promotion-Code hatte keinen `hintergrund_log`-Schreibpfad mehr. Der Header der Datei dokumentierte: *"Migriert aus: services/shadow_agent/tasks/lzg_promotion.py"*. Bei der Migration ging der Audit-Pfad verloren. Niemand bemerkte es, weil im normalen Betrieb die alten `hintergrund_log`-Einträge weiter sichtbar waren — der Anschein blieb, die Tabelle "lief".

Die Kombination der drei Anti-Patterns hatte zur Folge, dass sechs Wochen lang Datenverlust passierte und niemand es sehen konnte.

## 3. Die Diagnose

Der Bug fiel erst durch eine systematische Diagnose auf, ausgelöst durch die Beobachtung "Pixie läuft, aber LZG ist leer".

**Schritt 1 — Queue-Inspektion:** `LRANGE queue:nova 0 -1` zeigte 34 angesammelte Aufträge. Älteste mit Timestamps aus dem 15. April.

**Schritt 2 — KZG-Existenz-Check:** `EXISTS kzg:nova:1776291789265` lieferte `0`. Die Quelldaten waren weg.

**Schritt 3 — Tabellen-Check:** `SELECT MAX(id), MAX(erstellt_am) FROM hintergrund_log` zeigte Stand 5. April. Sechs Wochen Lücke.

**Schritt 4 — Code-Analyse:** Der Fallback `or themen` und der `warning`-Skip wurden in `_eintrag_verarbeiten` identifiziert. Der fehlende `_audit_log`-Pfad bestätigte den blinden Fleck.

Die Diagnose dauerte etwa 30 Minuten. Der eigentliche Defekt war sechs Wochen alt.

## 4. Die Behebung

Der Fix bestand aus zwei Eingriffen.

**Eingriff A — `_eintrag_verarbeiten` nach EVA-Disziplin umgebaut:**

Drei explizite Vorbedingungs-Checks vor jeder Verarbeitung, jeweils mit `logger.error` und Audit-Eintrag `status='fehler'`:

1. `not kzg_key` — Auftrag ohne KZG-Key
2. `not redis_client.exists(kzg_key)` — KZG-Hash existiert nicht mehr in Redis
3. `not _hget("inhalt")` — KZG-Hash existiert, aber Pflichtfeld leer

Der Fallback `or themen` wurde entfernt. Stattdessen: explizit prüfen, explizit verwerfen. Die übrigen `_hget`-Aufrufe wurden erst nach dem `inhalt`-Check ausgeführt, sodass keine unnötigen Redis-Operationen gegen tote Keys mehr laufen.

Bei erfolgreicher Verarbeitung: Audit-Eintrag `status='erledigt'` mit Ergebnis-Zusammenfassung (Klassifikation, Anzahl extrahierter Fakten, ob LZG-Eintrag geschrieben wurde).

**Eingriff B — `_audit_log` als statische Helper-Methode:**

```python
@staticmethod
def _audit_log(user_id, aufgabe, status, ergebnis):
    try:
        db_manager.execute(
            "INSERT INTO hintergrund_log "
            "(user_id, aufgabe, status, ergebnis, verarbeitet_am) "
            "VALUES (%s, %s, %s, %s, NOW())",
            (user_id, aufgabe, status, ergebnis),
        )
    except Exception as ex:
        logger.critical(
            f"hintergrund_log-INSERT fehlgeschlagen: {ex}"
        )
```

Failsafe gegen Endlos-Rekursion: Wenn der Audit-INSERT selbst scheitert, wird nur `logger.critical` gerufen, kein erneuter DB-Call.

Nach dem Restart lief Pixie aufgeräumt: 34 Aufträge wurden abgearbeitet, die toten KZG-Keys als `fehler` auditiert, der Rest sauber promotet. Der Audit-Trail war wieder vollständig.

## 5. Die Prinzipien

Aus diesem Vorfall werden vier Prinzipien abgeleitet, die ins Entwicklerhandbuch (§1–§4) übernommen wurden.

### Prinzip 1 — EVA: Eingabe, Verarbeitung, Ausgabe

Jede Funktion, die Daten von außen erhält, validiert ihre Eingabe vor der Verarbeitung und verifiziert ihr Ergebnis nach der Verarbeitung. Externe Datenquellen sind potenziell defekt, leer oder TTL-abgelaufen. Wer das ignoriert, schreibt Code, der irgendwann silent korrumpierte Daten produziert.

### Prinzip 2 — Fail loud, fail logged

Keine silent skips. Keine Fallbacks, die Defekte maskieren. Wenn etwas nicht stimmt, wird es laut bemerkt und in nachvollziehbarer Form protokolliert. `logger.warning` für einen Skip ist falsch — ein Skip ist ein Fehler, kein degradierter Zustand. `logger.error` und Audit-Eintrag sind die korrekte Reaktion.

### Prinzip 3 — Audit-Pflicht

Jeder Background-Task schreibt `gestartet`, `erledigt` oder `fehler` in `hintergrund_log`. Wer einen Task ausführt, hinterlässt einen Audit-Eintrag. Failsafe gegen Endlos-Rekursion ist Pflicht: wenn der Audit selbst scheitert, nur `logger.critical`, kein erneuter DB-Call.

### Prinzip 4 — Keine maskierten Defekte

Fallback-Werte für Pflichtfelder sind verboten. `value or fallback` ist kein Robustheits-Pattern, sondern ein Maskierungs-Pattern. Wenn ein Pflichtfeld fehlt, ist die Eingabe defekt — sie wird explizit geprüft, explizit verworfen, explizit geloggt.

## 6. Die Konsequenz

Drei strukturelle Maßnahmen folgten auf den Vorfall.

**Erstens:** Das Entwicklerhandbuch `docs/DEVELOPER_HANDBOOK.md` wurde angelegt und verpflichtend gemacht. Brudi-Prompts enthalten künftig die Referenz auf das Handbuch.

**Zweitens:** Ein Code-Audit-Sprint wurde geplant, der die EVA-Disziplin systematisch in allen Pipeline-Komponenten prüft und herstellt. Beginnend mit den Pixie-Agenten, dann Memory-Pipelines, dann LangGraph-Nodes.

**Drittens:** Diese Lesson wurde geschrieben — als Archiv, als Mahnung, als Referenz für künftige Architektur-Entscheidungen. Sie wird nicht überarbeitet. Wer in einem Jahr wissen will, warum Novaberg so streng mit Validierung und Audit ist, liest hier nach.

## 7. Der Preis

Sechs Wochen Datenverlust im Langzeitgedächtnis. Erinnerungen, die für Novas Charakter-Profil und Beziehungsdynamik wichtig gewesen wären, sind unwiederbringlich weg. Es gibt kein Backup für KZG-Inhalte, deren TTL abgelaufen ist.

Der Vorfall hat keinen einzelnen Verantwortlichen — er ist Folge einer Migration ohne Audit-Pfad, eines verbreiteten Anti-Patterns (`value or fallback`), und einer fehlenden gemeinsamen Übereinkunft über Code-Qualität.

Das Entwicklerhandbuch und der Audit-Sprint sind die Antwort. Diese Lesson ist die Erinnerung daran, dass die Antwort nicht aus prophylaktischer Disziplin entstanden ist, sondern aus konkretem Schaden.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*
