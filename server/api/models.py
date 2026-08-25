"""API-Datenmodelle — Pydantic-Schemas für Request/Response."""

from pydantic import BaseModel, Field

from config import ASSISTANT_NAME


class GespraechAnfrage(BaseModel):
    """Eingehende Chat-Nachricht."""

    prompt:     str   = Field(..., min_length=1, description="Benutzereingabe")
    user_id:    str   = Field(default="default",  description="Benutzer-ID")
    client_id: str = Field(default="", description="Absender-Client (z.B. desktop, telegram)")
    system: str = Field(
        default=(
            f"Du bist {ASSISTANT_NAME}. Antworte auf deutsch."
        ),
        description="System-Prompt"
    )
    temperatur: float = Field(default=0.7, ge=0.0, le=2.0, description="Kreativität")
