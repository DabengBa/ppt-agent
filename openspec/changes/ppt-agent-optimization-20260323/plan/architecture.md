# Unified Architecture — PPT Agent Optimization

> Merged from codex-plan.md (backend/system) and gemini-plan.md (frontend/UX)
> Date: 2026-03-23
> Conflict check: Both plans resolve UD-2 identically (option b). No conflicts found.

---

## System-Level View

The optimization restructures Phase 6 (Design Draft + Review) from a score-driven compliance loop into a suggestion-driven aesthetic optimization pipeline, while hardening the file-based state machine and correcting resource budgets.

**Preserved invariants** (NFR-01 through NFR-06):
- 4-agent architecture: research-core, content-core, slide-core, review-core
- Star topology: agents communicate only with lead orchestrator via SendMessage
- File-based state machine: artifact presence in RUN_DIR as durable truth layer
- Graceful degradation: Gemini available -> full aesthetic optimization; unavailable -> technical validation only
- Pipeline overlap: Phase 5->6 pipeline preserved, signaling simplified via batching

---

## Merged Architecture Decisions

### AD-01: review-core Bash tool (FR-01)

**Source**: Codex AD-1
**Decision**: Append `Bash` to review-core frontmatter tools array.
**Rationale**: 5 pre-review checks (xmllint, viewBox, font-size, color compliance, safe area) are dead code without Bash.
**Risk**: None.

### AD-02: content-core maxTurns 25->35 + signal batching (FR-02, FR-03)

**Source**: Codex AD-2
**Decision**: `maxTurns: 35`. Draft signals batched every 3 slides.
**Turn budget (15-slide worst case)**: 5 reads + 15 writes + 5 batched signals + 1 manifest = 26 turns (26% margin).
**Signal protocol**: `draft_slide_ready(indices=[N, N+1, N+2])`. Final batch includes `final=true`. Orchestrator launches slide-core per index, window cap `min(3, remaining)` still applies.
**Risk**: Low.

### AD-03: slide-core maxTurns 30->20 (FR-04)

**Source**: Codex AD-3
**Decision**: `maxTurns: 20`. Actual need ~15 turns (33% margin).
**Risk**: None.

### AD-04: review-core maxTurns 15->20 (FR-05)

**Source**: Codex AD-4
**Decision**: `maxTurns: 20`. Holistic mode on 12-slide deck: 12 reads + 1 write + 1 signal + 1 heartbeat = 15 (zero headroom at current limit).
**Risk**: None.

### AD-05: outline.json `approved` field + resume guard (FR-06)

**Source**: Codex AD-5
**Decision**: Add `"approved": false` to outline.json schema. Orchestrator sets `true` only after user confirms in Phase 4. Resume checks `approved === true`; missing/false triggers re-approval.
**Backward compat**: Missing field treated as `false`.
**Risk**: Low.

### AD-06: Gemini optimizer role rewrite (FR-07)

**Source**: Codex AD-6 + Gemini G-01/G-02/G-03
**Decision**: Reframe Gemini from "compliance checker" to "aesthetic optimizer". Three-file synchronized change:
1. **reviewer.md** (G-01): Output format restructured — Optimization Suggestions section above Quality Gate section. Score becomes secondary pass/fail gate.
2. **SKILL.md** (G-02): `## Review Criteria` -> `## Optimization Criteria`. Task description: "Propose concrete improvements to make the slide more compelling".
3. **reviewer.md framing** (G-03): Role description emphasizes aesthetic perspective. Optimization methodology adds step 0: "Identify the single highest-impact layout change". Trailing paragraph: "propose the bravest improvement you believe would work".
4. **review-core.md**: Steps 6-8 reframed as "request optimization suggestions" not "request quality review".

**ATOMIC with AD-07**: Must ship together — suggestion format and optimizer role are coupled.
**Risk**: Medium. Calibration gate after Wave 2 mitigates.

### AD-07: 5-type suggestion taxonomy (FR-09)

