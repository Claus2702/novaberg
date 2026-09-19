# Novaberg — Bugs: Gedächtnis — KZG, LZG, Promotion, Entitäten, Salienz, Verfall

**Inhalt:** die offenen Defekte dieses Gegenstands, 16 Eintraege, je mit `**Kategorie:** GED`.
**Wegweiser:** [`novaberg-bugs.md`](novaberg-bugs.md) — Kopf, Form eines Eintrags, Rangfolge, Verlauf. **Findemittel ueber alle Teile:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Archiv:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Register** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

---

## 04.09.2026 — die Verstärkung hängt am falschen Ereignis

Drei Kennungen aus einer Frage des Eigentuemers: *„EI-Calc ist lesend. Lesend verstaerkt nicht. Erzeugte Prompts reaktivieren und verstaerken. Kollidieren wir hier?"* Die Antwort ist ja — und die Ursache liegt tiefer als die Frage: **Nicht das Lesen verstaerkt, sondern die blosse Nachbarschaft im Schreibpfad.** Die verfeinerte Regel steht seit heute in `novaberg-memory-synapsen_k.md` §7.1a.

### `KZG-EINTRAG-BLEIBT-NACH-PROMOTION` — der Eintrag verstaerkt seinen eigenen Knoten
**Kategorie:** GED

**Zustand:** offen — am Bestand gemessen am 04.09.2026.

**Symptom.** `novaberg-memory-synapsen_k.md` §7.7 verlangt woertlich: *„Der KZG-Eintrag wird nach erfolgreicher Promotion vollstaendig aus Redis geloescht. […] Das macht den Schritt 4 der Promotion einfach: `DEL kzg:{user}:{char}:{id}`."*

**Der Code sagt ausdruecklich das Gegenteil.** `agents/synapsen_promotion/agent.py`, Modul-Docstring: *„Der KZG-Hash wird wie im alten Pfad NICHT geloescht — er verfaellt ueber seine TTL."* Ein Grep ueber die Datei findet kein `DEL` auf den KZG-Schluessel; geloescht werden nur die Queue-Listen.

**Wirkung.** Der Eintrag lebt weiter, geht erneut in die Promotion und **matcht dort den Knoten, der aus ihm selbst entstanden ist**:

| | |
|---|---:|
| Reinforcements gesamt | **14.947** auf 1.538 Knoten (Faktor 9,7) |
| davon mit `cosine = 1.0000` | **14.227 = 95,2 %** |
| Maximum je (Turn, Knoten) | **91** |
| verteilt ueber | **8 und mehr Kalendertage** |

Ein Knoten steht bei `haeufigkeit` 92 aus **einem einzigen** Turn; sein `gewicht_roh` liegt bei 10,10 an der Kappung `LZG_KNOTEN_GEWICHT_CAP`.

**Dasselbe Bild gab es am 12.07.2026** — 2.910 Reinforcements auf 302 Knoten, Faktor 9,6, `cosine_max = 1.0000`. Damals wurde der **ganze Bestand zurueckgesetzt**; die Ursache war das casing-blinde Embedding, das seither gewechselt hat. **Gleiches Bild, andere Ursache** (der Bruch-Hinweis steht in `novaberg-memory-synapsen_k.md` Punkt 9).

**Was fertig waere.** Schritt 4 der Promotion loescht den KZG-Hash, und eine Wiederholungsmessung zeigt `cosine = 1.0000` nur noch dort, wo sie hingehoert: nirgends.

**Prioritaet:** hoch — der Defekt verfaelscht `haeufigkeit` und `gewicht_roh` des gesamten LZG.

### `KZG-THEMA-VERSTAERKT-NACHBARN` — ein geteiltes Thema genuegt
**Kategorie:** GED

**Zustand:** offen — am Bestand gemessen am 04.09.2026.

**Symptom.** `memory/kzg.py:486` scannt bei **jedem** `kzg_store` die ganze Paar-Partition (`redis_client.keys(prefix*)`) und verstaerkt **jeden** Eintrag, der mindestens **ein einziges Thema** teilt: `haeufigkeit` +1, Salienz neu gerechnet, **und die TTL neu gesetzt**.

`[gemessen]` 04.09.2026 ueber 2.911 KZG-Eintraege des Paares `meister:nova`, Stichprobe 400:

| | |
|---|---:|
| `haeufigkeit` im Mittel | **8,1** |
| Maximum | **110** |
| Eintraege mit mindestens einer Verstaerkung | **257 von 400 = 64 %** |

**Wirkung.** Das ist die Sperre aus §7.1a von der anderen Seite: **Verstaerkung durch Nachbarschaft, nicht durch Verwendung.** Ein Eintrag mit gaengigen Themen steigt ueber `KZG_SALIENZ_HIGH`, bekommt bei jedem verwandten Turn 30 Tage TTL neu und laeuft nie ab — womit er dauerhaft Futter fuer `KZG-EINTRAG-BLEIBT-NACH-PROMOTION` liefert. **Die beiden Defekte bilden zusammen eine geschlossene Schleife**, und keiner von beiden allein erklaert die Zahlen.

**Was fertig waere.** Die thematische Verstaerkung folgt §7.1a: Sie greift nur fuer Eintraege, die in der Antwort tatsaechlich hergenommen wurden — oder sie faellt weg.

**Prioritaet:** hoch.

## Einzelbefunde ohne eigenen Datumsabschnitt

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

