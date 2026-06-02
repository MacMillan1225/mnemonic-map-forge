---
name: mnemonic-map-forge
description: Build reusable mnemonic exploration maps and memory-first knowledge graphs with helper nodes, low-clutter connections, and template-based PyVis output. Use when the user wants a memorization-friendly map where associative recall matters more than strict ontology.
---

# Mnemonic Map Forge

Create **记忆漫游图 / memory exploration maps** that help users remember material through strong, walkable associations.

This skill is for **memory-first graph design**, not strict ontology modeling, exhaustive causal graphs, or dense academic concept maps.

## Core Principle

Connect two nodes when the connection helps the user **remember them together quickly**.

- Good: `风险分类 → 应对策略`
- Good: `信息管理 → 项目管理信息系统`
- Bad: technically true but weak, noisy, or slow-to-recall edges

**Edge density is a first-class constraint, not a suggestion.** The Non-Negotiable Constraints section defines a hard ceiling (< 1.2 edges per node). Maps that exceed it violate the skill's core principle — they are classification webs, not memory maps.

## What This Skill Optimizes For

1. **Memory fluency over formal rigor**
2. **One connected graph**
3. **Low clutter**
4. **Helper nodes as memory compression**
5. **Template reuse** instead of regenerating the whole UI shell

## Non-Negotiable Constraints

### 1. One Connected Component
- No isolated subgraphs
- Every real node must be reachable from the rest of the map
- If disconnected, add the **single best bridge**, not many weak bridges

### 2. Helper Nodes Must Compress Memory
Use helper nodes only when they reduce clutter and improve recall.

Pattern:

```text
anchor node → helper node → sibling nodes
```

Good examples:
- `风险分类 → 应对策略 → 威胁 / 机会 / 整体 / 应急`
- `沟通方法 → 沟通辅助 → 会议 / 技能 / 模型 / 技术 / 需求分析`

Do not create helper nodes that merely rename a category or duplicate an already-good direct chain.

### 3. Classification Is Secondary
Color blocks and grouping are allowed, but the target shape is:

- a few landmarks
- local branches
- a couple of strong bridges
- helper compressions
- one walkable connected structure

Avoid:
- a giant classifier hub
- a pure taxonomy
- a dense everything-connects-to-everything web

### 4. No Reverse-Duplicate Links
- Do **not** encode both `A → B` and `B → A`
- Pick the single direction that best supports recall
- If two concepts mutually reinforce each other, use **one canonical edge** and put the extra explanation in the hover tooltip
- Treat helper `connects_to` as real directed edges when checking duplicates

### 5. Edge Density Ceiling

总边数（`edges[]` 条数 + 所有 helper 的 `connects_to` 条目数之和）与真实节点数的比值必须 **小于 1.2**。

公式：
```
(totalEdges + sum_of_helper_connects_to) / realNodesCount < 1.2
```

示例：
| 真实节点数 | 边数上限（含 helper 边） | 超过后怎么做 |
|---|---|---|
| 20 | < 24 | 删除冗余边直到达标 |
| 40 | < 48 | 同上 |
| 50 | < 60 | 同上 |

如果超出阈值，**禁止继续布局或渲染**。必须先删除弱/冗余/仅分类有效的边，直到比值低于 1.2。

⚠️ **常见陷阱：第一次设计的人通常会超出阈值 50% 以上。** 建议采用"先稀疏后补充"的策略——先用保证连通的最小边数做第一版，渲染确认可走后逐条添加确有必要的边。这比"先加满再删"省力得多。

高于此阈值意味着图已经退化成了"网"，失去了漫游图的可走性。密度再低一些（< 0.8）通常效果更好。

### 6. Tooltip Depth Is Allowed
- Hover tooltips may contain extra recall cues, examples, contrasts, and short mnemonics
- Prefer **plain multiline text** for tooltip detail
- Use tooltip detail to enrich understanding without adding more edges

## When To Use This Skill