**Source**: Codex AD-9 + Gemini G-04/G-05/G-06
**Decision**: Extend fix JSON with `suggestion_type` and optional `layout_suggestion` fields.

| Type | Definition | slide-core Execution |
|------|-----------|---------------------|
| `attribute_change` | Property tweak on existing element | Deterministic patch: change attribute from current->target |
| `layout_restructure` | Structural layout change | Regenerate with layout constraint from `layout_suggestion` |
| `full_rethink` | Fundamental redesign needed | Regenerate from scratch, no fixes_json |
| `content_reduction` | Lower info density | Regenerate with simplified content |
| `deck_coordination` | Cross-slide harmony | Deferred to orchestrator holistic pass |

**Schema rules** (G-05):
- `suggestion_type`: REQUIRED. One of the 5 types.
- `selector_hint`, `attribute`, `current`, `target`: REQUIRED for `attribute_change`, omitted for others.
- `layout_suggestion`: REQUIRED for `layout_restructure`, `content_reduction`, `deck_coordination`. Free-text.
- `severity`: REQUIRED. `critical | major | minor`.
- `reason`: REQUIRED.

**Backward compat** (G-06): Missing `suggestion_type` treated as `attribute_change`.
**Risk**: Medium. Taxonomy is theoretical until calibration (UD-3).

### AD-08: Technical validation — UD-2 Resolution (FR-08)

**Source**: Codex AD-7/AD-8 + Gemini G-07/G-08/G-09/G-10
**Decision**: Option (b) — validation checks inlined in review-core prompt, executed via Bash.

**Extended technical validation checklist** (8 checks):

| # | Check | Method | Severity |
|---|-------|--------|----------|
| 1 | XML validity | `xmllint --noout` | Critical |
| 2 | viewBox presence | String match `viewBox="0 0 1280 720"` | Critical |
| 3 | Font size floor | Regex extract, check >= 12 (label), >= 14 (body) | Major |
| 4 | Card gap minimum | Parse `<g transform>` positions | Major |
| 5 | Color contrast (WCAG AA) | Compute relative luminance ratio | Major |
| 6 | Safe area margins | Check x >= 60, x <= 1220, y >= 40, y <= 680 | Major |
| 7 | Text overflow estimation | Line capacity formula from svg-generator.md | Major |
| 8 | Outline content coverage | Compare key_points against SVG text | Major |

**Execution flow** (G-10):
1. Run all Bash-based technical checks
2. If any Critical fails -> write technical validation report -> `review_failed` -> DONE (skip Gemini)
3. If all Critical pass -> proceed to Gemini call
4. If Gemini unavailable (exit 2) -> write technical validation report -> `review_passed_technical_only`

**Output format** (G-08): Distinct header "SVG Slide Technical Validation", no `overall_score`, no per-criterion aesthetic scores. All fixes are `suggestion_type: "attribute_change"`.

**Three-file consistency**:
1. SKILL.md line 81: "technical validation only" (removes contradiction)
2. SKILL.md Fallback Strategy: technical checks only, no aesthetic scores
3. review-core.md step 7: "Execute technical validation checks only"
4. ppt.md line 339: "technical validation only — aesthetic optimization skipped"

**Risk**: Low.

### AD-09: chart_colors token (FR-10)

**Source**: Codex AD-10 + Gemini G-11/G-12
**Decision**: Add `chart_colors` array (8 hex values) to each style YAML. Update svg-generator.md chart patterns to use `chart_colors[n]`.

**Palette design** (G-11):
- First color = style's accent (continuity with single-series)
- Colors 2-4: harmonious, distinct at a glance
- Colors 5-8: progressively muted
- Each consecutive pair >= 3:1 contrast on card_bg

**Chart pattern integration** (G-12):
- Big Number / Progress Bar: stays `${accent}` (single value)
- Sparkline, Donut, Bar, Line: `chart_colors[n]` per series
- Backward compat: missing `chart_colors` falls back to `[${accent}]` repeated

