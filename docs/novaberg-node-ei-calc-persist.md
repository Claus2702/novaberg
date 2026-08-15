# Novaberg — Node: ei_calc_persist

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Pipeline-Node `ei_calc_persist` (Konsolidierung und Persistierung der Nova-EI)
**Stand:** 15. August 2026, Chat 140 (dreizehn Felder: die neun EI-Dimensionen, die beiden Raum-Achsen aus Chat 114 und die beiden Uhren der Eigenzeit)
**Pfad:** novaberg/docs/novaberg-node-ei-calc-persist.md
**Quellen:** novaberg-path2-perzeption_k.md (archiviert)
**Datei:** `graph/nodes/ei_calc_persist.py`
**Verwandt:** `novaberg-personality.md`, `novaberg-node-db-zugriff.md`, `novaberg-node-ei-calc.md`

---

## 1. Aufgabe

Der `ei_calc_persist`-Node ist der zweite EI-Calc-Schritt im CharacterGraph — die Konsolidierung am Ausgang des Laufs. Während der erste EI-Calc am Eingang (`_ei_calc_character` im `ei_calc`-Node) die Empathie-Modulation berechnet, konsolidiert dieser Node die frische Nova-Perzeption (vom `perzeption_assistant`-Node geliefert) durch Plausibilitäts-Regeln und persistiert das Ergebnis in Redis.

**Sinn:** Novas Selbst-Perzeption am Ende eines Turns soll plausibel bleiben, auch wenn die LLM-Klassifikation einzelne Felder ungenau setzt. Die Plausibilitäts-Regeln (Modus-Plausibilität, Stil-Plausibilität) korrigieren bekannte LLM-Inkonsistenzen, ohne die Klassifikation grundsätzlich zu überschreiben.

**Persistierung:** Das Ergebnis wird in den Redis-Hash `nova_state:{user_id}:{character_id}` geschrieben. Beim nächsten CharacterGraph-Lauf lädt der `db_zugriff`-Node diesen Hash. Damit ist Novas Zustand zwischen Turns kontinuierlich — sie wacht mit dem Zustand auf, mit dem sie eingeschlafen ist.

---

## 2. Position im Graph

```
CharacterGraph (Pfad 2):
  db_zugriff → ei_calc → enricher → reducer → router → ... → responder → thinker → tribunal → evaluate
                                                                                                  ↓
                                                          [corrector → tribunal]    [perzeption_assistant]
                                                                                              ↓
                                                                                    ▶ ei_calc_persist ◀
                                                                                              ↓
                                                                                          salience → dispatcher → END
```

Läuft nach `perzeption_assistant` und vor `salience`. Im evaluate-Branch des Tribunals nur dann erreichbar, wenn das Tribunal nicht erneut korrigieren lässt — also bei `verdict=ok` oder nach maximaler Korrektur-Runde.

Im HumanGraph läuft `ei_calc_persist` **nicht**. Pfad 1 hat keinen Perzeption-Assistant-Schritt und keinen Persistierungs-Bedarf — er erzeugt nur die User-Perzeption, die per Event-Queue weitergereicht wird.

---

## 3. Drei Schritte

### Schritt 1 — Plausibilitäts-Berechnung

Drei Korrekturen werden auf `internal.emotion` angewendet. Sie nutzen dieselben Funktionen aus `ei/berechnung.py`, die auch der HumanGraph-EI-Calc verwendet — aber mit Nova-Werten als Eingabe.

```python
# EI-Arousal: Modulations-Eingabe für Modus-Plausibilität
nova_arousal_ei = _ei_arousal_berechnen(
    internal.emotion.arousal,
    internal.emotion.relationship_dynamic,
    internal.emotion.intent,
    internal.emotion.tone,
)

# Modus-Plausibilität: korrigiert mode, falls Perzeption es widersprüchlich setzt
korrigierter_modus = _modus_plausibilitaet(
    internal.emotion.emotion,
    nova_arousal_ei,
    internal.emotion.mode,
)
internal.emotion.mode = korrigierter_modus

# Stil-Plausibilität: nutzt regelbasierten Stil aus Turn-Historie als Tiebreaker
regelbasiert_stil = _sprach_stil_erkennen(
    raw_turns,
    internal_charakter_dict,
    rolle="assistant",
)
korrigierter_stil = _stil_plausibilitaet(
    internal.emotion.emotion,
    nova_arousal_ei,
    internal.emotion.language_style,
    regelbasiert_stil,
    internal.emotion.tone,
)
internal.emotion.language_style = korrigierter_stil
```

