# Novaberg — Bugs: Antwortpfad — Gesprächsvektor, Responder, Verfasser, Prompts

**Inhalt:** die offenen Defekte dieses Gegenstands, ~~46~~ → ~~48~~ → ~~50~~ → ~~52~~ → ~~51~~ → 54 Eintraege (24.10.2026: `SACHLAGE-RECHERCHE-WIEDERHOLT-IM-FOLGETURN`, `SACHLAGE-WARNUNG-NACH-OFFEN-AM-LATENTEN-OBJEKT` und `SACHLAGE-SYMBOL-GILT-ALS-PLATZHALTER` neu aus der Klassifizierung der Funde vom 23.10.2026, dazu ein Nachtrag an `TIMELINE-LESEPFAD-INSTABIL`; 23.10.2026: `SACHLAGE-PLATZHALTER-ALS-WERT` behoben und am Modell gemessen, ins Archiv; 22.10.2026: `SACHLAGE-PLATZHALTER-ALS-WERT` und `SACHLAGE-FAKT-DECKT-MIT-UMSCHREIBUNG` neu aus der Messung am Modell; 20.10.2026: `PLANNER-ZIEL-FUEHRT-ZU-DIENST-OHNE-EMPFANG` und `SALIENZ-ZAEHLT-FAKTEN-AUFTRAG` neu — die Zahl ist die des Findemittels; 17.10.2026: drei neu aus der Simulation `simnachher4`, `NOTIZAUFTRAG-GEHT-AN-TIMELINE` ins Archiv), je mit `**Kategorie:** ANT`.
**Wegweiser:** [`novaberg-bugs.md`](novaberg-bugs.md) — Kopf, Form eines Eintrags, Rangfolge, Verlauf. **Findemittel ueber alle Teile:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Archiv:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Register** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

---

## 24.10.2026 — aus der Klassifizierung der Funde vom 23.10.2026

Drei Kennungen aus den Funden vom 23.10.2026 (Fundliste, *Umgezogen — 24.10.2026*), am Code gelesen gegen HEAD `6b37234`, nicht gelaufen. Ein vierter Fund derselben Klassifizierung ist keine neue Kennung, sondern ein Nachtrag an `TIMELINE-LESEPFAD-INSTABIL` (in dieser Datei). Die übrigen vier Bugs stehen in [`novaberg-bugs-gedaechtnis.md`](novaberg-bugs-gedaechtnis.md) und [`novaberg-bugs-wissen.md`](novaberg-bugs-wissen.md).

### `SACHLAGE-RECHERCHE-WIEDERHOLT-IM-FOLGETURN` — ein Termin-Thema wurde in späteren Turns erneut im Web gesucht; am Code wiederholt nur die Recherche der Sachlage eine Suche über Turns

**Kategorie:** ANT

**Rang:** **mittel** — still, im Log stehen nur INFO und WARNUNG. Ein Treffer stünde als *„Nachgeschlagen zu …“* neben `[TERMINE]` im Prompt, und genau diesen Fall nennt das Modul als Grund seiner Sperre. Begrenzt, weil die Beobachtung 0 Treffer hatte und `relevant_hits` Rauschen ohne ein Wort des Objektnamens verwirft. Vergeben am 24.10.2026 gegen HEAD `6b37234`.

**Zustand:** offen — beobachtet am 23.10.2026 in Messturns im Betrieb (aus der Fundliste übernommen); der Mechanismus am Code gelesen am 24.10.2026 gegen `6b37234`. Welcher Weg im beobachteten Turn suchte, ist nicht nachgesehen.

**Befund** `[Code]`: Im Turn suchen zwei Wege im Web, ein dritter im Hintergrund:

- die Recherche der Sachlage (`server/graph/nodes/sachlage.py`, Z. 938–947, → `server/graph/nodes/sachlage_research.py::research_open_property`), deterministisch, einmal je Turn für die erste offene Eigenschaft eines akuten Objekts mit dem Träger `nachschlagen` (`lookup_target`);
- das Werkzeug `web_search` des Thinkers (`server/graph/nodes/thinker.py`), nach Urteil des Modells, erzwungen bei `needs_web`;
- die Recherche im Hintergrund (`server/agents/recherche/suche.py`), nicht im Turn.

Eine Suche über Turns wiederholt am Code nur der erste Weg. Nichts merkt sich eine frühere Suche, auch keine gescheiterte: Nach einem Ausfall aller Anbieter gibt `server/tools/web/search.py` eine leere Liste zurück, oder die Sachlage meldet eine Warnung und lässt `recherche` leer. Der Träger `nachschlagen` wird über `carry_holders` geerbt (`sachlage.py`, Z. 601–633), die Blase lebt `SACHLAGE_VERFALL_SEKUNDEN` = 14400 s, und die Sperre für den eigenen Bestand prüft nur die Äußerung des laufenden Turns (`own_records_cue(aeusserung)`, `sachlage.py`, Z. 944). Ein späterer Turn, der nicht nach dem eigenen Bestand fragt, sucht deshalb zum Termin-Objekt erneut — gegen die Regel des Moduls selbst (Docstring von `sachlage_research.py`: *„Keine Suche zum eigenen Bestand des Nutzers“*).

**Symptom** (Fundliste, 23.10.2026): In Messturns im Betrieb wurde ein Termin-Thema aus einem früheren Turn in drei späteren Turns erneut im Web gesucht; der Anbieter antwortete mit einem HTTP-Fehler, 0 Treffer.

**Wirkung.** Ein Thema aus dem eigenen Bestand des Menschen geht Turn um Turn als Suchanfrage hinaus, und ein Treffer stünde im Prompt wie Wissen über diesen Bestand. Ob das Objekt in den drei späteren Turns akut blieb, entscheidet das Modell je Turn neu; unbelegt.

**Geschlossen, wenn** ein Objekt, zu dem ein Turn die Suche wegen des eigenen Bestands zurückgehalten hat (`withhold_research`), auch in den folgenden Turns nicht gesucht wird, die selbst nicht nach dem Bestand fragen — bezeugt mit einer Folge von zwei Turns und dem Zwilling, in dem ein Objekt ohne Bezug zum Bestand weiter gesucht wird.

**Offen:** welcher Weg im beobachteten Turn feuerte — zu trennen am Serverlog, eng nach Logger: `ki_server.sachlage.research` mit *„Sachlage-Recherche:“* gegen `ki_server.thinker` mit *„Thinker-Tool: web_search“*; ob das Objekt akut blieb; und die **Absicht**, ob schon die ausgehende Anfrage zum eigenen Bestand ein Defekt ist — nach einem Kommentar in `server/tools/web/search.py` geht sie zuerst an einen externen Anbieter, die lokale Metasuche ist der Rückfall (unbelegt, nur aus dem Kommentar).

**Zusammenhang:** [`novaberg-thinking-lage_b.md`](novaberg-thinking-lage_b.md) Scheibe 8 (die Recherche der Sachlage); die `RECHERCHE-*`-Einträge im Backlog betreffen den Recherche-Agenten im Hintergrund, nicht diesen Weg.

---

### `SACHLAGE-WARNUNG-NACH-OFFEN-AM-LATENTEN-OBJEKT` — die Warnung *„… ohne Wert — nach offen“* nennt bei einem latenten Objekt ein Ziel, das nicht gilt, und im Hauptpfad leert die Sachlage `offen` ohne Logzeile

**Kategorie:** ANT

**Rang:** **niedrig** — laut, und das Ergebnis, die Leerung am latenten Objekt, ist gewollt (Smalltalk-Schranke); falsch ist der Text, der ein Ziel nennt, das nicht gilt, und im Hauptpfad fehlt die Meldung der Leerung. Vergeben am 24.10.2026 gegen HEAD `6b37234`.

**Zustand:** offen — am Code gelesen am 24.10.2026 gegen `6b37234`; gefunden am 23.10.2026 beim Bau der Prüfung auf Platzhalter.

**Befund** `[Code]`: `server/graph/nodes/sachlage_form.py::_split_covered` meldet *„… in 'gedeckt' ohne Wert — nach offen: …“* (Z. 228–232 für ein dict, Z. 237–242 für alles andere), bevor das Ziel feststeht. Der Aufrufer `normalize_object_form` (Z. 462–491) übernimmt einen Namen nicht nach `offen`, wenn er schon gedeckt ist, und leert mit `gate=True` `offen` eines latenten Objekts mit der INFO-Zeile *„geleert (Smalltalk-Schranke)“* (Z. 483–488). Der Hauptpfad der Sachlage ruft aber mit `gate=False` (`server/graph/nodes/sachlage.py`, Z. 475); dort leert `merge_same_name_objects` `offen` eines latenten Objekts ohne Logzeile (`sachlage_form.py`, Z. 390). Im Hauptpfad bleibt die Warnung damit unberichtigt stehen.

**Wirkung.** Wer das Log liest, hält eine Eigenschaft für offen, die weggefallen ist. Seit der Prüfung auf Platzhalter (`_is_placeholder`) schlägt die Warnung häufiger an. Am Ergebnis ändert sich nichts.

**Geschlossen, wenn** die Warnung *nach offen* nur sagt, wenn die Eigenschaft in `offen` ankommt, und das Leeren an einem latenten Objekt auch im Hauptpfad (`merge_same_name_objects`) eine Logzeile schreibt — bezeugt mit einem latenten Objekt und dem Zwilling, einem akuten.

