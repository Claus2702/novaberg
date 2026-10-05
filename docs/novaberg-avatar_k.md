# Novaberg — Emotions-Avatar (Konzept)

**Absicht:** Ein 2D-Avatar im GTK4-Client zeigt Novas eigenen Emotionszustand als lebende Bleistiftskizze; er stellt dar, was die Emotionsberechnung liefert, und entscheidet selbst nichts.
**Stand:** 05.10.2026, nach 00:28 UTC (Gliederung: §13.18 Kopfdrehung in `_t`). Davor 04.10.2026, 18:01 UTC (§3: die Kopfdrehung). Davor 04.10.2026, 15:39 UTC (§3: im Nachdenken der Blick ins Leere; beim Sprechen Faktor 0,75). Davor 04.10.2026, 14:30 UTC (§3: beim Sprechen die Emotion der Antwort selbst). Davor 04.10.2026, 13:47 UTC (§3: die Schrift der Phasenanzeige folgt der Statusleiste; nicht jede Mimik muss deutlich sein; Erregung weitet die Pupille). Davor 04.10.2026, 12:25 UTC (§3: die Phase unter dem Gesicht, L6; die Reihenfolge L6 → Generator → L4/L5). Davor 04.10.2026, 10:30 UTC (§3: der Weg der Arbeitszyklen im Client — Architektur, Absender, Wächter, Statuszeile, Öffnen des Panels; ausgearbeitet in `_t` §17.10). Davor 03.10.2026, 20:48 UTC (§3: die Statuszeile zeigt jeden Arbeitszustand). Davor 03.10.2026, 19:19 UTC (§3: die Arbeitszyklen gehen als Ereignisse an den Client, auch für die Statuszeile). Davor 03.10.2026 (§3 neu: die Denkweisen im Leerlauf; dazu entschieden: das Nachdenken taktet länger; ausgearbeitet in `_t` §17, Bauteile in `_b` §18). Davor 02.10.2026
**Umsetzung:** ~~keine Featurezeile — sie entsteht, wenn Novaberg das Feature bekommt (Entscheidung vom 02.10.2026, `novaberg-avatar_e.md`). Im Client ist nichts gebaut; ein HTML-Prototyp liegt unter `labor/avatar/` (§13).~~ → **seit 03.10.2026 gebaut** und im Client gesehen (`novaberg-avatar_b.md` §16, Featurezeile *Avatar-Panel*); der Prototyp unter `labor/avatar/` bleibt die Referenz.
**Teile:** `novaberg-avatar_t.md` · `novaberg-avatar_b.md` · `novaberg-avatar_e.md` · `novaberg-avatar_m.md`
**Grundlagen:** `novaberg-ei-plutchik.md`, `novaberg-ei-dual-emotion_k.md`
**Entschieden:** 10 · **Offen beim Meister:** 8 (Liste in `novaberg-avatar_e.md`)

> Alle Bezeichner für **neue** Bausteine (Klassen, Felder, Funktionen) sind **Vorschläge**.
> Aussagen über das **bestehende** System stammen aus den oben genannten Dokumenten,
> nicht aus dem Code. Sie gelten als Doku-Stand, bis ein Audit sie belegt (Abschnitt 11).
>
> → **Am Code belegt am 02.10.2026:** O1–O5 und O9 (`novaberg-avatar_e.md` §11), der Datenvertrag in `novaberg-avatar_t.md` §14.

---

## § → Datei

| § | Abschnitt | Datei |
|---|---|---|
| 1, 2 | Ziel, Leitprinzip | `novaberg-avatar_k.md` |
| 3–9 | Darstellungsstil, Parameterraum, Emotions-Mapping, Intensität und Mischung, Übergangsmodell, Schichtenmodell, Integration im GTK4-Client | `novaberg-avatar_t.md` |
| 10 | Testbarkeit | `novaberg-avatar_b.md` |
| 14, 15 | Datenvertrag mit dem Server, Portierung nach GTK4 und Cairo | `novaberg-avatar_t.md` |
| 16 | Bauteile für den Client (B1–B8) | `novaberg-avatar_b.md` |
| 17 | Leerlauf: Zustände und Auslöser, Schichten, Formen, Antwort, Lidschlag, Raum, Datenvertrag, Abweichungen vom Generator | `novaberg-avatar_t.md` |
| 18 | Bauteile für den Leerlauf (L0–L5) und Abnahme | `novaberg-avatar_b.md` |
| 11, 12 | Offene Punkte, Annahmen | `novaberg-avatar_e.md` |
| 13 (Einleitung), 13.1, 13.3, 13.9, 13.12–13.14, 13.18 | Figur aus Vorlage: Pipeline, Alternative, bewegliches Kinn, Sprechschicht, Muskelkanäle, Einzellaute, Kopfdrehung | `novaberg-avatar_t.md` |
| 13.8, 13.10, 13.11 | Feinabstimmung des Prototyps nach Sichtprüfung | `novaberg-avatar_b.md` |
| 13.2, 13.4–13.7, 13.15, 13.16 | Befunde und Messungen | `novaberg-avatar_m.md` |
| — | Änderungen der Fassungen 0.1 bis 0.5, Entscheidungen, Befunde der Aufteilung, Abweichungen Prototyp ↔ Konzept | `novaberg-avatar_e.md` |

