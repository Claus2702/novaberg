"""Der Korpus: Turn-Paare mit Rohwert und Zeugenurteil.

Die Kalibrierung vergleicht zwei Lesarten desselben Turns. Damit der Vergleich
etwas prueft, duerfen sich beide Seiten nicht vorher treffen: Der Rohwert
entsteht aus `fuehrung_messen` wie zur Laufzeit, das Urteil aus einem Modell,
das nur zwei Texte sieht. Dieses Modul stellt die linke Seite her.

**Woher die Bestandteile kommen — und warum drei Quellen noetig sind.**

| Bestandteil | Quelle |
|---|---|
| Nutzer-Turn, Novas Vorantwort | `pipeline_log`, `art='turn_roh'` (dauerhaft, von der Retention ausgenommen) |
| Modus beider Seiten | derselbe Rohturn, `user_emotion.mode` / `nova_emotion.mode` |
| Intentionen (M1) | KZG-Hash, ueber `verbindung` am `turn_id` |
| Embeddings (M2) | frisch gerechnet aus den Rohtexten |

**Der Umweg ueber `verbindung` ist kein Umstand, sondern die Bedingung.** Der
Rohturn traegt `intent` als Einzelwert; `fuehrung_messen` prueft die Liste
`user_intentionen` gegen GV_INITIATIVE_FUEHREND, und die steht nur am
KZG-Eintrag. Der Schluessel dorthin ist `verbindung.turn_id`, **nicht** die
Zeitnaehe: Ein Zeit-Join ueber dieselben Daten ergab in Chat 116
Uebereinstimmungen unter Zufallsniveau (108 Zuordnungen aus 74 Eintraegen).

**Der Versatz bleibt bei 0.0.** Kalibriert wird die Schwelle, nicht die
Charakterverschiebung. Ginge der Versatz in den Rohwert ein, verschoebe er die
gefundene Schwelle um seinen eigenen Betrag, und beide zusammen zaehlten
doppelt (novaberg-gv-initiative_k.md §5).

Konzept: novaberg-gv-initiative_k.md §7, §12.
"""

import json
import logging
from dataclasses import dataclass

from config import (
    INTENT_KANON,
    KALIBRIERUNG_MAX_TURN_ZEICHEN,
    KALIBRIERUNG_MIN_TURNS,
)
from ei.initiative import fuehrung_messen
from graph.personality import Emotion, Personality
from memory.kzg import _kzg_key  # noqa: F401  — Key-Form dokumentiert hier
from services.model_services import model_service
from services.model_services.types import EmbedRequest
from tools.db_manager import db_manager
from tools.redis_manager import redis_manager

logger = logging.getLogger("ki_server.agents.kalibrierung.korpus")


_SQL_ROHTURNS: str = """
SELECT turn_id,
       inhalt->>'user_prompt'                AS user_prompt,
       inhalt->>'response'                   AS response,
       inhalt->'user_emotion'->>'mode'       AS user_modus,
       inhalt->'nova_emotion'->>'mode'       AS nova_modus,
       erstellt_am
FROM   pipeline_log
WHERE  art          = 'turn_roh'
  AND  user_id      = %s
  AND  character_id = %s
ORDER  BY erstellt_am
"""

_SQL_KZG_KEY: str = """
SELECT kzg_id
FROM   verbindung
WHERE  turn_id = %s
ORDER  BY erstellt_am
LIMIT  1
"""


@dataclass
class Turnpaar:
    """Ein Nutzer-Turn mit allem, was seine Fuehrungsmessung braucht.

    Zusammen geladen, zusammen gerechnet, zusammen verworfen — deshalb eine
    Klasse und keine flachen Felder
    (`novaberg-lesson_l_klassen-statt-flache-keys.md`).
    `vor_antwort` und `vor_modus` stammen aus dem
    **vorigen** Rohturn desselben Paars; der erste Turn einer Kette hat keine
    Vorantwort und faellt deshalb heraus.
    """

    turn_id:      str
    user_prompt:  str    # Rohtext des Nutzer-Turns
    user_modus:   str    # Modus dieses Turns, aus der Perzeption
    vor_antwort:  str    # Rohtext von Novas letzter Antwort
    vor_modus:    str    # Modus jener Antwort
    intentionen:  list   # aus dem KZG-Eintrag, ueber verbindung gefunden


