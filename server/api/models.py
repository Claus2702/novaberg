"""
API-Datenmodelle — Pydantic-Schemas für Request/Response.
"""

from config     import ASSISTANT_NAME
from pydantic   import BaseModel, Field


class GespraechAnfrage(BaseModel):
    """Eingehende Chat-Nachricht."""
    prompt:     str   = Field(..., min_length=1, description="Benutzereingabe")
    user_id:    str   = Field(default="default",  description="Benutzer-ID")
    system: str = Field(
        default=(
            f"Du bist {ASSISTANT_NAME}. Antworte auf deutsch."
        ),
        description="System-Prompt"
    )
    temperatur: float = Field(default=0.7, ge=0.0, le=2.0, description="Kreativität")


class GespraechAntwort(BaseModel):
    """Antwort vom LLM."""
    antwort:     str
    modell:      str
    token_total: int

    # Emotionale Intelligenz
    emotion:          str            = ""
    arousal:          float          = 0.0
    emotions_vektor:  str            = ""
    emotions_verlauf: list[dict]     = []
    sprach_stil:      str            = ""
    beziehungs_dynamik: str          = ""

    # Perzeption & Routing
    intent:           str            = ""
    tone:             str            = ""
    gespraechs_modus: str            = ""
    user_intentionen: list[str]      = []
    momentum:         str            = ""
    needs_web:        bool           = False
