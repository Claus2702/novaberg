"""Objekt-Naehe — der Empfang rechnet, welchen Diensten ein akutes Objekt gehoert.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 12, Teil C2. Je
akutem Objekt der Sachlage wird die Naehe zum Objekt-Merkmal jedes Dienstes
gerechnet (`agents/object_feature.py`) und **je Zettel fuer sich** beurteilt:
Das Objekt steht an jedem Dienst, dessen Naehe die Untergrenze erreicht — an
keinem, an einem oder an mehreren. **Kein Vergleich zwischen Merkmalen
entscheidet** (entschieden am 16.09.2026): Er machte das Urteil ueber einen
Dienst davon abhaengig, wer sonst angemeldet ist. Der Abstand zwischen groesster
und zweitgroesster Naehe wird weiter protokolliert, als Mass der Mehrdeutigkeit.

**Das Ergebnis geht ins Protokoll und als Rueckgabe an den Router**, der es als
`objekt_urteil` weiterreicht. Seit Teil D1 (17.09.2026) liest der Planner es:
`service_order` bildet daraus die Reihenfolge, in der die Dienste gefragt werden.
Ob ueberhaupt zugestellt wird, entscheidet weiter die Bitte — der Router.

**Der Objekttext ist die Formel der Eichung**, Zeichen fuer Zeichen: Klasse,
Name und die Namen der gedeckten und offenen Eigenschaften, keine Werte. Eine
andere Formel wuerde die Schwellen ungueltig machen, ohne dass etwas scheitert.
"""

import logging
import math
import re
from collections.abc import Callable
from dataclasses import dataclass

from agents.object_feature import FeatureVector, feature_vectors, vector_defect

logger = logging.getLogger("ki_server.agents.object_nearness")

RULE_VERSION: str = "c2-je-zettel-2026-09-16"

OUTCOME_ASSIGNED: str = "zugeordnet"
OUTCOME_SEVERAL: str = "mehrere"
OUTCOME_BELOW_FLOOR: str = "still_untergrenze"


@dataclass(frozen=True)
class ObjectJudgement:
    """Das Urteil ueber ein akutes Objekt — gerechnet, nicht benutzt."""

    name: str
    klasse: str
    text: str
    nearness: dict[str, float]
    receivers: tuple[str, ...]
    best: str
    top: float
    margin: float | None
    outcome: str


def build_object_text(obj: dict) -> str:
    """Der Embed-Text eines Lage-Objekts — die EINZIGE Formel dafuer.

    Vorbedingung: `obj` ist ein dict.
    Nachbedingung: `Klasse: <klasse oder 'ohne'>. Name: <name>` und, wenn es
        Eigenschaften gibt, `. Eigenschaften: <gedeckt-Namen>, <offen>` —
        zeichengleich mit der Formel, mit der die Schwellen am 16.09.2026
        geeicht wurden. Die Klasse ist kein Pflichtfeld: Sie fehlte bei 316 von
        1067 Objekten im Bestand.
    Fehlerfaelle: Kein dict ist ein `TypeError`.
    """
    if not isinstance(obj, dict):
        raise TypeError(f"build_object_text: Objekt ist {type(obj).__name__}, erwartet dict")
    eigenschaften = list(obj.get("gedeckt") or {}) + list(obj.get("offen") or [])
    teile = [f"Klasse: {obj.get('klasse') or 'ohne'}", f"Name: {obj.get('name') or ''}"]
    if eigenschaften:
        teile.append("Eigenschaften: " + ", ".join(str(e) for e in eigenschaften))
    return ". ".join(teile)


def cosine(a: tuple[float, ...] | list[float], b: tuple[float, ...] | list[float]) -> float:
    """Kosinus zweier Vektoren gleicher Dimension.

    Fehlerfaelle: Ungleiche Dimension ist ein `ValueError`; ein Nullvektor
        ebenfalls — er haette keine Richtung und lieferte ein "nicht nahe",
        das keine Messung ist.
    """
    if len(a) != len(b):
        raise ValueError(f"cosine: Dimension {len(a)} gegen {len(b)}")
    punkt = sum(x * y for x, y in zip(a, b, strict=True))
    la = math.sqrt(sum(x * x for x in a))
    lb = math.sqrt(sum(y * y for y in b))
    if not la or not lb:
        raise ValueError("cosine: Nullvektor hat keine Richtung")
    return punkt / (la * lb)


