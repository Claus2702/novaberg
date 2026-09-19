# Novaberg — Frames (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-thinking-frames_k.md`](novaberg-thinking-frames_k.md) · Bauplan und Umstellung: [`novaberg-thinking-frames_b.md`](novaberg-thinking-frames_b.md) · Diskussion und Ergänzungen: [`novaberg-thinking-frames_e.md`](novaberg-thinking-frames_e.md) · Messungen: keiner. Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 5. Iterative und rekursive Validierung

Sobald ein Frame akut wird, beginnt die Validierung. Sie ist nicht flach, sondern öffnet rekursiv die Frames, die über Slots referenziert werden, und prüft das gesamte Geflecht auf Konsistenz.

### 5.1 Die Reifenwechsel-Diagnose

Konkretes Beispiel, das die Mechanik zeigt:

> *Sprecher in Hamburg sagt: "Ich bringe morgen das Auto zum Reifenwechseln."*

Akute Frames:

1. **Vorgang-Frame** *Reifenwechsel*. Slots: `objekt=Auto`, `zeit=morgen`, `ort=?`, `werkstatt=?`, `reifen_vorhanden=?`.
2. **Objekt-Frame** *Auto* (durch Slot `objekt` aktiviert). Slots: `marke=?`, `standort=?`, `halter=Sprecher`.
3. **Ort-Frame** *Werkstatt* (durch Slot `werkstatt` aktiviert). Slots: `name=?`, `ort=?`, `erreichbarkeit_vom_auto=?`.
4. **Personen-Frame** *Sprecher* (durch impliziten Akteur aktiviert). Slots: `aktueller_aufenthaltsort=?`, `verfügbar_morgen=?`.

Frame-Auflöser zieht aus dem Bestand:

- `Auto.standort` aus Fakten: *Wolferstadt* (Standard-Standort).
- `Sprecher.aktueller_aufenthaltsort` aus letzten Turns / Reisedaten: *Hamburg* (heute angekommen).
- `Werkstatt.name` aus Frame-Lager: häufig *Werkstatt Müller, Wolferstadt* in vorigen Reifenwechsel-Frames.

Plausibilitäts-Test über Frame-Grenzen hinweg:

- `Auto.standort = Wolferstadt`, aber `Werkstatt.ort = Wolferstadt` — passt.
- `Sprecher.aktueller_aufenthaltsort = Hamburg`, aber `Auto.standort = Wolferstadt` — **Konflikt**: Sprecher kann das Auto nicht ohne Weiteres morgen zur Werkstatt bringen.

Das ist nicht ein Slot-Fehler, sondern ein **Cross-Frame-Konflikt**. Eine flache Slot-Erhebung (wie der Chat-80-Stand sie vorsah) würde das nicht entdecken — sie sähe nur, dass `ort` und `werkstatt` rekonstruierbar sind, und liefe durch.

### 5.2 Validierung als rekursive Operation

Schematisch:

```
validiere(frame):
    für jeden slot in frame.slots:
        wenn slot referenziert ein anderes frame:
            sub_frame = aktiviere(slot.referenz)
            validiere(sub_frame)             # rekursiv
            cross_check(frame, sub_frame)    # Konflikte zwischen Frames
        wenn slot ist atomar:
            plausibility_check(slot.wert, slot.constraints)
    plausibility_check(frame als Ganzes)
```

Die Tiefe ist nicht unbegrenzt — pragmatisch reichen 2-3 Ebenen für die meisten Aktivierungen. Die Regel: *aktiv referenzierte* Sub-Frames werden validiert, *bloß genannte* nicht. Bei *"Reifenwechsel morgen"* ist das Reifen-Frame nur genannt, nicht aktiv referenziert — wir prüfen nicht, ob die Reifen ihrerseits einen Lagerort haben, der konsistent ist. Solange der Sprecher nicht *"die Reifen sind in Hamburg"* sagt, bleibt das Reifen-Frame in geringer Akutheit.

### 5.3 Cross-Frame-Konsistenz

Die wichtigste Klasse von Validierungs-Fehlern entsteht zwischen Frames, nicht innerhalb. Beispiele:

- *Sprecher-Standort* vs. *Termin-Ort* (Hamburg-Reifen-Beispiel).
- *Termin-Zeit* vs. *Reise-Zeitraum* (Termin in München während Urlaub auf Mallorca).
- *Anliegen* vs. *Werkzeug-Fähigkeit* (Bitte um Wetterbericht, Werkzeug `web_search` nicht aktiviert).
- *Vorgang-Voraussetzungen* vs. *Bestand* (Backe Kuchen — kein Mehl im Vorrat).

