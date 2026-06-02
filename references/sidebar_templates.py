"""HTML/JS shell builders for mnemonic memory maps.

Theme CSS lives in mnemonic_theme.css so visual changes stay isolated.
This module focuses on panel markup and interaction logic only.
"""

from __future__ import annotations

from pathlib import Path


JsonObject = dict[str, object]
FeatureFlags = dict[str, bool]


BASE_DIR = Path(__file__).parent
THEME_CSS_FILE = BASE_DIR / "mnemonic_theme.css"


FEATURE_PROFILES: dict[str, FeatureFlags] = {
    "minimal": {
        "cluster_filter": True,
        "highlight": True,
        "hover": True,
        "physics_controls": True,
        "collapsible": True,
    },
    "standard": {
        "cluster_filter": True,
        "highlight": True,
        "hover": True,
        "physics_controls": True,
        "collapsible": True,
    },
    "full": {
        "cluster_filter": True,
        "highlight": True,
        "hover": True,
        "physics_controls": True,
        "collapsible": True,
    },
}


def load_theme_css() -> str:
    return THEME_CSS_FILE.read_text(encoding="utf-8")


def build_filter_section(clusters: JsonObject, sections: list[str]) -> str:
    if "filter" not in sections or not clusters:
        return ""
    cluster_buttons = "\n".join(
        f'<button class="mn-chip" data-cluster="{cluster_name}">{cluster_name.split(". ", 1)[-1]}</button>'
        for cluster_name in clusters
    )
    return f"""
    <section class="mn-section">
      <div class="mn-section-title">按记忆分块</div>
      <div class="mn-chip-wrap">
        <button class="mn-chip is-active" data-filter="all">全部</button>
        {cluster_buttons}
      </div>
    </section>"""


def build_hints_section(data: JsonObject, sections: list[str]) -> str:
    if "hints" not in sections:
        return ""
    sidebar = data.get("sidebar", {})
    hints = sidebar.get("hints", []) if isinstance(sidebar, dict) else []
    if not hints:
        return ""
    items = "".join(f"<li>{hint}</li>" for hint in hints)
    return f"""
    <section class="mn-section">
      <div class="mn-section-title">学习提示</div>
      <ul class="mn-list">{items}</ul>
    </section>"""


def build_legend_section(clusters: JsonObject, sections: list[str]) -> str:
    if "legend" not in sections or not clusters:
        return ""
    rows_parts: list[str] = []
    for cluster_name, cluster_data in clusters.items():
        if not isinstance(cluster_name, str) or not isinstance(cluster_data, dict):
            continue
        color = str(cluster_data.get("color", "#64748b"))
        rows_parts.append(
            f'<div class="mn-legend-row"><span class="mn-swatch" style="background:{color}"></span><span>{cluster_name}</span></div>'
        )
    rows = "\n".join(rows_parts)
    return f"""
    <section class="mn-section">
      <div class="mn-section-title">图例</div>
      {rows}
      <div class="mn-legend-row"><span class="mn-swatch mn-swatch-helper"></span><span>[辅助概念]</span></div>
    </section>"""


def build_stats_section(data: JsonObject, sections: list[str]) -> str:
    if "stats" not in sections:
        return ""
    clusters = data.get("clusters", {})
    helpers = data.get("helpers", [])
    edges = data.get("edges", [])
    cluster_count = len(clusters) if isinstance(clusters, dict) else 0
    node_count = 0
    if isinstance(clusters, dict):
        for cluster in clusters.values():
            if isinstance(cluster, dict):
                nodes = cluster.get("nodes", [])
                if isinstance(nodes, list):
                    node_count += len(nodes)
    helper_count = len(helpers) if isinstance(helpers, list) else 0
    edge_count = len(edges) if isinstance(edges, list) else 0
    if isinstance(helpers, list):
        for helper in helpers:
            if isinstance(helper, dict):
                connects_to = helper.get("connects_to", [])
                if isinstance(connects_to, list):
                    edge_count += len(connects_to)
    return f"""
    <section class="mn-section">
      <div class="mn-section-title">图谱统计</div>
      <div class="mn-stat-grid">
        <div class="mn-stat-card"><span class="mn-stat-value">{cluster_count}</span><span class="mn-stat-label">分区</span></div>
        <div class="mn-stat-card"><span class="mn-stat-value">{node_count}</span><span class="mn-stat-label">节点</span></div>
        <div class="mn-stat-card"><span class="mn-stat-value">{helper_count}</span><span class="mn-stat-label">辅助</span></div>
        <div class="mn-stat-card"><span class="mn-stat-value">{edge_count}</span><span class="mn-stat-label">连线</span></div>
      </div>
    </section>"""


