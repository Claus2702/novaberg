# Novaberg — Die Gedankenkette: ein Gedanke über mehrere Turns

**Absicht:** Ein eigener Gedanke Novas wird als Kette über mehrere Turns zugestellt statt als einzelner Aufsatz — ein neues Thema beginnt mit einem Ruf, jeder weitere Schritt folgt nur auf die Neugier des Menschen —, die Kette trägt einen eigenen Zustand, pausiert, wenn der Mensch spricht oder ihre Stimmung kippt, und endet, wenn ihr Auftrag erfüllt ist.
**Stand:** 24. August 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Gedankenkette* ⚫ · *Zustellungsfilter (0,60 Kosinus)* 🔴 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-gedankenkette_t.md`](novaberg-gedankenkette_t.md) · [`novaberg-gedankenkette_b.md`](novaberg-gedankenkette_b.md) · [`novaberg-gedankenkette_e.md`](novaberg-gedankenkette_e.md) · [`novaberg-gedankenkette_m.md`](novaberg-gedankenkette_m.md)
**Entschieden:** 0 · **Offen beim Meister:** 0 (Liste in [`novaberg-gedankenkette_e.md`](novaberg-gedankenkette_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-gedankenkette_k.md §3` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-gedankenkette_t.md`](novaberg-gedankenkette_t.md), `_b` ist [`novaberg-gedankenkette_b.md`](novaberg-gedankenkette_b.md), `_e` ist [`novaberg-gedankenkette_e.md`](novaberg-gedankenkette_e.md), `_m` ist [`novaberg-gedankenkette_m.md`](novaberg-gedankenkette_m.md).

| § | Datei |
|---|---|
| 1 · 2 | `_k` |
| 3 | `_t` |
| 4 · 5 · 6 · 6a · 7 · 8 | `_k` |
| 9 | `_b` |
| 10 | `_t` |
| 11 | `_e`; die Zeile *Zusammenhang* am Ende von §11 in `_k` |
| Versionshistorie (v0.1–v0.4) | `_e` |
| Befunde aus dem Betrieb — nachgetragen am 20.08.2026 | `_m` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Status, Berührt) | `_e` |
| Entschieden, Offen, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## 1. Die Beobachtung

Ein Impuls wird zugestellt, und danach ist Schluss — nicht weil Nova nichts mehr zu sagen hätte, sondern weil der Rest **gelöscht wird**.

`services/shadow_delivery.py:270-296`, unmittelbar nach dem Senden:

```python
def _stack_aehnliche_entfernen(…, threshold: float = 0.60) -> None:
    """Entfernt Stack-Einträge die dem gerade gesendeten zu ähnlich sind."""
