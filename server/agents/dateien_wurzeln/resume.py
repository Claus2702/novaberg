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

#: Kopie in den vier Ja/Nein-Deutungen (`direktiven`, `notizen`,
#: `charakter_identitaet`, `dateien_wurzeln`), bewusst kein gemeinsames Modul.
#: **Hier wird geschlossen angenommen:** Freigegeben wird nur, wenn die
#: Antwort aus nichts als Zustimmung besteht — jedes Wort steht in
#: `BESTAETIGUNGS_WOERTER` oder hier. Was zurueckhaelt, ablehnt oder
#: aufschiebt, ist eine offene Klasse; *„Wie bitte?“* trug *bitte* und gab
#: ein Verzeichnis frei, *„ja, bitte nichts“* ebenso. Die Zustimmung ist
#: geschlossen, und ein Wort, das hier fehlt, kostet eine zweite Frage, nie
#: einen Lesezugriff.
#: Die Regel der Menge: Artikel, Pronomen, das Hilfsverb *ist*, Partikeln,
#: die nicht zoegern, und *danke*. Nie darin: ein Verb, ein Nomen, eine
#: Zahl, ein Fragewort (*wie*, *was*), eine Partikel des Zoegerns (*na*,
#: *nun*, *also* — *„na ja“* ist keine Zustimmung), ein Wort der
#: Einschraenkung oder des Aufschubs (*aber*, *sondern*, *statt*, *erst*,
#: *nur*, *noch*, *lieber*, *spaeter*, *morgen*) oder ein Wort aus
#: `ABLEHNUNGS_WOERTER`. Abgeloest wird diese Deutung mit den Klaerfaellen
#: (`KLA-KLAERFALL-AM-OBJEKT`, Schritte 5 und 6).
FILLER_WORDS: frozenset[str] = frozenset({
    "der", "die", "das", "den", "dem", "des", "ein",
    "ich", "du", "er", "sie", "es", "wir", "ihr", "mich", "dich", "sich", "uns", "euch",
    "mir", "dir", "ihm", "ihn", "man",
    "dies", "diese", "dieses", "diesen", "dieser", "diesem",
    "ist",
    "mal", "doch", "ruhig", "sehr",
    "danke",
})

#: Das Apostroph faellt ohne Luecke weg (*mach's* ist *machs*).
_APOSTROPHES: str = "['’‘`´]"

#: **Auch die Zeichen werden geschlossen angenommen:** Ausser Buchstaben,
#: Ziffern und dem Apostroph darf in einer Zustimmung nur stehen, was hier
#: steht — ASCII-Leerraum und die Satzzeichen, mit denen *„Ja!“* und
#: *„Ja :)“* zustimmen. Jedes andere Zeichen macht die Antwort unklar: jedes
#: Fragezeichen jeder Schrift (*„ja？“*, *„ja¿“*, *„ja ❓“*), jedes Emoji
#: (*„ja 👎“*, *„ja 🤔“*), jedes Symbol. Eine Liste der Zeichen, die
#: zurueckhalten, liesse wie jede Liste der Woerter das naechste durch; ein
#: Zeichen, das hier fehlt, kostet eine zweite Frage, nie einen Lesezugriff.
#: `?` steht nie darin.
DROPPED_SIGNS: frozenset[str] = frozenset(" \t\n\r\f\v.,!;:-()")

