# TimelineAgent

Verwaltet temporale Eintraege: Termine, Geburtstage, Deadlines, Erinnerungen, Jahrestage.
Bi-temporales Modell: Verschieben invalidiert den alten Eintrag und legt einen neuen an.
Zeitparser fuer natuerlichsprachliche Datumsangaben (deutsch).

## Faehigkeiten
- termin_erstellen: Neuen Termin/Event anlegen (Titel, Datum, Typ, Details)
- termin_lesen: Termine per Zeitraum, Stichwort oder Entitaet finden
- termin_verschieben: Bestehenden Termin auf neues Datum setzen (bi-temporal)
- termin_loeschen: Termin invalidieren (Soft-Delete, aktiv=FALSE)

## Trigger
- "trag ein", "merk dir den Termin", "Zahnarzt am Donnerstag"
- "verschieb den Termin", "sag den Termin ab", "loesch den Termin"
- "wann ist nochmal", "was steht an", "welche Termine habe ich"
- Kontext-Bezug: Gespraechsverlauf enthaelt aktiven Termin und User bezieht sich darauf

## Entitaeten
Nutzt den shared Entity-Resolution-Subgraph (agents/shared/entity_resolution/)
fuer Personen und Orte in Terminen ("Termin mit Stefan", "Zahnarzt in Muenchen").

## Typ
Workflow (Typ 1) — deterministische Schrittfolge, LLM fuer Klassifikation und Zeitextraktion.
