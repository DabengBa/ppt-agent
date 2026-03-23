# Dev Scope — Wave 2: Rebuild Aesthetic Optimization Layer

> Proposal: ppt-agent-optimization-20260323
> Scope: T-07 + T-08 + T-09 + T-10 + T-10b (5 tasks, full Wave 2)
> Status: COMPLETE

## Selected Tasks

### T-07: Rewrite Gemini optimizer role prompts (P0, L) ✅
- Restructured reviewer.md output format: suggestions-first, scores secondary
- Updated SKILL.md prompt template and review-core.md execution steps

### T-09: Enrich suggestion format with 5-type taxonomy (P0, M) ✅
- Defined 5 suggestion types with JSON schemas in reviewer.md
- Documented handling per type in slide-core.md
- Updated review-core.md signal format

### T-08: Redefine self-review fallback as technical validation only (P0, M) ✅
- Rewrote SKILL.md fallback strategy
- Split review-core.md quality gates into dual-mode
- Updated ppt.md fallback rule

### T-10: Add chart_colors to style YAMLs + svg-generator (P1, S) ✅
- Added chart_colors array (8 hex, [0]=accent) to all 17 styles
- Updated svg-generator.md with chart_colors documentation and pattern examples

### T-10b: Expand style palette from 4 to 17 (P1, M) ✅
- Created 13 new style YAMLs with full token schema
- Updated index.json (v1.0.0→v1.1.0, 4→17 styles)

## Verification Summary
- Cross-file consistency verified (5-type taxonomy, fallback strategy, output format)
- chart_colors[0]==accent verified for all 17 styles
- 17 YAML files + index.json entries confirmed
- No stale references to old formats
