# Novaberg — Pixie-Agent: VertiefungsAgent (Konzept)

**Absicht:** Ein VertiefungsAgent füllt gezielt tiefe Lücken in Novas vorhandenem Wissen — tief statt breit — und liefert nur, was sie noch nicht wusste; ausgelöst wird er, wenn das Nachdenken über den Bestand eine Lücke gefunden hat.
**Stand:** 6. August 2026 (am 19.09.2026 in Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *VertiefungsAgent* ⚫ · *Vertiefung (aus dem eigenen Bestand)* 🔴 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-pixie-deepdive_t.md`](novaberg-pixie-deepdive_t.md) · `_b`: keiner · [`novaberg-pixie-deepdive_e.md`](novaberg-pixie-deepdive_e.md) · `_m`: keiner
**Entschieden:** 0 · **Offen beim Meister:** 0 (Liste in [`novaberg-pixie-deepdive_e.md`](novaberg-pixie-deepdive_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-pixie-deepdive_k.md §2` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-pixie-deepdive_t.md`](novaberg-pixie-deepdive_t.md), `_e` ist [`novaberg-pixie-deepdive_e.md`](novaberg-pixie-deepdive_e.md). `_b`: keiner, `_m`: keiner.

| § | Datei |
|---|---|
| Kasten *„Übergeordnet seit dem 06.08.2026 …“* vor §1 | `_k` |
| Kasten *„Bestätigt am 06.08.2026 …“* / *„Nicht baubar, solange …“* vor §1 | `_e` (Abschnitt D) |
| 1 | `_k` |
| 2 | `_t` |
| 3 | `_k` |
| 4 | `_t` |
| Verwandte Dokumente, ohne Nummer | `_k` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Quellen) | `_e` (Abschnitt F) |
| Entschieden, Offen beim Meister, überholte Fassungen, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

> **Übergeordnet seit dem 06.08.2026: `novaberg-thinking-erkenntniszyklus_k.md`.** Dieses Dokument beschreibt einen **Bestandteil**; die Folge, in der er ausgelöst wird, besitzt der Zyklus. Insbesondere gilt: **Recherche und Vertiefung werden nicht mehr direkt aus einer Intention ausgelöst**, sondern erst, wenn das Nachdenken über den vorhandenen Bestand eine Lücke gefunden hat. Die Überarbeitung dieses Dokuments auf den Zyklus steht aus.

---

## 1. Aufgabe

Der VertiefungsAgent vertieft bestehendes Wissen basierend auf KZG-Einträgen. Während der RechercheAgent breite Überblicke verschafft, füllt der VertiefungsAgent spezifische Lücken in Novas vorhandenem Wissen — tief, nicht breit.

---

## 3. Abgrenzung zum RechercheAgent

| Aspekt | RechercheAgent | VertiefungsAgent |
|--------|---------------|-----------------|
| **Ziel** | Breiter Überblick | Lücken in Novas Wissen füllen |
| **Kontext** | Session + Queue | Session + Queue + **LZG/KZG-Vorwissen (gewichtet)** |
| **Lagebeurteilung** | "Was weiß Nova? Was fehlt?" | "Was weiß Nova GUT? Wo sind TIEFE Lücken?" |
| **Planung** | "Verschaffe Überblick — verschiedene Facetten" | "Fülle spezifische Lücken — tief, nicht breit" |
| **Bewertung** | 3 Prüfungen (Standard) | 3 Prüfungen + **Prüfung 4: Tiefe** |
| **Destillation** | "Das Wichtigste zum Thema" | "Nur das Neue, was Nova noch nicht wusste" |

**Vertiefung = bestehendes Wissen vertiefen. Recherche = neues Wissen suchen.**

---

Verwandte Dokumente:
- RechercheAgent (Shared Infrastruktur): `novaberg-pixie-research.md`
- KZG-Agent (Queue-Quelle): `novaberg-pixie-kzg.md`
- Pixie-Agenten-Übersicht: `novaberg-pixie.md`
