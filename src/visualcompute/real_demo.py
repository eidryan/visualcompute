from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import cv2
import imageio_ffmpeg
import numpy as np

from .activity import ACTIVITY_META, ActivityEvent, write_activity_log


@dataclass(frozen=True)
class SourceSegment:
    start_frame: int
    end_frame: int
    source_label: str
    activity: str | None
    attributes: dict[str, str]


BREAKFAST_CEREALS_SEGMENTS = (
    SourceSegment(1, 30, "SIL", None, {}),
    SourceSegment(30, 150, "take_bowl", "pick_up_bowl", {"container": "bowl"}),
    SourceSegment(150, 428, "pour_cereals", "add_ingredient", {"item": "dry_topping_proxy"}),
    SourceSegment(428, 575, "pour_milk", "dispense_acai", {"item": "liquid_base_proxy"}),
    SourceSegment(575, 705, "stir_cereals", "mix_contents", {}),
    SourceSegment(705, 836, "SIL", None, {}),
)

SOURCE_COLORS = {
    "pick_up_bowl": (255, 179, 92),
    "add_ingredient": (85, 224, 255),
    "dispense_acai": (224, 111, 255),
    "mix_contents": (255, 139, 183),
}


def _segment_at(frame_index: int) -> SourceSegment:
    for segment in BREAKFAST_CEREALS_SEGMENTS:
        if segment.start_frame <= frame_index < segment.end_frame:
            return segment
    return BREAKFAST_CEREALS_SEGMENTS[-1]


def mapped_events(fps: float = 15.0) -> list[ActivityEvent]:
    events: list[ActivityEvent] = []
    for segment in BREAKFAST_CEREALS_SEGMENTS:
        if segment.activity is None:
            continue
        events.append(ActivityEvent(
            event_id=f"real_evt_{len(events) + 1:03d}",
            order_id="BREAKFAST_P03_CEREALS",
            activity=segment.activity,
            start=round(segment.start_frame / fps, 3),
            end=round(segment.end_frame / fps, 3),
            confidence=1.0,
            actor_id=1,
            attributes={
                **segment.attributes,
                "source_label": segment.source_label,
                "mapping": "public_ground_truth_to_acai_proxy",
            },
            evidence=(
                f"Breakfast Actions ground-truth label: {segment.source_label}",
                f"annotated frames {segment.start_frame}:{segment.end_frame}",
            ),
            status="source_annotation",
        ))
    return events


def _text(
    frame: np.ndarray,
    text: str,
    point: tuple[int, int],
    scale: float = .55,
    color: tuple[int, int, int] = (238, 238, 244),
    thickness: int = 1,
) -> None:
    cv2.putText(
        frame, text, point, cv2.FONT_HERSHEY_SIMPLEX,
        scale, color, thickness, cv2.LINE_AA,
    )


def _motion_box(
    subtractor: cv2.BackgroundSubtractor,
    frame: np.ndarray,
    last_box: tuple[int, int, int, int] | None,
) -> tuple[int, int, int, int] | None:
    mask = subtractor.apply(frame)
    mask = cv2.threshold(mask, 210, 255, cv2.THRESH_BINARY)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.dilate(mask, kernel, iterations=3)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = [cv2.boundingRect(contour) for contour in contours if cv2.contourArea(contour) > 120]
    if not boxes:
        return last_box
    x1 = min(box[0] for box in boxes)
    y1 = min(box[1] for box in boxes)
    x2 = max(box[0] + box[2] for box in boxes)
    y2 = max(box[1] + box[3] for box in boxes)
    if x2 - x1 < 25 or y2 - y1 < 25:
        return last_box
    return (
        max(0, x1 - 8), max(0, y1 - 8),
        min(frame.shape[1], x2 + 8), min(frame.shape[0], y2 + 8),
    )


