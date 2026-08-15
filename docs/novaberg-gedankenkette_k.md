# Novaberg — Die Gedankenkette: ein Gedanke über mehrere Turns

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — zusammenhängende Zustellungen zu einem Thema
**Stand:** 15. August 2026 (v0.4, Erstfassung 27. Juli 2026)
**Pfad:** novaberg/docs/novaberg-gedankenkette_k.md
**Typ:** Konzept
**Status:** ⬜ Konzept, nicht gebaut
**Berührt:** `services/shadow_delivery.py` · `plugins/wissen_manager/manager.py` · `services/wissensspeicher.py` · `novaberg-wissensluecken_k.md` · `novaberg-eigenzeit_k.md`

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

Dazu `MAX_BURST = 2`. ~~und ein Cooldown von einer Stunde~~ → **Der Cooldown ist am 15.08.2026 gefallen** (`novaberg-eigenzeit_k.md` §2.5); die Frist von einer Stunde hängt seither am Burst-Zähler, der sie als *Gedächtnis* trägt und nicht als Sperre.

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

## 3. Der Raum: das Embedding als Radius

Eine Kette bewegt sich in einer **Kugel um ihren Ausgangsvektor**. Was innerhalb liegt, gehört zum Gedanken; was außerhalb liegt, ist ein neuer.

```
kette_radius = 0.95        (Startwert, kalibrierbar)
```

Der Radius ist eng zu ziehen. Ein weiter Radius lässt sie abschweifen, bis das Thema beliebig wird; ein enger hält sie beim Gedanken.

### Die Zahl der Zustellungen misst den Radius

Das ist die Eigenschaft, die diesen Entwurf selbstkalibrierend macht: **Wie viele Zustellungen eine Kette hervorbringt, sagt, ob der Radius stimmt.**

| Zustellungen je Kette | Befund |
|---|---|
| 10 | Radius zu weit — sie schweift, das Thema trägt nicht so lange |
| **3** | gut |
| **4** | auch gut |
| 1 | Radius zu eng — sie kann nichts ergänzen |

Drei oder vier sind der erwartete Bereich, **aber keine Vorgabe.** Es kommt darauf an, was sie vermitteln will; eine Kette darf auch nach zweien fertig sein. Die Zahl ist ein Messwert über den Radius, keine Quote.

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

## 9. Was heute im Weg steht

| Ort | Heute | Nötig |
|---|---|---|
| `_stack_aehnliche_entfernen`, Schwelle 0.60 | löscht alles Verwandte **vom Stapel**; die Bibliothek behält es (§1) | Wiederholung entfernen, **Vertiefung behalten** — sie ist das Material der Kette |
| `MAX_BURST = 2` | zählt Zustellungen | zählt **abgeschlossene Gedanken**. Vier Zustellungen zu einem Thema sind ein Gedanke |
| Impuls-Prompt | nur das Wissensstück | plus das bisher Gesagte — und eine **andere Aufgabe je Glied** (§6) |
| `aufnahmebereitschaft` | skaliert nur die Lückensuche | pausiert zusätzlich die Kette (§5) |
| `responder.eigener_gedanke.txt` | sagt viermal, was sie **nicht** tun soll | die Sprechhaltung zum Gegenüber (§7) |
| `sprach_stil`, `beziehungs_dynamik`, `tone` | im Responder nur aus `external` | beim Impuls aus **`internal`** — sie spricht (§7) |
| Kontextfenster | `num_ctx = 32768` auf allen Pfaden des `qwen36`-Connectors | reicht; kein Hindernis |

Der erste Punkt ist der schwerste. Löschen ist endgültig — **zurückstellen wäre besser als entfernen.** Was zurückgestellt ist, kann später erneut geprüft werden, und wenn es dann wirklich veraltet ist, verfällt es über seine TTL von selbst.

## 10. Verhältnis zum Wissensspeicher

Eine Kette, die über Turns wächst, braucht einen Ort für das Gewachsene. Der Prompt ist er nicht — der wird nur damit gefüttert.

**Bei ihren eigenen Wissenslücken darf sie ihre Dateien beliebig ändern und erweitern.** Ausarbeitung und Reflexion einer Kette landen im Wissensspeicher und stehen dem nächsten Glied als Material zur Verfügung — und einer späteren Fortsetzung, auch Tage danach.

