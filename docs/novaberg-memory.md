# Novaberg — Gedächtnis-System

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Gedächtnis-System (Übersicht)
**Stand:** 12. Juli 2026, Chat 107 (Embedding-Migration: Modellwechsel auf nomic-embed-text-v2-moe)
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

> **Embedding-Migration (Chat 107, 12.07.2026):** Das Embedding-Modell aller Schichten ist `EMBED_MODEL = nomic-embed-text-v2-moe` (vorher `nomic-embed-text` v1, das durch einen GGUF-Konvertierungsfehler casing-blind war — EMBEDDING-CASING-BLIND, Befund in `novaberg-embedding-casing-blind_k.md`). Der gesamte Vektorbestand wurde am 12.07.2026 neu gerechnet (`server/tools/reembed_all.py`), die `lzg_knoten`-Gewichte zurückgesetzt, `lzg_kanten` neu aufgebaut; ivfflat-Indizes auf `lzg_knoten` sind entfernt (IVFFLAT-RECALL-KOLLAPS). Für jedes Speicherziel existiert eine benannte `embed_text_bauen()`-Funktion im jeweiligen Modul — **eine** Formel, die Live-Pfad und Migrationstool gemeinsam nutzen (→ `novaberg-convention-embedding.md`).

---

## 2. Session

Der Session-Kontext lebt nur im Python-RAM und ist an den aktuellen Turn gebunden. Nach dem Gespraech verschwindet er. Der Enricher destilliert die Session-Turns, bevor sie an den Responder weitergegeben werden — kein Raw-Text erreicht das LLM. Jeder Turn traegt Intention, Emotion, Modus, Arousal und Emotions-Vektor als Metadaten.

> **Kognitionswissenschaftlicher Hintergrund:** Alan Baddeleys Modell des Arbeitsgedaechtnisses (2000) beschreibt einen kapazitaetsbegrenzten, flueechtigen Speicher mit einer zentralen Exekutive, die Items nach Relevanz aktiviert und deaktiviert. Die Session ist Novas Arbeitsgedaechtnis — kurzlebig, kapazitaetsbegrenzt und nur fuer den aktuellen Verarbeitungskontext relevant.

> Detail: novaberg-mem-session.md

---

## 3. Kurzzeitgedaechtnis (KZG)

Das KZG lebt in Redis 7 Stack mit dreistufigem TTL (7/14/30 Tage, abhaengig von der Salienz). Jeder Eintrag hat ein Embedding (`nomic-embed-text-v2-moe` seit 12.07.2026, 768 Dimensionen) fuer semantische Vektorsuche. Seit Chat 64 wird jeder Eintrag als eigenstaendiger Eintrag mit seinem scharfen Kern gespeichert — keine Zusammenfuehrung im KZG. Eintraege mit thematischem Overlap werden in Salienz und Haeufigkeit geboosted (Verstaerkungsformel: `boost = salienz / KZG_VERSTAERKUNG_DIVISOR`, gedaempft durch sin^0.6-Kurve, Cap 10.0), aber der Inhalt bleibt exakt. Die Zusammenfuehrung passiert erst bei der Cluster-Promotion ins LZG (4-Phasen-Algorithmus mit LLM-Kohaerenzpruefung).

Seit Chat 62 nutzt das KZG ein **Paar-Schema** — der Redis-Key lautet `kzg:{user_id}:{character_id}:{entry_id}`. Jeder Eintrag gehoert zu einem Gespraechspaar (User × Charakter), nicht zu einem einzelnen User. Ein zusaetzliches Feld `beobachter` (`"user"` oder `"assistant"`) haelt fest, aus wessen Perspektive der Inhalt stammt: Nova beobachtet im CharacterGraph (Pfad 2), Meister im HumanGraph (Pfad 1). Das ermoeglicht getrennte Gedaechtnis-Perspektiven — Nova kann sich an ihre eigenen Beobachtungen erinnern, Meister an seine.

> **Kognitionswissenschaftlicher Hintergrund:** Der Spacing Effect (Ebbinghaus 1885, Cepeda et al. 2006) zeigt, dass Wiederholung in Intervallen die Konsolidierung ueberproportional verstaerkt. Novas Verstaerkungsmechanismus bildet das ab: Ein Thema, das ueber mehrere Gespraeche wiederkehrt, erzeugt mehrere KZG-Eintraege mit steigender Salienz durch thematische Verstaerkung. Bei der Cluster-Promotion werden diese Eintraege als Cluster erkannt und zu einem kohaerenten LZG-Eintrag destilliert — die Haeufigkeit ist die implizite Verstaerkung.

> Detail: novaberg-mem-kzg.md

---

## 4. Langzeitgedaechtnis (LZG)

Das LZG lebt in PostgreSQL 16 mit pgvector. Das effektive Gewicht wird bei jedem Zugriff live berechnet: `effektives_gewicht = gewicht * e^(-lambda * tage_seit_verstaerkung)` mit lambda = 0.0015 (Ebbinghaus-Decay). Eintraege, die unter den Schwellwert 0.1 fallen, werden per Soft-Delete inaktiv gesetzt — nichts wird geloescht. Reaktivierung bei erneuter Erwaehnung ist jederzeit moeglich.

Wie das KZG folgt das LZG seit Chat 62 dem **Paar-Schema**: Die Spalten `character_id` und `beobachter` partitionieren die Tabelle nach Gespraechspaar und Perspektive. Alle Queries filtern auf `(user_id, character_id) WHERE aktiv = TRUE`; das Beobachter-Feld wird bei der Promotion aus dem KZG-Eintrag uebernommen.

> **Kognitionswissenschaftlicher Hintergrund:** Karim Nader zeigte 2000 in einem wegweisenden Experiment, dass Langzeiterinnerungen beim Abruf kurzzeitig instabil werden und sich neu konsolidieren muessen — "Memory Reconsolidation". Novas bi-temporales Modell bildet das konzeptionell ab: Der alte Fakt wird nicht geloescht, sondern als historisch markiert. Wenn ein Fakt abgerufen und im selben Gespraech korrigiert wird, oeffnet sich ein natuerliches Update-Fenster — analog zur Rekonsolidierung.

