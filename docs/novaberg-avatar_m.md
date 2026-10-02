# Novaberg — Emotions-Avatar: Messungen

**Teil von:** `novaberg-avatar_k.md` — dort Absicht, Kopfblock und die Tabelle „§ → Datei“
**Stand:** 02.10.2026
**Inhalt:** Befunde am Prototyp und Messungen an Fotos und Videos sprechender Personen, je mit Datum, Material und Umfang (§13.2, §13.4–§13.7, §13.15, §13.16).

---

## 13. Figur aus Vorlage (Prototyp, 29.09.2026)

*Teil Messungen. Die übrigen Unterabschnitte von §13: Einleitung, 13.1, 13.3, 13.9, 13.12–13.14 in `novaberg-avatar_t.md`; 13.8, 13.10, 13.11 in `novaberg-avatar_b.md`.*

### 13.2 Befunde (Sichtprüfung, keine Messung)

| Befund | Bewertung |
|---|---|
| Mund- und Lachfaltenbereich lassen sich sauber entfernen | tragfähig |
| Augenbereiche bleiben nach dem Entfernen als leicht hellere Flächen erkennbar | wird von den gezeichneten Augen weitgehend verdeckt; für ein Produkt ist eine bessere Füllung nötig (z. B. Lidschatten-Schraffur mitzeichnen oder Vorlage mit geschlossenen, glatten Augenpartien anfertigen lassen) |
| Gezeichnete Merkmale wirken grafischer als die feine Vorlage | nach Detail-Überarbeitung (Iris-Fasern, Lidschatten, gebüschelte Wimpern, Lippenrillen, einzelne Zähne) deutlich reduziert; Zähne und Brauen wirken noch am stärksten gezeichnet |
| Zähne als feste Kieferebenen hinter der Lippenöffnung | wirkt deutlich realistischer als mitskalierende Zähne; Sprechen öffnet nur den Unterkiefer |
| Zeichenlast mit vollem Detail | gemessen 52–53 Frames/s, Headless-Chromium, 1200 × 900, Pixeldichte 2 — kein Messwert für den GTK4-Client (Cairo), dort neu messen |
| Freude, Überraschung, Angst, Trauer gut unterscheidbar | tragfähig |
| Trauer, Enttäuschung und Ärger liegen im Mund nah beieinander, Unterschied trägt vor allem die Brauenstellung | bestätigt die Schwäche aus Abschnitt 5 für diese Figur |

### 13.4 Mundproportionen (Stand 01.10.2026)

**Anpassung nach Sichtprüfung Meister:** Lippen voller (Oberlippe 14 → 17 px,
Unterlippe 19 → 23 px Volumen in Vorlagen-Pixeln). Mundbreite relativ zum
bisherigen Sektorwert: Zuversicht +5 % (90 → 94,5), Angst +15 % (64 → 73,6),
Überraschung +30 % (50 → 65). Neutral = 78. Überraschung bleibt damit schmaler als Neutral.

**Literaturbefund (FACS, qualitativ):**

| Sektor | Mund-Action-Units | Wirkung auf die Mundgeometrie |
|---|---|---|
| Freude | AU12 Lip Corner Puller (+ AU25/26) | Mundwinkel nach oben, hinten und seitlich, Mund breiter |
| Angst | AU20 Lip Stretcher + AU25/26 | Mundwinkel seitlich gestreckt, Mund breiter, leicht geöffnet |
| Überraschung | AU25 Lips Part + AU26 Jaw Drop | Kiefer fällt entspannt, Öffnung vor allem senkrecht, kein Strecken |
| Trauer | AU15 Lip Corner Depressor | Mundwinkel nach unten |

Konsequenz: Die Verbreiterung bei Angst ist durch AU20 gedeckt. Bei Überraschung
trägt die Öffnung die Höhe, nicht die Breite.

**Quantitative Daten: noch keine gefunden.** Die gesichteten Arbeiten nutzen
Landmarken-Abstände als Klassifikator-Merkmale, berichten aber keine
Mundbreite/-höhe je Emotion relativ zu Neutral. Eine Motion-Capture-Studie
(Mundwinkel-Marker) zeigt bei spontaner Angst größere Mundbreitenänderung als
bei Überraschung; bei gestellten Ausdrücken überlappen beide stark.

