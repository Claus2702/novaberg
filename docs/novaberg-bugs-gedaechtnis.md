# Novaberg — Bugs: Gedächtnis — KZG, LZG, Promotion, Entitäten, Salienz, Verfall

**Inhalt:** die offenen Defekte dieses Gegenstands, ~~13~~ → ~~14~~ → ~~15~~ → ~~17~~ → ~~18~~ → ~~16~~ → ~~18~~ → ~~17~~ → 18 Eintraege (24.10.2026, später: `LZG-KANTEN-BESTAND-AUF-ALTEM-KNOTENGEWICHT` neu aus der Klassifizierung der Funde vom 24.10.2026; 24.10.2026, 13:43 UTC: `LZG-KANTEN-NACH-VERWENDUNG-UNVERAENDERT` behoben und im Betrieb gemessen, ins Archiv; 24.10.2026: `LZG-TREFFER-MELDET-REINFORCEMENT` und `MAGNET-ANKER-VERGANGENES-WIRD-KOMMEND` neu aus der Klassifizierung der Funde vom 23.10.2026; 23.10.2026, abends: `LZG-PROMOTION-TREFFER-VERSTAERKT` und `KZG-EINTRAG-BLEIBT-NACH-PROMOTION` behoben und im Betrieb gemessen, ins Archiv; 23.10.2026: `LZG-PROMOTION-TREFFER-VERSTAERKT` neu nach einer Entscheidung; 22.10.2026: `LZG-HALBREAKTIVIERUNG-HAELT-EINEN-TAG` und `LZG-KANTEN-NACH-VERWENDUNG-UNVERAENDERT` neu, am Code geprüft; 21.10.2026: `MAGNET-RUECKFALL-BINDET-AEHNLICHEN-NAMEN` neu nach einer Entscheidung; 20.10.2026: `AUFLOESUNG-AUSFALL-WIRD-NEUE-ENTITAET` neu aus der Fundliste), je mit `**Kategorie:** GED`.
**Wegweiser:** [`novaberg-bugs.md`](novaberg-bugs.md) — Kopf, Form eines Eintrags, Rangfolge, Verlauf. **Findemittel ueber alle Teile:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Archiv:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Register** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

---

## 24.10.2026 — aus der Klassifizierung der Funde vom 24.10.2026

Eine Kennung aus den Funden vom 24.10.2026 zu den Kanten des Langzeitgedächtnisses (Fundliste, *Umgezogen — 24.10.2026, aus der Klassifizierung der Funde vom 24.10.2026*), am Code gelesen gegen HEAD `2702d94`. Die Summen je Lauf der Verstärkung stehen als Backlog `VERSTAERKUNG-KANTEN-NUR-ALS-SUMME` in [`novaberg-backlog-gedaechtnis.md`](novaberg-backlog-gedaechtnis.md); die übrigen Bugs derselben Klassifizierung stehen in [`novaberg-bugs-charakter.md`](novaberg-bugs-charakter.md) und [`novaberg-bugs-wissen.md`](novaberg-bugs-wissen.md).

### `LZG-KANTEN-BESTAND-AUF-ALTEM-KNOTENGEWICHT` — ein Viertel der Kanten des Langzeitgedächtnisses steht nicht auf der Stärke, die Trigger 2 aus den heutigen Knotengewichten rechnet

**Kategorie:** GED

**Rang:** **mittel**, wartet auf eine Absicht — still, und es betrifft den Bestand: ein Viertel der Kanten. Begrenzt, weil die Stärke im Lesepfad nur die Nachbarn je Schale auswählt und jede Verstärkung die Kanten ihres Knotens nachzieht. Vergeben am 24.10.2026 gegen HEAD `2702d94`.

**Zustand:** offen — gemessen am 24.10.2026 am Bestand, nur lesend; am Code gelesen gegen `2702d94`. Die Ursache ist lesend eingegrenzt, am Bestand nicht geprüft; nichts ist nachgerechnet.

**Befund** `[gemessen 24.10.2026]`, am Bestand, nur lesend — je Kante dieselbe Rechnung wie Trigger 2, ohne Schreiben (`labor/2026-10-24_kanten_nulllinie.{py,out}`; [`novaberg-memory-synapsen_m.md`](novaberg-memory-synapsen_m.md), *Aus §7.9.2*): **155.998 von 639.734** Kanten weichen ab, die größte um 1,35. Davon hängen 16.266 an Knoten mit `verstaerkt_am` ab dem 04.09.2026 (3,7 % von deren 441.418 Kanten) und **139.732** an den übrigen (70,5 % von 198.316).

**Am Code** `[Code]`:

- **Die Rechnung des Werkzeugs ist die von Trigger 2.** Sie folgt `kanten_neuberechnen_mit_befund` (`server/memory/lzg_kanten.py`, Z. 372–451): `_schicht_tiefen_aus_frozen` (Z. 646–676), `kanten_staerke_berechnen` (Z. 219–264) und `kante_daempfen` (Z. 78–86), mit dem heutigen `gewicht_absolut` beider Knoten. Eine Neuberechnung nach einer Verstärkung zieht alle Kanten von und zu dem Knoten nach (Z. 418).
- **Die Rechnung hat sich nicht geändert** — anders, als die Fundzeile vermutete. Die vier Funktionen sind seit `140b7598` (24.05.2026) unverändert (`git log -L`), ihre Konstanten in `server/config.py` seit `2ac816c1` (15.05.2026); `LZG_EMBEDDING_SCHWELLWERT` änderte sich zuletzt mit `3adc682f` am 12.07.2026, vor dem Nullpunkt vom 27.07.2026. Ob eine Umgebungsvariable des Betriebs eine Konstante überschreibt, ist nicht nachgesehen.
- **Verschoben haben sich die Eingänge.** `lzg_knoten.gewicht_absolut` schreiben am Code drei Wege: `knoten_anlegen`, `knoten_verstaerken` (`server/memory/lzg_knoten.py`, Z. 549–590) und der Reset `knoten_gewichte_zuruecksetzen` (Z. 225), nur über `tools/reembed_all.py`, der dabei alle Kanten löscht. Themen, `timeline_id` und `entitaet_ids` eines Knotens schreibt nach der Anlage niemand (geprüft sind alle `UPDATE lzg_knoten` in `server/`, Tests ausgenommen).
- **`verstaerkt_am` steht bei der Anlage auf `NOW()`** (`db/init.sql`, Tabelle `lzg_knoten`): Die Gruppe *ab dem 04.09.2026* enthält jeden seither angelegten Knoten; *die übrigen* sind Kanten zwischen Knoten, die vor dem 04.09.2026 angelegt und seither nicht verstärkt wurden.
- **Wofür die Stärke gelesen wird:** Im Lesepfad wählt sie nur die Nachbarn je Schale aus (`lzg_knoten.py::_kanten_nachbarn`, Z. 878–939, `ORDER BY gewicht_absolut DESC LIMIT top_k`; gerufen in Z. 1061); die Rangfolge danach trägt `gewicht_decay` des Knotens.

