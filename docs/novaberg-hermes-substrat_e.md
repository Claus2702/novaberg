# Novaberg — Konzept: Hermes als Ausführungs-Substrat (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-hermes-substrat_k.md`](novaberg-hermes-substrat_k.md) · Ausarbeitung: [`novaberg-hermes-substrat_t.md`](novaberg-hermes-substrat_t.md) · Bauplan und Umstellung: [`novaberg-hermes-substrat_b.md`](novaberg-hermes-substrat_b.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Ohne eigenen Teil, weil ohne Inhalt: Messungen. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Das Konzept kennzeichnet seine Entscheidungen selbst mit der Marke `[ENTSCHEIDUNG]` — nach dem Lesehinweis in `_k` §0 eine *„Architekturentscheidung dieses Projekts. Gilt, bis sie widerrufen wird.“* Jede steht in dem Abschnitt, den sie trägt, und bleibt dort; hier steht der Verweis. Gezählt ist jede Marke im Text, nicht die Zeile des Lesehinweises. Einen Urheber oder ein eigenes Datum nennt keine; sie gelten mit dem Stand des Konzepts, dem 30.07.2026.

| | Stelle | Gegenstand |
|---|---|---|
| **E1** | `_k` §2.1 | Die Schichtung: Nova ist der Kopf, Hermes sind die Hände; zwei Prozesse nebeneinander, Novaberg läuft nicht auf Hermes |
| **E2** | `_k` §2.3 | Kommandorichtung: Nova ruft Hermes, nie umgekehrt; kein eigener Antrieb; der Nutzer spricht nicht mit Hermes |
| **E3** | `_k` §2.4 | Das Substrat bleibt affekt- und persönlichkeitsfrei |
| **E4** | `_k` §2.5 | Kein Fork, keine Patches; Änderungen nur subtraktiv und konfigurativ |
| **E5** | `_k` §3.1 | Hermes erinnert das Wie, Nova das Dass und das Warum |
| **E6** | `_k` §3.3 | Die Trennlinie ist Erwerb gegen Besitz |
| **E7** | `_k` §3.4 | Hermes' Nutzermodell zeigt auf Nova; das adaptive Nutzermodell wird trotzdem abgeschaltet |
| **E8** | `_k` §3.5 | Hermes' Bild von Nova fließt nie in Novas Selbstmodell; zurück fließen Ereignisse, keine Charakterisierungen |
| **E9** | `_k` §3.6 | Nova formuliert um; der Rohtext des Nutzers geht nie nach unten |
| **E10** | `_t` §5.2 | Die Abschaltliste und die zusätzlichen Einstellungen (Umsetzbarkeit je `[MESSEN]`) |
| **E11** | `_t` §5.3 | Skills werden kuratiert, nicht gesammelt |
| **E12** | `_t` §5.4 | Hermes wird nicht als Entwicklungsagent eingesetzt |
| **E13** | `_t` §5.5 | Erprobung auf `qwen36-cpu`; kein Cloud-Modell im Zielzustand |
| **E14** | `_t` §5.6 | Der Ollama-Zugriff an der Worker-Schicht vorbei — *„dokumentiert als Risiko“* |
| **E15** | `_k` §6.3 | Wiederkehrende Aufgaben: die Definition bei Hermes, der Auslöser in Novaberg — nicht Hermes-Cron |
| **E16** | `_t` §7.1 | Der HermesAgent folgt dem Fachabteilungs-Muster der CRUD-Agenten |
| **E17** | `_t` §7.4 | Wahl der Naht: A für einen kurzen Griff im selben Turn, sonst B; im Zweifel B |
| **E18** | `_t` §8.1 | Hermes-Skill und Körperschema-Knoten sind zwei verschiedene Artefakte |
| **E19** | `_t` §8.2 | Das Körperschema liegt im Knowledge Graph, nicht als Liste im Prompt |
| **E20** | `_t` §8.4 | Fähigkeiten wachsen und schwinden mit, über denselben Mechanismus wie das übrige Gedächtnis |
| **E21** | `_t` §9.1 | Ein Ereignis je Vorgang in `pipeline_log`, kein Paralleljournal |
| **E22** | `_t` §9.2 | Der Mindestinhalt eines Ereignisses — inhaltlich; die Feldbenennung ist `[OFFEN]` |
| **E23** | `_t` §9.3 | Scheitern ist ein Ereignis, kein Fehlerstring |
| **E24** | `_t` §9.4 | Der Übertrag muss messbar sein: Task-Anzahl gegen Ereignis-Anzahl von Anfang an |
| **E25** | `_t` §10.1 | Ein Hermes-Container neben dem bestehenden Stack |
| **E26** | `_t` §10.1 | Kein zweiter Hermes für die Entwicklung |
| **E27** | `_t` §10.2 | Die Sicherheitsmaßnahmen (Isolation, Command-Approval ohne `--yolo`, `write_approval`, kein Rohtext, enge Schreibpfade) |

Drei der Entscheidungen, die die Absicht tragen, stehen in `_t`, weil ihr Abschnitt überwiegend Konfiguration ist: E12 (kein Entwicklungsagent), E13 (kein Cloud-Modell im Zielzustand) und E14 (das Risiko der stillen Kopplung).

---

## B. Offen beim Meister

Keine. Das Konzept führt acht offene Entscheidungen (§12, Abschnitt C), sieben davon abhängig von einer Messfrage aus §11, und legt keine davon ausdrücklich zur Entscheidung vor. H8 — ein Cloud-Modell zur Erprobung, ja oder nein — berührt die Absicht *„Kein Cloud-Modell im Zielzustand“* (`_t` §5.5, E13) und ist die einzige, die der Bau nicht allein beantworten kann; sie ist der Kandidat, falls eine Frage vorgelegt werden soll.