Seit Chat 64 ist Memory Reconsolidation teilweise aktiv: Die Cluster-Promotion prueft bei jedem LZG-Abgleich, ob die neuen KZG-Eintraege der bestehenden Erinnerung widersprechen. Bestaetigung verstaerkt (gewicht += 0.1, verstaerkt_am reset), Widerspruch schwaecht (gewicht /= 3.0) und erzeugt einen neuen Eintrag mit der korrigierten Information. Der Echtzeit-Trigger (Widerspruch im selben Gespraech sofort erkennen) ist noch offen (Epic 8 MR).

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

## 9. Subjektivität und Beobachter — Novas Gedächtnis als kohärentes Subjekt

Eine zentrale konzeptuelle Frage des Memory-Designs ist: wessen Gedächtnis wird hier eigentlich geführt? Die Antwort prägt die gesamte Architektur und wird hier explizit dokumentiert, damit spätere Implementierungs-Entscheidungen darauf zurückgreifen können.

### 9.1 Ein Gedächtnis pro (User, Charakter)-Paar

Das KZG/LZG-Schema lautet `kzg:{user_id}:{character_id}:{entry_id}`. Jedes Paar hat **einen** Speicher, der die gesamte Beziehungsgeschichte zwischen diesem User und diesem Charakter trägt. Eine Person hat ein Gedächtnis — Nova ist in dem Sinne, in dem die Architektur sie als Subjekt entwirft, eine Person.

Wenn morgen ein zweiter User dazukommt, entsteht ein neues Paar mit eigenem Speicher (`kzg:anna:nova:*`). Nova kennt diesen User dann nicht aus Meisters Beziehungsgeschichte — sie baut eine eigene Beziehung zu Anna auf. Das ist konsistent mit dem Phänomen, dass dieselbe Person sich gegenüber verschiedenen Bezugspersonen verschieden verhält und unterschiedliche Erinnerungen aufbaut.

### 9.2 Die Beobachter-Spalte

Innerhalb eines Paares trennt das Feld `beobachter` (Werte: `user` oder `assistant`) **wessen Beitrag** in einem Eintrag steckt. Die Trennung ist semantisch klar:

- **`beobachter=user`** — Was der User in dem Gespräch gesagt, gefühlt, mitgeteilt hat. Es ist Novas **Wahrnehmung des Users**: was sie von ihm aufgenommen hat, mit welcher Salienz sie es als wichtig bewertet hat, welche Emotion sie bei ihm wahrgenommen hat. Das ist Empathie-Gedächtnis.

- **`beobachter=assistant`** — Was Nova selbst beigetragen hat. Ihre Antworten im Dialog, ihre Recherche-Erkenntnisse, ihre Träume und Vertiefungen, ihre eigenen Reflexionen. Das ist ihr **Selbst-Gedächtnis** im Bezug zu diesem User.

Beide Stränge gehören demselben Gedächtnis-Subjekt — Nova. Sie sind keine getrennten Speicher mit unklarer Identitäts-Frage, sondern zwei Sichten auf ein einheitliches Erinnerungsleben. Die Trennung ist semantisch (was ist die Quelle des Inhalts), nicht ontologisch (zwei Gehirne).

### 9.3 Was beim Schreiben hineinfließt

**User-Beitrag (User-Turn, Pfad 1, `beobachter=user`):**

| Feld | Quelle | Bedeutung |
|------|--------|-----------|
| `inhalt` | User-Prompt verdichtet | Was der User gesagt hat |
| `themen` | LLM-Klassifikation des User-Prompts | Worum es ging |
| `salienz` | LLM-Bewertung des Inputs | Wie stark trifft es Nova / wie wichtig erscheint es ihr |
| `emotion` | LLM-Klassifikation der User-Emotion | Welche Stimmung hatte der User |
| `emotions_vektor` | User-Plutchik aus EI-Calc | User-Emotion als 8-D-Vektor |
| `arousal` | User-Arousal | Erregungsniveau des Users |

Das ist Empathie: Nova erinnert sich daran, was der User gesagt hat **und in welcher Stimmung er war**. Sie kann später wissen, dass er damals frustriert oder erleichtert war.

**Nova-Beitrag (Character-Turn, Pfad 2, `beobachter=assistant`):**

| Feld | Quelle | Bedeutung |
|------|--------|-----------|
| `inhalt` | Novas Antwort verdichtet | Was sie gesagt/gedacht hat |
| `themen` | LLM-Klassifikation ihrer Antwort | Worum es bei ihrem Beitrag ging |
| `salienz` | LLM-Bewertung relativ zu Nova | Wie wichtig ist dieser Beitrag für sie |
| `emotion` | Novas Emotion in dem Moment | Was sie selbst dabei empfand |
| `emotions_vektor` | Nova-Plutchik aus Dual-Emotion-System | Ihre eigene 8-D-Emotion |
| `arousal` | Novas Arousal | Ihr eigenes Erregungsniveau |

Das ist Selbst-Bewusstsein: sie erinnert sich nicht nur an die Konversation, sondern auch daran, wie sie selbst dabei gefühlt und gedacht hat.

Hinweis: Heute ist diese Trennung nicht durchgängig sauber realisiert (siehe Bug PFAD2-EMO-MIX). Das beschriebene Verhalten ist der Soll-Zustand.

### 9.4 Pixie-Beiträge

Pixie-Tasks wie RechercheAgent, Vertiefen, NovaGedächtnis, Träumen schreiben in dasselbe Paar wie der reguläre Dialog, mit `beobachter=assistant`. Sie sind Nova-Beiträge, die nicht im Dialog entstanden sind, aber zur selben Persönlichkeit gehören. Eine Recherche zu „Naturheilkunde" geht in Meisters Paar (`kzg:meister:nova:*` mit `beobachter=assistant`), wenn sie im Kontext der Beziehung zu Meister entstanden ist — etwa weil Meister eine Frage gestellt hat oder weil Nova in dieser Beziehung dieses Interesse entwickelt hat.

