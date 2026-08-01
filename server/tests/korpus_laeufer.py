"""Laeufer fuer den Haertefallkorpus.

Der Korpus ist die Spezifikation der Phasen 2-5. Ein Laeufer, der nur
bestanden/durchgefallen kennt, waere fuer diesen Zweck unbrauchbar: Die
Haelfte der Faelle SOLL heute scheitern, und der Unterschied zwischen
"noch nicht gebaut" und "kaputtgemacht" ist die ganze Information.

Vier Zustaende:

    ERFUELLT      besteht, ab_phase erreicht          -> gut
    OFFEN         scheitert, ab_phase noch nicht      -> erwartet, kein Fehler
    REGRESSION    scheitert, ab_phase laengst da      -> Abbruch
    VORAUSEILEND  besteht vor seiner Phase            -> ab_phase senken

`ab_phase: null` markiert dokumentierte Luecken. Sie werden gesondert
gezaehlt und nie als Fehler gewertet.

Zwei Pruefungen, nicht eine:

    korpus_pruefen()   prueft den Korpus gegen sich selbst — Schema,
                       Zonenversaetze, Intervallrichtung, Eindeutigkeit.
                       Laeuft ohne Parser.
    korpus_laufen()    prueft den Parser gegen den Korpus.

Die erste ist die wichtigere. Ein Golden-File mit falschen Sollwerten
zementiert Fehler, statt sie zu finden.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional
from zoneinfo import ZoneInfo

import yaml

KORPUS_PFAD: Path = Path(__file__).parent / "korpus" / "zeitausdruecke.yaml"

ERFUELLT: str = "erfuellt"
OFFEN: str = "offen"
REGRESSION: str = "regression"
VORAUSEILEND: str = "vorauseilend"
LUECKE: str = "luecke"

_ERLAUBTE_ARTEN: frozenset[str] = frozenset(
    {"punkt", "intervall", "dauer", "vage", "unaufloesbar"}
)
_ERLAUBTE_VAGE: frozenset[str] = frozenset(
    {"vergangenheit", "gegenwart", "zukunft"}
)
_ERLAUBTE_MODI: frozenset[str] = frozenset(
    {"absolut", "relativ", "relativ_rueckwaerts"}
)
_ERLAUBTE_PHASEN: frozenset = frozenset({None, 0, 1, 2, 3, 4, 5})


@dataclass
class Befund:
    """Ergebnis eines einzelnen Korpusfalls."""
    fall_id: str
    zustand: str
    ab_phase: Optional[int]
    text: str
    erwartet: str = ""
    erhalten: str = ""
    grund: str = ""


@dataclass
class Bericht:
    """Gesamtergebnis eines Korpuslaufs."""
    phase: int
    befunde: list[Befund] = field(default_factory=list)

    def nach_zustand(self, zustand: str) -> list[Befund]:
        return [b for b in self.befunde if b.zustand == zustand]

    @property
    def regressionen(self) -> list[Befund]:
        return self.nach_zustand(REGRESSION)

    def zusammenfassung(self) -> str:
        zeilen: list[str] = [f"Korpuslauf — Phase {self.phase}", ""]
        for zustand, etikett in (
            (ERFUELLT, "erfuellt"),
            (OFFEN, "offen (erwartet)"),
            (VORAUSEILEND, "vorauseilend"),
            (LUECKE, "dokumentierte Luecke"),
            (REGRESSION, "REGRESSION"),
        ):
            anzahl: int = len(self.nach_zustand(zustand))
            zeilen.append(f"  {etikett:24} {anzahl:3d}")
        zeilen.append(f"  {'gesamt':24} {len(self.befunde):3d}")
        return "\n".join(zeilen)


# ── Korpus laden ────────────────────────────────────────────────────────────

def korpus_laden(pfad: Optional[Path] = None) -> dict[str, Any]:
    """Liest den Korpus und loest die Anker in den Faellen auf.

    Vorbedingung: Die Datei existiert und ist gueltiges YAML.
    Nachbedingung: Jeder Fall hat aufgeloeste `jetzt`- und
        `referenz`-Zeitpunkte als datetime.
    """
    # ── Eingabe ─────────────────────────────────
    if pfad is None:
        pfad = KORPUS_PFAD

    with open(pfad, encoding="utf-8") as datei:
        rohdaten: dict[str, Any] = yaml.safe_load(datei)

    # ── Verarbeitung ────────────────────────────
    standard_jetzt: datetime = datetime.fromisoformat(rohdaten["meta"]["jetzt"])
    anker: dict[str, datetime] = {
        name: datetime.fromisoformat(wert)
        for name, wert in (rohdaten.get("anker") or {}).items()
    }

    for fall in rohdaten["faelle"]:
        fall["jetzt_dt"] = (
            datetime.fromisoformat(fall["jetzt"]) if "jetzt" in fall
            else standard_jetzt
        )
        referenz_name: Optional[str] = fall.get("referenz")
        fall["referenz_dt"] = (
            anker[referenz_name] if referenz_name else fall["jetzt_dt"]
        )

    # ── Ausgabe ─────────────────────────────────
    rohdaten["anker_dt"] = anker
    return rohdaten


# ── Selbstpruefung ──────────────────────────────────────────────────────────

def korpus_pruefen(korpus: Optional[dict[str, Any]] = None) -> list[str]:
    """Prueft den Korpus gegen sich selbst. Laeuft ohne Parser.

    Returns:
        Liste der Beanstandungen. Leer heisst: der Korpus ist in sich stimmig.
    """
    # ── Eingabe ─────────────────────────────────
    if korpus is None:
        korpus = korpus_laden()

    zone: ZoneInfo = ZoneInfo(korpus["meta"]["zone"])
    beanstandungen: list[str] = []
    gesehen: set[str] = set()

    # ── Verarbeitung ────────────────────────────
    for fall in korpus["faelle"]:
        kennung: str = fall.get("id", "<ohne id>")

        if kennung in gesehen:
            beanstandungen.append(f"{kennung}: doppelte id")
        gesehen.add(kennung)

        if not fall.get("text"):
            beanstandungen.append(f"{kennung}: kein text")

        if fall.get("ab_phase", "fehlt") not in _ERLAUBTE_PHASEN:
            beanstandungen.append(
                f"{kennung}: ab_phase {fall.get('ab_phase')!r} unzulaessig"
            )

        beanstandungen.extend(_zone_pruefen(kennung, "jetzt", fall.get("jetzt"), zone))

        vektor: dict = fall.get("vektor") or {}
        modus: Optional[str] = vektor.get("referenz_modus")
        if modus is not None and modus not in _ERLAUBTE_MODI:
            beanstandungen.append(f"{kennung}: referenz_modus {modus!r} unbekannt")

        erwartet: Optional[dict] = fall.get("erwartet")
        if erwartet is None:
            if not vektor:
                beanstandungen.append(f"{kennung}: weder erwartet noch vektor")
            continue

        beanstandungen.extend(_erwartung_pruefen(kennung, erwartet, zone))

    # ── Ausgabe ─────────────────────────────────
    return beanstandungen


def _zone_pruefen(
    kennung: str, feld: str, wert: Optional[str], zone: ZoneInfo,
) -> list[str]:
    """Prueft, ob der Zonenversatz eines ISO-Zeitpunkts zur Zone passt.

    Faengt den haeufigsten Tippfehler im Korpus: +01:00 statt +02:00 oder
    umgekehrt. Ein Sollwert mit falschem Versatz ist um eine Stunde falsch,
    sieht aber richtig aus.
    """
    if wert is None:
        return []

    try:
        zeitpunkt: datetime = datetime.fromisoformat(wert)
    except ValueError:
        return [f"{kennung}: {feld} {wert!r} ist kein ISO-Zeitpunkt"]

    if zeitpunkt.tzinfo is None:
        return [f"{kennung}: {feld} ohne Zonenversatz"]

    erwarteter: timedelta = zeitpunkt.replace(tzinfo=zone).utcoffset()
    if zeitpunkt.utcoffset() != erwarteter:
        return [
            f"{kennung}: {feld} hat Versatz {zeitpunkt.utcoffset()}, "
            f"{zone} liegt dort bei {erwarteter}"
        ]
    return []


def _erwartung_pruefen(
    kennung: str, erwartet: dict, zone: ZoneInfo,
) -> list[str]:
    """Prueft eine Erwartung auf innere Stimmigkeit."""
    beanstandungen: list[str] = []
    art: Optional[str] = erwartet.get("art")

    if art not in _ERLAUBTE_ARTEN:
        beanstandungen.append(f"{kennung}: art {art!r} unbekannt")
        return beanstandungen

    for feld in ("beginn", "ende"):
        beanstandungen.extend(
            _zone_pruefen(kennung, feld, erwartet.get(feld), zone)
        )

    if art == "punkt" and not erwartet.get("beginn"):
        beanstandungen.append(f"{kennung}: punkt ohne beginn")

    if art == "intervall":
        beginn_s, ende_s = erwartet.get("beginn"), erwartet.get("ende")
        if not beginn_s or not ende_s:
            beanstandungen.append(f"{kennung}: intervall ohne beginn/ende")
        else:
            beginn = datetime.fromisoformat(beginn_s)
            ende = datetime.fromisoformat(ende_s)
            if beginn >= ende:
                beanstandungen.append(
                    f"{kennung}: intervall laeuft rueckwaerts "
                    f"({beginn.date()} >= {ende.date()})"
                )
            tage: Optional[int] = erwartet.get("dauer_tage")
            if tage is not None and (ende - beginn).days != tage:
                beanstandungen.append(
                    f"{kennung}: dauer_tage {tage} passt nicht zur Spanne "
                    f"({(ende - beginn).days})"
                )

    if art == "dauer" and erwartet.get("dauer_tage") is None:
        beanstandungen.append(f"{kennung}: dauer ohne dauer_tage")

    if art == "vage":
        vage: Optional[str] = erwartet.get("vage")
        if vage not in _ERLAUBTE_VAGE:
            beanstandungen.append(f"{kennung}: vage {vage!r} unbekannt")

    return beanstandungen


# ── Lauf gegen den Parser ───────────────────────────────────────────────────

class UmgebungFehlt(RuntimeError):
    """Der Lauf ist nicht aussagekraeftig, weil eine Abhaengigkeit fehlt."""


def umgebung_pruefen() -> list[str]:
    """Prueft, ob ein Korpuslauf ueberhaupt aussagekraeftig sein kann.

    Ohne funktionsfaehiges `dateparser` scheitern alle Faelle, die Pfad 2
    oder 3 brauchen — und wuerden als Regression gemeldet. Fuenf falsche
    Alarme sind schlimmer als eine klare Fehlermeldung: Sie kosten die Zeit,
    die man braucht, um sie als falsch zu erkennen, und sie stumpfen die
    Aufmerksamkeit fuer echte Regressionen ab.

    Returns:
        Liste der Maengel. Leer heisst: der Lauf ist aussagekraeftig.
    """
    # ── Verarbeitung ────────────────────────────
    maengel: list[str] = []

    try:
        dateparser = importlib.import_module("dateparser")
    except ImportError:
        return ["dateparser ist nicht installiert"]

    probe: Any = dateparser.parse(
        "Montag", languages=["de"],
        settings={"RELATIVE_BASE": datetime(2026, 7, 31, 14, 0)},
    )
    if probe is None:
        maengel.append(
            "dateparser liefert fuer 'Montag' nichts — vermutlich ein Stub "
            "oder eine unvollstaendige Installation"
        )

    # ── Ausgabe ─────────────────────────────────
    return maengel


def korpus_laufen(
    phase: Optional[int] = None,
    korpus: Optional[dict[str, Any]] = None,
    umgebung_erzwingen: bool = True,
) -> Bericht:
    """Fuehrt den Korpus gegen den Parser aus.

    Args:
        phase: Umbauphase, gegen die bewertet wird. Default: `meta.aktuelle_phase`.
        korpus: Vorgeladener Korpus. Default: von Platte.
        umgebung_erzwingen: Bricht ab, wenn der Lauf nicht aussagekraeftig
            waere. Nur zum Pruefen des Laeufers selbst auf False setzen.

    Raises:
        UmgebungFehlt: Wenn eine Abhaengigkeit fehlt und `umgebung_erzwingen`.
    """
    # ── Eingabe ─────────────────────────────────
    if umgebung_erzwingen:
        maengel: list[str] = umgebung_pruefen()
        if maengel:
            raise UmgebungFehlt(
                "Korpuslauf abgebrochen — das Ergebnis waere nicht "
                "aussagekraeftig:\n  " + "\n  ".join(maengel)
            )

    if korpus is None:
        korpus = korpus_laden()
    if phase is None:
        phase = korpus["meta"]["aktuelle_phase"]

    zeitparser = importlib.import_module("utils.zeitparser")
    zone: ZoneInfo = ZoneInfo(korpus["meta"]["zone"])
    bericht: Bericht = Bericht(phase=phase)

    # ── Verarbeitung ────────────────────────────
    for fall in korpus["faelle"]:
        befund: Befund = _fall_laufen(fall, zeitparser, zone, phase)
        bericht.befunde.append(befund)

    # ── Ausgabe ─────────────────────────────────
    return bericht


def _fall_laufen(
    fall: dict, zeitparser: Any, zone: ZoneInfo, phase: int,
) -> Befund:
    """Fuehrt einen Fall aus und bewertet ihn gegen seine ab_phase."""
    kennung: str = fall["id"]
    ab_phase: Optional[int] = fall.get("ab_phase")

    bestanden, erwartet_text, erhalten_text, grund = _fall_pruefen(
        fall, zeitparser, zone,
    )

    if ab_phase is None:
        zustand: str = LUECKE
    elif bestanden and ab_phase <= phase:
        zustand = ERFUELLT
    elif bestanden:
        zustand = VORAUSEILEND
    elif ab_phase <= phase:
        zustand = REGRESSION
    else:
        zustand = OFFEN

    return Befund(
        fall_id=kennung,
        zustand=zustand,
        ab_phase=ab_phase,
        text=fall["text"],
        erwartet=erwartet_text,
        erhalten=erhalten_text,
        grund=grund,
    )


def _fall_pruefen(
    fall: dict, zeitparser: Any, zone: ZoneInfo,
) -> tuple[bool, str, str, str]:
    """Vergleicht Parserergebnis und Erwartung.

    Der heutige Kalendertag wird fuer die Dauer des Falls auf den im Korpus
    festgelegten Bezugsmoment gesetzt — sonst waeren die Zonenfaelle nur in
    dem Zeitfenster pruefbar, in dem sie fehlschlagen wuerden.
    """
    jetzt: datetime = fall["jetzt_dt"]
    referenz: datetime = fall["referenz_dt"]

    # Bis zum 01.08.2026 stand hier ein Monkey-Patch auf `_heute_lokal`: Der
    # Parser hatte keinen Weg, den Sprechzeitpunkt entgegenzunehmen, also
    # wurde eine private Funktion fuer die Dauer des Falls ersetzt. Seit es
    # `sprechzeitpunkt` gibt, laeuft der Korpus ueber die oeffentliche
    # Schnittstelle — und misst damit dasselbe, was auch der Betrieb benutzt.
    return _vergleichen(fall, zeitparser, zone, referenz, jetzt)


def _vergleichen(
    fall: dict, zeitparser: Any, zone: ZoneInfo, referenz: datetime,
    jetzt: datetime,
) -> tuple[bool, str, str, str]:
    """Der eigentliche Vergleich, ohne Zeitmanipulation."""
    text: str = fall["text"]
    vektor_erwartung: dict = fall.get("vektor") or {}
    erwartung: dict = fall.get("erwartet") or {}

    # Vektorfelder pruefen, wenn gefordert
    if vektor_erwartung:
        vektor = zeitparser.zeit_parsen_vektor(text, referenz, sprechzeitpunkt=jetzt)
        for feld, soll in vektor_erwartung.items():
            ist = getattr(vektor, feld, "<fehlt>")
            if ist != soll:
                return (
                    False, f"{feld}={soll!r}", f"{feld}={ist!r}",
                    "Vektorfeld weicht ab",
                )
        if not erwartung:
            return True, "vektor ok", "vektor ok", ""

    art: str = erwartung.get("art", "punkt")

    # Intervall, Dauer und vage Ausdruecke braucht einen Typ, den der Parser
    # erst ab Phase 3 hat. Vorher ist der Fall zwangslaeufig offen.
    if art in ("intervall", "dauer", "vage", "unaufloesbar"):
        if not hasattr(zeitparser, "zeit_spanne_parsen"):
            return (
                False, art, "zeit_spanne_parsen fehlt",
                "Typ erst ab Phase 3 darstellbar",
            )
        spanne = zeitparser.zeit_spanne_parsen(text, referenz)
        return _spanne_vergleichen(spanne, erwartung, zone)

    # Punkt: der heutige Rueckgabetyp
    ergebnis: Optional[datetime] = zeitparser.zeit_parsen(
        text, referenz, sprechzeitpunkt=jetzt,
    )
    soll_s: Optional[str] = erwartung.get("beginn")
    if soll_s is None:
        return True, "kein Sollwert", "-", ""
    soll: datetime = datetime.fromisoformat(soll_s)

    if ergebnis is None:
        return False, soll.isoformat(), "None", "nicht aufloesbar"

    genau: str = fall.get("genauigkeit", "minute")
    return _zeitpunkt_vergleichen(ergebnis, soll, zone, genau)


def _zeitpunkt_vergleichen(
    ist: datetime, soll: datetime, zone: ZoneInfo, genauigkeit: str,
) -> tuple[bool, str, str, str]:
    """Vergleicht zwei Zeitpunkte auf Tages- oder Minutengenauigkeit."""
    ist_lokal: datetime = ist.astimezone(zone)
    soll_lokal: datetime = soll.astimezone(zone)

    if genauigkeit == "tag":
        gleich: bool = ist_lokal.date() == soll_lokal.date()
        return (
            gleich, str(soll_lokal.date()), str(ist_lokal.date()),
            "" if gleich else "anderer Tag",
        )

    gleich = ist_lokal.replace(second=0, microsecond=0) == soll_lokal.replace(
        second=0, microsecond=0,
    )
    return (
        gleich, soll_lokal.isoformat(), ist_lokal.isoformat(),
        "" if gleich else "anderer Zeitpunkt",
    )


def _spanne_vergleichen(
    spanne: Any, erwartung: dict, zone: ZoneInfo,
) -> tuple[bool, str, str, str]:
    """Vergleicht eine ZeitSpanne ab Phase 3."""
    art: str = erwartung["art"]
    if getattr(spanne, "art", None) != art:
        return False, art, str(getattr(spanne, "art", "?")), "andere Art"

    if art == "vage":
        soll: str = erwartung["vage"]
        ist: Any = getattr(spanne, "vage", None)
        return ist == soll, soll, str(ist), "" if ist == soll else "andere Vagheit"

    if art == "dauer":
        soll_tage: int = erwartung["dauer_tage"]
        dauer = getattr(spanne, "dauer", None)
        ist_tage: Optional[int] = dauer.days if dauer else None
        return (
            ist_tage == soll_tage, f"{soll_tage}d", f"{ist_tage}d",
            "" if ist_tage == soll_tage else "andere Dauer",
        )

    for feld in ("beginn", "ende"):
        soll_dt: datetime = datetime.fromisoformat(erwartung[feld])
        ist_dt: Optional[datetime] = getattr(spanne, feld, None)
        if ist_dt is None:
            return False, soll_dt.isoformat(), "None", f"{feld} fehlt"
        gleich, s, i, grund = _zeitpunkt_vergleichen(ist_dt, soll_dt, zone, "minute")
        if not gleich:
            return False, f"{feld}={s}", f"{feld}={i}", grund

    return True, "intervall ok", "intervall ok", ""


# ── Bericht auf der Konsole ─────────────────────────────────────────────────

def bericht_drucken(bericht: Bericht, ausfuehrlich: bool = False) -> None:
    """Gibt den Bericht aus. Regressionen immer, Offene nur auf Wunsch."""
    print(bericht.zusammenfassung())

    for befund in bericht.regressionen:
        print(f"\n  REGRESSION {befund.fall_id} (ab Phase {befund.ab_phase})")
        print(f"    Text     : {befund.text!r}")
        print(f"    erwartet : {befund.erwartet}")
        print(f"    erhalten : {befund.erhalten}   [{befund.grund}]")

    for befund in bericht.nach_zustand(VORAUSEILEND):
        print(f"\n  VORAUSEILEND {befund.fall_id}: besteht schon vor "
              f"Phase {befund.ab_phase} — ab_phase senken")

    if ausfuehrlich:
        for befund in bericht.nach_zustand(OFFEN):
            print(f"  offen  {befund.fall_id:10} {befund.text!r:34} "
                  f"ab Phase {befund.ab_phase}  [{befund.grund}]")


if __name__ == "__main__":
    import sys

    beanstandungen: list[str] = korpus_pruefen()
    if beanstandungen:
        print("Korpus-Selbstpruefung FEHLGESCHLAGEN:")
        for zeile in beanstandungen:
            print(f"  {zeile}")
        sys.exit(2)
    print("Korpus-Selbstpruefung: in Ordnung\n")

    bericht: Bericht = korpus_laufen()
    bericht_drucken(bericht, ausfuehrlich="-v" in sys.argv)
    sys.exit(1 if bericht.regressionen else 0)
