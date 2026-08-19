# Novaberg — NMCP: wie ein Dienst sich anmeldet und was ihn erreicht

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Convention — Anmeldung, Zustellung, Zustandsübergabe und Rückgabe eines Fachdienstes
**Stand:** 17. August 2026 (v0.1, Erstfassung)
**Pfad:** novaberg/docs/novaberg-convention-nmcp.md
**Typ:** Convention
**Voraussetzung:** `novaberg-convention-planner-needs.md` §3 (das Clipboard-Prinzip) · §3.7a (die Sprachrichtung der Selbstauskunft)
**Verwandt:** `novaberg-agent-fachabteilung_k.md` (die Pipeline als Vision) · `novaberg-pattern-domain-language.md` (die Normalisierung) · `novaberg-pattern-crud-hardening.md` (die deterministische Bearbeitung)

---

> ## Zustandsteil — ausdrücklich getrennt vom Regelteil
>
> ~~**Von dieser Konvention ist am 17.08.2026 nichts gebaut.** Kein `NMCP`-Bezeichner existiert im Code, kein Handshake läuft, kein Dienst meldet einen Bedarf an, und der vierte Ausgang fehlt im Ergebnistyp.~~
>
> **Widerlegt am 18.08.2026, und der Satz stand über den Tag hinaus, an dem er wahr war.** Gemessen am Startlog: `NMCP-Handshake: 15 geprueft, 15 eingebunden, 0 verweigert, 10 ohne Zweifelsfaelle`. **Am 18.08.2026 abends: 17 geprueft, 17 eingebunden, 0 verweigert, 11 ohne Zweifelsfaelle** — zwei Dienste des Dateien-Verbunds sind hinzugekommen, und der Katalog der Zusagen ist zum ersten Mal **wegen** eines Bedarfs gewachsen: `such_vektor`, angemeldet vom lesenden Dienst, damit derselbe Turn nicht zweimal eingebettet wird. Im Code stehen `agents/nmcp.py` mit `anmelden()` und `gesamtbild_pruefen()`, `Bedarf` und `Zusage` in `agents/base.py`, und `AgentResult` trägt `korrektur` samt Pflichtprüfung im `__post_init__`. Fünf Dienste bedienen den vierten Ausgang.
>
> **Der Zustandskasten ist damit selbst ein Beleg für seine eigene Warnung.** Er wurde geschrieben, um zu verhindern, dass ein Bezeichner als vorhanden gelesen wird, bevor er existiert — und ist in die andere Richtung veraltet: Er behauptet Abwesenheit, wo längst Code steht. **Eine Zustandsaussage altert in beide Richtungen**, und ein Kasten, der nur vor der einen warnt, hat die andere nicht im Blick.
>
> **Neu am 18.08.2026:** `dateien_wurzeln` ist der **erste Dienst, dessen Anmeldung vor seinem Code stand**. Damit ist §3.4 einmal beim Entwerfen erprobt statt beim Nachtragen.
>
> Was existiert, sind ihre **Bestandteile in verstreuter Form**: die Aushänge der Manager samt Aggregator und Modellaufruf, drei Clipboards im Zustandstyp, die neunfache Deklarationsfläche der Agenten (davon fünf Felder ohne Leser), die Normalisierung im Klassifikationsschritt, und die deterministische Bearbeitung.
>
> **Diese Konvention setzt das Soll für einen Mechanismus, der noch nicht steht.** Das ist zulässig und in einem Punkt gefährlich: Genau so entstand `AgentInput` — ein Bezeichner, der vier Monate in einer Konvention stand und **nie existiert hat**. Deshalb trägt jeder Satz unten seine Sorte, und der Bestand steht nur in §9.
>
> **Kein Bezeichner dieses Dokuments darf als vorhanden gelesen werden, bevor er in §9 mit Datum als gebaut geführt ist.**

---

## 1. Warum dieses Dokument

Novaberg bindet Fachdienste an. Heute sind das eigene Agenten; morgen können es fremde sein. Die Frage ist in beiden Fällen dieselbe und in beiden Fällen ungelöst:

> **Woran erkennt der Empfang, dass er einen Dienst braucht — und was von dem, was er weiß, erreicht diesen Dienst?**

Das etablierte Protokoll für fremde Dienste (Model Context Protocol, geprüft gegen Revision `2026-07-28`) beantwortet die erste Frage ausdrücklich **nicht**: Werkzeuge sind *model-controlled*, und im Ablaufdiagramm der Spezifikation steht zwischen Auflistung und Aufruf ein Abschnitt *Tool Selection* ohne eine einzige Protokollnachricht. Die zweite Frage beantwortet es zur Hälfte — es überträgt Signatur und Beschreibung, aber weder Kosten noch Kadenz, weder Geltungsbereich noch Datenhoheit noch Vorbedingungen.

**NMCP ist der Name für die andere Hälfte.** Nicht ein Ersatz des Transports, sondern die Menge der Angaben und Regeln, die eine Anmeldung tragen muss, damit ein Aufrufer wählen und ein Dienst arbeiten kann.

**Der Name bedeutet Novaberg-MCP-Server.** Ein NMCP-Dienst kann ein Agent im eigenen Prozess sein oder ein fremder Dienst hinter einem Transport; die Regeln unterscheiden nicht danach, sondern nur dort, wo der Unterschied zählt — bei der Frage, ob eine Angabe erzwungen oder nur behauptet ist (§7).

---

## 2. Die Regel in einem Satz

> **Ein Dienst meldet in der Sprache des Empfangs an, woran er erkannt wird und was er dafür braucht; der Empfang sagt ihm verbindlich, wo das Gebrauchte liegt, und stellt im Zweifel zu. Der Dienst erhält, was er angemeldet hat — nicht, was vorhanden ist — und antwortet auf einem von vier Wegen, deren vierter einen Korrekturvorschlag trägt.**

Vier Teile, und jeder hat seinen eigenen Abschnitt: der Aushang (§3), die Zustellung im Zweifel (§4), der Handshake über den Zustand (§5), die Pipeline und die vier Ausgänge (§6).

---

## 3. Der Aushang — die Anmeldung ist in der Sprache des Empfangs

### 3.1 Die Regel

> **Ein Dienst meldet an, woran der Empfang erkennt, dass er ihn braucht — in der Sprache des Empfangs, mit Negativfällen. Eine Fähigkeitenliste ist keine Anmeldung.**

Das ist die bestehende Regel aus `novaberg-convention-planner-needs.md` §3.7a, hier um zwei Bedingungen geschärft, die erst beim Anbinden fremder Dienste sichtbar werden.

### 3.2 Die Sprachbedingung, und sie ist schärfer als „nicht die Anbietersprache"

Der Aushang darf **die Fachsprache des Dienstes nicht benutzen.** Nicht `termin_erstellen`, nicht `entity_resolve`, nicht `charakter_update` — und auch nicht deren ausgeschriebene Formen.

Der Grund ist keine Stilfrage. **Der Empfang kennt die Fachsprache keiner Abteilung, und er darf sie nicht kennen** — sonst ist er wieder die zentrale Zuordnungstabelle, gegen die die ganze Bauart gerichtet ist. Ein Aushang in Fachsprache verlangt vom Empfang eine Übersetzungsleistung, die er nur erbringen kann, wenn er das Fachgebiet versteht.

Der Aushang benennt deshalb **Merkmale der Äußerung**, nicht Operationen des Dienstes:

```
ERKENNUNG:
Entscheidend ist NICHT die Satzform, sondern ob die Äußerung
<beobachtbares Merkmal> enthält.
  - Imperativ:  "..."
  - Frage:      "..."
  - Beiläufig:  "..."

NICHT triggern bei:
  - <Fall, der oberflächlich passt und nicht hierher gehört>
  - <Fall, der zu einem Nachbardienst gehört>
```

**Die Negativfälle sind Pflicht, nicht Kür.** Eine Fähigkeitsgrenze sagt, wo das Können endet; ein Negativfall sagt, **wen der Dienst ausdrücklich nicht haben will, obwohl er zu passen scheint.** Fehlrouting scheitert fast nie an fehlender Fähigkeit, sondern an oberflächlicher Ähnlichkeit — der Negativfall ist die einzige Angabe, die dagegen wirkt.

### 3.3 Die Einsammelbedingung

**Ein Aushang gilt je Dienst, nicht je Anbieter, und er wird über alle Dienste eingesammelt und in jedem Durchlauf gelesen.**

Alle drei Teile sind notwendig, und alle drei fehlen im etablierten Protokoll: Dort gibt es einen Platz für natürlichsprachige Anleitung, aber **je Server** statt je Dienst, ohne vorgesehene Zusammenführung mehrerer Anbieter, und das Abrufen ist für den Aufrufer optional.

Ein Aushang, der nicht eingesammelt wird, ist eine Deklaration ohne Leser — und die verrottet unbemerkt (§8.2).

### 3.4 Die übrigen Angaben

Der Aushang ist die einzige Pflichtangabe für die **Auswahl**. Für den Betrieb kommen neun weitere hinzu, und sie beantworten je eine Frage des Aufrufers:

| Angabe | Frage des Aufrufers | Rang |
|---|---|---|
| **Aushang** | Woran erkenne ich, dass ich dich brauche? | Pflicht |
| **Negativfälle** | Wen schicke ich dir ausdrücklich nicht? | Pflicht |
| **Fähigkeit** | Was tust du, wenn ich dich rufe? | Ergänzung — **nie Auswahlkriterium** |
| **Grenze** | Was tust du ausdrücklich nicht? | Pflicht |
| **Kosten** | Was kostet mich der Aufruf — Zeit, Modell, Spur? | Pflicht, **erzwungen** (§3.5) |
| **Kadenz** | Läufst du auch ohne mich? | Pflicht |
| **Geltungsbereich** | Wo darfst du laufen? | Pflicht |
| **Datenhoheit** | Wessen Daten rührst du an? | Pflicht |
| **Bedarf** | Welchen Zustand brauchst du? | Pflicht, **verhandelt** (§5) |
| **Quote** | In welchem Anteil der Äußerungen kommst du vor? | Pflicht, **abgeglichen** (§4.4) |
| **Wiederholverhalten** | Was tut der zweite Aufruf mit demselben Auftrag? | Pflicht |

**Die Fähigkeitenliste bleibt zulässig und wird nie zur Auswahl gelesen.** Sie ist eine Auskunft für Menschen und für die Anzeige. Wer sie zum Auswahlkriterium macht, baut den Kanal, der im eigenen Bestand vier Monate lang keinen Leser gefunden hat.

### 3.5 Warum die Kostenangabe erzwungen gehört

**Zwei Lasten behindern sich.** Wer das Sprachmodell braucht, hält es minutenlang; wer nur rechnet und einbettet, ist in Sekunden fertig. In einer gemeinsamen Schlange verhungert der Schnelle hinter dem Langsamen.

