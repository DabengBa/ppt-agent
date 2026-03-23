# Audit: Codex Prototype -- Wave 1 (T-11, T-12, T-14)

**Auditor**: Gemini (cross-review)
**Date**: 2026-03-23
**Prototype Source**: Codex-core

---

## Blockers
- **Concurrent Write Data Loss (T-11, Change 2)**: The atomic `mv` prevents partial file corruption but does not solve the Read-Modify-Write race condition. Because Phase 6 executes slides in parallel, concurrent processes will read stale state, merge their updates, and overwrite each other's progress. Furthermore, the hardcoded `slide-status.tmp.json` filename will cause direct file collisions.
- **Unscorable Formula (T-14, Change 8)**: The `overall_coherence` formula requires numeric inputs for the 5 dimensions (e.g., `0.25*visual_rhythm`), but the prompt only instructs the LLM to "Flag" issues without assigning a 0-10 score to each dimension. The LLM will either hallucinate values or fail to compute the final score.

## Warnings
- **Missing Automation Script for Validation (T-12, Change 4)**: Validation Check #5 (Color Zone Compliance) is listed under "automated checks using the Bash tool" but provides no executable script or one-liner. The LLM will either fail or invent a brittle `grep` command on the fly.

## Test Gaps
- **Parallel Write Testing**: No test strategy is mentioned for verifying that atomic writes survive concurrent updates from multiple slide-generation threads.
- **Color Validation Tooling**: Tests are needed to ensure generated validation scripts correctly identify color zone violations without throwing false positives on `<linearGradient>` stops or `data-decorative` nested elements.

## Approved
- **T-11 (Change 1)**: The resume detection logic is robust, clears orphaned temp files, and correctly handles phase fallback cascades.
- **T-12 (Change 3, 5)**: The 3-zone color model is explicitly defined and elegantly integrates into the reviewer's hard rules table.
- **T-14 (Change 6, 7)**: The `visual_weight` schema addition is syntactically correct, and the fallback behavior for legacy files ensures backward compatibility.

---

## Change-by-Change Verdicts

### Change 1: Tighten `--run-id` resume detection with `.tmp.json` cleanup
**File**: commands/ppt.md
**Task**: T-11
**Verdict**: approve

The logic correctly clears orphaned temp files and introduces `python3` validation before trusting the resume state. The phase fallback cascade is complete and consistent with the pipeline design.

### Change 2: Upgrade incremental status write to atomic write protocol
**File**: commands/ppt.md
**Task**: T-11
**Verdict**: blocker

The python validation script safely removes the dependency on `jq`. However, Phase 6 runs concurrently. A standard read-modify-write cycle using a single hardcoded temp file (`slide-status.tmp.json`) introduces a race condition resulting in data loss.
**Fix**: Use a file lock (e.g., `flock`) around the read-modify-write block, or write individual slide statuses (e.g., `slide-status-01.json`) and aggregate them dynamically on resume.

### Change 3: Expand SVG Requirements to 3-zone color model
**File**: agents/slide-core.md
**Task**: T-12
**Verdict**: approve

The rules for the 3 zones are clearly defined and the `data-decorative="true"` exception is well-scoped to prevent systemic abuse.

### Change 4: Add Color Zone Compliance as validation check #5
**File**: agents/slide-core.md
**Task**: T-12
**Verdict**: suggestion

The validation step is semantically correct, but it is listed under "automated checks using the Bash tool" without providing a Bash/Python command.
**Fix**: Either provide a concrete Python script for Check #5, or move this check out of the "automated Bash checks" section and into a separate "LLM Visual Review" phase.

### Change 5: Replace Style tokens row with 3-zone color rules in reviewer hard rules table
**File**: skills/gemini-cli/references/roles/reviewer.md
**Task**: T-12
**Verdict**: approve

The hard rules table correctly maps the 3 zones to severity thresholds (Critical/Major/Minor) and is perfectly consistent with the `slide-core.md` definitions.

### Change 6: Add `visual_weight` field to outline.json page schema
**File**: skills/_shared/references/prompts/outline-architect.md
**Task**: T-14
**Verdict**: approve

The schema addition is structurally valid and appropriately placed.

### Change 7: Add Visual Weight Assignment rules and expand Page Type Definitions table
**File**: skills/_shared/references/prompts/outline-architect.md
**Task**: T-14
**Verdict**: approve

The documentation clearly explains `visual_weight` and provides sensible defaults. The instruction for handling legacy `outline.json` prevents breaking changes.

### Change 8: Upgrade Holistic Deck Review to weighted 5-dimension protocol with quantitative triggers
**File**: skills/gemini-cli/references/roles/reviewer.md
**Task**: T-14
**Verdict**: blocker

The formula `overall_coherence = 0.25*visual_rhythm + ...` cannot be computed because the prompt never instructs the LLM to score the individual dimensions.
**Fix**: Add an explicit instruction: "For each dimension, assign a score from 0-10 before applying the quantitative triggers to flag issues."

---

## Cross-File Consistency

- `data-decorative="true"` is consistently defined and referenced across both `slide-core.md` and `reviewer.md`.
- `chart_colors` is consistently restricted to Zone 2 in both files.
- The `visual_weight` enums (`low|medium|high`) correctly match between `outline-architect.md` and the holistic review triggers in `reviewer.md`.
- The legacy fallback (defaulting to `medium` weight) is properly documented and handled.
- Short deck relaxation thresholds (`<= 6` slides for narrative arc, `<= 5` slides for pacing) are practical, reasonable, and aligned.

---

## Overall Verdict

**Verdict**: blocked

**Summary**: The prototype correctly scopes the architectural intent of the 3 tasks, providing excellent schema updates, backward compatibility, and strong color boundary definitions. However, it introduces a critical data corruption risk during parallel atomic writes and a mathematical omission in the holistic review scoring formula that will cause pipeline failures.

**Blockers**:
- T-11: Concurrent read-modify-write using a static temp file will cause slide status data loss during Phase 6 parallel generation.
- T-14: The 5-dimension holistic review lacks instructions to generate 0-10 scores per dimension, breaking the weighted formula.

**Suggestions**:
- T-12: Validation Check #5 needs an explicit Python/Bash script if it is expected to be run as an automated tool, otherwise it should be reclassified as a semantic LLM check.
