# Novaberg — Emotions-Avatar: Bauplan und Umstellung

**Teil von:** `novaberg-avatar_k.md` — dort Absicht, Kopfblock und die Tabelle „§ → Datei“
**Stand:** 02.10.2026
**Inhalt:** die Tests der Bausteine (§10) und die Bauberichte des Prototyps (§13.8, §13.10, §13.11). Dazu die Bauteile für den Client mit `ZIEL` / `TEST` / `MESSUNG` (§16).

---

## 10. Testbarkeit

Jeder Baustein ist ohne GTK testbar. Tests, die ohne das jeweilige Verhalten rot werden:

| Test | Prüft |
|---|---|
| Arousal 0 ergibt Neutral | `face(s, 0) == neutral` für alle 8 Sektoren |
| Moderat schwächer als intensiv | gleicher Sektor, niedrigerer Arousal → kleinere Abweichung von Neutral |
| Stetigkeit bei Unterbrechung | Zielwechsel mitten im Übergang erzeugt keinen Sprung in Position oder Geschwindigkeit |
| Framerate-Unabhängigkeit | 1 s in 10 Schritten und in 60 Schritten ergeben denselben Endzustand (Toleranz) |
| Kanalbereiche | Mischung beliebiger Verläufe bleibt in allen Kanalgrenzen |
| Unbekannte Emotion | Emotion außerhalb des Kanons → Error-Log, Neutral, kein Absturz |
| Determinismus Renderer | gleicher `FaceState` + gleicher Seed → identische Pfade |

---

---

## 16. Bauteile für den Client

**Stand 02.10.2026.** Reihenfolge nach Abhängigkeit; B1 und B3 können nebeneinander laufen. Nach dem Schnitt in Module (`novaberg-avatar_t.md` §15.2) braucht erst B8 das Sprechen; empfohlen ist deshalb B3 → B6 → B7 → B4 → B8 — das Gesicht wird früher sichtbar. Ein Bauteil, das den Client berührt, berichtet zwei Bilanzzeilen — Server-Suite und Zeugen des Clients.

| Nr | Bauteil | ZIEL | TEST | MESSUNG | Prüftiefe |
|---|---|---|---|---|---|
| B1 | Sektor in der Antwort (Server) | Jede `character_response` trägt `nova_sektor` passend zu `nova_emotion`: 1–8, `null` bei `neutral`, `null` mit Error-Zeile bei einem Namen außerhalb des Kanons | Zeugen für alle 17 kanonischen Namen und einen unbekannten; bestehende Felder unverändert; Gegenprobe | eine echte `character_response` aus einem Mess-Turn mit wissenschaftlichem Thema: `nova_sektor` passt zu `nova_emotion` | schmal — additiv und rückholbar |
| B2 | Impulse erreichen den Avatar (Client) | Eine Antwort aus eigenem Impuls erreicht das Avatar-Panel wie eine gewöhnliche; die übrigen Panels verhalten sich unverändert | Zeuge am Stream-Handler mit ersetztem `GLib.idle_add` (Muster `client/tests/test_stream_assignment.py`) | ein echter Impuls bei geöffnetem Panel: das Gesicht wechselt | schmal |
| B3 | Ausdruck und Animator (Logik) | Aus Sektor und Arousal entsteht dasselbe Ziel wie im Prototyp, und der sichtbare Zustand folgt ihm stetig | die Tests aus §10; dazu Gleichheit mit Referenzwerten des Prototyps für alle neun Sektoren bei Arousal 0, 0,3, 0,6, 0,85 und 1,0 — als erzeugte JSON-Datei unter `client/tests/avatar_reference/`, ihr Erzeuger liegt im Labor neben dem Prototyp | — reine Logik, gemessen in B7 | tief — eine Abweichung vom Prototyp wäre still |
| B4 | Sprechen (Logik) | Aus einem Text entstehen dieselben Laute, Zeiten und Mundkanäle wie im Prototyp | Charakterisierung: Ausgabe des Prototyps für einen festen Satz Testsätze gegen die Python-Ausgabe, mit Toleranz für Gleitkomma | — | tief — wie B3 |
| B5 | Bilder | Grundbild, Gesichts- und Halsebene liegen als PNG in `client/avatar/images/`, die Gesichtsebene vorab ausgestanzt mit Alphakanal | Größe, Kanäle, Alphakanal unter der Kinnlinie | Sichtvergleich mit dem Prototyp | schmal — ob die Bilder committet werden, entscheidet O13 |
| B6 | Zeichnen | Dieselben Kanäle und derselbe Seed ergeben dieselbe Zeichnung, und das Gesicht gleicht dem Prototyp | Determinismus (gleiche Eingabe → gleiche Pixel), Grenzwerte aller Kanäle ohne Fehler; pixelgleich zum Prototyp ist nicht verlangt (ein Seed je Teil) | Sichtvergleich je Sektor neben dem Prototyp, durch den Meister | tief |
| B7 | Panel | Das Avatar-Panel zeigt Novas Emotion des laufenden Turns und lebt auch ohne Wechsel | Registrierung und Werkzeugleiste (bestehender Test); der Takt startet bei `map` und endet bei `unmap` | echter Turn mit wissenschaftlichem Thema: das Gesicht wechselt in etwa 1 s; Bildrate in Cairo bei Standardgröße, mit Kinnverzerrung und beim Sprechen | schmal |
| B8 | Sprechen im Panel | Erreicht eine Antwort das Panel, spricht der Mund ihren Text | Zeuge: Antwort → Lautfolge gestartet, Ende → Ruhe | echter Turn | schmal — erst nach O9 |

