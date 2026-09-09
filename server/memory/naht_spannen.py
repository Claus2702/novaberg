"""Ist-Spanne gegen Zielspanne je Naht — die Erhebung hinter dem Naht-Panel.

**Was eine Naht ist.** Eine Stelle, an der Groessen mit je eigener Skala
zusammengefuehrt werden. `F-NAHT-1` verlangt, dass sie dort auf **derselben**
Skala liegen, normiert ueber ihre je eigene **gemessene** Spanne; was danach
geschieht, darf sie verschieden behandeln.

**Warum das gemessen und nicht ueberlegt wird.** Eine Groesse, die ihre
unterstellte Obergrenze nie erreicht, traegt in einem Produkt ein stilles
Gewicht, das niemand gesetzt hat. `[gemessen 08.09.2026]` `resonanz` kommt
ueber 1762 Zeilen nie ueber **0,4322** — eine Cosine-Aehnlichkeit zwischen
zwei unabhaengig entstandenen Texten liegt bei 0,2 bis 0,5, und 1,0 hiesse
identischer Text. Wer sie als Faktor in [0…1] einsetzt, multipliziert mit
einer Zahl, deren Spanne er nie gemessen hat.

**Zwei Richtungen, und nur eine hatte bisher einen Waechter:**

    UEBERSCHREITUNG  Ist > Ziel    `ausserhalb` im Haltungsraum, seit 31.07.
    UNTERSCHREITUNG  Ist << Ziel   nichts — dieses Modul ist er

**Warum jede Naht zwei Fenster traegt.** Ohne Zeitachse meldet die Erhebung
eine behobene Fehljustierung als laufende: Die Haltungsgroessen zeigen ueber
den ganzen Bestand eine Ist-Spanne von 155 % der Zielspanne — und die
Ueberschreitungsmarke hat seit dem 08.08.2026 in **765 Zeilen kein einziges
Mal** angeschlagen. Die Extreme stammen aus der Zeit vor dem abgeleiteten
Abbildungsfaktor.
"""

import logging
from dataclasses import dataclass
from typing import Any

from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.memory.naht_spannen")

#: Wie viele Tage das junge Fenster umfasst. **Aus dem Projekt abgeleitet,
#: nicht gerundet:** Zwischen der Halbierung der Umfangs-Korridore (20.08.)
#: und der naechsten Kalibrierung (27.08.) lagen sieben Tage; vierzehn decken
#: also mindestens eine volle Generation ab.
FENSTER_TAGE: int = 14


@dataclass(frozen=True)
class Naht:
    """Eine gemessene Naht samt ihrer benannten Zielspanne.

    Attributes:
        gruppe:   Fachlicher Block, unter dem sie im Panel steht.
        name:     Der Bezeichner, unter dem die Groesse im Code laeuft.
        ziel:     Die **benannte** Zielspanne aus Code oder Konzept, oder
                  None, wenn keine benannt ist. **None ist ein Befund und
                  kein fehlender Eintrag**: Wo keine Spanne benannt ist,
                  kann keine verletzt werden — die Naht ist dann nicht
                  justiert, sondern ungeprueft.
        tabelle:  Herkunftstabelle.
        ausdruck: SQL-Ausdruck, der den Wert liefert.
        bedingung: Zusaetzliche WHERE-Klausel ohne fuehrendes AND.
        zeitfeld: Spalte mit dem Zeitbezug fuer das junge Fenster.
    """

    gruppe:    str
    name:      str
    ziel:      tuple[float, float] | None
    tabelle:   str
    ausdruck:  str
    bedingung: str = ""
    zeitfeld:  str = "erstellt_am"


def _haltung(name: str) -> Naht:
    """Eine der fuenf Haltungsgroessen aus dem Protokoll des Haltungsraums."""
    return Naht(
        gruppe="Haltung", name=name, ziel=(0.0, 1.0), tabelle="pipeline_log",
        ausdruck=f"(inhalt#>>'{{groessen,{name},ergebnis}}')::float",
        bedingung=(
            f"node='haltungsraum' AND art='berechnung' "
            f"AND inhalt#>>'{{groessen,{name},ergebnis}}' IS NOT NULL"
        ),
    )


def _log(gruppe: str, node: str, feld: str,
         ziel: tuple[float, float] | None) -> Naht:
    """Eine Groesse aus einer `berechnung`-Zeile des Pipeline-Logs."""
    return Naht(
        gruppe=gruppe, name=feld, ziel=ziel, tabelle="pipeline_log",
        ausdruck=f"(inhalt->>'{feld}')::float",
        bedingung=f"node='{node}' AND art='berechnung' AND inhalt->>'{feld}' IS NOT NULL",
    )


def _spalte(gruppe: str, tabelle: str, spalte: str,
            ziel: tuple[float, float] | None, zeitfeld: str) -> Naht:
    """Eine Groesse, die als eigene Spalte in einer Tabelle steht."""
    return Naht(
        gruppe=gruppe, name=spalte, ziel=ziel, tabelle=tabelle,
        ausdruck=spalte, bedingung=f"{spalte} IS NOT NULL", zeitfeld=zeitfeld,
    )


