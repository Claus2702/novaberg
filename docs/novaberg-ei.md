# Novaberg — Emotionale Intelligenz

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Emotionale Intelligenz (Übersicht)
**Stand:** 20. April 2026, Chat 59 (EI-Calc als eigener Node, Nova-Empathie, rolle-Parameter)
**Pfad:** novaberg/docs/novaberg-ei.md
**Quellen:** nova-04-k.md (EI-Konzept)

---

## 1. Konzept

Nova fuehlt nicht. Aber Nova nimmt wahr, berechnet und reagiert auf Emotionen — als mathematisches Signal, nicht als theatralische Geste. Emotionale Intelligenz bedeutet: den emotionalen Zustand des Gespraechspartners erkennen, den Verlauf ueber mehrere Turns nachverfolgen, den Kommunikationsstil anpassen und die Antwort in Ton, Laenge und Empathie darauf abstimmen.

Jede Interaktion wird auf sechs Saeulen analysiert, inspiriert von Schulz von Thun, Watzlawick und Berne:

| Saeule | Quelle | Was sie erfasst | Speicher |
|--------|--------|----------------|----------|
| **Inhalt** | Schulz von Thun (Sachebene) | Themen, Fakten, Zusammenfassung | Session, KZG |
| **Intention** | Schulz von Thun (Appell) | Warum sagt der Nutzer das? | KZG, Charakter-Hash |
| **Emotion** | Watzlawick (Beziehungsebene) | Emotionale Faerbung pro Turn | Session, KZG |
| **Modus** | Schulz von Thun (Selbstoffenbarung) | Gespraechsregister (alltag, fachlich, emotional) | Session, Charakter-Hash |
| **Beziehung** | Watzlawick + Berne | Dynamik zwischen Nutzer und Nova | Charakter-Hash (langfristig) |
| **Salienz** | Eigene Entwicklung | Wichtigkeit, steuert Gedaechtnisbildung | KZG → LZG |

> **Kognitionswissenschaftlicher Hintergrund:** Friedemann Schulz von Thun beschrieb 1981 das Vier-Seiten-Modell: Jede Nachricht hat eine Sachseite, eine Selbstoffenbarung, einen Beziehungshinweis und einen Appell. Paul Watzlawick postulierte 1967: "Man kann nicht nicht kommunizieren" — jede Interaktion hat eine Inhalts- und eine Beziehungsebene. Eric Bernes Transaktionsanalyse (1964) unterscheidet Eltern-Ich, Erwachsenen-Ich und Kind-Ich als Kommunikationspositionen. Nova nutzt alle drei Modelle, um das "Was wird gesagt" vom "Was wird gemeint" und "Was wird gebraucht" zu trennen.

### Drei Zeitskalen

Jede Saeule hat Daten auf drei Ebenen:

| Zeitskala | Quelle | Beispiel |
|-----------|--------|---------|
| **Aktuell** (dieser Turn) | Session / Perzeption | "Gerade jetzt ist der Nutzer frustriert" |
| **Kurzfristig** (Tage/Wochen) | KZG | "In letzter Zeit oft gestresst" |
| **Langfristig** (Monate) | Charakter-Hash | "Grundsaetzlich neugierig und analytisch" |

> **Bordcomputer-Analogie (Chat 8):** "Wenn ich generell ein ruhiger Fahrer bin, errechnet er einen Durchschnittsverbrauch der letzten Stunden und sagt: Jo, Brudi, kannst noch 550 km fahren. Aber gerade jetzt habe ich es eilig. Der Verbrauch steigt." — Langzeitwerte fuer Vorhersage, Session-Turn bestimmt die Gegenwart.

---

## 2. Plutchik-Emotionsmodell

