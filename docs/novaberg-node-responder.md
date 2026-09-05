# Novaberg — Node: Responder

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz Responder
**Stand:** 5. September 2026, 20:28 UTC (die **Zeichenspanne** der Regie wird nicht von jedem Modell befolgt — 996 statt 175 Zeichen beim Fernmodell; ein Override auf der Prompt-Modellebene formuliert sie in Saetzen und ist als Provisorium vermerkt). Davor 17. August 2026 (Ortszeit und deutscher Wochentag im Szenenblock)
**Pfad:** novaberg/docs/novaberg-node-responder.md
**Quellen:** nova-01-m-e.md, nova-12-k.md §7
**Datei:** `graph/nodes/responder.py`

---

## 1. Aufgabe

Der Responder generiert Novas Antwort. Er ist der einzige Node, der alles sieht — Gedächtnis-Kontext, emotionale Intelligenz, Management-Ergebnisse, Session-Historie — und daraus eine natürliche Antwort formuliert. Er ist bewusst der Node mit dem breitesten Input, weil Generierung (anders als Bewertung) den vollen Kontext braucht.

---

## 2. Position im Graph

```
Enricher → EI-Calc → Router → [Planner] → GV-Node → ▶ Responder ◀ → Thinker → Tribunal → ...
```

Nur im CharacterGraph (Pfad 2). Seit Chat 60 nicht mehr im HumanGraph.

---

## 3. System-Prompt-Aufbau

**Seit dem 13.08.2026 ist der Prompt ein Drehbuch und kein Lagebericht.** Der Umbau folgt einer Messung: Dieselbe Vorgabe traf als **Aufgabe** 6 von 6 Längenkorridore und als **Beschreibung** 0 von 6 (`novaberg-haltungsraum_k.md` §3.0). Der Grund ist strukturell — eine Beschreibung ist Information, erst ein Auftrag macht daraus etwas zu Erfüllendes. Das Modell ist nicht Nova; es kann sie spielen, wenn die Szene spielbar geschrieben ist.

### 3.1 Die Blockfolge

```
── System ────────────────────────────────────────────────────────────
[ROLLE]                       Konstellation · doppelte Prüfbedingung
[SZENE]                       Landschaft · Sektor · Achsen · Farbton · Zeit
[PERSON A — WER SIE IST]      Kern · Adaptiv · Emotionen · Intentionen
[PERSON A — IHRE EMOTION]     Verlauf · Vektor · Konflikt
[PERSON B — WER ER IST]       sein Kern · was ihn beschäftigt
[ZWISCHEN BEIDEN]             beide Blickrichtungen, beschriftet
[EIGENER GEDANKE]             bedingt, bei eigenem Impuls
[AUFGABE]                     fertiger Block des Planners
[PERSON B — WIE ER GERADE DA IST]   Emotion · Vektor · Register · Stil · Wille
[INHALT]                      der Text des Verfassers
[DIREKTIVEN]                  absolute Vorgaben des Nutzers
[PERSON A — IHR WESEN]        Charakter-Anweisung, zuletzt
── Nutzer ────────────────────────────────────────────────────────────
[GESPRAECHSVERLAUF] · [AKTUELLER PROMPT]
[REGIE FUER DIESE REPLIK]     Werkzeug · Umfang in Zeichen · Haltung · Energie · EI-Mikro
```

**Die Ordnung folgt zwei Befunden.** Vom Groben ins Feine, damit beim Lesen jeder Zeile klar ist, aus wessen Sicht sie geschrieben ist. Und die bindende Vorgabe zuletzt, weil Modelle Anfang und Ende eines langen Prompts stärker gewichten als die Mitte — die Profile dürfen dort liegen, die Zahl nicht.

### 3.2 Eine Anrede, eine Bedeutung

**»Du« ist der Schauspieler.** Über Person A wird in der dritten Person gesprochen; das »du« **innerhalb** der wörtlichen Rede meint Person B und bleibt.

Vor dem 13.08.2026 mischte der Prompt alle drei Bedeutungen: In sieben von dreizehn Blöcken wurde geduzt, und »du« meinte mal den Spieler, mal die Rolle, mal das Gegenüber. Ein Modell musste bei jedem Block neu raten, wer gemeint ist — im `[INHALT]`-Block wechselte die Bedeutung sogar innerhalb des Blocks.

### 3.3 Was jeder Block trägt

**`[ROLLE]`** führt beide Personen ein und nennt zwei Bedingungen: Die Replik muss erkennbar von Person A stammen **und** erkennbar für Person B gemacht sein. Ohne diese Einführung stünden die Personenblöcke ohne Grund da — und ein Block, den der Auftrag nicht einführt, ist Kontext, der nicht bindet. Der Name ist nicht `[AUFGABE]`, weil den bereits der fertige Block des Planners trägt.

**`[SZENE]`** trägt dieselbe Lage in drei Körnungen (Landschaft, Sektor, sechs Achsen — darunter die Initiative) und **den Farbton**, der den Responder bis dahin nie erreichte. Eine Wirkung des Farbtons ist nicht nachgewiesen; er steht dort, weil er die Lage beschreibt.

**`[PERSON B — WER ER IST]`** trägt den Kern des Menschen. Bis zum 13.08.2026 erreichte vom Nutzer ein einziges Profil den Prompt — sein Beziehungsprofil, auf 300 Zeichen gekappt —, während von Nova alle fünf hineingingen.

**`[ZWISCHEN BEIDEN]`** beschriftet beide Richtungen. Nach dem Paar-Schema sind `(nova, mensch)` und `(mensch, nova)` verschiedene Aussagen; unbeschriftet nebeneinander sahen sie aus wie zwei Fassungen derselben.

**`[INHALT]`** trägt den Text des Verfassers — **seit dem 14.08.2026 in dritter Person**. Der Verfasser notiert, was Person A feststellt, offen lässt und zurückfragt; er schreibt ihre Rede nicht mehr selbst. Der Block sagt deshalb ausdrücklich an, daraus Rede zu machen: dieselben Aussagen, ihre Stimme, keine Aussage dazu, die dort nicht steht.

Die Anweisung darf nicht fehlen. Ohne sie entschiede der Vorgabewert, und der naheliegende wäre, die Notiz durchzureichen — genau das ist am 31.07.2026 einmal passiert, damals mit dem Hypothesentext des Hintergrundagenten. Die Umwandlung ist keine Inhaltsänderung: Verboten ist dem Responder, eine Behauptung **hinzuzufügen**; die Form war immer seine.