#: Der Bestand der Naehte. Neue Naehte kommen hier dazu; das Panel liest
#: diese Liste und braucht keine eigene Kenntnis der Groessen.
NAEHTE: tuple[Naht, ...] = (
    _haltung("umfang"), _haltung("fragen"), _haltung("naehe"),
    _haltung("waerme"), _haltung("draengen"),

    # Der Deckel 2,0 steht im Konzept; der Faktor liegt um 1,0 (`F-NAHT-1`).
    _log("Faszination", "haltungsraum", "faszination", (0.0, 2.0)),
    _log("Faszination", "haltungsraum", "fasz_faktor", (0.60, 1.40)),

    # Drei rohe Skalen in einem Produkt — der Anlass dieser Erhebung.
    _spalte("Neugier", "wissensluecken", "resonanz", (0.0, 1.0), "aktualisiert_am"),
    _spalte("Neugier", "wissensluecken", "neuheit", (0.0, 1.0), "aktualisiert_am"),
    _spalte("Neugier", "wissensluecken", "neugier_vektor", (0.0, 0.5), "aktualisiert_am"),

    _spalte("Praegung", "praegung_faden", "ausschlag_eingang", None, "entstanden_am"),
    _spalte("Praegung", "praegung_faden", "ausschlag_aktuell", None, "entstanden_am"),
    _log("Praegung", "praegung", "ausschlag", (0.0, 1.0)),

    _log("Strang", "praegung_strang", "ladung_staerke", (0.0, 1.0)),
    _log("Strang", "praegung_strang", "ladung_praesenz", (0.0, 1.0)),
    _log("Strang", "praegung_strang", "konfrontation", None),

    _log("Salienz", "salienz", "zug_staerke", (0.0, 1.0)),
    _log("Salienz", "salienz", "eigen_pfad", (0.0, 1.0)),
    _log("Salienz", "salienz", "pflicht_pfad", (0.0, 1.0)),
    _log("Salienz", "salienz", "zielsog", None),

    # **Die Groesse, die die Naht am 09.09.2026 gebrochen hat, stand nicht in
    # dieser Liste.** Die Tafel fuehrte `eigen_pfad` und sah dort 393,4 %
    # Ausschoepfung — den Schaden, nicht die Ursache. Der Gravitationsterm ist
    # seither auf [0, 1] normiert; ohne eigene Zeile hier waere sein Rueckfall
    # wieder nur an der Folgegroesse ablesbar.
    #
    # **Der Bestand traegt zwei Skalengenerationen ohne Herkunftsfeld.** Ueber
    # das ganze Fenster gerechnet meldet diese Naht bis 600 %; die Zahl ist
    # erst ab dem 09.09.2026 eine Aussage ueber die Naht. Dieselbe Klasse wie
    # `KOSTENSPALTE-MISCHT-PREISGENERATIONEN`.
    _log("Salienz", "salienz", "gravitationsterm", (0.0, 1.0)),
)


def _ausschoepfung(
    unten: float | None, oben: float | None, ziel: tuple[float, float] | None,
) -> float | None:
    """Welchen Anteil der Zielspanne die gemessenen Werte belegen, in Prozent.

    **Der Wert darf ueber 100 liegen, und das ist der Zweck.** Eine gekappte
    Ausschoepfung machte aus *„passt gerade"* und *„sprengt die Spanne"*
    dieselbe Zahl — genau das tote Ende, das `F-NAHT-1` beim Kappen benennt.

    Vorbedingung: keine.
    Nachbedingung: Prozentwert oder None, wenn keine Zielspanne benannt ist
        oder keine Werte vorliegen.
    Fehlerfaelle: Eine Zielspanne der Breite 0 ist ein Fehler in `NAEHTE` —
        sie liefert None und eine Meldung, statt durch null zu teilen.

    Args:
        unten: kleinster gemessener Wert.
        oben:  groesster gemessener Wert.
        ziel:  die benannte Zielspanne.

    Returns:
        Die Ausschoepfung in Prozent, oder None.
    """
    # ── Eingabe-Validierung ─────────────────────
    if ziel is None or unten is None or oben is None:
        return None
    breite: float = ziel[1] - ziel[0]
    if breite <= 0:
        logger.error(
            "Naht-Spannen: Zielspanne %s hat die Breite %s — die Ausschoepfung "
            "ist nicht bildbar. Der Fehler steht in NAEHTE, nicht in den Daten.",
            ziel, breite,
        )
        return None

    # ── Verarbeitung / Ausgabe ──────────────────
    return round(100.0 * (oben - unten) / breite, 1)


