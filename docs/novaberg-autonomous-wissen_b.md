# Novaberg — Autonomes Wissen (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-autonomous-wissen_k.md`](novaberg-autonomous-wissen_k.md) · Ausarbeitung: [`novaberg-autonomous-wissen_t.md`](novaberg-autonomous-wissen_t.md) · Diskussion und Ergänzungen: [`novaberg-autonomous-wissen_e.md`](novaberg-autonomous-wissen_e.md) · Messungen: [`novaberg-autonomous-wissen_m.md`](novaberg-autonomous-wissen_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 9. Implementierungsreihenfolge

| Phase | Umfang | Abhaengigkeit |
|-------|--------|-------------|
| **Phase 1** | `tools/dateien/operationen.py` | Keine |
| **Phase 2** | `autonomous_wissen`-Tabelle + Embedding-Funktionen | Phase 1 |
| **Phase 3** | RechercheAgent: Keep/Discard-Gate, Datei-Schreiben, Embedding | Phase 1+2 |
| **Phase 4** | VertiefungsAgent: Mandelbrot-Navigation, Block-Ergaenzung | Phase 1+2+3 |
| **Phase 5** | Traum-Modus: Assoziatives Verknuepfen, NEVER-STOP-Loop | Phase 1+2, Epic 8 |
| **Phase 6** | Enricher: Sechste RAG-Quelle | Phase 2 |
| **Phase 7** | Prune-Zyklus (INDEX.md, Konsolidierung) | Phase 3+ |
| **Phase 8** | Auftragsmodus (mehrstufige User-Auftraege) | Phase 3, Pixie-Plugin-Architektur |

---

## Aus §11.6 — Gewichtung, Sättigung und Verfall nach dem Knoten-Schema

Kurve, Startwerte und Spalten (§11.6) stehen in [`novaberg-autonomous-wissen_t.md`](novaberg-autonomous-wissen_t.md). Hier stehen die Bauberichte dazu.

**Gebaut am 04.08.2026** in `db/init.sql`, mit drei Zusicherungen im Schema statt im Code: Das Paar-Tripel trägt — anders als `lzg_knoten` — **keinen Vorgabewert**, weil eine leere Tabelle sich den strengeren Weg leisten kann; `salienz_anfang` ebenfalls nicht; und `dateipfad` ist `UNIQUE`, damit Verstärken (§11.5) von Doppelt-Anlegen unterscheidbar bleibt. Die Zusicherungen sind live geprüft: Ein Schreibversuch ohne einen der vier Werte scheitert an der Datenbank, eine vollständige Zeile gelingt, eine zweite Zeile zum selben Pfad nicht.

**`WIS-3` gebaut am 04.08.2026** — der Schreibpfad am `recherche`-Agenten. Der Pfadwächter prüft zwei Bedingungen: innerhalb der Wurzel **und** außerhalb des Arbeitsbaums, jeweils am aufgelösten Pfad, damit kein `..` daran vorbeiführt. Das Anwendungsverzeichnis leitet er aus der Lage seines eigenen Moduls ab statt aus der Konfiguration — ein Wächter, den eine Umgebungsvariable verschieben kann, bewacht nichts.

> **Ein gescheiterter Durchlauf hinterlässt einen Bericht.** §5.1 sagt das, und der erste Messlauf hat gezeigt, warum es zählt: Eine Recherche scheiterte nach rund fünfzehn Minuten an der Zwischen-Destillation und kehrte zurück, bevor irgendetwas geschrieben war. Ohne den Bericht beginnt die nächste Lagebeurteilung bei null und sucht dasselbe noch einmal. Das Gate wird dabei **übergangen** — ein Modellaufruf über ein leeres Blatt wäre eine Frage ohne Gegenstand.

**Was damit noch nicht gebaut ist:** Die Kurve selbst. Die Spalten stehen, aber niemand schreibt sie — `gewicht_roh`, `gewicht_absolut` und `gewicht_decay` bekommen ihre Werte erst mit `WIS-3` (Schreibpfad) und `WIS-5` (Verfall). Eine vorhandene Spalte ist keine gerechnete Größe.

---

## Audit (seit 18.09.2026)

**Der Dienst belegt jeden Lauf selbst** im `hintergrund_log`, unter der Aufgabe `wissen_rueckweg` (`BaseAgent._audit`, `80d4b37`): `gestartet` mit Auftragsart und Thema, dann `erledigt` mit dem Ausgang (geschrieben oder nicht, und warum) oder `fehler`. Bis zum 18.09.2026 hatte der Rückweg keine einzige Zeile im `hintergrund_log`. Eine Ausnahme aus dem Lauf wird dort als `fehler` belegt, nicht weitergeworfen. Der Pixie-Dispatch schreibt nur noch, wenn der Dienst schweigt — eine entkommene Ausnahme oder ein fehlender Agent (`novaberg-convention-nmcp.md` §8.4, Entscheidung vom 18.09.2026).
