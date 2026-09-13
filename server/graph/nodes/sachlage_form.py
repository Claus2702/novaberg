"""Die Form des Sachlage-Artefakts — was ein Objekt tragen darf, bevor es gelesen wird.

**Anlass (12.09.2026, 18:55 UTC):** Das Modell lieferte `gedeckt` als Liste von
Eigenschaftsnamen. Die Pruefung des Artefakts normalisierte nur die Felder der
Scheiben 8 bis 10; eine Lesestelle rief `.items()` und riss den Turn ab, drei
weitere liefen mit der falschen Form weiter (`LAGE-FORMPRUEFUNG-UNVOLLSTAENDIG`).

**Die Regel (Entscheidung des Eigentuemers, 13.09.2026):** Eine Eigenschaft ist
*gedeckt*, wenn sie einen Wert hat — `gedeckt` ist eine Zuordnung Eigenschaft →
Wert. **Ohne Wert ist sie offen.** Darum wird hier nichts verworfen, was eine
Aussage traegt: Ein Name ohne Wert wandert nach `offen`, ein Wert, der unter
`offen` stand, nach `gedeckt`. Verworfen wird nur, was keine Eigenschaft ist
(kein Text, leer, doppelt).

**Zwei Aufrufer, zwei Quellen.** Der frische Parse (`from_model=True`) darf keine
Felder tragen, die der Server selbst schreibt — `quellen` (Scheibe 6),
`plausibilitaet` (7), `recherche` (8): Ein Modell, das sie aus der vorigen Blase
abschreibt oder erfindet, erzeugte sonst ungepruefte Herkunft. Die vorige Blase
aus Redis (`from_model=False`) behaelt sie, wird aber auf ihre Form gehalten —
ein gelesener Wert ist eine externe Quelle, auch wenn dasselbe System ihn schrieb.

Nicht hier: `traeger`, `kritikalitaet`, `sprecher` — sie haben ihre Normalisierer
in `sachlage.py` und laufen **nach** dieser Pruefung, weil sie gegen `offen` und
`gedeckt` gehalten werden.
"""

import logging

logger = logging.getLogger("ki_server.sachlage")

# Die Klassen aus frames_k §3.1, wie der Sachlage-Prompt sie nennt.
OBJECT_CLASSES: frozenset[str] = frozenset({"objekt", "person", "ort", "vorgang", "anliegen"})

# Felder, die nur der Server schreibt. Kommen sie aus dem Modell, sind sie
# abgeschrieben oder erfunden.
SERVER_OWNED_OBJECT_FIELDS: tuple[str, ...] = ("quellen", "plausibilitaet", "recherche")

_TRUE_TEXT: frozenset[str] = frozenset({"true", "ja", "1"})
_FALSE_TEXT: frozenset[str] = frozenset({"false", "nein", "0", ""})


def property_key(text: object) -> str:
    """Der Vergleichsschluessel einer Eigenschaft: Kleinschreibung, ein Leerzeichen."""
    return " ".join(str(text).lower().split())


def _as_value(roh: object) -> str | None:
    """Ein Wert ist Text oder eine Zahl mit Inhalt; alles andere ist kein Wert."""
    if isinstance(roh, bool) or roh is None:
        return None
    if isinstance(roh, (int, float)):
        return str(roh)
    if isinstance(roh, str) and roh.strip():
        return roh.strip()
    return None


def _as_name(roh: object) -> str | None:
    """Ein Eigenschaftsname ist Text oder eine Zahl mit Inhalt."""
    return _as_value(roh)


