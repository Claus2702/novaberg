# Novaberg — Eigenzeit: was zwischen zwei Turns geschieht (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-eigenzeit_k.md`](novaberg-eigenzeit_k.md) · Ausarbeitung: [`novaberg-eigenzeit_t.md`](novaberg-eigenzeit_t.md) · Diskussion und Ergänzungen: [`novaberg-eigenzeit_e.md`](novaberg-eigenzeit_e.md) · Messungen: [`novaberg-eigenzeit_m.md`](novaberg-eigenzeit_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Aus §2.3 — Der Level, den ein Gedanke mitträgt: der Stand des Kanals

Die Absicht von §2.3 steht in [`novaberg-eigenzeit_k.md`](novaberg-eigenzeit_k.md); hier steht der Stand der Umsetzung, der dort zwischen dem ersten Absatz und *„Die Wiedervorlage bleibt ohne Werte …“* stand.

~~Der Kanal dafür ist vorhanden und wird an beiden Enden nicht bedient: Der Stapel-Eintrag hat Felder für Emotion und Modus, die Zustellung reicht sie ins Ereignis, der Zugriffsknoten baut daraus einen Zustand — **und verwirft ihn auf dem Impuls-Pfad.** Vorne befüllt nur einer von drei Agenten die Felder; die Erregung ist gar kein Feld.~~ → **Am 15.08.2026 zur Hälfte behoben: Das vordere Ende ist bedient.**

`stack_push` nimmt seither `salienz` und `arousal` entgegen; die Recherche reicht Emotion, Modus, Intentionen und den auslösenden Wert aus dem Queue-Auftrag durch, das Nachfragen zusätzlich die Erregung des auslösenden Turns. **`None` heißt darin unbekannt und wird nie zu einer Zahl** — beide Felder stehen immer im Eintrag, auch leer, weil ein weggelassenes Feld von einem Eintrag alter Bauart nicht zu unterscheiden wäre.

Gemessen am selben Tag über 1028 Queue-Aufträge: Die Werte lagen dort seit jeher und streuen — `emotion` in sechs Ausprägungen ohne eine einzige Lücke, `modus` in sechs mit 141 leeren. Sie kamen nur nie an; der Stapel-Bestand trug bei allen 86 Einträgen ausschließlich das Embedding.

~~**Das hintere Ende steht weiterhin aus:** Der Zugriffsknoten verwirft den mitgereichten Zustand auf dem Impuls-Pfad nach wie vor.~~ → **Am 15.08.2026 geschlossen.** Die Zustellung reicht den Wert als `gedanke_arousal` ins Ereignis, `graph/reiz.py` liest ihn als einziger Zugang, und der Zugriffsknoten hebt damit Novas Erregung — das Gegenstück zum Verfall, je Turn greift höchstens eines von beiden. Das ist Bauteil B (§5.2).

**Der Kanal hat damit an beiden Enden einen Anschluss und trotzdem noch keinen Verkehr.** Gemessen am 15.08.2026 über den gesamten Stapel-Bestand: **kein einziger Eintrag trägt einen Level.** Der Grund steht in der Tabelle und nicht im Code — `shadow_auftrag` führt `emotion` und `modus`, aber **keine Spalte für die Erregung**. Die Recherche kann also nichts durchreichen, was sie nicht bekommt; einen Wert trägt allein das Nachfragen, das ihn direkt vom auslösenden Turn liest (45 von 1036 Aufträgen).

~~Ob die Queue die Erregung mitführen soll, ist **hier nicht entschieden**.~~ → **Am 15.08.2026 entschieden und gebaut.** `shadow_auftrag` trägt seither eine `arousal`-Spalte, **NULL-fähig und ohne Vorgabewert**; beide Erzeuger lesen sie aus derselben Lage, aus der `emotion` und `modus` stammen. Damit trägt auch die Recherche einen Level — nicht nur das Nachfragen, dessen beste Aufträge auf Rang 367 von 817 lagen und durch Warten nicht aufsteigen.

**Der Bestand bleibt leer und das ist richtig so:** 1050 Aufträge alter Bauart tragen NULL, und NULL heißt unbekannt. Der Bauteil wirkt an dem Tag, an dem der erste Auftrag **neuer** Bauart seinen Weg auf den Stapel und von dort in einen Einwurf nimmt.

---

## Aus §2.5 — Anwesenheit ist Bedingung: die Uhr ist gefallen

