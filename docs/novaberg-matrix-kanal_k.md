# Novaberg — Der Matrix-Kanal: ein Kanal mit zwei Absendern

**Absicht:** Matrix ist ein Kanal mit zwei Absendern: Was der Mensch an einem anderen Client sagt, erscheint im Raum als Nachricht des Menschen und nicht als Zitat der Figur — als `sender` im Ereignis, nicht als Präfix im Text.
**Stand:** 24. August 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Multi-Channel — Matrix + WireGuard* 🟢 · *Multi-Channel — Telegram* ⚫ (abgeschaltet) — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-matrix-kanal_t.md`](novaberg-matrix-kanal_t.md) · [`novaberg-matrix-kanal_b.md`](novaberg-matrix-kanal_b.md) · [`novaberg-matrix-kanal_e.md`](novaberg-matrix-kanal_e.md) · [`novaberg-matrix-kanal_m.md`](novaberg-matrix-kanal_m.md)
**Entschieden:** 1 · **Offen beim Meister:** 2 (Liste in [`novaberg-matrix-kanal_e.md`](novaberg-matrix-kanal_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-matrix-kanal_k.md §3.3` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-matrix-kanal_t.md`](novaberg-matrix-kanal_t.md), `_b` ist [`novaberg-matrix-kanal_b.md`](novaberg-matrix-kanal_b.md), `_e` ist [`novaberg-matrix-kanal_e.md`](novaberg-matrix-kanal_e.md), `_m` ist [`novaberg-matrix-kanal_m.md`](novaberg-matrix-kanal_m.md).

| § | Datei |
|---|---|
| Titelzeile, Kopfblock, Tabelle | `_k` |
| 1 | `_k` |
| 2 | `_b` (Überschrift und Tabelle der Bauteile); *Im Betrieb belegt* und *Die Messung, die den Kanal rechtfertigt* in `_m` |
| 2a (mit *Vier Dinge, die beim Bauen nicht offensichtlich waren*) | `_t` |
| 2b (mit *Der Befund, den die Gegenprobe fand*) | `_m` |
| 2c (mit *Drei Regeln*) · 2d | `_t` |
| 3 · 3.1 · 3.3 · 3.4 | `_t` |
| 3.2 | `_t`; der Absatz *Die Migration in Zahlen (23.08.2026)* mit Tabelle, Kasten und dem Absatz zur SQLite-Datei in `_b` |
| 4 (mit *Die Dateien des Connectors*, *Wo was liegt*) | `_t` |
| 5 | `_e` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Status, Voraussetzung, Abgrenzung) | `_e` |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## 1. Warum ein dritter Kanal

**Ein Telegram-Bot hat genau einen Absender: sich selbst.** Alles, was in einem Telegram-Chat erscheint, kommt entweder vom Menschen ueber seine eigene App oder vom Bot. Es gibt keinen Weg, im Namen eines Menschen zu senden — nicht als Berechtigung, die man erteilen koennte, sondern als Eigenschaft des Protokolls.

**Das wird zum Problem, sobald ein zweiter Client mitspielt.** Novaberg traegt drei Kanaele. Wer am Desktop schreibt, dessen Aeusserung geht ueber `POST /chat` in den Server, und der Prompt-Consumer verteilt sie als `user_message` an alle **anderen** Clients desselben Menschen. Genau dafuer ist der Typ da — nur kann der Telegram-Bot sie nicht als fremde Aeusserung zustellen, sondern nur selbst sagen. In `telegram_bot/bot.py` steht deshalb `f"[Du] {user_text}"`.

**Matrix hat den zweiten Absender.** Ein Application Service darf innerhalb seines Namensraums im Namen jedes Nutzers senden. Die Desktop-Aeusserung wird damit ein Event mit `sender: @meister` — nicht ein Zitat, sondern die Aeusserung selbst.

> **Der Unterschied ist keine Darstellung, sondern eine Struktur.** Das Praefix `[Du]` ist Text; wer den Verlauf spaeter ausliest, sieht eine Nachricht der Figur. Ein `sender`-Feld liest jeder Client, jedes Werkzeug und jede spaetere Auswertung.

---