Novas Emotionserkennung basiert auf Robert Plutchiks Emotionsrad (1980): 8 Grundemotionen in einem Oktagon, daraus abgeleitet 16+1 kanonische Emotionen mit sektorabhaengiger Normalisierung. Jede Emotion traegt einen kontinuierlichen Arousal-Wert (0.0-1.0) nach Russells Circumplex Model. Sektorspezifische Decay-Raten (Dopamin- vs. Cortisol-basiert) steuern, wie schnell Emotionen abklingen. Interleaved Sektorreihenfolge folgt dem Plutchik-Original.

> Detail: novaberg-ei-plutchik.md

---

## 3. Charakter-Profile

Fünf automatisch destillierte Profile, alle im Prompt genutzt: Kern-Hash (Grundpersoenlichkeit, stabil), Adaptiv-Hash (aktuelle Themen, dynamisch), Emotions-Profil (emotionale Grundstimmung), Intentions-Profil (Kommunikationsstil) und Beziehungs-Profil. Das Emotions-Profil liefert die gewachsene Stimmung, EI-MIKRO ergaenzt pro Turn die taktische Reaktion. Die Destillation uebernimmt Pixie (CharakterAgent), getriggert durch das `hash_dirty`-Flag — nur bei tatsaechlichen Aenderungen im LZG. Die Profile sind emergent: Sie werden nicht programmiert, sondern folgen aus den Daten.

> Detail: novaberg-ei-character-profiles.md

---

## 4. Sprachadaption

Basierend auf Communication Accommodation Theory (Giles 1973): Menschen passen ihren Stil an ihr Gegenueber an. Feature-Scoring (`_turn_features_bewerten()`) berechnet pro Turn Scores ueber 13 Merkmale mit positiven und negativen Beitraegen, akkumuliert ueber ein konfigurierbares Analyse-Fenster. Fuenf Stile: locker, formell, fachlich, emotional, jugendlich. Kreuz-Inhibition verhindert widerspruechliche Klassifikationen (Slang senkt Formell-Score, Konjunktiv senkt Jugendlich-Score).

> Detail: novaberg-ei-language-adaptation.md

---

## 5. Gespraechsvektor

Neun Vektoren beschreiben die emotionale Dynamik eines Gespraechs. Jeder Vektor hat eine eigene Nova-Strategie:

| Vektor | Uebergang | Nova-Strategie |
|--------|----------|----------------|
| `absturz` | positiv → negativ | Auffangen, nicht relativieren. "Was ist passiert?" |
| `spirale` | negativ → noch negativer | Alarm. Kurz, sanft, praesent. Keine Loesungen draengen. |
| `stabilisierung` | negativ → neutral | Ruhe geben. Nicht pushen. |
| `erholung` | negativ → positiv | Warmes Kissen. Besserung anerkennen, nicht feiern. |
| `aufbluehen` | neutral → positiv | Mitfreuen, bestaerken. |
| `eskalation` | positiv → noch positiver | Mitgehen, Begeisterung teilen. |
| `abkuehlung` | positiv → neutral | Sanfter Uebergang. |
| `einbruch` | neutral → negativ | Frueh erkennen, nachfragen. |
| `plateau` | stabil | Ton halten, keine Wechsel. |

**Spirale vs. Plateau:** Beide haben die gleiche Emotions-Gruppe (negativ → negativ). Der Unterschied: Spirale zeigt *neue* negative Emotionen (Intensitaetsanstieg), Plateau zeigt dieselben (keine Veraenderung). Gleiches gilt fuer Eskalation vs. Plateau bei positiv → positiv.

Der GV-Node berechnet den Vektor als eigener Node im HumanGraph (13 Nodes seit Chat 59 — 11 sync + 2 async). Farbmisch-System, Entity-Hop und Charakter-Linse steuern die Nuancen.

> Detail: novaberg-node-gv_k.md

---

## 6. Vier Dimensionen der Reaktion

Aus den sechs Wahrnehmungs-Saeulen leitet Nova vier Steuerungssignale ab:

