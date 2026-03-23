# Decision Log — PPT Agent Optimization

> All architecture decisions from codex-plan and gemini-plan, numbered sequentially.
> Includes UD-1/2/3 resolutions and conflict check results.
> Date: 2026-03-23

---

## Conflict Check

Both codex-plan (AD-7) and gemini-plan (G-10) resolved UD-2 identically: **option (b) — validation checks inlined in review-core prompt, executed via Bash**. Both plans agree on rationale (simplest, no new files, review-core already has the check list).

Both plans align on UD-1 resolution: two agent variants as primary approach, Task() model override as fallback if platform supports it.

**No conflicts detected between the two architecture plans.**

---

## Decisions

### D-01: Add Bash to review-core tools

- **Source**: Codex AD-1
- **FR**: FR-01
- **Options considered**:
  1. Add Bash to tools array
  2. Move pre-review checks to orchestrator
- **Chosen**: Option 1 — add Bash to review-core
- **Rationale**: The 5 checks already exist in review-core's prompt (lines 33-42). They just need the tool to execute. Zero-risk, single-line change.

### D-02: content-core maxTurns 25->35

- **Source**: Codex AD-2
- **FR**: FR-02
- **Options considered**:
  1. Increase to 30
  2. Increase to 35
  3. Increase to 40
- **Chosen**: Option 2 — 35 turns
- **Rationale**: 15-slide worst case needs 26 turns with signal batching. 35 provides 26% margin (9 turns headroom). 30 is too tight; 40 is wasteful.

### D-03: Signal batching every 3 slides

- **Source**: Codex AD-2
- **FR**: FR-03
- **Options considered**:
  1. Keep per-slide signaling, increase maxTurns to 40+
  2. Batch every 3 slides
  3. Batch every 5 slides
- **Chosen**: Option 2 — batch every 3
- **Rationale**: Per-slide signaling with 15 slides needs ~36 turns (busts 35). Batching by 3 reduces signals from 15 to 5 (ceil(15/3)). Batch-5 would delay pipeline startup too much.

### D-04: slide-core maxTurns 30->20

- **Source**: Codex AD-3
- **FR**: FR-04
- **Options considered**:
  1. Keep 30
  2. Reduce to 25
  3. Reduce to 20
- **Chosen**: Option 3 — 20 turns
- **Rationale**: Single slide design needs ~15 turns. 20 provides 33% margin. 30 was over-allocated by 15 turns.

### D-05: review-core maxTurns 15->20

- **Source**: Codex AD-4
- **FR**: FR-05
- **Options considered**:
  1. Keep 15
  2. Increase to 20
  3. Increase to 25
- **Chosen**: Option 2 — 20 turns
- **Rationale**: Holistic mode on 12-slide deck: 15 turns = zero headroom. 20 provides margin for style YAML reads. 25 is unnecessary (uses sonnet, but still wastes context).

### D-06: outline.json approved field + resume guard

- **Source**: Codex AD-5
- **FR**: FR-06
- **Options considered**:
  1. Add `approved` boolean field
  2. Add timestamp-based approval marker
  3. Separate approval file
- **Chosen**: Option 1 — boolean field in outline.json
- **Rationale**: Simplest. Backward compatible (missing = false). content-core never sets it; orchestrator sets after user confirms. Separate file adds unnecessary complexity.

### D-07: Gemini optimizer role rewrite — output format

- **Source**: Gemini G-01
- **FR**: FR-07
- **Options considered**:
  1. Keep scores first, suggestions after
  2. Move suggestions above scores
  3. Remove scores entirely
- **Chosen**: Option 2 — suggestions as primary output, scores as secondary gate
- **Rationale**: Framing shapes behavior. Leading with suggestions puts Gemini in collaborator role. Keeping scores as gate preserves pass/fail signal for the fix loop.

### D-08: Gemini optimizer role rewrite — prompt template

- **Source**: Gemini G-02
- **FR**: FR-07
- **Options considered**:
  1. Keep `## Review Criteria` heading
  2. Change to `## Optimization Criteria`
