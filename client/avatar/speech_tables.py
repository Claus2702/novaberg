"""Lauttabellen des Sprechens: Lautklassen, deutsche Laute auf Mundkanäle, Zunge.

Die Kanäle stehen in der Reihenfolge `SPEECH_KEYS` des Prototyps: Öffnung (`mo`)
und Kiefer (`jaw`) in Pixeln, die Muskelkanäle nach FACS in 0..1 — `up` hebt die
Oberlippe (AU10), `lo` senkt die Unterlippe (AU16), `str` zieht breit (AU20), `pk`
spitzt (AU18), `fn` trichtert (AU22), `press` presst (AU24), `fv` zieht die
Unterlippe unter die Zähne (AU28) —, dazu die Zungenhöhe `tng` (0 = Mundboden,
1 = Spitze am Gaumen).

Die Werte sind nach phonetischer Literatur gesetzt; Öffnung und Breite der Vokale
a:, E, E:, O und 6 sind an Videoaufnahmen kalibriert. Die Koartikulation folgt dem
Dominanzmodell nach Cohen und Massaro (1993): Jeder Laut hat je Kanal eine Dominanz
und eine zeitliche Reichweite in Millisekunden.
"""

from dataclasses import dataclass
from types import MappingProxyType

TABLE_KEYS: tuple[str, ...] = ("mo", "jaw", "up", "lo", "str", "pk", "fn", "press", "fv")
SPEECH_KEYS: tuple[str, ...] = (*TABLE_KEYS, "tng")


@dataclass(frozen=True)
class PhoneClass:
    """Eine Lautklasse: Dominanz je Tabellenkanal, Reichweite und Grunddauer in ms."""

    dominance: tuple[float, ...]
    reach_ms: float
    duration_ms: float


@dataclass(frozen=True)
class Phoneme:
    """Ein Laut: Zielwert und Dominanz je Kanal in der Reihenfolge `SPEECH_KEYS`."""

    code: str
    phone_class: str
    values: tuple[float, ...]
    dominance: tuple[float, ...]
    reach_ms: float


# Lautklassen. Spalten: Dominanz für mo jaw up lo str pk fn press fv, Reichweite, Grunddauer.
#   rest  Pause                         vL    langer Vokal
#   vS    kurzer Vokal                  vR    Schwa, vokalisiertes r
#   bil   p b m: Lippen schließen       lab   f v: Unterlippe an Oberzähne
#   sib   s z ç j: Zähne eng, breit     post  sch: Lippen vorgestülpt
#   alv   t d n l: Zunge, Lippen frei   vel   k g ng r ach: hinten, Lippen frei
#   h     übernimmt den Folgevokal
_CLASS_ROWS: dict[str, tuple[tuple[float, ...], float, float]] = {
    "rest": ((0.5, 0.5, 0.3, 0.3, 0.3, 0.3, 0.3, 0.2, 0.2), 140, 300),
    "vL": ((1, 1, 0.6, 0.6, 0.8, 1, 1, 0.3, 0.3), 130, 165),
    "vS": ((1, 1, 0.6, 0.6, 0.8, 1, 1, 0.3, 0.3), 100, 100),
    "vR": ((0.6, 0.6, 0.3, 0.3, 0.3, 0.3, 0.3, 0.2, 0.2), 70, 70),
    "bil": ((0.9, 0.4, 0.3, 0.3, 0.2, 0.1, 0.1, 1, 0.1), 60, 75),
    "lab": ((0.7, 0.3, 0.6, 0.3, 0.2, 0.1, 0.1, 0.1, 1), 60, 85),
    "sib": ((0.4, 0.6, 0.5, 0.2, 0.4, 0.05, 0.05, 0.1, 0.1), 55, 90),
    "post": ((0.5, 0.5, 0.4, 0.2, 0.3, 0.8, 0.8, 0.1, 0.1), 70, 95),
    "alv": ((0.3, 0.4, 0.15, 0.2, 0.1, 0.05, 0.05, 0.1, 0.1), 50, 65),
    "vel": ((0.2, 0.2, 0.1, 0.2, 0.1, 0.05, 0.05, 0.1, 0.1), 50, 70),
    "h": ((0.05, 0.05, 0.05, 0.05, 0.05, 0.02, 0.02, 0.05, 0.05), 40, 60),
}

