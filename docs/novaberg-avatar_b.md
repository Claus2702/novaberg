# Novaberg — Emotions-Avatar: Bauplan und Umstellung

**Teil von:** `novaberg-avatar_k.md` — dort Absicht, Kopfblock und die Tabelle „§ → Datei“
**Stand:** 05.10.2026, 14:01 UTC (§18: L0″, der Blickhalt in der Referenz). Davor 05.10.2026, 06:33 UTC (§16: W im Client vom Eigentümer abgenommen). Davor 05.10.2026, 06:15 UTC (§16: W — die Mimik nach der Literatur im Client gebaut und gegen den Prototyp gemessen). Davor 05.10.2026, 05:50 UTC (§18: L1′/L2′ im Betrieb vom Eigentümer abgenommen, die Bildzeit der Drehung hingenommen). Davor 05.10.2026, 00:27 UTC (§18: L1′, L2′a, L2′b und L2′c gebaut — der Client folgt der nachgestellten Referenz; die Bildzeit der Kopfdrehung gemessen, ihr Ziel verfehlt; die Messung im Betrieb steht aus). Davor 04.10.2026, 22:00 UTC (§18: die Sichtprüfung der Referenz L0′a–L0′c). Davor 04.10.2026, 21:49 UTC (§18: die Gegenproben zu L0′c gelaufen). Davor 04.10.2026, 21:05 UTC (§18.1: die Abnahme in der Fassung der nachgestellten Referenz — Nachdenken, Antwort, Lidschläge, Kopf, Pupille, Fall *langes Nachdenken*). Davor 04.10.2026, 20:31 UTC (§18: L0′c gebaut). Davor 04.10.2026, 19:45 UTC (§18: L0′b gebaut). Davor 04.10.2026, 17:30 UTC (§18: L0′a gebaut). Davor 04.10.2026, 15:35 UTC (§18: L4 gebaut). Davor 04.10.2026, 14:32 UTC (§16: die Wahrnehmung der Antwort im Betrieb gemessen). Davor 04.10.2026, 14:16 UTC (§16: das Gesicht zeigt beim Sprechen die Wahrnehmung der Antwort). Davor 04.10.2026, 13:41 UTC (§18: der Umbruch der Phasenanzeige behoben). Davor 04.10.2026, 13:39 UTC (§18: L6 im Betrieb gemessen). Davor 04.10.2026, 12:52 UTC (§18: L3 im Betrieb gemessen; L6 gebaut; die Reihenfolge L6 → Generator → L4/L5). Davor 04.10.2026, 11:28 UTC (§18: L3 gebaut). Davor 04.10.2026, 10:30 UTC (§18: L3 kennt alle vier Ereignisse und baut den Weg aus `_t` §17.10; L4 erst nach L3 und mit Thema; L5 mit Arbeitszustand, Art der Aufgabe und Tooltip). Davor 03.10.2026, 20:48 UTC (§18: die Statuszeile zeigt jeden Arbeitszustand, L5). Davor 03.10.2026, 19:19 UTC (§18: L5 zeigt Pixies Arbeitszyklus auch in der Statuszeile). Davor 03.10.2026, 19:07 UTC (§18: L2 gebaut). Davor 03.10.2026, 17:09 UTC (§18: L1 gebaut). Davor 03.10.2026, 13:40 UTC (§18: L0 gebaut). Davor 03.10.2026 (§18 neu: Bauteile für den Leerlauf). Davor 02.10.2026
**Inhalt:** die Tests der Bausteine (§10) und die Bauberichte des Prototyps (§13.8, §13.10, §13.11). Dazu die Bauteile für den Client mit `ZIEL` / `TEST` / `MESSUNG` (§16) und die für den Leerlauf samt Abnahme (§18).

---

## 10. Testbarkeit

Jeder Baustein ist ohne GTK testbar. Tests, die ohne das jeweilige Verhalten rot werden:

| Test | Prüft |
|---|---|
| Arousal 0 ergibt Neutral | `face(s, 0) == neutral` für alle 8 Sektoren |
| Moderat schwächer als intensiv | gleicher Sektor, niedrigerer Arousal → kleinere Abweichung von Neutral |
| Stetigkeit bei Unterbrechung | Zielwechsel mitten im Übergang erzeugt keinen Sprung in Position oder Geschwindigkeit |
| Framerate-Unabhängigkeit | 1 s in 10 Schritten und in 60 Schritten ergeben denselben Endzustand (Toleranz) |
| Kanalbereiche | Mischung beliebiger Verläufe bleibt in allen Kanalgrenzen |
| Unbekannte Emotion | Emotion außerhalb des Kanons → Error-Log, Neutral, kein Absturz |
| Determinismus Renderer | gleicher `FaceState` + gleicher Seed → identische Pfade |

---

---

## 16. Bauteile für den Client

**Stand 02.10.2026.** Reihenfolge nach Abhängigkeit; B1 und B3 können nebeneinander laufen. Nach dem Schnitt in Module (`novaberg-avatar_t.md` §15.2) braucht erst B8 das Sprechen; empfohlen ist deshalb B3 → B6 → B7 → B4 → B8 — das Gesicht wird früher sichtbar. Ein Bauteil, das den Client berührt, berichtet zwei Bilanzzeilen — Server-Suite und Zeugen des Clients.

| Nr | Bauteil | ZIEL | TEST | MESSUNG | Prüftiefe |
|---|---|---|---|---|---|
| B1 | Sektor in der Antwort (Server) | Jede `character_response` trägt `nova_sektor` passend zu `nova_emotion`: 1–8, `null` bei `neutral`, `null` mit Error-Zeile bei einem Namen außerhalb des Kanons | Zeugen für alle 17 kanonischen Namen und einen unbekannten; bestehende Felder unverändert; Gegenprobe | eine echte `character_response` aus einem Mess-Turn mit wissenschaftlichem Thema: `nova_sektor` passt zu `nova_emotion` | schmal — additiv und rückholbar |
| B2 | Impulse erreichen den Avatar (Client) | Eine Antwort aus eigenem Impuls erreicht das Avatar-Panel wie eine gewöhnliche; die übrigen Panels verhalten sich unverändert | Zeuge am Stream-Handler mit ersetztem `GLib.idle_add` (Muster `client/tests/test_stream_assignment.py`) | ein echter Impuls bei geöffnetem Panel: das Gesicht wechselt | schmal |
| B3 | Ausdruck und Animator (Logik) | Aus Sektor und Arousal entsteht dasselbe Ziel wie im Prototyp, und der sichtbare Zustand folgt ihm stetig | die Tests aus §10; dazu Gleichheit mit Referenzwerten des Prototyps für alle neun Sektoren bei Arousal 0, 0,3, 0,6, 0,85 und 1,0 — als erzeugte JSON-Datei unter `client/tests/avatar_reference/`, ihr Erzeuger liegt im Labor neben dem Prototyp | — reine Logik, gemessen in B7 | tief — eine Abweichung vom Prototyp wäre still |
| B4 | Sprechen (Logik) | Aus einem Text entstehen dieselben Laute, Zeiten und Mundkanäle wie im Prototyp | Charakterisierung: Ausgabe des Prototyps für einen festen Satz Testsätze gegen die Python-Ausgabe, mit Toleranz für Gleitkomma | — | tief — wie B3 |
| B5 | Bilder | Grundbild, Gesichts- und Halsebene liegen als PNG in `client/avatar/images/`, die Gesichtsebene vorab ausgestanzt mit Alphakanal | Größe, Kanäle, Alphakanal unter der Kinnlinie | Sichtvergleich mit dem Prototyp | schmal — ob die Bilder committet werden, entscheidet O13 |
| B6 | Zeichnen | Dieselben Kanäle und derselbe Seed ergeben dieselbe Zeichnung, und das Gesicht gleicht dem Prototyp | Determinismus (gleiche Eingabe → gleiche Pixel), Grenzwerte aller Kanäle ohne Fehler; pixelgleich zum Prototyp ist nicht verlangt (ein Seed je Teil) | Sichtvergleich je Sektor neben dem Prototyp, durch den Meister | tief |
| B7 | Panel | Das Avatar-Panel zeigt Novas Emotion des laufenden Turns und lebt auch ohne Wechsel | Registrierung und Werkzeugleiste (bestehender Test); der Takt startet bei `map` und endet bei `unmap` | echter Turn mit wissenschaftlichem Thema: das Gesicht wechselt in etwa 1 s; Bildrate in Cairo bei Standardgröße, mit Kinnverzerrung und beim Sprechen | schmal |
| B8 | Sprechen im Panel | Erreicht eine Antwort das Panel, spricht der Mund ihren Text | Zeuge: Antwort → Lautfolge gestartet, Ende → Ruhe | echter Turn | schmal — erst nach O9 |
| W | Mimik nach der Literatur (seit 05.10.2026, `novaberg-avatar_t.md` §5.2) | Angst hebt die ganze Braue und spannt das Unterlid; weitet sich das Auge, hebt sich nur das Oberlid, und ein Lidschlag schließt beide Lider weiter; Zuversicht presst die Lippen leicht; moderate Freude lächelt ohne Zähne | `expression.json`, `idle.json` und `speech.json` neu aus dem Prototyp erzeugt; `test_eye_open_1215` (Unterlid bei `eo` 1,215 = bei 1,0) und ein Zeuge für den Lidschlag im Unterlid | das Gesicht des Clients neben dem Prototyp (600 px) bei Angst, Überraschung, Zuversicht und Freude, je 0,6 und 1,0; die Sichtprüfung im Client | schmal — die Werte bezeugen die Referenzen des abgenommenen Prototyps |

