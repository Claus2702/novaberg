# Novaberg — Pixie-Agent: WiedervorlageAgent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** WiedervorlageAgent — Fällige Erinnerungen formulieren
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/novaberg-pixie-reminder.md
**Quellen:** nova-05-m-a.md

---

## 1. Aufgabe

Der WiedervorlageAgent scannt das Langzeitgedächtnis nach fälligen Erinnerungen, formuliert sie natürlichsprachlich per LLM und legt das Ergebnis auf den Shadow-Stack. Der Delivery-Service stellt die Erinnerung dem User zu, wenn der emotionale Kontext passt.

**Dateien:** `agents/wiedervorlage/agent.py`, `AGENT.md`

---

## 2. Scheduling

| Aspekt | Detail |
|--------|--------|
| **Priorität** | 0.5 |
| **Intervall** | Alle 12 Stunden |
| **LLM-Call** | 1 CPU-Call pro fälligem Eintrag |
| **context_user** | `user` |

---

## 3. 4-Tabellen-Scan

Der Agent scannt vier PostgreSQL-Tabellen nach fälligen Wiedervorlagen:

| Tabelle | Bedingung |
|---------|-----------|
| `entitaeten` | `wiedervorlage_am <= NOW()` |
| `fakten` | `wiedervorlage_am <= NOW()` |
| `timeline` | `wiedervorlage_am <= NOW()` |
| `notizen` | `wiedervorlage_am <= NOW()` |

---

## 4. LLM-Formulierung

Pro fälligem Treffer formuliert das CPU-Modell eine natürlichsprachliche Erinnerung. Kein starres Template — die Formulierung passt sich dem Inhalt an (Fakt, Ereignis, Entität, Notiz).

---

## 5. Shadow-Stack

Das formulierte Ergebnis geht per `stack_push()` auf den Shadow-Stack. Der Delivery-Service prüft emotionale und modale Kompatibilität, bevor er die Erinnerung dem User zustellt.

---

## 6. Snooze

Nach der Verarbeitung wird die Wiedervorlage um 7 Tage verschoben:

```
wiedervorlage_am += 7 Tage
```

Die Erinnerung kommt nach einer Woche erneut, falls sie nicht zwischenzeitlich anderweitig aufgelöst wurde.

---

## 7. Fehlerbehandlung

Jede Tabelle wird einzeln in `try/except` abgearbeitet. Ein Fehler bei der `fakten`-Tabelle verhindert nicht die Verarbeitung der `notizen`-Tabelle. Robustheit vor Atomarität.

---

## 8. Konfiguration

| Parameter | Wert | Pfad |
|-----------|------|------|
| `PIXIE_WIEDERVORLAGE_PRIORITAET` | 0.5 | `config.py` |
| `PIXIE_WIEDERVORLAGE_INTERVALL_SEKUNDEN` | 43200 (12 h) | `config.py` |
| `PIXIE_WIEDERVORLAGE_SNOOZE_TAGE` | 7 | `config.py` |
| Modell | `mistral-small3.2-cpu` | — |

---

Verwandte Dokumente:
- Pixie-Agenten-Übersicht: `novaberg-pixie.md`
- PromotionAgent (füllt die Tabellen): `novaberg-pixie-promotion.md`
- DecayAgent (deaktiviert alte Einträge): `novaberg-pixie-decay.md`
