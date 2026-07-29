from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


OBJECT_LABELS = (
    "worker", "customer", "bowl", "cup", "tray", "scoop", "spoon",
    "acai_dispenser", "ingredient_bin", "banana", "granola", "chocolate",
    "whey", "scale", "phone",
)

ACTIVITY_META = {
    "approach_station": ("APPROACHING STATION", (118, 215, 255)),
    "pick_up_bowl": ("PICKING UP BOWL", (255, 190, 92)),
    "place_bowl_on_scale": ("BOWL ON SCALE", (106, 238, 184)),
    "dispense_acai": ("DISPENSING ACAI", (231, 116, 255)),
    "retrieve_ingredient": ("GETTING INGREDIENT", (255, 201, 92)),
    "add_ingredient": ("ADDING INGREDIENT", (91, 232, 255)),
    "mix_contents": ("MIXING", (255, 140, 188)),
    "place_on_tray": ("PLACING ON TRAY", (112, 214, 255)),
    "handoff_order": ("HANDING OFF ORDER", (133, 241, 184)),
    "use_phone": ("PHONE USE", (92, 92, 255)),
    "idle": ("IDLE", (170, 170, 180)),
    "unknown": ("OBSERVING", (200, 200, 210)),
}


@dataclass(frozen=True)
class Detection:
    track_id: int
    label: str
    confidence: float
    bbox: tuple[int, int, int, int]
    attributes: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Detection":
        return cls(
            track_id=int(data["track_id"]),
            label=str(data["label"]),
            confidence=float(data.get("confidence", 1.0)),
            bbox=tuple(int(v) for v in data["bbox"]),
            attributes=dict(data.get("attributes", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["bbox"] = list(self.bbox)
        return data


@dataclass(frozen=True)
class ActivityEvent:
    event_id: str
    order_id: str
    activity: str
    start: float
    end: float
    confidence: float
    actor_id: int
    object_ids: tuple[int, ...] = ()
    attributes: dict[str, Any] = field(default_factory=dict)
    evidence: tuple[str, ...] = ()
    status: str = "observed"

    @property
    def duration(self) -> float:
        return round(self.end - self.start, 3)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["duration"] = self.duration
        data["object_ids"] = list(self.object_ids)
        data["evidence"] = list(self.evidence)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActivityEvent":
        known = {
            "event_id", "order_id", "activity", "start", "end", "confidence",
            "actor_id", "object_ids", "attributes", "evidence", "status",
        }
        clean = {key: value for key, value in data.items() if key in known}
        clean["object_ids"] = tuple(clean.get("object_ids", ()))
        clean["evidence"] = tuple(clean.get("evidence", ()))
        return cls(**clean)


def event_at(events: Iterable[ActivityEvent], timestamp: float) -> ActivityEvent | None:
    for event in events:
        if event.start <= timestamp < event.end:
            return event
    return None


def summarize_events(events: list[ActivityEvent]) -> dict[str, Any]:
    if not events:
        return {"orders": 0, "events": 0, "cycle_time": 0.0}
    return {
        "orders": len({event.order_id for event in events}),
        "events": len(events),
        "cycle_time": round(max(e.end for e in events) - min(e.start for e in events), 3),
        "mean_confidence": round(sum(e.confidence for e in events) / len(events), 3),
        "activities": sorted({e.activity for e in events}),
    }


def write_activity_log(
    events: list[ActivityEvent],
    json_path: Path,
    jsonl_path: Path | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "source": metadata or {},
        "summary": summarize_events(events),
        "events": [event.to_dict() for event in events],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if jsonl_path:
        with jsonl_path.open("w", encoding="utf-8") as stream:
            for event in events:
                stream.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")


def load_events(path: Path) -> list[ActivityEvent]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["events"] if isinstance(data, dict) else data
    return [ActivityEvent.from_dict(row) for row in rows]