PHONE_CLASSES: MappingProxyType[str, PhoneClass] = MappingProxyType({
    name: PhoneClass(dominance, reach, duration)
    for name, (dominance, reach, duration) in _CLASS_ROWS.items()
})

# Deutsche Laute (SAMPA-Kürzel). Spalten: mo jaw up lo str pk fn press fv, Klasse.
_PHONEME_ROWS: dict[str, tuple[tuple[float, ...], str]] = {
    "REST": ((0, 0, 0, 0, 0, 0, 0, 0, 0), "rest"),
    "a:": ((42, 33, 0, 0.3, 0, 0, 0, 0, 0), "vL"),  # Vater
    "a": ((40, 28, 0, 0.25, 0, 0, 0, 0, 0), "vS"),  # Mann
    "e:": ((22, 13, 0.25, 0.1, 0.35, 0, 0, 0, 0), "vL"),  # Beet
    "E": ((26, 22, 0.15, 0.15, 0.2, 0, 0, 0, 0), "vS"),  # Bett, Äpfel
    "E:": ((28, 24, 0.15, 0.15, 0.2, 0, 0, 0, 0), "vL"),  # Käse
    "i:": ((17, 7, 0.3, 0.1, 0.5, 0, 0, 0, 0), "vL"),  # Biene
    "I": ((17, 10, 0.25, 0.1, 0.35, 0, 0, 0, 0), "vS"),  # ich
    "o:": ((26, 18, 0, 0, 0, 0.4, 0.8, 0, 0), "vL"),  # Sohn
    "O": ((27, 26, 0, 0.1, 0, 0.2, 0.7, 0, 0), "vS"),  # Sonne
    "u:": ((17, 10, 0, 0, 0, 0.8, 0.3, 0, 0), "vL"),  # gut
    "U": ((18, 13, 0, 0, 0, 0.65, 0.35, 0, 0), "vS"),  # Mutter
    "y:": ((16, 8, 0.1, 0, 0, 0.75, 0.2, 0, 0), "vL"),  # müde
    "Y": ((19, 10, 0.1, 0, 0, 0.75, 0.2, 0, 0), "vS"),  # Hütte
    "2:": ((20, 14, 0, 0, 0, 0.7, 0.5, 0, 0), "vL"),  # schön
    "9": ((28, 20, 0, 0.05, 0, 0.45, 0.55, 0, 0), "vS"),  # können
    "@": ((18, 12, 0, 0.1, 0, 0, 0, 0, 0), "vR"),  # bitte (Schwa)
    "6": ((22, 20, 0, 0.15, 0, 0, 0, 0, 0), "vR"),  # Mutter, hier (vokalisiertes r)
    "p": ((0, 2, 0, 0, 0, 0, 0, 1, 0), "bil"),
    "b": ((0, 2, 0, 0, 0, 0, 0, 1, 0), "bil"),
    "m": ((0, 2, 0, 0, 0, 0, 0, 1, 0), "bil"),
    "f": ((6, 2, 0.3, 0, 0, 0, 0, 0, 1), "lab"),
    "v": ((6, 2, 0.3, 0, 0, 0, 0, 0, 1), "lab"),
    "s": ((7, 4, 0.25, 0.05, 0.2, 0, 0, 0, 0), "sib"),
    "z": ((7, 4, 0.25, 0.05, 0.2, 0, 0, 0, 0), "sib"),
    "C": ((10, 5, 0.2, 0, 0.25, 0, 0, 0, 0), "sib"),  # ich-Laut
    "j": ((10, 6, 0.2, 0, 0.25, 0, 0, 0, 0), "sib"),
    "S": ((12, 5, 0.2, 0, 0, 0.4, 0.8, 0, 0), "post"),  # sch
    "Z": ((12, 5, 0.2, 0, 0, 0.4, 0.8, 0, 0), "post"),  # Garage
    "t": ((10, 6, 0.1, 0, 0.1, 0, 0, 0, 0), "alv"),
    "d": ((10, 6, 0.1, 0, 0.1, 0, 0, 0, 0), "alv"),
    "n": ((10, 6, 0.1, 0, 0.1, 0, 0, 0, 0), "alv"),
    "l": ((18, 11, 0, 0.1, 0, 0, 0, 0, 0), "alv"),
    "k": ((14, 9, 0, 0, 0, 0, 0, 0, 0), "vel"),
    "g": ((14, 9, 0, 0, 0, 0, 0, 0, 0), "vel"),
    "N": ((14, 9, 0, 0, 0, 0, 0, 0, 0), "vel"),  # ng
    "R": ((16, 10, 0, 0, 0, 0, 0, 0, 0), "vel"),  # Zäpfchen-r
    "x": ((20, 13, 0, 0.1, 0, 0, 0, 0, 0), "vel"),  # ach-Laut
    "h": ((22, 14, 0, 0.1, 0, 0, 0, 0, 0), "h"),
}