Daraus zwei Regeln, die über die Spurtrennung hinausreichen:

**Die Vorgabe ist die langsame Spur.** Ein Dienst, den niemand eingeordnet hat, landet dort, wo Blockieren erwartet ist und nichts schadet. Die umgekehrte Vorgabe wäre die gefährliche: Ein übersehener Modellaufrufer verstopfte die schnelle Spur und erzeugte genau den Defekt, gegen den die Trennung gebaut ist.

**Die Angabe wird geprüft, nicht geglaubt.** Ein Dienst der Rechenspur, der doch das Sprachmodell ruft, scheitert laut. Der Grund steht in der Messung, die zur Trennung führte: Beim ersten Einordnen wurde ein Agent fälschlich für modellfrei gehalten, **weil sein Modellaufruf ein Modul tiefer stand.** Die Lastart ist eine Eigenschaft des ganzen Aufrufbaums, nicht der Klasse — und deshalb keine Angabe, die man auf Zuruf glauben darf.

---

### 3.6 Das schwarze Brett — jeder Zettel wird für sich beurteilt

**Das Bild, das die Bauart am genauesten trifft:** Die Aushänge hängen an einem schwarzen Brett. Der Empfang nimmt bei jeder Äußerung das ganze Brett zur Hand, liest **Zettel für Zettel** und entscheidet je Zettel: aufrufen oder nicht.

> **Der Empfang beurteilt keinen Zettel im Verhältnis zu einem anderen.** Er darf es nicht, und er hat die Grundlage dafür nicht. Ein Zettel ist von seinem Autor für einen Leser geschrieben, der die anderen Zettel nicht kennt — und dass er sie nicht kennen muss, ist der Kern des Plugin-Prinzips.

Vier Folgen, und jede ist eine Abweichung von dem, was Routing üblicherweise tut:

**Kein Vergleich, keine Rangliste, kein bester Treffer.** Der Empfang wählt nicht den passendsten Dienst aus, sondern **jeden, dessen Zettel anspricht**. Sobald er zwei Zettel gegeneinander abwägt, braucht er Wissen über deren Verhältnis — und dieses Wissen läge nirgends außer in ihm selbst. Damit wäre er wieder die zentrale Zuordnung, gegen die die ganze Bauart gerichtet ist.

**Mehrere Zusagen sind der Normalfall, nicht der Konflikt.** Zwei Dienste dürfen dieselbe Äußerung beanspruchen; dann wird an beide zugestellt. Deshalb darf die Summe aller Quoten über 100 % liegen (§5.6) — sie ist keine Aufteilung, sondern eine Menge von Ansprüchen.

