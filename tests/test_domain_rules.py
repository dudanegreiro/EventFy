from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from eventfy_api.domain import (
    RESERVATION_RESPONSE_SLA,
    can_cancel_reservation,
    can_evaluate_reservation,
    can_transition,
    cancellation_window_is_open,
    reservation_expiration_due,
    service_period_is_available,
)
from eventfy_api.schemas import (
    AvailabilityCreate,
    ReservationCancellation,
    ReservationDecision,
    ServiceEvaluationCreate,
)


@pytest.mark.parametrize(
    ("current_status", "next_status"),
    [
        ("SOLICITADA", "EM_ANALISE"),
        ("EM_ANALISE", "APROVADA"),
        ("EM_ANALISE", "RECUSADA"),
        ("APROVADA", "CONFIRMADA"),
        ("CONFIRMADA", "FINALIZADA"),
        ("SOLICITADA", "CANCELADA"),
        ("EM_ANALISE", "EXPIRADA"),
    ],
)
def test_reservation_follows_a_documented_state_transition(
    current_status: str,
    next_status: str,
) -> None:
    # Arrange
    # Act
    allowed = can_transition(current_status, next_status)

    # Assert
    assert allowed is True


@pytest.mark.parametrize(
    "terminal_status",
    ["RECUSADA", "CANCELADA", "EXPIRADA", "FINALIZADA"],
)
def test_terminal_reservation_state_cannot_transition_again(
    terminal_status: str,
) -> None:
    # Arrange
    # Act
    allowed = can_transition(terminal_status, "CONFIRMADA")

    # Assert
    assert allowed is False


@pytest.mark.parametrize(
    ("role", "status", "expected"),
    [
        ("ORGANIZADOR", "SOLICITADA", True),
        ("ORGANIZADOR", "EM_ANALISE", True),
        ("ORGANIZADOR", "APROVADA", True),
        ("ORGANIZADOR", "CONFIRMADA", True),
        ("PRESTADOR", "CONFIRMADA", True),
        ("PRESTADOR", "APROVADA", False),
        ("ADMINISTRADOR", "CONFIRMADA", False),
        ("ORGANIZADOR", "RECUSADA", False),
    ],
)
def test_cancellation_permission_depends_on_role_and_reservation_state(
    role: str,
    status: str,
    expected: bool,
) -> None:
    # Arrange
    # Act
    allowed = can_cancel_reservation(role, status)

    # Assert
    assert allowed is expected


def test_cancellation_closes_at_event_start_using_an_explicit_clock() -> None:
    # Arrange
    event_start = datetime(2030, 6, 1, 12, tzinfo=timezone.utc)
    one_second_before = event_start - timedelta(seconds=1)

    # Act
    cancellable_before_start = cancellation_window_is_open(
        event_start, one_second_before
    )
    cancellable_at_start = cancellation_window_is_open(event_start, event_start)

    # Assert
    assert cancellable_before_start is True
    assert cancellable_at_start is False


def test_expiration_uses_an_explicit_clock_and_the_48_hour_boundary() -> None:
    # Arrange
    now = datetime(2030, 6, 1, 12, tzinfo=timezone.utc)
    entered_state_at = now - RESERVATION_RESPONSE_SLA

    # Act
    due_at_boundary = reservation_expiration_due(
        "SOLICITADA", entered_state_at, now
    )
    due_one_second_early = reservation_expiration_due(
        "SOLICITADA", entered_state_at + timedelta(seconds=1), now
    )

    # Assert
    assert due_at_boundary is True
    assert due_one_second_early is False


@pytest.mark.parametrize(
    "terminal_status",
    ["RECUSADA", "CANCELADA", "EXPIRADA", "FINALIZADA"],
)
def test_terminal_reservation_does_not_expire_again(terminal_status: str) -> None:
    # Arrange
    now = datetime(2030, 6, 1, 12, tzinfo=timezone.utc)
    entered_state_at = now - timedelta(days=30)

    # Act
    due = reservation_expiration_due(terminal_status, entered_state_at, now)

    # Assert
    assert due is False


def test_service_is_available_when_one_period_covers_request_without_overlap() -> None:
    # Arrange
    request_start = datetime(2030, 6, 1, 10, tzinfo=timezone.utc)
    request_end = datetime(2030, 6, 1, 12, tzinfo=timezone.utc)
    available_periods = [
        (datetime(2030, 6, 1, 9, tzinfo=timezone.utc), request_end)
    ]

    # Act
    available = service_period_is_available(
        request_start,
        request_end,
        available_periods,
        [],
    )

    # Assert
    assert available is True