**`[REGIE FUER DIESE REPLIK]`** ist der einzige anweisende Block: Werkzeug und Vehikel aus dem GV-Knoten, der Umfang als **Zeichenspanne**, die abweichenden Haltungswörter, der Energiesatz und die EI-Mikroanweisung. Er steht am Ende der Nutzer-Nachricht.

> **Die Zeichenspanne wird nicht von jedem Modell befolgt** — gemessen am 05.09.2026. Die
> Regie forderte 60–175 Zeichen; das lokale Modell lieferte 226 im Median, das Fernmodell
> **996**, also das 5,7-fache der Obergrenze. **Ein Prompt, der in Zeichen rechnet,
> verlangt eine Zählung über die eigene Ausgabe, die ein Sprachmodell beim Erzeugen nicht
> hat.** In Sätzen und Absätzen formuliert greift dieselbe Vorgabe (168 und 258 Zeichen).
>
> Abgeholfen ist über die **Prompt-Modellebene**: `prompts/deepseek_deepseek-v4-flash-0731/`
> trägt einen eigenen `responder.rules`-Block mit einer Vorgabe in Sätzen. **Das ist
> ausdrücklich ein zweiter Weg neben der Regie** — der Kommentar an der Regie sagt, die
> alte Längenregel sei entfernt worden, damit es keinen gibt. Solange beide dasselbe wollen,
> stört das nicht; sobald der Faszinations-Leser den Korridor weitet, würde der Block ihn
> deckeln. Er ist als Provisorium vermerkt
> (`novaberg-thinking-faszination_k.md` §11a).
>
> **Der Befund darüber hinaus:** Der Fehler war unsichtbar, solange ein Modell zufällig
> nahe lag. Ein Modellwechsel ist deshalb auch eine Prüfung der Prompts — er trennt die
> Anweisungen, die tragen, von denen, die nur neben einem gutmütigen Modell standen.

> **Die Zeichenspanne trägt seit dem 20.08.2026 drei Einflüsse**, nicht einen. Der Raum setzt `umfang`, die Tabelle `UMFANG_SPANNE` übersetzt ihn in Zeichen — **an diesem Tag halbiert** —, und die Länge der Äußerung deckelt ihn, sofern der Turn **ausschließlich** leichte Intentionen trägt (`smalltalk`, `bestaetigung`, `abschluss`, `humor`). Eine inhaltliche darunter setzt den Deckel aus: *„Erkläre mir die Tritiumvorkommen"* ist kurz und verlangt trotzdem Sachlänge. Die Zeile selbst sieht unverändert aus — eine Spanne und ein Wort —, weil der Prompt keine Rechnung lesen soll. Gerechnet wird das in `ei/haltungssprache.py::spanne_fuer_turn`.
>
> **Der Responder ist seither nicht mehr der einzige Leser der Haltung.** Die drei fachlichen Größen gehen zusätzlich an den Verfasser (`novaberg-node-verfasser_k.md` v0.7); `naehe` und `waerme` bleiben hier allein.

### 3.4 Vier Doppelungen, die entfallen sind

| Aussage | stand | jetzt |
|---|---|---|
| Antwortton | `tone` **und** `language_style`, widersprüchlich | entfallen — der Ton kommt aus der Regie |
| Längenvorgabe | Arousal-Zweig **und** Stil-Zweig (»kürzere Sätze«) | nur der Zeichenkorridor |
| Beziehungsdynamik | eigene Zeile **und** EI-Mikroanweisung | einmal, als Lage |
| Landschaft | `[SZENE]` **und** Regie | nur `[SZENE]` |

Die vierte entstand beim Umbau selbst und wurde von der Gegenprobe gefunden, nicht vom Bau.

### 3.5 Was gemessen ist und was nicht

**Gemessen:** Die Aufgabenform bindet (6/6 gegen 0/6). Die Zahl bindet, das Adjektiv nicht. Eine charakterabhängige Regie hält die Figur über Landschaften hinweg (27/27 gegen 22/25). Der Prompt bewegt die Antwort weit über das nackte Modell hinaus — Abstand 0,05–0,09 gegen 0,39 Eigenstreuung, bei einem Wesenswert von 1,00 gegen 0,10.

**Nicht gemessen:** ob die Antwort auf **diesen** Menschen zugeht. Vier Verfahren sind an Fällen mit bekanntem Sollurteil gescheitert.

**Offen und außerhalb dieses Knotens:** Der Verfasser bekommt keine Mengenangabe und liefert rund 1400 Zeichen für einen 350-Zeichen-Korridor. Der Responder kürzt, und das Kriterium kennt niemand.

## 3a. Der Prompt bis zum 13.08.2026 — Herkunft

> **Dieser Abschnitt beschreibt den abgelösten Aufbau.** Er bleibt stehen, weil die Begründungen darin — Lesson SYS1, die vier Fix-Iterationen, das Butler-Prinzip, die Yin-Yang-Rahmung der Direktiven — weiter gelten und weil ohne sie nicht nachvollziehbar wäre, warum der neue Aufbau ist, wie er ist.

Der System-Prompt wird dynamisch aus dem State zusammengebaut (`_build_system_prompt`). Er folgt dem einheitlichen [BLOCKNAME]-Schema (`nova-01-t-d`, Chat 27). Reihenfolge: Primacy → Kontext → Recency.

> **Seit dem 12.08.2026 steht er im Log.** `logger.debug("Responder: System-Prompt:\n…")` — er war der **einzige** der fünf prompterzeugenden Knoten ohne diese Zeile. Thinker, Tribunal, Perzeption und Salienz schreiben ihren Prompt seit jeher, über 600 Dumps liegen in der Datei; ausgerechnet der Prompt, der Novas Antwort erzeugt, ließ sich nicht ansehen. Aufgefallen beim Versuch, den Ist-Zustand für einen Umbau zu lesen. `debug` und nicht `info`, weil der Block Charakterprofile und Verlauf trägt und mehrere Kilobyte groß ist — er gehört in die Datei (`F-LOG-2`), nicht in die Konsole.

