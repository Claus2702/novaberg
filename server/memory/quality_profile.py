"""Der Erzeuger der Qualitaetsprofile — `novaberg-thinking-faszination_k.md` §5, §6.

Ein Traeger, der oft genug wiedergekehrt ist, wird auf den sechs gesetzten
Dimensionen bewertet. Ein Modellaufruf je Traeger ist der Preis; die Daempfung
liegt in der Groesse selbst (§6.3): **Man fragt sich nicht beim ersten Mal, was
einen an einer Sache fasziniert.**

**Das Vokabular ist gesetzt, nicht geerntet.** Drei Ernteversuche sind am
30.08.2026 gemessen gescheitert — LZG-Themen (8.094 verschiedene Werte auf
12.040 Nennungen), Sachlage-Eigenschaften (Wissensluecken, keine Qualitaeten)
und die Ziele (bei sechs Gegenueber formgleich). Jeder gab die Form seines
Korpus zurueck statt einer Struktur. Deshalb steht der Satz im Schema und
dieses Modul fragt nur noch nach Auspraegungen.

**Und die Form der Frage ist der Unterschied**, nicht die Feinheit der Skala:
Der Versuch, dieselbe abstrakte Groesse ueber Cosine-Distanz zu gewinnen, ist
in Chat 114 gemessen gescheitert. Ein Modell, das jede Dimension einzeln mit
0.0/0.5/1.0 bewertet, traegt — wie bei den Raedern.
"""

import json
import logging

from config import (
    POSTGRES_URL,
    QUALITAET_KANON,
    QUALITAET_PROFIL_JE_LAUF,
    QUALITAET_STUFEN,
    get_node_config,
)
from ei.fascination import dominante_dimension, merkmalszug
from memory.repositories import quality_profile_repository as speicher
from services.model_services import BackgroundRequest, model_service

logger = logging.getLogger("ki_server.memory.quality_profile")

# Der Kern des Prompts. Die Beschreibungen stammen aus §6.1 und nennen je
# Dimension ihre Herkunft — nicht als Zierde: Ein Modell, das `weite` als
# »ausfuehrlich« liest statt als Kaplans *vastness*, bewertet eine andere
# Groesse, und niemand saehe es der Zahl an.
DIMENSIONS_ERKLAERUNG: str = """\
- komplexitaet: Wie viele unterscheidbare Teile und Beziehungen der Gegenstand traegt.
- ungewissheit: Wie viel offen bleibt. Wuerde eine Erklaerung den Reiz beenden?
- konflikt: Zwei Eigenschaften, die einander widersprechen. Nicht »guenstig«
  und nicht »stabil« allein — guenstig UND stabil zugleich.
- weite: Die Entfernung vom Greifbaren; Groessenordnungen, die den Massstab sprengen.
- schemasprengung: Der Gegenstand passt in kein vorhandenes Schema und verlangt,
  dass man es umbaut.
- bedrohungsrelevanz: Der Gegenstand beruehrt etwas, das gefaehrlich werden koennte."""


