# Gemini Thought: Frontend/UX Constraint Synthesis

> Consolidated from 4 boundary explorations: workflow, agents, SVG quality, platform.
> Date: 2026-03-23

---

## P0 — Must Fix (Blocks quality or correctness)

### C-01: Self-review quality gate is non-functional (rubber stamp)

**Description**: Claude self-review (Gemini fallback path) produces identical Notes text across all 12 slides, scores cluster in 8.2–8.8 with 0.6-point range, review format spec (5 criteria + structured fix JSON) is completely ignored. Holistic review is equally templated. The quality gate provides zero signal — all slides pass on first try regardless of actual quality.

**Evidence**:
- `explore-svg.json` §4_quality_gate_calibration: "All 12 slides score between 8.2-8.8", "identical Notes text ('层级关系清晰，首屏结论明确' repeated on every review)"
- `explore-svg.json` §9: "self_review_is_rubber_stamp" — "The quality gate provides no signal."
- `explore-workflow.json` §phase-6-fix-loop: fix loop has never been exercised in production — no slide has ever entered fix rounds.

**User Impact**: Users receive slides with inflated confidence scores. Genuinely poor slides (layout overflow, unreadable text, color clashes) pass unchallenged. The entire Phase 6 review pipeline (review-core agent, Gemini skill, fix loop budget) is effectively dead code when Gemini is unavailable.

**Resolution Options**:

| Option | Effort | Quality Gain | Recommendation |
|--------|--------|-------------|----------------|
| A. Stricter self-review prompt: require unique per-slide observations, reject templated responses, mandate element-level references (e.g., "card #3 at y=420 has font-size 14px, below 16px minimum") | Medium | High | **Recommended first step** |
| B. Programmatic pre-review validation: run measurable checks (color hex ∈ style palette, font-size ≥ 16px, gap ≥ 20px, viewBox=1280×720) as hard gates before LLM review. Fail = reject without LLM cost. | Low | Medium | **Recommended complement to A** |
| C. Score calibration samples: include 3 reference SVGs with known scores (a 5.0, a 7.0, a 9.0) in the review prompt. Reviewer must calibrate against these before scoring. | Medium | Medium | Good for Gemini path |
| D. Gemini-only quality gate: prohibit Claude self-review for quality scoring. When Gemini unavailable, skip scoring entirely and apply only programmatic checks. | Low | Variable | Simplest but loses the subjective review |

**Decision Record**: Options A+B together. A addresses the LLM review quality; B adds a hard validation layer that works regardless of LLM quality. Option D is too aggressive — self-review has value if properly prompted, and users without Gemini would lose all quality feedback.

---

### C-02: review-core missing Bash tool — pre-review checks are dead code

**Description**: review-core.md documents 5 pre-review automated checks (xmllint, viewBox grep, font-size grep, color compliance, safe area boundary) that all require Bash execution. But review-core's tool list does not include Bash. These checks cannot execute.

**Evidence**:
- `explore-agents.json` §tool-availability-gaps: "review-core.md lines 34-42 document Bash-dependent checks. review-core.md frontmatter (lines 4-8) does NOT include Bash in tools list."
- Severity: **critical** — pre-review checks are the first defense against trivially broken SVGs. Without them, expensive Gemini/Claude API calls run on malformed input.

**User Impact**: Wasted API cost. Broken SVGs (invalid XML, missing viewBox) consume full review cycles that should be caught in milliseconds.

**Resolution**: Add `Bash` to review-core's tools list. Single-line fix in agent frontmatter.

---

### C-03: Resume skips outline approval Hard Stop

**Description**: If outline.json exists but draft-manifest.json does not, resume jumps to Phase 5 (drafting). But outline.json may have been written before user approval (Phase 4 revision loop). A crash during the approval loop produces an unapproved outline that resume treats as approved.

**Evidence**:
- `explore-workflow.json` §resume-detection finding-4: "Resume skips outline approval gate if outline.json exists"
- Phase 4 is a MANDATORY Hard Stop per commands/ppt.md. The resume logic violates this contract.

**User Impact**: User may unknowingly receive slides built from an outline they never approved. This breaks the core UX promise of user control at decision points.