**Spur zur Ursache, lesend eingegrenzt** — am Bestand *unbelegt*: Der Wartungslauf der Salienz am 24.08.2026 um 12:38 UTC schrieb `gewicht_roh` und `gewicht_absolut` von **2448** LZG-Knoten per `UPDATE` (`labor/2026-08-24_salienz_wartungslauf.py`, Z. 284–291; Chronik [`novaberg-roadmap-2026-08.md`](novaberg-roadmap-2026-08.md), Eintrag 24.08.2026, 12:45 UTC; Archiv `KZG-SALIENZ-GESAETTIGT`). Er änderte `verstaerkt_am` nicht und rechnete die Kanten nicht neu: Das Werkzeug ruft `lzg_kanten` nicht, und weder Chronik noch Archiv nennen Kanten. Kanten zwischen zwei solchen Knoten stehen damit seither auf den Gewichten von vor dem Lauf, bis einer der beiden durch einen Weg mit Trigger 2 ging — bis zum 23.10.2026 die Promotion, seit dem 24.10.2026 die Verwendung. Das passt zur Lage der Abweichung (3,7 % gegen 70,5 %); die 16.266 an verstärkten Knoten passen zum geschlossenen `LZG-KANTEN-NACH-VERWENDUNG-UNVERAENDERT`, denn vom 04.09. bis zum 24.10.2026 verstärkte die Verwendung ohne Trigger 2. Die größte Abweichung (1,35) ordnet das Werkzeug keiner Gruppe zu. **Prüfbar, nur lesend:** Eine abweichende Kante der übrigen hat zwei Endknoten mit `erstellt_am` vor dem 24.08.2026, 12:38 UTC, die beide zu den 2448 umgerechneten gehören; eine Kante mit einem danach angelegten Endknoten weicht nicht ab; mit den Gewichten aus der Sicherung vor dem Lauf (`backups/salienz-vor-wartungslauf-20260824T122815Z/`) gerechnet, verschwindet ihre Abweichung.

**Wirkung.** Bei einem Viertel der Kanten folgt die Auswahl der Nachbarn je Schale einer Stärke, die die heutige Rechnung nicht ergibt; welche Nachbarn dadurch fehlen oder hinzukommen, ist nicht gemessen.

**Geschlossen, wenn** die Kanten des Bestands auf der Stärke stehen, die Trigger 2 aus den heutigen Knotengewichten rechnet — gemessen mit derselben Rechnung wie die Nulllinie, 0 abweichend bis auf eine begründete Menge —, oder entschieden ist, den Bestand stehen zu lassen, und der Eintrag das mit Grund sagt.

**Offen:** die **Absicht**, wie mit dem Bestand verfahren wird — nachrechnen; erst die Ursache am Bestand lesend prüfen und dann mit Sicherung nachrechnen; oder stehen lassen. Das Material oben gehört zum zweiten Weg. Dazu, ob der Wartungslauf die Ursache ist (die Prüfung oben), wie groß die Abweichung je Gruppe ist, und ob eine Umgebungsvariable eine Konstante überschreibt.

**Zusammenhang:** `LZG-KANTEN-NACH-VERWENDUNG-UNVERAENDERT` (Archiv, [`novaberg-bugs-archiv-gedaechtnis.md`](novaberg-bugs-archiv-gedaechtnis.md)) deckt nur die Verstärkung über die Verwendung; [`novaberg-memory-synapsen_m.md`](novaberg-memory-synapsen_m.md), *Aus §7.9.2*: *„Der Bau rechnet den Bestand nicht nach“*; [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md) §7.9.2.

---

## 24.10.2026 — aus der Klassifizierung der Funde vom 23.10.2026

Zwei Kennungen aus den Funden vom 23.10.2026 (Fundliste, *Umgezogen — 24.10.2026*), am Code gelesen gegen HEAD `6b37234`, nicht gelaufen. Die übrigen fünf Bugs derselben Klassifizierung stehen in [`novaberg-bugs-antwortpfad.md`](novaberg-bugs-antwortpfad.md) und [`novaberg-bugs-wissen.md`](novaberg-bugs-wissen.md).

### `LZG-TREFFER-MELDET-REINFORCEMENT` — beim Treffer meldet `match_pruefen` weiter *„-> Reinforcement“*, obwohl kein Zweig danach verstärkt

**Kategorie:** GED

**Rang:** **niedrig** — laut und nur im Text: Der Zweig danach schreibt die richtige `aktion` (`dublette` oder `halbreaktivierung`) in `pipeline_log` und Audit; ein falsches Ergebnis entsteht nicht. Vergeben am 24.10.2026 gegen HEAD `6b37234`.

**Zustand:** offen — am Code gelesen am 24.10.2026 gegen `6b37234`; gefunden am 23.10.2026 bei der Messung der Promotion im Betrieb.

**Befund** `[Code]`: `server/memory/lzg_knoten.py::match_pruefen` (Z. 540–541) schreibt für jeden besten Kandidaten ab `LZG_KNOTEN_MATCH_SCHWELLE` (0,82, `server/config.py`) die Zeile `Match erkannt: … -> Reinforcement` ins Log, bevor feststeht, ob der Knoten aktiv ist. Ihr einziger Aufrufer, `server/agents/synapsen_promotion/agent.py` (Z. 525), verzweigt danach in die Halbreaktivierung (inaktiver Knoten) oder in die Dublette (aktiver Knoten, seit `782274c`: *„kein `knoten_verstaerken`“*); keiner der beiden Zweige verstärkt. Zwei Docstrings sind ebenso veraltet: der von `match_pruefen` (*„nur echte Identitaet verstaerkt“*) und der von `knoten_verstaerken` (*„Reinforcement-Pfad bei Match (K10)“*) — dessen einziger Aufrufer außerhalb der Tests ist heute die Verstärkung über die Verwendung (`server/memory/usage_reinforcement.py`, Z. 239).

**Wirkung.** Wer das Serverlog liest, sieht bei jeder Dublette und jeder Halbreaktivierung eine Verstärkung, die nicht stattfindet. Ob eine Auswertung die Zeile *„-> Reinforcement“* zählt, ist nicht geprüft.

**Geschlossen, wenn** die Logzeile von `match_pruefen` keine Verstärkung mehr ankündigt und die beiden Docstrings sagen, was der Code tut: Der Treffer verhindert eine Dublette, verstärkt wird nur über die Verwendung.

**Zusammenhang:** `LZG-PROMOTION-TREFFER-VERSTAERKT` (Archiv, [`novaberg-bugs-archiv-gedaechtnis.md`](novaberg-bugs-archiv-gedaechtnis.md)), dessen Bau diese Zeile stehen ließ; das Backlog `PIPELINE-LOG-MERGE-BLIND` ([`novaberg-backlog-gedaechtnis.md`](novaberg-backlog-gedaechtnis.md)) behandelt das Protokoll der Dublette in `pipeline_log`, nicht diese Zeile; [`novaberg-node-synapsen-promotion.md`](novaberg-node-synapsen-promotion.md).

---

### `MAGNET-ANKER-VERGANGENES-WIRD-KOMMEND` — der Erinnerungs-Anker eines berichteten vergangenen Monats liegt im kommenden Jahr

**Kategorie:** GED

**Rang:** **mittel** — still, und es schreibt: Die Anker-Zeile steht im falschen Jahr, die `timeline_id` von KZG-Eintrag und LZG-Knoten zeigt auf sie, und spätere Nennungen desselben Tages nehmen sie wieder. Begrenzt, weil die Zeit des Ankers am Code nur die Kantenbildung liest (`server/memory/lzg_knoten.py`, Z. 398–404 und 806–812, als `timeline_event_time` an `server/memory/lzg_kanten.py::timeline_tiefe`). Vergeben am 24.10.2026 gegen HEAD `6b37234`.

**Zustand:** offen — beobachtet am 23.10.2026 in Messturns im Betrieb (aus der Fundliste übernommen), am Code gelesen am 24.10.2026 gegen `6b37234`; am Code folgerichtig, nicht nachgerechnet. Wie oft es vorkommt, ist nicht gezählt.

