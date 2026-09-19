# Novaberg — Antrieb (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-thinking-drive_k.md`](novaberg-thinking-drive_k.md) · Ausarbeitung: [`novaberg-thinking-drive_t.md`](novaberg-thinking-drive_t.md) · Diskussion und Ergänzungen: [`novaberg-thinking-drive_e.md`](novaberg-thinking-drive_e.md) · Messungen: [`novaberg-thinking-drive_m.md`](novaberg-thinking-drive_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 8. Eingriffspunkte in die bestehende Architektur

> **Hinweis zur Aufteilung (19.09.2026):** Die Eingriffspunkte sind die Planung der Bauteile und stehen deshalb im Bauplan. Eine Reihenfolge und `ZIEL` / `TEST` / `MESSUNG` je Bauteil trägt das Konzept nicht (Befund B7 in [`novaberg-thinking-drive_e.md`](novaberg-thinking-drive_e.md)). §8.2 nennt die Rechnung, die §5.3 in [`novaberg-thinking-drive_t.md`](novaberg-thinking-drive_t.md) als ersetzt führt — Befund B1.

### 8.1 Enricher — Zielsätze laden

Der Enricher trägt heute alle Kontextquellen zusammen (Session, KZG, LZG, Charakter-Hash). Künftig lädt er zusätzlich die aktiven Zielsätze und berechnet die Embedding-Similarity zu den Turn-Themen. Ergebnis: ein neues State-Feld `aktivierte_ziele` mit den Zielsätzen, deren Gravitation über der Schwelle liegt.

### 8.2 Salienz — Gravitationsterm

Die Salienz bekommt den Gravitationsterm als Input. Nach dem LLM-Call (der die Basis-Salienz berechnet) wird der Term in Python addiert: `salienz_final = salienz_basis + gravitationsterm`. Das verändert die KZG-TTL, die Promotion-Wahrscheinlichkeit und den Shadow-Queue-Trigger.

### 8.3 GV-Node — Aktivierte Ziele als Kontext

Der GV-Node erhält die aktivierten Zielsätze als zusätzlichen Kontext für seinen LLM-Call. Die Zielsätze werden als "Gedanken, die mir gerade durch den Kopf gehen" gerahmt — konsistent mit der "Du bist mittendrin"-Philosophie.

### 8.4 Responder — Zwei Emotionsströme

Der Responder bekommt heute den EI-MIKRO-Block (Nutzer-Emotion) und den GV-Block (Gesprächsrichtung). Künftig bekommt er zusätzlich Novas eigenen Emotionszustand als 8-dimensionalen Plutchik-Vektor, natürlichsprachlich formuliert. Zwei getrennte Blöcke:

```
[EI-MIKRO]
Die Stimmung des Gegenübers ist neutral und ruhig.

[NOVA-EMOTION]
Du bist gerade freudig überrascht. Das Thema berührt etwas, das dir am Herzen liegt.
```

Bei gesetztem `emotion_konflikt`-Flag bekommt der Responder einen zusätzlichen Hinweis:

```
[NOVA-EMOTION]
Du bist hin- und hergerissen. Du freust dich für ihn, aber du machst dir Sorgen
wegen der finanziellen Situation. Beides ist echt — zeig beides.
```

Der Charakter entscheidet, wie beides zusammenfließt.

### 8.5 Session-Gedächtnis — Nova-Emotion mitführen

Pro Turn wird Novas Emotionszustand (8-dimensionaler Vektor) im Session-State persistiert. Der Decay wird pro Dimension in Python berechnet, bevor der nächste Turn verarbeitet wird. Zusätzlich werden die `aktivierte_ziele` und das gecachte Turn-Embedding im Session-State gehalten, um bei Themenkonstanz Neuberechnungen zu vermeiden.

### 8.6 Pixie-Agenten — Zielsatz-Produktion

Am Ende jeder Pixie-Aktivität (Recherche, Vertiefen, Träumen) wird ein zusätzlicher Schritt ausgeführt: "Formuliere ein Ziel basierend auf dem Ergebnis. Bewerte die Motivation (0.0–1.0) und die Emotion." Das Ergebnis wird in `ziele` mit `ziel_typ = 'mittelfristig'` geschrieben.

### 8.7 Charakter-Destillation — Langfristige Zielsatz-Produktion

Bei der Charakter-Destillation formuliert Pixie zusätzlich zum Charakter-Hash 1–2 langfristige Zielsätze. Diese werden in `ziele` mit `ziel_typ = 'langfristig'` geschrieben und ersetzen die vorherigen.
