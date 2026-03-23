# Codex Architecture Plan — PPT Agent Optimization

> Generated: 2026-03-23
> Scope: Backend/system architecture decisions for all 27 FRs + 6 NFRs
> Constraint set: C1–C8, NFR-01–06

---

## Architecture Decisions

### AD-1: review-core tool list — add Bash (FR-01)

**Decision**: Append `Bash` to review-core frontmatter `tools` array after `SendMessage`.

**Rationale**: The 5 pre-review checks (xmllint, viewBox, font-size, color compliance, safe area) at lines 33–42 are dead code without Bash. This is a single-line frontmatter change with zero behavioral risk — it only enables code that already exists in the prompt.

**Risk**: None. Additive change, no backward compat concern.

### AD-2: content-core maxTurns 25→35 + signal batching (FR-02, FR-03)

**Decision**: Set `maxTurns: 35` in content-core frontmatter. Change draft signaling from per-slide to every-3-slides.

**Turn budget verification** (15-slide worst case):
- 5 reads (input, requirements, materials, outline, svg-generator) = 5
- 15 SVG writes = 15
- 5 batched signals (ceil(15/3)) = 5
- 1 manifest write = 1
- **Total: 26 turns** — 35 provides 9 turns headroom (26% margin)

Without batching: 15 signals → 36 turns → busts 35. Batching is mandatory companion to the maxTurns change.

**Signal protocol change**:
- content-core: after writing slides N, N+1, N+2, send `draft_slide_ready(indices=[N, N+1, N+2])`. On last batch (may be <3), send with whatever remains + include `final=true`.
- ppt.md Phase 5→6 pipeline: on receiving `draft_slide_ready`, launch slide-core for each index in the batch. Window cap `min(3, remaining)` still applies — if 3 slots already occupied, queue the new indices.

**Risk**: Low. Signal format change is orchestrator-internal. No external consumers.

### AD-3: slide-core maxTurns 30→20 (FR-04)

**Decision**: Set `maxTurns: 20` in slide-core frontmatter.

**Turn budget verification** (single slide):
- 5-6 reads (outline, draft, bento-grid, svg-generator, style YAML, optional brand-style) = 6
- 1 heartbeat = 1
- 1 SVG write = 1
- 4 validation checks (Bash) = 4
- 1 signal = 1
- Fix iterations: ~2 self-corrections = 2
- **Total: ~15 turns** — 20 provides 5 turns headroom (33% margin)

**Risk**: None. 30 was over-allocated by 15 turns. Even with fix rounds from FR-13, slide-core receives fixes_json as input — it doesn't do review+fix internally.

### AD-4: review-core maxTurns 15→20 (FR-05)

**Decision**: Set `maxTurns: 20` in review-core frontmatter.

**Rationale**: Holistic mode reads ALL SVGs (12+ files). At 15 turns, a 12-slide deck consumes 12 reads + 1 write + 1 signal + 1 heartbeat = 15 — zero headroom. 20 provides margin for style YAML reads and outline context.

**Risk**: None. review-core uses sonnet — extra turns are cheap.

### AD-5: outline.json `approved` field + resume guard (FR-06)

**Decision**: Add `"approved": false` to outline.json top-level schema in outline-architect.md. Orchestrator sets `approved: true` only after user confirms in Phase 4 Hard Stop.

**Schema change** (outline-architect.md):
```json
{
  "title": "...",
  "subtitle": "...",
  "approved": false,
  "total_pages": 12,
  ...
}
```

**Resume logic change** (ppt.md line 79):
```
Current:  outline.json exists but no draft-manifest.json → resume at Phase 5
Changed:  outline.json exists but no draft-manifest.json →
            if outline.json.approved === true → resume at Phase 5
            else → resume at Phase 4 (re-present for approval)
```

**Backward compat** (NFR-01): Missing `approved` field treated as `false`. Old run directories without the field will re-enter Phase 4 — safe because the user can immediately re-approve.

**Implementation**:
1. content-core generates outline.json with `"approved": false` — content-core NEVER sets this to true.
2. After user approves in Phase 4, orchestrator reads outline.json, sets `approved: true`, writes back.
3. Resume detection checks `approved` field with `=== true` (not truthy).

**Risk**: Low. Safe default (false) means worst case is an unnecessary re-approval, never a skipped approval.

### AD-6: Gemini optimizer role rewrite (FR-07)

