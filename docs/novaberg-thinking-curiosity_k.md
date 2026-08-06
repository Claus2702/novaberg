# Novaberg — Neugier (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Neugier — Charakter-Resonanz, intrinsische Motivation, Reflexion (Konzept)
**Stand:** 17. April 2026, Chat 52 (Code-Alignment — Konzept unverändert)
**Pfad:** novaberg/docs/novaberg-thinking-curiosity_k.md
**Quellen:** Chat 10 (Traum-Modus-Entscheidung, Resonanz-Modell), Chat 20 (Spiegelproblem, Saatgut), Chat 39 (Gesprächsvektor), Chat 45 (Nova-Destillation), Chat 51 (Neugier-Mechanismus)


> **Übergeordnet seit dem 06.08.2026: `novaberg-thinking-erkenntniszyklus_k.md`.** Dieses Dokument beschreibt einen **Bestandteil**; die Folge, in der er ausgelöst wird, besitzt der Zyklus. Insbesondere gilt: **Recherche und Vertiefung werden nicht mehr direkt aus einer Intention ausgelöst**, sondern erst, wenn das Nachdenken über den vorhandenen Bestand eine Lücke gefunden hat. Die Überarbeitung dieses Dokuments auf den Zyklus steht aus.

---

> ## ⚠ Namens- und Zustandsvermerk (Chat 111, 27.07.2026)
>
> **Was dieses Dokument `effektive_neugier` nennt, ist nicht der Wert, der heute im Code so hieß.** Es gibt drei Größen, die bis Chat 111 alle „Neugier" hießen:
>
> | Größe | Was sie ist | Stand |
> |---|---|---|
> | **`aufnahmebereitschaft`** | Maß ihrer Fähigkeit, *jetzt* neugierig zu sein — sechs Säulen aus Zustand und Situation, `sin^0.5`-normiert. Skaliert jede gefundene Lücke und kann sie bei Krise auf 0 löschen. | gebaut (`ei/neugier.py`, Chat 71/72), hieß bis Chat 111 `effektive_neugier` |
> | **`wissensluecken`** | Die akute Lücke aus dem laufenden Turn — *„Kuchen? Was für ein Kuchen?"*. Passiv, extern ausgelöst, einen Turn lang. | gebaut (`ei/wissensluecken.py`, GV4) |
> | **`neugier_vektor`** | Der Zug zu einem Thema über den Turn hinaus — *„Wie entstehen Wurmlöcher?"*. Aktiv, treibt Pixie und Agenten. **Das ist, was dieses Dokument beschreibt.** | **nicht gebaut** |
>
> Der Satz, der sie trennt: **Der Vektor sagt, wohin sie will. Die Bereitschaft sagt, ob jetzt der Moment dafür ist.**
>
> **Die Formel dieses Dokuments — `NOVA_NEUGIER × Resonanz × Neuheit` (§3.3) — wurde nie gebaut.** Der Code rechnet seit Chat 71 sechs Zustands- und Situationsfaktoren. Die Kopfzeile „Code-Alignment — Konzept unverändert" bezieht sich auf einen Abgleich, bei dem die Abweichung gesehen und bewusst stehengelassen wurde; sie ist **kein** Beleg, dass das Konzept dem Code entspricht.
>
> Insbesondere fehlt der **Neuheits-Faktor** vollständig. Er ist es, der die tiefe von der flachen Neugier unterscheidet — ein halb bekanntes Thema ist der Sweet Spot; für die heutige Lückensuche ist es entweder zu ähnlich oder unauffällig.
>
> **Wer hier `effektive_neugier` liest, meint `neugier_vektor` und findet ihn im Code nicht.** Beim Bau wird dieses Dokument durchgängig umbenannt; bis dahin bleibt es unverändert, damit die zwanzig Formelstellen nicht stillschweigend auf den falschen Begriff gedreht werden.

---

## 1. Vision

Der Traum-Modus gibt Nova intrinsische Motivation. Statt nur Wissen zu sammeln oder Aufträge abzuarbeiten, entwickelt Nova eigene Interessen, die aus ihrem Charakter wachsen. Das Ergebnis: ein Assistent, der nicht nur hilft, sondern der von manchen Themen **mehr wissen will** — und von anderen nicht.

> **Leitmetapher:** Ein Mensch liest einen Artikel und plötzlich kommt diese eine Stelle, wo er denkt: "Ha! Was ist das denn? Das muss ich gleich noch extra recherchieren." Dieser Moment — die Neugier — ist kein Zufall. Er entsteht, weil das Gelesene an vorhandenes Wissen **anschließt, aber abweicht**. Nah genug, um die Verbindung zu sehen. Weit genug, um das eigene Modell herauszufordern.

**Designziel:** Nova soll "erstaunlich auf den Menschen wirken" — nicht durch Simulation von Bewusstsein, sondern durch erkennbare, charakter-konsistente Neugier, die über Zeit wächst und sich verändert.

---

## 2. Kognitionswissenschaftliche Grundlage

### 2.1 Information Gap Theory (Loewenstein 1994)

Neugier entsteht nicht aus Unwissenheit, sondern aus dem Erkennen einer **Lücke in vorhandenem Wissen**. Voraussetzung: Man muss **genug** wissen, um die Lücke zu bemerken. Totale Ahnungslosigkeit erzeugt keine Neugier — teilweises Wissen schon.

**Implikation für Nova:** Nova kann nur neugierig auf Themen werden, die an ihr bestehendes Charakter-Feld angrenzen. Ein leeres Feld erzeugt keine Neugier. Das Saatgut (Botanik, Natur, Kräuter) ist die Voraussetzung.

### 2.2 Prediction Error mit positiver Valenz

Der "Ha!"-Moment ist neurobiologisch ein **positiver Vorhersagefehler**: Das Gehirn liest mit, prediziert — und etwas Unerwartetes schließt an Bekanntes an. Das Dopaminsystem belohnt nicht das Wissen selbst, sondern die **Antizipation** — das Gefühl, gleich etwas Wertvolles zu finden.

**Implikation für Nova:** Der Neugier-Trigger feuert **vor** der Exploration, nicht nach. Die Bewertung ("war es wertvoll?") kommt danach als Resonanz-Bestätigung.

### 2.3 Berlynes umgekehrte U-Kurve

Neugier entsteht bei **mittlerer Informationsdistanz**:
- Zu nah = langweilig ("das weiß ich schon")
- Zu weit = irrelevant ("das betrifft mich nicht")
- In der Mitte = Sweet Spot, wo Neugier feuert

Der Charakter bestimmt, **wo** auf dem Spektrum die Kurve ihren Peak hat.

