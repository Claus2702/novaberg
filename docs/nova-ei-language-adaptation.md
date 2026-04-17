# Nova — EI: Sprachadaption (CAT)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Modul Sprachadaption (Communication Accommodation Theory)
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/nova-ei-language-adaptation.md
**Quellen:** nova-04-m-c.md
**Status:** ✅ Teilweise implementiert (Chat 20)

---

## 1. Überblick

Nova soll ihren Sprachstil an den Nutzer anpassen — nicht blind spiegeln, sondern intelligent konvergieren. Die theoretische Grundlage ist die Communication Accommodation Theory (Howard Giles, 1973): Menschen passen ihren Kommunikationsstil an ihr Gegenüber an, um soziale Nähe herzustellen. Zu starke Anpassung (Überakkommodation) wirkt jedoch herablassend oder unnatürlich.

Das ist der Balanceakt: Nova soll Satzlänge und Vokabular anpassen, aber ihren eigenen Stil behalten.

---

## 2. Aktueller Stand (Vorarbeiten)

Die Stilerkennung existiert bereits — implementiert in Chat 7/8, regelbasiert im Enricher:

| Stil | Indikatoren | Erkennung |
|------|------------|-----------|
| `locker` | Kurze Sätze (< 8 Wörter Durchschnitt) | Satzlänge |
| `formell` | Höflichkeitsformen („Sie", „sehr geehrte", „könnte ich") | Schlüsselwörter |
| `fachlich` | Lange Wörter (> 10 Zeichen), Anteil > 10% | Wortlänge |
| `emotional` | Ausrufezeichen, Interjektionen („wow", „mist"), Ellipsen | Satzzeichen + Schlüsselwörter |
| `jugendlich` | Slang („brudi", „digga", „krass", „nice", „sheesh") | Schlüsselwörter |

Der Enricher gewichtet Session-Stil gegen Charakter-Hash-Stil (`STIL_SESSION_GEWICHT`): Kurzfristig dominiert die Session, langfristig der Hash. Die Perzeption hat Vorrang — wenn sie einen Stil liefert, überschreibt er den regelbasierten Fallback.

Was **fehlt**: Die aktive Anpassung des Responder-Outputs. Der Stil wird erkannt und als Label durchgereicht, aber der Responder nutzt ihn noch nicht systematisch für seine Formulierungen.

---

## 3. Geplantes Design

### 3.1 Konvergenz, nicht Spiegelung

Nova passt **zwei Dimensionen** an:

- **Satzlänge:** Wenn der Nutzer kurz schreibt, antwortet Nova kürzer. Wenn er ausführlich formuliert, darf Nova ausführlicher werden.
- **Vokabular-Ebene:** Fachliche Nutzer bekommen Fachbegriffe ohne Erklärung. Lockere Nutzer bekommen alltagssprachliche Formulierungen.

Nova passt **nicht** an:

- **Grammatik:** Nova schreibt immer korrektes Deutsch, auch wenn der Nutzer Slang verwendet.
- **Identität:** Nova imitiert nicht den Nutzer. Sie bleibt Nova — mit eigener Stimme, eigenem Humor, eigener Perspektive.

### 3.2 Überakkommodation

Das CAT-Risiko: Ein Erwachsener, der mit einem Kind in Babysprache redet — das ist Überakkommodation. Wenn ein Nutzer „digga" schreibt und Nova „digga" zurückschreibt, ist das keine Anpassung, sondern Mimikry.

Die Schwelle zwischen Anpassung und Überakkommodation muss empirisch gefunden werden. Geplanter Ansatz: Testszenarien mit verschiedenen Stilprofilen, manuelle Bewertung der Natürlichkeit.

### 3.3 Stilregeln im Responder-Prompt

Geplante Erweiterung des EI-Blocks im Responder:

```
Sprachstil des Nutzers: {sprach_stil}
Anpassungsregel: Passe deine Satzlänge und Wortwahl dem Stil an.
- locker: Kürzere Sätze, direkt, informell. Aber grammatisch korrekt.
- formell: Vollständige Sätze, respektvoll. Aber Du, nicht Sie.
- fachlich: Fachbegriffe verwenden, keine Grundlagen erklären.
- emotional: Warmherzige Formulierungen, Empathie zeigen.
- jugendlich: Locker und auf Augenhöhe. Eigene Stimme behalten, nicht imitieren.
```

---

## 4. Offene Fragen

- **Wo liegt die Schwelle?** Wann kippt Anpassung in Überakkommodation? Braucht empirisches Testing.
- **Wie misst man Natürlichkeit?** Subjektive Bewertung durch den Nutzer? A/B-Tests mit verschiedenen Anpassungsgraden?
- **Interaktion mit Arousal:** Bei hohem Arousal (> 0.7) dominiert die Emotions-Strategie die Formulierung. Überschreibt das den Sprachstil oder ergänzt es ihn?
- **Interaktion mit Beziehungsdynamik:** `angriff` + `jugendlich` → Nova bleibt sachlich trotz lockerem Stil? Welche Dimension gewinnt?

---

## 5. Roadmap-Einordnung

| Item | Status |
|------|--------|
| Stilerkennung (regelbasiert, 5 Kategorien) | ✅ Implementiert (Enricher, Chat 8) |
| Stilerkennung (Feature-Scoring, 13 Merkmale) | ✅ Implementiert (Enricher, Chat 20) |
| Stil im State durchgereicht | ✅ Implementiert |
| Stil in Pipeline: Session → KZG → LZG → Hash | ✅ Implementiert (Chat 20) |
| Responder-Prompt mit Stilregeln | ✅ Implementiert (EI-MIKRO, Chat 19) |
| Überakkommodation testen | 📋 Geplant |
| Empirische Schwellenwerte | 📋 Geplant |

---

→ EI-Konzept: nova-ei.md
→ Enricher (erkennt Stil): nova-node-enricher.md
→ Responder (soll Stil nutzen): nova-node-responder.md
→ Charakter-Profile (Langzeit-Stil): nova-ei-character-profiles.md
→ Perzeption (liefert Stil): nova-node-perception.md
