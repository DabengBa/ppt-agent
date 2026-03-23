# Implementation Analysis: Wave 1 Tasks (T-11, T-12, T-14)

> Source: Codex-core analysis (fallback: direct reasoning over source files; codex-cli provider unavailable — packycode 502)
> Date: 2026-03-23
> Files analyzed: commands/ppt.md, agents/slide-core.md, skills/gemini-cli/references/roles/reviewer.md, skills/_shared/references/prompts/outline-architect.md

---

## T-11: slide-status.json Atomic Write

### Target Location

**File**: `commands/ppt.md`, Phase 6 section (lines 179-193)

The current "Incremental progress tracking" paragraph at line 183 says:
> After each slide completes its design->review cycle (pass or accepted_with_warning), append its entry immediately.

This is the instruction to the lead orchestrator. It describes a direct write with no safety mechanism. The change inserts an atomic write protocol between "append its entry" and the JSON format example.

### Exact Change

**Insert after line 183** (after "append its entry immediately"), replace the implicit direct-write instruction with an explicit atomic write subsection:

```markdown
**Atomic write protocol**: All updates to `slide-status.json` MUST use the write-validate-rename pattern to prevent corruption on crash:

1. Write the updated JSON to `${RUN_DIR}/slide-status.tmp.json`
2. Validate the temp file is well-formed JSON:
   ```bash
   python3 -c "import json,sys; json.load(open(sys.argv[1]))" "${RUN_DIR}/slide-status.tmp.json"
   ```
   If validation fails, discard the `.tmp.json` and log the error. The previous `slide-status.json` remains intact.
3. Atomically replace: `mv "${RUN_DIR}/slide-status.tmp.json" "${RUN_DIR}/slide-status.json"`

The `mv` within the same directory is atomic on POSIX filesystems. A crash during step 1 or 2 leaves `slide-status.json` with the last valid state. At worst, progress for one slide is lost — never the entire file.
```

Additionally, update the resume logic paragraph (line 192-193) to add `.tmp.json` cleanup:

```markdown
On `--run-id` resume: read `slide-status.json`, skip slides already marked `passed` or `accepted_with_warning`, and continue from the first incomplete slide. If `slide-status.tmp.json` exists on resume, delete it (orphaned from a prior crash).
```

### Why python3 instead of jq

Gemini's analysis assumes `jq` availability. I disagree with this dependency choice:

1. **`python3` is already a hard dependency** of this project (the codebase imports Python modules). `jq` is not referenced anywhere in the existing codebase and is not guaranteed on all target systems.
2. The Python one-liner (`json.load`) is functionally equivalent for validation purposes and avoids adding a new binary dependency.
3. If `jq` were already used elsewhere in the codebase, I would agree. It is not.

**Alternative**: If the orchestrator runs entirely within Claude Code (which uses `Write` tool, not `bash`), then the "atomic write" is actually an instruction to the LLM lead, not a shell script. In that case, the instruction should be:
- Write to `.tmp.json` path first (via Write tool)
- Read back the `.tmp.json` and parse as JSON (via Bash `python3 -c ...`)
- If valid, rename via Bash `mv`
- If invalid, delete `.tmp.json` via Bash `rm`

This is what the lead orchestrator (an LLM agent) would actually execute. The instructions in `ppt.md` should be written for an LLM executor, not a shell script.

### Cross-File Consistency

- **Minimal risk**. Only `commands/ppt.md` is modified. No other file references the write mechanism for `slide-status.json`.
- **Resume logic** (same file, lines 99-100): Already reads `slide-status.json` by name. No change needed since `.tmp.json` is never the canonical path.
- **Review manifest generation** (same file, line 239): Reads from `slide-status.json`. No change needed.

### Edge Cases

| Case | Behavior |
|------|----------|
| Crash during `.tmp.json` write | `.tmp.json` is truncated/empty; validation would fail; original preserved |
| Disk full during write | `.tmp.json` partial; validation fails; original preserved |
| Crash between validation and `mv` | `.tmp.json` is valid but not renamed; resume detects and cleans up |
| Parallel slide completions | Two agents finish simultaneously; lead processes them sequentially (lead is single-threaded). No race condition on the JSON file. |
| First write (no prior file) | `mv` creates new file; no atomicity concern since there is no prior state to corrupt |

### Verification

1. After editing, confirm `slide-status.tmp.json` appears exactly once in the atomic write section and once in the resume cleanup section.
2. Confirm no other references to `.tmp.json` exist outside these two locations.
3. Confirm the existing `slide-status.json` format example (lines 186-191) is unchanged.

