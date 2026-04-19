# Novaberg — Pixie (Hintergrundverarbeitung)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Pixie — Hintergrundverarbeitung (Übersicht)
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/novaberg-pixie.md
**Quellen:** nova-05-k.md (Pixie-Konzept), nova-05-a.md (AgentGraph), nova-05-t-a.md (Queue/Stack/Delivery), nova-05-m-a.md (Agenten-Referenz)

---

## 1. Konzept

Pixie ist Novas Unterbewusstsein — ein autonomer Hintergrundprozess, der weiterdenkt, wenn niemand chattet. Die kognitionswissenschaftliche Grundlage ist das Default Mode Network (DMN): das Netzwerk im menschlichen Gehirn, das genau dann aktiv ist, wenn wir nicht auf eine konkrete Aufgabe fokussiert sind — beim Tagtraeumen, Gruebeln, freien Assoziieren. Studien zeigen, dass das DMN eine zentrale Rolle bei der Gedaechtniskonsolidierung und kreativen Problemloesung spielt.

Pixie recherchiert Themen, vertieft Wissen, promotet Erinnerungen ins Langzeitgedaechtnis, destilliert Persoenlichkeitsprofile und raeumt auf. Ergebnisse fliessen beim naechsten Gespraech natuerlich ein. Pixie ist kein eigenes Wesen — Pixie ist Nova im Hintergrundmodus. Gleicher Charakter, gleiche Memory-Engine, aber eigenes Gedaechtnis (`user_id: nova`) und eigene Verarbeitung (CPU-Modell, kein GPU-Lock).

Der fundamentale Unterschied zwischen Werkzeug und Denkpartner: Ein Werkzeug wartet. Ein Denkpartner denkt weiter. Kompetitives Scheduling sorgt dafuer, dass immer das Wichtigste zuerst bearbeitet wird.

---

## 2. Scheduling

Der Heartbeat (APScheduler, Default: 120 Sekunden) triggert jeden Zyklus. Ein Redis-Lock (`pixie:running`, TTL 600s als Sicherheitsnetz) verhindert Parallelitaet: laeuft der letzte Zyklus noch, wird der neue Trigger verworfen.

Pro Heartbeat werden Kandidaten aus zwei Quellen gesammelt:

**Queue-Peek:** Der Eintrag mit der hoechsten Prioritaet aus Shadow-Queue, Promotion-Queue und Delegations-Queue wird vorgemerkt (Peek, nicht Pop).

**Faellige periodische Aufgaben:** Jeder Agent meldet beim Serverstart seine periodische Aufgabe an (Redis `pixie:schedule:{name}` mit Priority, Interval, next_run). Alle Eintraege mit `next_run <= now()` sind Kandidaten.

Die hoechste Prioritaet gewinnt — Queue-Kandidat gegen periodischen Kandidaten, keine Normalisierung. Genau ein Agent wird pro Zyklus ausgefuehrt. Bei Fehler: Retry-Counter (max 3), danach verwerfen und loggen.

---

## 3. Queue, Stack und Delivery

Drei Redis-Strukturen verbinden Chat und Pixie:

**Shadow-Queue** (`shadow_queue:{user_id}`, List, Chat nach Pixie): Wird automatisch aus dem KZG befuellt, wenn Salienz >= 0.7. Die primaere Intention bestimmt die Aufgabe (recherche, vertiefen, nachfragen). Max 20 Eintraege pro User. Nova-Guard: kein Push fuer `user_id="nova"` (verhindert Feedback-Loop).

Shadow-Queue Eintragsformat:
```json
{
    "aufgabe": "recherche",
    "key": "kzg:meister:1711234567890",
    "themen": "Quantencomputing, Physik",
    "salienz": 0.85,
    "emotion": "neugierig",
    "modus": "fachgespraech"
}
```

