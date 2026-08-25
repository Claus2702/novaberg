# Novaberg — Backlog: Wissen — Bibliothek, Dateien, Notizen, Timeline, Fakten

**Inhalt:** die offene und abgeschlossene Arbeit dieses Gegenstands, 71 Eintraege.
**Findemittel ueber alle Gegenstaende:** [`novaberg-backlog-index.md`](novaberg-backlog-index.md) — es traegt auch die Rangordnung.

**Die Abschnittsueberschriften stammen aus dem ungeteilten Backlog** und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

| Gegenstand | Datei | Eintraege |
|---|---|---|
| Gedaechtnis | [`novaberg-backlog-gedaechtnis.md`](novaberg-backlog-gedaechtnis.md) | 76 |
| Hintergrund | [`novaberg-backlog-hintergrund.md`](novaberg-backlog-hintergrund.md) | 66 |
| Charakter | [`novaberg-backlog-charakter.md`](novaberg-backlog-charakter.md) | 66 |
| Antwortpfad | [`novaberg-backlog-antwortpfad.md`](novaberg-backlog-antwortpfad.md) | 46 |
| Wissen | [`novaberg-backlog-wissen.md`](novaberg-backlog-wissen.md) | 71 |
| Bauart | [`novaberg-backlog-bauart.md`](novaberg-backlog-bauart.md) | 96 |

---

## DATEIINDEX-GRAPHKANAL — Entitäten aus dem Dateiinhalt statt aus den Stichwörtern (23.08.2026)

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Ein Schreiber, der Entitaeten aus dem Dateiinhalt zieht, ist nicht gebaut; die Nulllinien des Eintrags (18 bzw. 37 Dateien) stehen unveraendert als Vergleichsmass.

**Anlass:** `DATEIINDEX-SPALTEN-OHNE-SCHREIBER` ist am 23.08.2026 durch eine **Statusmarke** geschlossen worden, nicht durch einen Schreiber — weil die Messung gegen den naheliegenden Schreiber entschied. Dieser Eintrag hält fest, was ein tragfähiger wäre.

**Was gemessen wurde** (`labor/2026-08-23_dateiindex_graphkanal.sql`, 175 Indexzeilen gegen die 690 Entitäten, die der Auflöser für dieses Paar sieht): Die je Datei erhobenen Stichwörter gegen den Entitätenbestand aufzulösen ergibt aus 843 verschiedenen Stichwörtern **10 Treffer**. 122 Dateien bekämen eine Kante, **116 davon zur Entität `Novaberg` — 95,1 %.** Ohne sie 18 von 175. Eine Kante an zwei Dritteln des Bestands sortiert nicht.

**Was fertig wäre:**

1. **Erhebung aus dem Inhalt, nicht aus den Stichwörtern.** Benannte Personen, Orte, Systeme im Dateitext — der Indexlauf liest die Datei ohnehin und ruft je Datei ein Modell.
2. **Auflösung ohne Anlegen.** Das ist **kein eigener Bau**: `resolve_batch` schreibt nichts, angelegt wird in drei Zeilen des KZG-Pfads (`agents/kzg/magnete.py`, `if ent.ist_neu and ist_referenz`). Der Dateiweg lässt sie weg. Zu beachten ist etwas anderes: `find_by_name` ist kein reines `SELECT`, sondern setzt `last_touched` — ein Indexlauf über 175 Dateien berührt damit den Entitätenbestand.
3. **Die Nulllinie hängt an ihrer Vergleichsstufe und muss sie mitnennen.** Exakter Namensvergleich (die Stufe, die `find_by_name` bildet): **18** Dateien mit einer anderen Kante als `Novaberg`. Wortgrenze: 37. Der Novaberg-Anteil bleibt über beide Stufen bei 91 bis 95 % — ein Schreiber, der ihn nicht deutlich drückt, ist nicht gebaut, sondern verschoben.

**Woran der Abschluss erkennbar wäre:** Die **Verteilung**, nicht die Menge — keine einzelne Entität trägt mehr als ein Drittel der verknüpften Dateien. Die Zahl der verknüpften Dateien wird gegen die Nulllinie **derselben Vergleichsstufe** gehalten (exakt: 18, Wortgrenze: 37); eine Zahl ohne ihre Stufe ist hier keine Aussage.

**Nicht Teil davon: `timeline_id`.** Die Spalte scheitert am Gegenstand und nicht an der Ausbeute — eine Datei hat keinen Ereigniszeitpunkt, und der Vorrang des Neueren steckt in `geaendert_am`. Sie bleibt ⬜.

**Band:** noch nicht zugeordnet — der Kanal ist eine Verbesserung der Auffindbarkeit, kein Defekt.

---


## Block 19.08.2026 — die Rollen eines Wissen-Silos

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Wissen**. Ueberschrift und Text stehen in jeder empfangenden Datei.

**Der Anlass ist eine Matrix, keine Wunschliste.** Am 19.08.2026 gezählt trägt von neun Silos **genau eines alle drei Rollen** (Timeline: Quelle, Zettel, Werkzeug). Das Web ist der Spiegelfall — Werkzeug ohne Quelle, weil es keine sein kann. Und das am schlechtesten angebundene Silo ist ihr **eigenes erarbeitetes Wissen**: eine Rolle von dreien.

