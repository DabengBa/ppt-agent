# Requirements — PPT Agent Optimization

> Extracted from thinking phase artifacts on 2026-03-23.
> Source: proposal.md, conclusion.md, synthesis.md, handoff.json

---

## Wave 1 — Unlock Foundation (no behavior model changes)

### FR-01: Add Bash tool to review-core (U-01 / R1)

- **Priority**: P0 | **Effort**: S | **Wave**: 1
- **Description**: review-core's 5 pre-review automated checks (xmllint, viewBox, font-size, color compliance, safe area) all require Bash but it is missing from the tools list. Every SVG skips technical pre-check and goes straight to expensive LLM review.
- **Affected files**: `agents/review-core.md`
- **Dependencies**: None (prerequisite for FR-04, FR-05, FR-06)
- **Acceptance**: `Bash` appears in review-core frontmatter tools array; pre-review checks execute successfully.

### FR-02: Fix content-core maxTurns 25 to 35 (U-03 / R3)

- **Priority**: P0 | **Effort**: S | **Wave**: 1
- **Description**: content-core truncates on 12+ slide decks. A 15-page deck needs ~36 turns (5 reads + 15 writes + 15 signals + 1 manifest). Combined with signal batching (FR-03), 35 turns provides adequate headroom.
- **Affected files**: `agents/content-core.md`
- **Dependencies**: Should deploy with FR-03 (signal batching) to stay within budget.
- **Acceptance**: `maxTurns: 35` in content-core frontmatter.

### FR-03: Batch draft signals every 3 slides (U-03 / R3)

- **Priority**: P0 | **Effort**: S | **Wave**: 1
- **Description**: Change `draft_slide_ready` from per-slide to every 3 slides. Reduces signal overhead from N to ceil(N/3), saving ~10 turns on a 15-page deck.
- **Affected files**: `agents/content-core.md` (execution section), `commands/ppt.md` (Phase 5-6 pipeline)
- **Dependencies**: Paired with FR-02.
- **Acceptance**: content-core sends `draft_slide_ready(index=N)` after every 3rd slide (and on last slide). ppt.md Phase 6 pipeline handles batched signals.

### FR-04: slide-core maxTurns 30 to 20 (U-11 / R3)

- **Priority**: P2 | **Effort**: S | **Wave**: 1
- **Description**: slide-core designs ONE slide per invocation. 30 turns is over-allocated by ~15 turns (actual need: 12-15).
- **Affected files**: `agents/slide-core.md`
- **Dependencies**: None.
- **Acceptance**: `maxTurns: 20` in slide-core frontmatter.

### FR-05: review-core maxTurns 15 to 20 (U-12 / R3)

- **Priority**: P2 | **Effort**: S | **Wave**: 1
- **Description**: Holistic review mode reads ALL SVGs — 15 turns too tight for 12+ slide decks.
- **Affected files**: `agents/review-core.md`
- **Dependencies**: None.
- **Acceptance**: `maxTurns: 20` in review-core frontmatter.

### FR-06: outline.json `approved` field + resume check (U-04 / R4a)

- **Priority**: P0 | **Effort**: S | **Wave**: 1
- **Description**: Resume logic can bypass Phase 4 Hard Stop if outline.json exists but was never user-approved. Add `approved: true` field set only after user confirmation. Resume checks this field; missing or false triggers re-approval.
- **Affected files**: `commands/ppt.md` (resume detection logic), `skills/_shared/references/prompts/outline-architect.md` (schema definition)
- **Dependencies**: None.
- **Backward compat**: Missing `approved` field treated as `false` (safe default).
- **Acceptance**: outline.json schema includes `approved` boolean; resume skips to Phase 5 only if `approved === true`; otherwise re-enters Phase 4 Hard Stop.

---

## Wave 2 — Rebuild Aesthetic Optimization Layer

### FR-07: Rewrite Gemini role as aesthetic optimizer (U-02 / R2a)

- **Priority**: P0 | **Effort**: L | **Wave**: 2
- **Description**: Rewrite review-core and reviewer.md prompts. Gemini's task is "proactively propose concrete visual improvements" not "check compliance and score". Output format: optimization suggestions as primary content, score as secondary judgment. Fix SKILL.md `## Review Criteria` heading to `## Optimization Criteria`.
- **Affected files**: `agents/review-core.md`, `skills/gemini-cli/references/roles/reviewer.md`, `skills/gemini-cli/SKILL.md` (prompt template section)
- **Dependencies**: FR-01 (Bash tool must be available for pre-review checks).
- **ATOMIC with FR-09**: Must ship together — suggestion format and optimizer role are coupled.
- **Acceptance**: Gemini prompts use optimization framing; reviewer.md output format leads with suggestions; SKILL.md prompt template updated.

