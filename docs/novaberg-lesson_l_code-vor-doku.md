# Lesson: Code lesen, nicht aus Protokollen ableiten

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Architektur-Beratung braucht aktuelle Code-Sicht, nicht rekonstruierten Protokoll-Kontext
**Stand:** 06. Mai 2026, Chat 78
**Pfad:** novaberg/docs/novaberg-lesson_l_code-vor-doku.md
**Typ:** Lesson (L)
**Entdeckt in:** Chat 78 (PIXIE-OFF + TimelineAgent-Audit + THINK-TRANSITION-INFO Design)
**Betrifft:** Architektur-Beratungs-Schicht, Brudi-Prompt-Schreiben, jede Code-spezifische Sprint-Vorbereitung

---

## 1. Beobachtung

In Chat 78 traten mehrere Fehlannahmen in der Architekturberatung auf, die alle dieselbe Quelle hatten: der Versuch, Code-Verhalten aus Protokollen und Memory-Snippets zu rekonstruieren statt die Quelldateien zu lesen.

Konkrete Beispiele:

- **Status-String falsch erinnert.** Im ersten THINK-TRANSITION-INFO-Brudi-Prompt-Entwurf stand `status == "completed"`. Im echten Code (`agents/base.py`) heißt der Erfolgsstatus `"abgeschlossen"`. Der Fehler kam aus einem englisch-deutsch-Mix in der Erinnerung, nicht aus einer Code-Lektüre. Hätte den ganzen Sprint stillschweigend ins Leere laufen lassen, weil keine `successes`-Liste gematcht hätte.
- **Update-Fall im Brudi-Prompt vergessen.** Der ursprüngliche Brudi-Prompt-Entwurf konzentrierte sich auf den Create-Fall ("Trag mir Zahnarzt morgen 14 Uhr ein"), obwohl der Live-Bug aus Chat 77 ein Update-Szenario war ("Verschiebe den Zahnarzt..."). Der Live-Befund war der ursprüngliche Auslöser — und im Sprint-Design wurde er übersehen.
- **Notizen-`memory_context`-Lücke erst nach Code-Vorlage erkannt.** Die Tatsache, dass der Thinker den `memory_context` (Vor-Insert-Stand) UND eigene Tool-Outputs (Nach-Insert-Stand) gleichzeitig sieht, wurde erst klar, als der Thinker-Code Zeile für Zeile gelesen wurde. Aus Protokoll-Kontext und Memory wäre die Diagnose fragmentiert geblieben.

---

## 2. Erkenntnis

> **Vor jedem Brudi-Prompt, der konkrete Code-Stellen referenziert, müssen die Quelldateien gelesen sein.**

Memory und Protokoll sind Kontextquellen für Stimmung, Geschichte, Entscheidungen — keine Wahrheitsquellen für Code-Details. Datei:Zeile-Anker erfordern Code-Sicht. Konkrete Funktionsnamen, Status-Strings, Parameter-Listen, Aufruf-Reihenfolgen müssen aus aktuell gelesenen Dateien stammen.

Code dreht sich schneller als Protokoll. Was vor zehn Chats stimmte, kann heute falsch sein — ohne dass der Doku- oder Memory-Stand mitgeführt wurde.

---

## 3. Verstärkung des bestehenden Prinzips

Das Prinzip *"Lies den Code, nicht die Doku"* ist im Projekt bereits etabliert — siehe `novaberg-pattern-domain-language.md` und der KZG/LZG-Kontext, in dem strukturelle Annahmen mehrfach durch direkte Code-Inspektion korrigiert wurden.

**Chat 78 zeigt:** Das Prinzip gilt nicht nur für die Implementierungs-Schicht (wo es offensichtlich ist), sondern auch für die Architekturberatungs-Schicht — die scheinbar abstrakter ist, aber genauso oft konkrete Code-Anker enthält (Datei:Zeile, Funktionsnamen, Status-Werte, Tabellen-Formate).

Architektur ohne Code-Anker ist Wunschdenken. Architektur mit falschen Code-Ankern ist gefährlich, weil sie Vertrauen ausstrahlt, das nicht gerechtfertigt ist.

---

## 4. Operationalisierung

Wenn ein Brudi-Prompt geschrieben wird, der konkrete Funktionsnamen, Zeilennummern oder Verhalten referenziert, müssen diese aus aktuell gelesenen Dateien stammen.

**Audit-Phase als Standard-Mechanismus:** Vor einem Code-spezifischen Sprint liest Brudi (oder die Architektur-Schicht selbst) den relevanten Code, dokumentiert Ist-Stand und mögliche Schreibstellen, danach wird geplant. Die Audit-Phase ist Pflicht, nicht Kür.

Beispiele aus Chat 78, in denen das Audit-Vorgehen den Sprint vor Fehlannahmen geschützt hat:

- **TimelineAgent-Audit** vor M2.5a: Hat aufgedeckt, dass die Manager-Schreibpfade tot sind (statt migriert werden zu müssen) und der Subgraph bereits sauber ist. Sprint-Scope schrumpfte deutlich.
- **PIXIE-OFF-Audit** vor Implementation: Hat die zehn konkreten Push-/Setter-Stellen exakt benannt (Datei:Zeile), inkl. Falsch-Positiver, die ausgeschlossen werden mussten (Migrations-Skript, CharakterAgent-Cleanup). Sprint-Prompt war damit präzise genug, dass Brudi keine Suchphase mehr brauchte.

---

## 5. Praktische Faustregel

Bevor ein Brudi-Prompt mit konkreten Code-Ankern abgeschickt wird:

1. Sind alle erwähnten Datei:Zeile-Referenzen aus einer aktuell gelesenen Datei?
2. Sind alle erwähnten Funktionsnamen, Status-Strings, Konstanten direkt im Code verifiziert?
3. Falls nein: Audit-Phase einschieben (lesen, dokumentieren), dann erneut planen.

Drei Minuten Lesen sparen einen halben Sprint, der ins Leere läuft.

---

→ Bestehendes Prinzip: `novaberg-pattern-domain-language.md`
→ Chat-78-Protokoll: `novaberg-chat-78_protokoll.md`
→ Beispiel TimelineAgent-Audit: `novaberg-backlog.md` §7 (Sprint M2.5a)