#: **Die Frage ohne `?` wird an der Wortstellung erkannt:** Eine deutsche
#: Ja/Nein-Frage stellt das finite Verb vor sein Subjekt (*„ist das ok“*,
#: *„ist das sicher“*), die Aussage stellt es dahinter (*„das ist sicher“*).
#: In der geschlossenen Menge ist die Wortstellung das einzige Merkmal, das
#: eine Frage ohne `?` traegt; Fragewoerter kennt die Menge nicht. Eine
#: Antwort mit einem Verb aus `ASKING_VERBS` und dahinter, im selben
#: Satzteil, einem Wort aus `SUBJECT_WORDS` ist deshalb unklar.
#: Fragend sind die Verben der Zustimmungs- und Fuellwoerter, die finit und
#: kein Imperativ sind: hier nur *ist*. Nicht darin: der Imperativ der
#: Zustimmung (*mach*, *machs* — *„mach das“* stimmt zu, *„mach ich“* bleibt
#: Selbstaussage) und die Formel *danke*.
ASKING_VERBS: frozenset[str] = frozenset({"ist"})
#: Die Fuellwoerter, die Subjekt sein koennen — im Nominativ stehen koennen.
#: Nicht darin: was nur Dativ, Akkusativ oder Genitiv ist (*den*, *dem*,
#: *des*, *mich*, *mir*, *ihn*, *uns*, *diesen* ...).
SUBJECT_WORDS: frozenset[str] = frozenset({
    "der", "die", "das", "ein",
    "ich", "du", "er", "sie", "es", "wir", "ihr", "man",
    "dies", "diese", "dieses", "dieser",
})
#: Die Zeichen, an denen ein Satzteil endet: Ein Subjekt gehoert zum Satz
#: seines Verbs, *„ist ok, mach das“* stimmt zu. `- ( )` und Leerraum trennen
#: nicht — *„ist - das ok“* und *„ist (das) ok“* fragen. Ein Zeichen mehr
#: hier liesse eine Frage als zwei Satzteile durch.
CLAUSE_SEPARATORS: frozenset[str] = frozenset(",.!;:")


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
    Schreibung. In `charakter_identitaet/resume.py` ist dieselbe
    Teilzeichenketten-Deutung seit dem 18.10.2026 behoben: Dort sucht die
    Ablehnung ihre Staemme im Text ohne die Zustimmungswoerter.

    **Die Grenze der ganzen Woerter:** *nichts*, *keinesfalls* und
    *ablehnen* sind hier keine Ablehnung. Neben einem Zustimmungswort machen
    sie die Antwort trotzdem nicht zur Zustimmung — die steht nur, wenn
    jedes Wort zustimmt oder ein Fuellwort ist (`_consists_of_consent`), und
    *„ja, bitte nichts“* fragt erneut.
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
    ABLEHNUNGS_WOERTER. **Die Zustimmung wird geschlossen angenommen**
    (`_consists_of_consent`): BESTAETIGUNG nur fuer eine Antwort aus
    Zustimmungs- und Fuellwoertern, ohne ein Zeichen ausserhalb von
    `DROPPED_SIGNS` (kein Fragezeichen, kein Emoji) und ohne die Wortstellung
    einer Frage (kein finites Verb vor seinem Subjekt). Alles andere ist
    UNKLAR — *„Wie bitte?“*, *„ja？“*, *„ja 👎“*, *„Moment, bitte“*,
    *„ist das sicher“*, *„ok, keinesfalls“*.
    """
    text: str = antwort.lower().strip()
    if not text:
        return UNKLAR

    if _traegt(text, ABLEHNUNGS_WOERTER):
        return ABLEHNUNG

    if _consists_of_consent(text):
        return BESTAETIGUNG

    return UNKLAR


def _consists_of_consent(text: str) -> bool:
    """Prueft, ob die Antwort aus nichts als Zustimmung besteht — die geschlossene Annahme.

    Vorbedingung: `text` ist kleingeschrieben (auch leer); die Ablehnung
    prueft der Aufrufer vorher.
    Nachbedingung: True nur, wenn (a) jedes Zeichen ausser Buchstaben,
    Ziffern und Apostroph in `DROPPED_SIGNS` steht — kein `?`, kein
    Fragezeichen einer anderen Schrift, kein Emoji, kein Symbol —, (b)
    mindestens ein Wort aus `BESTAETIGUNGS_WOERTER` dasteht und (c) jedes
    andere Wort in `FILLER_WORDS` steht und (d) die Wortstellung nicht
    fragt (`_asks_by_word_order`: kein fragendes Verb vor einem Subjekt).
    Das Apostroph faellt ohne Luecke weg: *„Ja :)“*, *„Ja, bitte!“*,
    *„mach's“* und *„das ist sicher“* stimmen zu, *„Wie bitte?“*, *„ja？“*,
    *„ja 👎“*, *„na ja“*, *„ist das sicher“* und *„ja, bitte nichts“*
    nicht.
    Fehlerfaelle: ein Text mit Grossbuchstaben wirft `ValueError`. Traegt
    eine Zustimmung ein `?` (dann traegt es `DROPPED_SIGNS`) oder ein Wort
    aus `ABLEHNUNGS_WOERTER` (dann steht es in einem Fuellwort oder einem
    Zustimmungswort) — die Listen widersprechen sich —, wird `RuntimeError`
    geworfen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if text != text.lower():
        msg: str = f"_consists_of_consent: Text nicht kleingeschrieben: {text!r}"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    joined: str = re.sub(_APOSTROPHES, "", text)
    woerter: list[str] = re.findall(r"\w+", joined)
    consents: bool = (
        all(zeichen in DROPPED_SIGNS for zeichen in re.sub(r"\w", "", joined))
        and any(wort in BESTAETIGUNGS_WOERTER for wort in woerter)
        and all(wort in BESTAETIGUNGS_WOERTER or wort in FILLER_WORDS for wort in woerter)
        and not _asks_by_word_order(joined)
    )

    # ── Ausgabe-Verifikation ────────────────────
    if consents and "?" in joined:
        msg = f"_consists_of_consent: `?` in einer Zustimmung: {text!r}"
        raise RuntimeError(msg)
    if consents and any(wort in ABLEHNUNGS_WOERTER for wort in woerter):
        msg = f"_consists_of_consent: Ablehnungswort in einer Zustimmung: {text!r}"
        raise RuntimeError(msg)
    return consents