def _draw_motion_track(
    canvas: np.ndarray,
    box: tuple[int, int, int, int] | None,
    activity: str | None,
) -> None:
    if box is None:
        return
    x1, y1, x2, y2 = (
        int(box[0] * 3), int(box[1] * 3),
        int(box[2] * 3), int(box[3] * 3),
    )
    color = SOURCE_COLORS.get(activity or "", (105, 226, 255))
    cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)
    for a, b in (
        ((x1, y1), (x1 + 19, y1)), ((x1, y1), (x1, y1 + 19)),
        ((x2, y1), (x2 - 19, y1)), ((x2, y1), (x2, y1 + 19)),
        ((x1, y2), (x1 + 19, y2)), ((x1, y2), (x1, y2 - 19)),
        ((x2, y2), (x2 - 19, y2)), ((x2, y2), (x2, y2 - 19)),
    ):
        cv2.line(canvas, a, b, color, 4, cv2.LINE_AA)
    action = ACTIVITY_META.get(activity or "unknown", ("OBSERVING", color))[0]
    label = f"#01 ACTOR MOTION TRACK · {action}"
    (width, height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, .52, 1)
    top = max(5, y1 - height - 15)
    overlay = canvas.copy()
    cv2.rectangle(overlay, (x1, top), (min(955, x1 + width + 16), y1), (12, 13, 22), -1)
    cv2.addWeighted(overlay, .86, canvas, .14, 0, canvas)
    _text(canvas, label, (x1 + 8, y1 - 8), .52, color)


def _draw_panel(
    canvas: np.ndarray,
    frame_index: int,
    timestamp: float,
    segment: SourceSegment,
) -> None:
    cv2.rectangle(canvas, (960, 0), (1279, 719), (12, 12, 20), -1)
    cv2.line(canvas, (960, 0), (960, 720), (50, 48, 65), 1)
    _text(canvas, "VISUALCOMPUTE", (988, 49), .68, (237, 228, 246), 2)
    _text(canvas, "REAL-DATA ACTIVITY MAP", (988, 73), .43, (153, 148, 168))
    cv2.rectangle(canvas, (988, 99), (1246, 129), (31, 47, 40), -1)
    _text(canvas, "PUBLIC DATASET / SOURCE GT", (1002, 120), .42, (117, 241, 186), 1)

    _text(canvas, "SOURCE", (988, 170), .39, (130, 127, 145))
    _text(canvas, "Breakfast Actions", (988, 197), .59, (246, 244, 250), 1)
    _text(canvas, "P03 / cam01 / cereals", (988, 221), .43, (174, 171, 187))

    _text(canvas, "PUBLISHED LABEL", (988, 267), .39, (130, 127, 145))
    _text(canvas, segment.source_label.upper(), (988, 300), .72, (255, 203, 105), 2)
    _text(canvas, f"frame {frame_index:04d}  /  {timestamp:05.1f}s", (988, 325), .43, (172, 170, 184))

    _text(canvas, "MAPPED ACAI PROXY", (988, 372), .39, (130, 127, 145))
    mapped = ACTIVITY_META.get(segment.activity or "unknown", ("OBSERVING", (230, 230, 235)))[0]
    color = SOURCE_COLORS.get(segment.activity or "", (220, 220, 230))
    _text(canvas, mapped, (988, 405), .65, color, 2)
    if segment.attributes.get("item"):
        _text(canvas, segment.attributes["item"].replace("_", " ").upper(), (988, 431), .43, (190, 187, 202))

    cv2.line(canvas, (988, 468), (1246, 468), (43, 42, 56), 1)
    _text(canvas, "INTERPRETATION", (988, 501), .39, (130, 127, 145))
    lines = (
        "Action timing: dataset ground truth",
        "Actor box: inferred motion region",
        "Identity: anonymous session ID",
        "Object boxes: not supplied by source",
    )
    for index, line in enumerate(lines):
        _text(canvas, line, (988, 530 + index * 24), .40, (188, 185, 199))

    _text(canvas, "ACTIVITY TIMELINE", (988, 649), .39, (130, 127, 145))
    total_frames = BREAKFAST_CEREALS_SEGMENTS[-1].end_frame
    left, right, y = 988, 1246, 677
    cv2.line(canvas, (left, y), (right, y), (54, 53, 68), 8, cv2.LINE_AA)
    for item in BREAKFAST_CEREALS_SEGMENTS:
        x1 = left + int((right - left) * item.start_frame / total_frames)
        x2 = left + int((right - left) * item.end_frame / total_frames)
        item_color = SOURCE_COLORS.get(item.activity or "", (72, 71, 84))
        cv2.line(canvas, (x1, y), (x2, y), item_color, 8, cv2.LINE_AA)
    cursor = left + int((right - left) * frame_index / total_frames)
    cv2.circle(canvas, (cursor, y), 7, (255, 255, 255), -1, cv2.LINE_AA)