Dieser Kasten stand im ungeteilten Konzept am Ende des Unterabschnitts *„Anwesenheit ist Bedingung, und sie steht vor der Kette — entschieden am 24.08.2026“* (in [`novaberg-eigenzeit_k.md`](novaberg-eigenzeit_k.md)), nach der Messung vom 24.08.2026 (in [`novaberg-eigenzeit_m.md`](novaberg-eigenzeit_m.md)).

> **Am 24.08.2026 gebaut: Die Uhr ist gefallen.** An der Stelle des `else: continue` steht ein
> dritter Auslöser, `stille`. Er trägt dieselbe Vorbedingung wie der Timeout — ohne Gespräch feuert
> er nicht — und verbraucht seinen Auslöser genauso, sonst fragte die Schleife alle 5 s statt alle 30 s.
>
> **Die Messung, die es trug, ist die Trennung von Wand und Burst.** Über 214,5 h Betrieb liegen
> zwölf Lücken über einer Stunde. **Zehn davon enden binnen zwei Minuten mit einer Äußerung des
> Menschen** — das ist die Signatur der Wand und keine Verbindungsfrage, denn eine wiederhergestellte
> Verbindung setzt die Schleife von selbst fort. Die beiden anderen sind **exakt 1:00:33 und 1:00:17**
> lang: die Burst-TTL. Zusammen **126 von 214,5 Stunden, 59 % der Zeit**.
>
> **Und die Riegel trugen die Entscheidung immer schon länger als die Uhr sie zuließ.** Ein
> Haltungsstand gilt bis `ZUWENDUNG_STAND_MAX_ALTER_SEKUNDEN` = **24 h**; danach gelten Riegel 1
> und 2 als *unbekannt* und verweigern von selbst. Die Wand schnitt bei 2 h ab — **zwölfmal früher
> als das Kriterium der Riegel**. In acht der zehn Wand-Lücken hätte der Stand noch getragen.
>
> **Im Betrieb belegt am 24.08.2026, 17:56 UTC** (Auslösefall: `last_activity` und der
> Burst-Zähler von Hand geleert, beides mimt die natürliche Expiry):
> `Trigger 'stille'` → `Riegelkette [wollen+0.96 frequenz+-0.86 ruhe+] entschieden=keiner` →
> `Bester Match 'Ordnung, Störung der Ordnung' (score=0.43)` → `Erfolgreich für 'meister'
> (trigger=stille)`, 1293 Zeichen. Dreißig Sekunden später übernahm wieder `timeout` — der
> Auslöser ist verbraucht, die Schleife fällt in den bekannten Takt zurück.
>
> Zeugen: `tests/test_stille_ausloeser.py` (6), Gegenprobe **4 vorhergesagt / 4 gezählt**.
>
> **Was an die Stelle der Wand trat, stand sofort da: Prüfung 1, der Burst.** Vier Riegelketten in
> neunzig Sekunden, zwei Impulse, dann Stille — um 18:17 UTC `shadow_burst_count = 2` bei TTL
> 2459 s, während `last_activity` noch 6042 s trägt. **Er ist ein Cooldown, kein Rate-Limit:**
> `_burst_erhoehen` setzt die TTL bei jedem Inkrement neu, `MAX_BURST=2` heißt *zwei, dann eine
> volle Stunde ab dem letzten*. Rechnerisch sind das bis zu 48 Impulse am Tag gegen 15 in zwei
> Tagen im Bestand; wieviel Riegel 2 davon wegnimmt, braucht einen Betriebstag. **Vor dieser
> Messung wird an den beiden Konstanten nichts gedreht.**

---

## Aus §3.6 — Verworfen: das Verbot als Mittel

§3.6 steht in [`novaberg-eigenzeit_k.md`](novaberg-eigenzeit_k.md); hier steht, was im ungeteilten Konzept am Ende von §3.6 stand: die Umsetzung vom 14.08.2026 mit ihrer Messung.

**Umgesetzt am 14.08.2026, als eigener Zug mit eigener Messung.** Beide Herkunftsblöcke tragen jetzt Führung statt Verbot — *„Es ist ihre Entdeckung", „Sie eröffnet", „Sie zeigt ihm, was sie sieht"* statt *„kein du hast", „schreibt sie ihm nicht zu"*.

`[gemessen]` — 14.08.2026, 20:30 UTC, ein Gedanke über die Silikatpartikel in den Fontänen des Enceladus, mit prohibitionsfreiem Prompt:

> *„**Person A** stellt die Entdeckung der Silikatpartikel … zur Diskussion. Sie weist darauf hin … Sie stellt die Frage nach der biologischen Implikation …"*

