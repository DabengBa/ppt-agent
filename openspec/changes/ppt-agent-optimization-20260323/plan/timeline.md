# Timeline — PPT Agent Optimization

> Relative timeline with dependencies, scope, and gates.
> Date: 2026-03-23

---

## Wave 1 — Unlock Foundation

**Scope**: 6 FRs (FR-01 through FR-06), all effort S
**Risk**: None — configuration changes, no behavior model alterations
**Dependencies**: None (all internal items independent)

| Task | FR | Effort | Files | Notes |
|------|----|--------|-------|-------|
| T-01: Add Bash to review-core | FR-01 | S | review-core.md | Prerequisite for Wave 2 |
| T-02: content-core maxTurns 35 | FR-02 | S | content-core.md | Atomic with T-03 |
| T-03: Signal batching | FR-03 | S | content-core.md, ppt.md | Atomic with T-02 |
| T-04: slide-core maxTurns 20 | FR-04 | S | slide-core.md | Independent |
| T-05: review-core maxTurns 20 | FR-05 | S | review-core.md | Independent |
| T-06: Approved field + resume | FR-06 | S | outline-architect.md, ppt.md | Independent |

**Commit strategy**: All items can go in a single commit (all independent, no behavioral coupling). Alternatively, T-01+T-05 (review-core changes) and T-02+T-03 (content-core + ppt.md) as separate commits.

**Estimated scope**: Small — all frontmatter tweaks + minor prompt/orchestrator text changes.

---

## Wave 2 — Rebuild Aesthetic Optimization Layer

**Scope**: 4 FRs (FR-07, FR-08, FR-09, FR-10), mixed M/L effort
**Risk**: Medium — changes Phase 6 behavior model
**Dependencies**: T-01 must be complete (Bash required for pre-review checks)

| Task | FR | Effort | Files | Notes |
|------|----|--------|-------|-------|
| T-10: chart_colors | FR-10 | S | 4x YAML, svg-generator.md | Independent — start immediately |
| T-07+T-09: Optimizer + taxonomy | FR-07+09 | L | reviewer.md, SKILL.md, review-core.md, slide-core.md | **ATOMIC** — largest change |
| T-08: Technical validation fallback | FR-08 | M | SKILL.md, review-core.md, ppt.md | Depends on T-01 |

**Ordering**:
1. T-10 (chart_colors) — independent, can start day 1
2. SKILL.md fixes first (canonical policy document)
3. reviewer.md format changes (output schema)
4. review-core.md prompt changes (consumes reviewer.md format)
5. slide-core.md fix handling docs (consumes suggestion types)
6. ppt.md fallback rules (references SKILL.md policy)

**Commit strategy**: T-10 as separate commit. T-07+T-09 as one atomic commit (reviewer.md + SKILL.md + review-core.md + slide-core.md). T-08 as separate commit (SKILL.md fallback + review-core fallback + ppt.md fallback).

**Estimated scope**: Large — significant prompt rewriting across 4+ files.

---

## Calibration Gate (mandatory)

**Trigger**: All Wave 2 tasks complete
**Activity**: Production run with 8-10 slide deck
**Duration**: One full workflow run + analysis

**Validation checklist**:

| # | Check | Pass criteria |
|---|-------|-------------|
| 1 | Gemini produces typed suggestions | >= 80% include valid `suggestion_type` |
| 2 | Taxonomy coverage | >= 80% map to existing 5 types |
| 3 | layout_suggestion actionable | slide-core interprets >= 70% |
| 4 | Technical validation catches issues | All Critical checks correct |
| 5 | Signal batching works | No dropped/duplicate slides |

**Gate outcomes**:
- **Pass**: Proceed to Wave 3
- **Partial**: Adjust taxonomy (expand/collapse types), re-calibrate, then proceed
- **Fail**: Iterate on Wave 2 prompts before proceeding

---

## Wave 3 — Fix Strategy + State Hardening

**Scope**: 4 FRs (FR-11, FR-12, FR-13, FR-14), all effort M
**Risk**: Medium — FR-13 changes fix loop behavior
**Dependencies**: Wave 2 complete + calibration gate passed

| Task | FR | Effort | Files | Dependencies |
|------|----|--------|-------|-------------|
| T-11: Atomic writes | FR-11 | S | ppt.md | T-06 |
| T-12: Guided-freedom | FR-12 | M | slide-core.md, reviewer.md | T-10 |
| T-13: Suggestion-driven fix | FR-13 | M | ppt.md, slide-core.md | T-09 + calibration |
| T-14: Holistic review design | FR-14 | M | outline-architect.md, reviewer.md | T-07, T-09 |

**Ordering**:
1. T-11 (atomic writes) — independent, no coupling
2. T-12 (guided-freedom) — touches reviewer.md + slide-core + style YAMLs
3. T-13 (suggestion-driven fix) — depends on calibration data
4. T-14 (holistic design) — touches outline-architect.md + reviewer.md

**Commit strategy**: T-11 standalone. T-12 as one commit (reviewer.md + slide-core). T-13 as one commit (ppt.md + slide-core). T-14 as one commit (outline-architect.md + reviewer.md).

**Estimated scope**: Medium — mix of orchestrator logic and prompt changes.

---

## Wave 4 — Visual Richness + Pipeline Optimization

**Scope**: 13 FRs (FR-15 through FR-27), mixed S/M effort
**Risk**: Low — incremental improvements on stable base
**Dependencies**: Wave 3 P1 items complete

| Group | Tasks | FRs | Effort | Notes |
|-------|-------|-----|--------|-------|
| SVG Patterns | T-15 | FR-15 | M | Depends on T-10 |
| Holistic Implementation | T-16 | FR-16 | M | Depends on T-14 |
| Sonnet Patches | T-17 | FR-17 | M | Depends on T-13; blocked by UD-1 |
| Agent Cleanup | T-18, T-19 | FR-18, FR-19 | S | Independent |
| Pipeline Optimization | T-20, T-21, T-22 | FR-20-22 | M/S | T-20 depends on T-14 |
| Quality & UX | T-23-T-27 | FR-23-27 | M/S | Mostly independent |

**Scheduling**: Flexible. Items can be implemented as ready. No strict ordering within Wave 4 except T-16 depends on T-14 and T-17 depends on T-13.

**Estimated scope**: Medium-large in aggregate, but each item is independent and can ship separately.

---

## Summary Timeline

```
Wave 1 ─────────────── (immediate, small scope)
         |
Wave 2 ─────────────────────── (after Wave 1, large scope)
         |
   [Calibration Gate] ──── (1 production run)
         |
Wave 3 ────────────────── (after calibration, medium scope)
         |
Wave 4 ──────────────────────────── (after Wave 3 P1s, flexible)
```
