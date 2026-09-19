# Novaberg — Skills (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-thinking-skills_k.md`](novaberg-thinking-skills_k.md) · Ausarbeitung: [`novaberg-thinking-skills_t.md`](novaberg-thinking-skills_t.md) · Diskussion und Ergänzungen: [`novaberg-thinking-skills_e.md`](novaberg-thinking-skills_e.md) · Messungen: keiner. Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 11. Phasen-Plan

Skills sind durch den Cognitive-Pipeline-Phasen-Plan abgedeckt — Phase B und Phase C dort sind die Skill-Phasen.

### Phase B (aus Cognitive-Pipeline §11) — Skill-Speicher und -Anwendung

**Ziel hier:** Skill-Speicher anlegen, manuell geschriebene Skills für die häufigen Aufgabentypen, Skill-Lookup im Cognitive Loop aktiv.

**Skills-spezifische Schritte:**

1. Skill-Verzeichnis-Struktur anlegen (`~/ki-assistent/novaberg/server/skills/`).
2. Skill-Format-Validator schreiben (Front-Matter-Check, Aufgabentyp-Existenz).
3. Skill-Index-Aufbau beim Server-Start.
4. Drei bis fünf manuelle Skills für häufige Aufgabentypen schreiben (Wetter, Notiz-Listen, Termin-Anlage).
5. Skill-Lookup im Pipeline-Schritt 4.7 aktivieren.
6. Skill-Executor-Prompt im Schritt 4.8 mit Skill-Text-Block.
7. Live-Beobachtung: Welche Skills werden befolgt, welche umgangen?

**Erfolgskriterium:** Drei manuelle Skills sind aktiv, nachweislich in mindestens 80% der passenden Fälle befolgt, ohne Werkzeug-Schicht-Verletzungen.

### Phase C (aus Cognitive-Pipeline §11) — Selbst-lernende Skills

**Ziel hier:** Pixie schreibt und ändert Skills autonom auf Basis von Negativ-Feedback.

**Skills-spezifische Schritte:**

1. Reflexions-Queue schreiben (Redis-Liste `skill_reflektion:{user_id}`).
2. Pipeline-Marker-Schreibung in den entsprechenden Schritten (4.6, 5.1–5.4).
3. Pixie-Task `skill_pflege` schreiben — periodisch die Queue lesen, pro Marker entscheiden.
4. Skill-Schreib-LLM-Call mit Format-Konvention.
5. Skill-Edit-LLM-Call analog.
6. Status-Übergänge implementieren (`entwurf` → `aktiv` nach n erfolgreichen Anwendungen).
7. Decay-Mechanik (`gewicht`-Reduktion bei wiederholtem Negativ-Feedback).
8. Git-Versionierung des Skill-Verzeichnisses einrichten.

**Erfolgskriterium:** Nova schreibt eigenständig mindestens drei Skills aus Praxis-Beobachtung, davon mindestens zwei stabil (kein Re-Edit nach erster Anwendung).
