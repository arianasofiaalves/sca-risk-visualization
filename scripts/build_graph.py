import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx


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


def shorten_label(text, max_len=13):
    return text if len(text) <= max_len else text[:max_len - 3] + "..."


def place_group(center_x, center_y, risk, dependencies):
    """
    Places dependencies around a project while preserving a general direction:
    HIGH to the left, MEDIUM below, LOW to the right.
    Dependencies are spread in a small fan to avoid overlap.
    """

    count = len(dependencies)
    positions = []

    if count == 0:
        return positions

    if risk == "HIGH":
        base_x = center_x - 2.6
        base_y = center_y
        spread_x = 0.0
        spread_y = 1.0

    elif risk == "MEDIUM":
        base_x = center_x
        base_y = center_y - 2.4
        spread_x = 1.1
        spread_y = 0.55

    else:  # LOW
        base_x = center_x + 2.6
        base_y = center_y
        spread_x = 0.75
        spread_y = 1.0

    middle = (count - 1) / 2

    for i, dependency in enumerate(dependencies):
        offset = i - middle

        if risk == "HIGH":
            x = base_x
            y = base_y - offset * spread_y

        elif risk == "MEDIUM":
            x = base_x + offset * spread_x
            y = base_y - abs(offset) * spread_y

        else:  # LOW
            x = base_x + abs(offset) * spread_x
            y = base_y - offset * spread_y

        positions.append((dependency, x, y))

    return positions


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

    # Clusters closer together to reduce blank space
    cluster_centers = [
        (-4.8, 3.2),
        (4.8, 3.2),
        (0, -2.3),
        (-4.8, -7.8),
        (4.8, -7.8)
    ]

    for project_index, project in enumerate(data):
        project_label = shorten_label(project["project"])
        center_x, center_y = cluster_centers[project_index]

        graph.add_node(project_label)
        project_nodes.append(project_label)
        positions[project_label] = (center_x, center_y)

        grouped = {
            "HIGH": [],
            "MEDIUM": [],
            "LOW": []
        }

        for dependency in project["dependencies"]:
            grouped[dependency["risk"]].append(dependency)

        for risk in ["HIGH", "MEDIUM", "LOW"]:
            placed_dependencies = place_group(
                center_x,
                center_y,
                risk,
                grouped[risk]
            )

            for dependency, dep_x, dep_y in placed_dependencies:
                dep_label = f"{shorten_label(dependency['name'])}\n{risk}"

                graph.add_node(dep_label)
                graph.add_edge(project_label, dep_label)

                positions[dep_label] = (dep_x, dep_y)
                risk_nodes[risk].append(dep_label)

    plt.figure(figsize=(15, 9))

    nx.draw_networkx_edges(
        graph,
        positions,
        edge_color="gray",
        arrows=True,
        arrowsize=8,
        alpha=0.3
    )

    nx.draw_networkx_nodes(
        graph,
        positions,
        nodelist=project_nodes,
        node_color="lightblue",
        node_shape="o",
        node_size=2600,
        edgecolors="black",
        linewidths=0.7,
        label="Project"
    )

    for risk in ["HIGH", "MEDIUM", "LOW"]:
        nx.draw_networkx_nodes(
            graph,
            positions,
            nodelist=risk_nodes[risk],
            node_color=RISK_COLORS[risk],
            node_shape=RISK_SHAPES[risk],
            node_size=2300,
            edgecolors="black",
            linewidths=0.7,
            label=f"{risk.title()} risk"
        )

    nx.draw_networkx_labels(
        graph,
        positions,
        font_size=6,
        font_weight="bold"
    )

    plt.title("Risk-Oriented Dependency Graph by Project", fontsize=16)

    plt.legend(
    loc="lower right",
    fontsize=6,
    frameon=False,
    markerscale=0.4
    )

    plt.axis("off")
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"[OK] Risk-grouped dependency graph saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()