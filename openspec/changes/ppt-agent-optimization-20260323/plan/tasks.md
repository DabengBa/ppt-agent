# Implementation Tasks — PPT Agent Optimization

> Decomposed from 27 FRs into implementation tasks.
> Grouped by wave. Dependencies and atomic groups marked.
> Date: 2026-03-23

---

## Wave 1 — Unlock Foundation

All Wave 1 tasks are independent of each other (can be committed in any order).

### T-01: Add Bash to review-core tools

- **FR**: FR-01
- **Priority**: P0 | **Effort**: S
- **Description**: Add `Bash` to review-core.md frontmatter tools array. This unblocks the 5 pre-review checks that are currently dead code.
- **Affected files**: `agents/review-core.md`
- **Dependencies**: None (prerequisite for T-07, T-08, T-09)
- **Acceptance**: `Bash` appears in tools array; running review-core no longer skips pre-review checks.

### T-02: content-core maxTurns 25->35

- **FR**: FR-02
- **Priority**: P0 | **Effort**: S
- **Description**: Change `maxTurns: 25` to `maxTurns: 35` in content-core.md frontmatter.
- **Affected files**: `agents/content-core.md`
- **Dependencies**: Paired with T-03 (atomic group W1-A)
- **Acceptance**: `maxTurns: 35` in frontmatter; 15-slide deck completes without truncation.

### T-03: Batch draft signals every 3 slides

- **FR**: FR-03
- **Priority**: P0 | **Effort**: S
- **Description**: Change content-core draft signaling from per-slide to every 3 slides. Update ppt.md Phase 5-6 pipeline to handle batched signals.
- **Affected files**: `agents/content-core.md` (execution section), `commands/ppt.md` (Phase 5 description + Phase 6 pipeline trigger)
- **Dependencies**: Paired with T-02 (atomic group W1-A)
- **Acceptance**: content-core sends `draft_slide_ready(indices=[N,N+1,N+2])` every 3rd slide (and final). ppt.md pipeline handles batch.

### T-04: slide-core maxTurns 30->20

- **FR**: FR-04
- **Priority**: P2 | **Effort**: S
- **Description**: Change `maxTurns: 30` to `maxTurns: 20` in slide-core.md frontmatter.
- **Affected files**: `agents/slide-core.md`
- **Dependencies**: None
- **Acceptance**: `maxTurns: 20` in frontmatter.

### T-05: review-core maxTurns 15->20

- **FR**: FR-05
- **Priority**: P2 | **Effort**: S
- **Description**: Change `maxTurns: 15` to `maxTurns: 20` in review-core.md frontmatter.
- **Affected files**: `agents/review-core.md`
- **Dependencies**: None
- **Acceptance**: `maxTurns: 20` in frontmatter.

### T-06: outline.json approved field + resume guard

- **FR**: FR-06
- **Priority**: P0 | **Effort**: S
- **Description**: Add `"approved": false` to outline.json schema in outline-architect.md. Update ppt.md resume detection to check `approved === true` before skipping to Phase 5. Missing field treated as `false`.
- **Affected files**: `skills/_shared/references/prompts/outline-architect.md`, `commands/ppt.md`
- **Dependencies**: None
- **Acceptance**: Schema includes `approved` boolean; resume skips to Phase 5 only if `approved === true`.

**Atomic Group W1-A**: T-02 + T-03 (maxTurns + batching must ship together)

---

## Wave 2 — Rebuild Aesthetic Optimization Layer

### T-07: Rewrite Gemini optimizer role prompts (ATOMIC with T-09)

- **FR**: FR-07
- **Priority**: P0 | **Effort**: L
- **Description**: Rewrite three files for optimization-first framing:
  1. reviewer.md: Restructure output format (suggestions above scores); update role description, methodology, trailing paragraph (G-01, G-03).
  2. SKILL.md: `## Review Criteria` -> `## Optimization Criteria`; rewrite Task section (G-02).
  3. review-core.md: Reframe steps 6-8 as "request optimization suggestions" (AD-06).
- **Affected files**: `skills/gemini-cli/references/roles/reviewer.md`, `skills/gemini-cli/SKILL.md`, `agents/review-core.md`
- **Dependencies**: T-01 (Bash required for pre-review checks)
- **ATOMIC with T-09**: Must commit together
- **Acceptance**: Output format leads with suggestions; score is secondary; prompt language uses optimization framing.

### T-08: Redefine self-review fallback as technical validation only

