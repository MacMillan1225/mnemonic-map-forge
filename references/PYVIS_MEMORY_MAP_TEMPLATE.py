#!/usr/bin/env python3
"""Reusable template for mnemonic exploration maps.

Replace only the DATA SECTIONS below in normal use.
Keep the rendering shell and sidebar patch largely unchanged to save tokens.
"""

from __future__ import annotations

import argparse
import importlib
import json
import webbrowser
from pathlib import Path
from typing import Any

from pyvis.network import Network

JsonDict = dict[str, Any]


if __package__:
    sidebar_templates = importlib.import_module(f"{__package__}.sidebar_templates")
else:
    sidebar_templates = importlib.import_module("sidebar_templates")

FEATURE_PROFILES = sidebar_templates.FEATURE_PROFILES
build_full_sidebar_html = sidebar_templates.build_full_sidebar_html


BASE_DIR = Path(__file__).parent
OUTPUT_FILE = BASE_DIR / "memory_map.html"


def tooltip_text(value: Any, fallback: str = "") -> str:
    if isinstance(value, str) and value:
        return value
    return fallback


def resolve_output_path(data_path: Path, output_path: Path | None) -> Path:
    if output_path is not None:
        return output_path
    return BASE_DIR / f"{data_path.stem}.html"


# ============================================================
# DATA SECTION — Legacy example (see mnemonic_data.json)
# Replace with your own JSON data file. These constants are
# kept for backward compatibility and reference.
# ============================================================

DATA_FILE: Path = BASE_DIR / "map_data.json"

CLUSTERS: dict[str, list[str]] = {
    "A. Example Region": ["Anchor A", "Anchor B"],
}

CLUSTER_COLORS = {
    "A. Example Region": "#3498db",
}

HELPER_DEFS: list[JsonDict] = [
    {
        "id": "helper_example",
        "label": "◈ Helper",
        "title": "Generic helper for memory compression",
        "connects_to": ["Anchor A", "Anchor B"],
        "cluster_hint": "A. Example Region",
    },
]

EDGE_LIST: list[tuple[str, str, str]] = [
    ("Anchor A", "helper_example", "anchor leads into helper"),
]

CLUSTER_CENTERS = {
    "A. Example Region": (0, 0),
}

ROUTE_ANGLES = {
    "A. Example Region": 0.0,
}

HELPER_POSITIONS = {
    "helper_example": (120, -40),
}

SIDEBAR_HINTS = [
    "Example route: Anchor A → Helper → Anchor B",
]

# ============================================================
# RENDERING SHELL: REUSE THIS
# ============================================================


def slugify(name: str) -> str:
    return "node_" + "".join(ch if ch.isalnum() else "_" for ch in name)


VALID_PROFILES = {"minimal", "standard", "full"}
VALID_SECTIONS = {"filter", "hints", "legend", "stats", "tips"}


def get_features(data: JsonDict) -> JsonDict:
    """Resolve feature flags from profile name."""
    profile = data.get("features", {}).get("profile", "minimal")
    return FEATURE_PROFILES.get(profile, FEATURE_PROFILES["minimal"])


