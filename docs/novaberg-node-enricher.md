# Novaberg — Node: Enricher

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Enricher
**Stand:** 18. August 2026 (der Dateien-Index als Kontextquelle neben der Plugin-Schleife, §3.1a — seit dem Nachmittag zweikanalig)
**Pfad:** novaberg/docs/novaberg-node-enricher.md
**Quellen:** nova-01-m-c.md
**Datei:** `graph/nodes/enricher.py`

---

## 1. Aufgabe

Der Enricher ist Novas Gedächtnis-Schnittstelle — seit Chat 59 ein **reiner I/O-Node**. Er lädt den Memory-Kontext — Session, KZG, LZG, Plugin-Daten — und stellt ihn dem Graph zur Verfügung. Die emotionale Intelligenz wird **nicht mehr** hier berechnet, sondern im nachgelagerten EI-Calc-Node. Charakter-/Identitäts-Daten lädt seit Phase 2 (Chat 89) der `db_zugriff`-Node am CG-Eingang.

**Kein LLM-Call.** Der Enricher macht ausschließlich Datenzugriffe und Embedding-Erzeugung.

**Keine EI-Berechnung mehr.** Alle 12 EI-Funktionen (Verlauf, Vektor, Modus-/Stil-Plausibilität, Nova-Empathie) sind in `ei/berechnung.py` ausgelagert und werden vom neuen EI-Calc-Node aufgerufen.

→ Details: `novaberg-node-ei-calc.md`

---

## 2. Position im Graph

```
HumanGraph (Pfad 1, 5 Nodes):
perzeption → ▶ enricher ◀ → ei_calc → salience → dispatcher

CharacterGraph (Pfad 2, 17 Nodes):
db_zugriff → ei_calc → ▶ enricher ◀ → emotionale_gravitation → reducer → router → planner → agent_dispatch
          → gv_node → responder → thinker → tribunal → evaluate → corrector
          → perzeption_assistant → ei_calc_persist → salience → dispatcher
```

**HumanGraph:** Zweiter Node, nach Perzeption (unverändert seit Phase 4).

**CharacterGraph:** Vierter Node, nach `db_zugriff → ei_calc`. Der Enricher liest aus `state["external"].character` (vom `db_zugriff` befüllt) und aus `state["internal"].emotion` (vom `ei_calc` aktualisiert mit Empathie-Modulation).

**Reihenfolge-Logik (Phase 2):** EI-Calc läuft im CG **vor** dem Enricher, weil das Empathie-Update gegen Novas persistierten Vorzustand berechnet wird, bevor Memory-Resonanz hinzukommt.

**Input:** State mit Perzeptionsergebnissen (Emotion, Arousal, Modus). Router-Flags (`needs_memory`, `needs_timeline`) spielen hier keine Rolle mehr, weil der Enricher jetzt vor dem Router läuft — er lädt alles, was später gebraucht werden könnte.

**Output:**

**HumanGraph (`_enrich_human`, 5 produktive Felder):**
`raw_turns`, `user_intentionen`, `prompt_embedding`, `aktivierte_ziele`, `gravitationsterm`

**CharacterGraph (`_enrich_character`, 8 produktive Felder):**
`raw_turns`, `session_turns` (Shadow-Impulse gefiltert), `user_intentionen`, `prompt_embedding`, `aktivierte_ziele` + `gravitationsterm`, `emotionale_gravitationspunkte`, `memory_entries`, `lzg_resonanz`

→ Vollständige Tabelle: §4 Geschrieben.

---


## Query Rewriting — der Schlüssel trägt den Gegenstand des Gesprächs

**Seit dem 20.08.2026 ist der eingebettete Text nicht mehr die rohe Äußerung.** Ein Turn wie *„und wie weist man das nach?"* nennt seinen Gegenstand nicht, er zeigt auf ihn zurück — und der Vektor daraus suchte ohne ihn — in **fünf** Konsumenten zugleich, weil sie denselben Schlüssel benutzen: KZG, LZG, die Bibliothek über den `WissenManager`, der Dateienindex (`aufzeichnungen`) und die beiden NMCP-Dienste `wissen` und `dateien`, denen `such_vektor` als angemeldeter Bedarf mitwandert.

**Die Zahl fünf stammt aus der zweiten Kontrolle, nicht aus dem Bau:** Der Befund, der den Umbau ausgelöst hat, nannte drei Speicher. Ein Suchlauf über die Leser des Schlüssels fand zwei weitere — und für die ist die Wirkung des Rewritings **ungemessen**, weil die Sonden gegen die Bibliothek liefen.

`_suchtext_bauen` formt aus dem Verlauf eine eigenständige Suchanfrage. **Ein Modellaufruf, und damit der einzige des Enrichers** — der Modulkopf sagte bis dahin ausdrücklich *„kein LLM-Aufruf"*.

**Gemessen vor dem Bau**, gegen 306 Ausarbeitungen und zehn Verläufe mit anaphorischem Schlussturn:

| Arm | Rang 1 | über der Abrufschwelle | Median-Rang | Median-Kosinus |
|---|---|---|---|---|
| rohe Äußerung (Zustand bis 20.08.) | 0/10 | **0/10** | 155,5 | 0,1865 |
| Rewrite auf **Frageform** | 3/10 | **5/10** | 10,5 | 0,4173 |
| Rewrite auf Themenform | 2/10 | 3/10 | 32,0 | 0,3514 |
| die ausgeschriebene Referenzfrage | 2/10 | 2/10 | 8,0 | 0,3971 |