| Kennung | Was offen ist | Band |
|---|---|---|
| ~~`WISSEN-OHNE-ZETTEL`~~ **— geschlossen am 19.08.2026.** Zettel (`plugins/wissen_manager/manager.py::router_prompt`) und Dienst (`agents/wissen/`) stehen, 26 Zeugen; **zwei echte Turns** routen dorthin (12:41 und 12:43 UTC), einer in den vierten Ausgang, einer abgeschlossen. Die Abfrage ist **eine** für beide Eingänge (§6a.1, `AutonomousWissenRepository.suchen`); der Eingang wählt nur die Tiefe. **Als Rest benannt:** die Tiefe bleibt Stufe 1 — Thema und Zusammenfassung, nicht der Wortlaut (`WIS-8-STUFE-2`), und der Dienst sagt es in seiner `grenze`. **Und der vierte Ausgang hat im ersten Lauf einen Befund geliefert:** die Schwelle trennt an diesem Korpus nicht (siehe `WIS-SCHWELLE-MESSEN`). Ursprünglicher Wortlaut: **Ihre Bibliothek ist angebunden wie ihr Gedächtnis, nicht wie eine Quelle.** `wissen_manager` trägt `immer_aktiv` und **keinen** `router_prompt` — sie fließt bei jedem Turn in den Kontext, und niemand kann sie **bestellen**: weder der Mensch (*„Was hast du selbst dazu erarbeitet?"*) noch sie selbst. Für die freigegebenen Dateien wurde der Zettel am 18.08. gebaut, für ihr eigenes Wissen nicht. **Was fertig wäre:** ein Aushang nach `novaberg-convention-nmcp.md` §3 mit Negativfällen gegen **drei** Nachbarn — `dateien` (fremde Unterlagen), `kzg` (Erinnerung an ein Gespräch), `recherche` (was sie noch nicht weiß) —, ein Dienst dahinter, der den vierten Ausgang bedient, und ein echter Turn, der eine Frage nach ihrem eigenen Wissen dorthin routet. **Vorbedingung erfüllt:** §6a der Konvention steht seit dem 19.08. und ist vor diesem Bau geschrieben. | ungebändigt |
| `SILO-OHNE-WERKZEUG` | **Sechs Silos sind bestellbar und keines davon greifbar.** Sie kann `web_search`, `web_fetch`, `memory_search`, `timeline_check` und `timeline_search` mitten im Denken ziehen — für Dateien, ihr Wissen, Notizen, Fakten, Direktiven und Identität gibt es kein Werkzeug. **Der Unterschied ist nicht Bequemlichkeit, sondern wer entscheidet:** Bestellbar heißt, der Empfang wählt anhand der Äußerung; greifbar heißt, sie beschließt es selbst. **Was fertig wäre:** je Silo ein Werkzeug **oder** eine Begründung an seinem Aushang, warum es keines gibt — die Regeln dafür stehen in §6a.1 bis §6a.3, insbesondere die benannte Faltung der vier Ausgänge in Text. **Reihenfolge:** `wissen` und `dateien` zuerst, weil sie die Quellen einer ausdrücklichen Suche sind. | [WIS] ungebändigt — ⬜ **offen — gegen HEAD `f31b3ab` geprueft am 25.08.2026.** `graph/nodes/thinker.py` fuehrt weiterhin nur `timeline_search`, `timeline_check`, `memory_search`, `web_search` und `web_fetch`. Fuer Dateien, Wissen, Notizen, Fakten, Direktiven und Identitaet gibt es kein Werkzeug. |

---


## Block 19.08.2026 — der dritte Konsument der Bibliothek

| Kennung | Was offen ist | Band |
|---|---|---|
| ~~`WIS-ENRICHER-UNGEMESSEN`~~ | [WIS] **✅ Nachgemessen am 19.08.2026 — der Weg ist besser geworden, nicht schlechter: 22/30 auf Rang 1 gegen 1/30, im Betrieb 3 Treffer bei Kosinus 0,730–0,629.** Ursprünglicher Befund: **Der Enricher-Weg wurde auf Themenvektoren und Schwelle 0,50 mitgestellt, ohne dass seine Anfrageart je gemessen wurde.** Er fragt mit dem **Gesprächsvektor** (`verschiebung.vektor`), nicht mit einer Frage und nicht mit einem Kontexttext — eine dritte Größe. Beide neuen Einstellungen sind an der **Frage**-Anfrage kalibriert. Aus dem Betriebslog über rund 32 Stunden vor dem Umbau: 5 Treffer bei Kosinus 0,402 bis 0,555; der erste Turn danach lieferte null. **Was fertig wäre:** dieselbe Methode wie an den anderen beiden Zugriffen — echte Gesprächsvektoren aus dem Betrieb, bekannte richtige Antwort, Anteil auf Rang 1, gegen beide Ziele. Erst danach ist entscheidbar, ob dieser Weg eine eigene Schwelle braucht oder ein eigenes Ziel. **Nicht im Vorbeigehen ändern:** Eine dritte Schwelle ohne Messung wäre genau der Fehler, den die Messung an den ersten beiden gerade verhindert hat.|

**Ergebnis:** Eine eigene Schwelle braucht dieser Weg **nicht** — die Verschiebung kostet bei dieser Art Frage 0,0000, weil kein Ziel aktiviert wird (stärkstes von 7: `similarity × motivation` = 0,3903 × 0,8 = 0,312, unter der Aktivierungsschwelle). Er verhält sich damit wie die Bestellung, für die 0,50 kalibriert ist. **Was offen bleibt:** Ob bei Äußerungen, die Novas Ziele *doch* aktivieren, ein Verlust entsteht — das ist eine andere Frage und braucht andere Fragen. | ungebändigt |

---


## Block 19.08.2026 — ein Vektor je Gegenstand

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Wissen**. Ueberschrift und Text stehen in jeder empfangenden Datei.

**Entschieden am 19.08.2026, festgehalten als Konvention 4** (`novaberg-convention-embedding.md` §5): Ein Vektor repräsentiert genau einen Gegenstand. Über sieben Vektorspalten gezählt folgen **fünf** der Regel, bevor sie geschrieben war — sie ist die Hausform. Zwei weichen ab, und es sind die jüngsten Speicher.

| Kennung | Was offen ist | Band |
|---|---|---|
| `BIBLIOTHEK-BLIND-AUF-INHALTSHOEHE` | **Die Bibliothek ist auf Themenhöhe abrufbar und auf Inhaltshöhe blind — und der Enricher fragt immer auf Inhaltshöhe.** Gemessen am 20.08.2026 gegen 287 Ausarbeitungen: 10 Sonden, aus dem **Dateiinhalt** formuliert, treffen ihr Ziel in **1 von 10** Fällen auf Rang 1; die Schwelle 0,50 schneidet **9 von 10** ab. Die Kontrolle stellt die Diagnose — dieselbe Zielausarbeitung, zweimal gefragt: auf Themenhöhe Rang 1 bei Kosinus 0,7375 / 0,5751 / 0,5559, auf Inhaltshöhe Rang 8 / 142 / 63 bei 0,3447 / 0,1768 / 0,2491. **Nicht die Schwelle ist falsch, sondern ihre Paarung:** Kalibriert wurde sie am 19.08. an Themenfragen (92 % Rang 1) — der bestellbare Weg. Der Enricher sucht mit dem Vektor des **Turns**, und ein Turn ist fast immer eine inhaltliche Äußerung. **Das erklärt den Betrieb:** 2 echte Treffer in 142 beantworteten Nutzerturns. **Ausdrücklich nicht mitzumachen:** an der Zahl drehen. Sie hält die fremden Fragen sauber draußen (0 von 10 durchgelassen), und die Verteilungen überlappen — der beste Fremdtreffer 0,3577 liegt über fünf der zehn Ziele; keine Zahl trennt beide Seiten. **Was fertig wäre:** ein Vergleichsgegenstand auf Inhaltshöhe — Zusammenfassung oder Inhaltsblöcke auffindbar gemacht — und dieselben 20 Sonden erneut gefahren. **Nulllinie: Rang 1 in 1 von 10, fremd max 0,3577.** **Vor dem Bau zu bedenken:** Der Gegenbefund vom selben Tag steht — `MAX` über viele Vektoren je Eintrag hebt auch das Rauschen (`EMBED-LISTE-DATEIENINDEX`, gemessen und verworfen). Messschrieb: `2026-08-20_bibliotheksschwelle_ergebnis.md` | [WIS] ungebändigt — ⬜ **offen** — nachgesehen am 25.08.2026. Der Enricher erreicht die Inhaltshoehe weiterhin nicht. |
| `EMBED-LISTE-AUTONOMES-WISSEN` | **Die Bibliothek bettet eine Themenliste als einen Vektor ein — und trifft damit nicht.** `autonomous_wissen.thema` trägt Ø **4,37** Themen je Feld (max 17), **558 von 559** Feldern mehr als eins. Zusätzlich stammt der Vektor gar nicht aus diesem Feld, sondern aus dem **Destillat** (`agents/recherche/agent.py`, siehe Fundliste). **Gemessen:** Bei einer Frage nach *einem* Thema liegt die richtige Antwort in **6 von 40** Fällen auf Rang 1, Kosinus-Median **0,2821** — unterhalb der eigenen Schwelle von 0,40, die Antwort wird also im Regelfall verworfen. Mit einem Vektor je Thema: 31 von 40 und Median 0,7425. **Was fertig wäre:** je Thema eine Zeile mit eigenem Vektor, die Lesepfade von `AutonomousWissenRepository.suchen` darauf umgestellt, und ein echter Turn, der eine Ausarbeitung über ein einzelnes ihrer Themen findet. **Nicht vergessen:** Der Rückweg fragt mit Ø 713 Zeichen (n=924) und braucht daneben weiterhin ein Ziel seiner Größenordnung — ein Themenvektor ersetzt keinen Inhaltsvektor. **Ist DDL und eine Migration von 249 Zeilen** (`F-DDL-1`) | [WIS] ungebändigt — ⬜ **offen, Bestand gewachsen — am Bestand gemessen am 25.08.2026.** ⌀ **4,69** Themen je Feld statt 4,37, und **886 von 890** Feldern tragen mehr als eins statt 558 von 559. Der Verstoss ist derselbe, die Menge groesser. |
| `EMBED-LISTE-DATEIENINDEX` | **Dritte Stelle derselben Klasse, und diesmal ist die Wirkung gemessen.** `embed_text_bauen` (`agents/dateien_index/indizieren.py`) bildet `themen_embedding` aus `thema` **plus rund acht Stichwörtern** — ein Schwerpunkt aus neun Gegenständen, wo gesucht wird nach **einem**. **Gemessen am 20.08.2026 über 24 Sonden gegen 174 Zeilen:** richtige Datei auf Rang 1 in **8 von 12**, in den ersten drei in 10 von 12. Der teure Fall ist der Rest: Die Sonde nach der Nabe des Charakter-Rads trifft ihr Ziel mit 0,3381 — **über** dem Boden — und bekommt es nie zu sehen, weil drei thematisch benachbarte Dateien davor liegen (0,5001 · 0,4495 · 0,3857) und die Kappung bei drei steht. Der scharfe Kanal fängt es nicht auf. **Keine Schwelle ändert daran etwas** — das ist der Unterschied zwischen einer Rangfolge- und einer Schwellenfrage, und er ist an dieser Messung ablesbar. **Der Präzedenzfall ist bezahlt:** Dieselbe Bauart hob an der Bibliothek den Anteil richtiger Antworten auf Rang 1 von 15 % auf 92 % (Konvention 4, `F-EMBED-2`). **Was fertig wäre:** ein Vektor je Stichwort/Thema in eigener Zeile, beide Schreibwege angeschlossen, und dieselben 24 Sonden erneut gefahren — die Rang-1-Quote von 8/12 ist die Nulllinie, gegen die zu messen ist. → ⊘ **Am 20.08.2026 gebaut, gemessen und zurückgebaut.** Tabelle, Schreibweg, drei Lesewege und 1456 nachgebettete Gegenstandsvektoren über 174 Zeilen standen; dieselben 24 Sonden ergaben **keine Verbesserung**: Rang 1 unverändert 8/12, in den ersten drei **9/12 statt 10/12**, und die Trennung wird schlechter — der beste Fremdtreffer steigt von 0,3052 auf 0,4008, über dem Boden liegen statt 1 Zeile **20**. Ein dritter Arm (nur der Themensatz, ohne Stichwörter) trennt die beiden Änderungen und liegt gleichauf mit dem zweiten: 8/12 und 9/12. **Warum der Präzedenzfall nicht trägt:** In der Bibliothek war das Feld eine Aufzählung *verschiedener* Gegenstände; hier beschreiben Thema und Stichwörter **einen** — die Datei. Ein Schwerpunkt aus Facetten eines Dings zeigt weiterhin auf dieses Ding. Und MAX über 1456 Vektoren ist eine Extremwertstatistik: Zur Sonde nach der Nabe des Charakter-Rads trug das Stichwort `CharacterGraph` den besten Treffer. **`F-EMBED-2` ist damit nicht widerlegt, die Analogie ist es** — dieser Fall ist weder Aufzählung noch Aussage, sondern die Beschreibung **eines** Gegenstands aus mehreren Blickwinkeln. Messschrieb: `2026-08-20_gegenstandsvektoren_ergebnis.md`. ~~**Was offen bleibt und jetzt ohne Kandidaten dasteht:** warum die richtige Datei nur in 8 von 12 Fällen auf Rang 1 steht~~ → **Am 21.08.2026 diagnostiziert, und die Antwort liegt nicht an der Formel.** Ein zweiter Kandidat wurde dabei verbraucht: Die **Präambel** des Themensatzes (66 von 174 Sätzen beginnen mit einer) ist entfernt worden — Rang 1 bleibt 8/12, Top 3 bleibt 10/12, die drei Fehlschläge bewegen sich um je einen Platz. **Zwei der vier Fehlschläge sind Sollurteil-Fehler:** Bei der Frage nach dem Verfall eines Kurzzeit-Eintrags steht `kzg-salienz.md` über dem Ziel, und ihr Themensatz beschreibt genau das Gefragte; bei der Frage nach der Führung im Gespräch steht das Moduldokument über seinem Konzept. Der Bestand führt zu mehreren Fragen **mehr als eine richtige Datei**, und die Sonde erklärt genau eine dazu. **Bei den zwei echten Fehlschlägen kommt der tragende Begriff der Frage im Index nicht vor:** `Nabe` steht 2× in der Datei und weder im Themensatz noch in den Stichwörtern, `Führung` 6× in der Datei und in den Stichwörtern nur als Bezeichner `fuehrung_messen`. **Der Index trägt neun Gegenstände je Datei; was nicht hineinfällt, ist für beide Kanäle unsichtbar** — und keine Änderung an der Form des Vektors heilt das. **Vor jedem Bau gemessen:** Der beste *Block* der Zieldatei erreicht 0,4617 gegen 0,3381 und 0,3926 gegen 0,2189. Das belegt Kopf, nicht Erfolg — bei einer Blockebene stiegen auch die Konkurrenten, und genau daran ist der Umbau vom 20.08. gescheitert. Messschrieb: `2026-08-21_dateiindex_rangfolge_ergebnis.md`. | [WIS] ⊘ verworfen, Ursache diagnostiziert |
| `EMBED-RUECKWEG-UNGEMESSEN` | [WIS] **Der zweite Konsument der Bibliotheksspalte ist nie gemessen worden.** `agents/wissen_rueckweg/zuordnung.kandidaten_laden` vergleicht `auftrag['kontext']` gegen `themen_embedding` — Ø **713** Zeichen Anfrage (n=924, min 28, max 3309) gegen ein Ziel von Ø 552. Die Längen passen; **ob er trifft, ist unbekannt.** **Warum das vor dem Umbau zählt:** Wer die Spalte auf Themen umstellt, stellt den Rückweg von einem passenden Ziel auf ein fünfmal kürzeres um — und würde eine Seite reparieren und die andere brechen, ohne es zu merken. ~~**Was fertig wäre:** beide Zugriffe gegen beide Ziele, vier Zellen, dieselbe Methode~~ — **gemessen am 19.08.2026, und das Ergebnis kehrt die Empfehlung für diesen Zugriff um.** — ⬜ **offen und weiterhin ungemessen — nachgesehen am 25.08.2026.** Der Eintrag verlangt eine Trefferprobe, und die ist nicht gefahren worden. **Das ist kein Befund ueber den Code, sondern ueber eine ausstehende Messung** — er bleibt genau so lange offen, bis jemand sie ansetzt. |

| | bester Kosinus (median) | Spreizung Rang 1 → 8 |
|---|---|---|
| Ziel Destillat (heute) | **0,5530** | 0,0664 |
| Ziel Themenvektoren | 0,4601 | 0,0718 |

**Die Kandidatenlisten sind fast disjunkt: Überlappung der Top-8 im Median 1 von 8** (min 0, max 3). Eine Umstellung tauscht also sieben von acht Kandidaten aus — es ist keine Verbesserung derselben Suche, sondern eine andere Suche.

**Mit Ground Truth** (die Zusammenfassung eines Eintrags als Anfrage, gesucht wird sein eigener Eintrag): Destillat **25/25 Recall@8**, Themenvektoren **12/25**. **Die Grenze ist ausdrücklich zu nennen:** Die Zusammenfassung ist ein Ausschnitt des Textes, aus dem das Destillat-Embedding gebaut wurde — die 100 % sind trivial günstig und keine Aussage über den Betrieb. Belastbar ist die Richtung, nicht der Abstand.

> **Damit ist belegt, was vorher nur ein Vorbehalt war: Ein Vektor je Thema ersetzt keinen Inhaltsvektor.** Wer allein umstellt, hebt die Bestellung von 15 % auf 78 % und senkt den Rückweg von 25/25 auf 12/25. **Beide Ziele werden gebraucht.**

**Ein dritter Befund fiel dabei an und gehört keinem der beiden Ziele:** Die Spreizung zwischen Rang 1 und Rang 8 liegt bei **0,066 bzw. 0,072** — die acht Kandidaten liegen dicht beieinander. Der Vektor wählt also kaum vor; das Modell in `ziel_bestimmen` entscheidet fast blind. Eigener Eintrag, siehe Fundliste. | ungebändigt |

---


## Block 16.08.2026 — die Gegenrichtung der Doku-Pruefung

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Wissen**. Ueberschrift und Text stehen in jeder empfangenden Datei.

| Kennung | Was offen ist | Band |
|---|---|---|
| `SELBSTAUSKUNFT-OHNE-LESER` | **Das erste Fundstück der Klasse, die `KANAL-OHNE-GEGENSTUECK` beschreibt — von Hand gefunden, nicht vom Werkzeug.** Jeder Agent beschreibt sich selbst: `faehigkeiten`, `AGENT.md`, `typ`, `graph_eignung`, `lastart`, `context_user`. `AgentRegistry.beschreibungen()` fügt das zu einem Text zusammen, dessen Docstring den Zweck nennt — *„für den Planner-Prompt"*. **Gemessen am 16.08.2026: 14 von 14 Agenten deklarieren `faehigkeiten`, 12 von 14 tragen ein `AGENT.md`, und `beschreibungen()` hat im Produktivcode null Aufrufer.** Die erzeugende Seite ist vollzählig gepflegt, die lesende fehlt ganz. **Was stattdessen entscheidet:** `planner.plan()` sucht den Zuständigen über Zeichenketten-Abgleich auf `router_intents`, `manager.ziel` und `management_target` — also über die zentrale Zuordnung, die `novaberg-convention-planner-needs.md` §1 als Bruch des Plugin-Prinzips (E7) benennt. Ein neuer Agent kann lückenlos deklarieren, was er kann, und wird nur gefunden, wenn sein Name zum Abgleich passt. **Der billigste Weg ist ein dritter, und er stand von Anfang an daneben:** Die **Manager** haben seit Chat 5 genau diesen Mechanismus, und er lebt — `router_prompt`, von `get_combined_router_prompt()` eingesammelt und in `graph/nodes/router.py:62` als `[AGENTEN]`-Block in den System-Prompt gesetzt. Die Agenten bekommen dieselbe Eigenschaft; Aggregator, Leser und Prompt-Block existieren bereits. **Und der Vergleich beider Deklarationen erklärt, warum die eine überlebte und die andere nicht:** `["termin_erstellen", "termin_lesen"]` ist eine Auskunft in der Sprache des **Anbieters**; *„Entscheidend ist NICHT die Satzform, sondern ob der Prompt ein Datum enthält"* ist eine Anweisung in der Sprache des **Aufrufers**. Nur die zweite ist benutzbar, und nur die zweite hat je einen Leser gefunden. Die Manager-Fassung trägt zusätzlich **Negativregeln** (*„NICHT triggern bei emotionalen Ausdrücken"*), die in keiner Fähigkeitenliste ausdrückbar sind. **Erster Schritt ist aber nicht der Bau, sondern eine Gegenprobe** — und der Grund ist gemessen: **`delegation` deklariert `graph_eignung = ["user"]` und läuft über den Hintergrund-Router** (`services/pixie/router.py`, Sonderfall `aufgabe == "delegation"`); auf dem Nutzerpfad ist der Agent nicht wählbar, weil kein Manager dieses Ziel trägt. Dreizehn Deklarationen stimmen, diese eine nicht — und **niemand konnte es merken, weil kein Lauf sie prüft.** Wer den Leser zuerst baut, schaltet eine nie gegengeprüfte Datenbasis scharf: `fuer_graph("user")` nähme `delegation` auf, `fuer_graph("pixie")` ließe ihn weg, beides verkehrt herum. **Also erst alle 14 Deklarationen gegen den tatsächlichen Aufrufweg halten, dann anschließen.** → **Am 16.08.2026 durchgeführt, und das Ergebnis ändert den Zuschnitt.** Zwölf von vierzehn stimmen. Zwei nicht, und sie sind **nicht dieselbe Art Fehler**: `delegation` ist schlicht falsch (`["user"]` deklariert, über den Hintergrund-Router erreicht). `kzg` deklariert `["user"]`, **und die Frage trifft ihn gar nicht** — sein produktiver Aufruf ist fest im `dispatcher`-Knoten verdrahtet und läuft in allen drei Graphen, einschließlich des AgentGraph, den `shadow_delivery` im Hintergrund treibt; der *wählbare* Pfad über `plugins/kzg_manager` führt sich im eigenen Docstring als Legacy. **Daraus der strukturelle Befund:** Es gibt **drei** Aufrufarten — vom Planner gewählt, aus der Pixie-Queue gezogen, fest in einem Knoten verdrahtet — und `graph_eignung` hat nur für die erste eine Bedeutung. Ein Feld, das alle vierzehn Agenten füllen, ist für einen Teil von ihnen **sinnlos statt falsch**, und das ist der schwerer zu findende Zustand. Wer den Leser baut, klärt zuerst, für welche Aufrufart die Selbstauskunft überhaupt gilt. Zwei erklärbare Randfälle sind geprüft und in Ordnung: `recherche` hat kein `periodic_task`, weil es queue-basiert läuft, und `ziel_decay` steht nicht im Pixie-Router, weil es rein periodisch läuft. **Was fertig wäre:** die 14 geprüften Deklarationen mit Zahl der Korrekturen, dazu eine `router_prompt`-Eigenschaft an `BaseAgent`, von mindestens den fünf über den Planner erreichbaren Agenten gefüllt, im `[AGENTEN]`-Block sichtbar, und an einem echten Turn gemessen. Verworfen wäre damit der ursprünglich naheliegende Weg, `beschreibungen()` einen Leser zu geben — er transportierte die falsche Gattung Text. **Alternativ**, wenn die Selbstauskunft nicht gebraucht wird: begründete Streichung der fünf ungelesenen Felder samt Nachzug in `novaberg-agent-*.md`. **Nicht mitgemacht:** die Vorbedingungs-Auflösung zur Laufzeit — die ist am 16.08.2026 verworfen und liegt unter `archive/`. | [WIS] ungebändigt — ⬜ **offen** — nachgesehen am 25.08.2026. Unveraendert ohne Leser. |

---


## Block 16.08.2026 — die Fachspeicher bekommen ihre Agenten

**Die Trennlinie ist der Fremdschlüssel.** Eine Fakten-Entität, deren ID anderswo als Fremdschlüssel verwendet wird, **verfällt nicht** — ein verfallener oder deaktivierter Satz risse die Referenz. **Die Bindung darauf darf verfallen.** Damit liegt der Verfall nicht an der Sorte des Speichers, sondern an der Rolle der Zeile: Ziel eines Fremdschlüssels oder nicht.

Der Bestand, aus dem sich die Zuordnung ablesen lässt (Stand 16.08.2026):

```
Ziel eines Fremdschluessels — verfaellt nicht
  entitaeten          <- fakten.subjekt_id, fakten.objekt_id
  timeline            <- lzg_knoten.timeline_id, notizen.timeline_id
  delegations_akten   <- delegations_seiten.akte_id

Bindung — darf verfallen
  fakten              -> entitaeten      (traegt heute KEINEN Verfall)
  lzg_kanten          -> lzg_knoten      (Knoten traegt ihn, s. u.)
  verbindung          -> lzg_knoten      (bewusst ohne — ein Tagebucheintrag verblasst nicht)

Kein Fremdschluessel zeigt darauf — freier Gedaechtnisinhalt
  notizen             (traegt heute nur `aktiv`)
```

**Warum `lzg_knoten` trotzdem verfällt, obwohl Fremdschlüssel darauf zeigen:** Es ist keine Fakten-Entität, sondern Gedächtnis. Die zweite Regel entscheidet den Ort — **der Verfall sitzt dort, wo gesucht wird.** Im LZG läuft die Suche über die Knoten, im Fakten-Gedächtnis über die Kanten. Deshalb trägt dort der Knoten den Verfall und hier die Kante.

**Reihenfolge ist Bedingung, nicht Vorliebe.** Erst stehen die Gedächtnisschichten und die Charakter-Destillation vollständig; danach die Agenten für die Fachspeicher. Wer sie vorzieht, baut Pflege für einen Bestand, dessen Bewertungsgrößen sich noch bewegen.

| Kennung | Was offen ist | Band |
|---|---|---|
| `FACHSPEICHER-AGENTEN` | **Notizen, Fakten, Timeline, Dateien, Wissen bekommen je einen pflegenden Agenten.** Heute entstehen ihre Einträge, aber niemand hält sie instand. **Je Speicher ist zuerst die Rolle zu bestimmen** — Ziel eines Fremdschlüssels, Bindung oder freier Inhalt —, denn daran hängt, ob und wo ein Verfall überhaupt hingehört. Die Karte oben ist der Ausgangspunkt und keine Festlegung: Sie beschreibt den Bestand, nicht die Absicht. **Voraussetzung:** Gedächtnisschichten und Charakter-Destillation vollständig. | [WIS] ungebändigt — ⬜ **offen** — nachgesehen am 25.08.2026. **Vier von fuenf stehen:** `notizen`, `timeline`, `dateien`, `wissen` liegen als Agenten vor — **`fakten` nicht**, und der Speicher selbst traegt 0 Zeilen. Der Eintrag ist damit zu vier Fuenfteln erledigt und in seinem Rest gegenstandslos, solange der Speicher leer bleibt. |
| `FAKTEN-BINDUNG-OHNE-VERFALL` | **`fakten` ist die Bindung zwischen zwei `entitaeten` und trägt keine Verfallsgröße.** Nach der Regel — Entität bleibt, Bindung darf verfallen — und nach dem Ort des Verfalls — im Fakten-Gedächtnis läuft die Suche über die Kanten — gehört er genau hierhin. Vorhanden sind `t_valid`, `t_invalid`, `last_touched`, `wiedervorlage_am`, `aktiv`: **Bi-Temporalität, kein Verfall.** Die beiden schließen einander nicht aus, sie beantworten verschiedene Fragen — *war das wahr* gegen *ist das noch wichtig*. Offen ist nur die zweite. `entitaeten` bleibt ausdrücklich unberührt: Fremdschlüssel zeigen darauf. | [WIS] ungebändigt — ⬜ **offen** — nachgesehen am 25.08.2026. Gegenstandslos, solange `fakten` 0 Zeilen traegt — der Verfall haette nichts zu verfallen. |
| `REEMBED-WISSENSSPEICHER` | **`tools/reembed_all.py` erfasst `autonomous_wissen.themen_embedding` nicht** — 390 von 390 Zeilen belegt. Der Speicher folgt der Form von `novaberg-convention-embedding.md` §2 (eigener benannter `embed_text_bauen`, aus der persistierten `zusammenfassung` rekonstruierbar), aber die Prüffrage der Konvention — *Kann reembed_all.py diesen Vektor allein neu erzeugen?* — ist für ihn mit **nein** zu beantworten. **Die Folge ist die, gegen die die Konvention gebaut ist:** Bei einem Modellwechsel bliebe die Wissens-Bibliothek im alten Vektorraum, während die sechs übrigen Speicher migrieren — ein zweiter Mischraum. **Der Zuschnitt ist klein:** ein Ziel im Werkzeug, das den vorhandenen Bauer importiert, wie die sieben anderen auch. Gefunden beim Halten der Konvention gegen den Code. | [WIS] ungebändigt — ⬜ **offen** — nachgesehen am 25.08.2026. Gegen HEAD `599c19b` geprueft: Das Werkzeug erfasst `delegations_akten.themen_embedding`, **`autonomous_wissen` kommt darin nicht vor**. Unveraendert. |

---


## Block 18.08.2026 — aus dem Bau der Enricher-Quelle

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Wissen**. Ueberschrift und Text stehen in jeder empfangenden Datei.

| Kennung | Was offen ist | Band |
|---|---|---|
| `AUFZEICHNUNGEN-QUANTIL` | **Die Schwelle des `[AUFZEICHNUNGEN]`-Blocks soll gerechnet werden, nicht gesetzt** — `Quantil(1 − K/N)` der mitlaufenden Verteilung (`novaberg-agent-dateien_k.md` §3.0a-bis). Gebaut ist heute nur die eine Hälfte: **Kappung `K = 3` und ein gemessener absoluter Boden von 0,30.** Die andere Hälfte ist nicht vergessen, sondern **noch nicht rechenbar** — das Quantil bezieht sich auf die Verteilung der echten Paarung von Anfrage gegen Eintrag, und diese Verteilung beginnt erst mit diesem Bauteil zu entstehen. **Der Rohstoff läuft seit dem 18.08.2026 mit:** Die Protokollzeile trägt je Turn Trefferzahl, Bestand und den Kosinus des schlechtesten gelieferten Treffers. **Was fertig wäre:** Der K-te Wert wird über eine benannte Zahl von Turns gesammelt, das Quantil daraus gerechnet und tritt **neben** den Boden — nicht an seine Stelle: Eine Quantilschwelle kann *„hier ist nichts Passendes"* per Konstruktion nicht ausdrücken. **Die Auslösebedingung ist eine Zahl, kein Gefühl:** Liegt die Trefferzahl dauerhaft auf der Kappung, wählt die Kappung aus statt des Bodens — genau der Zustand, in dem die Bibliothek vier Monate lief (40 von 42 Aufrufen). **Seit dem 20.08.2026 ist der Rohstoff kein Engpass mehr:** Der Bestand hinter dem Block ist mit der Freigabe von `/docs` auf **174** Zeilen gewachsen, und die Verteilung entsteht ab jetzt an einem Korpus, der diesen Namen trägt. | [WIS] ungebändigt — ⬜ **offen** — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden. |
| `AUFZEICHNUNGEN-BODEN-NACHZIEHEN` | **Am 18.08.2026 nachgemessen und widerlegt — der Eintrag bleibt offen, aber sein Gegenstand hat sich verschoben.** Sobald der Korpus heterogen war (13 statt 3 Zeilen), lag eine einschlägige Sonde bei **0,2899** und eine fremde bei **0,2515**: Die Lücke schrumpfte von 0,18 auf **0,038**, und 0,30 schnitt einen echten Treffer ab. **Die Abhilfe war nicht die nächste Zahl, sondern der zweite Kanal** (§6.3a) — der Boden behält sein Amt für den dense Kanal, der scharfe kennt ihn nicht. **Was offen bleibt:** Ob 0,30 für den dense Kanal die richtige Zahl ist, ist damit **nicht** beantwortet, nur entschärft. Eine Lücke von 0,038 trägt keine Schwelle; ob der dense Kanal auf diesem Korpus überhaupt eine tragen kann, ist die eigentliche Frage. **Was fertig wäre:** dieselbe Sondenmessung an einem Bestand, der groß genug für eine Verteilung ist, und ein Urteil darüber, ob der dense Kanal einen Boden oder nur eine Kappung braucht. → 🟢 **Am 20.08.2026 gemessen und beantwortet.** 24 Sonden (12 einschlägig mit bekannter Zieldatei, 12 fremd) gegen 174 Indexzeilen. **Die Verteilungen liegen auseinander:** einschlägig Median **0,4293**, fremd Median **0,2519** — die Lücke beträgt 0,177 gegen 0,038 am 18.08. Wiederhergestellt hat sie der **Korpus**, nicht die Schwelle. **Urteil: Der dense Kanal braucht den Boden, und 0,30 trägt hier.** Er schneidet 1 von 12 richtigen ab und lässt 1 von 12 fremden durch; elf der zwölf fremden Fragen erzeugen **null** Zeilen darüber, ohne ihn lieferte jede die Kappung voll aus. **Der abgeschnittene richtige Fall ist folgenlos — gemessen:** Die Sonde liegt dense bei 0,2189 unter dem Boden, der scharfe Kanal liefert genau diese Datei und kennt keinen Boden; der Fund besteht aus ihr allein. Auch der Vorbehalt des ursprünglichen Eintrags ist vermessen statt vermutet: In 157 von 227 protokollierten Fällen **ist** der Suchschlüssel das rohe Embedding (kein aktives Ziel, Imperativ); in den übrigen 70 liegt der gefärbte bei Kosinus 0,9330–0,9778 zum rohen. **Was daraus folgt, steht als eigener Eintrag:** `EMBED-LISTE-DATEIENINDEX` — der verbleibende Fehler ist die Rangfolge, nicht die Schwelle. Messschrieb: `2026-08-20_boden-sonden_ergebnis.md`. Ursprünglicher Wortlaut: **Der Boden 0,30 ist an drei Indexzeilen gemessen, und das steht an der Zahl.** Acht Sonden, beide Seiten, saubere Lücke zwischen 0,2014 und 0,3800 — aber der Bestand war **ein** Register (drei Dateien über die Paper des Projekts), und die Sonden liefen mit dem **rohen** Anfrage-Embedding, während der Betrieb mit dem verschobenen Suchvektor sucht. **Was fertig wäre:** dieselbe Sondenmessung erneut, sobald der Index heterogen ist (Fachtexte, Tabellen, Code), und der Vergleich der Sondenwerte gegen die im Betrieb protokollierten. **Warum es überhaupt dasteht:** Der Vorgängerwert 0,40 war nicht falsch, weil die Zahl falsch war, sondern weil ihr Vorbehalt beim Kopieren verdunstete. Dieser Eintrag ist der Vorbehalt in haltbarer Form. | [WIS] ungebändigt — ⬜ **offen** — nachgesehen am 25.08.2026. Der Eintrag sagt selbst, dass sein Gegenstand am 18.08.2026 widerlegt wurde und er trotzdem offen bleibt — daran hat sich nichts geaendert. |

---


## Block 20.08.2026 — aus der Klassifikation der Fundliste

**47 Eintraege sind aus `novaberg-fundliste.md` hierher gewandert** und haben eine stabile ID bekommen. Sie sind offene Arbeit: abschliessbar, in unserem Code, und mit einer Antwort auf die Prueffrage *welche Arbeit waere fertig, wenn der Eintrag geschlossen wird*.

> **Der Umzug uebertraegt den Wortlaut, er prueft ihn nicht.** Jeder Befund ist die Diagnose seines Tages; das Datum steht an jedem Eintrag. Die Pflicht, ihn vor der Umsetzung **und vor der Rangvergabe** gegen den heutigen Code zu halten, gilt unveraendert — ein erledigter Eintrag an der Spitze verstellt die Sicht auf alles darunter, und er tut es lautlos.

**Die Zeilen `Was fertig waere` und `Prioritaet` sind neu** und stammen nicht aus der Fundliste. Die Prioritaet ist eine erste Einschaetzung aus dem Wortlaut, **kein Band** — ein Band wird gegen den Code vergeben.

---


#### ZUSAMMENFASSUNG-ALS-ZWEITER-ARM — der Vektor liegt, der Leser fehlt

**Kategorie:** [WIS] WISSEN

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Der Vektor liegt, der zweite Leser fehlt; ob er trifft, ist ungemessen.

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Die eingebettete Zusammenfassung liegt gefüllt im Bestand und wird vom Suchweg der Bibliothek nicht benutzt.** `autonomous_wissen.themen_embedding` ist trotz des Namens der Vektor der **Zusammenfassung** — `embed_text_bauen` ist die Identität auf `zusammenfassung` (Ø 583 Zeichen). **Gemessen am 20.08.2026: 320 von 320** aktiven Ausarbeitungen vom Typ `wissen` tragen ihn. Der Rückweg nutzt ihn (25 von 25 unter den ersten acht, `db/init.sql`); `AutonomousWissenRepository.suchen` joint dagegen ausschließlich auf `autonomous_wissen_thema` und sieht ihn nie. **Warum es zählt:** Die Bauart *„Zusammenfassung je Ausarbeitung einbetten“* — bis dahin als offene Entwurfsfrage geführt — ist damit kein Bau, sondern ein zweiter Arm in einer vorhandenen Abfrage — der Vergleichsgegenstand auf Inhaltshöhe existiert bereits.

**Was fertig waere:** Die Suche der Bibliothek hat einen zweiten Arm auf Inhaltshoehe; der Vergleichsgegenstand existiert bereits.

**Prioritaet:** mittel


#### SCHREIBPFAD-BIBLIOTHEK-UNGEMESSEN — vier Embeddings je Ablage, Kosten unbekannt

**Kategorie:** [WIS] WISSEN

**Zustand:** offen und weiterhin ungemessen — nachgesehen am 25.08.2026. Der Eintrag verlangt eine Kostenmessung; sie ist nicht angesetzt worden.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Der Schreibpfad der Bibliothek ist seit dem Umbau teurer, und um wie viel ist nicht gemessen.** Jeder `speichern()`-Aufruf baut jetzt die Themenvektoren — bei Ø 4,37 Themen je Ausarbeitung sind das rund vier zusätzliche Embedding-Aufrufe je Ablage, auf dem kleinen Modell (0,6 GB). Beobachtet am 19.08. um 20:36 UTC, als 31 Rückweg-Aufträge in Serie liefen: GPU zu **100 %** ausgelastet, VRAM 89 %, 83 Modellaufrufe in sechs Minuten. **Der Beitrag der Themenvektoren daran ist nicht isoliert** — die 83 Aufrufe sind Chat-Aufrufe von `zuordnung` und `einarbeitung`, die Embeddings kommen zusätzlich. Wer die Kosten des Schreibwegs beziffern will, misst sie eigens.

**Was fertig waere:** Die Kosten des Schreibwegs sind eigens gemessen, getrennt von den Chat-Aufrufen daneben.

**Prioritaet:** niedrig


#### RUECKWEG-VORAUSWAHL-OHNE-TRENNSCHAERFE — acht Kandidaten, 0,066 Abstand

**Kategorie:** [WIS] WISSEN

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Die genannte Trennschaerfe ist seit dem Befund nicht nachgemessen worden.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Die Vorauswahl des Rückwegs wählt kaum vor: acht Kandidaten liegen im Median 0,066 Kosinus auseinander.** `kandidaten_laden` kappt bei `KANDIDATEN_KAPPUNG = 8` und hat **keine Schwelle**; die acht gehen an ein Modell, das eines auswählt. Gemessen über 25 echte Kontexte (Ø 833 Zeichen): Abstand Rang 1 zu Rang 8 **0,0664** beim heutigen Ziel, 0,0718 bei Themenvektoren. **Wenn alle acht praktisch gleich nah sind, trägt die Rangfolge die Auswahl nicht** — das Modell entscheidet dann über den Text, nicht über die Nähe, und die Vorauswahl ist eine Kappung ohne Aussage. Ob das schadet, hängt daran, wie gut das Modell aus acht ähnlichen wählt; gemessen ist das nicht.

**Was fertig waere:** Entweder traegt die Rangfolge die Auswahl, oder die Kappung ist als Kappung ohne Aussage benannt.

**Prioritaet:** mittel


#### BEZUG-ID-NIE-AUSGELOEST — 0 von 904, die Absicherung ist unbelegt

**Kategorie:** [WIS] WISSEN

**Zustand:** offen, am Bestand bestaetigt am 25.08.2026. **0 von 697** Auftraegen tragen ein `bezug_id` — die Absicherung ist gebaut und weiterhin nie ausgeloest worden. Der Befund nannte 0 von 904; die Grundmenge ist kleiner geworden, der Zaehler nicht.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Die Ausschluss-Absicherung des Verweiswegs ist gebaut und im Betrieb nie ausgelöst worden.** `shadow_auftrag.bezug_id` hält die gerade angelegte eigene Bibliothekszeile aus der Kandidatenmenge des Rückwegs; ohne sie verstärkt jedes Recherche-Ergebnis sich selbst. Gemessen: **0 von 904** Aufträgen tragen einen Wert. **Das ist kein Defekt** — die einzige Schreibstelle ist `agents/recherche/agent.py::_verweis_einreihen`, und die drei vorhandenen `wissen_verweis`-Aufträge stammen aus dem Zeitfenster **vor** der Behebung von `VERWEIS-OHNE-WISSEN` (08:03–08:05 UTC, alle mit dem Platzhalter-Thema `Gescheitert <hash>`). Der Befund ist: **Die Absicherung hat noch keinen einzigen echten Lauf gesehen**, und ihre Wirksamkeit ist damit unbelegt — sie steht auf 0 von 0.

**Was fertig waere:** Die Ausschluss-Absicherung hat einen echten Lauf gesehen und ihre Wirksamkeit ist belegt.

**Prioritaet:** mittel


#### FUNDSTELLE-ERREICHT-DEN-MENSCHEN-NICHT — der Dienst nennt sie, die Antwort nicht

**Kategorie:** [WIS] WISSEN

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Der Befund haengt an einer Antwort im Betrieb und ist ohne Messturn nicht zu entscheiden.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Der Dienst nennt seine Fundstelle, und die Antwort an den Menschen nennt sie nicht.** Echter Turn 12:43 UTC: `agents/wissen` liefert fünf Treffer, und sein Text trägt je Treffer den Dateipfad, den Kosinus und den ausdrücklichen Hinweis *„das ist der Stand aus meinen Metadaten — nicht der Wortlaut der Ausarbeitung"*. Die Antwort, die beim Menschen ankommt, ist inhaltlich richtig (ER=EPR, Page-Kurve, Island-Regel) und nennt **weder eine Datei noch die Tiefe** — sie liest sich, als wüsste sie es aus sich. Das ist die Frage aus `novaberg-agent-dateien_k.md` §1a.4 für dieses Silo, und für den Zettel-Weg ist sie unbeantwortet: Beim Dateien-Dienst trägt der Enricher-Block eine Beschriftung, hier läuft die Auskunft über `management_result`. Zu messen: an wie vielen von N Turns die Herkunft den Responder überlebt.

**Was fertig waere:** Die Antwort an den Menschen nennt die Fundstelle, die der Dienst geliefert hat.

**Prioritaet:** mittel


#### SILO-OHNE-ZUSTAND-IN-DER-MATRIX — gebaut und abgeschaltet ist kein Zustand

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Die Rollenmatrix kennt weiterhin keinen Zustand *gebaut und abgeschaltet*.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Ein Silo, dessen Lesefunktion gebaut und abgeschaltet ist, hat in der Rollenmatrix keinen Zustand.** `fakten` überschreibt `enrich_entries` und wird im Enricher mit `continue` übersprungen, begründet im Code mit *„produziert 130+ Rausch-Eintraege"*. Die Matrix kennt nur *ja* und *nein*; gebaut-und-stillgelegt ist beides nicht und sieht in jeder Zählung wie eine bewusste Entscheidung aus. Betrifft jede Prüfung, die aus der Anwesenheit einer Methode auf eine Rolle schließt.

**Was fertig waere:** Die Rollenmatrix kennt den Zustand *gebaut und abgeschaltet*.

**Prioritaet:** niedrig


#### BESTAND-ANTWORTET-ANDERS-NACH-90-MIN — 0,9226 gegen 0,4163

**Kategorie:** [WIS] WISSEN

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Der Befund ist eine Einzelbeobachtung ohne Wiederholung; ohne zweiten Lauf ist nichts zu entscheiden.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Dasselbe Material fand denselben Bestand neunzig Minuten spaeter voellig anders — bester Kosinus 0,9226 gegen 0,4163.** Zwei Verweis-Laeufe mit **zeichengleichem** `kontext` (08:21 und 09:46). Dazwischen wurde Zeile 8974 verstaerkt (`verstaerkt_am` 08:22:03), und die Verstaerkung **haengt die Ergaenzung an die Zusammenfassung an**, die bei 500 Zeichen gekappt ist — beide Zeilen stehen heute exakt auf dieser Kappung. **Korrelation, keine belegte Ursache**; was fehlt, ist die Antwort auf die Frage, ob `speichern` den Vektor neu rechnet. **Wenn ja, verschlechtert eine Verstaerkung die Auffindbarkeit genau des Materials, das sie ausgeloest hat** — der Mechanismus arbeitete dann gegen sich selbst. Zu messen: derselbe Fund vor und nach einer Verstaerkung, Kosinus beide Male.

**Was fertig waere:** Geklaert ist, warum dasselbe Material denselben Bestand verschieden findet.

**Prioritaet:** hoch


#### KANDIDATENABFRAGE-OHNE-DB-ZEUGEN — eine Verschiebung bliebe gruen

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Ein Zeuge, der die Kandidatenabfrage gegen eine Datenbank faehrt, ist nicht dazugekommen.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Kein Zeuge faehrt die Kandidatenabfrage des Rueckwegs gegen eine Datenbank — eine Verschiebung zwischen Platzhaltern und Parametern bliebe gruen.** Vorhergesagt waren 3 rote Tests beim Entfernen der Ausschlussbedingung, gezaehlt wurden **2**; der dritte war ausdruecklich als unsicher benannt und ist der Befund: Die Attrappe prueft die Parameterzahl nicht, ein echter Lauf gegen Postgres waere gescheitert. Klasse `20_TESTS §4h` — ein Zeuge faehrt den Bestand, nicht seine Nachbildung. **Betrifft nicht nur diese Abfrage:** Wer eine Spalte in eine bestehende Abfrage einfuegt, hat hier keine Wand.

**Was fertig waere:** Ein Zeuge faehrt die Kandidatenabfrage gegen eine echte Datenbank.

**Prioritaet:** mittel


#### VERSTAERKUNGSPFAD-IM-BETRIEB-UNGETROFFEN — bezeugt, gegengeprobt, nie gelaufen

**Kategorie:** [WIS] WISSEN

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Ob der Pfad inzwischen getroffen wurde, sagt nur ein Lauf ueber das Protokoll; er ist nicht gefahren.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Der Verstaerkungspfad von Weg 3 ist bezeugt und gegengeprobt, aber im Betrieb noch nicht getroffen worden.** Vier echte Laeufe am 19.08. endeten alle in *keine Zuordnung* — dreimal begruendet, einmal als unbrauchbarer Aufruf. Der Zweig, der `haeufigkeit` und `gewicht_roh` hebt, ist damit **am Bestand ungemessen**; was vorliegt, ist die Zusicherung und die Gegenprobe. Der Grund ist nicht der Bauteil, sondern der serielle Platz: Der wartende Auftrag steht hinter einem Recherche-Lauf.

**Was fertig waere:** Der Verstaerkungspfad hat einen echten Lauf im Protokoll.

**Prioritaet:** niedrig


#### DREI-WEGE-EINE-SCHWELLE — zeichengleich mit der Promotions-Schwelle

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Die Zeichengleichheit der beiden Schwellen besteht unveraendert; entschieden ist nichts.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Die Schwelle des *Einpraegsamen* ist zeichengleich die Schwelle, die schon die Promotions-Queue oeffnet — die drei Wege aus §4b.1a sind nicht drei Kriterien, sondern zwei.** `novaberg-agent-dateien_k.md` §4b.1a nennt fuer den ersten Weg `salienz_roh >= 0,7`; `KZG_SALIENZ_HIGH = 0.94393` traegt im Code den Kommentar `# roh 0.7`, und genau an dieser Konstante haengen die beiden Einreihpunkte der Promotion (`memory/kzg.py`, `agents/kzg/queues.py`). **Der erste Weg feuert damit auf exakt der Menge, aus der der zweite spaeter seine Kandidaten zieht** — nicht ueberlappend, sondern als Obermenge, nur frueher. Gemessen am laufenden Bestand: **2597 von 2942 Eintraegen (88,3 %)** liegen ueber der Schwelle, in den letzten 24 Stunden **108 von 161 neuen**. Der Rueckweg-Auftragsbestand ist heute **3**.

**Was fertig waere:** Die drei Wege tragen drei Kriterien, oder ihre Gleichheit ist als Absicht benannt.

**Prioritaet:** mittel


#### EINREIHPUNKT-HINTER-DEM-SCHREIBEN — Ergaenzung verlangt, Datei schon geschrieben

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Der Einreihpunkt liegt unveraendert hinter dem Schreiben.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Der dritte Weg verlangt *als Ergaenzung, nicht als neue Datei* — und sein Einreihpunkt liegt hinter dem Schreiben der Datei.** `ergebnis_ablegen` (`services/wissensspeicher.py`) legt Bericht und Wissensdatei an und schreibt die Bibliothekszeile; der Einreihpunkt fuer den Rueckweg kann erst danach liegen, weil der Docstring den Queue-Push ausdruecklich dem Aufrufer zuweist. Wer dort einreiht, bekommt **beides**: die neue Datei **und** denselben Inhalt in eine bestehende eingearbeitet. Der Wortlaut des Konzepts meint das Gegenteil.

**Was fertig waere:** Der Einreihpunkt des dritten Wegs liegt dort, wo die Ergaenzung noch moeglich ist.

**Prioritaet:** mittel


#### RUECKFRAGE-DEKLARIERT-UND-UNGENUTZT — deklariert, nie benutzt

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Der Ausgang ist weiterhin deklariert und ohne Fall im Betrieb.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Der lesende Dienst deklariert die Rückfrage und benutzt sie nie.** `ausgaenge` trägt alle vier, `build_graph` hat keinen Knoten, der `status="rueckfrage"` setzt, und der Dispatch kennt keinen Rückweg. Das ist begründet — der Dienst ändert nichts, also gibt es nichts zu bestätigen —, aber die Deklaration sagt das nicht: Ein Aufrufer, der sie liest, hält einen Ausgang für bedient, den es nicht gibt. Zu klären ist, ob der Kanon der Ausgänge *„kann"* oder *„tut"* bedeutet.

**Was fertig waere:** Der lesende Dienst benutzt seine Rueckfrage oder deklariert sie nicht mehr.

**Prioritaet:** niedrig


#### ZEILEN-LESEN-OHNE-AUFRUFER — weiterhin kein Aufrufer

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — gegen HEAD `ea1667c` geprueft am 25.08.2026. `zeilen_lesen` wird zwar aus `tools/dateien/hand.py` gerufen, **aber `hand.py` selbst hat ausser Zeugen keinen Aufrufer**. Der Befund ist damit nicht erledigt, sondern eine Ebene hoeher gewandert.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **`zeilen_lesen` hat weiterhin keinen Aufrufer.** Der Zoom des lesenden Dienstes kennt Karte, Block und Nadel; das Zeilenfenster aus `tools/dateien/operationen.py` ruft niemand. Rest von `WIS-8-STUFE-2`, dort benannt.

**Was fertig waere:** `zeilen_lesen` hat einen Aufrufer oder ist entfernt.

**Prioritaet:** niedrig


#### WERKZEUGSCHICHT-DATEIEN-OHNE-RUFER — gebaut, niemand ruft sie

**Kategorie:** [WIS] WISSEN

**Zustand:** abgeschlossen — gegen HEAD `ea1667c` geprueft am 25.08.2026. Die Werkzeugschicht hat Rufer bekommen: `plugins/wissen_manager/manager.py` und `services/wissensspeicher.py` greifen darauf zu. **Der Zoom-Weg ueber `hand.py` bleibt davon unberuehrt** — er steht als `ZEILEN-LESEN-OHNE-AUFRUFER` weiter offen.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Die Werkzeugschicht für Dateien ist gebaut und wird von niemandem gerufen.** `tools/dateien/` trägt seit dem 18.08.2026 vier Module mit 88 Zeugen — Karte, Block, Fenster, Fundstelle, chirurgische Schnitte, Versionierung mit Paarungsprüfung, und die Auftragsform `DATEI: {json}`. Gezählt über `grep` auf die Importe: **kein Knoten, kein Agent, kein Plugin importiert eines davon**, und die Anleitung steht in keinem Prompt. Der Werkzeugsatz ist an echten Wissensdateien erprobt (Kette aus Karte, Änderung, Einfügen, Verlauf, Paarung — 0 Befunde), aber Nova kann nichts davon aufrufen. **Kein Defekt, sondern ein Zwischenstand** — festgehalten, weil 88 grüne Zeugen genau darüber nichts sagen und die Lage aus dem Testergebnis nicht ablesbar ist.

**Was fertig waere:** Die Werkzeugschicht fuer Dateien hat einen Eingang von der Nutzerseite.

**Prioritaet:** hoch


#### RETRIEVAL-SCHWELLE-OHNE-WIRKUNG — die Kappung gibt den Ausschlag

**Kategorie:** [WIS] WISSEN

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Die Schwelle wird uebergeben (`plugins/wissen_manager/manager.py`); ob sie je den Ausschlag gibt, verlangt eine Verteilung und ist ungemessen. Deckungsgleich mit der Klasse von `KAPPUNG-VOR-GRENZWERT`.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **`WISSEN_RETRIEVAL_SCHWELLE = 0.40` hat noch nie den Ausschlag gegeben; die Kappung gibt ihn — und der Vorbehalt dazu ist auf dem Weg ins Konzept verdunstet.** Der Wissens-Manager sucht mit `WHERE cosine >= 0.40 ... LIMIT WISSEN_RETRIEVAL_TOP_K`, und `WISSEN_RETRIEVAL_TOP_K` ist **3**. Über 42 protokollierte Aufrufe kamen **40 mal genau drei** Treffer zurück — die Obergrenze, nicht die Auswahl. Der Kosinus des dritten Treffers liegt bei min 0,404, **Median 0,588**, max 0,691. Die Geometrie des Korpus erklärt, warum die Schwelle nichts tut: 217 aktive Einträge, 23.436 Paare, **Median-Kosinus 0,369**, und **35,6 % aller Paare liegen über 0,40**. Erst **0,55** liefert gerechnet die drei Treffer, die tatsächlich ankommen; **die wirksame Schwelle ist 0,55 und steht nirgends.** — **Der Bestand ist dabei nicht der Schuldige, und das ist der eigentliche Fund.** `config.py:478` sagt von sich aus *„von `anker_retrieval` uebernommen, NICHT gemessen"*, nennt den Grund (*„die Bibliothek hatte bei ihrer Einfuehrung drei Zeilen"*) und verweist auf den offenen Backlog-Eintrag `WIS-SCHWELLE-MESSEN`. Auch die Quelle trägt ihren Vorbehalt: `lzg_knoten.py:425` führt die Abdeckungsmessung mit (0,50 → 53 %, **0,40 → 82 % bei 4,1 Ankern von 302**, 0,35 → 89 % und Rauschen) und markiert sie als *„begruendeter Startwert, kein Verteilungs-Messergebnis"*. **Beide Code-Stellen sind ehrlich; erst das Konzept nannte den Wert „gemessen"** (`novaberg-agent-dateien_k.md` v0.5/v0.6, in v0.7 berichtigt). Die Zahl gibt der Übernahme quantitativ Unrecht: Im Knotenraum qualifiziert 0,40 rund **1,4 %** des Bestandes, in der Bibliothek **35,6 %** — derselbe Wert, derselbe Embedding-Raum, **Faktor 26 im Trennverhalten**. **Die Klasse ist allgemeiner als der Fall, und sie ist zweiteilig:** Ein Grenzwert, hinter dem eine Kappung steht, ist unbelegt, solange die Kappung greift — und **ein Vorbehalt überlebt das Kopieren einer Zahl nicht**, wenn nur die Zahl kopiert wird.

**Was fertig waere:** Die Schwelle wirkt oder entfaellt; der Vorbehalt steht unverkuerzt im Konzept.

**Prioritaet:** mittel


#### GRENZE-OHNE-LESER — auf fuenf Diensten deklariert, null Leser

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — gegen HEAD `ea1667c` geprueft am 25.08.2026. `grenze` wird ausschliesslich von Zeugen gelesen; im Produktivpfad hat die Eigenschaft weiterhin **null** Leser.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **`grenze` ist auf fünf Diensten deklariert und hat null Leser.** Die Eigenschaft beantwortet *„was tust du ausdrücklich nicht"* und ist nach der NMCP-Konvention Pflicht für alle Dienste; im Bestand tragen sie vier Empfangsdienste mit je drei Einträgen. **Kein Code liest sie** — weder der Aushang-Aggregator, noch die Anmeldeprüfung, noch der vierte Ausgang. Damit ist sie genau die Klasse, gegen die die Konvention gebaut wurde, entstanden am Tag ihrer Einführung. Die Konvention nennt ihren Zweck in §4.9: Trifft die Zustellquote und ist die Ablehnungsquote hoch, dann stimmt der Aushang und **die Grenzangabe fehlt** — dafür muss sie aber irgendwo gelesen werden. Wohin sie gehört, ist eine Entscheidung: ins Brett neben die Negativfälle (dann verhindert sie Zustellungen, die ohnehin abgelehnt würden), oder in den Vorschlag des vierten Ausgangs (dann erklärt sie dem Auftraggeber die Ablehnung).

**Was fertig waere:** `grenze` wird gelesen oder ist entfernt.

**Prioritaet:** niedrig


#### WISSEN-UND-WEBSUCHE-NICHT-ANSPRECHBAR — ueber den Empfang nicht erreichbar

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Ueber den Empfang sind beide weiterhin nicht als Dienste ansprechbar. Verwandt mit `SILO-OHNE-WERKZEUG`.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Novas eigenes Wissen und die Websuche sind über den Empfang nicht als Dienste ansprechbar.** Eine Äußerung wie *„such mal in deinem Wissen"* oder *„schau im Netz nach"* spricht etwas an, das keinen Aushang hat: Die Bibliothek (`autonomous_wissen`, 463 Zeilen) hängt als Kontextquelle am Enricher und wird nicht gewählt; der Web-Pfad läuft über den Zustandsmerker `needs_web`, den der Empfang setzt und den der Denkknoten liest — ebenfalls kein Dienst. **Damit gibt es drei Wissensbestände mit drei verschiedenen Zugängen** (eigenes Wissen, freigegebene Dateien, Web), von denen nur einer über einen Zettel erreichbar wäre. Ein Mensch, der einen davon ausdrücklich anspricht, bekommt kein Urteil und keine Fehlmeldung, sondern eine Antwort aus dem, was der Enricher ohnehin gelegt hat. Aufgefallen beim Entwurf des Dateien-Dienstes (`novaberg-agent-dateien_k.md` §3.0c); älter als er.

**Was fertig waere:** Novas eigenes Wissen und die Websuche sind als Dienste ansprechbar.

**Prioritaet:** mittel


#### ZUSTELLART-EINWERTIG — auf Anfrage UND periodisch geht nicht

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Die Zustellart ist unveraendert einwertig.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Die Zustellart eines Dienstes ist einwertig und kann einen Dienst nicht beschreiben, der auf Anfrage UND periodisch arbeitet.** Sie wird aus `graph_eignung` und `periodic_task()` abgeleitet: Wer im Nutzergraphen zugelassen ist, gilt als am Empfang; wer eine periodische Aufgabe hat, als am Zeitplan. Ein Dienst, der beides legitim ist — erreichbar über seinen Aushang und zusätzlich mit eigenem Takt —, fällt durch: Die abgeleitete Zustellart ist für die halbe Arbeit falsch, und die Anmeldeprüfung verlangt daraufhin einen Aushang zu viel oder zu wenig. Aufgefallen beim Entwurf des Dateien-Dienstes (`novaberg-agent-dateien_k.md` §3), dort durch Aufteilung in zwei Dienste umgangen — **umgangen, nicht gelöst.**

**Was fertig waere:** Die Zustellart eines Dienstes kann mehrwertig sein.

**Prioritaet:** niedrig


## 0c. Aus der Fundliste klassifiziert — Chat 133 (08.08.2026)

Sieben Einträge der Fundliste waren offene Arbeit: abschließbar, in unserem Code, und mit einer Antwort auf die Prüffrage *welche Arbeit wäre fertig, wenn der Eintrag geschlossen wird*. Drei davon sind Nähte ohne Prüfung, zwei sind Aussagen über den Zustand, die veraltet sind, und zwei sind Rechnungen ohne Abnehmer.


### Block 30.–27.07. — neun Einträge (08.08.2026)

Der aelteste Bestand. **Acht der neun sind Struktur statt Verhalten** — tote Zweige, doppelte Formen, ein Dokument ohne Abgleich. Der neunte, die Ungleichverteilung des Repertoires, ist der einzige, der eine Absicht braucht.


#### NOTIZEN-ENRICH-16-ZWEIGE

**Kategorie:** [WIS] WISSEN

**Zustand:** offen, gefallen — am Bestand gemessen am 25.08.2026. `enrich_entries` traegt heute **12** Verzweigungen statt 16. Kleiner, aber unveraendert der Befund: eine Funktion mit zwoelf Zweigen ist keine Funktion mit einer Aufgabe.

**Befund (2026-07-30).** `plugins/notizen_manager/manager.py` `enrich_entries()` traegt **16 Verzweigungen und 67 Anweisungen** — mehr als jede der fuenf Funktionen, die an diesem Tag zerlegt wurden. Sie tauchte in der Liste der Zaehlregel-Funde nicht auf, weil sie im **Ueberlappungsbereich** von C901 und PLR0912 liegt: Wer nur die eigenstaendigen Treffer der einen Regel ansieht, uebersieht die groessten Faelle, weil die von beiden Regeln gemeldet werden. Der Fund ist nicht die Funktion, sondern die Auswahlmethode.

**Was fertig waere.** Die Funktion ist zerlegt.

**Prioritaet:** niedrig.


## 0. Zeitparser und Kalibrierung (31.07.2026)

Vier Einträge aus einem Tag. Die ersten drei kommen aus dem ersten Lauf des Härtefallkorpus gegen den Parser, der vierte aus der Neuerhebung der Positions-Kontrolle.


#### ZEIT-ZWOELF-STUNDEN-DEUTUNG — „halb drei" trifft die falsche Tageshälfte

**Kategorie:** [WIS] WISSEN

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Eine Deutungsfrage, die eine Festlegung braucht und keine Messung.

Die Normalisierung bildet „halb drei" auf `2:30` ab, ohne zu entscheiden, welche Tageshälfte gemeint ist. Um 14 Uhr gesagt, ergibt der Ausdruck damit 2:30 des **nächsten** Tages statt 14:30 desselben. Betrifft ebenso „fünf nach drei".

**Der Befund wurde erst sichtbar, nachdem ein anderer Defekt weg war.** Bis zum 31.07.2026 ergab „halb drei" den 1. des Monats (`PARSER-NACKTE-UHRZEIT-FALSCHER-TAG`); dass zusätzlich die Stunde falsch ist, verdeckte der falsche Tag.

**Das ist eine Bedeutungsfrage, keine Reparatur:** Welche Tageshälfte ein Sprecher meint, folgt aus der Uhrzeit des Sprechens und aus dem Kontext, nicht aus einer Regel über Zahlwörter. Vor der Umsetzung gehört die Absicht ins Konzept.

**Belegt:** Korpus `REG-006`, `REG-008`. **Priorität:** mittel.


#### ZEIT-TAGESZEIT-VOR-ZIFFER — „3 nachmittags" wird zum 3. des Monats

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Unveraendert; verwandt mit `ZEIT-EINZAHL-GREIFT-DANEBEN`, das heute im Betrieb reproduziert wurde.

Die Tageszeit-Extraktion (Block 0) nimmt „nachmittags" aus dem Text und merkt sich 15:00 als Fallback. Die „3" bleibt stehen, der Fallback wird angehängt, und `dateparser` liest das Ergebnis `3 15:00` als **Tag 3 um 15:00**.

Der Block für alleinstehende Tageszeiten (Block 3) käme mit dem Ausdruck zurecht — er sieht ihn nur nie, weil Block 0 das Wort vorher entfernt hat. **Eine Reihenfolgefrage, kein fehlender Wortschatz.**

**Belegt:** Korpus `REG-011`. **Priorität:** niedrig — der Ausdruck ist selten, der Fehlbetrag klein.


## 2. Skill-System (Epic 10)

Nova lernt im Gespraech, wie sie bestimmte Aufgaben ausfuehren soll. Der User erklaert eine Faehigkeit, Nova abstrahiert daraus einen wiederverwendbaren Skill-Prompt, den sie bei zukuenftigen Auftraegen automatisch anwendet.

**Drei Instruktionsebenen:** Direktive (Verhaltensanweisung, dauerhaft, Ebbinghaus-Decay), Skill (Ausfuehrungsanweisung, persistent, kein Decay) und Auftrag (konkreter Befehl, einmalig, Session). Direktive formt das Wie, Skill definiert das Koennen, Auftrag ist das Was.

**Lebenszyklus:** Erstellen (User erklaert, Salienz erkennt Lehrsequenz, LLM destilliert Skill-Prompt) → Anwenden (Enricher findet Skill ueber Trigger-Match, injiziert in Kontext) → Verfeinern (Update zu bestehendem Skill, versioniert) → Loeschen (Soft-Delete).

**Architektur:** SkillManager als Plugin im Plugin-System (BaseManager, Auto-Discovery). Datenmodell: `skills`-Tabelle mit Name, Trigger-Keywords, Skill-Prompt, Version. Trigger-Matching: aktuell Keyword-basiert, spaeter moeglicherweise Embedding-basiert.

**Offene Fragen:** Skill-Konflikte bei Mehrfach-Match, Qualitaet der Destillation durch 24B-Modell, Meta-Skills (rekursives Lernen).


### Erweiterung: Code-Skills via Claude API (Chat 45)

Neben Prompt-Skills (Typ 1: Ausführungsanweisungen, Prompt-Injection) ein zweiter Skill-Typ:

**Typ 2: Code-Skills** — Nova sammelt Wissen, baut Spezifikation, beauftragt Claude API mit Code-Generierung, testet und registriert als Tool.

Beispiel-Flow:
```
User: "Bau mir einen Skill für meine Hue-Lampe"
Novaberg (lokal, Gemma 4): Sammelt Anforderungen, recherchiert Hue API
Nova: Reichert Spezifikation mit gesammeltem Wissen an
Novaberg → Claude API: "Generiere ein Python-Skript nach dieser Spec"
Claude API → Novaberg: Fertiger Code
Novaberg (lokal): Testet, registriert als Tool
Ab jetzt: "Mach das Licht an" → Nova ruft hue_skill.py auf
```

Nutzt den bestehenden AnthropicProvider. Traffic und Kosten gering (2-3 API-Calls pro Skill, Sonnet 4.6, wenige Cent).

**Voraussetzungen:** ProjektAgent (Wissen ablegen + Spec bauen), Recherche + Vertiefen (Wissen sammeln), Reasoning (Strategie + Ziel formulieren).

**Verbindung aller Epics:** Recherche → Dateien → Vertiefen → Spec → Claude API → Skill. Der ProjektAgent ist das Fundament.

---


## 7. Offene Epics & Features


### Kommunikation

> **Nur als Herkunft.** Dieser Abschnitt ist selbst ein Eintrag und steht in [`novaberg-backlog-antwortpfad.md`](novaberg-backlog-antwortpfad.md); hier stehen die Eintraege darunter, die zu diesem Gegenstand gehoeren.

#### AGENT-RUECKFRAGE-LOOP — Nicht-terminierende Planner→Agent-Rückfrage-Schleife

**Kategorie:** [WIS] WISSEN

**Status:** ⬜ Nicht reproduzierbar (Chat 101). Fünf Turns verschiedener Statustypen (rejected/abgeschlossen/fehler/read) terminierten alle über den `bereits_gelaufen`-Guard. Vermutlich durch Zwischen-Fix in `dispatch.py` (`_build_return` setzt `agent_name=""`, `agent_results` akkumuliert sauber) erledigt. Nicht geschlossen — falls unter anderen Bedingungen doch auftretend, hier wieder aufnehmen. Vorsorge-Konzept: `iteration-control_k` (geparkt).
**Entdeckt:** Chat 100
**Symptom:** Planner und Notizen-Agent bilden eine nicht-terminierende Schleife. Der Agent gibt `rueckfrage` zurück, der Folge-Durchlauf erkennt den nächsten Prompt nicht als Antwort auf die Rückfrage, plant neu und fragt erneut — die `notizen: rueckfrage`-Kette akkumuliert pro Iteration ein Glied. Beobachtet bei Prompt „… Du musst Dir nur merken, dass ich Claus heiße".
**Auswirkung:** Betriebsgefährdend — die Schleife terminiert nicht von selbst.
**Verwandt:** Vermutlich PENDING-RELEVANZ (Router prüft nicht, ob ein Prompt die Antwort auf eine Rückfrage ist) — gleiche Wurzel, andere Manifestation.
**Lösung:** Offen — noch nicht untersucht.
**Prio:** Herabgestuft (Chat 101) — siehe Status; nicht mehr betriebsgefährdend, da im aktuellen Codestand nicht reproduzierbar.


#### NOTIZEN-VOR-TURN-BEZUG — Klassifikator löst Rückbezüge aus dem Verlauf nicht auf (Chat 101)

**Kategorie:** [WIS] WISSEN

**Status:** ⬜ Offen, reproduzierbar
**Entdeckt:** Chat 101
**Symptom:** Der Notizen-Klassifikator löst Rückbezüge aus dem Verlauf nicht auf. Beleg: „Die andere ist die mit dem Grillkäse" wurde als `rejected` klassifiziert, obwohl der Verlauf die gemeinte Lösch-Aktion eindeutig machte — trotz Prompt-Anweisung „Nutze den Verlauf für Target-Auflösung".
**Verwandt:** Wiederauftreten der Klasse des abgeschlossenen Chat-80-Sprints `NOTIZEN-VOR-TURN-BEZUG` (Inhalts-Auflösung im Classify-Node, weiter unten in diesem Dokument) und von `NOTIZEN-UPDATE-TARGET-LEER` — hier auf einer Lösch-/Target-Auflösung. Regressions-Charakter: Der Chat-80-Sprint galt als abgeschlossen, doch dieser Pfad (Lösch-/Target-Auflösung nach vorheriger Rückfrage) tritt erneut auf. Zu klären, ob der Chat-80-Fix regrediert ist oder diesen Pfad nie abdeckte.
**Prio:** Mittel.


### Refactoring & Code-Hygiene (Chat 88)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Wissen**. Ueberschrift und Text stehen in jeder empfangenden Datei.

Sammelposten aus zwei Audits in Chat 88 — dem allgemeinen Code-Audit zum Synapsen-Umbau und der P0-Migrations-Konsolidierung (db/init.sql als Single Source of Truth). Zwölf Einträge: sechs aus dem allgemeinen Audit, drei aus P0-Beobachtungen während der Konsolidierung, drei aus dem P0-Abschluss-Bericht. Bewusste Trennung von den Synapsen-Sprints P1–P10: diese Einträge sind keine Voraussetzung für den Umbau, sondern Code-Hygiene auf Bestand und neuer Infrastruktur. Werden zwischen den Sprints oder in einer eigenen Refactor-Welle abgearbeitet.

| # | Thema | Status |
|---|-------|--------|
| TIMELINE-IN-KERN | Timeline-Plugin in den Kern anheben. Konsequenzen: `agents/timeline/init.sql` entfällt, die Tabellen-Definitionen wandern in `db/init.sql`, und der in P0 angelegte Übergangs-DO-Block für die FK-Constraints `langzeitgedaechtnis.timeline_id` und `notizen.timeline_id` wird in die jeweiligen CREATE-Definitionen konsolidiert. Der Übergangs-Kommentar in `agents/timeline/init.sql` verweist explizit auf diesen Umzug. | [WIS] ⬜ Prio mittel — Meister hat den Umzug für die nahe Zukunft angekündigt |
| FAKTEN-IN-KERN | Fakten-Plugin in den Kern anheben. Konsequenzen wie TIMELINE-IN-KERN: Tabellen-Definitionen, Indizes und FK-Constraints wandern in `db/init.sql`. | [WIS] ✅ **erledigt, festgestellt am 25.08.2026** — `fakten` steht in `db/init.sql`, und ein Verzeichnis `agents/fakten/` gibt es nicht mehr. Der Umzug ist gefahren, die Marke war nie gezogen. `TIMELINE-IN-KERN` steht dagegen weiter: `agents/timeline/init.sql` liegt unveraendert |
| NOTIZEN-INDIZES-NACHTRAG | Fünf Indizes auf `notizen` (`idx_notizen_aktiv`, `idx_notizen_wiedervorlage`, `idx_notizen_suchtext`, `idx_notizen_name_trgm`, `idx_notizen_text_trgm`) standen in der alten `db/init.sql`, fehlten aber in der Live-DB. P0-Audit hat „Live = Soll" angewandt — die Indizes sind in der neuen `db/init.sql` nicht enthalten. Frage ist nicht Schema-, sondern Funktions-Frage: wird Fuzzy-/Trigram-Suche auf Notizen tatsächlich gebraucht? Falls ja, nachziehen. | [WIS] ⬜ Prio niedrig — entscheiden, sobald Notizen-Suche eine konkrete Anforderung wird |
| REFAC-HANDBUCH-§9-MIGRATIONS | `DEVELOPER_HANDBOOK.md` §9 fordert „Niemals ALTER TABLE in init.sql. Schema-Änderungen laufen über separate, versionierte Migrations-Skripte (Alembic empfohlen)." Diese Norm widerspricht der seit P0 etablierten Konvention — `db/init.sql` ist Single Source of Truth, und Schema-Änderungen werden als ALTER-Statements am Ende der Datei eingefügt und in Reviews zu CREATE-Definitionen konsolidiert. Das Handbuch ist hier outdated und muss auf die gelebte P0-Konvention nachgezogen werden. Plugins (`agents/*/init.sql`) bleiben eigenständig. | ✅ Erledigt (Docs-Commit 12.07.2026) — §9 neu gefasst (Handbuch v0.4), siehe HANDBUCH-§9-VERALTET |
| PLANNER-TIMELINE-INTENT-MISS | Der Planner erkennt explizite Timeline-Aufträge ("Merk dir bitte den 17. Oktober als Annas Geburtstag") nicht zuverlässig als Timeline-Intent und dispatcht den TimelineAgent nicht. Folge: `magnete_aufloesen` legt einen `erinnerungs_anker` an, statt einen echten `geburtstag`-Eintrag zu sehen. Aufgedeckt im P3-V7-Clipboard-Test (Chat 88): Test-Turn mit expliziter Timeline-Absicht erzeugte nur einen `erinnerungs_anker` für den 17.10.2026, keinen `geburtstag`-Eintrag. Konsequenz: Clipboard-Pattern strukturell vorbereitet, aber im Live-Betrieb selten getriggert. Tiefere Betrachtung deutet auf eine grundsätzliche Architektur-Frage hin (Agenten-Aktivierungs-Modi, Push vs. Pull), die nach P9 in einem eigenen Konzept-Doku adressiert werden soll. | [WIS] ⬜ Prio mittel — nach P9 strukturell adressieren |


## EPIC-WISSENSSPEICHER — Novas eigene Bibliothek (04.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Wissen**. Ueberschrift und Text stehen in jeder empfangenden Datei.

**Kategorie:** [WIS] WISSEN

**Status:** 🔶 Vier von sechs Schritten gebaut, dazu der Enricher-Anschluss.
**Konzept:** `novaberg-autonomous-wissen_k.md` §11 — dort stehen alle Entscheidungen samt Herleitung.

| ID | Inhalt | Stand |
|---|---|---|
| **WIS-1-MOUNT** | `knowledge/` als Geschwister der Repositoriumswurzel, im Behälter `/knowledge` | [WIS] ✅ **04.08.2026** |
| **WIS-2-TABELLE** | `autonomous_wissen` mit Paar-Schema, Salienz ohne Default, drei Gewichtsspalten | [WIS] ✅ **04.08.2026** |
| **WIS-3-DATEIEN** | Agenten schreiben Wissen- und Bericht-Datei plus `INDEX.md`, mit `umask 000` / `0666` / `0777` | [WIS] ✅ **04.08.2026** — `recherche`; die übrigen Agenten ziehen nach dem Beispiel nach |
| **WIS-4-STAPEL-SALIENZ** | `stack_push()` bekommt Salienz und `verstaerkt_am` — beide fehlen heute ganz | [WIS] ⬜ |
| **WIS-5-VERFALL** | Dritter Schritt im vorhandenen Tageslauf `synapsen_decay`, je Schritt ein eigener Audit-Eintrag | [WIS] ⬜ |
| **WIS-6-FORTSETZEN** | Der Aufräumer verstärkt statt zu löschen, Schwelle 0.60 | [WIS] WIS-3 — ⬜ **offen** — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen; der Eintrag beschreibt ein Ziel und keinen Defekt. |
| **WIS-PRUEFUNG-F-WISSEN-1** | Pfadprüfung, dass kein Schreibziel des Wissenspfads innerhalb des Arbeitsbaums liegt | [WIS] ✅ **04.08.2026** — `schreibziel_pruefen()`, jeder Schreib- und Lesevorgang geht hindurch; fünf Testfälle inklusive `..`-Ausbruch |
| **WIS-7-ENRICHER** | Die Bibliothek als sechste Kontextquelle — `WissenManager`, Metadaten-Treffer über Embedding-Nähe, derselbe Suchschlüssel wie KZG und LZG | [WIS] ✅ **04.08.2026** — Stufe 1 |
| **WIS-8-STUFE-2** | Reicht die Zusammenfassung nicht, den **Dateiinhalt** lesen (§7.3). ~~Braucht den Lesepfad in `tools/dateien/`, den es nicht gibt.~~ → 🟢 **Der Lesepfad existiert seit dem 18.08.2026** (`tools/dateien/operationen.py`: `struktur_analysieren`, `block_lesen`, `zeilen_lesen`, `datei_grep`; 26 Zeugen). Die Blockade ist weg; **offen bleibt der Aufrufer** — kein Knoten ruft die Werkzeuge. **Neu bewertet am 18.08.2026:** Der Wächter (`dateien_index`) ist der **erste Produktivaufrufer** — er ruft `struktur_analysieren` je indizierter Datei. Damit ist die Leseschicht nicht mehr aufruferlos. **Offen bleibt der Zoom selbst:** `block_lesen`, `zeilen_lesen` und `datei_grep` hat weiterhin niemand, und genau die sind die Stufe 2 der Bibliothek. Sie wandern an den lesenden Dienst (Stufe 4). → 🟢 **Geschlossen am 18.08.2026:** Der lesende Dienst hat seinen Aufrufer, und `block_lesen` wie `datei_grep` laufen im Betrieb — gemessen an einem echten Turn: Karte 7 Blöcke ohne Dateizugriff, Nadel 2 Fundstellen, und die Antwort trägt Fundstelle und Zahl im selben Satz. **Rest, ausdrücklich benannt:** `zeilen_lesen` hat weiterhin keinen Aufrufer — der Zoom kennt Karte, Block und Nadel, aber kein Zeilenfenster. **Andere Bauart prüfen:** Die Mandelbrot-Navigation ist aus dem 32k-Zwang abgeleitet; im Hintergrund stehen 262144 Token | [WIS] WIS-7 — ⬜ **offen** — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen; der Eintrag beschreibt ein Ziel und keinen Defekt. |
| **WIS-SCHWELLE-MESSEN** | [WIS] `WISSEN_RETRIEVAL_SCHWELLE` steht auf **0.40 — übernommen von `anker_retrieval`, nicht gemessen.** Gleicher Embedding-Raum, gleiche Art Anfrage, aber die Bibliothek hatte bei ihrer Einführung drei Zeilen. Zu messen, sobald Bestand da ist: Abdeckung und Fehltreffer über echte Prompts, wie bei der Kalibrierung von 0.40 selbst. — 🔶 **Vorbedingung erfüllt und zur Hälfte gemessen (17.08.2026).** Bestand: 217 aktive Einträge. **Die Schwelle greift nicht — die Kappung greift:** 40 von 42 protokollierten Aufrufen lieferten genau `WISSEN_RETRIEVAL_TOP_K` = 3 Treffer, der Kosinus des dritten liegt bei Median 0,588 (min 0,404, max 0,691). Über 23.436 Paare des Korpus: Median 0,369, **35,6 % über 0,40**; gerechnet liefert erst **0,55** drei Treffer. Zum Vergleich qualifiziert 0,40 im Knotenraum, für den es kalibriert wurde, rund 1,4 % — **Faktor 26**. **Rest:** Abdeckung und Fehltreffer über echte Prompts sind damit **nicht** gemessen; dafür fehlen die Anfragevektoren, die nicht aufbewahrt werden. ~~Wer den Rest hebt, braucht zuerst einen Weg, `such_vektor` mitzuschreiben~~ — **am 19.08.2026 widerlegt, einen Tag nach der Niederschrift.** Aufbewahrte Anfragevektoren braucht die Messung nicht: Fragen kann man **stellen**. Eine Sonde mit acht ausdrücklichen Fragen gegen den Bestand lieferte am selben Tag die Zahl, die der Eintrag für unerreichbar hielt — und sie widersprach der Kalibrierung von 0,40 in der Gegenrichtung. **Der Rest ist damit nicht blockiert, sondern messbar**, und die Vorbedingung ist keine.|

**Gemessen am 19.08.2026 — und die Frage war falsch gestellt: die Schwelle ist nicht das Problem, die Rangfolge unter ihr ist es.** 40 Fragen (Seed 20260819) gegen 249 Einträge, je Frage ist die richtige Antwort bekannt. Der beste **falsche** Treffer liegt im Median näher als der richtige (0,4781 gegen 0,4045); **die richtige Antwort landet in 8 von 40 Fällen auf Rang 1 — 20 %.** Bei 0,40 werden gleichzeitig **50 % der richtigen verworfen und 80 % der Fehltreffer durchgelassen**; keine andere Zahl schafft beides, weil sich beide Verteilungen vollständig überlappen (40/40).

**Die Ursache steht an der Quelle und ist ein Feldname:** `agents/recherche/agent.py` baut `themen_embedding` aus dem **Destillat**, nicht aus dem Thema — der Docstring nennt es „Zusammenfassung", die Spalte „Thema", das Argument ist das Destillat. Gemessen sind das Ø 552 gegen Ø 110 Zeichen. Eine kurze Frage gegen einen fünfmal längeren Fließtext zerlegt die Rangfolge. Zum Vergleich mit frisch eingebettetem **Thema** als Ziel: **39 von 40 auf Rang 1**.

**Die Grenze der Messung, ausdrücklich:** Die Frage trägt das Thema wörtlich, was das Thema-Ziel systematisch begünstigt — die 98 % sind keine Vorhersage für den Betrieb. Belastbar ist die andere Seite, und zwar als **Untergrenze**: Selbst im günstigsten denkbaren Fall liegt der Bestand bei 20 %.

**Was jetzt fehlt, ist eine Absicht und keine Umsetzung:** Ein neues Embedding-Ziel heißt, 249 Bestandszeilen neu einzubetten. Drei Wege stehen offen — nur das Thema; Thema und Zusammenfassung in zwei Spalten; Thema plus gekappte Zusammenfassung in einem Vektor. **Welcher trägt, ist nicht gemessen** und wäre der nächste Lauf.

**Wofür getrennte Spalten — gemessen am 19.08.2026:** Die Spalte hat **zwei** Konsumenten, und ihre Anfragen liegen längenmäßig auseinander.

| Konsument | Anfrage | Länge | passt zu |
|---|---|---|---|
| Bestellung (`AutonomousWissenRepository.suchen`) | die Frage des Nutzers | ~60–100 Z. | **Thema** (Ø 110) |
| Rückweg (`agents/wissen_rueckweg/zuordnung.kandidaten_laden`) | `auftrag['kontext']` | **Ø 713 Z.** (n=924, min 28, max 3309) | **Destillat** (Ø 552) |

**Damit hat die naheliegende Abhilfe einen Preis, den bisher niemand genannt hat.** Wer allein auf das Thema umstellt, repariert die Bestellung und stellt den Rückweg auf ein fünfmal kürzeres Ziel um — dieselbe Asymmetrie, nur andersherum, und sie träfe 924 gelaufene Zuordnungen.

**Ausdrücklich offen:** Ob der Rückweg heute *trifft*, ist **nicht gemessen**. Die Längenpassung ist ein Argument dafür, ihn vor der Umstellung zu messen — kein Beleg dafür, dass er funktioniert. **Der nächste Lauf misst deshalb beide Zugriffe gegen beide Ziele**, nicht nur den einen, der aufgefallen ist. | Bestand in `autonomous_wissen` |
| **WIS-GATE-MESSUNG** | Wie oft das Keep/Discard-Gate falsch urteilt, ist **nicht gemessen**. Die Verteilung der vier Status über echte Durchläufe ist die Grundlage dafür, ob die Schwelle zwischen `ergaenzung` und `wiederholung` taugt | [WIS] WIS-3 — ⬜ **offen** — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden. |
| **WIS-KONTEXT-NEU-DIMENSIONIEREN** | ⚠ **Die Latenz-Begründung war zwischenzeitlich als widerlegt vermerkt — die Rücknahme ist selbst zurückgenommen.** Der Aufschlag von 35 s je Aufruf bei 262144 (`PIX-WARTESCHLANGE-AM-MODELL`) trifft die Recherche mit ihren gut zehn Aufrufen sehr wohl; er steckt nur nicht in `prompt_eval_duration`. Dazu kommt weiterhin der Verlust durch die Kompression. Der Hintergrundpfad hat **262144** Token, nicht 32768 — gemessen am 04.08.2026, 21:02 UTC. Damit steht die Kompressionsstufe der Recherche (`zwischen_destillieren`) zur Disposition: Sie komprimiert verlustbehaftet gegen eine Grenze, die achtmal weiter weg ist, **und ist der gemessene Ausfallpunkt** eines Durchlaufs. Ebenso das Zwei-Stufen-Retrieval: Eine ganze Wissen-Datei passt in den Prompt, der fraktale Zoom ist für den Hintergrund keine Notwendigkeit mehr, sondern eine Wahl. **Der Gesprächspfad bleibt bei 32768** — beide Zahlen gehören getrennt gehalten | [WIS] keine |

---


## EPIC-KLAERUNG — Abweichung und Luecke (04.08.2026)

**Kategorie:** [WIS] WISSEN

**Status:** ⬜ nicht begonnen. Grundsatz formuliert, Bestand belegt, Bauteile entworfen.
**Konzept:** `novaberg-klaerung_k.md` — dort stehen ZIEL, TEST, MESSUNG und Gegenprobe je Bauteil.

**Der Kern in einem Satz:** Weicht eine Eigenschaft eines Objekts von der gespeicherten ab, oder fehlt eine notwendige, ist das derselbe Zustand — *erwartet ≠ vorhanden* — und beide enden, wenn sie bedeutsam genug sind, in einer Frage, bevor weitergearbeitet wird.

**Der Anlass ist ein gemessener Defekt:** Der Aktualisierungspfad des Faktengedächtnisses entscheidet an einem reinen Zeichenkettenvergleich (`alter_wert != neuer_wert` → invalidieren). Damit nehmen zutreffende Berichtigung, Fortschreibung und Widerspruch zum eigenen früheren Wort denselben Weg — der dritte Fall überschreibt einen Triple, ohne dass irgendwo steht, dass er strittig war. Die bitemporale Maschinerie (`t_valid`, `t_invalid`, `aktiv`) könnte beide Werte halten; es fehlt das Signal.

**Zwei Tore, nicht eines.** Notwendigkeit kommt vom Objekt und der Aufgabe, Salienz vom Charakter. Ohne das erste fragt Nova nach Belanglosem, ohne das zweite nach allem Notwendigen sofort.

| ID | Inhalt | Vorbedingung |
|---|---|---|
| **KLA-K5-FAKTENPFAD** | Der Schreibpfad prüft selbst, statt an der Zeichenkette zu entscheiden — und deckt damit **beide Graphen** sowie den Aufgabenpfad ab, auf dem kein Verfasser läuft. **Am 04.08.2026 korrigiert:** Die Tabelle `fakten` hat 0 Zeilen und keinen Erzeuger; Urteil und Schreibvorgang liegen in **zwei** Graphen, korreliert nur über `turn_id`. Nicht mehr das erste Bauteil, sondern das letzte. | [WIS] **`15e`** (FaktenAgent), nicht `SYK-B1` — ⬜ **offen** — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen; der Eintrag beschreibt ein Ziel und keinen Defekt. |
| **KLA-K1-ERWARTUNGSSCHEMA** | Zu einem Objekttyp ist abrufbar, welche Eigenschaften er trägt und welche notwendig sind. Weltwissen, einmal abgelegt statt je Turn erfragt. | [WIS] keine — ⬜ **offen** — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen; der Eintrag beschreibt ein Ziel und keinen Defekt. |
| **KLA-K2-KLAERUNGSTOR** | Vergleicht erwartet gegen vorhanden und liefert beide Ausgänge — Lücke und Abweichung — aus einer Operation. | [WIS] K1, `SYK-B1` — ⬜ **offen** — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen; der Eintrag beschreibt ein Ziel und keinen Defekt. |
| **KLA-K3-SALIENZ** | Nur bedeutsamer Klärungsbedarf führt zu einer Frage. Gegenprobe: Bedeutung schlägt Charakter, sonst wird eine distanzierte Nova blind für Widersprüche. | [WIS] K2 — ⬜ **offen** — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen. |
| **KLA-K4-ZWISCHENSCHRITT** | Eine Klärungsfrage im Gesprächspfad, mit zurückgestelltem Schreibvorgang. Der Rückfrage-Fluss samt Resume existiert, hängt aber am Agentenpfad. | [WIS] K2, K3 — ⬜ **offen** — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen. |

**Offene Entwurfsentscheidung:** Auf dem Aufgabenpfad läuft der Verfasser nicht — dort gibt es kein Urteil, ausgerechnet da, wo ein Nutzer ausdrücklich etwas ändern lässt. Entweder ein reduziertes Urteil, oder die ausdrückliche Festlegung, dass von dort ungeprüft geschrieben wird.

**Verhältnis zum Sykophanz-Epic:** `SYK-B1` liefert das Urteil, das K2 für seinen Abweichungs-Ausgang braucht. Der Sykophanz-Sprint ist damit das erste Stück dieses Grundsatzes und kein eigenständiges Thema.

---


## Epic: GV4b — Agenten als Wissensquellen (Chat 71)


### Kontext

GV4 (Chat 71, Kern) durchsucht LZG und KZG nach Wissenslücken — semantisch nahe,
aber unbesprochene Konzepte. Die Relevanz wird über 6 Systeme berechnet: Gedächtnis,
Aktualität, Drive (Ziel-Gravitation), Neugier (6 EI-Säulen, sin^0.5), Register-
Kompatibilität und Charakter-Filter. Die Formel ist validiert (58-Testfälle-Matrix).

Was fehlt: Agenten-Domänen als Quellen. Timeline-Einträge, Notizen, Fakten und
autonome Wissens-Dateien enthalten Wissen, das Nova für Wissenslücken nutzen kann.
Die Agenten müssen sich selbst als Quelle anmelden und ihre eigenen Config-Werte
bereitstellen.


### Architektur: BaseAgent-Erweiterung

Neue Attribute in `server/agents/base.py` (`BaseAgent`):

| Attribut | Typ | Default | Beschreibung |
|----------|-----|---------|-------------|
| `neugier_quelle` | `bool` | `False` | Kann dieser Agent Wissenslücken liefern? |
| `neugier_config` | `dict` | `{}` | Agent-spezifische GV4-Parameter |

Neue Methode in `BaseAgent`:

```python
def neugier_suchen(
    self,
    turn_embedding: list[float],
    user_id: str,
    character_id: str,
    limit: int = 10,
) -> list[dict]:
    """Durchsucht die Domäne nach Wissenslücken.

    Returns: [{konzept, similarity, gewicht, gap_arousal, quelle, quellen_faktor}]
    """
    return []
```

Jeder Agent implementiert `neugier_suchen()` mit seiner eigenen DB-Query
(pgvector, RediSearch, Textsuche) und liefert Kandidaten mit seinem eigenen
`quellen_faktor` aus `neugier_config`.


### Agent-Registrierung (Opt-in)

| Agent | `neugier_quelle` | `quellen_faktor` | `gap_arousal_base` | Voraussetzung |
|-------|:-:|:-:|:-:|---|
| TimelineAgent | `True` | 0.7 | 0.3 | **Embedding-Nachrüstung** (s.u.) |
| NotizenAgent | `True` | 0.5 | 0.2 | **Embedding-Nachrüstung** (s.u.) |
| FaktenAgent | `True` | 0.6 | 0.3 | Fakten-Tabelle hat bereits `embedding VECTOR(768)` — sofort möglich |
| DateienAgent | `True` | 0.5 | 0.2 | `autonomous_wissen`-Tabelle (Phase 3, Pixie-Infrastruktur) |
| CharakterAgent | `False` | — | — | Keine Wissensdomäne |
| DelegationsAgent | `False` | — | — | Keine Wissensdomäne |
| RechercheAgent | `False` | — | — | Produziert Wissen, liefert es nicht |
| PromotionAgent | `False` | — | — | Infrastruktur, keine Domäne |
| DecayAgent | `False` | — | — | Infrastruktur, keine Domäne |
| WiedervorlageAgent | `False` | — | — | Trigger, keine Domäne |
| KZG-Agent | `False` | — | — | KZG ist Kern-Quelle, kein Agent-Opt-in |


### Embedding-Nachrüstung (Voraussetzung)

Zwei Tabellen haben aktuell **kein** `embedding`-Feld:

**1. Timeline:**

```sql
ALTER TABLE timeline ADD COLUMN IF NOT EXISTS embedding VECTOR(768);
CREATE INDEX IF NOT EXISTS idx_timeline_embedding
    ON timeline USING ivfflat (embedding vector_cosine_ops) WITH (lists = 20);
```

- TimelineAgent muss bei `create`, `update`, `reschedule` das Embedding aus
  `title + ' ' + COALESCE(details, '')` erzeugen.
- Einmalige Migration: Alle bestehenden Einträge embedden
  (`embedding_create(title + details, embed_client, EMBED_MODEL)`).
- `neugier_suchen()` Query: pgvector `ORDER BY embedding <=> %s LIMIT 10`
  mit Zeitfenster-Filter `WHERE event_time >= NOW() AND event_time <= NOW() + INTERVAL '{zeitfenster_h} hours'`
  (aus `neugier_config["zeitfenster_h"]`, Default 72).

**2. Notizen:**

```sql
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS embedding VECTOR(768);
CREATE INDEX IF NOT EXISTS idx_notizen_embedding
    ON notizen USING ivfflat (embedding vector_cosine_ops) WITH (lists = 20);
```

- NotizenAgent muss bei `create`, `update` das Embedding aus
  `titel + ' ' + COALESCE(inhalt, '')` erzeugen.
- Einmalige Migration analog zu Timeline.
- `neugier_suchen()` Query: pgvector `ORDER BY embedding <=> %s LIMIT 10`.

**3. Fakten:** Hat bereits `embedding VECTOR(768)` — kein ALTER TABLE nötig.
  FaktenAgent kann `neugier_suchen()` sofort implementieren.
  ~~Die Entity-Hop-ILIKE-Suche im GV-Node bleibt parallel bestehen —
  sie findet Named Entities, die pgvector-Suche findet semantische Nachbarschaft.~~

  **Zwei Behauptungen, beide widerlegt (Chat 115, 29.07.2026).** *Parallel bestehen:* Der
  GV-Node ruft `_entity_kontext_laden` nicht mehr auf; die Funktion schläft mit
  Weckbedingung im Modul, ein Test wird rot, wenn sie zurückverdrahtet wird.
  *Findet Named Entities:* Sie hat nie welche gefunden — der Suchschlüssel ist eine
  Themenphrase, die Entitätsnamen sind Eigennamen (65 von 89 einwortig), beide
  `ILIKE`-Richtungen 0 Treffer über 45 Läufe (GV-ENTITY-HOP-FINDET-NICHTS, Tür 1).
  Wer den FaktenAgent baut (M2.5b), erbt diesen Mismatch — er hängt an der Suche,
  nicht am GV-Node.

**4. Dateien:** `autonomous_wissen`-Tabelle hat bereits `themen_embedding VECTOR(768)`
  im Konzept (`novaberg-autonomous-wissen_k.md`). Wird mit Phase 3 (Pixie-Infrastruktur)
  angelegt. DateienAgent implementiert `neugier_suchen()` sobald die Tabelle existiert.


### Integration in `_wissensluecken_finden()`

Nach den Kern-Quellen (LZG + KZG) iteriert der GV-Node über die Agent-Registry:

```python
from agents import AgentRegistry

for agent in AgentRegistry.get_all():
    if agent.neugier_quelle:
        agent_kandidaten = agent.neugier_suchen(
            turn_embedding, user_id, character_id
        )
        alle_kandidaten.extend(agent_kandidaten)
```

Die Relevanz-Berechnung liest den `quellen_faktor` aus dem Kandidaten-Dict
(statt aus der zentralen Config-Variable). Kern-Quellen (LZG, KZG) setzen
weiterhin den Default `GV_QUELLEN_FAKTOR`.

```python
# Statt:
basis = k["similarity"] * k["gewicht"] * GV_QUELLEN_FAKTOR
# Jetzt:
basis = k["similarity"] * k["gewicht"] * k.get("quellen_faktor", GV_QUELLEN_FAKTOR)
```


### Reihenfolge

| Schritt | Was | Abhängigkeit |
|---------|-----|-------------|
| 1 | `BaseAgent` um `neugier_quelle`, `neugier_config`, `neugier_suchen()` erweitern | — |
| 2 | `_wissensluecken_finden()` um Agent-Registry-Loop ergänzen | Schritt 1 |
| 3 | FaktenAgent: `neugier_suchen()` implementieren | Schritt 1 (sofort, Embedding existiert) |
| 4 | Timeline: Embedding nachrüsten (ALTER TABLE + Migration + Agent-Writes) | — |
| 5 | TimelineAgent: `neugier_suchen()` implementieren | Schritt 1 + 4 |
| 6 | Notizen: Embedding nachrüsten (ALTER TABLE + Migration + Agent-Writes) | — |
| 7 | NotizenAgent: `neugier_suchen()` implementieren | Schritt 1 + 6 |
| 8 | DateienAgent: `neugier_suchen()` implementieren | Phase 3 (autonomous_wissen) |

Schritte 1–3 könnten unmittelbar nach GV4-Kern-Validierung erfolgen.
Schritte 4–7 sind unabhängig voneinander und parallelisierbar.
Schritt 8 wartet auf die Pixie-Infrastruktur (Phase 3).


### Designprinzipien

> **"Jeder Agent kennt seine Domäne."** Der GV-Node fragt nicht die Timeline-Tabelle
> direkt ab — der TimelineAgent weiß, wie seine Daten liegen und welche Filter
> (Zeitfenster, aktiv-Flag) gelten. Das ist "Separation of Concerns über Nodes"
> konsequent auf Agenten-Ebene angewendet.

> **"Die Neugier gehört Nova, die Daten gehören dem Agenten."** Der GV-Node berechnet
> die Relevanz (Neugier, Register, Charakter). Der Agent liefert die Rohdaten
> (Kandidaten mit Similarity, Gewicht, Arousal). Keine Vermischung.

> **"Config beim Agenten, nicht in der Zentrale."** Jeder Agent bringt seinen eigenen
> `quellen_faktor` und `gap_arousal_base` mit. Das vermeidet eine zentrale
> Faktor-Tabelle, die bei jedem neuen Agenten wachsen müsste.


### Priorität

Mittel. Der GV4-Kern (LZG + KZG) deckt den Hauptanwendungsfall ab. Die
Agent-Quellen erweitern die Reichweite, sind aber nicht blockierend.
FaktenAgent als erste Agent-Quelle (Embedding existiert) ist Quick Win.

---


## SPRINT-NOTIZEN-BEZUGSAUFLOESUNG — Inhalts-Aufloesung im Classify-Knoten

**Kategorie:** [WIS] WISSEN

> **Umbenannt am 25.08.2026.** Dieser Sprint trug bis dahin die Kennung `NOTIZEN-VOR-TURN-BEZUG` — dieselbe wie der Defekt, den er nur zur kleinsten Wirkstufe bearbeitet hat. **Ein Sprint und der Defekt, den er halb schliesst, sind nicht derselbe Gegenstand**, und der Defekt steht weiterhin offen unter seinem Namen.

**Status:** ✅ Abgeschlossen (Chat 80) — kleinste Wirkstufe der Bezugsauflösung

**Motivation:** NotizenAgent-Audit (Chat 80) hat strukturell belegt, dass Bezugs-Anweisungen wie *"Leg sie bitte an"* nach einem Listen-Turn nicht zuverlässig aufgelöst werden. Der Classify-Prompt verbot dem LLM explizit, den Verlauf für Inhalts-Auflösung zu nutzen — nur Target-Auflösung war erlaubt.

**Änderung:**

- Classify-Prompt-Verbot durch Erlaubnis für Inhalts-Auflösung ersetzt, Beispiel ergänzt
- Domain-Language-Block um zwei Bezugs-Beispiele erweitert
- Logging im Classify-Node: DEBUG mit `normalisiert`-Feld, INFO-Heuristik bei deutlich längerem `normalisiert` als `aufgabe`

**Geänderte Dateien:**

- `agents/notizen/klassifikation.py` (Z. 53-66, 130-138)
- `prompts/default/classify_notizen.rules.txt` (Z. 3-5)
- `prompts/default/classify_notizen.fachsprache.txt` (Z. 27-30)

**Smoke-Test (Chat 80):**

- Test A — Käse-Sorten + "Leg das bitte als Notiz an" → ✅ Inhalt korrekt aus Vor-Turn übernommen
- Test B — Bauwoche-Liste + "Schreib das auf" → ⚠️ deckte vier weitere strukturelle Schwächen auf (siehe neue Bugs unten)
- Test C — Direkt-Notiz "Notiere dir: Sonntag muss der Rasen gemäht werden" → ✅ unverändert

**Beurteilung:** Sprint-Kernziel erreicht (Test A), aber das Pattern reicht nur für **einfache Vor-Turn-Bezüge in CREATE-Aktionen**. Für mehrschrittige Kontext-Rekonstruktion in UPDATE/RENAME-Pfaden ist die strukturelle Lösung das Frame-Konzept Phase 1b.

**Verbindung zum Frame-Konzept:** Dieser Sprint ist die kleinste Wirkstufe. Das umfassendere Konzept (`novaberg-thinking-frames_k.md`) generalisiert das Pattern auf strukturierte Slot-Erhebung mit Vor-Wissen-Rekonstruktion und Skill-Bewusstsein.

---


## SPRINT-M25A-TIMELINE-CLEANUP — der TimelineAgent verliert seinen Manager ✅

**Kategorie:** [WIS] WISSEN

**Status:** ✅ Abgeschlossen (Chat 80) — Audit (Chat 78), Implementierung in zwei Phasen (Chat 80)

**Hintergrund:** Ursprünglich gedacht als TimelineAgent-Migration auf das NotizenAgent-Pattern. Audit in Chat 78 zeigt: der Subgraph ist bereits sauber, Search-vor-Execute korrekt verdrahtet seit Chat 27. Manager-Schreibpfade (`plan()`, `execute()` plus Hilfsfunktionen) sind tot — sie werden nicht mehr aufgerufen, seit der TimelineAgent in der Registry ist.

**Reduzierter Scope:**

1. Tote Manager-Schreibpfade in `plugins/timeline_manager/manager.py` löschen (`plan()`, `execute()`, `termin_verarbeiten`, `_termin_create`, `_termin_delete`, `_termin_update`, `_termin_query`).
2. Manager schrumpft auf Lese-Schicht: `enrich_entries()` und `_termin_zu_entry()` bleiben.
3. `themen`-Befüllung beim Schreiben in `agents/timeline/crud.py` (Create und Update). Variante in M2.5a zunächst: `ARRAY[event_type]`. Reichere thematische Anreicherung (kategorische Map über Entitäten) bleibt M3-Scope.
4. Drei Verhaltens-Flags (`binding`, `remind`, `conflict_check`) beim Schreiben aus `event_type` ableiten:
   - `termin`/`deadline` → alle drei TRUE
   - `geburtstag`/`jahrestag`/`erinnerung` → nur `remind=TRUE`

**Vorbedingung:** THINK-TRANSITION-INFO muss vorher ausgerollt sein, sonst stoßen die M2.5a-Smoke-Tests auf den THINK-MEM-CONFLICT-Bug.

**Vorbehalt zum Pattern-Vorbild:** Der NotizenAgent dient als Vorbild. Meister sieht aber noch Schwächen im NotizenAgent, die in Chat 79 ausformuliert werden müssen vor Pattern-Übertragung. Die `themen`-Befüllung sollte beim NotizenAgent gleichgezogen werden.

**Ergebnis (Chat 80):**

- **Phase 1 — Audit (read-only):** Bestätigt, dass `plan()`, `execute()`, `termin_verarbeiten()`, `_termin_create/_delete/_update/_query()` toter Code sind. Planner short-circuited via `AgentRegistry.finden("timeline")` vor `plan()`-Aufruf, kein Producer erzeugt `ziel="timeline"`-Writes für den Dispatcher.
- **Phase 2 — Cleanup + Magnet-Befüllung:**
  - 703 Zeilen tote Schreibpfade aus `manager.py` entfernt (960 → 257 Zeilen), 7 Imports entfernt.
  - `BaseManager.execute()` ist `@abstractmethod` ohne Default — `TimelineManager.execute()` bleibt als Loud-Failure-Stub mit `NotImplementedError`, voller Diagnose im Text.
  - Neuer Helper `agents/timeline/magneten.py` als Single Source of Truth für `event_type → (themen, binding, remind, conflict_check)`.
  - `TimelineRepository.insert()` erweitert um vier Magnet-Parameter.
  - `crud.py:_create` und `_update` rufen den Helper, reichen Werte durch.
- **Smoke-Test grün:** Termin → `(termin, T, T, T)`, Geburtstag → `(geburtstag, F, T, F)`. Erwartung erfüllt.
- **10 Minuten Server-Lauf nach Restart ohne einen einzigen `NotImplementedError`** — empirische Bestätigung, dass kein Producer mehr `ziel="timeline"` schreibt.

**Befunde fürs nächste Mal:** Migrations-Buckets in `agents/timeline/init.sql` und Helper-Mapping müssen langfristig konsistent gehalten werden — separater Sprint, nicht in M2.5a-Scope. `event_ende` und `recurring` werden nirgends ausgewertet, beides bleibt für spätere Sprints.

**Folge-Sprints:**

- M2.5a-PRECISION (`precision`-Erweiterung auf `hour`/`month`/`quarter`/`year`, abhängig von Zeitparser-Erweiterung)
- M2.5b (FaktenAgent neu anlegen)

---


## Bug: TIMELINE-PAIR-MISSING — Timeline-Tabelle ohne `character_id` (Chat 80)

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Am Schema bestaetigt: `timeline` traegt weiterhin **kein** `character_id`. **Dieselbe Kennung steht auch im Defektregister.**

**Entdeckt:** Chat 80
**Klasse:** Schema-Lücke, paar-spezifisches Wissen leakt zwischen Charakteren
**Severity:** Mittel — relevant erst bei Multi-Charakter-Setup, aber Foundation-Bug

**Beschreibung:**

Die Tabelle `timeline` hat heute nur `user_id`, kein `character_id`. Das verletzt:

- `novaberg-convention-paar-schema.md` — Subjekt × Gegenüber × Beobachter, Erlebnis-Wissen ist paar-spezifisch
- `novaberg-convention-magneten.md` §6 — Welt-Wissen vs. Erlebnis-Wissen, Timeline gehört zu Erlebnis (`(user_id, character_id)`-Skopierung)

Bei Multi-Charakter-Setup würden Aria-Termine bei Nova auftauchen (und umgekehrt). Heute kein praktisches Problem (Nur Nova), aber jeder neue Charakter bringt Wissens-Leck mit.

**Vermutung:** Andere paar-skopierte Speicher haben dieselbe Lücke. Geprüft (Chat 74) und sauber: KZG (im Redis-Schlüssel), `charakter_hash` (Composite PK). Ungeprüft: `langzeitgedaechtnis`, `notizen`, `fakten`, `dateien`.

**Lösung — zwei Sprints:**

1. **Inventur-Sprint TIMELINE-PAIR-INVENTUR:** `\d` auf alle paar-skopierten Speicher, prüfen wo `character_id` fehlt. Erwarteter Aufwand: 5-10 Minuten Read-only, ein kurzer Brudi-Prompt.
2. **Migrations-Sprint TIMELINE-PAIR-MIGRATION:** `character_id`-Spalte ergänzen wo nötig, Indexe anpassen, Repositories und Schreibpfade durchziehen, Bestand initialisieren (alle alten Einträge bekommen `character_id='nova'`).

**Eingeordnet:** Inventur-Sprint nach M2.5a (jetzt). Migrations-Sprint wahrscheinlich nach M3, abhängig vom Inventur-Befund.

---


## Bug: NOTIZEN-PAIR-MISSING — Notizen-Tabelle ohne `character_id` (Chat 80)

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Am Schema bestaetigt: `notizen` traegt weiterhin **kein** `character_id`. **Dieselbe Kennung steht auch im Defektregister.**

**Entdeckt:** Chat 80 (Audit zur character_id-Inventur)
**Klasse:** Schema-Lücke, paar-spezifisches Wissen leakt zwischen Charakteren
**Severity:** Mittel — relevant erst bei Multi-Charakter-Setup, aber Foundation-Bug

**Symptom:** Tabelle `notizen` hat nur `user_id`, kein `character_id`. Repository-Pfade filtern nur `WHERE user_id = %s`. Bei Multi-Charakter-Setup würden Aria-Notizen bei Nova auftauchen und umgekehrt.

**Klasse:** Identisch zu TIMELINE-PAIR-MISSING (Chat 80) und FAKTEN-PAIR-IGNORED (Chat 80) — alle drei sind Symptome derselben fehlenden Paar-Skopierung in Erlebnis-Wissens-Speichern. Verletzt `novaberg-convention-paar-schema.md` und `novaberg-convention-magneten.md` §6.

**Lösung:** Gemeinsamer Migrations-Sprint für alle drei Tabellen (Timeline, Notizen, Fakten). Bei Notizen ist die Migration einfach (1 Bestandseintrag, alle bekommen `character_id='nova'`).

---


## Bug: FAKTEN-PAIR-IGNORED — Fakten-Repository ignoriert `character_id`-Spalte (Chat 80)

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Am Schema bestaetigt: Die Spalte ist da, das Repository liest sie nicht — und die Tabelle traegt **0 Zeilen**, die im Befund genannten 171 gibt es nicht mehr. **Dieselbe Kennung steht auch im Defektregister.**

**Entdeckt:** Chat 80 (Audit zur character_id-Inventur)
**Klasse:** Repository-Lücke trotz vorhandener Schema-Spalte
**Severity:** Hoch — 171 Live-Einträge unter `user_id='nova'` betroffen

**Symptom:** Tabelle `fakten` hat die Spalte `character_id` mit Default `'nova'`. INSERTs in `fakten_repository.py` setzen die Spalte nicht — sie wird durch den DB-Default befüllt. SELECTs filtern nur `WHERE user_id = %s`, ignorieren `character_id` komplett.

**Komplikation — ASSISTANT_USER_ID-Pfad:** 171 Fakten-Einträge stehen heute unter `user_id='nova'` (Pre-Paar-Schema-Logik). Diese können bei einer Migration nicht pauschal auf `character_id='nova'` umgesattelt werden — sie repräsentieren *"Nova-Sicht auf Meister"* und gehören semantisch zu `(user_id='meister', character_id='nova', beobachter='assistant')`. Migration ist nicht trivial und braucht eine Heuristik.

**Lösung:** Konzept-Dokument für die Migration zuerst, dann Sprint. Konzept klärt: Spalten-Migration, Repository-Anpassung, Daten-Migration mit ASSISTANT_USER_ID-Umsattelung.

---


## Bug: ZIELE-PAIR-MISSING — Ziele-Tabelle ohne `character_id` (Chat 80)

**Kategorie:** [WIS] WISSEN

**Zustand:** abgeschlossen — am Schema geprueft am 25.08.2026. `ziele` traegt `character_id`. **Dieselbe Kennung steht auch im Defektregister und ist dort ebenfalls geschlossen.**

**Entdeckt:** Chat 80 (Audit zur character_id-Inventur)
**Klasse:** Schema-Lücke + offene Skopierungs-Frage
**Severity:** Niedrig — heute kein Live-Problem, aber Foundation-Bug

**Symptom:** Tabelle `ziele` hat `user_id` mit Default `'nova'` und kein `character_id`. Wirkt wie pro-User-global. 9 Bestandseinträge, alle unter `user_id='nova'`.

**Offene Frage:** Sind Ziele charakter-spezifisch (Nova hat andere Ziele als Aria hätte)? Drive-Konzept (`thinking-drive_k.md`) suggeriert ja — aber explizite Festlegung fehlt.

**Lösung:** Im Migrations-Konzept zusammen mit den anderen Paar-Lücken klären. Falls charakter-spezifisch: Spalte hinzufügen, Repositories anpassen.

---


## Bug: NOTIZEN-KONTEXT-REKONSTRUKTION — Mehrschritt-Rekonstruktion fehlt (Chat 80)

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

**Entdeckt:** Chat 80 (Live-Test B des NOTIZEN-VOR-TURN-BEZUG-Sprints)
**Klasse:** Strukturelle Lücke — Bezugsauflösung über mehrere Vor-Turns hinweg
**Severity:** Hoch — eingeschränkte Konversationsfähigkeit

**Symptom:** Bei UPDATE/RENAME-Aktionen mit mehreren Bezugs-Pronomen über mehrere Turns scheitert die Rekonstruktion.

**Konkreter Fall (Chat 80):**

- Turn n-3: User: *"Bei der nächsten Bauwoche brauche ich noch: Bohrer, Schrauben, Dübel."*
- Turn n-1: Notiz "Marketing-Aktion beim Obi" wurde angelegt
- Turn n: User: *"Und schreibe die 3 Sachen in die Liste, die ich erwähnt habe"*
- Nova: *"Welche drei Sachen?"* — obwohl die drei Sachen drei Turns davor explizit aufgezählt wurden

**Erwartete Kette:** *"Aktualisiere sie"* → Was könnte ich aktualisieren? → Hier, wir haben über eine Liste gesprochen → Die Liste betrifft Baumarkt-Wochen → Der Nutzer hat 3 Dinge erwähnt, die gehören wohl dazu → Container-Typ ändern + Inhalte einfügen.

**Was heute fehlt:** Der Classify-Node hat zwar Vor-Turns im `[KONTEXT]`-Block, aber keinen Mechanismus für **mehrschrittige semantische Kette** über Turn-Distanzen >1. Die Inhalts-Auflösung aus dem heutigen Sprint deckt nur einen Vor-Turn-Sprung ab, keine Kette.

**Strukturelle Lösung:** Frame-Konzept Phase 1b. Der Frame-Auflöser-Node (`thinking-frames_k.md` §7) ist genau für diese mehrschrittige Rekonstruktion gebaut — Slot für Slot prüfen, jeden Slot aus dem passenden Vor-Turn füllen, dann CRUD ausführen.

---


## Bug: NOTIZEN-CONTAINER-WECHSEL — Notiz↔Liste-Wechsel verweigert (Chat 80)

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen.

**Entdeckt:** Chat 80 (Live-Test B)
**Klasse:** Architektur-Strenge zu hoch — Container-Typ als unveränderliche Klasse
**Severity:** Mittel — eingeschränkte Funktionalität, aber kein Daten-Verlust

**Symptom:** NotizenAgent trennt "Textnotiz" und "Liste" als harte Klassen. Eine als Textnotiz angelegte Notiz kann nicht zu einer Liste mit Items erweitert werden, obwohl semantisch sinnvoll.

**Konkreter Fall (Chat 80):**

- Notiz "Marketing-Aktion beim Obi" wurde als Textnotiz angelegt
- User wollte Items hinzufügen: Bohrer, Schrauben, Dübel
- Nova: *"Die Notiz zur Marketing-Aktion ist eine einzelne Notiz und keine Liste, in die man Unterpunkte einfügen kann. Das System unterscheidet hier strikt zwischen einer Textnotiz und einer strukturierten Liste."*

**Was heute fehlt:** Container-Typ als änderbare Eigenschaft. Korrekte Aktion: Bei `add_content` auf Textnotiz mit mehreren Items → Container-Typ-Wechsel zu Liste, Items strukturieren.

**Strukturelle Lösung:** Frame-Konzept Phase 1b. Ein `notiz_update`-Frame hätte Slot `neuer_typ`, der explizit den Container-Wechsel als legitime Aktion definiert.

---


## Bug: NOTIZEN-SKILL-MANIFEST — Nova kennt eigene Fähigkeiten nicht in der Sprach-Schicht (Chat 80)

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen.

**Entdeckt:** Chat 80 (Live-Test B, durch Meister thematisiert)
**Klasse:** Domain-Language-Lücke — Skills im Code vorhanden, in der Sprach-Schicht nicht repräsentiert
**Severity:** Mittel — falsche Selbstauskunft an User

**Symptom:** Nova verweigert legitime Aktionen mit Begründungen, die im Code so nicht stimmen. Sie kennt ihre eigenen Skills nicht in dem Sinne, dass sie sie **erklären oder anbieten** kann. Wenn sie sagt *"eine Notiz und keine Liste"*, zieht sie eine harte Grenze, die im Code gar nicht so hart ist.

**Erwartung:** Nova sollte ihre Skills wie ein Butler kennen. *"Ich kann für Sie Listen erstellen, Notizen erstellen, das eine zum anderen abändern, Inhalte anhängen oder entfernen, umbenennen, leeren..."*. Pattern-Idee: Agent registriert sich beim Planner mit einer Skill-Beschreibung, die in der Sprach-Schicht verfügbar ist und Nova in Erklärungen nutzen kann.

**Strukturelle Lösung:** Frame-Konzept Phase 1b implizit. Frames definieren legitime Aktionen pro Domäne — wenn `notiz_update` einen Slot `neuer_typ` hat, ist Container-Wechsel automatisch eine bekannte Skill. Frame-Lager (§11) wird zur **Skill-Selbstkenntnis**: Nova kann anhand vergangener Frames erklären, was sie kann.

**Hinweis:** Falls dieser Punkt schneller adressiert werden soll, wäre ein kleiner Skill-Manifest-Sprint möglich — Domain-Language-Datei um die fehlenden Aktionen ergänzen. Wurde in Chat 80 bewusst gegen die strukturelle Lösung verworfen.

---


## Bug: NOTIZEN-UPDATE-TARGET-LEER — Bezugs-Pronomen für UPDATE/RENAME crashen (Chat 80)

**Kategorie:** [WIS] WISSEN

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

**Entdeckt:** Chat 80 (Live-Test B)
**Klasse:** Bezugsauflösung im UPDATE-Pfad — verwandt zu NOTIZEN-VOR-TURN-BEZUG, aber andere Aktion
**Severity:** Hoch — Crash-Verhalten

**Symptom:** Bei UPDATE/RENAME-Aktionen mit Bezugs-Pronomen (*"Aktualisiere sie"*) wird `target` leer übergeben. Crash mit *"keine Notiz mit Namen ''"*.

**Konkreter Fall (Chat 80):**

- Notiz im Vor-Turn: *"Neue Notiz anlegen"* — Nova hatte explizit darauf verwiesen
- User: *"Aktualisiere sie"*
- NotizenAgent crash: *"Es gab ein Problem beim Agenten 'notizen', da keine Notiz mit dem Namen '' gefunden werden konnte"*

**Was heute fehlt:** Der heutige Sprint NOTIZEN-VOR-TURN-BEZUG hat das Verbot nur für CREATE im Classify-Prompt aufgehoben (Inhalts-Auflösung). Der UPDATE-Pfad hat eine ähnliche Lücke: das `target`-Feld wird nicht aus Vor-Turns aufgelöst, wenn der User ein Bezugs-Pronomen verwendet.

**Strukturelle Lösung:** Frame-Konzept Phase 1b. Frame-Auflöser löst Slots wie `target` deterministisch aus dem Vor-Turn-Kontext auf. Pattern identisch zur Inhalts-Auflösung, nur in anderem Slot.

---




> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Wissen**. Ueberschrift und Text stehen in jeder empfangenden Datei.
**Kategorie:** [GED] GEDAECHTNIS

**Status:** ⬜ Strukturell offen, größtenteils mit P9-Löschung erledigt
**Prio:** Niedrig
**Auslöser:** PromotionAgent-Audit 1 (Chat 91)

Sieben Beifang-Punkte aus dem Audit-Sweep, die nicht zur P4-Klärung beitrugen, aber dokumentiert sein müssen:

| # | Beobachtung | Schicksal nach P9 |
|---|---|---|
| FAKTEN-TABELLE-ENTITY-MERGE | `fakten`-Tabellen-Konsistenz bei Entity-Merge — `entitaeten.id` wird sowohl in `lzg_knoten.entitaet_ids` als auch in `fakten`-Tripeln referenziert, aber Konsistenz-Pflege bei Merge nur für `lzg_kanten` definiert. | [WIS] Eigenes Faktengedächtnis-Konzept — ⬜ **offen** — nachgesehen am 25.08.2026. Gegenstandslos, solange `fakten` 0 Zeilen traegt. |
| TIMELINE-FK-DOKU-DRIFT | Konzept §4.1 listet `timeline_id INTEGER REFERENCES timeline(id) ON DELETE SET NULL`, Live `init.sql` hat bare INTEGER ohne FK (FK lebt in `agents/timeline/init.sql`). Funktional gleichwertig, dokumentarisch abweichend. | [WIS] Doku-Sync mit TIMELINE-IN-KERN — ⬜ **offen** — nachgesehen am 25.08.2026. Die Doku-Drift ist nicht nachgezogen. |

**Empfehlung:** Liste als Beobachtungs-Anker erhalten. Sechs der sieben Punkte sind entweder mit P9-Löschung erledigt oder in Folge-Sprints (P5, Faktengedächtnis, TIMELINE-IN-KERN) integriert. `REFAC-MAGNETE-AUDIT` als eigenständiger kleiner Sprint übrig.

---