### FR-08: Redefine self-review fallback as "technical validation only" (U-02 / R2b)

- **Priority**: P0 | **Effort**: M | **Wave**: 2
- **Description**: When Gemini is unavailable, Claude self-review cannot substitute independent aesthetic perspective. Fallback should honestly execute only programmable technical checks: XML validity, viewBox, font-size floor, spacing, color contrast (WCAG AA), safe area, text overflow estimation, outline content coverage check. Output explicitly marked "technical validation only -- aesthetic optimization skipped".
- **Affected files**: `agents/review-core.md` (fallback execution path), `skills/gemini-cli/SKILL.md` (line 81 contradiction: "optimization must still happen" must change to "technical validation only"), `commands/ppt.md` (fallback handling description)
- **Dependencies**: FR-01 (Bash required for technical checks).
- **Key fix**: SKILL.md line 81 currently says "optimization must still happen, just without the cross-model perspective" — this contradicts the corrected understanding. Must change to "technical validation only".
- **Acceptance**: Self-review output header says "technical validation only"; no aesthetic scores produced in fallback mode; SKILL.md line 81 fixed.

### FR-09: Enrich optimization suggestion format with 5-type taxonomy (U-02 / R2c)

- **Priority**: P0 | **Effort**: M | **Wave**: 2
- **Description**: Add `layout_suggestion` field to fix JSON format. Define 5 suggestion types: `attribute_change` (property tweak), `layout_restructure` (structural layout change), `full_rethink` (complete redesign), `content_reduction` (lower info density), `deck_coordination` (cross-slide harmony, from holistic review). Each suggestion carries its type, enabling slide-core to choose execution strategy.
- **Affected files**: `skills/gemini-cli/references/roles/reviewer.md` (fix suggestion format), `agents/review-core.md` (structured fix JSON section), `agents/slide-core.md` (fix handling)
- **Dependencies**: FR-07 (Gemini optimizer role must exist to produce typed suggestions).
- **ATOMIC with FR-07**: Must ship together.
- **Acceptance**: reviewer.md defines 5-type taxonomy; fix JSON includes `suggestion_type` and optional `layout_suggestion` fields; slide-core documents how to handle each type.

### FR-10: Add chart_colors token to all style YAMLs (U-08 / R5a)

- **Priority**: P1 | **Effort**: S | **Wave**: 2
- **Description**: All 4 style YAMLs lack `chart_colors`. Data visualizations currently use only `${accent}` as sole data color — multi-series charts are impossible. Add `chart_colors` as ordered array of 6-8 hex values. Update svg-generator.md chart patterns to use `chart_colors[n]` instead of `${accent}`.
- **Affected files**: `skills/_shared/references/styles/business.yaml`, `skills/_shared/references/styles/tech.yaml`, `skills/_shared/references/styles/creative.yaml`, `skills/_shared/references/styles/minimal.yaml`, `skills/_shared/references/prompts/svg-generator.md`
- **Dependencies**: None.
- **Acceptance**: Each style YAML has `chart_colors` array (6-8 entries); svg-generator.md chart patterns reference `chart_colors`.

### FR-10b: Expand style palette from 4 to 17 (NEW)

- **Priority**: P1 | **Effort**: M | **Wave**: 2
- **Description**: Current PPT Agent only offers 4 styles (business, tech, creative, minimal). Expand to 17 by adding 13 new style YAMLs aligned with the visual-content slide-generator style system (see: github.com/zengwenliang416/all-image-style-system-prompt-zh). New styles: blueprint, bold-editorial, chalkboard, editorial-infographic, fantasy-animation, intuition-machine, notion, pixel-art, scientific, sketch-notes, vector-illustration, vintage, watercolor. Each YAML follows the existing schema (color_scheme, typography, card_style, gradients, elevation, decoration, slide_type_overrides) with a `mood` field guiding SVG generation aesthetics. Register all in index.json.
- **Affected files**: NEW: 13 style YAML files in `skills/_shared/references/styles/`, `skills/_shared/index.json`
- **Dependencies**: None (independent, can start day 1 of Wave 2). FR-10 (chart_colors) should be applied to all 17 styles, not just the original 4.
- **Reference**: Style names and visual concepts from visual-content slide-generator: blueprint (engineering grid), bold-editorial (magazine impact), chalkboard (chalk on dark green), editorial-infographic (data magazine), fantasy-animation (magical purple+gold), intuition-machine (AI neural green+pink), notion (structured clarity), pixel-art (8-bit retro), scientific (academic blue), sketch-notes (hand-drawn), vector-illustration (flat modern), vintage (aged warm), watercolor (soft washes).
- **Acceptance**: 17 style YAMLs in styles/; index.json lists all 17 with domain=style; `--style=<name>` works for all new styles.

