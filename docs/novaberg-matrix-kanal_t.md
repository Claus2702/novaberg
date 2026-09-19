# Novaberg — Der Matrix-Kanal: ein Kanal mit zwei Absendern (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-matrix-kanal_k.md`](novaberg-matrix-kanal_k.md) · Bauplan und Umstellung: [`novaberg-matrix-kanal_b.md`](novaberg-matrix-kanal_b.md) · Diskussion und Ergänzungen: [`novaberg-matrix-kanal_e.md`](novaberg-matrix-kanal_e.md) · Messungen: [`novaberg-matrix-kanal_m.md`](novaberg-matrix-kanal_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

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

> **Hinweis zur Aufteilung (19.09.2026):** §2b *Die Zeugen — und warum die erste Fassung wertlos war* steht in [`novaberg-matrix-kanal_m.md`](novaberg-matrix-kanal_m.md).

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

> **Hinweis zur Aufteilung (19.09.2026):** Der Absatz *„Die Migration in Zahlen (23.08.2026)“* mit seiner Tabelle, dem Kasten zu `LC_COLLATE=C` und dem Absatz zur SQLite-Datei stand hier; er steht in [`novaberg-matrix-kanal_b.md`](novaberg-matrix-kanal_b.md), *Aus §3.2*.

### 3.3 `exclusive: false` im Namensraum

**Das ist die tragende Entscheidung der AS-Registrierung.** Der AS muss `@meister` puppeten duerfen, sonst erscheint eine Desktop-Aeusserung wieder als Nachricht der Figur. Zugleich muss sich der Mensch mit genau diesem Account vom Handy anmelden koennen.

**`exclusive: true` verbietet das zweite:** Ein exklusiver Namensraum gehoert dem AS allein; niemand sonst darf sich darin anmelden oder registrieren. Der Preis der offenen Variante ist benannt — sie haelt niemanden davon ab, Namen darin zu vergeben. Bei einem Homeserver ohne offene Registrierung und mit einem Menschen ist das folgenlos.

> **Daraus folgt, was der Mensch merkt:** Er meldet sich mit einem Account an, den auch Novaberg benutzt. Die Alternative waeren zwei Identitaeten im Raum — sein eigener Account und ein Schatten fuer die Desktop-Echos —, und dann stuenden dort zwei „du".

### 3.4 Push statt Polling

Der Homeserver **schiebt** Ereignisse an den AS (`PUT /_matrix/app/v1/transactions/{txnId}`). Der Connector ist deshalb ein Server und kein Poller — anders als der Telegram-Bot, der Long Polling faehrt. Die Gegenrichtung laeuft ueber die gewoehnliche Client-Server-API mit `as_token` als Bearer und `?user_id=` fuer den Absender.

---

## 4. Wo was liegt

### Die Dateien des Connectors

| Datei | Was darin steht |
|---|---|
| `matrix_bot/bot.py` | die drei Aufgaben: Push-Empfang, WebSocket-Zuhoerer, Raumaufbau — dazu `absender_fuer` und `_profil_pflegen` |
| `matrix_bot/matrix_api.py` | die Client-Server-API, so weit sie gebraucht wird; **hier steht `?user_id=`**, der ganze Unterschied zu einem Bot |
| `matrix_bot/formatierung.py` | Markdown → Matrix-HTML (§2c) |
| `matrix_bot/config.py` | alles aus der Umgebung, kein Geheimnis fest verdrahtet |
| `matrix_bot/test_connector.py` | 26 Zeugen, eigener Lauf (§2b) |

### Wo was liegt

| Ort | Inhalt | Versioniert |
|---|---|---|
| `matrix/data/` | Synapse-Daten, `homeserver.yaml`, Signaturschluessel, SQLite | nein — Betriebsdaten |
| `matrix/config/novaberg-as.yaml` | AS-Registrierung samt zweier Tokens | nein — Geheimnisse |
| `matrix/config/` (weitere) | dieselben Tokens fuer den Connector, dazu die Anmeldedaten | nein — Geheimnisse |
| `novaberg/matrix_bot/` | der Connector | **ja** — Code |
| `novaberg/matrix/` | **die Muster** zu den drei Dateien oben, Geheimnisse leer | **ja** — Struktur |

> **Die Trennung verlaeuft seit dem 24.08.2026 zwischen Geheimnis und Struktur, nicht
> zwischen Betrieb und Repositorium.** Der Satz darunter — *was Geheimnisse traegt, liegt
> neben dem Repositorium* — blieb richtig und war trotzdem zu grob gelesen: Er hielt
> **auch die Struktur** draussen. `exclusive: false` in beiden Namensraeumen, die
> `url` auf den Connector-Port, `LC_COLLATE=C` in der Datenbank und
> `app_service_config_files` sind keine Geheimnisse, sondern die tragenden
> Entscheidungen dieses Kanals — und sie standen nur in Dateien, die niemand ausser
> dem Betreiber je sieht.
>
> **Gemessen am selben Tag:** `README.md` und `README.de.md` hatten **0 Treffer** auf
> `matrix` und `synapse`. Der Kanal war gebaut, im Betrieb, konzeptionell vollstaendig
> beschrieben — und aus dem Repositorium **nicht herstellbar**.
>
> Seither liegen unter `novaberg/matrix/` drei Muster mit leeren Geheimnissen. Sie sind
> gegen die Betriebsdateien gehalten: **16 von 16 Schluesseln** in der `homeserver.yaml`,
> **6 von 6** in der AS-Registrierung, keine Abweichung ausser den geleerten Werten.
> Die Anleitung steht in beiden READMEs, Schritt 6.

**Die Trennung folgt derselben Regel wie beim Wissensspeicher** (`F-WISSEN-1`): Was Geheimnisse oder Gespraechsinhalte traegt, liegt neben dem Repositorium, nicht darin.

**`matrix/config` ist getrennt von `matrix/data`, weil die Rechte es verlangen:** Das Datenverzeichnis gehoert dem Server-Nutzer (UID 991), und eine Datei, die der Mensch pflegen soll, kann dort nicht liegen.

---
