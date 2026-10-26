"""Der Kanon der Beziehungen, die der Fakten-Agent schreibt.

Je Beziehung steht fest, ob sie höchstens einen aktiven Wert hat (einwertig:
ein neuer Wohnort löst den alten ab) oder mehrere (mehrwertig: ein zweites
Haustier kommt hinzu), ob ihr Objekt eine eigene Entität ist oder ein Wert,
welchen Typ eine neu angelegte Objekt-Entität bekommt und welche Typen ihr
Subjekt haben darf.

**Das Subjekt ist eine Person, wo nichts anderes steht.** Einen Namen trägt
jede Entität (`heisst`), einen Wohn- und Geburtsort auch ein Tier. `sonstiges`
steht in keiner Menge: Ein Subjekt, dessen Typ das Modell nicht einordnet,
lässt die Prüfung des Tripels gesondert durch.

**Alles Unentschiedene ist mehrwertig.** Eine mehrwertige Beziehung, die in
Wahrheit einwertig ist, lässt einen alten Wert neben dem neuen stehen — das ist
sichtbar und korrigierbar. Eine einwertige, die in Wahrheit mehrwertig ist,
löst einen richtigen Wert still ab.

**Die Schreibweise ist klein mit Unterstrich** (`wohnt_in`), wie die
bestehenden Zeilen in `fakten`. Eine zweite Schreibweise derselben Kante
(`WOHNT_IN`) ergäbe zwei Beziehungen, und weder *identisch* noch die Ablösung
fänden den alten Wert.
"""

from dataclasses import dataclass

# Typ einer neuen Objekt-Entität, wenn der Kanon keinen nennt — derselbe Wert,
# den die Datenbank als Vorgabe von `entitaeten.typ` führt.
TYP_SONSTIGES: str = "sonstiges"
TYP_PERSON:    str = "person"
TYP_TIER:      str = "tier"

# Die Typen einer Entität, klein geschrieben wie `objekt_typ`. Die Reihenfolge
# ist die des Prompts der Klassifikation, der sie dem Modell zur Wahl stellt.
ENTITY_TYPES: tuple[str, ...] = (
    TYP_PERSON, "ort", "organisation", TYP_TIER, "objekt", TYP_SONSTIGES,
)

if len(set(ENTITY_TYPES)) != len(ENTITY_TYPES):
    raise ValueError(f"Typen: doppelter Wert in {ENTITY_TYPES}")  # noqa: TRY003


@dataclass(frozen=True)
class Relation:
    """Eine Beziehung des Kanons.

    `objekt_typ` ist der Typ einer neu angelegten Objekt-Entität und leer, wenn
    das Objekt ein Wert ist. `subjekt_typen` sind die Typen, die das Subjekt
    haben darf, ohne `sonstiges`.
    """

    attribut:            str
    einwertig:           bool
    objekt_ist_entitaet: bool
    objekt_typ:          str
    subjekt_typen:       frozenset[str]

    def __post_init__(self) -> None:
        """Weist eine in sich widersprüchliche Beziehung ab.

        Vorbedingung: keine.
        Nachbedingung: Das Attribut ist klein geschrieben und ohne Leerzeichen;
            eine Objekt-Entität hat einen Typ, ein Wert keinen; die Typen des
            Subjekts sind nicht leer, stehen in `ENTITY_TYPES` und enthalten
            `sonstiges` nicht.
        Fehlerfälle: ValueError sonst — der Kanon ist dann beim Import defekt.
        """
        # ── Eingabe-Validierung ─────────────────────
        if not self.attribut or self.attribut != self.attribut.lower() or " " in self.attribut:
            raise ValueError(f"Beziehung: Schreibweise {self.attribut!r} nicht im Kanon")
        if self.objekt_ist_entitaet != bool(self.objekt_typ):
            raise ValueError(
                f"Beziehung {self.attribut!r}: objekt_ist_entitaet={self.objekt_ist_entitaet} "
                f"passt nicht zu objekt_typ={self.objekt_typ!r}"
            )
        fremd: set[str] = set(self.subjekt_typen) - (set(ENTITY_TYPES) - {TYP_SONSTIGES})
        if not self.subjekt_typen or fremd:
            raise ValueError(  # noqa: TRY003
                f"Beziehung {self.attribut!r}: Typen des Subjekts "
                f"{sorted(self.subjekt_typen)} leer oder ausserhalb der Liste: {sorted(fremd)}"
            )


