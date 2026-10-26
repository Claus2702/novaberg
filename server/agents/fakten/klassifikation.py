"""Klassifikation — welche Kandidaten eines Turns ein Fakt des Kanons sind.

**Ein Modellaufruf je Turn mit Kandidaten** (`classify_candidates`). Die
Eingabe ist die Äußerung des Menschen und die Kandidaten, die die Sachlage
in diesem Turn aus seinen Worten abgelegt hat, je mit einer Nummer, die der
Code vergibt. Die Antwort sagt zuerst, ob die Äußerung eine dauerhafte
Aussage über den Fall ist (die Vorprüfung), und nennt dann 0…n Tripel des
Kanons, je mit der Nummer ihres Kandidaten. Klassen werden nicht
vorgefiltert; was kein Fakt ist, sortiert das Modell nach den Negativfällen
im Prompt aus (`NEGATIVE_CASES`).

**Jedes Tripel wird geprüft, bevor es schreibt** (`vet_triple`): Seine
Nummer zeigt auf einen Kandidaten des Turns, und zwar einen des Menschen
— die Herkunft kommt aus dem Sprecher des Kandidaten (`SPEAKER_ORIGIN`),
nie aus der Antwort; die Beziehung steht im Kanon; der Typ des Subjekts,
den die Antwort je Tripel nennt (`typ`), steht in `ENTITY_TYPES` und ist
einer, den die Beziehung erlaubt, oder `sonstiges` (`typ_form`,
`subjekt_typ`); das Tripel spricht nicht über die Figur (`figur`) und legt
keine Vorliebe auf ein Hobby (`vorliebe`); Namen und Richtung trägt die
Äußerung. Was das verfehlt, ist `verworfen:<grund>`.

**Die Antwort wird gegen den Wortlaut der Äußerung gehalten** (`check_answer`).
`X hat_chef Y` heißt *Y ist Xs Chef*. Was das Modell an Richtung und Namen
liefert, prüft der Code, soweit der Satz es zeigt:

  * ein Name steht als Name in der Bitte — groß geschrieben, ohne Verb, in
    der Grundform; *Merten* passt auf *Mertens*, *Mertens* in der Stellung
    des Genitivs nicht;
  * *ICH* nur, wenn die Bitte in der ersten Person spricht — *unser* zählt
    wie *mein*;
  * bei einer Beziehung `hat_…` ist der Besitzer im Satz (*Ilvas*,
    *… von Ilva*, *mein*) das Subjekt, nie das Objekt;
  * bei `heisst` ist das Subjekt nie der Besitzer — *Mertens Mutter heißt …*
    nennt nicht Mertens Namen, *mein Hund heißt …* nicht den Namen von ICH;
    *mein Name* nennt ihn.

Ein Tripel, das das verfehlt, schreibt nichts.

Prompt-Schema: [BLOCKNAME]-Format unter `prompts/default/classify_fakten.*`.
"""

import logging
import re
from typing import NamedTuple

from agents.fakten.beziehungen import (
    ENTITY_TYPES,
    KANON,
    TYP_PERSON,
    TYP_SONSTIGES,
    Relation,
    find_relation,
)
from config import ASSISTANT_NAME, PROMPTS, get_node_config
from services.model_services import ChatRequest, model_service

logger = logging.getLogger("ki_server.agents.fakten.klassifikation")

# Das Subjekt, wenn der Mensch über sich selbst spricht.
SELF: str = "ICH"

# Sprecher eines Kandidaten → Herkunft des Fakts. Nur die Worte des Menschen
# werden ein Fakt; andere Sprecher gehen nicht ins Modell, und ein Tripel, das
# auf einen ihrer Kandidaten zeigt, wird verworfen.
SPEAKER_ORIGIN: dict[str, str] = {"nutzer": "mensch"}

