# DateienAgent

Beantwortet eine Frage aus den Verzeichnissen, die ein Mensch fuer eine Figur
freigegeben hat: finden, lesen, Fundstellen liefern.

**Er schreibt nichts, in keiner Zone.** Der Verbund importiert die lesenden
Module und nicht den Schreibpfad — ein Recht, das nicht im Modul liegt, kann
kein Prompt herbeireden.

**Warum es ihn gibt, ist gemessen.** Ohne ihn liefert der Weg ueber den
Enricher Thema und Zusammenfassung, nicht den Inhalt: Die Fundstelle stimmt,
die Auskunft daneben, und beides steht im selben Satz.

## Faehigkeiten
- Fundstelle suchen ("Steht irgendwo, wie die Salienz gerechnet wird?")
- Abschnitt lesen ("Lies mir den Abschnitt ueber die Baender vor")
- Wortlaut suchen ("Bei welcher Temperatur laeuft der Schruehbrand?")

## Trigger
- Bezug auf einen abgelegten Text — ein Dokument, eine Datei, eine Stelle darin
- Inhalt: "Was steht in ...", "Wie war das nochmal mit ..."
- Ort: "Steht das irgendwo", "Such mal in den Unterlagen nach ..."
- Eine Fachfrage, deren Antwort in einer Ablage stehen wuerde

## Nicht dafuer
- Weltwissen ohne Bezug auf Unterlagen — das ist Wissen, keine Fundstelle
- Etwas Erlebtes ("was habe ich dir letzte Woche erzaehlt") — das ist Gedaechtnis
- Die Bitte, etwas abzulegen — dieser Dienst schreibt nichts
- Die Freigabe eines Verzeichnisses als Ganzes — das ist eine Festlegung

## Grenzen
- Schreibt nichts, in keiner Zone
- Liefert keine Zusammenfassung ganzer Verzeichnisse
- Sucht nicht im Inhalt ohne vorherige Einschraenkung
- Kennt nur die freigegebenen Wurzeln des Paares

## Die drei Kanaele und die drei Stufen
Gesucht wird **scharf vor unscharf**: Name, dann Stichwort, dann Bedeutung. Der
Kosinus ordnet innerhalb der gefundenen Menge und entscheidet nicht ueber sie.

Gelesen wird in drei Stufen, und die Reihenfolge ist der Preis: Die **Karte**
steht im Index und kostet keinen Dateizugriff; der **Block** kostet einen; die
**Nadel** liefert die Zeilennummer und damit die Fundstelle im Wortlaut.

## Der vierte Ausgang
Eine Suche, die nichts findet, hat fast immer einen benachbarten Treffer, und
die Ablehnung traegt ihn: Befund, Beleg mit Zahlen, Vorschlag. Ein blankes
"nichts gefunden" liesse den Menschen im Unklaren, ob die Datei fehlt oder
seine Frage.