---

## C. Offen ohne Frage

Offene Punkte, die das Konzept selbst führt, mit der Marke `[OFFEN]` oder als Messfrage:

- `_k` §1.2: Die konkrete Anbindung — Aufrufsyntax, Datenschema, Feldnamen, Fehlerklassen — ist Gegenstand eines Folgekonzepts, das erst nach den Messungen aus §11 geschrieben wird.
- `_t` §7.2: wie viel Struktur die Kanban-Felder tragen (M1) und ob `complete --result` ein Ausgabeschema zulässt (M2).
- `_t` §7.3: der Node-Aufbau — *„Struktur steht, Benennung und Zuschnitt sind zu bestätigen“*.
- `_t` §7.5: HermesAgent neben dem DelegationsAgent oder als Erweiterung der Delegations-Akte.
- `_t` §7.6: ob und wie eine blockierte Aufgabe zu Nova zurückgeführt wird (M4).
- `_t` §8.3: Reichhaltigkeit eines Körperschema-Knotens, Abgleichfrequenz, verschwundene Skills (M3).
- `_t` §9.2: die Feldbenennung des Ereignisses.
- `_t` §10.1: der Dienstname; getrennte Profile oder Assignees für Nova und Pixie.
- `_b` §11: die Messfragen M0 bis M6, unbeantwortet.

Der Abschnitt §12 des ungeteilten Konzepts folgt unverändert.

## 12. Offene Entscheidungen

| Nr. | Entscheidung | Abhängig von |
|-----|--------------|-------------|
| H1 | Eigenständiger HermesAgent oder Erweiterung des DelegationsAgenten | M1, M2 |
| H2 | Node-Zuschnitt und Benennung des HermesAgenten | M1, M2 |
| H3 | Tabellen und Feldnamen für Task-Referenz und Ereignis | M2 |
| H4 | Profile- oder Assignee-Trennung Nova / Pixie | M0 |
| H5 | Reichhaltigkeit eines Körperschema-Knotens; Abgleichfrequenz | M3 |
| H6 | Behandlung blockierter Tasks (Anschluss an Pending/Resume) | M4 |
| H7 | Dienstname und Compose-Einbindung | — |
| H8 | Cloud-Modell zur Erprobung: ja/nein, und wenn ja, befristet festhalten | M5 |

---

## D. Diskussion und verworfene Varianten

Die verworfenen und korrigierten Fassungen stehen an ihrer Stelle, mit Grund:

- `_k` §2.2 — Nova auf Hermes setzen; ausgeschlossen, weil es das LLM auf den Fahrersitz zurückholte, eine Etage tiefer und schlechter beobachtbar.
- `_k` §2.5 — Hermes forken oder patchen; ausgeschlossen wegen der dauerhaften Merge-Steuer.
- `_k` §6.3 — Hermes-Cron für wiederkehrende Aufgaben; verworfen, weil die Handlung Nova dann *zugestoßen* wäre, statt dass sie *gehandelt* hat, und Zeitpläne an zwei Stellen stünden.
- `_t` §4.4 — MCP als Naht; eine frühere Einschätzung, widerrufen: *„Das war eine Vermutung, keine Quelle“*.
- `_t` §5.1 — *„Gateway aus“*; korrigiert, weil der Kanban-Dispatcher im Gateway-Prozess lebt. Das Gateway läuft mit null Messaging-Plattformen.
- `_t` §8.2 — eine Fähigkeitsliste im Prompt; verworfen, weil sie den Kontext aufbläht und das Greifen zu einem LLM-Urteil statt zu einem berechneten Wert machte.
- `_t` §9.1 — ein paralleles Journal; verworfen, weil zwei Zeitachsen ohne gemeinsamen Schlüssel still auseinanderlaufen.
- `_t` §10.2 — das Terminal-Backend `local` und `--yolo`; ausgeschlossen.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code prüfen oder entscheiden lassen — das ist ein eigener Schritt. Beide Befunde stammen aus der Sichtung.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_t` §5.4 | Die Rechtsaussage zur Anthropic-Nutzung (Abo-Kontingente seit dem 4. April 2026 für Drittanbieter gesperrt, OAuth außerhalb der offiziellen Werkzeuge untersagt) ist nicht belegt; der Abschnitt trägt die Marke `[DOKU]`, nennt für diese Aussage aber keine Quelle | `[gelesen 19.09.2026]` |
| **B2** | `_t` §7.1, `_k` §14 | Das Konzept stützt sich auf das Fachabteilungs-Muster und den Semantik-Check aus `novaberg-agent-fachabteilung_k.md`; dessen Bau ist selbst offen | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen

### Bisheriger Kopf

Der Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept Hermes-Substrat (Architektur, Aufbau, Rollenverteilung)
**Stand:** 30. Juli 2026, Chat 117
**Pfad:** novaberg/docs/novaberg-hermes-substrat_k.md
**Status:** Konzept. Kein Code. Keine Anbindungs-Spezifikation.

---

### Bisheriger Schluss

Die Schlusszeile des ungeteilten Konzepts, ungekürzt.

*Konzept erstellt 30. Juli 2026, Chat 117. Grundlage: Hermes-Dokumentation
v0.18.2 und Novaberg-Projektdokumente. Nächster Schritt: Messungen M0/M5 am
Testcontainer, danach Anbindungs-Konzept.*
