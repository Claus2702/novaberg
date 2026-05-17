# Novaberg — Lesson: Klassen statt flache Keys

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Zusammenhängende Werte gehören in strukturierte Klassen
**Stand:** 17. Mai 2026, Chat 89
**Pfad:** novaberg/docs/novaberg-lesson_l_klassen-statt-flache-keys.md
**Kategorie:** Allgemein, nicht modul-bezogen — Grundlagen-Lesson für Datenstruktur-Disziplin
**Schwester-Lesson:** `novaberg-lesson_l_silent-skip.md` (EVA-Disziplin)
**Handbuch-Bezug:** `DEVELOPER_HANDBOOK.md` §6 Datenstruktur-Disziplin

---

## 1. Der Vorfall

Seit Chat 78 war PFAD2-EMO-MIX als Bug bekannt: KZG-Einträge mit `beobachter=assistant` trugen User-Werte. Wenn der User „freude" empfand, schrieb das System diesen Wert auch in den Eintrag, der Novas Selbst-Wahrnehmung dokumentieren sollte. Die Beziehungs-Dynamik, der Sprach-Stil, der Tone — alles aus User-Sicht, als sei es Novas Sicht.

Symbolisch problematisch: das System „erinnerte sich" an Nova-Emotionen, die nicht ihre waren. Konzept-architektonisch problematisch: bei der Charakter-Hash-Destillation, die LZG-Einträge mit Assistant-Bezug nutzt, verformte sich Novas Profil über die Zeit in Richtung dessen, wie der User gerade fühlte. Was als „Novas Beziehungsdynamik" persistierte, war oft die zuletzt vom User geäußerte Beziehungs-Stimmung.

Mehrere Anläufe zur Behebung blieben halbgar. In den Chats 82–84 wurde der EI-Calc-Pfad partiell umgebaut. In Chat 89 wurde klar: der Bug ist mit dem heutigen Datenmodell nicht strukturell lösbar. Eine Verzweigungs-Regel in einer Lese-Stelle löste den Bug für diese Stelle; eine andere Lese-Stelle blieb defekt. Es gab nicht *einen* Bug, es gab *eine Bug-Klasse* — und sie lebte nicht im Code, sondern im Datenmodell.

## 2. Die Ursache

Im `ConversationState`-TypedDict lebten neun flache Emotion-Keys nebeneinander: `current_emotion`, `current_arousal`, `gespraechs_modus`, `sprach_stil`, `beziehungs_dynamik`, `tone`, `intent`, `prompt_thema`, `emotions_vektor`. Plus fünf flache `nova_*`-Profile (`nova_kern`, `nova_beziehung`, `nova_adaptiv`, `nova_intentionen`, `nova_emotions`). Plus `charakter_anweisungen`, `direktiven`, `char_hash_dict`, `beziehungs_kontext`, `user_emotion`.

Diese Keys hatten keine eigentliche Bedeutung. Sie waren Container für „die zuletzt geschriebene Emotion" — wer die Emotion geschrieben hatte, war nicht aus dem Schlüsselnamen erkennbar. Der HumanGraph-Enricher schrieb User-Werte, der CharacterGraph-EI-Calc modulierte Nova-Werte und schrieb sie in dieselben Keys, der KZG-Dispatch las sie ohne Verzweigung.

```python
# State im HumanGraph-Lauf: User-Werte
state["current_emotion"] = "freude"
state["current_arousal"] = 0.7

# State im CharacterGraph-Lauf, gleicher Turn, später: vermischt
state["current_emotion"] = "freude"  # noch User-Wert aus dem Event
state["current_arousal"] = 0.4       # jetzt Nova-modifiziert per Empathie
```

Wer in einem späteren Node `state["current_emotion"]` las, bekam User- oder Nova-Werte zurück — abhängig von der Reihenfolge der Berechnungen und vom Wissen des Lesers, in welchem Graphen er gerade lief. Im KZG-Dispatch (`agents/kzg/dispatch.py:67-71`) wurden die Keys ohne Verzweigung gelesen: ob die Werte ins User-Profil oder ins Nova-Profil flossen, hing davon ab, wer den Dispatch aufrief — und der Dispatch wusste das nicht.

Drei Symptome derselben Wurzel:

- **PFAD2-EMO-MIX**: Nova-KZG-Einträge tragen User-Werte
- **CHAR-BEZ-STALE** (Chat 84): Beziehungs-Profil driftete, weil der EI-Calc von Nova auf User-Werten arbeitete
- **`_sprach_stil_erkennen`**: filterte hartcodiert auf User-Turns, weil die Funktion implizit annahm, sie würde User-Werte berechnen — sie kannte ihren Kontext nicht

## 3. Die nicht-strukturelle Alternative