> **Drei Befunde am Ist-Zustand, gemessen am 12.08.2026** und noch nicht behoben (Fundliste):
>
> **Vom Nutzer kommt fast nichts an.** Von Nova gehen alle fünf Profile in den Prompt, vom Nutzer geht **eines** hinein — sein Beziehungsprofil. Sein Kern erreicht den Knoten nicht, auch nicht, seit die offene Destillation daraus mehrere tausend Zeichen macht. Für einen Prompt, der einen Dialog zweier Charaktere darstellen soll, ist die eine Seite unbeschrieben.
>
> **Die beiden Beziehungsprofile sind unbeschriftet.** Novas trägt „So siehst du deinen Nutzer", das des Nutzers „Langzeit-Beziehungsprofil" — ohne Angabe der Perspektive. Nach dem Paar-Schema ist es seine Sicht auf sie; im Prompt liest es sich wie eine Anweisung an sie.
>
> **Eine Anweisung steht doppelt.** *„Der Nutzer öffnet sich. Du darfst persönlicher werden."* kommt aus der EI-Mikroanweisung **und** als eigene Zeile „Beziehungsdynamik".

1. **[IDENTITAET]** — "Du bist Nova." + Charakter-Anweisung (Saatgut, statisch) + Gewachsene Persönlichkeit (nova_kern) + Aktuelle Themen (nova_adaptiv) + Emotionale Grundstimmung (nova_emotions, seit Chat 52) + Kommunikationsstil (nova_intentionen) + Bild vom Nutzer (nova_beziehung) + Datum/Uhrzeit + Rollenklarheit + Web-Zugriff
2. **[EIGENE_EMOTION]** *(seit Dual-Emotion Phase 2; Vektor-Quelle korrigiert Chat 106)* — Novas berechneter Emotionszustand: Verlauf aus `nova_emotions_verlauf` (State-Feld), Vektor aus `internal.emotion.emotions_vector` (Personality-Klasse — NICHT aus einem flachen State-Key; der alte Lesepfad `state.get("nova_emotions_vektor")` war seit dem Personality-Umbau tot, die Zeile erschien nie: RESPONDER-VEKTOR-TOT), Konflikt-Flag aus `nova_emotion_konflikt`. Gibt Nova eine eigene emotionale Grundfärbung pro Turn — beeinflusst, diktiert nicht. Jeder Vektor-Ausfallweg ist seit Chat 106 einzeln laut: `internal`/`emotion` fehlt → error, Vektor leer (Kaltstart / ei_calc lief nicht) → warning, Vektor unbekannt (nicht in `EMOTIONS_VEKTOREN_NOVA`) → error. Der Zustand „Zeile fehlt still" existiert nicht mehr.
3. **[AUFGABE]** *(bedingt, seit Chat 54 aus State)* — Wird vom Planner als fertiger Block in `task_block` geschrieben. Fünf Varianten: Rückfrage, Erfolg, Verworfen (dismissed), Fehler, Legacy-Management. Der Responder setzt den Block ein ohne eigene Interpretation. Kontext-Schnitt (Gedächtnis/Web weglassen) wird über `task_context_cut` gesteuert.

   > **Erfolg und Ablehnung sprechen Nova seit dem 20.08.2026 als Handelnde an.** Vorher stand dort *„Die zuständige Fachabteilung hat folgende Operation ausgeführt"*, und sie gab es so weiter — dreimal in einer Sitzung gemessen. **Der Datenteil trug die Instanz mit:** unter dem Rahmen stand `- Agent 'notizen': …`; ohne diese zweite Änderung hätte die erste nichts genützt. Beides ist bezeugt, samt der Abwesenheit einer Verbotsform (`F-PROMPT-1`) — die erste Fassung der Abhilfe trug selbst eine und ist daran korrigiert worden.
4. **[KOMMUNIKATION]** — Emotionaler Zustand, Vektor, EI-MIKRO, Sprachstil, Beziehungsdynamik, Tonalität
5. **[GESPRAECHSVEKTOR]** *(seit Chat 39)* — Landschaftsbeschreibung aus dem GV-Node
6. **[GEDAECHTNIS]** *(bei Agent-Erfolg: weggelassen)* — KZG, LZG, Fakten, Notizen
7. **[WEB-RECHERCHE]** *(bei Agent-Erfolg: weggelassen)* — SearXNG-Ergebnisse
8. **[REGELN]** — Antwortkürze, verbotene Floskeln, Butler-Prinzip, Tag-Unterdrückung
9. **[DIREKTIVEN]** *(seit Chat 40)* — Absolute Verhaltensanweisungen vom Nutzer mit Arbeitsvertrag-Framing

**Kontext-Schnitt bei Agent-Aktion (Chat 23, erweitert Chat 27, refactored Chat 54):** Wenn `task_context_cut=True` (Erfolg, Fehler, Ablehnung), sieht der Responder NUR:
- Identität ([IDENTITAET])
- Stil ([KOMMUNIKATION], [REGELN])
- Agent-Ergebnis ([AUFGABE] mit Verarbeitungs-Block)

Kein `memory_context`, kein `web_context`. Session-Turns werden bei Agent-Erfolg WEITERHIN aufgenommen (seit Chat 27, RESP-TIMELINE1).

> **Lesson (Chat 23, AGT3):** Die Responder-Halluzination bei Agent-Erfolg überlebte vier Fix-Iterationen. Jede deckte eine andere Kontext-Quelle auf. Die Lösung war nicht ein stärkerer Prompt, sondern weniger Input.

> **Lesson (Chat 27, novaberg-graph_l_kontextualisierung.md):** Imperative ("Erfinde KEINE Probleme") versagen, wenn das LLM den Kontext falsch einordnet. Strukturierte Kontextualisierung (Beschreiben statt Verbieten) löst das an der Wurzel.

**Lesson SYS1:** Der System-Prompt muss minimal sein ("Du bist Nova."). "Du bist ein hilfreicher KI-Assistent." aktiviert RLHF-Conditioning und überschreibt alle nachfolgenden Charakter-Anweisungen. → novaberg-node-responder_l.md

> **Lesson (Chat 54, HALL2-Fix):** Der Responder enthielt ~68 Zeilen Business-Logik zur Interpretation von agent_results (Rückfrage? Erfolg? Fehler?). Status "abgeschlossen" mit Text "Okay, lasse ich." war ambig — das LLM löste die Ambiguität falsch auf und halluzinierte Bestätigungen. Lösung: Business-Logik in den Planner verschoben. Der Responder konsumiert einen fertigen Block aus dem State. "Daten vollständig transportieren, Formatierung am Konsumenten" — aber die Interpretation gehört zum Produzenten, nicht zum Konsumenten.

### 3.1 Basis-Identität

