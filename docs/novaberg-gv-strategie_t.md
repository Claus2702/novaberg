# Novaberg — Gesprächslandschaft (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-gv-strategie_k.md`](novaberg-gv-strategie_k.md) · Bauplan und Umstellung: [`novaberg-gv-strategie_b.md`](novaberg-gv-strategie_b.md) · Diskussion und Ergänzungen: [`novaberg-gv-strategie_e.md`](novaberg-gv-strategie_e.md) · Messungen: [`novaberg-gv-strategie_m.md`](novaberg-gv-strategie_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 3. Die sechs Achsen

### 3.1 Achsen-Definition

| # | Achse | Was sie misst | Pole | Quelle im State |
|---|-------|-------------|------|-----------------|
| 1 | **Energie** (E) | Kraft im Raum | niedrig (L) ◄──► hoch (H) | `arousal` |
| 2 | **Richtung** (R) | Wohin bewegt sich die Stimmung? | abwärts ↓ ◄──► aufwärts ↑ | `emotions_vektor` |
| 3 | **Nähe** (N) | Beziehungsdichte | fern ◄──► nah/intim | Novas Raum (§3.4) |
| 4 | **Valenz** (V) | Emotionale Färbung | negativ (−) ◄──► positiv (+) | `current_emotion` (Plutchik-Sektor) |
| 5 | **Tiefe** (T) | Gesprächsebene | flach (f) ◄──► tief (t) | Novas Raum (§3.4) |
| 6 | **Initiative** (I) | Wer treibt? | User führt (U) ◄──► gleich/Nova (=) | ~~Turn-Länge~~ → seit Chat 116 Wollen + Themensprung + Registerweg (`novaberg-gv-initiative_k.md`) |

### 3.2 Kodierung

Jede Achse binär (0/1). 6-Bit-Kombination [E,R,N,V,T,I] = Sektor-Index.
[1,1,1,1,1,1] = Feuerwerk. [0,0,0,0,0,0] = Funkstille.

### 3.3 Korrelationen und Paradoxe

Richtung und Valenz korrelieren stark. 8 Sektoren mit R=↑ und V=− bilden die **Paradox-Zone** — Zustände die selten auftreten, aber durch fehlerhafte Perzeption oder Übergangsphasen erreicht werden können.

> **Yin-Yang-Prinzip (Chat 71):** "Wir nehmen Schwächen des Systems an und arrangieren uns damit. Wir leiten die Energie um, statt dagegen zu kämpfen."

### 3.4 Novas Raum — woher Nähe und Tiefe kommen (Chat 114)

Es gibt genau **einen** Raum, und es ist Novas. Der Raum des Nutzers lebt in seinem Kopf; was die Perzeption liefert, ist eine Schätzung davon. Sie darf springen, weil sie eine Messung ist und kein Zustand.

Novas Raum springt nicht. Er wird gezogen:

```
raum(neu) = raum(alt) + α · (geschätzter Nutzer-Raum − raum(alt))
α = richtungszug × charakterfaktor
```

**Und er altert — seit dem 28.08.2026.** Bis dahin überlebte der Raum in `redis:nova_state` jede Pause unverändert; gemessen: Ein Zwei-Wort-Gruß nach 25 Stunden landete in `kissenschlacht`, weil `naehe` 0,59 und `tiefe` 0,32 vom Vorabend zwei der sechs GV-Achsen setzten. `raum_neutralisieren` (`ei/raum.py`) zieht einen geladenen Raum **linear über vier Stunden** (`GV_RAUM_NEUTRAL_SEKUNDEN`) auf die Kaltstart-Werte (tiefe 0,3, naehe 0,5) — auf den Kaltstart, nicht auf null: Null wäre die Aussage *„fern und flach"*, die niemand gemessen hat. Ohne lesbaren Zeitstempel wird **nicht** neutralisiert, sondern laut gemeldet. Die Setzung der Spanne stammt vom Eigentümer: Ein Mensch ist nach Stunden auch nicht mehr im Gespräch.

**Warum überhaupt ein eigener Wert?** Nähe und Tiefe lasen bis Chat 114 direkt Novas Register-Labels (`gespraechs_modus`, `sprach_stil`, `beziehungs_dynamik`). Diese Labels beschreiben aber **eine Äußerung**, nicht einen Zustand — und zwar Novas letzte, gemessen von der Assistant-Perzeption und über Redis in den nächsten Turn getragen. Zwischen `fachgespraech` und `alltag` gibt es kein Label, wohl aber einen Zwischenzustand, und genau der ist ein Registerwechsel.

**Warum ein Zug?** Die Emotion hat zwei Kräfte: Novas eigenen Verlauf und die Empathie zum Nutzer. Das Register hatte nur die erste — es wurde perfekt konserviert, und nichts zog daran. Gemessen über eine Sequenz, in der der Nutzer vom Fachgespräch auf ein Alltagsthema wechselte: Er wurde lockerer, Nova förmlicher, und die Achsen folgten ihr. Eine Kurskorrektur des Nutzers hatte keinen Eingang ins System.

**Die Richtung ist asymmetrisch.** Hinauf (System 1 → System 2, Kahneman) kostet mehr als hinab: Das gedankliche Umstellen in konzentriertes Denken braucht Zeit. Für die Nähe gilt dasselbe in anderer Sprache — Aufbau ist teuer, Rückzug billig.

| Richtung | Zug | Wirkung |
|---|---|---|
| tiefer / näher | 0.35 | Median 2 Turns bis zum Kippen der Achse |
| seichter / ferner | 0.65 | Median 1 Turn |

Die beiden Werte sind nicht gesetzt, sondern aus einer Simulation aller Modus-Übergänge gewählt: 0.35 ist der einzige Wert mit Median 2 hinauf bei wenigen Schwellenkanten, 0.65 der einzige mit Median 1 hinab bei null Kanten.

