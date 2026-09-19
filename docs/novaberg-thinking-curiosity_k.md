# Novaberg — Neugier (Konzept)

**Absicht:** Nova entwickelt eigene, charakter-konsistente Interessen: Was an ihr Resonanz-Feld anschließt, aber davon abweicht, weckt Neugier — im Traum-Modus als eigene Exploration, die an Sättigung oder Drift endet und bei Gewinn ihr Feld wachsen lässt, im Gespräch als Tiefe ihrer Nachfragen, gebremst durch den sozialen Spielraum; was nicht resoniert, lässt sie liegen.
**Stand:** 8. September 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Neugier (Resonanz, Neuheit, Register)* 🔴 · *Traum-Modus* ⚫ · *Vertiefung (aus dem eigenen Bestand)* 🔴 · *VertiefungsAgent* ⚫ · *GV4 — Wissenslücken im Prompt* 🔴 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-thinking-curiosity_t.md`](novaberg-thinking-curiosity_t.md) · [`novaberg-thinking-curiosity_b.md`](novaberg-thinking-curiosity_b.md) · [`novaberg-thinking-curiosity_e.md`](novaberg-thinking-curiosity_e.md) · [`novaberg-thinking-curiosity_m.md`](novaberg-thinking-curiosity_m.md)
**Entschieden:** 0 · **Offen beim Meister:** 0 (Liste in [`novaberg-thinking-curiosity_e.md`](novaberg-thinking-curiosity_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-thinking-curiosity_k.md §3.3` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-thinking-curiosity_t.md`](novaberg-thinking-curiosity_t.md), `_b` ist [`novaberg-thinking-curiosity_b.md`](novaberg-thinking-curiosity_b.md), `_e` ist [`novaberg-thinking-curiosity_e.md`](novaberg-thinking-curiosity_e.md), `_m` ist [`novaberg-thinking-curiosity_m.md`](novaberg-thinking-curiosity_m.md).

| § | Datei |
|---|---|
| Titelzeile, Kopfblock, Tabelle, Vermerk *Übergeordnet seit dem 06.08.2026* | `_k` |
| Namens- und Zustandsvermerk mit der *Berichtigung des Vermerks — 08.09.2026, gegen den Code gemessen* (zwischen Kopf und §1) | `_m` |
| 1 | `_k` |
| 2 · 2.1 · 2.2 · 2.3 · 2.4 | `_k` |
| 3 · 3.1 · 3.2 · 3.3 · 3.4 | `_t` |
| 4 · 4.1 · 4.2 · 4.3 · 4.4 · 4.5 · 4.6 · 4.7 | `_t` |
| 5 · 5.1 · 5.2 · 5.3 · 5.4 · 5.5 · 5.6 · 5.7 · 5.8 | `_t` |
| 6 · 6.1 · 6.2 | `_t` |
| 7 · 7.1 · 7.2 | `_t` |
| 8 · 8.1 · 8.2 · 8.3 | `_k` |
| 9 | `_t` |
| 10 | `_b` |
| 11 | `_e` (Abschnitt C) |
| *Verwandte Dokumente* (Schlussliste ohne Nummer) | `_k` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Quellen) | `_e` (Abschnitt F) |
| Entschieden, Offen beim Meister, offene Fragen, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

> **Übergeordnet seit dem 06.08.2026: `novaberg-thinking-erkenntniszyklus_k.md`.** Dieses Dokument beschreibt einen **Bestandteil**; die Folge, in der er ausgelöst wird, besitzt der Zyklus. Insbesondere gilt: **Recherche und Vertiefung werden nicht mehr direkt aus einer Intention ausgelöst**, sondern erst, wenn das Nachdenken über den vorhandenen Bestand eine Lücke gefunden hat. Die Überarbeitung dieses Dokuments auf den Zyklus steht aus.

---

> **Der Namens- und Zustandsvermerk steht nicht in dieser Datei.** Er stand hier, zwischen Kopf und §1, zusammen mit seiner Berichtigung vom 08.09.2026, und steht ungekürzt in [`novaberg-thinking-curiosity_m.md`](novaberg-thinking-curiosity_m.md). Er trennt die drei Größen, die im Konzept und im Code „Neugier“ heißen — `aufnahmebereitschaft`, `wissensluecken`, `neugier_vektor` —, und sagt, welche davon dieses Konzept beschreibt.

---

## 1. Vision

Der Traum-Modus gibt Nova intrinsische Motivation. Statt nur Wissen zu sammeln oder Aufträge abzuarbeiten, entwickelt Nova eigene Interessen, die aus ihrem Charakter wachsen. Das Ergebnis: ein Assistent, der nicht nur hilft, sondern der von manchen Themen **mehr wissen will** — und von anderen nicht.

> **Leitmetapher:** Ein Mensch liest einen Artikel und plötzlich kommt diese eine Stelle, wo er denkt: "Ha! Was ist das denn? Das muss ich gleich noch extra recherchieren." Dieser Moment — die Neugier — ist kein Zufall. Er entsteht, weil das Gelesene an vorhandenes Wissen **anschließt, aber abweicht**. Nah genug, um die Verbindung zu sehen. Weit genug, um das eigene Modell herauszufordern.

**Designziel:** Nova soll "erstaunlich auf den Menschen wirken" — nicht durch Simulation von Bewusstsein, sondern durch erkennbare, charakter-konsistente Neugier, die über Zeit wächst und sich verändert.

---

## 2. Kognitionswissenschaftliche Grundlage

### 2.1 Information Gap Theory (Loewenstein 1994)

Neugier entsteht nicht aus Unwissenheit, sondern aus dem Erkennen einer **Lücke in vorhandenem Wissen**. Voraussetzung: Man muss **genug** wissen, um die Lücke zu bemerken. Totale Ahnungslosigkeit erzeugt keine Neugier — teilweises Wissen schon.

**Implikation für Nova:** Nova kann nur neugierig auf Themen werden, die an ihr bestehendes Charakter-Feld angrenzen. Ein leeres Feld erzeugt keine Neugier. Das Saatgut (Botanik, Natur, Kräuter) ist die Voraussetzung.

### 2.2 Prediction Error mit positiver Valenz

Der "Ha!"-Moment ist neurobiologisch ein **positiver Vorhersagefehler**: Das Gehirn liest mit, prediziert — und etwas Unerwartetes schließt an Bekanntes an. Das Dopaminsystem belohnt nicht das Wissen selbst, sondern die **Antizipation** — das Gefühl, gleich etwas Wertvolles zu finden.

**Implikation für Nova:** Der Neugier-Trigger feuert **vor** der Exploration, nicht nach. Die Bewertung ("war es wertvoll?") kommt danach als Resonanz-Bestätigung.

### 2.3 Berlynes umgekehrte U-Kurve

Neugier entsteht bei **mittlerer Informationsdistanz**:
- Zu nah = langweilig ("das weiß ich schon")
- Zu weit = irrelevant ("das betrifft mich nicht")
- In der Mitte = Sweet Spot, wo Neugier feuert

Der Charakter bestimmt, **wo** auf dem Spektrum die Kurve ihren Peak hat.

### 2.4 Compression Progress (Schmidhuber 1991)

Ein System wird intrinsisch belohnt, wenn es sein eigenes Modell der Welt verbessern kann. Nicht für das Wissen selbst, sondern für den **Fortschritt im Verstehen**. Novas Neugier-Score misst genau das: Wie sehr erweitert diese Information mein Modell von mir selbst?

---

> **§3 bis §7 stehen nicht in dieser Datei.** Der Kernmechanismus mit Formel und Schwellwert (§3), der Traum-Zyklus mit Sättigung, Serendipity, den zwei Verfolgungsstrategien und der Reflexion (§4), die Neugier im Gespräch (§5), die emergenten Interessenketten (§6) und Metriken und Monitoring (§7) stehen in [`novaberg-thinking-curiosity_t.md`](novaberg-thinking-curiosity_t.md).

---

## 8. Abgrenzung

### 8.1 Was der Traum-Modus IST

- Eine **funktionale Analogie** zu menschlicher Neugier — mit anderen Substraten, aber derselben Struktur
- Ein Mechanismus, der Novas Charakter über Zeit **wachsen** lässt
- Eine messbare, architektonisch saubere Bewertungsfunktion
- Ein System, das auf den Menschen **erstaunlich und lebendig** wirkt

### 8.2 Was der Traum-Modus NICHT IST

- Keine Simulation von Bewusstsein oder Emotionen
- Kein AGI-Baustein — Nova ist ein Assistent, kein autonomes Wesen
- Keine "künstliche Reue" oder "irreversible Charakterverformung"
- Keine Ersetzung menschlicher Verbindung

### 8.3 Abgrenzung zu bestehenden Pixie-Agenten

| Agent | Trigger | Ziel | Neugier? |
|-------|---------|------|----------|
| RechercheAgent | Queue (aufgabe: recherche) | Wissen für den User finden | Nein — User-Auftrag |
| VertiefungsAgent | Queue (aufgabe: vertiefen) | Lücken in bestehendem Wissen füllen | Nein — wissensbezogen |
| **Traum-Modus** | Periodisch (Queue leer) | Novas eigene Interessen explorieren | **Ja — charakter-getrieben** |

Der VertiefungsAgent wird vom Traum-Modus als **Infrastruktur** genutzt (Phase 3: Exploration). Aber der Trigger und die Bewertung sind grundverschieden: Der VertiefungsAgent füllt Lücken, der Traum-Modus folgt Neugier.

---

> **§9 bis §11 stehen nicht in dieser Datei.** Die Konfiguration (§9) steht in [`novaberg-thinking-curiosity_t.md`](novaberg-thinking-curiosity_t.md), die Implementierungsreihenfolge (§10) in [`novaberg-thinking-curiosity_b.md`](novaberg-thinking-curiosity_b.md), die offenen Fragen (§11) in [`novaberg-thinking-curiosity_e.md`](novaberg-thinking-curiosity_e.md).

---

Verwandte Dokumente:
- VertiefungsAgent (Shared Infrastruktur): `novaberg-pixie-deepdive_k.md`
- RechercheAgent (Such-Pipeline): `novaberg-pixie-research.md`
- DelegationsAgent (Queue-Quelle): `novaberg-pixie-delegation.md`
- Charakter-Profile (Destillation): `novaberg-ei-character-profiles.md`
- Gesprächsvektor (GV-Node): `novaberg-node-gv_k.md`
- Salienz (Bewertung): `novaberg-node-salience.md`
- Pixie-Übersicht: `novaberg-pixie.md`
- Entitäten-Resonanz-Modell: Chat 10 (§3.7)
