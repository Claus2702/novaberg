# WissenAgent

Beantwortet eine Frage aus dem, was sie sich selbst erarbeitet hat: die
eigene Bibliothek befragen, Thema und Zusammenfassung liefern, die Fundstelle
dazu.

**Er schreibt nichts.** Die Bibliothek wird von den Hintergrund-Agenten
gefuellt, nicht aus dem Gespraech. Das Modul importiert die Lesepfade des
Repositoriums und nicht `speichern` — ein Recht, das nicht im Modul liegt,
kann kein Prompt herbeireden.

**Warum es ihn gibt.** Bis zum 19.08.2026 war die Bibliothek angebunden wie
ein Gedaechtnis: Sie floss bei jedem Turn bei, und niemand konnte sie
bestellen — weder der Mensch noch sie selbst. Von neun Silos trug ihr eigenes
erarbeitetes Wissen genau eine der drei Rollen, und es war das am
schlechtesten angebundene.

## Faehigkeiten
- Die eigene Bibliothek zu einem Thema befragen
- Den Bestand beziffern ("wozu habe ich ueberhaupt gearbeitet")

## Trigger
- Bezug auf EIGENE, vorher erarbeitete Durchdringung eines Themas
- "Was hast du selbst zu ... herausgefunden?"
- "Kennst du dich mit ... aus?", "Weisst du was ueber ...?"
- "Hast du zu ... schon was zusammengetragen?"

## Nicht dafuer
- Der Inhalt eines vom Menschen abgelegten Schriftstuecks — fremdes Material
- Etwas Erlebtes ("was habe ich dir letzte Woche erzaehlt") — Erinnerung
- Die Bitte, etwas Neues herauszufinden — hier liegt nur Erarbeitetes
- Die Bitte, etwas abzulegen — dieser Dienst schreibt nichts

## Grenzen
- Liefert Thema und Zusammenfassung, **nicht den Wortlaut** der Ausarbeitung
- Schreibt nichts, in keiner Zone
- Sucht nur ueber die Bedeutung; es gibt keinen Wortkanal
- Kennt nur die Ausarbeitungen dieses Paares

## Eine Suche, zwei Eingaenge
Die Abfrage liegt im Repository und wird von der Quelle und von diesem Dienst
benutzt. Zwei Abfragen ueber denselben Bestand ergaeben zwei Rangfolgen, und
die Abweichung fiele erst auf, wenn jemand dieselbe Frage zweimal stellt.
Dieser Eingang waehlt allein die **Tiefe**, nicht die Ordnung.

## Der vierte Ausgang
Die Quelle kann nur beitragen oder schweigen, und Schweigen ist keine
Antwort: *"dazu habe ich nichts"* und *"dazu habe ich nicht nachgesehen"*
sehen im Gespraech gleich aus. Die Ablehnung traegt deshalb eine Zahl — wie
viele Ausarbeitungen durchsucht wurden und wie nah die knappste lag.
