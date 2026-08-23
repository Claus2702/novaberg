# Novaberg — Der Matrix-Kanal: ein Kanal mit zwei Absendern

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Matrix als dritter Kanal, mit Application Service statt Bot
**Stand:** 23. August 2026 (v0.7 — die Figur traegt Namen und Bild, ohne sie bei jedem Start neu abzulegen)
**Pfad:** novaberg/docs/novaberg-matrix-kanal_k.md
**Typ:** Konzept (`_k`)
**Status:** 🟢 **in Betrieb** — sieben von acht Arbeitspaketen; TLS (4) ist zurueckgestellt, siehe §5
**Voraussetzung:** `novaberg-tool-multi-channel.md` (die Kanalarchitektur) · der Epic in `novaberg-backlog.md`
**Abgrenzung:** Der Telegram-Bot bleibt unangetastet und laeuft parallel

---

## 1. Warum ein dritter Kanal

**Ein Telegram-Bot hat genau einen Absender: sich selbst.** Alles, was in einem Telegram-Chat erscheint, kommt entweder vom Menschen ueber seine eigene App oder vom Bot. Es gibt keinen Weg, im Namen eines Menschen zu senden — nicht als Berechtigung, die man erteilen koennte, sondern als Eigenschaft des Protokolls.

**Das wird zum Problem, sobald ein zweiter Client mitspielt.** Novaberg traegt drei Kanaele. Wer am Desktop schreibt, dessen Aeusserung geht ueber `POST /chat` in den Server, und der Prompt-Consumer verteilt sie als `user_message` an alle **anderen** Clients desselben Menschen. Genau dafuer ist der Typ da — nur kann der Telegram-Bot sie nicht als fremde Aeusserung zustellen, sondern nur selbst sagen. In `telegram_bot/bot.py` steht deshalb `f"[Du] {user_text}"`.

**Matrix hat den zweiten Absender.** Ein Application Service darf innerhalb seines Namensraums im Namen jedes Nutzers senden. Die Desktop-Aeusserung wird damit ein Event mit `sender: @meister` — nicht ein Zitat, sondern die Aeusserung selbst.

> **Der Unterschied ist keine Darstellung, sondern eine Struktur.** Das Praefix `[Du]` ist Text; wer den Verlauf spaeter ausliest, sieht eine Nachricht der Figur. Ein `sender`-Feld liest jeder Client, jedes Werkzeug und jede spaetere Auswertung.

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

## 2a. Der Aufbau des Connectors

**Drei nebenlaeufige Aufgaben** (`matrix_bot/bot.py`):

| Teil | Was er tut |
|---|---|
| HTTP-Dienst | nimmt `PUT /_matrix/app/v1/transactions/{txnId}` entgegen — der Connector wird **beliefert**, er fragt nicht |
| WebSocket-Zuhoerer | je Mensch einer, wie beim Telegram-Bot |
| Raumaufbau | beim Start: Raum finden oder anlegen, beide Kennungen hinein |

**Die Unterscheidung, die den Kanal ausmacht**, steht im WebSocket-Zuhoerer:

| Novaberg-Typ | Absender im Raum |
|---|---|
| `character_response` | die Figur |
| `shadow_delivery` | die Figur |
| `user_message` | **der Mensch** — hier stand im Telegram-Kanal `[Du] ...` |

### Vier Dinge, die beim Bauen nicht offensichtlich waren

**Der Homeserver wiederholt jede Transaktion, die nicht mit 200 beantwortet
wird.** Ein Ereignis, das der Connector nicht braucht, ist deshalb kein
Fehlschlag der Lieferung — wer es mit einem Fehler quittiert, bekommt es fuer
immer wieder. Ein einzelnes fehlerhaftes Ereignis wird protokolliert und
uebersprungen, der Stapel gilt trotzdem als zugestellt.

**Was der Connector selbst sendet, kommt als Transaktion zurueck.** Ohne
Gegenmassnahme liefe der Kanal im Kreis: Eine als `@meister` eingespeiste
Desktop-Aeusserung ginge erneut an `POST /chat`. Die Event-Kennungen der
eigenen Sendungen werden deshalb gemerkt und beim Ruecklauf uebergangen.

**Der Beitritt wird ausdruecklich ausgefuehrt.** Eine Einladung ist kein
Mitglied, und in einen Raum, den niemand betreten hat, kann auch niemand
sprechen. Der AS tritt fuer den Menschen bei — er darf es.

**Der Raumstand ueberlebt den Neustart.** `matrix/state/raeume.json` ist
gemountet; ohne ihn legte jeder Start einen neuen Raum an und liesse den
Verlauf des alten liegen, ohne dass etwas anschluege. Eine **unlesbare**
Standdatei fuehrt deshalb zum Abbruch und nicht zu einem leeren Stand.

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

## 2c. Formatierung — warum `body` allein nicht genuegt

