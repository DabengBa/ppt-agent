# Dev Scope — Wave 2: Suggestion-Driven Fix Strategy

> Proposal: ppt-agent-optimization-20260323
> Scope: T-13 (1 task, calibration-dependent, now unblocked)
> Date: 2026-03-23

## Calibration Evidence

Production run (ppt-xiaomi-su7-launch, 14 slides) confirmed:
- Gemini produces typed suggestions with valid `suggestion_type` (100% coverage)
- Fix loop is the primary bottleneck: avg score 6.68, only 4/14 passed ≥7.0
- Slide-05 (score 3.65) should have triggered `full_rethink` but only got 1 fix round
- Score-driven routing missed the opportunity to route by suggestion type

## Selected Task

### T-13: Suggestion-driven fix strategy (P1, M)
- **Description**: Replace score-driven fix routing with suggestion-type-driven routing:
  1. `commands/ppt.md`: Rewrite Phase 6 fix loop from score-band routing to type-driven routing with priority cascade.
  2. `agents/slide-core.md`: Rewrite fix handling from "deterministic patches" to type-aware execution.
- **Affected files**: `commands/ppt.md`, `agents/slide-core.md`
- **Dependencies**: T-09 ✅ (taxonomy exists), Calibration Gate ✅ (validated)
- **Acceptance**:
  - Fix loop routes by suggestion type, not by score bands
  - Score is auxiliary pass/fail gate only
  - Fallback mode only does technical fixes (no suggestion routing)
  - `full_rethink` triggers regeneration from scratch
  - `attribute_change` triggers deterministic patching
  - `layout_restructure` triggers constrained regeneration
  - `content_reduction` triggers content trimming + regeneration
- **Test**: Verify ppt.md fix loop uses suggestion types; slide-core.md documents type-aware handling; no stale score-band routing remains.
