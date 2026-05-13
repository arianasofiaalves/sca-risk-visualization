import json
import math
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D


INPUT_FILE = Path("data/processed/scored_dependencies.json")
OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "risk_grouped_dependency_graph.png"


RISK_COLORS = {
    "HIGH": "salmon",
    "MEDIUM": "gold",
    "LOW": "lightgreen"
}

RISK_SHAPES = {
    "HIGH": "s",
    "MEDIUM": "D",
    "LOW": "h"
}


def format_label(text, width=14):
    """
    Formats labels without breaking words into isolated letters.
    For package names with hyphens, the label may break at the hyphen.
    """
    text = text.replace("", "")

    if "-" in text and len(text) > width:
        parts = text.split("-")
        return "\n".join(parts)

    return "\n".join(
        textwrap.wrap(
            text,
            width=width,
            break_long_words=False,
            break_on_hyphens=False
        )
    )


def place_dependencies(center_x, center_y, risk, dependencies):
    """
    Places dependencies around the project at a similar distance,
    while preserving a general risk direction:
    HIGH = left, MEDIUM = bottom, LOW = right.
    """

    if not dependencies:
        return []

    count = len(dependencies)

    # Slightly increase radius when there are more dependencies
    radius = 3.0 + max(0, count - 2) * 0.25

    angle_ranges = {
        "HIGH": (145, 215),      # left side
        "MEDIUM": (225, 315),    # bottom side
        "LOW": (-55, 55)         # right side
    }

    start_angle, end_angle = angle_ranges[risk]

    if count == 1:
        angles = [(start_angle + end_angle) / 2]
    else:
        angles = [
            start_angle + i * (end_angle - start_angle) / (count - 1)
            for i in range(count)
        ]

    placed = []

    for dependency, angle in zip(dependencies, angles):
        radians = math.radians(angle)
        x = center_x + radius * math.cos(radians)
        y = center_y + radius * math.sin(radians)
        placed.append((dependency, x, y))

    return placed


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    graph = nx.DiGraph()
    positions = {}

    project_nodes = []
    risk_nodes = {
        "HIGH": [],
        "MEDIUM": [],
        "LOW": []
    }

    cluster_centers_by_project = {
    "async_flask": (-8, 4.5),
    "fastapi": (8, 4.5),
    "pipx": (0, -5),
    "requests": (-4, -1),
    "django": (4, -1),
    }

    label_map = {}

    for project in data:
        project_name = project["project"]
        project_label = format_label(project_name, width=14)

        center_x, center_y = cluster_centers_by_project.get(project_name, (0, 0))

        graph.add_node(project_label)
        positions[project_label] = (center_x, center_y)
        project_nodes.append(project_label)
        label_map[project_label] = project_label

        grouped = {
            "HIGH": [],
            "MEDIUM": [],
            "LOW": []
        }

        for dependency in project["dependencies"]:
            grouped[dependency["risk"]].append(dependency)

        for risk in ["HIGH", "MEDIUM", "LOW"]:
            placed_dependencies = place_dependencies(
                center_x,
                center_y,
                risk,
                grouped[risk]
            )

            for dependency, dep_x, dep_y in placed_dependencies:
                dep_name = dependency["name"]
                dep_label = format_label(dep_name, width=14)

                node_id = f"{project_name}:{dep_name}:{risk}"

                graph.add_node(node_id)
                graph.add_edge(project_label, node_id)

                positions[node_id] = (dep_x, dep_y)
                risk_nodes[risk].append(node_id)
                label_map[node_id] = dep_label

    plt.figure(figsize=(17, 10))

    nx.draw_networkx_edges(
        graph,
        positions,
        edge_color="gray",
        arrows=True,
        arrowsize=8,
        alpha=0.25
    )

    nx.draw_networkx_nodes(
        graph,
        positions,
        nodelist=project_nodes,
        node_color="lightblue",
        node_shape="o",
        node_size=3400,
        edgecolors="black",
        linewidths=0.7
    )

    for risk in ["HIGH", "MEDIUM", "LOW"]:
        nx.draw_networkx_nodes(
            graph,
            positions,
            nodelist=risk_nodes[risk],
            node_color=RISK_COLORS[risk],
            node_shape=RISK_SHAPES[risk],
            node_size=3600,
            edgecolors="black",
            linewidths=0.7
        )

    nx.draw_networkx_labels(
        graph,
        positions,
        labels=label_map,
        font_size=5.4,
        font_weight="bold"
    )

    legend_elements = [
        Line2D(
            [0], [0],
            marker="o",
            color="w",
            label="Project",
            markerfacecolor="lightblue",
            markeredgecolor="black",
            markersize=8
        ),
        Line2D(
            [0], [0],
            marker="s",
            color="w",
            label="High risk",
            markerfacecolor=RISK_COLORS["HIGH"],
            markeredgecolor="black",
            markersize=8
        ),
        Line2D(
            [0], [0],
            marker="D",
            color="w",
            label="Medium risk",
            markerfacecolor=RISK_COLORS["MEDIUM"],
            markeredgecolor="black",
            markersize=8
        ),
        Line2D(
            [0], [0],
            marker="h",
            color="w",
            label="Low risk",
            markerfacecolor=RISK_COLORS["LOW"],
            markeredgecolor="black",
            markersize=8
        ),
    ]

    plt.title("Risk-Oriented Dependency Graph by Project", fontsize=16)

    plt.legend(
        handles=legend_elements,
        loc="lower right",
        fontsize=8,
        frameon=False,
        labelspacing=0.6,
        handletextpad=0.6,
        borderpad=0.3
    )

    plt.axis("off")
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"[OK] Risk-grouped dependency graph saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()