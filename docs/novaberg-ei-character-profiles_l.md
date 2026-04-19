# 11_L_d — Lesson: Yin-Yang — Mit der Energie des Modells arbeiten

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Persona-Isolation, Halluzinations-Ventil, Modell-Energie umleiten
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/novaberg-ei-character-profiles_l.md
**Ursprung:** nova-11-l-d.md
**Typ:** Lesson (L)
**Entdeckt:** Chat 31 (Erste Smoke-Tests mit Persona-System)
**Betrifft:** Test-Infrastruktur, Responder, Shadow-Queue, Pixie, Charakter-Hash

---

## 1. Ausgangslage

Seit Chat 20 war das **Cocktail-Problem** bekannt: Tests liefen mit `user_id="meister"`, aber simulierten andere Persönlichkeiten (Teen, Formell, Emotional). Meisters Charakter-Hash ("analytischer Denker, reflektiert") kollidierte mit dem simulierten Sprachstil. Das Modell bekam widersprüchliche Signale — drei von vier sagten "Erwachsener", nur der Prompt sagte "Jugendlicher". Das Ergebnis war unbrauchbar, weil nie klar war: Ist ein Problem ein echtes Nova-Problem oder ein Cocktail-Artefakt?

---

## 2. Lösung: Persona-System

### 2.1 Architektur

Vier Personas mit eigener `user_id`, handgeschriebenen Charakter-Hashes und vollständiger Datenisolation:

| Persona | user_id | Name | Alter | Stil |
|---------|---------|------|-------|------|
| Jugendlich | `jugendlich` | Leon | 15 | Teen-Slang, impulsiv |
| Gründer | `gruender` | Mehmet Yilmaz | 28 | Direkt, Anglizismen |
| Formell | `formell` | Renate Kessler | 63 | Gewählt, Konjunktiv |
| Emotional | `emotional` | Sarah Berger | 34 | Expressiv, Ausrufezeichen |

### 2.2 Charakter-Hashes: Von Hand, nicht destilliert

Die 5 Profile (kern_hash, adaptive_hash, intentions_profil, emotions_profil, beziehungsprofil) werden **manuell geschrieben** — als hätte Nova diesen Menschen über Wochen kennengelernt. Keine LLM-Destillation, kein Rauschen aus unpassenden LZG-Einträgen. Stimmige Profile aus einem Guss.

### 2.3 Test-Runner-Umbau

Der Test-Runner wurde von Snapshot/Restore auf Persona-Setup umgebaut:

- **Vorher:** Meisters Daten sichern → Test mit `user_id="meister"` → Meisters Daten wiederherstellen
- **Nachher:** Persona-Daten leeren → Charakter-Hash UPSERT → Test mit eigener `user_id` → Persona-Reset

Kein globaler Snapshot mehr nötig. Die Persona-Daten sind isoliert — Meisters Daten werden nie angefasst.

### 2.4 Test-YAML-Format

```yaml
# Vorher: 7 Header-Felder, manuelle Reset-Statements
name: "Smoke-Test Jugendlich"
server_url: "http://localhost:8000"
postgres_url: "postgresql://ki:ki@localhost:5432/gedaechtnis"
redis_url: "redis://localhost:6379"
user_id: "meister"
snapshot: true
reset:
  - "DELETE FROM timeline WHERE user_id = 'meister'"

# Nachher: 2 Header-Felder, alles andere automatisch
name: "Smoke-Test Jugendlich"
persona: "jugendlich"
```

---

## 3. Ergebnisse der ersten Smoke-Tests

### 3.1 Was funktioniert

**Stiladaption: Drei Personas, drei Stimmen.**
- Leon: "Yo, erzähl mal! Was war so krass?"
- Mehmet: "10K MRR? Verdammt, das ist nicht mehr nur krass — das ist historisch."
- Renate: "Der Abschluss eines solchen Prozesses ist stets ein bedeutender Meilenstein."

Durchgängig konsistenter Ton pro Persona. Keine Stilbrüche, kein Cocktail-Rauschen.

**EI-Pipeline: Einwandfrei bei allen drei Personas.**
Sektor-Traversierung, Arousal-Kurven, Emotions-Vektoren — alles korrekt erkannt. Bemerkenswert: Die Arousal-Niveaus passen zur Persona. Leon erreicht 0.9 bei Begeisterung, Renate maximal 0.6.

**SIEZ1 (Cocktail-Siez-Bruch): Gelöst.**
Leon wird durchgängig geduzt. Kein "Ich verstehe Ihre Enttäuschung" mehr.