**Stand 03.10.2026 — gebaut, nicht im Betrieb gemessen.** Unter `client/avatar/` stehen Ausdruck und Animator (B3), Sprechen (B4), Zeichnen von Strich, Augen, Brauen, Extras und Mund (B6), Grundbild mit Verzerrung und ganzes Bild (`compose.draw_face`, `layers.load_layers`), die Puppe (`puppet.py`) und das Panel `client/ui/panels/avatar_panel.py` mit Eintrag in Registry und Werkzeugleiste (B7, mit B8). Die Zeugen laufen ohne GTK und ohne `cairo` (189 mit B2), die Client-Suite auf dem Host mit `test_toolbar_panels.py` (219 grün). Referenzwerte: `client/tests/avatar_reference/expression.json` (45 Ziele) und `speech.json` (vier synthetische Sätze), erzeugt aus dem Prototyp mit `labor/avatar/referenz_ausdruck.js` und `referenz_sprechen.js`. **Gemessen** mit echtem Cairo auf dem Host: das ganze Bild in allen neun Sektoren gleich dem Prototyp (Aufnahmen des Prototyps ohne Fenster, Bild für Bild daneben); eine Antwort spricht lippensynchron nach Lautzeiten — Öffnung je Silbe, Lippenschluss bei m/b/p, danach der Ausdruck; ein Bild mit 600 px braucht in Ruhe ≈ 30 ms, beim Sprechen ≈ 40 ms (≈ 25–34 Bilder/s; der Prototyp im Browser 60). **B1 entfällt für v1:** Die Antwort an den Client trägt `nova_emotion` und `nova_arousal`; das Panel bildet den Sektor aus dem Namen. **B5:** Die Bilder als PNG (`labor/avatar/bilder_png.py`) liegen in `client/avatar/images/`, aber nicht im Repositorium (O13) — fehlen sie, zeigt das Panel eine Meldung. **B2 gebaut:** Eine Antwort aus eigenem Impuls (`reiz_herkunft: eigener_impuls`) erreicht nur das Avatar-Panel, mit ihrem Text unter `antwort` (`client/ui/turn_routing.py`, `broadcast_impulse`); die übrigen Panels laden bei einem Impuls nicht neu, eine Nachricht eines anderen Clients erreicht den Avatar nicht. Client-Suite auf dem Host danach `Ran 219 tests` / `OK`. **Offen:** der echte Turn und ein echter Impuls im sichtbaren Fenster; die Bildrate; ob `nova_emotion: ""` (ein Turn ohne Emotionsverlauf) neutral bedeutet oder ein Fehler ist — heute neutral mit Error-Zeile.