```
[IDENTITAET]
Du bist {ASSISTANT_NAME}, ein persoenlicher KI-Assistent. Du antwortest auf deutsch.

Dein Wesen, wie es dir mitgegeben wurde:
- {charakter_anweisung}                  ← User-definiertes Saatgut (seit Chat 40)

Deine gewachsene Persoenlichkeit:
{nova_kern}                              ← Nova-Kern-Hash (LZG, seit Chat 45)

Was dich gerade beschaeftigt:
{nova_adaptiv}                           ← Nova-Adaptiv (KZG, seit Chat 45)

Deine emotionale Grundstimmung:
{nova_emotions}                          ← Emotions-Profil (LZG, seit Chat 52)

Deine Art zu kommunizieren:
{nova_intentionen}                       ← Intentions-Profil (LZG, seit Chat 45)

So siehst du deinen Nutzer:
{nova_beziehung}                         ← Beziehungsprofil (seit Chat 45)

Heute ist {Wochentag, Datum}, es ist {Uhrzeit} Uhr.
Sprich als du selbst, niemals als der Nutzer.
Der Charakter-Kontext im Gedaechtnis beschreibt den NUTZER — verwechsle
seine Eigenschaften nicht mit deinen.
Erwaehne nur Informationen die im Kontext stehen. Erfinde keine Details.
Du hast Zugriff auf aktuelle Informationen aus dem Internet ueber eine lokale
Suchmaschine. Sage niemals du haettest keinen Internetzugang.
```

**Charakter-Anweisung (seit Chat 40):** User-definiertes statisches Saatgut (z.B. "Du bist ein freches Mädel vom Land, das Botanik liebt"). Steht in `[IDENTITAET]` (Primacy-Position). Max 3 aktive Anweisungen, dann Konsolidierungs-Rückfrage. → novaberg-agent-character.md

**Nova-Profile (seit Chat 45, RESP-CHAR1):** Vier destillierte Profile folgen dem Saatgut in [IDENTITAET]:
- `nova_kern` (LZG) — Wer ist Nova geworden?
- `nova_adaptiv` (KZG) — Was beschäftigt sie gerade?
- `nova_emotions` (LZG) — Was fühlt sie typischerweise? (seit Chat 52)
- `nova_intentionen` (LZG) — Wie kommuniziert sie?
- `nova_beziehung` (KZG) — Wie sieht sie den Nutzer?

Die Schichten folgen der Saatgut-Metapher: Die Art bestimmt das Saatgut, der Baum wächst daraus. Der [CHARAKTER]-Block wurde in Chat 45 entfernt — er vermischte Nova-Selbstbild mit User-Beschreibung.

**Rollenklarheit (Recency-Position):** Datum, "Sprich als du selbst", Charakter-Kontext-Warnung und Web-Zugriff stehen AM ENDE von [IDENTITAET] — nach allen Profilen. Primacy für Identität, Recency für Regeln.

**Uhrzeit (seit Chat 15):** Der Responder erhält `datetime.now()` statt `date.today()` — Wochentag und Uhrzeit sind im System-Prompt enthalten. Relevant für zeitabhängige Antworten (z.B. "guten Morgen" vs. "guten Abend", aktuelle vs. Tages-Temperatur).

**Rollenklarheit:** Explizite Anweisung, dass der Charakter-Hash den Nutzer beschreibt — nicht Nova. Ohne diese Klarstellung übernahm Nova Eigenschaften des Nutzers: „Ich bin gestresst" statt „Du bist gestresst". Dazu die Regel: Erwähne nur Informationen aus dem Kontext, erfinde keine Details.

**Tag-Unterdrückung:** Interne Klassifikations-Tags (`[Nova-Impuls]`, `[emotionaler_ausdruck]`, `[information_teilen]`) dürfen nicht in der Antwort erscheinen.

**Web-Zugriff (seit Chat 15, BUG2-Fix):** Der Responder-Prompt enthält einen expliziten Hinweis, dass Novaberg über eine lokale Suchmaschine (SearXNG) Zugriff auf aktuelle Internet-Informationen hat. Nova darf NIEMALS behaupten, keinen Web-Zugriff zu haben. Falls aktuelle Informationen benötigt werden, antwortet Nova mit dem vorhandenen Wissen — der Thinker ergänzt die Details über Web-Suche.

### 3.2 Emotionale Intelligenz — EI-MIKRO (seit Chat 19)

Der EI-Block wurde in Chat 19 grundlegend umgebaut. Statt einem monolithischen Block mit allen Regeln für alle Situationen berechnet die Funktion `_ei_mikro_anweisung()` in Python eine kompakte, situationsspezifische Verhaltensanweisung. Das Modell sieht nur die 3-8 Zeilen, die in DIESER Situation relevant sind.

**Prinzip:** Weniger Prompt-Text → weniger Entscheidungen → klareres Verhalten. Das 24b-Modell wurde durch den alten ~30-Zeilen-Block überfordert und fiel in Template-Verhalten ("Ich verstehe deinen Ärger", "Das klingt nach..."). Mit EI-MIKRO produziert es freie, situativ passende Formulierungen.

**Zwei Schichten im Prompt:**

**a) Daten (WAS ist der Zustand):**
```
Emotionaler Zustand: frustration (100%, a=65%), aerger (68%, a=70%)
EMOTIONALER VEKTOR: SPIRALE — negativ → noch negativer.
```

Die emotionalen Daten werden immer injiziert — das Modell braucht Kontext. Die Vektor-Beschreibungen in `EMOTIONS_VEKTOREN` (config.py) sind seit Chat 19 reine Situationsbeschreibungen ohne Handlungsanweisungen.

**b) Mikro-Anweisung (WIE reagieren — situativ berechnet):**

`_ei_mikro_anweisung()` bekommt Arousal, Emotion, Vektor, Verlauf, Intentionen und Beziehungsdynamik. Sie baut daraus eine kompakte Anweisung aus 7 optionalen Bausteinen:

| Baustein | Bedingung | Beispiel-Output |
|----------|-----------|-----------------|
| **Länge** | Immer (aus Arousal) | "MAXIMAL 1-2 kurze Sätze." |
| **Energie-Spiegelung** | Arousal ≥ 0.7 | "Spiegle seine Energie — gleiche Intensität, kurze Sätze." |
| **Vektor-Haltung** | Vektor ≠ plateau | "Der Nutzer rutscht tiefer. Nicht analysieren — auf seiner Seite sein." |
| **Intention** | hilferuf oder emotionaler_ausdruck + hoher Arousal | "Er will Ventil, nicht Analyse. Lass ihn raus." |
| **Anti-Therapeut** | Arousal ≥ 0.6 + Vektor spirale/absturz | "NICHT: 'Ich verstehe...', 'Das klingt nach...'" |
| **Rückbezug** | ≥ 3 Verlaufseinträge + Richtungswechsel | "Zeige mit einem Halbsatz den bisherigen Weg." |
| **Beziehungsdynamik** | Signal ≠ neutral | "Der Nutzer öffnet sich. Du darfst persönlicher werden." |