- **FR**: FR-08
- **Priority**: P0 | **Effort**: M
- **Description**: Rewrite fallback behavior across three files:
  1. SKILL.md line 81: Remove "optimization must still happen" contradiction. Rewrite Fallback Strategy section. Update Constraints table.
  2. review-core.md step 7: Replace "Claude self-optimization" with "Execute technical validation checks only". Define distinct technical validation output format (G-08).
  3. ppt.md line 339: Replace "Claude self-review using same quality standards" with "technical validation only".
  Add extended checklist: text overflow estimation, outline content coverage, WCAG AA contrast.
- **Affected files**: `skills/gemini-cli/SKILL.md`, `agents/review-core.md`, `commands/ppt.md`
- **Dependencies**: T-01 (Bash required)
- **Acceptance**: SKILL.md line 81 fixed; fallback output has "Technical Validation" header; no overall_score in fallback; SKILL.md Fallback Strategy rewritten.

### T-09: Enrich suggestion format with 5-type taxonomy (ATOMIC with T-07)

- **FR**: FR-09
- **Priority**: P0 | **Effort**: M
- **Description**: Add `suggestion_type` and `layout_suggestion` fields to fix JSON format:
  1. reviewer.md: Define 5-type taxonomy, schema rules, examples for each type (G-04, G-05).
  2. review-core.md: Update structured fix JSON section.
  3. slide-core.md: Document how to handle each suggestion type (execution strategy).
- **Affected files**: `skills/gemini-cli/references/roles/reviewer.md`, `agents/review-core.md`, `agents/slide-core.md`
- **Dependencies**: T-07 (optimizer role must exist)
- **ATOMIC with T-07**: Must commit together
- **Acceptance**: reviewer.md defines taxonomy; JSON includes `suggestion_type`; slide-core documents type-aware handling.

### T-10: Add chart_colors to style YAMLs + svg-generator.md

- **FR**: FR-10
- **Priority**: P1 | **Effort**: S
- **Description**: Add `chart_colors` array (8 hex values) to each of 4 style YAMLs following palette design principles (G-11). Update svg-generator.md chart patterns to use `chart_colors[n]` (G-12). Add Multi-Series Color Assignment section.
- **Affected files**: `skills/_shared/references/styles/business.yaml`, `tech.yaml`, `creative.yaml`, `minimal.yaml`, `skills/_shared/references/prompts/svg-generator.md`
- **Dependencies**: None (independent, can start day 1 of Wave 2)
- **Acceptance**: Each YAML has `chart_colors` array; svg-generator patterns reference `chart_colors[n]`; backward compat fallback documented.

### T-10b: Expand style palette from 4 to 17

- **FR**: FR-10b
- **Priority**: P1 | **Effort**: M
- **Description**: Add 13 new style YAML files aligned with the visual-content slide-generator style system (github.com/zengwenliang416/all-image-style-system-prompt-zh). New styles: blueprint, bold-editorial, chalkboard, editorial-infographic, fantasy-animation, intuition-machine, notion, pixel-art, scientific, sketch-notes, vector-illustration, vintage, watercolor. Each follows existing YAML schema (color_scheme, typography, card_style, gradients, elevation, decoration, slide_type_overrides) with `mood` field guiding SVG aesthetic direction. Register all in index.json. chart_colors (from T-10) should be included in all 17 styles.
- **Affected files**: NEW: 13 YAML files in `skills/_shared/references/styles/`, `skills/_shared/index.json`
- **Dependencies**: T-10 (chart_colors design informs palette for new styles). Can start color/typography/card design independently.
- **Acceptance**: 17 style YAMLs exist; index.json total_count.styles = 17; all 17 registered with domain=style; `--style=chalkboard` (or any new name) works via discovery.

**Atomic Group W2-A**: T-07 + T-09 (optimizer role + suggestion taxonomy)
**Atomic Group W2-B**: T-08 (SKILL.md + review-core + ppt.md fallback consistency)
**Ordering within Wave 2**: SKILL.md first -> reviewer.md -> review-core.md -> ppt.md -> style YAMLs + svg-generator + style expansion

---

### Calibration Gate (mandatory after Wave 2)

**Purpose**: Production run (8-10 slide deck) to validate:
1. Does Gemini produce typed optimization suggestions with valid `suggestion_type`?
2. Does the 5-type taxonomy cover >= 80% of actual Gemini suggestions?
3. Are `layout_suggestion` descriptions actionable by slide-core?
4. Are technical validation thresholds reasonable in fallback mode?
5. Does signal batching work correctly in the pipeline?