# Äußerungen, die nach einem Fakt klingen und keiner sind — die eine Quelle für
# den Prompt der Klassifikation und für `FactsAgent.negativfaelle`.
NEGATIVE_CASES: tuple[str, ...] = (
    "eine Anweisung an die Figur, wie sie sich verhalten oder sprechen soll "
    "('sei ab jetzt frecher') — das ist kein Fakt über den Menschen",
    "eine Anweisung an die Figur über sie selbst — wie sie genannt werden, wer "
    "oder was sie sein, woher sie kommen soll ('ab sofort nennst du dich Ilva') — "
    "das ist kein Fakt über die Figur und keiner über den Menschen",
    "eine Vorliebe, ein Geschmack oder ein Vergleich ('Merten findet Jazz schöner "
    "als Techno') — das ist kein Hobby und keine andere Beziehung der Liste",
    "ein Satz im Rollenspiel oder in einer erfundenen Geschichte "
    "('mein Drache wohnt in der Höhle') — erfunden ist nicht der Fall",
    "eine Metapher oder Übertreibung ('mein Kopf ist ein Sieb') — "
    "gemeint ist nicht, was dasteht",
    "etwas, das auf eine Liste soll oder besorgt werden muss "
    "('wir brauchen noch Mehl') — das ist keine Beziehung",
    "ein Vorhaben oder Vorgang mit Zeitpunkt ('ich gehe Freitag zum Arzt') "
    "— ein Fakt trägt keine Zeit",
)

# Die Gründe, aus denen ein Tripel verworfen wird (`vet_triple`).
REJECT_FORM:       str = "form"
REJECT_CANDIDATE:  str = "kandidat_unbekannt"
REJECT_SPEAKER:    str = "sprecher"
REJECT_PRECHECK:   str = "vorpruefung"
REJECT_CANON:      str = "kanon"
REJECT_UTTERANCE:  str = "aeusserung"
REJECT_FIGURE:     str = "figur"
REJECT_TASTE:      str = "vorliebe"
REJECT_NO_EVENT:   str = "ereignis_fehlt"
# Das Feld `typ` fehlt oder nennt keinen Wert aus `ENTITY_TYPES` — ein Ausfall
# der Antwort, nie `sonstiges`.
REJECT_TYPE_FORM:  str = "typ_form"
# Der Typ des Subjekts steht in der Liste, aber die Beziehung erlaubt ihn nicht.
REJECT_TYPE:       str = "subjekt_typ"
REJECT_REASONS: frozenset[str] = frozenset({
    REJECT_FORM, REJECT_CANDIDATE, REJECT_SPEAKER, REJECT_PRECHECK, REJECT_CANON,
    REJECT_UTTERANCE, REJECT_FIGURE, REJECT_TASTE, REJECT_NO_EVENT,
    REJECT_TYPE_FORM, REJECT_TYPE,
})

# Die Marke eines Kandidaten, dessen Ereignis in diesem Turn in der Timeline
# eingetragen wurde: Er liefert das Tripel des Ergebnisses, obwohl er eine Zeit trägt.
EVENT_MARK: str = "EREIGNIS EINGETRAGEN"


class ModelCallError(RuntimeError):
    """Der Modellaufruf der Klassifikation ist ausgefallen — nie *kein Tripel*."""


class AnswerFormError(ValueError):
    """Die Antwort des Modells hat nicht die verlangte Form — nie *kein Tripel*."""


class Verdict(NamedTuple):
    """Das Urteil über ein Tripel der Antwort.

    `tripel` ist das geprüfte Tripel (subjekt, beziehung, objekt, herkunft,
    kandidat) oder None; dann nennt `grund` einen Wert aus `REJECT_REASONS`
    und `detail` den Anlass.
    """

    tripel: dict | None
    grund:  str
    detail: str

# Ein Wort der Bitte: Buchstaben, Ziffern, Bindestrich und Apostroph im Wort
# (*Anna-Lena*, *Klaus'*), ohne führendes Satzzeichen.
_WORD: re.Pattern[str] = re.compile(r"\w[\w'’-]*")

# Mit einem dieser Wörter ist ICH der Besitzer im Satz (*mein Nachbar*, *unser
# Hund*): Was der Mensch mit anderen teilt, besitzt er auch.
_FIRST_PERSON_POSSESSIVE: frozenset[str] = frozenset({
    "mein", "meine", "meinem", "meinen", "meiner", "meines",
    "unser", "unsere", "unserem", "unseren", "unserer", "unseres",
    "unsre", "unsrem", "unsren", "unsrer", "unsres",
})
# Mit einem dieser Wörter spricht die Bitte in der ersten Person.
_FIRST_PERSON: frozenset[str] = frozenset({"ich", "mich", "mir"}) | _FIRST_PERSON_POSSESSIVE
# Nach diesen Wörtern besitzt ICH nichts: *mein Name* ist der Name von ICH selbst.
_OWN_NAME: frozenset[str] = frozenset({"name", "namen", "vorname", "vornamen"})
# Endungen des Genitivs an einem Namen: *Mertens*, *Ilva's*, *Klaus'*.
_GENITIVE_ENDINGS: tuple[str, ...] = ("s", "'s", "’s", "'", "’")

