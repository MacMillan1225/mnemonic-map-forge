# Mnemonic Map Forge JSON Data Schema

## Purpose

This file defines the JSON data consumed by `PYVIS_MEMORY_MAP_TEMPLATE.exe` / `PYVIS_MEMORY_MAP_TEMPLATE.py`.

The current renderer is **data-driven for graph content**, while some layout behavior still lives in the renderer. Use this file for field rules and validation details, not for UI design.

## Minimal Shape

```json
{
  "meta": {
    "title": "Example Map",
    "subtitle": "Optional subtitle"
  },
  "clusters": {
    "A. Example": {
      "color": "#e74c3c",
      "center": [0, 0],
      "nodes": [
        {
          "id": "node_a",
          "label": "A",
          "title": "A",
          "tooltip": "A\nMore hover detail",
          "nodeType": "tool"
        }
      ]
    }
  },
  "helpers": [
    {
      "id": "helper_x",
      "label": "◈ X",
      "title": "helper",
      "tooltip": "helper\nMore hover detail",
      "connects_to": ["node_a"],
      "position": [180, -40]
    }
  ],
  "edges": [
    {
      "from": "node_a",
      "to": "helper_x",
      "label": "memory link",
      "tooltip": "Why this memory link exists"
    }
  ],
  "sidebar": {
    "hints": ["Walk from A to X."],
    "sections": ["filter", "hints", "legend", "stats", "tips"]
  },
  "features": {
    "profile": "minimal"
  }
}
```

## Top-Level Fields

| Field | Type | Required | Notes |
|---|---|---:|---|
| `meta` | object | No | Optional title/subtitle |
| `clusters` | object | Yes | Main graph regions and nodes |
| `helpers` | array | No | Memory-compression helper nodes |
| `edges` | array | Yes | Directed labeled edges |
| `sidebar` | object | Yes | Hints and enabled sections |
| `features` | object | Yes | Compatibility metadata; `profile` is still validated |

## `meta`

| Field | Type | Required | Notes |
|---|---|---:|---|
| `title` | string | No | Main page title |
| `subtitle` | string | No | Subtitle |

## `clusters`

`clusters` is a dictionary keyed by cluster name, usually in the form `"A. Cluster Name"`.

### Cluster object

| Field | Type | Required | Notes |
|---|---|---:|---|
| `color` | string | Yes | Hex color |
| `center` | array | No | Preferred cluster center as `[x, y]` for stable layout |
| `nodes` | array | Yes | May be empty, but empty clusters are skipped with a warning |

### Cluster node

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | string | Yes | Globally unique |
| `label` | string | Yes | Visible node label |
| `title` | string | Yes | Tooltip text |
| `tooltip` | string | No | Optional richer hover text; prefer plain multiline text |
| `nodeType` | string | Yes | Use `"tool"` for normal cluster nodes |

Notes:
- In the current renderer, cluster nodes render as standard nodes.
- Although the validator accepts `nodeType`, the separate `helpers[]` array is the real path for helper-style diamond nodes.
- `tooltip` overrides `title` for hover content when provided.
- Supplying `center` is strongly recommended for deterministic layout; if omitted, the renderer may auto-place the cluster and emit a warning.

## `helpers`

Helpers are rendered as diamond nodes and are the preferred way to express memory-compression nodes.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | string | Yes | Globally unique |
| `label` | string | Yes | Usually starts with `◈` |
| `title` | string | Yes | Tooltip text |
| `tooltip` | string | No | Optional richer hover text; prefer plain multiline text |
| `connects_to` | array | Yes | IDs of nodes or helpers that exist |
| `position` | array | No | Preferred helper position as `[x, y]` for stable layout |

Notes:
- Helper `connects_to` creates real directed edges from helper → target.
- Do not also define the same pair manually in `edges`.
- Supplying `position` is strongly recommended for deterministic layout; if omitted, the renderer may fall back to default placement and emit a warning.

## `edges`

| Field | Type | Required | Notes |
|---|---|---:|---|
| `from` | string | Yes | Source node ID |
| `to` | string | Yes | Target node ID |
| `label` | string | Yes | Edge label shown in the graph |
| `tooltip` | string | No | Optional richer hover text; falls back to `label` |
| `edgeType` | string | No | Currently ignored by the renderer; keep only if your pipeline needs it |

Notes:
- Treat edges as directed mnemonic links, not bidirectional graph declarations.
- Do **not** define both `A → B` and `B → A`.

## `sidebar`

| Field | Type | Required | Notes |
|---|---|---:|---|
| `hints` | array | Yes | Memory hints shown in the sidebar |
| `sections` | array | Yes | Enabled sidebar sections |

Allowed `sidebar.sections` values:
- `filter`
- `hints`
- `legend`
- `stats`
- `tips`

Notes:
- A section not listed here will not render.
- `stats` is controlled by `sections`; do not assume profile gating.

## `features`

| Field | Type | Required | Notes |
|---|---|---:|---|
| `profile` | string | Yes | Must be `minimal`, `standard`, or `full` |

Notes:
- The current renderer validates these three values.
- The current shell does **not** meaningfully differentiate behavior by profile.

## Validation Rules

The renderer validates data before rendering.

### Hard failures
- `clusters` missing or empty
- node/helper missing `id`
- duplicate node/helper IDs
- edge missing `from` or `to`
- edge references nonexistent node/helper IDs
- helper `connects_to` references nonexistent IDs
- duplicate directed edge pairs across explicit edges and helper-generated edges
- reverse duplicate pairs such as `A → B` and `B → A`
- invalid `features.profile`
- invalid `sidebar.sections` value
- self-loop edge (`from == to`)

### Warnings / non-fatal behavior
- empty cluster `nodes` array: skipped with warning
- missing cluster `center`: renderer may auto-place the cluster and emit a warning
- missing helper `position`: renderer may use fallback helper placement and emit a warning
- missing layout-specific constants in the renderer: fallback auto-layout / fallback helper positions may be used

## Practical Guidance

1. Prefer putting real content in `clusters`, helper-style memory compression in `helpers`, and direct relationships in `edges`.
2. Keep labels short and memorable.
3. Keep edge labels explanatory but concise.
4. Prefer tooltip detail before adding more edges; richer hover text is cheaper than a denser graph.
5. Keep one canonical direction for a concept pair instead of encoding both directions.
6. Provide `center` for each cluster and `position` for each helper whenever you want stable, intentional layout.
7. If the rendered layout is poor, adjust the renderer-side layout constants only when necessary.

## Output Path Guidance

- Use absolute paths for `--data` and `--output`.
- The stable default output location is the renderer `references/` directory.
- Keeping output in `references/` avoids relative asset resolution issues in generated HTML.