def _prompt_bauen(inhalt: str) -> str:
    """Baut die Bewertungsfrage fuer einen Traeger.

    **Drei Stufen, keine freie Skala.** Ein Raster von 0.0/0.5/1.0 ist die
    Bauart, die sich an den Raedern bewaehrt hat: Es zwingt zu einer
    Entscheidung, statt eine Scheingenauigkeit auf zwei Nachkommastellen zu
    erzeugen, die niemand belegen kann.

    **Und die Null ist ausdruecklich erlaubt.** Eine Groesse, die Faszination
    messen soll, muss auch Null sagen koennen (§6.2) — vier der 50 von Hand
    bewerteten Knoten lagen auf allen sechs Dimensionen unter 0,5, und das
    waren die richtigen vier.

    Rein. Vorbedingung: `inhalt` ist nicht leer. Prueft der Aufrufer.
    Nachbedingung: Ein Prompt, der genau die sechs Namen des Kanons nennt.
    """
    return (
        "Bewerte den folgenden Text auf sechs Dimensionen. Jede Dimension "
        "bekommt genau einen der drei Werte 0.0, 0.5 oder 1.0.\n\n"
        f"{DIMENSIONS_ERKLAERUNG}\n\n"
        "0.0 heisst: trifft nicht zu. 0.5: teilweise. 1.0: trifft deutlich zu.\n"
        "**0.0 ist eine gueltige Antwort** — die meisten Texte tragen nicht "
        "jede Dimension, und ein Text darf auf allen sechs bei 0.0 liegen.\n\n"
        "Antworte ausschliesslich mit einem JSON-Objekt, das genau diese "
        f"sechs Schluessel traegt: {', '.join(QUALITAET_KANON)}\n\n"
        f"TEXT:\n{inhalt}"
    )


def _json_lesen(text: str) -> dict | None:
    """Schaelt Codezaun und Leerraum ab und liest das Objekt.

    Vorbedingung: keine — `text` ist die rohe Antwort und darf alles sein.
    Nachbedingung: Das gelesene Objekt, oder None mit einer Zeile im Log.
    """
    # ── Eingabe-Validierung ─────────────────────
    roh: str = (text or "").strip()
    if not roh:
        logger.error(
            "Qualitaetsprofil: Modellantwort ist leer — verworfen; eine leere "
            "Antwort ist kein Profil aus lauter Nullen"
        )
        return None
    if roh.startswith("```"):
        roh = roh.split("\n", 1)[1] if "\n" in roh else roh[3:]
    if roh.endswith("```"):
        roh = roh[:-3]
    roh = roh.strip()

    # ── Verarbeitung ────────────────────────────
    try:
        gelesen = json.loads(roh)
    except json.JSONDecodeError as fehler:
        # Der Stacktrace zeigt hier auf `json.loads` und sagt nichts, was die
        # Meldung nicht schon traegt. Was den Ausfall erklaert, ist der Text
        # des Modells — und der steht daneben (das
        # unterscheidende Merkmal wird miterhoben).
        logger.error(  # noqa: TRY400
            f"Qualitaetsprofil: Antwort ist kein JSON ({fehler}) — verworfen; "
            f"erste 200 Zeichen: {roh[:200]!r}"
        )
        return None

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(gelesen, dict):
        logger.error(
            f"Qualitaetsprofil: Antwort ist ein {type(gelesen).__name__} statt "
            f"eines Objekts — verworfen"
        )
        return None
    return gelesen


def _schluessel_entraeumen(gelesen: dict) -> dict | None:
    """Zieht Leerraum aus den Schluesseln zusammen — und sagt es.

    `[gemessen]` 03.09.2026 im Erstlauf: **4 von 20 Traegern fielen aus, alle
    vier mit demselben Schluessel `un gewissheit`** — das Modell setzt ein
    Leerzeichen in einen Bezeichner, den es woertlich vorgegeben bekam.

    **Das ist keine stille Korrektur**: Sie greift nur
    bei Leerraum, sie bekommt ihre Zeile im Log, und die Kanon-Pruefung eine
    Stufe weiter bleibt scharf — ein erfundener Name faellt weiterhin durch.
    Ohne sie kostet ein Leerzeichen das ganze Profil, und der Traeger ist
    dauerhaft verloren: Der naechste Lauf sieht ihn ohne Kanten, ruft
    dasselbe Modell und bekommt dasselbe Leerzeichen.

    Vorbedingung: `gelesen` ist ein Objekt aus `_json_lesen`.
    Nachbedingung: Dasselbe Objekt mit zusammengezogenen Schluesseln und
        unveraenderter Schluesselzahl, oder None bei einer Kollision.
    """
    entraeumt: dict = {}
    berichtigt: list[str] = []
    for schluessel, wert in gelesen.items():
        sauber: str = "".join(str(schluessel).split())
        if sauber != schluessel:
            berichtigt.append(f"{schluessel!r} → {sauber!r}")
        entraeumt[sauber] = wert
    if berichtigt:
        logger.warning(
            f"Qualitaetsprofil: {len(berichtigt)} Schluessel trugen Leerraum "
            f"und wurden zusammengezogen: {', '.join(berichtigt)}"
        )

    # ── Ausgabe-Verifikation ────────────────────
    if len(entraeumt) != len(gelesen):
        logger.error(
            f"Qualitaetsprofil: Das Zusammenziehen der Schluessel erzeugte "
            f"eine Kollision ({len(gelesen)} → {len(entraeumt)}) — verworfen; "
            f"zwei verschiedene Angaben zu derselben Dimension sind keine "
            f"Berichtigung"
        )
        return None
    return entraeumt