Die Plausibilitäts-Funktionen sind beschrieben in `novaberg-ei.md`. Sie sind nicht-überschreibend: bei stimmiger Perzeption greifen sie nicht ein, bei widersprüchlichen Werten wählen sie den robusteren.

**Wichtige Detail-Korrektur:** `_sprach_stil_erkennen` wird mit `rolle="assistant"` aufgerufen. Vor Chat 89 filterte die Funktion intern hartcodiert auf User-Turns — was im CharacterGraph zu Stil-Verschiebungen führte (die Tiebreaker-Quelle waren die falschen Turns). Die Parametrisierung der Funktion war Teil von Phase 3 des PFAD2-PERZEPTION-FIX-Sprints.

### Schritt 2 — Redis-Persistierung

Die dreizehn konsolidierten Felder werden in einen Redis-Hash geschrieben — die neun EI-Dimensionen, die beiden Achsen von Novas Raum (Chat 114) und die beiden Uhren der Eigenzeit (Chat 140).

```python
nova_state_key = f"nova_state:{user_id}:{character_id}"
nova_state_mapping = {
    "raum_tiefe":           str(internal.raum.tiefe),
    "raum_naehe":           str(internal.raum.naehe),
    "emotion":              internal.emotion.emotion,
    "arousal":              str(internal.emotion.arousal),
    "emotions_vector":      internal.emotion.emotions_vector,
    "mode":                 internal.emotion.mode,
    "language_style":       internal.emotion.language_style,
    "relationship_dynamic": internal.emotion.relationship_dynamic,
    "tone":                 internal.emotion.tone,
    "intent":               internal.emotion.intent,
    "prompt_topic":         internal.emotion.prompt_topic,
    "turn_zeit":            str(jetzt),          # jeder Turn
}
if nutzer_zeit is not None:                      # nur eine Aeusserung
    nova_state_mapping["nutzer_zeit"] = str(nutzer_zeit)

redis_client.hset(nova_state_key, mapping=nova_state_mapping)
```

**Kein TTL.** Der Hash überlebt zwischen Turns und Server-Restarts. Konsistent zur `gv:detail:`-Konvention: jeder CharacterGraph-Lauf überschreibt den vorigen Stand, kein Verfall.

**Schreib-Modus `hset` mit `mapping`:** Atomischer Update aller Felder gleichzeitig, nicht inkrementell — der Hash wird durch jeden Lauf vollständig neu beschrieben. `nutzer_zeit` ist die Ausnahme: Es wird auf einem Impuls-Turn **nicht mitgeschrieben** und behält damit seinen Stand.

**Warum zwei Uhren (Chat 140).** Der Verfall über das Intervall (`novaberg-eigenzeit_k.md` Bauteil A) braucht den Abstand zur letzten **Nutzeräußerung**. Liefe er auf dem letzten Turn, setzte der stündliche Impuls die Uhr zurück und die Nacht wäre nie eine Pause — das ist die Bedingung, an der der Bauteil scheitert, wenn man sie übersieht. `turn_zeit` trägt deshalb jeden Turn, `nutzer_zeit` nur den, den ein Mensch ausgelöst hat.

**Und warum hier statt im Session-Verlauf**, der ein `zeit`-Feld je Turn führt: **Die Länge des Verlaufs ist begrenzt, nicht nur seine Frist.** Ab 25 Turns werden die ältesten zehn zusammengefasst und entfernt (`SESSION_SUMMARIZE_AT`) — als Zahl überlebt ein Zeitstempel das nicht. Eine Nacht mit stündlichen Impulsen schiebt die letzte Nutzeräußerung damit aus dem Fenster, **während sie die Frist immer wieder erneuert**: Der Verlauf lebt, und gerade der eine Eintrag, auf den es ankäme, ist fort.