> **Der vierte Arm war als Obergrenze gedacht und ist keine.** Das Rewrite schlägt die von Hand ausgeschriebene Frage. Erklärbar ist das damit, dass es aus demselben Modell stammt, das die Ausarbeitungen geschrieben hat: Es trifft die Sprache des Bestandes, die Handformulierung trifft die Sprache des Fragenden.

**Beidseitig gesondet.** Bei drei Verläufen mit Themenwechsel bleibt der **alte** Gegenstand in 3 von 3 Fällen unter der Schwelle — das Rewrite schreibt den neuen. Bei fünf Alltagsverläufen ohne Bezug zur Bibliothek kommt in 15 von 15 Kombinationen kein Treffer über sie.

**Was ausdrücklich nicht mitzieht: die Zielaktivierung.** Sie rechnet weiter gegen das rohe Embedding — aus demselben Grund, aus dem sie schon nicht mit dem verschobenen Vektor rechnet: Sie wäre sonst ihre eigene Eingabe. Der Rewrite kostet deshalb ein zweites Embedding, und nur dann, wenn er auch stattgefunden hat.

**Die Antwort des Modells ist eine externe Quelle und wird geprüft:** erste Zeile, nicht leer, nicht länger als die Plausibilitätsgrenze; ein vorangestelltes `Suchanfrage:` fällt weg. Jeder Ausgang, der nicht `rewrite` heißt, liefert die rohe Äußerung und **meldet sich laut** — `abgeschaltet`, `zu_wenig_verlauf`, `verlauf_leer`, `leer`, `zu_lang`, `aufruf_gescheitert`. Frist und Ausgabegrenze stehen als Paar an der Aufrufstelle.

**Im Betrieb gemessen am 20.08.2026**, an einem echten Turn:

```
roh      : "Und wie weist man das eigentlich nach?"
Rewrite  : "Wie weist man das Informationsparadoxon bei Schwarzen Löchern nach?"
herkunft : rewrite      turns_gesehen: 23
```

> **Der erste echte Turn hat einen Defekt gefunden, den zehn grüne Zeugen nicht sehen konnten.** Die Turns der Session tragen `rolle` und `inhalt`; der Bau las `role` und `content` und verwarf damit jeden Turn. Das Modell bekam seine Aufgabe ohne Verlauf und **fragte danach** — die Rückfrage *„Bitte stelle mir den Verlauf zur Verfügung"* wurde der Suchschlüssel. Seither steht ein Riegel davor: Ein leerer Verlauf bei vorhandenen Turns ist ein Defekt und kein Randfall.

---

## 3. Kontextquellen

**Hinweis (seit Chat 59, vereinfacht in Phase 3):** Der fünfte Abschnitt „Emotionale Intelligenz" wurde entfernt. Alle EI-Berechnungen laufen jetzt im EI-Calc-Node (→ `novaberg-node-ei-calc.md`). Der Enricher übergibt als Brücke nur noch `raw_turns` an den State.



### 3.1 Session-Kontext (immer, als erstes)

Lädt die bisherigen Turns des Gesprächs aus Redis. Zwei Bestandteile:

Session-Key seit Chat 60: `session:{user_id}:{character_id}:turns`. Der Enricher liest `character_id` aus dem State und verwendet `_session_key()` für den Summary-Key.

**Session-Summary:** Zusammenfassung älterer Turns (`session:{user_id}:{character_id}:summary`). Komprimierter Überblick über das bisherige Gespräch.

**Session-Turns (Chat 30: vollständiges Durchreichen):** Rohe Session-Turns werden vollständig in `state["session_turns"]` durchgereicht. Der Enricher filtert nur Shadow-Impulse (`[Nova-Impuls]`-Prefix im `kern`-Feld) — alle anderen Felder (inhalt, emotion, arousal, vektor, stil, dynamik, tone, kern, intentionen, modus) bleiben erhalten.

| Turn-Typ | Behandlung |
|----------|-----------|
| Shadow-Impuls (`[Nova-Impuls]` in kern) | **Komplett ausgeblendet** — nur in `_enrich_character`; `_enrich_human` hat den Filter nicht. **Seit Chat 110 wirkungslos:** Den Marker setzte allein die alte Delivery, auf dem neuen Pfad schreibt der CG-Dispatcher den Session-Turn ohne ihn. Ob der Filter noch gebraucht wird, ist offen — siehe `novaberg-pixie_l_kontamination.md` |
| Alle anderen Turns | **Vollständig durchgereicht** — alle Felder |

Jeder konsumierende Node formatiert die Turn-Dicts selbst:
- Responder: Originaltext (`inhalt`) + Emotion/Arousal in Turn-Headern
- Perzeption/Router: Gekürzter Text + Emotion als Annotation (via `format_session_turns_numbered()`)

→ Lesson: `novaberg-graph_l_datentransport.md — Daten vollständig transportieren`

> **Lesson gelernt (Chat 7):** Shadow-Delivery-Turns verunreinigten den Responder-Kontext. Lösung: Shadow-Turns werden komplett gefiltert. → novaberg-pixie_l_kontamination.md

