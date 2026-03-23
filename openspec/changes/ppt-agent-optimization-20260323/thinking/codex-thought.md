# Codex Thought — Architecture Constraint Synthesis

> Synthesized from 4 boundary explorations on 2026-03-23.
> Sources: explore-workflow.json, explore-agents.json, explore-svg.json, explore-platform.json

---

## Priority Legend

| Level | Meaning | Action Timeline |
|-------|---------|-----------------|
| **P0** | Structural bug or non-functional design contract | Must fix before next production run |
| **P1** | High-impact design gap or calibration error | Fix in current optimization cycle |
| **P2** | Optimization opportunity or quality improvement | Schedule after P0/P1 resolved |

---

## P0 — Structural Bugs

### P0-1: review-core missing Bash tool (BLOCKING BUG)

**Description:** review-core's frontmatter lists tools `[Read, Write, Skill, SendMessage]` but its documented workflow requires 5 Bash-dependent pre-review checks: xmllint, viewBox grep, font-size grep, color token compliance, safe area boundary check. Without Bash, these checks are dead code.

**Evidence:** `agents/review-core.md` lines 4-8 (frontmatter) vs lines 34-42 (pre-review checks). Confirmed by direct file read — Bash is absent from tools list.

**Impact:** Every slide goes to expensive Gemini/Claude review without pre-filtering trivially broken SVGs. Wasted API cost on malformed input. The pre-review validation layer is entirely non-functional.

**Resolution:** Add `Bash` to review-core's tools list in frontmatter. Single-line change.

**Dependency:** None. Immediate fix.

---

### P0-2: Self-review quality gate is non-functional (rubber stamp)

**Description:** When Gemini is unavailable, the Claude self-review fallback produces templated, non-discriminating reviews. All 12 slides in the Xiaomi production run scored 8.2-8.8 with identical Notes text across every review. The review format spec (5 criteria, structured fix JSON) is completely ignored.

**Evidence:** `explore-svg.json` §4_quality_gate_calibration — production reviews use simplified 3-field format omitting Readability and Color Harmony. Holistic review is also templated. Score clustering (0.6-point range across 12 slides of varied complexity) confirms no genuine per-slide evaluation.

**Impact:** The quality gate provides zero signal. Fix loops never trigger (all slides pass first review). The entire Phase 6 review→fix→review cycle is vestigial when Gemini is unavailable. Users get false confidence in output quality.

**Resolution (multi-part):**
1. Strengthen self-review prompt: require unique per-slide observations, enforce full 5-criterion format, mandate at least one specific fix suggestion per slide scoring < 9.0.
2. Add a programmatic validator that rejects reviews with identical Notes text across slides.
3. Require score variance: if all N slides score within 0.5 points, flag the review batch as suspicious and re-run with explicit instruction to discriminate.

**Dependency:** P0-1 (Bash in review-core) should land first so pre-review checks can filter trivial issues before the self-review even runs.

---

### P0-3: content-core maxTurns insufficient for large decks

**Description:** content-core has `maxTurns: 25`. In draft mode, generating N slide SVGs requires: ~5 reads + N writes + N signals + 1 manifest = 2N+6 turns. For a 15-slide deck: 36 turns, exceeding the 25-turn budget.

**Evidence:** `explore-agents.json` §max-turns-allocation — detailed turn accounting shows 15-slide decks overflow by 11 turns. Even 12-slide decks (2×12+6=30) overflow by 5.

**Impact:** content-core silently truncates draft generation for decks above ~9-10 slides. Remaining drafts are never written. Phase 6 design agents receive incomplete input.

**Resolution:** Increase content-core `maxTurns` to 40. Alternative: batch `draft_slide_ready` signals every 3 slides (saves N/3 turns) to stay within 25, but this is fragile. Increasing maxTurns is the safer fix.

**Dependency:** None. Immediate fix.

---

### P0-4: Resume skips outline approval if outline.json exists

**Description:** The `--run-id` resume logic checks artifact presence sequentially. If outline.json exists but draft-manifest.json does not, resume jumps to Phase 5 (draft generation). But outline.json may represent an unapproved outline — the user could have been in the Phase 4 revision loop when the process crashed.

