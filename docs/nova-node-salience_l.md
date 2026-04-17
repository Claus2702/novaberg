# 02_L_c — Lesson: Salienz-Mittlung

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Emotionale Signale verwässert durch Antwort-Kontext
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/nova-node-salience_l.md
**Ursprung:** nova-02-l-c.md
**Typ:** Lesson (L)
**Entdeckt:** Chat 3 (14. März 2026)
**Betrifft:** Salienz (`01_M_g`)

---

## 1. Symptom

„Ich bin total überfordert mit der Arbeit, alles wird zu viel!" — dieser Prompt erhielt Salienz 0.40 statt der erwarteten 0.70+. Stress-Signale wurden nicht erkannt. Der Eintrag landete nicht im Kurzzeitgedächtnis.

---

## 2. Ursache

Der Salienz-Agent erhielt als Input den gesamten Turn — User-Eingabe UND Assistenten-Antwort:

```
User: Ich bin total überfordert mit der Arbeit!
Assistent: [200 Wörter beruhigende, sachliche Antwort mit Tipps]
```

Das LLM mittelte über den gesamten Input. Die kurze, emotionale User-Eingabe ging in der langen, ruhigen Assistenten-Antwort unter. 20 Wörter Stress + 200 Wörter Sachlichkeit = Durchschnitt: moderate Salienz.

> **Das Mittlungs-Problem:** Ein LLM, das einen kurzen emotionalen Input UND eine lange sachliche Antwort bewertet, mittelt über beides. Die Länge der Antwort bestimmt das Ergebnis stärker als die Intensität der Eingabe.

---

## 3. Die Lösung

Zwei Maßnahmen, die zusammen wirken:

### 3.1 Lagebild / Bewertungsobjekt

Die Assistenten-Antwort steht im **Lagebild** (oben im Prompt), die User-Eingabe im **Bewertungsobjekt** (unten im Prompt):

```
═══ LAGEBILD (Hintergrund, nicht bewerten) ═══
Antwort des Assistenten: [200 Wörter sachliche Antwort]

═══ BEWERTUNGSOBJEKT (nur diesen Teil bewerten) ═══
Eingabe des Nutzers: Ich bin total überfordert mit der Arbeit!
```

### 3.2 Recency Bias nutzen

Das Bewertungsobjekt steht bewusst am Ende des Prompts. LLMs gewichten das zuletzt Gelesene stärker — der Recency Bias wird hier als Feature genutzt, nicht als Bug. Die emotionale User-Eingabe ist das Letzte, was das LLM sieht, bevor es die Salienz bewertet.

### 3.3 Explizite Anweisung

Im System-Prompt der Salienz:

```
Bewerte die Salienz AUSSCHLIESSLICH anhand der EINGABE DES NUTZERS.
Die Antwort des Assistenten ist Hintergrund-Kontext und darf die Bewertung NICHT beeinflussen.
```

---

## 4. Ergebnis

| Prompt | Vorher | Nachher |
|--------|--------|---------|
| „Total überfordert mit der Arbeit!" | 0.40 | **0.70** |
| „Streit mit Nachbarn belastet mich!" | — | **0.70** |
| „Hallo, wie geht es dir?" | — | **0.20** |
| „Ich liebe italienische Küche!" | — | **0.60** |

---

## 5. Generalisierbare Erkenntnis

> Wenn ein LLM ein kurzes Signal in einem großen Kontext bewerten soll, gewinnt immer der Kontext — nicht das Signal. Die einzige Lösung: Das Signal räumlich isolieren (Bewertungsobjekt-Trennung) und zeitlich bevorzugen (Recency Bias).

Dieses Prinzip gilt nicht nur für die Salienz. Es betrifft jede Situation, in der ein LLM einen spezifischen Teil eines größeren Inputs bewerten soll — Sentiment-Analyse, Relevanz-Scoring, Dringlichkeits-Bewertung.

---

→ Salienz-Node: `01_M_g`
→ Kontaminations-Lesson (übergeordnet): `01_L_a`