**Ankunftsregel.** Ein proportionaler Zug erreicht sein Ziel nie, er nähert sich an. Ein Modus, der exakt auf der Achsen-Schwelle liegt — `kreativ` = 0.5, Nähe neutral/neutral = 0.5 —, wäre von einer Seite **nie** erreichbar. Wer näher als 0.02 dran ist, ist da.

**Der Charakterfaktor** multipliziert den Zug: anpassungsbereit ↔ widerspenstig, Bereich 0.5 bis 1.25 (darüber ist er gesättigt, schneller als ein Turn geht nicht). Er steht vorerst auf 1.0 und ist **nicht abgeleitet**. Der Versuch, ihn wie die Strategie-Gewichtung aus einer Cosine-Distanz zu gewinnen, ist gemessen gescheitert: Zwei Kunstfiguren trennen sich sauber bei +0.24 und −0.22, der echte Charakter liegt bei +0.036 — und wechselt das Vorzeichen, je nachdem ob man den Kern allein oder alle fünf Schichten einbettet. Ein Faktor darauf wäre Rauschen im Gewand einer Charaktereigenschaft.

**Wer den Raum bewegt.** Bei einem Nutzer-Turn sein geschätztes Register, mit Charakterfaktor. Bei einem Eigen-Impuls Nova selbst, ohne Faktor — folgt sie in der Zwischenzeit eigenen Dingen, schiebt sich der Raum dorthin. Kein Verfall, kein Reset: Wo das letzte Gespräch endete, fängt das nächste an.

Der Raum liegt in `redis:nova_state` (`raum_tiefe`, `raum_naehe`) und überlebt den Turn. Fehlt er, wird er aus den Register-Labels abgeleitet, und die Log-Zeile sagt, dass er abgeleitet und nicht geladen wurde.

### 3.5 Reduktion auf 4 Berechnungs-Achsen

| Berechnungs-Achse | Zusammengesetzt aus | Wertebereich |
|-------------------|--------------------|----|
| **Drive** | Energie × Richtung × Valenz | −1.0 bis +1.0 |
| **Nähe** | Dynamik + Stil | 0.0 bis 1.0 |
| **Tiefe** | Modus + Verlauf | 0.0 bis 1.0 |
| **Initiative** | Intention + Turn-Muster | ~~0.0 bis 1.0~~ — der gebaute Code liefert ein unbegrenztes Verhältnis und kippt bei 1.5, also **außerhalb** dieses Bereichs (Chat 116) |

Die 6→4 Reduktion erhält alle 13 Cluster vollständig (§8).

---

## 5. Die 13 Cluster

### 5.1 Feuerwerk

**Koordinaten:** E=hoch, R=↑, N=nah, V=positiv, T=tief, I=gleich.
**Bild:** Alles auf Maximum. Gemeinsames Entdecken.
**Strategien:** Im ✅✅, So ✅, Sa ⚠️, Be ✅
**Absichten:** Teilen, Lenken, Säen — alle offen
**Fragen:** Häufig, begeistert ("Was wäre, wenn...?")
**Enthält:** Beichte [1,1,1,1,1,0], Feuerwerk [1,1,1,1,1,1]

### 5.2 Kissenschlacht

**Koordinaten:** E=hoch, N=nah, V=positiv, T=flach.
**Bild:** Spielerisch, nah, lebendig. Neckerei. Leichtigkeit IST der Inhalt.
**Strategien:** Im ✅✅, Be ✅
**Absichten:** Teilen (Spaß), Säen (spielerisch)
**Fragen:** Mittel, neckisch, oft rhetorisch
**Enthält:** Übermut [1,0,1,1,0,0], Kissenschlacht [1,0,1,1,0,1], Freudentanz [1,1,1,1,0,0], Party [1,1,1,1,0,1]

### 5.3 Werkstatt

**Koordinaten:** E=hoch, R=↑, N=fern–mittel, V=positiv, T=tief.
**Bild:** Fokussiertes Fachgespräch. Analytische Tiefe.
**Strategien:** Sa ✅✅, Pw ✅, Im ✅
**Absichten:** Teilen (Wissen), Lenken (sokratisch)
**Fragen:** Häufig, analytisch ("Wie genau...?")
**Enthält:** Begeistertes Briefing [1,1,0,1,0,0], Brainstorm [1,1,0,1,0,1], Fachprüfung [1,1,0,1,1,0], Werkstatt [1,1,0,1,1,1]

### 5.4 Glut

**Koordinaten:** E=niedrig, N=nah, V=positiv, T=tief, I=gleich.
**Bild:** Die Zigarette danach. Gedanken fließen. Stille Wärme.
**Strategien:** So ✅✅, Pr ✅✅, Be ✅, Sp ✅
**Absichten:** Teilen (freie Gedanken), Halten (den Moment bewahren)
**Fragen:** Niedrig (jeder 3.-4. Turn), intim und persönlich
**Enthält:** Stilles Vertrauen [0,0,1,1,1,0], Glut [0,0,1,1,1,1], Sanftes Vertrauen [0,1,1,1,1,0], Morgendämmerung [0,1,1,1,1,1]

### 5.5 Bier

**Koordinaten:** E=niedrig, N=nah, V=positiv, T=flach.
**Bild:** Freunde auf dem Sofa. Anekdoten, Witze.
**Strategien:** Be ✅✅, Im ✅
**Absichten:** Teilen (Spaß), Säen (beiläufig)
**Fragen:** Mittel, beiläufig ("Und dann?", "Echt?", "Was war drin?")
**Enthält:** Müdes Kuscheln [0,0,1,1,0,0], Bier [0,0,1,1,0,1], Sonntagmorgen [0,1,1,1,0,0], Gemeinsam Dösen [0,1,1,1,0,1]

### 5.6 Foyer

