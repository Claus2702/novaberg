# Nova — Pixie-Agent: RechercheAgent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** RechercheAgent — Web-Recherche für Pixie
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/nova-pixie-research.md
**Quellen:** nova-05-m-b.md, nova-05-k-b.md

---

## 1. Aufgabe

Der RechercheAgent ist Pixies Web-Recherche-Fähigkeit. Er destilliert den Arbeitskontext aus der Session, beurteilt die Wissenslage, plant Suchqueries, führt Web-Suche + Page-Fetch durch, bewertet die Ergebnisse iterativ, und destilliert einen Fließtext für den User. Das Ergebnis geht auf den Shadow-Stack (Delivery) und in Novas KZG (Langzeit-Wissen).

**Dateien:** `agents/recherche/agent.py`, `lagebeurteilung.py`, `planung.py`, `suche.py`, `bewertung.py`, `destillation.py`, `AGENT.md`

---

## 2. Trigger

Queue-basiert, NICHT periodisch.

| Aspekt | Detail |
|--------|--------|
| **Trigger** | Shadow-Queue (`aufgabe: recherche`) |
| **Intentionen** | recherche_vertiefen, reflexion, gemeinsam_eruieren, information_erfragen |
| **context_user** | `user` (recherchiert fuer den Meister) |
| **identity_user** | `nova` (denkt als Nova) |

---

## 3. Dual-Modell-Routing

Zwei spezialisierte Modelle statt einem:

| Modell | Rolle | Stärke |
|--------|-------|--------|
| **Qwen3-32B** | Analyse (Planung, Bewertung, Klassifikation) | Reasoning, strukturiertes JSON-Output |
| **Mistral Small 3.2 Q5** | Sprache (Destillation, Formulierung) | Deutsch, Fließtext, Charakter-Treue |

**Routing-Prinzip:** Qwen denkt (JSON-Output), Mistral formuliert (Fließtext). Statisch pro Schritt, kein dynamisches Routing.

**CJK-Guard:** Alles was Sprache wird, geht durch Mistral. Qwen3-32B erzeugt gelegentlich chinesische Zeichen — die können den User nicht erreichen, weil die Destillation immer durch Mistral läuft.

```python
def pixie_llm_call(prompt, modus="analyse", temperatur=0.1, json_output=False):
    modell = PIXIE_MODELL_ANALYSE if modus == "analyse" else PIXIE_MODELL_SPRACHE
    return ollama_call(model=modell, prompt=prompt, temperature=temperatur, ...)
```

---

## 4. Workflow (Vollständige Pipeline)

```
Queue-Eintrag (aufgabe: recherche, thema: "...")
    │
    ▼
0. KONTEXT AUFBAUEN [Python]
   session_kontext_extrahieren() via memory/kontext.py
   + LZG-Treffer via Embedding-Suche
   + KZG-Einträge zum Thema
   + Charakter-Hash
   → kontext_paket: dict
    │
    ▼
1. LAGEBEURTEILUNG [Qwen]
   Input: kontext_paket
   Output: vorwissen, luecken, user_mehrwert, ausschluss
    │
    ▼
2. PLANUNG [Qwen]
   Input: Thema + Session-Kontext + Lagebeurteilung
   Output: Recherche-Ziel (1 Satz), 2-4 Queries, Erfolgskriterien
    │
    ▼
3. SUCHE + FETCH [Python]
   Pro Query: web_search_manager.suchen() → Top-URL → page_fetch()
   URL-Blacklist, Domain-Deduplizierung
   Max PIXIE_RECHERCHE_MAX_SEITEN_PRO_RUNDE Fetches pro Runde
    │
    ▼
4. BEWERTUNG [Qwen]
   Input: Ziel + Kriterien + Zwischen-Destillation (~2000 Tokens)
   Output: FERTIG oder LUECKEN (+ neue Queries)
    │
    ├── FERTIG → Destillation
    └── LUECKEN → Zwischen-Destillation → Neue Queries → Schritt 3
        (max PIXIE_RECHERCHE_MAX_ITERATIONEN Runden)
    │
    ▼
5. DESTILLATION [Mistral]
   Input: neue_fakten + lage.user_mehrwert + Charakter-Kontext
   Output: Fließtext 3-8 Sätze (in Novas Stimme)
    │
    ▼
6. ERGEBNIS [Python]
   → stack_push() (Shadow-Stack → Delivery an User)
   → kzg_store(user_id="nova") (Novas Langzeit-Wissen)
```

