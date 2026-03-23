# Changes — Wave 2: Rebuild Aesthetic Optimization Layer (T-07~T-10b)

## skills/gemini-cli/references/roles/reviewer.md (T-07+T-09)
- **Output format restructured**: suggestions-first, scores secondary. Old order: scores → issues → fix JSON. New order: Optimization Suggestions (typed) → Suggestions JSON → Quality Gate (scores + hard rule violations).
- **5-type suggestion taxonomy added** (T-09): `attribute_change`, `layout_restructure`, `full_rethink`, `content_reduction`, `deck_coordination`. Each type has a defined JSON schema with `type`, `priority` (1-3), `description`, and type-specific `details`.
- **Priority system**: 1=must-fix, 2=should-fix, 3=nice-to-have. Replaces flat severity (critical/major/minor) on suggestions.
- **Old flat fix JSON absorbed**: `attribute_change` type replaces the old flat `{element, selector_hint, attribute, current, target, severity, reason}` format.
- **Holistic review updated**: outputs `deck_coordination` suggestions only.
- **Methodology updated**: step 2 and 3 rewritten to emphasize typed suggestions over scoring.

## skills/gemini-cli/SKILL.md (T-07+T-08)
- **Prompt template updated**: instructions now request typed optimization suggestions as primary output, quality gate as secondary.
- **Fallback Strategy rewritten** (T-08): "Technical Validation Only" — hard-rule checks only, no aesthetic scores, no optimization suggestions. Includes rationale (production data showing rubber-stamp scores).
- **Constraints table updated**: "MUST fall back to technical validation on exit 2" (was: "self-review"). "Review MUST produce typed suggestions (Gemini) or hard-rule pass/fail (fallback)".

## agents/review-core.md (T-07+T-08+T-09)
- **Execution steps 6-11 rewritten**: step 6 prompt updated for suggestion-first output. Step 7 fallback path now performs technical validation only. Step 8 writes typed suggestions. Step 9 split: Gemini path (weighted scores) vs technical path (hard-rule pass/fail).
- **Signal format clarified**: `review_failed(suggestions_json=[...])` — typed JSON array passed as `fixes_json` to slide-core downstream.
- **Quality Gates section split**: "Full Review (Gemini available)" vs "Technical Validation Only (Gemini unavailable)".
- **Technical validation output format specified**: header marking, Hard Rule Results table, no scores/suggestions.

## agents/slide-core.md (T-09)
- **Typed suggestion handling documented**: each of the 5 types maps to a specific execution strategy:
  - `attribute_change` → deterministic patch
  - `layout_restructure` → regenerate with layout constraint
  - `full_rethink` → regenerate from scratch using guidance
  - `content_reduction` → reduce content then regenerate
  - `deck_coordination` → not handled (flagged for lead/holistic)
- **Priority ordering**: `full_rethink` > `layout_restructure` > `content_reduction` > `attribute_change` (higher-impact supersedes lower).

## commands/ppt.md (T-08)
- **Fallback rule rewritten**: Gemini unavailable → technical validation only, no fix loop triggers, pass/fail on hard rules only.
- **review_engine field**: `"claude-self-review"` → `"technical-validation-only"` in review-manifest.json schema.
- **Holistic review clarified**: `deck_coordination` suggestions are reported, not auto-fixed.

## Key Decisions
- **Parameter naming**: review-core sends `suggestions_json` in signal; lead passes it as `fixes_json` parameter to slide-core (keeps existing dispatch contract).
- **Suggestion priority vs score routing**: Wave 2 defines the taxonomy; Wave 3 (T-13) implements suggestion-driven routing in the fix loop. Currently, score-based routing still determines fix budget (max rounds), but suggestions now carry type information for T-13.
- **Technical validation format**: simplified report (header + Hard Rule Results table) — no Optimization Suggestions, no Suggestions JSON, no Quality Gate sections.

---

## Part 2: Style Palette (T-10 + T-10b)

## 4 existing style YAMLs (T-10)
- **chart_colors added**: ordered array of 8 hex colors for multi-series data visualization. `chart_colors[0]` equals `accent` for single-series backward compatibility.
- Styles updated: business, tech, minimal, creative.

## skills/_shared/references/prompts/svg-generator.md (T-10)
- **Design Tokens section**: added `chart_colors` to the token list with usage documentation.
- **Chart Colors subsection**: describes multi-series assignment rules and legacy fallback.
- **Donut Chart pattern**: updated to use `chart_colors[0]` instead of `accent`.
- **Horizontal Bar Chart pattern**: updated to use `chart_colors[0]` with multi-series comment.

## 13 new style YAMLs (T-10b)
- Created: blueprint, bold-editorial, chalkboard, editorial-infographic, fantasy-animation, intuition-machine, notion, pixel-art, scientific, sketch-notes, vector-illustration, vintage, watercolor.
- All follow standard schema: name, mood, color_scheme (with chart_colors), typography (with cjk_font), card_style, gradients, elevation, decoration, slide_type_overrides.
- Each has unique visual identity, typography pairing, and decoration settings.

## skills/_shared/index.json (T-10b)
- Version 1.0.0 → 1.1.0.
- styles count 4 → 17.
- 13 new resource entries with unique id, keywords (Chinese + English), description, use_cases.

## Key Decisions (Part 2)
- **chart_colors length**: 8 colors per style (sufficient for most chart use cases, avoids excessive palette management).
- **Font choices**: new styles use distinctive heading fonts to maximize visual differentiation (e.g., Cinzel for fantasy, Press Start 2P for pixel-art, Caveat for chalkboard).
- **Dark vs light**: 5 dark-background styles (blueprint, tech, chalkboard, fantasy-animation, intuition-machine, pixel-art), 11 light-background styles.
- **Pattern decoration**: 6 styles use patterns (dots or grid), 11 use none — keeps the default clean.
