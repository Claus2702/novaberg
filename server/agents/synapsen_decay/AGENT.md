# Agent: synapsen_decay

**Typ:** Pixie-Hintergrund-Agent (workflow, kein LLM)
**Konzept:** `novaberg-memory-synapsen_k.md` §9 (Decay-Logik), P6
**Scheduling:** täglich (`interval = PIXIE_DECAY_INTERVALL_SEKUNDEN = 86400`, `priority = PIXIE_DECAY_PRIORITAET = 0.2`), Verhungerungsschutz über das Pixie-Aging (`novaberg-pixie.md` §2)
**Feature-Flag:** `SYNAPSEN_DECAY_AKTIV` (Default true, gated durch `PIXIE_AKTIV`)

## Aufgabe

Einmal täglich zwei entkoppelte Wartungsläufe im selben Job:

1. **Knoten-Decay** (`memory.lzg_knoten.run_node_decay`) — materialisiert
   `gewicht_decay` je aktivem Knoten aus dem exponentiellen Verfall seit
   `verstaerkt_am` (§9.2). `gewicht_absolut` (Anker-Stärke) bleibt unangetastet;
   der Decay zieht nur die aktuelle Präsenz nach unten. Knoten, deren
   `gewicht_decay` unter `LZG_KNOTEN_MIN_GEWICHT` fällt, werden auf
   `aktiv = FALSE` gesetzt (Soft-Delete, reaktivierbar via Halbreaktivierung).

2. **TTL-Cleanup** (`memory.pipeline_log.delete_expired_entries`) — löscht
   `pipeline_log`-Einträge älter als `LZG_PIPELINE_LOG_VORHALTUNG_TAGE`.

Der Lauf ist **global** über alle Paar-Partitionen — die Decay-Formel ist
knoten-lokal, ein globaler Bulk-Sweep ist bit-identisch zur Paar-Schleife.

## Architektur

- Kein LangGraph: `build_graph()` gibt `None`, die Arbeit läuft synchron in
  `invoke()` (Muster wie `decay`, `ziel_decay`, `synapsen_promotion`).
- Der Agent öffnet **keine** eigene DB-Connection. Fachlogik lebt in den
  `memory`-Modulen; `POSTGRES_URL` wird als Parameter durchgereicht.
- **Audit** (`hintergrund_log`): Lebenszyklus `gestartet → erledigt`/`fehler`.
- **Forensik** (`pipeline_log`): zwei Zeilen pro Lauf (Start / Ende), korreliert
  über einen synthetischen `run_id` (kein echter Turn im periodischen Lauf).
  Best-effort — ein Forensik-Schreibfehler killt den Decay-Lauf nicht.

## Abgrenzung

- **Halbreaktivierung** (§9.3) gehört NICHT hierher, sondern in den Schreibpfad
  von `memory/lzg_knoten.py` (P6 Teil B).
- **Kanten** haben keinen eigenen Decay (§9.5); ihre effektive Stärke ergibt
  sich indirekt aus dem Decay der beteiligten Knoten. Kein Re-Cache hier.
- **Charakter-Hash** bleibt unberührt (P7).
