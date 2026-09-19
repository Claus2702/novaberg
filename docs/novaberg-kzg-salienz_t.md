# Novaberg — KZG-Salienz: Neubau als abgeleiteter Wert (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-kzg-salienz_k.md`](novaberg-kzg-salienz_k.md) · Bauplan und Umstellung: [`novaberg-kzg-salienz_b.md`](novaberg-kzg-salienz_b.md) · Diskussion und Ergänzungen: [`novaberg-kzg-salienz_e.md`](novaberg-kzg-salienz_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Ohne eigenen Teil, weil ohne Inhalt: Messungen.

---

## 3. Die Formel

```
salienz_roh = salienz_eingang + haeufigkeit * KZG_SALIENZ_BOOST

anteil      = min(salienz_roh / KZG_SALIENZ_CAP, 1.0)
salienz     = KZG_SALIENZ_CAP * sin(anteil * pi/2) ** KZG_SALIENZ_DAEMPFUNG_EXP
```

`salienz_roh` wird **nicht gespeichert**. Es entsteht bei jeder Berechnung neu aus zwei Feldern, von denen keines je aus `salienz` berechnet wurde — Regel (2) und (3) der Konvention.

Die zweite Hälfte ist formgleich mit `gewicht_absolut_berechnen` in `memory/lzg_knoten.py`. Das ist Absicht: Beide Speicher tragen dieselbe Kurve, nur mit verschiedenen Deckeln.

**Der Boost greift am Anker an, vor der Kurve.** Das ist keine Geschmacksfrage. Ein Zuwachs von 0.03 auf den gekrümmten Wert würde am unteren Ende der Skala etwas anderes bedeuten als am oberen — ein Eintrag mit Bewertung 0.5 erreichte das Tor nach vier statt nach sieben Wiederholungen.

## 4. Felder

| Feld | Typ | Herkunft | Änderbar |
|---|---|---|---|
| `salienz_eingang` | Float 0.0–1.0 | Bewertung des Modells beim Anlegen | **nein** |
| `haeufigkeit` | Integer | Zähler, +1 je thematischer Verstärkung | steigt |
| `salienz` | Float 0.0–1.0 | berechnet, materialisiert für Leser | jederzeit neu berechenbar |

`salienz_eingang` ist neu. `haeufigkeit` existiert. `salienz` existiert und wechselt die Bauart.

## 5. Konstanten

| Konstante | Wert | entspricht roh | war |
|---|---|---|---|
| `KZG_SALIENZ_CAP` | **1.0** | — | 10.0 |
| `KZG_SALIENZ_DAEMPFUNG_EXP` | **0.5** | — | 0.6 |
| `KZG_SALIENZ_BOOST` | **0.03** | — | *neu* |
| `KZG_SALIENZ_MINIMUM` | **0.67378** | 0.3 | 0.3 |
| `KZG_SALIENZ_MID` | **0.84089** | 0.5 | 0.5 |
| `KZG_SALIENZ_HIGH` | **0.94393** | 0.7 | 0.7 |

**Fünf Nachkommastellen, abgerundet — und das ist kein Schönheitsfehler.** Ein Tor wird mit `>=` geprüft. Der exakte Kurvenwert von 0.3 ist 0.6737882; auf 0.6738 *aufgerundet* liegt die Konstante über ihrem eigenen Rohwert, und wer genau die Bewertung trifft, die das Tor meint, fällt durch. Gemessen am Live-Turn vom 28.07.2026, 09:27 UTC: `Salienz 0.6738 (Eingang 0.30) < 0.6738 — abgelehnt`. Dasselbe galt für MID (0.8408964). Nur HIGH war schon abgerundet.

Der Exponent wird von 0.6 auf 0.5 gezogen, damit KZG und LZG dieselbe Kurve tragen.

**Die drei Schwellwerte sind Bilder der alten Rohwerte unter der neuen Kurve.** Fachlich ändert sich nichts: Wer früher 0.3 sagte, sagt weiterhin 0.3 — die Zahl in der Konfiguration heißt nur anders. Jede der drei Konstanten trägt ihr Roh-Äquivalent im Kommentar, sonst ist sie unlesbar (Konvention, Regel 7).

