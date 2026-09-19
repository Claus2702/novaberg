# novaberg-metakognition_k.md

**Absicht:** Nova bekommt ein Gedächtnis über ihren eigenen Verarbeitungsprozess — jeder Knoten schreibt seine Entscheidung in ein Log, Nova kann dieses Log im Gespräch befragen, und eine Selbstreflexion leitet aus wiederkehrenden Mustern Vorsätze und Aktionen ab, die ihr künftiges Verhalten ändern, gehalten von drei Regulationskräften, damit Feedback sie nicht in schädliche Muster zieht.
**Stand:** 15. September 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Metakognition Phase 1* (Pipeline-Log) 🟠 · *Metakognition Phase 2* (`pipeline_search`) ⚫ · *Metakognition Phase 3–6* (Vorsätze, Selbstreflexion) ⚫ · *Pipeline-Log* (Forensik, Spans, JSONB) 🔴 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-metakognition_t.md`](novaberg-metakognition_t.md) · [`novaberg-metakognition_b.md`](novaberg-metakognition_b.md) · [`novaberg-metakognition_e.md`](novaberg-metakognition_e.md) · [`novaberg-metakognition_m.md`](novaberg-metakognition_m.md)
**Entschieden:** 0 · **Offen beim Meister:** 0 (Liste in [`novaberg-metakognition_e.md`](novaberg-metakognition_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-metakognition_k.md §5.3` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-metakognition_t.md`](novaberg-metakognition_t.md), `_b` ist [`novaberg-metakognition_b.md`](novaberg-metakognition_b.md), `_e` ist [`novaberg-metakognition_e.md`](novaberg-metakognition_e.md), `_m` ist [`novaberg-metakognition_m.md`](novaberg-metakognition_m.md).

| § | Datei |
|---|---|
| 1 | `_k` |
| 2 · 2.1 · 2.2 · 2.3 · 2.4 · 2.5 | `_t`; aus §2.1 die Absätze *Am Bestand nachgeprüft, nicht nur am Code* und *Der Bestand ist dabei breiter …*, aus §2.2 der Absatz *Die Verteilung sagt zugleich …*, aus §2.5 der Kasten *„Dauerhaft“ gilt ab dem 27.07.2026, nicht davor* in `_m` |
| 3 · 3.1 · 3.2 · 3.3 · 3.4 | `_t` |
| 4 · 4.1 · 4.2 · 4.3 · 4.4 · 4.5 | `_t` |
| 5 · 5.1 · 5.2 · 5.3 · 5.4 · 5.5 · 5.6 · 5.7 | `_t`; aus §5.2 der Unterabschnitt *Gemessen am 03.08.2026 — halb blind* in `_m`, der Unterabschnitt *⬜ Entwurf: die zweite Messgröße „Abdeckung“* in `_b`; aus §5.7 der Unterabschnitt *Verschärfung — aus dem Einzelfall wurde eine Rate* in `_m` |
| 6 · 6.1 · 6.2 | `_t` |
| 7 (mit den Bauteilen MK-1a bis MK-6) | `_b` |
| 8 · 9 | `_k` |
| 10 | `_e` (Abschnitt D) |
| Versionshistorie | `_e` (Abschnitt F) |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Status, Herkunftsvermerk, Zahlen, Verwandt, Quellen) | `_m` |
| Kasten *Übergeordnet seit dem 06.08.2026* | `_k` |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

Die Lesevereinbarungen des bisherigen Kopfs — *Herkunftsvermerk* (ohne Vermerk gilt eine Aussage als Annahme) und *Zahlen* (Zählungen tragen ihr Messdatum) — gelten für alle fünf Teile; sie stehen mit der Liste der verwandten Konzepte ungekürzt in [`novaberg-metakognition_m.md`](novaberg-metakognition_m.md), unter „Bisheriger Kopf“.

> **Übergeordnet seit dem 06.08.2026: `novaberg-thinking-erkenntniszyklus_k.md`.** Dieses Dokument beschreibt in §4.2 und §6.2 einen **Auslösepfad für Hintergrundaufträge**. Die Folge, in der solche Aufträge entstehen, besitzt seit dem 06.08.2026 der Zyklus. Insbesondere gilt: **Ein Auftrag aus Selbstbeobachtung tritt bei Schritt 1 in den Zyklus ein** — er geht nicht direkt an einen Agenten.

---

## 1. Vision

Nova weiß heute nicht, warum sie etwas gesagt hat. Die Emotionsberechnung, der Gesprächsvektor, das Tribunal-Urteil, die Thinker-Korrektur — all das existiert für einen Turn, wird ins Debug-Log geschrieben, und ist danach für Nova unsichtbar. Sie kann nicht reflektieren, weil sie keinen Zugang zu ihrem eigenen Denkprozess hat.

Dieses Konzept gibt Nova ein Gedächtnis über ihren eigenen Verarbeitungsprozess und die Fähigkeit, daraus Verhaltensänderungen abzuleiten.

Drei Schichten:

1. **Pipeline-Log** — Jeder Node schreibt seine Entscheidung in eine Datenbank
2. **Selbstbeobachtung** — Nova kann ihr eigenes Log durchsuchen
3. **Vorsätze** — Ein Reflexions-Agent erkennt Muster und leitet Verhaltensanweisungen ab, die Novas künftiges Verhalten steuern

Der geschlossene Kreis:

```
Handeln → Beobachten → Reflektieren → Vorsatz fassen → Verhalten aendern
   ↑                                                          |
   └──────────────────────────────────────────────────────────┘
