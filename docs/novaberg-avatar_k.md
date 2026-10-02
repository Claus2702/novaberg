# Novaberg — Emotions-Avatar (Konzept)

**Absicht:** Ein 2D-Avatar im GTK4-Client zeigt Novas eigenen Emotionszustand als lebende Bleistiftskizze; er stellt dar, was die Emotionsberechnung liefert, und entscheidet selbst nichts.
**Stand:** 02.10.2026
**Umsetzung:** keine Featurezeile — sie entsteht, wenn Novaberg das Feature bekommt (Entscheidung vom 02.10.2026, `novaberg-avatar_e.md`). Im Client ist nichts gebaut; ein HTML-Prototyp liegt unter `labor/avatar/` (§13).
**Teile:** `novaberg-avatar_t.md` · `novaberg-avatar_b.md` · `novaberg-avatar_e.md` · `novaberg-avatar_m.md`
**Grundlagen:** `novaberg-ei-plutchik.md`, `novaberg-ei-dual-emotion_k.md`
**Entschieden:** 5 · **Offen beim Meister:** 6 (Liste in `novaberg-avatar_e.md`)

> Alle Bezeichner für **neue** Bausteine (Klassen, Felder, Funktionen) sind **Vorschläge**.
> Aussagen über das **bestehende** System stammen aus den oben genannten Dokumenten,
> nicht aus dem Code. Sie gelten als Doku-Stand, bis ein Audit sie belegt (Abschnitt 11).

---

## § → Datei

| § | Abschnitt | Datei |
|---|---|---|
| 1, 2 | Ziel, Leitprinzip | `novaberg-avatar_k.md` |
| 3–9 | Darstellungsstil, Parameterraum, Emotions-Mapping, Intensität und Mischung, Übergangsmodell, Schichtenmodell, Integration im GTK4-Client | `novaberg-avatar_t.md` |
| 10 | Testbarkeit | `novaberg-avatar_b.md` |
| 11, 12 | Offene Punkte, Annahmen | `novaberg-avatar_e.md` |
| 13 (Einleitung), 13.1, 13.3, 13.9, 13.12–13.14 | Figur aus Vorlage: Pipeline, Alternative, bewegliches Kinn, Sprechschicht, Muskelkanäle, Einzellaute | `novaberg-avatar_t.md` |
| 13.8, 13.10, 13.11 | Feinabstimmung des Prototyps nach Sichtprüfung | `novaberg-avatar_b.md` |
| 13.2, 13.4–13.7, 13.15, 13.16 | Befunde und Messungen | `novaberg-avatar_m.md` |
| — | Änderungen der Fassungen 0.1 bis 0.5, Entscheidungen, Befunde der Aufteilung | `novaberg-avatar_e.md` |

---

## 1. Ziel

Ein 2D-Avatar im GTK4-Client, der **Novas** aktuellen Emotionszustand sichtbar macht.

- Stil: Bleistiftskizze, bewusst stilisiert, kein Fotorealismus.
- Dauerhaft animiert: Das Bild „lebt“ auch ohne Zustandsänderung.
- Emotionswechsel laufen als flüssiger Übergang in etwa 1 Sekunde,
  von jedem Zustand zu jedem anderen, auch mitten in einem laufenden Übergang.

**Nicht Ziel (v1):** Fotorealismus, 3D, generative Bild- oder Videomodelle,
eigenständige Interpretation von Emotionen durch den Avatar, Darstellung der
User-Emotion (das bleibt Aufgabe des Emotions-Radars).

---

## 2. Leitprinzip: Der Avatar ist ein reiner Renderer

Analog zu „LLM als Sprach-Renderer“: Der Avatar entscheidet nichts.

- Die Emotion wird deterministisch in Python berechnet (EI-Calc, Rolle `character`).
- Der Avatar erhält einen **Ziel-Emotionszustand** und stellt ihn dar.
- Der Avatar kennt keine Gesprächsinhalte, leitet keine Emotionen ab und
  normalisiert nicht erneut.

| Baustein | Verantwortung | Kennt Emotionen? |
|---|---|---|
| Mapping | Emotionszustand → Gesichtsparameter | ja |
| Animator | Übergang zwischen Gesichtsparametern über die Zeit | nein |
| Renderer | Gesichtsparameter → Zeichnung in einem Rechteck | nein |

---
