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
import re

logger = logging.getLogger("ki_server.sachlage")

# Die Klassen aus frames_k §3.1, wie der Sachlage-Prompt sie nennt.
OBJECT_CLASSES: frozenset[str] = frozenset({"objekt", "person", "ort", "vorgang", "anliegen"})

# Felder, die nur der Server schreibt. Kommen sie aus dem Modell, sind sie
# abgeschrieben oder erfunden.
SERVER_OWNED_OBJECT_FIELDS: tuple[str, ...] = ("quellen", "plausibilitaet", "recherche")

# Die Woerter der drei Kanons (Traeger, Kritikalitaet, Sprecher in sachlage.py).
# Als Wert einer gedeckten Eigenschaft sind sie keine Aussage ueber die Sache,
# sondern ein Feld, das an die falsche Stelle geraten ist. `[gemessen]`
# 13.09.2026, Labor: `"Entfernung zur Erde": "nachschlagen"` stand in `gedeckt`.
# Ein Zeuge haelt diese Menge gegen die Kanons, damit sie nicht auseinanderlaufen.
NO_VALUE_WORDS: frozenset[str] = frozenset({
    "nutzer", "welt", "nachschlagen", "kritisch", "unkritisch", "nova",
})

# Die Woerter, die als Sprecher taugen (SPRECHER_KANON in sachlage.py).
SPEAKER_WORDS: frozenset[str] = frozenset({"nutzer", "nova"})

_TRUE_TEXT: frozenset[str] = frozenset({"true", "ja", "1"})
_FALSE_TEXT: frozenset[str] = frozenset({"false", "nein", "0", ""})


def property_key(text: object) -> str:
    """Der Vergleichsschluessel fuer Eigenschaften und Objektnamen.

    casefold statt lower, und damit dieselbe Formel wie der Schluessel in der
    Datenbank (`memory.sachlage_properties.text_key`). `[gemessen]` zweite
    Kontrolle 13.09.2026: Mit lower blieben »Weißer Zwerg« und »WEISSER ZWERG«
    zwei Objekte, und die Datenbank loeste den einen Wert im selben Turn durch
    den anderen ab.
    """
    return " ".join(str(text or "").casefold().split())


def _as_value(roh: object) -> str | None:
    """Ein Wert ist Text oder eine Zahl mit Inhalt; alles andere ist kein Wert."""
    if isinstance(roh, bool) or roh is None:
        return None
    if isinstance(roh, (int, float)):
        return str(roh)
    if isinstance(roh, str) and roh.strip():
        return roh.strip()
    return None


def covered_value(roh: object) -> str | None:
    """Oeffentlich: derselbe Wertpruefer fuer jeden, der nach der Form nach `gedeckt` schreibt."""
    return _as_covered_value(roh)


def _as_covered_value(roh: object) -> str | None:
    """Ein Wert fuer `gedeckt`: ein Wert, der nicht nur aus Kanonwoertern besteht.

    `[gemessen 13.09.2026]` Im Bestand von 1771 gedeckten Werten waren 579 ein
    Kanonwort (»nutzer«, »nova«) und 86 die Vorlage des Prompts (»nutzer|nova«).
    """
    wert: str | None = _as_value(roh)
    if wert is None:
        return None
    teile: list[str] = [t for t in re.split(r"[\s|/,;]+", wert.casefold()) if t]
    if teile and all(t in NO_VALUE_WORDS for t in teile):
        return None
    return wert


def _as_name(roh: object) -> str | None:
    """Ein Eigenschaftsname ist Text oder eine Zahl mit Inhalt."""
    return _as_value(roh)


def _value_from_name(name: str, wert: object) -> tuple[str, str, str | None] | None:
    """Holt eine Angabe aus dem Namen, wenn der Wert nur ein Sprecherwort ist.

    `[gemessen 13.09.2026]` Im rohen Parse stand `"Temperatur: 2,725 Kelvin":
    "nutzer"` — die Angabe im Namen, der Sprecher im Wert. Nach der Regel
    »nichts verwerfen, was eine Aussage traegt« wird daraus Eigenschaft →
    Angabe, und das Sprecherwort wird zum Sprecher.

    Returns:
        (Eigenschaft, Angabe, Sprecher oder None), oder None ohne Angabe im Namen.
    """
    if not isinstance(wert, str) or ":" not in name:
        return None
    teile: list[str] = [t for t in re.split(r"[\s|/,;]+", wert.casefold()) if t]
    if not teile or not all(t in NO_VALUE_WORDS for t in teile):
        return None
    links, _, rechts = name.partition(":")
    if not links.strip() or not rechts.strip():
        return None
    sprecher: str | None = teile[0] if len(teile) == 1 and teile[0] in SPEAKER_WORDS else None
    return links.strip(), rechts.strip(), sprecher