---

## T-12: Guided-Freedom Color Enforcement

### Overview

Two files must change in lockstep: the generator (`slide-core.md`) and the evaluator (`reviewer.md`). A mismatch between them causes either false-positive review failures or silently accepted violations.

### Change 1: agents/slide-core.md

**Target**: SVG Requirements section (lines 88-101)

**Remove** line 94:
```
- Colors from style YAML — no hardcoded values.
```

**Replace with** a 3-zone color model section:

```markdown
- **Color zones** (guided-freedom model):
  - **Zone 1 — Mandatory Core**: Background fills, primary text, card backgrounds, headings, and body text MUST use semantic tokens from style YAML (`primary`, `secondary`, `accent`, `text`, `text_secondary`, `background`, `card_bg`). No exceptions.
  - **Zone 2 — Chart / Data**: Data visualization elements (bars, lines, pie segments, metric indicators) MUST sequence through the `chart_colors` array from style YAML. If `chart_colors` is not defined in the style, derive from `primary` and `accent` with 20% hue rotation steps.
  - **Zone 3 — Decorative Free**: Gradients, glows, abstract background shapes, pattern fills, decorative illustrations, and ornamental elements MAY use arbitrary colors. These elements MUST be marked with `data-decorative="true"` on the element itself or on a parent `<g>` wrapper. Colors inside `<defs>` (gradient stops, filter primitives) are implicitly decorative and do not require the attribute.
  - When generating decorative elements, prefer applying `data-decorative="true"` to a parent `<g>` container rather than to each individual path/shape. This reduces attribute noise and ensures the reviewer correctly classifies the entire group.
```

**Also add** a post-generation validation check. After the existing "### 4. Safe Area Boundary" section (line 79), add:

```markdown
### 5. Color Zone Compliance
Verify that non-decorative elements use only style YAML colors:
```bash
# Extract all fill/stroke values from non-decorative elements
# Elements with data-decorative="true" or inside <defs> are excluded
grep -oP '(?:fill|stroke)="[^"]*"' "${run_dir}/slides/slide-${slide_index}.svg" | grep -v 'none\|url(' | sort -u
```
Compare extracted colors against the style YAML palette. Flag any non-token color on a non-decorative element as a warning. This is a soft check — the reviewer will catch violations authoritatively, but catching them early avoids a wasted review round.
```

### Change 2: skills/gemini-cli/references/roles/reviewer.md

**Target**: Quality Standards table (lines 19-33)

**Remove** the existing style tokens row (line 31):
```
| Style tokens | All colors from declared style YAML | Minor for semantic extensions, Major for random colors |
```

**Replace with** three rows implementing the 3-zone model:

```markdown
| Color — Zone 1 (Core) | Background, text, card fills use only semantic style tokens | Major |
| Color — Zone 2 (Chart) | Data viz elements use `chart_colors` array from style YAML | Minor if within palette family, Major for clashing hues |
| Color — Zone 3 (Decorative) | Elements with `data-decorative="true"` or inside `<defs>` — any color allowed | Pass (no violation) |
| Color — Untagged arbitrary | Non-token color on element missing `data-decorative="true"` and not in `<defs>` | Warning: suggest adding `data-decorative="true"` if decorative intent is likely; Major if element is clearly semantic |
```

**Also update** the Scoring Guidelines section. In the Color Harmony criterion description, add:

```markdown
Color Harmony evaluates palette cohesion across all three zones. Decorative colors are not penalized for deviating from the style YAML, but they ARE evaluated for harmony with the overall palette. A decorative gradient that clashes with the core palette is a design issue (score 5-6), not a compliance violation.
```

### Cross-File Consistency

| Risk | Mitigation |
|------|-----------|
| slide-core generates `data-decorative` but reviewer doesn't recognize it | Both files must be committed together. The attribute name `data-decorative="true"` must be identical in both files. |
| Reviewer penalizes colors in `<defs>` | reviewer.md explicitly exempts `<defs>` in the Zone 3 row. |
| Heavy-decoration styles (watercolor, sketch-notes) produce many decorative elements | slide-core instruction says to use parent `<g>` wrappers, reducing the number of individual attributes the reviewer must parse. |
| Existing SVGs lack `data-decorative` attribute | Old SVGs from prior runs will trigger "Untagged arbitrary" warnings on resume. This is acceptable — the reviewer suggests adding the attribute rather than hard-failing. |