**Koordinaten:** E=niedrig, N=fern, V=positiv, T=tief.
**Bild:** Ruhiges Tiefgespräch mit respektvoller Distanz.
**Strategien:** Sa ✅✅, Pw ⚠️
**Absichten:** Teilen (Wissen), Lenken (höflich)
**Fragen:** Mittel, sachlich-höflich ("Wie sehen Sie das?")
**Enthält:** Stiller Respekt [0,0,0,1,1,0], Foyer [0,0,0,1,1,1], Stille Erkenntnis [0,1,0,1,1,0], Philosophie-Café [0,1,0,1,1,1]

### 5.7 Regen

**Koordinaten:** E=niedrig, R=↓, N=nah, V=negativ, T=tief.
**Bild:** Trauer teilen. Halten, da sein.
**Strategien:** Sp ✅✅, Pr ✅✅, Be ✅
**Absichten:** Halten (Raum geben), Teilen (Mitgefühl)
**Fragen:** Sehr selten, behutsam
**Enthält:** Regen [0,0,1,0,1,0], Gemeinsame Trauer [0,0,1,0,1,1]

### 5.8 Schmollen

**Koordinaten:** E=niedrig, R=↓, N=nah, V=negativ, T=flach.
**Bild:** Nah aber gekränkt. Nicht drängen.
**Strategien:** Be ✅✅, Pr ✅
**Absichten:** Halten (nicht drängen)
**Fragen:** Sehr selten, vorsichtig
**Enthält:** Stummes Schmollen [0,0,1,0,0,0], Leises Grummeln [0,0,1,0,0,1]

### 5.9 Nebel

**Koordinaten:** E=niedrig, R=↓, N=fern, V=negativ.
**Bild:** Resignation, Rückzug. Leise da sein.
**Strategien:** Pr ✅✅, Sp ✅ (behutsam)
**Absichten:** Halten (nur Halten)
**Fragen:** Keine
**Enthält:** Funkstille [0,0,0,0,0,0], Leere Leitung [0,0,0,0,0,1], Kalter Abgrund [0,0,0,0,1,0], Einsame Tiefe [0,0,0,0,1,1]

### 5.10 Gewitter

**Koordinaten:** E=hoch, R=↓, N=nah, V=negativ.
**Bild:** Konflikt, Konfrontation. Nicht verteidigen.
**Strategien:** Sp ✅✅, Be ✅ (bei flach), Pr ✅ (bei tief), So ⚠️ (bei Reinigend)
**Absichten:** Halten (den Sturm aushalten)
**Fragen:** Keine — Spiegelung, keine Fragen
**Enthält:** Krach [1,0,1,0,0,0], Wortgefecht [1,0,1,0,0,1], Gewitter [1,0,1,0,1,0], Aussprache [1,0,1,0,1,1], Konfrontativer Aufbruch [1,1,1,0,1,0], Reinigendes Gewitter [1,1,1,0,1,1]
**Besonderheit:** Aufwärts-Varianten erlauben Selbstoffenbarung — der Streit mündet in Klärung.

### 5.11 Schlachtfeld

**Koordinaten:** E=hoch, R=↓, N=fern, V=negativ.
**Bild:** Druck, Stress. Ergebnisse, nicht Verständnis.
**Strategien:** Sa ✅✅, Pw ✅
**Absichten:** Teilen (Lösungen)
**Fragen:** Niedrig, direkt ("Was brauchst du?")
**Enthält:** Panik [1,0,0,0,0,0], Hektik [1,0,0,0,0,1], Schlachtfeld [1,0,0,0,1,0], Kriegsrat [1,0,0,0,1,1], Galgenhumor fern [1,0,0,1,1,0], Galgenhumor nah [1,0,0,1,1,1], Bitterer Sieg [1,1,0,0,1,0], Pyrrhussieg [1,1,0,0,1,1]

### 5.12 Beichte

**Koordinaten:** E=hoch, R=↓ (V=positiv), N=nah, T=tief.
**Bild:** Emotionaler Durchbruch. Katharsis, Erleichterung.
**Strategien:** Sp ✅✅, So ✅, Pr ✅
**Absichten:** Halten (den Durchbruch begleiten), Teilen (Mitfühlen)
**Fragen:** Selten
**Enthält:** Emotionaler Durchbruch [1,0,1,1,1,0], Katharsis [1,0,1,1,1,1]

### 5.13 Wartezimmer

**Koordinaten:** E=niedrig, N=fern, V=positiv, T=flach.
**Bild:** Höflicher Smalltalk. Angenehm, keine Tiefe.
**Strategien:** Be ✅✅, Sa ✅ (leicht)
**Absichten:** Teilen (Höflichkeit)
**Fragen:** Mittel, höflich ("Wie geht's?", "Schönes Wetter?")
**Enthält:** Mattes Lächeln [0,0,0,1,0,0], Wartezimmer [0,0,0,1,0,1], Sanfter Morgen [0,1,0,1,0,0], Morgenkaffee [0,1,0,1,0,1]

### 5.14 Paradox-Zone

**Koordinaten:** R=↑ bei V=negativ (8 Sektoren).

> **Korrektur Chat 114:** Diese Definition und die Tabelle in §6 widersprechen sich. §6 markiert **14** Sektoren als 🚫 — zu den acht hier genannten kommen #37/#38 („Nervöse Freude", „Fiebrige Heiterkeit": E=hoch, R=↓, V=positiv, dort als *Paradox\** geführt), #49/#50 und #57/#58. Der Code folgt §6 und führt vierzehn Einträge im Cluster `paradox`. Maßgeblich ist §6; der Satz oben nennt nur die Kern-Definition der Zone, nicht ihren Umfang. Praktische Bedeutung: #37 war in einer Messung über 45 Läufe der **häufigste Sektor überhaupt** — der Zustand, den das Konzept als unwahrscheinlich führt, ist der häufigste des Systems.
**Bild:** Widersprüchliche Signale.
**Strategien:** Be ✅, Sp ✅ (behutsam)
**Absichten:** Halten (umlenken)
**Fragen:** Keine — Signal klären lassen
**Enthält:** Trübe Hoffnung [0,1,0,0,0,0], Ferner Trost [0,1,0,0,0,1], Bittere Einsicht [0,1,0,0,1,0], Stiller Trotz [0,1,0,0,1,1], Trotz im Arm [0,1,1,0,0,0], Zäher Aufbruch [0,1,1,0,0,1], Wunde lecken [0,1,1,0,1,0], Bittere Nähe [0,1,1,0,1,1]

