# Novaberg — Die Gedankenkette: ein Gedanke über mehrere Turns (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-gedankenkette_k.md`](novaberg-gedankenkette_k.md) · Ausarbeitung: [`novaberg-gedankenkette_t.md`](novaberg-gedankenkette_t.md) · Diskussion und Ergänzungen: [`novaberg-gedankenkette_e.md`](novaberg-gedankenkette_e.md) · Messungen: [`novaberg-gedankenkette_m.md`](novaberg-gedankenkette_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 9. Was heute im Weg steht

| Ort | Heute | Nötig |
|---|---|---|
| `_stack_aehnliche_entfernen`, Schwelle 0.60 | löscht alles Verwandte **vom Stapel**; die Bibliothek behält es (§1) | Wiederholung entfernen, **Vertiefung behalten** — sie ist das Material der Kette |
| `MAX_BURST = 2` | zählt Zustellungen | zählt **abgeschlossene Gedanken**. Vier Zustellungen zu einem Thema sind ein Gedanke |
| Impuls-Prompt | nur das Wissensstück | plus das bisher Gesagte — und eine **andere Aufgabe je Glied** (§6) |
| `aufnahmebereitschaft` | skaliert nur die Lückensuche | pausiert zusätzlich die Kette (§5) |
| `responder.eigener_gedanke.txt` | sagt viermal, was sie **nicht** tun soll | die Sprechhaltung zum Gegenüber (§7) |
| `sprach_stil`, `beziehungs_dynamik`, `tone` | im Responder nur aus `external` | beim Impuls aus **`internal`** — sie spricht (§7) |
| Kontextfenster | `num_ctx = 32768` auf allen Pfaden des `qwen36`-Connectors | reicht; kein Hindernis |

Der erste Punkt ist der schwerste. Löschen ist endgültig — **zurückstellen wäre besser als entfernen.** Was zurückgestellt ist, kann später erneut geprüft werden, und wenn es dann wirklich veraltet ist, verfällt es über seine TTL von selbst.