def rohturns_laden(user_id: str, character_id: str) -> list[Turnpaar]:
    """Laedt die Rohturns eines Paars und bildet daraus Turnpaare.

    Vorbedingung: `user_id` und `character_id` sind gesetzt.
    Nachbedingung: chronologische Liste; jeder Eintrag traegt einen nicht
    leeren Nutzer-Turn und eine nicht leere Vorantwort.
    Fehlerfaelle: Kein Bestand — leere Liste und eine `error`-Zeile, denn ein
    Paar ohne Rohturns kann nicht kalibriert werden. Einzelne Turns ohne Text
    oder ohne Modus werden uebersprungen und gezaehlt; ihre Zahl steht im Log,
    weil ein stiller Verlust die Fallzahl unbemerkt senken wuerde.

    Returns:
        Die Turnpaare.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id or not character_id:
        logger.error(
            f"Korpus: unvollstaendiges Paar (user_id='{user_id}', "
            f"character_id='{character_id}') — nichts zu laden"
        )
        return []

    rohturns: list[dict] = db_manager.select(
        _SQL_ROHTURNS, (user_id, character_id),
    )

    if not rohturns:
        logger.error(
            f"Korpus: keine Rohturns fuer {user_id}:{character_id} — "
            f"ohne Bestand keine Kalibrierung"
        )
        return []

    # ── Verarbeitung ────────────────────────────
    paare:        list[Turnpaar] = []
    ohne_text:    int = 0
    ohne_modus:   int = 0
    zu_lang:      int = 0

    for i in range(1, len(rohturns)):
        vorher = rohturns[i - 1]
        jetzt  = rohturns[i]

        prompt:  str = (jetzt.get("user_prompt") or "").strip()
        antwort: str = (vorher.get("response") or "").strip()

        if not prompt or not antwort:
            ohne_text += 1
            continue

        # Eigene Messturns aussortieren. Sie sind thematisch zulaessig, aber in
        # ihrer Bauart kein Gespraechsverhalten — dichte Fachprosa mit Formeln
        # und Literaturstellen, wo das Gespraech im Median 92 Zeichen hat. Der
        # Schnitt liegt in einer Luecke der Laengenverteilung und nicht an einem
        # gesetzten Wert; die Herleitung steht bei der Konstante.
        if len(prompt) >= KALIBRIERUNG_MAX_TURN_ZEICHEN:
            zu_lang += 1
            continue

        user_modus: str = jetzt.get("user_modus") or ""
        vor_modus:  str = vorher.get("nova_modus") or ""

        if not user_modus or not vor_modus:
            ohne_modus += 1

        paare.append(Turnpaar(
            turn_id     = jetzt["turn_id"],
            user_prompt = prompt,
            user_modus  = user_modus,
            vor_antwort = antwort,
            vor_modus   = vor_modus,
            intentionen = _intentionen_laden(jetzt["turn_id"]),
        ))

    # ── Ausgabe-Verifikation ────────────────────
    logger.info(
        f"Korpus {user_id}:{character_id}: {len(rohturns)} Rohturns → "
        f"{len(paare)} Turnpaare "
        f"(uebersprungen: {ohne_text} ohne Text; "
        f"{zu_lang} ueber {KALIBRIERUNG_MAX_TURN_ZEICHEN} Zeichen; "
        f"{ohne_modus} ohne Modus, diese bleiben drin und verlieren nur M3)"
    )

    if len(paare) < KALIBRIERUNG_MIN_TURNS:
        logger.error(
            f"Korpus {user_id}:{character_id}: nur {len(paare)} Turnpaare nach "
            f"dem Laengenfilter, verlangt sind {KALIBRIERUNG_MIN_TURNS} — die "
            f"Grundlage ist zu schmal. NICHT die Grenze heben: Sie liegt in "
            f"einer Luecke der Verteilung, und eine geschlossene Luecke ist ein "
            f"Befund ueber den Bestand"
        )

    return paare


def _intentionen_laden(turn_id: str) -> list:
    """Holt die Intentionen eines Turns ueber `verbindung` aus dem KZG.

    Das Feld ist eine **JSON-Liste**, geschrieben mit `json.dumps`
    (`memory/kzg.py`, `agents/kzg/speicher.py`), und wird entsprechend geparst.
    Ein Split an Kommas liefert Bruchstuecke mit Klammer und
    Anfuehrungszeichen — `["reflexion"` statt `reflexion`.

    Vorbedingung: `turn_id` ist gesetzt.
    Nachbedingung: Liste der Intentionen; leer, wenn der Turn keinen
    KZG-Eintrag hat oder dieser abgelaufen ist.
    Fehlerfaelle: Kein Verbindungs-Eintrag oder abgelaufener KZG-Key — beides
    ist ein **legitimer Leerfall** und kein Fehler: Ein Turn unter der
    Salienz-Schwelle kommt nie ins KZG, und ein alter faellt per TTL heraus.
    Die Folge ist, dass M1 fuer diesen Turn fehlt — `fuehrung_messen` benennt
    das dann in `fehlend`, statt es als 0 zu verrechnen.
    Ein **vorhandenes, aber unlesbares** Feld ist etwas anderes und wird laut
    gemeldet: Es ist ein Defekt und kein Leerfall. Zurueckgegeben wird dann
    ebenfalls die leere Liste, damit M1 als `fehlend` gilt — der einzige
    ehrliche Zustand. Der Unterschied ist nicht kosmetisch: Eine gefuellte
    Liste mit unpassenden Werten laesst M1 als **"nicht fuehrend"** durchgehen
    und traegt damit ein hartes -1.0 in jeden Turn, wo eine benannte Luecke
    stehen muesste.

    Returns:
        Die Intentionen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not turn_id:
        logger.error("Korpus: leere turn_id — Intentionen nicht ladbar")
        return []

    # ── Verarbeitung ────────────────────────────
    zeile: dict | None = db_manager.select_one(_SQL_KZG_KEY, (turn_id,))
    if not zeile:
        return []

    roh = redis_manager.client.hget(zeile["kzg_id"], "intentionen")
    if not roh:
        return []

    try:
        gelesen = json.loads(roh)
    except (TypeError, ValueError) as fehler:
        logger.exception(
            f"{type(fehler).__name__}: Korpus: Intentionen von "
            f"{zeile['kzg_id']} nicht lesbar — M1 fehlt fuer diesen Turn"
        )
        return []

    if not isinstance(gelesen, list):
        logger.error(
            f"Korpus: Intentionen von {zeile['kzg_id']} sind "
            f"{type(gelesen).__name__}, erwartet ist eine Liste — "
            f"M1 fehlt fuer diesen Turn"
        )
        return []

    # ── Ausgabe-Verifikation ────────────────────
    # Zugehoerigkeit zum Kanon pruefen, nicht nur Nichtleere. Ein Wert ausserhalb
    # von INTENT_KANON ist ein **Defekt**, kein "nicht fuehrend": Ohne diese
    # Pruefung ist ein Bruchstueck eines Transportformats von einer gueltigen
    # Intention, die nur nicht in GV_INITIATIVE_FUEHREND steht, nicht zu
    # unterscheiden — beides ergibt "kein Treffer".
    #
    # Sind alle Werte fremd, ist die Rueckgabe leer und M1 gilt als `fehlend`.
    # Das ist der Zustand, den der Defekt zwei Monate verdeckt hat: eine
    # benannte Luecke statt eines stillen Beitrags von -1.0.
    werte:   list[str] = [str(teil).strip() for teil in gelesen if str(teil).strip()]
    bekannt: list[str] = [wert for wert in werte if wert in INTENT_KANON]
    fremd:   list[str] = [wert for wert in werte if wert not in INTENT_KANON]

    if fremd:
        logger.error(
            f"Korpus: Intentionen von {zeile['kzg_id']} tragen "
            f"{len(fremd)} Wert(e) ausserhalb des Kanons: {fremd} — verworfen, "
            f"{len(bekannt)} von {len(werte)} bleiben"
        )

    return bekannt


