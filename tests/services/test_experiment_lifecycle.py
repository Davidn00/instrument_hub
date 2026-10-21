"""Unit tests for the experiment state machine."""

from app.services.experiments import ExperimentService


def test_created_experiment_can_start() -> None:
    assert "RUNNING" in ExperimentService.VALID_TRANSITIONS["CREATED"]


def test_running_experiment_can_complete() -> None:
    assert "COMPLETED" in ExperimentService.VALID_TRANSITIONS["RUNNING"]


def test_completed_experiment_cannot_restart() -> None:
    assert ExperimentService.VALID_TRANSITIONS["COMPLETED"] == set()


def test_failed_experiment_cannot_restart() -> None:
    assert ExperimentService.VALID_TRANSITIONS["FAILED"] == set()


def test_cancelled_experiment_cannot_restart() -> None:
    assert ExperimentService.VALID_TRANSITIONS["CANCELLED"] == set()


def test_invalid_transition_is_not_allowed() -> None:
    current_status = "CREATED"
    requested_status = "COMPLETED"

    assert requested_status not in (ExperimentService.VALID_TRANSITIONS[current_status])
