# Audit: Gemini Prototype — Wave 1 (T-11, T-12, T-14)

**Auditor**: Codex (cross-review, executed by lead due to CLI unavailability)
**Date**: 2026-03-23
**Prototype Source**: Gemini-core

---

## Change-by-Change Verdicts

### Change 1: Add atomic write protocol for slide-status.json (T-11)
**File**: commands/ppt.md
**Verdict**: suggestion

The protocol is correct: write to `.tmp.json`, validate, `mv` rename. The `jq` dependency concern raised by Codex analysis is valid — `jq` is not a guaranteed dependency in all environments. However, since ppt.md instructions are executed by an LLM agent (not a CI script), the agent can fallback to `python3 -c "import json; json.load(open(...))"` if `jq` is unavailable. This is a minor portability issue, not a blocker.

The "race condition" concern from Gemini audit of the Codex prototype applies equally here but is **not a real blocker**: the lead orchestrator is a single-threaded process that updates `slide-status.json` sequentially after each agent completion signal. There is no concurrent writer scenario — parallel slide-core agents do not write to this file directly.

**Suggestion**: Replace `jq -e .` with `python3` validation for portability, or document `jq` as an optional runtime dependency with python3 fallback.

### Change 2: Replace blanket color rule with 3-zone model (T-12)
**File**: agents/slide-core.md
**Verdict**: approve

Excellent replacement. The 3-zone model is clearly defined:
- Zone 1 (Mandatory Core) with semantic token enforcement
- Zone 2 (Chart) with `chart_colors` array
- Zone 3 (Decorative Free) with `data-decorative="true"` or `<defs>` scope
- Parent `<g>` wrapping for complex decorative groups

Consistent with task requirements. No issues.

### Change 3: Update style tokens review criteria to 3-zone model (T-12)
**File**: skills/gemini-cli/references/roles/reviewer.md
**Verdict**: approve

Clean split of the single "Style tokens" row into 3 severity-appropriate rows. Core=Major, Chart=Minor, Decorative=Pass. This correctly implements guided-freedom where decorative colors are exempt from violations.

Cross-file consistency with Change 2: Zone definitions match exactly.

### Change 4: Add visual_weight field to page schema (T-14)
**File**: skills/_shared/references/prompts/outline-architect.md
**Verdict**: approve

Minimal, correct schema addition. The field is placed adjacent to `layout_hint` which is the natural location. Inline documentation of the 3 values (low/medium/high) is sufficient.

### Change 5: Add visual weight distribution guidelines (T-14)
**File**: skills/_shared/references/prompts/outline-architect.md
**Verdict**: approve

Good practical guideline: "Avoid 3+ consecutive high-weight slides without a breathing slide." The rhythm pattern suggestion (high-medium-low-medium-high) gives the LLM a concrete target. Cover and end pages noted as inherently low weight — correct.

### Change 6: Expand Holistic Deck Review with 5-dimension framework (T-14)
**File**: skills/gemini-cli/references/roles/reviewer.md
**Verdict**: approve

This is the strongest change in the Gemini prototype. Key strengths:
1. **Quantitative triggers** for each dimension (e.g., "3+ consecutive same layout", ">60% accent usage")
2. **Explicit scoring table** with per-dimension scores — solves the "unscorable formula" blocker identified in the Codex prototype audit
3. **Deck size adaptation** rules for short decks (<10 slides, <5 slides)
4. **Legacy fallback** for `visual_weight` (infer from page type)
5. **Decorative exemption** in Color Story dimension — consistent with T-12 zone model

One minor note: weights sum to 100% (25+20+20+20+15=100) ✓

---

## Cross-File Consistency

| Token/Concept | slide-core.md (Ch.2) | reviewer.md (Ch.3+6) | outline-architect.md (Ch.4+5) |
|---|---|---|---|
| `data-decorative="true"` | Zone 3 definition | Zone 3 row + Color Story exemption | N/A |
| `chart_colors` | Zone 2 definition | Zone 2 row (Minor) | N/A |
| `visual_weight` enum | N/A | Holistic dims 1,3,5 | Schema + guidelines |
| Legacy fallback | N/A | Infer from page type | N/A |
| `<defs>` scope | Zone 3 definition | Zone 3 row | N/A |

All cross-references are consistent. ✓

---

## Blockers

None.

## Suggestions

1. **T-11**: Replace `jq` validation with `python3` for portability (or add jq-with-python3-fallback pattern).

## Test Gaps

1. No automated check script for Color Zone Compliance (Change 2 defines zones but the corresponding Change 3 only updates the reviewer table — the Codex prototype's Change 4 adds a validation Check #5 which is more complete).

---

## Overall Verdict

**Verdict**: approve (with suggestions)

The Gemini prototype is well-structured and complete. All 6 changes are internally consistent and cross-file references match. The holistic review expansion (Change 6) is particularly strong with its explicit scoring table and quantitative triggers. The only suggestion is a minor portability improvement for T-11's JSON validation.

Compared to Codex prototype: Gemini's holistic review (Change 6) is superior due to the explicit scoring table. Codex's Color Zone validation Check #5 (Change 4) is stronger. Recommend merging both approaches in finalization.
