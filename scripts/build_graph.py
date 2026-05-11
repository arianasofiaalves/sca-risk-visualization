import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx


INPUT_FILE = Path("data/processed/scored_dependencies.json")
OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "dependency_graph.png"


RISK_COLORS = {
    "LOW": "lightgreen",
    "MEDIUM": "gold",
    "HIGH": "salmon"
}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    graph = nx.DiGraph()
    positions = {}
    node_colors = {}

    # Fixed centers for each project cluster
    cluster_centers = [
        (-5, 4),
        (5, 4),
        (0, -4),
        (-5, -12),
        (5, -12),
    ]

    dependency_radius = 2.4

    for project_index, project in enumerate(data):
        project_name = project["project"]
        center_x, center_y = cluster_centers[project_index]

        graph.add_node(project_name)
        positions[project_name] = (center_x, center_y)
        node_colors[project_name] = "lightblue"

        dependencies = project["dependencies"]
        total_deps = len(dependencies)

        for dep_index, dependency in enumerate(dependencies):
            dep_name = dependency["name"]
            risk = dependency["risk"]
            label = f"{dep_name}\n({risk})"

            angle = 2 * math.pi * dep_index / total_deps
            dep_x = center_x + dependency_radius * math.cos(angle)
            dep_y = center_y + dependency_radius * math.sin(angle)

            graph.add_node(label)
            graph.add_edge(project_name, label)

            positions[label] = (dep_x, dep_y)
            node_colors[label] = RISK_COLORS.get(risk, "lightgray")

    colors = [node_colors[node] for node in graph.nodes()]

    plt.figure(figsize=(16, 12))

    nx.draw_networkx_edges(
        graph,
        positions,
        edge_color="gray",
        arrows=True,
        arrowsize=12,
        alpha=0.45
    )

    nx.draw_networkx_nodes(
        graph,
        positions,
        node_color=colors,
        node_size=2300,
        edgecolors="black",
        linewidths=0.6
    )

    nx.draw_networkx_labels(
        graph,
        positions,
        font_size=7,
        font_weight="bold"
    )

    plt.title("Dependency Risk Graph by Project Cluster", fontsize=16)
    plt.axis("off")
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"[OK] Dependency graph saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()