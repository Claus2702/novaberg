"""Personality-Klassen für den CharacterGraph.

Trennt den Zustand zweier Akteure im Gespräch:
- external: Personality — das Gegenüber (User, oder bei Pixie: Nova selbst).
- internal: InternalPersonality — Nova.

Jede Personality kombiniert einen statischen Character-Hash (fünf
destillierte Identitäts-Schichten) mit einer dynamischen Emotion
(neun Dimensionen pro Turn).

InternalPersonality ergänzt zwei Listen für Handlungsanweisungen,
die nur Nova trägt: explizite Charakter-Identitäten (vom
CharakterIdentitaetAgent) und Direktiven (vom DirektivenAgent).

Siehe docs/novaberg-path2-perzeption_k.md §3.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Character:
    """Fünf destillierte Identitäts-Schichten aus der Tabelle ``charakter_hash``.

    Felder spiegeln die DB-Spalten:
        core         <- kern_hash          (Kern-Persönlichkeit)
        adaptive     <- adaptive_hash      (aktuelle Anpassungs-Phase)
        relationship <- beziehungsprofil   (Beziehungs-Profil)
        intentions   <- intentions_profil  (Intentions-/Kommunikations-Profil)
        emotions     <- emotions_profil    (emotionales Grund-Profil, statisch)
    """

    core: str         = ""
    adaptive: str     = ""
    relationship: str = ""
    intentions: str   = ""
    emotions: str     = ""


@dataclass
class Emotion:
    """Neun dynamische EI-Dimensionen pro Turn.

    Defaults greifen beim Cold-Start (erster Turn pro User-Charakter-Paar,
    wenn noch kein persistierter Nova-State existiert).
    """

    emotion: str              = "neutral"
    arousal: float            = 0.5
    emotions_vector: str      = ""
    mode: str                 = "alltag"
    language_style: str       = "neutral"
    relationship_dynamic: str = "neutral"
    tone: str                 = "sachlich"
    intent: str               = "smalltalk"
    prompt_topic: str         = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialisiert alle neun EI-Dimensionen in ein dict.

        Explizite Feld-Abbildung (kein dataclasses.asdict) — ein neu
        hinzugefuegtes Emotion-Feld landet nur dann im Serialisat, wenn
        es hier bewusst ergaenzt wird. Verhindert unbeabsichtigtes Lecken
        interner Felder in dauerhafte Speicher (z.B. turn_roh).
        """
        return {
            "emotion":              self.emotion,
            "arousal":              self.arousal,
            "emotions_vector":      self.emotions_vector,
            "mode":                 self.mode,
            "language_style":       self.language_style,
            "relationship_dynamic": self.relationship_dynamic,
            "tone":                 self.tone,
            "intent":               self.intent,
            "prompt_topic":         self.prompt_topic,
        }


@dataclass
class Personality:
    """Vollständige Personality-Repräsentation für einen Akteur.

    Bündelt das statische Character-Profil mit der dynamischen
    Emotion-Schicht zu einem einzigen Container.
    """

    character: Character = field(default_factory=Character)
    emotion: Emotion     = field(default_factory=Emotion)


@dataclass
class Raum:
    """Novas Gesprächsraum — wo sie im Register steht, als Zahl.

    Es gibt nur einen Raum, und es ist ihrer. Der Raum des Nutzers lebt in
    seinem Kopf; was die Perzeption liefert, ist eine Schätzung davon und
    ein Ziel, zu dem Novas Raum gezogen wird (``ei/raum.py``).

    Warum Zahlen und nicht die Labels aus ``Emotion``: Zwischen
    ``fachgespraech`` und ``alltag`` gibt es kein Label, aber einen
    Zwischenzustand — und genau der ist ein Registerwechsel, der ein bis
    drei Turns dauert. Die Labels beschreiben je eine Äußerung, der Raum
    ist der Zustand dazwischen.

    Beide Werte liegen auf den Achsen aus ``novaberg-gv-strategie_k.md`` §3.1
    und werden mit denselben Schwellen binarisiert wie zuvor die Label-Werte.
    """

    tiefe: float = 0.3
    # Gesprächsebene, 0.0 flach bis 1.0 existenziell. Skala und Anker:
    # GV_TIEFE_MODUS. Default = Wert von "alltag" (Cold-Start).

    naehe: float = 0.5
    # Beziehungsdichte, 0.0 fern bis 1.0 intim. Skala: Mittel aus
    # GV_NAEHE_DYNAMIK und GV_NAEHE_STIL. Default = neutral/neutral.


@dataclass
class InternalPersonality(Personality):
    """Personality mit Handlungsanweisungen — nur für Nova.

    identities: Charakter-Identitäten aus der Tabelle
                ``charakter_anweisungen`` (Liste von Anweisungs-Strings).
    directives: Direktiven aus der Tabelle ``direktiven``
                (Liste von Dicts mit ``anweisung`` und ``kontext``).
    raum:       Novas Gesprächsraum (Tiefe, Nähe) — überlebt den Turn in
                ``redis:nova_state``, wird bei Nutzer-Turns zum geschätzten
                Raum des Nutzers gezogen.
    """

    identities: list[str]  = field(default_factory=list)
    directives: list[dict] = field(default_factory=list)
    raum: Raum             = field(default_factory=Raum)
