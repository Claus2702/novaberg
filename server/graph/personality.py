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


@dataclass
class Personality:
    """Vollständige Personality-Repräsentation für einen Akteur.

    Bündelt das statische Character-Profil mit der dynamischen
    Emotion-Schicht zu einem einzigen Container.
    """

    character: Character = field(default_factory=Character)
    emotion: Emotion     = field(default_factory=Emotion)


@dataclass
class InternalPersonality(Personality):
    """Personality mit Handlungsanweisungen — nur für Nova.

    identities: Charakter-Identitäten aus der Tabelle
                ``charakter_anweisungen`` (Liste von Anweisungs-Strings).
    directives: Direktiven aus der Tabelle ``direktiven``
                (Liste von Dicts mit ``anweisung`` und ``kontext``).
    """

    identities: list[str]  = field(default_factory=list)
    directives: list[dict] = field(default_factory=list)