**Stand 03.10.2026 — gebaut, nicht im Betrieb gemessen.** Unter `client/avatar/` stehen Ausdruck und Animator (B3), Sprechen (B4), Zeichnen von Strich, Augen, Brauen, Extras und Mund (B6), Grundbild mit Verzerrung und ganzes Bild (`compose.draw_face`, `layers.load_layers`), die Puppe (`puppet.py`) und das Panel `client/ui/panels/avatar_panel.py` mit Eintrag in Registry und Werkzeugleiste (B7, mit B8). Die Zeugen laufen ohne GTK und ohne `cairo` (189 mit B2), die Client-Suite auf dem Host mit `test_toolbar_panels.py` (219 grün). Referenzwerte: `client/tests/avatar_reference/expression.json` (45 Ziele) und `speech.json` (vier synthetische Sätze), erzeugt aus dem Prototyp mit `labor/avatar/referenz_ausdruck.js` und `referenz_sprechen.js`. **Gemessen** mit echtem Cairo auf dem Host: das ganze Bild in allen neun Sektoren gleich dem Prototyp (Aufnahmen des Prototyps ohne Fenster, Bild für Bild daneben); eine Antwort spricht lippensynchron nach Lautzeiten — Öffnung je Silbe, Lippenschluss bei m/b/p, danach der Ausdruck; ein Bild mit 600 px braucht in Ruhe ≈ 30 ms, beim Sprechen ≈ 40 ms (≈ 25–34 Bilder/s; der Prototyp im Browser 60). **B1 entfällt für v1:** Die Antwort an den Client trägt `nova_emotion` und `nova_arousal`; das Panel bildet den Sektor aus dem Namen. → **Seit 04.10.2026 liest das Panel `emotion`/`arousal`**, die Wahrnehmung der Antwort, und nie mehr `nova_emotion`/`nova_arousal` (entschieden, `novaberg-avatar_k.md` §3; `novaberg-avatar_t.md` §14.2). Die alten Felder sind Novas Stimmung zu Beginn des Turns und liefen im Betrieb einen Turn nach. Fehlen die neuen, zeigt das Gesicht Neutral mit Error-Zeile, ohne Rückfall. Avatar-Zeugen `Ran 349` / `OK`, Client-Suite auf dem Host `Ran 404` / `OK`. **Im Betrieb gemessen 04.10.2026** an zwei Turns über Astronomie: Stimmung zu Beginn des Turns 0,60, Wahrnehmung der Antwort 0,65, das Panel übernimmt 0,65 (im folgenden Nachdenken abgelesen); Stimmung 0,65, Wahrnehmung 0,50, das Panel zeigt in der Antwort Freude 0,50 (Server-Log gegen Phasenanzeige). **B5:** Die Bilder als PNG (`labor/avatar/bilder_png.py`) liegen in `client/avatar/images/`, aber nicht im Repositorium (O13) — fehlen sie, zeigt das Panel eine Meldung. **B2 gebaut:** Eine Antwort aus eigenem Impuls (`reiz_herkunft: eigener_impuls`) erreicht nur das Avatar-Panel, mit ihrem Text unter `antwort` (`client/ui/turn_routing.py`, `broadcast_impulse`); die übrigen Panels laden bei einem Impuls nicht neu, eine Nachricht eines anderen Clients erreicht den Avatar nicht. Client-Suite auf dem Host danach `Ran 219 tests` / `OK`. **Offen:** der echte Turn und ein echter Impuls im sichtbaren Fenster; die Bildrate; ob `nova_emotion: ""` (ein Turn ohne Emotionsverlauf) neutral bedeutet oder ein Fehler ist — heute neutral mit Error-Zeile.

**Stand 05.10.2026 — W gebaut.** Die Werte in `client/avatar/expression.py` folgen dem Prototyp, das Unterlid in `client/avatar/drawing_eye.py` der Öffnung nur bis 1; `lid_extent` trägt den Lidschlag als eigenen Wert, weil sich `min(eo, 1)` aus dem Produkt der Öffnung nicht zurückrechnen lässt. Suite des Avatars `Ran 428 tests` / `OK`. **Gegenproben** an Kopien: Angst ohne die neuen Brauen oder ohne `arc` → der Referenzzeuge des Ausdrucks rot; das alte Unterlid → zwei Zeugen der Zeichnung rot (vorhergesagt einer, der zweite hält einen festen Wert); das Unterlid ohne Lidschlag → nur der neue Zeuge; Zuversicht ohne `au24` → Ausdruck und sechs Läufe des Leerlaufs; Freude ohne `jaw` → Ausdruck und Sprechen, **der Leerlauf merkt es nicht** (vorhergesagt rot). **Gemessen** mit Cairo, der Mund nach `mouth_state_combine` wie in der Puppe: Prototyp/Client bleiben in allen acht Fällen bei 1,17–1,18 von 255 wie vorher, und der Client ändert sich von alt zu neu so stark wie der Prototyp (auf ±0,01). Im Prototyp vom Eigentümer abgenommen (*„index.html sieht gut aus“*); ~~**offen:** die Sichtprüfung im Client~~ → **im Client abgenommen am 05.10.2026, 06:2x UTC:** *„Das sieht gut aus. Die Bewegungen sind angenehm und weich.“* Dabei fiel ihm auf, dass die Augen mit dem Kopf mitwandern, wenn er nachdreht, statt ihren Punkt zu halten — dazu entsteht ein Entwurf im Labor-Prototyp.

**Nicht in v1:** Mischung des Verlaufs (O7), Konflikt (O8), Vorlauf des Mundes vor dem Ton (keine Tonausgabe), Ausspracheregeln aus einem Lexikon.

## 18. Bauteile für den Leerlauf

**Stand 03.10.2026.** Was gebaut wird, steht in `novaberg-avatar_t.md` §17; die Referenz ist der Generator im Labor (§17.1). Reihenfolge nach Abhängigkeit: L0 → L1 → L2 → L3 → L5; L4 kann neben L1 bis L3 laufen. **Seit 04.10.2026, nach der Messung von L3 (entschieden vom Meister):** erst L6 (die Phasenanzeige), dann der Generator nachgestellt nach den Befunden der Messung (Fundliste, 04.10.2026), dann L4 und L5. **Seit 04.10.2026:** L4 kann daneben gebaut werden, geht aber **erst nach dem Commit von L3** in den laufenden Baum — vorher erschiene jedes seiner Ereignisse im Chat (`novaberg-avatar_t.md` §17.10). Ein Bauteil, das den Client berührt, berichtet die Zeugen des Clients; L4 die Server-Suite.

| Nr | Bauteil | ZIEL | TEST | MESSUNG | Prüftiefe |
|---|---|---|---|---|---|
| L0 | Referenz (Labor, vor dem Bau) | Der Generator folgt dem Ereignismodell des Clients (§17.9), und seine Verläufe liegen als Referenzwerte vor | `labor/avatar/leerlauf_pruefen.py` grün; die Referenz als erzeugte JSON-Datei `client/tests/avatar_reference/idle.json`: Ereignisfolgen (Turn, Antwort, Ende der Wiedergabe, Pixie-Auftrag) × Startwerte × Lagen, je Lauf Zustände, Formen mit Beginn, Dauer und Blickpunkt, Lidschläge und Ziele aller Kanäle zu festen Zeiten | — | tief — eine falsche Referenz macht jeden Zeugen falsch |
| L1 | Leerlauf-Logik (`client/avatar/idle.py`, Katalog in einem eigenen Modul) | Für dieselben Ereignisse, Eingänge und denselben Startwert plant der Client dieselben Zustände, Formen, Dauern, Blickpunkte und Lidschläge wie der Generator | Charakterisierung gegen `idle.json` (Gleitkomma mit Toleranz); dazu die Prüfpunkte des Generators als Zeugen: kein F14 und kein offener Mund im Nachdenken, Einatmen 0,7–0,9 s, Nachklang endet an seiner Dauer, Antwort beginnt abgewandt und endet beim Betrachter, Lidschläge Nachdenken < Rauschen < Antwort bei gleicher Energie | — reine Logik, gemessen in L3 | tief — eine Abweichung vom Generator wäre still |
| L2 | Puppe mit Leerlauf (`puppet.py`, `animator.py`) | Die Puppe nimmt in jedem Zustand die Ziele des Leerlaufs ein — Feder je Kanalgruppe, Lidschlag aus dem Leerlauf, in der Antwort die Sprechschicht darüber — und meldet das Ende der Wiedergabe | Ziele gegen `idle.json` zu festen Zeiten; Stetigkeit beim Zustandswechsel (kein Sprung in Lage oder Geschwindigkeit); 1 s in 10 und in 60 Schritten ergibt denselben Endzustand (§10); das feste Blinzeln der Puppe (`_blink`) schweigt | — | tief |
| L3 | Panel und Ereignisse im Client | Sendet der Nutzer — in diesem oder einem anderen Client —, denkt Nova nach; trifft die Antwort ein, atmet sie ein und spricht; danach klingt sie nach und fällt ins Rauschen; ein gescheiterter Turn und ein Fehler beim Senden führen ins Rauschen. **Der Client kennt alle vier Ereignisse der Arbeitszyklen**, keines erscheint im Chat (`novaberg-avatar_t.md` §17.10, Schritte 1, 2, 4 und 5; entschieden 04.10.2026) | ~~Zeugen am Verteiler mit ersetztem `GLib.idle_add` (Muster `client/tests/test_stream_assignment.py`): Senden → `turn_beginnt` an Panels mit `REACTS_TO_IDLE`, an andere nicht; `turn_gescheitert` → Rauschen; Wächter nach 600 s~~ → **seit 04.10.2026:** **Eingang** (ersetztes `GLib.idle_add`, Muster `client/tests/test_stream_assignment.py`): `turn_gescheitert`, `pixie_auftrag` und `impuls_denkt` erreichen den neuen Rückruf, nicht den Chat — Zwilling: ein unbekannter Typ fällt weiter in den Auffangzweig, `turn_gescheitert` räumt weiter seine Kennungen ab; **Typ:** ohne `emotion` und `arousal` → leer, mit ihnen → ihre Werte; ungültige `phase` oder `spur` → Error-Zeile und kein Ereignis; **Verteiler** (Muster `DeliverTurnTest` in `client/tests/test_avatar_impulse.py`): ein Panel mit dem Merkmal bekommt das Ereignis, eines ohne nicht, auch wenn es `turn_reactive` ist; ein scheiterndes Panel hält die übrigen nicht auf; Senden und `user_message` → `turn_beginnt`; ein Fehler beim Senden → wie `turn_gescheitert`; **Panel:** zwei Ereignisse zwischen zwei Bildern erreichen die Puppe in der Reihenfolge des Eintreffens mit der Zeit des nächsten Bildes, `pixie_auftrag` ohne Thema; Wächter nach 600 s | ein echter Turn mit wissenschaftlichem Thema im sichtbaren Fenster, als Mitschnitt; Abnahme nach §18.1 | schmal |
| L4 | Pixie-Ereignisse (Server) | Beginnt oder beendet Pixie einen Auftrag, und beginnt oder endet der CharacterGraph für einen Impuls, erfährt es der Client — ~~ohne Thema~~ → **mit dem Thema eines Auftrags, für den Tooltip der Statuszeile** (seit 04.10.2026, `novaberg-avatar_t.md` §17.10) —, ohne den Auftrag oder den Server anzuhalten | Zeugen mit ersetztem Broadcast: ein Auftrag → `pixie_auftrag` `beginn` und `ende` mit `spur`, `art`, `emotion`, `arousal` und ~~**ohne**~~ → **mit** `thema`; ein Auftrag ohne Emotion → ohne die Felder `emotion` und `arousal`; ein leerer Heartbeat → kein Ereignis; eine periodische Aufgabe → kein Ereignis; ein Fehler beim Senden → Error-Zeile, der Auftrag läuft weiter; ein Impuls ohne Antwort → `impuls_denkt` `ende`; **ein Zeuge mit echtem Event-Loop**, dass das Senden aus dem Heartbeat nicht wartet (der ersetzte Broadcast sähe ein `broadcast_threadsafe` im Loop nicht); Gegenprobe | ein echter Pixie-Lauf: die Ereignisse im Log des Clients, ~~ihre Felder ohne Inhalt~~ → ihre Felder, ein Thema nur in `pixie_auftrag` | tief — ein Fehler im Hintergrund wäre still. **Eigener Arbeitsbaum** — der eingehängte Baum lädt die laufende Nova neu (`--reload`). **In den laufenden Baum erst nach dem Commit von L3** |
| L5 | Pixie im Client | Ein Auftrag Pixies färbt das Rauschen; im Turn ändert er nichts Sichtbares; ein Impuls lässt Nova nachdenken. **Die Statuszeile zeigt jeden Arbeitszustand lückenlos** — Pixies Aufträge in beiden Spuren und den CharacterGraph bei Turn und Impuls, von Beginn bis Ende, aus denselben Ereignissen und dem Turn des Clients; *idle* steht nur, wenn nichts läuft (`novaberg-avatar_k.md` §3, entschieden 03.10.2026). **Seit 04.10.2026:** Sie nennt die Art der Aufgabe — „Charakter-Berechnung“, „Recherche“, „Vertiefung“ … —, weitere Angaben wie das Thema im Tooltip; das Momentum entfällt. Öffnet das Panel, während der CharacterGraph denkt, beginnt es im Nachdenken (`novaberg-avatar_t.md` §17.10, Schritte 3, 6 und 7) | Zeugen: `pixie_auftrag` im Rauschen → nächster Zyklus mit der neuen Emotion und `a` = 0,6; im Nachdenken → nur der Rückfall; `impuls_denkt` → Nachdenken, `ende` ohne Antwort → Rauschen; **Arbeitszustand** in reinen Funktionen: zwei offene Nachrichten, eine Antwort auf die erste → weiter Charakter-Berechnung, Zwilling: eine Antwort, die beide nennt → *idle*; der Text der Statuszeile kommt nur aus ihm — das Momentum schreibt nicht mehr; Wächter nach 600 s auch hier; **Öffnen** während eines Turns → Nachdenken, Zwilling: ohne → Rauschen; ein laufender Auftrag wird nicht nachgereicht; **Statuszeile:** `pixie_auftrag` `beginn` → Pixie arbeitet (~~mit Art und Spur, ohne Thema~~ → mit der Art, das Thema im Tooltip), zwei Spuren: erst das Ende beider → Pixie *idle*; Senden des Nutzers → der CharacterGraph denkt (Turn) bis zur Antwort oder `turn_gescheitert`; `impuls_denkt` `beginn` → er denkt (Impuls) bis zur Antwort oder `ende`; an keinem Übergang eine Lücke, in der *idle* stünde, obwohl etwas läuft; ohne Panel des Avatars wirkt es ebenso | ein echter Pixie-Lauf bei offenem Panel: das Rauschen wechselt die Emotion, **die Statuszeile zeigt den Auftrag und danach wieder *idle*** | schmal |
| L6 | Phasenanzeige im Panel | Unter dem Gesicht steht, in welcher Phase der Leerlauf ist — Zustand mit Angabe und Emotion, laufende Form mit Dauer, Blick und nächster Form, das Band des Zyklus und seine Spanne —, wie im Kasten „Generator“ der Referenz; das Gesicht plant dabei genau wie vorher (entschieden 04.10.2026, `novaberg-avatar_k.md` §3) | Eine Logik, die in jedem Schritt ihren Status abgibt, plant gleich wie ihr Zwilling ohne Abfrage (Ziele, Formen, Lidschläge über mindestens drei Fälle); die Angabe je Zustand; die nächste Form oder *neuer Zyklus*; die Spanne gleich der geplanten; Blickrichtung an den Grenzen mit Zwilling; die Anzeige höchstens alle 120 ms | ein Turn im sichtbaren Fenster als Mitschnitt, mit mindestens 30 s Rauschen davor und danach: die Anzeige folgt den Phasen des Gesichts | schmal — die Charakterisierung von L1 bleibt unverändert grün |