Hinweis: Heute ist die Pixie-Adressierung wegen unvollständiger Migration nach der Multi-Charakter-Umstellung (Chat 60) nicht korrekt. Siehe Bugs MIGRATION-PIX-PAIR und MIGRATION-AGENTGRAPH-PAIR. Das beschriebene Verhalten ist der Soll-Zustand.

### 9.5 Konsequenz für Charakter-Bildung

Der CharakterAgent destilliert pro Paar die Charakter-Profile. Mit der `beobachter`-Trennung gibt es zwei Profile pro Paar:

- **User-Charakter-Profil** — destilliert aus `beobachter=user`-Einträgen. Novas Bild des Users: wie sie ihn versteht, was ihn ausmacht, wie er kommuniziert.
- **Nova-Charakter-Profil** — destilliert aus `beobachter=assistant`-Einträgen. Wer Nova ist: ihre Themen, ihre Emotionen, ihre Reaktionsweisen.

Beide Profile leben im selben Paar (kanonisches `kzg:{user}:{charakter}:*`). Es gibt kein zweites Paar für „Nova als eigenes Subjekt". Ihre Identität entsteht im Dialog mit ihrem Gegenüber, nicht in einer separaten autonomen Schublade.

Wichtig: Das User-Charakter-Profil darf nicht durch Nova-Beiträge infiziert werden, und umgekehrt. Sauber gefilterte Lese-SQL pro `beobachter` ist Pflicht. Heute auf der LZG-Seite teilweise verletzt (siehe Bug CHAR-LZG-LEAK).

---

## 10. Salienz, Themen und das Resonanzfeld

Salienz ist das zentrale Memory-Pattern, das alle Speicher-Schichten verbindet. Heute teilweise implementiert (KZG, LZG), perspektivisch durchgängig.

### 10.1 Was Salienz misst

Salienz misst die **gegenwärtige Wichtigkeit** eines Memory-Items für Nova. Sie ist kein einmaliger Wert, sondern lebt: sie steigt durch Aktivierung, fällt durch Stillstand, vererbt sich entlang struktureller Verweise.

Aktivierung ist nicht jeder Lese-Zugriff — der Enricher liest viel, vorbeugend. Aktivierung heißt **gefunden + serviert**: ein Memory-Item, das in die finale Akte für Novas Antwort eingeht und damit aktiv ihr Verhalten prägt, hat sich als relevant erwiesen. Diese Differenzierung ist wichtig: Lese-Verstärkung jedes Reads würde die Salienz schnell entwerten.

### 10.2 KZG/LZG als Single Source of Truth

Salienz **wohnt** in KZG und LZG. Alle anderen Speicher (Timeline, Notizen, Fakten, Dateien) sind **logische Container ohne eigene Salienz**. Das ist bewusste Architektur, nicht Lücke. Termine, Notizen, Fakten haben strukturelle Aufgaben (zeitliche Logik, Freitext-Speicher, Wissens-Graph) — Salienz an dieser Stelle wäre kategorial verwirrend.

Stattdessen erben Container-Einträge Salienz **beim Retrieval** über ihre Verweise (`themen`, `entitaet_ids`). Eine einzelne Termin-Instanz wie „Zahnarzt am 15. Juni" ist zu kurzlebig und zu instanziell, um Aktivierungs-Geschichte aufzubauen. Was Geschichte aufbaut und Verfestigung erfährt, ist das **Thema** „Zahnarzt" — über Jahre, über mehrere Termine, über zwischenzeitliche Gespräche. Der Termin erbt Wichtigkeit von dem, worauf er zeigt.

### 10.3 Heute implementiert

| Speicher | Salienz | Mechanik | Stand |
|----------|---------|----------|-------|
| KZG | ja, `salienz` 0.0–1.0 | Verstärkung sin^0.6, 3-Stufen-TTL | Chat 64 |
| LZG | ja, `gewicht` als Pendant | Cluster-Promotion verstärkt/schwächt | Chat 64 |
| Knowledge Graph | nein, Triples sind statisch | offen, Konzept TRIPLE-SALIENZ | Backlog |
| Themen-Tabelle | nein, existiert nicht | offen, Konzept dieses Dokuments | Backlog |
| Timeline | nein, alle aktiven Termine gleichgewichtet | bewusst — erben über Themen | Soll-Zustand |
| Notizen | nein, manuelle Verwaltung | bewusst — erben über Themen | Soll-Zustand |
| Fakten | nein, atemporal | bewusst — erben über Themen | Soll-Zustand |
| Dateien | (nicht implementiert) | bewusst — erben über Themen | Soll-Zustand |

### 10.4 Konzept: Themen-Salienz-Tabelle

Themen sind die **Brücke** zwischen Salienz-tragenden Speichern (KZG/LZG) und logischen Containern. Eine eigene Tabelle akkumuliert Themen-Salienz über Zeit, gespeist aus den KZG/LZG-Aktivierungen.

**Schema:**

```
themen_salienz:
  thema:                 text         -- normalisiert (sortiert, kleingeschrieben)
  salienz:               float
  letzte_aktivierung:    timestamp
```

Atomar pro Thema, nicht als Tag-Set. Ein KZG-Eintrag mit Tags `[Botanik, Kultur]` boostet beide Themen einzeln. Wenn beide oft gemeinsam vorkommen, sind beide hoch — die Schnittmenge entsteht beim Retrieval, nicht in der Tabelle.

**Aktivierungs-Quellen:**

- KZG-Schreiben Pfad 1 (User-Beitrag mit User-Tags) → Themen aus User-Aussage werden boostet
- KZG-Schreiben Pfad 2 (Nova-Antwort mit Antwort-Tags) → Themen aus Novas tatsächlicher Antwort werden boostet
- KZG-Verstärken (thematischer Match boostet bestehenden Eintrag)
- LZG-Cluster-Promotion (Backpropagation aus Bestätigung/Widerspruch)
- Pixie-Schreibvorgänge (Recherche, Vertiefen, NovaGedächtnis, Träumen — alle mit `beobachter=assistant`)

