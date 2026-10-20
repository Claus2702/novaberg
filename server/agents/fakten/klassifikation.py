"""Klassifikations-Knoten — bestimmt Subjekt, Beziehung und Objekt per Modell.

Die Beziehung muss im Kanon stehen (`beziehungen.KANON`). Nennt das Modell
eine andere oder lehnt es selbst ab, endet der Knoten mit `rejected`; der
Dispatch macht daraus die begründete Ablehnung, und der Planner fragt den
nächsten Dienst.

**Die Antwort wird gegen den Wortlaut der Bitte gehalten** (`check_answer`).
`X hat_chef Y` heißt *Y ist Xs Chef*. Was das Modell an Richtung und Namen
liefert, prüft der Code, soweit der Satz es zeigt:

  * ein Name steht als Name in der Bitte — groß geschrieben, ohne Verb, in
    der Grundform; *Merten* passt auf *Mertens*, *Mertens* in der Stellung
    des Genitivs nicht;
  * *ICH* nur, wenn die Bitte in der ersten Person spricht;
  * bei einer Beziehung `hat_…` ist der Besitzer im Satz (*Ilvas*,
    *… von Ilva*, *mein*) das Subjekt, nie das Objekt;
  * bei `heisst` ist das Subjekt nie der Besitzer — *Mertens Mutter heißt …*
    nennt nicht Mertens Namen.

Eine Antwort, die das verfehlt, schreibt nichts und endet als `fehler` mit
dem Grund — nicht als `rejected`: Die Bitte war ein Auftrag, nur die Antwort
ist defekt, und ein anderer Dienst soll ihn nicht übernehmen.

Prompt-Schema: [BLOCKNAME]-Format unter `prompts/default/classify_fakten.*`.
"""

import logging
import re
from typing import NamedTuple

from agents.base import AgentState
from agents.fakten.beziehungen import KANON, Relation, find_relation
from config import PROMPTS, get_node_config
from services.model_services import ChatRequest, model_service

logger = logging.getLogger("ki_server.agents.fakten.klassifikation")

# Das Subjekt, wenn der Mensch über sich selbst spricht.
SELF: str = "ICH"

# Ein Wort der Bitte: Buchstaben, Ziffern, Bindestrich und Apostroph im Wort
# (*Anna-Lena*, *Klaus'*), ohne führendes Satzzeichen.
_WORD: re.Pattern[str] = re.compile(r"\w[\w'’-]*")

# Mit einem dieser Wörter spricht die Bitte in der ersten Person.
_FIRST_PERSON: frozenset[str] = frozenset({
    "ich", "mich", "mir", "mein", "meine", "meinem", "meinen", "meiner", "meines",
})
# Mit einem dieser Wörter ist ICH der Besitzer im Satz (*mein Nachbar*).
_FIRST_PERSON_POSSESSIVE: frozenset[str] = frozenset({
    "mein", "meine", "meinem", "meinen", "meiner", "meines",
})
# Endungen des Genitivs an einem Namen: *Mertens*, *Ilva's*, *Klaus'*.
_GENITIVE_ENDINGS: tuple[str, ...] = ("s", "'s", "’s", "'", "’")

# Beziehungen, deren Subjekt der Besitzer ist: *Ilvas Bruder* ist Ilva hat_bruder.
_POSSESSIVE_PREFIX: str = "hat_"
# Beziehungen, deren Subjekt nie der Besitzer eines anderen ist.
_SUBJECT_NEVER_POSSESSOR: frozenset[str] = frozenset({"heisst"})