**Eine Stelle braucht dafür Code.** `agents/kzg/agent.py:71` vergleicht heute den rohen Modellwert gegen `KZG_SALIENZ_MINIMUM`. Dort muss die Kurve vor den Vergleich, sonst laufen zwei Skalen nebeneinander — genau der Zustand, den dieser Umbau beendet.

## 6. Der Weg zum Tor

| Bewertung | `salienz` | TTL-Stufe beim Anlegen | Verstärkungen bis zur Promotion | davon in LOW | längstmögliche Dauer |
|---|---|---|---|---|---|
| 0.30 | 0.6738 | LOW, 7 Tage | 14 | 7 | 147 Tage |
| 0.40 | 0.7667 | LOW, 7 Tage | 10 | 4 | 112 Tage |
| **0.50** | 0.8409 | MID, 14 Tage | **7** | 0 | 98 Tage |
| 0.60 | 0.8995 | MID, 14 Tage | 4 | 0 | 56 Tage |
| 0.65 | 0.9234 | MID, 14 Tage | 2 | 0 | 28 Tage |
| 0.70 | 0.9439 | HIGH, 30 Tage | 0 — sofort | 0 | — |

**Warum 0.03 und nicht weniger.** Die TTL-Stufen betragen 7, 14 und 30 Tage und werden nach derselben Salienz gewählt, die auch das Tor prüft. Jede Verstärkung frischt die TTL auf. Ein Eintrag muss also nicht nur *n*-mal wiederkommen, sondern jedes Mal innerhalb seines Fensters.

Bei einem Boost von 0.015 bräuchte ein Eintrag mit Bewertung 0.3 siebenundzwanzig Verstärkungen, vierzehn davon in Sieben-Tage-Fenstern — bis zu 280 Tage. Der Ansammlungspfad wäre für die untere Hälfte der Skala unerreichbar, während `novaberg-mem-kzg.md` das KZG als „schneller, flüchtiger Speicher über Tage und Wochen" beschreibt. Mit 0.03 halbiert sich der längste Weg.

Der Boost ist damit nicht frei gewählt, sondern durch die TTL-Stufen bestimmt. **Wer eine der beiden Größen ändert, prüft die andere mit.**

## 7. Die Konsumenten

`KZG-SALIENZ-KONSUMENTEN-DISSENS` verlangt als Abnahmebedingung, dass nach dem Umbau alle Leser auf dieselbe, dann tatsächlich eingehaltene Skala zeigen.

| Ort | heute | danach |
|---|---|---|
| `agents/synapsen_promotion/agent.py:17`, `:254` | dokumentiert Skala 0..10 | Kommentar auf 0..1 korrigieren |
| `agents/promotion/agent.py:322` | `min(salienz, 1.0)`, still | rechnerisch wirkungslos — **bleibt stehen** |
| `ei/gravitation.py:333` | ungeklemmt, multiplikativ im Lesepfad | Klemme nachrüsten — **bleibt stehen** |

Beide Klemmen bleiben. Sie sind die Zusicherung des Lesers an sich selbst, kein Pflaster über den Schreiber, und sie werden nicht als überflüssig zurückgebaut.

`_gedaempfter_boost` entfällt in beiden Kopien — `memory/kzg.py:229-249` und `agents/kzg/speicher.py:134-154`, deren Funktionskörper byte-identisch sind. Damit erledigt sich `REFAC-KZG-CODE-DUPLIKAT` mit.

## 8. Zweites Bauteil: der promotete Eintrag verlässt das KZG

Ein ins LZG promoteter Eintrag bleibt heute im KZG liegen. Der Wert existiert doppelt — einmal als `lzg_knoten`, einmal als Redis-Hash unter dem Schlüssel, den `lzg_knoten.kzg_quell_key` als Herkunft führt.