@pytest.mark.parametrize(
    ("block_start_hour", "block_end_hour", "expected"),
    [(11, 13, False), (12, 13, True), (9, 10, True)],
)
def test_manual_block_uses_half_open_interval_overlap(
    block_start_hour: int,
    block_end_hour: int,
    expected: bool,
) -> None:
    # Arrange
    request_start = datetime(2030, 6, 1, 10, tzinfo=timezone.utc)
    request_end = datetime(2030, 6, 1, 12, tzinfo=timezone.utc)
    available_periods = [(request_start, request_end)]
    blocking_periods = [
        (
            datetime(2030, 6, 1, block_start_hour, tzinfo=timezone.utc),
            datetime(2030, 6, 1, block_end_hour, tzinfo=timezone.utc),
        )
    ]

    # Act
    available = service_period_is_available(
        request_start,
        request_end,
        available_periods,
        blocking_periods,
    )

    # Assert
    assert available is expected


def test_service_is_unavailable_when_no_single_window_covers_request() -> None:
    # Arrange
    request_start = datetime(2030, 6, 1, 10, tzinfo=timezone.utc)
    request_end = datetime(2030, 6, 1, 12, tzinfo=timezone.utc)
    available_periods = [
        (request_start, datetime(2030, 6, 1, 11, tzinfo=timezone.utc)),
        (datetime(2030, 6, 1, 11, tzinfo=timezone.utc), request_end),
    ]

    # Act
    available = service_period_is_available(
        request_start,
        request_end,
        available_periods,
        [],
    )

    # Assert
    assert available is False


def test_availability_request_requires_timezone_and_positive_duration() -> None:
    # Arrange
    valid_request = {
        "tipo": "DISPONIVEL",
        "data_inicio": "2030-06-01T10:00:00Z",
        "data_fim": "2030-06-01T12:00:00Z",
    }

    # Act
    accepted = AvailabilityCreate.model_validate(valid_request)
    without_timezone = {**valid_request, "data_inicio": "2030-06-01T10:00:00"}
    invalid_duration = {
        **valid_request,
        "data_fim": "2030-06-01T10:00:00Z",
    }

    # Assert
    assert accepted.data_fim > accepted.data_inicio
    with pytest.raises(ValidationError, match="fuso horario"):
        AvailabilityCreate.model_validate(without_timezone)
    with pytest.raises(ValidationError, match="posterior"):
        AvailabilityCreate.model_validate(invalid_duration)


@pytest.mark.parametrize(
    ("decision", "reason", "accepted"),
    [
        ("APROVADA", None, True),
        ("RECUSADA", "curto", False),
        ("RECUSADA", "motivo valido", True),
    ],
)
def test_rejection_requires_at_least_ten_nonblank_characters(
    decision: str,
    reason: str | None,
    accepted: bool,
) -> None:
    # Arrange
    payload = {"decisao": decision, "motivo": reason}

    # Act
    if accepted:
        result = ReservationDecision.model_validate(payload)

    # Assert
    if accepted:
        assert result.decisao == decision
    else:
        with pytest.raises(ValidationError, match="10 caracteres"):
            ReservationDecision.model_validate(payload)


@pytest.mark.parametrize("reason", ["curto", "          ", "123456789"])
def test_cancellation_requires_a_meaningful_reason(reason: str) -> None:
    # Arrange
    payload = {"motivo": reason}

    # Act / Assert
    with pytest.raises(ValidationError) as error:
        ReservationCancellation.model_validate(payload)
    assert error.value.errors()[0]["loc"] == ("motivo",)


@pytest.mark.parametrize("rating", [1, 5])
def test_evaluation_accepts_each_endpoint_of_the_one_to_five_scale(
    rating: int,
) -> None:
    # Arrange
    payload = {"nota": rating}

    # Act
    evaluation = ServiceEvaluationCreate.model_validate(payload)

    # Assert
    assert evaluation.nota == rating


@pytest.mark.parametrize("rating", [0, 6, True, 3.5])
def test_evaluation_rejects_values_outside_the_integer_scale(rating: object) -> None:
    # Arrange
    payload = {"nota": rating}

    # Act / Assert
    with pytest.raises(ValidationError):
        ServiceEvaluationCreate.model_validate(payload)


@pytest.mark.parametrize(
    ("role", "status", "owner", "already_evaluated", "expected"),
    [
        ("ORGANIZADOR", "FINALIZADA", True, False, True),
        ("PRESTADOR", "FINALIZADA", True, False, False),
        ("ORGANIZADOR", "CONFIRMADA", True, False, False),
        ("ORGANIZADOR", "FINALIZADA", False, False, False),
        ("ORGANIZADOR", "FINALIZADA", True, True, False),
    ],
)
def test_evaluation_requires_owner_finalized_reservation_and_no_prior_rating(
    role: str,
    status: str,
    owner: bool,
    already_evaluated: bool,
    expected: bool,
) -> None:
    # Arrange
    # Act
    allowed = can_evaluate_reservation(
        role,
        status,
        is_organizer_owner=owner,
        already_evaluated=already_evaluated,
    )

    # Assert
    assert allowed is expected