**Resolution Options**:
- A. Add an `outline-approved.marker` file written only after explicit user approval. Resume checks for marker, not just outline.json.
- B. Add an `approved: true` field to outline.json, set only after user confirms.

**Decision Record**: Option B — simpler, keeps state in one file, easy to check.

---

### C-04: content-core maxTurns insufficient for large decks

**Description**: content-core has maxTurns=25. In draft mode for a 15-slide deck: 5 reads + 15 SVG writes + 15 per-slide signals + 1 manifest = 36 turns needed. Exceeds budget by 44%.

**Evidence**:
- `explore-agents.json` §max-turns-allocation: "content-core maxTurns=25 is insufficient for draft mode with 15-slide decks."
- Risk: draft generation truncated — missing slides from position ~10 onward.

**User Impact**: Silently incomplete decks. Last slides never get drafted, Phase 6 runs on partial input.

**Resolution**: Increase content-core maxTurns to 35. Additionally, consider batching draft_slide_ready signals every 3 slides to reduce turn overhead (saves ~10 turns for a 15-slide deck).

---

## P1 — Should Fix (Quality or efficiency impact)

### C-05: Style tokens bypassed in production — enforcement vs. creativity tradeoff

**Description**: The Xiaomi SU7 production run uses a custom color palette (#42E8FF, #FF7A1A, #6D7BFF) that does not match tech.yaml (#22d3ee accent). The agent invented a richer, better design system. But this means the style token system is decorative, not authoritative.

**Evidence**:
- `explore-svg.json` §8: "Custom color palette beyond style tokens" — "The agent created a custom design system."
- `explore-svg.json` §2: decorative_accent_color token gap — "The agent invented a richer palette during generation, which is good design but breaks the 'all colors from style tokens' review rule."

**User Impact**: Two problems. (1) Brand consistency: if a user selects "tech" style expecting specific colors, they get whatever the agent invents. (2) Review integrity: color compliance checks fail silently because the baseline (style YAML) doesn't match reality.

**Resolution — Design Decision Record**:

The fundamental question: **Should the system enforce tokens strictly or allow creative override with post-hoc validation?**

| Approach | Pros | Cons |
|----------|------|------|
| **Strict enforcement** (all colors from YAML) | Predictable, brand-safe, testable compliance | Limits visual quality; the production run proves the agent's choices were better |
| **Guided freedom** (YAML = base palette, agent may add harmonious accents) | Higher quality, preserves creativity | Harder to validate; user loses fine control |
| **Hybrid** (core colors enforced, decoration colors free) | Balances control and creativity | Complex rules; boundary between "core" and "decoration" is fuzzy |

**Recommended**: Guided freedom with guardrails:
1. Style YAML defines **mandatory** colors (primary, accent, background, text, card_bg) — these MUST appear as specified.
2. Style YAML gets a new **chart_colors** palette (ordered, 6-8 colors) for data viz.
3. Agent may introduce additional decorative colors (glows, gradients, secondary accents) but must declare them in a `custom_palette` block at the top of the SVG `<defs>`.
4. Post-hoc validation: check mandatory colors match YAML; decorative colors are logged but not blocked.
5. Review rubric: color compliance checks mandatory colors only.

---

### C-06: Missing chart_colors token blocks multi-series data visualization

**Description**: All chart SVG patterns use `${accent}` as the single data color. Multi-series data (grouped bars, multi-line charts, multi-segment donuts) is impossible without an ordered color palette.

**Evidence**:
- `explore-svg.json` §2: "chart_colors: Ordered palette of 6-8 colors for data visualization"
- `explore-svg.json` §3: "All current chart SVG patterns use ${accent} as the single data color."

**User Impact**: Data-heavy slides (dashboards, comparisons, trend analyses) limited to single-color charts. Grouped/stacked bars, multi-line charts, and multi-segment donuts are blocked.

**Resolution**: Add `chart_colors` as an ordered array (6-8 hex values) to all 4 style YAMLs. Derive from primary/secondary/accent with controlled hue rotation. Update svg-generator.md chart patterns to use `chart_colors[i]` instead of `${accent}`.

---

### C-07: Deterministic patching cannot fix structural issues

**Description**: Fix mechanism (fixes_json with element/attribute/current/target) is designed for attribute-level patches. But Layout Balance (25% weight) and Readability (25% weight) issues often require structural changes — moving cards, reflowing text, changing grid proportions. The fix format biases toward mechanical tweaks, not generative reinterpretation.

**Evidence**:
- `explore-workflow.json` §phase-6-fix-loop finding-3: "A font-size change is a patch; a layout reflow is generative."
- Combined impact: the two highest-weighted criteria (50% of total) are the least fixable via patches.

**User Impact**: Slides stuck in the 5.0–6.9 band exhaust their fix budget (2 rounds) on attribute tweaks that don't move the score. Wasted computation; slides ship at mediocre quality.

**Resolution Options**:
- A. Expand fix format: add a `structural_fix` type that gives the designer freedom to recompose the layout while preserving content.
- B. Score-dependent strategy: score < 6.0 → regenerate (not patch); score 6.0–6.9 → patch; score ≥ 7.0 → pass. This implicitly acknowledges that low-scoring slides need generative rewrite.
- C. Allow slide-core to ignore fixes_json and regenerate when the fix targets are structural (layout_balance or readability).

**Decision Record**: Option B — simplest behavioral change. Adjust the fix budget: score 5.0–5.9 → regenerate from scratch (1 attempt); score 6.0–6.9 → patch (2 rounds); score ≥ 7.0 → pass. The regeneration gives the agent a clean slate for structural issues.

---

### C-08: Late holistic review cannot fix systemic cross-slide issues

**Description**: Holistic review runs after ALL individual slides complete. It finds systemic issues (monotonous layouts, accent overuse, inconsistent shadows) but cannot cost-effectively fix them — all design agents have finished.

**Evidence**:
- `explore-workflow.json` §holistic-review-timing finding-1: "fixing requires re-running slide-core for multiple slides."
- `explore-workflow.json` §holistic-review-timing finding-5: "Color story escalation planned at wrong phase."

**User Impact**: Cross-slide consistency problems flagged as warnings but never fixed. User receives slides with advisory notes instead of actual improvements.

**Resolution**: Add a **mid-flight consistency check** after every 3–4 completed slides. Lightweight check: are layouts varying enough? Is accent usage escalating monotonically? Are shadows/border-radius consistent? Feedback to remaining slides' design context. Full holistic review remains for narrative arc (which genuinely requires complete deck).

Additionally, move color story planning to outline phase: add `visual_weight: low|medium|high` hint to each page in outline.json so slide-core can manage accent escalation proactively.

---

### C-09: Missing SVG patterns referenced in spec but not implemented

**Description**: svg-generator.md's chart selection table references Icon Array, Metric Card Grid, and Comparison Table — but provides no SVG implementation patterns. Agents must improvise without guidance.

**Evidence**:
- `explore-svg.json` §3: "Referenced in svg-generator.md chart type selection table but missing SVG pattern"
- Missing: Comparison Table, Grouped Bar Chart, Line Chart with axes, Icon Array, Metric Card Grid, Network/Relationship Diagram (used in slide-08)

**User Impact**: Inconsistent quality for data-heavy slides. Each invocation reinvents these patterns.

**Resolution (prioritized)**:
1. Comparison Table — explicitly referenced, high frequency
2. Metric Card Grid — explicitly referenced, KPI dashboards
3. Grouped/Stacked Bar Chart — extremely common, needs chart_colors
4. Network/Relationship Diagram — already produced ad-hoc in production
5. Line Chart with axes — common for trends

---

### C-10: Partial write to slide-status.json corrupts resume state

**Description**: slide-status.json is updated after each slide completes. Process crash mid-JSON-write produces truncated/invalid JSON. Resume fails to parse → all completed slides lost, entire Phase 6 restarts.

**Evidence**:
- `explore-workflow.json` §resume-detection finding-1: "No atomic write or backup strategy is defined."

**User Impact**: A crash near the end of a long run (e.g., slide 11 of 12) wastes all prior compute.

**Resolution**: Atomic write pattern — write to `slide-status.json.tmp`, then rename to `slide-status.json`. On resume, if `slide-status.json` is invalid, check for `.tmp` fallback.

---

## P2 — Nice to Have (Polish, extensibility, observability)

### C-11: HTML preview improvements

**Description**: Current preview template has 3 modes (Gallery/Scroll/Present) with keyboard navigation. Works well. Potential additions:

1. **Slide notes overlay** (N key): Show `notes` field from outline.json as speaker notes overlay in Present mode.
2. **Timer mode**: Elapsed/remaining time display for rehearsal.
3. **PDF export button**: Client-side SVG→PDF via jsPDF or browser print-to-PDF.
4. **Thumbnail numbers**: Show slide numbers in Gallery mode for quick reference.

**Evidence**: `explore-platform.json` §output_format: "PDF export is the lowest-effort win."

**User Impact**: Enhanced presentation rehearsal experience. PDF export eliminates a manual conversion step.

**Priority**: Slide notes overlay (low effort, high value) > PDF export button (medium effort, high value) > Thumbnail numbers (trivial) > Timer (low value).

---

### C-12: Cognitive design principles not operationalized in quality gate

**Description**: cognitive-design-principles.md is a well-written reference but acts as background reading, not operational guidance. Key integration gaps:

1. **Miller's Law inconsistency**: cognitive-design-principles.md uses 4±1 (Cowan 2001); outline-architect.md uses 7±2 (Miller 1956). Different references in the same system.
2. **Spatial Contiguity** (highest effect size, 1.10): no review criterion checks label-to-data proximity.
3. **3-Second Test**: not referenced in review rubric despite being the most practical design principle.

**Evidence**: `explore-svg.json` §6_cognitive_design_integration — detailed per-principle analysis.

**Resolution**:
1. Align to 4±1 (Cowan) consistently — update outline-architect.md.
2. Add spatial contiguity check to review rubric: "labels within card boundary of their data element."
3. Add 3-second test proxy: "largest text element on slide communicates the slide's key message from outline.json."

---

### C-13: Hard Stop UX quality at Phase 2 and Phase 4

**Description**: Phase 2 asks 5 clarification questions (audience, purpose, key messages, tone, constraints). Phase 4 shows outline-preview.md in "digital sticky notes" format. Quality of these interactions determines entire downstream output.

**Observations**:
- Phase 2 question list is well-designed but presented all at once. Users may provide shallow answers to all 5 rather than deep answers to the most important ones.
- Phase 4 outline-preview.md format (markdown tables with page structure) is functional but not visual. Users must imagine the spatial layout from text descriptions.

**Potential Improvements**:
- Phase 2: Prioritize questions. Ask audience + purpose first; derive tone from purpose if user doesn't specify. Reduce cognitive load on user.
- Phase 4: Generate a simple ASCII art or markdown grid showing approximate slide layouts alongside the outline. Makes the abstract concrete.

**User Impact**: Better input → better output. The Hard Stops are the highest-leverage user touchpoints.

---

### C-14: No score trajectory tracking across fix rounds

**Description**: slide-status.json records final score and fix_rounds count but not per-round scores. Cannot detect fix-loop thrashing (score oscillating around threshold) or measure fix effectiveness.

**Evidence**: `explore-workflow.json` §phase-6-fix-loop finding-4: "Without trajectory data, it is impossible to know if fixes are improving scores."

**Resolution**: Add `score_history: [6.2, 6.8, 7.1]` array to slide-status.json per-slide entry.

---

### C-15: No style YAML schema validation

**Description**: No formal schema for style YAML files. Malformed YAML (missing color, invalid hex, missing v1.1 tokens) causes silent failures at generation time. Risk increases with user-authored brand styles (--brand-colors flag).

**Evidence**: `explore-svg.json` §7: "No validation exists." `explore-platform.json` §style_extensibility: "No schema validation for style YAML files."

**Resolution**: Create a simple validation checklist (required keys, hex format regex, numeric range checks) as a pre-generation step in Phase 1 Init.

---

## Design Decision Records

### DDR-1: Spec enforcement model — Hard constraints vs. soft guidelines

**Context**: Production output systematically deviates from specifications (custom colors, custom decorative elements, simplified review format) but produces high-quality results. The specs function as inspirational guidelines, not constraints.

**Decision**: Adopt a **two-tier enforcement model**:
- **Hard constraints** (programmatically enforced): viewBox 1280×720, font-size ≥ 16px, safe area margins, mandatory style colors, valid XML.
- **Soft guidelines** (LLM-evaluated): layout variety, information density, cognitive load, color harmony, decorative choices.

Hard constraints fail the slide before LLM review. Soft guidelines are scored by the review system with proper calibration (see C-01).

**Rationale**: The production evidence shows that allowing agent creativity within structural bounds produces the best output. Over-constraining kills the visual quality that makes the system valuable.

---

### DDR-2: Fix loop strategy — patch vs. regenerate

**Context**: Deterministic patches (attribute changes) cannot fix structural layout issues. But regeneration is expensive (full opus invocation).

**Decision**: Score-dependent strategy:
- Score ≥ 7.0: pass
- Score 6.0–6.9: patch (structured fixes_json, max 2 rounds)
- Score 5.0–5.9: regenerate from scratch (1 attempt, no fixes_json)
- Score < 5.0: regenerate (1 attempt)
- Score < 3.0: regenerate with simplified content (reduce data_elements count by 30%)

**Rationale**: Patches work well for minor issues (wrong font size, missing padding). Structural issues (layout doesn't balance, information overflow) need a clean generative restart. The score threshold tells us which regime we're in.

---

### DDR-3: Pipeline mode — per-slide streaming vs. batch

**Context**: Phase 5→6 pipeline overlap provides marginal real-world benefit (~3-4 turns saved) while consuming significant content-core turn budget (N signals for N slides) and adding orchestrator complexity.

**Decision**: Keep pipeline mode as default but add batch mode fallback. If content-core's turn budget is tight (large decks, >12 slides), switch to batch: complete all drafts first, then launch Phase 6 as a clean batch. Per-slide signaling becomes optional (signal every 3 slides, matching window size).

**Rationale**: Pipeline is architecturally elegant but the cost/benefit is marginal. Batch mode is simpler and more robust for large decks.

---

## Visual Quality Improvement Roadmap

### Phase 1: Quality Gate Reform (addresses C-01, C-02)
- Add Bash to review-core tool list (C-02) — immediate fix
- Implement programmatic pre-review validation layer (C-01 option B)
- Strengthen self-review prompt with calibration samples and unique-observation requirement (C-01 option A)
- Add score trajectory tracking to slide-status.json (C-14)

### Phase 2: Token & Pattern Enrichment (addresses C-05, C-06, C-09)
- Add chart_colors token to all 4 style YAMLs (C-06)
- Add semantic_colors (success/warning/danger/info) to token schema
- Implement missing SVG patterns: Comparison Table, Metric Card Grid, Grouped Bar (C-09)
- Formalize centered_feature_spotlight and image_overlay_text layouts
- Adopt guided-freedom color model (C-05, DDR-1)

### Phase 3: Structural Improvements (addresses C-07, C-08, C-10)
- Implement score-dependent fix strategy (DDR-2)
- Add mid-flight consistency check after every 3-4 completed slides (C-08)
- Add visual_weight hint to outline.json pages for accent escalation planning
- Implement atomic write for slide-status.json (C-10)
- Add outline approval marker for safe resume (C-03)

### Phase 4: UX Polish (addresses C-11, C-12, C-13)
- Add slide notes overlay to HTML preview (C-11)
- Add PDF export button to preview (C-11)
- Operationalize cognitive design principles in review rubric (C-12)
- Improve Phase 2/4 Hard Stop interaction quality (C-13)
- Align Miller's Law reference (4±1 Cowan) across all specs (C-12)

### Phase 5: Platform & Extensibility (from explore-platform.json)
- Add style YAML schema validation (C-15)
- Increase content-core maxTurns to 35 (C-04)
- Optimize slide-core maxTurns to 20, review-core to 20
- Add headless mode flags (--headless, --profile, --outline)
- Document style authoring workflow

---

## Summary Statistics

| Priority | Count | Effort Profile |
|----------|-------|---------------|
| P0 (Must Fix) | 4 | 1 trivial, 2 low, 1 medium |
| P1 (Should Fix) | 6 | 2 low, 3 medium, 1 high |
| P2 (Nice to Have) | 5 | 2 trivial, 2 low, 1 medium |
| **Total** | **15** | |

**Critical path**: C-01 (self-review rubber stamp) → C-05 (style enforcement model) → C-07 (fix loop strategy). These three form a dependency chain: fixing reviews enables meaningful scoring → meaningful scoring reveals which slides need fixes → fix strategy determines how to improve them.