**Nicht in v1:** Mischung des Verlaufs (O7), Konflikt (O8), Vorlauf des Mundes vor dem Ton (keine Tonausgabe), Ausspracheregeln aus einem Lexikon.

## 13. Figur aus Vorlage (Prototyp, 29.09.2026)

*Teil Bauplan: die Feinabstimmung des Prototyps. Die übrigen Unterabschnitte von §13: Einleitung, 13.1, 13.3, 13.9, 13.12–13.14 in `novaberg-avatar_t.md`; 13.2, 13.4–13.7, 13.15, 13.16 in `novaberg-avatar_m.md`.*

### 13.8 Feinabstimmung nach Sichtprüfung (Meister, 01.10.2026)

- Ärger, Trauer, Enttäuschung nach v0.5: Ärger „wirklich gut“, übrige deutlich besser.
- Überraschung: Augenöffnung `eye_open` 1,35 → 1,215 (10 % weniger, ging zu weit auf).
- Partie unter den Augen: wirkte wie starke Falten. Tränensäcke der Vorlage um 50 %
  aufgehellt (nur Abdunklung gegenüber der umgebenden Haut, weich maskiert),
  gezeichnete Schraffur unter dem Auge
  ebenfalls halbiert. Ganz entfernen ist nicht gewollt: die Partie trägt deutlich
  zur Echtheit der Augen bei.
- Weiße Flecken über den Haaren an beiden äußeren Brauenenden: die Brauenmasken
  (runde Linienenden + weicher Rand) rissen Stücke aus den Strähnen. Behoben mit
  festen Schutzzonen je Strähne, in die weder Maske noch weicher Rand reichen.
  Nebenwirkung: links bleibt ein kurzes Stück des ursprünglichen Brauenendes an
  der Strähne stehen; es bewegt sich nicht mit der gezeichneten Braue mit.
  Die Schutzzonen sind an diese Vorlage gebunden (Koordinaten im Skript).

**Mundwinkel bei Freude (Messung 01.10.2026):** Relativ zur Mundmitte heben sich
die Winkel beim Avatar bereits wie auf den Fotos (Avatar 0,24, Vorlage 0,20,
Fotos 0,20–0,33 der halben Mundbreite). Relativ zu den Augen steigen die Winkel
auf den Fotos aber um ca. 0,12–0,14 Augenabstände gegenüber Neutral (Person 3
und Collage 4; Person 2 0,03–0,12, Kopfneigung stört), beim Avatar nur um 0,06.
→ `mouth_curve` Freude 30 → 40 (Anstieg jetzt ca. 0,08). Weiter nach oben wäre
durch die Messung gedeckt, gewünscht war „ein klein bisschen“.

**Brauen Überraschung vs. Angst (FACS):** Überraschung AU1+2 = ganze Braue hoch
und gewölbt; Angst AU1+2+4 = innen hoch, flach und gespannt. Neuer Kanal
`brow_arch`. Überraschung: Brauen −30/−28, Wölbung −7. Angst: −20/+4, Wölbung +5.

**Brauen bei Freude — bewusst abweichend von FACS (Meister, 01.10.2026):** Beim
Duchenne-Lächeln (AU6 + AU12) senkt sich die Braue außen leicht, innen bleibt sie
neutral. Der Avatar hebt die Brauen bei Freude leicht an (−6). Nach Sichtprüfung
bleibt das so („sieht gut aus“). Nicht umgesetzt: Krähenfüße am äußeren
Augenwinkel als abgeleitetes Merkmal — bei Bedarf wie die Zornesfalten aus
`eye_arc` ableitbar.

### 13.10 Brauen und Wimpern näher am Original (01.10.2026)

