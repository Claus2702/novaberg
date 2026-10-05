# Novaberg — Emotions-Avatar: Ausarbeitung

**Teil von:** `novaberg-avatar_k.md` — dort Absicht, Kopfblock und die Tabelle „§ → Datei“
**Stand:** 05.10.2026, 00:27 UTC (§4, §13.1, §13.18 neu, §15.2, §15.3, §17.1, §17.9: der Client zieht nach — L1′ plant wie die nachgestellte Referenz, das Kopfziel `head_yaw` neben dem Gesicht; L2′a Auge und Kopffeder; L2′b/L2′c die Kopfdrehung im Bild über eine Zwischenfläche, nur die verschobenen Dreiecke). Davor 04.10.2026, 21:05 UTC (§4, §17.1, §17.3–§17.7, §17.9: der Leerlauf auf dem Stand der nachgestellten Referenz L0′a–L0′c — Nachdenken abgewandt, Einatmen, Antwort ohne Sprung, Pupille, Blick an der Iris, Lidschläge, Kopfdrehung). Davor 04.10.2026, 15:35 UTC (§17.8: L4 gebaut). Davor 04.10.2026, 14:30 UTC (§14.2, §15.4, §17.2, §17.8: die Antwort zeigt die Wahrnehmung der Antwort selbst, `emotion`/`arousal`). Davor 04.10.2026, 11:28 UTC (§17.10: der Auffangzweig nach L3). Davor 04.10.2026, 10:30 UTC (§17.10 neu: der Weg der Arbeitszyklen im Client, entschieden; §17.2: Absender, Sendefehler, Öffnen des Panels; §17.8: Verteiler entschieden, `pixie_auftrag` mit Thema für die Statuszeile). Davor 03.10.2026, 19:07 UTC (§17.3, §17.8, §17.9: die Puppe lebt aus dem Leerlauf, L2). Davor 03.10.2026, 13:40 UTC (§17: der Generator folgt dem Ereignismodell des Clients, §17.1, §17.3, §17.6, §17.8, §17.9). Davor 03.10.2026 (§17 neu: der Leerlauf). Davor 02.10.2026
**Inhalt:** wie die Absicht ausgearbeitet ist — Darstellungsstil, Parameterraum `FaceState`, Emotions-Mapping, Intensität und Mischung, Übergangsmodell, Schichten, Integration im Client (§3–§9); aus dem Prototyp die Pipeline der Figur, die Alternative zur Vorlage, das bewegliche Kinn, die Sprechschicht, die Muskelkanäle des Mundes und die Einzellaute (§13 in Teilen); dazu der Datenvertrag mit dem Server (§14), die Portierung nach GTK4 und Cairo (§15) und der Leerlauf mit seinen vier Denkweisen (§17).

---

## 3. Darstellungsstil

Im Prototyp erprobt (HTML, `labor/avatar/index.html`):

- **Line Boil:** Jede Linie wird mehrmals pro Sekunde (ca. 9×) mit kleinem
  Zufallsversatz neu erzeugt. Klassischer Trick handgezeichneter Animation.
- **Doppelstrich:** Jede Linie wird zweimal gezeichnet — einmal kräftig, einmal
  dünn mit geringer Deckkraft. Ergibt Bleistiftanmutung.
- **Schraffur** als Schatten an einer Gesichtsseite.
- Linien als geglättete Polylinien (quadratische Kurven über Mittelpunkte).

**Determinismus:** Der Zufall für den Line Boil wird aus einem Seed erzeugt, der
aus einem Zeit-Bucket abgeleitet ist (z. B. `floor(t / 0.11 s)`). Damit ist die
Zeichnung für einen Zeitpunkt reproduzierbar und testbar. Ist der Boil
abgeschaltet, gilt ein fester Seed.

---

## 4. Parameterraum `FaceState`

Das Gesicht wird vollständig durch einen Vektor kontinuierlicher Parameter
beschrieben. **Es gibt keine Schalter** — auch Merkmale wie Träne oder Röte
sind Kanäle mit Wert 0..1. Nur so ist jeder Übergang interpolierbar.

| Kanal | Bereich | Bedeutung |
|---|---|---|
| `brow_left_inner`, `brow_left_outer` | −1..1 | Höhe der linken Braue innen/außen (negativ = hoch) |
| `brow_right_inner`, `brow_right_outer` | −1..1 | wie links, rechts getrennt für Asymmetrie |
| `brow_arch` | −1..1 | Brauenwölbung; negativ = Scheitel höher, runder Bogen (Überraschung), positiv = flach gespannt (Angst) |
| `eye_open` | 0..1.5 | Augenöffnung, 1 = neutral |
| `eye_arc` | 0..1 | Überblendung zu „Lachaugen“-Bögen |
| `lid_upper` | 0..1 | hängendes Oberlid |
| `lid_lower` | 0..1 | angespanntes Unterlid |
| `gaze_x`, `gaze_y` | −1..1 | Blickrichtung |
| `pupil_size` | 0.5..1.2 | Pupillengröße |
| `mouth_curve` | −1..1 | Mundkrümmung (positiv = Lächeln) |
| `mouth_open` | 0..1 | Lippenöffnung (wie weit die Lippen auseinandergehen) |
| `jaw` | 0..1 | Kieferöffnung; Unterkieferzähne folgen nur diesem Kanal. Ohne Vorgabe folgt der Kiefer der Lippenöffnung (Faktor 0,75) |
| `mouth_width` | 0.5..1.3 | Mundbreite |
| `mouth_asym` | −1..1 | Mundwinkel-Asymmetrie |
| `nose_wrinkle` | 0..1 | Nasenrümpfen |
| `blush` | 0..1 | Röte/Wangenschraffur |
| `tear` | 0..1 | Träne |
| `sweat` | 0..1 | Schweißtropfen |
| `yaw` | −15..15 | Kopfdrehung um die Hochachse in Grad, plus = nach rechts aus Sicht des Betrachters wie `gaze_x`; eigene, träge Feder (ω 3,5); die Zeichnung wirft jenseits von ±15° (seit 04.10.2026, §17.3). → **Im Client kein Feld von `FaceState`** (seit L1′, 05.10.2026): Die Leerlauf-Logik liefert das Kopfziel als `IdleFrame.head_yaw` neben dem Gesicht, die Pose trägt den Stand der Kopffeder als `Pose.head_yaw` (§15.2, §17.9) |

Der Neutralzustand ist ein fester `FaceState`, gegen den alle anderen definiert werden.

**Ergänzt am 02.10.2026 (W3):** Zum Parameterraum gehören seit §13.13 die Muskelkanäle des Mundes, je 0..1 — `au10`, `au12`, `au15`, `au16`, `au20` je Seite getrennt (`L`/`R`), dazu `au17`, `au18`, `au22`, `au23`, `au24`, `au28`. Die Sprechkanäle aus §13.12 sind darin aufgegangen: `round` ist kein eigener Kanal mehr, sondern folgt aus AU18 und AU22; `press` wirkt als AU24, `fv` als AU28 (Prototyp `labor/avatar/index.html`, gelesen am 02.10.2026).

**Lippen und Kiefer getrennt (v0.5):** Damit sind Mundformen möglich, bei denen die
Lippen offen sind, der Kiefer aber geschlossen bleibt: zusammengebissene Zähne
(Frustration, `mouth_open` 12, `jaw` 0) und die Angst-Grimasse mit beiden
Zahnreihen (`mouth_open` 22, `jaw` 6). Bei Schreien und Weinen folgt der Kiefer
der Lippenöffnung.

### 4.1 Abgeleitete Merkmale (kein eigener Kanal)

Aus der mittleren inneren Brauenhöhe werden Falten abgeleitet:
- innen gesenkt (Ärger, Wut) → senkrechte Zornesfalten zwischen den Brauen,
  Stärke ab Brauenwert 8, voll bei 24;
- innen angehoben (Trauer, Angst) → drei waagrechte Stirnfalten in der Mitte,
  Stärke ab −12, voll bei −26.

Die Brauen tragen die Unterscheidung der negativen Sektoren, weil der Mund dort
oft ähnlich ist (Befund aus den Fotos und gängigen Zeichenkonventionen):
Ärger = V-Form (innen 24/28 gesenkt, außen angehoben), Trauer = innen stark
angehoben (−20/−26), Enttäuschung = flach gesenkt (8) mit schweren Lidern.

---

## 5. Emotions-Mapping: 8 Sektor-Gesichter

### 5.1 Das Emotionsmodell im System (Doku-Stand)

Laut `novaberg-ei-plutchik.md` §3: 16 kanonische Emotionen + `neutral`,
angeordnet als Oktagon mit 8 Sektoren und je einer intensiven und einer
moderaten Emotion. Intensiv und moderat unterscheiden sich im Arousal.

| Sektor | Name | Intensiv | Moderat | Gegenpol |
|---|---|---|---|---|
| 1 | Freude | begeisterung | freude | 5 |
| 2 | Zuversicht | dankbarkeit | zufriedenheit | 6 |
| 3 | Angst | stress | unsicherheit | 7 |
| 4 | Überraschung | ueberrascht | verwundert | 8 |
| 5 | Trauer | verzweiflung | traurigkeit | 1 |
| 6 | Enttäuschung | frustration | enttaeuschung | 2 |
| 7 | Ärger | wut | aerger | 3 |
| 8 | Neugier | hoffnung | neugierig | 4 |

Besonderheit gegenüber Plutchik: Sektor 6 ist Enttäuschung statt Ekel.
Dyaden (Liebe, Ehrfurcht, …) sind **keine** eigenen Einträge; sie liegen
zwischen benachbarten Sektoren.

### 5.2 Konsequenz für den Avatar

Der Avatar braucht **nicht 16 Keyframes, sondern 8 Sektor-Gesichter + Neutral**.

- Jeder Sektor bekommt einen Ziel-`FaceState` für volle Ausprägung (Arousal 1.0).
- Intensiv vs. moderat ist kein eigenes Gesicht, sondern dieselbe Achse bei
  unterschiedlichem Arousal (Abschnitt 6.1).
- Zwischenformen (z. B. Ehrfurcht zwischen Angst und Überraschung) entstehen
  automatisch durch Mischung benachbarter Sektoren (Abschnitt 6.2).

Kalibrierung der 8 Sektor-Gesichter zunächst aus dem Prototyp —
**nicht validiert**, nur Ausgangspunkt. ~~Sektor 6 (Enttäuschung) ist dort nicht
enthalten und muss neu entworfen werden~~ (hängende Mundwinkel, gesenkter Blick,
leicht verengte Augen — Richtung „Vertrauen gebrochen“, nicht „Ekel“).
→ **Im Prototyp entworfen** (W2, aufgelöst am 02.10.2026, siehe `novaberg-avatar_e.md`, Befunde der Aufteilung): Mund nach Messung `novaberg-avatar_m.md` §13.7, Brauen flach gesenkt mit schweren Lidern (§4.1), Oberlippenheber AU10 einseitig betont (§13.13).

---

## 6. Intensität und Mischung

### 6.1 Intensität aus Arousal

Das Arousal (0..1) der jeweiligen Emotion skaliert die Abweichung vom Neutralzustand:

```
face(sektor, arousal) = neutral + arousal · (target(sektor) − neutral)
```

- Arousal 0 ergibt exakt Neutral — deckungsgleich mit dem neutralen Zentrum
  des Oktagons (Doku §4.1).

**Stand v0.4 — zwei Schlüsselbilder je Sektor (Entscheidung O11, Meister 01.10.2026):**
Die Form eines Ausdrucks hängt am Arousal. Jeder Sektor hat ein Schlüsselbild für
die moderate kanonische Emotion (bei Arousal `MOD_AROUSAL` = 0,6) und eines für die
intensive (bei 1,0). Interpolation stückweise linear: Neutral → moderat → intensiv.
Kanäle ohne eigenes moderates Schlüsselbild liegen linear zwischen Neutral und intensiv.

**Nachgetragen am 02.10.2026 (W11):** Der Prototyp führt ein moderates Schlüsselbild für drei Sektoren — Trauer, Enttäuschung und Ärger —, die Tabelle nannte zwei. Die Werte der Zeile Enttäuschung stammen aus dem Prototyp (`labor/avatar/index.html`, `SECTORS`, gelesen am 02.10.2026).

| Sektor | moderat (≤ 0,6) | intensiv (→ 1,0) |
|---|---|---|
| 5 Trauer | traurigkeit: Mund geschlossen, Winkel unten, schmaler (`mw` 84) | verzweiflung: Weinen, offen (~~`mo` 34~~ → `mo` 28), breit (~~`mw` 106~~ → `mw` 96), Träne — korrigiert in `novaberg-avatar_b.md` §13.11 (W6) |
| 6 Enttäuschung | enttaeuschung: geschlossen (`mw` 80, `mo` 0) — nachgetragen (W11) | frustration: `mw` 84, `mo` 12 — nachgetragen (W11) |
| 7 Ärger | aerger: Lippen gepresst, geschlossen (`mw` 68) | wut: Schreien, offen (`mo` 70), `mw` 76 |

