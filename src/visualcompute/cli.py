from __future__ import annotations

import argparse
from pathlib import Path

from .activity import load_events, write_activity_log
from .annotate import annotate_video
from .demo import generate_demo
from .engine import map_detection_rows, read_detection_rows


def _demo(args: argparse.Namespace) -> int:
    outputs = generate_demo(Path(args.output))
    for name, path in outputs.items():
        print(f"{name}: {path}")
    return 0


def _annotate(args: argparse.Namespace) -> int:
    input_path = Path(args.video)
    detections_path = Path(args.detections)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_detection_rows(detections_path)
    events = load_events(Path(args.events)) if args.events else map_detection_rows(rows, args.order_id)
    annotated = output_dir / "annotated.mp4"
    log_path = output_dir / "activity_log.json"
    annotate_video(input_path, annotated, rows, events)
    write_activity_log(events, log_path, output_dir / "activity_log.jsonl", {
        "video": annotated.name,
        "source_video": input_path.name,
        "station_id": args.station_id,
    })
    print(f"annotated_video: {annotated}")
    print(f"activity_log: {log_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="visualcompute",
        description="Map quick-service preparation video into annotated footage and activity logs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo", help="Generate a complete synthetic açaí workflow demo")
    demo.add_argument("--output", default="artifacts")
    demo.set_defaults(func=_demo)

    annotate = subparsers.add_parser("annotate", help="Render detections and mapped activities over a video")
    annotate.add_argument("video")
    annotate.add_argument("--detections", required=True, help="Frame-level JSONL detection/action stream")
    annotate.add_argument("--events", help="Optional pre-built activity log JSON")
    annotate.add_argument("--output", default="artifacts/annotated")
    annotate.add_argument("--order-id", default="ORDER_UNKNOWN")
    annotate.add_argument("--station-id", default="station_unknown")
    annotate.set_defaults(func=_annotate)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
