import json
from collections import Counter
from pathlib import Path


INPUT_FILE = Path("data/processed/scored_dependencies.json")
OUTPUT_FILE = Path("data/processed/summary_statistics.json")


def main():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    total_projects = len(data)
    total_dependencies = 0

    risk_distribution = Counter()
    dependency_frequency = Counter()

    for project in data:
        dependencies = project["dependencies"]

        total_dependencies += len(dependencies)

        for dependency in dependencies:
            risk_distribution[dependency["risk"]] += 1
            dependency_frequency[dependency["name"]] += 1

    average_dependencies = (
        total_dependencies / total_projects
        if total_projects > 0
        else 0
    )

    top_dependencies = dependency_frequency.most_common(5)

    statistics = {
        "total_projects_analyzed": total_projects,
        "total_dependencies": total_dependencies,
        "average_dependencies_per_project": round(average_dependencies, 2),
        "risk_distribution": {
            "LOW": risk_distribution.get("LOW", 0),
            "MEDIUM": risk_distribution.get("MEDIUM", 0),
            "HIGH": risk_distribution.get("HIGH", 0)
        },
        "top_dependencies": [
            {
                "name": name,
                "count": count
            }
            for name, count in top_dependencies
        ]
    }

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(statistics, file, indent=4)

    print("\n[OK] Summary statistics generated:\n")
    print(json.dumps(statistics, indent=4))


if __name__ == "__main__":
    main()