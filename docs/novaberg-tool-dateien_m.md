# Novaberg — Tool: Datei-Operationen (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-tool-dateien_k.md`](novaberg-tool-dateien_k.md) · Ausarbeitung: [`novaberg-tool-dateien_t.md`](novaberg-tool-dateien_t.md) · Diskussion und Ergänzungen: [`novaberg-tool-dateien_e.md`](novaberg-tool-dateien_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er steht hier, weil er die Messung der Ankertreue trägt.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Datei-Operationen — Intelligentes Lesen und Bearbeiten von Dateien
**Stand:** 18. August 2026 (Leseschicht, Schreibschicht und Versionierung gebaut); davor 29. April 2026, Chat 70

> **Bauzustand am 18.08.2026.** Die Operationen dieses Konzepts sind nicht mehr Entwurf:
>
> | Modul | Inhalt | Zeugen |
> |---|---|---|
> | `tools/dateien/operationen.py` | `struktur_analysieren`, `block_lesen`, `zeilen_lesen`, `datei_grep`, `metadaten_lesen`, `datei_suchen` | 26 |
> | `tools/dateien/redaktion.py` | `block_ersetzen`, `block_anfuegen`, `block_einfuegen`, `str_ersetzen`, `metadaten_setzen` | 20 |
> | `tools/dateien/versionierung.py` | §3.4 vollständig, dazu `aktuell_lesen` und `paarung_pruefen` | 20 |
> | `tools/dateien/hand.py` | die Auftragsform `DATEI: {json}` | 22 |
>
> **Zwei Abweichungen gegenüber diesem Konzept**, beide begründet: Die Wurzel ist bei jedem Aufruf ein **Pflichtargument** ohne Vorgabewert — ein Lesewerkzeug ohne Zonenangabe ist eine Zone ohne Grenze. Und `str_replace_in_block` heißt `str_ersetzen` mit optionalem `header`, weil der Suchraum bei Dateien ohne Blöcke ohnehin die ganze Datei ist.
>
> **Die Ankertreue ist gemessen, nicht angenommen:** 30 von 30 zeichengenaue, eindeutige Anker an echten Wissensdateien — `gemma4-gpu` mit Median 1,7 s, `qwen36-cpu` mit 17,9 s. **Was fehlt, ist der Aufrufer.**
**Pfad:** novaberg/docs/novaberg-tool-dateien_k.md
**Quellen:** Chat 70 (autoresearch-Analyse, Claude Code Leak, SWE-agent, Aider, Letta)

---