# Die Figur in der Anrede: Ein Tripel über *du* ist eine Anweisung an sie, kein Fakt.
_SECOND_PERSON: frozenset[str] = frozenset({
    "du", "dich", "dir", "dein", "deine", "deinem", "deinen", "deiner", "deines",
})
# Wörter einer Vorliebe (*mögen*, *lieber*, *am liebsten*, *Lieblings…*): Der
# Kanon hat keine Vorliebe, und ein Hobby ist etwas anderes.
_TASTE_WORDS: frozenset[str] = frozenset({
    "mag", "magst", "mögen", "mögt", "mochte", "mochtest", "mochten", "mochtet",
    "möchte", "möchtest", "möchten", "möchtet", "lieber", "liebsten",
})
_TASTE_PREFIX: str = "lieblings"
# Die Beziehung, auf die eine Vorliebe gelegt wird, wenn sie keine hat.
_TASTE_TARGET: str = "hat_hobby"

# Beziehungen, deren Subjekt der Besitzer ist: *Ilvas Bruder* ist Ilva hat_bruder.
_POSSESSIVE_PREFIX: str = "hat_"
# Beziehungen, deren Subjekt nie der Besitzer eines anderen ist.
_SUBJECT_NEVER_POSSESSOR: frozenset[str] = frozenset({"heisst"})


def build_classify_prompt() -> str:
    """Baut den System-Prompt der Klassifikation aus den drei Bausteinen.

    Vorbedingung: Die Bausteine `classify_fakten.identity`, `.task` und
        `.rules` sind geladen; `.task` trägt die Platzhalter `{beziehungen}`,
        `{negativfaelle}` und `{typen}`.
    Nachbedingung: Der Prompt nennt jede Beziehung des Kanons genau so, wie
        der Kanon sie schreibt, jeden Negativfall aus `NEGATIVE_CASES` und
        jeden Typ aus `ENTITY_TYPES`.
    Fehlerfälle: KeyError, wenn ein Baustein fehlt; RuntimeError, wenn eine
        Beziehung, ein Negativfall oder ein Typ im fertigen Prompt fehlt.
    """
    # ── Verarbeitung ────────────────────────────
    beziehungen: str = "\n".join(f"  - {attribut}" for attribut in sorted(KANON))
    negativfaelle: str = "\n".join(f"  - {fall}" for fall in NEGATIVE_CASES)
    typen: str = "\n".join(f"  - {typ}" for typ in ENTITY_TYPES)
    prompt: str = "\n\n".join([
        PROMPTS["classify_fakten.identity"],
        PROMPTS["classify_fakten.task"].format(beziehungen=beziehungen,
                                               negativfaelle=negativfaelle, typen=typen),
        PROMPTS["classify_fakten.rules"],
    ])

    # ── Ausgabe-Verifikation ────────────────────
    fehlend: list[str] = [a for a in KANON if f"  - {a}\n" not in f"{prompt}\n"]
    fehlend += [f for f in NEGATIVE_CASES if f"  - {f}\n" not in f"{prompt}\n"]
    fehlend += [t for t in ENTITY_TYPES if f"  - {t}\n" not in f"{prompt}\n"]
    if fehlend:
        raise RuntimeError(f"Klassifikation Fakten: Prompt ohne {fehlend}")
    return prompt