**Befund** `[Code]`: `server/agents/kzg/magnete.py::_timeline_aufloesen` ruft `zeit_parsen_vektor(zeitausdruck_roh)` (Z. 321) ohne Zeitlage und mit dem Vorgabewert `zukunft_bevorzugt=True` (`server/utils/zeitparser.py`, Z. 2496). Daraus wird `PREFER_DATES_FROM = "future"`, es sei denn, der Ausdruck trägt eine Rückwärtsmarke (`befund.rueckwaerts`, `zeitparser.py`, Z. 2305–2310). *„im September“* trägt keine: Die Zeitlage steht im Verb, und das Verb gehört nicht zu `zeitausdruck_roh`; die Salienz liefert dem Magnet-Pfad nur diesen Ausdruck (`magnete.py`, Z. 89). Der Anker wird gespeichert (`TimelineRepository.insert`), und über die Idempotenz (`find_by_date`) nehmen spätere Nennungen desselben Tages ihn wieder. Der Ereignis-Dienst setzt das Jahr dagegen aus der Zeitlage, die das Modell nennt (`server/agents/timeline/ereignis.py::event_time_of` über `_year_by_tense`); der Magnet-Pfad hat kein solches Feld.

**Symptom** (Fundliste, 23.10.2026): Für einen berichteten Satz *im September* lag der Anker des Magnet-Pfads auf dem 01.09.2027, während das Ereignis desselben Turns richtig im September 2026 liegt.

**Wirkung.** Die Kantenbildung rechnet die zeitliche Nähe gegen ein Datum, das ein Jahr daneben liegt, und jede spätere Nennung desselben Tages bindet sich an dieselbe falsche Zeile. Als Termin liest den Anker kein Weg (ein Erinnerungs-Anker ist in keinem Leseweg ein Termin, `TIMELINE-LESEPFAD-INSTABIL`; hier nicht nachgelesen).

**Geschlossen, wenn** der Anker eines berichteten Satzes über einen vergangenen Monat in der Vergangenheit liegt und der eines angekündigten in der Zukunft — bezeugt mit beiden Richtungen. Wie die Zeitlage den Magnet-Pfad erreicht, entscheidet der Bau; ein Feld der Salienz wäre ein Feld einer Modellausgabe und braucht vor dem Commit eine Messung am Modell.

**Offen:** welche Leser die `timeline_id` im KZG-Hash außer der Promotion hat; nicht geprüft.

**Zusammenhang:** `EREIGNIS-KOMMENDES-WIRD-VERGANGEN` (Archiv, [`novaberg-bugs-archiv-wissen.md`](novaberg-bugs-archiv-wissen.md)) — der Spiegelfall im Ereignis-Dienst; `ZEIT-RUECKWAERTS-WIRD-ZUKUNFT` (Archiv, ebenda) — die Richtung für Ausdrücke **mit** Marke; `ZEIT-EXTRAKTION-UNSCHARF` ([`novaberg-bugs-wissen.md`](novaberg-bugs-wissen.md)) — die Extraktion von `zeitausdruck_roh`, ein anderer Gegenstand; `MAGNET-RUECKFALL-BINDET-AEHNLICHEN-NAMEN` (in dieser Datei) — derselbe Pfad; [`novaberg-convention-magneten.md`](novaberg-convention-magneten.md).

---

## 22.10.2026 — am Code geprüft: die Doku der Synapsen gegen den Code

Zwei Kennungen aus dem Abgleich von `novaberg-memory-synapsen_{k,t,b,e}.md` mit dem Code, am Code geprüft am 22.10.2026; beide am Code gelesen, nicht gelaufen. Das Soll steht in `novaberg-memory-synapsen_t.md` unverändert, mit einem Vermerk, der die Kennung nennt (§9.3, §7.9.2). → 24.10.2026: `LZG-KANTEN-NACH-VERWENDUNG-UNVERAENDERT` ist mit `570cdda` behoben, im Betrieb gemessen und steht im Archiv ([`novaberg-bugs-archiv-gedaechtnis.md`](novaberg-bugs-archiv-gedaechtnis.md)); hier steht noch `LZG-HALBREAKTIVIERUNG-HAELT-EINEN-TAG`.

### `LZG-HALBREAKTIVIERUNG-HAELT-EINEN-TAG` — der halbe Wert eines geweckten Knotens hält nur bis zum nächsten Tageslauf
**Kategorie:** GED

**Rang:** ~~**mittel**~~ → **niedrig** (23.10.2026, am Bestand gemessen: heute tritt der Fall nicht ein — von 4571 Knoten ist **keiner** inaktiv, das kleinste `gewicht_absolut` ist 3,248, und mit `LZG_KNOTEN_DECAY_RATE` 0,0015 fällt der schwächste Knoten erst nach ln(3,248/0,1)/0,0015 ≈ 2320 Tagen unter `LZG_KNOTEN_MIN_GEWICHT`; `pipeline_log` trägt keine Halbreaktivierung). Davor: still: Ein geweckter Knoten steht nach dem nächsten Verfallslauf fast wieder bei seinem vollen Anker und rückt im Lesepfad nach vorn, gegen die Absicht von §9.3; geschrieben wird dabei nur `gewicht_decay`, der Anker `gewicht_absolut` bleibt unberührt. Wie oft halbreaktiviert wird, ist nicht gemessen. Vergeben am 22.10.2026 gegen HEAD `7c16bf5`.

**Zustand:** offen — am Code gelesen am 22.10.2026 gegen `7c16bf5`.

**Befund** `[Code]`: `server/memory/lzg_knoten.py::reactivate_node` setzt `gewicht_decay = (gewicht_absolut + LZG_KNOTEN_MIN_GEWICHT) / 2` und dabei `verstaerkt_am = NOW()` (Z. 639–647 am `7c16bf5`). Der nächste Tageslauf `run_node_decay` (gerufen von `server/agents/synapsen_decay/agent.py`, Z. 394) rechnet für jeden aktiven Knoten `gewicht_decay = gewicht_absolut · e^(−LZG_KNOTEN_DECAY_RATE · Tage seit verstaerkt_am)` neu (Z. 733–737), mit `LZG_KNOTEN_DECAY_RATE` = 0,0015 (`server/config.py`). Der Halbwert geht in diese Rechnung nicht ein — der Lauf rechnet vom Anker. Das Soll steht in `novaberg-memory-synapsen_t.md` §9.3: Der Knoten *„braucht Zeit und weitere Anstöße, um wieder voll präsent zu werden“*; der Docstring von `reactivate_node` sagt dasselbe.

**Wirkung.** Im Beispiel von §9.3 (`gewicht_absolut` 4,0) springt `gewicht_decay` auf 2,05 und steht einen Tag später bei 4,0 · e^(−0,0015) ≈ 3,99, also bei 99,85 % des Ankers. Der Schutz vor *„falschen Reaktivierungs-Spitzen“* hält bis zum nächsten Lauf; danach sortiert der Lesepfad den geweckten Knoten so, als wäre er nie verfallen.

**Vorhergesagter Zeuge** (nicht gelaufen): Ein deaktivierter Knoten mit `gewicht_absolut` 4,0 wird halbreaktiviert, danach läuft `run_node_decay`; am HEAD steht `gewicht_decay` bei ≈ 4,0, nicht beim Halbwert 2,05 oder darunter. Zwilling: Ein nie deaktivierter Knoten mit demselben Anker und demselben `verstaerkt_am` verfällt nach der Formel.

**Geschlossen, wenn** ein halbreaktivierter Knoten nach dem nächsten Verfallslauf nicht über seinem Halbwert steht und erst weitere echte Aktivierungen ihn seinem Anker nähern — bezeugt mit dem Zeugen oben und seinem Zwilling. Ob der Lauf vom Halbwert weiterrechnet oder die Erholung anders gespeichert wird, entscheidet der Bau.

**Zusammenhang:** [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md) §9.3; *Halbreaktivierung* in [`novaberg-featureliste.md`](novaberg-featureliste.md).

---

## 20.10.2026 — aus der Klassifizierung der Funde vom 18. bis 20.10.2026

### `MAGNET-RUECKFALL-BINDET-AEHNLICHEN-NAMEN` — der Magnet-Pfad bindet einen ähnlichen Namen still an eine andere Entität
**Kategorie:** GED