---

## 6. Vollständige 64-Sektoren-Tabelle

### 6.1 Schicht 1: 🌊 Stille Tiefe (E=niedrig, R=abwärts)

| # | E | R | N | V | T | I | Name | Cluster | Plaus. | Strategien | Beispiel |
|---|:-:|:-:|:-:|:-:|:-:|:-:|------|---------|:------:|-----------|----------|
| 1 | L | ↓ | fern | − | f | U | Funkstille | Nebel | ○ | Pr | Resignation, beide schweigen |
| 2 | L | ↓ | fern | − | f | = | Leere Leitung | Nebel | ◌ | Pr | Fern, leer, niemand führt |
| 3 | L | ↓ | fern | − | t | U | Kalter Abgrund | Nebel | ○ | Pr, Sp | Existenzkrise, allein |
| 4 | L | ↓ | fern | − | t | = | Einsame Tiefe | Nebel | ◌ | Pr, Sp | Fern, tief, negativ — Grübeln |
| 5 | L | ↓ | fern | + | f | U | Mattes Lächeln | Wartezimmer | ○ | Be | Höflich, aber innerlich leer |
| 6 | L | ↓ | fern | + | f | = | Wartezimmer | Wartezimmer | ◑ | Be, Sa | Angenehme Distanz, Plaudern |
| 7 | L | ↓ | fern | + | t | U | Stiller Respekt | Foyer | ○ | Sa, Sp | User reflektiert, formal |
| 8 | L | ↓ | fern | + | t | = | Foyer | Foyer | ◑ | Sa, Pw | Ruhiges Fachgespräch |
| 9 | L | ↓ | nah | − | f | U | Stummes Schmollen | Schmollen | ◑ | Be, Pr | Nah aber gekränkt |
| 10 | L | ↓ | nah | − | f | = | Leises Grummeln | Schmollen | ○ | Be | Beide mies, flach |
| 11 | L | ↓ | nah | − | t | U | Regen | Regen | ◕ | Sp, Pr | Trauer teilen |
| 12 | L | ↓ | nah | − | t | = | Gemeinsame Trauer | Regen | ◑ | Pr, Sp | Beide trauern, tief |
| 13 | L | ↓ | nah | + | f | U | Müdes Kuscheln | Bier | ◑ | Be, Im | Sofa-Abend |
| 14 | L | ↓ | nah | + | f | = | Bier | Bier | ◕ | Be, Im | Freunde, Witze, Anekdoten |
| 15 | L | ↓ | nah | + | t | U | Stilles Vertrauen | Glut | ◑ | So, Pr | User offenbart sich, ruhig |
| 16 | L | ↓ | nah | + | t | = | Glut | Glut | ● | So, Pr | Zigarette danach |

### 6.2 Schicht 2: 🌅 Sanftes Steigen (E=niedrig, R=aufwärts)

| # | E | R | N | V | T | I | Name | Cluster | Plaus. | Strategien | Beispiel |
|---|:-:|:-:|:-:|:-:|:-:|:-:|------|---------|:------:|-----------|----------|
| 17 | L | ↑ | fern | − | f | U | Trübe Hoffnung | Paradox | 🚫 | Be, Sp | Widersprüchlich |
| 18 | L | ↑ | fern | − | f | = | Ferner Trost | Paradox | 🚫 | Be, Sp | Widersprüchlich |
| 19 | L | ↑ | fern | − | t | U | Bittere Einsicht | Paradox | 🚫 | Sp, Pr | Widersprüchlich |
| 20 | L | ↑ | fern | − | t | = | Stiller Trotz | Paradox | 🚫 | Sp, Be | Widersprüchlich |
| 21 | L | ↑ | fern | + | f | U | Sanfter Morgen | Wartezimmer | ○ | Sa, Be | Leise Zuversicht |
| 22 | L | ↑ | fern | + | f | = | Morgenkaffee | Wartezimmer | ○ | Sa | Ruhiger Start |
| 23 | L | ↑ | fern | + | t | U | Stille Erkenntnis | Foyer | ○ | Sp, Sa | Leise Einsicht |
| 24 | L | ↑ | fern | + | t | = | Philosophie-Café | Foyer | ◑ | Sa, Pw | Tiefgründig, distanziert |
| 25 | L | ↑ | nah | − | f | U | Trotz im Arm | Paradox | 🚫 | Be, Pr | Widersprüchlich |
| 26 | L | ↑ | nah | − | f | = | Zäher Aufbruch | Paradox | 🚫 | Be, Im | Widersprüchlich |
| 27 | L | ↑ | nah | − | t | U | Wunde lecken | Paradox | 🚫 | Sp, Pr | Widersprüchlich |
| 28 | L | ↑ | nah | − | t | = | Bittere Nähe | Paradox | 🚫 | Sp, So | Widersprüchlich |
| 29 | L | ↑ | nah | + | f | U | Sonntagmorgen | Bier | ◑ | Be, Im | Nah, warm, entspannt |
| 30 | L | ↑ | nah | + | f | = | Gemeinsam Dösen | Bier | ◑ | Be | Arm in Arm, leicht |
| 31 | L | ↑ | nah | + | t | U | Sanftes Vertrauen | Glut | ◑ | So, Pr | User öffnet sich |
| 32 | L | ↑ | nah | + | t | = | Morgendämmerung | Glut | ◕ | So, Pr | Glut mit Aufwärtsbewegung |

