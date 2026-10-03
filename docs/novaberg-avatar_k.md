# Novaberg — Emotions-Avatar (Konzept)

**Absicht:** Ein 2D-Avatar im GTK4-Client zeigt Novas eigenen Emotionszustand als lebende Bleistiftskizze; er stellt dar, was die Emotionsberechnung liefert, und entscheidet selbst nichts.
**Stand:** 03.10.2026 (§3 neu: die Denkweisen im Leerlauf). Davor 02.10.2026
**Umsetzung:** ~~keine Featurezeile — sie entsteht, wenn Novaberg das Feature bekommt (Entscheidung vom 02.10.2026, `novaberg-avatar_e.md`). Im Client ist nichts gebaut; ein HTML-Prototyp liegt unter `labor/avatar/` (§13).~~ → **seit 03.10.2026 gebaut** und im Client gesehen (`novaberg-avatar_b.md` §16, Featurezeile *Avatar-Panel*); der Prototyp unter `labor/avatar/` bleibt die Referenz.
**Teile:** `novaberg-avatar_t.md` · `novaberg-avatar_b.md` · `novaberg-avatar_e.md` · `novaberg-avatar_m.md`
**Grundlagen:** `novaberg-ei-plutchik.md`, `novaberg-ei-dual-emotion_k.md`
**Entschieden:** 10 · **Offen beim Meister:** 8 (Liste in `novaberg-avatar_e.md`)

> Alle Bezeichner für **neue** Bausteine (Klassen, Felder, Funktionen) sind **Vorschläge**.
> Aussagen über das **bestehende** System stammen aus den oben genannten Dokumenten,
> nicht aus dem Code. Sie gelten als Doku-Stand, bis ein Audit sie belegt (Abschnitt 11).
>
> → **Am Code belegt am 02.10.2026:** O1–O5 und O9 (`novaberg-avatar_e.md` §11), der Datenvertrag in `novaberg-avatar_t.md` §14.

---

## § → Datei

| § | Abschnitt | Datei |
|---|---|---|
| 1, 2 | Ziel, Leitprinzip | `novaberg-avatar_k.md` |
| 3–9 | Darstellungsstil, Parameterraum, Emotions-Mapping, Intensität und Mischung, Übergangsmodell, Schichtenmodell, Integration im GTK4-Client | `novaberg-avatar_t.md` |
| 10 | Testbarkeit | `novaberg-avatar_b.md` |
| 14, 15 | Datenvertrag mit dem Server, Portierung nach GTK4 und Cairo | `novaberg-avatar_t.md` |
| 16 | Bauteile für den Client (B1–B8) | `novaberg-avatar_b.md` |
| 11, 12 | Offene Punkte, Annahmen | `novaberg-avatar_e.md` |
| 13 (Einleitung), 13.1, 13.3, 13.9, 13.12–13.14 | Figur aus Vorlage: Pipeline, Alternative, bewegliches Kinn, Sprechschicht, Muskelkanäle, Einzellaute | `novaberg-avatar_t.md` |
| 13.8, 13.10, 13.11 | Feinabstimmung des Prototyps nach Sichtprüfung | `novaberg-avatar_b.md` |
| 13.2, 13.4–13.7, 13.15, 13.16 | Befunde und Messungen | `novaberg-avatar_m.md` |
| — | Änderungen der Fassungen 0.1 bis 0.5, Entscheidungen, Befunde der Aufteilung, Abweichungen Prototyp ↔ Konzept | `novaberg-avatar_e.md` |

---

## 1. Ziel

Ein 2D-Avatar im GTK4-Client, der **Novas** aktuellen Emotionszustand sichtbar macht.

- Stil: Bleistiftskizze, bewusst stilisiert, kein Fotorealismus.
- Dauerhaft animiert: Das Bild „lebt“ auch ohne Zustandsänderung.
- Emotionswechsel laufen als flüssiger Übergang in etwa 1 Sekunde,
  von jedem Zustand zu jedem anderen, auch mitten in einem laufenden Übergang.

**Nicht Ziel (v1):** Fotorealismus, 3D, generative Bild- oder Videomodelle,
eigenständige Interpretation von Emotionen durch den Avatar, Darstellung der
User-Emotion (das bleibt Aufgabe des Emotions-Radars).

---

## 2. Leitprinzip: Der Avatar ist ein reiner Renderer

Analog zu „LLM als Sprach-Renderer“: Der Avatar entscheidet nichts.

- Die Emotion wird deterministisch in Python berechnet (EI-Calc, Rolle `character`).
- Der Avatar erhält einen **Ziel-Emotionszustand** und stellt ihn dar.
- Der Avatar kennt keine Gesprächsinhalte, leitet keine Emotionen ab und
  normalisiert nicht erneut.
