Here is the implementation analysis for replacing score-driven fix routing with suggestion-type-driven routing.

### 1. Changes Needed in `commands/ppt.md` (Lines 229-243)
The orchestrator routing logic must be updated to branch on the highest-priority suggestion type rather than the score bands, while still using the score as the initial pass/fail gate. Also, the fallback mode needs to be explicitly defined here.

**Proposed Replacement Text:**
```markdown
3. **Fix loop** (adaptive budget per Suggestion Type): if review fails (Score < 7.0 or hard gates fail), routing depends on the highest priority suggestion type returned by the review:
   - `full_rethink`: Regenerate from scratch, max 1 round. Re-run `mode=design` **without** `fixes_json` so slide-core produces a fresh layout.
   - `layout_restructure` or `content_reduction`: Constrained regeneration, max 2 rounds. Re-run with `fixes_json`.
   - `attribute_change` only: Deterministic patch, max 1 round. Re-run with `fixes_json`.
   - **Fallback mode (no Gemini)**: Technical XML fixes only, no suggestion routing.

   For fix rounds (`layout_restructure`, `content_reduction`, or `attribute_change`), re-run slide-core with fixes:
   ```text
   Task(subagent_type="ppt-agent:slide-core", prompt="run_dir=${RUN_DIR} mode=design slide_index=${N} style=${STYLE} fixes_json=${FIXES}")
   ```
   For regeneration (`full_rethink`), re-run without fixes:
   ```text
   Task(subagent_type="ppt-agent:slide-core", prompt="run_dir=${RUN_DIR} mode=design slide_index=${N} style=${STYLE}")
   ```
   Then re-run review-core. If still failing after max rounds, accept current version with quality note.
```

### 2. Changes to `agents/slide-core.md` (Lines 49-55)
**No changes are needed in `slide-core.md`.**
The file already correctly defines how to handle the `fixes_json` based on the suggestion types (`attribute_change`, `layout_restructure`, `full_rethink`, `content_reduction`) and correctly enforces the priority cascade (`full_rethink` > `layout_restructure` > `content_reduction` > `attribute_change`). Since the logic for executing the fixes is already type-driven, updating the orchestrator (`commands/ppt.md`) to align with this is sufficient.

### 3. Changes to `reviewer.md` (Adaptive Fix Budget Table)
**Yes, the table requires an update.**
The "Adaptive fix budget based on initial score" table (around line 261 in `skills/gemini-cli/references/roles/reviewer.md`) must be rewritten to match the new type-driven logic so the reviewer outputs expectations that align with the orchestrator.

**Target Table Update for `reviewer.md`:**
```markdown
**Adaptive fix budget based on highest-priority suggestion**:
| Primary Suggestion Type | Action | Budget |
|-------------------------|--------|--------|
| None (Score >= 7.0 + gates pass) | Pass — no fixes needed | 0 rounds |
| `attribute_change` only | Deterministic patch | Max 1 round |
| `layout_restructure` or `content_reduction` | Constrained regeneration | Max 2 rounds |
| `full_rethink` | Regenerate from scratch (do not patch) | Max 1 round |
```

### 4. Cross-cutting Affected Files
- **`agents/review-core.md`**: Line 69 mentions "Determine fix action based on Adaptive Fix Budget table." This language can remain as-is since it delegates to `reviewer.md`, but it implies the reviewer agent needs to parse the suggestion types to determine the fix action rather than just the score.
- **`slide-status.json`**: If the orchestrator (`commands/ppt.md`) reads from `slide-status.json` to determine routing, the review output parser must ensure that the `highest_priority_suggestion` (or equivalent list of suggestion types) is correctly aggregated into `slide-status.json` alongside the score.
- **Review Output Prompts/Formats**: If the reviewer outputs the suggested action as a text summary, the formatting instructions in `reviewer.md` need to enforce returning the `suggestion_type` explicitly in the top-level review payload so the orchestrator can route it without guessing.

### 5. Risk Assessment
- **Misalignment of review payloads (Medium Risk):** If the reviewer outputs a low score but fails to categorize its suggestions into the exact enum types (`attribute_change`, etc.), the orchestrator might fail to route the fix.
- **Lost fix contexts (Low Risk):** Since `full_rethink` drops the `fixes_json`, any granular `attribute_change` suggestions accompanying a `full_rethink` will be lost. This is acceptable per the priority cascade but requires the reviewer not to mix nitpicks with fundamental rewrites.
- **Infinite loops (Low Risk):** Bounding the max rounds specifically by the highest suggestion type (1, 2, 1) prevents runaway generation loops, making this safer than the previous generic "2 rounds for score 5.0" approach.

### 6. Verification Criteria
To verify the implementation is successful:
1. **Routing Test (Constrained Regeneration):** Run a generation where a slide scores 6.5 and outputs a `layout_restructure` suggestion. Verify that `slide-core` is dispatched with `fixes_json` included, and that a second round of fixes is permitted if it fails again.
2. **Routing Test (Regeneration):** Run a generation where a slide outputs a `full_rethink` suggestion (regardless of score, e.g., 4.5). Verify that `slide-core` is dispatched **without** `fixes_json` and that it caps at exactly 1 fix round.
3. **Routing Test (Patch):** A slide passing with 7.5 but failing a hard gate with an `attribute_change` must route to `slide-core` with `fixes_json` and run a maximum of 1 round.
4. **Fallback Test:** Simulate a run with no Gemini API keys and ensure only technical XML validation errors trigger fixes.