def build_classify_input(utterance: str, numbered: dict[int, dict],
                         events: dict[int, int | None] | None = None) -> str:
    """Baut die Nachricht an das Modell: die Äußerung und die nummerierten Kandidaten.

    Vorbedingung: `utterance` ist nicht leer; `numbered` ist nicht leer und
        bildet die Nummer, die der Code vergibt, auf einen Kandidaten mit
        `objekt`, `klasse`, `eigenschaft` und `wert` ab. `events` bildet die
        Nummer eines Kandidaten auf die Timeline-Zeile seines Ereignisses ab
        (None: das Eintragen scheiterte); fehlt es, trägt kein Kandidat eines.
    Nachbedingung: ein Text, der jede Nummer genau einmal als `[n]` trägt;
        ein Kandidat mit eingetragenem Ereignis trägt `EVENT_MARK`, einer mit
        gescheitertem nicht.
    Fehlerfälle: ValueError bei leerer Äußerung oder ohne Kandidaten;
        KeyError, wenn einem Kandidaten ein Feld fehlt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not utterance.strip() or not numbered:
        raise ValueError("Klassifikation Fakten: ohne Äußerung oder ohne Kandidaten")  # noqa: TRY003
    eingetragen: frozenset[int] = frozenset(
        nummer for nummer, zeile in (events or {}).items() if zeile is not None
    )

    # ── Verarbeitung ────────────────────────────
    zeilen: list[str] = [
        f"[{nummer}] Objekt: {k['objekt']} (Klasse: {k['klasse']}) | "
        f"Eigenschaft: {k['eigenschaft']} | Wert: {k['wert']}"
        + (f" | {EVENT_MARK}" if nummer in eingetragen else "")
        for nummer, k in sorted(numbered.items())
    ]
    text: str = (
        f"AEUSSERUNG DES MENSCHEN:\n{utterance.strip()}\n\n"
        "KANDIDATEN (was die Sachlage aus dieser Aeusserung abgelegt hat):\n"
        + "\n".join(zeilen)
    )

    # ── Ausgabe-Verifikation ────────────────────
    if any(text.count(f"[{nummer}] Objekt:") != 1 for nummer in numbered):
        raise RuntimeError("Klassifikation Fakten: Nummer eines Kandidaten nicht eindeutig")  # noqa: TRY003
    return text


def classify_candidates(utterance: str, numbered: dict[int, dict],
                        events: dict[int, int | None] | None = None) -> dict:
    """Der eine Modellaufruf eines Turns: Vorprüfung und 0…n Tripel.

    Vorbedingung: wie `build_classify_input` — nur Kandidaten des Menschen;
        `events` wie dort.
    Nachbedingung: `{"dauerhaft": bool, "grund": str, "tripel": list}`; die
        Tripel stehen, wie das Modell sie nennt, und sind ungeprüft
        (`vet_triple`). Verneint die Vorprüfung und fehlt `tripel`, ist die
        Liste leer.
    Fehlerfälle: ModelCallError, wenn der Aufruf wirft; AnswerFormError,
        wenn die Antwort kein Objekt ist, `dauerhafte_aussage` kein
        Wahrheitswert ist oder `tripel` keine Liste — beides ist ein Ausfall
        und darf nie wie *kein Tripel* aussehen.
    """
    # ── Eingabe-Validierung ─────────────────────
    # Wirft ValueError ohne Äußerung oder ohne Kandidaten.
    nachricht: str = build_classify_input(utterance, numbered, events)

    # ── Verarbeitung ────────────────────────────
    node_cfg: dict = get_node_config("router")
    anfrage = ChatRequest(
        messages          = [{"role": "user", "content": nachricht}],
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
        raise ModelCallError(  # noqa: TRY003 — die Art des Ausfalls gehört in den Eintrag
            f"Modellaufruf fehlgeschlagen: {type(fehler).__name__}",
        ) from fehler

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(antwort, dict) or not isinstance(antwort.get("dauerhafte_aussage"), bool):
        logger.error("klassifizieren: Antwort ohne Vorprüfung: %.300r", antwort)
        raise AnswerFormError("Antwort ohne Wahrheitswert dauerhafte_aussage")  # noqa: TRY003
    dauerhaft: bool = antwort["dauerhafte_aussage"]
    tripel: object = antwort.get("tripel", None if dauerhaft else [])
    if not isinstance(tripel, list):
        logger.error("klassifizieren: Antwort ohne Liste tripel: %.300r", antwort)
        raise AnswerFormError("Antwort ohne Liste tripel")  # noqa: TRY003
    grund: str = str(antwort.get("grund") or "")
    logger.info("klassifizieren: dauerhaft=%s, %d Tripel, %d Kandidaten", dauerhaft,
                len(tripel), len(numbered))
    return {"dauerhaft": dauerhaft, "grund": grund, "tripel": tripel}


def vet_triple(triple: object, candidates: dict[int, dict], utterance: str,
               dauerhaft: bool) -> Verdict:
    """Prüft ein Tripel der Antwort, bevor es schreiben darf.

    In dieser Reihenfolge: die Form (ein Objekt mit einer Nummer); die
    Nummer zeigt auf einen Kandidaten des Turns; sein Sprecher hat eine
    Herkunft (`SPEAKER_ORIGIN`); die Vorprüfung bejahte eine dauerhafte
    Aussage; die Beziehung steht im Kanon; Subjekt und Objekt sind nicht
    leer; der Typ des Subjekts steht in der Liste und die Beziehung erlaubt
    ihn (`_check_subject_type`); Tripel und Kandidat sprechen nicht über die
    Figur, keine Vorliebe liegt auf einem Hobby, und `check_answer` besteht
    gegen die Äußerung (`_against_utterance`).

    Vorbedingung: `candidates` sind **alle** Kandidaten des Turns, nummeriert
        wie in der Eingabe des Modells — auch die anderer Sprecher, damit
        eine Nummer auf sie erkannt wird und nicht als unbekannt gilt.
    Nachbedingung: Ein Verdict mit dem Tripel (`subjekt`, `beziehung` des
        Kanons, `objekt`, `herkunft` aus dem Kandidaten, `kandidat` als
        Nummer) und leerem Grund — oder ohne Tripel, mit einem Grund aus
        `REJECT_REASONS`.
    Fehlerfälle: ValueError bei leerer Äußerung.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not utterance.strip():
        raise ValueError("vet_triple: leere Äußerung")  # noqa: TRY003
    nummer: object = triple.get("kandidat") if isinstance(triple, dict) else None
    if isinstance(nummer, str) and nummer.strip().isdigit():
        nummer = int(nummer.strip())
    if not isinstance(nummer, int) or isinstance(nummer, bool):
        return Verdict(None, REJECT_FORM, f"keine Nummer eines Kandidaten: {triple!r:.120}")

    # ── Verarbeitung ────────────────────────────
    kandidat: dict | None = candidates.get(nummer)
    if kandidat is None:
        return Verdict(None, REJECT_CANDIDATE, f"Nummer {nummer} nicht im Turn")
    herkunft: str | None = SPEAKER_ORIGIN.get(str(kandidat.get("sprecher")))
    if herkunft is None:
        return Verdict(None, REJECT_SPEAKER, f"Kandidat {nummer} von {kandidat.get('sprecher')!r}")
    if not dauerhaft:
        return Verdict(None, REJECT_PRECHECK, "die Vorprüfung verneint eine dauerhafte Aussage")
    beziehung: Relation | None = find_relation(triple.get("beziehung"))
    if beziehung is None:
        return Verdict(None, REJECT_CANON, f"Beziehung {triple.get('beziehung')!r} nicht im Kanon")
    subjekt: str = _as_self(str(triple.get("subjekt") or "").strip())
    objekt: str = _as_self(str(triple.get("objekt") or "").strip())
    if not subjekt or not objekt:
        return Verdict(None, REJECT_FORM, "Subjekt oder Objekt fehlt")
    verfehlt: tuple[str, str] | None = (
        _check_subject_type(triple.get("typ"), subjekt, beziehung)
        or _against_utterance(utterance, subjekt, beziehung, objekt, kandidat)
    )

    # ── Ausgabe-Verifikation ────────────────────
    if verfehlt is not None:
        logger.error("klassifizieren: Tripel verworfen — %s (%s %s %s)", verfehlt[1], subjekt,
                     beziehung.attribut, objekt)
        return Verdict(None, *verfehlt)
    return Verdict({"subjekt": subjekt, "beziehung": beziehung.attribut, "objekt": objekt,
                    "herkunft": herkunft, "kandidat": nummer}, "", "")


