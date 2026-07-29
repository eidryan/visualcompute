from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import cv2


def generate_yolo_tracks(
    video_path: Path,
    output_path: Path,
    *,
    model_name: str = "yolo11n.pt",
    confidence: float = 0.15,
    image_size: int = 416,
) -> dict[str, Any]:
    """Run Ultralytics YOLO with ByteTrack and write one JSON object per frame."""
    try:
        from ultralytics import YOLO
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "Ultralytics is not installed. Install the project with the 'yolo' extra."
        ) from exc

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")

    fps = float(capture.get(cv2.CAP_PROP_FPS) or 15.0)
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model = YOLO(model_name)
    class_counts: Counter[str] = Counter()
    track_ids: set[int] = set()
    processed = 0
    detections_total = 0

    with output_path.open("w", encoding="utf-8") as stream:
        while True:
            ok, frame = capture.read()
            if not ok:
                break

            result = model.track(
                frame,
                persist=True,
                tracker="bytetrack.yaml",
                conf=confidence,
                imgsz=image_size,
                verbose=False,
            )[0]
            detections: list[dict[str, Any]] = []
            boxes = result.boxes
            if boxes is not None and len(boxes):
                xyxy = boxes.xyxy.cpu().tolist()
                classes = boxes.cls.int().cpu().tolist()
                confidences = boxes.conf.cpu().tolist()
                ids = (
                    boxes.id.int().cpu().tolist()
                    if boxes.id is not None
                    else [None] * len(xyxy)
                )
                for bbox, class_id, score, track_id in zip(
                    xyxy, classes, confidences, ids, strict=True
                ):
                    label = str(result.names[class_id])
                    class_counts[label] += 1
                    if track_id is not None:
                        track_ids.add(track_id)
                    detections.append(
                        {
                            "track_id": track_id,
                            "class_id": class_id,
                            "label": label,
                            "confidence": round(float(score), 4),
                            "bbox": [round(float(value), 2) for value in bbox],
                            "source": "ultralytics_yolo",
                        }
                    )

            row = {
                "frame_index": processed,
                "timestamp": round(processed / fps, 4),
                "model": model_name,
                "tracker": "ByteTrack",
                "detections": detections,
            }
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            processed += 1
            detections_total += len(detections)
            if processed % 100 == 0:
                print(f"processed {processed}/{total_frames or '?'} frames", flush=True)

    capture.release()
    return {
        "video": str(video_path),
        "output": str(output_path),
        "model": model_name,
        "tracker": "ByteTrack",
        "fps": fps,
        "frames": processed,
        "detections": detections_total,
        "unique_track_ids": len(track_ids),
        "classes": dict(class_counts.most_common()),
    }