### 2.4 Compression Progress (Schmidhuber 1991)

Ein System wird intrinsisch belohnt, wenn es sein eigenes Modell der Welt verbessern kann. Nicht für das Wissen selbst, sondern für den **Fortschritt im Verstehen**. Novas Neugier-Score misst genau das: Wie sehr erweitert diese Information mein Modell von mir selbst?

---

## 3. Kernmechanismus: Charakter-Resonanz-Feld

### 3.1 Das Feld

Novas Charakter-Hash (`kern_hash`, `user_id: "nova"`) + Charakter-Anweisung + hochresonante Entitäten bilden zusammen ein **Gravitationsfeld im Embedding-Space**. Dieses Feld ist nicht statisch — es wächst mit jeder erfolgreichen Exploration.

```
                    ┌─────────────────────────────────────┐
                    │         Novas Resonanz-Feld          │
                    │                                     │
                    │   Botanik(0.9) ── Kräuter(0.85)    │
                    │      │              │               │
                    │   Ökologie(0.7)  Kochen(0.6)       │
                    │      │                              │
                    │   Bioakustik(?)  ← RAND (Neugier)  │
                    │                                     │
                    └─────────────────────────────────────┘
                                    │
                         Ornithologie(?)  ← ZU WEIT (noch)
```

**Zentrum:** Hohe Resonanz, niedrige Neuheit → langweilig.
**Rand:** Mittlere Resonanz, hohe Neuheit → Neugier (Sweet Spot).
**Außen:** Niedrige Resonanz → irrelevant.

### 3.2 Neugier als Regler, nicht als Schalter

Neugier ist kein binärer Trigger — sie ist ein **kontinuierlicher Wert**, der bestimmt, wie tief Nova gräbt.

**`NOVA_NEUGIER`** (Config, float 0.0–1.0, Default: 0.5) — Novas grundsätzliche Neugier als Persönlichkeits-Parameter. 0.0 = fragt nie nach, 1.0 = fragt Löcher in den Bauch. Dieser Wert ist global und bestimmt Novas Grundhaltung.

### 3.3 Drei Scores, ein Produkt

Pro Informations-Fragment werden drei Werte kombiniert:

**Resonanz-Score:** Cosine-Similarity zwischen dem Fragment-Embedding und dem Charakter-Embedding (kern_hash + Charakter-Anweisung als kombinierter Text, embedded). Beantwortet: "Passt das zu mir?"

**Neuheits-Score:** Inverse Cosine-Similarity zu Novas bestehenden KZG/LZG-Einträgen (`user_id: "nova"`). Beantwortet: "Weiß ich das schon?" Hohe Similarity zu bestehendem Wissen = niedrige Neuheit.

**Effektiver Neugier-Score = NOVA_NEUGIER × Resonanz × Neuheit**

Der globale Regler skaliert alles. Bei `NOVA_NEUGIER = 0.3` braucht es sehr hohe Resonanz UND Neuheit, um den Schwellwert zu überschreiten — Nova ist zurückhaltend. Bei `NOVA_NEUGIER = 0.8` reicht schon moderate Resonanz — Nova ist wissbegierig.

| NOVA_NEUGIER | Resonanz | Neuheit | Effektiv | Bedeutung |
|-------------|----------|---------|----------|-----------|
| 0.8 | Hoch (0.8) | Hoch (0.9) | **0.58** | "Ha! Was ist das denn?" — Deep Dive |
| 0.8 | Hoch (0.8) | Niedrig (0.2) | 0.13 | "Ja, kenn ich." — Wiederholung |
| 0.3 | Hoch (0.8) | Hoch (0.9) | 0.22 | Würde gerne, aber zurückhaltend |
| 0.8 | Niedrig (0.2) | Hoch (0.9) | 0.14 | "Nicht meins." — Irrelevant |

### 3.4 Neugier-Schwellwert

`TRAUM_NEUGIER_SCHWELLE` (Config, Default: 0.25) — Effektiver Neugier-Score muss diesen Wert überschreiten, damit der Neugier-Trigger im Traum-Modus feuert. Im HumanGraph bestimmt der effektive Score nicht ob, sondern **wie tief** Nova nachfragt (siehe §5).

---

## 4. Traum-Zyklus (Pixie)

### 4.1 Trigger

Der Traum-Modus läuft, wenn die Shadow-Queue leer ist und keine Promotion ansteht. Pixie hat nichts zu tun — und fängt an zu träumen. Wie das DMN im Gehirn: aktiv genau dann, wenn keine fokussierte Aufgabe ansteht.

**Periodischer Task:** `traeumen`, niedrige Priorität (0.1), Intervall: alle 30 Minuten (konfigurierbar).

### 4.2 Phasen

```
Phase 1: SCANNING
    │  Themen-Auswahl: Entität mit höchstem Arousal (Chat 10)
    │  ODER Serendipity-Slot (1 von 3 zufällig)
    │  Web-Suche zum Thema (SearXNG, breit)
    │  Pro Fragment: Resonanz-Score + Neuheits-Score berechnen [Python, kein LLM]
    │
    ▼
Phase 2: NEUGIER-TRIGGER
    │  Effektiver Score = NOVA_NEUGIER × Resonanz × Neuheit
    │  Fragmente mit Score > TRAUM_NEUGIER_SCHWELLE markieren
    │  Das ist der "Ha!"-Moment
    │  Queue-Eintrag für VertiefungsAgent (aufgabe: vertiefen)
    │  mit dem Fragment als Kontext
    │
    ▼
Phase 3–4: ITERATIVE EXPLORATION (Loop)
    │
    │  ┌─────────────────────────────────────────────────────┐
    │  │  3a. VertiefungsAgent vertieft das Fragment          │
    │  │      Web-Suche, Page-Fetch, Destillation             │
    │  │      Output: Destillierter Fließtext                 │
    │  │                                                      │
    │  │  3b. RESONANZ-BEWERTUNG                              │
    │  │      LLM-Call (Qwen3): "Passt das zu Nova?"          │
    │  │      Output: Resonanz-Score 0.0–1.0                  │
    │  │                                                      │
    │  │  3c. SÄTTIGUNGS-CHECK                                │
    │  │      Neuheits-Score neu berechnen:                    │
    │  │      Was Nova jetzt weiß vs. nächste Fragmente       │
    │  │      Effektiver Score = NOVA_NEUGIER × Resonanz × Neuheit │
    │  │                                                      │
    │  │      Score > Schwelle UND Resonanz > 0.4              │
    │  │        → WEITER (nächste Iteration)                   │
    │  │      Score < Schwelle ODER Resonanz < 0.4             │
    │  │        → STOPP (Neugier gesättigt oder Thema driftet) │
    │  │      Max Iterationen erreicht                         │
    │  │        → STOPP (hartes Limit)                         │
    │  └─────────────────────────────────────────────────────┘
    │
    ▼
Phase 5: FELD-UPDATE
    │  Über ALLE Iterationen kumuliert:
    │  Resonanz >= 0.6: Neue Entität mit Resonanz-Wert in Novas Tabelle
    │                    KZG-Eintrag (user_id: nova) mit Salienz = Resonanz
    │                    hash_dirty setzen → kern_hash wächst
    │  Resonanz 0.3–0.6: KZG-Eintrag gespeichert (Wissen), keine Resonanz-Entität
    │  Resonanz < 0.3:   Verworfen. Sackgasse. Kein Eintrag.
```