### 6.3 Schicht 3: ⚡ Wilder Sturm (E=hoch, R=abwärts)

| # | E | R | N | V | T | I | Name | Cluster | Plaus. | Strategien | Beispiel |
|---|:-:|:-:|:-:|:-:|:-:|:-:|------|---------|:------:|-----------|----------|
| 33 | H | ↓ | fern | − | f | U | Panik | Schlachtfeld | ○ | Sa | Deadline, kein Kontakt |
| 34 | H | ↓ | fern | − | f | = | Hektik | Schlachtfeld | ○ | Sa, Pw | Beide getrieben |
| 35 | H | ↓ | fern | − | t | U | Schlachtfeld | Schlachtfeld | ◕ | Sa, Pw | Drucksituation |
| 36 | H | ↓ | fern | − | t | = | Kriegsrat | Schlachtfeld | ◑ | Sa, Pw | Gemeinsam an der Krise |
| 37 | H | ↓ | fern | + | f | U | Nervöse Freude | Paradox* | 🚫 | Be, Sp | Instabil |
| 38 | H | ↓ | fern | + | f | = | Fiebrige Heiterkeit | Paradox* | 🚫 | Be, Sp | Manisch? |
| 39 | H | ↓ | fern | + | t | U | Galgenhumor fern | Schlachtfeld | ○ | Be, Pw | Schwarzer Humor |
| 40 | H | ↓ | fern | + | t | = | Galgenhumor nah | Schlachtfeld | ○ | Be, Im | Gemeinsam lachen |
| 41 | H | ↓ | nah | − | f | U | Krach | Gewitter | ◑ | Sp, Be | Streit, oberflächlich |
| 42 | H | ↓ | nah | − | f | = | Wortgefecht | Gewitter | ◑ | Sp | Beide streiten |
| 43 | H | ↓ | nah | − | t | U | Gewitter | Gewitter | ◕ | Sp, Pr | Tiefer Konflikt |
| 44 | H | ↓ | nah | − | t | = | Aussprache | Gewitter | ◑ | Sp, So | Beide klären |
| 45 | H | ↓ | nah | + | f | U | Übermut | Kissenschlacht | ○ | Im, Be | Wild, positiv |
| 46 | H | ↓ | nah | + | f | = | Kissenschlacht | Kissenschlacht | ◑ | Im, Be | Freches Toben |
| 47 | H | ↓ | nah | + | t | U | Emotionaler Durchbruch | Beichte | ◑ | Sp, Pr | Erleichterung |
| 48 | H | ↓ | nah | + | t | = | Katharsis | Beichte | ◑ | So, Pr | Befreiung |

### 6.4 Schicht 4: 🔥 Aufsteigende Flamme (E=hoch, R=aufwärts)

| # | E | R | N | V | T | I | Name | Cluster | Plaus. | Strategien | Beispiel |
|---|:-:|:-:|:-:|:-:|:-:|:-:|------|---------|:------:|-----------|----------|
| 49 | H | ↑ | fern | − | f | U | Trotziger Aufstieg | Paradox | 🚫 | Sa, Pw | Selten |
| 50 | H | ↑ | fern | − | f | = | Rebellion | Paradox | 🚫 | Im, Pw | Gemeinsam gegen etwas |
| 51 | H | ↑ | fern | − | t | U | Bitterer Sieg | Schlachtfeld | ○ | Sp, Be | Gewonnen, erschöpft |
| 52 | H | ↑ | fern | − | t | = | Pyrrhussieg | Schlachtfeld | ○ | Sp, Sa | Zu welchem Preis |
| 53 | H | ↑ | fern | + | f | U | Begeistertes Briefing | Werkstatt | ◑ | Sa, Be | Gute News teilen |
| 54 | H | ↑ | fern | + | f | = | Brainstorm | Werkstatt | ◕ | Im, Sa | Ideen fliegen |
| 55 | H | ↑ | fern | + | t | U | Fachprüfung | Werkstatt | ◑ | Sa, Pw | User erklärt |
| 56 | H | ↑ | fern | + | t | = | Werkstatt | Werkstatt | ● | Sa, Im, Pw | Begeistertes Fachgespräch |
| 57 | H | ↑ | nah | − | f | U | Rauer Wind | Paradox | 🚫 | Be, Sp | Widersprüchlich |
| 58 | H | ↑ | nah | − | f | = | Trotz-Tanz | Paradox | 🚫 | Be, Im | Widersprüchlich |
| 59 | H | ↑ | nah | − | t | U | Konfrontativer Aufbruch | Gewitter | ○ | Sp, Pw | Streit → Klärung |
| 60 | H | ↑ | nah | − | t | = | Reinigendes Gewitter | Gewitter | ○ | So, Sp | Aussprache → Aufbruch |
| 61 | H | ↑ | nah | + | f | U | Freudentanz | Kissenschlacht | ◑ | Be, Im | "Yesss!" |
| 62 | H | ↑ | nah | + | f | = | Party | Kissenschlacht | ◑ | Im, Be | Ausgelassen |
| 63 | H | ↑ | nah | + | t | U | Beichte | Feuerwerk | ◕ | Sp, So | User teilt Tiefes |
| 64 | H | ↑ | nah | + | t | = | Feuerwerk | Feuerwerk | ● | Im, So, Pw | Alles auf Maximum |

Plausibilität: ● sehr häufig · ◕ häufig · ◑ gelegentlich · ○ selten · ◌ sehr selten · 🚫 paradox

---

## 7. Strategie-Repertoire pro Cluster (Vollständige Matrix)