def build_classify_prompt() -> str:
    """Baut den System-Prompt der Klassifikation aus den drei Bausteinen.

    Vorbedingung: Die Bausteine `classify_fakten.identity`, `.task` und
        `.rules` sind geladen.
    Nachbedingung: Der Prompt nennt jede Beziehung des Kanons genau so, wie
        der Kanon sie schreibt.
    Fehlerfälle: KeyError, wenn ein Baustein fehlt; RuntimeError, wenn eine
        Beziehung im fertigen Prompt fehlt.
    """
    # ── Verarbeitung ────────────────────────────
    beziehungen: str = "\n".join(f"  - {attribut}" for attribut in sorted(KANON))
    prompt: str = "\n\n".join([
        PROMPTS["classify_fakten.identity"],
        PROMPTS["classify_fakten.task"].format(beziehungen=beziehungen),
        PROMPTS["classify_fakten.rules"],
    ])

    # ── Ausgabe-Verifikation ────────────────────
    fehlend: list[str] = [a for a in KANON if f"  - {a}\n" not in f"{prompt}\n"]
    if fehlend:
        raise RuntimeError(f"Klassifikation Fakten: Prompt ohne Beziehungen {fehlend}")
    return prompt


def classify(state: AgentState) -> dict:
    """Bestimmt Subjekt, Beziehung und Objekt der Aufgabe.

    Vorbedingung: `state["aufgabe"]` ist der Text der Bitte.
    Nachbedingung: Bei einer Beziehung des Kanons, deren Antwort
        `check_answer` besteht, tragen die Parameter `subjekt`, `beziehung`
        (die Beziehung des Kanons) und `objekt`, alle nicht leer. Sonst
        `status = "rejected"` mit dem Grund im letzten Schritt.
    Fehlerfälle: Ein Fehler des Modellaufrufs, eine Antwort ohne Objekt
        oder ohne Subjekt ergibt `status = "fehler"` — eine Antwort, die eine
        Beziehung nennt und kein Objekt, ist ein Defekt der Antwort, kein
        Urteil über die Bitte. Ebenso eine Antwort, deren Namen oder Richtung
        die Bitte nicht trägt.
    """
    # ── Eingabe-Validierung ─────────────────────
    aufgabe: str = state["aufgabe"]
    if not aufgabe or not aufgabe.strip():
        return _with_step(state, {"status": "fehler", "fehler": "Klassifikation ohne Aufgabe"},
                          "leere_aufgabe")

    # ── Verarbeitung ────────────────────────────
    node_cfg: dict = get_node_config("router")
    anfrage = ChatRequest(
        messages          = [{"role": "user", "content": aufgabe}],
        system            = build_classify_prompt(),
        temperature       = node_cfg.get("temperature", 0.05),
        expect_json       = True,
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "agent/fakten/klassifikation",
    )
    try:
        antwort: object = model_service.chat.submit_sync(anfrage).parsed
    except Exception as fehler:
        logger.exception("klassifizieren: Modellaufruf fehlgeschlagen")
        return _with_step(state, {"status": "fehler",
                                  "fehler": f"Klassifikation fehlgeschlagen: {fehler}"},
                          "modell_fehler")
    if not isinstance(antwort, dict):
        logger.error("klassifizieren: Antwort ist kein Objekt: %r", antwort)
        return _with_step(state, {"status": "fehler",
                                  "fehler": "Klassifikation ohne auswertbare Antwort"},
                          "keine_antwort")

    beziehung: Relation | None = find_relation(antwort.get("beziehung"))
    if antwort.get("action") == "rejected" or beziehung is None:
        grund: str = str(antwort.get("grund") or
                         f"Beziehung {antwort.get('beziehung')!r} nicht im Kanon")
        logger.info("klassifizieren: REJECTED — %s", grund)
        return _with_step(state, {"status": "rejected"}, f"rejected/{grund}")

    subjekt: str = _as_self(str(antwort.get("subjekt") or "").strip())
    objekt: str = _as_self(str(antwort.get("objekt") or "").strip())

    # ── Ausgabe-Verifikation ────────────────────
    if not subjekt or not objekt:
        logger.error("klassifizieren: Antwort ohne Subjekt oder Objekt: %r", antwort)
        return _with_step(state, {"status": "fehler",
                                  "fehler": "Klassifikation ohne Subjekt oder Objekt"},
                          "unvollstaendig")
    verfehlt: str | None = check_answer(aufgabe, subjekt, beziehung, objekt)
    if verfehlt is not None:
        logger.error("klassifizieren: Antwort verworfen — %s (%s %s %s)", verfehlt, subjekt,
                     beziehung.attribut, objekt)
        return _with_step(state, {"status": "fehler",
                                  "fehler": f"Klassifikation verworfen: {verfehlt}"},
                          f"verworfen/{verfehlt}")
    logger.info("klassifizieren: %s %s %s", subjekt, beziehung.attribut, objekt)
    return _with_step(state, {"parameter": {
        **state["parameter"],
        "subjekt": subjekt, "beziehung": beziehung.attribut, "objekt": objekt,
    }}, f"{subjekt}/{beziehung.attribut}/{objekt}")