**Vorschlag Messung:** Bildset mit Neutral und Emotionen derselben Person
(z. B. RaFD, KDEF, CK+, FACES; Forschungslizenzen beachten), lokal Landmarken
erkennen, Mundbreite und -höhe auf den Augenabstand normieren, Verhältnis zu
Neutral je Emotion mitteln. Ergebnis ersetzt die Augenmaß-Werte in `SECTORS`.

### 13.5 Messung an einer Fotoserie (01.10.2026)

**Material:** Collage, 28 Aufnahmen derselben Frau, 7 × 4, je ca. 155 × 151 px.
Augenabstand nur
ca. 32 px — ein Pixel entspricht ca. 3 %.

**Methode (ohne Landmarken-Modell):**
- Maßstab: einheitlicher Augenabstand 32,5 px (Pupillen bei geradeaus blickenden
  Aufnahmen), je Aufnahme mit der Kopfbreite skaliert (66–70 px, ±3 %).
  Pupillen je Aufnahme waren unbrauchbar (25,6–38,6 px durch Zusammenkneifen,
  Aufreißen, Blickrichtung).
- Mundwinkel: Lippenfarbe (LAB a*) + Mundinneres; bei drei Lächeln lag die
  Erkennung auf der Wangenröte → von Hand gesetzt.
- Ober-/Unterlippe, Öffnung: an der Mundmitte von Hand abgelesen (±0,5 px).
- Neutral: Median aus r3c1, r4c1, r4c7 (keine eindeutig neutrale Aufnahme;
  r4c7 allein lächelt leicht und ist 20 % breiter als r3c1).
- Emotionszuordnung: **eigene Sichtung, keine Labels der Bildquelle.**
- r4c4 ausgeschlossen (Hand verdeckt den Mund). Mundwinkelhub verworfen
  (Höhenlage der automatisch gefundenen Winkel unplausibel).

**Ergebnis Mundbreite relativ zu Neutral (Median):**

| Sektor | Aufnahmen | gemessen | Avatar heute | Vorschlag `mw` (Neutral 78) |
|---|---|---|---|---|
| 1 Freude intensiv | r1c2, r3c5, r1c5 | ×1,45 | ×1,38 | 113 |
| 1 Freude moderat | r1c6, r1c7, r3c4 | ×1,37 | — | — |
| 2 Zuversicht | r4c6 (n = 1) | ×1,14 | ×1,21 | 89 |
| 3 Angst | r3c3, r2c6 | ×1,10 | ×0,94 | 86 |
| 4 Überraschung | r1c1, r2c4, r2c5 | ×0,94 | ×0,83 | 73 |
| 5 Trauer | r2c7, r3c6, r3c7 | ×1,04 | ×0,90 | 81 |
| 6 Ekel (Näherung) | r2c3, r1c3, r2c2 | ×1,02 | ×0,97 | 80 |
| 7 Ärger (Lippen vorgeschoben) | r2c1 (n = 1) | ×0,87 | ×1,00 | 68 |
| 8 Neugier (Seitenblick) | r4c5 (n = 1) | ×0,97 | ×0,90 | 76 |

**Öffnung (Lippenspalt Mitte, Augenabstand = 1):** Überraschung 0,126
(Avatar-`mo` ≈ 22, heute 46), Freude intensiv 0,164 (≈ 29, heute 40),
Angst 0,017 (≈ 3, heute 18), Ärger 0 (heute 10).

**Lippen Neutral absolut:** Oberlippe 0,079 (Avatar 0,059 → ca. ×1,3 zu dünn,
Basis-Offset 17 → ca. 23), Unterlippe 0,105 (Avatar 0,110, passt).

**Bewertung:** Eine Person, gestellte Ausdrücke, sehr kleine Auflösung, Neutral
nicht eindeutig — Richtwerte, keine Messung im Sinne eines Korpus. Die
Korrekturen vom 01.10. (Angst, Überraschung breiter, Lippen voller) gehen in
die Richtung der Messung; Überraschung und Angst sind laut Messung noch breiter,
Überraschung deutlich weniger geöffnet. Validierung
an einem Bildset mit vielen Personen steht aus.

### 13.6 Zweite Collage, Vergleich zweier Personen (01.10.2026)

**Material:** 16 Aufnahmen einer zweiten Person, 4 × 4, Augenabstand ca. 27 px.
Kopfgrößen schwanken → Maßstab je Aufnahme über den eigenen Augenabstand.
Augen, Mundwinkel und Mundmitte vollständig von Hand abgelesen (±1 px bzw. ±0,5 px).
Ausgeschlossen: r3c3 (Zunge), r4c1 (aufgeblasene Wangen). Neutral eindeutig (r1c1);
Gegenprobe r3c1 (Augen zu) weicht nur um 2 % ab.

