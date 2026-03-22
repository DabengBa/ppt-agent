# Agent Collaboration

## Core Agents

The system is built around four agent contracts under `agents/`:

- `research-core` - requirement research and material collection
- `content-core` - outline authoring and planning draft generation
- `slide-core` - final SVG design generation
- `review-core` - layout and aesthetic optimization plus quality scoring

## Responsibility Boundaries

### research-core

`research-core` owns internet-facing evidence gathering.

It probes tool availability through `skills/agent-reach/scripts/probe.sh`, chooses the best available search path, degrades gracefully when tools are missing, and writes either `research-context.md` or isolated collection files.

It should not append directly to a shared `materials.md` file.

### content-core

`content-core` owns structure.

It translates user requirements and gathered materials into:

- a strict `outline.json` schema,
- a human-reviewable `outline-preview.md`,
- simple planning draft SVGs.

It preserves unchanged structure on revise operations.

### slide-core

`slide-core` owns design realization.

It consumes the approved structure plus style tokens and outputs final `slides/slide-{nn}.svg` files. It is also responsible for low-cost deterministic validation before telling the lead a slide is ready.

### review-core

`review-core` owns optimization and gating, not generation.

It must read full SVG source, include style tokens in the review prompt, preserve Gemini raw output, and emit structured fix JSON that `slide-core` can apply deterministically.

## Handoff Model

The normal handoff chain is:

`research-core` -> `content-core` -> `slide-core` -> `review-core` -> lead delivery logic

More concretely:

1. `research-core` produces context and source material.
2. `content-core` converts that material into structured narrative and draft layout intent.
3. `slide-core` turns draft intent into polished SVG cards.
4. `review-core` scores, critiques, and either passes the slide or returns deterministic fixes.
5. The lead aggregates slide outcomes and performs deck delivery.

## Communication Expectations

Agent docs consistently require:

- heartbeat messages during long-running work,
- explicit ready/error messages,
- acknowledgment of directed messages with `requires_ack=true`,
- file-based outputs that the lead can verify.

This makes the file system the durable truth and messages the transient coordination layer.

## Why The Split Matters

The architecture deliberately separates:

- evidence gathering from narrative shaping,
- narrative shaping from visual realization,
- visual realization from quality judgment.

That separation gives the workflow bounded retries and clearer failure ownership. A bad review does not require regenerating requirements; a research gap does not need SVG fixes.