Und die Antwort: *„Weißt du, ich muss ständig an diesen einen Datenpunkt denken: Enceladus … **glaubst du**, dass diese thermische Energie die notwendige Resonanz für biologische Prozesse bietet?"*

**Die Zuschreibung bleibt auf Person A, ohne dass ein Verbot sie hält** — die Struktur trägt sie, wie §2.6 es vorhergesagt hat. Und die Führung hat etwas hinzugefügt, was vorher nicht da war: Sie wendet sich ihm zu und fragt ihn. Ein Verbot hätte das nie erzeugen können; es nennt nur, was ausbleiben soll.

> ⚠ **Zwei Turns sind keine Reihe, und sie sind nicht kontrolliert** — verschiedene Themen, verschiedene Landschaften. Was sie zeigen, ist das Ausbleiben eines Rückfalls, nicht die Wirkung der Führung.

---

## 5. Die Bauteile

### 5.1 Bauteil A — der Verfall über das Intervall

**Stand 15.08.2026: gebaut.** Der Verfall sitzt im Zugriffsknoten
(`graph/nodes/db_zugriff.py`, `_zustand_verfallen`) und wird von der Äußerung
ausgelöst, nicht von einer Uhr. Die Kurve steht in `ei/eigenzeit.py`, ihre drei
Marken in der Konfiguration.

**Die Uhr war nicht vorhanden und ist mitgebaut worden.** `nova_state` trug
elf Felder und keinen Zeitstempel. Der Session-Verlauf trägt zwar einen je
Turn, taugt aber nicht als Quelle: Ab 25 Turns werden die ältesten zehn
zusammengefasst und entfernt, und als Zahl überlebt ein Zeitstempel das nicht.
Eine Nacht mit stündlichen Impulsen schiebt die letzte Äußerung damit aus dem
Fenster, **während sie die Frist immer wieder erneuert** — der Verlauf lebt,
und gerade der Eintrag, auf den es ankäme, ist fort. Der Zustand trägt deshalb
jetzt **zwei** Uhren: `turn_zeit` bei jedem Turn, `nutzer_zeit` nur bei einer
Äußerung.

**Die Session-Frist ist dabei auf vier Stunden gestiegen** (vorher zwei). Sie
lag unter dem Nullpunkt der Kurve, und daraus entstand ein Fenster, in dem der
**Verlauf vor dem Zustand** verschwindet: Nova wäre noch nicht zur Ruhe
gekommen und hätte schon vergessen, worüber gesprochen wurde — dieselbe fremde
Nova wie in §2.2, nur von der anderen Seite. Ein Zeuge hält seither fest, dass
`SESSION_TTL` die Kurve überdauert; beide Zahlen stehen an verschiedenen Orten
und sind je für sich plausibel, also genau die Konstellation, in der sie
auseinanderlaufen.

**Drei Setzungen, die das Konzept offengelassen hat:**

1. **Zwischen den Marken wird linear interpoliert.** Die Sieben-Werte-Tabelle
   oben ist damit eine Illustration, keine Vorschrift — die gebaute Kurve
   weicht von ihr um bis zu **0,055** ab (bei 1,5 h: 0,675 statt 0,73). Das
   liegt unter der Unsicherheit der Marken selbst, die geschätzt sind (§6).
2. **Die Kategorien springen unterhalb des Halbwerts** (0,45,
   `EIGENZEIT_KATEGORIE_SCHWELLE`). Begründung: Trägt eine Kategorie zu
   weniger als der Hälfte, ist sie keine mehr. Setzung, nicht gemessen.
3. **Die Erregung wird zur Ruhelage 0,5 gezogen, nicht gegen null
   multipliziert.** Eine Erregung von 0,00 wäre keine Ruhe, sondern ein toter
   Wert — und im Bestand ist 0,5 der Ausfallwert der Wahrnehmung.

`[gemessen]` — 15.08.2026. Ein Impuls-Turn setzt `turn_zeit` und **nicht**
`nutzer_zeit`; auf ihm findet kein Verfall statt (null Verfallszeilen im
Protokoll). Eine Äußerung nach einer Pause von 14425 s ergab
`Faktor 0.00, Erregung 0.90 → 0.50, Kategorien gesprungen`. Der Zustand danach
steht wieder bei 0,90 — die Wahrnehmung der Äußerung hat sie von dem Wert aus
hinaufgezogen, auf den sie gefallen war. Genau das ist der Mechanismus aus §2.2.

