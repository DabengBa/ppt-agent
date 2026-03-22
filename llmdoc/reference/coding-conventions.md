# Coding Conventions

## Source Priority

For this repository, behavior contracts are defined in a layered way:

1. `commands/*.md` define orchestration and runtime artifacts.
2. `agents/*.md` define role-level execution and communication contracts.
3. `skills/*/SKILL.md` define reusable capability contracts.
4. `skills/_shared/` contains reusable prompt, style, and asset references.

When two documents overlap, prefer the more specific implementation contract.

## Stable Repository Patterns

- Agent definitions use YAML frontmatter followed by sections for Purpose, Inputs, Outputs, Execution, Communication, and Verification.
- Shared resources are discovered through `skills/_shared/index.json` instead of scattered implicit references.
- Runtime artifacts are written under `openspec/changes/<run_id>/`.
- Generated files are treated as explicit workflow checkpoints, not incidental byproducts.

## Naming Patterns

- slide files use two-digit numbering: `slide-{nn}.svg`
- review files use the same numbering: `review-{nn}.md`
- manifests describe sets of generated outputs, for example `draft-manifest.json` and `review-manifest.json`
- progress state is tracked in `slide-status.json`

## Documentation Conventions

- Public-facing usage stays in `README.md`.
- Host-specific operating notes stay in `CLAUDE.md`.
- Maintainer-oriented system docs belong in `llmdoc/`.
- Shared prompts and style rules are referenced by path rather than duplicated into multiple docs.

## Design-System Conventions

- SVG slides are fixed to `viewBox="0 0 1280 720"`.
- Safe-area and minimum-gap constraints are part of the design contract, not just visual suggestions.
- Color values should come from style YAML or merged brand-style output rather than ad hoc literals.
- CJK text handling is a first-class requirement in the SVG generator rules.

## Update Rule Of Thumb

If a change modifies one of the following, update `llmdoc/` alongside code or command changes:

- workflow phases,
- artifact names or checkpoint semantics,
- agent responsibilities,
- style token schema,
- review pass/fail logic,
- resume behavior.
