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
# Die Spalte `fragen` ist nicht gesetzt, sondern aus CLUSTER_FRAGEN
# (ei/dreischicht.py) uebersetzt: "Haeufig, begeistert" -> 0.9, "Keine" -> 0.0.
# Wer dort etwas aendert, aendert hier mit.
CLUSTER_GRUNDWERT: dict[str, dict[str, float]] = {
    "feuerwerk": {
        "umfang": 0.80, "fragen": 0.90, "naehe": 0.90,
        "waerme": 0.90, "draengen": 0.70,
    },
    "kissenschlacht": {
        "umfang": 0.30, "fragen": 0.60, "naehe": 0.80,
        "waerme": 0.90, "draengen": 0.50,
    },
    "werkstatt": {
        "umfang": 0.90, "fragen": 0.90, "naehe": 0.50,
        "waerme": 0.50, "draengen": 0.70,
    },
    "glut": {
        "umfang": 0.70, "fragen": 0.30, "naehe": 0.90,
        "waerme": 0.80, "draengen": 0.20,
    },
    "bier": {
        "umfang": 0.50, "fragen": 0.50, "naehe": 0.80,
        "waerme": 0.80, "draengen": 0.30,
    },
    "foyer": {
        "umfang": 0.70, "fragen": 0.50, "naehe": 0.30,
        "waerme": 0.50, "draengen": 0.30,
    },
    "regen": {
        "umfang": 0.20, "fragen": 0.15, "naehe": 0.80,
        "waerme": 0.90, "draengen": 0.00,
    },
    "schmollen": {
        "umfang": 0.20, "fragen": 0.15, "naehe": 0.60,
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
        "umfang": 0.15, "fragen": 0.30, "naehe": 0.20,
        "waerme": 0.20, "draengen": 0.80,
    },
    "beichte": {
        "umfang": 0.20, "fragen": 0.30, "naehe": 0.95,
        "waerme": 0.90, "draengen": 0.00,
    },
    "wartezimmer": {
        "umfang": 0.30, "fragen": 0.50, "naehe": 0.20,
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
    "wissbegier": {"umfang": 0.30, "fragen": 0.40, "draengen": 0.20},
    "wohlwollen": {"naehe": 0.10, "waerme": 0.40},
    "selbstbezogen": {"umfang": 0.10, "fragen": -0.20, "naehe": -0.30, "draengen": 0.30},
    "gleichgueltig": {"umfang": -0.30, "fragen": -0.20, "naehe": -0.20, "waerme": -0.40},
    "widerspenstig": {"waerme": -0.30, "draengen": 0.30},
    "distanz": {"umfang": -0.30, "naehe": -0.50, "waerme": -0.20},
    "langeweile": {"umfang": -0.40, "fragen": -0.30, "waerme": -0.20, "draengen": -0.20},
    "misstrauen": {"fragen": 0.10, "naehe": -0.20, "waerme": -0.40},
}

# Welche Speiche bei voller Auspraegung eine **Grenze durchbricht**, und in
# welcher Groesse. Bewusst wenige, beide an den Grenzen, die am ehesten
# ueberschreitbar sein sollten: Eine brennend neugierige Nova fragt auch im
# Gewitter, und volle Distanz ueberwiegt jede warme Landschaft.
SPEICHEN_UEBERSTEUERUNG: dict[str, frozenset[str]] = {
    "wissbegier": frozenset({"fragen"}),
    "distanz":    frozenset({"naehe"}),
}

# Ab dieser Auspraegung greift eine Uebersteuerung. Darunter wirkt der Beitrag
# der Speiche als gewoehnliche Neigung — gegen eine Grenze also gar nicht.
UEBERSTEUERUNG_AB: float = 1.0


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


def _uebersteuerer(rad: dict[str, float], groesse: str) -> str:
    """Nennt die Speiche, die diese Groesse uebersteuert, sonst "".

    Bei mehreren zutreffenden gewinnt die erste in SPEICHEN_UEBERSTEUERUNG;
    das ist heute nicht erreichbar, weil keine zwei Speichen dieselbe Groesse
    uebersteuern, bleibt aber deterministisch, falls eine dazukommt.

    Vorbedingung: wie `_modifikation`.
    Nachbedingung: Speichenname aus SPEICHEN_UEBERSTEUERUNG oder "".
    """
    for speiche, groessen in SPEICHEN_UEBERSTEUERUNG.items():
        if groesse in groessen and rad.get(speiche, 0.0) >= UEBERSTEUERUNG_AB:
            return speiche
    return ""


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


def _verrechnen(grund: float, summe: float, art: str) -> float:
    """Verknuepft Grundwert und Modifikation nach der Rechenart der Zelle.

    Steht als eigene Funktion, weil sie sonst nicht pruefbar waere: Alle sechs
    Grenzen im heutigen Bestand tragen den Grundwert 0.00, und dort ist eine
    Multiplikation von "immer null" nicht zu unterscheiden. Hier laesst sie
    sich mit einem Grundwert groesser null pruefen.

    Vorbedingung: `art` ist "neigung", "grenze" oder "uebersteuerung".
        Pruefung erfolgt beim Aufrufer, der die Art selbst setzt.
    Nachbedingung: Bei "grenze" und einem Grundwert von null ist das Ergebnis
        null, gleich welche Summe anliegt.
    """
    if art == "grenze":
        # Multiplikativ: Der Charakter skaliert, was die Lage zulaesst.
        return grund * (1.0 + summe)
    # Neigung und Uebersteuerung addieren; der Unterschied liegt darin, dass
    # die Uebersteuerung die Grenze ueberhaupt erst aufhebt.
    return grund + summe


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
        traeger: str  = _uebersteuerer(rad, groesse) if groesse in grenzen else ""

        if traeger:
            # Die Uebersteuerung hebt die Grenze auf. Sie ersetzt die
            # Rechenart, nicht den Beitrag.
            art: str = "uebersteuerung"
        elif groesse in grenzen:
            art = "grenze"
        else:
            art = "neigung"

        ergebnis: float = _verrechnen(grund, summe, art)

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
            logger.warning(
                f"Haltung: {wert.name} liegt mit {wert.ergebnis:.3f} ausserhalb "
                f"[{GROESSE_MIN}, {GROESSE_MAX}] — Cluster {cluster!r}, "
                f"Grundwert {wert.grundwert:.2f}, Modifikation "
                f"{wert.modifikation:+.2f}, Art {wert.art}. Nicht gekappt: Die "
                "Behandlung der Spannenenden ist eine offene Frage des "
                "Konzepts, und die Haeufigkeit dieses Falls ist die "
                "Messgroesse dafuer."
            )

    return Haltung(cluster=cluster, werte=werte)