# Zunge nur als Andeutung im Mundraum. L und R am stärksten, t/d/n Spitze am Zahndamm,
# s/z, ich-Laut und j heben den Zungenrücken leicht; alle anderen Laute: Mundboden.
_TONGUE_UP: dict[str, float] = {
    "l": 1, "R": 1, "t": 0.6, "d": 0.6, "n": 0.6,
    "s": 0.35, "z": 0.35, "C": 0.45, "j": 0.5, "S": 0.3, "Z": 0.3,
}
# Wo die Zunge den Laut bildet, setzt sie sich durch; bei Vokalen und Lippenlauten folgt
# sie den Nachbarn. Vokale binden die Zungenspitze kaum, damit sie bei L den Gaumen erreicht.
_TONGUE_DOMINANCE_BY_CLASS: dict[str, float] = {
    "rest": 0.5, "vL": 0.15, "vS": 0.15, "vR": 0.1, "bil": 0.1, "lab": 0.1,
    "sib": 0.6, "post": 0.5, "alv": 0.9, "vel": 0.3, "h": 0.05,
}
_TONGUE_DOMINANCE_BY_PHONEME: dict[str, float] = {"R": 0.9}


def _build_phonemes() -> dict[str, Phoneme]:
    """Je Laut die Kanalwerte samt Zunge und die Dominanzzeile samt Zunge."""
    # ── Eingabe-Validierung ──
    unknown = sorted({cls for _, cls in _PHONEME_ROWS.values()} - set(PHONE_CLASSES))
    if unknown:
        raise RuntimeError(f"Lauttabelle: unbekannte Lautklassen {unknown}")
    short_rows = [code for code, (row, _) in _PHONEME_ROWS.items() if len(row) != len(TABLE_KEYS)]
    if short_rows:
        raise RuntimeError(f"Lauttabelle: Zeilen ohne {len(TABLE_KEYS)} Kanäle: {short_rows}")

    # ── Verarbeitung ──
    phonemes = {}
    for code, (row, cls) in _PHONEME_ROWS.items():
        phone_class = PHONE_CLASSES[cls]
        tongue_dominance = _TONGUE_DOMINANCE_BY_PHONEME.get(code, _TONGUE_DOMINANCE_BY_CLASS[cls])
        phonemes[code] = Phoneme(
            code=code,
            phone_class=cls,
            values=(*(float(v) for v in row), float(_TONGUE_UP.get(code, 0))),
            dominance=(*(float(d) for d in phone_class.dominance), float(tongue_dominance)),
            reach_ms=float(phone_class.reach_ms),
        )

    # ── Ausgabe-Verifikation ──
    unused_tongue = sorted(set(_TONGUE_UP) - set(phonemes))
    if unused_tongue:
        raise RuntimeError(f"Zungentabelle: Laute ohne Zeile in der Lauttabelle: {unused_tongue}")
    width = len(SPEECH_KEYS)
    if any(len(p.values) != width or len(p.dominance) != width for p in phonemes.values()):
        raise RuntimeError("Lauttabelle: Laut ohne Wert oder Dominanz je Sprechkanal")
    return phonemes


PHONEMES: MappingProxyType[str, Phoneme] = MappingProxyType(_build_phonemes())
VOWEL_CODES: frozenset[str] = frozenset(
    code for code, phoneme in PHONEMES.items() if phoneme.phone_class.startswith("v")
)
BILABIAL_CODES: frozenset[str] = frozenset({"p", "b", "m"})
