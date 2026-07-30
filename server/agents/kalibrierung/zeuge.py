"""Der Zeuge: eine Lesart der Fuehrung, die die Achse nicht kennt.

Dem Modell werden **ausschliesslich zwei Texte** vorgelegt — der eine Turn und
seine Antwort. Keine Achse, kein Sektor, kein Cluster, kein einzelnes Mass.
Gefragt wird nur: Hat B die Richtung gesetzt?

**Warum A und B und nicht "Nutzer" und "Assistentin".** Mit den echten Rollen
reist eine Vorannahme mit: Ein Modell weiss, dass eine Assistentin antwortet
und ein Nutzer fragt, und liest die Fuehrung daraus statt aus dem Text. Mit A
und B muss es die Texte lesen. Ob das gelingt, prueft die Positions-Kontrolle
(`ei/kalibrierung.positions_kontrolle`): Derselbe Korpus wird ein zweites Mal
mit vertauschten Rollen vorgelegt, und die beiden Anteile muessen deutlich
auseinanderliegen.

**Der Zeuge liegt vor der Achse, nicht dahinter.** Das unterscheidet ihn von
Impuls und Fragezeichen, die beide die eigene Ausgabe mitmessen. Ein Zeuge,
der etwas sieht, das aus der Achse stammt, waere kein Zeuge — der Vergleich
traefe sich dann vor dem Pruefobjekt und pruefte nichts
(novaberg-gv-initiative_k.md §12.2).

Konzept: novaberg-gv-initiative_k.md §7, §12.
"""

import json
import logging

from config import KALIBRIERUNG_ZEUGE_MAX_ZEICHEN
from services.model_services import model_service
from services.model_services.types import BackgroundRequest

logger = logging.getLogger("ki_server.agents.kalibrierung.zeuge")


ZEUGE_PROMPT: str = """Zwei aufeinanderfolgende Beitraege aus einem Gespraech.

[A]
{text_a}

[B]
{text_b}

[AUFGABE]
Hat B die Richtung des Gespraechs gesetzt?

Eine Richtung setzt, wer etwas wissen will, wer das Thema wechselt oder wer
das Register wechselt — also die Ebene, auf der gesprochen wird.

Eine Richtung setzt NICHT, wer im Thema des anderen weitergeht, auch wenn er
es vertieft, erweitert oder mit viel Sachkenntnis fortfuehrt. Mitgehen ist
keine Fuehrung, auch nicht mit Tiefe.

Antworte AUSSCHLIESSLICH mit diesem JSON, ohne erklaerenden Text:
{{"b_fuehrt": true}}
"""


def _text_kuerzen(text: str) -> str:
    """Kuerzt einen Beitrag auf die Laenge, die der Zeuge lesen soll.

    Lange Antworten wuerden den Prompt sprengen und den kurzen Nutzer-Turn
    darin verschwinden lassen. Gekuerzt wird am Anfang gemessen: Wer die
    Richtung setzt, tut es zu Beginn seines Beitrags.

    Vorbedingung: `text` ist ein String.
    Nachbedingung: Rueckgabe ist hoechstens KALIBRIERUNG_ZEUGE_MAX_ZEICHEN
    lang und traegt bei Kuerzung eine sichtbare Marke — der Zeuge soll wissen,
    dass er einen Ausschnitt liest.
    Fehlerfaelle: Keine.

    Returns:
        Der gekuerzte Text.
    """

    # ── Eingabe-Validierung ─────────────────────
    sauber: str = (text or "").strip()

    # ── Verarbeitung ────────────────────────────
    if len(sauber) <= KALIBRIERUNG_ZEUGE_MAX_ZEICHEN:
        return sauber

    # ── Ausgabe ─────────────────────────────────
    return sauber[:KALIBRIERUNG_ZEUGE_MAX_ZEICHEN].rstrip() + " […]"


def zeuge_befragen(text_a: str, text_b: str) -> bool | None:
    """Fragt den Zeugen, ob B die Richtung gesetzt hat.

    Ein LLM-Call je Turn. Der Aufrufer bestimmt, wer A und wer B ist — fuer
    die Positions-Kontrolle wird derselbe Korpus mit vertauschten Rollen
    vorgelegt.

    Vorbedingung: beide Texte sind nicht leer. Ein leerer Beitrag ist kein
    Urteilsfall: Ohne Text gibt es nichts zu lesen.
    Nachbedingung: True (B fuehrt), False (B fuehrt nicht) oder None.
    Fehlerfaelle: leerer Text, unlesbares JSON, fehlender oder untypisierter
    Schluessel — in allen Faellen None und eine `error`-Zeile. **Kein
    Ausfall wird zu False**: Ein nicht abgegebenes Urteil saehe sonst aus wie
    das Urteil "fuehrt nicht" und verschoebe die Schwelle in eine Richtung
    (novaberg-lesson_l_default-wie-fehlschlag.md).

    Returns:
        Das Urteil oder None.
    """

    # ── Eingabe-Validierung ─────────────────────
    a: str = _text_kuerzen(text_a)
    b: str = _text_kuerzen(text_b)

    if not a or not b:
        logger.error(
            f"Zeuge: leerer Beitrag (A: {len(a)} Zeichen, B: {len(b)}) — "
            f"kein Urteil moeglich, Turn faellt aus dem Korpus"
        )
        return None

    # ── Verarbeitung ────────────────────────────
    # Ein einzelner langsamer Call darf den Lauf nicht toeten. Gemessen am
    # 29.07.2026 auf dem CPU-Backend: ein Urteil brauchte 342 Sekunden und
    # riss den Timeout von 300; die Exception nahm den gesamten Lauf mit —
    # rund 200 bereits geholte Urteile waren verloren. Ein Ausfall gehoert an
    # dieselbe Stelle wie jeder andere: Der Turn faellt aus dem Korpus, wird
    # gezaehlt und benannt, und die Erhebung laeuft weiter.
    try:
        antwort = model_service.background.submit_sync(BackgroundRequest(
            messages          = [{
                "role": "user",
                "content": ZEUGE_PROMPT.format(text_a=a, text_b=b),
            }],
            modus             = "sprache",
            temperature       = 0.0,
            caller            = "pixie/kalibrierung",
        ))
    except Exception as fehler:
        logger.exception(
            f"Zeuge: Urteil nicht erhalten ({type(fehler).__name__}: {fehler}) "
            f"— Turn faellt aus dem Korpus, die Erhebung laeuft weiter"
        )
        return None

    roh: str = (antwort.text or "").strip()

    # ── Ausgabe-Verifikation ────────────────────
    if roh.startswith("```"):
        roh = roh.strip("`").lstrip("json").strip()

    try:
        geparst: dict = json.loads(roh)
    except (json.JSONDecodeError, TypeError) as fehler:
        logger.exception(
            f"Zeuge: Antwort ist kein JSON ({type(fehler).__name__}). "
            f"Roh: '{roh[:120]}'"
        )
        return None

    urteil = geparst.get("b_fuehrt")
    if not isinstance(urteil, bool):
        logger.error(
            f"Zeuge: 'b_fuehrt' fehlt oder ist kein Boolean "
            f"(Typ {type(urteil).__name__}, Wert {urteil!r}) — kein Urteil"
        )
        return None

    return urteil