Die Frist selbst war bis zum 15.08.2026 das zweite Argument — sie lag bei zwei Stunden, also **unter** der Verfallskurve. Sie steht jetzt bei vier (`SESSION_TTL`) und deckt die Kurve ab; das Argument der Kappung bleibt davon unberührt. Unabhängig von beidem gilt: Der Zustand liegt ohnehin in diesem Hash, und seine Uhr gehört dorthin, wo er selbst liegt.

**Die Quelle von `nutzer_zeit` ist `empfangen_am` aus dem Ereignis, nicht die Uhr dieses Knotens.** Er läuft am Ende des Durchlaufs, hinter Perzeption, Salienz und den Modellaufrufen. Gemessen am 15.08.2026 lagen zwischen beiden **127,8 Sekunden** — sie steckten sonst als Fehler in jedem Abstand. Dieselbe Begründung steht an der Quelle in `api/chat.py`, wo `erstellt_am` aus genau diesem Grund verworfen wurde.

**Warum der Raum hier mitfährt (Chat 114):** Die neun EI-Felder beschreiben je eine Äußerung — sie werden pro Turn neu klassifiziert. Die beiden Raum-Achsen beschreiben einen **Zustand**, der zwischen zwei Labels liegen kann und über mehrere Turns wandert. Ohne Persistenz gäbe es keinen Zwischenzustand und damit keinen Zug, nur ein Springen von Label zu Label. Geschrieben werden sie hier, weil der Raum denselben Lebenszyklus hat wie der übrige Nova-Zustand: ein Wert je Paar, kein Verfall, überschrieben am Ausgang jedes CharacterGraph-Laufs.

### Schritt 3 — Pipeline-Log-Eintrag

Span-Klammer mit allen Berechnungen plus Schreib-Eintrag.

```
ei_calc_persist | character | span_start | {}
ei_calc_persist | character | berechnung | {schritt: "ei_arousal", arousal_roh, arousal_ei, ...}
ei_calc_persist | character | berechnung | {schritt: "modus_plausibilitaet", perzeption, korrigiert}
ei_calc_persist | character | berechnung | {schritt: "stil_plausibilitaet", perzeption, regelbasiert, korrigiert}
ei_calc_persist | character | db_write   | {tabelle: "redis:nova_state", felder: [...], operation: "hset"}
ei_calc_persist | character | span_end   | {}
```

Forensik: pro Turn ist nachvollziehbar, welche Plausibilität welchen Wert korrigiert hat. Bei Drift-Verdacht kann gegen die Roh-Perzeption verglichen werden.

---

## 4. Datenfluss

```
perzeption_assistant
  └─► state["internal"].emotion (neun Felder, frisch klassifiziert)
                                 │
                                 ▼
                          ei_calc_persist
                                 │
                          ┌──────┴───────┐
                          ▼              ▼
                Plausibilitäten      Redis-Write
              (Modus, Stil           nova_state:{u}:{c}
               korrigiert)
                          │
                          ▼
                   state["internal"].emotion
                   (konsolidiert)
                                 │
                                 ▼
                            salience
```

Die Konsolidierung wirkt **in-place auf `state["internal"]`** und ist damit für `salience` und den nachfolgenden `dispatcher` sichtbar. Salience analysiert den Assistant-Turn mit den konsolidierten Werten, der Dispatcher schreibt den Session-Turn mit den konsolidierten Werten.

---

## 5. Default Mode Network: Persistierung zwischen Turns

Der Redis-Hash `nova_state:{user_id}:{character_id}` ist Novas Zustands-Anker zwischen Turns. Architektur-Vision:

**User-Turns:** Jeder CharacterGraph-Lauf liest beim Start den Hash (via `db_zugriff`) und schreibt am Ende den Hash neu (via `ei_calc_persist`). Damit ist Novas Stimmung zwischen User-Turns kontinuierlich.

