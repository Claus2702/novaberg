# Novaberg — Backlog: Bauart — Code, Schema, Werkzeug, Tests, Doku, Register

**Inhalt:** die offene und abgeschlossene Arbeit dieses Gegenstands, 97 Eintraege.
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

## Block 25.08.2026 — das Gate, das die Protokollpflicht bewacht, gibt es nicht

**`18_NACHVOLLZIEHBARKEIT.md` §7 ist seit seiner Markierung als maschinell pruefbar gefuehrt und nie gebaut worden.** Nach `01_LESSON_UEBERNAHME.md` §6 gehoert zu jedem markierten Gate ein Backlog-Eintrag; fuer dieses gab es keinen — bemerkt beim Abgleich des Verlaufs gegen die Speicher am 25.08.2026.

| Kennung | Was offen ist | Band |
|---|---|---|
| `PROTOKOLLPFLICHT-OHNE-GATE` | **Kein Werkzeug prueft, ob ein Knoten seinen Ein- und Ausgang protokolliert und eine Weiche ihre Entscheidungsgroessen.** Die Regel steht seit dem 25.08.2026 als `F-LOG-3` und inhaltlich laenger in `18_NACHVOLLZIEHBARKEIT.md` §3; das Gate aus §7 fehlt. **Der Anlass ist gemessen:** Am 25.08.2026 riss ein Fehler in einem Nachlaufknoten den CharakterGraphen, und hinterher war nicht feststellbar, welcher Wert gefehlt hatte — die Weiche `_after_evaluate` las drei Eingangsgroessen mit Indexzugriff und protokollierte keine davon, die Zustellzeile meldete `342 Zeichen, 2 Clients`. **Drei Luecken sind von Hand geschlossen, das Gate fehlt weiter** — und damit ist die Regel eine Verabredung, keine Zusicherung. **Was fertig waere:** eine Pruefung ueber die Knotenfunktionen des Graphen, die eine Funktion ohne Eingangs- oder Ausgangszeile meldet, dazu eine ueber die Weichen, die einen Indexzugriff auf eine Entscheidungsgroesse findet. **Der Ausloesefall gehoert dazu:** Ein Knoten, dem man die Ausgangszeile nimmt, muss gemeldet werden — ohne ihn ist ein schweigender Scan von einem sauberen Bestand nicht zu unterscheiden. **Vorarbeit liegt vor:** Eine Handmessung am 25.08.2026 ueber die Einstiegsfunktionen ergab **2 von 19** ohne Ein- und Ausgang (`enricher`, `tribunal`), mit bekannter Unschaerfe — beide loggen in Unterfunktionen, und drei weitere Knoten waren so nicht messbar. **Die Zahl ist eine Untergrenze und ersetzt das Gate nicht.** | [BAU] ungebaendigt |

---

## Block 19.08.2026 — die Rollen eines Wissen-Silos

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Bauart**. Ueberschrift und Text stehen in jeder empfangenden Datei.

**Der Anlass ist eine Matrix, keine Wunschliste.** Am 19.08.2026 gezählt trägt von neun Silos **genau eines alle drei Rollen** (Timeline: Quelle, Zettel, Werkzeug). Das Web ist der Spiegelfall — Werkzeug ohne Quelle, weil es keine sein kann. Und das am schlechtesten angebundene Silo ist ihr **eigenes erarbeitetes Wissen**: eine Rolle von dreien.