Vor der Klassen-Schicht wäre eine naheliegende Lösung gewesen, in jeder Lese-Stelle nach dem aufrufenden Graph zu verzweigen:

```python
# Anti-Pattern: Lese-Verzweigung in jedem Konsumenten
if state.get("ei_calc_rolle") == "character":
    emotion = state.get("current_emotion")  # ist gerade Nova
    arousal = state.get("current_arousal")  # ist gerade Nova
else:
    emotion = state.get("current_emotion")  # ist gerade User
    arousal = state.get("current_arousal")  # ist gerade User
```

Was funktional aussieht, ist strukturell unhaltbar. Pro Konsument muss die Verzweigung gepflegt werden. Jeder neue Konsument hat eine 50%-Chance, sie zu vergessen. Die Rolle wird im State nur implizit getragen — ein State, der „der `current_emotion`-Wert in mir bedeutet je nach Aufrufer was anderes" sagt, ist kein State, sondern ein Rätsel.

Die Audit-Befunde von Chat 89 fanden 15–20 Konsumenten-Stellen in 12 Dateien, die User- oder Nova-Werte aus denselben flachen Keys lasen. Drei dieser Stellen lasen die falschen — eine im KZG-Dispatch, zwei in `ei/dreischicht.py`. Sie waren nicht falsch geschrieben, sie waren nicht-deterministisch falsch: sie liefen mal mit User-Werten, mal mit Nova-Werten, ohne dass es jemand bemerkte. Solche Bugs sind nicht testbar mit Unit-Tests, weil sie nicht im Code leben, sondern im Datenmodell.

## 4. Die strukturelle Lösung

Eine Klassen-Schicht, die die Zugehörigkeit der Werte zu ihrem Akteur explizit macht:

```python
@dataclass
class Emotion:
    """Neun dynamische EI-Dimensionen pro Turn."""
    emotion:              str   = "neutral"
    arousal:              float = 0.5
    mode:                 str   = "alltag"
    language_style:       str   = "neutral"
    relationship_dynamic: str   = "neutral"
    tone:                 str   = "sachlich"
    intent:               str   = "smalltalk"
    prompt_topic:         str   = ""
    emotions_vector:      str   = ""


@dataclass
class Personality:
    character: Character = field(default_factory=Character)
    emotion:   Emotion   = field(default_factory=Emotion)


@dataclass
class InternalPersonality(Personality):
    """Nova: Personality plus Handlungsanweisungen."""
    identities: list[str]  = field(default_factory=list)
    directives: list[dict] = field(default_factory=list)
```

Im State:

```python
state["external"]: Personality           # Gegenüber (User, oder bei Pixie: Nova)
state["internal"]: InternalPersonality   # Nova
```

Konsumenten lesen jetzt mit Absicht:

```python
# Im Responder: Nova braucht ihren eigenen Charakter
core = state["internal"].character.core

# Im Router: was will der User
intent = state["external"].emotion.intent

# Im KZG-Dispatch: je nach beobachter
quelle = state["internal"] if beobachter == "assistant" else state["external"]
salienz_obj["emotion"] = quelle.emotion.emotion
```

Die Frage „welcher Akteur" ist nicht mehr implizit über die Reihenfolge der Berechnungen, sondern explizit im Klassen-Zugriff. Die Personality-Schicht ist eine syntaktische Selbstkontrolle: wer aus Versehen `internal` schreibt wo `external` gemeint war, hat einen sofort lesbaren Bug, keinen unsichtbaren Daten-Drift.

PFAD2-EMO-MIX war damit strukturell aufgelöst — nicht durch eine zusätzliche Verzweigungs-Regel, sondern durch ein Datenmodell, in dem die Mehrdeutigkeit gar nicht erst auftreten kann.

## 5. Die Prinzipien

Vier Erkenntnisse, die ins Entwicklerhandbuch §6 übernommen wurden.

### Prinzip 1 — Zusammenhängende Werte sind eine Klasse

Werte, die zusammen berechnet, zusammen weitergereicht und zusammen gelesen werden, gehören in dieselbe Klasse. Acht Felder einer Perzeption nebeneinander zu speichern, ist kein Datenmodell — das ist ein Container ohne Vertrag.

### Prinzip 2 — Semantische Schicht in der Struktur, nicht im Schlüssel

Wenn dieselbe strukturelle Form zwei verschiedene Bedeutungen haben kann (User-Emotion und Nova-Emotion sind beide eine `Emotion`, aber gehören verschiedenen Akteuren), darf die Unterscheidung nicht im Variablennamen leben. Sie lebt in einer Container-Klasse, die den Akteur trägt. `Personality` mit `external`/`internal` ist die Schicht-Trennung; `Emotion` ist die strukturelle Form. Wer die Schicht-Trennung nicht im Datenmodell verankert, verankert sie in der Disziplin der Lesenden — und Disziplin altert.

