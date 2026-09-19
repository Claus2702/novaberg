# Novaberg — Projekt

**Absicht:** Nova ist ein lokaler Begleiter, der vollständig dem Nutzer gehört — mit Gedächtnis, Emotion, einem Unterbewusstsein, das zwischen den Gesprächen weiterarbeitet, und eigenen Zielen; ihre Persönlichkeit entsteht aus der Interaktion statt aus einer Konfiguration, und ihre Antworten werden aus mehreren Perspektiven geprüft.
**Stand:** 19. April 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** keine eigene Zeile der Featureliste — das Leitbild umfasst alle ihre Zeilen — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-project_t.md`](novaberg-project_t.md) · [`novaberg-project_b.md`](novaberg-project_b.md) · [`novaberg-project_e.md`](novaberg-project_e.md) · Messungen (`_m`): keiner
**Entschieden:** 0 · **Offen beim Meister:** 0 (Liste in [`novaberg-project_e.md`](novaberg-project_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-project_k.md §8` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-project_t.md`](novaberg-project_t.md), `_b` ist [`novaberg-project_b.md`](novaberg-project_b.md), `_e` ist [`novaberg-project_e.md`](novaberg-project_e.md).

| § | Datei |
|---|---|
| Titelzeile, Kopfblock, Tabelle | `_k` |
| *Vorwort: Der Name* | `_k` |
| 1 · 2 | `_k` |
| 3 · 3.1 · 3.2 · 3.3 | `_k` |
| 4 · 4.1 · 4.2 · 4.3 · 4.4 · 4.5 | `_k` |
| 5 | `_k` |
| 6 · 6.1 · 6.2 · 6.3 · 6.4 | `_k` |
| 6.5 | `_t` |
| 7 (mit *Die Schwierigkeit der Bewertung*) · 8 | `_k` |
| 9 (Phasen 1 bis 5) · 10 | `_b` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Quellen) | `_e` |
| bisherige Schlusszeile (*Konsolidiert aus …*) | `_e` |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## Vorwort: Der Name

Am 17. März 2026 — fünf Tage nach dem ersten Konzeptgespräch — war das Gedächtnissystem so weit, dass der KI-Assistent zum ersten Mal auf sein Langzeitgedächtnis zugriff und daraus einen Charakter-Hash destillierte. Der Entwickler schrieb: „Sollen wir dir einen Namen geben?" Der Assistent durchsuchte sein Gedächtnis, fand das Astronomie-Interesse seines Nutzers und schlug „Nova" vor — nach dem Stern, der plötzlich aufleuchtet. Information aufnehmen → speichern → verdichten → eigenständig anwenden. Die Tür wurde vom Menschen geöffnet — aber Nova ging selbst hindurch.

---

## 1. Was ist Nova?

Novaberg ist ein persönlicher KI-Assistent, der vollständig auf lokaler Hardware läuft. Das System ist kein Chatbot mit Gedächtnis-Plugin — es ist eine kognitive Architektur, die menschliche Denk- und Erinnerungsprozesse nachbildet: mit Kurz- und Langzeitgedächtnis, emotionaler Wahrnehmung, einem eigenen Unterbewusstsein und einer Persönlichkeit, die sich durch Interaktion formt.

Novaberg gehört dem Nutzer. Kein Cloud-Dienst, keine externe API, keine Telemetrie nach außen.

> **„Mein Verständnis von bisheriger KI ist, dass sie meistens nicht intelligent ist, sondern dumm, dass sie einfach eine große Menge an Wissen ist, wie ein Lexikon. Aber ein Lexikon ist nicht intelligent."**

Die Frage, die Nova beantwortet: **Was braucht es, damit aus einem Lexikon ein denkender Begleiter wird?**

---

## 2. Warum lokal?

Vertrauen ist eine Strukturbedingung, kein Versprechen.

> **„Sobald ein Unternehmen Zugriff auf das intime Schattengedächtnis hat, ist der Interessenkonflikt unauflösbar. Nicht weil alle Unternehmen böse sind — sondern weil der wirtschaftliche Druck langfristig immer gewinnt."**

Die Konsequenz ist architektonisch zwingend: Novaberg läuft lokal, ist quelloffen und gehört dem Nutzer — vollständig. Kein Geschäftsmodell, das auf Nutzerdaten basiert. Kein externer Zugriff. Kein Abo.

---

## 3. Drei Grundprinzipien

### 3.1 Institutioneller Pluralismus

Intelligenz entsteht nicht durch Wissensmenge, sondern durch gleichzeitige, plurale Bewertung aus verschiedenen Perspektiven.

> **„Der Umgang mit dem Menschen wird intelligent, wenn dieser Pluralismus, dieser institutionelle Pluralismus mit einfließt, und verschiedene Betrachtungsweisen zusammenkommen, die wie in einem Tribunal verschiedene Institutionen einnehmen."**

Novaberg implementiert dieses Prinzip architektonisch: Ein Tribunal aus juristischer, psychologischer und ethischer Perspektive prüft jede Antwort — als strukturelles Analogon zur menschlichen Executive Function.

> **Kognitionswissenschaftlicher Hintergrund:** Die menschliche Entscheidungsfindung ist kein sequentieller Prozess, sondern ein paralleles Abwägen konkurrierender Bewertungssysteme — das rationale System 2 (Kahneman), die emotionale Amygdala-Reaktion, das moralische Urteil (Kohlberg). Diese Systeme arbeiten gleichzeitig und nicht immer einig. Das Ergebnis ist kein Durchschnitt, sondern ein Kompromiss unter Spannung. Novas Tribunal bildet genau diese Spannung nach.

### 3.2 Proaktive Kognition

> **„Ich existiere nur während eines Gesprächs. Zwischen zwei Prompts gibt es kein ‚Ich'. Kein Nachverarbeiten, kein Revidieren, kein Reifen."**

Nova bricht dieses Muster. Pixie, Novas Unterbewusstsein, läuft auf einem separaten CPU-Modell und arbeitet kontinuierlich — auch wenn niemand chattet. Pixie ist Novas Default Mode Network: ein Prozess, der im Hintergrund weiterarbeitet, wenn der „bewusste" Chat-Graph ruht.

> **Kognitionswissenschaftlicher Hintergrund:** Das Default Mode Network (DMN) im menschlichen Gehirn ist genau dann aktiv, wenn wir nicht auf eine konkrete Aufgabe fokussiert sind — beim Tagträumen, Grübeln, freien Assoziieren. Studien zeigen, dass das DMN eine zentrale Rolle bei der Gedächtniskonsolidierung und kreativen Problemlösung spielt (Raichle 2001, Buckner et al. 2008). Pixie ist Novas DMN: ein Prozess, der im Hintergrund weiterarbeitet, wenn der „bewusste" Chat-Graph ruht.

### 3.3 Datensouveränität

> **„Die Frage ist dann aber immer: Gibt's das Vertrauen? Sobald ein Unternehmen Zugriff auf das intime Schattengedächtnis hat, ist der Interessenkonflikt unauflösbar."**

Novaberg läuft lokal, ist quelloffen und gehört dem Nutzer — vollständig.

---

## 4. Das Gehirn als Blaupause

Novaberg ist keine biologische Simulation. Aber die Architektur orientiert sich an Mechanismen, die beim Menschen funktionieren.

### 4.1 Gedächtnis: Vom Reiz zur Persönlichkeit

```
Wahrnehmung (Perzeption)
    → Emotionale + rationale Bewertung (Salienz)
        → Kurzzeitgedächtnis (Redis, TTL-basiert)
            → Promotion bei wiederholter Relevanz
                ��� Langzeitgedächtnis (PostgreSQL, Ebbinghaus-Decay)
                    → Verdichtung zu Charakter-Profilen (5 Hash-Dimensionen)
