# Novaberg — Der Matrix-Kanal: ein Kanal mit zwei Absendern (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-matrix-kanal_k.md`](novaberg-matrix-kanal_k.md) · Ausarbeitung: [`novaberg-matrix-kanal_t.md`](novaberg-matrix-kanal_t.md) · Diskussion und Ergänzungen: [`novaberg-matrix-kanal_e.md`](novaberg-matrix-kanal_e.md) · Messungen: [`novaberg-matrix-kanal_m.md`](novaberg-matrix-kanal_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 2. Die Bauteile

| # | Teil | Zustand am 23.08.2026 |
|---|---|---|
| 3 | **Homeserver** — Synapse, `ki_synapse`, Port 8008, **auf Postgres** | **steht** |
| 4 | TLS-Zugang — Reverse Proxy mit Zertifikat | **zurueckgestellt**, siehe §5 |
| 5 | **Accounts** — `@meister` und `@nova`, beide im AS-Namensraum | **steht** |
| 6 | **Application Service** — Registrierung geladen | **steht**, Empfaenger fehlt |
| 7 | **Connector** — `matrix_bot/`, Push-Empfang und zwei Absender | **steht** |
| 8 | **Client-Test** — FluffyChat verbunden, Turns aus der App in der Ereignistabelle | **steht** |

> **Hinweis zur Aufteilung (19.09.2026):** *Im Betrieb belegt, 23.08.2026* und *Die Messung, die den Kanal rechtfertigt* standen hier; sie stehen in [`novaberg-matrix-kanal_m.md`](novaberg-matrix-kanal_m.md), *Aus §2*.

---

## Aus §3.2 — Postgres statt SQLite

Die Entscheidung und ihre Begründung stehen in [`novaberg-matrix-kanal_t.md`](novaberg-matrix-kanal_t.md) §3.2. Hier steht die Umstellung.

**Die Migration in Zahlen (23.08.2026):**

| Schritt | Beleg |
|---|---|
| Datenbank `synapse` angelegt | `LC_COLLATE=C`, `LC_CTYPE=C` — fuer Synapse zwingend |
| `synapse_port_db` gelaufen | alle Tabellen portiert |
| **Vergleich beider Seiten** | 6 Tabellen, **0 Abweichungen** (2 Nutzer, 22 Events, 1 Raum, 4 Tokens, 3 Mitgliedschaften, 8 Zustandsereignisse) |
| Betrieb danach | ein echter Turn: `events` 22 → **23**, die Nachricht in Postgres wiedergefunden |

> **`LC_COLLATE=C` ist nachtraeglich nicht aenderbar** — eine bestehende Datenbank mit sprachabhaengiger Kollation muesste neu aufgebaut werden. Synapse verlaesst sich auf byteweise Ordnung; `en_US.utf8`, wie es die uebrigen Datenbanken dieses Servers tragen, ordnet anders.
>
> **`gedaechtnis` blieb unberuehrt.** Die neue Datenbank steht daneben, nicht darin.

**Die SQLite-Datei liegt als `homeserver.db.vor-migration` daneben** und wird nicht mehr gelesen. Sie bleibt, bis der Postgres-Betrieb ueber mehrere Tage getragen hat — ein Rueckweg, der nichts kostet.