### Edge Cases

| Case | Behavior |
|------|----------|
| Style YAML lacks `chart_colors` | slide-core derives from primary+accent with hue rotation. Reviewer should accept colors within hue family of primary/accent as Zone 2 compliant. |
| All elements are decorative (e.g., full-bleed illustration slide) | The slide would have only Zone 3 elements. Reviewer should not penalize but may flag if there is no semantic content at all. |
| `data-decorative` on a `<text>` element | Technically allowed but suspicious — reviewer should flag as Warning since text is almost always semantic. |
| Inline `style` attribute colors vs. XML attribute colors | Both `fill="..."` and `style="fill:..."` must be checked. The reviewer instructions should mention both syntaxes. |

### Verification

1. Grep `slide-core.md` for "no hardcoded values" — must be gone.
2. Grep `slide-core.md` for "data-decorative" — must appear in Zone 3 description and validation section.
3. Grep `reviewer.md` for "All colors from declared style YAML" — must be gone.
4. Grep `reviewer.md` for "Zone 1", "Zone 2", "Zone 3" — all three must appear in the Quality Standards table.
5. Confirm attribute name is exactly `data-decorative="true"` in both files (not `data-deco`, `decorative`, etc.).

---

## T-14: Holistic Deck Review Design

### Change 1: outline-architect.md — visual_weight field

**Target**: JSON schema in Output Format section (lines 30-73)

**Add** `visual_weight` to the page object, after `layout_hint`:

```json
"layout_hint": "single_focus|two_column|three_column|hero_grid|mixed_grid",
"visual_weight": "low|medium|high",
```

**Add** a definition section after the Speaker Notes Schema section (after line 82):

```markdown
### Visual Weight Assignment

The `visual_weight` field indicates the visual density and emphasis level of each page. It is used by the holistic deck review to evaluate rhythm and pacing.

| Weight | Assignment Rule | Typical Page Types |
|--------|----------------|-------------------|
| `low` | Breathing slides with minimal content: quotes, single images, section dividers, thank-you/Q&A | quote, image, end_page, table_of_contents |
| `medium` | Standard content delivery with moderate information density | content, comparison (2 columns) |
| `high` | Data-dense, multi-element, or climax slides that demand concentrated attention | data, process (>3 steps), comparison (3+ columns), timeline (>4 nodes) |

Cover pages default to `medium` unless they contain a complex visual (then `high`).

When assigning visual_weight, consider both the `type` and `key_points` count:
- 0-1 key_points with single_focus layout -> `low`
- 2-3 key_points -> `medium`
- 4+ key_points or dashboard/hero_grid layout -> `high`
```

**Also update** the Page Type Definitions table (lines 84-96) to add a Weight column:

```markdown
| Type        | Purpose                              | Typical Layout      | Default Weight |
| ----------- | ------------------------------------ | ------------------- | -------------- |
| content     | Text-focused information delivery    | two_column, mixed   | medium         |
| data        | Charts, statistics, metrics          | hero_grid, mixed    | high           |
| comparison  | Side-by-side analysis                | two_column, three   | medium-high    |
| process     | Step-by-step flow or timeline        | hero_grid, mixed    | medium         |
| quote       | Key quote or testimonial             | single_focus        | low            |
| image       | Visual-dominant with minimal text    | single_focus, hero  | low            |
| timeline    | Sequential process or chronological  | hero_grid, mixed    | medium         |
```

### Change 2: reviewer.md — Expanded Holistic Review

**Target**: Holistic Deck Review section (lines 281-294)

**Replace** the current 5-dimension list (lines 283-289) with a detailed protocol:

```markdown
## Holistic Deck Review (mode=holistic)

Run once after all individual slides pass review. Evaluate across the full set of `slides/slide-*.svg` with `outline.json` as the structural reference.

**Required inputs**:
- All `slides/slide-*.svg` files
- `outline.json` (for `visual_weight`, `type`, and narrative structure)
- All `reviews/review-{nn}.md` per-slide results (for score context)

### Assessment Dimensions

#### 1. Visual Rhythm (Weight: 25%)
Evaluate the alternation between high-weight and low-weight slides.

**Quantitative triggers**:
- Flag if 3+ consecutive slides share the same `visual_weight` level
- Flag if 3+ consecutive slides use the same `layout_hint`
- Flag if no `low` weight slide appears in any 5-slide window (missing breathing room)
- For decks < 6 slides: relax to 4+ consecutive same-weight before flagging

**Assessment**: Do layouts alternate between dense and sparse? Are there breathing slides between data-heavy sections?

#### 2. Color Story (Weight: 20%)
Evaluate accent color distribution across the deck.

**Quantitative triggers**:
- Flag if accent color appears on >70% of slides (overuse = no emphasis)
- Flag if accent color never appears on the highest-weight slide (missed climax)
- Flag if accent usage has no discernible pattern (random rather than escalating)

**Assessment**: Does accent color usage escalate toward key slides? Is there a color narrative from setup through climax?

#### 3. Narrative Arc (Weight: 25%)
Evaluate whether the slide sequence follows the expected progression framework.

**Quantitative triggers**:
- Map slides to arc phase: Setup (~15%), Tension (~60%), Resolution (~25%)
- Flag if the highest `visual_weight` slide is in the first 20% (premature climax)
- Flag if no `high` weight slide exists in the Tension phase (flat arc)
- Flag if Resolution section has higher average weight than Tension (anti-climactic)

**Assessment**: Do slides follow Setup -> Tension -> Resolution? Does the strongest visual moment align with the narrative peak?

#### 4. Style Consistency (Weight: 20%)
Evaluate cross-slide visual coherence.

**Quantitative triggers**:
- Flag if border-radius values differ by >4px across slides
- Flag if shadow definitions (blur, offset, color) vary between slides without semantic reason
- Flag if heading font-size varies by >4px across same-type slides
- Flag if card gap differs by >8px across slides

**Assessment**: Are shadows, corners, font sizes, and spacing consistent? Does the deck feel like a unified design system?

#### 5. Pacing (Weight: 10%)
Evaluate the distribution of slide types for audience engagement.

**Quantitative triggers**:
- Flag if no quote/image/single_focus slide in a deck of 8+ slides
- Flag if >50% of slides are the same type
- Flag if data slides are clustered (3+ adjacent) without a breathing slide between them
- For decks < 8 slides: skip pacing check (insufficient slides for meaningful rhythm)

**Assessment**: Are there enough variety and "breathing" slides to prevent cognitive fatigue?

### Holistic Scoring

| Dimension | Weight |
|-----------|--------|
| Visual Rhythm | 25% |
| Narrative Arc | 25% |
| Color Story | 20% |
| Style Consistency | 20% |
| Pacing | 10% |

Overall coherence score = weighted sum. Gate: >= 7/10 to pass. If < 7, flag specific issues for lead orchestrator but do not block delivery.

### Output Format

Use the standard review structure but with `deck_coordination` type suggestions only. Each suggestion must reference specific slide indices and include a concrete fix recommendation.

Output: `${run_dir}/reviews/review-holistic.md`
```

### Cross-File Consistency

| Risk | Mitigation |
|------|-----------|
| outline.json generated before this change lacks `visual_weight` | Reviewer must handle missing field gracefully: "If `visual_weight` is absent from outline.json pages, infer weight from `type` using the Default Weight mapping in outline-architect.md." Add this instruction to the holistic review section. |
| `deck_coordination` suggestion type already defined in Suggestion Taxonomy (line 140-159) | The holistic review expansion references but does not redefine this type. No conflict. Verify the `deck_coordination` schema remains compatible. |
| commands/ppt.md holistic review dispatch (line 231-236) | Already dispatches `mode=holistic` and handles results. No change needed in ppt.md for T-14. |
| Short decks (< 6 slides) | Quantitative triggers include explicit relaxation rules for short decks in dimensions 1 and 5. |

### Edge Cases

| Case | Behavior |
|------|----------|
| All slides are `medium` weight | Visual Rhythm flags monotonous weight sequence; suggests converting 1-2 to `low` (breathing) |
| Deck has only 3 slides | Pacing check skipped (< 8). Rhythm check relaxed (4+ consecutive trigger). Narrative arc still checked but with proportional phase mapping. |
| Outline.json has no `visual_weight` (legacy) | Reviewer infers from `type` + Default Weight table. Functions correctly but with less precision. |
| Single-part deck (no logical sections) | Narrative arc still maps to Setup/Tension/Resolution by slide position percentage. |

### Verification

