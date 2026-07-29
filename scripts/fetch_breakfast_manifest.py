"""Build a VisualCompute training manifest from Hugging Face's dataset API.

This fetches metadata and temporal labels, not the large video payloads. It keeps
the data-acquisition step auditable and lets a reviewer inspect the açaí-proxy
mapping before downloading or training on footage.
"""

from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API = "https://datasets-server.huggingface.co/rows"
DATASET = "CVML-TueAI/Breakfast-Actions"
ACTIVITY_ALLOWLIST = {"cereals", "milk", "coffee", "tea", "salat"}
CAMERA_PRIORITY = {"webcam01": 0, "webcam02": 1, "cam01": 2, "stereo": 3}

LABEL_MAP = {
    "take_bowl": ("pick_up_bowl", {}),
    "take_cup": ("pick_up_bowl", {"container_type": "cup"}),
    "pour_cereals": ("add_ingredient", {"item": "dry_topping_proxy"}),
    "spoon_powder": ("add_ingredient", {"item": "powder_topping_proxy"}),
    "pour_milk": ("dispense_acai", {"item": "liquid_base_proxy"}),
    "pour_coffee": ("dispense_acai", {"item": "liquid_base_proxy"}),
    "pour_water": ("dispense_acai", {"item": "liquid_base_proxy"}),
    "add_teabag": ("add_ingredient", {"item": "packaged_ingredient_proxy"}),
    "stir_milk": ("mix_contents", {}),
    "stir_coffee": ("mix_contents", {}),
    "stir_tea": ("mix_contents", {}),
    "cut_fruit": ("retrieve_ingredient", {"item": "fruit_proxy"}),
    "put_fruit2bowl": ("add_ingredient", {"item": "fruit_proxy"}),
}


def _get_page(split: str, offset: int, length: int) -> dict[str, Any]:
    query = urllib.parse.urlencode({
        "dataset": DATASET,
        "config": "default",
        "split": split,
        "offset": offset,
        "length": length,
    })
    request = urllib.request.Request(
        f"{API}?{query}",
        headers={"User-Agent": "visualcompute/0.1 dataset-manifest"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def _activity(video_name: str) -> str:
    for activity in ACTIVITY_ALLOWLIST:
        if activity in video_name.lower():
            return activity
    return "other"


def _map_segment(segment: dict[str, Any]) -> dict[str, Any] | None:
    source_label = str(segment["label"])
    if source_label == "SIL" or source_label not in LABEL_MAP:
        return None
    target, attributes = LABEL_MAP[source_label]
    return {
        "start_frame": int(segment["start"]),
        "end_frame": int(segment["end"]),
        "source_label": source_label,
        "target_activity": target,
        "attributes": attributes,
        "mapping_strength": "proxy",
    }


def build_manifest(split: str, limit: int, page_size: int = 100) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    offset = 0
    while len(records) < limit:
        payload = _get_page(split, offset, min(page_size, limit - len(records)))
        page = payload.get("rows", [])
        if not page:
            break
        for wrapped in page:
            row = wrapped.get("row", wrapped)
            video_name = str(row.get("video", row.get("video_path", "")))
            activity = _activity(video_name)
            if activity == "other":
                continue
            labels = [_map_segment(item) for item in row.get("labels", [])]
            labels = [item for item in labels if item]
            if not labels:
                continue
            records.append({
                "dataset": DATASET,
                "license_review": "verify upstream terms before training",
                "split": split,
                "participant": row.get("participant"),
                "camera": row.get("camera"),
                "camera_rank": CAMERA_PRIORITY.get(str(row.get("camera")), 99),
                "video_path": row.get("video_path"),
                "video": row.get("video"),
                "source_activity": activity,
                "fps": 15,
                "segments": labels,
            })
            if len(records) >= limit:
                break
        offset += len(page)
    return sorted(records, key=lambda item: (item["camera_rank"], item["source_activity"], str(item["video_path"])))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="s1", choices=("s1", "s2", "s3", "s4"))
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--output", type=Path, default=Path("data/breakfast_manifest.jsonl"))
    args = parser.parse_args()
    manifest = build_manifest(args.split, args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        for row in manifest:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Wrote {len(manifest)} mapped records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