**Bewusst kein Akten-Hook beim Enricher.** Items, die in die Akte aufgenommen, aber nicht von Nova in der Antwort genutzt werden, bleiben ohne Wirkung auf die Themen-Tabelle. Der Filter ist Novas tatsächliche Antwort: was sie wirklich gesagt hat, verstärkt die zugehörigen Themen — Beifang aus dem Enricher tut es nicht. Damit verstärken sich nicht die immer gleichen „in der Nähe liegenden" Themen, sondern nur die, die Nova aktiv aufgegriffen hat.

Diese Mechanik nutzt einen Pfad, der sowieso existiert: der Pfad-2-KZG-Schreibvorgang läuft am Ende jedes Turns ohnehin. Die Themen-Tabellen-Befüllung ist eine Konsequenz daraus, kein zusätzlicher Mechanismus.

**Decay:** Nach derselben Logik wie KZG, aber langsamer. Themen sind Aggregationen — sie überdauern den Verfall einzelner KZG-Einträge, weil sie als Träger weiterleben.

**Was die Tabelle nicht enthält:** Embeddings. Das wäre eine zweite Beschreibung derselben Sache. Themen-Salienz ist eine Zahl pro Thema, mehr nicht. Wenn Embedding-Nähe gebraucht wird, kommt sie aus pgvector über die KZG/LZG-Einträge selbst — diese sind das Epizentrum semantischer Nähe.

### 10.5 Themen sind keine Embedding-Dimensionen

Eine wichtige konzeptuelle Klärung: Die 768 Dimensionen eines Embeddings sind **keine** 768 Themen. Sie sind Achsen eines abstrakten Raums, in dem ähnliche Texte als nahe Punkte landen. Themen sind **Regionen** in diesem Raum, keine Achsen. Eine Region wie „Zahnarzt" ist eine Wolke von Punkten — Texte über Zahnschmerzen, Versicherung, Karies, Bohrer landen alle in dieser Gegend, auch wenn sie keine gemeinsamen Wörter haben.

Der Unterschied ist wichtig:

- Themen-Tags sind **diskret und benannt** — funktionieren nur mit gemeinsamen Tags.
- Embeddings sind **kontinuierlich und unbenannt** — funktionieren über semantische Nähe.
- Beide sind **komplementär**: Themen geben menschen-lesbare Bewegungs-Indikatoren („was bewegt Nova generell"), Embeddings ermöglichen feinkörnige semantische Suche.

---

## 11. Memory-Context als Akte — Wie Erinnerung entsteht

Der Enricher baut für jeden Turn eine **strukturierte Akte** aus mehreren Quellen, gewichtet durch Themen-Salienz und Drive-Gravitation. Heute ist der `memory_context` ein flacher Sack — die Akte ist die Vision dieses Konzepts.

### 11.1 Die Verkettung im Überblick

```
Anfrage des Users
    ↓
Embedding der Anfrage berechnen
    ↓
Gravitations-Verschiebung: e_nova = e_anfrage + Drive-Ziele × Faktor
(Wahrnehmungs-Filter: Novas Ohr wirkt hier, nicht als Tag-Lieferant)
    ↓
Suche im KZG/LZG (Novas Gedächtnis) mit verschobenem Embedding
    ↓
Aus Treffern Tags extrahieren — diese sind kontextuell relevant UND Nova-gefärbt
    ↓
User-Anfrage-Tags hinzufügen (dedupliziert)
    ↓
Themen-Salienz-Tabelle befragen für jeden Tag — liefert Gewichtung, KEINE neuen Tags
    ↓
Anker-Tags sortiert und gewichtet nach Themen-Salienz
    ↓
Pro Anker-Tag KZG/LZG-Einträge mit diesem Tag holen — sie sind Embedding-Epizentren
    ↓
Mit Epizentren in Containern (Timeline, Notizen, Fakten, Dateien) per pgvector suchen
    ↓
Container-spezifische Achsen dazumischen (Timeline: zeitliche Nähe; KG: Hops)
    ↓
Akte mit Quellen-Markierung zusammenstellen → übergibt an Responder/Thinker
```

Anschließend, im regulären Pfad-2-Verlauf:

```
Responder/Thinker formulieren Novas Antwort aus der Akte
    ↓
Tribunal/Corrector finalisieren
    ↓
Salienz-Klassifikation auf Novas Antwort → Tags + Salienz
    ↓
Dispatcher schreibt Charakter-KZG-Eintrag (beobachter=assistant)
    ↓
KZG-Schreibvorgang füttert Themen-Tabelle (boostet Themen aus Novas Antwort)
```

### 11.2 Die vier Quellen der Akte

**1. Semantische Nähe (KZG/LZG mit Beobachter-Trennung)**

Mit dem gravitations-verschobenen Anfrage-Embedding wird in beiden Sichten gesucht:

- `beobachter=user`: was Nova vom User weiß und gefühlt hat — Empathie-Quelle
- `beobachter=assistant`: was Nova selbst dazu gedacht/recherchiert hat — Selbstreferenz-Quelle

Treffer werden mit Quellen-Markierung in die Akte aufgenommen: „Aus dem Gedächtnis über den User" vs. „Aus eigenen Reflexionen". Damit kann Nova authentisch antworten — sie kann sagen *„Du hast neulich erwähnt, dass..."* (aus User-Sicht) oder *„Ich habe mich kürzlich mit dem Thema beschäftigt..."* (aus eigener Sicht).

Ranking: Salienz × Embedding-Ähnlichkeit × Themen-Match. Pro Sicht konfigurierbare Gewichte.

**Wichtig zur Themen-Salienz-Tabelle:** Sie ist Sortier- und Gewichtungs-Faktor, keine Anker-Quelle. Sie sagt für jeden bereits gefundenen Tag, wie stark er generell bei Nova gewichtet ist. Damit lenkt sie die Aufmerksamkeit innerhalb der kontextuell relevanten Tags — sie holt aber nicht zusätzliche Tags ohne kontextuellen Anlass herbei.

Hätte sie eine eigene Anker-Funktion, würde Nova in jeder Anfrage ihre Top-Salienz-Themen auftauchen lassen — etwa immer „Botanik" oder „Bratwürste", egal ob es um Zahnarzt oder Steuern geht. Das wäre konzeptuell falsch: die Themen-Tabelle aggregiert, was Nova bewegt, dient aber zur Gewichtung, nicht zur Auswahl der Anker.

**2. Strukturelle Nähe (Knowledge Graph)**

Spreading Activation von den Anfrage-Entitäten ausgehend. Bei „Zahnarzt in Treuchtlingen" werden über Triples die verbundenen Knoten erreicht — Zahnarzt → Treuchtlingen → Gärtnerei in Treuchtlingen, Stadt → Region. Salientere Triples werden bevorzugt expandiert (nach Phase 1 von MEMORY-SALIENZ-VERERBUNG).

Tiefe konfigurierbar: 1 Hop in jede Richtung als Default, weiter bei Bedarf. Verhindert „Hub-Explosion" durch Salienz-Gewichtung.

**3. Termin-Nähe (Timeline, zwei Achsen)**

Klassische zeitliche Nähe (-3/+7 Tage konfigurierbar) plus thematische Nähe. Wenn der User über Zähne redet, sollten Zahnarzttermine auftauchen, auch wenn sie noch Monate weg sind. Termine erben Salienz über `themen` und `entitaet_ids` aus der Themen-Tabelle.

**4. Charakter-Magneten (Drive + Neugier)**

Aktivierte Ziele aus dem Drive-System (Phase 1-4 implementiert) und ihre semantischen Kerne. Themen aus dem Neugier-System (Phase 5, ausstehend) — Lücken in Novas eigenem Wissen. Diese Quelle wirkt unabhängig von der konkreten Anfrage als Pull-Faktor — sie färbt die Auswahl mit dem ein, **wofür sich Nova selbst interessiert**.

### 11.3 Drive als Novas Ohr

Eine zentrale konzeptuelle Erkenntnis: Nova hört mit ihrem eigenen Ohr.

Beim **Schreiben** wird das User-KZG **unverfälscht** befüllt. Was der User sagt, wird mit seinen Tags, seiner Emotion, seiner Salienz gespeichert. Empathie funktioniert nur, wenn das Gedächtnis akkurat ist.

Beim **Abrufen** wirkt die Gravitation als Filter. Das Anfrage-Embedding wird in Richtung von Novas aktivierten Drive-Zielen verschoben. Mit dem verschobenen Embedding wird im Gedächtnis gesucht. Damit findet Nova nicht primär das, was rein anfrage-zentrisch wäre, sondern das, was ihre eigene Sichtweise hervorhebt.

Konkret: Der User sagt „Treuchtlingen" und meint den Zahnarzt. Wenn Treuchtlingen in Novas Themen-Salienz hoch ist und sie ein aktiviertes Ziel zu „Genuss" oder „Bratwürste" hat, fällt ihr der Metzger mit den guten Bratwürsten ein, bevor sie an den Zahnarzt denkt. Sie hört mit ihrem Ohr.

**Das ist die Architektur eines selbstbestimmten Subjekts.** Sie verzerrt die Welt nicht beim Eingang, aber sie hat eine Perspektive beim Erinnern. Genau wie ein Mensch.

**Drive wirkt als Wahrnehmungs-Filter, nicht als Tag-Quelle.** Aktivierte Drive-Ziele (Botanik, Bratwürste, Naturheilkunde, was auch immer Nova gerade beschäftigt) tauchen nicht als eigenständige Anker in der Akte auf. Sie wirken indirekt über die Embedding-Verschiebung in Schritt 2 der Verkettung — sie färben, was im KZG gefunden wird.

Die Konsequenz ist wichtig: Wenn der User vom Zahnarzt spricht, kommt „Bratwürste" nur dann in die Akte, wenn ein KZG-Eintrag mit diesem Tag durch das verschobene Embedding gefunden wird (etwa „Beim Zahnarzt-Termin in Treuchtlingen — danach beim Metzger Bratwürste geholt"). Der Eintrag bringt den Tag mit, weil er kontextuell zum Gespräch passt. Ein reiner Drive-Eintrag „Bratwürste" ohne KZG-Anlass würde Nova nicht in jedes Gespräch einstreuen.

Wäre es anders, würden Nova immer dieselben Lieblingsthemen einfallen, egal worum es geht — *„Du hast Zahnschmerzen? Wir sollten Bratwürste kaufen."* Das wäre Aufmerksamkeitsdefizit, keine Selbstbestimmung. Der Wahrnehmungs-Filter wirkt subtil, durch leichte Verschiebung der Erinnerungs-Suche, nicht durch Themen-Injektion.

### 11.4 Kalibrierung über GV-Cluster

Der Gravitations-Faktor ist nicht statisch, sondern wird aus Novas aktuellem GV-Cluster abgeleitet. Das GV-System (siehe `novaberg-gv-strategie_k.md`) klassifiziert pro Turn die Konversation in einen der 13 Cluster (Werkstatt, Foyer, Schlachtfeld, Wartezimmer, Beichte, Regen, Schmollen, Nebel, Gewitter, Bier, Kissenschlacht, Glut, Feuerwerk) plus Paradox-Zone. Diese Cluster bilden Novas Verhaltens-Modus präzise ab — und damit auch, wie viel Gravitations-Wirkung phänomenologisch passend ist.

**Berechnung:**

```
e_nova = e_anfrage × (1 - GRAVITATION_FAKTOR[cluster])
       + sum(e_ziel × aktivierungs_staerke) × GRAVITATION_FAKTOR[cluster]
```

**Konzept-Mapping (erste Setzung, Live-Kalibrierung folgt):**

