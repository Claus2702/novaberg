# KI-Assistent — Desktop-Client

PySide6-basierter Desktop-Client fuer den lokalen KI-Assistenten.
Kommuniziert mit dem FastAPI-Server ueber REST, SSE und WebSocket.


## Architektur

```
client/
  main.py                  Einstiegspunkt (QApplication, Font-Setup)
  ui/
    __init__.py             Modul-Paket
    icons.py                Zentrales Icon-Mapping (qtawesome)
    hauptfenster.py         Hauptfenster mit Sidebar-Navigation
    chat_panel.py           Chat mit SSE-Stream und WebSocket-Impulsen
    status_bar.py           Permanente Statusleiste (Health-Polling)
    fakten_panel.py         Entitaeten und Relationen (Knowledge Graph)
    gedaechtnis_panel.py    KZG, LZG, Charakter-Hash, Session-Kontext
    system_panel.py         Health-Check-Uebersicht aller Dienste
    schatten_panel.py       Platzhalter: Schatten-Agent-Aktivitaeten
    timeline_panel.py       Platzhalter: Terminuebersicht
```


## Aufbau des Hauptfensters

```
+--------------------------+----------------------------------------------+
|                          |                                              |
|   Sidebar (220px)        |   StackedWidget (aktives Panel)              |
|                          |                                              |
|   KI-Assistent           |   Chat / Gedaechtnis / Timeline              |
|   ──────────────         |   Fakten / Schatten / System                 |
|   (chat)    Chat         |                                              |
|   (brain)   Gedaechtnis  |                                              |
|   (timeline)Timeline     |                                              |
|   (book)    Fakten       |                                              |
|   (ghost)   Schatten     |                                              |
|   (cog)     System       |                                              |
|                          |                                              |
|   v0.1.0                 +----------------------------------------------+
|                          |   StatusLeiste (Server, Ollama, DB, Pixie)   |
+--------------------------+----------------------------------------------+
```


## Module im Detail

### main.py — Einstiegspunkt

Erstellt die `QApplication`, setzt die Schriftart (Noto Sans)
und oeffnet das `Hauptfenster`.

### hauptfenster.py — Hauptfenster

`Hauptfenster(QMainWindow)` — Zentrales Fenster mit:
- **Sidebar** (links, 220px): Titel, 6 Navigations-Buttons (checkable), Versionslabel
- **QStackedWidget** (rechts): Wechselt zwischen den 6 Panels
- **StatusLeiste** (unten): Permanenter Dienst-Status

Die Sidebar-Buttons steuern ueber `_panel_wechseln(index)` den StackedWidget-Index.

### chat_panel.py — Chat

Drei Klassen:

| Klasse | Aufgabe |
|---|---|
| `ChatStreamWorker(QThread)` | POST `/chat/stream` mit SSE-Parsing. Emittiert `stage_erhalten`, `antwort_erhalten`, `fehler_erhalten`. |
| `WebSocketWorker(QThread)` | Haelt WebSocket-Verbindung zu `/ws/{user_id}`. Empfaengt Shadow-Impulse (typ: `shadow_impuls`). Auto-Reconnect nach 5s. |
| `ChatPanel(QWidget)` | Hauptwidget mit Nachrichtenverlauf (ScrollArea), Pipeline-Stage-Anzeige und Eingabezeile. |

**Nachrichtenfluss:**
1. User tippt Nachricht -> `_nachricht_senden()` startet `ChatStreamWorker`
2. Server sendet SSE-Events: `stage` (Pipeline-Fortschritt) und `answer` (finale Antwort)
3. Stages werden live mit Chevron-Icon angezeigt, abgeschlossene mit Check-Icon
4. Parallel empfaengt der `WebSocketWorker` proaktive Impulse von Nova (Schatten-Agent)

### status_bar.py — Statusleiste

`StatusLeiste(QWidget)` — Liegt am unteren Fensterrand. Pollt alle 5 Sekunden
`GET /health` und aktualisiert vier Labels:
- **Server**: ok/offline
- **Ollama**: ok/offline
- **DB** (Postgres): ok/offline
- **Pixie**: idle oder aktiver Zustand mit Thema

Farbkodierung: gruen = ok, rot = fehler, grau = unbekannt/idle.

### fakten_panel.py — Fakten (Knowledge Graph)

`FaktenPanel(QWidget)` — Laedt Entitaeten ueber `GET /fakten/{user_id}`.
Stellt jede Entitaet als Karte dar:
- **Kopfzeile**: Name + Typ (farbkodiert: Person=blau, Tier=gruen, Objekt=orange, Ort=lila, Organisation=rot)
- **Fakten-Zeilen**: Schluessel = Wert mit Status (gesichert/ungesichert), Relevanz und Haeufigkeit