Hinweis Meister: Brauen im Original fülliger, Wimpern betonen die Augen intensiver.
- Brauen: statt paralleler Haarstriche eine weiche, gefüllte Fläche in drei
  Deckkraftstufen, innen voll, am Scheitel am breitesten, Ende spitz auslaufend;
  darüber 190 feine Haarstriche in Wuchsrichtung (innen steiler). Breite 12/14 → 16/18.
- Wimpern: dunkler, nach außen breiterer Wimpernkranz mit kurzem Schwung über den
  äußeren Augenwinkel; statt 28 dünner Striche 18 kräftige, gebogene, sich
  verjüngende Wimpern, paarweise gebüschelt, nach außen länger.
- Unterwimpern: weniger, unregelmäßig, nur äußere Hälfte deutlich.

- Korrektur Wimpernschwung (Hinweis Meister): Spitzen hingen nach unten. Jetzt
  Bogen symmetrisch um die Wimpernrichtung, Start flacher nach außen, Spitze nach
  oben gebogen; Biegung innen fast null, außen stark (k = 0,08 … 0,40 rad).
- Schattierung außen (Hinweis Meister: im Original außen eine Spur dunkler):
  Augenweiß mit Verlauf zum äußeren Winkel (bis 55 % Grafit-Deckkraft), weicher
  Schatten um den äußeren Augenwinkel, neun zusätzliche kurze Wimpern im äußeren
  Drittel, die zu einer dunklen Masse verschmelzen.
- Unterwimpern kräftiger (Hinweis Meister): 11 Wimpern, nach außen länger und
  dichter, leicht gebogen, Lidkante außen dunkler.
- Fehler behoben: Das Auslassen einzelner Unterwimpern hing am Zufallsgenerator,
  der für das Linien-Zittern ca. 9× pro Sekunde neu gesetzt wird → Unterwimpern
  flackerten. Jetzt festes Auslassmuster. Regel für den Client: Der Zufall des
  Linien-Zitterns darf nur Strichlagen verwackeln, nie über Sichtbarkeit oder
  Anzahl von Elementen entscheiden.
- Grafitschatten an den Augenrändern nach Markierung Meister: rauchige Fläche um
  den äußeren Augenwinkel (Verlauf + 46 Schraffurstriche) und dunkles Band unter
  dem Unterlid in der äußeren Hälfte (4 Lagen + 30 Striche). Kalibriert per
  Helligkeitsmessung gegen das Original (Grauwert 0–255):
  äußerer Winkel 114 / Avatar 119, unter dem Lid 156 / 147.
- Iris dunkler und gemasert: 110 dunkle radiale Fasern, 40 helle Zwischenstreifen,
  8 Krypten, Krausenring um die Pupille, dunklerer Limbusring. Grauwert Iris
  Original 64 / Avatar 82 (vorher heller).
- Feste Positionen über eine Hash-Funktion statt Zufall (Regel aus der
  Unterwimpern-Korrektur): Fasern und Schraffuren verwackeln, springen aber nicht.
- Lidfalte näher am Lid (Hinweis Meister 02.10.2026): Abstand Falte–Oberlid im
  Original ca. 12 px, im Avatar vorher ca. 18–25 px. Falte jetzt als Versatz des
  Oberlids (`CREASE_GAP` 14 px Mitte, zu den Winkeln auslaufend, schwere Lider
  −4 px) statt eigener Kurve; nach den Wimpern gezeichnet, damit die Wimpern sie
  kreuzen und sie sichtbar bleibt (bei 10 px verschwand sie im Wimpernkranz).
- Wimpern verklebt (Hinweis Meister 02.10.2026): statt 18 Einzelwimpern 11 Büschel
  aus je 3 Wimpern mit getrennten Wurzeln, die zur gemeinsamen Spitze zusammenlaufen;
  an der Wurzel kräftig, Spitze dünn. Längen und Lage fest über Hash. Äußere
  Verdichtung von 9 auf 5 kräftigere Wimpern reduziert. Ein erster Versuch mit
  breiteren Strichen wirkte wie Wimperntusche-Zacken und wurde verschlankt.