def validate_data(data: JsonDict) -> None:
    """Validate JSON data against the schema. Raises ValueError on failure."""
    # Rule 1: clusters exists and non-empty
    if "clusters" not in data or not data["clusters"]:
        raise ValueError("'clusters' is required and must not be empty")

    # Collect all valid node IDs (from clusters + helpers)
    valid_ids: set[str] = set()
    helper_ids: set[str] = set()

    # Rule 2: cluster names unique (dict keys are unique by definition in JSON)

    # Gather node IDs and check rules
    for cluster_name, cluster_data in data["clusters"].items():
        nodes = cluster_data.get("nodes", [])
        # Rule 4: empty nodes = warning (not crash)
        if not nodes:
            print(f"WARNING: Cluster '{cluster_name}' has no nodes - skipping")
            continue
        for node in nodes:
            nid = node.get("id")
            if not nid:
                raise ValueError(f"Node in cluster '{cluster_name}' missing 'id'")
            # Rule 3: node ID unique
            if nid in valid_ids:
                raise ValueError(f"Duplicate node ID '{nid}' in cluster '{cluster_name}'")
            valid_ids.add(nid)

    # Gather helper IDs
    for helper in data.get("helpers", []):
        hid = helper.get("id")
        if not hid:
            raise ValueError("Helper missing 'id'")
        if hid in valid_ids or hid in helper_ids:
            raise ValueError(f"Duplicate helper ID '{hid}'")
        helper_ids.add(hid)

    all_ids = valid_ids | helper_ids

    # Rule 5: edge references valid
    seen_edges: set[tuple[str, str]] = set()
    for edge in data.get("edges", []):
        frm = edge.get("from")
        to = edge.get("to")
        if not frm or not to:
            raise ValueError(f"Edge missing 'from' or 'to': {edge}")
        if frm not in all_ids:
            raise ValueError(f"Edge 'from' references nonexistent node '{frm}'")
        if to not in all_ids:
            raise ValueError(f"Edge 'to' references nonexistent node '{to}'")
        # Rule 9: no self-loop
        if frm == to:
            raise ValueError(f"Self-loop edge detected: '{frm}' -> '{to}'")
        pair = (frm, to)
        rev_pair = (to, frm)
        if pair in seen_edges:
            raise ValueError(f"Duplicate directed edge detected: '{frm}' -> '{to}'")
        if rev_pair in seen_edges:
            raise ValueError(f"Reverse duplicate edge detected: '{frm}' -> '{to}'")
        seen_edges.add(pair)

    # Rule 6: helper connects_to references valid
    for helper in data.get("helpers", []):
        for conn_id in helper.get("connects_to", []):
            if conn_id not in all_ids:
                raise ValueError(
                    f"Helper '{helper['id']}' connects_to nonexistent node '{conn_id}'"
                )
            pair = (helper["id"], conn_id)
            rev_pair = (conn_id, helper["id"])
            if pair in seen_edges:
                raise ValueError(f"Duplicate directed edge detected: '{pair[0]}' -> '{pair[1]}'")
            if rev_pair in seen_edges:
                raise ValueError(f"Reverse duplicate edge detected: '{pair[0]}' -> '{pair[1]}'")
            seen_edges.add(pair)

    # Rule 7: features.profile valid
    features = data.get("features", {})
    profile = features.get("profile", "")
    if profile not in VALID_PROFILES:
        raise ValueError(
            f"features.profile must be one of {VALID_PROFILES}, got '{profile}'"
        )

    # Rule 8: sidebar.sections valid
    sidebar = data.get("sidebar", {})
    for section in sidebar.get("sections", []):
        if section not in VALID_SECTIONS:
            raise ValueError(
                f"sidebar.sections contains invalid value '{section}'. "
                f"Must be one of {VALID_SECTIONS}"
            )


def build_nodes(data: JsonDict) -> list[JsonDict]:
    nodes: list[JsonDict] = []
    cluster_names = list(data["clusters"].keys())
    for idx, (cluster_name, cluster_data) in enumerate(data["clusters"].items()):
        # Use configured center or auto-calculate a fallback
        data_center = cluster_data.get("center")
        if (
            isinstance(data_center, list)
            and len(data_center) == 2
            and all(isinstance(value, (int, float)) for value in data_center)
        ):
            cx, cy = int(data_center[0]), int(data_center[1])
        elif cluster_name in CLUSTER_CENTERS:
            cx, cy = CLUSTER_CENTERS[cluster_name]
        else:
            # Auto-layout fallback: evenly space clusters in a ring
            import math
            angle_val = 2 * math.pi * idx / max(len(cluster_names), 1)
            cx = int(500 * math.cos(angle_val))
            cy = int(350 * math.sin(angle_val))
            print(f"WARNING: No CLUSTER_CENTERS for '{cluster_name}' — using auto-layout ({cx}, {cy})")
        items = cluster_data.get("nodes", [])
        if not items:
            continue  # skip empty clusters
        count = len(items)
        for j, item in enumerate(items):
            t = (j - (count - 1) / 2) * 40
            perp = -18 if j % 2 == 0 else 18
            x = cx + int(t)
            y = cy + int(perp)
            nodes.append(
                {
                    "id": item["id"],
                    "label": item["label"],
                    "title": tooltip_text(item.get("tooltip"), item.get("title", item["label"])),
                    "color": cluster_data["color"],
                    "shape": "dot",
                    "size": 22,
                    "font": {"size": 13, "color": "#f5f5f5"},
                    "cluster": cluster_name,
                    "nodeType": item.get("nodeType", "tool"),
                    "x": x,
                    "y": y,
                }
            )
    for helper in data.get("helpers", []):
        hid = helper["id"]
        data_position = helper.get("position")
        if (
            isinstance(data_position, list)
            and len(data_position) == 2
            and all(isinstance(value, (int, float)) for value in data_position)
        ):
            hx, hy = int(data_position[0]), int(data_position[1])
        elif hid in HELPER_POSITIONS:
            hx, hy = HELPER_POSITIONS[hid]
        else:
            hx, hy = (300, -200)  # fallback
            print(f"WARNING: No HELPER_POSITIONS for '{hid}' — using fallback ({hx}, {hy})")
        nodes.append(
            {
                "id": hid,
                "label": helper["label"],
                "title": tooltip_text(helper.get("tooltip"), helper.get("title", "")),
                "color": "#546e7a",
                "shape": "diamond",
                "size": 28,
                "font": {"size": 14, "color": "#eee", "bold": True},
                "cluster": "[辅助概念]",
                "nodeType": "helper",
                "x": hx,
                "y": hy,
            }
        )
    return nodes