**Rang:** **mittel** — still, und es schreibt: Erinnerungen und künftig Fakten hängen an der falschen Person; selten (7 Bindungen über den Rückfall vom 18.09. bis 21.10.2026). Vergeben am 21.10.2026 gegen HEAD `ba83730`.

**Zustand:** offen — **behoben im Tree** (21.10.2026): Der Magnet-Pfad fragt je Name `resolve_by_name`; ein ähnlicher Name ohne eigenen Treffer wird eine neue Entität, der gleiche Name bindet; Zeugen mit Zwilling, Gegenproben rot wie vorhergesagt. Geschlossen mit dem Commit und der Messung im Betrieb. Davor: offen — seit der Entscheidung vom 21.10.2026 ein Defekt (`novaberg-memory-fakten_e.md` A Nr. 35), nichts gebaut.

**Nachtrag 21.10.2026, aus der Fundliste:** *ICH* ohne Entität des Menschen wurde im Magnet-Pfad über `resolve_batch` eine Entität namens *ICH* (dort nur eine Warnung, dann die gewöhnliche Suche). Mit demselben Bau fällt *ICH* ohne Entität des Menschen für diesen Namen laut aus und legt nichts an (`resolve_by_name` wirft `LookupError`); in `resolve_batch` bleibt der Weg, ohne Aufrufer im Betrieb.

**Befund** `[Code]`: `server/agents/kzg/magnete.py` löst über `EntityResolutionService.resolve_batch` auf; findet die Namenssuche nichts, bindet der Rückfall auf Embeddings einen einzelnen Treffer, wenn der Name *plausibel* ist — gleicher Anfangsbuchstabe und höchstens drei Zeichen Längenunterschied (`memory/services/entity_resolution.py::_name_ist_plausibel`): *Lena* wird *Lea*. Fakten und Sachlage lösen seit dem 20. bzw. 17.10.2026 ohne diesen Rückfall auf.

**Geschlossen, wenn** der Magnet-Pfad nur über den Namen auflöst und ein Name ohne Treffer eine neue Entität wird, bezeugt mit einem ähnlichen Namen (Zwilling: der gleiche Name bindet).

---

### `AUFLOESUNG-AUSFALL-WIRD-NEUE-ENTITAET` — ein Ausfall der Suche in der Auflösung geht als *kein Treffer* weiter und legt eine neue Entität an
**Kategorie:** GED

**Rang:** **mittel** — still, und es schreibt: ein Duplikat der Entität, an das danach Magnete binden; selten, nur bei einem Ausfall der Datenbank oder des Embeddings. Vergeben am 20.10.2026 gegen HEAD `b52e919`.

**Zustand:** offen — **behoben, ~~im Tree, nicht committet~~ → committet** (21.10.2026): Die Suche wirft, der Magnet-Pfad fängt je Name und meldet; Zeugen mit Zwilling, Gegenprobe rot wie vorhergesagt. Geschlossen mit dem Commit und der Messung im Betrieb. Davor: offen — am Code gelesen am 20.10.2026 gegen HEAD `b52e919`, nicht gemessen.

**Befund** `[Code]`: `server/memory/services/entity_resolution.py::_search_by_name` fängt jeden Fehler der Datenbank, schreibt ihn ins Log und gibt `[]` zurück (Z. 274–278); `_search_by_embedding` tut dasselbe mit einer Warnung (Z. 352–354). `resolve_batch` liest `[]` als *kein Treffer* und geht über den Rückfall auf Embeddings bis zu *neue Entität* (Z. 161–187). Aufrufer sind `server/agents/kzg/magnete.py` (`resolve_batch`, danach `create_new_entity`) und das Plugin `fakten_manager`, das mit dem Bauteil F1 entfällt (`novaberg-memory-fakten_e.md` A, Nr. 28). Der Schreibweg des Fakten-Agenten löst seit dem 20.10.2026 über `resolve_by_name` auf und nimmt diesen Pfad nicht.

**Geschlossen, wenn** kein Ausfall einer Suche dieses Pfads als *kein Treffer* weitergeht: Er wird geworfen oder als Ausfall gemeldet, und es entsteht keine Entität.

---

## 04.09.2026 — die Verstärkung hängt am falschen Ereignis

Drei Kennungen aus einer Frage des Eigentuemers: *„EI-Calc ist lesend. Lesend verstaerkt nicht. Erzeugte Prompts reaktivieren und verstaerken. Kollidieren wir hier?"* Die Antwort ist ja — und die Ursache liegt tiefer als die Frage: **Nicht das Lesen verstaerkt, sondern die blosse Nachbarschaft im Schreibpfad.** Die verfeinerte Regel steht seit heute in `novaberg-memory-synapsen_k.md` §7.1a. → 23.10.2026: `KZG-EINTRAG-BLEIBT-NACH-PROMOTION` ist behoben, im Betrieb gemessen und im Archiv ([`novaberg-bugs-archiv-gedaechtnis.md`](novaberg-bugs-archiv-gedaechtnis.md)); hier steht noch `KZG-THEMA-VERSTAERKT-NACHBARN`.

### `KZG-THEMA-VERSTAERKT-NACHBARN` — ein geteiltes Thema genuegt
**Kategorie:** GED

**Rang:** **hoch** — still, verfälscht den Bestand. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt an beiden Wegen, `_thematisch_verstaerken` (`server/agents/kzg/speicher.py:152-264`) und der ältere in `server/memory/kzg.py:486-560`; ~~gebaut ist nur die LZG-Seite von §7.1a.~~ → Von der LZG-Seite von §7.1a ist nur der Weg der Verwendung gebaut (`server/memory/usage_reinforcement.py`, seit dem 04.09.2026); der Embedding-Treffer der Promotion verstärkt weiter (`server/agents/synapsen_promotion/agent.py`, Verstärkungspfad; → seit `782274c` nicht mehr, im Betrieb gemessen am 23.10.2026) — ~~offen, §7.1a gegen K10 (`novaberg-memory-synapsen_e.md` B; am Code geprüft am 22.10.2026)~~ → entschieden am 23.10.2026 für §7.1a: Ein Treffer der Promotion verstärkt nicht (`novaberg-memory-synapsen_e.md` A, E7); der Weg der Promotion ist damit ein eigener Defekt, `LZG-PROMOTION-TREFFER-VERSTAERKT`.

**Zustand:** offen — am Bestand gemessen am 04.09.2026.

**Nachtrag 23.10.2026, nach einer Entscheidung:** Die Entscheidung gilt der LZG-Seite von §7.1a, nicht der thematischen Verstärkung im KZG; dieser Eintrag bleibt, wie er ist. Sie berührt ihn an der Schleife: Ist `LZG-PROMOTION-TREFFER-VERSTAERKT` behoben, liefert ein Eintrag, den die thematische Verstärkung am Leben hält, der Promotion weiter Futter, aber keine Verstärkung im Langzeitgedächtnis mehr. Die Schleife mit `KZG-EINTRAG-BLEIBT-NACH-PROMOTION` ist dann auf der LZG-Seite offen; im KZG wirkt sie weiter (Salienz, `haeufigkeit`, TTL).

**→ 23.10.2026: Die Seite der Promotion ist im Code geschlossen** (Code-Trees `2d18b83` und `5342a6a`, committet als `d11de95` und `782274c`; ~~MESSUNG im Betrieb steht aus~~ → im Betrieb gemessen am 23.10.2026, beide Kennungen im Archiv): Ein Treffer der Promotion verstärkt nicht, und ein Eintrag, der als neuer Knoten angelegt wird, verlässt das KZG mit der Promotion — er wird nicht weiter aufgefrischt und trifft seinen Knoten nicht erneut. Ein Eintrag, der nach einem Treffer stehen bleibt (Dublette oder Halbreaktivierung), lebt bis zu seiner TTL weiter; die thematische Verstärkung kann ihn weiter auffrischen, und geht er erneut in die Promotion, trifft er denselben Knoten — ohne Verstärkung im Langzeitgedächtnis. Die Schleife ist damit auf der LZG-Seite offen; im KZG wirkt sie weiter (Salienz, `haeufigkeit`, TTL). **Dieser Eintrag bleibt offen:** Bis zur Promotion verstärkt die thematische Verstärkung im KZG weiter Nachbarn statt Verwendetes und bestimmt damit, was in die Promotion geht. Neu ist ein Fenster zwischen beiden: Löscht die Promotion nach einer Neuanlage einen Schlüssel zwischen `hget` und `hset` der Verstärkung, legt `hset` einen Rumpf-Hash ohne `inhalt` an (Fundliste, 23.10.2026).

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