**Die Uhr der Äußerung ist `empfangen_am` aus dem Ereignis, nicht die Uhr des
schreibenden Knotens.** Er läuft am Ende des Durchlaufs; gemessen lagen
zwischen beiden **127,8 Sekunden**, die sonst als Fehler in jedem Abstand
steckten.

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Eine Nutzeräußerung nach einer Pause trifft Nova auf einem über die Kurve gedämpften Zustand; Nähe, Tiefe und Beziehungsdynamik bleiben unberührt, Impuls-Turns sind nicht betroffen. |
| **TEST** | Derselbe gespeicherte Zustand, einmal mit letzter Nutzeräußerung vor fünf Minuten, einmal vor drei Stunden: im ersten Fall unverändert, im zweiten die Erregung auf dem Neutralwert und die Kategorien gesprungen. Nähe in beiden Fällen identisch. Derselbe Zustand auf einem Impuls-Turn: unverändert, unabhängig von der Pause. |
| **MESSUNG** | Der erste Turn eines Morgens nach einer Nacht mit Impulsen: Erregung, Modus, Sprachstil und die vermessene Landschaft, gegen den Stand vom 14.08.2026 (`beichte / Katharsis` auf einem spielerischen Gruß). |
| **Gegenprobe** | Die Uhr auch bei Impuls-Turns setzen: Der Nacht-Test muss rot werden. |

### 5.2 Bauteil B — der Level, den ein Gedanke mitträgt

**Stand 15.08.2026: gebaut, und ohne Wirkung auf dem heutigen Bestand.** Die
Zustellung reicht den Wert des Stapel-Eintrags als `gedanke_arousal` ins
Ereignis — **immer, auch leer**, weil ein weggelassenes Feld von einem Eintrag
alter Bauart nicht zu unterscheiden wäre. `graph/reiz.py` ist der einzige
Zugang und prüft dort, wo der Wert das System betritt: Sorte, Spanne und die
Falle, dass `True` in Python eine Eins ist. Ein Wert außerhalb von [0,0; 1,0]
wird **verworfen und gemeldet, nicht gekappt**. Der Zugriffsknoten hebt damit
die Erregung per Maximum; `_level_anheben` steht neben `_zustand_verfallen`
und beide haben dieselbe Weiche: der Verfall greift auf einer Äußerung, das
Anheben auf einem Gedanken.

**Drei Größen bleiben ausdrücklich unberührt.** Die Kategorien, weil ein
Maximum über ihnen nichts bedeutet. Der Raum, weil ein Gedanke im laufenden
Gespräch dessen Raum nimmt und nicht seine alte Lage mitbringt (§2.4). Und die
Bindung, aus demselben Grund wie beim Verfall.

**Die Wirkung ist heute null, und das ist messbar und nicht vermutet:** Kein
Eintrag des Stapels trägt einen Level (§2.3). Die Protokollzeile steht deshalb
auch dann, wenn nichts hinterlegt war — mit `wirkung: kein_level`. Ohne sie
wäre *„kein Level im Bestand"* von *„der Bauteil läuft nicht"* nicht zu
unterscheiden, und genau diese Verwechslung steht in diesem Projekt sechsmal
im Defektregister.

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Ein Einwurf hebt Novas Zustand auf den Stand, in dem der Gedanke gefasst wurde — per Maximum, und nur, wenn ein Stand hinterlegt ist. |
| **TEST** | Ein Stapel-Eintrag mit hinterlegter Erregung hebt einen niedrigeren Zustand; derselbe Eintrag senkt einen höheren **nicht**; ein Eintrag ohne hinterlegten Stand lässt den Zustand unverändert. |
| **MESSUNG** | Ein echter Einwurf nach einer Pause: der Zustand vor und nach dem Impuls-Turn, gegen den hinterlegten Wert des Eintrags. **Zur Hälfte eingelöst am 15.08.2026:** Der Mechanismus läuft im Betrieb — zwei echte Impuls-Turns (17:07 und 18:07 UTC) tragen die Zeile `schritt=gedanke_level`, beide mit `wirkung=kein_level` und `arousal 0,75 → 0,75`. Die **Wirkung** bleibt ungemessen, bis ein Eintrag mit Level zugestellt wird; dass sie ausbleibt, ist damit **belegt statt vermutet**. |
| **Gegenprobe** | Das Anheben entfernen: Der Test zum Heben wird rot, die beiden anderen bleiben grün. **Gefahren am 15.08.2026: 3 von 20 rot** — die beiden Zusicherungen *senkt nicht* und *kein Level* blieben grün, wie vorhergesagt. Dazu die zweite Gegenprobe auf die Naht — das Feld aus dem Payload der Zustellung entfernt: 3 von 3 Nahtzeugen rot. |

