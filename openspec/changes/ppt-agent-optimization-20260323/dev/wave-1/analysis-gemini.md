# Implementation Analysis: Wave 3 PPT Agent Tasks (T-11, T-12, T-14)

As the Implementer, the focus here is on behavioral correctness, structural safety, and ensuring prompt changes directly translate to predictable multi-agent interactions.

Here is the concrete execution plan and analysis for the three target tasks.

---

## Task T-11: `slide-status.json` Atomic Write
**Goal:** Prevent progress loss during Phase 6 orchestration crashes by hardening the JSON state persistence.

### 1. Exact Changes Needed
**File:** `commands/ppt.md`
**Target Section:** Phase 6 orchestration loop / Incremental progress tracking.
**Changes:** Replace direct file redirection/appending with an atomic write-and-swap pattern.
```bash
# Old pattern
# echo "$NEW_STATE" > "${RUN_DIR}/slide-status.json"

# New pattern
cat << 'EOF' > "${RUN_DIR}/slide-status.tmp.json"
{ "slides": ... }
EOF

# Validate structural integrity before committing
if jq -e . "${RUN_DIR}/slide-status.tmp.json" > /dev/null 2>&1; then
    mv "${RUN_DIR}/slide-status.tmp.json" "${RUN_DIR}/slide-status.json"
else
    echo "Error: Generated state JSON is invalid. Discarding update." >&2
fi
```

### 2. Implementation Approach
*   **Mechanical:** Locate the state update command in `commands/ppt.md`.
*   **Injection:** Wrap the JSON generation in a temporary file write (`.tmp.json`).
*   **Validation:** Insert a `jq` check.
*   **Commit:** Use `mv` for the atomic file swap. `mv` on POSIX systems within the same filesystem guarantees atomicity.

### 3. Cross-file Consistency Risks
*   **Minimal:** As long as readers (`--run-id` resume logic) only target `slide-status.json` and never the `.tmp` file, there are no cross-file risks. Ensure the resume logic specifically checks for file existence before reading.

### 4. Edge Cases and Failure Modes
*   **Disk Quota Exceeded / Process Killed mid-write:** The `.tmp.json` file will be truncated or malformed. The `jq` validation will fail, the `mv` will not occur, and the previous valid `slide-status.json` will be preserved. The system loses one slide's progress rather than the entire deck's progress.
*   **Missing Dependencies:** Assumes `jq` is available in the CLI environment. (Given the nature of the tool, this is highly probable, but worth verifying).

### 5. Verification Strategy
*   **Simulated Crash:** Run a dummy loop updating a JSON file. Insert a `sleep 1` and manually send `SIGKILL` (`kill -9`) to the process. Verify that the original `slide-status.json` remains completely intact and valid.

---

## Task T-12: Guided-Freedom Color Enforcement
**Goal:** Stop the reviewer from penalizing decorative elements while strictly enforcing brand colors on core semantic UI.

### 1. Exact Changes Needed
**File A:** `agents/slide-core.md`
**Changes:** Remove the blanket "no hardcoded colors" rule. Insert the 3-zone color model:
> *   **Mandatory Core:** Backgrounds, primary text, and standard cards MUST use strict semantic YAML tokens (`primary`, `secondary`, `text`, etc.).
> *   **Chart Colors:** Data visualizations MUST sequence through `chart_colors` array.
> *   **Decorative Free:** Gradients, glows, abstract shapes, and pattern fills MAY use arbitrary colors, but MUST either be enclosed in `<defs>` OR carry the attribute `data-decorative="true"`.

**File B:** `skills/gemini-cli/references/roles/reviewer.md`
**Changes:** Update the Quality Standards table.
> *   **Violation - Major:** Semantic elements (text, cards) deviating from YAML tokens.
> *   **Violation - Warning:** Arbitrary hex codes found on elements missing `data-decorative="true"` or outside `<defs>`.
> *   **Pass:** Arbitrary colors on `data-decorative="true"` elements.

### 2. Implementation Approach
*   **Creative/Translational:** Translate AD-11 into explicit, declarative prompt constraints for both the generator (`slide-core`) and the evaluator (`reviewer`).

### 3. Cross-file Consistency Risks
*   **Generation/Evaluation Mismatch:** If `slide-core.md` is updated but `reviewer.md` is delayed (or vice-versa), either the reviewer will constantly fail valid SVGs, or the generator will produce invalid SVGs that pass review. Both prompts must be committed in the same atomic update.