def judge(
    obj: dict,
    vector: list[float],
    features: dict[str, FeatureVector],
    floor: float,
) -> ObjectJudgement:
    """Beurteilt ein Objekt gegen jedes Merkmal fuer sich.

    Vorbedingung: `features` ist nicht leer; `vector` ist gueltig.
    Nachbedingung: `receivers` sind alle Dienste mit Naehe >= `floor`, nach Name;
        `outcome` ist `still_untergrenze` bei keinem, `zugeordnet` bei einem,
        `mehrere` bei mehreren. `margin` (groesste minus zweitgroesste Naehe,
        None bei nur einem Merkmal) ist Diagnose und entscheidet nichts.
    Fehlerfaelle: Leere Merkmale sind ein `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not features:
        raise ValueError("judge: keine Merkmale — nichts zu beurteilen")

    # ── Verarbeitung ────────────────────────────
    naehe = {name: cosine(vector, f.vector) for name, f in sorted(features.items())}
    rangfolge = sorted(naehe.items(), key=lambda kv: kv[1], reverse=True)
    best, top = rangfolge[0]
    abstand: float | None = top - rangfolge[1][1] if len(rangfolge) > 1 else None
    empfaenger = tuple(name for name, wert in naehe.items() if wert >= floor)
    if not empfaenger:
        ausgang = OUTCOME_BELOW_FLOOR
    elif len(empfaenger) == 1:
        ausgang = OUTCOME_ASSIGNED
    else:
        ausgang = OUTCOME_SEVERAL

    # ── Ausgabe-Verifikation ────────────────────
    if not all(-1.0 - 1e-9 <= w <= 1.0 + 1e-9 for w in naehe.values()):
        raise ValueError(f"judge: Kosinus ausserhalb [-1, 1]: {naehe}")
    if (ausgang == OUTCOME_BELOW_FLOOR) != (top < floor):
        raise ValueError(f"judge: Ausgang {ausgang} widerspricht groesster Naehe {top}")
    return ObjectJudgement(
        name=str(obj.get("name") or ""),
        klasse=str(obj.get("klasse") or ""),
        text=build_object_text(obj),
        nearness=naehe,
        receivers=empfaenger,
        best=best,
        top=top,
        margin=abstand,
        outcome=ausgang,
    )


def _embed_batch_via_worker(texts: list[str], deadline_s: float) -> list[list[float]]:
    """Die Vektoren ueber den Embed-Worker, ein Stapel — eigene Funktion fuer Zeugen."""
    from services.model_services import EmbedBatchRequest, model_service  # lokal: Startreihenfolge

    antwort = model_service.embed.submit_sync(EmbedBatchRequest(texts=texts), timeout=deadline_s)
    return [list(v) for v in antwort.embeddings]


def _record(ergebnis: str, judgements: list[ObjectJudgement], **extra: object) -> dict:
    """Der Protokolleintrag — dieselbe Form auf jedem Rueckkehrpfad."""
    from config import OBJEKT_NAEHE_UNTERGRENZE

    return {
        "ergebnis":    ergebnis,
        "untergrenze": OBJEKT_NAEHE_UNTERGRENZE,
        "regelfassung": RULE_VERSION,
        "objekte": [
            {
                "name":    j.name,
                "klasse":  j.klasse,
                "text":    j.text,
                "naehe":   {k: round(v, 4) for k, v in j.nearness.items()},
                "empfaenger": list(j.receivers),
                "bester":  j.best,
                "oben":    round(j.top, 4),
                "abstand": None if j.margin is None else round(j.margin, 4),
                "ausgang": j.outcome,
            }
            for j in judgements
        ],
        **extra,
    }


def shadow_nearness(
    state: dict,
    embed_batch: Callable[[list[str], float], list[list[float]]] | None = None,
    features: dict[str, FeatureVector] | None = None,
) -> dict:
    """Rechnet die Naehe der akuten Objekte und protokolliert sie — ohne den Zustand zu beruehren.

    Vorbedingung: keine; jede fehlende Eingabe ist ein eigener, protokollierter Ausgang.
    Nachbedingung: genau ein Eintrag im Pipeline-Log (Knoten `router`, Quelle
        `objekt_naehe`) mit `ergebnis` aus `gerechnet`, `ohne_sachlage`,
        `ohne_objektliste`, `ohne_akute_objekte`, `ohne_merkmale`, `ausfall`;
        der Zustand ist unveraendert. Zurueck kommt der Eintrag. Eine
        uebernommene Sachlage (Impuls, Ausfall) wird erneut beurteilt — `herkunft`
        steht im Eintrag, und wer Betriebszahlen zieht, filtert danach.
    Fehlerfaelle: Nichts wirft heraus — ein Schattenlauf darf den Turn nicht
        reissen. Ein Ausfall steht als `ausfall` mit Fehlerart im Eintrag und
        als `logger.error` im Log.
    """
    from config import OBJEKT_NAEHE_FRIST_S, OBJEKT_NAEHE_UNTERGRENZE

    try:
        # ── Eingabe-Validierung ─────────────────────
        sachlage = state.get("sachlage")
        if not isinstance(sachlage, dict):
            return _write(state, _record("ohne_sachlage", []))
        # Ein Impuls oder Ausfall ohne Vorgaenger traegt nur `herkunft` — eine
        # Sachlage ist da, eine Objektliste nicht. Das ist ein anderer Befund als
        # eine fehlende Sachlage und soll in der Reihe unterscheidbar sein.
        if not isinstance(sachlage.get("objekte"), list):
            return _write(
                state, _record("ohne_objektliste", [], herkunft=sachlage.get("herkunft")),
            )
        objekte = [o for o in sachlage["objekte"] if isinstance(o, dict)]
        akute = [o for o in objekte if o.get("akut") is True]
        herkunft = {"herkunft": sachlage.get("herkunft"), "latente": len(objekte) - len(akute)}
        if not akute:
            return _write(state, _record("ohne_akute_objekte", [], **herkunft))
        merkmale = feature_vectors() if features is None else features
        if not merkmale:
            return _write(state, _record("ohne_merkmale", [], **herkunft))

        # ── Verarbeitung ────────────────────────────
        texte = [build_object_text(o) for o in akute]
        einbetten = embed_batch or _embed_batch_via_worker
        vektoren = einbetten(texte, OBJEKT_NAEHE_FRIST_S)
        if len(vektoren) != len(texte):
            raise ValueError(f"{len(vektoren)} Vektoren fuer {len(texte)} Objekte")
        urteile: list[ObjectJudgement] = []
        for obj, vektor in zip(akute, vektoren, strict=True):
            mangel = vector_defect(vektor)
            if mangel is not None:
                raise ValueError(f"Objektvektor unbrauchbar ({mangel})")
            urteile.append(
                judge(obj, vektor, merkmale, OBJEKT_NAEHE_UNTERGRENZE),
            )

        # ── Ausgabe-Verifikation ────────────────────
        if len(urteile) != len(akute):
            raise ValueError(f"{len(urteile)} Urteile fuer {len(akute)} akute Objekte")
        logger.info(
            "Objekt-Naehe: %s",
            "; ".join(
                f"'{u.name}' → {'+'.join(u.receivers) or '—'} "
                f"(naechster {u.best} {u.top:.4f}) {u.outcome}"
                for u in urteile
            ),
        )
        return _write(state, _record("gerechnet", urteile, **herkunft))
    except Exception as fehler:  # noqa: BLE001 — der Schatten darf den Turn nicht reissen
        logger.exception("Objekt-Naehe (Schatten): Ausfall — nichts gerechnet")
        return _write(
            state,
            _record("ausfall", [], fehlerart=type(fehler).__name__, fehler=str(fehler)[:200]),
        )


def _write(state: dict, eintrag: dict) -> dict:
    """Schreibt den Eintrag dauerhaft; ein gescheitertes Schreiben wird gemeldet, nicht geworfen."""
    from memory.pipeline_log import log_berechnung

    turn_id = state.get("turn_id") or ""
    if not turn_id:
        logger.error("Objekt-Naehe (Schatten): ohne turn_id — Eintrag ist keinem Turn zuzuordnen")
    try:
        log_berechnung(
            turn_id      = turn_id,
            node         = "router",
            quelle       = "objekt_naehe",
            inhalt       = eintrag,
            user_id      = state.get("user_id"),
            character_id = state.get("character_id"),
        )
    except Exception:  # noqa: BLE001 — der Turn ist wichtiger als sein Protokoll
        logger.exception(
            "Objekt-Naehe (Schatten): nicht dauerhaft protokolliert (turn_id=%s, ergebnis=%s)",
            turn_id, eintrag.get("ergebnis"),
        )
    return eintrag


def service_order(verdict: dict | None) -> list[str]:
    """Die Dienste, die ein akutes Objekt erreicht, nach ihrer Naehe geordnet.

    Vorbedingung: keine — ein fehlendes oder nicht gerechnetes Urteil ergibt
        eine leere Liste.
    Nachbedingung: jeder Dienst hoechstens einmal; geordnet nach der groessten
        Naehe, mit der ihn irgendein akutes Objekt erreicht, absteigend, bei
        Gleichstand nach Name. Nur Empfaenger (Naehe >= Untergrenze) — ein
        Dienst unter der Untergrenze steht nicht darin, auch wenn er der
        naechste war.
    Fehlerfaelle: keine Ausnahme; ein unlesbarer Eintrag wird laut uebergangen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(verdict, dict) or verdict.get("ergebnis") != "gerechnet":
        return []

    # ── Verarbeitung ────────────────────────────
    beste: dict[str, float] = {}
    for objekt in verdict.get("objekte") or []:
        try:
            for dienst in objekt["empfaenger"]:
                wert = float(objekt["naehe"][dienst])
                beste[dienst] = max(beste.get(dienst, wert), wert)
        except (KeyError, TypeError, ValueError):
            logger.error("Objekt-Naehe: unlesbarer Objekteintrag im Urteil uebergangen: %r", objekt)

    # ── Ausgabe-Verifikation ────────────────────
    return sorted(beste, key=lambda d: (-beste[d], d))