# Beziehung -> Typ einer neuen Objekt-Entität. Startbestand aus der Zuordnung
# des bisherigen Schreibers, ohne die Beziehung "ist ein".
_ENTITAETS_OBJEKTE: dict[str, str] = {
    "wohnt_in":      "ort",
    "arbeitet_in":   "ort",
    "geboren_in":    "ort",
    "heimat":        "ort",
    "hat_schwester": "person",
    "hat_bruder":    "person",
    "hat_mutter":    "person",
    "hat_vater":     "person",
    "hat_partner":   "person",
    "hat_tochter":   "person",
    "hat_sohn":      "person",
    "hat_nachbar":   "person",
    "hat_freund":    "person",
    "hat_freundin":  "person",
    "hat_ehemann":   "person",
    "hat_ehefrau":   "person",
    "hat_kollege":   "person",
    "hat_kollegin":  "person",
    "hat_chef":      "person",
    "hat_haustier":  "tier",
}

# Beziehungen, deren Objekt ein Wert ist und keine Entität.
_WERT_OBJEKTE: frozenset[str] = frozenset({"heisst", "arbeitet_als", "hat_hobby"})

# Einwertig: Wohnort, Beruf, Partner, Mutter, Vater, Ehemann, Ehefrau,
# Geburtsort, Name. Alles andere ist mehrwertig.
_EINWERTIG: frozenset[str] = frozenset({
    "wohnt_in", "arbeitet_als", "hat_partner", "hat_mutter", "hat_vater",
    "hat_ehemann", "hat_ehefrau", "geboren_in", "heisst",
})

# Beziehungen, deren Subjekt jeden Typ haben darf: Einen Namen trägt jede Entität.
_SUBJEKT_JEDER_TYP: frozenset[str] = frozenset({"heisst"})
# Beziehungen, deren Subjekt auch ein Tier sein darf: Ein Tier wohnt und ist geboren.
_SUBJEKT_AUCH_TIER: frozenset[str] = frozenset({"wohnt_in", "geboren_in"})


def _subject_types(attribut: str) -> frozenset[str]:
    """Die Typen, die das Subjekt einer Beziehung haben darf.

    Vorbedingung: `attribut` ist eine Beziehung des Kanons in seiner Schreibweise.
    Nachbedingung: alle Typen außer `sonstiges` für `_SUBJEKT_JEDER_TYP`,
        Person und Tier für `_SUBJEKT_AUCH_TIER`, sonst nur Person.
    Fehlerfälle: keine; was die Menge verfehlt, weist `Relation` beim Import ab.
    """
    # ── Verarbeitung ────────────────────────────
    if attribut in _SUBJEKT_JEDER_TYP:
        return frozenset(ENTITY_TYPES) - {TYP_SONSTIGES}
    if attribut in _SUBJEKT_AUCH_TIER:
        return frozenset({TYP_PERSON, TYP_TIER})
    return frozenset({TYP_PERSON})


KANON: dict[str, Relation] = {
    attribut: Relation(
        attribut=attribut,
        einwertig=attribut in _EINWERTIG,
        objekt_ist_entitaet=attribut in _ENTITAETS_OBJEKTE,
        objekt_typ=_ENTITAETS_OBJEKTE.get(attribut, ""),
        subjekt_typen=_subject_types(attribut),
    )
    for attribut in sorted(set(_ENTITAETS_OBJEKTE) | _WERT_OBJEKTE)
}

if not _EINWERTIG <= set(KANON):
    raise ValueError(f"Kanon: einwertig ohne Beziehung {sorted(_EINWERTIG - set(KANON))}")
if not _SUBJEKT_JEDER_TYP | _SUBJEKT_AUCH_TIER <= set(KANON):
    raise ValueError(  # noqa: TRY003
        f"Kanon: Typen des Subjekts ohne Beziehung "
        f"{sorted((_SUBJEKT_JEDER_TYP | _SUBJEKT_AUCH_TIER) - set(KANON))}"
    )


def find_relation(attribut: str) -> Relation | None:
    """Findet eine Beziehung des Kanons.

    Vorbedingung: keine — die Eingabe stammt aus der Antwort des Modells.
    Nachbedingung: die Beziehung, wenn `attribut` nach Rand und Groß- und
        Kleinschreibung im Kanon steht, sonst None.
    Fehlerfälle: keine; None heißt *nicht im Kanon*, und das entscheidet der
        Aufrufer als Ablehnung.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(attribut, str):
        return None

    # ── Verarbeitung ────────────────────────────
    beziehung: Relation | None = KANON.get(attribut.strip().lower())

    # ── Ausgabe-Verifikation ────────────────────
    if beziehung is not None and beziehung.attribut != attribut.strip().lower():
        raise RuntimeError(f"Kanon: {attribut!r} lieferte {beziehung.attribut!r}")
    return beziehung
