# Implementation Context — PPT Agent Optimization

> Gathered from source file analysis on 2026-03-23.
> Each section documents current state, specific change points, and coupling constraints.

---

## 1. agents/review-core.md

**Current state**:
- Frontmatter tools: `[Read, Write, Skill, SendMessage]` — **Bash is missing** (line 3-8)
- `maxTurns: 15` (line 13)
- `memory: project` (line 9)
- `model: sonnet` (line 10)
- Pre-Review Automated Checks section (lines 33-42) lists 5 checks requiring Bash (xmllint, viewBox, font-size, color compliance, safe area) — all are dead code without Bash tool
- Execution step 6 (lines 53-57) calls `Skill(skill="ppt-agent:gemini-cli")` for review
- Step 7 (lines 58-61) handles Gemini fallback — currently says "Fall back to Claude self-optimization" (needs rewording to "technical validation only")
- Step 8 (lines 62-72) writes review with score + structured fix JSON
- Holistic mode section (lines 77-79) evaluates cross-slide consistency

**Changes needed**:
- **FR-01**: Add `Bash` to frontmatter tools array (between `Write` and `Skill`, or at end)
- **FR-05**: Change `maxTurns: 15` to `maxTurns: 20`
- **FR-07**: Rewrite execution steps 6-8 to use optimization framing instead of compliance framing
- **FR-08**: Rewrite step 7 fallback path — replace "Claude self-optimization" with "technical validation only — aesthetic optimization skipped"
- **FR-09**: Update step 8 structured fix JSON to include `suggestion_type` and `layout_suggestion` fields
- **FR-18** (Wave 4): Remove "before writing final output" from heartbeat instruction (line 48)
- **FR-19** (Wave 4): Change `memory: project` to `memory: none`

**Coupling**: review-core prompt structure is tightly coupled with reviewer.md output format and SKILL.md prompt template. Changes to fix JSON format must be synchronized across all three.

---

## 2. agents/content-core.md

**Current state**:
- `maxTurns: 25` (line 13)
- `model: opus` (line 10)
- Draft mode (lines 74-82): sends `draft_slide_ready(index=N)` per-slide after EACH draft (line 81)
- No issues with tool list or prompt structure

**Changes needed**:
- **FR-02**: Change `maxTurns: 25` to `maxTurns: 35`
- **FR-03**: Change line 81 from "After writing EACH slide draft, send `draft_slide_ready(index=N)`" to batched signaling: "After every 3rd slide (and the final slide), send `draft_slide_ready(index=N)` with the batch of completed indices"
- **FR-18** (Wave 4): Heartbeat reduction

**Coupling**: Signal batching change must be synchronized with `commands/ppt.md` Phase 5-6 pipeline logic, which currently expects per-slide signals.

---

## 3. agents/slide-core.md

**Current state**:
- `maxTurns: 30` (line 14)
- `model: opus` (line 11)
- `memory: project` (line 9)
- Tools include `Bash` (line 9) — already has Bash, unlike review-core
- Execution step 3 (lines 43-49): applies fixes from `fixes_json` as deterministic attribute patches
- Post-Generation Validation section (lines 53-75): 4 automated checks (XML, viewBox, font-size, safe area) — these work because slide-core HAS Bash
- Fix handling (line 49): "Fixes are deterministic patches, not generative reinterpretation" — this needs to change for suggestion-driven strategy (FR-13)

**Changes needed**:
- **FR-04**: Change `maxTurns: 30` to `maxTurns: 20`
- **FR-09**: Update fix handling to document response to different suggestion types (attribute_change -> patch, layout_restructure -> regenerate with constraints, full_rethink -> regenerate from scratch, content_reduction -> regenerate simplified)
- **FR-13**: Rewrite execution step 3 fix handling from "deterministic patches" to type-aware execution
- **FR-17** (Wave 4): Support model override for attribute_change fixes (sonnet vs opus). Blocked by UD-1.
- **FR-18** (Wave 4): Heartbeat reduction
- **FR-19** (Wave 4): Change `memory: project` to `memory: none`

**Coupling**: Fix handling changes must match reviewer.md fix JSON format exactly. slide-core's deterministic patch assumption is load-bearing for the current fix loop.

---

## 4. commands/ppt.md

**Current state**:
- Phase 5 (lines 144-152): `draft_slide_ready(index=N)` per-slide signal. Line 152: "content-core sends `draft_slide_ready(index=N)` per-slide as each draft completes"
- Phase 6 pipeline (lines 154-167): sliding window of `min(3, remaining_slides)`, slide-status.json incremental tracking
- Phase 6 fix loop (lines 185-199): **score-driven** strategy:
  - Score >= 7.0: pass
  - Score 5.0-6.9: fix loop, max 2 rounds
  - Score 3.0-4.9: fix loop, max 1 round
  - Score < 3.0: regenerate from scratch
