# Novaberg — Pixie-Agent: RechercheAgent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** RechercheAgent — Web-Recherche für Pixie
**Stand:** 16. August 2026 (die Zwischen-Destillation traegt eine eigene Frist — §7; drei Angaben in §5 sind gemessen widerlegt und durchgestrichen statt entfernt. Zuvor: 19. April 2026, Chat 57 — Modell-Alignment auf aktiven Connector)
**Pfad:** novaberg/docs/novaberg-pixie-research.md
**Quellen:** nova-05-m-b.md, nova-05-k-b.md


> **Übergeordnet seit dem 06.08.2026: `novaberg-thinking-erkenntniszyklus_k.md`.** Dieses Dokument beschreibt einen **Bestandteil**; die Folge, in der er ausgelöst wird, besitzt der Zyklus. Insbesondere gilt: **Recherche und Vertiefung werden nicht mehr direkt aus einer Intention ausgelöst**, sondern erst, wenn das Nachdenken über den vorhandenen Bestand eine Lücke gefunden hat. Die Überarbeitung dieses Dokuments auf den Zyklus steht aus.

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

Zwei spezialisierte Modelle statt einem (aktiver Connector: `gemma4`):

| Modell | Rolle | Stärke |
|--------|-------|--------|
| **Qwen3-32B** (`PIXIE_ANALYSE_MODEL`) | Analyse (Planung, Bewertung, Klassifikation) | Reasoning, strukturiertes JSON-Output |
| **Gemma 4** (`SHADOW_MODEL`) | Sprache (Destillation, Formulierung) | Deutsch, Fließtext, Charakter-Treue |

**Routing-Prinzip:** Qwen denkt (JSON-Output), das Sprach-Modell formuliert (Fließtext). Statisch pro Schritt, kein dynamisches Routing. Bei Connector `mistral` ist `SHADOW_MODEL = mistral-small3.2-cpu` — die Rolle bleibt identisch.

**CJK-Guard:** Alles was Sprache wird, geht durch das Sprach-Modell. Qwen3-32B erzeugt gelegentlich chinesische Zeichen — die können den User nicht erreichen, weil die Destillation immer über `SHADOW_MODEL` läuft.

```python
def pixie_llm_call(prompt, modus="analyse", temperatur=0.1, json_output=False):
    modell = PIXIE_ANALYSE_MODEL if modus == "analyse" else SHADOW_MODEL
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
5. DESTILLATION [SHADOW_MODEL — aktiv: Gemma 4]
   Input: neue_fakten + lage.user_mehrwert + Charakter-Kontext
   Output: Fließtext 3-8 Sätze (in Novas Stimme)
    │
    ▼
6. ERGEBNIS [Python]
   → stack_push() (Shadow-Stack → Delivery an User)
   → kzg_store(user_id="nova", turn_id=<ausloeser des Auftrags>) (Novas Langzeit-Wissen)
     Die Kennung wandert mit: Der Eintrag entsteht aus diesem Auftrag, der Auftrag
     aus jenem Turn — erstes Glied der Sachlage-Bruecke (seit 30.08.2026).
```

**LLM-Calls gesamt:** 4-10 Qwen-Calls (Analyse) + 1 Sprach-Call (`SHADOW_MODEL`) pro Durchlauf.

---

## 5. Zwischen-Destillation (RECH1-Fix)

Max 5000 Zeichen pro Seite mal max 3 Seiten = 15.000 Zeichen pro Suchrunde. Bei 5 Iterationen ohne Komprimierung: 75.000 Zeichen — ~~weit ueber dem CPU-Kontext (32768 Tokens)~~.

**Lösung:** Nach jeder Suchrunde die bisherigen Ergebnisse zu einer Zusammenfassung komprimieren (~~~500 Zeichen~~). Die nächste Runde bekommt die Zusammenfassung + die neuen Rohtexte. ~~Token-Verbrauch bleibt konstant pro LLM-Call.~~