**L0 gebaut, 03.10.2026, 13:40 UTC.** Der Generator folgt dem Ereignismodell (`novaberg-avatar_t.md` §17.9, mit den dort entschiedenen Formen), die gekoppelten Lidschläge werden je Zustand abgezogen (§17.6), der Blick ist allein der der Form (§17.3). Prüfung `leerlauf_pruefen.py` mit 40 Startwerten in drei Lagen: `360 Läufe, 0 Verstöße`; **Gegenproben:** die Antwort 100 ms zu spät behandelt → `120 Läufe, 120 Verstöße`, alle an E1, vorhergesagt 120; der Blick der Basis wieder addiert → `180 Läufe, 1190 Verstöße`, alle an den Blickzielen (F16 in allen drei Lagen, A1 und das Nachdenken nur bei Hoffnung — vorhergesagt waren F16 und A1 in allen drei). **Zweite Kontrolle** der Referenz (anderer Zugriff: die Datei gegen die Sätze des Konzepts, 16.222 Aussagen): 71 Abweichungen in vier Befunden, ein stiller Befund zur Abdeckung, sieben Lücken — die Befunde behoben (Blick der Basis, Lidform der neuen Form, beim Einfall ein Lidschlag, `ende` mit Art und Emotion), die Abdeckung um zwei Fälle erweitert, die Lücken in `_t` §17.9; danach mit ihren Skripten nachgemessen. Die Referenz `client/tests/avatar_reference/idle.json` (657 KB): zehn Fälle × drei Startwerte, Ereignisse als Eingang, je Lauf Zustände, Formen, Lidschläge mit Schließ- und Öffnungsdauer, behandelte Ereignisse (`wiedergabe_endet` entsteht im Generator, im Client meldet es die Puppe) und jede Sekunde die Ziele aller 35 Kanäle mit Lidöffnung, ω des Gesichts, `k` und `a`. Erzeugt von `labor/avatar/leerlauf_referenz.py`.

**L1 gebaut, 03.10.2026, 17:09 UTC.** Die Leerlauf-Logik des Clients: `client/avatar/idle.py` (`IdleLogic`) und der Katalog `client/avatar/idle_catalog.py`, rein — kein GTK, kein `cairo`, kein Netz, keine Uhr. Die Ereignisse kommen als Objekte (`TurnBegins`, `TurnFailed`, `AnswerArrives` mit der Dauer der Wiedergabe statt des Textes, `ImpulseThinks`, `PixieJob`) über `post`; `step(now_ms, gaze_x, gaze_y)` behandelt die fälligen und liefert die Ziele aller 35 Kanäle, die Öffnung des Lids, ω des Gesichts und den Zustand. Der Blick des Gesichts kommt von außen, weil der Blickwechsel beim Beginn eines Zustands gegen die Feder misst (L2). Der Zufall ist mulberry32 mit der Reihenfolge der Ziehungen des Generators. **Zeugen** `client/tests/test_avatar_idle.py` (46): die Charakterisierung aller 30 Läufe von `idle.json` im 20-ms-Raster — Zustände, Formen, Dauern, Blick, Lidschläge, behandelte Ereignisse, die Ziele jeder Sekunde; die Dauer der Wiedergabe aus dem gemeldeten Ende, sodass das Ende des Zustands den Nachlauf prüft —, dazu die Prüfpunkte des Generators (kein F14 und kein offener Mund im Nachdenken außer E1, Einatmen 0,7–0,9 s ab dem Eintreffen, Nachklang endet an seiner Dauer, Antwort beginnt abgewandt und endet beim Betrachter, Lidschlagrate Nachdenken < Rauschen < Antwort an der Rate je Zustand). Suite des Avatars `Ran 235 tests in 8.682s` / `OK`. **Gegenproben:** Faktor der Spanne im Nachdenken 0,85 → 27 rot, genau die Läufe mit einem Zyklus im Nachdenken (vorhergesagt 27); Nachlauf nach der Wiedergabe 300 statt 400 ms → 27 rot, alle Läufe mit Antwort (vorhergesagt 27); eine Höhe des Erinnerns verschoben → 15 rot (vorhergesagt 15 sicher und einer bedingt; der bedingte traf, ein sicherer nicht — dort meidet Nova, und das Meiden hat einen eigenen Zweig). Gegen den Generator Funktion für Funktion geprüft, ohne Abweichung. **Offen:** L2–L5; die Messung kommt mit L3. Daneben: `SECTOR_BY_NAME` steht in `idle_catalog.py` und `puppet.py` zweimal, ohne Zeugen, der beide bindet; die Gleichheit von `Math.log`/`Math.sin` in V8 und der C-Bibliothek ist nur über die Charakterisierung belegt.

**L2 gebaut, 03.10.2026, 19:07 UTC.** Die Puppe (`client/avatar/puppet.py`) hält eine `IdleLogic` und nimmt in jedem Schritt deren Ziele ein: die Feder je Kanalgruppe wie im Generator (Blick ω 35, Pupille ω 5, Gesicht ω der Logik, `animator.spring_step_each`), kein Mundversatz; `Pose.blink` ist die Öffnung des Lids der Logik, das feste Blinzeln (`_blink`) ist entfernt; in der Antwort liegt die Sprechschicht darüber. Die Logik bekommt den sichtbaren Blick der Feder vor jedem Schritt. **Die Wiedergabe:** Beim Eintreffen rechnet die Puppe die Dauer aus dem Text (`speech_timeline`) und gibt sie mit der Antwort an die Logik; das Sprechen beginnt, wenn die Logik die Antwort beginnen lässt (`IdleFrame.answer_at_ms`), mit dem Text dieser Antwort, und endet mit der Wiedergabe der Logik. Ein neuer Turn in der Antwort beendet das Sprechen ohne Sprung (abgeleitet aus §17.2 des `_t`: *ein neuer Turn unterbricht jeden Zustand sofort*), ebenso eine Antwort ohne Text, die eine laufende ablöst. Die übrigen Ereignisse gibt `puppet_event` an die Logik; aufgerufen wird es mit L3. **Abweichend vom TEST oben, entschieden vor dem Bau:** Die Referenz `idle.json` plant mit dem Blick (0, 0), die Puppe mit dem Blick der Feder, und davon hängt eine Ziehung ab — die Zeugen halten die Ziele der Puppe deshalb gegen einen **Zwilling** (eine zweite Logik mit demselben Startwert, denselben Ereignissen und dem Blick, den die Puppe übergab), in jedem Schritt aller zehn Fälle, exakt; die Bildrate (1 s in 10 und in 60 Schritten) gilt der Feder bei festem Ziel, denn die Logik plant im Takt der Bilder. Stetigkeit an jedem Zustandswechsel mit einer Schranke aus ω und Schritt — für den Blick ist sie bei 20 ms blind (2ω·dt = 1,4), gedeckt durch den Vergleich jedes Kanals mit der geschlossenen Form der Feder. Suite des Avatars `Ran 253 tests` / `OK`. **Gegenproben:** Blick ω 5 statt 35 → 10 rot (vorhergesagt 10); Blick (0, 0) an die Logik → 28 rot; Abbruch beim neuen Turn entfernt → 1 rot; Abbruch bei einer Antwort ohne Text entfernt → 1 rot — alle wie vorhergesagt. **Vor dem Commit gefunden und behoben:** Eine Antwort ohne Text, die eine laufende ablöste, ließ den alten Text weitersprechen. **Offen:** L3 (Panel und Ereignisse, mit der Messung), L4, L5. Das Panel ist unverändert; sichtbar wird der Leerlauf erst mit L3.