def _split_covered(
    roh: object, name: str,
) -> tuple[dict[str, str], list[str], dict[str, str]]:
    """Zerlegt `gedeckt` in Eigenschaften mit Wert, Namen ohne Wert und Sprecherhinweise."""
    mit_wert: dict[str, str] = {}
    ohne_wert: list[str] = []
    sprecher: dict[str, str] = {}
    if roh is None:
        return mit_wert, ohne_wert, sprecher
    if isinstance(roh, dict):
        for eigenschaft, wert in roh.items():
            name_norm: str | None = _as_name(eigenschaft)
            if name_norm is None:
                continue
            geborgen = _value_from_name(name_norm, wert)
            if geborgen is not None:
                mit_wert[geborgen[0]] = geborgen[1]
                if geborgen[2]:
                    sprecher[geborgen[0]] = geborgen[2]
                logger.warning(
                    f"Sachlage-Form: Angabe an '{name}' stand im Namen "
                    f"{name_norm!r} — als {geborgen[0]!r} → {geborgen[1]!r} geborgen"
                )
                continue
            wert_norm: str | None = _as_covered_value(wert)
            if wert_norm is None:
                ohne_wert.append(name_norm)
            elif any(property_key(k) == property_key(name_norm) for k in mit_wert):
                logger.warning(
                    f"Sachlage-Form: '{name_norm}' an '{name}' steht in anderer "
                    f"Schreibweise schon in 'gedeckt' — der erste Wert bleibt"
                )
            else:
                mit_wert[name_norm] = wert_norm
        if ohne_wert:
            logger.warning(
                f"Sachlage-Form: {len(ohne_wert)} Eigenschaft(en) an '{name}' in "
                f"'gedeckt' ohne Wert — nach offen: {ohne_wert}"
            )
        return mit_wert, ohne_wert, sprecher
    eintraege: list = roh if isinstance(roh, list) else [roh]
    for eintrag in eintraege:
        name_norm = _as_name(eintrag)
        if name_norm is not None:
            ohne_wert.append(name_norm)
    logger.warning(
        f"Sachlage-Form: 'gedeckt' an '{name}' ist {type(roh).__name__} statt "
        f"dict — {len(ohne_wert)} Name(n) ohne Wert nach offen: {ohne_wert}"
    )
    return mit_wert, ohne_wert, sprecher


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
            wert_norm: str | None = _as_covered_value(wert)
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


def merge_same_name_objects(objekte: list[dict]) -> list[dict]:
    """Fuehrt Objekte gleichen Namens zu einem zusammen.

    `[gemessen 13.09.2026]` Das Modell fuehrte »Crab-Pulsar« zweimal, je mit
    einer offenen Eigenschaft. Das Gedaechtnis kennt je Paar und Name genau
    ein Objekt; zwei Eintraege gleichen Namens sind zwei Haelften derselben
    Sache.

    Vorbedingung: Jedes Objekt ist durch `normalize_object_form` gelaufen.
    Nachbedingung: Je Namensschluessel ein Objekt, in der Reihenfolge des
        ersten Auftretens: akut, wenn eines akut war; `gedeckt` vereinigt
        (das erste gewinnt); `offen` vereinigt ohne Gedecktes und Dubletten
        (bei latentem Ergebnis leer); die dict-Felder `traeger`,
        `kritikalitaet`, `sprecher`, `quellen` vereinigt (das erste gewinnt).
    """
    zusammen: dict[str, dict] = {}
    for objekt in objekte:
        schluessel: str = property_key(objekt["name"])
        erstes: dict | None = zusammen.get(schluessel)
        if erstes is None:
            zusammen[schluessel] = objekt
            continue
        logger.warning(
            f"Sachlage-Form: Objekt '{objekt['name']}' steht zweimal im Artefakt — zusammengefuehrt"
        )
        erstes["akut"] = bool(erstes.get("akut") or objekt.get("akut"))
        vorhandene: set[str] = {property_key(k) for k in erstes["gedeckt"]}
        for eigenschaft, wert in (objekt.get("gedeckt") or {}).items():
            if property_key(eigenschaft) not in vorhandene:
                erstes["gedeckt"][eigenschaft] = wert
                vorhandene.add(property_key(eigenschaft))
        for feld in ("traeger", "kritikalitaet", "sprecher", "quellen"):
            if isinstance(objekt.get(feld), dict):
                ziel: object = erstes.setdefault(feld, {})
                if isinstance(ziel, dict):
                    for k, v in objekt[feld].items():
                        ziel.setdefault(k, v)
        erstes["offen"] = list(erstes.get("offen") or []) + list(objekt.get("offen") or [])
    for objekt in zusammen.values():
        gedeckt_keys: set[str] = {property_key(k) for k in objekt["gedeckt"]}
        offen: list[str] = []
        gesehen: set[str] = set()
        for eigenschaft in objekt.get("offen") or []:
            k: str = property_key(eigenschaft)
            if k not in gedeckt_keys and k not in gesehen:
                gesehen.add(k)
                offen.append(eigenschaft)
        objekt["offen"] = offen if objekt["akut"] else []
    return list(zusammen.values())


def normalize_object_form(objekt: dict, from_model: bool, gate: bool = True) -> dict:
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
        gate: Die Smalltalk-Schranke hier anwenden. False, wenn der Aufrufer
            danach Objekte gleichen Namens zusammenfuehrt — dann erst weiss
            er, ob das Objekt akut ist (`merge_same_name_objects` schraenkt ein).

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

    gedeckt, ohne_wert, sprecher_hinweise = _split_covered(objekt.get("gedeckt"), name)
    if sprecher_hinweise:
        vorhanden: object = objekt.get("sprecher")
        sprecher_neu: dict = dict(vorhanden) if isinstance(vorhanden, dict) else {}
        for eigenschaft, wer in sprecher_hinweise.items():
            sprecher_neu.setdefault(eigenschaft, wer)
        objekt["sprecher"] = sprecher_neu
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

    if gate and not objekt["akut"] and offen:
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
