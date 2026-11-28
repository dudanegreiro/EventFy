from datetime import datetime, timedelta


LEGACY_EXPIRATION_HOURS = 48


def reservation_expiration_deadline(
    entered_at: datetime,
    configured_hours: int = LEGACY_EXPIRATION_HOURS,
) -> datetime:
    """Return the deadline without exposing expiration policy to callers."""
    if configured_hours < 1:
        raise ValueError("configured_hours must be positive")
    return entered_at + timedelta(hours=configured_hours)
