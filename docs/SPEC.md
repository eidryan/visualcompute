# VisualCompute — Product and Technical Specification

Status: prototype specification 0.1  
Reference workflow: quick-service açaí preparation  
Primary buyer: operations, loss prevention, quality, training, and franchise leadership

## 1. Product decision

Build an **order timeline engine**, not a generic employee-monitoring camera. Its unit of value is an order and its operational steps:

```text
POS order opens
  → container selected
  → base dispensed
  → modifiers added
  → contents mixed/finished
  → tray/bag assembled
  → customer handoff
POS order closes
```

Every event must answer:

- what happened;
- when it started and ended;
- which anonymous actor/object tracks were involved;
- which order it belongs to;
- confidence and observable evidence;
- whether a sensor or rule corroborated the camera.

A manager should be able to act on the output: adjust portions, fix a slow station, change a layout, retrain a step, or investigate repeated rework. Raw “minutes near equipment” without a decision path is not a product.

## 2. Narrow MVP promise

The first commercial pilot should answer only three questions:

1. How much does portion weight vary from the recipe by product and modifier?
2. Which preparation step creates cycle-time variation or queues?
3. Which prescribed steps are missing, repeated, or followed by rework?

The MVP does not promise identity, emotion, intent, food quality, exact grams from pixels, or automatic employee evaluation.

## 3. Reference activity ontology

| Activity | Entry condition | Exit condition | Useful metric |
|---|---|---|---|
| `approach_station` | anonymous worker track enters prep zone | container interaction begins | readiness delay |
| `pick_up_bowl` | container moves with worker/hand | container reaches scale/base zone | container selection time |
| `place_bowl_on_scale` | bowl overlaps scale zone | dispense begins | scale compliance |
| `dispense_acai` | bowl under dispenser plus motion/weight delta | flow/weight delta stops | base grams and duration |
| `retrieve_ingredient` | utensil/hand enters named bin | utensil leaves bin | search/layout time |
| `add_ingredient` | bin-to-bowl transfer | utensil exits bowl zone | topping grams/count |
| `mix_contents` | repeated utensil motion in bowl | motion stops | finishing duration |
| `place_on_tray` | bowl and tray overlap | tray begins handoff motion | assembly time |
| `handoff_order` | completed order crosses handoff zone | customer/order leaves | end-to-end cycle |
| `use_phone` | phone associated with worker in production zone | association ends | review-only exception |
| `idle` | no active step after a configured dwell | productive step begins | station idle time |

`use_phone` is intentionally optional and sensitive. It should only be enabled after a written purpose/necessity review and must not trigger discipline automatically.

### Object ontology

Core: `worker`, `customer`, `bowl`, `cup`, `tray`, `scoop`, `spoon`, `acai_dispenser`, `ingredient_bin`, `scale`, `phone`.

Ingredient identity should initially come from a fixed station zone or bin marker—not visual classification of visually similar toppings. The configuration maps a tracked bin to `banana`, `granola`, `chocolate`, `whey`, and so on.

## 4. Data contracts

### Frame-level perception stream

One JSON object per sampled frame:

```json
{
  "frame_index": 183,
  "timestamp": 12.2,
  "frame_period": 0.0667,
  "activity": "add_ingredient",
  "activity_confidence": 0.94,
  "activity_attributes": {"item": "granola"},
  "evidence": ["bin-to-bowl transfer", "scale delta +24 g"],
  "detections": [
    {"track_id": 1, "label": "worker", "confidence": 0.98, "bbox": [575, 234, 725, 529]},
    {"track_id": 7, "label": "bowl", "confidence": 0.95, "bbox": [551, 404, 659, 472], "attributes": {"order_id": "ORDER_0007"}},
    {"track_id": 22, "label": "ingredient_bin", "confidence": 0.95, "bbox": [476, 196, 630, 296], "attributes": {"item": "granola"}}
  ]
}
```

Bounding boxes use `[x1, y1, x2, y2]` pixels. Track IDs are local to a camera session and are not personal identifiers.

### Consolidated activity event

```json
{
  "event_id": "evt_008",
  "order_id": "ORDER_0007",
  "activity": "add_ingredient",
  "start": 12.2,
  "end": 14.2,
  "duration": 2.0,
  "confidence": 0.94,
  "actor_id": 1,
  "object_ids": [7, 14, 22],
  "attributes": {"item": "granola"},
  "evidence": ["bin-to-bowl transfer", "scale delta +24 g"],
  "status": "observed"
}
```

### POS and scale joins

POS event minimum:

```json
{"order_id":"ORDER_0007","opened_at":"...","sku":"CLASSIC_500","modifiers":["banana","granola"],"station_id":"S01"}
```

Scale event minimum:

```json
{"station_id":"S01","timestamp":"...","grams":374.2,"stable":true}
```

Associate an anonymous bowl track to the most recent open POS order at that station. Reconcile with explicit screen/KDS signals when available. Never infer the customer’s identity.

## 5. Model architecture

```text
RTSP camera
  → decode/sample (GStreamer/OpenCV)
  → object detector (custom RT-DETR or YOLO)
  → multi-object tracker (ByteTrack/BoT-SORT)
  → spatial features (zones, overlap, motion, proximity)
  → action head + temporal state machine
Scale/POS ───────────────────────────────────────┘
  → event debouncing and order association
  → JSONL/PostgreSQL + short review clips by exception
  → dashboard/API
```

### Why detector plus state machine

A detector recognizes nouns. “Adding granola” is a temporal relation among a worker, utensil, named bin, bowl, motion path, recipe, and optionally a weight delta. Persistent IDs provide continuity; zone rules and the action head provide verbs; the state machine enforces plausible order and suppresses flicker.

### Detector choices