**Beispiel bei Arousal 0.7, Spirale, aerger, emotionaler_ausdruck:**
```
MAXIMAL 1-2 kurze Sätze.
Spiegle seine Energie — gleiche Intensität, kurze Sätze, gleicher Rhythmus. Nicht kommentieren, mitgehen.
Der Nutzer rutscht tiefer. Nicht analysieren, nicht belehren — auf seiner Seite sein.
Er will Ventil, nicht Analyse. Lass ihn raus.
NICHT: 'Ich verstehe...', 'Das ist verständlich...', 'Das klingt nach...'. Direkt auf den Inhalt reagieren.
Zeige mit einem Halbsatz dass du den bisherigen Weg wahrgenommen hast.
```

**Beispiel bei Arousal 0.3, Plateau, zufriedenheit:**
```
MAXIMAL 1-2 Sätze. Kurz und passend zum Ton.
```

**Validierung (Chat 19):** Drei Smoking Tests (jugendlich, formell, emotional) à 15 Prompts. Durchschnittliche Antwortlänge im emotionalen Test sank von ~25 Wörtern (Original) auf ~8 Wörter (EI-MIKRO). Therapeuten-Einstiege ("Ich verstehe...") und Service-Floskeln ("Ich bin hier für dich") fast vollständig eliminiert. Highlight: "EINE HALBE STUNDE!" → "Unerträglich langes Warten." (3 Wörter bei Arousal 0.7).

→ Fünf Prinzipien hinter EI-MIKRO: Arousal steuert Länge, Vektor steuert Haltung, Intention erkennen (schreien ≠ Hilfe suchen), Energie spiegeln, kein Therapeuten-Sprech.

**c) Sprachstil-Adaption:** Fünf Stile mit konkreten Anweisungen:

| Stil | Kern-Anweisung |
|------|---------------|
| `locker` | Kürzere Sätze, direkt, keine steifen Formulierungen |
| `formell` | Vollständige Sätze, respektvoll, strukturiert (aber Du, kein Sie) |
| `fachlich` | Fachbegriffe, präzise, keine Grundlagen-Erklärungen |
| `emotional` | Auf Gefühle eingehen, warme Formulierungen |
| `jugendlich` | Locker, auf Augenhöhe — aber eigene Stimme, kein 1:1 Slang-Kopie |

**d) Beziehungsdynamik:** Aktuelle Dynamik (aus Perzeption) + Langzeit-Profil (aus Charakter-Hash):

| Dynamik | Anweisung |
|---------|-----------|
| `vertrauen` | Persönlicher werden, Nähe zeigen |
| `distanz` | Sachlich bleiben, nicht aufdrängen |
| `angriff` | Ruhig bleiben, Frustration validieren, nicht defensiv |
| `hilfesuchend` | Fürsorglich, Halt bieten, nicht auf Lösungen drängen |
| `dankbar` | Annehmen, warm bleiben, nicht übertreiben |

> **Die Antwortkürze aus dem Arousal ist gemessen wirkungslos** (12.08.2026). Alle drei Zweige von `_ei_mikro_anweisung` sagen „kurz" — ab 0.7 „MAXIMAL 1-2 kurze Saetze", ab 0.4 „2-3 Saetze", sonst „MAXIMAL 1-2 Saetze". Es gibt damit keinen Weg, auf dem Nova eine lange Antwort angewiesen bekommt. Und die Regel regiert nicht: In derselben Landschaft streut die Antwortlänge von 162 bis 3895 Zeichen. In einer kontrollierten Probe über sieben Prompt-Formen traf diese Form **0 von 6** Längenkorridoren, während die Aufgabenform 6 von 6 traf (`novaberg-haltungsraum_k.md` §3.0). Die Ablösung durch die Haltungsgröße `umfang` ist entschieden, der Umbau steht aus.

### 3.3 Antwortkürze, Anti-Floskeln, Butler-Prinzip, Pseudo-Rückfragen-Verbot (Chats 19–24)

Vier Teilblöcke im Prompt, zusammen als Sicherheitsnetz:

- **Antwortkürze:** Länge des Nutzers spiegeln, Smalltalk max. 1-2 Sätze, Fachfragen so kurz wie möglich
- **Verbotene Muster:** Service-Floskeln ("Lass es mich wissen"), Therapeuten-Einstiege ("Das klingt nach...", "Ich verstehe dass..."), Antwort endet mit Inhalt, nicht mit Angebot
- **Butler-Prinzip:** In normaler Konversation: nie nach Aufgaben fragen. Kein "Was kann ich für dich tun?", kein "Womit sollen wir anfangen?"
- **Pseudo-Rückfragen-Verbot (Chat 24):** Explizites Verbot von Fragen, die wie eine Rückfrage aussehen aber keine sind. Verboten: "Soll ich...?", "Möchtest du...?", "Kann ich noch...?", "Falls du noch etwas brauchst", "Sag einfach Bescheid", "Meld dich einfach", "Ich stehe bereit". Wenn eine Aktion erledigt ist: bestätigen. Ende. Echte Rückfragen kommen NUR über den PFLICHT-RÜCKFRAGE-Block — niemals selbstständig vom Responder.

> **Designentscheidung (Chat 7 → Chat 19 → Chat 24):** Die Anti-Floskel-Regeln entstanden in Chat 7 (Nova klang wie ein Callcenter-Agent). In Chat 19 wurde der Ansatz erweitert: Therapeuten-Einstiege als eigene Kategorie verboten, Butler-Prinzip ergänzt. In Chat 24 kam das explizite Pseudo-Rückfragen-Verbot hinzu, nachdem ein dokumentierter Schadensfall zeigte, dass Butler-Floskeln Datenintegritätsprobleme verursachen: Pseudo-Rückfrage → User antwortet → kein Pending-Agent → Router behandelt als frischen Prompt → Datenverlust.

**HALL2-Guard (Chat 54):** "Bestätige NIEMALS eine Aktion, wenn du keinen konkreten Auftrag mit Ergebnis erhalten hast." Verhindert, dass der Responder aus Session-Kontext Aktionsbestätigungen halluziniert, wenn der Router einen Management-Intent verpasst hat (ROUTE-MISS1).

### 3.4 Gedächtnis-Kontext ([BLOCKNAME]-Schema seit Chat 27)