def generate_real_demo(input_path: Path, output_dir: Path) -> dict[str, Path]:
    capture = cv2.VideoCapture(str(input_path))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open Breakfast Actions video: {input_path}")
    fps = capture.get(cv2.CAP_PROP_FPS) or 15.0
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    source_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    source_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    output_dir.mkdir(parents=True, exist_ok=True)
    clean_path = output_dir / "breakfast_cereals_clean.mp4"
    browser_path = output_dir / "breakfast_cereals_browser.mp4"
    annotated_path = output_dir / "breakfast_cereals_annotated.mp4"
    log_path = output_dir / "activity_log.json"
    jsonl_path = output_dir / "activity_log.jsonl"
    tracks_path = output_dir / "motion_tracks.jsonl"
    attribution_path = output_dir / "SOURCE_AND_LICENSE.json"
    writer = cv2.VideoWriter(
        str(annotated_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (1280, 720),
    )
    if not writer.isOpened():
        raise RuntimeError(f"Could not create real-data demo: {annotated_path}")
    clean_writer = cv2.VideoWriter(
        str(clean_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (source_width, source_height),
    )
    if not clean_writer.isOpened():
        raise RuntimeError(f"Could not create clean real-data video: {clean_path}")

    subtractor = cv2.createBackgroundSubtractorMOG2(
        history=90, varThreshold=24, detectShadows=True,
    )
    last_box: tuple[int, int, int, int] | None = None
    with tracks_path.open("w", encoding="utf-8") as track_stream:
        for frame_index in range(frame_count):
            ok, source = capture.read()
            if not ok:
                break
            segment = _segment_at(frame_index)
            clean_writer.write(source)
            last_box = _motion_box(subtractor, source, last_box)
            canvas = np.full((720, 1280, 3), (12, 12, 20), dtype=np.uint8)
            canvas[:, :960] = cv2.resize(source, (960, 720), interpolation=cv2.INTER_CUBIC)
            timestamp = frame_index / fps
            _draw_motion_track(canvas, last_box, segment.activity)
            _draw_panel(canvas, frame_index, timestamp, segment)
            writer.write(canvas)
            track_stream.write(json.dumps({
                "frame_index": frame_index,
                "timestamp": round(timestamp, 3),
                "source_label": segment.source_label,
                "mapped_activity": segment.activity,
                "actor_track": {
                    "track_id": 1,
                    "label": "actor_motion_region",
                    "bbox": list(last_box) if last_box else None,
                    "status": "inferred_motion_not_person_detector",
                },
            }, ensure_ascii=False) + "\n")

    capture.release()
    writer.release()
    clean_writer.release()
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-i", str(clean_path),
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(browser_path),
    ], check=True, capture_output=True)
    events = mapped_events(fps)
    write_activity_log(events, log_path, jsonl_path, {
        "dataset": "CVML-TueAI/Breakfast-Actions",
        "source_video": "videos/P03/cam01/P03_cereals.avi",
        "participant": "P03",
        "camera": "cam01",
        "fps": fps,
        "frames": frame_count,
        "annotation_type": "published temporal ground truth mapped to acai proxy",
        "motion_track": "anonymous inferred motion region; not identity or person detection",
    })
    attribution_path.write_text(json.dumps({
        "dataset": "Breakfast Actions",
        "queryable_release": "https://huggingface.co/datasets/CVML-TueAI/Breakfast-Actions",
        "official_release": "https://huggingface.co/datasets/Serrelab/breakfast-actions",
        "official_release_license_listing": "CC BY 4.0",
        "source_path": "videos/P03/cam01/P03_cereals.avi",
        "participant": "P03",
        "camera": "cam01",
        "note": "Verify the exact mirror provenance and terms before redistributing this video commercially.",
    }, indent=2), encoding="utf-8")
    return {
        "clean_video": clean_path,
        "browser_video": browser_path,
        "annotated_video": annotated_path,
        "activity_log": log_path,
        "activity_jsonl": jsonl_path,
        "motion_tracks": tracks_path,
        "source_and_license": attribution_path,
    }
