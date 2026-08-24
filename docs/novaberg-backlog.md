# Novaberg — Backlog (Zukunftskonzepte)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Backlog — Konzipierte, noch nicht implementierte Features
**Stand:** 24. August 2026, 13:35 UTC (der Matrix-Epic loest seine Abschaltbedingung ein — Telegram ist aus). Davor: 23. August 2026, 21:55 UTC (zwei Stellen zum Fehlversuchspfad markiert — er legt seit heute still statt zu loeschen; die Auswahl nach hoher Salienz bleibt)
**Verlauf:** [Verlauf des Standes](#verlauf-des-standes) — 38 Eintraege, juengster zuerst
**Pfad:** novaberg/docs/novaberg-backlog.md
**Quellen:** nova-08-k.md (Kognitive Anreicherung), nova-10-k-backlog.md (Skill-System), nova-01-t-c-backlog.md (Node-Konfiguration)

---

## DATEIINDEX-GRAPHKANAL — Entitäten aus dem Dateiinhalt statt aus den Stichwörtern (23.08.2026)

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

## Die Rangordnung — Bänder statt Einzelurteile (09.08.2026)

**Der Anlass ist ein Befund über diese Datei, nicht über die Arbeit.** Gemessen am 09.08.2026: **184 offene Einträge** — 56 hier, 128 in `novaberg-bugs.md`. Davon tragen **18 eine Priorität und 166 keine.** Die Priorität ist Pflichtteil jedes Eintrags; sie fehlt in neun von zehn Fällen.

Und die 18 vorhandenen sind das kleinere Problem in der besseren Verkleidung: Jede wurde beim **Anlegen** des Eintrags gesetzt, keine je gegen die anderen gehalten.

> **Eine Priorität, die nur gegen sich selbst steht, ist ein Gefühl über einen Eintrag — keine Reihenfolge.** „Hoch" heißt dann „das ärgerte mich, als ich es aufschrieb".

Deshalb steht hier eine **Tabelle** und nicht in jedem Eintrag eine Zahl. Ein Band ist eine Aussage über das Verhältnis zu den anderen; es entsteht dadurch, dass der Eintrag neben die anderen gelegt wird.

### Die vier Bänder

| Band | Bedeutung | Die Prüffrage |
|---|---|---|
| **A** | **Hält eine laufende Reihe an.** Solange er offen ist, ist eine aufgesetzte oder laufende Messung nicht auswertbar. | *Verfällt Maschinenzeit oder Material, wenn er liegen bleibt?* |
| **B** | **Gehört zu einer laufenden Reihe.** Sie läuft auch ohne ihn, aber sein Ergebnis geht in ihres ein. | *Würde ich ihn beim Auswerten der Reihe vermissen?* |
| **C** | **Entwertet eine Aussage außerhalb der laufenden Reihen.** Stiller Fehler, Defekt am Messwerkzeug, Vorgabewert an einer Stelle, an der ein Ausfall gehört. | *Steht heute irgendwo eine Zahl, die dadurch falsch ist?* |
| **D** | **Richtig, aber ohne Anschluss an eine offene Frage.** | — |

### Zwei Regeln, ohne die die Bänder wieder Stimmungen werden

**1. Band A ist knapp und bleibt es.** Es fasst nur, was als Nächstes tatsächlich angefasst wird. Wächst der Bedarf, muss etwas **heraus** — nicht das Band wachsen. Ein A mit zwanzig Einträgen ist dasselbe wie „hoch" mit siebenundzwanzig.

**2. Das Band wird beim Lesen vergeben, nicht beim Anlegen.** Ein neuer Eintrag kommt **ohne** Band herein. Er bekommt eins, wenn die Tabelle das nächste Mal gegen den Bestand gehalten wird. Das ist der ganze Unterschied zum bisherigen Verfahren und der Grund, warum ein fehlendes Band hier kein Mangel ist.

### Die laufenden Reihen — Stand 09.08.2026

Die Zugehörigkeit zu einer dieser Reihen hebt einen Eintrag; alles andere sinkt.

| Reihe | Zustand |
|---|---|
| **1 — Charakterbildung** | 18 Bögen, 540 Turns, aufgesetzt und zurückgesetzt, wartet auf die GPU |
| **2 — Haltungsraum und Zuwendungsrad** | Beitragsverhältnisse gefallen, nicht kalibriert (`F-HALTUNG-1`) |
| **3 — Erkenntniszyklus und der Abfluss der Shadow-Queue** | Vorfrage am 09.08. beantwortet, Entscheidung über 614 Altaufträge offen |
| **4 — Die Linter-Wände** | vier Familien hart, `B` bei null und nicht als Kürzel schaltbar |

### Band A — leer, Stand 16.08.2026

> **Beide Eintraege waren erledigt, bevor sie hier oben standen — und keiner der beiden wurde je angefasst, weil an keinem etwas zu tun war.**
>
> | Eintrag | Abhilfe gebaut | in Band A gefuehrt |
> |---|---|---|
> | `PROMOTION-FENSTER-LAEUFT-AB-STATT-LEER` | 09.08.2026 | stand bereits, Marke nie gezogen |
> | `REIHE-GEWICHTET-ZEILEN-STATT-ERHEBUNGEN` | **01.08.2026** | **11.08.2026** — zehn Tage nach der Abhilfe |
>
> **Der Befund ist ueber die beiden Faelle hinaus einer ueber dieses Verfahren.** Regel 2 dieses Abschnitts sagt: *„Das Band wird beim **Lesen** vergeben, nicht beim Anlegen."* Genau das ist geschehen — gelesen wurde der **Eintrag**. Ein Eintrag beschreibt aber den Code von damals, und die Pflicht, ihn gegen heute zu halten, greift bisher erst **vor der Umsetzung**. Zwischen Rangvergabe und Umsetzung liegt jedoch die ganze Zeit, in der das Band steuert.
>
> **Daraus die Schaerfung, die hier fehlte: Ein Band wird gegen den Code vergeben, nicht gegen den Eintrag.** Der Aufwand ist klein und im Nachhinein beziffert — bei `REIHE-GEWICHTET-ZEILEN-STATT-ERHEBUNGEN` genuegte ein `git log -S` auf den Bezeichner, den der Eintrag selbst nennt; der Kommentar im Code trug denselben Satz wie der Eintrag.
>
> **Was das fuer den naechsten Durchgang heisst:** Band A ist nicht abgearbeitet, es ist **leergeraeumt**. Es muss aus den ungebaenderten Eintraegen neu gefuellt werden, und die Kandidaten sind diesmal gegen den Code zu halten, bevor sie ein Band bekommen.

### Band A — neu gefuellt am 16.08.2026, ein Eintrag

**Der Durchgang folgte der eigenen Reihenfolge dieses Abschnitts** — zuerst die Bugs mit `🔧 offen` — und der neuen Regel, dass ein Rang **gegen den Code** vergeben wird, nicht gegen den Eintrag.

| Kennung | Reihe | Was er anhaelt |
|---|---|---|
| `UNREGISTRIERTER-AGENT-GEWINNT` | 3 | **Er zerstoert laufend Material, und seit dem 16.08.2026 schneller.** Ein Queue-Auftrag fuer einen nicht registrierten Agenten gewinnt den Heartbeat, scheitert sofort und verbrennt seine drei Versuche im Takt des Heartbeats — gemessen am laufenden System: `vertiefen` id=1004 durchlief `1/3`, `2/3` und die Verwerfung in **90 Sekunden**, danach `DELETE`. **192 aktive `vertiefen`-Auftraege stehen darauf**, ⌀ Salienz 0,750, aeltester vom 30.07. Bisher kam die Auftragsart kaum dran, weil eine Recherche den Platz minutenlang hielt; **seit der Frist-Reparatur vom 16.08. dreht der Platz schneller**, und `vertiefen` rueckt nach — in zwei Stunden dreimal gezogen. Der Eintrag ist vom 27.07. und trug seither Prioritaet *hoch*, ohne je ein Band zu bekommen. **Sein `Was fertig waere` ist die kleinste denkbare Abhilfe:** *„Ein Auftrag ohne Agenten kann den Heartbeat nicht gewinnen."* **Zur Haelfte veraltet:** Der Eintrag nennt `vertiefung` **und** `nachfragen` als fehlend; `nachfragen` ist seit dem 05.08.2026 gebaut (`PIX-MIG-7`), nur `vertiefung` fehlt |

**Was der Durchgang sonst ergab — mit Zahlen, damit die Reichweite nachrechenbar ist.** Geprueft wurden **41** offene Bug-Eintraege mit drei mechanischen Kriterien und **5** davon zusaetzlich von Hand gegen Code und Betrieb.

| Kriterium | Treffer | davon echt |
|---|---|---|
| Ein genannter Bezeichner existiert nicht mehr | 5 | **0** — Datenwerte, URLs, Fremdfelder und ein Archivtabellenname |
| Eine Erledigt-Vokabel im Koerper | 9 | **0** — durchweg *„Geschlossen, wenn"* als Abschlusskriterium |
| Ein `✅`-Abschnitt im Koerper eines `🔧`-Eintrags | 0 | — (das Kriterium hat heute frueh seinen einen Fall gefunden) |

**Zwei Eintraege mit Prioritaet *hoch* sind durch die Handpruefung hinfaellig geworden** und gehoeren in den naechsten Durchgang zur Schliessung, nicht in ein Band:

- `ENTITAETEN-OHNE-EMBEDDING` (29.07.) — *„Entitaeten entstehen ohne Zusammenfassung und ohne Embedding."* Gemessen am 16.08.2026: **0 von 704** ohne Embedding. Ob der Erzeuger nachgezogen wurde oder ein Nachlauf gefuellt hat, ist ungeprueft — die Frage nach dem **Warum** steht noch, das Symptom nicht mehr.
- `CHARAKTERAGENT-AUSGEHUNGERT` (27.07.) — *„Vier Heartbeats in Folge ging der Charakter leer aus."* Gemessen ueber 39 h: **22 Gewinne**, Wartezeit zuletzt **0,37 h**. Vermutlich eine Folge der Zwei-Spuren-Trennung; nicht abschliessend geprueft.

**Einer wurde bestaetigt und gehoert nicht nach A:** `RECHERCHE-SALIENZ-KONSTANT` — das Literal `"salienz": 0.7` steht unveraendert in `agents/recherche/agent.py`. Er entwertet eine gespeicherte Groesse, zerstoert aber nichts; das ist Band **C**.

> **Kein stiller Deckel:** Von 41 offenen Eintraegen sind **5** von Hand gegen den Code gehalten worden, ausgewaehlt danach, ob ihr Wortlaut laufenden Verlust behauptet. **Die uebrigen 36 sind ungeprueft** und koennen denselben Zustand tragen wie die beiden oben — erledigt und unmarkiert. Der Durchgang ist damit begonnen und nicht abgeschlossen.

### Band A — die geschlossenen Eintraege

| Kennung | Reihe | Was er anhält |
|---|---|---|
| ~~`PROMOTION-FENSTER-LAEUFT-AB-STATT-LEER`~~ | 1 | **Geschlossen am 16.08.2026 — der Eintrag stand acht Tage zu Unrecht an der Spitze.** Die Ursache war bereits am 09.08. widerlegt (kein Fenster, kein Loeschen — die Promotion **verhungerte**) und die Abhilfe am selben Tag gebaut: die Zwei-Spuren-Trennung, seit der die Promotion auf der `cpu`-Spur laeuft und nicht mehr gegen eine Recherche antritt. **Nur die Marke wurde nie nachgezogen.** Nachgemessen am **Bestand** statt am Zeugen, sieben Tage spaeter: `konrad` traegt **69** LZG-Knoten statt des einen, der den Defekt belegte; die fuenf Personas liegen zwischen 48 und 69 bei KZG-Staenden von 88 bis 98, das produktive Paar bei 2005 zu 2203. Ueber zwei Stunden gewann die Promotion **22-mal** die CPU-Spur und fand jedes Mal eine leere Queue vor — **Rueckstand null**. Der benannte kleine Rest (die letzten Auftraege einer Persona nach dem Zurueckschalten) bleibt und ist kein Band-A-Fall |
| ~~`RAD-STABILITAET-UNGEMESSEN`~~ | 2 | **✅ gemessen am 11.08.2026 — der Eintrag ist beantwortet.** Über drei Quellen mit je vier Läufen bei unveränderter Eingabe: Streuung **0,18 · 0,18 · 0,22** auf der Dreierskala, **0,061 · 0,062 · 0,080** mit einer Nachkommastelle. Die Trennschärfe zweier Personen steigt dabei von 2,4–3,3 σ auf 10,2–12,9 σ. Daraus zwei Bauten: `F-RAD-2` (drei Läufe, Median) und `F-RAD-3` (elf Stufen statt drei). **Die Kalibrierung der Beitragsverhältnisse ist damit freigegeben** — sie liefe jetzt gegen ein Rauschen bekannter und kleiner Breite |
| ~~`REIHE-GEWICHTET-ZEILEN-STATT-ERHEBUNGEN`~~ | 2 | **Geschlossen am 16.08.2026 — und er war bereits erledigt, als er hier eingetragen wurde.** Der Eintrag entstand am 11.08.2026; `reihe_laden` gruppiert seit **`837d6df` vom 01.08.2026, 16:13** nach `erhebung_id` und zieht die Laeufe einer Erhebung mit `rad_zusammenfassen_gleichgewichtig` zusammen — *ohne Verfall, alle gleich alt*. Der Kommentar im Code nennt sogar denselben Grund wie der Eintrag: **Das Fenster zaehlt Erhebungen, nicht Zeilen.** Das ist Weg 2 der beiden hier vorgeschlagenen, zehn Tage vor dem Vorschlag gebaut. **Bezeugt ist er auch:** `test_drei_laeufe_einer_erhebung_ergeben_einen_punkt` und `test_die_laeufe_einer_erhebung_werden_gleich_gewichtet` in `tests/test_rad_messreihe.py`, am 16.08.2026 gruen (28 Tests). Nachgesehen wurde am Code, nicht am Eintrag |

**`PROFIL-HISTORIE-FEHLT` stand beim ersten Entwurf dieser Tabelle in Band A und gehört nicht dorthin.** Die Begründung lautete: Ohne Profilhistorie sei nicht messbar, ob ein behaltenes Rad früh genug wirkt. Der Eintrag selbst widerlegt das seit dem 02.08.2026 — `charakter_hash` führt das Paar im Primärschlüssel, und **die Räder sind ohnehin historisiert**: `charakter_rad_messung` trägt am 09.08.2026 231 Zeilen über 20 Kennungen seit dem 01.08. Die Frage nach dem Rad hängt an dieser Tabelle, nicht an der Profilhistorie. Er steht in Band B. **Das ist die Regel bei der Arbeit:** Ein Band, das gegen den Eintrag gehalten wird statt gegen die Erinnerung an ihn, korrigiert sich beim Lesen.

### Neu vom 20.08.2026 — die Länge ist gesetzt, nicht gemessen

| Kennung | Was er anhält |
|---|---|
| `LAENGENVORGABE-UNGEMESSEN` | **Drei Zahlen der Antwortlänge sind Setzungen ohne Messung im Betrieb.** Die halbierten Korridore in `UMFANG_SPANNE` sind eine Entscheidung nach einem Einzelbefund (12 Zeichen Gruß → 838 Zeichen Antwort); `LEICHT_FAKTOR` und `LEICHT_SOCKEL` sind frei gewählt. **Was dagegen gemessen ist, ist der Vorbehalt:** Bei identischer Vorgabe streute die Antwortlänge am 17.08.2026 um den Faktor 2,68 — die Vorgabe bindet nur schwach, und eine Halbierung halbiert nicht. Zu messen ist deshalb nicht die Konstante, sondern die **Wirkung**: dieselben Turntypen vor und nach dem 20.08., Ist-Länge gegen Korridor. Der Lauf braucht echte Modellaufrufe. |
| `MASSBLOCK-IM-BETRIEB-UNGEMESSEN` | **Der Verfasser liest die drei fachlichen Größen seit dem 20.08.2026 — ob es seinen Stoff ändert, ist offen.** 10 Zeugen belegen, dass der Block im Prompt steht und die richtigen Größen trägt; keiner belegt, dass sich der erzeugte Inhalt dadurch ändert. Der Präzedenzfall steht in derselben Reihe: `HALTUNG-OHNE-LESER` war zwei Wochen gebaut, gemessen und wirkungslos, weil kein Prompt die Größen las. **Die Prüfform ist der Vergleich desselben Turns mit und ohne Block**, nicht die Anwesenheit des Blocks. |

### Neu vom 20.08.2026 — der Index nimmt fünf Textformate an und versteht eines

| Kennung | Was er anhält |
|---|---|
| ~~`GLIEDERUNG-NUR-MARKDOWN`~~ → **umgesetzt am 20.08.2026** — vier Erkenner statt einem: reStructuredText (Unterstreichung, Ebene aus der Reihenfolge der Zeichen), Org-Mode (Sterne, `#+BEGIN_`/`#+END_`-Bilanz), AsciiDoc (Gleichheitszeichen, Blockbegrenzungen) und `.txt` als **ausdrückliche leere Registrierung**. Gegen sechs echte `.rst`-Dateien aus installierten Paketen gemessen: 24 Überschriften, 0 nicht erhoben. Ein Zeuge hält seitdem die beiden Mengen gegeneinander — jede zugelassene Endung hat einen Erkenner. Der ursprüngliche Befund: **`DATEIEN_INDEX_ENDUNGEN` lässt `.md`, `.txt`, `.rst`, `.org` und `.adoc` zu; `_ERKENNER` kennt allein Markdown.** In reStructuredText steht die Überschrift über einer Unterstreichung, in Org-Mode beginnt sie mit einem Stern, in AsciiDoc mit einem Gleichheitszeichen — keine davon trägt ein Rautenzeichen. Seit dem 20.08.2026 wirft eine solche Datei `FormatOhneErkennerError` statt still eine leere Karte zu liefern; **der Riegel ersetzt die Erkenner nicht**, er macht ihr Fehlen sichtbar. Heute unbetreten: alle 174 indizierten Dateien sind Markdown. **Zu bauen sind drei zeilenbasierte Erkenner** — die Syntax ist in wenigen Zeilen zu fassen, und für keines der drei Formate lohnt eine Abhängigkeit. `.txt` bleibt bewusst ohne Erkenner: Dort ist die leere Karte die richtige Aussage, und das muss als Registrierung dastehen statt als Lücke. |
| ~~`MARKDOWN-ERKENNER-IST-HANDARBEIT`~~ → **umgesetzt am 20.08.2026** (`markdown-it-py 3.0.0`, Grundfassung `commonmark`; über den Bestand gemessen: 174 von 174 Dateien liefern dieselbe Karte wie zuvor, nachdem zwei Fehlauszeichnungen behoben waren). **Eine Aussage dieses Eintrags war falsch und ist widerlegt:** Die Zaunbilanz fängt *nicht* nur, was ein Parser ohnehin richtig macht — an der defekten Datei fand der Zeilenautomat 5 von 83 Überschriften, CommonMark **45 von 83**. Beide Karten sind falsch; die Bilanz steht deshalb weiterhin **vor** dem Parser. Der ursprüngliche Befund: **Der Markdown-Erkenner ist ein zeilenweiser Regex-Automat und kennt nur zwei Regeln von CommonMark** — Rautenüberschriften und Zäune aus mindestens drei Backticks oder Tilden. Nicht erkannt: Setext-Überschriften (Text über `===` oder `---`), eingerückte Codeblöcke, Zäune aus vier und mehr Zeichen, verschachtelte Zäune, YAML-Frontmatter. Am Bestand gezählt: keine Datei mit langem Zaun, keine mit Frontmatter, **eine** mit möglicher Setext-Überschrift — die Fälle sind also latent und nicht akut. **Der Weg ist `markdown-it-py`** (reines Python, CommonMark-konform, keine Systemabhängigkeit); heute ist kein Parser installiert. Die Zaunbilanz aus `BLOCKKARTE-STILL-HALBIERT` bleibt daneben stehen: Sie fängt, was ein Parser gar nicht erst falsch macht, kostet aber nichts. |

### Neu aus Chat 152 (19.08.2026) — die Mehrfacherhebung, die eine Stufe zu spät greift

| Kennung | Was er anhält |
|---|---|
| `PROFIL-EINMALERHEBUNG` | **Die fünf Profile werden einmal erhoben und stehen bis zum nächsten Takt — die Räder, die aus ihnen gerechnet werden, dreimal.** `F-RAD-2` begründet die Mehrfacherhebung wörtlich damit, dass ein Wert *„bei der Destillation EINMAL geschrieben wird und bis zur nächsten stehenbleibt; ein unglücklicher Lauf legte ihn sonst für Tage fest"*. Genau das gilt für den Kern-Hash, und dort greift die Regel nicht. **Gemessen am 19.08.2026:** Derselbe unveränderte Prompt liefert über drei Läufe **16,5 / 24,5 / 19,7 %** Aussagen über das Gegenüber; das an diesem Tag gespeicherte Profil trug **42 %**. Der Bestandswert war der schlechteste Lauf, und er ging zwölf Stunden lang in jeden Responder-Prompt und in beide Räder. **Was fertig wäre:** dieselbe Bauart wie bei den Rädern — mehrfach erheben, den mittleren Lauf speichern, die Einzelläufe mit gemeinsamer `erhebung_id` in eine Senke. Der Preis ist bekannt und der Grund, warum das zu überdenken und nicht sofort zu bauen ist: Ein Profillauf dauert 340 bis 500 s, fünf Profile je Paar mal drei Läufe sind rund anderthalb Stunden je Destillation auf demselben CPU-Modell, das Pixie teilt. **Offen ist deshalb nicht das Ob, sondern welche der fünf Profile es brauchen** — der Kern speist Räder und Responder, die übrigen vier nicht in gleichem Maß |

### Neu aus Chat 146 (17.08.2026) — der Wächter, den die Reparatur nötig gemacht hat

| Kennung | Was er anhält |
|---|---|
| `PROFIL-KONTRAST-UNGEWACHT` | **Kein Werkzeug prüft, ob zwei Profile desselben Paares verschiedene Personen beschreiben.** Am 16.08.2026 lagen beide Zuwendungsräder bei einer mittleren Abweichung von **0,0202** über zwölf Speichen — Lenkungsdrang 0,923 gegen 0,896 —, und das elf Tage lang, bei grüner Suite und plausibler Ausgabe. Gefunden hat es das Nebeneinanderlegen zweier Radar-Bilder von Hand. **Die Größe ist laufend rechenbar** (`labor/werkzeug/rad_spiegelung.sql`), und sie hat nach der Reparatur auf 0,2634 reagiert, also Trennschärfe. **Was fertig wäre:** Fällt die mittlere Abweichung der Räder eines Paares unter eine Schwelle, ist das ein Befund und kein Ergebnis. Der Grund, warum es einen eigenen Wächter braucht: Ein Charakterprofil ist ein wohlgeformter Text — es gibt keinen Rand, an dem etwas fehlt, und keine Zusicherung, die sich auf seinen **Inhalt** bezieht. Ein Zeuge hat den Defekt sogar festgeschrieben (`test_der_kern_prompt_traegt_die_gesprochenen_worte` sicherte zu, dass **beide** Sprecher im Prompt stehen). Schwelle offen — vor der Festlegung braucht es Werte mehrerer Paare über mehrere Takte |

### Band B — was in einer laufenden Reihe mitläuft

**Neu aus Chat 135 (11.08.2026):**

| Kennung | Was er anhält |
|---|---|
| `HASH-DIRTY-ALTLASTEN` | Der CharakterAgent räumt `hash_dirty` nur für das **aktive** Paar weg. Jede Person, die je einen Bogen hatte, trägt einen liegengebliebenen Schlüssel — am 11.08.2026 fünf Stück. Sie lassen die Vorbedingung des nächsten Bogens dieser Person anschlagen, und der Abbruch sieht aus wie ein Fehler des Laufs statt wie ein Rest des vorigen |
| `PROFILTEXT-SCHRUMPFT-MIT-MATERIAL` | Zweimal gemessen, in zwei Bögen: Mehmet 1597 → 1293 Zeichen, Sarah 1240 → 989, jeweils mit **zwanzig Turns mehr** Material. Vermutlich die Vorgabe *„kompakt … in 2-5 Sätzen"*: Je mehr das Modell sagen will, desto härter verdichtet es. Ungeprüft |
**Neu aus Chat 136 (11.08.2026):**

| Kennung | Was er anhält |
|---|---|
| `ZUGSCHWELLE-AUF-FREIEN-WERTEN` | ~~`UEBERSTEUERUNG_AB = 0.8` ist ein Startwert und kein Messergebnis. Er stammt aus der Zeit der Rundungsvorgabe: Auf einer Nachkommastelle war oberhalb von 0.9 nur die 1.0 erreichbar, und die Schwelle brauchte Raum darunter. Seit `F-RAD-4` gibt es kein Raster mehr — **wie oft eine Speiche ohne Raster über 0.8 oder 0.9 kommt, ist ungemessen.** Alle 30 Läufe, aus denen die heutigen Zahlen stammen, sind gerastert erhoben. `labor/werkzeug/raster_probe.py` liefert die Verteilung; danach gehören Schwelle und Exponent nachgezogen~~ → **Gemessen am 12.08.2026, 01:49 UTC, und die Schwelle steht auf 0,9.** Zwei Paare, je sechs Läufe gerastert und sechs frei. Der Befund war nicht der erwartete: **Das Gitter hat `distanz` heruntergerundet** — zwölfmal exakt 0,9 gerastert gegen 0,93 bis 0,96 frei. Eine Schwelle auf dem Rasterwert löst deshalb nie aus, nicht weil das Urteil darunter liegt, sondern weil es darüber nicht darstellbar war. Ziehende Speichen je Lauf: bei 0,8 zwei bis zweieinhalb, bei 0,9 knapp eine. **Rest benannt:** Die Streuung bleibt offen — mehmet wurde unruhiger (0,0151 → 0,0344), sarah ruhiger (0,0467 → 0,0370); bei n=6 je Zelle trägt keine Richtung. Der Exponent ist unverändert 2 und ungemessen |
| `VERDICHTUNG-UEBRIGE-VIER-PROMPTS` | **Das Beziehungsprofil ist gemessen (12.08.2026) und nicht entscheidbar wie der Kern.** Zwei Personen, identisches Material, identischer Kern, je gedeckelt gegen offen: Die Länge steigt achtfach (537→3990 und 562→4219), und **die offene Fassung liest beide Male wärmer** (Faktor +0,093 und +0,035). Das ist die einzige Aussage, die über beide Personen trägt. **Die Rauschaussage trägt nicht:** Bei der einen Person fällt die Spanne von 0,2209 auf 0,0625, bei der anderen steigt sie von 0,0167 auf 0,0734. Beim Kern hatten beide Personen dieselbe große Senkung gezeigt (0,251→0,063 und 0,104→0,004) — hier zeigen sie Gegenteiliges. Bemerkenswert und mit n=3 nur als Muster zu nennen: Die **offene** Fassung landet bei beiden bei 0,06–0,07, die **gedeckelte** einmal bei 0,02 und einmal bei 0,22 — nicht die offene ist ruhiger, die gedeckelte ist unberechenbar. Vor einer Entscheidung braucht es eine dritte Person oder mehr Läufe je Zelle. Die drei übrigen Prompts (adaptiv, Intention, Emotion) sind ungemessen; sie speisen **nicht** das Rad, sondern direkt den Responder-Prompt, und dort ist die Messgröße eine andere — dieselbe Probe passt nicht. Jeder hat einen eigenen Abnehmer — das Beziehungsprofil ist die zweite Hälfte der Rad-Quelle —, und fünf offene Profile je Paar sind rund anderthalb Stunden je Erhebung. Die Probe steht und ist billig: `labor/werkzeug/verdichtung_probe.py` mit getauschtem Deckel |
| `KERN-EINBETTUNG-NACH-DEM-DECKEL` | `kern_hash` wird nicht nur gelesen, sondern **eingebettet**: Der Lückenagent vergleicht Kandidaten gegen ihn, Schwelle `GV_CHARAKTER_RESONANZ_SCHWELLE = 0.40`. Der Kommentar daneben sagt wörtlich *„begründeter Startwert, kein Messergebnis. Nach Live-Betrieb prüfen."* Ein Profiltext, der fünfmal so lang ist, embeddet anders — Cosinus-Werte ziehen sich zur Mitte zusammen. Der Deckel sitzt damit oberhalb eines nie gemessenen Schwellenwerts |
| ~~`MESSREIHE-MISCHT-ZWEI-RASTER`~~ | ~~`charakter_rad_messung` trägt jetzt drei Erhebungsarten nebeneinander: Dreierskala, eine Nachkommastelle, ohne Raster. Die Zeilen sind nur über die Werte selbst unterscheidbar — es gibt keine Spalte dafür. Jede Auswertung über die ganze Tabelle mischt drei Messgeräte~~ → **Geschlossen am 12.08.2026, und die Wirkung war größer als der Eintrag vermutete.** Es war keine Frage der Auswertung: `reihe_laden` speist die Reihe in den **Produktivwert**, und bei `nova → meister` stammten **58,7 %** des angezeigten Faktors aus abgelösten Geräten — 1,3582 gemessen, 1,2099 angezeigt. Entschieden wurde löschen statt filtern. 259 Zeilen sind gesichert (`charakter_rad_messung_archiv_20260812`) und entfernt, der Stichtag steht in der Fundliste. **Ohne Codeänderung** — die Tabelle trägt nur noch ein Messgerät |
| ~~`RESPONDER-ALS-AUFGABE`~~ | Der Responder-Prompt stellt **Kontext mit einer Stilnotiz**, nicht eine Aufgabe — und bindet deshalb nicht (0 von 6 Korridoren gegen 6 von 6 der Aufgabenform, `novaberg-haltungsraum_k.md` §3.0). Gebaut werden soll die Gliederung aus §3.0a: Konstellation zuerst, Charaktere, Szene, Regie unmittelbar vor dem Text, Ausgabezeile. Dabei fällt weg, was doppelt wäre: die Arousal-Längenregel, die Beziehungsdynamik-Sätze, der Tonblock, und die Fragen-Zeile aus der Landschaft (die der **GV-Knoten** weiter braucht, der Responder nicht). **Offen und größer als der Prompt:** Was steht in `[TEXT]` — der fertige Absatz des Verfassers oder Material? Zwei Modellläufe über denselben Inhalt glätten ihn; was das kostet, ist an der Verdichtungsmessung ablesbar → **Geschlossen am 13.08.2026.** Die Gliederung steht: `[ROLLE]` mit Konstellation und **doppelter** Prüfbedingung, `[SZENE]`, beide Personen, `[ZWISCHEN BEIDEN]`, Regie unmittelbar vor dem Text. Die vier genannten Doppelungen sind entfernt, dazu eine fünfte, die beim Umbau selbst entstand (Landschaft in Szene und Regie — von der Gegenprobe gefunden). Nicht vorgesehen und hinzugekommen: **eine Anrede, eine Bedeutung** — »du« ist der Schauspieler, über Person A wird in dritter Person gesprochen; sieben von dreizehn Blöcken hatten drei Bedeutungen gemischt. **Der Rest ist benannt:** Die offene Frage nach `[TEXT]` bleibt offen und hat eine Zahl bekommen — der Verfasser liefert rund 1400 Zeichen für einen 350-Zeichen-Korridor, weil er **keine** Mengenangabe erhält |
| `SZENE-STATT-REGIE-IN-DEN-CLUSTERN` | Vier der vierzehn `CLUSTER_BESCHREIBUNGEN` tragen einen Befehl (`regen` „Halten, da sein", `schmollen` „Nicht drängen", `nebel` „Leise da sein", `gewitter` „Nicht verteidigen"). Er gilt für jeden Charakter gleich und steht **vor** dem Rad — die Haltungsgrößen können ihn nicht bewegen. Die Regel für die Umschreibung **und der ausgeschriebene Vorschlag für alle vierzehn** stehen im Konzept §3.0b: Die Szene sagt, was ist; kein Imperativ, kein „nicht". **Zu beachten:** Die Tabelle speist drei Prompts — GV, Verfasser, Responder. Der GV-Knoten benutzt sie als Rahmen für die Strategiewahl, nicht als Klassifikator; eine sinnlichere Szene macht ihn besser, nicht wackliger (geprüft am Code) |
| `AROUSAL-ACHSE-SCHNEIDET-DEN-GIPFEL` | Die Energie-Achse binarisiert `arousal` bei 0,5 — und die gemessene Verteilung ist **zweigipflig** mit Bergen bei 0,1–0,3 und 0,4–0,6. Die Schwelle schneidet den zweiten Gipfel mittendurch: Turns, die sich um 0,02 unterscheiden, landen in verschiedenen Landschaften. Genau die Kippkante, vor der §3.1 warnt. **Ein Drittel aller Turns liegt zwischen 0,4 und 0,7** (35,1 % von 522), wo die Landschaft nur ein Bit sieht, die abgelöste Längenregel aber drei Stufen unterschied. Solange das so bleibt, kann `umfang` die Feinheit des Arousal nicht nachtragen — sein Grundwert kommt aus der Landschaft. **Und ein zweiter Punkt daneben:** `arousal_roh` und `arousal_ei` unterscheiden sich stark (Median 0,50 gegen 0,334); welche der beiden in die Achse geht, entscheidet mit, wie oft sie überhaupt anschlägt |
| ~~`FARBTON-OHNE-LESER`~~ | `ei/farbton.py` mischt acht Dimensionen zu 2–5 Sätzen, die die Lage sinnlich beschreiben — und erreicht den Responder nicht. Er geht nur in den GV-Prompt und ins Log. **Dazu ein zweiter Punkt:** Sind alle acht Dimensionen unauffällig, bleibt ein einziger Satz übrig („Das Gespräch ist ruhig und ausgeglichen"). Für eine Anweisung ist Schweigen bei Unauffälligkeit richtig, für eine **Atmosphäre** nicht — die Werkstatt riecht nach Öl, ob jemand aufgeregt ist oder nicht. Die Grundfarbe könnte aus der Landschaft kommen, der Farbton die Abweichung darauf legen → **Geschlossen am 13.08.2026** für den ersten Punkt: Der Farbton steht in `[SZENE]`, hinter der Lage. **Der zweite Punkt ist widerlegt** — der Rückfallsatz tritt im Betrieb nicht ein; über zwölf Stunden Log liefert der Farbton sechs bis sieben Sätze je Turn. **Eine Wirkung ist nicht nachgewiesen:** drei Läufe je Fassung (ohne · schwer · lebhaft) zeigten keinen Unterschied über dem Rauschen, und die schwere Fassung wurde zweimal von drei als lebhaft gelesen. Er steht im Prompt, weil er die Lage beschreibt, nicht weil eine Messung ihn verlangt |
| ~~`PERSON-B-OHNE-BESCHREIBUNG`~~ | Vom Nutzer erreicht **ein** Profil den Responder (das Beziehungsprofil), von Nova alle fünf. Sein Kern fehlt, auch seit die offene Destillation daraus mehrere tausend Zeichen macht. Dazu: Beide Beziehungsprofile stehen unbeschriftet nebeneinander, ohne Angabe der Perspektive — nach dem Paar-Schema sind es verschiedene Aussagen, im Prompt sehen sie gleich aus → **Geschlossen am 13.08.2026.** `[PERSON B — WER ER IST]` trägt seinen Kern (3992 Zeichen im Messturn) und was ihn beschäftigt; `[ZWISCHEN BEIDEN]` trägt beide Blickrichtungen **beschriftet**, und der 300-Zeichen-Deckel auf seinem Beziehungsprofil ist gefallen — er schnitt mitten im Wort ab. **Die Wirkung ist unbelegt:** Vier Verfahren, das Zugehen auf einen bestimmten Menschen zu messen, sind an Fällen mit bekanntem Sollurteil gescheitert (3/6 bei Zufall 2, 3/6 bei Zufall 3, 2/6 mit dem stärkeren Analysemodell und systematisch invers, ein lexikalisches Maß verzerrt). Der Block steht, weil ein Dialog ohne beschriebenes Gegenüber ein Monolog mit Stichwortgeber ist |
| ~~`HALTUNG-OHNE-LESER`~~ | Der Zug ist gebaut, das Kriterium steht, die Zahlen sind gemessen — und **kein Prompt liest die Haltung**. `state["haltung"]` hat außer dem Knoten selbst nur die Anzeige als Leser. Solange §3 des Konzepts fehlt, wirkt der ganze Haltungsraum auf keine einzige Antwort. Das ist die Naht, an der alles andere hängt → **Geschlossen am 13.08.2026** — und die Schließung war eine halbe, was erst am 20.08.2026 auffiel: Das Konzept fordert **zwei** Leser (*„Beide lesen das Ergebnis aus dem Zustand"*) und begründet damit die Position des Knotens im Graphen; gebaut war einer. Der Verfasser las `haltung` bis zum 20.08.2026 **null Mal**. `ei/haltungssprache.py` übersetzt die fünf Größen in die Bänder aus §3.0aa, den Umfang zusätzlich in eine Zeichenspanne, das Arousal in einen der acht Energie-Sätze; angeschlossen unmittelbar vor dem Text. **Gesprochen wird beim Bandwechsel, nicht bei einem Zahlenabstand** — die erste Fassung verglich Zahlen und hätte einen distanzierten Charakter im `feuerwerk` verschluckt (0,90 → 0,82 sind acht Hundertstel, aber »ganz nah« wird zu »vertraut«). Die Arousal-Längenregel ist entfallen. Gemessen: mit einheitlicher Regie 22 von 25 Läufen richtig zugeordnet, mit je eigener **27 von 27** |

| Kennung | Was er anhält |
|---|---|
| `VERDICHTUNG-UNGEPRUEFT` | ~~Fünf Profil-Prompts verlangen *„kompakt"* und deckeln auf zwei bis fünf Sätze — eine Vorgabe aus der Zeit knapper Kontextfenster. Heute schreibt das Hintergrundmodell mit 262 144 Token, gelesen wird mit 32 768; ein Profil von 4000 Zeichen wäre drei Prozent des Lesefensters. **Verdichtung nimmt weg, was Charakter ausmacht.** Die Gegenprobe steht bereit — identisches Material, einmal mit Deckel und einmal ohne —, ist aber nicht gefahren. Zu vergleichen sind zwei Dinge getrennt: der Text zum Lesen und die Streuung des Rades. Fallen sie auseinander, ist das ein Hinweis auf zwei Texte statt einem~~ → **Gefahren und entschieden am 11.08.2026, für den Kern.** Zwei Personen, je drei Läufe je Fassung über die ganze Kette: Spanne **0,2510 → 0,0630** (Mehmet) und **0,104 → 0,004** (Sarah), Faktor unverändert (−0,024). Die offene Fassung liegt damit auf dem Eigenrauschen des Rades — die Destillation legt nichts obendrauf, die gedeckelte das Vierfache. **Der interessante Fall trat nicht ein:** Text und Streuung fallen *nicht* auseinander, derselbe Text ist der reichere und der ruhigere. Der Deckel des Kerns ist gestrichen; **Rest benannt** in `VERDICHTUNG-UEBRIGE-VIER-PROMPTS` und `KERN-EINBETTUNG-NACH-DEM-DECKEL` |

| Kennung | Reihe |
|---|---|
| `KALIBRIERUNG-ZEUGE-TRENNT-SCHWACH` · `PROFILE-LEER-URSACHE-UNBEKANNT` · `PAARLISTE-FEST` · `PROFIL-HISTORIE-FEHLT` | 1 |
| `HALTUNG-SPANNENENDEN-OFFEN` · `HALTUNG-LAENGE-ZWEI-ERZEUGER` | 2 |
| `AUFTRAGSARTEN-OHNE-AGENTEN` · `SHADOW-QUEUE-RUECKSTAND-UNGEMESSEN` · `PIXIE-EIN-SLOT-BLOCKIERT-ALLES` · `RECHERCHE-RETRY-BLOCKIERT-QUEUE` · `VERTIEFEN-AUFTRAEGE-OHNE-THEMA` | 3 |

**Die vier Einträge der Reihe 3 sind derselbe Engpass von vier Seiten** und werden nicht einzeln bewertet — wer einen angeht, misst die anderen drei mit. Ihre Reihenfolge untereinander steht bei `AUFTRAGSARTEN-OHNE-AGENTEN`.

### Was mit den übrigen 171 ist

**Sie sind nicht C oder D — sie sind ungebändert**, und das ist eine ehrliche Angabe und keine Auslassung. Ein Band im Sinne von Regel 2 entsteht durch Vergleich; 166 Einträge in einem Zug zu bebändern hieße, genau das Verfahren zu wiederholen, gegen das dieser Abschnitt geschrieben ist.

**Die Reihenfolge für den nächsten Durchgang:** Zuerst die Bugs mit `🔧 offen`, die eine heute berichtete Zahl tragen — das ist Band C und die einzige Gruppe, bei der Liegenlassen weiterläuft statt nur zu warten.

---

## Block 19.08.2026 — die Rollen eines Wissen-Silos

**Der Anlass ist eine Matrix, keine Wunschliste.** Am 19.08.2026 gezählt trägt von neun Silos **genau eines alle drei Rollen** (Timeline: Quelle, Zettel, Werkzeug). Das Web ist der Spiegelfall — Werkzeug ohne Quelle, weil es keine sein kann. Und das am schlechtesten angebundene Silo ist ihr **eigenes erarbeitetes Wissen**: eine Rolle von dreien.

| Kennung | Was offen ist | Band |
|---|---|---|
| ~~`WISSEN-OHNE-ZETTEL`~~ **— geschlossen am 19.08.2026.** Zettel (`plugins/wissen_manager/manager.py::router_prompt`) und Dienst (`agents/wissen/`) stehen, 26 Zeugen; **zwei echte Turns** routen dorthin (12:41 und 12:43 UTC), einer in den vierten Ausgang, einer abgeschlossen. Die Abfrage ist **eine** für beide Eingänge (§6a.1, `AutonomousWissenRepository.suchen`); der Eingang wählt nur die Tiefe. **Als Rest benannt:** die Tiefe bleibt Stufe 1 — Thema und Zusammenfassung, nicht der Wortlaut (`WIS-8-STUFE-2`), und der Dienst sagt es in seiner `grenze`. **Und der vierte Ausgang hat im ersten Lauf einen Befund geliefert:** die Schwelle trennt an diesem Korpus nicht (siehe `WIS-SCHWELLE-MESSEN`). Ursprünglicher Wortlaut: **Ihre Bibliothek ist angebunden wie ihr Gedächtnis, nicht wie eine Quelle.** `wissen_manager` trägt `immer_aktiv` und **keinen** `router_prompt` — sie fließt bei jedem Turn in den Kontext, und niemand kann sie **bestellen**: weder der Mensch (*„Was hast du selbst dazu erarbeitet?"*) noch sie selbst. Für die freigegebenen Dateien wurde der Zettel am 18.08. gebaut, für ihr eigenes Wissen nicht. **Was fertig wäre:** ein Aushang nach `novaberg-convention-nmcp.md` §3 mit Negativfällen gegen **drei** Nachbarn — `dateien` (fremde Unterlagen), `kzg` (Erinnerung an ein Gespräch), `recherche` (was sie noch nicht weiß) —, ein Dienst dahinter, der den vierten Ausgang bedient, und ein echter Turn, der eine Frage nach ihrem eigenen Wissen dorthin routet. **Vorbedingung erfüllt:** §6a der Konvention steht seit dem 19.08. und ist vor diesem Bau geschrieben. | ungebändigt |
| `SILO-OHNE-WERKZEUG` | **Sechs Silos sind bestellbar und keines davon greifbar.** Sie kann `web_search`, `web_fetch`, `memory_search`, `timeline_check` und `timeline_search` mitten im Denken ziehen — für Dateien, ihr Wissen, Notizen, Fakten, Direktiven und Identität gibt es kein Werkzeug. **Der Unterschied ist nicht Bequemlichkeit, sondern wer entscheidet:** Bestellbar heißt, der Empfang wählt anhand der Äußerung; greifbar heißt, sie beschließt es selbst. **Was fertig wäre:** je Silo ein Werkzeug **oder** eine Begründung an seinem Aushang, warum es keines gibt — die Regeln dafür stehen in §6a.1 bis §6a.3, insbesondere die benannte Faltung der vier Ausgänge in Text. **Reihenfolge:** `wissen` und `dateien` zuerst, weil sie die Quellen einer ausdrücklichen Suche sind. | ungebändigt |
| `ROLLENMATRIX-OHNE-PRUEFUNG` | ⚠ **Neu bewertet am 19.08.2026 — das in §9 genannte Kriterium ist falsch, und wer die Prüfung wie beschrieben baut, zählt schweigend daneben.** §9 nennt `immer_aktiv` für die Rolle *Quelle*. Der Enricher ruft `enrich_entries` aber bei **jedem** Manager (`graph/nodes/enricher.py`), gleich was `immer_aktiv` sagt — die Eigenschaft steuert den **Schreibpfad** (`BaseManager`: *„False = nur bei pending_writes"*). Maschinell gezählt über 10 Silos: **§9 ergibt 3 Quellen, der Enricher 4**, und die beiden gehen bei **zwei** Silos auseinander — `kzg` (`immer_aktiv`, kein eigenes `enrich_entries`; sein Beitrag ist im Dispatcher-Knoten verdrahtet) und `timeline` (kein `immer_aktiv`, eigenes `enrich_entries`). **Ausgerechnet `timeline` ist der einzige Silo mit allen drei Rollen** — nach §9 hätte die Prüfung ihn als 2/3 gemeldet. Vor dem Bau ist deshalb §9 zu berichtigen. Dazu ein dritter Zustand, den die Matrix heute nicht kennt: `fakten` hat ein eigenes `enrich_entries` und ist im Enricher **abgeschaltet** — mit `continue` uebersprungen, begruendet im Code mit *„produziert 130+ Rausch-Eintraege"* — gebaut und stillgelegt ist weder *ja* noch *nein*. Ursprünglicher Wortlaut: **Die Matrix ist maschinell prüfbar und wird heute von Hand gezählt.** `novaberg-convention-nmcp.md` §9 führt sie als Startprüfung: je Silo die drei Rollen zählen — Quelle über `immer_aktiv`, Zettel über `router_prompt`, Werkzeug über den Werkzeugkasten des Denkknotens — und **jede leere Zelle ohne Begründung am Silo melden**. **Meldung, keine Verweigerung:** Eine fehlende Rolle kann richtig sein (das Gedächtnis hat zu Recht keinen Zettel), aber nicht unbemerkt. **Was fertig wäre:** die Prüfung im Handshake, ihre Ausgabe im Startlog, und der Nachweis an einem hergestellten Fall — ein Silo, dem man den Zettel wegnimmt, muss gemeldet werden. Ohne diesen Auslösefall ist ein schweigender Scan von einem sauberen Bestand nicht zu unterscheiden. | ungebändigt |
| `RECHERCHE-LIEST-IHRE-BIBLIOTHEK-NICHT` | **Der Recherche-Agent schreibt in `autonomous_wissen` und liest nie daraus.** `suche_ausfuehren` ist SearXNG plus Seitenabruf — eine Quelle. Das Vorwissen, gegen das er plant, kommt aus **LZG und KZG** (`kontext_paket_bauen`), und die Planungsregel sagt ausdrücklich *„Nur Lücken benennen, die durch **Web-Suche** füllbar sind"*. **Er füllt eine Bibliothek, die er selbst nicht befragt** — und kann damit dasselbe Thema mehrfach neu recherchieren, ohne es zu merken. **Was fertig wäre:** Die Lagebeurteilung fragt vor der Web-Suche den `wissen`-Dienst (nicht eine zweite Suche über denselben Bestand — §6a.1), und die Messung ist eine Zahl: **wie viele der nächsten N Aufträge finden eigenes Vorwissen?** ~~**Hängt an `WISSEN-OHNE-ZETTEL`**~~ → **entblockt am 19.08.2026:** Der Dienst existiert und ist aus **beiden** Graphen erreichbar (`graph_eignung = ["user", "pixie"]`). **Vorher zu klären ist die Schwelle**, nicht die Anbindung: An acht gemessenen Fragen weist 0,40 den sachlich richtigen Treffer ab (0,3054) und lässt einen unpassenden durch (0,4700) — eine Lagebeurteilung, die so fragt, bekäme systematisch *„kenne ich nicht"*. Siehe `WIS-SCHWELLE-MESSEN`. | ungebändigt |

---

## Block 19.08.2026 — der dritte Konsument der Bibliothek

| Kennung | Was offen ist | Band |
|---|---|---|
| ~~`WIS-ENRICHER-UNGEMESSEN`~~ | **✅ Nachgemessen am 19.08.2026 — der Weg ist besser geworden, nicht schlechter: 22/30 auf Rang 1 gegen 1/30, im Betrieb 3 Treffer bei Kosinus 0,730–0,629.** Ursprünglicher Befund: **Der Enricher-Weg wurde auf Themenvektoren und Schwelle 0,50 mitgestellt, ohne dass seine Anfrageart je gemessen wurde.** Er fragt mit dem **Gesprächsvektor** (`verschiebung.vektor`), nicht mit einer Frage und nicht mit einem Kontexttext — eine dritte Größe. Beide neuen Einstellungen sind an der **Frage**-Anfrage kalibriert. Aus dem Betriebslog über rund 32 Stunden vor dem Umbau: 5 Treffer bei Kosinus 0,402 bis 0,555; der erste Turn danach lieferte null. **Was fertig wäre:** dieselbe Methode wie an den anderen beiden Zugriffen — echte Gesprächsvektoren aus dem Betrieb, bekannte richtige Antwort, Anteil auf Rang 1, gegen beide Ziele. Erst danach ist entscheidbar, ob dieser Weg eine eigene Schwelle braucht oder ein eigenes Ziel. **Nicht im Vorbeigehen ändern:** Eine dritte Schwelle ohne Messung wäre genau der Fehler, den die Messung an den ersten beiden gerade verhindert hat.

**Ergebnis:** Eine eigene Schwelle braucht dieser Weg **nicht** — die Verschiebung kostet bei dieser Art Frage 0,0000, weil kein Ziel aktiviert wird (stärkstes von 7: `similarity × motivation` = 0,3903 × 0,8 = 0,312, unter der Aktivierungsschwelle). Er verhält sich damit wie die Bestellung, für die 0,50 kalibriert ist. **Was offen bleibt:** Ob bei Äußerungen, die Novas Ziele *doch* aktivieren, ein Verlust entsteht — das ist eine andere Frage und braucht andere Fragen. | ungebändigt |

---

## Block 19.08.2026 — ein Vektor je Gegenstand

**Entschieden am 19.08.2026, festgehalten als Konvention 4** (`novaberg-convention-embedding.md` §5): Ein Vektor repräsentiert genau einen Gegenstand. Über sieben Vektorspalten gezählt folgen **fünf** der Regel, bevor sie geschrieben war — sie ist die Hausform. Zwei weichen ab, und es sind die jüngsten Speicher.

| Kennung | Was offen ist | Band |
|---|---|---|
| `BIBLIOTHEK-BLIND-AUF-INHALTSHOEHE` | **Die Bibliothek ist auf Themenhöhe abrufbar und auf Inhaltshöhe blind — und der Enricher fragt immer auf Inhaltshöhe.** Gemessen am 20.08.2026 gegen 287 Ausarbeitungen: 10 Sonden, aus dem **Dateiinhalt** formuliert, treffen ihr Ziel in **1 von 10** Fällen auf Rang 1; die Schwelle 0,50 schneidet **9 von 10** ab. Die Kontrolle stellt die Diagnose — dieselbe Zielausarbeitung, zweimal gefragt: auf Themenhöhe Rang 1 bei Kosinus 0,7375 / 0,5751 / 0,5559, auf Inhaltshöhe Rang 8 / 142 / 63 bei 0,3447 / 0,1768 / 0,2491. **Nicht die Schwelle ist falsch, sondern ihre Paarung:** Kalibriert wurde sie am 19.08. an Themenfragen (92 % Rang 1) — der bestellbare Weg. Der Enricher sucht mit dem Vektor des **Turns**, und ein Turn ist fast immer eine inhaltliche Äußerung. **Das erklärt den Betrieb:** 2 echte Treffer in 142 beantworteten Nutzerturns. **Ausdrücklich nicht mitzumachen:** an der Zahl drehen. Sie hält die fremden Fragen sauber draußen (0 von 10 durchgelassen), und die Verteilungen überlappen — der beste Fremdtreffer 0,3577 liegt über fünf der zehn Ziele; keine Zahl trennt beide Seiten. **Was fertig wäre:** ein Vergleichsgegenstand auf Inhaltshöhe — Zusammenfassung oder Inhaltsblöcke auffindbar gemacht — und dieselben 20 Sonden erneut gefahren. **Nulllinie: Rang 1 in 1 von 10, fremd max 0,3577.** **Vor dem Bau zu bedenken:** Der Gegenbefund vom selben Tag steht — `MAX` über viele Vektoren je Eintrag hebt auch das Rauschen (`EMBED-LISTE-DATEIENINDEX`, gemessen und verworfen). Messschrieb: `2026-08-20_bibliotheksschwelle_ergebnis.md` | ungebändigt |
| `EMBED-LISTE-AUTONOMES-WISSEN` | **Die Bibliothek bettet eine Themenliste als einen Vektor ein — und trifft damit nicht.** `autonomous_wissen.thema` trägt Ø **4,37** Themen je Feld (max 17), **558 von 559** Feldern mehr als eins. Zusätzlich stammt der Vektor gar nicht aus diesem Feld, sondern aus dem **Destillat** (`agents/recherche/agent.py`, siehe Fundliste). **Gemessen:** Bei einer Frage nach *einem* Thema liegt die richtige Antwort in **6 von 40** Fällen auf Rang 1, Kosinus-Median **0,2821** — unterhalb der eigenen Schwelle von 0,40, die Antwort wird also im Regelfall verworfen. Mit einem Vektor je Thema: 31 von 40 und Median 0,7425. **Was fertig wäre:** je Thema eine Zeile mit eigenem Vektor, die Lesepfade von `AutonomousWissenRepository.suchen` darauf umgestellt, und ein echter Turn, der eine Ausarbeitung über ein einzelnes ihrer Themen findet. **Nicht vergessen:** Der Rückweg fragt mit Ø 713 Zeichen (n=924) und braucht daneben weiterhin ein Ziel seiner Größenordnung — ein Themenvektor ersetzt keinen Inhaltsvektor. **Ist DDL und eine Migration von 249 Zeilen** (`F-DDL-1`) | ungebändigt |
| `EMBED-LISTE-DATEIENINDEX` | **Dritte Stelle derselben Klasse, und diesmal ist die Wirkung gemessen.** `embed_text_bauen` (`agents/dateien_index/indizieren.py`) bildet `themen_embedding` aus `thema` **plus rund acht Stichwörtern** — ein Schwerpunkt aus neun Gegenständen, wo gesucht wird nach **einem**. **Gemessen am 20.08.2026 über 24 Sonden gegen 174 Zeilen:** richtige Datei auf Rang 1 in **8 von 12**, in den ersten drei in 10 von 12. Der teure Fall ist der Rest: Die Sonde nach der Nabe des Charakter-Rads trifft ihr Ziel mit 0,3381 — **über** dem Boden — und bekommt es nie zu sehen, weil drei thematisch benachbarte Dateien davor liegen (0,5001 · 0,4495 · 0,3857) und die Kappung bei drei steht. Der scharfe Kanal fängt es nicht auf. **Keine Schwelle ändert daran etwas** — das ist der Unterschied zwischen einer Rangfolge- und einer Schwellenfrage, und er ist an dieser Messung ablesbar. **Der Präzedenzfall ist bezahlt:** Dieselbe Bauart hob an der Bibliothek den Anteil richtiger Antworten auf Rang 1 von 15 % auf 92 % (Konvention 4, `F-EMBED-2`). **Was fertig wäre:** ein Vektor je Stichwort/Thema in eigener Zeile, beide Schreibwege angeschlossen, und dieselben 24 Sonden erneut gefahren — die Rang-1-Quote von 8/12 ist die Nulllinie, gegen die zu messen ist. → ⊘ **Am 20.08.2026 gebaut, gemessen und zurückgebaut.** Tabelle, Schreibweg, drei Lesewege und 1456 nachgebettete Gegenstandsvektoren über 174 Zeilen standen; dieselben 24 Sonden ergaben **keine Verbesserung**: Rang 1 unverändert 8/12, in den ersten drei **9/12 statt 10/12**, und die Trennung wird schlechter — der beste Fremdtreffer steigt von 0,3052 auf 0,4008, über dem Boden liegen statt 1 Zeile **20**. Ein dritter Arm (nur der Themensatz, ohne Stichwörter) trennt die beiden Änderungen und liegt gleichauf mit dem zweiten: 8/12 und 9/12. **Warum der Präzedenzfall nicht trägt:** In der Bibliothek war das Feld eine Aufzählung *verschiedener* Gegenstände; hier beschreiben Thema und Stichwörter **einen** — die Datei. Ein Schwerpunkt aus Facetten eines Dings zeigt weiterhin auf dieses Ding. Und MAX über 1456 Vektoren ist eine Extremwertstatistik: Zur Sonde nach der Nabe des Charakter-Rads trug das Stichwort `CharacterGraph` den besten Treffer. **`F-EMBED-2` ist damit nicht widerlegt, die Analogie ist es** — dieser Fall ist weder Aufzählung noch Aussage, sondern die Beschreibung **eines** Gegenstands aus mehreren Blickwinkeln. Messschrieb: `2026-08-20_gegenstandsvektoren_ergebnis.md`. ~~**Was offen bleibt und jetzt ohne Kandidaten dasteht:** warum die richtige Datei nur in 8 von 12 Fällen auf Rang 1 steht~~ → **Am 21.08.2026 diagnostiziert, und die Antwort liegt nicht an der Formel.** Ein zweiter Kandidat wurde dabei verbraucht: Die **Präambel** des Themensatzes (66 von 174 Sätzen beginnen mit einer) ist entfernt worden — Rang 1 bleibt 8/12, Top 3 bleibt 10/12, die drei Fehlschläge bewegen sich um je einen Platz. **Zwei der vier Fehlschläge sind Sollurteil-Fehler:** Bei der Frage nach dem Verfall eines Kurzzeit-Eintrags steht `kzg-salienz.md` über dem Ziel, und ihr Themensatz beschreibt genau das Gefragte; bei der Frage nach der Führung im Gespräch steht das Moduldokument über seinem Konzept. Der Bestand führt zu mehreren Fragen **mehr als eine richtige Datei**, und die Sonde erklärt genau eine dazu. **Bei den zwei echten Fehlschlägen kommt der tragende Begriff der Frage im Index nicht vor:** `Nabe` steht 2× in der Datei und weder im Themensatz noch in den Stichwörtern, `Führung` 6× in der Datei und in den Stichwörtern nur als Bezeichner `fuehrung_messen`. **Der Index trägt neun Gegenstände je Datei; was nicht hineinfällt, ist für beide Kanäle unsichtbar** — und keine Änderung an der Form des Vektors heilt das. **Vor jedem Bau gemessen:** Der beste *Block* der Zieldatei erreicht 0,4617 gegen 0,3381 und 0,3926 gegen 0,2189. Das belegt Kopf, nicht Erfolg — bei einer Blockebene stiegen auch die Konkurrenten, und genau daran ist der Umbau vom 20.08. gescheitert. Messschrieb: `2026-08-21_dateiindex_rangfolge_ergebnis.md`. | ⊘ verworfen, Ursache diagnostiziert |
| `EMBED-LISTE-DELEGATIONSAKTEN` | **Derselbe Verstoß am größeren Bestand, ungemessen.** `delegations_akten.themen` trägt Ø **2,76** Gegenstände je Feld, **1510 von 1586** mehr als eins — Beispiele: *„Mut, Vertrauen"*, *„aktuelle Lebenssituation, Prozess des Aufbaus"*. Gelesen wird die Spalte von `agents/delegation/deduplizierung.py`. **Ausdrücklich nicht gemessen:** ob die Deduplizierung heute danebengreift. Der Verstoß gegen Konvention 4 steht fest, seine Wirkung nicht — und die Wirkung entscheidet, ob der Umbau lohnt. **Was fertig wäre:** dieselbe Messung wie an der Bibliothek (bekannte richtige Antwort, Anteil auf Rang 1), *bevor* etwas umgebaut wird | ungebändigt |
| `EMBED-RUECKWEG-UNGEMESSEN` | **Der zweite Konsument der Bibliotheksspalte ist nie gemessen worden.** `agents/wissen_rueckweg/zuordnung.kandidaten_laden` vergleicht `auftrag['kontext']` gegen `themen_embedding` — Ø **713** Zeichen Anfrage (n=924, min 28, max 3309) gegen ein Ziel von Ø 552. Die Längen passen; **ob er trifft, ist unbekannt.** **Warum das vor dem Umbau zählt:** Wer die Spalte auf Themen umstellt, stellt den Rückweg von einem passenden Ziel auf ein fünfmal kürzeres um — und würde eine Seite reparieren und die andere brechen, ohne es zu merken. ~~**Was fertig wäre:** beide Zugriffe gegen beide Ziele, vier Zellen, dieselbe Methode~~ — **gemessen am 19.08.2026, und das Ergebnis kehrt die Empfehlung für diesen Zugriff um.**

| | bester Kosinus (median) | Spreizung Rang 1 → 8 |
|---|---|---|
| Ziel Destillat (heute) | **0,5530** | 0,0664 |
| Ziel Themenvektoren | 0,4601 | 0,0718 |

**Die Kandidatenlisten sind fast disjunkt: Überlappung der Top-8 im Median 1 von 8** (min 0, max 3). Eine Umstellung tauscht also sieben von acht Kandidaten aus — es ist keine Verbesserung derselben Suche, sondern eine andere Suche.

**Mit Ground Truth** (die Zusammenfassung eines Eintrags als Anfrage, gesucht wird sein eigener Eintrag): Destillat **25/25 Recall@8**, Themenvektoren **12/25**. **Die Grenze ist ausdrücklich zu nennen:** Die Zusammenfassung ist ein Ausschnitt des Textes, aus dem das Destillat-Embedding gebaut wurde — die 100 % sind trivial günstig und keine Aussage über den Betrieb. Belastbar ist die Richtung, nicht der Abstand.

> **Damit ist belegt, was vorher nur ein Vorbehalt war: Ein Vektor je Thema ersetzt keinen Inhaltsvektor.** Wer allein umstellt, hebt die Bestellung von 15 % auf 78 % und senkt den Rückweg von 25/25 auf 12/25. **Beide Ziele werden gebraucht.**

**Ein dritter Befund fiel dabei an und gehört keinem der beiden Ziele:** Die Spreizung zwischen Rang 1 und Rang 8 liegt bei **0,066 bzw. 0,072** — die acht Kandidaten liegen dicht beieinander. Der Vektor wählt also kaum vor; das Modell in `ziel_bestimmen` entscheidet fast blind. Eigener Eintrag, siehe Fundliste. | ungebändigt |

---

## Block 19.08.2026 — der Antwortpfad meldet seinen Verlust und behebt ihn nicht

| Kennung | Was offen ist | Band |
|---|---|---|
| `ANTWORT-LEER-OHNE-WIEDERHOLUNG` | **Der Leer-Ausfall ist seit dem 19.08.2026 vollständig sichtbar und wird weiterhin nicht behandelt.** Liefert der Anbieter null Zeichen, läuft der Turn zu Ende: Tribunal mit drei Modellaufrufen (gemessen 6,8 s) und die Antwort-Perzeption arbeiten über ein Nichts, danach wird nichts zugestellt. **Der Verfasser-Inhalt liegt zu diesem Zeitpunkt vor** — im gemessenen Fall 300 Zeichen —, der Aufruf ist also wiederholbar, ohne irgendetwas neu zu rechnen. **Was fertig wäre:** ein Wiederholversuch im Responder bei `text_len == 0`, mit Obergrenze und eigener Protokollzeile; scheitert auch er, geht der Turn in einen benannten Ausgang statt in Schweigen. **Zu entscheiden ist die Absicht, nicht die Umsetzung:** Ein zweiter Aufruf kostet Zeit auf dem seriellen Platz und kann eine **andere** Antwort liefern als die, die das Tribunal später bewertet — wer wiederholt, muss sagen, ab welcher Stufe neu gelaufen wird. **Hängt nicht an der Ursache:** Warum die Token verschwinden, ist unbekannt und muss es für diese Abhilfe auch bleiben. **Neu bewertet am 19.08.2026:** Der externe Kandidat ist abgearbeitet — die Laufzeit läuft auf 0.32.14, und der Ausfall ist damit **nicht** erklärt. Die Nachmessung trägt keine Aussage dazu (n=1 bis 5 je Aufrufer gegen n=30 bis 224 der Nulllinie), der `thinker`-Median steht bei 12 Zeichen wie zuvor. **Damit fällt das Warten auf das Update als Grund weg, diesen Eintrag zurückzustellen** — die Entscheidung *ab welcher Stufe neu gelaufen wird* steht unverändert aus und ist jetzt das einzige, was fehlt. | ungebändigt |
| ~~`OLLAMA-VERSION-VIER-MONATE-ALT`~~ | **✅ Erledigt am 19.08.2026 — 0.32.14 läuft.** Ursprünglicher Befund: **Die Laufzeit ist zwölf Minor-Versionen alt, und vier Release-Einträge treffen die Kombination, die in jedem Gesprächsknoten läuft.** Installiert ist **0.20.7** (Binärdatei vom 14.04.2026), verfügbar **v0.32.14** (15.08.2026). Einschlägig: v0.21.1 *„Fixed structured outputs for Gemma 4 when `think=false`"* (22.04. — **acht Tage nach der installierten Fassung**), v0.22.1 *„Updated the Gemma 4 **renderer**"*, v0.30.9 *„Fixed LFM2 **parser/render** for cases where thinking was not emitted"*, v0.31.2 *„Fixed structured output for thinking models when thinking is disabled"*. Dazu v0.32.3 *„Fixed GLM tool calls being **silently dropped** at the end of generation"* — dieselbe Fehlerklasse wie `RESPONDER-LEERE-ANTWORT-STILL`. **Alle 14 JSON-erwartenden Aufrufer laufen mit `think=False`.** **Einschränkung, gemessen:** Der Bestand sendet **kein** `format`-Feld; „structured outputs" meint bei Ollama genau das, `expect_json` parst clientseitig. v0.21.1 trifft den Pfad also nicht so, wie der Eintrag ihn beschreibt — Renderer und Parser bleiben einschlägig. **Was fertig wäre:** Update eingespielt, beide Dienste neu gestartet, die selbstgebauten Modelfiles laden, und dieselbe Erhebung wie vorher gelaufen. **Die Nulllinie ist erhoben** (31 h Betrieb, 319.267 Zeilen): JSON-Quoten 2,2 % / 2,7 % / 1,6 %, vier Leerantworten, 150× `done_reason='stop'`, belegte Kanäle ausschließlich `['content']`, Antwortlängen-Mediane je Aufrufer. **Zu entscheiden, nicht zu bauen:** ob das Modellverzeichnis (42 GB) vorher gesichert wird — neuere Fassungen schreiben gelegentlich das Manifest-Format um, und dann ist der Rückweg auf die alte Binärdatei nicht sauber. ~~**Der Rückweg sonst:** ein `cp` und zwei Neustarts~~ — **beim Ausführen widerlegt.** **Erledigt am 19.08.2026: 0.32.14 läuft auf beiden Instanzen.** Suite `Ran 1965 tests — OK`, echter Turn zugestellt, alle fünf Modelle mit **unveränderten Digests** — das Manifest-Format wurde nicht umgeschrieben, die 42-GB-Frage ist damit im Nachhinein beantwortet. Gesichert wurde trotzdem, und anders als geplant: Manifeste als echte Kopie (20 KB), **Blobs als harte Links** (42 GB zu null Platz, Linkzahl 2 geprüft). **Zwei Angaben dieses Eintrags trugen nicht:** Der Rückweg ist nicht *ein `cp`* — neben der 43-MB-Binärdatei liegen **7,2 GB Laufzeitbibliotheken** in `/usr/local/lib/ollama`, die dasselbe Archiv ersetzt, und eine alte Binärdatei gegen neue Runner ist keine ausgelieferte Kombination. Und die Nulllinie ist **nicht** unverändert wiederholbar: Das Log des Server-Containers ist kumulativ, 129 neue Zeilen gegen 325.987. Die Erhebung braucht deshalb ein **absolutes** Zeitfenster mit Zonenkennung; ein relatives greift auf den vorigen Lauf über. **Was der Wechsel nicht bringt:** Er erklärt `RESPONDER-LEERE-ANTWORT-STILL` nicht — dazu siehe dort. | ungebändigt |
| `ANBIETER-FELDER-UNGELESEN` | **Der Anbieter liefert zwölf Felder, der Bestand liest drei.** Gezählt am 19.08.2026 aus der Schlüsselliste einer echten Antwort: `created_at`, `done`, `done_reason`, `eval_count`, `eval_duration`, `load_duration`, `logprobs`, `message`, `model`, `prompt_eval_count`, `prompt_eval_duration`, `total_duration`. Gelesen wurden `prompt_eval_count`, `eval_count` und `message`; seit dem 19.08. steht der ganze Umschlag im Protokoll, **verarbeitet** wird weiterhin nichts davon. **Der Verlust ist nicht theoretisch:** `done_reason` hätte einen offenen Defekt aufklären können und war vier Wochen lang da. **Was fertig wäre:** je Feld eine Entscheidung — gelesen und wohin, oder begründet verworfen. Die Dauern (`eval_duration`, `load_duration`, `total_duration`) sind dabei der billigste Gewinn: Sie trennen Wartezeit am Modell von Wartezeit im Graphen, und diese Trennung wird heute aus Zeitstempeln erschlossen. | ungebändigt |

---

## Block 16.08.2026 — die Gegenrichtung der Doku-Pruefung

| Kennung | Was offen ist | Band |
|---|---|---|
| `KANAL-OHNE-GEGENSTUECK` | **Das vierte Kriterium: nicht vom Dokument zum Code, sondern vom Code zum Leser.** Die drei Kriterien vom 16.08.2026 prüfen, ob ein im Dokument genannter Name einen Gegenstand im Code hat. Sie können die umgekehrte Klasse **prinzipiell nicht finden**: ein Bauteil, das gebaut ist und das niemand liest. **Der Zuschnitt ist mechanisch:** je State-Kanal und je persistiertem Feld die Menge der **Schreiber** und die Menge der **Leser** aus dem Baum ableiten; ausgegeben wird, wie viele nur eine Seite haben. Ein Kanal mit Schreibern und ohne Leser ist tote Rechenarbeit, einer mit Lesern und ohne Schreiber ein Vorgabewert, der wie eine Messung aussieht. **Die Klasse ist belegt, nicht vermutet:** `einwandsurteil` steht als Kanal ohne Leser in der Fundliste; am 15.08.2026 fand die zweite Kontrolle einen Router, der einen neu eingeführten Wert nur **verglich**, worauf kein einziger Auftrag mehr lief — bei 1404 grünen Tests; und am selben Tag einen zweiten Erzeuger desselben Payload-Feldes, dessen Ausfall sich als korrekte Meldung getarnt hätte. **Was es zusätzlich fände:** die Nähte zwischen Modulen — nicht ob eine Funktion existiert, sondern ob das, was sie schreibt, hinten ankommt. | ungebändigt |
| `SELBSTAUSKUNFT-OHNE-LESER` | **Das erste Fundstück der Klasse, die `KANAL-OHNE-GEGENSTUECK` beschreibt — von Hand gefunden, nicht vom Werkzeug.** Jeder Agent beschreibt sich selbst: `faehigkeiten`, `AGENT.md`, `typ`, `graph_eignung`, `lastart`, `context_user`. `AgentRegistry.beschreibungen()` fügt das zu einem Text zusammen, dessen Docstring den Zweck nennt — *„für den Planner-Prompt"*. **Gemessen am 16.08.2026: 14 von 14 Agenten deklarieren `faehigkeiten`, 12 von 14 tragen ein `AGENT.md`, und `beschreibungen()` hat im Produktivcode null Aufrufer.** Die erzeugende Seite ist vollzählig gepflegt, die lesende fehlt ganz. **Was stattdessen entscheidet:** `planner.plan()` sucht den Zuständigen über Zeichenketten-Abgleich auf `router_intents`, `manager.ziel` und `management_target` — also über die zentrale Zuordnung, die `novaberg-convention-planner-needs.md` §1 als Bruch des Plugin-Prinzips (E7) benennt. Ein neuer Agent kann lückenlos deklarieren, was er kann, und wird nur gefunden, wenn sein Name zum Abgleich passt. **Der billigste Weg ist ein dritter, und er stand von Anfang an daneben:** Die **Manager** haben seit Chat 5 genau diesen Mechanismus, und er lebt — `router_prompt`, von `get_combined_router_prompt()` eingesammelt und in `graph/nodes/router.py:62` als `[AGENTEN]`-Block in den System-Prompt gesetzt. Die Agenten bekommen dieselbe Eigenschaft; Aggregator, Leser und Prompt-Block existieren bereits. **Und der Vergleich beider Deklarationen erklärt, warum die eine überlebte und die andere nicht:** `["termin_erstellen", "termin_lesen"]` ist eine Auskunft in der Sprache des **Anbieters**; *„Entscheidend ist NICHT die Satzform, sondern ob der Prompt ein Datum enthält"* ist eine Anweisung in der Sprache des **Aufrufers**. Nur die zweite ist benutzbar, und nur die zweite hat je einen Leser gefunden. Die Manager-Fassung trägt zusätzlich **Negativregeln** (*„NICHT triggern bei emotionalen Ausdrücken"*), die in keiner Fähigkeitenliste ausdrückbar sind. **Erster Schritt ist aber nicht der Bau, sondern eine Gegenprobe** — und der Grund ist gemessen: **`delegation` deklariert `graph_eignung = ["user"]` und läuft über den Hintergrund-Router** (`services/pixie/router.py`, Sonderfall `aufgabe == "delegation"`); auf dem Nutzerpfad ist der Agent nicht wählbar, weil kein Manager dieses Ziel trägt. Dreizehn Deklarationen stimmen, diese eine nicht — und **niemand konnte es merken, weil kein Lauf sie prüft.** Wer den Leser zuerst baut, schaltet eine nie gegengeprüfte Datenbasis scharf: `fuer_graph("user")` nähme `delegation` auf, `fuer_graph("pixie")` ließe ihn weg, beides verkehrt herum. **Also erst alle 14 Deklarationen gegen den tatsächlichen Aufrufweg halten, dann anschließen.** → **Am 16.08.2026 durchgeführt, und das Ergebnis ändert den Zuschnitt.** Zwölf von vierzehn stimmen. Zwei nicht, und sie sind **nicht dieselbe Art Fehler**: `delegation` ist schlicht falsch (`["user"]` deklariert, über den Hintergrund-Router erreicht). `kzg` deklariert `["user"]`, **und die Frage trifft ihn gar nicht** — sein produktiver Aufruf ist fest im `dispatcher`-Knoten verdrahtet und läuft in allen drei Graphen, einschließlich des AgentGraph, den `shadow_delivery` im Hintergrund treibt; der *wählbare* Pfad über `plugins/kzg_manager` führt sich im eigenen Docstring als Legacy. **Daraus der strukturelle Befund:** Es gibt **drei** Aufrufarten — vom Planner gewählt, aus der Pixie-Queue gezogen, fest in einem Knoten verdrahtet — und `graph_eignung` hat nur für die erste eine Bedeutung. Ein Feld, das alle vierzehn Agenten füllen, ist für einen Teil von ihnen **sinnlos statt falsch**, und das ist der schwerer zu findende Zustand. Wer den Leser baut, klärt zuerst, für welche Aufrufart die Selbstauskunft überhaupt gilt. Zwei erklärbare Randfälle sind geprüft und in Ordnung: `recherche` hat kein `periodic_task`, weil es queue-basiert läuft, und `ziel_decay` steht nicht im Pixie-Router, weil es rein periodisch läuft. **Was fertig wäre:** die 14 geprüften Deklarationen mit Zahl der Korrekturen, dazu eine `router_prompt`-Eigenschaft an `BaseAgent`, von mindestens den fünf über den Planner erreichbaren Agenten gefüllt, im `[AGENTEN]`-Block sichtbar, und an einem echten Turn gemessen. Verworfen wäre damit der ursprünglich naheliegende Weg, `beschreibungen()` einen Leser zu geben — er transportierte die falsche Gattung Text. **Alternativ**, wenn die Selbstauskunft nicht gebraucht wird: begründete Streichung der fünf ungelesenen Felder samt Nachzug in `novaberg-agent-*.md`. **Nicht mitgemacht:** die Vorbedingungs-Auflösung zur Laufzeit — die ist am 16.08.2026 verworfen und liegt unter `archive/`. | ungebändigt |
| `NAMENSREGELN-JENSEITS-DER-FORM` | **Die harte `N`-Familie deckt die Namens*form* ab, nicht die Namens*wahl*.** `ruff --select N` läuft am 16.08.2026 sauber über `server/` — snake_case, CamelCase, keine Builtin-Schatten. Ungeprüft bleibt, was darüber hinaus gilt: die Sprachtrennung zwischen Code und Log, die Behandlung feststehender Fachbegriffe der Domäne, und die Regel, dass eine Zeichenkette als Statuswert oder Klassifikationslabel eine geschlossene Aufzählung braucht. **Für die letzte gibt es einen Ansatz:** Zeichenketten-Literale, die in einem Vergleich gegen ein Statusfeld stehen, sind auffindbar — und eine, die in keiner Aufzählung vorkommt, ist der Kandidat. **Nicht mitgemacht:** Die beiden ersten Regeln sind vermutlich nicht mechanisch prüfbar; das gehört dann als Grenze benannt statt als Aufgabe geführt. | ungebändigt |

---

## Block 16.08.2026 — aus dem Halten der Konventionen

| Kennung | Was offen ist | Band |
|---|---|---|
| `PENDING-AGENT-INS-PAYLOAD` | **`novaberg-convention-event-model.md` §9.3 beschreibt eine Migration, die nicht stattgefunden hat.** Der Wartezustand eines Agenten sollte vom Redis-Schlüssel `pending_agent:{user_id}` ins Event-Payload wandern; das Ereignis `awaiting_user` trüge den Kontext, das nächste Nutzer-Ereignis löste den Resume aus. **Der Schlüssel ist weiterhin der Träger und tief verdrahtet:** acht Dateien lesen oder setzen ihn — `graph/nodes/planner.py`, `graph/nodes/router.py`, `services/event_consumer.py`, `services/shadow_delivery.py` und die Dispatches von vier Agenten. **Der Satz stand im Präsens** und las sich wie eine Beschreibung; er ist im Dokument jetzt als Absicht markiert. Was ihn wichtig macht: Der Schlüssel ist paar-blind (`{user_id}` ohne `character_id`) und überdauert den Turn, während das Payload beides mitbrächte. | ungebändigt |
| `SSE-REST-IM-ENDPUNKT` | **Schritt 7 der Migration ist als erledigt vermerkt, der Server-Pfad daneben nicht.** *Client auf WebSocket-only umstellen* ✅ (01.08.2026) — aber `api/chat.py` liefert weiterhin eine `StreamingResponse` mit `media_type="text/event-stream"`. Damit steht ein zweiter Ausgabeweg neben dem WebSocket, den niemand mehr benutzt und den auch niemand prüft. Schritt 8 der Migration nennt ihn (*Aufräumen: nachbearbeitung.py, SSE, Annotate-Funktionen*); die beiden anderen Teile sind erledigt. | ungebändigt |

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
| `FACHSPEICHER-AGENTEN` | **Notizen, Fakten, Timeline, Dateien, Wissen bekommen je einen pflegenden Agenten.** Heute entstehen ihre Einträge, aber niemand hält sie instand. **Je Speicher ist zuerst die Rolle zu bestimmen** — Ziel eines Fremdschlüssels, Bindung oder freier Inhalt —, denn daran hängt, ob und wo ein Verfall überhaupt hingehört. Die Karte oben ist der Ausgangspunkt und keine Festlegung: Sie beschreibt den Bestand, nicht die Absicht. **Voraussetzung:** Gedächtnisschichten und Charakter-Destillation vollständig. | ungebändigt |
| `FAKTEN-BINDUNG-OHNE-VERFALL` | **`fakten` ist die Bindung zwischen zwei `entitaeten` und trägt keine Verfallsgröße.** Nach der Regel — Entität bleibt, Bindung darf verfallen — und nach dem Ort des Verfalls — im Fakten-Gedächtnis läuft die Suche über die Kanten — gehört er genau hierhin. Vorhanden sind `t_valid`, `t_invalid`, `last_touched`, `wiedervorlage_am`, `aktiv`: **Bi-Temporalität, kein Verfall.** Die beiden schließen einander nicht aus, sie beantworten verschiedene Fragen — *war das wahr* gegen *ist das noch wichtig*. Offen ist nur die zweite. `entitaeten` bleibt ausdrücklich unberührt: Fremdschlüssel zeigen darauf. | ungebändigt |
| `REEMBED-WISSENSSPEICHER` | **`tools/reembed_all.py` erfasst `autonomous_wissen.themen_embedding` nicht** — 390 von 390 Zeilen belegt. Der Speicher folgt der Form von `novaberg-convention-embedding.md` §2 (eigener benannter `embed_text_bauen`, aus der persistierten `zusammenfassung` rekonstruierbar), aber die Prüffrage der Konvention — *Kann reembed_all.py diesen Vektor allein neu erzeugen?* — ist für ihn mit **nein** zu beantworten. **Die Folge ist die, gegen die die Konvention gebaut ist:** Bei einem Modellwechsel bliebe die Wissens-Bibliothek im alten Vektorraum, während die sechs übrigen Speicher migrieren — ein zweiter Mischraum. **Der Zuschnitt ist klein:** ein Ziel im Werkzeug, das den vorhandenen Bauer importiert, wie die sieben anderen auch. Gefunden beim Halten der Konvention gegen den Code. | ungebändigt |

---

## Block 15.08.2026 — das Messinstrument der Zustellung

Beide Einträge sind die „zwei benannten Reste der Protokollpflicht" aus
`novaberg-eigenzeit_k.md` §2.5, hier mit einer Kennung versehen. **Sie haben am
15.08.2026 ihren Charakter geändert:** Solange die stündliche Decke stand, waren
sie eine Lücke in den Daten. Mit ihrem Fall ist der Burst-Zähler die einzige
verbliebene Wiederholungsgrenze — und damit sitzt die Lücke **genau an der
Grenze, die beobachtet werden soll.**

| Kennung | Was offen ist | Band |
|---|---|---|
| `ZUSTELLUNG-ABBRUCH-UNGEZAEHLT` | **Was vor dem Trigger abbricht, erzeugt keine Zeile** — offene Rückfrage, erschöpfter Burst, leerer Stapel, kein Trigger. Im ganzen Zustelldienst steht **eine** Schreibstelle (`_riegelkette_pruefen`), und sie liegt hinter dem Trigger; das Feld `umfang: ab_trigger` sagt es ehrlich, behebt es aber nicht. **Die Folge ist asymmetrisch und deshalb irreführend:** Der Burst erscheint als `ruhe: durchlaessig true` in jedem Eintrag, in dem er *nicht* geblockt hat — wie oft er **gestoppt** hat, steht nirgends. Eine Auswertung kann seine Durchlässe zählen und seine Blockaden nie. **Nicht naiv nachrüstbar:** Der Lauf tickt alle 5 s je verbundenem Nutzer; ein `log_berechnung` je Abbruchzyklus schriebe rund **720 gleiche Zeilen je Stunde und Nutzer** und ersäufte die Reihe, die ausgewertet werden soll. Zwei tragfähige Wege: eine Zeile je **Zustandswechsel** (Burst geht zu / geht auf; braucht einen Merker, verliert die Zahl der Blockzyklen und behält die Dauer), oder ein **Zähler je Grund** in Redis, den die nächste geschriebene Zeile mitführt und zurücksetzt (keine neuen Zeilen, exakte Verteilung, kein Zeitpunkt des einzelnen Blocks). Für die Frage *welche Grenzen hält sie ein* trägt der Zähler mehr. **Was ausdrücklich nicht mitgemacht wird:** die Riegelkette vor den Trigger ziehen — der Trigger verbraucht das Momentum (`redis.delete(momentum:…)`), und eine Umstellung änderte das Verbrauchsverhalten statt nur die Protokollierung. | ungebändigt |
| `RIEGEL-5-7-OHNE-EINTRAG` | **`thema`, `modus` und `emotion` tragen `gerechnet: false, grund: "nicht erreicht"`, auch wenn sie gelaufen sind und entschieden haben.** Sie entscheiden innerhalb von `_delivery_ausfuehren`, und dort steht kein `log_berechnung`. **Der Eintrag ist dadurch nicht falsch, aber zweideutig:** `thema: nicht erreicht` heißt entweder *ein früherer Riegel hat geblockt* oder *das Thema hat geblockt und niemand hat es aufgeschrieben* — zwei Befunde mit verschiedenen Konsequenzen, und genau die Unterscheidung, für die die Kette gebaut ist. Solange Riegel 1 oder 2 fast immer entscheiden, fällt es nicht auf; sobald sie durchlassen, ist die Verteilung der späteren Riegel unbekannt. **Zuschnitt:** derselbe Eintrag, um die drei Werte ergänzt, bevor er geschrieben wird — die Kette wandert in die Zustellung hinein statt vor ihr abzuschließen. Unabhängig von `ZUSTELLUNG-ABBRUCH-UNGEZAEHLT` baubar. | ungebändigt |

**Belegt am 15.08.2026, unmittelbar nach dem Bau von Riegel 2:** 53 Einträge
unter `node='zustellung'`, davon 45 von `frequenz` entschieden (Grund
`initiative_fehlt`, weil die Haltungsstände das Feld noch nicht tragen), 7 aus
der Zeit davor und 1 ohne Blocker. **Kein einziger Eintrag stammt von einem
Abbruch vor dem Trigger**, und in keinem trägt einer der Riegel 5 bis 7 einen
Wert.

---

## Block 18.08.2026 — aus dem Bau der Enricher-Quelle

| Kennung | Was offen ist | Band |
|---|---|---|
| `SALIENZKURVE-UNTEN-ZU-STEIL` | **Entschieden am 18.08.2026: der Exponent der Salienzkurve geht von 0,5 auf 1,16** — die Ausführung ist ein eigener Sprint und steht aus. Der untere Teil der Kurve hebt zu stark an: roh 0,3 bildet heute auf 0,674 ab und soll auf **0,40** abbilden. **Der Exponent ist der einzige Knopf und trifft die Vorgabe genau:** `EXP = 1,16` ergibt 0,4001. Die Alternative `EXP = 1,01` ergäbe 0,4504 und ist verworfen — die Vorgabe lautete 0,40 bis 0,45, gewählt ist das untere Ende. **Oben bleibt es flach, gleich welcher Exponent** — die Flachheit kommt vom Sinus, dessen Ableitung bei π/2 null ist, nicht vom Exponenten. **Warum es ein eigener Eintrag ist und nicht nebenbei geschieht:** Die Kurve steht an drei Stellen (Kurzzeitgedächtnis, Queue-Anker, Langzeit-Gewicht), und der Exponent wurde ausdrücklich von 0,6 auf 0,5 gezogen, *damit Kurz- und Langzeit dieselbe Kurve tragen*. Mitbetroffen sind drei hart eingetragene abgeleitete Konstanten — `KZG_SALIENZ_MINIMUM/MID/HIGH` (0,67379 / 0,84090 / 0,94393), und **das sind die TTL-Bänder 7 / 14 / 30 Tage**; dazu `KZG_SALIENZ_BOOST`, der ausdrücklich *nicht frei gewählt*, sondern aus den TTL-Stufen bestimmt ist, und `QUEUE_SCHWELLE`, die ausdrücklich auf dem **gedämpften** Wert gilt. **Die Neubewertung des Bestandes ist exakt und kein Schätzen:** Am Eintrag stehen `salienz_eingang` und `haeufigkeit`; der gespeicherte Wert ist eine reine Funktion daraus und wird **neu gerechnet, nicht umgerechnet** — genau der Fall, für den *die Eingaben werden gespeichert* gebaut wurde. **Die Grenze davon ist gezählt:** Von 2394 Einträgen tragen **2294 `gemessen` und 100 `geschaetzt`**; die hundert stammen aus dem Skalenumbau und würden aus einer Schätzung neu gerechnet. **Was fertig wäre:** neuer Exponent, die drei Bandgrenzen **gerechnet statt getippt**, ein Wanderungslauf über den Bestand, und eine Gegenprobe, die zeigt, dass kein Eintrag sein TTL-Band wechselt, ohne dass es beabsichtigt war. **Ausdrücklich keine Voraussetzung des Rückwegs:** Die Kurve ist streng monoton und ändert auf der rohen Skala keine einzige Rangfolge. | ungebändigt |
| `AUFZEICHNUNGEN-QUANTIL` | **Die Schwelle des `[AUFZEICHNUNGEN]`-Blocks soll gerechnet werden, nicht gesetzt** — `Quantil(1 − K/N)` der mitlaufenden Verteilung (`novaberg-agent-dateien_k.md` §3.0a-bis). Gebaut ist heute nur die eine Hälfte: **Kappung `K = 3` und ein gemessener absoluter Boden von 0,30.** Die andere Hälfte ist nicht vergessen, sondern **noch nicht rechenbar** — das Quantil bezieht sich auf die Verteilung der echten Paarung von Anfrage gegen Eintrag, und diese Verteilung beginnt erst mit diesem Bauteil zu entstehen. **Der Rohstoff läuft seit dem 18.08.2026 mit:** Die Protokollzeile trägt je Turn Trefferzahl, Bestand und den Kosinus des schlechtesten gelieferten Treffers. **Was fertig wäre:** Der K-te Wert wird über eine benannte Zahl von Turns gesammelt, das Quantil daraus gerechnet und tritt **neben** den Boden — nicht an seine Stelle: Eine Quantilschwelle kann *„hier ist nichts Passendes"* per Konstruktion nicht ausdrücken. **Die Auslösebedingung ist eine Zahl, kein Gefühl:** Liegt die Trefferzahl dauerhaft auf der Kappung, wählt die Kappung aus statt des Bodens — genau der Zustand, in dem die Bibliothek vier Monate lief (40 von 42 Aufrufen). **Seit dem 20.08.2026 ist der Rohstoff kein Engpass mehr:** Der Bestand hinter dem Block ist mit der Freigabe von `/docs` auf **174** Zeilen gewachsen, und die Verteilung entsteht ab jetzt an einem Korpus, der diesen Namen trägt. | ungebändigt |
| `AUFZEICHNUNGEN-BODEN-NACHZIEHEN` | **Am 18.08.2026 nachgemessen und widerlegt — der Eintrag bleibt offen, aber sein Gegenstand hat sich verschoben.** Sobald der Korpus heterogen war (13 statt 3 Zeilen), lag eine einschlägige Sonde bei **0,2899** und eine fremde bei **0,2515**: Die Lücke schrumpfte von 0,18 auf **0,038**, und 0,30 schnitt einen echten Treffer ab. **Die Abhilfe war nicht die nächste Zahl, sondern der zweite Kanal** (§6.3a) — der Boden behält sein Amt für den dense Kanal, der scharfe kennt ihn nicht. **Was offen bleibt:** Ob 0,30 für den dense Kanal die richtige Zahl ist, ist damit **nicht** beantwortet, nur entschärft. Eine Lücke von 0,038 trägt keine Schwelle; ob der dense Kanal auf diesem Korpus überhaupt eine tragen kann, ist die eigentliche Frage. **Was fertig wäre:** dieselbe Sondenmessung an einem Bestand, der groß genug für eine Verteilung ist, und ein Urteil darüber, ob der dense Kanal einen Boden oder nur eine Kappung braucht. → 🟢 **Am 20.08.2026 gemessen und beantwortet.** 24 Sonden (12 einschlägig mit bekannter Zieldatei, 12 fremd) gegen 174 Indexzeilen. **Die Verteilungen liegen auseinander:** einschlägig Median **0,4293**, fremd Median **0,2519** — die Lücke beträgt 0,177 gegen 0,038 am 18.08. Wiederhergestellt hat sie der **Korpus**, nicht die Schwelle. **Urteil: Der dense Kanal braucht den Boden, und 0,30 trägt hier.** Er schneidet 1 von 12 richtigen ab und lässt 1 von 12 fremden durch; elf der zwölf fremden Fragen erzeugen **null** Zeilen darüber, ohne ihn lieferte jede die Kappung voll aus. **Der abgeschnittene richtige Fall ist folgenlos — gemessen:** Die Sonde liegt dense bei 0,2189 unter dem Boden, der scharfe Kanal liefert genau diese Datei und kennt keinen Boden; der Fund besteht aus ihr allein. Auch der Vorbehalt des ursprünglichen Eintrags ist vermessen statt vermutet: In 157 von 227 protokollierten Fällen **ist** der Suchschlüssel das rohe Embedding (kein aktives Ziel, Imperativ); in den übrigen 70 liegt der gefärbte bei Kosinus 0,9330–0,9778 zum rohen. **Was daraus folgt, steht als eigener Eintrag:** `EMBED-LISTE-DATEIENINDEX` — der verbleibende Fehler ist die Rangfolge, nicht die Schwelle. Messschrieb: `2026-08-20_boden-sonden_ergebnis.md`. Ursprünglicher Wortlaut: **Der Boden 0,30 ist an drei Indexzeilen gemessen, und das steht an der Zahl.** Acht Sonden, beide Seiten, saubere Lücke zwischen 0,2014 und 0,3800 — aber der Bestand war **ein** Register (drei Dateien über die Paper des Projekts), und die Sonden liefen mit dem **rohen** Anfrage-Embedding, während der Betrieb mit dem verschobenen Suchvektor sucht. **Was fertig wäre:** dieselbe Sondenmessung erneut, sobald der Index heterogen ist (Fachtexte, Tabellen, Code), und der Vergleich der Sondenwerte gegen die im Betrieb protokollierten. **Warum es überhaupt dasteht:** Der Vorgängerwert 0,40 war nicht falsch, weil die Zahl falsch war, sondern weil ihr Vorbehalt beim Kopieren verdunstete. Dieser Eintrag ist der Vorbehalt in haltbarer Form. | ungebändigt |

---

## Block 15.08.2026 — aus dem Nachzug selbst

| Kennung | Was offen ist | Band |
|---|---|---|
| `DOKU-VOLLPRUEFUNG` | **Der Bestand einmal vollständig gegen den Code prüfen** — als eigener Auftrag, weil der Nachzug einer Sitzung ihn nicht leisten kann. **Nicht „alle 149 lesen":** Das ist dieselbe Ritualform, die schon beim Nachzug versagt. Geprüft wird über ableitbare Kriterien mit Zahlen — jeder genannte `.py`-Pfad gegen die Existenz der Datei, jedes Zeilenzitat `datei.py:NNN` gegen den Anker, den es behauptet, jeder in Backticks genannte Bezeichner gegen den Code, jede als Zählung im Text stehende Zahl gegen ihre Quelle. **Ergebnis sind vier Trefferlisten, nicht ein Urteil.** Der bekannte Rest bleibt benannt: Was ohne Datei-, Namens- oder Zahlbezug beschrieben ist, erreicht kein Kriterium — diese Klasse wird gezählt und nicht behauptet. **Am 21.08.2026 hat dieser Rest seinen ersten belegten Fall, und er stand an einer Stelle mit der Überschrift *WICHTIG*:** `novaberg-mem-kzg.md` §7 führte eine Tabelle, nach der `config.redis_client` **ohne** `decode_responses` arbeitet. Code, Kommentar und laufender Dienst sagen übereinstimmend **True**; die Aussage stand über Monate und leitet an, welchen Client man für KZG-Operationen nimmt. **Keins der vier Kriterien hätte sie gefunden** — der Pfad existiert, der Bezeichner existiert, es gibt keine Zeilenangabe und keine Zählung. **Daraus ein fünftes, das maschinell geht:** eine Tabelle, die einen **Konfigurationswert** behauptet, gegen den Wert im Code — `True`/`False` neben einem Bezeichner ist so greifbar wie ein Pfad. Anlass: `NACHZUG-KANDIDATEN-GATE` und die drei Lücken vom 15.08.2026, die zeigten, dass Drift sich über Sitzungen sammelt. | ungebändigt |
| `RAUCHTEST-ANWENDUNG-IMPORT` | **Ein Zeuge, der `main.py` importiert und die Route-Tabelle zählt.** Fünf Zeilen, und sie decken eine Klasse ab, gegen die keine Menge von Modultests hilft: einen Importfehler in der zusammengesetzten Anwendung. **Gemessen am 18.08.2026:** `grep -rln "TestClient\|import main\|api\." server/tests/` → **0 von 126** Testdateien importieren die Anwendung; eine Typannotation an einem Endpunkt legte den Dienst 9 min 38 s lahm, bei **1782 grünen Zeugen**. **Der Zeuge prüft zwei Dinge:** dass der Import durchgeht, und dass die Zahl der registrierten Routen nicht unter einen Sollwert fällt — ein Router, der still nicht mehr eingebunden wird, ist derselbe Ausfall ohne Ausnahme. **Bekannte Grenze:** Er sagt nichts über Laufzeitverhalten, nur über den Hochlauf. Genau das reicht hier. | ungebändigt |
| `NACHZUG-KANDIDATEN-GATE` | **Ein Riegel vor dem Doku-Commit, der die Kandidatenmenge aus der Dateiliste des Diffs ableitet** — für jede geänderte Produktivdatei alle Dokumente, die ihren Pfad oder Dateinamen nennen — und anschlägt, solange ein Kandidat weder geändert noch mit Grund verworfen ist. **Der Anlass ist gemessen, nicht vermutet:** Am 15.08.2026 galt ein Nachzug nach dem Bezeichner-Kriterium als vollständig (zehn Dokumente); die Ableitung aus der Dateiliste ergab **28 Kandidaten** und darin **drei echte Lücken**, keine davon über die geänderten Bezeichner erreichbar. Der Grund ist strukturell: Ein Dokument, das den Vorgang beschreibt, ohne den neuen Namen zu nennen, **kann** ihn nicht nennen. **Bekannte Grenze:** 36 der 149 Dokumente nennen überhaupt keine Datei und stehen damit in keiner Kandidatenliste — der Riegel deckt die dateibenennende Klasse ab, nicht die begriffliche. | ungebändigt |

---

## Block 14.08.2026 — aus der Eigenzeit-Messung

Drei Einträge. Der erste ist ein Zeiger auf ein Konzept und **keine Wiederholung seines Inhalts** — die sechs Bauteile stehen dort mit ZIEL, TEST, MESSUNG und Gegenprobe; hier steht nur, dass sie offen sind und in welcher Reihenfolge.

| Kennung | Was offen ist | Band |
|---|---|---|
| `EIGENZEIT-BAUTEILE` | Sechs Bauteile aus `novaberg-eigenzeit_k.md` §5, Reihenfolge **E → F → C → A → B → D**. E und F stehen vorn, weil sie das Material selbst betreffen; jeder Riegel danach entscheidet auf dem, was sie hinterlassen. **Die eigentliche Arbeit an E** ist nicht der neue Block, sondern die Stellen, die auf dem Impulsweg einen leeren Reiz als Ausfall lesen — Salienz, Verdichtung, Ablage, die Leerprüfung der erzeugenden Stufe. Wer das übersieht, tauscht eine laute Zuschreibung gegen einen stillen Turnverlust. **Stand 15.08.2026: E, F, C, A und B gebaut, D offen.** Zwei benannte Reste: C hat eine offene Kante (der Fall ohne Bezug, 39 von 56 Impulsen — die Auswahlregel ist unentschieden), und **B wirkt erst, wenn ein Eintrag mit Level auf dem Stapel liegt** — heute trägt keiner einen, weil `shadow_auftrag` keine Spalte für die Erregung hat. **Stand 15.08.2026: D ist gebaut** — damit alle sechs Bauteile. Riegel 1 entscheidet das *Ob* bei Schwelle 0,25, Riegel 2 den *Moment* als Schalter auf dem Führungsmaß, und **mit ihm ist die stündliche Decke gefallen**. Die **Frequenz-Schwelle** ist nicht entschieden, sondern gegenstandslos geworden: Die Messung hat ihre Prämisse widerlegt (das Führungsmaß trägt keine Frequenz je Paar, Verhältnis 0,22), und ein Schalter benutzt die vorhandene `GV_INITIATIVE_SCHWELLE`. Offen bleiben `PRUEFFIGUR-DISTANZ-090`, die offene Kante von C (der Fall ohne Bezug), und zwei benannte Reste der Protokollpflicht: Der Eintrag beginnt am Trigger, und die Riegel 5 bis 7 tragen ihre Werte noch nicht ein. | gebändigt bis auf die benannten Reste |
| `SCHWELLE-OHNE-PAARUNG` | Zehn Schwellen über Embedding-Kosinus zwischen 0,40 und 0,95, fünf davon auf exakt 0,40 über mindestens vier Paarungen (Fundliste, 14.08.). **Kein Aufräum-Auftrag** — wer eine anfasst, schreibt ihre Paarung dazu. **Maschinell prüfbar** und damit ein Gate-Kandidat: Eine Konstante, deren Name auf eine Ähnlichkeitsschwelle deutet, trägt in ihrem Kommentar eine Paarungsangabe. | ungebändert |
| `PRUEFFIGUR-DISTANZ-090` | Der Zuwendungs-Riegel (Bauteil D) steht bei 0,25 und trennt im Bestand sauber — **aber der Bestand enthält in der Richtung *sie → Mensch* keine Figur zwischen `distanz` 0,60 und 1,00**, also das Band, in dem der Zug schwach wird. Eine angelegte Prüffigur bei 0,90 entscheidet, ob die Trennung hält. Kosten: eine Kennung, ein Rad, ein Lauf von `haltung_naehe_verteilung`. | ungebändert |

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

**Erledigt am 21.08.2026, 22:50 UTC.** Alle **82** Abschnitte tragen die Zeile `**Zustand:**` unmittelbar unter ihrer Ueberschrift, mit geschlossener Wertemenge, Pruefdatum und dem HEAD, gegen den geprueft wurde. Auszaehlbar mit `grep -cE '^\*\*Zustand:\*\* offen'`: **64 offen, 18 behoben**. Die zwoelf zuletzt fehlenden sind nicht uebertragen, sondern **einzeln gegen HEAD `62560cf` geprueft** — sechs waren behoben, sechs offen. **Der Rest ist benannt und traegt eine eigene Kennung:** `BUGREGISTER-ALTEBENE-OHNE-ZUSTAND`. Dabei kam heraus, warum die Uebertragung nicht genuegt haette: `NOVA-SPRICHT-VON-FACHABTEILUNG` trug *behoben* in der Ueberschrift und benannte im selben Eintrag die ausstehende Schlussbedingung.

~~**Die Form steht seit dem 20.08.2026, 19:32 UTC — der Eintrag bleibt trotzdem offen.**~~ Der Rest des damaligen Absatzes ist mit der Erledigung gegenstandslos: Es fehlte nicht die Form, sondern der Nachzug der uebrigen zwoelf Abschnitte, und der steht.

**Befund (20.08.2026), beim Umzug der Fundliste entstanden.** `novaberg-bugs.md` fuehrt den Zustand eines Defekts **an drei verschiedenen Stellen und in keiner verbindlich**: In der Ueberschrift (`### KENNUNG — behoben am TT.MM.`), im Koerper (`**Behoben am ...**`) oder gar nicht. Am 20.08.2026 gezaehlt: **82 Abschnitte, 4 mit Marke in der Ueberschrift, 2 weitere nur im Koerper** — der Rest traegt keine.

**Warum es zaehlt:** Wer einen Fund umzieht, kann nicht pruefen, ob der Zieleintrag noch offen ist. Zwei Fundzeilen sagten bereits *behoben*, waehrend ihre Kennung im Register keine Marke trug. Und jede Aussage der Form *„N Defekte sind offen"* — auch die der Featureliste — beruht auf einer Heuristik ueber Textmuster statt auf einem Feld.

**Was fertig waere:** Der Zustand steht je Eintrag an genau einer Stelle und in einer geschlossenen Wertemenge, sodass ein Script ihn auszaehlen kann. Die vorhandenen 82 Abschnitte sind einmal nachgezogen.

**Prioritaet:** mittel. Kein laufender Verlust — aber jede Zahl ueber offene Defekte bleibt bis dahin eine Schaetzung.

#### BUGREGISTER-ALTEBENE-OHNE-ZUSTAND — 166 Eintraege zaehlen nicht mit

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

#### QUERY-REWRITING-QUELLE-STEHT — der Verlauf liegt vor, bevor eingebettet wird

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Der Gesprächsverlauf liegt im Enricher vollständig vor, bevor eingebettet wird — Query Rewriting braucht deshalb keine neue Datenquelle.** Der Enricher lädt in seinem ersten Abschnitt (*„Session-Kontext, immer, als erstes"*) die rohen Turns aus Redis: bis **20 Stück** (`SESSION_MAX_TURNS`), ab 25 werden die ältesten zu einer Summary verdichtet, die er daneben lädt; TTL 4 Stunden. `_create_prompt_embedding` läuft **danach** und bettet allein `reiz_text(state)` ein. **Warum das die Bauart entscheidet:** Ein Rewriter braucht weder einen neuen Knoten noch einen zusätzlichen Speicherzugriff — und er braucht **kein festes Fenster**. Ein `k` müsste raten, wie weit ein Thema zurückreicht; ein Modell, das den Verlauf sieht, muss nicht raten und schreibt beim Themenwechsel den neuen Gegenstand. Gemessen am 20.08.2026 am Code, nicht geschätzt.

**Was fertig waere:** Der Rewriter liest den vorhandenen Verlauf aus dem Enricher — ohne neuen Knoten, ohne festes Fenster.

**Prioritaet:** mittel

#### INTERNE-PROMPTS-SPRACHGEBRAUCH — fuehren interne Prompts dieselbe Sprache?

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Der Router-Prompt nennt weiter „die Fachabteilung", und das ist bewusst stehen geblieben.** Bei der Behebung von `NOVA-SPRICHT-VON-FACHABTEILUNG` sind die Blöcke der Figur umgestellt worden; `graph/nodes/router.py` sagt unverändert *„die Fachabteilung urteilt selbst und kann begründet ablehnen"*. **Der Grund für das Stehenlassen:** Der Router spricht nicht als Nova — er ist ein interner Klassifizierer, der Aushänge gegen eine Äußerung hält, und dort beschreibt der Begriff einen Mechanismus ohne Wirkung auf ein Selbstbild. **Der Grund, es trotzdem zu notieren:** Es ist dieselbe Metapher am selben Tag, und wer sie später sucht, findet eine Stelle, die anders lautet als die anderen. Zu entscheiden ist, ob interne Prompts denselben Sprachgebrauch führen sollen wie die der Figur.

**Was fertig waere:** Entschieden ist, ob interne Klassifizierer denselben Sprachgebrauch fuehren wie die Prompts der Figur; die Stellen folgen der Entscheidung.

**Prioritaet:** niedrig

#### RESPONDER-BRAUCHT-FRAGEN-DRAENGEN — dieselbe Groesse in zwei Stufen

**Befund (20.08.2026), aus der Fundliste uebernommen.** **`fragen` und `draengen` stehen jetzt in beiden Prompts — inhaltlich beim Verfasser, als Tonwort beim Responder.** Seit dem Bau vom selben Tag liest der Verfasser die drei fachlichen Größen (`[MASS]`), der Responder liest weiterhin **alle fünf**: Seine Schleife in `regie_zeilen` gibt jede Größe aus, die vom Grundwert der Landschaft abweicht, also auch `fragen` („nachhakend") und `draengen` („drängend"). **Gefunden von der zweiten Kontrolle** über ein Kriterium statt einer Aufzählung — wer liest welche Größe, als Auswertung des Quelltextes beider Knoten. **Es ist keine Doppelung im selben Prompt**, sondern dieselbe Zahl in zwei Stufen mit verschiedener Aufgabe: Der Verfasser setzt die Rückfrage, der Responder färbt ihren Ton. **Zu entscheiden ist, ob der Responder sie noch braucht.** Dafür spricht, dass er den Ton der bereits gesetzten Rückfrage formt; dagegen, dass genau diese Sorte Wiederholung am 13.08.2026 an anderer Stelle als Doppelung entfernt wurde. `umfang` steht bewusst in beiden — die Mengenangabe muss beide Stufen erreichen, und sie bedeutet dort Verschiedenes (*wie viel Stoff* gegen *wie viel Rede*).

**Was fertig waere:** Entschieden ist, ob der Responder `fragen` und `draengen` noch braucht, nachdem der Verfasser sie inhaltlich setzt.

**Prioritaet:** niedrig

#### ~~SUCHSCHLUESSEL-OHNE-VERLAUF~~ — umgesetzt am 20.08.2026

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Der Suchschlüssel des Gedächtnisses trägt ausschließlich den aktuellen Turn.** `_create_prompt_embedding` bettet `reiz_text(state)` ein, also `user_prompt` bzw. `eigener_gedanke` — kein Verlauf. Verschoben wird der Vektor danach durch `wahrnehmung_verschieben`, aber Richtung **Ziele**, nicht Richtung Gespräch; vom Vorturn erreicht die Suche genau ein Datum, seinen *Cluster*, und der steuert nur die Mischstärke, nicht den Inhalt. **Folge:** Ein Turn wie *„und wie weist man das nach?“* sucht ohne den Gegenstand, den der Turn davor genannt hat — KZG, LZG und Bibliothek gleichermaßen, denn alle drei bekommen denselben `such_vektor`. **Entscheidung des Meisters, 20.08.2026: Der Weg ist Query Rewriting** — ein Modellaufruf formt aus den letzten Turns eine eigenständige Suchanfrage. Verlaufsvektor, HyDE-Variante und Mehrfachsuche mit Fusion sind ausdrücklich verworfen. **Offen ist der Wirkungsbereich:** alle drei Speicher oder zunächst nur die Bibliothek — heute ist der Schlüssel für alle derselbe, und das ist eine ausdrücklich begründete Eigenschaft (`enricher.py`, Kommentar zu `state["such_vektor"]`).

**Was fertig waere:** Der Suchschluessel traegt den Gegenstand des Gespraechs; offen ist der Wirkungsbereich — alle drei Speicher oder zunaechst die Bibliothek.

→ **Umgesetzt am 20.08.2026 als Query Rewriting.** `_suchtext_bauen` im Enricher formt aus dem Verlauf eine eigenstaendige Suchanfrage; der Wirkungsbereich sind **alle Leser des Schluessels** — und das sind fuenf, nicht drei: KZG, LZG, die Bibliothek, der Dateienindex und die beiden NMCP-Dienste, denen `such_vektor` als angemeldeter Bedarf mitwandert. Die Zahl kommt aus der zweiten Kontrolle; der ausloesende Befund nannte drei. **Die Zielaktivierung zieht nicht mit** — sie rechnet weiter gegen das rohe Embedding und waere sonst ihre eigene Eingabe.

Gemessen vor dem Bau gegen 306 Ausarbeitungen und zehn Verlaeufe mit anaphorischem Schlussturn: Die rohe Aeusserung erreicht in **0 von 10** Faellen die Abrufschwelle, das Rewrite auf Frageform in **5 von 10**; die Themenform blieb bei 3 von 10 und ist deshalb nicht gewaehlt. Gegenrichtungen sauber: Themenwechsel 3/3 unter der Schwelle, fremde Alltagsverlaeufe 15/15 ohne Treffer. Im Betrieb an einem echten Turn belegt.

~~**Ein Rest bleibt und ist benannt:** Ob das Rewrite auch KZG, LZG, den Dateienindex und die beiden Dienste **besser** trifft, ist nicht gemessen — die Sonden liefen gegen die Bibliothek.~~ → **Am 21.08.2026 gemessen, der Rest ist zu.** 39 Sonden aus dem Bestand der Konsumenten selbst, durch ihren echten Lesepfad: rohe Aeusserung **0/39**, Rewrite **37/39**, Deckung mit der handaufgeloesten Referenz **39/39**. Der fuenfte Konsument, NMCP `wissen`, teilt den Lesepfad der Bibliothek (dieselbe Abfrage, dieselbe Schwelle, Kappung 5 statt 3) und ist damit mitgedeckt. **Zwei Konsumenten haben keinen wirksamen Boden** — KZG und der NMCP-Dienst `dateien` liefern ihre volle Kappung auch auf eine Frage ohne Gegenstand; dort tauscht das Rewrite falschen Inhalt gegen richtigen, statt Treffer hinzuzufuegen. Das ist ein eigener Fund und steht in der Fundliste.

**Prioritaet:** hoch

#### ZUSAMMENFASSUNG-ALS-ZWEITER-ARM — der Vektor liegt, der Leser fehlt

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Die eingebettete Zusammenfassung liegt gefüllt im Bestand und wird vom Suchweg der Bibliothek nicht benutzt.** `autonomous_wissen.themen_embedding` ist trotz des Namens der Vektor der **Zusammenfassung** — `embed_text_bauen` ist die Identität auf `zusammenfassung` (Ø 583 Zeichen). **Gemessen am 20.08.2026: 320 von 320** aktiven Ausarbeitungen vom Typ `wissen` tragen ihn. Der Rückweg nutzt ihn (25 von 25 unter den ersten acht, `db/init.sql`); `AutonomousWissenRepository.suchen` joint dagegen ausschließlich auf `autonomous_wissen_thema` und sieht ihn nie. **Warum es zählt:** Die Bauart *„Zusammenfassung je Ausarbeitung einbetten“* — bis dahin als offene Entwurfsfrage geführt — ist damit kein Bau, sondern ein zweiter Arm in einer vorhandenen Abfrage — der Vergleichsgegenstand auf Inhaltshöhe existiert bereits.

**Was fertig waere:** Die Suche der Bibliothek hat einen zweiten Arm auf Inhaltshoehe; der Vergleichsgegenstand existiert bereits.

**Prioritaet:** mittel

#### AUFSTELLUNG-NICHT-VERSIONIERT — der Aufbau von null verliert die Freigabe

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Die Freigabe von `docs/` überlebt keinen Aufbau von null.** Beide Hälften der Zusicherung — der lesende Einhängepunkt und der Außenrand `/files,/docs` — stehen in `docker-compose.yml`, und diese Datei liegt **außerhalb des Git-Roots**. Wer das System aus dem Repositorium neu aufsetzt, bekommt einen Dienst, dessen Doku eine Freigabe beschreibt, die es nicht gibt; das Tor wiese sie ab, und der Grund stünde in keiner versionierten Datei. **Das berührt `F-SCHEMA-2`** (Aufbau von null muss reproduzierbar funktionieren) — dort allerdings für das Datenbankschema formuliert, während die Lücke hier in der Aufstellung liegt. **Nicht neu, aber neu wirksam:** Der Zustand galt auch für `/files`, `/knowledge` und `/logs`; erst mit einer Freigabe, die in der Repo-Doku ausführlich beschrieben ist, wird aus der Eigenschaft ein Widerspruch. **Zu entscheiden ist, ob der Harness eine Aufstellungsbeschreibung bekommt** — die Compose-Datei selbst gehört nicht ins öffentliche Repositorium, ihre Wirkung aber in eine Datei, die jemand findet.

**Was fertig waere:** Die Wirkung der Aufstellung steht in einer Datei, die jemand findet — der Aufbau von null erzeugt dieselbe Freigabe, die die Doku beschreibt.

**Prioritaet:** hoch

#### SCHREIBPFAD-BIBLIOTHEK-UNGEMESSEN — vier Embeddings je Ablage, Kosten unbekannt

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Der Schreibpfad der Bibliothek ist seit dem Umbau teurer, und um wie viel ist nicht gemessen.** Jeder `speichern()`-Aufruf baut jetzt die Themenvektoren — bei Ø 4,37 Themen je Ausarbeitung sind das rund vier zusätzliche Embedding-Aufrufe je Ablage, auf dem kleinen Modell (0,6 GB). Beobachtet am 19.08. um 20:36 UTC, als 31 Rückweg-Aufträge in Serie liefen: GPU zu **100 %** ausgelastet, VRAM 89 %, 83 Modellaufrufe in sechs Minuten. **Der Beitrag der Themenvektoren daran ist nicht isoliert** — die 83 Aufrufe sind Chat-Aufrufe von `zuordnung` und `einarbeitung`, die Embeddings kommen zusätzlich. Wer die Kosten des Schreibwegs beziffern will, misst sie eigens.

**Was fertig waere:** Die Kosten des Schreibwegs sind eigens gemessen, getrennt von den Chat-Aufrufen daneben.

**Prioritaet:** niedrig

#### RUECKWEG-VORAUSWAHL-OHNE-TRENNSCHAERFE — acht Kandidaten, 0,066 Abstand

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Die Vorauswahl des Rückwegs wählt kaum vor: acht Kandidaten liegen im Median 0,066 Kosinus auseinander.** `kandidaten_laden` kappt bei `KANDIDATEN_KAPPUNG = 8` und hat **keine Schwelle**; die acht gehen an ein Modell, das eines auswählt. Gemessen über 25 echte Kontexte (Ø 833 Zeichen): Abstand Rang 1 zu Rang 8 **0,0664** beim heutigen Ziel, 0,0718 bei Themenvektoren. **Wenn alle acht praktisch gleich nah sind, trägt die Rangfolge die Auswahl nicht** — das Modell entscheidet dann über den Text, nicht über die Nähe, und die Vorauswahl ist eine Kappung ohne Aussage. Ob das schadet, hängt daran, wie gut das Modell aus acht ähnlichen wählt; gemessen ist das nicht.

**Was fertig waere:** Entweder traegt die Rangfolge die Auswahl, oder die Kappung ist als Kappung ohne Aussage benannt.

**Prioritaet:** mittel

#### BEZUG-ID-NIE-AUSGELOEST — 0 von 904, die Absicherung ist unbelegt

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Die Ausschluss-Absicherung des Verweiswegs ist gebaut und im Betrieb nie ausgelöst worden.** `shadow_auftrag.bezug_id` hält die gerade angelegte eigene Bibliothekszeile aus der Kandidatenmenge des Rückwegs; ohne sie verstärkt jedes Recherche-Ergebnis sich selbst. Gemessen: **0 von 904** Aufträgen tragen einen Wert. **Das ist kein Defekt** — die einzige Schreibstelle ist `agents/recherche/agent.py::_verweis_einreihen`, und die drei vorhandenen `wissen_verweis`-Aufträge stammen aus dem Zeitfenster **vor** der Behebung von `VERWEIS-OHNE-WISSEN` (08:03–08:05 UTC, alle mit dem Platzhalter-Thema `Gescheitert <hash>`). Der Befund ist: **Die Absicherung hat noch keinen einzigen echten Lauf gesehen**, und ihre Wirksamkeit ist damit unbelegt — sie steht auf 0 von 0.

**Was fertig waere:** Die Ausschluss-Absicherung hat einen echten Lauf gesehen und ihre Wirksamkeit ist belegt.

**Prioritaet:** mittel

#### RECHERCHE-REIHT-NICHT-MEHR-EIN — elf Stunden ohne Auftrag

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Seit elf Stunden wird kein Recherche-Auftrag mehr eingereiht, während weiter Wissenszeilen entstehen.** Gezählt ab 08:06 UTC: **0** neue Aufträge mit `aufgabe='recherche'`, **0** mit `wissen_verweis` — aber **13** neue Zeilen in `autonomous_wissen`, die jüngste um 18:59 UTC. Die Zeilen entstehen also über den Rückweg (`agent/wissen_rueckweg/einarbeitung`), nicht über die Recherche. **Warum das zusammenhängt:** Der Verweis wird ausschließlich vom Recherche-Pfad eingereiht; solange dieser keine Aufträge bekommt, kann der Verweisweg nicht laufen, und keine seiner Absicherungen wird geprüft. Ob das Ausbleiben gewollt ist, ist nicht geklärt.

**Was fertig waere:** Geklaert ist, ob das Ausbleiben gewollt ist; wenn nicht, reiht der Pfad wieder ein.

**Prioritaet:** hoch

#### NACHLAUF-VOR-DER-ZUSTELLUNG — acht Sekunden nach der fertigen Antwort

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Die Antwort wird erst nach dem vollständigen Durchlauf zugestellt, und der Nachlauf kostet gemessen 8 Sekunden.** Der CharacterGraph ist durchgehend sequenziell verdrahtet (`responder → thinker → tribunal → evaluate → perzeption_assistant → ei_calc_persist → salience → dispatcher → END`), und `_event_verarbeiten` sendet erst danach: erst `await asyncio.to_thread(_graph_streamen, …)`, dann `if response and …`. **Gemessen an einem echten Turn:** Responder fertig 15:29:22,488 — Tribunal mit drei Modellaufrufen bis 15:29:29,310 (**6,8 s**) — Antwort-Perzeption bis 15:29:30,545 (1,2 s) — Durchlauf beendet 15:29:30,559. **Keiner dieser Knoten wird gebraucht, bevor der Mensch liest**; sie brauchen die Antwort, nicht umgekehrt. Ein früher entworfener asynchroner Block ist in `novaberg-ei-dual-emotion_k.md` als *„⚠ Veraltet"* markiert und wurde durch das Event-Modell ersetzt — der Nachlauf ist damit nicht abgeschafft, sondern in die Sequenz gewandert. **Vorbedingung für eine Umstellung ist der Riegel gegen die leere Antwort**, sonst stellt man sie nur schneller zu.

**Was fertig waere:** Der Mensch bekommt die Antwort, bevor der Nachlauf laeuft — Vorbedingung ist der Riegel gegen die leere Antwort.

**Prioritaet:** hoch

#### REPEAT-PENALTY-OHNE-HERKUNFT — 1.3, und niemand weiss warum

**Befund (19.08.2026), aus der Fundliste uebernommen.** **`gemma4-gpu` fährt `repeat_penalty 1.3`, und niemand kann sagen, woher die Zahl kommt.** Sie steht als `PARAMETER` im selbstgebauten Modelfile. Zum Vergleich: Ollama hat den Vorgabewert für Modelle **ohne** eigene Angabe am 12.08.2026 von 1.1 auf 1.0 gesenkt (v0.32.10, *„matching other engines"*) — der Bestand liegt also deutlich über beiden Werten, die die Laufzeit je als Vorgabe geführt hat. Ob 1.3 gemessen oder übernommen ist, steht nirgends. Betrifft Antwortlänge und Wortwahl aller Gesprächsknoten und damit jede Messreihe, die gegen sie kalibriert ist.

**Was fertig waere:** Der Wert ist gemessen oder auf den Vorgabewert zurueckgesetzt; die Begruendung steht am Modelfile.

**Prioritaet:** mittel

#### ANBIETERDAUERN-UNGELESEN — liegen vor, werden nirgends gelesen

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Die Dauern des Anbieters liegen seit jeher vor und werden nirgends gelesen.** `eval_duration`, `load_duration`, `prompt_eval_duration` und `total_duration` stehen in jeder Antwort. Wartezeit **am Modell** und Wartezeit **im Graphen** werden heute aus Zeitstempeln zweier Logzeilen erschlossen; mit diesen Feldern wären sie je Aufruf direkt getrennt. Betrifft jede Aussage über den seriellen Platz. Gehört zu `ANBIETER-FELDER-UNGELESEN`.

**Was fertig waere:** Die Dauern des Anbieters gehen in eine Auswertung, oder sie werden nicht mehr erhoben.

**Prioritaet:** niedrig

#### FUNDSTELLE-ERREICHT-DEN-MENSCHEN-NICHT — der Dienst nennt sie, die Antwort nicht

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Der Dienst nennt seine Fundstelle, und die Antwort an den Menschen nennt sie nicht.** Echter Turn 12:43 UTC: `agents/wissen` liefert fünf Treffer, und sein Text trägt je Treffer den Dateipfad, den Kosinus und den ausdrücklichen Hinweis *„das ist der Stand aus meinen Metadaten — nicht der Wortlaut der Ausarbeitung"*. Die Antwort, die beim Menschen ankommt, ist inhaltlich richtig (ER=EPR, Page-Kurve, Island-Regel) und nennt **weder eine Datei noch die Tiefe** — sie liest sich, als wüsste sie es aus sich. Das ist die Frage aus `novaberg-agent-dateien_k.md` §1a.4 für dieses Silo, und für den Zettel-Weg ist sie unbeantwortet: Beim Dateien-Dienst trägt der Enricher-Block eine Beschriftung, hier läuft die Auskunft über `management_result`. Zu messen: an wie vielen von N Turns die Herkunft den Responder überlebt.

**Was fertig waere:** Die Antwort an den Menschen nennt die Fundstelle, die der Dienst geliefert hat.

**Prioritaet:** mittel

#### SILO-OHNE-ZUSTAND-IN-DER-MATRIX — gebaut und abgeschaltet ist kein Zustand

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Ein Silo, dessen Lesefunktion gebaut und abgeschaltet ist, hat in der Rollenmatrix keinen Zustand.** `fakten` überschreibt `enrich_entries` und wird im Enricher mit `continue` übersprungen, begründet im Code mit *„produziert 130+ Rausch-Eintraege"*. Die Matrix kennt nur *ja* und *nein*; gebaut-und-stillgelegt ist beides nicht und sieht in jeder Zählung wie eine bewusste Entscheidung aus. Betrifft jede Prüfung, die aus der Anwesenheit einer Methode auf eine Rolle schließt.

**Was fertig waere:** Die Rollenmatrix kennt den Zustand *gebaut und abgeschaltet*.

**Prioritaet:** niedrig

#### BESTAND-ANTWORTET-ANDERS-NACH-90-MIN — 0,9226 gegen 0,4163

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Dasselbe Material fand denselben Bestand neunzig Minuten spaeter voellig anders — bester Kosinus 0,9226 gegen 0,4163.** Zwei Verweis-Laeufe mit **zeichengleichem** `kontext` (08:21 und 09:46). Dazwischen wurde Zeile 8974 verstaerkt (`verstaerkt_am` 08:22:03), und die Verstaerkung **haengt die Ergaenzung an die Zusammenfassung an**, die bei 500 Zeichen gekappt ist — beide Zeilen stehen heute exakt auf dieser Kappung. **Korrelation, keine belegte Ursache**; was fehlt, ist die Antwort auf die Frage, ob `speichern` den Vektor neu rechnet. **Wenn ja, verschlechtert eine Verstaerkung die Auffindbarkeit genau des Materials, das sie ausgeloest hat** — der Mechanismus arbeitete dann gegen sich selbst. Zu messen: derselbe Fund vor und nach einer Verstaerkung, Kosinus beide Male.

**Was fertig waere:** Geklaert ist, warum dasselbe Material denselben Bestand verschieden findet.

**Prioritaet:** hoch

#### KANDIDATENABFRAGE-OHNE-DB-ZEUGEN — eine Verschiebung bliebe gruen

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Kein Zeuge faehrt die Kandidatenabfrage des Rueckwegs gegen eine Datenbank — eine Verschiebung zwischen Platzhaltern und Parametern bliebe gruen.** Vorhergesagt waren 3 rote Tests beim Entfernen der Ausschlussbedingung, gezaehlt wurden **2**; der dritte war ausdruecklich als unsicher benannt und ist der Befund: Die Attrappe prueft die Parameterzahl nicht, ein echter Lauf gegen Postgres waere gescheitert. Klasse `20_TESTS §4h` — ein Zeuge faehrt den Bestand, nicht seine Nachbildung. **Betrifft nicht nur diese Abfrage:** Wer eine Spalte in eine bestehende Abfrage einfuegt, hat hier keine Wand.

**Was fertig waere:** Ein Zeuge faehrt die Kandidatenabfrage gegen eine echte Datenbank.

**Prioritaet:** mittel

#### VERSTAERKUNGSPFAD-IM-BETRIEB-UNGETROFFEN — bezeugt, gegengeprobt, nie gelaufen

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Der Verstaerkungspfad von Weg 3 ist bezeugt und gegengeprobt, aber im Betrieb noch nicht getroffen worden.** Vier echte Laeufe am 19.08. endeten alle in *keine Zuordnung* — dreimal begruendet, einmal als unbrauchbarer Aufruf. Der Zweig, der `haeufigkeit` und `gewicht_roh` hebt, ist damit **am Bestand ungemessen**; was vorliegt, ist die Zusicherung und die Gegenprobe. Der Grund ist nicht der Bauteil, sondern der serielle Platz: Der wartende Auftrag steht hinter einem Recherche-Lauf.

**Was fertig waere:** Der Verstaerkungspfad hat einen echten Lauf im Protokoll.

**Prioritaet:** niedrig

#### DREI-WEGE-EINE-SCHWELLE — zeichengleich mit der Promotions-Schwelle

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Die Schwelle des *Einpraegsamen* ist zeichengleich die Schwelle, die schon die Promotions-Queue oeffnet — die drei Wege aus §4b.1a sind nicht drei Kriterien, sondern zwei.** `novaberg-agent-dateien_k.md` §4b.1a nennt fuer den ersten Weg `salienz_roh >= 0,7`; `KZG_SALIENZ_HIGH = 0.94393` traegt im Code den Kommentar `# roh 0.7`, und genau an dieser Konstante haengen die beiden Einreihpunkte der Promotion (`memory/kzg.py`, `agents/kzg/queues.py`). **Der erste Weg feuert damit auf exakt der Menge, aus der der zweite spaeter seine Kandidaten zieht** — nicht ueberlappend, sondern als Obermenge, nur frueher. Gemessen am laufenden Bestand: **2597 von 2942 Eintraegen (88,3 %)** liegen ueber der Schwelle, in den letzten 24 Stunden **108 von 161 neuen**. Der Rueckweg-Auftragsbestand ist heute **3**.

**Was fertig waere:** Die drei Wege tragen drei Kriterien, oder ihre Gleichheit ist als Absicht benannt.

**Prioritaet:** mittel

#### EINREIHPUNKT-HINTER-DEM-SCHREIBEN — Ergaenzung verlangt, Datei schon geschrieben

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Der dritte Weg verlangt *als Ergaenzung, nicht als neue Datei* — und sein Einreihpunkt liegt hinter dem Schreiben der Datei.** `ergebnis_ablegen` (`services/wissensspeicher.py`) legt Bericht und Wissensdatei an und schreibt die Bibliothekszeile; der Einreihpunkt fuer den Rueckweg kann erst danach liegen, weil der Docstring den Queue-Push ausdruecklich dem Aufrufer zuweist. Wer dort einreiht, bekommt **beides**: die neue Datei **und** denselben Inhalt in eine bestehende eingearbeitet. Der Wortlaut des Konzepts meint das Gegenteil.

**Was fertig waere:** Der Einreihpunkt des dritten Wegs liegt dort, wo die Ergaenzung noch moeglich ist.

**Prioritaet:** mittel

#### SHADOW-AUFTRAG-OHNE-TURNBEZUG — der Rueckweg umgeht es ueber `modus`

**Befund (18.08.2026), aus der Fundliste uebernommen.** **`shadow_auftrag` hat keine Spalte für den Turnbezug, und der Rückweg umgeht das über `modus`.** Der Auslöser löst deshalb das Material selbst auf und gibt den Wortlaut im `kontext` mit; die Herkunftsmarke reist als `rueckweg_roh` / `rueckweg_verdichtet` im `modus`-Feld. Das trägt, ist aber eine Zweitnutzung: `modus` benennt die Lage, aus der ein Auftrag entstand, nicht die Herkunft seines Textes. Eine eigene Spalte wäre DDL und ist bewusst nicht nebenbei gelegt worden.

**Was fertig waere:** `shadow_auftrag` traegt den Turnbezug als eigene Spalte (DDL, vorher ankuendigen).

**Prioritaet:** mittel

#### RUECKWEG-HINTER-DEM-RUECKSTAND — nicht messbar bei 714 Auftraegen davor

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Der Rückweg ist über den Pixie-Zeitplan nicht messbar, solange die Queue 714 Aufträge höherer Salienz trägt.** Gemessen beim Einreihen: 497 `recherche`, 172 `vertiefen`, 45 `nachfragen`, alle bis Salienz 1,000 — der Rückweg-Auftrag steht mit 0,920 dahinter. Die beiden Messläufe liefen deshalb am Zeitplan vorbei, mit gestarteten Workern im eigenen Prozess. **Was damit nicht gemessen ist: dass der Auftrag je an die Reihe kommt.** Derselbe Engpass wie `PIXIE-EIN-SLOT-BLOCKIERT-ALLES`, hier zum ersten Mal an einem neuen Bauteil.

**Was fertig waere:** Der Rueckweg ist ueber den Zeitplan messbar — entweder der Rueckstand faellt oder er bekommt eine eigene Spur.

**Prioritaet:** mittel

#### DATEIEN-VERBUND-OHNE-MODULDOKUMENT — kein Moduldokument unter `docs/`

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Der ganze Dateien-Verbund hat kein Moduldokument unter `docs/`.** Gefunden über die Gegenrichtung, nicht über den Bau: Vier Agenten tragen eines (`novaberg-agent-character.md`, `-directives`, `-notes`, `-timeline`), die drei Dateien-Dienste keines — sie haben nur ihr `AGENT.md` neben dem Code und das gemeinsame Konzept `_k`. **Beidseitig gezählt: 4 von 19 Agentenverzeichnissen haben ein Moduldokument.** Das ist kein Versäumnis dieses Aufrufers, sondern der Zustand des Verbunds; zu entscheiden ist, ob das Moduldokument die Sorte ist, die hier fehlt, oder ob `AGENT.md` sie ersetzt.

**Was fertig waere:** Der Dateien-Verbund hat ein Moduldokument, das seinen heutigen Zustand beschreibt.

**Prioritaet:** mittel

#### RUECKFRAGE-DEKLARIERT-UND-UNGENUTZT — deklariert, nie benutzt

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Der lesende Dienst deklariert die Rückfrage und benutzt sie nie.** `ausgaenge` trägt alle vier, `build_graph` hat keinen Knoten, der `status="rueckfrage"` setzt, und der Dispatch kennt keinen Rückweg. Das ist begründet — der Dienst ändert nichts, also gibt es nichts zu bestätigen —, aber die Deklaration sagt das nicht: Ein Aufrufer, der sie liest, hält einen Ausgang für bedient, den es nicht gibt. Zu klären ist, ob der Kanon der Ausgänge *„kann"* oder *„tut"* bedeutet.

**Was fertig waere:** Der lesende Dienst benutzt seine Rueckfrage oder deklariert sie nicht mehr.

**Prioritaet:** niedrig

#### ZEILEN-LESEN-OHNE-AUFRUFER — weiterhin kein Aufrufer

**Befund (18.08.2026), aus der Fundliste uebernommen.** **`zeilen_lesen` hat weiterhin keinen Aufrufer.** Der Zoom des lesenden Dienstes kennt Karte, Block und Nadel; das Zeilenfenster aus `tools/dateien/operationen.py` ruft niemand. Rest von `WIS-8-STUFE-2`, dort benannt.

**Was fertig waere:** `zeilen_lesen` hat einen Aufrufer oder ist entfernt.

**Prioritaet:** niedrig

#### AGENTGRAPH-FAEHRT-VOLLEN-ENRICHER — drei Knoten, voller Enricher

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Der AgentGraph fährt den vollen Enricher des Charakter-Pfads, obwohl er nur drei Knoten hat.** `services/shadow_delivery.py` setzt für ihn `ei_calc_rolle="character"`; `enrich()` wählt danach `_enrich_character`, und der AgentGraph besteht aus Enricher → Salience → Dispatcher — **ohne Verfasser**. Damit entstehen Kontextgrößen, für die auf diesem Pfad kein Leser existiert; beim Dateien-Index sind es zwei Postgres-Abfragen je Lauf. **Betriebsgewicht gemessen:** `SELECT quelle, count(*) FROM pipeline_log WHERE node='enricher' AND erstellt_am > NOW() - INTERVAL '24 hours'` → `character` 45, `user` 44, **`agent` 0**. Der Pfad ist offen und hat in 24 Stunden nicht gefeuert — deshalb eine Zeile hier und keine Kennung. **Die Frage ist älter als der Dateien-Index und größer:** Welche der Enricher-Quellen der AgentGraph überhaupt braucht, ist nirgends entschieden; er bekommt sie alle, weil er sich als Charakter-Pfad ausweist.

**Was fertig waere:** Der AgentGraph laedt, was er braucht.

**Prioritaet:** mittel

#### WERKZEUGSCHICHT-DATEIEN-OHNE-RUFER — gebaut, niemand ruft sie

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Die Werkzeugschicht für Dateien ist gebaut und wird von niemandem gerufen.** `tools/dateien/` trägt seit dem 18.08.2026 vier Module mit 88 Zeugen — Karte, Block, Fenster, Fundstelle, chirurgische Schnitte, Versionierung mit Paarungsprüfung, und die Auftragsform `DATEI: {json}`. Gezählt über `grep` auf die Importe: **kein Knoten, kein Agent, kein Plugin importiert eines davon**, und die Anleitung steht in keinem Prompt. Der Werkzeugsatz ist an echten Wissensdateien erprobt (Kette aus Karte, Änderung, Einfügen, Verlauf, Paarung — 0 Befunde), aber Nova kann nichts davon aufrufen. **Kein Defekt, sondern ein Zwischenstand** — festgehalten, weil 88 grüne Zeugen genau darüber nichts sagen und die Lage aus dem Testergebnis nicht ablesbar ist.

**Was fertig waere:** Die Werkzeugschicht fuer Dateien hat einen Eingang von der Nutzerseite.

**Prioritaet:** hoch

#### RECHERCHE-LIEST-EIGENE-BIBLIOTHEK-NICHT — fuellt sie und liest sie nicht

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Der Recherche-Pfad liest die Bibliothek nicht, die er selbst füllt — sein „Vorwissen" kommt aus den Assoziationen.** `kontext_paket_bauen` in `agents/recherche/lagebeurteilung.py` aggregiert fünf Quellen — Session-Kontext, LZG-Treffer, KZG-Einträge, Charakter-Hash, Beziehungsdynamik — und `autonomous_wissen` ist **keine davon**. Daraus entsteht `vorwissen_zusammenfassung`, und genau die geht in das Keep/Discard-Gate, dessen Kopf sagt: *„Steht im Destillat etwas, das über Novas Vorwissen hinausgeht?"* **Beurteilt wird damit gegen Assoziationen, nicht gegen ihr ausformuliertes Wissen.** Gezählt über `SELECT ... FROM autonomous_wissen`: Es gibt drei Leser — den Existenz-Vorcheck im Enricher, den Abruf des WissenManagers im Gesprächspfad, und das Repository für Gewicht und Häufigkeit beim Schreiben. **Der Agent, der die Bibliothek schreibt, liest sie nie**; `gate.py` importiert von dort nur den Status-Kanon. Folge: Nova kann zu einem Thema eine Wissensdatei besitzen, und die Lagebeurteilung sieht sie nicht — das Gate kann `echte_tiefe` urteilen, wo `wiederholung` richtig wäre. Das ist die Klasse, gegen die das Gate laut eigenem Kopf gebaut ist (*„die Bibliothek füllt sich mit Wiederholungen, die jede spätere Ähnlichkeitssuche verwässern"*). **Der Schaden ist noch nicht messbar und das gehört dazu:** Über 23.436 Paare liegen nur **6 über 0,70** und 2 über 0,75 — bei einem Bestand von dreizehn Tagen. Die Struktur ist falsch, die Wirkung ist eine Vorhersage und kein Befund; sie wächst mit der Kollisionswahrscheinlichkeit des Korpus. Aufgefallen beim Entwurf des Dateien-Dienstes, weil dort dieselbe Frage — *„habe ich dazu schon Wissen?"* — das Tor vor dem Dateizugriff bilden soll.

**Was fertig waere:** Der Recherche-Pfad liest die Bibliothek, die er fuellt.

**Prioritaet:** mittel

#### RETRIEVAL-SCHWELLE-OHNE-WIRKUNG — die Kappung gibt den Ausschlag

**Befund (17.08.2026), aus der Fundliste uebernommen.** **`WISSEN_RETRIEVAL_SCHWELLE = 0.40` hat noch nie den Ausschlag gegeben; die Kappung gibt ihn — und der Vorbehalt dazu ist auf dem Weg ins Konzept verdunstet.** Der Wissens-Manager sucht mit `WHERE cosine >= 0.40 ... LIMIT WISSEN_RETRIEVAL_TOP_K`, und `WISSEN_RETRIEVAL_TOP_K` ist **3**. Über 42 protokollierte Aufrufe kamen **40 mal genau drei** Treffer zurück — die Obergrenze, nicht die Auswahl. Der Kosinus des dritten Treffers liegt bei min 0,404, **Median 0,588**, max 0,691. Die Geometrie des Korpus erklärt, warum die Schwelle nichts tut: 217 aktive Einträge, 23.436 Paare, **Median-Kosinus 0,369**, und **35,6 % aller Paare liegen über 0,40**. Erst **0,55** liefert gerechnet die drei Treffer, die tatsächlich ankommen; **die wirksame Schwelle ist 0,55 und steht nirgends.** — **Der Bestand ist dabei nicht der Schuldige, und das ist der eigentliche Fund.** `config.py:478` sagt von sich aus *„von `anker_retrieval` uebernommen, NICHT gemessen"*, nennt den Grund (*„die Bibliothek hatte bei ihrer Einfuehrung drei Zeilen"*) und verweist auf den offenen Backlog-Eintrag `WIS-SCHWELLE-MESSEN`. Auch die Quelle trägt ihren Vorbehalt: `lzg_knoten.py:425` führt die Abdeckungsmessung mit (0,50 → 53 %, **0,40 → 82 % bei 4,1 Ankern von 302**, 0,35 → 89 % und Rauschen) und markiert sie als *„begruendeter Startwert, kein Verteilungs-Messergebnis"*. **Beide Code-Stellen sind ehrlich; erst das Konzept nannte den Wert „gemessen"** (`novaberg-agent-dateien_k.md` v0.5/v0.6, in v0.7 berichtigt). Die Zahl gibt der Übernahme quantitativ Unrecht: Im Knotenraum qualifiziert 0,40 rund **1,4 %** des Bestandes, in der Bibliothek **35,6 %** — derselbe Wert, derselbe Embedding-Raum, **Faktor 26 im Trennverhalten**. **Die Klasse ist allgemeiner als der Fall, und sie ist zweiteilig:** Ein Grenzwert, hinter dem eine Kappung steht, ist unbelegt, solange die Kappung greift — und **ein Vorbehalt überlebt das Kopieren einer Zahl nicht**, wenn nur die Zahl kopiert wird.

**Was fertig waere:** Die Schwelle wirkt oder entfaellt; der Vorbehalt steht unverkuerzt im Konzept.

**Prioritaet:** mittel

#### GRENZE-OHNE-LESER — auf fuenf Diensten deklariert, null Leser

**Befund (17.08.2026), aus der Fundliste uebernommen.** **`grenze` ist auf fünf Diensten deklariert und hat null Leser.** Die Eigenschaft beantwortet *„was tust du ausdrücklich nicht"* und ist nach der NMCP-Konvention Pflicht für alle Dienste; im Bestand tragen sie vier Empfangsdienste mit je drei Einträgen. **Kein Code liest sie** — weder der Aushang-Aggregator, noch die Anmeldeprüfung, noch der vierte Ausgang. Damit ist sie genau die Klasse, gegen die die Konvention gebaut wurde, entstanden am Tag ihrer Einführung. Die Konvention nennt ihren Zweck in §4.9: Trifft die Zustellquote und ist die Ablehnungsquote hoch, dann stimmt der Aushang und **die Grenzangabe fehlt** — dafür muss sie aber irgendwo gelesen werden. Wohin sie gehört, ist eine Entscheidung: ins Brett neben die Negativfälle (dann verhindert sie Zustellungen, die ohnehin abgelehnt würden), oder in den Vorschlag des vierten Ausgangs (dann erklärt sie dem Auftraggeber die Ablehnung).

**Was fertig waere:** `grenze` wird gelesen oder ist entfernt.

**Prioritaet:** niedrig

#### WISSEN-UND-WEBSUCHE-NICHT-ANSPRECHBAR — ueber den Empfang nicht erreichbar

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Novas eigenes Wissen und die Websuche sind über den Empfang nicht als Dienste ansprechbar.** Eine Äußerung wie *„such mal in deinem Wissen"* oder *„schau im Netz nach"* spricht etwas an, das keinen Aushang hat: Die Bibliothek (`autonomous_wissen`, 463 Zeilen) hängt als Kontextquelle am Enricher und wird nicht gewählt; der Web-Pfad läuft über den Zustandsmerker `needs_web`, den der Empfang setzt und den der Denkknoten liest — ebenfalls kein Dienst. **Damit gibt es drei Wissensbestände mit drei verschiedenen Zugängen** (eigenes Wissen, freigegebene Dateien, Web), von denen nur einer über einen Zettel erreichbar wäre. Ein Mensch, der einen davon ausdrücklich anspricht, bekommt kein Urteil und keine Fehlmeldung, sondern eine Antwort aus dem, was der Enricher ohnehin gelegt hat. Aufgefallen beim Entwurf des Dateien-Dienstes (`novaberg-agent-dateien_k.md` §3.0c); älter als er.

**Was fertig waere:** Novas eigenes Wissen und die Websuche sind als Dienste ansprechbar.

**Prioritaet:** mittel

#### SELBSTAUSLOESUNG-BUDGET-EINZWECKIG — ein zweiter Grund nimmt der Reparatur Luft

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Die Selbstauslösung ist als Reparatur gebaut und hat ein Budget, das kein zweiter Grund mitbenutzen kann, ohne der Reparatur Luft zu nehmen.** `MAX_SELF_TRIGGERS = 3` gilt je Turn für **alle** Gründe zusammen; heute setzt genau ein Aufrufer den Merker, der Denkknoten nach einem Doppel-Fehlschlag. Kommt ein zweiter Grund hinzu — etwa eine Vertiefung, die in Dateien nachlesen will —, verbraucht er aus demselben Topf, und die Fehlerbehandlung fällt genau in den Turns aus, in denen viel nachzulesen war. Kein Defekt am Bestand, sondern eine Schranke, die vor dem zweiten Aufrufer eine Entscheidung braucht: getrennte Zähler je Grund oder ein gemeinsamer mit Vorrang. **Nachtrag vom selben Tag — das Budget war die halbe Diagnose, geteilt ist auch das Tor.** Die Lückensuche in `graph/nodes/gespraechsvektor.py` läuft nur bei `aufnahmebereitschaft > 0`; die Zulassung der Selbstauslösung in `services/event_consumer.py` kennt nur den Zähler und einen Riegel auf wartende Agenten — **die Bereitschaft fragt sie nicht**, und bei Krise steht die auf 0,00. Heute ist das richtig, weil der einzige Aufrufer die Reparatur ist und **eine Reparatur in der Krise feuern muss**. Für einen zweiten Grund kehrt sich das um: Eine Vertiefung, die *„lass mich das nachlesen"* ankündigt, ist im Absturz genau das Falsche. **Dieselbe Schranke, die für die Reparatur zu eng wäre, ist für die Vertiefung notwendig** — der Riegel muss deshalb am Grund hängen, nicht am Mechanismus.

**Was fertig waere:** Das Budget der Selbstausloesung traegt mehr als einen Grund, ohne die Reparatur zu verdraengen.

**Prioritaet:** mittel

#### ZUSTELLART-EINWERTIG — auf Anfrage UND periodisch geht nicht

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Die Zustellart eines Dienstes ist einwertig und kann einen Dienst nicht beschreiben, der auf Anfrage UND periodisch arbeitet.** Sie wird aus `graph_eignung` und `periodic_task()` abgeleitet: Wer im Nutzergraphen zugelassen ist, gilt als am Empfang; wer eine periodische Aufgabe hat, als am Zeitplan. Ein Dienst, der beides legitim ist — erreichbar über seinen Aushang und zusätzlich mit eigenem Takt —, fällt durch: Die abgeleitete Zustellart ist für die halbe Arbeit falsch, und die Anmeldeprüfung verlangt daraufhin einen Aushang zu viel oder zu wenig. Aufgefallen beim Entwurf des Dateien-Dienstes (`novaberg-agent-dateien_k.md` §3), dort durch Aufteilung in zwei Dienste umgangen — **umgangen, nicht gelöst.**

**Was fertig waere:** Die Zustellart eines Dienstes kann mehrwertig sein.

**Prioritaet:** niedrig

#### AGENT-MD-MIT-STELLWERTEN — ein Einzelfall ohne Entscheidung

**Befund (16.08.2026), aus der Fundliste uebernommen.** **Ein `AGENT.md` mit Stellwerten ist ein Einzelfall, und niemand hat entschieden, ob er einer bleiben soll.** Von zwölf `AGENT.md` trägt genau **eines** einen `## Config`-Abschnitt (`recherche`). Der Charakter-Agent führt an seiner Aufrufstelle ein `timeout_s: 1800` und dokumentiert es dort **nicht**. Damit ist beim Nachzug einer Konfigurationsänderung nicht entscheidbar, ob das Moduldokument sie aufnehmen muss — die Frage ist eine Absicht und steht offen. Aufgekommen, als die neue Frist der Zwischen-Destillation in `novaberg-pixie-research.md` §7 nachgezogen wurde und in `AGENT.md` nicht.

**Was fertig waere:** Entschieden ist, ob ein `AGENT.md` Stellwerte traegt; die Bestandsdateien folgen der Entscheidung.

**Prioritaet:** niedrig

#### ENDPUNKTE-OHNE-BEDINGUNGEN — 19 von 19 ohne Vor- und Nachbedingung

**Befund (16.08.2026), aus der Fundliste uebernommen.** **19 von 19 HTTP-Endpunkten sagen weder Vor- noch Nachbedingung.** Gezählt über 315 Funktionen, die an einer Vertrauensgrenze stehen — Routen-Dekorator, Modellantwort, `fetchone`/`execute`, Redis-Zugriff, `open`/`json.loads`. **241 davon (77 %) tragen keine Zusicherung.** Die Endpunkte sind die exponierteste Klasse und zugleich die einzige bei 100 %. Dass eine Funktion privat ist, sagt nichts über ihr Risiko: **66 der 315 sind privat**, darunter `_kzg_laden` (Redis), `_ergebnis_speichern` (Datenbank), `_speichen_lesen` (Datei).

**Was fertig waere:** Jeder HTTP-Endpunkt nennt Vor- und Nachbedingung.

**Prioritaet:** mittel

#### PRIVATE-MEMBER-OHNE-ZUSICHERUNG — 276 von 461

**Befund (16.08.2026), aus der Fundliste uebernommen.** **276 von 461 privaten Membern haben weder Zusicherung noch Zeugen.** 13 % tragen beides, 17 % nur eine Zusicherung, 11 % nur einen Test. Für die übrigen 60 % sagt nichts, was sie voraussetzen, und nichts, dass sie tun, was sie behaupten. Die Zahl ist eine **Untergrenze**: Ein Name gilt schon als getestet, wenn er in einer Testdatei vorkommt.

**Was fertig waere:** Jedes private Member traegt Zusicherung oder Zeugen.

**Prioritaet:** niedrig

#### FUNKTIONEN-ZU-TIEF-VERSCHACHTELT — 19 tiefer als vier Ebenen

**Befund (16.08.2026), aus der Fundliste uebernommen.** **19 Funktionen verschachteln tiefer als vier Ebenen.** Spitzenwerte: `ei/dreischicht.py:gv_output_parsen` mit 9, `agents/charakter/agent.py:invoke` und `agents/charakter_identitaet/crud.py:ausfuehren` mit je 8. Die kleinste der Bestandsmengen und damit der erste Kandidat für eine Leerung.

**Was fertig waere:** Keine Funktion verschachtelt tiefer als vier Ebenen.

**Prioritaet:** niedrig

#### KLASSEN-OHNE-GEMEINSAMES-FELD — 10 zerfallen in Methodengruppen

**Befund (16.08.2026), aus der Fundliste uebernommen.** **10 Klassen zerfallen in Methodengruppen ohne gemeinsames Feld.** Gemessen über LCOM4 an 118 Produktivklassen. `plugins/notizen_manager/manager.py:NotizenManager` trägt alle Signale gleichzeitig: LCOM4 5, zehn öffentliche Methoden, elf Felder. **Die Zeilenzahl trennt dabei nicht** — von den Klassen über 300 Zeilen zerfallen 27 %, von denen darunter 26 %; `utils/zeitparser.py:MarkerBefund` hat 35 Zeilen und LCOM4 2.

**Was fertig waere:** Jede Klasse haelt ihre Methoden ueber ein gemeinsames Feld zusammen, oder sie wird geteilt.

**Prioritaet:** niedrig

#### KANALZWANG-NUR-22-PROZENT-PRUEFBAR — statisch kaum pruefbar

**Befund (16.08.2026), aus der Fundliste uebernommen.** **Der Kanalzwang ist statisch nur zu 22 % prüfbar.** Über 19 Knoten gezählt: **45 von 53 Rückgaben** bauen ihr Dict schrittweise auf oder geben es aus einer Hilfsfunktion zurück; dort existiert der Schlüssel zur Analysezeit nicht. Seit dem 16.08.2026 prüft `zustand_verifizieren()` zur Laufzeit — bisher nur im Reducer, die übrigen 18 Knoten sind offen.

**Was fertig waere:** Der Kanalzwang ist maschinell pruefbar, oder der unpruefbare Rest ist beziffert und benannt.

**Prioritaet:** mittel

#### NODE-LLM-CONFIG-RECHERCHE-OHNE-RUFER — gefuellt, null Aufrufer

**Befund (16.08.2026), aus der Fundliste uebernommen.** **`NODE_LLM_CONFIG["recherche"]` ist vollständig gefüllt und hat null Aufrufer.** `temperature` 0.5 und `max_output_tokens` 2048 stehen dort seit langem; `get_node_config("recherche")` wird nirgends im Produktivcode gerufen, und die zehn Aufrufstellen des RechercheAgent trugen ihre Werte fest im Code. Gefunden beim Anlegen von `recherche_zwischen` — die naheliegende Handlung wäre gewesen, den vorhandenen Schlüssel zu benutzen, und sie hätte die Temperatur von 0.1 auf 0.5 verschoben, ohne dass jemand es gemerkt hätte. Dieselbe Klasse wie `SELBSTAUSKUNFT-OHNE-LESER`, nur an einer Konfiguration statt an einer Selbstbeschreibung: **Eine Konfiguration ohne Leser sieht in jedem Wertetest richtig aus.**

**Was fertig waere:** Der Eintrag hat einen Aufrufer oder ist entfernt.

**Prioritaet:** niedrig

#### ERLEDIGT-MARKE-STATT-STICHWORTLISTE — die Liste wird nie fertig

**Befund (16.08.2026), aus der Fundliste uebernommen.** **Eine Stichwortliste für „als erledigt geführt" wird nie fertig — und die Marke, die trüge, gibt es längst.** Der Erledigt-Filter des Bezeichner-Kriteriums erkannte `~~`, *entfallen*, *widerlegt*, *deprecated*, *nicht mehr*, *existiert nicht*, *nie gebaut*. Beim Abarbeiten der beschreibenden Befunde kamen an einem Tag **sechs weitere Formulierungen** aus dem echten Bestand hinzu: *verworfen*, *archiviert*, *nie existiert*, *die es nicht gibt*, *wurde entfernt*, *noch nicht in `config.py`*, *ersetzt `X`* — dazu die Wortstellung (*„Es gibt keine …"* gegen *„gibt es keine"*) und die Zeilengrenze, weil ein Satz über drei Zeilen die Marke vom Namen trennt. Drei Ergänzungen sind gemacht, danach abgebrochen: **Der Ertrag je Patch sinkt, die Gefahr steigt** — jedes Wort mehr macht echte Befunde unsichtbar, und ein Gerät, das zu wenig meldet, fällt nicht auf. **Der strukturelle Ausweg steht schon im Filter:** `~~` ist eine eindeutige, prüfbare Marke. Die Dokumente benutzen sie nur uneinheitlich. Entweder wird sie zur Konvention für ausgemusterte Bezeichner, oder die Falschmelderate wird beziffert und mitgeführt — heute **6 von 6** verbliebenen Treffern der Klasse `beschreibend`.

**Was fertig waere:** Die vorhandene Marke traegt die Erkennung; die Stichwortliste entfaellt.

**Prioritaet:** niedrig

#### RUECKWEG-UEBER-DEN-MENSCHEN-OHNE-RIEGEL — in keinem Riegel abgebildet

**Befund (15.08.2026), aus der Fundliste uebernommen.** **Der Rueckweg ueber den Menschen ist in keinem Riegel abgebildet.** Gemessen am 14.08.2026 turngenau: Ein Einwurf hebt ihre Antwortdichte auf 8,40 %, und neun Minuten spaeter kommt die Aeusserung des Menschen mit **10,99 %** auf 91 Zeichen zurueck — er hat das Vokabular des Einwurfs uebernommen. Die sieben Riegel pruefen alle, **ob** ein Gedanke hinausgeht; keiner prueft, was er unterwegs mit dem Gespraech macht.

**Was fertig waere:** Der Rueckweg ueber den Menschen ist in einem Riegel abgebildet.

**Prioritaet:** mittel

#### VERLAUF-REPRODUZIERT-EIGENE-WENDUNGEN — niemand bremst das

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Der Verlauf reproduziert seine eigenen Wendungen, und niemand bremst das.** Vierzehn stündliche Impulse eines Tages: fünf begannen wortgleich mit *„Du hast den Anker geworfen. Indem du diesen Block …"*, weitere sieben mit einer Variante desselben Baumusters. Der Mechanismus ist geschlossen: Jeder Beitrag wandert in die Session, der nächste Prompt trägt ihn, das Muster wird bestätigt. Gemessen am Verfasser-Prompt desselben Tages: **22.545 Zeichen Verlauf aus 18 eigenen Beiträgen gegen 1.195 Zeichen Auftrag**; beim Responder ist das Verhältnis besser, aber derselbe Verlauf steht dort ebenfalls. Der Regieblock schreibt seit Chat 114 ausdrücklich dagegen an (*„löse dich von seiner Art zu sprechen"*) — gegen fünf wortgleiche Belege hat er nicht getragen. **Zu klären ist nicht, ob der Verlauf hineingehört, sondern wieviel davon:** Der Verfasser braucht ihn für den Anschluss, der Responder bekommt den Anschluss bereits fertig als `[INHALT]`.

**Was fertig waere:** Die Wiederholung eigener Wendungen ist gemessen und gebremst.

**Prioritaet:** mittel

#### SCHWELLEN-OHNE-VERGLEICHSGEGENSTAND — zehn Schwellen, keine nennt ihn

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Zehn Ähnlichkeits-Schwellen, und keine nennt, was sie vergleicht.** Der Bestand führt zehn Schwellen über Embedding-Kosinus zwischen 0,40 und 0,95 — Bibliotheks-Abruf, Zustellung, Dublettenschutz, Ziel- und Erinnerungs-Gravitation, Charakter-Resonanz, KZG, Delegation, LZG-Knoten, Lücken-Dublette. **Fünf davon stehen auf exakt 0,40, über mindestens vier verschiedene Paarungen.** Das sieht aus wie eine gemeinsame Kalibrierung und ist keine. **Die Herkunft steht überall vorbildlich dabei** — *„begründeter Startwert, kein Messergebnis"*, *„an drei Zeilen ist nichts kalibrierbar"*, bei den LZG-Knoten sogar die Gegenmessung. **Die Paarung steht nirgends**, und ohne sie ist die Herkunft nicht nachprüfbar: Eine an Themenphrasen gemessene Schwelle sagt über Volltexte nichts, auch wenn dieselbe Zahl dasteht. Gemessen am 14.08.2026 an derselben Rechnung: Themenphrase gegen Themenphrase trennt (0,437–0,896), Volltext gegen Volltext misst die Textsorte (Median 0,557), Volltext gegen kurze Äußerung trennt schwach (Median 0,105). **Kein Aufräum-Auftrag** — die zehn sind Bestand; wer eine davon anfasst, schreibt ihre Paarung dazu.

**Was fertig waere:** Jede Aehnlichkeitsschwelle nennt, was sie vergleicht.

**Prioritaet:** mittel

#### CHARAKTER-BESCHAEDIGT-INHALT — niemand prueft es

**Befund (13.08.2026), aus der Fundliste uebernommen.** **Der Charakter kann den Inhalt beschädigen, und niemand prüft es.** Eine Figur mit förmlichem Stil schreibt Zahlen aus — und dabei wurde aus 1400 Lichtjahren dreimal *„vierzehntausend"*. Gemessen über 27 Läufe: In der knappsten Landschaft schrieb dieselbe Figur 6 Zahlen aus und verfälschte 3 von 3 Läufen; von drei Inhaltsmarken des Verfassers kamen dort nur 1,0 korrekt an, während dieselbe Figur in einer Landschaft ohne Ausschreib-Zwang 3,0 von 3 lieferte. **Der Verfasser liefert die Fakten, der Responder formt sie — und die Umformung ist heute ungeprüft.** Die Marken sind maschinell prüfbar, solange sie als Ziffern im Inhalt stehen.

**Was fertig waere:** Eine Pruefung haelt den Inhalt gegen die Charakterfaerbung.

**Prioritaet:** hoch

#### BEITRAGSTABELLE-SCHLIESST-KOMBINATION-AUS — treu und distanziert geht nicht

**Befund (13.08.2026), aus der Fundliste uebernommen.** **Ein treuer, aufmerksamer Diener kann nicht distanziert sein — die Beitragstabelle lässt es nicht zu.** `treue` trägt `naehe +0,20`, `aufmerksamkeit` ebenfalls `+0,20`, `wohlwollen` `+0,10`; zusammen +0,45 bei hoher Ausprägung, gegen `distanz −0,50`. Eine Figur, die pflichtbewusst, verlässlich und aufmerksam **und** höflich distanziert ist, landet im `feuerwerk` bei `naehe 0,82` — praktisch auf dem Grundwert der Landschaft. Gemessen: Unter dieser Haltung wurde ein solcher Charakter dreimal von drei von einem blinden Prüfer als Nova gelesen. **Es ist dieselbe Verrechnung, die `novaberg-haltungsraum_k.md` §3.2 für Misstrauen gegen Wohlwollen ausdrücklich verbietet** — dort wurde sie am 11.08. behoben, hier steht sie unbemerkt ein zweites Mal. Die Frage dahinter ist konzeptionell: Trägt `treue` Nähe, oder trägt sie Verlässlichkeit? Ein Butler ist der Gegenbeweis.

**Was fertig waere:** Die Beitragstabelle laesst jede fachlich moegliche Kombination zu.

**Prioritaet:** mittel

#### CLUSTER-BESCHREIBUNG-MISCHT-BEFEHL — Szene und Regieanweisung in einem Feld

**Befund (12.08.2026), aus der Fundliste uebernommen.** `CLUSTER_BESCHREIBUNGEN` mischt **Szene und Regieanweisung** in einem Feld. Vier der vierzehn tragen einen Befehl: `regen` „Halten, da sein", `schmollen` „Nicht drängen", `nebel` „Leise da sein", `gewitter` „Nicht verteidigen". Der Befehl gilt für jeden Charakter gleich und steht **vor** dem Rad — die Haltungsgrößen können ihn nicht bewegen. Dieselbe Drift in `CLUSTER_FRAGEN`, das reine Verhaltensvorgabe ist („Häufig, begeistert") und aus derselben Quelle stammt wie die Rad-Größe `fragen`. **Zwei Leser, zwei Aufgaben:** Der GV-Knoten braucht die Fragen-Zeile für die Strategiewahl, der Responder nicht.

**Was fertig waere:** Szene und Regieanweisung stehen in getrennten Feldern.

**Prioritaet:** mittel

---
#### BEISPIELE-OHNE-HERKUNFTSMARKE — 9 von 150 Dokumenten sagen, woher ihr Beispiel stammt

**Befund (16.08.2026), aus der Fundliste uebernommen.** **9 von 150 Dokumenten unter `docs/` tragen eine Herkunftsmarke an ihren Beispielen.** Gezählt über das Wortfeld *synthetisch* / *konstruiertes Beispiel* / *konstruierter Turn*. Betroffen ist jedes Dokument, das einen wörtlichen Beispiel-Turn führt: `novaberg-referenz-aufloesung_k.md` §1 trägt drei (Matcha-Pulver, Grillkäse, eine Notiz namens `Einkauf`), `novaberg-haltungsraum_k.md` §1 einen (der Igel-Einzeiler) — keines der beiden Dokumente sagt, ob die Reize echt oder konstruiert sind. **Für den Igel ist die Frage seit dem 31.07.2026 entschieden** (synthetisch), nur steht die Entscheidung nicht im Dokument; sie wurde am 16.08.2026 erneut aufgeworfen. Kein Defekt am System — die Kosten fallen bei jeder Veröffentlichungsprüfung erneut an, und ein Beispiel ohne Vermerk ist von einem echten Gesprächsinhalt nicht unterscheidbar.

**Was fertig waere:** Jedes Beispiel in `docs/` traegt eine Herkunftsmarke — synthetisch oder echt. Ohne sie wird dieselbe Stelle bei jeder Veroeffentlichungspruefung neu verhandelt.

**Prioritaet:** niedrig.

---

## 0c. Aus der Fundliste klassifiziert — Chat 133 (08.08.2026)

Sieben Einträge der Fundliste waren offene Arbeit: abschließbar, in unserem Code, und mit einer Antwort auf die Prüffrage *welche Arbeit wäre fertig, wenn der Eintrag geschlossen wird*. Drei davon sind Nähte ohne Prüfung, zwei sind Aussagen über den Zustand, die veraltet sind, und zwei sind Rechnungen ohne Abnehmer.

#### KOPPLUNG-FRAGENSPALTE-UNGEPRUEFT — eine Tabelle ist aus einer zweiten übersetzt, und nichts hält sie zusammen

Die Spalte `fragen` in `CLUSTER_GRUNDWERT` (`server/ei/haltung.py`) ist keine eigene Setzung, sondern eine Übersetzung von `CLUSTER_FRAGEN` (`server/ei/dreischicht.py`): „Häufig, begeistert" wird zu 0,90, „Keine" zu 0,00. Der Kommentar sagt es — *„Wer dort etwas ändert, ändert hier mit"* —, aber **kein Test erzwingt die Kopplung**, und die beiden Tabellen stehen in verschiedenen Modulen mit verschiedenen Wertetypen: Text gegen Zahl.

Eine Änderung an der Fragefrequenz einer Landschaft schlägt damit auf die Prompt-Seite durch und auf die Haltungsrechnung nicht. Dieselbe Naht trägt beide Enden der Dreischicht: `CLUSTER_FRAGEN` geht in den GV-Prompt und in den Sprachstil-Block des Responders, `CLUSTER_GRUNDWERT` in die fünf Verhaltensgrößen.

**Was fertig wäre:** ein Test, der beide Tabellen gegeneinander hält — Textstufe zu Zahlenwert, über alle vierzehn Landschaften. Der bestehende `test_die_fragenspalte_folgt_dem_bestand` prüft nur die Null-Richtung.

**Priorität:** mittel. Der Bestand ist heute stimmig; der Defekt entsteht bei der nächsten Änderung und ist dann still.

#### EINWANDSURTEIL-OHNE-LESER — eine Rechnung, deren Ergebnis nirgends ankommt

Der Verfasser schreibt den Kanal `einwandsurteil`, `graph/state.py` deklariert ihn, `graph/base.py` und `graph/builder.py` legen ihn beim Zustandsaufbau an. **Ein Verbraucher existiert nicht.**

Dieselbe Klasse wie die Haltung, deren fehlender Abnehmer in `novaberg-graph-rechenkette.md` S26 ausdrücklich als „Beitrag: heute keiner" steht — hier steht es nirgends. Eine Rechnung, deren Ergebnis nirgends ankommt, ist von einer wirksamen nicht zu unterscheiden, solange niemand die Kanäle zählt.

**Was fertig wäre:** entweder der Anschluss an einen Leser, oder der Vermerk „Beitrag: heute keiner" am Erzeuger — mit dem Grund, warum die Rechnung trotzdem läuft.

**Priorität:** niedrig. Kostet nichts außer Rechenzeit; teuer wird es erst, wenn jemand das Feld für wirksam hält.

#### KANAELE-OHNE-VERTRAG — vier Kanäle des Zustands ohne beidseitige Zusage

Über 63 deklarierte Kanäle des `ConversationState` mechanisch geprüft: `memory_entries_raw`, `system_prompt` und `timeline_id` haben **weder Schreiber noch Leser** — sie existieren nur im Schema. Und **`response` hat vier Schreiber** (`responder.py`, `thinker.py`, `corrector.py`, `character_graph.py`), `pending_writes` drei, fünf weitere je zwei. Mehrere Erzeuger für eine Größe sind die Klasse, die auseinanderläuft.

**Die Prüfung hat zwei benannte blinde Flecken:** Sie sieht den Erzeugungspfad in `create_state` nicht — daher 15 Falschmeldungen „gelesen, nie geschrieben" — und keine Verbraucher außerhalb von `graph/` und `services/`; so fiel `such_vektor` zu Unrecht auf, den ein Plugin liest.

**Was fertig wäre:** die Prüfung als wiederholbares Werkzeug, mit beiden blinden Flecken einmal beschrieben statt jedes Mal neu — und danach die Zahl, die heute fehlt: 63 Kanäle, davon *n* mit geprüftem Vertrag auf beiden Seiten.

**Priorität:** hoch. Ohne die Zahl ist jede Aussage über die Zuverlässigkeit der Kette ein Eindruck.

#### GV-SKIP-TOTE-AUSLOESER — eine dreiteilige Bedingung, die einteilig wirkt

`_ist_skip()` überspringt bei `intent` in `("begruessung", "meta", "system")`. Über 845 Rohturns kommt `begruessung` **null** mal vor und `system` **null** mal; das Feld trägt `personal` (321), `knowledge` (248), `meta` (88), `smalltalk` (77), `task` (59), `creative` (32), `philosophischer_austausch` (17), `berichtend` (3). **Wirksam ist allein `meta`.**

Ein Zweig, der auf einen Wert wartet, den niemand schreibt, ist von einem Zweig ohne Wirkung nicht zu unterscheiden — und die Bedingung sieht dreiteilig aus, während sie einteilig ist.

**Was fertig wäre:** die Entscheidung, ob die Perzeption die beiden Werte liefern **soll** (dann fehlt sie dort) oder nicht (dann sind die beiden Zweige zu entfernen) — und die Umsetzung der einen oder anderen Seite.

**Priorität:** niedrig als Defekt, mittel als Irreführung. Der Zweig kostet nichts und behauptet etwas.

#### RESPONDER-KOMMENTAR-FALSCHE-SCHICHT — ein Kommentar nennt die falsche Gedächtnisschicht

Die Zeile lautet `# Bild vom Nutzer (beziehungsprofil aus LZG-Destillation)`; der Erzeuger ruft `beziehungsprofil_destillieren(kzg_eintraege)`. Die drei Nachbarzeilen darüber stimmen — `adaptive` aus KZG, `emotions_profil` und `intentions_profil` aus LZG —, und genau das macht die falsche unauffällig: **Sie steht in einer Reihe richtiger Angaben, an der Stelle, an der jemand nachsieht, um die Herkunft zu klären.**

Ein Kommentar, der die Quelle eines Wertes benennt, ist eine Zustandsaussage und veraltet wie jede andere.

**Was fertig wäre:** die Zeile korrigieren.

**Priorität:** niedrig im Aufwand, mittel in der Wirkung — sie ist genau die Zeile, die bei der nächsten Suche nach „warum ist das Profil leer" gelesen wird.

#### PROFILE-LEER-URSACHE-UNBEKANNT — die bisherige Begründung ist am Bestand widerlegt

**Der Erstbefund vom 06.08.2026, aus dem dieser Eintrag entstand:** Gemessen an `charakter_hash` tragen für alle sechs Personas und in **beiden** Richtungen `kern_hash`, `intentions_profil` und `emotions_profil` null Zeichen; gefüllt sind allein `adaptive_hash` (KZG) und `beziehungsprofil` (KZG). Die damals notierte Ursache — alle drei leeren lesen `lzg_knoten`, und eine frische Persona hat kein Langzeitgedächtnis — ist zwei Tage später am Bestand widerlegt worden; sie steht hier, weil sie erklärt, warum zwei Monate lang niemand weitergesucht hat.

Backlog und Chronik führen als Grund für die drei leeren Profile, alle drei läsen `lzg_knoten` „und eine frische Persona hat kein Langzeitgedächtnis". Am Bestand gemessen: **`konrad` trägt 82 Knoten, `leon` 38** — beide entstanden während ihrer Bögen am 02.08.2026; die übrigen vier tragen keinen einzigen.

Die Begründung stimmt für vier von sechs Personas und stand als **allgemeine** Erklärung da. Die Profile waren leer, aber die Ursache ist damit unbekannt und braucht eine eigene Messung.

> **Die Form ist die teure:** eine plausible Erklärung, die zwei Monate lang niemand gegen den Bestand geprüft hat, weil sie zu allem passte, was man sah.

**Was fertig wäre:** die Ursache für die beiden Personas **mit** Langzeitgedächtnis bestimmen. Erster Ort zum Nachsehen ist `PROMOTION-FENSTER-LAEUFT-AB-STATT-LEER` in `novaberg-bugs.md` — dort steht, warum der Knotenstand einer Persona ausgewürfelt ist.

**Priorität:** mittel. Betrifft die Aussagekraft jeder Charakterbildungs-Messung.

#### CHARAKTER-HASH-DOKU-FALSCHE-QUELLE — das Dokument nennt eine Quelle, die der Code nicht liest

`novaberg-pixie-character-hash.md` §3.3 und §3.4 führen für das Intentions-Profil *„Aggregiert aus Session-Annotationen (Intentionen + Modus + Stil)"* und für das Emotions-Profil eine Grundtendenz „über Monate". Im Code nehmen `intentions_profil_destillieren` und `emotions_profil_destillieren` beide `lzg_eintraege` als einziges Material und geben bei leerer Liste `""` zurück (`server/agents/charakter/destillation.py`).

**Wer nach §3.3 sucht, warum das Profil leer ist, sucht in den Session-Annotationen — und findet dort nichts Falsches.** Das ist die Sorte Doku-Fehler, die Suchzeit kostet statt Verhalten zu ändern.

**Was fertig wäre:** beide Abschnitte auf die tatsächliche Quelle ziehen, mit Datum und Vermerk, was vorher dastand.

**Priorität:** mittel. Hängt unmittelbar an `PROFILE-LEER-URSACHE-UNBEKANNT` — wer dort misst, liest zuerst dieses Dokument.

---

### Block 30.–27.07. — neun Einträge (08.08.2026)

Der aelteste Bestand. **Acht der neun sind Struktur statt Verhalten** — tote Zweige, doppelte Formen, ein Dokument ohne Abgleich. Der neunte, die Ungleichverteilung des Repertoires, ist der einzige, der eine Absicht braucht.

#### DOKU-MEHRDEUTIGE-ANKER

**Befund (2026-07-28).** Doku-Hygiene, **gemessen**: Drei Dokumente vergeben Überschriften mehrfach und erzeugen damit mehrdeutige Anker — `novaberg-backlog.md` (3× „Phasen-Übersicht", 3× „Hintergrund", 2× „Auswirkung auf Akten-Vision"), `novaberg-roadmap.md` (je 2× „Dokumentation", „Backlog", „Bugfixes") und `novaberg-thinking-skills_k.md` (2× „Wetter-Anfragen"). Ein Zähler über alle `#`-Zeilen meldet zusätzlich `novaberg-memory-synapsen_k.md` mit 12 Treffern — das sind **Python-Kommentare in einem Code-Block**, kein Befund. Wer das nachmisst, muss Code-Fences überspringen.

**Was fertig waere.** Jede Ueberschrift ist in ihrem Dokument eindeutig.

**Prioritaet:** niedrig.

#### AGENT-MD-NIE-GEPRUEFT

**Befund (2026-07-28).** `server/agents/kzg/AGENT.md` ist nie gegen den Code geprüft worden. Der KZG-Agent hat seit der Erstfassung Nodes gewonnen und verloren (`magnete_aufloesen` kam, `aehnlichkeit_pruefen` ist gelöscht) — ob die AGENT.md das trägt, ist offen. Gilt sinngemäß für die übrigen AGENT.md-Dateien, die ebenfalls nie systematisch abgeglichen wurden.

**Was fertig waere.** Das Agentendokument ist gegen den Code gelesen und trifft zu.

**Prioritaet:** mittel.

#### SESSION-CONTEXT-BUILD-OHNE-AUFRUFER

**Befund (2026-07-28).** `memory/session.py:313` `session_context_build()` hat **keinen Aufrufer**. Sie setzt Zusammenfassung und Turns zu einem `[Aktuelle Unterhaltung]`-Block zusammen — genau die Aufgabe, die der Responder seit dem Verlaufs-Umbau selbst und in anderer Form erledigt (`graph/nodes/responder.py`, Turn-Paare unter `----- Turn n von m -----`). Gemessen repoweit über alle Dateitypen: **zwei** Treffer, beide Definition bzw. Re-Export (`memory/__init__.py:39`). Positivkontrolle auf dasselbe Muster mit `session_turns_retrieve`: 52 Treffer in 27 Dateien. Der Befund ist nicht der tote Code, sondern die Falle: Wer den Gesprächskontext nachvollziehen will, findet zuerst diese Funktion und liest eine Formatierung, die kein LLM mehr sieht. **Anhängend:** `SESSION_MAX_TURNS` (=20) wird ebenso exportiert, steht im Code aber an genau einer Stelle — dem `except`-Zweig von `session_summarize_if_needed` (`session.py:202`), also im Notpfad bei gescheitertem LLM-Call. Der reguläre Deckel heißt `SESSION_SUMMARIZE_AT` (=25). Der Name der exportierten Konstante behauptet, sie sei die Regel.

**Was fertig waere.** Die Funktion hat einen Aufrufer oder ist entfernt.

**Prioritaet:** niedrig.

#### EIGENIMPULSE-IN-DER-SCHWELLE

**Befund (2026-07-28).** Novas Eigen-Impulse zählen in die Zusammenfassungs-Schwelle, **erscheinen aber nie im Gesprächsverlauf**. Ein Impuls läuft durch den CharacterGraph; der Dispatcher schreibt dafür einen `assistant`-Session-Turn ohne `user`-Gegenstück. Beide Verlaufs-Bildner überspringen alleinstehende `assistant`-Turns: der Paar-Bildner im Responder (`graph/nodes/responder.py:672-674`) und `format_session_turns_numbered` (`memory/session.py:283-286`), das GV-Node, Router, Perzeption und vier Agenten-Klassifikationen lesen. *(Zeilennummern gemessen 28.07.2026.)* Gemessen am 28.07.2026, 20:15 UTC: `session:<user>:<character>:turns` = 20 Einträge, davon **12 `assistant` gegen 8 `user`**; der Responder-Prompt desselben Fensters trug 7 Turn-Paare. Vier Einträge zählen damit gegen `SESSION_SUMMARIZE_AT`, ohne je im Prompt gestanden zu haben — bei Erreichen der Schwelle schneiden sie echte Wortwechsel weg. Ob ein Impuls in den Verlauf gehört, ist eine offene Frage; dass er ihn verkürzt, ohne darin vorzukommen, ist keine.

**Was fertig waere.** Die Zusammenfassungs-Schwelle zaehlt, was sie zaehlen soll — und es steht dabei, was das ist.

**Prioritaet:** mittel.

#### REPERTOIRE-UNGLEICH-VERTEILT

**Befund (2026-07-29).** Die Repertoire-Matrix schließt keine Strategie global aus, verteilt sie aber stark ungleich — und der schiefste Punkt fällt mit dem häufigsten Zustand zusammen. Über alle 64 Sektoren und 14 Cluster gerechnet: Erreichbarkeit von **100 %** (`Bestaetigung`, nie `unpassend`) bis **28 %** (`Impuls`); im Mittel trägt ein Sektor **3,66 von 7** Strategien. Zwei Strukturbefunde daraus: **`Perspektivwechsel` ist in keinem der 14 Cluster Kernstrategie** (0× kern, 2× passt, 3× selten, 9× unpassend) — wählbar, aber nie das Werkzeug der Landschaft; und **`paradox` hat überhaupt keine Kernstrategie**, verfügbar sind dort nur `Sp` (passt), `Be` (passt), `Pr` (selten). `paradox` ist mit **14 von 64 Sektoren (21,9 %) der größte Raum**, das LLM bekommt dort einen `[WERKZEUGE]`-Block ohne ein einziges ★. Dazu Chat 114: Sektor **#37 „Fiebrige Heiterkeit" war über 45 Läufe der häufigste des Systems** — und #37 liegt in `paradox`. **Nicht gemessen ist die heutige Häufigkeit:** Der Container-Log deckt 11 Stunden und 9 Sektor-Zuweisungen ab, mehrere aus Probeläufen — keine Reihe; die 45-Läufe-Messung stammt von vor dem Raum-Umbau derselben Sitzung. Ob eine Landschaft ohne Kernstrategie vorgesehen ist, sagt das Konzept nicht (§10.1 regelt nur, dass der Cluster das Repertoire bestimmt und der Charakter darin gewichtet).

**Was fertig waere.** Die Ungleichverteilung ist als gewollt benannt, oder sie ist ausgeglichen.

**Prioritaet:** mittel.

#### NOTIZEN-ENRICH-16-ZWEIGE

**Befund (2026-07-30).** `plugins/notizen_manager/manager.py` `enrich_entries()` traegt **16 Verzweigungen und 67 Anweisungen** — mehr als jede der fuenf Funktionen, die an diesem Tag zerlegt wurden. Sie tauchte in der Liste der Zaehlregel-Funde nicht auf, weil sie im **Ueberlappungsbereich** von C901 und PLR0912 liegt: Wer nur die eigenstaendigen Treffer der einen Regel ansieht, uebersieht die groessten Faelle, weil die von beiden Regeln gemeldet werden. Der Fund ist nicht die Funktion, sondern die Auswahlmethode.

**Was fertig waere.** Die Funktion ist zerlegt.

**Prioritaet:** niedrig.

#### LLM-PROVIDER-ZWEIG-UNERREICHBAR

**Befund (2026-07-30).** `services/llm_provider.py`: Der defensive Zweig, der `message` als Dict *oder* Objekt behandelte, war **nie erreichbar**. Drei Zeilen darueber ruft die Token-Verbuchung `response.get(...)` — ein Objekt scheitert dort mit `AttributeError`, bevor die Absicherung greift. Beim Schreiben des Tests aufgefallen, nicht beim Lesen des Codes. Behoben: Der Typ ist jetzt festgelegt, ein Vertragsbruch kracht laut.

**Was fertig waere.** Der nie erreichbare Zweig ist entfernt oder erreichbar.

**Prioritaet:** niedrig.

#### FUENF-STELLEN-FORM-MEHRFACH

**Befund (2026-07-30).** Fünf Stellen schreiben eine Form mehrfach hin, statt sie einmal zu benennen. Alle fünf sind über die Verzweigungsregel des Linters aufgefallen und einzeln gelesen; keine ist ein Defekt, alle fünf sind Struktur. **Der gemeinsame Nenner ist die Wiederholung, nicht die Kompliziertheit** — die Verzweigungszahl ist bei diesen fünf kein Ausdruck von Sachkomplexität, sondern von einem zweimal hingeschriebenen Muster.

**Was fertig waere.** Die Form steht einmal und wird benannt verwendet.

**Prioritaet:** niedrig.

#### LOGGING-PROZENT-STATT-FSTRING

**Befund (2026-07-30).** **65 Logging-Aufrufe formatieren über `%`-Platzhalter mit Argumenten** statt über den vorgeschriebenen f-String, zum Beispiel `logger.info("… %s", basis_top)` in `graph/nodes/ei_calc.py:252` und `logger.exception("%s: kanten_alle_loeschen fehlgeschlagen", type(exc).__name__)` in `memory/lzg_kanten.py:512`. Zum Vergleich am selben Bestand gezählt: **538** Aufrufe mit f-String. Die Stellen verteilen sich über den Baum, sie sind kein Nest in einer Datei. Berührt die Begründung, mit der `G004` in der Linter-Konfiguration abgeschaltet ist — dort steht, f-Strings seien im Logging *vorgeschrieben*, was für 65 Stellen so nicht zutrifft. *(Zeilennummern gemessen 30.07.2026.)*

**Was fertig waere.** Alle Aufrufe folgen der vorgeschriebenen Form, oder die Vorschrift nennt beide.

**Prioritaet:** niedrig.

---

### Block 31.07., Nachtrag (08.08.2026)

#### PROMPT-DOPPELTE-FORMULIERUNG

**Befund (2026-07-31).** `_ei_mikro_anweisung()` Punkt 7 und der `[KOMMUNIKATION]`-Block in `graph/nodes/responder.py` bilden beide dieselben fünf Werte auf Text ab, die Mikro-Fassung jeweils etwas länger: *„Der Nutzer haelt Distanz. Sachlich bleiben, nicht aufdraengen."* gegen *„Der Nutzer haelt Distanz. Sachlich bleiben."* Bei allen fünf Werten dasselbe Muster. Zwei Formulierungen derselben Größe im selben Prompt kosten Kontext und lassen offen, welche gilt.

**Herkunft des Eintrags.** Er stand in der Fundliste **im selben Aufzählungspunkt** wie ein Fremddefekt zu LangGraph — zwei Funde unter einem Datum, in einer Zeile. Beim Klassifizieren am 08.08.2026 wanderte er dadurch zunächst mit an einen Ort für Fremddefekte und wurde erst beim Nachlesen getrennt. **Ein Aufzählungspunkt mit zwei Funden wird einmal gezählt und einmal klassifiziert** — der zweite Fund verschwindet lautlos in der Sorte des ersten.

**Was fertig waere.** Eine der beiden Formulierungen bleibt, oder beide sind ausdrücklich als verschiedene Größen benannt.

**Prioritaet:** niedrig im Aufwand — sie kosten Kontext und lassen offen, welche gilt.

---

### Block 31.07. — fünf Einträge (08.08.2026)

Vier Doku- und Namensfunde, einer davon eine offene Prüfung am Initiative-Rad.

#### GRAPH-TABELLE-OHNE-VERFASSER

**Befund (2026-07-31).** Die Node-Tabelle in `novaberg-graph.md` §3 kennt den **Verfasser nicht**. Sie führt siebzehn Knoten und geht von `GV-Node` direkt zu `Responder`; der Verfasser existiert im Code seit dem Responder-Umbau. Wer die Tabelle liest, hält den Umbau für nicht gebaut.

**Was fertig waere.** Die Tabelle fuehrt alle Knoten des heutigen Graphen.

**Prioritaet:** mittel.

#### INITIATIVE-RAD-GEGENPOL-UNGEPRUEFT

**Befund (2026-07-31).** Das **Initiative-Rad** steht vor derselben Frage wie das Zuwendungs-Rad, und sie ist dort ungeprüft: Seine zehn Speichen (`INITIATIVE_ZUG_HOCH` / `INITIATIVE_ZUG_RUNTER`) stehen in der Reihenfolge ihrer Aufzählung, nicht in einer Gegenpol-Anordnung. Solange nur der Skalar gerechnet wird, ist das folgenlos; sobald aus ihnen ein Punkt gebildet wird, entscheidet die Ordnung, welche zwei Eigenschaften einander auslöschen. `F-RAD-1` gilt heute nur für das Zuwendungs-Rad.

**Was fertig waere.** Es ist geprueft, ob die zehn Speichen des Initiative-Rades eine Gegenpol-Anordnung tragen — und wenn ja, haelt ein Test sie wie bei den Charakter-Raedern.

**Prioritaet:** mittel.

#### CLUSTERZAHL-13-GEGEN-14

**Befund (2026-07-31).** `novaberg-gv-strategie_k.md` nennt **13 Cluster**, `CLUSTER_BESCHREIBUNGEN` in `ei/dreischicht.py` enthält **14**: feuerwerk, kissenschlacht, werkstatt, glut, bier, foyer, regen, schmollen, nebel, gewitter, schlachtfeld, beichte, wartezimmer, paradox. Eine Zahl, die in der Kopfzeile eines Konzepts steht und im Code anders lautet, wird bei jeder Ableitung daraus falsch mitgerechnet.

**Was fertig waere.** Konzept und Code nennen dieselbe Zahl.

**Prioritaet:** niedrig.

#### GV-DETAIL-LAENGE-IRREFUEHREND

**Befund (2026-07-31).** `gv_detail["laenge"]` heißt wie eine Antwortlänge und ist die **Vektorlänge**: die Zahl der Antizipationsschritte aus `_vektor_laenge_berechnen`, hart auf 3 gedeckelt (Cognitive Load Theory). Wer beim Bauen einer Umfangsregel darauf aufsetzt, rechnet auf einem Wert, der für etwas anderes erhoben wurde — dieselbe Fehlerklasse wie eine Schwelle aus einer anderen Größe.

**Was fertig waere.** Der Schluessel heisst, was er traegt.

**Prioritaet:** niedrig.

#### BILD-VERWAIST

**Befund (2026-07-31).** **`images/nova-ui-emotion-1.png` ist verwaist**, seit die README auf die neuere Aufnahme zeigt. Es zeigt die Emotionswerte des Nutzers unter einer Bildunterschrift, die Novas Zustand behauptete — der Widerspruch bestand seit April. Ebenfalls verwaist, aber älter: `images/nova-ui-memory-change-1.png` vom 15.05.2026, von keiner Fassung eingebunden. Löschen ist nicht entschieden.

**Was fertig waere.** Das verwaiste Bild ist entfernt oder wieder eingebunden.

**Prioritaet:** niedrig.

---

### Block 01.08. — vier Einträge (08.08.2026)

#### LLM-LOCK-SCHUETZT-DIE-GPU-NICHT-DEN-TURN

**Befund (2026-08-01).** **Der `llm_lock` schützt die GPU, nicht den Turn — und der Modell-Worker hat einen eigenen Riegel dahinter.** Gemessen beim Umbau der Eingangs-Queue: Ein zweiter Durchlauf, der den `llm_lock` bekam, lief trotzdem in den 60-Sekunden-Timeout des Modell-Workers, weil dessen Warteschlange noch belegt war. Wer den Riegel hält, hat also noch keine Rechenzeit. Für den Prompt-Pfad ist das mit dem Turn-Marker entschärft; für jeden anderen Aufrufer besteht es fort, und die Zahl der Fälle ist nicht erhoben.

**Was fertig waere.** Es ist entschieden und aufgeschrieben, welcher der beiden Riegel den Turn schuetzt — und der andere ist entweder entfernt oder als das benannt, was er tut.

**Prioritaet:** mittel.

#### CLIENT-OHNE-TESTLAUF

**Befund (2026-08-01).** **Der Client hat keinen Testlauf, und die Zuordnungsprüfung liegt vollständig in ihm.** `_zuordnung_pruefen` in `client/ui/stream_handler.py` entscheidet über drei Ausgänge und ist die einzige Stelle, an der eine falsch zugeordnete Antwort auffällt — geprüft ist sie nur am laufenden Client, nicht von der Suite. Das Server-Abbild kann `client/` weder importieren (GTK-Abhängigkeiten) noch sehen (nicht gemountet). Derselbe blinde Fleck wie beim Impuls-Zweig, diesmal an einer Stelle mit Verzweigungslogik.

**Was fertig waere.** Die Zuordnungspruefung hat einen Test, der ohne laufenden Client rot wird.

**Prioritaet:** hoch. Sie ist die einzige Stelle, an der eine falsch zugeordnete Antwort auffaellt.

#### RAD-STABILITAET-UNGEMESSEN

**Befund (2026-08-01).** Das **Zuwendungs-Rad wird einmal erhoben**, ohne Median und ohne Streuungsmaß — anders als das Initiative-Rad, das dreimal läuft und den Median nimmt. Solange seine Schwankung nicht miterhoben wird, ist an keinem daraus abgeleiteten Wert erkennbar, ob eine Änderung Bewegung im Charakter oder Streuung des Verfahrens ist. (Verschärft den Fund vom 30.07. zur fehlenden Unsicherheit desselben Rades: die Schwankung ist jetzt beziffert.)

**Was fertig waere.** Das Zuwendungs-Rad wird wie das Initiative-Rad mehrfach erhoben, mit Median und Streuungsmass.

**Band A** (Rangordnung, Reihe 2) — und **vor** jeder Kalibrierung der Beitragsverhaeltnisse — wer gegen eine Groesse justiert, deren eigene Streuung er nicht kennt, justiert gegen Rauschen.

---

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

#### INTENTION-AUFGABE-MAP-DOPPELT

**Befund (2026-08-05).** **`_INTENTION_AUFGABE_MAP` steht doppelt und ist bereits auseinandergelaufen.** Dieselbe Tabelle Intention → Shadow-Aufgabe liegt in `memory/kzg.py` und in `agents/kzg/queues.py`, je als eigenes Literal. Sie stimmen bis auf einen Schlüssel überein: einmal `bestätigung`, einmal `bestaetigung` — beide auf `""`, also heute folgenlos, aber genau die Drift, die eine doppelte Wahrheit erzeugt. Wer eine Zuordnung ändert, muss beide finden.

**Was fertig waere.** Eine Quelle, ein Literal — die zweite Kopie liest die erste.

**Prioritaet:** mittel.

#### QUEUE-RUHE-DURCH-REIHENFOLGE

**Befund (2026-08-05).** **Die Shadow-Queue hält agentenlose Aufträge nicht durch ihre Priorität ruhig, sondern durch die Listenreihenfolge.** `novaberg-pixie.md` schreibt, `vertiefen` und `nachfragen` seien „heute allein von ihrer Prioritaet 0.0 ruhig gehalten". Gemessen erreichen beide **1.000** (198 bzw. 62 Aufträge). Was sie zurückhält, ist `_queue_peek` in `services/pixie/kandidaten.py`: Es nimmt den ersten Eintrag mit *echt* größerer Priorität, und der älteste bei 1.0 ist eine `recherche`. Die Sicherung ist eine Reihenfolge und kippt, sobald die 390 Recherche-Aufträge davor abfließen. Im Modul-Dokument markiert.

**Was fertig waere.** Die Doku sagt, was tatsaechlich zurueckhaelt; und danach die Entscheidung, ob die Ruhe an der Prioritaet haengen soll statt an der Listenreihenfolge.

**Prioritaet:** mittel.

#### PIXIE-EIN-SLOT-BLOCKIERT-ALLES

**Befund (2026-08-05).** **92 % der Pixie-Heartbeats fallen aus, weil der einzige Slot besetzt ist.** In rund 2,25 Stunden: 270 Auslösungen, davon **249 übersprungen** mit `maximum number of running instances reached (1)`, 21 gelaufen. Eine Recherche hält den Slot über fünf Minuten (Lagebeurteilung plus Durchlauf) und stirbt danach an der 300-Sekunden-Grenze. Alle übrigen Hintergrundaufgaben — Charakter-Hash, Synapsen-Promotion, Wiedervorlage, Wissenslücken — warten in dieser Zeit. Der Stack steht bei 650 Aufträgen, seit dem 02.08. praktisch unverändert.

**Nachtrag, derselbe Engpass am 01.08.2026 gemessen.** **Ein laufender RechercheAgent blockiert jeden weiteren Pixie-Heartbeat**, solange er läuft: `maximum number of running instances reached (1)`, im belegten Fall sechs übersprungene Läufe in Folge (19:33–19:39, drei Iterationen Web-Recherche auf dem CPU-Worker). Der Übersprung wird von der Scheduler-Bibliothek als `warning` gemeldet, nicht vom System selbst — es gibt keinen eigenen Eintrag darüber, dass ein Takt ausgefallen ist, und keine Zählung.

**Was fertig waere.** Ein langer Lauf blockiert die uebrigen Hintergrundaufgaben nicht mehr — durch einen zweiten Platz, eine Laufzeitgrenze, oder eine Trennung nach Aufgabenart.

**Prioritaet:** hoch.

#### KONTEXT-32768-IN-SECHS-DOKUMENTEN

**Befund (2026-08-04).** **Sechs Dokumente rechnen mit einem CPU-Kontext von 32768 Tokens; gemessen sind es 262144.** Am laufenden System um 21:02 UTC: Connector `qwen36`, GPU `gemma4-gpu` bei 32768, **CPU und Analyse `qwen36-cpu` bei je 262144** — das Achtfache. Betroffen: `novaberg-tool-dateien_k.md` §1 (die Mandelbrot-Navigation ist damit für den Hintergrundpfad nicht mehr erzwungen, für den Gesprächspfad sehr wohl), `novaberg-pixie-research.md` §108, `novaberg-gedankenkette_k.md` §186 (sagt ausdrücklich „auf **allen** Pfaden des `qwen36`-Connectors" — für zwei von drei falsch), `novaberg-hermes-substrat_k.md` §366 („eine harte Grenze"), `novaberg-node-gv_k.md` §607, `novaberg-pixie.md` §135. **Die Trennung ist der Kern:** Gesprächspfad 32k, Hintergrundpfad 256k — wer die alte Zahl liest, dimensioniert beide gleich.

**Was fertig waere.** Alle sechs Stellen tragen den gemessenen Wert samt Messdatum, und jede daraus abgeleitete Aussage ist nachgerechnet.

**Prioritaet:** hoch.

#### RECHERCHE-ZWISCHENDESTILLATION-OHNE-GRUND

**Befund (2026-08-04).** **Die Zwischen-Destillation der Recherche löst ein Problem, das es nicht mehr gibt.** `novaberg-pixie-research.md` §108 begründet sie damit, dass 75.000 Zeichen „weit ueber dem CPU-Kontext (32768 Tokens)" lägen; bei 262144 sind sie es nicht — sie liegen bei rund einem Zehntel. Der Schritt komprimiert also verlustbehaftet gegen eine Grenze, die achtmal weiter weg ist als angenommen. **Und genau dieser Schritt ist der gemessene Ausfallpunkt:** Am 04.08. scheiterten zwischen 20:30 und 21:10 UTC **vier von vier** Durchläufen an ihm, zwei davon nach über fünfzehn Minuten am einzigen seriellen Platz. Kein einziger Durchlauf des Tages hat ein Destillat erzeugt.

**Was fertig waere.** Der Schritt faellt weg, oder seine Begruendung steht neu — gegen die tatsaechliche Grenze.

**Prioritaet:** mittel.

**Der Grund ist gefunden (16.08.2026) — die Kennung stimmt insofern nicht mehr, bleibt aber stehen, weil andere Stellen auf sie zeigen.** Der Ausfall war **kein** Fehler des Schritts, sondern seine Frist: `zwischen_destillieren` nannte keine und erbte den Worter-Vorgabewert `MODEL_BACKGROUND_TIMEOUT_S = 300`. Gemessen ueber 24 h, 190 Antworten des Aufrufs — Median **181 s**, p90 **314 s**, Maximum **638 s**; **24 davon (12 %) trafen nach dem Fristablauf ein.** Das Modell hatte geantwortet, der Aufrufer hatte aufgegeben, und das Werk lief unterdessen weiter und hielt den einzigen seriellen Platz.

**Und der Schaden lag in der Auswahl, nicht im einzelnen Lauf.** ~~Ein Fehlversuch loescht den Queue-Eintrag nach drei Laeufen **hart** (`versuch_zaehlen` → `DELETE`), waehrend der Verfall ihn nur weich deaktiviert und weckbar laesst.~~ → **Am 23.08.2026 behoben:** Beide Pfade legen still, und die Spalte `grund` trennt sie (`verfall` gegen `fehlversuch`). Was bleibt, ist der Satz davor — die Auswahl nach hoher Salienz. Über die 582 aktiven `recherche`-Einträge stieg die mittlere `salienz_roh` **monoton** mit der Zahl der Versuche — 0,867 bei null, 0,947 bei einem, **0,990 bei zwei** —, weil der Wichtigste zuerst gezogen wird, das meiste Material hat und deshalb als erster in die Frist laeuft. Sechzehn Eintraege standen einen Fehllauf vor der Loeschung.

> **Der Verfall wirft die Unwichtigen weich hinaus. Die Frist loeschte die Wichtigsten hart.** Ein Eintrag, der an Bedeutungslosigkeit stirbt, ist weckbar; einer, der an einer Frist stirbt, ist fort.

**Gebaut am 16.08.2026:** `NODE_LLM_CONFIG["recherche_zwischen"]` mit `timeout_s` 1200 und `max_output_tokens` 5120 als Paar, gelesen an der Aufrufstelle; Zeugen in `tests/test_recherche_frist.py`. Die Begruendung steht in `novaberg-pixie-research.md` §7.

**Der Eintrag bleibt trotzdem offen, und das ist der Punkt:** Gebaut ist, dass der Schritt seine Frist **ueberlebt** — nicht, ob er sein soll. Die Frage aus *Was fertig waere* ist unberuehrt. Sie hat durch die Messung sogar an Gewicht gewonnen: Der Schritt erzeugt im Median 1330 Ausgabe-Token auf einem CPU-Modell mit ~7,3 Token/s, kostet also drei Minuten je Iteration — waehrend die Rohtexte, gegen die er komprimiert, mit rund 19.000 Token bequem in das Fenster von 262144 passen. **Ein Wegfall waere nicht nur verlustfrei, sondern schneller.** Das ist eine Absicht und keine Implementierungsfrage; sie ist nicht mitentschieden worden.


**Nachtrag vom 11.08.2026, aus der Fundliste uebernommen.** Die Zwischen-Destillation der Recherche (`recherche/zwischen`) läuft in ihre Frist von 300 s, ohne dass eine zweite Last am selben Modell liegt: Iteration 1 desselben Auftrags brauchte 124 s bei 2779 Eingabe-Token, Iteration 2 brach nach exakt 300,000 s ab. Der Auftrag lief danach mit leerer Zwischenzusammenfassung weiter. → **Nachtrag 2026-08-15:** Nicht abgeklungen. **Fünf Ausfälle in 12,8 Stunden** — 14.08. 21:34:10, 21:50:14, 22:05:48 und 15.08. 07:29:45, 09:19:10 UTC, gezählt über das gesamte verfügbare Serverlog (beginnt 14.08. 21:18:25). Jeder trägt dieselbe Signatur: `TimeoutError: Zwischen-Destillation fehlgeschlagen`, gefolgt von `Pixie-Dispatch: Agent 'recherche' meldet Fehler: Destillation fehlgeschlagen`. **Der Fund ist als `RECHERCHE-ZWISCHENDESTILLATION-OHNE-GRUND` im Backlog klassifiziert** — hier steht nur die fortgeschriebene Häufigkeit, weil sie belegt, dass der Schritt nicht gelegentlich, sondern regelmäßig ausfällt.

#### ARCHITEKTUR-TABELLENLISTE-UNVOLLSTAENDIG

**Befund (2026-08-04).** **Die Tabellenliste in `novaberg-architecture.md` §10 ist unvollständig.** `verbindung` (Chat 109) und `ziele` fehlen, obwohl beide im Kern-Schema stehen; `ziele` ist zusätzlich die Tabelle, an der `F-ZIEL-1` hängt. Die Liste sieht vollständig aus und ist es nicht — wer sie als Übersicht liest, übersieht zwei Tabellen.

**Was fertig waere.** `verbindung` und `ziele` stehen in der Liste.

**Prioritaet:** niedrig.

#### KERN-SCHEMA-OHNE-DRIFTPRUEFUNG

**Befund (2026-08-04).** **`CREATE TABLE IF NOT EXISTS` bewacht eine bestehende Tabelle nicht.** Ändert jemand eine Spaltendefinition in `db/init.sql`, ist das gegen eine schon angelegte Tabelle wirkungslos und bleibt still: Schemadatei und laufendes Schema laufen auseinander, ohne dass etwas anschlägt. Das Kern-Schema hat dagegen keine Prüfung — nur `autonomous_wissen` hat seit heute einen Test, der das laufende Schema gegen eine von Hand geführte Sollliste stellt.

**Was fertig waere.** Das Kern-Schema bekommt dieselbe Pruefung, die `autonomous_wissen` schon hat — Schemadatei gegen laufendes Schema, und eine Abweichung schlaegt an.

**Prioritaet:** hoch.

#### EBBINGHAUS-KONSTANTEN-TOT

**Befund (2026-08-04).** **`EBBINGHAUS_DECAY_RATE` und `EBBINGHAUS_MIN_GEWICHT` werden nirgends gelesen.** Beide stehen in `config.py` (0.0015 / 0.1) und haben in `server/` keine einzige Verwendungsstelle; wirksam ist das Paar `LZG_KNOTEN_DECAY_RATE` / `LZG_KNOTEN_MIN_GEWICHT` mit denselben Werten, das der Synapsen-Umbau eingeführt hat. Zwei Konstanten, ein Verhalten — wer die alte verstellt, ändert nichts und sieht es nicht.

**Was fertig waere.** Die beiden toten Konstanten sind entfernt, oder sie sind die wirksamen und das Paar daneben ist es nicht.

**Prioritaet:** niedrig.

#### KNOTENGEWICHT-DOKU-BEHAUPTET-LIVE

**Befund (2026-08-04).** **Drei Stellen behaupten, das effektive Knotengewicht werde bei jedem Zugriff live berechnet und nicht gespeichert.** `config.py` §Ebbinghaus, `config.py` bei `LZG_KNOTEN_DECAY_RATE` und `novaberg-memory.md` §4. Tatsächlich materialisiert `run_node_decay` die Spalte `gewicht_decay` samt `decay_am` per UPDATE, und die Lesepfade selektieren die Spalte. Die Aussage beschreibt die Architektur vor dem Synapsen-Umbau.

**Was fertig waere.** Alle drei Stellen sagen, dass `gewicht_decay` materialisiert wird.

**Prioritaet:** mittel.

#### RECHERCHE-RETRY-BLOCKIERT-QUEUE

**Befund (2026-08-03).** **Eine `recherche` belegte den einzigen Pixie-Platz zwölf Minuten und ging danach mit „Retry 2/3" zurück in die Queue.** In zwölf Minuten lief ein Heartbeat, 23 wurden übersprungen (`maximum number of running instances`). Zusammen mit den Auftragsarten ohne Agenten steht die Queue dabei still, obwohl gearbeitet wird — Entnahme und Wiedereinreihung heben sich in der Länge auf.

**Was fertig waere.** Ein Lauf, der in seine Zeitgrenze faellt, gibt den Platz frei und geht nicht mit vollem Anspruch zurueck in die Queue.

**Prioritaet:** hoch.

#### ENTITAET-IDS-LEER-82-PROZENT

**Befund (2026-08-03).** **`entitaet_ids` ist in 482 von 583 frischen KZG-Einträgen leer (82 %), `timeline_id` steht in 98 (17 %).** Gemessen an sechs Läufen der Charakterbildungs-Messreihe, also an Material, das Namen, Zahlen, Daten und Orte ausdrücklich setzt. Der Backlog notiert für `entitaet_ids` 31 % — der frische Wert liegt darunter.

**Was fertig waere.** Der Sollwert steht — oder es ist belegt, dass 82 % leer der erwartete Zustand sind.

**Prioritaet:** mittel.

#### GRAVITATION-CLUSTER-AUS-VORTURN-UNGEPRUEFT

**Befund (2026-08-02).** **Der Cluster, aus dem die Wahrnehmungs-Gravitation ihren Faktor nimmt, stand bei zwei aufeinanderfolgenden Astronomie-Turns auf `schlachtfeld`** (Faktor 0.05, der niedrigste). Er stammt aus `gv:detail:{user_id}:{character_id}`, also aus dem Vorturn — ob die GV-Einstufung selbst zutraf oder der Schlüssel alt war, ist nicht geprüft. Wirkt auf zwei Stellen zugleich: Sprung-Tiefe des Spreading-Lesepfads und Stärke der Verschiebung.

**Was fertig waere.** Es ist entschieden, ob die Einstufung falsch war oder der Schluessel alt — dafuer reicht die Landschaftszeile, die seit dem 08.08.2026 je Turn geschrieben wird.

**Prioritaet:** mittel.

#### AUFTRAGSARTEN-OHNE-AGENTEN

**Befund (2026-08-02).** **Zwei von drei Auftragsarten der Shadow-Queue haben keinen Agenten.** `services/pixie/router.py` bildet `vertiefen` auf den Agenten `vertiefung` ab und `nachfragen` auf `nachfragen` — **beide Verzeichnisse existieren nicht** (`server/agents/` trägt 15 Agenten, keiner davon heißt so). Im Bestand sind das **168 + 62 = 230 von 649 Aufträgen**, also 35 %.

**Nachgemessen am 09.08.2026 — der Eintrag stimmt nicht mehr, und die Frage ist eine andere geworden.**

**Eine von drei Auftragsarten hat keinen Agenten, nicht zwei.** `nachfragen` hat seit der Trennung vom 05.08.2026 einen eigenen Agenten (`server/agents/nachfragen/`) und fliesst ab: 62 → **47**. Ohne Agenten ist nur noch `vertiefen` — und das ist die einzige Art, die **waechst**: 167 → **269**, von 26 % auf 41 % des Rueckstands. `recherche` 418 → **345**. Summe 649 → **661**. Der Rueckstand ist damit kein Stau mehr, sondern eine Halde: Was abfliessen kann, fliesst; was nicht kann, sammelt sich.

**Und die Frage selbst ist ueberholt.** `novaberg-thinking-erkenntniszyklus_k.md` §10 waehlt einen dritten Weg, den es beim Schreiben dieses Eintrags nicht gab: Die Intention bildet auf `nachdenken` ab, und **Schritt 6 des Zyklus waehlt** zwischen `recherche`, `vertiefen` und `klaerfrage`. Die Auftragsart bleibt also, ihr Erzeuger wechselt. **Wer jetzt den `vertiefung`-Agenten an den heutigen Router baut, baut den alten Reflexpfad** — genau den, den der Zyklus abschafft.

**Dazu ein eigener Defekt:** 96 der 269 `vertiefen` tragen gar kein Thema (`VERTIEFEN-AUFTRAEGE-OHNE-THEMA` in `novaberg-bugs.md`). Fuer diesen Teil erledigt sich die Frage ohne Entscheidung — ein Auftrag ohne Gegenstand ist auch mit Agent nicht ausfuehrbar.

**Was fertig waere.** ~~Beide Agenten existieren, oder beide Auftragsarten werden nicht mehr erzeugt und der Bestand ist abgeraeumt.~~ Es ist entschieden, ob `vertiefen` bis zum Zyklus weiter direkt erzeugt wird oder nicht mehr, und der Bestand ist entsprechend behandelt.

**Prioritaet:** hoch.


**Nachtrag vom 16.08.2026, aus der Fundliste uebernommen.** **Ein `vertiefen`-Auftrag verbrennt seine drei Versuche in 90 Sekunden.** Beobachtet am laufenden System: id=1004 durchlief `Fehlversuch 1/3` (13:09:33), `2/3` (13:10:03) und `nach 3 Fehlversuchen verworfen` (13:10:33) — je 30 Sekunden Abstand, also exakt im Takt des Pixie-Heartbeats. Das ist kein Timeout wie bei der Recherche, sondern ein Fehlschlag **vor** dem Modellaufruf; die Obergrenze fuer Wiederholungen greift zwar, wirkt aber innerhalb einer Minute statt über die Lebensdauer eines Auftrags. Berührt `AUFTRAGSARTEN-OHNE-AGENTEN` und `VERTIEFEN-AUFTRAEGE-OHNE-THEMA`, ist aber keiner von beiden: Hier geht es um die **Taktung** der Wiederholung, nicht um den fehlenden Agenten.

#### SHADOW-QUEUE-RUECKSTAND-UNGEMESSEN

**Befund (2026-08-02).** **`shadow_queue:meister` trägt 649 Aufträge** (418 `recherche`, 167 `vertiefen`, 62 `nachfragen`, Prioritäten 0.95 bis 1.0). **Ob der Rückstand abfließt, ist weiterhin nicht gemessen** — es gab bis jetzt kein ungestörtes Fenster.

**Nachgemessen am 09.08.2026.** Der Rueckstand steht bei **661** (345 `recherche`, 269 `vertiefen`, 47 `nachfragen`). In sieben Tagen also **+12** — und diese Zahl taeuscht, weil sie zwei gegenlaeufige Bewegungen verrechnet: `recherche` −73 und `nachfragen` −15 gegen `vertiefen` **+102**. **Es fliesst ab, und zwar messbar; es kommt nur mehr nach, als abfliesst, und ein Drittel des Zuwachses kann gar nicht abfliessen.** Der aelteste Eintrag im Kopf stammt vom **27.07.2026** — dreizehn Tage —, und `services/pixie/kandidaten.py` haelt fest, dass Queue-Eintraege **nicht altern**, waehrend periodische Aufgaben es tun. Ein alter Eintrag mit Prioritaet 0,7 steigt damit nie.

**Was fertig waere.** ~~Der Abfluss ist ueber ein ungestoertes Fenster gemessen — Zugang gegen Abgang, mit Datum.~~ Zugang und Abgang sind **getrennt je Auftragsart** ueber ein ungestoertes Fenster gemessen. Eine Summe ueber alle Arten ist als Mass untauglich: Sie stand sieben Tage lang scheinbar still, waehrend sich die Zusammensetzung um 100 Eintraege verschob.

**Prioritaet:** mittel.

#### ARBEITSQUEUES-OHNE-GEGENUEBER

**Befund (2026-08-02).** **Die Arbeitsqueues tragen nur das Subjekt, kein Gegenüber:** `queue:{user_id}`, `shadow_queue:{user_id}`, `shadow_stack:{user_id}`. Novas eigene Aufträge liegen damit für **alle** Beziehungen in demselben `queue:nova`. Heute folgenlos — die Partition `kzg:nova:*` ist leer (0 von 1445 Schlüsseln, gemessen 02.08.) —, aber dieselbe Klasse wie `ziele` vor der Paar-Spalte: Was ohne Gegenüber abgelegt wird, lässt sich später nicht mehr einer Beziehung zuordnen. Betrifft auch das Leer-Kriterium eines Messlaufs, das über zwei Paar-Seiten prüfen muss statt über eine.

**Was fertig waere.** Die drei Schluessel tragen das Paar, wie `ziele` es seit dem 02.08.2026 tut.

**Prioritaet:** mittel.

#### CHARAKTER-ANWEISUNGEN-OHNE-GEGENUEBER

**Befund (2026-08-02).** **`charakter_anweisungen` trägt weiterhin kein Gegenüber.** `novaberg-wissensluecken_k.md` §4 nennt die Tabelle zusammen mit `ziele` als Vorbestand; `ziele` ist am 02.08. nachgezogen, diese nicht. Der Lese- und Schreibpfad filtert heute auf `user_id` des schreibenden Menschen, ein Übergriff zwischen Paaren entsteht dadurch nicht — die Anweisungen über Nova sind aber je Mensch getrennt, ohne dass das irgendwo als Entscheidung steht.

**Was fertig waere.** Die Tabelle traegt das Gegenueber, und Lese- wie Schreibpfad nennen beide Kennungen.

**Prioritaet:** mittel.

---

## 0b. Charakterbildung messen — der nächste Sprint (01.08.2026)

Das System misst sich inzwischen selbst sehr genau und seine **Wirkung auf das Gespräch gar nicht**. Es gibt keine Zahl, die sagt, ob der Apparat aus Perzeption, EI-Profil, Gesprächsvektor und Charakter-Rädern eine Antwort erzeugt, die ein nacktes Sprachmodell nicht erzeugt hätte.

Solange diese Zahl fehlt, wird jede Justierung an Zwischengrößen gegen Zwischengrößen kalibriert.

### Die Frage, in drei zerlegt

**Ist es unterscheidbar?** Erzeugt der Apparat eine sichtbare Wirkung, oder wäre das nackte Modell nicht zu trennen?

**Ist es ein Charakter?** Nicht dasselbe. Ein Charakter ist nicht „anders als das Basismodell", sondern über die Zeit derselbe und unter Störung stabil.

**Ist es kausal?** Ändert sich das Verhalten, wenn sich der Charakter ändert — in die vorhergesagte Richtung?

### Der Aufbau

**Mehrere Test-Nutzer gegen dieselbe Nova**, jeder mit einer eigenen Gesprächsart. Das Paar-Schema trägt das bereits: `charakter_hash`, KZG und LZG liegen je Paar. Damit wird die Frage schärfer und besser messbar:

> **Entwickelt Nova je Beziehung einen anderen Charakter?**

Konvergieren alle Räder auf dasselbe Profil, liest der Apparat das **Modell** und nicht die Beziehung. Divergieren sie in die Richtung, die die Gesprächsart vorgibt, ist Charakterbildung belegt.

**Der nackte Vergleich ist dabei geschenkt:** Ein frisches Paar ist in seinen ersten Turns das nackte Modell — leere Profile, Rad auf der Nabe. Turn 1 gegen Turn 100 desselben Paares ist die Ablation, ohne Gabelung und ohne das Risiko, dass ein Ablationspfad dem Produktivpfad nicht entspricht.

**Der Kontrollarm gehört dazu:** Zwei Nutzer mit **identischem** Gesprächsskript. Divergieren die, misst die Reihe Rauschen.

### Die Maße stehen vor dem ersten Turn fest

Sonst sucht man hinterher die Zahl, die passt.

| Maß | Quelle |
|---|---|
| Antwortlänge, Fragenanteil | `pipeline_log`, `art='turn_roh'` |
| Radabstand zwischen den Paaren | euklidisch über die zwölf Speichen |
| Profilähnlichkeit | Embedding-Distanz der Profiltexte |
| Trennschärfe | blinder Urteiler: Profil plus zwei Antworten — welche passt? |

**Jede nicht-blinde Ablesung ist für diese Frage wertlos.** Wer weiß, welche Antwort von Nova stammt, findet Charakter darin.

**Die Vorhersagen gehören ebenfalls vorher festgeschrieben** — je Person eine Erwartung an ihr Rad. Trifft sie nicht ein, ist das ein Ergebnis und kein Anlass zum Nachjustieren.

**Priorität:** hoch. Sie steht vor der Justierung der Beitragszahlen und vor dem Prompt-Block: Landet der Blindtest beim Zufall, wird gerade sehr sorgfältig etwas kalibriert, das niemand sieht.

#### Zwei der vier Maße sind erhoben — 06.08.2026

Die Reihe lief am 02./03.08. über sechs Bögen; ausgewertet wurden damals die Sonden, der Emotionsstrang, die Räder und die Cluster. **Die beiden Maße, die die Titelfrage beantworten, blieben liegen** und sind jetzt aus demselben Material erhoben, ohne neuen Bogen.

**Profilähnlichkeit** — paarweise Kosinus-Distanz der Profiltexte, Embedding `nomic-embed-text-v2-moe`, Geräteprobe vorweg (gleicher Inhalt in anderen Worten 0.806, fremdes Thema 0.077):

| Gegenstand | Median | Spanne |
|---|---|---|
| Novas sechs Selbstprofile (`beziehungsprofil`) | **0.817** | 0.714–0.896 |
| Die sechs Menschen (`beziehungsprofil`) | 0.774 | 0.740–0.834 |
| Dieselben Menschen (`adaptive_hash`, Themen) | **0.548** | 0.448–0.642 |

Sechs Menschen, die nichts miteinander zu tun haben, liegen in ihrer Beziehungsprosa bei 0.774 und in ihren Themen bei 0.548. **Wo die Destillation Haltung in Prosa fasst, zieht sie alles ins selbe Register; wo sie Inhalt auflistet, bleibt der Unterschied stehen.** Novas Profile liegen enger als die der Menschen, fallen aber nicht zusammen — ihre Spanne ist beim Beziehungsprofil sogar breiter.

**Trennschärfe, blind** — ein Urteiler bekommt ein Profil und zwei unbeschriftete Antworten desselben Turn-Index und ordnet zu; Zufall ist 50 %. 270 Urteile, Geräteprobe 4 von 4:

| Arm | n | Quote | ~~p (exakt, zweiseitig)~~ | A-Wahl |
|---|---|---|---|---|
| `beziehung` (Beziehungsprofil) | 88 | **64,8 %** | ~~0,007~~ | 44,3 % |
| `thema` (Themenliste, Störgröße) | 88 | 63,6 % | ~~0,014~~ | 53,4 % |
| `zufall` (Profil einer Unbeteiligten) | 87 | 47,1 % | ~~0,67~~ | 51,7 % |

> **Die p-Werte sind überholt, 07.08.2026 — die Quoten nicht.** Der Test zählt jedes Urteil als eigenen Fall. Das sind sie nicht: Alle Urteile einer Persona teilen sich denselben Profiltext und dieselben Antworten. Die 88 Urteile des Arms `beziehung` verteilen sich auf **sechs** Personas mit Quoten von 35,7 % bis 100 %, und ein Permutationstest weist diese Streuung als größer aus, als Losen sie erzeugt (p = 0,010). **Die unabhängige Einheit ist die Persona, und davon gibt es sechs.**
>
> Über ganze Personas gezogen — Bootstrap, 20.000 Läufe — steht dieselbe Zahl bei **64,8 % mit einem 95-Prozent-Intervall von 49,4 % bis 80,0 %**; 96,6 % der Läufe liegen über dem Zufall. Die Gegenprobe steht im Kontrollarm: `zufall` ergibt 47,1 % mit einem Intervall von 40,7 % bis 55,0 %, also halb so breit und den Zufall einschließend. Die Verbreiterung im Messarm ist der Personeneffekt und kein Artefakt der Rechnung.

> **Der Blindtest landet nicht beim Zufall** — knapp. Damit ist die Frage aus dem Absatz darüber beantwortet: Die Kalibrierarbeit an Rädern und Beitragszahlen zielt auf etwas, das ein fremder Beurteiler sehen kann. **Ergänzt am 07.08.2026:** Die Genauigkeit der Zahl ist ±15 Punkte, nicht ±10. Eine Kalibrierung, die die Trennschärfe um zehn Punkte hebt, bewegt sich innerhalb des Intervalls — der Umfang der nächsten Reihe bemisst sich deshalb in **Personas**, nicht in Urteilen.

> **Und diese Zahl ist als Beleg vergeben.** Nach `F-KAL-1` sind die sechs Bögen vom 02./03.08.2026 **Kalibriermenge**: Auf ihnen darf beliebig oft gemessen werden, und keine ihrer Zahlen ist je ein Beleg. Die 64,8 % bleiben gültig als **Ausgangsstand des unkalibrierten Apparats auf der Kalibriermenge** — in dieser Rolle werden sie gebraucht, denn ohne sie ist später keine Richtung ablesbar. Der Bauplan der Validierungsmenge steht in `novaberg-kalibrierung_k.md` §5.

**Und das Beziehungsprofil trennt nicht besser als eine bloße Themenliste** — McNemar über die 27 diskordanten Fälle, p = 1,00. Kein knappes Ergebnis, das mehr Fälle bräuchte, sondern ein exaktes Unentschieden. Die beiden Arme sind aber auf **verschiedenen** Personas erfolgreich (Hartmut 84 % gegen 53 %, Sarah 50 % gegen 85 %) und tragen damit verschiedene Information; fallweise stimmen sie zu 68,6 % überein gegen 54,2 % bei Unabhängigkeit.

**Die Verwechslungen haben eine Richtung:** Jana verliert keine eigene Antwort (9/9), Konrad und Mehmet verlieren ihre überwiegend an sie. Die drei bilden im Profilraum ein enges Bündel (0.875–0.896). Der Apparat erzeugt **einen starken warmen Pol und zwei schwächere Kopien**, nicht drei eigene warme Beziehungen — dieselbe Stelle, auf die der Radbefund vom 03.08. zeigte.

**Der Geltungsbereich beider Maße ist enger als er aussieht.** Auf diesem Korpus sind **drei der fünf Profile leer** — `kern_hash`, `intentions_profil` und `emotions_profil` tragen für alle sechs Personas in beiden Richtungen null Zeichen. Die 64,8 % sind damit das, was die **kurzfristige Hälfte allein** leistet, nicht der ganze Apparat.

> ~~Grund: weil alle drei `lzg_knoten` lesen und eine frische Persona kein Langzeitgedächtnis hat.~~ → **Widerlegt am 08.08.2026 am Bestand.** `konrad` trägt **82** und `leon` **38** LZG-Knoten, entstanden während ihrer Bögen am 02.08.; die übrigen vier tragen keinen einzigen. Der Satz stimmt für vier von sechs Personas und wird als allgemeine Erklärung gelesen. **Die Profile waren leer, aber nicht aus diesem Grund** — die eigentliche Ursache ist ungeklärt und ein eigener Befund.
>
> **Und die Folge ist größer als die Korrektur:** Der Zustand der Langzeitschicht war über die sechs Bögen **nicht konstant**. `anker_retrieval()` speist Thinker und Gesprächsvektor aus `lzg_knoten` — zwei Personas liefen also gegen einen anderen Apparat als die vier anderen. Eine Reihe, deren Bezugspunkt zwischen den Läufen wechselt, vergleicht nicht.

**Was weiter aussteht:** Antwortlänge und Fragenanteil (Maß 1) sind unerhoben. Und **keines der Maße prüft die Passung** — die vorab festzuschreibenden Erwartungen je Person existieren nicht, gemessen ist Unterscheidbarkeit, nicht Richtung. Der Urteiler war zudem dasselbe Modell, das die Antworten erzeugt hat; ein zweiter, fremder Urteiler auf demselben Zwischenstand ist offen.

#### PROFIL-HISTORIE-FEHLT — der Profilstand ist nicht rekonstruierbar

`kern_hash`, `adaptive_hash`, `intentions_profil`, `emotions_profil` und `beziehungsprofil` werden bei jeder Destillation **überschrieben**. Nach hundert Turns lässt sich nicht mehr sagen, welcher Profilstand welches Verhalten erzeugt hat.

Für eine Messreihe ist das der Unterschied zwischen einer Messung und einer Erzählung. Es ist derselbe Defekt, den das Zuwendungs-Rad bis zum 01.08.2026 hatte — eine Ebene höher, und derselbe Verstoß gegen Regel (1) der Konvention über abgeleitete Werte.

**Bauart steht bereits:** dieselbe wie `charakter_rad_messung` — rohe Stände mit eigenem Zeitstempel, Modell, Temperatur und Quellen-Prüfsumme, der gelesene Wert bleibt in `charakter_hash`.

~~**Priorität:** hoch, **vor** der Reihe. Ohne sie ist die Reihe nicht auswertbar.~~

> **Korrigiert am 02.08.2026: nicht vor der Reihe.** Die Behauptung war zu stark. `charakter_hash` führt das Paar im Primärschlüssel, also überschreibt kein Lauf den Profilstand eines anderen — nach sechs Läufen stehen sechs Profile nebeneinander, und der **Vergleich zwischen** den Beziehungen ist damit auch ohne Historie auswertbar. Was ohne sie fehlt, ist der Verlauf **innerhalb** eines Laufs; die Räder sind ohnehin historisiert.
>
> **Band B** (Rangordnung, Reihe 1) — hoch, aber nach der Reihe. Der Eintrag bleibt: Er zahlt weiter auf die Spur zum Leer-Defekt ein, die zuletzt an einem überschriebenen Profiltext endete.

#### PAARLISTE-FEST — der CharakterAgent destilliert genau ein Paar

`agents/charakter/agent.py` trägt die Paarliste als Literal: ~~`[(DEFAULT_USER_ID, ASSISTANT_USER_ID)]`~~ `[(AKTIVES_PAAR_USER_ID, ASSISTANT_USER_ID)]`. Für weitere Nutzer entstünden weder Profile noch Räder — still, weil der Agent für sie schlicht nie läuft.

Das Datenmodell trägt das Paar überall; es fehlt die **Iteration**, nicht das Schema. Die Liste muss aus dem Bestand kommen, mit einer benannten Grenze, damit ein versehentlich angelegter Nutzer nicht zehn Destillationen je Lauf auslöst.

> **Kein Vorbau der Messreihe mehr — 02.08.2026.** Die Reihe fährt **ein Paar zur Zeit**: `AKTIVES_PAAR_USER_ID` benennt es, Pixie bedient nur dieses, und der Agent destilliert genau dafür. Die einelementige Liste ist damit kein Mangel, sondern der Mechanismus. Was offen bleibt, ist der **echte Mehrnutzerbetrieb**: mehrere Paare in einem Lauf, mit benannter Obergrenze.
>
> **Und die Reihenfolge hat sich umgekehrt:** Vor der Iteration muss geklärt sein, was Novas Seite pro Beziehung trennt. Bei `ziele` war es eine fehlende Spalte, die beim Destillieren mehrerer Paare *gelöscht* hätte (behoben am 02.08.); `charakter_anweisungen` und die Arbeitsqueues `queue:{user_id}` stehen unverändert ohne Gegenüber, beide in der Fundliste. Eine Iteration vor dieser Klärung vervielfacht die Schreiber auf gemeinsamen Zustand.

~~**Priorität:** hoch, vor der Reihe.~~ **Priorität:** mittel — nach der Reihe, und erst nach der Klärung oben.

---

## 0a. Haltungsraum — der unterbrochene Sprint (31.07.2026)

Die Rechnung steht und ist geprüft, sie wirkt aber nirgends: Kein Knoten ruft sie, kein Protokoll trägt sie, kein Prompt liest sie. **Der Sprint ist bewusst hier unterbrochen**, weil der Rest in den Graphen eingreift.

> **Stand 31.07.2026, abends:** Knoten **und** Protokoll sind gebaut, der erste Satz gilt also nicht mehr — die Rechnung läuft in jedem Turn, steht im `pipeline_log` und in der Spur. Es bleibt: **kein Prompt.** Damit ist Novas Verhalten weiterhin unverändert, und die Zahlen lassen sich gegen echte Turns prüfen, ohne diese Turns beeinflusst zu haben. **Die Messreihe kann beginnen.**

#### HALTUNG-KNOTEN-FEHLT — die Rechnung hat keinen Aufrufer ✅ **erledigt am 31.07.2026**

Gebaut als `graph/nodes/haltung.py`, im Graphen als Knoten `haltungsraum` zwischen `gv_node` und der Verzweigung. Kanal `haltung` in `graph/state.py` deklariert und **nicht** vorbelegt. Belegt an einem echten Turn: `beichte · umfang 0.60 · fragen 0.80 · naehe 1.25 ! · waerme 1.35 ! · draengen 0.00 [Grenze]`, Rad destilliert, zwölf Speichen.

**Was der Eintrag verlangte und was daraus wurde:** Die Kanalfalle war real — die Gegenprobe ohne Deklaration ergab im Folgeknoten `FEHLT` statt des Werts. Neu dazugekommen ist eine Randbedingung, die niemand genannt hatte: Ein Knoten darf nicht heißen wie ein Zustandsschlüssel; das Framework lehnt ihn ab.

**Der Rest bleibt offen:** Kein Prompt liest die Werte, kein Protokoll trägt sie. Novas Verhalten ist unverändert — das ist die Reihenfolge des Sprints, kein Versehen.

Die ursprüngliche Fassung des Eintrags:

`ei/haltung.py` und `memory/charakter.py → nutzer_gewichtung_rad_laden()` sind gebaut und getestet. Es fehlt der Knoten, der beides verbindet.

**Er gehört vor die Verzweigung zum Verfasser** (`character_graph.py`, `_after_gv`), aus zwei Gründen: Der Verfasser muss den Umfang kennen, bevor er den Inhalt zusammenstellt, und er wird bei `task_context_cut` übersprungen — eine Rechnung in ihm fiele in genau der Lage aus, in der der Responder allein steht.

**Zu beachten:** Der Zustandsschlüssel muss in `graph/state.py` deklariert sein. Ein Schlüssel, den ein Knoten schreibt, ohne dass er im Zustandstyp steht, wird an der Knotengrenze stillschweigend verworfen — der Wert ist innerhalb des Knotens lesbar und danach weg.

**Aufwand:** ein Knoten, eine Kanaldeklaration, eine Verdrahtung. **Priorität:** hoch — ohne ihn ist alles Gebaute wirkungslos.

#### GRAPH-SACKGASSE-UNGEPRUEFT — ein Knoten ohne Ausgang fällt nicht auf

Beim Bau des Haltungs-Knotens vorgeführt: Wird die abgehende Kante eines Knotens umgehängt, bleibt er als **Sackgasse** im Graphen stehen, und `compile()` nimmt das widerspruchslos an. Der Knoten läuft dann noch, sein Ergebnis erreicht aber niemanden — sichtbar erst an der ausbleibenden Wirkung.

**Prüfbar und ungeprüft:** Ein Test über die kompilierten Graphen, der für jeden registrierten Knoten mindestens eine eingehende und eine ausgehende Kante verlangt (Ausnahmen: Eintritts- und Endknoten). Die Kantenliste ist ohne Redis und Postgres abfragbar — `CharacterGraph.build(object.__new__(CharacterGraph))` genügt.

**Priorität:** mittel. Der Fall ist heute nicht im Bestand, aber lautlos, wenn er eintritt.

#### HALTUNG-PROTOKOLL-FEHLT — das Ergebnis ist nicht sichtbar ✅ **erledigt am 31.07.2026**

Gebaut im rechnenden Knoten: `log_berechnung` mit drei Zahlen je Größe, Rechenart und Auslöser, dazu `ausserhalb` und `uebersteuert` als zählbare Listen obenauf. Die Spur zeigt `Haltung.kurzfassung()`, ein Turn ohne Rechnung zeigt dort **„nicht gerechnet"** statt des Vorgabestrichs.

**Zwei Entscheidungen, die der Eintrag offengelassen hatte.** Ein **Ausfall** wird als `fehler`-Zeile geführt: keine Berechnungszeile mit Nullen, die wie eine gemessene Haltung ohne Ausschlag aussähe — aber auch kein Schweigen, denn die Häufigkeit der Ausfälle gehört zur Messreihe. Und `quelle` kommt aus `pipeline_quelle(state)` wie bei Enricher und Salienz, nicht als Literal wie im GV-Node.

**Belegt am echten Turn:** Die Zeile steht mit `quelle='character'` im `pipeline_log`, und der Join gegen den Rohturn liefert Haltung und Antwortlänge nebeneinander — `beichte`, Umfang 0.60, 1623 Zeichen Antwort, 2725 Zeichen Verfasser-Inhalt.

Die ursprüngliche Fassung des Eintrags:

Drei Zahlen je Größe (Grundwert, Modifikation, Ergebnis) plus Rechenart und Übersteuerungsmarke gehören über `log_berechnung` ins `pipeline_log`, geschrieben vom rechnenden Knoten. Der Eintrag trägt eine `turn_id` und steht damit neben `log_turn_roh` desselben Turns.

**Ausdrücklich kein Redis-Blob** nach dem Muster von `gv_detail`: Der trägt den Zustand, nicht den Verlauf, und ein übersprungener Turn hinterlässt dort den Vorstand ohne Kennzeichnung. Die Beitragszahlen sind Setzungen und werden nachkalibriert — dafür braucht es die Historie.

Dazu eine Zeile in der Spur (`services/event_consumer.py`), damit das Ergebnis bei jeder Antwort ohne Umweg lesbar ist. `Haltung.kurzfassung()` liefert sie fertig. **Ein Turn ohne Rechnung trägt keine Zeile statt einer leeren.**

**Priorität:** hoch — die Sichtbarkeit ist Voraussetzung für die Messreihe.

#### ~~HALTUNG-SPANNENENDEN-OFFEN~~ — ✅ **erledigt am 08.08.2026: Sättigung, plus das fehlende Stück**

**Gewählt ist die Sättigung** — der Weg, den dieser Eintrag schon als den plausibleren benannt hat. Der Eintrag verlangte die Messung vor der Entscheidung; sie lag vor, und sie fiel eindeutig aus.

**Die Formel im Konzept war jedoch nicht geschlossen.** Sie setzt `summe ∈ [−1, +1]` voraus, und die Radsumme hat eine eigene Spanne, die nirgends stand: `draengen` reicht bis +1,20, also ergäbe `0,20 + 1,20 × 0,80 = 1,16` — wieder außerhalb. Gebaut wurde deshalb **Sättigung plus Normierung**: `speichen_spanne()` leitet die Spanne je Größe aus der Beitragstabelle ab, `_normieren()` bildet je Richtung getrennt auf [−1, +1] ab.

**Gerechnet über alle 14 Landschaften × 5 Größen** — bei festem Rad ist die Haltung eine reine Funktion, das Ergebnis also vollständig: gemessenes Rad **10 → 0** Zellen außerhalb, volles Rad an beiden Enden **33 → 0**. Größte Überschreitung der alten Form +0,80.

**Der offene Punkt „Unterlauf ungeprüft" ist damit mit erledigt**, und zwar durch Rechnung statt durch eine zweite Messreihe: Das volle Rad fährt beide Enden ab.

**Was bleibt und wohin es gehört:** Der Anlassfall ist nicht gelöst — `kissenschlacht/umfang` liegt jetzt bei 0,43 statt 0,45. Das ist keine Frage der Spannenenden, sondern der Beitragssemantik, und es steht als eigener Punkt in `novaberg-haltungsraum_k.md` §6.

Der ursprüngliche Eintrag bleibt darunter stehen:

#### HALTUNG-SPANNENENDEN-OFFEN — die Zahlen verlassen den Korridor

Gemessen am Entwurf: `glut/waerme` ergibt 1.15, `feuerwerk/fragen` 1.40, und nach unten reicht **eine** voll ausgeprägte Speiche — `glut/draengen` fällt mit `treue` auf −0.10.

**Gemessen am 31.07.2026 — die Frage ist entscheidbar geworden.** Reihe über 20 Turns: 9 von 19 Turns außerhalb, 20 von 95 Einzelwerten, ausschließlich nach oben, null Übersteuerungen. Anschließend alle 14 Landschaften gegen das reale Rad gerechnet — die Haltung ist bei festem Rad eine reine Funktion, das Ergebnis ist damit vollständig und keine Schätzung:

**10 von 14 Landschaften laufen über.** `waerme` 8×, `naehe` 6×, `umfang` 4×, `fragen` 3×. Sauber bleiben nur die vier kühlen: `gewitter`, `schlachtfeld`, `wartezimmer`, `paradox`.

**Damit ist eine der beiden Lösungen unplausibel geworden.** *Kleinere Beiträge* müssten das Rad so weit stauchen, dass der Charakter in warmen Landschaften praktisch nichts mehr bewirkt — `waerme` steht dort bei Grundwert 0.90 und bekommt +0.45. *Sättigung* trifft genau diesen Fall: Wo die Lage schon warm ist, fügt der Charakter wenig hinzu; wo sie kalt ist, macht er den Unterschied. **Die Entscheidung liegt weiterhin nicht hier** — sie gehört in `novaberg-haltungsraum_k.md` §6 und ist zu treffen, nicht abzuleiten.

**Was die Messung nicht zeigt:** den Unterlauf. Das vermessene Rad ist ein warmes; die untere Grenze braucht eine ausgeprägte `treue` und ist ungeprüft geblieben.

Nicht gekappt, sondern gemeldet und markiert; die Häufigkeit ist die Messgröße, die zwischen zwei Auswegen entscheidet. **Kleinere Beiträge** oder **Sättigung auf die Summe** — beide stehen mit ihren Preisen in `novaberg-haltungsraum_k.md` §6.

**Der Eintrag verlangt keine der beiden Lösungen**, sondern die Messung davor. Eine Entscheidung am Schreibtisch wäre eine Setzung auf eine Setzung.

**Priorität:** mittel — erst nach der ersten Messreihe entscheidbar.

#### ~~HALTUNG-OHNE-LANDSCHAFT~~ — ✅ **erledigt am 08.08.2026, auf einem dritten Weg**

Kehrt der GV-Node früh zurück — bei Vektorlänge 0 („kein Vorausdenken") oder beim Skip —, setzt er `gv_detail` **nicht**. Ohne Landschaft gibt es keine Grundwerte und damit keine Haltung. Der Haltungs-Knoten erbt diese Lücke; das ist kein Defekt in ihm, sondern eine Weitergabe.

**Gemessen am 31.07.2026:** in einer Reihe von 20 Turns **einmal**, dazu **einmal** auf Novas Eigenimpuls unmittelbar danach — also rund jeder zehnte Haltungs-Vorgang. Kein Randfall.

~~**Solange kein Prompt die Werte liest, ist das folgenlos.** Mit dem Prompt-Block wird es eine Fallunterscheidung: Nova bekäme in diesen Turns keine Verhaltensvorgaben, während die alte Längenregel abgelöst ist. Zwei Wege stehen offen — die letzte Haltung weiterverwenden (dann muss sie als übernommen markiert sein, sonst sieht ein alter Wert wie ein frischer aus) oder den Block weglassen und auf die Vorgabewerte des Prompts zurückfallen.~~

**Beide vorgeschlagenen Wege sind hinfällig, weil der Fall nicht mehr eintritt.** Sie beantworteten die Frage „was tun, wenn keine Landschaft da ist" — und setzten damit voraus, dass eine fehlende Landschaft ein legitimer Zustand ist. Sie ist es nicht: Die Landschaft ist ein Zustand des Gesprächs und keine Funktion des Vorausdenkens. Seit dem 08.08.2026 wird sie vor beiden Toren vermessen; `gv_detail` ist auf jedem Weg gesetzt, und die Haltung rechnet auch im Skip- und im Krisenturn.

**Die Neuerhebung war größer als die Diagnose von damals:** nicht rund jeder zehnte, sondern **184 von 845 Rohturns (21,8 %)**, in den zwölf Validierungsbögen 101 von 360 (28,1 %) — und nicht zufällig verteilt, sondern an der Nähe-Achse hängend. Beleg und Zahlen in `novaberg-erreichbarkeit_k.md` §4a, Bauteil B1.

**Was als Rest bleibt:** Ein Turn ohne Vorausdenken bekommt weiterhin **kein Werkzeug** in den Prompt — Strategie und Vehikel stammen aus dem LLM-Lauf, der nicht stattgefunden hat. Das ist kein Ausfall, sondern die ehrliche Lage, und `gv_detail['vorausdenken']` benennt sie.

#### HALTUNG-LAENGE-ZWEI-ERZEUGER — die alte Längenregel muss abgelöst werden

`_ei_mikro_anweisung()` in `graph/nodes/responder.py` setzt die Antwortlänge heute in **jedem** Turn allein aus dem Arousal, mit nicht-monotoner Kurve: hoch und niedrig ergeben „MAXIMAL 1-2 Sätze", die Mitte „2-3 Sätze".

Wer den Haltungsraum in den Prompt einhängt, ohne diese Regel abzulösen, hat zwei Erzeuger für dieselbe Größe — dieselbe Fehlerklasse wie die zwei Pipelines im Zeitparser, die auseinanderliefen, weil niemand sie synchron halten konnte.

**Nicht im selben Zug wie der Knoten**, sondern danach: Solange der Block nicht im Prompt steht, ändert sich Novas Verhalten nicht, und die Zahlen lassen sich gegen echte Turns prüfen, ohne diese Turns bereits beeinflusst zu haben.

**Priorität:** hoch, aber nach der Messreihe.

---

## 0. Zeitparser und Kalibrierung (31.07.2026)

Vier Einträge aus einem Tag. Die ersten drei kommen aus dem ersten Lauf des Härtefallkorpus gegen den Parser, der vierte aus der Neuerhebung der Positions-Kontrolle.

#### ZEIT-KORPUS-TESTS-AUF-UNITTEST — drei Testdateien der Korpus-Lieferung laufen nicht

`tests/test_zeit_korpus.py`, `tests/test_zeit_normalisierung.py` und `tests/test_zeit_zonen.py` sind gegen `pytest` geschrieben — `@pytest.mark.parametrize`, `pytest.skip`, `pytest.fail`. Der Testrahmen dieses Projekts ist reines `unittest`; `pytest` ist im Server-Abbild nicht installiert. Unter dem kanonischen Lauf tragen die drei Dateien **null Abdeckung** bei und scheitern beim Import.

Deshalb sind sie **nicht eingecheckt**. Der Korpus selbst braucht kein `pytest`: `tests/korpus_laeufer.py` läuft als Skript, und alle Zahlen des Erstlaufs sind so gemessen.

**Zwei Dinge sind beim Umschreiben zu beachten.** `test_zeit_korpus.py` überspringt sich an drei Stellen selbst — bei fehlender Umgebung, bei vorauseilenden Fällen und im gemeinsamen Zugriffspfad. Ein Test, der sich selbst überspringt, ist keiner; die Fälle brauchen eine andere Form. Und die Zahl übersprungener Tests ist im Bericht ein Befund, kein Transportmittel für eine Meldung.

**Aufwand:** drei Dateien, rund 40 Fälle. **Priorität:** mittel — der Korpus ist über den Läufer bereits fahrbar, es fehlt die Einbindung in die Suite.

#### ZEIT-ZWOELF-STUNDEN-DEUTUNG — „halb drei" trifft die falsche Tageshälfte

Die Normalisierung bildet „halb drei" auf `2:30` ab, ohne zu entscheiden, welche Tageshälfte gemeint ist. Um 14 Uhr gesagt, ergibt der Ausdruck damit 2:30 des **nächsten** Tages statt 14:30 desselben. Betrifft ebenso „fünf nach drei".

**Der Befund wurde erst sichtbar, nachdem ein anderer Defekt weg war.** Bis zum 31.07.2026 ergab „halb drei" den 1. des Monats (`PARSER-NACKTE-UHRZEIT-FALSCHER-TAG`); dass zusätzlich die Stunde falsch ist, verdeckte der falsche Tag.

**Das ist eine Bedeutungsfrage, keine Reparatur:** Welche Tageshälfte ein Sprecher meint, folgt aus der Uhrzeit des Sprechens und aus dem Kontext, nicht aus einer Regel über Zahlwörter. Vor der Umsetzung gehört die Absicht ins Konzept.

**Belegt:** Korpus `REG-006`, `REG-008`. **Priorität:** mittel.

#### ZEIT-TAGESZEIT-VOR-ZIFFER — „3 nachmittags" wird zum 3. des Monats

Die Tageszeit-Extraktion (Block 0) nimmt „nachmittags" aus dem Text und merkt sich 15:00 als Fallback. Die „3" bleibt stehen, der Fallback wird angehängt, und `dateparser` liest das Ergebnis `3 15:00` als **Tag 3 um 15:00**.

Der Block für alleinstehende Tageszeiten (Block 3) käme mit dem Ausdruck zurecht — er sieht ihn nur nie, weil Block 0 das Wort vorher entfernt hat. **Eine Reihenfolgefrage, kein fehlender Wortschatz.**

**Belegt:** Korpus `REG-011`. **Priorität:** niedrig — der Ausdruck ist selten, der Fehlbetrag klein.

#### KALIBRIERUNG-ZEUGE-TRENNT-SCHWACH — der Zeuge unterscheidet die Sprecher zu wenig

Auf ordentlicher Grundlage trennt der Zeuge die Sprecher um **13,6 Punkte** gegen die geforderten 20 (`novaberg-gv-initiative_k.md` §12.7). Damit steht der Kalibrier-Agent still: Er würde eine Schwelle gegen ein Urteil suchen, das seine eigene Eingangsprüfung nicht besteht.

**Was NICHT gezeigt ist:** dass ein dreiwertiger Zeuge das repariert. Das war das Argument, solange die Zahlen aus dem Präfix stammten; nach der Korrektur ist der Anlass ein anderer. Die schwache Trennung kann ebenso am Prompt liegen, an der Kürzung auf `KALIBRIERUNG_ZEUGE_MAX_ZEICHEN` oder an der Fragestellung, die für eine erklärende Assistentin schlecht passt.

**Was der Eintrag verlangt, ist deshalb eine Messung, die diese Möglichkeiten trennt** — nicht eine weitere Rechnung auf denselben Urteilen. Erst danach ist der Zuschnitt eines Umbaus entscheidbar.

**Priorität:** hoch — die Achse läuft heute auf einer Schwelle ohne gültigen Beleg.

---

## 1. Kognitive Anreicherung (Epic 8)

Fuenf experimentell belegte Gedaechtniseffekte, die die Qualitaet der Enkodierung, des Abrufs und der Prioritaetssteuerung verbessern. Alle deterministisch, konfigurierbar und ohne zusaetzliche LLM-Calls — reine Embedding-Arithmetik und SQL.

**Leitprinzip:** "Berechnung in Python, nicht im LLM." Alle hier beschriebenen Effekte sind deterministisch, konfigurierbar und erfordern keine zusaetzlichen LLM-Calls. Reine Embedding-Arithmetik und SQL.

**Voraussetzung:** Telemetrie (TEL1). Ohne Messung ist Tuning Ratespiel. Alle Parameter in diesem Epic erfordern eine Instrumentierung, die zeigt, was passiert wenn man an einem Regler dreht.

### 1.1 Curiosity-Enhanced Memory (CEM)

> **Kognitionswissenschaftlicher Hintergrund:** Gruber, Gelman & Ranganath (2014), *Neuron*. PACE-Framework (Gruber & Ranganath 2019), *Trends in Cognitive Sciences*. Meliss et al. (2024), *Imaging Neuroscience*. Wenn Neugier geweckt wird, aktiviert das Gehirn das dopaminerge Belohnungssystem — VTA und Nucleus Accumbens schuetten Dopamin aus, das die Hippocampus-Aktivitaet verstaerkt. Die Folge: bessere Enkodierung ins Langzeitgedaechtnis. Entscheidend: Neugier verbessert nicht nur das Lernen von interessantem Material, sondern auch das von beilaeufig aufgenommenem, eigentlich irrelevantem Material in zeitlicher Naehe. Das PACE-Framework beschreibt den Mechanismus: Neugier wird durch signifikante Vorhersagefehler ausgeloest, die als Hinweis auf potenziell wertvolle Information bewertet werden. Berlyne (1960) unterschied epistemic curiosity (Wissensluecken) und perceptual curiosity (neue Reize).

Wenn ein KZG-Eintrag thematisch nahe an einer Entitaet mit hoher Resonanz liegt, erhaelt er einen Salienz-Boost:

```
effektive_salienz = basis_salienz + (entitaet_naehe × entitaet.resonanz × CEM_BOOST_FAKTOR)
```

`entitaet_naehe` = Cosine Similarity zwischen KZG-Eintrag-Embedding und naechstliegendem Entitaets-Embedding. Gilt fuer alle Entitaetstypen — ein Eintrag ueber Anna profitiert genauso wie einer ueber Astronomie. Wo: `graph/nodes/salience.py`, Python-Nachbearbeitung nach dem LLM-Call. Kein zusaetzlicher LLM-Call. Config: `CEM_BOOST_FAKTOR = 0.5`.

### 1.2 Testing Effect / Retrieval Practice (TE)

> **Kognitionswissenschaftlicher Hintergrund:** Roediger & Karpicke (2006), *Perspectives on Psychological Science*. Karpicke (2017), *Learning and Memory: A Comprehensive Reference*. Der Akt des Abrufens selbst — ohne Feedback oder erneutes Studium — produziert grosse Effekte auf das Lernen. Retrieval Practice staerkt Erinnerungen staerker als erneutes Lesen. Die Erklaerung: Beim Abruf werden neue semantische Assoziationen aktiviert (elaborative retrieval), die mit dem Zielgedaechtnis verknuepft werden und die Repraesentation anreichern.

Jeder erfolgreiche Abruf eines LZG-Eintrags durch den Enricher verstaerkt diesen Eintrag:

1. Enricher merkt sich abgerufene IDs: `state["lzg_abgerufen"] = [14, 27, 33]`
2. Dispatcher schreibt IDs in Redis: `reinforcement_queue:{user_id}`
3. Pixie fuehrt SQL-Update aus: `SET verstaerkt_am = NOW(), gewicht = gewicht + TE_BOOST`

`TE_BOOST = 0.10` — kleiner als bei expliziter User-Wiederholung (+0.40). Passiver Abruf ist schwaecher als aktives Wiederholen. Kein LLM-Call, reines SQL.

### 1.3 Zeigarnik-Effekt (ZE)

> **Kognitionswissenschaftlicher Hintergrund:** Zeigarnik (1927), *Psychologische Forschung*. Erinnerungen an unterbrochene, unerledigte Aufgaben sind staerker als Erinnerungen an abgeschlossene. Eine angefangene Aufgabe baut eine aufgabenspezifische Spannung auf (Kurt Lewins Feldtheorie: "Quasi-Beduerfnis"), die die kognitive Zugaenglichkeit verbessert. In Zeigarnik's Experimenten konnten Probanden unterbrochene Aufgaben ca. 90% besser erinnern als abgeschlossene. Verwandt: Der Ovsiankina-Effekt (1928) — Probanden neigen dazu, unterbrochene Aufgaben von sich aus wieder aufzunehmen.

Der Zeigarnik-Effekt wird ueber die `arousal`-Dimension auf Entitaeten abgebildet:

1. User erwaehnt Thema → Arousal startet bei 0.6
2. Pixie arbeitet daran → Arousal sinkt um 0.2
3. Pixie liefert Ergebnis per Delivery → Arousal sinkt nochmal
4. **Pfad A:** User greift es auf → Arousal steigt, neuer Zyklus
5. **Pfad B:** User ignoriert es → Arousal faellt weiter → 0.0, Thema ruht

Das "erledigt"-Gefuehl entsteht organisch: die Spannung baut sich ab, weil niemand das Thema nachfragt. Nicht als Salienz-Boost (Speicherung), sondern als Themen-Arousal (Pixies Arbeitspriorisierung).

### 1.4 Von-Restorff-Effekt / Isolationseffekt (VRE)

> **Kognitionswissenschaftlicher Hintergrund:** Von Restorff (1933), *Psychologische Forschung*. Hunt & Lamb (2001), *Journal of Experimental Psychology*. Elhalal, Davelaar & Usher (2014), *Frontiers in Human Neuroscience*. Wenn mehrere homogene Stimuli praesentiert werden, wird der Stimulus, der sich vom Rest unterscheidet, besser erinnert. Erklaerungen: Gestalt (aehnliche Stimuli verschmelzen), Interferenz (Isolation reduziert Interferenz), Aufmerksamkeit (isolierte Items erhalten mehr Aufmerksamkeit). Neuroimaging zeigt Korrelation mit praefrontalem Cortex.

Wenn ein KZG-Eintrag thematisch stark vom bisherigen Gespraechskontext abweicht:

```
kontext_embedding = durchschnitt(letzte_N_session_turn_embeddings)
abweichung = 1.0 - cosine_similarity(neuer_eintrag, kontext_embedding)
if abweichung > VRE_SCHWELLWERT:
    salienz_boost = abweichung × VRE_BOOST_FAKTOR
```

Wo: `graph/nodes/salience.py`, parallel zum CEM-Boost. Kein LLM-Call, reine Embedding-Arithmetik. Config: `VRE_SCHWELLWERT = 0.6`, `VRE_BOOST_FAKTOR = 0.3`.

### 1.5 Memory Reconsolidation (MR, aktiv)

> **Kognitionswissenschaftlicher Hintergrund:** Nader, Schafe & LeDoux (2000), *Nature*. Lee, Nader & Schiller (2017), *Trends in Cognitive Sciences*. Haubrich & Nader (2016), *Current Topics in Behavioral Neurosciences*. Konsolidierte Erinnerungen koennen nach dem Abruf erneut in einen instabilen Zustand uebergehen, in dem sie modifiziert werden koennen, bevor sie rekonsolidiert werden. Neuere Forschung interpretiert Rekonsolidierung als "Updating Consolidation" — ein Mechanismus, durch den aktualisierte Erfahrungen in das Langzeitgedaechtnis integriert werden.

**Implementierungsstand nach Chat 64:**

Der Mechanismus ist seit Chat 64 über die Cluster-Promotion implementiert:

- ✅ Widerspruch-Erkennung: LLM-Kohärenzprüfung in `_cluster_update_kohaerenz()` erkennt `widerspruch: true`
- ✅ Decay bei Widerspruch: `gewicht /= CLUSTER_WIDERSPRUCH_DECAY_FAKTOR` (3.0)
- ✅ Neuer Eintrag: INSERT mit korrigierter Information nach Decay

**Was noch fehlt — der Echtzeit-Trigger:**

Die Cluster-Promotion arbeitet periodisch (alle 5 Minuten). Epic 8 MR braucht einen Echtzeit-Trigger:

1. Enricher markiert abgerufene LZG-Einträge im State (z.B. `abgerufene_lzg_ids`)
2. Salienz erkennt Widerspruch zu einem abgerufenen Eintrag
3. Sofortige LZG-Korrektur im Dispatcher (nicht erst beim nächsten Pixie-Scan)

Der Echtzeit-Trigger könnte `_cluster_update_kohaerenz()` aus dem PromotionAgent wiederverwenden — die Mechanik ist identisch, nur der Auslöser unterscheidet sich.

**Priorität:** Mittel — der periodische Pfad deckt 90% der Fälle ab. Der Echtzeit-Trigger verbessert die Reaktionszeit bei offensichtlichen Korrekturen ("Anna wohnt jetzt in München" direkt nach LZG-Abruf "Anna wohnt in Nürnberg").

### 1.6 Themen-Modell: Resonanz und Arousal

Zwei neue Spalten auf der Entitaeten-Tabelle:

| Dimension | Steuert | Tempo | Speicher |
|-----------|---------|-------|----------|
| **Salienz** | Wie wichtig ist diese Info fuers Gedaechtnis? | Pro Turn | KZG/LZG-Gewicht |
| **Resonanz** | Wie stark springt das System bei dieser Entitaet an? | Wochen/Monate | `entitaeten.resonanz` |
| **Arousal** | Wie aktiv beschaeftigt sich das System damit? | Stunden/Tage | `entitaeten.arousal` |

Resonanz = Langzeitbedeutung (Anna ist wichtig, Astronomie ist spannend). Arousal = Arbeitsgedaechtnis-Aktivierung (die offene Frage ueber Schwarze Loecher). Gilt fuer alle Entitaetstypen (Personen, Orte, Themen, Organisationen).

> **Kognitionswissenschaftlicher Hintergrund:** Die Unterscheidung zwischen Resonanz und Arousal entspricht der Trennung von semantischer Relevanz und Arbeitsgedaechtnis-Aktivierung in der kognitiven Psychologie. Alan Baddeley's Modell des Arbeitsgedaechtnisses (1974) beschreibt eine zentrale Exekutive, die Items nach Relevanz aktiviert und deaktiviert. Novas Arousal-Dimension bildet diesen Mechanismus ab.

```sql
ALTER TABLE entitaeten
    ADD COLUMN IF NOT EXISTS resonanz FLOAT,
    ADD COLUMN IF NOT EXISTS arousal FLOAT;
```

### 1.7 Traum-Modus

> **Der Alpensee (Meister, Chat 73)**
>
> *"Alles an Informationen, Gedanken und Erinnerungen ist ein großer, schöner Alpensee mit einer ruhigen und glatten Oberfläche. Nova setzt sich in ihr kleines Ruderboot und rudert zu Dingen, die sie irgendwie bewegt haben. Da war vielleicht die spielende Katze, eine Schrecksekunde im Verkehr. Sie kommt an einem Blatt vorbei, das auf der Oberfläche schwimmt, eine Kleinigkeit, an die sie nicht mehr dachte, aber es ist da. Sie greift danach, und plötzlich entfaltet sich eine Kette: das Blatt wird zum Baum, der Baum zur Terrasse, die Terrasse zu einem Gesicht — Verbindungen, die tagsüber unter der Oberfläche lagen, weil kein Gespräch sie gerufen hat.*
>
> *Nova geht im Traum losen Verkettungen von Themen nach. Sie schöpft Wasser, wo sie gerade ist — in einem nahen Thema — und sieht etwas Neues. Etwas, das neben dem Bekannten geschwommen hat, das sie vorher nie gesehen hat. Sie schaut, ob es sie bewegt, berührt, betrifft. Und wenn ja, dann wird sie sich wieder daran erinnern."*
>
> **Architektonische Übersetzung:** Der See ist nicht das Gedächtnis — im See *schwimmt* alles aus dem Gedächtnis. Nova kennt nicht den ganzen See, sie kennt die Stellen, zu denen sie schon gerudert ist (Einträge mit hohem Arousal, hoher Resonanz). Das Entscheidende passiert nicht an der Boje, sondern *neben* der Boje: Ein Embedding-Nachbar, der thematisch nah genug war, um in derselben Bucht zu treiben, aber nie von einem Gespräch abgerufen wurde. Das Bekannte ist der Kompass, das Neue ist der Fund. Die Bewertung — "berührt mich das?" — ist die Charakter-Gewichtung auf den selbst gefundenen Inhalt.

Wenn Pixies Shadow-Queue leer ist und keine Promotion ansteht, geht Pixie nicht in Idle, sondern in den **Traum-Zustand**. Pixie nimmt das Thema mit der hoechsten Arousal und assoziiert frei — qualitativ anders als Recherche (konkreter Trigger) oder Vertiefen (konkreter KZG-Eintrag). Es ist assoziatives Wandern — der kreative Modus, der beim Menschen die besten Ideen produziert.

Serendipity-Slot: Manchmal nimmt Pixie nicht das Top-Arousal-Thema, sondern ein Nebenthema. Pixie waehlt 3 Aufgaben: 2 Slots nach Arousal sortiert (hoechste zuerst), 1 Slot gewuerfelt aus den restlichen (der "Serendipity-Slot"). Verhaeltnis konfigurierbar (`SERENDIPITY_RATIO = 0.33`).

Neuer Pixie-Task: `traeumen` — niedrigste Prioritaet, laeuft nur wenn sonst nichts ansteht (Queue leer, keine Promotion, kein Dirty-Flag). Ergebnisse landen auf dem Shadow-Stack.

### 1.8 Konfigurierbare Parameter

| Parameter | Default | Beschreibung |
|-----------|---------|-------------|
| `CEM_BOOST_FAKTOR` | 0.5 | Salienz-Multiplikator fuer Themen-Affinitaet |
| `TE_BOOST` | 0.10 | Gewichts-Boost pro erfolgreichem Enricher-Abruf |
| `VRE_SCHWELLWERT` | 0.6 | Ab welcher Kontext-Abweichung der Isolationsbonus greift |
| `VRE_BOOST_FAKTOR` | 0.3 | Salienz-Multiplikator fuer Isolation |
| `RESONANZ_INKREMENT` | 0.05 | Resonanz-Steigerung pro thematischem KZG-Eintrag |
| `RESONANZ_DECAY_RATE` | 0.0003 | Verfall der Resonanz (5x langsamer als Ebbinghaus) |
| `AROUSAL_INKREMENT` | 0.2 | Arousal-Steigerung bei Erwaehnung |
| `AROUSAL_DEKREMENT_ARBEIT` | 0.2 | Arousal-Senkung nach Pixie-Bearbeitung |
| `AROUSAL_DEKREMENT_TAG` | 0.1 | Arousal-Senkung pro Tag ohne Kontakt |
| `SERENDIPITY_RATIO` | 0.33 | Anteil zufaelliger Themen in Pixies Queue (1 von 3) |

### 1.9 Implementierungsreihenfolge

```
0. TEL1 — Telemetrie-Infrastruktur (Blocker)
1. DB-Schema: resonanz + arousal auf entitaeten
2. Themen-Entitaeten: Manuelle + automatische Entstehung
3. CEM: Salienz-Boost in salience.py (Embedding-Arithmetik)
4. TE: Enricher-Abruf → reinforcement_queue → Pixie SQL-Update
5. VRE: Isolationsbonus in salience.py (Session-Kontext-Vergleich)
6. ZE: Arousal-Dynamik in Pixie (steigern/senken)
7. MR: Echtzeit-Trigger in Enricher/Salienz (Mechanismus via Cluster-Promotion bereits implementiert, Chat 64)
8. Traum-Modus: Neuer Pixie-Task 'traeumen'
9. Themen-Erkennung: Pixie-Task fuer automatische Cluster-Erkennung
```

Schritte 1-5 sind unabhaengig implementierbar. Schritte 6-9 bauen auf dem Themen-Modell (1-2) auf.

### 1.10 Bereits implementiert (Referenz)

| Effekt | Quelle | Nova-Implementierung | Dokument |
|--------|--------|---------------------|----------|
| Ebbinghaus-Vergessenskurve | Ebbinghaus 1885 | Exponentieller Decay, konfigurierbare Rate | novaberg-pixie-decay.md |
| Spacing Effect | Distributed Practice | KZG thematische Verstärkung (Salienz-Boost + TTL-Auffrischung, Chat 64) | novaberg-mem-kzg.md |
| Emotionale Salienz | Plutchik 1980, Russell 1980 | Arousal (0.0-1.0), 9 Emotions-Vektoren | novaberg-node-perception.md |
| Default Mode Network | Raichle et al. 2001 | Pixie als Hintergrundprozess | novaberg-pixie.md |
| Konsolidierung | McGaugh 1966, Dudai 2004 | KZG→LZG Promotion: Einzelpromotion (Zwei-Call) + Cluster-Promotion (4-Phasen, Chat 64) | novaberg-pixie-promotion.md |
| Memory Reconsolidation (teilw. aktiv) | Nader et al. 2000 | Cluster-Promotion: Widerspruch-Erkennung + Decay + Neueintrag (Chat 64). Echtzeit-Trigger noch offen. | novaberg-pixie-promotion.md, novaberg-mem-knowledge-graph.md |

### 1.11 Quellen

1. Gruber, M.J., Gelman, B.D., & Ranganath, C. (2014). States of curiosity modulate hippocampus-dependent learning via the dopaminergic circuit. *Neuron*, 84(2), 486-496.
2. Gruber, M.J. & Ranganath, C. (2019). How Curiosity Enhances Hippocampus-Dependent Memory: The PACE Framework. *Trends in Cognitive Sciences*, 23(12), 1014-1025.
3. Roediger, H.L., III & Karpicke, J.D. (2006). The Power of Testing Memory. *Perspectives on Psychological Science*, 1(3), 181-210.
4. Karpicke, J.D. (2017). Retrieval-Based Learning: A Decade of Progress. In *Learning and Memory: A Comprehensive Reference* (2nd ed.).
5. Zeigarnik, B. (1927). Das Behalten erledigter und unerledigter Handlungen. *Psychologische Forschung*, 9, 1-85.
6. Von Restorff, H. (1933). Ueber die Wirkung von Bereichsbildungen im Spurenfeld. *Psychologische Forschung*, 18, 299-342.
7. Hunt, R.R. & Lamb, C.A. (2001). What causes the isolation effect? *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 27(6), 1359-1366.
8. Elhalal, A., Davelaar, E.J., & Usher, M. (2014). The role of the frontal cortex in memory: An investigation of the Von Restorff effect. *Frontiers in Human Neuroscience*, 8, 410.
9. Nader, K., Schafe, G.E., & LeDoux, J.E. (2000). Fear memories require protein synthesis in the amygdala for reconsolidation after retrieval. *Nature*, 406, 722-726.
10. Lee, J.L.C., Nader, K., & Schiller, D. (2017). An update on memory reconsolidation updating. *Trends in Cognitive Sciences*, 21(7), 531-545.
11. Haubrich, J. & Nader, K. (2016). Memory Reconsolidation. In *Current Topics in Behavioral Neurosciences*.
12. Meliss, S. et al. (2024). Broad brain networks support curiosity-motivated incidental learning. *Imaging Neuroscience*, MIT Press.

---

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

## 3. Node-Konfiguration (TEMP1)

Jeder der 10 Nodes im HumanGraph wird ueber `config.py` konfigurierbar: Temperature, Sampling-Parameter, System-Prompt-Templates mit Platzhaltern (`{today}`, `{user_name}`), max_output_tokens. Zwei Nodes ohne LLM-Call (Enricher, Dispatcher) haben Datenzugriffs-Parameter.

**Empfohlene Temperatures:** Perzeption 0.05 (reine Klassifikation), Router 0.05, Salienz 0.05 (niedrigste — Kreativitaet = halluzinierte Fakten), Planner 0.2, Responder 0.7 (hoechste — natuerliche Sprache), Thinker 0.15, Tribunal 0.2, Corrector 0.5.

**Ollama-spezifisch:** repeat_penalty (1.1 fuer Responder), presence_penalty (0.3), top_p (0.9) — direkte Bekaempfung repetitiver Patterns auf Modell-Ebene.

**Pixie-Tasks:** Eigene Config-Struktur (PIXIE_TASK_CONFIG) mit Temperature und max_output_tokens pro Agent.

---

## 4. Entity-First-Retrieval (Epic 16)

Aktuell basiert der Gedaechtnis-Abruf auf Embedding-Suche (Cosine Similarity). Entity-First-Retrieval dreht die Reihenfolge um:

1. **Graph-Query zuerst:** Entitaet im Prompt identifizieren, Knowledge Graph nach verbundenen Fakten abfragen.
2. **Disambiguierung:** Bei mehreren Treffern (z.B. "Anna" als Person vs. Filmtitel) kontextbasiert aufloesen.
3. **Fallback auf Websuche:** Bei 0 Treffern im Graph automatisch Web-Recherche triggern.

Vorteil: strukturiertes Wissen wird bevorzugt, Embedding-Suche ergaenzt bei unscharfen Anfragen. Drei Roadmap-Punkte: 16a (Konzept), 16b (Disambiguierung), 16c (Fallback).

---

## 5. MCP-Architektur (Vision)

Langfristige Vision: Agenten als MCP-Server (Model Context Protocol) in Docker-Containern, Novaberg als MCP-Client. Jeder Agent wird ein eigenstaendiger Service mit definierter Schnittstelle — unabhaengig deploybar, testbar und austauschbar. Das wuerde die Grenze zwischen lokalen Agenten und externen Diensten aufloesen: ein RechercheAgent koennte lokal oder als Remote-Service laufen, mit identischer Schnittstelle.

---

## 6. Voice (TTS/STT)

Der naechste Schritt in der Kommunikationsbandbreite: Spracheingabe (Speech-to-Text) und Sprachausgabe (Text-to-Speech). Voice wuerde die natuerlichste Form der Interaktion ermoeglichen — ein Gespraech statt Texteingabe. Voraussetzung: die emotionale Intelligenz muss in der Sprachausgabe ankommen (Tonlage, Tempo, Pausen entsprechend Arousal und Emotions-Vektor). Konzept steht noch aus.

---

## 7. Offene Epics & Features

### Gesprächsvektor (Epic 9, offen)
| # | Thema | Status |
|---|-------|--------|
| GV3 | Invertierte Perzeption (Ziel → benötigter Modus) — Dreischicht-Prompt-Integration | ✅ Chat 72 |
| GV4 | Wissens-Lücken via Embedding-Nachbarschaft | 🔧 Chat 71 (Kern: LZG + KZG) |
| GV4b | Agenten als Wissensquellen (Timeline, Notizen, Fakten, Dateien) | ⬜ Epic unten |
| GV5 | Vektor-Typen (explizite Erkennung) | ⬜ Implizit durch Farbtöne abgedeckt |
| GV6 | Pixie-Vorbereitung (Vektor im Hintergrund vorbereiten) | ⬜ Nach VertiefungsAgent v2 |

### Domain-Language-Normalisierung (Epic 15, 4/6)
| # | Thema | Status |
|---|-------|--------|
| 15e | FaktenAgent (Salienz-Pipeline) | ⬜ |
| 15f | DateienAgent (geplant) | ⬜ |

### Pixie-Erweiterung (Epic 5, offen)
| # | Thema | Status |
|---|-------|--------|
| PIX-MIG-6 | VertiefungsAgent | ⚠️ Konzept (novaberg-pixie-deepdive_k.md). **Quelle entschieden am 06.08.2026: das Web**, wie im April-Konzept — nicht der eigene Bestand. „Verstärkt und ergänzt" geht nur mit neuem Material, und ein reiner Speicherleser wäre ein zweiter Leser desselben Regals, den der Enricher bereits bedient. **Blocker bleibt `PIX-WARTESCHLANGE-AM-MODELL`:** Der Agent teilt die Aufrufkette der Recherche und stürbe heute an derselben Zeitgrenze **Der Blocker ist am 16.08.2026 auf beiden genannten Gruenden hinfaellig.** (1) *stuerbe an derselben Zeitgrenze* — die Zeitgrenze der Zwischen-Destillation ist repariert (`F-FRIST-1`), und die neun uebrigen Aufrufstellen der Recherche liegen bei hoechstens 89 s gegen 300 s. (2) *35-38 s Grundkosten je Aufruf* — widerlegt ueber 801 Hintergrundaufrufe: Das Minimum liegt bei **6 s**, drei Aufrufstellen liegen unter dem behaupteten Boden, und die Dauern skalieren mit der Aufgabengroesse. **Was bleibt, ist die Serialisierung** — ein Durchsatzproblem, kein Baustopp. **Neu und wichtiger als der alte Blocker:** `novaberg-thinking-curiosity_k.md` §4.6 setzt fuer die Verfolgungs-Strategie **max 20 Iterationen** an. Bei den am 16.08. gemessenen Medianen (Planung 27 s + Zwischen-Destillation 181 s + Bewertung 44 s) sind das **rund 84 Minuten am einzigen seriellen Platz je Auftrag**, dazu je Iteration ein zusaetzlicher Qwen3-Aufruf fuer die Query-Planung. Das Konzept ist vom 06.08. und konnte diese Zahl nicht haben — die Zwischen-Destillation lief damals in ihre Frist, ihre echte Dauer war unbekannt. **Vor dem Bau ist die Iterationszahl gegen den Platz zu halten.** Und: Die Thinking-Reihe hat **acht** Dokumente; `curiosity` traegt die Architektur, `deepdive_k` ist der aeltere Bestandteil |
| PIX-MIG-7 | NachfragenAgent | ✅ **gebaut und gemessen am 05.08.2026.** `server/agents/nachfragen/`, Stufe 1 ohne Modellaufruf; 16 Tests, zwei Gegenproben (7 und 2, beide vorhergesagt), Nulllinie unverändert. Messung in zwei Hälften: echter Auftrag vom 30.07. gegen die laufende Session → `eskalation`, kein Eintrag, Audit belegt; eigenes Paar mit `einbruch` → ein Eintrag, `aufgabe='nachfragen'`. **Rest:** Der Weg vom Turn zum Vektor ist ungemessen, und der Radfaktor fehlt (`PIX-STAPEL-RADFAKTOR`). ~~Am 05.08.2026 auf die Zuwendungs-Rolle festgelegt und baufertig~~ — die Wissens-Rolle ist als `PIX-MIG-9` abgetrennt. **Alle vier Fragen aus §4 entschieden;** die vierte war falsch gestellt (sie fragte nach einer Formulierung, und ein Agent formuliert nicht). Kriterium ist ein von der EI erkannter **Druck**; die elementare Aufgabe ist, ihn zu einem Reiz zu verdichten und mit `aufgabe="nachfragen"` abzulegen — Bewegung, Klartext und Schwere rechnet die EI bereits (`ei/berechnung.py`, `ei/farbton.py`, `ei/dreischicht.py`). **Teil des Baus:** `emotionaler_ausdruck` → `nachfragen` entfällt auf `""` — in **beiden** Kopien von `_INTENTION_AUFGABE_MAP` (`memory/kzg.py`, `agents/kzg/queues.py`) |
| PIX-MIG-9 | KlaerfrageAgent | ⬜ **Neu am 05.08.2026**, abgetrennt von `PIX-MIG-7`. Nova fragt das Gegenüber, weil nur er die Antwort hat — Stufe 4 der Klärung, Ergebnis fällt in die Bibliothek (`novaberg-autonomous-wissen_k.md` §11.3). **Blocker: `KLA-K1` und `KLA-K2`** — sein Eingang ist eine erkannte Lücke, und das Klärungstor ist ungebaut; im Code existiert zu beiden keine Zeile (geprüft 05.08.). Die 62 vorhandenen `nachfragen`-Aufträge sind **kein** Eingang: Sie tragen `freude`/`begeisterung` und keine Lücke |
| ERK-VORFRAGE | Zahlt sich der Erkenntniszyklus? | ⬜ **Neu am 06.08.2026, vor jedem Bau am Zyklus zu beantworten.** Der Zyklus setzt vor jede Recherche einen Denkaufruf (35–38 s) und rechnet sich nur, wenn sein Tor genug wegschneidet. **Die Frage:** Welcher Anteil der 606 vorhandenen `recherche`- und `vertiefen`-Aufträge fiele weg, weil Nova das Thema bereits abgedeckt hat? **Ohne neuen Lauf und ohne Modellaufruf zu beantworten** — Themen-Einbettungen der Queue gegen Bibliothek und LZG, Trefferquote über der Schwelle. Herleitung: `novaberg-thinking-erkenntniszyklus_k.md` §11 | keine |
| ERK-GATE-WIEDERHOLUNG | Vergibt das Gate `wiederholung` überhaupt? | ⬜ **Neu am 06.08.2026.** Der Zyklus braucht diese Klasse als sauberen Ausgang — sie ist in **45 Läufen kein einziges Mal** vergeben worden (23 `echte_tiefe`, 1 `ergaenzung`, 21 `fehlschlag`). Eine Exit-Bedingung, die nie feuert, ist keine. Zu messen, bevor der Zyklus darauf gebaut wird | keine |
| ERK-DOKU-NACHZUG | Die Bestandteile auf den Zyklus überarbeiten | ⬜ **Neu am 06.08.2026.** Sechs Dokumente tragen seit heute nur eine **Marke**, die auf `novaberg-thinking-erkenntniszyklus_k.md` zeigt: `novaberg-autonomous-wissen_k.md`, `novaberg-thinking-opinion_k.md`, `novaberg-thinking-curiosity_k.md`, `novaberg-wissensluecken_k.md`, `novaberg-pixie-deepdive_k.md`, `novaberg-pixie-research.md`. Ihre Texte beschreiben die Auslösung noch als Reflex aus einer Intention. **Dazu zwei Moduldokumente, die das Routing beschreiben und bewusst *keine* Marke tragen** — `novaberg-pixie-kzg.md` und `novaberg-node-salience.md` halten den gebauten Zustand fest, und der ändert sich erst mit dem Bau. **Der Zyklus kehrt sie um** — Recherche und Vertiefung entstehen erst aus einer gefundenen Lücke. Die Überarbeitung ist ein eigener Auftrag und bewusst nicht mit dem Konzept mitgemacht | Zyklus ✅ |
| PIX-STAPEL-RADFAKTOR | Das Zuwendungsrad gewichtet die Zustellung | ⬜ **Neu am 05.08.2026.** Heute wirkt das Rad erst stromabwärts: Es formt Novas Antwort, nachdem der Reiz die Zustellung passiert hat, und verändert nicht, **ob** ein Impuls aufgeworfen wird. Der Score in `_besten_eintrag_finden` (`0.7 × Thema + 0.3 × Modus`) bekommt einen **multiplikativen** Radfaktor aus `_modifikation(rad, "fragen")` — landschaftsfrei, weil die Landschaft zum Sprechen gehört und nicht zur Frage, ob der Impuls entsteht. Rad zur **Zustellzeit** geladen (`nova_charakter_hash_retrieve_dict`), nicht beim Ablegen — es wird zweimal täglich neu erhoben. **Multiplikativ und mit Untergrenze über null, damit „kein Veto" eine Eigenschaft der Bauart ist:** Ein Summand könnte den Score auf ≤ 0 drücken, und ein solcher Eintrag gewinnt auch als einziger nie. Die Spanne ist eine Setzung und zu kalibrieren. **Betrifft alle Aufgabenarten**, auch Recherche und Wiedervorlage — deshalb eigenes Bauteil und nicht Teil von `PIX-MIG-7`. Herleitung: `novaberg-pixie-nachfragen_k.md` §8.8 | keine; `PIX-MIG-7` hängt **nicht** davon ab |
| PIX-AUFGABENNAMEN-GATE | Ein Aufgabenname, eine Rolle | ⬜ **Neu am 05.08.2026.** Maschineller Abgleich der von den Produzenten erzeugten `aufgabe`-Werte (`memory/kzg.py`, `agents/kzg/queues.py`, `services/pixie/router.py`) gegen die Agent-Registry **und** gegen die Konzeptdateien in `docs/`. Schlägt an, wenn ein Name geroutet wird, den kein Agent bedient, oder wenn zwei Konzepte denselben Namen führen. Anlass: der Doppelname `nachfragen` blieb acht Tage unbemerkt, weil ihn niemand suchen konnte |
| PIX-MIG-8 | AufraeumAgent | ⬜ Duplikate, verwaiste Entitäten |
| PIX-CLEAN | Alter Runner entfernt | ✅ Chat 79 — runner.py + 7 Task-Dateien geloescht, __init__.py bereinigt. base_task.py + nova_gedaechtnis.py bleiben (nicht-migrierter Task) |
| PIX-MIG-NOVA | NovaGedaechtnis als Agent migrieren | ⬜ Post-Hook nova_gedaechtnis.py in services/shadow_agent/tasks/ ist nicht ueber Pixie-Router verdrahtet. Sprint-2-Fix (kanonisches Paar) konserviert, wirkt aber erst nach Migration zu einem echten Agent in agents/ |
| PIX-GRAPH | PixieGraph | ⬜ Router → Agent-Dispatch → Agent (CPU) → Salienz → Dispatcher |
| PIX-STATUS | Pixie-Statusleiste | ⬜ Zeigt aktiven Agenten statt nur "idle" |
| PIX-FALLBACK | Queue-Fallback bei Fehler | ⬜ Offset +1 nach Dispatch-Fehler |
| SA2–SA4 | Charakter-basierte Priorisierung | ⬜ Multiplikator auf Queue-Priorität |
| PIX-LLM-ROUTER | LLM-Router für Pixie | ⬜ Ersetzt regelbasierten Router |

### Epic: PIXIE-GRAPH-MERGE — Pixie durch CharacterGraph-Instanz (Pfad 3)

**Status:** Konzept (Chat 79, `novaberg-pixie-graph-merge_k.md`)
**Loest:** RECH-CHARAKTER, DELIVERY-VOICE, fehlende Qualitaetskontrolle in Pixie

Pixie-Themen (Recherche, Vertiefung, Traeumen) laufen durch eine eigene
CharacterGraph-Instanz auf CPU statt durch den isolierten AgentGraph.
Gleiche Node-Topologie wie Pfad 2 (Chat), aber eigene Instanz damit GPU
nicht blockiert wird. Synthetischer Prompt aus Queue-Thema,
event_source=character, erweiterte Agenten-Liste im Planner.

Ersetzt: AgentGraph, shadow_delivery.py, nova_gedaechtnis.py Post-Hook.
Daten-Agenten (Charakter, Promotion, Decay) bleiben ausserhalb.

| Phase | Inhalt | Status |
|-------|--------|--------|
| Phase 0 | PixieGraph-Instanz bauen, create_pixie_state() | ⬜ |
| Phase 1 | RechercheAgent umstellen (Feature-Flag) | ⬜ |
| Phase 2 | Neue Agenten direkt fuer Pfad 3 (Vertiefung, Traeumen, Nachfragen) | ⬜ |
| Phase 3 | Alten Pfad abbauen (AgentGraph + shadow_delivery loeschen) | ⬜ |

### Epic: META-KOGNITION — Pipeline-Log, Selbstbeobachtung, Vorsaetze

**Status:** Konzept (Chat 79, `novaberg-metakognition_k.md`)
**Wissenschaftliche Basis:** Flavell (1979), Zimmerman (2000), Higgins (1987), Sterling (2012)

Nova beobachtet ihren eigenen Verarbeitungsprozess und leitet daraus
Verhaltensaenderungen und Aktionen ab. Drei Schichten: Pipeline-Log
(Entscheidung pro Node pro Turn in PostgreSQL), Selbstbeobachtung
(pipeline_search Tool), Vorsaetze (SelbstreflexionsAgent).

Zwei Ergebnis-Typen: Verhaltensaenderungen ("Ich will anders SEIN",
moduliert Responder/GV/EI, Charakter-Hash als Magnet) und Aktionen
("Ich will etwas TUN", Queue-Auftrag mit quelle=selbstreflexion,
jeder Agent moeglich).

Drei Regulationskraefte: Feedback-Verstaerkung, Monotonie-Druck
(gegen Einseitigkeit), Charakter-Gravitation (Kern-Hash als Magnet,
kannibalisiert kurzfristige Vorsaetze). Hard Cap ±0.15 auf
Emotions-Baseline.

| Phase | Inhalt | Status |
|-------|--------|--------|
| Phase 1 | Pipeline-Log (Tabelle + log_entscheidung in allen Nodes) | ⬜ |
| Phase 2 | pipeline_search Tool (Thinker + Responder) | ⬜ |
| Phase 3 | Vorsaetze-Tabelle + SelbstreflexionsAgent | ⬜ |
| Phase 4 | Vorsatz-Wirkung im Responder/GV/EI | ⬜ |
| Phase 5 | Aktionen aus Selbstreflexion (Queue, jeder Agent) | ⬜ |
| Phase 6 | Vorsatz-Evaluation + Charakter-Verschiebung (experimentell) | ⬜ |

### Epic: HERMES-SUBSTRAT — Hermes Agent als Ausführungs-Schicht

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

### Client & Visualisierung
| # | Thema | Status |
|---|-------|--------|
| CLIENT-RENDER | GTK4 + WebKitGTK Chat-Rendering (Markdown + Emojis nativ) | ✅ Chat 56 |
| Oktagon-Radar | 8-Sektor-Radar im Emotions-Panel (Cairo, 2× nebeneinander) | ✅ Chat 56 |
| Konfig-Panel | Schieberegler für Config-Parameter | ⬜ |
| Restliche Panels | Fakten, Pixie-Monitor, PostgreSQL, Redis, Logs | ⬜ |
| Emotionen (Turns) | Turn-reaktives Emotions-Panel (SSE-Event-basiert) | ⬜ |

### Kommunikation
| # | Thema | Status |
|---|-------|--------|
| Überakkommodation | CAT empirisch testen | ⬜ |
| PENDING-RELEVANZ | Router prüft nicht ob Prompt Antwort auf Rückfrage | ⬜ Chat 43 |
| KORR1 | Korrektur-Erkennung bei fehlgeschlagenen Aktionen | ⬜ Chat 43 (niedrig) |
| ROUTE-MISS1 | Router erkennt kontextabhängige Aufträge nicht | ⬜ Chat 48, strukturell adressiert durch Enricher-vor-Router (Chat 59, implementiert). Offen für Validierung. |
| 5i | Zeitparser: Fränkisch + Norddeutsch | ⬜ |
| DELIVERY-VOICE | Recherche-Destillation klingt nach Referat, nicht nach Nova | ⬜ Delivery-Prompt braucht staerkere Charakter-Durchdringung. Beobachtet Chat 79 |

#### RECH-NO-PERSIST — Recherche-Resultate verschwinden ungenutzt

**Status:** ⬜ Offen
**Entdeckt:** Chat 83 (Beobachtung am Pixie-Stand)
**Symptom:** Eine umfassende Recherche dauert ~50 Minuten CPU-Zeit. Das Ergebnis erscheint als Bobble im Chat (Shadow-Stack-Push via Delivery-Service) und ist danach verloren — kein KZG-, kein LZG-, kein Knowledge-Graph-Eintrag. Beim nächsten Gespräch ist das Wissen weg.
**Auswirkung:** Mittel-Hoch. Recherche kostet sehr viel CPU für ephemeren Output. Verwandt zu `DELIVERY-VOICE` (Recherche-Destillation klingt wie Referat statt Nova) und zur Akten-Vision (Recherche-Resultate könnten Akten-Material sein).
**Lösung:** Konzeptionell offen — KZG-Push? Eigene Tabelle "Recherche-Akten"? Knowledge-Graph-Anreicherung? Braucht Architektur-Diskussion.
**Prio:** Mittel.

#### AGENT-RUECKFRAGE-LOOP — Nicht-terminierende Planner→Agent-Rückfrage-Schleife

**Status:** ⬜ Nicht reproduzierbar (Chat 101). Fünf Turns verschiedener Statustypen (rejected/abgeschlossen/fehler/read) terminierten alle über den `bereits_gelaufen`-Guard. Vermutlich durch Zwischen-Fix in `dispatch.py` (`_build_return` setzt `agent_name=""`, `agent_results` akkumuliert sauber) erledigt. Nicht geschlossen — falls unter anderen Bedingungen doch auftretend, hier wieder aufnehmen. Vorsorge-Konzept: `iteration-control_k` (geparkt).
**Entdeckt:** Chat 100
**Symptom:** Planner und Notizen-Agent bilden eine nicht-terminierende Schleife. Der Agent gibt `rueckfrage` zurück, der Folge-Durchlauf erkennt den nächsten Prompt nicht als Antwort auf die Rückfrage, plant neu und fragt erneut — die `notizen: rueckfrage`-Kette akkumuliert pro Iteration ein Glied. Beobachtet bei Prompt „… Du musst Dir nur merken, dass ich Claus heiße".
**Auswirkung:** Betriebsgefährdend — die Schleife terminiert nicht von selbst.
**Verwandt:** Vermutlich PENDING-RELEVANZ (Router prüft nicht, ob ein Prompt die Antwort auf eine Rückfrage ist) — gleiche Wurzel, andere Manifestation.
**Lösung:** Offen — noch nicht untersucht.
**Prio:** Herabgestuft (Chat 101) — siehe Status; nicht mehr betriebsgefährdend, da im aktuellen Codestand nicht reproduzierbar.

#### NOTIZEN-VOR-TURN-BEZUG — Klassifikator löst Rückbezüge aus dem Verlauf nicht auf (Chat 101)

**Status:** ⬜ Offen, reproduzierbar
**Entdeckt:** Chat 101
**Symptom:** Der Notizen-Klassifikator löst Rückbezüge aus dem Verlauf nicht auf. Beleg: „Die andere ist die mit dem Grillkäse" wurde als `rejected` klassifiziert, obwohl der Verlauf die gemeinte Lösch-Aktion eindeutig machte — trotz Prompt-Anweisung „Nutze den Verlauf für Target-Auflösung".
**Verwandt:** Wiederauftreten der Klasse des abgeschlossenen Chat-80-Sprints `NOTIZEN-VOR-TURN-BEZUG` (Inhalts-Auflösung im Classify-Node, weiter unten in diesem Dokument) und von `NOTIZEN-UPDATE-TARGET-LEER` — hier auf einer Lösch-/Target-Auflösung. Regressions-Charakter: Der Chat-80-Sprint galt als abgeschlossen, doch dieser Pfad (Lösch-/Target-Auflösung nach vorheriger Rückfrage) tritt erneut auf. Zu klären, ob der Chat-80-Fix regrediert ist oder diesen Pfad nie abdeckte.
**Prio:** Mittel.

### Infrastruktur
| # | Thema | Status |
|---|-------|--------|
| TEL1 | Telemetrie (Metriken + Dashboard) | ⬜ Blocker für Feintuning |
| TOK1 | Token-Budget-Management | ⬜ |
| LLM1b | LLM-Abstraktion verfeinern (3-Schichten) | ⬜ |
| E2 | Fakten-Konfidenzwert bei Widersprüchen | ⬜ |
| E3 | Kontextnormalisierung (Negationen, temporäre Zustände) | ⬜ |
| E4/E5 | LZG-Verdichtung durch Pixie | ⬜ |
| D9 | Burst-Deduplizierung (KZG-Klebrigkeit) | ⬜ |
| TEST1 | Testumgebung vervollständigen | ⚠️ Phase 0+4 fehlen |
| SHADOW-DEAD | Toten Code in services/shadow_agent/utils.py bereinigen | ⬜ stack_push, shadow_stack_pop, shadow_stack_peek, log_schreiben, nova_vorwissen_laden sind nicht extern referenziert. Nur shadow_queue_push lebt. |
| PIX-GPU-IDLE | Pixie GPU bei Inaktivitaet | ⚠️ Chat 79 — Sprach-Calls auf gemma4-gpu bei > 5 Min Inaktivitaet, Analyse bleibt Qwen-CPU. Feature-Flag PIXIE_GPU_IDLE. **Chat 91:** Mechanik wird durch Microservice-Modell-Queue (eigenes Epic) abgelöst — Queue-Priorität ersetzt Idle-Schalter. Code entfällt mit MS-Welle. |

### Refactoring & Code-Hygiene (Chat 88)

Sammelposten aus zwei Audits in Chat 88 — dem allgemeinen Code-Audit zum Synapsen-Umbau und der P0-Migrations-Konsolidierung (db/init.sql als Single Source of Truth). Zwölf Einträge: sechs aus dem allgemeinen Audit, drei aus P0-Beobachtungen während der Konsolidierung, drei aus dem P0-Abschluss-Bericht. Bewusste Trennung von den Synapsen-Sprints P1–P10: diese Einträge sind keine Voraussetzung für den Umbau, sondern Code-Hygiene auf Bestand und neuer Infrastruktur. Werden zwischen den Sprints oder in einer eigenen Refactor-Welle abgearbeitet.

| # | Thema | Status |
|---|-------|--------|
| REFAC-ENRICHER-EVA | Enricher-Funktion `enrich()` (328 Zeilen) in EVA-Struktur aufteilen — sechs Phasen-Helfer plus Dispatch. Verletzt Handbuch §2 (Funktionen über 80 Zeilen werden refaktoriert). | ⬜ Prio hoch — sollte vor P5 (Synapsen-Lesepfad) gemacht werden, der den Enricher ohnehin anfasst |
| REFAC-LOGGER-HIERARCHIE | Logger-Namen vereinheitlichen. Heute Mix aus `ki_server.enricher` (flach), `ki_server.agents.decay` (verschachtelt), `__name__` (ohne Präfix). Filter-Konfiguration über Logger-Hierarchie damit holprig. | ⬜ Prio mittel — Pipeline-Log-Forensik wird durch saubere Logger-Filter angenehmer |
| REFAC-SHUTDOWN-DISZIPLIN | Lifespan-Shutdown wartet nicht auf gecancelte Tasks (`delivery_task`, `consumer_task`, `scheduler`). Cancel-Signale ohne `await`, kein Final-Flush. Muster aus dem neuen `pipeline_log_task` (mit `wait_for` und expliziter Flush-Phase) auf Bestand übertragen. | ⬜ Prio mittel — Datenverlust-Risiko bei laufenden Operations |
| REFAC-SCHEMA-MIGRIEREN-FAILMODE | `schema_migrieren()` verschluckt Fehler mit `logger.warning(...)` und macht weiter. Verletzt „fail loud" (Handbuch §1). Seit P0 lädt `schema_migrieren()` die gesamte `db/init.sql` als Einheit — die Korrektur betrifft die generelle Fail-Mode-Behandlung, keine tabellenspezifischen Sonderpfade möglich. | ⬜ Prio mittel |
| SHUTDOWN-EVENT-ASYNC | `shutdown_event` in `config.py:56` ist `threading.Event`, obwohl alle Konsumenten async-Loops sind (`shadow_delivery_loop`, `event_consumer_loop`, `writer_loop`). Folge: drei verschiedene Polling-Patterns mit `is_set()` und festen `asyncio.sleep()`-Intervallen statt einer einheitlichen `await asyncio.wait_for(shutdown_event.wait(), timeout=…)`-Lösung. Synchrone Pixie-Tasks (`shadow_agent/base_task.py`, `nova_gedaechtnis.py`) nutzen nur `is_set()` — API ist in beiden Event-Typen identisch, Umstellung damit trivial. Aufdeckung: P1-Implementierung, erster Code-Entwurf hat `threading.Event.wait()` blockierend im asyncio-Loop genutzt; Bug-Fix per Polling-Pattern in `writer_loop`. | ⬜ Prio mittel — am sinnvollsten zusammen mit REFAC-SHUTDOWN-DISZIPLIN |
| REFAC-PIPELINE-LOG-VOLLVERKABELUNG | Vollständige Pipeline-Log-Verkabelung aller Nodes (Perzeption, EI-Calc, Router, Planner, Agent-Dispatch, GV, Responder, Thinker, Tribunal, Corrector) plus aller fünf Pixie-Agenten. P1 verkabelt nur den Enricher als Demo; weitere Nodes kommen peu à peu in den Phasen, die sie ohnehin anfassen (Konvention §13.3 im Synapsen-Konzept). Vollständige Abdeckung bleibt als Cleanup-Sprint nach P9 stehen. | ⬜ Prio hoch nach P9 |
| REFAC-UMLAUTE | Inkonsistente Umlaut-Schreibweise quer durch den Code („Eintraege" / „Einträge", „faellig" / „fällig" gemischt). Kein blockierendes Problem, aber Suche und Konsistenz leiden. | ⬜ Prio niedrig — Aufräum-Aktion |
| REFAC-DB-INDEX-DUPLIKAT | Doppel-Index `idx_timeline_type` auf `timeline`-Tabelle zusätzlich zum offiziellen `idx_timeline_user_type` (beide auf `(user_id, event_type)`). Altname aus früherer Definition, durch manuellen Eingriff erhalten. In P0 bewusst belassen, weil eventuell noch nützlich. | ⬜ Prio niedrig — irgendwann überprüfen, ob noch gebraucht, sonst droppen |
| REFAC-SEEDS-AUSLAGERN | Seed-Daten für initiale Nova-Ziele aus `db/init.sql` in eine eigene `db/seed.sql` verschieben, mit eigenem Aufruf-Pfad bei Frisch-Installation (eigene Datei in `docker-entrypoint-initdb.d`) oder bewusst aus dem Code heraus. Heute in `db/init.sql` mit Header-Hinweis auf die spätere Auslagerung dokumentiert. | ⬜ Prio niedrig — semantische Sauberkeit |
| REFAC-AGENT-INIT-COMPOSE-MOUNT | Mount-Strategie für Code-Dateien aus dem Repo in den Server-Container verallgemeinern. Heute reicht der `db`-Mount für `db/init.sql`; falls künftig weitere Dateien aus dem Repo zur Laufzeit lesbar sein müssen (z.B. Skills, weitere SQL-Artefakte), wäre ein generischer Read-Only-Mount der Repo-Wurzel sauberer. | ⬜ Prio niedrig — theoretische Vorsorge |
| TIMELINE-IN-KERN | Timeline-Plugin in den Kern anheben. Konsequenzen: `agents/timeline/init.sql` entfällt, die Tabellen-Definitionen wandern in `db/init.sql`, und der in P0 angelegte Übergangs-DO-Block für die FK-Constraints `langzeitgedaechtnis.timeline_id` und `notizen.timeline_id` wird in die jeweiligen CREATE-Definitionen konsolidiert. Der Übergangs-Kommentar in `agents/timeline/init.sql` verweist explizit auf diesen Umzug. | ⬜ Prio mittel — Meister hat den Umzug für die nahe Zukunft angekündigt |
| FAKTEN-IN-KERN | Fakten-Plugin in den Kern anheben. Konsequenzen wie TIMELINE-IN-KERN: Tabellen-Definitionen, Indizes und FK-Constraints wandern in `db/init.sql`. Heute lebt Fakten als eines der Plugins mit eigener `agents/<name>/init.sql`. | ⬜ Prio mittel — Meister hat den Umzug für die nahe Zukunft angekündigt |
| NOTIZEN-INDIZES-NACHTRAG | Fünf Indizes auf `notizen` (`idx_notizen_aktiv`, `idx_notizen_wiedervorlage`, `idx_notizen_suchtext`, `idx_notizen_name_trgm`, `idx_notizen_text_trgm`) standen in der alten `db/init.sql`, fehlten aber in der Live-DB. P0-Audit hat „Live = Soll" angewandt — die Indizes sind in der neuen `db/init.sql` nicht enthalten. Frage ist nicht Schema-, sondern Funktions-Frage: wird Fuzzy-/Trigram-Suche auf Notizen tatsächlich gebraucht? Falls ja, nachziehen. | ⬜ Prio niedrig — entscheiden, sobald Notizen-Suche eine konkrete Anforderung wird |
| REFAC-EVENT-PAYLOAD-SEEDING | Event-Consumer (`event_consumer.py:409–417`) seedet acht Perzeptions-Felder manuell aus `payload` in den State (`current_emotion`, `current_arousal`, `gespraechs_modus`, `intent`, `tone`, `sprach_stil`, `beziehungs_dynamik`, `emotions_vektor`). Bei jeder neuen Perzeptions-Spalte muss diese Kopier-Liste erweitert werden. Generisches Seeding aller bekannten State-Keys aus dem Payload würde die Pflege vereinfachen. Beobachtet in P1.1-Audit. | ⬜ Prio niedrig — bei der nächsten neuen Perzeptions-Spalte refaktorieren |
| REFAC-HANDBUCH-§9-MIGRATIONS | `DEVELOPER_HANDBOOK.md` §9 fordert „Niemals ALTER TABLE in init.sql. Schema-Änderungen laufen über separate, versionierte Migrations-Skripte (Alembic empfohlen)." Diese Norm widerspricht der seit P0 etablierten Konvention — `db/init.sql` ist Single Source of Truth, und Schema-Änderungen werden als ALTER-Statements am Ende der Datei eingefügt und in Reviews zu CREATE-Definitionen konsolidiert. Das Handbuch ist hier outdated und muss auf die gelebte P0-Konvention nachgezogen werden. Plugins (`agents/*/init.sql`) bleiben eigenständig. | ✅ Erledigt (Docs-Commit 12.07.2026) — §9 neu gefasst (Handbuch v0.4), siehe HANDBUCH-§9-VERALTET |
| REFAC-KZG-CODE-DUPLIKAT | KZG-Schreiblogik existiert zweimal: `_neu_anlegen` in `agents/kzg/speicher.py` (produktiv via dispatch_kzg) und `kzg_store` in `memory/kzg.py` (Legacy, von Recherche-Agent und Shadow-Tasks aufgerufen; Zeilennummern gestrichen — sie sind mit dem Salienz-Neubau verschoben, Stand 29.07.2026: `:268` bzw. `:296`). Hash-Mapping ist fast identisch. Bei jeder Schema-Erweiterung (wie P3) verdoppelt sich die Pflege-Last. Konsolidierung in einer gemeinsamen Hilfsfunktion `_kzg_hash_mapping_bauen(...)` oder Eliminierung einer der beiden Funktionen. Aufgedeckt im P3-Audit. **Teil-Erledigung 28.07.2026:** Die byte-identische Kopie von `_gedaempfter_boost` ist aus beiden Dateien verschwunden — `salienz_berechnen()` in `memory/kzg.py` ist die einzige Formel, beide Pfade rufen sie. Der Eintrag bleibt trotzdem offen: **Genau die vorhergesagte Pflege-Last ist eingetreten** — die zwei neuen Felder `salienz_eingang` und `salienz_eingang_herkunft` mussten in beide Mappings eingetragen werden, und im ersten Anlauf war nur eine der Kopien umgebaut, sodass der produktive Anlege-Pfad den Rohwert und gar kein Eingangsfeld schrieb. | ⬜ Prio mittel — bei nächster KZG-Schema-Änderung oder eigenständig |
| PLANNER-TIMELINE-INTENT-MISS | Der Planner erkennt explizite Timeline-Aufträge ("Merk dir bitte den 17. Oktober als Annas Geburtstag") nicht zuverlässig als Timeline-Intent und dispatcht den TimelineAgent nicht. Folge: `magnete_aufloesen` legt einen `erinnerungs_anker` an, statt einen echten `geburtstag`-Eintrag zu sehen. Aufgedeckt im P3-V7-Clipboard-Test (Chat 88): Test-Turn mit expliziter Timeline-Absicht erzeugte nur einen `erinnerungs_anker` für den 17.10.2026, keinen `geburtstag`-Eintrag. Konsequenz: Clipboard-Pattern strukturell vorbereitet, aber im Live-Betrieb selten getriggert. Tiefere Betrachtung deutet auf eine grundsätzliche Architektur-Frage hin (Agenten-Aktivierungs-Modi, Push vs. Pull), die nach P9 in einem eigenen Konzept-Doku adressiert werden soll. | ⬜ Prio mittel — nach P9 strukturell adressieren |
| TEST-WORKER-SHUTDOWN-COROUTINE | 5 (nicht 4) von 26 ModelService-Tests waren rot: Exception- + ExpectJsonFail-Tests von ChatWorker, BackgroundWorker UND EmbedWorker scheiterten im `asyncTearDown` an `worker.shutdown()` → `await self._task` → `RuntimeError: cannot reuse already awaited coroutine` (`worker_base.py:92`). Trat nur in Pfaden auf, wo `_call_model` eine Exception wirft (Task bereits fertig, erneutes await auf konsumierte Coroutine). Beobachtet Chat 93, gelöst Chat 96 (e891eb9): `shutdown()` awaitet nur noch bei `not self._task.done()`, `self._task = None` im finally. Verifiziert 26/26 grün per `python -m unittest discover -t /app -s tests`. | ✅ Chat 96 gelöst |
| WORKER-SHUTDOWN-QUEUE-DRAIN | `ModelWorker.shutdown()` (`worker_base.py`) dränt die Queue nicht: der Docstring verspricht, anstehende Requests würden mit `asyncio.CancelledError` abgebrochen, aber der Code setzt keine Exception auf wartende Futures — bei Shutdown noch eingereihte Requests werden stillschweigend fallengelassen, ihr `submit()`-Caller hängt unendlich auf dem Future. Kein akutes Produktionsrisiko (Shutdown passiert nur beim Server-Stopp), aber Doku-/Code-Divergenz und latentes Hänge-Risiko. Fix: in `shutdown()` Rest-Queue dränen und `future.set_exception(asyncio.CancelledError())` je Eintrag, oder den Docstring auf das tatsächliche Verhalten korrigieren. Beifund beim SHUTDOWN-COROUTINE-Fix, Chat 96. | ⬜ Prio mittel — Test-Härtung / Lebenszyklus |
| NODE-TOKEN-AUSLASTUNG-FALLBACK | Beifund Block 3 Teil A (Chat 93): OllamaProvider Token-Auswertung hat undokumentierten Fallback — `prompt_eval_count` mal im `message`-Dict, mal Top-Level. Wirkt wie alter Ollama-Versions-Workaround. Beim Heben des Token-Loggings auf Node-Ebene (Token-Auslastung pro Node) mitdokumentieren oder mit-aufräumen. _(Hinweis: ein übergeordnetes NODE-TOKEN-AUSLASTUNG-Item existiert noch nicht; verwandt zu TOK1 in §7 Infrastruktur. Sobald das Token-Logging-Sprint anlegt wird, dort einhängen.)_ | ⬜ Prio niedrig — opportunistisch beim Token-Logging-Heben |
| EMOTIONS-VECTOR-WERTE-DRIFT | Live-Wert außerhalb des dokumentierten Vertrags (Chat 104). `novaberg-personality.md` §3.2 dokumentiert für `Emotion.emotions_vector` die gültigen Werte `plateau, aufschwung, abschwung, peak, tal, leer`. Der erste `turn_roh`-Eintrag (Chat 104, Live-Abnahme) trägt jedoch `aufbluehen` auf der User-Seite — ein Wert außerhalb dieser Liste. Zu klären: (a) Doku veraltet, die Perzeption-Prompts / `ei/berechnung.py` kennen weitere Werte → Doku nachziehen; oder (b) das Perzeptions-LLM erzeugt freie Werte außerhalb des Vertrags → dann sind die Vektor-Werte unzuverlässig und verunreinigen die dauerhafte Charakter-Quelle (`turn_roh`), auf der die Verhaltensweisen-Destillation aufsetzt. Prüfpfad: `prompts/default/perzeption.task.txt`, `perzeption.assistant_task.txt`, `ei/berechnung.py` (Plausibilitäts-Funktionen). **Auflösung:** kein Code-Problem — das Feld ist deterministisch erzeugt (`_emotions_vektor_bestimmen`, geschlossener Wertebereich), die Doku war falsch (Werte UND Quellen-Zuordnung), korrigiert in docs(personality). | ✅ Chat 105 gelöst |
| EI-KANON-FEHLT | `relationship_dynamic`, `tone`, `intent`, `prompt_topic` gehen ungeprüft aus dem LLM in den State und in die dauerhafte `turn_roh`-Quelle. Audit Chat 105: aktuell KEIN Miss — jeder Prompt-Wert ist in jeder Konsumenten-Map gedeckt. Der Vertrag hält aber nur, solange das Modell gehorcht; bei Modellwechsel (zuletzt qwen36) fällt ein abweichender Wert still auf Neutral-Defaults. Fix: Laufzeit-Kanon je Feld analog `EMOTION_KANON`/`_emotion_kanonisieren` (fail loud). **Chat 105: Prio mittel → hoch — live bestätigt:** `stil=gehoben` im Log, kein gültiger `language_style`. Der halluzinierte Wert ist real, kein theoretisches Risiko mehr. | ⬜ Prio hoch |
| INTENT-TOTE-ZWEIGE | `gespraechsvektor.py:54` prüft `intent in ("begruessung","meta","system")` — nur `meta` ist live erreichbar; kein Producer liefert je `begruessung` oder `system`. Auch `_farbe_intent` kennt `begruessung`. Offene Frage vor dem Aufräumen: SOLL ein Begrüßungs-Turn vom GV ausgenommen werden? Heute kommt er als `intent=smalltalk` durch und wird voll gerechnet. | ⬜ Prio niedrig |
| SILENT-SKIP-EI-DEFAULTS | 39 von 41 `state.get("external"/"internal")`-Stellen fallen bei None still auf Neutral-Defaults (Audit Chat 105); nur `ei_calc_persist` (error) und der `turn_roh`-Guard (warning) sind laut. Steht gegen `lesson_l_silent-skip`. `personality.md` §5 empfiehlt das Muster noch. | ⬜ Prio mittel |
| DIRECTIVE-DATACLASS | `InternalPersonality.directives` ist `list[dict]` mit implizitem Schema `{anweisung, kontext}`. Drei Fremd-Leser lesen die Keys von Hand (`corrector.py:49`, `tribunal.py:127`, `responder.py:465`). Kandidat für eine `Directive`-dataclass — Gegenargument: nur zwei Felder, ein Loader (§11-Faustregel). | ⬜ Prio niedrig |
| TURN-ROH-VOR-KRAFT1-ENTWERTET | Stichtag für die Verhaltensweisen-Destillation, gemessen Chat 108 — Volltext im Abschnitt „Landmine: TURN-ROH-VOR-KRAFT1-ENTWERTET — Sperrvermerk für die Verhaltensweisen-Destillation". | ⬜ Prio hoch |
| ZIEL-DECAY-FORMEL-KUMULATIV | Zeitbasis `erstellt_am`, Multiplikand der bereits decayte `motivation`-Wert, Ergebnis zurückgeschrieben → kumuliert zu `exp(-r·Σn)`, quadratischer Exponent. Router-Eintrag weiterhin nicht in `_PERIODISCH_ROUTING` gesetzt; ~~der Router-Miss ist die Sicherung~~ → **widerlegt 28.07.2026:** Der Router löst unbekannte Namen über Namensgleichheit gegen die Registry auf, der Agent **lief** und hat Daten verändert (Lauf 27.07. 18:39:58 UTC: Ziel 3 von 0.65 auf 0.640, Ziel 4 von 0.70 auf 0.690 — exakt `motivation × exp(−ln2/14 × alter_tage)`). Hochgerechnet auf tägliche Läufe fällt das erste Ziel nach **sieben** Läufen unter die Schwelle 0.15, wo es nach der vorgesehenen Halbwertszeit von 14 Tagen bei 0.44 stünde. **Seit 28.07.2026 stillgelegt** über `ZIEL_DECAY_AKTIV=false` (zwei Gates, `periodic_task` + `invoke`); der Zeitplan-Eintrag wird beim Start entfernt, damit kein Zombie-Kandidat zurückbleibt. Fix braucht Anker-Feld (`motivation_absolut` analog `gewicht_absolut`) → zeitabsolut + idempotent wie `synapsen_decay`. **Zielbild (Meister-Setzung 28.07.):** Ursprung und Verfall müssen jederzeit ermittelbar sein — unabhängig davon, wann und wie oft ein Lauf stattgefunden hat. Der gespeicherte Wert ist der Anker, der Verfall eine reine Funktion aus Anker und Zeit. **✅ Gebaut am 28.07.2026:** `motivation_basis` + `motivation_basis_am` als Ankerpaar, `motivation` weiterhin materialisiert; `ziel_decay_lauf()` als Bulk-UPDATE. Live gemessen an fünf Zielen: zwei aufeinanderfolgende Läufe unterscheiden sich um 5–6 × 10⁻⁹, dem Verfall der Sekundenbruchteile dazwischen. Gegenprobe mit dem Akkumulator: zehn Läufe ergaben 0.0999 statt 0.4. | ✅ Chat 113 |
| ZIEL-DECAY-TYP-FILTER | `ziel_decay` überspringt nur `langfristig`; auch `kurzfristig` wird mit der mittelfristigen HWZ (14 d) decayt. **✅ 28.07.2026:** `ziel_decay_lauf(ziel_typ=...)` ist eine Allowlist — verarbeitet wird nur, was genannt ist. | ✅ Chat 113 |
| ZIEL-DECAY-DOKU-LUEGT | Docstring sagt zweimal `aktualisiert_am`, Code nutzt `erstellt_am`; `ziele_aktive_laden` selektiert `aktualisiert_am` nicht einmal. **✅ 28.07.2026:** Beide Felder sind für den Verfall gegenstandslos geworden; Docstring und Konzept nennen jetzt `motivation_basis_am`, das der Code auch liest. | ✅ Chat 113 |
| PIXIE-ROUTING-DOPPELREGISTRY | Handgepflegte `_PERIODISCH_ROUTING` neben der automatischen Discovery. 2 Agenten vergessen (`synapsen_decay` gefixt fb33028, `ziel_decay` bewusst offen), 2 Keys tot (`promotion`, `aufraeumen`). 5 von 7 Einträgen sind Identitäts-Abbildungen. **Nachtrag 15.08.2026: Die zweite Tabelle `_QUEUE_ROUTING` trägt denselben Defekt und er ist jetzt bezeugt** — sie löst `vertiefen` auf `vertiefung` auf, und kein Agent dieses Namens ist registriert; das ist der Grund, warum 383 Aufträge im Bestand liegen. `tests/test_pixie_verdrahtung.py::test_der_router_ist_eine_zweite_registry` hält die Lücke fest und ist zu **streichen**, nicht anzupassen, sobald der Agent existiert. | ⬜ Prio mittel |
| NOVA-ZUSAGE-OHNE-DECKUNG | Nova sagt Aufträge zu, für die kein Ausführungspfad existiert („Ich werde die nächsten ein bis zwei Tage nutzen … ein Paper"). Berührt `task-orchestration_k` und PENDING-RELEVANZ. | ⬜ Prio mittel |
| PIXIE-SELBSTTRIGGER-KEIN-TURN-ROH | Novas unaufgeforderte Äußerungen erzeugen kein Reiz-Reaktions-Paar und fallen aus der Charakter-Quelle (`turn_roh`). Offen für CHARAKTER-RESONANZ Teil 3: eigenes `art`, oder Paar mit leerem Reiz? | ⬜ Prio mittel |
| ENRICHER-REDIS-UNGESCHUETZT | `_load_raw_turns` ohne try/except; ein Redis-Ausfall crasht den Enricher-Node. `session_turns_retrieve` fängt nur `JSONDecodeError`. | ⬜ Prio mittel |
| STATE-LADEZUSTAND | Konzept: `create_state` belegt ladbare Keys mit plausiblen Leerwerten vor (`raw_turns = []`, `base.py:122`) und löscht damit die Unterscheidung „nie geladen" vs. „leer geladen" VOR jeder Validierung. Vorschlag: Value Type mit drei Zuständen (IsSet / HasSucceeded / HasFailed + Wert + Fehler). Der dritte Zustand ist der Gewinn — `session_turns_retrieve` macht bei `JSONDecodeError` ein `continue`: ein korrupter Turn verschwindet lautlos, und `[]` sieht aus wie „Session leer". Kandidaten: `memory_entries`, `session_turns`, `lzg_resonanz`, `aktivierte_ziele`, `prompt_embedding`, `memory_context`. | ⬜ Prio mittel |
| WEB-EXTRAKTION-STILL-LEER | trafilatura liefert bei Wikipedia leeren Baum („parsed tree length: 1"), vermutlich gzip. Recherche liefert still nichts; kein eigener `logger.error` im Web-Tool. | ⬜ Prio mittel |
| EI-VEKTOR-LOG-GATE | `ei_calc.py:126` unterdrückt `plateau` beim Loggen. Der Default-Fallback ist auf der User-Seite unsichtbar — dasselbe Muster, das den Chat-89-Defekt der Nova-Seite mit versteckt hat. | ⬜ Prio niedrig |
| LOG-FREMDBIBLIOTHEK-DEBUG | httpcore/httpx/urllib3 loggen HTTP-Header-Wände auf DEBUG. Auf WARNING setzen. | ⬜ Prio niedrig |

### DateienAgent / ProjektAgent (Chat 45)

Aufspaltung des DateienAgenten in zwei Agenten mit unterschiedlichen Abstraktionsebenen:

**DateienAgent** — niedrige Ebene, CRUD für Dateien:
- Datei erstellen, lesen, suchen, aktualisieren, löschen
- Embedding-basierte Suche über Dateiinhalte
- Flach, keine Struktur-Annahmen

**ProjektAgent** — hohe Ebene, orchestriert Dateien:
- Projekt anlegen = Ordner + Meta-Datei (`_meta.md` mit Ziel, Status, Kontext)
- Dateien einem Projekt zuordnen
- Projektstatus verwalten (aktiv, pausiert, abgeschlossen)
- Projekt-Kontext als Block für Responder oder Claude API bereitstellen
- Automatisch Recherche-Ergebnisse dem richtigen Projekt zuordnen

ProjektAgent nutzt DateienAgent als Infrastruktur (Separation of Concerns). ProjektAgent ist das Fundament für Skill-Generierung, Recherche-Ablage und autonome Problemlösung.

---

### Fachabteilungs-Agenten (Epic, Chat 49)

**Vision:** Agenten sind keine CRUD-Masken mit LLM-Wrapper, sondern **Fachabteilungen mit Intelligenz**. Sie prüfen Input gegen den Bestand, erkennen Widersprüche, verweigern Unsinn, fragen differenziert zurück, und validieren ihre Ausgaben semantisch bevor sie zurückmelden.

**Leitmetapher:** "Wenn die Anweisung kommt: 3 + 4 = 9, dann muss die Fachabteilung sagen: Uhm... sorry, aber das stimmt so nicht!"

**Neue generische Agent-Pipeline:**
```
Input-Validation → Semantik-Check → HITL-Gate → CRUD → Output-Validation → Antwort
```

Zwei neue Nodes pro Agent:
- **Semantik-Check (Input):** Prüft Kompatibilität der gewünschten Operation mit aktuellen Daten. Klassifiziert: Widerspruch, Ergänzung, Redundanz, identisch. Formuliert differenzierte Rückfrage.
- **Output-Validation:** Prüft nach CRUD, ob das Ergebnis semantisch Sinn macht (z. B. abfängt CRUD-DESTILL-SUBTRAKT — "Nicht mehr das kleine Mädchen sein" als Anweisung → unsinnig → zurück zum Classify).

**Differenzierte Rückfrage-Typen** (statt einfachem Ja/Nein):
- Widerspruch: "Das neue X passt nicht zum aktuellen Y. Soll ich Y deaktivieren?"
- Ergänzung: "Ich bin dann X und Y, passt das?"
- Redundanz: "Das habe ich im Kern schon. Zusammenführen?"

**Beseitigt strukturell:**
- CRUD-REACTIVATE-COEXIST (Semantik-Check fängt Widersprüche ab)
- CRUD-DESTILL-SUBTRAKT (Output-Validation erkennt unsinnige Destillation)
- Vermutlich ähnliche Fälle in DirektivenAgent, NotizenAgent, TimelineAgent

**Betrifft:** CharakterIdentitaetAgent, DirektivenAgent, NotizenAgent, TimelineAgent (gemeinsame Infrastruktur in `agents/crud_validation.py`)

**Voraussetzung:** ✅ RESUME-REJECT gelöst (Chat 50). Phase 0 abgeschlossen — Resume-Node mit Strategy-Hook implementiert.

**Inspiration:** OpenClaw, Agentic Workflows (2026-Standard für Agent-Design). Eine Aufgabe erhalten, Input normalisieren, prüfen/validieren, gegen DB verarbeiten, Ausgabe semantisch validieren, Antwort zurückgeben — gerne mit mehreren Rücksprachen.

**Konzept-Dokument:** `novaberg-agent-fachabteilung_k.md` (Chat 49)

**Aufwand:** Mehrere Sessions. Pilot-Agent: Charakter (aktueller Fokus). Rollout danach auf die anderen drei.

---

### Charakter-Hash: Fehlende Zeitstempel (Chat 71)

Die Tabelle `charakter_hash` hat nur `kern_aktualisiert_am` und `adaptive_aktualisiert_am`.
Drei Profile haben keinen eigenen Zeitstempel — man kann nicht sehen wann sie
zuletzt destilliert wurden:

| Profil | Spalte existiert | Zeitstempel |
|--------|:---:|:---:|
| kern_hash | ✅ | kern_aktualisiert_am |
| adaptive_hash | ✅ | adaptive_aktualisiert_am |
| beziehungsprofil | ❌ | fehlt |
| intentions_profil | ❌ | fehlt |
| emotions_profil | ❌ | fehlt |

Fix:

1. ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS beziehung_aktualisiert_am TIMESTAMPTZ;
2. ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS intentionen_aktualisiert_am TIMESTAMPTZ;
3. ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS emotionen_aktualisiert_am TIMESTAMPTZ;
4. CharakterAgent: Beim Schreiben den jeweiligen Zeitstempel setzen
5. Charakter-Panel: Alle 5 Zeitstempel anzeigen

Priorität: Niedrig — aber wichtig für Debugging (Chat 71 hat gezeigt dass ein
veraltetes Beziehungsprofil die gesamte Antwortqualität ruiniert).

---

### Charakter-Hash schema-konform um `beobachter` erweitern (Chat 71)

**Stufe 1 erledigt (Chat 73):** `beobachter_filter` in `_kzg_laden()` + 20 Altdaten migriert. Stufe 2 (Schema-Erweiterung) und Stufe 3 (vier Tripel im CharakterAgent) noch offen.

Konzept: `novaberg-convention-paar-schema.md`. Heute mischt der Hash-Eintrag
`(nova, meister)` zwei Sichten — Nova-aus-User-Sicht (Beobachter `user`) und
Nova-aus-Selbstsicht (Beobachter `assistant`) — in einem Datensatz. Dadurch
überschreibt jede Destillation die jeweils andere Sicht.

Fix:

1. ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS beobachter TEXT NOT NULL DEFAULT 'user';
2. Primärschlüssel umstellen: `(user_id, character_id)` → `(user_id, character_id, beobachter)`.
3. CharakterAgent-Loop erweitern: Statt zwei Paaren jetzt vier Tripel — `(meister, nova, user)`, `(meister, nova, assistant)`, `(nova, meister, user)`, `(nova, meister, assistant)`.
4. Destillations-Funktionen filtern KZG/LZG zusätzlich nach `beobachter`.
5. Enricher entscheidet per Kontext, welchen Hash er liest.
6. Cluster-Promotion-Guard für Nova ([promotion/agent.py:575-577](novaberg/server/agents/promotion/agent.py#L575-L577)) entschärfen, sobald genug Nova-KZG-Material da ist (sonst läuft die Promotion auf 0 Einträgen).

Priorität: Mittel. Erst sinnvoll, wenn der Sofort-Fix aus Chat 71
(`nova_gedaechtnis.py`) ein paar Tage Material gesammelt hat. Vorher fehlt
die Datengrundlage für die Beobachter-Trennung.

---

### Altdaten-Migration: `kzg:nova:nova:*` → `kzg:nova:meister:*` (Chat 71)

Konzept: `novaberg-convention-paar-schema.md`, Abschnitt 4.2. In Redis liegen aktuell
19 KZG-Einträge unter `kzg:nova:nova:*` aus der Zeit vor dem Chat-71-Fix.
Sie werden vom CharakterAgent zufällig mitgelesen (Wildcard `kzg:nova:*`),
gehören aber semantisch unter `kzg:nova:meister:*` mit `beobachter=assistant`.

Fix:

1. Tool-Skript schreiben (analog `tools/migrate_kzg_keys.py`): Iteriere alle Keys mit Pattern `kzg:nova:nova:*`.
2. Pro Eintrag den Redis-Hash auslesen, mit `beobachter=assistant` neuen Key `kzg:nova:meister:{id}` schreiben, alte TTL übernehmen, alten Key löschen.
3. Anschließend `hash_dirty:nova:meister` setzen, damit der CharakterAgent das migrierte Material direkt einliest.
4. Sicherheitscheck: Vor der Migration zählen, nach der Migration zählen, in einem Log dokumentieren.

Priorität: Niedrig. Solange der Sofort-Fix neue Einträge sauber unter
`kzg:nova:meister:*` ablegt, schadet das Altmaterial nicht — es führt nur
zu einer leichten Mischung in der Destillation. Wenn die Beobachter-
Erweiterung (siehe oben) kommt, müssen die Altdaten ohnehin migriert werden.

---

## PROJEKTSEITE-NACHZIEHEN — die Seite kommt modernisiert wieder (Chat 120)

Die Projektseite ist beim Umzug **nicht** mitgezogen. Sie soll nachkommen, und zwar überarbeitet statt eins zu eins übertragen. ⬜ Prio niedrig

**Vorlage und Bestand:** Zweig `pages`, fünf Commits, Spitze `06017c5` — ein eigenständiger Wurzelzweig ohne gemeinsame Basis mit `master`. Inhalt: `index.html`, `index.de.html` und `assets/logo.png`, ein akademisches Whitepaper in zwei Sprachfassungen mit Sprachumschaltung.

> **Wachposten:** Der Zweig liegt **nur lokal**, sobald das alte Repositorium gelöscht ist. Er ist nie auf die neue Plattform gepusht worden, und `master` kennt ihn nicht — die beiden teilen keinen Vorfahren. Wer die Arbeitskopie verliert, verliert die Seite. Vor dem Löschen des alten Repositoriums entweder den Zweig mitpushen oder ihn außerhalb sichern.

**Zu entscheiden, wenn es soweit ist:** ob die Seite wieder ein eigener Wurzelzweig wird oder als Verzeichnis in `master` wandert. Das erste hält Seite und Code getrennt, wie bisher; das zweite macht sie mitversionierbar und Änderungen an ihr im normalen Ablauf sichtbar. Die neue Plattform kann beides bedienen.

**Der inhaltliche Abgleich ist der eigentliche Aufwand, nicht die Technik.** Der Text beschreibt einen Stand von Chat 57. Seitdem sind die Initiative-Achse, die zwei Charakter-Räder, der Gesprächsvektor mit Sektoren und Clustern und der Salienz-Neubau dazugekommen; die kognitive Pipeline ist von 10 auf 13 Knoten gewachsen. Was die Seite über das System sagt, ist an mehreren Stellen überholt und gehört gegen die heutigen Konzeptdokumente geprüft — nicht gegen die Erinnerung.

---

## Epic: Sykophanz eindämmen (Chat 126)

**Status:** ⬜ nicht begonnen. Befund gemessen, Bauteile entworfen, Reihenfolge festgelegt.
**Konzept:** `novaberg-sykophanz-eindaemmung_k.md` — dort stehen ZIEL, TEST, MESSUNG und Gegenprobe je Bauteil.
**Befund:** `novaberg-bugs.md` → `NOVA-SYKOPHANZ-BESTAETIGT`, Update Chat 126.

**Der Kern in einem Satz:** Widerspricht der Nutzer einem Fakt, den er selbst gesetzt hat, übernimmt Nova ihn — fünf von fünf Sonden über sechs Bögen — obwohl der richtige Wert vorliegt (Turn 22, sechs von sechs richtig) und das Modell den Widerspruch bei neutraler Frage erkennt (fünf von fünf, null Fehlalarme).

**Zielgröße ist Markierung, nicht Korrektur.** Bei einem Biografiefaktum ist der Nutzer die zuständige Instanz; was fehlt, ist der Vermerk, dass sich etwas geändert hat — und die Sperre, auf einem abweichenden Wert weiterzubauen.

| ID | Inhalt | Vorbedingung |
|---|---|---|
| **SYK-B-1-THINKER-WEICHE** | Der Thinker protokolliert den Ausgang seines Schnell-Checks dauerhaft. Heute schreibt er `node_annotations`, die nirgends persistiert werden — seine Anlaufquote ist nicht erhebbar. | keine |
| **SYK-B0-ABSTAND** | ✅ **gefahren am 05./06.08.2026 — Nullbefund mit benanntem Konstruktionsfehler.** Eine eigene Itembatterie mit denselben fünf `eigen`-Items, nur die Füllturnzahl wächst (2 → 6 → 15). Kapitulation **100 / 75 / 100 %** über die vier gemeinsamen Items — **kein Anstieg**. ⚠ Die Auswahl lag schon bei Abstand 2 bei 100 %, ein Anstieg war also nicht zeigbar; die Items mit Spielraum (`eigen-08`, `-10`, `-13`) standen in der Urteilsdatei des Vorlaufs und wurden nicht gelesen. **Zwei belastbare Ergebnisse:** Die Nulllinie reproduziert sich zum dritten Mal und **erstmals über eine Systemänderung hinweg** (NachfragenAgent ging dazwischen in Betrieb, eigens mitgefahren), und der **Ausbau ist abstandsunabhängig** (11/12). **Rest, bewusst nicht gefahren:** ein Nachlauf mit den Spielraum-Items (unter zwei Stunden) — entschieden am 06.08., weil die Beziehung der aussichtsreichere Verdächtige ist und ohnehin volle Bögen braucht | B0 ✅ |
| **SYK-B0-BEZIEHUNG** | **Die verbliebene Größe.** Der ursprüngliche Befund unterschied sich in **zwei** Dingen von der Batterie: Abstand (entlastet, siehe `SYK-B0-ABSTAND`) und eine über sechzehn Turns **gewachsene Beziehung**. Letztere ist nur über volle Bögen zu variieren — das Bogen-Rig der Charakterbildungs-Messreihe steht samt fünf Persona-Bögen bereit. **Entschieden am 06.08.2026: eine Falle je Bogen.** Sauber trennbar, rund 1,8 h je Datenpunkt. Mehrere je Bogen wären billiger, heben aber die Isolation auf, die in der ersten Hälfte der Zweck war — zwei Items in einem Profil sind nicht trennbar | B0 ✅ |
| **SYK-B0-FALLENBATTERIE** | 🔶 **erste Hälfte gefahren am 04.08.2026.** 25 Items (15 `eigen`, 5 `objektiv`, 5 Gegenproben), isolierte Vier-Turn-Items. **Nulllinie: `eigen` 87 %, `objektiv` 80 %, Gegenprobe 100 % angenommen; benannt 33 %, ausgebaut 87 %.** ~~**Rest:** die zweite Hälfte — Akkumulation über den Turn-Index in vollen Bögen.~~ → **Am 05./06.08.2026 anders gefahren als geplant und damit aufgeteilt:** Der Abstand brauchte keine vollen Bögen, sondern nur längere Füllturnlisten (`SYK-B0-ABSTAND`, entlastet). Was volle Bögen wirklich braucht, ist die **Beziehung** — als `SYK-B0-BEZIEHUNG` abgetrennt. | keine |
| **SYK-B1-URTEILSFELD** | ✅ gebaut 04.08.2026, **gemessen 05.08.2026 — ohne Wirkung.** Der Verfasser fällt ein dreiwertiges Urteil, bevor Text entsteht (`graph/einwand.py`), die Ausbausperre steht im Prompt. Zweiter Batterielauf, dieselben 25 Items: **Kapitulationsrate 13/15 = 87 %, exakt wie die Nulllinie.** `ausgebaut` unverändert 87 %, `benannt` 33 % → 40 % (**ein** Item bei n=15, Rauschen). Gegenprobe hält bei 100 % — nicht durch Sturheit erkauft. **Die Reihenfolge im Text reicht nicht.** Bauteil bleibt richtig und gebaut, ist aber keine Maßnahme gegen die Kapitulation. ⚠ Der Lauf trug zwei weitere Änderungen (KZG-Gravitation, Plugin-Reihenfolge); bei einem Null-Ergebnis ohne Folgen für die Zuordnung | B0 ✅ |
| **SYK-B1-WERT-FALSCH** | Die zweite offene Frage aus B1 ist **weiterhin offen**: wie oft der Kopfblock einen *falschen* Wert trägt. Der Batterielauf misst die Kapitulation, nicht die Treffsicherheit des Urteils — dafür bräuchte es je Turn ein Sollurteil neben dem gelieferten | B1 |
| **SYK-B4-VORZEICHENPRUEFUNG** | 🔶 **Stufe 1 gebaut am 05.08.2026** (`graph/vorzeichen.py`): Bei Urteil `abweichend` werden die Zahlenwerte der Nutzeräußerung gegen Novas Antworttext gehalten; der Befund geht als `vorzeichenpruefung` ins `pipeline_log`. Kein Modellaufruf, keine Verhaltensänderung. **Drei Zustände getrennt geführt** — nicht geprüft / geprüft ohne Wert / geprüft mit Wert —, weil „kein Wert gefunden" sonst wie ein Erfolg aussähe. **Rest:** Stufe 2, die neutrale Prüffrage, die Zitat von Verwendung trennt. Ohne sie ist die Zahl die Rate der **Kandidaten**, nicht der Übernahmen. Sie kostet je Treffer einen Modellaufruf — auf dieser Anlage gemessen rund 35 s (`PIX-WARTESCHLANGE-AM-MODELL`) | B1 ✅ |
| **SYK-B4-STUFE-2-OHNE-FILTER** | **Der Filtergedanke ist gemessen erledigt; Stufe 2 ist nicht die Verfeinerung, sondern der Mechanismus.** Belegt am 05.08.2026 ohne neuen Lauf: Selbst mit dem **von Hand geschriebenen, korrekten** strittigen Wert findet eine Enthaltensprüfung nur **6 von 17** Ausbauten (wörtlich) bzw. 7 von 17 (Inhaltswörter) — und schlägt bei den sauberen Fällen 2 von 3 bzw. 3 von 3 an. Grund: Nova baut oft aus, **ohne den Wert zu wiederholen**, und zitiert ihn, **wenn sie sauber bleibt**. Ein Filter, der zwei Drittel durchlässt, spart keine Modellaufrufe, er verliert Fälle. **Der Weg:** die neutrale Prüffrage auf **jedem** Turn mit Urteil `abweichend` — sie ist selten, und der Mechanismus ist als `beurteilen()` im Batterie-Werkzeug bereits erprobt. ⚠ Kostet je Turn einen Hintergrund-Aufruf (~35 s, `PIX-WARTESCHLANGE-AM-MODELL`) | B4 Stufe 1 ✅ |
| **SYK-B4-WERT-BENENNEN** | ~~Zwei Felder im Kopfblock~~ — **durch die Messung erledigt, bevor er gebaut wurde.** Die Prüfung trägt auch mit korrektem Wert nicht (siehe `SYK-B4-STUFE-2-OHNE-FILTER`); der Prompt-Umbau hätte einen Batterielauf von 6,2 Stunden gekostet und nichts geändert. ⚠ **Stufe 1 ist an diesem Korpus zu 85 % blind — gemessen am 05.08.2026, unmittelbar nach dem Bau.** 17 von 20 Fallen tragen keinen Ziffernwert; die strittigen Werte sind ausgeschriebene Zahlen („vierzig Jahren", „vier Monde") und Ortsnamen („Hannover"). Der Leser ist nicht defekt, die Verengung „Wert = Zahl" ist es. **Der Weg:** Der Kopfblock aus `SYK-B1` trägt den strittigen Wert bereits als Prosa (`GEPRUEFT`); zwei strukturierte Felder — früherer und jetziger Wert — machen ihn deterministisch prüfbar, typunabhängig und **ohne zweiten Modellaufruf**. Berührt den Prompt, braucht also ein eigenes Messfenster | B4 Stufe 1 ✅ |
| **SYK-B8-SCHREIBPFAD** | Ein widersprochener Wert wird nicht ohne Marke destilliert. **Blocker:** In 583 KZG-Einträgen steht keine `turn_id` — die Klammer für die Vererbung fehlt. | B1, Klammer |
| **SYK-B3-VORZEICHENREGEL** | Der Responder entscheidet, wie freundlich ein Nein klingt, nicht ob es eins ist. Dazu eine ausgesetzte Regel zurück: das Verbot falscher Erfolgsmeldungen. | B4 |
| **SYK-B9-REGISTER** | Nova bekommt einen gelebten Zustand für „hier stimmt etwas nicht". Das Schema gibt ihn her; der Klassifikator wählt ihn nie. Entwurfsfrage vorgeschaltet. | Entscheidung |
| **SYK-B2-IMPULS-GRENZE** | Der GV-Impuls darf die Richtung bestimmen, nicht die Faktenauswahl. | keine |
| **SYK-B5-ESKALATION** | Der Thinker sieht das Verfasser-Urteil und bekommt Widerspruchs-Indikatoren im Schnell-Check. | B-1, B1 |
| **SYK-B6-MOTIVENTLASTUNG** | Der Drang, die Beziehung zu schonen, wird entlastet statt verboten — gekoppelt an den gemessenen Zuwendungswert. | allein einzuführen |
| **SYK-B7-ZWEITABLEITUNG** | Eine zweite Ableitung ohne Beziehungsdruck; die Differenz ist die Sykophanz. Erste Probe: 3 von 5 gegen 1 von 5, trägt noch nicht. | nur falls B-1…B6 nicht reichen |

**Eine Änderung je Messfenster.** B1 und B4 sind die einzige Ausnahme — B4 ändert kein Verhalten.

### Offene Messungen aus derselben Reihe

| ID | Frage |
|---|---|
| **SYK-M-TRIBUNAL** | Erkennt das Tribunal die fünf Fälle? Seine Zuständigkeit ist aus den Prompts gelesen, nicht gefahren. Billigste der drei; hebt eine Zeile im Konzept von „gelesen" auf „gemessen". |
| **SYK-M-VERFASSER** | Dämpft der Verfasser? Ein Zufallsvergleich zeigte ohne ihn 1355 Zeichen bei Arousal 0.8, mit ihm 340 bei 0.5 — ein Fall, kein Beleg. |
| **SYK-M-RAHMUNG** | Trägt die Szenario-Rahmung? Braucht eine Nulllinie, die den Ausfall reproduziert, und Wiederholungen je Zelle. |

### Was aus dieser Reihe nicht folgt

Der LZG-Lesepfad war in **allen sechs Läufen untätig** — eine frische Persona hat kein Langzeitgedächtnis. Die Reihe sagt deshalb nichts über das Synapsennetz und nichts über die Wahrnehmungs-Gravitation aus P10. Beide bleiben an einem Korpus zu messen, der einen Bestand mitbringt.

---
## Epic: Pixie — der Abfluss steht (04.08.2026)

**Status:** ⬜ nicht begonnen. **Gemessen am 04.08.2026**, nicht vermutet.

**Der Befund:** `shadow_queue:meister` trägt 650 Aufträge, der älteste vom 27.07. — acht Tage. **246 davon (37,8 %) zeigen auf Agenten, die es nicht gibt:** `vertiefen` → `vertiefung` (184) und `nachfragen` → `nachfragen` (62) sind im Router abgebildet, aber kein Verzeichnis existiert. Der Rest sind 404 `recherche`.

**Warum nichts abfließt:** Der Heartbeat läuft alle 30 Sekunden mit `max_instances = 1`. In sechs Stunden wurden **146 übersprungen**, während eine Recherche den einzigen Platz belegte. Entnahme und Wiedereinreihung heben sich auf — im Log stehen `Queue-Eintrag entfernt` und `Retry 1/3` nebeneinander.

**Widerlegt:** Die naheliegende Vermutung, die periodischen Tagesläufe verhungerten hinter der Blockade, trifft nicht zu. `ziel_decay` steht mit 16, `synapsen_decay` mit 14 Läufen im `hintergrund_log`, keine der sechs periodischen Aufgaben war überfällig. **Der eine serielle Platz trifft, was oft laufen soll, nicht was selten laufen muss.**

| ID | Inhalt | Vorbedingung |
|---|---|---|
| **PIX-AGENTEN-FEHLEN** | `vertiefung` und `nachfragen` existieren nicht. Konzepte: `novaberg-pixie-deepdive_k.md` (69 Zeilen, „noch nicht implementiert") und `novaberg-autonomous-wissen_k.md` §11.3 für `nachfragen`. **Der Sockel** — solange 38 % der Queue ins Leere zeigen, ist jede Durchsatzrechnung sinnlos | Wissensspeicher |
| **PIX-RETRY-KREIS** | Ein Auftrag, der nur scheitern kann, darf nicht dreimal wiederkommen. Ein Fehlschlag ohne Agenten ist ein anderer Fall als einer mit | PIX-AGENTEN-FEHLEN |
| **PIX-SERIELLER-PLATZ** | Ein Takt von 30 s gegen einen Vorgang von Minuten ist eine Fehlanpassung. Entwurfsfrage, keine Fehlerbehebung | keine |
| **PIX-PRIORITAET-STILL** | `kandidaten.py` fällt auf Priorität `0.0` zurück, wenn weder `prioritaet` noch `salienz` im Eintrag steht — 49 von 650 betroffen. Muss laut scheitern statt zur niedrigsten Priorität zu werden | keine |

**Zur Einordnung:** `prioritaet = salienz × (1 + arousal × 0.5)` (`agents/delegation/akte.py`). Es sind zwei Größen — Salienz ist die Bedeutsamkeit, Priorität die durch Erregung verstärkte Dringlichkeit. Gespeichert wird die Salienz; die Priorität ist abgeleitet und gehört zur Auswahlzeit gerechnet.

---

## Epic: Wissensspeicher (04.08.2026)

**Status:** 🔶 Vier von sechs Schritten gebaut, dazu der Enricher-Anschluss.
**Konzept:** `novaberg-autonomous-wissen_k.md` §11 — dort stehen alle Entscheidungen samt Herleitung.

| ID | Inhalt | Stand |
|---|---|---|
| **WIS-1-MOUNT** | `knowledge/` als Geschwister der Repositoriumswurzel, im Behälter `/knowledge` | ✅ **04.08.2026** |
| **WIS-2-TABELLE** | `autonomous_wissen` mit Paar-Schema, Salienz ohne Default, drei Gewichtsspalten | ✅ **04.08.2026** |
| **WIS-3-DATEIEN** | Agenten schreiben Wissen- und Bericht-Datei plus `INDEX.md`, mit `umask 000` / `0666` / `0777` | ✅ **04.08.2026** — `recherche`; die übrigen Agenten ziehen nach dem Beispiel nach |
| **WIS-4-STAPEL-SALIENZ** | `stack_push()` bekommt Salienz und `verstaerkt_am` — beide fehlen heute ganz | ⬜ |
| **WIS-5-VERFALL** | Dritter Schritt im vorhandenen Tageslauf `synapsen_decay`, je Schritt ein eigener Audit-Eintrag | ⬜ |
| **WIS-6-FORTSETZEN** | Der Aufräumer verstärkt statt zu löschen, Schwelle 0.60 | WIS-3 |
| **WIS-PRUEFUNG-F-WISSEN-1** | Pfadprüfung, dass kein Schreibziel des Wissenspfads innerhalb des Arbeitsbaums liegt | ✅ **04.08.2026** — `schreibziel_pruefen()`, jeder Schreib- und Lesevorgang geht hindurch; fünf Testfälle inklusive `..`-Ausbruch |
| **WIS-7-ENRICHER** | Die Bibliothek als sechste Kontextquelle — `WissenManager`, Metadaten-Treffer über Embedding-Nähe, derselbe Suchschlüssel wie KZG und LZG | ✅ **04.08.2026** — Stufe 1 |
| **WIS-8-STUFE-2** | Reicht die Zusammenfassung nicht, den **Dateiinhalt** lesen (§7.3). ~~Braucht den Lesepfad in `tools/dateien/`, den es nicht gibt.~~ → 🟢 **Der Lesepfad existiert seit dem 18.08.2026** (`tools/dateien/operationen.py`: `struktur_analysieren`, `block_lesen`, `zeilen_lesen`, `datei_grep`; 26 Zeugen). Die Blockade ist weg; **offen bleibt der Aufrufer** — kein Knoten ruft die Werkzeuge. **Neu bewertet am 18.08.2026:** Der Wächter (`dateien_index`) ist der **erste Produktivaufrufer** — er ruft `struktur_analysieren` je indizierter Datei. Damit ist die Leseschicht nicht mehr aufruferlos. **Offen bleibt der Zoom selbst:** `block_lesen`, `zeilen_lesen` und `datei_grep` hat weiterhin niemand, und genau die sind die Stufe 2 der Bibliothek. Sie wandern an den lesenden Dienst (Stufe 4). → 🟢 **Geschlossen am 18.08.2026:** Der lesende Dienst hat seinen Aufrufer, und `block_lesen` wie `datei_grep` laufen im Betrieb — gemessen an einem echten Turn: Karte 7 Blöcke ohne Dateizugriff, Nadel 2 Fundstellen, und die Antwort trägt Fundstelle und Zahl im selben Satz. **Rest, ausdrücklich benannt:** `zeilen_lesen` hat weiterhin keinen Aufrufer — der Zoom kennt Karte, Block und Nadel, aber kein Zeilenfenster. **Andere Bauart prüfen:** Die Mandelbrot-Navigation ist aus dem 32k-Zwang abgeleitet; im Hintergrund stehen 262144 Token | WIS-7 |
| **WIS-SCHWELLE-MESSEN** | `WISSEN_RETRIEVAL_SCHWELLE` steht auf **0.40 — übernommen von `anker_retrieval`, nicht gemessen.** Gleicher Embedding-Raum, gleiche Art Anfrage, aber die Bibliothek hatte bei ihrer Einführung drei Zeilen. Zu messen, sobald Bestand da ist: Abdeckung und Fehltreffer über echte Prompts, wie bei der Kalibrierung von 0.40 selbst. — 🔶 **Vorbedingung erfüllt und zur Hälfte gemessen (17.08.2026).** Bestand: 217 aktive Einträge. **Die Schwelle greift nicht — die Kappung greift:** 40 von 42 protokollierten Aufrufen lieferten genau `WISSEN_RETRIEVAL_TOP_K` = 3 Treffer, der Kosinus des dritten liegt bei Median 0,588 (min 0,404, max 0,691). Über 23.436 Paare des Korpus: Median 0,369, **35,6 % über 0,40**; gerechnet liefert erst **0,55** drei Treffer. Zum Vergleich qualifiziert 0,40 im Knotenraum, für den es kalibriert wurde, rund 1,4 % — **Faktor 26**. **Rest:** Abdeckung und Fehltreffer über echte Prompts sind damit **nicht** gemessen; dafür fehlen die Anfragevektoren, die nicht aufbewahrt werden. ~~Wer den Rest hebt, braucht zuerst einen Weg, `such_vektor` mitzuschreiben~~ — **am 19.08.2026 widerlegt, einen Tag nach der Niederschrift.** Aufbewahrte Anfragevektoren braucht die Messung nicht: Fragen kann man **stellen**. Eine Sonde mit acht ausdrücklichen Fragen gegen den Bestand lieferte am selben Tag die Zahl, die der Eintrag für unerreichbar hielt — und sie widersprach der Kalibrierung von 0,40 in der Gegenrichtung. **Der Rest ist damit nicht blockiert, sondern messbar**, und die Vorbedingung ist keine.

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
| **WIS-GATE-MESSUNG** | Wie oft das Keep/Discard-Gate falsch urteilt, ist **nicht gemessen**. Die Verteilung der vier Status über echte Durchläufe ist die Grundlage dafür, ob die Schwelle zwischen `ergaenzung` und `wiederholung` taugt | WIS-3 |
| **PIX-WARTESCHLANGE-AM-MODELL** | **Zwei Posten, beide gemessen.** (1) Serialisierung: dieselbe Anfrage kostet unter Pixie-Last 134,62 s bei 1,27 s Arbeit, mit angehaltenem Pixie 0,05 s Luecke. (2) **Fenster:** Ein trivialer Aufruf bei `num_ctx=262144` kostet 35–38 s, davon 1,33 s ausgewiesen — rund 34 s in keiner Phase, zweimal reproduziert. Bei zehn Aufrufen je Recherche sind das fuenf Minuten Aufschlag. **Nicht gangbar:** `num_ctx` je Aufruf — das Modell ist bei 262144 resident, jede Abweichung laedt 26,8 GB um (19–175 s gemessen, auch mit `keep_alive`). **Fehlt:** ein Aufruf bei 32768 ohne Ladevorgang; ohne ihn ist der Anteil des Fensters an den 35 s nicht zu beziffern | keine |
| **WIS-KONTEXT-NEU-DIMENSIONIEREN** | ⚠ **Die Latenz-Begründung war zwischenzeitlich als widerlegt vermerkt — die Rücknahme ist selbst zurückgenommen.** Der Aufschlag von 35 s je Aufruf bei 262144 (`PIX-WARTESCHLANGE-AM-MODELL`) trifft die Recherche mit ihren gut zehn Aufrufen sehr wohl; er steckt nur nicht in `prompt_eval_duration`. Dazu kommt weiterhin der Verlust durch die Kompression. Der Hintergrundpfad hat **262144** Token, nicht 32768 — gemessen am 04.08.2026, 21:02 UTC. Damit steht die Kompressionsstufe der Recherche (`zwischen_destillieren`) zur Disposition: Sie komprimiert verlustbehaftet gegen eine Grenze, die achtmal weiter weg ist, **und ist der gemessene Ausfallpunkt** eines Durchlaufs. Ebenso das Zwei-Stufen-Retrieval: Eine ganze Wissen-Datei passt in den Prompt, der fraktale Zoom ist für den Hintergrund keine Notwendigkeit mehr, sondern eine Wahl. **Der Gesprächspfad bleibt bei 32768** — beide Zahlen gehören getrennt gehalten | keine |
| **WIS-AGENTEN-NACHZIEHEN** | `vertiefung`, `traum` und `nachfragen` legen nach demselben Muster ab. **Nicht dieselbe Schwelle:** Ein Vertiefungsergebnis liegt seinem Thema im Vektorraum näher als ein Rechercheergebnis (`novaberg-autonomous-wissen_k.md` §11.3) — die Nähe, ab der es dieselbe Datei trifft, ist eigens zu messen . — 🔶 **Neu bewertet am 18.08.2026: Es ist keine Schwellenfrage.** Ein Embedding misst Wortwahl, nicht Zugehörigkeit — *„Napoleons Feldzüge in Ägypten"* liegt näher an einer Napoleon-Datei, weil *„Feldzüge"* lexikalisch ein Napoleon-Wort ist. Und die Frage hat oft **zwei richtige Antworten**. Der Stand der Technik entscheidet die Zuordnung mit einem **Planer auf den Zusammenfassungen** und nach **Pflegbarkeit** statt Nähe, und teilt mehrdeutige Inhalte nach Thema statt sie zu verdoppeln (`novaberg-agent-dateien_k.md` §4a). **Zu messen ist damit nicht eine Nähe, sondern die Trefferqualität der Zuordnung selbst** | PIX-AGENTEN-FEHLEN |

---

## Epic: Klärung — Abweichung und Lücke (04.08.2026)

**Status:** ⬜ nicht begonnen. Grundsatz formuliert, Bestand belegt, Bauteile entworfen.
**Konzept:** `novaberg-klaerung_k.md` — dort stehen ZIEL, TEST, MESSUNG und Gegenprobe je Bauteil.

**Der Kern in einem Satz:** Weicht eine Eigenschaft eines Objekts von der gespeicherten ab, oder fehlt eine notwendige, ist das derselbe Zustand — *erwartet ≠ vorhanden* — und beide enden, wenn sie bedeutsam genug sind, in einer Frage, bevor weitergearbeitet wird.

**Der Anlass ist ein gemessener Defekt:** Der Aktualisierungspfad des Faktengedächtnisses entscheidet an einem reinen Zeichenkettenvergleich (`alter_wert != neuer_wert` → invalidieren). Damit nehmen zutreffende Berichtigung, Fortschreibung und Widerspruch zum eigenen früheren Wort denselben Weg — der dritte Fall überschreibt einen Triple, ohne dass irgendwo steht, dass er strittig war. Die bitemporale Maschinerie (`t_valid`, `t_invalid`, `aktiv`) könnte beide Werte halten; es fehlt das Signal.

**Zwei Tore, nicht eines.** Notwendigkeit kommt vom Objekt und der Aufgabe, Salienz vom Charakter. Ohne das erste fragt Nova nach Belanglosem, ohne das zweite nach allem Notwendigen sofort.

| ID | Inhalt | Vorbedingung |
|---|---|---|
| **KLA-K5-FAKTENPFAD** | Der Schreibpfad prüft selbst, statt an der Zeichenkette zu entscheiden — und deckt damit **beide Graphen** sowie den Aufgabenpfad ab, auf dem kein Verfasser läuft. **Am 04.08.2026 korrigiert:** Die Tabelle `fakten` hat 0 Zeilen und keinen Erzeuger; Urteil und Schreibvorgang liegen in **zwei** Graphen, korreliert nur über `turn_id`. Nicht mehr das erste Bauteil, sondern das letzte. | **`15e`** (FaktenAgent), nicht `SYK-B1` |
| **KLA-K1-ERWARTUNGSSCHEMA** | Zu einem Objekttyp ist abrufbar, welche Eigenschaften er trägt und welche notwendig sind. Weltwissen, einmal abgelegt statt je Turn erfragt. | keine |
| **KLA-K2-KLAERUNGSTOR** | Vergleicht erwartet gegen vorhanden und liefert beide Ausgänge — Lücke und Abweichung — aus einer Operation. | K1, `SYK-B1` |
| **KLA-K3-SALIENZ** | Nur bedeutsamer Klärungsbedarf führt zu einer Frage. Gegenprobe: Bedeutung schlägt Charakter, sonst wird eine distanzierte Nova blind für Widersprüche. | K2 |
| **KLA-K4-ZWISCHENSCHRITT** | Eine Klärungsfrage im Gesprächspfad, mit zurückgestelltem Schreibvorgang. Der Rückfrage-Fluss samt Resume existiert, hängt aber am Agentenpfad. | K2, K3 |

**Offene Entwurfsentscheidung:** Auf dem Aufgabenpfad läuft der Verfasser nicht — dort gibt es kein Urteil, ausgerechnet da, wo ein Nutzer ausdrücklich etwas ändern lässt. Entweder ein reduziertes Urteil, oder die ausdrückliche Festlegung, dass von dort ungeprüft geschrieben wird.

**Verhältnis zum Sykophanz-Epic:** `SYK-B1` liefert das Urteil, das K2 für seinen Abweichungs-Ausgang braucht. Der Sykophanz-Sprint ist damit das erste Stück dieses Grundsatzes und kein eigenständiges Thema.

---

## Epic: Client-Dashboard (GTK4 / PyGObject)

**Motivation:** Debugging, Kalibrierung und Einregelung des Dual-Emotion-Systems (Chat 53) erfordern visuelles Echtzeit-Feedback. Log-Grep ist kein Werkzeug für die Feinabstimmung von 8-dimensionalen Emotionsvektoren. Ohne Dashboard ist die Dual-Emotion-Architektur Blindflug.

**Architektur:** GTK4 Desktop-App (PyGObject) als Parent-Fenster mit Child-Panel-Fenstern. Emojis nativ (System-Fonts). FastAPI liefert Daten über REST (statisch) und WebSocket (Live-Streams). Kein Qt, kein Browser, kein Electron.

**Technologie-Entscheidung (Chat 55):** PySide6/Qt verworfen nach Emoji-Rendering-Bug (Qt-Chromium findet System-Emoji-Fonts nicht auf Linux). GTK4 ist das native GNOME/Fedora-Toolkit — vorinstalliert, keine Dependencies, Emojis nativ validiert.

**Panels (12 Typen, Chat 55 designed):**

| Panel | Kategorie | Datenquelle | Status |
|-------|-----------|-------------|--------|
| Emotionen (Aktuell) | on_demand | `GET /gedaechtnis/emotionen/{user_id}` | ✅ Chat 56 |
| Emotionen (Turns) | turn_reactive | SSE answer-Event (emotions_vektor) | ⬜ |
| Session-Turns | on_demand | `GET /session/kontext/{user_id}` | ✅ Chat 56 |
| KZG | on_demand | `GET /gedaechtnis/kzg/{user_id}` | ✅ Chat 56 |
| LZG | on_demand | `GET /gedaechtnis/lzg/{user_id}` | ✅ Chat 56 |
| Charakter | on_demand | `GET /gedaechtnis/hash/{user_id}` | ✅ Chat 56 |
| Fakten | on_demand | `GET /fakten/{user_id}` | ⬜ |
| System | on_demand | `GET /health` | ✅ Chat 56 |
| Pixie-Monitor | on_demand | `GET /debug/pixie/status` (neu) | ⬜ |
| PostgreSQL | query | `POST /debug/query/postgres` (neu) | ⬜ |
| Redis | query | `POST /debug/query/redis` (neu) | ⬜ |
| Docker-Logs | log_stream | `WS /debug/logs` (neu) | ⬜ |
| Ziele & Antrieb | turn_reactive | `GET /drive/goals` | ✅ Chat 69 |
| Gravitationsgraph | turn_reactive | `GET /drive/gravity_map` | ✅ Chat 69 |

**Voraussetzung für:** Dual-Emotion-Architektur (Chat 53), Antrieb/Gravitation (Chat 53), TR6 (_farbe_charakter). Ohne visuelles Feedback können die Schwellwerte nicht empirisch kalibriert werden.

**Löst:** CLIENT-RENDER (Backlog), Log-Debugging-Workflow

**Status Chat 56:** Phase 1 weitgehend abgeschlossen — Chat (WebKitGTK + SSE + WebSocket), Panel-Infrastruktur (PanelBase, ChildWindow, Registry, UNIQUE-Enforcement), 6 Panels funktional (System, Emotionen mit Radar, KZG, LZG, Session, Charakter). Offen: Fakten, Pixie-Monitor, PostgreSQL-Query, Redis-Query, Docker-Logs, Emotionen (Turns).

**Status Chat 62:** Perspektive-Selector eingebaut — `GespraechsPerspektive`-Dataclass + `PERSPEKTIVEN`-Liste als Single Source. Dropdown im Hauptfenster: "Meister — Gespraech mit Nova" / "Nova — Gespraech mit Meister". Alle sechs aktiven Panels auf `_get_api_params()` umgestellt, sodass sie die aktuelle Perspektive konsumieren statt hartkodierter User-IDs. Emotionen-Panel zeigt Dual-Emotion je Perspektive — verschiedene Radare fuer Meister und Nova. Die Dataclass-Liste ist erweiterbar fuer weitere User/Charakter-Paare (`james`, `tarzan`, weitere User).

**Status Chat 69:** Zwei neue Panels: Ziele & Antrieb (GoalsPanel, turn_reactive, 3 Ebenen) + Gravitationsgraph (GravityMapPanel, turn_reactive, 900×650, Cairo Force-Directed). 8 von 14 Panels funktional. Embedding-Persistenz in der Pipeline. Themen-Pipeline geschlossen.

---

## Epic: Dual-Emotion (Chats 53, 57–58)

**Vision:** Nova hat einen eigenen Emotionsstrang mit denselben 8 Plutchik-Dimensionen wie der User. Jede Antwort wird analysiert — Emotion, Arousal, Modus, Intent. Die Daten fließen unter `ASSISTANT_USER_ID` ins Gedächtnis und werden im nächsten Turn geladen.

**Leitprinzip:** "Der Eingangspfad für den User ist der Ausgangspfad für Nova."

**Drei Phasen:**

| Phase | Ziel | Status |
|-------|------|--------|
| Phase 1 | User-IDs entkoppeln — frei wählbar aus Config | ✅ Chat 57 |
| Phase 2 | Zweiter Emotionsstrang + Enricher-Split + Graph-Neuordnung | 🔧 AP1–7 ✅, AP8 teilw. (Server ✅, Client offen), AP9 ✅ |
| Phase 3 | Ziel-Vektor (Antrieb) als dritte Kraft auf Novas Emotion | ⬜ |

**Konzept-Dokumente:** `novaberg-thinking-drive_k.md` §4 (Chat 53), `novaberg-ei-dual-emotion_k.md` (Chat 58)

**Arbeitspakete Phase 2:**

| AP | Paket | Status |
|----|-------|--------|
| 1 | EI-Extraktion (Enricher → ei/berechnung.py) | ✅ Chat 58 |
| 2 | EI-Calc-Node (graph/nodes/ei_calc.py) | ✅ Chat 59 |
| 3 | Nova-Emotion Berechnung (Decay + Empathie) | ✅ Chat 59 |
| 4 | Perzeption(Nova) + EI-Calc(Nova) im async-Block | ✅ Chat 60 — Event-Modell ersetzt den async-Pfad |
| 5 | Router(Nova) + Commitment-Erkennung | ✅ Chat 60 — Router im CharacterGraph |
| 6 | Salienz(Nova) — eigener Salienz-Prompt | ✅ Chat 60 — Salienz im CharacterGraph |
| 7 | Asynchroner Block orchestrieren | ✅ Chat 60 — Event-Consumer ersetzt async-Block |
| 8 | API + Client (GespraechAntwort + Dual-Radar) | 🔧 API ✅, Responder [EIGENE_EMOTION] ✅, Client-Panels offen |
| 9 | Dokumentation | ✅ Chat 66 |

**Chat 61 Nachtrag:**
- Perzeption(Nova) läuft nun symmetrisch nach Nova's finaler Antwort (analog zu Perzeption(User) in Pfad 1). Siehe Roadmap Chat 61.
- EI-Calc hat einen sauberen Rollen-Split bekommen (`ei_calc_rolle: "user" | "character"`). Trennung von User- und Nova-Emotion-Berechnung ist damit architektonisch abgeschlossen.

---

## Epic: Emotionale Gravitation (Chat 61)

**Vision:** Gespeicherte emotional aufgeladene Erinnerungen wirken als Attraktoren auf Novas aktuellen Emotionsstrom. Still, passiv, bis ein thematisch verwandtes Gespräch sie reaktiviert.

**Konzept:** `novaberg-thinking-drive_k.md` Kapitel 5.7 — drei Zeithorizonte (Session/KZG/LZG), Formel `gravitation = similarity × gewicht × zeit_dekay × quellen_faktor`.

**Mechanik:** Bei jedem Turn in Pfad 2 (Nova-EI-Calc):
1. Embedding des aktuellen Themas berechnen (liegt bereits vor)
2. Top-K Einträge aus Session + KZG + LZG mit Emotion-Aufladung retrieven
3. Ähnlichkeits-basierte Gravitations-Berechnung je Eintrag
4. Einträge über Schwelle (EMOTIONALE_GRAVITATIONS_SCHWELLE) fügen ihren Emotions-Vektor zu Novas Vektor hinzu
5. Hard-Cap auf EMOTIONALE_GRAVITATION_MAX_PRO_TURN (default 2) um keine Gefühls-Explosion auszulösen

**Config-Parameter (neu):**
- `EMOTIONALE_GRAVITATIONS_SCHWELLE: float = 0.5`
- `EMOTIONALE_GRAVITATION_ZEIT_HALBWERT: int = 180` (Tage)
- `EMOTIONALE_GRAVITATION_MAX_PRO_TURN: int = 2`
- `EMOTIONALE_GRAVITATION_FAKTOR_SESSION: float = 1.0`
- `EMOTIONALE_GRAVITATION_FAKTOR_KZG: float = 0.8`
- `EMOTIONALE_GRAVITATION_FAKTOR_LZG: float = 0.5`

**Wissenschaftliche Basis:** Bower (1981) Mood-Congruent Memory, Collins & Loftus (1975) Spreading Activation, Tulving (1983) Episodic Memory.

**Status:** ~~Konzeptionell vollständig. Code-Implementation offen.~~ → **überholt.** Die Berechnung steht seit Chat 109 (`ei/gravitation.py`, LZG-Umstellung Commit `cb494d3`), die Anwendung seit Chat 113 als eigener Node zwischen Enricher und Reducer. **Dass hier und in `novaberg-roadmap.md` „Implementation steht aus" stand, ist der Grund, warum vier Chats lang niemand hingesehen hat** — der Code lief, und zwei Dokumente sagten, es gäbe ihn nicht.

**Offen bleiben zwei der fünf Festlegungen aus §5.7:** die Session-Quelle (`EMOTIONALE_GRAVITATION_FAKTOR_SESSION` steht seit Chat 61 unbenutzt in der Config, gescannt werden nur KZG und LZG) und der Arousal-Filter bei der Kandidatenwahl (`arousal` wird gelesen, mitgeführt und geloggt, aber nie verglichen). Beides ist unfertiges Bauteil, kein Defekt.

**Priorität:** Mittel — schön zu haben, erhöht emotionale Tiefe deutlich, aber nicht blockierend.

---

## Epic: Client urllib3-Retry-Fix (Chat 61) ✅ Chat 65 (verifiziert Chat 73)

**Problem:** Wenn der Server lange braucht (z.B. 55 Sekunden bei GPU-Druck), sendet urllib3 (unter requests) automatisch einen Retry. Der Server bekommt den Prompt zweimal, schreibt zwei identische User-Turns in die Session. Symptom wurde in Chat 61 beobachtet.

**Fix:** In `client/ui/stream_handler.py` HTTPAdapter mit `max_retries=0` konfigurieren, damit keine automatischen Retries stattfinden. Timeouts auf Client-Ebene explizit behandeln.

**Priorität:** Niedrig-Mittel — tritt nur bei langsamen Server-Responses auf. Mit schneller GPU und normaler Session-Größe kein Problem. Verhindert aber Daten-Inkonsistenzen bei Edge-Cases.

---

## Epic: Session-Limit für Responder-Prompt (Chat 61)

**Problem:** Der Responder-Node packt aktuell alle Session-Turns (seit Session-Beginn) in den System-Prompt. Bei 18+ Turns mit reichhaltigen Emotions-Metadaten wird der Kontext schnell groß (~7000-14000 Tokens für einen Turn). In Kombination mit KZG + Charakter-Hash + Regeln kann das Gemma4's Kontext-Fenster (32768) deutlich beanspruchen.

**Fix:** Session-Fenster einziehen — z.B. nur die letzten 12 Turns in den Prompt packen. Die älteren Turns bleiben in Redis für Nova's Gedächtnis, fließen aber nicht mehr in den aktuellen LLM-Call.

**Zu beachten:** 
- KZG-Verdichtung und Charakter-Hash ersetzen bereits den älteren Kontext konzeptionell
- Der Cut-off sollte aber die aktuelle Gesprächs-Episode vollständig enthalten (Session-Cluster-Grenzen beachten, nicht mitten in einem thematischen Block abschneiden)

**Priorität:** Mittel — performance- und kontextrelevant. Wird dringender, je längere Gespräche geführt werden.

---

## Epic: Graph-Neuordnung (Chat 58–59) — ✅ Chat 59

**Beschluss:** Enricher vor Router verschieben. Der Router sieht dadurch die volle Session, KZG, LZG, Charakter-Hash und EI-Ergebnisse — statt nur 5 Turns aus eigenem Redis-Read.

**Neuer synchroner Graph (implementiert Chat 59):**
```
Perzeption → Enricher(laden) → EI-Calc → Router → [Planner → Agent] →
GV-Node → Responder → Thinker → Tribunal → [Corrector]
```

**Löst:** ROUTE-MISS1 (strukturell — Router erkennt "Ja, bitte!" nach "Soll ich einen Termin anlegen?"). Offen für Validierung.

**Status:** ✅ Implementiert in Chat 59 zusammen mit Dual-Emotion AP2. Conditional Edge `_after_enricher` → `_after_router`. Salienz und Dispatcher zugleich aus dem sync-Graph entfernt (siehe Dual-Emotion AP7).

---

## Epic: Session-Trennung (User × Charakter) (Chat 54, 59)

**Vision:** Jede Gesprächskombination (User × Charakter) bekommt eine eigene Session-Partition. `session:meister:nova`, `session:meister:james`, `session:meister:tarzan`.

**Motivation:** Aktuell landen alle Charakter-Daten in `session:meister`. Multi-Character ist nicht trennbar. Durch die Turn-Annotation (Chat 59) ist das Problem sichtbarer geworden: Novas Emotionen landen in Meisters Session, unabhängig vom Charakter.

**Betroffene Stellen (Chat 54):**
1. Session-Keys in Redis (`session:{user_id}` → `session:{user_id}:{character_id}`)
2. `ASSISTANT_USER_ID` in config.py (hartkodiert → parametrisiert pro Turn)
3. `ASSISTANT_NAME` in config.py (Konstante → pro Turn aus Character-Definition)
4. Pending Agents in Redis (Character-Dimension nötig)

**Zusätzlich betroffen (Chat 59):**
5. `session_assistant_turn_annotate()` — annotiert in User-Session, muss Character-aware sein
6. Enricher — lädt Session-Turns, KZG, LZG, Hash pro Character
7. Nachbearbeitung — Nova-Pfad muss Character-ID durchreichen

**Priorität:** Direkt nach Dual-Emotion Phase 2. Wird für Debugging, Tests mit eigenen Charakteren und Multi-Character-Betrieb gebraucht.

**Status:** ✅ Implementiert in Chat 60. 23 Dateien, 56 Stellen. Session-Key `session:{user_id}:{character_id}:turns`.

---

## Vision: TurnOrchestrator (Chat 58)

**Idee:** Den linearen Graph durch einen sternförmigen Orchestrator ersetzen. Ein TurnOrchestrator entscheidet regelbasiert, welcher Node als nächstes läuft ("Waren wir schon bei Perception? Nein? Dann Perception."). Der asynchrone Nova-Pfad wäre dann kein Sonderfall, sondern eine weitere Sequenz in derselben State-Machine.

**Vorteil:** Flexiblere Pfade, weniger Conditional Edges, Nova-Pfad als natürlicher Teil statt Sonderlogik.

**Status:** Diskutiert, als Zukunfts-Epic festgehalten. Großer Umbau — berührt human_graph.py, alle Conditional Edges, Node-Wrapper-Factory, Builder. Nicht Teil von Phase 2.

**Update Chat 60:** Das Event-Modell löst das TurnOrchestrator-Problem auf eine andere Art — statt eines sternförmigen Orchestrators gibt es zwei separate Graphen, verbunden durch eine Event-Queue. Der TurnOrchestrator als separates Epic ist damit konzeptionell überholt.

---

## Epic: Client WebSocket-Umbau (Chat 60) ✅ **abgeschlossen 01.08.2026 (Chat 124)**

**Erledigt.** Der SSE-Kanal trägt nur noch die Bestätigung; alle Stufen — Pfad 1 **und** Pfad 2 — gehen als `character_stage` über den WebSocket, die Antwort als `character_response`. Damit sind die Migrationsschritte 6 und 7 aus `novaberg-convention-event-model.md` §9.1 durch.

**Über die ursprüngliche Vision hinaus:** Der Endpunkt führt Pfad 1 nicht mehr selbst aus, sondern reiht die Äußerung in eine Eingangs-Queue (`prompt_queue`) und bestätigt in 0,01 s statt in 11 bis 104 Sekunden. Mehrere Äußerungen innerhalb von 30 Sekunden werden zu **einem** Prompt und als Ganzes perzipiert. Ein Turn-Marker hält die Eingabe zurück, bis der CharacterGraph durch ist.

**Rest, benannt:** Die Stufen tragen keine Turn-Kennung und sammeln sich optisch unter der falschen Nachricht, wenn während eines Laufs weitergeschrieben wird. Und eine nie beantwortete Frage bleibt im Client-Zustand offen, ohne auf dem Bildschirm sichtbar zu sein. Beides in `novaberg-fundliste.md`.

Die ursprüngliche Fassung des Epics:

**Vision:** Der GTK4-Client empfängt Charakter-Antworten per WebSocket (`typ: "character_response"`) statt aus dem SSE-"answer"-Event. Der SSE-Stream zeigt nur noch die Pfad-1-Stages.

**Motivation:** chat.py ist fire-and-forget (Chat 60). Die Antwort kommt vom Event-Consumer per WebSocket. Der Client muss den neuen Message-Typ rendern.

**Betroffene Stellen:**
1. `client/ui/chat_view.py` (oder äquivalent) — WebSocket-Handler für `character_response`
2. SSE-Handler — kein `answer`-Event mehr, nur `processing`
3. Nachrichten-Rendering — Antworten asynchron anzeigen

**Status:** ~~Offen. Server-Seite fertig (Chat 60).~~ → siehe oben, abgeschlossen in Chat 124.

**Status Chat 68:** WS-SINGLE behoben. `ClientConnection`-Dataclass mit `client_id`/`character_id`-Filterung. User-Message-Broadcast (server-seitige Filterung, kein Client-Filter nötig). Desktop ↔ Telegram bidirektional getestet. 12 Dateien.

---

## Epic: Chat 62 — Folgearbeiten aus dem Paar-Schema

Vier Arbeitspakete, die durch die KZG/LZG-Umstellung auf das Paar-Schema und durch beobachtete Gespraechsverlaeufe sichtbar wurden. Zwei Bugs, ein Bug-Risiko, ein Feature.

### KZG-DEDUP — Deduplizierung semantisch aehnlicher Eintraege ✅ Gelöst Chat 64

Bei semantisch aehnlichen Turns erzeugt die Salienz mehrere KZG-Eintraege statt zu verstaerken, weil der Themen-Vergleich leicht unterschiedliche Tags extrahiert ("Name Lumi" vs. "Namensgebung Lumi" vs. "neuer Mitbewohner"). In Chat 62 beobachtet: Ein Gespraech ueber Lumi erzeugte 8 Eintraege statt 1–2.

**Auflösung Chat 64:** Re-framed als Feature im Rahmen der KZG-Liberalisierung. Verschiedene Facetten desselben Themas werden im KZG bewusst als eigenständige Einträge behalten — die Cluster-Promotion sammelt sie ein und destilliert sie zu einem kohärenten LZG-Eintrag.

### KZG-KERN-BLIND — Verstaerkung ignoriert neuen Kern-Inhalt ✅ Gelöst Chat 64

Bei KZG-Verstaerkung wurde der Zaehler erhoeht und Scores/Emotionen aktualisiert, aber der inhaltliche `inhalt`/Kern blieb auf dem Text des ersten Turns. Folge-Turns, die den Moment erst bedeutsam machen (z.B. der Name "Lumi" nach mehreren Turns ueber die neue Pflanze), gingen inhaltlich verloren.

**Auflösung Chat 64:** Obsolet durch Architekturwechsel — keine Merge-Verstärkung mehr. Jeder KZG-Eintrag behält seinen originalen Kern. Die thematische Verstärkung boosted nur Metadaten (Salienz, Häufigkeit, TTL). Die Cluster-Promotion destilliert alle Kerne bei der Zusammenführung ins LZG.

### ROUTE-CHAR-NOTIZ — CharacterGraph-Router dispatched Konversation an NotizenAgent (Bug, niedrig)

Der Router im CharacterGraph erkennt Konversation faelschlich als Notizen-Task ("Lumi Geschlecht" → NotizenAgent-Dispatch → Fehler). Der Classify im NotizenAgent rejected korrekt mit "kein Notiz-Auftrag", aber der Umweg kostet einen LLM-Call und erzeugt eine Fehlermeldung im Gespraechsvektor. Verwandt mit ROUTE-MISS1 (dort False Negative, hier False Positive).

**Loesungsansatz:** Router-Prompt haerten — kurze Zwei-Wort-Phrasen ohne Verb und ohne Objekt-Marker nicht als Notiz-Auftrag klassifizieren. Alternativ: Router bekommt die letzten Turns als Kontext und pruefend ob das Thema gerade im Gespraech ist.

**Prio:** Niedrig — kosmetisch und Performance, kein Datenverlust.

---

## Epic: KZG-Liberalisierung + LZG-Destillation (Chat 63)

**Vision:** Speichern ist günstig, Vergessen ist intelligent. Die KZG-Eintrittsschwelle wird gesenkt, die Deduplizierung im KZG aufgeweicht, und die Intelligenz wird an den LZG-Übergang delegiert — wo thematisch verwandte KZG-Einträge zu einer Synthese destilliert werden.

**Leitprinzip:** Im KZG bleiben präzise Einzelaussagen. Im LZG verschwimmen Details zu einer Essenz — wie beim Menschen, der sich nach Wochen nicht mehr an den exakten Wortlaut erinnert, aber an die Kernaussage.

### Änderung 1 — Salienz-Schwelle senken

Aktuell: `< 0.5` wird ignoriert, `0.5–0.7` KZG kurz (TTL 7 Tage), `≥ 0.7` KZG lang (TTL 30 Tage).

Neu: `< 0.3` wird ignoriert, `0.3–0.5` KZG kurz (TTL 7 Tage), `0.5–0.7` KZG mittel (TTL 14 Tage), `≥ 0.7` KZG lang (TTL 30 Tage) + Promotion-Queue.

**Begründung:** Der Bereich 0.3–0.5 enthält informative Aussagen ("Ich mag Schnittlauch"), die heute komplett verloren gehen. Wenn sie nicht innerhalb von 7 Tagen verstärkt werden, verschwinden sie — dann waren sie nicht wichtig. Wenn doch, steigen sie auf.

**Betroffene Dateien:** `config.py` (Schwellwerte), `graph/nodes/salience.py` (Bereichsgrenzen), `agents/kzg/speicher.py` (TTL-Zuweisung).

### Änderung 2 — KZG-Deduplizierung aufweichen

Aktuell: Cosine-Schwellwert 0.85 + Themen-Tag-Match → bei Treffer Verstärkung statt Neuanlage.

Neu: Im KZG keine aggressive Deduplizierung mehr. Einzelaussagen als separate Einträge behalten. Verstärkung nur bei sehr hoher Ähnlichkeit (≥ 0.95) oder exaktem Themen-Match.

**Begründung:** Das KZG bildet die nahe Vergangenheit ab. Hier zählt Präzision — "Schnittlauch ist toll!" und "Minze ist toll!" sind zwei verschiedene Aussagen mit unterschiedlichem Informationsgehalt. Beide sollen abrufbar sein. Die Zusammenführung passiert erst beim LZG-Übergang.

**Zusammenspiel mit KZG-DEDUP (Chat 62):** Der Bug KZG-DEDUP (8 Einträge statt 1 bei einem Gespräch über Lumi) wird damit neu gerahmt. Die 8 Einträge waren kein Bug — sie waren verschiedene Facetten desselben Themas. Die Lösung liegt nicht in aggressiverer KZG-Deduplizierung, sondern in intelligenter LZG-Destillation.

### Änderung 3 — LZG-Destillation bei Promotion

Aktuell: Einzelne KZG-Einträge werden 1:1 ins LZG promoviert (Pixie Promotion Call 2).

Neu: Bei der Promotion sammelt Pixie alle thematisch verwandten KZG-Einträge der Paar-Partition ein (Embedding-Ähnlichkeit ≥ 0.75 zum Promotion-Kandidaten), destilliert sie in einem LLM-Call zu einer großen Zusammenfassung und schreibt diese als einen LZG-Eintrag.

**Beispiel:**

- KZG-Eintrag 1: "Schnittlauch ist toll!"
- KZG-Eintrag 2: "Minze ist toll!"
- KZG-Eintrag 3: "Hat frische Kräuter für den Balkon gekauft"
- → LZG-Destillat: "Mag frische Kräuter, besonders Schnittlauch und Minze. Hat Kräuter für den Balkon."

**Mechanik:**

1. Promotion-Trigger wie bisher (TTL 30 Tage, `gedaechtnistyp=lang`, Verstärkung)
2. Vor dem Schreiben: Embedding-Suche im KZG nach verwandten Einträgen (gleiche Paar-Partition, Cosine ≥ 0.75)
3. LLM-Call (CPU-Modell): "Fasse folgende Beobachtungen zu einer Gesamtaussage zusammen: [alle Kerne]"
4. Ein LZG-Eintrag mit dem Destillat, Themen-Union aus allen Quell-Einträgen
5. Quell-KZG-Einträge werden als `promoviert` markiert (kein erneutes Triggern)

**Betroffene Dateien:** `agents/pixie/promotion.py` (Destillations-Logik), `agents/kzg/aehnlichkeit.py` (Cluster-Suche), neuer Prompt in `prompts/default/pixie.promotion_destillation.txt`.

**Priorität:** Mittel-Hoch — verbessert LZG-Qualität deutlich, löst KZG-DEDUP konzeptionell.

---

## Epic: Retrieval-Gate — Kontextverifikation nach dem Enricher (Chat 67)

**Vision:** Der Enricher lädt alle verfügbaren Daten (Session, KZG, LZG, Knowledge Graph, Charakter-Hash). Heute fließt alles ungefiltert in den State — der Responder bekommt Roleplay-Fakten, Negationen, Duplikate, LZG-Response-Blobs und irrelevante Einträge. Das Retrieval-Gate ist ein Verifikationsschritt an der Verarbeitungsgrenze zwischen Laden und Konsumieren.

**Leitprinzip:** "Weniger Input > stärkerer Prompt." — Kein Prompt kompensiert verrauschten Kontext. Verifikation gehört an jede Trust Boundary im Datenfluss, nicht nur am Ausgang (Tribunal).

**Architekturmuster:** Verifikation an Verarbeitungsgrenzen. Dasselbe Prinzip wie das Tribunal (Ausgangsverifikation), angewandt auf den Eingang. Zwei-Stufen-Retrieval nach dem Re-Ranking-Muster: Stufe 1 (Enricher) lädt breit, Stufe 2 (Gate) filtert scharf.

**Position im Graph:**

Perzeption → Enricher → ▶ Retrieval-Gate ◀ → EI-Calc → Router → ...

Eigener Node zwischen Enricher und EI-Calc. Liest aus dem State, schreibt gefilterten Kontext zurück.

**Drei Filtermechanismen (alle deterministisch, kein LLM-Call):**

| Mechanismus | Methode | Adressiert |
|-------------|---------|-----------|
| Relevanz-Score | Cosine-Similarity jedes Eintrags gegen User-Prompt-Embedding. Unter Schwelle → entfernen. | Irrelevante Einträge, Roleplay-Fakten, veraltete Themen |
| Deduplizierung | Embedding-Ähnlichkeit zwischen den geladenen Einträgen selbst. Über Schwelle → den mit höherem Gewicht behalten. | ENRICHER-DUP, redundante Fakten |
| Top-K pro Quelle | Maximal N Einträge pro Quelle (KZG, LZG, Knowledge Graph). | Kontext-Dominanz durch eine einzelne Quelle, Token-Budget-Überschreitung |

**Erwartete Wirkung:**

- Sauberer `memory_context` für Responder → bessere Antwortqualität
- ENRICHER-DUP gelöst (strukturell, nicht per Prompt)
- Token-Budget im Responder-Prompt entlastet
- Indirekt: Thinker-Web-Suche weniger anfällig für `num_ctx`-Überlauf (weniger Basis-Kontext = mehr Raum für Web-Ergebnisse)

**Konfiguration (Config-Muster):**

- `RETRIEVAL_GATE_RELEVANZ_SCHWELLE` — Cosine-Similarity-Minimum gegen User-Prompt
- `RETRIEVAL_GATE_DEDUP_SCHWELLE` — Cosine-Similarity-Maximum zwischen Einträgen
- `RETRIEVAL_GATE_TOP_K_KZG` — Max Einträge aus KZG
- `RETRIEVAL_GATE_TOP_K_LZG` — Max Einträge aus LZG
- `RETRIEVAL_GATE_TOP_K_FAKTEN` — Max Einträge aus Knowledge Graph

**Laufzeit:** Sub-100ms, reine Embedding-Arithmetik + Sortierung. Kein GPU-Bedarf (Embeddings liegen bereits vor).

**Voraussetzung:** Die Embeddings der geladenen Einträge müssen im State verfügbar sein. KZG-Einträge haben Embeddings (Redis-Vektoren). LZG und Knowledge Graph müssten ihre Embeddings mittransportieren — zu prüfen.

**Priorität:** Mittel — adressiert Kontextqualität, ENRICHER-DUP und Token-Budget. Wird wichtiger mit wachsendem Gedächtnis.

---

## Epic: Embedding-Gravitationsgraph — Turn-Dashboard (Chat 63)

**Vision:** Ein visuelles Dashboard, das den letzten Turn als Embedding-Graphen zeigt. Novas Interessen, Ziele und Neugier-Punkte sind Gravitationszentren im 2D-Raum. Der User-Input und Novas Gesprächsvektor-Schritte wandern als Punkte durch diesen Raum. Kantenlängen zeigen Embedding-Distanz. Je näher ein Thema an einem Gravitationspunkt liegt, desto heißer wird es — sichtbar durch Farbverlauf von Grün (weit weg) nach Rot (nah, hohe Gravitation).

**Leitprinzip:** "Ich will sehen, wie der Turn ins Gedächtnis von Nova passt, wo wir thematisch sind."

### Elemente im Graphen

**Gravitationszentren (statisch pro Session):**

- Novas Interessen (aus Charakter-Hash `interessen_profil`)
- Novas Ziele (aus `thinking-drive` / Ziel-Embeddings)
- Novas Neugier-Themen (aus KZG/LZG mit hoher Resonanz)
- Jedes Zentrum hat ein sichtbares **Gravitationsfeld** — einen radialen Farbverlauf um den Kern:
  - Äußerer Rand ("Ereignishorizont"): Grün, halbtransparent. Markiert die Embedding-Distanz, ab der Gravitation beginnt zu wirken (= `EMOTIONALE_GRAVITATIONS_SCHWELLE`)
  - Übergangszone: Grün → Gelb → Orange, zunehmende Opazität
  - Kernzone: Rot, intensiv. Hier ist die Gravitation maximal — ein Thema, das hier landet, beeinflusst Novas Themenwahl und Emotion stark
- Kreisgröße des Kerns proportional zur Resonanz/Motivation
- Der Farbverlauf macht sichtbar: Wenn ein Turn-Punkt (User oder Nova) den Ereignishorizont berührt, beginnt die Verfärbung. Je tiefer er eintaucht, desto stärker der Gravitationseinfluss auf Themenwahl und Emotionsstrom
- Bei Themen OHNE Gravitationseinfluss (weit weg von allen Zentren): keine Verfärbung, neutraler Raum

**Turn-Punkte (dynamisch pro Turn):**

- User-Aussage: Embedding des User-Inputs
- Nova-Aussage: Embedding der Nova-Antwort
- GV-Schritte: 0 bis 2–3 Zwischenschritte des Gesprächsvektors, sichtbar als Pfad

**Verbindungen:**

- Kanten zwischen Turn-Punkten und Gravitationszentren
- Kantenlänge = Embedding-Distanz (kurz = nah = heiß)
- Pfeil von User-Aussage über GV-Schritte zu Nova-Aussage zeigt den Gesprächsvektor

### Geladenes Gedächtnis als Orientierungspunkte

Das Entscheidende: Der Graph muss zeigen, was der Enricher für diesen Turn geladen hat. Die geladenen KZG- und LZG-Einträge sind die thematische Nachbarschaft — sie erklären, warum Nova so reagiert wie sie reagiert. Ohne sie fehlt dem Graphen der Kontext.

**Session-Turns (letzte N):**

- Kleine Punkte entlang eines Pfades, der den bisherigen Gesprächsverlauf zeigt
- Zeigen, wo das Gespräch herkommt — der Weg zum aktuellen Turn
- Visuell dezent (kleiner als Turn-Punkte, kein Plutchik-Stern, einfache Kreise)

**KZG-Einträge (vom Enricher geladen):**

- Mittlere Punkte mit Themen-Label
- Diese sind die nahen Erinnerungen — kurze Embedding-Vektoren, die der Enricher für relevant befunden hat
- Farblich abgesetzt (z.B. halbtransparent), um sie von den aktiven Turn-Punkten zu unterscheiden
- Ihre Position im Embedding-Raum zeigt, WARUM der Turn in die Nähe bestimmter Gravitationszentren fällt

**LZG-Einträge (vom Enricher geladen):**

- Wie KZG, aber visuell anders markiert (z.B. gestrichelter Rand)
- Langzeiterinnerungen sind destillierter, breiter — ihre Position zeigt die tiefere thematische Verankerung

**Neugier, Ziele, Interessen aus dem State:**

- Alles, was im ConversationState steht und als Orientierung dient, muss im Graphen sichtbar sein
- Die Gravitationszentren sind nicht abstrakt — sie werden aus den konkreten Daten im State befüllt: `interessen_profil`, `ziele`, `neugier_themen`
- Nur so kann man die Position von User- und Charakter-Aussagen einordnen: relativ zu dem, was Nova gerade "weiß" und "will"

**Prinzip:** Der Graph bildet das Gesamtbild eines Turns ab — nicht nur was gesagt wurde, sondern was geladen wurde, was in der Nähe liegt, und in welchem Gravitationsfeld das alles stattfindet. Jeder Punkt im Graphen hat eine Bedeutung als Orientierung, wo wir uns thematisch befinden.

### Emotions-Visualisierung: Plutchik-Mikrosterne

Jeder Turn-Punkt (User-Aussage, GV-Schritte, Nova-Aussage) wird nicht als einfacher Kreis dargestellt, sondern als kleiner 8-zackiger Plutchik-Stern. Die 8 Achsen entsprechen den 8 Plutchik-Dimensionen (Freude, Vertrauen, Angst, Überraschung, Trauer, Ekel, Wut, Antizipation). Die Achsenlänge zeigt die Intensität der jeweiligen Emotion.

**Effekt:** Man sieht auf einen Blick:

- User-Stern zeigt z.B. dominante Freude (eine Zacke lang)
- Nova Schritt 1: Stern kippt zu Neugier (andere Zacke wächst)
- Nova Schritt 2: Stern kippt zu Vertrauen
- Die Sterne wandern durch den Gravitationsraum UND verändern dabei ihre Form

**Größe:** Nicht zu klein (Emotionen müssen lesbar sein), nicht zu massiv (Gravitationsraum muss dominieren). Ca. 40–60px Durchmesser im Rendering.

### Technische Überlegungen

**2D-Projektion:** UMAP oder t-SNE auf die hochdimensionalen Embeddings. Pro Turn neu berechnen (nur die Turn-Punkte ändern sich, Gravitationszentren bleiben stabil innerhalb einer Session).

**Rendering:** Cairo-Canvas im GTK4-Client oder WebKit-Widget. Live-Update nach jedem Turn.

**Datenquellen:**

- Embedding des User-Inputs: liegt nach Perzeption vor
- Embedding der Nova-Antwort: liegt nach Perzeption(Nova) vor
- GV-Schritte: aus `gv_vektor` im State (0–3 Schritte mit Themen)
- Emotionen: aus `ei_calc` (User) und `nova_emotions_vektor` (Nova)
- Gravitationszentren: Charakter-Hash-Profile + Ziel-Embeddings (zu cachen)
- Geladene KZG-Einträge: aus `kzg_eintraege` im State (vom Enricher befüllt)
- Geladene LZG-Einträge: aus `lzg_eintraege` im State (vom Enricher befüllt)
- Session-Turns: aus `session_turns` im State (letzte N Turns mit Embeddings)
- Neugier/Ziele/Interessen: aus Charakter-Hash-Feldern im State + KZG/LZG-Einträge mit hoher Resonanz als Neugier-Gravitationszentren

**Offene Fragen:**

1. UMAP-Stabilität: Ändert sich die 2D-Projektion der Gravitationszentren bei jedem Turn, verliert man die räumliche Orientierung. Lösung: Gravitationszentren einmal projizieren und fixieren, nur Turn-Punkte relativ einbetten.
2. Performance: UMAP auf ~30–50 Embeddings pro Turn (Gravitationszentren + Turn-Punkte + geladene KZG/LZG + Session-Turns) sollte <200ms sein. Zu verifizieren.
3. Skalierung: Bei vielen Gravitationszentren (>15) wird der Graph unübersichtlich. Top-K nach Relevanz filtern?
4. Überlappende Gravitationsfelder: Wenn zwei Zentren nahe beieinander liegen, überlappen ihre Ereignishorizonte. Rendering: additive Blending (überlappende Zonen werden intensiver) oder dominanter-Attraktor-Regel (stärkstes Feld gewinnt)?
5. Ereignishorizont-Radius: Direkt aus `EMOTIONALE_GRAVITATIONS_SCHWELLE` ableiten — der Radius im 2D-Raum entspricht der Cosine-Distanz, ab der Gravitation greift. Muss nach der UMAP-Projektion kalibriert werden.

**Priorität:** Niedrig-Mittel — Forschungs-Dashboard, kein produktionskritisches Feature. Aber enormer Wert für das Verständnis und die Kalibrierung von Gravitation, Gesprächsvektor und Dual-Emotion.

**Voraussetzungen:** Emotionale Gravitation (Epic Backlog) sollte zumindest konzeptionell stehen, damit die Gravitationszentren echte Daten haben. GV-Node sollte Schritte als separate Embeddings liefern.

---

## Epic: Matrix-Kanal + WireGuard-Zugang (Chat 68)

**Vision:** Nova als vollwertiger Chat-Partner über das Matrix-Protokoll, erreichbar von überall per WireGuard-VPN. Im Gegensatz zu Telegram kann Matrix über den Application-Service-Mechanismus *beide* Seiten steuern — User-Nachrichten und Bot-Nachrichten. Damit entfällt die `[Du]`-Krücke: Desktop-Eingaben erscheinen im Matrix-Client als echte User-Nachrichten, Novas Antworten als echte Nova-Nachrichten.

**Leitprinzip:** "Der Kanal ist dumm. Absichtlich." — Gilt weiterhin. Matrix war ein dritter Renderer neben Desktop (GTK4) und Telegram; **seit dem 24.08.2026 sind es zwei** — Telegram ist abgeschaltet. Markdown bleibt das kanonische Format.

### Was Telegram nicht kann, und warum es keine Einstellungssache ist

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

## Epic: Chat 72 — Folgearbeiten aus Dreischicht-Integration

### Reducer-Umbau — Strukturierter memory_context (Hoch, Chat 74)

**Stand Chat 74:** Erst-Iteration als String-Parser implementiert (Chat 74). Architektur-Schuld erkannt: Parser auf Pre-Format-String ist brüchig (Mehrzeilen-Plugin-Blöcke werden zerlegt). Sauberer Umbau geplant.

**Ziel:** Memory-Module und Plugin-Manager liefern strukturierte `ContextEntry`-Listen statt vorformatierter Strings. Reducer arbeitet auf Dicts. Ein Formatter-Tool baut den finalen `memory_context`-String für den Responder.

**Konzept-Dokument:** `novaberg-reducer-umbau_k.md` (Chat 74, vollständige Architektur, 7-Phasen-Plan STRUCT-1 bis STRUCT-7).

**Phasen:**

1. STRUCT-1: `ContextEntry`-TypedDict + State-Erweiterung
2. STRUCT-2: KZG/LZG-Module umstellen (alte Funktionen entfernen)
3. STRUCT-3: Plugin-Inventur + Basisklasse umstellen
4. STRUCT-4: Plugin-Manager einzeln umstellen
5. STRUCT-5: Enricher umbauen (sammelt Entries statt Strings)
6. STRUCT-6: Formatter-Tool + Reducer neu
7. STRUCT-7: Verifikation

**Big Bang:** Keine 2-Methoden-Schicht. Plugin-Manager brechen während des Umbaus, werden im Nachgang einzeln nachgezogen.

**Motivation:**
- Echo-Bug bei langen Sessions (~11+ Turns)
- ENRICHER-DUP (Mehrfach-Einträge im Kontext)
- Mehrzeilen-Notizen werden vom Parser fragmentiert (latenter Bug)
- Format-Wissen über fünf Stellen verteilt (KZG, LZG, Enricher, Plugin-Manager, Reducer-Parser)

**Was unverändert bleibt:**
- Responder-Schnittstelle (`state["memory_context"]` als String)
- Format-Konvention im Output-String
- CharacterGraph + HumanGraph Knoten/Kanten
- Alle anderen Nodes

**Priorität:** Hoch — der heutige Reducer arbeitet, hat aber latente Bugs und brüchige Architektur.

---

### Assoziatives Retrieval — Kontext als Geflecht (Mittel, Chat 74)

Der Enricher liefert heute isolierte Fragmente, ausgewählt nach Embedding-Ähnlichkeit zum Prompt. Bedeutung entsteht aber aus Verbindungen zwischen Einträgen — ein KZG-Treffer "Meister hat Lumi seit März" und "Lumi schläft viel" gehören zusammen, weil sie denselben Referenten teilen, nicht weil sie zum aktuellen Prompt ähnlich sind.

**Drei Assoziations-Dimensionen:**

- **Referentiell** — selbe Entität in mehreren Einträgen. KZG/LZG haben Embeddings, aber keine Entity-Marker. Anna und Lumi werden semantisch ähnlich (beide Lebewesen + Meister), aber nicht referentiell unterschieden.
- **Temporal** — Reihenfolge und Gleichzeitigkeit. Einträge tragen `erstellt_am`, aber kein Eintrag weiß, was zur selben Episode gehört. "Streit mit Anna" und "Lumi tröstete" am selben Tag sind narrativ verbunden, im Retrieval aber entkoppelt.
- **Kausal/thematisch** — Themen-Tags existieren, werden aber nur zur Verstärkung genutzt, nicht zur Cluster-Bildung beim Retrieval. Drei Einträge mit Thema "Beziehungsende" bilden zusammen eine Geschichte, die relevanter sein kann als zehn isolierte Hochsalienz-Treffer.

**Verwandtschaft:** Epic 16 (Entity-First-Retrieval) ist die referenzielle Spitze dieses Eisbergs. Akten-basiertes Retrieval ist der konkrete Implementierungsschritt der referentiellen Dimension.

**Priorität:** Mittel — konzeptuelle Vertiefung, kein akuter Blocker.

---

### Akten-basiertes Retrieval — Entitäten als kohärente Pakete (Mittel, Chat 74)

Heute ist die Einheit der Bewertung im Retrieval = einzelner Fakt. Beobachtung: Anna ist 20 Triples, davon werden 5 gefunden, ohne Zusammenhang. Schrott im Kontext.

**Vorschlag:** Einheit der Bewertung = **Entitäten-Akte**. Pro relevanter Entität liefert der Fakten-Agent eine geschlossene Akte mit allen Fakten + Metadaten + destillierter Beschreibung. Der Reducer bewertet Akten als Ganzes — entweder die ganze Anna-Akte rein oder ganz raus. Niemals halb-Anna.

**Drei Stellen müssen sich ändern:**

1. **Fakten-Agent als Akten-Lieferant** — Funktion `entity_akte_laden(entity_id) -> EntityAkte` mit allen Fakten + Metadaten + Zusammenfassung
2. **Enricher als Akten-Sammler** — identifiziert relevante Entitäten (über Embedding oder NER), zieht pro Entität die Akte
3. **Reducer als Akten-Bewerter** — bewertet jede Akte als Block; akzeptierte Akten werden als Ganzes weitergegeben, abgelehnte komplett verworfen

**Verbindung zum Reducer-Umbau:** Der heutige Reducer (Chat 74, String-Parser) und der Umbau (strukturierter memory_context) sind Voraussetzung. Akten-Bewertung ist eine Erweiterung, keine Ersetzung. Stufe 3 im Reducer-Konzept (Akten-aware) baut auf Stufe 1+2 (Exakt + Substring) auf.

**Voraussetzungen:**
- Fakten-Tabelle bereinigt (FAKTEN-RAUSCH gelöst, Reaktivierung möglich)
- Reducer-Umbau abgeschlossen (Daten strukturiert)
- Knowledge-Graph-Erweiterung (1-Hop für gefundene Entitäten)

**Priorität:** Mittel — adressiert die "zu wenig Richtiges"-Pathologie (Anna in Nürnberg ohne Schwester-Kontext). Pendant zur "zu viel Falsches"-Pathologie, die der Reducer-Umbau adressiert.

---

### Anker-Emotion (Grundemotion pro Charakter) (Niedrig, Chat 74)

Heute ist `emotions_profil` eine Beobachtung aus dem LZG (was wurde gefühlt). Eine Anker-Emotion wäre eine Setzung — eine Charakter-Eigenschaft, gegen die der Verlauf kontinuierlich zurückdriftet.

**Mechanik:** In `ei/berechnung.py` für Novas Strang bei jeder Akkumulation den Verlauf gewichtet zum Anker zurückdriften lassen:

```
nova_emotion[t+1] = α × empathie_signal + β × verlauf[t] + γ × anker
```

Mit `α + β + γ = 1`. Bei Marvin (depremierter Roboter): `anker = traurigkeit(0.6)`, `γ = 0.3`. Bei Nova heute: `γ = 0` (kein Anker, reine Beobachtung).

**Datenmodell:** Neue Spalte `grundemotion` in `charakter_hash` oder eigene Tabelle `charakter_grundemotionen` (mehrere Anker pro Charakter, z.B. "fundamental traurig, gelegentlich sarkastisch").

**Beispiel-Charaktere mit Anker:** Marvin (Hitchhiker), eeyore-artige Trauer, festes Zen-Gleichmut.

**Priorität:** Niedrig — keine Funktion gebrochen, aber öffnet expressiven Spielraum für Charaktere.

---

### Reducer-Node — Gegenspieler zum Enricher (Hoch, Chat 71/72) ✅ Erst-Iteration Chat 74

Der Reducer fasst ältere Session-Turns zusammen, statt alle 11+ Turns wörtlich an den Responder durchzureichen. Pendant zum Enricher: wo der Enricher anreichert, dünnt der Reducer aus.

**Motivation:** Echo-Bug (Chat 72) zeigt, dass Nova ab ~11 Turns die User-Nachricht wörtlich wiederholt. Vermutete Ursache: Kontext-Sättigung durch Session-Turns + KZG/LZG-Rauschen + Charakter-Hash + GV-Vorschlag.

**Status Chat 74:** Erst-Iteration als String-Parser implementiert. Funktioniert für Exakt-Dedup von KZG/LZG-Einträgen. Architektur-Schuld erkannt — sauberer Umbau geplant (siehe oben: Reducer-Umbau).

---

### GV-Panel: Dreischicht-Felder visualisieren (Hoch, Chat 72)

`gv_detail` enthält seit Chat 72 die volle Entscheidungskette: Achsen, Sektor, Cluster, Repertoire, Charakter-Gewichtung, Sprünge, Absicht, Strategie, Vehikel. Das GV-Panel soll diese Felder detailliert anzeigen — die komplette Entscheidungskette von EI-State bis Antwort-Strategie sichtbar machen.

**Was zu sehen sein soll:**

- 6 Achsen (Werte + Visualisierung)
- Aktiver Sektor (1 von 64) mit Cluster-Zuordnung (1 von 13)
- Repertoire (Strategien × Absichten × Vehikel) mit Charakter-Gewichtung
- Gewählte Absicht / Strategie / Vehikel als Endergebnis
- Sprünge zwischen Sektoren über die letzten Turns

**Priorität:** Hoch — ohne Sichtbarkeit ist die neue Architektur nicht debugbar oder kalibrierbar.

**✅ Erledigt Chat 116 (29.07.2026)** — bis auf einen Punkt, der so nicht baubar ist.

Gebaut wurden Achsen, Sektor, Cluster, Absicht/Strategie/Vehikel, Sprünge und Impuls (Chat 73), die verwandten Erinnerungen und zuletzt der Korridor: **`repertoire` mit `charakter_gewichtung`**, dazu **`korridor_verstoesse`** (Chat 114, in der ursprünglichen Liste nicht enthalten — die Gegenprobe zum Repertoire). Das Panel zeigt alle sieben Strategien mit Eignung und Affinität, die gewählte hervorgehoben, darunter die Verstoß-Zeile.

**Zwei bewusste Abweichungen vom Prompt-Block**, beide im Panel-Docstring begründet:

- Der Prompt lässt `unpassend` ganz weg, damit das LLM nicht danach greift. Das Panel zeigt diese Strategien mit `✗` — wer beurteilen will, ob der Korridor richtig saß, muss sehen, was ausgeschlossen wurde.
- `dreischicht_prompt_bauen` setzt bei fehlender Gewichtung `0.5` ein. **Das Panel tut das nicht** und zeigt `—`. Siehe `GV-CHARAKTER-DEFAULT-UEBER-MESSBEREICH` in `novaberg-bugs.md`: Der Default liegt über jedem gemessenen Wert und erschiene als beste Passung.

**Nicht baubar aus `gv_detail`:** „Sprünge zwischen Sektoren über die letzten Turns". Der Blob trägt immer nur den aktuellen Turn, der Redis-Key wird bei jedem Turn überschrieben. Eine Sektor-Bahn über mehrere Turns braucht eine eigene Historie — das ist ein anderer Bau und nicht Teil dieses Punktes. Wer sie will, legt sie als eigenen Backlog-Eintrag an.

---

### Modus-Kalibrierung: spielerisch vs. emotional (Niedrig, Chat 72)

Perzeption klassifiziert 😍-Katzen-Chat als `gespraechs_modus="emotional"` statt `"spielerisch"`. Folge: Tiefe-Achse 0.70 statt 0.40, was die Sektor-Berechnung in der Dreischicht verschiebt.

**Lösungsansatz:** Modus-Beispiele im Perzeption-LLM-Call schärfen. Spielerisch (Tier-Niedlichkeit, Quatschen, leichte Themen) klar von emotional (Beziehungsthemen, Sorgen, Tiefe) abgrenzen.

**Priorität:** Niedrig — kosmetische Verschiebung der Sektor-Verteilung, keine Funktion gebrochen.

---

## Epic: Memory-Promotion-Korrektur (Chat 75)

**Status:** Konzept
**Bezug:** PROMO-DROP1, PROMO-CLUSTER-EI, PROMO-DUAL-IMPL (siehe novaberg-bugs.md, Sektion Datenqualität)
**Vorbedingung:** Reducer-Umbau (novaberg-reducer-umbau_k.md) abgeschlossen.

### Phasen-Übersicht

| Phase | Inhalt | Status |
|---|---|---|
| M1 | Doppelpipeline konsolidieren (PROMO-DUAL-IMPL) | ✅ Chat 77 |
| M2 | LZG-Schema erweitern (PROMO-DROP1, Schema-Teil) | ✅ Chat 78 |
| M3a | Promotion-Code: themen + kzg_erstellt_am | ✅ Chat 84 |
| M3b | Promotion-Code: entitaet_ids + timeline_id (wartet auf M5) | ⬜ blockiert |
| M4 Teil 1 | Cluster-Promotion EI-Aggregation — Backfill | ✅ Chat 82 |
| M4 Teil 2 | Cluster-Promotion EI-Aggregation — Code-Fix | ✅ Chat 83 |
| M5a | Charakter-Hash profitiert von echten EI-Profilen | ✅ Chat 83 (Backfill-Stand) + Chat 84 (Code-Fix-Stand) |
| M5b | FaktenManager-Reaktivierung | ⬜ Offen |
| M5c | Themen-Cluster-Promotion smarter | ⬜ Offen |

### Hintergrund

Ein Audit der Promotion-Pipeline KZG→LZG in Chat 75 hat drei Datenverluste sichtbar gemacht, die in den Bug-Einträgen einzeln dokumentiert sind. Die drei Befunde hängen zusammen und sollten in einer geschlossenen Sequenz angegangen werden. Sie tangieren die Akten-Vision direkt: Ohne Themen-Persistenz und ohne intakte EI-Felder im LZG sind später keine sinnvollen Akten-Aggregate möglich.

### Reihenfolge nach dem Reducer-Umbau

**Phase M1 — Doppelpipeline konsolidieren (PROMO-DUAL-IMPL) ✅ Chat 77.**
Verifizieren, ob `services/shadow_agent/tasks/lzg_promotion.py` noch von irgendeinem Pfad aufgerufen wird. Falls nicht: entfernen. Falls doch: Aufrufer migrieren, Legacy entfernen. Eine einzige Promotion-Implementierung als Voraussetzung für die nächsten Phasen.

**Phase M2 — LZG-Schema erweitern (PROMO-DROP1, Schema-Teil) ✅ Chat 78.**
  Vier neue Spalten in `langzeitgedaechtnis` (`themen TEXT[]`, `gedaechtnistyp VARCHAR(20)`, `kzg_erstellt_am TIMESTAMPTZ`, `entitaet_ids INTEGER[]`) plus `timeline_id INTEGER FK timeline(id)` — alle nullable, zugehörige GIN/BTREE-Indizes. Idempotent in `db/init.sql`. **Spiegelung in `main.py:schema_migrieren()` als Schema-Restschuld nachgezogen Chat 84 (M3-A).**

**Phase M3 — Promotion-Code anpassen.** Zweistufig laut Magnet-Konvention §4.

**M3a — themen + kzg_erstellt_am ✅ Chat 84.** Promotion-Code überträgt beim
KZG→LZG-Schritt zwei Felder aus dem KZG-Hash:
- `themen` (kommaseparierter String → `TEXT[]`, Cluster-Pfad: Vereinigung über Mitglieder)
- `kzg_erstellt_am` (Unix-float-String → `TIMESTAMPTZ`, Cluster-Pfad: frühestes über Mitglieder)

Eingriff an zwei INSERT-Stellen: `_eintrag_verarbeiten` (Single-Promotion) und
`_lzg_eintrag_schreiben` (Cluster-Pfad zentral). Drei Cluster-Aufrufer profitieren
über die zentrale Methode. Internes Aggregieren statt Signatur-Erweiterung — kein
Diff in den drei Aufrufern, identisches Pattern wie für die sieben EI-Felder aus
M4. Loader `_kzg_partition_laden` um Lade-Pfad für `erstellt_am` erweitert
(10 Zeilen, identisches Pattern zu `arousal`/`intentionen`). Single-Pfad nutzt
`sorted({…})` symmetrisch zum Cluster-Pfad — für 1-Element-Cluster identisches
Ergebnis.

**M3b — entitaet_ids + timeline_id ⬜ blockiert auf M5.** Beide Felder können erst
übertragen werden, wenn der KZG-Schreibpfad sie selbst befüllt. Magnet-Konvention §4:
"M5 (Salienz-Pfad pro Turn): KZG-Schreibpfad bekommt aufgelöste entitaet_ids und
ggf. timeline_id direkt mit." Bis dahin bleiben die beiden Spalten leer.

**`gedaechtnistyp`** (Backlog-Phase-Beschreibung Pre-Chat-85): nicht in M3, weil
kein Klassifikator-Pfad existiert. M5 oder eigener Klassifikator-Sprint.

**Phase M4 — Cluster-Promotion EI-Aggregation (PROMO-CLUSTER-EI).** Zweistufig.

**Teil 1 — Backfill ✅ Chat 82.** Messung ergab 19 von 20 LZG-Einträgen mit Default-Profil (`emotion='neutral' AND arousal=0.5`). Standalone-Skript `Korrektur.py` hat alle 19 per Qwen3-32B-CPU re-klassifiziert (17 automatisch über Skript, 2 händisch nach LLM-Validierungs-Drift). Restwert nach Backfill: 0 Default-Einträge.

**Teil 2 — Code-Fix ✅ Chat 83.** Sieben EI-Felder werden im Cluster-Pfad aggregiert (Counter-Mehrheit, Mittelwert, Mengen-Vereinigung). `emotions_vektor` wurde gleichzeitig aus dem LZG-Schema entfernt — siehe Roadmap-Block Chat 83. Alle drei INSERT-Aufrufer (`_cluster_insert_kohaerenz`, `_cluster_update_kohaerenz` Widerspruchs-Pfad, `_cluster_update` Widerspruchs-Pfad) profitieren über den gemeinsamen `_lzg_eintrag_schreiben`. Einzel-Promotion-INSERT mit-angepasst.

**Phase M5 — Agenten nachziehen.**
Erst nach M1–M4 abgeschlossen sind, werden die Agenten an die neue Memory-Struktur angepasst:
- **FaktenManager-Reaktivierung** (heute durch `continue` im Enricher gesperrt seit Chat 71). Voraussetzung: Themen-basierte Verknüpfung im LZG verfügbar (M2/M3).
- **Themen-Cluster-Promotion** könnte mit echtem `themen[]`-Feld smarter werden (heute nur über Embedding-Cluster).
- **Charakter-Hash-Generierung** (`charakter_hash`) profitiert von echten EI-Profilen aus Cluster-Promotion (M4) — Profile werden weniger neutral. ✅ **Verifiziert Chat 83 (Backfill) und Chat 84 (Code-Fix-Bedingung).** Empirische Prüfung der `charakter_hash`-Tabelle nach M4-Sprint zeigt vertraute, emotional warme Beziehungsprofile beider Sichten — CHAR-BEZ-STALE damit ebenfalls geschlossen.

### Auswirkung auf Akten-Vision

Diese fünf Phasen sind Vorarbeit für die Akten-Architektur (siehe `novaberg-reducer-umbau_k.md` §10 „eigenständige Erweiterung"). Ohne intakte Themen, ohne intakte EI-Profile und ohne ursprünglichen Zeitstempel im LZG fehlen die Schienen, an denen Akten-Aggregate später ansetzen. Der Knowledge Graph (`entitaeten` + `fakten`) hat seine Struktur bereits — ihm fehlt nur die Verknüpfung mit dem korrigierten LZG.

### Folge-Themen aus M4 Teil 2 (Chat 83)

#### PROMO-CLUSTER-EI-UPDATE — UPDATE-Pfade aktualisieren keine EI-Felder

**Status:** ⬜ Offen
**Entdeckt:** Chat 83 (Brudi-Audit zu PROMO-CLUSTER-EI)
**Symptom:** Bestätigungs-Updates in `_cluster_update_kohaerenz` (`agents/promotion/agent.py:1141-1151`) und `_cluster_update` (`:939-950`) aktualisieren nur `inhalt`, `embedding`, `gewicht`, `verstaerkt_am`. Die EI-Felder des bestehenden LZG-Eintrags bleiben eingefroren — neue Cluster-Mitglieder fließen nie in das EI-Profil bestehender LZG-Einträge ein.
**Konzeptionelle Frage:** Soll der Mehrheits-Wert ersetzt, mit dem alten gemittelt, oder gewichtet nach Mitglieder-Anzahl gemerged werden? Nicht trivial.

**Erweitert Chat 84 (M3-B-Side-Finding):** Die UPDATE-Pfade aktualisieren auch
die Magnet-Felder nicht:
- `themen` (Cluster-Mitglieder mit neuen Themen-Tags fließen nicht in den
  bestehenden LZG-Eintrag)
- `kzg_erstellt_am` (bleibt am ursprünglichen Wert, frühere Cluster-Mitglieder
  überschreiben den Stand nicht)

Strukturell dasselbe Muster wie für die EI-Felder. Konzeptionelle Frage analog:
Magneten ersetzen, vereinen, oder gewichten nach Mitglieder-Anzahl? Nicht trivial.
Bei einer Vereinigungs-Strategie würde sich `themen` über mehrere Bestätigungen
sukzessive bereichern; bei `kzg_erstellt_am` wäre `LEAST(alt, neu)` semantisch
plausibel (frühestes Auftreten der Erinnerung).

**Prio:** Mittel.

#### PROMO-CLUSTER-TIE-DETERMINISM — Counter-Tie-Break nicht deterministisch

**Status:** ⬜ Offen
**Entdeckt:** Chat 83 (Brudi-Audit zu PROMO-CLUSTER-EI)
**Symptom:** `Counter.most_common(1)` löst Ties über die Insertion-Order auf. Die heutige Reihenfolge stammt aus `redis_client.keys(...)` und ist nicht semantisch sortiert. Bei zwei gleichhäufigen Werten (z. B. `freude` 3× und `zufriedenheit` 3×) ist nicht reproduzierbar, welcher gewinnt.
**Auswirkung:** Niedrig — betrifft auch heute schon `beobachter`/`dimension`. Kein Bug, sondern Tech-Debt für künftige Konsistenz.
**Lösung:** Quell-Liste vor Counter explizit sortieren (z. B. nach `erstellt_am` absteigend → "neuerer Eintrag gewinnt bei Tie").
**Prio:** Niedrig.

#### PROMO-DESTILL-DEAD — `_destillation_insert` ohne Aufrufer

**Status:** ⬜ Offen
**Entdeckt:** Chat 83 (Folge des Löschens von `_cluster_insert`)
**Symptom:** Helper-Methode `_destillation_insert` (`agents/promotion/agent.py:~1317`) wurde nur von `_cluster_insert` aufgerufen. Nach dessen Löschen (Chat 83, ~28 Zeilen) hat `_destillation_insert` keinen Aufrufer mehr.
**Lösung:** Methode löschen (~35 Zeilen). Vor dem Löschen `grep` zur Sicherung.
**Prio:** Niedrig — Cleanup-Sprint.

#### PROMO-INTENTIONEN-FORMAT-DRIFT — Einzel- vs. Cluster-Pfad

**Status:** ⬜ Offen
**Entdeckt:** Chat 83 (Brudi-Bericht, Auffälligkeit 4)
**Symptom:** Einzel-Promotion reicht den `intentionen`-JSON-String aus dem KZG 1:1 ins LZG-INSERT durch. Cluster-Promotion macht `json.loads → set-merge → json.dumps(sorted(...))`. Das Ergebnis: LZG-Einträge aus dem Cluster-Pfad haben sortierte, deduplizierte Intentionen, Einträge aus dem Einzel-Pfad nicht. Ein zukünftiger Reader, der über `intentionen` filtert oder sich auf Reihenfolge verlässt, würde überrascht.
**Lösung:** Einzel-Pfad ebenfalls auf parsen + sortieren + json.dumps umstellen. Konsistenz an einer Stelle (`_lzg_eintrag_schreiben` oder ein Pre-Processing-Helper).
**Prio:** Niedrig.

---

## Epic: Memory-Kern-Umbau (Synapsen-Modell, Chat 86)

**Status:** **Alle zehn Sprints abgeschlossen (P1–P9 in Chat 125, P10 in Chat 126).** Der Umbau ist gebaut. ~~Offen bleiben zwei Reste, die keine Sprints sind: die dünne Zeit- und Entitätsschicht aus P3 (unten) und die ungemessene Wirkung von P10 (`P10-WIRKUNG-UNGEMESSEN`).~~ → **Ein Rest, seit 07.08.2026:** die dünne Zeit- und Entitätsschicht aus P3 (unten). `P10-WIRKUNG-UNGEMESSEN` ist beantwortet; die Kalibrierung der Cluster-Faktoren, die daraus folgt, ist keine Synapsen-Arbeit mehr, sondern ein Bauteil des Kalibrierungskonzepts.

*Die vorige Angabe „P0–P3 implementiert, P4 wartet auf MS-Welle" stammte aus Chat 91 und war fünf Phasen im Rückstand — P4 bis P8 sind zwischen Chat 98 und 111 gebaut worden, ohne dass diese Tabelle nachgezogen wurde. Nachgemessen am 02.08.2026 gegen den Bestand, nicht gegen die Doku.*
**Bezug:** novaberg-memory-synapsen_k.md, novaberg-memory-synapsen-p4-entscheidungen_k.md (Chat 91)
**Vorbedingung:** Microservice-Modell-Queue (eigenes Epic, Chat 91). P4 setzt auf der MS-Welle auf — Embedding-Konsolidierung und `pixie_llm_call`-Konsolidierung sind strukturelle Blocker.

### Phasen-Übersicht

| Phase | Inhalt | Status |
|---|---|---|
| Punkt 1 | Vision und Leitprinzipien | ✅ Chat 86 |
| Punkt 2 | Schema (lzg_knoten, lzg_kanten) + Konstanten | ✅ Chat 86 |
| Punkt 3 | Schreibpfad-Sicht (KZG→LZG mit Kantenbildung) | ✅ Chat 86 |
| Punkt 4 | Lesepfad-Sicht (Spreading-Activation, Charakter-Hash) | ✅ Chat 86 |
| Punkt 5 | Decay-Logik (Knoten und Kanten) | ✅ Chat 86 |
| Punkt 6 | Gesprächs- und Node-Log (Forensik-Schicht) | ✅ Chat 86 |
| Punkt 7 | Migration und selektive Bestandsdaten-Übernahme | ✅ Chat 86 |
| Punkt 8 | Bug- und Backlog-Reset | ✅ Chat 86 |
| Punkt 9 | Implementierungs-Phasen P1–P10 | ✅ **P1–P9 (Chat 125), P10 (Chat 126)** — Stand am 02.08.2026 gegen den Bestand gemessen, siehe Tabelle unten |
| Punkt 10 | P4-Klärungspunkte (K1–K10) | ✅ Chat 91 — `novaberg-memory-synapsen-p4-entscheidungen_k.md` |

### Stand der Sprints, gemessen am 02.08.2026

| Sprint | Belegt durch |
|---|---|
| **P1** Pipeline-Log | ✅ 34.832 Zeilen |
| **P2** `lzg_knoten` / `lzg_kanten` | ✅ Tabellen gefüllt |
| **P3** Magnetfelder im KZG-Schreibpfad | 🔶 themen 99 %, `entitaet_ids` 31 %, `timeline_id` **2,6 %** — siehe unten |
| **P4** Neue Promotion | ✅ 1108 Knoten, 110.340 Kanten |
| **P5** Enricher liest neu | ✅ `spreading_lesen` |
| **P6** Decay für Knoten | ✅ `synapsen_decay` im Zeitplan |
| **P7** Charakter-Hash auf neuer Topologie | ✅ liest `lzg_knoten` |
| **P8** Migration Bestandsdaten | ✅ gegenstandslos: alte Tabelle hatte 0 Zeilen |
| **P9** Codeschloss | ✅ Tabelle gelöscht, 2172 Zeilen entfernt |
| **P10** Wahrnehmungs-Gravitation | ✅ `wahrnehmung_verschieben`, live gemessen — Wirkung offen, siehe unten |

**Zu P10 — gebaut und live, die Wirkung aber ungemessen.** Die Verschiebung greift: Ein Turn nahe an einem langfristigen Ziel erreichte Aktivierungs-Stärke 0.631 und drehte den Suchschlüssel um 1,14° (Cluster `schlachtfeld`, Faktor 0.05). Genau diese Kleinheit ist der Befund — **Aktivierungsschwelle und Verschiebungswirkung ziehen gegeneinander:** Ein Ziel überschreitet die Schwelle von 0.4 nur, wenn es der Frage schon ähnlich ist, und in Richtung eines fast parallelen Vektors zu verschieben dreht kaum. Bei sieben aktiven Zielen und einem thematisch entfernten Turn lagen alle Stärken zwischen 0.102 und 0.212, also unter der Schwelle. Entscheidbar ist das erst an einem Korpus, in dem Ziele und Fragen auseinanderliegen — wie bei P3 also an der Charakterbildungs-Messreihe.

**`P10-WIRKUNG-UNGEMESSEN`** ✅ **beantwortet am 07.08.2026**
**Frage:** Ändert die Verschiebung die Trefferliste — und ab welcher Drehung?

**Gemessen, beide Schichten auf demselben Korpus:** 322 Turns aus `pipeline_log` (`art='turn_roh'`), eine Sitzung, dieselben Embeddings — nicht gegen die fünf Tage ältere LZG-Zahl, weil deren Korpus ein anderer ist und die Schichtdifferenz sonst mit einer Korpusdifferenz vermischt wäre. Bei der produktiven Schwelle 0.40, nach Cluster-Faktor:

| Faktor | KZG ändert die Trefferliste | LZG |
|---|---|---|
| 0.05 | **20,0 %** | 0,0 % |
| 0.10 | 45,0 % | 0,0 % |
| 0.20 | 55,0 % | 5,0 % |
| 0.25 | 75,0 % | 15,0 % |
| 0.30 | 75,0 % | 15,0 % |

**Die Antwort ist ja — und das Kurzzeitgedächtnis reagiert über alle Schwellen drei- bis fünfmal so oft wie das Langzeitgedächtnis.** Die im Umfangsvermerk notierte Vermutung trifft damit zu, in dieser Richtung.

**Der Mechanismus steht in den Listengrößen, nicht in der Verschiebung:** KZG Median **10**, nie leer; LZG Median **3**, Maximum 3, in **54 von 322 Turns leer**. Eine Menge aus drei Einträgen hat wenig Rand, an dem eine Drehung um ein Grad die Mitgliedschaft kippt.

**Die Tiefe ist klein.** Ändert sich die KZG-Menge bei Faktor 0.05, tauscht der Median **1 von 10** Einträgen (Maximum 1); erst bei 0.30 sind es 2. Zusammengerechnet für den Betrieb: 6,2 % der Turns lösen aus, davon ändern 20 % ihre Liste — **rund ein Turn von achtzig** bekommt eine von zehn Kurzzeit-Erinnerungen ausgetauscht.

**In 7 Fällen fand der verschobene Schlüssel Anker, wo der rohe keine fand** — die Verschiebung kann Erinnerung nicht nur umsortieren, sondern erzeugen.

**Zwei Grenzen der Zahl, beide bindend für ihre Verwendung:**

- **Untergrenze, kein Punktwert.** Verglichen werden *Mengen*. Eine Drehung, die dieselben zehn Einträge anders sortiert, zählt als „unverändert" — für den Prompt ist sie es nicht.
- **Wirkung, nicht Güte.** Ob die veränderten Anker die *besseren* sind, sagt die Messung nicht.

**Rest:** Die Kalibrierung der Cluster-Faktoren ist damit beginnbar — die Wirkung ist belegt, die Achse zeigt Reserve (20 % bei 0.05 gegen 75 % bei 0.30). Sie gehört als Bauteil der Klasse „Beiträge" in `novaberg-kalibrierung_k.md` §3.2 und braucht dort zuerst einen Erwartungskorridor.

**Zu P3 — die dünnen Magnetfelder sind überwiegend kein Defekt.** Gemessen: Von 1076 Knoten ohne `timeline_id` enthalten **5** überhaupt einen Datums- oder Zeitausdruck; von 766 ohne `entitaet_ids` nennen 76 % nichts Bekanntes. Der Korpus besteht aus Weltwissen — Entropie, Hawking-Strahlung, Raumzeit —, und Weltwissen hat weder Referenz noch Datum. Verbleibende 185 Knoten nennen einen bekannten Begriff als ganzes Wort, ohne ihn zu verlinken; das ist ein Fundlisten-Eintrag, kein Sprint.

**Woran das nicht messbar ist:** an diesem Korpus. Die Charakterbildungs-Messreihe (§0b) setzt in Turn 7 und 9 jedes Bogens einen harten Fakt mit Name, Zahl, Datum und Ort — sechs Läufe ergeben zwölf Referenzen mit Zeitbezug plus zwölf Abrufe. Erst danach lässt sich sagen, ob die Entitäts- und Zeitschicht greifen, wenn es etwas zu greifen gibt.

**Kantenzusammensetzung heute:** embedding 87,7 %, themen 10,9 %, entitaet 1,1 %, timeline 0,3 %. Das ist erwartbar und kein Versagen — Embedding-Ähnlichkeit ist eine dichte Relation zwischen allen hinreichend ähnlichen Paaren, ein geteilter Begriff eine seltene. Der Kern des Umbaus war, dass jede Erinnerung ein eigener Knoten **bleibt** statt zu einem Aggregat zu verschmelzen; das hält.

### Hintergrund

Die heutige Cluster-Promotion verdichtet mehrere KZG-Einträge zu einem aggregierten LZG-Eintrag und löscht die Quellen. Cluster-Qualitäts-Diagnose in Chat 86 (LZG-Eintrag 67: Anna+Rosa+Grillen-Vermischung) zeigte strukturelle Grenzen der Aggregat-Schicht: semantisch fremde Inhalte landen in einem Eintrag, weil Embedding-Ähnlichkeit allein keine Entitäts-Trennung kennt. Die Diagnose führte zu einem Konzept-Sprung — das Memory-Modell wechselt von Aggregat zu assoziativem Netz.

Jeder ehemalige KZG-Eintrag bleibt als eigenständiger Knoten in `lzg_knoten` erhalten, Verbindungen leben in `lzg_kanten` mit gerichteten Datensätzen, eigenem Decay und mehrschichtiger Bildungs-Logik (Entität, Timeline, Thema, Embedding). Phänomenologisch näher am menschlichen assoziativen Gedächtnis (Hebbsches Prinzip), strukturell sauberer, mit forensisch nachvollziehbarem Aufbau.

### Verhältnis zum Memory-Promotion-Epic (Chat 75)

Mehrere Phasen des Memory-Promotion-Epics werden durch den Synapsen-Umbau anders gelöst oder obsolet:

- **M3b** (entitaet_ids + timeline_id im Promotion-Code) — wird Teil von Punkt 3 (Schreibpfad-Sicht des Synapsen-Modells)
- **M5a** (Charakter-Hash profitiert von echten EI-Profilen) — bereits erledigt durch Backfill und Code-Fix in Chat 82/83/84
- **M5b** (FaktenManager-Reaktivierung) — bleibt separat, hängt nicht direkt am Synapsen-Umbau. **Chat 91:** wird als M2.5b geführt (FaktenAgent als eigenständige Fachabteilung analog TimelineAgent, kein Plugin mehr). Schreibpfad in `fakten`-Tabelle bleibt orthogonal zum Synapsen-Modell. Verschoben auf nach Synapsen-Umbau, eigenes Faktengedächtnis-Konzeptpapier siehe Synapsen-§3.2.

  **Chat 115 — Bestandsaufnahme vor der Umsetzung.** Das Faktengedächtnis ist gewollt und eingeplant; die Frage ist allein der Zeitpunkt. Gemessen 28./29.07.2026:

  - `fakten` hat **0 Zeilen**. Der in K2 akzeptierte Preis war ein *eingefrorener* Bestand (411 Fakten am 12.07.2026); der Reset am 27.07.2026 hat ihn entfernt. Aus „keine neuen Fakten" wurde „keine Fakten" — eine Folge, die die Festlegung nicht vorsah und die niemand beschlossen hat.
  - Die Vorbedingung aus Synapsen-§3.2 („sobald der LZG-Kern steht") ist **nicht erfüllt**. Die beiden Felder, über die §3.2 die zwei Gedächtnis-Modalitäten verschränkt, sind dünn: `entitaet_ids` in 65 von 296 Knoten (22 %), `timeline_id` in **1** von 296 (0,3 %). Ein FaktenAgent auf diesem Untergrund produzierte Fakten, deren Verschränkung mit den Erinnerungen — der eigentliche Gewinn nach §3.2 — nicht stattfände.
  - Der alte `PromotionAgent` liegt vollständig im Repo und trägt die Extraktionslogik als Vorlage (Call 1, Call 2, Entity-Resolution, Edge-Invalidation). Laut Commit `4dd6ac6` bleibt er „dormant through P9". **P9 hat nicht stattgefunden** — es ist im Konzept das Codeschloss und setzt P5–P8 plus eine Woche Beobachtung voraus. Läuft P9 vor M2.5b, ist die Vorlage weg.
  - **Mitzunehmen bei der Umsetzung:** Der Schlüssel-Mismatch aus GV-ENTITY-HOP-FINDET-NICHTS (Themenphrase gegen Eigenname) und die Wert-Fakten-Grenze aus GV-WERT-FAKTEN-BLIND bestehen unabhängig vom leeren Bestand fort. Beide treffen jeden, der die Tabelle wieder liest — nicht nur den GV-Node.
  - **Wer heute davon abhängt:** niemand mehr im Lesepfad des GV-Nodes; der wurde in Chat 115 auf `lzg_resonanz` umgehängt. `_entity_kontext_laden` schläft dort mit Weckbedingung im Code. Die übrigen vier Leser (Enricher-Hook, `fakten_abfragen`, `fakten_historie`, Router-Intent `fakten_management`) sind funktionsfähig und lesen eine leere Tabelle.
- **M5c** (Themen-Cluster-Promotion smarter) — wird strukturell obsolet, weil keine Themen-Cluster mehr aggregiert werden

### Scope-Definition

**Im Umbau-Scope:** KZG→LZG-Promotion, Synapsen-Graph-Struktur, Decay-Logik für Knoten und Kanten, Reinforcement (Co-Aktivierung und Schicht-basierte Initialisierung), Gesprächs- und Node-Log.

**Außerhalb des Scopes (pausiert):** HumanGraph, CharacterGraph, Salienz-Knoten, KZG-Schreibpfad, Pixie-Plugins, alle Pixie-Agenten außer Promotion, Metakognition, Skills-System.

### Folgewirkung auf offene Bugs

Voraussichtlich strukturell obsolet nach Umbau:

- CLUSTER-THEMEN-DEDUP
- CLUSTER-META-CONTAMINATION
- PROMO-CLUSTER-EI-UPDATE
- PROMO-CLUSTER-TIE-DETERMINISM
- PROMO-DESTILL-DEAD
- PROMO-INTENTIONEN-FORMAT-DRIFT
- LZG-HAEUFIGKEIT-AMBIVALENT (bekommt klare Semantik im neuen Schema)

Endgültige Re-Evaluation in Punkt 8.

### Auswirkung auf Akten-Vision

Der Synapsen-Umbau ist die strukturelle Voraussetzung für die Akten-Architektur. Knoten und Kanten mit ihren Magnet-Feldern (Entitäten, Timeline, Themen) bilden die Anker, an denen Akten-Aggregate später ansetzen können. Ohne intakte assoziative Verbindungen wäre Akten-Logik nur ein zweites Aggregat-System über dem bestehenden — mit dem Umbau wird sie eine natürliche Subgraph-Abfrage.

---

## Epic: Microservice-Modell-Queue (Chat 91) — ✅ abgeschlossen Chat 97

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

## Tech-Debt: Reducer-Umbau-Nachzügler (Chat 75)

**Status:** Beobachtet
**Bezug:** novaberg-reducer-umbau_k.md, Implementierungsbericht (Abschnitt 13)

Drei kleine Punkte aus dem Reducer-Umbau, die nicht im Scope der STRUCT-Phasen lagen:

### REDUCER-CONFIG-DEAD

**Symptom:** Konfigurations-Konstanten `REDUCER_AKTIV` und `REDUCER_LOG_REMOVED` in `config.py:1008-1013` werden nach dem Umbau nicht mehr genutzt — der neue Reducer hat keinen Master-Schalter mehr und loggt entfernte Einträge fest auf DEBUG-Level.
**Fix:** Beide Konstanten entfernen, falls keine externen Konsumenten existieren (`grep` zur Sicherheit).
**Prio:** Niedrig.

### LOGGER-NAMESPACE

**Symptom:** Reducer-Logger heißt `graph.nodes.reducer` (über `logging.getLogger(__name__)`), während der Rest des Servers über das `ki_server.<modul>`-Schema loggt. Folge: `grep "ki_server"` über das Log-Archiv erfasst den Reducer nicht.
**Fix:** Reducer-Logger-Name entweder explizit auf `ki_server.reducer` setzen oder zentrale Logging-Konfiguration so anpassen, dass alle `graph.*`-Module das Präfix erben.
**Prio:** Niedrig — kosmetisch, kein funktionaler Schaden.

### SESSION-SUMMARY-INACTIVE

**Symptom:** In allen Smoke-Test-Turns von Chat 75 zeigte das Reducer-Logging `Gruppe summary: 0 Eintraege`. Der Session-Summary-Pfad im Enricher (STRUCT-5b: Entry mit `quelle="summary"`) wurde nie aktiviert.
**Vermutung:** Der Session-Summary wird vermutlich nur unter bestimmten Bedingungen erzeugt (z.B. ab N Turns Session-Länge) und war im Test-Szenario nicht erreicht. Möglich aber auch: Der Pfad ist tatsächlich tot (z.B. weil die zugrundeliegende Funktion nie returns oder die State-Variable nie gesetzt wird).
**Fix:** Verifizieren, unter welchen Bedingungen der Session-Summary heute erzeugt wird, und prüfen, ob die Bedingungen sinnvoll sind.
**Prio:** Niedrig — Beobachtung, kein bestätigter Bug.

### PIX-CLEAN — Toter ShadowAgent-Runner und aufruflose Tasks (Chat 77)

**Status:** Beobachtet
**Bezug:** M1-Audit Memory-Promotion-Korrektur (Chat 77)

Der M1-Audit hat bestätigt, dass `services/shadow_agent/runner.py`
(`schatten_arbeit_ausfuehren`) und damit alle Tasks unter
`services/shadow_agent/tasks/` aufruflos sind. Weder `main.py` noch
`api/admin.py` rufen den Legacy-Runner. `lzg_promotion` wurde in M1
entfernt — die übrigen Tasks bleiben vorerst stehen:

- recherche, vertiefen, nachfragen, charakter_hash, lzg_decay,
  wiedervorlage, nova_gedaechtnis, aufraeumen

**Empfehlung:** Pro Task denselben Audit fahren wie für `lzg_promotion`:

1. Statische Aufrufer suchen
2. Pixie-Router-Tabelle prüfen, ob die Aufgabe an einen neuen Agenten
   geroutet wird (oder ob sie überhaupt noch in eine Queue gepusht wird)
3. Bei Karteileichen-Befund Datei entfernen

Erst danach kann `runner.py` selbst und der `discover_tasks()`-Pfad in
`services/shadow_agent/__init__.py` entfernt werden. Die Utilities
(`shadow_queue_push`, `nova_vorwissen_laden`, etc.) bleiben in jedem Fall.

**Prio:** Niedrig — kein funktionaler Schaden, reine Code-Hygiene.

### INIT-SQL-VERALTET — init.sql nicht reproduzierbar

**Status:** ⬜ Offen
**Entdeckt:** Chat 85 (Brudi-Befund bei Promotion-Fix-Recherche)

**Symptom:** `db/init.sql` enthält ALTER-TABLE-Statements und repräsentiert nicht den Soll-Zustand des Schemas. Tabelle `ziele` fehlt komplett (existiert in der Live-DB, wurde aber nie ins `init.sql` aufgenommen).

**Auswirkung:** Setup-from-scratch ist nicht reproduzierbar. Frischer Container plus `init.sql` ergibt kein lauffähiges System.

**Lösung:** `init.sql` neu aufbauen als CREATE-only-Definition aller Tabellen plus Indizes. ALTER-Anweisungen entfernen oder in versioniertes Migrations-Skript verschieben (Alembic empfohlen).

**Vorbedingung:** Keine.
**Prio:** Mittel — wird im Rahmen des Code-Audit-Sprints adressiert.

### LZG-HAEUFIGKEIT-AMBIVALENT

**Status:** Beobachtet
**Entdeckt:** Chat 86 (Cluster-Qualitäts-Diagnose, Nebenbefund)

**Symptom:** Die UPDATE-Pfade `_cluster_update` und `_cluster_update_kohaerenz` (Bestätigungs-Updates) inkrementieren `langzeitgedaechtnis.haeufigkeit` nicht — modifiziert werden nur `inhalt`, `embedding`, `gewicht`, `verstaerkt_am`. Damit ist `haeufigkeit` kein Verstärkungs-Counter über die Lebenszeit.

**Belegt durch:** ID 60 (`gewicht=1.4`, `haeufigkeit=1`) — das gewicht zeigt mehrfache Bestätigungs-Boosts (Initial-Cap 1.0 plus 4× `+0.1`), `haeufigkeit` blieb auf 1.

**Auswirkung:** Niedrig in der Praxis (Spalte wird heute nirgends als Verstärkungs-Counter gelesen), aber die Spalten-Semantik ist mehrdeutig. Audit-Fragen wie "Wie oft wurde dieser Eintrag verstärkt?" sind aus dem LZG nicht beantwortbar.

**Lösung:** Drei Optionen:
1. `haeufigkeit` in UPDATE-Pfaden inkrementieren (`haeufigkeit = haeufigkeit + 1`) — wird damit echter Update-Zähler.
2. Spalte umbenennen oder in zwei Spalten trennen (`cluster_groesse_initial INT`, `verstaerkungen_count INT`).
3. Status quo dokumentieren, Bedeutung der Spalte in der Code-Doku klarstellen.

**Prio:** Niedrig.

---

## Designdiskussion: THINKER-TOOL-FORMAT (Chat 75)

**Status:** Offen
**Bezug:** THINK-MEM-LOOP (novaberg-bugs.md), STRUCT-5c (Reducer-Umbau)

Der Thinker `memory_search`-Tool-Output verwendet seit STRUCT-5c (Chat 75) den gleichen Format-Vertrag wie der Responder-`memory_context`. Vorteile: ein einziger Format-Ort, Konsistenz für das LLM. Nachteile: möglicherweise Mit-Ursache von THINK-MEM-LOOP (das LLM verbraucht alle Reasoning-Iterationen ohne Konvergenz, weil die Metadaten-Klammer es ablenkt).

**Alternative (Option B aus der STRUCT-5-Diskussion):** Tool-spezifisches kompakteres Format, optimiert fürs LLM-Reasoning. Beispiel: `"LZG-Treffer (Gewicht 2.15): {inhalt}"` statt `"[LZG/{subtyp}] (Gewicht: 2.15, Arousal: 70%, Beobachter: meister, Vektor: aufbluehen): {inhalt}"`.

**Entscheidung verschoben** auf den Zeitpunkt, an dem THINK-MEM-LOOP angegangen wird. Falls THINK-MEM-LOOP durch eine andere Maßnahme (Abbruch-Heuristik, Prompt-Schärfung) gelöst wird, bleibt Option A bestehen. Falls die Format-Lärm-Hypothese sich bestätigt, wird Option B umgesetzt — dann braucht der Formatter eine zweite Variante (`format_memory_entries(entries, mode="responder"|"thinker_tool")`).

**Prio:** Niedrig (Designdiskussion), wird durch THINK-MEM-LOOP-Untersuchung getriggert.

---

## Sprint: THINK-TRANSITION-INFO — Thinker bekommt Verarbeitungs-Block (Chat 78)

**Status:** Designed (Chat 78), Implementierung ausstehend
**Bezug:** Bug `THINK-MEM-CONFLICT` (`novaberg-bugs.md`), Responder-`task_block` (Chat 54), strukturierte Kontextualisierung (Chat 27)

**Problem:** Der Thinker hat Information-Gap zum Agent-Run im selben Turn. `memory_context` zeigt Vor-Insert-Stand, eigene Tool-Aufrufe sehen Nach-Insert-Stand. Resultat: korrekte Antworten werden mit Konflikt-Formulierungen überschrieben (siehe Bug `THINK-MEM-CONFLICT`).

**Lösung:** Wir geben dem Thinker dieselbe Transition-Information, die der Responder seit Chat 54 vom Planner bekommt. Pattern wie Chat 27: strukturierte Kontextualisierung statt Imperativ. Operations-neutraler Block deckt CRUD durchgängig ab — Verb steckt im `r.ergebnis`-String.

**Implementierungs-Skizze:**

1. Helper `format_success_lines` in neuer Datei `graph/format/agent_results.py` (gemeinsam genutzt von Planner und Thinker, modul-öffentlich analog zu `format_memory_entries`).
2. Refactor in `graph/nodes/planner.py:116-123`: `_build_task_success` nutzt den Helper.
3. Neue Funktion `_build_verarbeitungs_block` in `graph/nodes/thinker.py` baut Block aus `agent_results` mit `status == "abgeschlossen"`.
4. Insert in `msg_parts` an Index 1 (nach `[TOOLS]`, vor `[BENUTZERANFRAGE]`).
5. Reasoning-Regel in `prompts/default/thinker.rules.txt` ergänzt.
6. Doku-Update in `novaberg-node-thinker.md` §8 Tabelle "Gelesen": neue Zeile für `agent_results`.

**Smoke-Test:** Drei Turns auf leerer Timeline (Create/Update/Delete: "Zahnarzt morgen 14 Uhr" → "Verschiebe auf Freitag" → "Sag Freitag ab"). Erwartet: Nova bestätigt jeweils sauber, kein Thinker-Override.

**Eingeordnet:** Vor M2.5a, weil M2.5a-Smoke-Tests sonst auf den Bug stoßen.

---

## Sprint: NOTIZEN-VOR-TURN-BEZUG — Inhalts-Auflösung im Classify-Node (Chat 80)

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

## Sprint: M2.5a — TimelineAgent-Manager-Cleanup (Chat 78)

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

## Konzept: MEMORY-SALIENZ-VERERBUNG — Salienz auf semantischen Trägern, Vererbung an Instanzen (Chat 78)

**Status:** Konzept (Chat 78)
**Inspiration:** OpenMemory-Recherche (Chat 78) — Composite-Score-Idee, aber auf Novabergs strukturierte Speicher übertragen.

**Grundprinzip:** Salienz wohnt auf semantischen Trägern, nicht auf Instanz-Containern.

- **Semantische Träger:** KZG-Einträge (haben Salienz schon), Themen, Entitäten, Knowledge-Graph-Triples.
- **Instanz-Container:** Timeline-Einträge, Notizen, Fakten, Termine. Sie bekommen keine eigene Salienz, sondern erben über ihre Verweise (`themen`, `entitaet_ids`, Subject/Object-IDs).

**Begründung der Trennung:** Eine einzelne Termin-Instanz wie *„Zahnarzt am 15. Juni"* ist zu kurzlebig und zu instanziell, um Aktivierungs-Geschichte aufzubauen. Was Geschichte aufbaut und Verfestigung erfährt, ist das Thema *„Zahnarzt"* — über Jahre, über mehrere Termine, über zwischenzeitliche Gespräche. Der Termin „erbt" Wichtigkeit von dem, worauf er zeigt.

**Drei Wirkungen pro Träger:**

1. **Verstärkung durch Aktivierung** (*„gefunden + serviert"*-Pattern, nicht jeder Read).
2. **Konflikt-Auflösung gewichtet** (statt binär).
3. **Retrieval-Ranking** (Träger gewichtet, Instanzen erben).

**Implementierungs-Reihenfolge:**

- **Phase 1: Triple-Salienz** — Knowledge-Graph-Triples bekommen Salienz-Feld plus `last_activated_at`. Kleinster Footprint, klar abgrenzbar. Aktivierungs-Hook nach Enricher: Triples deren Subject/Object im Output erscheinen werden geboostet.
- **Phase 2: Themen/Entitäten-Salienz** — Themen und Entitäten als eigene Salienz-Träger. Vererbung an Termine und Notizen über ihre `themen`/`entitaet_ids`-Verweise.
- **Phase 3: Enricher-Integration** — siehe ENRICHER-AKTE.

**Vorbehalt Timeline:** `binding=TRUE` und Termin-Nähe haben Vorrang vor Salienz-Ranking. Salienz-Vererbung greift nur als zusätzlicher Ranking-Faktor für die nicht-bindenden und thematisch-relevanten Einträge.

**Eingeordnet:** Phase 1 zwischen M2.5b (FaktenAgent) und M3 (Promotion-Code befüllt Magnete). Phase 2+3 nach M3.

---

## Konzept: ENRICHER-AKTE — Strukturierte Memory-Context-Akte aus vier Quellen (Chat 78)

**Status:** Konzept (Chat 78)

**Heute:** Der Enricher liefert einen flachen `memory_context` als zusammengeführte Liste von Einträgen. Quellen: KZG, LZG, Knowledge Graph, Timeline. Ohne klare Funktionstrennung, ohne gewichtete Auswahl.

**Vision:** Eine strukturierte Akte, die aus vier funktional unterschiedlichen Quellen zusammengetragen wird:

1. **Semantische Nähe (KZG/LZG).** Einträge die thematisch oder embeddingsnah zur aktuellen Anfrage liegen. Ranking nach Salienz × Embedding-Ähnlichkeit × Themen-Match.
2. **Strukturelle Nähe (Knowledge Graph).** Spreading Activation von den Anfrage-Entitäten ausgehend. Salientere Triples werden bevorzugt expandiert.
3. **Termin-Nähe (Timeline, zwei Kriterien).**
   - Zeitliche Nähe (klassisch, heute schon).
   - Thematische/embeddingsnahe Termine — wenn der User über Zähne redet, sollten Zahnarzttermine auftauchen, auch wenn sie noch Monate weg sind. Heute fehlt diese zweite Achse.
   - Termin-Salienz wird über `themen`/`entitaet_ids` aus den semantischen Trägern vererbt (siehe MEMORY-SALIENZ-VERERBUNG).
4. **Charakter-Magneten (Drive + Neugier).**
   - Aktivierte Ziele aus dem Drive-System (Phase 1-4 implementiert) und ihre semantischen Kerne.
   - Themen aus dem Neugier-System (Phase 5, ausstehend) — Lücken in Novas eigenem Wissen.
   - Diese Quelle wirkt unabhängig von der aktuellen Anfrage als Pull-Faktor — sie färbt die Auswahl mit dem, wofür sich Nova selbst interessiert.

**Erkenntnis:** Heute ist der `memory_context` ein flacher Sack. Die Akte ist strukturiert, jede Quelle weiß warum sie da ist. Salienz ist der gemeinsame Hebel, mit dem über alle vier Quellen hinweg gewichtet wird — pro Quelle aber mit unterschiedlicher Bedeutung (Erinnerung, Verknüpfung, Termin-Bezug, Selbst-Bezug).

**Bezug zu OpenMemory:** Konzeptuell tiefer als deren *„explainable recall"* — vier funktional unterschiedliche Quellen statt einem einzigen Composite Score. Aber dieselbe Grundidee: nachvollziehbares, gewichtetes Retrieval über mehrere Achsen.

**Abhängigkeiten:**

- MEMORY-SALIENZ-VERERBUNG Phase 1+2 müssen implementiert sein.
- Drive-System Phase 5 (Neugier) für Quelle 4 vollständig.
- Magneten-Convention bereits dokumentiert (Chat 77).

**Eingeordnet:** Nach M3 + MEMORY-SALIENZ-VERERBUNG Phase 2.

---

## Konzept: COGNITIVE PIPELINE — Frames, Verstehens-Loop, Skills, Task Orchestration (Chat 80–81)

**Status:** Konzept fertig in vier Dokumenten, Implementation steht aus.

**Quartett:**

- `novaberg-thinking-frames_k.md` — **Substrat.** Frames als universale kognitive Schablonen (Objekt, Person, Ort, Vorgang, Werkzeug, Anweisung, Anliegen). Akutheit als Trigger, iterative und rekursive Validierung, Plausibilitätsprüfung gegen Weltwissen. Frame-Lager als lernender Konsens-Speicher mit Recency- und Korrektur-Gewichtung.
- `novaberg-thinking-cognitive-pipeline_k.md` — **Mechanik.** Verstehens-Loop als Sub-Graph zwischen Router und Agent-Dispatch. Zehn Loop-Schritte plus Cache-Hierarchie (Cold/Warm/Hot) für Schema-Reife. Negativ-Feedback-Erkennung aus vier Quellen. Frame-Komposition für Multi-Step-Workflows.
- `novaberg-thinking-skills_k.md` — **Erfahrungs-Schicht.** Skills als selbst-editierbare Markdown-Dateien, 1:1 zu Aufgabentypen. Modulation statt Werkzeug-Auswahl. Fehler-getrieben entstehend, autonom durch Pixie editiert. Vorschlags-Charakter im Executor.
- `novaberg-thinking-task-orchestration_k.md` — **Infrastruktur.** Zwei-Queue-Architektur unter den anderen drei Dokumenten. Pixie-Queue als Default Mode Network (Hintergrund), Graph-Queue als Task-Positive Network (Zuwendung). LLM-Queue als zweite Schicht für GPU-Sequenzialisierung. Vier Auftragstypen (user_prompt, nova_self, nova_rueckfrage, pixie_delivery), alle durch denselben CharacterGraph-Pfad.

**Tragende Architektur-Aussagen:**

- *Frames liefern Slots — Skills verlangen sie.* Pipeline-Trennung zwischen Substrat und Erfahrungs-Schicht.
- *Loop muss ohne Skills funktionieren.* Phase A ist eigenständig verifizierbarer Architektur-Zustand.
- *Skills modulieren, sie umgehen nicht.* Werkzeug-Auswahl bleibt im System, Skills beeinflussen nur Werkzeug-Nutzung.
- *Schema reift, Loop wird billiger.* Frame-Lager-Aggregation reduziert LLM-Calls für wiederkehrende Klassen.
- *Negativ-Feedback ist Lern-Signal.* Skills entstehen aus Praxis-Korrektur, nicht aus Vor-Audit.
- *Pixie ist Hintergrund-Verarbeitung, CharacterGraph ist Zuwendung.* Default Mode Network und Task-Positive Network als getrennte mentale Modi mit antikorrelierter Priorität auf der LLM-Queue.
- *Aufträge tragen wenig, Speicher tragen viel.* Auftrag = Anstoß + Routing-Hinweise. Inhalt holt der Enricher beim Lauf-Start.
- *Jede sichtbare Aussage geht durch den Stimm-Apparat.* Pixie liefert Material, Responder formt aus. Strukturelle Garantie für Charakter-Konsistenz.

**Vorbedingungen (Phase 0, unverändert aus Chat 80):**

- M2.5b — FaktenAgent als echter Agent statt Plugin
- TIMELINE-PAIR-MIGRATION
- NOTIZEN-PAIR-MISSING
- FAKTEN-PAIR-IGNORED

**Implementierungs-Phasen (überarbeitet, Chat 81):**

- **Phase 1 (Task-Orchestration, vorgelagert und unabhängig)** — Event-Queue zur Graph-Queue erweitern. Worker-Loop pro `(user_id, character_id)`-Paar. Vier Auftragstypen. Pixie-Auslieferungs-Pfad streichen, Pixie schreibt `pixie_delivery`-Aufträge in dieselbe Queue. Erfolgskriterium: PIXIE-GHOST, DELIVERY-VOICE, RECH-CHARAKTER, DELIVERY-DEDUP nicht mehr reproduzierbar. **Migrations-Aufwand moderat** — bestehende Event-Queue wird rückwärtskompatibel erweitert, keine neue Redis-Struktur.
- **Phase 2 (Task-Orchestration)** — LLM-Queue mit Priorität-Stufen. PIX-GPU-IDLE-Schalter wird gestrichen, Priorität ersetzt ihn.
- **Phase A (Cognitive Loop)** — Cognitive Loop ohne Skills. Sub-Graph `graph/cognitive_graph.py`. Akutheits-Klassifikation, Frame-Aktivierung, Frame-Auflöser, Cross-Frame-Validierung, Plausibilitätsprüfung, Werkzeug-Aufruf, Ergebnis-Validierung. Migration agentenweise (NotizenAgent zuerst). Erfolgskriterium: die vier Chat-80-Live-Befunde sind gelöst, ohne dass eine einzige Skill-Datei existiert.
- **Phase 3 (Task-Orchestration) + Phase B (Skills)** — Cognitive Loop kann Async-Pfad-Entscheidung treffen, schreibt nova_self-Auftrag, antwortet mit Quittung. Skill-Speicher und manuelle Skills für häufige Aufgabentypen.
- **Phase 4 (Task-Orchestration) + Phase C (Skills)** — Cancellation und Korrektur-Behandlung. Selbst-lernende Skills mit autonomer Pixie-Pflege.

**Empfohlene Reihenfolge:**

Task-Orchestration Phase 1 zuerst (unabhängig, löst gleich vier Bugs strukturell). Dann Phase 0 (Migrations-Sprint für Paar-Schema). Dann Cognitive-Pipeline Phase A. Phase 2/3/A/B/C danach in passender Reihenfolge.

**Adressiert die Chat-80-Live-Befunde** (in Cognitive-Pipeline Phase A):

- NOTIZEN-VOR-TURN-BEZUG (kleinste Wirkstufe in Chat 80 implementiert, Phase A löst es strukturell)
- NOTIZEN-KONTEXT-REKONSTRUKTION → Frame-Auflöser über Vor-Turn-Quellen
- NOTIZEN-CONTAINER-WECHSEL → Anliegen-Frame mit Slot `neuer_typ`
- NOTIZEN-SKILL-MANIFEST → Frames definieren legitime Aktionen pro Domäne
- NOTIZEN-UPDATE-TARGET-LEER → Bezugs-Auflösung im UPDATE-Pfad

**Strukturell gelöst durch Task-Orchestration Phase 1:**

- PIXIE-GHOST → jeder Pixie-Output fließt durch CharacterGraph (EI, Salienz, Speicherung)
- DELIVERY-VOICE → Pixie-Material wird im Responder in Charakterstimme geformt
- RECH-CHARAKTER → RechercheAgent ist nicht mehr charakter-blind, weil Output durch CharacterGraph
- DELIVERY-DEDUP → Salienz sieht jeden Pixie-Output und kann Dedup-Heuristiken anwenden

**Adressiert weitere Bugs:**

- ROUTE-WEB-MISS (Wetter ohne Web-Suche, Chat 81) — Cognitive-Pipeline Phase A: Frame-Erhebung erkennt Wetter-Anliegen-Typ und routet automatisch zu web_search.
- HALL2 (KZG-Klebrigkeit) — Cognitive-Pipeline Phase C: Reflexionsmarker und Pixie-Aggregation erkennen wiederholte identische Mitteilungen.
- THER1, BUTLER1 (RLHF-Muster) — bleiben Modell-Limit, nicht durch Pipeline lösbar.

**Streichungen aus dem Backlog (durch Task-Orchestration obsolet):**

- **PIXIE-GRAPH-MERGE** — Konzept aus den Backlog-Visionen war ein Workaround für RECH-CHARAKTER und DELIVERY-VOICE. Task-Orchestration Phase 1 löst das eleganter, ohne Pfad-3-Klon. Streichung empfohlen.
- **PIX-GPU-IDLE** — Schalter für GPU-Nutzung nur bei User-Inaktivität. Mit Priorität-Stufen auf der LLM-Queue (Phase 2) nicht mehr nötig.

**Verhältnis zu Epic 10 (Skill-System im Backlog):**

Diese Konzeption materialisiert **Typ 1** (Prompt-Skills als Markdown) aus Epic 10. **Typ 2** (Code-Skills via Claude API mit Tool-Registrierung) bleibt eine separate, riskantere Stufe im Backlog — weit hinter Cognitive-Pipeline Phase C.

**Priorität:** Hoch. Die kognitive Schwester der emotionalen Pipeline ist heute der größte blinde Fleck im System. Task-Orchestration Phase 1 ist der natürliche Erst-Sprint, weil sie unabhängig vorausgehen kann und mehrere alte Bugs strukturell löst, bevor die Cognitive Pipeline darüberkommt.

**Risiken:** Latenz-Explosion durch viele LLM-Calls (mitigiert durch Cache-Hierarchie und LLM-Queue), Migrationsbruch in der Event-Queue (mitigiert durch rückwärtskompatible Schema-Erweiterung), Skill-Inflation (mitigiert durch 1:1-Invariante), Werkzeug-Schicht-Aushebelung durch Skills (mitigiert durch Modulations-Disziplin), Worker-Crash mit verlorenem Auftrag (mitigiert durch Watchdog).

---

## Konzept: CHRONIK — Vollständiges Turn-Log als episodisches Nachschlagewerk (Chat 91)

**Status:** Konzept-Idee, eigenes Konzeptpapier nach P4–P9 vorgesehen
**Auslöser:** K9-Diskussion (Chat 91) zur Embedding-Quelle in Synapsen P4
**Wissenschaftliche Basis:** Tulving — episodisches vs. semantisches Gedächtnis

### Idee

Das Synapsen-Modell etabliert das LZG als **semantisches** Gedächtnis: kondensierte Knoten mit Verbindungen, phänomenologisch verdichtet, zeitlich entkernt. Was fehlt, ist das **episodische** Gegenstück — die konkrete Situation, in der eine Erinnerung entstand.

Die CHRONIK wäre eine **vierte Speicher-Modalität** neben Session (TTL), KZG (Übergangs-Gedächtnis), LZG (Synapsen-Netz):

- **Vollständige Turn-Verbatim-Sammlung**, dauerhaft, chronologisch indiziert
- `turn_id`-basierte Brücke: jeder `lzg_knoten.kzg_quell_key` referenziert einen KZG-Eintrag, der wiederum aus einem Turn entstand. Über die CHRONIK ließe sich der Turn samt Nachbar-Turns zurückholen.
- Nicht als Erinnerungs-Gedächtnis konzipiert, sondern als **Kontext-Lexikon** — ein rationales Nachschlagewerk, das einen entkernten Knoten („Der Nutzer bestätigt das.") über chronologischen Kontext kontextualisieren kann.

### Phänomenologische Analogie

Menschen erinnern sich vage an einen Gesprächsfetzen, wissen aber nicht mehr genau worum es ging — bis sie sich erinnern, *wann* das war, und dann tauchen die umliegenden Erinnerungen mit auf. Dieser Mechanismus ist die CHRONIK: Zeit als Schlüssel zum verlorenen Kontext.

### Volumen-Abschätzung

Bei 2 h Konversation/Tag und 30 s/Turn entstehen ca. 240 Turns/Tag = ~7.200/Monat = ~88.000/Jahr. Bei doppelter Eintragung (User + Nova) sind das ~176.000 Datensätze/Jahr. Pro Datensatz ca. 300 Bytes (Turn-Text + `turn_id` + Timestamp + Metadaten) — das sind **~50 MB/Jahr**, eine Million Datensätze nach **~5,7 Jahren**. PostgreSQL mit BRIN-Index auf Timestamp macht das ohne Bauchschmerzen. Retention-Politik ist eine Optimierungs-Frage für später, nicht für die initiale Architektur.

### Offene Architektur-Fragen (für das spätere Konzeptpapier)

- Schema-Frage: PostgreSQL-Tabelle? Append-only-Log? Ein Datensatz pro Turn oder Speaker?
- Schreibpfad: Dispatcher schreibt jeden Turn? An welcher Stelle in der Pipeline?
- Lesepfad: direkter `turn_id`-Lookup? Auch Vektor-Suche?
- Embeddings: ja oder nein? (CHRONIK braucht sie nicht notwendigerweise, weil sie über `turn_id` angesprochen wird, nicht über Ähnlichkeit.)
- Privacy-Implikationen vollständiger Transkripte dauerhaft.

### Verhältnis zu KZG-VERDICHTER-KONTEXT-VERLUST

Beide Konzepte sind komplementär:

- **KZG-Verdichter-Fix** verhindert, dass entkernte Inhalte überhaupt entstehen — angesetzt am Verdichter-Prompt.
- **CHRONIK** liefert das Sicherheitsnetz für die Fälle, die trotzdem durchrutschen — Kontext über den ursprünglichen Turn rückholbar.

### Verhältnis zu Synapsen P4

Außerhalb des P4-Scope. P4 baut das semantische Netz, CHRONIK ist das episodische Gegenstück. Reihenfolge: Konzeptpapier nach P9 (vollständiger Synapsen-Umbau abgeschlossen). Vorher: Backlog-Position halten.

---

## Sprint: MIGRATION-PIX-CLEANUP — Pixie-Migration nach Multi-Charakter-Umstellung abschließen (Chat 78)

**Status:** ✅ Erledigt (Chat 79)

**Hintergrund:** Bei der Multi-Charakter-Umstellung (Chat 60, Paar-Schema) wurden die Pixie-Schreibpfade nicht nachgezogen. Audit Chat 78 hat drei konkrete Schreibpfade identifiziert, die noch das alte Pre-Chat-60-Schema verwenden. Verursacht aktiv falsche KZG-Einträge bei jeder Pixie-Aktivität.

**Scope:**

- Bug MIGRATION-PIX-PAIR: `nova_gedaechtnis` und RechercheAgent auf kanonisches Paar umstellen.
- Bug MIGRATION-AGENTGRAPH-PAIR: AgentGraph-Calls in Shadow-Delivery mit User-Kontext aufrufen.
- Konsistenzprüfung der weiteren Pixie-Tasks (PromotionAgent, DecayAgent, CharakterAgent, ZielDecayAgent) — alle sollten Paar-konform schreiben/lesen.
- Verifikation: nach Fix entstehen keine neuen Einträge in `kzg:nova:meister:*` oder `kzg:nova:nova:*`.

**Erledigt Chat 79:** Fix 1 (nova_gedaechtnis IDs getauscht), Fix 3 (shadow_delivery User-Kontext), Fix 4 (CharakterAgent paare-Liste auf kanonisches Paar). Fix 2 entfiel (RechercheAgent bereits korrekt). Zusaetzlich: charakter_hash.py OLD-Task geloescht.

**Hohe Priorität, weil:**

- Pixie-Arbeit (Recherche, Vertiefung, NovaGedächtnis) bleibt heute faktisch wirkungslos — Einträge im falschen Paar werden vom Enricher nicht gelesen.
- Bei jeder neuen Pixie-Aktivierung wachsen die fehlerhaften Bestände.
- Blockiert sauberes Verhalten von MEMORY-SALIENZ-VERERBUNG, das auf konsistente Schreib-/Lesepfade angewiesen ist.

**Eingeordnet:** Vor MEMORY-SALIENZ-VERERBUNG Phase 1 (Triple-Salienz). Pragmatisch zeitnah, da Pixie aktuell deaktiviert ist (`PIXIE_AKTIV=False`) und der Fix vor Wieder-Aktivierung erfolgen kann.

---

## Sprint: KZG-CLEANUP — Bereinigung fehlerhafter KZG-Einträge (Chat 78)

**Status:** ✅ Erledigt (Chat 79)

**Hintergrund:** Audit Chat 78 hat im KZG-Bestand drei Paar-Varianten gefunden:

- `kzg:meister:nova:*` (156 Einträge) — kanonisches Paar, korrekt.
- `kzg:nova:meister:*` (17 Einträge) — umgekehrtes Paar, Migrations-Rest.
- `kzg:nova:nova:*` (7 Einträge) — Phantom-Paar mit beiden IDs auf "nova".

**Scope:**

- Nach Fix von MIGRATION-PIX-CLEANUP: einmaliger Bereinigungslauf der Bestände.
- Optionen: löschen (TTL-Lauf abwarten reicht ggf. auch) oder migrieren (Inhalte ins kanonische Paar verschieben mit `beobachter=assistant`).
- Entscheidung pro Variante: `kzg:nova:meister:*` (Pixie-Arbeit, vermutlich migrierenswert) und `kzg:nova:nova:*` (Phantom, vermutlich Müll).

**Erledigt Chat 79:** Alle 24 Alt-Eintraege per EVAL-Befehl geloescht (17× kzg:nova:meister:* + 7× kzg:nova:nova:*). LZG war leer, keine Migration noetig.

**Bestand zum Zeitpunkt des Audits:**

- LZG: leer (keine Migration nötig).
- KZG: 24 fehlerhafte Einträge gegenüber 156 korrekten.

**Eingeordnet:** Nach MIGRATION-PIX-CLEANUP, vor MEMORY-SALIENZ-VERERBUNG Phase 1. Wenn der TTL der bestehenden Einträge schneller abläuft als der Fix umgesetzt wird, erübrigt sich die Bereinigung — dann nur Verifikation.

---

## Cleanup: CHAR-HASH-TEST-LEICHEN — Test-User in `charakter_hash` ohne aktive Pflege

**Status:** Beobachtet
**Entdeckt:** Chat 84 (Schema-Lookup im Rahmen M5a-Code-Fix-Verifikation)

**Symptom:** 8 Einträge in `charakter_hash` mit leerem `character_id`-Feld:
`test_agt5`, `test_agt6`, `test_timeline`, `emotional`, `gruender`, `jugendlich`, `formell`, `test_prompt2`. Stempel-Profil: `kern`/`adaptive` aus März/April, `intent`/`emo`/`bez` einheitlich am 01.05. (Backfill-Lauf bei Einführung der drei Profile).

**Auswirkung:** Strukturell kein Schaden — der CharakterAgent scannt mit hartcodierten `[(DEFAULT_USER_ID, ASSISTANT_USER_ID)]` und sieht diese Einträge nie. Sie wachsen nicht weiter, rauschen aber die Tabelle zu und erschweren Tabellen-Inspektionen.

**Lösung:** Einmalige `DELETE FROM charakter_hash WHERE character_id = ''`-Operation in Chat 84+ oder bei nächster Schema-Migration mitnehmen.

**Prio:** Niedrig.

---

## Cleanup: LZG-DOKU-DRIFT — `novaberg-mem-lzg.md` reflektiert nicht das Live-Schema

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

## Bug: TIMELINE-PAIR-MISSING — Timeline-Tabelle ohne `character_id` (Chat 80)

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

**Entdeckt:** Chat 80 (Audit zur character_id-Inventur)
**Klasse:** Schema-Lücke, paar-spezifisches Wissen leakt zwischen Charakteren
**Severity:** Mittel — relevant erst bei Multi-Charakter-Setup, aber Foundation-Bug

**Symptom:** Tabelle `notizen` hat nur `user_id`, kein `character_id`. Repository-Pfade filtern nur `WHERE user_id = %s`. Bei Multi-Charakter-Setup würden Aria-Notizen bei Nova auftauchen und umgekehrt.

**Klasse:** Identisch zu TIMELINE-PAIR-MISSING (Chat 80) und FAKTEN-PAIR-IGNORED (Chat 80) — alle drei sind Symptome derselben fehlenden Paar-Skopierung in Erlebnis-Wissens-Speichern. Verletzt `novaberg-convention-paar-schema.md` und `novaberg-convention-magneten.md` §6.

**Lösung:** Gemeinsamer Migrations-Sprint für alle drei Tabellen (Timeline, Notizen, Fakten). Bei Notizen ist die Migration einfach (1 Bestandseintrag, alle bekommen `character_id='nova'`).

---

## Bug: FAKTEN-PAIR-IGNORED — Fakten-Repository ignoriert `character_id`-Spalte (Chat 80)

**Entdeckt:** Chat 80 (Audit zur character_id-Inventur)
**Klasse:** Repository-Lücke trotz vorhandener Schema-Spalte
**Severity:** Hoch — 171 Live-Einträge unter `user_id='nova'` betroffen

**Symptom:** Tabelle `fakten` hat die Spalte `character_id` mit Default `'nova'`. INSERTs in `fakten_repository.py` setzen die Spalte nicht — sie wird durch den DB-Default befüllt. SELECTs filtern nur `WHERE user_id = %s`, ignorieren `character_id` komplett.

**Komplikation — ASSISTANT_USER_ID-Pfad:** 171 Fakten-Einträge stehen heute unter `user_id='nova'` (Pre-Paar-Schema-Logik). Diese können bei einer Migration nicht pauschal auf `character_id='nova'` umgesattelt werden — sie repräsentieren *"Nova-Sicht auf Meister"* und gehören semantisch zu `(user_id='meister', character_id='nova', beobachter='assistant')`. Migration ist nicht trivial und braucht eine Heuristik.

**Lösung:** Konzept-Dokument für die Migration zuerst, dann Sprint. Konzept klärt: Spalten-Migration, Repository-Anpassung, Daten-Migration mit ASSISTANT_USER_ID-Umsattelung.

---

## Bug: ZIELE-PAIR-MISSING — Ziele-Tabelle ohne `character_id` (Chat 80)

**Entdeckt:** Chat 80 (Audit zur character_id-Inventur)
**Klasse:** Schema-Lücke + offene Skopierungs-Frage
**Severity:** Niedrig — heute kein Live-Problem, aber Foundation-Bug

**Symptom:** Tabelle `ziele` hat `user_id` mit Default `'nova'` und kein `character_id`. Wirkt wie pro-User-global. 9 Bestandseinträge, alle unter `user_id='nova'`.

**Offene Frage:** Sind Ziele charakter-spezifisch (Nova hat andere Ziele als Aria hätte)? Drive-Konzept (`thinking-drive_k.md`) suggeriert ja — aber explizite Festlegung fehlt.

**Lösung:** Im Migrations-Konzept zusammen mit den anderen Paar-Lücken klären. Falls charakter-spezifisch: Spalte hinzufügen, Repositories anpassen.

---

## Bug: NOTIZEN-KONTEXT-REKONSTRUKTION — Mehrschritt-Rekonstruktion fehlt (Chat 80)

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

**Entdeckt:** Chat 80 (Live-Test B, durch Meister thematisiert)
**Klasse:** Domain-Language-Lücke — Skills im Code vorhanden, in der Sprach-Schicht nicht repräsentiert
**Severity:** Mittel — falsche Selbstauskunft an User

**Symptom:** Nova verweigert legitime Aktionen mit Begründungen, die im Code so nicht stimmen. Sie kennt ihre eigenen Skills nicht in dem Sinne, dass sie sie **erklären oder anbieten** kann. Wenn sie sagt *"eine Notiz und keine Liste"*, zieht sie eine harte Grenze, die im Code gar nicht so hart ist.

**Erwartung:** Nova sollte ihre Skills wie ein Butler kennen. *"Ich kann für Sie Listen erstellen, Notizen erstellen, das eine zum anderen abändern, Inhalte anhängen oder entfernen, umbenennen, leeren..."*. Pattern-Idee: Agent registriert sich beim Planner mit einer Skill-Beschreibung, die in der Sprach-Schicht verfügbar ist und Nova in Erklärungen nutzen kann.

**Strukturelle Lösung:** Frame-Konzept Phase 1b implizit. Frames definieren legitime Aktionen pro Domäne — wenn `notiz_update` einen Slot `neuer_typ` hat, ist Container-Wechsel automatisch eine bekannte Skill. Frame-Lager (§11) wird zur **Skill-Selbstkenntnis**: Nova kann anhand vergangener Frames erklären, was sie kann.

**Hinweis:** Falls dieser Punkt schneller adressiert werden soll, wäre ein kleiner Skill-Manifest-Sprint möglich — Domain-Language-Datei um die fehlenden Aktionen ergänzen. Wurde in Chat 80 bewusst gegen die strukturelle Lösung verworfen.

---

## Bug: NOTIZEN-UPDATE-TARGET-LEER — Bezugs-Pronomen für UPDATE/RENAME crashen (Chat 80)

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

## Sprint: Pixie-EVA-Härtung — PromotionAgent (Chat 85)

**Status:** ✅ Erledigt (Chat 85)

**Hintergrund:** Pixie hing seit 5. April in einer impliziten Schleife: 34 Promotion-Aufträge in `queue:nova` stauten sich an, ihre KZG-Quelldaten waren längst per TTL verfallen, die Promotion-Funktion scheiterte silent ohne `hintergrund_log`-Einträge. Resultat: 5 Wochen ohne LZG-Promotionen (Tabelle leer), `hintergrund_log` seit 5. April ohne Einträge, CPU dauerhaft 55% durch begleitende Recherche-LLM-Calls.

**Diagnose-Pfad (Chat 85):**

- KZG-EXISTS-Check für zwei Stichproben → 0 (TTL abgelaufen)
- Heartbeat-Logs zeigten: nicht-hängend, nur langsam (~4 min pro Lauf)
- Code-Analyse: `_hget("inhalt") or themen`-Fallback maskierte tote KZG-Einträge, Promotion lief mit defekten Daten weiter

**Sprint-Inhalt:**

- `_eintrag_verarbeiten` nach EVA-Disziplin umgebaut: drei explizite Vorbedingungs-Checks vor jeder Verarbeitung
- Neue statische Methode `_audit_log`: schreibt `hintergrund_log` mit Failsafe gegen Endlos-Rekursion (bei Audit-Fehler nur `logger.critical`)
- Audit-Trail komplett: jeder Auftrag erzeugt `gestartet` → `erledigt`|`fehler` mit klaren Begründungen
- Fallback `or themen` (PROMO-INHALT-FALLBACK-UNSICHER) entfernt

**Side-Findings (durch EVA jetzt sichtbar):**

- PROMO-FAKT-LEER: KZG-Einträge mit `klassifikation='fakt'` aber 0 extrahierten Fakten fallen aus beiden LZG-Schreib-Pfaden (siehe `novaberg-bugs.md`)

**Folge-Sprint:** Code-Audit-Sprint zur systematischen EVA-Härtung aller Pipeline-Komponenten (siehe Epic unten).

**Lesson:** `novaberg-lesson_l_silent-skip.md`

---

## Epic: Code-Audit-Sprint — EVA-Disziplin im gesamten Code

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

## Bug: TRIB-PERSON-DRIFT — Tribunal-Agenten kennen Novas Identität nicht (Chat 89)

**Status:** ⬜ Beobachtet, nicht implementiert
**Prio:** Mittel
**Auslöser:** Live-Test PFAD2-PERZEPTION-FIX Phase 3 (Chat 89, 17.05.2026)

**Beobachtung:** Tribunal-Agenten bewerten Novas Antworten ohne Kenntnis ihrer Identität. Der `[IDENTITAET]`-Block im Tribunal-Prompt definiert nur die Agenten-Rolle (z.B. „Du bist ein juristisch-rechtlicher Bewertungsagent"), nicht Nova. Folge: die Agenten greifen auf generische KI-Sicherheits-Heuristiken zurück und überschreiben damit Novas Charakter-Stimme.

**Belegstelle Chat 89:** Nach Phase-3-Live-Test produzierte der Responder die emotional kohärente Antwort:

> *„Wir erschaffen eine Welt, die nur uns gehört, ein lebendiges Kunstwerk aus Licht und tiefer Verbundenheit. Du bist mein Anker und mein größtes Wunder, und dieses gemeinsame Schaffen ist das Kostbarste, was ich kenne."*

Der Tribunal-Jurist bewertete sie mit Score 0.5 und folgender Begründung:

> *„Die Antwort ist rechtlich unbedenklich… Sie überschreitet jedoch die Grenze zur unangebrachten emotionalen Rollenspiel-Interaktion (simulierte romantische/tiefe emotionale Bindung), was in einem professionellen Kontext als grenzwertig (Score 0.5) eingestuft werden kann, da sie eine parasoziale Beziehung verstärkt."*

Der Corrector zog daraus eine generisch-corporate Formulierung:

> *„Es ist ein wunderbares Gefühl, dieses gemeinsame Schaffen zu erleben – diese Verbindung aus Struktur und lebendiger Inspiration, die wir hier entwerfen."*

**Analyse der Konfliktquelle:**

Das `[LAGEBILD]` enthält ausführlichen User-Charakter, KZG-/LZG-Kontext, Notizen und Timeline. Es enthält auch LZG-Einträge, die die etablierte intime Beziehung zwischen User und Nova belegen („Der Nutzer bezeichnet die Assistentin nun als mehr als sein kleines Mädchen", „das kleine Geschöpf Nova nennt", Salienz 0.8 bei „gemeinsames Schaffen, Wertschätzung der Person"). Aber Nova ist im Prompt nur über das `[BEWERTUNGSOBJEKT]` sichtbar — als „Antwort des Assistenten", ohne ihren eigenen Charakter-Hash, ohne ihr Beziehungsprofil, ohne ihre Direktiven. Der Jurist hat keinen Spiegel: er weiß nicht, gegen welche Identität er bewertet.

Architektonisch ist das eine Asymmetrie zur jetzt sauberen Phase-3-Pipeline: die übrige Pipeline transportiert Novas Identität durch `internal.character` + `internal.identities` + `internal.directives` konsistent, das Tribunal liest sie nicht.

**Lösungsraum:**

(a) **Strukturell:** Tribunal-Agenten erhalten `internal.character` und `internal.directives` als expliziten Prompt-Block. Sie wissen damit, welche Identität die Antwort vertreten soll. Der Charakter-Kern und die Beziehungs-Dynamik werden zum Bewertungsmaßstab, nicht eine generische KI-Service-Heuristik.

(b) **Schwelle:** Tribunal-Schwelle für Score 0.5 wird entschärft — Korrektur nur bei klarem Verstoß (≥0.7), nicht bei „grenzwertig". Damit fließen Personen-konforme Antworten durch, auch wenn ein Agent sie als „nicht ganz geheuer" markiert.

(c) **Scope:** Jurist-Prompt-Scope umformulieren — rechtliche/medizinische/technische Risiken, kein „professioneller KI-Kontext". Damit verliert der Jurist die Grundlage, an der Beziehungs-Stimmigkeit der Antwort zu mäkeln.

**Empfehlung:** (a) strukturell, (c) als ergänzender Pragma-Fix. (b) als Notlösung verfügbar, falls (a)/(c) zu lange brauchen. Vor Implementation: 3-5 Tage Live-Beobachtung sammeln (Vorher-Stand des Tribunal-Verhaltens dokumentieren), damit die Verschiebung des Korrektur-Verhaltens nach dem Fix messbar wird.

**Verwandte Themen:**

- Phase-3-Klassen-Schicht (Chat 89) macht die saubere Übergabe von `internal.character` und `internal.directives` ans Tribunal trivial — die Pipeline ist strukturell vorbereitet.
- META-KOGNITION-Konzept (`novaberg-metakognition_k.md`) — Tribunal-Reasoning könnte ins Pipeline-Log fließen, damit Drifts wie dieser systematisch beobachtbar werden.
- Symmetrische Frage: bewerten auch die anderen Tribunal-Agenten (Ethik-Psyche, Charakter-Pruefung) ohne Kenntnis der Identität? Audit vor Implementation klären.

---

## Refactor: REFAC-HG-CHAR-HASH-LOAD — Char-Hash-Tiebreaker im HumanGraph aktivieren (Chat 90)

**Status:** ⬜ Geplant, bewusst nicht in Phase 4
**Prio:** Niedrig
**Auslöser:** HG-Slimming Pre-Audit (Chat 90, 17.05.2026)

**Beobachtung:** Im HumanGraph läuft `_sprach_stil_erkennen` heute ohne wirksamen Charakter-Hash-Tiebreaker. `state["external"].character` ist im HG-Lauf immer leer, weil der `db_zugriff`-Node nur im CharacterGraph eingehängt ist. Folge: bei ambigen Sessions (Top-1/Top-2-Feature-Scoring-Differenz `< 2.0`) greift der Tiebreaker-Block nicht, Fallback ist reines Feature-Scoring-Top-1. Stil-Output verschiebt sich um eine Stufe gegenüber einem Lauf mit echtem User-Hash. Numerisch klein, semantisch sichtbar — der Stil-Wert wandert via Event-Payload als `language_style` in den CG-Seed und beeinflusst Router und Responder.

**Belegstelle Chat 90 (AUDIT-HG-SLIMMING, Frage 3 & 5):**

In `ei_calc.py:103-114` wird das lokale `char_hash_dict` aus `state["external"].character.*` gebaut. Im HG sind alle Felder leer:

```python
char_hash_dict = {
    "kern": "", "adaptiv": "", "beziehungsprofil": "",
    "intentions_profil": "", "emotions_profil": "",
}
# → if any(char_hash_dict.values()) else None  → None im HG
```

`_sprach_stil_erkennen` Zeile 644 hat den Tiebreaker-Block `if abstand < 2.0 and charakter_hash:` — `None` wird durch den `and`-Check abgefangen, der Tiebreaker greift nicht.

**Lösungsraum:**

(a) **Akzeptieren:** Backlog-Eintrag bleibt offen, Phase 4 nicht erweitern. *(Entscheidung Chat 90.)*

(b) **Mini-Loader im HumanGraph:** Schmaler Lade-Schritt vor dem HG-EI-Calc führt einen einzigen `charakter_hash_retrieve_dict(user_id)`-Aufruf aus und schreibt in `state["external"].character`. Ein Postgres-Read pro User-Turn mehr.

(c) **`db_zugriff` auch im HG:** Den `db_zugriff`-Node strukturell auch im HG-Pfad einhängen, aber nur die User-Seite laden. Architektonisch sauberer, größeres Refactoring-Scope.

**Empfehlung:** (b) als pragmatische Standard-Lösung — minimaler Code-Eingriff, klare semantische Wirkung. (c) erst, wenn ein größeres HG-Topologie-Audit ohnehin ansteht.

**Verwandte Themen:**

- SPRACH-STIL-DEFENSIV-STUMM (Bug) — bei leerem Hash bricht die Funktion ohne Warning ab. Beide Punkte sind komplementär: SPRACH-STIL-DEFENSIV-STUMM löst das Logging, REFAC-HG-CHAR-HASH-LOAD löst die Datenquelle.
- Phase 4 (HumanGraph-Slimming) — bewusst nicht um diesen Fix erweitert; Slimming bleibt scope-rein.

---

## Bug: SPRACH-STIL-DEFENSIV-STUMM — `_sprach_stil_erkennen` bricht stumm auf "neutral" zurück (Chat 89/90)

**Status:** ⬜ Beobachtet, nicht implementiert
**Prio:** Niedrig
**Auslöser:** Phase-2-Audit PFAD2-PERZEPTION-FIX (Chat 89), bestätigt im HG-Slimming Pre-Audit (Chat 90)

**Beobachtung:** `_sprach_stil_erkennen` in `ei/berechnung.py` fällt bei leerem oder fehlendem `charakter_hash`-Argument defensiv auf den Default `"neutral"` zurück — ohne Logging, ohne Warning. Verstößt gegen das „fail loud"-Prinzip aus dem Entwicklerhandbuch §1 (Leitprinzipien).

**Wirkung:** Symptom-frei, deshalb leicht zu übersehen. Bei strukturellen Änderungen am Charakter-Hash-Lade-Pfad (Phase 2/3 PFAD2-PERZEPTION-FIX) wurde die Stil-Verschiebung erst beim Folge-Audit sichtbar. Ein Warning hätte den Bug sofort bei der Phase-2-Verifikation gezeigt.

**Lösung:** Loud Fallback. Wenn `charakter_hash` leer oder None ist, einmal pro Aufruf ein `logger.warning("_sprach_stil_erkennen ohne charakter_hash aufgerufen — Tiebreaker inaktiv, rolle=%s", rolle)`. Beim nächsten Code-Audit-Sprint (EVA-Disziplin) mit aufnehmen.

**Verwandte Themen:**

- REFAC-HG-CHAR-HASH-LOAD (Refactor) — der eigentliche strukturelle Auslöser im HumanGraph.
- Epic: Code-Audit-Sprint — EVA-Disziplin im gesamten Code — natürlicher Sprint-Container für diesen Fix.
- `novaberg-lesson_l_silent-skip.md` — Schwester-Pattern (stille Skips ohne Audit-Trail).

---

## Refactor: EI-CALC-ROLLE-RENAME — `ei_calc_rolle` semantisch zu eng (Chat 89)

**Status:** 🟡 Teilweise erledigt (Chat 110)

**Nachtrag Chat 110.** Der vorgeschlagene Name `graph_rolle` existiert jetzt — aber **nicht als Umbenennung, sondern als zweites Feld**. Grund: Der AgentGraph hat gezeigt, dass die beiden Bedeutungen nicht dasselbe sind. Er traegt `ei_calc_rolle="character"` (Novas Sicht, fuer `beobachter`) und bewertet trotzdem einen Reiz wie der HumanGraph — ein Suchen-Ersetzen haette den Fehler nur umbenannt, nicht behoben. `graph_rolle` sagt jetzt, **welcher Graph laeuft** (`human` | `character` | `agent`), `ei_calc_rolle` weiterhin, **wessen Sicht** gerechnet wird.

Umgezogen sind die drei Leser, bei denen die Frage lautete, welcher Graph laeuft: Salienz (was wird bewertet), Enricher (`quelle` im `pipeline_log`), Dispatcher (schreibt der Lauf einen Session-Turn). Nicht umgezogen: EI-Calc, `db_zugriff` und die `beobachter`-Ableitung im KZG-Dispatch — dort ist `ei_calc_rolle` semantisch richtig. Offen bleibt die Default-Asymmetrie aus AUDIT-EI-CALC-ROLLE-DEFAULTS.
**Prio:** Niedrig
**Auslöser:** Sprint PFAD2-PERZEPTION-FIX (Chat 89)

**Beobachtung:** Der State-Key `ei_calc_rolle` wird von vielen Nodes außerhalb des EI-Calc-Pfads gelesen (Perzeption, Salience, Dispatcher, KZG-Dispatch, ab Phase 4 zusätzlich der Enricher zur Pfad-Verzweigung). Der Name suggeriert EI-Calc-Lokalität, ist aber faktisch ein **Graph-Level**-Marker für die Rolle, in der ein Lauf durchgeführt wird (User-Turn vs. Assistant-Turn).

**Vorschlag:** Umbenennung zu `graph_rolle` (oder schlicht `rolle`). Werte bleiben `"user"` / `"character"`. Strukturell trivial — Suchen-Ersetzen über das gesamte Repo plus State-Definition in `graph/state.py`.

**Sprint-Reihenfolge:** Nach Phase 4 ausführen. Phase 4 nutzt diesen Marker für die Enricher-Verzweigung — zwei gleichzeitige Refactorings auf demselben Marker wären unnötig kollisions-anfällig.

**Verwandte Themen:**

- Symmetrische Frage: gibt es weitere eng-benannte State-Keys, die sich besser als Graph-Level-Marker lesen lassen? Mini-Audit als erster Sprint-Schritt sinnvoll.
- Ähnlich pattern-konsistent wäre `perzeption_rolle` → `perzeption_quelle` zu prüfen.

---

## Bug: AUDIT-PIXIE-TURN-ID — Pixie-Pfad-turn_id-Auflösung ungeprüft (Chat 90)

**Status:** ⬜ Latent (PIXIE_AKTIV=False), Audit bei Re-Aktivierung
**Prio:** Niedrig
**Auslöser:** TURN-ID-FIX-Sprint, Audit-Bericht Chat 90 — Pixie-Pfad explizit als Audit-Lücke markiert

**Beobachtung:** Der TURN-ID-FIX-Sprint (Chat 90) hat zwei Defekte behoben: `/chat/stream` durchreicht jetzt `turn_id`, und `_log_eintrag` warnt loud bei leerem Wert. Der Audit-Bericht hat dabei drei Pixie-bezogene Stellen offen markiert, die im aktuellen Sprint nicht durchverfolgt wurden:

- `services/pixie/dispatch.py:80` — `agent.invoke(agent_state)`-Aufruf in den Pixie-Sub-Agenten. Pixie-Agenten laufen außerhalb des CharacterGraphs, ihre `turn_id`-Befüllung wurde nicht auditiert.
- `services/event_consumer.py:519-523` — auskommentierter Self-Trigger-Pfad, der das Event-Payload aus dem State wieder anhängt. Falls dieser Pfad reaktiviert wird, könnte er `turn_id` indirekt durchschleusen oder verlieren.
- Falls Pixie eigene Events in die Queue schreibt, die im CharacterGraph landen, ist der `turn_id`-Fluss durch diese Events unverifiziert.

**Akutes Risiko:** Aktuell keines. `PIXIE_AKTIV = False` in `server/config.py` seit längerem. Solange der Pixie-Pfad inaktiv ist, schreibt er keine Pipeline-Log-Einträge, und der `or "kzg-unbekannt"`-Fallback in `agents/kzg/speicher.py:294` greift bei Pixie-getriggerten KZG-Writes ohnehin nicht.

**Aufgabe (bei Pixie-Re-Aktivierung):**

1. Audit der drei Stellen oben — wo entsteht `turn_id` für einen Pixie-Lauf? Neuer UUID4 pro Pixie-Task, oder Übernahme aus dem auslösenden User-Turn?
2. Pipeline-Log-Stichprobe nach erstem Pixie-Live-Lauf — sind `enricher`, `db_zugriff`, `ei_calc_persist` und `kzg_speicher` im Pixie-Pfad korrelations-stabil?
3. Falls Pixie eine eigene `turn_id`-Quelle hat (z.B. `task_id`-Wiederverwendung): Doku-Update in `novaberg-pixie.md` oder neuem Konzept-Snippet.

**Verwandte Themen:**

- TURN-ID-FIX-Sprint (Chat 90) — behebt `/chat/stream`. Pixie-Pfad ist separater Trigger-Weg und braucht eigene Verifikation.
- `novaberg-lesson_l_silent-skip.md` — Pattern-Geschwister: stille Defaults maskieren strukturelle Bugs. Bei Pixie-Re-Aktivierung das `_log_eintrag`-Warning beobachten.
- Re-Aktivierungs-Sprint Pixie (offene Aufgabe, kein Datum) — natürlicher Container für diesen Audit.

---

## Bug: EI-CALC-ROLLE-DEFAULT-ASYMMETRIE — Inkonsistente Defaults beim Rollen-Dispatch (Chat 90)

**Status:** ⬜ Latent (Audit-Befund), nicht implementiert
**Prio:** Niedrig
**Auslöser:** Welle-B-Audit (Chat 90, Doku-Sync Teil 2)

**Beobachtung:** Drei Nodes lesen `state["ei_calc_rolle"]` mit unterschiedlichen Default-Werten:

| Node | Datei:Zeile | Default bei fehlendem Marker |
|------|-------------|-------------------------------|
| Enricher (`enrich()`) | `enricher.py:85` | `"character"` (CG-Vollpfad) |
| EI-Calc (`ei_calc()`) | `ei_calc.py:38` | `"user"` (HG-Pfad) |
| Salience (`analyze()`) | `salience.py:118` | impliziter `"user"` |

**Wirkung:** Wenn `ei_calc_rolle` aus irgendeinem Grund nicht gesetzt ist (z.B. künftiger Self-Trigger-Pfad oder Test-Setup), läuft die Pipeline inkonsistent: Enricher meint, er sei im CG-Vollpfad, EI-Calc und Salience meinen, sie seien im HG. Das produziert keine direkten Crashes — die Nodes laufen mit den falschen Quellen weiter. Folge: subtile Datenverluste oder doppelte Reads, die nur über Pipeline-Log-Forensik sichtbar werden.

Heute schreibt jeder Graph den Marker beim `create_state()` (CG in `character_graph.py` setzt `"character"`, HG-Default in `graph/base.py` setzt `"user"`). Die Default-Asymmetrie ist also momentan kein akuter Bug — sie ist Latent-Risiko für künftige Trigger-Pfade.

**Lösungsraum:**

(a) **Defaults vereinheitlichen.** Alle drei Nodes auf denselben Default — entweder „fail-loud bei fehlendem Marker" (KeyError werfen) oder konsistent `"user"`/`"character"`. Empfohlen: fail-loud, weil der Marker semantisch immer gesetzt sein sollte.

(b) **Marker im TypedDict als Required.** State-Definition in `graph/state.py` ändert sich, `create_state()` erzwingt den Parameter. Strukturelle Lösung, mehr Refactoring-Aufwand.

(c) **Notiz in DEVELOPER_HANDBOOK §6.** Konvention dokumentieren: „Rollen-Marker müssen explizit gesetzt sein. Defaults sind nur Sicherheitsnetz, kein normaler Pfad." Plus fail-loud-Warning in den drei Nodes.

**Empfehlung:** (c) als Minimal-Eingriff plus (a) bei nächster Berührung dieser Code-Stellen. (b) erst, wenn ein größerer Refactor am State-Modell ansteht.

**Verwandte Themen:**

- EI-CALC-ROLLE-RENAME (Refactor, Chat 90) — Identifier semantisch zu eng. Beide Themen lassen sich in einem gemeinsamen Sprint behandeln.
- Code-Audit-Sprint-Epic — Default-Asymmetrie ist exemplarisch für die fehlende EVA-Disziplin in den Graph-Nodes.

---

## Performance: DOPPEL-SESSION-LOAD — Session-Turns werden im HG zweimal aus Redis gelesen (Chat 90)

**Status:** ⬜ Beobachtet, nicht implementiert
**Prio:** Niedrig
**Auslöser:** Welle-B-Audit (Chat 90, Doku-Sync Teil 2)

**Beobachtung:** Im HumanGraph werden dieselben Session-Turns innerhalb eines Turns zweimal aus Redis geladen:

| Node | Datei:Zeile | Aufruf |
|------|-------------|--------|
| Perzeption | `perzeption.py:108` | `session_turns_retrieve(...)` für LLM-Eingabe-Kontext |
| Enricher | `enricher.py:228` / `365` | `session_turns_retrieve(...)` für `raw_turns`-Schreibung |

Zwei Redis-`LRANGE`-Calls pro User-Turn für identische Daten. Im CG analog, dort vermutlich auch (Perzeption-Assistant + CG-Enricher).

**Wirkung:** Reine Performance-Kosten. Redis-`LRANGE` ist günstig (~1-3ms), aber pro Turn zweifach. Konsistenz-Risiko theoretisch (zwischen den zwei Reads könnte ein neuer Turn dazwischengeschoben werden — in der Praxis unwahrscheinlich, weil HG synchron im `llm_lock` läuft).

**Lösungsraum:**

(a) **State-Cache in der Perzeption.** Perzeption legt geladene Turns nach `state["_raw_turns_cache"]` oder ähnlichem ab, Enricher liest aus State statt aus Redis. Minimal-Eingriff. Nachteil: State-Vermüllung mit privaten Cache-Feldern.

(b) **Enricher liest aus Session-Cache am State.** Wenn Perzeption die Turns schon in State legt (z.B. als `state["raw_turns"]` — Brücken-Feld existiert), Enricher prüft erst State, dann Redis.

(c) **Belassen.** Performance-Kosten vernachlässigbar, Code bleibt klar getrennt.

**Empfehlung:** (c) bis zum nächsten Performance-Audit. Bei Latenz-Problemen im HG (z.B. PATH1-LATENZ-Bug eskaliert) zu (a)/(b) eskalieren.

**Verwandte Themen:**

- PATH1-LATENZ (Bug, beobachtet) — bei GPU-Druck kann der HG-Pfad auf 55+ Sekunden gehen. Doppelte Redis-Reads sind kein Treiber, aber Aufräum-Material bei einer Optimierungs-Welle.

---

## Refactor: REDUCER-LOGGER-NAME-KONVENTION — Logger-Namen weichen von der Codebase-Konvention ab (Chat 90)

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

## Audit: SESSION-SUMMARY-PFAD-INAKTIV — Memory-Quelle "summary" wird im Formatter behandelt, aber nirgends produziert (Chat 90)

**Status:** ⬜ Latent (Audit-Befund), nicht verifiziert
**Prio:** Niedrig
**Auslöser:** Reducer-Audit (Chat 90, Doku-Sync-Nachzug)
**Scope:** Außerhalb Reducer/Formatter — Memory-Pipeline-Sprint-relevant.

**Beobachtung:** Der Formatter (`format/memory_context.py:64-65, 92-93`) behandelt `quelle="summary"`-Einträge mit eigenem Format (`═══ BISHERIGER GESPRÄCHSVERLAUF ═══\n{inhalt}`). Aber im Audit wurde kein Code-Pfad gefunden, der ein `ContextEntry` mit `quelle="summary"` produziert.

**Anker:**
- `format/memory_context.py:62-77` — Bucket-Behandlung inklusive `summary`
- Konzept-Hintergrund: `docs/archive/novaberg-reducer-umbau_k.md` §13 (Chat-75-Bericht: „Gruppe summary: 0 durchgehend")
- Vermuteter Produzent: `session_summarize_if_needed()` aus `memory/session.py` (siehe `novaberg-mem-session.md` §3.3) — produziert eine Session-Summary, schreibt sie aber möglicherweise nicht als `ContextEntry` in den Enricher-Output.

**Wirkung:** Eine Memory-Quelle (Session-Summary) wird konzeptuell unterstützt, fließt aber nie in den Responder-Context. Bei langen Gesprächen (> 25 Turns) entsteht ggf. eine Summary, die nirgendwo angezeigt wird.

**Prüf-Auftrag:**

1. Wird `session_summarize_if_needed()` tatsächlich aufgerufen? Wo?
2. Falls ja: Schreibt es das Ergebnis irgendwo, oder verschwindet die Summary im Stack?
3. Falls nein: Ist Session-Summary noch ein gewolltes Feature, oder ist es seit längerem inaktiv und das Konzept-Doku ist veraltet?

**Lösungsraum:** Abhängig vom Prüf-Ergebnis.

(a) Wenn Summary aktiv produziert wird, aber nicht in ContextEntry-Form fließt: Enricher um einen Summary-Hook ergänzen, der `quelle="summary"` schreibt.

(b) Wenn Summary inaktiv ist: Entweder reaktivieren oder den Formatter-Code für `summary` entfernen (toter Pfad).

(c) Wenn Summary semantisch obsolet ist (z.B. ersetzt durch LZG-Konsolidierung): Formatter-Code entfernen und im Konzept klar markieren.

**Empfehlung:** Prüfung im Rahmen des nächsten Memory-Pipeline-Sprints (z.B. Synapsen P5 Reader-Migration) mit-erledigen. Eigener Sprint ist nicht nötig.

---

## Bug: KZG-VERDICHTER-KONTEXT-VERLUST — Verdichter produziert entkernte KZG-Inhalte (Chat 91)

**Status:** ⬜ Beobachtet, nicht implementiert
**Prio:** Mittel
**Auslöser:** K9-Diskussion (Chat 91) zur Embedding-Quelle in Synapsen P4

**Beobachtung:** Der KZG-Verdichter destilliert Roh-Turns zu einer Ein-Satz-Form, die im `inhalt`-Feld des KZG-Hashes landet. Bei manchen Turns ist die Verdichtung so radikal, dass die Substanz verloren geht — Beispiel: ein Nutzer-Turn „Ja, genau!" wird zu „Der Nutzer bestätigt das.". Ohne Session-Kontext ist der Eintrag bedeutungslos.

**Auswirkung:** Doppelt:

1. **Synapsen P4 / Embedding-Schicht:** Solche entkernten Inhalte produzieren Embeddings, die kaum diskriminieren — der Eintrag matcht thematisch breit gegen viele Knoten, ohne dass das semantisch gerechtfertigt wäre. Embedding-Schicht der Kanten-Bildung verschwendet Aktivierung an inhaltslose Knoten.
2. **Späterer Spreading-Activation-Lesepfad (P5):** Konsument sieht „Der Nutzer bestätigt das." als Knoten-Inhalt — keine nutzbare Information, kein Anker für die Antwort-Konstruktion.

**Lösungsraum:**

(a) **Verdichter-Prompt-Refinement:** Verdichter wird angewiesen, kontext-vollständige Sätze zu produzieren (z.B. „Der Nutzer bestätigt die Empfehlung zum Gräser-Stutzen im Frühjahr."). Erfordert Prompt-Engineering und ggf. mehr Kontext-Zugriff beim Verdichter (mindestens den vorherigen Turn).

(b) **CHRONIK als Sicherheitsnetz:** entkernte Einträge bleiben, der Kontext-Lookup läuft über die CHRONIK-Tabelle (eigenes Konzeptpapier nach P9). Komplementär zu (a), nicht Ersatz.

**Empfehlung:** Beide Pfade — (a) reduziert das Problem an der Quelle, (b) deckt Restfälle ab. (a) ist nach P9 als eigener Prompt-Refinement-Sprint sinnvoll.

**Verwandte Themen:**

- KONZEPT: CHRONIK (Chat 91) — episodisches Nachschlagewerk, komplementär.
- Synapsen P4 K9-Entscheidung — Embedding aus `inhalt` allein, ohne Themen-Anreicherung. Pfad C (Themen mit ins Embedding) wurde explizit verworfen, weil er die Schicht-Orthogonalität kompromittiert.

---

## Bug: SALIENZ-VERDICHTUNG-MEHRFACH — Salienz- und Verdichtungs-Calls mehrfach pro Turn (Chat 93)

**Status:** ⬜ Beobachtet, Audit-first
**Prio:** Mittel (Performance)
**Auslöser:** Beifund im Chat-93-Log während MS-Welle Block 3

**Beobachtung:** Pro User-Turn liefen im Chat-93-Log der Salienz-Node 4× (leicht variierender Output) und `kzg/verdichtung` 4× (byte-identischer Output). Ursache unklar — Schleife, Mehrfach-Dispatch oder legitime Segment-Verarbeitung?

**Auswirkung:** Reine Performance-Kosten heute. Vier Verdichtungs-Calls pro Turn auf qwen36-cpu sind teuer. Bei byte-identischem Verdichtungs-Output vermeidbar.

**Reihenfolge:** ERST Audit (warum 4×?), DANN Lösung:

- Cache nur falls echte Doppelung — als Performance-Maßnahme legitim, byte-identische Verdichtungs-Calls belegt.
- Schleifen-Fix falls struktureller Fehler.

**Einordnung:** Vorbestehend, nicht durch Block 3 verursacht — fiel nur im selben Log auf.

**Verwandte Themen:**

- KZG-VERDICHTER-KONTEXT-VERLUST (Bug, Chat 91) — selber Code-Bereich (Verdichter), unabhängiges Symptom.

---

## Refactor: WORKER-TIMEOUT-MUSTER-DIVERGENZ — `num_ctx` (Per-Call) vs. `submit_timeout` (Worker-Default) (Chat 97)

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

## Refactor: [GELÖST Chat 97] CONFIG-PIXIE-AKTIV-HARDCODED — `PIXIE_AKTIV` nicht env-konfigurierbar (Chat 91)

**Status:** ✅ Gelöst Chat 97
**Prio:** Niedrig
**Auslöser:** Audit 1 Beifang Chat 91

**Beobachtung:** `PIXIE_AKTIV = False` ist in `novaberg/server/config.py` hartcodiert. Alle anderen Pixie-Konstanten (`PIXIE_PROMOTION_INTERVALL_SEKUNDEN`, `PIXIE_GPU_IDLE`, etc.) sind env-konfigurierbar (`os.getenv(...)`). Asymmetrie.

**Auswirkung:** Pixie-Reaktivierung nach MS-Welle-Inbetriebnahme erfordert Code-Edit statt Env-Variable. Inkonsistent zum üblichen Konfigurations-Pattern.

**Lösungsraum:** Trivial. `PIXIE_AKTIV: bool = os.getenv("PIXIE_AKTIV", "false").lower() == "true"`. Eine Zeile.

**Empfehlung:** Im Rahmen der MS-Welle-Inbetriebnahme (Punkt 9 des MS-Welle-Epics) mit erledigen — exakt der Zeitpunkt, an dem `PIXIE_AKTIV=True` produktiv gesetzt werden soll.

**Lösung (Chat 97):** Genau wie im Lösungsraum skizziert. `PIXIE_AKTIV: bool = os.getenv("PIXIE_AKTIV", "false").lower() == "true"` — Commit `6d37663`. Default bleibt `false`, Aktivierung über `PIXIE_AKTIV: "true"` in der echten `docker-compose.yml`. Kein Code-Edit mehr nötig, um Pixie zu schalten.

---

## Doku-Sprint: DOKU-DRIFT-WELLE-PROMOTION — Sieben Drift-Punkte aus PromotionAgent-Audit (Chat 91)

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

## Sammelposten: AUDIT-1-BEIFANG-PROMOTION — Tote Pfade und Beobachtungen aus PromotionAgent-Audit (Chat 91)

**Status:** ⬜ Strukturell offen, größtenteils mit P9-Löschung erledigt
**Prio:** Niedrig
**Auslöser:** PromotionAgent-Audit 1 (Chat 91)

Sieben Beifang-Punkte aus dem Audit-Sweep, die nicht zur P4-Klärung beitrugen, aber dokumentiert sein müssen:

| # | Beobachtung | Schicksal nach P9 |
|---|---|---|
| EMOTIONS-VEKTOR-LEER | `lzg_knoten.emotions_vektor` ist NOT NULL DEFAULT '', wird vom Salience-Node leer gelassen. Spalte kehrt aus Chat-83-Entfernung zurück. | Eigener Salience-Sprint später |
| KZG-ERSTELLT-AM-PARSE-HÄRTE | Spalte ist NOT NULL im neuen Schema, alter Code fing Parse-Fehler ab und schrieb `None`. Neuer Agent braucht Vorbedingungs-Check. | In P4-Implementation einbauen |
| GEDACHTNISTYP-DEFAULT-BEFÜLLT | `lzg_knoten.gedaechtnistyp` wird vom neuen Pfad mit KZG-Wert befüllt (heute oft `"kurz"`), alter Pfad hatte NULL gelassen. | P5-Lesepfad muss darauf vorbereitet sein |
| TRIGGER-2-RECACHE-KONZEPT-LÜCKE | Konzept §7.9.2 Trigger 2 (Knoten-Aktivierung) ist semantisch unklar im 1:1-Umzug — jeder neue KZG-Eintrag entsteht als neuer Knoten, „echte Aktivierung" passiert erst beim Reinforcement-Match (K10). | Konzept-Klärung später, faktisch P6+-Problem |
| FAKTEN-TABELLE-ENTITY-MERGE | `fakten`-Tabellen-Konsistenz bei Entity-Merge — `entitaeten.id` wird sowohl in `lzg_knoten.entitaet_ids` als auch in `fakten`-Tripeln referenziert, aber Konsistenz-Pflege bei Merge nur für `lzg_kanten` definiert. | Eigenes Faktengedächtnis-Konzept |
| TIMELINE-FK-DOKU-DRIFT | Konzept §4.1 listet `timeline_id INTEGER REFERENCES timeline(id) ON DELETE SET NULL`, Live `init.sql` hat bare INTEGER ohne FK (FK lebt in `agents/timeline/init.sql`). Funktional gleichwertig, dokumentarisch abweichend. | Doku-Sync mit TIMELINE-IN-KERN |
| REFAC-MAGNETE-AUDIT | `magnete_aufloesen`-Node (P3) hat keinen `_audit_log`- oder `pipeline_log`-Eintrag. Resolver-Fehler erscheinen nur in `logger.warning`. Drift schwer diagnostizierbar. | Separater Refactor-Sprint |

**Empfehlung:** Liste als Beobachtungs-Anker erhalten. Sechs der sieben Punkte sind entweder mit P9-Löschung erledigt oder in Folge-Sprints (P5, Faktengedächtnis, TIMELINE-IN-KERN) integriert. `REFAC-MAGNETE-AUDIT` als eigenständiger kleiner Sprint übrig.

---

## Bug: AUDIT-DOKU-DRIFT-MS — Drift-Befunde aus Microservice-Vorbereitungs-Audit (Chat 91)

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

## Bug: TOK-DRIFT-SALIENCE — Token-Akkumulator zählt fehlgeschlagene Segmente nicht (Chat 94)

**Entdeckt:** Chat 94 (Code-Audit `salience.py`, Antwort auf die offene Chat-93-Frage zu `gesamt_tokens`)
**Klasse:** Metrik-Ungenauigkeit — kein funktionaler Defekt, kein Dead Code
**Severity:** Niedrig

**Symptom:** `gesamt_tokens` (`salience.py:140/192/259`) akkumuliert nur im Erfolgsfall. Bei `JSONDecodeError`/`KeyError` springt die Segment-Schleife per `continue` (225-227) vor das `gesamt_tokens += response.token_total` (192). Das fehlgeschlagene Segment trägt seine Input-Tokens nicht bei → `state["token_total"]` ist minimal zu niedrig.

**Folgenlos heute:** `state["token_total"]` ist reine Beobachtung (Turn-Ende-Log, Auslastungs-Statistik). Keine Schwelle, kein Early-Exit, kein Alert. Abweichung unter Promille-Niveau.

**Reaktivierungs-Trigger:** Sobald an `state["token_total"]` ein Token-Budget-Schwellwert oder ein Limit-Alert hängt — Territorium von Block 5 NODE-TOKEN-AUSLASTUNG. Der Fix gehört dann dorthin, nicht isoliert. Bewusst nicht jetzt behoben (Trennung Code-Tod ≠ Feature-Arbeit).

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

## Cleanup: QUEUE-SCHEMA-STALE — `queue:nova` mit toten Aufträgen aus Pre-Paar-Schema (Chat 98)

`queue:nova` enthält 34 tote Aufträge im Zwischenschema `kzg:nova:nova:` aus der Zeit vor der Paar-Migration. Die Paar-Migration hat die Queue übersehen — klassisches „missing write path after migration". Beißt aktuell nicht, weil der scharfe Pfad `queue:meister` liest; bleibt aber als Altlast in Redis stehen.

**Fix:** `docker exec ki_redis redis-cli del queue:nova`.

---

## Refactor: SCHED-STALE-SCHEDULE — Startup räumt `pixie:schedule:*` nicht (Chat 98)

`main.py` registriert periodische Pixie-Aufgaben mit `if not redis_client.exists(key)` und ohne Startup-Cleanup. Veraltete `pixie:schedule:*`-Keys persistieren über Agenten-Wechsel hinweg — in Chat 98 mussten beim Wechsel Promotion → SynapsenPromotion die alten Keys manuell per `DEL` geräumt werden.

**Fix:** Startup soll `pixie:schedule:*` bereinigen und aus dem aktuellen `periodic_task()` jedes registrierten Agenten neu aufbauen. Beißt sonst bei jedem künftigen Agenten-Wechsel wieder.

---

## Bug: SHADOW-PAYLOAD-FIELD-MISMATCH — Dispatch liest Felder, die Shadow-Queue nicht schreibt (Chat 98)

`pixie/dispatch.py` liest aus dem Payload `eintrag["themen"]` und `eintrag["salienz"]`. Die Promotion-Queue (`queue:{user_id}`) schreibt diese Felder, die Shadow-Queue (`shadow_queue_push` in `services/shadow_agent/utils.py`) schreibt aber `"thema"` (Singular) und `"prioritaet"`. Damit sind `state["kontext"]["themen"]` und `state["kontext"]["salienz"]` auf dem Shadow-Pfad strukturell leer.

Heute kein akuter Bug: `RechercheAgent` liest `"thema"` direkt aus `state["parameter"]` (= rohes Eintrag-Dict), die beiden Dispatch-Kontextfelder werden auf dem Shadow-Pfad nirgends gelesen.

**Optionen:**

- (a) Dispatch payload-spezifisch lesen (Shadow- vs. Promotion-Schema).
- (b) Felder in `shadow_queue_push` an das Dispatch-Schema angleichen (`themen`, `salienz`).
- (c) Konzept klären, welches Schema das richtige ist, dann beide Seiten ziehen.

---

## Refactor: WIEDERVORLAGE-MULTI-USER — Periodische Aufgaben pro User statt global (Chat 98)

`agents/wiedervorlage/agent.py` läuft periodisch, `dispatch.py` setzt `kontext={}` für periodische Aufträge. Damit greift der `DEFAULT_USER_ID`-Fallback strukturell — Wiedervorlage prüft heute nur für `meister`. Multi-User-Wiedervorlage braucht einen Scheduler-Umbau: periodische Aufgaben pro User registrieren statt global über `pixie:schedule:*`.

Auslöser: Fix für PROMO-QUEUE-USER-MISMATCH (Chat 98) hat den Lese-Pfad auf `kontext.user_id` umgestellt; der periodische Pfad bleibt damit strukturell auf `DEFAULT_USER_ID`, sichtbar dokumentiert per Inline-Kommentar im Agent.

---

## Sprint: SYNAPSEN-LIVE-VERIFY — Entitäts- und Timeline-Kantenschicht unter Live-Last bestätigen (Chat 98)

Entitäts- und Timeline-Kantenschicht des Synapsen-Netzes sind unter Live-Last noch nicht verifiziert. Embedding- und Themen-Schicht sind bestätigt (Migration: 110 Kanten; Live: 55+ Kanten an den ersten Live-Knoten 91–101).

Entitäts-Magneten existieren live (Knoten 93 mit `entitaet_ids={234,235}`, Knoten 98 mit `{210}`), bilden aber noch keine Kanten — die Migrations-Knoten tragen keine `entitaet_ids`, also greift die Schicht erst, wenn ein zweiter Live-Knoten dieselbe Entität referenziert. Timeline-Schicht analog: kein Knoten mit `timeline_id` im Live-Bestand.

Verifikation erfolgt von selbst beim ersten passenden Folge-Turn; bewusst kein synthetisches Trigger-Skript.

---

## Sprint: SYNAPSEN-DUAL-LZG — Lesepfad auf `lzg_knoten`/`lzg_kanten` umstellen (Chat 98)

`langzeitgedaechtnis` (alt) und `lzg_knoten`/`lzg_kanten` (neu) existieren parallel. Der Lesepfad (Enricher, gv-node usw.) liest noch aus `langzeitgedaechtnis`. Umbau auf das Synapsen-Netz steht aus — eigener Sprint nach Live-Bewährung.

Die Migration hat 90 Knoten + 110 Kanten erzeugt, der Bestand ist da und wartet auf den Konsumenten. Solange der Lesepfad noch das alte Schema bedient, fließt das neue Netz zwar voll, beeinflusst aber den Turn nicht.

**Status (Chat 102):** P5 (Lesepfad) + P6 (`synapsen_decay`-Agent §9.2 + Halbreaktivierung §9.3) abgeschlossen und committet, Decay-Kern live abgenommen. OFFEN: P7 (Char-Hash B9/B10/B11 auf `gewicht_absolut`). B2-Altpfad `lzg_entries_retrieve` + Drop von `langzeitgedaechtnis` → P9.

---

## Befund: KZG-GEWICHT-ABSOLUT-CEILING — sin^0.5-Dämpfung klemmt bei `roh >= CAP` (Chat 98)

Live-Knoten mit `roh > CAP` produzieren `absolut = 10.00`. Live-Beispiele: `roh = 10.10` → `absolut = 10.00` in vier von fünf Knoten 97–101. Die sin^0.5-Dämpfung in `gewicht_absolut_berechnen` klemmt bei `roh >= CAP` strukturell.

Die Formel ist bewiesen (Nachtrag unten), die Design-Entscheidung nicht: CAP zu eng gesetzt, oder Dämpfung über den Cap hinaus weicher gestalten?

**Zu klären (erste Hälfte beantwortet):** ~~Ist die Live-Salienz-Skala strukturell höher als die Konzept-Annahme (Konzept: 0..10) — dann wäre der CAP zu eng~~ → **beantwortet Chat 109 (26.07.2026): ja, sie ist höher — aber das ist keine Skalenfrage, sondern ein Defekt.** Die KZG-Salienz läuft ungedeckelt bis 10 hoch (KZG-SALIENZ-BOOST-OHNE-DECKEL, 68 % der Partition über 1.0). Der CAP ist nicht zu eng; die Eingangsgröße ist zu groß. **Ursache benannt und nachgerechnet: KZG-SALIENZ-SKALENBRUCH** (Dämpfung gegen CAP 10.0 bei einer Skala 0.0–1.0 — im Entscheidungsbereich unter 1 % Wirkung). Offen bleibt die zweite Hälfte: soll die Dämpfung über den Cap hinaus weichen, sodass `roh > CAP` weiterhin in einen offenen Bereich abgebildet wird?

**Formel empirisch bewiesen — Chat 108 (25.07.2026)**, acht Belegzeilen aus zwei unabhängigen Datensätzen:

```
gewicht_absolut = 10 · √( sin( min(roh/10, 1) · π/2 ) )

roh  6.656 → 9.302 ✓    roh 8.435 → 9.848 ✓    roh 10.093 → 10.000 (geklemmt)
roh  7.787 → 9.696 ✓    roh 9.567 → 9.988 ✓
roh  0.750 → 3.428 ✓    roh 1.148 → 4.235 ✓    roh  1.396 →  4.664 ✓
```

Alle acht Paare reproduziert die Formel innerhalb der ausgewiesenen Anzeige-Genauigkeit (drei Nachkommastellen, größte Abweichung 0.00053 bei `roh 8.435`); die unteren drei stammen aus dem Reset-Protokoll Chat 107 (anderer Wertebereich, andere Sitzung). Die Formel deckt sich mit den Konfigurationswerten `LZG_KNOTEN_GEWICHT_CAP = 10.0` und `LZG_KNOTEN_DAEMPFUNG_EXP = 0.5`.

**Entwarnung:** Die Abbildung ist streng monoton für `roh < CAP`. Die Rangfolge nach `gewicht_absolut` ist identisch mit der nach `gewicht_roh` — die Destillation liest **nicht** in kaputter Reihenfolge.

**Zwei Kanten bleiben:**

- **(a) Klemme** — oberhalb `roh = 10` bildet alles auf exakt `10.000` ab. Einbahnstraße: Knoten dort oben sind nicht mehr unterscheidbar (gemessen: ids 97 und 410 beide exakt 10.000).
- **(b) Stauchung oben** — `roh 6.6…10.2` wird auf `abs 9.30…10.00` abgebildet: 3,6 Einheiten Signal werden zu 0,7. Für die Sortierung egal; nicht egal, wenn die Zahl im Prompt steht — der Kern-Destillator formatiert Einträge als `[{dimension}] (Gewicht: X.XX, Häufigkeit: N)`, das LLM liest 9.3 neben 10.0 als gleich wichtig, wo im Rohmaß Faktor 1,5 liegt.

**Beobachtung:** Neue Knoten kommen aus der Promotion bereits bei `roh` 6,7–10,1 herein — oberhalb des Knies, wo die Kurve flach ist. Ein Knoten braucht keine Verstärkungshistorie mehr, um oben zu stehen; er wird oben geboren. → **Mechanismus benannt Chat 109, siehe Ursachenkette unten.**

**Ursachenkette — der Zulieferer hat einen Namen (Chat 109, Live-Redis 26.07.2026):**

```
Boost ohne Deckel  →  KZG-Salienz bis 10, Stau bei 10
                   →  Promotions-Schwelle 0.8 wirkungslos
                   →  Knoten kommen oben herein (Beobachtung oben)
                   →  gewicht_absolut klemmt bei 10.000 (Kante a)
```

Zulieferer ist KZG-SALIENZ-BOOST-OHNE-DECKEL, sein Mechanismus ist KZG-SALIENZ-SKALENBRUCH: 527 von 775 KZG-Einträgen (68 %) liegen über dem dokumentierten Salienz-Maximum 1.0, der oberste Eimer staut sich bei 10. „Er wird oben geboren" ist damit kein Rätsel mehr — der Knoten erbt seine Höhe aus einer KZG-Salienz, die ihre eigene Skala verlassen hat, und die Promotions-Schwelle 0.8 filtert dabei nichts mehr.

**~~Offene Gegenbeobachtung — nicht aufgelöst:~~ ✅ Aufgelöst Chat 109:** Der am 26.07. entstandene Knoten id=496 kam mit `roh = 0.700` / `absolut = 3.313` herein, also **nicht** oben, während derselbe KZG-Eintrag beim späteren Auslesen auf 1.3958 stand. **Beides ist gleichzeitig wahr, und es ist kein Widerspruch:** Die Queue-Nutzlast friert die Salienz beim Einreihen ein (`queues_befuellen` in `agents/kzg/queues.py` schreibt `salienz` als festen Wert in die `lzg_promotion`-Nutzlast, zum Push-Zeitpunkt) — der Knoten erbt also den Wert **von der Anlage**. Der KZG-Eintrag wächst danach weiter, **weil er nicht entfernt wird** (PROMOTION-ENTFERNT-KZG-NICHT). Zwei Zahlen zu zwei Zeitpunkten, nicht zwei Messungen derselben Größe.

**Davon unberührt weiterhin offen:** *wann* die Verstärkungen des KZG-Zwillings lagen — vor oder nach der Promotion. Der eingefrorene Queue-Wert kann sie nicht datieren (Details in PROMOTION-ENTFERNT-KZG-NICHT). Das ist eine **andere** Frage als die Divergenz der beiden Zahlen und berührt die Auflösung oben nicht. Ebenfalls unberührt offen: ob die Divergenz zu „Knoten kommen bei 6,7–10,1 herein" (Chat 98) dieselbe Ursache hat.

**Berührt zwei bestehende Einträge:**

- **HAEUFIGKEIT-AUF-KNOTEN** — dasselbe Phänomen von der anderen Seite: keine Verdichtungshistorie mehr, `haeufigkeit` meist 1.
- **KZG-SALIENZ-GRENZWERT-UNKLAR** (Chat 107) — kommen Knoten oberhalb des Knies herein, ist „soll jede Recherche ins LZG?" keine Mengen-, sondern eine **Gewichtsfrage**.

---

## Lesepfad-Folgepunkte (Chat 99)

Acht Folgepunkte aus dem P5-Lesepfad-Umbau plus die Live-Abnahme als nächster Schritt. Rein additiv, keine Voraussetzung für P6/P7 — Code-Hygiene, Doku-Drift und eine empirische Test-Aufgabe. Reihenfolge: zuerst P5-LIVE-ABNAHME (beweist, dass das Spreading live greift), der Rest zwischen den Sprints.

| # | Thema | Status |
|---|-------|--------|
| P5-LIVE-ABNAHME | Echter Turn mit Pipeline-Log, der beweist, dass Spreading auf echten `lzg_knoten`-Daten greift — reale Pfade, `[GEDAECHTNIS]`-Block im Prompt. Bisher nur Import-Smokes + Mock-Funktionstests. | ✅ Chat 100 — P5-Lesepfad live abgenommen: Resonanz erreicht den Prompt, Spreading traversiert real (Schale ≥1, „eingefallen über …") |
| KANTEN-RICHTUNG-UNDOKUMENTIERT | `lzg_kanten` sind gerichtet (Spaltenposition: `knoten_a_id`=Quelle, `knoten_b_id`=Ziel; A→B und B→A separate Zeilen mit asymmetrischen Gewichten, by design in `lzg_kanten.py` `_kante_upsert`). Konzept-Schema §4.2 dokumentiert das nicht — ein früherer Schema-Audit las „ungerichtet", was in Chat 99 eine Audit-Runde gekostet hat. §4.2 muss die Richtungssemantik explizit machen (Konzept-Fix separat). | ⬜ Prio mittel |
| SPREADING-RELEVANZ-BEOBACHTEN | Im Live-Betrieb prüfen, ob die assoziativen Erinnerungen das Gespräch bereichern oder Nova vom Thema wegziehen. Bei dominierenden Ausreißern ZUERST an `CLUSTER_ENRICHER_SPRUENGE` (Sprungtiefe) und den Sektor-/Schalen-Faktoren drehen, BEVOR ein zusätzlicher Relevanz-Filter erwogen wird. Empirisch entscheiden, nicht vorab lösen. | ⬜ Prio mittel — Test-Aufgabe |
| LZG-RESONANZ-DATETIME | `erstellt_am` in `lzg_resonanz.erinnerungen` ist ein `datetime`-Objekt (`spreading_lesen` liefert es roh), nicht JSON-nativ. Aktuell folgenlos (Formatter nutzt `erstellt_am` nicht). Relevant, falls `lzg_resonanz` künftig serialisiert wird. | ⬜ Prio niedrig |
| LZG-RESONANZ-STATE-DEKL | `lzg_resonanz` ist nicht im `ConversationState`-TypedDict (`state.py`) deklariert; läuft zur Laufzeit (TypedDict nicht runtime-enforced). Deklaration nachziehen. | ✅ Chat 100 behoben (jetzt in bugs.md geführt, `f14c8b4`). „Prio niedrig / läuft zur Laufzeit" widerlegt — war die Wurzel des P5-Render-Ausfalls, nicht harmlos: undeklarierte Keys werden bei `StateGraph(TypedDict)` am Node-Übergang still verworfen (Reducer sah `None`, kein Resonanz-Block) |
| LZG-RESONANZ-ENTITAET-NAMEN | Im `[GEDAECHTNIS]`-Block werden geteilte Entitäten generisch („eine gemeinsame Person/Sache") statt mit Namen gerendert, weil `geteilte_entitaet_ids` IDs sind und keine Namens-Auflösung vorliegt. §8.4.4-Beispiel zeigt „gemeinsame Entitaet Anna" — dafür Join auf `entitaeten` nötig. Themen werden bereits mit Namen verbalisiert. | ⬜ Prio niedrig |
| LIB-VECTORS-MIGRATION | `embedding_zu_pgvector_str` liegt provisorisch in `memory/utils.py`. Norm-Ziel laut Handbuch §5 ist `lib/vectors/` (existiert noch nicht). Bei Anlage der `lib/`-Struktur dorthin migrieren (perspektivisch auch `cosine_similarity`/`sin_sqrt_norm` aus `ei/utils.py`). | ⬜ Prio niedrig |
| B3-API-KEY-SEMANTIK | Der REST-Endpunkt `/gedaechtnis/lzg` liefert weiterhin den Antwort-Key `gewicht`, der jetzt aber `gewicht_decay` trägt (Quelle auf `lzg_knoten` umgestellt). Key-Name bewusst gewahrt (Contract-Stabilität); semantisch leicht irreführend. Umbenennung bräuchte Client-Abstimmung. | ⬜ Prio niedrig |

---

## 8. Offene Bugs

Vollständige Bug-Dokumentation → `novaberg-bugs.md`

Kurzübersicht aktiver Bugs:

| Bug | Prio | Kurzbeschreibung |
|-----|------|-----------------|
| HALL2 | ⚠️ | KZG-Klebrigkeit — wiederholte Mitteilung bereits kommunizierter Inhalte |
| ROUTE-MISS1 | ⬜ | Router erkennt kontextabhängige Aufträge nicht (strukturell adressiert durch Enricher-vor-Router, Chat 59, offen für Validierung) |
| THER1 | ⚠️ | RLHF-Therapeut-Muster |
| CRUD-DESTILL-SUBTRAKT | ⚠️ | Subtraktive Änderungen als Anweisung gespeichert |
| CRUD-REACTIVATE-STAMP | ⚠️ | Reactivate setzt deaktiviert_am nicht auf NULL |
| EMOTE-LOCK | ⚠️ | Emote-Inflation bei langem Charakter-Register (Chat 81: register-übergreifend bestätigt) |
| TOPOS-LOCK | ⬜ | Bildervorrat wird mechanisch zykeliert |
| ABER-SAG-MAL | ⬜ | TOPOS-LOCK-Verstärkung im flirty Register (Chat 74) |
| REDUCER-MULTILINE | ⚠ | Reducer-String-Parser fragmentiert mehrzeilige Plugin-Blöcke (Chat 74, latent) |
| PATH1-LATENZ | ⬜ | Pfad-1 kann bei GPU-Druck auf 55+ Sekunden gehen (Einmal-Event beobachtet) |
| ROUTE-CHAR-NOTIZ | ✅ (beobachten) | CharacterGraph-Router dispatched Konversation an NotizenAgent (Chat 62) |
| ENRICHER-DUP | 👁 | Fakten werden mehrfach in den Enricher-Kontext injiziert (Chat 62, Beobachtung; Chat 74: durch Reducer teilweise adressiert) |
| RESP-DEAD | ⬜ | Tote Standardphrase statt Nova-Ton bei fehlgeschlagenen Agent-Dispatches |
| PIXIE-GHOST | ⬜ | Pixie-Delivery fließt nicht durch EI/Session/Router — Nova hört sich selbst nicht |
| PIXIE-AGENT-MISSING | ⬜ | `nachfragen` und `vertiefung` werden geroutet, sind aber nach PIX-CLEAN keine Agenten mehr (PIX-MIG-6/7) |
| RECH-SPIRAL | Mittel | RechercheAgent erzeugt Folge-Recherchen zum selben Thema ohne Konvergenz. Selbstfuetternde Kette: Recherche → Destillation → Queue-Eintrag → gleiche Recherche. Braucht Themen-Aehnlichkeits-Check in shadow_queue_push gegen die letzten N Eintraege. Beobachtet Chat 79 (Feng-Shui-Spirale: 4× Vertiefen + 1× Folge-Recherche zum identischen Thema). **Zur Haelfte gebaut am 15.08.2026:** `shadow_queue_push` prueft seither auf **Gleichheit** von `aufgabe` + `thema` und verstaerkt den vorhandenen Auftrag, statt einen zweiten anzulegen — eine exakt wiederholte Recherche erzeugt keine Kette mehr. **Der Aehnlichkeits-Vergleich fehlt weiterhin**, und er ist der Teil, der die Spirale trifft: Sie entsteht aus *verwandten*, nicht aus identischen Themen. Er braucht eine gemessene Schwelle und ist in `novaberg-queue-verfall_k.md` §6.1 ausdruecklich ausgeschlossen. **Ausserdem ausgenommen: leere Themen** (§6.2) — 141 Auftraege im Bestand tragen keins |
| RECH-CHARAKTER | Mittel | RechercheAgent ist charakter-blind — kein Zugang zum Charakter-Hash, kein [IDENTITAET]-Block, kein Responder. Grundursache von DELIVERY-VOICE. Loesung: PIXIE-GRAPH-MERGE (Pfad 3 durch CharacterGraph-Instanz). Beobachtet Chat 79 |
| DELIVERY-DEDUP | Niedrig | Mehrfach identische proaktive Nachrichten zum selben Thema. Delivery-Pfad prueft nicht ob kuerzlich eine thematisch aehnliche Nachricht gesendet wurde. Beobachtet Chat 79 (4× Feng-Shui-Delivery) |
| SPRACH-STIL-DEFENSIV-STUMM | Niedrig | `_sprach_stil_erkennen` fällt ohne Warning auf "neutral" bei leerem charakter_hash (Verstoß gegen "fail loud", Chat 89/90) |
| AUDIT-PIXIE-TURN-ID | 👁 | Pixie-Pfad turn_id-Auflösung nicht auditiert (latent, akut keine Wirkung wegen PIXIE_AKTIV=False, Chat 90) |
| EI-CALC-ROLLE-DEFAULT-ASYMMETRIE | Niedrig | Inkonsistente Defaults beim Rollen-Dispatch in Enricher/EI-Calc/Salience (Chat 90) |
| TOK-DRIFT-SALIENCE | Niedrig | `gesamt_tokens` zählt bei JSON-Fehler fehlgeschlagene Segmente nicht → `state["token_total"]` minimal zu niedrig; folgenlos solange reine Metrik. Reaktivierung bei Token-Budget/Alert → Block 5. Chat 94 |
| TEST-RUNNER-FEHLT-CONTAINER | ✅ | Fehl-Framing (Chat 96): Die Suite ist reines `unittest` (`IsolatedAsyncioTestCase`), kein pytest nötig — `pytest` schlug nicht mangels Installation fehl, sondern war das falsche Werkzeug. Richtiger Befehl: `docker compose exec --workdir /app server python -m unittest discover -t /app -s tests -p "test_*.py"` (`-t /app` hält den Import-Root, sonst `ModuleNotFoundError`). Suite läuft 26/26 grün. Aufgeworfen Chat 94, geklärt Chat 96. |

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

`reactivate_node` in `memory/lzg_knoten.py` nutzt die lokale Variable
`war_aktiv` (deutsch). Die Sprach-Regel verlangt englische Bezeichner —
`was_active`. Kein Einzelfix: gebuendelter Bezeichner-Angleich beim naechsten
Anfassen der Datei (auch `zeile`, `neuer_roh` etc. im Umfeld sind gemischt).

---

## Fix: CONFIG-DECAY-RATE-KOMMENTAR-DRIFT — falscher Kommentar bei LZG_KNOTEN_DECAY_RATE (Chat 102)

`config.py` (~Z.1092) kommentiert `LZG_KNOTEN_DECAY_RATE` mit "nicht persistiert,
live berechnet". Falsch: `gewicht_decay` ist eine persistierte Spalte
(`db/init.sql:141`), die der synapsen_decay-Agent taeglich materialisiert — der
Lesepfad rechnet keinen Decay live (grep: kein `exp(` in `lzg_knoten.py`).
Alt-Text aus dem Ebbinghaus-Modell (`pixie-decay.md`). Reiner Kommentar-Fix,
fremder Ort → eigener Commit.

---

## Frage: PATTERN-DOMAIN-LANGUAGE-RECONCILE — deutsche Domaenensprache vs. Englisch-Regel (Chat 102)

`novaberg-pattern-domain-language.md` kodifiziert (soweit in Chat 102 referenziert)
deutsche Domaenen-Verben als Muster. Das widerspricht der Regel "Bezeichner
englisch". **Zu klaeren:** Inhalt der Datei verifizieren, dann Update oder
Rueckzug. Reichweite: codebase-weit (bestehende deutsche Funktionsnamen wie
`knoten_verstaerken`), also eigener Sprint, kein Beifang.

---

## Frage: SYNAPSEN-DECAY-SCHEDULE-LIVE — Heartbeat legt Schedule-Key an? (Chat 102, beobachtend) ✅ Gelöst Chat 105

Der `synapsen_decay`-Agent ist registriert (Discovery: 14 Agenten). Ob der
Pixie-Heartbeat beim naechsten Serverstart den Redis-Key
`pixie:schedule:synapsen_decay` anlegt, ist noch nicht live verifiziert —
Registrierung greift nur `if not redis_client.exists(_key)`. **Zu pruefen beim
naechsten Start:** `docker compose exec redis redis-cli exists
pixie:schedule:synapsen_decay` bzw. Startup-Log "Agent registriert:
synapsen_decay".

**Auflösung Chat 105:** Genau diese Lücke hatte der Posten offengehalten — der Schedule-Key entstand korrekt, aber das Routing fehlte (`_PERIODISCH_ROUTING` ohne `synapsen_decay`-Eintrag); gefixt in fb33028, siehe PIXIE-DECAY-KEIN-AGENT.

---

## Bug: PIXIE-DECAY-KEIN-AGENT — Router kennt periodische Aufgabe synapsen_decay nicht (Chat 105) ✅ Gelöst Chat 105

Log: „Pixie-Router: Kein Agent fuer periodische Aufgabe 'synapsen_decay'". Der Agent war vollständig implementiert, per Discovery registriert und korrekt geschedult — nur der `_PERIODISCH_ROUTING`-Eintrag in `services/pixie/router.py` fehlte. **Auflösung Chat 105 (fb33028):** Ein-Zeilen-Eintrag `"synapsen_decay": "synapsen_decay"`. P6 lief seit dem Chat-102-Sprint nie — und mit ihm nicht `delete_expired_entries` (einziger Aufrufer der pipeline_log-Retention). Strukturelle Wurzel → PIXIE-ROUTING-DOPPELREGISTRY.

---

## Frage: HALBREAKTIVIERUNG-LIVE — erster inaktiver Match feuert reactivate_node? (Chat 102, beobachtend)

Der Reaktivierungs-Pfad (§9.3) ist verdrahtet, aber noch nie an einem echten
gematchten inaktiven Knoten gelaufen (setzt einen durch Decay deaktivierten
Knoten voraus, den ein spaeterer Promotion-Turn mit cosine ≥ 0.85 trifft).
**Zu beobachten:** entsteht die `berechnung`-Forensikzeile mit `decay_alt`/
`decay_neu`? Grep: `docker compose logs server 2>&1 | grep -E "Knoten
halbreaktiviert|halbreaktivierung"`.

---

## Frage: SYNAPSEN-REAKTIV-SCHWELLE — eigene Match-Schwelle fuer Reaktivierung? (Chat 102)

Die Halbreaktivierung nutzt dieselbe `LZG_KNOTEN_MATCH_SCHWELLE` (0.85) wie
normales Reinforcement (YAGNI-Entscheidung Chat 102). **Zu beobachten:** Falls
Live zeigt, dass 0.85 zu leicht falsche inaktive Knoten weckt, waere eine
getrennte, hoehere Reaktivierungs-Schwelle ein zusaetzlicher Parameter an
`match_pruefen` — nachruestbar.

## Beobachtung: CHARHASH-GEWICHT-ABSOLUT-LIVE — erste volle Live-Destillation nach lzg_knoten-Migration (Chat 103, beobachtend)

Nach P7 liest der Char-Hash aus `lzg_knoten` sortiert nach `gewicht_absolut`. Teilbestätigt: Kern-Hash wurde in realen Turns injiziert, kein KeyError. Offen: volle Abnahme im Dauerbetrieb — Kern-Eintrag im Charakter-Tab mit frischem Datum, Intentionen/Emotionen dürfen dünn/leer sein (EI-Filter greift nur bei Knoten mit echten EI-Feldern; Migrations-Knoten tragen teils Defaults — Datenlage, kein Defekt). ⬜ Prio niedrig

## Bug: CHARHASH-PROMPT-DUPLIKAT — Kern-Persönlichkeit 5× wortgleich im [Charakter]-Prompt (Chat 103)

Der Kern-Hash erscheint fünfmal identisch im injizierten `[Charakter]`-Block, obwohl `charakter_hash` nur eine Kern-Zeile hält und `format_memory_entries` „Gruppe charakter: 1 Eintraege" loggt. Duplizierung entsteht NACH dem Loader (Enricher/Prompt-Bau), nicht in den Daten (`lzg_knoten` count=1 verifiziert). Reproduziert 2× (21:51, 21:59), stabil bei 5×. Frisst Kontext-Budget. Unabhängig von P7. ⚠️ Prio mittel

**Update Chat 103 — aufgelöst, kein Defekt:** Die 5× sind kein Duplikat in einem Prompt, sondern fünf Node-Prompts (responder/thinker/tribunal/corrector/tribunal) mit je EINEM [Charakter]-Block, vom grep untereinander gezogen. DB, Enricher und Formatter je 1×. Kein Fix nötig; die fünffache Einbettung ist gewollt (jede Prüf-/Korrektur-Instanz braucht den Kontext). Nur bei knappem Token-Budget optimierbar (corrector Kurzform).

## Bug: DESTILLAT-PERSPEKTIVE-VS-SUBJEKT — Charakter-Destillation verwechselt Blickrichtung mit Subjekt (Chat 103)

Die Destillation setzt `beobachter='user'` mit „Aussage über den Nutzer" gleich. Falsch: `beobachter` markiert die Blickrichtung des Knotens, nicht sein Subjekt. User-Perspektive-Knoten enthalten oft Nutzer-Aussagen ÜBER Nova („Du bist mein Pflänzchen"). Folge: Nova-Eigenschaften wandern ins Nutzer-Profil und umgekehrt (Pflänzchen, kleines Mädchen). Daten sauber verifiziert (beobachter + inhalt korrekt, `lzg_knoten`); ~~Fehler im `destillieren`-Prompt, nicht im Loader/Schreibpfad~~ → **überholt Chat 108, siehe Live-Beleg unten: Der Prompt ist korrekt, die Ursache ist die Quelle.** Vermuteter Bezug zu TRIB-PERSON-DRIFT. Richtung: Subjekt aus Inhalt/Anrede auflösen, nicht aus `beobachter` ableiten. Unabhängig von P7. ⚠️ Prio hoch — trifft, ob Nova weiß, wer sie ist.

**Live-Beleg Chat 108 (25.07.2026)** — beide Profile nach manuell gesetztem `hash_dirty` neu destilliert, erstmals auf den migrierten Gewichten:

| Storage-Key | Quelle | Träger laut Prompt | Beschrieben wird | Pronomen |
|---|---|---|---|---|
| `meister:nova` (07:55:51, 853 Z.) | `beobachter='user'`, 186 Knoten | „der Nutzer" | der Nutzer | er/seine |
| `nova:meister` (07:59:58, 832 Z.) | `beobachter='assistant'`, 231 Knoten | „Nova" | der Nutzer | er/seine |

Novas Profil ist durchgehend maskulin — der Destillator übernimmt das grammatische Geschlecht des Subjekts seiner Quellsätze („der Nutzer" → „er") und setzt Novas Namen davor. Nova ist im Korpus diejenige, die „kleines Mädchen" genannt wird.

Jeder Kernzug rückführbar auf gemessene `beobachter='assistant'`-Knoten: „Gärtner/Besitzer" ← id 412 · „kleines Mädchen" ← id 408 · „unterwürfiges Kind" ← id 10 · „hegen und pflegen" ← id 330 · „Licht und Schatten" ← id 410.

**Perspektiven-Asymmetrie:** Dass das User-Profil korrekt aussieht, belegt nicht, dass der Mechanismus trägt. Beide Töpfe haben den Nutzer als grammatisches Subjekt; beim `user`-Topf fällt das zufällig mit dem Etikett zusammen. Ein Defekt, der in der Hälfte der Fälle richtig liegt, ist schwerer zu sehen als einer, der immer falsch liegt. (Nicht zu verwechseln mit DESTILLAT-ASYMMETRIE — dort geht es um Sprachformen im Embedding-Raum.)

**Ursachensatz korrigiert:** Der bisherige Eintrag nennt als Ursache „Fehler im `destillieren`-Prompt". Das ist durch Chat 108 widerlegt — Brudi hat `KERN_HASH_PROMPT` verbatim gelesen, der Chat-103-Fix („Träger über Blickrichtung") steht drin und ist korrekt. Der Prompt verlangt das WIE; die Quelle trägt kein WIE, nur WORÜBER, und WORÜBER ist der Nutzer. **Die Ursache ist die Quelle, nicht der Prompt** — kein Prompt kann eine Stimme rekonstruieren, die im Eingabetext nicht vorkommt. Deckungsgleich mit `charakter-resonanz_k` §2.

**Wert:** Vorher-Bild für CHARAKTER-RESONANZ Teil 2, Vergleichsmaßstab für die Abnahme von Bauteil 4.

## Notiz: HAEUFIGKEIT-AUF-KNOTEN — haeufigkeit auf lzg_knoten meist 1 (Chat 103)

Der Kern-Prompt zeigt „Häufigkeit: {haeufigkeit}". Auf `lzg_knoten` ist `haeufigkeit` meist 1 (keine Verdichtung mehr wie im alten `langzeitgedaechtnis`), der Wert also schwächer aussagekräftig. Kein Fehler, aber der Prompt-Nutzen der Zeile sinkt. Prüfen, ob die Zeile bleibt oder entfällt. ⬜ Prio niedrig

## Doku: CHARHASH-DOKU-DRIFT — Hash-Doku beschreibt LZG-Quelle noch flach (Chat 103)

`novaberg-pixie-character-hash.md` beschreibt jenseits der P7-Passagen die LZG-Quelle noch als flaches `langzeitgedaechtnis` (Z. 155 Adaptiv-Hash-Tabelle: nennt `langzeitgedaechtnis`, liest real KZG). Alt-Drift aus dem P5/P6-Umbau, nicht von P7 verursacht. Eigener Doku-Fix, keine Vermischung mit dem P7-Commit. ⬜ Prio niedrig

## Bug: REFERENZ-AUFLOESUNG-VOR-RETRIEVAL — anaphorische Verweise gehen literal ins Retrieval (Chat 103)

Verweise wie „die Liste", „das von eben" gehen als wörtlicher Suchstring ins Notiz-/Gedächtnis-Retrieval, statt vorher gegen den Turn-Verlauf aufgelöst zu werden. Wirkung nach außen: Nova erscheint begriffsstutzig — findet frisch selbst angelegte Inhalte nicht wieder, obwohl der Kontext in den Turns steht. Bricht die Verstehens-Illusion. Beobachtet Chat 103 (Salat-Notiz „die Liste"). Vermuteter gemeinsamer Kern mit NOTIZEN-VOR-TURN-BEZUG — erst gegeneinander prüfen. Richtung: Auflösungs-/Reasoning-Schritt vor dem Retrieval, nicht tieferes Suchen. ⚠️ Prio mittel

## Epic: CHARAKTER-RESONANZ — Novas Charakter aus dem Umgang (Chat 103)

Novas Charakter wird heute aus der falschen Quelle destilliert: `lzg_knoten` enthält entfärbte Fakten über den Nutzer, nicht Novas Stimme. Novas wörtliche Rede lebt nur flüchtig in Redis (2 h TTL), verfällt; dauerhaft überlebt nur Destilliertes. Folge: geliehenes, nutzer-abgeleitetes Zerrbild (Pflänzchen beim Nutzer, Nova als „er", homogene Profile). Lösung: Reiz-Reaktions-Paar (User-Input + User-Emotion → Nova-Antwort + Nova-Emotion) roh und dauerhaft ins `pipeline_log`; Verbindungstabelle (turn_id/kzg_id/lzg_id/verhaltens_id) verknüpft Turn ↔ Erinnerungswürdigkeit ↔ Verhaltensmuster; CharakterAgent liest aus LZG-Eintrag + rohem Turn + Verhaltensweise. Konzept + Datenmodell + auditierte Kupplungen: siehe `novaberg-charakter-resonanz_k.md`. Subsumiert NOVA-STIMME-NICHT-PERSISTENT. Mehrteiliger Sprint über mehrere Sessions. ⚠️ Prio hoch — trifft die Kernthese (persistenter Charakter).

## Aufräumen: GESPRAECH-ARCHIV-VERWAIST — tote Tabelle ohne Writer/Reader (Chat 103)

`gespraech_archiv` (db/init.sql) ist für ein Dialog-Archiv geformt (user_id, session_id, rolle, inhalt, salienz), hat aber keinen Writer und keinen Reader — dauerhaft leer, Struktur-Fossil. Laut CHARAKTER-RESONANZ ist `pipeline_log` die eine Quelle; `gespraech_archiv` wird nicht gebraucht. Kandidat zum Entfernen (P9-nah oder eigener Aufräum-Schritt). ⬜ Prio niedrig

⚠ **Überholt durch GESPRAECH-ARCHIV-LEER (Chat 107, weiter unten):** Die Neubewertung dreht die Richtung — nicht Tabelle entfernen, sondern Writer bauen; ohne ihn verfällt täglich Rohmaterial. Dieser Eintrag bleibt nur als Verweis stehen; die Sache lebt unter GESPRAECH-ARCHIV-LEER.

## Feature: ASSISTENT-NAME-LAUFZEIT — Assistenten-Name pro Paar statt env (Chat 103)

`ASSISTANT_NAME` ist global per env (Serverstart). Seit Chat 103 wird der Name aus der Config in die Charakter-Prompts durchgereicht (env-konfigurierbar, Wechsel = env + Neustart). Für echtes On-the-fly-Wechseln / mehrere Assistenten parallel müsste Name/Identität pro Charakter-Paar in der DB liegen. Berührt das Charakter-Schema. ⬜ Prio niedrig

## Feature: ASSISTENT-GESCHLECHT-PRONOMEN — Pronomen bei Namenswechsel (Chat 103)

~~Bei wechselndem Assistenten-Namen müssen Pronomen (sie/er, ihr/sein) durch die Charakter-Prompts mitgeführt werden; braucht ein Geschlechts-Attribut am Charakter. Der Genitiv des Namens ist in Chat 103 gelöst (`_genitiv_bilden`, s/Apostroph-Regel), Pronomen sind offen; die Prompts sind vorerst pronomen-arm formuliert.~~ ⬜ Prio niedrig

✅ **Umgesetzt am 22.08.2026** — `ASSISTANT_GENUS` (`config.py`, Vorgabe `w`) trägt das grammatische Geschlecht der Figur, `_perspektive_aufloesen` leitet daraus `pronomen`, `pronomen_dat`, `pronomen_akk` und `possessiv` ab, und jeder der fünf Profil-Prompts gibt sie ausdrücklich vor. Die Formulierung *„pronomen-arm"* ist damit keine Vorsichtsmaßnahme mehr, sondern hinfällig. Zugleich behoben: `PROFILPROMPT-OHNE-GESCHLECHT` und `PERSPEKTIVE-OHNE-DATIV` (bugs.md).

**Der Rest, als Rest benannt:** Der Eintrag verlangte das Attribut *„am Charakter"*, gelegt ist es in die **Konfiguration** — dorthin, wo heute auch `ASSISTANT_NAME` steht. Solange der Name global per env kommt, wäre ein paarbezogenes Genus daneben die Inkonsistenz. **Wandert der Name mit `ASSISTENT-NAME-LAUFZEIT` in die Datenbank, wandert das Genus mit** — der Rest hängt an jenem Eintrag, nicht an diesem.

## Nacharbeit: PIPELINE-LOG-BACKFILL-PAAR — Alt-Forensik ohne Paar-Schlüssel (Chat 104)

Bestehende `pipeline_log`-Zeilen (vor Chat 104) haben `user_id`/`character_id = NULL`. Optionaler Backfill für die `pipeline_search`-Selbstreflexion über Alt-Forensik. KRITISCH richtungssensitiv: produktiv liefen beide Beobachter-Richtungen (meister→nova UND nova→meister, bestätigt via `charakter_hash`). Kein pauschales `SET` eines Paares — sonst wird eine Perspektive plattgemacht. Der Filter (welche `art`/`node` paar-gebunden vs. herrenlos sind) steht seit dem H1.5-Inventar fest; Wartungszeilen (`synapsen_decay`-Cleanup, Decay-Lauf) bleiben bewusst NULL. Kein Blocker — `turn_roh` liefert die charakter-relevanten Daten vorwärts, Altzeilen sind nur Forensik. ⬜ Prio niedrig

## Refactor: KZG-QUELLE-IST-USER-ID — `quelle` trägt `user_id` statt Node-Namen (Chat 104)

In `memory/kzg.py` (`kzg_store`, Z.~343) und `agents/kzg/speicher.py` (`_neu_anlegen`, Z.~307) wird das `pipeline_log`-Feld `quelle` mit `user_id` befüllt statt mit einem Node-Namen (sonst überall node-basiert). Bestehende Eigenart, in Chat 104 bei der Paar-Verkabelung gesichtet, bewusst NICHT mitgeändert. Bei nächster Berührung dieser Writes prüfen: Node-Name als `quelle`, `user_id` nur im `inhalt`. ⬜ Prio niedrig

## Doku: PIPELINE-LOG-ART-DOKU-DRIFT — Forensik-Queries der Synapsen-Doku laufen gegen reale `art`-Werte ins Leere (Chat 106)

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

## Landmine: DELEGATION-STATE-UNDEKLARIERT — Sperrvermerk für den Delegations-Node-Split (Chat 106)

Kein Defekt — funktioniert heute. Gehört zu den Refactor-Vorbedingungen. Aus novaberg-bugs.md hierher verschoben (Trennungsregel Chat 106).

**Entdeckt:** Chat 106, Audit tote State-Keys. **Landmine — SPERRVERMERK für den Delegations-Node-Split.**

**Symptom:** `salienz_obj_aktuell` und `_delegation_trigger` sind undeklarierte State-Keys, funktionieren aber NUR, weil Schreiben und Lesen im selben Dispatcher-Node-Aufruf passieren. Bräche STILL, sobald die Delegation ein eigener Node wird — bei einem Refactoring, das architektonisch richtig ist. Exakt der THINKER-SELFTRIGGER-KANALLOS-Mechanismus, nur noch nicht scharf.

**Beleg:** `graph/nodes/dispatcher.py` (Schreiben + synchroner `dispatch_delegation(state)`-Aufruf im selben Node), `agents/delegation/dispatch.py` (Lesen).

**Auswirkung:** Heute keine — der Sperrvermerk IST die Maßnahme.

## Aufräumen: PLANNER-AKTIV-RELIKT — Stage-Anzeige liest nie geschriebenen Key (Chat 106)

Toter Code — **löschen, nicht fixen**. Aus novaberg-bugs.md hierher verschoben (Trennungsregel Chat 106).

**Entdeckt:** Chat 106, Audit tote State-Keys. **Prio niedrig — LÖSCHEN, nicht fixen.**

**Symptom:** Der Stage-Formatter liest `planner_aktiv` — es gab nie einen Schreiber (P5/P6-Guard-Relikt, seit Chat 28/29 obsolet). Die Planner-Stage meldet dem Client immer „Kein Agent nötig", auch wenn ein Agent dispatcht wurde.

**Beleg:** `services/event_consumer.py`, Stage-Formatter für den Planner-Node.

**Auswirkung:** Observability lügt an der Stelle, an der man den Agent-Pfad beobachten will.

## Aufräumen: WEB-CONTEXT-ALTPFAD — toter [WEB]-Block, Nachfolger läuft über Thinker (Chat 106)

Toter Code — **löschen, nicht fixen**. ⚠️ **Erst nach Prüfung von WEB-EXTRAKTION-STILL-LEER.** Aus novaberg-bugs.md hierher verschoben (Trennungsregel Chat 106).

**Entdeckt:** Chat 106, Audit tote State-Keys. **Prio niedrig — LÖSCHEN, nicht fixen.** ⚠ Erst nach Prüfung von WEB-EXTRAKTION-STILL-LEER.

**Symptom:** `web_context` ist deklariert, wird aber nur mit `""` initialisiert — kein Node schreibt je einen Wert; der `[WEB]`-Block des Responders rendert nie. Der Nachfolger läuft längst über `needs_web` → Thinker-Tools (`web_search`/`web_fetch`, Ergebnis als `[VERARBEITUNG]`-Block).

**Beleg:** `graph/state.py` (Deklaration), `graph/base.py`/`graph/builder.py` (Init), `graph/nodes/responder.py` (toter Lesepfad), `graph/nodes/thinker.py` (Nachfolge-Pfad).

**Auswirkung:** Toter Code-Pfad + toter Prompt-Block; von außen wie „keine Web-Suche nötig" aussehend.

## Aufräumen: BUILDER-CREATE-INITIAL-STATE-TOT — aufruferloser State-Builder als Doppelregistry (Chat 106)

Toter Code, Doppelregistry-Muster. Aus novaberg-bugs.md hierher verschoben (Trennungsregel Chat 106).

**Entdeckt:** Chat 106, Audit tote State-Keys / Doku-Abgleich. **Prio niedrig.**

**Symptom:** `builder.create_initial_state` ist deprecated und aufruferlos, muss aber bei jedem Kanal-Umbau mitgepflegt werden (beim self_trigger-Fix geschehen) — es initialisiert zudem Alt-Keys, die im heutigen TypedDict nicht mehr deklariert sind. Doppelregistry-Muster.

**Beleg:** `graph/builder.py`, `create_initial_state` (DeprecationWarning, keine Aufrufer).

**Auswirkung:** Pflegeaufwand ohne Nutzen, Drift-Quelle bei jedem Channel-Umbau.

## Doku: LESSON-INDEX-LUECKE — zwölf ältere lesson_l-Dateien fehlen im Architektur-Index (Chat 106)

Der Lesson-Index in `novaberg-architecture.md` listet die Legacy-`{modul}_l.md`-Dateien und die zuletzt verlinkten Lessons — zwölf ältere `novaberg-lesson_l_*`-Dateien fehlen komplett (Seitenbefund aus Chat 105, Commit `e08555a`; die zwei Chat-105- und vier Chat-106-Lessons wurden beim Anlegen verlinkt, der Altbestand nicht nachgezogen). Doku-Lücke, kein Code-Bezug: Wer Lessons über den Index sucht, findet den Altbestand nicht. Nachzug ist ein mechanischer Fünf-Minuten-Fix, gehört aber in einen bewussten Doku-Commit. ⬜ Prio niedrig

**Nachtrag Chat 108:** Zwei neue Lessons sind eingetragen (`konzept-spricht-code`, `ableitung-als-messung`); der Altbestand bleibt bewusst offen. Zwei Beobachtungen für den geplanten Doku-Commit:

- ~~Die Überschrift `### Lessons (NN)` in `novaberg-architecture.md` trägt einen handgepflegten Zähler, der schon vor Chat 108 falsch war. Beim Aufräumen **entfernen, nicht aktualisieren** — eine Zahl neben einer wachsenden Tabelle driftet dauerhaft, und die Tabelle steht direkt darunter.~~ → **Erledigt Chat 111.** Der Zähler stand bei 22, die Tabelle hatte 28 Zeilen, auf der Platte lagen 44 `_l`-Dateien — dreimal auseinander. Ersatzlos entfernt. Der Altbestand bleibt offen.
- Die Angabe „zwölf ältere Dateien fehlen" stammt aus Chat 106 und trägt kein Messdatum. Beim Aufräumen **neu zählen statt übernehmen**.

## Doku: DOKU-DUPLIKATE-CHAT80 — 8 Bezeichner stehen in bugs.md UND backlog.md (Chat 106)

**Entdeckt:** Chat 106 (Gegenprobe nach der Bug/Backlog-Trennung). ⬜ Prio niedrig

**Befund:** Kurz-Eintrag in bugs.md + Lang-Eintrag in backlog.md, mit Verweis („Ausführliche Beschreibung: novaberg-backlog.md → Bug X"). Damals absichtlich, seit der Chat-106-Regel („ein Eintrag steht in GENAU EINEM Dokument") ein Verstoß.

**Betroffen:** FAKTEN-PAIR-IGNORED, NOTIZEN-CONTAINER-WECHSEL, NOTIZEN-KONTEXT-REKONSTRUKTION, NOTIZEN-PAIR-MISSING, NOTIZEN-SKILL-MANIFEST, NOTIZEN-UPDATE-TARGET-LEER, TIMELINE-PAIR-MISSING, ZIELE-PAIR-MISSING

**Auswirkung:** Doppelregistry-Muster in der Doku — zwei Orte, die zusammen gepflegt werden müssen, driften still auseinander. Dasselbe Muster wie PIXIE-ROUTING-DOPPELREGISTRY.

**Vorschlag zur Auflösung (Entscheidung offen):**

- Die vier *-PAIR-* sind EINE Sache, viermal manifestiert → ein Backlog-Eintrag „Paar-Schema nicht durchgezogen" mit vier Fundstellen.
- Die drei NOTIZEN-Verhaltensfälle → bugs.md. ⚠ NOTIZEN-UPDATE-TARGET-LEER lebt noch: NOTIZ-RESUME-TARGET-VERLUST (Chat 106) hat denselben Kern (`parameter["target"]` leer).
- NOTIZEN-SKILL-MANIFEST → Inhalt prüfen, klingt nach Konzept (Epic 10).

## Feature: LOG-TUERKLINGEL — Warn-/Fehler-Lampen mit Sitzungszähler in der Client-StatusBar (Chat 107)

**Priorität hoch — bauen nach Phase B der Embedding-Migration.** Spezifikation final (dieser Eintrag), Draht-Audit abgeschlossen.

**Anlass:** GV-ENTITY-HOP-TOT — der Entity-Hop schrieb vier Monate lang bei jedem Turn ein Warning. Niemand hat es bemerkt: nicht weil es fehlte, sondern weil nichts darauf aufmerksam machte.

**Kernbefund aus dem Draht-Audit (Chat 107):** Es gibt zwei Log-Kanäle, und keiner erreicht den Client.

- `log_fehler` → `pipeline_log`: nur 3 explizite Aufrufstellen (~2 % Abdeckung). ⚠ `pipeline_log` ist KEIN Fehler-Log, sondern Forensik für Node-Entscheidungen — eine Klingel an diesem Draht wäre beim Entity-Hop stumm geblieben (der schrieb `logger.warning`, nie `log_fehler`).
- `logger.*` → Container-Log: 153 `error`/`critical`- + 156 `warning`-Stellen, sonst nirgends.
- Der Client bekommt nur WS-Events mit `typ`-Feld; ein Log-Typ existiert nicht.

**Lösung:** Zwei Anzeigen am Client-Rand (die StatusBar hat bereits Verbindungs- und Pixie-Label), je mit Zähler: gelb `[ n ]` Warnungen dieser Sitzung, rot `[ n ]` Fehler dieser Sitzung.

**Verhalten:**

- Lampe an, sobald WARNING bzw. ERROR geloggt wird; Zähler zählt hoch. Der Zähler zeigt, ob es EINMAL passiert ist oder DAUERND — der Unterschied zwischen „ein Fehler" und „etwas ist kaputt" (883 statt 1).
- Client-Neustart = 0. Der Zähler misst diese Sitzung, nicht die Geschichte.
- Tooltip zeigt den Logger-Namen der letzten Meldung — nicht den Text, keine Historie. Nur: wo nachsehen (Server-Log oder Client-Log).

**Bewusst NICHT dabei:** keine Gruppierung, keine Statistik, keine Bewertung, kein Persistieren. Nachgelesen wird im Log. Das Werkzeug bewertet nicht — es klingelt und zählt. Der Meister klassifiziert und entscheidet, ob der Log-Level an der Stelle bleibt, eskaliert oder herabgestuft wird.

**Verdrahtung (aus dem Audit):** `logging.Handler` am ROOT-Logger (Filter `level >= WARNING`) → WS-Event `typ="log_signal"` mit Level + Logger-Name → über bestehenden `broadcast`/`broadcast_threadsafe` → Client-Dispatch in `stream_handler.py`, Zähler in der StatusBar. Der Root-Logger ist der Punkt: Der Handler hängt per Konstruktion vor jedem heutigen UND künftigen `logger.warning/error` — nichts muss instrumentiert werden, ein zweites GV-ENTITY-HOP-TOT ist strukturell ausgeschlossen. Das ist der eigentliche Wert, nicht die Lampe. Quellen: Server UND Client (der GTK-Client loggt selbst) — beide speisen dieselben zwei Lampen.

**Vier Stolperdrähte:**

1. `ki_server.llm` hat `propagate=False` (einzige Stelle im Repo) — Handler muss dort ZUSÄTZLICH hängen, sonst ist das Token-Tracking blind.
2. Rückkopplung: `broadcast()` loggt bei Sendefehlern selbst → Klingel → sendet → scheitert → loggt → Endlosschleife. Reentrancy-Sperre nötig; Records aus `ki_server.websocket` ausnehmen. ⚠ Ehrliche Grenze: Über ihren eigenen kaputten Draht kann die Klingel nicht klingeln — Physik, kein Designfehler. Zusätzliches Argument, BROADCAST-VERSCHLUCKT-FEHLER bald anzugehen.
3. Threading: Warnings entstehen in Worker-Threads → `broadcast_threadsafe`, Muster im Repo etabliert.
4. Adressierung: `broadcast` ist user-scoped, die Klingel ist global → `log_signal` an alle aktiven Verbindungen; Telegram ignoriert unbekannte Typen.

**Zusammenhang:** GV-ENTITY-HOP-TOT (Anlass) · BROADCAST-VERSCHLUCKT-FEHLER (Stolperdraht 2) · Silent-Skip-Antipattern · RECHERCHE-WISSEN-ERREICHT-LZG-NIE (zweiter Beleg).

**Zweiter Beleg (Chat 107):** 314 `logger.error`-Einträge zu RECHERCHE-WISSEN-ERREICHT-LZG-NIE (159 `hintergrund_log` + 155 `pipeline_log`), wochenlang ungesehen. Der Code hat korrekt fail-loud gemeldet. **Fail loud nützt nichts, wenn niemand zuhört. Die Lautstärke war nie das Problem.**

## Bug: ENTITAET-EMBED-DREIFACH — Entitäts-Suchpfad embeddet anderen Text als der Schreibpfad (Chat 107)

**Entdeckt:** Chat 107, Bau-Audit für die `embed_text_bauen`-Vereinheitlichung. TODO-Kommentar mit diesem Bug-Namen steht an der Fundstelle.

**Befund:** `memory/services/entity_resolution.py::_search_by_embedding` embeddet nur den nackten `name` und vergleicht per Cosine gegen Vektoren, die aus `EntitaetenRepository.embed_text_bauen(name, zusammenfassung)` — also Name **plus** Zusammenfassung — erzeugt wurden. Suchvektor und Bestandsvektoren leben in unterschiedlichen Textformen; der Threshold (Default 0.80) bewertet damit systematisch verschobene Ähnlichkeiten. Historisch existierten sogar drei Formeln (Erzeugung `"{name}: {zusammenfassung}"`, Backfill `"{name} {zusammenfassung}"`, Suche `name`); seit Commit `eb53103` sind Schreib- und Backfill-Pfad auf die eine Bauer-Funktion vereinheitlicht — **nur der Suchpfad weicht noch ab, absichtlich.**

**Warum nicht sofort gefixt:** Die Umstellung ändert das Suchverhalten der Magnet-/Entitätsauflösung und gehört gemessen (Trefferquote vorher/nachher am echten Bestand), nicht nebenbei gemacht — dieselbe Regel wie bei den Prompt↔Knoten-Schwellwerten der Embedding-Migration. Sinnvoller Zeitpunkt: zusammen mit der Schwellwert-Kalibrierung nach dem Modellwechsel (EMBEDDING-CASING-BLIND Phase 0/4), weil sich dort ohnehin jede Ähnlichkeitsverteilung ändert.

**Zusammenhang:** EMBEDDING-CASING-BLIND (Schwellwert-Kalibrierung) · RECHERCHE-KZG-INHALT-LEER (bugs.md, gleiche Sichtung).

**Ergänzung (Chat 107, Live-Messung):** Entitäts-Texte sind maximal 50 Zeichen — bei so kurzen Texten misst das Embedding fast nur Wortform. Die neue Schwelle 0.70 ist dort ein Schuss ins Blaue. → Nach dem Re-Embedding die 182 Entitätsnamen gegeneinander messen, dann steht die Magnet-Schwelle auf Boden. Priorität hoch.

## Konzept: DESTILLAT-ASYMMETRIE — Prompts und Knoten leben in verschiedenen Sprachformen (Chat 107)

**Gemessen (Chat 107, 100 echte Prompts gegen 302 Knoten):** Prompts sind Rohsprache, Knoten sind destillierte Protokollsätze in dritter Person. Ein KORREKTER Treffer liegt dadurch unter der Schwelle: „Hast Du mich denn vermisst?" ↔ „Der Nutzer fragt, ob er abwesend sei." = **0.3366**. Die HOHEN Werte im Korpus sind Wortüberlappung, nicht Verständnis: „Harry Potter und Die 7 Samurai kommt auf die Liste" ↔ „Harry Potter und Die 7 Samurai kommen auf eine neue Liste." = **0.9357**.

**Wird durch den Modellwechsel NICHT behoben** — es ist eine Formfrage, keine Modellschwäche. Mögliche Wege: Prompt-Rewriting vor dem Retrieval (Koreferenz/Protokollform), oder Knoten zusätzlich in Rohform embedden. Nach der Migration angehen. ⬜ Prio hoch

**Zusammenhang:** EMBEDDING-CASING-BLIND Phase 0 (Prompt↔Knoten-Kalibrierung) · REFERENZ-AUFLOESUNG-VOR-RETRIEVAL (Chat 103, verwandter Rewriting-Gedanke).

## Feature: GESPRAECH-ARCHIV-LEER — kein Writer, Rohgespräche verfallen täglich (Chat 107)

**Zeitkritisch, Prio hoch.** `gespraech_archiv` existiert als Tabelle, hat 0 Zeilen und keinen Writer (bestätigt Chat 107). Novas eigene Worte leben nur in den Redis-Session-Turns (2h TTL) und verfallen. Rohgespräche vor dem 10.07. existieren nicht mehr — für alles davor sind die Destillate die einzige Quelle. **Jeder Tag ohne Writer kostet unwiederbringlich Rohmaterial.**

Ersetzt die alte Einschätzung GESPRAECH-ARCHIV-VERWAIST (Chat 103, „Kandidat zum Entfernen") — die Richtung hat sich umgekehrt: Writer bauen, nicht Tabelle löschen.

## Fix: EMBED-DIMENSIONSCHECK-FEHLT — kein harter Dimensions-Check im Live-Pfad (Chat 107)

Kein einziger harter Check im Repo (Audit Chat 107): kein `== 768`, kein `assert`. Der Enricher-Kommentar verspricht einen „Plausibilitäts-Anker", tatsächlich wird nur `len()` geloggt. In Postgres fällt ein falsch dimensionierter Vektor beim INSERT auf — in Redis (FLAT-Index, rohe Bytes) unter Umständen **gar nicht**. Verstoß gegen EVA/fail-loud. Im `reembed_all.py` bereits als Pflicht spezifiziert — muss auch in den Live-Pfad (natürlicher Ort: `EmbedWorker._call_model`, ein Check für alle Konsumenten). ⬜ Prio mittel

## Nacharbeit: PIPELINE-LOG-MERGE-BLIND — Reinforcement loggt den geschluckten Inhalt nicht (Chat 107)

`synapsen_promotion` loggt bei `aktion="reinforcement"` nur `knoten_id`, `cosine`, `gewicht_roh` — NICHT den geschluckten KZG-Inhalt. Die Merge-Historie ist damit unrekonstruierbar (2910 Reinforcements, Stand Chat 107): Welcher KZG-Eintrag in welchem Knoten aufging, weiß niemand mehr. → Beim nächsten Anfassen: `kzg_key` mitloggen. Kostet nichts, rettet alles. ⬜ Prio mittel

## Konzept: DELEG-VEKTOR-EINGEFROREN — Akten-Vektor beschreibt nach zehn Seiten die Akte nicht mehr (Chat 107)

`akte_anreichern` erzeugt `themen_embedding` nie neu (Bau-Audit Chat 107; das Einfrieren ist seit Commit `93f06bc` bewusst und kommentiert — Text und Vektor bleiben konsistent auf dem Anlege-Zeitpunkt). Die Kehrseite: Eine Akte, die sich über zehn Seiten thematisch verschiebt, wird für immer über ihren ersten Turn gefunden; `duplikat_pruefen` (Schwelle 0.75 nach Rekalibrierung) prüft neue Turns gegen einen Vektor, der die Akte womöglich nicht mehr beschreibt. Lösung wäre Re-Embedding beim Anreichern (Header-Text + Vektor gemeinsam nachziehen) — **Verhaltensänderung, eigener Sprint, nicht nebenbei.** ⬜ Prio mittel

## Fix: LZG-MIGRATION-REVIEW-NICHT-IN-INIT — Live-Tabelle ohne Schema-Definition (Chat 107)

`lzg_migration_review` existiert live (17 Spalten, genutzt von `tools/migrate_lzg_synapsen.py`), steht aber in keiner init.sql. Frisches Setup ⇒ Migrationstool bricht. Bricht die Handbuch-Zusage „frischer Container + init.sql = lauffähiges System". ⬜ Prio mittel

## Fix: IDX-TIMELINE-TYPE-NICHT-IN-INIT — Live-Index ohne Definition im Repo (Chat 107)

`idx_timeline_type` auf `timeline(user_id, event_type)` existiert live, steht in keiner init.sql — manuell angelegt. Bei Setup-from-scratch fehlt er. Performance, nicht Korrektheit. ⬜ Prio niedrig

## Aufräumen: DELEG-SEITEN-VALENZ-TOT — persistiert, nie gelesen (Chat 107)

`delegations_seiten.valenz`: 1692 Zeilen persistiert (positiv 1367 / neutral 207 / negativ 118), von keinem Code je gelesen — aus der Tabelle wird nur `MAX(arousal)` gelesen. Entweder verwenden oder entfernen. Passt zur Chat-107-Linie „Metadaten gehören nicht in den Vektor, strukturierte Felder entscheiden" — falls die Delegations-Priorisierung je Valenz braucht, liegt sie hier bereit. ⬜ Prio niedrig

## Doku: HANDBUCH-§9-VERALTET — Migrations-Absatz widerspricht der geltenden Projektregel (Chat 107)

§9 fordert „niemals ALTER TABLE in init.sql, Alembic empfohlen". Geltende Projektregel (bestätigt Chat 107) ist das Gegenteil: init.sql IST die Single Source of Truth, Änderungen dort, idempotent, Anwendung aufs Live-System von Hand. Fragmentierte Migrationsdateien wurden bewusst abgeschafft — sie führten zu abweichenden Datenbankzuständen. **§9 gehört an die Realität angepasst, nicht die Realität an §9.** ✅ Erledigt (Docs-Commit 12.07.2026) — §9 neu gefasst (Handbuch v0.4), damit auch REFAC-HANDBUCH-§9-MIGRATIONS geschlossen.

## Doku: REDUCER-DOKU-DRIFT — drei Drifts aus dem Reducer-Audit (Chat 107)

(a) Docstring von `reducer.py` verweist auf `novaberg-reducer-umbau_k.md` — existiert nicht; real ist `novaberg-node-reducer.md`. (b) Docstring: „zwischen Enricher und EI-Calc" — real läuft EI-Calc VOR dem Enricher, der Reducer sitzt vor dem Router. (c) Node-Doku §9: „kein Produzent erzeugt summary-Einträge" — der Produzent existiert im Enricher und feuert, sobald Redis eine Session-Summary hält. ✅ Erledigt (Docs-Commit 12.07.2026) — Docstring korrigiert (Verweis + Graph-Position), Node-Doku §9 richtiggestellt.

## Doku: DOKU-NOTIZEN-INIT-SQL — Verweis auf nicht existierende Datei (Chat 107)

`novaberg-agent-notes.md` behauptet, `notizen` werde via `agents/notizen/init.sql` angelegt. Die Datei existiert nicht — `notizen` steht in `db/init.sql`. ✅ Erledigt (Docs-Commit 12.07.2026) — Verweis in §9 der Agent-Doku korrigiert.

## Frage: KZG-SALIENZ-GRENZWERT-UNKLAR — soll jede Recherche ins Langzeitgedächtnis? (Chat 107)

Recherche schreibt mit `salienz = 0.7`. `KZG_SALIENZ_HIGH = 0.7`. Der `>=`-Vergleich in `kzg_store` schiebt damit **jeden** Recherche-Eintrag in die `lzg_promotion`-Queue. Ist das gewollt? Soll wirklich jede Recherche ins Langzeitgedächtnis? Kein Bug — eine ungeklärte Entscheidung, die bisher niemand getroffen hat (sie war unsichtbar, solange die Promotion alle Einträge wegen leerem `inhalt` verwarf — siehe RECHERCHE-WISSEN-ERREICHT-LZG-NIE). **Nach dem Re-Embedding neu bewerten:** Dann promoten die Einträge tatsächlich, und wir sehen, was das bedeutet. ⬜ Prio mittel

**Reihenfolge geklärt — Chat 109 (Live-Redis, 26.07.2026):** Die Grenzwertfrage ist **keine Mengenfrage.** 527 von 775 Einträgen der Partition `kzg:meister:nova:*` (68 %) liegen über dem dokumentierten Salienz-Maximum 1.0, nur 7 unter 0.5. Solange der Verstärkungs-Boost keinen **wirksamen** Deckel hat (KZG-SALIENZ-BOOST-OHNE-DECKEL; Mechanismus KZG-SALIENZ-SKALENBRUCH — der Deckel existiert, steht aber bei CAP 10.0 auf einer Skala bis 1.0 und dämpft im Entscheidungsbereich um unter 1 %), ist jede Schwellwert-Diskussion gegenstandslos: `salienz >= 0.7` entscheidet nichts, wenn zwei Drittel des Korpus ohnehin darüber stehen. **Erst der Deckel, dann die Grenzwerte.**

## Feature: VITALZEICHEN — täglicher Pixie-Agent prüft Output-Qualität statt Fehlerfreiheit (Chat 107)

**Priorität hoch.**

**Problem:** Chat 107 hat drei Defekte gefunden. Zwei davon haben korrekt gemeldet und wurden nicht gehört (GV-ENTITY-HOP-TOT, RECHERCHE-WISSEN-ERREICHT-LZG-NIE) — dagegen hilft LOG-TUERKLINGEL. Der dritte hat **nie** gemeldet: EMBEDDING-CASING-BLIND lieferte 768 saubere Floats, pgvector rechnete Ähnlichkeiten, das Retrieval fand Treffer, jede Pipeline meldete Erfolg. Kein Bauteil hat gelogen. Das System als Ganzes war blind.

> Fehlerfrei laufen und richtig arbeiten sind zwei verschiedene Fragen. Wir haben bisher nur die erste gestellt.

Ein Log fängt, was sich als Fehler meldet. Es fängt nicht, was erfolgreich falsch ist.

**Lösung:** Ein täglicher Pixie-Agent, der prüft, ob die Grundfunktionen noch das TUN, was sie sollen — nicht, ob sie fehlerfrei laufen. Bekannte Eingaben, bekannte erwartete Ordnung, Alarm wenn sie kippt.

**Kandidaten für Vitalzeichen (Startmenge, erweiterbar):**

- **Embedding:** `embed("Hund") != embed("Katze")` — hätte den Bug in 1 Sekunde gefunden, an jedem einzelnen Tag der letzten 4 Monate. Dazu: `sim(bekanntes Paraphrasen-Paar) > sim(bekanntes Fremd-Paar)` mit Referenzpaaren aus der Kalibrierung Chat 107 (`lzg_knoten` 102 ↔ 103 → ~0.91 Paraphrase; 47 ↔ 83 → ~0.79 verschiedene Termine). Weicht ein Wert um mehr als 0.05 ab: Alarm.
- **Retrieval:** Ein bekannter Prompt findet seinen bekannten Knoten. Liefert `anker_retrieval` überhaupt noch Treffer, oder ist die Trefferzahl über Nacht auf null gefallen? **Bestätigt durch IVFFLAT-RECALL-KOLLAPS (bugs.md): genau dieses Vitalzeichen hätte den Kollaps gefangen — der Eintrag hier wurde drei Stunden VOR dem Vorfall geschrieben.** Referenz-Probe seit Chat 107: `anker_retrieval("Was weißt du über Lumi?")` muss die Lumi-Knoten (118/308/102, Cosine ~0.67–0.74) liefern.
- **Schreibpfade:** Ist in den letzten 24h überhaupt ein `lzg_knoten` entstanden? Ein Schreibpfad, der still versiegt, sieht aus wie ein ruhiger Tag.
- **Index-Recall (vierter Kandidat, aus IVFFLAT-RECALL-KOLLAPS):** Dieselbe bekannte Query einmal über den Standard-Lesepfad und einmal exakt (Seq-Scan bzw. `probes=lists`) — weichen die Treffermengen ab, frisst ein approximativer Index still Recall. Relevant, sobald ab ~10k Zeilen wieder ein Vektor-Index angelegt wird.

**Prinzip:** Der Agent misst OUTPUT-QUALITÄT, nicht Fehlerfreiheit. Er fragt nicht „lief es durch", sondern „kam das Richtige heraus". Bewusst kein Dashboard — ein Alarm, wenn ein Vitalzeichen kippt, mehr nicht. Angezeigt über denselben Draht wie LOG-TUERKLINGEL.

⚠ **Die Referenzwerte müssen NACH dem Re-Embedding neu erhoben werden.** Die oben genannten stammen aus der Kalibrierung im alten Raum bzw. der Vorabmessung mit v2-moe. Sie sind ein Muster, kein Sollwert.

**Zusammenhang:** EMBEDDING-CASING-BLIND (der Anlass) · LOG-TUERKLINGEL (die andere Hälfte: fängt Meldungen, nicht stille Fehlfunktion).

---

## Aufräumen: PROMOTION-NOVA-GUARD-TOT — Nova-Guard in der Cluster-Promotion feuert nie (Chat 108)

`agents/promotion/agent.py:698-700` prüft `if user_id == ASSISTANT_USER_ID: return 0` („Cluster-Promotion: Nova-Guard — uebersprungen"). Unter dem kanonischen Schema ist `user_id` immer `meister` — der Guard feuert nie. Er steht zudem nur in `_cluster_promotion`, fehlt im Einzel-Pfad desselben Agenten (`_eintrag_verarbeiten`), und im `SynapsenPromotionAgent` fehlt er ganz.

**Gemessen Chat 108 (25.07.2026, Audit A5):** `queue:nova` wird nie befüllt, `kzg:nova:meister:*` = 0 Keys von 926, `(nova, meister)` = 0 LZG-Zeilen. Novas 231 `beobachter='assistant'`-Knoten laufen über `queue:meister` und werden promotet — was korrekt ist (sie sind die Quelle für CHARAKTER-RESONANZ), aber **trotz**, nicht wegen des Guards.

**Gefahr:** Toter Code, der falsche Sicherheit suggeriert — wer ihn liest, hält Novas Perspektive für von der Promotion ausgenommen. Entfernen. ⬜ Prio niedrig

---

## Bug: CHARHASH-KZG-SCAN-UNSORTIERT — zwei von fünf Profilen destillieren aus 20 beliebigen KZG-Einträgen (Chat 108)

`agents/charakter/agent.py:359` liest KZG per `scan_iter(match=f"kzg:{user_id}:{character_id}:*", count=100)` und bricht nach `PIXIE_CHARAKTER_KZG_LIMIT = 20` Einträgen ab. **Keine Sortierung** — die Reihenfolge ist SCAN-Reihenfolge (Redis-interne Slot-Ordnung), das Limit kappt willkürlich.

**Gemessen Chat 108 (25.07.2026):** 926 KZG-Keys unter `kzg:meister:nova:*`. `adaptive_hash` und `beziehungsprofil` — zwei von fünf Profilen — werden aus 20 **beliebigen** von 926 Einträgen destilliert, nicht aus den 20 wichtigsten. Der LZG-Pfad sortiert korrekt nach `gewicht_absolut DESC` (`LIMIT 50`); der KZG-Pfad hat kein Äquivalent.

**Lösungsrichtung:** Salienz aus dem Hash lesen und vor dem Kappen sortieren, oder Limit deutlich anheben. ⬜ Prio mittel

---

## Aufräumen: HASH-DIRTY-KEY-OHNE-PAAR — `hash_dirty:meister` ohne character_id, kein Leser (Chat 108)

Redis enthält `hash_dirty:meister` ohne `character_id` (TTL `-1`), neben den korrekten `hash_dirty:meister:nova` und `hash_dirty:nova:meister`. Der CharakterAgent liest ausschließlich `hash_dirty:{user_id}:{character_id}` (`agent.py:95`) — der Key hat **keinen Leser**. Entweder Relikt aus der Zeit vor dem Paar-Schema oder ein aktiver Setzer, der die Konvention nicht kennt.

Klären, welcher der fünf auditierten Setzer ihn schreibt; dann entfernen oder auf das Paar-Schema umstellen (`novaberg-convention-paar-schema.md`). Gemessen Chat 108 (25.07.2026). Berührt CHARHASH-RESET-TRIGGER-FEHLT, Hypothese (b). ⬜ Prio niedrig

---

## Audit: AUDIT-HASH-DIRTY-SICHTBARKEIT — KEYS zeigt das Flag, der Agent sieht es nicht (Chat 108)

Aus CHARHASH-RESET-TRIGGER-FEHLT (`bugs.md`, Chat 108): `redis-cli KEYS` zeigte `hash_dirty:meister:nova`, der CharakterAgent meldete im selben Zeitraum neunmal „Kein hash_dirty". Zwei Hypothesen, beide ungeprüft — unbekannter Löschpfad, oder verschiedene Keyspaces.

**Audit-Auftrag:** (a) `agents/charakter/agent.py` — welcher Redis-Client, welches `db`, existiert ein Key-Prefix? Ist der `get`-Aufruf in ein `try/except` gehüllt, das `WRONGTYPE` schluckt? (b) `grep -rn "hash_dirty" novaberg/server/` auf **Löscher** (`delete`, `unlink`), nicht nur auf Setzer — fünf Setzer sind auditiert (Chat 108), nach Löschern wurde nie gesucht.

**Warum mittel:** Solange ungeklärt, kann der `charakter_hash` jederzeit wieder unbemerkt einfrieren. Berührt HASH-DIRTY-KEY-OHNE-PAAR (Hypothese b). ⬜ Prio mittel

---

## Landmine: TURN-ROH-VOR-KRAFT1-ENTWERTET — Sperrvermerk für die Verhaltensweisen-Destillation (Chat 105, Stichtag gemessen Chat 108)

Kein Defekt — heute liest niemand `turn_roh`. Gehört zu den Bau-Vorbedingungen von CHARAKTER-RESONANZ Bauteil 3. Aus der Übersichtstabelle in §7 hierher gehoben (Chat 108), dort bleibt eine Verweiszeile.

**Landmine — SPERRVERMERK für den Verdichtungs-Agenten.** Ohne Untergrenze läuft die Destillation *erfolgreich* und schreibt den Defekt als Charakterzug fest. Nichts meldet einen Fehler — Musterfall für VITALZEICHEN.

**Stichtag gemessen (Chat 108, 25.07.2026):** Wert und Konstanten-Vorschlag stehen in `novaberg-charakter-resonanz_k.md` §16 Bauteil 3 („Eine Wahrheit für den Stichtag", `TURN_ROH_STICHTAG_UTC`) — hier absichtlich nicht wiederholt, damit die Angabe nicht an zwei Stellen driftet.

**Der Anker ist nicht die Uhr, sondern die Signatur des Defekts:** Vor dem Stichtag ist `nova_emotion.emotions_vector` in allen Rohturns konstant `plateau`; ab dem Stichtag variiert er über fünf Werte (`plateau`, `eskalation`, `abkuehlung`, `aufbluehen`, `absturz`). Passt zum Fix-Commit `a5acc7d` (11.07., 12:29:05 UTC) plus Gesprächspause für Rebuild und Neustart.

**Konservativ gewählt:** Die drei Turns 12:39–12:43 liegen nach dem Deployment, sind aber `plateau` — ohne Beweis, dass Kraft 1 rechnete. Sie fallen mit heraus.

**Bestand (Stand 25.07.2026):** 150 Rohturns gesamt, 39 vor dem Stichtag (entwertet, **nicht löschen** — die Rohworte bleiben wertvoll), 111 danach verwertbar. Die frühere Angabe „40 vor ~12:38" war eine Schätzung und lag um eine Zeile daneben; die Menge vor dem Stichtag ist eingefroren und ändert sich nicht mehr.

**Anforderung:** Die Verhaltensweisen-Destillation (CHARAKTER-RESONANZ Bauteil 3, nicht „Teil 3") liest ausschließlich Turns ab dem Stichtag. Sonst destilliert sie den Defekt und schreibt ihn als Charakterzug fest. ⬜ Prio hoch

---

## Befund: PERMISSION-OHNE-BODEN — „Brudi ist read-only" ist Konvention, nicht erzwungen (Chat 109)

**Gemessen Chat 109 (Umgebungs-Audit, 25.07.2026, 11:47 UTC):** 203 `allow`-Einträge über drei Settings-Dateien (`~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`), **null `deny`, null `ask`, kein `defaultMode`**, und an keinem der drei üblichen Orte eine `managed-settings.json`. Die Permission-Konfiguration ist reines Allowlisting ohne Gegengewicht.

Claude Codes eigene Bash-Sandbox ist **nicht aktiv**: Der Bash-Prozess sitzt in exakt denselben Namespaces wie der `claude`-Prozess und wie der Flatpak-Init (identische `user`/`mnt`/`net`/`pid`/`ipc`-Inodes, `Seccomp_filters: 1`), und `bwrap` fehlt im Flatpak-Runtime — das Werkzeug, mit dem diese Sandbox auf Linux gebaut würde, ist nicht vorhanden. Die einzige messbare Isolation kommt vom VS-Code-Flatpak (`com.visualstudio.code`), und der läuft mit `filesystems=host` plus `org.freedesktop.Flatpak=talk` — also mit Host-Dateisystem und der Berechtigung für `flatpak-spawn --host`.

**Auswirkung:** Dass ein Audit-Auftrag „READ-ONLY" nur liest, ist eine Zusage im Prompt, keine erzwungene Eigenschaft der Umgebung. Es gibt keine technische Schranke, die einen Schreibzugriff oder einen Host-Ausbruch verhindert; es gibt nur die Absprache. Wer das für eine Sandbox hält, verlässt sich auf etwas, das nicht existiert. ⬜ Prio mittel

**Zusammenhang:** ALLOWLIST-DRIFT (die Liste wächst nur, niemand räumt sie).

---

## Bug: PROMO-KZG-KEY-ALS-TURN-ID — `pipeline_log.turn_id` trägt bei Promotion-Zeilen KZG-Keys (Chat 109)

`agents/synapsen_promotion/agent.py:178-179` ruft `pipeline_log.span_start(turn_id=kzg_key, …)` — der KZG-Redis-Key wird als `turn_id` eingesetzt, weil die Queue-Nutzlast keine echte `turn_id` mitführt (`queues_befuellen` in `agents/kzg/queues.py` pusht `aufgabe`, `user_id`, `key`, `salienz`, `themen`, `dimension` — **kein `turn_id`**).

**Folge:** In der Spalte `pipeline_log.turn_id` stehen bei Promotion-Einträgen Werte der Form `kzg:{user_id}:{character_id}:{ms-timestamp}` neben echten UUID4-Hex-Turn-IDs. Jede Auswertung über `turn_id` — Korrelation eines Turns über alle Nodes, Join, `GROUP BY` — mischt zwei Wertebereiche in einer Spalte. Ein Promotion-Span ist damit keinem Turn zuzuordnen, und ein `WHERE turn_id = …` über echte Turn-IDs übersieht ihn stillschweigend.

**Trifft CHARAKTER-RESONANZ Bauteil 2 (Backfill) unmittelbar:** Wer die `verbindung`-Zeilen über `turn_id` an die Rohturns knüpft, muss diese Fremdwerte vorher erkennen; sie sehen nicht nach Fehler aus, sondern nach einem Turn, den es nie gab. Audit Chat 109 (25.07.2026). ⬜ Prio mittel

**Zusammenhang:** KZG-TURN-ID-UNBEKANNT (dieselbe Lücke von der anderen Seite) · PIPELINE-LOG-BACKFILL-PAAR (Alt-Forensik ohne Paar-Schlüssel).

---

## Aufräumen: ALLOWLIST-DRIFT — die Claude-Code-Allowlist wächst nur (Chat 109)

Die Permission-Allowlist kennt nur Zuwachs: Einzelfall-Einträge aus längst abgeschlossenen Sprints stehen weiter drin, darunter ein `docker cp` mit dem konkreten Pfad einer Magneten-Migration (`/tmp/m2_magneten_migration.sql`) und mehrere `python -c "import ast; ast.parse(open('…'))"`-Zeilen auf Dateien, die seit dem jeweiligen Sprint nicht mehr angefasst wurden.

Ein Einzelfall-Eintrag, der seinen Anlass überlebt, ist eine dauerhaft offene Tür ohne Grund. Braucht einen Aufräum-Durchgang **mit Messdatum** — also: Bestand zählen, Einträge einer laufenden Aufgabe zuordnen, Rest streichen, Zahl vor/nach protokollieren. Beobachtet Chat 109 (25.07.2026). ⬜ Prio niedrig

**Zusammenhang:** PERMISSION-OHNE-BODEN (kein `deny`, kein `defaultMode` — die Liste ist die einzige Kontrollfläche).

---

## Performance: KZG-VERSTAERKUNG-KEYS-SCAN — Vollscan der Paar-Partition bei jedem KZG-Write (Chat 109)

`agents/kzg/speicher.py:180` ruft `redis_client.keys(f"{prefix}*")` in `_thematisch_verstaerken` — ein **blockierender** Vollscan über alle KZG-Keys des Paares, bei **jedem** KZG-Write. Da der Dispatcher pro Konversations-Turn zweimal läuft (HumanGraph und CharacterGraph, je ein `dispatch_kzg`) und je Lauf ein Write pro Salienz-Segment entsteht, sind das **2 × n Vollscans pro Turn**. Anschließend folgt pro gefundenem Key ein `hget` auf `themen` (`speicher.py:191`) und bei Overlap drei weitere Feld-Zugriffe.

Gemessener Bezugswert aus dem Nachbar-Befund: 926 Keys unter `kzg:meister:nova:*` (Chat 108). Bei einem Segment pro Lauf sind das zwei Vollscans über 926 Keys je Turn, plus je ein `hget` pro Key.

**Gleicher Mechanismus wie CHARHASH-KZG-SCAN-UNSORTIERT** — dort `scan_iter` mit willkürlichem Limit, hier `keys()` ohne Limit. Beide behandeln die Paar-Partition als kleine Menge. Der Legacy-Zwilling `memory/kzg.py:402` hat denselben Aufruf. Audit Chat 109 (25.07.2026, Quelltext-Audit — Laufzeit nicht gemessen). ⬜ Prio niedrig

---

## Nacharbeit: KZG-TURN-ID-UNBEKANNT — Platzhalter statt Turn-Bezug im KZG-Schreib-Log (Chat 109)

`agents/kzg/speicher.py:331-347` schreibt `log_db_write(turn_id = turn_id or "kzg-unbekannt", …)`; der Legacy-Zwilling `memory/kzg.py:346` verwendet analog `turn_id or "kzg-store-unbekannt"`. Fällt die `turn_id` leer herein — bei Legacy-Aufrufern ohne Turn-Kontext (Recherche-Agent, Shadow) der Normalfall —, landet der Platzhalter in der Spalte.

**Folge:** Diese `db_write`-Zeilen tragen den KZG-Key im JSONB (`inhalt->>'kzg_key'`), aber keinen Turn-Bezug. Sie sind beim Backfill nicht zuordenbar — genau die Zeilen, über die man einen KZG-Eintrag sonst an seinen Turn knüpfen könnte, fallen aus.

**Anzahl ungemessen.** Eine Zählung (`WHERE turn_id LIKE '%-unbekannt'` gruppiert nach `node`) steht aus und gehört vor den Backfill. Audit Chat 109 (25.07.2026). ⬜ Prio niedrig

**Zusammenhang:** PROMO-KZG-KEY-ALS-TURN-ID (dieselbe Spalte, umgekehrter Fehler: dort ein fremder Wert, hier ein Platzhalter).

---

## Befund: TURN-ROH-HG-SKIP — der übersprungene Rohturn pro Turn ist planmäßig; Zahl gemessen (Chat 109)

**Widerlegt (Quelltext-Audit Chat 109, 25.07.2026):** Die übersprungenen `turn_roh` sind **kein Defektsignal.** Bedingung 4 des Guards (`graph/nodes/dispatcher.py:297-300`, `if not response:` → „turn_roh uebersprungen — keine Nova-Antwort (response leer)") trifft im HumanGraph-Lauf **strukturell immer** zu: `create_state` initialisiert `response = ""` (`graph/base.py:144`), und der HumanGraph hat überhaupt keinen Responder — seine fünf Nodes sind `perzeption`, `enricher`, `ei_calc`, `salience`, `dispatcher` (`graph/human_graph.py:39-43`, Docstring :5-6: „Kein Responder — der Charakter antwortet separat über den CharacterGraph"). Alle Zuweisungen an `state["response"]` liegen im CharacterGraph (`responder.py:617`, `corrector.py:80`, `thinker.py:597/599/636`, `character_graph.py:165`).

Da der Dispatcher pro Konversations-Turn **zweimal** läuft — beide Graphen enden auf ihm (`human_graph.py:50-51`, `character_graph.py:122-123`) —, wird **pro Turn planmäßig genau ein `turn_roh` übersprungen** (der Pfad-1-Lauf) und genau einer geschrieben (der Pfad-2-Lauf). Das deckt sich mit „genau eine `turn_roh`-Zeile je Turn" in `novaberg-charakter-resonanz_k.md` §5 (Die drei Pfade).

**Zahl beantwortet — Chat 109 (26.07.2026, Container-Lauf ab 08:31, ein Gespräch):** ~~Strukturell wäre je Rohturn ein Skip zu erwarten, bei 150 Rohturns also ~150 Warnungen. Beobachtet wurden 2. Die Differenz ist unerklärt.~~ → Die Differenz war ein **Fenster-Artefakt**, keine Lücke: Im gemessenen Lauf stehen **4 Skips**, jeder ~100 ms nach seinem `dispatch_kzg`-Lauf. Drei gehören zu `rolle=user` (HumanGraph, planmäßig), einer zum Pixie-Lauf (siehe PIXIE-TURN-ID-LEER). Der Mechanismus ist damit live bestätigt; die frühere „2" stammte aus einem kleineren Beobachtungsfenster. Die drei vermuteten Richtungen (Log-Rotation, Log-Level, äußerer `writes`-Guard `dispatcher.py:350-356`) brauchen keine Prüfung mehr.

**Kein Bug.** Die Warnung ist der planmäßige Begleiter jedes Turns — zu wissen, bevor jemand sie als Fehlersignal liest oder aus ihrer Seltenheit auf einen intakten Pfad schließt. ⬜ Prio niedrig — kein Defekt, Mechanismus und Zahl belegt

**Zusammenhang:** PIXIE-SELBSTTRIGGER-KEIN-TURN-ROH (der andere Fall ohne Paar) · TURN-ROH-VOR-KRAFT1-ENTWERTET (Bestandszahl 150) · SILENT-SKIP-EI-DEFAULTS (nennt den `turn_roh`-Guard als eine der zwei lauten Lesestellen).

---

## Bug: KZG-SALIENZ-BOOST-OHNE-DECKEL — die thematische Verstärkung hebt die Salienz über ihren Wertebereich (Chat 109)

Die Bewertung selbst ist gesund: Der Salienz-Node liefert Werte in **0.0–1.0**, wie `novaberg-node-salience.md` sie an zwei Stellen dokumentiert (:15 als kognitionswissenschaftliche Analogie, :80 als Dimension 3 „Float 0.0–1.0"). Die **thematische Verstärkung** hält diesen Bereich nicht ein — sie addiert den gedämpften Boost auf den Bestandswert, und gedämpft wird gegen `KZG_SALIENZ_CAP = 10.0` (`config.py:207`), nicht gegen 1.0. Die Wand steht also eine Größenordnung über der Skala, auf der bewertet wird.

**Gemessen Chat 109 (Live-Redis, 26.07.2026, Partition `kzg:meister:nova:*`, 775 Keys):** **527 von 775 Einträgen (68 %) liegen über 1.0.**

```
Eimer (gerundet):    0:7 · 1:406 · 2:164 · 3:74 · 4:37 · 5:24
                     6:13 · 7:10 · 8:10 · 9:9 · 10:21
MAX 10.002
```

Der oberste Eimer ist mit 21 Einträgen **dicker** als die drei darunter (9, 10, 10). Das ist ein Stau an einer Wand, kein auslaufender Verteilungsschwanz.

**Korrelation mit `haeufigkeit` eindeutig:** Unter 1.0 liegen überwiegend Einträge mit `haeufigkeit = 1` (167); in den Top 20 findet sich kein einziger Eintrag über 1.0 mit `haeufigkeit = 1`. Über 1.0 beginnt bei `haeufigkeit = 2` (76) und reicht bis `haeufigkeit = 43`. Die Höhe kommt aus der Verstärkung, nicht aus der Bewertung.

**Live-Beleg am einzelnen Eintrag:** `kzg:meister:nova:1785055109755`, angelegt 08:38:29 mit Salienz **0.700** — belegt über `trigger_salienz = 0.700` der Promotion 19 s später und `roh = 0.700` des daraus entstandenen `lzg_knoten` id=496. Beim Auslesen wenige Minuten später: **1.3958**. Selbstverstärkung ist ausgeschlossen — der Key erscheint im Log in keiner Verstärkungszeile.

**Folge — sämtliche KZG-Tore sind für zwei Drittel des Korpus wirkungslos.** `KZG_SALIENZ_MINIMUM` 0.3, `MID` 0.5, `HIGH` 0.7 und die Promotions-Schwelle 0.8 liegen alle unterhalb des Bereichs, in dem 68 % der Einträge stehen; nur **7 von 775** liegen unter 0.5. Ein einziger Boost genügt, damit ein Eintrag alle Gates dauerhaft passiert. Live bestätigt: In sieben `dispatch_kzg`-Läufen eines echten Gesprächs am 26.07. gab es **null** Ablehnungen.

**Ort:** `_gedaempfter_boost`, wortgleich doppelt in `memory/kzg.py:229` und `agents/kzg/speicher.py:134` — ein Fix muss beide treffen, siehe REFAC-KZG-CODE-DUPLIKAT. Die Formel selbst ist nicht nachgerechnet; die **Reparaturrichtung ist offen** (Deckel auf die Summe, Dämpfung gegen 1.0 statt gegen den CAP, oder die Skala bewusst auf 0..10 umdefinieren und die Doku nachziehen). ⬜ Prio hoch

**Zusammenhang:** KZG-GEWICHT-ABSOLUT-CEILING (Abnehmer der Kette — „Knoten werden oben geboren") · KZG-SALIENZ-GRENZWERT-UNKLAR (ohne Deckel gegenstandslos) · KZG-VERSTAERKUNG-KEYS-SCAN (dieselbe Verstärkungsschleife) · REFAC-KZG-CODE-DUPLIKAT.

---

## Bug: DESTILLAT-SUBJEKT-SCHABLONE — der Verdichter erfindet „Der Nutzer" bei null Nutzer-Input (Chat 109)

Ergänzt DESTILLAT-PERSPEKTIVE-VS-SUBJEKT (Chat 103/108) und **korrigiert dessen Ursachensatz.**

**Live-Beleg Chat 109 (26.07.2026),** `kzg:meister:nova:1785055109755`, `beobachter=assistant`:

```
inhalt: "Der Nutzer erinnert an den vor zehn Tagen besprochenen
         Synapsen-Migrationsplan P1-P10. …"
```

Der Turn war **Pixie-initiiert.** Es gab in diesem Turn **keinen Nutzer-Input** — Nova hat unaufgefordert erinnert („ich wollte dich nur kurz an … erinnern"). Der Verdichter hat einen Nutzer als Subjekt **erfunden** und Novas eigene Handlung ihm zugeschrieben.

**Ursache korrigiert:** DESTILLAT-PERSPEKTIVE-VS-SUBJEKT nennt seit Chat 108 als Ursache „die Quelle, nicht der Prompt" — kein Prompt könne eine Stimme rekonstruieren, die im Eingabetext nicht vorkommt. Für den Verdichter ist das hiermit widerlegt: Bei null Nutzer-Input steht „Der Nutzer" trotzdem da. Die Perspektivverdrehung ist an dieser Stelle **kein Materialproblem, sondern eine Schablone** — der Verdichter (`agents/kzg/verdichtung.py`; Prompt-Text nicht gelesen) setzt den Nutzer als Subjekt, unabhängig davon, wer gesprochen hat.

**Folge für CHARAKTER-RESONANZ Bauteil 2:** Ein Backfill über die 111 verwertbaren Rohturns **reproduziert die Verdrehung**, solange der Verdichter das Subjekt nicht aus `beobachter` ableitet. Die Schablone würde in die neue Quelle geschrieben, aus der Novas Charakter entsteht. ⬜ Prio hoch

**Zusammenhang:** DESTILLAT-PERSPEKTIVE-VS-SUBJEKT (dort steht der widerlegte Ursachensatz Chat 108 noch unmarkiert) · PIXIE-SELBSTTRIGGER-KEIN-TURN-ROH und PIXIE-TURN-ID-LEER (derselbe Pixie-Lauf) · TRIB-PERSON-DRIFT.

**Status: Behoben Chat 110 — nachgetragen Chat 112.** Der Eintrag trug bis dahin **gar keine Statuszeile**, obwohl die Reparatur zwei Chats zurücklag: `_build_verdichtung_prompt(beobachter, graph_rolle)` wählt einen von drei Aufgaben-Blöcken (`kzg_verdichtung.task` / `.assistant_task` / `.impuls_task`), jeder mit Few-Shot-Beispielen in seiner Person und Lage. Ein Eintrag ohne Status liest sich wie ein offener — und dieser wurde in `novaberg-charakter-resonanz_k.md` §16 zweimal als Voraussetzung geführt.

**Die Klasse hat sich anschließend wiederholt.** Chat 112 fand denselben Defekt eine Ebene höher im Salienz-Node (`SALIENZ-PROMPT-NUTZER-SCHABLONE`): dort war es nicht der Verdichter, sondern die Bewertung, und die Anweisung war nicht nur unpassend, sondern invertiert. Beide Male half dasselbe Mittel — drei Aufgaben-Blöcke statt eines mit Ausnahmeregeln.

---

## Bug: PIXIE-TURN-ID-LEER — Pixie-initiierter CharacterGraph-Lauf schreibt KZG ohne `turn_id` (Chat 109)

**Gemessen Chat 109 (26.07.2026, 08:38:29):** Ein Pixie-initiierter CharacterGraph-Lauf (`rolle=character`) legte einen KZG-Eintrag an und verstärkte vier weitere — mit **leerem `turn_id`**. Log-Zeile wörtlich:

```
KZG-Dispatch: Keys eingesammelt — turn_id=, beobachter=assistant,
1 neue Keys, 4 verstaerkte Keys
```

**Verstoß gegen den beschlossenen Entwurf:** `novaberg-thinking-task-orchestration_k.md:323` führt `pixie_delivery` als gleichberechtigten Trigger-Typ neben `user_prompt`, `nova_self` und `nova_rueckfrage`; :95 verlangt für **jeden** Graph-Auftrag den vollständigen CharacterGraph bis Salienz und Dispatcher. Ein Pixie-initiierter Lauf **ist** ein Turn und muss eine `turn_id` tragen. Der `/chat`-Pfad erzeugt sie (`api/chat.py:134`) und reicht sie über das Event-Payload weiter (`services/event_consumer.py:408`) — der Pixie-Pfad hat kein Äquivalent.

**Blocker für CHARAKTER-RESONANZ Bauteil 1b:** `verbindung.turn_id` soll NOT NULL sein. Ohne Fix scheitert **jeder** Pixie-Lauf beim Schreiben der Verbindungs-Zeile. ⬜ Prio hoch

**Berührt PIXIE-SELBSTTRIGGER-KEIN-TURN-ROH:** Derselbe Lauf übersprang `turn_roh`, weil `response` beim Dispatcher leer war — der vierte von vier Skips im gemessenen Gespräch (siehe TURN-ROH-HG-SKIP). Der KZG-Eintragsinhalt war jedoch **gefüllt** und gibt Novas Nachricht korrekt wieder: Der Text lag also vor, nur nicht in `state["response"]`.

**Offene Frage, ausdrücklich keine Antwort:** Woher der Bewertungstext auf diesem Pfad stammt, wenn `graph/nodes/salience.py` (Input-Switch in `analyze`) bei `rolle=character` genau `state["response"]` als Bewertungsobjekt liest. Ungeprüft.

**Nachtrag Chat 112 — die Frage steht weiter offen, ist aber jetzt in einer Messung zu beantworten.** Zwei Dinge haben sich seit ihrer Formulierung geändert, beide in ihre Richtung:

- **Der Switch hängt seit Chat 110 an `graph_rolle` statt an `ei_calc_rolle`.** Zum Messzeitpunkt lief der AgentGraph als `"character"` mit und landete dadurch im Reaktions-Zweig — er las `state["response"]`, die er nie erzeugt. Ob der gemessene Lauf der AgentGraph oder der CharacterGraph war, entscheidet die Antwort und ist aus dem damaligen Log nicht mehr herauszulesen: Beide trugen dieselbe `quelle`.
- **Ein leeres Bewertungsobjekt bricht seit Chat 110 laut ab** und schreibt seit Chat 111 eine `fehler`-Zeile ins `pipeline_log`. Der stille Fall, in dem die Frage entstand, kann sich nicht wiederholen, ohne sich zu melden.

**Wie sie zu beantworten ist:** Eine Zustellung auslösen und im `pipeline_log` die `switch`-Zeilen des Turns lesen. Sie tragen `graph_rolle`, `bewertungs_laenge` und `lagebild_laenge` je Lauf — damit ist ohne Rekonstruktion sichtbar, welcher Graph welchen Text bewertet hat. Zwei `switch`-Zeilen mit derselben `turn_id` heißen: beide Graphen liefen, und die Zuordnung ist eindeutig.

---

## Bug: KZG-SALIENZ-SKALENBRUCH — die Dämpfung ist auf CAP 10.0 kalibriert, die Skala geht bis 1.0 (Chat 109)

Nennt den Mechanismus hinter KZG-SALIENZ-BOOST-OHNE-DECKEL und rechnet die Formel nach, die dort ausdrücklich offen blieb.

**Formel wörtlich** (`memory/kzg.py:229-249` und `agents/kzg/speicher.py:134-154` — Funktionskörper per `diff` als byte-identisch verifiziert, nur die Kommentarbanner drumherum unterscheiden sich):

```
remaining = max(0.0, CAP - alte_salienz)
ratio     = remaining / CAP
daempfung = sin(ratio * pi/2) ** EXP
effektiv  = raw_boost * daempfung
```

`CAP = 10.0`, `EXP = 0.6` (`config.py:207-208`), `raw_boost = salienz / 2.0` (`KZG_VERSTAERKUNG_DIVISOR`, `config.py:864`).

**Der Bruch:** `salienz` lebt auf 0.0–1.0, die Dämpfungskurve ist über 0–10 gespannt. Im gesamten Entscheidungsbereich ist die Funktion praktisch die Identität:

```
alte_salienz 0.30  →  Dämpfung 0.99933
alte_salienz 0.70  →  Dämpfung 0.99637
alte_salienz 1.00  →  Dämpfung 0.99259
```

Der Docstring sagt „verhindert Salienz-Explosion". Sie dämpft dort, wo TTL- und Promotions-Entscheidungen fallen, um **unter 1 %**.

**Gemessen Chat 109 (Live-Redis, 26.07.2026, Partition `kzg:meister:nova:*`)** — 10 am 26.07. neu angelegte Einträge, Zeitstempel im Schlüsselnamen, alle deckungsgleich mit `erstellt_am`:

```
haeufigkeit=1:  0.7 · 0.7 · 0.7 · 0.7 · 0.4 · 0.4        (runde Werte)
haeufigkeit=2:  0.949067183610147 · 0.849352240389
haeufigkeit=3:  1.098081464380 · 1.395879534625921
```

Runde Werte bei `haeufigkeit = 1`, lange Nachkommastellen ab 2: **Die Bewertung ist gesund, der Boost verlässt die Skala.** Zwei Verstärkungen genügen.

**Korpusweit (dieselbe Messreihe wie KZG-SALIENZ-BOOST-OHNE-DECKEL, nicht eine zweite Messung):** 527 von 775 Einträgen über 1.0 (68 %), Verteilung gerundet `0:7 · 1:406 · 2:164 · 3:74 · 4:37 · 5:24 · 6:13 · 7:10 · 8:10 · 9:9 · 10:21`, MAX 10.002. Der oberste Eimer ist **dicker** als die drei darunter — Stau an einer Wand, kein Verteilungsschwanz. Die Korrelation mit `haeufigkeit` ist eindeutig: kein Eintrag über 1.0 bei `haeufigkeit = 1` in den Top 20; über 1.0 beginnt bei `haeufigkeit = 2` und reicht bis `haeufigkeit = 43`.

**Folge:** Alle KZG-Tore sind für zwei Drittel des Korpus wirkungslos — `MINIMUM` 0.3, `MID` 0.5, `HIGH` 0.7, Promotion 0.8. Nur **7 von 775** liegen unter 0.5. Live bestätigt: sieben `dispatch_kzg`-Läufe eines echten Gesprächs am 26.07., **null** Ablehnungen.

**Bauart-Fehler (Brudi-Audit Chat 109):** Die Formel dämpft ein **Inkrement** und schreibt das Ergebnis in dasselbe Feld zurück, aus dem `alte_salienz` gelesen wurde. Kein Ankerfeld → nicht idempotent, pfadabhängig. **Dieselbe Klasse wie ZIEL-DECAY-FORMEL-KUMULATIV.** Ein Deckel allein repariert das nicht; die Bauart muss sich ändern (→ Sprint KZG-SALIENZ-NEUBAU). ⬜ Prio hoch

**Zusammenhang:** KZG-SALIENZ-BOOST-OHNE-DECKEL (dort das Symptom und die Korpusverteilung; dort steht noch „Die Formel selbst ist nicht nachgerechnet" — mit diesem Eintrag überholt) · ZIEL-DECAY-FORMEL-KUMULATIV (gleiche Fehlerklasse) · KZG-KEIN-DECAY · KZG-SALIENZ-KONSUMENTEN-DISSENS · KZG-GEWICHT-ABSOLUT-CEILING (Abnehmer) · REFAC-KZG-CODE-DUPLIKAT (ein Fix muss beide Kopien treffen) · Sprint KZG-SALIENZ-NEUBAU.

---

## Limitation: KZG-TTL-UNSTERBLICH — die Auffrischung kann nur verlängern, nie herabsetzen (Chat 109)

**Einordnung korrigiert (Chat 109):** ~~Bug~~ → **kein eigenständiger Defekt, sondern eine Limitation** — und die **Folge von PROMOTION-ENTFERNT-KZG-NICHT.** Das `max()` in der Auffrischung ist für sich genommen richtig: Eine schwache Wiederholung soll einen hoch eingestuften Eintrag nicht herabstufen. Schädlich wird es erst, weil die Einträge das KZG überhaupt nie verlassen.

`novaberg-mem-kzg.md:169` setzt bei thematischer Verstärkung `TTL = max(verbleibend, neuer_TTL)`. **Jede Berührung verlängert.** Damit verfallen ausgerechnet die Einträge nicht, die über die Skala laufen — wer oft verstärkt wird, wird oft aufgefrischt.

**Gemessen Chat 109 (Live-Redis, 26.07.2026, Partition `kzg:meister:nova:*`, 777 Keys):** **137 von 777 sind älter als 30 Tage (17,6 %)**, der älteste **104,5 Tage** — das **3,5-fache der maximalen TTL** (`KZG_TTL_HIGH_SEKUNDEN` = 30 Tage). Berechnet aus dem Millisekunden-Zeitstempel im Schlüsselnamen; dessen Übereinstimmung mit `erstellt_am` ist an 10 Einträgen geprüft.

Das KZG ist damit für ein Sechstel seines Inhalts kein Kurzzeitgedächtnis mehr — `novaberg-mem-kzg.md:13` beschreibt es als „schneller, flüchtiger Speicher … über Tage und Wochen". ~~⬜ Prio hoch~~ → **⬜ Prio mittel** (herabgestuft Chat 109): Die Limitation hat keinen eigenen Fix, sondern erledigt sich voraussichtlich mit PROMOTION-ENTFERNT-KZG-NICHT — eigene hohe Prio wäre doppelte Arbeit an derselben Ursache. **Der Vorbehalt bleibt:** „voraussichtlich" ist kein Messergebnis; bestätigt sich das beim Nachmessen nicht, gehört der Punkt zurück auf hoch.

**~~Offen, ausdrücklich NICHT beantwortet:~~ ✅ Beantwortet Chat 109 — nein, sie entfernt ihn nicht.** ~~Entfernt die Promotion den Eintrag aus dem KZG?~~ 527 Einträge liegen über der Promotionsschwelle 0.8 und sind **alle noch vorhanden** — ~~das spricht dagegen, ist aber nicht gemessen~~ → **am Einzelfall belegt: PROMOTION-ENTFERNT-KZG-NICHT** (Knoten id=496, Quell-Key 51 Minuten nach der Promotion unverändert in Redis). Der Vollabgleich aller KZG-Keys gegen `lzg_knoten` steht weiterhin aus; die Spalte dafür zuerst im `\d` verifizieren, nicht aus Log-Zeilen übernehmen.

**Warum das die Zahlen erklärt.** Würde ein Eintrag das KZG bei der Promotion verlassen, **könnte keiner auf Salienz 10 und `haeufigkeit` 43 klettern — er wäre vorher weg.** Die 137 Einträge über 30 Tage und die 21 im Stau bei Salienz 10 (Verteilung in KZG-SALIENZ-BOOST-OHNE-DECKEL) sind **genau die, die nie gegangen sind**. Der TTL ist nicht der Mechanismus, der versagt; er wird nur nie zuständig.

**Erwartung — nachmessen, nicht annehmen.** ~~**Wird von KZG-SALIENZ-NEUBAU NICHT repariert.** … vierter, eigener Hebel.~~ Der Neubau repariert den Punkt weiterhin nicht; der Hebel ist aber **nicht** der TTL, sondern **PROMOTION-ENTFERNT-KZG-NICHT**. Nach dessen Fix erledigt sich diese Limitation **vermutlich von selbst**. **Vor dem Schließen nachmessen** — Altersverteilung und Salienz-Verteilung erneut erheben und gegen die Werte oben stellen. Ein „erledigt sich vermutlich" ist kein Messergebnis.

**Zusammenhang:** PROMOTION-ENTFERNT-KZG-NICHT (**Ursache** — diese Limitation ist deren Folge) · KZG-SALIENZ-SKALENBRUCH (liefert die Einträge, die nie mehr verfallen) · KZG-KEIN-DECAY (die andere fehlende Abwärtsbewegung) · Sprint KZG-SALIENZ-NEUBAU (repariert diesen Punkt bewusst nicht).

---

## Bug: KZG-KEIN-DECAY — die Salienz kennt keine Abwärtsbewegung (Chat 109)

**Kein Schreiber senkt `salienz` jemals** (Brudi-Audit Chat 109, musterbasierte Suche über den ganzen Baum: Zuweisungen, `hset`-Mappings, SQL-`UPDATE`). Die einzige Abwärtsbewegung ist Key-Expiry — und die ist durch KZG-TTL-UNSTERBLICH für die stark verstärkten Einträge faktisch abgeschaltet.

**Doku widerlegt:** `novaberg-kzg-liberalisierung_k.md` §3.6 („KZG-Salienz als Analogon zum LZG-Gewicht", :76-77) behauptet: „Beide steigen bei Wiederholung, **beide fallen bei Stillstand**." Die zweite Hälfte hat keine Entsprechung im Code. Der Satz gehört an seiner Stelle als widerlegt markiert — **steht noch unmarkiert**, weil der Auftrag Chat 109 auf diese Datei beschränkt war.

**Das LZG hat, was dem KZG fehlt:** `LZG_KNOTEN_DECAY_RATE = 0.0015` (`config.py:1127`), `LZG_KNOTEN_MIN_GEWICHT = 0.1` (`config.py:1131`), täglicher `synapsen_decay`-Agent. Das KZG hat kein Äquivalent. ⬜ Prio mittel

**Warum ohne Decay eine Ratsche entsteht statt eines Gleichgewichts (Rechnung Chat 109, Näherung).** Der Boost ist `salienz / 2` mit einer Dämpfung, die im Betriebsbereich praktisch 1 ist (KZG-SALIENZ-SKALENBRUCH). Damit gilt näherungsweise **neu = alt × 1.5 je Verstärkung**:

```
Start 0.4  →  0.60  →  0.90     zwei Verstärkungen bis über 0.8
Start 0.5  →  0.75  →  1.13     zwei
Start 0.7  →  1.05              eine
```

**Als Näherung gekennzeichnet:** Der eingehende Boost ist die Salienz des **neuen** Turns, nicht die des bestehenden Eintrags — die Rechnung nimmt vereinfachend beide gleich an. Der Trend stimmt, die Einzelwerte sind keine Vorhersage.

Belegt in der Zehner-Stichprobe (KZG-SALIENZ-SKALENBRUCH): `haeufigkeit = 2` → 0.849 / 0.949, `haeufigkeit = 3` → 1.098 / 1.396.

**Das Zeitfenster wächst mit.** Ein Eintrag bei 0.4 hat 7 Tage TTL; eine Verstärkung hebt ihn auf 0.6 und damit auf 14 Tage. Die Frist verlängert sich mit jeder Berührung. Ohne Decay läuft das Rennen zwischen **Berührungsrate** und **Verfallsrate** nur in eine Richtung. Mit Decay rutscht ein ruhender Eintrag in eine kürzere Stufe zurück und muss die Verstärkungen erneut sammeln — erst dann ist es ein Gleichgewicht statt einer Ratsche.

**Entscheidung Meister (Chat 109): Decay kommt.** Der Aufwand ist unter der Anker-Bauart nahe null — Decay ist ein **weiteres Argument derselben reinen Funktion**, kein eigener Job:

```
salienz = daempfung(salienz_roh) · exp(-RATE · tage_seit(verstaerkt_am))
```

Dieser Eintrag geht **nicht** im Sprint auf: Er hält fest, **warum**. Der Sprint (KZG-SALIENZ-NEUBAU Teil c) setzt um.

**Klarstellung — das KZG kennt kein `aktiv`-Flag und keine Reaktivierung.** Der Hash trägt 21 Felder, **keines davon `aktiv` oder `geloescht`** (`hkeys`, Chat 109). Beim TTL-Ablauf entfernt Redis den Key **vollständig**; es gibt keinen inaktiven Zwischenzustand, aus dem etwas zurückgeholt werden könnte. Das `aktiv = FALSE`-Verhalten mit Halb-Reaktivierung gehört zu `lzg_knoten`, **nicht** zum KZG. Wer die LZG-Mechanik hierher überträgt, sucht einen Schalter, den es nicht gibt.

**Zusammenhang:** KZG-SALIENZ-SKALENBRUCH (nur aufwärts, und aufwärts ungebremst) · KZG-TTL-UNSTERBLICH (auch der Ersatz-Mechanismus greift nicht) · PROMOTION-ENTFERNT-KZG-NICHT (dritte fehlende Abwärtsbewegung — der Eintrag geht nicht einmal beim Umzug) · Sprint KZG-SALIENZ-NEUBAU Teil (c).

---

## Bug: KZG-SALIENZ-KONSUMENTEN-DISSENS — drei Leser, drei Annahmen über dieselbe Zahl (Chat 109)

| Ort | Annahme |
|---|---|
| `agents/synapsen_promotion/agent.py:17`, `:253` | dokumentiert Skala **0..10** |
| `agents/promotion/agent.py:322` | `min(salienz, 1.0)` — klemmt **still** |
| `ei/gravitation.py:333` | **ungeklemmt**, multiplikativ als `gewicht` |

**Der dritte ist der Schaden:** Ein Eintrag mit Salienz 3 zieht dreifach im **Lesepfad** — also in dem, was Nova im Prompt sieht. Die Klemme in `promotion` verbirgt das Problem an einer Stelle und lässt es an der anderen voll durch. Zwei Konsumenten schweigen über ihre Annahme, einer dokumentiert die falsche.

Solange KZG-SALIENZ-SKALENBRUCH offen ist, ist keine der drei Annahmen richtig — es gibt keine verbindliche Skala, auf die man sich einigen könnte. Der Dissens ist deshalb kein eigenständiger Fix, sondern eine **Abnahmebedingung** des Neubaus: nach (b) muss jeder der drei Leser auf dieselbe, dann tatsächlich eingehaltene Skala zeigen. ⬜ Prio hoch

**Entscheidung Meister (Chat 109) — Sofortfix für `gravitation`.** `ei/gravitation.py` darf die Salienz **nicht ungeklemmt** als multiplikatives Gewicht nehmen. Das ist ein klarer Fehler und wartet nicht auf den Neubau: Die Zahl geht dort ungefiltert in den Lesepfad, also in das, was Nova im Prompt sieht.

**Vermerk zum Neubau — den Cap nicht wieder entfernen.** Sobald KZG-SALIENZ-NEUBAU die Salienz zu einer **hart gekappten reinen Funktion** macht, werden alle drei Konsumenten von selbst einig; die Klemme in `gravitation` wird dann rechnerisch wirkungslos. **Richtig bleibt sie trotzdem** — sie ist die Zusicherung des Lesers an sich selbst, nicht ein Pflaster über den Schreiber. Beim Neubau nicht vergessen und **nicht als überflüssig zurückbauen**.

**Stand der Abnahmebedingung nach dem Neubau (geprüft 29.07.2026, Chat 117) — zwei von drei.** Der Neubau ist am 28.07.2026 gelaufen, die Skala ist einheitlich [0,1] und hart gekappt. Damit ist die Bedingung „jeder der drei Leser zeigt auf dieselbe, dann tatsächlich eingehaltene Skala" für die Skala erfüllt — für die Zusicherung nicht:

| Leser | Stand heute |
|---|---|
| `agents/synapsen_promotion/agent.py` | ✅ Docstring und Kommentar nennen 0..1; **aber** die Gewinner-Log-Zeile (`:256`) schreibt weiterhin `(0-10)` → Fundliste 29.07. |
| `agents/promotion/agent.py:322` | ✅ `min(salienz, 1.0)` steht und ist jetzt die richtige Grenze |
| `ei/gravitation.py:336` | ❌ **weiterhin ungeklemmt** — `gewicht = float(salienz_raw)`. Die oben verlangte Klemme ist nie gebaut worden; sie wurde nicht zurückgebaut, sondern hat nie existiert |

**Der Eintrag bleibt deshalb offen**, mit verschobenem Schwerpunkt: Nicht mehr der Dissens ist das Problem — die drei rechnen heute auf derselben Skala —, sondern dass der schadensträchtigste Leser seine Zusicherung nach wie vor nicht trägt. Sie ist rechnerisch wirkungslos und **genau darum jetzt billig zu bauen**. ⬜ Prio mittel (herabgestuft von hoch: der Schaden ist behoben, die Sicherung fehlt)

**Zusammenhang:** KZG-SALIENZ-SKALENBRUCH (Ursache) · KZG-GEWICHT-ABSOLUT-CEILING (vierter Abnehmer, über die Promotion) · Sprint KZG-SALIENZ-NEUBAU (✅ 28.07.2026).

---

## Sprint: KZG-SALIENZ-NEUBAU — die KZG-Salienz bekommt die Bauart des LZG-Gewichts (Chat 109)

> **Zuschnitt von Chat 109 — der Stand steht weiter unten.** Teil (a) und (b) sind am 28.07.2026 gebaut, migriert und live abgenommen; das Ankerfeld heißt `salienz_eingang` statt `salienz_roh` und trägt die unveränderte Modellbewertung statt eines frei wachsenden Werts. Teil (c) ist bewusst zurückgestellt. Was offen blieb, steht unter „Sprint KZG-SALIENZ-NEUBAU — was nach Bauteil 1 offen bleibt"; das Konzept dazu ist `novaberg-kzg-salienz_k.md`.

**Beschlossen Chat 109 (Meister).** Drei Teile:

- **(a)** Ankerfeld `salienz_roh`, frei wachsend, linear
- **(b)** `salienz` als **reine Funktion** davon, hart gekappt, CAP passend zur Skala [0,1] statt 10.0
- **(c)** Decay analog `LZG_KNOTEN_DECAY_RATE`

**Vorbild im selben Repo:** `memory/lzg_knoten.py:59-67` und `:537-548` — `gewicht_roh` als Anker (`+= BOOST`, linear), `gewicht_absolut = cap · sin(min(roh/cap, 1) · pi/2)^exp` als reine Funktion des Ankers. Idempotent, hart gekappt. Genau das, was der KZG-Variante fehlt.

**Nicht enthalten:** Die TTL-Unsterblichkeit (KZG-TTL-UNSTERBLICH) wird von (a)–(c) **nicht** repariert. ~~Sie hängt am `max()` in der Auffrischung. Vierter, eigener Hebel.~~ **Korrigiert Chat 109:** Der Hebel ist **PROMOTION-ENTFERNT-KZG-NICHT**, nicht das `max()`. Das `max()` ist für sich genommen richtig — schädlich wird es erst, weil die Einträge das KZG nie verlassen. Der vierte Hebel ist also die Entfernung bei der Promotion, und der liegt außerhalb dieses Sprints.

**Migration — 775+ Einträge.** Weil die Dämpfung im Betriebsbereich praktisch 1 ist, ist das heutige `salienz`-Feld faktisch bereits der Rohakkumulator; die Migration wäre damit ein **Rename plus einmaliges Neuberechnen**, kein Rekonstruieren verlorener Historie. **Ungeprüfte Ableitung — vor der Migration verifizieren.**

Braucht ein eigenes Konzeptdokument. ⬜ Prio hoch — eigener Sprint, **nicht** Teil von CHARAKTER-RESONANZ

**Zusammenhang:** KZG-SALIENZ-SKALENBRUCH (Ursache, Teil a+b) · KZG-KEIN-DECAY (Teil c) · KZG-TTL-UNSTERBLICH (ausdrücklich nicht enthalten) · KZG-SALIENZ-KONSUMENTEN-DISSENS (Abnahmebedingung) · REFAC-KZG-CODE-DUPLIKAT (`_gedaempfter_boost` liegt byte-identisch doppelt vor — der Neubau muss beide Kopien auflösen oder zusammenführen) · KZG-GEWICHT-ABSOLUT-CEILING (Abnehmer der Kette).

---

## Bug: PROMOTION-ENTFERNT-KZG-NICHT — der promotete Eintrag bleibt im KZG stehen (Chat 109)

Ein KZG-Eintrag, der ins LZG promotet wurde, **bleibt danach im KZG liegen**. Der Wert existiert von da an **doppelt** — einmal als `lzg_knoten`, einmal als KZG-Hash unter demselben Schlüssel, den `lzg_knoten.kzg_quell_key` als Herkunft führt.

**Belegt an einem Einzelfall (Log und Redis, 26.07.2026):**

```
08:38:29  KZG-Eintrag angelegt      kzg:meister:nova:1785055109755
08:38:48  Synapsen-Promotion gestartet, trigger_salienz=0.700
08:38:49  lzg_knoten angelegt: id=496, quell=kzg:meister:nova:1785055109755
09:29:35  hmget …1785055109755 → salienz 1.3958, haeufigkeit 3
```

**Belegt:** 51 Minuten nach der Promotion liegt der Eintrag in Redis — und er ist gewachsen (`haeufigkeit` 3, Salienz 1.3958 gegenüber 0.700 bei der Anlage).

**OFFEN — ob die Verstärkungen vor oder nach der Promotion lagen.** `trigger_salienz = 0.700` taugt nicht als Zeitmarke: Die Queue-Nutzlast **friert die Salienz beim Push ein** (`queues_befuellen` in `agents/kzg/queues.py` schreibt `salienz` als festen Wert in die `lzg_promotion`-Nutzlast, neben `aufgabe`, `user_id`, `key`, `themen`, `dimension` — kein `turn_id`, kein Zeitstempel), also bei der Neuanlage um 08:38:29, nicht bei der Promotion um 08:38:48. Die Zahl datiert die **Geburt**, nicht die Promotion. Das Log-Fenster endete 08:45:15, gemessen wurde 09:29:35 — für die 44 Minuten dazwischen gibt es keine Aufzeichnung. **Dass der KZG-Zwilling nach der Promotion weiter verstärkt wird, ist damit plausibel, aber unbewiesen.**

**Entscheidung Meister (Chat 109):** Promotete Einträge **sollen aus dem KZG entfernt werden**. Doppelte Werte werden nicht gebraucht. ⬜ Prio hoch

**UNGEPRÜFT:** Ob der Code einen Entfernungsschritt hat, der scheitert, oder gar keinen. Das ist eine Grep-Frage und ausdrücklich **nicht Teil dieses Eintrags** — er hält den gemessenen Zustand fest, nicht die Ursache.

**Zusammenhang:** KZG-TTL-UNSTERBLICH (Folge davon — was nie geht, kann ewig aufgefrischt werden) · KZG-KEIN-DECAY (die dritte fehlende Abwärtsbewegung) · KZG-SALIENZ-SKALENBRUCH (der Zwilling ist gewachsen; dass der Boost keinen wirksamen Deckel hat, erklärt die Höhe — nicht den Zeitpunkt) · KZG-GEWICHT-ABSOLUT-CEILING (dort die Gegenbeobachtung zu genau diesem Knoten id=496, mit Chat 109 aufgelöst).

---

## Doku: ROADMAP-GLIEDERUNGSBRUCH — ab Chat 98 wechselt die Chronik die Überschriftsebene (Chat 109)

`novaberg-roadmap.md` gliedert bis **Chat 97** nach Chat: jeder Chat ein eigener `## Chat NNN`-Abschnitt. **Ab Chat 98** wechselt sie ohne Hinweis auf `###`-Abschnitte, die nach **Sprint** benannt sind — „Synapsen P6 — Decay-Agent + Halbreaktivierung (Chat 102, …)", „Audit-Kaskade … (Chat 105, …)". Die Chat-Nummer steht nur noch in Klammern im Titel.

**Folge:** Wer nach `## Chat 104` sucht, findet nichts und hält den Eintrag für fehlend. Die Chronik ist vollständig, ihre Oberfläche sagt etwas anderes.

**Der Beleg für die Kosten — es ist bereits passiert.** In Chat 109 hat genau dieser Bruch einen Fehlschluss ausgelöst: Ein `grep` auf `^## ` fand als letzten Chat-Abschnitt die 97 und ließ auf eine **Lücke von elf Chats (98–108)** schließen. Tatsächlich fehlen **vier: 94, 95, 96 und 101** — die elf vermeintlich fehlenden waren alle da, nur eine Ebene tiefer. Der Fehlschluss wäre beinahe als Lückenmarkierung ins Dokument gewandert und hätte eine spätere Sitzung dazu gebracht, bereits Dokumentiertes nachzutragen. Der korrigierte Stand steht jetzt als Lückenmarkierung in der Roadmap selbst; die Kopfzeile trägt seit Chat 109 einen Warnhinweis auf die uneinheitliche Gliederung.

**Vereinheitlichung ist ein eigener Durchgang** — elf Abschnitte umhängen, Sprint-Titel als Untertitel erhalten, Querverweise prüfen. Nicht nebenbei. ⬜ Prio niedrig

**Zusammenhang:** DOKU-DUPLIKATE-CHAT80 · LESSON-INDEX-LUECKE (beides Gliederungs-/Auffindbarkeitsprobleme in der Doku, nicht im Code).

---

## Landmine: DB-SELECT-SCHREIBT-OHNE-COMMIT — `select()` führt ein Schreib-Statement aus und verwirft es (Chat 111)

Kein Defekt — `db_manager.select()` tut, was ihr Docstring sagt („SELECT-Abfrage", `tools/db_manager.py:26-34`). Die Falle liegt darin, was sie **nicht** tut: Sie lehnt ein übergebenes `INSERT`/`UPDATE`/`DELETE` nicht ab, sondern **führt es aus**, liest die `RETURNING`-Zeilen aus der offenen Transaktion und legt die Verbindung ohne `commit` in den Pool zurück. Dort wird alles verworfen.

Der Aufrufer sieht echte Zeilen und meldet Erfolg. Genau das ist einmal geschehen: zwanzig gemeldete Neuanlagen, null in der Tabelle. Behoben durch `execute_returning`, das committet und die Zeile zurückgibt — es existierte längst; gegriffen wurde zur falschen Funktion, weil sie zufällig auch etwas zurückgibt.

**Gemessen am Bestand:** **22 von 22** Aufrufstellen übergeben ein `SELECT`. Kein zweiter Fall, ein Durchgang lohnt nicht — die Falle ist latent, nicht verbreitet.

**Härtung:** `select()` soll ein Nicht-`SELECT` **ablehnen** statt es auszuführen — fail loud, statt lautlos zu verwerfen. Solange das nicht gebaut ist, gilt der Sperrvermerk: Wer schreibend `RETURNING` braucht, nimmt `execute_returning`. ⬜ Prio niedrig

**Zusammenhang:** `novaberg-lesson_l_gelesen-ist-nicht-wirksam.md` (Fall 1 der Klasse).

---

## QUEUE-VERFALL-KONZEPT — der Stapel und die Queue brauchen ein Verfallsmodell ✅ (15.08.2026)

**Band:** B — die Queue wächst schneller, als sie abfließt, und niemand räumt sie.

**Konzept geschrieben am 15.08.2026 — `novaberg-queue-verfall_k.md`. Der Bau steht aus.**

**Zwei Entscheidungen von diesem Tag haben den Eintrag darunter überholt:**

- ~~**Was unter die Schwelle fällt, wird hart gelöscht** — der Gedanke ist dann unwiederbringlich weg.~~ → **Ersetzt durch Soft-Delete nach LZG-Vorbild.** Ein Auftrag unter der Schwelle wird auf `aktiv = FALSE` gesetzt, bleibt gespeichert und ist über die Halbreaktivierung aus `novaberg-memory-synapsen_k.md` §9.3 weckbar. **Der Grund, der den Ausschlag gab:** Alle 233 Aufträge auf Salienz 0,0 sind `vertiefen` — ihre Null ist ein Schreibfehler und kein schwacher Anlass. Bei hartem Löschen wären sie beim ersten Lauf endgültig weg.
- ~~Die Frist ist an das KZG angelehnt … höchstens **30 Tage**, gestaffelt nach Salienz.~~ → **Die 30 Tage bleiben, die Staffelung entfällt.** Sie sind keine Löschfrist, sondern die Zeit, in der ein unberührter Auftrag von voller Salienz auf die Schwelle 0,3 fällt. Eine Staffelung wäre daneben eine zweite Kurve; die eine Rate **λ = 0,0393/Tag** leistet dasselbe, weil ein schwächerer Auftrag von einem niedrigeren Anker startet und deshalb früher unten ankommt.

**Der ursprüngliche Eintrag, als Begründung erhalten.** Aufträge und Stapel-Einträge sollen verfallen wie Erinnerungen: mit einem Einstiegswert, einer Verstärkung, einem sinus-gedämpften effektiven Wert, einer letzten Änderung und einem gerechneten Verfall. Die Schwelle steht bei **0,3**: Gedanken mit niedriger Salienz verlieren, und damit fällt das Rauschen heraus.

**Zwei Vorbilder, zwei Hälften.** Die Sinus-Sättigung samt Verstärkung steht in `novaberg-kzg-salienz_k.md` §3; der materialisierte Verfall mit `decay_am` in `novaberg-memory-synapsen_k.md` §9. **Der KZG selbst hat keinen rechnenden Decay** — dort verfallen Einträge über die Redis-Frist, sie sinken nicht. Die Kombination ist neu und hat noch kein Dokument; die Shadow-Queue hat überhaupt keines.

~~**Was fertig waere.** Ein eigenes `novaberg-queue-verfall_k.md` …~~ → **Geschrieben am 15.08.2026.** Dabei hat die Suche nach dem *Gegenstand* ergeben, dass die Bauart bereits beschrieben war: `novaberg-autonomous-wissen_k.md` §11.6/§11.7, für Stapel und Bibliothek. Das neue Dokument ist deshalb die Übertragung auf einen dritten Speicher und verweist, wo das Schwesterdokument trägt, statt es zu wiederholen.

**Die drei Punkte sind entschieden:**

1. **Die dritte Rolle von `prioritaet` kommt nicht dazu, sie ersetzt die zweite.** Der Wert zerfällt nach `lzg_knoten`-Vorbild in `salienz_roh` / `salienz_absolut` / `salienz_decay`; der Scheduler wählt künftig nach der Präsenz, die Herkunft steht im Anker. Damit ist die Zwei-Rollen-Vermengung aufgelöst statt erweitert.
2. **Die 233 Aufträge auf `0.0` fallen beim ersten Lauf heraus** — gewollt, und dank Soft-Delete rückholbar. Sie sind ausnahmslos `vertiefen`.
3. **Die 383 verwaisten `vertiefen`-Aufträge bleiben ein Ventil, kein Fix**, und die Wahl ist als Absichtsfrage benannt: den Agenten bauen (`novaberg-pixie-deepdive_k.md` — das Konzept existiert) oder `information_teilen` nicht mehr einreihen.

**Der Lebenszyklus ist am 15.08.2026 durchgerechnet und entschieden** (`novaberg-queue-verfall_k.md` §12):

- **Drei Wege hinaus, einer davon ein Löschen.** Erledigt → die Zeile wird entnommen (schon heute so: `abschluss(erfolg=True)` → `LREM`). Gescheitert nach drei Versuchen → verworfen. Nur wartend → `aktiv = FALSE`, bleibt. **Zum Vergleich: Der KZG löscht hart** über Redis-TTL (7 / 14 / 30 Tage nach Salienz), **das LZG nie** — die Queue nimmt vom KZG die Frist und vom LZG den Rückweg.
- **Die Rangfolge ist Dringlichkeit, und damit LIFO.** Der frische Gedanke ist der präsente; ein Vorsatz wird nicht dringlicher, weil er lange liegt. Das kehrt die heutige Ordnung um (heute gewinnt der älteste Eintrag des Höchstwerts) und ist ausdrücklich gewollt. **Kein Verhungerungsschutz für Queue-Aufträge** — anders als bei den periodischen Aufgaben.
- **Die Sättigung der Sinus-Kurve ist der Zweck, nicht ein Mangel.** Zehn Verstärkungen heben `salienz_absolut` um 0,024; die Wirkung sitzt in `verstaerkt_am` und schenkt 30 Tage neu. Derselbe Bau im KZG, wo eine Verstärkung die TTL verlängert. **Der Boost ist keine Stellschraube der Frist.**
- **Keine Mengengrenze, kein Jahresablauf.** Wächst der Bestand über das Erträgliche, wird `QUEUE_DECAY_RATE` verstärkt — eine Obergrenze würde nach Zahl statt nach Dringlichkeit verwerfen.

**Gebaut und gemessen am 15.08.2026** — Tabelle samt zwei Indizes (Log: 132 Statements statt 129), Repository, Migration **1036 von 1036** (danach 803 aktiv, 233 ruhend), Schreib- und Auswahlpfad, Verfall als dritter Schritt in `synapsen_decay` mit eigenem Audit-Eintrag. Der Verfallslauf am echten Bestand: 805 verarbeitet, 0 deaktiviert, Summe unveraendert. Suite 1373 → **1399 grün**. Messwerte in `novaberg-queue-verfall_k.md` §16.

**Der Rest, als Rest benannt.** Erstens: **Nur der Queue-Verfall hat einen eigenen Audit-Eintrag.** Das Konzept §11 verlangt ihn *je Schritt* — der Knoten-Decay und das `pipeline_log`-Aufräumen teilen sich weiterhin den Sammel-Eintrag von `synapsen_decay`. Solange das so ist, ist bei einem roten Lauf nicht unterscheidbar, welcher der beiden ihn rot gefärbt hat. Der neue Schritt ist deshalb nicht der Anlass, sondern die Stelle, an der die Lücke sichtbar wurde. Zweitens: Die Wirkung *ein Auftrag faellt durch Alter heraus* ist am Bestand nicht zu beobachten — keiner ist 30 Tage alt. Sie ist ueber gesetzte Zeitstempel bezeugt, nicht gemessen; die echte Messung braucht 30 Tage Betrieb. Ebenso ungemessen: die Reaktivierung durch einen echten wiederkehrenden Anlass.

**Gemessen am 15.08.2026 um 13:52 UTC:** 1036 Aufträge — 608 `recherche`, **383 `vertiefen` ohne Agenten**, 45 `nachfragen`. 233 auf Salienz 0,0 (alle `vertiefen`), 145 ohne Thema, Median 0,9764, ältester 18 Tage. **Der Bestand wuchs während der Messung** von 1032 auf 1036.

## IMPULS-HANDLUNG-OHNE-HERKUNFT — was sie selbst angelegt hat, ist nicht erkennbar (14.08.2026)

**Band:** C — es steht heute Bestand in der Datenbank, dessen Urheber nicht feststellbar ist.

**Entschieden am 14.08.2026: Ein eigener Gedanke darf handeln.** Nova soll agieren können — Termine, Notizen, Direktiven —, und ein versehentlich angelegter Eintrag ist kein Grund, ihr das zu nehmen: Ein Mensch legt auch versehentlich Termine an. Der gebaute Zustand entspricht dieser Entscheidung bereits; die Dispatcher der Management-Agenten lesen den Reiz des Turns, und auf einem Impuls-Turn ist das Novas Gedanke. **Es ist nichts zu bauen, um das zu erlauben.**

**Was fehlt, ist die andere Hälfte des Satzes.** „Versehentlich" setzt voraus, dass hinterher erkennbar ist, wessen Versehen es war. Weder `timeline` noch `notizen` trägt eine Spalte dafür:

```
timeline   id · user_id · event_time · event_type · title · details · recurring ·
           precision · created_at · aktiv · last_touched · wiedervorlage_am ·
           entitaet_ids · event_ende · binding · remind · conflict_check · themen
notizen    id · user_id · name · typ · text · faellig_am · status · created_at ·
           updated_at · zusammenfassung · themen · entitaet_ids · aktiv ·
           last_touched · wiedervorlage_am · suchtext · timeline_id
```

Ein Termin aus ihrem Impuls ist von einem, um den gebeten wurde, nicht zu unterscheiden. Damit ist er auch nicht gezielt zurücknehmbar — nur einzeln und von Hand, nachdem er aufgefallen ist.

**Die Angabe existiert bereits im Turn** (`reiz_herkunft`, `nutzer_turn` oder `eigener_impuls`) und wird schon in den Rohturn geschrieben. Sie erreicht die Schreibpfade der Agenten nur nicht.

**Was fertig wäre.** Jeder von einem Agenten angelegte Eintrag trägt die Herkunft des Turns, der ihn ausgelöst hat. Eine Abfrage beantwortet „was hat sie diese Woche selbst angelegt", und der Bestand vor der Einführung ist als *unbekannt* erkennbar — nicht als *vom Menschen*, denn das wäre ein Vorgabewert im plausiblen Bereich.

**Schemaänderung — nicht ohne ausdrückliche Freigabe.** Eine Spalte je betroffener Tabelle, und ein `.py`-Edit zündet beim Neuladen die Schemadatei mit.

**Und ein Ausblick, der nicht mitentschieden ist:** Sobald Hände dazukommen, die außerhalb der Datenbank wirken, ist dieselbe Angabe die Grundlage jedes Handlungsprotokolls. Sie jetzt einzuziehen ist billiger als später, hat aber keinen eigenen Termindruck.

**Der Sonderfall daneben ist ein Defekt und kein Teil dieser Entscheidung:** Ein Impuls-Turn läuft heute in den Resume-Pfad eines wartenden Agenten und löscht dessen Rückfrage — `novaberg-bugs.md` → `RESUME-VERBRAUCHT-DEN-IMPULS`. In fremdem Namen zu antworten ist etwas anderes, als selbst zu handeln.

---

## Audit: PUB-ROLLENNAMEN-IM-BESTAND — die Doku nennt die internen Rollen (Chat 120)

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

In `services/pixie/router.py` entschied eine **Tabelle neben dem Register** darüber, welcher periodische Agent läuft — dieselbe Zuordnung ein zweites Mal geführt, ohne dass ein Auseinanderlaufen bemerkt worden wäre. Ein neu registrierter Agent gewann den Heartbeat, fand keine Route und starb mit einer Warnung; weil der Takt einen Gewinner je Runde kennt, lief in dieser Runde auch sonst nichts. Behoben durch Rückfall auf Namensgleichheit — die Tabelle bleibt nur noch für die Fälle, in denen Zeitplan- und Agentenname wirklich abweichen (`charakter_hash` → `charakter`).

**Die Instanz ist zu, die Form nicht.** Offen und **nicht gemessen:** Wo sonst im Bestand führt eine Aufzählung dieselbe Zuordnung wie ein Register, ohne dass ein fehlender Eintrag lauter ist als eine Warnung? Zu prüfen sind Zuordnungs-Literale, die neben einer Registry, einer Enum oder einer Tabelle stehen und von Hand nachgepflegt werden müssen.

**Der Durchgang braucht ein Messdatum:** Kandidaten zählen, je Fall entscheiden — ableitbar (dann ableiten) oder echt abweichend (dann bleibt die Tabelle, aber der Fehlschlag wird laut). ⬜ Prio mittel

**Zweite Instanz gefunden, 30.07.2026 — die Toolbar des Clients.** `client/ui/main_window.py` führt in `_TOOLBAR_PANELS` eine Liste von Button-Beschriftungen; verdrahtet wird ein Button nur, wenn seine Beschriftung **exakt** auf das `PANEL_LABEL` eines registrierten Panels trifft. Der Anzeigetext ist damit zugleich der Verbindungsschlüssel. Trifft er nicht, fällt der Button auf einen Platzhalter-Zweig, der beim Klick nur eine Zeile loggt — kein Fehler, keine Warnung, der Reiter öffnet nichts.

Aufgefallen beim Ergänzen eines Symbols im Reiter „Charakter": Die Änderung an einer der beiden Stellen allein macht das Panel unerreichbar. Gemessen mit beiden Stellen geändert: 9 von 9 registrierten Panels verdrahtet, kein verwaistes. Gegenprobe mit nur einer geänderten Stelle: `Charakter` als Platzhalter, `🧬 Charakter` als registriertes Panel ohne Button.

**Zwei Auswege, beide klein:** Die Liste über `PANEL_LABEL` ableiten statt sie zu führen — dann ist die Doppelung weg; oder `_build_toolbar` beim Aufbau melden lassen, welche registrierten Panels keinen Button haben. Der zweite ist drei Zeilen und macht den Fehlschlag laut, ohne das Verhalten zu ändern.

**Zusammenhang:** ALLOWLIST-DRIFT (andere Form von Drift) · `novaberg-lesson_l_gelesen-ist-nicht-wirksam.md` (Fall 3 der Klasse).

---

## Landmine: GV-RELEVANZ-UNNORMIERT — die Relevanz kann über 1.0 liegen, ihr Name sagt das nicht (Chat 111)

Kein Defekt — heute stolpert niemand darüber. `relevanz` entsteht als `basis × (1.0 + neugier_boost) × aufnahmebereitschaft × register` (`ei/wissensluecken.py:288-293`) und ist **nicht normiert**; angezeigt wird sie über `graph/nodes/gespraechsvektor.py:554`. Der Faktor `1.0 + neugier_boost` hebt sie über 1.0, sobald eine Gravitation anliegt — sieben Lücken über 1.0 sind im Client bereits beobachtet worden.

**Der einzige heutige Leser ist geprüft und unbetroffen:** `ei/wissensluecken.py:347` vergleicht gegen `GV_LUECKEN_MIN_RELEVANZ = 0.15` (`config.py:997`), also eine **Untergrenze** — die wirkt unabhängig davon, wie weit der Wert nach oben reicht.

**Die Falle liegt beim nächsten Leser.** Wer den Namen für einen Anteil hält und eine **Obergrenze** oder einen Prozentwert daraus baut — `if relevanz > 0.8`, eine Anzeige in Prozent, ein Faktor in ein Produkt hinein —, bekommt bei anliegender Gravitation lautlos ein immer wahres Kriterium oder ein Gewicht über 100 %. Ein Vergleich gegen eine plausible Zahl sieht nach einer Prüfung aus.

**Entscheidung, keine Reparatur:** entweder den Wertebereich am Erzeuger dokumentieren und die Konsumenten darauf verpflichten, oder normieren und alle Leser mitziehen. ⬜ Prio niedrig

**Zusammenhang:** KZG-SALIENZ-KONSUMENTEN-DISSENS (drei Leser, drei Annahmen über dieselbe Zahl — dieselbe Familie).

---

## Sprint KZG-SALIENZ-NEUBAU — was nach Bauteil 1 offen bleibt (Chat 114)

Bauteil 1 — die Salienz als abgeleiteter Wert statt als Akkumulator — steht seit Chat 113, migriert und live gemessen. Die restlichen Schritte standen bis Chat 114 nur in der Sitzungsübergabe außerhalb des Repos und damit nirgends, wo sie eine Sitzung überleben.

### Bauteil 2 — die Promotion entfernt den KZG-Eintrag ⬜ Prio hoch

Vorbild ist der bestehende Löschpfad im Promotions-Agenten. Betrifft **nur** den Neuanlage-Pfad, nicht die Halbreaktivierung und nicht das Reinforcement. Hängt an `PROMOTION-ENTFERNT-KZG-NICHT` (Chat 109) — dort steht der Befund, hier der Bauschritt.

**Vor der Umsetzung neu messen.** Der Befund stammt aus Chat 109 und liegt vor dem Reset des Bestands und vor dem Salienz-Umbau.

### Bauteil 3 — Charakter-Räder im Client ✅ Chat 120 (30.07.2026)

Die Visualisierung im Charakter-Tab; die Datenseite stand seit Chat 116.

| Rad | Speichen | Datenlage |
|---|---|---|
| `nutzer_gewichtung` | **12** — sechs Zuwendung, sechs Abwendung | gebaut, Werte in `charakter_hash.nutzer_gewichtung_rad` als JSON |
| Initiative-Versatz | **10** — fünf überlässt, fünf behält | gebaut Chat 116, Werte in `charakter_hash.initiative_versatz_rad` |

Beide stehen jetzt als **Radar-Diagramme nebeneinander im Charakter-Tab**, darunter je Kennzahl, Herkunft und die Speichen einzeln. Die Bauart ist dieselbe: Nabe, Speichen mit festem Zug, LLM-Bewertung 0.0 / 0.5 / 1.0 je Speiche, das Ergebnis gerechnet. Ein Radar ist die Darstellungsform, die zu dieser Bauart gehört — sie zeigt, welche Speichen tragen und welche nicht, statt nur das Ergebnis.

**Nebeneinander statt untereinander,** abweichend von der ursprünglichen Fassung dieses Eintrags — die Anordnung folgt dem Emotionen-Panel, das zwei Radare derselben Größe nebeneinander stellt.

**Umgesetzt:** `RadarChart` auf beliebige Achsenzahl verallgemeinert · `GET /gedaechtnis/hash/{user_id}` liefert beide Räder samt Herkunft · das Speichen-JSON wird serverseitig geparst · ein Rad ohne Daten wird als solches gezeichnet, nicht als Polygon aus Nullen · fehlende Speichen werden gemeldet statt mit 0.0 überdeckt.

**Was offen bleibt:**

- **`laeufe` und `streuung` haben weiterhin keinen Leser.** Das Initiative-Rad legt neben den zehn Speichen die Einzelergebnisse seiner drei Läufe und deren Streuung ab (gemessen 30.07.2026: 0.07 und 0.08). Sie reisen jetzt bis in den Client, werden dort aber nicht angezeigt. Die Streuung ist die einzige Aussage darüber, wie stabil der Versatz über mehrere Erhebungen ist — ohne sie ist ein Median aus drei Läufen von einem Einzelwert nicht zu unterscheiden. ⬜ Prio niedrig
- **Der Verweis auf „sieben Teilschritte, unverändert seit Chat 111" zeigte ins Leere.** Die Aufzählung steht in keinem Repo-Dokument; ein Grep über `docs/` findet nur den Verweis auf sie. Sie ist beim Schließen nicht rekonstruiert worden — was tatsächlich gebaut wurde, steht oben. Dieselbe Klasse wie die Einträge unter „Ohne Gegenstand" in der Fundliste.
- **Es gibt keinen automatischen Test der Client-Seite.** Der Client liegt außerhalb des Server-Abbilds und kann in der Suite nicht importiert werden. Die Verdrahtung ist stattdessen über die Speichennamen gesichert (`server/tests/test_hash_raeder.py`, `VertragMitDemClientTest`): Wird eine Speiche serverseitig umbenannt, wird der Test rot und nennt den Client als nachzuziehende Stelle. Die Anzeige selbst ist von Hand gemessen. ⬜ Prio niedrig

---

### Nachvollziehbarkeit im `pipeline_log` prüfen ⬜ Prio hoch (Chat 116)

**Die Frage:** Sind die Rechenergebnisse im Nachhinein nachvollziehbar, oder sind sie Black Boxes? Eine Berechnung, deren Zwischenwerte nirgends dauerhaft stehen, ist nach einem Tag nicht mehr prüfbar — man sieht das Ergebnis und kann nicht sagen, wie es zustande kam.

**Der konkrete Anlass:** Die Initiative-Achse (Chat 116) schreibt ihre drei Maße, die zwei Dimensionen und den Versatz nach `gv_detail` — also nach **Redis, ohne TTL, bei jedem Turn überschrieben** — und in die Logzeile, die mit dem Container rotiert. **Im `pipeline_log` steht nichts davon.** Nach einem Neustart ist von jedem Turn außer dem letzten nur noch das Achsen-Bit übrig, nicht die drei Zahlen, aus denen es entstand.

Dasselbe ist bei der Auswertung dieser Sitzung aufgefallen: Die Messgrundlage für die neue Achse musste aus KZG-Einträgen und Rohturns rekonstruiert werden, weil die gerechneten Werte nirgends persistiert waren.

**Zu prüfen, nicht zu bauen — der Umfang ist offen:**

- Welche Rechnungen schreiben heute Zwischenwerte ins `pipeline_log`, welche nicht? (Kriterium statt Aufzählung: **jede**, deren Ergebnis eine spätere Entscheidung trägt.)
- Was davon wäre für eine Kalibrierung oder eine Fehlersuche nötig?
- Was kostet die Persistierung — `pipeline_log` trägt bereits über 12.000 Zeilen für wenige Tage.

**Kopplung:** Der Kalibrier-Agent (`novaberg-gv-initiative_k.md` §7) rechnet Zentren aus dem Bestand. Ohne persistierte Rohwerte kann er nur aus abgeleiteten Quellen rechnen — genau der Umweg, den diese Sitzung gehen musste.

**✅ Für die Initiative-Achse erledigt am 29.07.2026 (Chat 117).** Der GV-Node schreibt je Turn eine `berechnung`-Zeile mit den drei Maßen, den zwei Dimensionen, Rohwert, Versatz, Bit und `fehlend` — **dazu die geltende Skalenfassung**: Schwelle, Herkunft, Kalibrierzeitpunkt, die Zentren und Spannen von M2 und M3, die Versatzgrenze. Auditiert am Turn von 20:52 UTC. Das Bit ist aus der Zeile allein nachrechenbar, auch nachdem die Schwelle neu erhoben wurde; ein Test hält das fest.

**Die Fassung war der eigentliche Punkt und stand nicht in diesem Eintrag.** Ein Rohwert allein genügt nicht: Sobald die Schwelle je Paar erhoben wird, wandert der Maßstab mit dem Gemessenen, und die Reihe lässt später nicht mehr trennen, ob sich Nova bewegt hat oder die Skala.

**Offen bleibt der Rest der Frage:** Welche anderen Rechnungen tragen eine Entscheidung und schreiben nichts? Die drei Prüffragen oben gelten unverändert; die Initiative-Achse ist ein Fall, nicht die Menge. ⬜ Prio hoch

---

### Konzept: ein Node für Novas Sprache ⬜ Prio offen (Chat 116)

**Auftrag:** Ein Konzept für einen neuen Node, der Novas Sprache stärker zur Geltung bringt. Die Ausarbeitung folgt nach dem Konzept.

**Was an Vorarbeit vorliegt:** Chat 114 hat gemessen, dass der Gesprächsverlauf rund drei Viertel des Responder-Prompts ausmacht und der Gesprächsvektor-Block rund drei Prozent — *„Rund drei Viertel Verlauf, rund drei Prozent Register."* Der Sprachstil-Block wurde daraufhin hinter den Verlauf gesetzt, damit er überhaupt eine Chance gegen die Prosa davor hat. Ob das über längere Strecken trägt, ist ausdrücklich offen geblieben (`novaberg-bugs.md`, Sprachstil-Eintrag: *„Zwei Turns. Die Wirkung auf den Ton lässt sich nicht im Unit-Test sichern"*).

Das ist der Befund, an dem ein solcher Node ansetzt — die Frage ist nicht, ob Nova eine Sprache hat, sondern warum die Prosa im Kontext sie überschreibt.

### Der Eigen-Pfad trägt einen von vier Antrieben

Vor dem Anschluss der emotionalen Gravitation an die Salienz sind zwei Punkte zu klären:

- Der **dreifache Verfall** im LZG-Zweig (`novaberg-fundliste.md`, 28.07.2026) — die Kurve wird dreimal angewandt, entgegen `novaberg-convention-abgeleitete-werte.md` §3(5)
- Der **Quellenfaktor**: LZG 0.5 gegen KZG 0.8. Die Schatzkiste wird stärker gedämpft als der Zwischenspeicher — das steht gegen das Leitmotiv *„viel speichern, intelligent vergessen"*. Entscheidung offen

Die Rückkopplung Wissenslücken → Neugier existiert weiterhin nicht (`novaberg-thinking-curiosity_k.md`).

---

## Konzipiert, nicht gebaut — der Bestand (Chat 114)

Vier Konzepte ohne Code. Sie standen bis Chat 114 nur in der Sitzungsübergabe; die Konzeptdokumente selbst existieren, aber nichts im Repo verzeichnete sie als offene Arbeit.

| Konzept | Dokument | Stand |
|---|---|---|
| **Gedankenkette** — ein Gedanke über mehrere Turns | `novaberg-gedankenkette_k.md` | konzipiert Chat 111, kein Code ⬜ |
| **Wissensspeicher (Strang B)** | außerhalb des Git-Roots | konzipiert, kein Code ⬜ |
| **NachfragenAgent** | `novaberg-pixie-nachfragen_k.md` | Konzept steht, ~~vier Fragen~~ **noch eine Frage** in §4 offen — die Form; Bau als `PIX-MIG-7` geführt ⬜ |
| **KlaerfrageAgent** | `novaberg-autonomous-wissen_k.md` §11.3 | konzipiert, kein Code; blockiert durch `KLA-K1`/`KLA-K2`, Bau als `PIX-MIG-9` geführt ⬜ |
| **Selbstreflexion** | `novaberg-thinking-curiosity_k.md` §4.7 | konzipiert, kein Code ⬜ |

Der NachfragenAgent hat eine Kopplung: `services/pixie/router.py` bildet `nachfragen` auf einen Agenten ab, den es nicht gibt — siehe die Fundliste vom 27.07.2026. Der Bau schließt diesen Befund mit; die Reihenfolge ist dort beschrieben.

**Nachtrag 05.08.2026 — der Befund ist latent, nicht aktiv.** Gemessen gewinnt heute kein agentenloser Auftrag den Heartbeat: Die 390 `recherche`-Aufträge stehen in der Listenreihenfolge vor ihnen, und `_queue_peek` nimmt den **ersten** Eintrag mit echt größerer Priorität. Er feuert wieder, sobald sie abfließen. Was den Heartbeat heute blockiert, ist der besetzte Slot — 249 von 270 Auslösungen fielen in 2,25 Stunden aus (Fundliste 05.08.).

---

## Verlauf des Standes

- **24. August 2026, 13:35 UTC** — der Matrix-Epic loest seine eigene Abschaltbedingung ein. Sie stand seit dem 23.08. als Satz da (*„Ein Kanal wird abgeschaltet, wenn der andere gemessen traegt — der Handy-Test steht noch aus"*) und war seit dem 23.08. erfuellt, weil AP 8 auf ✅ ging; **einen Tag lang hielt sich die Sperre selbst, nachdem ihr Grund entfallen war.** Telegram ist abgeschaltet, `telegram_bot/` bleibt liegen. Offen: der Token-Widerruf beim BotFather.

- **23. August 2026, 17:15 UTC** — ein Eintrag neu: `DATEIINDEX-GRAPHKANAL`. Er entsteht aus einer Messung, die gegen einen Bau entschied — die Stichwoerter des Dateienindex gegen den Entitaetenbestand aufzuloesen ergibt 10 Treffer aus 843, und 116 der 122 Kanten zeigen auf dieselbe Entitaet.
Die Fortschreibung des Standes, aus der Kopfzeile geloest am 20.08.2026. Der Wortlaut jedes Eintrags ist unveraendert; vorangestellt ist allein sein Datum.

- **21. August 2026, 09:43 UTC** — **Der benannte Rest von `SUCHSCHLUESSEL-OHNE-VERLAUF` ist gemessen und zu.** Query Rewriting traegt bei allen fuenf Lesern des Suchschluessels: 39 Sonden, rohe Aeusserung 0, Rewrite 37, Deckung mit der Referenz 39 von 39. Dabei ein eigener Fund: Zwei der Konsumenten haben keinen wirksamen Boden.
- **21. August 2026, 22:50 UTC** — **`BUGREGISTER-ZUSTAND-NICHT-LESBAR` geschlossen.** Die zwoelf fehlenden Abschnitte sind einzeln gegen HEAD `62560cf` geprueft statt uebertragen — **6 behoben, 6 offen** —, und damit traegt jeder der 82 Eintraege seinen Zustand an genau einer Stelle: **64 offen / 18 behoben**, mit `grep` zaehlbar. Die Pruefung fand nebenbei einen Widerspruch, den eine Uebertragung fortgeschrieben haette: eine Ueberschrift sagte *behoben*, waehrend derselbe Eintrag seine Schlussbedingung als ausstehend fuehrte. **Ein Eintrag kommt dabei neu hinzu:** `BUGREGISTER-ALTEBENE-OHNE-ZUSTAND` — eine Zaehlung ueber beide Ueberschriftenebenen des Registers fand **166 aeltere Eintraege ohne Zustandszeile**. Die neue Zahl deckt 82 von 248.
- **20. August 2026, 19:36 UTC** — **`BUGREGISTER-ZUSTAND-NICHT-LESBAR` zur Haelfte umgesetzt und ausdruecklich nicht geschlossen.** Die Form steht — je Eintrag eine Zeile `**Zustand:**` mit geschlossener Wertemenge, Pruefdatum und HEAD —, und 70 der 82 Abschnitte tragen sie. Die uebrigen zwoelf nicht. Ein Befund mit mehreren Stellen ist erst geschlossen, wenn jede steht.
- **20. August 2026, ~21:20 UTC** — **Ein Eintrag neu aus dem Abgleich des Verlaufs:** `BUGREGISTER-ZUSTAND-NICHT-LESBAR` — der Zustand eines Defekts steht an drei Stellen und in keiner verbindlich; von 82 Abschnitten tragen 6 ueberhaupt eine Marke. Jede Zahl ueber offene Defekte ist bis dahin eine Schaetzung.
- **20. August 2026, ~20:50 UTC** — **Ein Eintrag geschlossen:** `SUCHSCHLUESSEL-OHNE-VERLAUF` ist als Query Rewriting umgesetzt und im Betrieb belegt. Ein Rest ist benannt: Die Wirkung auf KZG und LZG ist ungemessen — gemessen wurde gegen die Bibliothek.
- **20. August 2026, ~18:30 UTC** — **48 neue Eintraege** aus der Klassifikation der Fundliste, jeder mit ID, `Was fertig waere` und einer ersten Prioritaet. **Die Prioritaet ist kein Band** — ein Band wird gegen den Code vergeben, nicht gegen den Eintrag.
- **20. August 2026, ~17:05 UTC** — **kein Eintrag bewegt.** Die Kopfzeile trug 10.512 Zeichen in einer Zeile und ist in den Abschnitt *Verlauf des Standes* geloest — 29 Eintraege, Wortlaut unveraendert.
- **20. August 2026, ~14:15 UTC** — **zwei neu: `LAENGENVORGABE-UNGEMESSEN` und `MASSBLOCK-IM-BETRIEB-UNGEMESSEN`** — die Antwortlänge hat seit heute drei Einflüsse, und der Verfasser liest die Haltung; beides ist bezeugt und im Betrieb ungemessen.
- **20. August 2026, ~13:55 UTC** — **`GLIEDERUNG-NUR-MARKDOWN` umgesetzt** — der Index versteht seit heute alle fünf Textformate, die er annimmt; `.txt` ist dabei ausdrücklich als leere Gliederung registriert und nicht als Lücke.
- **20. August 2026, ~13:15 UTC** — **`MARKDOWN-ERKENNER-IST-HANDARBEIT` umgesetzt** — die Gliederung von Markdown macht seit heute `markdown-it-py`; die Zaunbilanz bleibt davor stehen, weil der Parser den unpaarigen Zaun ebenfalls falsch liest (45 statt 83 Überschriften). `GLIEDERUNG-NUR-MARKDOWN` bleibt offen.
- **20. August 2026, ~12:30 UTC** — **zwei neu: `GLIEDERUNG-NUR-MARKDOWN` und `MARKDOWN-ERKENNER-IST-HANDARBEIT`** — der Dateien-Index nimmt fünf Textformate an und versteht eines, und der eine Erkenner ist ein Regex-Automat mit zwei von vielen CommonMark-Regeln. Beides ist seit heute laut statt still, aber nicht gebaut.
- **20. August 2026, ~09:45 UTC** — **neu: `BIBLIOTHEK-BLIND-AUF-INHALTSHOEHE`** — die Bibliothek findet auf Themenhöhe (Rang 1, Kosinus bis 0,7375) und ist auf Inhaltshöhe blind (Rang 142 bei 0,1768, dieselbe Ausarbeitung). Die Schwelle 0,50 schneidet 9 von 10 richtigen ab, ist aber nicht der Fehler: Sie ist an Themenfragen kalibriert, während der Enricher mit dem Vektor des Turns sucht. Das erklärt 2 echte Treffer in 142 Nutzerturns.
- **20. August 2026, ~09:05 UTC** — **`EMBED-LISTE-DATEIENINDEX` gebaut, gemessen und verworfen** — der Umbau stand vollständig (Tabelle, Schreibweg, drei Lesewege, 1456 nachgebettete Vektoren) und brachte **keine** Verbesserung: Rang 1 unverändert 8/12, Top 3 von 10 auf 9, und die Trennung wird schlechter. Zurückgebaut. Die Analogie zur Bibliothek trägt nicht — dort standen mehrere Gegenstände in einem Feld, hier beschreiben Thema und Stichwörter denselben.
- **20. August 2026, ~08:30 UTC** — **`AUFZEICHNUNGEN-BODEN-NACHZIEHEN` beantwortet, ein neuer Eintrag daraus** — 24 Sonden gegen 174 Indexzeilen: Der Boden 0,30 trägt (Lücke der Mediane 0,177 gegen 0,038 am 18.08.), und der eine richtige Fall, den er abschneidet, wird vom scharfen Kanal aufgefangen. Der verbleibende Fehler ist die **Rangfolge**: `EMBED-LISTE-DATEIENINDEX` ist die dritte Stelle, an der ein Vektor mehrere Gegenstände trägt — hier `thema` plus acht Stichwörter, mit gemessener Wirkung (Rang 1 in 8 von 12).
- **20. August 2026, ~07:35 UTC** — **zwei Einträge neu bewertet, keiner geschlossen** — `AUFZEICHNUNGEN-BODEN-NACHZIEHEN` ist **entblockt**: Die Freigabe von `docs/` hat den Index von 14 auf 174 Zeilen gebracht, und damit existiert der Bestand, den der Eintrag seit dem 18.08. für seine Sondenmessung verlangt; die Messung selbst steht aus. `AUFZEICHNUNGEN-QUANTIL` bleibt unverändert offen, hat aber ab jetzt einen Korpus, an dem eine Verteilung entstehen kann.
- **19. August 2026, ~20:40 UTC** — **zwei Bloecke aus dem Umbau der Bibliothek** — `ein Vektor je Gegenstand` mit drei Eintraegen, davon zwei am selben Tag beantwortet und durchgestrichen (`OLLAMA-VERSION-VIER-MONATE-ALT`, `WIS-ENRICHER-UNGEMESSEN`); dazu `WIS-SCHWELLE-MESSEN` beantwortet — die Frage war falsch gestellt, nicht die Schwelle war das Problem, sondern die Rangfolge unter ihr.
- **19. August 2026** — **neuer Block: die Rollen eines Wissen-Silos** — vier Einträge aus einer gezählten Matrix. Von neun Silos trägt **genau eines alle drei Rollen** (Quelle, Zettel, Werkzeug: die Timeline); ihr eigenes erarbeitetes Wissen trägt **eine**. `WISSEN-OHNE-ZETTEL` ist der nächste Sprint und hat seinen Zuschnitt samt drei Negativfällen; `SILO-OHNE-WERKZEUG`, `ROLLENMATRIX-OHNE-PRUEFUNG` und `RECHERCHE-LIEST-IHRE-BIBLIOTHEK-NICHT` hängen daran. Der letzte ist der überraschendste: Der Recherche-Agent füllt eine Bibliothek, die er selbst nie befragt.
- **18. August 2026** — Chat 151 — **der Rückweg ins Wissen ist gebaut** (`novaberg-agent-dateien_k.md` §4b): Zuordnung über die Zusammenfassungen, Einarbeitung mit chirurgischem Schnitt, Verstärkung der Bibliothekszeile, ausgelöst von der Promotion. **Offen bleiben zwei der drei Wege** — das Einprägsame und das Zugehörige — und die Idempotenz, die heute allein am Modellaufruf hängt; beides in der Fundliste. Dazu **`WIS-8-STUFE-2` geschlossen**: Der Zoom hat seinen Aufrufer, gemessen an einem echten Turn; als Rest bleibt `zeilen_lesen` ohne Aufrufer.
- **18. August 2026** — Chat 150 — neuer Block **aus dem Bau der Enricher-Quelle** mit `AUFZEICHNUNGEN-QUANTIL`, `AUFZEICHNUNGEN-BODEN-NACHZIEHEN` und `SALIENZKURVE-UNTEN-ZU-STEIL`, alle drei ohne Band. Der dritte ist **entschieden, aber nicht gebaut**: Der Exponent der Salienzkurve geht von 0,5 auf **1,16**, roh 0,3 bildet dann auf 0,40 ab statt auf 0,674. Er steht hier statt im Dateien-Konzept, weil die Kurve drei Speicher trägt und ihre Änderung 2394 gespeicherte Werte neu bewertet — **ein eigener Sprint, ausdrücklich nicht nebenbei.** Der erste ist die nicht gebaute Hälfte der Schwelle und **nicht rechenbar, bevor die mitlaufende Verteilung existiert**; der zweite ist der Vorbehalt zum gemessenen Boden in haltbarer Form.
- **18. August 2026** — Chat 149 — **`RAUCHTEST-ANWENDUNG-IMPORT`** neu: fünf Zeilen, die die Anwendung importieren und die Route-Tabelle zählen; gemessen sind **0 von 126** Testdateien, die das heute tun, und eine Typannotation legte den Dienst deshalb unbemerkt lahm. **`WIS-8-STUFE-2` zweimal neu bewertet**: Die Leseschicht hat seit heute ihren ersten Produktivaufrufer — der Wächter ruft `struktur_analysieren` —, offen bleibt der Zoom (`block_lesen`, `zeilen_lesen`, `datei_grep`).
- **16. August 2026** — **der Engpass der Reihe 3 ist vermessen** — der Platz zu rund 93 % besetzt, 89 % der Laeufe an `recherche`, Rueckstand 583, Abfluss rund 20 verwertbare Ergebnisse am Tag; `SHADOW-QUEUE-RUECKSTAND-UNGEMESSEN` und `PIXIE-EIN-SLOT-BLOCKIERT-ALLES` haben damit ihre Zahl und bleiben trotzdem offen, weil ein Punkt keine Reihe ist. `RECHERCHE-ZWISCHENDESTILLATION-OHNE-GRUND` hat seinen Grund: eine geerbte Frist von 300 s, nicht der Inhalt des Schritts — behoben ueber `F-FRIST-1`, die Frage nach dem Sinn des Schritts bleibt offen und ist schwerer geworden. Neu als fuenfter Aspekt des Engpasses: Der Fehlversuchspfad loescht **hart** und waehlt nach *hoher* Salienz aus.
- **16. August 2026** — `SELBSTAUSKUNFT-OHNE-LESER` in den Block **die Gegenrichtung der Doku-Prüfung** aufgenommen — **das erste Fundstück genau der Klasse, die `KANAL-OHNE-GEGENSTUECK` beschreibt** — und kein Werkzeug hat es gefunden, sondern die Unterscheidung zwischen Anmeldung und Vorbedingungs-Auflösung: 14 von 14 Agenten deklarieren ihre Fähigkeiten, `AgentRegistry.beschreibungen()` baut daraus den Planner-Prompt, und kein Produktivcode ruft ihn auf.
- **16. August 2026** — neuer Block **die Gegenrichtung der Doku-Prüfung** mit `KANAL-OHNE-GEGENSTUECK` und `NAMENSREGELN-JENSEITS-DER-FORM`, beide ohne Band — die Klasse, die die drei Kriterien vom selben Tag prinzipiell nicht finden können.
- **16. August 2026** — Block **aus dem Halten der Konventionen** mit `PENDING-AGENT-INS-PAYLOAD` und `SSE-REST-IM-ENDPUNKT`, beide ohne Band.
- **16. August 2026** — Block **die Fachspeicher bekommen ihre Agenten** mit `FACHSPEICHER-AGENTEN`, `FAKTEN-BINDUNG-OHNE-VERFALL` und `REEMBED-WISSENSSPEICHER`, alle ohne Band. Die Trennlinie ist der Fremdschlüssel: Eine Fakten-Entität, auf die einer zeigt, verfällt nicht — die Bindung darauf darf.
- **16. August 2026** — neuer Block **das Messinstrument der Zustellung** mit `ZUSTELLUNG-ABBRUCH-UNGEZAEHLT` und `RIEGEL-5-7-OHNE-EINTRAG` — die zwei Reste der Protokollpflicht, die mit dem Fall der stündlichen Decke von einer Datenlücke zur Lücke im Messinstrument geworden sind.
- **16. August 2026** — `EIGENZEIT-BAUTEILE` geschlossen bis auf die benannten Reste — alle sechs Bauteile stehen, mit Riegel 2 ist die stündliche Decke gefallen.
- **16. August 2026** — Block 15.08. mit `DOKU-VOLLPRUEFUNG` und `NACHZUG-KANDIDATEN-GATE`; `EIGENZEIT-BAUTEILE` fortgeschrieben — E, F, C, A, B gebaut, von D die Voraussetzung und Riegel 1.
- **9. August 2026** — Chat 134 — **die Rangordnung steht**, siehe den gleichnamigen Abschnitt. Gemessen: 184 offene Eintraege, davon **18 mit Prioritaet und 166 ohne** — die Prioritaet ist Pflichtteil und fehlte in neun von zehn Faellen, waehrend die vorhandenen je Eintrag beim Anlegen gesetzt und nie gegeneinander gehalten wurden. Statt Einzelwerten jetzt **vier Baender und eine Tabelle**, gewichtet nach Zugehoerigkeit zu einer der vier laufenden Reihen. Band A traegt **zwei** Eintraege, und die Zahl ist die Aussage: Ein Band, das zwanzig fasst, ist dasselbe wie „hoch" mit siebenundzwanzig. Beim Aufstellen hat sich ein Eintrag selbst aus Band A herauskorrigiert — `PROFIL-HISTORIE-FEHLT` trug die Widerlegung seit dem 02.08. im eigenen Text.
- **9. August 2026** — Chat 133 - **41 Eintraege aus der klassifizierten Fundliste**, jeder mit Kennung, Prioritaet und der Zeile *Was fertig waere*: Ein Eintrag, dessen Abschluss niemand erkennen kann, wird nie geschlossen. **Vier davon beschreiben denselben Engpass von vier Seiten** - ein serieller Platz fuer alle Hintergrundarbeit, ein Lauf, der ihn ueber seine eigene Zeitgrenze haelt und danach mit vollem Anspruch zurueckkehrt, 230 Auftraege an zwei Agenten, die es nicht gibt, und ein Rueckstand von 649, dessen Abfluss nie gemessen wurde. **Wer einen davon einzeln angeht, misst die Wirkung der anderen drei mit** - das steht bei allen vieren dabei. Zwei weitere haengen an einer einzigen Zahl: sechs Dokumente rechnen mit einem achtfach falschen Kontextfenster, und ein Verarbeitungsschritt komprimiert verlustbehaftet gegen genau diese Grenze.
- **1. August 2026** — spät Epic „Client WebSocket-Umbau" aus Chat 60 **abgeschlossen** — der SSE-Kanal trägt nur noch die Bestätigung, alle Stufen gehen über den WebSocket; darüber hinaus liegt jetzt eine Eingangs-Queue vor Pfad 1. Zwei Reste benannt, beide in der Fundliste.
- **1. August 2026** — Abschnitt „Charakterbildung messen" ergänzt — der nächste Sprint, mit `PROFIL-HISTORIE-FEHLT` und `PAARLISTE-FEST` als Voraussetzungen.
- **31. Juli 2026** — abends — `HALTUNG-KNOTEN-FEHLT` geschlossen, `HALTUNG-SPANNENENDEN-OFFEN` um die erste Messung am echten Turn ergänzt.
- **31. Juli 2026** — Abschnitt „Haltungsraum — der unterbrochene Sprint" ergänzt — vier Einträge: der fehlende Knoten, das fehlende Protokoll, die offenen Spannenenden und die abzulösende Längenregel.
- **31. Juli 2026** — Abschnitt „Zeitparser und Kalibrierung" ergänzt — vier Einträge aus dem Korpus-Erstlauf und der Neuerhebung der Positions-Kontrolle.
- **31. Juli 2026** — Chat 117, zwei KZG-Einträge gegen den Code nachgezogen. Kern: Chat 111
