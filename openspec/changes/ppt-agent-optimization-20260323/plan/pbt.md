# Property-Based Test Specifications — PPT Agent Optimization

> Testable properties per wave for verifying implementation correctness.
> Date: 2026-03-23

---

## Wave 1 Properties

### P-W1-01: review-core has Bash tool

**Property**: `agents/review-core.md` frontmatter `tools` array contains `Bash`.
**Verification**: Parse YAML frontmatter, assert `Bash` in tools list.
**Files**: `agents/review-core.md`

### P-W1-02: maxTurns values correct

**Property**: Agent frontmatter `maxTurns` values match specification.
**Verification**:
- `agents/content-core.md` -> `maxTurns: 35`
- `agents/slide-core.md` -> `maxTurns: 20`
- `agents/review-core.md` -> `maxTurns: 20`
**Files**: All 3 agent files above.

### P-W1-03: Signal batching in content-core

**Property**: content-core draft signaling instruction mentions "every 3" or "batch" and does NOT say "after writing EACH slide".
**Verification**: Grep content-core.md for `draft_slide_ready` context. Assert batch language present, per-slide language absent.
**Files**: `agents/content-core.md`

### P-W1-04: Signal batching in ppt.md

**Property**: ppt.md Phase 5-6 pipeline description handles batched `draft_slide_ready` with `indices` (array), not single `index`.
**Verification**: Grep ppt.md Phase 5 section for `indices` or batch handling.
**Files**: `commands/ppt.md`

### P-W1-05: outline.json has approved field

**Property**: outline-architect.md schema definition includes `"approved"` field with default `false`.
**Verification**: Parse the JSON schema in outline-architect.md, assert `approved` key present with value `false`.
**Files**: `skills/_shared/references/prompts/outline-architect.md`

### P-W1-06: Resume logic checks approved field

**Property**: ppt.md resume detection explicitly checks `approved === true` before allowing skip to Phase 5.
**Verification**: Grep ppt.md resume section for `approved` check. Assert the check exists and treats missing/false as "resume at Phase 4".
**Files**: `commands/ppt.md`

---

## Wave 2 Properties

### P-W2-01: Gemini output format leads with suggestions

**Property**: reviewer.md Output Format section has "Optimization Suggestions" section appearing BEFORE "Quality Gate" or score section.
**Verification**: In reviewer.md, find "Optimization Suggestions" and "Quality Gate" (or "overall_score") headings. Assert suggestion heading has lower line number.
**Files**: `skills/gemini-cli/references/roles/reviewer.md`

### P-W2-02: Suggestion JSON contains suggestion_type

**Property**: reviewer.md fix JSON schema definition includes `suggestion_type` as REQUIRED field with 5 valid values.
**Verification**: Grep reviewer.md for `suggestion_type`. Assert field is documented as required. Assert all 5 types are listed.
**Files**: `skills/gemini-cli/references/roles/reviewer.md`

### P-W2-03: SKILL.md uses Optimization Criteria heading

**Property**: SKILL.md prompt template uses `## Optimization Criteria` heading, NOT `## Review Criteria`.
**Verification**: Grep SKILL.md for both headings. Assert `Optimization Criteria` present, `Review Criteria` absent.
**Files**: `skills/gemini-cli/SKILL.md`

### P-W2-04: SKILL.md line 81 contradiction resolved

**Property**: SKILL.md does NOT contain "optimization must still happen" or equivalent language suggesting Claude can self-perform aesthetic optimization.
**Verification**: Grep SKILL.md for "optimization must still happen". Assert zero matches. Grep for "technical validation only" in fallback context. Assert present.
**Files**: `skills/gemini-cli/SKILL.md`

### P-W2-05: Self-review output has no overall_score

**Property**: review-core.md fallback path output format does NOT include `overall_score` field.
**Verification**: In review-core.md, find the fallback/technical-validation output section. Assert no `overall_score` in that section.
**Files**: `agents/review-core.md`

### P-W2-06: SKILL.md has no internal contradictions

**Property**: SKILL.md Fallback Strategy section is consistent with line 81 area and Constraints table regarding self-review capability.
**Verification**: Extract all references to fallback/self-review behavior in SKILL.md. Assert all say "technical validation only" with no contradiction.
**Files**: `skills/gemini-cli/SKILL.md`

### P-W2-07: chart_colors present in all 4 style YAMLs

**Property**: Each style YAML contains `chart_colors` array with 6-8 hex values.
**Verification**: For each of business.yaml, tech.yaml, creative.yaml, minimal.yaml: parse YAML, assert `chart_colors` key exists, assert array length >= 6 and <= 8, assert each value matches hex color regex `#[0-9a-fA-F]{6}`.
**Files**: All 4 style YAMLs.

### P-W2-08: svg-generator.md uses chart_colors

**Property**: svg-generator.md chart patterns reference `chart_colors[n]` instead of only `${accent}` for multi-series elements.
**Verification**: Grep svg-generator.md Data Visualization section for `chart_colors`. Assert present. Verify Donut, Bar patterns use `chart_colors[n]`.
**Files**: `skills/_shared/references/prompts/svg-generator.md`

### P-W2-09: Backward compat for missing suggestion_type

