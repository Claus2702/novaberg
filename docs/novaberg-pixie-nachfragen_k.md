# Novaberg — NachfragenAgent: die einfühlsame Rückfrage

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Rolle, Auslöser und Sonderstellung des NachfragenAgenten
**Stand:** 27. Juli 2026, Chat 111
**Pfad:** novaberg/docs/novaberg-pixie-nachfragen_k.md
**Typ:** Konzept
**Status:** ⬜ Offen — `PIX-MIG-7`, Agent nicht implementiert
**Verwandt:** `novaberg-pixie.md` §5 · `novaberg-pixie-deepdive_k.md` (Schwester-Agent)

---

## 1. Warum dieses Dokument

Der NachfragenAgent existiert nicht. Sein Auftrag wird aber bereits erzeugt, geroutet und in der Zustellung sonderbehandelt — an vier unabhängigen Stellen im Code, die sich über seine Rolle einig sind, ohne dass sie irgendwo beschrieben wäre.

Das ist die gefährliche Lage: Ein Verhalten ist verdrahtet, aber nicht dokumentiert. Wer eine der vier Stellen ändert, kann die anderen drei nicht kennen. Dieses Dokument hält fest, was **gebaut ist**, und trennt es von dem, was **noch nicht entschieden ist**.

Vorfall, der es ausgelöst hat: Am 27.07.2026 gewann ein `nachfragen`-Auftrag dreimal den Pixie-Heartbeat und scheiterte jedes Mal an der Registry — sechs Minuten, in denen kein anderer Hintergrund-Job drankam.

## 2. Die Rolle

**Nova geht von sich aus auf den Nutzer zu, wenn es ihm schlecht geht.**

Das unterscheidet den Agenten von seinen Geschwistern. Recherche und Vertiefung bringen Inhalt; das Nachfragen bringt Zuwendung. Der Router benennt es in seinem Kommentar als *„einfühlsame Begleitung"*.

## 3. Was gebaut ist

### Auslöser — zwei Intentionen

`memory/kzg.py:80,85` und `agents/kzg/queues.py:18,23` bilden Intentionen auf Shadow-Aufgaben ab:

| Intention | Aufgabe |
|---|---|
| `emotionaler_ausdruck` | `nachfragen` |
| `hilferuf` | `nachfragen` |

Der Eintrag entsteht nur, wenn die Salienz `KZG_SALIENZ_HIGH` erreicht (`novaberg-pixie.md` §3). Ein Nova-Guard verhindert Aufträge für `user_id="nova"` — sonst entstünde eine Rückkopplung, in der sie sich selbst nachfragt.

### Routing — der fallende Verlauf

`services/pixie/router.py:76-78` wählt den Agenten zusätzlich über den Emotions-Vektor:

```python
# Emotionale Vektoren -> Nachfragen (einfuehlsame Begleitung)
if emotions_vektor in ("absturz", "spirale", "einbruch"):
    return "nachfragen"
```

Nicht die momentane Emotion entscheidet, sondern die **Bewegung**: Ein Verlauf, der abstürzt, sich eindreht oder einbricht. Bei allem anderen fällt der Router auf Recherche zurück.

### Sonderstellung in der Zustellung

`services/shadow_delivery.py:86-92` — hier liegt die eigentliche Bedeutung:

```python
if user_emotion == "stress":
    return False                              # gar nichts einbringen
if user_emotion in NEGATIVE_EMOTIONEN:
    return stack_aufgabe == "nachfragen"      # nur Nachfragen erlaubt
```

**Wenn es dem Nutzer schlecht geht, ist das Nachfragen die einzige ungefragte Annäherung, die Nova erlaubt ist.** Keine Recherche, keine Vertiefung, kein Humor. Bei Stress schweigt sie ganz.

Damit trägt der Agent eine Aufgabe, die kein anderer übernehmen kann: Fällt er aus, hat Nova in negativen Phasen **überhaupt keinen** Weg, von sich aus da zu sein. Der Filter lässt dann nichts durch, weil das Einzige, was durchdürfte, nicht existiert.

### Konfiguration

`config.py:930` — `temperature: 0.6`, `max_output_tokens: 1024`. Die Temperatur liegt deutlich über den Analyse-Knoten (0.05–0.1) und über der Verdichtung (0.1). Das ist stimmig: Eine Rückfrage darf nicht schablonenhaft klingen.

## 4. Was nicht entschieden ist

**Was der Agent erzeugt.** Ob eine Frage, eine Beobachtung oder ein bloßes Dasein-Signal — nirgends festgelegt. Die alte Task-Datei `services/shadow_agent/tasks/nachfragen.py` wurde beim Runner-Rückbau gelöscht (Roadmap, Chat 79); ihr Inhalt ist nicht mehr die Vorlage.

**Wann er schweigt.** Der Zustellungsfilter regelt, *ob* etwas rausgeht. Ob der Agent selbst zu dem Schluss kommen darf, dass Nachfragen gerade falsch wäre, ist offen.

**Der Bezug zum Anlass.** Der Auftrag trägt Thema und Kontext des auslösenden KZG-Eintrags. Ob die Rückfrage daran anknüpfen soll („du hattest gestern von … erzählt") oder offen bleibt, ist eine Charakterfrage.

**Der Abstand.** Kein Mechanismus begrenzt heute, wie oft nachgefragt wird. Bei anhaltend negativer Stimmung erzeugt jeder hinreichend saliente Turn einen neuen Auftrag.

Diese vier Punkte sind **nicht abzuleiten** — sie brauchen eine Entscheidung, bevor gebaut wird.

## 5. Ein Befund nebenbei

Ein Queue-Auftrag für einen nicht registrierten Agenten **gewinnt** den Heartbeat und blockiert ihn für drei Durchläufe. Der fehlende Agent ist Roadmap und kein Defekt; die Verdrängung ist einer. Ein Auftrag für einen unbekannten Agenten sollte gar nicht erst gewinnen, sondern beim Einreihen oder spätestens bei der Auswahl aussortiert werden.

Steht in `novaberg-fundliste.md`, 27.07.2026.
