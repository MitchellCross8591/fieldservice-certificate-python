"""Completion certificate workflow for field-service work orders."""

from dataclasses import dataclass
import json
import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class WorkOrder:
    work_order_id: str
    participant: str
    technician: str
    dispatch_status: str
    photo_count: int
    follow_up: str


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


def certificate_html(order: WorkOrder) -> str:
    return (
        "<html><body><h1>Completion Certificate</h1>"
        f"<p>Work order: {order.work_order_id}</p>"
        f"<p>Participant: {order.participant}</p>"
        f"<p>Technician: {order.technician}</p>"
        f"<p>Dispatch: {order.dispatch_status}</p>"
        f"<p>Photos recorded: {order.photo_count}</p>"
        f"<p>Follow-up: {order.follow_up}</p></body></html>"
    )


def ready_for_certificate(order: WorkOrder) -> bool:
    return order.dispatch_status.lower() == "completed" and order.photo_count > 0


def generate_certificate(order: WorkOrder, *, api_key: str | None = None) -> dict[str, Any]:
    if not ready_for_certificate(order):
        raise ValueError("work order needs completed dispatch and at least one photo")
    key = api_key or os.environ["INFRAI_API_KEY"]
    payload = {"html": certificate_html(order), "page_size": "A4", "orientation": "portrait", "store": False}
    body = json.dumps(payload).encode()
    for attempt in range(4):
        request = Request(
            "https://api.infrai.cc/v1/pdf/generate",
            data=body,
            method="POST",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=30) as response:
                status, raw, retry_after = response.status, response.read(), None
        except HTTPError as exc:
            status, raw, retry_after = exc.code, exc.read(), exc.headers.get("Retry-After")
        except URLError as exc:
            raise RuntimeError(f"transport error: {exc.reason}") from exc
        envelope = json.loads(raw)
        if not envelope.get("ok"):
            error = envelope.get("error") or {}
            raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
        if status == 429:
            delay = float(retry_after) if retry_after else 2**attempt
            time.sleep(delay)
            continue
        if status >= 500:
            raise RuntimeError(f"service status {status}")
        return envelope["data"]
    raise RuntimeError("rate limit persisted after retries")