def check_answer(aufgabe: str, subjekt: str, beziehung: Relation, objekt: str) -> str | None:
    """Hält Subjekt und Objekt der Antwort gegen den Wortlaut der Bitte.

    Geprüft wird jeder Name, der eine Entität wird: das Subjekt immer, das
    Objekt, wenn die Beziehung eine Objekt-Entität hat. Ein Wert (Beruf,
    Hobby, Name bei `heisst`) darf umformuliert sein und wird nicht geprüft.

    Vorbedingung: `aufgabe`, `subjekt` und `objekt` sind nicht leer; ICH ist
        schon als `SELF` geschrieben.
    Nachbedingung: None, wenn jeder geprüfte Name als Name in der Bitte steht
        und die Richtung zum Besitzer im Satz passt; sonst der Grund, warum
        die Antwort nichts schreiben darf.
    Fehlerfälle: ValueError bei leerer Bitte, leerem Subjekt oder Objekt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not aufgabe.strip() or not subjekt or not objekt:
        raise ValueError("check_answer: Bitte, Subjekt und Objekt dürfen nicht leer sein")

    # ── Verarbeitung ────────────────────────────
    woerter: list[str] = _WORD.findall(aufgabe)
    # Wer klein schreibt, schreibt auch Namen klein: Dann trägt die Schreibung
    # nichts, und die Prüfungen, die an ihr hängen, entfallen.
    gross: bool = any(w[0].isupper() for w in woerter[1:])
    rollen: dict[str, str] = {"subjekt": subjekt}
    if beziehung.objekt_ist_entitaet:
        rollen["objekt"] = objekt
    bitte: _Request = _Request(woerter, gross, frozenset(
        _norm(w) for name in rollen.values() for w in name.split()
    ))
    besitzer: dict[str, bool] = {}
    for rolle, name in rollen.items():
        grund, ist_besitzer = _place_in_request(bitte, name)
        if grund is not None:
            return f"{rolle} {name!r} {grund}"
        besitzer[rolle] = ist_besitzer

    # ── Ausgabe-Verifikation ────────────────────
    if beziehung.attribut.startswith(_POSSESSIVE_PREFIX) and besitzer.get("objekt"):
        return (f"objekt {objekt!r} ist im Satz der Besitzer — bei "
                f"{beziehung.attribut} ist der Besitzer das Subjekt, die Richtung ist vertauscht")
    if beziehung.attribut in _SUBJECT_NEVER_POSSESSOR and besitzer["subjekt"] \
            and subjekt != SELF:
        return (f"subjekt {subjekt!r} ist im Satz der Besitzer — {beziehung.attribut} "
                f"nennt dann den Namen eines anderen")
    return None


class _Request(NamedTuple):
    """Die Bitte, wie `check_answer` sie liest.

    `woerter` in ihrer Reihenfolge; `gross` sagt, ob die Bitte Substantive
    groß schreibt (ein großes Wort nach dem ersten); `antwortwoerter` sind die
    normierten Wörter aller geprüften Namen der Antwort.
    """

    woerter:        list[str]
    gross:          bool
    antwortwoerter: frozenset[str]

    def capital(self, wort: str) -> bool:
        """Sagt, ob ein Wort als groß geschrieben gilt.

        Vorbedingung: `wort` ist nicht leer.
        Nachbedingung: True, wenn es groß beginnt — oder die Bitte nichts groß
            schreibt; dann trägt die Schreibung nichts.
        Fehlerfälle: ValueError bei leerem Wort.
        """
        # ── Eingabe-Validierung ─────────────────────
        if not wort:
            raise ValueError("_Request.capital: leeres Wort")

        # ── Verarbeitung ────────────────────────────
        return wort[0].isupper() or not self.gross


def _place_in_request(bitte: _Request, name: str) -> tuple[str | None, bool]:
    """Sucht einen Namen der Antwort in den Wörtern der Bitte.

    Vorbedingung: `bitte` ist die gelesene Bitte, `name` ein Name der Antwort.
    Nachbedingung: (None, Besitzer?), wenn der Name in der Bitte steht —
        Besitzer heißt: im Genitiv (*Ilvas*), nach *… von* (*Chef von Ilva*)
        oder, bei ICH, mit einem Possessiv der ersten Person (*mein*). Sonst
        (Grund, False).
    Fehlerfälle: ValueError bei leerem Namen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not name:
        raise ValueError("_place_in_request: leerer Name")
    normiert: list[str] = [_norm(w) for w in bitte.woerter]
    if name == SELF:
        if _FIRST_PERSON.isdisjoint(normiert):
            return "steht für dich selbst, aber die Bitte spricht nicht von dir", False
        return None, not _FIRST_PERSON_POSSESSIVE.isdisjoint(normiert)
    teile: list[str] = name.split()
    if not all(_WORD.fullmatch(t) for t in teile):
        return "ist kein Name", False

    # ── Verarbeitung ────────────────────────────
    treffer: list[tuple[int, bool]] = _occurrences(bitte, teile)
    if not treffer:
        return "steht so nicht als Name in der Bitte", False
    folgend: list[str] = [
        bitte.woerter[start + len(teile)] if start + len(teile) < len(bitte.woerter) else ""
        for start, _ in treffer
    ]
    # *Mertens Schwester*: ein Name auf -s, jedes Mal vor einem Substantiv —
    # das ist ein Genitiv, und die Antwort hat die Grundform nicht gefunden.
    nur_genitivform: bool = bitte.gross and _norm(teile[-1]).endswith(("s", "'", "’")) and all(
        not genitiv and wort[:1].isupper()
        for (_, genitiv), wort in zip(treffer, folgend, strict=True)
    )
    besitzer: bool = any(
        genitiv or _after_of(bitte, start) for start, genitiv in treffer
    )

    # ── Ausgabe-Verifikation ────────────────────
    if nur_genitivform:
        return "steht in der Bitte nur im Genitiv — die Grundform fehlt", False
    return None, besitzer