Use this skill when the user wants to:
- memorize tools, methods, concepts, processes, formulas, or frameworks
- turn notes into an interactive revision graph
- create a low-noise map instead of a strict knowledge graph
- iteratively refine graph structure for better recall

## Deliverables

The ideal output contains:

1. Real nodes
2. Helper nodes only where useful
3. Labeled edges with a memory reason
4. A reusable renderer
5. A review pass proving the graph is easier to remember

## Required Workflow

### Step 1 — Extract Real Nodes
- Preserve required real nodes unless the user explicitly allows omission
- Normalize aliases and naming inconsistencies
- Distinguish real nodes from helper nodes

### Step 2 — Identify Memory Anchors
Look for vivid terms, common hubs, contrast pairs, concrete methods, and familiar workflow landmarks.

Do **not** assume the biggest hub is always best.

### Step 3 — Propose Memory Connections
For each candidate edge, ask:

> Will this help the user remember the next node quickly?

Keep an edge if it provides:
- obvious memory association
- clear contrast
- familiar workflow progression
- semantic compression
- visual route-building value

Then check:
- Would one direction be enough?
- Can the extra context live in a tooltip instead of another edge?
- Would this edge still be worth keeping if the map were viewed from afar?

Reject an edge if it is only technically true, weak for recall, redundant, or visually noisy.

### Step 4 — Introduce Helper Nodes Sparingly
Add helper nodes only when they:
- compress several siblings into one mental hook
- reduce messy direct links
- connect from a meaningful anchor
- make the route easier to walk mentally

### Step 5 — Force Connectivity & Enforce Density
Before layout, verify:
- every real node belongs to one connected component
- no region is isolated
- cross-block bridges are intentional and minimal
- **edge density ratio < 1.2** (`(edges.length + sum(helpers[].connects_to.length)) / realNodes.length`)
- **if density ≥ 1.2**: stop and delete weak edges until under threshold, then re-verify connectivity — if deletion breaks connectivity, restore the minimal bridge needed for that connection and try deleting a different edge

### Step 6 — Choose Layout Strategy
Pick one dominant layout mode:

- **Route Map**: memorable travel path
- **Landmark + Branches**: a few anchors with short branches
- **Grid of Regions**: user already thinks in spatial zones

Prefer macro clarity first, then light local scatter.

### Step 7 — Render With the Reusable Template
Do **not** regenerate the whole UI shell unless the user explicitly asks.

Usually change only:
- JSON data
- helper data
- edge data
- layout-related constants when necessary
- sidebar hints

When using the current renderer flow, treat **layout input as part of the deliverable**: provide cluster centers and helper positions together with the graph content. Missing positions are tolerated, but the renderer may emit `WARNING` messages and fall back to auto/fallback placement.

#### Minimal JSON Shape

```json
{
  "clusters": {
    "A. Example": {
      "color": "#e74c3c",
      "center": [0, 0],
      "nodes": [
        {"id": "node_a", "label": "A", "title": "A", "tooltip": "A\n核心记忆：这是入口概念\n对比：不要和 B 混淆", "nodeType": "tool"}
      ]
    }
  },
  "helpers": [
    {"id": "helper_x", "label": "◈ X", "title": "helper", "tooltip": "helper\n作用：压缩兄弟节点记忆", "connects_to": ["node_a"], "position": [180, -40]}
  ],
  "edges": [
    {"from": "node_a", "to": "helper_x", "label": "memory link", "tooltip": "为什么连？\n因为 A 最容易把你带到辅助记忆 X"}
  ],
  "sidebar": {
    "hints": ["Walk the graph from anchor to helper."],
    "sections": ["filter", "hints", "legend", "stats", "tips"]
  },
  "features": {
    "profile": "minimal"
  }
}
```

Use `references/data_schema.md` only when debugging validation failures or checking exact field rules.

#### Edge Direction Rule

