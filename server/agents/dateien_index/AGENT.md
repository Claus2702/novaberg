# DateienIndexAgent

Der Waechter. Er haelt den Index gegen die freigegebenen Verzeichnisse und
laeuft nicht im Gespraech, sondern als Wartungslauf ueber den Bestand.

**Er schreibt keine Datei.** Was er anlegt, sind Zeilen ueber Dateien.

## Drei Faelle, drei Wege
- **neu** — Pfad nicht im Index → vollstaendig indizieren
- **geaendert** — `inhalt_hash` weicht ab → auffrischen
- **verschwunden** — Zeile im Index, Datei fehlt → `aktiv = false`, nicht loeschen

## Die Aenderungserkennung
`mtime` und Groesse sind der Vorfilter, der Inhalts-Hash ist die
Entscheidung. Ein Werkzeug kann eine Datei mit gleicher Zeit neu schreiben,
und ein Kopiervorgang aendert die Zeit ohne den Inhalt — eine
Neu-Indizierung kostet je Datei einen Modellaufruf.

## Grenzen
- Indiziert nur die konfigurierten Wurzeln, und der Aussenrand wird je Lauf
  erneut geprueft
- Text nach konfigurierter Endungsliste; alles andere wird **mit Grund**
  uebergangen und in der Bilanz genannt
- Hoechstens `DATEIEN_INDEX_MAX_PRO_LAUF` Dateien je Lauf — was stehenbleibt,
  steht als `offen` in der Bilanz und nicht im Schweigen

## Takt
**Keiner.** `periodic_task()` liefert None, bis die Aenderungsrate des
Verzeichnisses gemessen ist. Angestossen wird von Hand:

    POST /admin/dateien/index