### 5.3 Bauteil C — das Tor

**Stand 15.08.2026: gebaut, mit einem benannten Aufschub.** Der Bezugsvektor kommt aus den Aeusserungen des Menschen und ohne Zeitfenster, die Schwelle steht bei **0,30** als eigene Konstante mit ihrer Paarung im Kommentar, und ein Eintrag ohne Embedding wird **abgelehnt** statt als exakt auf der Schwelle liegend durchgelassen.

**Nicht gebaut ist der Fall ohne Bezug.** Das Konzept will, dass dann nur dieses Tor entfaellt und die uebrigen bleiben — aber wonach ohne Themenwert zu waehlen waere, ist unentschieden (§6), und es ist der **haeufigste** Fall: 39 von 56. Bis das entschieden ist, wird dort nichts zugestellt, und die Stelle meldet sich als `error`, damit der Aufschub zaehlbar ist statt unsichtbar zu bleiben. **Das ist eine bewusst offene Kante und kein fertiges Bauteil.**


| Zeile | Inhalt |
|---|---|
| **ZIEL** | Ein Gedanke erreicht ein laufendes Gespräch nur, wenn er thematisch und im Modus dazu passt; sonst bleibt er auf dem Stapel. Ohne Äußerung des Menschen im Fenster gibt es kein Tor. |
| **TEST** | Ein Eintrag zu einem entfernten Thema wird bei laufendem Gespräch abgelehnt und bleibt auf dem Stapel; ein Eintrag zum laufenden Thema kommt durch. Ein Eintrag ohne Embedding wird abgelehnt. Der Bezugsvektor enthält keine Assistenz-Turns. Ohne Nutzeräußerung im Fenster wird nicht gefiltert. |
| **MESSUNG** | Über einen Tag: Zahl der Einwürfe, ihr thematischer Abstand zum jeweils letzten Nutzer-Turn, und die Zahl der Einträge, die auf dem Stapel warten statt zu verfallen. |
| **Gegenprobe** | Den Bezugsvektor wieder aus allen Rollen bilden: Der Test auf das entfernte Thema muss grün werden, obwohl er es nicht sein darf. |

### 5.4 Bauteil D — der Rad-Riegel

~~**Voraussetzung:** Die Haltung überlebt den Turn (§2.5). Ohne sie ist D nicht baubar.~~ → **Am 15.08.2026 erfüllt.** Der Stand liegt unter `haltung:{user_id}:{character_id}` und ist von außerhalb des Graphen lesbar (`memory/haltung.py`).

**Was jetzt noch fehlt, sind zwei Dinge, und nur eines davon ist Bauarbeit:**

1. **Die Prüffigur bei `distanz 0,90`** (`novaberg-backlog.md` → `PRUEFFIGUR-DISTANZ-090`). Ohne sie ist die Trennung bei 0,25 nicht widerlegt, aber auch nicht belegt (§6).
2. ~~**Die Frequenz-Schwelle des Führungsmaßes** für Riegel 2. Sie ist unentschieden, und mit ihr steht und fällt das Fallen der stündlichen Decke.~~ → **Am 15.08.2026 erledigt, aber nicht durch eine Entscheidung über die Zahl.** Die Messung hat die Prämisse widerlegt: Das Führungsmaß trägt keine Frequenz. Riegel 2 ist stattdessen ein **Schalter** und liest die vorhandene `GV_INITIATIVE_SCHWELLE` — es gab nie eine zweite Zahl zu setzen.

**Riegel 1 ist davon unabhängig baubar** — er entscheidet das *Ob*, nicht die Häufigkeit. Was er ohne Riegel 2 nicht darf, ist die Decke ablösen.

**Stand 15.08.2026: Riegel 1 ist gebaut** (`services/pixie/riegel.py`), mit der Schwelle 0,25 auf `haltung.werte["naehe"]` aus dem persistierten Stand. Er steht **vor** der Suche und vor dem LLM-Lock: Will sie nicht zugehen, kostet die Runde weder ein Embedding noch die GPU.

**Vier seiner fünf Blockgründe heißen „unbekannt", einer heißt „nein".** Kein Stand, ein Stand ohne Rechnung, ein zu alter Stand und eine fehlende Nähe blocken alle — aber sie werden **getrennt gezählt**, sonst sieht ein kaputter Speicher in jeder Auswertung aus wie eine distanzierte Figur. Ein unbekannter Riegel lässt nicht durch, sondern verweigert; die Frist für den Stand liegt bei 24 h und ist eine Setzung.