**Mundbreite relativ zu Neutral:**

| Sektor | Person 1 | Person 2 | Mittel | Avatar heute | Vorschlag `mw` |
|---|---|---|---|---|---|
| 1 Freude intensiv | ×1,45 | ×1,41 | ×1,43 | ×1,38 | 112 |
| 2 Zuversicht | ×1,14 | ×1,15 | ×1,15 | ×1,21 | 89 |
| 3 Angst | ×1,10 | ×1,14 (Lippen gestreckt) | ×1,12 | ×0,94 | 87 |
| 4 Überraschung | ×0,94 | ×1,08 | ×1,01 | ×0,83 | 79 |
| 5 Trauer | ×1,04 | — | ×1,04 | ×0,90 | 81 |
| 6 Ekel (Näherung) | ×1,02 | ×0,99 | ×1,00 | ×0,97 | 78 |
| 6 Skepsis | ×1,13 | ×1,07 | ×1,10 | — | — |
| 7 Ärger | ×0,87 (n = 1) | — | ×0,87 | ×1,00 | 68 |
| 8 Neugier | ×0,97 (n = 1) | — | ×0,97 | ×0,90 | 76 |

Weitere Aufnahmen Person 2 (Zuordnung unsicher): Lippe gebissen ×1,23,
Schrei (Angst oder Wut) ×1,04 mit Öffnung 0,356.

**Öffnung (Augenabstand = 1):** Überraschung 0,126 / 0,127 (sehr gut
übereinstimmend → `mo` ≈ 23, heute 46); Freude intensiv 0,164 / 0,184
(→ `mo` ≈ 31, heute 40).

**Lippen Neutral absolut:** Oberlippe 0,079 / 0,121, Unterlippe 0,105 / 0,189.
Stark personenabhängig. Beide Personen haben eine deutlich dickere Oberlippe als
der Avatar (0,059) → Erhöhung bestätigt. Unterlippe Avatar (0,110) liegt an der
unteren Grenze.

**Bewertung:** Zwei Personen, gestellte Ausdrücke, Handablesung — Richtwerte.
Freude, Zuversicht, Angst, Ekel und die Öffnung bei Überraschung stimmen
zwischen beiden Personen auf ±4 % überein. Überraschung (Breite), Trauer, Ärger
und Neugier stützen sich auf wenig oder widersprüchliches Material.

### 13.7 Collagen 3 und 4, Gesamtauswertung (01.10.2026)

**Material:** Collage 3: 9 Aufnahmen, Augenabstand ca. 50 px, Neutral vorhanden
(r2c2). Collage 4: 9 Aufnahmen, Augenabstand ca. 64–78 px, **kein Neutral** —
nach Augenschein dieselbe Person wie Collage 3 (nicht gesichert), daher Bezug auf
das Neutral aus Collage 3 (Mundbreite 0,687 Augenabstände). Ausgeschlossen bzw.
nur teilweise: c4 r3c1 (Hand verdeckt Mund), c4 r1c3 (rechter Mundwinkel verdeckt),
c4 r3c2 (Hand drückt Wange, nicht als Neutral verwendbar).

**Einzelwerte Person 3 (Breite × Neutral, Öffnung in Augenabständen):**
Freude ×1,26 / ×1,36 / ×1,37 (Öffnung 0,14 / 0,20 / 0,39) · Überraschung O-Mund
×0,72 (0,25), „Oh“ gespitzt ×0,80 (0,08) · Trauer Weinen ×1,29 (geschlossen),
×1,43 (offen, 0,23), Schmollmund ×1,11 · Missbilligung ×1,04 · Genervt/Ekel ×1,13
· Ärger Schrei ×1,04 / ×0,97 / ×0,90 (Öffnung 0,75 / 0,75 / 0,47) · Angst
(Zähne, Lippen gestreckt) ×1,36 (0,13) · Schock Öffnung 0,63.

**Zusammenfassung über drei Personen (Median der Personen):**