> **Lesson gelernt (Chat 30):** Die frühe Destillation (`kern` statt `inhalt`, Metadaten als String-Tags) zerstörte emotionale Information. Der Responder sah sachliche Zusammenfassungen statt Originaltext und antwortete therapeutisch. Lösung: Vollständiges Durchreichen. → novaberg-graph_l_datentransport.md

### 3.1a Der Dateien-Index — die Quelle, die kein Plugin ist (18.08.2026)

Der Enricher fragt in jedem Turn den Index der freigegebenen Verzeichnisse ab (`agents/dateien_index/aufzeichnungen.py`), mit demselben `such_vektor`, mit dem KZG, LZG und die Bibliothek suchen. Die Treffer gehen in den eigenen Zustandskanal `aufzeichnungen`; der Verfasser rendert daraus den Block `[AUFZEICHNUNGEN]`.

> **Sie steht ausdrücklich neben der Plugin-Schleife und nicht darin, und das ist keine Ordnungsfrage.** Ein Plugin liefert `ContextEntry` in den `memory_entries`-Pool, und alles aus diesem Pool rendert der Formatter unter `[GEDAECHTNIS]`. **Dateiinhalt darf dort nicht hinein** (`novaberg-agent-dateien_k.md` §1a.2): Was in den Dateien steht, ist nicht Novas Erinnerung, und die Beschriftung ist die Aussage. Der Präzedenzfall steht offen im Bestand — sie hat die Biografie eines Menschen als ihre eigene übernommen.

| Größe | Wert | Herkunft |
|---|---|---|
| Kappung | 3 | `AUFZEICHNUNGEN_KAPPUNG` — die Zusicherung |
| Absoluter Boden | 0,30 | `AUFZEICHNUNGEN_BODEN` — gemessen am 18.08.2026, acht Sonden, beide Seiten |
| Auszug je Eintrag | 300 Zeichen | `AUFZEICHNUNGEN_AUSZUG_ZEICHEN` |

**Kein Dateizugriff und kein Modellaufruf** — die Zeile trägt Thema und Zusammenfassung, beides beim Indizieren einmal bezahlt.

**Seit dem 18.08.2026 zweikanalig, und der scharfe läuft zuerst.** Postgres zerlegt den Wortlaut des Turns mit `to_tsvector` in Lexeme — ohne Stoppwörter, ohne Modellaufruf. Trägt eine Datei einen davon in ihren **erhobenen Stichwörtern**, ist sie einschlägig, und **der Boden gilt für sie nicht**: Ein exakter Begriff schätzt nicht.

| Kanal | findet | Boden |
|---|---|---|
| scharf (Stichwörter) | den genannten Fachbegriff | nein |
| dense (Vektor) | Themennähe | ja, 0,30 |

`[gemessen]` — 18.08.2026: Zwei Treffer bei 0,1901 und 0,2148 lagen unter dem Boden und wurden **nur** scharf gefunden; eine Frage, deren Stichwort das Erschließungsmodell verstümmelt hatte, fing der dense Kanal bei 0,4904 auf. **Die beiden sind gegenseitige Absicherung, nicht Redundanz.**

**Die Protokollzeile trägt Trefferzahl, Bestand und den Kosinus des schlechtesten gelieferten Treffers.** Liegt die Trefferzahl dauerhaft auf der Kappung, hat nicht der Boden ausgewählt, sondern die Kappung — genau der Zustand, in dem die Bibliothek gemessen wurde (40 von 42 Aufrufen).

### 3.2 Plugin-Hooks (dynamisch)

Der Enricher iteriert über alle registrierten Manager-Plugins und ruft den Hook `manager.enrich_entries(state, postgres_url)` auf. Jeder Manager entscheidet selbst, ob er Kontext liefert:

| Manager | Liefert |
|---------|---------|
| FaktenManager | **Deaktiviert seit Chat 71** (`enricher.py:416-419`) — Hook wird übersprungen |
| TimelineManager | Anstehende Termine, heutige Ereignisse |
| NotizenManager | Betroffene Notiz bei Management-Intent |
| **WissenManager** | **Novas erarbeitete Bibliothek** (seit 04.08.2026) — Metadaten-Treffer über Embedding-Nähe |
| KzgManager | (kein enrich-Hook, KZG wird direkt geladen) |

Neue Plugins liefern automatisch Kontext — ohne Änderung am Enricher.

> **Die Hooks laufen seit dem 04.08.2026 NACH der Gedächtnissuche, nicht davor.** Bis dahin standen sie vor der Erzeugung des Prompt-Embeddings; ein Plugin, das über Embedding-Nähe sucht, hätte sich dreißig Zeilen vor dessen Erzeugung ein **zweites** rechnen lassen müssen — rund 1,6 s je Turn für denselben Vektor. Jetzt findet jedes Plugin `state["prompt_embedding"]` **und** `state["such_vektor"]` vor.
>
> **Was die Verschiebung anfasst, geprüft statt behauptet:** Von den Managern liefern nur Timeline, Notizen und Wissen; sie lesen ausschließlich Felder, die vor dem Enricher feststehen, und **keiner schreibt in den State**. Der Formatter gruppiert nach `quelle` statt nach Listenposition — die Plugin-Gruppe steht als Block, gleich wann sie angehängt wurde.
>
> **Der eine gefundene Effekt, benannt statt weggeredet:** Der Reducer entdoppelt bei identischem Inhalt nach höchstem Gewicht, bei Gleichstand nach Eingangsreihenfolge. Trägt ein Plugin-Eintrag denselben Text **und** dasselbe Gewicht wie ein KZG-Treffer, überlebt seither der andere von beiden — und weil `quelle` das Format steuert, erschiene derselbe Satz unter einem anderen Etikett.