---

## 1. Ziel

Ein 2D-Avatar im GTK4-Client, der **Novas** aktuellen Emotionszustand sichtbar macht.

- Stil: Bleistiftskizze, bewusst stilisiert, kein Fotorealismus.
- Dauerhaft animiert: Das Bild „lebt“ auch ohne Zustandsänderung.
- Emotionswechsel laufen als flüssiger Übergang in etwa 1 Sekunde,
  von jedem Zustand zu jedem anderen, auch mitten in einem laufenden Übergang.

**Nicht Ziel (v1):** Fotorealismus, 3D, generative Bild- oder Videomodelle,
eigenständige Interpretation von Emotionen durch den Avatar, Darstellung der
User-Emotion (das bleibt Aufgabe des Emotions-Radars).

---

## 2. Leitprinzip: Der Avatar ist ein reiner Renderer

Analog zu „LLM als Sprach-Renderer“: Der Avatar entscheidet nichts.

- Die Emotion wird deterministisch in Python berechnet (EI-Calc, Rolle `character`).
- Der Avatar erhält einen **Ziel-Emotionszustand** und stellt ihn dar.
- Der Avatar kennt keine Gesprächsinhalte, leitet keine Emotionen ab und
  normalisiert nicht erneut.
- **Er ist eine Puppe, an der Fäden gezogen werden** (Entscheidung vom 02.10.2026, `novaberg-avatar_e.md`):
  Entschieden wird vorher, in der Emotionsberechnung, im Verfasser und im Responder; der Avatar
  bekommt die Fäden — Emotion und Arousal, beim Sprechen die Laute — und nimmt die Stellung ein.

| Baustein | Verantwortung | Kennt Emotionen? |
|---|---|---|
| Mapping | Emotionszustand → Gesichtsparameter | ja |
| Animator | Übergang zwischen Gesichtsparametern über die Zeit | nein |
| Renderer | Gesichtsparameter → Zeichnung in einem Rechteck | nein |

---

## 3. Die Denkweisen: Rauschen, Nachdenken, Antwort, Nachklang

**Absicht des Meisters, 03.10.2026**, wörtlich: *„Wenn Nova keinen Prompt hat, haben wir einen Leerlauf, in dem normalerweise Pixie arbeiten sollte. Gibt man einen Prompt ein, beginnt Nova mit der aktuellen Emotion nachzudenken für die Dauer des Turn, das ist konvergentes Denken. Dies können wir für die Dauer des Turns darstellen. Danach kommt die Widergabe der Antwort, die Interaktion mit dem Nutzer. Danach und ein paar Sekunden später — evtl 1 Minute — wird sie wieder in ein Rauschen verfallen, das divergente Denken. Wenn Pixie denkt (divergent), hat sie einen Auftrag, dieser hat Emotionen. Mit diesen geht sie an einen Auftrag heran, der dann wieder zu einem Turn führt, wenn er in den Charakter-Graph eingespeist wird (konvergent). Wir wechseln hier die Denkweisen, während sie nicht in Turns mit dem User beschäftigt ist. Diese konvergenten Turns und die divergenten Pixie-Phasen können wir darstellen. Wir haben Emotionen an jedem Punkt. Wir müssen nur eine angebrachte Form von Leerlauf-Animationen einfügen mit entsprechender Ruhe, Zeiten, Pausen, Zufall, etc.. […] Zufall, aber geformt. Und das ist das wichtigste! Es muss stimmig sein, aber aus der Gruppe der dann möglichen Mimiken können wir zufällig eine Abhandlung aufbauen.“*