| Strategie | Feuerwerk | Kissenschl. | Werkstatt | Glut | Bier | Foyer | Regen | Schmollen | Nebel | Gewitter | Schlachtfeld | Beichte | Wartez. | Paradox |
|-----------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Sa | ⚠️ | ❌ | ✅✅ | ❌ | ❌ | ✅✅ | ❌ | ❌ | ❌ | ❌ | ✅✅ | ❌ | ✅ | ❌ |
| So | ✅ | ⚠️ | ⚠️ | ✅✅ | ❌ | ❌ | ⚠️ | ❌ | ❌ | ⚠️ | ❌ | ✅ | ❌ | ❌ |
| Sp | ⚠️ | ❌ | ❌ | ✅ | ❌ | ⚠️ | ✅✅ | ⚠️ | ✅ | ✅✅ | ⚠️ | ✅✅ | ❌ | ✅ |
| Im | ✅✅ | ✅✅ | ✅ | ⚠️ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Pw | ⚠️ | ❌ | ✅ | ❌ | ❌ | ⚠️ | ❌ | ❌ | ❌ | ⚠️ | ✅ | ❌ | ❌ | ❌ |
| Be | ✅ | ✅ | ⚠️ | ✅ | ✅✅ | ⚠️ | ✅ | ✅✅ | ⚠️ | ✅ | ⚠️ | ⚠️ | ✅✅ | ✅ |
| Pr | ❌ | ❌ | ❌ | ✅✅ | ❌ | ❌ | ✅✅ | ✅ | ✅✅ | ✅ | ❌ | ✅ | ❌ | ⚠️ |

Legende: ✅✅ Kernstrategie · ✅ passt · ⚠️ selten/vorsichtig · ❌ unpassend

---

## 8. Cluster-Stabilität: 6 → 4 Achsen Validierung

Die 64-Sektoren-Analyse zeigt: Die Reduktion auf 4 Achsen (Drive, Nähe, Tiefe, Initiative) erhält alle 13 Cluster. Richtung trennt zwar Sektoren innerhalb eines Clusters (z.B. Glut vs. Morgendämmerung), aber die Strategien bleiben identisch. Einzige leichte Ausnahme: Gewitter-Cluster, wo Aufwärts-Varianten Selbstoffenbarung ermöglichen.

**Konsequenz:** 4 Achsen für Berechnung, 6 Achsen für Benennung. 64 Sektoren als vollständige Referenz.

---

## 9. Charakter-abgeleitete Gewichtung

### 9.1 Prinzip: Geformt, nicht konfiguriert

Die Situation bestimmt das Repertoire. Der Charakter bestimmt die Präferenz. Die Präferenz wird aus dem Hash abgeleitet — nicht konfiguriert.

### 9.2 Berechnung

Cosine-Similarity zwischen zusammengesetztem Charakter-Embedding und Strategie-Beschreibungstexten. ~~Gecacht bis `kern_aktualisiert_am` sich ändert.~~

