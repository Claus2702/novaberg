"""Der Rueckweg der Rueckfrage — der Mensch darf nein sagen.

Spezifikation: docs/novaberg-agent-dateien_k.md §2a.2 (das Tor) ·
`novaberg-convention-nmcp.md` §5.5.

**Eine differenzierte Rueckfrage ohne eigenen Rueckweg taeuscht eine
Genauigkeit vor, die sie nicht einloest.** Am 17.08.2026 gezaehlt hatte
einer von vier Torwaechtern des Bestandes diesen Rueckweg; die uebrigen drei
fragten, ohne ein unterscheidbares Nein zu kennen.

Fuer diesen Dienst ist er nicht Kuer, sondern die Bedingung des Tores: Was
hier bestaetigt wird, ist Lesezugriff auf ein Verzeichnis des Menschen. Ein
Nein, das als Ja durchginge, waere der teuerste Fehler des Verbunds — und
deshalb fuehrt **Unklarheit zur erneuten Frage und nie zur Ausfuehrung.**
"""

import logging
import re

from agents.base import AgentState

logger = logging.getLogger("ki_server.agents.dateien_wurzeln.resume")

#: Die drei Lesarten einer Antwort am Tor. Geschlossene Menge.
ABLEHNUNG: str = "abgelehnt"
BESTAETIGUNG: str = "bestaetigt"
UNKLAR: str = "unklar"

#: Ablehnung wird zuerst geprueft und gewinnt bei Zusammentreffen: "ja, aber
#: nicht das" traegt beide Woerter, und die sichere Lesart ist hier die
#: verneinende — eine faelschlich unterbliebene Freigabe kostet eine
#: Nachfrage, eine faelschlich erteilte kostet Lesezugriff.
ABLEHNUNGS_WOERTER: tuple[str, ...] = (
    "nein", "ne", "nee", "noe", "nicht", "kein", "keine",
    "lass", "abbruch", "abbrechen", "stopp", "stop",
)

BESTAETIGUNGS_WOERTER: tuple[str, ...] = (
    "ja", "jau", "jo", "jep", "jepp", "yes", "jawohl",
    "ok", "okay", "klar", "bitte", "mach", "machs", "los", "gerne",
    "genau", "meinetwegen", "sicher", "unbedingt",
)


#: Die Antwort auf die Eigentumsfrage traegt einen **Wert**, kein Ja oder
#: Nein. Sie wird aus der Sicht des Antwortenden gelesen: Nova fragt, der
#: Mensch antwortet — "deins" meint deshalb **ihres** und "meins" seines.
EIGENTUM_FIGUR_WOERTER: tuple[str, ...] = (
    "deins", "deines", "dein", "deine", "dir", "du", "dich",
)

EIGENTUM_NUTZER_WOERTER: tuple[str, ...] = (
    "meins", "meines", "mein", "meine", "mir", "ich", "mich",
)

EIGENTUM_GEMISCHT_WOERTER: tuple[str, ...] = (
    "beides", "beide", "beiden", "gemischt", "uns", "unser", "unsere", "unseres",
)


def _eigentum_deuten(antwort: str) -> str:
    """Liest aus der Antwort einen der drei Eigentumswerte — oder nichts.

    Vorbedingung: keine; eine leere Antwort ist zulaessig.
    Nachbedingung: "nutzer", "figur", "gemischt" oder der leere String, und
    der leere String heisst **erneut fragen** — nie schreiben.

    **Treffen beide Seiten, ist das keine Mischung, sondern eine Unklarheit.**
    *„meins, aber auch deins"* liesse sich als `gemischt` lesen und
    *„nicht meins, sondern deins"* genauso — dieselben zwei Treffer, zwei
    verschiedene Bedeutungen. Wer hier zusammenfasst, raet; die Frage kostet
    einen Turn, ein falscher Eigentuemer kostet die Zuschreibung, gegen die
    die Spalte gebaut wurde.
    """
    text: str = antwort.lower().strip()
    if not text:
        return ""

    if _traegt(text, EIGENTUM_GEMISCHT_WOERTER):
        return "gemischt"

    figur: bool = _traegt(text, EIGENTUM_FIGUR_WOERTER)
    nutzer: bool = _traegt(text, EIGENTUM_NUTZER_WOERTER)
    if figur and nutzer:
        logger.info(
            "dateien_wurzeln.resume: Antwort %r nennt beide Seiten — "
            "erneute Frage statt Zusammenfassung", antwort[:60],
        )
        return ""
    if figur:
        return "figur"
    if nutzer:
        return "nutzer"
    return ""


