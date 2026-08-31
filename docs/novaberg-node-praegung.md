# Novaberg — Node: Prägung — das Faden-Tor

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Moduldokument — `graph/nodes/praegung.py`
**Stand:** 31. August 2026
**Pfad:** novaberg/docs/novaberg-node-praegung.md
**Konzept:** `novaberg-thinking-faszination_k.md` §7 (die Prägungsschicht), §7.3 (das Tor)
**Zustand:** 🟠 Scheibe 1 gebaut — Fäden entstehen, die **Verstärkung fehlt**

---

## 1. Aufgabe

Entscheidet je Turn, ob ein **Faden** entsteht — ein einschneidendes, embeddingbezogenes
Ereignis, das später zu Strängen verdichtet. Er ist das einzige, was die Fadenkarte von
*„jeder Turn ist ein Faden"* trennt, und trägt damit die volle Last.

Der Node **schreibt nicht in den Zustandsverbund**. Eine Prägung wirkt später über den
Prägungszug, nicht im Turn ihrer Entstehung.

## 2. Position

```
… → perzeption_assistant → ei_calc_persist → salience → praegung → dispatcher → END
```

**Die Position ist erzwungen, nicht gewählt.** Die effektive Salienz ist eine der beiden
Torbedingungen und wird erst im Salienz-Knoten gerechnet; nach dem Dispatcher ist der Turn
vorbei.

## 3. Ein- und Ausgänge

| Feld | Richtung | Quelle / Wirkung |
|---|---|---|
| `pending_writes` | liest | Salienz **und** perzipierte Emotion, aus `salienz_obj` des stärksten Segments |
| `nova_emotions_verlauf` | liest | nur die **Stärke** der Turn-Emotion, nicht die Führung |
| `prompt_embedding` | liest | Ort auf der Themenlandkarte |
| `praegung_faden` | schreibt | eine Zeile bei Durchlass |
| `pipeline_log` | schreibt | `schritt: praegung_tor` — **bei jeder Prüfung** |

**Kein Feld des Verbunds wird verändert.**

## 4. Das Tor — zwei Bedingungen

**Salienz** (`PRAEGUNG_TOR_SALIENZ`, 0,70) und **Emotionsausschlag**
(`PRAEGUNG_TOR_AUSSCHLAG`, 0,70). **Arousal ist keine davon** (Konzept §7.3): Der EI-Arousal
ist ein Mischwert und schleppte Beziehungsdynamik in ein Tor, das von Themenbindung handelt
— er steckt ohnehin im Emotionswert, weil dessen Decay arousal-abhängig ist.

> **Beide Schwellen sind Setzungen.** Deshalb protokolliert der Node **jede** Prüfung, auch
> die abgelehnte, mit beiden Werten und dem Grund. Eine Schwelle, deren Neins niemand zählt,
> kann aufhören zu trennen, ohne dass es auffällt — genau das war `EMGRAV-SCHWELLE-TOT`.

## 5. Drei Größen, die leicht zu verwechseln sind

`[gemessen]` 31.08.2026 — alle drei Fehler traten beim Bau auf und kosteten Betriebsturns:

| statt | richtig | warum |
|---|---|---|
| `salienz_human` (Mittel 0,41) | **effektive Salienz** (Mittel 0,80) | jene erreicht 0,90 in 3 von 2757 Läufen |
| Führung des Verlaufs | **Emotion des Turns** | der Verlauf ist eine Summe und hinkt dem Reiz **einen Turn nach** |
| Gewicht der Führung | **Gewicht der Fadenemotion** | sonst misst der Ausschlag eine Emotion, die der Faden nicht trägt |

Salienz und Emotion kommen aus **demselben Segment** — sonst trüge der Faden die Wucht des
einen und den Sektor eines anderen. Das Maximum entscheidet: Ein Turn mit einem einzigen
einschneidenden Satz ist einschneidend, auch wenn drei belanglose daneben stehen.

## 6. Verhalten

**Der Normalfall ist die Ablehnung.** `[gemessen]` 31.08.2026 über zwei Reihen: **14
Torzeilen, ein Faden.**

Fehlt eine der beiden Torgrößen, ist das **kein stiller Ausfall**: Der Node meldet mit
`logger.error` und lässt den Zustand unberührt. Ein Durchlass ohne geschriebene Zeile
ebenso — dann haben die Vorbedingungen von `faden_anlegen` abgelehnt.

## 7. Offene Punkte

**Die Verstärkung fehlt.** `praegung_beruehrung` steht, `beruehrung_anlegen()` ist gebaut
und getestet und hat **keinen Aufrufer**. Die Zuordnung Reaktivierung → Faden läuft über
Embedding-Nähe (Konzept §7.12, zwei Andockwege); der Gravitations-Node hält die Kandidaten
seit dem 30.08.2026 samt `knoten_id`. **Bis dahin bleibt `ausschlag_aktuell` für immer gleich
`ausschlag_absolut`.**

**Der Ausschlag ist eine Näherung.** Er stammt aus dem Verlauf und trägt damit Historie; das
Konzept will die Stärke *im Moment des Erlebens*. Eine reine Turn-Stärke liefert das System
heute nicht — die **Emotion** ist die des Turns, ihre **Stärke** nicht.

**Die Sektoren der Perzeption sind ungeprüft.** `[gemessen]` 31.08.2026 über acht gezielte
Plutchik-Reize: 4 von 8 getroffen, `neutral` dreimal, wo ein besetzter Sektor gemeint war.
Darauf bauen das Sektor-Histogramm eines Strangs (§7.8) und die acht Verfallsfaktoren (§7.9).

**Beide Torschwellen warten auf Kalibrierung** — sie ist erst nach Wochen laufender Fäden
möglich, und die Torzeilen sind ihre Grundlage.
