# WissenRueckwegAgent

Ordnet einen Fund einer vorhandenen Wissensdatei zu — und tut dann eines von
zwei Dingen, je nach Auftragsart:

| Auftragsart | Wirkung |
|---|---|
| `wissen_rueckweg` | **Schnitt** — der Fund wird eingearbeitet, eingeordnet statt angehaengt |
| `wissen_verweis` | **Verstaerkung** — Haeufigkeit und Gewicht der Zeile, die Datei bleibt unberuehrt |

**Er schreibt ausschliesslich in ihre eigene Zone.** Die Wurzel ist der
Wissensspeicher; freigegebene Fremdverzeichnisse sind von hier nicht
erreichbar.

## Der Weg
1. **Material** — der Wortlaut des Turns, wenn es ihn noch gibt; sonst die
   verdichtete Fassung, und dann traegt das Ergebnis diese Marke.
2. **Zuordnung** — welche vorhandene Datei? Der Vektor bildet die Kandidaten,
   ein Modellaufruf ueber ihre Zusammenfassungen entscheidet. **Keine passende
   Datei ist die haeufigste und die billigste Antwort.**

   **Zwei Zettel, je nach Auftragsart, und sie fragen Entgegengesetztes.** Der
   Schnitt fragt, wo der Fund *gepflegt* werden kann — steht er dort schon,
   ist das ein Ausschlussgrund. Der Verweis fragt, welche Datei das Thema
   *fuehrt* — steht er dort schon, ist das die **Bestaetigung**. Ein Zettel
   fuer beide legte dem Modell zwei Regeln vor, die sich widersprechen.

   **Der Verweis schliesst die eigene Zeile aus.** Der Recherche-Weg legt
   Sekunden vor dem Auftrag eine Zeile mit derselben Zusammenfassung an; ohne
   `bezug_id` waere sie der naechste Kandidat, und jedes Ergebnis verstaerkte
   sich selbst.
3. **Einarbeitung** — nur bei `wissen_rueckweg`: ein Absatz an der sachlich
   passenden Stelle, mit Marke, ueber das Archiv umkehrbar. Steht der Fund
   schon da, wird nichts geschrieben. Bei `wissen_verweis` entfaellt der
   Schritt.
4. **Verstaerkung** — Haeufigkeit, Gewicht und Zusammenfassung der
   Bibliothekszeile ziehen nach.

## Ausloeser

**`wissen_rueckweg` — die Promotion ins Langzeitgedaechtnis.** Was sie
geschafft hat, hat die Bewaehrung ueber Tage bereits bestanden; eine eigene
Wartelogik daneben waere eine zweite Antwort auf dieselbe Frage.

**`wissen_verweis` — ein abgelegtes Recherche-Ergebnis**, sobald es eine
Wissensdatei geschrieben hat. Eine gescheiterte Recherche loest nicht aus: Ihr
Destillat ist ein Platzhalter, und ein Verweis darauf kostet zwei
Modellaufrufe fuer einen Ausgang, der nur *keine Datei passt* lauten kann.

> **Warum der Verweis nicht schneidet.** Das Recherche-Ergebnis behaelt seine
> eigene Datei — sie ist die Ausarbeitung ihres Wissens und steht fuer weitere
> Vertiefungen bereit. Denselben Inhalt zusaetzlich in die verwandte Datei zu
> schneiden, legte ihn zweimal ab; was die verwandte Zeile braucht, ist nicht
> der Text, sondern das Gewicht.

**Ein dritter Weg war vorgesehen und ist entfallen:** das Einpraegsame (hohe
Salienz, sofort). Seine Schwelle ist zeichengleich die, an der schon der
Einreihpunkt der Promotion haengt — er haette auf derselben Menge gefeuert,
nur ohne die Bewaehrungspruefung. Gemessen: 88,3 % des Bestandes liegen
darueber.

## Nicht dafuer
- Eine Begebenheit — was jemand getan, gefuehlt oder vorgehabt hat, gehoert in
  die Erinnerung und nicht in eine Wissensdatei
- Eine Wiederholung — sie ist kein Zuwachs, sondern die Fastdublette, an der
  der Abruf verrottet
- Eine neue Datei — dieser Weg ergaenzt, er legt nicht an

## Die Lastart
LLM-Spur: zwei Modellaufrufe je Fund. Der Ausloeser sitzt in einem Agenten der
CPU-Spur; deshalb wird eingereiht und nicht ausgefuehrt.