**Gate outcome**: Proceed to Wave 3 (possibly with taxonomy adjustments), or iterate on Wave 2 prompts.

---

## Wave 3 — Fix Strategy + State Hardening

### T-11: slide-status.json atomic write

- **FR**: FR-11
- **Priority**: P1 | **Effort**: S
- **Description**: Add atomic write pattern to ppt.md Phase 6 slide-status.json updates: write to `.tmp`, validate JSON, rename.
- **Affected files**: `commands/ppt.md`
- **Dependencies**: T-06 (resume hardening group)
- **Acceptance**: slide-status.json writes use tmp+rename; crash mid-write preserves previous state.

### T-12: Guided-freedom color enforcement

- **FR**: FR-12
- **Priority**: P1 | **Effort**: M
- **Description**: Implement 3-zone enforcement model (mandatory core / chart / decorative free):
  1. slide-core.md: Document mandatory vs free color zones; require `data-decorative="true"` for free-zone colors.
  2. reviewer.md: Rewrite color compliance section with guided-freedom rules (G-13).
- **Affected files**: `agents/slide-core.md`, `skills/gemini-cli/references/roles/reviewer.md`
- **Dependencies**: T-10 (chart_colors must exist)
- **Acceptance**: slide-core documents zones; reviewer uses guided-freedom model; decorative colors not flagged as errors.

### T-13: Suggestion-driven fix strategy

- **FR**: FR-13
- **Priority**: P1 | **Effort**: M
- **Description**: Replace score-driven fix routing with suggestion-type-driven routing:
  1. ppt.md: Rewrite Phase 6 fix loop from score-band routing to type-driven routing with priority cascade (G-19).
  2. slide-core.md: Rewrite fix handling from "deterministic patches" to type-aware execution.
- **Affected files**: `commands/ppt.md`, `agents/slide-core.md`
- **Dependencies**: T-09 (taxonomy must exist), calibration gate (taxonomy validated)
- **Acceptance**: Fix loop routes by suggestion type; score is auxiliary pass/fail gate; fallback mode only does technical fixes.

### T-14: Holistic deck review design

- **FR**: FR-14
- **Priority**: P1 | **Effort**: M
- **Description**: Design holistic review protocol:
  1. outline-architect.md: Add `visual_weight: "low"|"medium"|"high"` to page schema with assignment rules (G-15).
  2. reviewer.md: Expand holistic review section with 5 assessment dimensions and deck_coordination output (G-16).
- **Affected files**: `skills/_shared/references/prompts/outline-architect.md`, `skills/gemini-cli/references/roles/reviewer.md`
- **Dependencies**: T-07 (optimizer role), T-09 (deck_coordination type)
- **Acceptance**: outline.json schema includes visual_weight; holistic protocol documented; deck_coordination suggestions defined.

---

## Wave 4 — Visual Richness + Pipeline Optimization

### T-15: Add 5 missing SVG patterns

- **FR**: FR-15
- **Priority**: P1 | **Effort**: M
- **Description**: Add SVG patterns for: table, metric card grid, grouped bar chart, line chart with axes, network/relationship diagram (G-14). Add Pattern Selection by Content table.
- **Affected files**: `skills/_shared/references/prompts/svg-generator.md`
- **Dependencies**: T-10 (chart_colors for multi-series patterns)
- **Acceptance**: svg-generator.md includes all 5 patterns with constraints and selection guide.

### T-16: Holistic review implementation

- **FR**: FR-16
- **Priority**: P1 | **Effort**: M
- **Description**: Implement deck_coordination flow in orchestrator (G-17): receive holistic review, group suggestions by slide, spawn slide-core for affected slides, re-run holistic review (max 1 re-run).
- **Affected files**: `commands/ppt.md`, `agents/review-core.md`
- **Dependencies**: T-14 (holistic design)
- **Acceptance**: Holistic review produces deck_coordination suggestions; orchestrator processes them.

### T-17: Sonnet for attribute-level fix patches

- **FR**: FR-17
- **Priority**: P2 | **Effort**: M
- **Description**: Create `agents/slide-core-patch.md` (sonnet variant) for `attribute_change` fixes. Or use Task() model override if supported.
- **Affected files**: `agents/slide-core.md`, `commands/ppt.md`, NEW: `agents/slide-core-patch.md`
- **Dependencies**: T-13 (suggestion-driven fix strategy). Blocked by UD-1 investigation.
- **Acceptance**: attribute_change fixes use sonnet; layout_restructure and full_rethink use opus.