**Rang:** **mittel** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `server/agents/kzg/magnete.py:171` hängt ohne Prüfung an, Schreiber und Leser deduplizieren nicht.

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. keine Deduplizierung auf dem Schreibweg; die Zahl im Bestand braucht einen Messlauf. → 22.10.2026: Der neue Leseweg `memory/lzg_knoten.py::knoten_zu_entitaeten` (Code-Tree `0d5f633`, committet; der Erinnerungsanker) führt `geteilte_entitaet_ids` als Menge, jede Kennung einmal, auch wenn der Knoten sie doppelt trägt (Zeuge `test_shared_ids_carry_each_id_once`). Schreibweg, Bestand und die übrigen Leser sind unverändert.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **`entitaet_ids` trägt Dubletten.** In 3 von 84 belegten KZG-Arrays steht dieselbe Entitäts-ID mehrfach, etwa `193,269,871,196,870,193,194`. Die Achse ist nach `novaberg-convention-magneten.md` §2.1 **referenziell und n:m** — eine Erinnerung betrifft eine Entität oder nicht; ein zweites Vorkommen bedeutet nichts. **Die Enthaltenseins-Suche bleibt richtig** (`entitaet_ids @> ARRAY[x]` trifft weiterhin), aber jede Zählung über die Achse ist verzerrt, und §4 nennt für die Cluster-Aggregation ausdrücklich die *Vereinigung* der `entitaet_ids` — eine Vereinigung, die Dubletten mitschleppt, ist keine. Gefunden beim Halten der Magneten-Konvention gegen den Bestand. **Nicht mitgeändert:** Ob dedupliziert wird und wo — beim Auflösen, beim Schreiben oder beim Lesen — ist eine Entscheidung.

**Geschlossen, wenn** `entitaet_ids` traegt jede Kennung einmal.

---

