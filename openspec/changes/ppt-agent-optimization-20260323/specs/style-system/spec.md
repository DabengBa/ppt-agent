# Capability: Style System

> Multi-series chart colors, style palette expansion, guided-freedom enforcement, and SVG pattern enrichment.

## ADDED Requirements

### Requirement: Expand style palette from 4 to 17

The style system MUST be expanded from 4 built-in styles to 17 by adding 13 new style YAMLs. New styles SHALL be aligned with the visual-content slide-generator style system and registered in index.json for automatic discovery.

#### Scenario: User selects a new style by name

- **Given** a user invokes PPT generation with `--style=chalkboard`
- **When** the orchestrator reads index.json for available styles
- **Then** `chalkboard.yaml` is discovered and loaded as the active style
- **And** all downstream agents (content-core, slide-core, review-core) use the chalkboard design tokens

#### Scenario: All 17 styles are registered and discoverable

- **Given** 17 style YAML files exist in `skills/_shared/references/styles/`
- **When** index.json is read with filter `domain == "style"`
- **Then** exactly 17 entries are returned, each with unique id, keywords, and use_cases
- **And** each YAML follows the standard schema (name, mood, color_scheme, typography, card_style, gradients, elevation, decoration, slide_type_overrides)

#### Scenario: New styles include chart_colors

- **Given** a new style YAML (e.g., blueprint.yaml) is created
- **When** chart_colors token is defined (per FR-10)
- **Then** the style includes a chart_colors array of 6-8 hex values
- **And** chart_colors[0] equals the style's accent color

### Requirement: chart_colors token for multi-series data visualization

Each style YAML MUST provide an ordered array of 6-8 hex colors for chart data series. The first color SHALL equal the accent color.

#### Scenario: Multi-series bar chart uses distinct colors

- **Given** a slide with a grouped bar chart showing 3 data series
- **When** slide-core generates the SVG using the active style
- **Then** each series uses a different color from chart_colors (series 1 = chart_colors[0], series 2 = chart_colors[1], etc.)
- **And** chart_colors[0] equals the style's accent color for single-series backward compatibility

#### Scenario: Style YAML without chart_colors (backward compat)

- **Given** a style YAML that predates the chart_colors addition
- **When** svg-generator encounters a chart pattern
- **Then** it falls back to using accent color for all series (current behavior)

### Requirement: Guided-freedom color enforcement model

Style token enforcement MUST use a 3-zone model: mandatory core, chart colors, and decorative free zone. Decorative elements SHALL declare themselves via `data-decorative` attribute.

#### Scenario: Core colors are mandatory

- **Given** a slide SVG using a style with defined background, text, and accent colors
- **When** the slide is reviewed for color compliance
- **Then** background, primary text, and accent colors must match style tokens exactly
- **And** violations are reported as `attribute_change` fix suggestions

#### Scenario: Decorative colors are free but declared

- **Given** a slide SVG with decorative elements (grid patterns, glows, gradients)
- **When** those elements use colors not in the style tokens
- **Then** decorative elements must carry `data-decorative="true"` attribute
- **And** free-zone colors are not flagged as style violations

## MODIFIED Requirements

### Requirement: SVG generator supports 5 additional chart patterns

svg-generator.md MUST include patterns for table, metric card grid, grouped bar, line chart with axes, and network diagram. All chart patterns SHALL use chart_colors for data series.

#### Scenario: Table pattern renders structured data

- **Given** slide content includes a data table (3+ columns, 4+ rows)
- **When** slide-core selects the table SVG pattern
- **Then** the rendered table uses alternating row colors, header styling from style tokens, and chart_colors for any highlighted cells

#### Scenario: Grouped bar chart renders multi-series comparison

- **Given** slide content includes a comparison of 2-4 data series across categories
- **When** slide-core selects the grouped bar pattern
- **Then** each series uses a distinct chart_colors entry
- **And** axes, labels, and legend are rendered with proper spacing
