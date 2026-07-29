# Dataset Strategy

Research date: 28 July 2026

## Recommendation

Use **Breakfast Actions** as the public-data backbone for the first prototype, **CaptainCook4D** as a secondary procedural/error source, and a **staged synthetic açaí dataset** as the decisive target-domain dataset.

This is not a claim that breakfast footage equals an OAKBERRY station. It is the closest practical public bridge for fixed-camera container selection, pouring, ingredient transfer, utensil use, and stirring. The final model must be tested and tuned on authorized footage from the target layout.

## 1. Breakfast Actions — primary public proxy

Official release: [Serre Lab / Brown University](https://huggingface.co/datasets/Serrelab/breakfast-actions)  
Queryable release: [CVML-TueAI/Breakfast-Actions](https://huggingface.co/datasets/CVML-TueAI/Breakfast-Actions)

Published characteristics:

- 52 participants;
- 18 kitchens;
- approximately 77 hours and more than four million frames;
- 320×240 at 15 fps;
- ten preparation activities and 48 fine-grained action units;
- multiple fixed camera views;
- Serre Lab release is listed as CC BY 4.0.

The queryable release exposes 1,989 rows across four splits and fields including participant, camera, video path, and frame-range labels. Confirm the terms and provenance of the exact release before training or redistribution.

### Strongest source activities

| Source activity | Relevant source labels | Açaí proxy |
|---|---|---|
| cereals | `take_bowl`, `pour_cereals`, `pour_milk` | bowl, dry topping, base dispense |
| milk | `take_cup`, `spoon_powder`, `pour_milk`, stir | container, powder topping, dispense, mix |
| coffee | `take_cup`, `pour_coffee`, `pour_milk`, stir | container, liquid transfer, mix |
| tea | `take_cup`, `add_teabag`, `pour_water`, stir | packaged modifier, transfer, mix |
| fruit salad (`salat`) | `cut_fruit`, `take_bowl`, fruit-to-bowl action | fruit handling and bowl assembly |

### Explicit label map

| Breakfast label | VisualCompute activity | Strength | Note |
|---|---|---:|---|
| `take_bowl` | `pick_up_bowl` | strong | same container interaction |
| `take_cup` | `pick_up_bowl` | medium | same verb, different container |
| `pour_cereals` | `add_ingredient` | strong | dry ingredient into container |
| `spoon_powder` | `add_ingredient` | strong | utensil-mediated powder addition |
| `pour_milk` | `dispense_acai` | medium | liquid/base transfer, different viscosity |
| `pour_coffee` | `dispense_acai` | medium | liquid/base transfer |
| `add_teabag` | `add_ingredient` | medium | packaged ingredient placement |
| `stir_milk` / `stir_coffee` / `stir_tea` | `mix_contents` | strong | repeated utensil motion |
| `cut_fruit` | `retrieve_ingredient` | weak | useful hand/fruit features, not same step |
| fruit-to-bowl | `add_ingredient` | strong | same spatial relation |

Not covered: scale placement, tray assembly, customer handoff, phone use, specific OAKBERRY equipment, and exact ingredient identity.

### Get a reviewable manifest

The repository includes a metadata importer that queries Hugging Face’s dataset API and writes only relevant rows and mapped temporal labels:

```bash
python scripts/fetch_breakfast_manifest.py \
  --split s1 \
  --limit 50 \
  --output data/breakfast_manifest.jsonl
```

The output is deliberately a manifest, not an automatic bulk video download. Review camera, labels, source terms, and sample suitability before incurring bandwidth/storage or beginning training. `configs/breakfast_to_acai.yaml` is the human-readable mapping authority.

Recommended selection order:

1. `webcam01` and `webcam02` fixed views;
2. cereals and milk sequences;
3. coffee/tea for stirring and liquid transfer;
4. fruit salad for fruit/container interaction;
5. balance participants and kitchens across train/validation/test;
6. never put different camera views of the same performance into both train and test.

## 2. CaptainCook4D — secondary procedural/error source

Official project: [CaptainCook4D](https://captaincook4d.github.io/captain-cook/)

Published characteristics include 94.5 hours, 384 recordings, 5.3k step annotations, and 10k fine-grained action annotations. It contains both normal execution and procedural errors and is distributed under Apache 2.0 according to the project site.

Useful contribution:

- learn representations for taking, placing, pouring, mixing, and measuring;
- design the exception taxonomy: omitted step, repeated step, wrong order, wrong quantity, wrong tool;
- test temporal models against explicit recipe order;
- use “butter corn cup” and other cup assembly tasks as quick-service proxies.

Limitation: it is primarily egocentric/4D cooking data. It is not a direct substitute for a fixed CCTV-like store view.

## 3. 50 Salads — benchmark only

Dataset record: [University of Dundee](https://discovery.dundee.ac.uk/en/datasets/50-salads/)

It provides RGB-D salad preparation by 25 people with annotated manipulative gestures and is semantically close to ingredient-to-bowl assembly. Its CC BY-NC-SA license makes it inappropriate for commercial training or a proprietary customer deliverable without separate permission. Keep it out of the production dataset pipeline; it may be used for non-commercial research comparisons under its terms.

## 4. Other useful but non-primary data

- EPIC-KITCHENS: broad kitchen action pretraining, mostly egocentric and large.
- Ego4D: general activity representation and hand-object interaction, weakly matched to fixed stations.
- Nutrition5k: ingredients and mass of finished food, useful for portion research but not temporal preparation actions.
- Synthetic/staged footage: fastest path to exact bowls, trays, bins, uniforms, overlays, and exception cases.

## 5. Target-domain capture specification

### Camera

- fixed oblique-overhead view, 1080p, 15–30 fps;
- hands, bowl, dispenser, bins, scale and tray visible;
- no break area, POS PIN pad, or unnecessary customer area;
- locked focus/exposure where possible;
- calibration marker and versioned zone configuration.

### Scripted order matrix

Record at least:

- 3 bowl sizes;
- 12 high-volume topping/modifier combinations;
- one and two-person station operation;
- daytime/night lighting;
- normal pace and rush pace;
- missing topping, repeated topping, wrong order, rework, spill, utensil change, occlusion and interruption;
- tray and takeaway/bag variants;
- customer handoff using actors.

### Ground truth

For each order capture:

- POS SKU/modifiers and open/close times;
- stable scale readings before/after base and every topping;
- manually reviewed action boundaries;
- object tracks for bowl, tray and utensil;
- camera/store/config version;
- whether each step is correct, omitted, repeated or uncertain.

### Splitting policy

A real generalization test holds out at least one worker, one capture session, and preferably one store/camera layout. Random frame splits cause leakage and misleading accuracy.

## 6. Training progression

1. Run the deterministic repository demo to confirm the data and UX contract.
2. Import and inspect 50 Breakfast Actions sequences.
3. Train/evaluate temporal segmentation on public labels.
4. Record staged açaí footage and train target object classes.
5. Fine-tune action features using the exact station zones and objects.
6. Add scale/POS events and evaluate complete order timelines.
7. Shadow-deploy; collect only uncertain/exception clips under the approved retention policy.
8. Retrain through active learning and re-test on held-out stores.

## 7. Data governance checklist

Before any target footage is collected:

- define controller/operator roles and purpose;
- obtain store authorization and employee/actor notices or releases as applicable;
- prohibit face recognition and audio in configuration;
- specify storage location, encryption, access and deletion;
- document retention for raw clips, annotations, embeddings and events separately;
- confirm dataset licenses and attribution requirements;
- prohibit uploading customer or employee footage to third-party labeling/model services without approval;
- maintain a lineage record from source clip to training run and model version.
