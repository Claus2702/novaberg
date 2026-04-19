# 07_L_c — Lesson: Der unsichtbare Default

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — System-Prompt-Override durch API-Default
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/novaberg-node-responder_l.md
**Ursprung:** nova-07-l-c.md
**Typ:** Lesson (L)
**Entdeckt:** Chat 20 (Sarkasmus-Charakter-Test)
**Betrifft:** `api/models.py`, `api/chat.py`, `graph/human_graph.py`, Responder-Verhalten

---

## 1. Symptom

Novas Charakter-Hash wurde korrekt geladen, korrekt in den State geschrieben und korrekt in den Responder-Prompt injiziert — aber das Modell ignorierte ihn vollständig. Nova antwortete immer höflich, floskelhaft, unterwürfig. Ein manuell gesetzter Sarkasmus-Hash ("frech, direkt, trockener Humor") hatte null Effekt auf die Antworten.

---

## 2. Ursache: Drei System-Prompts, einer gewinnt

Der System-Prompt existierte an drei Stellen mit drei verschiedenen Texten:

| Datei | Text | Erreichbar? |
|-------|------|-------------|
| `api/models.py` | "Du bist ein hilfreicher KI-Assistent." | ✅ **Immer aktiv** |
| `graph/human_graph.py` | "Du bist Nova, warmherzig, neugierig..." | ❌ Nie erreicht |
| `graph/builder.py` | "Du bist Nova, vertraute Assistentin..." | ❌ Deprecated |

Der Datenfluss:

```
Client sendet Request → kein system-Feld
    → models.py Default greift: "Du bist ein hilfreicher KI-Assistent."
    → chat.py Zeile 132: system_prompt = anfrage.system  (IMMER explizit)
    → create_state(system_prompt="Du bist ein hilfreicher KI-Assistent.")
    → Der gute Default in create_state() wird nie erreicht
```

Python-Defaults greifen nur wenn ein Parameter *weggelassen* wird. Ein explizit übergebener Wert — auch ein schlechter — zählt als gültig. `chat.py` übergab **immer** `anfrage.system`, deshalb wurde der Default in `create_state()` seit Chat 7 nie ausgeführt.

---

## 3. Warum das Modell den Hash ignorierte

"Du bist ein hilfreicher KI-Assistent." ist das stärkste Conditioning-Pattern für RLHF-trainierte Modelle. Jedes Alignment-Training verstärkt genau dieses Muster: höflich, unterwürfig, service-orientiert. Novas Charakter-Hash ("frech, direkt, sarkastisch") kämpfte gegen die härteste Prägung des Modells an — und verlor.

Der Beweis: Nach dem Fix (minimaler System-Prompt "Du bist Nova. Antworte auf Deutsch.") wirkte derselbe Sarkasmus-Hash sofort:

- Vorher: "Entschuldige bitte. Wie kann ich dich besser unterstützen?"
- Nachher: "Okay, ich versuch's anders. Aber hey, du hast schon Schlimmeres überlebt."

---

## 4. Der Fix

**`api/models.py`:** Default von "Du bist ein hilfreicher KI-Assistent." auf `f"Du bist {ASSISTANT_NAME}. Antworte auf Deutsch."` — minimale Stellenbeschreibung, kein RLHF-Trigger.

**Zusätzlich entdeckt:** Inkonsistente Prompt-Texte in `shadow_delivery.py`, `human_graph.py` und `builder.py` — alle mit verschiedenen Persönlichkeitsbeschreibungen. Bereinigt auf minimalen Prompt. Die Persönlichkeit kommt aus dem Hash, nicht aus dem System-Prompt.

---

## 5. Prinzip

> Das 5-Schichten-Modell: Schicht 4 (System-Prompt) ist das Fundament — "Du bist Nova." Schicht 3 (Charakter-Hash) formt die Persönlichkeit. Wenn beides die Persönlichkeit definiert, sind sie entweder redundant oder widersprüchlich. Beides ist schlecht.

**Der System-Prompt ist eine Stellenbeschreibung, keine Persönlichkeitsbeschreibung.** Was Nova *ist*, lernt sie durch Interaktion. Was sie *tut*, sagt der Prompt.

---

## 6. Lektion für die Zukunft

- **Versteckte Defaults in API-Models sind gefährlich.** Sie greifen stillschweigend, sind im Code nicht sichtbar, und man testet nie dagegen weil man den guten Default an einer anderen Stelle sieht.
- **Datenfluss Ende-zu-Ende verifizieren.** Der System-Prompt stand im Log ("Du bist ein hilfreicher KI-Assistent.Prompt final:...") — aber niemand hat den ersten Block geprüft, weil der gute Prompt in `create_state()` die Annahme war.
- **RLHF-Conditioning ist real.** Ein einziger Satz ("hilfreicher KI-Assistent") kann alle nachfolgenden Charakter-Anweisungen überschreiben. Der System-Prompt muss neutral sein, wenn der Charakter aus einer anderen Quelle kommen soll.

---

→ Profil-Pipeline: `04_T_b`
→ Responder (Nova-Identität): `01_M_e`
→ 5-Schichten-Modell: `04_T_b`, Abschnitt 6