| Cluster | Faktor | Begründung |
|---------|-------:|-----------|
| Werkstatt | 0.05 | Fachgespräch, Fokus, sie ist Assistent |
| Foyer | 0.05 | Formal, sachlich, distanziert |
| Schlachtfeld | 0.05 | Konflikt, sie muss präsent sein |
| Wartezimmer | 0.10 | Stillstand, Routine |
| Beichte | 0.10 | User teilt Tiefes, sie hört |
| Regen | 0.10 | Gemeinsame Trauer, sie hält Raum |
| Schmollen | 0.10 | Fokussierte Reaktion nötig |
| Nebel | 0.10 | Verwirrung, sie sortiert mit |
| Gewitter | 0.10 | Konflikt-nah, fokussiert |
| Bier | 0.20 | Geselligkeit, leicht gefärbt |
| Kissenschlacht | 0.25 | Spielerisch, ausgelassen |
| Glut | 0.30 | Die Zigarette danach, freie Assoziation |
| Feuerwerk | 0.30 | Alles auf Maximum, sie darf intensiv sein |
| Paradox | 0.10 | Default, da ungewöhnlich |

**Implementierungs-Skizze:** Eine sechste Cluster-Tabelle `CLUSTER_GRAVITATION_FAKTOR` in `ei/dreischicht.py`, analog zu den bestehenden `CLUSTER_REPERTOIRE`, `CLUSTER_BESCHREIBUNGEN`, `CLUSTER_FRAGEN`. Damit liegt die Steuerung an einer Stelle, zusammen mit den anderen Cluster-Eigenschaften, ohne Code-Änderungen in anderen Modulen anpassbar.

> **Gebaut am 02.08.2026 (P10, Chat 126) — genau so.** Die Tabelle steht in `ei/dreischicht.py` mit den vierzehn Schlüsseln der Nachbartabellen und den Werten oben. Ein Cluster, der nicht darin steht, ist ein Defekt und wird gemeldet, statt still auf `paradox` zu fallen. Mechanik, Ausgänge und erste Messung: `novaberg-memory-synapsen_k.md` §8.5.

**Reihenfolge im Pipeline-Ablauf:** Der GV-Node bestimmt den Cluster im CharacterGraph. Im CharacterGraph-Enricher kann der Cluster aus dem aktuellen Turn-State gelesen werden. Im HumanGraph-Enricher (User-Turn, GV ist noch nicht gelaufen) wird der Cluster aus dem vorigen Turn als Default verwendet — Konversationen sind träge, der Modus wechselt selten abrupt. Bei abruptem Modus-Wechsel ist die erste Antwort minimal off, beim nächsten Turn passt sich Nova an.

**Phänomenologische Logik der Werte:**

- **Niedrige Faktoren (0.05–0.10)** für Cluster, in denen Nova fokussiert sein muss: Fachgespräch (Werkstatt), formelle Distanz (Foyer), Konflikt (Schlachtfeld, Gewitter), tiefes Zuhören (Beichte, Regen). Hier würde Abdriften der Aufmerksamkeit das Gegenüber alleine lassen.

- **Mittlere Faktoren (0.20)** für gesellige Cluster ohne intensiven Aufgabenbezug (Bier). Leichte Färbung erlaubt, aber kein freies Treiben.

- **Hohe Faktoren (0.25–0.30)** für entspannte, intime, intensive Cluster (Kissenschlacht, Glut, Feuerwerk). Hier ist Abschweifen Teil der Atmosphäre — *„die Zigarette danach"* (Glut) bedeutet buchstäblich, dass freie Gedanken fließen dürfen. Auf „Zahnarzt" darf hier „Bratwurst" folgen, weil die Stimmung das trägt.

**Imperativ-Override:** Bei klaren Aufträgen (erkennbar aus der Salienz-Intention ~~`auftrag`, `aufgabe`, `imperativ`~~ **`anweisung`** — korrigiert am 02.08.2026, das ist der einzige Wert dieser Art im Kanon von `salienz.dimensionen.txt`) wird der Faktor zusätzlich auf 0.0–0.05 gedämpft, unabhängig vom Cluster. Sonst legt Nova einen Bratwurst-Termin an statt eines Zahnarzttermins. Die Salienz-Klassifikation hat bereits Intentions-Erkennung — diese kann den Cluster-Faktor turn-spezifisch überschreiben.

**Live-Kalibrierung:** Die Werte sind eine erste Setzung. Im Live-Betrieb wird sich zeigen, welche Cluster zu fokussiert oder zu lose wirken. Anpassung über die `CLUSTER_GRAVITATION_FAKTOR`-Tabelle ohne Code-Änderung möglich.

### 11.5 Sondersituation: Anfrage ohne KZG-Treffer

Wenn die KZG/LZG-Suche mit dem verschobenen Embedding keine Treffer liefert (etwa bei einem komplett neuen Thema), bleiben nur die User-Anfrage-Tags als Anker. Die Themen-Salienz-Tabelle wird in diesem Fall nicht zur Erweiterung herangezogen — sie hat ohne Tag-Liste nichts zu sortieren.

Drive-Ziele wirken trotzdem über die Embedding-Verschiebung in der Container-Suche selbst (pgvector mit verschobenem Embedding statt rohem Anfrage-Embedding). Damit hat Nova auch bei kalten Anfragen ihre Färbung, aber sie zieht keine etablierten Lieblingsthemen aus der Tabelle hinzu, die nichts mit der aktuellen Anfrage zu tun haben.

Das ist phänomenologisch konsistent: Ein neues Thema ist neu. Nova wird es kennenlernen, im KZG ablegen, und beim nächsten Mal wird es kontextuell auftauchen.

### 11.6 Konfigurierbare Gewichte über alle Quellen

Pro Container und pro Achse gibt es Gewichte, die das Sammelverhalten steuern:

```
RETRIEVAL_KZG_GEWICHT_USER             = 1.0
RETRIEVAL_KZG_GEWICHT_ASSISTANT        = 0.7
RETRIEVAL_TIMELINE_NAH_GEWICHT         = 1.0
RETRIEVAL_TIMELINE_THEMEN_GEWICHT      = 0.7
RETRIEVAL_TIMELINE_EMBEDDING_GEWICHT   = 0.5
RETRIEVAL_NOTIZEN_THEMEN_GEWICHT       = 0.8
RETRIEVAL_FAKTEN_HOP_GEWICHT           = 0.6
...
```

