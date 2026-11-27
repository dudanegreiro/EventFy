"""Pure policy rules for EventFy reservation and service domain behavior."""

from collections.abc import Sequence
from datetime import datetime, timedelta

RESERVATION_RESPONSE_SLA = timedelta(hours=48)

RESERVATION_TRANSITIONS = {
    "SOLICITADA": frozenset({"EM_ANALISE", "CANCELADA", "EXPIRADA"}),
    "EM_ANALISE": frozenset({"APROVADA", "RECUSADA", "CANCELADA", "EXPIRADA"}),
    "APROVADA": frozenset({"CONFIRMADA", "CANCELADA", "EXPIRADA"}),
    "CONFIRMADA": frozenset({"CANCELADA", "FINALIZADA"}),
    "RECUSADA": frozenset(),
    "CANCELADA": frozenset(),
    "EXPIRADA": frozenset(),
    "FINALIZADA": frozenset(),
}


def can_transition(current_status: str, next_status: str) -> bool:
    return next_status in RESERVATION_TRANSITIONS.get(current_status, frozenset())


def can_cancel_reservation(user_role: str, status: str) -> bool:
    if user_role == "ORGANIZADOR":
        return can_transition(status, "CANCELADA")
    return user_role == "PRESTADOR" and status == "CONFIRMADA"


def cancellation_window_is_open(event_start: datetime, now: datetime) -> bool:
    return now < event_start


def reservation_expiration_due(
    status: str,
    state_entered_at: datetime,
    now: datetime,
) -> bool:
    return (
        status in {"SOLICITADA", "EM_ANALISE", "APROVADA"}
        and now >= state_entered_at + RESERVATION_RESPONSE_SLA
    )


def service_period_is_available(
    requested_start: datetime,
    requested_end: datetime,
    available_periods: Sequence[tuple[datetime, datetime]],
    blocking_periods: Sequence[tuple[datetime, datetime]],
) -> bool:
    if requested_end <= requested_start:
        return False

    covered = any(
        available_start <= requested_start and available_end >= requested_end
        for available_start, available_end in available_periods
    )
    overlaps_block = any(
        block_start < requested_end and block_end > requested_start
        for block_start, block_end in blocking_periods
    )
    return covered and not overlaps_block


def can_evaluate_reservation(
    user_role: str,
    status: str,
    *,
    is_organizer_owner: bool,
    already_evaluated: bool,
) -> bool:
    return (
        user_role == "ORGANIZADOR"
        and is_organizer_owner
        and status == "FINALIZADA"
        and not already_evaluated
    )
