"""TimeParser — Proxy auf den bestehenden Zeitparser in utils/zeitparser.py.

Der eigentliche Parser lebt in utils/zeitparser.py. Dieser Proxy stellt
die gleiche API unter tools/ bereit. In Phase 2 wird der Parser hierher
migriert, wenn der TimelineManager zum TimelineAgent wird.
"""

# Re-Export aus dem bestehenden Code
from utils.zeitparser import zeit_parsen, zeit_parsen_vektor, ZeitVektor

__all__ = ["zeit_parsen", "zeit_parsen_vektor", "ZeitVektor"]
