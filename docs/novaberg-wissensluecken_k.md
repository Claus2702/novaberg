# Novaberg — Wissenslücken: der Zug zu einem Thema

**Absicht:** Nova führt eine dauerhafte Tabelle von Themen am Rand ihres Wissens — Themen, die sie angehen und die sie noch nicht kennt —, jedes bewertet mit Resonanz, Neuheit und dem Produkt daraus (`neugier_vektor`), gefüllt von einem eigenen Agenten; eine Lücke wird nie gelöscht, nur geschlossen oder ausgeschlossen.
**Stand:** 18. September 2026 (am 19.09.2026 in Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Wissenslücken-Speicher* 🔴 · *WissensluecketAgent* 🔴 · *Neugier (Resonanz, Neuheit, Register)* 🔴 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-wissensluecken_t.md`](novaberg-wissensluecken_t.md) · [`novaberg-wissensluecken_b.md`](novaberg-wissensluecken_b.md) · [`novaberg-wissensluecken_e.md`](novaberg-wissensluecken_e.md) · `_m`: keiner
**Entschieden:** 2 · **Offen beim Meister:** 1 (Liste in [`novaberg-wissensluecken_e.md`](novaberg-wissensluecken_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-wissensluecken_k.md §2` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-wissensluecken_t.md`](novaberg-wissensluecken_t.md), `_b` ist [`novaberg-wissensluecken_b.md`](novaberg-wissensluecken_b.md), `_e` ist [`novaberg-wissensluecken_e.md`](novaberg-wissensluecken_e.md). `_m`: keiner — die Messungen in §5 markieren die widerlegte Aussage an ihrer Stelle und bleiben deshalb in `_t`.

| § | Datei |
|---|---|
| Kasten *„Übergeordnet seit dem 06.08.2026 …“* vor §1 | `_k` |
| 1 | `_k` |
| 2 (mit den Unterabschnitten ohne Nummer: *Erweitern braucht einen Erzeuger*, *Vier Quellen für Stichpunkte*, *Filtern ist der billige Teil*, *Nicht zwanzigmal dasselbe finden*, *Drei Zustände, eine Sperrwirkung*) | `_t` |
| 3 (mit *Das Charakterfeld*) | `_t` |
| 4 | `_t` |
| 5 | `_t`, mit dem Kasten *„Am 12.09.2026 gemessen und widerlegt“* an seiner Stelle |
| 6 | `_b` |
| 7 | `_k` |
| 8 | `_e` (Abschnitt D); die Zeile *Zusammenhang* am Ende von §8 in `_k` |
| Audit (seit 18.09.2026), ohne Nummer | `_t` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Herkunft, Voraussetzung, Abnehmer) | `_e` (Abschnitt F) |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

> **Übergeordnet seit dem 06.08.2026: `novaberg-thinking-erkenntniszyklus_k.md`.** Dieses Dokument beschreibt einen **Bestandteil**; die Folge, in der er ausgelöst wird, besitzt der Zyklus. Insbesondere gilt: **Recherche und Vertiefung werden nicht mehr direkt aus einer Intention ausgelöst**, sondern erst, wenn das Nachdenken über den vorhandenen Bestand eine Lücke gefunden hat. Die Überarbeitung dieses Dokuments auf den Zyklus steht aus.

---

## 1. Welche Neugier hier gemeint ist

Drei Größen hießen bis Chat 111 alle „Neugier". Dieses Dokument baut die dritte:

| | Was sie ist | Stand |
|---|---|---|
| `aufnahmebereitschaft` | ob jetzt der Moment dafür ist — Zustand und Situation | gebaut |
| GV4-Lückensuche | die akute Lücke aus **diesem** Turn, flüchtig | gebaut |
| **`neugier_vektor`** | der Zug zu einem Thema **über den Turn hinaus** | **dieses Dokument** |

**Der Vektor sagt, wohin sie will. Die Bereitschaft sagt, ob jetzt der Moment dafür ist.**

Die GV4-Suche ist turn-gebunden: Sie findet, was gerade nebenan liegt, und vergisst es. Was hier entsteht, überdauert — es liegt in einer Tabelle, wird angereichert, und schließt sich erst, wenn Nova das Thema wirklich kennt.

## 7. Nicht enthalten

**Der Wissensspeicher.** Rechercheergebnisse in Dateien, später über MCP erreichbar, Dokumente und Obsidian-Vault — das ist ein eigenes Subsystem mit eigenem Konzept. Es berührt die Repo-Grenze neu: Der Server erreicht heute ausschließlich `novaberg/`, und Rechercheinhalte sind vom Gespräch abgeleitet. Ein Wissensverzeichnis **muss außerhalb des Git-Roots liegen**, sonst veröffentlicht jeder Commit die gesammelten Inhalte.

**Die Verdrahtung in die Salienz.** `salienz_charakter = max(ziel_grav, emo_grav, neugier_vektor)` folgt, wenn die Lücken stehen.

**Der Traum-Zyklus** aus `thinking-curiosity_k.md` §4 — TR3 bis TR9 bleiben Vision.

*Aus §8 — die übrigen Punkte von §8 stehen in [`novaberg-wissensluecken_e.md`](novaberg-wissensluecken_e.md), Abschnitt D.*

**Zusammenhang:** `novaberg-thinking-curiosity_k.md` (Vision) · `novaberg-salienz-berechnung_k.md` §4 (Abnehmer) · `novaberg-convention-abgeleitete-werte.md` (Bauart) · `novaberg-gv-strategie_k.md` (GV4, die turn-gebundene Schwester)