- Prototype adapter: Ultralytics YOLO with custom weights, when licensing is acceptable.
- Production default to evaluate: RT-DETRv2/PaddleDetection or another commercially compatible implementation.
- Tracker: ByteTrack for simple fixed-camera scenes; BoT-SORT if occlusion/re-entry is common.
- Edge: OpenVINO on Intel, TensorRT/DeepStream on NVIDIA, or CPU-only low-FPS sampling for the first trial.

A generic COCO model can bootstrap `person`, `cell phone`, and some containers. It is not the final model.

## 6. Training data plan

### Stage A — public proxy

Use Breakfast Actions to validate temporal segmentation and initialize representations for `take_bowl`, pour/add, utensil handling, and stirring. Use fixed-view cameras first. Use CaptainCook4D for procedural order and error experiments. Do not use 50 Salads for commercial training without separate permission because of its non-commercial ShareAlike license.

### Stage B — staged target footage

Record 20–30 scripted sessions after written authorization:

- 5 camera/lighting/layout variants;
- 3–5 workers who volunteer for the capture;
- all bowl sizes and top 12 modifiers;
- normal, missing-step, repeated-step, spill/rework, phone, and occlusion cases;
- POS and scale ground truth;
- no customers, or actors with releases.

Target 6–10 hours of staged video for the first object/action prototype. Annotate 5,000–10,000 object frames and 1,000–2,000 temporal action segments. Active learning then selects uncertain real-pilot clips for review.

### Annotation layers

1. Station zones and camera calibration.
2. Object boxes and class.
3. Track continuity.
4. Temporal activity segments.
5. Order association.
6. Sensor evidence and exception type.

Use CVAT or Label Studio with a written ontology guide and dual review on at least 10% of labels.

## 7. Evaluation gates

Do not ship based only on detector mAP.

| Layer | Pilot gate |
|---|---|
| Object detection | mAP50 and per-class recall reported; bowl/bin/utensil recall ≥ 0.90 in target view |
| Tracking | IDF1 ≥ 0.85; ID switches per order reported |
| Activity segmentation | segment F1@0.5 ≥ 0.80 for the five core steps |
| Order timeline | ≥ 90% of orders have correct start/end and step sequence |
| Portion signal | mean absolute error comes from scale integration, not vision |
| Operations | agreed KPI improves versus two-week baseline |

Report performance separately by store, shift, lighting, occlusion, worker, and product. Averages can hide a failed camera angle.

## 8. Prototype execution

```bash
pip install -e ".[dev]"
visualcompute demo --output artifacts
```

The deterministic demo is a visual contract and sales aid. Its “predictions” are scenario-generated and must never be represented as target-store model accuracy.

To use frame predictions from a detector/action model:

```bash
visualcompute annotate store_clip.mp4 \
  --detections model_output.jsonl \
  --order-id ORDER_123 \
  --station-id SP_001 \
  --output artifacts/store_clip
```

## 9. Pilot schedule and acceptance

| Weeks | Deliverable | Exit criterion |
|---|---|---|
| 0–2 | discovery, layout, KPI and LGPD design | signed measurement and privacy plan |
| 3–4 | staged capture and annotation guide | representative footage and labels pass review |
| 5–7 | object model, tracking, zones | stable IDs and core-object recall gate |
| 8–9 | activity state machine, POS/scale join | order timeline works on held-out staged clips |
| 10–11 | one-store shadow deployment | no operational interruption; privacy controls verified |
| 12–14 | baseline vs assisted experiment | agreed KPI report and go/no-go decision |
| 15–16 | hardening buffer | production backlog and rollout economics |

## 10. Pricing hypothesis

Sell the pilot as a measured operational experiment, not open-ended AI research:

- discovery and data/privacy design: R$15k–R$30k;
- staged prototype: R$35k–R$70k;
- one-store integrated pilot: R$80k–R$180k depending on POS/scale access and hardware;
- production SaaS hypothesis: R$800–R$2,500 per station/month plus hardware/support.

Validate price against annualized, verified savings. A reasonable business case should show at least 3–5× expected annual value over recurring software cost.

## 11. Privacy and labor safeguards

- no facial recognition or biometric templates;
- no microphone;
- edge processing and event-only retention by default;
- raw video discarded unless a defined, short exception window applies;
- masking/exclusion zones for customer and break areas;
- employee notice, purpose limitation, access logs, deletion controls, and a channel to contest findings;
- Relatório de Impacto à Proteção de Dados Pessoais before production;
- human review before any adverse decision;
- explicit prohibition on productivity ranking from a single noisy metric.

Legal basis, legitimate-interest balancing, labor implications, controller/operator roles, retention, and international transfers require Brazilian counsel/DPO review.

## 12. Principal risks

| Risk | Consequence | Mitigation |
|---|---|---|
| Visual ambiguity between toppings | wrong modifier tag | identify fixed bin/zone; combine POS |
| Occlusion by worker/body | lost bowl/utensil | oblique overhead placement, two-stage tracking |
| Camera moved after installation | silent degradation | calibration marker and health alert |
| Treating vision as a scale | false portion claims | integrate a real load cell |
| Domain gap from public kitchen data | impressive lab, weak store | staged target capture and store-held-out tests |
| Employee mistrust | pilot rejection and legal exposure | co-design, strict purpose, no biometrics, review rights |
| YOLO licensing mismatch | commercial/legal risk | choose license before model implementation |
| Pilot measures everything | slow delivery, unclear ROI | three outcomes and five core activities first |

## 13. Success decision

Proceed to production only if the one-store pilot demonstrates:

- a reliable order timeline in target conditions;
- an operational intervention based on that timeline;
- verified savings or service improvement;
- acceptable privacy/labor review;
- deployment cost and support burden compatible with franchise-level unit economics.
