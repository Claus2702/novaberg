"""Die Kandidatensuche des lesenden Dienstes — scharf vor unscharf.

Spezifikation: docs/novaberg-agent-dateien_k.md §6.1, §6.3, §8.1.

**Die Reihenfolge ist die Aussage dieses Moduls.** Entitaeten und Stichwoerter
sind exakt; sie bilden die Kandidatenmenge. Der Kosinus entscheidet **innerhalb**
dieser Menge und nicht ueber sie.

Der Grund steht in §6.3 und ist eine Eigenschaft des Index, keine Vorliebe:
`pgvector` filtert nach Voreinstellung **hinterher** — der Vektorindex laeuft,
dann greift die Bedingung auf die Kandidaten. Bei einer engen Bedingung bleiben
dadurch weniger Treffer uebrig, als die Kappung erlaubt, **ohne dass es
auffaellt**. Wer die Reihenfolge umdreht, bekommt ein leeres Ergebnis, das wie
"nichts gefunden" aussieht und "falsch gesucht" heisst.

**Dieses Modul liest den Index, nicht die Datei.** Der Griff zur Datei ist der
Zoom (`zoom.py`) und kostet einen Dateizugriff je Stufe.
"""

import logging

from config import DATEIEN_SUCHE_KAPPUNG
from memory.utils import embedding_zu_pgvector_str
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.dateien.suche")

#: Woher die Kandidaten stammen. Geschlossene Menge — der Kanal gehoert in
#: die Antwort, weil "ueber den Namen gefunden" und "semantisch am naechsten"
#: verschieden verlaesslich sind und der Mensch das wissen darf.
KANAL_NAME: str = "name"
KANAL_STICHWORT: str = "stichwort"
KANAL_VEKTOR: str = "vektor"
KANAELE: frozenset[str] = frozenset({KANAL_NAME, KANAL_STICHWORT, KANAL_VEKTOR})

#: Die Spalten, die ein Kandidat mitbringt. Einmal hier, damit die drei
#: Abfragen unten nicht auseinanderlaufen koennen.
_SPALTEN: str = (
    "i.id, i.pfad, i.name, i.thema, i.zusammenfassung, i.stichwoerter, "
    "i.struktur, i.zeilen, w.pfad AS wurzel, w.bezeichnung"
)

_VON: str = (
    "FROM dateien_index i "
    "JOIN dateien_wurzeln w ON w.id = i.wurzel_id "
    "WHERE w.user_id = %s AND w.character_id = %s "
    "  AND w.aktiv = TRUE AND i.aktiv = TRUE"
)


def _paar_pruefen(user_id: str, character_id: str) -> bool:
    """Prueft, dass beide Kennungen des Paares vorliegen.

    Vorbedingung: keine.
    Nachbedingung: True nur, wenn beide nicht leer sind. Fehlt eine, waere der
    Treffer aus einer fremden Freigabe — das wird laut gemeldet und nicht
    stillschweigend zu einer leeren Ergebnismenge.
    """
    if not user_id or not character_id:
        logger.error(
            "Dateien-Suche: unvollstaendiges Paar (user_id=%r, character_id=%r) "
            "— keine Abfrage",
            user_id, character_id,
        )
        return False
    return True