**L3 gebaut, 04.10.2026, 11:28 UTC.** Die Arbeitszyklen erreichen das Panel, nach dem Weg aus `novaberg-avatar_t.md` §17.10 (Schritte 1, 2, 4 und 5).

- **Der Typ** steht in `client/ui/work_events.py`, ohne GTK. Es gibt vier unveränderliche Ereignisse ohne Zeit: `TurnStarted`, `TurnFailure`, `ImpulseThinking` und `PixieWork` (mit Thema). `work_event_from_payload` formt die Nutzlast des WebSockets einmal um, im Stream-Handler vor `GLib.idle_add`. Jede ungültige Nutzlast ergibt eine Error-Zeile ohne das Thema und kein Ereignis.
- **Der Eingang:** `pixie_auftrag` und `impuls_denkt` gehen nur an den neuen Rückruf `on_work_event` und nicht mehr in den Auffangzweig. `turn_gescheitert` gibt weiter seine Kennungen frei, zeigt die Stufe „Ausfall“ und geht zusätzlich an den Rückruf.
- **Das Hauptfenster** erzeugt „Turn beginnt“ vor dem Senden und bei `user_message` aus einem anderen Client. Einen Fehler beim Senden meldet es als „Turn gescheitert“; `_on_error` kommt nur aus dem Senden. Jedes Ereignis gibt es über die Registry an die Panels mit `REACTS_TO_WORK`. Gewählt wird nach dem Merkmal allein (`deliver_work_event` in `turn_routing.py`), und ein scheiterndes Panel hält die übrigen nicht auf.
- **Das Avatar-Panel** hält Antworten und Ereignisse in einer Warteschlange (`AvatarFeed` in `client/ui/avatar_feed.py`, ersetzt `_pending`). Im nächsten Bild übergibt es sie in der Reihenfolge des Eintreffens an die Puppe. `PixieJob` bekommt kein Thema.
- **Zeugen** in drei neuen Dateien: `test_avatar_work_events.py`, ~~`test_avatar_work_stream.py` und `test_avatar_work_window.py`~~ → seit 04.10.2026 `test_work_stream.py` und `test_work_window.py` (umbenannt, Inhalt gleich: Sie brauchen `requests`, `websocket` und GTK und gehören deshalb nicht zum Lauf `test_avatar*.py`, der ohne diese Bibliotheken läuft). Die ganze Client-Suite ergibt `Ran 333 tests` / `OK`. Die beiden letzten Dateien importieren Stream-Handler und Hauptfenster und laufen deshalb nur mit `requests`, `websocket` und GTK.
- **Gegenproben:**
  - Zweig für `pixie_auftrag` entfernt → 2 rot, vorhergesagt war 1. Der zweite Zeuge schickt eine ungültige Nutzlast dieses Typs, die ohne den Zweig im Auffangzweig landet.
  - Verteiler zusätzlich nach `CATEGORY` → 1 rot, wie vorhergesagt.
  - Umgekehrte Reihenfolge im Panel → 2 rot, wie vorhergesagt.
  - Kein „Turn beginnt“ bei `user_message` → 1 rot, wie vorhergesagt.
- **Die Messung steht aus:** ein echter Turn im sichtbaren Fenster, abgenommen nach §18.1.
- **Offen:** L4 (Server; darf jetzt in den laufenden Baum) und L5 (Arbeitszustand, Statuszeile; das Momentum in `_handle_answer` bleibt bis dahin).

**L3 im Betrieb gemessen, 04.10.2026.** Es gab zwei Turns über Astronomie mit offenem Panel. Der zweite ist im Bildschirmmitschnitt (60 fps) ausgewertet und mit dem Code des Clients nachgespielt:

- **Im Mitschnitt:** Nachdenken 12 → 137 s (125 s), Antwort ab 137,5 s, danach Nachklang. Im Chat stand keine JSON-Zeile.
- **Im Nachlauf:** Nachdenken 12,0 → 137,75 s, Antwort bis 242,2 s, Nachklang 14,8 s.
- **Der Weg der Ereignisse ist damit bestätigt.**
- **Die Abnahme nach §18.1 besteht der Turn nicht:**
  - Das Nachdenken liest sich als Warten. Im Nachdenken liegt `|gaze_x|` im Mittel bei 0,23, im Rauschen bei 0,21.
  - Das Einatmen ist kaum sichtbar (Lippen bis 3,7 px), und der Sprechbeginn springt.
  - Die Lidschläge sind ungleich verteilt.
  - Diese Abstände liegen in der Referenz und in der Zeichnung, nicht in L3; die Einzelheiten stehen in der Fundliste (04.10.2026).
- **Nicht gemessen:** der Übergang ins Rauschen (der Mitschnitt endet vorher) und ein neuer Turn im Nachklang.

**L6 gebaut, 04.10.2026, 12:52 UTC.** Unter dem Gesicht steht die Phase des Leerlaufs, wie im Kasten „Generator“ der Referenz.

- **Die Lese-Sicht:** `IdleLogic.status(now_ms)` liefert `IdleStatus` (`client/avatar/idle_status.py`). Darin stehen der Zustand mit seiner Angabe und die Emotion mit Quelle. Dazu die laufende Form mit Dauer und Blickrichtung, die nächste Form oder *neuer Zyklus*, das Band des Plans und die Spanne.
  - Die Spanne merkt der Plan beim Planen (`_Plan.span`), sie wird nicht neu gerechnet.
  - `status` zieht keine Zufallszahl, setzt kein Feld und behandelt kein Ereignis.
  - Die Emotion kommt aus derselben Rechnung wie die Ziele. Deren Mix im Nachklang ist dafür in `_afterglow_mix` gezogen.
- **Der Text** steht in `client/avatar/status_text.py`, ohne GTK: die Richtung mit den Grenzen 0,12 und 0,15 und Zahlen mit Komma. `status_due` lässt die Anzeige höchstens alle 120 ms nachziehen.
- **Die Puppe** reicht den Wert mit `puppet_status` durch.
- **Das Panel** zeigt fünf Zeilen und das Band als Zeichenfläche, die laufende Form markiert. Ein Fehler der Anzeige hält nur die Anzeige an, das Gesicht läuft weiter.
- **Zeugen** in `test_avatar_status_logic.py` und `test_avatar_status_text.py`:
  - Zwei Logiken über drei Fälle der Referenz planen gleich, auch wenn eine davon in jedem Schritt `status` fragt.
  - Lange Folgen vergleicht eine Hilfe, die die erste Abweichung meldet: Der volle Diff von `assertEqual` über Tausende Bilder lief bei Rot länger als 600 s.
  - Die ganze Client-Suite ergibt `Ran 394 tests` / `OK`, die Charakterisierung von L1 ist unverändert grün.
- **Gegenproben**, alle rot wie vorhergesagt:
  - eine Zufallszahl in `status` → 5 rot in 2,6 s;
  - die nächste Form gleich der laufenden → 1;
  - die Grenze für *seitlich* bei 0,2 → 1;
  - die Anzeige in jedem Bild → 2.
- **Ohne Zeugen** ist, dass das Panel `status_due` aufruft; das zeigt erst die Messung.
- **Die Messung steht aus:** ein Turn im sichtbaren Fenster mit je mindestens 30 s Rauschen davor und danach.

**L6 im Betrieb gemessen, 04.10.2026.** Der Mitschnitt läuft 305 s: zwei Turns über Astronomie, der zweite im Nachklang des ersten, davor und danach Rauschen. Die Anzeige ist alle 0,25 s abgelesen und das Gesicht Bild für Bild vermessen.

- **Die Anzeige folgt dem Gesicht:** Alle 9 Zustandswechsel liegen innerhalb von 0,25 s an Chat, Mund und Lidschlag. Rund 80 Formwechsel gehen bei *in 0 s* zur angekündigten Form. Abgebrochen wird eine Form nur bei einem Zustandswechsel, und dort gehört es so. Die Markierung im Band stimmt, und nichts flackert.
- **Ein Turn im Nachklang** wechselt sofort ins Nachdenken.
- **Ein Mangel:** ~~Im Nachklang bricht die erste Zeile um, und das Gesicht springt von 409 auf 392 px (Fundliste).~~ → **behoben 13:41 UTC:** Keine Zeile bricht mehr um, was nicht passt, wird mit „…“ gekürzt, und der volle Text steht im Tooltip (`client/ui/status_label.py`). Ein Zeuge mit GTK (`client/tests/test_status_view.py`, läuft auf dem Rechner mit Anzeige) hält die Höhe für kurzen und längsten Text gleich; sein Zwilling mit Umbruch wird höher. Die ganze Client-Suite ergibt `Ran 400 tests` / `OK`. Die Gegenprobe mit Umbruch: 5 rot.
- **Die Befunde aus der Messung von L3 bestehen fort**, jetzt mit der Anzeige belegt:
  - Das Einatmen dauert 0,75 s wie geplant, ist aber im Bild nicht zu sehen.
  - Die Blickrichtung erreicht das Bild kaum.
  - Im Nachklang ist die Lidschlagrate am höchsten.
- **Neu:** Die Antwort trägt die Emotion des vorigen Turns (Fundliste).

**L4 gebaut, 04.10.2026, 15:35 UTC.** Der Server sendet die Arbeitszyklen an den Client.