def _antwort_lesen(text: str) -> dict[str, float] | None:
    """Liest ein Profil aus der Modellantwort, oder verwirft es laut.

    **Die Antwort eines Sprachmodells ist die unzuverlaessigste Quelle im
    System.** Geprueft wird deshalb gegen den **Kanon** und
    nicht gegen eine Teilmenge: Ein erfundener Dimensionsname und ein
    gueltiges »trifft nicht zu« sind sonst dasselbe Ergebnis.

    Vorbedingung: keine — `text` ist die rohe Antwort und darf alles sein.
    Nachbedingung: Ein Profil mit genau den sechs Namen des Kanons und
        Werten aus `QUALITAET_STUFEN`, oder None mit einer Zeile im Log, die
        sagt, woran es lag.
    """
    # ── Eingabe-Validierung ─────────────────────
    roh_objekt: dict | None = _json_lesen(text)
    if roh_objekt is None:
        return None
    gelesen: dict | None = _schluessel_entraeumen(roh_objekt)
    if gelesen is None:
        return None

    # ── Ausgabe-Verifikation ────────────────────
    erwartet: set[str] = set(QUALITAET_KANON)
    if set(gelesen) != erwartet:
        logger.error(
            f"Qualitaetsprofil: Schluesselsatz weicht vom Kanon ab — fehlend "
            f"{sorted(erwartet - set(gelesen))}, unerwartet "
            f"{sorted(set(gelesen) - erwartet)}; verworfen"
        )
        return None
    profil: dict[str, float] = {}
    for name in QUALITAET_KANON:
        wert = gelesen[name]
        if isinstance(wert, bool) or not isinstance(wert, (int, float)):
            logger.error(
                f"Qualitaetsprofil: '{name}' traegt {wert!r} und keine Zahl — "
                f"das ganze Profil verworfen"
            )
            return None
        if float(wert) not in QUALITAET_STUFEN:
            logger.error(
                f"Qualitaetsprofil: '{name}' traegt {wert}, erlaubt sind "
                f"{QUALITAET_STUFEN} — das ganze Profil verworfen, nicht "
                f"gerundet; eine stille Rundung machte eine erfundene Skala "
                f"von der vorgegebenen ununterscheidbar"
            )
            return None
        profil[name] = float(wert)
    return profil


