# Git Conventions

## Observed Commit Style

Recent history shows a conventional-prefix pattern such as:

- `docs: ...`
- `feat: ...`
- `fix(readme): ...`
- `refactor(openspec): ...`

Use concise prefixes that describe the dominant intent of the change.

## Documentation Changes

Use a `docs:`-style subject when the change is primarily documentation, including:

- `README.md`
- `CLAUDE.md`
- `llmdoc/`
- other explanatory or process-oriented markdown

If code and docs change together, choose the prefix that best represents the primary behavioral change.

## Safe Collaboration Expectations

- Do not assume generated artifacts in `openspec/changes/` are disposable unless the change explicitly targets them.
- When editing documentation, preserve the file names and artifact terms used by the implementation contract.
- When a contract changes, update the closest source-of-truth document first, then sync dependent docs.

## Suggested Documentation Sync Order

1. Update command or agent contract files if behavior changed.
2. Update `llmdoc/` to explain the new maintainer-facing model.
3. Update `README.md` only if user-facing behavior or onboarding changed.
4. Update `CHANGELOG.md` when the repo's release narrative should mention the change.

## Review Checklist For Doc Commits

- Do file paths still exist?
- Do artifact names match the implementation exactly?
- Do phase numbers and hard-stop points still match `commands/ppt.md`?
- Do agent responsibilities still match `agents/*.md`?
- Do style and review rules still match `skills/_shared/` and `skills/gemini-cli/`?
