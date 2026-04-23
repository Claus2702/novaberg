# Novaberg — Gedächtnis-System

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Gedächtnis-System (Übersicht)
**Stand:** 23. April 2026, Chat 62 (Paar-Schema in KZG/LZG)
**Pfad:** novaberg/docs/novaberg-memory.md
**Quellen:** nova-02-k.md (Gedächtnis-Konzept)

---

## 1. Schichten-Modell

Das Gedächtnis bildet den menschlichen Gedächtnisweg architektonisch nach: Wahrnehmung, Bewertung, Speicherung, Verfall, Verstärkung, Verdichtung, Charakter.

```
┌─────────────────────────────────────────────┐
│  Session           RAM, flüchtig            │
├─────────────────────────────────────────────┤
│  Kurzzeitgedächtnis (KZG)   Redis, TTL      │
├─────────────────────────────────────────────┤
│  Langzeitgedächtnis (LZG)   PostgreSQL      │
├─────────────────────────────────────────────┤
│  Knowledge Graph            Entitäten+Tripel│
├─────────────────────────────────────────────┤
│  Timeline                   Absolute Zeit   │
├─────────────────────────────────────────────┤
│  Notizen                    Freiform        │
└─────────────────────────────────────────────┘
```

Jede Schicht verwendet die Technologie, die ihren Anforderungen am besten entspricht: RAM fuer Fluechtige, Redis fuer TTL-faehiges, PostgreSQL fuer Persistentes. Das Mehrspeichermodell von Atkinson und Shiffrin (1968) und Tulvings Trennung in episodisches und semantisches Gedaechtnis (1972) bilden die wissenschaftliche Grundlage.

---

## 2. Session

Der Session-Kontext lebt nur im Python-RAM und ist an den aktuellen Turn gebunden. Nach dem Gespraech verschwindet er. Der Enricher destilliert die Session-Turns, bevor sie an den Responder weitergegeben werden — kein Raw-Text erreicht das LLM. Jeder Turn traegt Intention, Emotion, Modus, Arousal und Emotions-Vektor als Metadaten.

> **Kognitionswissenschaftlicher Hintergrund:** Alan Baddeleys Modell des Arbeitsgedaechtnisses (2000) beschreibt einen kapazitaetsbegrenzten, flueechtigen Speicher mit einer zentralen Exekutive, die Items nach Relevanz aktiviert und deaktiviert. Die Session ist Novas Arbeitsgedaechtnis — kurzlebig, kapazitaetsbegrenzt und nur fuer den aktuellen Verarbeitungskontext relevant.

> Detail: novaberg-mem-session.md

---

## 3. Kurzzeitgedaechtnis (KZG)

Das KZG lebt in Redis 7 Stack mit TTL (7 oder 30 Tage, abhaengig von der Salienz). Jeder Eintrag hat ein Embedding (nomic-embed-text, 768 Dimensionen) fuer semantische Vektorsuche. Bei erneutem Auftreten desselben Themas (Cosine Similarity >= 0.85) wird der bestehende Eintrag verstaerkt statt dupliziert — das bildet den Spacing Effect ab. Die Verstaerkungsformel: `neues_gewicht = altes_gewicht + (salienz / KZG_VERSTAERKUNG_DIVISOR)`.

Seit Chat 62 nutzt das KZG ein **Paar-Schema** — der Redis-Key lautet `kzg:{user_id}:{character_id}:{entry_id}`. Jeder Eintrag gehoert zu einem Gespraechspaar (User × Charakter), nicht zu einem einzelnen User. Ein zusaetzliches Feld `beobachter` (`"user"` oder `"assistant"`) haelt fest, aus wessen Perspektive der Inhalt stammt: Nova beobachtet im CharacterGraph (Pfad 2), Meister im HumanGraph (Pfad 1). Das ermoeglicht getrennte Gedaechtnis-Perspektiven — Nova kann sich an ihre eigenen Beobachtungen erinnern, Meister an seine.