**Die im Backlog als ungeprüft markierte Frage ist beantwortet (Chat 111, Grep über beide Promotionspfade):** Der aktive Pfad `agents/synapsen_promotion/agent.py` hat **überhaupt keinen** Entfernungsschritt — kein `delete`, kein `expire`, kein `unlink`. Der schlafende Pfad `agents/promotion/agent.py:812` hat einen und ist damit das Vorbild:

```python
for key in promovierte_keys:
    redis_client.delete(key)
```

Es fehlt also nichts Kaputtes, es fehlt ein Schritt. Der Schritt gehört ans Ende des Neuanlage-Pfads, nach bestätigtem `knoten_anlegen` — und **nur** dort. Der Reinforcement- und der Halbreaktivierungs-Pfad legen keinen neuen Knoten an; dort wäre die Löschung ein Datenverlust.

**Warum beide Bauteile zusammengehören.** Über dem Tor bleiben nur 0.3 Kopfraum bis zum Deckel — bei einem Boost von 0.03 sind das elf Verstärkungen, dann steht der Wert auf 1.0 und rührt sich nicht mehr. Gemessen erreicht `haeufigkeit` heute Werte bis 43. Bliebe der Eintrag nach der Promotion liegen, staute sich alles Häufige erneut an einer Wand — diesmal bei 1.0, und im Lesepfad wären die meistgenannten Einträge nicht mehr unterscheidbar. Verlässt der Eintrag das KZG bei 0.7, sieht er den Deckel nie.

Zwei Folgeeinträge erledigen sich damit voraussichtlich mit: `KZG-TTL-UNSTERBLICH` (was das KZG verlässt, kann nicht ewig aufgefrischt werden) und `KZG-KEIN-DECAY` für den promoteten Teil des Bestands. **„Voraussichtlich" ist kein Messergebnis** — beide werden vor dem Schließen nachgemessen, nicht abgeleitet.

## 9. Wirkung im LZG

Die Übergabe `gewicht_roh = salienz` in `agents/synapsen_promotion/agent.py:319` bleibt unverändert.

| | `gewicht_roh` | `gewicht_absolut` |
|---|---|---|
| gerade promotet | 0.9439 | 3.843 |
| Höchstwert überhaupt | 1.0 | 3.955 |

Zwei Konsequenzen:

**`roh > CAP` kann nicht mehr auftreten.** Damit fällt `KZG-GEWICHT-ABSOLUT-CEILING` ersatzlos weg, ohne eine Zeile im LZG anzufassen. Jede Multiplikation an der Übergabestelle würde den Befund neu erzeugen — sie ist ausdrücklich nicht Teil dieses Konzepts.

**Alle Knoten werden fast gleich schwer geboren**, mit 1,1 % Spreizung. Das ist gewollt: Der Eintritt ist ein Ja/Nein, die Unterscheidung findet danach statt. Ein Knoten hält bei einer Halbwertszeit von 462 Tagen rund 6,7 Jahre, bevor er unter `LZG_KNOTEN_MIN_GEWICHT` fällt und deaktiviert wird — Zeit genug, sich zu entwickeln oder zu verblassen. Die Uhr beginnt bei jeder Verstärkung neu.

## Aus §11 — Bauteil 1b: Was Salienz für Novas Äußerung bedeutet

Befund, Prompt-Reparatur, `ZIEL` / `TEST` / `MESSUNG` und Abnahme von Bauteil 1b stehen in [`novaberg-kzg-salienz_b.md`](novaberg-kzg-salienz_b.md), §11; der offene Punkt *AgentGraph* in [`novaberg-kzg-salienz_e.md`](novaberg-kzg-salienz_e.md). Hier stehen die Unterabschnitte, die die Formel ausarbeiten.

#### Was Salienz für Novas Äußerung bedeutet

**Entschieden Chat 111.** Formel, Herleitung und das vollständige Charakter-Rad stehen in **`novaberg-salienz-berechnung_k.md`**. Hier nur der Umriss:

```
salienz_effektiv  = max( salienz_human × nutzer_gewichtung , salienz_charakter )
salienz_charakter = max( ziel_gravitation , emotionale_gravitation , neugier_bezug )
                    × (1 + erregungs_zuschlag)
```