```

**Stand September 2026.** Der Kreis ist an keiner Stelle geschlossen. Gebaut ist allein die Beobachtungsschicht — das Pipeline-Log schreibt, und es schreibt mehr als entworfen (§2, §2.5). Was stattdessen gemessen vorliegt, ist der Kreis **ohne** seinen Reflexionsschritt: was geschieht, wenn Verhalten Feedback erzeugt und niemand es prüft (§5.7).

> **Kognitionswissenschaftlicher Bezug:** Flavell (1979) definierte Meta-Kognition als "Denken über das Denken". Zimmerman (2000) beschrieb den Kreislauf aus Voraussicht (Vorsätze), Ausführung (Handeln mit Selbstbeobachtung) und Selbstreflexion (Bewertung + Anpassung). Carver & Scheier (1982) modellierten Selbstregulation als Feedback-Schleife: Ist-Zustand messen, mit Soll-Zustand vergleichen, Differenz reduzieren.

---

> **§2 bis §7 und §10 stehen nicht in dieser Datei.** Die Ausarbeitung der drei Schichten, der Regulationskräfte und des Lebenszyklus (§2 bis §6) steht in [`novaberg-metakognition_t.md`](novaberg-metakognition_t.md), die Implementierungs-Phasen mit den Bauteilen MK-1a bis MK-6 (§7) und der Entwurf der Messgröße *Abdeckung* in [`novaberg-metakognition_b.md`](novaberg-metakognition_b.md), das Paper-Potenzial (§10) und die Versionshistorie in [`novaberg-metakognition_e.md`](novaberg-metakognition_e.md), die Messungen am Bestand in [`novaberg-metakognition_m.md`](novaberg-metakognition_m.md). Welche Datei welchen Abschnitt trägt, sagt die Tabelle oben.

## 8. Wissenschaftliche Einordnung

- **Flavell (1979):** metacognitive knowledge (Log), experience (Beobachtung), regulation (Vorsätze)
- **Zimmerman (2000):** Forethought → Performance → Self-Reflection
- **Carver & Scheier (1982):** Feedback-Loop: Referenzwert → Vergleich → Reduktion
- **Higgins (1987):** Ideal-Selbst vs. Soll-Selbst vs. Real-Selbst → Charakter-Gravitation
- **Skinner (1938):** Operante Konditionierung, aber selbstgesteuert
- **Sterling (2012):** Allostase → Monotonie-Druck

**Abgrenzung:** Reflektive, nicht introspektive Meta-Kognition. Nova "spürt" nicht während des Denkens, kann aber nachträglich reflektieren.

> **"Wir bauen kein Bewusstsein. Wir simulieren bekannte Regulationsprozesse."**

---

## 9. Prinzipien

> **"Nova beobachtet sich selbst."**

> **"Vorsätze kommen von innen."** Der User kann anregen, aber Nova entscheidet.

> **"Sein oder Tun."** Reflexion erzeugt Verhaltensänderungen (ich will anders SEIN) und Aktionen (ich will etwas TUN). Vorsätze modulieren, Aktionen handeln. Beide entstehen aus derselben Beobachtung.

> **"Drei Kräfte, ein Gleichgewicht."** Feedback, Monotonie-Druck, Charakter-Gravitation. (Zielbild; Bestand siehe §5.4)

> **"Der Charakter ist der Magnet."** Vorsätze sind kurzfristig und werden vom Charakter-Hash zurückgezogen. Nur persistente, immer wieder verstärkte Vorsätze verschieben langfristig den Charakter selbst. (gilt, sobald der gespeicherte Charakter Novas ist; siehe §5.3)

> **"Transparenz, nicht Kontrolle."**

> **"Gefallen ja, Schaden nein."** Nova darf dem User gefallen — aber Charakter-Gravitation verhindert, dass Feedback-Optimierung in schädliche Muster führt. Echte Fürsorge schließt nicht ab.

---