def _traegt(text: str, woerter: tuple[str, ...]) -> bool:
    """Prueft, ob der Text eines der Woerter **als ganzes Wort** enthaelt.

    Vorbedingung: `text` ist bereits kleingeschrieben und beschnitten.
    Nachbedingung: True nur bei einem Treffer an Wortgrenzen.

    **Ein Teilzeichenketten-Vergleich taugt hier nicht, und der Preis ist
    hoch.** `"ne"` steckt in `"gerne"`, `"meinetwegen"` und `"ohne"`; eine
    Zustimmung wird damit zur Ablehnung. Das ist kein Randfall — *„ja,
    gerne"* ist eine der haeufigsten Zustimmungen im Deutschen.

    `[gemessen]` — 18.08.2026 im Betrieb: *„Ja, gerne."* am Tor einer
    Freigabe wurde als Ablehnung gedeutet, der Vorgang endete ohne
    Schreibung. Dieselbe Bauart im Bestand (`charakter_identitaet/resume.py`)
    liest `"gerne"` und `"meinetwegen"` ebenso — dort steht der Fund in der
    Fundliste.
    """
    return any(re.search(rf"\b{re.escape(wort)}\b", text) for wort in woerter)


def resume(state: AgentState) -> dict:
    """Deutet die Antwort des Menschen auf die Torfrage.

    Vorbedingung: `parameter["user_answer"]` traegt die Antwort,
    `parameter["original_rueckfrage"]` die gestellte Frage.
    Nachbedingung: Genau einer von drei Zustaenden —
      `dismissed`  → der Mensch hat abgelehnt, nichts wird geschrieben
      `rueckfrage` → die Antwort war unklar, es wird erneut gefragt
      `laufend`    → bestaetigt, die Ausfuehrung darf laufen

    **Ein vierter Ausgang existiert nicht, und das ist Absicht:** Es gibt
    keinen Pfad, auf dem eine ungedeutete Antwort zur Ausfuehrung fuehrt.
    """
    # ── Eingabe-Validierung ─────────────────────
    antwort: str = state["parameter"].get("user_answer", "") or ""
    urspruengliche_frage: str = state["parameter"].get("original_rueckfrage", "") or ""
    action: str = state["parameter"].get("action", "")

    logger.debug(
        "dateien_wurzeln.resume: Einstieg — action='%s', antwort='%s'",
        action, antwort[:80],
    )

    # ── Verarbeitung ────────────────────────────
    # Die Eigentumsfrage hat keine Ja-Nein-Antwort und wird deshalb zuerst
    # behandelt. Eine Ablehnung gilt trotzdem: Wer "lass es" sagt, will
    # keine Freigabe und nicht einen dritten Eigentuemer.
    if state["parameter"].get("frage_art") == "eigentum":
        return _eigentum_beantworten(state, antwort, urspruengliche_frage)

    deutung: str = _antwort_deuten(antwort)

    # ── Ausgabe-Verifikation ────────────────────
    if deutung == ABLEHNUNG:
        logger.info(
            "dateien_wurzeln.resume: abgelehnt — '%s' wird nicht ausgefuehrt", action,
        )
        return {
            "status": "dismissed",
            "ergebnis": "Gut, dann lasse ich es. Es hat sich nichts geaendert.",
            "schritte": state["schritte"] + [
                {"node": "resume", "ergebnis": "abgelehnt"}
            ],
        }

    if deutung == UNKLAR:
        logger.info(
            "dateien_wurzeln.resume: Antwort %r nicht deutbar — erneute Frage "
            "statt Ausfuehrung", antwort[:60],
        )
        return {
            "status": "rueckfrage",
            "rueckfrage": urspruengliche_frage or "Soll ich das tun?",
            "schritte": state["schritte"] + [
                {"node": "resume", "ergebnis": "unklar"}
            ],
        }

    logger.info("dateien_wurzeln.resume: bestaetigt — '%s' wird ausgefuehrt", action)
    return {
        "parameter": {**state["parameter"], "resume": False},
        "status": "laufend",
        "schritte": state["schritte"] + [
            {"node": "resume", "ergebnis": "bestaetigt"}
        ],
    }