def build_tips_section(sections: list[str]) -> str:
    if "tips" not in sections:
        return ""
    return """
    <section class="mn-section">
      <div class="mn-section-title">操作提示</div>
      <ul class="mn-list">
        <li>单击节点：突出其直接关联。</li>
        <li>点击空白：恢复整张图的默认强调。</li>
        <li>双击画布：重新适配视图。</li>
        <li>左侧面板可实时调整物理参数。</li>
      </ul>
    </section>"""


def build_right_panel_body(data: JsonObject) -> str:
    sidebar = data.get("sidebar", {})
    sections = sidebar.get("sections", []) if isinstance(sidebar, dict) else []
    raw_clusters = data.get("clusters", {})
    clusters: JsonObject = raw_clusters if isinstance(raw_clusters, dict) else {}
    return "".join(
        [
            build_filter_section(clusters, sections),
            build_hints_section(data, sections),
            build_legend_section(clusters, sections),
            build_stats_section(data, sections),
            build_tips_section(sections),
        ]
    )


def build_left_panel_body() -> str:
    return """
    <section class="mn-section">
      <div class="mn-section-title">基础操作</div>
      <div class="mn-action-grid">
        <button class="mn-btn" id="btn-fit-view" type="button">适配视图</button>
        <button class="mn-btn" id="btn-reset-focus" type="button">清除强调</button>
      </div>
    </section>
    <section class="mn-section">
      <div class="mn-section-headline">
        <div class="mn-section-title">物理</div>
        <button class="mn-btn mn-btn-primary" id="btn-toggle-physics" type="button" aria-pressed="false">已关闭</button>
      </div>
      <div class="mn-control-stack">
        <label class="mn-control">
          <span class="mn-control-row"><span>连线长度</span><strong id="distance-value">180</strong></span>
          <input id="distance-slider" class="mn-slider" type="range" min="80" max="360" step="5" value="180">
        </label>
        <label class="mn-control">
          <span class="mn-control-row"><span>连线弯曲度</span><strong id="curvature-value">0.20</strong></span>
          <input id="curvature-slider" class="mn-slider" type="range" min="0" max="0.6" step="0.02" value="0.20">
        </label>
        <label class="mn-control">
          <span class="mn-control-row"><span>弹簧强度</span><strong id="spring-value">0.025</strong></span>
          <input id="spring-slider" class="mn-slider" type="range" min="0.005" max="0.12" step="0.001" value="0.025">
        </label>
        <label class="mn-control">
          <span class="mn-control-row"><span>斥力大小</span><strong id="repulsion-value">-6000</strong></span>
          <input id="repulsion-slider" class="mn-slider" type="range" min="-12000" max="-1200" step="100" value="-6000">
        </label>
        <label class="mn-control">
          <span class="mn-control-row"><span>阻尼</span><strong id="damping-value">0.42</strong></span>
          <input id="damping-slider" class="mn-slider" type="range" min="0.15" max="0.8" step="0.01" value="0.42">
        </label>
      </div>
    </section>"""


def build_panel_html(panel_id: str, side: str, title: str, body: str) -> str:
    return f"""
<aside id="{panel_id}" class="mn-panel mn-panel-{side}">
  <button class="mn-panel-toggle" type="button" data-target="{panel_id}" aria-expanded="true"></button>
  <div class="mn-panel-shell">
    <div class="mn-panel-header">
      <div class="mn-panel-title">{title}</div>
    </div>
    <div class="mn-panel-body">{body}</div>
  </div>
</aside>"""


