# Novaberg — Frames (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-thinking-frames_k.md`](novaberg-thinking-frames_k.md) · Ausarbeitung: [`novaberg-thinking-frames_t.md`](novaberg-thinking-frames_t.md) · Diskussion und Ergänzungen: [`novaberg-thinking-frames_e.md`](novaberg-thinking-frames_e.md) · Messungen: keiner. Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

Hier stehen die Teile des Konzepts, die berichten, was gebaut oder entworfen ist, und die Implementierungs-Reihenfolge. Der Phasen-Plan selbst liegt im Pipeline-Konzept (`novaberg-thinking-cognitive-pipeline_k.md` §11).

## Aus §3.1 — Die Frame-Klassen

Die Frame-Klassen stehen in [`novaberg-thinking-frames_k.md`](novaberg-thinking-frames_k.md); der Nachtrag zum Werkzeug-Frame stand dort unter den *Werkzeug-Frames*.

> **Nachtrag 14.09.2026:** Die erste Form eines Werkzeug-Frames ist entworfen — als **Objekt-Merkmal in der Anmeldung eines Dienstes** (Scheibe 12 des Lage-Konzepts, Teil C): Der Dienst beschreibt das Objekt, das er bedient, und eine gerechnete Nähe zu den akuten Objekten der Sachlage entscheidet, ob der Empfang ihm ein Objekt zuordnet. Der TimelineAgent bedient jedes Objekt mit Bezug zu einem Zeitpunkt. Nicht gebaut.

---

## Stand-Block zwischen §4 und §5

Der Stand-Block des ungeteilten Konzepts, ungekürzt. Er stand zwischen §4 ([`novaberg-thinking-frames_k.md`](novaberg-thinking-frames_k.md)) und §5 ([`novaberg-thinking-frames_t.md`](novaberg-thinking-frames_t.md)) und berichtet, was von §3 bis §7 in Konversationsfassung gebaut ist.

**Stand 28.08.2026:** Die Konversationsfassung ist gebaut — der Sachlage-Knoten (`novaberg-thinking-lage_k.md` §3) erhebt je Turn Objekte mit Frame-Klasse (§3.1), Akutheit (§4, latent ohne offene Slots: §4.3 als Prüfung im Code) und gedeckten/offenen Slots aus dem Turn und aus Novas Antworten. **Ohne Frame-Lager (§7, §9)**: Die typischen Eigenschaften einer Sache erfindet das Modell je Turn neu — »Geburtstag« bekam einmal `wer`, einmal `Anlass`. Validierung (§5) und Plausibilität (§6) sind nicht gebaut. **Seit dem 28.08.2026, spät, werden offene Slots gegen den Bestand gehalten** (Frame-Auflöser in der Konversationsfassung, `novaberg-thinking-lage_k.md` §4 Scheibe 6): ein eigener Call prüft je akutem Objekt, ob ein Eintrag aus KZG, LZG, Bibliothek, Aufzeichnungen oder Kalender eine offene Eigenschaft beantwortet — gedeckt mit Quelle, sonst offen; im Labor 5/5 richtig und 0/5 falsch. Ohne Frame-Lager bleibt die Lücken-Menge selbst je Turn erfunden. **Seit dem 29.08.2026 ist auch §6 in der Konversationsfassung gebaut** (Scheibe 7): Behauptungen des Nutzers über die akute Sache werden gegen Weltwissen geprüft, in den vier Stufen aus §6.2; Labor 0/12 Fehlalarme, 18/18 nicht-plausible gemeldet, die Stufe im Mittel eine zu hoch. §5 (Cross-Frame) bleibt offen. **Seit dem 29.08.2026, vormittags, trägt jeder offene Slot seinen Wissensträger** (Scheibe 8: `nutzer` / `welt` / `nachschlagen`) — die Lückenbehandlung aus dem Pipeline-Konzept §4.6 in der Konversationsfassung: nur eine `nutzer`-Lücke wird gefragt, die anderen beantwortet Nova, notfalls mit einer Websuche. **Seit dem 29.08.2026, mittags, trägt jeder gedeckte Slot seinen Sprecher** (Scheibe 9: `nutzer` / `nova`) — ein Slot, den der Nutzer gefüllt hat, bleibt sein Gedanke, und der Verfasser nimmt ihn als seinen auf.

---

## Aus §9.1 — Schema (vorläufig)

Das vorläufige Schema des Frame-Lagers steht in [`novaberg-thinking-frames_t.md`](novaberg-thinking-frames_t.md); der Nachtrag stand dort unter dem *Hinweis zur Klassen-Konvention*.

> **Nachtrag 13.09.2026 — ein Teil des Lagers steht, in Konversationsfassung.** Scheibe 11 des Lage-Konzepts (`novaberg-thinking-lage_k.md` §4) legt je gerechnetem Turn die Objekte der Sachlage ab: `sachlage_objekt` (eine Zeile je Paar und Objektname, mit später gebundener `entitaet_id`), `sachlage_objekt_turn` (die Objekte je Turn) und `sachlage_eigenschaft` (je Slot sein Wert mit Quelle, Sprecher, `timeline_id` und Historie — ein neuer Wert löst ab, `aktiv = FALSE` und `t_invalid`, statt zu überschreiben). **Anders als das Schema oben:** Verankert ist das Objekt an `entitaeten` statt an einem Präfix-String `frame_klasse`, die Slots stehen als Zeilen statt als JSONB, es gibt keinen Decay (protokolliertes Faktum) und keine `haeufigkeit`. Der Rückweg läuft über den Frame-Auflöser: gespeicherte Werte der akuten Objekte werden ihm angeboten. **Konzept bleiben** die Lernmechanik aus §7.3 und die Operationen aus §9.2 — Konsens, Schema-Aggregat, Korrektur-Gewichtung, Decay.

---

## Aus §12 — Offene Punkte und nächste Schritte

§12.1 und §12.3 stehen in [`novaberg-thinking-frames_e.md`](novaberg-thinking-frames_e.md), Abschnitt C.

### 12.2 Implementierungs-Reihenfolge

Die Phasen-Planung wandert in das Folge-Dokument `novaberg-thinking-cognitive-pipeline_k.md`, weil Pipeline-Mechanik dort orchestriert wird. Hier nur die Markierung, dass die Frame-Schicht **vor** der Skill-Schicht implementiert werden muss — Skills brauchen Frames als Input.

Aus dem Chat-80-Stand bleibt der Hinweis, dass die Phase 0 (Vorbedingungen) weiterhin gilt:

- M2.5b — FaktenAgent als echter Agent statt Plugin
- TIMELINE-PAIR-MIGRATION
- NOTIZEN-PAIR-MISSING
- FAKTEN-PAIR-IGNORED

Diese Migrations-Themen sind unabhängig vom Frame-Konzept anzugehen — sie bereinigen das Paar-Schema und sind Voraussetzung für den FaktenAgent-Push in §9.3.