### 3.2a Die Bibliothek als sechste Quelle (seit 04.08.2026)

Der `WissenManager` findet Novas erarbeitete Dateien **über die Datenbank, nicht über ihren Inhalt**: eine Abfrage gegen `autonomous_wissen` auf Embedding-Nähe zur Zusammenfassung, gefiltert auf Paar, `aktiv` und `typ='wissen'`. Berichte bleiben draußen — sie sind Prozessdokumentation für die Lagebeurteilung und im Prompt des Responders Rauschen (§7.5 des Konzepts).

**Der Suchschlüssel ist `state["such_vektor"]`** — derselbe, mit dem KZG und LZG gesucht haben, also die Frage plus Novas Motivation. Die Bibliothek ist Langzeitgedächtnis in Dateiform und wird mit demselben Ohr gehört.

**Das Gewicht wird umgerechnet.** `gewicht_decay` läuft bis `LZG_KNOTEN_GEWICHT_CAP` (10.0), der ContextEntry-Pool erwartet 0.0 bis 1.0. Ohne die Division schlüge jeder Bibliothekseintrag im Reducer jeden KZG-Treffer — eine Rangfolge aus zwei Skalen statt aus zwei Bedeutungen.

| Größe | Wert | Herkunft |
|---|---|---|
| Schwelle | 0.40 | **übernommen von `anker_retrieval`, nicht gemessen** — dort an 100 echten Prompts kalibriert. Gleicher Embedding-Raum, gleiche Art Anfrage; als Startwert vertretbar, als Ergebnis nicht. **Seit dem 17.08.2026 gemessen: sie greift nicht** — siehe unten |
| Top-K | 3 | Der Gesprächspfad hat 32768 Token, nicht die 262144 des Hintergrunds. **Faktisch ist dies die Auswahl, nicht die Kappung** |

> **Gemessen am 17.08.2026 — was hier auswählt, ist Top-K und nicht die Schwelle.** Über 42 protokollierte Aufrufe kamen **40 mal genau drei** Treffer zurück, also die Obergrenze; der Kosinus des dritten Treffers liegt bei Median **0,588** (min 0,404, max 0,691). Über den Korpus gerechnet — 217 aktive Einträge, 23.436 Paare, Median-Kosinus 0,369 — liegen **35,6 % aller Paare über 0,40**, für eine Abfrage also rund 77 von 217 Einträgen. Erst **0,55** ergibt gerechnet die drei Treffer, die tatsächlich ankommen. **Die wirksame Schwelle ist damit 0,55, und sie steht in keiner Konfiguration.**
>
> Die Übernahme von `anker_retrieval` war der Fehler und ist jetzt beziffert: Im Knotenraum, für den 0,40 kalibriert wurde, qualifiziert der Wert rund **1,4 %** des Bestandes (4,1 von 302) — in der Bibliothek **35,6 %**. Derselbe Embedding-Raum, **Faktor 26**. Eine Schwelle ist keine Eigenschaft des Raums allein, sondern des Raums **und** der Dichte des Korpus darin.
>
> **Offen bleibt die andere Hälfte** (`WIS-SCHWELLE-MESSEN`): Abdeckung und Fehltreffer über echte Prompts sind nicht gemessen, weil `such_vektor` nicht aufbewahrt wird. Die 35,6 % sind an Einträgen gegen Einträge gerechnet; belastbar ist die Richtung, nicht die zweite Nachkommastelle.

> **Stufe 2 fehlt.** Reicht die Zusammenfassung nicht, soll der Dateiinhalt gelesen werden (§7.3). Dafür fehlt der Lesepfad in `tools/dateien/` — und mit 262144 Token im Hintergrund ist dort eine andere Bauart möglich als die Mandelbrot-Navigation, die das Konzept aus dem 32k-Zwang ableitet.

### 3.3 KZG/LZG (semantische Suche)

Nur wenn Einträge existieren (Vor-Check zur Kostenoptimierung):

1. Prüfe ob KZG-Keys (`kzg:{user_id}:*`) in Redis existieren
2. Prüfe ob aktive LZG-Einträge in PostgreSQL existieren
3. Nur bei Existenz: Embedding für `user_prompt` erzeugen → semantische Suche in KZG und LZG

> **Designentscheidung (Chat 3):** Der Vor-Check vermeidet teure Embedding-Berechnungen bei leeren Speichern. Ohne Gedächtnis: ~0ms. Mit Gedächtnis: ~1.6s (Embedding) + Suche.