def nach_name(user_id: str, character_id: str, muster: str) -> list[dict]:
    """Findet Dateien, deren Name das Muster enthaelt — der schaerfste Kanal.

    Vorbedingung: `muster` ist nicht leer.
    Nachbedingung: Hoechstens `DATEIEN_SUCHE_KAPPUNG` Zeilen, jede mit
    `kanal = "name"`. Leer, wenn nichts passt — das ist eine Antwort.
    Fehlerfaelle: Datenbankfehler werden protokolliert und ergeben eine leere
    Liste; der Aufrufer erfaehrt den Kanal, auf dem nichts kam.

    **Der Name wird nicht eingebettet** (`F-EMBED-1`): Was man exakt
    vergleichen kann, gehoert nicht in den Vektor.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not muster.strip():
        logger.error("Dateien-Suche: leeres Namensmuster — keine Abfrage")
        return []
    if not _paar_pruefen(user_id, character_id):
        return []

    # ── Verarbeitung ────────────────────────────
    try:
        zeilen: list[dict] = db_manager.select(
            f"SELECT {_SPALTEN} {_VON} AND i.name ILIKE %s "
            f"ORDER BY length(i.name), i.name LIMIT %s",
            (user_id, character_id, f"%{muster.strip()}%", DATEIEN_SUCHE_KAPPUNG),
        )
    except Exception as fehler:
        logger.exception(
            "%s: Dateien-Suche ueber den Namen fehlgeschlagen", type(fehler).__name__,
        )
        return []

    # ── Ausgabe-Verifikation ────────────────────
    for zeile in zeilen:
        zeile["kanal"] = KANAL_NAME
    logger.info(
        "Dateien-Suche: Name '%s' → %d Treffer", muster.strip(), len(zeilen),
    )
    return zeilen


def nach_stichwort(user_id: str, character_id: str, woerter: list[str]) -> list[dict]:
    """Findet Dateien ueber Stichwoerter und den lexikalischen Kanal.

    Vorbedingung: `woerter` ist nicht leer.
    Nachbedingung: Hoechstens `DATEIEN_SUCHE_KAPPUNG` Zeilen, jede mit
    `kanal = "stichwort"`.
    Fehlerfaelle: wie oben.

    **Bei dieser Bestandsgroesse ist das der staerkere Kanal** (§6.2): Ein
    Embedding ueber Thema und Stichwoerter mittelt, ein exakter Begriff nicht.
    Deshalb laeuft er vor dem Vektor und nicht neben ihm.
    """
    # ── Eingabe-Validierung ─────────────────────
    sauber: list[str] = [w.strip().lower() for w in woerter if w.strip()]
    if not sauber:
        logger.error("Dateien-Suche: keine brauchbaren Stichwoerter — keine Abfrage")
        return []
    if not _paar_pruefen(user_id, character_id):
        return []

    # ── Verarbeitung ────────────────────────────
    # Zwei scharfe Wege in einer Abfrage: das Array der beim Indizieren
    # erhobenen Stichwoerter, und der `tsvector` ueber denselben Text. Der
    # erste trifft den Begriff, der zweite seine Beugung.
    try:
        zeilen: list[dict] = db_manager.select(
            f"SELECT {_SPALTEN} {_VON} "
            f"  AND (ARRAY(SELECT lower(unnest(i.stichwoerter))) && %s::text[] "
            f"       OR i.suchtext @@ plainto_tsquery('german', %s)) "
            f"ORDER BY i.name LIMIT %s",
            (user_id, character_id, sauber, " ".join(sauber), DATEIEN_SUCHE_KAPPUNG),
        )
    except Exception as fehler:
        logger.exception(
            "%s: Dateien-Suche ueber Stichwoerter fehlgeschlagen", type(fehler).__name__,
        )
        return []

    # ── Ausgabe-Verifikation ────────────────────
    for zeile in zeilen:
        zeile["kanal"] = KANAL_STICHWORT
    logger.info(
        "Dateien-Suche: Stichwoerter %s → %d Treffer", sauber, len(zeilen),
    )
    return zeilen


def nach_vektor(
    user_id: str, character_id: str, such_vektor: list[float],
    kandidaten_ids: list[int] | None = None,
) -> list[dict]:
    """Ordnet nach semantischer Naehe — innerhalb der Kandidatenmenge.

    Vorbedingung: `such_vektor` traegt den Suchschluessel des Turns. Sind
    `kandidaten_ids` gesetzt, wird **nur** innerhalb dieser Menge geordnet;
    ist die Liste leer, wird ueber den ganzen Bestand des Paares gesucht.
    Nachbedingung: Hoechstens `DATEIEN_SUCHE_KAPPUNG` Zeilen, jede mit
    `kanal = "vektor"` und `kosinus`.
    Fehlerfaelle: wie oben.

    **Der Unterschied zwischen `None` und `[]` ist die ganze Regel aus §6.3.**
    `None` heisst "es gab keine scharfe Einschraenkung" — dann ordnet der
    Vektor den ganzen Bestand. Eine **leere Liste** heisst "die scharfe Suche
    lief und fand nichts"; dann gibt es nichts zu ordnen, und der Vektor darf
    die Einschraenkung nicht stillschweigend aufheben.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not such_vektor:
        logger.debug("Dateien-Suche: kein Suchschluessel — keine Vektorabfrage")
        return []
    if not _paar_pruefen(user_id, character_id):
        return []
    if kandidaten_ids is not None and not kandidaten_ids:
        logger.info(
            "Dateien-Suche: die scharfe Suche lief und fand nichts — der Vektor "
            "hebt das nicht auf"
        )
        return []

    # ── Verarbeitung ────────────────────────────
    vektor_str: str = embedding_zu_pgvector_str(such_vektor)
    einschraenkung: str = " AND i.id = ANY(%s)" if kandidaten_ids else ""

    # Die Reihenfolge der Platzhalter, ausgeschrieben statt gerechnet: Kosinus
    # im SELECT, das Paar, optional die Kandidaten, Kosinus im ORDER BY, Kappung.
    parameter: list = [vektor_str, user_id, character_id]
    if kandidaten_ids:
        parameter.append(kandidaten_ids)
    parameter.extend([vektor_str, DATEIEN_SUCHE_KAPPUNG])

    try:
        zeilen: list[dict] = db_manager.select(
            f"SELECT {_SPALTEN}, 1 - (i.themen_embedding <=> %s::vector) AS kosinus "
            f"{_VON} AND i.themen_embedding IS NOT NULL{einschraenkung} "
            f"ORDER BY i.themen_embedding <=> %s::vector LIMIT %s",
            tuple(parameter),
        )
    except Exception as fehler:
        logger.exception(
            "%s: Dateien-Suche ueber den Vektor fehlgeschlagen", type(fehler).__name__,
        )
        return []

    # ── Ausgabe-Verifikation ────────────────────
    for zeile in zeilen:
        zeile["kanal"] = KANAL_VEKTOR
        zeile["kosinus"] = round(float(zeile.get("kosinus") or 0.0), 4)
    logger.info(
        "Dateien-Suche: Vektor über %s → %d Treffer",
        "Kandidaten" if kandidaten_ids else "den ganzen Bestand", len(zeilen),
    )
    return zeilen