| Größe | Herkunft | Bereich |
|---|---|---|
| `salienz_human` | LLM-Bewertung der Nutzeräußerung — im HumanGraph korrekt | 0.0–1.0 |
| `nutzer_gewichtung` | neues Feld auf `charakter_hash`, aus dem Zwölf-Speichen-Rad | **0.5–1.5**, Default 0.9 |
| `salienz_charakter` | Novas eigener Antrieb, je Segment | 0.0–1.0 |

**Je Segment, nicht je Turn.** Jedes Segment bekommt sein eigenes `salienz_effektiv`; der `user`-Eintrag behält `salienz_human` unverändert. Kognitive Begründung: Über `verbindung` sind alle Segmente ohnehin mit dem ganzen Turn verbunden — ein gering gewichteter Teil ist nicht gelöscht, sondern **nur nicht auffindbar**, weil er unbedeutend war.

~~**Drei Antriebe sind gebaut und nicht angeschlossen.**~~ — **teilweise überholt, Chat 112.** Die Ziel-Gravitation ist im Eigen-Pfad angeschlossen (und liefert dort gemessen 0.0, siehe `novaberg-salienz-berechnung_k.md` §9). Emotionale Gravitation und Neugier sind es weiterhin nicht. Dazugekommen ist ein vierter Antrieb, den diese Fassung nicht kannte: die **sprachliche Lesung des Segmenttexts** — die einzige segmentweite Größe im System und damit die einzige, die „je Segment" überhaupt einlösen kann.

#### Das neue Feld

| Spalte | Typ | Zweck |
|---|---|---|
| `nutzer_gewichtung` | `REAL NOT NULL DEFAULT 0.9` | der Faktor |
| `nutzer_gewichtung_quelle` | `TEXT NOT NULL DEFAULT 'default'` | `'default'` oder `'destilliert'` |
| `nutzer_gewichtung_am` | `TIMESTAMPTZ` | wann destilliert |

**Das Quelle-Feld ist Pflicht, keine Zierde.** `0.9` sieht aus wie ein echter Wert. Ohne die Trennung kann niemand unterscheiden, ob der Charakter das ergeben hat oder ob nie destilliert wurde — die Regel „ein Default darf nie aussehen wie ein echter Wert" (Konvention Regel 1, `novaberg-lesson_l_default-wie-fehlschlag.md`).

#### Das Charakter-Rad

Zwölf Speichen um die Nabe 0.9 — sechs nach oben (Summe 0.60), sechs nach unten (Summe 0.40). Ein LLM-Call in der Charakter-Destillation bewertet jede mit 0.0 / 0.5 / 1.0; der Faktor wird daraus gerechnet, nicht geschätzt. Volle Auslenkung trifft die Grenzen exakt.

**Die zwölf Speichen mit ihren Zügen stehen in `novaberg-salienz-berechnung_k.md` §5.** Sie sind eine Setzung, keine Messung, und ausdrücklich nachkalibrierbar.

Gespeichert wird **das ganze Rad**, nicht nur das Ergebnis: zwölf Ausprägungen plus der errechnete Faktor. Sonst wäre die Zahl ein Wert ohne Herkunft.

#### Zusammenspiel mit der Kurve

Das Produkt kann 1.5 erreichen, die Skala endet bei 1.0. Das wäre `KZG-SALIENZ-SKALENBRUCH` in neuer Gestalt — **es löst sich nur, wenn der Faktor am Anker angreift, vor der Kurve:**

```
salienz_roh = salienz_effektiv + haeufigkeit × KZG_SALIENZ_BOOST
anteil      = min(salienz_roh / KZG_SALIENZ_CAP, 1.0)
salienz     = KZG_SALIENZ_CAP · sin(anteil · π/2) ^ 0.5
```

Das `min()` kappt hart: Ein Produkt von 1.4 wird zu `salienz = 1.0` — maximal erinnerungswürdig, nicht jenseits der Skala. Stünde die Multiplikation **nach** der Kurve, wäre der Bruch wieder da.