*Die Einträge dieses Abschnitts standen bis zum 19.09.2026 ohne eigene Überschrift unter dem Abschnitt vom 25.08.2026, zu dem nur der erste Eintrag davor gehört. Ihre Befunddaten reichen vom 05.08. bis zum 18.09.2026.*

### `ENTITAETIDS-MIT-DUBLETTEN` — Dubletten in der Liste
**Kategorie:** GED

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. keine Deduplizierung auf dem Schreibweg; die Zahl im Bestand braucht einen Messlauf.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **`entitaet_ids` trägt Dubletten.** In 3 von 84 belegten KZG-Arrays steht dieselbe Entitäts-ID mehrfach, etwa `193,269,871,196,870,193,194`. Die Achse ist nach `novaberg-convention-magneten.md` §2.1 **referenziell und n:m** — eine Erinnerung betrifft eine Entität oder nicht; ein zweites Vorkommen bedeutet nichts. **Die Enthaltenseins-Suche bleibt richtig** (`entitaet_ids @> ARRAY[x]` trifft weiterhin), aber jede Zählung über die Achse ist verzerrt, und §4 nennt für die Cluster-Aggregation ausdrücklich die *Vereinigung* der `entitaet_ids` — eine Vereinigung, die Dubletten mitschleppt, ist keine. Gefunden beim Halten der Magneten-Konvention gegen den Bestand. **Nicht mitgeändert:** Ob dedupliziert wird und wo — beim Auflösen, beim Schreiben oder beim Lesen — ist eine Entscheidung.

**Geschlossen, wenn** `entitaet_ids` traegt jede Kennung einmal.

---

