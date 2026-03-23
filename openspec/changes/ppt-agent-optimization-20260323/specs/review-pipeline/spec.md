# Capability: Review Pipeline

> Aesthetic optimization layer for PPT Agent Phase 6.

## MODIFIED Requirements

### Requirement: Gemini acts as aesthetic optimizer, not compliance scorer

Gemini's role in the review pipeline MUST be reframed from "score and check compliance" to "proactively propose concrete visual improvements". Output format SHALL lead with optimization suggestions; score is a secondary pass/fail gate.

#### Scenario: Gemini available — full aesthetic optimization

- **Given** a generated SVG slide and the active style tokens
- **When** review-core invokes Gemini via gemini-cli
- **Then** Gemini returns typed optimization suggestions (each with `suggestion_type` from: `attribute_change`, `layout_restructure`, `full_rethink`, `content_reduction`, `deck_coordination`)
- **And** each suggestion includes a `layout_suggestion` description when type is `layout_restructure`, `content_reduction`, or `deck_coordination`
- **And** an overall score >= 7 indicates pass (no fix needed), < 7 triggers fix loop

#### Scenario: Gemini unavailable — technical validation only

- **Given** a generated SVG slide and Gemini is not reachable
- **When** review-core falls back to Claude self-review
- **Then** the output is labeled "Technical Validation Only — aesthetic optimization skipped"
- **And** only programmatic checks are performed: XML validity, viewBox 1280x720, font-size >= 14px, safe area compliance, color token usage, text overflow estimation, outline content coverage, WCAG AA contrast
- **And** no `overall_score` or aesthetic suggestions are produced
- **And** only `attribute_change` type fixes are emitted for hard constraint violations

#### Scenario: Pre-review automated checks execute via Bash

- **Given** review-core has the Bash tool in its tools list
- **When** a slide SVG enters review
- **Then** 5 pre-review checks execute: xmllint validation, viewBox verification, font-size minimum, color compliance, safe area boundaries
- **And** failures are reported before LLM review begins

### Requirement: Suggestion-driven fix strategy replaces score-driven routing

The Phase 6 fix loop MUST route by optimization suggestion type, not score bands. The system SHALL use suggestion-driven routing as the primary fix strategy.

#### Scenario: attribute_change suggestion

- **Given** Gemini returns a suggestion with `suggestion_type: "attribute_change"`
- **When** slide-core processes the fix
- **Then** a deterministic attribute patch is applied (modify specific SVG attributes)
- **And** the slide is re-reviewed

#### Scenario: layout_restructure suggestion

- **Given** Gemini returns a suggestion with `suggestion_type: "layout_restructure"` and a `layout_suggestion` description
- **When** slide-core processes the fix
- **Then** the slide is regenerated with the layout constraint from the suggestion
- **And** original content is preserved

#### Scenario: full_rethink suggestion

- **Given** Gemini returns a suggestion with `suggestion_type: "full_rethink"`
- **When** slide-core processes the fix
- **Then** the slide is regenerated from scratch using the outline spec
- **And** maximum 1 full_rethink per slide per review cycle

#### Scenario: Mixed suggestion types with priority cascade

- **Given** Gemini returns multiple suggestions of different types for one slide
- **When** slide-core selects execution strategy
- **Then** the highest-priority type determines the strategy: `full_rethink` > `layout_restructure` > `content_reduction` > `attribute_change`

### Requirement: 5-type suggestion taxonomy

All optimization suggestions MUST be classified into exactly one of 5 types. The taxonomy SHALL be validated via calibration run.

#### Scenario: Taxonomy completeness validation

- **Given** a calibration production run (8-10 slides) with Gemini available
- **When** all Gemini suggestions are collected
- **Then** >= 80% of suggestions map to one of the 5 types without ambiguity
- **And** if coverage < 80%, the taxonomy must be adjusted before Wave 3

## ADDED Requirements

### Requirement: Holistic deck aesthetic coherence review

After all individual slide reviews complete, Gemini MUST perform a cross-slide coherence assessment. The system SHALL route deck_coordination suggestions to affected slides.

#### Scenario: Holistic review produces deck_coordination suggestions

- **Given** all slide SVGs have passed individual review
- **When** Gemini performs holistic deck review
- **Then** assessment covers 5 dimensions: visual rhythm, color story, layout variety, style consistency, pacing
- **And** any cross-slide issues emit `deck_coordination` type suggestions targeting specific slides
- **And** the orchestrator routes these suggestions to the affected slides for correction