**Emotions-Verlauf:** Gewichteter Verlauf ueber alle User-Turns mit logarithmischem Decay. Neuere Emotionen wiegen staerker. Formel: `gewicht = 1.0 / (1.0 + DECAY_FACTOR * log_base(1 + position))`. Arousal-basierter Decay moduliert: hoher Arousal (Kuendigung, Todesfall) verlangsamt den Verfall.

**Emotions-Vektor:** Die Richtung der emotionalen Bewegung (9 Vektoren, siehe Abschnitt 5).

**Arousal (Float 0.0-1.0):** Steuert Tempo und Laenge der Antwort:

| Arousal | Bedeutung | Antwort-Strategie |
|---------|-----------|-------------------|
| > 0.7 | Stark aufgewuehlt | 2-3 Saetze, praesent, direkt |
| 0.4-0.7 | Moderate Energie | 2-4 Saetze, normales Tempo |
| < 0.4 | Erschoepft, resigniert | Max. 1-2 Saetze. Kein "Moechtest du darueber reden?" Einfach da sein. |

> **Warum Float statt String (Chat 8)?** Urspruenglich war Arousal `high/mid/low`. Das war zu ungenau — "aergerlich (high)" konnte leicht genervt oder Raserei sein. Der Float ermoeglicht feinere Steuerung. Abwaertskompatibilitaet ueber `_arousal_to_float()`.

**Sprachstil (5 Kategorien):** Feature-Scoring (`_turn_features_bewerten()`) berechnet pro Turn Scores ueber 13 Merkmale mit positiven und negativen Beitraegen. `_sprach_stil_erkennen()` akkumuliert ueber das Analyse-Fenster (`STIL_ANALYSE_TURNS`):

| Stil | Wichtigste Merkmale | Nova passt an |
|------|-------------------|--------------|
| `locker` | Kurze Saetze (< 8 Woerter), keine Zeichensetzung | Kuerzere Saetze, direkt, informell |
| `formell` | Lange Saetze (> 15 Woerter), Komma-Dichte, Konjunktiv, Abwesenheit Slang | Vollstaendige Saetze, respektvoll (aber Du) |
| `fachlich` | Lange Woerter (> 10 Zeichen), korrekte Zeichensetzung | Fachbegriffe, praezise, keine Grundlagen |
| `emotional` | Ausrufezeichen (> 1), Interjektionen, Grossbuchstaben-Woerter | Warmherzige Formulierungen |
| `jugendlich` | Slang-Woerter ("digga", "krass", "ey"), Emojis, Abkuerzungen | Locker, auf Augenhoehe — eigene Stimme behalten |

**Kreuz-Inhibition:** Slang senkt den Formell-Score, Konjunktiv senkt den Jugendlich-Score. Ein Turn wird nie gleichzeitig formell und jugendlich. **Hash als Tiebreaker:** Bei Ambiguitaet (Abstand Top-1 zu Top-2 < 2.0) wird das Kommunikations-Profil aus dem Hash herangezogen.

**Natuerliche Variation:** Ein formeller Sprecher wechselt natuerlich zwischen formell, fachlich und sachlich-neutral — genau wie ein Mensch. Im Smoking Test: 3/15 → 15/15 im formell/fachlichen Spektrum (Chat 20).

> **Erkenntnis (Chat 20):** Die Stil-*Erkennung* funktioniert zuverlaessig. Die Stil-*Adaption* in den Antworten haengt vom Modell ab. Ein 24B-Modell folgt dem Stil-Label nicht immer — besonders unter RLHF-Conditioning. Der minimale System-Prompt ("Du bist Nova. Antworte auf Deutsch.") reduziert das Problem, loest es aber nicht vollstaendig.

---

## 7. EI-MIKRO

Statt dem Modell alle EI-Regeln fuer alle Situationen zu geben, berechnet `_ei_mikro_anweisung()` in Python eine situative Mikro-Anweisung (3-8 Zeilen), die nur das Relevanteste fuer den aktuellen Turn enthaelt. Sieben optionale Bausteine:

1. **Laenge** — Immer aktiv. Maximale Satzanzahl.
2. **Energie-Spiegelung** — Bei Arousal >= 0.7. Gleiche Intensitaet.
3. **Vektor-Haltung** — Bei Bewegung. Richtung beachten.
4. **Intention** — Bei Hilferuf/emotionalem Ausdruck.
5. **Anti-Therapeut** — Bei Arousal >= 0.6 + Spirale/Absturz. Keine Templates.
6. **Rueckbezug** — Bei >= 3 Turns + Richtungswechsel.
7. **Beziehungsdynamik** — Bei Signal (Oeffnung, Distanz, Angriff).

**Prinzip:** Weniger Text = weniger Entscheidungen = klareres Verhalten. Ergebnis: durchschnittliche Antwortlaenge im emotionalen Test von ~25 auf ~8 Woerter.

---

## 8. Beziehungsdynamik nach Berne

Die Perzeption klassifiziert die aktuelle Beziehungsdynamik:

| Dynamik | Beschreibung | Nova-Reaktion |
|---------|-------------|---------------|
| `vertrauen` | Nutzer oeffnet sich, teilt Persoenliches | Persoenlicher werden, Naehe zeigen |
| `distanz` | Nutzer haelt Abstand, sachlich | Respektieren, sachlich bleiben |
| `angriff` | Vorwuerfe, Kritik an Nova | Ruhig bleiben, validieren, nicht defensiv |
| `hilfesuchend` | Ueberforderung, braucht Unterstuetzung | Fuersorglich, nicht auf Loesungen draengen |
| `dankbar` | Dankbarkeit, Zufriedenheit | Annehmen, warm bleiben |

> **Kognitionswissenschaftlicher Hintergrund:** Eric Bernes Transaktionsanalyse modelliert Kommunikation als Transaktionen zwischen drei Ich-Zustaenden. `hilfesuchend` entspricht dem Kind-Ich (verletzlich), `distanz` dem Erwachsenen-Ich (rational), `angriff` dem kritischen Eltern-Ich. Nova reagiert mit komplementaeren Transaktionen — fuersorgliches Eltern-Ich bei verletzlichem Kind-Ich, Erwachsenen-Ich bei sachlichen Fragen. Validiert in Chat 8 mit 8 Testszenarien nach Berne.

---

## 9. EI im Pipeline-Flow

Die EI-Berechnung ist vollstaendig deterministisch und in Python implementiert. Seit Chat 59 laeuft sie in einem eigenen Node `graph/nodes/ei_calc.py` — nicht mehr im Enricher.

```
Perzeption (LLM: Emotion + Arousal pro Turn)
    → produziert: current_emotion, current_arousal, beziehungs_dynamik, modus
    |
    v
Enricher (Python: laedt Daten — reiner I/O)
    → laedt: session_turns, raw_turns, char_hash_dict, Plugin-Kontext, KZG/LZG
    |
    v
EI-Calc (Python: berechnet Verlauf, Vektor, Stil, Nova-Empathie)
    → berechnet: emotions_verlauf (log decay), emotions_vektor (9 Richtungen),
      sprach_stil (Feature-Scoring), beziehungs_kontext, Modus-/Stil-Plausibilitaet,
      nova_emotions_verlauf (Decay + Empathie), nova_emotions_vektor, nova_emotion_konflikt
    |
    v
Router → [Planner] → GV-Node → Responder → ...
```

Das LLM liefert die Rohdaten (Emotion, Arousal, Beziehungsdynamik pro Turn via Perzeption). Python berechnet Verlauf, Vektor und Stil. Das LLM bekommt die Ergebnisse als Klartext im Responder-Prompt. Schneller, exakter, reproduzierbar.

**Funktions-Standort (seit Chat 58, AP1):** Alle 12 EI-Funktionen leben in `ei/berechnung.py` — extrahiert aus dem Enricher. Der EI-Calc-Node importiert sie. Ein zusaetzliches Paket (`_nova_empathie_berechnen()`) kam in Chat 59 (AP3) hinzu.

