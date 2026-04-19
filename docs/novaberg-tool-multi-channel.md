# Novaberg — Tool: Multi-Channel-Architektur

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Multi-Channel-Architektur (Telegram Bot, Formatierung)
**Stand:** 19. April 2026, Chat 56
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
| Web-Interface | — | Geplant |

---

## 3. Telegram-Bot

**Dateien:** `telegram_bot/bot.py`, `telegram_bot/config.py`

**Architektur:** Dünner Client. Leitet Nachrichten an `POST /chat` weiter und gibt die Antwort zurück. Kein eigener State, keine Business-Logik.

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

**Prinzip aus Chat 30:** "Daten vollständig transportieren, Formatierung am Konsumenten." Der Server liefert immer Markdown. Jeder Client konvertiert für sein Medium.

---

*Basiert auf Chat 41 (Telegram Bot) und Chat 43 (Konzept-Referenz). Das ursprünglich geplante Konzeptdokument nova-13-k.md wurde als eigenständige Datei nie erstellt — die Inhalte sind in der Roadmap und den Chat-Protokollen dokumentiert.*