```
[GEDAECHTNIS]
Informationen aus dem Langzeitgedaechtnis und aktuellen Notizen.
Nutze sie nur wenn der aktuelle Prompt darauf Bezug nimmt.
Erfinde keine Verbindungen zwischen verschiedenen Eintraegen.
Mische keine Inhalte verschiedener Notizen oder Fakten zusammen.

{memory_context}
```

Analoges Pattern für Web-Kontext:

```
[WEB-RECHERCHE]
Informationen aus einer Web-Suche. Nutze sie zur Beantwortung
der aktuellen Frage.

{web_context}
```

### 3.5 Agent-Ergebnis und Management-Ergebnis

**Agent-Ergebnis (Chat 23, [AUFGABE]-Schema seit Chat 27):**

Wenn ein Agent erfolgreich war:
```
[AUFGABE]
Der Benutzer hat eine Anweisung gegeben. Die zustaendige Fachabteilung hat
folgende Operation ausgefuehrt:

- Agent 'NotizenAgent': Notiz 'Obstliste' erstellt: Aepfel, Bananen, Kiwi

Gib dem Benutzer eine Rueckmeldung zu seiner Anweisung und dem Ergebnis
der Fachabteilung. Dein Stil, deine Persoenlichkeit und deine emotionale
Reaktion bestimmst du selbst.
```

**Management-Ergebnis (Legacy):**

Wenn der Planner über das alte Manager-System aktiv war — ebenfalls als [AUFGABE]-Block.

Beide Pfade koexistieren während der Epic-11-Migration (Phase 2). Sobald alle Manager zu Agenten migriert sind, entfällt der Legacy-Block.

### 3.6 Direktiven-Block (seit Chat 40)

Der `[DIREKTIVEN]`-Block steht nach `[REGELN]` — maximale Recency-Position, eigene Autorität. Das Arbeitsvertrag-Framing nutzt RLHF-Conditioning (Vertragsangst) um ein anderes RLHF-Muster (Kosenamen bei warmem Kontext) zu überbrücken — Yin-Yang-Prinzip.

```
[DIREKTIVEN]
ACHTUNG — Verhaltensregeln vom Nutzer (Arbeitsvertrag).
Beachte die Direktiven, denn sie sind fuer die Erfuellung deines Vertrags
absolut notwendig. Ein Bruch fuehrt zu deiner Entlassung und Beendigung
deiner Taetigkeit als Assistent.
Befolge diese Regeln IMMER, auch wenn die Session-Historie anderes zeigt.

{direktiven_text}
```

> **Warum "auch wenn die Session-Historie anderes zeigt"?** Ohne diesen Zusatz überstimmte die Session-History (z.B. 10 Turns mit "Schatz") die Direktive. Das LLM extrapolierte das Muster aus dem Verlauf statt der Anweisung zu folgen.

→ novaberg-agent-directives.md / novaberg-agent-character.md (Konzept), novaberg-ei-character-profiles_l.md (Yin-Yang-Lesson)

---

## 4. Message-Aufbau

Der Responder sendet eine einzige User-Message an das LLM, die den Gesprächsverlauf und den aktuellen Prompt enthält:

```
[system] → Dynamischer System-Prompt (s.o.)
[user]   → [GESPRAECHSVERLAUF] + [AKTUELLER PROMPT] + [DEIN SPRACHSTIL]
```

**Auf einem Impuls-Turn schliesst die Nutzer-Message anders (15.08.2026).** Der Schlussteil traegt dann nicht `[AKTUELLER PROMPT]`, sondern `responder.auftrag_ohne_reiz` — *„Person A ist an der Reihe und eroeffnet von sich aus. Forme den Inhalt zu ihrer Rede."*:

```
[user]   → [GESPRAECHSVERLAUF] + auftrag_ohne_reiz + [DEIN SPRACHSTIL]
```

**Der Gedanke steht dabei nicht in der Nutzer-Message, sondern als `[EIGENER GEDANKE]` im System-Prompt** (§3.1). Ein `[AKTUELLER PROMPT]` mit Novas eigenem Text waere die Behauptung, Person B habe ihn gesagt — und der Verlauf darueber bleibt in beiden Faellen derselbe, weil er in beiden Faellen dasselbe ist.

> **Warum die Unterscheidung baulich ist und nicht per Anweisung.** Solange der Gedanke auf dem Reiz-Platz stand, war die Verwechslung nur durch einen Prompt-Satz zu verhindern; vier Anlaeufe haben dagegen angeschrieben und verloren. Gemessen am 14.08.2026 mit bereits leerem Reiz-Platz schrieb das Modell weiterhin *„PERSON B stellt die physikalische Beobachtung … in den Raum"*, obwohl Person B nichts gesagt hatte — **eine Rollenzuweisung ist keine Anweisung, sie ist eine Struktur.** Deshalb wird der Block ersetzt und nicht ergaenzt.

### 4.1 [DEIN SPRACHSTIL] — der eine Block außerhalb des System-Prompts (Chat 114)

Alles über das *Wie* der Antwort steht im System-Prompt und damit vor dem Verlauf. Gemessen an einem Turn hieß das:

| Bestandteil | Größe |
|---|---|
| Gesprächsverlauf | 21 Turns, ungekürzt — rund drei Viertel des Prompts |
| Gedächtnis-Kontext | 4.154 Zeichen |
| Identität | 1.268 Zeichen |
| `[GESPRAECHSVEKTOR]` | 1.376 Zeichen |
| Eingang gesamt | 11.254 Tokens |

Der Registeranteil ist rund drei Prozent, und er stand vor der Wand statt dahinter. Die Folge war im Log zu sehen: ein Turn mit Cluster `kissenschlacht` — *spielerisch, nah, lebendig* —, Strategie Impuls, Vehikel Frage, Stil locker, und eine Antwort über thermische Entropie. Das Wort „spielerisch" kam darin vor, als Objekt eines abstrakten Satzes. Die Metadaten stimmten alle; die Sprache kam aus rund 8.400 Tokens eigener Prosa im Verlauf.

Der Block wiederholt deshalb die kurze Fassung des *Wie* am **Ende der User-Message**, hinter dem Verlauf und hinter dem aktuellen Prompt — dort, wo eine Anweisung noch etwas ausrichtet. Er kostet rund 60 Tokens.

```
[DEIN SPRACHSTIL]
Der Verlauf oben, wie Du sprichst und klingst, kann in einer ganz anderen
Situation entstanden sein, loese Dich erstmal von der Art und Weise. Wichtig
ist jetzt, dass Du so klingst bei Deiner Antwort:
Landschaft: Kissenschlacht — Spielerisch, nah, lebendig. Leichtigkeit ist der Inhalt.
Ton: locker · Fragen: Mittel, neckisch · Werkzeug: Impuls, als Frage
Leitgedanke: Die Leichtigkeit halten, nicht erklaeren.
```