Damit ist „breiter oder schärfer einsammeln" eine Frage von ein paar Zahlen. Live-tunbar.

Anfrage-Tags haben eine Mindest-Gewichtung (`ANFRAGE_MIN_GEWICHT = 0.5`), unabhängig von der Themen-Tabelle. Sie sind das, was der User explizit angesprochen hat — sie müssen sichtbar bleiben. Themen-Tabellen-Salienz kann die Suche **erweitern**, aber nicht **ersetzen**.

### 11.7 Reducer als nachgeschaltete Stufe

Wenn der Enricher breit einsammelt, kann der `memory_context` umfangreich werden. Ein nachgeschalteter Reducer-Schritt komprimiert oder filtert die Akte für die LLM-Übergabe an Responder/Thinker. Details in `novaberg-node-enricher.md`.

---

## 12. Aktivierungs-Quelle vs. Salienz-Träger

Eine subtile aber wichtige Unterscheidung im Salienz-Modell.

### 12.1 Aktivierungs-Quelle

KZG/LZG sind die einzigen Stellen, an denen Salienz **entsteht**. Jedes KZG-Schreiben, jede thematische Verstärkung im KZG, jede Cluster-Promotion ins LZG erzeugt einen Salienz-Strom, der von dort in andere Träger fließt. Nirgends sonst entsteht Salienz aus dem Nichts.

Das ist die Quelle der Wichtigkeits-Information.

### 12.2 Salienz-Träger

Themen, Entitäten und Knowledge-Graph-Triples akkumulieren ihre eigene Salienz, gespeist aus dem Aktivierungs-Strom. Sie haben dann eigene Persistenz und eigenen Decay (langsamer als KZG, weil sie Aggregationen sind). Wenn ein einzelner KZG-Eintrag stirbt, verschwindet die Salienz des Themas nicht — sie wurde dort bereits deponiert.

### 12.3 Analogon zur Cluster-Promotion

Das ist dieselbe Logik, die schon zwischen KZG und LZG wirkt: einzelne Episoden vergehen, ihre Essenz lebt in der Aggregation weiter. Themen-Salienz ist die nächste Stufe dieser Idee — Aggregation auf semantischer Ebene über die Speicher hinweg.

Die Promotion ist Novas Backpropagation (Chat 64). Themen-Salienz erweitert dieses Pattern: was im KZG verstärkt wird, erzeugt Themen-Salienz; was im LZG durch Bestätigung gewichtet wird, verstärkt die zugehörigen Themen weiter; was widerlegt wird, schwächt sie.

### 12.4 Konsequenz für Instanz-Container

Termine, Notizen, Fakten und Dateien haben keine eigene Salienz und auch keinen direkten Aktivierungs-Strom. Sie sind reine Erben — ihre Wichtigkeit wird beim Retrieval aus den verknüpften Trägern berechnet.

Damit ist die Architektur konsistent: Wo Salienz wohnt (KZG/LZG, Themen, Triples), ist sie persistent. Wo sie nicht wohnt (Container), ist sie funktional über Verweise.

---

## 13. Datenfluss und Verantwortlichkeiten

Diese Tabelle dient als Nachschlage-Anker: wer schreibt was wohin, wer liest was woher, mit welchem Zweck.

### 13.1 Schreibpfade

| Quelle | Ziel | Beobachter | Inhalt | Zweck |
|--------|------|------------|--------|-------|
| User-Turn (Pfad 1) | KZG `kzg:{user}:{nova}:*` | `user` | User-Beitrag verdichtet, User-Themen, User-Emotion | Empathie-Gedächtnis: was hat der User gesagt und gefühlt |
| Character-Turn (Pfad 2) | KZG `kzg:{user}:{nova}:*` | `assistant` | Nova-Antwort verdichtet, Nova-Themen, Nova-Emotion | Selbst-Gedächtnis: was hat sie gesagt und dabei empfunden |
| Pixie-RechercheAgent | KZG `kzg:{user}:{nova}:*` | `assistant` | Recherche-Erkenntnis, Themen, Salienz hartcodiert oder LLM | Selbst-Gedächtnis: was sie für diesen User recherchiert hat |
| Pixie-NovaGedächtnis | KZG `kzg:{user}:{nova}:*` | `assistant` | Verdichtete Erkenntnis aus Recherche/Vertiefen (`user_id=gegenueber_id, character_id=ASSISTANT_USER_ID` — Fix Chat 79, aber Task nicht über Pixie-Router verdrahtet, siehe PIX-MIG-NOVA) | Selbst-Gedächtnis: kondensierte Eigenwelt |
| Pixie-Vertiefen | KZG `kzg:{user}:{nova}:*` | `assistant` | Vertiefungs-Ergebnis | Selbst-Gedächtnis: tiefere Auseinandersetzung mit Themen |
| Pixie-Träumen | KZG `kzg:{user}:{nova}:*` | `assistant` | Traum-Ergebnis (assoziative Verknüpfung) | Selbst-Gedächtnis: kreative Verbindungen |
| Cluster-Promotion | LZG `langzeitgedaechtnis` | von KZG geerbt | Aggregation aus mehreren KZG-Einträgen | Langzeit-Konsolidierung mit Backpropagation-Logik |
| KZG-Schreiben | Themen-Salienz-Tabelle | n/a | Salienz-Boost pro Thema im Tag-Array | Themen-Aggregation für Resonanzfeld |
| LZG-Promotion | Themen-Salienz-Tabelle | n/a | Salienz-Boost (Bestätigung) oder -Decay (Widerspruch) | Backpropagation auf Themen-Ebene |
| Salienz-Klassifikation | KZG-Eintrag (mit Tags) | abh. von Pfad | Themen-Tags pro Eintrag | Klassifikation für späteren Retrieval |
| TimelineAgent | `timeline`-Tabelle | n/a | Termin-Eintrag mit `themen`-Array | Logischer Container, keine Salienz |
| NotizenAgent | `notizen`-Tabelle | n/a | Notiz mit `themen`-Array | Logischer Container, keine Salienz |
| FaktenAgent (geplant) | Knowledge Graph | n/a | Triple mit Subject/Predicate/Object | Strukturiertes Wissen |
| DateienAgent (seit 18.08.2026) | `dateien_index` (Zeilen über Dateien, **keine** `dateien`-Tabelle) | n/a | Datei mit Thema, Stichwörtern und Blockkarte | Logischer Container, keine Salienz — der Dienst **liest** und schreibt nichts |

