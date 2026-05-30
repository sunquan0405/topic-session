---
topic: Industry Agent Technical Routes
created: 2026-05-30
updated: 2026-05-30
domain: AI-Agent
status: active
sessions: 3
tags:
  - agent-architecture
  - layered-hybrid
  - RAG
  - skill-ecosystem
  - industry-model
summary: >
  Analysis of two technical routes for building industry agents
  (training vertical models vs API + exhaustive skills), proposing
  a third route: Layered Hybrid Framework, with discussion on
  when training industry models actually makes sense.
related_topics: []
---

## 2026-05-30

### Q: Analyze the pros and cons of two technical routes for building industry agents
A: Neither route is complete. The optimal solution is a third route: Layered Hybrid Framework.
- **Route A (train vertical model + Skills)**: 6 fatal disadvantages — training cost (7B model ~$5K-20K GPU), knowledge freezing (model is frozen after training), general capability erosion (even LoRA degrades general reasoning), Skill execution gap (domain knowledge ≠ tool calling ability), maintenance debt (full ML engineering pipeline required), diseconomy of scale (more scenarios = diminishing returns). Confidence: 95%.
- **Route B (general API + exhaustive Skills)**: "Exhaustive scenarios" is a false premise. Three reasons — scenario combinatorial explosion, Skill routing complexity (error rate climbs exponentially beyond 30 skills), surface understanding trap (models know definitions but not industry practice). Confidence: 90%.
- **Route C (Layered Hybrid Architecture)**: 5 decoupled layers — Layer 0 (UI), Layer 1 (Intent Detection via embedding — <50ms latency, near-zero cost), Layer 2 (main inference: API LLM + economy channel + offline/local model), Layer 3 (RAG knowledge layer replacing knowledge freezing), Layer 4 (Skill ecosystem: Core/Domain/User + dynamic registration), Layer 5 (lightweight domain experts: 0.5B-3B models, 500-2000 samples each).
- Key data: 8-dimension comparison across all three routes.

### Q: What's the actual point of continuously training industry models?
A: Half marketing narrative, half real value. Five meaningful reasons:
- **Data flywheel**: RAG knows "what was written", training understands "what it means". A trained model can answer questions that have no answer in your knowledge base but are common knowledge in the industry. Confidence: 90% for complex reasoning domains (medical, legal, finance).
- **Cost threshold**: At 100k+ daily queries or $30k+ annual API spend, self-training becomes cheaper. Calculation: API $6k/month vs self-train $30k one-time + $2k/month ops.
- **Latency/reliability**: P99 < 500ms, 100% uptime (offline-capable), data never leaves premises, version consistency — API cannot deliver these.
- **Brand moat**: "We have our own model" vs "We use an API" → 3-5x valuation difference. This is a business narrative, not a technical one.
- **Three-layer progressive strategy**: Full pretraining (50B+ tokens, millions, semi-annual) → LoRA fine-tuning (3k-10k samples, tens of thousands, quarterly) → RAG (near-zero cost, continuous). Top teams use all three.

### Pending Discussion
- User DAU estimate (determines whether Phase 2 LoRA fine-tuning is worth it)
- Domain-specific data volume
