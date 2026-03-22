# PPT Workflow Architecture

## Summary

The authoritative orchestration contract lives in `commands/ppt.md`.

The workflow has seven ordered phases:

1. Init
2. Requirement Research
3. Material Collection
4. Outline Planning
5. Planning Draft
6. Design Draft + Gemini Review
7. Delivery

Three phases are explicit hard stops that require user interaction or delivery confirmation semantics:

- Phase 2 requirement confirmation
- Phase 4 outline approval
- Phase 7 delivery

## Phase Breakdown

### 1. Init

The lead command parses `--style`, `--brand-colors`, `--pages`, and `--run-id`, resolves the run directory, writes the OpenSpec scaffold, and stores the raw input.

Important details:

- available styles are discovered from `skills/_shared/index.json` instead of being hardcoded,
- brand overrides are merged into a generated `${RUN_DIR}/brand-style.yaml`,
- `proposal.md` and `tasks.md` are mandatory scaffold files.

### 2. Requirement Research

`research-core` runs in `mode=research` and writes `${RUN_DIR}/research-context.md`.

The lead must then ask the user about:

- target audience,
- presentation purpose,
- key messages,
- tone,
- any constraints.

The combined result becomes `${RUN_DIR}/requirements.md`.

### 3. Material Collection

The lead derives section topics from `requirements.md` and launches parallel `research-core` collection tasks. Each task writes to an isolated `materials-*.md` file. The lead serially merges these files into `${RUN_DIR}/materials.md`.

This isolation is a deliberate race-condition avoidance strategy.

### 4. Outline Planning

`content-core` in `mode=outline` reads `requirements.md` and `materials.md`, then produces:

- `${RUN_DIR}/outline.json`
- `${RUN_DIR}/outline-preview.md`

If the user requests adjustments, `content-core` runs in `mode=revise` and mutates the existing outline incrementally instead of regenerating it from scratch.

`outline.json` is a workflow pivot file because later phases consume it directly.

### 5. Planning Draft

`content-core` in `mode=draft` converts the approved outline into lightweight draft SVGs under `${RUN_DIR}/drafts/` and writes `${RUN_DIR}/draft-manifest.json`.

It emits per-slide readiness signals so Phase 6 can start before all draft slides finish.

### 6. Design Draft + Gemini Review

This phase pipelines `slide-core` and `review-core`.

- `slide-core` reads the outline, matching draft SVG, style YAML, Bento Grid rules, and SVG generation rules.
- `review-core` checks the generated SVG, attempts Gemini optimization first, and falls back to Claude self-review when Gemini is unavailable.
- `slide-status.json` is updated incrementally so `--run-id` can skip already accepted slides.
- `review-manifest.json` is built from `slide-status.json` plus holistic review output.

Quality rules here are not just advisory. They gate whether a slide passes directly, enters a bounded fix loop, or needs regeneration.

### 7. Delivery

The lead reads `review-manifest.json`, copies final SVGs into `${RUN_DIR}/output/`, builds the HTML preview from `skills/_shared/assets/preview-template.html`, extracts notes into `speaker-notes.md`, and prints the final quality summary.

## Resume Model

`--run-id` resumes work based on the deepest existing artifact:

- `slide-status.json` -> resume Phase 6 from the first incomplete slide,
- `draft-manifest.json` only -> resume at Phase 6 start,
- `outline.json` only -> resume at Phase 5,
- `materials.md` only -> resume at Phase 4,
- `requirements.md` only -> resume at Phase 3,
- `research-context.md` only -> resume at Phase 2,
- no artifacts -> start from Phase 1.

This means artifact presence is part of the runtime state machine.

## Architectural Pressure Points

- `outline.json` is the central contract between content planning and downstream rendering.
- `slide-status.json` is the central contract for incremental progress and resume safety.
- `review-manifest.json` is the quality-gate handoff into delivery.
- `brand-style.yaml` is the bridge between user-provided brand colors and the style token system.
