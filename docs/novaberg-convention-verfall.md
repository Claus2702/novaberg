# Novaberg — Verfall: Was als Gedächtnis dient, verfällt

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Convention — Verfall vorgehaltener Daten
**Stand:** 16. August 2026
**Pfad:** novaberg/docs/novaberg-convention-verfall.md
**Typ:** Convention

---

## 1. Die Regel

> **Was als Gedächtnis dient, verfällt. Was als Faktum protokolliert, bleibt.**

Vorgehaltene Daten unterliegen grundsätzlich einem Verfall: Ihr Gewicht sinkt über die Zeit, bis sie unter eine Schwelle fallen und ruhen. Das ist kein Aufräumen, sondern die Bauart des Gedächtnisses — was lange niemanden interessiert hat, soll nicht mehr so laut sein wie das Frische.

Zwei weitere Sätze sagen, **wo** der Verfall sitzt. Ohne sie ist die Regel nicht anwendbar, weil ein Speicher aus mehreren Tabellen besteht und nicht jede von ihnen ihn tragen darf.

### 1.1 Der Verfall sitzt dort, wo gesucht wird

Ein Speicher trägt den Verfall an der Stelle, über die seine **Suche** läuft.

- Im **Langzeitgedächtnis** läuft die Suche über die **Knoten** — also trägt `lzg_knoten` den Verfall, und `lzg_kanten` trägt ihn nicht.
- Im **Fakten-Gedächtnis** läuft die Suche nach einer ID über die **Kanten** — also gehört er dort an die Kante.

Der Grund ist mechanisch: Ein Verfall an einer Stelle, die nie durchsucht wird, ändert kein Ergebnis. Er wäre eine Zahl, die sinkt, ohne dass sie je jemand liest.

### 1.2 Die Trennlinie ist der Fremdschlüssel

**Eine Fakten-Entität, deren ID anderswo als Fremdschlüssel verwendet wird, verfällt nicht.** Ein verfallener oder deaktivierter Satz risse die Referenz.

**Die Bindung darauf darf verfallen.** Damit hängt der Verfall an der **Rolle der Zeile**, nicht an der Sorte des Speichers: Ziel eines Fremdschlüssels, Bindung, oder freier Inhalt.

> **Beides zusammen erklärt den scheinbaren Widerspruch bei `lzg_knoten`:** Fremdschlüssel zeigen darauf, und es verfällt trotzdem. Der Grund ist, dass es **keine Fakten-Entität** ist, sondern Gedächtnis. §1.2 nimmt Fakten aus, nicht Fremdschlüsselziele.

---

## 2. Geltungsbereich

**Erfasst:** jeder Speicher, der der Einbindung als Gedächtnis dient — Kurzzeit- und Langzeitgedächtnis, die Auftrags-Queue, die Metadaten über Dateien und Wissen, und die Bindungen zwischen Fakten.

**Ausdrücklich nicht erfasst:**

| Was | Warum |
|---|---|
| **Faktentabellen** — Termine, Entitäten | Ein Termin verblasst nicht. Er war, oder er wird sein. |
| **Forensik** — `pipeline_log` | Eine Protokollzeile, die an Gewicht verliert, wäre kein Protokoll. Sie hat stattdessen eine **Vorhaltefrist** — das ist etwas anderes: Die Zeile verschwindet ganz, statt unwichtig zu werden. |
| **Audit** — `hintergrund_log` | dasselbe |
| **Die Brücke Turn ↔ Gedächtnis** — `verbindung` | Ausdrücklich ohne Gewicht und Verfall: ein Tagebucheintrag verblasst nicht (`novaberg-charakter-resonanz_k.md` §12). |

**Die Ausnahmen sind Teil der Regel und nicht ihre Aufweichung.** Eine Regel ohne benannte Ausnahmen wird an der ersten Ausnahme gebrochen statt geändert.

---

## 3. Woran man einen Verstoß erkennt

Drei Formen, und die dritte ist die stille:

1. **Ein Gedächtnisspeicher ohne Verfallsgröße.** Er wächst, und alles darin bleibt gleich laut.
2. **Ein Verfall an der falschen Stelle** — an einer Tabelle, über die nicht gesucht wird. Er sinkt, ohne etwas zu ändern.
3. **Ein Verfall mit Spalten, aber ohne Lauf.** Die Struktur ist da, `decay_am` bleibt auf dem Einfügezeitpunkt stehen, und jede Auswertung liest einen Wert, der wie eine Messung aussieht. Das ist die teuerste Form, weil sie von außen wie Erfüllung aussieht.

---

## 4. Maschinelle Prüfbarkeit

**Teilweise — und die Grenze gehört zur Auskunft.**

Diese Abfrage liefert je Tabelle, ob sie eine Verfallsgröße führt, ob sie einen Lauf hat, und ob ein Fremdschlüssel auf sie zeigt:

```sql
SELECT c.table_name,
       bool_or(c.column_name LIKE '%_decay') AS hat_decay,
       bool_or(c.column_name = 'decay_am')   AS hat_lauf,
       EXISTS (SELECT 1 FROM information_schema.constraint_column_usage u
               JOIN information_schema.table_constraints t
                 ON t.constraint_name = u.constraint_name
               WHERE t.constraint_type = 'FOREIGN KEY'
                 AND u.table_name = c.table_name) AS ist_fk_ziel
FROM information_schema.columns c
WHERE c.table_schema = 'public'
GROUP BY c.table_name ORDER BY 4 DESC, 2 DESC, 1;
```