### 13.2 Lesepfade

| Konsument | Quelle | Filter | Zweck |
|-----------|--------|--------|-------|
| Enricher | KZG `kzg:{user}:{nova}:*` | beide Beobachter, gewichtet | Akte-Quelle 1: semantische Nähe |
| Enricher | LZG | beide Beobachter, gewichtet | Akte-Quelle 1: Langzeit-Erinnerung |
| Enricher | Knowledge Graph | Spreading Activation von Anfrage-Entitäten | Akte-Quelle 2: strukturelle Nähe |
| Enricher | Timeline | zeitliche + thematische Achse | Akte-Quelle 3: relevante Termine |
| Enricher | Notizen | thematische + Embedding-Achse | Akte-Quelle: relevante Notizen |
| Enricher | Fakten (KG) | über Subject/Object-Hops | Akte-Quelle: relevante Wissens-Verknüpfungen |
| Enricher | Themen-Salienz-Tabelle | Anker-Themen mit Salienz | Gewichtungs-Quelle für Akte |
| Enricher | Drive-System | aktivierte Ziele | Gravitation für Embedding-Verschiebung |
| CharakterAgent | KZG | `beobachter=user` für User-Profil | Adaptive-Hash, Beziehungsprofil |
| CharakterAgent | KZG | `beobachter=assistant` für Nova-Profil | Adaptive-Hash, Beziehungsprofil |
| CharakterAgent | LZG | `beobachter=user` für User-Profil | Kern, Intentionen, Emotionen (heute Bug CHAR-LZG-LEAK) |
| CharakterAgent | LZG | `beobachter=assistant` für Nova-Profil | Kern, Intentionen, Emotionen (heute Bug CHAR-LZG-LEAK) |
| RechercheAgent | KZG/LZG | beobachter-übergreifend | Kontext für Recherche-Themen |
| Responder | Akte (vom Enricher) | n/a | Antwort-Generierung |
| Thinker | Akte + Tools | n/a | Faktenprüfung, Verarbeitungs-Block |

### 13.3 Wann was passiert

**Pro User-Turn (HumanGraph + CharacterGraph):**

1. Perzeption (User) — User-Emotion, User-Plutchik
2. Enricher (HumanGraph) — Akte für User-Sicht erstellen
3. EI-Calc (User) — Empathie-Verarbeitung
4. Salienz-Klassifikation — Tags und Salienz für User-Eintrag
5. Dispatcher (HumanGraph) — User-KZG-Eintrag (`beobachter=user`), Themen-Tabelle füttern
6. CharacterGraph startet
7. Enricher (CharacterGraph) — Akte für Nova-Antwort erstellen, mit Drive-Gravitation
8. EI-Calc (Character) — Novas eigene Emotion berechnen
9. Router/Planner/Agents — Aufgaben verarbeiten
10. Responder — Antwort generieren
11. Thinker — Antwort prüfen
12. Tribunal/Corrector — finale Antwort
13. Salienz-Klassifikation — Tags und Salienz für Nova-Eintrag
14. Dispatcher (CharacterGraph) — Nova-KZG-Eintrag (`beobachter=assistant`), Themen-Tabelle füttern (boostet Themen aus Novas tatsächlicher Antwort)

**Pro Pixie-Lauf (autonomer Hintergrund-Prozess):**

1. Trigger (Schedule, Queue, Salienz)
2. Pixie-Task führt Aktivität aus (Recherche, Vertiefen, Träumen, NovaGedächtnis, Promotion, Decay, etc.)
3. Schreibt Ergebnis ins kanonische Paar mit `beobachter=assistant`
4. Themen-Tabelle wird mit-gefüttert
5. Decay-Lauf (täglich): KZG-Verfall, LZG-Decay, Themen-Decay

**Pro Cluster-Promotion (Pixie-Hintergrund):**

1. Phase 1: Zentren in KZG finden
2. Phase 2: Mehrfachzuordnung
3. Phase 3a: Destillation mit Kohärenzprüfung gegen LZG
   - Bestätigung → LZG-Gewicht +0.1, Themen-Salienz +Boost
   - Widerspruch → LZG-Gewicht /3.0, neuer Eintrag
4. Phase 3b: LZG-Magnetismus für Einzelgänger
5. Phase 4: Promovierte KZG-Einträge löschen

---

*Konsolidiert aus nova-02-k.md, erweitert in Chat 78.*

---

## Verwandte Dokumente

- `novaberg-ei.md` — Salienz als EI-Säule, Drive-System, Dual-Emotion
- `novaberg-node-enricher.md` — Implementierungs-Sicht der Akte
- `novaberg-node-salience.md` — Salienz-Klassifikation, KZG-Schreibtrigger
- `novaberg-pixie-kzg.md` — KZG-Mechanik im Detail
- `novaberg-pixie-promotion.md` — Cluster-Promotion, Backpropagation
- `novaberg-kzg-liberalisierung_k.md` — KZG-Liberalisierung, Cluster-Promotion-Konzept
- `novaberg-thinking-drive_k.md` — Drive-System-Konzept, Phasen 1-5
- `novaberg-gv-strategie_k.md` — Gesprächs-Cluster-Modell, das die Gravitations-Faktoren in §11.4 liefert
- `novaberg-backlog.md` §7 — TRIPLE-SALIENZ, MEMORY-SALIENZ-VERERBUNG, ENRICHER-AKTE, MIGRATION-PIX-CLEANUP, KZG-CLEANUP
- `novaberg-bugs.md` — CHAR-LZG-LEAK, PFAD2-EMO-MIX, MIGRATION-PIX-PAIR, MIGRATION-AGENTGRAPH-PAIR