**Der Server liefert Markdown, jeder Kanal wandelt fuer sein Medium.** Matrix hat dafuer ein eigenes Feld: `formatted_body` mit `format: org.matrix.custom.html`. Fehlt es, zeigt der Client den rohen Text — aus `**wichtig**` werden vier Sternchen, aus einer Aufzaehlung eine Reihe Bindestriche.

**`body` bleibt trotzdem der Markdown-Text**, und das ist keine Verlegenheit, sondern die Vorschrift: `body` ist die Rueckfallform fuer Clients ohne HTML und soll lesbar sein. Genau dafuer ist Markdown gebaut.

**Der Wandler erzeugt absichtlich wenig.** Die Spezifikation laesst nur eine begrenzte Menge an Auszeichnungen zu, und ein Client darf alles Uebrige entfernen; was hier entstuende und dort verschwaende, waere Uebertragung ohne Wirkung.

### Drei Regeln, die sich beim Bauen als notwendig zeigten

**Maskiert wird zuerst, ausgezeichnet danach.** Andersherum wuerde ein `<` im Antworttext als Element gelesen — bei einem Modell, das ueber Code und Mathematik spricht, ist das kein Randfall, sondern der Normalfall.

**Der Code-Block wird vor dem Fettdruck gewandelt.** Sonst wird aus `a ** b` innerhalb eines Blocks ein `<strong>`, und der Code stimmt nicht mehr.

**`formatted_body` kommt nur hinzu, wo etwas ausgezeichnet wurde.** Ein zweites Feld, das nur den maskierten Text wiederholt, kostet Uebertragung und traegt nichts.

---

## 2d. Das Profil der Figur

**Ohne Anzeigename zeigt ein Client den lokalen Teil der Kennung** — also die Kleinschreibung des Kontonamens. Der Connector setzt beim Start Namen und Bild, damit ein Neuaufbau des Homeservers sie nicht kostet.

**Hochgeladen wird nur, was sich geaendert hat**, und das ist die eigentliche Zusicherung dieses Abschnitts:

> **Der Medienspeicher vergibt je Aufruf eine neue Adresse.** Derselbe Inhalt zweimal hochgeladen ergibt zwei Objekte. Ein Connector, der bei jedem Start ablegt, fuellt den Speicher mit Kopien desselben Bildes — und **keine davon faellt auf**, denn jede einzelne ist gueltig und das Profil sieht richtig aus.

Der Fingerabdruck der Datei (SHA-256) liegt neben dem Raumstand im Zustandsverzeichnis. Stimmt er und traegt das Profil bereits ein Bild, geschieht nichts; aendert sich die Datei, wird neu abgelegt.

**Im Auslesefall belegt (23.08.2026):** Medienobjekte vor einem Neustart **5**, danach **5**. Beim ersten Lauf mit Bild stieg die Zahl von 4 auf 5.

**Ein fehlendes Bild haelt den Start nicht auf.** Ein Profil ohne Bild ist ein Schoenheitsfehler; ein Connector, der deswegen nicht startet, kostet den Kanal.

> **Gefunden hat den Mount-Fehler der Betrieb, nicht die Zeugen.** Beim ersten Lauf lag das Bild nicht im Behaelter — `matrix/config` war nur bei Synapse eingehaengt. Die sechs Zeugen der Profilpflege konnten das nicht finden: Sie setzen den Pfad selbst, damit sie ohne Datei auskommen. **Ein Zeuge, der seine Eingabe herstellt, prueft nie, ob sie im Betrieb vorliegt.**

---

## 3. Entscheidungen, und warum sie so fielen

### 3.1 `server_name: novaberg.de` — nicht die IP

**Der Servername steckt in jeder Nutzer- und Raum-ID und ist nachtraeglich nicht aenderbar.** Ein Wechsel bedeutet neue Accounts, neue Raeume, neuen Verlauf. Die LAN-Adresse des Wirts stammt aus DHCP (`dynamic` am Interface) — sie als Namen zu nehmen hiesse, die Identitaet des Servers an einen Lease zu binden.

**Erreichbarkeit und Name fallen deshalb auseinander**, und das ist kein Mangel: Beim Anmelden nennt der Client die **Adresse** des Wirts im lokalen Netz samt Port, die Kennung lautet trotzdem `@meister:novaberg.de`. Matrix trennt beides ausdruecklich.

> **Der Fall ist am 23.08.2026 eingetreten.** Die Adresse des Wirts wechselte ueber Nacht von `.31` auf `.19` — durch DHCP, ohne Zutun. Die Kennung `@meister:novaberg.de` hat das ueberstanden; eine Kennung mit IP haette jeden Account und jeden Raum ungueltig gemacht. Der Wirt hat seither eine feste Adresse, und die Trennung bleibt trotzdem richtig: Sie hat den einen Tag getragen, an dem sie gebraucht wurde.

**Foederiert wird nichts.** `federation_domain_whitelist: []` ist die geschlossene Seite — sie erlaubt nichts, statt alles ausser einer Aufzaehlung zu erlauben. Solange unter der Domain kein `.well-known` liegt, findet ohnehin kein fremder Server hierher.

