# Market Research and Go-to-Market

Research date: 28 July 2026

## Executive answer

This is a viable category, but the winning product is not “YOLO watches employees.” Existing companies prove demand for restaurant computer vision; they also prove that generic surveillance is crowded and sensitive. The strongest wedge is:

> **Turn each order into a verified preparation timeline, combining the camera, scale and POS to reduce portion variance, bottlenecks and rework—without identifying employees or customers.**

For OAKBERRY, sell a one-station operational experiment tied to food cost and throughput. Do not ask the company to finance an undefined model. Arrive with the generated overlay, an event log, a measurement plan, the public-data bridge, and a fixed-price discovery/pilot proposal.

## Why OAKBERRY is a credible design partner

OAKBERRY’s franchising page describes a highly standardized, fast preparation model and reports more than 850 stores in 55 countries and 2.8 million bowls per month. The company’s US integration with Qu covers POS, KDS, open APIs, and edge computing, showing that operational integration and store-edge infrastructure are not foreign concepts. In June 2026, OAKBERRY’s Latam Operations Director publicly discussed using AI to forecast franchisee demand from weather, history, and weekday data. These signals make an operations-data pilot strategically legible.

The business case is multiplicative:

```text
verified saving per bowl × bowls per store × stores × operating days
```

Example only—not a claim about OAKBERRY economics:

- 180 bowls/store/day;
- R$0.18 verified reduction in avoidable base/topping variance;
- 30 pilot stores;
- 360 days;

Annualized gross saving: `180 × 0.18 × 30 × 360 = R$349,920`, before throughput/rework value. Replace every assumption with POS, recipe and scale data during discovery.

## What the buyer can do with the data

| Finding | Operational decision | Money path |
|---|---|---|
| Base/topping weight varies by shift | recalibrate dispenser, recipe or training | lower food cost |
| One modifier creates repeated search motion | move bin/utensil | lower cycle time |
| Orders stall between scale and handoff | change tray/KDS/handoff layout | greater peak throughput |
| Frequent missing or repeated step | improve KDS prompt and coaching | less rework/refund |
| Demand pattern plus step duration | adjust staffing/station readiness | labor efficiency |
| Equipment interaction/idle anomaly | preventative maintenance review | uptime and fewer lost sales |

A dashboard without an intervention owner is not success. Every reported KPI should name the role that can change it.

## Competitive landscape