| Zustand | Wann | Denkweise | Emotion aus |
|---|---|---|---|
| **Rauschen** | kein Turn; Pixie arbeitet an einem Auftrag | divergent | Pixies Auftrag |
| **Nachdenken** | vom Prompt bis zur Antwort — auch, wenn ein Auftrag Pixies als Impuls in den CharacterGraph geht | konvergent | Nova im Turn |
| **Antwort** | die Wiedergabe, lippensynchron | — | die Antwort ~~(`nova_emotion`, `nova_arousal`)~~ → die Wahrnehmung der Antwort (`emotion`, `arousal`), entschieden 04.10.2026 |
| **Nachklang** | einige Sekunden bis etwa eine Minute nach der Antwort, dann zurück ins Rauschen | Übergang | ausklingend |

**Das Leitprinzip bleibt (§2):** Der Avatar entscheidet nichts — er bekommt je Zustand die Emotion und spielt aus einer Gruppe stimmiger Mimiken eine Abfolge. **Zufall, aber geformt:** Welche Mimiken zu einem Zustand und einer Emotion gehören, wie lange eine steht, welche auf welche folgen darf und wie lang die Pausen sind, ist festgelegt; welche davon gerade kommt, entscheidet der Zufall.

**Grundlage:** die Recherche `labor/avatar/recherche_mimik_leerlauf.md` (03.10.2026: Verhaltensweisen beim Denken mit Belegstärke, Zeitwerte, Leerlauf virtueller Agenten, Zuordnung zum Novaberg-Raum, Entwurf eines Generators). ~~**Was der Client heute bekommt:** `character_stage` während eines Turns (Beginn und Fortschritt des Nachdenkens, ohne Emotion als Feld) und die Antwort mit `nova_emotion`/`nova_arousal`; **nicht:** Pixies Phase und die Emotion ihres Auftrags.~~ → **Am Code gelesen 03.10.2026:** `character_stage` taugt nicht als Auslöser — ohne Herkunft und zum Teil erst nach der Antwort; den Beginn eines Turns kennt nur das Senden im Client, Pixies Auftrag und den Beginn eines Impulses meldet der Server nicht (`novaberg-avatar_t.md` §17.2, §17.8). **Umsetzung:** ausgearbeitet in `novaberg-avatar_t.md` §17, Bauteile L0–L5 und Abnahme in `novaberg-avatar_b.md` §18. **Backlog:** `AVATAR-PIXIE-LEERLAUF` (`novaberg-backlog-antwortpfad.md`), `PIXIE-START-ALS-EREIGNIS` (`novaberg-backlog-hintergrund.md`).

**Entschieden vom Meister, 03.10.2026:**

- **Die Arbeitszyklen gehen als Ereignisse an den Client — auch für die Statuszeile:** auf die Feststellung, dass es für Pixies Aufträge und für einen Impuls im CharacterGraph weder Start noch Ende als Ereignis gibt: *„Wir müssen natürlich die Arbeitszyklen mit Events an den Client geben. Auch schon deshalb, weil in der Statuszeile die Information erscheinen sollte. Dort haben wir bereits einen Eintrag Pixie: idle“*. Daraus folgt: Die Ereignisse aus `novaberg-avatar_t.md` §17.8 (`pixie_auftrag`, `impuls_denkt`) haben einen zweiten Empfänger neben dem Avatar — die Statuszeile des Clients (`client/ui/status_bar.py`). Heute ist ihr *„Pixie: idle“* der Startwert des Labels; überschrieben wird er nur von einem `momentum` aus den Metadaten eines Turns (`client/ui/main_window.py`, gelesen 03.10.2026), Pixies Arbeit erreicht ihn nie. → `novaberg-avatar_b.md` §18, L4 und L5. **Dazu**, auf die Frage, ob die Statuszeile auch einen Impuls des CharacterGraph zeigt oder nur Pixies Aufträge: *„Am besten jeden Status, so dass die Information lückenlos ist“* — die Statuszeile zeigt jeden Arbeitszustand Pixies (beide Spuren) und des CharacterGraph (Turn und Impuls), von Beginn bis Ende ohne Lücke; *idle* steht nur, wenn nichts läuft.
- **Pixies Start als Ereignis, nur als Rückfall:** *„der Start Pixies mit Auftrag und Emotion kann als Ereignis an den Client geschickt werden, darf aber konvergentes Denken in Turns und die User-Interaktion nicht stören, sondern nur den Fallback setzen und — wenn Nova bereits im Leerlauf ist — auf die Änderung des Fallbacks hinweisen. Das müssen wir am Server ändern.“* → Backlog `PIXIE-START-ALS-EREIGNIS` (`novaberg-backlog-hintergrund.md`).
- **Blinzeln bei Ärger wie bei Freude:** *„Die Blinzelrate: Ärger wie Freude. Ärger kann auch ruhig ablaufen und hat keine Beschleunigung der Frequenz automatisch im Beiklang.“* Die Emotion allein beschleunigt das Blinzeln nicht; die Recherche fand für Ärger ohnehin keine Messung.
- **Der Generator wird so eingebaut:** *„Gut, das bauen wir so den Avatar ein. Wir haben Leerlauf Emotionen und Rauschen mit Pixie. Das Konzept sollte vollständig sein.“* → `novaberg-avatar_t.md` §17, Bauteile `novaberg-avatar_b.md` §18. Zurückgestellt: *„Den Punkt mit der hohen Valenz ohne Reserve prüfen wir später.“* → `AVATAR-VALENZ-RESERVE`.
- **Das Nachdenken taktet länger als das Rauschen:** auf den Vorschlag, die Taktlänge im Nachdenken mit dem Faktor 1,3 statt 0,85 zu rechnen und dort am Blickwechsel seltener zu blinzeln (Wahrscheinlichkeit 0,3 statt 0,7): *„Ja, Faktor 1,3 wirkt gut, dann testen wir erneut“*. Anlass: Die Analyse eines Mitschnitts des Generators las Konvergenz an wenigen, langen Formen; mit den kurzen Formen blinzelte Nova im Nachdenken öfter als im Rauschen (im Labor gemessen, Freude 0,6 gegen Neugier 0,45: 25,5 gegen 21,8 je Minute, danach 16,2 gegen 22,6).