**Property**: Documentation states that missing `suggestion_type` defaults to `attribute_change`.
**Verification**: Grep reviewer.md or review-core.md for default/backward-compat language about missing `suggestion_type`.
**Files**: `skills/gemini-cli/references/roles/reviewer.md` or `agents/review-core.md`

---

## Wave 3 Properties

### P-W3-01: Fix loop routes by suggestion type, not score

**Property**: ppt.md Phase 6 fix loop decision logic references `suggestion_type` for routing, NOT score thresholds (5.0-6.9, <5.0, etc.) as primary routing.
**Verification**: In ppt.md Phase 6 fix section, grep for `suggestion_type` routing. Assert score thresholds (5.0-6.9, <5.0, <3.0) are NOT used for fix type selection. Score may remain as auxiliary pass/fail (>= 7.0).
**Files**: `commands/ppt.md`

### P-W3-02: Priority cascade documented

**Property**: ppt.md or slide-core.md documents the fix priority cascade: `full_rethink` > `layout_restructure` > `content_reduction` > `attribute_change`.
**Verification**: Grep for priority cascade or the specific ordering language.
**Files**: `commands/ppt.md` and/or `agents/slide-core.md`

### P-W3-03: slide-status.json uses atomic write

**Property**: ppt.md Phase 6 slide-status update instructions include tmp file + rename pattern.
**Verification**: Grep ppt.md for `.tmp` or `rename` in context of slide-status.json. Assert atomic write pattern present.
**Files**: `commands/ppt.md`

### P-W3-04: slide-status.json survives simulated crash

**Property**: If a write to `slide-status.json.tmp` is interrupted (file truncated or incomplete), the original `slide-status.json` remains valid JSON.
**Verification**: Manual test: create valid slide-status.json, write partial content to .tmp, verify original is unmodified. Then: write complete .tmp, rename, verify new content.
**Files**: `commands/ppt.md` (pattern specification)

### P-W3-05: Guided-freedom zones documented

**Property**: slide-core.md documents three color zones (mandatory core, chart, decorative free) with enforcement rules.
**Verification**: Grep slide-core.md for "mandatory" and "decorative" zone language. Assert both present.
**Files**: `agents/slide-core.md`

### P-W3-06: reviewer.md uses guided-freedom for color compliance

**Property**: reviewer.md color compliance section uses "Guided Freedom" model with Major for mandatory violations, Warning for untagged decorative.
**Verification**: Grep reviewer.md color compliance section. Assert "Guided Freedom" or 3-zone model present. Assert no "Minor for semantic extensions, Major for random colors" (old model).
**Files**: `skills/gemini-cli/references/roles/reviewer.md`

### P-W3-07: visual_weight in outline.json schema

**Property**: outline-architect.md page schema includes `visual_weight` with valid values `"low"|"medium"|"high"`.
**Verification**: Parse outline-architect.md page schema. Assert `visual_weight` field present.
**Files**: `skills/_shared/references/prompts/outline-architect.md`

### P-W3-08: Holistic review protocol has 5 dimensions

**Property**: reviewer.md holistic section documents 5 assessment dimensions: visual rhythm, color story escalation, layout variety, style consistency, pacing.
**Verification**: Grep reviewer.md holistic section for all 5 dimension names.
**Files**: `skills/gemini-cli/references/roles/reviewer.md`

---

## Wave 4 Properties

### P-W4-01: Chart patterns use chart_colors

**Property**: New SVG patterns (table, metric grid, grouped bar, line chart, network diagram) use `chart_colors[n]` for data/series colors.
**Verification**: For each new pattern in svg-generator.md, grep for `chart_colors`. Assert each multi-series pattern references it.
**Files**: `skills/_shared/references/prompts/svg-generator.md`

### P-W4-02: All 5 new patterns present

**Property**: svg-generator.md contains SVG code patterns for: table, metric card grid, grouped bar chart, line chart with axes, network/relationship diagram.
**Verification**: Grep svg-generator.md for each pattern name or heading. Assert all 5 present.
**Files**: `skills/_shared/references/prompts/svg-generator.md`

### P-W4-03: Holistic review produces deck_coordination suggestions

**Property**: review-core.md holistic mode description states that output includes `suggestion_type: "deck_coordination"` entries.
**Verification**: Grep review-core.md holistic section for `deck_coordination`.
**Files**: `agents/review-core.md`

### P-W4-04: Heartbeat is start-only

**Property**: All 4 agent .md files specify heartbeat at start only (no "before final output" heartbeat).
**Verification**: For each agent file, grep for heartbeat instruction. Assert no "before writing final output" or "before final" heartbeat language.
**Files**: All 4 agent .md files.

### P-W4-05: Memory scope none for slide-core and review-core

**Property**: `agents/slide-core.md` and `agents/review-core.md` have `memory: none` in frontmatter.
**Verification**: Parse frontmatter, assert `memory: none`.
**Files**: `agents/slide-core.md`, `agents/review-core.md`

### P-W4-06: Pattern selection guide present

**Property**: svg-generator.md contains a "Pattern Selection by Content" table mapping content signals to recommended patterns.
**Verification**: Grep svg-generator.md for "Pattern Selection" heading. Assert table with at least 5 content signal -> pattern mappings.
**Files**: `skills/_shared/references/prompts/svg-generator.md`