### T-18: Heartbeat reduction to start-only

- **FR**: FR-18
- **Priority**: P2 | **Effort**: S
- **Description**: Remove "before writing final output" heartbeat from all 4 agent .md files.
- **Affected files**: `agents/research-core.md`, `agents/content-core.md`, `agents/slide-core.md`, `agents/review-core.md`
- **Dependencies**: None
- **Acceptance**: Agents send heartbeat at start only.

### T-19: Memory scope none for slide-core and review-core

- **FR**: FR-19
- **Priority**: P2 | **Effort**: S
- **Description**: Change `memory: project` to `memory: none` in slide-core.md and review-core.md.
- **Affected files**: `agents/slide-core.md`, `agents/review-core.md`
- **Dependencies**: None
- **Acceptance**: `memory: none` in both frontmatters.

### T-20: Adaptive sliding window

- **FR**: FR-20
- **Priority**: P2 | **Effort**: M
- **Description**: Replace fixed `min(3, remaining)` window with adaptive sizing based on system load and completion rate.
- **Affected files**: `commands/ppt.md`
- **Dependencies**: T-14 (holistic review timing may constrain window)
- **Acceptance**: Phase 6 window size adapts dynamically.

### T-21: Requirements section extraction schema

- **FR**: FR-21
- **Priority**: P2 | **Effort**: S
- **Description**: Structured extraction of sections from requirements.md for Phase 3 parallel collection.
- **Affected files**: `commands/ppt.md`
- **Dependencies**: None
- **Acceptance**: Section extraction uses defined schema.

### T-22: Material merge deduplication

- **FR**: FR-22
- **Priority**: P2 | **Effort**: S
- **Description**: Add deduplication logic to Phase 3 material merge.
- **Affected files**: `commands/ppt.md`
- **Dependencies**: None
- **Acceptance**: Merged materials.md has no duplicate content blocks.

### T-23: Cognitive design principles

- **FR**: FR-23
- **Priority**: P2 | **Effort**: M
- **Description**: Operationalize Miller's Law, Mayer's principles, Gestalt rules into concrete slide design constraints in outline-architect and reviewer.
- **Affected files**: `skills/_shared/references/prompts/outline-architect.md`, `skills/gemini-cli/references/roles/reviewer.md`
- **Dependencies**: None
- **Acceptance**: Cognitive principles referenced as concrete rules.

### T-24: Score trajectory tracking

- **FR**: FR-24
- **Priority**: P2 | **Effort**: S
- **Description**: Record per-round scores in slide-status.json for debugging.
- **Affected files**: `commands/ppt.md`
- **Dependencies**: None
- **Acceptance**: slide-status.json records per-round scores.

### T-25: HTML preview improvements

- **FR**: FR-25
- **Priority**: P2 | **Effort**: M
- **Description**: Add speaker notes panel, slide comparison view to HTML preview.
- **Affected files**: `skills/_shared/assets/preview-template.html`
- **Dependencies**: None
- **Acceptance**: Enhanced preview features.

### T-26: Hard Stop UX quality

- **FR**: FR-26
- **Priority**: P2 | **Effort**: M
- **Description**: Improve Phase 2 and Phase 4 Hard Stop prompts and feedback format.
- **Affected files**: `commands/ppt.md`
- **Dependencies**: None
- **Acceptance**: Structured, user-friendly Hard Stop interactions.

### T-27: Artifact schema validators

- **FR**: FR-27
- **Priority**: P2 | **Effort**: M
- **Description**: Validation scripts for outline.json, slide-status.json, review-manifest.json.
- **Affected files**: New validation scripts
- **Dependencies**: T-06 (approved field), T-11 (atomic writes)
- **Acceptance**: Validators catch schema violations at write time.

---

## Critical Path

```
T-01 (Bash) -> T-07+T-09 (optimizer + taxonomy) -> [calibration gate] -> T-13 (fix strategy) -> T-17 (sonnet patches)
```

## Dependency Summary

```
T-01 --> T-07, T-08, T-09
T-02 <-> T-03 (paired)
T-06 --> T-11
T-07 <-> T-09 (atomic)
T-07+T-09 --> T-13, T-14
T-09 --> T-13
T-10 --> T-12, T-15
T-14 --> T-16, T-20
T-13 --> T-17
[calibration] --> T-13
```
