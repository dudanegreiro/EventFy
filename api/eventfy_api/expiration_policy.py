from datetime import datetime, timedelta


LEGACY_EXPIRATION_HOURS = 48


def reservation_expiration_deadline(
    entered_at: datetime,
    configured_hours: int = LEGACY_EXPIRATION_HOURS,
    *,
    contract_created_at: datetime | None = None,
    effective_at: datetime | None = None,
) -> datetime:
    """Return the deadline without exposing expiration policy to callers."""
    if configured_hours < 1:
        raise ValueError("configured_hours must be positive")
    # Keep existing contracts on the historical SLA; opt new contracts in at
    # an explicit UTC cutover so a deployment never silently changes deadlines.
    hours = configured_hours
    if (
        effective_at is None
        or contract_created_at is None
        or contract_created_at < effective_at
    ):
        hours = LEGACY_EXPIRATION_HOURS
    return entered_at + timedelta(hours=hours)


def reservation_is_expired(
    now: datetime,
    entered_at: datetime,
    configured_hours: int = LEGACY_EXPIRATION_HOURS,
    *,
    contract_created_at: datetime | None = None,
    effective_at: datetime | None = None,
) -> bool:
    return now >= reservation_expiration_deadline(
        entered_at,
        configured_hours,
        contract_created_at=contract_created_at,
        effective_at=effective_at,
    )