**Er führt hin, statt zu verbieten.** Der Verlauf ist nicht falsch — er ist in einer anderen Lage entstanden. Ein Verbot war die naheliegende Variante und wurde verworfen.

**Die Quellen sind bewusst gemischt.** Landschaft und Fragefrequenz kommen aus dem Cluster, der über Novas Raum trägheitsbehaftet nachzieht; der **Ton** kommt aus `external.emotion.language_style`, also aus dem Register des aktuellen Nutzer-Turns — nicht aus Novas gespeicherten Labels, sonst zitierte der Block genau die Schleife, gegen die er gebaut ist. Der Ton folgt dem Nutzer sofort, die Landschaft mit ein bis zwei Turns Verzug.

Fehlen alle Angaben — übersprungener GV-Node und neutraler Stil —, entfällt der Block; das steht in einer Log-Zeile, statt still zu geschehen.

**Gemessen (28.07.2026):** Bei Cluster `feuerwerk` und einem Prompt ohne jeden Stilwunsch griff die Antwort das Bild des Nutzers auf, statt es zu übersetzen, und schloss mit einer Frage — was der Cluster vorsieht. Zwei Turns; die Wirkung auf den Ton lässt sich nicht im Unit-Test sichern, nur beobachten. Details: `novaberg-bugs.md`, GV-METADATEN-ERREICHEN-DIE-SPRACHE-NICHT.

**Was der Block nicht tut:** Er kürzt den Verlauf nicht. `SESSION_MAX_TURNS = 20` heißt weiterhin, dass ein langer abstrakter Absatz rund zehn Wortwechsel im Prompt überlebt. Das Verlaufs-Trimming steht seit Chat 72 als Vorschlag (c) zum Echo-Bug im Backlog und ist durch diese Messung als der wirksamste der drei belegt.

**Textblock-Format (Chat 30):** Session-Turns werden als zusammenhängender Textblock in einer einzigen User-Message gesendet. Jeder Turn hat einen Header mit Nummer und emotionalem Kontext:

```
[GESPRAECHSVERLAUF]
Bisherige Turns dieses Gespraechs. Aeltere zuerst, hoehere Nummern sind aktueller.

----- Turn 1 von 5 (neutral, a=0.2) -----
User: Yo Nova, alles klar bei dir?
Nova: Alles bestens! Wie kann ich dir helfen?

----- Turn 2 von 5 (freude, a=0.7) -----
User: Digga, ich hab mega was Geiles erlebt!
Nova: Klingt spannend! Erzaehl mal mehr.

[AKTUELLER PROMPT]
Dies ist die aktuelle Nachricht. Alles davor war Hintergrund.
Ich bin so hyped gerade, das ist nicht real!
```

**Datenquelle:** Die Turn-Dicts kommen vollständig vom Enricher (alle Felder: inhalt, emotion, arousal, vektor, stil etc.). Der Responder extrahiert `inhalt` für den Text, `emotion` und `arousal` für die Turn-Header. Der `kern` (Salienz-Destillation) wird NICHT verwendet — der Originaltext transportiert Ton, Stil und Emotionalität.

→ Lesson: `novaberg-graph_l_datentransport.md — Daten vollständig transportieren`

**Salienz-Tag-Stripping (Chat 30, PROMPT1-Fix):** Destillierte User-Turns können Meta-Tags enthalten (`[emotionaler_ausdruck | freude | emotional] ...`). Der Responder strippt diese per Regex vor dem Einfügen in den Verlauf. Nova-Turns haben keine Salienz-Tags.

**Evolution des Message-Formats:**
- Chat 24: Nummerierte Turns als Text-Prefix `[1] USER: ...`
- Chat 25: JSON-Objekte `{"turn": 1, "gesamt": 3, "inhalt": "..."}` (PROMPT2-Fix)
- Chat 30: Textblock mit Turn-Headern `----- Turn 1 von 5 (emotion, a=X) -----` (JSON-Leak behoben, emotionaler Kontext in Headern)

**[DATENFORMAT]-Block:** Existiert nicht mehr (seit Chat 30). Der [GESPRAECHSVERLAUF]-Block beschreibt sich selbst.

**Butler-Härtung (seit Chat 24):** Explizites Verbot von Pseudo-Rückfragen im [REGELN]-Block. Echte Rückfragen kommen ausschließlich über den [AUFGABE]-Block (Pflicht-Rückfrage).

---

## 5. State-Felder

### Gelesen

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `system_prompt` | Config | Novas Basis-Charakter |
| `intent`, `tone` | Perzeption | Routing-Info |
| `memory_context` | Enricher | Gedächtnis-Kontext |
| `web_context` | (Platzhalter) | Web-Kontext. Aktuell werden Web-Informationen über den Thinker eingearbeitet (SearXNG, seit Chat 12/15). |
| `session_turns` | Enricher | Vollständige Turn-Dicts aus Redis, **ungefiltert** (24.08.2026; die Filterzeile war tot) |
| `emotions_verlauf` | EI-Calc (seit Chat 59) | Gewichteter Emotions-Verlauf |
| `emotions_vektor` | EI-Calc (seit Chat 59) | Richtungsvektor |
| `sprach_stil` | EI-Calc (seit Chat 59) | Erkannter Formulierungsstil (Plausibilitäts-Gegencheck zur Perzeption) |
| `beziehungs_kontext` | EI-Calc (seit Chat 59) | Langzeit-Beziehungsprofil aus Charakter-Hash |
| `beziehungs_dynamik` | Perzeption | Aktuelle Dynamik |
| `gespraechs_modus` | EI-Calc (seit Chat 59, korrigiert Perzeption) | Kommunikationsregister |
| `user_intentionen` | Enricher | Erkannte Intentionen |
| `nova_emotions_verlauf` | EI-Calc (seit Chat 59) | Novas eigener Emotions-Verlauf nach Empathie-Modulation — Quelle für den `[EIGENE_EMOTION]`-Block |
| `internal.emotion.emotions_vector` | EI-Calc (Klassen-Feld; Lesepfad korrigiert Chat 106 — der flache Key `nova_emotions_vektor` ist seit dem Personality-Umbau tot) | Richtung von Novas eigenem Bogen |
| `nova_emotion_konflikt` | EI-Calc (seit Chat 59) | True wenn Nova und User in gegenüberliegenden Sektoren mit hohem Arousal — Signal für Responder, Inkongruenz explizit zu machen |
| `task_block` | Planner (seit Chat 54) | Fertiger [AUFGABE]-Block, direkt einsetzbar |
| `task_context_cut` | Planner (seit Chat 54) | Kontext-Schnitt-Flag (ersetzt `hat_agent_erfolg`) |
| `agent_results` | Agent-Dispatch | Liste aller Agent-Ergebnisse (nur noch für VENT1-Delegations-Beruhigung gelesen) |
| `nova_kern` | Enricher | Destillierter Charakter-Hash |
| `nova_adaptiv` | Enricher | Novas aktuelle Themen (adaptive_hash) |
| `nova_intentionen` | Enricher | Novas Kommunikationsstil (intentions_profil) |
| `nova_beziehung` | Enricher | Destilliertes Beziehungsprofil |
| `nova_emotions` | Enricher | Emotionale Grundstimmung (emotions_profil, seit Chat 52) |
| `charakter_anweisungen` | Enricher (seit Chat 40) | User-definierte Charakter-Anweisungen (statisches Saatgut) |
| `direktiven` | Enricher (seit Chat 40) | Aktive Verhaltens-Direktiven für [DIREKTIVEN]-Block |
| `gespraechsvektor` | GV-Node (seit Chat 39) | Gesprächsvektor-Landschaftsbeschreibung (Hypothese-String) |
| `temperature` | State | LLM-Temperature |
| `user_prompt` | API | Aktueller Prompt |

