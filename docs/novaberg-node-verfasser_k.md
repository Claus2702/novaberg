# Novaberg — Der Verfasser: Inhalt und Wesen werden getrennt

**Absicht:** Ein eigener Knoten vor dem Responder — der Verfasser — bestimmt den fachlichen Inhalt der Antwort aus Gedächtnis, Aufzeichnungen, Recherche, Sachlage und Gesprächsvektor; der Responder sieht dieses Wissen nicht mehr und gibt dem fertigen Inhalt nur Novas Form.
**Stand:** 19. September 2026 (am selben Tag in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *`verfasser` — der Inhalt vor der Form* 🔴 · *Haltungsraum — der zweite Leser (Verfasser)* 🟡 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-node-verfasser_t.md`](novaberg-node-verfasser_t.md) · [`novaberg-node-verfasser_b.md`](novaberg-node-verfasser_b.md) · [`novaberg-node-verfasser_e.md`](novaberg-node-verfasser_e.md) · [`novaberg-node-verfasser_m.md`](novaberg-node-verfasser_m.md)
**Entschieden:** 1 · **Offen beim Meister:** 1 (Liste in [`novaberg-node-verfasser_e.md`](novaberg-node-verfasser_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-node-verfasser_k.md §2.2a` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-node-verfasser_t.md`](novaberg-node-verfasser_t.md), `_b` ist [`novaberg-node-verfasser_b.md`](novaberg-node-verfasser_b.md), `_e` ist [`novaberg-node-verfasser_e.md`](novaberg-node-verfasser_e.md), `_m` ist [`novaberg-node-verfasser_m.md`](novaberg-node-verfasser_m.md).

| § | Datei |
|---|---|
| 1 | `_k` |
| 2 · 2.1 · 2.2 · 2.3 · 2.4 | `_k` (2.2 mit Hinweis) |
| 2.2aa · 2.2ab · 2.2a · 2.2a-2 · 2.2a-3 · 2.2b · 2.2c | `_t`; aus 2.2aa der `[gemessen]`-Absatz vom 18.08.2026, aus 2.2a-2 der `[gemessen]`-Absatz über 156 Impuls-Turns und aus 2.2a-3 die Betriebsbelege vom 11.09.2026 (ab *„Der Block wirkt“*) in `_m` |
| 3 · 3.1 · 3.2 · 3.3 | `_k` |
| 4 | `_k` |
| 5 · 5.1 · 5.2 · 5.3 · 5.4 | `_b` (5 mit Hinweis) |
| 6 | `_e` |
| 7 | `_b`; die Absätze *Erster Befund aus dem Betrieb* und *Zweiter Befund, am Bestand gemessen am 15.09.2026* in `_m` |
| Versionshistorie (v0.1 bis v0.8) | `_e` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Status, Voraussetzung, Betrifft) | `_m` |
| Nachträge am bisherigen Kopf (04.08.2026, 05.08.2026, *Nicht abgedeckt*, 22.08.2026) | `_b` |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## 1. Die Beobachtung

Der Responder ist der Node, der **alles** sieht: Gedächtnis, Web-Recherche, Aufgabe, Gesprächsvektor, Identität, Emotion, Kommunikationslage, Regeln, Direktiven. Er entscheidet daraus in **einem** Zug, was gesagt wird und wie es klingt.

Das ist keine Vermutung, sondern steht als Bauart im Moduldokument: *„Er ist bewusst der Node mit dem breitesten Input, weil Generierung (anders als Bewertung) den vollen Kontext braucht."*

**Der Code dokumentiert selbst, was das kostet.** Der Sprachstil-Block wird nicht in den System-Prompt gesetzt, sondern ans **Ende der Nutzer-Nachricht** — mit dieser Begründung im Kommentar:

> *„Der Sprachstil steht am ENDE der Nutzer-Nachricht, hinter dem Verlauf und hinter dem aktuellen Prompt — dort, wo eine Anweisung gegen 8.400 Tokens fremder Prosa noch etwas ausrichtet."*

Eine Stilanweisung, die einen Platz gegen den Kontext *erkämpfen* muss, ist ein Symptom. Sie steht nicht dort, wo sie hingehört, sondern dort, wo sie überlebt.

**Zwei Befunde aus dem Bestand zeigen dieselbe Richtung** (`auditiert`, aus `novaberg-node-responder.md`):

- Die Halluzination bei Agent-Erfolg überlebte **vier** Fix-Iterationen. Die Lehre: *„Die Lösung war nicht ein stärkerer Prompt, sondern weniger Input."* Der heutige Kontext-Schnitt (`task_context_cut`) ist die Konsequenz — eine Fallunterscheidung, die dem Responder in bestimmten Lagen fast alles wegnimmt.
- Rund 68 Zeilen Geschäftslogik wanderten aus dem Responder in den Planner. Der Grundsatz daraus: **die Interpretation gehört zum Produzenten, nicht zum Konsumenten.** Der Responder konsumiert seither einen fertigen `[AUFGABE]`-Block.

Beide Male war die Antwort dieselbe Bewegung: dem Responder eine Entscheidung abnehmen und ihm ein Ergebnis geben. Dieses Konzept führt sie zu Ende.

---

## 2. Was gelten soll

**Der Responder entscheidet keinen Inhalt mehr.**

Er erhält den fachlichen Inhalt der Antwort fertig und gibt ihm Novas Form: ihr Wesen, ihren Charakter, ihre Art, ihre Laune, ihre Stimmung, ihre Haltung, ihre Loyalität, ihre Distanz.

Ein neuer Node — der **Verfasser** — sitzt zwischen GV-Node und Responder und bestimmt, **was** gesagt wird.

```
… → reducer → router → [planner] → gv_node → ▶ verfasser ◀ → responder → thinker → …
```

### 2.1 Die Trennlinie steht schon im Dreischicht-Modell

`novaberg-gv-strategie_k.md` teilt die Antwortgestaltung in drei Schichten:

```
Strategie = WAS  ich tue         (7 Strategien)
Absicht   = WARUM ich es tue     (4 Absichten)
Vehikel   = WIE ich es verpacke  (3 Formen: Aussage, Frage, Schweigen)
```

**Alle drei gehören zum Inhalt, nicht zum Wesen.** Auch das Vehikel: Ob Nova antwortet, zurückfragt oder schweigt, ist eine Entscheidung über die Substanz. Ein Schweigen lässt sich nicht stilistisch nachformen.

Der Gesprächsvektor hat seine Wahl damit bereits getroffen, bevor der Verfasser läuft. Der Verfasser führt sie aus; er erfindet keine zweite Strategie.

### 2.2 Wer was sieht

> **Hinweis zur Aufteilung (19.09.2026):** Die Tabelle legt die Trennlinie zwischen den beiden Stufen fest und bleibt deshalb hier; ihre Zellen tragen den Baustand der Blöcke mit Datum. Die Ausarbeitung einzelner Blöcke (§2.2aa bis §2.2c) steht in [`novaberg-node-verfasser_t.md`](novaberg-node-verfasser_t.md).

| | **Verfasser** | **Responder** |
|---|---|---|
| `[AUFGABE]` | ✅ | — |
| `[GEDAECHTNIS]` | ✅ | **—** |
| `[AUFZEICHNUNGEN]` | ✅ | **—** |
| `[WEB-RECHERCHE]` | ✅ | **—** |
| `[SACHLAGE]` | ✅ | — (seit 28.08.2026: Gegenstand, vermutetes Nutzerziel, offene Eigenschaften akuter Objekte; seit 28.08. spät je Deckung aus dem Gedächtnis *»Dazu weiss Nova schon (aus …)«* (Scheibe 6); seit 29.08. je Plausibilitätsbefund *»Zweifel (Stufe): Behauptung — Grund«* (Scheibe 7), je Welt-Eigenschaft *»Der Nutzer will zu … wissen: … — beantworte es«* und je Suchtreffer *»Nachgeschlagen zu …«* (Scheibe 8); seit 29.08. mittags je gedeckter Eigenschaft mit Sprecher *»Der Nutzer hat zu … gesagt: …«* / *»Nova hat schon zu … gesagt: …«* (Scheibe 9, `speaker_lines`) — `graph/nodes/sachlage.py::sachlage_block`, `novaberg-thinking-lage_k.md`; **seit 29.08. spät in den Namen des Lesers:** hier *Person A* und *Person B* (*»Person B will zu … wissen: … — Person A beantwortet es aus ihrem Wissen«*), beim Gesprächsvektor *Nova* und *der Nutzer* — bis dahin trug der Block *»der Nutzer«*, *»Nova«* und *»beantworte es aus deinem Wissen«* in diesen Prompt, das zweite und dritte Namenssystem (§2.2b); steht vor dem Gesprächsvektor: erst worum es geht, dann wie es sich bewegt. Drei unterscheidbare Ausgänge: Block · gelaufen-und-leer als `info` · nicht gelaufen als `error`) |
| `[SACHLAGE-BRUECKE]` | ✅ | — (seit 28.08.2026, nur auf Impuls-Turns mit zweitem Ende: die Sachlage des Turns, aus dem der Gedanke entstand, neben der aktuellen — `sachlage_bridge_block`, `novaberg-thinking-lage_k.md` §4 Scheibe 4. Nennt, ob der Anlass belegt (`turn_id`) oder erschlossen ist (Embedding-Rückfall mit Kosinus), und trägt den Auftrag, den Übergang hörbar zu bauen. Fehlt die Brücke, fehlt der Block ohne Fehlerzeile — der Knoten hat den Grund schon protokolliert) |
| `[GESPRAECHSVEKTOR]` | ✅ | — (seit 12.09.2026 bei einer Bitte des Menschen, `intent = task`, mit der Vorgabe *»Person B hat um etwas Konkretes gebeten. Person A liefert es zuerst …«* — in den Namen dieses Lesers; **entschieden im GV-Knoten**, hier nur aus `gv_detail['bitte_zuerst']` gelesen: bei `task` immer, bei `knowledge` nach dem Zuwendungsrad) |
| `[MASS]` | ✅ | — (die Zahl steht dort in `[REGIE]`). **Die Rückfrage-Zeile trägt seit dem 27.08.2026 Menge UND Art** („eine Rückfrage, und zwar analytisch — kein Angebot"), aus `CLUSTER_FRAGE_ART` an der Landschaft — nicht am Vehikel, das in 75 % der Parses leer ist (`ei/haltungssprache.py::_rueckfragenzeile`). **Seit dem 28.08.2026 abends auch den Gegenstand** (*»… — ihr Gegenstand: Geburtstag — was dazu noch offen ist: wer«*) aus der Sachlage (`graph/nodes/sachlage.py::question_target`, Scheibe 3 des Lage-Konzepts); bei *»keine Rückfrage«* entfällt er wie die Art — die Haltung bleibt der Regler. Labor: Rückfrage trifft den Gegenstand 4/4 statt 1/4. **Seit dem 29.08.2026 abends trägt der Gegenstand seine Herkunft:** Ist er Novas Kurzziel außerhalb der Blase (`question_target_origin` → `eigener_zug`), führt die Zeile *»das ist Person As eigenes Ziel, nicht die Sache von Person B — sie nennt es als das, was sie gerade zieht, und lässt ihm die Wahl«*; Labor 5/5 statt 0/5 als eigener Schritt, vorher verbog der Stoff das Nutzerthema (Lage-Konzept §4, Scheibe 3 Nachtrag) |
| `[ANGEBOT]` | ✅ | — **seit 18.09.2026 (Scheibe 12 E2).** Steht eine akute Sache am Zettel von Timeline oder Notizen, hat niemand darum gebeten und lässt Novas Pflichtbewusstsein zum Menschen es zu, bietet Person A — ~~ab `ANGEBOT_PFLICHT_SCHWELLE` 0,9~~ → seit 18.09.2026, 21:41 UTC: unter `ANGEBOT_PFLICHT_BODEN` 0,33 nie, darüber mit einer Wahrscheinlichkeit ~~je Turn~~ → je Sache (seit 19.09.2026, siehe unten), die linear auf 100 % bei 1,0 steigt (gezogen im Code, Zug und Wahrscheinlichkeit im Log) — am Ende an, sie einzutragen oder zu notieren (`prompts/default/verfasser.angebot.txt`; seit 18.09.2026, 22:13 UTC nennt der Satz die Sache beim Namen, und die angebotene Sache steht für den Dispatcher in `state["angebot_kandidat"]`). Nicht auf einem Impuls, nicht für eine abgelehnte Sache (E3), **seit 19.09.2026 pro Sache**; das Verb (*eintragen*/*notieren*) kommt vom **nächsten** schreibenden Dienst der Sache, nicht vom ersten nach Name (`utils/offers.py::_writing_services`, seit 18.09.2026 — vorher sagten 4 von 4 Terminangebote *„notieren"*); für eine Sache wird je Paar in der Frist `ANGEBOT_VERFALL_SEKUNDEN` einmal gewürfelt (`utils/offers.py::draw_recorded`), Ausgänge `schon_gewuerfelt` und `wurf_unbekannt`; eine Ablehnung als Nicht-Auftrag (`Korrektur.kein_auftrag`) sperrt das Angebot nicht. Jeder Ausgang als `verfasser.angebot` im Pipeline-Log. |
| `[IDENTITAET]` | — | ✅ |
| `[EIGENE_EMOTION]` | — | ✅ |
| `[KOMMUNIKATION]` | — | ✅ |
| `[REGELN]` | — | ✅ |
| `[DIREKTIVEN]` | — | ✅ |
| `[GESPRAECHSVERLAUF]` (Session-Verlauf) | ✅ | ✅ | — die bisherigen Turns, älteste zuerst; `Nova (von sich aus)` markiert eine Äußerung, die sie selbst begonnen hat. **Die Zeile stand bis zum 01.09.2026 als *Session-Verlauf* hier** und nannte den Block damit nicht bei seinem Namen — für jede Prüfung, die Blocknamen gegen den Code hält, fehlte er |
| fachlicher Inhalt der Antwort | erzeugt ihn | erhält ihn |

**Die beiden fett gesetzten Zeilen sind der tragende Teil.** Der Responder verliert Gedächtnis und Web-Recherche vollständig. Er kann dann nichts aus einem Wissen erfinden, das er nicht sieht — die Lehre aus den vier Fix-Iterationen wird von einer Fallunterscheidung zu einer Eigenschaft der Bauart.

> **§2.2aa bis §2.2c** — Aufzeichnungen neben dem Gedächtnis, Wissensblöcke über Person A, die Herkunft des Reizes, Anschluss und Brücke des Impulses, der Auftrag als Aufgabe, der Gesprächsvektor-Block — stehen in [`novaberg-node-verfasser_t.md`](novaberg-node-verfasser_t.md).

### 2.3 Die Art ist selbst Information

**Das Ergebnis des Verfassers ist nicht die vollständige Nachricht.** Erst durch Novas Art kommen alle Informationen in die Kommunikation: Nähe oder Distanz, Zustimmung oder Vorbehalt, Wärme oder Zurückhaltung stehen nicht in den Fakten, sondern in der Form, in der sie gesagt werden.

Das schärft den Satz aus §2. „Der Responder entscheidet keinen Inhalt mehr" heißt: **Er entscheidet keine Fakten.** Er fügt keine Behauptung hinzu, die im Verfasser-Ergebnis nicht stand. Bedeutung fügt er sehr wohl hinzu — das ist seine Aufgabe.

> **Weglassen ist erlaubt, ergänzt am 31.07.2026.** Ursprünglich stand hier „und lässt keine weg". Das machte die Kürze-Regel unbefolgbar: Länge ist formal Stil, folgt aber aus dem Inhalt — solange der Responder nichts weglassen durfte, war für den Umfang **niemand** zuständig. Hinzufügen bleibt die harte Grenze; wie viel gesagt wird, entscheidet sie. Woraus sich das ergibt, steht in `novaberg-haltungsraum_k.md`.

Daraus folgt unmittelbar, was der Thinker bewertet (§5.2).

### 2.4 Der Leitgedanke

Der Gesprächsvektor liefert heute einen `impuls` — im Prompt als *„Dein Leitgedanke für diese Antwort"*, mit dem Zusatz *„Finde deine eigenen Worte — der Leitgedanke ist die Richtung, nicht der Text."*

**Der Leitgedanke geht an den Verfasser.** Er verändert, was gesagt wird: Eine Querverbindung oder eine Überraschung ist Inhalt, nicht Tonfall.

~~**Der Zusatz entfällt.** „Finde deine eigenen Worte" ist ab dann keine Bitte mehr, sondern die Aufgabe der zweiten Stufe. Eine Anweisung, die beschreibt, was die Architektur ohnehin erzwingt, ist Prompt-Gewicht ohne Wirkung.~~ → **Widerlegt am 31.07.2026, live gemessen.**

Der Schutz war tragend. Die Begründung enthielt ihr eigenes Gegenteil: §2.3 verbietet dem Responder, den Inhalt zu ändern — damit formuliert **niemand** um. Beim ersten Lauf reichte die Kette den Hypothesentext des Hintergrundagenten unverändert bis zum Nutzer durch.

Der Schutz steht jetzt beim Verfasser, verschärft: *„Schreibe ihn niemals ab und übernimm keine seiner Formulierungen — er beschreibt, was der Nutzer tut, nicht was du sagst."* Der Zusatz ist wichtig — die Hypothese ist eine Beobachtung **über** den Nutzer; wörtlich weitergereicht wird sie zur Konfrontation.

---

## 3. Warum so und nicht anders

### 3.1 Verworfen: nur verdichten statt formulieren

Der Verfasser könnte Gedächtnis und Web bloß **auswählen und kürzen**, ohne eine Antwort zu bestimmen. Das träfe das Token-Problem und wäre billiger.

**Verworfen**, weil es die Entscheidung nicht verschiebt. Der Responder bliebe der Ort, an dem Inhalt und Form gemeinsam entstehen — nur mit kürzerem Input. Die Stilanweisung stünde weiterhin gegen fremde Prosa, nur gegen weniger davon.

### 3.2 Verworfen: ein strukturierter Antwortauftrag statt eines Inhalts

Der Verfasser könnte einen **Auftrag** liefern — welche Fakten zu verwenden sind, was wegzulassen ist, was zurückzufragen wäre — und der Responder schriebe daraus die Antwort.

**Verworfen**, weil diese Entscheidungen bereits gefallen sind, bevor der Verfasser läuft: Der Router hat den Weg gewählt, der Planner das Ergebnis der Aufgabe geliefert, der Gesprächsvektor Strategie, Absicht und Vehikel. Ein Auftrag, der das noch einmal in Anweisungen fasst, wäre eine dritte Instanz, die dieselbe Wahl ein weiteres Mal trifft.

### 3.3 Der bewusst getragene Preis

**Zwei erzeugende Stufen können über den Wortlaut auseinanderlaufen.** Weicht die Endantwort vom Inhalt ab, ist ohne Messung nicht unterscheidbar, ob das Stil war oder eine Inhaltsänderung.

Zwei Dinge halten das in Grenzen, und beide sind Bauart statt Bitte:

- Der Responder **sieht das Wissen nicht**. Was er hinzufügen könnte, müsste er frei erfinden — nicht aus einer Quelle beziehen, die neben ihm liegt.
- Die Abweichung ist **messbar**: Beide Texte existieren getrennt im State und lassen sich vergleichen.

**Der zweite Preis steht auf der Uhr.** Der Responder streamt seine Antwort zum Client. Ein Node davor verlängert die Zeit bis zum **ersten Token**, nicht nur die Gesamtdauer. Das ist der einzige Teil dieses Konzepts, der für den Nutzer unmittelbar spürbar ist, und er wird gemessen, bevor er akzeptiert wird (§5).

---

## 4. Was ausdrücklich nicht enthalten ist

- **Keine Änderung an GV-Node, Planner, Router oder Thinker.** Sie treffen ihre Entscheidungen unverändert.
- **Keine Umformulierung der Blöcke.** Die Blockinhalte werden **verschoben, nicht neu geschrieben**. Sonst vermischt sich der Schnitt mit einer Prompt-Überarbeitung, und eine Verschlechterung wäre nicht mehr einer der beiden Ursachen zuzuordnen.
- **Keine zweite Wissensquelle.** Der Verfasser bekommt, was der Responder heute bekommt — nicht mehr.
- **Kein neues Modell.** Beide Stufen laufen auf dem bestehenden Chat-Backend. Ob die Inhaltsstufe später ein anderes Modell verdient, ist eine eigene Frage.

---

> **§5 Der Bauteil** (mit §5.1 bis §5.4) und **§7 Die Regeln sind zur Probe ausgesetzt** stehen in [`novaberg-node-verfasser_b.md`](novaberg-node-verfasser_b.md); **§6 Was offen ist** und die **Versionshistorie** in [`novaberg-node-verfasser_e.md`](novaberg-node-verfasser_e.md).
