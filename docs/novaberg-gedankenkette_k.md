# Novaberg — Die Gedankenkette: ein Gedanke über mehrere Turns

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — zusammenhängende Zustellungen zu einem Thema
**Stand:** 27. Juli 2026, Chat 111
**Pfad:** novaberg/docs/novaberg-gedankenkette_k.md
**Typ:** Konzept
**Status:** ⬜ Konzept, nicht gebaut
**Berührt:** `services/shadow_delivery.py` · `novaberg-wissensluecken_k.md` · Wissensspeicher (Strang B)

---

## 1. Die Beobachtung

Ein Impuls wird zugestellt, und danach ist Schluss — nicht weil Nova nichts mehr zu sagen hätte, sondern weil der Rest **gelöscht wird**.

`services/shadow_delivery.py:270-296`, unmittelbar nach dem Senden:

```python
def _stack_aehnliche_entfernen(…, threshold: float = 0.60) -> None:
    """Entfernt Stack-Einträge die dem gerade gesendeten zu ähnlich sind."""
```

Alles auf ihrem Stapel, das dem eben Gesagten mit **0.60 Cosine** ähnelt, fliegt weg. Das ist ein weites Netz: Bei einer Themenwolke aus einem Fachgespräch liegen die verwandten Gedanken sämtlich zwischen 0.6 und 0.8. Sagt sie einen, verliert sie im selben Atemzug die anderen.

Dazu `MAX_BURST = 2` und ein Cooldown von einer Stunde.

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
| **erstes** | die Substanz — gespickt mit Informationen, der Fund selbst |
| **zweites** | eine Kleinigkeit, die gefehlt hat |
| **drittes** | die Verknüpfung, die Freude daran |

Das dritte Glied kann ein einziger Satz sein:

> *„Und das Beste ist, es passt genau in unser Bild!"*

Das ist keine Information. Es ist die Stelle, an der sichtbar wird, dass sie mitgedacht hat — und genau die klingt lebendig. So erzählen Menschen: erst die Sache, dann der Nachtrag, dann das Funkeln.

**Der Prompt muss das tragen, sonst schreibt sie vier Aufsätze.** Ein Modell, das viermal dieselbe Aufgabe bekommt, liefert viermal dieselbe Fülle — und aus einem Gedanken wird eine Wiederholung mit Variationen.

Das spätere Glied braucht also eine **andere** Anweisung als das erste: Du hast das Wesentliche gesagt; ergänze nur, was fehlte, und sei kurz. Das ist derselbe Griff wie bei den drei Verdichtungs-Prompts nach Rolle — ein Beispiel schlägt eine Regel, und eine Aufgabe, die für alle Glieder gleich lautet, legt die Länge auf das erste fest.

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
| `_stack_aehnliche_entfernen`, Schwelle 0.60 | löscht alles Verwandte | Wiederholung entfernen, **Vertiefung behalten** — sie ist das Material der Kette |
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

Das setzt Strang B voraus: Verzeichnis, Format, Mount außerhalb des Git-Roots. Ohne ihn kann eine Kette nur so weit tragen, wie ein Prompt reicht.

## 11. Offen

**Wer entscheidet, dass der Auftrag erfüllt ist?** Sie selbst am Ende jeder Zustellung, ein eigener Prüfschritt, oder das Vorhandensein einer Reflexion. Nicht entschieden.

**Der Radius 0.95** ist ein Startwert. Die erste Messung über die Zahl der Zustellungen sagt, ob er stimmt — siehe §3.

**Wie verhält sich eine Kette zum Burst-Cooldown?** Eine Stunde Sperre nach zwei Zustellungen würde jede Kette zerreißen. Der Cooldown müsste zwischen Ketten greifen, nicht innerhalb.

**Zusammenhang:** `IMPULS-ICH-PERSPEKTIVE-TEILWEISE` (der offene Befund, den §7 auflöst) · `novaberg-wissensluecken_k.md` (woher der Auftrag kommt) · `novaberg-pixie.md` (Shadow-Delivery) · `novaberg-thinking-curiosity_k.md` §4 (der Traum-Zyklus dachte Ähnliches für Pixie)