**Risk**: None.

### AD-10: slide-status.json atomic write (FR-11)

**Source**: Codex AD-11
**Decision**: Write to `.tmp`, validate JSON, then `mv` (atomic rename).
**Risk**: None.

### AD-11: Guided-freedom enforcement model (FR-12)

**Source**: Codex AD-12 + Gemini G-13
**Decision**: Single unified enforcement model with three zones:

| Zone | Colors | Enforcement |
|------|--------|-------------|
| **Mandatory Core** | primary, secondary, accent, background, text, card_bg | Programmatic — Major for deviations |
| **Chart Colors** | chart_colors[0..7] | Programmatic — reviewer checks chart elements |
| **Decorative Free** | Any color | Must be on elements tagged `data-decorative="true"` or within `<defs>`. Warning if untagged |

**Risk**: Low.

### AD-12: Suggestion-driven fix strategy (FR-13)

**Source**: Codex AD-13 + Gemini G-18/G-19
**Decision**: Replace score-driven fix routing with suggestion-type-driven routing.

**Fix loop** (G-19 simplified):
1. Receive review from review-core
2. Pass AND no critical/major suggestions -> mark complete
3. Has suggestions:
   a. Separate `attribute_change` -> batch as one patch pass
   b. If `layout_restructure` or `content_reduction` -> pick highest-severity, regenerate with constraint
   c. If `full_rethink` -> regenerate from scratch (ignore attribute_change)
   d. If `deck_coordination` -> queue for holistic pass
4. After fix, re-review (max 2 total rounds per slide)
5. After round 2, accept with warning

**Priority cascade**: `full_rethink` > `layout_restructure` > `content_reduction` > `attribute_change`

**Score's new role**: Auxiliary pass/fail gate only. Score >= 7 + no critical issues = pass. Score NOT used for fix budget allocation.

**Fallback mode** (no Gemini): Only technical fixes — all `attribute_change` type.

**Risk**: Medium. Depends on calibration gate.

### AD-13: Holistic deck review design (FR-14)

**Source**: Codex AD-14 + Gemini G-15/G-16/G-17
**Decision**: Add `visual_weight: "low"|"medium"|"high"` to outline.json page schema. Expand holistic review protocol.

**visual_weight semantics** (G-15):
- `low`: breathing slides (quote, image, single_focus)
- `medium`: standard content, comparison
- `high`: key data, climax moment

**Holistic review protocol** (G-16) — 5 dimensions:
1. **Visual Rhythm**: Flag 3+ consecutive high-weight or 2+ identical layout types
2. **Color Story Escalation**: Flag accent on every slide or missing on key slide
3. **Layout Variety**: Flag < 3 distinct layouts in 10+ slide deck or > 40% same layout
4. **Style Consistency**: Flag inconsistent border-radius, shadow depths
5. **Pacing**: Setup (~15%), Tension (~60%), Resolution (~25%) alignment

**deck_coordination flow** (G-17):
1. Orchestrator receives holistic review with `deck_coordination` suggestions
2. Groups by target slide index
3. Spawns slide-core with `context: "deck_coordination_pass"` flag
4. After regeneration, runs holistic review once more (max 1 re-run)

**Risk**: Low (design only in Wave 3, implementation in Wave 4).

### AD-14: Agent infra model override — UD-1 Resolution (FR-17)

**Source**: Codex AD-15
**Decision**: Two agent prompt variants — `slide-core.md` (opus) and `slide-core-patch.md` (sonnet).
**Alternative**: If Task() model override IS supported, use single agent with runtime override. Investigate before Wave 4 implementation.
**Risk**: Low (Wave 4, no action until suggestion strategy validated).

---

## Data Flow Diagrams

### Review Pipeline (Phase 6 — Normal Mode)