def kandidaten_finden(
    user_id: str, character_id: str, muster: str, woerter: list[str],
    such_vektor: list[float],
) -> list[dict]:
    """Die Reihenfolge aus §6.3, in einem Aufruf: scharf, dann unscharf.

    Vorbedingung: Mindestens eine der drei Eingaben trägt etwas.
    Nachbedingung: Höchstens `DATEIEN_SUCHE_KAPPUNG` Kandidaten. Jeder trägt
    seinen `kanal`; die Liste ist leer, wenn kein Kanal etwas fand.
    Fehlerfaelle: keine eigenen — die drei Kanäle melden selbst.

    **Der erste Kanal, der etwas findet, gewinnt.** Ein Name ist schärfer als
    ein Stichwort, ein Stichwort schärfer als ein Vektor; wer alle drei mischt,
    bekommt eine Rangfolge aus drei Skalen. Der Vektor ordnet danach **innerhalb**
    des Gefundenen, wenn ein schärferer Kanal mehr als einen Treffer lieferte.
    """
    # ── Verarbeitung ────────────────────────────
    if muster.strip():
        treffer: list[dict] = nach_name(user_id, character_id, muster)
        if treffer:
            return _innerhalb_ordnen(user_id, character_id, treffer, such_vektor)

    if [w for w in woerter if w.strip()]:
        treffer = nach_stichwort(user_id, character_id, woerter)
        if treffer:
            return _innerhalb_ordnen(user_id, character_id, treffer, such_vektor)

    # ── Ausgabe ─────────────────────────────────
    # Kein scharfer Kanal hat gegriffen — jetzt darf der Vektor über den
    # ganzen Bestand, denn es gab keine Einschränkung, die er aufheben könnte.
    return nach_vektor(user_id, character_id, such_vektor, kandidaten_ids=None)


def _innerhalb_ordnen(
    user_id: str, character_id: str, treffer: list[dict], such_vektor: list[float],
) -> list[dict]:
    """Ordnet eine gefundene Kandidatenmenge nach Nähe — ohne sie zu erweitern.

    Vorbedingung: `treffer` ist nicht leer.
    Nachbedingung: Dieselbe Menge, semantisch geordnet — oder die
    Eingangsmenge unverändert, wenn kein Suchschlüssel vorliegt oder die
    Ordnung ausfällt. **Nie eine andere Menge**: Der Vektor ordnet hier, er
    wählt nicht aus.
    """
    # ── Eingabe-Validierung ─────────────────────
    if len(treffer) < 2 or not such_vektor:
        return treffer

    # ── Verarbeitung ────────────────────────────
    ids: list[int] = [int(t["id"]) for t in treffer]
    geordnet: list[dict] = nach_vektor(user_id, character_id, such_vektor, ids)

    # ── Ausgabe-Verifikation ────────────────────
    if len(geordnet) != len(treffer):
        # Der Vektorkanal hat Zeilen verloren — etwa weil eine Einbettung
        # fehlt. Die scharfe Menge bleibt maßgeblich; sonst verschwände ein
        # Treffer, weil ihm ein Vektor fehlt, und niemand sähe es.
        logger.warning(
            "Dateien-Suche: Ordnung lieferte %d von %d Kandidaten — die scharfe "
            "Menge bleibt maßgeblich",
            len(geordnet), len(treffer),
        )
        return treffer

    # Den scharfen Kanal behalten: Er sagt, WARUM die Datei im Rennen ist.
    # Geprueft gelesen, nicht blind: Jeder Kanal setzt ihn vor der Rueckgabe,
    # und fehlt er doch, ist das ein Defekt am liefernden Kanal — er gehoert
    # gemeldet und nicht in einen KeyError mitten in der Ordnung.
    kanal: str = treffer[0].get("kanal", "")
    if kanal not in KANAELE:
        logger.error(
            "Dateien-Suche: Kandidat ohne gueltigen Kanal (%r) — die Ordnung "
            "laeuft, aber die Herkunft des Treffers ist verloren",
            kanal,
        )
        return geordnet

    for zeile in geordnet:
        zeile["kanal"] = kanal
    return geordnet
