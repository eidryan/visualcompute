from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

from .activity import event_at, write_activity_log
from .annotate import annotate_video
from .engine import map_detection_rows
from .scenario import demo_events, detections_at


WIDTH, HEIGHT, FPS, DURATION = 1280, 720, 15, 22.0


def _label(frame: np.ndarray, text: str, point: tuple[int, int], scale: float = .55,
           color: tuple[int, int, int] = (224, 226, 236), thickness: int = 1) -> None:
    cv2.putText(frame, text, point, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def _scene(timestamp: float) -> np.ndarray:
    frame = np.full((HEIGHT, WIDTH, 3), (20, 21, 31), dtype=np.uint8)
    cv2.rectangle(frame, (0, 0), (WIDTH, 180), (31, 29, 44), -1)
    cv2.rectangle(frame, (80, 180), (1120, 570), (48, 50, 61), -1)
    cv2.rectangle(frame, (80, 510), (1120, 590), (69, 69, 76), -1)
    cv2.rectangle(frame, (1120, 160), (1279, 620), (37, 39, 50), -1)
    _label(frame, "PREP STATION", (91, 207), .48, (148, 151, 169))
    _label(frame, "HANDOFF", (1154, 207), .48, (148, 151, 169))

    cv2.rectangle(frame, (518, 35), (692, 165), (70, 50, 82), -1)
    cv2.rectangle(frame, (555, 90), (655, 173), (105, 43, 119), -1)
    _label(frame, "ACAI", (578, 78), .52, (243, 199, 255), 2)

    bins = ((291, "BANANA", (63, 177, 240)), (476, "GRANOLA", (62, 192, 181)), (661, "CHOCO", (98, 123, 186)))
    for x, name, color in bins:
        cv2.rectangle(frame, (x, 205), (x + 154, 305), color, -1)
        cv2.rectangle(frame, (x, 205), (x + 154, 227), tuple(max(0, c - 28) for c in color), -1)
        _label(frame, name, (x + 18, 279), .5, (22, 24, 31), 2)

    cv2.rectangle(frame, (502, 442), (708, 514), (77, 82, 92), -1)
    cv2.rectangle(frame, (527, 451), (683, 493), (115, 134, 139), -1)
    _label(frame, "SCALE", (566, 483), .5, (220, 239, 231), 1)
    cv2.rectangle(frame, (790, 441), (1030, 533), (72, 76, 91), -1)
    cv2.rectangle(frame, (808, 455), (1012, 518), (58, 62, 76), 3)

    detections = detections_at(timestamp)
    worker = next(d for d in detections if d.label == "worker")
    wx1, wy1, wx2, wy2 = worker.bbox
    center = ((wx1 + wx2) // 2, wy1 + 47)
    cv2.circle(frame, center, 29, (170, 128, 96), -1, cv2.LINE_AA)
    cv2.ellipse(frame, ((wx1 + wx2) // 2, wy1 + 165), (58, 96), 0, 0, 360, (98, 70, 163), -1, cv2.LINE_AA)
    cv2.line(frame, (center[0] - 38, wy1 + 130), (center[0] - 100, wy1 + 206), (170, 128, 96), 18, cv2.LINE_AA)
    cv2.line(frame, (center[0] + 38, wy1 + 130), (center[0] + 91, wy1 + 202), (170, 128, 96), 18, cv2.LINE_AA)

    bowl = next(d for d in detections if d.label == "bowl")
    bx1, by1, bx2, by2 = bowl.bbox
    cv2.ellipse(frame, ((bx1 + bx2) // 2, (by1 + by2) // 2), ((bx2 - bx1) // 2, (by2 - by1) // 2),
                0, 0, 180, (231, 225, 241), -1, cv2.LINE_AA)
    cv2.ellipse(frame, ((bx1 + bx2) // 2, (by1 + by2) // 2), ((bx2 - bx1) // 2, 12),
                0, 0, 360, (101, 34, 120), -1, cv2.LINE_AA)

    if timestamp >= 18.9:
        customer = next(d for d in detections if d.label == "customer")
        cx1, cy1, cx2, cy2 = customer.bbox
        cv2.circle(frame, ((cx1 + cx2) // 2, cy1 + 45), 28, (133, 155, 187), -1, cv2.LINE_AA)
        cv2.ellipse(frame, ((cx1 + cx2) // 2, cy1 + 160), (55, 94), 0, 0, 360, (60, 131, 130), -1)

    active = event_at(demo_events(), timestamp)
    if active and active.activity in {"dispense_acai", "add_ingredient"}:
        cv2.circle(frame, ((bx1 + bx2) // 2, (by1 + by2) // 2), 10, (94, 30, 114), -1)
    return frame


def generate_demo(output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "demo_input.mp4"
    annotated_path = output_dir / "demo_annotated.mp4"
    detections_path = output_dir / "detections.jsonl"
    log_path = output_dir / "activity_log.json"
    jsonl_path = output_dir / "activity_log.jsonl"

    writer = cv2.VideoWriter(str(raw_path), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (WIDTH, HEIGHT))
    if not writer.isOpened():
        raise RuntimeError(f"Could not create demo video: {raw_path}")

    reference = demo_events()
    rows: list[dict] = []
    frame_count = int(DURATION * FPS)
    with detections_path.open("w", encoding="utf-8") as stream:
        for frame_index in range(frame_count):
            timestamp = frame_index / FPS
            active = event_at(reference, timestamp)
            row = {
                "frame_index": frame_index,
                "timestamp": round(timestamp, 3),
                "frame_period": 1 / FPS,
                "activity": active.activity if active else None,
                "activity_confidence": active.confidence if active else 0.0,
                "activity_attributes": active.attributes if active else {},
                "activity_object_ids": list(active.object_ids) if active else [],
                "evidence": list(active.evidence) if active else [],
                "detections": [item.to_dict() for item in detections_at(timestamp)],
            }
            rows.append(row)
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            writer.write(_scene(timestamp))
    writer.release()

    mapped_events = map_detection_rows(rows, order_id="ORDER_0007")
    write_activity_log(
        mapped_events,
        log_path,
        jsonl_path,
        metadata={
            "video": annotated_path.name,
            "station_id": "demo_acai_01",
            "generated": True,
            "privacy": {"faces": "not identified", "audio": False},
        },
    )
    annotate_video(raw_path, annotated_path, rows, mapped_events)
    return {
        "input_video": raw_path,
        "annotated_video": annotated_path,
        "detections": detections_path,
        "activity_log": log_path,
        "activity_jsonl": jsonl_path,
    }
