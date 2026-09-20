import pytest

from src.certificate_service import WorkOrder, ready_for_certificate


def test_certificate_requires_completed_dispatch_and_photo() -> None:
    complete = WorkOrder("WO-1", "A", "T", "completed", 1, "call site")
    waiting = WorkOrder("WO-2", "A", "T", "dispatched", 2, "call site")
    no_photo = WorkOrder("WO-3", "A", "T", "completed", 0, "call site")
    assert ready_for_certificate(complete) is True
    assert ready_for_certificate(waiting) is False
    assert ready_for_certificate(no_photo) is False