Die Schwelle 0,6 entspricht der Wahl der kanonischen Emotion im Prototyp
(intensiv ab Arousal 0,6). Offen: ob das zur Grenze intensiv/moderat in der
Perzeption passt — gegen den Code zu prüfen.
→ **Geprüft am 02.10.2026:** Der Server kennt keine solche Grenze; Name und Arousal werden unabhängig gesetzt. Es gilt §5.2: Das Arousal bestimmt die Ausprägung, der Name nur den Sektor (§14.1).

Bei offenem Mund und negativer Mundkrümmung wird die Kontur kastenförmig
(Exponent der Konturkurve 2 → bis 5) und die Mundwinkel sinken tiefer — sonst
liest sich Weinen/Schreien als Grinsen.
- Die Intensitätsstufen sind Punkte auf derselben Achse, keine eigenen Keyframes.
- Offen: ob eine nichtlineare Kennlinie nötig ist, damit moderate Emotionen
  sichtbar genug sind (O6).
  → **Teilweise beantwortet** durch O11 (oben): stückweise linear über zwei Schlüsselbilder. Offen bleibt die Kennlinie für Sektoren und Kanäle ohne moderates Schlüsselbild (W5).

### 6.2 Mischung aus dem Emotionsverlauf

Das System liefert laut Doku einen gewichteten Verlauf (Emotion, Gewicht, Arousal),
bereits sektorabhängig normalisiert, die Dominante mit Gewicht 1.0.
Daraus ergibt sich:

```
face = neutral + Σ_i  w_i · arousal_i · (target(sektor(e_i)) − neutral)  /  Σ_i w_i
```

anschließend jeder Kanal auf seinen Bereich begrenzt.

**Der Avatar normalisiert nicht erneut.** Die Frage, ob gegensätzliche
Emotionen koexistieren dürfen, beantwortet bereits die Sektor-Normalisierung
im Emotionsmodell (Nachbarn gestützt, Gegenpaare bei hohem Arousal verdrängt).
Der Avatar stellt dar, was ankommt.

Offen: ob der Avatar den vollen Verlauf mischt oder nur die Dominante zeigt (O7).

### 6.3 Emotionskonflikt

Laut Dual-Emotion-Konzept §4.4 existiert ein Flag `nova_emotion_konflikt`
(Empathie-Vektor und eigener Zustand zeigen gegeneinander).
Mögliche Darstellung: Asymmetrie-Kanäle (`mouth_asym`, getrennte Brauen),
also ein sichtbar ambivalentes Gesicht. Entscheidung offen (O8).

---

## 7. Übergangsmodell

### 7.1 Zeitbasiert, nicht schrittbasiert

Der Animator beantwortet die Frage: *Welcher `FaceState` gilt zum Zeitpunkt t?*
Der Renderer fragt so oft, wie er zeichnet.

- Keine feste Anzahl Zwischenschritte (z. B. „10 Aufrufe à 0,1 s“).
- Die Framerate ist frei wählbar, ohne die Übergangslogik anzufassen.
- Begründung: 10 fps genügen für den Emotionsübergang, Blinzeln und
  Mundbewegung wirken bei 10 fps aber abgehackt.

### 7.2 Unterbrechung

Ein neues Ziel darf jederzeit eintreffen, auch mitten im Übergang.
**Ausgangspunkt ist immer der aktuell sichtbare Zustand**, nicht das alte Ziel
und nicht die alte Ausgangsemotion. Sonst springt das Gesicht.

### 7.3 Kritisch gedämpfte Feder je Kanal

Jeder Kanal folgt seinem Ziel wie eine kritisch gedämpfte Feder. Vorteile:

- Unterbrechung ist automatisch stetig — Position **und** Geschwindigkeit bleiben erhalten.
- Kein Überschwingen.
- Die Übergangsdauer wird über einen einzigen Parameter `ω` gesteuert.

Exakte (framerate-unabhängige) Aktualisierung pro Kanal, mit
`d = x − ziel`, Geschwindigkeit `v`, Zeitschritt `Δt`:

```
e      = exp(−ω · Δt)
tmp    = (v + ω · d) · Δt
d_neu  = (d + tmp) · e
v_neu  = (v − ω · tmp) · e
x_neu  = ziel + d_neu
```

Richtwert: `ω ≈ 5 /s` → rund 95 % des Wegs nach etwa 1 s.
Kalibrierung per Sichtprüfung, nicht per Annahme.

### 7.4 Kanalversatz

Echte Mimik ändert sich nicht synchron. Vorschlag:

- Brauen und Augen übernehmen ein neues Ziel sofort.
- Mundkanäle übernehmen es mit 100–200 ms Verzögerung.

---

## 8. Schichtenmodell

Pro Frame werden drei unabhängige Schichten zu einem `FaceState` kombiniert:

| Schicht | Inhalt | Quelle |
|---|---|---|
| 1 Emotion | Federübergang zum Ziel-`FaceState` | Novas Emotionszustand |
| 2 Lebendigkeit | Blinzeln (zufällige Abstände), Atmen, Line Boil | lokal im Avatar |
| 3 Sprechen | ~~Mundöffnung~~ → Öffnung, Kiefer, Breite und Muskelkanäle des Mundes (W10, §13.12, §13.13) | Audiopegel oder Viseme — Quelle offen (O9); im Prototyp Lautzeiten aus dem Text (§13.12, §13.14) |

Reihenfolge der Kombination:

1. Schicht 1 liefert den Basiszustand.
2. Schicht 2 moduliert `eye_open` (Blinzeln) multiplikativ und verschiebt die Figur (Atmen).
3. ~~Schicht 3 addiert auf `mouth_open`, begrenzt auf den Kanalbereich.~~
   → Schicht 3 blendet weich ein und ~~legt Öffnung, Kiefer und Muskelkanäle additiv auf die Emotion; die Breite wirkt als Faktor auf die Emotionsbreite~~ → überblendet Öffnung und Kiefer zwischen Emotion und Sprache und addiert die Muskelkanäle; die Breite folgt aus ihnen (W10, §13.12, §13.13; berichtigt nach dem Prototyp, P4).

Schicht 2 und 3 verändern nie das Emotionsziel.

---

## 9. Integration im GTK4-Client

- **Datenquelle (Doku-Stand):** Laut Dual-Emotion-Konzept §8.3 enthält
  `GespraechAntwort` die Felder `nova_emotion`, `nova_arousal`,
  `nova_emotions_vektor`. Ob der Client sie empfängt und ob der volle
  Verlauf (`nova_emotions_verlauf`) transportiert wird: offen (O2, O3).
- **Zeichnen:** `Gtk.DrawingArea` mit `set_draw_func`. Die Draw-Funktion ist
  zustandslos: `(cairo_context, breite, höhe, face_state, boil_seed)` → Zeichnung.
- **Takt:** `add_tick_callback` am Widget. Der Frame-Clock liefert die Zeit;
  daraus werden `Δt` für die Federn und der Boil-Seed abgeleitet, danach
  `queue_draw()`.
- **Ruhezustand:** Auch ohne Emotionswechsel läuft der Takt (Line Boil, Atmen).
  CPU-Last ist zu messen; ggf. Boil-Rate reduzieren, wenn das Panel nicht sichtbar ist.
- **Panel:** eigener Panel-Typ in der bestehenden Panel-Architektur.
  Registrierung und UNIQUE/CATEGORY: offen (O4).
- **Bezug zum Emotions-Panel:** Das Dual-Radar (AP 8 im Dual-Emotion-Konzept)
  ist laut Doku offen. Avatar und Radar teilen dieselbe Datenquelle und sollten
  sie gemeinsam erschließen.

---

## 13. Figur aus Vorlage (Prototyp, 29.09.2026)

**Vorlage:** Bleistiftzeichnung von Nova, 1254 × 1254 px, lachend, Kopfneigung ca. 9°.
Die Kopfneigung wurde aus der Lage beider Augen und beider Mundwinkel abgelesen
(beide ca. 8,5–9,5°). Alle Merkmale werden in einem um diesen Winkel gedrehten
lokalen Koordinatensystem gezeichnet.

### 13.1 Pipeline

1. **Merkmale aus der Vorlage entfernen** — Stand v0.5: enge Masken (Auge als
   gedrehte Ellipse nur bis zu den Wimpernspitzen, Braue als Linienzug). Die
   großen Ellipsen aus v0.3 reichten links in die Haarsträhne und die beschattete
   Gesichtskante und überdeckten sie hell (Hinweis Meister, 01.10.2026). Füllung
   am Rand aus der Umgebung (feine Striche per morphologischem Schließen entfernt,
   flächige Schatten bleiben), zur Maskenmitte hin helle Hautfüllung.
   Ursprüngliche Fassung: Augen samt Brauen, Mund und die
   Lachfalten werden über Ellipsenmasken ausgeschnitten. Füllung = lokaler Median
   der Umgebung (Masken vorher ausgeblendet) plus prozedurale, diagonal
   gerichtete Bleistiftkörnung mit der Streuung einer echten Wangenpartie
   (σ ≈ 2,2 Grauwerte), weicher Übergang an den Maskenrändern.
2. **Statischer Rest bleibt Rasterbild:** Haare, Kontur, Nase, Ohrringe, Hals.
   Line Boil auf dem Rasterbild über drei Varianten mit leichter, glatter
   Verzerrung (max. ca. 3 px bei 900 px), die im Boil-Takt wechseln.
3. **Mimische Merkmale parametrisch gezeichnet:** Brauen (Haarstriche entlang
   einer Kurve durch innen / Scheitel / außen), Augen (Lidkurven, Iris mit Clip
   auf die Lidöffnung, Wimpern, Lidfalte), Mund (Mundlinie bzw. Öffnung, Lippen
   als Versatzkurven mit Amorbogen-Profil, Zähne, Lachfalten ab `mouth_curve` > 10).
   Positionen stammen aus der Vorlage (Augen- und Mundwinkel, Brauenpunkte).
   - **Auge** (seit 04.10.2026 im Prototyp, seit 05.10.2026 im Client, L2′a): Der Blick rückt die Iris um 0,5·hw je Einheit quer und 0,26·hw längs (hw = halbe Augenbreite; bis dahin 0,3 und 0,16 — ein Blick von 0,25 zur Seite rückte sie nur 0,075·hw und las sich noch als Blickkontakt). Unter der Öffnung 0,06 (bis dahin 0,12) ist das Auge geschlossen gezeichnet: eine Lidlinie in sieben Strichen (1,2 bis 5 px, nach außen kräftiger) und 8 Büschel zu je 3 Wimpern — vorher ein dünner Strich, schwächer als die Wimpernlinie des offenen Auges.
4. **Animation:** unverändert nach Abschnitt 7 und 8 (Feder, Kanalversatz, Blinzeln, Atmen).
5. **Zähne als feste Kieferebenen** (Vorgabe Meister, 29.09.2026): Die Zähne
   skalieren und verformen sich nicht mit dem Mund.
   - Oberkiefer: fest am Kopf, feste Zahnbreiten und -höhen, Zahnbogen zu den Seiten ansteigend.
   - Unterkiefer: gleiche Bauart, verschiebt sich nur senkrecht um die
     Kieferöffnung (`jaw = mouth_open · Faktor`).
   - Die Lippen bilden darüber die Öffnung (Clip) und legen mehr oder weniger
     von den Zähnen frei. Ein schmaler Mund zeigt nur die Schneidezähne, ein
     breites Lachen auch die hinteren, abgedunkelten Zähne.
   - Reihenfolge: Mundraum, Zunge, Unterkieferzähne, Oberkieferzähne (Überbiss), Lippenschatten, Lippen.

### 13.3 Alternative für die Vorlage

Die entfernten Bereiche sind der schwächste Teil. Sauberer ist eine zweite
Vorlage derselben Figur **ohne** Augen, Brauen und Mund (nur Gesichtsfläche mit
Schraffur), gezeichnet oder generiert im selben Stil. Dann entfällt das
Ausschneiden vollständig. Offen, ob sich eine solche Vorlage stilgleich erzeugen lässt.

### 13.9 Proportionen und bewegliches Kinn (01.10.2026)

**Befund (Messung, Sichtprüfung Meister):** Augen liegen wie im Original (Pupillen,
Lider ±3 px). Ursache des „großen Kinns“: Die Vorlage zeigt Nova lachend mit
abgesenktem Unterkiefer (ca. 30 px); das Kinn ist Teil des statischen Grundbilds
und blieb auch bei geschlossenem Mund unten. Gemessen entlang der Gesichtsachse
(Neigung 9° herausgerechnet):