- Resume detection (lines 76-83): checks artifact existence to determine resume point. **No `approved` field check** for outline.json — if outline.json exists, resume skips to Phase 5 regardless of approval status
- Fallback rules (lines 336-339): line 339 says "review-core falls back to Claude self-review using the same quality standards" — needs update for "technical validation only"
- slide-status.json write (lines 158-167): no atomic write pattern

**Changes needed**:
- **FR-03**: Update Phase 5 description (line 152) to reflect batched signals. Update Phase 6 pipeline trigger to handle batch of indices.
- **FR-06**: Add `approved` field check to resume detection. Between lines 79-80, when `outline.json` exists, also check `approved === true`. If false/missing, resume at Phase 4 (not Phase 5).
- **FR-08**: Update fallback rules (line 339) from "Claude self-review using the same quality standards" to "technical validation only"
- **FR-11**: Add atomic write pattern for slide-status.json (write .tmp, validate, rename)
- **FR-13**: Rewrite Phase 6 fix loop (lines 185-199) from score-driven to suggestion-driven routing
- **FR-14**: Update holistic review invocation (lines 201-206) with enhanced protocol
- **FR-20** (Wave 4): Adaptive sliding window replacing fixed `min(3, remaining)`
- **FR-21** (Wave 4): Structured section extraction for Phase 3
- **FR-22** (Wave 4): Deduplication in Phase 3 merge
- **FR-24** (Wave 4): Score trajectory in slide-status.json
- **FR-26** (Wave 4): Phase 2 and Phase 4 Hard Stop UX

**Coupling**: This is the orchestrator — nearly every change touches it. Phase 6 fix loop logic must be synchronized with review-core output format and slide-core fix handling. Resume logic must be synchronized with outline.json schema.

---

## 5. skills/gemini-cli/SKILL.md

**Current state**:
- Step 4 (lines 79-82): Exit code 2 handling says "optimization must still happen, just without the cross-model perspective" (line 81). **This contradicts the corrected understanding** — Claude self-review cannot do aesthetic optimization.
- Prompt template (lines 92-123): Uses `## Review Criteria` heading (line 108) — should be `## Optimization Criteria`
- Fallback Strategy section (lines 127-135): Describes Claude self-optimization with same structured process. Needs rewrite to "technical validation only".
- Constraints table (lines 148-156): "MUST fall back to self-review on exit 2" is correct in direction but needs wording update

**Changes needed**:
- **FR-07**: Change prompt template `## Review Criteria` (line 108) to `## Optimization Criteria`
- **FR-08**: Rewrite line 81 from "optimization must still happen, just without the cross-model perspective" to "fall back to technical validation only — aesthetic optimization requires Gemini's independent perspective and cannot be self-performed"
- **FR-08**: Rewrite Fallback Strategy section (lines 127-135): Claude fallback performs technical validation checks only, not the same structured optimization. Mark output as "technical validation only".
- **FR-08**: Update Constraints table: "MUST fall back to technical validation on exit 2"

**Coupling**: SKILL.md is the canonical policy document for Gemini usage. review-core and ppt.md both reference it. Internal contradictions (like line 81) propagate confusion to all consumers.

---

## 6. skills/gemini-cli/references/roles/reviewer.md

**Current state**:
- Title: "PPT Slide Layout & Aesthetic Optimizer" (line 1) — correct framing
- Focus section (lines 6-10): 5 criteria, correct
- Optimization Methodology (lines 12-16): "Think like a designer, not an auditor" — correct framing
- Quality Standards table (lines 20-32): hard rules with severity levels — these are the technical validation rules
- Output Format (lines 52-100): Structured review with scores + fix suggestions
- Fix Suggestion Format (lines 104-129): JSON array with `element`, `selector_hint`, `attribute`, `current`, `target`, `severity`, `reason` — **no `suggestion_type` or `layout_suggestion` fields**
- Weighted Scoring Model (lines 140-165): Score weights and adaptive fix budget — **score-driven** routing
- Holistic Deck Review section (lines 180-191): 5 dimensions for cross-slide review

**Changes needed**:
- **FR-07**: Strengthen optimization framing throughout. Output format should lead with optimization suggestions, score secondary.
- **FR-09**: Add `suggestion_type` field (one of 5 types) and optional `layout_suggestion` string to fix JSON format. Each entry must declare its type so slide-core can route execution.
- **FR-12**: Update Color Token Compliance in Quality Standards from "Minor for semantic extensions, Major for random colors" to guided-freedom model rules.
- **FR-13**: Rewrite Adaptive Fix Budget section from score-driven to suggestion-type-driven routing.
- **FR-14**: Expand Holistic Deck Review section with full protocol (visual rhythm, color story escalation, deck_coordination suggestions).
- **FR-23** (Wave 4): Add cognitive design principles as concrete quality rules.

**Coupling**: This is the single source of truth for review output format. Changes here must be reflected in review-core.md (which parses the output) and slide-core.md (which consumes fix suggestions). The fix JSON schema change (FR-09) is the most coupling-sensitive modification.

---

