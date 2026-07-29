from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .activity import ActivityEvent, Detection


@dataclass
class _OpenEvent:
    activity: str
    start: float
    last_seen: float
    confidence_sum: float
    samples: int
    actor_id: int
    object_ids: set[int] = field(default_factory=set)
    attributes: dict[str, Any] = field(default_factory=dict)
    evidence: set[str] = field(default_factory=set)


class ActivityMapper:
    """Collapse frame-level action predictions into stable operational events.

    A production action head, state machine, or human annotation may supply the
    frame-level activity. This class provides debouncing, gap tolerance and the
    stable event contract consumed by dashboards and integrations.
    """

    def __init__(self, order_id: str = "ORDER_UNKNOWN", min_duration: float = 0.25):
        self.order_id = order_id
        self.min_duration = min_duration
        self._open: _OpenEvent | None = None
        self._events: list[ActivityEvent] = []

    def ingest(
        self,
        timestamp: float,
        activity: str | None,
        detections: list[Detection],
        confidence: float = 0.0,
        attributes: dict[str, Any] | None = None,
        evidence: list[str] | None = None,
    ) -> None:
        if not activity or activity in {"unknown", "idle"}:
            return
        actor = next((d.track_id for d in detections if d.label == "worker"), 0)
        object_ids = {d.track_id for d in detections if d.label not in {"worker", "customer"}}
        if self._open and self._open.activity != activity:
            self._close(timestamp)
        if self._open is None:
            self._open = _OpenEvent(
                activity=activity,
                start=timestamp,
                last_seen=timestamp,
                confidence_sum=confidence,
                samples=1,
                actor_id=actor,
                object_ids=object_ids,
                attributes=dict(attributes or {}),
                evidence=set(evidence or []),
            )
        else:
            self._open.last_seen = timestamp
            self._open.confidence_sum += confidence
            self._open.samples += 1
            self._open.object_ids.update(object_ids)
            self._open.attributes.update(attributes or {})
            self._open.evidence.update(evidence or [])

    def _close(self, end: float) -> None:
        current = self._open
        self._open = None
        if current is None or end - current.start < self.min_duration:
            return
        self._events.append(ActivityEvent(
            event_id=f"evt_{len(self._events) + 1:03d}",
            order_id=self.order_id,
            activity=current.activity,
            start=round(current.start, 3),
            end=round(end, 3),
            confidence=round(current.confidence_sum / current.samples, 3),
            actor_id=current.actor_id,
            object_ids=tuple(sorted(current.object_ids)),
            attributes=current.attributes,
            evidence=tuple(sorted(current.evidence)),
        ))

    def finish(self, end: float) -> list[ActivityEvent]:
        self._close(end)
        return list(self._events)


def read_detection_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def map_detection_rows(
    rows: list[dict[str, Any]],
    order_id: str = "ORDER_UNKNOWN",
) -> list[ActivityEvent]:
    mapper = ActivityMapper(order_id=order_id)
    last_time = 0.0
    for row in rows:
        timestamp = float(row["timestamp"])
        last_time = timestamp
        detections = [Detection.from_dict(item) for item in row.get("detections", [])]
        mapper.ingest(
            timestamp=timestamp,
            activity=row.get("activity"),
            detections=detections,
            confidence=float(row.get("activity_confidence", 0.0)),
            attributes=row.get("activity_attributes"),
            evidence=row.get("evidence"),
        )
    frame_period = rows[-1].get("frame_period", 1 / 15) if rows else 0.0
    return mapper.finish(last_time + float(frame_period))
