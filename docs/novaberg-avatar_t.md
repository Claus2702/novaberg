# Novaberg — Emotions-Avatar: Ausarbeitung

**Teil von:** `novaberg-avatar_k.md` — dort Absicht, Kopfblock und die Tabelle „§ → Datei“
**Stand:** 02.10.2026
**Inhalt:** wie die Absicht ausgearbeitet ist — Darstellungsstil, Parameterraum `FaceState`, Emotions-Mapping, Intensität und Mischung, Übergangsmodell, Schichten, Integration im Client (§3–§9); aus dem Prototyp die Pipeline der Figur, die Alternative zur Vorlage, das bewegliche Kinn, die Sprechschicht, die Muskelkanäle des Mundes und die Einzellaute (§13 in Teilen).

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
   → Schicht 3 blendet weich ein und legt Öffnung, Kiefer und Muskelkanäle additiv auf die Emotion; die Breite wirkt als Faktor auf die Emotionsbreite (W10, §13.12, §13.13).

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