def link_event(verdict: Verdict, events: dict[int, int | None]) -> Verdict:
    """Hängt an ein geprüftes Tripel die Timeline-Zeile des Ereignisses seines Kandidaten.

    Der Fakt eines Ereignisses verweist auf dessen Zeile (`fakten.timeline_id`).
    Scheiterte das Eintragen, entsteht kein Fakt: Er stünde sonst ohne das
    Ereignis, aus dem er folgt.

    Vorbedingung: `verdict` kommt aus `vet_triple`; `events` bildet die
        Nummer eines Kandidaten auf die Zeile ab, None bei gescheitertem Eintrag.
    Nachbedingung: ein verworfenes Urteil unverändert; ein Tripel ohne
        Ereignis unverändert; eines mit Ereignis trägt `timeline_id`; eines
        auf einen gescheiterten Eintrag ist verworfen mit `ereignis_fehlt`.
    Fehlerfälle: eine Zeile, die keine positive ganze Zahl ist, wirft ValueError.
    """
    # ── Eingabe-Validierung ─────────────────────
    if verdict.tripel is None or verdict.tripel["kandidat"] not in events:
        return verdict
    nummer: int = verdict.tripel["kandidat"]
    zeile: int | None = events[nummer]

    # ── Verarbeitung ────────────────────────────
    if zeile is None:
        logger.error("klassifizieren: Tripel auf Kandidat %d verworfen — sein Ereignis fehlt",
                     nummer)
        return Verdict(None, REJECT_NO_EVENT, f"Ereignis des Kandidaten {nummer} nicht eingetragen")

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(zeile, int) or isinstance(zeile, bool) or zeile <= 0:
        raise ValueError(f"link_event: Timeline-Zeile {zeile!r} ungültig")  # noqa: TRY003
    return Verdict({**verdict.tripel, "timeline_id": zeile}, "", "")