### 4. Edge Cases and Failure Modes
*   **Heavy Decoration Styles:** Styles like "watercolor" or "cyberpunk" rely heavily on inline gradients and complex layered vectors. If the LLM forgets to append `data-decorative="true"` to a group `<g>` tag containing 50 paths, the reviewer might spam 50 separate color warnings. The prompt in `slide-core.md` must explicitly mention applying `data-decorative="true"` to parent `<g>` wrapper tags to cascade intent.

### 5. Verification Strategy
*   **Prompt Dry-Run:** Feed a mocked SVG containing `<path fill="#FF00FF" data-decorative="true" />` and `<text fill="#FF00FF">` to the `review-core` prompt. Assert that it flags the text (Major) but ignores the path (Pass).

---

## Task T-14: Holistic Deck Review Design
**Goal:** Implement deck-wide cohesion checks (rhythm, pacing, consistency) rather than just single-slide vacuum checks.

### 1. Exact Changes Needed
**File A:** `skills/_shared/references/prompts/outline-architect.md`
**Changes:** Extend the JSON schema definition for the page object:
> ```json
> "visual_weight": "low | medium | high", // low: breathing/quotes, medium: standard content, high: key data/climax
> ```

**File B:** `skills/gemini-cli/references/roles/reviewer.md`
**Changes:** Rewrite the "Holistic review" section.
> *   **Input Dependency:** Require full `outline.json` and all generated SVGs.
> *   **5 Dimensions:** Explicitly list the AD-13 dimensions with their quantitative triggers (e.g., "Visual Rhythm: Trigger if 3+ consecutive high-weight slides").
> *   **Output Schema:** Define the `deck_coordination` JSON structure:
> ```json
> "deck_coordination": [
>   { "target_slide": "04", "issue": "Pacing", "suggestion": "Change layout to single_focus to break 3-slide high-weight streak" }
> ]
> ```

### 2. Implementation Approach
*   **Creative/Architectural:** Update schemas and instructional text. Ensure the `deck_coordination` array aligns with the existing suggestion taxonomy from T-09.

### 3. Cross-file Consistency Risks
*   **Pipeline Data Flow:** The `reviewer.md` holistic pass relies on `outline-architect.md` generating the `visual_weight` property. Older saved `outline.json` files will lack this property and cause the reviewer to hallucinate or crash.
*   **Orchestrator Blind Spot:** The prompt specifies a "deck_coordination_pass" workflow, but `commands/ppt.md` must actually implement this feedback loop. (Though modifying the orchestrator loop might fall under a separate execution task, the prompts must be ready for it).

### 4. Edge Cases and Failure Modes
*   **Short Decks (< 6 slides):** Quantitative rules like "Flag < 3 distinct layouts in 10+ slide deck" will fail or create noise on short presentations. Add a prompt constraint: *"Adjust threshold proportionality for decks under 10 slides; ignore layout variety warnings for decks under 5 slides."*
*   **Infinite Loops:** The architecture specifies "max 1 re-run" for deck coordination. The `reviewer.md` prompt must be told: *"If flag `deck_coordination_pass` is true in context, DO NOT generate further deck_coordination suggestions."*

### 5. Verification Strategy
*   **Schema Linting:** Verify the new `outline.json` schema is valid JSON.
*   **Mocked Context Test:** Provide a mock outline of 4 "high" weight slides in a row to the reviewer prompt and verify it successfully emits a `deck_coordination` warning based on the Visual Rhythm rule.

---

## 6. Implementation Order

These tasks have differing blast radii. The optimal sequence balances safety and file contention:

1.  **Parallel Track 1: T-11 (Atomic Write)**
    *   *Why:* Strictly localized to `commands/ppt.md`. Purely mechanical shell scripting. Can be implemented and merged immediately without affecting any LLM behavior.
2.  **Sequential Track 2: T-14 then T-12 (Prompt Engineering)**
    *   *Why T-14 first:* `outline-architect.md` changes should be merged first so the pipeline begins generating `visual_weight` fields in new outlines immediately. This seeds data for the holistic reviewer.
    *   *Why T-12 second:* Both T-14 and T-12 require modifying `skills/gemini-cli/references/roles/reviewer.md`. Doing T-14 (schema additions at the bottom of the file) followed by T-12 (modifying the inline color standards table) prevents mental context switching and git merge conflicts on the reviewer file.

**Recommendation:** Execute T-11 independently. Execute T-14 and T-12 as a single stacked PR/commit sequence focused on the prompt-layer upgrade.