1. Grep `outline-architect.md` for `visual_weight` — must appear in JSON schema, assignment rules table, and page type table.
2. Grep `reviewer.md` for "Visual Rhythm", "Color Story", "Narrative Arc", "Style Consistency", "Pacing" — all 5 must appear as H4 headings under the Holistic section.
3. Verify each dimension has a "Quantitative triggers" subsection with specific thresholds.
4. Confirm the holistic scoring weights sum to 100%.
5. Confirm `deck_coordination` type references are consistent with the existing Suggestion Taxonomy.

---

## Implementation Ordering

### Dependency Graph

```
T-11 (ppt.md only)          T-14 (outline-architect.md + reviewer.md)
        |                              |
   [independent]              T-12 (slide-core.md + reviewer.md)
                                       |
                              [T-14 and T-12 share reviewer.md]
```

### Recommended Sequence

**Track A (immediate)**: T-11
- Touches only `commands/ppt.md`
- Zero overlap with T-12 or T-14
- Pure mechanical change, lowest risk
- Can be implemented and verified independently

**Track B (sequential)**: T-14 first, then T-12
- Both T-14 and T-12 modify `reviewer.md`
- T-14 changes are at the bottom of reviewer.md (Holistic section, lines 281+)
- T-12 changes are in the middle (Quality Standards table, lines 19-33, and Color Harmony criterion)
- Doing T-14 first avoids merge conflicts: T-14 appends content at the bottom while T-12 edits the middle
- If done in reverse order, T-12's table changes might shift line numbers for T-14's target section

**Parallel execution**: T-11 can run fully in parallel with Track B.

### Agreement with Gemini Analysis

I **agree** with Gemini on:
- T-11 as an independent parallel track
- T-14 before T-12 ordering for reviewer.md conflict avoidance
- The 3-zone model structure for T-12
- `data-decorative="true"` as the attribute mechanism
- Parent `<g>` wrapper pattern for heavy-decoration styles
- `visual_weight: low|medium|high` enum for T-14
- Short deck threshold adjustments

I **disagree** with Gemini on:
1. **jq dependency (T-11)**: Gemini assumes `jq` is available. The project has no existing `jq` dependency. Use `python3 -c "import json..."` instead, which is already a project dependency. Alternatively, since the orchestrator is an LLM agent using tool calls (not a shell script), the "atomic write" is an instruction to the agent, not a shell snippet — frame it accordingly.
2. **Infinite loop guard (T-14)**: Gemini suggests a `deck_coordination_pass` flag to prevent re-running holistic suggestions. This is unnecessary — `commands/ppt.md` already specifies holistic review runs exactly once ("after ALL individual slides have reviews") and holistic suggestions are "not auto-fixed — reported for user review." There is no loop to guard against.
3. **Orchestrator blind spot (T-14)**: Gemini flags that `commands/ppt.md` might need updating for the deck_coordination feedback loop. I disagree — the existing ppt.md Phase 6 step 5 already handles holistic review dispatch and states suggestions are advisory. No ppt.md change is needed for T-14.

---

## Risk Assessment

### High Risk

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Generator/reviewer desync on `data-decorative` (T-12) | False positives flood review, wasting fix budget | Commit slide-core.md and reviewer.md changes atomically. Verify attribute name identical in both. |
| Holistic review overwhelms with false-positive rhythm flags (T-14) | Every deck gets 5+ deck_coordination suggestions regardless of quality | Tune quantitative triggers conservatively. "3+ consecutive same-weight" is the threshold — not 2. Short deck exemptions prevent noise on small decks. |

### Medium Risk

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Legacy outline.json lacks `visual_weight` (T-14) | Holistic review degrades to type-based inference | Add explicit fallback instruction in reviewer.md. Inference from type+Default Weight table provides reasonable accuracy. |
| `python3` unavailable in some sandboxed environments (T-11) | JSON validation step fails; atomic write becomes non-validated write | The `mv` still provides atomicity even without validation. Wrap the python3 check in `if command -v python3` guard. |
| Inline `style="fill:..."` syntax not caught by reviewer color check (T-12) | Semantic color violations in CSS syntax bypass Zone 1 enforcement | Add explicit note in reviewer.md that both XML attribute (`fill="..."`) and CSS property (`style="fill:..."`) must be checked. |

### Low Risk

| Risk | Impact | Mitigation |
|------|--------|-----------|
| `visual_weight` assignment disagreement between architect and reviewer | Minor mismatch in rhythm assessment | Default Weight table in outline-architect.md is the single source of truth; reviewer references it. |
| Atomic write adds ~3 lines of instruction to ppt.md | Negligible prompt size increase | No action needed. |
