# Project Overview

## What This Project Does

`ppt-agent` is a multi-agent plugin that turns a topic prompt into a complete SVG slide deck.

The main workflow combines:

- requirement research and material collection,
- outline authoring with Pyramid Principle structure,
- planning draft SVG generation,
- final Bento Grid slide design,
- Gemini-assisted review and quality gating,
- final delivery as SVG files, HTML preview, and speaker notes.

The top-level product description in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` matches the implementation contracts under `commands/` and `agents/`.

## Main Entry Points

- `commands/ppt.md` defines the `/ppt-agent:ppt` command and the full seven-phase orchestration contract.
- `CLAUDE.md` describes the plugin-facing workflow summary, available command, and output expectations.
- `README.md` is the public-facing entry point for installation, usage, showcase assets, and high-level workflow explanation.

## Repository Layout

- `.claude-plugin/` - plugin metadata used by the host environment.
- `commands/` - command-level orchestration specs.
- `agents/` - role contracts for the four core agents.
- `skills/` - reusable skills and shared references used by the agents.
- `openspec/` - run artifacts and deeper analysis material.
- `docs/images/` - showcase outputs referenced by the README.
- `llmdoc/` - project-maintained internal documentation.

## Core Runtime Model

Each PPT run writes to `openspec/changes/<run_id>/`.

Important artifacts include:

- early-phase planning files such as `input.md`, `proposal.md`, `tasks.md`, `requirements.md`, and `materials.md`,
- structural outputs such as `outline.json` and `outline-preview.md`,
- generation outputs such as `drafts/slide-{nn}.svg` and `slides/slide-{nn}.svg`,
- review checkpoints such as `slide-status.json`, `reviews/review-{nn}.md`, `reviews/review-holistic.md`, and `review-manifest.json`,
- delivery outputs such as `output/index.html` and `output/speaker-notes.md`.

## Documentation Scope

This `llmdoc/` tree is intended to answer four recurring questions:

1. What are the stable workflow contracts?
2. Which files are the source of truth for each subsystem?
3. How do the agents and skills hand work off between phases?
4. What should a maintainer update when behavior changes?

## Known Documentation Boundaries

- `README.md` remains the public product overview and usage page.
- `CLAUDE.md` remains the host-specific operational memory entry.
- `llmdoc/` focuses on maintainers who need implementation-aware documentation rather than user marketing copy.