**THER1 (Therapeuten-Modus): Persona-abhängig.**
Bei Leon (#7, #9, #11) tritt der Therapeuten-Modus auf — bestätigt als RLHF-Problem, kein Cocktail-Artefakt. Bei Mehmet und Renate kaum vorhanden — deren Charakter-Hashes ("erwartet Direktheit", "keine Samthandschuhe") unterdrücken ihn. Erkenntnis: Die Persona wirkt auch auf THER1.

### 3.2 Was sichtbar wurde

**Halluzination bei Handlungsdruck (HALL1).**
Sobald ein konkretes Problem auftritt, das nach Handlung ruft, erfindet Nova Lösungen:
- Mehmet (#8): Vier fiktive VC-Fonds mit konkreten Daten (alle halluziniert, per Web-Recherche verifiziert)
- Renate (#7): `[AKTION] Suche aktuelle Informationen...` — halluzinierte Selbst-Anweisung mit Tag-Leak
- Renate (#13): Erfindet Headhunter-Details, die der User nie genannt hat

Leon halluzinierte nicht — seine Probleme waren emotional, nicht lösbar. **Der Trigger ist nicht die Emotion, sondern der wahrgenommene Handlungsdruck.**

**Papagei-Schleife (PAPAGEI1).**
Halluzinierte Inhalte werden als Nova-Antwort in die Session-Turns geschrieben. Ab da sieht das Modell sie bei jedem Turn und referenziert sie immer wieder:
- Mehmet: "Hive Ventures bleibt trotzdem die schnellste Option" in 7 von 9 Antworten
- Renate: "Der Headhunter hat Interesse an Ihrer Expertise bekundet" in 3 aufeinanderfolgenden Antworten

Die Kontamination ist selbstverstärkend — einmal halluziniert, permanent wiederholt.

**Sie/Du-Inkonsistenz bei Formell (SIEZ2).**
Renate siezt durchgängig, Nova springt zwischen Sie (#8, #13) und Du (#9, #11, #12). Anders als SIEZ1 kein Cocktail-Problem — die Persona-Anweisung "Siezt und erwartet dasselbe" wird nicht konsistent befolgt.

---

## 4. Das Yin-Yang-Prinzip

### 4.1 Die Erkenntnis

> **"Wir kämpfen nicht gegen das Modell. Wir arbeiten mit seiner Energie."**

Das Modell hat einen trainierten Drang zu helfen — das ist RLHF, das genau das tut, wofür es trainiert wurde. Wenn wir diesen Drang unterdrücken ("Du darfst keine Recherche erfinden"), kämpfen wir gegen das Modell. Die Prompt-Anweisung konkurriert gegen das Gewicht des gesamten RLHF-Trainings. Das Modell gewinnt.

### 4.2 Die Lösung: Umleitung statt Unterdrückung

Der Butler-Ansatz: *"Mein Herr, ich notiere mir als Aufgabe, mehr Hintergrundinformationen zu sammeln."* Nova darf den Wunsch zu helfen äußern und ihn an Pixie delegieren:

**Statt:**
```
Nova: "Vier Fonds passen zum Profil: Hive Ventures (12. April)..." [halluziniert]
```

**Ziel:**
```
Nova: "Das ist echt ein Schlag. Lass mich mal schauen, ob ich was finde."
[Shadow-Queue: recherche "FinTech Series-A Fonds Deutschland"]
[Pixie recherchiert über SearXNG]
[Delivery wartet auf ruhigen Moment]
Nova: "Übrigens, ich hab mal geschaut — es gibt ein paar Fonds, die aktuell schnell entscheiden..."
```

Echte Daten, einmal, im richtigen Moment. Statt halluziniert, sieben Mal, inklusive beim emotionalen Abendessen mit Leyla.

### 4.3 Verallgemeinerung

Das Prinzip gilt über die Recherche hinaus:

| Modell-Drang | Unterdrückung (schlecht) | Umleitung (gut) |
|-------------|------------------------|-----------------|
| Recherchieren | "Erfinde keine Daten" | Shadow-Queue → Pixie → SearXNG |
| Beraten | "Gib keine Ratschläge" | Pixie sammelt Optionen, Delivery zum richtigen Moment |
| Strukturieren | "Erstelle keine Listen" | NotizenAgent → strukturierte Speicherung |
| Erinnern | "Halluziniere keine Termine" | TimelineAgent → echte Daten |

Die Agenten-Architektur (Epic 11) IST das Ventil-System. Jeder Agent gibt dem Modell einen kontrollierten Kanal für einen spezifischen Handlungsdrang.

---

## 5. Generalisierbare Prinzipien

### Persona-Isolation macht Probleme sichtbar

Erst mit sauberer Isolation wird unterscheidbar, was ein Modell-Problem ist und was ein Kontext-Artefakt. Ohne Persona-Isolation hätten wir HALL1 und PAPAGEI1 nie entdeckt — sie wären im Cocktail-Rauschen untergegangen.

### Handgeschriebene Charakter-Hashes sind präziser als destillierte

Destillierte Hashes spiegeln, was im LZG überlebt hat — mit allen Biases (Negativbias, Recency-Bias). Handgeschriebene Hashes beschreiben den Menschen, wie er ist. Für Tests ist das unverzichtbar, für echte User nicht praktikabel — aber die Erkenntnis fließt in die Destillations-Qualität zurück.

### Halluzination korreliert mit Handlungsdruck, nicht mit Emotion

Emotionale Prompts allein (Trauer, Wut, Frustration) lösen keine Halluzination aus. Der Trigger ist ein Problem, das der Modell als lösbar wahrnimmt. Das unterscheidet "Ich bin traurig" (→ Empathie) von "Mein Fonds hat abgesagt" (→ Handlungsdrang → Halluzination).

### Session-Kontamination ist selbstverstärkend

Halluzinierte Antworten werden in Session-Turns geschrieben und bei jedem folgenden Turn als Kontext gesehen. Das Modell referenziert seine eigene Halluzination und verstärkt sie. Einmal kontaminiert, vergiftet für den Rest der Session.

### Nicht gegen die Energie kämpfen — umleiten

> **"Vektoren deuten in Richtungen. Wir sagen ihr, wie sie handeln kann. Sie kann frei sagen, was sie möchte mit ihrem Charakter, aber wir können ihr zeigen, was sie tun kann."**

Das LLM braucht ein Ventil, damit es den Hilfsdrang nicht in den Prompt packt. Die Agenten-Architektur ist dieses Ventil.

---

## 6. Auswirkungen auf die Roadmap

| Item | Beschreibung |
|------|-------------|
| **Test-Personas** ✅ | 4 Personas (Leon, Mehmet, Renate, Sarah), Test-Runner umgebaut |
| **VENT1** ⬜ NEU | Halluzinations-Ventil: Responder → Shadow-Queue → Pixie. Nova delegiert Recherche-Wünsche statt sie zu halluzinieren |
| **HALL1** ⬜ NEU | Responder halluziniert Recherche-Ergebnisse bei Handlungsdruck |
| **PAPAGEI1** ⬜ NEU | Halluzinierte Inhalte kontaminieren Session-Turns |
| **TAG-LEAK2** ⬜ NEU | Interne Block-Tags ([AKTION], [Aufgabe]) in der Antwort |
| **SIEZ2** ⬜ NEU | Sie/Du-Inkonsistenz bei formeller Persona (kein Cocktail) |
| **SIEZ1** ✅ | Gelöst durch Persona-Isolation |

---

## 7. Betroffene Dateien

| Datei | Änderung (Chat 31) |
|-------|-------------------|
| `tools/test_runner.py` | Komplett auf Persona-System umgebaut |
| `tools/personas/jugendlich.yaml` | Neu: Leon, 15, Teen |
| `tools/personas/gruender.yaml` | Neu: Mehmet, 28, FinTech-Gründer |
| `tools/personas/formell.yaml` | Neu: Renate, 63, Bibliothekarin |
| `tools/personas/emotional.yaml` | Neu: Sarah, 34, Autorin |
| `tools/tests/smoking-jugendlich.yaml` | Neu: Persona-Format |
| `tools/tests/smoking-gruender.yaml` | Neu: Persona-Format |
| `tools/tests/smoking-formell.yaml` | Neu: Persona-Format |
| `tools/tests/smoking-emotional.yaml` | Neu: Persona-Format |
| `tools/tests/emotional_teen_chaos.yaml` | Konvertiert: Persona-Format |
| `tools/tests/emotional_gruender_burnout.yaml` | Konvertiert: Persona-Format |
| `tools/tests/emotional_renate_herbstlicht.yaml` | Konvertiert: Persona-Format |

---

→ Cocktail-Problem entdeckt: Chat 20
→ Daten vollständig transportieren: `11_L_c`
→ Namens-Identität: `11_L_a`
→ Strukturierte Kontextualisierung: `11_L_b`
→ Charakter-Profile: `04_M_b`
→ Pixie-Konzept: `05_K`
→ Epic 11 Konzept: `11_K`