| Maß | vorher | nachher | Faustregel |
|---|---|---|---|
| unteres / mittleres Gesichtsdrittel | ×1,31 | ×1,09 | ×1,0–1,1 |
| Nase–Mund : Mund–Kinn | 27 : 73 | 31 : 69 | 33 : 67 |

**Umsetzung:** Gitterverzerrung des Grundbilds (13 × 13 Zellen, 338 Dreiecke) im
unteren Gesichtsbereich, Verschiebung entlang der Gesichtsachse:
- Kinn = (`jaw` − 30) · Gewicht; Gewicht 1 von Mundhöhe + 130 px bis Kinn,
  zum Hals hin und seitlich (ab 110 px, null bei 230 px) weich auslaufend.
  Geschlossener Kiefer → Kinn 30 px höher; Schreien (`jaw` 52) → 22 px tiefer
  als in der Vorlage. Damit entfällt die Grenze aus ~~13.4~~ → 13.7 in `novaberg-avatar_m.md` (Ärger intensiv `mo` 70; W7) (Öffnung nicht über das Kinn).
- Nase 5 px länger (Nasenspitze und Oberlippe), Mund 5 px tiefer (`MOUTH_C`).
- Ohren, Haare, Schultern außerhalb der Gewichte.

**Kosten:** Bildrate im Headless-Browser 52 → 37,5 Frames/s (Pixeldichte 2).
Optimierbar (weniger Dreiecke, Zwischenspeicher bei unverändertem Kiefer).
Im GTK-Client mit Cairo neu zu messen.

**Bekannte Schwäche:** leichter Knick in der Kinnlinie rechts im Übergangsbereich
der seitlichen Abschwächung.

### 13.12 Sprechschicht: Lippensynchronität aus Text (02.10.2026, Prototyp)

Umsetzung von Schicht 3 (Abschnitt 8) als Prototyp; Zeitquelle Weg 3 (aus Text),
(W9: die drei Wege nach *Grenzen* unten — Lautzeiten der TTS, Analyse des Audios, Ableitung aus dem Text; die Nummern der ersten beiden sind nicht überliefert)
damit die Mundbilder geprüft werden können, bevor eine TTS angebunden ist (O9 offen).

**Viseme (12, Deutsch):** Ruhe, M/B/P, F/W, A, E, I, O, U, Ö/Ü, S (s, z, t, d, n),
SCH (sch, ch, j), L/R/K/G (l, r, k, g, h, ng). Je Visem: Lippenöffnung, Kiefer,
Breitenfaktor auf die Emotions-Mundbreite, Rundung, Pressen, F/W.

**Neue Kanäle (nur Sprechschicht)** — ~~eigene Kanäle~~ → seit §13.13 über die Muskelkanäle: `round` aus AU18/AU22, `press` als AU24, `fv` als AU28 (W3): `round` (Rundung/Vorstülpen: Mund schmaler,
Lippen dicker, Zähne weitgehend verdeckt), `press` (Lippen gepresst und eingerollt,
Öffnung und Kiefer × (1 − press)), `fv` (Oberlippe leicht angehoben, Unterlippe dünner).

**Text → Viseme:** regelbasiert, längste Graphemfolge zuerst (sch, ch, ie, ei, au,
eu, Dehnungs-h, Doppelvokale), Doppelkonsonanten einfach. Dauer: Vokal 115 ms,
langer Vokal 165 ms, Konsonant 70 ms, Satzzeichen 300 ms Pause, Wortlücke 25 ms
(behält das vorige Mundbild). Sprechtempo-Regler 0,6–1,6×.

**Kombination mit Emotion:** Sprechanteil S blendet weich ein (Feder ω = 12).
Öffnung und Kiefer vom Visem, Breite = Emotionsbreite × Visemfaktor, Lächeln durch
Rundung (−50 %) und Pressen (−30 %) gedämpft — Nova kann lächelnd sprechen.
Koartikulation über eine schnelle Feder je Sprechkanal (ω = 30); M/B/P schließt die
Lippen über `press` sicher.

**Gemessen:** 60 Frames/s im Testbrowser beim Sprechen (ohne Pixeldichte 2).

**Behobener Fehler:** Der Zeitstempel des Bildtakts liegt manchmal knapp vor dem
Startzeitpunkt; das wurde als Ende der Sequenz gewertet und die Sprechschicht
sprang sofort aus. Jetzt auf 0 begrenzt.

**Grenzen:** Regelbasierte Aussprache (z. B. „ch“ nach a/o/u, Endungs-„-er“,
Fremdwörter nicht unterschieden); Zeitverteilung geschätzt, nicht aus Audio.
Für echte Synchronität: Phonem-Zeitstempel der TTS oder Analyse des Audios.

**Koartikulation (02.10.2026, Hinweis Meister: Bewegungen künstlich, Übergänge prüfen):**
Ursache: Jeder Laut setzte alle Mundkanäle neu (z. B. kurzes Entrunden bei „s“
zwischen zwei „u“). Ersetzt durch das Dominanzmodell nach Cohen & Massaro (1993):
- Je Laut und Kanal eine Dominanz und eine zeitliche Reichweite; Zielwert =
  dominanzgewichteter Mittelwert aller Laute. Konsonanten haben auf Kanälen, die
  sie nicht brauchen, kaum Dominanz → Rundung und Breite laufen durch.
- Öffnung und Kiefer mit 35 % der Reichweite, damit der Silbenrhythmus erhalten
  bleibt (erster Versuch mit voller Reichweite glättete das Auf und Zu weg).
- M/B/P schließt in der Lautmitte erzwungen.
- Betonung: erster Vokal eines Wortes voll, weitere ×0,8, „e“ in Nebensilben ×0,55.
- Federn je Kanal: Lippenöffnung ω 32, Kiefer 20, Breite 18, Rundung 16,
  Pressen 45, F/W 30.
Werte aus der Literatur gesetzt, nicht gemessen. Kalibrierung an einem Video einer
deutsch sprechenden Person (frontal, 10–20 s) ~~steht aus~~ → durchgeführt am 02.10.2026, *Kalibrierung an Video* unten und `novaberg-avatar_m.md` §13.15, §13.16 (W8).

**Kalibrierung an Video (02.10.2026):** Mitschnitt einer Nachrichtensendung
(640 × 360, 25 Bilder/s), nur zur Messung von Bewegungskennzahlen verwendet.
- Auswahl: 5 Abschnitte (14–36 s) mit genau einem großen, frontalen Gesicht
  (Haar-Kaskade, 1 Abtastung/s). Zwei Sprecherinnen.
- Messung je Bild: Mund-Ausschnitt, per Phasenkorrelation stabilisiert;
  Öffnung = Ausdehnung von Mundinnerem (dunkel) und Zähnen (hell, farbarm) in der
  Mittelspalte; Breite = Ausdehnung der dunklen Mundlinie. Erster Ansatz über
  Lippenfarbe verworfen (Lippen kaum röter als Haut, Maske traf Zufallsflächen).
- Prüfung: Bildmessung visuell Bild für Bild bestätigt. Abgleich mit dem Ton
  unbrauchbar (bester Versatz je Abschnitt −600 … +400 ms, vermutlich Off-Stimmen
  bzw. Mischton) — Zeitbezug zum Laut daher nicht gemessen.
- Ergebnis (Öffnung / Mundbreite; Abschnitte A3, A4 = längste, sauberste Spur):
  an Silbenspitzen 0,32 / 0,34, dazwischen (Median) 0,13 / 0,18.
  Nova vorher 0,08 / 0,03 — ca. dreifach zu kleine Öffnung, zwischen den Silben fast zu.
- Kalibrierung: Visem-Öffnungen angehoben (z. B. A 30 → 44, E 16 → 30,
  Konsonanten S 3 → 9, L/R/K 8 → 18), Verstärkung 1,7 auf Öffnung/Kiefer,
  geringere Glättung (Öffnungsreichweite 0,35 → 0,25, Federn Öffnung 45, Kiefer 30),
  Konsonanten-Dominanz auf die Öffnung gesenkt.
  Nova jetzt: 0,21 an Spitzen, 0,12 dazwischen. Bewusst unter den Videowerten,
  da die Videomessung die Öffnung wahrscheinlich überschätzt (Zähne mitgezählt,
  Mundbreite eher zu klein gemessen).
- Nicht ableitbar aus diesem Material: Zeitbezug Lippe ↔ Laut, Rundung (Auflösung
  zu gering), Silbentempo (bei 25 Bildern/s und dieser Auflösung unterschätzt).
- Schatten auf den Zähnen halbiert (Hinweis Meister 02.10.2026): Abdunklung bei Lippenrundung 85 % → 42,5 %, Lippenschatten auf den Zähnen und Wurzelschatten je 50 % schwächer.
- Abdunklung der Zähne bei Rundung (O/U) weiter reduziert: 42,5 % → 15 % (Hinweis Meister 02.10.2026).
- Linien-Zittern auf 50 % (Hinweis Meister 02.10.2026): Versatz aller gezeichneten Striche (`BOIL_AMP` 0,5) und Verzerrung der drei Grundbild-Varianten (max. ca. 1,6 statt 3,3 px) halbiert. Takt unverändert (ca. 9 Wechsel/s).

### 13.13 Mund in Muskelkanälen nach FACS (02.10.2026, Prototyp)

Vorgabe Meister: Mund in Kanäle aufteilen, damit er die Flexibilität des menschlichen Mundes erreicht.
Grundlage sind die Action Units (AU) des Facial Action Coding System. Kiefer (`jaw`) und
Öffnung (`mo`) bleiben, die bisherigen Sammelkanäle `mc`/`mw`/`ma` bleiben als Grundform erhalten.

| Kanal | AU | Wirkung im Prototyp | Seiten |
|---|---|---|---|
| `au12L/R` | Mundwinkel hoch und außen | Winkel −10 px, Breite +16 % | getrennt |
| `au15L/R` | Mundwinkel runter | Winkel +11 px | getrennt |
| `au20L/R` | Lippen seitlich ziehen | Breite +22 %, Winkel +2 px | getrennt |
| `au10L/R` | Oberlippe heben | Oberlippe seitlich bis 10 px höher, Öffnung +9 | getrennt |
| `au16L/R` | Unterlippe senken | Unterlippe seitlich bis 10 px tiefer, Öffnung +9 | getrennt |
| `au18` | Lippen spitzen | Breite −30 %, Lippen dicker | gemeinsam |
| `au22` | Lippen trichtern | Breite −18 %, Lippen gewölbt, Öffnung +4 | gemeinsam |
| `au23` | Lippen spannen | Breite −8 %, Lippen dünner, Öffnung −35 % | gemeinsam |
| `au24` | Lippen pressen | schließt Öffnung, Kiefer −80 % | gemeinsam |
| `au17` | Kinn heben | Unterlippe hoch, Winkel −3 px, Öffnung −30 % | gemeinsam |
| `au28` | Unterlippe einziehen (F/W) | Öffnung −70 %, Kiefer −40 % | gemeinsam |

- Alle AU-Kanäle laufen über dieselben Federn und denselben Mundversatz (150 ms) wie die übrigen Mundkanäle.
- Emotionen nutzen sie gezielt: Trauer AU15 + AU17, Enttäuschung AU10 einseitig betont (links stärker),
  Angst AU20 (Grundbreite dafür 89 → 80), Ärger gedämpft AU23 + AU24, Neugier AU12 nur rechts (schiefes Lächeln).
- Sprechschicht: Viseme bestehen jetzt aus `mo, jaw, up (AU10), lo (AU16), str (AU20), pk (AU18), fn (AU22), press (AU24), fv (AU28)`.
  Beispiele: I = `str` 0,85, U = `pk` 1, O = `fn` 0,85, SCH = `fn` 0,75 + `pk` 0,35, F/W = `fv` 1.
  Koartikulation (Dominanz je Kanal) und Federn (`OMEGA`) entsprechend erweitert; Sprechanteil wird additiv auf die Emotion gelegt.
- Lächeln wird durch Spitzen/Trichtern (−50 %) und Pressen (−30 %) gedämpft.
- Testfeld „Mundmuskeln“ in der Oberfläche: ein Regler je Kanal (Seiten getrennt), wirkt zusätzlich, „Zurücksetzen“.
- Prüfung: keine Laufzeitfehler, Emotionsbilder ohne Abweichung über das Blinzel-/Blickrauschen hinaus,
  Einzel-AU-Bilder und Visem-Bilder sichtgeprüft. Bildrate im Headless-Chromium ca. 55–59/s (keine Messung am Zielsystem).
