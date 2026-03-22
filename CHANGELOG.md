# Changelog

## [Unreleased]

### Added
- **agent-reach skill**: Self-contained multi-platform search & read skill (14+ platforms). Zero external dependencies — uses upstream CLI tools (curl+Jina, gh, yt-dlp, xreach, mcporter) directly with tier-based graceful degradation. Includes `probe.sh` for runtime tool detection.
- **MIT LICENSE** for agent-reach skill (derived from [Agent Reach](https://github.com/Panniantong/Agent-Reach) by Agent Eyes).

### Changed
- **Gemini role redefined**: From "quality reviewer" to "layout & aesthetic optimizer". Gemini now proposes concrete visual improvements, not just compliance checks.
- **Gemini intermediate artifacts preserved**: Raw Gemini outputs (`gemini-raw-*.md`) are kept in `${RUN_DIR}/reviews/` for traceability and debugging.
- **research-core agent**: Replaced `agent-reach` CLI dependency with probe-first flow — detects available tools at runtime and selects the best search method per platform.