Cross-Frame-Validierung ist genau die Schicht, an der Nova heute systematisch schwach ist. Die einzelnen Agenten arbeiten lokal in ihrem Domänen-Frame, niemand prüft, ob die Frames untereinander passen.

### 5.4 Was bei Konflikt passiert

Konflikt bedeutet nicht zwingend Abbruch. Drei Reaktions-Klassen, je nach Schwere:

**Hart blockierend.** Die Aktion ist physisch oder logisch nicht ausführbar. Sprecher in Hamburg, Auto in Wolferstadt, Werkstatt in Wolferstadt, Reifenwechsel morgen 10 Uhr — das geht nicht. Frame-Auflöser meldet Konflikt zurück, Antwort fragt nach Auflösung: *"Du bist gerade in Hamburg — soll ich einen Termin für nach deiner Rückkehr suchen, oder wird der Wagen anders zur Werkstatt gebracht?"*

**Frage wert, nicht blockierend.** Ungewöhnliche Konstellation, die ein Default-Wert nicht abdecken würde. Reifenwechsel an einem Sonntag — die meisten Werkstätten sind zu, aber es gibt Ausnahmen. Frame-Auflöser meldet als Hinweis, die Antwort kann dezent darauf eingehen: *"Den Sonntag-Termin habe ich notiert — die meisten Werkstätten sind dann zu, ist deine Werkstatt offen?"*

**Plausibel, kein Konflikt.** Der Standardfall. Validierung läuft durch, das Frame ist konsistent, der Vorgang kann angelegt werden.

Die Klassifikation der Konflikt-Schwere ist eine **offene Designfrage** (siehe §11). Eine Heuristik wäre: hart blockierend, wenn ein Slot mit hoher Konsens-Häufigkeit klar widersprochen ist; Frage wert, wenn ein Default unsicher ist.

### 5.5 Reaktionszeitpunkt — Fragen oder Akut warten

Eine zweite offene Designfrage betrifft den Reaktions-*Zeitpunkt*. Gegeben, ein Konflikt ist erkannt — soll Nova sofort reagieren, oder zum Akutheits-Zeitpunkt?

Variante A: **Sofortige Plausibilitäts-Reaktion.** Sprecher sagt heute *"Ich bringe morgen das Auto zur Werkstatt"*, Nova merkt sofort den Standort-Konflikt und antwortet *"Aber du bist in Hamburg…"*. Vorteil: proaktive Beratung, Konflikt früh aufgelöst. Nachteil: kann übergriffig wirken, wenn der Sprecher gerade nur erzählen will.

Variante B: **Aufgeschobene Reaktion zum Akut-Zeitpunkt.** Heute geht der Eintrag durch, morgen früh meldet Nova *"Heute wäre Reifenwechsel — du bist in Hamburg, das passt nicht zusammen"*. Vorteil: weniger aufdringlich. Nachteil: Konflikte werden spät entdeckt, der Termin ist schon im Kalender, möglicherweise wurde was anderes verpasst.

Mein Bauchgefühl, das ich aber nicht hartcoden möchte: Variante A bei Konflikten, die die Durchführbarkeit **blockieren**; Variante B bei Slots, deren Lücke sich später noch schließen lässt. Konflikt-Klassen-abhängige Reaktion, keine globale Regel.

Diese Frage bleibt im Konzept offen und wird in der Implementierungs-Phase pragmatisch entschieden — vermutlich erst, wenn wir ein paar Live-Beispiele beisammen haben.

---

## 6. Plausibilitätsprüfung

Validierung über Slot-Vollständigkeit und Cross-Frame-Konsistenz hinaus gibt es noch eine dritte Operation: die **Plausibilitätsprüfung gegen Weltwissen**. Sie ist die Stelle, an der Frames Constraints tragen, die nicht aus den Daten der Nutzer-Konversation stammen, sondern aus dem allgemeinen Wissen über die Welt.

### 6.1 Konzept

Frames tragen implizit Constraints. Ein Elefant-Frame hat einen Slot *Fortbewegungsart* mit einem Wertebereich, der *gehen, laufen, schwimmen* enthält, aber nicht *fliegen*. Das LLM weiß das aus seinem Training. Wenn jemand sagt *"Mein Elefant ist gestern hergeflogen"*, soll Nova nicht stumm zustimmen, sondern markieren: *Plausibilitäts-Verletzung*.