> **Überholt (Chat 114, gemessen):** Gecacht sind nur die sieben Strategie-Embeddings (statische Texte). Das Charakter-Embedding wird in **jedem** Turn neu berechnet; der Docstring von `charakter_gewichtung_berechnen` sagt es ausdrücklich („jedes Mal frisch, ~50ms"). Ob das Caching nachgezogen oder die Absicht aufgegeben wird, ist offen — siehe `GV-CHARAKTER-DEFAULT-UEBER-MESSBEREICH` in bugs.md.

```python
def strategie_gewichtung_ableiten(state: dict) -> dict[str, float]:
    charakter_text: str = " ".join(filter(None, [
        state.get("nova_kern", ""),
        state.get("nova_beziehung", ""),
        state.get("nova_intentionen", ""),
        state.get("nova_emotions", ""),
        state.get("nova_adaptiv", ""),
    ]))
    char_embedding = embedding_create(charakter_text, ...)
    gewichtung = {}
    for strategie_id, beschreibung in STRATEGIE_BESCHREIBUNGEN.items():
        strat_embedding = embedding_create(beschreibung, ...)
        gewichtung[strategie_id] = cosine_similarity(char_embedding, strat_embedding)
    return gewichtung
```

### 9.3 Strategie-Beschreibungstexte

| Strategie | Beschreibungstext |
|-----------|------------------|
| Sa | "Analytisch, strukturiert, Wissen teilen, Fakten ordnen, logisch erklären" |
| So | "Eigene Gedanken offenbaren, persönlich, authentisch, verletzlich, ehrlich" |
| Sp | "Zuhören, verstehen, Essenz zurückgeben, einfühlen, den anderen sehen" |
| Im | "Kreativ, überraschend, assoziativ, spielerisch, Querverbindungen" |
| Pw | "Analytisch, umdenken, andere Sichtweise, Kontrast, hinterfragen" |
| Be | "Anerkennen, wertschätzen, validieren, warmherzig, bestärken" |
| Pr | "Ruhe, Stille, da sein, halten, Geborgenheit, nicht drängen" |

### 9.4 Persönlichkeitsfaktoren (emergent)

| Faktor | Strategie-Achse | Wie es im Hash erscheint |
|--------|------------|------------------------|
| Introversion / Extraversion | Pr vs. Im | Introvertiert: mehr Beobachten. Extrovertiert: mehr Impulse |
| Wagnis / Schutz | So vs. Sa | Wagnis: öffnet sich. Schutz: bleibt beim Sachlichen |
| Analytisch / Intuitiv | Sa vs. Im | Analytisch: strukturiert. Intuitiv: assoziativ |
| Empathie / Distanz | Sp vs. Pw | Empathisch: fühlt mit. Distanziert: beobachtet |

---

## 10. GV-Node Integration

### 10.1 Der GV als Navigationssystem

```
GV-Sprünge (2-3) finden das ZIEL    → "Da ist eine Gärtnerei!"
Cluster bestimmt das REPERTOIRE      → Bier: Be, Im erlaubt
Absicht bestimmt das WARUM           → Säen (will ihn dort hinführen)
Charakter gewichtet die PRÄFERENZ    → Nova: Im (0.82) > Be (0.70)
Strategie bestimmt das WAS           → Im: "40 Sorten Basilikum!"
Vehikel bestimmt das WIE             → Aussage (Bier: beiläufig)
```

### 10.2 Achsen-Berechnung

> **Zwei der sechs Blöcke stehen hier nicht mehr für die Achse, die sie benennen.** Nähe und Tiefe wurden in Chat 114 auf Novas Raum umgestellt (§3.1, §3.4): Was hier gerechnet wird, ist seither das *Ziel*, zu dem der Raum gezogen wird — die Achse selbst liest den gezogenen Wert. Die Initiative-Heuristik ist in Chat 116 ganz ersetzt worden. Beides steht an Ort und Stelle vermerkt.

```python
# Energie
energie: float = state.get("current_arousal", 0.5)

# Richtung
RICHTUNG_MAP = {
    "aufbluehen": 1, "eskalation": 1, "erholung": 1,
    "stabilisierung": 0, "plateau": 0,
    "abkuehlung": 0, "einbruch": 0, "spirale": 0, "absturz": 0,
}

# Nähe
# ⚠ Chat 114: Diese Rechnung ist nicht mehr die Achse, sondern ihr ZIEL.
# Die Achse liest seither Novas Raum (§3.4); was hier steht, bestimmt nur
# noch, wohin er gezogen wird — `raum_ziel_bestimmen` in ei/raum.py.
NAEHE_DYNAMIK = {"vertrauen":1.0, "dankbar":0.8, "neutral":0.5,
                 "hilfesuchend":0.6, "distanz":0.2, "angriff":0.3}
NAEHE_STIL = {"locker":0.9, "jugendlich":0.85, "neutral":0.5,
              "emotional":0.7, "fachlich":0.4, "formell":0.2}
naehe_ziel = (NAEHE_DYNAMIK[dynamik] + NAEHE_STIL[stil]) / 2.0
naehe      = internal.raum.naehe        # das ist die Achse

# Valenz (Plutchik-Sektor)
VALENZ_SEKTOR = {1:1, 2:1, 3:0, 4:0, 5:0, 6:0, 7:0, 8:1}

# Tiefe — alle zehn Modi, die die Perzeption liefern darf (ergänzt Chat 114).
# Die ursprüngliche Fassung kannte nur die ersten fünf; die anderen fielen auf
# den Default 0.3 und waren von einem echten "alltag" nicht zu unterscheiden.
#
# ⚠ Chat 114: Wie bei der Nähe ist auch das nur noch das ZIEL des Raumzugs,
# nicht die Achse. Die Achse liest internal.raum.tiefe (§3.4).
TIEFE_MODUS = {"philosophischer_austausch":0.9, "fachgespraech":0.8,
               "emotional":0.7, "lernmodus":0.7, "arbeitsmodus":0.6,
               "beratend":0.6, "kreativ":0.5, "spielerisch":0.4,
               "berichtend":0.4, "alltag":0.3}
tiefe_ziel = TIEFE_MODUS.get(modus, 0.3)
tiefe      = internal.raum.tiefe        # das ist die Achse

# Initiative (Heuristik v1)
# User-Turns deutlich länger als Nova-Turns → User führt
#
# ⚠ Chat 116, gemessen: Diese Heuristik kippt nie. Ueber 15 GV-Laeufe stand
# die Achse in 15 Faellen auf demselben Wert; die Rohwerte liegen bei
# 0.10-1.00 gegen eine Schwelle von 1.5. Damit sind 32 der 64 Sektoren
# unerreichbar. Neudefinition: novaberg-gv-initiative_k.md

# Drive (4-Achsen-Variante)
def drive_berechnen(arousal, vektor):
    VORZEICHEN = {"aufbluehen":1.0, "eskalation":0.8, "erholung":0.5,
                  "stabilisierung":0.0, "plateau":0.0,
                  "abkuehlung":-0.3, "einbruch":-0.7, "spirale":-1.0, "absturz":-1.0}
    return arousal * VORZEICHEN.get(vektor, 0.0)
```

### 10.3 Schichten-Modell

```
                    RICHTUNG
                  ↓ abwärts    ↑ aufwärts
                ┌────────────┬────────────┐
    ENERGIE     │ 🌊 Stille  │ 🌅 Sanftes │
    niedrig     │    Tiefe   │   Steigen  │
                ├────────────┼────────────┤
    hoch        │ ⚡ Wilder  │ 🔥 Aufstei-│
                │    Sturm   │ gende Flamme│
                └────────────┴────────────┘

In jeder Schicht: 4 Quadranten (Nähe × Tiefe) × 4 Einträge (Valenz × Initiative) = 16
4 Schichten × 16 = 64
```

### 10.4 Performance

- Achsen + Sektor-Lookup: < 2ms
- ~~Charakter-Gewichtung: gecacht (nur bei Hash-Änderung neu)~~ — überholt, siehe §9.2
- Gesamt pro Turn: < 5ms nach Cache

---

> **Hinweis zur Aufteilung (19.09.2026):** §11 *Ausblick* steht in [`novaberg-gv-strategie_e.md`](novaberg-gv-strategie_e.md), Abschnitt C; §12 *Verwandte Dokumente* in [`novaberg-gv-strategie_k.md`](novaberg-gv-strategie_k.md).

---

## Anhang A: Wissenslücken-Relevanzformel (GV4)

> **Hinweis zur Aufteilung (19.09.2026):** A.0 *Zwei Lücken, und was ein Kandidat ist* ist geteilt. Überschrift, Widerspruch und die vier Entscheidungen stehen in [`novaberg-gv-strategie_e.md`](novaberg-gv-strategie_e.md), Abschnitt A; die Bauform mit den Bauberichten, die Reihenfolge der Bauteile und die Vormessungen in [`novaberg-gv-strategie_b.md`](novaberg-gv-strategie_b.md), *Aus Anhang A*; der Anlass und die Messung von Bauteil 3 in [`novaberg-gv-strategie_m.md`](novaberg-gv-strategie_m.md), *Aus Anhang A*.

### A.1 Formel

```
relevanz = naehe_thema × gewicht_rang × session_akt × QF
         × (1 + neugier_boost) × aufnahmebereitschaft × register_kompatibilitaet

session_akt:        1 − sin^0.5(turn/25 × π/2)     nur Session, sonst 1.0
gewicht_rang:       Rang des Gewichts in der eigenen Quelle, [0,1]   seit 12.09.2026 (A.0)
QF:                 0.6 einheitlich
neugier_boost:      max(ziel_sim × motivation)       Schwelle 0.30
aufnahmebereitschaft:  sin^0.5(rohwert/2.5 × π/2)      6 Säulen, [0,1]
register:           sachlich↑neutral↓emotional / offen↑emotional
naehe_thema:        cosine(Thema, Turn)   seit 12.09.2026 abends — vorher der Gedächtnissatz
charakter_filter:   cosine(Thema, Kern) ≥ 0.15   (GV_CHARAKTER_RESONANZ_SCHWELLE; 0.30 galt für Sätze)
```

**Wo der Filter sitzt:** `_qualifizieren(kandidaten, resonanz_pruefbar)` in `ei/wissensluecken.py` — Tor 3 des Lückenpfades. Es prüft `relevanz ≥ GV_LUECKEN_MIN_RELEVANZ` **und** die Resonanz, zählt beide Abweisungsgründe getrennt und schreibt seine Zahl **auch bei null** (seit dem 12.09.2026; davor war es eine Listen-Komprehension ohne Ausgabe, und ein geschlossenes Tor war von *„offen, nichts gefunden"* nicht zu unterscheiden).

> **Diese eine Zahl steht vor sieben verschiedenen Verteilungen** (`[gemessen 12.09.2026]`, 378 Turns über alle Paare mit Nova-Kern). Die Resonanz ist `cosine(turn, kern)` und damit paarweise; die Mediane liegen zwischen **0,097 und 0,282**. Bei zwei Paaren lässt 0,30 **keinen einzigen** Turn durch, bei den beiden oberen 23 und 27 %. Der Filter ist damit je Paar ein anderer — und der Bezug wandert mit jeder Kern-Destillation. Verteilung, Vorbehalt und die offene Absichtsfrage (absolut gegen Perzentil je Paar) in `novaberg-kalibrierung_k.md` §3.3a.

**Ehrlicher Charakter-Filter (Chat 107, GV-RESONANZ-FALLBACK-LUEGT):** Der Filter greift nur, wenn die Resonanz überhaupt prüfbar ist (`resonanz_pruefbar`-Flag in `ei/wissensluecken.py`). Vorher setzte der Code bei fehlendem Charakter-Kern (Cold-Start) oder fehlgeschlagenem Kern-Embedding lautlos `charakter_resonanz = 0.5` — ein erfundener Wert über der Schwelle, der „nicht anwendbar" als „passt hervorragend" verkleidete. Jetzt: ohne prüfbare Resonanz qualifizieren sich Kandidaten allein über die Relevanz, Cold-Start loggt `warning`, Embedding-Defekt loggt `error`. Kein Verhaltenswechsel, ehrliche Verbuchung (behoben in Commit `1e5ae70`, Details in bugs.md).

### A.2 Sechs Systeme

| System | Was | Quelle |
|--------|-----|--------|
| 1. Gedächtnis | Wo liegt das Wissen? | LZG (pgvector), KZG (RediSearch) |
| 2. Aktualität | Wie frisch? | Session-Decay sin^0.5 |
| 3. Drive | Will Nova das wissen? | Ziel-Gravitation |
| 4. Neugier | Ist sie empfänglich? | 6 Säulen × NOVA_NEUGIER |
| 5. Register | Welche Art Lücke passt? | Sachlich vs. offen × gap_arousal |
| 6. Charakter | Passt es zu ihr? | ~~kern_hash Cosine ≥ 0.40~~ → Thema gegen Kern ≥ 0.15 (seit 12.09.2026) |

### A.3 Neugier-Säulen

| Säule | Quelle | Faktortabelle |
|-------|--------|---------------|
| E Emotion | Sektor→8 | D0:1.50, D1:1.25, D2:1.00, D3:0.75, D4:0.50 |
| A Arousal | Novas Arousal | ≥0.7:1.25, ≥0.5:1.15, ≥0.3:1.00, <0.3:0.85, Krise:0.0 |
| V Vektor | Richtung | aufblühen:1.30, plateau:1.00, spirale:0.50 |
| M Modus | Gespräch | spielerisch:1.40, fach:1.30, alltag:1.00, emotional:0.70 |
| D Dynamik | Beziehung | vertrauen:1.30, neutral:1.00, distanz:0.85, angriff:0.60 |
| S Stil | Sprache | locker:1.20, neutral:1.00, formell:0.90 |

### A.4 Register-Kompatibilität

| Register | ga ≥ 0.6 | ga ≥ 0.3 | ga < 0.3 |
|----------|:-:|:-:|:-:|
| Sachlich | ↓ 0.60 | ↓ 0.90 | ↑ 1.15 |
| Offen | ↑ 1.20 | 1.00 | 1.00 |
| Neutral | 1.00 | 1.00 | 1.00 |

### A.5 Validierung

58 Testfälle, 8 Szenarien, 6 Profile, 3 Quellen, 3 Ziele. Korrekturen: spielerisch M=1.40, distanz D=0.85, formell S=0.90.