- **`pixie_auftrag`** (`server/services/work_events.py`, gerufen im Heartbeat `server/services/pixie/scheduler.py`): `beginn` nach der Wahl des Agenten und vor seinem Lauf, `ende` nach dem Lauf, auch mit Fehler, nie nach einem leeren Heartbeat. Felder `phase`, `spur`, `art` (geschlossene Menge `QUEUE_JOB_KINDS` des Routers), `emotion`/`arousal` und `thema` nur, wenn der Auftrag sie trägt — abwesend, nicht leer. Nur Aufträge mit Nutzer, an diesen Nutzer; periodische Aufgaben senden nichts. Auch die Promotions-Queue sendet (Spur `cpu`, ohne Emotion).
- **`impuls_denkt`** (Event-Consumer): `beginn` und `ende` um den ganzen Durchlauf eines Impulses, `ende` auch ohne Antwort und nach einem Fehler, immer nach der Antwort.
- **Gesendet mit `await broadcast(…)`**; ein Fehler beim Senden schreibt eine Error-Zeile, Auftrag und Turn laufen weiter.
- **Zeugen** `server/tests/test_work_events.py` (18), darunter einer mit echtem Event-Loop: Das Senden aus dem Heartbeat hält den Loop nicht an. Server-Suite `Ran 4094 tests` / `OK` (vorher 4076). Gegenprobe `emotion: null` statt Weglassen → 1 rot, wie vorhergesagt; drei weitere vorhergesagt, nicht gelaufen.
- **Die Messung steht aus:** ein echter Pixie-Auftrag bei offenem Panel; im Rauschen zeigt die Phasenanzeige *Emotion: Pixie* mit der Emotion des Auftrags.
- **Befund:** `_event_verarbeiten` erwirbt `graph_run_lock` blockierend in einer Koroutine (bis 60 s); das hielte auch das Senden an (Fundliste).

**L0′a gebaut, 04.10.2026, 17:30 UTC** — die Referenz nachgestellt nach den Messungen von L3 und L6 (Fundliste) und den Entscheidungen in `novaberg-avatar_k.md` §3, erster Teil. Im Nachdenken geht der Blick ins Leere: F5 abgewandt, F9 dort ein kurzer Akzent von 2–3 s, F16 halb so oft; geplant beim Betrachter 9,0 % der Nachdenkzeit (vorher 29 %). Das Einatmen öffnet den Mund erkennbar, die Antwort gleitet ohne Sprung in die Emotion mit dem Faktor 0,75, die Öffnung der Basis bleibt dort klein, und Brauen und Mundwinkel rauschen leise. Die Pupille weitet sich mit der Energie; Angst und Überraschung verengen sie nicht mehr. Die Prüfung kennt eine neue Lage *langes Nachdenken* (120 s) und neue Prüfpunkte (G1, G2, O1–O3, P-1, P-2, E1 geändert): `412 Läufe, 0 Verstöße`; elf Gegenproben rot wie vorhergesagt. **Noch nicht im Client:** die Referenzwerte `idle.json` und `expression.json` werden mit L1′ neu erzeugt; bis dahin bleibt der Client auf der Referenz von L0. **Als Nächstes:** L0′b (Iris-Weg, Lidschläge, geschlossenes Auge), dann L1′ und L2′.

**L0′b gebaut, 04.10.2026, 19:45 UTC** — die Referenz nachgestellt, zweiter Teil. Der Blick erreicht das Bild: Die Iris wandert 0,5 statt 0,3 der halben Augenbreite (senkrecht 0,26 statt 0,16), das Oberlid hebt sich beim Blick nach oben. Die Lidschläge: Abstände nach Gamma(3) statt exponentiell, ein in der Sperrzeit fälliger Lidschlag wird neu gezogen statt verschoben (keine Paare bei genau 0,8 s mehr), ein Einfall ersetzt die ganze Serie und sperrt 1 s, die Energie klingt im Nachklang mit aus, das Auge bleibt 40 ms × Lidform geschlossen, ein neuer Lidschlag setzt an einem laufenden an. **Am Ende der Antwort** kommt genau ein Lidschlag mit anschließender Sperre — vorher häuften sich dort bis zu vier. Das geschlossene Auge trägt Wimpern wie das offene. Die Prüfung: neue Prüfpunkte G3, N1, L-1 … L-6, B5 erweitert (*Nachklang < Antwort*); L-3 als Anteil (höchstens 2 % der Läufe einer Lage mit 4 Lidschlägen um das Ende der Antwort, keiner mit 5) — gemessen 0 %. `412 Läufe, 0 Verstöße`; elf Gegenproben je an ihrem Prüfpunkt rot. **Unbezeugt:** die Klausel *keiner mit 5* — die Rate ist bei 32/min begrenzt, kein Eingriff erreicht sie. **Im Client noch nicht** (L1′, L2′).

**L0′c gebaut, 04.10.2026, 20:31 UTC** — die Kopfdrehung in der Referenz (entschieden, `novaberg-avatar_k.md` §3). Neuer Kanal `yaw` in Grad, hart begrenzt auf ±15°, mit eigener, träger Feder (ω 3,5). Gezeichnet als zweite Gitterverzerrung über das fertige Bild: Jeder Punkt wandert nach seiner Tiefe, die Nase am meisten, der Hals verdrillt sich, die Schultern bleiben; bis 0,05° bleibt der bisherige Zeichenweg. Der Kopf folgt dem Blick 200 ms nach den Augen, meist wenig; wendet sich der Blick im Nachdenken zur Seite, dreht er etwa 10° mit; dazu leises Wandern um 1°. Der Zufall der Drehung kommt aus einer eigenen Quelle — mit und ohne Drehung plant der Leerlauf dieselben Formen, Lidschläge und Blicke (Y5, 100 Laufpaare). Im langen Nachdenken ist der Kopf in 90 % der Zeit mindestens 1°, in 69 % mindestens 5° gedreht. Neue Referenz `client/tests/avatar_reference/yaw.json` (acht Winkel, Verschiebung an 696 Punkten). Prüfung `513 Läufe, 0 Verstöße`. ~~**Offen:** die Gegenproben~~ → **Gegenproben gelaufen, 04.10.2026, 21:49 UTC** — zwölf Eingriffe, je an einer frischen Kopie:

- **Y1** (tiefes Ziel 20°, ohne Begrenzung): `513 Läufe, 397 Verstöße`, alle an Y1, je Lauf einer (vorhergesagt: fast alle 400).
- **Y2** (Vorzeichen gedreht): 400 an Y2, **Y3** (Kopf ohne Verzögerung): 400 an Y3 — je genau wie vorhergesagt, sonst nichts rot.
- **Y4** (das Zurück erbt das Ziel): 400 an Y4 und 400 an Y1, wie vorhergesagt.
- **Y5** (die Drehung zieht aus dem Zufall des Plans): alle 100 Laufpaare rot (Zustände, Formen, Lidschläge, Proben; Ereignisse in 91). **Dazu L-6** in der Lage *langes Nachdenken*: Median der längsten Pause 10,1 s gegen die Grenze 10 — die Lage hält sie im Grundbau mit 10,0 s, ohne Abstand.
- **D1** (Nasentiefe 26): 8 Winkel; **D5** (Rand bewegt sich): 60 Winkel, dazu D1 an 8; **D6** (Grenze 30°): 2 — wie vorhergesagt.
- **D3** bei Grenze 30°: rot, aber an 25 Winkeln statt höchstens 14 — **die linke Seite klappt schon ab −21,5° um**, die rechte ab 27°. Innerhalb von ±15° bleibt das ohne Wirkung; der Abstand zur Grenze ist links 6,5°, nicht 12°.
- **Die Prüfläufe zeichnen ungedreht:** ohne diese Stelle läuft ein Prüflauf in die Frist von 120 s (zweimal gemessen; ein erster Lauf blieb bei 0,6 s, ungeklärt); mit `kopf=0` 0,6 s.
- **Die Prüfung liest genau ein Element:** der alte Lesezugriff mit dem alten Kommentar → `JSONDecodeError`; nur der alte Kommentar → grün; ein zweites Element → `RuntimeError` mit der Zahl.

**Sichtprüfung des Eigentümers, 04.10.2026, 22:00 UTC** — Generator (`leerlauf.html`) und Prototyp mit dem Regler der Drehung (`index.html`): *„Leerlauf sieht sehr gut! Index auch. Und ja die Bewegungen sehen sehr gut aus“* — auf die Frage, ob ein Kopf, der im langen Nachdenken 90 % der Zeit mindestens 1° und 70 % mindestens 5° gedreht ist, zu *„Drehung meist klein“* passt. Damit ist die nachgestellte Referenz L0′a–L0′c abgenommen; der Client folgt mit L1′ und L2′.

**Befund:** ein Bild mit Drehung kostet im Browser ohne Grafikkarte rund 0,8 s — die Bildzeit ist das größte Risiko für den Client (L2′). Prüfläufe zeichnen den Kopf deshalb ungedreht. → **Im Client mit Cairo gemessen am 05.10.2026** (L2′b, L2′c unten): bei 600 px in Ruhe 48,6–49,1 ms mit Drehung gegen 27,5–28,0 ms ohne.

**L1′ gebaut, 05.10.2026** — die Leerlauf-Logik des Clients folgt der nachgestellten Referenz L0′a–L0′c (`client/avatar/idle.py`, `idle_catalog.py`, `expression.py`). Bei gleichen Ereignissen, Eingängen und Startwerten plant sie dieselben Zustände, Formen, Blicke, Lidschläge (mit Art, Beginn und geschlossener Phase) und Kopfziele wie der Generator und setzt dieselben Ziele aller 36 Kanäle.

