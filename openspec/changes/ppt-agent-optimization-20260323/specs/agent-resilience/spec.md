# Capability: Agent Resilience

> Resource budget, resume safety, and state hardening for PPT Agent.

## MODIFIED Requirements

### Requirement: Agent turn budgets match actual workload

maxTurns for each agent MUST be calibrated to observed workload. The system SHALL NOT over- or under-allocate turn budgets.

#### Scenario: content-core handles 15-slide deck without truncation

- **Given** a presentation request with 15 slides
- **When** content-core generates outline and drafts with maxTurns=35
- **Then** all 15 slides are planned and drafted without truncation
- **And** draft signals are batched every 3 slides (not per-slide)

#### Scenario: slide-core operates within reduced budget

- **Given** a single slide design task
- **When** slide-core operates with maxTurns=20
- **Then** the slide is designed within budget (typical: 12-15 turns)

#### Scenario: review-core has adequate budget for holistic mode

- **Given** a 12-slide deck entering holistic review
- **When** review-core operates with maxTurns=20
- **Then** all slide SVGs are read and reviewed without turn exhaustion

### Requirement: Resume logic respects outline approval

Resume detection MUST NOT skip the Phase 4 Hard Stop when the outline was never approved. The system SHALL check the `approved` field before bypassing Phase 4.

#### Scenario: Resume with approved outline

- **Given** outline.json exists with `"approved": true`
- **When** a resumed run detects existing outline
- **Then** Phase 4 is skipped and execution continues to Phase 5

#### Scenario: Resume with unapproved outline

- **Given** outline.json exists with `"approved": false` or the field is missing
- **When** a resumed run detects existing outline
- **Then** Phase 4 Hard Stop is triggered for user approval
- **And** the user must explicitly approve before proceeding

## ADDED Requirements

### Requirement: Crash-safe slide status persistence

slide-status.json MUST survive mid-write crashes without data loss. The system SHALL use atomic write (tmp + rename) pattern.

#### Scenario: Crash during slide-status.json write

- **Given** slide-status.json contains progress for slides 1-8
- **When** a write for slide 9 crashes mid-operation
- **Then** slide-status.json still contains valid JSON with slides 1-8 progress
- **And** the interrupted slide 9 is retried on resume

### Requirement: review-core has Bash tool for pre-review checks

review-core MUST have Bash in its tools list to execute automated SVG validation.

#### Scenario: Pre-review checks are executable

- **Given** review-core is spawned with Bash in its tools array
- **When** a slide SVG enters the review pipeline
- **Then** all 5 pre-review automated checks can execute (xmllint, viewBox, font-size, color compliance, safe area)