## Chat 148 (18.08.2026) — aus der Werkzeugreihe Vera

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Antwortpfad](novaberg-bugs-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Drei Defekte aus einem 20-Turn-Bogen auf einem eigenen Paar (`vera`), mit angehaltenem Pixie gefahren. Die Reihe liegt in `labor/bogen/bogen_vera_werkzeuge.yaml`, das Ergebnis in `labor/ergebnis/`.

### `FALSCHE-BESTAETIGUNG-WIRD-ERINNERUNG`
**Kategorie:** GED

**Zustand:** offen — gegen HEAD `9bcd214` nachgesehen am 24.08.2026, unveraendert seit `62560cf`. **Die zweite Haelfte ist gebaut:** Die Verdichtung sieht den Ausgang. `agents/kzg/dispatch.py::abgelehnte_ausgaenge` zieht die abgelehnten Dienste samt Befund aus `agent_results`, und `agents/kzg/verdichtung.py` setzt daraus den Block `[TATSAECHLICHER AUSGANG]` **vor** das Bewertungsobjekt — als Tatsache, nicht als Regel. Elf Zeugen (`tests/test_kzg_ausgang_im_kern.py`), Gegenprobe 3 vorhergesagt / 3 gezaehlt, Suite `Ran 2067 tests — OK`. Im Betrieb belegt am 22.08.2026, 00:16 UTC: `timeline` lehnte ab, `Ausgangsblock gesetzt — 1 abgelehnte(r) Dienst(e)`, der Kern trug reinen Inhalt.

> **Der Eintrag bleibt trotzdem offen, und zwar aus zwei Gruenden.** Erstens: Die Antwort jenes Messturns behauptete gar keine Handlung — belegt ist, dass der Weg **laeuft**, nicht dass er den Fehler **verhindert**. Der scharfe Fall verlangt eine Antwort, die eine abgelehnte Handlung bestaetigt, und den stellt das Modell her, nicht der Messende. Zweitens: Die erste Haelfte — dass die Antwort selbst keine Bestaetigung enthaelt — haengt weiter an einer Anweisung im Prompt der Figur (`server/graph/nodes/planner.py`, seit dem 20.08.2026) und ist keine Zusicherung.

> **Nachgesehen am 24.08.2026 gegen HEAD `9bcd214`: unveraendert in der Sache, der Zeiger ist tot.** `planner.py:67` traegt heute den `refusals`-Filter. Die Anweisung steht in der Prompt-Vorlage `responder.aufgabe_ablehnung`, gesetzt von `_build_task_ablehnung` (`:165`) — sie ist damit weiterhin eine Anweisung an die Figur und keine Pruefung im Code. Der einzige Riegel dort ist eine Ausgabe-Verifikation auf **leeren Text**, nicht auf eine Bestaetigung.

> **Gebaut am 15.09.2026: Die erste Hälfte hängt nicht mehr an der Anweisung, sie wird gerechnet.** Die Auswertung des Tribunals erkennt eine Speicherbehauptung in der Antwort und hält sie gegen die Ausgänge der Dienste des Turns; ohne `abgeschlossen` — auch bei `abgelehnt`, `fehler` oder `rueckfrage` — geht die Antwort in die Korrekturrunde (`utils/storage_claims.py`, `graph/nodes/tribunal.py::_storage_claim_step`; `novaberg-node-tribunal.md`, *Die Speicherbehauptung*). **Der Originalfall dieses Eintrags ist darunter:** Die Antwort vom 18.08.2026, 00:05 UTC, kam in der echten Korrekturrunde unter `gemma4-a4b-gpu` als Wiedergabe des Wunsches zurück, ohne die Bestätigung; die Erklärung des Fehlschlags blieb stehen `[gemessen 15.09.2026, Labor, Lauf 3]`. Über alle 24 Behauptungen des Bestands ab 14.08.2026: **20 sauber, 2 Grenzfälle, 2 überstanden beide Runden**.
>
> **Der Eintrag bleibt offen.** Die Schließbedingung verlangt eine Antwort ohne Bestätigung — zwei von 24 behielten sie über beide Runden, gemeldet und nicht verhindert. ~~Ob eine solche Behauptung aus der Antwort entfernt wird, ist offen~~ → **am 16.09.2026 entschieden, nicht gebaut:** Sie wird nicht entfernt; ein Korrektursatz wird angehängt, der Ausgang am Turn vermerkt, und ein später gefundener Fall am Gedächtnisknoten nachgetragen — also genau an dieser Kennung (`novaberg-thinking-lage_k.md`, Scheibe 12, *Offen für den Bau*). Und der scharfe Fall im **Betrieb** — ein Dienst lehnt ab, die Antwort bestätigt, die Korrektur beseitigt es — ist nicht gemessen; im Betrieb belegt ist nur der dauerhafte Eintrag der Prüfung.

**Befund.** Nach dem misslungenen Notizauftrag antwortete Nova: *„Ich habe es notiert... also, ich wollte es gerade so richtig ordentlich für dich festhalten. Aber da gab es ein kleines technisches Stolpern in der Logik meines 'Timeline'-Agenten."* **Der Satz widerspricht sich in zwei Sätzen selbst.** Und die falsche Hälfte wurde verdichtet:

```
[KZG] Salienz 0.984: Nova hat notiert, dass der Gasvertrag gekündigt werden soll.
```

**Warum es der teurere von beiden ist.** Dieselbe Klasse wie `RESPONDER-ERFINDET-DATUM`: Eine falsche Bestätigung ist teurer als eine fehlende, weil sie geglaubt wird. **Hier ist sie zusätzlich dauerhaft** — die Verdichtung hat sie übernommen, und beim nächsten Abruf steht sie ohne den widersprechenden Nachsatz da.

**Geschlossen, wenn.** Eine Antwort, deren Agentenergebnis `abgelehnt` lautet, enthält keine Bestätigung der Handlung — und was ins Gedächtnis geht, trägt den Ausgang.

## Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### Chat 133 — aus der Fundliste klassifiziert, Block 30.–27.07. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Siebzehn Defekte, der aelteste Bestand der Liste. **Sechs von ihnen sind derselbe Bauplan:** ein Vorgabewert an einer Stelle, an der ein Ausfall gehoert — beim Queue-Push, beim Dispatch, am Spalten-Default des Rades, bei zwei Kanon-Feldern, in der fehlenden Klemme und beim Suchdienst, dessen Ausfall wie ein leeres Ergebnis aussieht.

#### ENTITAETEN-OHNE-EMBEDDING 🔧 offen — Symptom am 16.08.2026 nicht mehr auffindbar
**Kategorie:** GED

**Zustand:** offen, **zur Haelfte erledigt** — gegen HEAD `b8e9543` und den Bestand nachgemessen am 25.08.2026. **Das Embedding ist gebaut:** `create_new_entity` erzeugt es immer, das Feature-Flag ist entkernt; im Bestand **0 von 817** Entitaeten ohne Embedding. **Die Zusammenfassung ist es nicht:** `zusammenfassung` ist zwar Parameter, aber **802 von 817** Entitaeten tragen keine. Der Eintrag nennt beide Felder; er ist nach der Regel, dass ein Eintrag mit mehreren Stellen erst geschlossen ist, wenn jede steht, deshalb offen.

**Nachgemessen am 16.08.2026: 0 von 704 Entitaeten ohne Embedding.** Das Symptom ist weg. **Ungeprueft bleibt das Warum** — ob der Erzeuger nachgezogen wurde oder ein Nachlauf gefuellt hat; ohne diese Antwort ist nicht entscheidbar, ob neue Entitaeten weiterhin leer entstehen und nur nachtraeglich gefuellt werden. Der Eintrag bleibt bis dahin offen.

**Befund (2026-07-29).** Entitäten entstehen ohne Zusammenfassung und ohne Embedding. Einziger aktiver Erzeuger ist `agents/kzg/magnete.py`, `_entitaeten_aufloesen` → `EntityResolutionService.create_new_entity(postgres_url, user_id, name, typ)` — vier Argumente, `zusammenfassung` und `embedding` sind nicht darunter. Gemessen 28.07.2026: **88 von 89** aktiven Entitäten haben ein leeres `zusammenfassung`-Feld; nur die eine `user`-Entität trägt eines (die aus `api/chat.py` stammt, wo beide Felder gesetzt werden). Die Spalten existieren beide in `entitaeten`. Wirkung heute: Jede Suche über die Zusammenfassung ist ohne Substrat — das war Tür 2 des GV-Entity-Hop-Befunds — und eine Embedding-Suche über Entitäten ist gar nicht möglich. Wirkung morgen: M2.5b und die Entity-Resolution selbst hängen an denselben zwei Feldern. Offen ist nicht der Fix, sondern die Frage, **woher** die Zusammenfassung einer im KZG-Pfad nebenbei aufgelösten Entität kommen soll — der Magnet-Pfad ist nicht-interaktiv und hat nur den Namen.

**Was fertig waere.** Eine Entitaet entsteht mit Zusammenfassung und Embedding, oder ihr Fehlen ist gemeldet.

**Prioritaet:** hoch.

#### PROMOTION-LOG-ALTE-SKALA 🔧 offen
**Kategorie:** GED

**Zustand:** offen — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. Die Logzeile nennt weiterhin `(0-10)`. **Die Zeilenangabe des Befundes ist veraltet:** Sie steht heute bei `:362`, nicht bei `:256`. Der Befund selbst ist unveraendert.

**Befund (2026-07-29).** Die Gewinner-Log-Zeile der Synapsen-Promotion nennt die alte Salienz-Skala: `agents/synapsen_promotion/agent.py:256` schreibt `kzg_salienz={salienz:.3f} (0-10)`. Derselbe Commit, der die Skala auf 0–1 umgestellt hat, korrigierte den Modul-Docstring (Zeile 16) und den Kommentar an der Lesestelle (Zeile 235) — die Log-Zeile blieb stehen. Wer das Log liest, ordnet einen Wert von 0.95 auf einer Skala bis 10 ein und hält ihn für niedrig.

**Was fertig waere.** Die Logzeile nennt die geltende Skala.

**Prioritaet:** niedrig.

#### GRAVITATION-KLEMME-FEHLT 🔧 offen
**Kategorie:** GED

**Befund (2026-07-29).** Die Klemme in `ei/gravitation.py` fehlt weiterhin: Zeile 336 übernimmt `salienz` ungeklemmt als `gewicht` in den Lesepfad. Der Backlog führt sie als Sofortfix (`KZG-SALIENZ-KONSUMENTEN-DISSENS`, Entscheidung aus Chat 109) und hält im selben Eintrag fest, dass sie nach dem Neubau zwar rechnerisch wirkungslos, aber **als Zusicherung des Lesers an sich selbst** richtig bleibt. Seit dem Salienz-Neubau vom 28.07. kann kein Wert über 1.0 mehr entstehen; die Zusicherung ist damit nicht erfüllt, sondern nur unbeobachtbar geworden.

**Was fertig waere.** Der uebernommene Wert ist auf seine Spanne geklemmt, oder ein Wert ausserhalb wird gemeldet.

**Prioritaet:** hoch.

### Chat 133 — aus der Fundliste klassifiziert, Block 31.07. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Antwortpfad](novaberg-bugs-antwortpfad.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Acht Defekte. **Vier davon sind Prompt-Bloecke, die etwas ueber den Nutzer behaupten, was Novas Zustand ist** — dieselbe Verwechslung an vier Stellen, jede fuer sich unauffaellig.

#### SALIENZ-ZEITFELD-FAELLT-AM-LIMIT-ZUERST 🔧 offen
**Kategorie:** GED

**Befund (2026-07-31).** **`zeitausdruck_roh` ist das letzte Feld des Salienz-Antwortschemas**, und die Salienz läuft mit `max_output_tokens: 1024`. Läuft eine Antwort ans Limit, fehlt dieses Feld als erstes — und ein fehlendes Feld ist von „kein Zeitbezug erkannt" nicht zu unterscheiden. Ob es im Betrieb zuschlägt, ist **nicht gemessen**; die Beobachtung stammt aus dem Lesen des Schemas, nicht aus einem Ausfall. Dieselbe Klasse wie `lesson_l_default-wie-fehlschlag`: Der Ausfall sieht aus wie ein Ergebnis. Wer es prüft, zählt abgeschnittene Antworten im Salienz-Pfad; wer es entschärfen will, zieht das Feld im Schema nach vorn.

**Was fertig waere.** Ein abgeschnittenes Schema ist von einem vollstaendigen mit leerem Feld unterscheidbar.

**Prioritaet:** hoch.

### Chat 133 — aus der Fundliste klassifiziert, Block 05.–02.08. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Acht Defekte aus dem zweiten Fundlisten-Block. **Der Befund steht im Wortlaut, in dem er notiert wurde** — er trägt Beleg und Datum und wird nicht nacherzählt; ergänzt sind Kennung, Priorität und die Zeile, an der man erkennt, wann der Eintrag geschlossen ist.

Drei von ihnen sind stille Vorgabewerte an einer Stelle, an der ein Ausfall gehört: eine feste Salienz, eine Priorität, die auf null fällt, und ein Pflichtfeld, das leer durchgeht.

#### SALIENZ-JSON-BRICHT-AN-LATEX 🔧 offen
**Kategorie:** GED

**Zustand:** offen, **unbelegt** — nachgesehen am 25.08.2026. Der juengste JSON-Fehler im Salienz-Pfad stammt vom **12.08.2026**; in den 13 Tagen danach steht keiner mehr im Protokoll. Von vier Fehlerzeilen des Knotens in 14 Tagen nennt genau eine das Parsen. **Ob die Ursache weg ist oder nur nicht getroffen wurde, ist nicht entschieden:** Der Defekt braucht Formeln in der Modellantwort, und das haengt am Gegenstand des Gespraechs, nicht am Code.

**Befund (2026-08-02).** **Die Salienz-Bewertung scheitert an LaTeX in der Modellantwort.** Belegt beim Abnahme-Turn zu P9 (19:15:01 UTC): `ChatWorker 'chat': JSON-Parsing fehlgeschlagen (caller=salienz/segment, fehler=Invalid \escape)`. Das Modell antwortet mit Formeln — `$T_H$`, `\propto`, `\n\n` im Fließtext —, und `parse_json_strict` bricht am Backslash ab. **Das erklärt vermutlich die 6 `salienz`-Fehler**, die im Pipeline-Log der letzten sieben Tage stehen (von insgesamt 11): Der Korpus ist Physik, und Physik schreibt sich in LaTeX. Der Turn selbst lief durch, nur seine Bewertung fiel aus — der Eintrag bekommt damit keine Salienz und wird nicht promotet.

**Was fertig waere.** Der Parser haelt Backslash-Sequenzen aus, oder die Anweisung verbietet LaTeX im Fliesstext — und ein Parse-Fehler faellt nicht als leeres Ergebnis durch.

**Prioritaet:** mittel.

---

### Agent-System (Epic 11, Chat 22–29)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Wissen](novaberg-bugs-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### BUG3 — "Bruder" als Verwandtschaft statt Anrede-Slang ⬜
**Kategorie:** GED
**Entdeckt:** Chat 19
**Prio:** Niedrig — kosmetisch, nur bei jugendlichem Stil.

---

### Datenqualität

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### CLUSTER-THEMEN-DEDUP — Semantisch redundante Themen-Strings in Cluster-Promotion
**Kategorie:** GED

**Zustand:** offen, **ueberholt** — nachgesehen am 25.08.2026. Der genannte Schreiber `_lzg_eintrag_schreiben` existiert nicht mehr; die Cluster-Promotion ist von der Synapsen-Promotion abgeloest. Im heutigen Bestand stehen keine wortgleichen Dubletten der beschriebenen Art mehr, wohl aber semantisch nahe Themen ueber verschiedene Knoten hinweg — das ist ein anderer Gegenstand und braucht ein Aehnlichkeitsmass, keine Zeichenkette.

**Status:** ⬜ Offen
**Entdeckt:** Chat 86 (Cluster-Qualitäts-Diagnose im LZG)

**Symptom:** Cluster-promovierte LZG-Einträge enthalten Themen-Listen mit semantisch redundanten Strings. Beispiele aus dem aktuellen LZG:
- ID 67: `{"Annas Geburtstag", "Geburtstag", "Geburtstag von Anna", "Geburtstag von Rosa", ...}` — vier Strings, die im Kern dasselbe Konzept ("Geburtstag") fassen.
- ID 66: `{Datenbanken, PostgreSQL, "PostgreSQL Architektur", Datenbank-Performance, Software-Performance, ...}` — drei Granularitätsstufen desselben Konzepts plus ein Phrasen-Paar mit gemeinsamem Wortstamm.

**Ursache:** Die Cluster-Aggregation in `_lzg_eintrag_schreiben` führt eine Mengen-Vereinigung über alle Cluster-Mitglieds-Themen durch (`sorted(set().union(*[m.themen]))`). Diese Vereinigung dedupliziert nur **String-identische** Themen. Semantische Duplikate ("Geburtstag" vs. "Annas Geburtstag") werden als zwei verschiedene Set-Einträge behandelt.

**Auswirkung:** Mittel. Themen-Listen wachsen aufgebläht, was die Themen-basierte Retrieval-Logik (Themen-Tabelle, Themen-Salienz-Erweiterung) verzerrt. Aufgeblähte Themen-Listen erzeugen Pseudo-Vielfalt — derselbe Inhalt zählt mehrfach als "verschiedenes Thema". Folgen treten bei der Retrieval-Erweiterung im Enricher auf (siehe `novaberg-memory.md` §11).

**Lösung:** Drei Ansätze, von einfach zu robust:
1. **Lexikalische Normalisierung** vor der Mengen-Vereinigung (Lowercase, Lemma, Stopword-Entfernung). Fängt offensichtliche Duplikate, aber nicht "Annas Geburtstag" vs. "Geburtstag von Anna".
2. **Embedding-Cluster auf den Themen-Strings**: Themen-Embeddings rechnen, Cosine ≥ Schwellwert → derselbe Cluster, repräsentativster String gewinnt. Analog zur Cluster-Promotion selbst.
3. **LLM-Konsolidierungs-Call** in der Cluster-Destillation: Mini-Call reduziert die Themen-Liste auf den semantischen Kern. Höchste Recall-Garantie, höhere LLM-Kosten.

**Vorbedingung:** Keine.
**Prio:** Mittel.

**Status-Update Chat 86:** Beide Bugs werden voraussichtlich durch den Synapsen-Umbau (siehe `novaberg-memory-synapsen_k.md`) strukturell obsolet, weil keine Themen-Aggregation mehr stattfindet. Themen bleiben pro Knoten eingefroren, geteilte Themen werden zur Kanten-Charakterisierung. Bis zur Umsetzung des Umbaus bleibt der Bug-Eintrag bestehen — aktive Mitigation wird zurückgestellt.

---

#### CLUSTER-META-CONTAMINATION — Pipeline-Meta-Begriffe als Themen-Tags
**Kategorie:** GED

**Zustand:** offen — gegen HEAD `cc5aaae` und den Bestand gehalten am 25.08.2026. **Der Beleg ist verfallen, der Befund gewachsen:** Die Knoten `id 50` und `id 67` gibt es nicht mehr; ueber `lzg_knoten` gezaehlt tragen aber **113 von 3047** einen der genannten Meta-Begriffe im Themenfeld (3,7 %). Von den zwei Loesungsansaetzen ist keiner gebaut — `SALIENZ_THEMEN_STOPWORDS` kommt in `config.py` nicht vor.
**Status:** ⬜ Offen
**Entdeckt:** Chat 86 (Cluster-Qualitäts-Diagnose im LZG)

**Symptom:** Cluster-promovierte LZG-Einträge enthalten Themen-Strings, die nicht Inhalts-Begriffe sind, sondern Meta-Beobachtungen über die Interaktion oder Pipeline:
- ID 67 (beobachter=assistant): `"Ergänzung zur Notiz"`, `"Gedächtnis des Gegenübers"`
- ID 50 (beobachter=user): `Charakterisierung`, `"Charakterisierung des Gegenübers"`, `"Wahrnehmung der KI"`, `"Wahrnehmung von Fokus und Zielorientierung"`

**Ursache:** Der Themen-Extraktor (Salienz Dim 1) klassifiziert nicht nur Inhalts-Entitäten, sondern auch sprachliche Reflexionen über die Interaktion als Themen. Besonders sichtbar in Assistant-Cluster-Einträgen (Nova-seitige Beobachtungen enthalten häufiger Meta-Reflexion), aber auch user-seitig nachweisbar (ID 50).

**Auswirkung:** Mittel. Meta-Themen ziehen über die Retrieval-Erweiterung im Enricher unverwandte LZG-Einträge in die Akte — "Wahrnehmung" als Tag matched auf jeden Eintrag mit Wahrnehmungs-Reflexion, unabhängig vom Inhalt. Verwässert die Themen-Trennschärfe und untergräbt die Salienz-Träger-Architektur (`novaberg-memory.md` §12).

**Lösung:** Zwei Ansätze, kombinierbar:
1. **Prompt-Schärfung** in `prompts/default/salienz.aufgabe.txt`: explizite Negativ-Beispiele ("nicht: Wahrnehmung, Gedächtnis, Charakterisierung — diese sind Pipeline-Begriffe, keine Inhalts-Themen").
2. **Post-Filter-Stopword-Liste** (`SALIENZ_THEMEN_STOPWORDS` in `config.py`) mit Pipeline-Begriffen, angewendet im KZG-Schreibpfad nach der LLM-Extraktion. Robuste Notbremse für den Fall, dass Prompt-Schärfung nicht reicht.

**Vorbedingung:** Keine.
**Prio:** Mittel.

**Status-Update Chat 86:** Beide Bugs werden voraussichtlich durch den Synapsen-Umbau (siehe `novaberg-memory-synapsen_k.md`) strukturell obsolet, weil keine Themen-Aggregation mehr stattfindet. Themen bleiben pro Knoten eingefroren, geteilte Themen werden zur Kanten-Charakterisierung. Bis zur Umsetzung des Umbaus bleibt der Bug-Eintrag bestehen — aktive Mitigation wird zurückgestellt.

---

#### PROMO-FAKT-LEER — Fakt-klassifizierte Einträge ohne Fakten fallen aus dem LZG-Schreib-Pfad
**Kategorie:** GED

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: ein Promotionsergebnis ohne Faktinhalt. Die Bedingung entsteht im Lauf, nicht in einer Zeile.
**Status:** ⬜ Offen
**Entdeckt:** Chat 85 (durch EVA-Audit-Logging nach Pixie-EVA-Härtung sichtbar geworden)

**Symptom:** KZG-Einträge werden in Call 1 als `klassifikation="fakt"` klassifiziert. Call 2 extrahiert anschließend 0 Fakten-Tripel (weil der Inhalt keine extrahierbaren Tripel enthält — typisch für Beobachtungen über Interaktionsstil, Selbstdarstellung, abstrakte Eigenschaften). Da der LZG-Schreib-Pfad an die Bedingung `klassifikation in ("erinnerung", "gemischt")` gebunden ist, wird weder ein LZG-Eintrag noch ein Knowledge-Graph-Eintrag geschrieben. Der KZG-Eintrag geht verloren.

**Beispiele (Chat 85, 11.05.26, Audit-Logs):**

- `kzg:meister:nova:1778440554756` — themen=`Selbstbewusstsein, Intelligenz`, salienz=0.7, klassifikation=fakt, 0 Fakten
- `kzg:meister:nova:1778440555618` — themen=`Schwertkampf, Strategie, Angriff und Verteidigung, Taktik des Lockens`, salienz=0.8, klassifikation=fakt, 0 Fakten
- `kzg:meister:nova:1778440588602` — themen=`Selbstdarstellung, Spielerische Interaktion`, salienz=0.7, klassifikation=fakt, 0 Fakten

**Ursache:** Der Klassifikator stuft Inhalte mit allgemeinen Beobachtungen als `fakt` ein, obwohl sie keine extrahierbaren Tripel enthalten. Der Promotion-Code hat keinen Auffang-Pfad für diesen Fall: `fakt` schaltet auf Tripel-Extraktion, und wenn diese leer ist, passiert gar nichts mehr.

**Auswirkung:** Mittel. Substanzielle KZG-Einträge mit Salienz 0.7-0.8 gehen verloren, ohne dass sie als Erinnerung im LZG landen. Vor der EVA-Härtung war der Verlust komplett unsichtbar; jetzt wird er als Audit-Eintrag `status='erledigt'` mit `lzg_eintrag_geschrieben=false` protokolliert, aber der Verlust selbst bleibt.

**Lösungsoptionen (eine oder mehrere):**

- (a) Klassifikator: bei Inhalten ohne konkrete Tripel auf `erinnerung` statt `fakt` fallen (Anpassung des Klassifikator-Prompts, sodass abstrakte Beobachtungen explizit als Erinnerung erkannt werden)
- (b) Promotion-Pfad: bei `klassifikation="fakt"` und 0 extrahierten Fakten automatisch auf `gemischt` umschalten, damit der Erinnerungs-Pfad greift
- (c) Eigener Auffang-Pfad: Audit-Eintrag `status='fehler'` mit Begründung "Klassifikation 'fakt' ohne extrahierbare Tripel", statt silent Erfolgs-Meldung

**Empfehlung:** (b) als pragmatischer Fix, (a) als nachhaltige Lösung. Reihenfolge: erst (c) für Sichtbarkeit, dann (a) oder (b) für Datenrettung.

**Vorbedingung:** Keine.
**Prio:** Mittel — kein Datenverlust ohne Audit-Trail mehr (durch EVA-Härtung), aber Datenverlust persistiert bis Fix.

---

### Chat 78 — TimelineAgent-Audit + Thinker-Findings

#### PFAD2-EMO-MIX — Pfad-2-KZG-Eintrag mischt User- und Nova-Emotion ⚠️
**Kategorie:** GED

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: Vermischung zweier Emotionsquellen im zweiten Pfad. Braucht einen Turn mit beiden.
**Entdeckt:** Chat 78 Audit (KZG/LZG-Befund)

**Symptom:** Im CharacterGraph schreibt der KZG-Pfad einen `beobachter=assistant`-Eintrag, aber die Emotion-Felder sind inkonsistent:

- `salienz_obj.emotion` kommt aus LLM-Klassifikation des `user_prompt` → User-Emotion
- `arousal` kommt aus `perzeption_assistant` → Nova-Emotion
- `emotions_vektor` bleibt leer, weil `_ei_calc_character` nur `nova_emotions_vektor` setzt, der Dispatcher aber `state.emotions_vektor` liest

**Konkrete Stellen:**

- [graph/nodes/salience.py:147-153](graph/nodes/salience.py#L147-L153) — Salience-Node analysiert weiterhin `state.user_prompt`
- [graph/nodes/ei_calc.py:124-198](graph/nodes/ei_calc.py#L124-L198) — `_ei_calc_character` setzt nur `nova_emotions_vektor`
- [graph/nodes/dispatcher.py:48](graph/nodes/dispatcher.py#L48) und [graph/nodes/dispatcher.py:238](graph/nodes/dispatcher.py#L238) — liest `state.emotions_vektor` (User-Vektor), nicht den Nova-Vektor
- [agents/kzg/dispatch.py:67-71](agents/kzg/dispatch.py#L67-L71) — übernimmt User-`emotions_vektor` ins Nova-KZG

**Konsequenz:** KZG-Einträge mit `beobachter=assistant` haben keinen kohärenten Emotionsstand. Konzeptuelle Folge: spätere Analysen über Nova-Emotionen (Cluster, Trends, Selbst-Reflexion) arbeiten auf inkonsistenten Daten.

**Soll-Verhalten:** Im Pfad-2-KZG-Schreibvorgang wird Novas eigene Emotion gespeichert. Salience-Node berücksichtigt `ei_calc_rolle`, Dispatcher nutzt `nova_emotions_vektor` wenn `beobachter=assistant`.

**Verwandt:** Dual-Emotion-Architektur (Chat 60+).

**Prio:** Mittel — schreibt heute schon korrupte Daten in jeden Pfad-2-Eintrag, aber Auswertungen darauf existieren noch nicht. Vor erster Nova-Selbst-Reflexion fixen.

---

*Aktualisiert Chat 78: THINK-MEM-CONFLICT angelegt mit Audit-Befund. Bug sitzt im Thinker-Information-Gap, nicht im TimelineAgent-Subgraph. Lösung THINK-TRANSITION-INFO im Backlog §7 designed. Vier weitere Bugs aus KZG/LZG-Audit ergänzt: CHAR-LZG-LEAK (LZG-Spiegelung von CHAR-HASH-FILTER), PFAD2-EMO-MIX (User-/Nova-Emotion gemischt), MIGRATION-PIX-PAIR (Pixie-Schreibpfade in altem Schema), MIGRATION-AGENTGRAPH-PAIR (AgentGraph-Calls mit beiden IDs auf "nova"). Bereinigung der Bestände: Backlog-Eintrag KZG-CLEANUP.*

---

*Aktualisiert Chat 79: Vier Bugs behoben (THINK-MEM-CONFLICT, CHAR-LZG-LEAK, MIGRATION-PIX-PAIR, MIGRATION-AGENTGRAPH-PAIR). PIX-CLEAN: 7 alte Task-Dateien + Runner geloescht, __init__.py bereinigt. KZG-CLEANUP: 24 Alt-Eintraege (17× kzg:nova:meister:* + 7× kzg:nova:nova:*) geloescht. PIXIE-AGENT-MISSING praezisiert.*

---

### Chat 106 — Audit „Lügende Logs" (9 Funde, hier die Bug-würdigen)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Hintergrund](novaberg-bugs-hintergrund.md), [Antwortpfad](novaberg-bugs-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Leitfrage des Audits: *Wo loggt ein Node eine Wirkung, die er nicht beobachten kann?*
Zwei wiederkehrende Klassen: (1) `broadcast()`-Aufrufer, die Rückkehr als Zustellung
deuten; (2) Batch-Zähler, die exception-freie Durchläufe zählen, während die
Arbeitsfunktion per stillem `return` verwerfen darf. Beide haben dieselbe Form: Der
Aufrufer KANN nicht wissen, ob es geklappt hat. Positivbefund: graph/ ist nach dem
Kanal-Fix sauber, die CRUD-Agenten verifizieren sich selbst, die model_services-Schicht
propagiert Fehler vorbildlich — das Muster sitzt in den Zustell- und Batch-Pfaden.

#### BATCH-ZAEHLER-ZAEHLEN-AUFRUFE — „N promotet" zählt Verworfene mit ⚠️
**Kategorie:** GED

**Zustand:** offen, **Beleg zur Haelfte gegenstandslos** — gegen HEAD `cc5aaae` gehalten am 25.08.2026. `agents/promotion/agent.py` (der als *dormant* genannte Pfad) **existiert nicht mehr**. Im aktiven Pfad gilt der Befund unveraendert, an neuer Stelle: `agents/synapsen_promotion/agent.py:234` zaehlt `promotet += 1` nach jedem exceptionfreien Aufruf, waehrend die Verwurfsfaelle (`:300` TTL abgelaufen, `:316` Inhalt leer) per normalem `return` zurueckkehren.
**Entdeckt:** Chat 106, Audit „Lügende Logs". **Prio mittel.**

**Symptom:** Die Summenzeilen „{promotet} Eintraege promotet, {fehler} Fehler" zählen
jeden exception-freien `_eintrag_verarbeiten`-Aufruf als Erfolg. Die Arbeitsfunktion
kehrt aber bei Vorbedingungs-Verstößen per normalem `return` zurück, ohne LZG-Write
(fehlender kzg_key, KZG-Key nicht mehr in Redis/TTL, leerer Inhalt, unbekannte
Klassifikation) — alle „verworfen"-Fälle landen in `promotet`. Die Zahl, auf die man beim
Debuggen schaut, lügt. Das per-Eintrag-`hintergrund_log` ist korrekt.

**Beleg:** `agents/promotion/agent.py:107-124` (dormant) und
`agents/synapsen_promotion/agent.py:138-152` (aktiver Pfad).

**Auswirkung:** Pipeline-Debugging über die Summenzeile führt in die Irre.

### Chat 110 (26.07.2026) — Impuls-Pfad, Gedächtnis-Duplikate und blinde Stellen

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Alle Einträge dieser Sektion stammen aus dem Sprint, der den Pixie-Impuls durch den CharacterGraph geführt hat (Roadmap Chat 110). Sie sind **nicht** durch ihn entstanden — er hat sie sichtbar gemacht, weil zum ersten Mal ein vollständiger Turn ohne Nutzer-Reiz durch alle Nodes lief.

**Gemeinsamer Reproduktionsweg.** Die Brücke macht jeden Fund nachvollziehbar, ohne Logs durchsuchen zu müssen:

```sql
-- Alle KZG-Einträge eines Turns:
SELECT kzg_id FROM verbindung WHERE turn_id = '<turn_id>' ORDER BY id;
-- Rohturn dazu:
SELECT inhalt FROM pipeline_log WHERE turn_id = '<turn_id>' AND art = 'turn_roh';
-- Welche Nodes den Turn protokolliert haben:
SELECT art, quelle, count(*) FROM pipeline_log WHERE turn_id = '<turn_id>' GROUP BY art, quelle;
```

```
# Inhalt und Beobachter eines KZG-Eintrags:
redis-cli HGET <kzg_id> inhalt ; redis-cli HGET <kzg_id> beobachter
```

**Belegturns (26.07.2026, Produktivsystem):**

| Turn | `turn_id` | Zeit UTC |
|---|---|---|
| Impuls (Pixie) | `57b6e84c14ed48a4a715c58aa733927a` | 18:47:57 |
| Impuls (Pixie) | `5eeee91e68f14f9b83983874e65af713` | 18:20:57 |
| Nutzer-Turn (Vergleich) | `00e6678b5f974bb8925deff7841efee9` | 18:5x |

---

#### IMPULS-DOPPELTE-SPUR — ein eigener Gedanke wird zweimal ins Gedächtnis geschrieben ⚠️
**Kategorie:** GED

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: ein Impuls schreibt ueber beide Graphen unter derselben `turn_id`. Zaehlbar, aber nur an einem Impuls-Turn, den es zu erzeugen gilt.
**Entdeckt:** Chat 110, nach der Umverdrahtung des Impuls-Pfads.

**Klasse:** Doppelte Persistenz durch zwei Graphen auf einem Turn. Severity **mittel** — kein Datenverlust, aber ein Gedanke wiegt doppelt.

**Symptom:** Ein Impuls durchläuft **beide** Graphen unter derselben `turn_id`: den AgentGraph (der Gedanke entsteht) und den CharacterGraph (er wird gedacht und gesprochen). Beide rufen `dispatch_kzg` auf, beide schreiben unter `beobachter='assistant'` — mit **verschiedenen** Kernsätzen, weil sie verschiedene Texte verdichten. Zusammen mit KZG-SEGMENT-DUPLIKAT ergeben sich sechs Einträge aus einem Impuls.

**Beleg:** Impuls-Turn `57b6e84c…` — sechs Einträge, **alle** `beobachter='assistant'`, **kein** `user`-Eintrag (richtig, es gab keinen Nutzer-Reiz). Zeitlich zwei Blöcke: `…16738` bis `…16773` (AgentGraph, 18:47) und `…17977` bis `…18006` (CharacterGraph, 18:49). Zum Vergleich der Nutzer-Turn: ein `user`-Eintrag aus dem HumanGraph, `assistant`-Einträge aus dem CharacterGraph.

**Offene Frage, nicht entschieden:** Soll ein Impuls beide Spuren tragen? Dafür spricht, dass Entstehen und Aussprechen verschiedene Ereignisse sind — der Mensch erinnert den Einfall anders als das Gesagte. Dagegen spricht, dass beide unter demselben Beobachter stehen und für jeden Leser ununterscheidbar sind. **Wenn beide bleiben, brauchen sie ein unterscheidendes Feld.**

**Status:** Offen, Entscheidung ausstehend. **Verwandt:** KZG-SEGMENT-DUPLIKAT.

---