```
Iteration 1: 3 Rohtexte → Zwischen-Destillation → Zusammenfassung
Iteration 2: Zusammenfassung + 2 neue Rohtexte → Zwischen-Destillation → Zusammenfassung
...
Iteration N: Zusammenfassung + neue Rohtexte → finale Zusammenfassung = Destillat
```

> **Drei Angaben dieses Abschnitts sind gemessen widerlegt (16.08.2026).** Sie sind durchgestrichen statt entfernt, weil die Bauart auf ihnen steht.
>
> **Die Grenze.** Der Hintergrundpfad liest mit **262144** Token, nicht mit 32768. Die 75.000 Zeichen liegen damit bei rund einem Zehntel des Fensters statt darueber — der Schritt komprimiert verlustbehaftet gegen eine Grenze, die achtmal weiter weg ist als angenommen. Gefuehrt als `RECHERCHE-ZWISCHENDESTILLATION-OHNE-GRUND`, und die dort gestellte Frage steht weiter offen: **faellt der Schritt weg, oder steht seine Begruendung neu?**
>
> **Die Laenge.** Ueber 164 Laeufe in 24 h: Minimum **2161** Zeichen, Median **4122**, Maximum **9328**. **Kein einziger** lag unter 800. Der Prompt bittet um hoechstens 2000 Token und uebergab bis zum 16.08.2026 **kein `max_output_tokens`** — `num_predict` blieb ungesetzt, die Ausgabe unbegrenzt. Ein Prompt bittet; ein Parameter haelt.
>
> **Der konstante Verbrauch.** Er ist nicht konstant. Ausgabe-Token je Aufruf: Median **1330**, p90 **2425**, Maximum **4176**.
>
> **Was daraus folgte.** Bei den gemessenen ~7,3 Token/s auf dem CPU-Backend dauert der Aufruf im Median **181 s**, p90 **314 s**, maximal **638 s** — gegen eine Frist von 300 s, die der Aufruf nicht selbst nannte und deshalb vom Worker erbte. **24 von 190 Antworten (12 %) trafen nach dem Fristablauf ein**: Das Modell hatte geantwortet, der Aufrufer hatte aufgegeben. Seit dem 16.08.2026 traegt die Aufrufstelle ihre eigene Frist, siehe §7.

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
| `PIXIE_ANALYSE_MODEL` | `qwen3-32b-cpu` | Reasoning/JSON-Output (über alle Connectors gleich) |
| `SHADOW_MODEL` | `gemma4-cpu` (Connector `gemma4`, Default) bzw. `mistral-small3.2-cpu` (Connector `mistral`) | Fließtext/Deutsch |

### Die Frist der Zwischen-Destillation (16.08.2026)

**Zehn Aufrufstellen des Agenten rufen das Hintergrundmodell, und genau eine braucht eine eigene Frist.** Die uebrigen neun liegen bei hoechstens 89 s und sind mit dem Vorgabewert `MODEL_BACKGROUND_TIMEOUT_S = 300` bequem versorgt; `recherche/zwischen` liegt im Median bei 181 s und riss die Frist regelmaessig. Sie steht deshalb an der Aufrufstelle und nicht am Worker — derselbe Grund wie bei den Sampling-Parametern (`F-SAMPLING-1`): Der Vorgabewert gilt fuer **jeden** Hintergrund-Aufrufer.

| Schlüssel in `NODE_LLM_CONFIG` | Wert | Herkunft |
|---|---|---|
| `recherche_zwischen.timeout_s` | 1200 | 1,9× über dem groessten gemessenen Lauf (638 s) |
| `recherche_zwischen.max_output_tokens` | 5120 | über der groessten gemessenen Antwort (4176 Token) |
| `recherche_zwischen.temperature` | 0.1 | unveraendert, vorher fest an der Aufrufstelle |