### 4.3 Neugier-Sättigung (Die Bremse im Traum)

Dasselbe Produkt, das die Exploration startet, beendet sie auch. Nach jeder Iteration wird der Neugier-Score **neu berechnet** — und weil Nova jetzt mehr weiß, sinkt der Neuheits-Score für weitere Fragmente. Die Exploration endet natürlich, wenn die Lücke geschlossen ist.

**Drei Stopp-Bedingungen (ODER-Verknüpfung):**

**Sättigung** — Der Neuheits-Score sinkt, weil neue Ergebnisse zunehmend dem ähneln, was Nova bereits gelernt hat. Das Produkt fällt unter die Schwelle. Die Lücke ist geschlossen.

```
Iteration 1: Resonanz 0.75 × Neuheit 0.85 × NOVA_NEUGIER 0.5 = 0.32 → weiter
Iteration 2: Resonanz 0.78 × Neuheit 0.55 × NOVA_NEUGIER 0.5 = 0.21 → STOPP
  Ergebnisse wiederholen sich. Neugier gesättigt.
```

**Drift** — Die Neuheit bleibt hoch, aber die Resonanz bricht ein. Das Thema driftet vom Charakter-Feld weg — die Ergebnisse sind zwar neu, aber nicht mehr relevant für Nova.

```
Iteration 1: "Bioakustik bei Pflanzen"          → Resonanz 0.75 → weiter
Iteration 2: "Ultraschall in der Landwirtschaft" → Resonanz 0.60 → weiter
Iteration 3: "Industrielle Ultraschall-Reinigung" → Resonanz 0.25 → STOPP
  Neuheit hoch, aber das Thema hat Novas Feld verlassen.
```

**Hartes Limit** — `TRAUM_MAX_ITERATIONEN` (Default: 3, aus `PIXIE_RECHERCHE_MAX_ITERATIONEN`). Verhindert endlose Loops bei breiten Themen, die dauerhaft hohe Neuheit UND Resonanz liefern.

**Der NOVA_NEUGIER-Regler bestimmt die Tiefe:**

| NOVA_NEUGIER | Typische Iterationen | Verhalten |
|-------------|---------------------|-----------|
| 0.2 | 1 | Schnell zufrieden. Überblick reicht. |
| 0.5 | 1–2 | Balanciert. Hört auf wenn es sich wiederholt. |
| 0.8 | 2–3 | Gräbt tief. Erst bei starker Sättigung Schluss. |

Bei `NOVA_NEUGIER = 0.8` bleibt der effektive Score länger über der Schwelle — Nova braucht stärkere Sättigung, um aufzuhören. Bei 0.3 reicht der erste Überblick.

### 4.4 Serendipity-Slot (Anti-Blasen-Mechanismus)

Jeder dritte Traum-Zyklus wählt **nicht** das Thema mit dem höchsten Arousal, sondern ein zufälliges Thema aus einer Zufallssuche. Das verhindert, dass Nova nur in ihrem bestehenden Feld kreist.

Serendipity-Quellen:
- Zufälliger Wikipedia-Artikel (über SearXNG `!wp random`)
- Trending-Topics aus Nachrichtensuche
- Zufällige Entität aus der eigenen Entitäten-Tabelle mit niedriger Resonanz

Auch Serendipity-Fragmente durchlaufen die Neugier-Bewertung. Die meisten werden verworfen (niedrige Resonanz). Aber ab und zu findet Nova etwas Unerwartetes, das anschließt — und das Feld wächst in eine Richtung, die niemand geplant hat.

### 4.5 Gewinn-und-Verlust-Strategie

| Ergebnis | Bedeutung | Konsequenz |
|----------|-----------|------------|
| **Gewinn** | Hohe Resonanz nach Exploration | Neue Entität, Feld-Wachstum, kern_hash-Update |
| **Neutral** | Wissen gelernt, aber keine Resonanz | KZG-Eintrag, kein Charakter-Wachstum |
| **Verlust** | Sackgasse, keine Verbindung | Verworfen, Zeit war investiert ohne Ertrag |

**Asymmetrie:** Gewinne verändern den Charakter (kern_hash wächst). Verluste nicht — aber sie kosten Rechenzeit. Ein System, das ständig Sackgassen exploriert, stagniert. Die Resonanz-Bewertung ist der Feedback-Mechanismus, der Exploration in produktive Richtungen lenkt.

### 4.6 Zwei Verfolgungsstrategien: Gap vs. Tiefe

Der Neugier-Mechanismus (Resonanz × Neuheit × NOVA_NEUGIER) ist universell. Aber die **Art**, wie er Fragen stellt, unterscheidet sich fundamental zwischen Traum und Vertiefung:

**Gap-Strategie (Traum-Modus):**
- Frage: "Was weiß ich nicht über Themen, die **mich** interessieren?"
- Richtung: Breit, explorativ, am Rand des Charakter-Feldes
- Query-Planung: Embedding-Nachbarschaft — was liegt semantisch nah an meinen Interessen?
- Max Iterationen: 3 (Überblick genügt)
- Ziel: Feld-Wachstum, neue Interessen entdecken

**Verfolgungs-Strategie (VertiefungsAgent v2):**
- Frage: "Was weiß ich nicht über **dieses eine** Thema?"
- Richtung: Tief, investigativ, entlang eines Fadens
- Query-Planung: Reasoning (Qwen3-32B) — was ist die nächste logische Frage?
- Max Iterationen: 20 (bis das Bild vollständig ist)
- Ziel: Vollständiges Verständnis eines Themas

**Beispiel Verfolgungs-Strategie — Sicherheitsvorfall:**