- Offen: Wirkstärken sind Schätzwerte aus Sichtprüfung, nicht gemessen. Messbar über
  Mundwinkel, Breite und Lippenhöhen je Bild an eigenen Aufnahmen je AU.

### 13.14 Einzellaute statt Viseme (02.10.2026, Prototyp)

- Sprechschicht arbeitet mit 37 deutschen Lauten (SAMPA) statt 12 Visemen: lange/kurze Vokale getrennt
  (e:/E, o:/O, u:/U, i:/I, y:/Y, 2:/9), Schwa `@`, vokalisiertes r `6`, ich-/ach-Laut `C`/`x`, Diphthonge als zwei Ziele (a+I, a+U, O+Y).
- Jeder Laut hat einen vollständigen Satz Muskelwerte (`PH_TABLE`); Dominanz und Grunddauer kommen aus seiner Lautklasse (`PH_CLASS`).
- Text -> Laute regelbasiert (`wordToPhonemes`): Vokallänge aus Dehnungs-h, Doppelvokal, ie und Silbenstruktur;
  Endungen -e/-en/-el -> Schwa, -er und r nach Vokal -> `6`; Betonung erste Silbe, nach be-/ge-/ver-/zer-/ent-/emp- die zweite.
  Bekannte Fehler: Buch -> kurzes u, Abend/Pferd -> kurzer Vokal. Für die Produktion: Ausspracheregeln durch ein Lexikon/G2P-Modell ersetzen.

### 13.18 Kopfdrehung (Prototyp 04.10.2026, Client 05.10.2026)

Die Rechnung ist die des Prototyps (`labor/avatar/index.html`, `yawGitter`, `yawWarpDraw`), im Client `client/avatar/head_turn.py` (L2′b, L2′c); der Kopf folgt dem Ziel des Leerlaufs (§17.3) über die Kopffeder der Puppe (§15.2).

- **Der Weg:** Dreht der Kopf um mehr als 0,05° (`TURN_MIN`), zeichnet `draw_face` Hals, verzerrtes Gesicht und alle Züge ohne Atem auf eine Zwischenfläche in Bildgröße und legt sie mit dem Drehgitter auf das Bild, mit Atem und Maßstab. Bis 0,05° bleibt der Weg genau der ungedrehte.
- **Das Gitter:** 24 × 29 Punkte (`YAW_XS`, `YAW_YS`), über dem Hals und im Gesicht dichter, 1288 Dreiecke. Jeder Punkt wandert quer zur geneigten Gesichtsachse um seine Tiefe vor der Halswirbelsäule mal sin θ: Kopf 30, Wölbung mit Haaren 60, Gesicht 20, Nasenspitze 25 px. Ab der Kinnlinie (`JAWLINE`, 35 Punkte) verdrillt sich stattdessen der Hals als Zylinder (Mitte 600, Halbmesser 130); 230 px darunter ist die Verdrillung abgeschlossen. Brust, Schultern, das Haar neben dem Hals und der Bildrand stehen. Bei 12° wandert die Nase etwa 27 px der Vorlage, die Augen weniger, die Ohren noch weniger.
- **Die Grenze:** Jenseits von ±15° und bei einem nicht endlichen Winkel wirft das Gitter; bis dahin klappt kein Dreieck um. Den Wert teilen Ziel und Zeichnung (`YAW_MAX`).
- **Die Zeichnung:** Zuerst liegt die Zwischenfläche unverzerrt als Unterlage, darüber nur die Dreiecke, an denen eine Ecke verschoben ist. Ein Dreieck ohne Verschiebung wäre die Identität über derselben Unterlage; das Bild ist dasselbe, außerhalb von Kopf und Hals wird nichts gezeichnet, und keine Naht liegt offen. Jedes verschobene Dreieck ist ein `fill` mit der Zwischenfläche als Muster, kein `clip` mit `paint` (L2′c).
- **Die Naht:** Jedes Dreieck — das der Drehung als Pfad des `fill`, das der Kinnverzerrung (§13.9) als Clip — ist wie im Prototyp radial um 1,6 px vom Schwerpunkt vergrößert (bis L2′b im Client je Achse um 0,6), sodass auch die Diagonale einer Zelle überdeckt ist.
- **Die Kosten:** Die Bildzeit mit Drehung steht in `novaberg-avatar_b.md` §18 (L2′c).

---

## 14. Datenvertrag: was der Client braucht und woher es kommt

**Stand 02.10.2026.** Abgeleitet aus dem Prototyp (`labor/avatar/index.html`, vollständig gelesen) und belegt am Code dieses Tages. Leitlinie: Der Client bekommt, was das Gesicht bewegt — Maßstab ist der Prototyp, nicht das Verfügbare.

### 14.1 Was der Prototyp verarbeitet

Von außen nur drei Größen: einen **Sektor** (0 = neutral, 1–8), ein **Arousal** (0..1) und einen **Text zum Sprechen** samt Tempo. Den kanonischen Namen zeigt er nur an; die Ausprägung moderat/intensiv bestimmt allein das Arousal (§5.2, §6.1). Eine Mischung mehrerer Emotionen (§6.2) und den Konflikt (§6.3) setzt er nicht um.

### 14.2 Was heute schon mit der Antwort reist

Die Antwort erreicht den Client als WebSocket-Nachricht `character_response` (`server/services/event_consumer.py`, `_antwort_nutzlast_bauen`). Für den Avatar trägt sie bereits:

| Feld | Inhalt | Stand |
|---|---|---|
| `nova_emotion` | kanonischer Name, Eintrag 0 von `nova_emotions_verlauf` | Novas Emotion, mit der sie antwortet — gerechnet vor dem Responder |
| `nova_arousal` | 0..1, Eintrag 0 des Verlaufs | wie oben |
| `nova_emotions_verlauf` | `list[dict]` mit `emotion`, `gewicht`, `arousal`; die Dominante trägt Gewicht 1.0 | wie oben |
| `nova_emotion_konflikt` | `bool` | wie oben |
| `nachricht` | Novas Antworttext | — |

**Kein Client-Code liest heute eines dieser Felder.** Die Felder `emotion` und `arousal` derselben Nachricht stammen aus `internal.emotion` und beschreiben bei der Freigabe Novas Wahrnehmung ihrer eigenen Antwort; der Avatar liest sie **nicht**. → **Seit 04.10.2026 umgekehrt** (entschieden, `novaberg-avatar_k.md` §3): Der Avatar liest `emotion`/`arousal`, die Wahrnehmung der Antwort, und nie `nova_emotion`/`nova_arousal` — die sind Novas Stimmung zu Beginn des Turns, gerechnet aus ihren früheren Antworten, und zeigten deshalb im Betrieb den Wert des Turns davor (Turn A 0,60 statt 0,65, Turn B 0,65 statt 0,50). Die Wahrnehmung liegt beim Senden vor, weil die Auslieferung am Ende von `perzeption_assistant` hängt; die Antwort wartet darauf 2,3–2,7 s, und das ist gewollt.

### 14.3 Was fehlt

1. **Der Sektor.** Die Nachricht trägt den Namen, nicht den Sektor. Die einzige Abbildung Name → Sektor ist `EMOTION_SEKTOR_MAP` (`server/config.py`): `dict[str, int]`, 16 Schlüssel, Werte 1–8, `neutral` nicht enthalten. **Der Server liefert den Sektor** als neues Feld `nova_sektor` (`int` 1–8, `null` bei `neutral`), damit der Client den Kanon nicht ein weiteres Mal führt. Ein Name außerhalb von `EMOTION_KANON` ist ein Defekt: `null` und eine Error-Zeile im Server-Log; der Avatar zeigt dann Neutral (§10).
2. **Die Antworten aus eigenem Impuls.** Der Client leitet eine `character_response` mit `reiz_herkunft = "eigener_impuls"` an `_invoke_impulse` und **nicht an die Panels** (`client/ui/stream_handler.py`, `_ws_on_message`). Der Avatar muss auch dann reagieren: Ein eigener Gedanke ist eine Äußerung Novas mit ihrer Emotion.

### 14.4 Was der Avatar nicht braucht

Strategie, Absicht, Vehikel und Haltung (`gv_detail`, `haltung`) bewegen im Prototyp kein Gesicht, und das Leitprinzip (§2) lässt den Avatar nur den Emotionszustand darstellen. Sie werden **nicht** übertragen. Soll eine davon später sichtbar werden — etwa das Vehikel *Frage* —, ist das eine neue Absicht und gehört zuerst nach §1.

### 14.5 Sprechen

Im Repositorium gibt es **keine Sprachausgabe** — keine Bibliothek, keinen Dienst, keine Abhängigkeit (gelesen am 02.10.2026). Damit gibt es auch keine Lautzeiten. Der Prototyp leitet sie aus dem Text ab (§13.12, §13.14); der Client kann das mit `nachricht` genauso. Ob der Avatar ohne Ton spricht, ist offen (O9). Der Server entfernt aus dem Antworttext weder Markdown noch Sternchen; ob Text in `*…*` gesprochen wird, ist offen (O12).

---

## 15. Portierung nach GTK4 und Cairo

**Stand 02.10.2026.** Grundlage: Inventur des Prototyps (1312 Zeilen) und des Clients, beide vom 02.10.2026.

### 15.1 Der Prototyp ist die Referenz

Wo der Text dieses Konzepts vom Prototyp abweicht, gilt für den Bau der Prototyp — mit den Ausnahmen, die einzeln entschieden sind. Die Abweichungen stehen in `novaberg-avatar_e.md`, *Abweichungen Prototyp ↔ Konzept* (P1–P17), jede mit dem, was gebaut wird.

### 15.2 Schichten des Codes

Die Trennung aus §2 wird zur Gliederung: reine Logik ohne GTK, Zeichnen ohne Widget, ein dünnes Panel.

| Teil | Inhalt | GTK? | Umfang im Prototyp |
|---|---|---|---|
| Ausdruck | Sektor-Schlüsselbilder (`SECTORS`), Ziel aus Sektor und Arousal (`sectorTarget`) | nein | ≈ 55 Zeilen |
| Animator | Feder je Kanal, Mundversatz 150 ms, Blinzeln, Atmen, Boil-Takt | nein | ≈ 50 Zeilen |
| Sprechen | Laute aus Text, Lauttabellen, Koartikulation, Zusammenführung mit der Emotion | nein | ≈ 270 Zeilen |
| Zeichnen | Augen, Brauen, Mund, Zähne, Falten, Extras als Funktionen `(cr, zustand, seed)` | Cairo, kein Widget | ≈ 600 Zeilen |
| Grundbild | Bildvarianten, Gesichts- und Halsebene, Gitterverzerrung des Kinns | Cairo | ≈ 120 Zeilen |
| Panel | `Gtk.DrawingArea`, Bildtakt, Empfang der Antwort | ja | neu |

Der Client hat bisher keinen Ort für GTK-freie Logik (am nächsten `client/ui/formatierung.py`) und keinen für Bilder; ~~Ablage und Aufteilung in Module sind offen (O14)~~. Neue Dateien tragen englische Bezeichner.

→ **Entschieden am 02.10.2026 (O14, `novaberg-avatar_e.md`):** Die Logik liegt in einem eigenen Paket `client/avatar/` ohne GTK und ohne `requests`; nur das Panel liegt unter `client/ui/panels/`. Die Abhängigkeit läuft nur von `ui` nach `avatar`. Der Schnitt in Module — die Namen sind Vorschläge:

| Modul | Inhalt | Zugriff |
|---|---|---|
| `client/avatar/face.py` | die Datentypen: `FaceState` (ein Feld je Kanal, in Pixeln der Vorlage), `Pose` (sichtbarer Zustand mit Zunge, Blinzeln, Atem, Boil-Takt), `Utterance` (Sektor, Arousal, Text) | keiner |
| `client/avatar/expression.py` | Schlüsselbilder, `face_target(sector, arousal) -> FaceState` — der einzige Teil, der Emotionen kennt | keiner |
| `client/avatar/animator.py` | Feder je Kanal, Mundversatz, Blinzeln, Atmen, Boil-Takt | keiner; Zeit und Zufallsquelle als Parameter |
| `client/avatar/speech.py` | Laute aus Text, Lauttabellen, Koartikulation, Zusammenführung mit der Emotion | keiner |
| `client/avatar/puppet.py` | die Fäden: Animator- und Sprechzustand zusammen, ein Schritt je Bild | keiner |
| `client/avatar/drawing.py` (aufteilbar) | Strichformen, Augen, Brauen, Mund, Falten, Extras auf einem gegebenen Cairo-Kontext | Cairo |
| `client/avatar/base_image.py` | Gitterverzerrung des Kinns, Zwischenspeicher der verzerrten Gesichtsebene | Cairo |
| `client/avatar/head_turn.py` (seit L2′b, 05.10.2026) | Drehgitter der Kopfdrehung, Verdrillung des Halses, die Zeichnung über Unterlage und verschobene Dreiecke (§13.18) | keiner; gezeichnet wird über `base_image` (`paint_layer`, `fill_triangles`) |
| `client/avatar/layers.py` | das Laden der Bilder — der einzige Dateizugriff | Dateisystem |
| `client/ui/panels/avatar_panel.py` | `PanelBase`, `turn_reactive`, `UNIQUE`; Bildtakt von `map` bis `unmap`; macht aus der Antwort eine `Utterance` | GTK |

