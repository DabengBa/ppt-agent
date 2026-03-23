# Wave 1 Finalized Changes (T-11, T-12, T-14)

**Date**: 2026-03-23
**Strategy**: Gemini prototype as primary base (0 blockers), merged with specific Codex strengths per cross-review audits.

---

## Summary of Merge Decisions

| Task | Primary Source | Merged From Codex | Rationale |
|------|---------------|-------------------|-----------|
| T-11 | Gemini atomic write structure | `python3` validation (replacing `jq`), orphaned `.tmp.json` cleanup in resume detection | `jq` not guaranteed in all environments (audit-codex.md suggestion #1) |
| T-12 | Gemini 3-zone color model + reviewer hard rules | Check #5 Color Zone Compliance in Post-Generation Validation | Gemini lacked automated pre-review check (audit-codex.md test gap #1) |
| T-14 | Gemini holistic review (explicit scoring table) | Visual weight assignment rules, expanded Page Type Definitions with Default Weight column | Gemini scoring table solves Codex "unscorable formula" blocker; Codex rules are more detailed |

---

## File: `commands/ppt.md`

### Change 1: Resume detection with orphaned temp file cleanup (T-11)

**Lines affected**: 98-108 (resume detection block)

Added two new bullet points at the top of the resume detection cascade:
- Delete orphaned `slide-status.tmp.json` before checking resume artifacts (from Codex Change 1)
- Validate `slide-status.json` with `python3` before trusting it; stop on validation failure (from Codex Change 1)
- Changed "slide-status.json exists" to "Valid slide-status.json exists" and "no slide-status.json" to "no valid slide-status.json"

### Change 2: Atomic write protocol for incremental progress tracking (T-11)

**Lines affected**: 185-208 (incremental progress tracking section)

Replaced the simple "append immediately" instruction with Gemini's full atomic write protocol, but substituted `python3` validation for `jq` (from Codex Change 2):
- Full write-validate-rename protocol (7 steps)
- `python3 -c "import json, sys; json.load(open(sys.argv[1]))"` instead of `jq -e .`
- Explicit failure handling: delete temp file, keep last good state
- Resume section now includes `.tmp.json` deletion on `--run-id` resume

---

## File: `agents/slide-core.md`

### Change 3: 3-zone color model in SVG Requirements (T-12)

**Lines affected**: 101-106 (SVG Requirements section)

Replaced single-line `Colors from style YAML -- no hardcoded values.` with Gemini's structured 3-zone model:
- **Zone 1 -- Mandatory Core**: Semantic tokens only for backgrounds, text, cards, dividers, UI icons
- **Zone 2 -- Chart Colors**: `chart_colors` array from style YAML, with hue-rotation fallback
- **Zone 3 -- Decorative Free**: Arbitrary colors allowed with `data-decorative="true"` or inside `<defs>`
- Heavy-decoration parent `<g>` wrapping guidance

### Change 4: Check #5 Color Zone Compliance in Post-Generation Validation (T-12)

**Lines affected**: 81-88 (Post-Generation Validation section)

Added new automated check from Codex Change 4, inserted after Check #4 (Safe Area Boundary):
- Checks all `fill`, `stroke`, and `stop-color` attributes against the 3-zone model
- Zone-specific validation rules matching the SVG Requirements definitions
- Updated closing paragraph to mention "broken color scoping" in the error catch list

---

## File: `skills/gemini-cli/references/roles/reviewer.md`

### Change 5: 3-zone color rules in hard rules table (T-12)

**Lines affected**: 31-33 (Quality Standards table)

Replaced single `Style tokens` row with three zone-specific rows from Gemini Change 3:
- `Color zone 1 (Mandatory Core)` -- Major severity
- `Color zone 2 (Chart/Data)` -- Minor severity
- `Color zone 3 (Decorative Free)` -- Pass (exempt)

### Change 6: 5-dimension holistic review framework with scoring table (T-14)

**Lines affected**: 283-328 (Holistic Deck Review section)

Replaced basic 5-point list with Gemini's comprehensive framework (Change 6):
- **Quantitative trigger table** with weights summing to 100% (25+20+20+20+15)
- **Dimension details** with concrete flag criteria and deck-size adaptations
- **Decorative exemption** in Color Story -- consistent with T-12 zone model
- **Holistic Scoring Output table** with per-dimension 0-10 scores (solves Codex "unscorable formula" blocker)
- Explicit instruction: "assign a score from 0-10 based on the quantitative triggers and qualitative assessment"
- Legacy `visual_weight` fallback: infer from page type (`quote`/`image`=low, `content`/`process`=medium, `data`/`comparison`=high)

---

## File: `skills/_shared/references/prompts/outline-architect.md`

### Change 7: `visual_weight` field in page schema (T-14)

**Lines affected**: 57 (page schema JSON block)

Added `"visual_weight": "low|medium|high"` between `layout_hint` and `transition_cue` in the outline.json page schema. Both prototypes agreed on placement.

### Change 8: Visual Weight Assignment rules + expanded Page Type Definitions (T-14)

**Lines affected**: 85-111 (Speaker Notes Schema through Page Type Definitions)

Added new `### Visual Weight Assignment` section from Codex Change 7:
- Three behavioral rules (MUST emit, legacy fallback to `medium`, emphasis vs. priority distinction)
- Assignment table mapping weight values to use cases and typical signals

Replaced Page Type Definitions table with Codex's expanded version (Change 7):
- Added `Default Weight` column mapping each page type to low/medium/high
- Expanded layout hints to full names (`mixed_grid` instead of `mixed`, `three_column` instead of `three`)
- Added closing note: "These defaults are guidance, not a hard lock."

### Change 9: Visual weight distribution guideline in Structure Guidelines (T-14)

**Lines affected**: 123 (Structure Guidelines section)

Added Gemini's visual weight distribution guideline (Change 5) after "Ensure logical flow between pages within each part":
- Avoid 3+ consecutive high-weight slides without a breathing slide
- Rhythm pattern guidance: high-medium-low-medium-high
- Cover and end pages noted as inherently low weight

---

## Cross-File Consistency Verification

| Token/Concept | slide-core.md | reviewer.md | outline-architect.md |
|---------------|---------------|-------------|----------------------|
| `data-decorative="true"` | Zone 3 definition (Ch.3) + Check #5 (Ch.4) | Zone 3 row (Ch.5) + Color Story exemption (Ch.6) | N/A |
| `chart_colors` | Zone 2 definition (Ch.3) | Zone 2 row (Ch.5) | N/A |
| `visual_weight` enum | N/A | Holistic dims 1,2,3,5 (Ch.6) | Schema (Ch.7) + Assignment rules (Ch.8) + Distribution (Ch.9) |
| Legacy `visual_weight` fallback | N/A | Infer from page type (Ch.6) | Treat as `medium` (Ch.8) |
| `<defs>` implicit decorative | Zone 3 definition (Ch.3) | Zone 3 row (Ch.5) + Color Story (Ch.6) | N/A |
| Short deck relaxation | N/A | Dims 1 (<5), 3 (infer), 5 (<=5) (Ch.6) | N/A |
| `python3` validation | N/A (not in slide-core scope) | N/A | N/A |

All cross-file references are consistent across the 4 modified files.

---

## Blockers Resolved

1. **Codex T-11 "Concurrent Write Data Loss"**: Not applicable -- the lead orchestrator updates `slide-status.json` sequentially after each agent completion signal; parallel slide-core agents do not write to this file directly (per audit-codex.md analysis).
2. **Codex T-14 "Unscorable Formula"**: Resolved by using Gemini's explicit scoring table with instruction to "assign a score from 0-10" per dimension before computing weighted sum.

## Audit Suggestions Addressed

1. **audit-codex.md suggestion #1** (Replace `jq` with `python3`): Applied in Changes 1-2.
2. **audit-codex.md test gap #1** (No automated Color Zone Compliance check): Applied in Change 4 by merging Codex's Check #5.