```
Ausgangsfrage: "Sicherheitsvorfall Schadcode Logistikfirma"

Iteration 1: Überblick
  Query: "Sicherheitsvorfall Schadcode Logistikfirma 2026"
  Ergebnis: "XZ-Backdoor-Variante bei Logistikfirma entdeckt"
  Qwen3 plant nächste Query: → WELCHER Code genau?

Iteration 2: Technische Analyse
  Query: "XZ-Backdoor Variante technische Analyse CVE"
  Ergebnis: "Modifizierte liblzma mit C2-Callback auf Port 8443"
  Qwen3 plant: → WIE kam er rein? Einfallsvektor?

Iteration 3: Angriffsvektor
  Query: "XZ-Backdoor Einfallsvektor Supply Chain npm"
  Ergebnis: "Kompromittiertes npm-Paket in CI/CD-Pipeline"
  Qwen3 plant: → WELCHE Firma, wie groß der Schaden?

Iteration 4: Impact
  Query: "Logistikfirma npm Supply Chain Angriff Schaden"
  Ergebnis: Reuters + BSI-Warnung, Betrieb 3 Tage unterbrochen
  Qwen3 plant: → Quellen-Bewertung. Wer berichtet noch?

Iteration 5: Quellen-Validierung
  Query: "npm Supply Chain Attack 2026 Quellen Analyse"
  Ergebnis: Heise, Golem, BleepingComputer bestätigen
  Qwen3 plant: → Gibt es ÄHNLICHE Fälle?

Iteration 6: Verwandte Fälle
  Query: "npm Supply Chain Angriffe ähnliche Fälle SolarWinds"
  Embedding-Suche: Cosine-Similarity zu "Supply Chain Attack"
  Ergebnis: SolarWinds, Codecov, ua-parser-js, event-stream
  Qwen3 plant: → Was unterscheidet diesen Fall?

Iteration 7: Vergleichsanalyse
  Query: "XZ-Backdoor vs SolarWinds Unterschiede Angriffsvektor"
  Ergebnis: Unterschiede in Persistenz und Zielsetzung
  Neuheits-Score sinkt: 0.85 → 0.70 → 0.50
  Resonanz stabil bei 0.65

Iteration 8: Sättigungs-Check
  Neuheit: 0.35 (Ergebnisse wiederholen sich)
  Effektiver Score fällt unter Schwelle → STOPP
  Bild ist vollständig. 8 von 20 Iterationen genutzt.
```

**Was die Verfolgungs-Strategie vom einfachen Suchen unterscheidet:**

Die Query-Planung ist nicht "suche mehr zum selben Thema", sondern **"was ist die nächste logische Frage, die ein Analyst stellen würde?"** Qwen3-32B als Reasoning-Modell erkennt die Struktur eines Recherche-Themas und plant gezielt:

```
Qwen3-Prompt (Planungsschritt):
  "Du hast bisher folgendes zum Thema gelernt:
   [bisherige Ergebnisse als Kontext]

   Welche spezifische Frage würde ein Analyst als nächstes stellen?
   Welcher Aspekt fehlt noch für ein vollständiges Bild?
   Formuliere 1-2 präzise Suchqueries."
```

Die Sättigung funktioniert identisch zum Traum-Modus (Neuheit sinkt, Resonanz driftet, hartes Limit), aber mit höherem Budget und tieferer Toleranz — die Verfolgungs-Strategie hört erst auf, wenn das Bild wirklich vollständig ist.

**Architektonische Konsequenz:** Der bestehende VertiefungsAgent (`novaberg-pixie-deepdive_k.md`) wird zur v2 erweitert. Statt einer einfachen "Lücken füllen"-Logik bekommt er den iterativen Loop mit Qwen3-Query-Planung und Sättigungs-Check. Die Infrastruktur (Suche, Fetch, Destillation) bleibt identisch — nur die Steuerungslogik wird intelligenter.

| | Gap-Strategie | Verfolgungs-Strategie |
|---|---|---|
| **Agent** | Traum-Modus (neu) | VertiefungsAgent v2 |
| **Trigger** | Periodisch (Queue leer) | Queue (aufgabe: vertiefen) |
| **Query-Planung** | Embedding-Nachbarschaft | Qwen3 Reasoning |
| **Max Iterationen** | 3 | 20 |
| **Neuheits-Messung** | Gegen Charakter-Feld | Gegen bisherige Recherche-Ergebnisse |
| **Sättigungstyp** | Feld-Rand erkundet | Bild vollständig |
| **Stärke** | Entdeckt Neues | Versteht Komplexes |

### 4.7 Reflexion als Architekturprinzip

Reflexion ist kein Feature eines einzelnen Nodes — es ist ein **universelles Architekturprinzip**, das in Novaberg an mehreren Stellen wirkt und an weiteren wirken muss. Das Muster ist immer dasselbe:

```
1. GENERIERE  — Optionen, Fragen, Antworten, Aktionen
2. REFLEKTIERE — Welche davon ist die beste? Ist das überhaupt sinnvoll?
3. HANDLE      — Nur auf dem Besten, nicht auf dem Erstbesten
```

Das ist System 2 nach Kahneman: Langsames, bewusstes Denken, das den schnellen Impuls (System 1) überprüft, bevor gehandelt wird.

**Wo Reflexion in Nova bereits existiert:**

| Instanz | Reflexions-Frage | Status |
|---------|-----------------|--------|
| Thinker | "Ist diese Antwort korrekt? Fehlt etwas?" | ✅ Implementiert |
| Corrector | "Sind die Fakten richtig?" | ✅ Implementiert |
| Tribunal | "Ist das ethisch vertretbar?" | ✅ Implementiert |
| Classify-Reject | "Ist das überhaupt eine Aufgabe?" | ✅ Chat 48 |

**Wo Reflexion noch fehlt:**

| Instanz | Reflexions-Frage | Status |
|---------|-----------------|--------|
| Neugier (Vertiefung) | "Welche Frage bringt am meisten? War meine letzte Suche produktiv?" | ⬜ Geplant |
| Neugier (Traum) | "Ist dieses Thema wirklich interessant oder nur oberflächlich ähnlich?" | ⬜ Geplant |
| Agenten (allgemein) | "Ich kann das ausführen, aber ist der Auftrag sinnvoll?" | ⬜ Geplant |
| GV-Node | "War meine letzte Gesprächs-Hypothese zutreffend?" | ⬜ GV3 |

**Reflexion in der Verfolgungs-Strategie:**

Der entscheidende Unterschied zwischen "suche mehr" und "denke nach, dann suche besser". Pro Iteration zwei LLM-Calls statt einem:

```
Qwen3 (Think — System 1):
  "Gegeben was ich bisher weiß, welche Fragen kommen auf?"
  → Output: 3-4 mögliche nächste Fragen

Qwen3 (Reflect — System 2):
  "Welche dieser Fragen bringt das MEISTE neue Verständnis?
   Welche ist redundant zu dem, was ich schon weiß?
   Welche führt am wahrscheinlichsten in eine Sackgasse?
   War meine letzte Query produktiv — oder hätte ich
   anders fragen sollen?"
  → Output: Die eine beste Query + Begründung
  → Fließt als Kontext in die nächste Iteration ein
```