## Chat 148 (18.08.2026) — aus der Werkzeugreihe Vera

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Antwortpfad](novaberg-bugs-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Drei Defekte aus einem 20-Turn-Bogen auf einem eigenen Paar (`vera`), mit angehaltenem Pixie gefahren. Die Reihe liegt in `labor/bogen/bogen_vera_werkzeuge.yaml`, das Ergebnis in `labor/ergebnis/`.

### `FALSCHE-BESTAETIGUNG-WIRD-ERINNERUNG`
**Kategorie:** GED

**Rang:** ~~**mittel**~~ → **hoch** (16.10.2026: der scharfe Fall ist gemessen — die falsche Bestätigung ging ins Gedächtnis, und zwei Turns später nannte die Antwort zwei Notizen, die es nicht gibt) — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt als Rest. Punkt 1 und 2 der Entscheidung vom 16.09.2026 sind gebaut (Korrektursatz `2eb77ed`, Ausgang am Turn `f0e3d53`, beide 18.09.2026); offen sind Punkt 3, der Nachtrag am Gedächtnisknoten beim Audit, und ~~die Messung des scharfen Falls im Betrieb~~ → der scharfe Fall ist am 16.10.2026 gemessen und die Lücke, durch die er ging, gebaut; offen ist die Messung danach (Zustand).

**Zustand:** **offen — der scharfe Fall ist am 16.10.2026 gemessen, die Lücke, durch die er ging, am selben Tag gebaut und am Abend geschärft (noch nicht committet); in der zweiten Simulation trat er nicht auf, der Bestandsabgleich ist im Betrieb ungemessen; offen bis zu dieser Messung und bis zum Nachtrag am Gedächtnisknoten** (unten, *Der scharfe Fall* und *Die zweite Simulation*). ~~offen — der scharfe Fall ist am 16.10.2026 gemessen, die Lücke, durch die er ging, am selben Tag gebaut; offen bis zur Messung an einem frischen Prüf-Nutzer und bis zum Nachtrag am Gedächtnisknoten~~ *Davor:* offen — gegen HEAD `9bcd214` nachgesehen am 24.08.2026, unveraendert seit `62560cf`. **Die zweite Haelfte ist gebaut:** Die Verdichtung sieht den Ausgang. `agents/kzg/dispatch.py::abgelehnte_ausgaenge` zieht die abgelehnten Dienste samt Befund aus `agent_results`, und `agents/kzg/verdichtung.py` setzt daraus den Block `[TATSAECHLICHER AUSGANG]` **vor** das Bewertungsobjekt — als Tatsache, nicht als Regel. Elf Zeugen (`tests/test_kzg_ausgang_im_kern.py`), Gegenprobe 3 vorhergesagt / 3 gezaehlt, Suite `Ran 2067 tests — OK`. Im Betrieb belegt am 22.08.2026, 00:16 UTC: `timeline` lehnte ab, `Ausgangsblock gesetzt — 1 abgelehnte(r) Dienst(e)`, der Kern trug reinen Inhalt.

> **Der Eintrag bleibt trotzdem offen, und zwar aus zwei Gruenden.** Erstens: Die Antwort jenes Messturns behauptete gar keine Handlung — belegt ist, dass der Weg **laeuft**, nicht dass er den Fehler **verhindert**. Der scharfe Fall verlangt eine Antwort, die eine abgelehnte Handlung bestaetigt, und den stellt das Modell her, nicht der Messende. Zweitens: Die erste Haelfte — dass die Antwort selbst keine Bestaetigung enthaelt — haengt weiter an einer Anweisung im Prompt der Figur (`server/graph/nodes/planner.py`, seit dem 20.08.2026) und ist keine Zusicherung.

> **Nachgesehen am 24.08.2026 gegen HEAD `9bcd214`: unveraendert in der Sache, der Zeiger ist tot.** `planner.py:67` traegt heute den `refusals`-Filter. Die Anweisung steht in der Prompt-Vorlage `responder.aufgabe_ablehnung`, gesetzt von `_build_task_ablehnung` (`:165`) — sie ist damit weiterhin eine Anweisung an die Figur und keine Pruefung im Code. Der einzige Riegel dort ist eine Ausgabe-Verifikation auf **leeren Text**, nicht auf eine Bestaetigung.

> **Gebaut am 15.09.2026: Die erste Hälfte hängt nicht mehr an der Anweisung, sie wird gerechnet.** Die Auswertung des Tribunals erkennt eine Speicherbehauptung in der Antwort und hält sie gegen die Ausgänge der Dienste des Turns; ohne `abgeschlossen` — auch bei `abgelehnt`, `fehler` oder `rueckfrage` — geht die Antwort in die Korrekturrunde (`utils/storage_claims.py`, `graph/nodes/tribunal.py::_storage_claim_step`; `novaberg-node-tribunal.md`, *Die Speicherbehauptung*). **Der Originalfall dieses Eintrags ist darunter:** Die Antwort vom 18.08.2026, 00:05 UTC, kam in der echten Korrekturrunde unter `gemma4-a4b-gpu` als Wiedergabe des Wunsches zurück, ohne die Bestätigung; die Erklärung des Fehlschlags blieb stehen `[gemessen 15.09.2026, Labor, Lauf 3]`. Über alle 24 Behauptungen des Bestands ab 14.08.2026: **20 sauber, 2 Grenzfälle, 2 überstanden beide Runden**.
>
> **Der Eintrag bleibt offen.** Die Schließbedingung verlangt eine Antwort ohne Bestätigung — zwei von 24 behielten sie über beide Runden, gemeldet und nicht verhindert. ~~Ob eine solche Behauptung aus der Antwort entfernt wird, ist offen~~ → **am 16.09.2026 entschieden, nicht gebaut:** Sie wird nicht entfernt; ein Korrektursatz wird angehängt, der Ausgang am Turn vermerkt, und ein später gefundener Fall am Gedächtnisknoten nachgetragen — also genau an dieser Kennung (`novaberg-thinking-lage_k.md`, Scheibe 12, *Offen für den Bau*). Und der scharfe Fall im **Betrieb** — ein Dienst lehnt ab, die Antwort bestätigt, die Korrektur beseitigt es — ~~ist nicht gemessen; im Betrieb belegt ist nur der dauerhafte Eintrag der Prüfung~~ → **gemessen am 16.10.2026, und die Korrektur blieb aus** (nächster Absatz).

> **Der scharfe Fall, gemessen am 16.10.2026** in einer Simulation an einem Prüf-Nutzer (`labor/2026-10-15_sim_timeline_notizen/simnachher1/`): Ein Notizauftrag ging an die Timeline, die mit `fehler` endete (`NOTIZAUFTRAG-GEHT-AN-TIMELINE`); die Antwort bestätigte, notiert zu haben. Die Speicherprüfung fand die Behauptung (`nicht_belegt`), **der Bestandsabgleich ergab trotzdem `gefunden` — durch einen fremden Termin:** Die Lage trug als akutes Objekt einen älteren Termin, nach dem im Turn niemand fragte, und der stand im Kalender. Keine Korrektur, kein Korrektursatz. Die Bestätigung stand im Kurzzeitgedächtnis, und **zwei Turns später zählte die Antwort zwei Notizen auf, die es nicht gibt**, und ließ die echte weg. Damit ist im Betrieb belegt, was dieser Eintrag beschreibt: Eine falsche Bestätigung wird Erinnerung und kommt als Tatsache zurück.
>
> **Gebaut am 16.10.2026** (getestet, im Betrieb nicht gemessen): Ein gefundener Termin deckt nur die Behauptung, deren Satz ihn nennt — über die Uhrzeit, den Tag oder ein Inhaltswort des Titels aus dem Bestand; nennt ein behauptender Satz keinen, wird korrigiert, und der dauerhafte Eintrag trägt `bestandsabgleich: gefunden_nicht_genannt` (`server/utils/storage_inventory.py::check_inventory`, `names_appointment`; 18 Zeugen in `server/tests/test_storage_inventory_naming.py`, Server-Suite 4440, grün). Bauart und benannte Grobheiten: `novaberg-node-tribunal.md`, *Die Nennung*. **Offen bleiben** die Messung an einem frischen Prüf-Nutzer — im Eintrag der Speicherprüfung `gefunden_nicht_genannt` statt `gefunden`, keine Bestätigung ohne Schreibung — und Punkt 3, der Nachtrag am Gedächtnisknoten: Eine falsche Bestätigung, die beide Korrekturrunden übersteht, geht weiter ins Gedächtnis.

> **Die zweite Simulation, 16.10.2026, 16:42–19:40 UTC** — an einem frischen Prüf-Nutzer, mit dem ersten Bau im Dienst (`labor/2026-10-15_sim_timeline_notizen/simnachher2/`): **0 falsche Bestätigungen** in 20 Sätzen (in der ersten Simulation 3). Der scharfe Fall trat nicht auf: Kein älterer Termin war akut, und beide Notizaufträge erreichten die Notizen. Die Speicherprüfung schlug nie an — jede Behauptung war durch einen abgeschlossenen Dienst gedeckt, oder es gab keine —, und **der Bestandsabgleich wurde kein einziges Mal befragt**. Gebraucht wurden weder der Riegel noch der Router-Vorzug aus `NOTIZAUFTRAG-GEHT-AN-TIMELINE`; beide sind in der Lage des Defekts im Betrieb ungemessen.
>
> **Die dritte Simulation, 17.10.2026** (`simnachher3`, Prüf-Nutzer): Eine Antwort auf eine reine Lesefrage behauptete, sie habe den Termin eingetragen, und galt als gedeckt, weil ein lesender Dienst jede Behauptung deckte — dieselbe Klasse in der Gegenrichtung zum Bestandsabgleich. Seit dem 17.10.2026 deckt ein Lesevorgang nicht mehr (gebaut, noch nicht committet; `novaberg-node-tribunal.md`, *Ein Lesevorgang deckt nicht*). Der scharfe Fall dieses Eintrags trat nicht auf.
>
> **Geschärft am 16.10.2026, abends** (gebaut und getestet, noch nicht committet): Ein Tag nennt den Termin nur zusammen mit der Uhrzeit oder einem Titelwort; ein Satzwort, das nur einen Tag sagt, trägt keinen Titel; die Art, die die Zeile selbst führt (`event_type`), wird aus den Titelwörtern gekürzt, auch in Zusammensetzungen und mit Fugen-s, das ganze Wort bleibt vorwärts nennbar; die Gegenrichtung des Präfixvergleichs gilt erst ab 7 Buchstaben; eine Zeile ohne Art meldet sich laut (`server/utils/storage_inventory.py`, `names_appointment`, `title_words`; 35 Zeugen in `server/tests/test_storage_inventory_naming.py`, Server-Suite 4457, grün). Bauart: `novaberg-node-tribunal.md`, *Die Nennung, geschärft*.
>
> **Benannte Restlücken** — Wege, auf denen eine falsche Bestätigung auch danach stehen bleibt (*teuer*) oder eine wahre korrigiert wird (*billig*):
>
> - *teuer, selten:* ein Tageswort im Titel gegen ein Kompositum im Satz (Titel *„Yoga Mittwoch“*, Satz *„… das Mittwochstraining …“*) — gewollt, ein Kompositum ist kein Tageswort;
> - *teuer, selten:* *Sonnabend* — die Wochentagsnamen der Tageserkennung führen nur *Samstag*;
> - *teuer:* Abwandlungen, die die Tageserkennung nicht liest — *Sonntags* am Satzanfang (gegen *„Sonntagsbrunch“* rückwärts, gegen *„Brunch Sonntag“* vorwärts), *Wochenende* gegen einen Titel mit *Wochenende*, ein Monatsname gegen einen Titel mit demselben Monat;
> - *teuer, entlegen:* hinten ein *s*, das zum Wort gehört, fällt mit der Art (*Kreistermin* → *krei* nennt auch *Kreide*);
> - *billig:* vorn ein *s*, das zum Wort gehört (*Terminsache* → *ache*: *Sache* allein nennt nicht), und die Gegenrichtung unter 7 Buchstaben (*Physio* gegen *„Physiotherapie“*);
> - die Beispiele sind synthetisch.

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

**Rang:** **mittel** — still; ~~wartet auf eine Absicht: woher die Zusammenfassung einer im KZG-Pfad nebenbei aufgelösten Entität kommt.~~ → **entschieden am 06.10.2026** (unten). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: die Zusammenfassung fehlt weiter (`server/agents/kzg/magnete.py:153-158` und `server/plugins/fakten_manager/manager.py:449-454` rufen ohne sie; `update_zusammenfassung` hat keinen Aufrufer außerhalb der Tests).

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: Ein **Nachlauf im Hintergrund** füllt fehlende Zusammenfassungen; das Anlegen im KZG-Pfad bleibt ohne Modellaufruf. Der Magnet-Pfad bleibt schnell, und der Nachlauf hat den Kontext mehrerer Erwähnungen.

**Zustand:** offen, **zur Haelfte erledigt** — gegen HEAD `b8e9543` und den Bestand nachgemessen am 25.08.2026. **Das Embedding ist gebaut:** `create_new_entity` erzeugt es immer, das Feature-Flag ist entkernt; im Bestand **0 von 817** Entitaeten ohne Embedding. **Die Zusammenfassung ist es nicht:** `zusammenfassung` ist zwar Parameter, aber **802 von 817** Entitaeten tragen keine. Der Eintrag nennt beide Felder; er ist nach der Regel, dass ein Eintrag mit mehreren Stellen erst geschlossen ist, wenn jede steht, deshalb offen.

**Nachgemessen am 16.08.2026: 0 von 704 Entitaeten ohne Embedding.** Das Symptom ist weg. **Ungeprueft bleibt das Warum** — ob der Erzeuger nachgezogen wurde oder ein Nachlauf gefuellt hat; ohne diese Antwort ist nicht entscheidbar, ob neue Entitaeten weiterhin leer entstehen und nur nachtraeglich gefuellt werden. Der Eintrag bleibt bis dahin offen.

**Befund (2026-07-29).** Entitäten entstehen ohne Zusammenfassung und ohne Embedding. Einziger aktiver Erzeuger ist `agents/kzg/magnete.py`, `_entitaeten_aufloesen` → `EntityResolutionService.create_new_entity(postgres_url, user_id, name, typ)` — vier Argumente, `zusammenfassung` und `embedding` sind nicht darunter. Gemessen 28.07.2026: **88 von 89** aktiven Entitäten haben ein leeres `zusammenfassung`-Feld; nur die eine `user`-Entität trägt eines (die aus `api/chat.py` stammt, wo beide Felder gesetzt werden). Die Spalten existieren beide in `entitaeten`. Wirkung heute: Jede Suche über die Zusammenfassung ist ohne Substrat — das war Tür 2 des GV-Entity-Hop-Befunds — und eine Embedding-Suche über Entitäten ist gar nicht möglich. Wirkung morgen: M2.5b und die Entity-Resolution selbst hängen an denselben zwei Feldern. Offen ist nicht der Fix, sondern die Frage, **woher** die Zusammenfassung einer im KZG-Pfad nebenbei aufgelösten Entität kommen soll — der Magnet-Pfad ist nicht-interaktiv und hat nur den Namen.

**Nachtrag 20.10.2026, aus der Fundliste:** `create_new_entity` duldet einen Fehler des Embeddings mit einer Warnung und legt die Entität ohne Vektor an (`server/memory/services/entity_resolution.py`, Z. 485–486). Seit dem 20.10.2026 ruft auch der Schreibweg des Fakten-Agenten die Funktion (`server/agents/fakten/suche.py`, Z. 133). Eine Warnung im Log ist nicht *gemeldet* im Sinn der Schließbedingung unten: Kein Leser der Entität erfährt es. → **21.10.2026, behoben (~~im Tree, nicht committet~~ → committet):** Der Ausfall wird mit `logger.error` und der ID gemeldet; die Zeile bleibt `embedding IS NULL` und wird vom Repair beim Start gefüllt ~~(ob das genügt, ist eine offene Frage)~~ → das genügt, entschieden am 21.10.2026 (`novaberg-memory-fakten_e.md` A Nr. 39): ohne den Rückfall im Magnet-Pfad hat das Embedding einer Entität keinen Leser. Für das Embedding ist die Schließbedingung damit erfüllt, sobald der Bau im Betrieb gemessen ist; offen bleibt die Zusammenfassung (Nachlauf vom 06.10.2026).

**Was fertig waere.** Eine Entitaet entsteht mit Zusammenfassung und Embedding, oder ihr Fehlen ist gemeldet.

**Prioritaet:** hoch.

#### GRAVITATION-KLEMME-FEHLT 🔧 offen
**Kategorie:** GED

**Rang:** **niedrig** — still, heute nicht beobachtbar: Seit dem Skalenumbau entstehen nur Werte in [0, CAP]. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt, `server/ei/gravitation.py:732-738` übernimmt ungeklemmt, Vorgabe 0.5 bei unlesbarem Feld.

**Befund (2026-07-29).** Die Klemme in `ei/gravitation.py` fehlt weiterhin: Zeile 336 übernimmt `salienz` ungeklemmt als `gewicht` in den Lesepfad. Der Backlog führt sie als Sofortfix (`KZG-SALIENZ-KONSUMENTEN-DISSENS`, Entscheidung aus Chat 109) und hält im selben Eintrag fest, dass sie nach dem Neubau zwar rechnerisch wirkungslos, aber **als Zusicherung des Lesers an sich selbst** richtig bleibt. Seit dem Salienz-Neubau vom 28.07. kann kein Wert über 1.0 mehr entstehen; die Zusicherung ist damit nicht erfüllt, sondern nur unbeobachtbar geworden.

**Was fertig waere.** Der uebernommene Wert ist auf seine Spanne geklemmt, oder ein Wert ausserhalb wird gemeldet.

**Prioritaet:** hoch.

### Chat 133 — aus der Fundliste klassifiziert, Block 31.07. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Antwortpfad](novaberg-bugs-antwortpfad.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Acht Defekte. **Vier davon sind Prompt-Bloecke, die etwas ueber den Nutzer behaupten, was Novas Zustand ist** — dieselbe Verwechslung an vier Stellen, jede fuer sich unauffaellig.

#### SALIENZ-ZEITFELD-FAELLT-AM-LIMIT-ZUERST 🔧 offen
**Kategorie:** GED

**Rang:** **mittel** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `repair_truncated_json` schließt eine abgeschnittene Antwort (`server/services/postprocess.py`), `server/graph/nodes/salience.py:710-711` macht aus dem fehlenden Feld `""` ohne Kennzeichnung.

**Befund (2026-07-31).** **`zeitausdruck_roh` ist das letzte Feld des Salienz-Antwortschemas**, und die Salienz läuft mit `max_output_tokens: 1024`. Läuft eine Antwort ans Limit, fehlt dieses Feld als erstes — und ein fehlendes Feld ist von „kein Zeitbezug erkannt" nicht zu unterscheiden. Ob es im Betrieb zuschlägt, ist **nicht gemessen**; die Beobachtung stammt aus dem Lesen des Schemas, nicht aus einem Ausfall. Dieselbe Klasse wie `lesson_l_default-wie-fehlschlag`: Der Ausfall sieht aus wie ein Ergebnis. Wer es prüft, zählt abgeschnittene Antworten im Salienz-Pfad; wer es entschärfen will, zieht das Feld im Schema nach vorn.

**Was fertig waere.** Ein abgeschnittenes Schema ist von einem vollstaendigen mit leerem Feld unterscheidbar.

**Prioritaet:** hoch.

### Chat 133 — aus der Fundliste klassifiziert, Block 05.–02.08. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Acht Defekte aus dem zweiten Fundlisten-Block. **Der Befund steht im Wortlaut, in dem er notiert wurde** — er trägt Beleg und Datum und wird nicht nacherzählt; ergänzt sind Kennung, Priorität und die Zeile, an der man erkennt, wann der Eintrag geschlossen ist.

Drei von ihnen sind stille Vorgabewerte an einer Stelle, an der ein Ausfall gehört: eine feste Salienz, eine Priorität, die auf null fällt, und ein Pflichtfeld, das leer durchgeht.

#### SALIENZ-JSON-BRICHT-AN-LATEX 🔧 offen
**Kategorie:** GED

**Rang:** **mittel** — laut (Fehlerzeile, Segment verworfen), aber die Erinnerung geht verloren. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `parse_json_strict` kennt keine Reparatur von Backslash-Folgen, die Salienz-Prompts verbieten LaTeX nicht.

**Zustand:** offen, **unbelegt** — nachgesehen am 25.08.2026. Der juengste JSON-Fehler im Salienz-Pfad stammt vom **12.08.2026**; in den 13 Tagen danach steht keiner mehr im Protokoll. Von vier Fehlerzeilen des Knotens in 14 Tagen nennt genau eine das Parsen. **Ob die Ursache weg ist oder nur nicht getroffen wurde, ist nicht entschieden:** Der Defekt braucht Formeln in der Modellantwort, und das haengt am Gegenstand des Gespraechs, nicht am Code.

**Befund (2026-08-02).** **Die Salienz-Bewertung scheitert an LaTeX in der Modellantwort.** Belegt beim Abnahme-Turn zu P9 (19:15:01 UTC): `ChatWorker 'chat': JSON-Parsing fehlgeschlagen (caller=salienz/segment, fehler=Invalid \escape)`. Das Modell antwortet mit Formeln — `$T_H$`, `\propto`, `\n\n` im Fließtext —, und `parse_json_strict` bricht am Backslash ab. **Das erklärt vermutlich die 6 `salienz`-Fehler**, die im Pipeline-Log der letzten sieben Tage stehen (von insgesamt 11): Der Korpus ist Physik, und Physik schreibt sich in LaTeX. Der Turn selbst lief durch, nur seine Bewertung fiel aus — der Eintrag bekommt damit keine Salienz und wird nicht promotet.

**Was fertig waere.** Der Parser haelt Backslash-Sequenzen aus, oder die Anweisung verbietet LaTeX im Fliesstext — und ein Parse-Fehler faellt nicht als leeres Ergebnis durch.

**Prioritaet:** mittel.

---

### Agent-System (Epic 11, Chat 22–29)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Wissen](novaberg-bugs-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### BUG3 — "Bruder" als Verwandtschaft statt Anrede-Slang ⬜
**Kategorie:** GED

**Rang:** **niedrig** — der Eintrag nennt weder Stelle noch Beispiel und ist nicht gegen den Code prüfbar (Durchsicht 05.10.2026, gegen HEAD `17bf86e`). Eine Regel *„Bruder als Anrede“* gibt es in den Prompts nicht.

**Entdeckt:** Chat 19
**Prio:** Niedrig — kosmetisch, nur bei jugendlichem Stil.

---

### Datenqualität

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Gedächtnis**, die uebrigen in [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

---

#### CLUSTER-META-CONTAMINATION — Pipeline-Meta-Begriffe als Themen-Tags
**Kategorie:** GED

**Rang:** **mittel** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt an der Ursache; der Cluster-Pfad ist weg (`8a0e5c2`), aber die Themenextraktion (`server/prompts/default/salienz.dimensionen.txt:4-6`) nennt keine Meta-Begriffe als Ausschluss, und `SALIENZ_THEMEN_STOPWORDS` gibt es nicht.

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

### Chat 78 — TimelineAgent-Audit + Thinker-Findings

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

**Rang:** **niedrig** — still, nur die Summenzeile des Laufs. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt an der aktiven Stelle (`server/agents/synapsen_promotion/agent.py:350`); die *dormant* genannte Stelle gibt es nicht mehr. **Dieselbe Ursache wie `PROMO-LAUF-ZAEHLT-VERWORFENE`** — eine Änderung schließt beide.

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

**Rang:** **mittel** — still; ~~wartet auf eine Absicht: eine oder zwei Spuren je Impuls, und wenn zwei, welches Feld sie unterscheidet.~~ → **entschieden am 06.10.2026** (unten). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; beide Graphen rufen `dispatch_kzg`, der KZG-Hash trägt kein unterscheidendes Feld.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: **Beide Spuren bleiben**, und ein Feld unterscheidet sie — Einfall und Aussprechen sind zwei Ereignisse. Das Feld ist eine Schemaänderung und wird vor dem Bau angekündigt.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: ein Impuls schreibt ueber beide Graphen unter derselben `turn_id`. Zaehlbar, aber nur an einem Impuls-Turn, den es zu erzeugen gilt.
**Entdeckt:** Chat 110, nach der Umverdrahtung des Impuls-Pfads.

**Klasse:** Doppelte Persistenz durch zwei Graphen auf einem Turn. Severity **mittel** — kein Datenverlust, aber ein Gedanke wiegt doppelt.

**Symptom:** Ein Impuls durchläuft **beide** Graphen unter derselben `turn_id`: den AgentGraph (der Gedanke entsteht) und den CharacterGraph (er wird gedacht und gesprochen). Beide rufen `dispatch_kzg` auf, beide schreiben unter `beobachter='assistant'` — mit **verschiedenen** Kernsätzen, weil sie verschiedene Texte verdichten. Zusammen mit KZG-SEGMENT-DUPLIKAT ergeben sich sechs Einträge aus einem Impuls.

**Beleg:** Impuls-Turn `57b6e84c…` — sechs Einträge, **alle** `beobachter='assistant'`, **kein** `user`-Eintrag (richtig, es gab keinen Nutzer-Reiz). Zeitlich zwei Blöcke: `…16738` bis `…16773` (AgentGraph, 18:47) und `…17977` bis `…18006` (CharacterGraph, 18:49). Zum Vergleich der Nutzer-Turn: ein `user`-Eintrag aus dem HumanGraph, `assistant`-Einträge aus dem CharacterGraph.

~~**Offene Frage, nicht entschieden:**~~ → **entschieden am 06.10.2026: beide Spuren, mit einem unterscheidenden Feld** (oben). Soll ein Impuls beide Spuren tragen? Dafür spricht, dass Entstehen und Aussprechen verschiedene Ereignisse sind — der Mensch erinnert den Einfall anders als das Gesagte. Dagegen spricht, dass beide unter demselben Beobachter stehen und für jeden Leser ununterscheidbar sind. **Wenn beide bleiben, brauchen sie ein unterscheidendes Feld.**

**Status:** Offen, ~~Entscheidung ausstehend~~ → entschieden am 06.10.2026, nicht gebaut. **Verwandt:** KZG-SEGMENT-DUPLIKAT.

---

---

### 19.09.2026 — aus dem Bau von `KZG-ERSTELLT-AM-PARSE-HÄRTE`

#### PROMO-LAUF-ZAEHLT-VERWORFENE — der Lauf der Synapsen-Promotion zählt einen verworfenen Eintrag als promotet
**Kategorie:** GED

**Rang:** **niedrig** — still, nur die Laufzeile. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt (`server/agents/synapsen_promotion/agent.py:350`, Verwurf an `:409-449`). Dieselbe Ursache wie `BATCH-ZAEHLER-ZAEHLEN-AUFRUFE`.

**Zustand:** offen — am Code gelesen am 19.09.2026, nicht gemessen.

**Klasse:** Ein Zähler, der einen Fehlschlag als Erfolg führt. Severity **niedrig**: Es geht kein Datum verloren, aber das Audit des Laufs gibt ein falsches Bild.

**Symptom:** `_eintrag_verarbeiten` (`server/agents/synapsen_promotion/agent.py`) verwirft einen Eintrag, dessen Vorbedingung nicht hält, über `_fehler` und kehrt dann normal zurück. `_paar_abarbeiten` zählt darauf `promotet += 1`. Das Verwerfen selbst ist gewollt, der Eintrag wird nie grün. Die Laufzeile `promotet=…, fehler=…` sagt aber nicht, wie viele Einträge verworfen wurden. Betroffen sind alle vier Vorbedingungen, die vierte (unlesbarer Anlagezeitpunkt) seit `404a19a`.

**Soll:** Der Lauf führt verworfene Einträge getrennt von promoteten. Die einzelnen Fehlerzeilen stehen schon heute im `pipeline_log`.

**Status:** Offen. Eingeordnet aus der Fundliste am 19.09.2026. **Verwandt:** `KZG-ERSTELLT-AM-PARSE-HÄRTE` (Backlog, abgeschlossen).