**Promotion-Queue** (`queue:{user_id}`, List, Chat nach Pixie): Separater Kanal fuer Gedaechtnis-Promotion. Trigger: KZG-Eintrag erreicht Salienz >= PROMOTION_THRESHOLD (0.8). Hoechste Prioritaet — wird vollstaendig abgearbeitet.

Promotion-Queue Eintragsformat:
```json
{
    "aufgabe": "lzg_promotion",
    "key": "kzg:meister:1711234567890",
    "salienz": 0.95,
    "themen": "Astronomie, schwarze Löcher",
    "dimension": "interessen"
}
```

**Shadow-Stack** (`shadow_stack:{user_id}`, Sorted Set, Pixie nach Chat): Ergebnisse von Pixie-Agenten. Jeder Eintrag hat ein Embedding. Zwei Konsumenten: der Enricher (reaktiv, beim naechsten Turn, bester Cosine-Match) und der Shadow Delivery Service (proaktiv, via WebSocket).

Shadow-Stack Eintragsformat:
```json
{
    "aufgabe": "recherche",
    "themen": "Quantencomputing, Physik",
    "zusammenfassung": "Quantencomputing nutzt Quantenbits...",
    "wichtigster_punkt": "...",
    "vorschlag": "...",
    "emotion": "neugierig",
    "modus": "fachgespraech",
    "embedding": [0.12, -0.34, ...]
}
```

**Delivery Service:** Eigenstaendiger Dienst, prueft zyklisch ob eine proaktive Nachricht gesendet werden soll. Entscheidungskette: Momentum low? Session-Turns vorhanden? Cosine Similarity >= 0.65? Emotionale Kompatibilitaet? Modus-Kompatibilitaet? Bei Bestehen: GPU-Modell formuliert Nachricht, WebSocket liefert aus. MAX_BURST = 2 Impulse pro Zyklus.

---

## 4. Tri-LLM-Routing

Pixie laeuft auf zwei eigenen LLMs, physisch getrennt vom Chat:

| Modell | Zweck | Hardware | Context |
|--------|-------|----------|---------|
| `mistral-small3.2-gpu` | Chat (bewusst) | VRAM (GPU) | 16384 |
| `qwen3-32b-cpu` | Pixie Analyse (Reasoning, JSON) | RAM (CPU) | 32768 |
| `mistral-small3.2-cpu` | Pixie Sprache (Fliesstext, Deutsch) | RAM (CPU) | 32768 |

Statisches Routing pro Workflow-Schritt: Analyse (Reasoning, JSON-Output) auf Qwen3, Sprache (Fliesstext, Charakter-Treue) auf Mistral. Beide CPU-Modelle gleichzeitig im RAM (36 GB < 64 GB verfuegbar). Komplett entkoppelt — der Chat-Flow wird nie durch Pixie blockiert. CJK-Guard verhindert chinesische Ausgaben bei Qwen.

---

## 5. Agenten-Uebersicht

| # | Agent | Typ | Periodisch | Prio | Intervall | LLM-Call | context_user | Status |
|---|-------|-----|-----------|------|-----------|----------|-------------|--------|
| 1 | **PromotionAgent** | Workflow | Ja | 0.9 | 5 min | Ja (CPU, 1-3 Calls) | `user` | ✅ |
| 2 | **DecayAgent** | Workflow | Ja | 0.2 | 24 h | Nein | `user` + `nova` | ✅ |
| 3 | **CharakterAgent** | Workflow | Ja | 0.3 | 10 min | Ja (CPU, 5 Calls) | `meister` + `nova` | ✅ |
| 4 | **WiedervorlageAgent** | Workflow | Ja | 0.5 | 12 h | Ja (CPU, 1 pro Eintrag) | `user` | ✅ |
| 5 | **RechercheAgent** | Workflow | Queue | — | — | Ja (CPU, 3-5 Calls) | `user` | ✅ |
| 6 | VertiefungsAgent | Workflow | Queue | — | — | — | `user` | ⬜ |
| 7 | NachfragenAgent | Workflow | Queue | — | — | — | `user` | ⬜ |
| 8 | AufraeumAgent | Workflow | Ja | 0.1 | 24 h | — | `user` | ⬜ |