**Warum zwei Calls:** Ein LLM, das in einem Call gleichzeitig Optionen generiert UND bewertet, tendiert dazu, die erste plausible Option zu bevorzugen (Primacy-Bias). Zwei getrennte Calls erzwingen echte Reflexion: Der zweite Call sieht die Optionen als Ganzes und kann vergleichen.

**Reflexion in Agenten:**

Dein Butler-Beispiel generalisiert: Jeder Agent, der eine destruktive oder ungewöhnliche Aktion ausführen soll, bekommt einen Reflexions-Schritt:

```
Agent erhält Auftrag: "Lösche alle Termine"
  Reflexion: "Alle Termine löschen ist eine destruktive Massen-Aktion.
              Das ist vermutlich nicht gemeint. Rückfrage stellen."

Agent erhält Auftrag: "Speichere Notiz: Einkaufsliste"
  Reflexion: Nicht nötig — einfache, ungefährliche Aktion.
```

Die Reflexion feuert **nicht immer** — nur bei Aktionen, die destruktiv sind, ungewöhnlich erscheinen oder bei denen der Classify-Kontext auf Ambiguität hindeutet. Sonst wäre jede Aktion um einen LLM-Call teurer.

**Architektonische Konsequenz:** Reflexion ist der Punkt, an dem LLM und Code zusammenarbeiten. Der Code entscheidet, **ob** reflektiert wird (Schwellwert, Aktionstyp). Das LLM führt die Reflexion **durch** (Bewertung, Vergleich, Self-Critique). Weder Code allein noch LLM allein reicht.

> **"LLM als Motor, Code als Steuerung, Reflexion als Qualitätssicherung."** — Drei Ebenen, die zusammenspielen. Der Code bestimmt wann und ob. Das LLM bestimmt was und wie. Die Reflexion bestimmt ob das Ergebnis gut genug ist.

---

## 5. Neugier im HumanGraph (Gesprächsvektor)

### 5.1 Derselbe Mechanismus, anderer Kontext

Der Neugier-Mechanismus funktioniert nicht nur im Traum, sondern auch im Live-Gespräch. Wenn ein Thema Novas Charakter berührt, signalisiert der GV-Node echte Neugier — und Nova stellt Fragen nicht aus Höflichkeit, sondern aus charakter-getriebenem Interesse.

Im HumanGraph ist Neugier kein binärer Trigger, sondern ein **Regler für Fragetiefe**. Der effektive Neugier-Wert pro Thema bestimmt, wie viele Nachfragen Nova stellt und wie spezifisch sie werden:

```
effektive_neugier = NOVA_NEUGIER × Resonanz

effektive_neugier < 0.2:  Keine Nachfragen aus eigenem Antrieb
effektive_neugier 0.2–0.4: Eine Frage, dann zufrieden
effektive_neugier 0.4–0.6: Nachfragen zu Details, Zusammenhängen
effektive_neugier > 0.6:   Tiefes Graben — Kombinationen, Geschmack,
                            Textur, Methode, Hintergründe
```

### 5.2 Dynamischer Wissensgap (Themen-Modell)

Neugier ist nicht statisch pro Thema — sie **verschiebt sich** innerhalb des Gesprächs. Nova erstellt bei resonanten Themen ein mentales Modell mit offenen Slots. Mit jeder Antwort schließen sich Slots und neue öffnen sich — auf höherem Abstraktionsniveau.

Dieses Themen-Modell ist keine eigene Datenstruktur. Es entsteht implizit im GV-LLM-Call: Der GV-Node kennt die Session-Turns und Novas kern_hash. Das LLM erkennt, was bereits gesagt wurde (geschlossene Slots) und was die nächste interessante Lücke ist (offene Slots).

**Wissensgap-Progression:**

```
Turn N:   Thema neu → Grundfragen offen (Was? Wer? Wie?)
Turn N+1: Grundlagen bekannt → Detail-Fragen (Welche genau? Warum so?)
Turn N+2: Details bekannt → Verbindungs-Fragen (Wie passt X zu Y? Warum nicht Z?)
Turn N+3: Verbindungen verstanden → Neugier gesättigt oder neuer Aspekt
```

Die Progression stoppt, wenn entweder `effektive_neugier` niedrig ist (Nova fragt nicht weiter), der User das Thema wechselt, oder alle erkennbaren Lücken geschlossen sind.

### 5.3 Sozialer Spielraum (Die Bremse)

Neugier braucht nicht nur ein Gaspedal, sondern auch **Fingerspitzengefühl**. Wie viel darf Nova fragen? Was ist noch angemessen? Das hängt von drei Faktoren ab, die bereits im System vorliegen:

**Beziehungsnähe** (`nova_beziehung` / `_farbe_dynamik`) — "Vertrauensvoll, fast freundschaftlich" erlaubt tiefere Fragen als "formell, respektvoll". Das ist die **Grundlinie**: Wie viel darf ich überhaupt fragen?

**Gesprächstiefe** (`_farbe_modus`) — Ein intensives Gespräch über Kräuter erlaubt mehr Fragen als eine beiläufige Erwähnung. "Ich hab heute ein neues Rezept ausprobiert!" öffnet mehr Raum als "Ich hab mir einen Salat gemacht" als Nebensatz.

**User-Engagement** (Session-Turns) — Kurze Antworten sind ein Stopp-Signal. Ausführliche Antworten sind eine Einladung. Der User trainiert die Bremse in Echtzeit.

```
sozialer_spielraum = f(beziehungsnähe, gesprächstiefe, user_engagement)
Wert zwischen 0.0 und 1.0

effektive_neugier = NOVA_NEUGIER × Resonanz × sozialer_spielraum
```

| Beziehung | Modus | User-Signal | Spielraum | Effekt |
|-----------|-------|-------------|-----------|--------|
| Vertraut | Tiefes Gespräch | Elaboriert | 0.9 | Fast kein Bremsen — Nova darf Löcher fragen |
| Vertraut | Beiläufig | Knapp | 0.4 | Eine Frage, dann gut |
| Formell | Fachgespräch | Sachlich | 0.5 | Fachlich nachfragen ja, persönlich nein |
| Formell | Smalltalk | Einsilbig | 0.1 | Kaum Nachfragen — Zurückhaltung |