def rohwert_rechnen(
    paar:              Turnpaar,
    embedding_prompt:  list[float] | None,
    embedding_antwort: list[float] | None,
) -> float | None:
    """Rechnet den Initiative-Rohwert eines Turnpaars nach.

    Ruft dieselbe Funktion, die zur Laufzeit rechnet, mit einem State, der die
    drei Quellen traegt. **Ohne Charakter-Versatz** — kalibriert wird die
    Schwelle, und ein mitgerechneter Versatz verschoebe sie um seinen eigenen
    Betrag.

    Vorbedingung: `paar` stammt aus `rohturns_laden`.
    Nachbedingung: Rohwert in [-1, +1] oder None, wenn kein Mass verfuegbar war.
    Fehlerfaelle: Kein Mass — `fuehrung_messen` meldet das selbst laut; hier
    wird None zurueckgegeben und der Turn faellt aus dem Korpus. Er darf nicht
    mit einem Ersatzwert einziehen: Ein Ausfall auf einer regulaeren
    Achsenposition ist genau der Defekt, den die neue Achse abgeloest hat.

    Returns:
        Der Rohwert oder None.
    """
    # ── Eingabe-Validierung ─────────────────────
    external = Personality(emotion=Emotion(mode=paar.user_modus))

    state: dict = {
        "external":         external,
        "prompt_embedding": embedding_prompt,
        "user_intentionen": paar.intentionen,
    }

    # ── Verarbeitung ────────────────────────────
    fuehrung = fuehrung_messen(
        state,
        vorher_embedding = embedding_antwort,
        vorher_modus     = paar.vor_modus,
        versatz          = 0.0,
    )

    # ── Ausgabe-Verifikation ────────────────────
    return fuehrung.rohwert


