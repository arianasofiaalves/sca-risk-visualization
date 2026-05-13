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
    "LOW": "lightgreen",
}

RISK_SHAPES = {
    "HIGH": "s",
    "MEDIUM": "D",
    "LOW": "h",
}


def format_label(text, width=13):
    text = text.replace("", " ")
    text = text.replace("-", "- ")

    return "\n".join(
        textwrap.wrap(
            text,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


def place_dependencies(center_x, center_y, risk, dependencies):
    if not dependencies:
        return []

    count = len(dependencies)

    radius = 4.2 + max(0, count - 2) * 0.45

    angle_ranges = {
        "HIGH": (140, 220),
        "MEDIUM": (230, 310),
        "LOW": (-75, 75),
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
    labels = {}

    project_nodes = []

    risk_nodes = {
        "HIGH": [],
        "MEDIUM": [],
        "LOW": [],
    }

    cluster_centers_by_project = {
        "requests": (10, 8.4),
        "pipx": (-11.5, 6.8),
        "async_flask": (1.2, 1.5),
        "fastapi": (-8, -6.0),
        "django": (11, -6.2),
    }

    for project in data:

        project_name = project["project"]
        project_label = f"project::{project_name}"

        center_x, center_y = cluster_centers_by_project.get(
            project_name,
            (0, 0)
        )

        graph.add_node(project_label)

        positions[project_label] = (center_x, center_y)

        labels[project_label] = format_label(project_name)

        project_nodes.append(project_label)

        grouped = {
            "HIGH": [],
            "MEDIUM": [],
            "LOW": [],
        }

        for dependency in project["dependencies"]:
            grouped[dependency["risk"]].append(dependency)

        for risk in ["HIGH", "MEDIUM", "LOW"]:

            placed_dependencies = place_dependencies(
                center_x,
                center_y,
                risk,
                grouped[risk],
            )

            for dependency, dep_x, dep_y in placed_dependencies:

                dep_name = dependency["name"]

                dep_node = f"{project_name}::{dep_name}::{risk}"

                graph.add_node(dep_node)

                graph.add_edge(project_label, dep_node)

                positions[dep_node] = (dep_x, dep_y)

                labels[dep_node] = format_label(dep_name)

                risk_nodes[risk].append(dep_node)

    plt.figure(figsize=(20, 12))

    nx.draw_networkx_edges(
        graph,
        positions,
        edge_color="gray",
        arrows=True,
        arrowsize=8,
        alpha=0.22,
    )

    nx.draw_networkx_nodes(
        graph,
        positions,
        nodelist=project_nodes,
        node_color="lightblue",
        node_shape="o",
        node_size=5600,
        edgecolors="black",
        linewidths=0.7,
    )

    for risk in ["HIGH", "MEDIUM", "LOW"]:

        if risk == "MEDIUM":
            current_size = 4700
        else:
            current_size = 5800

        nx.draw_networkx_nodes(
            graph,
            positions,
            nodelist=risk_nodes[risk],
            node_color=RISK_COLORS[risk],
            node_shape=RISK_SHAPES[risk],
            node_size=current_size,
            edgecolors="black",
            linewidths=0.7,
        )

    nx.draw_networkx_labels(
        graph,
        positions,
        labels=labels,
        font_size=6.8,
        font_weight="bold",
    )

    legend_elements = [
        Line2D(
            [0], [0],
            marker="o",
            color="w",
            label="Project",
            markerfacecolor="lightblue",
            markeredgecolor="black",
            markersize=11,
        ),
        Line2D(
            [0], [0],
            marker="s",
            color="w",
            label="High risk",
            markerfacecolor=RISK_COLORS["HIGH"],
            markeredgecolor="black",
            markersize=11,
        ),
        Line2D(
            [0], [0],
            marker="D",
            color="w",
            label="Medium risk",
            markerfacecolor=RISK_COLORS["MEDIUM"],
            markeredgecolor="black",
            markersize=10,
        ),
        Line2D(
            [0], [0],
            marker="h",
            color="w",
            label="Low risk",
            markerfacecolor=RISK_COLORS["LOW"],
            markeredgecolor="black",
            markersize=11,
        ),
    ]

    plt.title(
        "Risk-Oriented Dependency Graph by Project",
        fontsize=18
    )

    plt.legend(
        handles=legend_elements,
        loc="lower right",
        fontsize=10,
        frameon=False,
        labelspacing=0.5,
        handletextpad=0.5,
    )

    plt.axis("off")

    plt.savefig(
        OUTPUT_FILE,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"[OK] Risk-grouped dependency graph saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()