### 3.2 ~~SQLite statt Postgres~~ → Postgres, seit dem 23.08.2026

**Der Erstaufbau nahm SQLite**, und die Begruendung war die kleinere Beruehrung: Eine zweite Datenbank im laufenden Postgres anzulegen ist ein Eingriff in ein produktives System, und ein Paar in einem privaten Netz traegt SQLite ohne weiteres.

**Entschieden wurde dann anders, und die Begruendung ist eine andere Groesse:** weniger verschiedene Systeme. Ein Stapel mit einer Datenbank ist einfacher zu sichern, zu ueberwachen und zu verstehen als einer mit zweien — und dieser Gewinn faellt jeden Tag an, waehrend die Beruehrung einmalig war.

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

### 3.3 `exclusive: false` im Namensraum

**Das ist die tragende Entscheidung der AS-Registrierung.** Der AS muss `@meister` puppeten duerfen, sonst erscheint eine Desktop-Aeusserung wieder als Nachricht der Figur. Zugleich muss sich der Mensch mit genau diesem Account vom Handy anmelden koennen.

**`exclusive: true` verbietet das zweite:** Ein exklusiver Namensraum gehoert dem AS allein; niemand sonst darf sich darin anmelden oder registrieren. Der Preis der offenen Variante ist benannt — sie haelt niemanden davon ab, Namen darin zu vergeben. Bei einem Homeserver ohne offene Registrierung und mit einem Menschen ist das folgenlos.

> **Daraus folgt, was der Mensch merkt:** Er meldet sich mit einem Account an, den auch Novaberg benutzt. Die Alternative waeren zwei Identitaeten im Raum — sein eigener Account und ein Schatten fuer die Desktop-Echos —, und dann stuenden dort zwei „du".

### 3.4 Push statt Polling

Der Homeserver **schiebt** Ereignisse an den AS (`PUT /_matrix/app/v1/transactions/{txnId}`). Der Connector ist deshalb ein Server und kein Poller — anders als der Telegram-Bot, der Long Polling faehrt. Die Gegenrichtung laeuft ueber die gewoehnliche Client-Server-API mit `as_token` als Bearer und `?user_id=` fuer den Absender.

---

## 4. Wo was liegt

| Ort | Inhalt | Versioniert |
|---|---|---|
| `matrix/data/` | Synapse-Daten, `homeserver.yaml`, Signaturschluessel, SQLite | nein — Betriebsdaten |
| `matrix/config/novaberg-as.yaml` | AS-Registrierung samt zweier Tokens | nein — Geheimnisse |
| `matrix/config/` (weitere) | dieselben Tokens fuer den Connector, dazu die Anmeldedaten | nein — Geheimnisse |
| `novaberg/matrix_bot/` | der Connector | **ja** — Code |

**Die Trennung folgt derselben Regel wie beim Wissensspeicher** (`F-WISSEN-1`): Was Geheimnisse oder Gespraechsinhalte traegt, liegt neben dem Repositorium, nicht darin.

**`matrix/config` ist getrennt von `matrix/data`, weil die Rechte es verlangen:** Das Datenverzeichnis gehoert dem Server-Nutzer (UID 991), und eine Datei, die der Mensch pflegen soll, kann dort nicht liegen.

---

## 5. Was offen ist

~~**TLS.** … Ob FluffyChat eine `http://`-Adresse annimmt, ist **ungeprueft**.~~

→ **Am 23.08.2026 am Geraet beantwortet: FluffyChat nimmt `http://` an.** Die Verbindung steht, und in der Ereignistabelle liegen Turns, die aus der App kamen. **Damit ist Arbeitspaket 4 nicht erledigt, sondern zurueckgestellt** — der Unterschied ist wichtig: Unverschluesselt geht ueber das lokale Netz und den VPN-Tunnel ein Passwort und jeder Nachrichtentext im Klartext. Innerhalb von WireGuard ist die Strecke bereits verschluesselt; ohne ihn, im heimischen WLAN, ist sie es nicht.

**Die Recherche hat diese Frage nicht beantwortet, das Geraet schon.** Zwei Suchlaeufe fanden keine belastbare Aussage zum Schema-Zwang von FluffyChat — eine halbe Stunde Suche gegen eine Minute Ausprobieren.

**Push zum Handy.** Der Homeserver ist nur erreichbar, solange WireGuard steht. Was ohne dauerhaften Tunnel mit einem Impuls von Nova geschieht, steht als offener Punkt im Epic.

**Verschluesselung.** Der Raum wird zunaechst **unverschluesselt** angelegt. Ein AS kann in einem E2EE-Raum nicht ohne weiteres senden — er braucht Geraeteschluessel und eine Verifikation, und das ist ein eigenes Bauteil. Im privaten Netz auf eigener Maschine ist der Gewinn gering, der Aufwand hoch.
