"""Haltungsraum — aus Landschaft und Zuwendung folgen fuenf Verhaltensgroessen.

Die Lage sagt, was allgemein angemessen ist; der Charakter sagt, wie *diese*
Nova es tut. Der Cluster setzt Grundwerte, das Zuwendungsrad modifiziert sie.

Konzept: novaberg-haltungsraum_k.md §2. Die Zahlen in diesem Modul sind die
**Ausgangswerte** aus §2.0 — gesetzt, um gemessen zu werden, nicht als
Ergebnis. Ihre Justierung folgt aus Messreihen.

Drei Rechenarten, und welche gilt, steht an der Zelle:

  Neigung        addiert       der Charakter verschiebt den Wert
  Grenze         multipliziert der Charakter bleibt darin, null bleibt null
  Uebersteuerung hebt die Grenze auf und addiert wie eine Neigung

Eine Uebersteuerung greift nur bei **voller** Auspraegung der ausloesenden
Speiche. Bei halber wirkt ihr Beitrag als gewoehnliche Neigung — und gegen
eine Grenze damit gar nicht.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger("ki_server.ei.haltung")


# ─────────────────────────────────────────────
# Kanon der Groessen
# ─────────────────────────────────────────────
# Geschlossene Wertemenge. Sie existiert als Konstante, damit eine Zelle
# gegen sie pruefbar ist statt nur benutzbar — ein unbekannter Groessenname
# waere sonst von einem fehlenden Beitrag nicht zu unterscheiden.
GROESSEN: tuple[str, ...] = ("umfang", "fragen", "naehe", "waerme", "draengen")

# Zielspanne je Groesse. 0 = ein Satz · keine Fragen · distanziert · sachlich
# · zurueckhaltend. Sie wird geprueft und **nicht erzwungen**: Ob die Beitraege
# verkleinert oder auf die Summe gesaettigt werden, ist offen
# (novaberg-haltungsraum_k.md §6). Bis dahin ist ein Ueberlauf ein Befund, den
# die Messreihe zaehlt — kappen wuerde ihn unsichtbar machen.
GROESSE_MIN: float = 0.0
GROESSE_MAX: float = 1.0


# ─────────────────────────────────────────────
# Grundwerte je Landschaft
# ─────────────────────────────────────────────
# Die Spalte `fragen` ist nicht gesetzt, sondern aus CLUSTER_FRAGE_MENGE
# (ei/dreischicht.py) uebersetzt: "Mittel" -> 0.45, "Keine" -> 0.0.
# Wer dort etwas aendert, aendert hier mit.
#
# **Am 27.08.2026 halbiert** — Setzung des Meisters, keine Messung: Die
# Rueckfragen-Haeufigkeit war zu hoch. Halbiert ist ausschliesslich diese
# Spalte; `SPEICHEN_BEITRAG` bleibt unangetastet, obwohl das Rad im Betrieb
# rund +0,38 auf `fragen` legt und damit nach der Halbierung den groesseren
# Anteil am Ergebnis traegt. Die Begruendung und der Preis stehen bei
# CLUSTER_FRAGE_MENGE.
CLUSTER_GRUNDWERT: dict[str, dict[str, float]] = {
    "feuerwerk": {
        "umfang": 0.80, "fragen": 0.45, "naehe": 0.90,
        "waerme": 0.90, "draengen": 0.70,
    },
    "kissenschlacht": {
        "umfang": 0.30, "fragen": 0.30, "naehe": 0.80,
        "waerme": 0.90, "draengen": 0.50,
    },
    "werkstatt": {
        "umfang": 0.90, "fragen": 0.45, "naehe": 0.50,
        "waerme": 0.50, "draengen": 0.70,
    },
    "glut": {
        "umfang": 0.70, "fragen": 0.15, "naehe": 0.90,
        "waerme": 0.80, "draengen": 0.20,
    },
    "bier": {
        "umfang": 0.50, "fragen": 0.25, "naehe": 0.80,
        "waerme": 0.80, "draengen": 0.30,
    },
    "foyer": {
        "umfang": 0.70, "fragen": 0.25, "naehe": 0.30,
        "waerme": 0.50, "draengen": 0.30,
    },
    "regen": {
        "umfang": 0.20, "fragen": 0.07, "naehe": 0.80,
        "waerme": 0.90, "draengen": 0.00,
    },
    "schmollen": {
        "umfang": 0.20, "fragen": 0.07, "naehe": 0.60,
        "waerme": 0.60, "draengen": 0.00,
    },
    "nebel": {
        "umfang": 0.15, "fragen": 0.00, "naehe": 0.50,
        "waerme": 0.60, "draengen": 0.00,
    },
    "gewitter": {
        "umfang": 0.30, "fragen": 0.00, "naehe": 0.20,
        "waerme": 0.20, "draengen": 0.20,
    },
    "schlachtfeld": {
        "umfang": 0.15, "fragen": 0.15, "naehe": 0.20,
        "waerme": 0.20, "draengen": 0.80,
    },
    "beichte": {
        "umfang": 0.20, "fragen": 0.15, "naehe": 0.95,
        "waerme": 0.90, "draengen": 0.00,
    },
    "wartezimmer": {
        "umfang": 0.30, "fragen": 0.25, "naehe": 0.20,
        "waerme": 0.50, "draengen": 0.20,
    },
    "paradox": {
        "umfang": 0.20, "fragen": 0.00, "naehe": 0.30,
        "waerme": 0.50, "draengen": 0.00,
    },
}

# Welche Zelle eine **Grenze** ist statt einer Neigung. Abgelesen aus den
# Beschreibungen in CLUSTER_BESCHREIBUNGEN, wo sie woertlich stehen:
# "Nicht draengen", "Halten, da sein", "Keine — Spiegelung, keine Fragen".
# Alles, was hier nicht steht, ist eine Neigung.
CLUSTER_GRENZE: dict[str, frozenset[str]] = {
    "regen":        frozenset({"draengen"}),
    "schmollen":    frozenset({"draengen"}),
    "nebel":        frozenset({"fragen", "draengen"}),
    "gewitter":     frozenset({"fragen"}),
    "beichte":      frozenset({"draengen"}),
    "paradox":      frozenset({"fragen", "draengen"}),
}


# ─────────────────────────────────────────────
# Beitrag je Speiche
# ─────────────────────────────────────────────
# Werte bei voller Auspraegung (1.0); halbe Auspraegung wirkt halb. Jede Zeile
# folgt der eigenen Beschreibung ihrer Speiche (novaberg-salienz-berechnung_k.md
# §5): `dienst` "sucht von sich aus Gelegenheiten" draengt und redet mehr,
# `pflicht` "nimmt Auftraege ernst" arbeitet ab statt zu fragen.
SPEICHEN_BEITRAG: dict[str, dict[str, float]] = {
    "treue": {"naehe": 0.20, "waerme": 0.10, "draengen": -0.30},
    "dienst": {"umfang": 0.20, "draengen": 0.30},
    "pflicht": {"umfang": 0.20, "fragen": -0.20, "draengen": 0.10},
    "aufmerksamkeit": {"fragen": 0.20, "naehe": 0.20},
    # Kein Beitrag auf `umfang`. Gestrichen am 08.08.2026 nach der Definition
    # beider Groessen: `umfang` ist die Laenge von Novas eigenem Text, und
    # `wissbegier` heisst „fremde Themen wecken echtes Interesse" — eine
    # rezeptive Disposition. Interesse an dem, was der andere bringt, aeussert
    # sich darin, sich ihm zuzuwenden, nicht darin, den Raum zu fuellen. Der
    # Kanal dafuer steht eine Spalte weiter: `fragen` +0.40, dazu eine von nur
    # zwei Uebersteuerungen im ganzen System.
    #
    # Sie senkt den Umfang auch nicht: „Raum lassen" ein zweites Mal zu
    # kodieren, waere derselbe Fehler mit umgekehrtem Vorzeichen. Eine ruhige,
    # gespannt zuhoerende Nova stellt kurze Fragen — das leistet die
    # Fragenspalte, und der Verfasser bekommt ueber den Umfang ohnehin weniger
    # Material.
    #
    # Der Gegenpol bleibt: `langeweile` traegt `umfang -0.40`, und dieser Weg
    # ist direkt — kein Interesse, also nichts zu sagen, „Hmmm... ja."
    # **Die Tabelle ist nicht als Spiegelpaare gebaut** (`treue` hat keinen
    # Umfangsbeitrag, ihr Gegenpol `selbstbezogen` +0.10), also verlangt der
    # eine Wert den anderen nicht.
    "wissbegier": {"fragen": 0.40, "draengen": 0.20},
    "wohlwollen": {"naehe": 0.10, "waerme": 0.40},
    "selbstbezogen": {"umfang": 0.10, "fragen": -0.20, "naehe": -0.30, "draengen": 0.30},
    "gleichgueltig": {"umfang": -0.30, "fragen": -0.20, "naehe": -0.20, "waerme": -0.40},
    "widerspenstig": {"waerme": -0.30, "draengen": 0.30},
    "distanz": {"umfang": -0.30, "naehe": -0.50, "waerme": -0.20},
    "langeweile": {"umfang": -0.40, "fragen": -0.30, "waerme": -0.20, "draengen": -0.20},
    "misstrauen": {"fragen": 0.10, "naehe": -0.20, "waerme": -0.40},
}

# Welche Speichen bei extremem Ausschlag **ziehen** duerfen — die Lage also
# ueberstimmen statt sie nur zu verschieben.
#
# **Eine Liste, keine Abbildung** (11.08.2026). Bis dahin stand hier je
# Speiche **eine** Groesse. Das war eine zweite Tabelle neben
# `SPEICHEN_BEITRAG`, die dieselbe Frage schon beantwortet — und schlechter,
# weil eine Speiche auf mehrere Groessen traegt. Der Zug fliesst jetzt durch
# die Zeile der Speiche in `SPEICHEN_BEITRAG`, in ihren eigenen
# Verhaeltnissen; hier steht nur noch, **wer** ziehen darf.
#
# **Das Kriterium: Ziehen darf, was sich abwendet — nicht, was sich
# zuwendet.** Die Landschaft *ist* die Lage des Anderen. Eine Speiche, die
# "ich wende mich dir zu" bedeutet, kann nicht zugleich sagen, ihr sei
# gleich, was diese Lage verlangt: Waerme, die die Lage ueberstimmt, ist
# nicht mehr Waerme, sondern weniger Abstimmung. Eine Speiche, die "ich bin
# bei mir" bedeutet, kann das sehr wohl — sie beschreibt einen Zustand, der
# den Anderen aus dem Blick nimmt.
#
#     distanz         Rueckzug, Zumachen — der Rueckzug ist die Reaktion
#     misstrauen      Wachsamkeit statt Begegnung (Konzept §3.2 verlangt es
#                     woertlich: "soll sich nicht mit Wohlwollen verrechnen
#                     lassen, es soll die Rechnung beenden" — und genau das
#                     tat es nicht: `misstrauen -0.40` und `wohlwollen +0.40`
#                     auf `waerme` heben sich exakt auf)
#     gleichgueltig   der Andere zaehlt nicht — affektive Abflachung
#     langeweile      das Thema zaehlt nicht — Disengagement
#     widerspenstig   Gegenhalten als Haltung — Reaktanz
#     selbstbezogen   nur noch die eigene Sicht — Selbstabsorption
#
# Draussen bleibt die **ganze** Zuwendungsseite: `aufmerksamkeit`,
# `wohlwollen`, `treue`, `dienst`, `pflicht` — und seit dem 12.08.2026 auch
# `wissbegier`. Bei `dienst` und `pflicht` ist das Argument am schaerfsten:
# Im `regen` steht "nicht draengen", und der Helfer, der es doch tut, ist der
# Fehler und nicht die Ausnahme.
#
# **`wissbegier` war die eine zugelassene Ausnahme und ist gestrichen** —
# gemessen und dann entschieden. Sie zog beim produktiven Paar in **14 von
# 14** Landschaften, weil der Wert bei 0.97 steht und damit dauerhaft ueber
# der Schwelle liegt; `fragen` fiel dort in keiner Landschaft unter 0.50,
# auch nicht in `nebel`, `gewitter` und `paradox`, wo die Landschaft eine
# Grenze bei 0.00 setzt. Das Konzept nennt als Kriterium: »Ein
# Ausnahmezustand, der in jedem zweiten Turn eintritt, ist keiner.«
#
# **Der Grund ist nicht die Schwelle, sondern die Art der Groesse.**
# Wissbegier ist das *Ergebnis* einer Eigenschaft und kein Zustand, der
# ueberstimmt — deshalb kein Zug bei Extremen. Der Zug ist fuer Zustaende
# gebaut: Rueckzug, Wachsamkeit, Reaktanz. Wer dauerhaft neugierig ist,
# zoege dauerhaft, und keine Schwelle unterhalb des gemessenen Wertes
# aenderte daran etwas.
#
# **Die naheliegende Gegenerklaerung ist geprueft und traegt nicht:** Der
# hohe Wert ist kein Artefakt des Gespraechsthemas. Die Profile beschreiben
# Denkart statt Themen, und ueber drei Paare mit derselben Messanordnung
# liegt `wissbegier` bei 0.97, 0.86 und 0.83.
#
# **Gemessen, drei Paare mit offenem Profil und freiem Rad (12.08.2026):**
# Jedes Paar traegt Speichen ueber der Schwelle — bei den beiden Personas
# `aufmerksamkeit` 0.98, `treue` 0.95 und `wohlwollen` 0.95, alle drei von
# diesem Kriterium ausgeschlossen. Ohne es haetten alle drei Paare
# Dauerzuege. Die sechs verbliebenen Speichen erreichen die Schwelle in
# keinem Paar; Novas hoechste ist `distanz` mit 0.38. **Der Zug ist damit
# heute in 0 von 14 Landschaften aktiv** — und steht bereit fuer den Tag,
# an dem ein Gespraech wirklich in einen Abwendungszustand laeuft.
UEBERSTEUERUNG_SPEICHEN: frozenset[str] = frozenset({
    "distanz", "misstrauen", "gleichgueltig", "langeweile",
    "widerspenstig", "selbstbezogen",
})

# Ab dieser Auspraegung greift eine Uebersteuerung. Darunter wirkt der Beitrag
# der Speiche als gewoehnliche Neigung — gegen eine Grenze also gar nicht.
#
# **Nachgeeicht am 11.08.2026 von 1.0 auf 0.8, weil die Skala darunter eine
# andere geworden ist.** Der Wert stammt aus der Zeit der Dreierskala, in der
# 1.0 eine der drei erlaubten Ausprägungen war und entsprechend haeufig fiel.
# Seit `F-RAD-3` wurde auf eine Nachkommastelle erhoben, und eine exakte 1.0
# ist dort ein Eckfall. Gemessen ueber alle Laeufe des Zuwendungsrades:
#
#     grobe Skala, 50 Laeufe   distanz >= 1.0 in 54 %, wissbegier in 52 %
#     feine Skala, 30 Laeufe   distanz >= 1.0 in  3 %, wissbegier in  0 %
#
# Beide Uebersteuerungen waren damit praktisch abgeschaltet — ohne Meldung,
# ohne roten Test, weil die Tests die Schwelle symbolisch fuehren und nicht
# als Zahl. Genau die Klasse aus `22_STILLE_FEHLER.md`.
#
# Die Schwelle trennt dabei, was sie trennen soll: Das aktive Paar
# (`meister` <-> `nova`, distanz 0.0 bis 0.2) loest in 0 von 6 Laeufen aus,
# die distanzierten Personas in 3 bis 6 von 6. Sie steht auf 0.8, weil die
# Kurve darueber Raum braucht — die Begruendung dazu eine Konstante weiter
# unten.
#
# **Auf Novas Verhalten wirkt das heute noch nicht** — die Haltung wird
# gerechnet, protokolliert und angezeigt, aber kein Prompt liest sie
# (`novaberg-haltungsraum_k.md` §3, offen). Der Wert muss trotzdem stimmen,
# bevor der Prompt-Block kommt: Sonst startet die erste Messreihe ueber
# Novas Verhalten auf einer Schwelle, die nie ausloest.
#
# **Auf 0.9 gesetzt, nachdem das Raster gefallen war** (11.08.2026, spät).
# Die 0.8 war ein Notbehelf: Solange die Prompts »auf eine Nachkommastelle«
# verlangten, war oberhalb von 0.9 nur die 1.0 erreichbar, und die Kurve
# brauchte Raum darunter. Die Messung Raster gegen frei zeigt, warum das
# der falsche Ausweg gewesen wäre — **das Gitter hat `distanz` systematisch
# heruntergerundet:**
#
#     gerastert   0.9 · 0.9 · 0.9 · 0.9 · 0.9 · 0.9        (beide Paare)
#     frei        0.93 · 0.91 · 0.91 · 0.95 · 0.96 · 0.86   (mehmet)
#                 0.93 · 0.943 · 0.96 · 0.94 · 0.94 · 0.95  (sarah)
#
# Der wahre Wert liegt bei 0.93 bis 0.96. Auf dem Gitter war er nicht
# darstellbar, und deshalb sah 0.9 aus wie eine Schwelle, die nie ausloest.
# Ziehende Speichen je Lauf, ueber 12 freie Laeufe zweier Paare:
#
#     Schwelle 0.8    2.0 bis 2.5 je Lauf   — kein Ausnahmezustand mehr
#     Schwelle 0.9    0.8 bis 1.2 je Lauf   — je Rad etwa eine
#
# **Und sie trennt, auch ohne Raster.** Das aktive Paar `nova -> meister`,
# drei freie Laeufe am selben Abend: `distanz` 0.11 / 0.063 / 0.03 gegen
# 0.86 bis 0.96 bei den beiden Personas. Keine Ueberschneidung, und die
# Null war keine Rundung — sie ist mit Aufloesung eine kleine Zahl
# geblieben. Die Schwelle 0.9 loest bei den Personas aus und beim aktiven
# Paar in keinem Lauf.
UEBERSTEUERUNG_AB: float = 0.9

# Die Steilheit der Uebersteuerungskurve.
#
# **Kein Sprung, sondern ein Zug.** Bis zum 11.08.2026 war die
# Uebersteuerung ein Umschalten der Rechenart und aenderte fuer eine
# Neigungszelle keine einzige Zahl. Statt zu **ersetzen** zieht sie jetzt:
# Ueber der Schwelle liefert `uebersteuerungs_zug` einen Betrag zwischen 0
# und 1, der auf das Ergebnis der Zelle addiert oder von ihm abgezogen wird
# — in der Richtung, in die die ausloesende Speiche ohnehin traegt.
#
# **Die Begruendung ist die Natur der Sache:** Ein Wesen kennt selten nur 0
# und 1. Ein extremer Ausschlag soll seinen Gegenpol niederziehen, aber
# graduell — bei knapper Ueberschreitung kaum, bei voller Auspraegung ganz.
#
# Der Exponent 2 macht die Kurve lange flach und dann steil. Mit der
# Schwelle 0.9 trifft sie die entworfene Form fast genau — verlangt waren
# rund ein halber Zug bei 0.97 und der ganze bei 1.0:
#
#     Auspraegung   0.90   0.93   0.95   0.97   1.00
#     Zug           0.00   0.09   0.25   0.49   1.00
#
# Auf den gemessenen `distanz`-Werten der beiden Personas (0.93 bis 0.96)
# liegt der Zug damit zwischen 0.09 und 0.36: spuerbar, aber nicht am
# Anschlag. Der volle Zug bleibt dem vollen Ausschlag vorbehalten.
UEBERSTEUERUNG_EXPONENT: float = 2.0


@dataclass(frozen=True)
class Groessenwert:
    """Eine der fuenf Verhaltensgroessen, mit ihrer Herkunft.

    Drei Zahlen statt einer: Ohne Grundwert und Modifikation ist am Ergebnis
    nicht erkennbar, ob die Landschaft den Wert gesetzt oder der Charakter ihn
    verschoben hat (Konzept §3.1).

    Attributes:
        name:         Groessenname aus GROESSEN.
        grundwert:    was die Landschaft vorgibt.
        modifikation: Summe der Speichenbeitraege, vorzeichenbehaftet.
        ergebnis:     der verrechnete Wert.
        art:          "neigung", "grenze" oder "uebersteuerung".
        ausloeser:    bei Uebersteuerung die Speiche, sonst "".
        ausserhalb:   True, wenn `ergebnis` die Zielspanne verlaesst.
    """

    name:         str
    grundwert:    float
    modifikation: float
    ergebnis:     float
    art:          str
    ausloeser:    str
    ausserhalb:   bool


@dataclass(frozen=True)
class Haltung:
    """Das Ergebnis einer Haltungsrechnung fuer einen Turn.

    Attributes:
        cluster: die Landschaft, aus der die Grundwerte stammen.
        werte:   je Groessenname ein Groessenwert, vollstaendig ueber GROESSEN.
    """

    cluster: str
    werte:   dict[str, Groessenwert]

    def kurzfassung(self) -> str:
        """Eine Zeile fuer die Spur — lesbar ohne Umweg ueber das Protokoll."""
        teile: list[str] = []
        for name in GROESSEN:
            wert: Groessenwert = self.werte[name]
            stueck: str = f"{name} {wert.ergebnis:.2f}"
            if wert.art == "uebersteuerung":
                stueck += f" UEBERSTEUERT ({wert.ausloeser})"
            elif wert.art == "grenze":
                stueck += " [Grenze]"
            if wert.ausserhalb:
                stueck += " !"
            teile.append(stueck)
        return f"{self.cluster} · " + " · ".join(teile)


def speichen_spanne(groesse: str) -> tuple[float, float]:
    """Die Spanne, die die Radsumme einer Groesse ueberhaupt annehmen kann.

    **Der benannte Abbildungsfaktor der Naht.** Landschaft und Rad sprechen
    zwei verschiedene Skalen: Der Grundwert liegt in [0, 1], die Radsumme in
    einer Spanne, die sich aus `SPEICHEN_BEITRAG` ergibt und nirgends stand.
    Sie einfach zu addieren heisst, zwei Einheiten gleichzusetzen, die nicht
    dieselben sind — gemessen am 08.08.2026 verliess dabei **jede** der 62
    Nicht-Grenz-Zellen die Spanne an mindestens einem Ende.

    Der Faktor wird **abgeleitet, nicht gesetzt**: Er ist die Summe der
    positiven und die Summe der negativen Beitraege bei voller Auspraegung.
    Damit wandert er mit der Tabelle mit, statt neben ihr zu veralten — eine
    neue Speiche aendert ihn, ohne dass jemand daran denken muss.

    Args:
        groesse: eine der GROESSEN.

    Returns:
        (kleinstmoegliche Summe, groesstmoegliche Summe). Beide Werte sind
        vorzeichenrichtig; die erste ist <= 0, die zweite >= 0.
    """
    positiv: float = sum(
        max(beitraege.get(groesse, 0.0), 0.0) for beitraege in SPEICHEN_BEITRAG.values()
    )
    negativ: float = sum(
        min(beitraege.get(groesse, 0.0), 0.0) for beitraege in SPEICHEN_BEITRAG.values()
    )
    return negativ, positiv


def _normieren(summe: float, groesse: str) -> float:
    """Bildet die Radsumme auf [-1, +1] ab, je Richtung auf ihre eigene Spanne.

    **Getrennt je Richtung, nicht ueber die Gesamtbreite.** Die Beitraege sind
    unsymmetrisch — `waerme` reicht von -1.50 bis +0.50 —, und eine gemeinsame
    Normierung wuerde die schwaechere Richtung stauchen: Ein Rad, das die
    Waerme so weit hebt, wie die Tabelle es zulaesst, kaeme nur auf +0.25 statt
    auf +1. Die volle Auspraegung einer Richtung muss ihr volles Ergebnis
    liefern, sonst ist ein Teil der Tabelle unerreichbar.

    Vorbedingung: `groesse` ist eine der GROESSEN.
    Nachbedingung: Rueckgabe in [-1, +1]; 0.0 genau dann, wenn die Summe 0 ist.
    Fehlerfaelle: Eine Spanne von 0 in der beanspruchten Richtung bedeutet,
        dass keine Speiche dorthin zieht — dann ist eine Summe in dieser
        Richtung ein Defekt der Tabelle und wird laut gemeldet.
    """
    if summe == 0.0:
        return 0.0

    negativ, positiv = speichen_spanne(groesse)
    grenze: float = positiv if summe > 0 else -negativ

    if grenze <= 0.0:
        logger.error(
            f"Haltung: Radsumme {summe:+.2f} auf {groesse!r}, aber keine "
            f"Speiche zieht in diese Richtung (Spanne {negativ:+.2f}..{positiv:+.2f}) "
            "— die Normierung ist nicht moeglich, der Beitrag entfaellt"
        )
        return 0.0

    return summe / grenze


def _modifikation(rad: dict[str, float], groesse: str) -> float:
    """Summiert die Speichenbeitraege einer Groesse.

    Erst summieren, dann verrechnen: Die Reihenfolge der Speichen darf das
    Ergebnis nicht bestimmen.

    Vorbedingung: `rad` enthaelt nur bekannte Speichennamen und Auspraegungen
    in [0.0, 1.0]. Pruefung erfolgt beim Aufrufer (`haltung_berechnen`).
    Nachbedingung: Summe der beteiligten Beitraege, Vorzeichen erhalten.
    """
    return sum(
        SPEICHEN_BEITRAG.get(speiche, {}).get(groesse, 0.0) * auspraegung
        for speiche, auspraegung in rad.items()
    )


def uebersteuerungs_zug(auspraegung: float) -> float:
    """Wie stark eine Speiche ueber der Schwelle ihre Groesse an den Anschlag zieht.

    Null unterhalb und **genau auf** der Schwelle, eins bei voller
    Auspraegung, dazwischen die Potenzkurve mit `UEBERSTEUERUNG_EXPONENT`.

    **Stetig an der Schwelle, und das ist der Zweck.** Ein Schwellenwert, der
    einen Sprung von 0 auf 1 ausloest, macht aus einer Zehntelstelle im
    Modellurteil einen Zustandswechsel im Verhalten — genau die Haerte, die
    das Rad mit der feinen Skala loswerden sollte.

    Vorbedingung: `auspraegung` in [0.0, 1.0]. Ausserhalb ist ein Defekt des
        Aufrufers und wird laut gemeldet, nicht stillschweigend geklemmt.
    Nachbedingung: Rueckgabe in [0.0, 1.0]; 0.0 genau dann, wenn die
        Auspraegung die Schwelle nicht ueberschreitet.
    """
    if not 0.0 <= auspraegung <= 1.0:
        raise ValueError(
            f"uebersteuerungs_zug: Auspraegung {auspraegung} liegt ausserhalb "
            "[0.0, 1.0] — das Rad ist an seiner Eingabegrenze zu pruefen"
        )
    if auspraegung <= UEBERSTEUERUNG_AB:
        return 0.0
    anteil: float = (auspraegung - UEBERSTEUERUNG_AB) / (1.0 - UEBERSTEUERUNG_AB)
    return anteil ** UEBERSTEUERUNG_EXPONENT


def _uebersteuerer(rad: dict[str, float], groesse: str) -> tuple[str, float]:
    """Nennt die Speiche, die diese Groesse am staerksten zieht, und den Zug.

    Der Zug einer Speiche auf eine Groesse ist ihre Kurve, verteilt in den
    Verhaeltnissen ihrer eigenen Zeile in `SPEICHEN_BEITRAG`::

        zug = kurve(auspraegung) * beitrag[groesse] / max|beitrag der Zeile|

    Damit zieht sie dort voll, wo sie am staerksten traegt, und anteilig auf
    den uebrigen Groessen derselben Zeile — `distanz` nimmt die Naehe ganz,
    den Umfang zu 0.6 und die Waerme zu 0.4. Das Vorzeichen kommt aus dem
    Beitrag, nicht aus einer zweiten Setzung.

    **Bei mehreren zutreffenden gewinnt der staerkste Zug, sie summieren
    sich nicht.** Zwei gleichzeitige Ausnahmezustaende sind nicht doppelt so
    ausnahmehaft; der extremere bestimmt die Groesse. Summiert stuende
    ausserdem in `ausloeser` nur einer von zweien, und die Zeile logeine
    Ursache, die die Zahl nicht allein erklaert. Bei gleichem Betrag
    entscheidet der Name, damit die Auswahl deterministisch bleibt.

    **Echt groesser, nicht groesser-gleich.** Genau auf der Schwelle ist der
    Zug null (`uebersteuerungs_zug`), und eine Marke ohne Wirkung waere
    schlimmer als keine: Wie oft die Uebersteuerung greift, ist eine
    Messgroesse des Konzepts (§2) — eine Zeile, die »uebersteuerung« sagt
    und nichts verschoben hat, treibt sie nach oben.

    Vorbedingung: wie `_modifikation`.
    Nachbedingung: (Speichenname, Zug) mit Zug != 0.0, oder ("", 0.0).
    """
    beste: tuple[str, float] = ("", 0.0)
    for speiche in sorted(UEBERSTEUERUNG_SPEICHEN):
        auspraegung: float = rad.get(speiche, 0.0)
        if auspraegung <= UEBERSTEUERUNG_AB:
            continue
        zeile: dict[str, float] = SPEICHEN_BEITRAG[speiche]
        beitrag: float = zeile.get(groesse, 0.0)
        if beitrag == 0.0:
            continue
        staerkste: float = max(abs(wert) for wert in zeile.values())
        zug: float = uebersteuerungs_zug(auspraegung) * beitrag / staerkste
        if abs(zug) > abs(beste[1]):
            beste = (speiche, zug)
    return beste


def _rad_pruefen(rad: dict[str, float], cluster: str) -> str:
    """Prueft das Rad an der Eingabegrenze und nennt den Grund einer Ablehnung.

    Steht als eigene Funktion, weil eine Waechterkette die Zweigzahl ihres
    Aufrufers bestimmt und dort nichts erklaert: Der Rechenteil soll rechnen.
    Die Zahl der Rueckgaben ist die Zahl der Vorbedingungen und folgt dem
    Datenmodell.

    Args:
        rad:     Speichenname -> Auspraegung, ungeprueft.
        cluster: nur fuer die Fehlermeldung, damit sie den Fall benennt.

    Returns:
        Leere Zeichenkette, wenn das Rad brauchbar ist, sonst der Grund im
        Klartext — mit dem Wert, nicht nur dem Feldnamen.
    """
    for speiche, auspraegung in rad.items():
        if speiche not in SPEICHEN_BEITRAG:
            return (
                f"unbekannte Speiche {speiche!r} im Rad zu Cluster {cluster!r} — "
                f"erwartet werden {len(SPEICHEN_BEITRAG)} Namen"
            )
        # Ein Wahrheitswert ist in Python eine Zahl und schluepfte sonst durch.
        if isinstance(auspraegung, bool) or not isinstance(auspraegung, (int, float)):
            return (
                f"Auspraegung von {speiche!r} ist {auspraegung!r} "
                f"({type(auspraegung).__name__}), erwartet wird eine Zahl"
            )
        if not (0.0 <= float(auspraegung) <= 1.0):
            return (
                f"Auspraegung von {speiche!r} ist {auspraegung} und liegt "
                "ausserhalb [0.0, 1.0]"
            )
    return ""


def _verrechnen(grund: float, summe: float, art: str, groesse: str) -> float:
    """Verknuepft Grundwert und Modifikation nach der Rechenart der Zelle.

    Steht als eigene Funktion, weil sie sonst nicht pruefbar waere: Alle sechs
    Grenzen im heutigen Bestand tragen den Grundwert 0.00, und dort ist eine
    Multiplikation von "immer null" nicht zu unterscheiden. Hier laesst sie
    sich mit einem Grundwert groesser null pruefen.

    **Der Charakter wirkt auf den verbleibenden Weg, nicht auf den Wert.**
    Bis zum 08.08.2026 wurde addiert: `grund + summe`. Das setzt zwei Skalen
    gleich, die es nicht sind, und verliess ueber die volle Charakterspanne in
    **62 von 62** Zellen die Spanne [0, 1]. Gekappt wurde nicht, und das war
    richtig — Kappen erzeugt genau die toten Enden, die der Raum nicht haben
    darf: Zwei Landschaften, die oben anstossen, sind nicht mehr zu
    unterscheiden.

    Die Wegform loest beides ohne Kappen::

        n > 0:  ergebnis = grund + n * (1 - grund)      # Weg nach oben
        n < 0:  ergebnis = grund + n * grund            # Weg nach unten

    Vier Eigenschaften, jede einzeln pruefbar:

      * **Geschlossen** — das Ergebnis liegt in [0, 1] durch Konstruktion.
      * **Ordnungserhaltend** — die Ableitung nach dem Grundwert ist (1 - n)
        beziehungsweise (1 + n) und damit positiv; zwei Landschaften fallen
        unter keinem Charakter zusammen.
      * **Keine geschlossene Tuer** — 1.0 nur bei n = 1 exakt, 0.0 nur bei
        n = -1 exakt. Der Charakter verschiebt, er schliesst nicht
        (`novaberg-gv-initiative_k.md` §8, hier als Rechenform statt als
        Absicht).
      * **Neutral** — n = 0 gibt den Grundwert zurueck. Die Gegenprobe: ein
        Rad auf der Nabe reproduziert die Landschaft exakt.

    **Die Grenze behaelt ihre multiplikative Form**, und das ist Absicht: Sie
    ist das eine gewollte tote Ende — in `gewitter` wird nicht gefragt. Die
    Wegform wuerde sie oeffnen, weil ein Grundwert von 0 dort vollen Weg nach
    oben haette. Ihre einzige Freigabe bleibt die Uebersteuerung.

    **Die Uebersteuerung ist hier keine Rechenart mehr** (11.08.2026). Sie
    ersetzte bis dahin die Art und lieferte damit fuer jede Neigungszelle
    exakt dieselbe Zahl wie ohne sie — sie war nur in Grenzzellen ueberhaupt
    unterscheidbar. Sie wirkt jetzt als **Zug nach der Rechnung**
    (`uebersteuerungs_zug`, angewandt in `haltung_berechnen`); diese
    Funktion kennt deshalb nur noch die zwei Arten der Zelle.

    Args:
        grund:   Grundwert der Landschaft, in [0, 1].
        summe:   rohe Radsumme, unnormiert.
        art:     "neigung" oder "grenze" — die Art der Zelle.
        groesse: fuer die Normierung — jede Groesse hat ihre eigene Spanne.

    Vorbedingung: `art` ist einer der beiden Werte. Pruefung erfolgt beim
        Aufrufer, der die Art selbst setzt.
    Nachbedingung: Bei "neigung" liegt das Ergebnis in [0, 1]. Bei "grenze"
        und einem Grundwert von null ist es null, gleich welche Summe
        anliegt.
    """
    n: float = _normieren(summe, groesse)

    if art == "grenze":
        # Multiplikativ: Der Charakter skaliert, was die Lage zulaesst — und
        # sie laesst hier nichts zu. Bei einem Grundwert ueber 0.5 koennte
        # diese Form die Spanne verlassen; im Bestand tragen alle Grenzzellen
        # 0.00, und ein Test haelt das fest.
        return grund * (1.0 + n)

    return grund + n * ((1.0 - grund) if n > 0 else grund)


def haltung_berechnen(cluster: str, rad: dict[str, float]) -> Haltung | None:
    """Rechnet aus Landschaft und Zuwendungsrad die fuenf Verhaltensgroessen.

    Reine Funktion ohne Datenzugriff: Der Aufrufer laedt Cluster und Rad und
    uebergibt sie (Schichtregel — rechnen und laden bleiben getrennt).

    Args:
        cluster: Landschaftsname, muss in CLUSTER_GRUNDWERT stehen.
        rad:     Speichenname -> Auspraegung in [0.0, 1.0]. Leere Raeder sind
                 zulaessig; dann bleibt es bei den Grundwerten.

    Returns:
        Eine `Haltung` mit einem Eintrag je Groesse aus GROESSEN, oder None,
        wenn eine Vorbedingung verletzt ist.

    Nachbedingung: Zielspanne je Ergebnis ist GROESSE_MIN bis GROESSE_MAX. Sie
        wird **geprueft und nicht erzwungen** — ein Ueberlauf wird gemeldet und
        im Ergebnis markiert (`ausserhalb`), nicht gekappt. Eine Kappung machte
        einen Rechenfehler von der bekannten offenen Frage zur oberen Grenze
        ununterscheidbar (Konzept §6).

    Fehlerfaelle:
        Unbekannter Cluster, unbekannte Speiche, Auspraegung ausserhalb
        [0.0, 1.0], nicht-numerische Auspraegung — je `logger.error` und None.
    """
    # ── Eingabe-Validierung ─────────────────────
    if cluster not in CLUSTER_GRUNDWERT:
        logger.error(
            f"Haltung: unbekannter Cluster {cluster!r} — bekannt sind "
            f"{len(CLUSTER_GRUNDWERT)} Landschaften, keine Berechnung"
        )
        return None

    grund_der_ablehnung: str = _rad_pruefen(rad, cluster)
    if grund_der_ablehnung:
        logger.error(f"Haltung: {grund_der_ablehnung} — keine Berechnung")
        return None

    # ── Verarbeitung ────────────────────────────
    grundwerte: dict[str, float] = CLUSTER_GRUNDWERT[cluster]
    grenzen:    frozenset[str]   = CLUSTER_GRENZE.get(cluster, frozenset())
    werte:      dict[str, Groessenwert] = {}

    for groesse in GROESSEN:
        grund:  float = grundwerte[groesse]
        summe:  float = _modifikation(rad, groesse)
        # **Nicht mehr auf Grenzzellen beschraenkt.** Bis zum 11.08.2026 stand
        # hier `if groesse in grenzen`, und weil `naehe` in keiner der
        # vierzehn Landschaften eine Grenze ist, war die Uebersteuerung
        # `distanz -> naehe` seit dem Bau in 0 von 14 Faellen erreichbar —
        # ohne Meldung, ohne roten Test. Das Konzept verlangt das Gegenteil:
        # »`distanz` uebersteuert die Naehe, gleich wie warm die Landschaft
        # ist« (`novaberg-haltungsraum_k.md` §2).
        traeger, zug = _uebersteuerer(rad, groesse)

        # Die Zellart bleibt, was die Landschaft sagt — die Uebersteuerung
        # ersetzt sie nicht, sie zieht danach. Eine Grenze haelt damit
        # weiterhin (multiplikativ, null bleibt null) und oeffnet sich nur
        # so weit, wie der Zug sie aufzieht.
        zellart: str = "grenze" if groesse in grenzen else "neigung"
        ergebnis: float = _verrechnen(grund, summe, zellart, groesse)
        art: str = zellart

        if traeger:
            art = "uebersteuerung"
            # **Der Zug geht den Weg, er wird nicht abgeschnitten.** Dieselbe
            # Form wie bei der Neigung, hier auf das fertige Ergebnis
            # angewandt: Der Zug nimmt den Anteil des Wegs, der in seiner
            # Richtung noch offen ist.
            #
            # Ein einfaches Abziehen mit `max(wert, 0)` waere naeher an der
            # Anschauung und ist verworfen: Es erzeugt genau die toten Enden,
            # die der Raum nicht haben darf. Zwei Landschaften, die beide
            # unter null gedrueckt werden, sind danach dieselbe Zahl — und
            # `test_die_ordnung_der_landschaften_ueberlebt_jeden_charakter`
            # faellt darueber, zu Recht.
            #
            # Die Wegform hat vier Eigenschaften, die das Kappen nicht hat:
            # Sie bleibt in [0, 1] **durch Konstruktion** (keine Klemme
            # noetig, `ausserhalb` bleibt allein das Zeichen eines Defekts),
            # sie ist ordnungserhaltend fuer jeden Zug unter 1, sie ist bei
            # Zug 0 neutral, und sie schliesst die Tuer **nur** bei
            # Auspraegung exakt 1.0 — der einen Stelle, an der das Konzept
            # ein totes Ende ausdruecklich will: Dort ist der Charakter der
            # Zustand, und die Landschaft zaehlt nicht mehr.
            ergebnis += zug * ((1.0 - ergebnis) if zug > 0 else ergebnis)

        werte[groesse] = Groessenwert(
            name         = groesse,
            grundwert    = grund,
            modifikation = summe,
            ergebnis     = ergebnis,
            art          = art,
            ausloeser    = traeger,
            ausserhalb   = not (GROESSE_MIN <= ergebnis <= GROESSE_MAX),
        )

    # ── Ausgabe-Verifikation ────────────────────
    if set(werte) != set(GROESSEN):
        logger.error(
            f"Haltung: Ergebnis traegt {sorted(werte)} statt {sorted(GROESSEN)} "
            f"— Cluster {cluster!r}, verworfen"
        )
        return None

    for wert in werte.values():
        if wert.ausserhalb:
            # Seit dem 08.08.2026 ist das kein erwarteter Zustand mehr, sondern
            # ein Defekt: Die Wegform kann die Spanne nicht verlassen. Bleibt
            # nur die multiplikative Grenzzelle, und die kaeme nur bei einem
            # Grundwert ueber 0.5 heraus — den es im Bestand nicht gibt.
            logger.error(
                f"Haltung: {wert.name} liegt mit {wert.ergebnis:.3f} ausserhalb "
                f"[{GROESSE_MIN}, {GROESSE_MAX}] — Cluster {cluster!r}, "
                f"Grundwert {wert.grundwert:.2f}, Modifikation "
                f"{wert.modifikation:+.2f}, Art {wert.art}. Nicht gekappt: "
                "Kappen erzeugt tote Enden. Bei Art 'neigung' oder "
                "'uebersteuerung' ist dieser Fall unmoeglich und zeigt einen "
                "Defekt der Rechenform an."
            )

    return Haltung(cluster=cluster, werte=werte)
