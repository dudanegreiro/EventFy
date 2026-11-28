from datetime import datetime, timedelta, timezone

import pytest

from eventfy_api.expiration_policy import (
    reservation_expiration_deadline,
    reservation_is_expired,
)


@pytest.mark.parametrize("hours", [24, 48, 96])
def test_expiration_deadline_uses_configured_hours(hours: int) -> None:
    entered_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

    assert reservation_expiration_deadline(
        entered_at,
        hours,
        contract_created_at=entered_at,
        effective_at=entered_at,
    ) == entered_at + timedelta(hours=hours)


def test_expiration_deadline_defaults_to_legacy_48_hours() -> None:
    entered_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

    assert reservation_expiration_deadline(entered_at) == entered_at + timedelta(
        hours=48
    )


def test_contract_created_before_cutover_keeps_legacy_deadline() -> None:
    cutover = datetime(2026, 2, 1, tzinfo=timezone.utc)
    created_at = cutover - timedelta(microseconds=1)
    entered_at = datetime(2026, 1, 31, tzinfo=timezone.utc)

    assert reservation_expiration_deadline(
        entered_at,
        72,
        contract_created_at=created_at,
        effective_at=cutover,
    ) == entered_at + timedelta(hours=48)


def test_contract_created_at_cutover_uses_new_deadline() -> None:
    cutover = datetime(2026, 2, 1, tzinfo=timezone.utc)

    assert reservation_expiration_deadline(
        cutover,
        72,
        contract_created_at=cutover,
        effective_at=cutover,
    ) == cutover + timedelta(hours=72)


@pytest.mark.parametrize(
    "elapsed_hours,expected",
    [(48 - 1 / 3600, False), (48, True), (48 + 1 / 3600, True)],
)
def test_legacy_expiration_boundary(elapsed_hours: float, expected: bool) -> None:
    entered_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

    assert reservation_is_expired(
        entered_at + timedelta(hours=elapsed_hours), entered_at
    ) is expected


def test_expiration_deadline_rejects_non_positive_hours() -> None:
    with pytest.raises(ValueError):
        reservation_expiration_deadline(datetime.now(timezone.utc), 0)