**rolle-Parameter:** `_emotions_verlauf_berechnen()` und `_emotions_vektor_bestimmen()` akzeptieren seit Chat 59 einen Parameter `rolle: str = "user"`. Fuer Novas eigenen Bogen wird `rolle="assistant"` uebergeben. Gleiche Funktion, gleicher Decay-Mechanismus — andere Turn-Filterung.

| Dimension | Berechnung | LLM-Call? |
|-----------|-----------|-----------|
| Emotions-Verlauf (User + Nova) | `_emotions_verlauf_berechnen()` im EI-Calc | Nein |
| Emotions-Vektor (User + Nova) | `_emotions_vektor_bestimmen()` im EI-Calc | Nein |
| Arousal | Float aus Perzeption, Decay im EI-Calc | Perzeption: Ja, Decay: Nein |
| Sprachstil | `_sprach_stil_erkennen()` + `_stil_plausibilitaet()` im EI-Calc | Nein |
| EI-Plausibilitaets-Gate | `_ei_arousal_berechnen()` + `_modus_plausibilitaet()` im EI-Calc | Nein |
| Nova-Empathie | `_nova_empathie_berechnen()` im EI-Calc | Nein |

### EI-Plausibilitaets-Gate

Die Perzeption erkennt Emotion und Arousal zuverlaessig, verwechselt aber Inhalt mit Stil. Das EI-Plausibilitaets-Gate im EI-Calc korrigiert das mit drei Faktor-Tabellen:

- **Beziehungsdynamik-Faktor:** vertrauen=1.0, distanz=0.3, angriff=0.8, hilfesuchend=1.0, dankbar=0.5
- **Intent-Faktor:** emotionaler_ausdruck=1.0, hilferuf=1.0, information_erfragen=0.3, ...
- **Tone-Faktor:** empathisch=1.0, sachlich=0.3, kreativ=0.5, direkt=0.7

Ergebnis: `ei_arousal = arousal * dynamik_faktor * intent_faktor * tone_faktor`

Der berechnete `ei_arousal` wird gegen eine Matrix geprueft. Alles Python, kein LLM-Call — deterministisch und nachvollziehbar.

> Detail: novaberg-node-ei-calc.md

---

## 10. Nova-Empathie (Dual-Emotion Phase 2, Chat 59)

Seit Chat 59 hat Nova einen eigenen Emotionsstrang. Der EI-Calc berechnet pro Turn zwei Kraefte, die auf Novas Position im Plutchik-Raum wirken:

### 10.1 Kraft 1 — Eigener Decay

`_emotions_verlauf_berechnen(nova_turns, rolle="assistant")` wendet den gleichen logarithmischen Decay auf Novas annotierte Session-Turns an. Der `rolle`-Parameter filtert Turns auf `rolle="assistant"`.

### 10.2 Kraft 2 — Asymmetrische Empathie

`_nova_empathie_berechnen(nova_verlauf_basis, current_emotion, current_arousal)` moduliert Novas Zustand durch die Emotion des Users. Der Empathie-Koeffizient α haengt von der Sektor-Distanz im Plutchik-Oktagon ab:

| Distanz | α | Effekt |
|---------|-----|--------|
| 0 (gleicher Sektor) | 0.10 | Leichte Bestaetigung |
| 1 (benachbart) | 0.15 | Geringe Modulation |
| 2 (nah-diagonal) | 0.35 | Spuerbare Modulation |
| 3 (fern-diagonal) | 0.70 | Empathie dominiert |
| 4 (gegenueberliegend) | 0.85 | Empathie ueberschreibt |

Ist Novas eigene Emotion neutral (kein Sektor bestimmbar), gilt `EMPATHIE_ALPHA_NEUTRAL = 0.30`.

### 10.3 Konflikt-Erkennung