def embedding_holen(text: str) -> list[float] | None:
    """Embeddet einen Rohtext ueber den EmbedWorker.

    Vorbedingung: `text` ist nicht leer.
    Nachbedingung: normierter Vektor der Modell-Dimension.
    Fehlerfaelle: leerer Text oder leere Antwort — `error` und None. Ein
    Nullvektor waere hier besonders schaedlich: Er ergaebe einen
    Cosinus-Abstand von exakt 1.0 und damit einen mittleren Themensprung, wo
    gar nichts gemessen wurde.

    Returns:
        Der Vektor oder None.
    """
    # ── Eingabe-Validierung ─────────────────────
    sauber: str = (text or "").strip()
    if not sauber:
        logger.error("Korpus: leerer Text — kein Embedding")
        return None

    # ── Verarbeitung ────────────────────────────
    # Wie beim Zeugen: Ein Ausfall kostet den Turn, nicht den Lauf.
    try:
        antwort = model_service.embed.submit_sync(EmbedRequest(text=sauber))
    except Exception as fehler:
        logger.exception(
            f"{type(fehler).__name__}: Korpus: Embedding fehlgeschlagen "
            f"— Turn verliert M2"
        )
        return None

    vektor: list[float] = antwort.embedding

    # ── Ausgabe-Verifikation ────────────────────
    if not vektor:
        logger.error(
            f"Korpus: EmbedWorker lieferte keinen Vektor fuer "
            f"'{sauber[:60]}...' — Turn verliert M2"
        )
        return None

    return vektor
