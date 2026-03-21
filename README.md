# PPT Agent

Multi-agent PPT slide generation workflow for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

Generate presentation slides (SVG 1280×720 Bento Grid layout) powered by Claude + Gemini review.

## Install

```bash
claude plugin add github:zengwenliang416/ppt-agent
```

## Usage

```
/ppt-agent:ppt <topic or requirement>
```

## Workflow

1. **Init** — Parse arguments, create run directory
2. **Requirement Research** — Background search + user clarification
3. **Material Collection** — Per-section deep search (parallel)
4. **Outline Planning** — Pyramid Principle outline + user approval
5. **Planning Draft** — Simple SVG drafts per slide
6. **Design Draft + Review** — Bento Grid SVG generation + Gemini quality review loop
7. **Delivery** — Final SVGs + interactive HTML preview

## Agents

| Agent | Role |
|-------|------|
| `research-core` | Requirement research + material collection |
| `content-core` | Outline planning + planning draft |
| `slide-core` | Design SVG generation (Bento Grid) |
| `review-core` | Gemini-powered SVG quality review |

## Output

```
openspec/changes/<run_id>/
├── research-context.md
├── requirements.md
├── materials.md
├── outline.json
├── drafts/slide-{nn}.svg
├── slides/slide-{nn}.svg
├── reviews/review-{nn}.md
└── output/
    ├── slide-{nn}.svg      # Final SVGs
    └── index.html           # Interactive preview
```

## License

MIT