Wir hardcoden diese Constraints **nicht**. Das wäre der Albtraum-Pfad — eine endlose Tabelle "was ist plausibel". Stattdessen lassen wir das LLM die Plausibilität prüfen, mit dem expliziten Auftrag, gegen sein Weltwissen zu validieren.

### 6.2 Abstufung

Plausibilität ist nicht binär. Vier Stufen, die in der Praxis auftreten:

**Plausibel.** Slot-Wert passt ins Frame, kein Konflikt. *Reifenwechsel im März* — typisch, kein Hinweis nötig.

**Frage wert.** Slot-Wert ist möglich, aber ungewöhnlich. *Reifenwechsel im Juli* — möglich (Reifenkauf, Wechsel auf Neuware), aber atypisch genug, dass eine Rückfrage angemessen wäre. *"Wechseln auf Sommerreifen oder ein Reifenkauf?"*

**Konflikt.** Slot-Wert widerspricht etablierter Erwartung. *Reifenwechsel im November in Mallorca, wo es keine Saisonreifen gibt.* Das ist ein erkennbarer Konflikt — Mallorca-Wissen + Reifensaison-Wissen.

**Unmöglich.** Slot-Wert verletzt grundlegende Welt-Constraints. *Mein Elefant ist hergeflogen.* Hier soll Nova nicht stumm bleiben.

### 6.3 Reaktionsformen

Wie auf jede Stufe reagiert wird, hängt vom Vehicle ab (Beziehungs-Schicht, siehe §10). Das Frame liefert nur den Plausibilitäts-Wert, der Responder formt daraus eine angemessene Antwort. *Plausibel* — keine Reaktion. *Frage wert* — sanfte Rückfrage. *Konflikt* — klärende Bemerkung. *Unmöglich* — direkte Markierung, mit der Möglichkeit, dass es Metapher oder Scherz ist (*"Du meinst sicher, der Elefant kam mit dem Flugzeug?"*).

Wichtig: Plausibilitätsprüfung ist nicht Besserwisserei. Sie ist die Stelle, an der Nova Verstehen demonstriert, indem sie nicht durchwinkt. Aber sie soll dezent sein, nicht belehrend. Die Vehicle-Schicht entscheidet die Form.

### 6.4 Plausibilität als Slot-Eigenschaft

Im Frame-Lager (§9) wird Plausibilität nicht als separates Schema gespeichert, sondern emerge implizit aus der Häufigkeit und Verteilung der beobachteten Slot-Werte. Wenn `Elefant.fortbewegung` in 1000 beobachteten Frames immer eines aus *gehen, laufen, schwimmen* war, wird *fliegen* zu einer Anomalie. Das LLM kann diese Verteilung im Lager nachschlagen — aber meistens reicht sein Trainings-Wissen.

---

## 7. Doppelte Bewegung — LLM-Wissen und Frame-Lager

Aus dem Chat-80-Stand übernommen, im Universal-Kontext etwas ausgeweitet. Frames werden nicht im Code definiert. Sie sind Weltwissen, das das LLM hat. Aber für Nova-spezifisches Lernen brauchen wir einen **zentralen Speicher**, der über das Generelle hinaus die Beobachtungen über *diesen* Nutzer und *seine* Welt sammelt.

### 7.1 Warum eleganter als hardcoded Schemas

| Vergleich | Hardcoded Schema | LLM-Wissen + Frame-Lager |
|---|---|---|
| Neue Frame-Klasse (z.B. *Werkstatt-Termin* spezifisch vs. *Termin* generell) | Code-Änderung nötig | Funktioniert sofort |
| Frame-Variante (z.B. *Geburtstags-Termin* mit zusätzlichem Slot *Geschenk*) | Schema-Erweiterung | Slot wird einfach mit erhoben |
| Domänen-spezifisches Wissen (z.B. *Zahnarzt = meist Zahnreinigung*) | Externer Knowledge Graph | Frame-Lager lernt aus Häufigkeit |
| Selbst-Korrektur (z.B. *Kunde hat doch keinen `wo`-Slot, war Default*) | Manueller Eingriff | Lager passt Konsens an |

### 7.2 Lager als Beobachtungs-Aggregat

Das Frame-Lager sammelt:

- **Welche Frame-Klassen haben wir gesehen?** (Termin, Einkauf, Reifenwechsel, Person *Anna*, Ort *Treuchtlingen*…)
- **Welche Slots werden bei Klasse X typischerweise belegt?** (Bei *Termin* meistens `wer/wo/wann/was`, manchmal `anlass`, selten `kosten`.)
- **Welche Werte tauchen häufig auf?** (Bei `wo` für *Zahnarzt-Termin* dieses Nutzers: *Treuchtlingen*.) `[Herkunft geprüft 19.09.2026: keine realen Personen oder Angaben]`
- **Welche Frame-Verbindungen treten auf?** (Reifenwechsel-Frame öffnet typisch Auto-Frame, das öffnet Standort-Frame.)