| Company/product | Apparent focus | Implication for VisualCompute |
|---|---|---|
| [PreciTaste](https://precitaste.com/) | restaurant operations, demand and food preparation intelligence | validates large-chain demand; compete with a narrow, faster pilot |
| [Kwali](https://www.kwali.ai/) | AI video for QSR execution, speed and quality | closest positioning overlap; differentiate through open event schema and camera+scale+POS |
| [Berry AI](https://www.berry-ai.com/) | restaurant video analytics, speed/service/operations | general restaurant analytics competitor |
| [alwaysAI](https://alwaysai.co/solutions/restaurants) | configurable edge computer vision for restaurants | platform/implementation alternative |
| [TraySense](https://traysense.ai/) | tray/order recognition and analytics | validates order-object tracking |
| [OpenVector](https://www.openvector.com/) | restaurant operational video intelligence | another category validator |
| [FoodVizion](https://foodvizion.com/) | food-service video analytics and loss control | overlaps compliance/loss framing |
| [Intel Order Accuracy](https://docs.openedgeplatform.intel.com/dev/edge-ai-suites/ai-suite-retail/order-accuracy/index.html) | reference architecture for order accuracy at the edge | useful architecture benchmark, not necessarily direct vendor |
| [NoWaste Brasil](https://nowastebrasil.com/) | food-waste management and measurement | adjacent partner/competitor for savings budget |

The absence of a household-name product specifically for açaí assembly is not proof of a hidden monopoly. It reflects hard domain adaptation, integration, privacy, unit economics, and support at store scale. Those are the real moats.

## Best pitch structure

### Central sentence

> Hoje vocês sabem o que foi vendido; o piloto mostra como cada pedido foi preparado, onde houve variação e qual ação operacional pode recuperar margem.

### 45-second spoken pitch

> “Eu montei um protótipo que transforma o preparo de cada bowl em uma linha do tempo: pegou o bowl, colocou na balança, serviu a base, adicionou banana e granola, misturou e entregou. A câmera gera os IDs e os tempos; a balança confirma gramas; o POS informa a receita. A proposta não usa reconhecimento facial e não é para punir funcionário. É para medir três perdas que a operação consegue corrigir: variação de porção, gargalo por etapa e retrabalho. Em vez de pedir que vocês apostem num software pronto, proponho duas semanas de diagnóstico e uma demonstração com imagens autorizadas. Se os dados mostrarem economia suficiente, partimos para um piloto de uma estação com meta financeira previamente combinada.”

### Five-slide meeting flow

1. **The leak:** a small per-bowl variance becomes material at network volume.
2. **See one order:** play the 22-second annotated video; click an event in the synchronized log.
3. **From pixels to action:** camera + scale + POS and the nine-step state machine.
4. **Decision and ROI:** three KPIs, two-week baseline, assisted phase, agreed savings equation.
5. **Safe pilot:** one station, no faces/audio, fixed scope, schedule, price, success gate.

Do not lead with YOLO, model architecture, employee phone detection, or the number of possible tags. Lead with the operational decision and measurable value.

## What to show

The repository demo is designed for the first meeting:

- persistent `#01 worker`, `#07 bowl`, `#22 granola bin` IDs;
- live label such as `ADDING INGREDIENT: GRANOLA`;
- current order, step number, elapsed time and confidence;
- colored activity timeline;
- JSON evidence including scale deltas;
- synchronized viewer that jumps to any event.

Be explicit that the included video is synthetic. It demonstrates the desired product contract, not trained accuracy.

### May you record people in a gym/store to make the example?

Do not secretly record identifiable employees, customers or gym users. “Anonymous IDs” drawn on top do not make the original footage anonymous; people can remain identifiable from face, body, uniform, tattoos, time and location. A safer sales demo uses:

1. the repository’s synthetic scenario;
2. staged footage with actors and written releases;
3. a closed store outside operating hours;
4. a customer-supplied clip under a written pilot/data agreement;
5. masking at capture/edge, with no audio and short retention.

Obtain Brazilian privacy/labor advice for the exact context. The [LGPD](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm), [ANPD legitimate-interest guidance](https://www.gov.br/anpd/pt-br/assuntos/noticias/anpd-lanca-guia-orientativo-sobre-legitimo-interesse), and [ANPD RIPD guidance](https://www.gov.br/anpd/pt-br/canais_atendimento/agente-de-tratamento/relatorio-de-impacto-a-protecao-de-dados-pessoais-ripd) are starting points, not a substitute for counsel.

## Who to approach

### Publicly identifiable entry points

Verify current role immediately before outreach:

- **Alejandro Veiga — Director of Operations, OAKBERRY Latin America.** Highest-fit business sponsor: he publicly discussed applied AI and operational data in June 2026.
- **Georgios Frangulis — founder and CEO.** Executive sponsor, but usually not the best cold first contact unless a warm introduction exists.
- **Carlos Alberto Brito Soares — operations/expansion leadership in the Pará production operation.** Relevant for industrial automation/supply applications; less direct for the first store-line pilot.
- **Everton Alves — publicly listed in franchise/real-estate expansion leadership.** Useful route to franchise network economics and pilot-store selection.

Public directories also list Brazil franchise operations, training/quality, data, finance, legal and expansion staff, but directory titles can be stale. Search the company’s current LinkedIn employees before using a name.

### Buying committee by role

| Role | Why they care | Ask |
|---|---|---|
| Latam/Brazil Operations Director | speed, standardization, rollout | sponsor a one-station discovery |
| Franchise Operations Manager | franchisee economics, execution variance | nominate two representative stores |
| Training & Quality leader | missed steps and coaching | validate ontology and interventions |
| Food Cost/Finance | verified margin impact | supply recipe/COGS ranges and ROI gate |
| Technology/Data/POS owner | integration and security | provide sandbox event contract |
| Legal/DPO/HR | LGPD and labor safeguards | approve capture/retention plan |
| Franchisee/operator | daily feasibility | host baseline and assisted phases |

The most effective route is multi-threaded: one operations sponsor, one store operator, and one technical/privacy reviewer.

## Outreach sequence

### First message

> Oi, Alejandro. Vi sua fala sobre IA aplicada à previsão e à operação da rede. Construí um protótipo que transforma o preparo de um bowl em uma linha do tempo anônima — bowl, base, topping, mistura e entrega — combinando câmera, balança e POS. O objetivo é medir variação de porção, gargalo e retrabalho, não avaliar pessoas. Posso te mandar um vídeo de 22 segundos e uma proposta de diagnóstico de uma estação? Se não for sua pauta, quem lidera excelência operacional/tecnologia nas lojas do Brasil?

### If no one answers

Do not repeat the same “quer conhecer?” message indefinitely. Use five distinct touches over 15–20 business days:

1. warm introduction from the existing contact, franchisee, POS/vendor, or industry peer;
2. short LinkedIn note with one relevant observation;
3. email with a 22-second demo and one-page pilot—not a large deck;
4. follow-up with a concrete value hypothesis and request to correct it;
5. courteous close-the-loop message asking for the correct owner.

Example value follow-up:

> “Fiz uma conta ilustrativa: R$0,18 de variação evitável × 180 bowls/dia já daria ~R$11,7 mil/ano por loja. Não estou assumindo que esses são os números de vocês; queria validar se porção, tempo por etapa ou retrabalho é a dor economicamente relevante. Se nenhuma for, eu encerro a hipótese.”

If there is still no response:

- interview 10–15 franchisees/operators in adjacent brands;
- offer a paid or low-cost staged discovery to one owner-operated store;
- publish the synthetic demo and a technical case study;
- partner with scale, POS/KDS, CCTV installer, food-cost consultant, or franchise-operations firm;
- use ABF and foodservice events for warm conversations;
- improve evidence, not message volume.

Do not scrape or spam personal contacts. A non-response is market information: the pain, buyer, credibility, timing, or channel may be wrong.

## Pilot offer

### Phase 1 — paid diagnostic

Two weeks, fixed scope:

- map one store/station and recipes;
- analyze POS and weight availability;
- record only staged/authorized examples;
- configure the nine-step ontology;
- deliver synthetic/staged overlay, event log, privacy design, and ROI model;
- go/no-go recommendation.

### Phase 2 — integrated shadow pilot

One station, four to six operational weeks:

- edge camera pipeline;
- connected scale and POS/KDS events;
- two-week baseline;
- reviewed alerts/dashboard;
- one or two operational interventions;
- comparison against agreed KPI.

Suggested commercial ranges are documented in `docs/SPEC.md`. Keep hardware, POS integration, labeling volume, travel and support assumptions explicit.

## Market context

ABF reported 2025 Brazilian franchising revenue of R$301.7 billion, 202,444 operations, and 3,297 networks; Food Service grew 10.8%. A solution that works in one standardized station can extend to coffee, frozen dessert, bowls, sandwiches and other assembly-line franchise formats. This supports a vertical product strategy, but each format still needs its own ontology and target data.

## Technology and licensing warning

Ultralytics states that proprietary commercial embedding/deployment generally requires its Enterprise license unless the project complies with AGPL terms. Decide the production license before building around Ultralytics. Keep the repository’s perception contract model-neutral and evaluate commercially compatible alternatives.

## Sources

- [OAKBERRY franchising](https://www.oakberry.com/pt-BR/seja-um-franqueado)
- [OAKBERRY and Qu platform integration](https://www.prnewswire.com/news-releases/global-acai-brand-oakberry-taps-qus-unified-commerce-platform-to-anchor-us-expansion-302660568.html)
- [Alejandro Veiga on applied AI in operations](https://mercadoeconsumo.com.br/23/06/2026/tecnologia/hoje-esta-muito-mais-pratico-ter-visao-do-negocio-diz-diretor-de-operacoes-da-oakberry/)
- [ABF 2025 results](https://www.abf.com.br/wp-content/uploads/2026/03/ABFNEWS090326.html)
- [Ultralytics licensing](https://www.ultralytics.com/license)
