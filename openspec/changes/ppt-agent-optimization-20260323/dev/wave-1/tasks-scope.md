# Dev Scope — Wave 1: Fix Strategy + State Hardening (Part 1)

> Proposal: ppt-agent-optimization-20260323
> Scope: T-11 + T-12 + T-14 (3 tasks from Wave 3, excluding T-13 pending calibration)
> Date: 2026-03-23

## Selected Tasks

### T-11: slide-status.json atomic write (P1, S)
- **Description**: Add atomic write pattern to ppt.md Phase 6 slide-status.json updates: write to `.tmp`, validate JSON, rename.
- **Affected files**: `commands/ppt.md`
- **Dependencies**: T-06 ✅
- **Acceptance**: slide-status.json writes use tmp+rename; crash mid-write preserves previous state.
- **Test**: Verify ppt.md contains atomic write instructions for slide-status.json.

### T-12: Guided-freedom color enforcement (P1, M)
- **Description**: Implement 3-zone enforcement model (mandatory core / chart / decorative free):
  1. slide-core.md: Document mandatory vs free color zones; require `data-decorative="true"` for free-zone colors.
  2. reviewer.md: Rewrite color compliance section with guided-freedom rules.
- **Affected files**: `agents/slide-core.md`, `skills/gemini-cli/references/roles/reviewer.md`
- **Dependencies**: T-10 ✅
- **Acceptance**: slide-core documents zones; reviewer uses guided-freedom model; decorative colors not flagged as errors.
- **Test**: Verify both files contain guided-freedom color rules; no stale "strict color" references remain.

### T-14: Holistic deck review design (P1, M)
- **Description**: Design holistic review protocol:
  1. outline-architect.md: Add `visual_weight: "low"|"medium"|"high"` to page schema with assignment rules.
  2. reviewer.md: Expand holistic review section with 5 assessment dimensions and deck_coordination output.
- **Affected files**: `skills/_shared/references/prompts/outline-architect.md`, `skills/gemini-cli/references/roles/reviewer.md`
- **Dependencies**: T-07 ✅, T-09 ✅
- **Acceptance**: outline.json schema includes visual_weight; holistic protocol documented; deck_coordination suggestions defined.
- **Test**: Verify outline-architect.md has visual_weight field; reviewer.md has holistic review with 5 dimensions.

## Scope Note
- T-13 (suggestion-driven fix strategy) deferred pending Calibration Gate.
- All 3 tasks are independent of each other and can be implemented in parallel.