**Evidence:** `explore-workflow.json` §resume-detection finding-4. The Hard Stop contract at Phase 4 says "Do NOT proceed until user approves." Resume bypasses this.

**Impact:** User gets slides built from an unapproved outline structure, violating the explicit Hard Stop guarantee.

**Resolution:** Add an `approved: true` field to outline.json. Content-core sets this field only after the user explicitly approves. Resume logic checks `outline.json.approved === true` before skipping to Phase 5. If not approved, resume at Phase 4 outline review.

**Dependency:** Requires outline.json schema update. Backward-compatible (treat missing field as `approved: false`).

---

## P1 — High-Impact Design Gaps

### P1-1: Deterministic patching cannot fix structural issues

**Description:** The fix loop mechanism treats all fixes as deterministic attribute patches (element/selector_hint/attribute/current/target). But the two highest-weighted review criteria — Layout Balance (25%) and Readability (25%) — often require structural changes: moving cards, reflowing text, rebalancing grid proportions. These are generative, not patch-able.

**Evidence:** `explore-workflow.json` §phase-6-fix-loop finding-3. slide-core.md:49 explicitly says "Fixes are deterministic patches, not generative reinterpretation." The fix JSON format biases toward attribute-level changes.

**Impact:** Slides failing on Layout or Readability exhaust their fix budget (2 rounds) without meaningful improvement. Fix loops are effective only for Typography, Information Density, and Color Harmony issues.

**Resolution:** Introduce a two-tier fix model:
- **Attribute fixes** (current behavior): font-size, color, opacity, gap adjustments. Quick, deterministic. Use sonnet.
- **Structural fixes** (new): when reviewer flags Layout or Readability issues with severity=critical, trigger a regeneration from draft reference with specific layout constraints (e.g., "reduce card count from 6 to 4", "switch from three_column to two_column_asymmetric"). Use opus.

The reviewer must classify each fix suggestion as `fix_type: "attribute"` or `fix_type: "structural"`. Structural fixes consume 1 fix round but produce a new design, not a patched one.

**Dependency:** Requires reviewer.md fix format extension. Requires slide-core to handle structural fix mode.

---

### P1-2: slide-status.json partial write corrupts resume state

**Description:** slide-status.json is updated after each slide completes. If the process crashes mid-JSON-write, the file becomes truncated/invalid JSON. On resume, parse failure causes the entire Phase 6 to restart from scratch, redoing all completed slides.

**Evidence:** `explore-workflow.json` §resume-detection finding-1. No atomic write or backup strategy is documented.

**Impact:** A single crash during a long Phase 6 run can waste all completed slide design+review work (potentially hours of compute).

**Resolution:** Atomic write pattern:
1. Write to `slide-status.tmp.json`
2. Validate JSON parse of the tmp file
3. Rename `slide-status.tmp.json` → `slide-status.json` (atomic on POSIX)

Additionally, maintain `slide-status.bak.json` as the previous valid state. On resume, if `slide-status.json` fails to parse, fall back to `.bak.json`.

**Dependency:** None. Orchestrator-level change in commands/ppt.md.

---

### P1-3: Late holistic review cannot fix systemic issues

**Description:** The holistic review runs after ALL individual slides complete. If it discovers cross-slide consistency problems (monotonous layouts, accent color overuse, inconsistent shadows), fixing requires re-running slide-core for multiple slides. The holistic review is advisory only — it does not block delivery.

**Evidence:** `explore-workflow.json` §holistic-review-timing finding-1. commands/ppt.md:206 — "If holistic score < 7, flag issues but do not block delivery."

**Impact:** Systemic visual consistency issues are reported to the user but never fixed. The holistic review creates awareness without actionability.

**Resolution:** Add a **partial holistic checkpoint** after every 3-4 completed slides. This lightweight check evaluates:
- Layout variety (are layouts varying enough across completed slides?)
- Accent color usage pattern (escalating or flat?)
- Shadow/border-radius/gap consistency

