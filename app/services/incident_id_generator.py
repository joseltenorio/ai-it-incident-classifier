# app/services/incident_id_generator.py

from datetime import UTC, datetime
from uuid import uuid4


def generate_incident_id(created_at: datetime | None = None) -> str:
    """Generate a stable incident identifier for classified tickets.

    The identifier includes the current date for readability and a short UUID
    suffix to avoid requiring a database counter during local or cloud runtime.
    """

    timestamp = created_at or datetime.now(UTC)
    date_part = timestamp.strftime("%Y%m%d")
    random_part = uuid4().hex[:8].upper()

    return f"INC-{date_part}-{random_part}"