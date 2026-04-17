# 02_L_d — Lesson: Doppelspeicherung Salienz + Planner

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Zwei Systeme schreiben gleichzeitig
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/nova-node-dispatcher_l.md
**Ursprung:** nova-02-l-d.md
**Typ:** Lesson (L)
**Entdeckt:** Chat 11 (24. März 2026), P5 + P6
**Betrifft:** Salienz (`01_M_g`), Planner (`01_M_d`), Dispatcher (`01_M_h`)

---

## 1. Symptom

Zwei Varianten des gleichen Problems:

**P5 — Doppelte Notiz + Fakt:** „Merk dir: Einkaufsliste — Milch, Eier, Brot" → Der Planner legte eine Notiz an (korrekt). Die Salienz extrahierte zusätzlich den Fakt `ICH EINKAUFSLISTE Milch, Eier, Brot` und schrieb ihn in die Fakten-Tabelle (unerwünscht). Ergebnis: Dieselbe Information existierte als Notiz und als Fakt.

**P6 — Doppelter Termin:** „Trag ein: Zahnarzt am Donnerstag um 14 Uhr" → Der Planner legte den Termin an (14:00 MEZ). Die Salienz erkannte `temporal_fact` und legte einen zweiten Termin an (13:00 UTC — da die Timezone-Konvertierung im Salienz-Pfad noch nicht gefixt war). Ergebnis: Zwei Zahnarzttermine.

---

## 2. Ursache: Zwei unabhängige Schreibsysteme

Der Graph hat zwei Quellen für `pending_writes`:

1. **Planner** — bei Management-Aktionen (explizite Befehle: „merk dir", „trag ein")
2. **Salienz** — bei speicherwürdigem Content (implizite Erkennung: Fakten, Termine)

Beide laufen im selben Turn. Beide erkennen dieselben Informationen. Beide schreiben `pending_writes`. Der Dispatcher führt alle aus — ohne zu wissen, dass sie sich überlappen.

```
"Trag ein: Zahnarzt am Donnerstag"
    │
    ├── Planner: management_action="create" → pending_write (timeline)
    │
    └── Salienz: temporal_fact erkannt → pending_write (timeline)
    
    → Dispatcher führt beide aus → 2 Termine
```

---

## 3. Warum wir es nicht vorhergesehen haben

Die Entscheider/Arbeiter-Trennung (A1) war korrekt — Salienz entscheidet, Dispatcher führt aus. Aber die Trennung berücksichtigte nicht, dass es *zwei* Entscheider gibt: Planner und Salienz. Beide haben die gleiche Berechtigung, `pending_writes` zu erzeugen. Die Architektur hatte keine Regel, wer Vorrang hat.

---

## 4. Die Lösung: Salienz-Guard

Ein einfacher Guard in der Salienz:

```python
planner_aktiv = bool(state.get("management_action", ""))

if facts and planner_aktiv:
    logger.info("Salienz: Fakten erkannt, aber Planner aktiv — übersprungen")
    
if temporal_fact and planner_aktiv:
    logger.info("Salienz: Temporaler Fakt erkannt, aber Planner aktiv — übersprungen")
```

**Wenn der Planner im selben Turn aktiv war, unterdrückt die Salienz ihre Fakten- und Timeline-Writes.** Der Planner hat die Daten bereits verarbeitet — über den strukturierten Management-Pfad (Router → Planner → Manager), nicht über den impliziten Salienz-Pfad.

**KZG-Writes bleiben aktiv.** Die Salienz darf weiterhin ins KZG schreiben — das ist ein anderer Zweck (Gesprächskontext vs. strukturierte Daten). Doppelte KZG-Einträge werden über die Ähnlichkeitssuche (Cosine ≥ 0.85) abgefangen.

---

## 5. Generalisierbare Erkenntnis

> **Das Dual-Writer-Problem:** Wenn zwei unabhängige Komponenten die gleiche Information erkennen und in den gleichen Speicher schreiben können, entsteht unweigerlich Duplikation — es sei denn, eine explizite Vorrang-Regel existiert.

Die Regel ist simpel: **Explizit schlägt implizit.** Der Planner (explizite Management-Aktion) hat Vorrang vor der Salienz (implizite Erkennung). Wenn der Nutzer sagt „Merk dir X", will er den Management-Pfad — nicht dass beide Pfade gleichzeitig feuern.

> **Für zukünftige Manager:** Jeder neue Manager, der sowohl über den Planner (explizit) als auch über die Salienz (implizit) beschrieben werden kann, braucht denselben Guard. Das ist kein Bug-Fix — das ist ein Architektur-Pattern.

---

→ Salienz (Guard implementiert): `01_M_g`
→ Planner: `01_M_d`
→ Dispatcher: `01_M_h`
→ Entscheider/Arbeiter-Trennung: `00_A`, Abschnitt 6
