# Novaberg — KZG-Salienz: Neubau als abgeleiteter Wert (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-kzg-salienz_k.md`](novaberg-kzg-salienz_k.md) · Ausarbeitung: [`novaberg-kzg-salienz_t.md`](novaberg-kzg-salienz_t.md) · Bauplan und Umstellung: [`novaberg-kzg-salienz_b.md`](novaberg-kzg-salienz_b.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Ohne eigenen Teil, weil ohne Inhalt: Messungen. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Beide Entscheidungen stehen in dem Abschnitt, den sie tragen, und bleiben dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_k` §2, *„Entschieden …“* am Kopf des Abschnitts | Die Salienz ist das Tor zwischen Kurzzeit- und Langzeitgedächtnis und bildet zwei Wege ab, den Einprägsamen und den Angesammelten. Eingangswert und Zahl der Wiederholungen sind zwei getrennte, gespeicherte Größen; die Salienz ist ihre reine Funktion | Konzeptphase, Juli 2026 — der Abschnitt nennt eine Sitzung, kein Datum |
| **E2** | `_t`, *Aus §11 — Bauteil 1b*, Unterabschnitt *„Was Salienz für Novas Äußerung bedeutet“* | Für Novas Äußerung wird die Salienz gerechnet, nicht gefragt: `salienz_effektiv = max(salienz_human × nutzer_gewichtung, salienz_charakter)`, je Segment, nicht je Turn. Formel, Herleitung und Charakter-Rad stehen in `novaberg-salienz-berechnung_k.md` | wie E1 |

Der Wortlaut der Entscheidungen steht in keinem der beiden Abschnitte; beide geben sie als Ergebnis wieder, und keiner nennt einen Urheber.

