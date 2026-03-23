# Gemini Plan — Frontend/UX/Visual Architecture

> Perspective: Gemini (Frontend/UX architect)
> Scope: FR-07/08/09/10/12/13/14/15/23 + style tokens + SVG patterns + holistic deck review
> Date: 2026-03-23

---

## 1. Gemini Role Reframing (Wave 2 — FR-07)

### 1.1 Architecture Decision: Optimization-First Output Format

**Decision G-01**: reviewer.md output format restructured — optimization suggestions are primary content, score is a secondary pass/fail gate.

**Rationale**: The current format (scores first → issues → fix suggestions) frames Gemini as a judge. The reframe puts Gemini in the role of a design collaborator who says "here's what I'd improve" first, then scores as a formality.

**Concrete restructuring of reviewer.md Output Format section**:

```markdown
## Optimization Suggestions (PRIMARY OUTPUT)

| # | Type | Target | Suggestion | Impact |
|---|------|--------|------------|--------|
| 1 | layout_restructure | full slide | Replace 3-equal-column → hero(60%)+grid(40%) for visual hierarchy | High |
| 2 | attribute_change | card-2 title | font-size 16→24, font-weight normal→bold | Medium |
| 3 | content_reduction | card-3 | Remove 2 of 5 bullet points — cognitive overload | Medium |

## Structured Suggestion JSON

{suggestion_json_block}

## Quality Gate (SECONDARY)

| Field | Value |
|-------|-------|
| overall_score | {1-10} |
| pass | {true/false} |

## Per-Criterion Scores
...
```

Key change: the "Fix Suggestions" section is now "Optimization Suggestions" and appears before scores, not after.

### 1.2 Prompt Template Rewrite

**Decision G-02**: SKILL.md prompt template heading changes from `## Review Criteria` to `## Optimization Criteria`. Task description changes from "Identify what works well" to "Propose concrete improvements to make the slide more visually compelling".

Concrete wording for the prompt template `## Task` section:

```
## Task
You are optimizing this SVG slide's layout and visual aesthetics.
Your primary output is concrete improvement suggestions — each one
a specific change that would make the slide more compelling.
Score the slide secondarily as a quality gate.
```

### 1.3 reviewer.md Prompt Framing Changes

**Decision G-03**: Three framing changes to reviewer.md:

1. **Line 3** (role description): Replace "Your job is not just to check compliance — it is to actively improve" with "Your job is to propose concrete visual improvements that make each slide more compelling. Compliance checking is handled by automated pre-review; your value is aesthetic perspective."

2. **Optimization Methodology section**: Add step 0 before current step 1: "0. Identify the single highest-impact layout change that would transform this slide from adequate to excellent."

3. **Line 178** (trailing paragraph): Replace "Beyond measurable quality standards, actively suggest aesthetic improvements" with: "Your primary contribution is aesthetic optimization — propose the bravest improvement you believe would work, even if it means restructuring the layout. Automated checks handle the measurable standards."

---

## 2. Five-Type Suggestion Taxonomy (Wave 2 — FR-09, atomic with FR-07)

### 2.1 Taxonomy Specification

**Decision G-04**: Five suggestion types with clear definitions, examples, and execution semantics.

| Type | Definition | When to Use | slide-core Execution | Example |
|------|-----------|-------------|---------------------|---------|
| `attribute_change` | A property tweak on an existing element — font-size, fill, opacity, spacing, position offset. The layout structure remains intact. | Single element is wrong but the overall layout works. | Deterministic patch: parse selector_hint, change attribute from current→target. No regeneration. | `font-size 16→24 on card-2 title` |
| `layout_restructure` | Structural layout change — rearranging cards, changing column count, moving elements between cards, converting layout type. Layout structure changes but content stays the same. | Layout doesn't serve the content well (e.g., 3 equal columns where a hero+grid would work better). | Regenerate with constraints: keep content, apply new layout hint from suggestion. Pass `layout_suggestion` as binding constraint to svg-generator. | `Convert 3-column equal → hero(60%)+detail-grid(40%)` |
| `full_rethink` | Complete redesign from scratch. The current approach fundamentally doesn't work for this content — wrong visual metaphor, wrong information architecture. | Score < 4 or the slide's visual concept is wrong (e.g., a timeline rendered as a bullet list). | Regenerate from scratch: re-read outline, re-select layout, generate fresh SVG. No constraint from current version. | `This data comparison slide should be a dashboard layout, not a text list` |
| `content_reduction` | Lower information density — remove, merge, or defer content elements to reduce cognitive load. The layout may stay the same but with fewer items. | Info unit count exceeds type max, or the slide tries to say too much. | Regenerate with simplified content: reduce key_points consumed from outline, or split into sub-slides (flag to orchestrator). | `Remove 3 of 7 bullet points; move detail to speaker notes` |
| `deck_coordination` | Cross-slide harmony change — only produced during holistic review (mode=holistic). Affects how this slide relates to its neighbors in the deck. | Holistic review finds monotonous layouts, accent overuse, missing breathing slides, or broken visual rhythm. | Deferred to orchestrator: orchestrator queues affected slides for re-design pass with deck-level constraint. | `Slides 4-6 all use hero_grid — convert slide 5 to single_focus for visual breathing` |