def traeger_profilieren(
    postgres_url: str, knoten_id: int, inhalt: str, qualitaeten: dict[str, int]
) -> dict[str, float] | None:
    """Bewertet einen Traeger und schreibt sein Profil.

    **Alle sechs oder keine.** Ein Profil entsteht in einem Zug; eine
    teilweise geschriebene Bewertung waere von einem abgebrochenen Lauf nicht
    zu unterscheiden, und `profiles_load` meldet genau das als Defekt.

    Vorbedingung: `inhalt` ist nicht leer, `qualitaeten` traegt den
        vollstaendigen Kanon (aus `qualities_load`). Beides wird geprueft.
    Nachbedingung: Das geschriebene Profil, oder None — dann steht im Log,
        woran es lag, und es ist nichts geschrieben.

    Args:
        knoten_id: Der Traeger.
        inhalt: Sein Text, die Grundlage der Bewertung.
        qualitaeten: {dimension: id} aus `qualities_load`.

    Returns:
        {dimension: auspraegung} mit allen sechs Dimensionen, sonst None.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not inhalt or not inhalt.strip():
        logger.error(
            f"Qualitaetsprofil: Knoten {knoten_id} hat keinen Inhalt — "
            f"verworfen; ein leerer Text traegt keine Qualitaeten"
        )
        return None
    if set(qualitaeten) != set(QUALITAET_KANON):
        logger.error(
            f"Qualitaetsprofil: Der uebergebene Kanon ist unvollstaendig "
            f"({sorted(qualitaeten)}) — Knoten {knoten_id} nicht profiliert"
        )
        return None

    # ── Verarbeitung ────────────────────────────
    node_cfg: dict = get_node_config("qualitaet_profil")
    try:
        antwort = model_service.background.submit_sync(
            BackgroundRequest(
                messages=[{"role": "user", "content": _prompt_bauen(inhalt)}],
                modus="sprache",
                temperature=node_cfg.get("temperature", 0.0),
                max_output_tokens=node_cfg.get("max_output_tokens"),
                caller="pixie/qualitaet_profil",
            ),
            timeout=node_cfg.get("timeout_s", 600),
        )
    except Exception as fehler:  # noqa: BLE001 — der Aufrufer laeuft ueber viele Traeger weiter
        logger.exception(
            f"Qualitaetsprofil: Modellaufruf fuer Knoten {knoten_id} "
            f"fehlgeschlagen — {type(fehler).__name__}"
        )
        return None

    profil: dict[str, float] | None = _antwort_lesen(getattr(antwort, "text", ""))
    if profil is None:
        logger.error(
            f"Qualitaetsprofil: Knoten {knoten_id} nicht profiliert — die "
            f"Antwort war unbrauchbar; nichts geschrieben"
        )
        return None

    geschrieben: int = 0
    for name, auspraegung in profil.items():
        if speicher.quality_upsert(
            postgres_url, knoten_id, qualitaeten[name], auspraegung,
            quelle="pixie/qualitaet_profil",
        ) is not None:
            geschrieben += 1

    # ── Ausgabe-Verifikation ────────────────────
    if geschrieben != len(QUALITAET_KANON):
        logger.error(
            f"Qualitaetsprofil: Knoten {knoten_id} — nur {geschrieben} von "
            f"{len(QUALITAET_KANON)} Auspraegungen geschrieben; das Profil ist "
            f"unvollstaendig und wird beim naechsten Lauf nicht wieder "
            f"aufgegriffen, weil der Traeger jetzt Kanten traegt"
        )
        return None
    name, staerke = dominante_dimension(profil)
    logger.info(
        f"Qualitaetsprofil: Knoten {knoten_id} profiliert — dominant "
        f"'{name}' {staerke:.1f}, Merkmalszug {merkmalszug(profil):.4f}"
    )
    return profil


def profil_lauf(postgres_url: str = POSTGRES_URL, deckel: int = 0) -> dict:
    """Profiliert die naechsten Traeger, gedeckelt (Schritt des Tageslaufs).

    **Gedeckelt, nicht in einem Zug.** Am 03.09.2026 standen 368 Kandidaten
    im Bestand; ebenso viele Modellaufrufe passen nicht in einen
    Heartbeat-Platz. Bei `QUALITAET_PROFIL_JE_LAUF` fuellt sich der Bestand
    in rund drei Wochen, und ein Ausfall kostet einen Tag statt eines Laufs.

    **Ein Fehlschlag an einem Traeger beendet den Lauf nicht.** Die Zusicherung
    ist die Vollstaendigkeit der Buchfuehrung, nicht die des Ergebnisses:
    `versucht`, `profiliert` und `gescheitert` gehen auf, damit ein Lauf, der
    nichts fand, von einem, der nicht lief, unterscheidbar bleibt.

    **Ein Totalausfall ist dennoch ein Fehler** (seit 05.09.2026). Gehen
    `versucht > 0` und `profiliert == 0` zusammen, ist die Buchfuehrung in
    Ordnung und der Lauf trotzdem gescheitert — ohne diese Zeile schriebe der
    Tageslauf `erledigt`, und niemand erfuehre davon.

    Vorbedingung: keine — ein leerer Kandidatensatz ist der Normalfall,
        sobald der Bestand aufgeholt hat.
    Nachbedingung: {versucht, profiliert, gescheitert, traeger_gesamt,
        kanten_gesamt, error}. `error` ist None oder eine Meldung.
    """
    # ── Eingabe-Validierung ─────────────────────
    grenze: int = deckel if deckel > 0 else QUALITAET_PROFIL_JE_LAUF
    ergebnis: dict = {
        "versucht": 0, "profiliert": 0, "gescheitert": 0,
        "traeger_gesamt": 0, "kanten_gesamt": 0, "error": None,
    }
    qualitaeten: dict[str, int] = speicher.qualities_load(postgres_url)
    if not qualitaeten:
        ergebnis["error"] = (
            "Der Kanon der Qualitaeten ist nicht lesbar — kein Traeger profiliert"
        )
        logger.error(f"Qualitaetsprofil: {ergebnis['error']}")
        return ergebnis

    # ── Verarbeitung ────────────────────────────
    kandidaten: list[dict] = speicher.candidates_load(postgres_url, grenze)
    for kandidat in kandidaten:
        ergebnis["versucht"] += 1
        profil = traeger_profilieren(
            postgres_url, int(kandidat["id"]), str(kandidat["inhalt"]), qualitaeten
        )
        if profil is None:
            ergebnis["gescheitert"] += 1
        else:
            ergebnis["profiliert"] += 1

    # ── Ausgabe-Verifikation ────────────────────
    if ergebnis["versucht"] != ergebnis["profiliert"] + ergebnis["gescheitert"]:
        ergebnis["error"] = (
            f"Buchfuehrung geht nicht auf: {ergebnis['versucht']} versucht, "
            f"{ergebnis['profiliert']} profiliert, {ergebnis['gescheitert']} "
            f"gescheitert"
        )
        logger.error(f"Qualitaetsprofil: {ergebnis['error']}")
    elif ergebnis["versucht"] > 0 and ergebnis["profiliert"] == 0:
        # **Ein Totalausfall ist ein Fehler, kein Ergebnis** — gefunden am
        # 05.09.2026: Ein Lauf mit 20 versuchten und 0 profilierten Traegern
        # meldete `error: None`, weil die Buchfuehrung aufging (0 + 20 = 20).
        # Der Tageslauf haette `erledigt` ins hintergrund_log geschrieben.
        # Einzelne Fehlschlaege bleiben weiterhin nur gezaehlt: Sie sind der
        # erwartete Betrieb, ein Totalausfall ist es nicht.
        ergebnis["error"] = (
            f"Kein einziger von {ergebnis['versucht']} Traegern profiliert — "
            f"das ist ein Ausfall, kein leerer Kandidatensatz"
        )
        logger.error(f"Qualitaetsprofil: {ergebnis['error']}")
    traeger, kanten = speicher.profile_count(postgres_url)
    ergebnis["traeger_gesamt"] = traeger
    ergebnis["kanten_gesamt"] = kanten
    logger.info(
        f"Qualitaetsprofil: {ergebnis['profiliert']} von {ergebnis['versucht']} "
        f"Traegern profiliert ({ergebnis['gescheitert']} gescheitert); Bestand "
        f"{traeger} Traeger, {kanten} Kanten"
    )
    return ergebnis