- **Eine Uhr:** Nur das Panel liest die Zeit der Frame-Clock und gibt sie als Sekunden an die Logik; Ausdruck, Animator und Sprechen lesen nie selbst eine Uhr. Die Zeugen treiben die Zeit künstlich.
- **Ein Seed je Teil** (`novaberg-avatar_e.md`, P12), abgeleitet aus dem Boil-Takt; das Blinzeln zieht aus einer Zufallsquelle, die das Panel erzeugt und ein Zeuge festsetzt. Pixelgleich zum Prototyp ist die Zeichnung damit nicht — die Gleichheit prüft der Sichtvergleich (`novaberg-avatar_b.md` §16, B6).
- **Die Bilder** liegen in `client/avatar/images/`; den Ort nennt eine Konstante in `client/config.py`. Fehlt ein Bild, zeigt das Panel einen Hinweis statt des Gesichts und schreibt eine Error-Zeile.
- **Der Kopf** (seit L2′a/L2′b, 05.10.2026): Den Kopf führt in der Puppe eine eigene Feder mit ω 3,5 (`HEAD_OMEGA`) zum Kopfziel `IdleFrame.head_yaw` des Leerlaufs (§17.9), mit demselben Zeitschritt wie die Kanäle und derselben Formel (`animator.spring_one`). Die Pose trägt ihn als `Pose.head_yaw` in Grad, plus nach rechts aus Sicht des Betrachters, ohne Angabe 0; `check_pose` prüft ±15°. Weil die Feder kritisch gedämpft ist und in Ruhe beginnt, bleibt der Kopf innerhalb der Spanne seiner Ziele — gerechnet, nicht gemessen: Er ist ein gewichtetes Mittel der früheren Ziele mit Gewichten ≥ 0 und Summe < 1. `draw_face` liest `pose.head_yaw` und zeichnet den Kopf damit gedreht (§13.18): Die Puppe liefert den Stand der Kopffeder, nicht das Ziel, das Bild folgt dem Ziel also mit ω 3,5. Über 0,05° geht das ganze Bild ohne Atem über eine Zwischenfläche, und auf das Bild kommen nur deren Unterlage und die verschobenen Dreiecke.

### 15.3 Browser-Mittel und ihre Entsprechung

| Mittel im Prototyp | in Cairo | Entscheidung |
|---|---|---|
| Pfade, `quadraticCurveTo`, `arc`, gedrehte Ellipse | vorhanden; quadratisch → kubisch (2/3-Regel), Ellipse über `save`/`rotate`/`scale` | übertragen |
| `fill` und danach `stroke`/`clip` auf demselben Pfad | `fill_preserve`, `clip_preserve` | übertragen |
| Verläufe, `setTransform`, Offscreen-Canvas, `destination-out` | vorhanden (`cairo.Matrix`, `ImageSurface`, `OPERATOR_DEST_OUT`) | übertragen |
| `globalAlpha` | fehlt | Deckkraft in die Farbe einrechnen |
| `filter: blur()` beim Ausstanzen der Gesichtsebene | fehlt | Gesichtsebene vorab berechnen und als Bild mit Alphakanal ablegen, wie die Halsebene |
| JPEG-Bilder | Cairo liest nur PNG | Bilder als PNG ablegen |
| `drawImage` je Dreieck, 338 je Frame | möglich, teuer | verzerrte Gesichtsebene nur neu rechnen, wenn sich der Kiefer ändert; Bildrate messen (`novaberg-avatar_b.md` §16, B7) |
| `drawImage` je Dreieck des Drehgitters (`yawWarpDraw`, 1288 Dreiecke) | `clip` und `paint` je Dreieck — teuer, eine Maske je Aufruf | **seit L2′c (05.10.2026):** die Zwischenfläche einmal als Unterlage, darüber nur die verschobenen Dreiecke, je eines ein `fill` mit **einem** Muster je Bild, dessen Matrix die Abbildung des Dreiecks trägt; was nur am Gitterpunkt hängt, ist beim Laden gerechnet (`YAW_BASIS`). Das Bild bleibt gleich; die Bildzeit in `novaberg-avatar_b.md` §18 |
| `requestAnimationFrame`, `performance.now()` | `add_tick_callback`, Zeit der Frame-Clock | **eine** Uhr für Animation und Sprechen (vgl. den behobenen Fehler in §13.12) |
| `Math.round` | Pythons `round` rundet .5 zur geraden Zahl | `math.floor(x + 0.5)` |
| Zufall für Strichlagen (Park-Miller-Generator, Hash) | in Python exakt nachbildbar | übertragen; `Math.random` nur für die Blinzelabstände |

### 15.4 Das Panel im Client

- **Turn-reaktiv und einmalig** (`CATEGORY = "turn_reactive"`, `UNIQUE = True`); nur solche Panels erhalten eine Antwort (`client/ui/panel_registry.py`, `broadcast_turn`). Ein Eintrag in der Werkzeugleiste ist Pflicht (`client/ui/main_window.py`, `_TOOLBAR_PANELS`; geprüft von `client/tests/test_toolbar_panels.py`).
- **Kein REST:** Das Panel lädt nichts; `load_data` wird trotzdem überschrieben, sonst steht beim Öffnen „Fehler“ in der Fußzeile.
- **Der Bildtakt hängt an der Sichtbarkeit:** Die Registry baut bei jedem Klick eine neue Instanz, und es gibt keinen Abbau-Hook. Der Takt (`add_tick_callback`) startet bei `map` und endet bei `unmap`.
- **Antwort → Ziel:** `on_turn_received` liest ~~`nova_sektor`, `nova_arousal` und `nachricht`~~ → **gebaut 03.10.2026:** ~~`nova_emotion`~~ → **seit 04.10.2026 `emotion`**, die Wahrnehmung der Antwort, §14.2 (den Namen; der Sektor folgt aus den Namen der Schlüsselbilder, `neutral` → neutral, ein unbekannter Name → Error-Zeile und neutral), ~~`nova_arousal`~~ → `arousal` und `antwort` — so kommt die `character_response` im Client an; ein `nova_sektor` vom Server ist nicht nötig — und setzt das neue Ziel; ein laufender Übergang geht vom sichtbaren Zustand aus weiter (§7.2).
- **Die Testbedienung des Prototyps** — Sektor-Knöpfe, Regler, Muskelregler, Gesprächssimulation — wird nicht übernommen.

### 15.5 Prüfbarkeit ohne Bildschirm

`Gtk.DrawingArea()` stürzt ohne Display-Sitzung ab (gemessen am 02.10.2026). Die Tests prüfen deshalb die Logik direkt und das Zeichnen über Funktionen `(cr, breite, höhe, zustand, seed)` auf einer `cairo.ImageSurface`, ohne Widget. Die Zeugen des Clients laufen auf dem Host neben der Server-Suite.

---

## 17. Leerlauf: die Denkweisen im Client

**Stand 03.10.2026.** Die Absicht steht in `novaberg-avatar_k.md` §3 (Rauschen, Nachdenken, Antwort, Nachklang; *„Zufall, aber geformt“*). Dieser Abschnitt sagt, wie der Client sie umsetzt; die Bauteile stehen in `novaberg-avatar_b.md` §18.

### 17.1 Der Generator ist die Referenz

Für die Leerlauf-Schicht ist der Generator im Labor, was der Prototyp für das Gesicht ist (§15.1): `labor/avatar/leerlauf_bauen.py` erzeugt `leerlauf.html` über dem Prototyp, Stand 03.10.2026 — **nachgestellt am 04.10.2026** nach den Messungen von L3 und L6 (L0′a–L0′c, `novaberg-avatar_b.md` §18); dieser Abschnitt trägt den Stand von L0′c. **Wo dieser Text vom Generator abweicht, gilt für den Bau der Generator** — ausgenommen die Abweichungen in §17.9. Die Werte des Generators und ihre Herkunft stehen in `labor/avatar/recherche_mimik_leerlauf.md` (§1.2 Formen, §2 Zeitwerte, §4 Raum, §5 Generator); geschätzte Werte tragen dort und im Code ein **(S)**.

Seine Prüfung `labor/avatar/leerlauf_pruefen.py` lässt ihn über eine eigene Uhr laufen (Anker `#sim`, ~~`#turnab`~~ → **seit 03.10.2026 `#ev`**, die Ereignisse des Clients nach §17.8 mit ihrer Zeit) und legt den Verlauf als JSON ab — Zustände, Formen mit Dauer und Blickpunkt, Lidschläge, Mundöffnung je Form. **Daraus entstehen die Referenzwerte des Clients** (`novaberg-avatar_b.md` §18, L1) — **erzeugt am 03.10.2026** von `labor/avatar/leerlauf_referenz.py` als `client/tests/avatar_reference/idle.json`: zehn Fälle — die der Abnahme (§18.1), dazu Unterbrechungen, Antwort ohne Nachdenken, Impuls und gescheiterter Turn — × drei Startwerte, je Lauf Zustände, Formen, Lidschläge, die behandelten Ereignisse und jede Sekunde die Ziele aller Kanäle: Der Zufall des Generators hat einen Startwert (mulberry32) und ist in Python exakt nachbildbar; bei gleichem Startwert, gleichen Eingängen und gleicher Reihenfolge der Ziehungen plant der Client dieselben Formen mit denselben Dauern. ~~**`idle.json` und `expression.json` stehen bis L1′ auf dem Stand von L0**; mit L1′ werden sie aus der nachgestellten Referenz neu erzeugt.~~ → **Mit L1′ neu erzeugt (05.10.2026):** `idle.json` trägt 33 Läufe — elf Fälle (die zehn bisherigen und das lange Nachdenken, 120 s) × drei Startwerte — und je Probe 36 Kanäle samt `yaw`; `expression.json` folgt der nachgestellten Referenz. Neu seit L0′c ist `client/tests/avatar_reference/yaw.json` (die Verformung der Kopfdrehung an acht Winkeln).

### 17.2 Die Zustände und ihre Auslöser im Client

| Zustand | beginnt | endet | Emotion | Aktivität `a` |
|---|---|---|---|---|
| **Rauschen** | beim Öffnen des Panels, wenn der CharacterGraph nicht denkt (§17.10); am Ende des Nachklangs | ein Turn oder ein Impuls beginnt; eine Antwort trifft ein | **Pixies Auftrag** (§17.8): Emotion und Arousal des zuletzt begonnenen Auftrags, der noch läuft und eine Emotion trägt — Pixie rechnet in zwei Spuren, ein Auftrag ohne Emotion verdrängt keinen mit; läuft keiner mit Emotion, neutral mit Arousal 0 | 0,6, solange in einer Spur ein Auftrag läuft, sonst 0,2 (S) |
| **Nachdenken** | der Client sendet eine Nachricht des Nutzers; **eine Nachricht des Nutzers aus einem anderen Client trifft ein** (`user_message`, seit 04.10.2026); ein Impuls geht in den CharacterGraph (§17.8); **das Panel öffnet, während der CharacterGraph für einen Turn oder Impuls denkt** (§17.10) | eine Antwort trifft ein → Einatmen, dann Antwort; der Turn scheitert (`turn_gescheitert`) **oder schon das Senden** → Rauschen; Wächter: nach 600 s ohne Antwort → Rauschen mit Warning-Zeile | **Novas aktuelle Emotion** — die ihrer letzten Antwort (Absicht §3: *„beginnt Nova mit der aktuellen Emotion nachzudenken“*); vor der ersten Antwort neutral | 0,7 |
| **Antwort** | nach dem Einatmen; die Wiedergabe beginnt | Ende der Wiedergabe + 0,4 s | die der Antwort ~~(`nova_emotion`, `nova_arousal`)~~ → ihre Wahrnehmung (`emotion`, `arousal`), seit 04.10.2026 (§14.2) | 0 |
| **Nachklang** | Ende der Antwort | nach `(6 + 24·N) · U(0,8; 1,2)` s, bei N = 0,5 also 14,4–21,6 s | Nova klingt aus, in den letzten 40 % zu Pixie (§17.3) | 0,2 |