def _check_subject_type(typ: object, subjekt: str,
                        beziehung: Relation) -> tuple[str, str] | None:
    """Hält den Typ des Subjekts, den das Modell nennt, gegen die Liste und die Beziehung.

    **ICH ist der Mensch und gilt als Person**: Nennt das Modell bei ICH
    einen anderen Typ der Liste, hat es ein anderes Subjekt gemeint (*mein
    Hund wohnt in Ostheim* als ICH `wohnt_in` mit `tier`), und das Tripel
    schreibt nicht — auch wo die Beziehung den Typ erlaubt. `sonstiges` geht
    durch, auch bei ICH: Das Modell ordnet nicht ein, und ohne Einordnung
    gilt jede Entität als `sonstiges`.

    Vorbedingung: `subjekt` nicht leer und schon als `SELF` geschrieben,
        `beziehung` aus dem Kanon; `typ` ist das Feld der Antwort, ungeprüft.
    Nachbedingung: None, wenn der Typ `sonstiges` ist oder die Beziehung ihn
        erlaubt (bei ICH: `person`); sonst (Grund aus `REJECT_REASONS`, Anlass).
    Fehlerfälle: ein fehlendes, leeres oder nicht-textliches Feld und ein Wert
        außerhalb von `ENTITY_TYPES` ergeben `REJECT_TYPE_FORM`, ein Typ, den
        die Beziehung nicht erlaubt, `REJECT_TYPE` — laut macht beide
        `vet_triple` mit `logger.error`, einmal je Tripel wie bei
        `_against_utterance`. ValueError bei leerem Subjekt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not subjekt:
        raise ValueError("_check_subject_type: leeres Subjekt")  # noqa: TRY003
    gelesen: str | None = typ.strip().lower() if isinstance(typ, str) else None
    if gelesen not in ENTITY_TYPES:
        return REJECT_TYPE_FORM, f"Typ des Subjekts {typ!r:.60} nicht in {list(ENTITY_TYPES)}"

    # ── Verarbeitung ────────────────────────────
    erlaubt: frozenset[str] = (frozenset({TYP_PERSON}) if subjekt == SELF
                               else beziehung.subjekt_typen)

    # ── Ausgabe-Verifikation ────────────────────
    if gelesen == TYP_SONSTIGES:
        logger.info("klassifizieren: Typ des Subjekts sonstiges — durchgelassen (%s %s)",
                    subjekt, beziehung.attribut)
        return None
    if gelesen not in erlaubt:
        return REJECT_TYPE, (f"Subjekt {subjekt!r} mit Typ {gelesen} — {beziehung.attribut} "
                             f"erlaubt {sorted(erlaubt)}")
    return None


def _against_utterance(utterance: str, subjekt: str, beziehung: Relation, objekt: str,
                       kandidat: dict) -> tuple[str, str] | None:
    """Hält ein Tripel gegen die Äußerung: Figur, Vorliebe, dann `check_answer`.

    **Die Figur:** Ist das Subjekt die Figur — ihr Name (`ASSISTANT_NAME`)
    oder *du* in einer Form — oder ist der Kandidat ein Objekt der Figur, sagt
    der Mensch der Figur, wer sie ist. Das ist eine Anweisung, kein Fakt.
    **Die Vorliebe:** Ein `hat_hobby` aus einem Satz mit *mögen*, *lieber*,
    *am liebsten* oder *Lieblings…* ist ein Geschmack, den der Kanon nicht
    kennt; ein Hobby ist etwas, das jemand tut. Beide Klassen bestehen
    Vorprüfung und `check_answer`, wenn das Modell sich irrt.

    Vorbedingung: `utterance`, `subjekt` und `objekt` nicht leer und gestutzt,
        `beziehung` aus dem Kanon, `kandidat` der Kandidat des Tripels.
    Nachbedingung: (Grund aus `REJECT_REASONS`, Anlass) — `figur`,
        `vorliebe` oder `aeusserung` (`check_answer`) —, sonst None.
    Fehlerfälle: ValueError bei leerer Äußerung, leerem Subjekt oder Objekt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not utterance.strip() or not subjekt or not objekt:
        raise ValueError(  # noqa: TRY003
            "_against_utterance: Äußerung, Subjekt und Objekt dürfen nicht leer sein")

    # ── Verarbeitung ────────────────────────────
    # Ohne `- {""}` träfe ein leerer Name der Figur jeden Kandidaten ohne Objekt.
    figur: frozenset[str] = (_SECOND_PERSON | {ASSISTANT_NAME.strip().casefold()}) - {""}
    objekt_des_kandidaten: str = str(kandidat.get("objekt") or "").strip()
    ueber_figur: bool = (subjekt.casefold() in figur
                         or objekt_des_kandidaten.casefold() in figur)
    woerter: list[str] = [_norm(w) for w in _WORD.findall(utterance)]
    vorliebe: list[str] = [w for w in woerter
                           if w in _TASTE_WORDS or w.startswith(_TASTE_PREFIX)]

    # ── Ausgabe-Verifikation ────────────────────
    if ueber_figur:
        return REJECT_FIGURE, (f"das Tripel spricht über die Figur ({subjekt!r}, Kandidat "
                               f"{objekt_des_kandidaten!r}) — eine Anweisung, kein Fakt")
    if beziehung.attribut == _TASTE_TARGET and vorliebe:
        return REJECT_TASTE, (f"{_TASTE_TARGET} aus einer Vorliebe ({', '.join(vorliebe)}) — "
                              "der Kanon kennt keine Vorliebe")
    verfehlt: str | None = check_answer(utterance, subjekt, beziehung, objekt)
    return None if verfehlt is None else (REJECT_UTTERANCE, verfehlt)