- Zur Nase hin feiner (Hinweis Meister 02.10.2026): Wimpernbüschel beginnen erst bei
  27 % der Lidlänge (vorher 14 %), Strichstärke innen halbiert und nach außen
  ansteigend, innerstes Büschel kürzer. Wimpernkranz innen nur eine feine Linie,
  kräftige Lagen erst ab dem ersten Fünftel.
- Unterwimpern außen länger (Hinweis Meister 02.10.2026): Länge 4 → 18 px von innen
  nach außen (vorher 4 → 13), stärker zum Augenwinkel hin ansteigend; Länge fest
  über Hash statt Zufall.
- Obere Wimpern innen 10 % weniger (11 → 10 Büschel, Beginn bei 34 % statt 27 %),
  außen kräftiger: dunkler keilförmiger Wimpernrand ab 35 % der Lidlänge, zum
  äußeren Winkel bis ca. 6 px breit (Hinweis Meister 02.10.2026). Fehler beim
  ersten Entwurf: zwei getrennte Teilpfade schlossen sich quer über das Auge;
  jetzt ein zusammenhängender Pfad.
- Lidfalte parallel zur Lidlinie (Hinweis Meister 02.10.2026): Abstandsprofil
  sin^0,25 statt sin^0,8, d. h. über fast die ganze Länge gleicher Abstand, nur an
  den Enden kurz auslaufend. Darunter drei weiche Schattenlagen zum Lid hin,
  Faltenlinie etwas dunkler.

### 13.11 Mund ans Original angeglichen (02.10.2026)

- Zähne: Schneidezähne breiter (27/21/18 px statt 22/17/15), Kanten runder,
  deutlich weißer (Ton 250 statt 238), schwächerer Wurzelschatten, dunkle Fugen
  zwischen den Zähnen, schwächerer Lippenschatten auf den Zähnen.
- Mundraum dunkler, Zunge größer und heller mit Mittellinie und Struktur
  (sichtbar erst bei größerer Öffnung, z. B. Schreien, Weinen).
- Lippen: senkrechte Rillen ersetzt durch feine Schraffur entlang der Lippe
  (130 Striche je Lippe, feste Positionen), zur Mundlinie und zu den Winkeln
  dunkler; Grundton kräftiger; Konturen dunkler; Unterlippe zur Unterkante hin
  dunkler, weiches Glanzlicht in der Mitte.
- Mundwinkel als tief dunkle Keile.
- Offen: Die Öffnung bei Freude bleibt bei den gemessenen Werten (13.7) und ist
  damit kleiner als in der lachenden Vorlage.
- Verhältnis Ober- zu Unterlippe (Hinweis Meister 02.10.2026): Oberlippe
  19 − 0,12 · `mouth_curve` (wird beim Lächeln gestreckt und dünner), Unterlippe
  23 − 0,03 · `mouth_curve`. Mitte neutral ca. 1 : 1,7, bei Freude ca. 1 : 2,1
  (Original lachend ca. 1 : 2; Fotos neutral 1 : 1,3–1,6).
- Unterlippe voller (Hinweis Meister 02.10.2026): Grunddicke 23 → 28.
- Zahnform mit Bögen am Zahnfleischrand (Hinweis Meister): jeder Zahn oben eigener
  Bogen, dazwischen kleine dunkle Zwickel; Ecken an der Schneidekante gerundet,
  Schneidekante leicht gewölbt. Zahnfleischrand 9 px tiefer, Zahnhöhen angepasst.
  Erster Versuch mit tiefen Zwickeln und großen Radien sah aus wie Kiesel und
  wurde verworfen.
- Beim Lächeln hebt sich die Oberlippe (AU10/AU12: Kontrollpunkt −0,3 · `mouth_curve`
  bei offenem Mund) und legt die Zahnbögen frei; bei negativer Mundkrümmung
  (Wut, Trauer, Angst) keine Änderung.
