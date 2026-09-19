# Novaberg — Wissenslücken: der Zug zu einem Thema (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-wissensluecken_k.md`](novaberg-wissensluecken_k.md) · Ausarbeitung: [`novaberg-wissensluecken_t.md`](novaberg-wissensluecken_t.md) · Bauplan und Umstellung: [`novaberg-wissensluecken_b.md`](novaberg-wissensluecken_b.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Beide Entscheidungen stehen in den Abschnitten, die sie tragen, und bleiben dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_t` §3, *Das Charakterfeld* (*„Es wird nicht persistiert.“*), und `_t` §5 (*„Eigener Agent, nicht Anhang am CharakterAgent.“*) | Die Lücken bekommen eine eigene Tabelle und einen eigenen Agenten, angestoßen über den Stack; das Charakterfeld entsteht im Lauf und wird verworfen, statt am Charakter persistiert zu werden | 27.07.2026 |
| **E2** | `_t` §2, *Nicht zwanzigmal dasselbe finden*, und *Drei Zustände, eine Sperrwirkung* | Die Tabelle ist ihre eigene Ausschlussliste über Embeddings (Dublette ab 0.95), nicht über eine Textliste im Prompt; ein Thema wird über den Zustand `ausgeschlossen` zum Antithema | 27.07.2026 |

Der Wortlaut der Entscheidungen steht in keinem der Abschnitte; sie geben sie als Ergebnis wieder.

**Im Text als entschieden geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_t` §2, *Erweitern braucht einen Erzeuger*: *„Entschieden …: ein LLM als Erzeuger, zwanzig Stichpunkte je Lauf.“* Die Zwanzig sind ausdrücklich ein Startwert.
- `_t`, *Audit*: *„Entscheidung vom 18.09.2026“* — sie gehört zu `novaberg-convention-nmcp.md` §8.4, nicht zu diesem Konzept.

---

## B. Offen beim Meister

- `_t` §5, Kasten *„Am 12.09.2026 gemessen und widerlegt“*, letzter Absatz: *„Die Reichweite ist damit klein, und der Rest ist eine Absichtsfrage: Wonach eine Lücke zu schließen wäre, die Nova kennt, ohne dass ihr Thema wörtlich in einem Knoten steht, ist offen. Ähnlichkeit ist es nicht.“*

**Offen ohne Frage an den Meister** — Punkte, die das Konzept selbst als offen führt:

- Abschnitt D (§8): Saat-Themen je Lauf, Verfall, Feld-Divergenz (dort *„hier nicht entschieden“*).
- `_t` §2: die Zwanzig *„nach der ersten Messung nachzujustieren“*; ob Umformulierungen die Schwelle 0.95 unterlaufen, *„zeigt die erste Messung an der Tabelle“*.
- `_t` §4, Kasten vom 02.08.2026: `charakter_anweisungen` trägt weiter kein `character_id`.
- `_k`, Kasten vor §1: *„Die Überarbeitung dieses Dokuments auf den Zyklus steht aus.“*

---

## C. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, mit Grund:

- `_t` §2 — Web-Suche und Ontologie als Erzeuger; teurer und ohne Gewähr, dass die Themen zu ihr passen.
- `_t` §2 — eine Text-Ausschlussliste im Prompt; verfehlt Umformulierungen und verstopft den Kontext.
- `_t` §2 — eine Dublette stumpf verwerfen statt auffrischen; ließe veraltete Werte stehen.
- `_t` §3 — eine Summe statt des Produkts; belohnte ein völlig fremdes Thema mit maximaler Neuheit.
- `_t` §3 — das Charakterfeld persistieren (E1); hieße, ein Zwischenergebnis synchron zu halten.
- `_t` §4 — ein `aktiv`-Flag statt `status`; sagt nicht, warum eine Zeile nicht mehr zählt.
- `_t` §5 — das Schließen einer Lücke, weil sie *„beim nächsten Lauf den Filter nicht mehr passiert“*; durchgestrichen, gemessen und widerlegt am 12.09.2026.
- `_t` §5 — der Agent als Anhang am CharakterAgent (E1).

---

## D. Aus §8 — Offen

§8 steht hier, weil `_e` die offenen Fragen sammelt. Die Zeile *Zusammenhang* vom Ende des Abschnitts steht in [`novaberg-wissensluecken_k.md`](novaberg-wissensluecken_k.md).

## 8. Offen

**Wie viele Saat-Themen je Lauf?** Die Stichprobe aus ihrem Bestand bestimmt, wie breit ein Lauf streut. Noch nicht entschieden.

**Verfall.** Eine Lücke, die über Wochen niemanden interessiert, sollte verblassen — sonst zieht die Tabelle ewig zu Themen, die einmal am Rand lagen. Ob über `aktualisiert_am` und einen Decay wie beim LZG-Gewicht, ist offen.

**Feld-Divergenz.** Wächst ihr Feld über Monate, interessiert sie sich am Ende für alles. `thinking-curiosity_k.md` §11 nennt das und schlägt ein Budget vor — hier nicht entschieden.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder die Entscheidung prüfen — das ist ein eigener Schritt. B1 bis B3 stammen aus der Sichtung.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_b` §6, Zeilen **ZIEL** und **MESSUNG** | Das ZIEL verspricht, ein besprochenes Thema *„verschwindet beim nächsten Lauf aus der Liste“*, die MESSUNG, die Zeile *„muss inaktiv werden oder fallen“*; `_t` §5 (Kasten vom 12.09.2026) widerlegt genau das — der nächste Lauf findet für eine alte Zeile nicht statt, und der Filter trägt die Unterscheidung nicht | `[gelesen 19.09.2026]` |
| **B2** | `_k`, Kasten vor §1 | *„Die Überarbeitung dieses Dokuments auf den Zyklus steht aus“* — seit dem 06.08.2026 unerledigt, der Stand ist der 18.09.2026 | `[gelesen 19.09.2026]` |
| **B3** | `_k` §7 gegen `novaberg-salienz-berechnung_k.md` | Hier speist der `neugier_vektor` den Antrieb (*„`salienz_charakter = max(ziel_grav, emo_grav, neugier_vektor)`“*); `novaberg-salienz-berechnung_k.md` nennt als Neugier-Bezug GV4 — zwei verschiedene Quellen für denselben Antrieb. Der bisherige Kopf (Abschnitt F) nennt ihn *„dritter Antrieb“*, die Sichtung *„vierten Antrieb“* | `[gelesen 19.09.2026]` |

---

## F. Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — persistente Wissenslücken, `neugier_vektor`, eigener Agent
**Stand:** 18. September 2026 (Audit: der Dienst belegt seinen Lauf selbst). Davor 27. Juli 2026, Chat 111
**Pfad:** novaberg/docs/novaberg-wissensluecken_k.md
**Typ:** Konzept
**Herkunft:** `novaberg-thinking-curiosity_k.md` (Vision, TR1/TR2) — dieses Dokument ist die konkrete Bauform
**Voraussetzung:** `novaberg-convention-abgeleitete-werte.md`
**Abnehmer:** `novaberg-salienz-berechnung_k.md` §4 — dritter Antrieb im Eigen-Pfad