- **Chosen**: Option 2 — Optimization Criteria
- **Rationale**: Language shapes LLM behavior. "Review" implies judgment; "Optimization" implies improvement. The entire role reframe is about being a design collaborator.

### D-09: Gemini optimizer role rewrite — reviewer.md framing

- **Source**: Gemini G-03
- **FR**: FR-07
- **Options considered**:
  1. Minimal wording changes
  2. Three targeted framing changes (role description, methodology step 0, trailing paragraph)
- **Chosen**: Option 2 — three targeted changes
- **Rationale**: The three changes create a consistent optimizer voice throughout reviewer.md. Step 0 ("identify the single highest-impact layout change") primes Gemini to think big before getting into detail.

### D-10: 5-type suggestion taxonomy

- **Source**: Gemini G-04
- **FR**: FR-09
- **Options considered**:
  1. Keep existing attribute-only fix format
  2. Add 3 types (attribute, layout, rethink)
  3. Add 5 types (attribute, layout, rethink, content_reduction, deck_coordination)
- **Chosen**: Option 3 — 5-type taxonomy
- **Rationale**: 5 types map cleanly to distinct execution strategies. `content_reduction` captures a common Gemini observation (too much info density) that isn't a layout change. `deck_coordination` is essential for holistic review output. May collapse to 4 after calibration if content_reduction merges with layout_restructure.

### D-11: Extended suggestion JSON schema

- **Source**: Gemini G-05
- **FR**: FR-09
- **Options considered**:
  1. Add `suggestion_type` only
  2. Add `suggestion_type` + `layout_suggestion`
- **Chosen**: Option 2 — both fields
- **Rationale**: `layout_suggestion` carries the creative content for non-attribute types. Without it, slide-core has no guidance for regeneration beyond the type label.

### D-12: UD-2 Resolution — technical validation inlined in review-core

- **Source**: Codex AD-7, Gemini G-10
- **UD**: UD-2
- **Options considered**:
  (a) External bash script called by review-core
  (b) Validation checks inlined in review-core prompt, executed via Bash
  (c) Separate validation step in orchestrator before spawning review-core
- **Chosen**: Option (b) — inlined in review-core
- **Rationale**: review-core already has the 5 checks at lines 33-42 — they just need Bash. The fallback path needs these same checks as primary output, keeping it self-contained. Option (c) blurs orchestrator/agent boundary. Option (a) adds a file to maintain with no benefit.

### D-13: Self-review fallback as technical validation only

- **Source**: Codex AD-8, Gemini G-07/G-08/G-09
- **FR**: FR-08
- **Options considered**:
  1. Keep "Claude self-optimization with same quality standards"
  2. Technical validation only — no aesthetic scores or suggestions
- **Chosen**: Option 2 — technical validation only
- **Rationale**: Claude reviewing its own SVGs lacks independent aesthetic perspective. The production run proved this: 12 identical scores (8.2-8.8), Notes completely identical. Strengthening the prompt would only make Claude more detailed about "why it did a good job". Honest degradation is better than fake optimization.

### D-14: chart_colors token design

- **Source**: Gemini G-11
- **FR**: FR-10
- **Options considered**:
  1. 4 colors per style
  2. 6 colors per style
  3. 8 colors per style
- **Chosen**: Option 3 — 8 colors, ordered by visual weight
- **Rationale**: 8 covers up to 8-series charts (max practical). First color = accent for continuity. Progressive muting for lower-priority series. Accessible pairs at >= 3:1 contrast.

### D-15: Guided-freedom enforcement model

- **Source**: Gemini G-13, Codex AD-12
- **FR**: FR-12
- **Options considered**:
  1. Strict enforcement (all colors must match tokens)
  2. Split strict/flexible (core strict, decorative flexible with separate severity)
  3. Three-zone unified model (mandatory core / chart / decorative free)
- **Chosen**: Option 3 — three-zone unified model
- **Rationale**: Production run showed agents using unlisted decorative colors to good effect (gradient overlays, glows). Strict enforcement would kill creative expression. Three zones codify observed behavior: structure is locked, data viz uses chart_colors, decoration is free.

