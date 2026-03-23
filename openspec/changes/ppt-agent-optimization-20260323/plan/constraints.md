# Constraints — PPT Agent Optimization

> Consolidated from: handoff.json (C1-C8), requirements.md (NFR-01 to NFR-06),
> architecture decisions, and resolved unresolved decisions.
> Date: 2026-03-23

---

## Structural Constraints (from handoff.json)

| ID | Constraint | Source |
|----|-----------|--------|
| C1 | 4-agent architecture is validated — do not decompose or merge agents (research-core, content-core, slide-core, review-core) | handoff.json, NFR-02 |
| C2 | Star topology — agents communicate only with lead orchestrator via SendMessage, no agent-to-agent communication | handoff.json, NFR-03 |
| C3 | File-based state machine is the right resume pattern — harden it (atomic writes, approval markers), do not replace it | handoff.json, NFR-04 |
| C4 | Gemini's role is aesthetic optimizer — all review prompts must reflect this, not compliance checker framing | handoff.json |
| C5 | Claude self-review CANNOT substitute Gemini's aesthetic perspective — fallback must honestly degrade to technical validation only | handoff.json, NFR-05 |
| C6 | Graceful degradation pattern preserved: Gemini available -> full aesthetic optimization; unavailable -> technical validation only (no fake aesthetic review) | handoff.json, NFR-05 |
| C7 | Pipeline overlap (Phase 5 to 6) is architecturally sound — simplify signaling but keep the pipeline | handoff.json, NFR-06 |
| C8 | All changes must be backward-compatible with existing run directories | handoff.json, NFR-01 |

---

## Non-Functional Requirements

| ID | Requirement | Verification |
|----|------------|-------------|
| NFR-01 | Backward compatibility with existing run directories | New fields have safe defaults when absent |
| NFR-02 | 4-agent architecture preserved | No new agents added, no agents merged |
| NFR-03 | Star topology preserved | No SendMessage calls between agents |
| NFR-04 | File-based state machine preserved | Artifact presence remains durable truth layer |
| NFR-05 | Graceful degradation preserved | Fallback mode produces technical validation only |
| NFR-06 | Pipeline overlap preserved | Phase 5->6 batched signaling maintains pipeline |

---

## Architecture-Derived Constraints

| ID | Constraint | Source AD |
|----|-----------|----------|
| AC-01 | review-core MUST have Bash in tools array for technical validation to function | AD-01 (prerequisite for AD-06, AD-08) |
| AC-02 | Optimizer role (FR-07) and suggestion taxonomy (FR-09) MUST ship atomically — format mismatch between producer (reviewer.md) and consumer (slide-core) if shipped separately | AD-06, AD-07 |
| AC-03 | Suggestion-driven fix strategy (FR-13) MUST NOT ship before calibration gate validates the 5-type taxonomy against real Gemini outputs | AD-12, UD-3 |
| AC-04 | Fallback mode MUST NOT produce `overall_score`, per-criterion aesthetic scores, or optimization suggestions — prevents downstream from treating technical-only as aesthetic pass | AD-08 |
| AC-05 | All fix suggestions in fallback mode MUST be `suggestion_type: "attribute_change"` — technical fixes are always deterministic patches | AD-08 |
| AC-06 | `deck_coordination` suggestions are NEVER processed in per-slide fix loop — always deferred to orchestrator holistic pass | AD-07, AD-13 |
| AC-07 | Fix priority cascade: `full_rethink` > `layout_restructure` > `content_reduction` > `attribute_change` — if full_rethink present, skip all lower types | AD-12 |
| AC-08 | Max 2 fix rounds per slide — after round 2, accept with warning regardless of remaining suggestions | AD-12 |
| AC-09 | `approved` field in outline.json is set ONLY by orchestrator after user confirmation, NEVER by content-core | AD-05 |
| AC-10 | slide-status.json writes MUST use tmp+rename atomic pattern | AD-10 |
| AC-11 | Mandatory-zone colors (primary, secondary, accent, background, text, card_bg) MUST match style YAML exactly — Major severity for deviations | AD-11 |
| AC-12 | Chart elements MUST use `chart_colors[n]` from style YAML, not arbitrary colors | AD-09, AD-11 |

---

## Resolved Unresolved Decisions (now constraints)

### UD-1 Resolution: Agent infra model override -> Two agent variants

**Decision**: Create `slide-core-patch.md` (sonnet) for `attribute_change` fixes alongside `slide-core.md` (opus) for design + structural fixes.
**Constraint**: Until Wave 4 implementation, all slide-core invocations use opus. The patch variant is created only when FR-17 is implemented.
**Fallback**: If Task() model override is confirmed supported, use single agent with runtime override instead of two files.
**Source**: AD-14

### UD-2 Resolution: Technical validation inlined in review-core (option b)

**Decision**: Validation checks stay in review-core prompt, executed via Bash. No separate script, no orchestrator pre-step.
**Constraint**: Technical validation logic lives exclusively in review-core.md. The orchestrator (ppt.md) MUST NOT duplicate or pre-execute these checks. This maintains the 4-agent boundary (C1) and star topology separation of concerns (C2).
**Source**: AD-08

### UD-3 Resolution: Validate taxonomy via calibration gate

**Decision**: The 5-type suggestion taxonomy is shipped in Wave 2 as a design hypothesis. Wave 2 calibration production run (8-10 slides) validates coverage.
**Constraint**: Wave 3 FR-13 implementation MUST NOT proceed until calibration confirms the taxonomy covers >= 80% of actual Gemini suggestions. If taxonomy needs adjustment, update reviewer.md and slide-core.md before FR-13.
**Expected outcomes**:
- `attribute_change` + `layout_restructure` cover 80%+ of suggestions
- `full_rethink` may be rare (Gemini tends toward incremental improvement)
- `content_reduction` may merge with `layout_restructure` if Gemini frames density as layout
- `deck_coordination` only in holistic mode
**Source**: AD-07, AD-12

---

## Calibration Gate Requirements

The calibration gate between Wave 2 and Wave 3 is a mandatory checkpoint:

| Check | Pass Criteria | Fail Action |
|-------|-------------|-------------|
| Gemini produces typed optimization suggestions | >= 80% of suggestions include valid `suggestion_type` | Adjust reviewer.md prompt guidance |
| 5-type taxonomy coverage | >= 80% of suggestions map to existing types | Expand or collapse taxonomy types |
| `layout_suggestion` descriptions are actionable | slide-core can interpret >= 70% without clarification | Add examples to reviewer.md |
| Technical validation catches real issues | All Critical checks produce correct PASS/FAIL | Fix check implementations |
| Signal batching works in pipeline | No dropped slides, no duplicate processing | Fix orchestrator batch handling |