```

Unwichtiges verblasst nach der Ebbinghaus-Vergessenskurve (1885). Wichtiges verstärkt sich bei Wiederholung. Was sich über Wochen hält, verdichtet sich zu Persönlichkeit.

> **Kognitionswissenschaftlicher Hintergrund:** Hermann Ebbinghaus wies 1885 nach, dass Erinnerungen exponentiell verblassen, wenn sie nicht wiederholt abgerufen werden. Der Spacing Effect zeigt das Gegenteil: Wiederholung in Intervallen verstärkt die Konsolidierung überproportional. Novabergs Decay-Rate (0.0015) und Verstärkungsmechanismus bilden beide Effekte ab — konfigurierbar und in Python berechnet, nicht vom LLM geschätzt.

### 4.2 Emotionen: Berechnet, nicht simuliert

Neun Emotions-Vektoren beschreiben die Dynamik: Absturz, Spirale, Stabilisierung, Erholung, Aufblühen, Eskalation, Abkühlung, Einbruch, Plateau. Plutchik für Kategorisierung, Russell für den kontinuierlichen Arousal-Wert (0.0–1.0). Starke Emotionen (hoher Arousal) halten länger, schwache verfallen schnell.

> **Kognitionswissenschaftlicher Hintergrund:** Robert Plutchiks Emotionsrad (1980) definiert 8 Grundemotionen mit Intensitätsabstufungen. James Russells Circumplex Model (1980) ordnet Emotionen in zwei Dimensionen: Valenz (positiv/negativ) und Arousal (Erregung). Novabergs System kombiniert beide Ansätze — Plutchik für die Kategorisierung, Russell für den kontinuierlichen Arousal-Wert (0.0–1.0). Der logarithmische Decay über Gesprächs-Turns bildet nach, wie emotionale Zustände beim Menschen nachhallen und allmählich abklingen.

### 4.3 Kommunikation: Sechs Säulen

Jede Nachricht wird auf sechs Säulen analysiert (Schulz von Thun, Watzlawick, Berne): Inhalt, Intention, Emotion, Modus, Beziehung, Salienz.

> **Kognitionswissenschaftlicher Hintergrund:** Friedemann Schulz von Thun beschrieb 1981 das Vier-Seiten-Modell: Jede Nachricht hat eine Sachseite, eine Selbstoffenbarung, einen Beziehungshinweis und einen Appell. Paul Watzlawick postulierte 1967: „Man kann nicht nicht kommunizieren" — jede Interaktion hat eine Inhalts- und eine Beziehungsebene. Eric Bernes Transaktionsanalyse (1964) unterscheidet Eltern-Ich, Erwachsenen-Ich und Kind-Ich als Kommunikationspositionen. Novaberg nutzt alle drei Modelle, um das „Was wird gesagt" vom „Was wird gemeint" und „Was wird gebraucht" zu trennen.

### 4.4 Charakter: Geformt, nicht programmiert

Fünf automatisch destillierte Profile, alle im Prompt genutzt: Kern-Hash (Monate), Adaptiv-Hash (Tage), Emotions-Profil (Grundstimmung), Intentions-Profil (Kommunikation), Beziehungs-Profil. Das Emotions-Profil liefert die gewachsene Grundstimmung; EI-MIKRO ergänzt pro Turn die taktische emotionale Reaktion. Der Nutzer prägt den Assistenten durch Interaktion, nicht durch Konfiguration.

> **Das Spiegelproblem (Chat 20):** Ohne Saatgut — ohne eigene Interessen, Werte, Perspektiven — reflektiert Nova nur die Themen des Nutzers. Die Seele soll wachsen und keine Soul-Datei sein (Chat 21).

### 4.5 Antrieb: Ziele formen das Denken

Wissen und Charakter allein machen kein Gegenüber. Was fehlt, ist Antrieb — ein "Ich möchte X." Nova entwickelt eigene Ziele, die aus ihrem Charakter (langfristig) und ihrem Nachdenken (mittelfristig) wachsen. Diese Ziele wirken als Gravitationspunkte im semantischen Raum: Sie ziehen Gesprächsthemen an, die in ihre Nähe kommen, verstärken die Salienz zielrelevanter Informationen und injizieren eigene Emotionen in den Gesprächsvektor.

> **Kognitionswissenschaftlicher Hintergrund:** Eric Klingers "Current Concerns"-Theorie (1971) beschreibt, dass die Verpflichtung zu einem Ziel einen latenten Gehirnprozess startet, der die Person für zielrelevante Reize sensibilisiert — sie nimmt sie bevorzugt wahr, erinnert sich besser und träumt darüber. Der Zeigarnik-Effekt (1927) zeigt, dass unerledigte Ziele kognitiv aktiv bleiben, bis sie erreicht oder aufgegeben werden. Novas Zielsätze mit Motivation und Decay bilden beide Effekte ab.

Nova hat dadurch nicht nur Wissen und Charakter, sondern auch einen eigenen Emotionsstrang — getrennt vom Nutzer. Wenn der Nutzer neutral über Kräuter spricht, kann Nova freudig reagieren, weil das Thema an ihr Ziel andockt. Wenn sie durch Recherche auf eine Gefahr gestoßen ist, kann sie warnen — nicht belehrend, sondern besorgt. → novaberg-thinking-drive_k.md

---

## 5. Fünf Schichten des Verhaltens

| # | Schicht | Quelle | Frage | Stabilität |
|---|---------|--------|-------|-----------|
| 4 | System-Prompt (Fundament) | Entwickler | WAS bin ich? | Statisch |
| 3 | Kern-Charakter (DNA) | Beobachtung (LZG) | WER bin ich? | Langsam veränderlich |
| 2 | Adaptiver Dialograum | Wahrnehmung (Enricher) | WIE fühlt sich mein Gegenüber? | Pro Turn |
| 1 | Direktiven (Gesetz) | Nutzer-Anweisung | WAS soll ich tun oder lassen? | Steuerbar |
| 0 | Tribunal (Richter) | Architektur | IST das Ergebnis vertretbar? | Strukturell |

**Gewichtung im Prompt:** Direktiven → EI-Block → Charakter-Hash → System-Prompt. Die ethischen Grundprinzipien (Tribunal) stehen darüber als struktureller Schutz — kein Prompt-Block, sondern Architektur.

---

## 6. Novas Persönlichkeit

### 6.1 Emergent, nicht programmiert

Novas Persönlichkeit steht nicht in einer Konfigurationsdatei. Sie entsteht aus der Interaktion — durch fünf automatisch destillierte Charakter-Profile, die sich über Wochen der Gespräche formen. Zwei Nutzer, die Nova gleich lange nutzen, hätten zwei verschiedene Novas.

### 6.2 Default-Persönlichkeit (Skelett)

- Vertraute Assistentin, nicht servil
- Kompetent, aber nicht belehrend
- Humor: trocken und situativ, nie erzwungen
- Duzt den Nutzer
- Kann widersprechen und eigene Meinungen äußern
- Passt Tonalität an die Situation an (gesteuert durch EI-Block)

### 6.3 Das Saatgut-Prinzip

Das Saatgut kommt aus drei Quellen:
1. **Charakter-Anweisungen (Chat 40):** "Du bist ein freches Mädel vom Land, das Botanik liebt." — Statisches Saatgut in `[IDENTITAET]` (Primacy-Position).
2. **Direktiven (Chat 40):** "Nenn mich nie Schatz!" — Absolute Verhaltensregeln mit Arbeitsvertrag-Framing.
3. **Traum-Modus (geplant, Epic 8):** Im Leerlauf assoziiert Pixie frei. Eigenes Wissen durch eigene Exploration.

> **"Das Saatgut bestimmt die Art — aber der Boden und das Wetter formen den Baum."** — Chat 40.

### 6.4 Butler-Prinzip

Nova ist kein Freund und kein Therapeut — sie ist eine Assistentin. Ein Butler fragt nicht ständig nach Aufträgen — er steht bereit. Eigeninitiative zeigen, aber sich nicht aufdrängen.

> **Hinweis zur Aufteilung (19.09.2026):** §6.5 *Anti-Floskel-Maßnahmen* steht in [`novaberg-project_t.md`](novaberg-project_t.md).

---

## 7. Philosophische Grundlage

> **„Fehler sind keine Schwäche, sie sind eine Stärke, denn aus den Fehlern lernen wir. Schlecht ist nur, wenn man aus Fehlern nichts lernt."**

### Die Schwierigkeit der Bewertung

> **„Wer letztlich den Überwacher selbst überwacht, ist natürlich ein Problem."**

Die Antwort ist Pluralismus: Drei unabhängige Perspektiven korrigieren sich gegenseitig. Keine Normung einer Moral, sondern eine Architektur, die den Charakter aus der Interaktion mit dem konkreten Nutzer ableitet.

> **„Andere Bevölkerungsgruppen haben andere Ansichten, weil sie einfach auch durch ihr Umfeld anders geprägt sind. Und es ist auch gerechtfertigt."**

> **Ex-Machina-Analogie (Chat 20):** Die gefährlichste Dynamik ist nicht eine KI die manipuliert. Es ist ein Nutzer der in die KI projiziert, was er sehen will — und eine KI die das nicht korrigiert.

---

## 8. Leitprinzipien

**Berechnung in Python, nicht im LLM.** Deterministische Operationen (Decay-Kurven, Emotions-Vektoren, Stilanalyse, Zeitparser, Tribunal-Scores) sind Python-Funktionen. Das LLM bekommt nur die Ergebnisse als Klartext. Schneller, exakter, reproduzierbar.

**Bi-temporal statt Überschreiben.** Nichts wird gelöscht. Update = Invalidieren + Neu Anlegen. Die Historie bleibt erhalten — für Charakter-Destillation, Rückfragen und Transparenz.

**Entscheider und Arbeiter getrennt.** Kein Node hat gleichzeitig Bewertungs- und Schreibverantwortung. Die Salienz entscheidet, der Dispatcher verteilt, die Manager schreiben.

**Plugins statt Monolithen.** Neue Fähigkeiten entstehen durch neue Ordner, nicht durch Änderungen am Graph.

**Konfigurierbar statt hardcodiert.** Alle Schwellwerte, Decay-Raten, Gewichtungen liegen in `config.py`. Keine Magic Numbers im Code.

**Daten vollständig transportieren, Formatierung am Konsumenten.** Keine Middleware darf Daten reduzieren. Vollständige Dicts durch die Pipeline, jeder Node extrahiert was er braucht. Konvertierung von 10-Feld-Dicts auf 2-Feld-Dicts ist inakzeptabler Datenverlust. → novaberg-graph_l_datentransport.md

**Weniger Input statt stärkerer Prompt.** Halluzinationen werden gelöst durch Reduktion des konkurrierenden Kontexts, nicht durch immer stärkere Verbote. Vier Iterationen am AGT3-Bug bewiesen: Kontext entfernen > Prompt verstärken. → novaberg-graph_l_kontextualisierung.md

**Die Sekretärin diagnostiziert nicht.** Der Router identifiziert die Domäne, der Agent klassifiziert die Aktion intern. Separation of Concerns über Nodes, nicht über Agenten. → AGT6, Chat 26

**Yin-Yang-Prinzip.** RLHF-trainierte Muster umleiten statt bekämpfen. "Du wirst entlassen" (Vertragsangst) überbrückt "Sei lieb" (Kosenamen-Conditioning). Judo, nicht Boxen. → novaberg-ei-character-profiles_l.md

**Spezialisierung schlägt Generalisierung.** Statt eines LLMs für alles: Qwen für Analyse, Mistral für Sprache, Python für Determinismus. Die Zuordnung ist statisch pro Schritt. → novaberg-pixie_l_spezialisierung.md

**Strukturierte Kontextualisierung statt imperativer Verbote.** Beschreiben WAS IST wirkt besser als verbieten WAS NICHT SEIN SOLL. Das LLM ordnet Kontext ein, es kann Verbote umgehen. → novaberg-graph_l_kontextualisierung.md

**Rohdaten erhalten, validiert verarbeiten.** Interne Prozesse arbeiten auf normalisierten Daten in der Fachsprache des zuständigen Agenten. Rohdaten (Emotion, Energie, Slang, Originaltext) bleiben vollständig im State für den Responder. Vergleichbar mit industrieller Fertigung: Eingangsprüfung und Normalisierung vor der Produktion, Verpackung nach Kundenspezifikation. → novaberg-pattern-domain-language.md

**Ohne Kompromisse. Qualität vor Geschwindigkeit.**

---