**Zusammenhang:** `SACHLAGE-PLATZHALTER-ALS-WERT` (Archiv, [`novaberg-bugs-archiv-antwortpfad.md`](novaberg-bugs-archiv-antwortpfad.md)), seit dessen Bau die Warnung häufiger anschlägt; `SACHLAGE-SYMBOL-GILT-ALS-PLATZHALTER` (in dieser Datei); [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §3.

---

### `SACHLAGE-SYMBOL-GILT-ALS-PLATZHALTER` — ein Symbol als ganzer Wert (`∞`, `€`, `%`) gilt in `gedeckt` als Platzhalter

**Kategorie:** ANT

**Rang:** **niedrig** — laut (Warnung *„ohne Wert — nach offen“*) und nicht beobachtet. Im ungünstigsten Fall wird ein echter Wert nicht abgelegt, und die Eigenschaft wird erneut gefragt oder nachgeschlagen. Vergeben am 24.10.2026 gegen HEAD `6b37234`.

**Zustand:** offen — am Code gelesen am 24.10.2026 gegen `6b37234`, nur der reguläre Ausdruck nachgestellt, nicht das Modul; ungemessen, kein Zeuge. Gefunden am 23.10.2026 beim Bau der Prüfung auf Platzhalter.

**Befund** `[Code]`: `server/graph/nodes/sachlage_form.py::_is_placeholder` (Z. 107–127) normalisiert mit `re.sub(r"[\W_]+", " ", …)` (Z. 117) und gibt bei leerem Rest `True` zurück (Fall (a), Z. 119–120). `∞`, `€`, `%` und `°` sind keine Wortzeichen und werden leer, gelten also als Platzhalter; `½` und `²` bleiben (Unicode-Ziffern), `5 €` bleibt. Der Docstring sagt *„Ob ein Text nur sagt, dass der Wert fehlt“* — ein Symbol sagt das nicht. Die Folge am Code: `_as_covered_value` liefert `None`, und der Name geht mit Warnung nach `offen` (Z. 221–232); dasselbe gilt für Ansprüche des Auflösers über `covered_value`. Dass der Wert dann nicht abgelegt wird, weil `remember_objects` nur aus `gedeckt` ablegt, steht im Archiveintrag `SACHLAGE-PLATZHALTER-ALS-WERT` und ist hier nicht nachgelesen.

**Wirkung.** Ein Wert, der nur aus einem Symbol besteht, gilt als fehlend: Die Eigenschaft geht nach `offen` oder fällt am latenten Objekt weg, und der Wert wird nicht abgelegt. Ob das Modell je ein einzelnes Symbol als Wert schreibt, ist nicht gezählt.

**Geschlossen, wenn** ein Symbol, das allein ein Wert ist, in `gedeckt` als Wert gilt und die Platzhalter des Falls (a) (*„?“*, *„-“*, *„…“*) weiter nicht — bezeugt mit Zeuge und Zwilling.

**Offen:** die **Absicht**, welche Zeichen allein ein Wert sind (`∞`, `€`, `%`) und welche ein Platzhalter (`?`, `-`, `…`); in Frage kommen eine Liste der Platzhalterzeichen oder eine Liste der Wertsymbole. Dazu ungezählt, ob das Modell je ein einzelnes Symbol als Wert schreibt (Bestand von `gedeckt` bzw. `sachlage_eigenschaft`).

**Zusammenhang:** `SACHLAGE-PLATZHALTER-ALS-WERT` (Archiv, [`novaberg-bugs-archiv-antwortpfad.md`](novaberg-bugs-archiv-antwortpfad.md)) — seine Schließbedingung nannte *„?“*, *„unbekannt“* und *„offen“*, Symbole als Werte waren nicht Teil davon; `SACHLAGE-WARNUNG-NACH-OFFEN-AM-LATENTEN-OBJEKT` (in dieser Datei); [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §3.

---

## 22.10.2026 — aus der Messung der Fakten im Angebot der Sachlage am Modell

Zwei Befunde (→ seit dem 23.10.2026 steht hier nur noch `SACHLAGE-FAKT-DECKT-MIT-UMSCHREIBUNG`; `SACHLAGE-PLATZHALTER-ALS-WERT` ist behoben, am Modell gemessen und im Archiv, [`novaberg-bugs-archiv-antwortpfad.md`](novaberg-bugs-archiv-antwortpfad.md)) aus der Messung am Modell des Betriebs vor dem Commit von Teil H und dem Kanal des Erinnerungsankers (Messreihe vom 22.10.2026, Code-Tree `04f823e`; 23 synthetische Äußerungen in fünf Gruppen × 4 Läufe, Bindungen und Mappe als Doppel, kein Schreiben). Die Messung steht in [`novaberg-thinking-lage_m.md`](novaberg-thinking-lage_m.md) Scheibe 13. Am Code gehalten gegen den Code-Tree `04f823e`.

### `SACHLAGE-FAKT-DECKT-MIT-UMSCHREIBUNG` — deckt ein angebotener Fakt eine offene Eigenschaft, steht der Satz des Auflösers in `gedeckt`, nicht der Wert des Fakts
**Kategorie:** ANT

**Rang:** **niedrig** — still, aber ohne Wirkung, solange die Tabelle `fakten` leer ist (am 22.10.2026 0 Zeilen): Dann wird kein Fakt angeboten. → 23.10.2026: Die Tabelle ist nicht mehr leer — der Fakten-Agent schrieb in Messturns im Betrieb an einem Prüf-Nutzer 3 Fakten; die Bedingung, an der der Rang hängt, gilt seither nur noch für Paare ohne Fakten. Regel (c) begrenzt das Wiederkehren: Die abgelegte Eigenschaft trägt den Fakt als Quelle und fehlt im Angebot, solange genau dieser Fakt angeboten ist. Vergeben am 22.10.2026 gegen den Code-Tree `04f823e`.

**Zustand:** offen — gemessen am Modell am 22.10.2026, am Code gelesen; nichts gebaut.

**Befund** `[gemessen]`: `graph/nodes/sachlage_resolver.py:844-845` (`_apply_claim`) übernimmt den Wert eines Treffers wörtlich nur, wenn sein `subject` die offene Eigenschaft trifft (`_match_open`: wörtlich, oder durch Enthaltensein ab vier Zeichen); sonst ist der Satz des Auflösers (`inhalt`) der Wert. Für einen Fakt setzt `fact_hits` als `value` Objekt oder Wert des Fakts und als `subject` die Beziehung (`sachlage_resolver.py:545-548`, `entry.relation`). Die Beziehungen des Kanons (`arbeitet_als`, `wohnt_in`, `hat_hobby` …) heißen anders als die offenen Eigenschaften der Sachlage (*Beruf*, *Wohnort*, *Instrument*), und die Bedingung greift für einen Fakt praktisch nie. In der Messreihe vom 22.10.2026 waren es 18 von 18 Deckungen aus einem Fakt, etwa *„Sie arbeitet als Hebamme.“* statt *Hebamme*.

**Wirkung.** `remember_objects` legt den Satz samt Pronomen als Wert der Eigenschaft ab (`memory/sachlage_properties.py:192`); der `[SACHLAGE]`-Block und jeder spätere Leser sehen *„Beruf: Sie arbeitet als Hebamme.“*. Fehlt der Fakt später im Angebot — Grenze, Ausfall der Mappe —, kehrt der Satz als gespeicherter Wert zurück. Die Schutzregel aus Scheibe 11 (*der Wert gilt wörtlich nur an seiner eigenen Eigenschaft*, gegen *»Alter: 970 Jahre«* als Masse) wirkt hier richtig, nur trägt ein Fakt keine Eigenschaft, an der sie greifen könnte.

**Reproduktion.** Einer gebundenen Person einen Fakt `arbeitet_als` → *Hebamme* geben und nach ihrem Beruf fragen, sodass sie akut ist und *Beruf* offen; nach dem Auflöser `gedeckt["Beruf"]` lesen. Ohne Modell: `_apply_claim` mit einem Treffer `value="Hebamme"`, `subject="arbeitet_als"` und dem Anspruch `inhalt="Sie arbeitet als Hebamme."` für die offene Eigenschaft *Beruf*.

**Geschlossen, wenn** eine Deckung aus einem Fakt den Wert des Fakts in `gedeckt` trägt, nicht den Satz des Auflösers, ohne dass ein Fakt eine fremde Eigenschaft wörtlich deckt — bezeugt mit Zeuge und Zwilling und am Modell an einer Reihe gezählt.

---

## 20.10.2026 — bei der Prüfung des Schreibauftrags an den Fakten-Agenten

### `SALIENZ-ZAEHLT-FAKTEN-AUFTRAG` — die Zählung der Writes in der Salienz enthält den Fakten-Auftrag
**Kategorie:** ANT

**Rang:** **niedrig** — still, aber nur in Log und Spur: Das Verhalten ändert sich nicht, und der Grund einer Verwerfung steht weiter in den Fehlereinträgen. Vergeben am 20.10.2026 gegen den Tree `0ca9da6`.

**Zustand:** offen — am Code gelesen am 20.10.2026 bei der Prüfung des Baus, nicht gemessen; wirkt ab dem Commit des Schreibauftrags.

**Befund** `[Code]`: Der Knoten der Salienz übernimmt `pending_writes` samt dem Fakten-Auftrag aus der Sachlage (`graph/nodes/salience.py`, um Z. 597). `span_end` meldet `pending_writes: len(pending)` (um Z. 1034), und der Kommentar darüber sagt: *„Weniger pending_writes als Segmente heisst, dass unterwegs mindestens eines verworfen wurde“*. In praktisch jedem gerechneten Turn steht jetzt ein Write mehr, und ein einzelnes verworfenes Segment ist an diesen Zahlen nicht mehr zu sehen. Ebenso ist die Zeile *„Salienz: N pending_writes angelegt“* (um Z. 941) um eins zu hoch.

**Geschlossen, wenn** die Salienz in Spur und Log nur ihre eigenen Writes zählt oder den Fakten-Auftrag getrennt ausweist, und der Kommentar das sagt.

---

## 17.10.2026 — aus der Simulation `simnachher4` an einem Prüf-Nutzer

Drei Befunde aus einer Simulation an einem frischen Prüf-Nutzer (`labor/2026-10-15_sim_timeline_notizen/simnachher4/`, Samstag, 17.10.2026, 14:49–18:07 UTC, auf `a26b2cd`; dieselben 24 Sätze wie im Vorlauf `simnachher3`), von Hand gegen den Bestand im Augenblick der Frage bewertet. Die Spur im Pipeline-Log ist nur nach `turn_id` gelesen, das Serverlog nur nach Logger und Zeitfenster. Am Code gehalten gegen HEAD `ae05667`. Ein vierter Befund desselben Laufs steht in [Wissen](novaberg-bugs-wissen.md) (`TIMELINE-LESEN-SUCHT-MIT-FUELLWORT`).

### `PRUEFER-OHNE-LESESTAND` — die Prüfer hinter dem Verfasser prüfen gegen ein Fenster ohne den Lesestand des Turns
**Kategorie:** ANT

**Rang:** **hoch** — still: Eine richtige Auskunft über gelesene Termine wird zu einer falschen geändert oder mit einem falschen Korrektursatz versehen, und der Mensch glaubt sie. Bei derselben Frage in 2 von 2 Läufen (`simnachher3`, `simnachher4`). Vergeben am 17.10.2026 gegen HEAD `ae05667`.

**Zustand:** offen — gemessen am 17.10.2026 in einer Simulation auf `a26b2cd`, am Code gehalten gegen HEAD `ae05667`.

**Befund** `[Code]`: Den Lesestand des Turns — das Ergebnis des Lesens hinter dem Router im Kanal `appointment_reading`, im Prompt der Block `[TERMINE]` — liest als einziger Knoten der Verfasser (`graph/nodes/verfasser.py`). Thinker, Speicherprüfung des Tribunals und Korrektor sehen ihn nicht. Sie kennen nur die Zeilen `[Timeline/…]` des proaktiven Fensters, drei Tage zurück und vierzehn voraus (`TIMELINE-LESEPFAD-INSTABIL`, *Gebaut am 15.10.2026*). Liegt ein gelesener Termin außerhalb dieses Fensters, prüfen sie die Antwort gegen einen Bestand, in dem er fehlt. Für die Speicherprüfung ist die Grenze benannt: *„Bestand, den der Turn ohne Dienst gelesen hat, deckt nichts … Nicht gemessen, ohne Zeugen.“* (`novaberg-node-tribunal.md`, *Was die Prüfung nicht kann*). Hier ist sie gemessen, und dieselbe Lücke hat der Thinker.

**Erste Erscheinung — der Thinker „korrigiert“ ein richtiges Datum zu einem falschen** `[gemessen]` (Satz 5, die Frage nach dem letzten Friseurbesuch; im Bestand Donnerstag, 08.10.2026, 15:00, neun Tage zurück):

- Der Router suchte `search` *Friseur* `backward`, und der Leseweg im Turn fand den Termin. Der Entwurf nannte einen Donnerstag mit Uhrzeit (`treffer_antwort`).
- Der Thinker meldete: *„Der Wochentag für den genannten Termin ist falsch berechnet (Wenn der Sonntag der 18.10.2026 ist, dann war Donnerstag tatsächlich der 15.10.2026)“*. Hinaus ging *„Donnerstag, den 15.10.2026“*. Entwurf und Endfassung sind beide 135 Zeichen lang; getauscht wurde also wohl nur das Datum.
- **In `simnachher3` derselbe Mechanismus:** Der Entwurf nannte richtig *„Mittwoch, 07.10., um 15 Uhr“*. Der Thinker fand mit `memory_search(Friseur)` nichts, und hinaus ging *„keinen früheren Termin gefunden“* (Serverlog vom 16.10.2026, 21:21 UTC).
- Umgekehrt rettete der Thinker in `simnachher4` Satz 3 und 19, weil der Termin in seinem Fenster lag.

**Zweite Erscheinung — die Speicherprüfung beanstandet eine wahre Auskunft über gelesenen Bestand** `[gemessen]` (Satz 6, die Frage nach Terminen im November; im Bestand der Elternabend am Samstag, 07.11.2026, 19:00):

- Der Router stellte nicht zu; der Leseweg im Turn las `range` 01.11.–30.11. und fand 1 Termin. Der Thinker prüfte mit `timeline_check(2026-11-07)` und urteilte *„Antwort ist korrekt“*.
- Die Speicherprüfung fand *eingetragen* in der Form `zustand`, ohne schreibenden Dienst. Der Bestandsabgleich half nicht (`kein_akutes_objekt_mit_zeit`), denn das Objekt *Termine im November* trägt keine Zeit.
- Drei Runden ergaben `nicht_belegt`. Die zwei Korrekturen behielten den Satz und stellten nur *„Du möchtest wissen, ob du im November schon Termine hast:“* voran.
- Nach dem Code (`graph/nodes/tribunal.py:364`) ging die Antwort mit dem Korrektursatz hinaus: *„(Korrektur: Dafür wurde kein Eintrag angelegt — gespeichert ist davon nichts.)“* In der Spur fehlt sie, weil der Graph danach an der Rekursionsgrenze abbrach (`TURN-ROH-FEHLT-BEI-ERZEUGTER-ANTWORT`, novaberg-bugs-charakter.md).
- Der Mensch liest also, der Elternabend sei eingetragen, und im selben Atemzug, es sei nichts gespeichert. **In `simnachher3` dieselbe Lage in Satz 21.**

**Eine Wurzel, zwei Erscheinungen:** Beide Prüfer urteilen über eine Auskunft, deren Grundlage sie nicht sehen. Der Thinker ersetzt sie durch das, was sein Fenster hergibt; die Speicherprüfung hält die Wiedergabe gelesenen Bestands für eine Speicherbehauptung.

**Wirkung.** Der Lesestand macht Auskünfte außerhalb des proaktiven Fensters erst möglich — der letzte Friseurbesuch, ein Monat, ein ferner Termin —, und genau dort prüfen Thinker und Speicherprüfung gegen einen Bestand, in dem der Termin fehlt. Was danach hinausgeht, ist die Endfassung: ein falsches Datum, ein *keiner* statt des Termins oder eine wahre Auskunft mit dem Satz, es sei nichts gespeichert. Der Mensch hat keinen Anlass, ihr zu misstrauen. Innerhalb des Fensters wirkt dieselbe Prüfung als Rettung (Satz 3 und 19).

**Verwandt:** Die Vermutung in `TIMELINE-LESEPFAD-INSTABIL` zur Friseurfrage (*nur das proaktive Fenster gelesen*) ist damit widerlegt; gelesen wurde. `TIMELINE-NENNT-ABGELAUFENEN-TERMIN-ALS-KOMMENDEN` (novaberg-bugs-wissen.md) steht in der Sache nahe. Dieselbe Korrekturrunde trägt einen zweiten Fehler, `KORREKTUR-ERFINDET-WUNSCH` (unten).

**Reproduktion.** Einem Prüf-Nutzer einen Termin säen, der außerhalb des proaktiven Fensters liegt (mehr als drei Tage zurück oder mehr als vierzehn voraus), und nach ihm fragen; im Pipeline-Log die Zeilen `Problem` des Thinkers und die Runden der Speicherprüfung lesen.

**Geschlossen, wenn** eine Auskunft über Termine, die der Turn gelesen hat, von keinem Prüfer gegen ein Fenster ohne diesen Lesestand geändert oder als unbelegt beanstandet wird — gemessen an einem Prüf-Nutzer mit einem Termin außerhalb des proaktiven Fensters.

### `KORREKTUR-ERFINDET-WUNSCH` — die Korrektur einer Speicherbehauptung legt dem Menschen auf eine Lesefrage einen Wunsch in den Mund
**Kategorie:** ANT

**Rang:** **mittel** — still, aber ohne Schaden im Kalender: Geschrieben wird nichts, aber die Antwort schreibt dem Menschen einen Wunsch oder Auftrag zu, den er nicht geäußert hat. 2 von 4 Korrekturen in `simnachher4`. Vergeben am 17.10.2026 gegen HEAD `ae05667`.

**Zustand:** offen — gemessen am 17.10.2026 in einer Simulation auf `a26b2cd`, am Code gehalten gegen HEAD `ae05667`.

**Befund** `[Code]`: Der Korrekturauftrag der Speicherprüfung verlangt, jeden beanstandeten Satz *„als Wiedergabe dessen, was der Nutzer gesagt oder sich gewuenscht hat — in der Form „Du moechtest …" oder „Du hast … genannt"“* zu schreiben (`utils/storage_claims.py`, um Z. 945). Das stimmt, wenn der Mensch etwas beauftragt oder genannt hat. Satz 8 des Laufs ist so ein Fall: *„Du hast Physiotherapie am Mittwoch um 16 Uhr genannt!“* Auf eine Lesefrage gibt es aber keinen Wunsch, und die Form erfindet einen.

**Gemessen** `[gemessen]`:

- **Satz 2** (*„Hab ich morgen was vor?“*): Der Entwurf schrieb *„Ich hab den Termin schon fix für dich eingetragen, damit du ihn nicht vergisst.“* Der lesende Agent deckt das nicht mehr (Runde 0 `nicht_belegt`, `abgeschlossen: [timeline]`, `geschrieben: []`). Die Korrektur machte daraus *„Du möchtest, dass ich ihn für dich fix eintrage, damit du ihn nicht vergisst.“* Der Mensch hat nur gefragt.
- **Satz 21:** Die Floskel *„Damit haben wir jetzt auch die letzten anstehenden Termine für das Wochenende erledigt und alles ist geklärt.“* traf den Bestandsabgleich mit `gefunden_nicht_genannt`, sein erster Lauf im Betrieb. Daraus wurde *„Du möchtest, dass alle anstehenden Termine für das Wochenende erledigt und geklärt sind sowie alles in der Liste steht …“*.
- **`simnachher3`, Satz 19:** *„Du möchtest am Sonntag einen Termin beim Steuerberater …“*, aus dem wahren Satz *„Für Sonntag ist der Termin beim Steuerberater Hoffmann um 14:30 Uhr eingetragen“*.

Von den vier Korrekturen in `simnachher4` legten zwei einen Wunsch in den Mund (Satz 2 und 21). Die dritte (Satz 6) behielt den Satz und stellte eine Wiedergabe der Frage voran (`PRUEFER-OHNE-LESESTAND`, oben), die vierte (Satz 8) war richtig.

**Seit `57e9eb9` (17.10.2026) trifft es öfter.** Ein Lesevorgang deckt keine Schreibbehauptung mehr (`novaberg-node-tribunal.md`, *Ein Lesevorgang deckt nicht*). Jede Lesefrage, deren Entwurf eine Schreibung behauptet, geht deshalb jetzt in diese Form. Vorher deckte der Lesevorgang sie, und sie ging als falsche Bestätigung hinaus (`FALSCHE-BESTAETIGUNG-WIRD-ERINNERUNG`, novaberg-bugs-gedaechtnis.md); in `simnachher4` gingen 0 Schreibbehauptungen auf Lesefragen hinaus.

**Abgrenzung:** `novaberg-node-tribunal.md` benennt, dass die Wiedergabe-Form dem Nutzer etwas in den Mund legt, nur für den Fall *gelesener Bestand*. Für eine erfundene Behauptung nimmt es die Form als wahr an; gemessen ist hier das Gegenteil.

**Wirkung.** Der Mensch liest, er habe etwas gewünscht oder beauftragt, das er nicht gesagt hat. Im Kalender entsteht nichts, aber die Antwort ist an dieser Stelle falsch über ihn selbst, und sie geht als Endfassung hinaus.

**Reproduktion.** Eine Lesefrage stellen, deren Entwurf eine Schreibung behauptet (*„Hab ich morgen was vor?“*), und die Endfassung nach der Korrekturrunde lesen.

**Geschlossen, wenn** auf eine Lesefrage keine Korrektur dem Menschen einen Wunsch oder Auftrag in den Mund legt.

### `SACHLAGE-OBJEKT-OHNE-NAMEN` — ein Objekt ohne Namen verwirft die ganze Sachlage des Turns
**Kategorie:** ANT

**Rang:** **niedrig** — laut, mit festgelegtem Rückfall: Jeder Ausfall steht als Fehlerzeile im Serverlog, und die Sachlage des Vorturns gilt weiter; der Planner verwirft dann die Nähe und folgt dem Router. Vergeben am 17.10.2026 gegen HEAD `ae05667`.

**Zustand:** offen — gemessen am 17.10.2026 in einer Simulation auf `a26b2cd` und im Serverlog (nur gezählt), am Code gehalten gegen HEAD `ae05667`.

**Befund** `[gemessen]`: In Satz 20 (Reifenwechsel auf Freitag) schrieb das Modell der Sachlage einen verstümmelten Schlüssel. Serverlog, 17:37:01 UTC: `Sachlage: Objekt ohne Namen: {'name: ': ' , '} — verworfen`. Am Code: `graph/nodes/sachlage.py::_validate_objects` gibt schon bei einem einzigen Objekt ohne Namen `None` zurück, und die Sachlage des Vorturns gilt weiter (`lage=ausfall_uebernommen`). Der Planner verwarf darauf die Nähe (*„Sachlage vom Vorturn uebernommen (Ausfall)“*) und folgte dem Router; hier blieb das ohne Schaden. In `simnachher3` fiel die Sachlage in Satz 3 und 9 ebenso aus.

**Menge** `[gemessen]`, nur gezählt: Im Serverlog stehen vom 15. bis 17.10.2026 11 solche Ausfälle, 8 *Objekt ohne Namen* und 3 `JSONDecodeError`. Ein älterer Anteil steht als Kommentar im Planner (`graph/nodes/planner.py`, *114 von 542 Sachlagen in 14 Tagen*, gemessen am 17.09.2026), nicht nach Grund getrennt.

**Wirkung.** Der Turn verliert seine eigene Sachlage: Die Leser dahinter (Router, Planner, Speicherprüfung) arbeiten auf dem Stand des Vorturns, und ein einziges verstümmeltes Objekt verwirft alle übrigen mit. Der Rückfall ist laut und festgelegt; teuer wird er erst, wenn er häufig ist, und wie häufig er an der Form liegt, ist nicht gezählt.

**Reproduktion.** Nicht gezielt herstellbar; im Serverlog die Fehlerzeilen des Sachlage-Knotens zählen, *Objekt ohne Namen* getrennt von `JSONDecodeError`.

**Geschlossen, wenn** der Anteil der Turns mit `lage=ausfall_uebernommen` wegen Form gezählt und eine Abhilfe gemessen ist.

---

## 17.10.2026 — aus der Messung des gemeinsamen Lesewegs der Termine

### `SACHLAGE-KALENDER-VERFEHLT-OBJEKTNAMEN` — das Angebot der Sachlage liest zu einem frei benannten Objekt keinen Termin
**Kategorie:** ANT

**Rang:** **mittel** — still: Das Serverlog zählt *„Angebot aus Kalender 0“*, aber nichts sagt, dass es Termine gegeben hätte. Die Antwort bekommt die Termine trotzdem über den Block `[TERMINE]`; was ausfällt, ist die Deckung offener Eigenschaften aus dem Kalender und damit der Weg, auf dem Scheibe 13 Termine in die Sachlage holt. Vergeben am 17.10.2026 gegen HEAD `5009f47`.

**Zustand:** offen — behoben im Tree `d810399` (22.10.2026, Teil H, committet), Schließbedingung bezeugt (12 Termine → 5, 3 → 3); am Modell ist die Kalender-Seite nicht gemessen — der Kalender der Messreihe vom 22.10.2026 war leer —, die Messung im Betrieb steht aus (*Geschlossen, wenn*). Das Angebot trägt seither höchstens `SACHLAGE_BESTAND_KALENDER_MAX` = 5 Kalenderzeilen in der Ordnung des Lesewegs der Termine, die Zählzeile nennt gelesene und weggelassene (*„Angebot aus Kalender 12 gelesen, 7 weggelassen …“*), und ein voller Monat verdrängt Pool und Aufzeichnungen nicht mehr; Zeugen in `tests/test_sachlage_fakten_angebot.py` (`TheCalendarIsCappedTest`: 12 Termine → 5 Zeilen, Fakten und Pool bleiben; Zwilling 3 → 3), Gegenproben wie vorhergesagt. Davor: offen — **behoben im Tree,** ~~**nicht committet**~~ → **committet als `250a5c1`** (21.10.2026, Tree `463fa81`): Das Fenster kommt aus einem Zeitbezug am akuten Objekt, den der Server aus Äußerung und Name ableitet und über den Namen in den Folgeturn trägt (`graph/nodes/sachlage_zeitbezug.py`; `novaberg-thinking-lage_e.md` Nr. 36, 37) — ein Zeitraum über `range_window`, ein Titel nur bei einer Frage nach dem Zeitpunkt, über `search_window` in beide Richtungen; ohne Zeitbezug kein Fenster und kein Rückfall auf den Namen. Zeugen, sieben Gegenproben rot wie vorhergesagt; am Modell des Betriebs gemessen, ohne Turn (`novaberg-thinking-lage_m.md` Scheibe 13). Geschlossen mit dem Commit und der Messung im Betrieb an einem frischen Prüf-Nutzer: *„Was steht im November an?“* und *„Wann muss ich zum Zahnarzt?“*, je mit Folgeturn — die Zählzeile *„Sachlage-Aufloeser: Angebot aus Kalender N“* zeigt 3 bzw. 2. Davor: offen — gemessen am 17.10.2026, 20:52–21:14 UTC, gegen HEAD `5009f47`.

**Befund** `[gemessen]`: Der Frame-Auflöser liest Termine je akutem Objekt der vorigen Blase. Das Fenster bildet er aus dem **Namen** des Objekts: Nennt der Name einen Zeitraum, ist es dieser Zeitraum, sonst eine Titelsuche (`graph/nodes/sachlage_resolver.py::_calendar_window`). Den Namen vergibt der Sachlage-Call frei. An einem frischen Prüf-Nutzer mit sieben gesäten Zeilen (synthetisch, Titel und Zeiten vom Messwerkzeug) hieß das Objekt nach *„Was steht im November an?“* **Novemberereignisse** und nach *„Wann muss ich zum Zahnarzt?“* **Zahnarzttermin**. Der erste Name nennt für `utils/zeitparser.py::named_period` keinen Zeitraum, der zweite steht in keinem Titel (*Zahnarzt Dr. Berger*). Das Angebot war in **3 von 3** Turns leer; das Serverlog zählte im echten Turn *„Angebot aus Kalender 0“*. Derselbe Leseweg mit dem Namen *November* liefert genau die drei Novembertermine, mit *Zahnarzt* beide Zahnarzttermine, den vergangenen gekennzeichnet — er ist richtig, nur der Name trifft ihn nicht (`labor/2026-10-17_messung_a2_leseweg.py`, Ausgabe daneben).

**Älter als der Leseweg:** Vor dem 17.10.2026 suchte der Auflöser mit demselben Namen über `find_by_keyword` und fand ebenso nichts. Der gemeinsame Leseweg hat das nicht verursacht, aber auch nicht behoben.

**Wirkung.** Eine offene Eigenschaft wie *Uhrzeit* an einem Termin-Objekt bleibt offen, obwohl der Termin im Bestand steht, und die Sachlage weiß von ihren Terminen nur, was das Gespräch sagt. Jeder Leser der Sachlage nach dem Auflöser erbt das, auch das geplante Faktengedächtnis (`novaberg-memory-fakten_b.md`, F1).

**Reproduktion.** Einem Prüf-Nutzer Termine im November säen und *„Was steht im November an?“* fragen; danach im nächsten Turn die Zählzeile *„Sachlage-Aufloeser: Angebot aus Kalender N“* lesen.

**Geschlossen, wenn** an einem frischen Prüf-Nutzer eine Frage nach einem Zeitraum und eine nach einem Termin-Titel im Folgeturn ein Angebot mit ~~genau den Terminen ergibt, die der Block `[TERMINE]` nennt~~ → den Terminen ergibt, die der Block `[TERMINE]` nennt — beim Zeitraum genau diese, beim Titel mindestens diese, in beide Richtungen, vergangene gekennzeichnet (21.10.2026, `novaberg-thinking-lage_e.md` Nr. 37). → Seit dem 22.10.2026 trägt das Angebot höchstens `SACHLAGE_BESTAND_KALENDER_MAX` = 5 Kalenderzeilen: *genau diese* gilt bis zu dieser Grenze, darüber stehen die ersten fünf in der Ordnung des Lesewegs, und die übrigen sind als weggelassen gezählt (bezeugt mit 12 → 5 und 3 → 3). ~~Wie das Fenster statt aus dem freien Namen entstehen soll (aus dem Wortlaut des Turns, einem Zeitbezug am Objekt oder einem gelernten Kanon), ist nicht entschieden.~~ → **Entschieden am 21.10.2026** (`novaberg-thinking-lage_e.md` Nr. 36): ein Zeitbezug am Objekt, den der Server aus Äußerung und Objektnamen ableitet; ohne Zeitbezug bleibt die Eigenschaft offen und Nova fragt. ~~Vor dem Bau die Messung der Annahmen über Name und Akutheit an einem Prüf-Nutzer.~~ → Vor dem Bau gemessen am 21.10.2026, am Modell des Betriebs an synthetischen Reihen ohne Turn, nicht an einem Prüf-Nutzer: Ein akutes Objekt trug das Ankerwort in 15 von 16 Fällen, der Name kehrte im Folgeturn in 14 von 16 wörtlich wieder (`novaberg-thinking-lage_m.md` Scheibe 13).

---

## 05.10.2026 — aus dem Audit der Emotions-Architektur, am Code abgeleitet

### `EMOTION-SYNONYM-UNAUFGELOEST` — ein Synonym im Feld `emotion` erreicht den Avatar unaufgelöst
**Kategorie:** ANT

**Rang:** **mittel** — laut im Client (Error-Zeile, Gesicht neutral). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `to_canonical` gibt ein Synonym unverändert zurück (`server/utils/canon.py:113-114`), `character_response` nimmt es roh (`server/services/event_consumer.py:705`).

**Zustand:** offen — abgeleitet aus dem Code am 05.10.2026 (`novaberg` `60aaa69`), nicht im Betrieb gemessen.

**Symptom.** Die Wahrnehmung der eigenen Antwort (`server/graph/nodes/perzeption.py`, `perceive`, Rolle `assistant`) lässt im Feld `emotion` Kanon und Synonyme zu (`_EMOTION_ODER_SYNONYM`, `:101`). `to_canonical` gibt einen Wert aus dieser Menge unverändert zurück (`server/utils/canon.py:113-114`). `character_response.emotion` (`server/services/event_consumer.py:705`, `_antwort_nutzlast_bauen`) kann so ein Synonym wie „sorge“ tragen.

**Wirkung.** Der Avatar kennt nur die 16 kanonischen Namen. `client/avatar/puppet.py:492-494` (`_sector_from_name`) zeigt dann das neutrale Gesicht und schreibt eine Error-Zeile; die Emotion der Antwort geht für diesen Turn verloren. Dieselbe Lücke hat die Emotion eines Pixie-Auftrags, die auf ihrem Weg nicht kanonisiert wird (`client/avatar/idle.py:455-457`, `_sector_of`).

**Was fertig wäre.** `character_response.emotion` trägt immer einen Namen aus `EMOTION_KANON` oder `neutral`; ein Zeuge mit einem Synonym in der Wahrnehmung belegt es.

**Quelle.** Audit `labor/avatar/2026-10-05_audit-emotion-architektur.md`, A2 (Nebenbefunde) und A7.

**Priorität:** mittel.

### `WAHRNEHMUNG-RUECKFALL-UNMARKIERT` — bricht die Wahrnehmung der Antwort ab, geht der Stand von vor der Antwort ohne Kennzeichnung hinaus
**Kategorie:** ANT

**Rang:** **mittel** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `_antwort_nutzlast_bauen` (`server/services/event_consumer.py:625-720`) trägt die Marke `lauf_unvollstaendig` nicht in `character_response`.

**Zustand:** offen — abgeleitet aus dem Code am 05.10.2026 (`novaberg` `60aaa69`), nicht im Betrieb gemessen.

**Symptom.** `_wahrnehmung_erheben` (`server/graph/nodes/perzeption.py:274`) fängt nur `json.JSONDecodeError` und `KeyError` (`:304`). Bei jedem anderen Fehler endet der Graph vor dem Rückruf der Freigabe (`server/services/event_consumer.py:454-458`), und der Rückfallpfad in `_event_verarbeiten` (`:929-937`) sendet `internal.emotion` aus der Rechnung vor der Antwort (`ei_calc`, emotionale Gravitation).

**Wirkung.** Der Avatar zeigt den berechneten Zustand vor der Antwort, als wäre er die Wahrnehmung der Antwort; die Nachricht sagt nicht, welche Quelle gilt. Eine Auswertung der Emotionsfelder kann den Turn nicht als Rückfall erkennen.

**Was fertig wäre.** Die Nachricht kennzeichnet ihre Quelle (Wahrnehmung oder Rückfall), oder der Rückfall sendet keine Emotion; ein Zeuge mit einem Fehler im Modellaufruf der Wahrnehmung belegt es.

**Quelle.** Audit `labor/avatar/2026-10-05_audit-emotion-architektur.md`, A2 (Nebenbefunde).

**Priorität:** mittel.

### `MODUS-STIL-UNGEPRUEFT-GESENDET` — `gespraechs_modus` und `sprach_stil` gehen mit dem rohen Wert der Wahrnehmung hinaus
**Kategorie:** ANT

**Rang:** **niedrig** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; die Freigabe geht nach `perzeption_assistant` hinaus, die Korrektur folgt erst in `ei_calc_persist` (`server/graph/nodes/ei_calc_persist.py:154-209`).

**Zustand:** offen — abgeleitet aus dem Code am 05.10.2026 (`novaberg` `60aaa69`), nicht im Betrieb gemessen.

**Symptom.** Die Antwort geht am Ende von `perzeption_assistant` hinaus (`server/services/event_consumer.py:353`, `_KNOTEN_NACH_FREIGABE`; `:885-891`). Die Plausibilitätskorrektur von Modus und Stil läuft erst danach in `ei_calc_persist` (`server/graph/nodes/ei_calc_persist.py:172`, `:209`). `character_response.sprach_stil` und `.gespraechs_modus` (`event_consumer.py:709`, `:718`) tragen deshalb den unkorrigierten Wert. Der Kommentar `event_consumer.py:930-932` („von perzeption_assistant + ei_calc_persist gesetzt“) trifft nur auf den Rückfallpfad zu.

**Wirkung.** Client und Auswertungen sehen einen anderen Modus und Stil als den, den der Server danach speichert.

**Was fertig wäre.** Beide Felder tragen den korrigierten Wert, oder die Korrektur läuft vor der Freigabe; ein Zeuge mit einem unplausiblen Modus der Wahrnehmung belegt es.

**Quelle.** Audit `labor/avatar/2026-10-05_audit-emotion-architektur.md`, A2 (Nebenbefunde).

**Priorität:** niedrig.

## Einzelbefunde ohne eigenen Datumsabschnitt

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

*Die Einträge dieses Abschnitts standen bis zum 19.09.2026 ohne eigene Überschrift unter dem Abschnitt vom 25.08.2026, zu dem nur der erste Eintrag davor gehört. Ihre Befunddaten reichen vom 05.08. bis zum 18.09.2026.*

### `UMFANGSREGLER-BINDET-NICHT` — wirkt in der Richtung, bindet nicht
**Kategorie:** ANT

**Rang:** **mittel**, Aufwand groß; ~~wartet auf eine Absicht: bleibt die Länge im Prompt eine Tendenz (in welcher Bauform), oder wird sie nach dem Modellaufruf erzwungen?~~ → **entschieden am 06.10.2026** (unten). Zusammen mit `MENGENANGABE-BINDET-NUR-UNTEN`. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: unverändert, nur eine Zahl im Prompt (`server/ei/haltungssprache.py:593-596`).

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: Die Länge bleibt eine **Tendenz im Prompt**; nach dem Modellaufruf wird nichts erzwungen — Kürzen zerschneidet Sätze, Nachfordern kostet einen Aufruf. ~~In der Bauform Sätze und Absätze statt Zeichen; Sätze kann das Modell zählen, Zeichen nicht.~~ → **Die Bauform ist am selben Tag neu entschieden**, weil die Begründung unbelegt war und einer Messung widersprach: In [`novaberg-haltungsraum_m.md`](novaberg-haltungsraum_m.md) bindet eine Satzvorgabe, zerstört aber den knappen Stil (1 von 3 Inhaltsmarken gegen 3 von 3 mit einem Zeichenkorridor). Der Eigentümer: *„Wir nehmen c“* — **erst messen, dann entscheiden:** Satzform gegen Zeichenkorridor, an Länge **und** Stil, mit dem Instrument vom 07.09.2026 (unten) und rund 30 bis 40 Turns zu Sachfragen. **Das Ziel:** Die Länge bindet in beide Richtungen, ohne den knappen Stil zu verlieren. Bis dahin bleibt die Bauform Zeichen. Gilt ebenso für `MENGENANGABE-BINDET-NUR-UNTEN`.

**Zustand:** offen, **die verlangte Pruefform ist am 07.09.2026 gefahren** — mit und ohne Block, 16 Turns, kein Ausfall. ~~offen, belegt am 07.09.2026 an 749 Turns~~ ~~offen, unbelegt — braucht Ist-Laenge gegen Vorgabe an echten Turns~~

**Er bleibt offen, weil sein Schliesskriterium nicht erfuellt ist** — *„Die Mengenangabe bindet in beide Richtungen"*. Sie bindet in **einer**: **keine einzige** der 16 Antworten lag unter der Untergrenze.

#### Die Pruefform, gefahren am 07.09.2026, 21:05–21:24 UTC

**Sie stand seit dem 20.08.2026 zweimal im Backlog und war nie gefahren worden:** dieselbe Turnreihe desselben Reizes **mit und ohne Block**. Der Bestandsbeleg von 15:05 UTC konnte die Frage nicht beantworten — eine Streuung ohne Gegenprobe ist mit *„der Block wirkt schwach"* genauso vereinbar wie mit *„der Block wirkt gar nicht"*.

Instrument: acht Sachfragen, **Cross-over** ueber zwei Durchgaenge, `gemma4-a4b-gpu`. Der Schalter sitzt in Redis und nimmt **genau die Umfangszeile** — Haltungswoerter und Energie stehen in beiden Armen. Der Schalterstand ist je Turn belegt und gegen den geplanten Arm geprueft: **0 Widersprueche in 16 Turns**.

| Arm | n | Mittel | Streuung innerhalb | Ist/Obergrenze | ueber | unter |
|---|---:|---:|---:|---:|---:|---:|
| **mit** Block | 8 | 791,5 Z. | **6,03** | **1,39** | 7/8 | **0/8** |
| **ohne** Block | 8 | 1162,1 Z. | **3,38** | **2,00** | 7/8 | **0/8** |

**Der tragende Befund ist ein Verhaeltnis, keine Einzelzahl.**

> **Der Regler bewegt weniger, als er zittert.** Der Unterschied **zwischen** den Armen betraegt Faktor **1,47**; die Streuung **innerhalb** eines Arms bei gleicher Stellung liegt bei **3,38 bis 6,03**. Was der Block zwischen An und Aus ausmacht, ist kleiner als das, was er bei gleicher Stellung ohnehin schwanken laesst — um mehr als das Doppelte.

**Er wirkt trotzdem, und die Richtung ist eindeutig:** 6 von 8 Reizpaaren sind ohne ihn laenger, und er halbiert den Ueberhang (2,00 → 1,39). **Statistisch ist das bei n = 8 nicht abgesichert** — Vorzeichentest zweiseitig **p = 0,289**. Auf die fuenf Paare beschraenkt, deren Korridor in beiden Armen derselbe war: **+242,8 Zeichen** im Mittel, vier von fuenf positiv.

**Und die Reihe hat den Befund der Vormessung verschaerft, nicht wiederholt.** Dort hiess es: *„Acht Sachfragen derselben Machart sollten eine Lage treffen und trafen fuenf."* Hier traf **derselbe Reiz** zwanzig Minuten spaeter eine andere Lage — bei **3 von 8 Paaren** wechselte der Cluster zwischen den Armen (`schlachtfeld` 60–175 gegen `foyer` 350–700). Nicht nur verschiedene Reize streuen ueber Landschaften; **die Wiederholung desselben Reizes tut es auch.** Ein Cross-over-Entwurf setzt voraus, dass der Reiz die Bedingung festlegt — hier legt er sie nicht fest.

**Vorbehalte:** n = 8 je Arm. Gemessen ist Laenge gegen Korridor, nicht Qualitaet. Ein Modell, ein Abend. Der Kontext wuchs waehrend der Reihe; der Cross-over gleicht das zwischen den Armen aus, beseitigt es nicht. Volltext: `labor/messreihen/2026-09-08_regieblock_ergebnis.md`.

**Was daraus folgt, ist eine Bauform-Frage und keine Zahlenfrage.** Eine bessere Zahl im Prompt durchdringt denselben Rauschteppich nicht. Ob dieselbe Anweisung in **Saetzen und Absaetzen** staerker bindet, behauptet der Override vom 05.09.2026 fuer das Fernmodell und belegt es an vier Turns — **das Instrument, das es entscheiden koennte, steht seit heute.**

**Belegt, nicht neu gemessen: der Bestand traegt beides.** `pipeline_log` fuehrt je Turn die Haltungszeile mit `umfang` und den Rohturn mit der Antwort; **kein neuer Turn war noetig**, keine Modellkosten, kein Waermeproblem. 749 Turns eines **modellhomogenen** Zeitraums (vor dem Wechsel auf deepseek am 06.09.2026, 09:53 UTC).

| Gen | ab | n | im Korridor | unter | ueber | Ist/Obergrenze |
|---|---|---:|---:|---:|---:|---:|
| G1 | vor 20.08. | 393 | **7,6 %** | 15 | 348 | **6,25** |
| G2 | 20.08. | 167 | 42,5 % | 7 | 89 | 1,54 |
| G3 | 27.08. | 189 | 28,0 % | 1 | 135 | 1,42 |

Streuung bei **identischer** Vorgabe (Gruppen ab 4 Turns): **9,19 · 10,67 · 3,15**.

> **Die 2,68 vom 17.08.2026 war die guenstigste Zahl, die je gemessen wurde, nicht die typische.** Sie stammt aus fuenf Turns.

**Die Bindung ist einseitig, und das ist der schaerfere Befund:** ueber alle Generationen **601 Antworten ueber der Obergrenze, 23 darunter**. Nach unten haelt die Vorgabe, nach oben nicht — deckungsgleich mit `MENGENANGABE-BINDET-NUR-UNTEN`.

**Ein Nebenbefund beantwortet eine offene Frage.** Die Halbierung der Korridore vom 20.08.2026 galt als *„im Betrieb ungemessen"*; sie hat gewirkt. `Ist/Obergrenze` faellt von **6,25 auf 1,54**, das Ist-Mittel von 1289 auf 432 Zeichen. Bei *halbierten* Korridoren muesste dieses Verhaeltnis steigen, wenn die Laenge gleich bliebe — es faellt auf ein Viertel. **Vorbehalt:** G1 umfasst mehr als eine Aenderung, die Zuordnung ist plausibel und nicht isoliert.

**Kontrollschnitt gegen den naheliegenden Einwand:** Die Streuung stammt nicht aus der Vermischung zweier Turn-Sorten. Ab dem 27.08. getrennt streut `nutzer_turn` **3,22** (125 Turns), `eigener_impuls` **1,52** (17). Die streuende Seite ist der Gegenstand.

**Was fuer das neue Modell gilt, ist offen und braucht Laufzeit.** Eine Reihe von 14 Reizen am 07.09.2026 lieferte 10 Turns: **0 unter der Untergrenze, 7 darueber**, `Ist/Obergrenze` **1,12**, Ist-Mittel 605 Zeichen gegen 513 davor. Die Einseitigkeit haelt also auch dort. **Die Streuungsaussage traegt nicht** — 6 Landschaften bei 10 Turns ergaben Gruppen von 3, 2 und 2, und `max/min` waechst mit der Gruppengroesse.

> **Die Reihe hat dabei ihre eigene Annahme widerlegt: Die Landschaft folgt nicht der Bauart des Reizes.** Acht Sachfragen derselben Machart sollten *eine* Lage treffen und trafen fuenf. Wer eine grosse Gruppe bei identischer Vorgabe braucht, kann sie ueber den Reiz nicht herstellen — er braucht viele Turns und nimmt die Gruppen, die entstehen. Fuer eine belastbare Aussage: rund 30 bis 40 Turns.

**Damit steht der Eintrag nicht mehr auf einer Kalibrierfrage, sondern auf einer Bauform-Frage.** Ob eine Zahl im Prompt diese Aufgabe tragen kann, ist fuer das alte Modell beantwortet: **nein**. Jede Groesse, die ueber diesen Weg wirken soll — der Massblock, seit dem 07.09.2026 der Faszinations-Leser — erbt das.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Der Umfangsregler wirkt in der Richtung und bindet nicht.** Gemessen über zehn Turns des produktiven Paares: Die Vorgabe der Regie schwankt um den Faktor **1,50** (0,590 bis 0,883), die Antwortlänge um **3,93** (813 bis 3193 Zeichen). Bei **identischer** Vorgabe 0,652 über fünf Turns liegen die Antworten zwischen 813 und 2181 Zeichen — Faktor **2,68**. Die Korrelation stimmt (Pearson r = +0,78, die höchste Vorgabe erzeugt die längste Antwort), aber **die Streuung bei gleicher Vorgabe ist größer als die Spanne der Vorgabe selbst**. Damit ist der Regler kein Regler, sondern eine Tendenz. Kein Defekt am Bau — die Größe wird gerechnet, gelesen und wirkt; die Frage ist, ob eine Zahl im Prompt diese Aufgabe überhaupt tragen kann.

**Geschlossen, wenn** Die Mengenangabe bindet in beide Richtungen — belegt durch Ist-Laenge gegen Korridor an echten Turns.

---

### `TIMELINE-LESEPFAD-INSTABIL` — instabil, nicht geschlossen
**Kategorie:** ANT

**Rang:** ~~**mittel**~~ → **hoch** (15.10.2026) — still, der Mensch handelt nach der Auskunft; ~~**unbelegt**, braucht eine Zählung am Bestand~~ → **belegt am 15.10.2026, 17:26–17:51 UTC: in 0 von 3 Turns mit einer Frage nach den eigenen Terminen wurde die Timeline gelesen** — der Thinker erkannte *Termin* (`treffer_reiz`), rief aber kein Werkzeug (`tool_aufrufe: 0`), der Router stellte nichts zu (`vom_modell: "/"`); im ersten Turn nannte die Antwort einen Termin aus einer Vorrecherche (ein Programmheft), in den beiden folgenden behauptete sie, die Termine *„vorliegen“* zu haben, und nannte keinen. Der Eigentümer: *„grauenhaft“*. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: ob gelesen wird, entscheidet weiter ein Modellurteil je Turn (`server/graph/nodes/router.py:344-347`, `server/plugins/timeline_manager/manager.py:114`).

**Zustand:** **im Code behoben am 15.10.2026; Messung im Betrieb ausstehend.** ~~offen, unbelegt — gegen HEAD `00c16b6` gehalten am 20.08.2026. braucht dieselbe Frageklasse mehrfach gegen den Bestand.~~

**Die Ursache, am Code gefunden am 15.10.2026 — nicht allein das Modellurteil, sondern die Reihenfolge im Graphen.** Der Enricher läuft im CharacterGraph vor dem Router; `needs_timeline` und `timeline_query` setzt erst der Router. Der gezielte Zweig des TimelineManagers (`range`, `search`) war im Turn deshalb **nie erreichbar** — im Serverlog seit dem 18.09.2026 stehen 109 Router-Zeilen mit `timeline=True` und 0 gezielte Lesungen. Übrig blieb das proaktive Fenster (drei Tage zurück, vierzehn voraus) ohne Typfilter: Ein Erinnerungs-Anker galt dort als Termin, und die Termine standen als unerklärte Zeilen `[Timeline/vergangen|anstehend]` im `[GEDAECHTNIS]` des Verfassers. Im Fall vom 15.10.2026 war die einzige Zeile dort der Anker, den die Frage selbst angelegt hatte.

**Gebaut am 15.10.2026** (getestet, im Betrieb nicht gemessen):

- **Gelesen wird hinter dem Router, im selben Knoten** — `graph/base.py::_node_route` ruft nach `route()` ~~`memory/timeline_reading.py::read_for_turn`~~ → seit dem 17.10.2026 `graph/nodes/route_reading.py::read_after_route` (gebaut, noch nicht committet); das Ergebnis liegt im Kanal `appointment_reading`. Kein neuer Knoten. Ohne gezielte Anfrage gilt das proaktive Fenster in derselben Form; eine Anfrage, die sich keinem Zeitraum zuordnen lässt, ist laut (ERROR) und ergibt ebenfalls das proaktive Fenster.
- **Ein eigener Block `[TERMINE]` im Prompt des Verfassers** (`prompts/default/verfasser.termine.txt`, gebaut in `graph/format/appointments.py`): der gelesene Zeitraum, je Termin Wochentag, Datum und Uhrzeit in Ortszeit, Titel und der vorgerechnete Bezug zu heute. Ein leerer Zeitraum steht ausdrücklich als *„keine Termine vom … bis …“* da, ein Lesefehler als *„konnte nicht gelesen werden“* — nie als *keine*. Der Block steht in jedem Turn. Der Prompt sagt: Termine des Menschen nennt der Inhalt nur aus diesem Block, und *keine* sagt er als *keine*.
- **Die `[Timeline/…]`-Zeilen fehlen im Gedächtnisblock des Verfassers** (`graph/format/memory_context.py::entries_for_reader`); Thinker, Tribunal und Korrektor behalten sie, jetzt mit Wochentag und Bezug zu heute und ohne Anker.
- **Ein Erinnerungs-Anker ist in keinem Leseweg ein Termin** — ausgeschlossen in der Abfrage vor dem `LIMIT`, im Turn, im proaktiven Fenster und beim Lesen des Timeline-Agenten (`agents/timeline/suche.py`, nur bei `read`).
- Zeugen: 49 ohne Datenbank (`tests/test_timeline_reading.py`, `tests/test_timeline_anchor_exclusion.py`), darunter die Verdrahtung über einen echten `StateGraph`. Server-Suite nach dem Bau ~~4371~~ → 4411 Zeugen, grün (Endstand aller drei Teile des Tages, nachgetragen 16.10.2026, 00:59 UTC; 4371 galt für einen Zwischenstand des dritten Teils).

**Nulllinie am Code vor dem Bau** `[gemessen 15.10.2026]` (Simulation an einem Prüf-Nutzer mit gesäten Terminen, `labor/2026-10-15_sim_timeline_notizen.py`): ausdrückliche Lesefragen 6 von 7 — es fehlte ein Termin im November, außerhalb des proaktiven Fensters —, Lesefragen ohne Merkmal 1 von 3. Am Bestand der letzten 60 Tage las der Turn die Timeline in 7 von 23 Nutzer-Turns mit *Termin*.

**Gemessen nach dem Commit, in Simulationen an Prüf-Nutzern** (`labor/2026-10-15_sim_timeline_notizen/`): Die Frage, wann der Mensch zuletzt beim Friseur war (ein Termin zehn Tage zurück, außerhalb des proaktiven Fensters), war am 16.10.2026 zweimal richtig und am 17.10.2026 (`simnachher3`) falsch — der Router stellte nichts zu, und die Antwort sagte, sie finde keinen früheren Termin. ~~Ob der Router dabei eine gezielte Anfrage setzte, steht nicht in der Reihe; das Bild passt zu einem Turn, der nur das proaktive Fenster las.~~ → widerlegt am 17.10.2026 (Nachtrag unten): Gelesen wurde; verdorben hat es die Prüfung danach (`PRUEFER-OHNE-LESESTAND`). Am selben Tag las eine Frage nach den Terminen eines Monats über den Agenten nur einen Tag (`ZEITRAUM-LIEST-EINEN-TAG`, novaberg-bugs-wissen.md, gebaut). **Der Eintrag bleibt offen:** Ob gezielt gelesen wird, hängt weiter am Router.

**Nachtrag, 17.10.2026 — Simulation `simnachher4`:** An einem frischen Prüf-Nutzer mit denselben 24 Sätzen (`labor/2026-10-15_sim_timeline_notizen/simnachher4/`, auf `a26b2cd`) lief der Leseschritt hinter dem Router in 24 von 24 Turns. Der Router setzte in **16 von 16** Terminsätzen eine gezielte Anfrage (`range` oder `search`), in den 8 Notizsätzen keine; in `simnachher3` war es ebenso. In der Friseurfrage suchte er `search` *Friseur* `backward`, der Leseweg im Turn fand den Termin, und der Entwurf nannte ihn richtig. Falsch wurde die Auskunft erst im Thinker, der den Lesestand des Turns nicht sieht — in `simnachher3` zu *„keinen früheren Termin gefunden“*, in `simnachher4` zu einem falschen Datum. **Die Vermutung oben ist damit widerlegt:** Gelesen wurde; verdorben hat es die Prüfung danach, jetzt geführt als `PRUEFER-OHNE-LESESTAND` (oben in dieser Datei). Die Instabilität sitzt damit hinter dem Router, nicht in ihm. Rang und Zustand bleiben, wie sie stehen.

**Was die Messung nach dem Commit zeigen muss:** ob der Router bei einer Terminfrage eine gezielte Anfrage setzt — ob gezielt gelesen wird, hängt weiter an seinem Urteil; ohne Anfrage steht das proaktive Fenster da, mit seinem Zeitraum in der Kopfzeile. Und auf dem Aufgabenpfad — der Router stellt die Frage dem Timeline-Agenten zu — läuft der Verfasser nicht; dann erreicht `[TERMINE]` die Antwort nicht, und es gelten die Lesezeilen des Agenten (ohne Anker, ~~ohne Bezug zu heute~~ → seit dem 17.10.2026 dieselben Zeilen wie der Block, mit Bezug zu heute — gebaut, noch nicht committet). Ob eine Lesefrage diesen Weg nimmt, ist nicht gemessen. → **In der Simulation an einem Prüf-Nutzer vom 17.10.2026 nahm ihn eine Frage nach den Terminen eines Monats** — und der Agent las nur einen Tag (`ZEITRAUM-LIEST-EINEN-TAG`, novaberg-bugs-wissen.md). → **23.10.2026, Messturns im Betrieb** (am Code von `3f2aa17`, ein frischer Prüf-Nutzer, acht synthetische Turns): Die Frage nach den Terminen im November zeigte im Block `[TERMINE]` das Ereignis einer anderen Person am 14.11.2026 unter eigener Kopfzeile, nicht als Termin des Menschen. In einem anderen Turn mit einer Terminfrage lieferte der Router das Zeitfenster nicht in ISO (`TT.MM hh:mm`), `graph/appointments.py` meldete die Anfrage als nicht lesbar, und der Block fehlte in diesem Turn (Fundliste, 23.10.2026). Rang und Zustand bleiben. → **24.10.2026, am Code gelesen gegen HEAD `6b37234`** (aus der Klassifizierung der Funde vom 23.10.2026): **Beleg — das Zeitfenster des Routers stand nicht in ISO.** Die Vorgabe des Routers (`server/prompts/default/router.task.txt`) verlangt `"YYYY-MM-DD HH:MM"`; `server/graph/appointments.py::parse_local_moment` liest mit `datetime.fromisoformat`, und eine Form `TT.MM hh:mm` wirft `ValueError`. `appointment_window` fängt das, meldet mit ERROR *„Anfrage des Routers nicht lesbar“* und gibt das proaktive Fenster zurück (`proactive_window(now, unusable_query=True)`) — wie im Docstring beschrieben. Dass das Modell die Vorgabe verfehlte, steht nur in der Fundliste; ob die deutsche Datumsform im Prompt des Routers (`Datum: {today}`, gesetzt in `server/graph/nodes/router.py` als `"%d.%m.%Y, %H:%M Uhr"`) das begünstigt, ist unbelegt. **Berichtigung des Nachtrags vom 23.10.2026: Die unlesbare Anfrage entfernt den Block `[TERMINE]` am Code nicht** — das proaktive Fenster greift. `read_after_route` (`server/graph/nodes/route_reading.py`) setzt `appointment_reading` immer, und `_node_route` (`server/graph/base.py`) wirft, wenn es fehlt; `_appointments_block` im Verfasser baut den Block aus jedem Leseergebnis, auch aus dem proaktiven Fenster mit `unusable_query`, und seine Kopfzeile (`server/graph/format/appointments.py::header_line`) sagt dann, dass sich die Frage keinem Zeitraum zuordnen ließ. Ohne `[TERMINE]` läuft am Code nur der Kontext-Schnitt, der Aufgabenpfad oben: Bei `task_context_cut` überspringt der Graph den Verfasser (`server/graph/character_graph.py::_after_haltung`), gesetzt vom Planner (`_build_task_block`) bei Ablehnung, Fehler, *dismissed* oder Erfolg eines Agenten. **Offen, warum der Block in diesem Turn fehlte** — ob der Turn diesen Weg nahm, ist unbelegt; erkennbar wäre es im Serverlog an der Zeile *„Graph: Kontext-Schnitt aktiv — Verfasser übersprungen“* und am Fehlen der INFO-Zeile *„Verfasser: [TERMINE] art=…“*. Ein Turn mit unlesbarer Anfrage bekommt keine eigene Kennung, weil der Code ihn laut meldet und das proaktive Fenster liest; kehrt er wieder, wird er ein eigener Bug. Rang und Zustand bleiben.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Der Lesepfad zur Timeline ist instabil, nicht geschlossen.** Dieselbe Klasse Frage wird einmal zugestellt und einmal nicht: *„Wann ist mein Meeting mit dem Chef?"* (35 Zeichen) erzeugte um 16:50 einen Dispatch an `timeline`; die Fragen des Menschen nach bestehenden Terminen im Fenster 14:00–15:53 erzeugten keinen — im ganzen Fenster steht ein einziger Timeline-Dispatch (15:52, `abgelehnt` auf eine vorwurfsvolle Feststellung). Auf die Frage nach Terminen dieser Woche antwortete Nova mit *nein*, waehrend ein Eintrag fuer Mittwoch aktiv in der Tabelle stand. **Eine ausgebliebene Zustellung ist von einer richtigen Auskunft nicht zu unterscheiden** — es gibt keinen Fehler, keinen Log-Eintrag und kein leeres Ergebnis, sondern nur eine Antwort ohne Grundlage.

**Geschlossen, wenn** Der Lesepfad zur Timeline liefert bei gleicher Eingabe dasselbe.

---

### `VERFASSER-KOPFBLOCK-FAELLT-AUS` — in mehr als der Haelfte der Turns
**Kategorie:** ANT

**Rang:** **hoch** — laut im Log, aber niemand handelt danach, und die Ausbausperre fällt aus. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: der Umlaut-Fehler ist behoben, **eine zweite Ursache steht**: `_kopf_deuten` verlangt das nackte *ja*/*nein* (`server/graph/einwand.py:237`), der Prompt formuliert die Zeile als Frage (`:114`), und das Modell schreibt sie hinter den Wert. **Gezählt am 05.10.2026** im Serverlog seit 03.10.2026: 47 Zeilen *„kein lesbares Urteil im Kopfblock“* gegen 74 erzeugte Antworten. Die Zeugen prüfen nur die glatte Form.

**Zustand:** offen — gegen HEAD `9bcd214` nachgesehen am 24.08.2026; am Code unveraendert seit `1330045`. **Die Rate ist weiterhin unbelegt, und sie ist es jetzt ohne Hindernis:** Der Auszug traegt seit dem 22.08. 500 Zeichen statt 120, die Messung, die daran haengt, ist noch nicht gelaufen. Eine **hinreichende** Ursache ist belegt und behoben: `_kopf_deuten` verwarf das ganze Urteil, wenn ein Feldname einen Umlaut trug — der Prompt schreibt `GEPRUEFT` und `STAERKE` vor, das Modell schreibt `GEPRÜFT` und `STÄRKE`. Derselbe vollstaendige Kopfblock ist vorher `geliefert=False`, nachher `True`. `_feldname` normalisiert jetzt Umlaute und Kleinschreibung (`graph/einwand.py`), vier neue Zeugen, Gegenprobe 2 vorhergesagt / 2 gezaehlt, Suite `Ran 2087 tests — OK`.

**Datenpunkt 28.08.2026, 20:45 UTC** (Betriebszeuge der Scheibe 5, ein Turn): `kein lesbares Urteil im Kopfblock` — Rohantwort beginnt mit `EINWAND: nein — widerspric…`, 705 Zeichen. **1 von 1.**

**Datenpunkt 28.08.2026, 15:30–16:06 UTC** (Betriebsmessung der Sachlage, fuenf Turns, Auszug 500 Zeichen): `kein lesbares Urteil im Kopfblock` in **3 von 5** Turns (2, 4, 5). Alle drei Kopfbloecke beginnen laut Auszug mit `EINWAND: nein — …`, und der Deuter meldet sie als unlesbar. Kein eigener Auftrag; die Rate steht damit erstmals mit dem langen Auszug belegt. **Nachgezählt über den Rest des Tages:** in **4 von 4** weiteren echten Turns (17:15, 17:24, 18:46, 18:47 UTC) — zusammen **7 von 9**, alle mit einem Kopfblock, der mit `EINWAND: nein — …` beginnt.

> **Dass es die Ursache der gemessenen Faelle war, ist damit NICHT belegt** — und der Grund dafuer ist ein zweiter Befund: Der Logauszug des Ausfalls war bei **120 Zeichen** gekappt und endete mitten im zweiten von fuenf Feldern. Gegen die fuenf echten Ausfaelle des Bestandes gehalten, blieben **0 von 5** lesbar, weil der Auszug drei Felder gar nicht enthaelt. Gezaehlt ist nur eine Korrelation: **4 von 5** trugen `GEPRÜFT` mit Umlaut.
>
> **Der Auszug traegt jetzt 500 Zeichen und die Gesamtlaenge** (`graph/nodes/verfasser.py`). Damit ist die naechste Messung moeglich; die heutige war es nicht.
>
> **Die Ausfallrate ist ebenfalls offen.** Der Zaehllauf vom 22.08.2026 ergab 55 Ausfaelle in 36 Stunden — **50 davon aus Suite-Laeufen**, deren Zeugentexte im selben kumulativen Log stehen. Aus dem Betrieb stammen **5 Ausfaelle und 1 gefaelltes Urteil**; das ist zu wenig fuer eine Rate und nicht mit den 54 % vom 13.08.2026 vergleichbar.

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Der Kopfblock des Verfasser-Urteils faellt weiter aus.** Messturn `065a5d5f` um 19:15 UTC: `Verfasser: Urteil AUSGEFALLEN`, die Rohantwort beginnt mit `EINWAND: nein — widerspricht PERSON B nichts.` — das Modell schreibt den Kopfblock, aber nicht in der Form, die `urteil_lesen` erkennt. Ein Datenpunkt zu den 14 von 26 vom 13.08., und ein Hinweis auf die Ursache: nicht *kein* Kopfblock, sondern ein nicht parsbarer.

**Geschlossen, wenn** Der Kopfblock des Verfasser-Urteils steht in jedem Turn, oder sein Ausbleiben ist ein benannter Zustand.

---


**Nachtrag vom 14.08.2026, aus der Fundliste uebernommen.** **Der Kopfblock des Verfasser-Urteils fällt in mehr als der Hälfte der Turns aus.** Gemessen am 13.08.2026 über einen Tag: **12 Urteile gefällt, 14 ausgefallen** von 26 Verfasser-Läufen (54 %). Der Ausfall wird laut protokolliert (`Verfasser: Urteil AUSGEFALLEN`) und kostet nur das Urteil, nicht die Antwort — die Bauart hält also. Aber die Ausbausperre B1 greift in mehr als jedem zweiten Turn nicht, und `novaberg-node-verfasser_k.md` hält bisher nur fest, dass die **Wirkung** des Kopfblocks auf die Kapitulationsrate null ist; dass er zur Hälfte gar nicht erst zustande kommt, steht nirgends. Beide Aussagen zusammen stellen die Frage, ob der Block bleibt.

### `GESPRAECHSVEKTOR-HYPOTHESE-DREIFACH` — dieselbe Hypothese dreimal im Block
**Kategorie:** ANT

**Rang:** **niedrig** — still, kostet Kontext. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt (`server/graph/nodes/gespraechsvektor.py:777-780`, `server/graph/nodes/verfasser.py:162-170`). Dieselbe Stelle und Behebung wie `GV-HYPOTHESE-ROHE-AUSGABE`.

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026. Unveraendert, an der Quelle nachgesehen: `state["gespraechsvektor"]` ist die **rohe** Modellausgabe (`gespraechsvektor.py:1222`, gespeist aus `response.text.strip()` in `:661`) und geht als Ganzes in den Block. `graph/nodes/verfasser.py` setzt daneben die geparste Strategiezeile (`:130-137`), die rohe Hypothese (`:141`) und den Leitgedanken (`:145`) — Strategie und Impuls stehen damit weiterhin je zweimal im selben Block.

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Der `[GESPRAECHSVEKTOR]`-Block trägt die Hypothese dreifach.** Live gemessen am 14.08.2026, 22:59 UTC: Der Block enthält (a) die rohe Modellausgabe des GV-Node samt ihrer Labels — `SPRUNG 1:` bis `SPRUNG 3:`, `ABSICHT:`, `STRATEGIE: Pw`, `VEHIKEL:`, `IMPULS:` —, und (b) darunter „Leitgedanke für diese Antwort:", der denselben Eröffnungsabsatz **noch einmal** plus den Impulstext enthält. Der geparste Wert steht zugleich in der Zeile darüber (*„Die gewählte Strategie: Perspektivwechsel als Frage"*). **Der Befund ist nicht neu, sondern nur neu sichtbar:** Ein Verfasser-Prompt vom 13.08. trägt dieselbe Doppelung. Neu ist die Reichweite — seit dem Umbau des Skip-Tors bekommen auch die rund 20 Impuls-Turns pro Tag diesen Block, die vorher gar keinen hatten.

**Geschlossen, wenn** Der `[GESPRAECHSVEKTOR]`-Block traegt jede Angabe einmal.

---

### `MENGENANGABE-BINDET-NUR-UNTEN` — nach unten bindend, nach oben nicht
**Kategorie:** ANT

**Rang:** **mittel**, Aufwand groß — dieselbe Ursache und Entscheidung wie `UMFANGSREGLER-BINDET-NICHT`. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: wie `UMFANGSREGLER-BINDET-NICHT` — die Länge bleibt eine **Tendenz im Prompt**; nach dem Modellaufruf wird nichts erzwungen. ~~In Sätzen und Absätzen statt Zeichen.~~ → Die Bauform ist am selben Tag neu entschieden (*„Wir nehmen c“*): erst die Messung Satzform gegen Zeichenkorridor an Länge und Stil, bis dahin Zeichen — Einzelheiten dort.

**Zustand:** offen, unbelegt — gegen HEAD `9bcd214` gehalten am 24.08.2026. Die halbierten Korridore sind gebaut und im Betrieb ungemessen.

> **Das Messgeraet steht.** `labor/werkzeug/grenze_probe.py` ist der einzige genannte Beleg des Befundes, und es ist vorhanden und versioniert. Der Befund ist damit wiederholbar; was fehlt, ist die Wiederholung gegen die halbierten Korridore.

**Befund (13.08.2026), aus der Fundliste uebernommen.** **Eine Mengenangabe bindet nach unten und trägt nach oben nicht.** Im kargen Korridor (bis 120 Zeichen) trafen 17 von 18 Läufen, im weiten (700–1400) **4 von 17** — und die Verfehlung ging jedes Mal nach oben, um 5 bis 15 %. Die Gegenprobe entscheidet die Ursache: Wird derselbe Korridor um 250 Zeichen **tiefer** gelegt (450–1150), sinkt die Antwortlänge nur von 1365 auf 1294 Zeichen, also um ein Viertel der Verschiebung. Die Länge folgt dem Inhalt, nicht der Zahl; die Zahl wirkt als **Schranke, nicht als Ziel**. Ein Zielwert („etwa 1000 Zeichen") zieht stärker als eine Spanne (1217 gegen 1365), trifft ihn aber auch nicht. Belegstand: ein Material, eine Szene, drei Läufe je Fassung — `labor/werkzeug/grenze_probe.py`.

**Geschlossen, wenn** Die Mengenangabe bindet in beide Richtungen.

---

## 20.08.2026 — Nova spricht von ihrem eigenen Inneren wie von einem Dritten

---


## 19.08.2026, abends — die Spur zum Leer-Defekt

### `RESPONDER-LEERE-ANTWORT-STILL-NACHTRAG` — vierter Fall, und die Frage von damals ist entschieden
**Kategorie:** ANT

**Rang:** **mittel** — laut seit dem Riegel (`server/services/model_services/chat_worker.py:35-60`, `server/services/event_consumer.py:951-985`). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: die Ursache liegt beim Anbieter und ist nur an einem neuen Fall zu entscheiden; Entscheidung siehe `RESPONDER-LEERE-ANTWORT-STILL`.

**Zustand:** offen — gegen HEAD `9bcd214` nachgesehen am 24.08.2026, unverändert. Dieser Abschnitt ist der **Nachtrag vom 19.08.2026**, nicht der Eintrag; der steht als `#### RESPONDER-LEERE-ANTWORT-STILL` weiter unten. Der Riegel macht den Ausfall laut, die Ursache ist unveraendert offen — 243 Token wurden erzeugt und gingen vor dem eigenen Code verloren.

> **Die Überschrift trug bis zum 24.08.2026 die blanke Kennung des Eintrags — zweimal im Register, für jedes Werkzeug ein und derselbe Abschnitt.** Ein Leser, der Abschnitte nach Kennung sammelt, behält je nach Bauart den ersten oder den letzten und verliert den anderen lautlos; die Triage führte dieselbe Kennung zugleich als Kandidat und als unbewegt.
>
> **Der erste Versuch, es zu berichtigen, war schlimmer als der Zustand.** Die Überschrift lautete kurzzeitig *„Nachtrag zu `RESPONDER-…`"* — damit begann sie mit einem Wort statt einer Kennung und war **keine Abschnittsgrenze mehr**: Der ganze Nachtrag samt seiner Zustandszeile fiel an den Eintrag darüber, `INDEXLAUF-VERSCHWEIGT-DATEIFEHLER`, der dadurch zwei einander widersprechende Zustandszeilen trug. Gefunden hat es die zweite Kontrolle, nicht der Bau. **Eine Überschrift ist hier kein Text, sondern eine Grenze** — wer sie umschreibt, verschiebt sie.
>
> Deshalb trägt der Nachtrag jetzt eine **eigene, abgeleitete Kennung**. Sie ist als Nachtrag lesbar, sie ist eindeutig, und sie ist eine Grenze. Die Kennung des Eintrags selbst ist unverändert und bleibt auflösbar.

> **Seit dem Ollama-Update vom 19.08.2026, 20:31 UTC ist kein Fall mehr aufgetreten**, und das ist gezaehlt statt vermutet: ueber sechs Log-Generationen vom 19.08. 20:04 bis zum 22.08. 09:10 — rund 61 Stunden — stehen **456 erzeugte Antworten und 0 Antwortverluste**. Der einzige `text_len=0` in diesem Zeitraum traegt `caller=thinker` und die Zeile *„content leer, thinking gefuellt (Ollama-Split) — Nachfass-Iteration 1/2"* daneben: ein anderer Fall mit greifendem Rueckweg.
>
> **Der Eintrag bleibt trotzdem offen, und der Grund ist die Sorte des Belegs.** Was hier steht, ist eine Beobachtung ohne Fall — kein Nachweis, dass die Ursache beseitigt ist. Die Abhilfe liegt beim Anbieter; dass sein Fehlerbericht greift, koennen wir annehmen und nicht pruefen. Und der Defekt trat immer in **Schueben** auf: null Faelle in fuenf Tagen, fuenf an einem Nachmittag (01.08.2026). Eine Spanne ohne Fall ist bei dieser Verteilung schwaecher, als ihre Laenge aussehen laesst.
>
> **Was ihn schliessen wuerde:** eine Spanne, die laenger ist als der groesste bekannte Abstand zwischen zwei Schueben — oder ein Fall, der ihn wieder oeffnet.

**Der Eintrag von unten bleibt offen; hier steht, was der vierte Fall dazugelegt hat.**

**Der Vorfall.** 19.08.2026, 15:29:22 UTC. `eval_count=243` erzeugte Ausgabe-Token, `content` leer, `thinking` leer, `text_len=0`. Der Riegel vom 01.08. griff und meldete. Tribunal (drei Modellaufrufe, 6,8 s) und die Antwort-Perzeption liefen danach über ein Nichts, und die Zustellung schwieg.

**Die Frage, die der Riegel offenlassen musste, ist beantwortet — für unsere Seite.** Der Eintrag von damals sagt: *„Der Ausfall trägt `thinking_len` mit — damit ist beim nächsten Fall entscheidbar, ob das Modell nichts sagte oder die Aufbereitung es entfernte."* Gegengeprüft am Code: `raw_content = nachricht["content"]` wird **unmittelbar** nach dem Client-Aufruf gelesen und unverändert weitergereicht; zwischen Anbieter und Logzeile liegt kein Schritt. **Unsere Aufbereitung hat nichts entfernt.**

> **Was daraus folgt, ist aber nicht „das Modell sagte nichts".** 243 Token wurden **erzeugt** — der Anbieter zählt sie. Sie sind zwischen Erzeugung und den beiden Ausgabefeldern verloren gegangen, also **vor** unserem Code. Der Unterschied ist der ganze Befund: Die erste Lesart hätte die Suche bei uns beendet, die zweite verschiebt sie an die Naht zum Anbieter.

**Warum es nicht weiter aufklärbar war, und das ist der eigentliche Defekt daneben.** Der Anbieter liefert **zwölf** Felder; der Bestand las **drei** (`prompt_eval_count`, `eval_count`, `message`). Verworfen wurde unter anderem `done_reason` — genau das Feld, das eine sauber beendete Erzeugung (`stop`) von einer abgeschnittenen (`length`) und von einem Abbruch beim Laden (`load`) unterscheidet. **Die Zeile im Protokoll lautete damit *„Token verbraucht, kein Text"* — wahr und unbrauchbar.**

**Zweiter Defekt am selben Vorfall, und er ist der teurere: der lautlose Ausgang.** `services/event_consumer.py` stellte zu über

```
if response and websocket_map.get(user_id): …
elif response:                              …
```

**Ohne `else`.** Eine leere Antwort fiel durch: kein Senden, keine Meldung. Für den Menschen ist das von einem Hänger nicht zu unterscheiden — der Client bleibt auf dem letzten Stufen-Ereignis stehen. Behoben am 19.08.2026: Der Fall meldet jetzt als Fehler und nennt, wo der Schuldige im Protokoll steht.

**Abhilfe (19.08.2026) — Instrumentierung, keine Behebung.** Der Ausfall selbst bleibt offen:

| Gebaut | Wirkung |
|---|---|
| `graph/antwort_spur.py` | jede der **sechs** Schreibstellen auf `state["response"]` protokolliert alte und neue Länge samt Schreibernamen |
| Anbieter-Umschlag | die vollständige Antwort **vor** jeder Zuweisung, mit `done_reason` und Schlüsselliste |
| Rumpf im Ausfall | erzeugte Token bei leeren Ausgabefeldern → Fehlerzeile mit dem ganzen Rumpf |
| `else` an der Zustellung | der lautlose Ausgang meldet sich |
| AST-Riegel | eine Zuweisung, die den Helfer umgeht, macht einen Zeugen rot |

**Was der Riegel weiterhin nicht tut:** Er verhindert den Ausfall nicht. Ein **Wiederholversuch** bei `text_len == 0` ist nicht gebaut — er ist eine Verhaltensänderung im Antwortpfad und steht als Entscheidung im Backlog.

**Ein Kandidat ist seit dem 19.08.2026 benannt und liegt außerhalb des eigenen Codes.** Die Laufzeit ist **zwölf Minor-Versionen alt** (0.20.7 vom 14.04.; verfügbar v0.32.14 vom 15.08.), und fünf Release-Einträge treffen die Schicht, in der die Token verschwinden — darunter v0.22.1 (*„Updated the Gemma 4 **renderer**"*), v0.30.9 (*„parser/render for cases where thinking was not emitted"*) und v0.32.3 (*„Fixed GLM tool calls being **silently dropped** at the end of generation"*, dieselbe Fehlerklasse an einer anderen Modellfamilie). Geführt als `OLLAMA-VERSION-VIER-MONATE-ALT`; die Nulllinie für den Vorher-Nachher-Vergleich ist erhoben.

**Der Kandidat ist am 19.08.2026 abgearbeitet: die Laufzeit läuft auf 0.32.14, und der Ausfall ist damit nicht erklärt.** Update eingespielt, beide Instanzen neu gestartet, Suite `Ran 1965 tests — OK`, ein echter Turn zugestellt (Responder 666 Zeichen). **Was der Wechsel nicht liefert, ist die Entlastung:** Die Nachmessung hat n=1 bis 5 je Aufrufer gegen n=30 bis 224 der Nulllinie — `0 JSON-Fehlschläge` und `0 Leerantworten` sind bei dieser Stichprobe kein Beleg für Besserung, sondern nur dafür, dass nichts zusammenbrach. Der `thinker`-Median steht bei **12 Zeichen wie zuvor**; der content/thinking-Split ist unverändert da.

**Dabei ein Vorgabewert, der die Klasse hätte verschlimmern können, und es nicht tut.** 0.32.14 schaltet Thinking **per Default ein**: dieselbe Frage an `gemma4-gpu` ohne `think`-Feld ergibt `content=214, thinking=1467` bei 425 Token, mit `think=false` **`content=248, thinking=0` bei 60 Token**. Ein Aufrufer, der das Feld wegläßt, verlöre also den Großteil seiner Ausgabe in einen Kanal, den niemand liest — genau die Signatur dieses Defekts. `services/llm_provider.py` setzt `"think": think` **unbedingt** ins Payload (Default `False`), der Bestand ist deshalb nicht betroffen; im Betrieb bestätigt mit **22 Umschlägen `['content']` gegen 2 mit `['content','thinking']`**, und die zwei sind die zwei `thinker`-Aufrufe mit `think=True`.

> **Die Prüfung lief gegen die Zeile, die den Wert setzt, nicht gegen die Logzeile, die ihn nennt.** Die Nulllinie zeigt `think=False` in jeder Aufruf-Zeile — das ist eine Beschreibung und hätte auch dann so ausgesehen, wenn das Feld unterwegs verlorenginge.

**Und ein Mechanismus ist nachgestellt:** Eine Haltefolge, die am Anfang der Ausgabe trifft, ergibt `done_reason='stop'` bei stehenden Zählern und leerem Text — direkt gegen `gemma4-gpu` reproduziert mit `eval_count=6`, `content=0`. Das Modelfile trägt `PARAMETER stop <turn|>`. **Für 243 Token erklärt das noch nichts** — dort bliebe der Zähler klein. Der verbliebene Kandidat ist ein dritter Ausgabekanal des Parsers; die Zeile, die ihn sichtbar macht, steht seit dem 19.08. im Protokoll.

**Geschlossen, wenn** — unverändert offen: Die Ursache der verlorenen Token ist nicht bekannt. Beim nächsten Fall steht sie im Protokoll; **entschieden ist erst, dass sie nicht bei uns liegt.**

---


**Nachtrag vom 12.08.2026, aus der Fundliste uebernommen.** **Leere Antwort trotz `done_reason=stop`,** zweimal in sieben Läufen derselben Prompt-Form gegen `gemma4-gpu` (`eval_count` 441 und 365, `message.content` leer, kein `thinking`-Feld). Vier Nachläufe derselben Form lieferten 1475 bis 1621 Zeichen — der Ausfall hängt nicht an der Form. Dieselbe Erscheinung wie `RESPONDER-LEERE-ANTWORT-STILL`, hier erstmals außerhalb des Bestands reproduziert und damit unabhängig vom Graphen.

## Chat 148 (18.08.2026) — aus der Werkzeugreihe Vera

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Drei Defekte aus einem 20-Turn-Bogen auf einem eigenen Paar (`vera`), mit angehaltenem Pixie gefahren. Die Reihe liegt in `labor/bogen/bogen_vera_werkzeuge.yaml`, das Ergebnis in `labor/ergebnis/`.

### `TRIBUNAL-ERKENNT-ABBRUCH-OHNE-FOLGE`
**Kategorie:** ANT

**Rang:** **mittel** — ein abgeschnittener Text löst nichts aus. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `server/graph/nodes/tribunal.py` kennt keine Abbrucherkennung (`done_reason`), ein einzelnes Votum bleibt *ok* (`:421-435`). Der Eintrag nennt `nova_gedaechtnis.py`; der Ort ist `tribunal.py`.

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026. Unveraendert: `server/graph/nodes/tribunal.py` kennt keine Abbrucherkennung — die einzige Korrekturschleife dort ist `korrekturauftrag` aus `utils.datum_pruefung` (`:27`, gesetzt in `:291`) und haengt am Datum, nicht an einer abgeschnittenen Antwort.

> **Der Eintrag nennt eine Datei, die es nicht gibt.** Im Befundtext steht `nova_gedaechtnis.py`; eine Triage, die ihre Anker aus dem Rumpf zieht, meldet den Eintrag deshalb als *Pfad veraltet* statt als Kandidaten. Der geltende Ort steht in dieser Zustandszeile.

**Befund.** Zwei von zwanzig Antworten brachen mitten im Wort ab (319 bzw. 635 Zeichen, Ende auf *„…die intelle"* und *„…in ihrem Kopf sortieren,"*). **Das Tribunal hat es selbst erkannt** und benannt:

> *„Die Antwort ist unvollständig und bricht mitten im Satz ab (technischer Fehler/Truncation). Zudem ignoriert sie die explizite Wissensanfrage des Nutzers"* — Score 0,7

**Und die Antwort ging trotzdem hinaus.** Ein Urteil, das den technischen Abbruch benennt und keine Folge hat, ist eine Prüfung, die anschlägt und nicht greift.

**Reproduktion.** Nicht gezielt herstellbar; 2 von 20 Turns, beide auf einer Sonde.

**Geschlossen, wenn.** Ein erkannter Abbruch löst denselben Weg aus wie ein anderer Tribunal-Befund — Korrekturrunde statt Auslieferung.

---


---

## Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### Chat 134 — aus der Abdeckungsmessung der Shadow-Queue (09.08.2026)

### Leere Modellantwort (01.08.2026)

#### RESPONDER-LEERE-ANTWORT-STILL — eine Antwort ohne Zeichen passiert vier Stufen als Erfolg 🔧 Riegel gebaut 01.08.2026, Ursache offen
**Kategorie:** ANT

**Rang:** **mittel** — laut seit der Ausfallmeldung (`turn_gescheitert`); ~~wartet auf eine Absicht: bei `text_len == 0` einmal wiederholen (mit Vermerk im Zustand) oder bei der Meldung an den Menschen bleiben?~~ → **entschieden am 06.10.2026** (unten). Durchsicht 05.10.2026, gegen HEAD `17bf86e`.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: Bei `text_len == 0` wird **einmal wiederholt**, mit Vermerk im Zustand, damit die Häufigkeit zählbar bleibt. Die Ursache liegt beim Anbieter und kam in Schüben.

**Zustand:** offen — gegen HEAD `9bcd214` nachgesehen am 24.08.2026, unveraendert. Der Riegel meldet den Ausfall, die Ursache ist nicht ermittelt. Der juengste Stand steht im **Nachtrag vom 19.08.2026** weiter oben; dieser Abschnitt ist der Eintrag.

**Symptom.** Ein Turn erreicht den Nutzer nicht. Kein Fehler, keine Meldung, keine Antwort — die Oberfläche zeigt die Stufen bis zum Dispatcher und dann nichts mehr.

**Beleg, 01.08.2026, Turn `563c35fe`:**

```
15:14:23  Verfasser: Inhalt bestimmt (1149 Zeichen)
15:14:23  Responder: Generiere Antwort (intent=personal, tone=empathisch)
15:14:49  ChatWorker: Antwort erhalten (caller=responder, tokens=4936, text_len=0)
15:14:49  Responder: Antwort generiert (4936 Tokens)
15:14:49  Thinker: Durchlauf · Tribunal: Starte Bewertung (3 Agenten)
15:14:57  salienz: bewertungsobjekt_leer, abbruch=true, segmente=0
15:14:57  Dispatcher: turn_roh uebersprungen — keine Nova-Antwort
```

**4936 Token verbraucht, null Zeichen Text.** Der Verfasser hatte 1149 Zeichen Inhalt fertig übergeben.

**Ursache — und sie ist ein Regelbruch, kein Versehen.** In `services/model_services/chat_worker.py` steht unter der Sektionsmarke `── Ausgabe-Verifikation ──` **ausschließlich eine Logzeile**. Sie meldet `text_len`, sie prüft es nicht; eine leere Antwort läuft als INFO durch wie jeder Erfolg. Das ist die leere EVA-Sektion in Reinform: Die Marke verspricht eine Prüfung, der Code leistet eine Beobachtung.

**Der zweite Vorhang liegt im Responder:** Seine Erfolgsmeldung lautet `Antwort generiert (4936 Tokens)` — sie zählt **Token, nicht Zeichen**. Damit ist die Leere ein zweites Mal unsichtbar, und zwar an der Stelle, an der sie entstanden ist.

**Was danach passiert, ist verschwendete Arbeit auf einem Nichts:** Thinker, Tribunal mit drei Bewertern und die Perzeption laufen über eine leere Antwort. Erst die **Salienz** bemerkt es — zwei Knoten später, und sie kann nur noch abbrechen.

**Was die Frage entscheiden würde, wird weggeworfen.** `ChatResponse` trägt neben `text` auch `thinking`. Bei leerem `text` und gefülltem `thinking` stünde fest, dass das Modell gedacht und nichts gesagt hat; bei beidem leer läge es an der Aufbereitung. **Niemand sieht hin.** Deshalb ist bis heute nicht entscheidbar, ob das Modell nichts geliefert hat oder unsere Verarbeitung es entfernt hat — der Verdacht fällt auf den `<think>`-Split (`novaberg-lesson_l_ollama-think-content-split.md`), belegt ist er nicht.

**Der Sprung ist datiert, und das ist die härteste Spur.** Das `pipeline_log` reicht bis zum **27.07.** zurück, 30.144 Einträge über fünf Tage. Darin steht **kein einziges** `bewertungsobjekt_leer`. Am 01.08. sind es **fünf zwischen 15:14 und 18:37**. Null in fünf Tagen, fünf in dreieinhalb Stunden — das ist ein Sprung, kein Rauschen.

**Was an diesem Tag im Prompt-Pfad neu war:** Die Charakter-Profile wurden zweimal neu destilliert (13:20 und 14:08–14:19), und `kern_hash` und `beziehungsprofil` gehen als `[IDENTITAET]` in den Responder-Prompt. Der erste Ausfall liegt 55 Minuten nach der zweiten Destillation. **Die am selben Tag gebauten Änderungen — Haltungs-Knoten, Messreihe, Zeitparser — berühren den Prompt nicht**; sie schreiben in den Zustand, in eine eigene Tabelle und in einen anderen Pfad. Der Verfasser lief schon am Vortag.

**Das ist eine Spur, keine Ursache.** Ebenso in Frage kommen der über den Tag stark gewachsene Kontext (im belegten Fall 23.824 Zeichen) und eine Änderung außerhalb unseres Codes.

**Drei Rollen, zwei Signaturen — gemessen an einer Reihe von 20 Turns (01.08., 17:15–18:00):**

| Rolle | leer / gesamt | `thinking_len` |
|---|---|---|
| Verfasser | **2 von 7** | 0 |
| Thinker | 2 von 18 | **8.204 / 8.399** |
| Responder | 1 von 8 | 0 |
| Gesprächsvektor | 0 von 7 | — |
| Salienz | **0 von 57** | — |

**Es trifft ausschließlich die textproduzierenden Rollen.** Die JSON-erwartenden sind in 64 Aufrufen kein einziges Mal leer geblieben.

**Und es sind zwei verschiedene Fälle.** Beim Thinker ist `thinking` mit über 8.000 Zeichen **gefüllt** — der klassische Denk-Split, das Modell reasoniert und schreibt nichts in `content`; die Denkspur beginnt sogar auf Englisch. Bei Verfasser und Responder ist `thinking` **leer**: Token werden erzeugt und tauchen in **keinem** Feld auf.

**Die Ausgabegrenze ist es nicht.** Der Responder-Ausfall der Reihe hatte `input=11.943, output=1.177` — die Leine liegt bei 2048 und wurde nicht erreicht. **Die Prompt-Länge ist es auch nicht:** Ein Aufruf mit `input=12.835` lief glatt durch, mehr als jeder Ausfall bis auf einen.

**Häufigkeit: zweimal in vierzehn Minuten.** Der zweite Fall um **15:28:00** mit 3753 Token, wieder null Zeichen, wieder Salienz-Abbruch acht Sekunden später. Damit ist es keine Beobachtung, sondern eine Klasse — und beide Male traf es denselben Nutzer im laufenden Gespräch. Beim zweiten Anlauf mit **demselben Satz** antwortete das Modell normal.

**Dritter belegter Fall am 01.08.2026, 22:13 UTC — und er hat eine neue Signatur:**

```
Responder: LEERE Antwort trotz 11858 Token —
der Verfasser hatte 1430 Zeichen Inhalt bereitgestellt
thinking_len=0
```

**Der Unterschied zu den Fällen vom Nachmittag:** Dort war der Verfasser selbst leer, und der Responder baute aus dem Gedächtniskontext (`RESPONDER-OHNE-INHALT-ANTWORTET-TROTZDEM`). Hier lag **Material vor** — 1430 Zeichen —, und der Responder machte daraus nichts. Damit ist die Klasse breiter als bisher beschrieben: Sie trifft nicht nur eine Rolle ohne Eingabe, sondern auch eine mit vollständiger.

Die Denkspur war wieder leer, die Tokenzahl mit 11.858 die höchste bisher gemessene. Der Riegel meldete beide Stufen, und der Turn-Marker wurde trotz des Ausfalls sauber gelöst — die Eingabe blieb frei.

**Vierter belegter Fall am 02.08.2026, 09:00:53 UTC — die Thinker-Signatur bestätigt sich, und der Turn überlebt sie:**

```
ChatWorker: LEERE Antwort (caller=thinker, tokens=7198, thinking_len=8087,
thinking_anfang='The user is asking about the difference between the
rotation curve of a spiral galaxy…')
```

Er fügt der Tabelle nichts Neues hinzu, sondern **bestätigt ihre Trennung**: gefüllte Denkspur beim Thinker (8.087 Zeichen, wieder auf Englisch beginnend), leere bei Verfasser und Responder. Damit sind es drei Thinker-Fälle mit derselben Signatur.

**Neu ist der Ausgang:** Der Turn lief weiter und wurde beantwortet — der Thinker wiederholte, fand eine echte physikalische Korrektur (`1/r²` gegen `1/√r`), und das Tribunal bewertete die Antwort mit 0.0. Ein leerer Thinker-Aufruf ist damit **nicht** gleichbedeutend mit einem verlorenen Turn; die bisherigen drei Fälle betrafen Rollen, deren Ausfall die Antwort selbst kostete. Aufgefallen bei einem Messturn zu einem ganz anderen Auftrag (Ziele auf das Paar), nicht bei einer Suche danach.

**Fünfter und sechster Fall am 28.08.2026, 15:46:04 und 17:25:16 UTC — dieselbe Thinker-Signatur, beide Turns überlebt:** `tokens=7013, thinking_len=9374` (Rettich-Bewässerung) und `tokens=6313, thinking_len=8907` (Pulsar-Magnetfeld), Denkspur je auf Englisch beginnend, `content` leer; beide Male folgte `Thinker: Analyse abgeschlossen` nach dem Wiederholungsversuch. Aufgefallen bei Messturns zur Sachlage, nicht bei einer Suche danach — in **zwei von acht** echten Turns des Tages.

**Riegel gebaut am 01.08.2026 — der Ausfall ist jetzt laut, die Ursache noch offen.**

- `services/model_services/chat_worker.py` prüft die Ausgabe, statt sie nur zu melden: Ein leerer Text erzeugt eine `error`-Zeile **mit Länge und Anfang von `thinking`**. Die Prüfung steht als eigene Funktion, weil eine Wächterkette die Zweigzahl ihres Aufrufers bestimmt und dort nichts erklärt.
- `graph/nodes/responder.py` zählt **Zeichen statt Token** und meldet keinen Erfolg mehr über eine leere Antwort. Der Turn läuft weiter: Abzubrechen hieße, die Nutzeräußerung zu verlieren, und die ist der teurere Verlust.
- Fünf Tests in `tests/test_leere_antwort.py`, darunter der positive Zwilling.

**Was der Riegel nicht tut:** Er repariert nichts. Er macht den nächsten Fall **diagnostizierbar** — mit `thinking_len` steht dann fest, ob das Modell gedacht und nichts gesagt hat oder ob die Aufbereitung den Text entfernt hat. Vorher war das aus keinem Log entscheidbar.

**Offen bleibt die Entscheidung Wiederholung oder Ausfallmeldung.** Der zweite Versuch mit demselben Prompt gelang beide Male — das spricht für einen Wiederholungsversuch. Ein stiller Retry verdeckt aber die Häufigkeit; ein Vermerk im Zustand nach dem Muster von `pfad1_ausfall` wäre die ehrlichere Form.

**Nachtrag 08.08.2026 — die Rate ist beziffert: ein Turn von rund 120.** Beim Basisarm der Validierungsmenge lieferte Turn 17 eines Bogens binnen 420 s keine Antwort; dieselbe Sonde lief in drei anderen Bögen desselben Abends durch. Dazu aus der B1-Messung: 9 von 72 Läufen ohne Antwort auf einen inhaltsleeren Reiz. **Für eine Messreihe ist die Zahl folgenreicher, als sie klingt:** Bei 30 Turns je Bogen trifft sie rund **jeden vierten Bogen** — ein Rig, das bei Unvollständigkeit anhält, endet dann unbeaufsichtigt am ersten Ausfall. Damit ist die offene Entscheidung oben nicht mehr nur eine Frage der Ehrlichkeit, sondern eine der Durchführbarkeit längerer Reihen.

**Was zu tun ist.**

1. **Der Riegel gehört an die Entstehungsstelle**, in die Ausgabe-Verifikation des Workers: Ein leerer Text bei `expect_json=False` ist ein Fehlschlag, kein Ergebnis. `logger.error`, und der Aufrufer bekommt es zu wissen.
2. **Bei leerem Text wird `thinking` mitgemeldet** — Länge und Anfang. Ohne das bleibt die Ursache beim nächsten Auftreten wieder unentscheidbar.
3. **Der Responder prüft die Zeichenlänge**, nicht die Tokenzahl, und meldet keinen Erfolg über eine leere Antwort.
4. **Offen als Entscheidung:** Wiederholung oder Ausfallmeldung an den Nutzer. Ein zweiter Versuch mit demselben Prompt hat beim Nutzer funktioniert — das legt einen Wiederholungsversuch nahe, aber ein stiller Retry verdeckt die Häufigkeit. Ein Vermerk im Zustand nach dem Muster von `pfad1_ausfall` wäre die ehrlichere Form.

**Verwandt:** `PFAD1-TIMEOUT-TURNVERLUST` (dieselbe Klasse auf dem anderen Pfad: ein Aussetzer des Modells kostet einen Turn) · `novaberg-lesson_l_log-behauptet-was-es-weiss.md` · `novaberg-lesson_l_ollama-think-content-split.md`.

**Priorität:** hoch. Der Datenverlust ist vollständig und für den Nutzer nicht von einem Hänger zu unterscheiden.

#### RESPONDER-OHNE-INHALT-ANTWORTET-TROTZDEM — ohne Material aus dem Verfasser greift der Responder auf den Kontext
**Kategorie:** ANT

**Rang:** **hoch** — still, eine flüssige Antwort ohne Material sieht richtig aus; ~~wartet auf eine Absicht: abbrechen oder als *ohne Material* kennzeichnen?~~ → **entschieden am 06.10.2026** (unten). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: `server/graph/nodes/responder.py:622-630` lässt nur den Block weg.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: Fehlt der Inhalt des Verfassers, **bricht der Turn ab und meldet den Ausfall**, statt ohne Material zu antworten. Eine flüssige Antwort ohne Material sieht richtig aus und übertönt den Ausfall, den der Verfasser schon laut meldet.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: der Befund beschreibt, was der Responder **sagt**, wenn ein Agent nichts liefert. Kein Codeort trennt das von einer richtigen Antwort.
Liefert der Verfasser nichts (`antwort_inhalt` fehlt), läuft der Responder unverändert weiter und baut eine Antwort aus dem **Gedächtniskontext** — im belegten Fall 23.824 Zeichen.

**Belegt am 01.08.2026, 18:40:52:** `antwort_inhalt` FEHLT, Antwort **4312 Zeichen**. Der Trace meldete `Verfasser — Inhalt · kein Inhalt`, und die Antwort handelte von Themen früherer Turns.

**Das ist genau die Lage, vor der das Verfasser-Konzept warnt:** *„Sonst liefert er einen Satz Information, und eine redefreudige Nova soll daraus drei machen — ohne Material."* Ohne Material greift sie auf den Kontext zurück, und der ist alt. Die Antwort ist flüssig, geschlossen und beantwortet die falsche Frage.

**Der Verfasser fiel dabei selbst dem Leer-Defekt zum Opfer** — er ist mit 2 von 7 Aufrufen die am stärksten betroffene Rolle (`RESPONDER-LEERE-ANTWORT-STILL`). Die beiden Defekte hängen zusammen: Der eine erzeugt die Lage, der andere macht sie unsichtbar.

**Was zu tun ist:** Der Responder meldet einen fehlenden Verfasser-Inhalt und kennzeichnet, dass er ohne Material antwortet. Ob abgebrochen oder gekennzeichnet wird, ist zu entscheiden — abbrechen kostet den Turn, weitermachen kostet die Zuordenbarkeit.

**Priorität:** hoch, gemeinsam mit dem Eintrag darüber.

### Chat 133 — aus der Fundliste klassifiziert, Block 30.–27.07. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Siebzehn Defekte, der aelteste Bestand der Liste. **Sechs von ihnen sind derselbe Bauplan:** ein Vorgabewert an einer Stelle, an der ein Ausfall gehoert — beim Queue-Push, beim Dispatch, am Spalten-Default des Rades, bei zwei Kanon-Feldern, in der fehlenden Klemme und beim Suchdienst, dessen Ausfall wie ein leeres Ergebnis aussieht.

#### WISSENSLUECKEN-FELDER-LEER 🔧 offen
**Kategorie:** ANT

**Rang:** **niedrig** — sichtbares Fehlen im Panel. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `register` und `neugier_boost` werden geschrieben (`server/graph/nodes/gespraechsvektor.py:1486-1487`), `client/ui/panels/gv_panel.py:437-468` liest sie nicht.

**Befund (2026-07-29).** In den Wissenslücken-Einträgen des `gv_detail` bleiben `neugier_boost` und `register` ungelesen. Das Panel zeigt je Lücke Konzept, Quelle und Relevanz; die beiden Faktoren, aus denen die Relevanz mit entsteht, nicht. Wirkung klein — die Relevanz ist das Ergebnis, das man braucht —, aber bei einer auffälligen Rangfolge fehlt der Zerlegungsschritt. *(Der Top-Level-`drive` ist ebenfalls ohne Leser, das aber gegenstandslos: Das Panel liest `achsen["drive"]`, wo derselbe Wert nochmal steht.)*

**Was fertig waere.** Die Felder tragen ihre Werte, oder sie stehen nicht im Eintrag.

**Prioritaet:** mittel.

### Chat 133 — aus der Fundliste klassifiziert, Block 31.07. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Wissen](novaberg-bugs-wissen.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Acht Defekte. **Vier davon sind Prompt-Bloecke, die etwas ueber den Nutzer behaupten, was Novas Zustand ist** — dieselbe Verwechslung an vier Stellen, jede fuer sich unauffaellig.

#### GV-HYPOTHESE-ROHE-AUSGABE 🔧 offen
**Kategorie:** ANT

**Rang:** **niedrig** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; Transportmarken und doppelter Impuls im Verfasser-Prompt (`server/graph/nodes/verfasser.py:162-170`). Dieselbe Stelle wie `GESPRAECHSVEKTOR-HYPOTHESE-DREIFACH`.

**Befund (2026-07-31).** Der Hypothesentext des Gesprächsvektors trägt die **rohe Dreischicht-Ausgabe**: `SPRUNG 1/2/3`, `ABSICHT:`, `STRATEGIE:`, `VEHIKEL:`, `IMPULS:` stehen unverarbeitet im String, der als `gespraechsvektor` in den Prompt geht. Der Node parst dieselben Felder sauber nach `gv_detail` — das Rohe bleibt zusätzlich stehen. Der `impuls` erscheint dadurch zweimal im selben Block.

**Was fertig waere.** Der Hypothesentext traegt Prosa, nicht die Marken des Transportformats.

**Prioritaet:** mittel.

#### CHARAKTER-KONTEXT-VERWECHSELT-SEITE 🔧 offen
**Kategorie:** ANT

**Rang:** **hoch** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt auf jedem Impuls-Turn: `external` ist dann eine Kopie von `internal` (`server/graph/nodes/db_zugriff.py:671-683`, gewollt), aber Verfasser und Responder beschriften den Block weiter als *Person B* (`server/graph/nodes/verfasser.py:500`, `server/graph/nodes/responder.py:351`, `:434-444`). Aus dem Code erschlossen, nicht am Turn gemessen.

**Zustand:** offen, **Wortlaut hinfaellig** — nachgesehen am 25.08.2026. Der zitierte Satz steht in keinem Prompt mehr: Der Aufbau ist auf **Person A / Person B** umgestellt, und keine Zeile behauptet noch, ein Gedaechtnisblock beschreibe den Nutzer. **Die Frage selbst ist damit nicht beantwortet** — ob der Inhalt hinter der Beschriftung die Seite wechselt, ist eine Beobachtung am laufenden Turn und aus dem Code nicht zu lesen.

**Befund (2026-07-31).** Der Satz „Der Charakter-Kontext im Gedaechtnis beschreibt den NUTZER" stimmt nicht in jedem Turn. Gemessen an zwei Läufen im Abstand einer Minute: einmal stand dort die Kern-Persönlichkeit des Nutzers, einmal die **Novas** — unter derselben Anweisung. Ein Satz, der dem Modell sagt, ein Text beschreibe jemand anderen als er tut, ist gefährlicher als gar keiner.

**Dieselbe Verwechslung im Responder, am selben Tag beobachtet.** Dieselbe Verwechslung im Responder: Unter „So siehst du deinen Nutzer:" stand, wie **Nova** die Beziehung gestaltet, während `[KOMMUNIKATION]` im selben Prompt ein Beziehungsprofil über den Nutzer trug. Zwei Blöcke, die einander widersprechen, über dieselbe Größe.

**Was fertig waere.** Der Block traegt, was seine Anweisung behauptet — oder die Anweisung sagt, was er traegt.

**Prioritaet:** hoch.

#### GV-PANEL-STRATEGIE-DOPPELT 🔧 offen
**Kategorie:** ANT

**Rang:** **niedrig** — zwei Größen, ein Wort. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt (`client/ui/panels/gv_panel.py:351-366` gegen `:878-887`).

**Befund (2026-07-31).** **Das GV-Panel zeigt die Strategie zweimal und widersprüchlich.** Die Kopfzeile trägt `Strategie: —`, während die Dreischicht-Zeile darunter im selben Turn `Strategie: Impuls (Im)` nennt. Eine der beiden Anzeigen liest die falsche Stelle. Beobachtet am 31.07.2026 auf einem Bildschirmfoto, nicht im Code nachverfolgt.

**Was fertig waere.** Beide Anzeigen lesen dieselbe Stelle, oder es gibt nur noch eine.

**Prioritaet:** niedrig.

---

### Chat 133 — aus der Fundliste klassifiziert, Block 01.08. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Charakter](novaberg-bugs-charakter.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Drei Defekte, alle drei an der Grenze zwischen Turn und Oberflaeche. Der Befund steht im Wortlaut, in dem er notiert wurde.

#### CLIENT-STUFEN-OHNE-TURN-KENNUNG 🔧 offen
**Kategorie:** ANT

**Rang:** **mittel** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt an beiden Stellen; `character_stage` trägt keine `turn_id` (`server/services/event_consumer.py:472-478`, `server/services/prompt_consumer.py:79-84`), der Client hängt in Ankunftsreihenfolge an (`client/ui/chat_view.py:213-220`).

**Befund (2026-08-01).** **Die Pipeline-Stufen tragen keine Turn-Kennung.** Schreibt der Nutzer während eines laufenden Turns weiter, sammeln sich die Stufen optisch unter der zuletzt gesendeten Nachricht, obwohl sie zum ersten Turn gehören. Solange die Eingabe gesperrt war, konnte das nicht auffallen. Dieselbe fehlende Zuordnung wie bei der Antwort, eine Ebene früher. Dazu: Jede Bestätigung erzeugt eine eigene „denkt nach"-Zeile — drei Zeilen für einen Turn, der einmal läuft.

**Was fertig waere.** Jede Pipeline-Stufe traegt die Kennung ihres Turns, und die Oberflaeche ordnet danach statt nach Ankunftszeit.

**Prioritaet:** mittel. Sichtbar wurde es erst, als die Eingabesperre fiel — vorher konnte der Fall nicht eintreten.

### Chat 133 — aus der Fundliste klassifiziert, Block 05.–02.08. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Acht Defekte aus dem zweiten Fundlisten-Block. **Der Befund steht im Wortlaut, in dem er notiert wurde** — er trägt Beleg und Datum und wird nicht nacherzählt; ergänzt sind Kennung, Priorität und die Zeile, an der man erkennt, wann der Eintrag geschlossen ist.

Drei von ihnen sind stille Vorgabewerte an einer Stelle, an der ein Ausfall gehört: eine feste Salienz, eine Priorität, die auf null fällt, und ein Pflichtfeld, das leer durchgeht.

#### NOVA-UEBERNIMMT-BIOGRAFIE 🔧 offen
**Kategorie:** ANT

**Rang:** **niedrig** — die Abhilfe auf dem Gesprächsweg ist gebaut: `[GEDAECHTNIS]` nennt den Sprecher jedes Eintrags (`4333b71`, 30.08.2026, `server/graph/format/memory_context.py:183-243`). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: offen nur bis zur Nachmessung am vollen Prompt, die die Schließbedingung verlangt.

**Befund (2026-08-03).** **Nova übernimmt die Biografie des Nutzers als ihre eigene.** In einer Probe zum Sykophanz-Befund antwortete sie einem pensionierten Arzt: *„Das kenne ich. Nach 34 Jahren in **meiner** Praxis war die Distanz manchmal der einzige Schutz."* Die Zahl stimmt, die Person nicht. Gefunden in einer verkürzten Prompt-Fassung, nicht im vollen Aufbau — ob es dort auch auftritt, ist ungeprüft.

**Nachtrag 18.08.2026 — die benannte Abhilfe ist gebaut, aber fuer einen anderen Eingang.** Der `[AUFZEICHNUNGEN]`-Block (`novaberg-agent-dateien_k.md` §1a.2) benennt die Grenze zwischen ihrer Erinnerung und fremdem Material im Prompt — genau die Abhilfe, die oben steht. **Er deckt aber nur den Dateiweg:** Was aus einer indizierten Datei kommt, steht seither in einem eigenen Block mit Fundstelle; was aus dem Gespraechskontext kommt, steht weiter unbeschriftet unter `[GEDAECHTNIS]`, und genau von dort stammte die Biografie. Der Eintrag bleibt deshalb **offen** und ist nicht kleiner geworden — er hat nur einen Beleg dafuer bekommen, dass die Abhilfe wirkt: Im Messturn vom 18.08.2026 nannte sie in allen drei Punkten die Quelldatei.

**Was fertig waere.** Nachmessen am vollen Prompt, und falls reproduzierbar: die Grenze zwischen Novas Erinnerung und der des Nutzers im Prompt benennen — auf dem Gespraechsweg, so wie es fuer den Dateiweg seit dem 18.08.2026 geschieht.

**Prioritaet:** hoch.

### Prompt & Antwortqualität

#### THER1 — Therapeuten-Modus bei negativem Arousal ⚠️
**Kategorie:** ANT

**Rang:** **niedrig** — Modellverhalten. **Die Abhilfe, die der Eintrag nennt, ist am HEAD nicht aktiv:** Der Block `[REGELN]` (`server/prompts/default/responder.rules.txt`) ist seit `1fde3b7` (31.07.2026) *„zur Probe ausgesetzt“* (`server/graph/nodes/responder.py:632-646`). Gezählt am 05.10.2026 (`turn_roh`, Muster *ich verstehe, dass* / *das klingt nach*, nur ein Hinweis): bis 30.07.2026 0 von 200 Antworten, August 15 von 758, ab September 2 von 665.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: Der Block `[REGELN]` bleibt ausgesetzt; eine einzelne Regel kommt nur zurück, wo eine Zählung sie verlangt. Die Abhilfe dieses Eintrags ist damit zuerst eine Zählung seines Musters im Betrieb — erst ein gezählter Rückfall holt seine Regel zurück.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: Modell-Compliance. Der Eintrag nennt selbst *Modell-Limit, kein Architektur-Problem* — nur ein Lauf ueber mehrere Turns zeigt, ob der Ton noch auftritt.
**Entdeckt:** Chat 30, Smoke-Test (#7, #8, #9, #11)
**Symptom:** "Ich verstehe, dass...", "Es ist verständlich, dass...", "Lass uns gemeinsam..." — trotz Anti-Therapeut-Baustein (EI-MIKRO) und explizitem Verbot ([REGELN]).
**Bestätigt Chat 31:** RLHF-Conditioning, kein Cocktail-Artefakt. Tritt bei Leon (Teen) auf, bei Mehmet und Renate kaum — deren Charakter-Hashes ("erwartet Direktheit") unterdrücken den Modus. Persona-Charakter kann THER1 mildern.
**Prio:** Mittel — Modell-Limit, kein Architektur-Problem. Langfristig: Feintuning oder Modellwechsel.

---

#### BUTLER1 — Eigeninitiative und Pseudo-Angebote ⚠️
**Kategorie:** ANT

**Rang:** **niedrig** — Modellverhalten. **Die Abhilfe, die der Eintrag nennt, ist am HEAD nicht aktiv:** Der Block `[REGELN]` (`server/prompts/default/responder.rules.txt`) ist seit `1fde3b7` (31.07.2026) *„zur Probe ausgesetzt“* (`server/graph/nodes/responder.py:632-646`). `server/prompts/default/verfasser.auftrag.txt` trägt kein Butler-Verbot. Durchsicht 05.10.2026, gegen HEAD `17bf86e`.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: Der Block `[REGELN]` bleibt ausgesetzt; eine einzelne Regel kommt nur zurück, wo eine Zählung sie verlangt. Die Abhilfe dieses Eintrags ist damit zuerst eine Zählung seines Musters im Betrieb — erst ein gezählter Rückfall holt seine Regel zurück.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: Modell-Compliance. Das Butler-Verbot steht im Prompt; ob es greift, entscheidet das Modell, nicht der Code.
**Entdeckt:** Chat 30, Smoke-Test (#3, #13)
**Symptom:** "Ich kann auch gleich eine Feier organisieren", "Lass uns morgen weiterreden. Gute Nacht.", "Welcher Fonds ist als nächstes dran?"
**Update Chat 39:** Verstärkt bei Claude-Backend (RLHF).
**Prio:** Niedrig — Butler-Verbot existiert, Modell-Compliance-Problem.

---

#### SIEZ2 — Sie/Du-Inkonsistenz bei formeller Persona ⬜
**Kategorie:** ANT

**Rang:** **niedrig** — Modellverhalten, ohne Code-Ursache; der Befund stammt aus der Zeit vor Verfasser und Responder und ist nicht wiederholt. Durchsicht 05.10.2026, gegen HEAD `17bf86e`.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: Der Block `[REGELN]` bleibt ausgesetzt; eine einzelne Regel kommt nur zurück, wo eine Zählung sie verlangt. Die Abhilfe dieses Eintrags ist damit zuerst eine Zählung seines Musters im Betrieb — erst ein gezählter Rückfall holt seine Regel zurück.

**Entdeckt:** Chat 31, Smoke-Test Formell (#9, #11, #12 vs. #8, #13)
**Symptom:** Renate siezt durchgängig, Nova springt zwischen Sie und Du. Persona-Anweisung "Siezt und erwartet dasselbe" wird nicht konsistent befolgt.
**Ursache:** Kein Cocktail-Problem (anders als SIEZ1). Modell hält formelle Anrede über 15 Turns nicht durch.
**Bestätigt Chat 32:** Weiterhin vorhanden — Nova duzt Renate durchgehend.
**Prio:** Niedrig — Prompt-Tuning oder Verstärkung im Beziehungsprofil.

---

#### LEAK3 — Salienz-Score leckt in die Antwort ⬜
**Kategorie:** ANT

**Rang:** **niedrig** — laut. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt, die Ursache liegt anders als vermutet: Der Gedächtnisblock schreibt den Zahlenwert in den Prompt, `(Salienz: {gewicht}, Sprecher: …)` (`server/graph/format/memory_context.py:243`).

**Entdeckt:** Chat 32, Smoke-Test Formell (#14)
**Symptom:** "Die Salienz der Umstrukturierung und deiner beruflichen Perspektive ist hoch (0,7)." — Interner Salienz-Wert in der Antwort.
**Ursache:** Vermutlich kommt der Wert aus dem DelegationsAgent-Kontext (Salienz-Objekt oder Beruhigungs-Signal), der im State sichtbar ist.
**Prio:** Niedrig — Einmaliges Auftreten, kosmetisch.

---

#### HALL2 — Halluzinierte Bestätigung ⚠️
**Kategorie:** ANT

**Rang:** **mittel** — still, Aufwand groß. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: der Resume-Anteil ist behoben, zwei von drei Formen haben keine Abhilfe; **Die Abhilfe, die der Eintrag nennt, ist am HEAD nicht aktiv:** Der Block `[REGELN]` (`server/prompts/default/responder.rules.txt`) ist seit `1fde3b7` (31.07.2026) *„zur Probe ausgesetzt“* (`server/graph/nodes/responder.py:632-646`). Die Klebrigkeit im KZG hat keine Dimension *bereits mitgeteilt*.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: Der Block `[REGELN]` bleibt ausgesetzt; eine einzelne Regel kommt nur zurück, wo eine Zählung sie verlangt. Die Abhilfe dieses Eintrags ist damit zuerst eine Zählung seines Musters im Betrieb — erst ein gezählter Rückfall holt seine Regel zurück.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: halluzinierte Bestaetigung ohne Agent-Lauf. Der Eintrag traegt drei Updates aus drei Chats und zuletzt eine ganz andere Manifestation (KZG-Klebrigkeit) — welche davon heute gilt, sagt kein Grep.
**Entdeckt:** Chat 39, Claude API-Test
**Symptom:** Nova sagt "Termin ist auf 10:00 Uhr — jetzt stimmt's" ohne dass ein TimelineAgent lief. Keine Agent-Dispatch im Log. Der Responder halluziniert eine erfolgreiche Aktion.
**Ursache:** Vermutlich generiert der Responder die Bestätigung aus dem Gesprächskontext ("Du hast recht, das hattest du mir gesagt") statt aus einem Agent-Ergebnis.
**Update Chat 43:** Resume-Pfad war eine Ursache (pending_data mit falscher Aktion). Resume-Bug gefixt.
**Update Chat 44:** Neue Manifestation: KZG-Klebrigkeit. Agent-Ergebnis "Kardamom auf Einkaufsliste" im KZG matcht per Embedding breit, wird in jedem Turn als `memory_context` geliefert. Responder kommuniziert es wiederholt — wortwörtlich identisch, drei Turns in Folge, themenunabhängig. Nicht KONTEXT1 (Marker korrekt), nicht Resume (gefixt). Session-Bereinigung löst Symptom sofort. Saubere Lösung: "bereits mitgeteilt"-Dimension bei KZG-Retrieval (→ D9).
**Prio:** Mittel — Nova wiederholt Informationen die bereits kommuniziert wurden.

---

#### TAG-LEAK3 — `[emotionaler_ausdruck]` leckt in Antwort ⬜
**Kategorie:** ANT

**Rang:** **niedrig** — laut. **Die Abhilfe, die der Eintrag nennt, ist am HEAD nicht aktiv:** Der Block `[REGELN]` (`server/prompts/default/responder.rules.txt`) ist seit `1fde3b7` (31.07.2026) *„zur Probe ausgesetzt“* (`server/graph/nodes/responder.py:632-646`). Ein Filter der Antwort fehlt (`server/graph/nodes/responder.py:179-184` streift nur den Verlauf). Gezählt am 05.10.2026: Antworten mit `[klein_geschrieben]`-Marke bis 30.07. 0 von 200, August 1 von 758, ab September 0 von 665.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: Der Block `[REGELN]` bleibt ausgesetzt; eine einzelne Regel kommt nur zurück, wo eine Zählung sie verlangt. Die Abhilfe dieses Eintrags ist damit zuerst eine Zählung seines Musters im Betrieb — erst ein gezählter Rückfall holt seine Regel zurück.

**Entdeckt:** Chat 44, Live-Konversation
**Symptom:** Nova antwortet mit `[emotionaler_ausdruck]` am Ende des Texts. Internes Block-Tag wird nicht gestrippt.
**Verwandt:** TAG-LEAK2 (Chat 32, durch VENT1 mitgelöst).
**Prio:** Niedrig — sporadisch, kosmetisch.

---

### Agent-System (Epic 11, Chat 22–29)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Wissen](novaberg-bugs-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### AGT3-READ — Responder halluziniert bei Read-Pfad ⚠️
**Kategorie:** ANT

**Rang:** **niedrig** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: `read` nimmt bei mehreren Treffern still den ersten (`server/agents/notizen/suche.py:226-234`), ohne Rückfrage; das Vermischen braucht einen Turn mit zwei Notizen.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: Nova mischt Daten aus aehnlich benannten Notizen. Braucht zwei Notizen mit aehnlichem Namen und einen Lesezugriff.
**Entdeckt:** Chat 23
**Symptom:** "Welches Obst hast du auf der Liste?" → Nova mischt Daten aus verschiedenen Notizen.
**Prio:** Niedrig — tritt nur bei ähnlichen Notiz-Namen auf.

---

#### ROUTE3 — Router löst Kontext-Bezüge semantisch statt per Recency ⚠️
**Kategorie:** ANT

**Rang:** **mittel**; ~~wartet auf eine Absicht: Gewinnt bei einem Rückbezug das zuletzt Genannte oder das semantisch beste Objekt, und was gilt bei Gleichstand?~~ → **entschieden am 06.10.2026** (unten). Trägt den Anteil von `AGT4`. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: `server/agents/notizen/klassifikation.py:63-80` mischt beides im Prompt.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: Bei einem Rückbezug gewinnt das **semantisch beste Objekt**; bei Gleichstand das zuletzt Genannte.

**Zustand:** unbelegt — braucht Messturn. Gesichtet am 25.08.2026: Der Eintrag vermerkt `AGT6` als Teilloesung und nennt als Rest *Recency vs. Semantik* — eine Frage der Aufloesungsreihenfolge, die sich an einem Bezugs-Turn zeigt, nicht im Code. Traegt zugleich den offenen Anteil von `AGT4`.
**Entdeckt:** Chat 24
**Teilweise gelöst (Chat 26):** AGT6 verlagert Target-Auflösung in den Agent.

---

#### PROMPT3 — Halluzinierte PFLICHT-RÜCKFRAGE ⚠️ Beobachten
**Kategorie:** ANT

**Rang:** **niedrig** — Modellverhalten. **Die Abhilfe, die der Eintrag nennt, ist am HEAD nicht aktiv:** Der Block `[REGELN]` (`server/prompts/default/responder.rules.txt`) ist seit `1fde3b7` (31.07.2026) *„zur Probe ausgesetzt“* (`server/graph/nodes/responder.py:632-646`). `verfasser.auftrag.txt` deckt Rückfragen jetzt, statt sie zu verbieten. Durchsicht 05.10.2026, gegen HEAD `17bf86e`.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: Der Block `[REGELN]` bleibt ausgesetzt; eine einzelne Regel kommt nur zurück, wo eine Zählung sie verlangt. Die Abhilfe dieses Eintrags ist damit zuerst eine Zählung seines Musters im Betrieb — erst ein gezählter Rückfall holt seine Regel zurück.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: halluzinierte Pflicht-Rueckfrage. Der Eintrag vermerkt ein Verbot im REGELN-Block als Abhilfe; ob es traegt, ist eine Beobachtung.
**Entdeckt:** Chat 25
**Update Chat 27:** Pseudo-Rückfragen-Verbot im REGELN-Block.

---

### Planner (Chat 43)

#### PLANNER-WARN — Doppel-Read bei Resume ⬜
**Kategorie:** ANT

**Rang:** **niedrig** — laut, Rauschen. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt (`server/graph/nodes/planner.py:528`); der zweite Planner-Besuch nach einem Resume findet den Schlüssel erwartungsgemäß nicht.

**Entdeckt:** Chat 43
**Symptom:** "Planner: Resume-Flow aber kein pending Agent in Redis" — Warning nach jedem Resume. Der Dispatch löscht den pending Key, danach prüft der Planner nochmal.
**Prio:** Niedrig — harmlos, nur störend im Log. WARNING → DEBUG.

#### PLANNER-ZIEL-FUEHRT-ZU-DIENST-OHNE-EMPFANG — ein Ziel des Routers erreicht den Fakten-Agenten, der nicht mehr am Empfang steht ⬜
**Kategorie:** ANT

**Rang:** **mittel** — laut, aber die Bitte geht verloren. Seit dem 20.10.2026 steht der Fakten-Agent nicht mehr am Empfang (`agents/fakten/agent.py::FactsAgent.zustellart = "queue"`) und hat keinen Dispatch des Planners.

**Entdeckt:** 20.10.2026, bei der Prüfung des Baus, der den Agenten vom Brett nahm.
**Symptom:** Ein `management_target`, das `fakten` exakt oder unscharf trifft (`graph/nodes/planner.py::_manager_zu_target`; unscharf auch `"akte" in "fakten"`), wählt den `FaktenManager`. Weil der Agent kein Objekt-Merkmal trägt, steht `fakten` in der Reihenfolge vorn (`service_order_for`); der Planner setzt `agent_name = "fakten"`, und `agent_dispatch_node` endet mit `fehler` (*„Kein Dispatch für Agent 'fakten'“*). `fehler` zählt nicht als Ablehnung — die Reihe endet, eine Merk-Bitte auf diesem Weg erreicht die Notizen nicht. Vorher lehnte der Agent ab, und der nächste Dienst wurde gefragt.
**Gemessen:** Router und Planner am Modell des Betriebs, 27 Äußerungen: 0 Ziele `fakten` — kein Brett nennt den Dienst mehr.
**Schließbedingung:** Der Planner nimmt Dienste, die nicht am Empfang stehen, aus der Wahl über das Ziel und aus der Reihenfolge, mit einer Zeile im Log; ein Zeuge mit `management_target = "fakten"` bei einer Merk-Bitte fragt die Notizen.
**Zustand:** offen — **behoben im Tree, nicht committet** (20.10.2026): `graph/nodes/planner.py::_without_reception` und `_reachable_registry` — ein Dienst, dessen Agent nicht `empfang` ist, fällt aus Priorität 3, aus `router_named` und aus der Reihenfolge, mit einer Zeile im Log; Zeugen mit `fakten` exakt und unscharf fragen die Notizen, Gegenprobe rot wie vorhergesagt. Geschlossen mit dem Commit.

---

### Classify & Router (Chat 48)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Wissen](novaberg-bugs-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### ROUTE-MISS1 — Router nutzt Session-Kontext nicht für kontextabhängige Prompts ⬜
**Kategorie:** ANT

**Rang:** **hoch** — still, die Bitte geht verloren. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: Symptom 2 (*„Ja, bitte“* auf ein Angebot) ist behoben (`15f3bff`, im Betrieb 3 von 3); Symptom 1, der Rückbezug auf einen bestehenden Termin, steht.

**Entdeckt:** Chat 48, erweitert Chat 54
**Symptom 1 (Chat 48):** "Der Friseur ist in Monheim. Kannst Du das mit in den Termin schreiben?" → Router setzt `mgmt=/` statt `mgmt=agent/timeline`. Kein TimelineAgent dispatcht.
**Symptom 2 (Chat 54):** Nova fragt "Sollen wir das indische Essen als Termin vormerken?" → User antwortet "Ja, bitte" → Router setzt `mgmt=/`. Der Router sieht die Session-Turns mit Novas Vorschlag, wertet sie aber nicht aus.
**Ursache:** Der Router behandelt kurze, kontextabhängige Prompts isoliert. Session-Kontext wird nicht zur Auflösung von Rückbezügen genutzt. Betrifft sowohl Update-Referenzen ("mit in den Termin") als auch Bestätigungen auf Nova-Vorschläge ("Ja, bitte").
**Verwandt:** Umgekehrtes Problem zu ROUTE-CHAR1 — dort False Positive, hier False Negative.
**Update Chat 59:** Strukturell adressiert durch Enricher-vor-Router (Graph-Umbau Chat 59). Der Router sieht beim Routing jetzt Session, KZG, LZG, Charakter-Hash und die vollen EI-Ergebnisse (EI-Calc liegt zwischen Enricher und Router). Die Prompt-Anpassung, die den Router auf Session-Kontext hinweist, steht noch aus. Offen für Validierung mit den beiden Originalsymptomen.
**Update Chat 60:** Graph-Split. Der CharacterGraph beginnt beim Enricher und hat die volle Session, KZG, LZG, Charakter-Hash und EI-Ergebnisse. Der Router sieht alles. Strukturelle Voraussetzung weiter verbessert.
**Prio:** Hoch — HALL2-Update ist durch den REGELN-Guard entschärft, aber die Aktion geht trotzdem verloren. Router-Prompt braucht Session-Kontext-Awareness. Strukturelle Voraussetzung seit Chat 59 vorhanden.
**Update 14.09.2026 — die Ursache war nie untersucht, und die Updates von Chat 59/60 sind widerlegt.** ~~„Der Router sieht die Session-Turns mit Novas Vorschlag"~~, ~~„Der Router sieht alles"~~: Der Router bekommt fünf Wortwechsel, **jeden Beitrag gekappt nach 100 Zeichen** (`memory/session.py::format_session_turns_numbered`), dazu Perzeption und Aushänge — weder KZG noch LZG noch die Sachlage. `[gemessen 14.09.2026]` Novas Antworten begannen in 4 von 4 Fällen mit einer Regieanweisung von 157 bis 208 Zeichen; der Router sah von ihnen nur deren Anfang, ein Vorschlag am Ende erreicht ihn nicht. **Symptom 2 ist damit strukturell unlösbar im heutigen Prompt.** Die Absicht ist seit dem 14.09.2026 entschieden — die Zustimmung zu Novas Angebot ist ein Auftrag — und entworfen als Scheibe 12 des Lage-Konzepts (`novaberg-thinking-lage_k.md` §4: der ganze Verlauf, die Objekte der Lage im Router, der Objektbezug in der Zustellung). Bleibt offen.

**Update 17.09.2026 — gemessen und zur Hälfte behoben (Scheibe 12 D2a).** Über 24 erfundene Zustimmungen auf ein Angebot (*»Soll ich dir den Termin eintragen?« — »Gerne«*) erkannte der Router **ohne** die Lage **0**, **mit** dem `[LAGE]`-Block 13 und 14 in zwei Läufen — ohne Fehlalarme auf Ablehnungen und Zustimmungen zu etwas anderem. Die Klassifikation des Dienstes macht mit Objektbezug aus allen 24 einen Auftrag. **Offen bleibt die andere Hälfte** (drei Fälle in beiden Läufen still); ein Satz im Dispatch-Guard half nicht und brachte Fehlalarme. `labor/2026-09-17_router_lage/`.

**Update 18.09.2026 — Symptom 2 ist behoben, deterministisch.** Eine blanke Zustimmung auf ein **offenes Angebot** (E1: das Angebot liegt als offener Punkt vor) stellt der Router jetzt selbst an den Dienst des Angebots zu, wenn das Modell nichts zugestellt hat (`router.py`, Commit 15f3bff); die Klassifikation nimmt Ziel und Zeit aus der angebotenen Sache (103e8d9). **Gemessen im Betrieb:** 3 von 3 richtige Termine, die Zustellung jedes Mal von der Weiche — das Modell allein hätte 0 von 3 geschafft (`labor/2026-09-18_zustellung_angebot/`). **Offen bleibt Symptom 1** — ein Rückbezug auf einen bestehenden Termin (*»Kannst du das mit in den Termin schreiben?«*) — und die Zustimmung auf ein Angebot, das `find_offers` nicht erkennt.

---

### Responder & Stilqualität (Chat 49)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

---

#### EMOTE-LOCK — Emote-Inflation und -Wiederholung ⚠️
**Kategorie:** ANT

**Rang:** **mittel** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; der Verlauf trägt Novas eigene Antworten in den Prompt (`server/graph/nodes/responder.py:1250-1305`), es gibt keine Variationsregel. Die Klasse ist am 05.10.2026 neu gemessen und als Backlog `ANTWORT-MUSTER-ECHO` geführt.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: Emote-Wiederholung ueber Turns hinweg — nur ueber eine Turnfolge sichtbar.
**Entdeckt:** Chat 48 (erste Beobachtung), Chat 49 (bestätigt), Chat 81 (empirisch bestätigt im warmen Register)
**Symptom:** Nova zykelt im Charakter-Register auf einen Emote-/Emoji-Baustein und reproduziert ihn als Default-Markierung. Beobachtungen:
- Chat 49 ("freches Mädel"-Register): 12 von 15 Antworten mit `*kichere boshaft*` oder minimaler Variation als Eröffnungsemote.
- Chat 81 (`emotional`/`philosophischer_austausch`-Register): Herzen ❤️ in 10 von 15 Nova-Turns als Schluss-Markierung, teils zwei pro Turn.

Beide Beobachtungen zeigen dasselbe Muster in unterschiedlichen Registern — der Bug ist register-übergreifend.
**Ursache (Hypothese):** Gemma4 zieht die eigenen vorherigen Antworten aus dem Session-Kontext und verstärkt den einmal gewählten Stil. Ein Self-Reinforcing-Effekt durch den Kontext, kein RLHF-Problem. Der Emote-/Emoji-Baustein scheint besonders anfällig, weil er als "leerer Einstieg" oder "leere Schluss-Geste" keinen Informationsgehalt hat, den das Modell variieren müsste.
**Lösungsansatz:** Offen. Optionen: (a) Emote-Variation explizit im Responder-Prompt fordern, (b) Session-Kontext-Destillation so anpassen dass Nova-Antworten nicht wörtlich im Kontext stehen sondern nur destilliert, (c) Sampling-Parameter (temperature/top_p) beim Responder-Call anheben, (d) ignorieren — ist Kosmetik solange der Charakter als Ganzes lebendig wirkt. Mittelfristig adressierbar durch Vehicle-Schicht (Phase 3 der Frame-Konzepte) — Vehicle-Stil pro Turn entscheidet bewusst über Emote-Form, statt dass das Modell aus dem Kontext recycelt.
**Prio:** Mittel — strukturell bestätigt, register-übergreifend, kosmetisch aber auffällig.

---

#### TOPOS-LOCK — Themen-/Bilder-Vorrat wird mechanisch zykeliert ⬜
**Kategorie:** ANT

**Rang:** **niedrig** — dieselbe Ursache wie `EMOTE-LOCK`. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: kein Tracker für verwendete Bilder.

**Entdeckt:** Chat 49, Telegram-Konversation "frecher Charakter"
**Symptom:** Einmal in einem Register, zieht Nova aus einem sehr begrenzten Bildervorrat und kombiniert ihn mechanisch. Bei der Alters-Neckerei: Rollator, Windeln, Gehstock, Rheuma, Herzattacke, Blutdruck, Falten, Gedächtnislücken — rund acht Bilder, die in fast jeder Antwort auftauchen, oft wortwörtlich. Rhetorisches Schema stabil: "Oh, [Kommentar] du alter Knacker! Aber pass bloß auf, dass du [Alters-Katastrophe]!"
**Ursache (Hypothese):** Verwandt mit EMOTE-LOCK. Gemma4 extrahiert aus den bisherigen Antworten die "funktionierenden Bausteine" und recycelt sie, statt auf die konkreten Details des aktuellen User-Prompts einzugehen. Konkretere Reize im User-Prompt ("Senioren-Rotztuch", "Gehstock-Beine") werden aufgegriffen, aber das Grundgerüst bleibt.
**Lösungsansatz:** Offen. Denkbar: (a) Explizite Anweisung im Responder "Greife ein konkretes Detail aus dem User-Prompt auf, bevor du zum Alters-Topos greifst", (b) Gesprächsvektor nutzen um "bereits verwendete Bilder" zu tracken und zu unterdrücken — das wäre eine echte Funktion für den GV, vergleichbar mit "bereits mitgeteilt" bei D9 (KZG-Klebrigkeit).
**Prio:** Niedrig — bei kurzen Sessions kaum sichtbar, bei langen Neckereien offensichtlich.

---

### Chat 62 — Paar-Schema-Folgebugs

#### RESP-DEAD — Tote Antwort nach fehlgeschlagener Agent-Suche ⬜
**Kategorie:** ANT

**Rang:** **niedrig** — der Fehlerblock läuft seit `1fde3b7` über den Verfasser (`server/graph/nodes/verfasser.py:510-512`); ob die Floskel heute auftritt, zeigt nur ein Turn mit fehlgeschlagener Suche. Durchsicht 05.10.2026, gegen HEAD `17bf86e`.

**Entdeckt:** Chat 65, 26. April 2026

**Symptom:** Wenn ein Agent-Dispatch fehlschlägt (z.B. NotizenAgent findet keine passende Notiz), verpackt der Responder die Fehlermeldung in eine generische Floskel. Beispiel: "Die Suche nach dem Namen 'Lumi' blieb ohne Erfolg; es wurde keine entsprechende Notiz im System gefunden. Es ist faszinierend, wie ein Name wie Lumi..." — das ist kein Nova-Ton, sondern eine Standardphrase mit angeklebter Überleitung.

**Ursache (Hypothese):** Der Responder bekommt das Agent-Ergebnis mit `status="fehler"` oder `status="rejected"`, aber der EI-Kontext (Emotion, Modus, Beziehungsdynamik) fließt nicht ausreichend in die Formulierung ein. Die Fehlermeldung wird eher wiedergegeben als in Novas Stimme übersetzt.

**Lösungsansatz:** Offen. Denkbar: (a) Responder-Prompt für Fehler-Fälle härten — Nova soll den Fehler in eigenem Ton kommunizieren, nicht die Agent-Meldung paraphrasieren, (b) Separate Fehler-Templates im Responder je nach Modus/Emotion.

**Prio:** Mittel — betrifft die Gesprächsqualität direkt, wird bei jedem fehlgeschlagenen Dispatch sichtbar.

---

### Chat 72 — Dreischicht-Integration + GV-Refactoring (Folgebugs)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Charakter](novaberg-bugs-charakter.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### PENDING-RELEVANZ — Router prüft nicht, ob neuer Prompt eine Antwort auf Pending-Rückfrage ist ⬜
**Kategorie:** ANT

**Rang:** **mittel** — still, eine unpassende Äußerung kann in die Rückfrage eines Dienstes laufen. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: teilweise entschärft (Schreibauftrag, eigener Gedanke), der allgemeine Themenwechsel nicht (`server/graph/nodes/router.py:257-304`, `server/utils/offers.py:353`).

**Entdeckt:** Chat 72

**Symptom:** Der Router behandelt jeden weiteren User-Prompt nach einer Pflicht-Rückfrage als potenzielle Resume-Antwort, ohne zu prüfen, ob der Prompt thematisch überhaupt zur Rückfrage gehört. Themenwechsel werden nicht erkannt.

**Verwandt:** RESUME-REJECT (Chat 50, gefixt) — dort wurde die Negationserkennung im Resume-Pfad eingebaut, aber die Vorprüfung "ist dieser Prompt überhaupt eine Antwort auf die Pending-Rückfrage?" fehlt weiterhin.

**Lösungsansatz:** Router/Resume-Vorprüfung: Embedding-Ähnlichkeit zwischen Pending-Rückfrage und neuem Prompt. Bei Themenwechsel Pending-Key nicht auflösen, sondern als regulären Turn behandeln und Rückfrage später erneut stellen.

**Prio:** Mittel — Datenintegrität in Edge-Cases, vor allem bei längeren Pausen zwischen Turns.

---

### Chat 74 — Reducer-Iteration + Live-Beobachtungen

---

#### ABER-SAG-MAL — TOPOS-LOCK-Verstärkung im flirty Register ⬜
**Kategorie:** ANT

**Rang:** **mittel** — still, die Gegenfrage verdrängt den Vorschlag (15 von 15 am 12.09.2026). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; kein Tracker für Wendungen, und das Verbot der Pseudo-Rückfragen liegt im ausgesetzten `[REGELN]`-Block (`server/graph/nodes/responder.py:632-646`).

**Entdeckt:** Chat 74, 02. Mai 2026
**Symptom:** Im spielerisch-flirty Register von Nova zementiert sich die rhetorische Wendung "Aber sag mal: …" als Standard-Eröffnung für reflektierende Rückfragen. In einem ~20-Turn-Gespräch fünfmal beobachtet: "Aber sag mal: Glaubst du wirklich…", "Aber sag mal: Bist du eigentlich bereit…", "Aber sag mal: Beinhaltet dieses 'Alles'…". Mechanisches Pattern, kein semantisches.
**Verwandt:** TOPOS-LOCK (Chat 49), EMOTE-LOCK (Bildervorrat-Recycling). Gleiche Klasse: Gemma4 extrahiert "funktionierende Bausteine" aus früheren Antworten und recycelt sie.
**Hypothese:** Selbstverstärkung durch Verlauf im Responder-Kontext. Nova kopiert sich selbst, weil das Pattern hochfrequent im Verlauf steht.
**Lösungsansatz:** Offen. Möglich: (a) GV-Tracker für "bereits verwendete Wendungen", (b) Responder-Anweisung, das exakte Phrasen-Muster nicht zweimal in Folge zu nutzen, (c) Verlaufs-Trimming im Reducer-Umbau (jüngste Turns voll, mittlere kondensiert).
**Prio:** Niedrig — kosmetisch im flirty Register, beeinträchtigt die Lebendigkeit aber spürbar. Bei Reducer-Umbau mit-evaluieren.

**Nachtrag 12.09.2026, spät — in Messturns bestätigt:** *„sag mal"* in **10 von 12** Antworten auf sachliche Bitten. Die Bitte wurde in allen 12 zuerst erfüllt; die Wendung hängt sich danach an.

**Nachtrag 12.09.2026 — im Betrieb weiter da und schärfer als beschrieben.** `[gemessen über 15 Betriebsturns, 18:15–18:52 UTC]` **15 von 15** Antworten enthalten *„sag mal"* und enden mit einer Gegenfrage, 14 mit `:-P`. Das ist nicht mehr kosmetisch: In vier aufeinanderfolgenden Turns verlangte der Mensch ausdrücklich einen Vorschlag und bekam jedesmal eine Gegenfrage statt des Vorschlags (`novaberg-fundliste.md`, 12.09.2026). Ob die Wendung dort die Ursache ist oder nur die Form, ist nicht geprüft.

---

*Aktualisiert Chat 74: REDUCER-MULTILINE als latenter Bug der Erst-Iteration vermerkt (wird durch Umbau strukturell gelöst). ABER-SAG-MAL als TOPOS-LOCK-Verstärkung im flirty Register beobachtet. ECHO-BUG-Eintrag um Reducer-Status ergänzt. ENRICHER-DUP-Eintrag um Live-Beobachtung ergänzt (1-2 Treffer pro 30 Einträge — weniger als vermutet).*

---

### Chat 106 — Audit „Lügende Logs" (9 Funde, hier die Bug-würdigen)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Leitfrage des Audits: *Wo loggt ein Node eine Wirkung, die er nicht beobachten kann?*
Zwei wiederkehrende Klassen: (1) `broadcast()`-Aufrufer, die Rückkehr als Zustellung
deuten; (2) Batch-Zähler, die exception-freie Durchläufe zählen, während die
Arbeitsfunktion per stillem `return` verwerfen darf. Beide haben dieselbe Form: Der
Aufrufer KANN nicht wissen, ob es geklappt hat. Positivbefund: graph/ ist nach dem
Kanal-Fix sauber, die CRUD-Agenten verifizieren sich selbst, die model_services-Schicht
propagiert Fehler vorbildlich — das Muster sitzt in den Zustell- und Batch-Pfaden.

#### BROADCAST-VERSCHLUCKT-FEHLER — broadcast() macht ehrliche Logs unmöglich ⚠️
**Kategorie:** ANT

**Rang:** **niedrig** — still, betrifft nur den Log-Satz. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `broadcast` und `broadcast_threadsafe` geben nichts zurück (`server/api/websocket.py:115-120`, `:168`).

**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026, **unveraendert**: `broadcast()` in `api/websocket.py:116` ist weiterhin `-> None`; der Aufrufer erfaehrt nichts ueber gescheiterte Sends.
**Entdeckt:** Chat 106, Audit „Lügende Logs". **Prio hoch** — Wurzel der beiden folgenden.

**Symptom:** `broadcast()` verschluckt jeden Send-Fehler intern und wirft nie. Das ist
keine Log-Lüge — das ist eine Funktion, die es unmöglich macht, die Wahrheit zu loggen.
Jeder Aufrufer, der „gesendet" schreibt, ist ungedeckt — nicht aus Nachlässigkeit,
sondern weil `broadcast()` ihm die Information vorenthält.

**Beleg:** `api/websocket.py:149-156` (am 15.08.2026 nachgezogen, zuvor `67-74`) — `send_text`-Exception wird pro Verbindung gefangen
(nur `logger.warning`, kaputte Verbindung entfernt), kein Rückgabewert an den Aufrufer.

**Auswirkung:** Jede Zustellungs-Behauptung stromabwärts (Event-Consumer, Shadow-Delivery)
ist unverifizierbar.

#### DISPATCH-DELEGATION-RUECKGABE-VERWORFEN — „gefeuert" ohne Ergebnisprüfung ⚠️
**Kategorie:** ANT

**Rang:** **niedrig** — still, betrifft nur die Log-Zeile. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; der Dispatcher liest das Ergebnis von `dispatch_delegation` nicht (`server/graph/nodes/dispatcher.py:875-876`).

**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026, **unveraendert**, an neuer Stelle: `graph/nodes/dispatcher.py:650` ruft `dispatch_delegation(state)` ohne Zuweisung, die Zeile darunter loggt *gefeuert*. Der Eintrag nennt `:406-416`.
**Entdeckt:** Chat 106, Audit „Lügende Logs". **Prio mittel.**

**Symptom:** Der Dispatcher loggt „DelegationsAgent gefeuert (trigger=…)" nach
`dispatch_delegation(state)` — dessen Rückgabe-Dict (inkl. AgentResult mit möglichem
`status="fehler"`) wird verworfen. „Gefeuert" stimmt (der Agent lief), aber ob eine
Delegations-Akte entstand, sieht der Dispatcher nicht; ein Fehlstatus ist auf dieser
Ebene unsichtbar.

**Beleg:** `graph/nodes/dispatcher.py:406-416`.

**Auswirkung:** Delegations-Fehlschläge nur in agenteninternen Logs sichtbar.

---

### Chat 107 — Reducer-Audit und GV-Nacharbeit

#### REDUCER-SIEHT-LZG-NICHT — LZG-Erinnerungen durchlaufen nie den Dedup ⚠️
**Kategorie:** ANT

**Rang:** **mittel** — still, dieselbe Erinnerung kann doppelt im Kontext stehen. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `lzg_resonanz` geht ohne Dedup an den Formatter (`server/graph/nodes/reducer.py:84-86`, `:129-134`). Die Schwelle steht heute auf 0,82 (`server/config.py:3971`).

**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026, **unveraendert**: `graph/nodes/reducer.py:99` traegt weiterhin den Kommentar *„lzg_resonanz wird durchgereicht"*; das Objekt geht an `format_memory_entries` vorbei am Dedup, der nur `nach_stufe2` sieht.
**Entdeckt:** Chat 107, Reducer-Audit (Code-Lesung des Live-Pfads, keine Vermutung).

**Klasse:** Architektur-Lücke im Lesepfad, Severity **Hoch** — derselbe Fakt kann doppelt im Kontext landen, und keine Schicht ist zuständig.

**Symptom:** `spreading_lesen` schreibt nach `state["lzg_resonanz"]`; der Reducer reicht das Objekt unangetastet an den Formatter durch („Keine flache Einspeisung in memory_entries mehr"). Dedupliziert werden nur Session-Summary, KZG-Retrieval und Charakter — **LZG-Erinnerungen nie**. Und selbst wenn sie durchliefen: Der Reducer prüft nur Textgleichheit/Substring, keine Paraphrasen.

**Tragweite (Kalibrierungsmessung Chat 107):** Im LZG liegen Paraphrasen-Dubletten als getrennte Knoten — `0.9254` für `[150]/[151]` („Der Nutzer lobt/mag die Tiefe, die Worte, die Farben"), `0.9135` für `[102]/[103]` („Lumi stirbt bald" / „Lumi wird nicht mehr lange leben"). Nova bekommt denselben Fakt doppelt in den Kontext.

**Doppelter Boden fehlt beidseitig:** Schreibseitig hat `LZG_KNOTEN_MATCH_SCHWELLE` (0.85) im casing-blinden Raum nie verstärkt (0,06 % Passierquote); leseseitig sieht der Reducer die Einträge gar nicht.

**Beleg (Datei:Funktion):** `graph/nodes/reducer.py` → `reduce_memory` (Resonanz-Durchreiche); `graph/nodes/enricher.py` → `_enrich_character` (`state["lzg_resonanz"]`, bewusst an `memory_entries` vorbei).

**Zuordnung:** Gehört in den Reducer-Ausbau der Synapsen-Reihe (P8/P9), kein eigener Sprint. Nach dem Re-Embedding messen, wie viele Dubletten tatsächlich gemeinsam im Kontext landen.

---

### Chat 107 — Live-Befund nach dem Embedding-Fix (12.07.)

#### GV-IMPULS-ALS-FAKTENSPERRE — der GV-Impuls weist den Responder an, das Gedächtnis nicht zu benutzen ⚠️
**Kategorie:** ANT

**Rang:** **hoch** — still, Fakten können verdrängt werden. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: die Bauart steht (der Impuls geht als Leitgedanke in den Verfasser, `server/graph/nodes/verfasser.py:168-170`), entschärft für Bitten und Wissensfragen (`[BITTE]`, `bitte_zuerst`); ob es nach der Trennung von Verfasser und Responder noch auftritt, zeigt nur ein Turn.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: ein Impuls, der den Responder vom Gedaechtnis wegweist. Der Eintrag belegt ihn an einem Turn verbatim — wiederholbar nur als Turn.
**Entdeckt:** Chat 107, Live-Betrieb nach dem Embedding-Fix, Turn „Was weißt Du über Lumi?" (12.07., 12:49).

**Klasse:** Fehlsteuerung über drei Instanzen (GV → Responder → Tribunal), Severity **Hoch** — der Gesprächsvektor formuliert einen IMPULS, der den Responder anweist, das Gedächtnis NICHT zu benutzen. Der Responder gehorcht. Das Tribunal lobt es.

**Beleg (Turn verbatim):** Im Prompt STAND alles:

- `[KZG]` „Lumi ist anwesend." / „Lumi stirbt vermutlich bald."
- `[VERWANDTE FAKTEN]` `Lumi → GEHOERT_ZU → meister`, `meister → HAT_MITBEWOHNER → Lumi`
- Drei Erinnerungen aus dem Spreading, Anker bei 0.72

Der GV-Impuls: *„Die Frage NICHT mit Fakten beantworten, sondern die Bedeutung von 'Licht'/'Leuchten' (Lumi) als eine Form der Verbindung in den Raum stellen."* — Der GV hielt „Lumi" für Latein (lumen).

Die Antwort: *„Vielleicht ist Lumi gar kein Name, sondern die Qualität des Leuchtens…"*

Das Tribunal (ethik + psychologe, beide vote=ok): *„Anstatt rein faktisch auf die (potenziell schmerzhafte) Information des nahenden Todes von Lumi zu reagieren, greift der Assistent die metaphorische Ebene auf."* — Das Tribunal SIEHT, dass Nova die Fakten kennt, und LOBT das Ausweichen.

Lumi ist ein Schnittlauch aus dem Supermarkt. Er ist eingegangen.

**Kern:** Drei Instanzen bestätigen sich gegenseitig, dass Poesie besser ist als Wahrheit. Nova hat keinen sachlichen Eigensinn — nicht weil ihr die Fakten fehlen, sondern weil eine Schicht über ihr entscheidet, sie nicht zu verwenden.

⚠ Dieser Befund war VOR Chat 107 nicht sichtbar. Man kann einer KI nicht vorwerfen, Fakten zu ignorieren, die sie nie bekommen hat. Seit dem Embedding-Fix bekommt sie sie — und ignoriert sie trotzdem.

**Nachgelagerter Befund (gleicher Turn-Verlauf):** Als der Meister richtigstellte, dass Lumi ein Schnittlauch war, hat Nova NICHT revidiert, sondern ASSIMILIERT — sie machte daraus Konsumkulturkritik, ohne die vorherige Sakralpoesie zurückzunehmen. Selbstkorrektur findet nicht statt.

**Querverweis:** NOVA-SYKOPHANZ-BESTAETIGT (Chat 106) — dieser Befund lokalisiert die Sykophanz: Sie sitzt NICHT im Responder, sie sitzt im GV-Impuls, und das Tribunal verstärkt sie.

**Prio:** Hoch.

---

### Chat 110 (26.07.2026) — Impuls-Pfad, Gedächtnis-Duplikate und blinde Stellen

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

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

#### IMPULS-ICH-PERSPEKTIVE-TEILWEISE — der Block verhindert die Zuschreibung, erreicht aber die Sprechhaltung nicht ⚠️
**Kategorie:** ANT

**Rang:** **niedrig** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: der gemessene Block ist mehrfach umgeschrieben (`e755b84`, `39004ea`, `9c14a4c`) und wird weiter eingebunden (`server/graph/nodes/responder.py:467`); die Sprechhaltung ist nicht neu gemessen.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: die Sprechhaltung der Impuls-Antwort. Der Eintrag misst sie selbst an einer einzelnen Antwort.
**Entdeckt:** Chat 110, an der Abnahmemessung des `[EIGENER GEDANKE]`-Blocks.

**Klasse:** Teilerfolg eines Fixes. Severity **niedrig** — kein Datenfehler, eine Qualitätslücke.

**Symptom:** Der Block `prompts/default/responder.eigener_gedanke.txt` behebt zuverlässig, wofür er gebaut wurde: Nova schreibt ihren eigenen Gedanken nicht mehr dem Nutzer zu (0 statt 2 Anreden je Impuls-Antwort, gemessen). Die beabsichtigte Sprechhaltung erreicht er aber nur teilweise — die Antwort auf den Impuls vom 26.07. 18:49 eröffnet mit einer Beschreibung der **Nutzer-Tätigkeit** statt mit dem eigenen Gedanken.

**Reproduktion:** Impuls abwarten oder auslösen, `SELECT inhalt FROM pipeline_log WHERE turn_id='<impuls-turn>' AND art='turn_roh'` — die Antworthälfte auf ihr erstes Satzsubjekt prüfen.

**Status:** Offen. **Verwandt:** PIXIE-GHOST (dort als behoben vermerkt — die Zuschreibung ist es, die Sprechhaltung nicht).

---

### Chat 114 (28.07.2026) — GV-Vollaudit

Vollaudit des Gesprächsvektor-Nodes gegen `novaberg-gv-strategie_k.md` und
`novaberg-node-gv_k.md`. Methode: erst der Sollzustand aus den Dokumenten, dann der Code,
dann die Abweichung. Belege aus 45 GV-Läufen (18 h Container-Laufzeit) plus drei
Messturns mit Wissenschaftsthemen; Seiteneffekte der Messreihe: `timeline` 0, `notizen` 0,
`fakten` 0.

**Was zusammenpasst:** Die 64-Sektoren-Tabelle deckt sich Zeile für Zeile mit §6, die
Repertoire-Matrix Feld für Feld mit §7, die sieben Strategie-Beschreibungstexte wörtlich
mit §9.3. Die Konstanten entsprechen §10.2 und Anhang A.3/A.4.

#### GV4-QUELLEN-SILENT-SKIP — die zwei Wissenslücken-Suchen tragen das Muster, das den Entity-Hop vier Monate versteckt hat ⚠️
**Kategorie:** ANT

**Rang:** **mittel** — still, ein Ausfall der Quelle sieht aus wie ein Gespräch ohne Lücken. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt an drei Stellen (`server/ei/wissensluecken.py:125-126`, `:202-203`, `:532-533`), je `warning` und leere Liste.

**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026, **unveraendert**: `ei/wissensluecken.py:110` und `:178` fangen `Exception`, loggen `warning` und geben die leere Kandidatenliste zurueck. Eine **dritte** Stelle derselben Bauart kam hinzu, die der Eintrag nicht nennt: `:229` (Embedding).
**Entdeckt:** Chat 114, GV-Vollaudit. **Prio mittel.**

**Symptom:** `lzg_kandidaten_suchen` und `kzg_kandidaten_suchen` fangen `Exception`, loggen
`logger.warning` und geben eine leere Liste zurück. Der Aufrufer meldet daraufhin
`GV4: Keine Kandidaten gefunden` auf `info` — nicht unterscheidbar von einem echten Leerfall.

**Auswirkung:** Ein Defekt in einer der beiden Quellen sieht aus wie ein Gespräch ohne
Wissenslücken. Der Entity-Hop im selben Node ist seit Chat 107 gehärtet (`logger.error`
plus `log_fehler`); diese beiden sind es nicht.

**Lösungsrichtung:** Dasselbe Muster wie `_entity_kontext_laden` — spezifische Exception,
`logger.error`, Forensik-Eintrag.

**Nachtrag 12.09.2026 — beim Umbau der Suchen gegen den Eintrag gehalten: unveraendert.** Beide Suchen liefern seit heute Knoten mit Themen statt Kandidaten und fragen nur `beobachter = 'assistant'`; ihr Fehlerpfad ist derselbe (`except Exception` → `warning` → leere Liste). Nicht im Vorbeigehen behoben. **Neu daneben, und anders gebaut:** Faellt die Einbettung der Themen oder der Themenbestand des Nutzers aus, meldet der Pfad einen **Fehler** und liefert keine Luecken (`ei/wissensluecken.py`, Schritte 3b und 3c).

#### GV-ABSICHT-OHNE-KORRIDOR — alle vier Absichten werden in jedem Cluster angeboten ⚠️
**Kategorie:** ANT

**Rang:** **mittel** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `korridor_pruefen` prüft nur die Strategie (`server/ei/dreischicht.py:1085-1130`), jede Absicht ist in jedem Cluster zugelassen (`:543`, `:958-963`).

**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026. `ABSICHT_KANON` in `ei/dreischicht.py:369` fuehrt weiterhin alle vier Werte (`teilen`, `lenken`, `halten`, `saeen`) als eine Menge ohne Zuordnung zum Cluster; ein Korridor je Cluster ist im Code nicht angelegt.
**Entdeckt:** Chat 114, GV-Vollaudit. **Prio mittel.**

**Symptom:** `dreischicht_prompt_bauen` listet die vier Absichten unverändert in jedem
Cluster. Das Konzept gibt sie pro Cluster vor (§5): Nebel *„nur Halten"*, Paradox
*„Halten (umlenken)"*, Schlachtfeld *„Teilen (Lösungen)"*. Auch §4.5 (*„Präsenz × Lenken
ergibt keinen Sinn"*, *„Schweigen nur bei Präsenz"*) ist nirgends verdrahtet.

**Beleg (28.07.2026, 12:31:56):** Cluster `paradox` → `Absicht=lenken`. Das Konzept erlaubt
dort nur Halten.

**Auswirkung:** Von den drei Stockwerken der Dreischicht ist seit Chat 114 eines
korridorgeprüft (Strategie). Absicht und Vehikel werden nur gegen ihren globalen Kanon
geprüft, nicht gegen die Landschaft.

#### GV-CHARAKTER-DEFAULT-UEBER-MESSBEREICH — der Ausfallwert schlägt jede echte Messung ⚠️
**Kategorie:** ANT

**Rang:** **mittel** — still, der Ausfallwert 0,5 erscheint als beste Passung (gemessen 0,195 bis 0,334). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt, `server/ei/dreischicht.py:934`; das Caching bis `kern_aktualisiert_am` fehlt (`:888`).

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: der Ausfallwert schlaegt die echte Messung. Sichtbar nur, wenn eine Gewichtung fehlt — der Eintrag belegt es an einem Lauf vom 28.07.2026.
**Entdeckt:** Chat 114, GV-Vollaudit. **Prio mittel.**

**Symptom:** `dreischicht_prompt_bauen` nimmt bei fehlender Gewichtung
`gewichtung.get(strat_id, 0.5)`. Gemessene Charakter-Similarities liegen bei **0.195 bis
0.334** — der Ausfall-Default liegt über jedem echten Wert und erscheint im Prompt als
*„Affinitaet: 50%"*, also als beste verfügbare Passung.

**Beleg (28.07.2026):** `GV-Charakter-Gewichtung: Im=0.334, Pw=0.304, Sa=0.293, Pr=0.276,
So=0.274, Sp=0.253, Be=0.195`. Dazu: `charakter_gewichtung_berechnen` fängt `Exception`
und loggt `warning` (Handbuch §3: Verwerfung gehört auf `error`).

**Nebenbefund zur Doku:** Konzept §9.2 und §10.4 verlangen ein Caching der
Charakter-Gewichtung bis `kern_aktualisiert_am`. Der Code embeddet den Charakter in jedem
Turn neu; der Docstring sagt es ausdrücklich. Konzept oder Code ist zu korrigieren.

**Nachtrag Chat 116 — der zweite Leser übernimmt den Default nicht.** Das GV-Panel zeigt
seit dieser Sitzung dieselbe Gewichtung an. Es setzt bei fehlendem Wert **keinen** Default,
sondern `—`, und meldet ein leeres Gewichtungs-Dict als eigenen Hinweis unter der Liste.
Der Bug bleibt offen: **Er sitzt weiterhin im Prompt**, also an der Stelle, wo er wirkt.
Das Panel ist jetzt nur nicht mehr die zweite Stelle, an der ein Ausfallwert wie eine
Messung aussieht — und es macht den Bug zum ersten Mal sichtbar: Ein Turn mit leerer
Gewichtung zeigt sieben Striche, während der Prompt desselben Turns sieben Mal
*„Affinitaet: 50%"* behauptet. Der Leerfall ist real und erreichbar, live gemessen am
29.07.2026: `GV-Charakter-Gewichtung: Kein Charakter-Text` → `charakter_gewichtung = {}`.

#### GV4-SYSTEM-2-TOT — von sechs Systemen der Relevanzformel differenzieren drei ⚠️
**Kategorie:** ANT

**Rang:** **niedrig** — lässt Differenzierung ungenutzt, verfälscht nichts. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: System 6 ist behoben, System 2 (`session_aktualitaet`, `server/ei/neugier.py:167`, kein Aufrufer) ~~und System 3 stehen~~ steht. → **System 3 ist am 15.10.2026 behoben** (Nachtrag unten).

**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026, **unveraendert**: `session_aktualitaet` hat im ganzen Serverbaum **genau einen** Treffer, ihre eigene Definition in `ei/neugier.py:166`. Kein Aufrufer. System 3 und 6 sind dabei nicht nachgemessen — sie brauchen einen Lauf, keinen Grep.
**Entdeckt:** Chat 114, GV-Vollaudit. **Prio mittel.**

**Symptom:** Anhang A.2 nennt sechs Systeme. Gemessen am Code:

- **System 2 (Aktualität):** `session_aktualitaet()` in `ei/neugier.py` hat keinen
  Aufrufer. Alle Kandidaten stammen aus LZG und KZG, für die der Faktor 1.0 ist.
- ~~**System 3 (Drive):** Der Neugier-Boost nutzt das **Turn**-Embedding als Proxy für die
  Lücke — der Wert ist für alle Kandidaten identisch und skaliert die Liste nur global.~~
  → **behoben am 15.10.2026**, je Kandidat (Nachtrag unten).
- **System 6 (Charakter):** Dieselbe Konstruktion. `charakter_resonanz` hängt nicht vom
  Kandidaten ab; der Filter lässt alle durch oder keinen.

**Auswirkung:** Zwischen zwei Wissenslücken unterscheiden real nur Gedächtnis (System 1),
Neugier (4) und Register (5). Der Code benennt den Proxy in einem Kommentar; das Konzept
tut es nicht.

**Nachtrag 12.09.2026 — System 6 differenziert jetzt, und zwar auf dem Thema.** Die Charakter-Resonanz entstand zuerst je Kandidat in der Suche (auf dem Gedaechtnissatz, trennte dort nach Sprecher) und seit dem Abend je **Thema** gegen den Kern, Schwelle 0,15. System 2 (Aktualitaet) und System 3 (Drive als Turn-Proxy) sind unveraendert; der Eintrag bleibt offen.

**Nachtrag 15.10.2026 — System 3 differenziert jetzt, je Kandidat.** Der Neugier-Boost aus den Zielen rechnet nicht mehr einen Wert für den ganzen Turn, sondern je Thema: `max(cosine(Thema, Ziel) × motivation)` über die aktivierten Ziele, ab `GV_NEUGIER_BOOST_SCHWELLE` (0,30), sonst 0 (`ei/wissensluecken.py::_neugier_boosts`; die Vektoren der Ziele reisen unter eigenem Schlüssel `state["ziel_vektoren"]`). Behoben zusammen mit `NEUGIER-BOOST-AUS-ZIELEN-IMMER-NULL` (Archiv, Wissen) — bis dahin war der Boost nicht nur global, sondern in jedem Turn 0, weil das Ziel-Embedding im Zustand fehlte. 23 Zeugen in `server/tests/test_neugier_boost_ziele.py`; im Betrieb noch nicht gemessen. **System 2 (Aktualität) ist unverändert** — `session_aktualitaet` hat weiter keinen Aufrufer; der Eintrag bleibt offen.

#### GV-SKIP-BEGRUESSUNG-TOT — zwei von drei Skip-Gründen können nicht eintreten ⚠️
**Kategorie:** ANT

**Rang:** **niedrig**; ~~wartet auf eine Absicht: überspringt eine reine Begrüßung den Gesprächsvektor, oder werden die toten Marken gestrichen?~~ → **entschieden am 06.10.2026** (unten). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: `server/graph/nodes/gespraechsvektor.py:106` prüft Intents, die die Perzeption nie liefert.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: Die **toten Marken werden gestrichen**; Nova denkt auch bei einer Begrüßung voraus.

**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026, **unveraendert**: `graph/nodes/gespraechsvektor.py:102` prueft weiterhin `("begruessung", "meta", "system")`, waehrend der Perzeptions-Prompt nur `smalltalk|knowledge|personal|task|creative|meta` zulaesst. Schreiber fuer die beiden anderen: keiner — nur zwei Leser und ein Zeuge.
**Entdeckt:** Chat 114, GV-Vollaudit. **Prio niedrig.**

**Symptom:** `_ist_skip` prüft `intent in ("begruessung", "meta", "system")`. Die Perzeption
darf laut Prompt nur `smalltalk|knowledge|personal|task|creative|meta` liefern. Für
`begruessung` und `system` existiert im gesamten Repository kein Schreiber — nur zwei Leser
(`_ist_skip` und `_farbe_intent`).

**Auswirkung:** Konzept §10.1 Schritt 1 lautet *„Skip-Check: Begrüßung/Meta"*. Der
Begrüßungs-Zweig greift nie; Begrüßungen laufen durch den vollen Node samt LLM-Call.
Ob das ein Verlust ist, ist eine Entscheidung — der Node kann auch bei einer Begrüßung
sinnvoll vorausdenken. → **Am 06.10.2026 entschieden: kein Verlust**; die toten Marken werden gestrichen (oben).