**Und die Kette verweigert, wenn sie unvollständig ist.** `durchgelassen()` hing zunächst allein am fehlenden Blocker — eine Kette ohne einen einzigen Eintrag hat keinen, und damit hätte ein Ausfall der Aufnahme **jeden** Gedanken durchgelassen, bei grüner Suite. Ein Urteil ohne die Pflicht-Riegel ist keines; „nichts geprüft" darf nicht aussehen wie „nichts einzuwenden". Die Vollständigkeit steht mit den fehlenden Namen im Eintrag, damit eine Auswertung sie nicht an `durchgelassen: false` raten muss.

**Die Protokollpflicht ist zur Hälfte eingelöst.** Je Zustellversuch entsteht ein Eintrag im `pipeline_log` (Knoten `zustellung`) mit dem entscheidenden Riegel, den Werten der gerechneten und der Marke für die nicht gerechneten — alle sieben stehen darin, auch die nie berührten. **Zwei benannte Reste** (`novaberg-backlog.md` → `ZUSTELLUNG-ABBRUCH-UNGEZAEHLT` und `RIEGEL-5-7-OHNE-EINTRAG`)**:** Der Eintrag beginnt am Trigger (`umfang: ab_trigger`), weil Rückfrage, Burst und leerer Stapel davor abbrechen und ihre Umstellung das Verbrauchsverhalten des Momentums änderte; und die Riegel 5 bis 7 entscheiden **innerhalb** der Zustellung und tragen ihre Werte noch nicht in denselben Eintrag ein.

**Stand 15.08.2026: Riegel 2 ist gebaut** (`services/pixie/riegel.py`, `initiative_pruefen`), als **Schalter** auf dem Führungsmaß des persistierten Standes, mit der vorhandenen Schwelle `GV_INITIATIVE_SCHWELLE`. **Mit ihm ist die stündliche Decke gefallen** — `_cooldown_aktiv` und `_cooldown_setzen` sind weg, `shadow_cooldown_reset` heißt jetzt `shadow_burst_reset` und löscht nur noch den Zähler.

**Drei seiner vier Blockgründe heißen „unbekannt", einer heißt „nein".** Kein Stand, ein zu alter Stand und ein fehlendes Führungsmaß blocken alle — getrennt gezählt, aus demselben Grund wie bei Riegel 1. Nur `mensch_fuehrt` ist eine Aussage über den Moment.

**`frequenz` ist Pflicht-Riegel geworden, und zwar als Folge des Deckenfalls.** Solange die Uhr stand, war ein nicht gerechneter Riegel 2 eine Lücke in den Daten; jetzt wäre er das Fehlen der einzigen Begrenzung, die den Zeitpunkt noch beurteilt. Eine Kette ohne ihn lässt nicht durch.

**Seine Voraussetzung ist dieselbe wie bei Riegel 1 und war nicht erfüllt:** Das Führungsmaß entsteht im Graphen, der Riegel entscheidet außerhalb. Der Haltungsstand trägt es seit dem 15.08.2026 als **eigenes Feld mit eigenem Grund** — ausdrücklich nicht in `werte` und ausdrücklich nicht an der Marke `gerechnet`: Die Haltung fällt aus, wenn das Rad fehlt, das Führungsmaß, wenn seine Maße keine Quelle hatten. Lägen beide auf einer Marke, verdeckte **Riegel 1 den Riegel 2** — genau das, was §2.5 als nicht mehr kalibrierbar benennt.

`[gemessen]` — 15.08.2026 im Betrieb, unmittelbar nach dem Umbau: Der Trigger fällt jetzt alle 30 s statt einmal je Stunde, und der Eintrag lautet `[wollen+0.91 frequenz- ruhe+] entschieden=frequenz` mit `grund: initiative_fehlt`. **Der einzige Haltungsstand im Bestand trug das Feld nicht** — erwartetes Ergebnis: Es entsteht beim nächsten Turn je Paar, und bis dahin blockt Riegel 2 selbstheilend und zählbar.