def _eigentum_beantworten(
    state: AgentState, antwort: str, urspruengliche_frage: str,
) -> dict:
    """Nimmt die Antwort auf die Eigentumsfrage entgegen.

    Vorbedingung: `parameter["frage_art"] == "eigentum"`, `antwort` ist der
    Wortlaut des Menschen.
    Nachbedingung: Genau einer von drei Zustaenden — `dismissed` bei
    Ablehnung, `rueckfrage` bei jeder ungedeuteten Antwort, sonst `laufend`
    mit gesetztem `parameter["eigentum"]`.

    **Ein Ausgang, der ohne Wert zur Ausfuehrung fuehrt, existiert nicht.**
    Das ist dieselbe Zusicherung wie am Tor: Unklarheit fuehrt zur erneuten
    Frage.
    """
    if _antwort_deuten(antwort) == ABLEHNUNG:
        logger.info("dateien_wurzeln.resume: Eigentumsfrage abgelehnt — keine Freigabe")
        return {
            "status": "dismissed",
            "ergebnis": "Gut, dann lasse ich es. Es hat sich nichts geaendert.",
            "schritte": state["schritte"] + [
                {"node": "resume", "ergebnis": "eigentum/abgelehnt"}
            ],
        }

    gedeutet: str = _eigentum_deuten(antwort)
    if not gedeutet:
        logger.info(
            "dateien_wurzeln.resume: Eigentum aus %r nicht deutbar — erneute Frage",
            antwort[:60],
        )
        return {
            "status": "rueckfrage",
            "rueckfrage": urspruengliche_frage or (
                "Wessen Material liegt dort — deins, meins, oder beides?"
            ),
            "schritte": state["schritte"] + [
                {"node": "resume", "ergebnis": "eigentum/unklar"}
            ],
        }

    logger.info("dateien_wurzeln.resume: Eigentum gedeutet als '%s'", gedeutet)
    return {
        "parameter": {
            **state["parameter"], "eigentum": gedeutet,
            "frage_art": "", "resume": False,
        },
        "status": "laufend",
        "schritte": state["schritte"] + [
            {"node": "resume", "ergebnis": f"eigentum/{gedeutet}"}
        ],
    }


def _antwort_deuten(antwort: str) -> str:
    """Ordnet eine Antwort einer der drei Lesarten zu.

    Vorbedingung: keine — eine leere Antwort ist zulaessig und heisst UNKLAR.
    Nachbedingung: einer der drei Werte ABLEHNUNG, BESTAETIGUNG, UNKLAR.

    Die Ablehnung wird zuerst geprueft; der Grund steht bei
    ABLEHNUNGS_WOERTER.
    """
    text: str = antwort.lower().strip()
    if not text:
        return UNKLAR

    if _traegt(text, ABLEHNUNGS_WOERTER):
        return ABLEHNUNG

    if _traegt(text, BESTAETIGUNGS_WOERTER):
        return BESTAETIGUNG

    return UNKLAR