def _occurrences(bitte: _Request, teile: list[str]) -> list[tuple[int, bool]]:
    """Findet jede Stelle, an der die Teile eines Namens in der Bitte stehen.

    Vorbedingung: `teile` ist nicht leer.
    Nachbedingung: je Stelle (Anfang, Genitiv?). Jedes Wort der Stelle gilt
        als groß geschrieben (`_Request.capital`); alle Teile stimmen nach
        Groß- und Kleinschreibung und `ß`/`ss` überein, der letzte darf
        zusätzlich eine Endung des Genitivs tragen (*Merten* auf *Mertens*) —
        dann ist Genitiv? wahr.
    Fehlerfälle: ValueError bei leeren Teilen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not teile:
        raise ValueError("_occurrences: Name ohne Teile")

    # ── Verarbeitung ────────────────────────────
    soll: list[str] = [_norm(t) for t in teile]
    genitivformen: frozenset[str] = frozenset(soll[-1] + e for e in _GENITIVE_ENDINGS)
    treffer: list[tuple[int, bool]] = []
    for start in range(len(bitte.woerter) - len(teile) + 1):
        fenster: list[str] = bitte.woerter[start:start + len(teile)]
        ist: list[str] = [_norm(w) for w in fenster]
        if not all(bitte.capital(w) for w in fenster) or ist[:-1] != soll[:-1]:
            continue
        if ist[-1] == soll[-1] or ist[-1] in genitivformen:
            treffer.append((start, ist[-1] != soll[-1]))

    # ── Ausgabe-Verifikation ────────────────────
    if any(not 0 <= start < len(bitte.woerter) for start, _ in treffer):
        raise RuntimeError(f"_occurrences: Stelle außerhalb der Bitte {treffer}")
    return treffer


def _after_of(bitte: _Request, start: int) -> bool:
    """Sagt, ob der Name an `start` als Besitzer nach *… von* steht.

    Vorbedingung: `start` ist eine Stelle in `bitte.woerter`.
    Nachbedingung: True, wenn vor dem Namen *von* steht und davor ein groß
        geschriebenes Wort, das kein Name der Antwort ist (*die Kollegin von
        Ilva*); *Merten von Ilva* zählt nicht — dort steht vor *von* ein Name.
    Fehlerfälle: ValueError, wenn `start` außerhalb der Bitte liegt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not 0 <= start < len(bitte.woerter):
        raise ValueError(f"_after_of: Stelle {start} außerhalb der Bitte")

    # ── Verarbeitung ────────────────────────────
    if start < 2 or _norm(bitte.woerter[start - 1]) != "von":
        return False
    davor: str = bitte.woerter[start - 2]
    return bitte.capital(davor) and _norm(davor) not in bitte.antwortwoerter