**Beide Werte sind Obergrenzen, keine Ziele** — wer frueher fertig ist, kostet nicht mehr. Sie gehoeren als Paar zusammen und muessen es bleiben: 5120 Token brauchen bei den gemessenen ~7,3 Token/s rund 700 s und liegen damit mit Abstand innerhalb der Frist. Ein Deckel, der innerhalb der Frist nicht erreichbar waere, ist wirkungslos — die Frist schluege vorher zu.

**Warum das mehr ist als eine Bequemlichkeit.** Ein Fehlversuch loescht den Queue-Eintrag nach drei Laeufen **hart** (`versuch_zaehlen` → `DELETE`), waehrend der Verfall ihn nur weich deaktiviert und weckbar laesst. Und die Fehlversuche trafen die Wichtigen: Über die 582 aktiven `recherche`-Einträge stieg die mittlere `salienz_roh` monoton mit der Zahl der Versuche — 0,867 bei null, 0,947 bei einem, **0,990 bei zwei**. Der Grund ist mechanisch: Der Wichtigste wird zuerst gezogen, hat das meiste Material und laeuft deshalb als erster in die Frist. Sechzehn Eintraege standen einen Fehllauf vor der Loeschung.

Zeugen: `tests/test_recherche_frist.py` — zwei auf den Werten, einer auf ihrem Verhaeltnis, und zwei **am Syntaxbaum** darauf, dass die Aufrufstelle sie ueberhaupt liest. Der letzte Punkt ist der, der den Defekt gefunden haette: `NODE_LLM_CONFIG["recherche"]` existiert seit langem, ist vollstaendig — und hat **null Aufrufer**.

**Genutzte Infrastruktur:**

| Komponente | Pfad |
|-----------|------|
| Session-Kontext | `memory/kontext.py` |
| Web-Suche | `tools/web/search.py` (Serper, SearXNG als Rueckfall — seit 30.08.2026) |
| Page-Fetch | `tools/web/fetch.py` (trafilatura + BS4-Fallback) |
| Shadow-Stack | `services/pixie/stack.py` |
| KZG | `memory/kzg.py` |

---

Verwandte Dokumente:
- VertiefungsAgent (Konzept): `novaberg-pixie-deepdive_k.md`
- Pixie-Agenten-Übersicht: `novaberg-pixie.md`
- KZG-Agent (Shadow-Queue-Quelle): `novaberg-pixie-kzg.md`
- DelegationsAgent (Queue-Quelle): `novaberg-pixie-delegation.md`

---

## Befunde aus dem Betrieb — nachgetragen am 20.08.2026

Aus `novaberg-fundliste.md` hierher gezogen: Aussagen ueber den **Zustand** dieses Gegenstands, die dort als rohe Funde standen und in kein Defekt- oder Vorhabenregister gehoeren. Der Wortlaut ist unveraendert, das Datum steht an jedem Befund — geprueft ist keiner von ihnen gegen den heutigen Code.

- **16.08.2026** — **`server/agents/recherche/AGENT.md` ist seit dem 18.04.2026 unverändert und widerspricht dem Code an zwei Stellen.** Es führt `PIXIE_RECHERCHE_MAX_ITERATIONEN` mit Vorgabewert **2** und schreibt im Ablauf *„max 2 Iterationen"*; `server/config.py:425` und `novaberg-pixie-research.md` §7 sagen **3**. Und `## LLM-Calls` zählt *„Gesamt: 4-6 Calls"* **ohne die Zwischen-Destillation**, während das Konzeptdokument *„4-10 + 1"* zählt. **Gefunden von der zweiten Kontrolle**, nicht vom Nachzug — und der Grund ist mechanisch: Die Kandidatenmenge des Nachzugs durchsucht ausschließlich `docs/`, im Baum liegen aber **12 `AGENT.md` unter `server/`** und **null** in `docs/`. Das Moduldokument des geänderten Verzeichnisses ist damit der naheliegendste Kandidat und zugleich der einzige, den das Kriterium prinzipiell nicht erreicht.