> **Kognitionswissenschaftlicher Hintergrund:** Der Spacing Effect (Ebbinghaus 1885, Cepeda et al. 2006) zeigt, dass Wiederholung in Intervallen die Konsolidierung ueberproportional verstaerkt. Novas Verstaerkungsmechanismus bildet das ab: Ein Thema, das ueber mehrere Gespraeche hinweg wiederkehrt, gewinnt kontinuierlich an Gewicht — und wird dadurch wahrscheinlicher ins LZG promoviert.

> Detail: novaberg-mem-kzg.md

---

## 4. Langzeitgedaechtnis (LZG)

Das LZG lebt in PostgreSQL 16 mit pgvector. Das effektive Gewicht wird bei jedem Zugriff live berechnet: `effektives_gewicht = gewicht * e^(-lambda * tage_seit_verstaerkung)` mit lambda = 0.0015 (Ebbinghaus-Decay). Eintraege, die unter den Schwellwert 0.1 fallen, werden per Soft-Delete inaktiv gesetzt — nichts wird geloescht. Reaktivierung bei erneuter Erwaehnung ist jederzeit moeglich.

Wie das KZG folgt das LZG seit Chat 62 dem **Paar-Schema**: Die Spalten `character_id` und `beobachter` partitionieren die Tabelle nach Gespraechspaar und Perspektive. Alle Queries filtern auf `(user_id, character_id) WHERE aktiv = TRUE`; das Beobachter-Feld wird bei der Promotion aus dem KZG-Eintrag uebernommen.

> **Kognitionswissenschaftlicher Hintergrund:** Karim Nader zeigte 2000 in einem wegweisenden Experiment, dass Langzeiterinnerungen beim Abruf kurzzeitig instabil werden und sich neu konsolidieren muessen — "Memory Reconsolidation". Novas bi-temporales Modell bildet das konzeptionell ab: Der alte Fakt wird nicht geloescht, sondern als historisch markiert. Wenn ein Fakt abgerufen und im selben Gespraech korrigiert wird, oeffnet sich ein natuerliches Update-Fenster — analog zur Rekonsolidierung.

> Detail: novaberg-mem-lzg.md

---

## 5. Knowledge Graph

Der Knowledge Graph speichert strukturiertes Wissen als Entitaeten (Personen, Orte, Organisationen) und Fakten-Tripel (Subjekt, Attribut, Objekt). Das bi-temporale Modell garantiert, dass kein Fakt ueberschrieben wird: Update bedeutet Invalidieren des alten Fakts (`t_invalid = NOW()`) und Neuanlegen. Die gesamte Historie bleibt erhalten und abfragbar.

> **Kognitionswissenschaftlicher Hintergrund:** Endel Tulving (1972) differenzierte das Langzeitgedaechtnis in episodisches Gedaechtnis (Ereignisse mit zeitlichem Kontext) und semantisches Gedaechtnis (Wissen ohne Zeitbindung). Novas Trennung in Timeline (episodisch) und Knowledge Graph (semantisch) folgt dieser Unterscheidung direkt.

> Detail: novaberg-mem-knowledge-graph.md

---

## 6. Timeline

Die Timeline bildet die absolute Zeitachse ab: Termine, Geburtstage, Ereignisse mit konkreten Datums- und Uhrzeitangaben. Ein 3-Pfade-Zeitparser mit 12 Normalisierungsbloecken (inklusive fraenkischer und norddeutscher Dialektvarianten) wandelt natuerlichsprachliche Zeitausdruecke in exakte Timestamps um. CRUD-Operationen laufen ueber den TimelineManager.

> Detail: novaberg-agent-timeline.md

---

## 7. Notizen

Notizen sind Freiform-Merkzettel, die vom Nutzer explizit angelegt werden: Listen, Snippets, Rezepte, Einkaufslisten. Sie unterliegen keinem automatischen Verfall (kein Ebbinghaus-Decay) und werden manuell verwaltet. Der NotizenManager bietet CRUD-Operationen mit Disambiguierung bei mehrdeutigen Referenzen.