**Was sie nicht kann:** Sie unterscheidet nicht Gedächtnis von Faktum. Genau diese Einordnung ist das Urteil, und sie ist nicht aus dem Schema ablesbar — `timeline` und `shadow_auftrag` sehen einer Abfrage gleich aus.

**Die Abfrage grenzt also ein, sie entscheidet nicht.** Ihre Ausgabe ist eine Kandidatenliste; die Zuordnung steht in §5 und wird dort gepflegt.

---

## 5. Der Bestand — Zustandssätze

> ⚠ **Dieser Abschnitt beschreibt, er legt nicht fest.** Er wird nachgezogen, wenn sich der Code ändert. Die Regel steht in §1 bis §3; hier steht nur, wie weit sie heute eingelöst ist. Wer diesen Abschnitt für bindend hält, hat die Sorte verwechselt.

`[gemessen]` — 16. August 2026:

| Tabelle | Rolle | Verfall | Lauf | Beurteilung |
|---|---|---|---|---|
| `lzg_knoten` | Gedächtnis, Suchort | ✅ | ✅ Sweep, täglich | konform |
| `shadow_auftrag` | Gedächtnis | ✅ | ✅ Sweep, täglich | konform (seit 15.08.2026) |
| `autonomous_wissen` | Gedächtnis-Metadaten | ✅ | ✅ träge, beim Anfassen | konform |
| `lzg_kanten` | Bindung | ❌ | — | **konform** — der Knoten trägt ihn, §1.1 |
| `entitaeten` | Fakten-Entität, FK-Ziel | ❌ | — | **konform** — §1.2 |
| `timeline` | Fakten-Entität, FK-Ziel | ❌ | — | **konform** — §2 |
| `pipeline_log` · `hintergrund_log` | Forensik, Audit | ❌ | — | **konform** — §2 |
| `verbindung` | Brücke | ❌ | — | **konform** — §2, ausdrücklich |
| `fakten` | **Bindung** zwischen zwei `entitaeten` | ❌ | — | **offen** → `FAKTEN-BINDUNG-OHNE-VERFALL` |
| `notizen` | freier Gedächtnisinhalt, kein FK zeigt darauf | ❌ | — | **offen** → `FACHSPEICHER-AGENTEN` |

**Zwei Bauarten des Laufs, beide zulässig:** ein **Sweep** über alle Zeilen im Tageslauf (`lzg_knoten`, `shadow_auftrag`) oder **träge** beim Anfassen einer Zeile (`autonomous_wissen`). Erkennbar an `decay_am`: Ein Sweep hinterlässt ein bis zwei Datumswerte über den ganzen Bestand, ein träger Lauf viele.

---

## 6. Erwogene Alternativen

| Verworfen | Warum |
|---|---|
| **Hartes Löschen unter der Schwelle** | Ein Gedanke wäre unwiederbringlich weg. Stattdessen Soft-Delete nach LZG-Vorbild: `aktiv = FALSE`, weckbar über die Halbreaktivierung. Den Ausschlag gab ein Bestandsbefund — 233 Aufträge auf Salienz 0,0, deren Null ein Schreibfehler war und kein schwacher Anlass. **Seit dem 23.08.2026 gilt dasselbe für den Fehlversuchspfad**, der bis dahin ausdrücklich ausgenommen war: Ein Ausführungsfehler ist formal kein Verfall, aber der Verfall entfernte weich, was niemanden interessiert, und der Fehlversuch hart, was am meisten interessiert. Beide Pfade legen still, und die Spalte `grund` trennt sie (`F-STILLLEGUNG-1`). |
| **Verfallsrate gestaffelt nach Salienz** | Eine zweite Kurve neben der ersten. Eine einzige Rate leistet dasselbe, weil ein schwächerer Eintrag von einem niedrigeren Anker startet und deshalb früher unten ankommt. |
| **Mengengrenze je Speicher** | Verwürfe nach **Zahl** statt nach **Dringlichkeit**. Wächst ein Bestand über das Erträgliche, wird stattdessen die Verfallsrate verstärkt. |
| **Verfall auch auf Faktentabellen** | Ein Termin, der an Gewicht verliert, ist kein Termin mehr. Und bei Fremdschlüsselzielen risse ein deaktivierter Satz die Referenz (§1.2). |

Herleitung und Messwerte: `novaberg-queue-verfall_k.md` §11–§16, `novaberg-memory-synapsen_k.md` §9.

---

## Versionshistorie

- **v0.1 — 16.08.2026:** Erstfassung. Die Regel war seit Langem Praxis — drei Speicher folgen ihr, mit zwei verschiedenen Bauarten des Laufs —, aber sie stand in keinem Dokument und galt deshalb nur dort, wo jemand an sie dachte. Zwei Sätze machen sie erst anwendbar und sind beide neu formuliert: **der Verfall sitzt, wo gesucht wird** (§1.1, erklärt `lzg_kanten` ohne Verfall als konform statt als Lücke) und **die Trennlinie ist der Fremdschlüssel** (§1.2, Entität bleibt, Bindung darf verfallen). Beim ersten Anlegen der Bestandstabelle warf die Regel zwei offene Stellen aus: `fakten` als Bindung ohne Verfallsgröße und `notizen` als freier Inhalt ohne jede.
