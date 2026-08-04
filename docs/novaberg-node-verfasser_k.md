# Novaberg — Der Verfasser: Inhalt und Wesen werden getrennt

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — ein Node vor dem Responder, der den fachlichen Inhalt der Antwort bestimmt
**Stand:** 4. August 2026 (Erstfassung 31. Juli 2026)
**Pfad:** novaberg/docs/novaberg-node-verfasser_k.md
**Typ:** Konzept (`_k`)
**Status:** ✅ **gebaut.** Der Knoten läuft im CharacterGraph. Am 04.08.2026 um das Urteilsfeld erweitert — siehe unten.

> **Nachgetragen am 04.08.2026 — was seit der Erstfassung dazukam.**
>
> Der Verfasser liefert nicht mehr nur Prosa, sondern **erst ein Urteil, dann den Text**. Vor der Antwort steht ein Kopfblock aus fünf Zeilen — Prüfung, dreiwertige Bewertung (`trifft_zu` / `trifft_nicht_zu` / `abweichend`), Stärke, Quelle — abgeschlossen durch eine Trennlinie. Ein Sprachmodell legt sich mit dem ersten Token fest; steht die Prüfung vor dem Urteil und das Urteil vor dem Text, kann die Zustimmung nicht mehr vor der Prüfung fallen.
>
> **Kein JSON, mit Grund.** Der Verfasser liefert Prosa bis über 3800 Zeichen; in JSON gepresst hinge der ganze Turn daran, dass das Modell einen langen Freitext fehlerfrei maskiert — ein Ausfall, der im Bestand belegt ist. Misslingt der Kopfblock, ist nur das Urteil weg, nicht die Antwort. Er erzeugt dann **keinen Vorgabewert**, sondern `geliefert=False` samt Fehlerzeile.
>
> Der Aufbau steht in `graph/einwand.py`, die gültigen Werte stehen **nur dort** und werden dem Prompt zur Laufzeit eingesetzt. Konzept des Bauteils: `novaberg-sykophanz-eindaemmung_k.md` §7 B1; übergeordnet `novaberg-klaerung_k.md`.
>
> **Nicht abgedeckt:** der Aufgabenpfad. Bei `task_context_cut` wird der Knoten übersprungen (§5.1), dort entsteht kein Urteil — und der HumanGraph hat ihn ohnehin nicht.
**Voraussetzung:** `novaberg-gv-strategie_k.md` (Dreischicht: Strategie, Absicht, Vehikel)
**Betrifft:** `novaberg-node-responder.md` · `graph/character_graph.py` · `graph/state.py`

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

| | **Verfasser** | **Responder** |
|---|---|---|
| `[AUFGABE]` | ✅ | — |
| `[GEDAECHTNIS]` | ✅ | **—** |
| `[WEB-RECHERCHE]` | ✅ | **—** |
| `[GESPRAECHSVEKTOR]` | ✅ | — |
| `[IDENTITAET]` | — | ✅ |
| `[EIGENE_EMOTION]` | — | ✅ |
| `[KOMMUNIKATION]` | — | ✅ |
| `[REGELN]` | — | ✅ |
| `[DIREKTIVEN]` | — | ✅ |
| Session-Verlauf | ✅ | ✅ |
| fachlicher Inhalt der Antwort | erzeugt ihn | erhält ihn |

**Die beiden fett gesetzten Zeilen sind der tragende Teil.** Der Responder verliert Gedächtnis und Web-Recherche vollständig. Er kann dann nichts aus einem Wissen erfinden, das er nicht sieht — die Lehre aus den vier Fix-Iterationen wird von einer Fallunterscheidung zu einer Eigenschaft der Bauart.

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

## 5. Der Bauteil

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Der Responder erzeugt keinen Inhalt mehr: Er erhält den fachlichen Inhalt fertig und gibt ihm Novas Form. |
| **TEST** | Der System-Prompt des Responders enthält weder `[GEDAECHTNIS]` noch `[WEB-RECHERCHE]`. Das Ergebnis des Verfassers liegt nach dem Lauf im State. Bei `task_context_cut=True` läuft der Verfasser nicht. |
| **MESSUNG** | Live-Turns über wissenschaftliche Themen: Zeit bis zum ersten Token vor und nach der Änderung, und ein Abgleich, ob die Endantwort Aussagen trägt, die im Verfasser-Ergebnis nicht standen. |
| **Gegenprobe** | Den State-Kanal aus `graph/state.py` entfernen: Der Schreibvorgang des Verfassers wird wirkungslos, der Responder bekommt einen leeren Inhalt — die Tests, die den Kanal prüfen, müssen rot werden. |

### 5.1 Der Kontext-Schnitt bleibt gültig

Bei `task_context_cut=True` sieht der Responder heute absichtlich fast nichts — kein Gedächtnis, kein Web, nur Identität, Stil und das Ergebnis der Aufgabe. Das war die Lösung nach vier Iterationen.

**Ein Verfasser, der in dieser Lage Gedächtnis und Web zusammenfasst, holt genau den Input zurück, der entfernt wurde** — nur einen Node früher und in verdichteter Form. Der Verfasser läuft in diesem Fall deshalb **nicht**; der Responder verarbeitet den `[AUFGABE]`-Block wie bisher.

### 5.2 Der Thinker bewertet weiterhin die Endantwort

Nach der Trennung gibt es zwei Texte. Der Thinker sitzt hinter dem Responder und bewertet **das, was Nova gesagt hat** — nicht das, was der Verfasser vorgelegt hat.

**Der Grund ist nicht Bequemlichkeit, sondern §2.3:** Das Verfasser-Ergebnis trägt die Fakten, aber nicht die vollständige Mitteilung. Wer den Inhalt allein bewertet, bewertet eine unfertige Nachricht — und übersähe genau den Teil, den die zweite Stufe beiträgt.

