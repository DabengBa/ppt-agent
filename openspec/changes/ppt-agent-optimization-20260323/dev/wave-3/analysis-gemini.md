# Analysis: T-15 + T-16 (Gemini, lead-executed due to API 429)

## T-15 Analysis

Same as codex analysis. Key design decisions:
- Table pattern should use rect backgrounds per row, not actual HTML table
- Metric Card Grid is a layout pattern, not a chart — it's a grid of Big Number cards
- Grouped Bar needs vertical bars (not horizontal) with series clustering
- Line Chart needs proper SVG path for smooth curves
- Network diagram should use force-layout-style positioning

## T-16 Analysis

Agree with codex. Additional considerations:
- deck_coordination suggestions from holistic review target multiple slides — the orchestrator needs to batch slide-core dispatches
- Only priority-1 deck_coordination suggestions should trigger auto-fix; priority-2/3 are advisory only
- The re-run holistic review is a lighter check — only verify that the specific flagged dimensions improved
- review-core.md holistic mode should explicitly read outline.json for visual_weight data