- **Eine Antwort, die ohne Nachdenken eintrifft** — ein Impuls, dessen Beginn der Client nicht kannte, eine Antwort im Rauschen oder im Nachklang —, geht ebenso über das Einatmen in die Antwort.
- **Ein neuer Turn unterbricht jeden Zustand sofort**; Nachklang und Rauschen haben keinen Vorrang vor dem Nutzer. Den Übergang glättet die Feder (Blick ≈ 0,14 s, Gesicht ≈ 0,5–1 s).
- **Trifft eine Antwort während einer Antwort ein**, löst die neue die laufende ab, wie heute (§15.4).
- **Ein Ereignis Pixies ändert im Nachdenken und in der Antwort nichts Sichtbares**; es setzt nur den Rückfall (entschieden, `novaberg-avatar_k.md` §3). **Im Nachklang** zielt die Überblendung der letzten 40 % auf den jeweils aktuellen Rückfall — sie ist der Übergang in ihn, kein Teil des Turns; so liest es auch der Generator in jedem Bild. **Im Rauschen** plant der nächste Zyklus mit der neuen Emotion, und die Basis gleitet über die Feder hinüber.
- **Die Stufen des CharacterGraph** (`character_stage`) taugen **nicht** als Auslöser: Sie tragen keine Herkunft und kommen zum Teil erst **nach** der Antwort — die Antwort geht schon bei `perzeption_assistant` hinaus, die Stufen des Nachlaufs folgen ihr (`server/services/event_consumer.py`, gelesen am 03.10.2026). Ein Auslöser aus ihnen schickte Nova nach der Antwort zurück ins Nachdenken.

### 17.3 Schichten

Von unten nach oben, jede ein eigener Prozess (Perlin 1997; Andrist 2014):

| Schicht | Inhalt | Werte |
|---|---|---|
| Emotionsbasis | `face_target(sektor, arousal · f)` — im Rauschen und Nachdenken schwach (f = 0,5), ~~in der Antwort voll (f = 1)~~ → **in der Antwort f = 0,75** (entschieden 04.10.2026, `novaberg-avatar_k.md` §3); **die Antwort gleitet über A0 mit `smooth(t / A0)` vom Gesicht vor dem ersten Laut in ihre Basis** — bis dahin sprang sie am ersten Laut; im Nachklang Nova ausklingend (0,7 → 0,35 ihres Arousals über die ersten 60 %), in den letzten 40 % geglättet zu Pixie | Generator `lage`, `BASIS_FAKTOR` |
| Form | Abweichung je Gesichtskanal zur Basis, mal der Amplitude `k = (0,5 + 0,5·a) · (0,7 + 0,3·N)` | `FORMEN`, `abweichung` |
| Blick | Blickpunkt der Form plus kleine Sakkaden im Takt der Form; **nicht** mit `k` skaliert — der Blick trägt das Nachdenken. **Seit 03.10.2026 allein die Form:** Bis dahin addierte der Generator den Blick der Emotionsbasis; bei Neugier, Hoffnung, Trauer und Enttäuschung, deren Schlüsselbild einen Blick trägt, sah Nova dann in F16 und A1 am Betrachter vorbei, und im Nachdenken hob er den abgewandten Blick einer Form auf. **Seit 04.10.2026 (L0′b)** rückt die Iris je Einheit Blick um 0,5·hw waagrecht und 0,26·hw senkrecht (hw = halbe Augenbreite; bis dahin 0,3 und 0,16 — der Blick erreichte das Bild mit 1–1,5 px kaum); das Oberlid hebt sich beim Blick nach oben um 0,08 je Einheit (`eo`) und senkt sich beim Blick nach unten (`lidU` 0,3) | `blickBasis`, `sakkaden` |
| Kopf | **seit 04.10.2026 (L0′c)**: Der Kopf folgt dem Blick der Form (ohne Sakkaden; F7 je Pendelpunkt, F9 je Phase) 200 ms nach den Augen, zurück zum Betrachter (\|x\| ≤ 0,12) nach 150 ms. Meist klein, `Seite · 10° · \|x\| · (0,6 + 0,4·h)`; im Nachdenken bei deutlich seitlichem Blick (\|x\| ≥ 0,25, Denkformen außer F7 und F9) `Seite · 10° · (0,9 + 0,2·h)` — *„beim zur Seite schauen, nachdenklich, dreht er um etwa 10° mit“* (`novaberg-avatar_k.md` §3). Dazu Wandern von 1° (glattes Rauschen, ohne Ziehung). Ziel hart auf ±15°. h je Form aus einer **eigenen** Zufallsquelle, damit der Plan mit und ohne Kopf derselbe bleibt. E1 und A0 behalten das Ziel des Vorgängers, wie den Blick (`blickWeiter`). Gezeichnet als zweite Gitterverzerrung über das fertige Bild: jeder Punkt wandert nach seiner Tiefe, der Hals verdrillt sich, die Schultern stehen; bis 0,05° bleibt der bisherige Zeichenweg | `kopfSoll`, `kopfRegel`, `kopfSchritt`; Prototyp `yawGitter`, `yawWarpDraw` |
| Lidschlag | eigener Prozess (§17.6); ersetzt das feste Blinzeln der Puppe — ~~`client/avatar/puppet.py`, `_blink`~~ → **seit L2 (03.10.2026) entfernt**, `Pose.blink` ist die Öffnung des Lids aus dem Leerlauf | `lidschlaege` |
| Rauschen | glattes Rauschen auf Brauen, Mundwinkeln und Mund, Stärke ∝ `a`; ~~nicht in der Antwort~~ → **in der Antwort a = 0,25 nur auf Brauen und Mundwinkeln; die Stärke gleitet über A0** von der des Nachdenkens zu der der Antwort (seit 04.10.2026, L0′a) | `rauschen`, `AMP`, `RAUSCHEN_ANTWORT` |
| Pupille | Basis + Form (F3 +0,05, F4 −0,05, F5 +0,12) + Last 0,06·a + **0,12·E, ungedämpft, in allen vier Zuständen** — Erregung weitet (entschieden 04.10.2026, Backlog `AVATAR-PUPILLE-AROUSAL`); begrenzt auf 0,6–1,3. ~~Angst 0,72, Überraschung 0,8 als eigenes `ps` des Sektors~~ → entfallen, beide verengen nicht mehr | `zielSetzen`, `PUPILLE_E` |
| Sprechen | in der Antwort die Sprechschicht (§13.12) über der Emotion, wie heute | — |

**Der Mund im Leerlauf:** Die Öffnung der Basis ist auf 2 begrenzt, sonst liest sich eine offene Freude-Basis als Sprechen. Nur F9 (Einfall) hebt die Grenze auf, **im Nachdenken keine Form** — dort bleibt der Mund ruhig. F14 (*Mund leicht offen*) legt `+4 · k` über die begrenzte Basis (im Rauschen ≈ +2,7). **Offen** heißt in den Prüfungen: Öffnung `mo` über 4. **Auch in der Antwort ist die Öffnung der Basis ≤ 2, der Kiefer folgt mit 0,75; dort öffnet die Stimme** (seit 04.10.2026, L0′a — sonst stand der Kiefer bei Freude über geschlossenen Lippen offen).

**Die Feder je Kanalgruppe:** dieselbe kritisch gedämpfte Feder (§7.3), aber mit ω je Gruppe — Gesicht `5 · (1 + 0,8·E)`, Pupille 5, Blick 35 (eine Sakkade erreicht 95 % nach 0,14 s), **Kopf 3,5 (95 % nach 1,36 s, seit 04.10.2026)**. Der Mundversatz (§7.4) entfällt im Leerlauf.

### 17.4 Formen, Gruppen und Zyklus

- **Formen:** F1–F17 (Konzentration, Erinnern, Vorstellen, Ins Leere, Denklast, Verwirrung, Unsicherheit, Skepsis, Einfall, Sorge, Formulieren, Nachsinnen, Kinn hoch, Mund offen, Lächeln kontrolliert, Blick zum Betrachter, Fixieren), dazu **E1** Einatmen und für die Antwort **A0** Denkblick weiter, **A1** Zuwenden, **A2** Wegsehen beim Sprechen. **Seit 04.10.2026 (L0′a)** schaut F5 (Denklast) fest seitlich unten ins Leere (±0,3; 0,3) statt geradeaus (0; 0,1) — *„Nachdenken ist eher den Blick ins Leere richten abseits des Betrachters“* (`novaberg-avatar_k.md` §3); F15 trägt denselben Blick.
- **Gruppe je Zustand und Emotion:** Gewicht = Grundgewicht des Sektors (`GRUND`) × Faktor des Zustands (`GRUPPE`, 0 = gehört nicht dazu) × Modifikatoren aus Tiefe, Energie, Aktivität, Nähe, Richtung und Valenz (`MOD`). Rauschen: breit, leicht zu inneren, weiten Formen geneigt. Nachdenken: Anstrengung, Prüfen, Formulieren; kein Abschweifen (F4), kein offener Mund (F14). Nachklang: Nachsinnen, ins Leere, gebremstes Lächeln; keine Last, kein Einfall.
- **Art des Auftrags** (nur im Rauschen, Generator `gewichte`): Recherche hebt Erinnern und Vorstellen (F2, F3 × 1,5), Reflexion Nachsinnen oder Sorge je nach Valenz (F12/F10 × 1,5), Wissenslücke Verwirrung (F6 × 1,5). Die Abbildung der Arten des Servers steht in §17.8.
- **Zyklus:** 4–5 Formen ohne Zurücklegen nach Gewicht, Wiederholungen über Zyklen gedämpft, geordnet nach den Regeln R1–R8 (Eröffnung mit Blickwechsel, Einfall nur nach Vorläufern, höchstens zwei Asymmetrien, keine Form zweimal, Kontrast zwischen Nachbarn, Schluss mit F16 oder abwärts, Lidschlag am Blickwechsel) — `zyklusPlanen`, `ordnen`. **R7 im Nachdenken seit 04.10.2026 (L0′a):** F16 als Akzent mit halber Wahrscheinlichkeit und 1,0–1,5 s — *„sie darf auch zum Betrachter sehen, selten“*; im Rauschen und im Nachklang unverändert.
- **Takt:** `x_c = max(0,5; (6 − 4·E + Δ_S + (T − 0,3)) · Faktor)`, Faktor Rauschen 1, **Nachdenken 1,3** (entschieden, `novaberg-avatar_k.md` §3), Nachklang 1,3. Jede Form steht eine Zeit aus einer Dreiecksverteilung über `0,65·x_c` bis `1,35·x_c` (mindestens 1,5 s, höchstens 10 s) mit Gipfel bei `x_c`. **Ausnahme seit 04.10.2026 (L0′a): F9 (Einfall) im Nachdenken ist ein Akzent** von 1,0 s (Phase a und b, der Blick dabei seitlich mindestens 0,2) + U(1,0; 2,0) s, gleich viele Ziehungen wie die Dreiecksverteilung; im Rauschen gilt die Spanne — die Kürzung auch dort brachte mehr Formwechsel und gekoppelte Lidschläge und hob die Rate des Rauschens bei Ärger über die der Antwort.

### 17.5 Antwort und Einatmen

- **Einatmen (E1):** Das Nachdenken endet mit 0,7–0,9 s leicht geöffnetem Mund (Torreira 2015) — ~~`mo` 6·k~~ → **seit 04.10.2026 (L0′a) `mo` 10,5·k und die Augen +0,05·k**, gemessen lag die Öffnung zuvor im Bild bei 3,7 px und war kaum zu sehen; der Blick bleibt, wo er ist, wenn er abgewandt war — sonst wendet er sich ab wie beim Sprechen (`blickWeiter`).
- **Antwort:** A0 — der Denkblick läuft in die ersten Worte hinein, `min(2,23 s · U(0,65; 1,35); 40 % der Antwort)` (Andrist 2013: das Denk-Wegsehen endet 2,23 s nach Beginn der Äußerung) — **über A0 gleitet das Gesicht in die Emotion der Antwort (§17.3)**; dann F16 mit kurzem Brauenheben (0,6 s); dann A1 und A2 im Wechsel, Wegsehen 1,96 s alle 4,75 s (je · U(0,65; 1,35)); **die letzten 1,5 s beim Betrachter** — der Sprecher gibt das Wort mit dem Blick zurück (Kendon 1967; Ho 2015).
- **Nachklang:** beginnt mit F16 (1,5–3 s, Blick zum Gegenüber), dann Zyklen der Nachklang-Gruppe. Seine Dauer ist eine Grenze: Die laufende Form endet an ihr.

### 17.6 Lidschlag