`[gemessen]` — Wie oft der Schalter offen stünde, über 424 Zeilen auf der heutigen Schwelle: **38,7 %** über alle Paare, **47,9 %** beim produktiven Paar, **0 Ausfälle**. Das ist die Zahl, die die Decke ersetzt.

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Eine Figur, die auf Abstand hält, wirft keine eigenen Gedanken ein; eine nahe, aber zurückhaltende Figur tut es selten. Der Riegel greift **vor** der thematischen Suche. |
| **TEST** | Dasselbe Paar, einmal mit naher und einmal mit distanzierter Haltung bei sonst gleichem Stapel und gleicher Landschaft: im ersten Fall wird ein Eintrag gewählt, im zweiten wird **gar nicht erst gesucht**. Bei gleicher Nähe und zwei verschiedenen Führungsmaßen unterscheidet sich die Zahl der Einwürfe, nicht das Ob. Der Zeuge gegen die Verwechslung: Ein hohes Führungsmaß heißt *der Mensch treibt* und darf die Einwurfrate **nicht** heben. Und der Zeuge auf das Protokoll: Nach einem Versuch, den Riegel 1 abgewiesen hat, tragen die Riegel 2 bis 4 trotzdem ihre Werte, und Riegel 5 trägt die Marke *nicht gerechnet* — **nicht** einen Leerwert. |
| **MESSUNG** | Über einen Tag je Paar: Haltungs-Nähe, Führungsmaß, Zahl der Einwürfe. Dazu die Protokollzeile je Prüfung — entschiedener Riegel, Werte der gerechneten, Marke der nicht gerechneten. Die Verteilung der Entscheidungsgründe über einen Tag ist die eigentliche Zahl: Sie sagt, welcher Riegel trägt und welcher nie zum Zug kommt. |
| **Gegenprobe** | Den Riegel auf die Nähe-Achse der Landschaft statt auf die Haltung setzen: Der Test mit der distanzierten Figur in warmer Landschaft muss grün werden, obwohl er es nicht darf. Das ist die verworfene Variante aus §3.4 in Testform. |

### 5.5 Bauteil E — der Platz des Gedankens

**Stand 14.08.2026: gebaut.** Der Gedanke hat einen eigenen Kanal, alle elf Leser sind umgestellt, die Zustellung befüllt den Reiz-Platz nicht mehr, und beide erzeugenden Stufen bekommen ihn als **Block** neben Gedächtnis und Recherche. Auf dem Platz des Gegenübers steht nur noch der Auftrag — eine Nachricht muss dort stehen, aber ein Auftrag ist keine fremde Rede.

`[gemessen]` — 14.08.2026, 19:15 UTC, ein Impuls-Turn mit leerem Reiz-Platz (Gedanke: 193 Zeichen über Rotationskurven von Spiralgalaxien):

```
Enricher    Embedding Dim 768        (nicht über der leeren Zeichenkette)
Router      Route Prompt 193 Zeichen (nicht 0)
GV-Node     User-Prompt 2241 Zeichen (Landschaft mit Gegenstand)
Verfasser   Inhalt bestimmt, 669 Z.  (kein „leerer Reiz")
Salienz     lagebild_laenge=193      (kein leeres Bewertungsobjekt)
Verdichtung lagebild_laenge=193      (zweimal, je Segment)
Session     rolle=assistant          (der Gedanke steht nicht als fremde Rede)
Rohturn     prompt=193 Z.            (die Messreihe bleibt fortschreibbar)
```

**Und derselbe Turn belegte, warum der Block nötig war.** Der Verfasser schrieb: *„PERSON B stellt die physikalische Beobachtung der flachen Rotationskurven … in den Raum."* Person B ist der Mensch, und der hatte nichts gesagt. Der Reiz-Platz war bereits leer, die Zuschreibung stand trotzdem da.

`[gemessen]` — 14.08.2026, 19:50 UTC, derselbe Knoten, ein Gedanke über die Periheldrehung des Merkur, diesmal mit dem Materialblock:

> *„**Person A** stellt fest, dass die newtonsche Mechanik eine spezifische, messbare Abweichung beim Perihel-Vorlauf des Merkur aufweist … Person A hinterfragt, ob diese mathematische Unvollkommenheit nicht vielmehr als ein Signal für eine tieferliegende Struktur zu deuten ist."*

Und die Antwort daraus: *„Weißt du, ich muss ständig an diese 43 Bogensekunden denken … Ist das nicht wahnsinnig?"* — sie **spielt** den Gedanken, statt auf ihn zu reagieren.

**Die Zuschreibung ist von Person B auf Person A gekippt, zwischen zwei Turns desselben Tages, ohne dass ein Verbot geändert wurde.** Der Prompt-Log belegt die Ursache: Der Gedanke steht im System-Prompt unter `[EIGENER GEDANKE]`, die Nachricht in der Rolle des Gegenübers trägt nur den Auftrag.