**Pixie-Turns:** Wenn Pixie einen CharacterGraph-Lauf triggert (für Träumen, Recherche-Reflexion), läuft derselbe Pfad. Der `db_zugriff` lädt den letzten Stand, Pixie produziert Inhalt im Responder, die Selbst-Perzeption erfasst Novas Reaktion auf den eigenen Inhalt, `ei_calc_persist` schreibt das Ergebnis. Novas Innenleben akkumuliert Spuren zwischen User-Turns.

**Beim nächsten User-Turn** wacht Nova mit dem Zustand auf, der durch Pixie-Aktivität (und/oder dem letzten User-Turn) entstanden ist. Pixie ist Novas Default Mode Network — die innere Aktivität, die zwischen externen Reizen passiert.

Vor dem PFAD2-PERZEPTION-FIX gab es keinen persistierten Nova-Zustand zwischen Turns. Jeder CharacterGraph-Lauf startete mit den User-Werten aus dem Event-Payload, modifizierte sie minimal und schrieb sie ungespeichert in den nächsten Lauf. Nova hatte keine Identität über die Zeit — sie war reaktive Spiegelung des Users.

---

## 6. Schema des Redis-Hash

Tabellarisch zur Übersicht:

| Feld | Typ in Redis | Beispielwert |
|---|---|---|
| `raum_tiefe` | string (numerisch) | `0.51` |
| `raum_naehe` | string (numerisch) | `0.64` |
| `emotion` | string | `begeisterung` |
| `arousal` | string (numerisch) | `0.9` |
| `emotions_vector` | string | `plateau` |
| `mode` | string | `emotional` |
| `language_style` | string | `emotional` |
| `relationship_dynamic` | string | `vertrauen` |
| `tone` | string | `empathisch` |
| `intent` | string | `personal` |
| `prompt_topic` | string | `Gefuehl des Einklangs` |
| `turn_zeit` | string (Unix-Zeit) | `1786792663.6` |
| `nutzer_zeit` | string (Unix-Zeit) | `1786792535.8` — fehlt, solange nie eine Äußerung einging |

Inspektion per `redis-cli`:

```bash
docker exec ki_redis redis-cli HGETALL "nova_state:meister:nova"
```

Schreibvorgänge sind nur durch `ei_calc_persist` vorgesehen. Andere Schreib-Pfade sind nicht implementiert (kein direkter Pixie-Schreib-Pfad — Pixie schreibt indirekt über den CharacterGraph-Lauf).

---

## 7. Cold-Start-Verhalten

Beim allerersten Turn pro User-Charakter-Paar existiert der Hash noch nicht. Reihenfolge:

1. **Turn 1, db_zugriff:** Hash existiert nicht. `internal.emotion` wird mit `Emotion()`-Defaults befüllt (alle Felder neutral).
2. **Turn 1, Pipeline läuft:** Perzeption-Assistant klassifiziert Novas erste Antwort.
3. **Turn 1, ei_calc_persist:** Konsolidiert die frische Perzeption, schreibt zum ersten Mal in den Hash.
4. **Turn 2, db_zugriff:** Hash existiert jetzt. `internal.emotion` wird mit den Turn-1-Werten befüllt.

Im Pipeline-Log ist Cold-Start an `exists: false` im `db_zugriff`-`db_read`-Eintrag erkennbar. Ab Turn 2 steht dort `exists: true`.

---

## 8. Pixie-Pfad — abweichendes Verhalten

Bei Pixie-getriggerten Läufen (`event_source != "user"`) hat `db_zugriff` die Pixie-Sonderbehandlung angewandt (`external = Kopie von internal`). Im EI-Calc ist die Empathie-Modulation neutral, weil keine Differenz besteht.

Im `ei_calc_persist` ändert sich **nichts** — der Node arbeitet auf `internal.emotion` wie immer. Die Plausibilitäten korrigieren, die Persistierung schreibt. Pixie ist damit ein vollständiger Akteur im Default Mode Network: jede Pixie-Reflexion hinterlässt eine Spur in Novas Zustand.