~~Das setzt Strang B voraus: Verzeichnis, Format, Mount außerhalb des Git-Roots. Ohne ihn kann eine Kette nur so weit tragen, wie ein Prompt reicht.~~ → **Steht seit Chat 128 (14.08.2026 nachgeprüft).**

Die Bibliothek ist gebaut und läuft in beide Richtungen:

| | Stand am 14.08.2026 |
|---|---|
| **Schreiben** | jede Recherche legt Bericht und Wissensdatei ab, dazu eine Metadatenzeile mit Themen-Embedding; ein Gate entscheidet, ob es Wissen wird oder nur ein Bericht |
| **Lesen** | der Wissens-Manager sucht in **jedem** Turn über das Themen-Embedding, Schwelle 0,40, und speist die Treffer als eigene Kontextquelle ein |
| **Bestand** | über dreitausend Zeilen, stündlich wachsend |

**Was eine Kette daraus gewinnt:** Sie muss das Gewachsene nicht im Prompt mitschleppen. Ausarbeitung und Reflexion liegen in der Bibliothek und werden gefunden, wenn das Thema wiederkommt — auch Tage später, auch ohne dass jemand die Kette fortsetzt.

## 11. Offen

**Wer entscheidet, dass der Auftrag erfüllt ist?** Sie selbst am Ende jeder Zustellung, ein eigener Prüfschritt, oder das Vorhandensein einer Reflexion. Nicht entschieden. **Die Frage setzt einen Willen voraus** — solange keiner die Kette trägt, gibt es auch niemanden, der ihr Ende feststellt (§6a).

**Woran hängt der Wille?** `novaberg-thinking-drive_k.md` trägt Zielsätze, Motivation und Zieltabelle; die Recherche erzeugt bereits ein Folgeziel aus ihrem eigenen Ergebnis. Was nirgends steht: dass ein solches Ziel eine Kette **führt** — wie viele Schritte es rechtfertigt, wann es als erreicht gilt und was mit ihm geschieht, wenn das Gespräch dazwischenkommt. Das ist der eigentliche offene Gegenstand hinter §6a und größer als dieses Konzept.

**Der Radius 0.95** ist ein Startwert. Die erste Messung über die Zahl der Zustellungen sagt, ob er stimmt — siehe §3.

~~**Wie verhält sich eine Kette zum Burst-Cooldown?** Eine Stunde Sperre nach zwei Zustellungen würde jede Kette zerreißen. Der Cooldown müsste zwischen Ketten greifen, nicht innerhalb.~~ → **Gegenstandslos seit §6a (14.08.2026).** Die Sorge stand auf der Annahme, eine Kette bestehe aus mehreren Zustellungen. Sie besteht aus **einer** — dem Ruf — und danach aus Antworten auf Nutzer-Turns. Burst und Cooldown greifen damit ohnehin nur dort, wo sie sollen: zwischen Ketten. Die Forderung war richtig und ist bereits erfüllt.

**Wie lang darf ein Schritt sein?** §6a sagt „ein, zwei Sätze". Eine Zahl steht nicht dabei, und ohne Zahl bindet die Vorgabe nicht — gemessen an anderer Stelle dieses Projekts: Die Mengenangabe trägt, das Adjektiv nicht. **Die Untergrenze ist dabei kein Satz, sondern ein Laut:** Ein Ruf kann aus einem gedehnten Wort bestehen. Ein Zeichenkorridor, dessen Unterkante bei einem Satz liegt, macht ihn unmöglich.

**Bricht eine Treppe die Antwortzeit?** Fünf Wechsel für einen Gedanken sind fünf Modellläufe. Ob das im Gespräch als lebendig oder als zäh ankommt, ist ungemessen und hängt daran, wie schnell die kurzen Schritte kommen.

**Was zählt als „ein Turn ohne Bezug zum Anriss"?** Die abwendenden Intentionen sind eine geschlossene Menge, der Themenwechsel ist es nicht. Ob dafür dieselbe Ähnlichkeitsrechnung dient wie beim Zustellungstor, ist nicht entschieden.

**Zusammenhang:** `IMPULS-ICH-PERSPEKTIVE-TEILWEISE` (der offene Befund, den §7 auflöst) · `novaberg-eigenzeit_k.md` (wann ein Gedanke überhaupt auftauchen darf, und in welcher Gestalt) · `novaberg-wissensluecken_k.md` (woher der Auftrag kommt) · `novaberg-pixie.md` (Shadow-Delivery) · `novaberg-thinking-curiosity_k.md` §4 (der Traum-Zyklus dachte Ähnliches für Pixie)

