from datetime import datetime, timedelta, timezone

import pytest

from eventfy_api.expiration_policy import reservation_expiration_deadline


@pytest.mark.parametrize("hours", [24, 48, 96])
def test_expiration_deadline_uses_configured_hours(hours: int) -> None:
    entered_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

    assert reservation_expiration_deadline(entered_at, hours) == entered_at + timedelta(
        hours=hours
    )


def test_expiration_deadline_defaults_to_legacy_48_hours() -> None:
    entered_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

    assert reservation_expiration_deadline(entered_at) == entered_at + timedelta(
        hours=48
    )


def test_expiration_deadline_rejects_non_positive_hours() -> None:
    with pytest.raises(ValueError):
        reservation_expiration_deadline(datetime.now(timezone.utc), 0)