**Eine echte Doppelung wird am Zettel aufgelöst — und zwar über die Äußerung, nicht über den Nachbarn.** Der Zettel wird geschärft: Er beschreibt genauer, welche Äußerungen der Dienst *nicht* will. Ein Negativfall nennt eine **Eigenschaft der Äußerung** (*„das ist Feedback, kein Charakter"*) und **niemals einen anderen Dienst**.

#### 3.6b Kein Zettel darf einen anderen Dienst ausschließen

**Zwei Gründe, und der zweite ist der schwerere.**

**Ein Dienst kann seinen Nachbarn nicht kennen.** Woher sollte ein Plugin von der Existenz eines anderen Plugins wissen? Es weiß es nicht, es soll es nicht wissen, und dass es es nicht muss, *ist* das Plugin-Prinzip. Ein Negativfall, der einen Dienst benennt, setzt Wissen voraus, das der Anmeldende nicht haben kann.

**Und selbst wenn er es hätte, wäre das Ausschlussrecht Gift.** Ein Zettel mit dem Satz *„wenn es mich betrifft, rufe keinen anderen"* erzeugt genau die Fehlerklasse, gegen die diese Konvention gebaut ist:

> **Ein Ausschluss verwandelt eine Fehlzustellung in eine ausgebliebene Zustellung.** Im Fehlerfall — wenn der ausschließende Dienst gar nicht der Richtige war — hätte er den **korrekten** Dienst mit ausgeschlossen. Aus dem billigen, sichtbaren Fehler (eine überflüssige Zustellung, die in einer Ablehnung endet) wird der teure, unsichtbare (§4.2).

**Ein Ausschlussrecht ist damit ein Mechanismus zur Herstellung des unsichtbaren Fehlers.** Es ist nicht bloß unzulässig, weil das Wissen fehlt — es wäre auch mit vollständigem Wissen falsch.

**Wer die Überlappung dann auflöst:** Die Registrierung findet sie (§5.6) und meldet sie dem **Menschen**, der beide Zettel pflegt. Der weiß, dass es beide Dienste gibt — er ist der einzige in der Kette, der es wissen darf. Er schärft daraufhin einen der beiden Zettel **an seiner Äußerungsbeschreibung**. Damit bleibt das Wissen über die Nachbarschaft dort, wo es hingehört: bei der Person, nicht im System.

**Das gleichzeitige Schreiben verhindert nicht der Empfang.** Zwei Dienste, die beide zustellen und beide schreiben, kollidieren nicht am Routing, sondern am Gegenstand — und dagegen wirkt das Clipboard: Wer im selben Durchlauf einen Anker anlegt, legt ihn ab, und der zweite übernimmt ihn statt einen eigenen zu erzeugen (§5.4). **Die Reihenfolge löst das, nicht die Auswahl.**

#### 3.6a Die Unabhängigkeit ist eine Anweisung, keine Garantie — und deshalb messbar

**Hier liegt eine Schwäche, die benannt gehört.** Liegen alle Zettel in einem einzigen Modellaufruf, sieht das Modell sie zusammen und wägt sie unvermeidlich gegeneinander ab, ob es soll oder nicht. Ein Aufruf je Zettel wäre strukturell unabhängig und kostet so viele Aufrufe, wie es Dienste gibt.

**Der tragbare Weg ist der eine Aufruf mit ausdrücklicher Anweisung:** jeden Zettel für sich beurteilen, nicht vergleichen, nicht den besten wählen. Damit ist die Unabhängigkeit eine Bitte an das Modell und keine Eigenschaft des Aufbaus — **und genau deshalb muss sie geprüft werden statt geglaubt.**

> **Die Gegenprobe auf Unabhängigkeit:** Ein Zettel wird allein beurteilt, dann zusammen mit einem zweiten. **Ändert sich das Urteil über den ersten, ist die Unabhängigkeit verletzt** — und die Zahl der Fälle, in denen sie sich ändert, ist das Maß dafür.

Das ist ein Zeuge, der falsch sein kann, und er gehört zum Mechanismus. Ohne ihn ist *„jeder Zettel für sich"* eine Absicht im Prompt und niemand erfährt, ob sie eingehalten wird.

---

## 4. Die Zustellung — der Zweifel geht an die Fachabteilung

**Ort im Code:** die Anmeldung in `server/agents/nmcp.py`, der Abgleich samt Zählern in `server/agents/nmcp_quote.py`.

### 4.1 Die Regel

> **Kann der Empfang nicht klar entscheiden, ob ein Dienst zuständig ist, wird zugestellt. Die Unschärfe wird dort aufgelöst, wo das Fachwissen liegt — nicht am Empfang.**

Der Empfang entscheidet die klaren Fälle. Er hat keinen Zugriff auf den Bestand des Dienstes, kennt seine Fachsprache nicht und darf sie nicht kennen (§3.2). **Ein Empfang, der Unschärfe selbst auflöst, tut es notwendig auf schlechterer Grundlage als der Dienst.**

Die Fachabteilung hat für diesen Fall einen eigenen Ausgang: Sie prüft den Auftrag gegen ihren Bestand und antwortet gegebenenfalls mit einer begründeten Ablehnung (§6.7). **Eine überflüssige Zustellung endet also nicht in einem Fehler, sondern in einem Urteil** — und genau deshalb ist sie billig.

### 4.2 Die Fehlerkosten sind asymmetrisch, und daraus folgt die Schwelle

Die beiden Fehlrichtungen sind nicht gleich teuer:

| Fehler | Kosten | Sichtbarkeit |
|---|---|---|
| **Zugestellt, obwohl unzuständig** | ein Modellaufruf, eine Ablehnung | sichtbar — die Ablehnung steht in der Prüfspur |
| **Nicht zugestellt, obwohl zuständig** | **die Leistung selbst** | **unsichtbar** — es gibt keinen Lauf, der fehlt |

> **Der ausgebliebene Aufruf ist der teure Fehler, und er ist der unsichtbare.** Ein Dienst, der nie gefragt wird, verhält sich nach außen wie ein Dienst, der nicht gebraucht wird. Niemand vermisst ihn, und nichts schlägt an.

Daraus folgt die Regel für jede Schwelle im Zustellpfad:

> **Die Schwelle wird zugunsten des Zustellens gesetzt. Überwacht wird die Nichtzustellung, nicht die Fehlzustellung.**

Und daraus folgt die Messgröße, die mit dem Mechanismus zusammen entsteht: **Für jeden angemeldeten Dienst ist die Zahl seiner Zustellungen zu erheben und gegen eine von ihm selbst genannte Quote zu halten.** Ein Dienst mit null Zustellungen ist kein seltener Fall — er ist ein Befund, und zwar entweder ein unbrauchbarer Aushang oder ein Dienst, den niemand braucht. Beides muss man wissen, und beides sieht ohne die Zahl gleich aus. Der Mechanismus dafür steht in §4.4 bis §4.9.

### 4.3 Was diese Regel nicht erlaubt

**Sie erlaubt nicht, im Zweifel an alle zuzustellen.** Der Zweifel bezieht sich auf einen Dienst, dessen Aushang **angesprochen** ist — nicht auf die Restmenge. Ein Aushang, der bei jeder Äußerung anspricht, trennt nichts und ist derselbe Defekt wie einer, der nie anspricht.

### 4.4 Die Quote — der Aushang wird eine Behauptung, die falsch sein kann

> **Jeder Dienst nennt bei der Anmeldung eine geschätzte Quote: In welchem Anteil der Äußerungen kommt er vor? Der Empfang zählt die tatsächlichen Zustellungen und hält sie gegen die Schätzung. Weicht sie ab, meldet der Abgleich.**

**Das ist der wichtigste Absatz dieser Konvention, und der Grund liegt nicht in der Zahl.** Eine Deklaration ohne Leser wird gepflegt und nie widerlegt — es gibt keinen Lauf, der sie prüft, und keinen Fehler, den sie auslöst (§8.2). Genau so verrottete im Bestand ein Geltungsbereich unbemerkt vier Monate lang.

> **Die Quote gibt jedem Aushang einen Leser, der ihm widersprechen kann.** Ein Schritt wirkt, wenn sein Ergebnis eine Zahl ist, die falsch sein kann — nicht, wenn er eine Handlung nennt. *„Ich bin für Zeitangaben zuständig"* kann nicht falsch sein. *„Ich komme in einem Viertel der Äußerungen vor"* kann es, und deshalb wirkt es.

**Die Quote ist nicht dafür da, genau zu sein.** Sie ist dafür da, falsifizierbar zu sein.

### 4.5 Die Skala — fünf Stufen, und die Grobheit ist Absicht

| Angabe | Bedeutung | Band |
|---|---|---|
| **0 %** | praktisch nie — eine Ausnahme | 0 bis unter 12,5 % |
| **25 %** | ein Viertel der Äußerungen | 12,5 bis unter 37,5 % |
| **50 %** | etwa die Hälfte | 37,5 bis unter 62,5 % |
| **75 %** | die meisten | 62,5 bis unter 87,5 % |
| **100 %** | praktisch immer | ab 87,5 % |

**Jede Stufe ist ein Band, kein Punkt.** Niemand kann über seinen eigenen Dienst 37 % schätzen, und wer es behauptet, hat geraten und Genauigkeit vorgetäuscht. Fünf Stufen sind das, was ein Mensch über seinen Dienst tatsächlich weiß — und eine grobe Angabe, die widerlegbar ist, ist mehr wert als eine feine, die es nicht ist.

**0 % ist eine zulässige und sinnvolle Angabe.** Ein Dienst für Charakteränderungen kommt selten vor, und das ist kein Mangel. Die Angabe sagt: seltener als die Auflösung dieser Skala.

### 4.6 Die Bezugsgröße — und hier liegt die Falle

**Der Nenner ist die Zahl der Äußerungen einer Art, die den Empfang erreicht haben — nicht die Zahl aller Durchläufe.**

Der Grund ist gemessen: An einem Tag Betrieb waren **49 von 122 Durchläufen eigene Impulse** des Hintergrunds, nicht Nutzeräußerungen. Die Impulsrate ist eine Eigenschaft des Hintergrund-Zeitgebers und hat mit keinem Fachdienst zu tun. Wer beide Arten in einen Nenner wirft, bekommt eine Quote, die schwankt, sobald jemand den Takt des Hintergrunds ändert — und der Dienst, dessen Zahl daraufhin ausschlägt, hat nichts falsch gemacht.

> **Ein Dienst nennt seine Quote je Graph, in dem er angemeldet ist.** Damit bekommt auch die Geltungsbereichs-Angabe einen Leser: Ein Dienst, der für beide Graphen angemeldet ist und nur in einem vorkommt, ist entweder falsch angemeldet oder in einem der beiden unerreichbar.

**Und gezählt wird die Zustellung, nicht der Erfolg.** Der Empfang entscheidet, die Pipeline führt aus, und zwischen beidem kann etwas verlorengehen. Zwei Zähler:

| Zähler | Was er zählt |
|---|---|
| `zugestellt` | der Empfang hat den Dienst gewählt |
| `bearbeitet` | die Pipeline ist an einem der vier Ausgänge angekommen |

**Die Quote vergleicht gegen `zugestellt`.** Die Differenz zwischen den beiden Zählern ist ein eigener Befund — ein Zustellverlust, und der hat mit dem Aushang nichts zu tun. Wer nur `bearbeitet` zählt, liest einen Pipeline-Defekt als Routing-Problem.

### 4.7 Die Schwellen — als Verhältnis, nicht als Differenz

> **Warnung, wenn das Verhältnis gemessen zu geschätzt außerhalb von 0,75 bis 1,33 liegt. Fehler, wenn es außerhalb von 0,5 bis 2,0 liegt.**

**Als Verhältnis und nicht als Prozentpunkt-Differenz, und das ist keine Formsache.** Eine Differenz beurteilt dieselbe Fehlschätzung je nach Richtung verschieden: Von 25 % auf 50 % sind +100 %, von 50 % auf 25 % sind −50 % — dieselbe Verwechslung zweier Nachbarstufen, zwei verschiedene Urteile. Das Verhältnis ist in beide Richtungen symmetrisch: Faktor 2 ist Faktor 2, gleich ob nach oben oder unten.

| Geschätzt | Warnung unter | Warnung über | Fehler unter | Fehler über |
|---|---|---|---|---|
| 0 % | — | 12,5 % | — | 25 % |
| 25 % | 18,8 % | 33,3 % | 12,5 % | 50 % |
| 50 % | 37,5 % | 66,7 % | 25 % | 100 % |
| 75 % | 56,3 % | 100 % | 37,5 % | — |
| 100 % | 75 % | — | 50 % | — |

**Bei 0 % gelten absolute Schranken**, weil ein Verhältnis zu null nicht gebildet werden kann: Warnung, sobald das Band verlassen wird; Fehler eine Stufe darüber.

**Bei 100 % und 75 % fällt die obere Schranke weg**, weil die Skala dort endet. Das ist kein Sonderfall, sondern die Folge davon, dass es über *immer* nichts gibt.

### 4.8 Die Mindest-Stichprobe — ohne sie meldet der Abgleich Rauschen

**Eine Quote über vier Durchläufe ist keine Quote.** Bei einer wahren Rate von 25 % liegt in vier Durchläufen mit rund einem Drittel Wahrscheinlichkeit keine einzige Zustellung — der Abgleich meldete einen Fehler, wo die Schätzung stimmte.

**Die Mindestzahl ist gerechnet, nicht gesetzt.** Verlangt wird, dass das 95-Prozent-Intervall der Messung die Nachbarstufe ausschließt. Im ungünstigsten Fall (geschätzt 50 %, größte Streuung):

| Zu erkennen | Abstand | Nötige Durchläufe | Gesetzt auf |
|---|---|---|---|
| halbe Abweichung (Fehler) | 25 Prozentpunkte | 16 | **30** |
| Viertel-Abweichung (Warnung) | 12,5 Prozentpunkte | 62 | **100** |

Die gesetzten Werte liegen bewusst über dem Rechenergebnis. Die Asymmetrie ist begründet: **Je größer die behauptete Abweichung, desto weniger Durchläufe braucht es, um ihrer sicher zu sein.**

> **Unterhalb der Mindestzahl meldet der Abgleich *„noch keine Aussage"* — und das ist ein Zustand, der sichtbar bleibt, nicht Schweigen.** Ein Dienst, der monatelang unter der Mindestzahl bleibt, hat damit selbst einen Befund: Seine Quote ist nicht prüfbar, weil er zu selten vorkommt. Genau das wäre sonst der stille Fall.

**Das Fenster läuft über die letzten N Äußerungen der betreffenden Art, nicht über einen Kalenderzeitraum.** Ein Zeitfenster gibt in einer stillen Woche einen Fehlalarm und in einer geschwätzigen ein Gefühl von Sicherheit; ein Fenster über Durchläufe normiert sich selbst.

### 4.9 Was eine Abweichung bedeutet — die Richtung ist die Diagnose

| Befund | Was er heißt | Wo zu suchen |
|---|---|---|
| gemessen **deutlich unter** geschätzt | **der Dienst wird übersehen** — der teure, unsichtbare Fehler | Aushang zu eng · ein Negativfall zu breit · ein Nachbardienst fängt ab |
| gemessen **deutlich über** geschätzt | der Dienst wird behelligt | Aushang zu breit · Negativfälle fehlen |
| gemessen **null**, geschätzt über null | der Dienst ist **unerreichbar** | keine Naht · kein Aushang, der anspricht · die Anmeldung ist verrottet |
| gemessen **null**, geschätzt null | konsistent — **und trotzdem ein Befund** | siehe §4.2: unbrauchbarer Aushang oder unnötiger Dienst, beides sieht gleich aus |
| Quote trifft, aber **hohe Ablehnungsquote** | der Aushang trifft, das **Urteil** nicht | die **Grenze** fehlt in der Anmeldung (§3.4) — der Dienst wird richtig gerufen und ist inhaltlich unzuständig |

**Die letzte Zeile ist die, die den Mechanismus mit dem vierten Ausgang verbindet**, und sie ist ohne ihn nicht zu haben: Ein Dienst, der genau so oft zugestellt wird wie geschätzt und die Hälfte davon ablehnt, hat einen richtigen Aushang und eine falsche Grenzangabe. Wer nur die Zustellquote betrachtet, sieht dort nichts.

> **Beide Abweichungsrichtungen bekommen dieselben Schwellen, und sie sind nicht gleich teuer.** Nach §4.2 ist die Untererfüllung der teure, unsichtbare Fall — die Überschreitung endet in einer Ablehnung und ist billig. Ob die untere Schranke deshalb enger gesetzt werden soll als die obere, ist eine Frage der Gewichtung und keine der Umsetzung; sie ist bewusst nicht in dieser Fassung entschieden.

---

## 5. Der Handshake — die Naht wird zugesagt, nicht geraten

> **Naht** heißt der Übergang zwischen zwei Modulen an ihrer Grenze. Ein Plugin ist genau das: die Grenze des Systems zu einem von außen kommenden Dienst. Die Einbindung ist die Naht, und sie muss stimmen.
>
> **Der Begriff ist absichtlich weiter als dieses Dokument.** Dieselbe Regel gilt, wo zwei **Skalen** zusammenstoßen: Dort steht ein benannter, abgeleiteter Abbildungsfaktor dazwischen und keine rohe Addition (`novaberg-haltungsraum_k.md` §6). Der Satz darüber ist in beiden Fällen derselbe — **wo zwei Dinge zusammengeführt werden, steht eine benannte, geprüfte Zusage und keine rohe Übergabe.** Der Skalenfall ist der numerische, der Handshake der schnittstellenseitige.

**Die Registrierung tut zwei Dinge, und der Aufruf danach tut eines.**

| Zeitpunkt | Was geschieht |
|---|---|
| **Registrierung** | die Naht herstellen (§5.1 bis §5.4) **und** die Kompatibilität prüfen (§5.7 bis §5.10) |
| **Aufruf** | Auftrag hinein, Antwort heraus (§5.5) |

### 5.1 Die Regel

> **Ein Dienst meldet bei der Anmeldung seinen Bedarf an. Der Empfang antwortet mit einer verbindlichen Fundstelle oder mit einer Ablehnung. Ohne Zusage wird der Dienst nicht eingebunden.**

Der Ablauf, in vier Zügen:

```
Dienst   → "Ich brauche den Zustand des Objekts A."
Empfang  → "Den gibt es. Er liegt unter `zustand_a`, ist vom Typ T,
            bedeutet B, und lebt V."
Dienst   → "Angenommen."      ← eingebunden
```

oder

```
Dienst   → "Ich brauche den Zustand des Objekts A."
Empfang  → "Den gibt es hier nicht."
                              ← NICHT eingebunden, laut, beim Start
```

### 5.2 Die vier Teile einer Zusage

Eine Fundstelle besteht nicht aus einem Namen. **Sie besteht aus vier Angaben, und wer eine davon wegfallen lässt, hat geraten statt zugesagt:**

| Teil | Warum er nicht fehlen darf |
|---|---|
| **Name** | der Schlüssel, unter dem gelesen wird |
| **Typ** | ein Schlüssel mit dem erwarteten Namen und einem anderen Typ ist schlimmer als ein fehlender |
| **Bedeutung** | `timeline_id` kann der angelegte oder der gefundene Eintrag sein — der Unterschied entscheidet über die Richtigkeit des Ergebnisses |
| **Lebensdauer** | beim eigenen Dienst implizit ein Durchlauf; beim fremden nicht mehr, und dann hält jemand einen Schlüssel für gültig, den niemand mehr kennt |

> **Die Naht muss stimmen.** Ein Bedarf, der auf einen Schlüssel zeigt, den es nicht gibt, verhindert die Einbindung — **laut, beim Start, nicht still im dritten Durchlauf.** Das ist der einzige Zeitpunkt, an dem ein solcher Fehler billig ist.

### 5.3 Zur Anmeldezeit, nicht zur Laufzeit — und das ist die Grenze zum Verworfenen

**Dieser Abschnitt trennt den Handshake von einem Mechanismus, der in diesem Projekt geprüft und verworfen wurde.** Ohne die Trennung liest sich §5.1 wie dessen Wiederauferstehung.

Verworfen ist die **Auflösung zur Laufzeit**: ein Index über Anbieter, der pro Durchlauf befragt wird, ein Merker für offene Bedarfe, ein Wiedereintritt in die Schleife. Der Text liegt vollständig unter `archive/novaberg-convention-planner-needs-erweiterung.md`; der Grund war eine Zahl — eine Kette und ein Anbieter je Bedarf im Bestand. Ein Index über einen Eintrag vermittelt nichts.

**Der Handshake ist das Gegenteil davon:**

| | Verworfene Laufzeit-Auflösung | NMCP-Handshake |
|---|---|---|
| **Wann** | in jedem Durchlauf | **einmal, beim Anmelden** |
| **Ergebnis** | ein gefundener Anbieter | **eine feste Naht im Code** |
| **Bei Nichterfüllung** | Wiedereintritt, Wartezustand | **keine Einbindung, laut** |
| **Wer entscheidet** | ein Vermittler zur Laufzeit | der Empfang, einmal, statisch |
| **Prüfbar** | nein — die Zuordnung entsteht erst im Lauf | **ja, beim Start** |

**Damit bleibt die Grundregel des Datentransports unangetastet:** Wer welchen Wert übernimmt, ist Code und keine Inferenz. Der Handshake ändert nicht, *wie* der Wert wandert — er wandert weiterhin über einen deklarierten, flachen, benannten, optionalen Schlüssel nach `novaberg-convention-planner-needs.md` §3. **Er ändert nur, ob die Bindung überhaupt zustande kommt, und er verlegt diese Frage vom dritten Durchlauf an den Start.**

### 5.4 Der Zustand wird nach Lieferfähigkeit zugeschnitten

> **Ein Dienst erhält, was er angemeldet hat — nicht, was vorhanden ist.**

Der Gedanke *„der Dienst nimmt sich, was er braucht"* ist richtig und hat eine Bedingung, die leicht übersehen wird: **Er setzt voraus, dass der Dienst sagt, wonach er greift.** Ohne Anmeldung bedeutet *„nimm dir, was du brauchst"* faktisch *„ich gebe dir alles"* — und damit ist der Zustand kein Clipboard mehr, sondern ein Kontext-Dump mit allen Schäden, gegen die die Clipboard-Bauart gerichtet ist.

Deshalb ist der Bedarf keine Höflichkeitsangabe, sondern **die Gegenseite der Übergabe:** Der Empfang legt hin, was zugesagt ist; der Dienst nimmt, was er angemeldet hat; **was weder angemeldet noch zugesagt ist, wandert nicht.**

Und die Optionalität bleibt: Ein zugesagter Schlüssel darf im einzelnen Durchlauf leer sein, weil der Erzeuger nicht lief. **Die Zusage sichert den Kanal, nicht den Wert.** Der lesende Dienst arbeitet ohne den Wert weiter und hält nicht an.

### 5.5 Der Aufruf bleibt trivial — und das ist der Ertrag des Handshakes

> **Zur Laufzeit gilt: Auftrag hinein, Antwort heraus.** Keine Verhandlung, keine Suche, kein Index, kein Wiedereintritt. Die Naht steht, der Zustand liegt an den zugesagten Stellen, der Dienst nimmt sich das Angemeldete.

**Das ist der eigentliche Grund für den ganzen Handshake, und er ist wichtiger als jede seiner Einzelregeln.** Alle Kosten der Anbindung liegen an der Registrierung — also dort, wo etwas noch **verweigern** kann. Zur Laufzeit kann niemand mehr nein sagen, ohne das Gespräch anzuhalten; ein Aufrufer mitten im Turn hat nur die Wahl zwischen weitermachen und scheitern. Wer die Prüfung dorthin verlegt, hat sie faktisch abgeschafft.

**Eine Ausnahme, und nur eine:** Die Antwort darf *„ich brauche eine Angabe"* lauten (§6.4). Dann ist der Aufruf kein einzelner Austausch, sondern ein **begrenzter Wechsel** — der Dienst nennt, was er braucht, und erhält beim erneuten Aufruf seinen eigenen Zustandsmerker zurück.

**Die Grenze ist Pflicht und keine Feinheit:** Die Zahl der Rückfragen je Auftrag ist beschränkt. Ohne Schranke kann ein Dienst endlos nachfragen, und der Auftrag hat keinen Endzustand. Ein Transport, der strikt nur einen Austausch zulässt, macht das Rückfrage-Tor unbaubar — wer den Aufruf entwirft, entwirft diesen Fall mit.

### 5.6 Die Registrierung ist der einzige Ort mit dem Gesamtbild

**Bisher ist der Handshake zweiseitig beschrieben: ein Dienst, ein Bedarf, eine Zusage.** Das lässt den wertvollsten Teil des Zeitpunkts ungenutzt.

> **Zur Laufzeit sieht niemand alle Dienste zugleich. Bei der Registrierung sieht der Empfang sie alle.** Das ist der einzige Moment, in dem Fragen über die Menge beantwortbar sind — und diese Fragen sind genau die, aus denen später Fehlrouting entsteht.

Vier Prüfungen sind nur dort möglich, und alle vier laufen **vor dem ersten Durchlauf**:

| Prüfung | Was sie findet |
|---|---|
| **Quotensumme** | Liegt die Summe aller Quoten weit unter 100 %, erreicht ein großer Teil der Äußerungen keinen Dienst. Liegt sie darüber, beanspruchen mehrere Dienste dieselben Äußerungen — **das ist zulässig und der Normalfall** (§3.6), auffällig ist erst ein Vielfaches. Beides ist eine Zahl, bevor irgendetwas läuft |
| **Überlappende Aushänge** | Zwei Dienste, deren Erkennungsmerkmale sich schneiden, **ohne dass einer den anderen als Negativfall nennt**. Die häufigste Quelle von Fehlzustellungen — ein paarweiser Vergleich der Aushänge |
| **Gleicher Bedarf, verschiedene Bedeutung** | Zwei Dienste verlangen denselben Schlüssel, einer meint den angelegten und einer den gefundenen Eintrag. Zur Laufzeit ist das nie sichtbar; bei der Registrierung stehen beide Anmeldungen nebeneinander |
| **Kanal ohne Gegenstück** | Ein Bedarf, den niemand erzeugt (verhindert die Einbindung, §5.1) — **und die Gegenrichtung:** ein zugesagter Schlüssel, den niemand anmeldet. Das ist ein toter Kanal, und im Bestand gibt es dafür einen Präzedenzfall mit **beiden Enden leer** über Monate |

#### 5.6a Diese Prüfungen erzeugen eine Meldung, niemals eine Regel für den Empfang

**Der wichtigste Satz dieses Abschnitts, und ohne ihn kippt er ins Gegenteil.**

Der paarweise Vergleich zweier Aushänge findet einen **Mangel an einem Zettel** — dass ein Negativfall fehlt. Sein Ergebnis geht an den **Autor** des Zettels und wird von ihm dort behoben.

> **Es geht nicht an den Empfang.** Würde der Fund als Vorrang, Ausschluss oder Rangfolge in die Zustellentscheidung eingebaut, hätte der Empfang genau das Verhältniswissen, das §3.6 ihm verwehrt — und es entstünde eine zentrale Zuordnungstabelle, nur auf dem Umweg über eine Prüfung. **Der Zeitpunkt macht keinen Unterschied: Eine bei der Registrierung berechnete Rangfolge ist zur Laufzeit dieselbe Zuordnungstabelle.**

Der Unterschied in einem Satz: **Die Registrierung darf über die Menge urteilen, um Zettel zu verbessern — nicht, um Zustellungen zu entscheiden.**

Deshalb ist auch keine dieser vier Prüfungen ein Einbindungshindernis. Sie stehen in §5.9 unter *gemeldet*, nicht unter *verweigert*: Ein fehlender Negativfall macht einen Dienst nicht arbeitsunfähig, er macht ihn ungenau — und die Ungenauigkeit fällt dem Quotenabgleich auf (§4.9, Zeile *behelligt*).

### 5.7 Die Naht-Signatur — damit die Zusage nicht verrottet

**Der Handshake prüft einmal. Danach gilt seine Zusage unbefristet — und genau das ist die Bauart, an der dieses Projekt mehrfach bezahlt hat.** Eine Angabe, die einmal geprüft und nie wieder angesehen wird, ist eine ungelesene Deklaration mit Anlaufzeremonie (§8.2).

> **Jede Zusage trägt eine Signatur über ihre vier Teile** — Name, Typ, Bedeutung, Lebensdauer, über alle zugesagten Fundstellen des Dienstes. Die Signatur wird bei der Einbindung festgehalten und **bei jedem Start neu gebildet und verglichen.**

Drei Fälle, drei Folgen:

| Fall | Folge |
|---|---|
| Signatur gleich | die Naht gilt weiter, keine Meldung |
| Signatur geändert, **der Dienst hat neu angemeldet** | reguläre Neuverhandlung — der Dienst weiß, dass sich etwas geändert hat |
| Signatur geändert, **der Dienst hat nicht neu angemeldet** | **Einbindung verweigert, laut.** Jemand hat die Bedeutung eines Schlüssels unter dem Dienst weggezogen |

**Der dritte Fall ist der, den es ohne Signatur nicht zu erkennen gibt.** Er entsteht nicht durch Nachlässigkeit des Dienstes, sondern durch eine berechtigte Änderung auf der anderen Seite der Naht — und er ist deshalb der wahrscheinlichste von allen. Ein Schlüssel behält seinen Namen und ändert seine Bedeutung: Das ist die Änderung, die kein Typprüfer sieht und kein Test bemerkt.

### 5.8 Was Kompatibilität heißt — die Prüfliste

**„Kompatibilität prüfen" ist ohne Aufzählung eine Absicht.** Fünf Prüfungen, jede mit einer eigenen Folge:

| Prüfung | Bedingung | Folge bei Verstoß |
|---|---|---|
| **Naht** | jeder Bedarf hat eine Zusage mit vier Teilen | keine Einbindung |
| **Signatur** | die festgehaltene stimmt mit der gebildeten | keine Einbindung |
| **Ausgänge** | der Dienst bedient alle vier, **insbesondere den vierten** | eingeschränkte Einbindung, siehe unten |
| **Sprache** | der Aushang nennt kein Fachwort des Dienstes | Meldung, Einbindung läuft |
| **Quote** | eine Schätzung liegt vor | Meldung; bei fremden Diensten Ersatzregel, siehe §5.9 |

**Die dritte Zeile ist die, die nicht auf der Hand liegt, und sie verbindet §5 mit §4.** Die Zweifelsregel setzt den vierten Ausgang voraus: Im Zweifel wird zugestellt, **weil die Fachabteilung ablehnen kann**. Ein Dienst ohne begründete Ablehnung *führt aus*, was ihn erreicht — er beurteilt es nicht.

> **Also darf ein Dienst ohne vierten Ausgang keine Zweifelsfälle bekommen.** Er wird eingebunden, aber nur für klare Zustellungen; die Unschärfe bleibt am Empfang und wird dort als unauflösbar gemeldet. Das ist eine ehrliche Einschränkung — und die unehrliche Alternative wäre, ihm Zweifelsfälle zu schicken und zu hoffen.

### 5.9 Drei Grade der Ablehnung — und sie trifft den Dienst, nicht das System

**Nicht jede Unstimmigkeit ist gleich schwer, und ein einziger Grad wäre in beide Richtungen falsch:**

| Grad | Wann | Wirkung |
|---|---|---|
| **verweigert** | Naht oder Signatur stimmen nicht | der Dienst wird nicht eingebunden — er *kann* nicht arbeiten |
| **eingeschränkt** | der vierte Ausgang fehlt | eingebunden, aber ohne Zweifelsfälle |
| **gemeldet** | Aushang in Fachsprache, Quote fehlt | eingebunden; der Mangel ist ein Qualitätsdefekt, kein Funktionsdefekt |

**Und die Ablehnung trifft immer nur den einen Dienst.** Ein fremdes Plugin mit fehlerhafter Anmeldung darf den Assistenten nicht am Starten hindern — das System kommt hoch, der Dienst ist nicht gebunden.

> **Daraus folgt eine Pflicht, die man leicht übersieht:** Eine verweigerte Einbindung muss **zur Laufzeit sichtbar bleiben**, nicht nur in einer Startmeldung. Eine Zeile beim Hochlauf ist nach zehn Minuten aus dem Blick, und danach verhält sich der fehlende Dienst wie ein Dienst, den niemand braucht — genau der stille Zustand, gegen den §4.2 gebaut ist.

**Für einen fremden Dienst ohne Quote gilt eine Ersatzregel statt einer Verweigerung:** Der Empfang **erhebt** sie über das erste vollständige Fenster und hält sie danach als Zusage fest. Ein fremder Anbieter kann nicht wissen, welchen Anteil er in *diesem* System hat — die Angabe zu verlangen wäre unerfüllbar, sie wegzulassen nähme dem Aushang die Widerlegbarkeit. Die erhobene Quote ist beides: erfüllbar und prüfbar.

### 5.10 Die Grenze der Prüfung — Form, nicht Verhalten

**Der Handshake prüft, was zugesagt wurde, nicht was getan wird.** Dass ein Schlüssel existiert, seinen Typ hat und eine Bedeutung zugesagt bekam, ist prüfbar. Dass der Dienst den Wert dieser Bedeutung entsprechend **behandelt**, ist es nicht.

| | Eigener Dienst | Fremder Dienst |
|---|---|---|
| Form der Naht | geprüft | geprüft |
| Umgang mit dem Wert | durch Tests belegbar | **nur beobachtbar** |

Für den fremden Dienst bleibt damit derselbe Vorbehalt wie in §7: Was nicht erzwungen werden kann, wird gemessen — und was nicht gemessen werden kann, gehört in einen Freigabedialog und nicht in eine Auswahlheuristik. **Ein Handshake, der Vertrauen verspricht, verspricht zu viel.** Er stellt die Naht her und schließt die Fälle aus, die *sicher* nicht gehen; er sagt nicht, dass die übrigen gut gehen.

---

## 6. Die Pipeline — neun Stufen und vier Ausgänge

### 6.1 Die Regel

> **Ein NMCP-Dienst durchläuft neun Stufen. Die Intelligenz liegt vor und nach der Bearbeitung, nicht in ihr.**

```
1  Auftragsprüfung      — ist der Auftrag formal vollständig?
2  Normalisierung       — Rohsprache zu bereinigter Aussage
3  Domänenübersetzung   — bereinigte Aussage zu Fachsprache und Aktion
4  Semantik-Prüfung     — passt die Aktion zum BESTAND?
5  Rückfrage-Tor        — bei Unschärfe fragen statt handeln
6  Bearbeitung          — deterministisch, ohne Sprachmodell
7  Ergebnisprüfung      — ergibt das Gespeicherte Sinn?
8  Rücknahme            — wenn nicht: zurückrollen
9  Rückgabe             — vier Ausgänge
```

### 6.2 Stufe 1 bis 3 — vom Rohtext zur Fachsprache

**Rohdaten vollständig erhalten, intern nur auf validierten Daten arbeiten.** Zwei Schichten, und die Trennung ist strikt: Rohtext, Emotion und Erregung gehören dem Antwortpfad; normalisierte Aussage, Aktion und Ziel gehören der Verarbeitungskette. Kein Bearbeitungscode liest den Rohtext, kein Antwortcode liest die Normalisierung. Ausführlich in `novaberg-pattern-domain-language.md`.

**Die Fachsprache gehört dem Dienst, nicht dem Empfang.** Das ist dieselbe Regel wie in §3.2, hier an der anderen Grenze: Der Aushang geht nach außen in der Sprache des Empfangs, die Übersetzung nach innen findet im Dienst statt.

**Wo die Normalisierung sitzt, ist eine Kostenentscheidung.** Sie gehört in einen Schritt, der ohnehin ein Sprachmodell ruft — dann ist sie ein zusätzliches Ausgabefeld statt eines zusätzlichen Aufrufs.

### 6.3 Stufe 4 — die Semantik-Prüfung gegen den Bestand

**Stufe 1 prüft die Form des Auftrags. Stufe 4 prüft ihn gegen den Bestand.** Das ist der Unterschied zwischen einer Maske und einer Fachabteilung.

Eingabe: die aktiven Datensätze des Fachgebiets plus die geplante Operation. Ausgabe strukturiert, mit engem Wertebereich:

| Befund | Bedeutung | Folge |
|---|---|---|
| `passt` | keine Kollision | weiter zum Tor |
| `widerspruch` | steht gegen einen aktiven Datensatz | Rückfrage mit dem Widerspruch im Wortlaut |
| `ergaenzung` | erweitert einen aktiven Datensatz | Information über den Folgezustand |
| `redundanz` | im Kern vorhanden | Konsolidierungs-Rückfrage |
| `identisch` | exakt vorhanden | Ablehnung ohne Tor — nichts zu tun |

**Das ist die Stufe, an der aus einer widersprüchlichen Anweisung ein Urteil wird statt eines Datensatzes.** Drei live beobachtete Fehlspeicherungen hatten alle dieselbe Wurzel: Der Dienst prüfte nie, ob die Operation Sinn ergibt (`novaberg-agent-fachabteilung_k.md` §2.2).

### 6.4 Stufe 5 — das Rückfrage-Tor

> **Rücksprachen sind kein Makel, sondern Qualität.** Ein Dienst, der bei Unschärfe zurückfragt, ist besser als einer, der im Zweifel handelt.

Das Tor hat zwei Aufgaben, und die zweite wird oft vergessen: Es holt eine **Entscheidung** ein (bei Widerspruch) und es holt eine **fehlende Information** nach (bei Lücke). Beides ist derselbe Zustand — erwartet, aber nicht vorhanden — und beides endet in derselben Handlung.

Drei Bedingungen machen ein Tor benutzbar:

**Die Rückfrage ist differenziert, nicht binär.** *„Soll ich das ausführen?"* ist bei jedem Befund aus §6.3 dieselbe Frage und deshalb nutzlos.

**Jede Frageart hat ihren eigenen Rückweg.** Auf *„Soll ich X deaktivieren?"* heißt *„nein"* nicht *„brich alles ab"*, sondern *„lass X aktiv und mach den Rest"*. Ohne strukturierte Antwortdeutung ist die differenzierte Rückfrage schlechter als die binäre, weil sie eine Genauigkeit vortäuscht, die der Rückweg nicht einlöst.

**Der Nein-Pfad funktioniert vor den differenzierten Fragen.** Er ist Voraussetzung, nicht Teil des Umbaus.

### 6.5 Stufe 6 — Bearbeitung ohne Sprachmodell

**Die Schreiboperation bleibt deterministisch.** Das hält sie wiederholbar und trennt die semantische Ebene von der technischen. Ein Sprachmodell mitten in der Transaktion macht jeden Fehlerfall unwiederholbar. Die Phasenform steht in `novaberg-pattern-crud-hardening.md`.

### 6.6 Stufe 7 und 8 — Ergebnisprüfung mit Rückweg

Eingabe: das tatsächlich Gespeicherte plus die ursprüngliche Absicht. Frage: Ergibt das Ergebnis semantisch Sinn als Darstellung dieser Absicht?

> **Eine Ergebnisprüfung ohne Rücknahme ist eine Meldung, keine Prüfung.** Ohne Rückweg wird der Befund protokolliert und das Unsinnige steht trotzdem im Bestand.

Die Rücknahme setzt den Zustand vor die Bearbeitung zurück und übergibt an Stufe 9 mit dem Befund — nicht an den Nutzer mit einer Entschuldigung.

### 6.7 Stufe 9 — vier Ausgänge, und der vierte trägt einen Vorschlag

| Ausgang | Bedeutung | Zuständig für die Folge |
|---|---|---|
| `abgeschlossen` | getan, hier ist das Ergebnis | — |
| `rueckfrage` | ich brauche eine Entscheidung oder eine Angabe | der Mensch |
| `fehler` | **ich konnte nicht** — Verbindung, Schema, Frist | der Betreiber |
| `abgelehnt` | **ich habe nicht** — und hier ist, was stattdessen richtig wäre | der Auftraggeber |

**Ein Fehler ist eine Störung. Eine Ablehnung ist ein Urteil.** Wer beide in denselben Ausgang legt, macht die wertvollste Leistung des Dienstes als Störung sichtbar — und optimiert sie beim nächsten Aufräumen weg.

### 6.8 Die Ablehnung trägt einen Korrekturvorschlag — und das ist ein eigener Mechanismus

> **Eine Ablehnung ohne Vorschlag ist eine Sackgasse. Eine Ablehnung mit Vorschlag ist ein Gegenangebot.**

Der vierte Ausgang ist nicht bloß ein vierter Status. Er ist der Eingang in ein System, das heute fehlt: **die Korrektur.** Die Fachabteilung sagt nicht *„das geht nicht"*, sondern *„das stimmt so nicht — richtig wäre folgendes"*.

Der Ausgang trägt deshalb drei Angaben und nicht eine:

| Teil | Inhalt |
|---|---|
| **Der Befund** | was am Auftrag nicht stimmt, in der Sprache des Auftraggebers |
| **Der Beleg** | woran es der Dienst erkannt hat — welcher Bestandsteil widerspricht |
| **Der Vorschlag** | was der Dienst stattdessen täte, als ausführbarer Auftrag |

**Der Vorschlag geht an den Auftraggeber, nicht in den Bestand.** Ein Dienst, der seinen Korrekturvorschlag selbst ausführt, hat den Auftrag ersetzt statt ihn beurteilt — und das ist derselbe Fehler wie das ungeprüfte Ausführen, nur mit besserem Gewissen.

**Der Vorschlag ist selbst ein Auftrag in NMCP-Form.** Nimmt der Auftraggeber ihn an, läuft er als regulärer Auftrag durch dieselben neun Stufen — einschließlich der Semantik-Prüfung. Ein angenommener Vorschlag überspringt keine Stufe; der Bestand kann sich zwischen Vorschlag und Annahme geändert haben.

---

## 6a. Der zweite Eingang — wenn das Modell selbst greift

**Neu am 19.08.2026, und ausdrücklich vor dem ersten Bau.** Ein Silo soll nicht nur **bestellbar** sein (der Empfang wählt anhand des Aushangs), sondern auch **greifbar** — das Modell zieht es mitten im Denken, wie es heute `web_search` zieht.

**Das ist keine Erweiterung dieser Konvention, sondern die Rückkehr der Hälfte, die §1 ausklammert.** Dort steht, dass das etablierte Protokoll die Auswahl *model-controlled* lässt und dafür keine Protokollnachricht vorsieht; NMCP ist die andere Hälfte. Wer ein Silo zum Werkzeug macht, nimmt die erste Hälfte wieder dazu — beides nebeneinander ist zulässig, und die drei Rollen unterscheiden sich nur darin, **wer entscheidet und wann**:

| Rolle | Wer entscheidet | Wann |
|---|---|---|
| **Quelle** | niemand — sie fließt bei | vor dem Denken |
| **Zettel** | der Empfang, anhand der Äußerung | vor dem Denken |
| **Werkzeug** | das Modell selbst | mitten im Denken |

### 6a.1 Ein Silo hat einen Dienst — die Eingänge sind zwei, die Implementierung ist eine

> **Zettel und Werkzeug sind zwei Türgriffe an derselben Tür.** Wer für den Werkzeug-Eingang eine zweite Suche über denselben Bestand baut, bekommt zwei Rangfolgen, die auseinanderlaufen — und die Abweichung fällt erst auf, wenn jemand dieselbe Frage zweimal stellt und zwei Antworten bekommt.

Der Grund steht im eigenen Bestand: Am 19.08.2026 stellten zwei Wege desselben Dienstes dieselbe Frage mit entgegengesetztem Vorzeichen, weil beide denselben Zettel benutzten. Der Fehler war nicht die doppelte Implementierung, sondern die geteilte — er zeigt aber dieselbe Klasse: **Zwei Eingänge zu einem Gegenstand müssen sich über die eine Sache einig sein, sonst ist der Gegenstand zwei.**

### 6a.2 Die vier Ausgänge überstehen den Werkzeug-Eingang nicht von selbst

Ein Dienst antwortet auf einem von vier Wegen; der vierte trägt einen **Korrekturvorschlag** (§6). Ein Werkzeugaufruf bekommt dagegen eine **Zeichenkette** zurück — die Konvention des Denkknotens kennt keinen vierten Ausgang.

> **Damit wird aus *„ich lehne begründet ab"* und *„ich habe nichts gefunden"* dieselbe leere Antwort**, wenn niemand die Unterscheidung in den Text schreibt. Das ist die Fehlerklasse aus `22_STILLE_FEHLER`, eine Ebene höher: nicht ein stiller Ausfall, sondern ein **eingeebneter Ausgang**.

**Regel:** Ein Dienst, der über beide Eingänge erreichbar ist, faltet seine vier Ausgänge für den Werkzeug-Weg **benannt** in Text — der Ausgang steht als Wort in der Antwort, nicht als Abwesenheit von Inhalt.

### 6a.3 Der Handshake hat auf dem Werkzeug-Weg kein Gegenüber

Ein Dienst bekommt, was er **angemeldet** hat (§5) — der Empfang schneidet den Zustand nach seinen Zusagen zu. Ruft ihn das Modell mitten im Denken, gibt es keinen Empfang, der das täte.

Zwei Auflösungen sind vertretbar, und die Wahl ist eine **Absicht**, keine Implementierungsfrage:

| Auflösung | Preis |
|---|---|
| Der Werkzeug-Eingang reicht denselben zugeschnittenen Zustand durch | Der Aufrufer muss ihn haben — im Denkknoten liegt er nicht selbstverständlich vor |
| Der Dienst kommt ohne den Zustand aus und sagt es an | Er arbeitet dann auf dem Werkzeug-Weg schlechter als auf dem Zettel-Weg, und **das gehört in seinen Aushang**, nicht in seinen Code |

**Ungeklärt ist sie erst dann nicht mehr, wenn sie am Dienst steht.** Ein Dienst, der über beide Eingänge erreichbar ist und dazu nichts sagt, behauptet stillschweigend die erste Auflösung.

---

## 7. Der Unterschied zwischen eigenem und fremdem Dienst

Die Regeln §3 bis §6 gelten für beide. **Genau zwei Zeilen unterscheiden sich, und sie sind die wichtigsten:**

| | Eigener Dienst | Fremder Dienst |
|---|---|---|
| **Anmeldung** | im Code deklariert, gegen den Baum prüfbar | fremder Text — **als unvertrauenswürdig zu behandeln** |
| **Kosten** | **erzwungen** — der Falschmelder scheitert laut | **behauptet** — auffällig an der Uhr oder gar nicht |
| Fachsprache | im eigenen Verzeichnis | seine; die Übersetzung liegt beim Aufrufer |
| Semantik-Prüfung | gegen den eigenen Bestand | er kennt meinen Bestand nicht, ich seinen nicht |
| Lebensdauer des Zustands | ein Durchlauf, implizit | **muss in der Zusage stehen** (§5.2) |
| Audit | er schreibt selbst | **der Aufrufer schreibt für ihn mit** (§8.4) |

> **Die Regel, die daraus folgt:** Was beim eigenen Dienst erzwungen werden kann, muss beim fremden **gemessen** werden — und wo nicht gemessen werden kann, gehört die Angabe in einen Freigabedialog und nicht in eine Auswahlheuristik.

Das ist keine Erfindung dieses Dokuments: Die Spezifikation des Model Context Protocol sagt für ihre eigenen Verhaltenshinweise dasselbe — sie sind unverbindlich, von nicht vertrauenswürdigen Anbietern als untrusted zu behandeln, und taugen für Freigabe und abgestufte Vertrauensstellung, **nicht als Durchsetzung.**

---

## 8. Woran man einen Verstoß erkennt

Acht Formen, in absteigender Schwere. Die ersten drei sind harte Brüche, die übrigen sind stille.

**8.1 Ein Aushang in Fachsprache.** Er verlangt vom Empfang Fachwissen und macht ihn zur zentralen Zuordnung. Erkennbar daran, dass der Aushang eine Operation des Dienstes nennt statt eines Merkmals der Äußerung.

**8.2 Eine Anmeldeangabe ohne Leser.** Der teuerste Verstoß, weil er kein Symptom hat: Er wird gepflegt und nie widerlegt. Ein Feld ohne Leser sieht so lange richtig aus, wie niemand hinsieht — im Bestand deklarieren 15 von 15 Agenten ihre Fähigkeiten, und einer davon deklariert einen Geltungsbereich, in dem er gar nicht erreichbar ist. **Dreizehn stimmen, einer nicht, und kein Lauf konnte es melden** (`novaberg-convention-planner-needs.md` §3.7b).

> **Daraus die Reihenfolge, die nicht die naheliegende ist: Die Anmeldeangaben werden vor dem Anschließen gegengeprüft, nicht danach.** Wer den fehlenden Leser zuerst baut, schaltet eine Datenbasis scharf, die niemand je geprüft hat, und bekommt Fehlrouting in beide Richtungen gleichzeitig.

**8.2a Ein Aushang ohne Quote.** Derselbe Verstoß, eine Stufe früher: Ein Aushang ohne genannte Quote ist eine Behauptung, die nicht falsch sein kann, und damit die Vorform der ungelesenen Deklaration. Der Abgleich aus §4.4 ist der Leser, der jedem Aushang widersprechen kann — wer ihn weglässt, nimmt der Anmeldung ihre einzige Widerlegbarkeit.

**8.2b Ein Quotenabgleich, der unter der Mindest-Stichprobe meldet.** Vier Durchläufe tragen keine Quote. Ein Abgleich, der dort schon urteilt, erzeugt Fehlalarme und wird deshalb abgeschaltet — und mit ihm der einzige Leser aus 8.2a. **Ein Alarm, der zu früh kommt, ist teurer als keiner**, weil er den Mechanismus mitnimmt.

**8.3 Ein Bedarf ohne Zusage, und der Dienst läuft trotzdem.** Die Naht ist geraten. Erkennbar am Start: Ein angemeldeter Bedarf ohne Fundstelle muss die Einbindung verhindern.

**8.4 Ein Aufruf ohne Audit-Eintrag.** Jeder Lauf schreibt *gestartet* und dann *erledigt* oder *fehler*. Bei fremden Diensten ist die Frage ausdrücklich zu beantworten: **Wer schreibt den Eintrag, wenn der Dienst schweigt?** Ein Aufruf ohne Antwort darf nicht als Erfolg enden und nicht spurlos verschwinden.

**8.5 Eine Ablehnung, die als Fehler zurückkommt.** Macht das Urteil zur Störung.

**8.6 Eine Ablehnung ohne Vorschlag.** Formal richtig, praktisch eine Sackgasse.

**8.7 Der Empfang löst die Unschärfe selbst auf.** Erkennbar an einer Zustellentscheidung, die Fachwissen voraussetzt.

**8.7a Der Empfang trägt Verhältniswissen über zwei Dienste.** Erkennbar an einer Rangfolge, einem Vorrang, einem Ausschluss oder einem *„nur wenn kein anderer"* — gleich ob zur Laufzeit gebildet oder bei der Registrierung berechnet und mitgeführt. **Der Zeitpunkt entlastet nicht:** Eine vorberechnete Rangfolge ist zur Laufzeit dieselbe zentrale Zuordnungstabelle. Der Empfang beurteilt jeden Zettel für sich (§3.6); eine Doppelung gehört als Negativfall an den Zettel (§5.6a).

**8.7b Das Urteil über einen Zettel ändert sich, wenn ein zweiter hinzukommt.** Die Unabhängigkeit ist verletzt. Prüfbar durch die Gegenprobe aus §3.6a — ein Zettel allein, dann derselbe neben einem zweiten. **Ohne diese Gegenprobe ist die Unabhängigkeit eine Absicht im Prompt, von der niemand weiß, ob sie eingehalten wird.**

**8.8 Die drei Wiederholversuche verbrennen im Takt statt über die Lebensdauer.** Beobachtet wurde ein Auftrag, der seine drei Versuche in **90 Sekunden** verbrauchte — in exakt drei Takten des Zeitgebers, ohne dass sich zwischendurch etwas hätte ändern können. **Die Obergrenze griff und war wirkungslos.** Die Versuche verteilen sich über die Lebensdauer des Auftrags, nicht über den Takt des Zeitgebers.

---

## 9. Maschinelle Prüfbarkeit

**Sechs der zehn Verstoßformen sind prüfbar, drei davon beim Start.** Dazu seit dem 19.08.2026 die **Rollenmatrix** aus §6a, die keine Verstoßform ist, sondern eine Vollständigkeitsfrage.

| Form | Prüfung | Zeitpunkt |
|---|---|---|
| 8.3 Bedarf ohne Zusage | Abgleich der angemeldeten Bedarfe gegen die zugesagten Fundstellen | **Start** — der Dienst wird nicht eingebunden |
| — Naht verrottet | Signatur über die vier Teile jeder Zusage, neu gebildet und verglichen (§5.7) | **Start** — verweigert, wenn sie sich ohne Neuanmeldung geändert hat |
| — Gesamtbild | Quotensumme · überlappende Aushänge ohne Negativfall · gleicher Bedarf mit verschiedener Bedeutung · Kanal ohne Gegenstück (§5.6) | **Start** — vier Prüfungen über die Menge, **Ergebnis ist eine Meldung an den Autor** (§5.6a) |
| 8.7b Urteil nicht unabhängig | Gegenprobe: ein Zettel allein, dann neben einem zweiten — ändert sich das Urteil? (§3.6a) | Prüfstrecke, **mit Zähler** |
| — vierter Ausgang fehlt | Abgleich der bedienten Ausgänge gegen die vier (§5.8) | **Start** — eingeschränkte Einbindung |
| 8.2a Aushang ohne Quote | Pflichtfeld der Anmeldung, für fremde Dienste erhoben (§5.9) | **Start** |
| 8.2 Angabe ohne Leser | Abgleich jeder Anmeldeangabe gegen ihre Aufrufer im Baum | Prüfstrecke |
| 8.1 Aushang in Fachsprache | Abgleich des Aushangs gegen die Fachbegriffe des eigenen Dienstes | Prüfstrecke, heuristisch |
| 8.2b Abgleich unter der Mindest-Stichprobe | Zählerstand gegen die Schwellen aus §4.8 | **Betrieb, im Abgleich selbst** |
| 8.4 Aufruf ohne Audit | Abgleich der Aufrufe gegen die Audit-Einträge | Betrieb |
| — **Rollenmatrix** (§6a) | Je Silo zählen, welche der drei Rollen es trägt — Quelle über ~~`immer_aktiv`~~ **`enrich_entries`** (⚠ berichtigt am 19.08.2026, siehe unter der Tabelle), Zettel über `router_prompt`, Werkzeug über den Werkzeugkasten des Denkknotens. **Eine leere Zelle ohne Begründung am Silo ist der Befund** | **Start** — Meldung an den Autor, keine Verweigerung: Eine fehlende Rolle kann richtig sein, aber nicht unbemerkt |

> **⚠ Berichtigt am 19.08.2026 — das ursprüngliche Merkmal der Rolle *Quelle* war falsch, und es wäre schweigend falsch gezählt worden.**
>
> Diese Tabelle nannte `immer_aktiv`. Der Enricher ruft `enrich_entries` aber bei **jedem** Manager (`graph/nodes/enricher.py`), gleich was `immer_aktiv` sagt; die Eigenschaft steuert nach `BaseManager` den **Schreibpfad** — *„False = nur bei pending_writes"*. Beides sind Merkmale, aber nicht dasselbe Merkmal.
>
> Maschinell über zehn Silos gezählt: **`immer_aktiv` ergibt 3 Quellen, `enrich_entries` ergibt 4**, und die beiden gehen bei **zweien** auseinander:
>
> | Silo | `immer_aktiv` | eigenes `enrich_entries` | tatsächlich Quelle |
> |---|---|---|---|
> | `kzg` | ja | nein | **nein** — sein Beitrag ist im Dispatcher-Knoten verdrahtet |
> | `timeline` | nein | ja | **ja** |
>
> **Der Fall `timeline` ist der teure:** Er ist der einzige Silo mit allen drei Rollen und damit der Bezugsfall der Matrix. Nach dem alten Merkmal hätte die Prüfung ihn als 2 von 3 gemeldet — und eine Meldung über eine fehlende Rolle, die es gibt, ist schlimmer als keine Meldung.
>
> **Ein dritter Zustand fehlt der Matrix weiterhin:** `fakten` überschreibt `enrich_entries` und ist im Enricher abgeschaltet — mit `continue` übersprungen, begründet im Code mit *„produziert 130+ Rausch-Eintraege"*. *Gebaut und stillgelegt* ist weder ja noch nein und sieht in jeder Zählung wie eine Entscheidung aus.
>
> Gemessen mit `labor/2026-08-19_rollenmatrix.py`; der Anlass war die zweite Kontrolle beim Bau des `wissen`-Dienstes.

**Nicht mechanisch prüfbar:** 8.5 bis 8.8 hängen an Bedeutung — ob eine Rückmeldung ein Urteil oder eine Störung ist, ob ein Vorschlag brauchbar ist, ob eine Zustellentscheidung Fachwissen voraussetzte.

**Der Quotenabgleich (§4.4 bis §4.9) ist keine Verstoßprüfung, sondern der laufende Zeuge der Anmeldung.** Er sitzt im Empfang, nicht in der Prüfstrecke, und meldet in drei Stufen: *noch keine Aussage* unterhalb der Mindest-Stichprobe, *Warnung* ab einer Viertel-Abweichung, *Fehler* ab einer halben. Seine Zähler — `zugestellt` je Dienst und je Graph — sind zugleich die Datenbasis für die Diagnosetabelle in §4.9 und die einzige Größe, die einen unbrauchbaren Aushang von einem unnötigen Dienst unterscheidet.

---

## 10. Erwogene Alternativen

| Alternative | Warum verworfen |
|---|---|
| **Auflösung des Bedarfs zur Laufzeit** — Anbieter-Index, Merker, Wiedereintritt | Geprüft und verworfen: eine Kette, ein Anbieter je Bedarf. Ein Index über einen Eintrag vermittelt nichts. Text unter `archive/novaberg-convention-planner-needs-erweiterung.md`. Zusätzlich hier: Eine Naht, die pro Durchlauf neu entsteht, ist beim Start nicht prüfbar |
| **Den ganzen Zustand übergeben** | Kontext-Dump mit allen Schäden, gegen die die Clipboard-Bauart gerichtet ist. Und die Anmeldung des Bedarfs wäre überflüssig — womit die Zusage entfiele und die Naht wieder geraten wäre |
| **Fähigkeitenliste als Auswahlkriterium** | Im eigenen Bestand vier Monate ohne Leser. Eine Liste von Verben ist kein Auswahlkriterium: Der Aufrufer müsste wissen, welches Verb auf welche Äußerung passt — genau das, was die Liste nicht sagt |
| **Der Empfang löst den Zweifel auf** | Er müsste die Fachsprache aller Abteilungen kennen. Das ist die zentrale Zuordnungstabelle, die bei jedem neuen Anbieter angefasst werden müsste |
| **Der Empfang wählt den besten Treffer** | Eine Rangliste setzt Verhältniswissen über die Dienste voraus, und das läge nirgends außer im Empfang selbst. Er beurteilt jeden Zettel für sich und stellt an jeden zu, dessen Zettel anspricht (§3.6) |
| **Überlappungen als Vorrang im Empfang hinterlegen** | Auch wenn bei der Registrierung berechnet: Eine mitgeführte Rangfolge ist zur Laufzeit dieselbe zentrale Zuordnung. Die Überlappung gehört als Negativfall an den Zettel, dessen Autor seinen Nachbarn kennt (§5.6a) |
| **Ein Modellaufruf je Zettel** | Strukturell unabhängig und damit die sauberste Lösung — sie kostet so viele Aufrufe, wie es Dienste gibt, in jedem Durchlauf. Verworfen zugunsten eines Aufrufs mit ausdrücklicher Unabhängigkeitsanweisung **und einer Gegenprobe darauf** (§3.6a). Wird die Gegenprobe schlecht, ist diese Alternative erneut zu bewerten |
| **Fail-Fast bei fehlender Vorbedingung** | Eine fehlende Auflösung hielte das Gespräch an. Der Nutzer bezahlt für eine Unschärfe, die das System selbst erzeugt hat. Deshalb sichert die Zusage den Kanal und nicht den Wert (§5.4) |
| **Ablehnung als Fehler** | Macht das Urteil zur Störung und die Fachabteilung unsichtbar |
| **Ablehnung ohne Vorschlag** | Formal zulässig und praktisch eine Sackgasse: Der Auftraggeber weiß, dass es nicht ging, und nicht, was ginge |
| **Schwelle zugunsten der Genauigkeit** | Optimiert den sichtbaren Fehler und verschlimmert den unsichtbaren. Ein Dienst, der nie gerufen wird, sieht aus wie einer, der nicht gebraucht wird |

---

## 11. Geltungsbereich

**Erfasst:** jede Anbindung eines Fachdienstes an den Zustellpfad — eigener Agent im Prozess oder fremder Dienst hinter einem Transport. Erfasst sind Anmeldung, Zustellentscheidung, Zustandsübergabe, die neun Stufen und die vier Ausgänge.

**Ausdrücklich nicht erfasst:**

| Nicht erfasst | Warum |
|---|---|
| **Der Lesepfad** | Mehrere Lese-Dienste laufen parallel ohne Datenfluss untereinander. Sie brauchen keine Vorbedingung, nur eine Quelle — dieselbe Grenze wie in `novaberg-convention-planner-needs.md` §8 |
| **Werte innerhalb eines Dienstes** | Was ein Schritt an den nächsten desselben Dienstes weitergibt, folgt der Bauart dieses Dienstes, nicht dieser Regel |
| **Der Weg zum Antwortpfad** | Das Ergebnis trägt Ausgabe, keine Vorbedingung |
| **Hintergrunddienste ohne Zustellentscheidung** | Ein Dienst, der nur nach Zeitplan läuft, braucht keinen Aushang. Kadenz, Kosten, Datenhoheit und Audit gelten trotzdem |
| **Die Wahl des Transports** | Diese Konvention sagt, welche Angaben eine Anmeldung tragen muss, nicht über welche Leitung sie geht |

---

## 12. Versionshistorie

- **v0.5 — 19.08.2026:** **Neu §6a — der zweite Eingang.** Ein Silo kann nicht nur bestellbar sein (Zettel, Empfang entscheidet), sondern auch greifbar (Werkzeug, das Modell entscheidet mitten im Denken). **Das ist keine Erweiterung dieser Konvention, sondern die Rückkehr der Hälfte, die §1 ausklammert** — dort steht, dass das etablierte Protokoll die Auswahl *model-controlled* lässt und NMCP die andere Hälfte ist. Drei Rollen, unterschieden nach **wer entscheidet und wann**: Quelle (niemand), Zettel (Empfang), Werkzeug (Modell). **Drei Regeln daraus, alle vor dem ersten Bau geschrieben:** §6a.1 — ein Silo hat **einen** Dienst, die Eingänge sind zwei, die Implementierung eine; zwei Suchen über denselben Bestand ergeben zwei Rangfolgen, die auseinanderlaufen. §6a.2 — **die vier Ausgänge überstehen den Werkzeug-Eingang nicht von selbst**: Ein Werkzeug gibt eine Zeichenkette zurück, und damit wird aus *begründet abgelehnt* und *nichts gefunden* dieselbe leere Antwort; der Ausgang gehört benannt in den Text. §6a.3 — **der Handshake hat auf dem Werkzeug-Weg kein Gegenüber**: Zwei Auflösungen sind vertretbar, und welche gilt, gehört an den Aushang, nicht in den Code. Dazu in §9 die **Rollenmatrix** als Startprüfung mit Meldung statt Verweigerung — gemessen am 19.08.2026 trägt von neun Silos genau eines alle drei Rollen (Timeline), und das am schlechtesten angebundene ist ihr eigenes erarbeitetes Wissen mit nur einer.
- **v0.4 — 17.08.2026:** **Das schwarze Brett** (§3.6) — der Empfang nimmt bei jeder Äußerung das ganze Brett zur Hand, liest Zettel für Zettel und entscheidet je Zettel. **Er beurteilt keinen Zettel im Verhältnis zu einem anderen**, und der Grund liegt im Bild selbst: Ein Zettel ist für einen Leser geschrieben, der die anderen nicht kennt. Vier Folgen, jede eine Abweichung vom üblichen Routing: kein Vergleich und keine Rangliste; **mehrere Zusagen sind der Normalfall, nicht der Konflikt** (weshalb die Quotensumme über 100 % liegen darf); eine echte Doppelung wird als Negativfall **am Zettel** aufgelöst, weil der Dienst seinen Nachbarn kennt und der Empfang nicht; und gleichzeitiges Schreiben verhindert das Clipboard über die Reihenfolge, nicht die Auswahl. **Neu §5.6a, und ohne diesen Absatz kippte §5.6 ins Gegenteil:** Die vier Prüfungen über die Menge erzeugen eine **Meldung an den Autor** und niemals eine Regel für den Empfang — *die Registrierung darf über die Menge urteilen, um Zettel zu verbessern, nicht um Zustellungen zu entscheiden.* **Der Zeitpunkt entlastet dabei nicht:** eine bei der Registrierung berechnete Rangfolge ist zur Laufzeit dieselbe zentrale Zuordnungstabelle. Deshalb stehen alle vier unter *gemeldet* und keine unter *verweigert*. **Neu §3.6a mit einer benannten Schwäche:** Liegen alle Zettel in einem Modellaufruf, wägt das Modell sie unvermeidlich gegeneinander ab — die Unabhängigkeit ist dann eine Anweisung im Prompt und keine Eigenschaft des Aufbaus. Dazu der Zeuge, der sie prüfbar macht: **ein Zettel allein, dann derselbe neben einem zweiten — ändert sich das Urteil, ist die Unabhängigkeit verletzt**, und die Zahl dieser Fälle ist das Maß. Neu die Verstoßformen 8.7a (Verhältniswissen im Empfang, gleich wann gebildet) und 8.7b (Urteil nicht unabhängig). Drei erwogene Alternativen ergänzt, darunter der Aufruf je Zettel: strukturell unabhängig, teuer, und erneut zu bewerten, wenn die Gegenprobe schlecht ausfällt.
- **v0.3 — 17.08.2026:** **Der Handshake ist als Registrierungsvorgang ausgebaut, und der Aufruf danach ist trivial** — Auftrag hinein, Antwort heraus (§5.5). Das ist der Ertrag der ganzen Bauart und der Grund, sie überhaupt zu haben: Alle Kosten liegen dort, wo etwas noch **verweigern** kann; zur Laufzeit kann niemand mehr nein sagen, ohne das Gespräch anzuhalten. Der Begriff **Naht** ist als allgemeiner Übergang zwischen zwei Modulen gefasst und ausdrücklich mit dem Skalenfall zusammengeführt (`novaberg-haltungsraum_k.md` §6) — dieselbe Regel an einer Zahlengrenze. Fünf Ergänzungen: **§5.6** nutzt den Zeitpunkt, an dem der Empfang als einziger alle Dienste zugleich sieht — Quotensumme, überlappende Aushänge ohne Negativfall, gleicher Bedarf mit verschiedener Bedeutung, Kanal ohne Gegenstück; vier Prüfungen vor dem ersten Durchlauf. **§5.7** die **Naht-Signatur** über die vier Teile jeder Zusage, bei jedem Start neu gebildet: Sie fängt den wahrscheinlichsten Verfall, nämlich einen Schlüssel, der seinen Namen behält und seine Bedeutung ändert — die Änderung, die kein Typprüfer sieht. **§5.8** die Prüfliste, mit der Zeile, die §5 an §4 bindet: **Die Zweifelsregel setzt den vierten Ausgang voraus**, weil ein Dienst ohne begründete Ablehnung ausführt statt zu beurteilen; ohne ihn keine Zweifelsfälle. **§5.9** drei Grade — verweigert, eingeschränkt, gemeldet —, die Ablehnung trifft den Dienst und nicht das System, sie bleibt zur Laufzeit sichtbar statt nur beim Hochlauf, und ein fremder Dienst ohne Quote bekommt sie **erhoben** statt verweigert. **§5.10** die benannte Grenze: geprüft wird die Form der Zusage, nicht der Umgang mit dem Wert. Ein Handshake, der Vertrauen verspricht, verspricht zu viel. Dazu in §5.5 die Schranke für die Zahl der Rückfragen je Auftrag — ohne sie hat ein Auftrag keinen Endzustand, und ein Transport mit nur einem Austausch macht das Rückfrage-Tor unbaubar.
- **v0.2 — 17.08.2026:** **Die Quote und ihr Abgleich** (§4.4 bis §4.9) — aus der Messgröße in §4.2 ist ein Mechanismus geworden. Der Dienst nennt bei der Anmeldung eine geschätzte Quote auf einer Fünf-Stufen-Skala, der Empfang zählt die Zustellungen, der Abgleich meldet. **Der tragende Grund ist nicht die Zahl, sondern die Widerlegbarkeit:** Die Quote gibt jedem Aushang einen Leser, der ihm widersprechen kann — und behebt damit strukturell die Klasse aus §8.2, an der im Bestand ein Geltungsbereich vier Monate unbemerkt verrottete. Vier Entscheidungen darin sind gerechnet oder aus einer Messung begründet, nicht gesetzt: **Die Schwellen sind Verhältnisse, keine Differenzen** (0,75–1,33 Warnung, 0,5–2,0 Fehler), weil eine Differenz dieselbe Verwechslung zweier Nachbarstufen je nach Richtung verschieden beurteilt. **Die Mindest-Stichprobe ist gerechnet** — 16 Durchläufe für die halbe, 62 für die Viertel-Abweichung im ungünstigsten Fall, gesetzt auf 30 und 100. **Der Nenner ist je Graph getrennt**, weil an einem Tag Betrieb 49 von 122 Durchläufen eigene Impulse waren und die Impulsrate keinem Fachdienst gehört. **Gezählt wird die Zustellung, nicht der Erfolg** — die Differenz zu `bearbeitet` ist ein eigener Befund und kein Routing-Problem. Neu dazu §4.9, die Diagnose nach Abweichungsrichtung, deren letzte Zeile den Abgleich mit dem vierten Ausgang verbindet: Quote trifft und Ablehnungsquote hoch heißt richtiger Aushang und falsche Grenzangabe. Neu die Verstoßformen 8.2a (Aushang ohne Quote) und 8.2b (Abgleich unter der Mindest-Stichprobe — ein zu früher Alarm nimmt den Mechanismus mit). **Offen gelassen:** ob die untere Schranke enger gehört als die obere, weil die Untererfüllung nach §4.2 der teurere Fall ist.
- **v0.1 — 17.08.2026:** Erstfassung. Setzt das Soll für einen Mechanismus, von dem nichts gebaut ist — der Zustandsteil steht dafür im Kasten vor §1 und in §9. Neu gegenüber dem Bestand sind fünf Regeln: die **Sprachbedingung** des Aushangs (keine Fachsprache, weil der Empfang sie nicht kennen darf, §3.2), die **Zustellung im Zweifel** samt asymmetrischen Fehlerkosten und der Aufrufzahl als Messgröße (§4), der **Handshake** über Bedarf und zugesagte Fundstelle mit ihren vier Teilen (§5.1, §5.2), der **Zuschnitt des Zustands nach Lieferfähigkeit** (§5.4) und der **vierte Ausgang mit Korrekturvorschlag** (§6.7, §6.8). Übernommen und nur geschärft: die Sprachrichtung der Selbstauskunft und das Clipboard-Prinzip aus `novaberg-convention-planner-needs.md`. **§5.3 grenzt den Handshake ausdrücklich gegen die verworfene Laufzeit-Auflösung ab** — er läuft einmal beim Anmelden, sein Ergebnis ist eine feste Naht, und er lässt die Regel unangetastet, dass die Werteübernahme Code und keine Inferenz ist.