- **Er ist eine Puppe, an der Fäden gezogen werden** (Entscheidung vom 02.10.2026, `novaberg-avatar_e.md`):
  Entschieden wird vorher, in der Emotionsberechnung, im Verfasser und im Responder; der Avatar
  bekommt die Fäden — Emotion und Arousal, beim Sprechen die Laute — und nimmt die Stellung ein.

| Baustein | Verantwortung | Kennt Emotionen? |
|---|---|---|
| Mapping | Emotionszustand → Gesichtsparameter | ja |
| Animator | Übergang zwischen Gesichtsparametern über die Zeit | nein |
| Renderer | Gesichtsparameter → Zeichnung in einem Rechteck | nein |

---

## 3. Die Denkweisen: Rauschen, Nachdenken, Antwort, Nachklang

**Absicht des Meisters, 03.10.2026**, wörtlich: *„Wenn Nova keinen Prompt hat, haben wir einen Leerlauf, in dem normalerweise Pixie arbeiten sollte. Gibt man einen Prompt ein, beginnt Nova mit der aktuellen Emotion nachzudenken für die Dauer des Turn, das ist konvergentes Denken. Dies können wir für die Dauer des Turns darstellen. Danach kommt die Widergabe der Antwort, die Interaktion mit dem Nutzer. Danach und ein paar Sekunden später — evtl 1 Minute — wird sie wieder in ein Rauschen verfallen, das divergente Denken. Wenn Pixie denkt (divergent), hat sie einen Auftrag, dieser hat Emotionen. Mit diesen geht sie an einen Auftrag heran, der dann wieder zu einem Turn führt, wenn er in den Charakter-Graph eingespeist wird (konvergent). Wir wechseln hier die Denkweisen, während sie nicht in Turns mit dem User beschäftigt ist. Diese konvergenten Turns und die divergenten Pixie-Phasen können wir darstellen. Wir haben Emotionen an jedem Punkt. Wir müssen nur eine angebrachte Form von Leerlauf-Animationen einfügen mit entsprechender Ruhe, Zeiten, Pausen, Zufall, etc.. […] Zufall, aber geformt. Und das ist das wichtigste! Es muss stimmig sein, aber aus der Gruppe der dann möglichen Mimiken können wir zufällig eine Abhandlung aufbauen.“*

| Zustand | Wann | Denkweise | Emotion aus |
|---|---|---|---|
| **Rauschen** | kein Turn; Pixie arbeitet an einem Auftrag | divergent | Pixies Auftrag |
| **Nachdenken** | vom Prompt bis zur Antwort — auch, wenn ein Auftrag Pixies als Impuls in den CharacterGraph geht | konvergent | Nova im Turn |
| **Antwort** | die Wiedergabe, lippensynchron | — | die Antwort (`nova_emotion`, `nova_arousal`) |
| **Nachklang** | einige Sekunden bis etwa eine Minute nach der Antwort, dann zurück ins Rauschen | Übergang | ausklingend |

**Das Leitprinzip bleibt (§2):** Der Avatar entscheidet nichts — er bekommt je Zustand die Emotion und spielt aus einer Gruppe stimmiger Mimiken eine Abfolge. **Zufall, aber geformt:** Welche Mimiken zu einem Zustand und einer Emotion gehören, wie lange eine steht, welche auf welche folgen darf und wie lang die Pausen sind, ist festgelegt; welche davon gerade kommt, entscheidet der Zufall.

**Grundlage:** die Recherche `labor/avatar/recherche_mimik_leerlauf.md` (03.10.2026: Verhaltensweisen beim Denken mit Belegstärke, Zeitwerte, Leerlauf virtueller Agenten, Zuordnung zum Novaberg-Raum, Entwurf eines Generators). **Was der Client heute bekommt:** `character_stage` während eines Turns (Beginn und Fortschritt des Nachdenkens, ohne Emotion als Feld) und die Antwort mit `nova_emotion`/`nova_arousal`; **nicht:** Pixies Phase und die Emotion ihres Auftrags. **Backlog:** `AVATAR-PIXIE-LEERLAUF` (`novaberg-backlog-antwortpfad.md`).

**Entschieden vom Meister, 03.10.2026:**

- **Pixies Start als Ereignis, nur als Rückfall:** *„der Start Pixies mit Auftrag und Emotion kann als Ereignis an den Client geschickt werden, darf aber konvergentes Denken in Turns und die User-Interaktion nicht stören, sondern nur den Fallback setzen und — wenn Nova bereits im Leerlauf ist — auf die Änderung des Fallbacks hinweisen. Das müssen wir am Server ändern.“* → Backlog `PIXIE-START-ALS-EREIGNIS` (`novaberg-backlog-hintergrund.md`).
- **Blinzeln bei Ärger wie bei Freude:** *„Die Blinzelrate: Ärger wie Freude. Ärger kann auch ruhig ablaufen und hat keine Beschleunigung der Frequenz automatisch im Beiklang.“* Die Emotion allein beschleunigt das Blinzeln nicht; die Recherche fand für Ärger ohnehin keine Messung.

