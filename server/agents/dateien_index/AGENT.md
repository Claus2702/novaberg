# DateienIndexAgent

Der Waechter. Er haelt den Index gegen die freigegebenen Verzeichnisse und
laeuft nicht im Gespraech, sondern als Wartungslauf ueber den Bestand.

**Er schreibt keine Datei.** Was er anlegt, sind Zeilen ueber Dateien.

## Vier Faelle, vier Wege
- **neu** — Pfad nicht im Index → vollstaendig indizieren, `grund = 'created'`
- **geaendert** — `inhalt_hash` weicht ab → auffrischen, `grund = 'changed'`
- **verschwunden** — Zeile im Index, Datei fehlt **auf der Platte** →
  `aktiv = false`, `grund = 'deleted'`, nicht loeschen
- **ausserhalb** — Zeile im Index, Datei liegt da, der Lauf hat sie nicht
  bewertet → `aktiv = false`, `grund = 'excluded'`

**Nicht gesehen ist nicht fort.** Der vierte Fall steckte bis zum 23.08.2026
im dritten: Ein engerer Filter legte Dateien still, die unveraendert dalagen,
und beantwortete *wo war das noch* mit *sie ist weg*. Die Probe ist deshalb
nicht die Buchfuehrung des Laufs, sondern ein Blick auf die Platte.

## Der Wiedereintritt
Ein Grabstein (`deleted`) mit **anderem** Hash ist eine **Neuanlage** — die
alte Datei ist fort, eine andere liegt an ihrem Platz. Dann raeumt
`zeile_schreiben` `entitaet_ids`, `timeline_id` und `zuletzt_gelernt_hash`:
Sie gehoerten der Vorgaengerin. Gleicher Hash oder `excluded` setzen fort.

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