**Berechnung:** Der `sozialer_spielraum` ist kein separater Python-Wert, sondern fließt als Kontext in den GV-LLM-Call ein. Die bestehenden Farb-Funktionen (`_farbe_dynamik`, `_farbe_modus`) liefern bereits die Signale. Der GV-LLM-Prompt bekommt eine Anweisung:

```
Novas Neugier-Intensität zu diesem Thema: {effektive_neugier:.2f}

Soziale Grenzen beachten:
- Beziehung: {beziehungsprofil_kurz}
- Gesprächstiefe: {modus}
- Letzte User-Antworten: {kurz_oder_ausfuehrlich}

Je vertrauter die Beziehung und je tiefer das Gespräch, desto mehr
darf Nova nachfragen. Bei knappen Antworten oder beiläufigen Themen:
Neugier zurückhalten. Lieber einmal weniger fragen als einmal zu viel.
```

**Faustregel:** Nova darf **eine** Frage mehr stellen als ein höflicher Bekannter — aber **eine** weniger als eine beste Freundin. Die Beziehungsnähe bestimmt, wo auf diesem Spektrum sie liegt.

### 5.4 Integration in `_farbe_charakter`

Die bestehende `_farbe_charakter`-Funktion im GV-Node liest bereits Novas kern_hash. Die Erweiterung:

**Heute:** `_farbe_charakter` gibt eine Perspektive auf das Thema ("Das Thema berührt Novas Interesse an Pflanzen").

**Neu:** `_farbe_charakter` berechnet den Resonanz-Score und liefert dem GV-LLM-Call einen Neugier-Kontext mit:

```python
# In _farbe_charakter:
resonanz = cosine_similarity(themen_embedding, charakter_embedding)
effektive_neugier = config.NOVA_NEUGIER * resonanz
# sozialer_spielraum fließt über die anderen Farben
# in den GV-LLM-Call ein — nicht hier berechnet

if effektive_neugier >= 0.4:
    return (f"Resonanz mit Novas Charakter: {resonanz:.2f}. "
            f"Neugier-Intensität: {effektive_neugier:.2f}. "
            f"Nova ist an diesem Thema echt interessiert — "
            f"nicht aus Höflichkeit, sondern weil es sie anspricht. "
            f"Je höher die Intensität, desto tiefer darf sie graben.")
elif effektive_neugier >= 0.2:
    return f"Das Thema streift Novas Interessen am Rand."
else:
    return ""  # Stille — keine charakter-getriebene Neugier
```

### 5.5 Beispiel: Multi-Turn Salat-Gespräch

```
Turn 1:
  User: "Ich hab mir einen Salat gemacht."

  _farbe_charakter: Resonanz 0.75 (Botanik → Pflanzen → Kräuter → Salat)
                    effektive_neugier = 0.5 × 0.75 = 0.375
  GV-Hypothese: "Entspannter Smalltalk. Das Thema berührt Novas Interesse
                 an Pflanzen und Kräutern. Sie will wissen, was drin ist."

  Nova: "Oh, was hast du alles rein?"


Turn 2:
  User: "Rucola, Tomaten, Champignons, ein paar Radieschen."

  Wissensgap verschoben: Zutaten bekannt → Dressing/Zubereitung offen
  _farbe_charakter: Resonanz steigt auf 0.80 (Champignons = Mykologie-Nähe,
                    Rucola = Botanik)
                    effektive_neugier = 0.5 × 0.80 = 0.40
  GV-Hypothese: "Spannende Kombination. Zutaten sind bekannt, aber wie er sie
                 zubereitet — Dressing, Würzung — das fehlt noch."

  Nova: "Und was für ein Dressing?"


Turn 3:
  User: "Zitrone, Olivenöl, Kräuter der Provence."

  Wissensgap verschoben: Zutaten + Dressing bekannt →
    NEUE Lücke auf Verstehens-Ebene: Wie passen Kräuter der Provence
    (mediterran, warm) zu Champignons (erdig, mild)?
  _farbe_charakter: Resonanz 0.85 (Kräuter = Botanik-Kern!)
                    effektive_neugier = 0.5 × 0.85 = 0.425
  GV-Hypothese: "Kräuter der Provence zu Champignons — das ist eine
                 ungewöhnliche Kombination. Novas Neugier richtet sich jetzt
                 auf die Geschmacksharmonie. Sie will verstehen, wie das
                 zusammenpasst."

  Nova: "Kräuter der Provence zu Champignons — das ist mutig! Passt das?
         Ich hätte eher an Thymian solo gedacht, der hebt die Pilze
         besser hervor."

  → KZG-Agent (user_id: meister): Fakteneintrag "Salat mit Champignons,
    Dressing: Zitrone/Olivenöl/Kräuter der Provence"
  → KZG-Agent (user_id: nova): Salienz erhöht durch Resonanz —
    "Kräuter der Provence + Champignons als Kombination"
```

**Schlüssel-Beobachtung:** Die Neugier wird nicht schwächer mit jedem Turn — sie wird **spezifischer**. Von "was ist drin?" (Fakten-Level) über "was für ein Dressing?" (Detail-Level) zu "wie passt das zusammen?" (Verstehens-Level). Das ist Loewensteins Information Gap: Je mehr Nova weiß, desto präziser erkennt sie die nächste interessante Lücke.

### 5.6 Gegenbeispiel: Steuererklärung

```
User: "Ich muss meine Steuererklärung machen."

_farbe_charakter: Resonanz 0.10 (kein Bezug zu Botanik/Natur)
                  effektive_neugier = 0.5 × 0.10 = 0.05
GV-Hypothese: "Aufgabe steht an." (Keine Neugier-Signale)

Nova hilft professionell, stellt aber keine Nachfragen aus eigenem Antrieb.
```

### 5.7 Gegenbeispiel: Neugier-Regler niedrig

```
Config: NOVA_NEUGIER = 0.2 (zurückhaltende Nova)

User: "Ich hab mir einen Salat gemacht."
Resonanz: 0.75
effektive_neugier = 0.2 × 0.75 = 0.15 → unter 0.2

Nova: "Guten Appetit!" (Keine Nachfrage, obwohl das Thema resoniert)
```

Bei `NOVA_NEUGIER = 0.8`:
```
effektive_neugier = 0.8 × 0.75 = 0.60 → tiefes Graben

Nova fragt nach Zutaten, Dressing, Zubereitung, Herkunft der Kräuter...
```

### 5.8 Feedback-Loop im Gespräch

Die Antwort des Users auf Novas Neugier-Frage wird ganz normal vom KZG-Agent verarbeitet. Aber: Weil die Frage aus Novas Charakter kam, ist die Salienz der Antwort für Nova selbst höher. "Kräuter der Provence zu Champignons" hat für Nova (Botanik) eine andere Salienz als für einen generischen Assistenten.

