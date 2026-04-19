# Novaberg — Pixie-Agent: DecayAgent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** DecayAgent — Ebbinghaus-Vergessenskurve
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/novaberg-pixie-decay.md
**Quellen:** nova-05-m-a.md, nova-02-t-a.md

---

## 1. Aufgabe

Der DecayAgent implementiert die Ebbinghaus-Vergessenskurve für das Langzeitgedächtnis. Vergessen ist kein Defekt, sondern ein aktiver Filterprozess, der das Signal-Rausch-Verhältnis verbessert. Der Agent berechnet effektive Gewichte, deaktiviert verblasste Einträge und ermöglicht Verstärkung durch Wiederholung.

**Dateien:** `agents/decay/agent.py`, `AGENT.md`

---

## 2. Scheduling

| Aspekt | Detail |
|--------|--------|
| **Priorität** | `PIXIE_DECAY_PRIORITAET = 0.2` (`config.py`) |
| **Intervall** | `PIXIE_DECAY_INTERVALL_SEKUNDEN = 86400` = 24 Stunden (`config.py`) |
| **LLM-Call** | Keiner — reines Python/SQL |
| **context_user** | `user` + `nova` (kein user_id-Filter) |

---

## 3. Decay-Formel

```
effektives_gewicht = gewicht * e^(-lambda * tage)
```

| Symbol | Bedeutung | Quelle |
|--------|-----------|--------|
| `gewicht` | Kumuliertes Basis-Gewicht (steigt bei Verstärkung, wird nie reduziert) | `langzeitgedaechtnis.gewicht` |
| `lambda` | Decay-Rate | `config.py: EBBINGHAUS_DECAY_RATE` (0.0015) |
| `tage` | Tage seit letzter Verstärkung | Berechnet aus `verstaerkt_am` |

Das effektive Gewicht wird nie gespeichert. Es wird bei jedem Zugriff live berechnet. Das gespeicherte `gewicht` dokumentiert die Verstärkungshistorie.

---

## 4. Decay-Tabelle

0.0015 ist bewusst langsam — ein persönlicher Assistent soll nicht zu schnell vergessen.

| Zeitraum | Decay-Faktor | Effekt auf Gewicht 0.80 |
|----------|-------------|------------------------|
| 1 Woche | 0.99 | 0.79 — kaum spürbar |
| 1 Monat | 0.96 | 0.77 |
| 6 Monate | 0.76 | 0.61 |
| 1 Jahr | 0.58 | 0.46 |
| 2 Jahre | 0.33 | 0.27 |
| 3 Jahre | 0.19 | 0.15 |

Einmalig Erwähntes hält etwa 3 Jahre, bevor es unter den Schwellwert fällt. Häufig Besprochenes (Gewicht 4.80 nach 10 Verstärkungen) hält praktisch ewig.

---

## 5. Soft-Delete

Einträge mit effektivem Gewicht unter `EBBINGHAUS_MIN_GEWICHT` (0.1) werden auf `aktiv = FALSE` gesetzt. Keine Löschung — Soft-Delete.

Ablauf:
1. Alle aktiven LZG-Einträge laden (beide User)
2. Effektives Gewicht für jeden berechnen
3. Unter 0.1 → `aktiv = FALSE`
4. Batch-UPDATE mit `WHERE id = ANY(...)`

Ein Partial Index (`WHERE aktiv = TRUE`) beschleunigt alle Abfragen — inaktive Einträge verursachen keinen Overhead.

**Reaktivierung:** Ein inaktiver Eintrag kann durch erneute Erwähnung reaktiviert werden. Pixie setzt bei Promotion eines semantisch ähnlichen inaktiven Eintrags `aktiv = TRUE` und verstärkt das Gewicht.

---

## 6. Verstärkung

Bei Wiederholung (Cosine Similarity >= 0.85 im KZG):

```
neues_gewicht = altes_gewicht + (aktuelle_salienz / VERSTAERKUNG_DIVISOR)
```

Im LZG bei erneuter Erwähnung via Promotion:

```sql
UPDATE langzeitgedaechtnis
SET gewicht = gewicht + verstaerkung,
    verstaerkt_am = NOW()
WHERE id = ...
```

`verstaerkt_am = NOW()` setzt den Decay-Timer zurück. Ein Eintrag, der nach 2 Jahren Inaktivität wieder angesprochen wird, behält sein volles kumuliertes Gewicht und beginnt den Decay von vorne.

**Balance-Tabelle:**

| Szenario | Gewicht | Nach 1 Jahr | Nach 3 Jahren |
|----------|---------|-------------|---------------|
| Einmalig erwähnt | 0.80 | 0.46 | 0.15 |
| 3x verstärkt | 2.00 | 1.16 | 0.38 |
| 10x verstärkt | 4.80 | 2.78 | 0.91 |
| Kern-Interesse (20x) | 8.80 | 5.10 | 1.67 |

---

## 7. Beide User

Der DecayAgent verarbeitet Einträge beider User (`meister` und `nova`) ohne Filter. Kein `WHERE user_id = ...` — alle aktiven LZG-Einträge werden gleichbehandelt.

---

## 8. Kein LLM

Reines Python/SQL. Die Formel ist deterministisch — ein LLM, das gebeten wird `e^(-0.0015 * 180)` zu berechnen, macht gelegentlich Fehler. Python nie. Grundprinzip: Alles was berechenbar ist, wird berechnet.

---

## 9. Konfiguration

| Parameter | Default | Beschreibung |
|-----------|---------|-------------|
| `EBBINGHAUS_DECAY_RATE` | 0.0015 | Lambda — Decay-Rate. Höher = schnelleres Vergessen. |
| `EBBINGHAUS_MIN_GEWICHT` | 0.1 | Schwellwert für Inaktivierung (Soft-Delete). |
| `KZG_VERSTAERKUNG_DIVISOR` | 2.0 | Verstärkungs-Stärke. Niedriger = stärkere Verstärkung. |

---

Verwandte Dokumente:
- PromotionAgent (Verstärkungs-Quelle): `novaberg-pixie-promotion.md`
- CharakterAgent (nutzt gewichtete Einträge): `novaberg-pixie-character-hash.md`
- KZG-Agent (KZG-Verstärkung): `novaberg-pixie-kzg.md`
- Pixie-Agenten-Übersicht: `novaberg-pixie.md`
