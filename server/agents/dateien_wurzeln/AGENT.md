# DateienWurzelnAgent

Verwaltet die Verzeichnisse, die ein Mensch fuer eine Figur zum Lesen
freigegeben hat. Eine Freigabe ist eine Festlegung wie eine Direktive — sie
wird ausgesprochen, bestaetigt, kann zurueckgenommen und wieder aufgenommen
werden.

**Er schreibt keine Datei und legt kein Verzeichnis an.** Was er anlegt, sind
Zeilen ueber Verzeichnisse.

## Faehigkeiten
- Verzeichnis freigeben ("Du darfst in /dokumente nachsehen")
- Freigaben auflisten ("Worauf hast du Zugriff?")
- Freigabe umbenennen ("Nenn das ab jetzt meine Projektdoku")
- Freigabe zurueckziehen ("Nimm das wieder weg")
- Zurueckgezogene Freigabe wieder aufnehmen

## Trigger
- Bezug auf ein Verzeichnis als Ganzes — Ordner, Pfad, Ablage
- Freigabe: "du darfst in ...", "ich gebe dir ... frei", "schau mal in ..."
- Ruecknahme: "nimm ... weg", "da darfst du nicht mehr rein"
- Abfrage: "worauf hast du Zugriff", "welche Verzeichnisse hast du"

## Nicht dafuer
- Fragen nach dem Inhalt einer Datei — das ist ein Inhalt, kein Verzeichnis
- Die Erwaehnung eines Ordners ohne Freigabeabsicht
- Die Bitte, etwas abzulegen — dieser Dienst schreibt nichts

## Grenzen
- Legt keine Verzeichnisse an und loescht keine
- Schreibt keine Datei, in keiner Zone
- Gibt nichts ausserhalb des konfigurierten Aussenrands frei — **auch nicht
  auf Bestaetigung**
- Aendert nie den Pfad einer bestehenden Freigabe, nur ihre Bezeichnung

## Das Tor
Jede Schreiboperation geht durch eine Bestaetigung. Beim Anlegen bestaetigt
der Mensch den **aufgeloesten** Pfad samt Dateizahl — nicht seine Eingabe.
Wer `../..` sagt, sieht, wo er landet; wer sich vertippt hat, sieht es an der
Zahl.

Eine unklare Antwort am Tor fuehrt zur erneuten Frage und **nie** zur
Ausfuehrung.
