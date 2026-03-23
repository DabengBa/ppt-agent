# Plan — PPT Agent Optimization

> Executive summary of the optimization plan.
> Proposal ID: ppt-agent-optimization-20260323
> Date: 2026-03-23

---

## Problem Statement

PPT Agent's 7-phase workflow and 4-agent architecture are structurally sound, but a production run (Xiaomi SU7, 12 slides) revealed that the aesthetic optimization layer is completely non-functional. Three root causes compound: (1) review-core lacks the Bash tool, making all 5 pre-review automated checks dead code; (2) Gemini is framed as a compliance scorer rather than an aesthetic optimizer, and when unavailable, Claude self-review rubber-stamps its own work (identical 8.2-8.8 scores across all 12 slides); (3) the fix loop routes by score thresholds rather than the nature of needed improvements, making structural layout suggestions impossible to execute. The net effect: Phase 6 degrades from a design-review-fix cycle into a single-pass generator.

---

## Solution Overview

### Wave 1 — Unlock Foundation (no behavior model changes)

Fix immediate blockers without altering the review behavior model. Add Bash to review-core (unblocking 5 dead checks). Correct maxTurns for all three agents (content-core 25->35 to prevent truncation on 12+ slide decks, slide-core 30->20, review-core 15->20). Batch draft signals every 3 slides to stay within turn budget. Add `approved` field to outline.json to prevent resume logic from bypassing the Phase 4 Hard Stop. **6 FRs, all P0 or P2, all effort S. Zero behavioral risk.**

### Wave 2 — Rebuild Aesthetic Optimization Layer

The core transformation. Rewrite Gemini's role from compliance checker to aesthetic optimizer — output format leads with concrete improvement suggestions, score becomes a secondary pass/fail gate. Define a 5-type suggestion taxonomy (attribute_change, layout_restructure, full_rethink, content_reduction, deck_coordination) that maps each suggestion to an execution strategy. Redefine self-review fallback as honest "technical validation only" — no fake aesthetic scores. Add chart_colors tokens to all style YAMLs for multi-series data visualization. Expand the style palette from 4 to 17 by adding 13 new styles aligned with the visual-content slide-generator style system (blueprint, bold-editorial, chalkboard, editorial-infographic, fantasy-animation, intuition-machine, notion, pixel-art, scientific, sketch-notes, vector-illustration, vintage, watercolor). **5 FRs (FR-07/08/09/10/10b), FR-07+09 are atomic. Medium-high risk, mitigated by mandatory calibration gate.**

### Calibration Gate (mandatory after Wave 2)

Production run (8-10 slide deck) to validate: Does Gemini produce typed suggestions? Does the taxonomy cover actual output? Are technical thresholds reasonable? Results inform Wave 3 adjustments. **This gate is non-negotiable — Wave 3 must not proceed without calibration data.**

### Wave 3 — Fix Strategy + State Hardening

Informed by calibration data, replace score-driven fix routing with suggestion-driven strategy. Each suggestion type maps to an execution: attribute_change -> deterministic patch, layout_restructure -> regenerate with constraint, full_rethink -> regenerate from scratch. Implement guided-freedom color enforcement (mandatory core / chart / decorative free zones). Add atomic writes for slide-status.json. Design the holistic deck review protocol for cross-slide aesthetic coherence. **4 FRs (FR-11/12/13/14), all P1, medium effort.**

### Wave 4 — Visual Richness + Pipeline Optimization

Add 5 missing SVG patterns (table, metric grid, grouped bar, line chart, network diagram). Implement holistic deck review. Use sonnet for cheap attribute-level patches. Reduce heartbeats, optimize memory scope, add adaptive sliding window. Improve HTML preview and Hard Stop UX. Add schema validators. **13 FRs (FR-15 through FR-27), mostly P2. Flexible scheduling.**

---

## Implementation Sequence with Dependencies

```
Wave 1 (immediate):
  T-01: review-core + Bash
  T-02+T-03: content-core maxTurns + signal batching [atomic]
  T-04: slide-core maxTurns
  T-05: review-core maxTurns
  T-06: outline.json approved field

Wave 2 (after Wave 1):
  T-10: chart_colors [independent, can start day 1]
  T-10b: expand style palette 4→17 [independent, parallel with T-10]
  T-07+T-09: Gemini optimizer role + taxonomy [atomic, depends on T-01]
  T-08: technical validation fallback [depends on T-01]

  [CALIBRATION GATE — 8-10 slide production run]

Wave 3 (after calibration):
  T-11: atomic writes [independent]
  T-12: guided-freedom enforcement [depends on T-10]
  T-13: suggestion-driven fix strategy [depends on T-09 + calibration]
  T-14: holistic review design [depends on T-07, T-09]

Wave 4 (after Wave 3 P1s complete):
  T-15 through T-27 [see tasks.md for full breakdown]
```

**Critical path**: T-01 -> T-07+T-09 -> [calibration] -> T-13 -> T-17

---

## Risk Matrix

| Risk | Likelihood | Impact | Severity | Mitigation |
|------|-----------|--------|----------|------------|
| Suggestion taxonomy doesn't match Gemini output | Medium | High | **High** | Calibration gate after Wave 2. Taxonomy is adjustable. |
| Prompt changes degrade Gemini response quality | Low | Medium | **Medium** | A/B comparison during calibration. Preserve raw outputs. |
| Signal batching breaks Phase 5->6 pipeline | Low | Medium | **Medium** | Test with 6-slide and 15-slide decks. |
| Two slide-core variants drift apart (Wave 4) | Medium | Low | **Low** | Share common content via reference. Prefer Task() override if supported. |
| Old run directories re-enter Phase 4 | High (by design) | Low | **Low** | This IS the safe behavior. Re-approval takes seconds. |
| Atomic write adds latency | Low | Low | **Negligible** | JSON validation + rename < 10ms vs LLM call minutes. |

---

## Success Criteria

1. **Aesthetic optimization functional**: Gemini produces actionable typed suggestions that lead to measurable visual improvements in fix rounds.
2. **Honest degradation**: When Gemini is unavailable, output clearly states "technical validation only" — no rubber-stamp aesthetic scores.
3. **No truncation**: 15-slide decks complete without content-core truncation.
4. **Resume safety**: outline.json approval check prevents skipping Hard Stop. Crash-safe slide-status.json.
5. **Multi-series charts**: Data visualization slides can use distinct colors per series.
6. **Calibration validates taxonomy**: >= 80% of Gemini suggestions map to the 5-type taxonomy.

---

## Timeline (Relative)

| Phase | Content | Gate |
|-------|---------|------|
| Wave 1 | 6 FRs, all S effort, single commit | None — ship immediately |
| Wave 2 | 4 FRs, mixed M/L effort, ordered commits | Calibration gate (production run) |
| Wave 3 | 4 FRs, all M effort, calibration-informed | None — ship after calibration |
| Wave 4 | 13 FRs, mixed S/M effort, flexible schedule | None — ship as ready |
