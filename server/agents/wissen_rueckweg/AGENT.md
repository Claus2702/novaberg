# WissenRueckwegAgent

Arbeitet einen Fund aus dem Gespraech in eine vorhandene Wissensdatei ein —
eingeordnet, nicht angehaengt.

**Er schreibt ausschliesslich in ihre eigene Zone.** Die Wurzel ist der
Wissensspeicher; freigegebene Fremdverzeichnisse sind von hier nicht
erreichbar.

## Der Weg
1. **Material** — der Wortlaut des Turns, wenn es ihn noch gibt; sonst die
   verdichtete Fassung, und dann traegt das Ergebnis diese Marke.
2. **Zuordnung** — welche vorhandene Datei? Das Kriterium ist Pflegbarkeit,
   nicht Aehnlichkeit. Der Vektor bildet die Kandidaten, ein Modellaufruf
   ueber ihre Zusammenfassungen entscheidet. **Keine passende Datei ist die
   haeufigste und die billigste Antwort.**
3. **Einarbeitung** — ein Absatz an der sachlich passenden Stelle, mit Marke,
   ueber das Archiv umkehrbar. Steht der Fund schon da, wird nichts
   geschrieben.
4. **Verstaerkung** — Haeufigkeit, Gewicht und Zusammenfassung der
   Bibliothekszeile ziehen nach.

## Ausloeser
Die Promotion ins Langzeitgedaechtnis. Was sie geschafft hat, hat die
Bewaehrung ueber Tage bereits bestanden — eine eigene Wartelogik daneben waere
eine zweite Antwort auf dieselbe Frage.

**Zwei weitere Wege sind vorgesehen und nicht verdrahtet:** das Einpraegsame
(hohe Salienz, sofort) und das Zugehoerige. Beide sind je eine Zeile an ihrem
Einreihpunkt.

## Nicht dafuer
- Eine Begebenheit — was jemand getan, gefuehlt oder vorgehabt hat, gehoert in
  die Erinnerung und nicht in eine Wissensdatei
- Eine Wiederholung — sie ist kein Zuwachs, sondern die Fastdublette, an der
  der Abruf verrottet
- Eine neue Datei — dieser Weg ergaenzt, er legt nicht an

## Die Lastart
LLM-Spur: zwei Modellaufrufe je Fund. Der Ausloeser sitzt in einem Agenten der
CPU-Spur; deshalb wird eingereiht und nicht ausgefuehrt.