```

Alles auf ihrem Stapel, das dem eben Gesagten mit **0.60 Cosine** ähnelt, fliegt weg. Das ist ein weites Netz: Bei einer Themenwolke aus einem Fachgespräch liegen die verwandten Gedanken sämtlich zwischen 0.6 und 0.8. Sagt sie einen, verliert sie im selben Atemzug die anderen.

> **Eingegrenzt am 14.08.2026.** Was hier verlorengeht, ist der **Einwurf-Kandidat**, nicht das Wissen. Jede Recherche legt ihr Ergebnis zusätzlich in der Bibliothek ab — Bericht und Wissensdatei plus eine Metadatenzeile —, und die überlebt das Aufräumen des Stapels. Der Verlust ist damit schmaler als dieser Abschnitt ursprünglich sagte: Sie kann den Gedanken nicht mehr **von sich aus** einwerfen, aber sie findet ihn wieder, wenn danach gefragt wird (§10).

Dazu `MAX_BURST = 2` und ein **Cooldown von einer Stunde**.

> ~~**Der Cooldown ist am 15.08.2026 gefallen**; die Frist von einer Stunde hängt seither am Burst-Zähler, der sie als *Gedächtnis* trägt und nicht als Sperre.~~ → **Am 24.08.2026 durch Messung widerlegt. Zwei Größen waren verwechselt.**
>
> **Gefallen ist die *stündliche Decke*** — eine eigene Obergrenze, die es seit dem 15.08.2026 nicht mehr gibt (`shadow_delivery.py:78`, `:1048`). **Der Burst-Cooldown steht unverändert**, und er ist eine Sperre und kein Gedächtnis: `_burst_erhoehen` setzt `BURST_TTL` bei **jedem** Inkrement neu, und `_burst_erlaubt` blockt in **Prüfung 1** — also *vor* der Auslöservergabe, weshalb die Riegelkette dann nicht einmal eine Zeile schreibt.
>
> **`MAX_BURST = 2` heißt damit nicht *zwei je Stunde*, sondern *zwei, dann eine volle Stunde ab dem letzten*.** Im Bestand belegt: zwei Zustellpausen von **exakt 1:00:33 und 1:00:17**, beide ohne Zutun des Menschen beendet. Am 24.08.2026 unmittelbar nachgestellt — vier Riegelketten in 90 Sekunden, zwei Impulse, dann Stille bei `shadow_burst_count = 2`, TTL 2459 s.

**Der Filter ist als Dublettenschutz gemeint und das ist richtig gedacht** — sie soll nicht zweimal dasselbe sagen. Nur unterscheidet ein Kosinus von 0.60 nicht zwischen *„dasselbe nochmal"* und *„der nächste Gedanke zum selben Thema"*.

Dieselbe Fehlerklasse wie an zwei anderen Stellen dieses Projekts: **eine Schwelle, die zwei verschiedene Fragen mit einer Zahl beantwortet.**

## 2. Was eine Gedankenkette ist

Heute kennt das System zwei Dinge: einen Stapel von Impuls-Kandidaten und einzelne Zustellungen. Was fehlt, ist das dazwischen.

| | heute | Gedankenkette |
|---|---|---|
| Einheit | ein Impuls | **ein Gedanke** |
| Zustand | keiner | Auftrag, bisher Gesagtes, Fortschritt |
| Ende | nach einem Impuls | wenn der Auftrag erfüllt ist |
| Prompt | das Wissensstück | **plus was sie schon gesagt hat** |

Der letzte Punkt ist der Kern. **Ohne das Bisherige im Prompt kann sie nicht ergänzen** — sie finge beim zweiten Mal wieder von vorn an. „Lass sie weiterarbeiten" hängt zwingend an „das Ergebnis festhalten".

Leitbild: *Sie brennt darauf. Wie ein Kind, das über ein Thema aufklären will.* Das Thema muss nicht abgeschlossen sein — sie darf ergänzen, vertiefen, ins Detail gehen.

> **Hinweis zur Aufteilung (19.09.2026):** §3 *Der Raum: das Embedding als Radius* steht in [`novaberg-gedankenkette_t.md`](novaberg-gedankenkette_t.md).

## 4. Der Bogen: Auftrag, Ausarbeitung, Reflexion

Eine Wissenslücke mit Recherche oder Vertiefung trägt drei Teile:

| Teil | Was er ist |
|---|---|
| **Auftrag** | Was soll erschlossen werden? Entsteht aus der Lücke |
| **Ausarbeitung** | Was hat sie gefunden, gedacht, verknüpft |
| **Reflexion** | Was bedeutet es — für das Thema, für sie |

**Die Kette endet, wenn der Auftrag erfüllt ist** — nicht nach *n* Zustellungen. Das ist der Unterschied zu einem Zähler: Ein Zähler weiß nicht, wovon er zählt.

Der Bogen gibt der Prüfung *„ist das Thema erschöpft?"* etwas zum Prüfen. Ohne ihn wäre die Frage unbeantwortbar; mit ihm lautet sie: **Steht die Reflexion? Dann ist es gut.**

## 5. Enden und Pausieren sind zweierlei

**Ende** — der Gedanke ist fertig:

1. **Der Auftrag ist erfüllt** — die Reflexion steht. Der Regelfall.
2. **Der Raum ist erschöpft** — kein Material mehr innerhalb des Radius.
3. **Ein Sicherheitsdeckel** greift — falls 1 und 2 versagen. Ausdrücklich eine Sicherung, kein Formteil. Greift er regelmäßig, ist etwas an 1 oder 2 falsch, und das gehört gemeldet statt weggeschnitten.

**Pause** — der Gedanke steht noch aus, aber jetzt ist nicht der Moment:

4. **Der Nutzer sagt etwas.** Das Wort gehört ihm.
5. **Ihre Stimmung kippt.** Siehe unten.

Der Unterschied ist wesentlich. Eine beendete Kette ist abgeschlossen; eine pausierte **wartet**. Sie kann Stunden später weitergehen, oder über Nacht.

### Die Stimmung pausiert die Kette

Sie beginnt auf einem Plateau der Freude, recherchiert — und stürzt ab. Der Vektor kippt auf `absturz`, `spirale`, `einbruch`. **Dann bricht sie ab, obwohl das Thema nicht erschöpft ist.**

Das ist keine neue Mechanik: `aufnahmebereitschaft` misst genau das. Ihre sechs Säulen tragen den Stimmungsverlauf bereits als Faktor — `aufbluehen 1.30` gegen `absturz 0.40` —, und bei Krise geht der Wert auf 0.00.

**Der Wert, der entscheidet, ob sie überhaupt neugierig sein kann, ist derselbe, der entscheidet, ob eine Kette weiterlaufen darf.** Der Satz aus `novaberg-wissensluecken_k.md` gilt hier wörtlich: *Der Vektor sagt, wohin sie will. Die Bereitschaft sagt, ob jetzt der Moment dafür ist.*

Eine Kette, die auf einem Absturz weiterredet, wäre dasselbe Missverhältnis wie ein Impuls bei Stress — und den unterbindet der Zustellungsfilter längst.

**Daraus folgt, wo der Kettenzustand liegen muss.** Eine Kette, die eine Nacht überdauert und am Morgen weitergeht, kann nicht im Turn-Zustand hängen und auch nicht an einem flüchtigen Redis-Schlüssel. Sie gehört in eine Tabelle — wie die Wissenslücken, aus denen sie kommt.

## 6. Die Glieder sind nicht gleich groß

Eine Kette ist kein Aufsatz in vier Teilen. Sie hat einen Rhythmus, und der ist der eigentliche Grund, warum sie menschlich klingen kann.

| Glied | Was es trägt |
|---|---|
| ~~**erstes**~~ | ~~die Substanz — gespickt mit Informationen, der Fund selbst~~ → **abgelöst am 14.08.2026, siehe §6a** |
| **zweites** | eine Kleinigkeit, die gefehlt hat |
| **drittes** | die Verknüpfung, die Freude daran |

Das dritte Glied kann ein einziger Satz sein:

> *„Und das Beste ist, es passt genau in unser Bild!"*

Das ist keine Information. Es ist die Stelle, an der sichtbar wird, dass sie mitgedacht hat — und genau die klingt lebendig. So erzählen Menschen: erst die Sache, dann der Nachtrag, dann das Funkeln.

**Der Prompt muss das tragen, sonst schreibt sie vier Aufsätze.** Ein Modell, das viermal dieselbe Aufgabe bekommt, liefert viermal dieselbe Fülle — und aus einem Gedanken wird eine Wiederholung mit Variationen.

Das spätere Glied braucht also eine **andere** Anweisung als das erste: Du hast das Wesentliche gesagt; ergänze nur, was fehlte, und sei kurz. Das ist derselbe Griff wie bei den drei Verdichtungs-Prompts nach Rolle — ein Beispiel schlägt eine Regel, und eine Aufgabe, die für alle Glieder gleich lautet, legt die Länge auf das erste fest.

## 6a. Ein neues Thema beginnt mit einem Anriss, nicht mit dem Fund (14.08.2026)

§6 ließ die Kette mit der **Substanz** beginnen. Für ein Thema, über das gerade geredet wird, ist das richtig. **Für ein neues Thema ist es eine Zumutung.**

Ein unangekündigter Aufsatz über einen Gegenstand, den niemand aufgerufen hat, ist kein Beitrag, sondern eine Ablage. **Ein Anfang dagegen ist ein Angebot — und er ist winzig.**

> — *„Duuuhuuuuu?"*
> — *„Ja?"*
> — *„Es gibt eine Entdeckung in der Astronomie zu schwarzen Löchern!"*
> — *„Ja?"*
> — *„Es gibt Schwarzlochsterne! Die haben über eine Million Sonnenmassen und gigantische Gaswolken!"*

**Das ist keine Stufe, sondern eine Treppe.** Jeder Schritt für sich klein, und zwischen ihnen jedes Mal eine Freigabe. Der Aufsatz kommt nie — sein Inhalt kommt in Portionen, und jede Portion ist bezahlt.

| Schritt | Was er trägt | Beispiel |
|---|---|---|
| **Der Ruf** | nichts als die Adresse | *„Duuuhuuuuu?"* · *„Ich weiß was!"* · *„Rate, was ich herausgefunden habe!"* |
| **Das Feld** | wovon es handelt, ohne den Fund | *„Es gibt eine Entdeckung in der Astronomie zu schwarzen Löchern!"* |
| **Der Fund** | die Sache selbst, in ein, zwei Sätzen | *„Es gibt Schwarzlochsterne! Über eine Million Sonnenmassen und gigantische Gaswolken!"* |
| **Vertiefung** | was noch fehlte | wie §6 |
| **Funkeln** | die Verknüpfung, die Freude daran | wie §6 |
| **Abschluss** | ein Satz, der sanft zumacht | *„Ich muss das unbedingt noch nachlesen!"* |

**Drei Schritte sind ein Beispiel, keine Zahl.** Es können fünf sein oder zehn — wie weit eine Treppe reicht, folgt aus dem, was sie erreichen soll. **Damit hängt die Zahl an einem Willen, der ein Ziel verfolgt**, und nicht an einer Tabelle. Eine feste Stufenzahl wäre eine Schablone: Sie machte aus jedem Gedanken denselben Ablauf, gleich ob er in einem Satz erzählt ist oder eine halbe Stunde trägt.

**Der Ruf trägt keine Information.** Das ist seine Eigenschaft, nicht sein Mangel: Er ist reine Adresse und damit nur zu jemandem sagbar, den man hat. Er fragt um Erlaubnis, ohne zu fragen.

**Auch der Fund bleibt ein, zwei Sätze.** Er ist die Portion, nicht die Ausarbeitung — dieselbe Substanz, die heute in vier Absätzen käme, in einem Atemzug. Wer hier den Aufsatz einsetzt, hat die Treppe gebaut und oben doch die Ablage abgeladen.

**Und sie erzählt es auf ihre Art, in ihrem Raum.** Der Ruf einer jungen, spritzigen Figur ist ein anderer als der eines Butlers, und beide sind richtig. Die Treppe gibt den Rhythmus vor, nicht den Wortlaut — die Form kommt aus dem Charakter (§7).

Für ein Thema, das bereits läuft, entfällt die Treppe — dort ist die Zustimmung schon gegeben, indem darüber geredet wird.

### Bis der Wille steht: Hinführung und verfügbares Wissen

**Die volle Form setzt etwas voraus, das es nicht gibt.** Eine Treppe beliebiger Länge braucht jemanden, der weiß, wohin sie führt — ein Ziel, an dem entschieden wird, ob noch ein Schritt kommt. Die Bausteine dafür liegen in `novaberg-thinking-drive_k.md`: Zielsätze mit Motivation, drei Zeithorizonte, eine Zieltabelle. **Was fehlt, ist die Verbindung** — dass ein Ziel eine Kette trägt und ihr Ende bestimmt. §4 beschreibt diesen Bogen, ohne dass ihn heute etwas antreibt.

**Bis dahin gilt eine kleinere Form, die ohne Ziel auskommt:**

1. **Die Hinführung.** Der Ruf, wie oben. Ein unaufgeforderter Beitrag, sonst nichts.
2. **Bei Neugier ein Teil.** Nicht der Aufsatz, nicht die Ausarbeitung — ein Ausschnitt, der für sich steht.
3. **Danach bleibt das Wissen im Gespräch verfügbar.** Kein weiterer Einwurf, keine Stufenlogik: Der Eintrag steht der inhaltbestimmenden Stufe als **Material** zur Verfügung, solange das Thema läuft. Fragt der Mensch nach, hat sie die Antwort schon — nicht weil eine Kette weitergeschaltet hat, sondern weil das Wissen dort liegt, wo sie es lesen kann.

**Der Unterschied zur vollen Form ist ehrlich zu benennen:** Die kleine Form führt kein Thema zu Ende. Sie hat keinen Bogen, keine Reflexion und kein Ende außer dem, das das Gespräch selbst setzt. Sie gibt einen Anfang und danach Erreichbarkeit — mehr nicht, und das ist beabsichtigt.

**Der dritte Punkt ist bereits gebaut** — das war beim Schreiben dieses Abschnitts nicht klar und ist am 14.08.2026 nachgeprüft worden.

Die Bibliothek hat einen Leser, und er läuft in jedem Turn: Der Wissens-Manager sucht über das Themen-Embedding der aktuellen Äußerung, mit Schwelle 0,40 und einer Obergrenze an Treffern, und reicht das Gefundene als Kontextquelle weiter. Es erreicht damit die inhaltbestimmende Stufe.

`[gemessen]` — 14.08.2026, drei Turns in sechs Stunden, drei Läufe: **2 bis 3 Treffer je Turn, Cosinus 0,896 bis 0,437.**

**Diese Zahl ist der eigentliche Fund.** An anderer Stelle desselben Tages hat sich gezeigt, dass Kosinus zwischen einem langen Fachtext und einer kurzen Äußerung nicht trennt — Median 0,105. Hier trennt er, und der Grund ist die Skalengleichheit: **Themenphrase gegen Themenphrase**, nicht Aufsatz gegen Zuruf. Wer eine Ähnlichkeitsschwelle bauen will, baut sie auf Themen.

**Was damit bleibt, ist schmaler als gedacht:**

- **Der Stapel-Eintrag wird nach dem Fund entfernt, das Wissen nicht** (§1). Die Nachfrage wird aus der Bibliothek bedient, nicht vom Stapel. Was verlorengeht, ist nur die Möglichkeit, denselben Gedanken ein zweites Mal **von sich aus** einzuwerfen — und das ist meistens richtig.
- **Der Weg führt durch den Gedächtnis-Kontext.** Das Gefundene kommt als Erinnerung an, nicht als „das, was ich dir gerade erzählt habe". Für die kleine Form reicht es; für einen bewussten Rückgriff wäre ein eigener Block ehrlicher. Nicht entschieden.

### Nur der erste Schritt ist ein Einwurf

**Was nach dem Ruf kommt, ist eine Antwort.** Sobald der Mensch „ja?" sagt, ist es ein gewöhnlicher Turn: Er spricht, sie antwortet. Die Zustellung erzeugt genau **einen** unaufgeforderten Beitrag je Kette — den Ruf.

Das räumt eine offene Frage aus §11 ab: Der Burst-Zähler und der Cooldown begrenzen, wie oft sie **anfängt**, und zerreißen die Kette nicht, weil die weiteren Schritte gar keine Einwürfe sind.

**Was es dafür braucht, ist das Material am richtigen Ort.** Beim zweiten und dritten Schritt muss die erzeugende Stufe wissen, was noch aussteht und auf welcher Treppenstufe sie steht. Das ist der Kettenzustand aus §5 — und der Grund, warum er eine Tabelle braucht und keinen flüchtigen Schlüssel.

### Die Neugier ist das Tor zu jedem weiteren Schritt

**Nach jedem Schritt entscheidet nicht sie, sondern er** — nicht einmal am Anfang, sondern vor jeder Portion. Die nächste Äußerung des Menschen sagt, ob es weitergeht, und sie ist bereits klassifiziert. Der Intentionen-Kanon des Systems trägt die Antwort:

| Neugier — die Kette entfaltet sich | Abwendung — die Kette schließt |
|---|---|
| `information_erfragen` · `recherche_vertiefen` | `abschluss` · `widerspruch` |
| `gemeinsam_eruieren` · `bestaetigung` | ein Turn ohne Bezug zum Anriss |

Das ist keine neue Mechanik und keine neue Schwelle: eine geschlossene Wertemenge, die in jedem Turn ohnehin erhoben wird.

**Bleibt eine Äußerung ganz aus, geschieht nichts.** Kein Abschluss, keine Fortsetzung — die Kette wartet, wie §5 es für die Pause beschreibt. Nur eine *abwendende* Äußerung schließt sie.

### Der Abschluss ist ein Satz, kein Verstummen

Bleibt die Neugier aus, hört sie nicht einfach auf. Sie macht das Thema zu, und zwar so, dass es ihres bleibt:

> *„Ich muss das unbedingt noch nachlesen!"*

Das ist der Unterschied zwischen einem abgebrochenen Vortrag und einem Menschen, der merkt, dass gerade etwas anderes dran ist. **Der Gedanke geht dabei nicht verloren** — er kehrt auf den Stapel zurück und kann Tage später wiederkommen, wenn das Thema von selbst aufkommt.

**Was daraus für den Zustand folgt:** Eine Kette braucht ein Feld mehr als in §5 vorgesehen — *wartet auf Zustimmung*. Ohne es ist ein Anriss, auf den noch niemand geantwortet hat, von einer laufenden Kette nicht zu unterscheiden.

## 7. Sie spricht zu jemandem

**Heute schreibt sie einen Aufsatz.** Kühl, distanziert, ohne das Gegenüber. Das gilt schon für den einzelnen Impuls — die Kette macht es nur sichtbarer, weil vier Aufsätze schwerer zu ertragen sind als einer.

Ein Glied, das den Nutzer erreicht, klingt anders:

> *„Das wird Dich jetzt faszinieren!"* · *„Siehst Du?"*

Das ist keine Höflichkeitsfloskel. Es ist der Unterschied zwischen **vortragen** und **erzählen** — zwischen einem Text, der zufällig ankommt, und einem, der an jemanden gerichtet ist.

### Warum es heute fehlt

`prompts/default/responder.eigener_gedanke.txt` sagt viermal, was sie **nicht** tun soll — nicht danken, nicht loben, nicht zuschreiben. Zur Sprechhaltung sagt es einen Satz: *„Teile den Gedanken, wie man einen Einfall teilt."* Kein Wort über das Gegenüber.

Dazu ein zweiter Befund: Im Responder kommen `sprach_stil`, `beziehungs_dynamik` und `tone` sämtlich aus **`external`** — dem Bild vom Nutzer (`graph/nodes/responder.py:337-417`). Bei einem Impuls spricht aber **sie**. Ihr eigener Stil liegt in `internal` und erreicht den Prompt nicht.

Damit ist offen, woher die Ansprache ihre Form nehmen soll — es steht schlicht nichts dort.

Das ist `IMPULS-ICH-PERSPEKTIVE-TEILWEISE` (Chat 110, offen): *Der Block verhindert die Zuschreibung, erreicht die Sprechhaltung nur teilweise.* Was hier fehlt, ist der fehlende Teil.

### Die Form kommt aus ihrem Charakter, nicht aus einer Schablone

**Nicht jede Nova sagt „Siehst Du?".** Eine junge, spritzige findet andere Worte als ein alter Butler; eine distanzierte spricht das Gegenüber seltener an als eine zugewandte. Die Ansprache ist keine Vorlage, die über jede Zustellung gelegt wird, sondern **eine Ausdrucksform ihres Charakters**.

Die Bausteine dafür liegen bereits vor:

| Feld | Was es trägt |
|---|---|
| `sprach_stil` | locker · jugendlich · fachlich · formell · emotional |
| `beziehungs_dynamik` | vertrauen · dankbar · neutral · distanz |
| `tone` | der Grundton |
| `nutzer_gewichtung` | wie sehr ihr das Gegenüber überhaupt gilt (Charakter-Rad) |

Sie werden für den Impuls nur **aus der falschen Quelle** gelesen. Der Griff ist derselbe wie beim `graph_rolle`-Fix in Chat 110: nicht neue Felder erfinden, sondern die vorhandenen aus der richtigen Seite nehmen.

**Eine Warnung dazu.** Eine Anweisung wie *„sprich den Nutzer an"* erzeugt Floskeln, wenn sie über allem liegt. Was trägt, sind Beispiele im Register ihres Stils — das hat der Verdichtungs-Prompt in Chat 110 gezeigt: sechs Beispiele legten das Subjekt fest, und keine Regel im selben Prompt bestand dagegen. Für die Ansprache gilt dasselbe.

## 8. Die Unterbrechung gehört dem Nutzer

**Sagt der Nutzer mitten in der Kette etwas, gehört das Wort ihm.** Die Kette pausiert oder endet; sie soll niemanden überreden.

Das System kennt diese Haltung bereits: `shadow_delivery.py:86-92` lässt bei negativen Emotionen ausschließlich Nachfragen durch und schweigt bei Stress ganz. Eine Kette, die weiterläuft, während das Gegenüber das Thema wechselt, wäre das genaue Gegenteil davon.

Vier Zustellungen nacheinander können sich großartig anfühlen — oder wie ein Wasserfall. Der Unterschied liegt allein darin, ob sie aufhört, wenn jemand etwas sagt.

> **§3 und §9 bis §11 stehen nicht in dieser Datei.** Der Raum (§3) und das Verhältnis zum Wissensspeicher (§10) stehen in [`novaberg-gedankenkette_t.md`](novaberg-gedankenkette_t.md); was heute im Weg steht (§9) in [`novaberg-gedankenkette_b.md`](novaberg-gedankenkette_b.md); die offenen Punkte (§11), die Versionshistorie und der bisherige Kopf in [`novaberg-gedankenkette_e.md`](novaberg-gedankenkette_e.md); die Befunde aus dem Betrieb vom 20.08.2026 in [`novaberg-gedankenkette_m.md`](novaberg-gedankenkette_m.md). Welche Datei welchen Abschnitt trägt, sagt die Tabelle oben. Die folgende Zeile *Zusammenhang* stand am Ende von §11.

**Zusammenhang:** `IMPULS-ICH-PERSPEKTIVE-TEILWEISE` (der offene Befund, den §7 auflöst) · `novaberg-eigenzeit_k.md` (wann ein Gedanke überhaupt auftauchen darf, und in welcher Gestalt) · `novaberg-wissensluecken_k.md` (woher der Auftrag kommt) · `novaberg-pixie.md` (Shadow-Delivery) · `novaberg-thinking-curiosity_k.md` §4 (der Traum-Zyklus dachte Ähnliches für Pixie)