### gedaechtnis_panel.py — Gedaechtnis

`GedaechtnisPanel(QWidget)` — Vier Tabs:

| Tab | Endpoint | Inhalt |
|---|---|---|
| KZG (Kurzzeit) | `GET /gedaechtnis/kzg/{user_id}` | Aktuelle Themen mit Salienz, Dimension, TTL |
| LZG (Langzeit) | `GET /gedaechtnis/lzg/{user_id}` | Destillierte Eintraege mit Gewicht, Haeufigkeit |
| Charakter-Hash | `GET /gedaechtnis/hash/{user_id}` | Kern-Hash (stabil) + Adaptive-Hash (dynamisch) |
| Session | `GET /session/kontext/{user_id}` | Zusammenfassung + aktuelle Turns |

### system_panel.py — System

`SystemPanel(QWidget)` — Zeigt den Status von Server, Redis, Postgres und Ollama.
Manueller Health-Check ueber Button, initialer Check nach 500ms.
Fragt `GET /health` ab und zeigt pro Dienst ein Status-Icon (check/close/alert).

### schatten_panel.py — Schatten-Agent (Platzhalter)

`SchattenPanel(QWidget)` — Noch nicht implementiert.
Geplant: Live-Ansicht der Pixie-Aktivitaeten, Queue-Status, Stack-Eintraege.

### timeline_panel.py — Timeline (Platzhalter)

`TimelinePanel(QWidget)` — Noch nicht implementiert.
Geplant: Kalender-Integration, Termine, Erinnerungen.


## Icon-System (ui/icons.py)

Alle grafischen Symbole im Client werden zentral ueber `qtawesome` bereitgestellt.
Statt ASCII-Tokens (`[OK]`, `[X]`, `[>>]`) werden Material Design Icons (mdi6) verwendet.

**Aufbau:**
- `_MAP` — Dict mit Token → (qtawesome-Name, Standardfarbe)
- `IC` — Lazy-Cache, liefert `QIcon` per `IC["token"]` oder `QPixmap` per `IC.pixmap("token")`
- `icon_label()` — Erzeugt ein Kompakt-Widget (Icon + Text) fuer Status-Anzeigen

**Token-Kategorien:**

| Kategorie | Beispiel-Tokens |
|---|---|
| Navigation | `nav.chat`, `nav.gedaechtnis`, `nav.timeline`, `nav.fakten`, `nav.schatten`, `nav.system` |
| Status | `ok`, `fehler`, `warnung`, `offline`, `pruefe`, `idle` |
| Aktionen | `refresh`, `senden`, `health` |
| Pipeline | `stage.aktiv`, `stage.fertig` |
| Dienste | `dienst.server`, `dienst.ollama`, `dienst.redis`, `dienst.postgres`, `dienst.pixie` |
| Fakten | `fakt.gesichert`, `fakt.ungesichert` |


## Server-Kommunikation

| Protokoll | Endpoint | Verwendet in |
|---|---|---|
| SSE (POST) | `/chat/stream` | ChatStreamWorker |
| WebSocket | `/ws/{user_id}` | WebSocketWorker |
| REST (GET) | `/health` | StatusLeiste, SystemPanel |
| REST (GET) | `/fakten/{user_id}` | FaktenPanel |
| REST (GET) | `/gedaechtnis/kzg/{user_id}` | GedaechtnisPanel |
| REST (GET) | `/gedaechtnis/lzg/{user_id}` | GedaechtnisPanel |
| REST (GET) | `/gedaechtnis/hash/{user_id}` | GedaechtnisPanel |
| REST (GET) | `/session/kontext/{user_id}` | GedaechtnisPanel |


## Abhaengigkeiten

- **PySide6** — UI-Framework
- **qtawesome** — Icon-Font-Bibliothek (Material Design Icons, Font Awesome u.a.)
- **requests** — HTTP-Kommunikation (REST, SSE)
- **websocket-client** — WebSocket-Verbindung fuer Shadow-Impulse


## Starten

```bash
cd client
python main.py
```

Voraussetzung: Der FastAPI-Server laeuft auf `http://localhost:8000`.


## Design

- Dark Theme (`#121212` Hintergrund, `#1a1a1a` Sidebar)
- Akzentfarbe: `#4da6ff` (Blau)
- Erfolg: `#4caf50` (Gruen) | Fehler: `#ff6b6b` (Rot) | Warnung: `#ffa726` (Orange)
- Schrift: Noto Sans, 11pt Basis
- Icons: Material Design Icons 6 via qtawesome
- Alle Texte und Bezeichner auf Deutsch
