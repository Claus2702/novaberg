# Novaberg — Der Matrix-Kanal: ein Kanal mit zwei Absendern (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-matrix-kanal_k.md`](novaberg-matrix-kanal_k.md) · Ausarbeitung: [`novaberg-matrix-kanal_t.md`](novaberg-matrix-kanal_t.md) · Bauplan und Umstellung: [`novaberg-matrix-kanal_b.md`](novaberg-matrix-kanal_b.md) · Messungen: [`novaberg-matrix-kanal_m.md`](novaberg-matrix-kanal_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

**Eine.** Sie steht in dem Abschnitt, den sie trägt, und bleibt dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_t` §3.2, Absatz *„Entschieden wurde dann anders …“* | Der Homeserver läuft auf Postgres statt auf SQLite — *„weniger verschiedene Systeme“*. Die Umstellung steht in [`novaberg-matrix-kanal_b.md`](novaberg-matrix-kanal_b.md), *Aus §3.2* | 23.08.2026 |

Der Abschnitt nennt keinen Urheber, und der Wortlaut der Entscheidung steht nicht im Konzept; der Abschnitt gibt sie als Ergebnis wieder.

**Im Text als Entscheidung geführt, beim Bauen getroffen — nicht gezählt:**

- `_t` §3.1: `server_name: novaberg.de` statt der IP.
- `_t` §3.3: `exclusive: false` im Namensraum — *„die tragende Entscheidung der AS-Registrierung“*.
- `_t` §3.4: Push statt Polling.
- Abschnitt D (§5), *Verschlüsselung*: der Raum zunächst unverschlüsselt.
- Abschnitt F, bisheriger Kopf, Feld **Abgrenzung**: der Telegram-Kanal ist am 24.08.2026 abgeschaltet — ein Urheber ist nicht genannt.

---

## B. Offen beim Meister

**Zwei** — aus §5 (Abschnitt D unten). §5 nennt keinen Adressaten; gezählt sind die Punkte, die eine Absicht verlangen und keine Messung:

1. **TLS** (Arbeitspaket 4) — *„nicht erledigt, sondern zurueckgestellt“*; ohne WireGuard gehen Passwort und Nachrichtentext im Klartext.
2. **Push zum Handy** — was ohne dauerhaften Tunnel mit einem Impuls von Nova geschieht, *„steht als offener Punkt im Epic“*.

**Offen, ohne eine Entscheidung zu verlangen:**

- [`novaberg-matrix-kanal_b.md`](novaberg-matrix-kanal_b.md), *Aus §3.2*: Die SQLite-Datei bleibt, *„bis der Postgres-Betrieb ueber mehrere Tage getragen hat“*.

---

## C. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Kasten, und mit Grund:

- `_k` §1 — der Telegram-Bot mit dem Präfix `[Du]`; er hat nur einen Absender, und das ist eine Eigenschaft des Protokolls.
- `_t` §3.1 — die LAN-Adresse als Servername; verworfen, weil sie aus DHCP stammt. Der Fall ist am 23.08.2026 eingetreten.
- `_t` §3.2 — SQLite (Erstaufbau, kleinere Berührung); abgelöst am 23.08.2026 (E1).
- `_t` §3.3 — `exclusive: true`; verworfen, weil sich der Mensch mit demselben Account vom Handy anmelden muss. Die Alternative mit zwei Identitäten im Raum ist mit Grund verworfen.
- `_t` §3.4 — Polling wie beim Telegram-Bot; der Homeserver schiebt.
- `_m` §2b — die erste Fassung der Zeugen, die den Sendeweg direkt aufrief; ersetzt durch die eigene Funktion `absender_fuer`.
- `_t` §4, Kasten — die Trennung zwischen Betrieb und Repositorium; seit dem 24.08.2026 verläuft sie zwischen Geheimnis und Struktur.
- Abschnitt D (§5), *TLS* — die Frage, ob FluffyChat `http://` annimmt; am Gerät beantwortet am 23.08.2026.
- Abschnitt F, bisheriger Kopf, Feld **Abgrenzung** — der Parallelbetrieb mit Telegram; überholt am 24.08.2026.

---

## D. Aus dem Konzept: §5

Der Abschnitt, in dem das Konzept seine offenen Punkte führt, ungekürzt.

## 5. Was offen ist

~~**TLS.** … Ob FluffyChat eine `http://`-Adresse annimmt, ist **ungeprueft**.~~