| Kennung | Was offen ist | Band |
|---|---|---|
| ~~`WISSEN-OHNE-ZETTEL`~~ **— geschlossen am 19.08.2026.** Zettel (`plugins/wissen_manager/manager.py::router_prompt`) und Dienst (`agents/wissen/`) stehen, 26 Zeugen; **zwei echte Turns** routen dorthin (12:41 und 12:43 UTC), einer in den vierten Ausgang, einer abgeschlossen. Die Abfrage ist **eine** für beide Eingänge (§6a.1, `AutonomousWissenRepository.suchen`); der Eingang wählt nur die Tiefe. **Als Rest benannt:** die Tiefe bleibt Stufe 1 — Thema und Zusammenfassung, nicht der Wortlaut (`WIS-8-STUFE-2`), und der Dienst sagt es in seiner `grenze`. **Und der vierte Ausgang hat im ersten Lauf einen Befund geliefert:** die Schwelle trennt an diesem Korpus nicht (siehe `WIS-SCHWELLE-MESSEN`). Ursprünglicher Wortlaut: **Ihre Bibliothek ist angebunden wie ihr Gedächtnis, nicht wie eine Quelle.** `wissen_manager` trägt `immer_aktiv` und **keinen** `router_prompt` — sie fließt bei jedem Turn in den Kontext, und niemand kann sie **bestellen**: weder der Mensch (*„Was hast du selbst dazu erarbeitet?"*) noch sie selbst. Für die freigegebenen Dateien wurde der Zettel am 18.08. gebaut, für ihr eigenes Wissen nicht. **Was fertig wäre:** ein Aushang nach `novaberg-convention-nmcp.md` §3 mit Negativfällen gegen **drei** Nachbarn — `dateien` (fremde Unterlagen), `kzg` (Erinnerung an ein Gespräch), `recherche` (was sie noch nicht weiß) —, ein Dienst dahinter, der den vierten Ausgang bedient, und ein echter Turn, der eine Frage nach ihrem eigenen Wissen dorthin routet. **Vorbedingung erfüllt:** §6a der Konvention steht seit dem 19.08. und ist vor diesem Bau geschrieben. | ungebändigt |
| `ROLLENMATRIX-OHNE-PRUEFUNG` | ⚠ **Neu bewertet am 19.08.2026 — das in §9 genannte Kriterium ist falsch, und wer die Prüfung wie beschrieben baut, zählt schweigend daneben.** §9 nennt `immer_aktiv` für die Rolle *Quelle*. Der Enricher ruft `enrich_entries` aber bei **jedem** Manager (`graph/nodes/enricher.py`), gleich was `immer_aktiv` sagt — die Eigenschaft steuert den **Schreibpfad** (`BaseManager`: *„False = nur bei pending_writes"*). Maschinell gezählt über 10 Silos: **§9 ergibt 3 Quellen, der Enricher 4**, und die beiden gehen bei **zwei** Silos auseinander — `kzg` (`immer_aktiv`, kein eigenes `enrich_entries`; sein Beitrag ist im Dispatcher-Knoten verdrahtet) und `timeline` (kein `immer_aktiv`, eigenes `enrich_entries`). **Ausgerechnet `timeline` ist der einzige Silo mit allen drei Rollen** — nach §9 hätte die Prüfung ihn als 2/3 gemeldet. Vor dem Bau ist deshalb §9 zu berichtigen. Dazu ein dritter Zustand, den die Matrix heute nicht kennt: `fakten` hat ein eigenes `enrich_entries` und ist im Enricher **abgeschaltet** — mit `continue` uebersprungen, begruendet im Code mit *„produziert 130+ Rausch-Eintraege"* — gebaut und stillgelegt ist weder *ja* noch *nein*. Ursprünglicher Wortlaut: **Die Matrix ist maschinell prüfbar und wird heute von Hand gezählt.** `novaberg-convention-nmcp.md` §9 führt sie als Startprüfung: je Silo die drei Rollen zählen — Quelle über `immer_aktiv`, Zettel über `router_prompt`, Werkzeug über den Werkzeugkasten des Denkknotens — und **jede leere Zelle ohne Begründung am Silo melden**. **Meldung, keine Verweigerung:** Eine fehlende Rolle kann richtig sein (das Gedächtnis hat zu Recht keinen Zettel), aber nicht unbemerkt. **Was fertig wäre:** die Prüfung im Handshake, ihre Ausgabe im Startlog, und der Nachweis an einem hergestellten Fall — ein Silo, dem man den Zettel wegnimmt, muss gemeldet werden. Ohne diesen Auslösefall ist ein schweigender Scan von einem sauberen Bestand nicht zu unterscheiden. | [BAU] ungebändigt |

---


## Block 19.08.2026 — der Antwortpfad meldet seinen Verlust und behebt ihn nicht

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Bauart**. Ueberschrift und Text stehen in jeder empfangenden Datei.

| Kennung | Was offen ist | Band |
|---|---|---|
| ~~`OLLAMA-VERSION-VIER-MONATE-ALT`~~ | **✅ Erledigt am 19.08.2026 — 0.32.14 läuft.** Ursprünglicher Befund: **Die Laufzeit ist zwölf Minor-Versionen alt, und vier Release-Einträge treffen die Kombination, die in jedem Gesprächsknoten läuft.** Installiert ist **0.20.7** (Binärdatei vom 14.04.2026), verfügbar **v0.32.14** (15.08.2026). Einschlägig: v0.21.1 *„Fixed structured outputs for Gemma 4 when `think=false`"* (22.04. — **acht Tage nach der installierten Fassung**), v0.22.1 *„Updated the Gemma 4 **renderer**"*, v0.30.9 *„Fixed LFM2 **parser/render** for cases where thinking was not emitted"*, v0.31.2 *„Fixed structured output for thinking models when thinking is disabled"*. Dazu v0.32.3 *„Fixed GLM tool calls being **silently dropped** at the end of generation"* — dieselbe Fehlerklasse wie `RESPONDER-LEERE-ANTWORT-STILL`. **Alle 14 JSON-erwartenden Aufrufer laufen mit `think=False`.** **Einschränkung, gemessen:** Der Bestand sendet **kein** `format`-Feld; „structured outputs" meint bei Ollama genau das, `expect_json` parst clientseitig. v0.21.1 trifft den Pfad also nicht so, wie der Eintrag ihn beschreibt — Renderer und Parser bleiben einschlägig. **Was fertig wäre:** Update eingespielt, beide Dienste neu gestartet, die selbstgebauten Modelfiles laden, und dieselbe Erhebung wie vorher gelaufen. **Die Nulllinie ist erhoben** (31 h Betrieb, 319.267 Zeilen): JSON-Quoten 2,2 % / 2,7 % / 1,6 %, vier Leerantworten, 150× `done_reason='stop'`, belegte Kanäle ausschließlich `['content']`, Antwortlängen-Mediane je Aufrufer. **Zu entscheiden, nicht zu bauen:** ob das Modellverzeichnis (42 GB) vorher gesichert wird — neuere Fassungen schreiben gelegentlich das Manifest-Format um, und dann ist der Rückweg auf die alte Binärdatei nicht sauber. ~~**Der Rückweg sonst:** ein `cp` und zwei Neustarts~~ — **beim Ausführen widerlegt.** **Erledigt am 19.08.2026: 0.32.14 läuft auf beiden Instanzen.** Suite `Ran 1965 tests — OK`, echter Turn zugestellt, alle fünf Modelle mit **unveränderten Digests** — das Manifest-Format wurde nicht umgeschrieben, die 42-GB-Frage ist damit im Nachhinein beantwortet. Gesichert wurde trotzdem, und anders als geplant: Manifeste als echte Kopie (20 KB), **Blobs als harte Links** (42 GB zu null Platz, Linkzahl 2 geprüft). **Zwei Angaben dieses Eintrags trugen nicht:** Der Rückweg ist nicht *ein `cp`* — neben der 43-MB-Binärdatei liegen **7,2 GB Laufzeitbibliotheken** in `/usr/local/lib/ollama`, die dasselbe Archiv ersetzt, und eine alte Binärdatei gegen neue Runner ist keine ausgelieferte Kombination. Und die Nulllinie ist **nicht** unverändert wiederholbar: Das Log des Server-Containers ist kumulativ, 129 neue Zeilen gegen 325.987. Die Erhebung braucht deshalb ein **absolutes** Zeitfenster mit Zonenkennung; ein relatives greift auf den vorigen Lauf über. **Was der Wechsel nicht bringt:** Er erklärt `RESPONDER-LEERE-ANTWORT-STILL` nicht — dazu siehe dort. | [BAU] ungebändigt |
| `ANBIETER-FELDER-UNGELESEN` | **Der Anbieter liefert zwölf Felder, der Bestand liest drei.** Gezählt am 19.08.2026 aus der Schlüsselliste einer echten Antwort: `created_at`, `done`, `done_reason`, `eval_count`, `eval_duration`, `load_duration`, `logprobs`, `message`, `model`, `prompt_eval_count`, `prompt_eval_duration`, `total_duration`. Gelesen wurden `prompt_eval_count`, `eval_count` und `message`; seit dem 19.08. steht der ganze Umschlag im Protokoll, **verarbeitet** wird weiterhin nichts davon. **Der Verlust ist nicht theoretisch:** `done_reason` hätte einen offenen Defekt aufklären können und war vier Wochen lang da. **Was fertig wäre:** je Feld eine Entscheidung — gelesen und wohin, oder begründet verworfen. Die Dauern (`eval_duration`, `load_duration`, `total_duration`) sind dabei der billigste Gewinn: Sie trennen Wartezeit am Modell von Wartezeit im Graphen, und diese Trennung wird heute aus Zeitstempeln erschlossen. | [BAU] ungebändigt — ⬜ **offen** — nachgesehen am 25.08.2026. `eval_duration` und die uebrigen Dauern kommen im ganzen Baum nicht vor. Gegen HEAD `599c19b` geprueft. |

---


## Block 16.08.2026 — die Gegenrichtung der Doku-Pruefung

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Bauart**. Ueberschrift und Text stehen in jeder empfangenden Datei.

| Kennung | Was offen ist | Band |
|---|---|---|
| `KANAL-OHNE-GEGENSTUECK` | **Das vierte Kriterium: nicht vom Dokument zum Code, sondern vom Code zum Leser.** Die drei Kriterien vom 16.08.2026 prüfen, ob ein im Dokument genannter Name einen Gegenstand im Code hat. Sie können die umgekehrte Klasse **prinzipiell nicht finden**: ein Bauteil, das gebaut ist und das niemand liest. **Der Zuschnitt ist mechanisch:** je State-Kanal und je persistiertem Feld die Menge der **Schreiber** und die Menge der **Leser** aus dem Baum ableiten; ausgegeben wird, wie viele nur eine Seite haben. Ein Kanal mit Schreibern und ohne Leser ist tote Rechenarbeit, einer mit Lesern und ohne Schreiber ein Vorgabewert, der wie eine Messung aussieht. **Die Klasse ist belegt, nicht vermutet:** `einwandsurteil` steht als Kanal ohne Leser in der Fundliste; am 15.08.2026 fand die zweite Kontrolle einen Router, der einen neu eingeführten Wert nur **verglich**, worauf kein einziger Auftrag mehr lief — bei 1404 grünen Tests; und am selben Tag einen zweiten Erzeuger desselben Payload-Feldes, dessen Ausfall sich als korrekte Meldung getarnt hätte. **Was es zusätzlich fände:** die Nähte zwischen Modulen — nicht ob eine Funktion existiert, sondern ob das, was sie schreibt, hinten ankommt. | [BAU] ungebändigt — ⬜ **offen** — nachgesehen am 25.08.2026. Das vierte Kriterium ist nicht als Werkzeug entstanden. |
| `NAMENSREGELN-JENSEITS-DER-FORM` | **Die harte `N`-Familie deckt die Namens*form* ab, nicht die Namens*wahl*.** `ruff --select N` läuft am 16.08.2026 sauber über `server/` — snake_case, CamelCase, keine Builtin-Schatten. Ungeprüft bleibt, was darüber hinaus gilt: die Sprachtrennung zwischen Code und Log, die Behandlung feststehender Fachbegriffe der Domäne, und die Regel, dass eine Zeichenkette als Statuswert oder Klassifikationslabel eine geschlossene Aufzählung braucht. **Für die letzte gibt es einen Ansatz:** Zeichenketten-Literale, die in einem Vergleich gegen ein Statusfeld stehen, sind auffindbar — und eine, die in keiner Aufzählung vorkommt, ist der Kandidat. **Nicht mitgemacht:** Die beiden ersten Regeln sind vermutlich nicht mechanisch prüfbar; das gehört dann als Grenze benannt statt als Aufgabe geführt. | [BAU] ungebändigt — ⬜ **offen** — nachgesehen am 25.08.2026. Die Namenswahl ist weiterhin nicht pruefbar. |

---


## Block 16.08.2026 — aus dem Halten der Konventionen

| Kennung | Was offen ist | Band |
|---|---|---|
| `PENDING-AGENT-INS-PAYLOAD` | **`novaberg-convention-event-model.md` §9.3 beschreibt eine Migration, die nicht stattgefunden hat.** Der Wartezustand eines Agenten sollte vom Redis-Schlüssel `pending_agent:{user_id}` ins Event-Payload wandern; das Ereignis `awaiting_user` trüge den Kontext, das nächste Nutzer-Ereignis löste den Resume aus. **Der Schlüssel ist weiterhin der Träger und tief verdrahtet:** acht Dateien lesen oder setzen ihn — `graph/nodes/planner.py`, `graph/nodes/router.py`, `services/event_consumer.py`, `services/shadow_delivery.py` und die Dispatches von vier Agenten. **Der Satz stand im Präsens** und las sich wie eine Beschreibung; er ist im Dokument jetzt als Absicht markiert. Was ihn wichtig macht: Der Schlüssel ist paar-blind (`{user_id}` ohne `character_id`) und überdauert den Turn, während das Payload beides mitbrächte. | [BAU] ungebändigt — ⬜ **offen** — nachgesehen am 25.08.2026. Die beschriebene Migration hat nicht stattgefunden. |
| `SSE-REST-IM-ENDPUNKT` | **Schritt 7 der Migration ist als erledigt vermerkt, der Server-Pfad daneben nicht.** *Client auf WebSocket-only umstellen* ✅ (01.08.2026) — aber `api/chat.py` liefert weiterhin eine `StreamingResponse` mit `media_type="text/event-stream"`. Damit steht ein zweiter Ausgabeweg neben dem WebSocket, den niemand mehr benutzt und den auch niemand prüft. Schritt 8 der Migration nennt ihn (*Aufräumen: nachbearbeitung.py, SSE, Annotate-Funktionen*); die beiden anderen Teile sind erledigt. | [BAU] ungebändigt |

---


## Block 15.08.2026 — aus dem Nachzug selbst

| Kennung | Was offen ist | Band |
|---|---|---|
| `DOKU-VOLLPRUEFUNG` | **Der Bestand einmal vollständig gegen den Code prüfen** — als eigener Auftrag, weil der Nachzug einer Sitzung ihn nicht leisten kann. **Nicht „alle 149 lesen":** Das ist dieselbe Ritualform, die schon beim Nachzug versagt. Geprüft wird über ableitbare Kriterien mit Zahlen — jeder genannte `.py`-Pfad gegen die Existenz der Datei, jedes Zeilenzitat `datei.py:NNN` gegen den Anker, den es behauptet, jeder in Backticks genannte Bezeichner gegen den Code, jede als Zählung im Text stehende Zahl gegen ihre Quelle. **Ergebnis sind vier Trefferlisten, nicht ein Urteil.** Der bekannte Rest bleibt benannt: Was ohne Datei-, Namens- oder Zahlbezug beschrieben ist, erreicht kein Kriterium — diese Klasse wird gezählt und nicht behauptet. **Am 21.08.2026 hat dieser Rest seinen ersten belegten Fall, und er stand an einer Stelle mit der Überschrift *WICHTIG*:** `novaberg-mem-kzg.md` §7 führte eine Tabelle, nach der `config.redis_client` **ohne** `decode_responses` arbeitet. Code, Kommentar und laufender Dienst sagen übereinstimmend **True**; die Aussage stand über Monate und leitet an, welchen Client man für KZG-Operationen nimmt. **Keins der vier Kriterien hätte sie gefunden** — der Pfad existiert, der Bezeichner existiert, es gibt keine Zeilenangabe und keine Zählung. **Daraus ein fünftes, das maschinell geht:** eine Tabelle, die einen **Konfigurationswert** behauptet, gegen den Wert im Code — `True`/`False` neben einem Bezeichner ist so greifbar wie ein Pfad. Anlass: `NACHZUG-KANDIDATEN-GATE` und die drei Lücken vom 15.08.2026, die zeigten, dass Drift sich über Sitzungen sammelt. | [BAU] ungebändigt — ⬜ **offen** — nachgesehen am 25.08.2026. Am 16.08.2026 einmal gefahren; als **wiederkehrender** Auftrag nicht eingerichtet. |
| `RAUCHTEST-ANWENDUNG-IMPORT` | **Ein Zeuge, der `main.py` importiert und die Route-Tabelle zählt.** Fünf Zeilen, und sie decken eine Klasse ab, gegen die keine Menge von Modultests hilft: einen Importfehler in der zusammengesetzten Anwendung. **Gemessen am 18.08.2026:** `grep -rln "TestClient\|import main\|api\." server/tests/` → **0 von 126** Testdateien importieren die Anwendung; eine Typannotation an einem Endpunkt legte den Dienst 9 min 38 s lahm, bei **1782 grünen Zeugen**. **Der Zeuge prüft zwei Dinge:** dass der Import durchgeht, und dass die Zahl der registrierten Routen nicht unter einen Sollwert fällt — ein Router, der still nicht mehr eingebunden wird, ist derselbe Ausfall ohne Ausnahme. **Bekannte Grenze:** Er sagt nichts über Laufzeitverhalten, nur über den Hochlauf. Genau das reicht hier. | [BAU] ungebändigt — ⬜ **offen** — nachgesehen am 25.08.2026. Gegen HEAD `599c19b` geprueft: Es gibt keinen Zeugen, der die Anwendung importiert und die Route-Tabelle zaehlt. |
| `NACHZUG-KANDIDATEN-GATE` | **Ein Riegel vor dem Doku-Commit, der die Kandidatenmenge aus der Dateiliste des Diffs ableitet** — für jede geänderte Produktivdatei alle Dokumente, die ihren Pfad oder Dateinamen nennen — und anschlägt, solange ein Kandidat weder geändert noch mit Grund verworfen ist. **Der Anlass ist gemessen, nicht vermutet:** Am 15.08.2026 galt ein Nachzug nach dem Bezeichner-Kriterium als vollständig (zehn Dokumente); die Ableitung aus der Dateiliste ergab **28 Kandidaten** und darin **drei echte Lücken**, keine davon über die geänderten Bezeichner erreichbar. Der Grund ist strukturell: Ein Dokument, das den Vorgang beschreibt, ohne den neuen Namen zu nennen, **kann** ihn nicht nennen. **Bekannte Grenze:** 36 der 149 Dokumente nennen überhaupt keine Datei und stehen damit in keiner Kandidatenliste — der Riegel deckt die dateibenennende Klasse ab, nicht die begriffliche. | [BAU] ungebändigt — ✅ **abgeschlossen** — nachgesehen am 25.08.2026. Der Riegel vor dem Doku-Commit ist gebaut und leitet seine Kandidaten aus der Dateiliste des Diffs ab. |

---


## Block 14.08.2026 — aus der Eigenzeit-Messung

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Bauart**. Ueberschrift und Text stehen in jeder empfangenden Datei.

Drei Einträge. Der erste ist ein Zeiger auf ein Konzept und **keine Wiederholung seines Inhalts** — die sechs Bauteile stehen dort mit ZIEL, TEST, MESSUNG und Gegenprobe; hier steht nur, dass sie offen sind und in welcher Reihenfolge.

| Kennung | Was offen ist | Band |
|---|---|---|
| `SCHWELLE-OHNE-PAARUNG` | Zehn Schwellen über Embedding-Kosinus zwischen 0,40 und 0,95, fünf davon auf exakt 0,40 über mindestens vier Paarungen (Fundliste, 14.08.). **Kein Aufräum-Auftrag** — wer eine anfasst, schreibt ihre Paarung dazu. **Maschinell prüfbar** und damit ein Gate-Kandidat: Eine Konstante, deren Name auf eine Ähnlichkeitsschwelle deutet, trägt in ihrem Kommentar eine Paarungsangabe. | [BAU] ungebändert — ⬜ **offen** — nachgesehen am 25.08.2026. Die zehn Schwellen nennen ihre Paarung weiterhin nicht. Deckungsgleich mit `SCHWELLEN-OHNE-VERGLEICHSGEGENSTAND` — **zwei Kennungen, ein Befund.** |

---


## Stichtag Bestandsdaten — 27.07.2026, 09:13 UTC

Das System wurde zu diesem Zeitpunkt auf einen leeren Datenbestand zurückgesetzt. Geleert wurden `pipeline_log`, `hintergrund_log`, `lzg_knoten`, `lzg_kanten`, `verbindung`, `langzeitgedaechtnis`, `timeline`, `ziele`, `notizen`, `fakten`, `entitaeten`, `delegations_akten`, `delegations_seiten` sowie die vollständige KZG-Partition in Redis (864 Schlüssel). Erhalten blieben `charakter_hash`, `charakter_anweisungen` und `direktiven`.

**Jede Korpuszahl in diesem Dokument, die vor diesem Zeitpunkt gemessen wurde, ist historisch und nicht mehr reproduzierbar.** Betroffen sind insbesondere die Messreihen aus Chat 109, auf denen die gesamte Salienz-Analyse ruht: die 775 Einträge der Partition, die 527 über 1.0 (68 %), die Verteilung über die Salienz-Eimer, die 137 Einträge älter als 30 Tage, der Knoten `id=496` mit seinem Quell-Schlüssel.

**Die Befunde bleiben gültig.** Sie ruhen auf Formeln, Konstanten und Codestellen, nicht auf den Zahlen — die Zahlen waren ihr Beleg, nicht ihre Ursache. `KZG-SALIENZ-SKALENBRUCH` ist eine Aussage über eine Dämpfungskurve und einen Deckel; die hält, solange der Code sie trägt.


### Nachgemessen am 01.08.2026 — die Salienz steht wieder oben

Erste Erhebung der KZG-Salienz **nach** dem Reset, 400 Schlüssel des Paares `meister/nova` aus 1045:

| | |
|---|---|
| Minimum | 0.67 |
| **Median** | **0.98** |
| ≥ 0.9 | 345 = **86 %** |
| = 1.0 (Deckel) | 119 = **30 %** |

**Die rohe Bewertung ist dabei gesund:** 132 Segmentbewertungen einer Messreihe lagen zwischen 0.2 und 0.9, Mittel **0.61**, keine einzige bei 1.0. Zwischen Bewertung und Ablage hebt die Formel also fast alles ans Dach — dieselbe Aussage wie vor dem Reset (damals 68 % über 1.0), auf frischem Bestand bestätigt. **Der Befund ist damit nicht historisch, sondern aktuell.**

**Was neu gemessen werden muss, bevor es geschlossen wird:** `KZG-TTL-UNSTERBLICH` (die Altersverteilung ist weg), `PROMOTION-ENTFERNT-KZG-NICHT` (der Vollabgleich hat keinen Bestand mehr), `KZG-GEWICHT-ABSOLUT-CEILING` (die Knoten über dem Cap existieren nicht mehr). Ein leerer Bestand ist kein Nachweis, dass ein Defekt behoben ist.

---


## Block 20.08.2026 — aus der Klassifikation der Fundliste

**47 Eintraege sind aus `novaberg-fundliste.md` hierher gewandert** und haben eine stabile ID bekommen. Sie sind offene Arbeit: abschliessbar, in unserem Code, und mit einer Antwort auf die Prueffrage *welche Arbeit waere fertig, wenn der Eintrag geschlossen wird*.

> **Der Umzug uebertraegt den Wortlaut, er prueft ihn nicht.** Jeder Befund ist die Diagnose seines Tages; das Datum steht an jedem Eintrag. Die Pflicht, ihn vor der Umsetzung **und vor der Rangvergabe** gegen den heutigen Code zu halten, gilt unveraendert — ein erledigter Eintrag an der Spitze verstellt die Sicht auf alles darunter, und er tut es lautlos.

**Die Zeilen `Was fertig waere` und `Prioritaet` sind neu** und stammen nicht aus der Fundliste. Die Prioritaet ist eine erste Einschaetzung aus dem Wortlaut, **kein Band** — ein Band wird gegen den Code vergeben.

---


#### BUGREGISTER-ZUSTAND-NICHT-LESBAR — offen oder behoben ist nicht auszaehlbar

**Kategorie:** [BAU] BAUART

**Zustand:** abgeschlossen — nachgeprueft am 25.08.2026. Jeder Eintrag des Defektregisters traegt seinen Zustand an genau einer Stelle, und ein Werkzeug prueft die Bilanz zwischen offenem Register und Archiv. Gemessen: 273 Eintraege, 0 Kennungen in beiden Dateien.

**Erledigt am 21.08.2026, 22:50 UTC.** Alle **82** Abschnitte tragen die Zeile `**Zustand:**` unmittelbar unter ihrer Ueberschrift, mit geschlossener Wertemenge, Pruefdatum und dem HEAD, gegen den geprueft wurde. Auszaehlbar mit `grep -cE '^\*\*Zustand:\*\* offen'`: **64 offen, 18 behoben**. Die zwoelf zuletzt fehlenden sind nicht uebertragen, sondern **einzeln gegen HEAD `62560cf` geprueft** — sechs waren behoben, sechs offen. **Der Rest ist benannt und traegt eine eigene Kennung:** `BUGREGISTER-ALTEBENE-OHNE-ZUSTAND`. Dabei kam heraus, warum die Uebertragung nicht genuegt haette: `NOVA-SPRICHT-VON-FACHABTEILUNG` trug *behoben* in der Ueberschrift und benannte im selben Eintrag die ausstehende Schlussbedingung.

~~**Die Form steht seit dem 20.08.2026, 19:32 UTC — der Eintrag bleibt trotzdem offen.**~~ Der Rest des damaligen Absatzes ist mit der Erledigung gegenstandslos: Es fehlte nicht die Form, sondern der Nachzug der uebrigen zwoelf Abschnitte, und der steht.

**Befund (20.08.2026), beim Umzug der Fundliste entstanden.** `novaberg-bugs.md` fuehrt den Zustand eines Defekts **an drei verschiedenen Stellen und in keiner verbindlich**: In der Ueberschrift (`### KENNUNG — behoben am TT.MM.`), im Koerper (`**Behoben am ...**`) oder gar nicht. Am 20.08.2026 gezaehlt: **82 Abschnitte, 4 mit Marke in der Ueberschrift, 2 weitere nur im Koerper** — der Rest traegt keine.

**Warum es zaehlt:** Wer einen Fund umzieht, kann nicht pruefen, ob der Zieleintrag noch offen ist. Zwei Fundzeilen sagten bereits *behoben*, waehrend ihre Kennung im Register keine Marke trug. Und jede Aussage der Form *„N Defekte sind offen"* — auch die der Featureliste — beruht auf einer Heuristik ueber Textmuster statt auf einem Feld.

**Was fertig waere:** Der Zustand steht je Eintrag an genau einer Stelle und in einer geschlossenen Wertemenge, sodass ein Script ihn auszaehlen kann. Die vorhandenen 82 Abschnitte sind einmal nachgezogen.

**Prioritaet:** mittel. Kein laufender Verlust — aber jede Zahl ueber offene Defekte bleibt bis dahin eine Schaetzung.


#### BUGREGISTER-ALTEBENE-OHNE-ZUSTAND — 166 Eintraege zaehlen nicht mit

**Kategorie:** [BAU] BAUART

**Zustand:** offen, stark gefallen — am Bestand gemessen am 25.08.2026. Von **166** Eintraegen ohne Zustandsangabe sind **45** geblieben. Gefallen ist die Zahl durch die Teilung des Registers und 21 nachgetragene Zustandszeilen, nicht durch einen Durchgang ueber die Altebene selbst — die 45 stehen unveraendert aus.

**Befund (21.08.2026), aus einem Abgleich der Feature-Ampeln gegen die Registerzustaende.**
`novaberg-bugs.md` fuehrt Defekte auf **zwei** Ueberschriftenebenen. Die Klassifikations-Sektion
(`### \`KENNUNG\``) traegt seit dem 21.08.2026 an allen **82** Eintraegen eine Zustandszeile mit
Pruefdatum und HEAD. Der aeltere Bestand steht als `#### KENNUNG` — **166 Eintraege**, und
**keiner** von ihnen traegt sie; ihr Zustand steht im Titel (`✅ behoben`), im Koerper oder
nirgends.

**Warum es zaehlt:** Genau die Aussage, die der Vorlaeufer-Eintrag herstellen sollte, gilt damit
nur fuer ein Drittel des Registers. Wer *„N Defekte sind offen"* zaehlt, zaehlt 82 von 248 —
und die Zahl sieht vollstaendig aus, weil der `grep` sauber durchlaeuft. **Was ihn fand, war nicht das Register selbst, sondern das Dokument, das
daran haengt:** Der Abgleich meldete **63 Kennungen, die eine Feature-Zeile nennt und zu denen
es keinen Eintrag gibt** — sie lagen alle auf der zweiten Ebene.

**Was fertig waere:** Beide Ebenen tragen dieselbe Zustandszeile, oder die zweite Ebene ist in die
erste ueberfuehrt. Die Zahl aus einem `grep` deckt dann das ganze Register.

**Prioritaet:** mittel. Kein laufender Verlust — aber eine Zahl, die vollstaendig aussieht und es
nicht ist, ist teurer als eine, die als Schaetzung kenntlich bleibt.


#### AUFSTELLUNG-NICHT-VERSIONIERT — der Aufbau von null verliert die Freigabe

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Ein Aufbau von null ist seither nicht gefahren worden, die Luecke damit unveraendert.

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Die Freigabe von `docs/` überlebt keinen Aufbau von null.** Beide Hälften der Zusicherung — der lesende Einhängepunkt und der Außenrand `/files,/docs` — stehen in `docker-compose.yml`, und diese Datei liegt **außerhalb des Git-Roots**. Wer das System aus dem Repositorium neu aufsetzt, bekommt einen Dienst, dessen Doku eine Freigabe beschreibt, die es nicht gibt; das Tor wiese sie ab, und der Grund stünde in keiner versionierten Datei. **Das berührt `F-SCHEMA-2`** (Aufbau von null muss reproduzierbar funktionieren) — dort allerdings für das Datenbankschema formuliert, während die Lücke hier in der Aufstellung liegt. **Nicht neu, aber neu wirksam:** Der Zustand galt auch für `/files`, `/knowledge` und `/logs`; erst mit einer Freigabe, die in der Repo-Doku ausführlich beschrieben ist, wird aus der Eigenschaft ein Widerspruch. **Zu entscheiden ist, ob der Harness eine Aufstellungsbeschreibung bekommt** — die Compose-Datei selbst gehört nicht ins öffentliche Repositorium, ihre Wirkung aber in eine Datei, die jemand findet.

**Was fertig waere:** Die Wirkung der Aufstellung steht in einer Datei, die jemand findet — der Aufbau von null erzeugt dieselbe Freigabe, die die Doku beschreibt.

**Prioritaet:** hoch


#### REPEAT-PENALTY-OHNE-HERKUNFT — 1.3, und niemand weiss warum

**Kategorie:** [BAU] BAUART

**Zustand:** offen, Zahl nicht mehr auffindbar — nachgesehen am 25.08.2026. Im Bestand steht `repeat_penalty` nur einmal, im Knoten `responder` mit **1.1**; die im Befund genannte 1.3 ist an keiner Stelle mehr zu finden. **Damit ist die Frage nach der Herkunft nicht beantwortet, sondern verschoben:** Auch die 1.1 traegt keine Begruendung.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **`gemma4-gpu` fährt `repeat_penalty 1.3`, und niemand kann sagen, woher die Zahl kommt.** Sie steht als `PARAMETER` im selbstgebauten Modelfile. Zum Vergleich: Ollama hat den Vorgabewert für Modelle **ohne** eigene Angabe am 12.08.2026 von 1.1 auf 1.0 gesenkt (v0.32.10, *„matching other engines"*) — der Bestand liegt also deutlich über beiden Werten, die die Laufzeit je als Vorgabe geführt hat. Ob 1.3 gemessen oder übernommen ist, steht nirgends. Betrifft Antwortlänge und Wortwahl aller Gesprächsknoten und damit jede Messreihe, die gegen sie kalibriert ist.

**Was fertig waere:** Der Wert ist gemessen oder auf den Vorgabewert zurueckgesetzt; die Begruendung steht am Modelfile.

**Prioritaet:** mittel


#### ANBIETERDAUERN-UNGELESEN — liegen vor, werden nirgends gelesen

**Kategorie:** [BAU] BAUART

**Zustand:** offen — gegen HEAD `ea1667c` geprueft am 25.08.2026. `eval_duration` kommt im ganzen Baum nicht vor; die Dauern des Anbieters werden weiterhin nirgends gelesen.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Die Dauern des Anbieters liegen seit jeher vor und werden nirgends gelesen.** `eval_duration`, `load_duration`, `prompt_eval_duration` und `total_duration` stehen in jeder Antwort. Wartezeit **am Modell** und Wartezeit **im Graphen** werden heute aus Zeitstempeln zweier Logzeilen erschlossen; mit diesen Feldern wären sie je Aufruf direkt getrennt. Betrifft jede Aussage über den seriellen Platz. Gehört zu `ANBIETER-FELDER-UNGELESEN`.

**Was fertig waere:** Die Dauern des Anbieters gehen in eine Auswertung, oder sie werden nicht mehr erhoben.

**Prioritaet:** niedrig


#### DATEIEN-VERBUND-OHNE-MODULDOKUMENT — kein Moduldokument unter `docs/`

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Unter `docs/` gibt es weiterhin kein Moduldokument des Dateien-Verbunds.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Der ganze Dateien-Verbund hat kein Moduldokument unter `docs/`.** Gefunden über die Gegenrichtung, nicht über den Bau: Vier Agenten tragen eines (`novaberg-agent-character.md`, `-directives`, `-notes`, `-timeline`), die drei Dateien-Dienste keines — sie haben nur ihr `AGENT.md` neben dem Code und das gemeinsame Konzept `_k`. **Beidseitig gezählt: 4 von 19 Agentenverzeichnissen haben ein Moduldokument.** Das ist kein Versäumnis dieses Aufrufers, sondern der Zustand des Verbunds; zu entscheiden ist, ob das Moduldokument die Sorte ist, die hier fehlt, oder ob `AGENT.md` sie ersetzt.

**Was fertig waere:** Der Dateien-Verbund hat ein Moduldokument, das seinen heutigen Zustand beschreibt.

**Prioritaet:** mittel


#### AGENT-MD-MIT-STELLWERTEN — ein Einzelfall ohne Entscheidung

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Der Einzelfall steht, eine Entscheidung darueber gibt es nicht.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **Ein `AGENT.md` mit Stellwerten ist ein Einzelfall, und niemand hat entschieden, ob er einer bleiben soll.** Von zwölf `AGENT.md` trägt genau **eines** einen `## Config`-Abschnitt (`recherche`). Der Charakter-Agent führt an seiner Aufrufstelle ein `timeout_s: 1800` und dokumentiert es dort **nicht**. Damit ist beim Nachzug einer Konfigurationsänderung nicht entscheidbar, ob das Moduldokument sie aufnehmen muss — die Frage ist eine Absicht und steht offen. Aufgekommen, als die neue Frist der Zwischen-Destillation in `novaberg-pixie-research.md` §7 nachgezogen wurde und in `AGENT.md` nicht.

**Was fertig waere:** Entschieden ist, ob ein `AGENT.md` Stellwerte traegt; die Bestandsdateien folgen der Entscheidung.

**Prioritaet:** niedrig


#### ENDPUNKTE-OHNE-BEDINGUNGEN — 19 von 19 ohne Vor- und Nachbedingung

**Kategorie:** [BAU] BAUART

**Zustand:** offen, zum Teil erledigt — am Bestand gemessen am 25.08.2026. Von 19 Endpunkten tragen inzwischen **4** Vor- **und** Nachbedingung; 15 stehen aus. Der Befund lautete 19 von 19.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **19 von 19 HTTP-Endpunkten sagen weder Vor- noch Nachbedingung.** Gezählt über 315 Funktionen, die an einer Vertrauensgrenze stehen — Routen-Dekorator, Modellantwort, `fetchone`/`execute`, Redis-Zugriff, `open`/`json.loads`. **241 davon (77 %) tragen keine Zusicherung.** Die Endpunkte sind die exponierteste Klasse und zugleich die einzige bei 100 %. Dass eine Funktion privat ist, sagt nichts über ihr Risiko: **66 der 315 sind privat**, darunter `_kzg_laden` (Redis), `_ergebnis_speichern` (Datenbank), `_speichen_lesen` (Datei).

**Was fertig waere:** Jeder HTTP-Endpunkt nennt Vor- und Nachbedingung.

**Prioritaet:** mittel


#### PRIVATE-MEMBER-OHNE-ZUSICHERUNG — 276 von 461

**Kategorie:** [BAU] BAUART

**Zustand:** offen, gewachsen — am Bestand gemessen am 25.08.2026 mit der Pruefung, die den Befund erhoben hat: **299** statt 276. **Ein geduldeter Bestand ist keine Konstante.**

**Befund (16.08.2026), aus der Fundliste uebernommen.** **276 von 461 privaten Membern haben weder Zusicherung noch Zeugen.** 13 % tragen beides, 17 % nur eine Zusicherung, 11 % nur einen Test. Für die übrigen 60 % sagt nichts, was sie voraussetzen, und nichts, dass sie tun, was sie behaupten. Die Zahl ist eine **Untergrenze**: Ein Name gilt schon als getestet, wenn er in einer Testdatei vorkommt.

**Was fertig waere:** Jedes private Member traegt Zusicherung oder Zeugen.

**Prioritaet:** niedrig


#### FUNKTIONEN-ZU-TIEF-VERSCHACHTELT — 19 tiefer als vier Ebenen

**Kategorie:** [BAU] BAUART

**Zustand:** offen, gewachsen — am Bestand gemessen am 25.08.2026 mit derselben Pruefung: **21** statt 19 Funktionen tiefer als vier Ebenen.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **19 Funktionen verschachteln tiefer als vier Ebenen.** Spitzenwerte: `ei/dreischicht.py:gv_output_parsen` mit 9, `agents/charakter/agent.py:invoke` und `agents/charakter_identitaet/crud.py:ausfuehren` mit je 8. Die kleinste der Bestandsmengen und damit der erste Kandidat für eine Leerung.

**Was fertig waere:** Keine Funktion verschachtelt tiefer als vier Ebenen.

**Prioritaet:** niedrig


#### KLASSEN-OHNE-GEMEINSAMES-FELD — 10 zerfallen in Methodengruppen

**Kategorie:** [BAU] BAUART

**Zustand:** offen, gewachsen — am Bestand gemessen am 25.08.2026 mit derselben Pruefung: **13** statt 10 Klassen ohne gemeinsames Feld.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **10 Klassen zerfallen in Methodengruppen ohne gemeinsames Feld.** Gemessen über LCOM4 an 118 Produktivklassen. `plugins/notizen_manager/manager.py:NotizenManager` trägt alle Signale gleichzeitig: LCOM4 5, zehn öffentliche Methoden, elf Felder. **Die Zeilenzahl trennt dabei nicht** — von den Klassen über 300 Zeilen zerfallen 27 %, von denen darunter 26 %; `utils/zeitparser.py:MarkerBefund` hat 35 Zeilen und LCOM4 2.

**Was fertig waere:** Jede Klasse haelt ihre Methoden ueber ein gemeinsames Feld zusammen, oder sie wird geteilt.

**Prioritaet:** niedrig


#### KANALZWANG-NUR-22-PROZENT-PRUEFBAR — statisch kaum pruefbar

**Kategorie:** [BAU] BAUART

**Zustand:** offen, unveraendert — am Bestand gemessen am 25.08.2026: Abdeckung **21 %** (19 Knoten, 13 gepruefte Literale, 48 nicht analysierbare Rueckgaben), 0 Befunde. Bei dieser Abdeckung ist *0 Befunde* keine Aussage — das sagt die Pruefung selbst in ihrer Ausgabe.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **Der Kanalzwang ist statisch nur zu 22 % prüfbar.** Über 19 Knoten gezählt: **45 von 53 Rückgaben** bauen ihr Dict schrittweise auf oder geben es aus einer Hilfsfunktion zurück; dort existiert der Schlüssel zur Analysezeit nicht. Seit dem 16.08.2026 prüft `zustand_verifizieren()` zur Laufzeit — bisher nur im Reducer, die übrigen 18 Knoten sind offen.

**Was fertig waere:** Der Kanalzwang ist maschinell pruefbar, oder der unpruefbare Rest ist beziffert und benannt.

**Prioritaet:** mittel


#### NODE-LLM-CONFIG-RECHERCHE-OHNE-RUFER — gefuellt, null Aufrufer

**Kategorie:** [BAU] BAUART

**Zustand:** offen — gegen HEAD `ea1667c` geprueft am 25.08.2026. Die Einstellung wird ausser in einem Zeugen an keiner Stelle gelesen.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **`NODE_LLM_CONFIG["recherche"]` ist vollständig gefüllt und hat null Aufrufer.** `temperature` 0.5 und `max_output_tokens` 2048 stehen dort seit langem; `get_node_config("recherche")` wird nirgends im Produktivcode gerufen, und die zehn Aufrufstellen des RechercheAgent trugen ihre Werte fest im Code. Gefunden beim Anlegen von `recherche_zwischen` — die naheliegende Handlung wäre gewesen, den vorhandenen Schlüssel zu benutzen, und sie hätte die Temperatur von 0.1 auf 0.5 verschoben, ohne dass jemand es gemerkt hätte. Dieselbe Klasse wie `SELBSTAUSKUNFT-OHNE-LESER`, nur an einer Konfiguration statt an einer Selbstbeschreibung: **Eine Konfiguration ohne Leser sieht in jedem Wertetest richtig aus.**

**Was fertig waere:** Der Eintrag hat einen Aufrufer oder ist entfernt.

**Prioritaet:** niedrig


#### ERLEDIGT-MARKE-STATT-STICHWORTLISTE — die Liste wird nie fertig

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Eine Marke, die traegt, ist nicht gebaut worden. **Der heutige Durchgang belegt den Befund:** Ohne Marke ist der Zustand aus dem Fliesstext zu lesen, und dann liest ihn kein Werkzeug.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **Eine Stichwortliste für „als erledigt geführt" wird nie fertig — und die Marke, die trüge, gibt es längst.** Der Erledigt-Filter des Bezeichner-Kriteriums erkannte `~~`, *entfallen*, *widerlegt*, *deprecated*, *nicht mehr*, *existiert nicht*, *nie gebaut*. Beim Abarbeiten der beschreibenden Befunde kamen an einem Tag **sechs weitere Formulierungen** aus dem echten Bestand hinzu: *verworfen*, *archiviert*, *nie existiert*, *die es nicht gibt*, *wurde entfernt*, *noch nicht in `config.py`*, *ersetzt `X`* — dazu die Wortstellung (*„Es gibt keine …"* gegen *„gibt es keine"*) und die Zeilengrenze, weil ein Satz über drei Zeilen die Marke vom Namen trennt. Drei Ergänzungen sind gemacht, danach abgebrochen: **Der Ertrag je Patch sinkt, die Gefahr steigt** — jedes Wort mehr macht echte Befunde unsichtbar, und ein Gerät, das zu wenig meldet, fällt nicht auf. **Der strukturelle Ausweg steht schon im Filter:** `~~` ist eine eindeutige, prüfbare Marke. Die Dokumente benutzen sie nur uneinheitlich. Entweder wird sie zur Konvention für ausgemusterte Bezeichner, oder die Falschmelderate wird beziffert und mitgeführt — heute **6 von 6** verbliebenen Treffern der Klasse `beschreibend`.

**Was fertig waere:** Die vorhandene Marke traegt die Erkennung; die Stichwortliste entfaellt.

**Prioritaet:** niedrig


#### SCHWELLEN-OHNE-VERGLEICHSGEGENSTAND — zehn Schwellen, keine nennt ihn

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die Schwellen nennen ihren Vergleichsgegenstand weiterhin nicht.

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Zehn Ähnlichkeits-Schwellen, und keine nennt, was sie vergleicht.** Der Bestand führt zehn Schwellen über Embedding-Kosinus zwischen 0,40 und 0,95 — Bibliotheks-Abruf, Zustellung, Dublettenschutz, Ziel- und Erinnerungs-Gravitation, Charakter-Resonanz, KZG, Delegation, LZG-Knoten, Lücken-Dublette. **Fünf davon stehen auf exakt 0,40, über mindestens vier verschiedene Paarungen.** Das sieht aus wie eine gemeinsame Kalibrierung und ist keine. **Die Herkunft steht überall vorbildlich dabei** — *„begründeter Startwert, kein Messergebnis"*, *„an drei Zeilen ist nichts kalibrierbar"*, bei den LZG-Knoten sogar die Gegenmessung. **Die Paarung steht nirgends**, und ohne sie ist die Herkunft nicht nachprüfbar: Eine an Themenphrasen gemessene Schwelle sagt über Volltexte nichts, auch wenn dieselbe Zahl dasteht. Gemessen am 14.08.2026 an derselben Rechnung: Themenphrase gegen Themenphrase trennt (0,437–0,896), Volltext gegen Volltext misst die Textsorte (Median 0,557), Volltext gegen kurze Äußerung trennt schwach (Median 0,105). **Kein Aufräum-Auftrag** — die zehn sind Bestand; wer eine davon anfasst, schreibt ihre Paarung dazu.

**Was fertig waere:** Jede Aehnlichkeitsschwelle nennt, was sie vergleicht.

**Prioritaet:** mittel


#### BEISPIELE-OHNE-HERKUNFTSMARKE — 9 von 150 Dokumenten sagen, woher ihr Beispiel stammt

**Kategorie:** [BAU] BAUART

**Zustand:** offen, nicht fortschreibbar — nachgesehen am 25.08.2026. Der Befund nennt 9 von 150; eine Nachzaehlung mit einem **anderen** Muster ergab 52 von 162 und ist deshalb keine Fortschreibung. **Eine Zahl gegen eine aeltere zu halten verlangt dasselbe Instrument, nicht dasselbe Thema** — das Instrument des Befundes ist nicht mit ueberliefert.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **9 von 150 Dokumenten unter `docs/` tragen eine Herkunftsmarke an ihren Beispielen.** Gezählt über das Wortfeld *synthetisch* / *konstruiertes Beispiel* / *konstruierter Turn*. Betroffen ist jedes Dokument, das einen wörtlichen Beispiel-Turn führt: `novaberg-referenz-aufloesung_k.md` §1 trägt drei (Matcha-Pulver, Grillkäse, eine Notiz namens `Einkauf`), `novaberg-haltungsraum_k.md` §1 einen (der Igel-Einzeiler) — keines der beiden Dokumente sagt, ob die Reize echt oder konstruiert sind. **Für den Igel ist die Frage seit dem 31.07.2026 entschieden** (synthetisch), nur steht die Entscheidung nicht im Dokument; sie wurde am 16.08.2026 erneut aufgeworfen. Kein Defekt am System — die Kosten fallen bei jeder Veröffentlichungsprüfung erneut an, und ein Beispiel ohne Vermerk ist von einem echten Gesprächsinhalt nicht unterscheidbar.

**Was fertig waere:** Jedes Beispiel in `docs/` traegt eine Herkunftsmarke — synthetisch oder echt. Ohne sie wird dieselbe Stelle bei jeder Veroeffentlichungspruefung neu verhandelt.

**Prioritaet:** niedrig.

---


## 0c. Aus der Fundliste klassifiziert — Chat 133 (08.08.2026)

Sieben Einträge der Fundliste waren offene Arbeit: abschließbar, in unserem Code, und mit einer Antwort auf die Prüffrage *welche Arbeit wäre fertig, wenn der Eintrag geschlossen wird*. Drei davon sind Nähte ohne Prüfung, zwei sind Aussagen über den Zustand, die veraltet sind, und zwei sind Rechnungen ohne Abnehmer.


#### KANAELE-OHNE-VERTRAG — vier Kanäle des Zustands ohne beidseitige Zusage

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die Pruefung ist als Werkzeug nicht entstanden; die beiden blinden Flecken stehen unbenannt.

Über 63 deklarierte Kanäle des `ConversationState` mechanisch geprüft: `memory_entries_raw`, `system_prompt` und `timeline_id` haben **weder Schreiber noch Leser** — sie existieren nur im Schema. Und **`response` hat vier Schreiber** (`responder.py`, `thinker.py`, `corrector.py`, `character_graph.py`), `pending_writes` drei, fünf weitere je zwei. Mehrere Erzeuger für eine Größe sind die Klasse, die auseinanderläuft.

**Die Prüfung hat zwei benannte blinde Flecken:** Sie sieht den Erzeugungspfad in `create_state` nicht — daher 15 Falschmeldungen „gelesen, nie geschrieben" — und keine Verbraucher außerhalb von `graph/` und `services/`; so fiel `such_vektor` zu Unrecht auf, den ein Plugin liest.

**Was fertig wäre:** die Prüfung als wiederholbares Werkzeug, mit beiden blinden Flecken einmal beschrieben statt jedes Mal neu — und danach die Zahl, die heute fehlt: 63 Kanäle, davon *n* mit geprüftem Vertrag auf beiden Seiten.

**Priorität:** hoch. Ohne die Zahl ist jede Aussage über die Zuverlässigkeit der Kette ein Eindruck.


#### CHARAKTER-HASH-DOKU-FALSCHE-QUELLE — das Dokument nennt eine Quelle, die der Code nicht liest

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Beide Abschnitte nennen weiterhin die falsche Quelle.

`novaberg-pixie-character-hash.md` §3.3 und §3.4 führen für das Intentions-Profil *„Aggregiert aus Session-Annotationen (Intentionen + Modus + Stil)"* und für das Emotions-Profil eine Grundtendenz „über Monate". Im Code nehmen `intentions_profil_destillieren` und `emotions_profil_destillieren` beide `lzg_eintraege` als einziges Material und geben bei leerer Liste `""` zurück (`server/agents/charakter/destillation.py`).

**Wer nach §3.3 sucht, warum das Profil leer ist, sucht in den Session-Annotationen — und findet dort nichts Falsches.** Das ist die Sorte Doku-Fehler, die Suchzeit kostet statt Verhalten zu ändern.

**Was fertig wäre:** beide Abschnitte auf die tatsächliche Quelle ziehen, mit Datum und Vermerk, was vorher dastand.

**Priorität:** mittel. Hängt unmittelbar an `PROFILE-LEER-URSACHE-UNBEKANNT` — wer dort misst, liest zuerst dieses Dokument.

---


### Block 30.–27.07. — neun Einträge (08.08.2026)

Der aelteste Bestand. **Acht der neun sind Struktur statt Verhalten** — tote Zweige, doppelte Formen, ein Dokument ohne Abgleich. Der neunte, die Ungleichverteilung des Repertoires, ist der einzige, der eine Absicht braucht.


#### DOKU-MEHRDEUTIGE-ANKER

**Kategorie:** [BAU] BAUART

**Zustand:** offen, und heute erneut belegt — 25.08.2026. Das Findemittel der Chronik zaehlt fuenf mehrfach vergebene Titel und muss sie mit `-1`, `-2` durchzaehlen, damit die Verweise nicht auf dieselbe Stelle zeigen. Der Befund gilt ueber die drei genannten Dokumente hinaus.

**Befund (2026-07-28).** Doku-Hygiene, **gemessen**: Drei Dokumente vergeben Überschriften mehrfach und erzeugen damit mehrdeutige Anker — `novaberg-backlog.md` (3× „Phasen-Übersicht", 3× „Hintergrund", 2× „Auswirkung auf Akten-Vision"), `novaberg-roadmap.md` (je 2× „Dokumentation", „Backlog", „Bugfixes") und `novaberg-thinking-skills_k.md` (2× „Wetter-Anfragen"). Ein Zähler über alle `#`-Zeilen meldet zusätzlich `novaberg-memory-synapsen_k.md` mit 12 Treffern — das sind **Python-Kommentare in einem Code-Block**, kein Befund. Wer das nachmisst, muss Code-Fences überspringen.

**Was fertig waere.** Jede Ueberschrift ist in ihrem Dokument eindeutig.

**Prioritaet:** niedrig.


#### AGENT-MD-NIE-GEPRUEFT

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Ein Abgleich der Datei gegen den Code hat nicht stattgefunden.

**Befund (2026-07-28).** `server/agents/kzg/AGENT.md` ist nie gegen den Code geprüft worden. Der KZG-Agent hat seit der Erstfassung Nodes gewonnen und verloren (`magnete_aufloesen` kam, `aehnlichkeit_pruefen` ist gelöscht) — ob die AGENT.md das trägt, ist offen. Gilt sinngemäß für die übrigen AGENT.md-Dateien, die ebenfalls nie systematisch abgeglichen wurden.

**Was fertig waere.** Das Agentendokument ist gegen den Code gelesen und trifft zu.

**Prioritaet:** mittel.


#### LLM-PROVIDER-ZWEIG-UNERREICHBAR

**Kategorie:** [BAU] BAUART

**Zustand:** offen, unbelegt — gegen HEAD `599c19b` nachgesehen am 25.08.2026. Der im Befund zitierte defensive Zweig ist in dieser Form nicht mehr auffindbar; `services/llm_provider.py` liest das Feld heute als `daten.get("message") or {}`. **Ob der Zweig entfallen ist oder nur umgeschrieben, ist ohne den alten Wortlaut nicht zu entscheiden.**

**Befund (2026-07-30).** `services/llm_provider.py`: Der defensive Zweig, der `message` als Dict *oder* Objekt behandelte, war **nie erreichbar**. Drei Zeilen darueber ruft die Token-Verbuchung `response.get(...)` — ein Objekt scheitert dort mit `AttributeError`, bevor die Absicherung greift. Beim Schreiben des Tests aufgefallen, nicht beim Lesen des Codes. Behoben: Der Typ ist jetzt festgelegt, ein Vertragsbruch kracht laut.

**Was fertig waere.** Der nie erreichbare Zweig ist entfernt oder erreichbar.

**Prioritaet:** niedrig.


#### FUENF-STELLEN-FORM-MEHRFACH

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die Form steht weiterhin an mehreren Stellen.

**Befund (2026-07-30).** Fünf Stellen schreiben eine Form mehrfach hin, statt sie einmal zu benennen. Alle fünf sind über die Verzweigungsregel des Linters aufgefallen und einzeln gelesen; keine ist ein Defekt, alle fünf sind Struktur. **Der gemeinsame Nenner ist die Wiederholung, nicht die Kompliziertheit** — die Verzweigungszahl ist bei diesen fünf kein Ausdruck von Sachkomplexität, sondern von einem zweimal hingeschriebenen Muster.

**Was fertig waere.** Die Form steht einmal und wird benannt verwendet.

**Prioritaet:** niedrig.


#### LOGGING-PROZENT-STATT-FSTRING

**Kategorie:** [BAU] BAUART

**Zustand:** offen, gewachsen — am Bestand gemessen am 25.08.2026: **96** Aufrufe mit `%`-Platzhaltern statt 65. **Ein geduldeter Bestand ist keine Konstante.**

**Befund (2026-07-30).** **65 Logging-Aufrufe formatieren über `%`-Platzhalter mit Argumenten** statt über den vorgeschriebenen f-String, zum Beispiel `logger.info("… %s", basis_top)` in `graph/nodes/ei_calc.py:252` und `logger.exception("%s: kanten_alle_loeschen fehlgeschlagen", type(exc).__name__)` in `memory/lzg_kanten.py:512`. Zum Vergleich am selben Bestand gezählt: **538** Aufrufe mit f-String. Die Stellen verteilen sich über den Baum, sie sind kein Nest in einer Datei. Berührt die Begründung, mit der `G004` in der Linter-Konfiguration abgeschaltet ist — dort steht, f-Strings seien im Logging *vorgeschrieben*, was für 65 Stellen so nicht zutrifft. *(Zeilennummern gemessen 30.07.2026.)*

**Was fertig waere.** Alle Aufrufe folgen der vorgeschriebenen Form, oder die Vorschrift nennt beide.

**Prioritaet:** niedrig.

---


### Block 31.07. — fünf Einträge (08.08.2026)

Vier Doku- und Namensfunde, einer davon eine offene Prüfung am Initiative-Rad.


#### GRAPH-TABELLE-OHNE-VERFASSER

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die Node-Tabelle kennt den Verfasser weiterhin nicht.

**Befund (2026-07-31).** Die Node-Tabelle in `novaberg-graph.md` §3 kennt den **Verfasser nicht**. Sie führt siebzehn Knoten und geht von `GV-Node` direkt zu `Responder`; der Verfasser existiert im Code seit dem Responder-Umbau. Wer die Tabelle liest, hält den Umbau für nicht gebaut.

**Was fertig waere.** Die Tabelle fuehrt alle Knoten des heutigen Graphen.

**Prioritaet:** mittel.


#### BILD-VERWAIST

**Kategorie:** [BAU] BAUART

**Zustand:** offen, am Bestand bestaetigt am 25.08.2026. Die Datei liegt unveraendert unter `images/`; der einzige Verweis darauf steht in **diesem Register**, nicht in der Doku.

**Befund (2026-07-31).** **`images/nova-ui-emotion-1.png` ist verwaist**, seit die README auf die neuere Aufnahme zeigt. Es zeigt die Emotionswerte des Nutzers unter einer Bildunterschrift, die Novas Zustand behauptete — der Widerspruch bestand seit April. Ebenfalls verwaist, aber älter: `images/nova-ui-memory-change-1.png` vom 15.05.2026, von keiner Fassung eingebunden. Löschen ist nicht entschieden.

**Was fertig waere.** Das verwaiste Bild ist entfernt oder wieder eingebunden.

**Prioritaet:** niedrig.

---


### Block 01.08. — vier Einträge (08.08.2026)


#### LLM-LOCK-SCHUETZT-DIE-GPU-NICHT-DEN-TURN

**Kategorie:** [BAU] BAUART

**Zustand:** offen, unbelegt — nachgesehen am 25.08.2026. Der Befund haengt an einer Laufzeitbeobachtung; nicht wiederholt.

**Befund (2026-08-01).** **Der `llm_lock` schützt die GPU, nicht den Turn — und der Modell-Worker hat einen eigenen Riegel dahinter.** Gemessen beim Umbau der Eingangs-Queue: Ein zweiter Durchlauf, der den `llm_lock` bekam, lief trotzdem in den 60-Sekunden-Timeout des Modell-Workers, weil dessen Warteschlange noch belegt war. Wer den Riegel hält, hat also noch keine Rechenzeit. Für den Prompt-Pfad ist das mit dem Turn-Marker entschärft; für jeden anderen Aufrufer besteht es fort, und die Zahl der Fälle ist nicht erhoben.

**Was fertig waere.** Es ist entschieden und aufgeschrieben, welcher der beiden Riegel den Turn schuetzt — und der andere ist entweder entfernt oder als das benannt, was er tut.

**Prioritaet:** mittel.


### Block 05.–02.08. — sechzehn Einträge (08.08.2026)

Der Befund steht im Wortlaut, in dem er notiert wurde; ergänzt sind Kennung, Priorität und die Zeile, an der erkennbar ist, wann der Eintrag geschlossen ist.

**Vier davon gehören zusammen und ergeben erst zusammen ein Bild.** `PIXIE-EIN-SLOT-BLOCKIERT-ALLES`, `RECHERCHE-RETRY-BLOCKIERT-QUEUE`, `AUFTRAGSARTEN-OHNE-AGENTEN` und `SHADOW-QUEUE-RUECKSTAND-UNGEMESSEN` beschreiben denselben Engpass von vier Seiten: Ein serieller Platz, ein Lauf, der ihn über seine Zeitgrenze hinaus hält und danach mit vollem Anspruch zurückkehrt, 230 Aufträge für Agenten, die es nicht gibt, und ein Rückstand von 649, dessen Abfluss niemand gemessen hat. **Wer einen davon einzeln angeht, misst die Wirkung der anderen drei mit.**

> #### Der Engpass ist am 16.08.2026 vermessen worden — die Zahlen stehen hier, die Einträge bleiben offen
>
> Anlass war `RECHERCHE-ZWISCHENDESTILLATION-OHNE-GRUND`, und die Regel *„wer einen angeht, misst die anderen drei mit"* hat sich bestätigt. Über 39 h Laufzeit und 24 h Logfenster:
>
> ```
> Der Platz          LLM-Spur: 239 Laeufe, 3376 uebersprungene Heartbeats
>                    -> zu rund 93 % besetzt
>                    213 der 239 Laeufe (89 %) gingen an `recherche`,
>                    19 an die Charakter-Destillation (Reihe 1)
>
> Der Rueckstand     583 aktive recherche-Auftraege, aeltester vom 27.07.
>                    189 vertiefen aktiv, 45 nachfragen
>
> Der Abfluss        70 Ablagen in der Bibliothek je 24 h, davon
>                    50 `fehlschlag` und 20 mit verwertbarem Ergebnis
>
> Der Verfall        270 der 583 (46 %) fallen binnen 17 Tagen unter die
>                    Schwelle; 14 davon binnen 2 bis 6 Tagen
> ```
>
> **`SHADOW-QUEUE-RUECKSTAND-UNGEMESSEN` hat damit seine Zahl** — der Abfluss beträgt rund **20 verwertbare Ergebnisse am Tag**. Der Eintrag bleibt trotzdem offen: Gemessen ist ein Tag, und die Frage nach dem Verhältnis von Zulauf, Abfluss und Verfall über die Zeit braucht eine Reihe, keinen Punkt. **Der Zulauf schwankt stark** (26 am 15.08., 76 am 14.08., 103 am 13.08.) und hängt selbst am Erkenntniszyklus, der denselben Platz braucht — Zulauf und Abfluss sind also nicht unabhängig.
>
> **`PIXIE-EIN-SLOT-BLOCKIERT-ALLES` hat seine Zahl ebenfalls:** 3376 übersprungene Heartbeats mit der Meldung *„maximum number of running instances reached"*. Die Zwei-Spuren-Trennung vom 09.08. wirkt — sie trennt Rechnung von Sprache, aber **innerhalb** der LLM-Spur konkurrieren Recherche und Charakter-Destillation weiter um einen Platz, und die Recherche nimmt neun von zehn. Das ist die Trennung nach Latenz eine Ebene tiefer als bisher gedacht: Sie ist zwischen den Spuren gebaut und innerhalb der LLM-Spur nicht vorhanden.
>
> **`RECHERCHE-RETRY-BLOCKIERT-QUEUE` ist in seinem Kern erklärt und zur Hälfte behoben.** *„Ein Lauf, der ihn über seine Zeitgrenze hinaus hält und danach mit vollem Anspruch zurückkehrt"* — die Zeitgrenze war die geerbte Frist von 300 s, und der Lauf hielt den Platz danach weiter, weil eine Frist nur das Warten beendet, nicht die Ausführung. Seit dem 16.08. trägt die Aufrufstelle 1200 s (`F-FRIST-1`). **Nicht behoben ist der Rückkehr-Teil:** Der Auftrag kommt mit unverändertem Anspruch zurück und verliert nur einen Versuch von dreien.
>
> **Und ein fünfter Aspekt kam hinzu, den keiner der vier nannte:** ~~Der Fehlversuchspfad löscht **hart**~~ und wählt dabei nach *hoher* Salienz aus — ~~die mittlere `salienz_roh` steigt monoton mit dem Versuchszähler (0,867 · 0,947 · 0,990)~~. Er steht in der Fundliste.
>
> **Am 23.08.2026 zur Hälfte erledigt und einmal widerlegt** (`FEHLVERSUCHSPFAD-LOESCHT-HART`): Der Pfad legt still statt zu löschen, mit eigener Spalte `grund`. Die **Auswahl** nach hoher Salienz ist unverändert. Und die Kurve, die den Befund trug, ist heute nicht mehr reproduzierbar — nachgemessen 213 Aufträge bei null Versuchen, 3 bei einem, keiner darüber.

**Zwei weitere hängen an derselben Zahl:** `KONTEXT-32768-IN-SECHS-DOKUMENTEN` und `RECHERCHE-ZWISCHENDESTILLATION-OHNE-GRUND`. Der zweite ist eine Folge des ersten — ein Verarbeitungsschritt, der verlustbehaftet gegen eine Grenze komprimiert, die achtmal weiter weg ist als angenommen.


#### KONTEXT-32768-IN-SECHS-DOKUMENTEN

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die sechs Dokumente rechnen unveraendert mit dem falschen Kontextmass.

**Befund (2026-08-04).** **Sechs Dokumente rechnen mit einem CPU-Kontext von 32768 Tokens; gemessen sind es 262144.** Am laufenden System um 21:02 UTC: Connector `qwen36`, GPU `gemma4-gpu` bei 32768, **CPU und Analyse `qwen36-cpu` bei je 262144** — das Achtfache. Betroffen: `novaberg-tool-dateien_k.md` §1 (die Mandelbrot-Navigation ist damit für den Hintergrundpfad nicht mehr erzwungen, für den Gesprächspfad sehr wohl), `novaberg-pixie-research.md` §108, `novaberg-gedankenkette_k.md` §186 (sagt ausdrücklich „auf **allen** Pfaden des `qwen36`-Connectors" — für zwei von drei falsch), `novaberg-hermes-substrat_k.md` §366 („eine harte Grenze"), `novaberg-node-gv_k.md` §607, `novaberg-pixie.md` §135. **Die Trennung ist der Kern:** Gesprächspfad 32k, Hintergrundpfad 256k — wer die alte Zahl liest, dimensioniert beide gleich.

**Was fertig waere.** Alle sechs Stellen tragen den gemessenen Wert samt Messdatum, und jede daraus abgeleitete Aussage ist nachgerechnet.

**Prioritaet:** hoch.


#### ARCHITEKTUR-TABELLENLISTE-UNVOLLSTAENDIG

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die Tabellenliste ist weiterhin unvollstaendig; heute sind ihr zwei Dokumente hinzugefuegt worden, die Tabellen selbst nicht geprueft.

**Befund (2026-08-04).** **Die Tabellenliste in `novaberg-architecture.md` §10 ist unvollständig.** `verbindung` (Chat 109) und `ziele` fehlen, obwohl beide im Kern-Schema stehen; `ziele` ist zusätzlich die Tabelle, an der `F-ZIEL-1` hängt. Die Liste sieht vollständig aus und ist es nicht — wer sie als Übersicht liest, übersieht zwei Tabellen.

**Was fertig waere.** `verbindung` und `ziele` stehen in der Liste.

**Prioritaet:** niedrig.


#### KERN-SCHEMA-OHNE-DRIFTPRUEFUNG

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. `CREATE TABLE IF NOT EXISTS` bewacht eine bestehende Tabelle unveraendert nicht.

**Befund (2026-08-04).** **`CREATE TABLE IF NOT EXISTS` bewacht eine bestehende Tabelle nicht.** Ändert jemand eine Spaltendefinition in `db/init.sql`, ist das gegen eine schon angelegte Tabelle wirkungslos und bleibt still: Schemadatei und laufendes Schema laufen auseinander, ohne dass etwas anschlägt. Das Kern-Schema hat dagegen keine Prüfung — nur `autonomous_wissen` hat seit heute einen Test, der das laufende Schema gegen eine von Hand geführte Sollliste stellt.

**Was fertig waere.** Das Kern-Schema bekommt dieselbe Pruefung, die `autonomous_wissen` schon hat — Schemadatei gegen laufendes Schema, und eine Abweichung schlaegt an.

**Prioritaet:** hoch.


## 0. Zeitparser und Kalibrierung (31.07.2026)

Vier Einträge aus einem Tag. Die ersten drei kommen aus dem ersten Lauf des Härtefallkorpus gegen den Parser, der vierte aus der Neuerhebung der Positions-Kontrolle.


#### ZEIT-KORPUS-TESTS-AUF-UNITTEST — drei Testdateien der Korpus-Lieferung laufen nicht

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die Umstellung ist nicht erfolgt.

`tests/test_zeit_korpus.py`, `tests/test_zeit_normalisierung.py` und `tests/test_zeit_zonen.py` sind gegen `pytest` geschrieben — `@pytest.mark.parametrize`, `pytest.skip`, `pytest.fail`. Der Testrahmen dieses Projekts ist reines `unittest`; `pytest` ist im Server-Abbild nicht installiert. Unter dem kanonischen Lauf tragen die drei Dateien **null Abdeckung** bei und scheitern beim Import.

Deshalb sind sie **nicht eingecheckt**. Der Korpus selbst braucht kein `pytest`: `tests/korpus_laeufer.py` läuft als Skript, und alle Zahlen des Erstlaufs sind so gemessen.

**Zwei Dinge sind beim Umschreiben zu beachten.** `test_zeit_korpus.py` überspringt sich an drei Stellen selbst — bei fehlender Umgebung, bei vorauseilenden Fällen und im gemeinsamen Zugriffspfad. Ein Test, der sich selbst überspringt, ist keiner; die Fälle brauchen eine andere Form. Und die Zahl übersprungener Tests ist im Bericht ein Befund, kein Transportmittel für eine Meldung.

**Aufwand:** drei Dateien, rund 40 Fälle. **Priorität:** mittel — der Korpus ist über den Läufer bereits fahrbar, es fehlt die Einbindung in die Suite.


## 3. Node-Konfiguration (TEMP1)

Jeder der 10 Nodes im HumanGraph wird ueber `config.py` konfigurierbar: Temperature, Sampling-Parameter, System-Prompt-Templates mit Platzhaltern (`{today}`, `{user_name}`), max_output_tokens. Zwei Nodes ohne LLM-Call (Enricher, Dispatcher) haben Datenzugriffs-Parameter.

**Empfohlene Temperatures:** Perzeption 0.05 (reine Klassifikation), Router 0.05, Salienz 0.05 (niedrigste — Kreativitaet = halluzinierte Fakten), Planner 0.2, Responder 0.7 (hoechste — natuerliche Sprache), Thinker 0.15, Tribunal 0.2, Corrector 0.5.

**Ollama-spezifisch:** repeat_penalty (1.1 fuer Responder), presence_penalty (0.3), top_p (0.9) — direkte Bekaempfung repetitiver Patterns auf Modell-Ebene.

**Pixie-Tasks:** Eigene Config-Struktur (PIXIE_TASK_CONFIG) mit Temperature und max_output_tokens pro Agent.

---


## 5. MCP-Architektur (Vision)

Langfristige Vision: Agenten als MCP-Server (Model Context Protocol) in Docker-Containern, Novaberg als MCP-Client. Jeder Agent wird ein eigenstaendiger Service mit definierter Schnittstelle — unabhaengig deploybar, testbar und austauschbar. Das wuerde die Grenze zwischen lokalen Agenten und externen Diensten aufloesen: ein RechercheAgent koennte lokal oder als Remote-Service laufen, mit identischer Schnittstelle.

---


## 7. Offene Epics & Features


### Pixie-Erweiterung (Epic 5, offen)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Bauart**. Ueberschrift und Text stehen in jeder empfangenden Datei.
| # | Thema | Status |
|---|-------|--------|
| ERK-DOKU-NACHZUG | Die Bestandteile auf den Zyklus überarbeiten | ⬜ **Neu am 06.08.2026.** Sechs Dokumente tragen seit heute nur eine **Marke**, die auf `novaberg-thinking-erkenntniszyklus_k.md` zeigt: `novaberg-autonomous-wissen_k.md`, `novaberg-thinking-opinion_k.md`, `novaberg-thinking-curiosity_k.md`, `novaberg-wissensluecken_k.md`, `novaberg-pixie-deepdive_k.md`, `novaberg-pixie-research.md`. Ihre Texte beschreiben die Auslösung noch als Reflex aus einer Intention. **Dazu zwei Moduldokumente, die das Routing beschreiben und bewusst *keine* Marke tragen** — `novaberg-pixie-kzg.md` und `novaberg-node-salience.md` halten den gebauten Zustand fest, und der ändert sich erst mit dem Bau. **Der Zyklus kehrt sie um** — Recherche und Vertiefung entstehen erst aus einer gefundenen Lücke. Die Überarbeitung ist ein eigener Auftrag und bewusst nicht mit dem Konzept mitgemacht | [BAU] Zyklus ✅ |
| SA2–SA4 | Charakter-basierte Priorisierung | ⬜ Multiplikator auf Queue-Priorität |


### Epic: HERMES-SUBSTRAT — Hermes Agent als Ausführungs-Schicht

**Kategorie:** [BAU] BAUART

**Status:** Konzept steht, kein Code (`novaberg-hermes-substrat_k.md`)
**Berührt:** Skill-System (Epic 10, Abschnitt 2) — siehe Abgrenzung unten

Nova bleibt Kopf (Persönlichkeit, Emotion, Gedächtnis, Entscheidung), Hermes
wird Hände (Werkzeuge, Skills, Workflows, Ausführung). Zwei getrennte
Prozesse, Kommandorichtung einseitig: Nova ruft, Hermes antwortet. Kein Fork —
Anbindung entsteht vollständig auf Novaberg-Seite.

Alle sechs Gedächtnisse bleiben oben: Notizen, Timeline, Fakten, Entitäten,
Knowledge Graph, Datei-Gedächtnis.

**Vor dem Anbindungs-Konzept sind sieben Messungen am Testcontainer zu
erledigen:**

| # | Frage | Status |
|---|-------|--------|
| M0 | Startet der Gateway ohne konfigurierte Messaging-Plattform, und tickt der Kanban-Dispatcher? (Dispatcher lebt im Gateway-Prozess — Gateway darf nicht abgeschaltet werden.) | ⬜ |
| M5 | Läuft lokale Ollama über den Custom-Endpoint-Pfad? Welches Tool-Calling-Verhalten zeigt qwen36-cpu? | ⬜ |
| M1 | Wieviel Struktur nimmt ein Kanban-Worker aus den Feldern auf, wieviel muss Prosa im `--body` sein? | ⬜ |
| M2 | Ist `complete --result` strukturierbar? Kann ein Ausgabeschema vorgegeben werden? | ⬜ |
| M3 | Welche Felder liefert `hermes skills list` maschinenlesbar? Reicht das für einen Körperschema-Knoten? | ⬜ |
| M4 | Wie erfährt ein Aufrufer von `block`? Polling oder Rückkanal? | ⬜ |
| M6 | Queue-Tiefe und Wartezeiten an Port 11435 vor und nach Anschluss des dritten Verbrauchers | ⬜ |

**Reihenfolge zwingend M0 → M5 → M1–M4.** Wird M5 nicht zuerst beantwortet,
misst man das Modell statt Hermes und kann beides hinterher nicht trennen.

Offene Entscheidungen H1–H8 siehe Konzeptdokument, Abschnitt 12.


### Refactoring & Code-Hygiene (Chat 88)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Bauart**. Ueberschrift und Text stehen in jeder empfangenden Datei.

Sammelposten aus zwei Audits in Chat 88 — dem allgemeinen Code-Audit zum Synapsen-Umbau und der P0-Migrations-Konsolidierung (db/init.sql als Single Source of Truth). Zwölf Einträge: sechs aus dem allgemeinen Audit, drei aus P0-Beobachtungen während der Konsolidierung, drei aus dem P0-Abschluss-Bericht. Bewusste Trennung von den Synapsen-Sprints P1–P10: diese Einträge sind keine Voraussetzung für den Umbau, sondern Code-Hygiene auf Bestand und neuer Infrastruktur. Werden zwischen den Sprints oder in einer eigenen Refactor-Welle abgearbeitet.

| # | Thema | Status |
|---|-------|--------|
| REFAC-ENRICHER-EVA | Enricher-Funktion `enrich()` (328 Zeilen) in EVA-Struktur aufteilen — sechs Phasen-Helfer plus Dispatch. Verletzt Handbuch §2 (Funktionen über 80 Zeilen werden refaktoriert). | [BAU] ⬜ Prio hoch — sollte vor P5 (Synapsen-Lesepfad) gemacht werden, der den Enricher ohnehin anfasst |
| REFAC-LOGGER-HIERARCHIE | Logger-Namen vereinheitlichen. Heute Mix aus `ki_server.enricher` (flach), `ki_server.agents.decay` (verschachtelt), `__name__` (ohne Präfix). Filter-Konfiguration über Logger-Hierarchie damit holprig. | [BAU] ⬜ Prio mittel — Pipeline-Log-Forensik wird durch saubere Logger-Filter angenehmer |
| REFAC-SHUTDOWN-DISZIPLIN | Lifespan-Shutdown wartet nicht auf gecancelte Tasks (`delivery_task`, `consumer_task`, `scheduler`). Cancel-Signale ohne `await`, kein Final-Flush. Muster aus dem neuen `pipeline_log_task` (mit `wait_for` und expliziter Flush-Phase) auf Bestand übertragen. | [BAU] ⬜ Prio mittel — Datenverlust-Risiko bei laufenden Operations |
| REFAC-SCHEMA-MIGRIEREN-FAILMODE | `schema_migrieren()` verschluckt Fehler mit `logger.warning(...)` und macht weiter. Verletzt „fail loud" (Handbuch §1). Seit P0 lädt `schema_migrieren()` die gesamte `db/init.sql` als Einheit — die Korrektur betrifft die generelle Fail-Mode-Behandlung, keine tabellenspezifischen Sonderpfade möglich. | [BAU] ⬜ Prio mittel |
| SHUTDOWN-EVENT-ASYNC | `shutdown_event` in `config.py:56` ist `threading.Event`, obwohl alle Konsumenten async-Loops sind (`shadow_delivery_loop`, `event_consumer_loop`, `writer_loop`). Folge: drei verschiedene Polling-Patterns mit `is_set()` und festen `asyncio.sleep()`-Intervallen statt einer einheitlichen `await asyncio.wait_for(shutdown_event.wait(), timeout=…)`-Lösung. Synchrone Pixie-Tasks (`shadow_agent/base_task.py`, `nova_gedaechtnis.py`) nutzen nur `is_set()` — API ist in beiden Event-Typen identisch, Umstellung damit trivial. Aufdeckung: P1-Implementierung, erster Code-Entwurf hat `threading.Event.wait()` blockierend im asyncio-Loop genutzt; Bug-Fix per Polling-Pattern in `writer_loop`. | [BAU] ⬜ Prio mittel — am sinnvollsten zusammen mit REFAC-SHUTDOWN-DISZIPLIN |
| REFAC-PIPELINE-LOG-VOLLVERKABELUNG | Vollständige Pipeline-Log-Verkabelung aller Nodes (Perzeption, EI-Calc, Router, Planner, Agent-Dispatch, GV, Responder, Thinker, Tribunal, Corrector) plus aller fünf Pixie-Agenten. P1 verkabelt nur den Enricher als Demo; weitere Nodes kommen peu à peu in den Phasen, die sie ohnehin anfassen (Konvention §13.3 im Synapsen-Konzept). Vollständige Abdeckung bleibt als Cleanup-Sprint nach P9 stehen. | [BAU] ⬜ Prio hoch nach P9 |
| REFAC-UMLAUTE | Inkonsistente Umlaut-Schreibweise quer durch den Code („Eintraege" / „Einträge", „faellig" / „fällig" gemischt). Kein blockierendes Problem, aber Suche und Konsistenz leiden. | [BAU] ⬜ Prio niedrig — Aufräum-Aktion |
| REFAC-DB-INDEX-DUPLIKAT | Doppel-Index `idx_timeline_type` auf `timeline`-Tabelle zusätzlich zum offiziellen `idx_timeline_user_type` (beide auf `(user_id, event_type)`). Altname aus früherer Definition, durch manuellen Eingriff erhalten. In P0 bewusst belassen, weil eventuell noch nützlich. | [BAU] ⬜ Prio niedrig — irgendwann überprüfen, ob noch gebraucht, sonst droppen |
| REFAC-SEEDS-AUSLAGERN | Seed-Daten für initiale Nova-Ziele aus `db/init.sql` in eine eigene `db/seed.sql` verschieben, mit eigenem Aufruf-Pfad bei Frisch-Installation (eigene Datei in `docker-entrypoint-initdb.d`) oder bewusst aus dem Code heraus. Heute in `db/init.sql` mit Header-Hinweis auf die spätere Auslagerung dokumentiert. | [BAU] ⬜ Prio niedrig — semantische Sauberkeit |
| REFAC-AGENT-INIT-COMPOSE-MOUNT | Mount-Strategie für Code-Dateien aus dem Repo in den Server-Container verallgemeinern. Heute reicht der `db`-Mount für `db/init.sql`; falls künftig weitere Dateien aus dem Repo zur Laufzeit lesbar sein müssen (z.B. Skills, weitere SQL-Artefakte), wäre ein generischer Read-Only-Mount der Repo-Wurzel sauberer. | [BAU] ⬜ Prio niedrig — theoretische Vorsorge |
| REFAC-EVENT-PAYLOAD-SEEDING | Event-Consumer (`event_consumer.py:409–417`) seedet acht Perzeptions-Felder manuell aus `payload` in den State (`current_emotion`, `current_arousal`, `gespraechs_modus`, `intent`, `tone`, `sprach_stil`, `beziehungs_dynamik`, `emotions_vektor`). Bei jeder neuen Perzeptions-Spalte muss diese Kopier-Liste erweitert werden. Generisches Seeding aller bekannten State-Keys aus dem Payload würde die Pflege vereinfachen. Beobachtet in P1.1-Audit. | [BAU] ⬜ Prio niedrig — bei der nächsten neuen Perzeptions-Spalte refaktorieren |
| REFAC-HANDBUCH-§9-MIGRATIONS | `DEVELOPER_HANDBOOK.md` §9 fordert „Niemals ALTER TABLE in init.sql. Schema-Änderungen laufen über separate, versionierte Migrations-Skripte (Alembic empfohlen)." Diese Norm widerspricht der seit P0 etablierten Konvention — `db/init.sql` ist Single Source of Truth, und Schema-Änderungen werden als ALTER-Statements am Ende der Datei eingefügt und in Reviews zu CREATE-Definitionen konsolidiert. Das Handbuch ist hier outdated und muss auf die gelebte P0-Konvention nachgezogen werden. Plugins (`agents/*/init.sql`) bleiben eigenständig. | ✅ Erledigt (Docs-Commit 12.07.2026) — §9 neu gefasst (Handbuch v0.4), siehe HANDBUCH-§9-VERALTET |
| TEST-WORKER-SHUTDOWN-COROUTINE | 5 (nicht 4) von 26 ModelService-Tests waren rot: Exception- + ExpectJsonFail-Tests von ChatWorker, BackgroundWorker UND EmbedWorker scheiterten im `asyncTearDown` an `worker.shutdown()` → `await self._task` → `RuntimeError: cannot reuse already awaited coroutine` (`worker_base.py:92`). Trat nur in Pfaden auf, wo `_call_model` eine Exception wirft (Task bereits fertig, erneutes await auf konsumierte Coroutine). Beobachtet Chat 93, gelöst Chat 96 (e891eb9): `shutdown()` awaitet nur noch bei `not self._task.done()`, `self._task = None` im finally. Verifiziert 26/26 grün per `python -m unittest discover -t /app -s tests`. | [BAU] ✅ Chat 96 gelöst |
| WORKER-SHUTDOWN-QUEUE-DRAIN | `ModelWorker.shutdown()` (`worker_base.py`) dränt die Queue nicht: der Docstring verspricht, anstehende Requests würden mit `asyncio.CancelledError` abgebrochen, aber der Code setzt keine Exception auf wartende Futures — bei Shutdown noch eingereihte Requests werden stillschweigend fallengelassen, ihr `submit()`-Caller hängt unendlich auf dem Future. Kein akutes Produktionsrisiko (Shutdown passiert nur beim Server-Stopp), aber Doku-/Code-Divergenz und latentes Hänge-Risiko. Fix: in `shutdown()` Rest-Queue dränen und `future.set_exception(asyncio.CancelledError())` je Eintrag, oder den Docstring auf das tatsächliche Verhalten korrigieren. Beifund beim SHUTDOWN-COROUTINE-Fix, Chat 96. | [BAU] ⬜ Prio mittel — Test-Härtung / Lebenszyklus |
| NODE-TOKEN-AUSLASTUNG-FALLBACK | Beifund Block 3 Teil A (Chat 93): OllamaProvider Token-Auswertung hat undokumentierten Fallback — `prompt_eval_count` mal im `message`-Dict, mal Top-Level. Wirkt wie alter Ollama-Versions-Workaround. Beim Heben des Token-Loggings auf Node-Ebene (Token-Auslastung pro Node) mitdokumentieren oder mit-aufräumen. _(Hinweis: ein übergeordnetes NODE-TOKEN-AUSLASTUNG-Item existiert noch nicht; verwandt zu TOK1 in §7 Infrastruktur. Sobald das Token-Logging-Sprint anlegt wird, dort einhängen.)_ | [BAU] ⬜ Prio niedrig — opportunistisch beim Token-Logging-Heben |
| DIRECTIVE-DATACLASS | `InternalPersonality.directives` ist `list[dict]` mit implizitem Schema `{anweisung, kontext}`. Drei Fremd-Leser lesen die Keys von Hand (`corrector.py:49`, `tribunal.py:127`, `responder.py:465`). Kandidat für eine `Directive`-dataclass — Gegenargument: nur zwei Felder, ein Loader (§11-Faustregel). | [BAU] ⬜ Prio niedrig |
| STATE-LADEZUSTAND | Konzept: `create_state` belegt ladbare Keys mit plausiblen Leerwerten vor (`raw_turns = []`, `base.py:122`) und löscht damit die Unterscheidung „nie geladen" vs. „leer geladen" VOR jeder Validierung. Vorschlag: Value Type mit drei Zuständen (IsSet / HasSucceeded / HasFailed + Wert + Fehler). Der dritte Zustand ist der Gewinn — `session_turns_retrieve` macht bei `JSONDecodeError` ein `continue`: ein korrupter Turn verschwindet lautlos, und `[]` sieht aus wie „Session leer". Kandidaten: `memory_entries`, `session_turns`, `lzg_resonanz`, `aktivierte_ziele`, `prompt_embedding`, `memory_context`. | [BAU] ⬜ Prio mittel |
| LOG-FREMDBIBLIOTHEK-DEBUG | httpcore/httpx/urllib3 loggen HTTP-Header-Wände auf DEBUG. Auf WARNING setzen. | [BAU] ⬜ Prio niedrig |


## PROJEKTSEITE-NACHZIEHEN — die Seite kommt modernisiert wieder (Chat 120)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen; der Eintrag beschreibt ein Ziel und keinen Defekt.

Die Projektseite ist beim Umzug **nicht** mitgezogen. Sie soll nachkommen, und zwar überarbeitet statt eins zu eins übertragen. ⬜ Prio niedrig

**Vorlage und Bestand:** Zweig `pages`, fünf Commits, Spitze `06017c5` — ein eigenständiger Wurzelzweig ohne gemeinsame Basis mit `master`. Inhalt: `index.html`, `index.de.html` und `assets/logo.png`, ein akademisches Whitepaper in zwei Sprachfassungen mit Sprachumschaltung.

> **Wachposten:** Der Zweig liegt **nur lokal**, sobald das alte Repositorium gelöscht ist. Er ist nie auf die neue Plattform gepusht worden, und `master` kennt ihn nicht — die beiden teilen keinen Vorfahren. Wer die Arbeitskopie verliert, verliert die Seite. Vor dem Löschen des alten Repositoriums entweder den Zweig mitpushen oder ihn außerhalb sichern.

**Zu entscheiden, wenn es soweit ist:** ob die Seite wieder ein eigener Wurzelzweig wird oder als Verzeichnis in `master` wandert. Das erste hält Seite und Code getrennt, wie bisher; das zweite macht sie mitversionierbar und Änderungen an ihr im normalen Ablauf sichtbar. Die neue Plattform kann beides bedienen.

**Der inhaltliche Abgleich ist der eigentliche Aufwand, nicht die Technik.** Der Text beschreibt einen Stand von Chat 57. Seitdem sind die Initiative-Achse, die zwei Charakter-Räder, der Gesprächsvektor mit Sektoren und Clustern und der Salienz-Neubau dazugekommen; die kognitive Pipeline ist von 10 auf 13 Knoten gewachsen. Was die Seite über das System sagt, ist an mehreren Stellen überholt und gehört gegen die heutigen Konzeptdokumente geprüft — nicht gegen die Erinnerung.

---


## Epic: Matrix-Kanal + WireGuard-Zugang (Chat 68)

**Vision:** Nova als vollwertiger Chat-Partner über das Matrix-Protokoll, erreichbar von überall per WireGuard-VPN. Im Gegensatz zu Telegram kann Matrix über den Application-Service-Mechanismus *beide* Seiten steuern — User-Nachrichten und Bot-Nachrichten. Damit entfällt die `[Du]`-Krücke: Desktop-Eingaben erscheinen im Matrix-Client als echte User-Nachrichten, Novas Antworten als echte Nova-Nachrichten.

**Leitprinzip:** "Der Kanal ist dumm. Absichtlich." — Gilt weiterhin. Matrix war ein dritter Renderer neben Desktop (GTK4) und Telegram; **seit dem 24.08.2026 sind es zwei** — Telegram ist abgeschaltet. Markdown bleibt das kanonische Format.


### TELEGRAM-GRENZE-STRUKTURELL — was der Kanal nicht kann, und warum es keine Einstellungssache ist

**Kategorie:** [BAU] BAUART

**Zustand:** gegenstandslos seit dem 24.08.2026 — der Telegram-Kanal ist abgeschaltet. **Der Abschnitt bleibt stehen, weil er eine Begruendung traegt und keinen Auftrag:** Wer den Kanal zurueckholen will, findet hier, woran er strukturell scheitert.

**Ein Telegram-Bot hat genau einen Absender: sich selbst.** Die Bot-API kennt keinen Weg, eine Nachricht im Namen eines Menschen in einen Chat zu stellen — nicht als Berechtigung, die man erteilen könnte, sondern als Eigenschaft des Protokolls. Alles, was in diesem Chat erscheint, kommt entweder vom Menschen selbst (über seine App) oder vom Bot.

**Der Nachrichtenfluss macht daraus ein Problem, sobald ein zweiter Client mitspielt.** Novaberg trägt drei Kanäle: Desktop, Telegram, künftig Matrix. Wer am Desktop schreibt, dessen Äußerung geht über `POST /chat` in den Server; der Prompt-Consumer verteilt sie danach als `user_message` an **alle anderen** Clients desselben Menschen (`prompt_consumer.py`, `exclude_client`). Genau dafür ist der Typ da: Der Telegram-Chat soll zeigen, was am Desktop gesagt wurde.

**Nur kann der Bot sie nicht als fremde Äußerung zustellen — er kann sie nur selbst sagen.** In `telegram_bot/bot.py` steht deshalb:

```python
elif typ == "user_message":
    # User-Eingabe von einem anderen Client — als Info anzeigen
    await _nachricht_senden(bot, chat_id, user_id, f"[Du] {user_text}")
```

**Die vier eckigen Klammern sind die ganze Krücke**, und sie kosten mehr als ihr Aussehen:

| Was geschieht | Folge |
|---|---|
| Novas Konto sagt einen Satz des Menschen | Der Verlauf zeigt eine Figur, die den Nutzer zitiert, ohne es zu kennzeichnen — außer durch ein Präfix, das nur ein Mensch versteht |
| Das Präfix ist Text, keine Struktur | Wer den Chat später ausliest, sieht eine Nova-Nachricht. Kein Feld trennt Zitat von Äußerung |
| Antwortbezüge zeigen auf den Bot | Ein Reply auf „seine eigene" Nachricht ist formal ein Reply an Nova |
| Ungelesen-Zähler und Benachrichtigung | Jede eigene Desktop-Eingabe erscheint unterwegs als eingehende Nachricht von Nova |

> **Und es ist keine Einstellungssache, sondern eine Grenze der Bot-API.** Was fehlt, ist nicht ein Schalter, sondern ein zweiter Absender.

**Matrix hat genau diesen zweiten Absender.** Ein Application Service darf innerhalb seines Namensraums im Namen jedes Nutzers senden (`?user_id=` am Client-Server-Endpunkt). Die Desktop-Äußerung wird damit ein Event mit `sender: @meister` — nicht ein Zitat, sondern die Äußerung selbst, mit der Struktur, die jeder Client ohnehin liest. Das Präfix entfällt, weil die Information, die es transportiert, ins Protokoll gehört und nicht in den Text.

**Der Preis steht dabei:** Der Account des Menschen muss im Namensraum des Application Service liegen, damit dieser für ihn sprechen darf. Praktisch heißt das ein gemeinsamer Account statt zweier Identitäten — entschieden am 23.08.2026 (Chat 160).

**Architektur:**

1. **Matrix-Homeserver** — Synapse oder Dendrite, lokal auf der Novaberg-Maschine. Kein Cloud-Dienst, kein föderierter Zugang (optional später).
2. **Zwei Accounts** — `@meister:novaberg.local` (User) + `@nova:novaberg.local` (Charakter) in einem gemeinsamen Room.
3. **Application Service (AS)** — Novaberg registriert sich als AS beim Homeserver. Kann als beide Accounts schreiben. Empfängt Room-Events per Callback.
4. **Novaberg-Integration** — Analog zum Telegram-Bot: fire-and-forget POST /chat + WebSocket-Listener. Aber zusätzlich: User-Nachrichten von anderen Clients werden als `@meister` in den Room geschrieben (nicht als Bot-Nachricht).
5. **WireGuard-VPN** — Server auf der Novaberg-Maschine, Client auf dem Handy (e/OS, F-Droid). Kein offener Port, kein externer Server. Voller Zugriff auf lokales Netz (Matrix, REST-API, Panels, Docker).
6. **Matrix-Client** — FluffyChat auf e/OS (F-Droid), Fractal auf dem Desktop (GTK4, Flathub). Verbindet sich über VPN-Tunnel auf den lokalen Homeserver. Die Client-Wahl ist keine Architekturentscheidung: Das Puppeting läuft im Application Service, serverseitig. Jeder spezifikationskonforme Client zeigt `@meister` und `@nova` als getrennte Absender. Ausschlaggebend für FluffyChat ist UnifiedPush — ohne Play Services auf e/OS ist FCM kein gangbarer Push-Weg. Ausschlaggebend für Fractal ist GTK4: gleiche Toolkit-Familie wie der bestehende Desktop-Client, ein Widget-Set weniger im System.

**Vorteil gegenüber Telegram:**

| Aspekt | Telegram | Matrix |
|--------|----------|--------|
| User-Nachrichten einspeisen | ❌ Nur Bot-Messages | ✅ AS kann als beliebiger User schreiben |
| Datenhaltung | Telegram-Cloud | Lokal (Homeserver auf eigener Maschine) |
| Erreichbarkeit unterwegs | Internet (Telegram-API) | WireGuard-VPN (kein offener Port) |
| Client-Verfügbarkeit | Telegram-App | FluffyChat (F-Droid) / Fractal (Flathub) |
| Protokoll | Proprietär | Offen (Matrix-Spezifikation) |

**Bestandteile:**

| # | Arbeitspaket | Beschreibung |
|---|-------------|-------------|
| 1 | WireGuard-Server | Installation + Konfiguration auf der Novaberg-Maschine (Nobara/Fedora) |
| 2 | WireGuard-Client | Konfiguration auf e/OS Handy, Verbindungstest |
| 3 | Matrix-Homeserver | Synapse als Docker-Service im Compose-Stack. Synapse statt Dendrite, weil Simplified Sliding Sync nativ ab 1.114 (relevant für Element-X-basierte Clients als spätere Option) |
| 4 | TLS-Zugang | Reverse Proxy mit gültigem Zertifikat vor Synapse. Clients lehnen `http://` gegen den Homeserver ab. Entweder eigene CA (Root-Cert auf jedem Gerät) oder echtes Zertifikat für eine Subdomain, die intern auf die VPN-IP zeigt. Blockiert AP 8 |
| 5 | Account-Setup | Zwei Accounts anlegen, Room erstellen, Berechtigungen |
| 6 | Application Service | AS-Registrierung, Event-Callback, Nachrichtensteuerung als beide User |
| 7 | Novaberg-Connector | `matrix_bot/bot.py` analog zu `telegram_bot/bot.py` — POST /chat + WebSocket-Listener + user_message-Einspeisung als `@meister` |
| 8 | Client-Test | FluffyChat auf e/OS über VPN, Fractal auf dem Desktop, bidirektionaler Nachrichtentest |

~~**Priorität:** Niedrig — Telegram funktioniert, Matrix ist Kür. Aber architektonisch sauber und privacy-konform.~~

✅ **Prototyp gebaut am 23.08.2026.** Fünf der acht Arbeitspakete stehen: Homeserver (3), Accounts (5), Application Service (6), Connector (7) — dazu WireGuard (1, 2) vom Auftraggeber. **Gemessen im Raumverlauf:** drei Nachrichten, zwei Absender, kein `[Du]`-Präfix. Die dritte Zeile kam über `POST /chat` mit `client_id=desktop` und steht im Raum als Nachricht von `@meister` — genau der Fall, den Telegram nicht tragen kann.

✅ **Am 23.08.2026 ergänzt: Postgres statt SQLite, und der Client ist verbunden.** Sieben der acht Arbeitspakete stehen.

| # | Was | Zustand |
|---|---|---|
| 4 | TLS-Zugang | **zurückgestellt, nicht erledigt.** FluffyChat nimmt `http://` an — die Frage war ungeprüft und ist am Gerät beantwortet. Unverschlüsselt geht damit im heimischen WLAN jedes Passwort und jeder Nachrichtentext im Klartext; innerhalb des VPN-Tunnels ist die Strecke bereits verschlüsselt |
| 8 | Client-Test | ✅ **verbunden.** In der Ereignistabelle liegen Turns aus der App |

**Die Migration nach Postgres in Zahlen:** Datenbank `synapse` mit `LC_COLLATE=C` angelegt (für Synapse zwingend, nachträglich nur über einen Neuaufbau änderbar), `synapse_port_db` gelaufen, danach **6 Tabellen auf beiden Seiten gezählt — 0 Abweichungen**. Ein echter Turn danach: `events` 22 → 23. `gedaechtnis` blieb unberührt, die SQLite-Datei liegt als Rückweg daneben.

**Der Grund für den Wechsel war nicht technische Not, sondern Systemzahl:** Ein Stapel mit einer Datenbank ist einfacher zu sichern und zu verstehen als einer mit zweien, und dieser Gewinn fällt täglich an.

**Zustand:** Synapse als eigener Compose-Dienst, aus dem lokalen Netz erreichbar (`/_matrix/client/versions` → 200). Der Connector läuft daneben, ein Raum je Paar. Die Zugangsdaten liegen außerhalb des Repositoriums. Konzept: `novaberg-matrix-kanal_k.md`.

**Seit dem 24.08.2026 aus dem Repositorium herstellbar.** Beide Compose-Dienste stehen in der Vorlage, drei Muster mit leeren Geheimnissen unter `novaberg/matrix/`, Aufbauanleitung in beiden READMEs (Schritt 6). Gegengehalten: 16 von 16 Schlüsseln der `homeserver.yaml`, 6 von 6 der AS-Registrierung, keine Abweichung außer den geleerten Werten. **Das war kein Arbeitspaket dieses Epics** — die acht beschreiben, was der Kanal *kann*, keins beschreibt, ob ihn jemand anders aufbauen kann.

~~**Telegram bleibt unangetastet und läuft parallel.** Ein Kanal wird abgeschaltet, wenn der andere gemessen trägt — der Handy-Test steht noch aus.~~ → **Am 24.08.2026 eingelöst.** Die Bedingung war AP 8, und AP 8 steht seit dem 23.08.2026 auf ✅. **Telegram ist abgeschaltet:** Behälter `ki_telegram` gestoppt und entfernt, Compose-Block aus Betriebsdatei und Template genommen; `telegram_bot/` bleibt liegen. Der Server meldete `WebSocket getrennt: 'meister' (client=telegram, 2 verbleibend)`. **Nebenbei gemessen, über dieselben 24 Stunden davor:** `ki_telegram` 144 WebSocket-Abbrüche mit Reconnect, `ki_matrix_bot` **0**. Offen bleibt allein der Widerruf des Bot-Tokens beim BotFather — ein gestoppter Behälter widerruft nichts. **Am 24.08.2026 ausdrücklich zurückgestellt**, nicht übersehen: Das Token in `.env` bleibt bis dahin gültig. Die Gegenseite ist klein — der Dienst läuft nicht mehr, also erreicht nichts, was jemand über dieses Token sendete, Novaberg —, aber der Bot kann in seinem Namen weiter senden, solange das Token lebt.

**Voraussetzung:** WS-SINGLE Fix (Chat 68, ✅), ClientConnection mit client_id/character_id-Filterung (Chat 68, ✅).

**Offene Punkte (Chat 160):**

1. **Push versus VPN-Tunnel.** Der Homeserver ist nur erreichbar, solange WireGuard steht. Ohne dauerhaften Tunnel kommt ein Impuls von Nova erst an, wenn die App geöffnet wird. Zu klären: WireGuard-Keepalive dauerhaft aktiv (Akkukosten messen) oder Push-Gateway außerhalb des Tunnels. Beides betrifft nur die Erreichbarkeit unterwegs, nicht den Nachrichtenfluss im lokalen Netz.
2. **UnifiedPush-Verteiler.** FluffyChat braucht einen Verteiler (ntfy oder vergleichbar). Ob der lokal betrieben werden kann oder eine öffentlich erreichbare Instanz braucht, ist nicht geprüft — hängt an Punkt 1.
3. **Element X als spätere Option.** Element X ist deutlich performanter als die Classic-Generation, setzt aber Simplified Sliding Sync voraus (mit AP 3 gegeben) und der Push-Weg ohne Play Services ist ungeprüft. Nicht für den Erstaufbau, aber nach AP 8 als Vergleich sinnvoll.

---


## EPIC-MS-MODELL-QUEUE — die Modellaufrufe bekommen eine Warteschlange ✅

**Kategorie:** [BAU] BAUART

**Status:** ✅ MS-Welle vollständig abgeschlossen (Block 1–5). Block 1 (Chat 92), Block 2 + Block 3 (Chat 93/94), Block 5 (Chat 96), Block 4 + Inbetriebnahme + Pixie-Reaktivierung (Chat 97).
**Bezug:** novaberg-memory-synapsen-p4-entscheidungen_k.md (Chat 91), Audit-Ausgaben Chat 91, novaberg-microservice-modell-queue_k.md
**Vorbedingung:** Keine — kann parallel zur Bestands-Pipeline aufgebaut werden, Migration erfolgt Pfad für Pfad.


### Phasen-Übersicht

| Phase | Inhalt | Status |
|---|---|---|
| Punkt 1 | Konzeptpapier `novaberg-microservice-modell-queue_k.md` | ✅ Chat 92 |
| Punkt 2 | Audit-Konsolidierung (Temperatur-pro-Call ✅ Chat 91, Microservice-Vorbereitung ✅ Chat 91) | ✅ Chat 91 |
| Block 1 | Embedding-Konsolidierung (zwei Pfade → einer, Queue/Worker) | ✅ Chat 92 |
| Block 2 | `pixie_llm_call`- und `OllamaProvider.chat`-Konsolidierung zu Worker-Schnittstelle: ChatWorker (gemma4-gpu) + BackgroundWorker (qwen36-cpu). system-Prompt + vollständigen Parameter-Satz durchreichen, CJK-Guard und JSON-Validierung in den Worker heben. Vorbild: EmbedWorker aus Block 1. | ✅ Chat 93/94 |
| Block 3 | `think`-Parameter pro Call (Hartkodierung entfernen, node-spezifische Politik) — inkl. Teil-2-Kahlschlag | ✅ Chat 93/94 |
| Block 5 | `num_ctx` pro Call durchreichbar machen | ✅ Chat 96 |
| Block 4 | Connector-Erweiterung für Qwen 3.6 (neuer Connector `qwen36`, GPU=`gemma4-gpu` / CPU=`qwen36-cpu`) — bewusst ans Ende der MS-Welle terminiert | ✅ Chat 97 |
| Punkt 8 | Inbetriebnahme — `OLLAMA_CONNECTOR: qwen36` als Compose-Env aktiviert (Code-Default bleibt `gemma4` als Fallback-Anker), alte CPU-Modelle gelöscht (Gemma4-CPU, Qwen3-32B-CPU, drei Mistral-Varianten, ~105 GB) | ✅ Chat 97 |
| Punkt 9 | Pixie-Reaktivierung (`PIXIE_AKTIV=True` per Env) — Pixie verifiziert auf qwen36-cpu, BackgroundWorker-Submit-Timeout-Default auf 300 s (Variante B, pro Call überschreibbar, Chat/Embed bleiben bei 60 s) | ✅ Chat 97 |


### Hintergrund

Audit 3 (Temperatur-pro-Call, Chat 91) hat bestätigt: das Pattern „ein Modell, viele Temperaturen pro Call" trägt für die Chat-Pipeline produktiv — `gemma4-gpu` läuft mit sieben verschiedenen Temperaturen aus 18 verschiedenen Aufrufer-Stellen, alle Parameter sauber durch `_build_options` ins Ollama-`options`-Dict. Damit ist die Architektur-Voraussetzung für die Modell-Konsolidierung gegeben.

Audit 4 (Microservice-Vorbereitung, Chat 91) hat fünf strukturelle Defizite aufgedeckt, die die Konsolidierung blockieren würden:

1. **Zwei parallele Embedding-Pfade** — `embedding_manager` (Singleton, Pixie-Pfade) und freie Funktion `embedding_create()` (Live-Pipeline) tun dasselbe gegen denselben GPU-Client, ohne Konkurrenz-Schutz. Embeddings können mit Chat-LLM-Calls auf demselben Client kollidieren, ohne dass `llm_lock` greift.
2. **`pixie_llm_call` als zweite Aufruf-Schicht** — umgeht `get_node_config`, reicht `system` nicht durch, ignoriert fünf von acht Generation-Parametern (`top_p`, `repeat_penalty`, `presence_penalty`, `max_output_tokens`, `num_ctx`).
3. **`think=False` hartkodiert** in `OllamaProvider.chat:202` — `OLLAMA_THINK_DEFAULT` aus dem Connector wird in `get_node_config` eingewoben, aber im Provider überschrieben. `NODE_LLM_CONFIG[thinker]["think"] = True` ist toter Code.
4. **`num_ctx` provider-fix**, nicht pro Call — Edge-Cases (kurze Klassifikation vs. lange Destillation) nicht differenzierbar.
5. **Konnektoren noch auf alte Modell-Topologie** — neuer Connector `qwen36` muss eingeführt werden, damit Pixie auf das in Chat 91 verifizierte Qwen 3.6-35B-A3B umstellen kann.


### Verifizierte Modell-Wahl Qwen 3.6 (Chat 91)

Sieben Tests gegen `qwen3.6:35b-a3b` (Q4_K_M, 23 GB) auf der CPU haben das Modell für alle Pixie-Workloads validiert:

| Test | Modus | Zeit | Befund |
|---|---|---|---|
| A1 | Klassifikation Grenzfall, think | 4–5 min | Interpretativ („erinnerung"), abweichend von Regel-Schema |
| A1 | Klassifikation Grenzfall, nothink | 13 s | Regelkonform („gemischt"), strikter |
| A2 | Klassifikation eindeutig, think | 2:16 min | „fakt" — null Reasoning-Mehrwert sichtbar |
| B1 | Destillation Apfelbaum, think | 4–5 min | Abstrakt, sachlich |
| B1 | Destillation Apfelbaum, nothink | 6 s | Konkreter, alle Aspekte abgedeckt |
| B2 | Destillation Frust, nothink | 8 s | Emotionalen Kern getroffen, idiomatisch |
| C1/C2 | Aussagen-Vergleich, think vs nothink | 2:30 min vs. 15 s | Identische Antwort, Konfidenz identisch |
| C2b | Echte Unabhängigkeit, nothink | 18 s | Sauber „unabhaengig", Konfidenz 1.0 |

**Konsolidiertes Verdikt:** JSON-Stabilität perfekt, deutsches funktionales Deutsch idiomatisch, Reasoning bei klaren Aufgaben zuverlässig, CPU-Last 51% bei 62 °C (statt vorher 90 °C bei Zwei-Modell-Setup). Geschwindigkeit ohne Thinking 6–18 s — interaktiv brauchbar.

**Think-Politik empirisch begründet:** Thinking ist bei Klassifikation/Destillation kontraproduktiv (führt zu Über-Interpretation der Aufgabe). Default `think=False` für alle Pixie-Nodes. `think=True` nur für explizit reasoning-bedürftige Nodes (`thinker` — Recherche-Planung).


### Modell-Topologie nach Inbetriebnahme

| Rolle | Modell heute | Modell nach MS-Welle |
|---|---|---|
| Live-Konversation (Nova-Stimme) | gemma4-gpu | gemma4-gpu (unverändert) |
| Pixie Sprache | gemma4-cpu | **qwen36-cpu** |
| Pixie Analyse | qwen3-32b-cpu | **qwen36-cpu** (selbes Modell!) |
| Embedding | nomic-embed-text (GPU) | nomic-embed-text (GPU, unverändert) |
| Fallback Mistral | mistral-small3.2-* | gelöscht |

**Plattenplatz-Gewinn:** ~52 GB nach Löschung der vier abgelösten Modelle (gemma4-cpu 17 GB, qwen3-32b-cpu 20 GB, drei Mistral-Varianten 45 GB).


### Scope-Definition

**Im Welle-Scope:** Konzeptpapier, Embedding-Konsolidierung, `pixie_llm_call`-Konsolidierung, `think`-Politik pro Call, Connector-Erweiterung, `num_ctx`-Durchreichung, Modell-Konsolidierung, Pixie-Reaktivierung.

**Außerhalb des Scopes:** Synapsen P4 (eigenes Epic, wartet darauf), CharacterGraph-Strukturen, KZG-Schreibpfad, Pipeline-Log-Architektur, sternförmiger Orchestrator-Graph (Vision für später).


### Folgewirkung auf offene Bugs

Voraussichtlich strukturell obsolet oder gelöst nach Umbau:

- **PIX-GPU-IDLE** — Mechanik wird durch Queue-Priorität ersetzt. Feature-Flag und Code entfallen.
- **PROMO-QUEUE-SCHWELLE-ASYMMETRIE** — bereits durch Pre-P4-Fix erledigt, Doku-Drift wird Teil der MS-Welle.
- Zwei Embedding-Pfade und Kapselungs-Bruch in PromotionAgent (`embedding_manager._client/._model`).

Endgültige Re-Evaluation in Punkt 9 (Pixie-Reaktivierung).


### Verhältnis zum Synapsen-Memory-Kern-Umbau

P4 setzt **strukturell** auf der MS-Welle auf: der neue Pixie-Agent `synapsen_promotion` ruft Embedding über die konsolidierte Schnittstelle, schreibt in `lzg_knoten`/`lzg_kanten` über die Microservice-Queue. Ohne MS-Welle würde P4 auf brüchiger Grundlage aufsetzen — zwei Embedding-Pfade in einem neuen Agent, `think=False`-Hartkodierung blockiert Qwen-3.6-Thinking für die Klassifikations-Logik.

K-Punkte für P4 sind unabhängig von der MS-Welle bereits in Chat 91 abgeschlossen (`novaberg-memory-synapsen-p4-entscheidungen_k.md`). Implementation wartet auf MS-Welle-Abschluss.


### Block 3 — Offene Restpunkte (Chat 93)

Block 3 (think pro Call + Thinking-Normalizer + Self-Trigger) ist code-vollständig. Zwei Rest-Sprints und ein Beobachtungs-Punkt bleiben:

- **Block 3 Teil 2 — Kahlschlag (offen):** `generate` aus OllamaProvider + AnthropicProvider + LLMProvider-ABC entfernen (belegt tot, Worker nutzen nur `chat`); tote `format_json`-Pfade in beiden Providern; die drei Postprocess-Duplikate (`_clean_json_response` / `_deduplicate_repetition` / `_repair_truncated_json`); `init_providers` + tote Modul-Variablen (`_chat` / `_background` / `_background_analyse_provider`); `OLLAMA_THINK_DEFAULT` + `node_cfg["think"]` + Connector-`think`-Feld; Worker-interne `parsed`-Type-Hints auf `Optional[Any]` nachziehen. Reiner Code-Tod, verhaltensneutral. Vor dem Löschen frischer Verifikations-Grep — die Datei hat sich seit Block-3-Audit durch das `thinking`-Feld + Normalizer geändert.
- **Block 3 Diagnose-Logging-Ausbau (offen):** `DIAGNOSE`- und `DIAGNOSE-VOLL`-Logging in `OllamaProvider.chat` entfernen. Gekoppelt an THINKER-DOPPELFEHLSCHLAG-LIVE-VERIFIKATION (s.u.) — erst entfernen, wenn der Self-Trigger-Pfad einmal live gefeuert hat. Gut mit dem Kahlschlag zusammenlegbar.
- **THINKER-DOPPELFEHLSCHLAG-LIVE-VERIFIKATION (offen, abwartend):** Self-Trigger-Notnagel (Block 3 Teil D+E+F) ist gebaut und logisch belegt, aber der Doppel-Fehlschlag (beide Nachfass-Iterationen liefern leeren `content`) ist im Live-Betrieb noch nie gefeuert. Abwarten — tritt im Normalbetrieb auf, wenn `gemma4` zweimal hintereinander ins `thinking`-Feld driftet. Verifikations-Log: „Doppel-Fehlschlag — Self-Trigger gesetzt" → „continue erzeugt" → „Unsicherheits-Retry erkannt". Erwartetes User-Erlebnis: erste Antwort + „Hmm... ich muss das nochmal durchgehen.", dann zweite Nachricht mit Klärung. Kein eigener Bau — nur Beobachtung. Löst den Diagnose-Logging-Ausbau aus.

---


## Herkunft: was der Reducer-Umbau offengelassen hat

> **Nur als Herkunft.** Dieser Abschnitt ist selbst ein Eintrag und steht in [`novaberg-backlog-antwortpfad.md`](novaberg-backlog-antwortpfad.md); hier stehen die Eintraege darunter, die zu diesem Gegenstand gehoeren.

### LOGGER-NAMESPACE

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die im Befund genannte Stelle ist in dieser Form nicht mehr auffindbar; ohne den alten Wortlaut ist nicht zu entscheiden, ob sie entfallen oder umgeschrieben wurde. **Unbelegt, nicht erledigt.**

**Symptom:** Reducer-Logger heißt `graph.nodes.reducer` (über `logging.getLogger(__name__)`), während der Rest des Servers über das `ki_server.<modul>`-Schema loggt. Folge: `grep "ki_server"` über das Log-Archiv erfasst den Reducer nicht.
**Fix:** Reducer-Logger-Name entweder explizit auf `ki_server.reducer` setzen oder zentrale Logging-Konfiguration so anpassen, dass alle `graph.*`-Module das Präfix erben.
**Prio:** Niedrig — kosmetisch, kein funktionaler Schaden.


### INIT-SQL-VERALTET — init.sql nicht reproduzierbar

**Kategorie:** [BAU] BAUART

**Status:** ⬜ Offen
**Entdeckt:** Chat 85 (Brudi-Befund bei Promotion-Fix-Recherche)

**Symptom:** `db/init.sql` enthält ALTER-TABLE-Statements und repräsentiert nicht den Soll-Zustand des Schemas. Tabelle `ziele` fehlt komplett (existiert in der Live-DB, wurde aber nie ins `init.sql` aufgenommen).

**Auswirkung:** Setup-from-scratch ist nicht reproduzierbar. Frischer Container plus `init.sql` ergibt kein lauffähiges System.

**Lösung:** `init.sql` neu aufbauen als CREATE-only-Definition aller Tabellen plus Indizes. ALTER-Anweisungen entfernen oder in versioniertes Migrations-Skript verschieben (Alembic empfohlen).

**Vorbedingung:** Keine.
**Prio:** Mittel — wird im Rahmen des Code-Audit-Sprints adressiert.


## Cleanup: LZG-DOKU-DRIFT — `novaberg-mem-lzg.md` reflektiert nicht das Live-Schema

**Kategorie:** [BAU] BAUART

**Status:** Beobachtet
**Entdeckt:** Chat 84 (M3-D, beim Doku-Synchronisations-Audit)

**Symptom:** Die Schema-Tabelle in `novaberg-mem-lzg.md` §2 listet 13 Spalten, die Live-DB-Tabelle `langzeitgedaechtnis` hat 24 Spalten. Fehlend in der Doku:
- Fünf Magnet-/Meta-Spalten (`themen`, `gedaechtnistyp`, `kzg_erstellt_am`, `entitaet_ids`, `timeline_id`) — seit Chat 78 im Schema, in M3-D nur die zwei M3-relevanten ergänzt
- Sechs EI-Metadaten-Spalten (`intentionen`, `emotion`, `modus`, `sprach_stil`, `beziehungs_dynamik`, `tone`) — nur summarisch im Hinweis-Block erwähnt, nicht einzeln tabelliert

**Auswirkung:** Niedrig in der Praxis (Code arbeitet korrekt), aber strukturell unsauber. Neue Mitwirkende oder spätere Audits müssen aus dem Quellcode rekonstruieren, was die Spalten bedeuten. Drift verstärkt sich mit jeder weiteren Schema-Erweiterung, wenn nicht aktiv synchronisiert wird.

**Lösung:** Eigenständiger Doku-Refresh-Sprint — Live-Schema komplett gegen Doku abgleichen, alle Spalten dokumentieren, Schreibpfade pro Spalte benennen (Promotion, Cluster-Promotion, EI-Calc-Node, …), Reader pro Spalte benennen (Retrieval, Charakter-Hash, …). Eventuell auch §5 "Schreibpfade" erweitern um vollständige Pro-Spalte-Provenance.

**Vorbedingung:** Keine.
**Prio:** Mittel — kein akuter Schaden, aber die Drift hält Doku unzuverlässig.

**Verwandt:** Audit-Empfehlung Chat 84 — alle Convention-Dokumente vollständig lesen, nicht aus Stichproben Schlüsse ziehen. LZG-Doku ist ein Beispiel für nicht-Convention-Doku, die ähnlich aktiv gepflegt werden müsste.

---


## EPIC-EVA-DISZIPLIN — Zusicherungen im ganzen Bestand

**Kategorie:** [BAU] BAUART

**Status:** ⬜ Geplant (nach M5)
**Auslöser:** Chat 85 — Pixie-Schleife durch fehlende EVA-Disziplin

**Erkenntnis:** Der Promotion-Bug war Symptom einer fehlenden Codequalitäts-Übereinkunft. Brudi-erzeugter Code hatte keine verbindlichen EVA-Standards. Allgemeines Lesson in `novaberg-lesson_l_silent-skip.md`.

**Phase 1 — Standards etabliert (Chat 85):**

- `docs/DEVELOPER_HANDBOOK.md` angelegt, 12 Paragraphen
- §1 Leitprinzipien, §2 Funktionsanatomie, §3 EVA-Disziplin, §4 Logging-Standards, §5 Modul-Struktur, §6 Sprache, §7 Naming, §8 DB-Disziplin, §9 Redis-Disziplin, §10 Worker-Disziplin, §11 Tests, §12 Review-Pflicht
- Modul-Topologie (§5) zunächst als Platzhalter, wird nach Brudi-Scan konkretisiert

**Phase 2 — Codebase-Inventar (in Vorbereitung):**

- Brudi-Scan über `server/`-Tree, Output in `reviews/codebase-inventar.md` (parallel zu `novaberg/`, außerhalb Repo)
- Sechs Funktionskategorien: Mathematik, Vektoren/Embeddings, Emotionen, Decay/Zeit, Salienz/Scoring, Plausibilitäts-Checks
- Pure vs. seiteneffektbehaftete Funktionen markiert
- Aus Ergebnis: konkrete `lib/`-Topologie ableiten, in Handbuch §5 einbauen

**Phase 3 — Systematische Härtung (Sprint-Block):**

- EVA-Audit aller Pixie-Agenten: Recherche, Decay, Charakter-Hash, Wiedervorlage, Ziel-Decay (Promotion gefixt in Chat 85)
- EVA-Audit Memory-Pipelines: KZG-Schreiben, LZG-Schreiben, Cluster-Promotion, Salienz-Berechnung
- EVA-Audit LangGraph-Nodes: HumanGraph, CharacterGraph, AgentGraph
- `init.sql` neu aufbauen (siehe INIT-SQL-VERALTET): CREATE-only, Tabelle `ziele` ergänzt, ALTER-Anweisungen in versioniertes Migrations-Skript verschieben
- Setup-from-scratch verifizieren

**Konkrete Stellen aus Welle-B-Audit (Chat 90, Doku-Sync Teil 2):**

Fünf identifizierte EVA-/Fail-Loud-Verstöße in den Graph-Nodes, die beim Code-Audit mit-bearbeitet werden sollten:

- `enricher.py:431` — Plugin-Exception wird gefangen, mit `logger.error` gemeldet, aber ohne `hintergrund_log`-Audit-Eintrag. Plugin-Manager-Liste läuft schweigend weiter.
- `perzeption.py:159` — JSON-Decode-Fehler werden mit `logger.warning` geloggt, dann fallen Default-Werte ins State. Kein Audit, kein Fail-Loud — Symptom-frei genau wie SPRACH-STIL-DEFENSIV-STUMM.
- `ei_calc.py:46` — Unbekannte Rolle führt zu `logger.warning` + Silent-Fallback auf `_ei_calc_user`. Verstößt gegen „fail loud" (Handbuch §1).
- `ei_calc.py:64-66, 201-204` — `external` und `internal` werden bei Bedarf spontan via `Personality()` / `InternalPersonality()` instanziiert. EVA-Disziplin (Handbuch §3) würde harte Vorbedingungs-Prüfung + Fail-Loud verlangen, weil eine fehlende Personality strukturell auf einen kaputten Lade-Pfad hindeutet (z.B. `db_zugriff` nicht gelaufen).
- `salience.py:85` — Catch-all `Exception` im Segmentierer, nur `logger.warning`, kein Audit-Eintrag.

Diese fünf Stellen sind Pattern-Geschwister zu `_sprach_stil_erkennen` (siehe Bug SPRACH-STIL-DEFENSIV-STUMM, Chat 89/90). Gemeinsame Ursache: Stille Defaults und Catch-all-Exceptions, die strukturelle Drift maskieren.

**Aufwand:** 2-3 Sprints à 1-2 Tage. Reihenfolge: erst Agenten (akute Defekte), dann Memory (größter potenzieller Schaden), dann Graphs, `init.sql` zum Schluss.

**Priorität:** Hoch. Eingeordnet nach M5 (Salienz-Pfad-Erweiterung) und M3b (Magnet-Felder).

---


## Refactor: REDUCER-LOGGER-NAME-KONVENTION — Logger-Namen weichen von der Codebase-Konvention ab (Chat 90)

**Kategorie:** [BAU] BAUART

**Status:** ⬜ Latent (Audit-Befund), nicht implementiert
**Prio:** Niedrig
**Auslöser:** Reducer-Audit (Chat 90, Doku-Sync-Nachzug)
**Sprint-Empfehlung:** Opportunismus — beim nächsten Anfassen des Reducer- oder Formatter-Codes mit-korrigieren, kein eigener Sprint.

**Beobachtung:** Reducer und Formatter nutzen `logging.getLogger(__name__)`, was zu Logger-Namen `graph.nodes.reducer` und `graph.format.memory_context` führt. Die etablierte Codebase-Konvention ist `ki_server.` (z.B. `human_graph.py:27` mit `getLogger("ki_server.graph.human")`).

**Stellen:**
- `reducer.py:18` — `logger = logging.getLogger(__name__)`
- `format/memory_context.py:21` — `logger = logging.getLogger(__name__)`

**Wirkung:** Inkonsistente Log-Namen erschweren das Filtern in zentralen Log-Aggregatoren. Funktional kein Bug — Logs werden geschrieben, nur unter einem nicht-konventionellen Namen.

**Tech-Debt seit Chat 75** (im damaligen Implementierungs-Bericht `docs/archive/novaberg-reducer-umbau_k.md` §13 dokumentiert, bis heute nicht abgetragen).

**Lösungsraum:**

(a) **Beide Logger umbenennen** auf `ki_server.graph.reducer` und `ki_server.graph.format.memory_context`. Zwei Zeilen, keine API-Auswirkung.

(b) **Allgemeiner Logger-Konvention-Sweep** — alle Module mit `getLogger(__name__)` auf die `ki_server`-Konvention ziehen. Größerer Refactor, gehört eher zum Code-Audit-Sprint-Epic (Phase 3).

**Empfehlung:** (a) opportunistisch beim nächsten Reducer-Anfassen. (b) als Erweiterung des Code-Audit-Epics, wenn die Inkonsistenz auch in anderen Modulen identifiziert wird.

---


## Refactor: REDUCER-CONFIG-DEAD-KONSTANTEN — Tote Konstanten in config.py (Chat 90)

**Kategorie:** [BAU] BAUART

**Status:** ⬜ Latent (Audit-Befund), nicht implementiert
**Prio:** Niedrig
**Auslöser:** Reducer-Audit (Chat 90, Doku-Sync-Nachzug)
**Sprint-Empfehlung:** Opportunismus — bei nächster config.py-Berührung mit-entfernen.

**Beobachtung:** Zwei Konstanten existieren weiterhin in `config.py`, werden aber nirgends im Code gelesen:

- `config.py:1022` — `REDUCER_AKTIV: bool = True`
- `config.py:1027` — `REDUCER_LOG_REMOVED: bool = True`

`grep` über `reducer.py` und die gesamte `server/`-Tree liefert für beide Konstanten null Treffer (außer den Definitions-Zeilen selbst).

**Tech-Debt seit Chat 75** (im damaligen Implementierungs-Bericht `docs/archive/novaberg-reducer-umbau_k.md` §13 dokumentiert, bis heute nicht abgetragen).

**Wirkung:** Karteileichen erzeugen Verwirrung — wer die config.py durchgeht und „Reducer aktivieren?" liest, vermutet einen Kill-Switch, der nicht existiert.

**Lösungsraum:**

(a) **Entfernen** — zwei Zeilen aus config.py raus, knapper Commit-Body-Kommentar zur Historie.

(b) **Wieder verdrahten** — `REDUCER_AKTIV` als echter Kill-Switch im Reducer (`if not REDUCER_AKTIV: return state`), `REDUCER_LOG_REMOVED` als Detail-Log-Verbose-Toggle. Symbolismus-Risiko, weil der Reducer in Chat 75 als unbedingt-aktiv eingestuft wurde.

**Empfehlung:** (a). Tote Konstanten sind echte Karteileichen, kein potentieller Ein-Aus-Mechanismus.

---


## Refactor: WORKER-TIMEOUT-MUSTER-DIVERGENZ — `num_ctx` (Per-Call) vs. `submit_timeout` (Worker-Default) (Chat 97)

**Kategorie:** [BAU] BAUART

**Status:** ⬜ Offen
**Prio:** Niedrig — beide Muster funktional korrekt, reine Konsistenz-Frage
**Auslöser:** Block 4 (Chat 97) — Einführung `MODEL_BACKGROUND_TIMEOUT_S`

**Beobachtung:** Die MS-Welle hat zwei konzeptionell gleiche Sachverhalte (Worker-Parameter mit sinnvollem Default + pro Call überschreibbar) mit zwei unterschiedlichen Mustern gelöst:

- `num_ctx` (Block 5): reines Per-Call-Override am Request-Dataclass (`BackgroundRequest.num_ctx: Optional[int] = None`, `ChatRequest.num_ctx`), Worker reicht via `is not None`-Guard durch, Provider-Default greift wenn nichts gesetzt. **Variante A** — kein Worker-Default.
- `submit_timeout` (Block 4, Chat 97): Worker-Instanz-Default per Konstruktor injiziert (`BackgroundWorker._default_submit_timeout`), `submit_sync`-Override mit `timeout: float | None = None` fällt auf den Instanz-Default zurück. **Variante B** — Worker-Default plus pro Call überschreibbar.

**Auswirkung:** Keine funktionale — beide Muster tun das Richtige. Dokumentationelle und kognitive Last: ein Leser muss sich zwei Muster für dieselbe Klasse von Problem merken, und neue Worker-Parameter brauchen jedes Mal eine Stil-Entscheidung.

**Lösungsraum:** Konsistenz-Option ist, `num_ctx` später auf das Worker-Default-Muster (B) nachzuziehen — Konstruktor-Parameter `default_num_ctx`, Instanz-Feld `_default_num_ctx`, im `_kwargs_fuer_call`-Helfer auf den Instanz-Default zurückfallen wenn `request.num_ctx is None`. Konfigurations-Konstante `MODEL_BACKGROUND_NUM_CTX_DEFAULT` analog zu `MODEL_BACKGROUND_TIMEOUT_S`.

**Empfehlung:** Niedrige Prio — nicht eilig. Aufgreifen, wenn ohnehin am `num_ctx`-Pfad gearbeitet wird, oder als Aufräum-Sprint nach P4-Stabilisierung.

---


## Doku-Sprint: DOKU-DRIFT-WELLE-PROMOTION — Sieben Drift-Punkte aus PromotionAgent-Audit (Chat 91)

**Kategorie:** [BAU] BAUART

**Status:** ⬜ Beobachtet, nicht implementiert
**Prio:** Niedrig — Doku stirbt mit dem alten Code in P9
**Auslöser:** PromotionAgent-Audit 1 (Chat 91)

**Beobachtung:** Audit 1 hat sieben konkrete Drift-Stellen zwischen `novaberg/docs/novaberg-pixie-promotion.md` und dem Live-Code im alten `PromotionAgent` aufgedeckt:

1. **Methoden-Namen:** Doku §10 nennt `_call1_klassifizieren` / `_call2_fakten_extrahieren`, Code hat `_klassifiziere` / `_extrahiere_fakten`.
2. **Schwellen-Widerspruch:** Doku §7.1 nennt `CLUSTER_THEMEN_SIMILARITY = 0.75`, Doku §9 listet korrekt 0.85, Code nutzt 0.85.
3. **Modell-Trennung:** Doku §9 trennt Analyse- und Sprach-Modell für die zwei Calls, Code geht für beide Calls über `get_background_provider()` (selbes Modell).
4. **Prompt-Lokation:** Audit-Vorlage erwartete Prompts in `prompts/default/...`, alle Promotion-Prompts sind als f-Strings im Code hartkodiert.
5. **`hash_dirty` paar-spezifisch:** Code nutzt `hash_dirty:{user_id}:{character_id}`, Doku §6 dokumentiert vereinfacht `hash_dirty:{user_id}`.
6. **O6-Filter:** Doku §4 beschreibt Interface-Regel als separate Python-Prüfung; im Code ist sie ausschließlich LLM-Prompt-Regel.
7. **Entitäts-Typen:** Doku §3 listet `person | ort | organisation | tier | objekt`, Call 1-Prompt liefert nur `person | ort | organisation | objekt` (kein `tier`).

**Empfehlung:** Doku-Sprint erst nach P9 sinnvoll — der alte Code (inklusive der dokumentierten Mechanik) wird mit der vollständigen Synapsen-Umstellung gelöscht. Bis dahin: alle sieben Punkte als Markdown-Anmerkung in `novaberg-pixie-promotion.md` einleiten, damit jemand mit dem Code arbeitet, ohne der Doku zu blind zu vertrauen. Vollständiger Doku-Sweep stirbt mit dem Code in P9.

---


## Doku-Sprint: CHRONIK-BACKFILL — Lücken in Roadmap- und Backlog-Chronik (Chat 97)

**Kategorie:** [BAU] BAUART

**Status:** ⬜ Offen
**Prio:** Niedrig
**Auslöser:** Brudi-Befund beim Chat-97-Abschluss

**Beobachtung:** Zwei vorbestehende Chronik-Lücken sind beim Chat-97-Abschluss-Sweep sichtbar geworden:

1. **Roadmap-Chronik:** `novaberg-roadmap.md` springt von Chat 93 direkt auf Chat 97 — Chat 94/95/96 fehlen ganz.
2. **Backlog-Chronik:** Die Sammelliste am Datei-Ende enthält bisher nur MS-Welle Block 1 und Block 4 — Block 2/3/5 wurden nie als Chronik-Eintrag nachgezogen.

Beide Lücken sind nicht durch Chat 97 verursacht; sie wurden beim Abschluss nur sichtbar.

**Auswirkung:** Sucharbeit beim späteren Nachschlagen — wer „was war in Chat 95?" über die Roadmap rekonstruieren will, findet nichts. Folgewirkung für jede künftige Doku, die auf Chronik-Einträge verlinkt oder „Stand laut Roadmap" als Referenz nimmt.

**Lösungsraum:** Backfill aus den echten Protokollen unter `/mnt/project/Chat_94..96__Protokoll.md` und den entsprechenden Block-2/3/5-Chat-Logs. Sorgfaltsarbeit mit eigenem Audit pro Chat — was wurde tatsächlich gebaut, welche Lessons fielen ab, welche Bugs entstanden. Nicht zwischen Tür und Angel zu erledigen.

**Empfehlung:** Eigener Doku-Sprint, nicht als Nebenarbeit. Alternativ opportunistisch auffüllen — wenn jemand sowieso ein 94/95/96-Detail nachschlagen muss, beim Lesen gleich den Chronik-Eintrag schreiben.

**Verwandt:** ROADMAP-CHRONIK-DOPPELFÜHRUNG — Chronik wird doppelt geführt (Roadmap UND Backlog), was strukturelles Drift-Risiko erzeugt. Separates Thema.

---


## Bug: AUDIT-DOKU-DRIFT-MS — Drift-Befunde aus Microservice-Vorbereitungs-Audit (Chat 91)

**Kategorie:** [BAU] BAUART

**Status:** ⬜ Beobachtet, mit MS-Welle erledigt
**Prio:** Niedrig
**Auslöser:** Audit 4 (Microservice-Vorbereitung, Chat 91)

**Beobachtung:** Audit 4 hat sechs strukturelle Drift-Befunde aufgedeckt, die nicht direkt zu den fünf MS-Welle-Blöcken gehören, aber im Rahmen der Welle mit-aufgeräumt werden sollten:

1. **Zwei parallele Embedding-Pfade:** `embedding_manager` Singleton (Pixie) und freie Funktion `embedding_create()` (Live-Pipeline). Beide tun dasselbe. — Wird mit Block 1 erledigt.

2. **`pixie_llm_call` als parallele Aufruf-Schicht:** Existenz ist im Code-Bestand nicht in `novaberg-pixie.md` oder vergleichbarer Doku dokumentiert. — Mit Block 2 entfällt der Sonderpfad strukturell.

3. **`init_providers` nicht idempotent:** Doppel-Aufruf überschreibt Singletons silent. Praktisch heute irrelevant (nur ein Aufruf im Lifespan), aber strukturell ein Footgun.

4. **`_pixie_idle_provider` redundant mit `_chat_provider`:** identische Konfiguration (gleicher Client, Modell, num_ctx), separate Instanz. Möglicherweise als Lock-Vorbereitung gedacht, aber undokumentiert.

5. **Kommentar-Drift `agents/recherche/destillation.py:181`:** Kommentar nennt „MISTRAL, nicht Qwen", produktiv läuft im `gemma4`-Connector aber `gemma4-cpu`.

6. **Asymmetrie zwischen `OllamaProvider` und `AnthropicProvider` bei JSON-Reparatur:** Ollama-Pfad ruft drei Helper auf (`_clean_json_response`, `_deduplicate_repetition`, `_repair_truncated_json`), Anthropic-Pfad nur den ersten.

**Empfehlung:** Befunde 1+2 sind durch MS-Welle strukturell erledigt. Befund 3 (Idempotenz) als Mini-Schutz im Rahmen der MS-Welle-Konzeptarbeit einbauen — `init_providers` sollte beim zweiten Aufruf warnen oder no-op sein. Befunde 4–6 als Doku-Korrektur in derselben Welle aufnehmen.

**Verwandte Themen:**

- Epic: Microservice-Modell-Queue (Chat 91) — alle sechs Befunde lösen sich strukturell oder werden im Rahmen der Welle erledigt.

---


## Bug: [GELÖST Chat 96] TEST-RUNNER-FEHLT-CONTAINER — pytest im server-Container nicht installiert (Chat 94)

**Entdeckt:** Chat 94 (Verifikation des MS-Welle-Kahlschlags — `docker compose exec server pytest` schlägt fehl, pytest fehlt im Image)
**Klasse:** Test-Infrastruktur — Verifikations-Lücke
**Severity:** Mittel

**Symptom:** Im `server`-Container ist `pytest` nicht installiert. Der im Handover dokumentierte Verifikations-Befehl `docker compose exec server pytest …` läuft nicht. Die Verifikation des Kahlschlags (Chat 94) erfolgte ersatzweise per Import-Smoke-Test (`python -c "import …"` über alle berührten Module + `main`) plus pattern-basierte Greps.

**Was fehlt:** Ein lauffähiger Test-Runner im Container. Solange er fehlt, ist der Status der „4 vorbestehenden TEST-WORKER-SHUTDOWN-COROUTINE-Fails" unbestätigt — sie wurden zuletzt mit einem Runner festgestellt, der aktuell nicht reproduzierbar ist.

**Reaktivierungs-Trigger / Frist:** Vor Block 4 der MS-Welle (Pixie-Reaktivierung, erste Live-Verifikation des Background-Pfads G3–G6) klären — entweder pytest ins server-Image (requirements/Dockerfile) oder dokumentieren, wie die Suite tatsächlich gelaufen wird. Block 4 ist der Punkt, an dem die Suite am dringendsten gebraucht wird.

**Lösung (Chat 96):** Fehl-Framing aufgelöst — die Suite ist reines `unittest` (`IsolatedAsyncioTestCase`), kein pytest und kein pytest-asyncio nötig. Der dokumentierte Befehl `docker compose exec server pytest` war die falsche Tool-Wahl, nicht eine fehlende Installation. Korrekter Lauf: `docker compose exec --workdir /app server python -m unittest discover -t /app -s tests -p "test_*.py"`. Das `-t /app` ist zwingend — ohne es setzt unittest den Import-Root auf `tests/` und alle `from services.X`-Importe scheitern mit `ModuleNotFoundError`. Suite verifiziert 26/26 grün; die zuvor unbestätigten „4 Fails" waren real 5 (TEST-WORKER-SHUTDOWN-COROUTINE, inkl. EmbedWorker) und sind in Chat 96 gefixt (e891eb9). Kein Image-Rebuild, kein requirements-dev.txt — die ursprünglich erwogene pytest-Einführung war überflüssig.

---


## Lesepfad-Folgepunkte (Chat 99)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Bauart**. Ueberschrift und Text stehen in jeder empfangenden Datei.

Acht Folgepunkte aus dem P5-Lesepfad-Umbau plus die Live-Abnahme als nächster Schritt. Rein additiv, keine Voraussetzung für P6/P7 — Code-Hygiene, Doku-Drift und eine empirische Test-Aufgabe. Reihenfolge: zuerst P5-LIVE-ABNAHME (beweist, dass das Spreading live greift), der Rest zwischen den Sprints.

| # | Thema | Status |
|---|-------|--------|
| LIB-VECTORS-MIGRATION | `embedding_zu_pgvector_str` liegt provisorisch in `memory/utils.py`. Norm-Ziel laut Handbuch §5 ist `lib/vectors/` (existiert noch nicht). Bei Anlage der `lib/`-Struktur dorthin migrieren (perspektivisch auch `cosine_similarity`/`sin_sqrt_norm` aus `ei/utils.py`). | [BAU] ⬜ Prio niedrig |
| B3-API-KEY-SEMANTIK | Der REST-Endpunkt `/gedaechtnis/lzg` liefert weiterhin den Antwort-Key `gewicht`, der jetzt aber `gewicht_decay` trägt (Quelle auf `lzg_knoten` umgestellt). Key-Name bewusst gewahrt (Contract-Stabilität); semantisch leicht irreführend. Umbenennung bräuchte Client-Abstimmung. | [BAU] ⬜ Prio niedrig |

---


## 8. Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Kategorien; hier stehen die von **Bauart**. Ueberschrift und Text stehen in jeder empfangenden Datei.

Vollständige Bug-Dokumentation → `novaberg-bugs.md`

Kurzübersicht aktiver Bugs:

| Bug | Prio | Kurzbeschreibung |
|-----|------|-----------------|
| HALL2 | ⚠️ | KZG-Klebrigkeit — wiederholte Mitteilung bereits kommunizierter Inhalte |
| THER1 | ⚠️ | RLHF-Therapeut-Muster |
| PATH1-LATENZ | ⬜ | [BAU] Pfad-1 kann bei GPU-Druck auf 55+ Sekunden gehen (Einmal-Event beobachtet) |
| TEST-RUNNER-FEHLT-CONTAINER | ✅ | [BAU] Fehl-Framing (Chat 96): Die Suite ist reines `unittest` (`IsolatedAsyncioTestCase`), kein pytest nötig — `pytest` schlug nicht mangels Installation fehl, sondern war das falsche Werkzeug. Richtiger Befehl: `docker compose exec --workdir /app server python -m unittest discover -t /app -s tests -p "test_*.py"` (`-t /app` hält den Import-Root, sonst `ModuleNotFoundError`). Suite läuft 26/26 grün. Aufgeworfen Chat 94, geklärt Chat 96. |

Details, Ursachen und Lösungsansätze → `novaberg-bugs.md`

---

*Aktualisiert Chat 61: Perzeption-Symmetrie ✅, EI-Calc Rollen-Split ✅, Akkumulations-Refactor mit Historien-Gewicht + sin^0.5-Glättung ✅, perzeption_assistant Client-Label ✅. Konzeptionell: Emotionale Gravitation (Kapitel 5.7 in thinking-drive), Paper-Portfolio (novaberg-papers.md mit 29 Titeln, 9 angereichert). Neue Epics: Emotionale Gravitation implementieren, Client urllib3-Retry-Fix, Session-Limit für Responder-Prompt. Neue Bugs: urllib3-RETRY, PATH1-LATENZ.*

*Aktualisiert Chat 63: Zwei neue Epics — KZG-Liberalisierung + LZG-Destillation (Schwelle senken, Deduplizierung aufweichen, Destillation bei Promotion), Embedding-Gravitationsgraph (Turn-Dashboard mit Plutchik-Mikrosternen, geladenem Gedächtnis als Orientierungspunkte).*

*Aktualisiert Chat 68: WS-SINGLE behoben (ClientConnection-Dataclass, broadcast()/broadcast_threadsafe() mit character_id/exclude_client). User-Message-Broadcast: Desktop ↔ Telegram bidirektional sichtbar (server-seitige Filterung). 12 Dateien.*

*Aktualisiert Chat 69: Goals-Panel ✅ + Gravitationsgraph-Panel ✅ (2 neue Panels). Embedding-Persistenz in Session-Turns. Themen-Pipeline (`prompt_thema` → Dispatcher → Session) geschlossen. `thema`-Spalte in `ziele`-Tabelle. GRAVITATIONS_SCHWELLE kalibriert (0.3 → 0.75). Dashboard-Epic: 8/14 Panels.*

*Aktualisiert Chat 72: GV3 (Dreischicht-Prompt-Integration) ✅ — implementiert in Chat 72. GV-Panel Redis-Persistierung ✅ (war bei Chat-72-Start bereits erledigt). Drei neue Folgearbeiten: Reducer-Node (Hoch, gegen Echo-Bug bei langen Sessions), GV-Panel Dreischicht-Felder visualisieren (Hoch, Sichtbarkeit der neuen Architektur), Modus-Kalibrierung spielerisch vs. emotional (Niedrig, Perzeption-Prompt).*

*Aktualisiert Chat 71: GV3 + GV4 in Implementierung (🔧). GV4b als neues Epic: Agenten als Wissensquellen mit BaseAgent-Erweiterung (neugier_quelle, neugier_config, neugier_suchen()). Embedding-Nachrüstung für Timeline + Notizen. FaktenAgent als Quick Win (Embedding existiert). 6-Systeme-Relevanzformel validiert (58-Testfälle-Matrix, sin^0.5 Neugier-Normalisierung, Register-Kompatibilität, Session-Decay).*

- Chat 77: Convention-Magneten angelegt (`novaberg-convention-magneten.md`) — Drei-Achsen-Modell für Bündelung von Erinnerungen
- Chat 77: Convention-Planner-Needs angelegt (`novaberg-convention-planner-needs.md`) — Multi-Agent-Schreibpfad mit Vorbedingungs-Auflösung

*Aktualisiert Chat 74: Reducer-Erst-Iteration ✅ (String-Parser, funktional aber brüchig). Reducer-Umbau als neues Hoch-Prio-Epic mit Konzept-Dokument `novaberg-reducer-umbau_k.md` (7-Phasen-Plan STRUCT-1 bis STRUCT-7, Big Bang). Drei neue Konzept-Backlog-Punkte: Assoziatives Retrieval, Akten-basiertes Retrieval, Anker-Emotion. Hash-Zeitstempel für alle 5 Profile ✅ (3 neue DB-Spalten + Migration + Agent + API + Client).*

*Aktualisiert Chat 88: Neue Subsektion „Refactoring & Code-Hygiene (Chat 88)" in §7 angelegt. Zwölf REFAC-Einträge aus zwei Audits — sechs aus dem allgemeinen Code-Audit zum Synapsen-Umbau (REFAC-ENRICHER-EVA, REFAC-LOGGER-HIERARCHIE, REFAC-SHUTDOWN-DISZIPLIN, REFAC-SCHEMA-MIGRIEREN-FAILMODE, REFAC-PIPELINE-LOG-VOLLVERKABELUNG, REFAC-UMLAUTE), drei aus der P0-Migrations-Konsolidierung während der Ausarbeitung (REFAC-DB-INDEX-DUPLIKAT, REFAC-SEEDS-AUSLAGERN, REFAC-AGENT-INIT-COMPOSE-MOUNT), drei aus dem P0-Abschluss-Bericht (TIMELINE-IN-KERN, FAKTEN-IN-KERN, NOTIZEN-INDIZES-NACHTRAG). Bewusste Trennung von den Synapsen-Sprints P1–P10. Außerdem in Chat 88: Synapsen-Konzept §13 (Implementierungs-Phasen, Stufe 1 mit P1–P10) ausgearbeitet, P0-Migrations-Konsolidierung abgeschlossen — `db/init.sql` ist Single Source of Truth, `schema_migrieren()` reduziert auf reines Laden und Ausführen, `docker-compose.yml` um db-Mount erweitert, sechs `__backup`-Tabellen aus Live-DB entfernt.*

*Aktualisiert Chat 88 (P1.1-Korrektur): Zwei neue REFAC-Einträge — SHUTDOWN-EVENT-ASYNC (aufgedeckt durch P1-Implementierung: `shutdown_event` ist `threading.Event` statt `asyncio.Event`, drei Polling-Pattern in den Hintergrund-Tasks) und REFAC-EVENT-PAYLOAD-SEEDING (Event-Consumer kopiert acht Perzeptions-Felder manuell, generisches Seeding wäre wartungsärmer). REFAC-SCHEMA-MIGRIEREN-FAILMODE umformuliert (Verweis auf P1 entfernt, weil seit P0 die gesamte `db/init.sql` als Einheit geladen wird). P1.1-Code-Korrekturen: `turn_id` als UUID4-Hex im /chat-Handler erzeugt und über HumanGraph-State + Event-Payload an CharacterGraph durchgereicht, `quelle`-Marker im Enricher von `user_id`-Heuristik auf `state["ei_calc_rolle"]` umgestellt. Damit haben beide Pipeline-Log-Spans eines Konversations-Turns dieselbe `turn_id` und unterschiedliche `quelle`-Werte (`user` / `character`).*

*Aktualisiert Chat 88 (P2): Tabellen `lzg_knoten` und `lzg_kanten` in `db/init.sql` angelegt, leer, parallel zum bestehenden `langzeitgedaechtnis`. 18 neue Konstanten aus Konzept §6 in `config.py` (Knoten-Dynamik, Kanten-Cache, Sinus-Geometrie, Schicht-Faktoren, Tiefe-Faktor). FK-Übergangsblock für `lzg_knoten.timeline_id → timeline.id` in `agents/timeline/init.sql`. Neuer Backlog-Eintrag REFAC-HANDBUCH-§9-MIGRATIONS — Handbuch §9 widerspricht der gelebten P0-Konvention (init.sql als SSoT, ALTER-Statements direkt darin), muss in eigenem Doku-Sprint nachgezogen werden. Doku-Korrektur in §13.5 — Entitäts-IDs sind Integers, nicht UUIDs.*

*Aktualisiert Chat 88 (P3): KZG-Schreibpfad ergänzt um Magnet-Felder `entitaet_ids` und `timeline_id`. Salience extrahiert pro Turn zwei neue Roh-Dimensionen (`entitaeten_roh`, `zeitausdruck_roh`). Neuer Node `magnete_aufloesen` im KzgAgent-Subgraph zwischen `schwelle_pruefen` und `verdichten` resolviert via EntityResolutionService und TimelineRepository — bei nicht-Treffer wird via `create_new_entity` bzw. `TimelineRepository.insert` mit `event_type='erinnerungs_anker'` angelegt. Clipboard-Pattern: TimelineAgent schreibt `state["timeline_id"]` ins ConversationState; `magnete_aufloesen` übernimmt diesen Wert statt einen doppelten Erinnerungs-Anker anzulegen. Beide KZG-Schreibfunktionen (`_neu_anlegen`, `kzg_store`) um optionale Parameter erweitert, Default-Werte sichern Backward-Compat für Recherche-Agent, Shadow-Tasks und KzgManager. Pipeline-Log `log_db_zugriff` in beiden Schreibfunktionen. Neuer Backlog-Eintrag REFAC-KZG-CODE-DUPLIKAT — fast identische Hash-Mapping-Logik in beiden Schreibfunktionen sollte konsolidiert werden. Konzept-Doku §13.5 ausführlich nachgezogen (Architektur statt der vorigen falschen Vorbedingung „EntityResolver liefert entitaet_ids"). Convention-Magneten §5 dokumentiert jetzt den konkreten `event_type`-String `erinnerungs_anker` für die Klasse Bezug.*

*V7-Befund (Clipboard-Test): Der Test-Turn "Merk dir bitte den 17. Oktober als Annas Geburtstag" erzeugte einen `erinnerungs_anker` statt eines `geburtstag`-Eintrags, weil der Planner den expliziten Timeline-Intent nicht erkannt hat. Das Clipboard-Pattern ist strukturell vorbereitet, aber im Live-Betrieb selten getriggert. Eingetragen als PLANNER-TIMELINE-INTENT-MISS — strukturelle Klärung nach P9.*

*Aktualisiert in Chat 90: PFAD2-PERZEPTION-FIX abgeschlossen (Phase 2/3, Chat 89), HumanGraph-Slimming Phase 4 + TURN-ID-FIX (Chat 90), drei neue Backlog-Einträge aus Welle-B-Audit (BUG-EI-CALC-ROLLE-DEFAULT-ASYMMETRIE, PERF-DOPPEL-SESSION-LOAD, plus fünf konkrete Stellen am Code-Audit-Sprint-Epic), Stand-Datum auf 17. Mai 2026.*

- ✅ **MS-Welle Block 1 — Embedding-Konsolidierung** (Chat 92): EmbedWorker in services/model_services/ als In-Process-Microservice mit FIFO-Queue. 24+ Aufruf-Stellen migriert (G1-G8), Cleanup-Sprint, drei Main-Loop-Blocker und zwei Silent-Skip-Bugs nebenbei behoben, CPU-Embedding-Sonderpfad und Pixie-Idle-Provider rückgebaut. Drei Lessons archiviert.
- ✅ **MS-Welle Block 4 + Inbetriebnahme + Pixie-Reaktivierung — MS-Welle abgeschlossen** (Chat 97): Connector `qwen36` live (GPU=`gemma4-gpu`, CPU=`qwen36-cpu` für Sprache und Analyse), aktiviert über `OLLAMA_CONNECTOR: qwen36` in der echten `docker-compose.yml` (Code-Default in `config.py` bleibt `gemma4` als Fallback-Anker). GPU-Connector-Fehlgriff (`gpu_model` zunächst fälschlich auf `qwen3.6:35b-a3b`) noch vor Aktivierung gegen die Block-4-Spec korrigiert. Alte CPU-Modelle nach verifiziertem Background-Pfad gelöscht (Gemma4-CPU, Qwen3-32B-CPU, drei Mistral-Varianten, ~105 GB). `PIXIE_AKTIV` env-konfigurierbar gemacht (CONFIG-PIXIE-AKTIV-HARDCODED gelöst) und Pixie reaktiviert + verifiziert. BackgroundWorker-Submit-Timeout-Default 300 s (Variante B: Worker-Instanz-Default per Konstruktor, pro Call überschreibbar; Chat/Embed behalten 60 s). Neuer Backlog-Eintrag WORKER-TIMEOUT-MUSTER-DIVERGENZ als Konsistenz-Beobachtung. MS-Welle damit vollständig abgeschlossen (Block 1–5), P4 darf loslegen.

---


## Refactor: BEZEICHNER-WAR-AKTIV — was_active statt war_aktiv (Chat 102)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Gegen HEAD `599c19b` geprueft: `war_aktiv` steht unveraendert in `memory/repositories/shadow_auftrag_repository.py`. Die Umbenennung ist nicht erfolgt.

`reactivate_node` in `memory/lzg_knoten.py` nutzt die lokale Variable
`war_aktiv` (deutsch). Die Sprach-Regel verlangt englische Bezeichner —
`was_active`. Kein Einzelfix: gebuendelter Bezeichner-Angleich beim naechsten
Anfassen der Datei (auch `zeile`, `neuer_roh` etc. im Umfeld sind gemischt).

---


## Fix: CONFIG-DECAY-RATE-KOMMENTAR-DRIFT — falscher Kommentar bei LZG_KNOTEN_DECAY_RATE (Chat 102)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die im Befund genannte Stelle ist in dieser Form nicht mehr auffindbar; ohne den alten Wortlaut ist nicht zu entscheiden, ob sie entfallen oder umgeschrieben wurde. **Unbelegt, nicht erledigt.**

`config.py` (~Z.1092) kommentiert `LZG_KNOTEN_DECAY_RATE` mit "nicht persistiert,
live berechnet". Falsch: `gewicht_decay` ist eine persistierte Spalte
(`db/init.sql:141`), die der synapsen_decay-Agent taeglich materialisiert — der
Lesepfad rechnet keinen Decay live (grep: kein `exp(` in `lzg_knoten.py`).
Alt-Text aus dem Ebbinghaus-Modell (`pixie-decay.md`). Reiner Kommentar-Fix,
fremder Ort → eigener Commit.

---


## Frage: PATTERN-DOMAIN-LANGUAGE-RECONCILE — deutsche Domaenensprache vs. Englisch-Regel (Chat 102)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Eine Festlegung, keine Messung — und sie ist nicht getroffen worden.

`novaberg-pattern-domain-language.md` kodifiziert (soweit in Chat 102 referenziert)
deutsche Domaenen-Verben als Muster. Das widerspricht der Regel "Bezeichner
englisch". **Zu klaeren:** Inhalt der Datei verifizieren, dann Update oder
Rueckzug. Reichweite: codebase-weit (bestehende deutsche Funktionsnamen wie
`knoten_verstaerken`), also eigener Sprint, kein Beifang.

---


## Doku: CHARHASH-DOKU-DRIFT — Hash-Doku beschreibt LZG-Quelle noch flach (Chat 103)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die Doku beschreibt die Quelle weiterhin flach.

`novaberg-pixie-character-hash.md` beschreibt jenseits der P7-Passagen die LZG-Quelle noch als flaches `langzeitgedaechtnis` (Z. 155 Adaptiv-Hash-Tabelle: nennt `langzeitgedaechtnis`, liest real KZG). Alt-Drift aus dem P5/P6-Umbau, nicht von P7 verursacht. Eigener Doku-Fix, keine Vermischung mit dem P7-Commit. ⬜ Prio niedrig


## Nacharbeit: PIPELINE-LOG-BACKFILL-PAAR — Alt-Forensik ohne Paar-Schlüssel (Chat 104)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Geplante Arbeit, nicht begonnen.

Bestehende `pipeline_log`-Zeilen (vor Chat 104) haben `user_id`/`character_id = NULL`. Optionaler Backfill für die `pipeline_search`-Selbstreflexion über Alt-Forensik. KRITISCH richtungssensitiv: produktiv liefen beide Beobachter-Richtungen (meister→nova UND nova→meister, bestätigt via `charakter_hash`). Kein pauschales `SET` eines Paares — sonst wird eine Perspektive plattgemacht. Der Filter (welche `art`/`node` paar-gebunden vs. herrenlos sind) steht seit dem H1.5-Inventar fest; Wartungszeilen (`synapsen_decay`-Cleanup, Decay-Lauf) bleiben bewusst NULL. Kein Blocker — `turn_roh` liefert die charakter-relevanten Daten vorwärts, Altzeilen sind nur Forensik. ⬜ Prio niedrig


## Doku: PIPELINE-LOG-ART-DOKU-DRIFT — Forensik-Queries der Synapsen-Doku laufen gegen reale `art`-Werte ins Leere (Chat 106)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die Doku-Drift ist nicht nachgezogen.

Kein Code-Defekt — der Code ist RICHTIG (`db_write`/`db_read`/`turn_roh`), das Konzeptdokument ist falsch (`db_zugriff`). Aus novaberg-bugs.md hierher verschoben (Trennungsregel Chat 106). ⚠️ **Sperrvermerk: vor CHARAKTER-RESONANZ Teil 2 zu klären** — `pipeline_log` ist die Quelle für den Destillator; wer ihn nach dem Konzeptdokument baut, baut gegen ein Schema, das es nicht gibt.

**Entdeckt:** Chat 106, systematischer Doku-Code-Abgleich (Fund über `novaberg-memory-synapsen_k.md` §10.1/§10.2/§13.5)

**Klasse:** Doku-Code-Drift an der Forensik-Schnittstelle, Severity **Mittel** — blockiert nichts im Betrieb, aber verminte Forensik

**Symptom:** Die Synapsen-Doku definiert für schreibende DB-Zugriffe den `art`-Wert `db_zugriff` und behauptet „Lesen wird nicht geloggt". Der Code schreibt tatsächlich `db_write`, `db_read` (Lesen WIRD geloggt) und `turn_roh`. Die in §13.5 dokumentierten Forensik-Queries (`WHERE art = 'db_zugriff'`) liefern gegen reale Daten 0 Zeilen. Dazu zwei Nachbar-Drifts im selben Kapitel: Das §10.1-Schema führt die real existierenden Spalten `user_id`/`character_id` nicht, und die §10.5-Retention (365 Tage) verschweigt die dauerhafte Ausnahme für `turn_roh`.

**Beleg (Datei:Funktion):**

- `memory/pipeline_log.py` → `log_db_write` (schreibt `art="db_write"`, Z. 505/519), `log_db_read` (`art="db_read"`, Z. 522/536), `log_turn_roh` (`art="turn_roh"`, Z. 627/647)
- Produktive Schreiber: `memory/kzg.py` → `kzg_store` (via `log_db_write`, Z. 340); `agents/kzg/speicher.py` → `_neu_anlegen` (Z. 304)
- Spalten: `memory/pipeline_log.py` → `_insert` mit `user_id`/`character_id` (Z. 303–306); Schema `db/init.sql:381ff`
- Retention-Ausnahme: `memory/pipeline_log.py` → `delete_expired_entries` (`AND art <> 'turn_roh'`, Z. 362–365)

**Auswirkung:** Wer nach der Doku debuggt oder Forensik betreibt, bekommt leere Ergebnismengen und zieht falsche Schlüsse („keine DB-Writes geloggt"); die undokumentierte `turn_roh`-Ausnahme lässt Speicherwachstum an einer Stelle zu, an der die Doku Löschung verspricht. Fix bewusst offen — Klärung, ob Doku oder `art`-Taxonomie führt, kommt nach eigenem Audit.


## Doku: LESSON-INDEX-LUECKE — zwölf ältere lesson_l-Dateien fehlen im Architektur-Index (Chat 106)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die Doku-Drift ist nicht nachgezogen.

Der Lesson-Index in `novaberg-architecture.md` listet die Legacy-`{modul}_l.md`-Dateien und die zuletzt verlinkten Lessons — zwölf ältere `novaberg-lesson_l_*`-Dateien fehlen komplett (Seitenbefund aus Chat 105, Commit `e08555a`; die zwei Chat-105- und vier Chat-106-Lessons wurden beim Anlegen verlinkt, der Altbestand nicht nachgezogen). Doku-Lücke, kein Code-Bezug: Wer Lessons über den Index sucht, findet den Altbestand nicht. Nachzug ist ein mechanischer Fünf-Minuten-Fix, gehört aber in einen bewussten Doku-Commit. ⬜ Prio niedrig

**Nachtrag Chat 108:** Zwei neue Lessons sind eingetragen (`konzept-spricht-code`, `ableitung-als-messung`); der Altbestand bleibt bewusst offen. Zwei Beobachtungen für den geplanten Doku-Commit:

- ~~Die Überschrift `### Lessons (NN)` in `novaberg-architecture.md` trägt einen handgepflegten Zähler, der schon vor Chat 108 falsch war. Beim Aufräumen **entfernen, nicht aktualisieren** — eine Zahl neben einer wachsenden Tabelle driftet dauerhaft, und die Tabelle steht direkt darunter.~~ → **Erledigt Chat 111.** Der Zähler stand bei 22, die Tabelle hatte 28 Zeilen, auf der Platte lagen 44 `_l`-Dateien — dreimal auseinander. Ersatzlos entfernt. Der Altbestand bleibt offen.
- Die Angabe „zwölf ältere Dateien fehlen" stammt aus Chat 106 und trägt kein Messdatum. Beim Aufräumen **neu zählen statt übernehmen**.


## Doku: DOKU-DUPLIKATE-CHAT80 — 8 Bezeichner stehen in bugs.md UND backlog.md (Chat 106)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. **Und heute mehrfach neu belegt.** Der Durchgang durch dieses Register fand vier Kennungen, die zweimal als Ueberschrift stehen, und mehrere Befunde unter zwei bis drei verschiedenen Kennungen. Der Eintrag ist damit nicht kleiner, sondern groesser geworden.

**Entdeckt:** Chat 106 (Gegenprobe nach der Bug/Backlog-Trennung). ⬜ Prio niedrig

**Befund:** Kurz-Eintrag in bugs.md + Lang-Eintrag in backlog.md, mit Verweis („Ausführliche Beschreibung: novaberg-backlog.md → Bug X"). Damals absichtlich, seit der Chat-106-Regel („ein Eintrag steht in GENAU EINEM Dokument") ein Verstoß.

**Betroffen:** FAKTEN-PAIR-IGNORED, NOTIZEN-CONTAINER-WECHSEL, NOTIZEN-KONTEXT-REKONSTRUKTION, NOTIZEN-PAIR-MISSING, NOTIZEN-SKILL-MANIFEST, NOTIZEN-UPDATE-TARGET-LEER, TIMELINE-PAIR-MISSING, ZIELE-PAIR-MISSING

**Auswirkung:** Doppelregistry-Muster in der Doku — zwei Orte, die zusammen gepflegt werden müssen, driften still auseinander. Dasselbe Muster wie PIXIE-ROUTING-DOPPELREGISTRY.

**Vorschlag zur Auflösung (Entscheidung offen):**

- Die vier *-PAIR-* sind EINE Sache, viermal manifestiert → ein Backlog-Eintrag „Paar-Schema nicht durchgezogen" mit vier Fundstellen.
- Die drei NOTIZEN-Verhaltensfälle → bugs.md. ⚠ NOTIZEN-UPDATE-TARGET-LEER lebt noch: NOTIZ-RESUME-TARGET-VERLUST (Chat 106) hat denselben Kern (`parameter["target"]` leer).
- NOTIZEN-SKILL-MANIFEST → Inhalt prüfen, klingt nach Konzept (Epic 10).


## Fix: EMBED-DIMENSIONSCHECK-FEHLT — kein harter Dimensions-Check im Live-Pfad (Chat 107)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Gegen HEAD `599c19b` geprueft: Ein harter Dimensionsvergleich steht nur im Werkzeug fuer den Neuaufbau, **nicht im Live-Pfad**.

Kein einziger harter Check im Repo (Audit Chat 107): kein `== 768`, kein `assert`. Der Enricher-Kommentar verspricht einen „Plausibilitäts-Anker", tatsächlich wird nur `len()` geloggt. In Postgres fällt ein falsch dimensionierter Vektor beim INSERT auf — in Redis (FLAT-Index, rohe Bytes) unter Umständen **gar nicht**. Verstoß gegen EVA/fail-loud. Im `reembed_all.py` bereits als Pflicht spezifiziert — muss auch in den Live-Pfad (natürlicher Ort: `EmbedWorker._call_model`, ein Check für alle Konsumenten). ⬜ Prio mittel


## Fix: LZG-MIGRATION-REVIEW-NICHT-IN-INIT — Live-Tabelle ohne Schema-Definition (Chat 107)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Am Schema bestaetigt: Die Tabelle liegt in der Datenbank und steht in keiner `init.sql`. Ein Aufbau von null erzeugt sie nicht.

`lzg_migration_review` existiert live (17 Spalten, genutzt von `tools/migrate_lzg_synapsen.py`), steht aber in keiner init.sql. Frisches Setup ⇒ Migrationstool bricht. Bricht die Handbuch-Zusage „frischer Container + init.sql = lauffähiges System". ⬜ Prio mittel


## Fix: IDX-TIMELINE-TYPE-NICHT-IN-INIT — Live-Index ohne Definition im Repo (Chat 107)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Am Schema bestaetigt: Der Index liegt in der Datenbank und steht in keiner `init.sql`. Deckungsgleich mit `REFAC-DB-INDEX-DUPLIKAT`, das denselben Index als Dublette fuehrt — **zwei Eintraege, ein Index, entgegengesetzte Abhilfen.**

`idx_timeline_type` auf `timeline(user_id, event_type)` existiert live, steht in keiner init.sql — manuell angelegt. Bei Setup-from-scratch fehlt er. Performance, nicht Korrektheit. ⬜ Prio niedrig


## Doku: HANDBUCH-§9-VERALTET — Migrations-Absatz widerspricht der geltenden Projektregel (Chat 107)

§9 fordert „niemals ALTER TABLE in init.sql, Alembic empfohlen". Geltende Projektregel (bestätigt Chat 107) ist das Gegenteil: init.sql IST die Single Source of Truth, Änderungen dort, idempotent, Anwendung aufs Live-System von Hand. Fragmentierte Migrationsdateien wurden bewusst abgeschafft — sie führten zu abweichenden Datenbankzuständen. **§9 gehört an die Realität angepasst, nicht die Realität an §9.** ✅ Erledigt (Docs-Commit 12.07.2026) — §9 neu gefasst (Handbuch v0.4), damit auch REFAC-HANDBUCH-§9-MIGRATIONS geschlossen.


## Doku: REDUCER-DOKU-DRIFT — drei Drifts aus dem Reducer-Audit (Chat 107)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die Doku-Drift ist nicht nachgezogen.

(a) Docstring von `reducer.py` verweist auf `novaberg-reducer-umbau_k.md` — existiert nicht; real ist `novaberg-node-reducer.md`. (b) Docstring: „zwischen Enricher und EI-Calc" — real läuft EI-Calc VOR dem Enricher, der Reducer sitzt vor dem Router. (c) Node-Doku §9: „kein Produzent erzeugt summary-Einträge" — der Produzent existiert im Enricher und feuert, sobald Redis eine Session-Summary hält. ✅ Erledigt (Docs-Commit 12.07.2026) — Docstring korrigiert (Verweis + Graph-Position), Node-Doku §9 richtiggestellt.


## Doku: DOKU-NOTIZEN-INIT-SQL — Verweis auf nicht existierende Datei (Chat 107)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die Doku-Drift ist nicht nachgezogen.

`novaberg-agent-notes.md` behauptet, `notizen` werde via `agents/notizen/init.sql` angelegt. Die Datei existiert nicht — `notizen` steht in `db/init.sql`. ✅ Erledigt (Docs-Commit 12.07.2026) — Verweis in §9 der Agent-Doku korrigiert.


## Befund: PERMISSION-OHNE-BODEN — „Brudi ist read-only" ist Konvention, nicht erzwungen (Chat 109)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Unveraendert.

**Gemessen Chat 109 (Umgebungs-Audit, 25.07.2026, 11:47 UTC):** 203 `allow`-Einträge über drei Settings-Dateien (`~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`), **null `deny`, null `ask`, kein `defaultMode`**, und an keinem der drei üblichen Orte eine `managed-settings.json`. Die Permission-Konfiguration ist reines Allowlisting ohne Gegengewicht.

Claude Codes eigene Bash-Sandbox ist **nicht aktiv**: Der Bash-Prozess sitzt in exakt denselben Namespaces wie der `claude`-Prozess und wie der Flatpak-Init (identische `user`/`mnt`/`net`/`pid`/`ipc`-Inodes, `Seccomp_filters: 1`), und `bwrap` fehlt im Flatpak-Runtime — das Werkzeug, mit dem diese Sandbox auf Linux gebaut würde, ist nicht vorhanden. Die einzige messbare Isolation kommt vom VS-Code-Flatpak (`com.visualstudio.code`), und der läuft mit `filesystems=host` plus `org.freedesktop.Flatpak=talk` — also mit Host-Dateisystem und der Berechtigung für `flatpak-spawn --host`.

**Auswirkung:** Dass ein Audit-Auftrag „READ-ONLY" nur liest, ist eine Zusage im Prompt, keine erzwungene Eigenschaft der Umgebung. Es gibt keine technische Schranke, die einen Schreibzugriff oder einen Host-Ausbruch verhindert; es gibt nur die Absprache. Wer das für eine Sandbox hält, verlässt sich auf etwas, das nicht existiert. ⬜ Prio mittel

**Zusammenhang:** ALLOWLIST-DRIFT (die Liste wächst nur, niemand räumt sie).

---


## Aufräumen: ALLOWLIST-DRIFT — die Claude-Code-Allowlist wächst nur (Chat 109)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die Liste kennt weiterhin nur Zuwachs.

Die Permission-Allowlist kennt nur Zuwachs: Einzelfall-Einträge aus längst abgeschlossenen Sprints stehen weiter drin, darunter ein `docker cp` mit dem konkreten Pfad einer Magneten-Migration (`/tmp/m2_magneten_migration.sql`) und mehrere `python -c "import ast; ast.parse(open('…'))"`-Zeilen auf Dateien, die seit dem jeweiligen Sprint nicht mehr angefasst wurden.

Ein Einzelfall-Eintrag, der seinen Anlass überlebt, ist eine dauerhaft offene Tür ohne Grund. Braucht einen Aufräum-Durchgang **mit Messdatum** — also: Bestand zählen, Einträge einer laufenden Aufgabe zuordnen, Rest streichen, Zahl vor/nach protokollieren. Beobachtet Chat 109 (25.07.2026). ⬜ Prio niedrig

**Zusammenhang:** PERMISSION-OHNE-BODEN (kein `deny`, kein `defaultMode` — die Liste ist die einzige Kontrollfläche).

---


## Doku: ROADMAP-GLIEDERUNGSBRUCH — ab Chat 98 wechselt die Chronik die Überschriftsebene (Chat 109)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. **Teilweise entschaerft, nicht behoben.** Die Chronik ist am 25.08.2026 nach Zeitraeumen geteilt und das falsch beschriftete Kapitel aufgeloest worden; die laufende Datei fuehrt 120 Kapitel auf `##`. **Der Bruch der aelteren Teile besteht fort** — die Chats 98 bis 108 stehen dort weiterhin als `###` unter einem fremden Kapitel. Neu ist, dass ein erzeugtes Findemittel ueber alle Ebenen und Teile spannt: Wer sucht, findet den Eintrag auch dann, wenn die Ueberschriftenebene wechselt.

`novaberg-roadmap.md` gliedert bis **Chat 97** nach Chat: jeder Chat ein eigener `## Chat NNN`-Abschnitt. **Ab Chat 98** wechselt sie ohne Hinweis auf `###`-Abschnitte, die nach **Sprint** benannt sind — „Synapsen P6 — Decay-Agent + Halbreaktivierung (Chat 102, …)", „Audit-Kaskade … (Chat 105, …)". Die Chat-Nummer steht nur noch in Klammern im Titel.

**Folge:** Wer nach `## Chat 104` sucht, findet nichts und hält den Eintrag für fehlend. Die Chronik ist vollständig, ihre Oberfläche sagt etwas anderes.

**Der Beleg für die Kosten — es ist bereits passiert.** In Chat 109 hat genau dieser Bruch einen Fehlschluss ausgelöst: Ein `grep` auf `^## ` fand als letzten Chat-Abschnitt die 97 und ließ auf eine **Lücke von elf Chats (98–108)** schließen. Tatsächlich fehlen **vier: 94, 95, 96 und 101** — die elf vermeintlich fehlenden waren alle da, nur eine Ebene tiefer. Der Fehlschluss wäre beinahe als Lückenmarkierung ins Dokument gewandert und hätte eine spätere Sitzung dazu gebracht, bereits Dokumentiertes nachzutragen. Der korrigierte Stand steht jetzt als Lückenmarkierung in der Roadmap selbst; die Kopfzeile trägt seit Chat 109 einen Warnhinweis auf die uneinheitliche Gliederung.

**Vereinheitlichung ist ein eigener Durchgang** — elf Abschnitte umhängen, Sprint-Titel als Untertitel erhalten, Querverweise prüfen. Nicht nebenbei. ⬜ Prio niedrig

**Zusammenhang:** DOKU-DUPLIKATE-CHAT80 · LESSON-INDEX-LUECKE (beides Gliederungs-/Auffindbarkeitsprobleme in der Doku, nicht im Code).

---


## Landmine: DB-SELECT-SCHREIBT-OHNE-COMMIT — `select()` führt ein Schreib-Statement aus und verwirft es (Chat 111)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Unveraendert.

Kein Defekt — `db_manager.select()` tut, was ihr Docstring sagt („SELECT-Abfrage", `tools/db_manager.py:26-34`). Die Falle liegt darin, was sie **nicht** tut: Sie lehnt ein übergebenes `INSERT`/`UPDATE`/`DELETE` nicht ab, sondern **führt es aus**, liest die `RETURNING`-Zeilen aus der offenen Transaktion und legt die Verbindung ohne `commit` in den Pool zurück. Dort wird alles verworfen.

Der Aufrufer sieht echte Zeilen und meldet Erfolg. Genau das ist einmal geschehen: zwanzig gemeldete Neuanlagen, null in der Tabelle. Behoben durch `execute_returning`, das committet und die Zeile zurückgibt — es existierte längst; gegriffen wurde zur falschen Funktion, weil sie zufällig auch etwas zurückgibt.

**Gemessen am Bestand:** **22 von 22** Aufrufstellen übergeben ein `SELECT`. Kein zweiter Fall, ein Durchgang lohnt nicht — die Falle ist latent, nicht verbreitet.

**Härtung:** `select()` soll ein Nicht-`SELECT` **ablehnen** statt es auszuführen — fail loud, statt lautlos zu verwerfen. Solange das nicht gebaut ist, gilt der Sperrvermerk: Wer schreibend `RETURNING` braucht, nimmt `execute_returning`. ⬜ Prio niedrig

**Zusammenhang:** `novaberg-lesson_l_gelesen-ist-nicht-wirksam.md` (Fall 1 der Klasse).

---


## Audit: PUB-ROLLENNAMEN-IM-BESTAND — die Doku nennt die internen Rollen (Chat 120)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. **Die Grundlage ist zur Haelfte widerlegt.** Am 19.08.2026 ist entschieden worden, dass der Name der bauenden Instanz keine schuetzenswerte Angabe ueber einen Menschen ist; damit faellt ein Teil der gezaehlten Fundstellen aus dem Befund. Was steht, ist die Beschreibung der Zusammenarbeit mit einem Menschen darin — und die ist nicht neu gezaehlt worden. **Eine Zahl, deren Kriterium sich geaendert hat, ist keine Zahl mehr.**

Rollennamen der Zusammenarbeit gehören nicht ins öffentliche Repositorium. Sie stehen trotzdem darin, und zwar nicht vereinzelt.

**Gemessen am 30.07.2026.** Die Abfrage gehört zur Zahl, sonst ist sie beim nächsten Nachzählen nicht reproduzierbar: alle `*.md` im Wurzelverzeichnis und unter `docs/`, **ohne** `docs/archive/` (siehe unten) und **ohne** `novaberg-backlog.md`, weil dieser Eintrag die Begriffe selbst nennt und sich sonst mitzählt.

| Begriff | Dateien | Fundstellen |
|---|---|---|
| „Brudi" | 19 | 70 |
| „Meister" | 35 | 107 |
| Commit-Meldungen mit einem der beiden | — | 9 |

`docs/archive/` trägt zusätzlich „Brudi" in 2 Dateien (4 Fundstellen) und „Meister" in 1 Datei (2 Fundstellen).

**Die bisherige Notiz führte drei Stellen.** Sie war keine Zählung, sondern eine Aufzählung dessen, was zufällig aufgefallen war — die tatsächliche Menge liegt zwei Größenordnungen darüber. Dieselbe Klasse wie die „Manager-Signatur-Drift über 19 Dateien" in der Fundliste: eine Zahl ohne die Abfrage, die sie erzeugt hat.

**Die Falle bei der Umsetzung — sie ist der Grund, warum hier ein Kriterium steht und keine Ersetzung:**

> **Kleingeschriebenes `meister` ist die `user_id` des Systems und muss bleiben.** Es steht in 33 Dateien, im Schema, in Redis-Schlüsseln, in jedem Paar-Beispiel und in gemessenen Ausgaben. Wer über `[Mm]eister` ersetzt, zerstört die Doku des Paar-Schemas.

Zu ändern ist, was die **Rolle** benennt, nicht was die **Kennung** nennt. Ein großer Teil der Fundstellen steht dabei im Fließtext (*„Brudi commitet erst, wenn alle Konsumenten umgestellt sind"*, *„Diff-Review durch Meister"*) — das ist Umformulieren, nicht Ersetzen, und deshalb ein eigener Durchgang und keine Nebenarbeit. ⬜ Prio mittel

**Entschieden am 30.07.2026:** Der Umzug auf die neue Plattform nimmt die Historie **unverändert** mit. Der Inhalt stand bereits öffentlich; der Umzug legt nichts neu offen. Die Säuberung ist davon getrennt.

**Die Reihenfolge ist nicht beliebig:** erst der heutige Baum, dann — falls überhaupt gewollt — die Historie. Eine gesäuberte Historie unter einem Baum, der die Namen weiter trägt, wäre Aufwand ohne Wirkung. Ein Rewrite bleibt danach möglich und kostet dann einen Force-Push auf veröffentlichte Historie, also eine eigene Freigabe.

**Nicht in diesem Auftrag:** `archive/` — dort steht Aufgegebenes, das ausdrücklich als historisch geführt wird. Ob es mitgezogen wird, ist beim Durchgang zu entscheiden, nicht vorher.

**Dieser Eintrag ist der letzte Schritt seiner selbst.** Er nennt die beiden Begriffe wörtlich, weil ein Auftrag, der sein Ziel nicht benennt, nicht ausführbar ist — und solange sie in hundert Dateien stehen, fügt das nichts hinzu. Ist der Bestand geräumt, sind die Nennungen hier die letzten im Repositorium. Dann wird der Eintrag umformuliert und auf sein Ergebnis reduziert; er darf nicht als sein eigener Rest stehen bleiben.

**Zusammenhang:** `F-PUB-1` (Protokolle gehören nicht ins Repositorium — dieselbe Grenze, andere Seite).

---


## Audit: REGISTER-SPIEGEL-DURCHGANG — wo spiegelt sonst eine Aufzählung ein Register? (Chat 111)

**Kategorie:** [BAU] BAUART

**Zustand:** offen — nachgesehen am 25.08.2026. Die verlangte Messung ist nicht angesetzt worden.

In `services/pixie/router.py` entschied eine **Tabelle neben dem Register** darüber, welcher periodische Agent läuft — dieselbe Zuordnung ein zweites Mal geführt, ohne dass ein Auseinanderlaufen bemerkt worden wäre. Ein neu registrierter Agent gewann den Heartbeat, fand keine Route und starb mit einer Warnung; weil der Takt einen Gewinner je Runde kennt, lief in dieser Runde auch sonst nichts. Behoben durch Rückfall auf Namensgleichheit — die Tabelle bleibt nur noch für die Fälle, in denen Zeitplan- und Agentenname wirklich abweichen (`charakter_hash` → `charakter`).

**Die Instanz ist zu, die Form nicht.** Offen und **nicht gemessen:** Wo sonst im Bestand führt eine Aufzählung dieselbe Zuordnung wie ein Register, ohne dass ein fehlender Eintrag lauter ist als eine Warnung? Zu prüfen sind Zuordnungs-Literale, die neben einer Registry, einer Enum oder einer Tabelle stehen und von Hand nachgepflegt werden müssen.

**Der Durchgang braucht ein Messdatum:** Kandidaten zählen, je Fall entscheiden — ableitbar (dann ableiten) oder echt abweichend (dann bleibt die Tabelle, aber der Fehlschlag wird laut). ⬜ Prio mittel

**Zweite Instanz gefunden, 30.07.2026 — die Toolbar des Clients.** `client/ui/main_window.py` führt in `_TOOLBAR_PANELS` eine Liste von Button-Beschriftungen; verdrahtet wird ein Button nur, wenn seine Beschriftung **exakt** auf das `PANEL_LABEL` eines registrierten Panels trifft. Der Anzeigetext ist damit zugleich der Verbindungsschlüssel. Trifft er nicht, fällt der Button auf einen Platzhalter-Zweig, der beim Klick nur eine Zeile loggt — kein Fehler, keine Warnung, der Reiter öffnet nichts.

Aufgefallen beim Ergänzen eines Symbols im Reiter „Charakter": Die Änderung an einer der beiden Stellen allein macht das Panel unerreichbar. Gemessen mit beiden Stellen geändert: 9 von 9 registrierten Panels verdrahtet, kein verwaistes. Gegenprobe mit nur einer geänderten Stelle: `Charakter` als Platzhalter, `🧬 Charakter` als registriertes Panel ohne Button.

**Zwei Auswege, beide klein:** Die Liste über `PANEL_LABEL` ableiten statt sie zu führen — dann ist die Doppelung weg; oder `_build_toolbar` beim Aufbau melden lassen, welche registrierten Panels keinen Button haben. Der zweite ist drei Zeilen und macht den Fehlschlag laut, ohne das Verhalten zu ändern.

**Zusammenhang:** ALLOWLIST-DRIFT (andere Form von Drift) · `novaberg-lesson_l_gelesen-ist-nicht-wirksam.md` (Fall 3 der Klasse).

---
