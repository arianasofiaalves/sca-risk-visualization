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
    node_colors = []

    for project in data:
        project_name = project["project"]
        graph.add_node(project_name, node_type="project", risk="PROJECT")

        for dependency in project["dependencies"]:
            dep_name = dependency["name"]
            risk = dependency["risk"]
            label = f"{dep_name}\n({risk})"

            graph.add_node(label, node_type="dependency", risk=risk)
            graph.add_edge(project_name, label)

    for node in graph.nodes(data=True):
        node_type = node[1].get("node_type")
        risk = node[1].get("risk")

        if node_type == "project":
            node_colors.append("lightblue")
        else:
            node_colors.append(RISK_COLORS.get(risk, "lightgray"))

    plt.figure(figsize=(18, 12))

    pos = nx.spring_layout(graph, seed=42, k=1.8)

    nx.draw(
        graph,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=3200,
        font_size=9,
        font_weight="bold",
        arrows=True,
        edge_color="gray"
    )

    plt.title("Dependency Risk Graph", fontsize=16)
    plt.savefig(OUTPUT_FILE, dpi=300)
    plt.close()

    print(f"[OK] Dependency graph saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()