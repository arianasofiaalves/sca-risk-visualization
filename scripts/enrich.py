import json
import random
from pathlib import Path


INPUT_FILE = "data/processed/dependencies_summary.json"
OUTPUT_FILE = "data/processed/enriched_dependencies.json"


def assign_risk(dep_name):
    # versão simples (mock)
    return random.choice(["LOW", "MEDIUM", "HIGH"])


def main():
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    enriched_data = []

    for project in data:
        new_deps = []

        for dep in project["dependencies"]:
            new_deps.append({
                "name": dep,
                "risk": assign_risk(dep)
            })

        enriched_data.append({
            "project": project["project"],
            "dependencies": new_deps
        })

    with open(OUTPUT_FILE, "w") as f:
        json.dump(enriched_data, f, indent=4)

    print("Enriched data saved!")


if __name__ == "__main__":
    main()