Das Lager ist nicht autoritativ. Es zwingt keine Schemas auf. Es **hilft** beim Frame-Auflöser (Defaults rekonstruieren) und beim Plausibilitäts-Test (Anomalien erkennen).

### 7.3 Lernende Eigenschaften

Fünf Lern-Mechanismen, die das Lager nicht statisch lassen:

**Häufigkeits-Aggregation.** Je öfter ein Slot belegt wird, desto mehr "gehört" er zur Frame-Klasse. Ein Termin-Frame mit `wo=null` in 90% der Fälle ist ein Hinweis, dass `wo` für diesen Nutzer nicht kritisch ist (vermutlich Telefontermine oder Routine-Treffen ohne Ortswechsel).

**Wert-Cluster.** Häufige Werte für einen Slot werden zur impliziten Default-Annahme. *Treuchtlingen* bei Zahnarzt-`wo` wird zum Erst-Vorschlag des Auflösers.

**Recency-Gewichtung.** Jüngere Beobachtungen wiegen mehr als ältere. Wenn *Treuchtlingen* in 12 von 14 Zahnarzt-Frames der letzten zwei Jahre vorkommt, aber die letzten drei Beobachtungen in *Donauwörth* waren, soll der Default sich anpassen. Mechanik: zeitlich gewichtete Häufigkeit (linear oder exponentiell), nicht reine Zählung. Das Lager folgt der Realität, ohne dass jemand explizit *"vergiss Treuchtlingen"* sagen muss.

**Korrektur-Gewichtung.** Wenn ein Default-Vorschlag des Auflösers vom Nutzer aktiv korrigiert wird (*"Nicht in Donauwörth, in Treuchtlingen"*), zählt das stärker als eine beiläufige Beobachtung. Korrekturen sind explizite Lehrmomente und sollen entsprechend gewichtet werden — pragmatisch fünf- bis zehnfach im Vergleich zur normalen Häufigkeit. Das macht das Lager schnell-lernend gegen Fehler, ohne dass es bei jeder beiläufigen Erwähnung zappelt.

**Schema-Aggregation.** Über die einzelnen Beobachtungen hinaus pflegt das Lager pro Frame-Klasse einen aggregierten **Schema-Zustand**: welche Slots sind typisch, welche optional, welche Defaults sind aktuell etabliert. Dieser Aggregat-Zustand wird beim Hot-Cache (siehe Cognitive-Pipeline-Dokument §4.11) direkt abgerufen, ohne dass für jede Frame-Aktivierung ein neuer LLM-Call das Slot-Inventar bestimmen muss.

**Decay.** Alte, selten reproduzierte Frame-Klassen verschwinden langsam. Das Schema lebt mit dem Nutzer.

---

> **§8 steht nicht in dieser Datei.** Das Verhältnis von Frames zu Skills ist die tragende Trennung der Absicht und steht in [`novaberg-thinking-frames_k.md`](novaberg-thinking-frames_k.md).

## 9. Frame-Lager — Schema und Operationen

Aus dem Chat-80-Stand übernommen, leicht angepasst an die universale Sicht.

### 9.1 Schema (vorläufig)

```sql
CREATE TABLE frames (
    id              SERIAL PRIMARY KEY,
    user_id         TEXT NOT NULL,
    character_id    TEXT NOT NULL,
    frame_klasse    TEXT NOT NULL,        -- 'anliegen_termin', 'objekt_auto',
                                          -- 'person_anna', 'ort_treuchtlingen',
                                          -- 'vorgang_reifenwechsel', ...
    slots           JSONB NOT NULL,       -- aufgelöste Slot-Belegungen
    quellen         JSONB,                -- pro Slot: prompt|rekonstruiert|default
    haeufigkeit     INTEGER DEFAULT 1,
    erstellt_am     TIMESTAMPTZ DEFAULT NOW(),
    zuletzt_gesehen TIMESTAMPTZ DEFAULT NOW(),
    timeline_id     INTEGER REFERENCES timeline(id) ON DELETE SET NULL,
    notiz_id        INTEGER REFERENCES notizen(id) ON DELETE SET NULL,
    aktiv           BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_frames_klasse      ON frames (user_id, character_id, frame_klasse);
CREATE INDEX idx_frames_zuletzt     ON frames (zuletzt_gesehen DESC);
CREATE INDEX idx_frames_slots_gin   ON frames USING GIN (slots);
```