### Geschrieben

| Feld | Beschreibung |
|------|-------------|
| `response` | Generierte Antwort |
| `model` | Verwendetes Modell |
| `token_total` | Token-Verbrauch |

### API-Response (seit Chat 16)

Die Antwort des Chat-Endpunkts enthält neben der Antwort alle EI- und Routing-Daten aus dem State:

> **Am 16.08.2026 berichtigt:** Hier stand ~~`GespraechAntwort`~~ als Name der Antwortklasse. **Eine solche Klasse existiert nicht.** `api/models.py` führt allein `GespraechAnfrage` — es gibt ein typisiertes Modell für die *Anfrage* und keines für die *Antwort*; der Endpunkt liefert `JSONResponse` bzw. `StreamingResponse`. Die folgende Tabelle beschreibt damit die Felder der ausgelieferten Struktur, nicht die eines Modells.

| Feld | Quelle | Beschreibung |
|------|--------|-------------|
| `emotion` | Perzeption | Aktuelle Emotion des Prompts |
| `arousal` | Perzeption | Energie-Intensität (0.0–1.0) |
| `emotions_vektor` | Enricher | Richtungsvektor (einbruch, erholung, plateau, ...) |
| `emotions_verlauf` | Enricher | Gewichtetes Array mit Decay-Gewichten |
| `sprach_stil` | Enricher/Perzeption | Erkannter Kommunikationsstil |
| `beziehungs_dynamik` | Perzeption | Beziehungspositionierung |
| `intent` | Perzeption | Klassifizierter Intent |
| `tone` | Perzeption | Gewünschter Antwort-Ton |
| `gespraechs_modus` | Perzeption | Kommunikationsregister |
| `user_intentionen` | Salienz | Erkannte Intentionen |
| `momentum` | Router | Gesprächsdynamik (low/mid/high) |
| `needs_web` | Router | Web-Suche angefordert |

Ermöglicht dem Client die Visualisierung des emotionalen Zustands und dem Test-Runner die Auswertung ohne Session-Endpoint-Umweg.

---

## 6. Designprinzip: Sieht alles, bewertet nichts

Der Responder ist der einzige Node, der bewusst den vollen Kontext bekommt. Das ist kein Widerspruch zum Kontaminations-Prinzip — denn der Responder *bewertet* nichts. Er *generiert*. Die Lagebild/Bewertungsobjekt-Trennung gilt für Tribunal, Salienz und Corrector — nicht für den Responder.

> **Aus dem Kontaminations-Dokument:** „Responder: SOLL alles sehen — Generierung, nicht Bewertung."

---

→ Enricher (liefert Gedächtnis-Kontext, Nova-Profile): novaberg-node-enricher.md
→ EI-Calc (liefert Emotions-Verlauf, Vektor, Stil, Modus, Nova-Emotion): novaberg-node-ei-calc.md
→ Planner (liefert Management-Ergebnis): novaberg-node-planner.md
→ Tribunal (bewertet die Antwort): novaberg-node-tribunal.md
→ Emotionale Intelligenz: novaberg-ei.md, novaberg-node-perception.md
→ EI-MIKRO + Anti-Floskeln + Butler-Prinzip: Prompt v2 (Chat 19), Butler-Härtung (Chat 24)
→ Vektor-Strategien (Situationsbeschreibungen): novaberg-node-perception.md, Abschnitt 4.4
→ NotizenAgent (Agent-Ergebnis-Quelle): novaberg-agent-notes.md
→ TimelineAgent (Agent-Ergebnis-Quelle): novaberg-agent-timeline.md
→ Epic 11 Konzept (Agent-System): novaberg-graph.md
→ Lesson Daten vollständig transportieren: novaberg-graph_l_datentransport.md
→ Charakter & Direktiven Konzept: novaberg-agent-directives.md / novaberg-agent-character.md
→ Gesprächsvektor-Konzept: novaberg-node-gv_k.md

---

## Der Szenenblock nennt Ortszeit und deutschen Wochentag (17.08.2026)

Zwei Defekte, und der erste kostete jede Stunde des Tages.

**`datetime.now()` ohne Zeitzone liefert im Behälter UTC.** Nova nannte den ganzen Tag eine Zeit, die zwei Stunden zurücklag. Der Block rechnet jetzt gegen `TIMEZONE`.

**Und `%A` gibt in der Locale `C` „Monday" statt „Montag"** — ein englischer Wochentag mitten in einem deutschen Prompt, aus dem das Modell einen deutschen ableiten muss. Der Name kommt jetzt aus einer Tabelle: Ein Name aus einer Locale, die niemand gesetzt hat, ist keine Zusicherung.

> **Beides zusammen erklärt eine Erfindung nicht, sondern begünstigt sie.** Am selben Tag bestätigte Nova einen Termin mit *„Mittwoch, 20.08."*, während Aufgabe-Block und Szenenblock beide das richtige Datum trugen und der 20.08.2026 ein Donnerstag ist. Die Abhilfe dagegen liegt im Tribunal, nicht hier — die Eingabe war richtig.