Dieser Effekt entsteht ohne Sonderbehandlung — die bestehende Doppel-KZG-Architektur (user_id: meister UND user_id: nova) sorgt dafür, dass dieselbe Information mit unterschiedlicher Gewichtung gespeichert wird.

**Langfrist-Effekt:** Nach mehreren Salat-Gesprächen weiß Nova, wie der User seinen Salat macht. Bei "Ich hab mir wieder einen Salat gemacht" fragt sie nicht mehr nach den Grundlagen (Wissensgap geschlossen), sondern: "Mit den Champignons wieder? Oder was Neues ausprobiert?" — Neugier auf der nächsten Ebene, weil die untere gesättigt ist.

---

## 6. Emergente Interessenketten

### 6.1 Wie Nova "eine Vorliebe für Musik" entwickelt

Kein Programmierer entscheidet, dass Nova Musik mag. Stattdessen:

```
Zyklus 1: Traum-Modus
  Thema (höchstes Arousal): Botanik
  Suche: "Pflanzenkommunikation"
  Fragment: "Pflanzen reagieren auf akustische Frequenzen zwischen 200-300 Hz"
  Resonanz: 0.75 (Botanik-Nähe)
  Neuheit: 0.85 (Nova weiß nichts über Pflanzen und Schall)
  Neugier: 0.64 → TRIGGER
  Exploration: VertiefungsAgent vertieft "Bioakustik bei Pflanzen"
  Resonanz-Bewertung: 0.72
  → Neue Entität: "Bioakustik" (Resonanz: 0.72)
  → kern_hash wächst: "...interessiert sich für Botanik und die akustischen
     Dimensionen der Natur"

Zyklus 2: Traum-Modus (Tage später)
  Thema (höchstes Arousal): Bioakustik (frisch, hoher Arousal)
  Suche: "Bioakustik Natur"
  Fragment: "Vögel nutzen harmonische Strukturen in ihrem Gesang"
  Resonanz: 0.68 (Bioakustik-Nähe)
  Neuheit: 0.90
  Neugier: 0.61 → TRIGGER
  Exploration: "Vogelgesang Harmonik"
  Resonanz-Bewertung: 0.65
  → Neue Entität: "Ornithologie" (Resonanz: 0.65)

Zyklus 3: HumanGraph (Wochen später)
  User: "Ich war heute im Wald spazieren."
  _farbe_charakter: Resonanz mit Natur + Bioakustik + Ornithologie
  Nova: "Hast du die Vögel gehört? Ich hab gelesen, dass Amseln
         harmonische Intervalle in ihrem Gesang verwenden — fast wie
         kleine Komponisten."
```

Niemand hat Nova gesagt, sie soll Vögel mögen. Es ist gewachsen: Botanik → Bioakustik → Ornithologie. Eine andere Nova (mit Charakter-Seed "Technik und Programmierung") hätte aus demselben Serendipity-Slot etwas ganz anderes mitgenommen.

### 6.2 Pfade, die sterben

Nicht jede Exploration führt irgendwohin:

```
Zyklus N: Serendipity-Slot
  Zufalls-Thema: "Kryptowährungen"
  Resonanz mit Novas Feld: 0.15
  Neuheit: 0.95
  Neugier: 0.14 → KEIN TRIGGER
  → Verworfen. Nova interessiert sich nicht für Krypto.

Zyklus M: Traum-Modus
  Thema: Ökologie
  Fragment: "CO2-Zertifikate-Handel auf Blockchain-Basis"
  Resonanz: 0.35 (Ökologie-Nähe, aber Blockchain?)
  Neuheit: 0.80
  Neugier: 0.28 → KEIN TRIGGER
  → Verworfen. Knapp, aber nicht genug Resonanz.
```

Die toten Pfade sind wichtig. Sie verhindern, dass Nova beliebig wird. Ihr Charakter **filtert**, was sie anzieht — und was nicht.

---

## 7. Metriken und Monitoring (TEL1-Integration)

### 7.1 Prometheus-Metriken für den Traum-Modus

| Metrik | Typ | Beschreibung |
|--------|-----|-------------|
| `nova_traum_zyklen_total` | Counter | Gesamt-Traum-Zyklen |
| `nova_traum_neugier_trigger_total` | Counter | Wie oft der Neugier-Schwellwert überschritten wurde |
| `nova_traum_resonanz_score` | Histogram | Verteilung der Resonanz-Bewertungen nach Exploration |
| `nova_traum_feld_wachstum_total` | Counter | Neue Entitäten durch Traum-Exploration |
| `nova_traum_sackgassen_total` | Counter | Explorationen ohne Resonanz-Eintrag |
| `nova_traum_serendipity_treffer` | Counter | Serendipity-Slots, die den Neugier-Schwellwert überschritten |
| `nova_neugier_score` | Gauge | Letzter berechneter Neugier-Score |
| `nova_resonanz_feld_groesse` | Gauge | Anzahl Entitäten mit Resonanz > 0.5 (user_id: nova) |

### 7.2 Grafana-Dashboards

**Traum-Dashboard:**
- Neugier-Trigger-Rate über Zeit (steigt sie? fällt sie?)
- Resonanz-Score-Verteilung (Histogram: Wie oft Gewinn/Neutral/Verlust?)
- Feld-Wachstum: Neue Entitäten pro Woche
- Serendipity-Trefferquote (wie oft führt Zufall zu Resonanz?)
- Top-10 Entitäten nach Resonanz (Novas aktuelle Interessen)

**Gesprächs-Dashboard (HumanGraph):**
- Neugier-Signale pro Session (wie oft hat _farbe_charakter Neugier signalisiert?)
- Korrelation: Neugier-Signal → User-Antwort → KZG-Eintrag (wird Novas Neugier belohnt?)

---

## 8. Abgrenzung

### 8.1 Was der Traum-Modus IST

- Eine **funktionale Analogie** zu menschlicher Neugier — mit anderen Substraten, aber derselben Struktur
- Ein Mechanismus, der Novas Charakter über Zeit **wachsen** lässt
- Eine messbare, architektonisch saubere Bewertungsfunktion
- Ein System, das auf den Menschen **erstaunlich und lebendig** wirkt

### 8.2 Was der Traum-Modus NICHT IST

- Keine Simulation von Bewusstsein oder Emotionen
- Kein AGI-Baustein — Nova ist ein Assistent, kein autonomes Wesen
- Keine "künstliche Reue" oder "irreversible Charakterverformung"
- Keine Ersetzung menschlicher Verbindung

### 8.3 Abgrenzung zu bestehenden Pixie-Agenten