---

### Calibration Gate (mandatory after Wave 2)

Production run (8-10 slide deck) required to validate:
- Does Gemini produce actionable aesthetic optimization suggestions?
- Does the 5-type suggestion taxonomy cover actual Gemini output?
- Are technical validation thresholds reasonable in fallback mode?
- Calibration results inform Wave 3 adjustments (especially FR-13 fix strategy).

---

## Wave 3 — Fix Strategy + State Hardening

### FR-11: slide-status.json atomic write (U-06 / R4b)

- **Priority**: P1 | **Effort**: S | **Wave**: 3
- **Description**: Crash during slide-status.json write corrupts the file, losing all completed slide progress. Use atomic write pattern: write to `.tmp`, validate JSON, then rename.
- **Affected files**: `commands/ppt.md` (Phase 6 slide-status update logic)
- **Dependencies**: FR-06 (resume hardening group).
- **Acceptance**: slide-status.json writes use tmp+rename pattern; crash mid-write preserves previous valid state.

### FR-12: Style token guided-freedom enforcement model (U-07)

- **Priority**: P1 | **Effort**: M | **Wave**: 3
- **Description**: Adopt Gemini's unified guided-freedom model: mandatory core colors enforced programmatically (primary, secondary, accent, background, text, card_bg), decorative colors free but must be declared, chart_colors from token. Review rubric uses single enforcement model (not split strict/flexible).
- **Affected files**: `agents/slide-core.md` (color usage rules), `skills/gemini-cli/references/roles/reviewer.md` (color compliance section), all 4 style YAMLs (if decorative declaration format needed)
- **Dependencies**: FR-10 (chart_colors must exist).
- **Acceptance**: slide-core documents mandatory vs. free color zones; reviewer.md color compliance section uses guided-freedom model.

### FR-13: Suggestion-driven fix strategy (U-05 / R5b)

- **Priority**: P1 | **Effort**: M | **Wave**: 3
- **Description**: Replace score-driven fix routing (5.0-6.9 patch, <5 regenerate) with suggestion-driven strategy. Gemini suggests -> each suggestion has type -> slide-core picks execution: `attribute_change` -> deterministic patch, `layout_restructure` -> regenerate with layout constraints, `full_rethink` -> regenerate from scratch, `content_reduction` -> regenerate with simplified content, `deck_coordination` -> deferred to holistic pass. Without Gemini: only technical fixes (hard constraint violations).
- **Affected files**: `commands/ppt.md` (Phase 6 fix loop logic), `agents/slide-core.md` (fix handling by type)
- **Dependencies**: FR-09 (taxonomy must exist), calibration gate (taxonomy validated against real data).
- **Acceptance**: Phase 6 fix loop routes by suggestion type, not score threshold; score remains as auxiliary pass/fail gate.

### FR-14: Holistic deck aesthetic coherence review design (U-09)

- **Priority**: P1 | **Effort**: M | **Wave**: 3
- **Description**: Design the Gemini holistic review protocol: cross-slide visual rhythm, color story escalation, layout variety, narrative arc pacing. Add `visual_weight` hint to outline.json for proactive planning at outline time. This is Gemini's most irreplaceable contribution — the ability to see the entire deck as a visual narrative.
- **Affected files**: `commands/ppt.md` (holistic review invocation), `skills/_shared/references/prompts/outline-architect.md` (visual_weight in schema), `skills/gemini-cli/references/roles/reviewer.md` (holistic mode section)
- **Dependencies**: FR-07 (Gemini optimizer role), FR-09 (deck_coordination suggestion type).
- **Acceptance**: outline.json schema includes `visual_weight`; holistic review protocol documented in reviewer.md; deck_coordination suggestions flow from holistic review.

---

## Wave 4 — Visual Richness + Pipeline Optimization

### FR-15: Missing SVG patterns (U-10)

- **Priority**: P1 | **Effort**: M | **Wave**: 4
- **Description**: Add SVG patterns for: table, metric card grid, grouped bar chart, line chart with axes, network/relationship diagram. Production run showed agent improvising these without spec guidance.
- **Affected files**: `skills/_shared/references/prompts/svg-generator.md`
- **Dependencies**: FR-10 (chart_colors for multi-series patterns).
- **Acceptance**: svg-generator.md includes SVG code patterns for all 5 types.

