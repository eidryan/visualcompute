from __future__ import annotations

import math
from dataclasses import dataclass

from .activity import ActivityEvent, Detection


@dataclass(frozen=True)
class Step:
    activity: str
    start: float
    end: float
    confidence: float
    objects: tuple[int, ...]
    attributes: dict[str, str]
    evidence: tuple[str, ...]


STEPS = (
    Step("approach_station", 0.0, 1.6, .97, (), {}, ("worker centroid entered prep_zone",)),
    Step("pick_up_bowl", 1.6, 3.2, .95, (7,), {}, ("worker #1 and bowl #7 converged", "bowl #7 began moving",)),
    Step("place_bowl_on_scale", 3.2, 4.8, .96, (7, 31), {}, ("bowl #7 overlaps scale #31",)),
    Step("dispense_acai", 4.8, 7.4, .94, (7, 30), {"item": "acai_base"}, ("bowl #7 below dispenser #30", "scale delta +312 g",)),
    Step("retrieve_ingredient", 7.4, 9.0, .92, (14, 21), {"item": "banana"}, ("scoop #14 left banana bin #21",)),
    Step("add_ingredient", 9.0, 10.8, .95, (7, 14, 21), {"item": "banana"}, ("bin-to-bowl transfer", "scale delta +38 g",)),
    Step("retrieve_ingredient", 10.8, 12.2, .93, (14, 22), {"item": "granola"}, ("scoop #14 left granola bin #22",)),
    Step("add_ingredient", 12.2, 14.2, .94, (7, 14, 22), {"item": "granola"}, ("bin-to-bowl transfer", "scale delta +24 g",)),
    Step("mix_contents", 14.2, 16.9, .91, (7, 14), {}, ("repeated scoop motion inside bowl #7",)),
    Step("place_on_tray", 16.9, 18.9, .96, (7, 11), {}, ("bowl #7 overlaps tray #11",)),
    Step("handoff_order", 18.9, 22.0, .97, (7, 11, 2), {}, ("order crossed handoff_zone", "customer #2 present",)),
)


def demo_events() -> list[ActivityEvent]:
    return [
        ActivityEvent(
            event_id=f"evt_{index:03d}",
            order_id="ORDER_0007",
            activity=step.activity,
            start=step.start,
            end=step.end,
            confidence=step.confidence,
            actor_id=1,
            object_ids=step.objects,
            attributes=step.attributes,
            evidence=step.evidence,
        )
        for index, step in enumerate(STEPS, 1)
    ]


def _lerp(a: float, b: float, amount: float) -> float:
    return a + (b - a) * max(0.0, min(1.0, amount))


def _box(cx: float, cy: float, width: int, height: int) -> tuple[int, int, int, int]:
    return (int(cx - width / 2), int(cy - height / 2), int(cx + width / 2), int(cy + height / 2))


def detections_at(timestamp: float) -> list[Detection]:
    worker_x = _lerp(190, 650, timestamp / 2.3) if timestamp < 2.3 else 650
    worker_y = 382
    bowl_x, bowl_y = 450, 465
    if timestamp >= 1.6:
        bowl_x = _lerp(450, 605, (timestamp - 1.6) / 2.0)
        bowl_y = _lerp(465, 438, (timestamp - 1.6) / 2.0)
    if timestamp >= 16.9:
        bowl_x = _lerp(605, 955, (timestamp - 16.9) / 4.2)
        bowl_y = _lerp(438, 475, (timestamp - 16.9) / 4.2)

    detections = [
        Detection(1, "worker", .98, _box(worker_x, worker_y, 150, 295), {"role": "crew"}),
        Detection(7, "bowl", .95, _box(bowl_x, bowl_y, 108, 68), {"order_id": "ORDER_0007"}),
        Detection(11, "tray", .96, _box(910, 487, 240, 92)),
        Detection(21, "ingredient_bin", .94, _box(368, 246, 154, 100), {"item": "banana"}),
        Detection(22, "ingredient_bin", .95, _box(553, 246, 154, 100), {"item": "granola"}),
        Detection(23, "ingredient_bin", .93, _box(738, 246, 154, 100), {"item": "chocolate"}),
        Detection(30, "acai_dispenser", .98, _box(605, 100, 175, 140)),
        Detection(31, "scale", .97, _box(605, 478, 205, 72)),
    ]
    if 7.4 <= timestamp < 16.9:
        if timestamp < 10.8:
            source_x = 368
        else:
            source_x = 553
        phase = (timestamp * 2.4) % 2.0
        amount = phase if phase <= 1.0 else 2.0 - phase
        scoop_x = _lerp(source_x, bowl_x, amount)
        scoop_y = _lerp(265, bowl_y - 35, amount)
        if timestamp >= 14.2:
            angle = timestamp * 8
            scoop_x = bowl_x + math.cos(angle) * 28
            scoop_y = bowl_y - 25 + math.sin(angle) * 13
        detections.append(Detection(14, "scoop", .91, _box(scoop_x, scoop_y, 86, 28)))
    if timestamp >= 18.9:
        customer_x = _lerp(1185, 1080, (timestamp - 18.9) / 2.2)
        detections.append(Detection(2, "customer", .96, _box(customer_x, 382, 145, 292)))
    return detections
