# Tasks — PPT Agent Optimization

> Root-level task list for OpenSpec validation.
> Proposal ID: ppt-agent-optimization-20260323

## Wave 1 — Unlock Foundation

| ID | Title | Priority | Effort | Files | Status |
|----|-------|----------|--------|-------|--------|
| T-01 | Add Bash to review-core tools | P0 | S | `agents/review-core.md` | ✅ Done |
| T-02 | content-core maxTurns 25→35 | P0 | S | `agents/content-core.md` | ✅ Done |
| T-03 | Batch draft signals every 3 slides | P0 | S | `agents/content-core.md`, `commands/ppt.md` | ✅ Done |
| T-04 | slide-core maxTurns 30→20 | P2 | S | `agents/slide-core.md` | ✅ Done |
| T-05 | review-core maxTurns 15→20 | P2 | S | `agents/review-core.md` | ✅ Done |
| T-06 | outline.json approved field + resume guard | P0 | S | `commands/ppt.md`, `skills/_shared/references/prompts/outline-architect.md` | ✅ Done |

Atomic groups: T-02 + T-03

## Wave 2 — Rebuild Aesthetic Optimization Layer

| ID | Title | Priority | Effort | Files |
|----|-------|----------|--------|-------|
| T-07 | Rewrite Gemini optimizer role prompts | P0 | L | `skills/gemini-cli/references/roles/reviewer.md`, `skills/gemini-cli/SKILL.md`, `agents/review-core.md` |
| T-08 | Redefine self-review fallback as technical validation only | P0 | M | `skills/gemini-cli/SKILL.md`, `agents/review-core.md`, `commands/ppt.md` |
| T-09 | Enrich suggestion format with 5-type taxonomy | P0 | M | `skills/gemini-cli/references/roles/reviewer.md`, `agents/review-core.md`, `agents/slide-core.md` |
| T-10 | Add chart_colors to style YAMLs + svg-generator | P1 | S | 4→17 style YAMLs, `skills/_shared/references/prompts/svg-generator.md` |
| T-10b | Expand style palette from 4 to 17 | P1 | M | NEW: 13 style YAMLs, `skills/_shared/index.json` |

Atomic groups: T-07 + T-09

**Calibration Gate**: Production run (8-10 slides) required after Wave 2.

## Wave 3 — Fix Strategy + State Hardening

| ID | Title | Priority | Effort | Files |
|----|-------|----------|--------|-------|
| T-11 | slide-status.json atomic write | P1 | S | `commands/ppt.md` |
| T-12 | Guided-freedom color enforcement | P1 | M | `agents/slide-core.md`, `skills/gemini-cli/references/roles/reviewer.md` |
| T-13 | Suggestion-driven fix strategy | P1 | M | `commands/ppt.md`, `agents/slide-core.md` |
| T-14 | Holistic deck review design | P1 | M | `skills/_shared/references/prompts/outline-architect.md`, `skills/gemini-cli/references/roles/reviewer.md` |

## Wave 4 — Visual Richness + Pipeline Optimization

| ID | Title | Priority | Effort | Files |
|----|-------|----------|--------|-------|
| T-15 | Add 5 missing SVG patterns | P1 | M | `skills/_shared/references/prompts/svg-generator.md` |
| T-16 | Holistic review implementation | P1 | M | `commands/ppt.md`, `agents/review-core.md` |
| T-17 | Sonnet for attribute-level fix patches | P2 | M | `agents/slide-core.md`, `commands/ppt.md` |
| T-18 | Heartbeat reduction to start-only | P2 | S | All 4 agent .md files |
| T-19 | Memory scope none for slide-core/review-core | P2 | S | `agents/slide-core.md`, `agents/review-core.md` |
| T-20 | Adaptive sliding window | P2 | M | `commands/ppt.md` |
| T-21 | Requirements section extraction schema | P2 | S | `commands/ppt.md` |
| T-22 | Material merge deduplication | P2 | S | `commands/ppt.md` |
| T-23 | Cognitive design principles | P2 | M | `outline-architect.md`, `reviewer.md` |
| T-24 | Score trajectory tracking | P2 | S | `commands/ppt.md` |
| T-25 | HTML preview improvements | P2 | M | `preview-template.html` |
| T-26 | Hard Stop UX quality | P2 | M | `commands/ppt.md` |
| T-27 | Artifact schema validators | P2 | M | New validation scripts |

## Critical Path

```
T-01 → T-07+T-09 → [calibration gate] → T-13 → T-17
```