def _satz_bauen(naht: Naht, zeile: dict[str, Any]) -> dict[str, Any]:
    """Formt eine Ergebniszeile zu dem Satz, den das Panel liest."""
    n_ges,  min_ges,  max_ges  = zeile["n_ges"],  zeile["min_ges"],  zeile["max_ges"]
    n_jung, min_jung, max_jung = zeile["n_jung"], zeile["min_jung"], zeile["max_jung"]

    def teil(n: int, u: float | None, o: float | None) -> dict[str, Any]:
        ausschoepfung = _ausschoepfung(u, o, naht.ziel)
        ueber: bool = bool(
            naht.ziel and u is not None and o is not None
            and (u < naht.ziel[0] - 1e-9 or o > naht.ziel[1] + 1e-9)
        )
        return {
            "n": int(n or 0),
            "min": float(u) if u is not None else None,
            "max": float(o) if o is not None else None,
            "ausschoepfung": ausschoepfung,
            "ueberschreitung": ueber,
        }

    return {
        "gruppe": naht.gruppe, "name": naht.name,
        "ziel": list(naht.ziel) if naht.ziel else None,
        "gesamt": teil(n_ges, min_ges, max_ges),
        "jung": teil(n_jung, min_jung, max_jung),
    }


def spannen_erheben(tage: int = FENSTER_TAGE) -> dict[str, Any]:
    """Erhebt Ist-Spanne und Ausschoepfung jeder Naht in zwei Zeitfenstern.

    **Beide Fenster in einer Abfrage je Naht**, nicht in zweien: Der Vergleich
    ist die Aussage, und zwei getrennte Laeufe koennten verschiedene Zeilen
    sehen, wenn nebenher geschrieben wird.

    Vorbedingung: keine.
    Nachbedingung: Je Naht ein Satz mit beiden Fenstern. **Eine Naht ohne
        Werte faellt nicht weg** — sie traegt `n = 0`, und das ist eine
        Auskunft.
    Fehlerfaelle: Faellt eine einzelne Abfrage aus, traegt ihre Naht
        `fehler` und die uebrigen bleiben erhalten. Ein Ausfall soll die
        Tafel nicht leeren, sondern eine Luecke in ihr zeigen.

    Args:
        tage: Breite des jungen Fensters in Tagen.

    Returns:
        `{"tage": int, "naehte": [...], "fehler": int}`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if tage <= 0:
        raise ValueError(f"spannen_erheben: tage={tage} muss positiv sein")

    # ── Verarbeitung ────────────────────────────
    saetze: list[dict[str, Any]] = []
    fehler: int = 0

    for naht in NAEHTE:
        frist: str = f"{naht.zeitfeld} > NOW() - INTERVAL '{tage} days'"
        sql: str = f"""
            SELECT count(*)                                   AS n_ges,
                   min({naht.ausdruck})                       AS min_ges,
                   max({naht.ausdruck})                       AS max_ges,
                   count(*) FILTER (WHERE {frist})             AS n_jung,
                   min({naht.ausdruck}) FILTER (WHERE {frist}) AS min_jung,
                   max({naht.ausdruck}) FILTER (WHERE {frist}) AS max_jung
              FROM {naht.tabelle}
             WHERE {naht.bedingung}
        """
        try:
            zeile = db_manager.select_one(sql)
        except Exception as ausfall:
            # Fail loud, aber nicht toedlich: Die uebrigen Naehte tragen
            # ihre Aussage weiter, und die Luecke ist im Panel sichtbar.
            logger.error(
                "Naht-Spannen: Abfrage fuer '%s' (%s) fehlgeschlagen (%s: %s)",
                naht.name, naht.tabelle, type(ausfall).__name__, ausfall,
            )
            fehler += 1
            saetze.append({
                "gruppe": naht.gruppe, "name": naht.name,
                "ziel": list(naht.ziel) if naht.ziel else None,
                "fehler": str(ausfall),
                "gesamt": {"n": 0, "min": None, "max": None,
                           "ausschoepfung": None, "ueberschreitung": False},
                "jung": {"n": 0, "min": None, "max": None,
                         "ausschoepfung": None, "ueberschreitung": False},
            })
            continue

        leer: dict[str, Any] = {
            "n_ges": 0, "min_ges": None, "max_ges": None,
            "n_jung": 0, "min_jung": None, "max_jung": None,
        }
        saetze.append(_satz_bauen(naht, zeile or leer))

    # ── Ausgabe-Verifikation ────────────────────
    if len(saetze) != len(NAEHTE):
        raise RuntimeError(
            f"Naht-Spannen: {len(saetze)} Saetze fuer {len(NAEHTE)} Naehte — "
            "eine Naht ist unterwegs verlorengegangen"
        )

    ohne_ziel: int = sum(1 for s in saetze if s["ziel"] is None)
    logger.info(
        "Naht-Spannen: %d Naehte erhoben (%d Tage), %d ohne benannte "
        "Zielspanne, %d Abfragen gescheitert",
        len(saetze), tage, ohne_ziel, fehler,
    )
    return {"tage": tage, "naehte": saetze, "fehler": fehler}