Paar-skopiert über `(user_id, character_id)` analog zu LZG/Notizen/Timeline (Magneten-Convention §6). Querverweise zu Timeline/Notizen für Re-Identifikation, weil viele Anliegen-Frames dort materialisiert sind. Querverweise zu Knowledge-Graph-Entitäten ergänzbar (zukünftige Erweiterung).

**Hinweis zur Klassen-Konvention:** `frame_klasse` ist ein Präfix-strukturierter String. *anliegen_termin*, *objekt_auto*, *person_anna*, *ort_treuchtlingen* — das Präfix gibt die Frame-Kategorie, der Rest die spezifische Klasse. Das vereinfacht spätere Analysen: alle Anliegen-Frames per `WHERE frame_klasse LIKE 'anliegen_%'`.

> **Hinweis zur Aufteilung (19.09.2026):** Hier stand der *Nachtrag 13.09.2026 — ein Teil des Lagers steht, in Konversationsfassung*. Er berichtet, was gebaut ist und wie es vom Schema oben abweicht, und steht in [`novaberg-thinking-frames_b.md`](novaberg-thinking-frames_b.md), *Aus §9.1*.

### 9.2 Operationen

```python
def frame_registrieren(klasse, slots, quellen, ...) -> int:
    """Legt Frame-Eintrag an. Erhöht Häufigkeit, falls ähnliches Frame existiert.
    Ähnlichkeit über Klasse + Slot-Schlüssel-Übereinstimmung."""

def frame_konsens_holen(klasse) -> dict | None:
    """Aggregiert Konsens für Frame-Klasse mit Recency-Gewichtung:
       - typische Slots (welche werden in >X% der Fälle belegt?)
       - typische Werte (Modus, häufigste Belegung, jüngere stärker gewichtet)
       - durchschnittliche Vollständigkeit
       Korrekturen (siehe frame_korrektur_registrieren) zählen mehrfach."""

def frame_schema_holen(klasse) -> dict | None:
    """Schnellzugriff auf den aggregierten Schema-Zustand pro Klasse:
       - slots_typisch: Liste der Slots, die in >X% der Fälle belegt sind
       - slots_optional: Liste der Slots, die selten, aber regelmäßig auftreten
       - defaults: Dict mit aktuell etablierten Default-Werten pro Slot
       - reife_stufe: 'cold', 'warm', 'hot' anhand Häufigkeit
       Wird vom Cognitive Loop (Pipeline §4.11) für die Cache-Hierarchie genutzt.
       Wenn nicht vorhanden oder nur 'cold': LLM-basierte Slot-Inventarisierung."""

def frame_aehnliche_finden(klasse, slots) -> list[dict]:
    """Findet Frames mit gleicher Klasse und teil-überlappenden Slots.
       Für Rekonstruktion: 'In früheren Zahnarzt-Frames war wo=Treuchtlingen'."""

def frame_korrektur_registrieren(klasse, slot, falscher_wert, korrekter_wert) -> None:
    """Verbucht eine vom Nutzer ausgesprochene Korrektur eines Default-Vorschlags.
       Erhöht das Gewicht des korrekten Werts deutlich (5-10× normale Häufigkeit),
       reduziert das Gewicht des falschen Werts. Triggert ggf. Default-Wechsel im
       Schema-Aggregat."""

def frame_decay() -> int:
    """Decay analog zu LZG: alte, selten gesehene Frames verlieren Gewicht.
       Salienz-inspirierte Decay-Funktion (siehe Memory-Decay-Konzept)."""
```

### 9.3 Verhältnis zum Knowledge Graph

Das Frame-Lager und der Knowledge Graph sind verschiedene Schichten:

| | Frame-Lager | Knowledge Graph |
|---|---|---|
| Granularität | Frame-Schemas mit Slot-Belegungen | Atomare Tripel `(S, P, O)` |
| Lebensdauer | Wachsend, decaybar | Bi-temporal (`valid_from`, `valid_to`) |
| Zweck | Schema-Konsens, Vor-Erfahrung, Plausibilitäts-Basis | Welt-Wissen für Anfragen |
| Schreibtrigger | Frame-Aktivierung im Cognitive Loop | Salienz, Planner, Agent-Push |

Zusammenspiel: Ein neuer Termin-Frame schreibt sowohl ins Frame-Lager (als Schema-Beleg und Quelle für künftige Plausibilitäts-Tests) als auch über den FaktenAgent-Push in den Knowledge Graph (als atomare Tripel).

---