- **Plan:** F9 im Nachdenken ein Akzent von 2–3 s, F5 abgewandt, F16 als seltener Akzent.
- **Antwort:** Die Basis gleitet über A0 in die Emotion, Faktor 0,75; Brauen und Mundwinkel rauschen auch in der Antwort; im Nachklang klingt die Energie aus.
- **Lidschläge:** Abstände nach Gamma(3), ein in der Sperrzeit fälliger wird neu gezogen; am Ende der Antwort genau einer; das Auge ist 40 ms ganz geschlossen; ein neuer setzt am laufenden an.
- **Pupille:** Die Energie weitet sie; Angst und Überraschung verengen sie nicht mehr (`AVATAR-PUPILLE-AROUSAL`).
- **Kopf:** Das Kopfziel ist `IdleFrame.head_yaw` in Grad, mit Wandern, hart auf ±15° — kein Feld von `FaceState` (`novaberg-avatar_t.md` §17.9); keine Emotion dreht den Kopf. `h` je Form kommt aus einer eigenen Quelle (`head_seed(seed)`) und wird auch bei abgeschalteter Drehung gezogen: `IdleLogic(…, head_turn=False)` plant genau gleich, mit dem Ziel 0. Die Feder führt die Puppe (L2′a).
- **Referenz:** `idle.json` (33 Läufe, 36 Kanäle samt `yaw`) und `expression.json` aus der nachgestellten Referenz neu erzeugt.
- **Zeugen:** die Charakterisierung aller 33 Läufe; Prüfpunkte an den Läufen E1, O1–O3, G2, G3, N1, L-4, L-5, L-6 und Y1–Y5, an eigenen Läufen P-2, an der Regel P-1, G1, B5, L-1–L-3 und L-6. **L-6 an der Regel:** Das Modell der Regel (Sperre 800 ms + Gamma(3)) ergibt für 120 s Nachdenken einen Median der längsten Pause von 6,53 s bei der Schranke 7 s, mit einer um 30 % niedrigeren Grundrate des Nachdenkens 8,00 s; an den drei Läufen des langen Nachdenkens sind es 7,70 s (Grenze 10 s). Suite des Avatars `Ran 376 tests` / `OK`.
- **Gegenproben**, je an einer frischen Kopie: (a) Gamma(3) → Exponentialziehung: 33 Läufe rot (vorhergesagt 33); (b) Faktor der Antwort 1,0: 27 (höchstens 30); (c) keine Energie an der Pupille: P-1 und 32 Läufe (praktisch alle 33); (d) tiefes Kopfziel 8° statt 10°: 27, Y1–Y5 grün (wie vorhergesagt); (e) `h` aus dem Zufall des Plans: 33, Y5 grün (wie vorhergesagt); (f) geschlossene Phase 20 ms: 33 Läufe und der Zeuge der Sperrzeiten (wie vorhergesagt); (g) F9 im Nachdenken aus der Dreiecksverteilung: G2 und 3 Läufe (höchstens 23); (h) Grundrate des Nachdenkens −30 %: L-6 an der Regel, die Rate je Zustand und 27 Läufe — vorhergesagt waren mindestens 28. Vermutet, nicht geprüft: Eine im Nachdenken gezogene Lücke wird beim Zustandswechsel mit dem Mittel des neuen Zustands neu gezogen, dort erreicht die geänderte Rate den Lauf nicht.
- **Die Messung steht aus:** ein echter Turn im sichtbaren Fenster mit mindestens 60 s Nachdenken, abgenommen nach §18.1.

**L2′a gebaut, 05.10.2026** — Auge und Kopffeder im Client (`drawing_eye.py`, `animator.py`, `puppet.py`, `pose.py`, `compose.py`).

- **Auge:** Die Iris rückt je Einheit Blick 0,5·hw quer und 0,26·hw längs — ein Blick von 0,25 zur Seite 0,125·hw statt 0,075·hw. Geschlossen gezeichnet wird erst unter der Öffnung 0,06 (`CLOSED_BELOW`, bisher 0,12), mit einer Lidlinie in sieben Strichen von 1,2 bis 5 px und 8 Büscheln zu je 3 Wimpern wie im Prototyp (`novaberg-avatar_t.md` §13.1).
- **Kopffeder:** ω 3,5 (`HEAD_OMEGA`) in der Puppe zum Kopfziel `IdleFrame.head_yaw`, dieselbe Formel wie für die Kanäle (`animator.spring_one`) und derselbe Zeitschritt. Die Pose trägt den Stand als `Pose.head_yaw` in Grad; `check_pose` wirft jenseits von ±15° (`ValueError`) und bei einem Wert, der keine Zahl ist (`TypeError`). Gezeichnet wird der Kopf erst mit L2′b.
- **Gerechnet statt begrenzt:** Die Feder ist kritisch gedämpft und beginnt in Ruhe; der Kopf ist damit ein gewichtetes Mittel der früheren Ziele (Gewichte ≥ 0, Summe < 1) und kann die Spanne der Ziele nicht verlassen. Bei Zielen in ±12° bleiben bis ±15° mindestens 3°, eine Begrenzung in der Puppe ist nicht nötig. **Ungeprüft:** dass die Ziele des Leerlaufs in ±12° liegen (geschätzt: tief bis 11°, dazu Wandern 1°).
- **Zeugen:** Irisweg quer und längs, die gezeichnete Iris am Ort von `iris_center`, geschlossen unter 0,06 mit Zwilling ab 0,06, das geschlossene Auge Strich für Strich gegen den Prototyp (112 Striche); der Kopf der Puppe trifft `kopf` aller 90 Proben des Laufs `lang_neutral` und das Ende seiner Antwort von 20 s auf 1e-3, die Feder bei festem Ziel jeden Schritt auf 1e-9. Suite des Avatars `Ran 389 tests` / `OK`, ganze Client-Suite `Ran 444 tests` / `OK`. Gegenproben rot wie vorhergesagt: Irisweg 0,3, `CLOSED_BELOW` 0,12, Kopffeder ω 5, Kopffeder mit dem ω des Gesichts.

**L2′b gebaut, 05.10.2026** — die Kopfdrehung im Bild (`client/avatar/head_turn.py` neu, `base_image.py`, `compose.py`; `novaberg-avatar_t.md` §13.18).

- **Das Drehgitter des Prototyps,** Rechnung für Rechnung: 24 × 29 Punkte, 1288 Dreiecke, Verdrillung des Halses, Grenze ±15°, Schwelle 0,05°. Über der Schwelle zeichnet `draw_face` das Bild ohne Atem auf eine Zwischenfläche und legt sie als unverzerrte Unterlage auf das Bild, darüber nur die verschobenen Dreiecke; bis 0,05° bleiben die Aufrufe dieselben wie vorher.
- **Die Naht:** radial um 1,6 px vom Schwerpunkt wie im Prototyp, auch in der Kinnverzerrung (bisher je Achse 0,6).
- **Zeugen:** D1 — das Gitter gleich `yaw.json` an allen 696 Punkten und 8 Winkeln auf 1e-9 px; D3 — kein Dreieck klappt um, an 61 Winkeln von −15° bis 15°, Zwilling bei ±30°; D5 — Rand, Schultern und Haar unter dem Kinn stehen, bei 12° wandert die Nase mehr als die Augen, die mehr als die Ohren, die mehr als das Haar, die Nase 26,5–29 px; D6 — 15,01°, `nan` und `inf` werden abgewiesen; dazu der Weg bei 0,05° und 0,06°, nur die verschobenen Dreiecke, radiale Ecken der Clips. Suite des Avatars `Ran 414 tests` / `OK`, ganze Client-Suite `Ran 469 tests` / `OK`. Fünf Gegenproben rot wie vorhergesagt (Nasentiefe 20, Grenze 20°, Naht 0,6, Schwelle 0, alle Dreiecke statt der verschobenen).
- **Gemessen 05.10.2026** mit Cairo auf dem Host, 600 px: das Bild gegen den Prototyp (Sektor 0, Arousal 1,0, Atem 0) mit einer mittleren Abweichung der Grauwerte von 1,17 (0°), 1,77 (−5°), 1,81 (5°) und 1,73 (±12°) von 255. Die Bildzeit (Median, 60 Bilder) ohne Drehung 27,5 ms in Ruhe und 39,0 ms beim Sprechen, mit Drehung 58,4 / 68,2 ms bei 1° und 58,4 / 69,8 ms bei 12°. Durch das Wandern von 1° läuft der gedrehte Weg praktisch immer.

**L2′c gebaut, 05.10.2026** — die Kopfdrehung schneller, das Bild gleich (`head_turn.py`, `base_image.py`).

- **Basis:** Was nur am Gitterpunkt hängt — Tiefe, Kinnanteil, Rand, Lage auf dem Hals —, steht einmal beim Laden in `YAW_BASIS`; je Bild bleibt der Teil mit dem Winkel. Ein Zeuge hält beide Rechnungen an sieben Winkeln über alle 696 Punkte gleich.
- **Geprüft je Gitter:** Ausgang und Eingang des Gitters einmal je Bild statt je Dreieck.
- **`fill` statt `clip` und `paint`, ein Muster je Aufruf:** je verschobenes Dreieck ein Pfad, die Zwischenfläche als Muster mit der Umkehrung der Abbildung als Matrix und ein `fill` — 6 Aufrufe am Kontext statt 10. Die Kinnverzerrung behält ihren Clip.
- Suite des Avatars `Ran 427 tests` / `OK`, ganze Client-Suite `Ran 482 tests` / `OK`.
- **Gemessen 05.10.2026** mit Cairo auf dem Host: Das Bild ist gleich dem von L2′b — mittlere Abweichung 0,000 von 255 bei −12, −5, 0, 1, 5 und 12° (600 px). Die Bildzeit (Median, Drehung 1°):

| Bild | ohne Drehung | mit Drehung, L2′b | mit Drehung, L2′c |
|---|---|---|---|
| 600 px, Ruhe | 27,5–28,0 ms | 58,4 ms | 48,6–49,1 ms |
| 600 px, Sprechen | 39,0 ms | 68,2 ms | 59,3–59,7 ms |
| 409 px (das Panel im Betrieb), Ruhe | 22,6–23,0 ms | — | 36,0–36,5 ms |

- **Das Ziel ist verfehlt:** mit Drehung höchstens ein Drittel mehr als ohne, bei 600 px also ≤ 37 ms in Ruhe und ≤ 52 ms beim Sprechen. Der Rest ist das Rastern der 996 verschobenen Dreiecke in Cairo, rund 12 ms bei 409 px. Ein schnellerer Filter des Musters ändert nichts (47–48 ms) und entfällt; auch das eine Muster je Aufruf brachte messbar nichts. Die weiteren Wege weichen vom Prototyp ab — ein gröberes Gitter, gedrehte Ebenen im Zwischenspeicher, eine Schwelle über 0,05° — und sind beim Eigentümer offen (`AVATAR-DREHUNG-BILDZEIT`).
- ~~**Die Messung im Betrieb steht aus** — für L1′ und L2′ derselbe echte Turn im sichtbaren Fenster mit mindestens 60 s Nachdenken, abgenommen nach §18.1.~~ → **Sichtprüfung im Betrieb bestanden, 05.10.2026, 05:50 UTC.** Der Eigentümer: *„Nachdenken im Client sieht gut aus. Geschwindigkeit ist sauber“*. Damit ist die Bildzeit der Drehung hingenommen (`AVATAR-DREHUNG-BILDZEIT` erledigt). **Nicht gemessen** sind die gezählten Größen nach §18.1: Iris-Abstand F16 ↔ F2, Anteil beim Betrachter im Nachdenken, Lidschläge je Zustand, Mund in E1, `mc` in den ersten 2 s der Antwort.