| Sektor | P1 | P2 | P3 | Breite | Öffnung | Vorschlag `mw` / `mo` |
|---|---|---|---|---|---|---|
| 1 Freude intensiv | ×1,45 | ×1,41 | ×1,36 | ×1,41 | 0,18 | 110 / 32 |
| 2 Zuversicht | ×1,14 | ×1,15 | — | ×1,15 | 0 | 89 / 0–3 |
| 3 Angst | ×1,10 | ×1,14 | ×1,36 | ×1,14 | 0,125 | 89 / 22 |
| 4 Überraschung | ×0,94 | ×1,08 | ×0,76 | ×0,94 | 0,127 | 73 / 23 |
| 5 Trauer moderat | ×1,04 | — | ×1,11 | ×1,08 | 0 | — |
| 5 Trauer intensiv (Weinen) | — | — | ×1,29–1,43 | ×1,36 | 0–0,23 | 106 / 0–41 |
| 6 Enttäuschung (Ekel, Missbilligung) | ×1,02 | ×0,99 | ×1,04–1,13 | ×1,03 | 0–0,08 | 80 / 0–9 |
| 7 Ärger gepresst | ×0,87 | — | — | ×0,87 | 0 | 68 / 0 |
| 7 Ärger Schrei | — | — | ×0,90–1,04 | ×0,97 | 0,47–0,75 | 76 / 83–133 |
| 8 Neugier | ×0,97 | — | — | ×0,97 | 0 | 76 / 0 |

**Befunde:**
- Freude, Zuversicht, Angst (P1/P2), Enttäuschung und die Öffnung bei Überraschung
  sind über die Personen stabil.
- Korrektur zu 13.4/13.5: Angst ist meist **geöffnet** (0,125), nicht geschlossen;
  der Avatar-Wert `mo` 18 liegt nahe an der Messung (≈ 22).
- Überraschung hat zwei Mundformen: geöffnet (×0,94–1,08) und O-Mund bzw. gespitzt
  (×0,72–0,80). Gemeinsam ist die Öffnung um 0,13.
- Trauer wird mit steigender Intensität **breiter** (Weinen: Mundwinkel seitlich
  gezogen). Das passt zur linearen Arousal-Skalierung, wenn das Ziel bei Arousal 1,0
  das Weinen ist.
- Ärger zerfällt in zwei Formen: Lippen gepresst (schmaler, geschlossen) und
  Schreien (weit offen). Welche Form `wut` bei hohem Arousal zeigt, ist eine
  Designentscheidung (O11).

**Designentscheidung O11 — entschieden (Meister, 01.10.2026): Form am Arousal festmachen, siehe 6.1.** Ursprüngliche Frage: Soll Nova bei hohem Arousal in Ärger schreien und
in Trauer sichtbar weinen (offener Mund), oder bleiben die Ausdrücke gedämpft
(gepresste Lippen, geschlossener Mund)?

**Übernommen in den Prototyp (01.10.2026):** `mw`/`mo` je Sektor laut Tabelle 13.7
(Freude 110/32, Zuversicht 89/3, Angst 89/22, Überraschung 73/23, Trauer 106/34
mit moderat 84/0, Enttäuschung 80/6, Ärger 76/70 mit moderat 68/0, Neugier 76/0),
Oberlippe Basis-Offset 17 → 22. Ärger intensiv begrenzt auf `mo` 70 statt
gemessen ≈ 83–133: Kinn und Kiefer sind Teil des statischen Grundbilds und
bewegen sich nicht mit; eine größere Öffnung würde über das Kinn hinausreichen.

### 13.15 Abgleich Text + Ton + Mundbild am Video (02.10.2026, Messung)

Material: Video 1, Mitschnitt einer Nachrichtensendung (640×360, 25 Bilder/s), 5 Abschnitte, 111 s, eine Nachrichtensprecherin + eine Interviewte.

Ablauf:
1. Text: Spracherkennung mit Whisper small. Transkript fehlerfrei bis auf Zahlen.
2. Laute: Regeln der Avatar-Seite. Zeitzuordnung per DTW an die Ton-Hüllkurve (300–3000 Hz); r 0,0 -> 0,42–0,57.
3. Mund: OpenCV FacemarkLBF (68 Punkte), Öffnung = Innenlippe, Breite = Mundwinkel, normiert auf Augenabstand.
   Die Helligkeitsmessung vom Vormittag korreliert mit nichts (r ≤ 0,14) und ist verworfen.
4. Versatz und Off-Stimmen: Ton-Hüllkurve ist als Vergleich ungeeignet (Einatmen in Pausen mit offenem Mund).
   Stattdessen erwartete Öffnung aus dem Text gegen gemessene Öffnung, Pausen ausgenommen.
   Sprecherin: Bild 0,08–0,10 s vor dem Ton, in fast allen 4-s-Fenstern r 0,2–0,5.
   Interview: nur die ersten Sekunden passen, danach Stimme aus dem Off -> verworfen. 801 von 1404 Lauten verwertbar.