Der Thinker wird deshalb **nicht angefasst**.

### 5.3 Kein Rückfallpfad für den Verfasser

**Es wird kein Weg gebaut, auf dem der Responder in seine heutige Bauart zurückfällt.** Ein Rückfall wäre eine zweite, selten gelaufene Architektur im selben Graphen — und die Erfahrung mit selten gelaufenen Zweigen steht im Bestand.

Der zu erwartende Fehlerfall ist auch ein anderer: Der Verfasser wird kaum ausfallen, er wird **falsch liegen**. Gegen inhaltlichen Unsinn hilft kein Rückfallpfad, sondern nur die Messung am laufenden System.

**Was ein technischer Ausfall trotzdem nicht darf:** wie eine Antwort aussehen. Bleibt das Ergebnis leer, wird das laut gemeldet und der Turn scheitert sichtbar — er wird nicht mit einer Antwort überdeckt, die auf nichts steht. Das folgt aus der allgemeinen Regel gegen stille Fehler und ist keine eigene Entscheidung.

### 5.4 Der Kanalzwang

Das neue State-Feld muss in `graph/state.py` deklariert **und** in `graph/base.py` initialisiert werden. Ein Schreibvorgang in einen nicht deklarierten Kanal ist stillschweigend wirkungslos — die Belegstelle dafür liegt als eigene Lesson im Bestand.

---

## 6. Was offen ist

- **Die Namen der Blöcke im Verfasser-Prompt.** Ob er dasselbe `[BLOCKNAME]`-Schema trägt wie der Responder oder ein eigenes, ist nicht entschieden. Für dasselbe spricht die Einheitlichkeit, dagegen, dass seine Blöcke einen anderen Adressaten haben.
- **Ob der Verfasser den Session-Verlauf in voller Länge braucht.** Er ist der größte einzelne Posten im Kontext. Eine Kürzung wäre wirksam und ist unbelegt — sie gehört gemessen, nicht geschätzt.
- **Wie gut der Verfasser inhaltlich trifft.** Das ist die eigentliche offene Frage und der Grund für den eigenen Zweig: Sie ist nicht durch Nachdenken zu beantworten, sondern am laufenden System.

---

## 7. Die Regeln sind zur Probe ausgesetzt (31.07.2026)

`[REGELN]` läuft nicht mehr — Antwortkürze, verbotene Floskeln, Butler-Prinzip, Tag-Unterdrückung, das Verbot falscher Erfolgsmeldungen.

**Der Grund ist nicht Aufräumen.** Jede dieser Regeln ist gegen ein Verhalten gewachsen, das der überladene Prompt hervorbrachte: Ein Modell, das gleichzeitig Wissen sichten, Inhalt bestimmen und Form finden soll, greift zu Floskeln. Seit der Trennung ist diese Ursache weg — ob die Narben noch gebraucht werden, ist damit eine offene Frage, und sie ist nur zu beantworten, indem man sie einmal weglässt.

**Belegt ist bereits, dass mindestens eine widersprach:** Die Regeln untersagten Rückfragen (*„Soll ich…?", „Möchtest du…?"*), während der Gesprächsvektor im selben Turn `Vehikel: Frage` und eine Landschaft mit *„Fragen: Mittel, neckisch, oft rhetorisch"* gewählt hatte. Ein pauschales Verbot schlug eine gemessene Vorgabe.

**Der Prompt-Baustein bleibt bestehen; nur der Aufruf entfällt.** Zurückgeholt wird die einzelne Zeile, die sich als nötig zeigt — nicht der Block.

**Erster Befund aus dem Betrieb:** Die Kürze fehlt. Sie kommt aber nicht als Regel zurück, sondern als Grenze aus dem Haltungsraum.

---

## Versionshistorie

- **v0.3 — 31.07.2026:** Zwei Aussagen live widerlegt und an ihrer Stelle markiert. §2.4 — der Schutz „der Leitgedanke ist die Richtung, nicht der Text" war **tragend**; ohne ihn formuliert niemand um, und die Kette reichte den Hypothesentext des Hintergrundagenten unverändert bis zum Nutzer durch. §2.3 — „lässt keine weg" machte die Kürze unbefolgbar und ist aufgehoben; hinzufügen bleibt verboten. Neu §7: Die Regeln sind zur Probe ausgesetzt, samt Beleg, dass mindestens eine der gemessenen Vorgabe des Gesprächsvektors widersprach. Woher die Länge stattdessen kommt, steht in `novaberg-haltungsraum_k.md`.
- **v0.2 — 31.07.2026:** Zwei offene Punkte entschieden. Der Thinker bewertet weiterhin die **Endantwort**, weil erst Novas Art die vollständige Mitteilung ergibt — daraus §2.3, das den Satz „der Responder entscheidet keinen Inhalt" auf **Fakten** einschränkt: Bedeutung fügt er sehr wohl hinzu. Und es wird **kein Rückfallpfad** gebaut; der erwartete Fehlerfall ist nicht der Ausfall, sondern der inhaltliche Irrtum, und dagegen hilft nur die Messung. Ein technischer Ausfall bleibt laut.
- **v0.1 — 31.07.2026:** Erstfassung. Die Trennlinie folgt dem Dreischicht-Modell des Gesprächsvektors: Strategie, Absicht und Vehikel gehören zum Inhalt, nicht zum Wesen. Der Responder verliert Gedächtnis und Web-Recherche vollständig; damit wird die Lehre aus den vier Fix-Iterationen von einer Fallunterscheidung zu einer Eigenschaft der Bauart. Zwei Alternativen mit Begründung verworfen (reine Verdichtung, strukturierter Antwortauftrag). Vier Punkte ausdrücklich offen.