Konsequenz: Pixie-Turns moduliert Novas Stimmung. Wenn Pixie über etwas Schweres reflektiert (z.B. eine schwierige Erinnerung aus der LZG-Promotion), schreibt der `ei_calc_persist` einen entsprechend gefärbten Zustand. Der nächste User-Turn wacht damit auf.

---

## 9. Was der Node nicht tut

- **Keine LLM-Aufrufe.** Plausibilitäten sind reine Python-Funktionen.
- **Keine neuen DB-Reads.** Alle nötigen Werte liegen schon im State (von `db_zugriff` und `perzeption_assistant`).
- **Keine Modifikation von `external`.** Nur `internal.emotion` wird angepasst und persistiert.
- **Kein KZG- oder LZG-Eintrag.** Salience und KZG-Dispatch sind getrennte Verantwortung.
- **Keine Charakter-Profile.** `internal.character` wird nicht hier persistiert — Charakter-Hashes pflegt der CharakterAgent in PostgreSQL.

Klare Trennung: dieser Node ist ein dedizierter Zustands-Konsolidierer und -Persistierer. Eine Aufgabe, eine Verantwortung.

---

## 10. Fehler-Pfade

| Quelle | Fehler | Verhalten |
|---|---|---|
| `internal` fehlt im State | Unmöglich nach `db_zugriff`-Lauf | `logger.warning`, überspringt Persistierung |
| Plausibilitäts-Funktion wirft | Eingabe-Werte unsinnig | Exception propagiert, ungeplante Drift möglich |
| Redis `hset` schlägt fehl | Verbindungsfehler | Exception propagiert, kein silent skip |
| `raw_turns` leer | Erster Turn, keine Historie | `_sprach_stil_erkennen` liefert Default, keine Plausibilitäts-Korrektur |

Defensiv-Verhalten an einer Stelle: wenn `internal` aus dem State fehlt (ein unmöglicher Pfad, weil `db_zugriff` ihn immer setzt), schreibt der Node `logger.warning` und kehrt zurück. Damit bricht der Graph nicht, aber der Persistierungs-Schritt fehlt für diesen Turn — ein anomalies-erkennbarer Fall.

---

## 11. Performance

Pro Lauf:

- 3 reine Python-Berechnungen (`_ei_arousal_berechnen`, `_modus_plausibilitaet`, `_stil_plausibilitaet`)
- 1 Redis `HSET` mit Mapping
- 4 Pipeline-Log-Inserts (gebatcht)

Gesamt unter 2 ms. Keine LLM-Calls, keine pgvector-Suchen. Der Node ist Schreib-orientiert mit minimaler Verarbeitung.

---

## 12. Migration: vor und nach PFAD2-PERZEPTION-FIX

**Vorher (bis Chat 88):** Es gab keinen `ei_calc_persist`-Node. Die Plausibilitäts-Funktionen liefen im HumanGraph auf User-Werten, der CharacterGraph hatte keine eigene Konsolidierung. Novas Emotion-Werte wurden teilweise im `_ei_calc_character` im Eingangs-EI-Calc modifiziert (Empathie), aber nicht persistiert. Zwischen Turns ging Novas Zustand verloren.

**Nachher (ab Chat 89):** Eigener Node am Ausgang des CharacterGraphs. Plausibilitäten laufen explizit für Nova. Persistierung in Redis. Kontinuität zwischen Turns. Pixie-Aktivität wirkt sich auf Novas Stimmung aus.

Die Vorgeschichte ist im archivierten Konzept-Dokument `novaberg-path2-perzeption_k.md` ausführlich dokumentiert.

---

## 13. Verwandte Dokumente

- `novaberg-personality.md` — die Klassen-Schicht, in deren `internal.emotion` der Node schreibt
- `novaberg-node-db-zugriff.md` — der Eingangsnode, der die Persistierung beim nächsten Turn wieder lädt
- `novaberg-node-ei-calc.md` — erster EI-Calc-Schritt (Empathie-Modulation am Eingang)
- `novaberg-ei.md` — die Plausibilitäts-Funktionen
- `novaberg-mem-session.md` — Redis-Key-Konventionen
- `novaberg-pixie.md` — Pixie-Architektur und Default Mode Network