- **Rate je Minute:** Grundrate je Zustand (Rauschen 15, Nachdenken 12, Antwort 20, Nachklang 15) + 12·E; Angst +6, Trauer −2, während F4 +3; begrenzt auf 8–32. Ärger beschleunigt nicht (entschieden, `novaberg-avatar_k.md` §3).
- **Zwei Quellen:** ein Poisson-Prozess mit 0,8 s Sperrzeit und gekoppelte Lidschläge — am Blickwechsel über 0,4 mit Wahrscheinlichkeit 0,7, **im Nachdenken 0,3** (entschieden), ein langer beim Einfall, eine Serie aus 2–3 nach Denklast (F5), während F5 keine. ~~Die gekoppelten der letzten 60 s werden von der Poisson-Rate abgezogen.~~ → **Seit 03.10.2026 zählen nur die gekoppelten des laufenden Zustands**, als Rate über seine bisherige Dauer (höchstens die letzte Minute, als Fenster mindestens 10 s), und diese Rate wird von der Poisson-Rate abgezogen. Anlass: Über die Grenze des Zustands hinweg erbte eine kurze Antwort den Abzug aus dem Rauschen; bei Ärger 0,9 mit gleicher Energie lag sie mit den Startwerten 21–60 unter dem Rauschen (Nachdenken 21,0 · Rauschen 31,6 · Antwort 23,7 je Minute) — die Rangfolge der Entscheidung (Nachdenken < Rauschen < Antwort) hielt nur mit den Startwerten 1–20. **Ausnahme seit 04.10.2026 (L0′b): Der Nachklang zählt die gekoppelten ab dem Beginn der Antwort** (`Z.lidSeit`).
- **Die Abstände seit 04.10.2026 (L0′b):** ~~exponentialverteilt; ein in der Sperrzeit fälliger Lidschlag wurde auf ihr Ende verschoben~~ → Nach jedem Lidschlag sperrt der Generator 0,8 s; der nächste Poisson-Lidschlag folgt nach Sperrzeit + Gamma(3) mit gleichem Mittel (die Summe dreier Exponentialziehungen, in fester Reihenfolge). Wird er in der Sperrzeit fällig, etwa nach einem Lidschlag am Blickwechsel, wird er ab ihrem Ende **neu gezogen**, nicht verschoben. Nach dem langen Lidschlag des Einfalls sperrt er 1 s. **Am Ende der Antwort fällt genau ein Lidschlag** (fiel in den 0,8 s davor schon einer, bleibt es dieser), danach sperrt er 1,5 s — so lange wie das kürzeste F16 am Beginn des Nachklangs. Anlass, gemessen am 04.10.2026: Paare im Abstand von genau 0,8 s (das verschobene Ende der Sperre), Gruppen von 2–3 an jedem Blickwechsel mit Pausen bis 22 s, und bis zu fünf Lidschläge in 4 s nach dem Ende der Antwort.
- **Form:** Schließen 80–100 ms, **ganz geschlossen 40 ms (seit 04.10.2026)**, Öffnen 150–250 ms, je × Lidform; länger bei F4 und Trauer (× 1,2) — **der Faktor der Form, die gerade beginnt** (bis 03.10.2026 trug ein Lidschlag am Beginn einer Form den der vorigen). **Beim Einfall genau ein langer Lidschlag:** Er ersetzt den am Blickwechsel und ~~den ersten einer fälligen Serie nach F5~~ → **seit 04.10.2026 die ganze fällige Serie nach F5** (bis 03.10.2026 fielen zwei auf denselben Zeitpunkt, nach F5 überschrieb der kurze den langen). **Beginnt ein Lidschlag, während der vorige läuft, setzt er an dessen Öffnung an** (seit 04.10.2026), statt das Lid aufspringen zu lassen.
- **Das geschlossene Auge** ist seit 04.10.2026 unter einer Öffnung von 0,06 (bis dahin 0,12) gezeichnet, mit dem Strichgewicht der Wimpernlinie und 8 Wimpernbüscheln — vorher ein dünner Strich ohne Wimpern, im Bild schneller zu als die Logik (Fundliste, 04.10.2026).
- **Gemessen im Generator mit dem Abzug je Zustand** (03.10.2026, 13:28 UTC, je Lage 40 Startwerte × drei Antwortlängen, `leerlauf_pruefen.py` 360 Läufe): Freude 0,6 gegen Pixies Neugier 0,45 Nachdenken 17,3 · Rauschen 20,7 · Antwort 27,0 je Minute; Ärger 0,9 gegen Pixie 0,9 22,1 · 27,5 · 30,0; Hoffnung 0,7 gegen Neugier 0,7 19,2 · 24,3 · 27,6 — jeder Zustand nahe seiner Rate (Ärger: 22,8 · 25,8 · 30,8). Die Messungen der nachgestellten Referenz stehen in `novaberg-avatar_b.md` §18 (L0′a, L0′b).
- ~~**Gemessen im Generator** (03.10.2026, je Lage 20 Startwerte × drei Antwortlängen): bei Freude 0,6 gegen Pixies Neugier 0,45 Nachdenken 16,2 · Rauschen 22,6 · Antwort 29,5 je Minute. Die Energie hebt die Rate in jedem Zustand; hat Nova deutlich mehr Energie als Pixie (Ärger 0,9 gegen Neugier 0,45), blinzelt sie im Nachdenken etwas öfter als im Rauschen (23,0 gegen 21,5; gemessen in einem Lauf derselben Prüfung mit Pixie bei 0,45 — seitdem fährt die Prüfung die Ärger-Lage mit gleicher Energie).~~ → überholt durch den Abzug je Zustand (oben).

### 17.7 Die Lage im Raum in v1

Der Generator nimmt die Lage im Novaberg-Raum als Eingang — Energie E, Valenz V, Richtung R, Tiefe T, Nähe N. **In v1 folgen E und V der Emotion des Zustands, R, T und N stehen fest:** E = Arousal — **im Nachklang klingt E seit 04.10.2026 (L0′b) mit Novas Emotion aus**: E = A·(1 − 0,5·min(1, p/0,6)) mit A dem Arousal der Antwort und p dem Anteil des Nachklangs, danach die Überblendung zu Pixie; V = Valenz des Sektors, moderat oder intensiv je nach Arousal unter oder ab 0,6 (die Tabelle wie `EMOTION_VALENZ` in `server/config.py`; zur fehlenden Reserve `AVATAR-VALENZ-RESERVE`); R offen, T 0,3, N 0,5 — der Kaltstart des Raums (`novaberg-gv-strategie_t.md` §3.4). Den Raum an den Client zu übertragen ist eine eigene, spätere Absicht.

### 17.8 Datenvertrag: was der Leerlauf braucht

Gelesen am 03.10.2026; die Fundstellen sind die dieses Tages.

| Was | heute | Zu bauen |
|---|---|---|
| **Ein Turn beginnt** | Der Client sendet in `MainWindow._send_current_input` (`client/ui/main_window.py`); kein Panel erfährt es — `PanelBase` kennt nur `on_turn_received` | ein Verteiler an die Panels, die es wollen — nach dem Muster von `REACTS_TO_IMPULSE`: Panels mit `REACTS_TO_IDLE = True` bekommen `on_idle_event(ereignis)`, mit den Ereignissen `turn_beginnt`, `turn_gescheitert`, `pixie_auftrag` und `impuls_denkt` (~~Vorschlag — `PanelBase` ist eine gemeinsame Klasse, ihre Erweiterung ist eine Architekturentscheidung~~ → **entschieden 04.10.2026**, §17.10; die Namen von Merkmal und Methode wählt der Bau). `turn_beginnt` auch, wenn der Nutzer aus einem anderen Client schreibt (`user_message`) |
| **Die Antwort trifft ein** | `on_turn_received` mit ~~`nova_emotion`, `nova_arousal`~~ → `emotion`, `arousal` (seit 04.10.2026, §14.2), `antwort`, auch aus eigenem Impuls (§16, B2) | nichts |
| **Die Wiedergabe endet** | die Sprechschicht weiß es (`SpeechState.active`, `start_ms`, `end_ms`) | die Puppe meldet das Ende an die Leerlauf-Schicht — **gebaut in L2 (03.10.2026):** Die Puppe rechnet die Dauer beim Eintreffen aus dem Text (`speech_timeline`) und gibt sie mit der Antwort an die Logik; die Logik lässt die Wiedergabe danach enden, und das Sprechen beginnt erst, wenn die Logik die Antwort beginnen lässt |
| **Der Turn scheitert** | WebSocket `turn_gescheitert` (`client/ui/stream_handler.py`), nur an den Chat | dasselbe Ereignis an `on_idle_event`; **ebenso ein Fehler beim Senden** (`StreamHandler` → `MainWindow._handle_error`, seit 04.10.2026) — davon erfährt der Server nie, und ohne ihn dächte Nova bis zum Wächter |
| **Pixie beginnt oder beendet einen Auftrag** | nur in Redis (`shadow_status`, `server/services/pixie/scheduler.py`, `pixie_heartbeat`), gelesen per REST; ~~**nichts geht an den Client**~~ → **seit 04.10.2026 (L4)** sendet der Heartbeat `pixie_auftrag` (`novaberg-avatar_b.md` §18) | **Server:** WebSocket-Ereignis `pixie_auftrag` mit `phase` (`beginn`/`ende`), `spur` (`llm`/`cpu`), `art`, `emotion` (kanonischer Name), `arousal` (0..1) — **`emotion` und `arousal` fehlen, wenn der Auftrag keine trägt** (abwesend, nicht leer: `novaberg-convention-event-model.md`); ~~**ohne `thema`**: das Thema ist Gesprächsinhalt.~~ → **mit `thema`, seit 04.10.2026** — für den Tooltip der Statuszeile (`novaberg-avatar_k.md` §3); das Panel des Avatars gibt es nicht an die Puppe weiter. **`beginn`**, wenn ein Gewinner feststeht und sein Lauf beginnt; **`ende`**, wenn dieser Lauf vorbei ist, auch mit Fehler — **nicht** am Zurücksetzen von `shadow_status`: Das `finally` des Heartbeats setzt den Schlüssel auch nach jedem leeren Heartbeat zurück (CPU-Spur alle 30 s), und beide Spuren teilen ihn. **Gesendet mit `await broadcast(…)`** — `pixie_heartbeat` läuft als async-Job im Event-Loop (`AsyncIOScheduler`, `server/main.py`); `broadcast_threadsafe` wartete dort auf eine Coroutine desselben Loops und hielte den Server 5 s je Verbindung an (`server/api/websocket.py`, `future.result(timeout=…)`). Ein Fehler beim Senden stört den Auftrag nicht und schreibt eine Error-Zeile. **Nur Aufträge mit Nutzer** senden; periodische Aufgaben tragen weder Emotion noch Nutzer und bleiben ohne Ereignis. Backlog `PIXIE-START-ALS-EREIGNIS` |
| **Ein Impuls geht in den CharacterGraph** | die Zustellung (`server/services/shadow_delivery.py`, `_delivery_ausfuehren`) fährt nur den AgentGraph und legt ein Ereignis in die Queue; den CharacterGraph fährt danach der Event-Consumer (`server/services/event_consumer.py`, Herkunft `reiz_herkunft = eigener_impuls`). Seine Stufen sind von denen eines Nutzer-Turns nicht zu unterscheiden; **seit 04.10.2026 (L4)** meldet der Event-Consumer `impuls_denkt` | **Server:** WebSocket-Ereignis `impuls_denkt` mit `phase` `beginn`, wenn der Event-Consumer den CharacterGraph für einen Impuls startet, und `ende` in seinem `finally` — auch wenn keine Antwort entsteht; ohne Inhalt; async gesendet wie oben. **Client:** `ende` beendet nur ein Nachdenken, auf das keine Antwort kam; die Antwort geht schon bei `perzeption_assistant` hinaus, das `ende` kommt danach |

**Woher Pixies Emotion kommt:** Ein Auftrag (`ShadowAuftrag`) trägt `emotion` und `arousal` aus der Salienz des Turns, der ihn ausgelöst hat (`server/memory/kzg.py`, `server/agents/kzg/queues.py`; `beobachter = "user"` gesetzt in `server/services/shadow_agent/utils.py`); `None` heißt unbekannt.

**Die Art des Auftrags** kommt aus der geschlossenen Menge der Aufgaben in `server/services/pixie/router.py`, nie als Freitext. Für die Gewichte des Rauschens (§17.4): `recherche`, `vertiefen`, ~~`verweis`~~ → `wissen_verweis` (so heißt die Art im Router, nachgesehen 03.10.2026), `wissen_rueckweg` → Recherche; `nachfragen` → Reflexion; jede andere → keine Gewichtung. Die Intention *Reflexion* bildet der Server heute auf `recherche` ab (`server/agents/kzg/queues.py`); die Wissenslücke ist eine periodische Aufgabe und sendet kein Ereignis — beide Gewichte des Generators bleiben damit in v1 ohne Anlass. Periodische Aufgaben tragen keine. **Eine eigene Emotion Pixies gibt es nicht** — *„dieser [Auftrag] hat Emotionen“* (Absicht §3) ist genau diese.

