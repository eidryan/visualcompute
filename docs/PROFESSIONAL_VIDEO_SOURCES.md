# Professional Restaurant Video Sources

Research date: 29 July 2026

## Bottom line

There is no large, modern, openly licensed dataset that perfectly matches a fixed OAKBERRY-style assembly line with ingredient selection, bowl tracking, checkout context and customer handoff. The best strategy is a three-part evidence stack:

1. **UCF fast-food sandwich research video** for exact semantic precedent;
2. **free-use professional stock footage** for a polished, visually credible prototype;
3. **staged footage in a consenting real store** for the model and pilot.

The dashboard should remain outside the video. Store a clean source MP4, an event log and optional frame-level tracks; render the dashboard and boxes in HTML. This keeps source media reusable and lets the product change labels, models and explanations without re-encoding video.

## Tier 1 — closest semantic match

### UCF Monitoring Fast Food Production

- Page: https://www.crcv.ucf.edu/research/monitoring-fast-food-production/
- Video: https://www.crcv.ucf.edu/projects/FastFood/rr_iccv2001_seq2.mpg
- Setting: controlled fast-food sandwich assembly from a static camera.
- Actions: arms reach ingredient bins, pick up food, place it on the bread stack and assemble the sandwich.
- Value: this is almost exactly the VisualCompute problem statement and establishes that the problem has a research lineage.
- Weakness: 2001-era resolution and segmentation; the published video already contains research overlays.
- Rights: the page does not state a reusable media license. Treat it as internal research evidence and request permission before redistributing it in a customer deck or public demo.

The local suitability check found a 320×240, 25 fps, 46.6-second sequence. It is valuable for algorithm comparison, not for visual polish.

## Tier 2 — polished professional clips

The following Pexels pages describe the clips as free to use/download. Save the clip page, creator, download date and applicable Pexels license alongside every downloaded asset; re-check the terms before commercial publication.

### Fast-food line and order preparation

1. [People Working at a Fast Food Chain](https://www.pexels.com/video/people-working-at-a-fast-food-chain-3371015/)
   - Professional quick-service kitchen and counter.
   - Multiple staff preparing orders.
   - Best for queue, station occupancy, order assembly and handoff-zone tracking.

2. [People Preparing Food](https://www.pexels.com/video/people-preparing-food-3371016/)
   - Fast-paced restaurant kitchen.
   - Useful for worker/station tracking and concurrent activity.

3. [Chef Packs Crispy Fried Food](https://www.pexels.com/video/a-person-is-preparing-food-in-a-kitchen-4253728/)
   - Close professional-kitchen view of food placed in takeaway packaging.
   - Useful for container, portion and package-completion states.

### Bowl and ingredient assembly

4. [Professional Chef Preparing a Noodle Bowl](https://www.pexels.com/video/a-man-preparing-a-bowl-of-noodle-with-different-ingredients-3298230/)
   - Closest polished visual analogy to an açaí bowl.
   - Multiple ingredients are placed into one bowl.
   - Best source for `pick_up_bowl`, `retrieve_ingredient`, `add_ingredient` and `inspect_order`.

5. [Person Preparing Food in a Bowl](https://www.pexels.com/video/a-footage-of-a-person-preparing-food-on-a-bowl-8085282/)
   - Bowl, fruit, toppings and pouring.
   - Semantically close to açaí toppings, although not necessarily a commercial store.

6. [Street-Food Preparation in a Stainless Bowl](https://www.pexels.com/video/vibrant-street-food-preparation-in-stainless-steel-bowl-37296032/)
   - Gloved hands and vigorous mixing in a professional food context.
   - Good proxy for `mix_contents`.

### Handoff

7. [Food and Drink Prepared on a Tray and Served to a Customer](https://www.pexels.com/video/foods-and-drink-prepared-on-a-tray-served-to-a-customer-3044155/)
   - Explicit tray completion and customer handoff.
   - Best visual source for `place_on_tray` and `handoff_order`.

A set made from clips 1, 4 and 7 covers line operation, bowl assembly and handoff. It is not one continuous order, so the UI must identify each clip as a separate source/session.

## Tier 3 — professional or richer datasets

### Chinese Commercial Kitchen Manipulation Dataset Preview

- Page: https://huggingface.co/datasets/nova-dynamics/Chinese_Commercial_Kitchen_Manipulation_Dataset_Preview
- Real operating commercial restaurant and a professional chef with about 20 years of experience.
- Side, overhead, egocentric and RGB-D views.
- Public sample tasks: vegetable cutting and wok stir-fry.
- Strong professional-domain data, but weak match for cold assembly/handoff.
- The publisher requests contact for evaluation/full data. Confirm licensing and commercial rights directly.

### MOMA

- Page: https://moma.stanford.edu/
- Includes a `dining service` activity with taking orders, serving food/wine and cleaning.
- Rich actor/object/relationship annotations.
- Helpful for front-of-house service and handoff relationships, not for bowl preparation.

### COM Kitchens

- Paper: https://arxiv.org/abs/2408.02272
- 145 unedited fixed-view videos, 70 kitchens, 40 hours and visual action graphs.
- Overhead counter coverage and grounded actions are technically useful.
- Not a professional restaurant dataset, but camera geometry is closer to a deployable counter system than egocentric footage.

### YouCook2

- Page: https://youcook2.eecs.umich.edu/
- 2,000 third-person cooking videos across 89 recipes with temporally bounded procedure descriptions and object boxes.
- Useful for representation learning and temporal procedure models.
- Videos originate from YouTube and are generally domestic/unconstrained; availability and reuse must be checked per source.

## Sources to avoid as a commercial demo

- Brand training or kitchen videos copied from YouTube without permission.
- Franchise CCTV leaks or employee/customer recordings.
- 50 Salads for proprietary/commercial training without separate permission because of its non-commercial ShareAlike terms.
- Vendor product demos downloaded and presented as VisualCompute output.
- Stock clips whose free tier is restricted to personal use; for example, some Mixkit items use a Restricted License even when the page offers a free download.

## Recommended next demo pack

```text
professional-demo/
  clips/
    01_fast_food_line.mp4
    02_bowl_assembly.mp4
    03_tray_handoff.mp4
  sessions/
    01_fast_food_line.activity.json
    02_bowl_assembly.activity.json
    03_tray_handoff.activity.json
  tracks/
    01_fast_food_line.tracks.jsonl
    02_bowl_assembly.tracks.jsonl
    03_tray_handoff.tracks.jsonl
  index.html
  SOURCES_AND_LICENSES.json
```

The HTML viewer should switch sessions, play the clean MP4, synchronize activity events, and render optional boxes as a canvas layer. Source annotations, human review and model inference must use visibly different status labels.

## Labeling approach for unannotated stock footage

For each short clip:

1. mark clip-level source and license;
2. manually segment the visible steps in CVAT or a simple JSON editor;
3. label only observable activities;
4. run person/object detection and tracking separately;
5. store `annotation_source` per event: `human_review`, `source_ground_truth` or `model_inference`;
6. never assign model confidence to a human-authored event;
7. use the clips as UX and pipeline validation—not as evidence of target-store accuracy.

## Production capture remains necessary

Stock footage is excellent for the pitch and UI. It cannot establish accuracy in OAKBERRY lighting, camera angle, bowls, bins, uniforms, recipes, occlusions or pace. The decisive dataset remains a consented, staged capture at one target station with scale and POS ground truth.
