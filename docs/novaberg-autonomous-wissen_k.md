# Novaberg — Autonomes Wissen (Konzept)

**Absicht:** Was Nova selbst erarbeitet — durch Recherche, Vertiefung, Klärfrage oder Traum —, bleibt je Paar als Wissens- und Berichtsdatei mit Metadaten erhalten, ist später wieder abrufbar, wird bei Wiederkehr verstärkt statt verdoppelt und verfällt wie das Langzeitgedächtnis, statt gelöscht zu werden.
**Stand:** 18. September 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Wissensspeicher / Bibliothek* 🟠 · *Bibliothek als bestellbarer Dienst* 🟢 · *Retrieval der Bibliothek — ein Vektor je Thema* 🔴 · *Bibliothek — drei Kanäle* 🔴 · *WissenManager* 🟠 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-autonomous-wissen_t.md`](novaberg-autonomous-wissen_t.md) · [`novaberg-autonomous-wissen_b.md`](novaberg-autonomous-wissen_b.md) · [`novaberg-autonomous-wissen_e.md`](novaberg-autonomous-wissen_e.md) · [`novaberg-autonomous-wissen_m.md`](novaberg-autonomous-wissen_m.md)
**Entschieden:** 2 · **Offen beim Meister:** 0 (Liste in [`novaberg-autonomous-wissen_e.md`](novaberg-autonomous-wissen_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-autonomous-wissen_k.md §11.6` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-autonomous-wissen_t.md`](novaberg-autonomous-wissen_t.md), `_b` ist [`novaberg-autonomous-wissen_b.md`](novaberg-autonomous-wissen_b.md), `_e` ist [`novaberg-autonomous-wissen_e.md`](novaberg-autonomous-wissen_e.md), `_m` ist [`novaberg-autonomous-wissen_m.md`](novaberg-autonomous-wissen_m.md).

| § | Datei |
|---|---|
| die beiden Vorrang-Hinweise unter dem bisherigen Kopf (§11 und der Erkenntniszyklus) | `_k`, unter dieser Tabelle |
| 1 | `_k` |
| 2 · 2.1 · 2.2 · 2.3 | `_t` |
| 3 | `_t` |
| 4 | `_t` |
| 5 · 5.1 · 5.2 | `_t` |
| 6 · 6.1 · 6.2 · 6.3 · 6.4 | `_t` |
| 7 · 7.1 · 7.2 · 7.3 · 7.4 · 7.5 | `_t` |
| 7.3a | `_t` (mit Hinweis); der `[gemessen]`-Kasten aus *Der vierte Ausgang ist hier der eigentliche Zugewinn* in `_m` |
| 8 | `_t` |
| 9 | `_b` |
| 10 | `_k` |
| Verwandte Dokumente (ohne Nummer, nach §10) | `_k` |
| 11 · 11.1 · 11.2 · 11.3 · 11.4 · 11.5 · 11.7 | `_t` |
| 11.6 | `_t` (mit Hinweis); die Bauberichte *Gebaut am 04.08.2026*, *`WIS-3` gebaut am 04.08.2026*, der Kasten *Ein gescheiterter Durchlauf hinterlässt einen Bericht* und *Was damit noch nicht gebaut ist* in `_b` |
| 11.8 | `_e` (Abschnitt D) |
| Audit (seit 18.09.2026) | `_b` |
| Versionshistorie | `_e` (Abschnitt F) |
| Befunde aus dem Betrieb — nachgetragen am 20.08.2026 | `_m` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Status, Quellen, Verwandt) | `_e` (Abschnitt F) |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

> **§11 ist gegenueber §1 bis §10 vorrangig.**

> **Übergeordnet seit dem 06.08.2026: `novaberg-thinking-erkenntniszyklus_k.md`.** Dieses Dokument beschreibt einen **Bestandteil**; die Folge, in der er ausgelöst wird, besitzt der Zyklus. Insbesondere gilt: **Recherche und Vertiefung werden nicht mehr direkt aus einer Intention ausgelöst**, sondern erst, wenn das Nachdenken über den vorhandenen Bestand eine Lücke gefunden hat. Die Überarbeitung dieses Dokuments auf den Zyklus steht aus.
 Die frueheren Abschnitte beschreiben den Entwurf vom April; wo sie ihm widersprechen, gilt §11. Sie bleiben stehen, weil sie die Begruendungen tragen, die weiterhin gelten.

---

## 1. Aufgabe

RechercheAgent, VertiefungsAgent und Traum-Modus produzieren Wissen. Aktuell geht dieses Wissen auf den Shadow-Stack (Delivery, vergaenglich) und ins KZG (Decay, vergaenglich). Das erarbeitete Wissen verschwindet.

Das `autonomous/`-Verzeichnis ist Novas persistenter Wissensspeicher. Jeder Durchlauf erzeugt bis zu zwei Dateien: eine **Wissen-Datei** (das Was) und eine **Bericht-Datei** (das Wie). Beide sind ueber RAG (Embedding + pgvector) fuer den Enricher abrufbar.

> **Nachgetragen am 04.08.2026:** Es sind **drei** Quellen, nicht zwei — Recherche schoepft aus der Welt, Vertiefung aus dem eigenen Bestand, **die Klaerfrage aus dem Gegenueber**. Siehe §11.3. *(Der Modus hiess hier bis zum 05.08.2026 `nachfragen`; der Name war doppelt vergeben und ist getrennt — §11.3.)*

---

## 10. Referenzen und Quellen

| Quelle | Relevanz | Fundort |
|--------|----------|---------|
| **autoresearch** (Karpathy, 2026) | Keep/Discard/Crash-Status, Experiment-Log, NEVER-STOP-Loop | github.com/karpathy/autoresearch |
| **Claude Code autoDream** | 4-Phasen-Zyklus (Orient/Gather/Consolidate/Prune), INDEX unter 200 Zeilen | github.com/Piebald-AI/claude-code-system-prompts |
| **Sleep-time Compute** (UC Berkeley / Letta) | Idle-Time-Vorberechnung spart 5x Test-Time-Compute, 18% Genauigkeitsgewinn | arXiv:2504.13171 |
| **Letta/MemGPT** | Paradigma "LLM verwaltet eigenes Gedaechtnis", Core/Archival Memory | github.com/letta-ai/letta |
| **dream-skill** (Community-Reimplementierung) | Open-Source-Nachbau von autoDream mit Stop-Hook | github.com/grandamenium/dream-skill |
| **Claude Code autoDream Guide** | Praxisbericht, 913 Sessions in 9 Minuten konsolidiert | claudefa.st/blog/guide/mechanics/auto-dream |
| **zenvanriel AutoDream Guide** | Detaillierte Analyse der 4 Phasen | zenvanriel.com/ai-engineer-blog/claude-code-autodream-memory-consolidation-guide/ |

---

Verwandte Dokumente:
- Datei-Operationen: `novaberg-tool-dateien_k.md`
- Pixie-Plugin-Architektur: `novaberg-pixie-plugin_k.md`
- RechercheAgent: `novaberg-pixie-research.md`
- VertiefungsAgent: `novaberg-pixie-deepdive_k.md`
- Neugier / Traum-Modus: `novaberg-thinking-curiosity_k.md`
- Drive-System: `novaberg-thinking-drive_k.md`
- Web-Infrastruktur: `novaberg-tool-web.md`