JS_APP = r'''
  var STORAGE_KEY = "mnemonic_map_ui_state_v2";
  var selectedNodeId = null;
  var hoveredNodeId = null;
  var uiState = {
    leftCollapsed: false,
    rightCollapsed: false,
    activeCluster: null,
    physics: {
      enabled: false,
      repulsion: -6000,
      distance: 180,
      spring: 0.025,
      curvature: 0.20,
      damping: 0.42
    }
  };

  function cloneColor(colorValue) {
    if (!colorValue || typeof colorValue !== "object") return colorValue;
    return Object.assign({}, colorValue);
  }

  function cloneFont(fontValue) {
    if (!fontValue || typeof fontValue !== "object") return fontValue;
    return Object.assign({}, fontValue);
  }

  function cloneNode(node) {
    return Object.assign({}, node, {
      color: cloneColor(node.color),
      font: cloneFont(node.font)
    });
  }

  function cloneEdge(edge) {
    return Object.assign({}, edge, {
      color: cloneColor(edge.color),
      font: cloneFont(edge.font),
      smooth: edge.smooth && typeof edge.smooth === "object" ? Object.assign({}, edge.smooth) : edge.smooth
    });
  }

  var originNodes = nodes.get().map(cloneNode);
  var originEdges = edges.get().map(cloneEdge);
  var originNodeMap = {};
  var originEdgeMap = {};
  originNodes.forEach(function(node) { originNodeMap[node.id] = node; });
  originEdges.forEach(function(edge) { originEdgeMap[edge.id] = edge; });

  function readStoredState() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      var parsed = JSON.parse(raw);
      if (typeof parsed.leftCollapsed === "boolean") uiState.leftCollapsed = parsed.leftCollapsed;
      if (typeof parsed.rightCollapsed === "boolean") uiState.rightCollapsed = parsed.rightCollapsed;
      if (typeof parsed.activeCluster === "string" || parsed.activeCluster === null) {
        uiState.activeCluster = parsed.activeCluster;
      }
      if (parsed.physics && typeof parsed.physics === "object") {
        Object.assign(uiState.physics, parsed.physics);
      }
    } catch (error) {}
  }

  function saveStoredState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(uiState));
    } catch (error) {}
  }

  function hexToRgba(colorValue, alpha) {
    if (!colorValue || typeof colorValue !== "string") return "rgba(160, 174, 192, " + alpha + ")";
    if (colorValue.indexOf("rgba(") === 0) {
      return colorValue.replace(/rgba\(([^,]+),([^,]+),([^,]+),[^)]+\)/, function(_, r, g, b) {
        return "rgba(" + r.trim() + ", " + g.trim() + ", " + b.trim() + ", " + alpha + ")";
      });
    }
    var normalized = colorValue.replace("#", "");
    if (normalized.length === 3) {
      normalized = normalized.split("").map(function(part) { return part + part; }).join("");
    }
    var parsed = parseInt(normalized, 16);
    if (Number.isNaN(parsed)) return "rgba(160, 174, 192, " + alpha + ")";
    return "rgba(" + ((parsed >> 16) & 255) + ", " + ((parsed >> 8) & 255) + ", " + (parsed & 255) + ", " + alpha + ")";
  }

  function getNodeColor(baseColor, alpha) {
    if (baseColor && typeof baseColor === "object") {
      return {
        background: hexToRgba(baseColor.background || "#3b82f6", alpha),
        border: hexToRgba(baseColor.border || baseColor.background || "#cbd5e1", alpha)
      };
    }
    return hexToRgba(baseColor || "#3b82f6", alpha);
  }

  function getEdgeBaseColor(edge) {
    if (edge.color && typeof edge.color === "object") return edge.color.color || "#cfd8dc";
    return edge.color || "#cfd8dc";
  }

  function getNeighborIds(targetId) {
    var result = {};
    if (!targetId) return result;
    result[targetId] = true;
    edges.get().forEach(function(edge) {
      if (edge.hidden) return;
      if (edge.from === targetId || edge.to === targetId) {
        result[edge.from] = true;
        result[edge.to] = true;
      }
    });
    return result;
  }

  function isNodeVisible(node) {
    if (!uiState.activeCluster) return true;
    return node.cluster === uiState.activeCluster || node.nodeType === "helper";
  }

  function isEdgeVisible(edge) {
    var fromNode = originNodeMap[edge.from];
    var toNode = originNodeMap[edge.to];
    if (!fromNode || !toNode) return true;
    return isNodeVisible(fromNode) && isNodeVisible(toNode);
  }

  function getVisibleNodeIds() {
    return originNodes.filter(isNodeVisible).map(function(node) { return node.id; });
  }

  function renderGraphState() {
    var neighbors = getNeighborIds(selectedNodeId);
    nodes.update(nodes.get().map(function(node) {
      var base = originNodeMap[node.id] || node;
      var isSelected = selectedNodeId === node.id;
      var isNeighbor = !!neighbors[node.id];
      var isHover = hoveredNodeId === node.id;
      var alpha = selectedNodeId ? (isSelected ? 1 : (isNeighbor ? 0.98 : 0.14)) : 1;
      var fontAlpha = selectedNodeId ? (isSelected ? 1 : (isNeighbor ? 0.94 : 0.22)) : 1;
      var sizeBoost = isSelected ? 5 : (isHover ? 3 : 0);
      var borderWidth = isSelected ? 4 : (isHover ? 3 : (base.borderWidth || 1));
      return {
        id: node.id,
        hidden: !isNodeVisible(base),
        color: getNodeColor(base.color, alpha),
        font: Object.assign({}, cloneFont(base.font) || {}, { color: hexToRgba((base.font && base.font.color) || "#ffffff", fontAlpha) }),
        size: (base.size || 22) + sizeBoost,
        borderWidth: borderWidth,
        shadow: !!(isSelected || isHover)
      };
    }));

    edges.update(edges.get().map(function(edge) {
      var base = originEdgeMap[edge.id] || edge;
      var connected = selectedNodeId ? (edge.from === selectedNodeId || edge.to === selectedNodeId) : true;
      var edgeAlpha = selectedNodeId ? (connected ? 0.96 : 0.12) : 1;
      var fontAlpha = selectedNodeId ? (connected ? 0.94 : 0.18) : 1;
      var baseColor = getEdgeBaseColor(base);
      return {
        id: edge.id,
        hidden: !isEdgeVisible(base),
        width: selectedNodeId ? (connected ? Math.max(base.width || 1.8, 3) : 1) : (base.width || 1.8),
        dashes: base.dashes,
        color: {
          color: hexToRgba(baseColor, edgeAlpha),
          highlight: hexToRgba(baseColor, Math.min(edgeAlpha + 0.04, 1))
        },
        font: Object.assign({}, cloneFont(base.font) || {}, {
          color: hexToRgba((base.font && base.font.color) || "#dbe4f0", fontAlpha),
          background: selectedNodeId && !connected ? "rgba(15, 23, 42, 0.08)" : ((base.font && base.font.background) || "rgba(15, 23, 42, 0.48)")
        }),
        smooth: base.smooth && typeof base.smooth === "object" ? Object.assign({}, base.smooth) : base.smooth
      };
    }));
  }

  function restoreOriginalStyles() {
    selectedNodeId = null;
    hoveredNodeId = null;
    nodes.update(originNodes.map(function(node) {
      return {
        id: node.id,
        hidden: !isNodeVisible(node),
        color: cloneColor(node.color),
        font: cloneFont(node.font),
        size: node.size,
        borderWidth: node.borderWidth || 1,
        shadow: false
      };
    }));
    edges.update(originEdges.map(function(edge) {
      return {
        id: edge.id,
        hidden: !isEdgeVisible(edge),
        color: cloneColor(edge.color),
        font: cloneFont(edge.font),
        width: edge.width,
        dashes: edge.dashes,
        smooth: edge.smooth && typeof edge.smooth === "object" ? Object.assign({}, edge.smooth) : edge.smooth
      };
    }));
  }

  function fitView() {
    network.fit({ animation: { duration: 280, easingFunction: "easeInOutQuad" } });
  }

  function setChipActive(activeButton) {
    document.querySelectorAll(".mn-chip").forEach(function(button) {
      button.classList.toggle("is-active", button === activeButton);
    });
  }

  function syncActiveClusterChip() {
    if (!uiState.activeCluster) {
      var allButton = document.querySelector('.mn-chip[data-filter="all"]');
      if (allButton) setChipActive(allButton);
      return;
    }
    var clusterButton = document.querySelector('.mn-chip[data-cluster="' + uiState.activeCluster.replace(/"/g, '\\"') + '"]');
    if (clusterButton) setChipActive(clusterButton);
  }

  function showAllClusters() {
    uiState.activeCluster = null;
    saveStoredState();
    syncActiveClusterChip();
    renderGraphState();
    var visibleNodeIds = getVisibleNodeIds();
    if (visibleNodeIds.length) {
      network.fit({ nodes: visibleNodeIds, animation: { duration: 280, easingFunction: "easeInOutQuad" } });
    }
  }

  function filterCluster(clusterName) {
    uiState.activeCluster = clusterName;
    saveStoredState();
    syncActiveClusterChip();
    renderGraphState();
    var visibleNodeIds = getVisibleNodeIds();
    if (visibleNodeIds.length) {
      network.fit({ nodes: visibleNodeIds, animation: { duration: 280, easingFunction: "easeInOutQuad" } });
    }
  }

  function bindClusterFilter() {
    document.querySelectorAll(".mn-chip[data-cluster]").forEach(function(button) {
      button.addEventListener("click", function() {
        filterCluster(button.getAttribute("data-cluster"));
      });
    });
    var allButton = document.querySelector('.mn-chip[data-filter="all"]');
    if (allButton) {
      allButton.addEventListener("click", function() {
        showAllClusters();
      });
    }
  }

  function syncToggleButton(panel) {
    var toggle = panel.querySelector(".mn-panel-toggle");
    if (!toggle) return;
    var isCollapsed = panel.classList.contains("is-collapsed");
    var isLeft = panel.classList.contains("mn-panel-left");
    toggle.textContent = isCollapsed ? (isLeft ? "▶" : "◀") : (isLeft ? "◀" : "▶");
    toggle.setAttribute("aria-expanded", isCollapsed ? "false" : "true");
    toggle.setAttribute("title", isCollapsed ? "展开侧边栏" : "收起侧边栏");
  }

  function setPanelCollapsed(panelId, collapsed) {
    var panel = document.getElementById(panelId);
    if (!panel) return;
    panel.classList.toggle("is-collapsed", !!collapsed);
    syncToggleButton(panel);
  }

  function bindPanelToggles() {
    document.querySelectorAll(".mn-panel-toggle").forEach(function(button) {
      button.addEventListener("click", function() {
        var panelId = button.getAttribute("data-target");
        var panel = document.getElementById(panelId);
        if (!panel) return;
        var nextCollapsed = !panel.classList.contains("is-collapsed");
        setPanelCollapsed(panelId, nextCollapsed);
        if (panelId === "mnemonic-left-panel") uiState.leftCollapsed = nextCollapsed;
        if (panelId === "mnemonic-right-panel") uiState.rightCollapsed = nextCollapsed;
        saveStoredState();
      });
    });
  }

  function updatePhysicsLabels() {
    var values = uiState.physics;
    var mappings = {
      "distance-value": values.distance,
      "curvature-value": values.curvature.toFixed(2),
      "spring-value": values.spring.toFixed(3),
      "repulsion-value": values.repulsion,
      "damping-value": values.damping.toFixed(2)
    };
    Object.keys(mappings).forEach(function(id) {
      var element = document.getElementById(id);
      if (element) element.textContent = String(mappings[id]);
    });
  }

  function syncPhysicsInputs() {
    var values = uiState.physics;
    var inputs = {
      "distance-slider": values.distance,
      "curvature-slider": values.curvature,
      "spring-slider": values.spring,
      "repulsion-slider": values.repulsion,
      "damping-slider": values.damping
    };
    Object.keys(inputs).forEach(function(id) {
      var input = document.getElementById(id);
      if (input) input.value = String(inputs[id]);
    });
    updatePhysicsLabels();
  }

  function applyPhysics() {
    var values = uiState.physics;
    var nextSmooth = { enabled: true, type: "curvedCW", roundness: values.curvature };
    originEdges = originEdges.map(function(edge) {
      return Object.assign({}, edge, { smooth: Object.assign({}, nextSmooth) });
    });
    originEdgeMap = {};
    originEdges.forEach(function(edge) { originEdgeMap[edge.id] = edge; });
    network.setOptions({
      interaction: { hover: true, tooltipDelay: 120 },
      physics: {
        enabled: values.enabled,
        stabilization: { enabled: false, iterations: 0, fit: false },
        barnesHut: {
          gravitationalConstant: values.repulsion,
          springLength: values.distance,
          springConstant: values.spring,
          damping: values.damping,
          centralGravity: 0.08,
          avoidOverlap: 0.4
        }
      },
      edges: {
        smooth: {
          enabled: nextSmooth.enabled,
          type: nextSmooth.type,
          roundness: nextSmooth.roundness
        }
      }
    });
    edges.update(edges.get().map(function(edge) {
      return {
        id: edge.id,
        smooth: Object.assign({}, nextSmooth)
      };
    }));
    if (values.enabled) {
      network.startSimulation();
    } else {
      network.stopSimulation();
    }
    var button = document.getElementById("btn-toggle-physics");
    if (button) {
      button.textContent = values.enabled ? "已开启" : "已关闭";
      button.classList.toggle("is-active", values.enabled);
      button.setAttribute("aria-pressed", values.enabled ? "true" : "false");
    }
    updatePhysicsLabels();
  }

  function bindPhysicsControls() {
    var button = document.getElementById("btn-toggle-physics");
    if (button) {
      button.addEventListener("click", function() {
        uiState.physics.enabled = !uiState.physics.enabled;
        applyPhysics();
        saveStoredState();
      });
    }

    var sliderBindings = [
      ["distance-slider", "distance", parseInt],
      ["curvature-slider", "curvature", parseFloat],
      ["spring-slider", "spring", parseFloat],
      ["repulsion-slider", "repulsion", parseInt],
      ["damping-slider", "damping", parseFloat]
    ];
    sliderBindings.forEach(function(binding) {
      var input = document.getElementById(binding[0]);
      if (!input) return;
      input.addEventListener("input", function(event) {
        uiState.physics[binding[1]] = binding[2](event.target.value);
        applyPhysics();
        saveStoredState();
      });
    });
  }

  function bindCanvasActions() {
    var fitButton = document.getElementById("btn-fit-view");
    var resetButton = document.getElementById("btn-reset-focus");
    if (fitButton) fitButton.addEventListener("click", fitView);
    if (resetButton) {
      resetButton.addEventListener("click", function() {
        showAllClusters();
        setChipActive(document.querySelector('.mn-chip[data-filter="all"]'));
        restoreOriginalStyles();
      });
    }
  }

  network.on("click", function(params) {
    if (params.nodes && params.nodes.length > 0) {
      selectedNodeId = params.nodes[0];
      renderGraphState();
      return;
    }
    restoreOriginalStyles();
  });

  network.on("hoverNode", function(params) {
    hoveredNodeId = params.node;
    document.body.style.cursor = "pointer";
    renderGraphState();
  });

  network.on("blurNode", function() {
    hoveredNodeId = null;
    document.body.style.cursor = "default";
    renderGraphState();
  });

  network.on("deselectNode", function() {
    restoreOriginalStyles();
  });

  network.on("doubleClick", function(params) {
    if (!params.nodes || !params.nodes.length) {
      restoreOriginalStyles();
      showAllClusters();
    }
  });

  network.on("stabilized", function() {
    if (uiState.physics.enabled) {
      network.startSimulation();
    }
  });

  readStoredState();
  bindClusterFilter();
  bindPanelToggles();
  bindPhysicsControls();
  bindCanvasActions();
  setPanelCollapsed("mnemonic-left-panel", uiState.leftCollapsed);
  setPanelCollapsed("mnemonic-right-panel", uiState.rightCollapsed);
  syncActiveClusterChip();
  syncPhysicsInputs();
  applyPhysics();
  if (uiState.activeCluster) {
    filterCluster(uiState.activeCluster);
  }
  renderGraphState();
'''


def build_full_sidebar_html(data: JsonObject, _features: FeatureFlags) -> str:
    meta = data.get("meta", {})
    title = meta.get("title", "Memory Map") if isinstance(meta, dict) else "Memory Map"
    left_panel = build_panel_html(
        panel_id="mnemonic-left-panel",
        side="left",
        title="基础操作",
        body=build_left_panel_body(),
    )
    right_panel = build_panel_html(
        panel_id="mnemonic-right-panel",
        side="right",
        title=title,
        body=build_right_panel_body(data),
    )
    return f"""
<style>
{load_theme_css()}
</style>
{left_panel}
{right_panel}
<script>
(function() {{
  // PyVis globals: network, nodes, edges
{JS_APP}
}})();
</script>
</body>"""
