import json
from pathlib import Path

import requests


INPUT_FILE = Path("data/processed/dependencies_summary.json")
OUTPUT_FILE = Path("data/processed/enriched_dependencies.json")

OSV_BATCH_API_URL = "https://api.osv.dev/v1/querybatch"


def classify_risk(vulnerability_count):
    if vulnerability_count == 0:
        return "LOW"
    if vulnerability_count == 1:
        return "MEDIUM"
    return "HIGH"


def query_osv_batch(package_names):
    queries = [
        {
            "package": {
                "name": package_name,
                "ecosystem": "PyPI"
            }
        }
        for package_name in package_names
    ]

    response = requests.post(
        OSV_BATCH_API_URL,
        json={"queries": queries},
        timeout=30
    )

    response.raise_for_status()
    return response.json().get("results", [])


def main():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        projects = json.load(file)

    all_package_names = sorted({
        dependency
        for project in projects
        for dependency in project["dependencies"]
    })

    osv_results = query_osv_batch(all_package_names)

    vulnerability_lookup = {}

    for package_name, result in zip(all_package_names, osv_results):
        vulnerabilities = result.get("vulns", [])
        vulnerability_lookup[package_name] = {
            "vulnerability_count": len(vulnerabilities),
            "vulnerability_ids": [
                vulnerability.get("id")
                for vulnerability in vulnerabilities
            ],
            "risk": classify_risk(len(vulnerabilities))
        }

    enriched_projects = []

    for project in projects:
        enriched_dependencies = []

        for dependency in project["dependencies"]:
            vulnerability_data = vulnerability_lookup.get(
                dependency,
                {
                    "vulnerability_count": 0,
                    "vulnerability_ids": [],
                    "risk": "LOW"
                }
            )

            enriched_dependencies.append({
                "name": dependency,
                "risk": vulnerability_data["risk"],
                "vulnerability_count": vulnerability_data["vulnerability_count"],
                "vulnerability_ids": vulnerability_data["vulnerability_ids"]
            })

        enriched_projects.append({
            "project": project["project"],
            "dependencies": enriched_dependencies
        })

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(enriched_projects, file, indent=4)

    print("[OK] Enriched data saved using OSV vulnerability data.")


if __name__ == "__main__":
    main()