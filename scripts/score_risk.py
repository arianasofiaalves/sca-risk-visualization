import json
from pathlib import Path


INPUT_FILE = Path("data/processed/enriched_dependencies.json")
OUTPUT_FILE = Path("data/processed/scored_dependencies.json")


RISK_SCORES = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3
}


def main():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    scored_data = []

    for project in data:
        scored_dependencies = []

        for dependency in project["dependencies"]:
            risk = dependency["risk"]
            risk_score = RISK_SCORES.get(risk, 0)

            scored_dependency = {
                "name": dependency["name"],
                "risk": risk,
                "risk_score": risk_score,
                "vulnerability_count": dependency.get("vulnerability_count", 0),
                "vulnerability_ids": dependency.get("vulnerability_ids", [])
            }

            scored_dependencies.append(scored_dependency)

        scored_data.append({
            "project": project["project"],
            "dependencies": scored_dependencies
        })

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(scored_data, file, indent=4)

    print(f"[OK] Risk scoring completed. Output saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()