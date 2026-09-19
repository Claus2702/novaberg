# Novaberg — Der Matrix-Kanal: ein Kanal mit zwei Absendern (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-matrix-kanal_k.md`](novaberg-matrix-kanal_k.md) · Ausarbeitung: [`novaberg-matrix-kanal_t.md`](novaberg-matrix-kanal_t.md) · Bauplan und Umstellung: [`novaberg-matrix-kanal_b.md`](novaberg-matrix-kanal_b.md) · Diskussion und Ergänzungen: [`novaberg-matrix-kanal_e.md`](novaberg-matrix-kanal_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Aus §2 — Die Bauteile

Die Tabelle der Bauteile steht in [`novaberg-matrix-kanal_b.md`](novaberg-matrix-kanal_b.md) §2. Hier stehen die Belege aus dem Betrieb.

**Im Betrieb belegt, 23.08.2026 00:50 UTC:**

```
Puppeting geprueft: @meister:novaberg.de
Raum angelegt:      !<raum>:novaberg.de (Nova & meister)
@meister ist beigetreten
WebSocket verbunden (ws://server:8000/ws/meister?client_id=matrix)
PUT /_matrix/app/v1/transactions/{1..4} -> 200 OK
[meister] Eingehend: <Frage>  ->  POST /chat angenommen
```

Der Weg ist damit in **beide** Richtungen gemessen: Eine Nachricht, die ein
angemeldeter Client als `@meister` sendet, erreicht `POST /chat`; der
Homeserver liefert sie per Push, und der Connector quittiert.

### Die Messung, die den Kanal rechtfertigt

**Der Raumverlauf, ausgelesen als angemeldeter Client (23.08.2026, 00:53 UTC):**

| Absender | Text | Woher |
|---|---|---|
| `@meister:novaberg.de` | *Was ist ueber 40-Hz-Gamma-Oszillationen …* | echter Client-Login, wie vom Handy |
| `@nova:novaberg.de` | *Diese Oszillationen wirken als globaler Taktgeber …* | Novas Antwort |
| `@meister:novaberg.de` | *Welche Rolle spielt die Gravitationslinsenwirkung …* | **`POST /chat` mit `client_id=desktop`** |

**Die dritte Zeile ist der ganze Punkt.** Sie hat kein Geraet in diesem Raum je gesendet — sie kam ueber den Desktop-Weg, lief als `user_message` durch den WebSocket und wurde vom Application Service im Namen des Menschen eingestellt. Im Telegram-Kanal stuende dort `[Du] Welche Rolle spielt …`, gesendet von Novas Konto.

**Gezaehlt:** drei Nachrichten, zwei Absender, **kein Praefix**.

**Erreichbarkeit aus dem lokalen Netz belegt:** `/_matrix/client/versions` antwortet ueber die LAN-Adresse des Wirts mit 200, und `/login` bietet `m.login.password` sowie `m.login.application_service` an.

---

## 2b. Die Zeugen — und warum die erste Fassung wertlos war

**26 Zeugen, in einem eigenen Lauf:**

```
docker compose exec matrix-bot python -m unittest discover -p "test_*.py"
Ran 26 tests — OK
```

**Sie laufen nicht in der Server-Suite**, und das ist die Lage und keine Nachlaessigkeit: Der Connector ist ein eigener Dienst mit eigenem Behaelter und eigenem Abhaengigkeitssatz. `unittest discover` im Server sieht ihn nicht. **Das steht auch so in der Featureliste** — der Prototyp ist gemessen und bezeugt, aber nicht von derselben Suite.

### Der Befund, den die Gegenprobe fand

**Die erste Fassung der Zeugen prüfte nichts.** Die Absenderwahl stand inline in der Empfangsschleife des WebSockets; ein Zeuge kam an sie nur heran, indem er den ganzen Socket fuhr. Stattdessen rief er den **Sendeweg** direkt auf — und behauptete damit, was er prüfen sollte.

> **Gemessen:** Die Gegenprobe baute den Telegram-Zustand zurück — `user_message` wieder als Figur, mit `[Du]`-Präfix — und **kein einziger Test wurde rot.** Sechzehn grüne Zeugen über einem Kanal, dessen einziger Zweck entfallen war.

**Die Abhilfe war nicht ein besserer Test, sondern eine eigene Funktion.** `absender_fuer(typ, mensch)` trifft die Entscheidung an einer Stelle, die ein Zeuge adressieren kann. Danach färbt derselbe Eingriff **2** Tests rot — `test_eine_fremde_aeusserung_kommt_vom_menschen` und `test_die_beiden_sorten_sind_verschieden`.

> **Eine Entscheidung, die inline in einer Schleife steht, ist nicht bezeugbar — nur umständlich erreichbar.** Und was umständlich zu erreichen ist, wird stattdessen behauptet.

---