## 7. skills/_shared/references/prompts/outline-architect.md

**Current state**:
- Output schema (lines 30-72): JSON with `title`, `subtitle`, `total_pages`, `cover`, `table_of_contents`, `parts[].pages[]`, `end_page`
- Page schema (lines 48-63): `index`, `title`, `type`, `key_points`, `layout_hint`, `transition_cue`, `notes`
- **No `approved` field** in schema
- **No `visual_weight` field** in page schema
- Framework Selection section (lines 111-130): auto-selection heuristic

**Changes needed**:
- **FR-06**: Add `"approved": false` to top-level schema. Document that this field is set to `true` by the lead orchestrator after user confirmation in Phase 4, never by content-core.
- **FR-14**: Add `"visual_weight": "low|medium|high"` to page schema for proactive visual planning at outline time.
- **FR-23** (Wave 4): Reference cognitive design principles more concretely in structure guidelines.

**Coupling**: outline-architect.md is the single source of truth for outline.json schema. Changes here affect content-core (which generates the JSON), ppt.md (which reads approved field), and review-core holistic mode (which reads visual_weight).

---

## 8. skills/_shared/references/prompts/svg-generator.md

**Current state**:
- Data Visualization Patterns section (lines 184-266): Chart type selection table and SVG patterns
- Available patterns: Big Number, Progress Bar, Sparkline, Donut Chart, Horizontal Bar Chart, Timeline
- **Missing patterns**: Table, Metric Card Grid, Grouped Bar, Line Chart with axes, Network Diagram
- All chart patterns use `${accent}` as sole data color — no multi-series support
- Chart Constraints (lines 199-204): max 8 bars, max 6 donut segments, prefer direct labels

**Changes needed**:
- **FR-10**: Update all chart patterns to use `chart_colors[0]`, `chart_colors[1]`, etc. for multi-series. Add note on chart_colors token from style YAML.
- **FR-15** (Wave 4): Add 5 new SVG patterns: table, metric card grid, grouped bar, line chart with axes, network/relationship diagram.

**Coupling**: svg-generator.md is referenced by both content-core (draft mode) and slide-core (design mode). Chart color changes affect all data visualization slides.

---

## 9. Style YAMLs (all 4)

**Current state for all 4 styles** (`business.yaml`, `tech.yaml`, `creative.yaml`, `minimal.yaml`):
- Have: `color_scheme` (6 colors), `typography`, `card_style`, `gradients`, `elevation`, `decoration`, `slide_type_overrides`
- **Missing**: `chart_colors` array — confirmed absent in all 4 files
- No decorative color declaration mechanism (for guided-freedom model)

**Changes needed**:
- **FR-10**: Add `chart_colors` array (6-8 hex values) to each style YAML, placed after `color_scheme`. Colors should be harmonious with the style's existing palette.
  - business.yaml: navy/blue/orange palette derivatives
  - tech.yaml: cyan/indigo/purple palette derivatives
  - creative.yaml: violet/pink/amber palette derivatives
  - minimal.yaml: blue/gray palette with subtle differentiation
- **FR-12** (Wave 3): May need `decorative_colors` declaration section for guided-freedom enforcement.

**Coupling**: Style YAMLs are read by slide-core, review-core (for color compliance), and content-core (draft mode). Changes must be backward-compatible — new keys are additive.

---

## 10. skills/_shared/index.json

**Current state**:
- Version 1.0.0, last updated 2026-03-20
- 4 prompts, 4 styles, 1 asset registered
- Style entries: business, tech, creative, minimal (all domain="style")
- All referenced files exist at declared paths

**Changes needed**:
- **FR-27** (Wave 4): If validation scripts are added as discoverable resources, add entries here. Otherwise no changes needed.
- No changes needed for Waves 1-3.

**Coupling**: index.json is read by ppt.md Phase 1 for style discovery. Adding new resources requires updating `total_count` and `resources` array.

---

## 11. agents/research-core.md

**Current state**:
- `maxTurns: 20` (line 15)
- `model: sonnet` (line 10)
- Tools include `Bash`, `WebSearch` (lines 8-9) — full tool set

**Changes needed**:
- **FR-18** (Wave 4): Heartbeat reduction only.
- No changes needed for Waves 1-3.

---

## Cross-File Synchronization Matrix

| Change | Files that must change together |
|--------|-------------------------------|
| FR-01 (Bash tool) | `review-core.md` only |
| FR-02+03 (maxTurns + batch) | `content-core.md` + `ppt.md` |
| FR-06 (approved field) | `ppt.md` + `outline-architect.md` |
| FR-07+09 (optimizer + taxonomy) | `review-core.md` + `reviewer.md` + `SKILL.md` + `slide-core.md` |
| FR-08 (self-review fallback) | `review-core.md` + `SKILL.md` + `ppt.md` |
| FR-10 (chart_colors) | 4x style YAML + `svg-generator.md` |
| FR-13 (fix strategy) | `ppt.md` + `slide-core.md` + `reviewer.md` |
