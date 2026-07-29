# VisualCompute

Computer-vision prototype for mapping quick-service preparation workflows into an auditable activity log. The first reference workflow is an OAKBERRY-style açaí station: pick up a bowl, dispense base, add ingredients, mix, place on a tray, and hand off the order.

The demo produces two synchronized outputs:

1. an annotated MP4 with persistent object IDs and live action labels;
2. a machine-readable JSON activity log with timestamps, confidence, actor/object IDs, and evidence.

Example overlay:

```text
#01 WORKER · ADDING GRANOLA · 94%
#07 BOWL · ORDER_0007
#22 GRANOLA BIN
ACTIVE STEP 06/09 · add_ingredient · 00:12.4
```

> This repository is a product and technical prototype, not an employee-surveillance system. The proposed deployment avoids facial recognition and audio, processes video at the edge, keeps only operational events by default, and requires an LGPD review before a real pilot.

## Why this prototype

A camera should answer **who/what/when**; a scale should answer **how many grams**; the POS should answer **what was ordered**. Combining those signals can reveal rework, missed steps, portion variance, queue delays, and training opportunities. Video alone should not be presented as a reliable gram-scale measurement system.

```text
Camera → detection/tracking → station state machine ┐
Scale  → weight events ─────────────────────────────┼→ order timeline → dashboard/alerts
POS    → order and modifiers ───────────────────────┘
```

## Quick start

Requires Python 3.11+ and FFmpeg-compatible OpenCV codecs.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
visualcompute demo --output artifacts
```

The command generates:

- `artifacts/demo_input.mp4` — deterministic synthetic station footage;
- `artifacts/demo_annotated.mp4` — the sales-demo overlay;
- `artifacts/activity_log.json` — order summary and mapped activities;
- `artifacts/activity_log.jsonl` — one event per line.

Open `viewer/index.html`, select the annotated video and JSON log, and the timeline will follow video playback.

## Process a real video

The prototype accepts a normalized detection stream so a detector can be changed without changing the activity engine:

```bash
visualcompute annotate footage.mp4 \
  --detections detections.jsonl \
  --output artifacts/real_run
```

Each detection line is a JSON object:

```json
{"timestamp": 3.2, "detections": [{"track_id": 7, "label": "bowl", "confidence": 0.93, "bbox": [540, 380, 650, 475]}]}
```

Run the included Ultralytics YOLO + ByteTrack exporter with the optional dependency:

```bash
pip install -e ".[yolo]"
visualcompute yolo-track footage.mp4 \\
  --output artifacts/real_run/yolo_tracks.jsonl \\
  --model yolo11n.pt --confidence 0.15
```

Every row records the actual model name, tracker, frame index, bounding boxes, COCO class, confidence, and session-local track ID. Load the JSONL beside the clean video in `viewer/synced_dashboard.html` to render labels such as `#07 BOWL 83%`.

A generic COCO model is useful for people, bowls and cups but will not reliably recognize açaí utensils, ingredient bins, order states, or actions; those require labeled station footage and a separate action/state layer. The dashboard intentionally keeps detector output and activity evidence separate.

## Activity ontology

The first model logs nine customer-visible preparation states:

| # | Activity | Main evidence |
|---|---|---|
| 1 | `approach_station` | worker enters preparation zone |
| 2 | `pick_up_bowl` | bowl becomes associated with worker |
| 3 | `place_bowl_on_scale` | bowl overlaps scale zone |
| 4 | `dispense_acai` | bowl remains below dispenser |
| 5 | `retrieve_ingredient` | utensil moves from an ingredient bin |
| 6 | `add_ingredient` | utensil/bin-to-bowl transfer |
| 7 | `mix_contents` | repeated utensil motion inside bowl |
| 8 | `place_on_tray` | bowl overlaps a tracked tray |
| 9 | `handoff_order` | completed order crosses handoff zone |

See [docs/SPEC.md](docs/SPEC.md) for schemas, rules, model plan, evaluation, risks, and delivery schedule. See [docs/DATASETS.md](docs/DATASETS.md) for the public-data strategy and label mapping. See [docs/MARKET_RESEARCH.md](docs/MARKET_RESEARCH.md) for positioning, competition, pricing, LGPD safeguards, and an OAKBERRY pilot pitch.

## Dataset choice

The recommended public starting point is **Breakfast Actions**: fixed multi-camera kitchen footage, 52 participants, 18 kitchens, ten preparation activities, and 48 fine-grained action units. Bowl/cup retrieval, pouring, ingredient handling, and stirring are the closest public proxies to an açaí line. **CaptainCook4D** complements it with procedural-step and error annotations. **50 Salads** is useful only as a research benchmark because its non-commercial ShareAlike license is unsuitable for commercial training without separate permission.

Public datasets validate the pipeline and bootstrap action representations. They do not replace a consented, staged dataset from the target store layout.

## Repository map

```text
src/visualcompute/     activity model, renderer, CLI and synthetic scenario
configs/               station ontology and normalized zones
viewer/                local synchronized video/log viewer
docs/                  product, market and data specifications
tests/                 deterministic engine tests
.github/workflows/     CI and generated demo artifact
```

## Recommended pilot

A credible first pilot is one station, one overhead/oblique camera, one connected scale, and POS order events. Limit the promise to three measurable outcomes:

- portion variance by product/modifier;
- preparation time and bottleneck by step;
- missing/repeated steps and rework rate.

Run a two-week baseline and a four-week assisted phase. Agree on target savings before development and treat automatic findings as operational evidence for review—not automatic disciplinary decisions.

## Sources

- [OAKBERRY franchising](https://www.oakberry.com/pt-BR/seja-um-franqueado)
- [Breakfast Actions dataset](https://huggingface.co/datasets/Serrelab/breakfast-actions)
- [CaptainCook4D](https://captaincook4d.github.io/captain-cook/)
- [LGPD](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm)
- [ANPD legitimate-interest guidance](https://www.gov.br/anpd/pt-br/assuntos/noticias/anpd-lanca-guia-orientativo-sobre-legitimo-interesse)
