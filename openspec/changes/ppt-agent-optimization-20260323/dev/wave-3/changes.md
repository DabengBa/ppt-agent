# Changes: Wave 3 — Visual Richness + Pipeline Quick Wins

> Date: 2026-03-23

## T-15: 5 Missing SVG Patterns (+141 lines)
**File**: `skills/_shared/references/prompts/svg-generator.md`
- Added 5 SVG patterns: Table, Metric Card Grid, Grouped Bar Chart, Line Chart with Axes, Network/Relationship Diagram
- Added Pattern Selection by Content table (10 content types mapped to patterns)
- Each pattern includes complete SVG code example, constraints, and usage notes

## T-16: Holistic Review Implementation (+12/-1 lines)
**Files**: `commands/ppt.md`, `agents/review-core.md`
- ppt.md: Added 7-step holistic fix flow (parse suggestions → filter P1 → group by slide → re-dispatch → re-run max 1)
- review-core.md: Expanded holistic mode with outline.json reading, visual_weight inference, and 5-dimension framework reference

## T-18: Heartbeat Reduction (+4/-4 lines)
**Files**: All 4 agent .md files
- Changed "Send heartbeat when starting and before writing final output" → "Send heartbeat when starting"

## T-19: Memory Scope None (+2/-2 lines)
**Files**: `agents/slide-core.md`, `agents/review-core.md`
- Changed `memory: project` → `memory: none` in frontmatter

## Summary
6 files modified, +224/-24 LOC
