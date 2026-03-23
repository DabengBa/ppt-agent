# Analysis: T-13 Suggestion-Driven Fix Strategy (Codex)

## Summary

T-13 requires rewriting ppt.md Phase 6 fix loop from score-band routing to suggestion-type routing. slide-core.md already handles typed suggestions correctly — no changes needed there.

## File-by-File Analysis

### 1. commands/ppt.md (lines 229-243) — FULL REWRITE

**Current**: Score-band routing (>=7 pass, 5-6.9 fix 2, 3-4.9 fix 1, <3 regenerate)
**Target**: Type-driven routing with score as auxiliary pass/fail gate

New routing logic:
1. Parse review output: extract `suggestions` JSON array and `overall_score`
2. If score >= 7.0 AND all hard gates pass AND no priority-1 suggestions → PASS
3. If score < 7.0 OR hard gates fail OR priority-1 suggestions exist → enter fix loop
4. Fix loop routes by **highest-impact suggestion type present**:
   - `full_rethink` present → regenerate from scratch (no fixes_json), max 1 round
   - `layout_restructure` or `content_reduction` present → constrained regen with fixes_json, max 2 rounds
   - `attribute_change` only → deterministic patch with fixes_json, max 1 round
5. If no suggestions but score < 7.0 → accept with warning (edge case: score fails but no actionable suggestions)
6. Fallback (no Gemini/technical-only mode) → only technical fixes (XML, viewBox, etc.), no suggestion routing

**Key change from calibration**: Slide-05 scored 3.65 with content_reduction + layout_restructure suggestions. Under old rules: 1 round max. Under new rules: 2 rounds (layout_restructure is the highest-impact type present).

### 2. agents/slide-core.md — NO CHANGES

Lines 49-55 already implement:
- Priority cascade: full_rethink > layout_restructure > content_reduction > attribute_change
- Type-specific execution strategies
- full_rethink supersedes all other suggestions

This is already correct and aligned with T-13's target.

### 3. skills/gemini-cli/references/roles/reviewer.md — TABLE UPDATE

The "Adaptive fix budget based on initial score" table (around line 259-265) must be updated to match the new type-driven routing. Otherwise reviewer and orchestrator have mismatched expectations.

### 4. Edge Cases

1. **No suggestions but score < 7.0**: Can happen if Gemini gives a low score with only general observations, no typed suggestions. → Accept with warning.
2. **Priority-1 full_rethink + priority-2 attribute_changes**: full_rethink supersedes all — attribute_changes are discarded. This is correct per slide-core's cascade.
3. **Fallback mode**: Technical validation doesn't produce suggestions → no fix loop, pass/fail on hard rules only.

## Execution Order

Single edit session: ppt.md fix loop first, then reviewer.md table.
