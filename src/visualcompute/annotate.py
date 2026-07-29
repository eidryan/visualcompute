from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np

from .activity import ACTIVITY_META, ActivityEvent, Detection, event_at


COLORS = {
    "worker": (92, 238, 255),
    "customer": (168, 225, 122),
    "bowl": (255, 142, 228),
    "tray": (245, 190, 82),
    "scoop": (128, 241, 202),
    "ingredient_bin": (196, 140, 255),
    "acai_dispenser": (255, 126, 164),
    "scale": (112, 214, 255),
}


def _text(frame: np.ndarray, label: str, point: tuple[int, int], scale: float = .58,
          color: tuple[int, int, int] = (245, 245, 250), thickness: int = 1) -> None:
    cv2.putText(frame, label, point, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def _track_label(detection: Detection, active: ActivityEvent | None) -> str:
    prefix = f"#{detection.track_id:02d} {detection.label.upper()}"
    if detection.label == "worker" and active:
        action = ACTIVITY_META.get(active.activity, (active.activity.upper(), (255, 255, 255)))[0]
        item = active.attributes.get("item")
        if item and active.activity in {"retrieve_ingredient", "add_ingredient"}:
            action = f"{action}: {str(item).upper()}"
        return f"{prefix} · {action} · {active.confidence:.0%}"
    if detection.label == "bowl":
        return f"{prefix} · {detection.attributes.get('order_id', 'UNASSIGNED')}"
    if detection.label == "ingredient_bin":
        return f"#{detection.track_id:02d} {str(detection.attributes.get('item', 'ingredient')).upper()} BIN"
    return f"{prefix} · {detection.confidence:.0%}"


def _draw_detection(frame: np.ndarray, detection: Detection, active: ActivityEvent | None) -> None:
    x1, y1, x2, y2 = detection.bbox
    color = COLORS.get(detection.label, (220, 220, 225))
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)
    length = 16
    for start, end in (
        ((x1, y1), (x1 + length, y1)), ((x1, y1), (x1, y1 + length)),
        ((x2, y1), (x2 - length, y1)), ((x2, y1), (x2, y1 + length)),
        ((x1, y2), (x1 + length, y2)), ((x1, y2), (x1, y2 - length)),
        ((x2, y2), (x2 - length, y2)), ((x2, y2), (x2, y2 - length)),
    ):
        cv2.line(frame, start, end, color, 4, cv2.LINE_AA)
    label = _track_label(detection, active)
    (width, height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, .52, 1)
    top = max(4, y1 - height - 13)
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, top), (min(frame.shape[1] - 4, x1 + width + 14), y1), (14, 16, 27), -1)
    cv2.addWeighted(overlay, .84, frame, .16, 0, frame)
    _text(frame, label, (x1 + 7, y1 - 7), .52, color, 1)


def _draw_status(frame: np.ndarray, timestamp: float, events: list[ActivityEvent],
                 active: ActivityEvent | None) -> None:
    overlay = frame.copy()
    cv2.rectangle(overlay, (22, 20), (508, 121), (11, 12, 22), -1)
    cv2.addWeighted(overlay, .87, frame, .13, 0, frame)
    cv2.rectangle(frame, (22, 20), (28, 121), (229, 104, 255), -1)
    _text(frame, "VISUALCOMPUTE / LIVE ACTIVITY MAP", (45, 49), .54, (204, 202, 216), 1)
    if active:
        title = ACTIVITY_META.get(active.activity, (active.activity.upper(), (255, 255, 255)))[0]
        item = active.attributes.get("item")
        if item:
            title += f" · {str(item).upper()}"
        _text(frame, title, (45, 82), .76, (255, 255, 255), 2)
        index = events.index(active) + 1
        _text(frame, f"ORDER_0007  /  STEP {index:02d}/{len(events):02d}  /  {timestamp:05.1f}s  /  {active.confidence:.0%}",
              (45, 108), .47, (171, 220, 236), 1)
    else:
        _text(frame, "WAITING FOR ACTIVITY", (45, 84), .7, (235, 235, 240), 2)

    height, width = frame.shape[:2]
    y = height - 42
    start_x, end_x = 30, width - 30
    total = max((event.end for event in events), default=1)
    cv2.line(frame, (start_x, y), (end_x, y), (68, 70, 84), 7, cv2.LINE_AA)
    for event in events:
        x1 = int(start_x + (end_x - start_x) * event.start / total)
        x2 = int(start_x + (end_x - start_x) * event.end / total)
        color = ACTIVITY_META.get(event.activity, ("", (220, 220, 220)))[1]
        cv2.line(frame, (x1, y), (x2, y), color, 7, cv2.LINE_AA)
    cursor = int(start_x + (end_x - start_x) * min(timestamp / total, 1.0))
    cv2.circle(frame, (cursor, y), 8, (255, 255, 255), -1, cv2.LINE_AA)
    _text(frame, "ACTIVITY TIMELINE", (30, y - 14), .42, (205, 205, 215), 1)


def annotate_video(
    input_path: Path,
    output_path: Path,
    detection_rows: list[dict[str, Any]],
    events: list[ActivityEvent],
) -> None:
    capture = cv2.VideoCapture(str(input_path))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open input video: {input_path}")
    fps = capture.get(cv2.CAP_PROP_FPS) or 15.0
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        raise RuntimeError(f"Could not create output video: {output_path}")

    row_by_frame = {int(row.get("frame_index", index)): row for index, row in enumerate(detection_rows)}
    frame_index = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        timestamp = frame_index / fps
        active = event_at(events, timestamp)
        row = row_by_frame.get(frame_index, {})
        for raw in row.get("detections", []):
            _draw_detection(frame, Detection.from_dict(raw), active)
        _draw_status(frame, timestamp, events, active)
        writer.write(frame)
        frame_index += 1
    writer.release()
    capture.release()