### D-16: Suggestion-driven fix strategy

- **Source**: Codex AD-13, Gemini G-18/G-19
- **FR**: FR-13
- **Options considered**:
  1. Keep score-driven routing (5.0-6.9 patch, <5 regenerate)
  2. Hybrid: score + suggestion type
  3. Pure suggestion-type-driven routing with score as auxiliary gate
- **Chosen**: Option 3 — pure suggestion-driven with score as gate
- **Rationale**: Score tells you "something is wrong" but not "what to do". Suggestion type tells you both. Score remains as pass/fail signal (>= 7 = pass) but doesn't drive fix selection. This eliminates the case where a 6.5 score triggers "patch" but the actual needed fix is a layout restructure.

### D-17: Holistic review protocol — visual_weight

- **Source**: Gemini G-15
- **FR**: FR-14
- **Options considered**:
  1. No proactive planning — holistic review only reactive
  2. Add visual_weight to outline.json for proactive planning
- **Chosen**: Option 2 — visual_weight in outline.json
- **Rationale**: visual_weight enables proactive rhythm planning at outline time, not just reactive fixes after all slides are designed. content-core can flag 3+ consecutive high-weight slides before any SVG is generated.

### D-18: Holistic review protocol — 5 dimensions

- **Source**: Gemini G-16
- **FR**: FR-14
- **Options considered**:
  1. Keep existing 5-dimension list (current reviewer.md)
  2. Expand with concrete assessment criteria and thresholds
- **Chosen**: Option 2 — expanded protocol with thresholds
- **Rationale**: The current holistic section is vague ("evaluates cross-slide consistency"). Concrete thresholds (e.g., "flag 3+ consecutive high-weight slides") make the review actionable.

### D-19: deck_coordination flow

- **Source**: Gemini G-17
- **FR**: FR-14, FR-16
- **Options considered**:
  1. deck_coordination suggestions applied by slide-core autonomously
  2. Orchestrator queues and dispatches deck_coordination fixes
- **Chosen**: Option 2 — orchestrator-managed queue
- **Rationale**: deck_coordination involves cross-slide decisions. Respects star topology (C2): orchestrator sees the full deck context, individual slide-core instances don't. Orchestrator groups by target slide and spawns fresh slide-core tasks.

### D-20: UD-1 Resolution — agent infra model override

- **Source**: Codex AD-15
- **UD**: UD-1
- **Options considered**:
  (a) Task() model override at runtime
  (b) Two agent prompt variants (slide-core + slide-core-patch)
- **Chosen**: Option (b) — two agent variants, with (a) as fallback if platform supports it
- **Rationale**: Agent frontmatter `model:` field is the source of truth. Runtime override creates a hidden parameter. The use case is narrow (only attribute_change uses sonnet). Two explicit files are self-documenting. If Task() override IS supported, it's cleaner — investigate before Wave 4.

### D-21: UD-3 Resolution — taxonomy validated via calibration gate

- **Source**: Codex AD-13, Gemini G-18
- **UD**: UD-3
- **Options considered**:
  1. Ship taxonomy as final
  2. Ship as hypothesis, validate via calibration, adjust before Wave 3
- **Chosen**: Option 2 — hypothesis + calibration
- **Rationale**: The taxonomy is derived from design analysis, not empirical data. Calibration run will show whether Gemini naturally produces suggestions matching the 5 types. Expected: attribute_change + layout_restructure cover 80%+. content_reduction may merge with layout_restructure.

### D-22: Fix loop priority cascade

- **Source**: Gemini G-19
- **FR**: FR-13
- **Options considered**:
  1. Process all suggestion types in parallel
  2. Priority cascade: full_rethink > layout_restructure > content_reduction > attribute_change
- **Chosen**: Option 2 — priority cascade
- **Rationale**: If full_rethink is suggested, patching attributes is wasted work — the whole slide is being redone. Cascade ensures the highest-impact fix is applied first, preventing redundant lower-level fixes.