**L0″ gebaut, 05.10.2026, 14:01 UTC** — der Blickhalt in der Referenz (`novaberg-avatar_k.md` §3). Zieht der Kopf nach, halten die Augen ihren Punkt, und der Blick zur Seite bleibt sichtbar.

- **Plan:** Der Blick des Plans ist die Lage des Auges im Kopf, wenn der Kopf angekommen ist. Das Blickziel `gx` liegt deshalb um das Kopfziel der Regel (ohne Wandern) weiter außen: `x + Kopfziel / 34`, mit 34° Augendrehung je Einheit Blick. Das Kopfziel gilt ab dem Blickwechsel, nicht erst 200 ms später, wenn der Kopf ihm folgt.
- **Zeichnung `geo`**, jetzt ohne Anker: Die Iris steht bei `gx − yaw / 34` und hält so den Punkt.
- **Prüfung:** Y5 vergleicht ohne `gx`. Der neue Prüfpunkt Y7 verlangt `gx = gx(kopf=0) + Kopfziel / 34`, das Kopfziel rekonstruiert aus den Kopfzielen des Laufs. Die letzten 200 ms eines Laufs sind ausgenommen, denn dort steht ein eingereihtes Ziel noch nicht in der Liste. Zwilling: 10 Läufe mit `halt=0`. Ergebnis: `523 Läufe, 0 Verstöße`. Fünf Gegenproben wurden rot wie vorhergesagt: falsches Vorzeichen, das Kopfziel erst bei seiner Geltung, ohne die Bedingung `geo`, ohne die Bedingung Kopf, das Wandern im Ziel. Die Referenz des Ausdrucks hat sich in keinem Wert geändert.
- **Gemessen** an 232 Formen im langen Nachdenken: Am Ende jeder Form steht die Iris im Median 0,35° neben dem Blick des Plans, ohne den Sprung waren es 9,8°.
- **Im Client noch nicht:** `idle.json` wird mit dem Client neu erzeugt. Dazu kommen der Blick im Plan (`idle.py`), `Pose.head_yaw` in `drawing_eye.py` und Y5/Y7 in den Zeugen. Offen ist zuerst die Sichtprüfung des Eigentümers.

### 18.1 Abnahme

Ein Turn gilt als abgenommen, wenn ein Betrachter ohne Bedienung die Phasen erkennt und die Prüfpunkte halten. Übernommen aus der Analyse eines Mitschnitts des Generators (03.10.2026).

**Wahrnehmung — ohne Panelwerte:**

- Nachdenken wird als Denken gelesen, nicht als Staunen oder Abwesenheit.
- Der Wechsel Nachdenken → Antwort ist am Gesicht erkennbar, bevor der erste Laut kommt.
- Die Emotion bleibt während des Sprechens sichtbar.
- Der Nachklang wirkt als Nachhall, nicht als Abbruch.
- Der Übergang ins Rauschen zeigt keinen Sprung.
- **Seit 04.10.2026 (L0′c):** Im Nachdenken wendet Nova den Kopf mit dem Blick etwa 10° zur Seite und mit dem Blick zum Betrachter zurück, sonst bewegt er sich kaum. Der Hals verdrillt sich, die Schultern stehen, keine hellen Nähte.

**Messung — in den Zeugen von L1, im Betrieb an einem Mitschnitt** (seit 04.10.2026 in der Fassung der nachgestellten Referenz L0′a–L0′c, `labor/avatar/leerlauf_pruefen.py`):

- Nachdenken: Blick abgewandt ~~außer bei Denklast (F5, starr geradeaus) und nach einem Einfall (F9, Blick zurück)~~ → **außer nach einem Einfall (F9, ab 1 s) und einem seltenen kurzen Blick zum Betrachter (F16); im langen Nachdenken (120 s) höchstens 12 % der Zeit beim Betrachter**, über alle Läufe der Lage; kein offener Mund (Öffnung über 4) länger als 1 s außer dem Einatmen; Einatmen 0,7–0,9 s, **Mund 7–11**.
- **Antwort:** Die Basis gleitet über A0 (bei A0 ab 1,45 s in 500 ms höchstens 30 % des Wegs); die Öffnung aus dem Leerlauf ≤ 2; in Antworten über 10 s steht kein Ziel der Brauen und Mundwinkel 5 s still.
- Lidschläge: Nachdenken < Rauschen < Antwort bei gleicher Energie; **seit 04.10.2026 dazu Nachklang < Antwort, bei gleicher Energie von Nova und Pixie Nachklang ≤ Rauschen + 10 %**. Keine Doppelschläge, keine Paare im Abstand von genau 0,8 s (höchstens 1 % der Poisson-Lidschläge bei 800–820 ms); am Ende der Antwort ein Lidschlag, danach eine kurze Ruhe — in −0,4 … +4 s um das Ende höchstens in 2 % der Läufe einer Lage 4 und nie 5; beim Einfall genau einer; das Auge ist in jedem Lidschlag mindestens 40 ms ganz geschlossen; im langen Nachdenken liegt der Median der längsten Pause bei höchstens 10 s.
- **Kopf:** Ziel in ±15°; ein Kopfziel gilt 200 ms (zurück 150 ms) nach seinem Blick; am Ende einer Antwort ab 5 s höchstens 0,5° von der Mitte; mit und ohne Kopf derselbe Plan.
- **Pupille:** Erregung weitet sie um 0,12·E; mit Angst und Überraschung 0,9 ist sie im Nachdenken und in der Antwort nie unter 1.
- Nachklang endet an seiner geplanten Dauer.
- Antwort über 5 s: zu Beginn abgewandt, die letzten 1,5 s beim Betrachter.

**Fälle:** kurze Antwort mit positiver Emotion; lange Antwort über 15 s, neutral; negative Emotion mit hohem Arousal; neuer Turn während des Nachklangs; neuer Turn während des Nachdenkens; Pixie-Auftrag während eines Turns und im Rauschen; **langes Nachdenken (120 s)**.

**Nicht in v1:** die Lage im Raum aus dem Server (§17.7); Linien-Zittern und Grafitstriche als sichtbares Rauschen (Skizze in `AVATAR-PIXIE-LEERLAUF`); die Valenz mit Reserve (`AVATAR-VALENZ-RESERVE`).

---

## 13. Figur aus Vorlage (Prototyp, 29.09.2026)

*Teil Bauplan: die Feinabstimmung des Prototyps. Die übrigen Unterabschnitte von §13: Einleitung, 13.1, 13.3, 13.9, 13.12–13.14 in `novaberg-avatar_t.md`; 13.2, 13.4–13.7, 13.15, 13.16 in `novaberg-avatar_m.md`.*

### 13.8 Feinabstimmung nach Sichtprüfung (Meister, 01.10.2026)

- Ärger, Trauer, Enttäuschung nach v0.5: Ärger „wirklich gut“, übrige deutlich besser.
- Überraschung: Augenöffnung `eye_open` 1,35 → 1,215 (10 % weniger, ging zu weit auf).
- Partie unter den Augen: wirkte wie starke Falten. Tränensäcke der Vorlage um 50 %
  aufgehellt (nur Abdunklung gegenüber der umgebenden Haut, weich maskiert),
  gezeichnete Schraffur unter dem Auge
  ebenfalls halbiert. Ganz entfernen ist nicht gewollt: die Partie trägt deutlich
  zur Echtheit der Augen bei.
- Weiße Flecken über den Haaren an beiden äußeren Brauenenden: die Brauenmasken
  (runde Linienenden + weicher Rand) rissen Stücke aus den Strähnen. Behoben mit
  festen Schutzzonen je Strähne, in die weder Maske noch weicher Rand reichen.
  Nebenwirkung: links bleibt ein kurzes Stück des ursprünglichen Brauenendes an
  der Strähne stehen; es bewegt sich nicht mit der gezeichneten Braue mit.
  Die Schutzzonen sind an diese Vorlage gebunden (Koordinaten im Skript).

**Mundwinkel bei Freude (Messung 01.10.2026):** Relativ zur Mundmitte heben sich
die Winkel beim Avatar bereits wie auf den Fotos (Avatar 0,24, Vorlage 0,20,
Fotos 0,20–0,33 der halben Mundbreite). Relativ zu den Augen steigen die Winkel
auf den Fotos aber um ca. 0,12–0,14 Augenabstände gegenüber Neutral (Person 3
und Collage 4; Person 2 0,03–0,12, Kopfneigung stört), beim Avatar nur um 0,06.
→ `mouth_curve` Freude 30 → 40 (Anstieg jetzt ca. 0,08). Weiter nach oben wäre
durch die Messung gedeckt, gewünscht war „ein klein bisschen“.

**Brauen Überraschung vs. Angst (FACS):** Überraschung AU1+2 = ganze Braue hoch
und gewölbt; Angst AU1+2+4 = innen hoch, flach und gespannt. Neuer Kanal
`brow_arch`. Überraschung: Brauen −30/−28, Wölbung −7. Angst: −20/+4, Wölbung +5.

**Brauen bei Freude — bewusst abweichend von FACS (Meister, 01.10.2026):** Beim
Duchenne-Lächeln (AU6 + AU12) senkt sich die Braue außen leicht, innen bleibt sie
neutral. Der Avatar hebt die Brauen bei Freude leicht an (−6). Nach Sichtprüfung
bleibt das so („sieht gut aus“). Nicht umgesetzt: Krähenfüße am äußeren
Augenwinkel als abgeleitetes Merkmal — bei Bedarf wie die Zornesfalten aus
`eye_arc` ableitbar.

### 13.10 Brauen und Wimpern näher am Original (01.10.2026)

Hinweis Meister: Brauen im Original fülliger, Wimpern betonen die Augen intensiver.
- Brauen: statt paralleler Haarstriche eine weiche, gefüllte Fläche in drei
  Deckkraftstufen, innen voll, am Scheitel am breitesten, Ende spitz auslaufend;
  darüber 190 feine Haarstriche in Wuchsrichtung (innen steiler). Breite 12/14 → 16/18.
- Wimpern: dunkler, nach außen breiterer Wimpernkranz mit kurzem Schwung über den
  äußeren Augenwinkel; statt 28 dünner Striche 18 kräftige, gebogene, sich
  verjüngende Wimpern, paarweise gebüschelt, nach außen länger.
- Unterwimpern: weniger, unregelmäßig, nur äußere Hälfte deutlich.

- Korrektur Wimpernschwung (Hinweis Meister): Spitzen hingen nach unten. Jetzt
  Bogen symmetrisch um die Wimpernrichtung, Start flacher nach außen, Spitze nach
  oben gebogen; Biegung innen fast null, außen stark (k = 0,08 … 0,40 rad).
