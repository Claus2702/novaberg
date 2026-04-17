# 12_L_a — Lesson: "NIEMALS" ist kein Proxy für "nur wenn erlaubt"

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Absolute Verbote bei instruktionstreuen Modellen
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/nova-node-router_l.md
**Ursprung:** nova-12-l-a.md
**Typ:** Lesson (L)
**Auslöser:** Router setzte `management_action` nie auf `"agent"` bei Claude-Backend

---

## 1. Das Problem

Nach der Claude API-Integration (Chat 39) erkannte der Router keine Agent-Domänen mehr. "Erinnere mich morgen um 8 Uhr" und "IT-Termin in Frankfurt um 10 Uhr" gingen beide nicht an den TimelineAgent. Der Router gab `management_action = ""` zurück — bei jeder Nachricht, ausnahmslos.

Mit Mistral (lokal) funktionierte dieselbe Konfiguration einwandfrei.

---

## 2. Die Ursache

Der Router-Base-Prompt enthielt im `[REGELN]`-Block:

```
AGENTEN-DELEGATION:
- "management_action", "management_target", "management_target_typ":
  Diese Felder werden AUSSCHLIESSLICH durch die Agentenregeln unten gesteuert.
  Setze sie NIEMALS eigenstaendig.
  Ohne passende Agentenregel: ALLE DREI Felder LEER lassen ("").
```

Darunter folgten die Plugin-Prompts mit Erkennungsregeln:

```
TIMELINE-ERKENNUNG:
Setze management_action = "agent" wenn:
1. Der User einen Termin erstellen, verschieben oder loeschen moechte
...
```

**Mistral** las "NIEMALS eigenständig" und verstand implizit: "...außer wenn die Plugin-Regeln es verlangen." Die Plugin-Regeln waren ja keine "eigenständige" Entscheidung, sondern eine explizite Anweisung.

**Claude** las "NIEMALS eigenständig" als absolutes Verbot. Aus Claudes Perspektive: Wenn ich `management_action = "agent"` setze, setze ich es eigenständig — egal ob eine Plugin-Regel das vorschlägt. "NIEMALS" heißt NIEMALS. Die Plugin-Regeln wurden nicht als Ausnahme erkannt, sondern als widersprüchliche Anweisung, die das Verbot nicht aufheben konnte.

---

## 3. Die Lösung

Drei Änderungen:

### 3.1 Positive Handlungsanweisung statt Universalverbot

**Alt:**
```
Setze sie NIEMALS eigenstaendig.
Ohne passende Agentenregel: ALLE DREI Felder LEER lassen ("").
```

**Neu:**
```
Wenn eine Regel aus dem [AGENTEN]-Block zutrifft, MUSST du die Felder setzen.
Ohne passende Agentenregel: ALLE DREI Felder LEER lassen ("").
```

Der Unterschied ist subtil aber entscheidend: "MUSST wenn Regel zutrifft" ist eine eindeutige positive Anweisung. Kein Modell — egal wie instruktions­treu — kann das als Verbot interpretieren.

### 3.2 Konkrete Beispiele in allen Plugin-Prompts

Abstrakte Regeln allein reichen nicht. Jeder Plugin-Prompt bekam 4–5 konkrete Beispiele:

```
BEISPIELE:
- "Erinnere mich morgen um 8 Uhr ans Meeting" → management_action = "agent"
- "Termin am Freitag um 14 Uhr" → management_action = "agent"
```

Beispiele sind modellunabhängig wirksam — sie zeigen das gewünschte Verhalten statt es zu beschreiben.

### 3.3 Wording-Konsistenz

"Bei management_action = 'agent'" → "Bei Erkennung:" in allen Plugins. Die alte Formulierung verwies auf das Feld, das gesetzt werden sollte — ein Zirkelschluss. Die neue Formulierung ist eine klare Handlungsanweisung.

---

## 4. Die Regel

> **"NIEMALS" ist kein Proxy für "nur wenn erlaubt".**

Bei instruktionstreuen Modellen (Claude, GPT-4) überschreibt ein kategorisches Verbot im Base-Prompt alle nachfolgenden Erlaubnisse in Plugin-Prompts. Das Modell kann nicht wissen, dass "NIEMALS" eigentlich "nur unter bestimmten Bedingungen" bedeutet.

**Prompt-Design-Regel:** Verwende positive Handlungsanweisungen ("MUSST wenn X") statt negative Universalverbote ("NIEMALS Y"). Verstärke durch konkrete Beispiele.

---

## 5. Verwandte Lessons

- **"Base-Prompt schreit lauter als Plugin-Prompt"** (Chat 26, `nova-11-l-b`): Der Base-Prompt mit 20+ konkreten Beispielen überstimmte die abstrakte Plugin-Regel. Lösung: Management-Block entfernen. — Hier war es nicht Lautstärke, sondern Absolutheit.

- **"Strukturierte Kontextualisierung"** (Chat 27, `nova-11-l-b`): Imperative ("Erfinde KEINE Probleme") versagen, wenn das LLM den Kontext falsch einordnet. Beschreiben statt Verbieten. — Verwandtes Prinzip: Positive Anweisung > Negative Anweisung.

- **"Der unsichtbare Default"** (Chat 20, `nova-07-l-c`): "Du bist ein hilfreicher KI-Assistent" aktivierte RLHF-Conditioning. — Zeigt ebenfalls: Modelle nehmen Prompt-Inhalte wörtlicher als Entwickler erwarten.

---

## 6. Modellübergreifende Prompt-Hygiene

| Muster | Risiko | Besser |
|--------|--------|--------|
| "NIEMALS X" | Blockiert auch gewünschte Ausnahmen | "X nur wenn Y" |
| "Setze NICHT eigenständig" | Modell weiß nicht, was "eigenständig" ist | "Setze wenn Regel zutrifft" |
| Abstrakte Regel ohne Beispiel | Modell interpretiert anders als gemeint | Regel + 3–5 Beispiele |
| "Ignoriere wenn nicht relevant" | Erlaubnis zum Überspringen | "Nutze als Grundlage" (Chat 39, GV) |

Diese Muster gelten nicht nur für den Router, sondern für alle Prompt-Stellen, die Modell-übergreifend funktionieren sollen.

---

→ Router (Agenten-Delegation): `nova-01-m-b.md`
→ Base-Prompt-Lesson: `nova-11-l-b.md`
→ Epic 12 Konzept: `nova-12-k.md`