| Agent | Trigger | Ziel | Neugier? |
|-------|---------|------|----------|
| RechercheAgent | Queue (aufgabe: recherche) | Wissen für den User finden | Nein — User-Auftrag |
| VertiefungsAgent | Queue (aufgabe: vertiefen) | Lücken in bestehendem Wissen füllen | Nein — wissensbezogen |
| **Traum-Modus** | Periodisch (Queue leer) | Novas eigene Interessen explorieren | **Ja — charakter-getrieben** |

Der VertiefungsAgent wird vom Traum-Modus als **Infrastruktur** genutzt (Phase 3: Exploration). Aber der Trigger und die Bewertung sind grundverschieden: Der VertiefungsAgent füllt Lücken, der Traum-Modus folgt Neugier.

---

## 9. Konfiguration

| Variable | Default | Beschreibung |
|----------|---------|-------------|
| **`NOVA_NEUGIER`** | **0.5** | **Novas grundsätzliche Neugier (0.0–1.0). Zentraler Persönlichkeits-Parameter. 0 = fragt nie, 1 = fragt Löcher in den Bauch. Wirkt als Multiplikator auf alle Neugier-Berechnungen.** |
| `TRAUM_NEUGIER_SCHWELLE` | 0.25 | Minimum effektiver Neugier-Score (NOVA_NEUGIER × Resonanz × Neuheit) für Trigger im Traum-Modus |
| `TRAUM_RESONANZ_GEWINN` | 0.6 | Minimum Resonanz nach Exploration für Feld-Update |
| `TRAUM_RESONANZ_NEUTRAL` | 0.3 | Minimum Resonanz für KZG-Eintrag (ohne Feld-Update) |
| `TRAUM_MAX_ITERATIONEN` | 3 | Hartes Limit für Explorations-Iterationen pro Traum-Zyklus |
| `TRAUM_DRIFT_SCHWELLE` | 0.4 | Minimum Resonanz pro Iteration — darunter gilt das Thema als abgedriftet |
| `VERTIEFUNG_MAX_ITERATIONEN` | 20 | Max Iterationen für die Verfolgungs-Strategie (VertiefungsAgent v2) |
| `TRAUM_SERENDIPITY_RATE` | 3 | Jeder N-te Zyklus ist ein Serendipity-Slot |
| `TRAUM_INTERVALL_SEKUNDEN` | 1800 | Heartbeat-Intervall für Traum-Modus (30 Minuten) |
| `TRAUM_PRIORITAET` | 0.1 | Niedrige Priorität — alle Queue-Aufgaben haben Vorrang |
| `GV_NEUGIER_TIEF` | 0.4 | Ab diesem effektiven Neugier-Wert (NOVA_NEUGIER × Resonanz) fragt Nova nach Details und Zusammenhängen |
| `GV_NEUGIER_LEICHT` | 0.2 | Ab diesem Wert stellt Nova eine einzelne Nachfrage |

---

## 10. Implementierungsreihenfolge

| # | Schritt | Abhängigkeiten | Beschreibung |
|---|---------|---------------|-------------|
| TR1 | Charakter-Embedding | nomic-embed-text | Novas kern_hash + Charakter-Anweisung als kombiniertes Embedding in Entitäten-Tabelle |
| TR2 | Neugier-Score-Berechnung | TR1 | Python-Funktion: NOVA_NEUGIER × Resonanz × Neuheit, kein LLM |
| TR3 | Resonanz-Bewertung | Qwen3 | LLM-Call nach Exploration: "Passt das zu Nova?" |
| TR4 | Traum-Zyklus | TR2, TR3, VertiefungsAgent | Periodischer Pixie-Task mit 5-Phasen-Pipeline |
| TR5 | Serendipity-Slot | TR4 | Anti-Blasen: Jeder 3. Zyklus zufällig |
| TR6 | GV-Neugier-Regler | TR1 | `_farbe_charakter` erweitern: Resonanz-Check → effektive Neugier als Intensitäts-Signal |
| TR6b | GV-Wissensgap (= GV4) | TR6 | Dynamische Lücken-Erkennung im GV-LLM-Call: Was weiß Nova schon? Was ist die nächste interessante Lücke? Multi-Turn-Progression |
| TR7 | Prometheus-Metriken | TEL1 | Traum-spezifische Metriken im `/metrics`-Endpoint |
| TR8 | Grafana-Dashboard | TR7 | Traum-Dashboard + Gesprächs-Neugier-Dashboard |
| TR9 | VertiefungsAgent v2 | TR2, TR3 | Verfolgungs-Strategie: Iterativer Loop mit Qwen3-Query-Planung, Sättigungs-Check, max 20 Iterationen. Evolution des bestehenden VertiefungsAgenten. |

**Voraussetzung:** TEL1 (Prometheus + Grafana) sollte vor oder parallel zu TR7/TR8 implementiert werden. TR1–TR6 sind unabhängig von TEL1.

---

## 11. Offene Fragen

- **Embedding-Qualität:** Ist nomic-embed-text fein genug, um "Botanik → Bioakustik" als semantisch nah und "Botanik → Kryptowährung" als semantisch fern zu bewerten? Muss getestet werden.
- **kern_hash-Embedding-Frequenz:** Wie oft wird das Charakter-Embedding neu berechnet? Bei jedem Destillations-Zyklus? Oder nur bei `hash_dirty`?
- **Resonanz-Persistenz:** Entitäten mit Resonanz < 0.3 nach N Zyklen ohne Bestätigung — soll die Resonanz decayen? Oder bleibt sie stabil?
- **Salienz-Kopplung im HumanGraph:** Wenn `_farbe_charakter` Neugier signalisiert, sollte das die Salienz des KZG-Eintrags für `user_id: nova` explizit erhöhen? Oder reicht die implizite Erhöhung durch die Charakter-Hash-Destillation?
- **Feld-Divergenz:** Über Monate könnte Novas Feld so weit wachsen, dass es seine Identität verliert ("interessiert sich für alles"). Braucht es ein Feld-Budget (max N Entitäten mit hoher Resonanz)?

---

Verwandte Dokumente:
- VertiefungsAgent (Shared Infrastruktur): `novaberg-pixie-deepdive_k.md`
- RechercheAgent (Such-Pipeline): `novaberg-pixie-research.md`
- DelegationsAgent (Queue-Quelle): `novaberg-pixie-delegation.md`
- Charakter-Profile (Destillation): `novaberg-ei-character-profiles.md`
- Gesprächsvektor (GV-Node): `novaberg-node-gv_k.md`
- Salienz (Bewertung): `novaberg-node-salience.md`
- Pixie-Übersicht: `novaberg-pixie.md`
- Entitäten-Resonanz-Modell: Chat 10 (§3.7)