**Decision**: Rewrite three files to shift Gemini framing from "compliance checker that also suggests" to "aesthetic optimizer that produces structured suggestions as primary output".

**Key prompt changes**:
- reviewer.md: Output format restructured — suggestions section moves ABOVE scores. Score becomes secondary judgment, not primary output.
- SKILL.md prompt template: `## Review Criteria` → `## Optimization Criteria`
- review-core.md steps 6-8: Reframe execution as "request optimization suggestions" not "request quality review"

**Atomic coupling**: FR-07 and FR-09 must ship together. The optimizer role produces typed suggestions (FR-09's taxonomy) — shipping the role without the format, or vice versa, creates a format mismatch between reviewer.md output and review-core/slide-core consumers.

**Risk**: Medium. This is the largest prompt engineering change. Mitigation: calibration gate after Wave 2.

### AD-7: Technical validation implementation — UD-2 Resolution

**Decision**: Option (b) — validation checks inlined in review-core prompt, executed via Bash tool.

**Analysis of all three options**:

| Option | Pros | Cons |
|--------|------|------|
| (a) Bash script | Reusable, testable independently | Extra file to maintain; review-core must parse script output; script has no access to style YAML context |
| **(b) Inlined in review-core** | Already partially exists (lines 33-42); review-core has full context (style YAML, outline); no new files; checks are simple one-liners | Checks are prompt-encoded, not independently testable |
| (c) Orchestrator pre-step | Separates concerns cleanly | Adds orchestrator complexity; requires new message protocol; duplicates slide-core's post-generation checks; violates NFR-02 (4-agent architecture) by moving review logic to orchestrator |

**Rationale for (b)**:
1. review-core already has the 5 checks at lines 33-42 — they just need Bash (FR-01) to execute.
2. The fallback path (Gemini unavailable) needs these same checks as its primary output. Inlining keeps the fallback path self-contained within review-core.
3. Adding text overflow estimation and outline content coverage to the check list is a prompt addition, not an architectural change.
4. Option (c) would blur the boundary between orchestrator (dispatch) and review agent (assess) — violating the star topology's separation of concerns.

**Extended technical validation checklist** (for fallback mode):
1. XML validity (xmllint)
2. ViewBox present and correct
3. Font-size floor (14px body, 12px labels)
4. Color token compliance (hex values vs style YAML)
5. Safe area margins (60px)
6. Text overflow estimation (text length vs container width)
7. Outline content coverage (key_points from outline.json present in SVG text)
8. WCAG AA contrast ratio (4.5:1 body, 3:1 large text)

Checks 1-5 are existing (currently dead). Checks 6-8 are new additions for the fallback path.

**Risk**: Low. This is the natural evolution of the existing check list.

### AD-8: Self-review fallback as technical validation only (FR-08)

**Decision**: When Gemini is unavailable (exit code 2), review-core executes ONLY the technical validation checks from AD-7. No aesthetic scores, no optimization suggestions. Output explicitly labeled "Technical Validation Only — Aesthetic Optimization Skipped".

**Three files must change consistently**:
1. **SKILL.md line 81**: "optimization must still happen, just without the cross-model perspective" → "fall back to technical validation only — aesthetic optimization requires Gemini's independent perspective and cannot be self-performed"
2. **SKILL.md Fallback Strategy section** (lines 127-135): Rewrite to describe technical-validation-only behavior.
3. **review-core.md step 7**: "Fall back to Claude self-optimization" → "Execute technical validation checks only"
4. **ppt.md line 339**: "review-core falls back to Claude self-review using the same quality standards" → "review-core falls back to technical validation only — aesthetic optimization skipped"

**Fallback output format**:
```markdown
# Technical Validation — Slide {N}
**Mode**: Technical validation only (Gemini unavailable — aesthetic optimization skipped)

## Automated Check Results
| Check | Status | Detail |
|-------|--------|--------|
| XML validity | PASS/FAIL | ... |
| ViewBox | PASS/FAIL | ... |
| ... | ... | ... |

## Technical Fixes Required
{structured fix JSON — only for hard constraint violations}

## Note
No aesthetic optimization suggestions are provided in this mode.
Aesthetic scoring is not performed — only pass/fail on technical checks.
```

**Fix loop behavior in fallback mode**: Only technical violations trigger fixes. No score-driven routing (because no aesthetic score exists). A slide passes if all Critical and Major technical checks pass.

**Risk**: Low. This is an honest acknowledgment of a fundamental limitation, not a capability reduction.

### AD-9: 5-type suggestion taxonomy (FR-09)

**Decision**: Extend fix JSON format with `suggestion_type` and optional `layout_suggestion` fields.

**Extended fix JSON schema**:
```json
{
  "element": "card-2 title text",
  "selector_hint": "g[transform*='translate(640'] > text:first-child",
  "attribute": "font-size",
  "current": "16",
  "target": "24",
  "severity": "major",
  "reason": "Card title below minimum size",
  "suggestion_type": "attribute_change",
  "layout_suggestion": null
}
```

**Suggestion types and their semantics**:

| Type | Meaning | slide-core Execution | Example |
|------|---------|---------------------|---------|
| `attribute_change` | Single property tweak | Deterministic patch: change attribute to target value | font-size 16→24 |
| `layout_restructure` | Structural layout change | Regenerate SVG with layout constraint in prompt | "Change 3-column to hero+grid" |
| `full_rethink` | Fundamental redesign needed | Regenerate from scratch (no fixes_json) | "Entire layout is wrong for this content type" |
| `content_reduction` | Too much info density | Regenerate with simplified content from outline | "Remove 3 of 7 data points, keep top 4" |
| `deck_coordination` | Cross-slide harmony | Deferred to holistic pass, not per-slide fix | "This slide's accent usage conflicts with slide 5" |

**Backward compat** (NFR-01): Old fix JSON without `suggestion_type` is treated as `attribute_change` (safe default — preserves current deterministic patch behavior).

**Risk**: Medium. The taxonomy is theoretical until validated by calibration run. UD-3 acknowledges this — may need adjustment post-calibration.

### AD-10: chart_colors token (FR-10)

**Decision**: Add `chart_colors` array (8 hex values) to each style YAML, placed after `color_scheme`. Update svg-generator.md chart patterns to use `chart_colors[n]`.

**Palette design principles**:
- First 2 colors: primary data colors (high contrast against card_bg)
- Colors 3-4: secondary data colors
- Colors 5-8: tertiary, for 5+ series (progressively lower saturation)
- All colors must pass WCAG AA (4.5:1) against the style's `card_bg`

**Risk**: None. Additive YAML key, no existing consumers break.

### AD-11: slide-status.json atomic write (FR-11)

**Decision**: Write to `slide-status.json.tmp`, validate JSON, rename to `slide-status.json`.

**Implementation** (ppt.md Phase 6 instructions):
```
When updating slide-status.json:
1. Read current slide-status.json (if exists)
2. Update the in-memory object with new slide entry
3. Write to slide-status.json.tmp
4. Validate: `python3 -c "import json; json.load(open('slide-status.json.tmp'))"` or `node -e "JSON.parse(require('fs').readFileSync('slide-status.json.tmp','utf8'))"`
5. Rename: `mv slide-status.json.tmp slide-status.json`
```

**Why tmp+rename**: On POSIX systems, `mv` within the same filesystem is atomic (single `rename()` syscall). A crash during step 3 leaves `.tmp` incomplete but the original `slide-status.json` intact. A crash during step 5 either completes or doesn't — no partial state.

**Risk**: None. Standard pattern. The only subtlety: orchestrator must not read slide-status.json while a write is in progress, but since the orchestrator is single-threaded and slide-status writes happen in response to completed slide signals, there's no race.

### AD-12: Style token guided-freedom enforcement (FR-12)

**Decision**: Single enforcement model across all styles (brand-override and default):

- **Mandatory zone** (programmatically enforced): `primary`, `secondary`, `accent`, `background`, `text`, `card_bg` — must match style YAML exactly.
- **Free zone** (declared but unchecked): decorative elements (gradients, glows, grid overlays) — any color allowed, but must be declared in a `// decorative` comment or `data-decorative="true"` attribute for auditability.
- **Chart zone**: must use `chart_colors` from style YAML.

**Review rubric change**: reviewer.md's "Style tokens" quality standard row changes from "Minor for semantic extensions, Major for random colors" to "Critical for mandatory-zone violations, Info for undeclared decorative colors".

**Risk**: Low. The production run already showed agents using unlisted decorative colors to good effect. This codifies observed behavior rather than fighting it.

### AD-13: Suggestion-driven fix strategy (FR-13)

**Decision**: Replace score-driven fix routing with suggestion-type-driven routing.

**Current flow** (score-driven):
```
review score → threshold → action (patch / regenerate / accept)
```

**New flow** (suggestion-driven):
```
Gemini suggestions → group by type → route each type:
  attribute_change    → pass as fixes_json to slide-core (deterministic patch)
  layout_restructure  → regenerate with layout constraint in prompt
  full_rethink        → regenerate from scratch (no fixes_json)
  content_reduction   → regenerate with simplified outline content
  deck_coordination   → queue for holistic pass (not per-slide action)
```

**Score's new role**: Auxiliary pass/fail gate only. Score >= 7 + no critical issues = pass regardless of suggestions. Score < 7 = process suggestions. Score is NOT used for fix budget allocation.

**Fix budget**: Max 2 rounds per slide (unchanged). A "round" processes all non-deck_coordination suggestions from one review. If round 1 fixes produce new suggestions in round 2 review, process those. After round 2, accept with warning.

**Fallback mode** (no Gemini): Only technical fixes from AD-8. Route: all are `attribute_change` type (hard constraint violations are always attribute-level). No layout_restructure or full_rethink — those require aesthetic judgment.

**Risk**: Medium. Depends on calibration gate validating the taxonomy (UD-3). Mitigated by: keeping score as auxiliary gate means the worst case is equivalent to current behavior.

### AD-14: Holistic deck review design (FR-14)

**Decision**: Add `visual_weight: "low" | "medium" | "high"` to outline.json page schema for proactive visual planning. Expand holistic review protocol in reviewer.md.

**visual_weight semantics**:
- `low`: breathing slides — quote, image, single_focus. Light color, minimal elements.
- `medium`: standard content, comparison. Moderate color and density.
- `high`: key data slides, climax moment. Rich color, maximum visual impact.

**Holistic review protocol additions** (reviewer.md):
1. **Visual Weight Curve**: Plot weight across slides. Flag 3+ consecutive high-weight slides (fatigue) or 3+ consecutive low-weight (boredom).
2. **Color Story Escalation**: Accent color should intensify toward the deck's climax slide(s). Flag uniform accent usage.
3. **Layout Variety**: No more than 2 consecutive slides with the same layout_type. Flag monotony.
4. **deck_coordination suggestions**: Holistic review produces `suggestion_type: "deck_coordination"` for cross-slide issues. These are advisory (not auto-fixed) — flagged for lead orchestrator to decide.

**Risk**: Low (design only in Wave 3, implementation in Wave 4).

### AD-15: Agent infra model override — UD-1 Resolution

**Decision**: Recommend **two agent prompt variants** over Task() model override.

**Analysis**:

| Approach | Pros | Cons |
|----------|------|------|
| Task() model override | Single agent definition; runtime flexibility | Requires platform feature that may not exist; if it does exist, needs investigation of Task() API; model in frontmatter becomes misleading |
| **Two agent variants** | No platform dependency; explicit and auditable; each variant is self-documenting | Two files to maintain; naming convention needed |

**Rationale**:
1. Agent frontmatter `model:` field is the source of truth for model selection. Overriding it at Task() call time creates a hidden parameter that contradicts the visible definition.
2. The use case is narrow: only `attribute_change` fixes use sonnet. This is a well-defined, stable boundary — not a dynamic runtime decision.
3. Two files: `agents/slide-core.md` (opus, for design + structural fixes) and `agents/slide-core-patch.md` (sonnet, for attribute patches). The patch variant is a thin wrapper that inherits most of slide-core's prompt but restricts scope to attribute-level changes.

**Naming**: `slide-core-patch` — clear that it's a scoped variant of slide-core.

**Risk**: Low, but this is Wave 4 (FR-17). No action needed until suggestion-driven fix strategy is validated.

**Alternative if Task() model override IS supported**: Use single agent with `Task(subagent_type="ppt-agent:slide-core", model="sonnet", ...)`. This is cleaner IF the platform supports it. Recommend investigating Task() API before Wave 4 implementation. If supported, AD-15 changes to single-agent with override.

---

## File Change Map

### Wave 1 — Unlock Foundation

| File | Changes | FRs | Risk |
|------|---------|-----|------|
| `agents/review-core.md` | Add `Bash` to tools (line 7); `maxTurns: 15` → `20` (line 13) | FR-01, FR-05 | None |
| `agents/content-core.md` | `maxTurns: 25` → `35` (line 13); rewrite line 81 for batched signaling | FR-02, FR-03 | None |
| `agents/slide-core.md` | `maxTurns: 30` → `20` (line 14) | FR-04 | None |
| `commands/ppt.md` | Update Phase 5 signal description (line 152); update Phase 6 pipeline trigger for batched signals; add `approved` field check to resume detection (after line 79) | FR-03, FR-06 | Low |
| `skills/_shared/references/prompts/outline-architect.md` | Add `"approved": false` to JSON schema | FR-06 | None |

**Order**: All Wave 1 changes are independent — can be applied in any order within a single commit.

### Wave 2 — Rebuild Aesthetic Optimization Layer

| File | Changes | FRs | Risk |
|------|---------|-----|------|
| `agents/review-core.md` | Rewrite steps 6-8 for optimizer framing; rewrite step 7 fallback to "technical validation only"; update structured fix JSON for suggestion_type | FR-07, FR-08, FR-09 | Medium |
| `skills/gemini-cli/references/roles/reviewer.md` | Restructure output format (suggestions above scores); add suggestion_type + layout_suggestion to fix JSON; rewrite Adaptive Fix Budget section | FR-07, FR-09 | Medium |
| `skills/gemini-cli/SKILL.md` | Line 81 contradiction fix; `## Review Criteria` → `## Optimization Criteria` (line 108); rewrite Fallback Strategy section (lines 127-135); update Constraints table | FR-07, FR-08 | Low |
| `commands/ppt.md` | Update fallback rules (line 339) to "technical validation only" | FR-08 | Low |
| `skills/_shared/references/styles/business.yaml` | Add `chart_colors` array | FR-10 | None |
| `skills/_shared/references/styles/tech.yaml` | Add `chart_colors` array | FR-10 | None |
| `skills/_shared/references/styles/creative.yaml` | Add `chart_colors` array | FR-10 | None |
| `skills/_shared/references/styles/minimal.yaml` | Add `chart_colors` array | FR-10 | None |
| `skills/_shared/references/prompts/svg-generator.md` | Update chart patterns to use `chart_colors[n]` | FR-10 | Low |

**Order**:
1. SKILL.md fixes first (canonical policy document)
2. reviewer.md format changes (output schema)
3. review-core.md prompt changes (consumes reviewer.md format)
4. ppt.md fallback rules (references SKILL.md policy)
5. Style YAMLs + svg-generator.md (independent, can be parallel with 1-4)

**ATOMIC**: reviewer.md + review-core.md + slide-core.md fix JSON format changes must be in the same commit.

### [Calibration Gate] — Mandatory after Wave 2

**Purpose**: Validate with 8-10 slide production run.
**Check**:
1. Does Gemini produce typed optimization suggestions?
2. Does the 5-type taxonomy cover actual Gemini output? (UD-3)
3. Are technical validation thresholds reasonable in fallback mode?
4. Does signal batching work correctly in the pipeline?

**Gate outcome**: Proceed to Wave 3, or adjust taxonomy/thresholds first.

### Wave 3 — Fix Strategy + State Hardening

| File | Changes | FRs | Risk |
|------|---------|-----|------|
| `commands/ppt.md` | Rewrite Phase 6 fix loop from score-driven to suggestion-driven; add atomic write for slide-status.json | FR-11, FR-13 | Medium |
| `agents/slide-core.md` | Rewrite fix handling (line 49) from "deterministic patches" to type-aware execution | FR-09 (impl), FR-13 | Medium |
| `skills/gemini-cli/references/roles/reviewer.md` | Update color compliance to guided-freedom model; expand holistic section with visual_weight protocol | FR-12, FR-14 | Low |
| `agents/slide-core.md` | Update color usage rules for guided-freedom | FR-12 | Low |
| `skills/_shared/references/prompts/outline-architect.md` | Add `visual_weight` to page schema | FR-14 | None |
| All 4 style YAMLs | Add `decorative_colors` declaration section if needed for FR-12 | FR-12 | None |

**Order**:
1. FR-11 (atomic writes) — independent, no coupling
2. FR-12 (guided-freedom) — touches reviewer.md + slide-core + style YAMLs
3. FR-13 (suggestion-driven fix) — touches ppt.md + slide-core. Depends on calibration data.
4. FR-14 (holistic design) — touches outline-architect.md + reviewer.md

### Wave 4 — Visual Richness + Pipeline Optimization

| File | Changes | FRs | Risk |
|------|---------|-----|------|
| `skills/_shared/references/prompts/svg-generator.md` | Add 5 new SVG patterns | FR-15 | Low |
| `commands/ppt.md` | Holistic review implementation; adaptive window; section extraction; dedup; score trajectory; Hard Stop UX | FR-16, FR-20, FR-21, FR-22, FR-24, FR-26 | Medium |
| `agents/review-core.md` | Holistic review implementation; heartbeat reduction; memory: none | FR-16, FR-18, FR-19 | Low |
| `agents/slide-core.md` | Sonnet patch variant or model override; heartbeat reduction; memory: none | FR-17, FR-18, FR-19 | Low |
| `agents/content-core.md` | Heartbeat reduction | FR-18 | None |
| `agents/research-core.md` | Heartbeat reduction | FR-18 | None |
| `skills/_shared/assets/preview-template.html` | Speaker notes panel, comparison view | FR-25 | Low |
| New: validation scripts | outline.json, slide-status.json, review-manifest.json validators | FR-27 | Low |
| New (conditional): `agents/slide-core-patch.md` | Sonnet variant for attribute patches | FR-17 | Low |

---

## Risk Assessment

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| Suggestion taxonomy doesn't match Gemini output | High | Medium | Calibration gate after Wave 2. Taxonomy is adjustable. |
| Prompt changes degrade Gemini response quality | Medium | Low | A/B comparison with current prompts during calibration. Preserve raw outputs for comparison. |
| Signal batching breaks Phase 5→6 pipeline | Medium | Low | Test with 6-slide and 15-slide decks. Batching logic is simple (counter mod 3). |
| Atomic write adds latency | Low | Low | JSON validation + rename is <10ms. Negligible vs LLM call time. |
| Two slide-core variants drift apart | Low | Medium | Share common content via reference. Consider Task() model override if platform supports it. |
| Old run directories without `approved` field re-enter Phase 4 | Low | High (by design) | This IS the safe behavior. Users re-approve in seconds. |

---

## Implementation Sequence (Dependency-Respecting)

```
Week 1: Wave 1 (all independent, single commit)
  ├─ FR-01: review-core + Bash
  ├─ FR-02: content-core maxTurns 35
  ├─ FR-03: signal batching (content-core + ppt.md)
  ├─ FR-04: slide-core maxTurns 20
  ├─ FR-05: review-core maxTurns 20
  └─ FR-06: approved field (outline-architect + ppt.md)

Week 2: Wave 2 (ordered within wave)
  ├─ FR-10: chart_colors (independent, can start day 1)
  ├─ FR-07+FR-09: Gemini optimizer role + suggestion taxonomy (ATOMIC)
  │   ├─ SKILL.md fixes
  │   ├─ reviewer.md format restructure
  │   ├─ review-core.md prompt rewrite
  │   └─ slide-core.md fix handling docs
  └─ FR-08: technical validation fallback (SKILL.md + review-core + ppt.md)

[Calibration Gate]: Production run (8-10 slides)

Week 3-4: Wave 3 (after calibration)
  ├─ FR-11: atomic writes (independent)
  ├─ FR-12: guided-freedom enforcement
  ├─ FR-13: suggestion-driven fix strategy
  └─ FR-14: holistic review design

Week 5+: Wave 4 (schedule after P0/P1 complete)
  ├─ FR-15 through FR-27 (see file change map)
```

---

## Unresolved Decision Recommendations

### UD-1: Agent infra model override → Two agent variants (AD-15)

Create `agents/slide-core-patch.md` (sonnet) for `attribute_change` fixes. Investigate Task() model override API before Wave 4 — if supported, use single agent with runtime override instead.

### UD-2: Technical validation form → Inlined in review-core (AD-7)

Validation checks stay in review-core prompt, executed via Bash. No separate script, no orchestrator pre-step. Extends existing dead-code checks with 3 new items.

### UD-3: Suggestion taxonomy → Validate via calibration gate

The 5-type taxonomy is a design hypothesis. Ship it in Wave 2, test with production run, adjust before Wave 3's FR-13 implementation. Expected outcomes:
- `attribute_change` and `layout_restructure` will cover 80%+ of Gemini suggestions
- `full_rethink` may be rare (Gemini tends toward incremental improvement)
- `content_reduction` may merge with `layout_restructure` if Gemini frames density issues as layout problems
- `deck_coordination` will only appear in holistic mode — verify during calibration