**Im Text als Setzung oder Festlegung geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_b` §10, *„Wirkung der Setzung 0.6“* — die geschätzte Eingangsbewertung der verstärkten Alteinträge bei der Migration vom 28.07.2026.
- `_t`, *Aus §11*, *Das Charakter-Rad*: Die zwölf Speichen *„sind eine Setzung, keine Messung, und ausdrücklich nachkalibrierbar“*.
- `_t` §7: *„Beide Klemmen bleiben.“*
- `_t` §6: Der Boost 0.03 *„ist damit nicht frei gewählt, sondern durch die TTL-Stufen bestimmt“*.

---

## B. Offen beim Meister

Keine. Das Konzept legt keine Frage ausdrücklich zur Entscheidung vor. Der offene Punkt *AgentGraph* (Abschnitt C) ist eine Frage an die Absicht und nicht an den Bau — er ist der Kandidat, falls eine Frage vorgelegt werden soll.

---

## C. Offen ohne Frage

Offene Punkte, die das Konzept selbst führt:

- Unten, *Aus §11 — Bauteil 1b*: Der AgentGraph hat keine Nutzeräußerung; ein Impuls ohne Zielbezug bekäme Salienz 0 und würde nie gespeichert — *„nicht entschieden“*.
- `_b` §11, Bauteil 1a, *Offenes Risiko*: Ein Segment kann ohne seine Nachbarn unauflösbar sein; belegt ist *„einen Fall, nicht die Klasse“*.
- `_b` §11, Bauteil 1a, *Nicht behoben*: Alle drei Segmente erhielten Salienz 0.3; der Verdacht, dass die Bewertung den Gesamtzusammenhang statt des Segments liest.
- `_b` §11, Bauteil 2: Die Promotion entfernt den Eintrag — `ZIEL` / `TEST` / `MESSUNG` stehen, ein Baubericht nicht (Befund B3).
- `_t` §8: `KZG-TTL-UNSTERBLICH` und `KZG-KEIN-DECAY` erledigen sich *„voraussichtlich“* mit; beide werden vor dem Schließen nachgemessen.
- `_k` §12: Decay auf der KZG-Salienz wird **nach** der Messung aus §11 entschieden; die Lebensdauer im LZG (rund 6,7 Jahre) ist ein eigener Befund; E7 aus `novaberg-charakter-resonanz_k.md` ist neu zu stellen, sobald die Skala hält.

### Aus §11 — Bauteil 1b

Die übrigen Teile von Bauteil 1b stehen in [`novaberg-kzg-salienz_b.md`](novaberg-kzg-salienz_b.md) (Befund, Prompt-Reparatur, `ZIEL` / `TEST` / `MESSUNG`, Abnahme) und in [`novaberg-kzg-salienz_t.md`](novaberg-kzg-salienz_t.md) (Formel, Feld, Rad, Kurve).

#### Offen

**Der AgentGraph.** Ein eigener Gedanke hat keine Nutzeräußerung, `salienz_human` existiert nicht. Der Ausdruck fällt auf `salienz_charakter` zusammen — reiner Zielbezug. Folge: Ein Impuls ohne Zielbezug bekäme Salienz 0 und würde nie gespeichert. Das ist eine nachvollziehbare Konsequenz, aber **nicht entschieden**.

---

## D. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Grund:

- `_t` §3 — der Boost auf den gekrümmten Wert statt am Anker; verworfen, weil ein Eintrag mit der Bewertung 0.5 das Tor dann nach vier statt nach sieben Wiederholungen erreichte.
- `_t` §5 — die auf vier Stellen aufgerundeten Tore; verworfen nach dem Live-Turn vom 28.07.2026, weil ein Tor mit `>=` genau die Bewertung abwies, die es meint.
- `_t` §6 — ein Boost von 0.015; verworfen, weil der Ansammlungspfad für die untere Hälfte der Skala unerreichbar würde (bis zu 280 Tage).
- `_t` §7 — die Klemmen der Leser als überflüssig zurückbauen; ausdrücklich nicht.
- `_t` §9 — eine Multiplikation an der Übergabestelle ins LZG; ausdrücklich nicht Teil des Konzepts.
- `_t`, *Aus §11*, *Zusammenspiel mit der Kurve* — die Multiplikation mit `nutzer_gewichtung` nach der Kurve; verworfen, weil der Skalenbruch wiederkäme.
- `_t`, *Aus §11* — ~~*„Drei Antriebe sind gebaut und nicht angeschlossen“*~~; teilweise überholt, die Ziel-Gravitation ist angeschlossen.
- `_b` §10 — ~~*„Aufgelöst durch den Reset am 27.07.2026“*~~; überholt am 28.07.2026, weil in einem Tag 192 neue Einträge entstanden.
- `_b` §11, Bauteil 1a — das `[LAGEBILD]` um den Volltext erweitern; bewusst nicht, sonst stünde die beseitigte Ursache wieder im Prompt.
- `_b` §11, Bauteil 1b — ~~*„nur nicht mehr für die Salienz-Skala“*~~; der Rollen-Switch wird samt Skala gebraucht.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code prüfen oder entscheiden lassen — das ist ein eigener Schritt. B1 bis B5 stammen aus der Sichtung, B6 bis B8 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_t`, *Aus §11 — Bauteil 1b*, Absatz *„~~Drei Antriebe …~~ — teilweise überholt …“* | *„Emotionale Gravitation und Neugier sind es weiterhin nicht“*; die Emotionale Gravitation ist seit dem 11.09.2026 angeschlossen (Featureliste *Emotionale Gravitation* 🟠, `novaberg-salienz-berechnung_k.md` §4b) | `[gelesen 19.09.2026]` |
| **B2** | Abschnitt F, bisheriger Kopf, Kasten *„Diese Zeile war eine Absicht …“* | Für den Stand der IDs verweist er auf `novaberg-backlog.md`; diese Datei trägt keine Einträge mehr, sie stehen in `novaberg-backlog-{gegenstand}.md` (Wegweiser `novaberg-backlog-index.md`) | `[gelesen 19.09.2026]` |
| **B3** | `_b` §11, Bauteil 2 | Der Stand ist unklar: Der bisherige Kopf (29.07.2026) führt `PROMOTION-ENTFERNT-KZG-NICHT` als offen, §11 trägt bei Bauteil 2 weder Häkchen noch Baubericht | `[gelesen 19.09.2026]` |
| **B4** | Abschnitt F, bisheriger Kopf (*„Sollte schließen …“*); `_t` §8 | Hier und in `novaberg-embedding-casing-blind_k.md` (Nachtrag 04.09.2026): Der KZG-Eintrag wird nach der Promotion nicht gelöscht. `novaberg-memory-synapsen_t.md` §7.7 sagt, er wird gelöscht (dort `_e` B5) | `[gelesen 19.09.2026]` |
| **B5** | `_t` §4 (`salienz` Float 0.0–1.0) | `novaberg-memory-synapsen-p4-entscheidungen_k.md` K8 nennt die KZG-Salienz-Skala 0–10 | `[gelesen 19.09.2026]` |
| **B6** | `_b` §11, Bauteil 1b, *„Offen aus diesem Bauteil“* | *„Der Rollen-Switch am Prompt (Bauteil unten) wird jetzt dringender“*; der Unterabschnitt *„Der Prompt bleibt trotzdem zu reparieren — erledigt …“* steht davor, nicht darunter, und meldet ihn als gebaut und abgenommen | `[gelesen 19.09.2026]` |
| **B7** | `_b` §11, Bauteil 1a, *„Warum vor Bauteil 1“* | Der Absatz nennt ein Bauteil 3; das Konzept führt die Bauteile 0, 1a, 1b, 1 und 2 | `[gelesen 19.09.2026]` |
| **B8** | `_k` §12, Absatz *E7* | *„`novaberg-charakter-resonanz_k.md` §442“* sieht nach einer Zeilennummer aus, nicht nach einem Abschnitt; die Zeile *Zusammenhang* nennt dieselbe Stelle *„§E7“* | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen

### Bisheriger Kopf

Der Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier und nicht in einem Teil *Messungen*.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Bauart, Skala und Tore der KZG-Salienz
**Stand:** 29. Juli 2026, Chat 117 (Abgleich der „Schließt"-Zeile gegen den Code — drei der sieben IDs sind offen. Bauteil 1: gebaut, migriert und live gemessen, Chat 113)
**Pfad:** novaberg/docs/novaberg-kzg-salienz_k.md
**Typ:** Konzept
**Voraussetzung:** `novaberg-convention-abgeleitete-werte.md`
**Ersetzt:** die Bauart in `memory/kzg.py` und `agents/kzg/speicher.py` (`_gedaempfter_boost`)
**Schließt:** `SALIENZ-OHNE-PIPELINE-LOG` · `KZG-SALIENZ-SKALENBRUCH` · `KZG-SALIENZ-BOOST-OHNE-DECKEL` · `KZG-GEWICHT-ABSOLUT-CEILING`

**Sollte schließen, tut es nach Bauteil 1 aber nicht** (geprüft am Code, 29.07.2026): `KZG-SALIENZ-KONSUMENTEN-DISSENS` — die Klemme in `ei/gravitation.py` fehlt weiterhin · `PROMOTION-ENTFERNT-KZG-NICHT` — die Synapsen-Promotion löscht den KZG-Eintrag nach wie vor nicht · `REFAC-KZG-CODE-DUPLIKAT` — `_gedaempfter_boost` ist aufgelöst, das doppelte Hash-Mapping in `kzg_store` und `_neu_anlegen` besteht fort.

> **Diese Zeile war eine Absicht, kein Zustand.** Sie stand von Anfang an im Kopf des Konzepts und liest sich wie eine Erledigt-Liste. Wer nach einer der drei IDs sucht und hier landet, hält sie für geschlossen. Der Stand jeder einzelnen steht in `novaberg-backlog.md`.