5. Sprechmodell der Seite mit denselben Lautzeiten simuliert und je Laut gegen die Messung gestellt.

Befunde:
- Rangfolge der Öffnungen in der Lauttabelle stimmt (Rangkorrelation 0,76 über 30 Laute).
- **Der echte Mund läuft dem Modell 0,14 s voraus** (beide Sprecherin-Abschnitte gleich). Konsequenz für die Sprachausgabe:
  Mundanimation ca. 140 ms vor dem Ton starten. Noch nicht umgesetzt (keine Tonausgabe im Prototyp).
- Rundung (O, U) passt: Breite Modell 0,90/0,91, Messung 0,89/0,88.
- Breitziehen war zu stark (i: Modell 1,11, Messung 1,005) -> `str` bei i:/I/e:/E/E:/ç/j/s/z halbiert.
- Zu weit offen: a: 46->42, E 32->26, E: 34->28, O 36->27, `6` 28->22.
- Ergebnis: Modell<->Mund r 0,31/0,32 -> 0,34/0,34.

Grenzen (ehrlich):
- Gesicht ca. 75 px breit: geschlossene Lippen (m, b, p) messen sich nie ganz zu (0,22–0,28 statt 0). Nicht übernommen.
- a: misst sich weniger offen als a (n = 12) – widerspricht der Phonetik, vermutlich Zuordnungsfehler; nicht übernommen.
- Laute mit n < 10 (u:, Y, S) nicht ausgewertet. Vorstülpen ist frontal nicht messbar.
- Im Wesentlichen eine Sprecherin. Mehr Sprecherinnen, höhere Auflösung (Gesicht ≥ 200 px, 720p/1080p, frontal,
  Sprecherin im Bild während sie spricht) würden die Werte belastbarer machen. Ideal: eigene Aufnahmen mit 60 Bildern/s.

### 13.16 Zweite Sprecherin: Video 2 (02.10.2026, Messung)

Material: 640×360, 25 Bilder/s, 16 min; Moderatorin frontal, Gesicht ca. 140 px (doppelt so groß wie in Video 1).
39 Abschnitte, 306 s, 5675 Laute. Eingeblendete Fremdclips (Gesicht ca. 65 px, andere Personen) ausgelassen.

Befunde Methode:
- Der Gesichtsdetektor hält die Lampe links oben für ein Gesicht -> Gesichter mit Mitte x < 200 px ausgeschlossen (Sichtprüfung).
- Innere LBF-Lippenpunkte sind ungenau (Mund fast zu, Punkte auseinander). Neue Messung: Pixel innerhalb der
  äußeren Lippenkontur, die keine Lippenfarbe haben (Zähne oder Mundhöhle). Passt in beiden Videos besser zum Text
  (Video 1 r 0,25 -> 0,33, Video 2 0,19 -> 0,24).

Befunde Sprechen (beide Sprecherinnen):
- **Vorlauf bestätigt:** Mund läuft dem Sprechmodell 0,10 s (Video 2, 16 Abschnitte) bzw. 0,12–0,14 s (Video 1) voraus.
- Rundung O identisch (0,94 / 0,94), Breitziehen i/e passt nach 13.15 (Modell 1,03–1,04, Messung 1,01–1,02).
- Rundung bei u:/o:/ü im Modell zu stark (Breite 0,86–0,90 statt 0,94–0,95) -> `pk` u: 1->0,8, o: 0,55->0,4, y: 0,95->0,75, U 0,75->0,65.
- u:, ü, i: bei beiden offener als im Modell -> `mo` u: 12->17, y: 12->16, Y 16->19, i: 13->17.
- Rangübereinstimmung Modell <-> Messung (Öffnung, 31 Laute): 0,73 -> 0,76.

Nicht übernommen (Sprechstil, nicht verallgemeinerbar):
- Konsonanten-Öffnung: Sprecherin in Video 2 zeigt fast durchgehend die Zähne (Konsonanten 0,5–0,9 von a),
  Sprecherin in Video 1 kaum (meist 0). Übereinstimmung der beiden Sprecherinnen nur 0,55. Wäre ein Persönlichkeitsparameter
  („deutliche/offene Aussprache“) statt eines festen Tabellenwerts – Kandidat für Novas Charakter, offen.