Wenn Nova und User in gegenueberliegenden Sektoren sind UND beide mindestens `EMPATHIE_KONFLIKT_MIN_AROUSAL = 0.4` Arousal haben, setzt EI-Calc `nova_emotion_konflikt = True`. Beispiel: "Ich freue mich fuer dich, und gleichzeitig mache ich mir Sorgen."

**Config-Konstanten (alle in `config.py`, Chat 59):**

| Konstante | Wert | Zweck |
|-----------|------|-------|
| `EMPATHIE_ALPHA` | `{0:0.10, 1:0.15, 2:0.35, 3:0.70, 4:0.85}` | α pro Sektor-Distanz |
| `EMPATHIE_ALPHA_NEUTRAL` | `0.30` | α bei neutraler Nova-Emotion |
| `EMPATHIE_KONFLIKT_DISTANZ` | `3` | Ab welcher Distanz Konflikt geprueft wird |
| `EMPATHIE_KONFLIKT_MIN_AROUSAL` | `0.4` | Mindest-Arousal fuer Konflikt-Flag |

### 10.4 Kein Decay im Async-Pfad

Novas Antwort wird im async-Pfad (`services/nachbearbeitung.py`) per Perzeption analysiert und mit Emotion + Arousal in den Session-Turn annotiert — genau wie beim User. **Kein Decay beim Speichern.** Der Decay laeuft beim Lesen im synchronen EI-Calc des naechsten Turns. Eine Berechnung, nicht zwei.

> Detail: novaberg-ei-dual-emotion_k.md (Konzept), novaberg-node-ei-calc.md (Implementierung), novaberg-service-nachbearbeitung.md (async-Pfad)

---

## 11. Die zwei Achsen: WAS und WIE

EI-MIKRO und Kommunikations-Profil sind zwei unabhaengige Achsen:

| Achse | Quelle | Steuert |
|-------|--------|---------|
| **EI-MIKRO** | Berechnet pro Turn | WAS — Emotionale Haltung ("Auf seiner Seite sein. Kurz.") |
| **Kommunikations-Profil** | Aus Hash (Langzeit) | WIE — Register/Formulierung ("Formell, keine Emojis") |

EI-MIKRO hat Vorrang. Bei Arousal 0.8 + Spirale wird alles kurz — auch formeller Stil. Aber innerhalb der EI-Vorgabe waehlt Nova das Register: "Unertraeglich." (formell) vs. "Ey, das geht gar nicht!" (jugendlich).

### Hash-Analyse: Der Beweis (Chat 20)

Drei Smoking Tests (jugendlich, formell, emotional) × 15 Prompts zeigten verschiedene Destillationsergebnisse:

**Meister-Hash nach den Tests:**
> "Emotional und direkt, lockere jugendliche Formulierungen. Emotional volatil — schnelle Umschwuenge zwischen extremer Begeisterung und tiefen Abstuerzen."

**Novas Hash nach den Tests:**
> "Reflektiert und ausdrucksstark, klar und praezise. Emotional sehr stabil mit gleichmaessigen Plateau-Phasen."

Zwei deutlich verschiedene Persoenlichkeiten — destilliert aus verschiedenen Daten, mit den gleichen Prompts. Die Pipeline bildet die Datenlage korrekt ab. Novas Stabilitaet ist nicht programmiert — sie folgt aus der Art ihrer Daten (Recherchen, Beobachtungen, keine emotionalen Ausbrueche).

> **Das Cocktail-Problem:** Die Smoking Tests liefen unter `user_id="meister"`. Der User-Hash enthielt Meisters echte Persoenlichkeit, die Test-Prompts simulierten einen Teen. Drei von vier Signalen im Responder sagten "sachlich-erwachsen", eins sagte "jugendlich". Das Modell folgte der Mehrheit. **Das ist kein Bug — das ist korrektes Verhalten.** Ein echter Teen wuerde ueber Wochen seinen eigenen Hash aufbauen, und alle Signale wuerden in die gleiche Richtung zeigen.

---

*Konsolidiert aus nova-04-k.md.*
