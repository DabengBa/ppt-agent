# PPT Agent Documentation Index

`llmdoc/` is the project-oriented documentation hub for `ppt-agent`.

## Overview

- `llmdoc/overview/project-overview.md` - project purpose, repository layout, runtime outputs, and documentation boundaries.

## Architecture

- `llmdoc/architecture/ppt-workflow.md` - the seven-phase PPT generation workflow, hard stops, resume points, and artifacts.
- `llmdoc/architecture/agent-collaboration.md` - responsibilities and handoffs across `research-core`, `content-core`, `slide-core`, and `review-core`.

## Guides

- `llmdoc/guides/running-ppt-workflow.md` - how to invoke `/ppt-agent:ppt`, how runs are resumed, and what output to expect.
- `llmdoc/guides/updating-styles-and-review.md` - how style tokens, Bento Grid rules, and Gemini review fit together.
- `llmdoc/guides/research-and-material-collection.md` - how requirement research and material collection are executed and extended.

## Reference

- `llmdoc/reference/coding-conventions.md` - stable repository conventions inferred from command specs, agent contracts, and shared resources.
- `llmdoc/reference/git-conventions.md` - commit message patterns, document maintenance expectations, and safe collaboration notes.

## Source Of Truth

This documentation is derived from the current implementation contracts in:

- `commands/ppt.md`
- `agents/research-core.md`
- `agents/content-core.md`
- `agents/slide-core.md`
- `agents/review-core.md`
- `skills/_shared/index.json`
- `skills/_shared/references/prompts/bento-grid-layout.md`
- `skills/_shared/references/prompts/svg-generator.md`
- `skills/gemini-cli/references/roles/reviewer.md`
- `README.md`
- `CLAUDE.md`