def _asks_by_word_order(joined: str) -> bool:
    """Prueft, ob die Antwort durch ihre Wortstellung fragt — finites Verb vor seinem Subjekt.

    Vorbedingung: `joined` ist kleingeschrieben, das Apostroph ist entfernt.
    Nachbedingung: True, wenn in einem Satzteil (getrennt an den Zeichen
    aus `CLAUSE_SEPARATORS`) ein Wort aus `ASKING_VERBS` steht und irgendwo
    dahinter ein Wort aus `SUBJECT_WORDS` — *„ist das ok“*, *„ist das
    sicher“*, *„ist es ok“*, *„ist - das ok“*. *„das ist sicher“*, *„es ist
    ok“* und *„ist ok, mach das“* fragen nicht.
    Fehlerfaelle: ein Text mit Grossbuchstaben wirft `ValueError`. Steht ein
    fragendes Verb nicht unter den Zustimmungs- und Fuellwoertern, ein
    Subjekt nicht unter den Fuellwoertern oder ein Trennzeichen nicht unter
    `DROPPED_SIGNS`, kann es in keiner Zustimmung stehen — die Listen
    widersprechen sich, es wird `RuntimeError` geworfen; ebenso bei leeren
    Trennzeichen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if joined != joined.lower():
        msg: str = f"_asks_by_word_order: Text nicht kleingeschrieben: {joined!r}"
        raise ValueError(msg)
    consent_words: set[str] = set(BESTAETIGUNGS_WOERTER) | FILLER_WORDS
    if not ASKING_VERBS <= consent_words or not SUBJECT_WORDS <= FILLER_WORDS:
        msg = "_asks_by_word_order: fragendes Verb oder Subjekt ausserhalb der Zustimmung"
        raise RuntimeError(msg)
    if not CLAUSE_SEPARATORS or not CLAUSE_SEPARATORS <= DROPPED_SIGNS:
        msg = f"_asks_by_word_order: Trennzeichen ungueltig: {sorted(CLAUSE_SEPARATORS)!r}"
        raise RuntimeError(msg)

    # ── Verarbeitung ────────────────────────────
    separators: str = re.escape("".join(sorted(CLAUSE_SEPARATORS)))
    clauses: list[list[str]] = [
        re.findall(r"\w+", clause) for clause in re.split(rf"[{separators}]", joined)
    ]
    asks: bool = any(
        word in ASKING_VERBS and not SUBJECT_WORDS.isdisjoint(words[index + 1:])
        for words in clauses
        for index, word in enumerate(words)
    )

    # ── Ausgabe-Verifikation ────────────────────
    # Eine Frage nach der Wortstellung braucht ein fragendes Verb und ein
    # Subjekt, also mindestens zwei Woerter.
    words_of_answer: list[str] = re.findall(r"\w+", joined)
    if asks and (ASKING_VERBS.isdisjoint(words_of_answer) or len(words_of_answer) < 2):
        msg = f"_asks_by_word_order: Frage ohne fragendes Verb und Subjekt in {joined!r}"
        raise RuntimeError(msg)
    return asks