> ⚠ **Ein Turn ist keine Messung.** Am 14.08.2026 wurde aus genau einem Turn geschlossen, die dritte Person trage — nachgemessen duzten danach 9 von 14. Was hier anders ist, ist die Art der Zusicherung, nicht ihre Belegdichte: Eine Struktur kann nicht ignoriert werden wie ein Satz. Der Anteil zugeschriebener Antworten gehört über einen Tag gemessen, bevor daraus etwas folgt.

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Ein eigener Gedanke erreicht die erzeugenden Stufen als **Material** in einem eigenen Block, nicht als Nachricht in der Rolle des Gegenübers. Der Auftrag führt ihn ein; der Reiz-Platz bleibt leer. |
| **TEST** | Auf einem Impuls-Turn enthält die Nachrichtenfolge beider Stufen **keinen** Eintrag mit der Rolle des Gegenübers, der den Gedankentext trägt; der Prompt enthält ihn als Block. Auf einem Nutzer-Turn ist es unverändert umgekehrt. Und die Stellen, die den Reiz lesen — Salienz, Verdichtung, Ablage, Leerprüfung —, melden auf einem Impuls-Turn **keinen Ausfall**. |
| **MESSUNG** | Über einen Tag mit Impulsen: Anteil der Antworten, die den Gedanken einer Person zuschreiben, gegen den Stand vom 14.08.2026 (13 von 14 an einem Tag, fünf davon wortgleich). Dazu Zeichenzahl und Register. |
| **Gegenprobe** | Den Gedanken wieder auf den Reiz-Platz legen und den Block entfernen: Der Zeuge auf die Rollenzuweisung muss rot werden. **Nicht ausreichend ist eine Gegenprobe im Prompttext** — genau die war viermal grün, während das Verhalten blieb. |

### 5.6 Bauteil F — die Form des Materials

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Die Destillation einer Recherche liefert **Wissen**, nicht Novas Rede: kein Sprecher, kein Register, keine Anrede. Der Auftrag hat die Form einer Aufgabe mit prüfbarer Bedingung und einer Mengenangabe **als Zahl**. |
| **TEST** | Das Destillat enthält keine erste Person und keine Anrede des Gegenübers. Sein Umfang liegt im vorgegebenen Zeichenkorridor. Der Auftrag nennt mindestens eine Bedingung, an der das Ergebnis prüfbar ist. |
| **MESSUNG** | Anteil des fachlichen Vokabulars und Zeichenzahl ueber zwanzig Destillate, gegen den **gemessenen** Stand vom 14.08.2026: ueber 87 Recherche-Destillate **Median 1748 Zeichen** (510 bis 3309, p10 1112, p90 2577), Fachvokabular **1,63 %**. Die frueher genannten rund 2100 Zeichen reproduzieren sich nicht; die 2,07 % waren ueber die Reiz-Texte des Rohturns gemessen und nicht ueber den Stapel - zwei Populationen, kein Widerspruch. |
| **Gegenprobe** | Die Stilzeile zurücknehmen, die Fachbegriffe für Experten verlangt: Der Vokabular-Anteil muss messbar steigen. |

> **Die beiden hängen zusammen und werden trotzdem getrennt gebaut.** F ändert, in welcher Gestalt das Wissen entsteht; E, auf welchem Platz es ankommt. Zusammen gebaut wäre bei einer Verschlechterung nicht mehr trennbar, welches von beiden sie verursacht hat.

**Die Reihenfolge ist E, F, C, A, B, D** — mit zwei Einschränkungen.

**E und F stehen vorn**, weil sie das Material selbst betreffen. Jeder Riegel danach entscheidet auf dem, was sie hinterlassen: C misst die Ähnlichkeit eines Textes, dessen Gestalt F bestimmt, und A ordnet einen Zustand, den E mitprägt. Wer erst die Tore baut und dann das Material ändert, hat die Tore auf einem Bestand gemessen, den es danach nicht mehr gibt.

**Die ältere Begründung bleibt gültig:** C ist die Quelle: Jeder deplatzierte Einwurf schiebt Material in die Session, aus der der nächste Turn liest. A ordnet danach die Energie, B verfeinert den Aufwärtsweg; B setzt C voraus, weil beide dieselben Felder des Stapel-Eintrags befüllen.

**D steht zuletzt, obwohl sein Riegel im Ablauf zuerst greift.** Der Grund ist seine Voraussetzung: Die Haltung muss persistiert sein, und ihre Eingangsgröße trägt einen offenen Defekt (§6). Wer D vorzieht, misst einen Riegel gegen eine Größe, von der bekannt ist, dass sie den Hauptfall nicht trennt.

---