### FR-16: Holistic aesthetic coherence implementation (U-09)

- **Priority**: P1 | **Effort**: M | **Wave**: 4
- **Description**: Implement the holistic review protocol designed in FR-14. deck_coordination suggestion type lands in practice.
- **Affected files**: `commands/ppt.md`, `agents/review-core.md`
- **Dependencies**: FR-14 (design).
- **Acceptance**: Holistic review produces deck_coordination suggestions; lead orchestrator processes them.

### FR-17: Sonnet for attribute-level fix patches (U-14)

- **Priority**: P2 | **Effort**: M | **Wave**: 4
- **Description**: Use sonnet (cheaper, faster) for mechanical `attribute_change` fixes instead of opus. Requires agent infra model override support (UD-1).
- **Affected files**: `agents/slide-core.md`, `commands/ppt.md`
- **Dependencies**: FR-13 (suggestion-driven fix strategy must classify fix types). Blocked by UD-1 (model override infra).
- **Acceptance**: attribute_change fixes use sonnet; layout_restructure and full_rethink use opus.

### FR-18: Heartbeat reduction to start-only (U-13)

- **Priority**: P2 | **Effort**: S | **Wave**: 4
- **Description**: Agents currently send heartbeat at start AND before final output. Reduce to start-only to save context window.
- **Affected files**: All 4 agent .md files (`research-core.md`, `content-core.md`, `slide-core.md`, `review-core.md`)
- **Dependencies**: None.
- **Acceptance**: Agent prompts specify heartbeat at start only.

### FR-19: Memory scope none for slide-core and review-core (U-15)

- **Priority**: P2 | **Effort**: S | **Wave**: 4
- **Description**: slide-core and review-core process one slide at a time with full context in prompt. Project memory is wasted context.
- **Affected files**: `agents/slide-core.md`, `agents/review-core.md`
- **Dependencies**: None.
- **Acceptance**: `memory: none` in slide-core and review-core frontmatter.

### FR-20: Adaptive sliding window (U-16)

- **Priority**: P2 | **Effort**: M | **Wave**: 4
- **Description**: Current fixed window of `min(3, remaining)` parallel slide-core agents. Adapt window size based on system load and completion rate.
- **Affected files**: `commands/ppt.md`
- **Dependencies**: FR-14 (holistic review timing may constrain window).
- **Acceptance**: Phase 6 window size adapts dynamically.

### FR-21: requirements.md section extraction schema (U-17)

- **Priority**: P2 | **Effort**: S | **Wave**: 4
- **Description**: Structured extraction of sections from requirements.md for Phase 3 parallel collection.
- **Affected files**: `commands/ppt.md`
- **Dependencies**: None.
- **Acceptance**: Section extraction uses defined schema.

### FR-22: Material merge deduplication (U-18)

- **Priority**: P2 | **Effort**: S | **Wave**: 4
- **Description**: Lead's serial merge of per-topic material files into materials.md should deduplicate overlapping content.
- **Affected files**: `commands/ppt.md`
- **Dependencies**: None.
- **Acceptance**: Merged materials.md has no duplicate content blocks.

### FR-23: Cognitive design principles operationalized (U-20)

- **Priority**: P2 | **Effort**: M | **Wave**: 4
- **Description**: Operationalize Miller's Law, Mayer's principles, Gestalt rules into concrete slide design constraints.
- **Affected files**: `skills/_shared/references/prompts/outline-architect.md`, `skills/gemini-cli/references/roles/reviewer.md`
- **Dependencies**: None.
- **Acceptance**: outline-architect and reviewer reference cognitive principles as concrete rules.

### FR-24: Score trajectory tracking (U-21)

- **Priority**: P2 | **Effort**: S | **Wave**: 4
- **Description**: Track score improvements across fix rounds for debugging and tuning.
- **Affected files**: `commands/ppt.md`
- **Dependencies**: None.
- **Acceptance**: slide-status.json records per-round scores.

### FR-25: HTML preview improvements (U-22)

- **Priority**: P2 | **Effort**: M | **Wave**: 4
- **Description**: Improve HTML preview page (speaker notes panel, slide comparison view, etc.).
- **Affected files**: `skills/_shared/assets/preview-template.html`
- **Dependencies**: None.
- **Acceptance**: Enhanced preview features implemented.

### FR-26: Hard Stop UX quality (U-23)