**Entschieden vom Meister, 04.10.2026** — zum Weg der Arbeitszyklen im Client, auf einen Architekturentwurf mit acht Fragen; ausgearbeitet in `novaberg-avatar_t.md` §17.10, Bauteile in `novaberg-avatar_b.md` §18:

- **Die Architektur:** `PanelBase` *„darf wachsen“* — um ein Merkmal und eine leere Methode, über die ein Panel die Arbeitszyklen bekommt; *„Quelle im Hauptfenster“* — ein Arbeitszustand im Hauptfenster bekommt jedes Ereignis zuerst, schreibt als einziger die Statuszeile und gibt das Ereignis an die Panels weiter; *„eigener Typ“* — je Ereignis ein Typ, einmal beim Eingang aus der Nutzlast gebildet und geprüft; *„gleich alle 4 Typen“* — der Client kennt `turn_beginnt`, `turn_gescheitert`, `pixie_auftrag` und `impuls_denkt` ab L3, und der Server sendet die beiden neuen erst danach.
- **Nova denkt, gleich wer den Turn beginnt — solange das Panel offen ist:** *„Nova denkt, wenn das Avatar-Panel offen ist. Dann ist egal, wer der Initiator ist, bzw. die Idle-Time existiert dann. Ist der Avatar geschlossen, fehlt der Ereignis-Empfänger und es gibt keine Berechnung des Avatars“*. Auch eine Nachricht des Nutzers aus einem anderen Client lässt Nova nachdenken.
- **Der Wächter gilt auch für die Statuszeile:** auf den Vorschlag, dass ein Fehler beim Senden das Denken beendet wie ein gescheiterter Turn und die Statuszeile denselben Wächter bekommt wie der Avatar: *„Ja, die 600 Sekunden Grenze passt“*.
- **Die Statuszeile nennt die Art der Aufgabe, das Momentum entfällt:** *„Das Momentum ist nicht notwendig und kann entfallen. Wichtig ist, dass der Status angezeigt wird, welche Typ von Aufgabe sie gerade rechnen: "Charakter-Berechnung", "Recherche", "Vertiefung", etc., man kann bei MouseOver zusätzliche Daten wie das Thema anzeigen, das Inhalt der Aufgabe ist.“* Daraus folgt: `pixie_auftrag` trägt das Thema doch — für den Tooltip der Statuszeile. **Der Avatar bekommt es weiter nicht** (§2): Das Panel gibt es nicht an die Puppe weiter.
- **Öffnen während des Denkens:** auf die Frage, ob das Panel im Nachdenken oder im Rauschen beginnt, wenn es geöffnet wird, während Nova denkt: *„Es startet in Nachdenken (Idle-Time), bis das nächste Start-Event nähere Informationen liefert.“*

**Entschieden vom Meister, 04.10.2026, nach der Messung von L3 im Betrieb** — Bauteile in `novaberg-avatar_b.md` §18:

- **Die Phase steht unter dem Gesicht:** *„Ich möchte, dass wir die aktuelle Phase unter dem Avatar mit anzeigen. Im Generator war das sehr gut gezeigt, Etwas in der Art als Status im Panel.“* Gemeint ist der Kasten „Generator“ der Referenz: laufende Form, wie lange sie steht, Blick, nächste Form, das Band des Zyklus und seine Spanne. Bauteil L6.
- **Die Reihenfolge:** *„Wir bauen erst den Status ein, L6, danach den Generator und L4/L5“* — der Generator wird nach den Befunden der Messung nachgestellt (Blick im Nachdenken, Einatmen, Sprechbeginn, Lidschläge; Fundliste, 04.10.2026), bevor L4 und L5 folgen.
- **Die Schrift der Phasenanzeige folgt der Statusleiste:** *„Halte bitte fest, dass wir die Schriftgröße im Status des Avatar-Panels an die Größe in der Statusleiste des Client-Panels anpassen. Das reduziert etwas das Gewicht der Anzeige unter dem Avatar.“* Backlog `AVATAR-STATUS-SCHRIFT`.
- **Nicht jede Mimik muss deutlich sein:** *„Ebenfalls möchte ich festhalten, dass nicht jede Mimik "deutlich" sichtbar sein muss. Das Geheimnis ist, dass viele kleine Mikrobewegungen das Erlebnis realer machen. Oft sind es kleine, subtile Bewegungen.“* Das gilt für das Nachstellen des Generators nach den Funden vom 04.10.2026: Ein Befund *„kaum sichtbar“* heißt nicht von selbst *„größer machen“*. Lebendig wird das Gesicht durch viele kleine Bewegungen, nicht durch wenige große.
- **Erregung weitet die Pupille:** auf den Hinweis, dass Angst (0,72) und Überraschung (0,8) die Pupille heute verengen, wie es im Zeichentrick üblich ist, und dass Erregung sie beim Menschen weitet: *„Erregung soll sie weiten, ja.“* Backlog `AVATAR-PUPILLE-AROUSAL`.
- **Beim Sprechen zeigt das Gesicht die Emotion der Antwort selbst:** auf den Befund, dass die Antwort heute Novas Stimmung zu Beginn des Turns trägt — `nova_emotion`/`nova_arousal`, Eintrag 0 des Verlaufs aus ihren früheren Antworten —, während die Wahrnehmung der eigenen Antwort beim Senden schon vorliegt (`emotion`/`arousal` derselben Nutzlast), und auf drei Möglichkeiten: **A** das Gesicht zeigt die Wahrnehmung der Antwort, nur der Client ändert sich, und die Antwort wartet weiter 2,3–2,7 s auf diese Wahrnehmung; **B** die Antwort geht vorher hinaus, und ein zweites Ereignis bringt die Wahrnehmung nach; **C** es bleibt. Der Meister: *„Die Entscheidung ist: A.“* Daraus folgt: Die Wartezeit auf die Wahrnehmung ist gewollt, nicht Verlust. Wer die Auslieferung vor `perzeption_assistant` zieht, nimmt dem Gesicht seine Emotion.
- **Im Nachdenken geht der Blick ins Leere, selten zum Betrachter:** auf die Frage, ob Nova im langen Nachdenken zum Betrachter sehen darf (gemessen sah sie dort 29 % der Zeit zum Betrachter, im Rauschen 11 %; empfohlen war *selten, etwa jeder vierte Zyklus, 1–1,5 s*): *„Ja, sie darf auch zum Betrachter sehen, selten, Nachdenken ist eher den Blick ins Leere richten abseits des Betrachters.“*
- **Beim Sprechen zeigt das Gesicht die Emotion mit dem Faktor 0,75:** auf die Frage, wie stark (empfohlen war 0,75, schwankend 0,65–0,85; Alternativen voll oder 0,5): *„Wir probieren 0,75“* — ein Versuch, der an der Messung bewertet wird. Ob der Faktor schwankt, sagt die Antwort nicht.
- **Der Kopf dreht sich mit, meist wenig:** auf einen Prototyp des Eigentümers im Labor mit einer Kopfdrehung bis ±15° und die Frage, wie weit der Kopf im Leerlauf dreht (empfohlen war *meist klein, selten 10–12°*): *„Drehung meist klein, beim zur Seite schauen, nachdenklich, dreht er um etwa 10° mit“*. Zur Frage, ob die Drehung vor oder nach L5 kommt: *„die Drehung können wir gleich einbauen“* — als eigener Bau der Referenz (L0′c) gleich nach L0′b, vor L1′/L2′.