def _split_covered(roh: object, name: str) -> tuple[dict[str, str], list[str]]:
    """Zerlegt `gedeckt` in Eigenschaften mit Wert und Namen ohne Wert."""
    mit_wert: dict[str, str] = {}
    ohne_wert: list[str] = []
    if roh is None:
        return mit_wert, ohne_wert
    if isinstance(roh, dict):
        for eigenschaft, wert in roh.items():
            name_norm: str | None = _as_name(eigenschaft)
            if name_norm is None:
                continue
            wert_norm: str | None = _as_value(wert)
            if wert_norm is None:
                ohne_wert.append(name_norm)
            else:
                mit_wert[name_norm] = wert_norm
        if ohne_wert:
            logger.warning(
                f"Sachlage-Form: {len(ohne_wert)} Eigenschaft(en) an '{name}' in "
                f"'gedeckt' ohne Wert — nach offen: {ohne_wert}"
            )
        return mit_wert, ohne_wert
    eintraege: list = roh if isinstance(roh, list) else [roh]
    for eintrag in eintraege:
        name_norm = _as_name(eintrag)
        if name_norm is not None:
            ohne_wert.append(name_norm)
    logger.warning(
        f"Sachlage-Form: 'gedeckt' an '{name}' ist {type(roh).__name__} statt "
        f"dict — {len(ohne_wert)} Name(n) ohne Wert nach offen: {ohne_wert}"
    )
    return mit_wert, ohne_wert


def _split_open(roh: object, name: str) -> tuple[dict[str, str], list[str]]:
    """Zerlegt `offen` in Namen ohne Wert — und Werte, die dort nicht hingehoeren."""
    mit_wert: dict[str, str] = {}
    namen: list[str] = []
    if roh is None:
        return mit_wert, namen
    if isinstance(roh, dict):
        for eigenschaft, wert in roh.items():
            name_norm: str | None = _as_name(eigenschaft)
            if name_norm is None:
                continue
            wert_norm: str | None = _as_value(wert)
            if wert_norm is None:
                namen.append(name_norm)
            else:
                mit_wert[name_norm] = wert_norm
        logger.warning(
            f"Sachlage-Form: 'offen' an '{name}' ist dict statt Liste — "
            f"{len(mit_wert)} mit Wert nach gedeckt, {len(namen)} bleiben offen"
        )
        return mit_wert, namen
    eintraege: list = roh if isinstance(roh, list) else [roh]
    verworfen: int = 0
    for eintrag in eintraege:
        name_norm = _as_name(eintrag)
        if name_norm is None:
            verworfen += 1
            continue
        namen.append(name_norm)
    if not isinstance(roh, list) or verworfen:
        logger.warning(
            f"Sachlage-Form: 'offen' an '{name}' ({type(roh).__name__}) — "
            f"{verworfen} Eintrag/Eintraege ohne Namen verworfen"
        )
    return mit_wert, namen


def _as_bool(roh: object, name: str) -> bool:
    """`akut` als Wahrheitswert; eine unlesbare Form gilt als latent."""
    if isinstance(roh, bool):
        return roh
    if isinstance(roh, (int, float)) and roh in (0, 1):
        return bool(roh)
    if isinstance(roh, str) and roh.strip().lower() in _TRUE_TEXT | _FALSE_TEXT:
        return roh.strip().lower() in _TRUE_TEXT
    if roh is not None:
        logger.warning(
            f"Sachlage-Form: 'akut' an '{name}' ist {roh!r} — als latent gelesen"
        )
    return False


def _checked_sources(roh: object, gedeckt: dict[str, str], name: str) -> dict[str, dict]:
    """`quellen` der vorigen Blase: nur Zuordnungen an gedeckten Eigenschaften."""
    if not isinstance(roh, dict):
        if roh is not None:
            logger.warning(
                f"Sachlage-Form: 'quellen' an '{name}' ist {type(roh).__name__} — verworfen"
            )
        return {}
    gedeckt_keys: set[str] = {property_key(k) for k in gedeckt}
    quellen: dict[str, dict] = {}
    for eigenschaft, quelle in roh.items():
        if isinstance(quelle, dict) and property_key(eigenschaft) in gedeckt_keys:
            quellen[str(eigenschaft)] = quelle
    if len(quellen) != len(roh):
        logger.warning(
            f"Sachlage-Form: {len(roh) - len(quellen)} Quelle(n) an '{name}' ohne "
            f"dict oder ohne gedeckte Eigenschaft — verworfen"
        )
    return quellen


