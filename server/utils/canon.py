"""Zieht einen Wert aus einer Modellantwort auf seine kanonische Form.

**Das Modell schreibt Deutsch, der Kanon steht in ASCII.** Die Prompts
verlangen `ueberrascht` und `fachgespraech`; ein Sprachmodell schreibt
gelegentlich `überrascht` und `fachgespräch`. Der Wert faellt dann aus seiner
geschlossenen Menge, und was danach passiert, haengt am Aufrufer — im besten
Fall eine Fehlerzeile, im schlechteren ein Vorgabewert, der wie eine Messung
aussieht.

`[gemessen]` — 03.09.2026 ueber 3317 Knoten des Bestandes: **18 Knoten**
tragen einen Emotionswert ausserhalb von `EMOTION_KANON`, darunter
`ueberrascht` und `mitgefuehl` in Umlautschreibung. Kennung
`PERZEPTION-EMOTION-AUSSER-KANON`. Dieselbe Klasse hat am 22.08.2026 an
anderer Stelle ein ganzes Urteil gekostet: `_kopf_deuten` verwarf den
Kopfblock des Verfassers, wenn ein Feldname `GEPRÜFT` statt `GEPRUEFT` hiess.

**Was dieser Helfer NICHT tut: raten.** Er ersetzt keine Umlaute auf Verdacht
und erfindet keine Werte. Er prueft gegen die uebergebene Menge, loest bei
einem Fehlschlag die Umlaute auf und prueft **noch einmal**. Trifft auch das
nicht, gibt er `None` zurueck und ueberlaesst dem Aufrufer die Entscheidung —
denn ob ein unbekannter Wert ein Fehler, ein Vorgabewert oder ein Abbruch ist,
weiss nur er.
"""

from __future__ import annotations

import logging
from typing import Collection, Optional

logger = logging.getLogger("ki_server.utils.canon")

#: Umlaute und Eszett auf ihre ASCII-Doppel, gross wie klein.
#:
#: **Nur diese Richtung ist sicher.** `ue` → `ü` waere die Umkehrung und
#: verbietet sich: `neue` wuerde zu `neü`. Die Abbildung ist deshalb
#: absichtlich einseitig.
UMLAUT_MAP: dict[int, str] = str.maketrans({
    "Ä": "AE", "Ö": "OE", "Ü": "UE", "ä": "ae", "ö": "oe", "ü": "ue",
    "ß": "ss", "ẞ": "SS",
})


def strip_umlauts(text: str) -> str:
    """Loest Umlaute und Eszett in ihre ASCII-Doppel auf.

    Vorbedingung: `text` ist eine Zeichenkette.
    Nachbedingung: dieselbe Zeichenkette ohne Umlaute; Gross- und
    Kleinschreibung bleiben im Uebrigen erhalten.
    Fehlerfaelle: keine.
    """
    return text.translate(UMLAUT_MAP)


def to_canonical(
    value:  object,
    canon:  Collection[str],
    field:  str,
    caller: str = "",
) -> Optional[str]:
    """Gibt den Wert in kanonischer Form, oder `None`, wenn er nicht dazu passt.

    Vorbedingung: `canon` ist die geschlossene Menge, die das Feld erlaubt —
    ein `set`, `frozenset`, `dict` oder eine andere Sammlung von
    Zeichenketten. `value` ist der rohe Wert aus der Modellantwort und darf
    jede Form haben, auch `None`.
    Nachbedingung: ein Element von `canon`, oder `None`. Wurde der Wert dabei
    veraendert, steht eine Zeile im Protokoll — **eine stille Korrektur waere
    schlimmer als der Fehler**, weil sie die Haeufigkeit unsichtbar macht.
    Fehlerfaelle: keine eigenen; ein Wert, der nicht passt, ist eine Aussage
    und kein Ausfall.

    Drei Stufen, in dieser Reihenfolge:

    1. **Der Wert steht im Kanon** — unveraendert zurueck, kein Protokoll.
    2. **Kleinschreibung und aufgeloeste Umlaute stehen im Kanon** — die
       kanonische Form zurueck, mit einer Zeile auf `info`.
    3. **Sonst** `None`. Der Aufrufer entscheidet, was das bedeutet.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(value, str) or not value:
        return None

    # ── Verarbeitung ────────────────────────────
    if value in canon:
        return value

    normalisiert: str = strip_umlauts(value.strip()).lower()
    if normalisiert in canon:
        logger.info(
            "Kanon [%s]: Feld %r kam als %r und wurde auf %r gezogen "
            "(Umlaut- oder Grossschreibung)",
            caller or "ohne Aufrufer", field, value, normalisiert,
        )
        return normalisiert

    # Keine Ausgabe-Verifikation, und das ist Absicht: Der Nichttreffer **ist**
    # das Ergebnis. Eine Marke ueber einer Meldung sieht beim Lesen aus wie
    # eine Pruefung und ist keine (`11_EVA` §4).
    logger.warning(
        "Kanon [%s]: Feld %r traegt %r — steht auch nach dem Aufloesen der "
        "Umlaute nicht im Kanon (%d erlaubte Werte). Der Aufrufer entscheidet.",
        caller or "ohne Aufrufer", field, value, len(canon),
    )
    return None