**Der Avatar bekommt weiter keinen Gesprächsinhalt** (§2, §14.4): kein Thema, keinen Text des Auftrags. Das Thema eines Auftrags erreicht seit 04.10.2026 den Client — für die Statuszeile, nicht für den Avatar.

### 17.9 Abweichungen vom Generator

| Generator | Client | Grund |
|---|---|---|
| Bedienung im Platz des Mischpults, Anker `#sim`, `#aufnahme` | entfallen | Testbedienung (§15.4) |
| Das Ende des Nachdenkens ist vorab bekannt (`denkEnde`) | Der Client kennt es nicht; das Einatmen beginnt, wenn die Antwort eintrifft, und die Wiedergabe beginnt danach — ≈ 0,8 s später als heute | Ereignis statt Plan; ohne Ton (O9) verschiebt sich nichts Hörbares |
| `performance.now()` | die Zeit der Frame-Clock (§15.2, *eine Uhr*) | — |
| Pixies Emotion, Aktivität und Auftragsart von Hand | aus `pixie_auftrag` (§17.8) | — |
| Raum über Regler | fest wie §17.7 | der Client bekommt den Raum nicht |
| Lidschlag ersetzt `drawEye` des Prototyps | ersetzt das Blinzeln der Puppe (`puppet.py`; `_blink` seit L2 entfernt) | dieselbe Form, ein Ort |
| Anker `#kopf=0`, `#drehung=1`; mit `#sim` und `#drehung=1` zeichnet der Prototyp den Kopf ungedreht | entfallen | Prüfbedienung: `#kopf=0` ist der Zwilling ohne Kopf, `#drehung=1` schreibt die Rechnung der Verformung, die die Prüfung gegen `yaw.json` hält; ungedreht, weil ein gedrehtes Bild im Browser ohne Grafikkarte rund 0,8 s kostet. ~~Im Client ist der Faktor des Kopfes eine Konstante~~ → **seit L1′ (05.10.2026)** schaltet `IdleLogic(…, head_turn=False)` die Drehung ab — der Zwilling ohne Kopf in den Zeugen (Y5); die Puppe dreht immer |
| Kanal `yaw` unter den Zielen des Gesichts; die Feder des Kopfes (ω 3,5) im Generator | **seit L1′ (05.10.2026):** Die Logik liefert das Kopfziel `head_yaw` neben dem Gesicht, nicht in `FaceState`; die Feder (ω 3,5) führt die Puppe (§15.2) | Ein Feld in `FaceState` hätte die Zeugen gebrochen, die `FaceState` aus Referenzen ohne `yaw` bauen; die Feder ist Bewegung, kein Plan, und gehört wie die Federn der übrigen Kanäle in die Puppe |
| `h` je Form aus eigener Quelle, `#kopf=0` | `h` je Form kommt aus einer eigenen Quelle mit dem Startwert `head_seed(seed)` und wird auch bei abgeschalteter Drehung gezogen; der Plan ist mit und ohne Drehung derselbe | wie im Generator mit `kopf=0`; keine Abweichung im Verhalten, nur die Form des Schalters |


**Vor dem Bau** wird der Generator an das Ereignismodell des Clients angeglichen — das Einatmen beginnt beim Eintreffen der Antwort, Pixies Auftrag kommt als Ereignis —, damit die Referenzwerte dieselben Ziehungen in derselben Reihenfolge tragen (`novaberg-avatar_b.md` §18, L0). → **Angeglichen am 03.10.2026.** Dabei entschieden (Form, nicht Absicht): Im Einatmen gilt noch Novas Emotion vor der Antwort, die neue ab dem ersten Laut; kommt die Antwort ohne Nachdenken, besteht das Nachdenken nur aus dem Einatmen, ohne Zyklus davor; eine zweite Antwort im Einatmen ersetzt die wartende, eine Antwort in der Antwort löst sie sofort ab; ein neuer Turn verwirft eine wartende Antwort; `turn_gescheitert` und `impuls_denkt` `ende` wirken nur auf ein Nachdenken, auf das keine Antwort kam; die Art des Auftrags kommt vom selben Auftrag wie der Rückfall, ohne Auftrag mit Emotion vom zuletzt begonnenen; ein Auftrag, der beim Start schon läuft (Zeit ≤ 0), setzt den Rückfall vor dem ersten Zyklus. **Ein Impuls stört weder einen Turn noch das Gespräch** — abgeleitet aus der Entscheidung zu Pixies Start (`novaberg-avatar_k.md` §3: *„darf aber konvergentes Denken in Turns und die User-Interaktion nicht stören“*): `impuls_denkt` `beginn` im Nachdenken eines Turns, im Einatmen und in der Antwort bleibt ohne Wirkung, `ende` beendet nur ein Nachdenken, das ein Impuls begann; `turn_gescheitert` nur eines, das ein Turn begann.

**Lücken, die die zweite Kontrolle der Referenz fand** (03.10.2026; der Generator beantwortet sie so, die Absicht sagt nichts): *beim Betrachter* ist nicht beziffert — die Prüfungen nehmen |x| ≤ 0,12 und |y| ≤ 0,15, und F12 (*ins Leere oben*, 0,10–0,25 zur Seite) liegt am Rand darin; F16 als Akzent am Schluss eines Zyklus steht 1–2 s, unter der Mindestdauer der übrigen Formen (§17.4); ein Lidschlag am Blickwechsel fällt in die Sperrzeit nicht, wirksam koppelt er deshalb mit etwa 0,5 statt 0,7; ob *während F5 keine* auch den Lidschlag am Beginn von F5 meint; F16 als Akzent kann auch einen Zyklus des Nachdenkens schließen — die Abnahme nennt dort nur F5 und F9 beim Betrachter.

### 17.10 Der Weg der Arbeitszyklen im Client

**Entschieden am 04.10.2026** (`novaberg-avatar_k.md` §3), auf einen Architekturentwurf, der am Bestand auf `fdf88ed` geprüft war; die Fundstellen sind die dieses Tages. Bauteile: `novaberg-avatar_b.md` §18, L3 und L5.

**Eine Quelle, zwei Empfänger.** Die vier Ereignisse der Arbeitszyklen (§17.8) erreichen das Avatar-Panel und die Statuszeile über denselben Weg:

1. **Eingang.** Der Stream-Handler bekommt einen eigenen Zweig für `turn_gescheitert`, `pixie_auftrag` und `impuls_denkt` und gibt sie über `GLib.idle_add` an einen neuen Rückruf des Hauptfensters. `turn_gescheitert` behält, was es heute tut — die Kennungen abräumen, die Stufe „Ausfall“ zeigen —, und geht zusätzlich diesen Weg. `turn_beginnt` entsteht im Client: beim Senden (`MainWindow._send_current_input`) und bei einer Nachricht des Nutzers aus einem anderen Client (`user_message`). Ein Fehler beim Senden wirkt wie `turn_gescheitert`.
2. **Typ.** Je Ereignis ein eigener, unveränderlicher Typ **ohne Zeit**, im UI-Teil des Clients und ohne GTK; aus der Nutzlast bildet ihn **eine** Funktion beim Eingang. Eine ungültige Nutzlast ergibt eine Error-Zeile und kein Ereignis; fehlen `emotion` und `arousal`, bleiben sie leer (`None`), statt einen Wert zu erfinden.
3. **Arbeitszustand.** Das Hauptfenster besitzt ihn, wie Statuszeile und Registry. Er hält die laufenden Aufträge Pixies je Spur — Art, Emotion, Thema — und ob der CharacterGraph für einen Turn oder einen Impuls denkt. **Der Turn folgt der Menge der offenen Nachrichten, nicht einem einzelnen Wahrheitswert:** Eine Antwort kann mehrere Nachrichten beantworten, zwei Nachrichten können einzeln beantwortet werden. Fortgeschrieben wird er in reinen Funktionen, ohne Fenster prüfbar wie `client/ui/turn_routing.py`. Jedes Ereignis erreicht zuerst ihn; dann setzt er den Text der Statuszeile — **als ihr einziger Schreiber** — und gibt das Ereignis an die Panels weiter. Die Antwort beendet das Denken eines Turns, die Antwort aus Impuls das eines Impulses; an die Panels geht die Antwort wie bisher über `on_turn_received`.
4. **Verteiler.** `PanelBase` bekommt ein Merkmal und eine leere Methode (bisher hier `REACTS_TO_IDLE`/`on_idle_event`; die Namen wählt der Bau). Eine Funktion ohne GTK neben `deliver_turn` wählt die Panels **nach dem Merkmal allein**, ohne Bedingung an `CATEGORY`; ein Panel, dessen Methode scheitert, wird als Fehler geschrieben und hält die übrigen nicht auf. Wie jede Verteilung der Registry erreicht sie nur Panels mit `UNIQUE` — nur die führt sie als offen.
5. **Im Avatar-Panel.** Es übersetzt den Typ in die Ereignisse der Leerlauf-Logik (`TurnBegins` …, `client/avatar/idle.py`) und gibt `pixie_auftrag` ohne Thema weiter. Es merkt jedes Ereignis vor und übergibt es im nächsten Bild mit der Zeit der Frame-Clock an die Puppe, in der Reihenfolge des Eintreffens — wie heute die Antwort (§15.2, *eine Uhr*). Ist das Panel geschlossen, rechnet niemand den Avatar.
6. **Öffnen.** Öffnet das Panel, während der CharacterGraph für einen Turn oder einen Impuls denkt, beginnt es im Nachdenken, sonst im Rauschen. Mehr als das übernimmt es nicht: Novas Emotion ist beim Öffnen unbekannt (neutral), und laufende Aufträge Pixies reicht niemand nach — **das nächste Start-Ereignis bringt Emotion und Art.**
7. **Statuszeile.** Sie nennt je laufendem Arbeitszustand die Art der Aufgabe: „Charakter-Berechnung“ für den CharacterGraph bei Turn und Impuls, für Pixie die Art des Auftrags lesbar („Recherche“, „Vertiefung“ …), aus der geschlossenen Menge des Routers (§17.8). Weitere Angaben wie das Thema stehen im Tooltip. *idle* steht nur, wenn nichts läuft. Der Wächter von 600 s gilt auch hier. **Das Momentum entfällt** — es ist ein Wert des Turns, kein Zustand Pixies, und überschriebe die Arbeit.

**Warum der Server erst nach L3 sendet:** Heute fällt jeder unbekannte Typ in den Auffangzweig des Stream-Handlers (`_ws_on_message`, `text = nachricht or json.dumps(data, …)`) und erscheint über `MainWindow._handle_impulse` im Chat als hervorgehobene Bubble — als Wort Novas. `pixie_auftrag` und `impuls_denkt` tragen kein `nachricht`; jeder Auftrag schriebe zwei JSON-Zeilen in den Chat. Der Server lädt neuen Code sofort (`--reload`). Deshalb lernt der Client **alle vier** Typen schon mit L3, und L4 geht erst nach dessen Commit in den laufenden Baum. → **Seit L3 (04.10.2026)** gehen `pixie_auftrag` und `impuls_denkt` nicht mehr in den Auffangzweig (`novaberg-avatar_b.md` §18); für jeden weiteren neuen Typ des Servers gilt der erste Satz weiter.

**Verworfen:**

| Variante | Grund |
|---|---|
| Ein Abonnement, an dem sich Panels und Statuszeile an- und abmelden | allgemeine Infrastruktur für zwei Empfänger; ein Panel hat keinen Abbau-Hook (§15.4), und ein vergessenes Abmelden ließe ein geschlossenes Panel weiter Ereignisse bekommen |
| Das Panel bezieht die Ereignisse selbst, `PanelBase` wächst nicht | das Panel kennt weder Hauptfenster noch Stream-Handler; ein globaler Zustand oder Abfragen kehrten die Richtung Hauptfenster → Registry → Panel um |
| Die Registry ruft jedes Panel mit passender Methode (`hasattr`), ohne Merkmal | die Auswahl hinge still an einem Namen; ein Tippfehler im Panel ließe es nie etwas bekommen, ohne dass ein Zeuge es merkt |
| Die Klassen der Leerlauf-Logik über die Grenze | sie tragen die Zeit einer Puppe (ms ab ihrem ersten Bild); ohne offenes Panel gibt es keine, und die Statuszeile hinge am Paket des Avatars |
| Das Dict der Nutzlast durchreichen, wie `on_turn_received` | bei zwei Empfängern prüfte jeder dieselben Felder selbst, und ob ein Feld fehlt oder leer ist, hinge an jeder Lesestelle |
| Jeder Empfänger hält seinen Zustand selbst | die Regel *idle erst, wenn alles fertig ist* stünde zweimal |
