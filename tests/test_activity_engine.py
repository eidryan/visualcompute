from visualcompute.activity import event_at, summarize_events
from visualcompute.engine import map_detection_rows
from visualcompute.real_demo import mapped_events
from visualcompute.scenario import demo_events, detections_at


def test_demo_sequence_is_ordered_and_complete():
    events = demo_events()
    assert events[0].activity == "approach_station"
    assert events[-1].activity == "handoff_order"
    assert all(left.end <= right.start for left, right in zip(events, events[1:]))
    assert summarize_events(events)["cycle_time"] == 22.0


def test_event_lookup_respects_boundaries():
    events = demo_events()
    assert event_at(events, 5.2).activity == "dispense_acai"
    assert event_at(events, 14.3).activity == "mix_contents"
    assert event_at(events, 22.0) is None


def test_frame_predictions_are_collapsed_into_events():
    reference = demo_events()
    rows = []
    for frame in range(220):
        timestamp = frame / 10
        active = event_at(reference, timestamp)
        rows.append({
            "timestamp": timestamp,
            "frame_period": .1,
            "activity": active.activity if active else None,
            "activity_confidence": active.confidence if active else 0,
            "activity_attributes": active.attributes if active else {},
            "activity_object_ids": list(active.object_ids) if active else [],
            "evidence": list(active.evidence) if active else [],
            "detections": [item.to_dict() for item in detections_at(timestamp)],
        })
    mapped = map_detection_rows(rows, "ORDER_0007")
    assert [event.activity for event in mapped] == [event.activity for event in reference]
    assert mapped[5].attributes["item"] == "banana"
    assert mapped[5].object_ids == (7, 14, 21)
    assert mapped[7].attributes["item"] == "granola"
    assert mapped[-1].end == 22.0


def test_breakfast_ground_truth_maps_to_acai_proxy():
    events = mapped_events()
    assert [event.activity for event in events] == [
        "pick_up_bowl",
        "add_ingredient",
        "dispense_acai",
        "mix_contents",
    ]
    assert events[1].attributes["source_label"] == "pour_cereals"
    assert events[0].status == "source_annotation"