### 2.2 Extended Suggestion JSON Schema

**Decision G-05**: Each suggestion entry in the JSON array carries its type, enabling slide-core to route execution.

```json
[
  {
    "suggestion_type": "attribute_change",
    "element": "card-2 title text",
    "selector_hint": "g[transform*='translate(640'] > text:first-child",
    "attribute": "font-size",
    "current": "16",
    "target": "24",
    "severity": "major",
    "reason": "Card title below minimum for heading hierarchy"
  },
  {
    "suggestion_type": "layout_restructure",
    "element": "full slide layout",
    "layout_suggestion": "Convert 3-equal-column to hero(60% left) + detail-grid(40% right). Move the key metric to hero position for immediate visual impact.",
    "severity": "major",
    "reason": "Equal-weight columns bury the lead metric — hero layout creates visual hierarchy"
  },
  {
    "suggestion_type": "content_reduction",
    "element": "card-3 bullet list",
    "layout_suggestion": "Reduce from 7 bullet points to 3. Move detail points to speaker notes.",
    "severity": "major",
    "reason": "7 info units on a content slide exceeds the 3-5 target — cognitive overload"
  },
  {
    "suggestion_type": "deck_coordination",
    "element": "slide-05 layout",
    "layout_suggestion": "Convert from hero_grid to single_focus (quote or image). Slides 3-7 all use dense layouts — need a breathing slide.",
    "severity": "minor",
    "reason": "Visual rhythm: 3+ consecutive dense layouts fatigue the audience"
  }
]
```

**Schema rules**:
- `suggestion_type`: REQUIRED. One of the 5 types.
- `element`: REQUIRED. Human-readable target.
- `selector_hint`: OPTIONAL. Only meaningful for `attribute_change`.
- `attribute`, `current`, `target`: REQUIRED for `attribute_change`. Omitted for other types.
- `layout_suggestion`: REQUIRED for `layout_restructure`, `content_reduction`, `deck_coordination`. Free-text description of the proposed change. This is Gemini's creative contribution — it should be specific enough to guide regeneration but not a mechanical instruction.
- `severity`: REQUIRED. `critical | major | minor`.
- `reason`: REQUIRED. Why this improves the slide.

### 2.3 Backward Compatibility

**Decision G-06**: The new schema is a superset of the old schema. Old-format entries (without `suggestion_type`) are treated as `attribute_change` by default. This ensures existing review outputs remain parseable during migration.

---

## 3. Self-Review Fallback UX (Wave 2 — FR-08)

### 3.1 Technical Validation Scope

**Decision G-07**: When Gemini is unavailable, Claude performs only programmable technical checks. No aesthetic scoring, no layout suggestions, no "how to make it more compelling" — those require independent visual perspective.

Technical checks Claude CAN reliably self-perform:

| Check | Method | Severity | Notes |
|-------|--------|----------|-------|
| XML validity | `xmllint --noout` | Critical | Binary pass/fail |
| viewBox presence | String match `viewBox="0 0 1280 720"` | Critical | Binary pass/fail |
| Font size floor | Regex extract all `font-size` values, check >= 12 | Major (body < 14), Info (label < 12) | Deterministic |
| Card gap minimum | Parse `<g transform>` positions, compute distances | Major (< 20px) | Approximation — parse translate values |
| Color contrast (WCAG AA) | Extract text fill + background fill pairs, compute relative luminance ratio | Major (< 4.5:1 body, < 3:1 large) | Requires color parsing — feasible with Bash |
| Safe area | Parse element positions, check x >= 60, x <= 1220, y >= 40, y <= 680 | Major | Approximation from transform values |
| Text overflow estimation | Compare text length against card dimensions using line capacity formulas from svg-generator.md | Major | Heuristic — uses `card_width / (font_size * char_width_factor)` |
| Outline content coverage | Compare `key_points` from outline.json against text content in SVG | Major | Checks that all key_points appear in some form |
| Color token compliance | Extract all fill/stroke hex values, compare against style YAML | Warning (flag, don't block) | May flag decorative colors incorrectly — acceptable in technical-only mode |

### 3.2 Technical Validation Output Format

**Decision G-08**: Self-review output uses a distinct format header that makes it unambiguous to downstream consumers.

```markdown
# SVG Slide Technical Validation — Slide {N}: {Title}

**Validator**: Claude technical validation (Gemini unavailable)
**Mode**: technical-only — aesthetic optimization skipped
**Style**: {style_name}
**Viewport**: 1280x720

---

## Automated Check Results

| Check | Status | Details |
|-------|--------|---------|
| XML Valid | PASS/FAIL | {detail} |
| ViewBox | PASS/FAIL | {detail} |
| Font Size Floor | PASS/WARN | {detail} |
| Card Gap Minimum | PASS/WARN | {detail} |
| Color Contrast | PASS/WARN | {detail} |
| Safe Area | PASS/WARN | {detail} |
| Text Overflow | PASS/WARN | {detail} |
| Content Coverage | PASS/WARN | {detail} |
| Color Token Compliance | PASS/WARN | {detail} |

## Technical Issues

| # | Severity | Check | Description |
|---|----------|-------|-------------|
| 1 | critical | XML Valid | {detail} |

## Technical Fix JSON

{fix_json with suggestion_type always "attribute_change"}

---

> **Note**: This is a technical validation only. Aesthetic optimization
> (layout improvements, visual hierarchy, design suggestions) requires
> Gemini's independent perspective and was not performed.
> Overall aesthetic score: NOT AVAILABLE (technical validation only).
```

**Key differences from full review**:
- Header says "Technical Validation" not "Review"
- No `overall_score` field (prevents downstream from treating technical-only as aesthetic-pass)
- No per-criterion aesthetic scores (Layout Balance, Color Harmony, etc.)
- All fix suggestions are `suggestion_type: "attribute_change"` (technical fixes are always deterministic patches)
- Explicit footer note about what was NOT done

### 3.3 SKILL.md Fallback Strategy Rewrite

**Decision G-09**: SKILL.md lines 81, 127-135 rewritten.

Line 81 change:
```
- Old: "optimization must still happen, just without the cross-model perspective"
- New: "fall back to technical validation only — aesthetic optimization requires
  Gemini's independent visual perspective and cannot be self-performed by the
  generating model"
```

Fallback Strategy section rewrite:
```markdown
## Fallback Strategy

The dual-model approach (Claude generates, Gemini optimizes) provides value
through independent aesthetic perspective. When Gemini is unavailable:

1. Run deterministic technical checks via Bash: XML validity, viewBox, font-size
   floor, card gap, color contrast, safe area, text overflow, content coverage.
2. Output results in "Technical Validation" format (not "Review" format).
3. Mark as "technical validation only — aesthetic optimization skipped".
4. Do NOT produce aesthetic scores, layout suggestions, or overall_score.
5. Technical fixes use `suggestion_type: "attribute_change"` only.

The quality standards for measurable rules (14px min font, 20px min gap,
WCAG AA contrast) apply regardless of which model performs validation.
Aesthetic optimization (layout restructure, visual hierarchy, design
improvements) is Gemini-only capability.
```

### 3.4 UD-2 Resolution: Technical Validation Implementation Form

**Decision G-10**: Option (b) — validation checks inlined in review-core prompt with Bash tool.

Rationale:
- Option (a) (external bash script) creates a maintenance burden — the script must be kept in sync with the check list, and review-core must parse its output.
- Option (c) (orchestrator step) adds complexity to ppt.md and means the orchestrator must understand SVG validation.
- Option (b) is simplest: review-core already has Bash (after FR-01). The checks are listed in the prompt. review-core runs them sequentially using Bash, collects results, writes the technical validation report. No new files, no parsing layer.

The check sequence in review-core's execution flow:
1. Run all Bash-based technical checks (XML, viewBox, font-size, safe area)
2. If any Critical check fails → write technical validation report → send `review_failed` with technical fixes → DONE (skip Gemini call entirely)
3. If all Critical checks pass → proceed to Gemini call for aesthetic optimization
4. If Gemini unavailable (exit 2) → write technical validation report from check results → send `review_passed_technical_only` signal

---

## 4. Style Token System (Wave 2-3 — FR-10, FR-12)

### 4.1 chart_colors Token Design

**Decision G-11**: Each style YAML gets a `chart_colors` array of 6-8 hex values, placed after `color_scheme`. Colors are ordered by visual weight (most prominent first) and designed for sequential use in multi-series data visualizations.

Design principles:
- **First color**: style's accent color (continuity with single-series behavior)
- **Colors 2-4**: harmonious with the style's palette, distinct from each other at a glance
- **Colors 5-8**: progressively more muted (for lower-priority series)
- **Accessible**: each consecutive pair should have >= 3:1 contrast ratio against each other on the style's card_bg

```yaml
# business.yaml
chart_colors:
  - "#e67e22"    # accent (warm orange) — primary series
  - "#1a365d"    # navy — secondary series
  - "#2d5f8a"    # medium blue — tertiary
  - "#27ae60"    # green — quaternary
  - "#8e44ad"    # purple — fifth
  - "#c0392b"    # red — sixth
  - "#16a085"    # teal — seventh
  - "#7f8c8d"    # gray — eighth/overflow

# tech.yaml
chart_colors:
  - "#22d3ee"    # cyan accent — primary
  - "#6366f1"    # indigo — secondary
  - "#a855f7"    # purple — tertiary
  - "#f472b6"    # pink — quaternary
  - "#34d399"    # emerald — fifth
  - "#fbbf24"    # amber — sixth
  - "#818cf8"    # light indigo — seventh
  - "#64748b"    # slate — eighth/overflow

# creative.yaml
chart_colors:
  - "#d97706"    # dark amber accent — primary
  - "#7c3aed"    # violet — secondary
  - "#ec4899"    # pink — tertiary
  - "#059669"    # emerald — quaternary
  - "#2563eb"    # blue — fifth
  - "#dc2626"    # red — sixth
  - "#8b5cf6"    # light violet — seventh
  - "#6b7280"    # gray — eighth/overflow

# minimal.yaml
chart_colors:
  - "#3b82f6"    # blue accent — primary
  - "#18181b"    # near-black — secondary
  - "#71717a"    # zinc — tertiary
  - "#6366f1"    # indigo — quaternary
  - "#0891b2"    # cyan — fifth
  - "#4b5563"    # gray — sixth
  - "#94a3b8"    # light slate — seventh
  - "#d4d4d8"    # light zinc — eighth/overflow
```

### 4.2 svg-generator.md chart_colors Integration

**Decision G-12**: All chart patterns in svg-generator.md updated to use `chart_colors[n]` instead of `${accent}`.

Specific changes:
- Big Number: stays `${accent}` (single value, not a series)
- Progress Bar: stays `${accent}` (single value)
- Sparkline: `chart_colors[0]` for the primary line. If multi-series, `chart_colors[1]`, `chart_colors[2]`, etc.
- Donut Chart: each segment uses `chart_colors[n]` in order. The background track uses `${card_bg}` at 0.2 opacity.
- Horizontal Bar Chart: `chart_colors[n]` per bar if comparing categories, `chart_colors[0]` if ranking within one category.
- Timeline: nodes use `chart_colors[0]` (all same category).

Add a new section to svg-generator.md:

```markdown
### Multi-Series Color Assignment

When a chart has multiple data series:
- Assign `chart_colors[0]` to the primary/most important series
- Assign `chart_colors[1]`, `chart_colors[2]`, etc. in order
- If more series than chart_colors entries, cycle from the beginning
- For grouped bars: each group gets one color from chart_colors
- For stacked charts: layers assigned from bottom (chart_colors[0]) up

Read `chart_colors` from the active style YAML. If `chart_colors` is not
present (backward compatibility), fall back to `[${accent}]` repeated.
```

### 4.3 Guided-Freedom Enforcement Model

**Decision G-13**: Single unified enforcement model for all color usage in slides.

**Three zones**:

| Zone | Colors | Enforcement | Example |
|------|--------|-------------|---------|
| **Mandatory Core** | `primary`, `secondary`, `accent`, `background`, `text`, `card_bg` | Programmatic — technical check flags deviations as Major | Card backgrounds, text fills, slide background |
| **Chart Colors** | `chart_colors[0..7]` | Programmatic — reviewer checks chart elements use only chart_colors | Bar fills, donut segments, line strokes |
| **Decorative Free** | Any color | Must be declared in SVG `<defs>` with `data-decorative="true"` attribute | Background patterns, glow effects, gradient overlays, accent stripes |

**How it works in practice**:
- slide-core MUST use core colors for structural elements (cards, text, backgrounds)
- slide-core MUST use chart_colors for data visualization elements
- slide-core MAY use any color for decorative elements, but must tag them
- reviewer checks: all undeclared non-core, non-chart colors are flagged as Warning (not blocking, but tracked)

**reviewer.md color compliance section rewrite**:

```markdown
### Color Token Compliance (Guided Freedom)

| Zone | Rule | Severity |
|------|------|----------|
| Core colors (primary, secondary, accent, background, text, card_bg) | MUST match style YAML exactly | Major |
| Chart colors | Data viz elements MUST use chart_colors[n] from style YAML | Major |
| Decorative colors | Free to use any color — must be on elements tagged data-decorative="true" or within <defs> gradient/pattern | Warning if untagged |

Do NOT flag decorative elements (background patterns, glow effects, grain
overlays) that use non-token colors — these are creative freedom zones.
Only flag structural elements (card backgrounds, body text, headings) that
deviate from core tokens.
```

---

## 5. SVG Pattern Enrichment (Wave 4 — FR-15)

### 5.1 Missing Patterns

**Decision G-14**: Five new SVG patterns for svg-generator.md, all designed to work with `chart_colors`.

#### 5.1.1 Table Pattern

```xml
<!-- Table: 4 columns x 5 rows -->
<g transform="translate(24, 40)">
  <!-- Header row -->
  <rect x="0" y="0" width="552" height="36" rx="4" fill="${primary}" />
  <text x="12" y="24" font-size="14" font-weight="bold" fill="#ffffff">Column A</text>
  <text x="150" y="24" font-size="14" font-weight="bold" fill="#ffffff">Column B</text>
  <text x="288" y="24" font-size="14" font-weight="bold" fill="#ffffff">Column C</text>
  <text x="426" y="24" font-size="14" font-weight="bold" fill="#ffffff">Column D</text>
  <!-- Data rows (alternate bg) -->
  <rect x="0" y="36" width="552" height="32" fill="${card_bg}" opacity="0.5" />
  <text x="12" y="56" font-size="14" fill="${text}">Value</text>
  <!-- ... repeat, alternate fill="none" and fill="${card_bg}" opacity="0.5" -->
</g>
```

Table constraints:
- Max 6 columns (beyond that, consider splitting or rotating)
- Max 8 data rows (beyond that, use pagination or "Top N" truncation)
- Header row uses `${primary}` background with white text
- Alternate row shading at 0.5 opacity of `${card_bg}`
- Min column width: 80px

#### 5.1.2 Metric Card Grid

```xml
<!-- Metric Grid: 2x2 KPI cards -->
<g transform="translate(60, 120)">
  <!-- Metric 1 -->
  <g transform="translate(0, 0)">
    <rect width="260" height="120" rx="${border_radius}" fill="${card_bg}" filter="url(#card-shadow)" />
    <text x="24" y="40" font-size="14" fill="${text}" opacity="0.6">Revenue</text>
    <text x="24" y="80" font-size="42" font-weight="bold" fill="chart_colors[0]">$2.4M</text>
    <text x="24" y="100" font-size="14" fill="#22c55e">▲ +15%</text>
  </g>
  <!-- Metric 2 at translate(280, 0) -->
  <!-- Metric 3 at translate(0, 140) -->
  <!-- Metric 4 at translate(280, 140) -->
</g>
```

Metric grid constraints:
- 2x2 (4 metrics) or 3x2 (6 metrics) layout
- Each metric card: number + label + optional delta
- Big numbers use `chart_colors[n]` for visual differentiation across cards
- 20px gap between metric cards

#### 5.1.3 Grouped Bar Chart

```xml
<!-- Grouped Bar: 3 categories x 3 groups -->
<g transform="translate(60, 100)">
  <!-- Y-axis labels -->
  <text x="0" y="20" font-size="14" fill="${text}" opacity="0.6" text-anchor="end">Category A</text>
  <!-- Group 1 bars -->
  <rect x="120" y="4" width="180" height="14" rx="3" fill="chart_colors[0]" />
  <rect x="120" y="22" width="140" height="14" rx="3" fill="chart_colors[1]" />
  <rect x="120" y="40" width="200" height="14" rx="3" fill="chart_colors[2]" />
  <!-- Values -->
  <text x="308" y="16" font-size="12" fill="${text}">180</text>
  <!-- Legend -->
  <g transform="translate(120, -30)">
    <rect x="0" y="0" width="12" height="12" rx="2" fill="chart_colors[0]" />
    <text x="18" y="10" font-size="12" fill="${text}">Series A</text>
    <rect x="100" y="0" width="12" height="12" rx="2" fill="chart_colors[1]" />
    <text x="118" y="10" font-size="12" fill="${text}">Series B</text>
    <rect x="200" y="0" width="12" height="12" rx="2" fill="chart_colors[2]" />
    <text x="218" y="10" font-size="12" fill="${text}">Series C</text>
  </g>
</g>
```

Grouped bar constraints:
- Max 5 categories on Y-axis
- Max 4 groups per category (beyond that, too dense)
- Each group gets one `chart_colors[n]`
- Compact legend row above or below the chart
- Bar height: 14-18px with 4px gap between groups

#### 5.1.4 Line Chart with Axes

```xml
<!-- Line Chart with X/Y axes -->
<g transform="translate(80, 40)">
  <!-- Y-axis -->
  <line x1="0" y1="0" x2="0" y2="200" stroke="${text}" stroke-width="1" opacity="0.3" />
  <text x="-12" y="4" font-size="11" fill="${text}" opacity="0.5" text-anchor="end">100</text>
  <text x="-12" y="104" font-size="11" fill="${text}" opacity="0.5" text-anchor="end">50</text>
  <text x="-12" y="204" font-size="11" fill="${text}" opacity="0.5" text-anchor="end">0</text>
  <!-- Grid lines -->
  <line x1="0" y1="100" x2="400" y2="100" stroke="${text}" stroke-width="0.5" opacity="0.1" />
  <!-- X-axis -->
  <line x1="0" y1="200" x2="400" y2="200" stroke="${text}" stroke-width="1" opacity="0.3" />
  <text x="0" y="220" font-size="11" fill="${text}" opacity="0.5" text-anchor="middle">Jan</text>
  <!-- Series 1 -->
  <polyline points="0,160 80,120 160,100 240,60 320,80 400,40"
    fill="none" stroke="chart_colors[0]" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
  <circle cx="400" cy="40" r="4" fill="chart_colors[0]" />
  <!-- Series 2 -->
  <polyline points="0,180 80,170 160,140 240,130 320,110 400,90"
    fill="none" stroke="chart_colors[1]" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
  <circle cx="400" cy="90" r="4" fill="chart_colors[1]" />
</g>
```

Line chart constraints:
- Max 4 series (beyond that, too noisy)
- Max 12 data points per series
- Each series uses `chart_colors[n]`
- Endpoint dots for visual clarity
- Subtle grid lines at 0.1 opacity
- Axis labels at reduced size (11px) and opacity

#### 5.1.5 Network/Relationship Diagram

```xml
<!-- Network Diagram: hub-and-spoke -->
<g transform="translate(300, 180)">
  <!-- Connections (draw FIRST, under nodes) -->
  <line x1="0" y1="0" x2="-180" y2="-100" stroke="${text}" stroke-width="1.5" opacity="0.2" />
  <line x1="0" y1="0" x2="180" y2="-80" stroke="${text}" stroke-width="1.5" opacity="0.2" />
  <line x1="0" y1="0" x2="-160" y2="100" stroke="${text}" stroke-width="1.5" opacity="0.2" />
  <line x1="0" y1="0" x2="180" y2="100" stroke="${text}" stroke-width="1.5" opacity="0.2" />
  <!-- Hub node -->
  <circle r="40" fill="chart_colors[0]" />
  <text text-anchor="middle" dy="5" font-size="14" font-weight="bold" fill="#ffffff">Core</text>
  <!-- Spoke nodes -->
  <g transform="translate(-180, -100)">
    <circle r="28" fill="chart_colors[1]" />
    <text text-anchor="middle" dy="5" font-size="12" fill="#ffffff">Node A</text>
  </g>
  <!-- ... more spoke nodes with chart_colors[2], [3], etc. -->
</g>
```

Network diagram constraints:
- Max 8 nodes total (hub + 7 spokes)
- Hub-and-spoke preferred for clarity; free-form only if relationship structure demands it
- Connections drawn before nodes (z-order)
- Node colors from `chart_colors[n]`
- Text inside nodes: white fill, centered
- Connection lines: `${text}` at 0.2 opacity

### 5.2 Pattern Guidelines Addition

Add to svg-generator.md after Chart Constraints:

```markdown
### Pattern Selection by Content

| Content Signal | Recommended Pattern |
|---------------|-------------------|
| "compared to", "vs", multiple named metrics | Grouped Bar Chart |
| "over time", "trend", "growth", months/quarters | Line Chart with Axes |
| Exact values in rows and columns | Table |
| 3-6 KPIs with numbers and deltas | Metric Card Grid |
| "ecosystem", "connected", "depends on", relationships | Network Diagram |
```

---

## 6. Holistic Deck Review (Wave 3-4 — FR-14, FR-16)

### 6.1 visual_weight in outline.json

**Decision G-15**: Add `visual_weight` field to page schema for proactive visual planning.

```json
{
  "index": 5,
  "title": "Revenue Breakdown",
  "type": "data",
  "visual_weight": "high",
  "key_points": [...],
  "layout_hint": "hero_grid",
  "notes": {...}
}
```

Values:
- `"low"`: Breathing slide — single_focus, quote, image. Minimal visual density.
- `"medium"`: Standard content slide — moderate card count, balanced whitespace.
- `"high"`: Dense data or comparison slide — multiple cards, charts, high information density.

**Assignment rules** (in outline-architect.md):
- `cover`, `quote`, `image` → always `"low"`
- `content` with <= 3 key_points → `"medium"`
- `content` with > 3 key_points → `"high"`
- `data`, `comparison` → `"high"` by default
- `process`, `timeline` → `"medium"`
- End page → `"low"`

**Visual rhythm validation**: The outline should avoid 3+ consecutive `"high"` slides. If detected, content-core should insert a breathing slide or flag for user review.

### 6.2 Gemini Holistic Review Protocol

**Decision G-16**: Expand reviewer.md Holistic Deck Review section into a full protocol.

```markdown
## Holistic Deck Review (mode=holistic)

Run once after all individual slides pass review. Read ALL `slides/slide-*.svg`
and `outline.json` (for visual_weight hints).

### Assessment Dimensions

1. **Visual Rhythm**: Map the visual_weight sequence across slides.
   - Flag: 3+ consecutive "high" weight slides without a breathing slide
   - Flag: 2+ consecutive identical layout types
   - Ideal: alternating dense/sparse pattern with climax at key message

2. **Color Story Escalation**: Track accent color usage per slide.
   - Flag: accent on every slide (= no emphasis anywhere)
   - Flag: no accent on the key message slide
   - Ideal: accent usage builds toward the 1-2 most important slides

3. **Layout Variety**: Count distinct layout types used across the deck.
   - Flag: < 3 distinct layouts in a 10+ slide deck
   - Flag: same layout used > 40% of slides
   - Ideal: 4-5 distinct layouts that match content types

4. **Style Consistency**: Check shadows, border-radius, font sizes, gaps.
   - Flag: inconsistent border-radius across slides (e.g., 12px and 20px)
   - Flag: different shadow depths for equivalent card types
   - These should be uniform — unlike layout variety, consistency is good

5. **Pacing**: Verify narrative arc alignment.
   - Setup slides (~15%): should be lower visual_weight
   - Tension slides (~60%): escalating weight with accent usage
   - Resolution slides (~25%): strong weight at climax, then tapering

### Output

Holistic review produces `deck_coordination` suggestions — each targeting
a specific slide with a proposed change that improves deck-level coherence.
These are queued by the orchestrator for a re-design pass.

Holistic score gate: >= 7/10 overall coherence. If < 7, the orchestrator
should apply the top 3 deck_coordination suggestions (by severity) and
re-run holistic review once.
```

### 6.3 deck_coordination Flow

**Decision G-17**: When holistic review produces `deck_coordination` suggestions, the orchestrator:

1. Receives `review_holistic_done` with suggestion JSON from review-core
2. Filters to `suggestion_type: "deck_coordination"` only
3. Groups by target slide index
4. For each affected slide, spawns a new slide-core task with:
   - `mode: design` (fresh generation)
   - `fixes_json`: the deck_coordination suggestion's `layout_suggestion` as a constraint
   - `context: "deck_coordination_pass"` flag so slide-core knows this is a deck-level adjustment
5. After all affected slides are regenerated, runs holistic review once more (max 1 re-run)

---

## 7. Optimization Suggestion → Execution Strategy Mapping (Wave 3 — FR-13)

### 7.1 Suggestion-Driven Fix Strategy

**Decision G-18**: Replace score-driven fix routing with suggestion-type-driven routing.

| Suggestion Type | slide-core Execution | Model | Max Rounds |
|----------------|---------------------|-------|------------|
| `attribute_change` | Deterministic patch: parse selector_hint, change attribute. No regeneration. | sonnet (Wave 4, after UD-1 resolved); opus until then | N/A (applied in one pass) |
| `layout_restructure` | Regenerate with constraints: re-read outline, apply `layout_suggestion` as binding layout requirement. Content preserved. | opus | 1 |
| `full_rethink` | Regenerate from scratch: re-read outline, re-select layout, ignore current SVG entirely. | opus | 1 |
| `content_reduction` | Regenerate with simplified content: reduce key_points from outline, add "detail in notes" markers. If suggestion says "split slide", flag to orchestrator. | opus | 1 |
| `deck_coordination` | Handled by orchestrator, not individual fix loop. See section 6.3. | opus | 1 (via orchestrator) |

**Score as auxiliary gate**: The overall_score remains as a pass/fail signal (>= 7.0 = pass). But the fix strategy is driven by what suggestions exist, not by the score value.

| Scenario | Behavior |
|----------|----------|
| Score >= 7 AND no critical/major suggestions | Pass — no fixes |
| Score >= 7 BUT has major suggestions | Apply suggestions (Gemini sees something worth improving even though it "passes") |
| Score < 7 AND has suggestions | Apply suggestions per type |
| Score < 7 AND no suggestions | Regenerate from scratch (Gemini couldn't articulate what's wrong — start over) |
| Technical-only (no Gemini) AND has critical technical issues | Apply attribute_change fixes for technical violations |
| Technical-only (no Gemini) AND no critical issues | Pass — no aesthetic improvements possible without Gemini |

### 7.2 Fix Loop Simplification

**Decision G-19**: The fix loop in ppt.md Phase 6 simplifies from score-band routing to:

```
1. Receive review from review-core
2. If pass AND no critical/major suggestions → mark slide complete
3. If has suggestions:
   a. Separate attribute_change suggestions → batch as one patch pass
   b. If any layout_restructure or content_reduction → pick the highest-severity one, regenerate with that constraint
   c. If any full_rethink → regenerate from scratch (ignore attribute_change)
   d. If any deck_coordination → queue for holistic pass (don't process now)
4. After fix pass, re-review (max 2 total rounds per slide)
5. After round 2, accept current result regardless
```

Priority cascade: `full_rethink` > `layout_restructure` > `content_reduction` > `attribute_change`. If a full_rethink is suggested, don't bother patching attributes — the whole slide is being redone.

---

## 8. Implementation Sequence

### Wave 2 (ship together, then calibrate)

1. **FR-07 + FR-09** (ATOMIC):
   - Rewrite reviewer.md: optimization-first output format, 5-type suggestion taxonomy, extended JSON schema
   - Update SKILL.md: `## Optimization Criteria`, prompt template rewrite
   - Update review-core.md: execution steps 6-8 for new format, new signal types

2. **FR-08**:
   - Rewrite SKILL.md fallback (line 81, Fallback Strategy section)
   - Rewrite review-core.md step 7 fallback path
   - Update ppt.md fallback description

3. **FR-10**:
   - Add `chart_colors` to all 4 style YAMLs
   - Update svg-generator.md chart patterns with `chart_colors[n]`
   - Add Multi-Series Color Assignment section

4. **Calibration gate**: Production run (8-10 slides) to validate:
   - Does Gemini produce the 5 suggestion types?
   - Are layout_suggestion descriptions actionable by slide-core?
   - Does the technical-only fallback catch real issues?

### Wave 3 (informed by calibration)

5. **FR-12**: Guided-freedom enforcement model in slide-core and reviewer.md
6. **FR-13**: Suggestion-driven fix strategy in ppt.md and slide-core (may adjust taxonomy based on calibration)
7. **FR-14**: visual_weight in outline.json + holistic review protocol design

### Wave 4

8. **FR-15**: Five new SVG patterns in svg-generator.md
9. **FR-16**: Holistic review implementation (deck_coordination flow)
10. **FR-23**: Cognitive design principles in outline-architect.md and reviewer.md

---

## Summary of Key Architecture Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| G-01 | Optimization suggestions are primary output, score is secondary | Reframes Gemini as collaborator, not judge |
| G-02 | Prompt template uses "Optimization Criteria" heading | Language shapes behavior |
| G-03 | Three reviewer.md framing changes | Consistent optimizer voice throughout |
| G-04 | 5-type suggestion taxonomy | Maps cleanly to execution strategies |
| G-05 | Extended JSON schema with suggestion_type + layout_suggestion | Enables type-driven routing |
| G-06 | Missing suggestion_type defaults to attribute_change | Backward compatible |
| G-07 | Technical-only fallback scope defined | Honest about what self-review can/cannot do |
| G-08 | Distinct output format for technical validation | Prevents downstream from treating as aesthetic pass |
| G-09 | SKILL.md fallback rewrite removes contradiction | Single source of truth for fallback policy |
| G-10 | Technical validation inlined in review-core (option b) | Simplest implementation, no new files |
| G-11 | chart_colors: 6-8 ordered hex values per style | Accent first, progressively muted |
| G-12 | Chart patterns use chart_colors[n] | Multi-series support |
| G-13 | Guided-freedom: 3 zones (core/chart/decorative) | Single enforcement model, not split strict/flexible |
| G-14 | 5 new SVG patterns with chart_colors integration | Covers observed production gaps |
| G-15 | visual_weight field in outline.json | Proactive rhythm planning at outline time |
| G-16 | Holistic review protocol with 5 dimensions | Gemini's most irreplaceable contribution |
| G-17 | deck_coordination flows through orchestrator queue | Respects star topology |
| G-18 | Suggestion-type-driven fix routing | Replaces score-only routing |
| G-19 | Priority cascade for mixed suggestion types | full_rethink > restructure > reduction > attribute |
