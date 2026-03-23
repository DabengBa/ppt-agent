# Changes: Wave 2 — T-13 Suggestion-Driven Fix Strategy

> Date: 2026-03-23
> Merge strategy: Codex numbered-step format + Gemini 3-column table + Codex edge case handling

## Files Modified

### 1. commands/ppt.md (+18/-7)

**Phase 6 fix loop (line 229)**: Replaced score-band routing with suggestion-type-driven routing.

Old: 4 score bands (>=7, 5-6.9, 3-4.9, <3) determining fix rounds.
New: 6-step routing:
1. Parse suggestions JSON + overall_score
2. Score >= 7.0 + gates pass + no P1 suggestions → PASS
3. Score < 7.0 OR gates fail → enter fix loop
4. Route by highest-impact suggestion type:
   - `full_rethink` → regenerate, max 1 round
   - `layout_restructure`/`content_reduction` → constrained regen, max 2 rounds
   - `attribute_change` → deterministic patch, max 1 round
5. No suggestions + score < 7.0 → accept with warning
6. Fallback (no Gemini) → technical fixes only

**Quality Gates section (line 381)**: Updated summary to reflect type-driven routing.

### 2. skills/gemini-cli/references/roles/reviewer.md (+10/-6)

**Adaptive Fix Budget table (line 261)**: Replaced "based on initial score" table with "based on highest-priority suggestion type" table.

New 3-column format (Type / Action / Budget):
- None + pass conditions → 0 rounds
- `attribute_change` only → Max 1 round
- `layout_restructure`/`content_reduction` → Max 2 rounds
- `full_rethink` → Max 1 round (regenerate)
- No suggestions + low score → Accept with warning

Added technical-only fallback reference.

### 3. agents/slide-core.md — NO CHANGES

Lines 49-55 already implement correct type-aware fix handling with priority cascade. No modifications needed.

## Cross-File Consistency

| Concept | ppt.md | reviewer.md | slide-core.md |
|---------|--------|-------------|---------------|
| Type routing order | full_rethink > layout_restructure > content_reduction > attribute_change | Same in table | Same priority cascade (line 55) |
| full_rethink budget | Max 1 round | Max 1 round | N/A (executor) |
| layout_restructure budget | Max 2 rounds | Max 2 rounds | N/A (executor) |
| attribute_change budget | Max 1 round | Max 1 round | N/A (executor) |
| Edge case (no suggestions) | Accept with warning | Accept with warning | N/A |
| Fallback | Technical fixes only | Referenced | N/A |