def check_answer(aufgabe: str, subjekt: str, beziehung: Relation, objekt: str) -> str | None:
    """Hält Subjekt und Objekt der Antwort gegen den Wortlaut der Äußerung.

    Geprüft wird jeder Name, der eine Entität wird: das Subjekt immer, das
    Objekt, wenn die Beziehung eine Objekt-Entität hat. Ein Wert (Beruf,
    Hobby, Name bei `heisst`) darf umformuliert sein und wird nicht geprüft.
    Im Code heißt die Äußerung noch `bitte`: Sie war es, bis der Agent
    passiv wurde; geprüft wird derselbe Wortlaut.

    Vorbedingung: `aufgabe` (die Äußerung), `subjekt` und `objekt` sind nicht
        leer; ICH ist schon als `SELF` geschrieben.
    Nachbedingung: None, wenn jeder geprüfte Name als Name in der Äußerung
        steht und die Richtung zum Besitzer im Satz passt; sonst der Grund,
        warum das Tripel nichts schreiben darf.
    Fehlerfälle: ValueError bei leerer Äußerung, leerem Subjekt oder Objekt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not aufgabe.strip() or not subjekt or not objekt:
        raise ValueError("check_answer: Äußerung, Subjekt und Objekt dürfen nicht leer sein")

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
    if beziehung.attribut in _SUBJECT_NEVER_POSSESSOR and besitzer["subjekt"]:
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
        oder, bei ICH, mit einem Possessiv der ersten Person (*mein Hund*),
        auf das nicht *Name* folgt (*mein Name* besitzt nichts). Sonst
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
        nachfolger: list[str] = [*normiert[1:], ""]
        return None, any(
            wort in _FIRST_PERSON_POSSESSIVE and folgt not in _OWN_NAME
            for wort, folgt in zip(normiert, nachfolger, strict=True)
        )
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
