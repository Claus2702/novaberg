# Novaberg — Tool: Multi-Channel-Architektur

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Multi-Channel-Architektur (Telegram Bot, Formatierung)
**Stand:** 23. August 2026 (**dritter Kanal: Matrix**, als Prototyp — der erste mit zwei Absendern; §2, §4. Davor: 21. April 2026, Chat 60 — chat.py fire-and-forget, Event-Modell)
**Pfad:** novaberg/docs/novaberg-tool-multi-channel.md
**Quellen:** Chat 41 (Telegram Bot), Chat 43 (Konzept-Referenz)

---

## 1. Konzept

Novaberg ist nicht an einen einzelnen Client gebunden. Der Server (FastAPI) ist kanal-agnostisch — er weiß nicht, ob die Nachricht vom Desktop-Client, vom Telegram-Bot oder einem zukünftigen Web-Interface kommt.

**Prinzip:** Markdown als kanonisches Format, Formatierung am Konsumenten.

---

## 2. Kanäle

| Kanal | Technologie | Status |
|-------|------------|--------|
| Desktop-Client | GTK4 (PyGObject) + WebKitGTK, SSE + WebSocket | Produktiv |
| Telegram-Bot | python-telegram-bot v20+, Long Polling | Produktiv (Chat 41) |
| **Matrix** | Synapse + Application Service, Push statt Polling | **Prototyp (23.08.2026)** |
| Web-Interface | — | Geplant |

> **Der Matrix-Kanal ist der erste mit zwei Absendern.** Desktop und Telegram haben je einen: Was dort erscheint, kommt vom Menschen selbst oder vom Dienst. Ein Application Service darf im Namen jedes Nutzers seines Namensraums senden — deshalb erscheint dort eine Aeusserung, die an einem **anderen** Client gemacht wurde, als Nachricht des Menschen und nicht als `[Du] …` aus Novas Mund. Konzept: `novaberg-matrix-kanal_k.md`.
>
> **Fuer das Leitprinzip aendert das nichts.** Der Kanal bleibt dumm: Er reicht `POST /chat` weiter und stellt zu, was der WebSocket liefert. Was hinzukommt, ist eine Angabe — **wer** spricht —, und die stand vorher nur deshalb nicht im Protokoll, weil Telegram sie nicht tragen kann.

---

## 3. Telegram-Bot

**Dateien:** `telegram_bot/bot.py`, `telegram_bot/config.py`

**Architektur:** Dünner Client. Leitet Nachrichten an `POST /chat` weiter und gibt die Antwort zurück. Kein eigener State, keine Business-Logik.

Seit Chat 60: chat.py führt nur Pfad 1 (HumanGraph) aus — Wahrnehmung und Speicherung. Die Charakter-Antwort wird asynchron per WebSocket geliefert (Event-Consumer → CharacterGraph → WebSocket). Der SSE-Stream zeigt Pfad-1-Stages, kein "answer"-Event mehr.

**Whitelist:** `TELEGRAM_USER_MAP` in `.env` (Format: `telegram_id:user_id`). Unbekannte Telegram-IDs werden ignoriert.

**Telegram-Limits:**
- 4096 Zeichen pro Nachricht — bei längeren Antworten wird an Absatz-Grenzen gesplittet
- Typing-Indicator während der Verarbeitung
- `concurrent_updates=False` — sequentielle Verarbeitung

**Docker:** Eigener Service im Compose-Stack, `depends_on: server`, kein Port-Mapping nach außen.

---

## 4. Formatierung

| Kanal | Format | Konvertierung |
|-------|--------|--------------|
| Server-Antwort | Markdown (kanonisch) | — |
| Desktop-Client | HTML (WebKitGTK WebView) | Markdown → HTML am Client |
| Telegram | Plain Text | Markdown → Text (Telegram unterstützt teilweise Markdown) |
| Matrix | `m.text` mit `body` | derzeit keine — der Client zeigt den Markdown-Text roh |

> **Der Matrix-Kanal sendet vorerst nur `body`.** Die Spezifikation kennt daneben `formatted_body` mit `org.matrix.custom.html`; ohne dieses Feld zeigt ein Client die Markdown-Zeichen woertlich. Das ist beim Prototyp bewusst offen gelassen — erst tragen, dann formatieren.

**Prinzip aus Chat 30:** "Daten vollständig transportieren, Formatierung am Konsumenten." Der Server liefert immer Markdown. Jeder Client konvertiert für sein Medium.

---

*Basiert auf Chat 41 (Telegram Bot) und Chat 43 (Konzept-Referenz). Das ursprünglich geplante Konzeptdokument nova-13-k.md wurde als eigenständige Datei nie erstellt — die Inhalte sind in der Roadmap und den Chat-Protokollen dokumentiert.*
