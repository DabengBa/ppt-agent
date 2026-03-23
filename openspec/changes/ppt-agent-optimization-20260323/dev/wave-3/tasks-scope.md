# Dev Scope — Wave 3: Visual Richness + Pipeline Quick Wins

> Proposal: ppt-agent-optimization-20260323
> Scope: T-15 + T-16 + T-18 + T-19 (2 P1 + 2 P2 quick wins)
> Date: 2026-03-23

## Selected Tasks

### T-15: Add 5 missing SVG patterns (P1, M)
- **Description**: Add SVG patterns for table, metric card grid, grouped bar chart, line chart with axes, network/relationship diagram. Add Pattern Selection by Content table.
- **Affected files**: `skills/_shared/references/prompts/svg-generator.md`
- **Dependencies**: T-10 ✅
- **Acceptance**: svg-generator.md includes all 5 patterns with constraints and selection guide.

### T-16: Holistic review implementation (P1, M)
- **Description**: Implement deck_coordination flow in orchestrator: receive holistic review, group suggestions by slide, spawn slide-core for affected slides, re-run holistic review (max 1 re-run).
- **Affected files**: `commands/ppt.md`, `agents/review-core.md`
- **Dependencies**: T-14 ✅
- **Acceptance**: Holistic review produces deck_coordination suggestions; orchestrator processes them.

### T-18: Heartbeat reduction to start-only (P2, S)
- **Description**: Remove "before writing final output" heartbeat from all 4 agent .md files. Keep only start heartbeat.
- **Affected files**: `agents/research-core.md`, `agents/content-core.md`, `agents/slide-core.md`, `agents/review-core.md`
- **Acceptance**: Agents send heartbeat at start only.

### T-19: Memory scope none for slide-core and review-core (P2, S)
- **Description**: Change `memory: project` to `memory: none` in slide-core.md and review-core.md.
- **Affected files**: `agents/slide-core.md`, `agents/review-core.md`
- **Acceptance**: `memory: none` in both frontmatters.