**LZG-Lesepfad (Synapsen-Konzept §8.1–8.4, live seit P5 / Chat 100):** Kein flacher LZG-Read mehr. Der Enricher ruft `spreading_lesen` auf (Anker-Knoten via `anker_retrieval`, dann Spreading Activation entlang der Kanten; Cluster aus dem Redis-Vorturn, Novas dominante Emotion aus `nova_emotions_verlauf`) und schreibt das Ergebnis als `state["lzg_resonanz"]` — bewusst an `memory_entries` vorbei. Der Reducer reicht das Objekt unangetastet an den Formatter durch, der den `[GEDAECHTNIS]`-Block rendert; die Erinnerungen durchlaufen damit keinen Dedup (REDUCER-SIEHT-LZG-NICHT, bugs.md).

**Kalibrierung Chat 107:** `anker_retrieval min_similarity` steht auf **0.40** (vorher 0.50), kalibriert auf `nomic-embed-text-v2-moe` per Abdeckungsmessung an 100 echten Prompts (82 % der Turns mit Anker, Ø 4.1 Anker; 100 % Abdeckung ist nicht das Ziel — Cold Start ist bei ankerlosen Prompts die richtige Antwort). ⚠ Wachposten, kein Endwert.

### 3.3a Wahrnehmungs-Gravitation (Synapsen-Konzept §8.5, live seit P10 / Chat 126)

Der Suchschlüssel der LZG-Suche ist nicht mehr das rohe Anfrage-Embedding, sondern eine Mischung aus Frage und Novas aktivierten Zielen:

```
e_nova = e_anfrage × (1 − faktor) + Σ(e_ziel × aktivierungs_staerke) × faktor
```

`faktor` ist ein Wert **pro Turn** aus `CLUSTER_GRAVITATION_FAKTOR` (`ei/dreischicht.py`, 14 Cluster, 0.05 bis 0.30); `aktivierungs_staerke` ist ein Wert **pro Ziel** (`similarity × motivation`). Die Rechnung steht in `ei/gravitation.py:wahrnehmung_verschieben()`, der Enricher ruft sie nur auf.

~~**Nur die LZG-Suche bekommt den verschobenen Schlüssel.**~~ **Seit dem 04.08.2026 bekommen ihn beide Gedächtnisschichten.** Die Verschiebung wird einmal je Turn gerechnet, vor beiden Suchen, und KZG wie LZG suchen mit demselben Vektor.