- Schattierung außen (Hinweis Meister: im Original außen eine Spur dunkler):
  Augenweiß mit Verlauf zum äußeren Winkel (bis 55 % Grafit-Deckkraft), weicher
  Schatten um den äußeren Augenwinkel, neun zusätzliche kurze Wimpern im äußeren
  Drittel, die zu einer dunklen Masse verschmelzen.
- Unterwimpern kräftiger (Hinweis Meister): 11 Wimpern, nach außen länger und
  dichter, leicht gebogen, Lidkante außen dunkler.
- Fehler behoben: Das Auslassen einzelner Unterwimpern hing am Zufallsgenerator,
  der für das Linien-Zittern ca. 9× pro Sekunde neu gesetzt wird → Unterwimpern
  flackerten. Jetzt festes Auslassmuster. Regel für den Client: Der Zufall des
  Linien-Zitterns darf nur Strichlagen verwackeln, nie über Sichtbarkeit oder
  Anzahl von Elementen entscheiden.
- Grafitschatten an den Augenrändern nach Markierung Meister: rauchige Fläche um
  den äußeren Augenwinkel (Verlauf + 46 Schraffurstriche) und dunkles Band unter
  dem Unterlid in der äußeren Hälfte (4 Lagen + 30 Striche). Kalibriert per
  Helligkeitsmessung gegen das Original (Grauwert 0–255):
  äußerer Winkel 114 / Avatar 119, unter dem Lid 156 / 147.
- Iris dunkler und gemasert: 110 dunkle radiale Fasern, 40 helle Zwischenstreifen,
  8 Krypten, Krausenring um die Pupille, dunklerer Limbusring. Grauwert Iris
  Original 64 / Avatar 82 (vorher heller).
- Feste Positionen über eine Hash-Funktion statt Zufall (Regel aus der
  Unterwimpern-Korrektur): Fasern und Schraffuren verwackeln, springen aber nicht.
- Lidfalte näher am Lid (Hinweis Meister 02.10.2026): Abstand Falte–Oberlid im
  Original ca. 12 px, im Avatar vorher ca. 18–25 px. Falte jetzt als Versatz des
  Oberlids (`CREASE_GAP` 14 px Mitte, zu den Winkeln auslaufend, schwere Lider
  −4 px) statt eigener Kurve; nach den Wimpern gezeichnet, damit die Wimpern sie
  kreuzen und sie sichtbar bleibt (bei 10 px verschwand sie im Wimpernkranz).
- Wimpern verklebt (Hinweis Meister 02.10.2026): statt 18 Einzelwimpern 11 Büschel
  aus je 3 Wimpern mit getrennten Wurzeln, die zur gemeinsamen Spitze zusammenlaufen;
  an der Wurzel kräftig, Spitze dünn. Längen und Lage fest über Hash. Äußere
  Verdichtung von 9 auf 5 kräftigere Wimpern reduziert. Ein erster Versuch mit
  breiteren Strichen wirkte wie Wimperntusche-Zacken und wurde verschlankt.
- Zur Nase hin feiner (Hinweis Meister 02.10.2026): Wimpernbüschel beginnen erst bei
  27 % der Lidlänge (vorher 14 %), Strichstärke innen halbiert und nach außen
  ansteigend, innerstes Büschel kürzer. Wimpernkranz innen nur eine feine Linie,
  kräftige Lagen erst ab dem ersten Fünftel.
- Unterwimpern außen länger (Hinweis Meister 02.10.2026): Länge 4 → 18 px von innen
  nach außen (vorher 4 → 13), stärker zum Augenwinkel hin ansteigend; Länge fest
  über Hash statt Zufall.
- Obere Wimpern innen 10 % weniger (11 → 10 Büschel, Beginn bei 34 % statt 27 %),
  außen kräftiger: dunkler keilförmiger Wimpernrand ab 35 % der Lidlänge, zum
  äußeren Winkel bis ca. 6 px breit (Hinweis Meister 02.10.2026). Fehler beim
  ersten Entwurf: zwei getrennte Teilpfade schlossen sich quer über das Auge;
  jetzt ein zusammenhängender Pfad.
- Lidfalte parallel zur Lidlinie (Hinweis Meister 02.10.2026): Abstandsprofil
  sin^0,25 statt sin^0,8, d. h. über fast die ganze Länge gleicher Abstand, nur an
  den Enden kurz auslaufend. Darunter drei weiche Schattenlagen zum Lid hin,
  Faltenlinie etwas dunkler.

### 13.11 Mund ans Original angeglichen (02.10.2026)

- Zähne: Schneidezähne breiter (27/21/18 px statt 22/17/15), Kanten runder,
  deutlich weißer (Ton 250 statt 238), schwächerer Wurzelschatten, dunkle Fugen
  zwischen den Zähnen, schwächerer Lippenschatten auf den Zähnen.
- Mundraum dunkler, Zunge größer und heller mit Mittellinie und Struktur
  (sichtbar erst bei größerer Öffnung, z. B. Schreien, Weinen).
- Lippen: senkrechte Rillen ersetzt durch feine Schraffur entlang der Lippe
  (130 Striche je Lippe, feste Positionen), zur Mundlinie und zu den Winkeln
  dunkler; Grundton kräftiger; Konturen dunkler; Unterlippe zur Unterkante hin
  dunkler, weiches Glanzlicht in der Mitte.
- Mundwinkel als tief dunkle Keile.
- Offen: Die Öffnung bei Freude bleibt bei den gemessenen Werten (13.7) und ist
  damit kleiner als in der lachenden Vorlage.
- Verhältnis Ober- zu Unterlippe (Hinweis Meister 02.10.2026): Oberlippe
  19 − 0,12 · `mouth_curve` (wird beim Lächeln gestreckt und dünner), Unterlippe
  23 − 0,03 · `mouth_curve`. Mitte neutral ca. 1 : 1,7, bei Freude ca. 1 : 2,1
  (Original lachend ca. 1 : 2; Fotos neutral 1 : 1,3–1,6).
- Unterlippe voller (Hinweis Meister 02.10.2026): Grunddicke 23 → 28.
- Zahnform mit Bögen am Zahnfleischrand (Hinweis Meister): jeder Zahn oben eigener
  Bogen, dazwischen kleine dunkle Zwickel; Ecken an der Schneidekante gerundet,
  Schneidekante leicht gewölbt. Zahnfleischrand 9 px tiefer, Zahnhöhen angepasst.
  Erster Versuch mit tiefen Zwickeln und großen Radien sah aus wie Kiesel und
  wurde verworfen.
- Beim Lächeln hebt sich die Oberlippe (AU10/AU12: Kontrollpunkt −0,3 · `mouth_curve`
  bei offenem Mund) und legt die Zahnbögen frei; bei negativer Mundkrümmung
  (Wut, Trauer, Angst) keine Änderung.
- Zahnfleisch heller (Hinweis Meister 02.10.2026): eigenes Band entlang des
  oberen Zahnbogens (Grauwert ca. 118 → 182 zum Zahnrand hin) statt des dunklen
  Mundraums hinter den Zahnbögen.
- Zahngrößen einzeln nach Original (Hinweis Meister 02.10.2026: zu gleichmäßig).
  Gemessen (Vorlagen-Pixel, Breite / sichtbare Höhe): mittlere Schneidezähne
  26–31 / ca. 35, seitliche 17–21 / ca. 22, Eckzähne 15–17 / ca. 17, Backenzähne
  13–15 / 13 → 10. Avatar oben jetzt 28/31, 19/23, 16/22, 14/16, 13/13, 12/11, 11/9;
  Eckzahn leicht spitz; feste Abweichung je Zahn und Seite (±4 % Breite, ±5 % Höhe),
  da echte Zähne nicht spiegelgleich sind.
- Mittlere Schneidezähne 4 px kürzer (31 → 27) nach Sichtprüfung Meister.
- Untere Zahnreihe als Gegenstück zur oberen (Hinweis Meister 02.10.2026: zu breit
  in der Bissbreite, Zähne zu schmal, nicht dem Kiefer nachgebogen):
  - Zähne auf einem Kreisbogen (Radius 85 px), von vorn projiziert: zur Seite
    perspektivisch schmaler, Reihe insgesamt schmaler als die obere.
  - Kanten steigen zu den Seiten leicht an (0,18 · Bogenhöhe); erster Versuch mit
    0,4 ließ die Seitenzähne hochklettern.
  - Zähne breiter (17–18 px vorn) und länger, damit sie hinter der Unterlippe
    nicht abreißen; untere Schneidekanten gerade statt gerundet (gerundet wirkten
    sie wie eine Pillenreihe).
  - Bei negativer Mundkrümmung und offenem Mund zieht die Unterlippe nach unten
    (AU15/AU16) und legt die untere Reihe frei (Weinen).
- Korrektur Weinmund (Hinweis Meister 02.10.2026: unten kein breites Aufziehen
  ohne Hilfsmittel möglich). Zug der Unterlippe von 0,9 auf 0,25 · |`mouth_curve`|
  reduziert; Trauer intensiv `mo` 34 → 28, `mw` 106 → 96. Untere Zähne nur noch
  als schmaler Streifen hinter der Unterlippe sichtbar. Anatomie: AU16 senkt die
  Unterlippe nur begrenzt; AU12 (oben) hat deutlich mehr Hub.
- Fleischiges Polster an den Mundwinkeln (Hinweis Meister 02.10.2026): Die dunkle
  Öffnung lief spitz bis in den Lippenwinkel und zeigte seitlich zu viel Zähne.
  Jetzt endet sie um 12 + 0,35 · `mouth_open` px (max. 30 % der halben Mundbreite)
  vor dem Winkel, mit gerundeten Ecken; dazwischen eine schattierte Lippenfläche
  und eine kurze Falte vom Lippenwinkel ins Polster.
- Polster-Schattierung korrigiert (Hinweis Meister: heller Ring innen, dunkle Lippen
  außen wirkte unnatürlich): Verlauf jetzt vom Lippenton am Winkel zur Öffnung hin
  dunkler (Schatten in den Mund), Schraffur wie auf den Lippen; dunkle Striche an
  den Lippenwinkeln nur noch bei geschlossenem Mund.
- Polster heller an die Lippen angeglichen (Grauwert 196 → 150 zur Öffnung statt 150 → 92), Schraffur schwächer (Hinweis Meister 02.10.2026).
- Angst: Augenöffnung `eye_open` 1,30 → 1,12 (Hinweis Meister 02.10.2026). Erster Schritt auf 1,21
  (7 % des Werts) änderte die Lidhöhe nur um ca. 2 px und war nicht sichtbar; der
  Eindruck „aufgerissen“ hängt am Weiß über der Iris, nicht an der Gesamthöhe.
- Lachfalten 14 px tiefer (Hinweis Meister 02.10.2026).