- Zahnfleisch heller (Hinweis Meister 02.10.2026): eigenes Band entlang des
  oberen Zahnbogens (Grauwert ca. 118 → 182 zum Zahnrand hin) statt des dunklen
  Mundraums hinter den Zahnbögen.
- Zahngrößen einzeln nach Original (Hinweis Meister 02.10.2026: zu gleichmäßig).
  Gemessen (Vorlagen-Pixel, Breite / sichtbare Höhe): mittlere Schneidezähne
  26–31 / ca. 35, seitliche 17–21 / ca. 22, Eckzähne 15–17 / ca. 17, Backenzähne
  13–15 / 13 → 10. Avatar oben jetzt 28/31, 19/23, 16/22, 14/16, 13/13, 12/11, 11/9;
  Eckzahn leicht spitz; feste Abweichung je Zahn und Seite (±4 % Breite, ±5 % Höhe),
  da echte Zähne nicht spiegelgleich sind.
- Mittlere Schneidezähne 4 px kürzer (31 → 27) nach Sichtprüfung Meister.
- Untere Zahnreihe als Gegenstück zur oberen (Hinweis Meister 02.10.2026: zu breit
  in der Bissbreite, Zähne zu schmal, nicht dem Kiefer nachgebogen):
  - Zähne auf einem Kreisbogen (Radius 85 px), von vorn projiziert: zur Seite
    perspektivisch schmaler, Reihe insgesamt schmaler als die obere.
  - Kanten steigen zu den Seiten leicht an (0,18 · Bogenhöhe); erster Versuch mit
    0,4 ließ die Seitenzähne hochklettern.
  - Zähne breiter (17–18 px vorn) und länger, damit sie hinter der Unterlippe
    nicht abreißen; untere Schneidekanten gerade statt gerundet (gerundet wirkten
    sie wie eine Pillenreihe).
  - Bei negativer Mundkrümmung und offenem Mund zieht die Unterlippe nach unten
    (AU15/AU16) und legt die untere Reihe frei (Weinen).
- Korrektur Weinmund (Hinweis Meister 02.10.2026: unten kein breites Aufziehen
  ohne Hilfsmittel möglich). Zug der Unterlippe von 0,9 auf 0,25 · |`mouth_curve`|
  reduziert; Trauer intensiv `mo` 34 → 28, `mw` 106 → 96. Untere Zähne nur noch
  als schmaler Streifen hinter der Unterlippe sichtbar. Anatomie: AU16 senkt die
  Unterlippe nur begrenzt; AU12 (oben) hat deutlich mehr Hub.
- Fleischiges Polster an den Mundwinkeln (Hinweis Meister 02.10.2026): Die dunkle
  Öffnung lief spitz bis in den Lippenwinkel und zeigte seitlich zu viel Zähne.
  Jetzt endet sie um 12 + 0,35 · `mouth_open` px (max. 30 % der halben Mundbreite)
  vor dem Winkel, mit gerundeten Ecken; dazwischen eine schattierte Lippenfläche
  und eine kurze Falte vom Lippenwinkel ins Polster.
- Polster-Schattierung korrigiert (Hinweis Meister: heller Ring innen, dunkle Lippen
  außen wirkte unnatürlich): Verlauf jetzt vom Lippenton am Winkel zur Öffnung hin
  dunkler (Schatten in den Mund), Schraffur wie auf den Lippen; dunkle Striche an
  den Lippenwinkeln nur noch bei geschlossenem Mund.
- Polster heller an die Lippen angeglichen (Grauwert 196 → 150 zur Öffnung statt 150 → 92), Schraffur schwächer (Hinweis Meister 02.10.2026).
- Angst: Augenöffnung `eye_open` 1,30 → 1,12 (Hinweis Meister 02.10.2026). Erster Schritt auf 1,21
  (7 % des Werts) änderte die Lidhöhe nur um ca. 2 px und war nicht sichtbar; der
  Eindruck „aufgerissen“ hängt am Weiß über der Iris, nicht an der Gesamthöhe.
- Lachfalten 14 px tiefer (Hinweis Meister 02.10.2026).