def normalize_object_form(objekt: dict, from_model: bool) -> dict:
    """Stellt die Form eines Objekts her: `gedeckt` mit Werten, `offen` ohne.

    Vorbedingung: `objekt` ist ein dict mit nicht leerem `name` (der Aufrufer
        prueft das und verwirft sonst das Artefakt).
    Nachbedingung: `gedeckt` ist ein dict Text → Text mit nicht leeren Werten;
        `offen` ist eine Liste von Texten ohne Dubletten und ohne Eigenschaft,
        die gedeckt ist; ein latentes Objekt hat leeres `offen`; `akut` ist
        bool; `klasse` fehlt oder steht im Kanon. Mit `from_model` fehlen die
        Felder des Servers, sonst sind sie auf ihre Form gehalten.
    Fehlerfaelle: Keine Ausnahme — jede Abweichung wird laut benannt und
        nach der Regel des Eigentuemers eingeordnet.

    Args:
        objekt: Das Objekt, wird an Ort und Stelle normalisiert.
        from_model: True fuer den frischen Parse, False fuer die vorige Blase.

    Returns:
        Dasselbe Objekt.
    """
    # ── Eingabe-Validierung ─────────────────────
    name: str = str(objekt.get("name", "")).strip()
    objekt["name"] = name

    # ── Verarbeitung ────────────────────────────
    objekt["akut"] = _as_bool(objekt.get("akut"), name)

    klasse: object = objekt.get("klasse")
    if klasse is not None:
        klasse_norm: str = str(klasse).strip().lower()
        if klasse_norm in OBJECT_CLASSES:
            objekt["klasse"] = klasse_norm
        else:
            logger.warning(
                f"Sachlage-Form: Klasse {klasse!r} an '{name}' steht nicht im "
                f"Kanon {sorted(OBJECT_CLASSES)} — entfernt"
            )
            del objekt["klasse"]

    gedeckt, ohne_wert = _split_covered(objekt.get("gedeckt"), name)
    werte_aus_offen, offen_namen = _split_open(objekt.get("offen"), name)
    for eigenschaft, wert in werte_aus_offen.items():
        gedeckt.setdefault(eigenschaft, wert)

    gedeckt_keys: set[str] = {property_key(k) for k in gedeckt}
    offen: list[str] = []
    gesehen: set[str] = set()
    for eigenschaft in offen_namen + ohne_wert:
        schluessel: str = property_key(eigenschaft)
        if schluessel in gedeckt_keys or schluessel in gesehen:
            continue
        gesehen.add(schluessel)
        offen.append(eigenschaft)

    if not objekt["akut"] and offen:
        logger.info(
            f"Sachlage-Form: latentes Objekt '{name}' trug {len(offen)} offene "
            f"Eigenschaft(en) — geleert (Smalltalk-Schranke)"
        )
        offen = []

    objekt["gedeckt"] = gedeckt
    objekt["offen"] = offen

    if from_model:
        entfernt: list[str] = [f for f in SERVER_OWNED_OBJECT_FIELDS if f in objekt]
        for feld in entfernt:
            del objekt[feld]
        if entfernt:
            logger.warning(
                f"Sachlage-Form: das Modell lieferte an '{name}' Felder des "
                f"Servers {entfernt} — entfernt"
            )
    else:
        if "quellen" in objekt:
            objekt["quellen"] = _checked_sources(objekt["quellen"], gedeckt, name)
        for feld, typ in (("plausibilitaet", list), ("recherche", dict)):
            if feld in objekt and not isinstance(objekt[feld], typ):
                logger.warning(
                    f"Sachlage-Form: '{feld}' an '{name}' ist "
                    f"{type(objekt[feld]).__name__} statt {typ.__name__} — verworfen"
                )
                del objekt[feld]

    # ── Ausgabe-Verifikation ────────────────────
    doppelt: set[str] = {property_key(o) for o in objekt["offen"]} & {
        property_key(k) for k in objekt["gedeckt"]
    }
    if doppelt:
        raise ValueError(f"Sachlage-Form: {sorted(doppelt)} zugleich offen und gedeckt")
    return objekt