**LLM-Calls gesamt:** 4-10 Qwen-Calls (Analyse) + 1 Mistral-Call (Sprache) pro Durchlauf.

---

## 5. Zwischen-Destillation (RECH1-Fix)

Max 5000 Zeichen pro Seite mal max 3 Seiten = 15.000 Zeichen pro Suchrunde. Bei 5 Iterationen ohne Komprimierung: 75.000 Zeichen — weit ueber dem CPU-Kontext (32768 Tokens).

**Lösung:** Nach jeder Suchrunde die bisherigen Ergebnisse zu einer Zusammenfassung komprimieren (~500 Zeichen). Die nächste Runde bekommt die Zusammenfassung + die neuen Rohtexte. Token-Verbrauch bleibt konstant pro LLM-Call.

```
Iteration 1: 3 Rohtexte → Zwischen-Destillation → Zusammenfassung (~500 Zeichen)
Iteration 2: Zusammenfassung + 2 neue Rohtexte → Zwischen-Destillation → Zusammenfassung
...
Iteration N: Zusammenfassung + neue Rohtexte → finale Zusammenfassung = Destillat
```

---

## 6. 3 Prüfungen in der Bewertung

Jede Bewertungsrunde prüft drei Kriterien:

1. **Relevanz:** Enthalten die Ergebnisse Information, die UEBER das bekannte Wissen hinausgeht?
2. **Qualität:** Sind die Erfolgskriterien abgedeckt?
3. **Redundanz:** Wäre das Ergebnis für den User nützlich oder nur Wiederholung?

FERTIG wenn mindestens Prüfung 1 UND 2 erfüllt. Im Zweifel: FERTIG — lieber ein gutes Teilergebnis als endlose Iteration.

---

## 7. Konfiguration

| Variable | Default | Beschreibung |
|----------|---------|-------------|
| `PIXIE_RECHERCHE_MAX_ITERATIONEN` | 3 | Max Such-Iterationen |
| `PIXIE_RECHERCHE_MAX_QUERIES` | 4 | Max Queries pro Planungsschritt |
| `PIXIE_RECHERCHE_SESSION_TURNS` | 10 | Turns für Kontext-Extraktion |
| `PIXIE_RECHERCHE_MAX_SEITEN_PRO_RUNDE` | 3 | Max Page-Fetches pro Suchrunde |
| `PAGE_FETCH_TIMEOUT` | 10.0 | HTTP-Timeout für Page-Fetch |
| `PAGE_FETCH_MAX_CHARS` | 5000 | Max Zeichen pro Seite |
| `PIXIE_MODELL_ANALYSE` | `qwen3-32b-cpu` | Reasoning/JSON-Output |
| `PIXIE_MODELL_SPRACHE` | `mistral-small3.2-cpu` | Fließtext/Deutsch |

**Genutzte Infrastruktur:**

| Komponente | Pfad |
|-----------|------|
| Session-Kontext | `memory/kontext.py` |
| Web-Suche | `tools/web/search.py` (SearXNG) |
| Page-Fetch | `tools/web/fetch.py` (trafilatura + BS4-Fallback) |
| Shadow-Stack | `services/pixie/stack.py` |
| KZG | `memory/kzg.py` |

---

Verwandte Dokumente:
- VertiefungsAgent (Konzept): `nova-pixie-deepdive_k.md`
- Pixie-Agenten-Übersicht: `nova-pixie.md`
- KZG-Agent (Shadow-Queue-Quelle): `nova-pixie-kzg.md`
- DelegationsAgent (Queue-Quelle): `nova-pixie-delegation.md`