- `edges[]` and helper `connects_to` together form the final directed graph
- Do **not** define the same pair twice
- Do **not** define reverse pairs like `A → B` and `B → A`
- When in doubt, keep the single edge with the strongest recall direction

#### Tooltip Rule

- `title` remains the baseline tooltip text
- Optional `tooltip` may contain richer hover text
- Prefer newline-separated plain text over HTML
- Tooltips are the first place to put extra detail before adding more edges

#### Profile Guidance

Current renderer accepts `minimal`, `standard`, and `full` for compatibility, but the current shell does **not** provide materially different feature sets by profile. Treat profile mainly as metadata unless the renderer is explicitly extended.

#### Sidebar Sections

`sidebar.sections` may include:
- `filter`
- `hints`
- `legend`
- `stats`
- `tips`

#### Positions & Warnings

- For stable, intentional layouts, provide a cluster center for every cluster and a position for every helper in the render input.
- In practice, that means carrying `center` information with each cluster in your planning/data payload and carrying `position` information with each helper.
- If positions are omitted, the renderer may emit `WARNING` messages and fall back to auto-layout / fallback coordinates.
- Warnings are acceptable as a safety net, but they are not the preferred final-state workflow.

### Step 8 — Mandatory Review Pass

Before finalizing, verify:

- [ ] All required real nodes are present
- [ ] Graph is one connected component — no isolated nodes or subgraphs
- [ ] Edge density ratio < 1.2 (`(edges + helper_connects_to) / real_nodes`), otherwise weak edges have been removed to bring it under
- [ ] Every edge helps memory rather than merely being defensible
- [ ] No pair appears in both directions (`A → B` and `B → A`)
- [ ] No useless helper node remains
- [ ] Each helper node genuinely compresses memory
- [ ] Weak or redundant edges are removed
- [ ] Macro layout matches how the user thinks spatially
- [ ] The graph is neither a straight line nor a chaotic web
- [ ] Extra detail lives in tooltips before new edges are added
- [ ] Static template code was reused wherever possible
- [ ] The final graph is visually walkable after one or two passes

## Rendering Strategy

This skill includes reusable renderer resources under `references/`.

### Preferred Execution Path

Prefer running:

```powershell
"E:\文档\Obsidian\软考学习\.opencode\skills\mnemonic-map-forge\references\PYVIS_MEMORY_MAP_TEMPLATE.exe" --data "E:\文档\Obsidian\软考学习\test_mnemonic_map.json" --output "E:\文档\Obsidian\软考学习\.opencode\skills\mnemonic-map-forge\references\test_mnemonic_map_refactored_exe.html"
```

Rules:
- Use **absolute full paths** for `--data` and `--output`
- Prefer placing the output HTML in the **same directory as** `PYVIS_MEMORY_MAP_TEMPLATE.exe` so nearby relative assets resolve cleanly
- Treat the `references/` directory as the stable default output location
- Prefer deterministic filenames derived from the JSON data filename
- Provide cluster centers and helper positions as part of the render input whenever you want deterministic layout and fewer warnings
- If the `.exe` cannot be used, fall back to:

```powershell
python "E:\文档\Obsidian\软考学习\.opencode\skills\mnemonic-map-forge\references\PYVIS_MEMORY_MAP_TEMPLATE.py" --data "E:\文档\Obsidian\软考学习\test_mnemonic_map.json" --output "E:\文档\Obsidian\软考学习\.opencode\skills\mnemonic-map-forge\references\test_mnemonic_map_refactored_exe.html"
```

### Token Discipline

- Prefer editing data over renderer code
- Do not read the full template unless the user explicitly asks for renderer changes
- Do not rewrite the full template when a small patch will do
- Keep the sidebar and interaction shell intact unless the UI itself must change

## Recommended Output Style

When reporting the result, summarize briefly:
- chosen structural principle
- helper nodes used and why
- major bridges used
- whether the graph is fully connected

Do not over-explain every edge unless asked.