def build_edges(data: JsonDict) -> list[JsonDict]:
    edges: list[JsonDict] = []
    for edge_data in data["edges"]:
        edges.append(
            {
                "from": edge_data["from"],
                "to": edge_data["to"],
                "title": tooltip_text(edge_data.get("tooltip"), edge_data["label"]),
                "label": edge_data["label"],
                "font": {
                    "size": 10,
                    "color": "#ccd6e0",
                    "align": "horizontal",
                    "background": "rgba(30,30,46,0.55)",
                    "strokeWidth": 0,
                },
                "color": {"color": "#cfd8dc", "highlight": "#ffffff"},
                "width": 1.8,
                "arrows": "to",
                "smooth": {"type": "continuous"},
            }
        )
    for helper in data.get("helpers", []):
        for item in helper.get("connects_to", []):
            edges.append(
                {
                    "from": helper["id"],
                    "to": item,
                    "title": tooltip_text(
                        helper.get("tooltip"),
                        f"辅助概念: {helper['label']} → {item}",
                    ),
                    "label": helper["label"],
                    "font": {
                        "size": 9,
                        "color": "#90a4ae",
                        "align": "horizontal",
                        "background": "rgba(30,30,46,0.45)",
                        "strokeWidth": 0,
                    },
                    "color": {"color": "#78909c", "highlight": "#b0bec5"},
                    "width": 1.5,
                    "arrows": "to",
                    "dashes": [6, 4],
                    "smooth": {"type": "continuous"},
                    "helperEdge": True,
                }
            )
    return edges


def build_network(nodes: list[JsonDict], edges: list[JsonDict]) -> Network:
    net = Network(
        height="980px",
        width="100%",
        directed=True,
        bgcolor="#1e1e2e",
        select_menu=False,
        filter_menu=False,
    )
    net.barnes_hut(
        gravity=-6000,
        central_gravity=0.08,
        spring_length=180,
        spring_strength=0.025,
        damping=0.42,
        overlap=0,
    )
    for node in nodes:
        payload = dict(node)
        node_id = payload.pop("id")
        net.add_node(node_id, **payload)
    for edge in edges:
        payload = dict(edge)
        source = payload.pop("from")
        target = payload.pop("to")
        net.add_edge(source, target, **payload)
    return net


def inject_sidebar(html_path: Path, data: JsonDict, features: JsonDict | None = None) -> None:
    """Inject sidebar HTML/CSS/JS into the PyVis output.

    Sidebar sections are driven by data['sidebar']['sections'].
    JS features are gated by the resolved feature flags dict.
    Uses sidebar_templates module for all HTML/CSS/JS code.
    """
    if features is None:
        features = FEATURE_PROFILES["minimal"]

    html = html_path.read_text(encoding="utf-8")
    patch = build_full_sidebar_html(data, features)
    html = html.replace("</body>", patch)
    html_path.write_text(html, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a mnemonic exploration map")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--data", type=Path, default=DATA_FILE, help="Path to JSON data file")
    parser.add_argument("--open", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    output_path = resolve_output_path(args.data, args.output)
    validate_data(data)
    features = get_features(data)
    nodes = build_nodes(data)
    edges = build_edges(data)
    net = build_network(nodes, edges)
    net.save_graph(str(output_path))
    inject_sidebar(output_path, data, features)
    print(f"→ {output_path}")
    if args.open:
        webbrowser.open(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