def objects_for_service(sachlage: object, verdict: object, service: str) -> list[dict]:
    """Die akuten Objekte, die das Urteil an den Zettel eines Dienstes stellt — der Objektbezug.

    Vorbedingung: keine.
    Nachbedingung: je Objekt ein dict mit `name`, `klasse` (oder None) und
        `gedeckt` (Name → Wert), in der Reihenfolge der Sachlage. Leer, wenn das
        Urteil fehlt, nicht gerechnet ist, von einer uebernommenen Sachlage nach
        einem Ausfall stammt oder den Dienst bei keinem akuten Objekt nennt —
        ein geratener Bezug waere schlimmer als keiner.
    Fehlerfaelle: keine Ausnahme.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not service or not isinstance(sachlage, dict) or not isinstance(verdict, dict):
        return []
    if verdict.get("ergebnis") != "gerechnet" or verdict.get("herkunft") == "ausfall_uebernommen":
        return []

    # ── Verarbeitung ────────────────────────────
    namen: set[str] = {
        str(o.get("name") or "") for o in verdict.get("objekte") or []
        if isinstance(o, dict) and service in (o.get("empfaenger") or [])
    }
    bezug: list[dict] = []
    for objekt in sachlage.get("objekte") or []:
        if not isinstance(objekt, dict) or objekt.get("akut") is not True:
            continue
        name = str(objekt.get("name") or "")
        if name in namen:
            gedeckt = objekt.get("gedeckt") if isinstance(objekt.get("gedeckt"), dict) else {}
            bezug.append({"name": name, "klasse": objekt.get("klasse"), "gedeckt": dict(gedeckt)})

    # ── Ausgabe-Verifikation ────────────────────
    return bezug


def render_object_reference(bezug: list[dict]) -> str:
    """Die Objektzeilen eines Objektbezugs, wie Router und Klassifikation sie lesen.

    Nachbedingung: je Objekt eine Zeile `- Name (klasse) — Eigenschaft: Wert; …`;
        leer bei leerem Bezug.
    """
    zeilen: list[str] = []
    for objekt in bezug or []:
        kopf = f"- {objekt.get('name')}" + (f" ({objekt['klasse']})" if objekt.get("klasse") else "")
        gedeckt = objekt.get("gedeckt") or {}
        zeilen.append(kopf + (" — " + "; ".join(f"{k}: {v}" for k, v in gedeckt.items()) if gedeckt else ""))
    return "\n".join(zeilen)



# Die Schluessel, unter denen die Lage eine Zeitangabe fuehrt — frei benannt,
# deshalb als Wortstamm geprueft (Bestand: "Tag/Datum", "Uhrzeit", "Frist").
_TIME_KEYS: tuple[str, ...] = ("tag", "datum", "uhrzeit", "zeit", "frist", "termin", "wochentag")


_CLOCK: re.Pattern = re.compile(
    r"\bum\s+(\d{1,2})(?:[:.](\d{2}))?\b|\b(\d{1,2})(?:[:.](\d{2}))?\s*uhr\b", re.IGNORECASE,
)


def _with_clock(resolved_date: str, original: str) -> str:
    """Das aufgeloeste Datum mit der Uhrzeit aus dem urspruenglichen Wert, falls er eine traegt.

    Nachbedingung: *"19.09.2026"* + *"Samstag um 10"* → *"19.09.2026 10:00"*;
        ohne Uhrzeit im Wert bleibt das Datum allein. Eine unmoegliche Uhrzeit
        wird nicht uebernommen.
    """
    m = _CLOCK.search(str(original))
    if m is None:
        return resolved_date
    stunde = int(m.group(1) or m.group(3))
    minute = int(m.group(2) or m.group(4) or 0)
    if not (0 <= stunde <= 23 and 0 <= minute <= 59):
        return resolved_date
    return f"{resolved_date} {stunde:02d}:{minute:02d}"


def consent_fields(objekt_bezug: list[dict]) -> tuple[str, str]:
    """Ziel und Zeitangabe aus der Sache, der der Mensch zugestimmt hat.

    Vorbedingung: `objekt_bezug` sind die Objekte, die der Planner dem Dienst
        mitgegeben hat — bei einer Zustimmung genau die angebotenen.
    Nachbedingung: `(ziel, zeitausdruck)` aus dem **ersten** Objekt: sein Name,
        und aus seinen gedeckten Eigenschaften die Werte, deren Schluessel nach
        Zeit klingen (Tag, Datum, Uhrzeit, Zeit, Frist, Termin), in der
        Reihenfolge des Objekts zu einem Ausdruck verbunden. Leere Zeichenkette,
        wo nichts dasteht — **geraten wird nichts.**
    Fehlerfaelle: keine Ausnahme.

    **Warum im Code und nicht im Prompt:** `[gemessen 17.09.2026, Betrieb]` Mit
    dem `[ZUSTIMMUNG]`-Block im Prompt liess die Klassifikation Ziel und Zeit
    trotzdem leer — die Angaben standen im Block, das Modell nahm sie nicht.
    Eine Zustimmung nennt nichts; was sie meint, steht fest, und Festes wird
    gesetzt, nicht erbeten.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not objekt_bezug or not isinstance(objekt_bezug[0], dict):
        return "", ""

    # ── Verarbeitung ────────────────────────────
    objekt = objekt_bezug[0]
    ziel: str = str(objekt.get("name") or "").strip()
    gedeckt = objekt.get("gedeckt") if isinstance(objekt.get("gedeckt"), dict) else {}
    zeitwerte: dict[str, str] = {
        str(schluessel): str(wert).strip() for schluessel, wert in gedeckt.items()
        if any(w in str(schluessel).casefold() for w in _TIME_KEYS) and str(wert).strip()
    }
    # Eine relative Angabe, zu der die Lage das Datum festgehalten hat, wird
    # durch dieses ersetzt (Scheibe 12 D, 18.09.2026): "morgen" gilt dem Tag,
    # an dem es gesagt wurde, nicht dem, an dem jemand zustimmt.
    aufgeloest: dict[str, str] = {
        k[: -len(" (aufgeloest)")]: v for k, v in zeitwerte.items() if k.endswith(" (aufgeloest)")
    }
    # Die Aufloesung ersetzt nur den Tag. Steht die Uhrzeit im selben Feld
    # ("Samstag um 10"), bleibt sie erhalten — `[zweite Kontrolle 18.09.2026]`
    # vorher ging sie bei 7 von 29 echten Objekten verloren, und aus 10:00
    # wurde ein ganztaegiger Termin.
    teile: list[str] = [
        _with_clock(aufgeloest[k], v) if k in aufgeloest else v
        for k, v in zeitwerte.items() if not k.endswith(" (aufgeloest)")
    ]

    # ── Ausgabe-Verifikation ────────────────────
    return ziel, " ".join(teile)