```
slide-core writes slide SVG
        |
        v
orchestrator spawns review-core
        |
        v
review-core: run 8 technical checks via Bash
        |
   [Critical fail?] --YES--> write technical report + review_failed signal
        |                     (fixes: attribute_change only)
        NO
        |
        v
review-core: call Gemini via ppt-agent:gemini-cli
        |
   [Gemini available?] --NO--> write technical validation report
        |                       (no aesthetic scores/suggestions)
        YES                     review_passed_technical_only signal
        |
        v
Gemini returns optimization suggestions (typed)
        |
        v
review-core: write review with suggestions + quality gate score
        |
        v
orchestrator: route by suggestion type (AD-12 logic)
```

### Fix Loop (Phase 6)

```
review received
    |
    v
[pass AND no critical/major suggestions?] --YES--> slide complete
    |
    NO
    |
    v
[any full_rethink?] --YES--> regenerate from scratch (opus)
    |                         re-review (round N+1)
    NO
    |
    v
[any layout_restructure/content_reduction?]
    |
    YES --> pick highest-severity, regenerate with constraint (opus)
    |       re-review (round N+1)
    NO
    |
    v
[attribute_change only] --> batch patch pass (sonnet in Wave 4)
                            re-review (round N+1)

[max 2 rounds total per slide; after round 2 accept with warning]
```

### Resume Logic

```
RUN_DIR exists?
    |
    NO --> start fresh (Phase 1)
    |
    YES
    |
    v
outline.json exists?
    |
    NO --> resume at Phase 3 or earlier (check other artifacts)
    |
    YES
    |
    v
outline.json.approved === true?
    |
    NO --> resume at Phase 4 (Hard Stop: re-present for approval)
    |
    YES
    |
    v
draft-manifest.json exists?
    |
    NO --> resume at Phase 5
    |
    YES
    |
    v
slide-status.json exists?
    |
    YES --> check per-slide status, resume incomplete slides in Phase 6
    |
    NO --> resume at Phase 6 start
```

---

## Cross-Cutting Concerns

### Backward Compatibility (NFR-01)

All changes are additive or have safe defaults when the new field is absent:
- `approved` missing in outline.json -> treated as `false` (triggers re-approval)
- `suggestion_type` missing in fix JSON -> treated as `attribute_change`
- `chart_colors` missing in style YAML -> fall back to `[${accent}]` repeated
- `visual_weight` missing in outline.json page -> default to `"medium"`

### Atomic Changes (Must-Commit-Together Groups)

| Group | Files | Reason |
|-------|-------|--------|
| **Optimizer + Taxonomy** (FR-07 + FR-09) | reviewer.md, review-core.md, SKILL.md, slide-core.md | Output format + consumer must match |
| **Signal Batching** (FR-02 + FR-03) | content-core.md, ppt.md | Producer + consumer of batch signal |
| **Approved Field** (FR-06) | outline-architect.md, ppt.md | Schema + resume logic |
| **chart_colors** (FR-10) | 4x style YAML, svg-generator.md | Token + consumer |
| **Fallback Rewrite** (FR-08) | SKILL.md, review-core.md, ppt.md | Policy + implementation + reference |

### File Change Synchronization Matrix

| Change | Files that must change together |
|--------|-------------------------------|
| FR-01 (Bash tool) | `review-core.md` only |
| FR-02+03 (maxTurns + batch) | `content-core.md` + `ppt.md` |
| FR-06 (approved field) | `ppt.md` + `outline-architect.md` |
| FR-07+09 (optimizer + taxonomy) | `review-core.md` + `reviewer.md` + `SKILL.md` + `slide-core.md` |
| FR-08 (self-review fallback) | `review-core.md` + `SKILL.md` + `ppt.md` |
| FR-10 (chart_colors) | 4x style YAML + `svg-generator.md` |
| FR-12 (guided-freedom) | `reviewer.md` + `slide-core.md` + (style YAMLs if needed) |
| FR-13 (fix strategy) | `ppt.md` + `slide-core.md` + `reviewer.md` |
| FR-14 (holistic design) | `outline-architect.md` + `reviewer.md` |