→ **Am 23.08.2026 am Geraet beantwortet: FluffyChat nimmt `http://` an.** Die Verbindung steht, und in der Ereignistabelle liegen Turns, die aus der App kamen. **Damit ist Arbeitspaket 4 nicht erledigt, sondern zurueckgestellt** — der Unterschied ist wichtig: Unverschluesselt geht ueber das lokale Netz und den VPN-Tunnel ein Passwort und jeder Nachrichtentext im Klartext. Innerhalb von WireGuard ist die Strecke bereits verschluesselt; ohne ihn, im heimischen WLAN, ist sie es nicht.

**Die Recherche hat diese Frage nicht beantwortet, das Geraet schon.** Zwei Suchlaeufe fanden keine belastbare Aussage zum Schema-Zwang von FluffyChat — eine halbe Stunde Suche gegen eine Minute Ausprobieren.

**Push zum Handy.** Der Homeserver ist nur erreichbar, solange WireGuard steht. Was ohne dauerhaften Tunnel mit einem Impuls von Nova geschieht, steht als offener Punkt im Epic.

**Verschluesselung.** Der Raum wird zunaechst **unverschluesselt** angelegt. Ein AS kann in einem E2EE-Raum nicht ohne weiteres senden — er braucht Geraeteschluessel und eine Verifikation, und das ist ein eigenes Bauteil. Im privaten Netz auf eigener Maschine ist der Gewinn gering, der Aufwand hoch.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code prüfen oder eine Entscheidung einholen — das ist ein eigener Schritt. B1 bis B5 stammen aus der Sichtung, B6 ist beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | Abschnitt F, bisheriger Kopf, Feld **Status** | *„sieben von acht Arbeitspaketen“*; die Tabelle in `_b` §2 führt nur die Nummern 3 bis 8 | `[gelesen 19.09.2026]` |
| **B2** | `_b` §2, Tabelle | Zeile 6 (Application Service) *„steht, Empfaenger fehlt“*; Zeile 7 (Connector, *„Push-Empfang und zwei Absender“*) *„steht“* | `[gelesen 19.09.2026]` |
| **B3** | `_t` §4 | Die Überschrift *„Wo was liegt“* steht doppelt: als §4 und als Unterabschnitt darin | `[gelesen 19.09.2026]` |
| **B4** | Abschnitt F, bisheriger Kopf, Feld **Voraussetzung** | Der Epic wird in `novaberg-backlog.md` verortet; dort stehen keine Einträge mehr, wo ein Eintrag liegt, sagt `novaberg-backlog-index.md` | `[gelesen 19.09.2026]` |
| **B5** | `_t` §2a, §2c, §2d, §4 | Inhaltlich eher Moduldoku als Konzept: Aufbau, Dateien, Formatierung | `[gelesen 19.09.2026]` |
| **B6** | [`novaberg-matrix-kanal_m.md`](novaberg-matrix-kanal_m.md) §2b und `_t` §4 (Tabelle *Die Dateien des Connectors*) | 26 Zeugen; die Featureliste (*Multi-Channel — Matrix + WireGuard*) nennt *„21 eigene Zeugen“* | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen

Der bisherige Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier.

### Bisheriger Kopf

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Matrix als dritter Kanal, mit Application Service statt Bot
**Stand:** 24. August 2026 (v0.9 — der Kanal ist aus dem Repositorium herstellbar: drei Muster unter `novaberg/matrix/`, zwei Compose-Dienste in der Vorlage, Aufbauanleitung in beiden READMEs; §4. Davor am selben Tag, v0.8 — der abgeloeste Kanal ist abgeschaltet, die Abgrenzung damit ueberholt; davor 23. August 2026, v0.7 — die Figur traegt Namen und Bild, ohne sie bei jedem Start neu abzulegen)
**Pfad:** novaberg/docs/novaberg-matrix-kanal_k.md
**Typ:** Konzept (`_k`)
**Status:** 🟢 **in Betrieb** — sieben von acht Arbeitspaketen; TLS (4) ist zurueckgestellt, siehe §5
**Voraussetzung:** `novaberg-tool-multi-channel.md` (die Kanalarchitektur) · der Epic in `novaberg-backlog.md`
**Abgrenzung:** ~~Der Telegram-Bot bleibt unangetastet und laeuft parallel~~ → **am 24.08.2026 ueberholt.** Der Parallelbetrieb war die Abgrenzung des *Aufbaus*, nicht das Ziel: Der Telegram-Kanal ist abgeschaltet, Matrix traegt ihn allein. `telegram_bot/` liegt weiter im Repositorium, der Dienst laeuft nicht mehr.

---
