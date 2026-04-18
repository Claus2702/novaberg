# RechercheAgent

**Typ:** Workflow (queue-basiert)
**Graph:** Pixie
**Trigger:** Shadow-Queue (`aufgabe: recherche`)
**context_user:** user
**identity_user:** nova

## Aufgabe

Breiter Überblick zu einem Thema im Arbeitskontext des Users.
Iterative Web-Suche mit Qualitätssicherung.

## Ablauf

1. Session-Kontext destillieren (`memory/kontext.py`)
2. Planung: Ziel + Queries + Kriterien (LLM)
3. Web-Suche + Page-Fetch (`tools/web/`)
4. Bewertung: Fertig oder Lücken? (LLM)
5. Bei Lücken: Neue Queries → Schritt 3 (max 2 Iterationen)
6. Destillation: Fließtext 3-8 Sätze (LLM)
7. Ergebnis → Shadow-Stack + Novas KZG

## LLM-Calls

- Kontext-Extraktion: 1 (CPU, in memory/kontext.py)
- Planung: 1 (CPU)
- Bewertung: 1 pro Iteration (CPU)
- Destillation: 1 (CPU)
- Gesamt: 4-6 Calls (CPU-Modell)

## Config

| Variable | Default | Beschreibung |
|----------|---------|-------------|
| PIXIE_RECHERCHE_MAX_ITERATIONEN | 2 | Max Such-Iterationen |
| PIXIE_RECHERCHE_MAX_QUERIES | 4 | Max Queries pro Planung |
| PIXIE_RECHERCHE_SESSION_TURNS | 10 | Turns für Kontext-Extraktion |
| PIXIE_RECHERCHE_MAX_SEITEN_PRO_RUNDE | 3 | Max Fetches pro Runde |