- **Priority**: P2 | **Effort**: M | **Wave**: 4
- **Description**: Improve Phase 2 and Phase 4 Hard Stop user experience — better prompts, clearer options, structured feedback format.
- **Affected files**: `commands/ppt.md`
- **Dependencies**: None.
- **Acceptance**: Hard Stop interactions are more structured and user-friendly.

### FR-27: Artifact schema validators (U-19)

- **Priority**: P2 | **Effort**: M | **Wave**: 4
- **Description**: Validation scripts for outline.json, slide-status.json, review-manifest.json schemas.
- **Affected files**: New validation scripts
- **Dependencies**: FR-06 (approved field), FR-11 (atomic writes).
- **Acceptance**: Validators catch schema violations at write time.

---

## Non-Functional Requirements

### NFR-01: Backward compatibility with existing run directories
All changes must be backward-compatible. New fields (e.g., `approved` in outline.json) must have safe defaults when absent.

### NFR-02: 4-agent architecture preserved
Do not decompose or merge agents: research-core, content-core, slide-core, review-core.

### NFR-03: Star topology preserved
Agents communicate only with the lead orchestrator via SendMessage. No agent-to-agent communication.

### NFR-04: File-based state machine preserved
Artifact presence in RUN_DIR as durable truth layer. Harden it (atomic writes, approval markers), do not replace it.

### NFR-05: Graceful degradation preserved
Gemini available -> full aesthetic optimization. Gemini unavailable -> technical validation only. Never fake aesthetic review.

### NFR-06: Pipeline overlap preserved
Phase 5->6 pipeline overlap is architecturally sound. Simplify signaling (batch) but keep the pipeline.

---

## Constraints (from handoff.json)

| # | Constraint |
|---|-----------|
| C1 | 4-agent architecture is validated -- do not decompose or merge agents |
| C2 | Star topology (no agent-to-agent communication) is correct |
| C3 | File-based state machine is the right resume pattern -- harden it, do not replace it |
| C4 | Gemini's role is aesthetic optimizer -- all review prompts must reflect this, not compliance checker framing |
| C5 | Claude self-review CANNOT substitute Gemini's aesthetic perspective -- fallback must honestly degrade to technical validation only |
| C6 | Graceful degradation pattern must be preserved: Gemini available -> full aesthetic optimization; unavailable -> technical validation only (no fake aesthetic review) |
| C7 | Pipeline overlap (Phase 5 to 6) is architecturally sound -- simplify signaling but keep the pipeline |
| C8 | All changes must be backward-compatible with existing run directories |

---

## Unresolved Decisions

### UD-1: Agent infra model override support

- **Description**: Sonnet for attribute-level fix rounds (FR-17) requires either two agent variants or Task() model override. Current agent YAML frontmatter fixes the model at definition time.
- **Blocking**: FR-17
- **Resolution path**: Investigate Task() API for model override parameter.

### UD-2: Technical validation implementation form

- **Description**: Pre-review technical validation (FR-08) can be: (a) bash script called by review-core, (b) validation checks inlined in review-core prompt, (c) separate validation step in orchestrator before spawning review-core.
- **Blocking**: FR-08
- **Resolution path**: Decide during plan phase architecture analysis.

### UD-3: Optimization suggestion type taxonomy

- **Description**: 5-type taxonomy (attribute_change, layout_restructure, full_rethink, content_reduction, deck_coordination) must be validated against actual Gemini outputs from Wave 2 calibration run. May need expansion or collapse.
- **Blocking**: FR-13
- **Resolution path**: Wave 2 calibration production run.

---

## Dependency Graph

```
FR-01 (Bash tool) ──prereq──> FR-07 (Gemini optimizer role)
                               FR-08 (self-review fallback)
                               FR-09 (suggestion taxonomy)  [ATOMIC with FR-07]
                                        |
                                   [calibration gate]
                                        |
                                        v
                                   FR-13 (suggestion-driven fix)
                                        |
                                        v
                                   FR-17 (sonnet for patches)  [blocked by UD-1]

FR-02 (content maxTurns) + FR-03 (batch signals) ── paired, independent

FR-04 (slide-core maxTurns) ── independent
FR-05 (review-core maxTurns) ── independent

FR-06 (approved field) ──prereq──> FR-11 (atomic writes)

FR-10 (chart_colors) ──prereq──> FR-12 (style enforcement)
                                  FR-15 (SVG patterns)

FR-07 + FR-09 ──prereq──> FR-14 (holistic design) ──prereq──> FR-16 (holistic impl)
                                                                FR-20 (adaptive window)
```

**Critical path**: FR-01 -> FR-07+FR-09 -> [calibration] -> FR-13 -> FR-17
