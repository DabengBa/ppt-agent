# Synthesis — PPT Agent Optimization

> Consolidated from 6 evidence sources on 2026-03-23.
> Sources: explore-workflow.json, explore-agents.json, explore-svg.json, explore-platform.json, codex-thought.md, gemini-thought.md

---

## Cross-Cutting Themes

Six themes emerge across multiple boundary explorations, indicating systemic patterns rather than isolated issues.

### Theme 1: Aesthetic Optimization Layer Failure (appears in: workflow, SVG, agents)

Gemini 在架构中的角色是**视觉审美优化师**（不是打分员）— 主动提出布局改进和视觉增强建议，让幻灯片从"正确"变为"出色"。这是 dual-model 架构的核心价值。当前这一层完全失效：

- **Workflow**: Fix loop 从未在 production 中触发 — 12 张幻灯片全部首轮通过 (explore-workflow §phase-6-fix-loop)。原因不是幻灯片完美，而是审查层没有产出任何有价值的优化建议。
- **SVG Quality**: 12 份 review 使用相同的 Notes 文本，分数聚集在 8.2–8.8（0.6 分区间），review 格式规范完全被忽略 (explore-svg §4)。Claude self-review 不是在做审美优化，而是在给自己打高分。
- **Agents**: review-core 缺少 Bash 工具，5 项预审技术检查是死代码 (explore-agents §tool-availability-gaps)。

**根因分析**：Claude self-review 作为 Gemini 的 fallback，天然无法提供独立审美视角。一个模型审自己的产出，结果只能是"确认自己做得不错"。这不是提示词能解决的问题 — 这是 self-review 作为审美优化替代方案的根本局限。正确的 fallback 应该诚实承认：Gemini 不可用时只做可编程的技术验证，跳过审美优化。

### Theme 2: Spec vs. Practice Gap (appears in: SVG, workflow, platform)

Specifications are elaborate but weakly enforced. The production run demonstrates systematic deviation:

- **Style tokens**: Agent uses custom colors (#42E8FF, #FF7A1A, #6D7BFF) instead of tech.yaml tokens (#22d3ee) — explore-svg §8
- **Review format**: 3-field simplified format instead of specified 5-criterion structured JSON — explore-svg §4
- **Decorative elements**: Rich background system (grid, glow, grain) ungoverned by any spec — explore-svg §8
- **Chart patterns**: Agent improvises network diagrams and metric cards without spec guidance — explore-svg §3

The irony: the deviations produce *better* output. This suggests the specs should be restructured as hard constraints (measurable) + soft guidelines (inspirational), not treated as uniform requirements.

### Theme 3: Resource Budget Misalignment (appears in: agents, workflow)

Turn budgets and model allocations don't match actual workload:

- **content-core**: maxTurns=25 insufficient for 12+ slide decks (needs ~36 for 15 slides) — explore-agents §max-turns-allocation
- **slide-core**: maxTurns=30 over-allocated by ~15 turns (designs ONE slide, needs 12-15 turns) — explore-agents §max-turns-allocation
- **review-core**: maxTurns=15 too tight for holistic mode (reads ALL SVGs) — explore-agents §max-turns-allocation
- **slide-core fix rounds**: Uses opus for mechanical attribute patching that sonnet could handle — explore-agents §model-selection

### Theme 4: Resume Fragility (appears in: workflow, platform)

The file-based resume system has multiple edge cases:

- **Unapproved outline**: outline.json exists but was never user-approved → resume skips Hard Stop — explore-workflow §resume-detection
- **Partial JSON write**: slide-status.json crash mid-write → corrupted JSON → all completed work lost — explore-workflow §resume-detection
- **Stale artifacts**: User edits requirements.md between runs → outline is stale but resume trusts it — explore-workflow §resume-detection
- **No concurrency guard**: No lock file for headless/CI scenarios — explore-platform §cross_cutting_observations

### Theme 5: Optimization Suggestion Pathway Mismatch (appears in: workflow, SVG)

Gemini 的审美优化建议无法有效传递到 slide-core 执行：

- Fix JSON 格式（element/attribute/current/target）只能承载属性级微调，无法表达"将 3 列改为 hero+grid"等结构性布局建议
- Gemini 作为优化师可能建议根本性的布局重组，但传递管道只支持 deterministic patch
- 缺少 `layout_suggestion` 类型的建议字段，导致 Gemini 最有价值的创意建议无法落地
- 分数驱动的 fix 策略（5.0-6.9 patch, <5 regenerate）应该改为建议驱动：由优化建议的性质（attribute change vs layout restructure vs full rethink）决定执行策略

Both codex-thought (P1-1) and gemini-thought (C-07) converge on this, though they propose slightly different solutions. The corrected framing shifts the driver from "score threshold" to "optimization suggestion type".

### Theme 6: Data Visualization Limitations (appears in: SVG)

Single-color chart rendering and missing patterns constrain data-heavy presentations:

- All charts use `${accent}` as sole data color — multi-series impossible
- 3 chart types referenced in spec (table, icon array, metric grid) have no SVG patterns
- Common types (grouped bar, line chart with axes) entirely missing
- Network/relationship diagram used in production but not specified

---

## Conflict Resolution

Where codex-thought and gemini-thought disagree, I resolve with evidence.

### Conflict 1: Fix loop strategy

- **Codex**: Two-tier model — attribute fixes (sonnet) vs. structural fixes (opus, regeneration with layout constraints)
- **Gemini**: Score-dependent strategy — ≥7.0 pass, 6.0–6.9 patch, 5.0–5.9 regenerate, <5.0 regenerate, <3.0 regenerate with simplified content

**Resolution (revised)**: Both approaches的共同错误是以分数作为决策驱动。Gemini 的角色是审美优化师，其输出本质上是优化建议，而不是分数。正确的 fix 策略应该是**建议驱动**的：
- Gemini 提出具体优化建议 → 每条建议自带类型（attribute_change / layout_restructure / full_rethink）
- slide-core 根据建议类型选择执行方式：attribute patch / regenerate with constraints / regenerate from scratch
- 分数作为辅助判断而非主要驱动
- 无 Gemini 时：只有技术验证产出的 fix（硬约束违规），不伪造审美优化建议
**Adopt suggestion-driven strategy, deprecate score-only routing (DDR-2 revised).**

### Conflict 2: content-core maxTurns target

- **Codex**: Increase to 40
- **Gemini**: Increase to 35

**Resolution**: 35 is sufficient. For 15 slides: 5 reads + 15 writes + 5 batched signals (every 3 slides) + 1 manifest = 26 turns. With per-slide signaling: 36 turns. Combining the maxTurns increase to 35 with batched signaling (every 3 slides) provides adequate headroom without over-allocating. **Set to 35 + batch signals every 3 slides.**

### Conflict 3: Style token enforcement

- **Codex**: Option A (strict) for brand-override, Option B (guided freedom) for defaults
- **Gemini**: Guided freedom with guardrails: mandatory core colors + free decorative colors + chart_colors token

**Resolution**: Gemini's unified "guided freedom" model is better. Having two different enforcement modes (strict for brand, flexible for default) creates confusion in the review rubric. A single model — mandatory core colors enforced programmatically, decorative colors free but declared — is simpler to implement and review. **Adopt Gemini's guided-freedom model (C-05).**

### Conflict 4: Holistic review improvement

- **Codex**: Partial holistic checkpoint after every 3-4 slides (new review-core mode=checkpoint)
- **Gemini**: Mid-flight consistency check + add visual_weight hint to outline.json for proactive planning

**Resolution**: Both are valuable, but Gemini's proactive planning (visual_weight in outline.json) is more impactful than reactive checking. Color story escalation and layout variety are best planned at outline time, not discovered mid-flight. **Adopt both**: visual_weight in outline.json (proactive) + lightweight mid-flight check (reactive catch for deviations).

### Non-conflicts (independent agreement)

Both perspectives independently agree on:
- P0: review-core needs Bash (identical finding, identical fix)
- P0: Self-review is rubber stamp (identical diagnosis)
- P0: Resume skips outline approval (identical fix: add approved field)
- Architecture: 4-agent split is correct, star topology is correct
- Architecture: No agent decomposition provides net positive value

---

## Unified Priority Stack-Ranking (Deduplicated)

### P0 — Must Fix Before Next Production Run

| ID | Title | Codex | Gemini | Effort | Files Affected |
|----|-------|-------|--------|--------|---------------|
| **U-01** | review-core missing Bash tool | P0-1 | C-02 | S | `agents/review-core.md` |
| **U-02** | Rebuild aesthetic optimization layer (self-review → technical validation only) | P0-2 | C-01 | L | `agents/review-core.md`, `skills/gemini-cli/references/roles/reviewer.md`, `skills/gemini-cli/SKILL.md`, `commands/ppt.md` |
| **U-03** | content-core maxTurns insufficient for large decks | P0-3 | C-04 | S | `agents/content-core.md` |
| **U-04** | Resume skips outline approval Hard Stop | P0-4 | C-03 | S | `commands/ppt.md`, `skills/_shared/references/prompts/outline-architect.md` |

### P1 — Fix in Current Optimization Cycle

| ID | Title | Codex | Gemini | Effort | Files Affected |
|----|-------|-------|--------|--------|---------------|
| **U-05** | Suggestion-driven fix strategy (by optimization suggestion type, not score) | P1-1 | C-07 | M | `commands/ppt.md`, `agents/slide-core.md`, `skills/gemini-cli/references/roles/reviewer.md` |
| **U-06** | slide-status.json partial write corrupts resume | P1-2 | C-10 | S | `commands/ppt.md` |
| **U-07** | Style token guided-freedom model + enforcement | P1-4 | C-05 | M | `agents/slide-core.md`, `skills/gemini-cli/references/roles/reviewer.md`, all style YAMLs |
| **U-08** | chart_colors token for multi-series data viz | P1-5 | C-06 | S | All 4 style YAMLs, `skills/_shared/references/prompts/svg-generator.md` |
| **U-09** | Holistic review timing + proactive visual planning | P1-3 | C-08 | M | `commands/ppt.md`, `skills/_shared/references/prompts/outline-architect.md` |
| **U-10** | Missing SVG patterns (table, metric grid, grouped bar) | P2-7 | C-09 | M | `skills/_shared/references/prompts/svg-generator.md` |

### P2 — Schedule After P0/P1

| ID | Title | Codex | Gemini | Effort | Files Affected |
|----|-------|-------|--------|--------|---------------|
| **U-11** | slide-core maxTurns 30→20 | P2-2 | — | S | `agents/slide-core.md` |
| **U-12** | review-core maxTurns 15→20 | P2-3 | — | S | `agents/review-core.md` |
| **U-13** | Heartbeat reduction (start-only) | P2-4 | — | S | All 4 agent .md files |
| **U-14** | Sonnet for attribute fix rounds | P2-1 | — | M | `agents/slide-core.md`, `commands/ppt.md` |
| **U-15** | Memory scope: none for slide-core/review-core | P2-6 | — | S | `agents/slide-core.md`, `agents/review-core.md` |
| **U-16** | Adaptive sliding window | P2-5 | — | M | `commands/ppt.md` |
| **U-17** | requirements.md section extraction schema | P2-9 | — | S | `commands/ppt.md` |
| **U-18** | Material merge deduplication | P2-10 | — | S | `commands/ppt.md` |
| **U-19** | Artifact schema validators | P2-8 | C-15 | M | New validation scripts |
| **U-20** | Cognitive design principles operationalized | — | C-12 | M | `skills/_shared/references/prompts/outline-architect.md`, `skills/gemini-cli/references/roles/reviewer.md` |
| **U-21** | Score trajectory tracking | — | C-14 | S | `commands/ppt.md` |
| **U-22** | HTML preview improvements | — | C-11 | M | `skills/_shared/assets/preview-template.html` |
| **U-23** | Hard Stop UX quality (Phase 2/4) | — | C-13 | M | `commands/ppt.md` |

---

## Implementation Dependencies

```
U-01 (review-core Bash) ─── prerequisite for ──→ U-02 (rebuild aesthetic optimization layer)
                                                    │
                                                    ▼
                                        [calibration run gate]
                                                    │
                                                    ▼
                                               U-05 (suggestion-driven fix strategy)
                                                    │
                                                    ▼
                                               U-14 (sonnet for attribute patches)

U-03 (content-core maxTurns) ─── independent, immediate

U-04 (resume approval) ─── prerequisite for ──→ U-06 (atomic writes)

U-07 (style enforcement) + U-08 (chart_colors)
         │
         ▼
    U-10 (SVG patterns) ──→ U-19 (schema validators)

U-09 (holistic aesthetic coherence) ──→ U-16 (adaptive window)

U-11, U-12, U-13, U-15, U-17, U-18, U-21 ─── all independent
```

**Critical path**: U-01 → U-02 → [calibration run] → U-05 → U-14

This chain must execute sequentially: pre-review checks must work (U-01) before the aesthetic optimization layer can be rebuilt (U-02), which must be validated with a calibration production run before the suggestion-driven fix strategy can be designed (U-05, because the suggestion taxonomy depends on what Gemini actually produces), which must be defined before optimizing model selection for patches (U-14).

---

## Validated Good Decisions (Do NOT Change)

Evidence from explore-agents.json §agent-scope-boundaries confirms these architectural decisions are sound:

1. **4-agent architecture** (research / content / slide / review): No decomposition provides net positive value. All 4 alternatives analyzed (split content-core, merge review-core, specialize research-core, add validation-core) were rejected with high confidence.

2. **Star topology**: Agents communicate only with orchestrator. No agent-to-agent communication needed — workflow is sequential per-slide, orchestrator has full context.

3. **File-based state machine**: Artifact presence in RUN_DIR as durable truth layer. Elegant and host-agnostic. Needs hardening (atomic writes, approval markers) but the architecture is correct.

4. **Model allocation (research-core: sonnet, content-core: opus)**: Research is retrieval-heavy (sonnet sufficient), outline architecture requires deep structural reasoning (opus justified).

5. **Graceful degradation pattern**: agent-reach (Tier 2→1→0→WebSearch) and gemini-cli (model chain + Claude fallback) demonstrate a consistent, well-executed degradation strategy.

6. **Style registry (index.json)**: Discovery-driven, not hardcoded. Adding a new style requires only 2 files. Clean extensibility design.