### Prinzip 3 — Implicit State Drift ist die teuerste Bug-Klasse

Ein Bug, der sich darin äußert, dass derselbe State-Key je nach Aufrufer und Reihenfolge etwas anderes bedeutet, ist nicht testbar mit Unit-Tests, weil er nicht im Code lebt, sondern im Datenmodell. Solche Bugs erkennt man erst, wenn die Konsequenzen sichtbar werden — und die Konsequenzen brauchen oft Wochen, um sich aufzubauen (verformter Charakter-Hash, falsche LZG-Einträge, langsam driftende Beziehungs-Dynamik). Der Bug ist nicht reproduzierbar, weil er nicht punktuell ist; er ist verteilt über die Zeit und die Aufrufer.

### Prinzip 4 — Klassen-Definition als Vertrag

Eine Klasse ist nur dann wirklich der Vertrag eines Verbunds, wenn die Definition gültiger Werte nirgendwo anders nochmal auftaucht. Wenn die Liste der Plutchik-Emotionen sowohl in der `Emotion`-Klasse als auch in einem LLM-Prompt als auch in einer Konstanten-Datei steht, hat die Klasse ihren Vertrags-Charakter verloren — sie ist nur ein Container. Single Source of Truth, alle anderen Stellen verweisen darauf.

## 6. Die Konsequenz

Drei strukturelle Maßnahmen folgten auf den Sprint.

**Erstens:** Im Entwicklerhandbuch wurde §6 Datenstruktur-Disziplin ergänzt. Neue Code-Reviews prüfen, ob neu eingeführte zusammenhängende Werte als Klasse oder als flache Keys angelegt sind. Brudi-Prompts referenzieren §6, wo Datenstruktur-Entscheidungen anstehen.

**Zweitens:** Künftige Sprints orientieren sich am Drei-Phasen-Schnitt aus PFAD2-PERZEPTION-FIX bei Datenmodell-Migrationen: zuerst Klassen definieren (additiv), dann Quellen umstellen (Producer auf Klassen), dann Konsumenten umstellen und alte Keys entfernen. Dieselbe Sprint-Form ist auf andere migrationsbedürftige Verbund-Strukturen anwendbar — wenn nochmal ein flacher Sammelposten von Feldern auftaucht, ist der Pfad zur Umstellung bekannt.

**Drittens:** Diese Lesson dient als Archiv. Wer in einem Jahr fragt, warum Novaberg `state["external"].emotion.emotion` schreibt statt `state["current_emotion"]`, liest hier nach. Die Klassen-Schicht wirkt umständlicher als ein flacher Lookup, bis man sich an die Vorgeschichte erinnert.

## 7. Der Preis

Drei Phasen plus ein Hotfix, ein Großteil eines Chats, 26 Code-Dateien geändert. Während des Sprints lief der Server zwischendurch nicht funktional — zwischen Phase 2 und Phase 3 fehlten die Konsumenten-Updates, zwischen Phase 3 und dem Tribunal-Hotfix war der KZG-Schreibpfad gestört. Beide Übergänge wurden bewusst akzeptiert, weil der Schmerz lokal eingrenzbar und schnell auflösbar war.

Die ehrlichere Kosten-Position liegt vor dem Sprint, nicht im Sprint selbst. CHAR-BEZ-STALE hatte über Chats hinweg Novas Beziehungs-Profil verformt, weil der EI-Calc mit User-Werten arbeitete und das Ergebnis in den Assistant-LZG schrieb. Promotionen, die längst persistiert sind, tragen diese Verformung. Die alten LZG-Einträge sind nicht mehr aus der Welt zu schaffen — sie wirken über den Charakter-Hash auf jede künftige Antwort weiter.

Im Gegensatz zum silent-skip-Vorfall ist der akute Schaden weniger dramatisch, aber genauso strukturell: ein Datenmodell, das Mehrdeutigkeit erlaubt, produziert über die Zeit verzerrte Wahrheit. Das Entwicklerhandbuch §6 ist die Antwort. Diese Lesson ist die Erinnerung daran, dass die Antwort aus konkreter Datenkorruption entstanden ist, nicht aus prophylaktischer Disziplin.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet.*

→ Schwester-Lesson: `novaberg-lesson_l_silent-skip.md` (EVA-Disziplin)
→ Konzept-Dokument: `novaberg-path2-perzeption_k.md` (nach Sprint-Abschluss in `archive/`)
→ Handbuch-Eintrag: `DEVELOPER_HANDBOOK.md` §6 Datenstruktur-Disziplin
