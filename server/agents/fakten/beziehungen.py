"""Der Kanon der Beziehungen, die der Fakten-Agent schreibt.

Je Beziehung steht fest, ob sie höchstens einen aktiven Wert hat (einwertig:
ein neuer Wohnort löst den alten ab) oder mehrere (mehrwertig: ein zweites
Haustier kommt hinzu), ob ihr Objekt eine eigene Entität ist oder ein Wert, und
welchen Typ eine neu angelegte Objekt-Entität bekommt.

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


@dataclass(frozen=True)
class Relation:
    """Eine Beziehung des Kanons.

    `objekt_typ` ist der Typ einer neu angelegten Objekt-Entität und leer, wenn
    das Objekt ein Wert ist.
    """

    attribut:            str
    einwertig:           bool
    objekt_ist_entitaet: bool
    objekt_typ:          str

    def __post_init__(self) -> None:
        """Weist eine in sich widersprüchliche Beziehung ab.

        Vorbedingung: keine.
        Nachbedingung: Das Attribut ist klein geschrieben und ohne Leerzeichen;
            eine Objekt-Entität hat einen Typ, ein Wert keinen.
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

KANON: dict[str, Relation] = {
    attribut: Relation(
        attribut=attribut,
        einwertig=attribut in _EINWERTIG,
        objekt_ist_entitaet=attribut in _ENTITAETS_OBJEKTE,
        objekt_typ=_ENTITAETS_OBJEKTE.get(attribut, ""),
    )
    for attribut in sorted(set(_ENTITAETS_OBJEKTE) | _WERT_OBJEKTE)
}

if not _EINWERTIG <= set(KANON):
    raise ValueError(f"Kanon: einwertig ohne Beziehung {sorted(_EINWERTIG - set(KANON))}")


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
