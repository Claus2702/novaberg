# WiedervorlageAgent

Prüft fällige Wiedervorlagen über 4 Tabellen und erstellt Erinnerungen auf dem Shadow-Stack.

## Trigger
- Periodisch (alle 12h), Prio 0.5

## Ablauf
1. Scan: entitaeten, fakten, timeline, notizen — WHERE wiedervorlage_am <= now()
2. Pro Treffer: LLM formuliert Erinnerung (CPU-Modell)
3. Erinnerung → Shadow-Stack (stack_push)
4. Wiedervorlage um 7 Tage verschoben (Snooze)

## Besonderheiten
- Nur für user_id des Meisters (context_user = "user")
- Jede Tabelle einzeln in try/except (Fehlertoleranz)
- Snooze-Dauer konfigurierbar (PIXIE_WIEDERVORLAGE_SNOOZE_TAGE)
