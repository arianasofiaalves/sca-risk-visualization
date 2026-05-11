import json
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
    node_colors = {}
    positions = {}

    y_gap = 4
    x_project = 0
    x_dependency = 4

    for project_index, project in enumerate(data):
        project_name = project["project"]
        project_y = -project_index * y_gap

        graph.add_node(project_name)
        positions[project_name] = (x_project, project_y)
        node_colors[project_name] = "lightblue"

        dependencies = project["dependencies"]

        for dep_index, dependency in enumerate(dependencies):
            dep_name = dependency["name"]
            risk = dependency["risk"]

            label = f"{dep_name}\n({risk})"

            # Spread dependencies vertically around their project
            dep_y = project_y + (len(dependencies) / 2) - dep_index

            graph.add_node(label)
            graph.add_edge(project_name, label)

            positions[label] = (x_dependency, dep_y)
            node_colors[label] = RISK_COLORS.get(risk, "lightgray")

    colors = [node_colors[node] for node in graph.nodes()]

    plt.figure(figsize=(18, 10))

    nx.draw(
        graph,
        positions,
        with_labels=True,
        node_color=colors,
        node_size=2800,
        font_size=8,
        font_weight="bold",
        arrows=True,
        edge_color="gray",
        arrowsize=15
    )

    plt.title("Dependency Risk Graph by Project", fontsize=16)
    plt.axis("off")
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"[OK] Dependency graph saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()