def _as_self(name: str) -> str:
    """Schreibt *ich* in jeder Schreibung als `SELF`, alles andere unverändert.

    Vorbedingung: `name` ist gestutzt.
    Nachbedingung: `SELF` für *ich*, *Ich*, *ICH*; sonst `name`.
    Fehlerfälle: ValueError, wenn `name` nicht gestutzt ist — *„ ich“* bliebe
        sonst ein Name.
    """
    # ── Eingabe-Validierung ─────────────────────
    if name != name.strip():
        raise ValueError(f"_as_self: Name nicht gestutzt {name!r}")

    # ── Verarbeitung ────────────────────────────
    return SELF if name.casefold() == SELF.casefold() else name


def _norm(wort: str) -> str:
    """Normiert ein Wort für den Vergleich: Groß- und Kleinschreibung, `ß` als `ss`.

    Vorbedingung: `wort` ist ein Wort der Bitte oder der Antwort, ohne Leerzeichen.
    Nachbedingung: `casefold` des Worts — das schreibt `ß` als `ss`.
    Fehlerfälle: ValueError bei einem Leerzeichen im Wort — verglichen wird
        Wort für Wort, nie eine Phrase.
    """
    # ── Eingabe-Validierung ─────────────────────
    if any(zeichen.isspace() for zeichen in wort):
        raise ValueError(f"_norm: kein einzelnes Wort {wort!r}")

    # ── Verarbeitung ────────────────────────────
    return wort.casefold()


def _with_step(state: AgentState, aenderung: dict, ergebnis: str) -> dict:
    """Hängt den Schritt der Klassifikation an eine Zustandsänderung.

    Vorbedingung: `aenderung` ist die Änderung des Zustands ohne `schritte`.
    Nachbedingung: dieselbe Änderung mit einem Schritt mehr.
    Fehlerfälle: ValueError, wenn `aenderung` selbst Schritte trägt — sie
        gingen sonst verloren.
    """
    # ── Eingabe-Validierung ─────────────────────
    if "schritte" in aenderung:
        raise ValueError("Klassifikation Fakten: Änderung trägt schon Schritte")

    # ── Verarbeitung ────────────────────────────
    return {
        **aenderung,
        "schritte": state["schritte"] + [{"node": "klassifizieren", "ergebnis": ergebnis}],
    }
