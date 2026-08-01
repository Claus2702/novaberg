# 02_L_a — Lesson: Timezone UTC vs. Lokal

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Timezone-Fehler in drei Wellen
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/novaberg-tool-timeparser_l_timezone.md
**Ursprung:** nova-02-l-a.md
**Typ:** Lesson (L)
**Entdeckt:** Chat 10 (O18) + Chat 11 (P7, P7b)
**Betrifft:** Timeline-System, Repository-Layer

---

## 1. Symptom

Drei Fehler, die nacheinander auftraten — jeder ein Symptom des gleichen Grundproblems:

**Welle 1 (O18):** Nova sagte „Dein Zahnarzttermin ist um 12:00 Uhr" — obwohl der Termin um 14:00 MEZ angelegt wurde. Der Termin wurde intern als UTC gespeichert (12:00 UTC = 14:00 MEZ), aber ohne Konvertierung angezeigt.

**Welle 2 (P7):** Nach dem O18-Fix (Schreibpfad korrigiert) sagte Nova „13:00" statt „14:00". Der Thinker korrigierte auf 14:00. Ursache: Der Schreibpfad war gefixt, aber die Lesepfade lieferten weiterhin UTC.

**Welle 3 (P7b):** Der Thinker fand einen verschobenen Termin nicht. Ursache: `timeline_check()` definierte die Tagesrange naiv (00:00–23:59 ohne Timezone), wurde als UTC interpretiert — der Termin lag am UTC-Vortag.

---

## 2. Ursache: Partielle Fixes

Das Grundproblem war nicht die fehlende Timezone-Konvertierung — die war bekannt. Das Problem war, dass der Fix nur einen Pfad traf und die anderen vergaß:

| Pfad | O18-Fix | P7-Fix | P7b-Fix |
|------|---------|--------|---------|
| Schreiben (Store) | ✅ Lokal→UTC | — | — |
| Lesen (Retrieve) | ❌ UTC blieb | ✅ UTC→Lokal | — |
| Query-Parameter (Range) | ❌ Naiv | ❌ Naiv | ✅ Lokal→UTC |

Drei Wellen, weil jede Welle nur den gerade sichtbaren Pfad fixte.

---

## 3. Die Lösung: Zentralisierung im Repository

Statt jeden Aufrufer einzeln zu fixen: Timezone-Konvertierung im Repository zentralisiert. Der `TimelineRepository` konvertiert jetzt an genau drei Stellen:

1. **Schreiben:** Lokale Zeit → UTC bei jedem INSERT
2. **Lesen:** UTC → Lokale Zeit bei jedem SELECT
3. **Query-Parameter:** Range-Grenzen in lokaler Zeit annehmen, vor der Query nach UTC konvertieren

Kein Aufrufer muss sich um Timezones kümmern — das Repository ist die einzige Stelle, die UTC kennt.

**Config:** `TIMEZONE = "Europe/Berlin"` in `config.py`. Verwendet `zoneinfo.ZoneInfo` (Python 3.9+).

---

## 4. Generalisierbare Erkenntnis

> **Das Partial-Fix-Problem:** Wenn ein Datentransformations-Schritt (wie UTC-Konvertierung) an mehreren Stellen im Code nötig ist, fixe nie die Stellen einzeln. Zentralisiere die Transformation an einer einzigen Schicht — im Repository, im Serializer, im Adapter. Jeder einzelne Fix erzeugt eine neue Asymmetrie, die den nächsten Bug verursacht.

> **Die Drei-Pfade-Regel:** Jede Datentransformation betrifft mindestens drei Pfade: Schreiben, Lesen, Abfragen. Wenn einer gefixt wird, müssen alle drei geprüft werden — nicht nur der gerade sichtbare.

## 5. Die vierte Welle — und warum sie keine Welle war (01.08.2026)

Nach Zone und Kalendertag fiel eine dritte Größe auf: `morgen` rechnete gegen die **echte Uhr**, auch wenn ein Bezugsmoment übergeben war. Dreimal derselbe Ausdruck gegen drei Bezugsmomente lieferte dreimal denselben Tag.

**Die naheliegende Diagnose war „schon wieder ein partieller Fix" — und sie war falsch.** Die Weitergabe fehlte nicht aus Nachlässigkeit; sie durfte so nicht stattfinden. Ein bestehender Test hielt fest, warum:

> Der Update-Pfad der Timeline reicht als Referenz die Zeit des **bestehenden Termins** durch. Würde `morgen` ihr folgen, schöbe „verschieb ihn auf morgen" einen Termin im August auf den Tag nach jenem Termin statt auf den Tag nach heute.

**Der Parameter trug zwei Bedeutungen.** Für relative Dauern ist `referenz` der Anker, für deiktische Tagesworte müsste es der Sprechzeitpunkt sein — und die beiden fallen nur im Live-Pfad zusammen. Die Ersatzlösung „Tagesworte nehmen die echte Uhr" war für den Betrieb richtig und für jede nachträgliche Verarbeitung falsch.

**Daraus die Regel, die über diesen Fall hinausreicht:**

> **Ein Parameter, der in zwei Aufrufkontexten Verschiedenes bedeutet, ist zwei Parameter.** Solange sie im Normalfall zusammenfallen, sieht die Verwechslung wie ein funktionierender Vorgabewert aus. Sie wird erst dort sichtbar, wo die beiden auseinanderlaufen — und das ist typischerweise die Wiederverarbeitung, nicht der Live-Pfad.

Der Beleg dafür, dass die Unterscheidung schon vorher gebraucht wurde: Der Härtefallkorpus **ersetzte für jeden Fall eine private Funktion** (`_heute_lokal`), weil der Parser keinen Weg hatte, den Sprechzeitpunkt entgegenzunehmen. Ein Monkey-Patch auf ein Privatsymbol ist die Form, die eine fehlende Schnittstelle annimmt. Seit es `sprechzeitpunkt` gibt, läuft der Korpus über die öffentliche Schnittstelle — bei unveränderten Zahlen: 49 erfüllt, 31 offen, 5 Lücken, 4 Regressionen.

---

→ Timeline-Modul: `02_M_e`
→ Thinker (nutzt timeline_check): `01_M_f`