> **Für die frühere Grenze gab es keine Begründung.** Weder das Konzept noch der einführende Commit nannten einen Grund; der Commit beschreibt nur den Umfang („wires the shift into the LZG path"). KZG und LZG sind dieselbe Art Speicher mit verschiedenen Zeithorizonten — Nova hört nicht mit zwei Ohren. Die Anpassung wurde beim nachträglichen Einbau der Gravitation schlicht übersehen.

**Was ausdrücklich nicht mitzieht:** Ziel-Aktivierung und emotionale Gravitation rechnen weiter gegen das rohe Embedding — die Aktivierung wäre sonst ihre eigene Eingabe. Aus demselben Grund steht der Ziele-Block seit P10 **vor** der Memory-Suche statt danach. Das ist keine Ausnahme aus Vorsicht, sondern eine Sperre gegen eine Rückkopplung.

**Der Imperativ-Override gilt damit für beide Schichten.** Bei der Intention `anweisung` sucht auch das Kurzzeitgedächtnis roh — sonst legte Nova zwar keinen Bratwurst-Termin aus dem Langzeitgedächtnis an, wohl aber aus dem Kurzzeitgedächtnis.

**Sieben Ausgänge, jeder benannt.** Das Feld `herkunft` im Pipeline-Log (`quelle="wahrnehmungs_gravitation"`) trennt sie: `verschoben`, `anweisung` (Imperativ-Override), `keine_ziele`, `kein_ziel_embedding`, `cluster_unbekannt`, `dimension_ungleich`, `verworfen_ausser_spanne` — dazu **`keine_gedaechtnis_suche`** für den Durchlauf ohne jede Suche. Jeder Ausgang außer dem ersten sucht mit dem rohen Embedding weiter; ein Durchlauf ohne Eintrag gibt es nicht.

> **Der Marker hieß bis zum 04.08.2026 `keine_lzg_suche`.** Umbenannt, weil seine Bedeutung mit dem Umfang gewandert ist: Solange nur das LZG den verschobenen Schlüssel bekam, war „keine LZG-Suche" dasselbe wie „nichts zu verschieben". Denselben String weiterzuverwenden hieße, Einträge von vorher und nachher gleich aussehen zu lassen, obwohl sie Verschiedenes bedeuten. **Wer Log-Einträge über den 04.08. hinweg vergleicht, muss beide Schreibweisen kennen.**

**Die Summe wird nicht normiert.** Mehrere Ziele verstärken sich, und der Ziel-Anteil kann den Anfrage-Anteil überwiegen. Ein Ergebnis, dessen Cosinus zum rohen Embedding nicht in (0.0, 1.0] liegt, wird deshalb gemeldet und **verworfen, nicht gekappt** — es zeigt von der Frage weg und ist keine Färbung mehr.

**Gemessen am 02.08.2026:** Bei sieben aktiven Zielen des Paares lagen die Aktivierungs-Stärken zwischen 0.102 und 0.212 gegen eine Schwelle von 0.4 — kein Ziel aktivierte. Ein zweiter Turn nahe an einem langfristigen Ziel erreichte 0.631; die Verschiebung im Cluster `schlachtfeld` (Faktor 0.05) drehte den Suchschlüssel um **1,14°** (Cosinus 0.9998). Aktivierungsschwelle und Verschiebungswirkung ziehen gegeneinander: Ein Ziel aktiviert nur, wenn es der Frage schon ähnlich ist, und in Richtung eines fast parallelen Vektors zu verschieben dreht kaum. Ob der Mechanismus die Trefferliste je ändert, ist **nicht gemessen** (`novaberg-fundliste.md`, 02.08.).

**Korrektur zur Historie (Chat 107):** Die frühere Aussage, das Anker-Retrieval „findet Anker", war faktisch falsch. Der ivfflat-Index auf `lzg_knoten` (lists=100 bei ~300 Zeilen, probes=1) durchsuchte eine einzige Liste und lieferte pro Query drei Zufallstreffer (IVFFLAT-RECALL-KOLLAPS, bugs.md); im casing-blinden Embedding-Raum lag bei Grundrauschen 0.74 praktisch jeder Zufallstreffer über der alten 0.50-Schwelle — die Treffer sahen deshalb plausibel aus. Die ivfflat-Indizes sind entfernt (Commit `0fd54a1`); bis ~10k Zeilen läuft das Retrieval exakt per Seq-Scan.

### 3.4 Charakter-Hash (nicht mehr geladen, seit Phase 2)

Der Enricher lädt den Charakter-Hash nicht mehr selbst. Seit Chat 89 (PFAD2-PERZEPTION-FIX Phase 2) ist das Laden in den `db_zugriff`-Node gewandert, der am CG-Entry läuft. Der Enricher konsumiert `state["external"].character` direkt (nur für die Hash-Formatierung im `memory_entries`-Akkumulator; im HG bleibt `external.character` leer und der Eintrag entfällt).

→ Lade-Pfad: `novaberg-node-db-zugriff.md`
→ Ablage-Konvention: `novaberg-personality.md`

### 3.5 Rohdaten für den EI-Calc (seit Chat 59, vereinfacht in Phase 3)

Der Enricher schreibt eine Brücke in den State, die der nachfolgende EI-Calc-Node konsumiert:

| Feld | Quelle | Inhalt |
|------|--------|--------|
| `raw_turns` | `session_turns_retrieve()` | Ungefilterte Session-Turns für Verlauf, Vektor, Stilanalyse |

Der frühere Brücken-Eintrag `char_hash_dict` ist mit Phase 3 entfallen — EI-Calc baut sich das Dict bei Bedarf inline aus `state["external"].character` (`ei_calc.py:100-106`).

Die eigentliche Berechnung (Verlauf, Vektor, EI-Arousal, Modus-/Stil-Plausibilität, Nova-Empathie) passiert im EI-Calc-Node.

→ Vollständige Beschreibung aller EI-Berechnungen: `novaberg-node-ei-calc.md`
→ Fensterbreiten (`EMOTION_MAX_TURNS`, `EMOTION_VEKTOR_TURNS`, `STIL_ANALYSE_TURNS`): dort im Detail

---

## 4. State-Felder

### Gelesen

| State-Quelle | Typ | Beschreibung |
|---|---|---|
| `user_id` | str | Gedächtnis-Partition |
| `character_id` | str | Paar-Partition (seit Chat 60) |
| `user_prompt` | str | Für Embedding-Erzeugung |
| `ei_calc_rolle` | str | Dispatcher-Switch (`"user"` → HG, `"character"` → CG; Default: `"character"`) |
| `graph_rolle` | str | Quelle im `pipeline_log` *(seit Chat 110)*: `"human"`→`user`, `"character"`→`character`, `"agent"`→`agent`. Vorher aus `ei_calc_rolle` abgeleitet — der AgentGraph war dadurch vom CharacterGraph nicht zu trennen |
| `turn_id` | str | Pipeline-Log-Korrelation (Chat 88 P1.1) |
| `state["external"].character` | Character | Charakter-Hash-Formatierung für `memory_entries` (nur CG, im HG leer) |

### Geschrieben

**HumanGraph (`_enrich_human`):**

| State-Ziel | Typ | Bewusst flach? | Beschreibung |
|---|---|---|---|
| `state["raw_turns"]` | list[dict] | n.a. (Brücken-Datenstruktur, kein Personality-Wert) | Ungefilterte Session-Turns |
| `state["user_intentionen"]` | list[str] | n.a. | Letzte Intentionen aus User-Turn |
| `state["prompt_embedding"]` | list[float] | n.a. | 768-dim Vektor aus `user_prompt` |
| `state["aktivierte_ziele"]` | list[dict] | n.a. | Ziele über Gravitations-Schwelle. Feld je Ziel seit Chat 126 `aktivierungs_staerke` (vorher `gravitation`); das Ziel-Embedding bleibt **draußen** — es trägt die Verschiebung und hat im State keinen Leser |
| `state["gravitationsterm"]` | float | n.a. | Aggregierter Drive-Term |

**CharacterGraph (`_enrich_character`):**

| State-Ziel | Typ | Bewusst flach? | Beschreibung |
|---|---|---|---|
| `state["raw_turns"]` | list[dict] | n.a. | Ungefilterte Session-Turns |
| `state["session_turns"]` | list[dict] | n.a. | Shadow-Impulse gefiltert |
| `state["user_intentionen"]` | list[str] | n.a. | Letzte Intentionen aus User-Turn |
| `state["prompt_embedding"]` | list[float] | n.a. | 768-dim Vektor |
| `state["aktivierte_ziele"]` | list[dict] | n.a. | Ziele über Schwelle, Feld `aktivierungs_staerke` (siehe HG-Tabelle) |
| `state["gravitationsterm"]` | float | n.a. | Aggregierter Drive-Term |
| `state["emotionale_gravitationspunkte"]` | list[dict] | n.a. | Scan ueber **KZG und LZG** auf Eintraege mit Emotion (`ei/gravitation.py`). ~~hoch-arousal~~ — **einen Arousal-Filter gibt es nicht:** §5.7 des Konzepts verlangt „Emotion ≠ neutral und Arousal ueber Schwelle", der Code liest `arousal`, fuehrt es mit und loggt es, vergleicht es aber nie. Offener Punkt, kein Defekt (Backlog-Epic). Verbraucher: Node `emotionale_gravitation` |
| `state["memory_entries"]` | list[ContextEntry] | n.a. | Akkumulierte Memory-Quellen für den Reducer |
| `state["lzg_resonanz"]` | dict | n.a. | Spreading-Lesepfad (§3.3): Kontext-Rahmen (Anker-Anzahl, Sprung-Tiefe, Cluster, Nova-Sektor) + Erinnerungen mit Pfad; Transport zum Formatter via Reducer-Durchreiche |

**Phase 3 entfernt:** `char_hash_dict`, `user_emotion`, `charakter_anweisungen`, `direktiven`, `nova_kern`, `nova_adaptiv`, `nova_beziehung`, `nova_intentionen`, `nova_emotions`. Diese Felder werden vom Enricher nicht mehr geschrieben. Charakter-/Identitäts-Daten liegen in den Personality-Klassen (`state["external"].character`, `state["internal"].character`/`identities`/`directives`), befüllt vom `db_zugriff`-Node am CG-Eingang.

---

## 5. Besonderheiten

**Turn 0 — weiterhin relevant (jetzt im EI-Calc):** Der Turn-0-Trick (Perzeptionsergebnis als virtueller neuester Turn) lebt weiter — nur im EI-Calc statt im Enricher. Hintergrund: Die Salienz annotiert Session-Turns erst *nach* dem Responder (und seit Chat 59 asynchron). Deshalb fügt EI-Calc die Perzeptionswerte als Turn 0 in die Verlaufsberechnung ein, damit der Emotions-Vektor Richtungswechsel sofort erkennt.

> **Entdeckt in Chat 8:** Edge Case „Alles scheiße!" nach positiver Phase → Vektor zeigte `stabilisierung` statt `absturz`. Ursache: Aktuelle Emotion war für die EI-Berechnung unsichtbar. Fix: Turn 0 aus Perzeption.

**Kein LLM-Call:** Der Enricher ist bewusst LLM-frei. Alle Operationen sind deterministisch: Datenbankabfragen, Embedding-Erzeugung (via Ollama, aber das ist kein generativer Call). Das macht ihn schnell, reproduzierbar und testbar.

**Reiner I/O-Node (seit Chat 59):** Keine Python-Berechnungen mehr — alles was rechnet, steht im EI-Calc. Der Enricher lädt Session-Turns aus Redis, erzeugt Embeddings via Ollama-Embed-Modell, liest aktivierte Ziele aus Postgres (`ziele`-Tabelle). Punkt.

**Das gilt auch nach P10.** Die Wahrnehmungs-Gravitation (§3.3a) rechnet in `ei/gravitation.py`; im Node steht der Aufruf und die Entscheidung, welchen Schlüssel die Suche bekommt.

**Der GV-Cluster kommt immer aus dem Vorturn (Chat 126).** Der `gv_node` läuft in **beiden** Graphen nach dem Enricher (§2) — der Cluster des aktuellen Turns existiert zum Zeitpunkt der Suche noch nicht. `_vorturn_cluster_lesen()` holt ihn aus `gv:detail:{user_id}:{character_id}` in Redis, mit `paradox` als Rückfall. Das Synapsen-Konzept §8.5.2 behauptete für den CharacterGraph das Gegenteil; die Kantenliste in `graph/character_graph.py` widerlegt es, und beide Messturns vom 02.08. lasen den Cluster aus Redis.

**Ziele je Beziehung (seit Chat 125):** Der Enricher liest die Ziele des Paares, nicht alle Ziele Novas. Beide Pfade — `_enrich_human` und `_enrich_character` — reichen ihr Turn-Paar an `ziel_paar_bestimmen()` weiter, weil sie es in verschiedener Reihenfolge führen: `(mensch, nova)` gegen `(nova, mensch)`. Wer das Turn-Paar direkt als Ziel-Paar verwendet, liest auf einem der beiden Pfade nichts.

**Plugin-Erweiterbarkeit:** Neue Manager können Kontext liefern ohne den Enricher zu ändern. Der Hook `manager.enrich_entries(state, postgres_url)` ist das einzige Interface.

---

→ Konzept: `novaberg-graph.md` — Graph-Konzept
→ Architektur: `novaberg-graph.md` — Graph-Architektur
→ Emotionale Intelligenz: `novaberg-ei.md` — EI-Konzept, `novaberg-node-perception.md` — Perzeption & Emotions-Vektoren
→ EI-Berechnung: `novaberg-node-ei-calc.md` — User-/Character-Pfad, Empathie-Switch
→ EI-Persist: `novaberg-node-ei-calc-persist.md` — Konsolidiert `internal.emotion` und persistiert am CG-Ausgang (Chat 89)
→ DB-Zugriff: `novaberg-node-db-zugriff.md` — Lädt `internal.emotion` und `external.character` am CG-Eingang (Chat 89)
→ Personality-Klassen: `novaberg-personality.md` — Character, Emotion, InternalPersonality
→ Plutchik-Emotionsmodell: `novaberg-ei-plutchik.md`
→ Lesson Timing-Bug: `novaberg-node-perception.md` (Turn-0-Fix)
→ Lesson Session-Kontamination: `novaberg-pixie_l_kontamination.md`
→ Profil-Pipeline (CAT + Destillation): `novaberg-ei-character-profiles.md`

---

### Feature-Scoring für Sprachstil (seit Chat 20, jetzt im EI-Calc)

Die regelbasierte Stil-Erkennung wurde im Zuge von AP2 (Chat 59) aus dem Enricher entfernt und läuft jetzt im EI-Calc-Node. Die Funktionen `_turn_features_bewerten()`, `_sprach_stil_erkennen()` und `_hash_stil_extrahieren()` leben in `ei/berechnung.py`.

→ Details: `novaberg-node-ei-calc.md`

### Novas eigener Hash (verschoben nach db_zugriff)

Seit Phase 2 (Chat 89) lädt der `db_zugriff`-Node Novas Charakter-Hash und schreibt ihn nach `state["internal"].character`. Der Enricher konsumiert diese Daten nicht direkt — der Responder liest sie für die `[IDENTITAET]`-Block-Konstruktion.

→ `novaberg-node-db-zugriff.md`

---

## Befunde aus dem Betrieb — nachgetragen am 20.08.2026

Aus `novaberg-fundliste.md` hierher gezogen: Aussagen ueber den **Zustand** dieses Gegenstands, die dort als rohe Funde standen und in kein Defekt- oder Vorhabenregister gehoeren. Der Wortlaut ist unveraendert, das Datum steht an jedem Befund — geprueft ist keiner von ihnen gegen den heutigen Code.

- **19.08.2026** — **Der Vorcheck `has_wissen` des Enrichers ist gröber als der Lesepfad, den er ankündigt — und die Lücke ist mit Konvention 4 gewachsen.** `graph/nodes/enricher.py` prüft `EXISTS(… WHERE user_id AND character_id AND aktiv)` und loggt daraufhin `Bibliothek=ja`. Der Lesepfad filtert zusätzlich auf **`typ='wissen'`** und braucht seit dem Umbau einen **Themenvektor** (JOIN auf `autonomous_wissen_thema`). `Bibliothek=ja` heißt damit nicht *„sie kann antworten"*, sondern nur *„es gibt irgendeine aktive Zeile dieses Paares"* — auch wenn alle davon vom Typ `bericht` sind. **Gemessen an einem echten Turn** (19:49 UTC): `Bibliothek=ja`, null Treffer, weil zum gefragten Thema nur `bericht`-Einträge existierten; der beste Kandidat lag bei 0,3918 und wurde von der Schwelle korrekt abgewiesen. **Kein Defekt** — der Vorcheck entscheidet nur, ob die Verschiebung gerechnet wird, und darf grob sein. Aber die **Logzeile** liest sich als Zusage, die sie nicht ist, und genau daran habe ich beim Prüfen des Umbaus eine falsche Hypothese aufgehängt.

- **18.08.2026** — **Zwei Register beschreiben die Lesequellen des Enrichers und kennen die Bibliothek nicht.** Beim Nachzug der Enricher-Quelle gesucht und beidseitig gezählt: `novaberg-graph-rechenkette.md` führt **34 Rechensysteme** des Charakter-Pfads, darunter S10 (KZG-Abruf) und S11 (LZG-Spreading) — **der `WissenManager` steht nicht darin**, obwohl er seit dem 04.08.2026 in jedem Turn eine Vektorsuche mit Schwelle und Kappung fährt und damit exakt die Sorte ist, die S10/S11 beschreiben. Dasselbe zweimal auf der Prompt-Seite. In `novaberg-pattern-prompt-schema.md`: Die Blockmatrix in §3 führt `GEDAECHTNIS` in der Responder-Spalte, obwohl der Responder ihn **seit dem 14.08.2026 nicht mehr sieht** — die Trennung von Verfasser und Responder ist an dieser Tabelle vorbeigegangen, und der Verfasser hat dort bis heute keine Spalte. Und in `novaberg-node-responder.md` führt die nummerierte Liste der neun Prompt-Blöcke `[GEDAECHTNIS]` und `[WEB-RECHERCHE]` als Blöcke **des Responders** — Stand 17.08.2026, also drei Tage nach der Trennung. **Beide Lücken sind älter als der heutige Umbau** und wurden nur sichtbar, weil er dieselben Register anfasste; nicht im Vorbeigehen repariert.