---

## Versionshistorie

- **v0.4 — 15.08.2026:** §2 nachgezogen: **Der Cooldown von einer Stunde ist gefallen** (`novaberg-eigenzeit_k.md` §2.5). Was von der Stunde bleibt, hängt am Burst-Zähler und ist dort sein *Gedächtnis*, keine Sperre. Die Feststellung aus §11, dass Burst und Cooldown eine Kette nicht zerreißen, bleibt richtig — sie greifen weiterhin nur zwischen Ketten.

- **v0.3 — 14.08.2026:** Die Bibliothek ist nachgeprüft und **steht in beide Richtungen** — §10 hatte sie als Voraussetzung geführt, die noch fehle. Sie wird von jeder Recherche beschrieben und in **jedem** Turn gelesen; gemessen 2 bis 3 Treffer je Turn bei Cosinus 0,896 bis 0,437. Damit ist §1 eingegrenzt: Das Aufräumen des Stapels kostet den Einwurf-Kandidaten, nicht das Wissen — die Nachfrage wird aus der Bibliothek bedient. Und die „kleine Form" aus §6a braucht weniger als dort stand: Der Rückgriff im Gespräch ist gebaut. **Der Nebenfund gehört festgehalten:** Diese Ähnlichkeitsrechnung trennt, wo dieselbe Rechnung zwischen Aufsatz und Zuruf versagt — der Unterschied ist die Skalengleichheit, Themenphrase gegen Themenphrase. Was offen bleibt, ist schmal: Das Gefundene kommt als Erinnerung an, nicht als das eben Erzählte.
- **v0.2 — 14.08.2026:** §6a neu — **ein neues Thema beginnt mit einem Ruf, nicht mit dem Fund.** Das erste Glied trug bisher die Substanz; für ein Thema, das niemand aufgerufen hat, ist das eine Ablage statt eines Beitrags. An seine Stelle tritt eine **Treppe**: Ruf, Feld, Fund — jeder Schritt ein, zwei Sätze, und vor jedem eine Freigabe durch den Menschen. Der Ruf trägt **keine Information**, das ist seine Eigenschaft und nicht sein Mangel; auch der Fund bleibt eine Portion und wird nicht zur Ausarbeitung. Dazu der **Abschluss** für den Fall, dass die Neugier ausbleibt. Das Tor ist die nächste Äußerung, gelesen über den vorhandenen Intentionen-Kanon — keine neue Mechanik, keine neue Schwelle. **Nur der erste Schritt ist ein Einwurf**, alles danach sind Antworten auf einen Nutzer-Turn; damit ist die offene Frage aus §11 erledigt, ob Burst und Cooldown eine Kette zerreißen. Bleibt eine Äußerung ganz aus, wartet die Kette; nur eine abwendende schließt sie. Der Kettenzustand braucht ein Feld mehr — *wartet auf Zustimmung* — und die Treppenstufe. **Die Zahl der Schritte ist offen und hängt an einem Willen** — drei ist ein Beispiel, nicht die Form; eine feste Stufenzahl wäre eine Schablone. Weil dieser Wille fehlt, trägt §6a zusätzlich eine **kleinere Form ohne Ziel**: Hinführung, bei Neugier ein Teil, und danach bleibt das Wissen im Gespräch **verfügbar** statt weiter zugestellt zu werden. Sie setzt zweierlei voraus, das schon benannt ist — der Eintrag darf nicht gelöscht werden (§1, §9), und er muss als Material erreichbar sein statt als Reiz. §6 ist im Rumpf markiert, nicht ersetzt. Fünf offene Punkte ergänzt oder geschärft, darunter: Die Untergrenze eines Schritts ist kein Satz, sondern ein Laut — und der Wille, der eine Kette führt, ist der eigentliche offene Gegenstand dahinter.
- **v0.1 — 27.07.2026:** Erstfassung. Die Kette als Einheit zwischen Stapel und Einzelzustellung, der Radius als selbstkalibrierende Größe, der Bogen aus Auftrag/Ausarbeitung/Reflexion, die Trennung von Enden und Pausieren, der Rhythmus der Glieder, die Sprechhaltung zum Gegenüber und die sieben Stellen, die heute im Weg stehen.