**PromotionAgent:** Zwei-Call-Promotion (Klassifikation + Extraktion). Arbeitet die Promotion-Queue vollstaendig ab. 4 Qualitaetsfilter in der Nachbearbeitung. Setzt `hash_dirty` nach erfolgreicher Promotion.

**DecayAgent:** Berechnet Ebbinghaus-Decay fuer alle aktiven LZG-Eintraege beider User. Eintraege unter 0.1 werden per Soft-Delete inaktiv. Kein LLM-Call — reines Python/SQL.

**CharakterAgent:** Destilliert 5 Profile einzeln (Kern, Adaptiv, Intention, Emotion, Beziehung). Prueft `hash_dirty` fuer beide User. Kein dirty Flag bedeutet sofortiger Return.

**WiedervorlageAgent:** Scannt 4 Tabellen (Entitaeten, Fakten, Timeline, Notizen) nach `wiedervorlage_am <= now()`. Pro Treffer formuliert das LLM eine Erinnerung fuer den Shadow-Stack. Verschiebt Wiedervorlage um 7 Tage.

**RechercheAgent:** Erster Agent mit echter Web-Recherche. Destilliert Session-Kontext, plant Suchqueries, fuehrt Web-Suche + Auto-Fetch durch, bewertet iterativ, destilliert Fliesstext fuer Delivery.

---

## 6. AgentGraph

Der AgentGraph ist eine leichtgewichtige 3-Node-Kette fuer Novas eigene Gedaechtnis-Verarbeitung nach Shadow-Delivery:

```
Enricher → Salienz → Dispatcher → END
```

Kein Perzeption, kein Router, kein Responder, kein Tribunal. Pixie weiss bereits, was zu tun ist. Typischer LLM-Verbrauch: 1 Call (Salienz) pro Durchlauf. Die migrierten Pixie-Agenten (5 von 8) laufen eigenstaendig — sie nutzen eigene Tool-Manager und KZG/Stack-Aufrufe, ohne den AgentGraph. Der geplante PixieGraph (PIX-GRAPH) wird den AgentGraph als zentrale Routing-Infrastruktur abloesen.

---

## 7. Konfiguration

| Parameter | Default | Pfad | Beschreibung |
|-----------|---------|------|-------------|
| `PIXIE_INTERVALL_SEKUNDEN` | 120 | `config.py` | Heartbeat-Intervall |
| `PIXIE_LOCK_TTL_SEKUNDEN` | 600 | `config.py` | Sicherheits-TTL gegen Deadlocks |
| `PROMOTION_THRESHOLD` | 0.8 | `memory/kzg.py` | Salienz-Schwelle fuer LZG-Promotion (KZG-lokal, nicht in config.py) |
| `PIXIE_PROMOTION_PRIORITAET` | 0.9 | `config.py` | Scheduler-Priorität für den Promotion-Task |
| `PIXIE_PROMOTION_INTERVALL_SEKUNDEN` | 300 | `config.py` | Trigger-Intervall des Promotion-Tasks |
| `qwen3-32b-cpu` | Port 11435 | — | Analyse-Modell (Reasoning, JSON) |
| `mistral-small3.2-cpu` | Port 11435 | — | Sprach-Modell (Fliesstext, Deutsch) |
| `MAX_BURST` | 2 | `services/shadow_delivery.py` | Max. Impulse pro Delivery-Zyklus |

Naming-Konvention: Anzeige = "Pixie" (Logs, UI, Dokumentation). Technisch = "Shadow" (Redis-Keys, Verzeichnisse, Funktionsnamen).

---

*Konsolidiert aus nova-05-k.md, nova-05-a.md, nova-05-t-a.md, nova-05-m-a.md.*