> Detail: novaberg-agent-notes.md

---

## 8. Datenfluss zwischen Schichten

Der Gedaechtnisweg ist strikt sequentiell — es gibt keinen Direktweg ins LZG:

```
User-Nachricht
    |
    v
Perzeption (Salienz-Bewertung 0.0-1.0)
    |
    +-- < 0.5: Ignorieren (Smalltalk, Floskeln)
    +-- 0.5-0.7: KZG-Eintrag (TTL 7 Tage) + Promotion-Queue
    +-- > 0.7: KZG-Eintrag (TTL 30 Tage) + Promotion-Queue
    |
    v
KZG (Verstaerkung bei Wiederholung, Spacing Effect)
    |
    v
Pixie: Promotion (Hintergrund, CPU-Modell, Zwei-Call-Prozess)
    → Klassifizieren, Strukturieren, Verknuepfen — nicht einfach Verschieben
    |
    v
LZG (Ebbinghaus-Decay) + Knowledge Graph (Fakten-Tripel)
    |
    v
Charakter-Destillation (5 Profile: Kern, Adaptiv, Emotionen, Intentions, Beziehung — alle im Prompt genutzt)
```

Die Salienz-Bewertung wird vom LLM geschaetzt und mit Python-Regeln nachkorrigiert: konkrete Personen, Orte und Beziehungen sind immer mindestens 0.70.

> **Kognitionswissenschaftlicher Hintergrund:** James McGaugh (1966) und Yadin Dudai (2004) zeigten, dass Gedaechtniskonsolidierung ein aktiver Prozess ist — das Gehirn sortiert, bewertet und verknuepft im Schlaf. Es ist kein passives Kopieren von "kurz" nach "lang". Novas Zwei-Call-Promotion bildet diese aktive Verarbeitung ab: Klassifizieren, Strukturieren, Verknuepfen.

---

## 9. Prinzipien

**Alles geht zuerst ins KZG.** Kein Bypass, keine Abkuerzung. Der KZG-Eingang ist der einzige Eingangspunkt fuer neue Informationen. Die Promotion ins LZG uebernimmt Pixie im Hintergrund.

**Ebbinghaus-Decay: Verfall ist ein Feature.** Das menschliche Gehirn vergisst, weil Vergessen ein aktiver Filterprozess ist. Novas Decay verhindert, dass das LZG mit Einmal-Erwaehnungen zumuellt wird. Rate 0.0015 bedeutet: einmalig Erwaehntes haelt etwa 3 Jahre.

> **Kognitionswissenschaftlicher Hintergrund:** Hermann Ebbinghaus wies 1885 in "Ueber das Gedaechtnis" nach, dass Erinnerungen exponentiell verblassen. Die Vergessenskurve `R = e^(-t/S)` ist einer der robustesten Befunde der experimentellen Psychologie — ueber 130 Jahre repliziert. Novas Decay-Rate von 0.0015 entspricht einem bewusst sanften Verfall: einmalig Erwaehntes haelt etwa 3 Jahre, bevor es unter den Schwellwert faellt.

**Soft-Delete: Nichts wird geloescht.** Inaktive Eintraege bleiben in der Datenbank. Partial Indexes filtern sie aus Abfragen heraus. Reaktivierung bleibt moeglich.

**Bi-temporales Modell.** Fakten, Timeline und Entitaeten werden nie ueberschrieben, sondern historisch markiert und neu angelegt. Die vollstaendige Historie ist jederzeit abfragbar.

**Berechnung in Python, nicht im LLM.** Decay-Kurven, Verstaerkung, Emotions-Vektoren, effektives Gewicht — alles deterministische Python-Funktionen. Schneller, exakter und reproduzierbar als jede LLM-Berechnung.

---

*Konsolidiert aus nova-02-k.md.*