If the checkpoint flags an issue, the orchestrator adjusts the style context or layout hints for remaining slides. This catches systemic issues early enough to course-correct, while the full holistic review after completion catches narrative arc issues that require the complete deck.

**Dependency:** Requires orchestrator logic change. The partial checkpoint could reuse review-core in a new `mode=checkpoint` with a subset of holistic criteria.

---

### P1-4: Style tokens bypassed in practice

**Description:** The Xiaomi production run uses a custom color palette (#07111E, #132842, #42E8FF, #FF7A1A, #6D7BFF) that doesn't match tech.yaml token values (#0f172a, #1e293b, #22d3ee). The agent invented a richer design system at runtime, effectively bypassing the style token constraints.

**Evidence:** `explore-svg.json` §8_production_quality_analysis finding-1. The custom palette is aesthetically superior but undermines the token system's purpose.

**Impact:** Style tokens function as suggestions rather than constraints. Brand consistency is not guaranteed. The review criterion "color token compliance" cannot pass if the agent routinely invents custom colors.

**Resolution:** Design decision required — two valid paths:

**Option A: Enforce tokens strictly.** Add a programmatic pre-review check that validates all fill/stroke colors in the SVG against the style YAML palette (with tolerance for opacity variants). Non-compliant SVGs fail pre-review. Requires enriching style tokens (see P2-1 chart_colors).

**Option B: Embrace flexibility with guardrails.** Allow agents to extend the palette but require: (1) all extended colors must be declared in a `<defs>` block with semantic names, (2) the primary/accent/background tokens must be used as the dominant colors, (3) extended colors serve supporting/decorative roles only.

**Recommendation:** Option A for brand-override scenarios (--brand-colors), Option B for default styles. The reviewer should check which mode applies.

**Dependency:** Affects reviewer.md color compliance check and slide-core generation constraints.

---

### P1-5: Missing chart_colors token blocks multi-series data visualization

**Description:** All chart SVG patterns use `${accent}` as the single data color. Multi-series charts (grouped bars, multi-line, multi-segment donuts) need an ordered color palette of 6-8 colors.

**Evidence:** `explore-svg.json` §2_style_token_completeness — chart_colors identified as highest-severity missing token. §3_data_visualization_gaps — grouped bar chart and line chart (both high-frequency) are blocked by single-color limitation.

**Impact:** Data-heavy presentations cannot properly differentiate between series in charts. Agents must improvise palettes, creating inconsistency.

**Resolution:** Add `chart_colors` token to style YAML schema — an ordered array of 6-8 hex colors designed for data visualization (high contrast, colorblind-friendly). Update all 4 style YAMLs. Update svg-generator.md chart patterns to reference `${chart_colors[n]}`.

**Dependency:** Requires style YAML schema extension. All existing styles need update.

---

## P2 — Optimization Opportunities

### P2-1: slide-core fix rounds should use sonnet instead of opus

**Description:** When slide-core applies structured fix patches (fixes_json), the task is mechanical: parse fix array, locate element, change attribute. This doesn't require opus-level reasoning.

**Evidence:** `explore-agents.json` §model-selection — slide-core verdict "APPROPRIATE but OVER-SPECIFIED for fix rounds." Estimated savings: 5-8 opus calls → sonnet per run.

**Impact:** ~20-32 equivalent sonnet calls saved per run. Significant cost reduction for decks with many fix rounds.

**Resolution:** Split slide-core invocation: use opus for initial generation (no fixes_json), use sonnet for fix application (with fixes_json). Requires either (a) two agent variants, or (b) model override support in Task() args.

**Note:** This becomes more impactful if P1-1 (structural vs attribute fix model) is implemented — attribute fixes are the ideal candidate for sonnet downgrade.

---

### P2-2: slide-core maxTurns over-allocated (30 → 20)

**Description:** slide-core designs ONE slide per invocation. Typical workflow: 12-15 turns. maxTurns=30 wastes ~15 turns of resource budget.

**Evidence:** `explore-agents.json` §max-turns-allocation — detailed turn accounting confirms 20 is sufficient even for worst-case (2 validation failures + rewrites).

**Resolution:** Reduce slide-core `maxTurns` from 30 to 20.

---

### P2-3: review-core maxTurns too tight for holistic mode (15 → 20)

**Description:** In holistic mode, review-core reads ALL slide SVGs (potentially 15 files) plus runs pre-review checks. 15 turns is barely sufficient for individual review and insufficient for holistic.

**Evidence:** `explore-agents.json` §max-turns-allocation — holistic mode could consume 10+ turns for reads alone.

**Resolution:** Increase review-core `maxTurns` from 15 to 20. Alternative: batch pre-review checks into a single bash script (1 turn instead of 5).

---

### P2-4: Heartbeat signaling overhead

**Description:** Each agent sends 2 heartbeats (start + pre-final-write). For a 12-slide deck, ~62-66 heartbeat signals total, consuming 2 turns per agent invocation.

**Evidence:** `explore-agents.json` §communication-overhead.

**Resolution:** Reduce to start-only heartbeat. The ready/complete signal already serves as the "I'm finishing" indicator. Saves ~31-33 turns across a full run.

---

### P2-5: Adaptive sliding window for Phase 5→6 pipeline

**Description:** Fixed window of min(3, remaining) doesn't account for fix loop overhead. A slide in fix loop blocks 33% of window capacity.

**Evidence:** `explore-workflow.json` §phase-5-6-pipeline findings 2-4.

**Resolution:** Adaptive policy: start at 3, expand by 1 if last 2 slides passed without fixes, shrink by 1 if last slide entered fix loop. Cap at 5.

---

### P2-6: Memory scope optimization for per-slide agents

**Description:** slide-core and review-core load full project memory on spawn despite being highly focused per-invocation agents. They receive all context through prompt args and file reads.

**Evidence:** `explore-agents.json` §memory-setting.

**Resolution:** Set `memory: none` for slide-core and review-core. Keep `memory: project` for research-core and content-core.

---

### P2-7: Missing SVG patterns for referenced chart types

**Description:** svg-generator.md's chart selection table references Icon Array, Metric Card Grid, and Comparison Table, but no SVG implementation patterns are provided.

**Evidence:** `explore-svg.json` §3_data_visualization_gaps.

**Resolution:** Add SVG template patterns for: Comparison Table (high priority — explicitly mentioned in generation rules), Grouped Bar Chart, Metric Card Grid.

---

### P2-8: No artifact schema validation

**Description:** Style YAML, outline.json, index.json registry, and SVG output have no formal schema validation. Malformed artifacts cascade failures silently.

**Evidence:** `explore-svg.json` §7_style_yaml_schema_validation + `explore-platform.json` §testing.

**Resolution:** Create validation scripts for: (1) style YAML required fields + color format, (2) index.json registry integrity (referenced files exist, no duplicate ids), (3) outline.json schema compliance, (4) SVG structural rules (viewBox, font-size floor, safe area). These serve as both tests and runtime pre-generation guards.

---

### P2-9: requirements.md has no schema for section extraction

**Description:** Phase 2→3 transition requires extracting section topics from free-form requirements.md. No structured format or required headings are defined.

**Evidence:** `explore-workflow.json` §phase-2-3-transition finding-1.

**Resolution:** Define a standard `## Key Sections` heading in requirements.md with a bullet list of section topics. The lead writes this during Phase 2; Phase 3 reads it deterministically.

---

### P2-10: No cross-section deduplication in material merge

**Description:** Phase 3 material merge is simple concatenation. Overlapping content from parallel research-core agents wastes tokens in Phase 4.

**Evidence:** `explore-workflow.json` §phase-3-parallelism finding-2.

**Resolution:** During merge, the orchestrator deduplicates data points and annotates which sections each material supports. Low effort, medium impact on content-core's token efficiency.

---

## Architecture Decision Records

### ADR-1: Keep 4-agent architecture (no decomposition)

**Decision:** Retain the current research-core / content-core / slide-core / review-core split.

**Alternatives considered:**
- Split content-core into outline-core + draft-core → Rejected: sequential dependency means no parallelism gain; additional spawn overhead.
- Merge review-core into slide-core → Rejected: fundamentally undermines the dual-model review principle (cross-model perspective is the whole point).
- Specialize research-core into search + synthesis → Rejected: over-decomposition for current scale.
- Add validation-core for pre-review checks → Rejected: over-engineering for 5 bash commands; fix review-core's Bash access instead.

**Confidence:** High. Evidence from `explore-agents.json` §agent-scope-boundaries shows no decomposition provides net positive value.

---

### ADR-2: Star topology for agent communication

**Decision:** Agents communicate only with the orchestrator via SendMessage. No agent-to-agent messages.

**Rationale:** The workflow is sequential per-slide (design → review → fix → review). The orchestrator has full context. Agent-to-agent communication would add complexity without enabling new capabilities.

**Confidence:** High. No change needed.

---

### ADR-3: File-based state machine for resume

**Decision:** Continue using artifact presence in RUN_DIR as the durable state layer.

**Enhancement:** Add `approved` field to outline.json (P0-4). Add atomic writes for slide-status.json (P1-2). These harden the existing design without changing the architecture.

**Tradeoff:** No lock file or concurrency guard exists. Acceptable for single-user mode. Would need addressing for CI/headless (P2 scope).

---

### ADR-4: Two-tier fix model (attribute vs structural)

**Decision:** Extend the fix loop to distinguish attribute patches from structural regeneration (P1-1).

**Rationale:** The current "all fixes are patches" model cannot address Layout/Readability failures, which together carry 50% of the review weight. Without this, the fix loop is effective for only 50% of possible failures.

**Tradeoff:** Structural fixes are more expensive (full opus regeneration) and less predictable. But the alternative — exhausting fix budget with ineffective patches — is worse.

---

## Dependency Graph

```
P0-1 (review-core Bash)
  └─► P0-2 (self-review quality gate) — pre-review checks must work before fixing self-review prompt
        └─► P1-1 (structural vs attribute fixes) — quality gate must produce real scores before fix model matters
              └─► P2-1 (sonnet for fix rounds) — fix model must be defined before optimizing model selection

P0-3 (content-core maxTurns) — independent, immediate fix

P0-4 (resume outline approval)
  └─► P1-2 (slide-status atomic writes) — both harden the resume system
        └─► ADR-3 (file-based state) — resume improvements feed into architecture decision

P1-3 (partial holistic checkpoint)
  └─► P2-5 (adaptive sliding window) — both optimize Phase 6 pipeline

P1-4 (style token enforcement) + P1-5 (chart_colors token)
  └─► P2-7 (missing SVG patterns) — patterns need the enriched token set
        └─► P2-8 (artifact schema validation) — validators need the finalized schemas

P2-2 (slide-core maxTurns) — independent
P2-3 (review-core maxTurns) — independent
P2-4 (heartbeat reduction) — independent
P2-6 (memory scope) — independent
P2-9 (requirements schema) — independent
P2-10 (material dedup) — independent
```

---

## Implementation Sequence

**Phase A — Immediate fixes (unblock correct behavior):**
1. P0-1: Add Bash to review-core tools
2. P0-3: Increase content-core maxTurns to 40
3. P0-4: Add `approved` field to outline.json + resume logic check
4. P2-2 + P2-3: Adjust slide-core (30→20) and review-core (15→20) maxTurns

**Phase B — Quality gate rehabilitation:**
5. P0-2: Strengthen self-review prompt + add validation layer
6. P1-2: Atomic writes for slide-status.json

**Phase C — Design model evolution:**
7. P1-1: Two-tier fix model (attribute vs structural)
8. P1-4: Style token enforcement decision
9. P1-5: Add chart_colors token to style schema

**Phase D — Pipeline optimization:**
10. P1-3: Partial holistic checkpoint
11. P2-1: Sonnet for attribute fix rounds
12. P2-4: Heartbeat reduction
13. P2-5: Adaptive sliding window

**Phase E — Quality infrastructure:**
14. P2-7: Missing SVG patterns
15. P2-8: Artifact schema validators
16. P2-9: Requirements schema
17. P2-10: Material deduplication
