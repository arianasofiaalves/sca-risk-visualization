import json
from pathlib import Path

import requests


INPUT_FILE = Path("data/processed/dependencies_summary.json")
OUTPUT_FILE = Path("data/processed/enriched_dependencies.json")

OSV_BATCH_API_URL = "https://api.osv.dev/v1/querybatch"


def extract_severity_labels(vulnerabilities):
    labels = []

    for vulnerability in vulnerabilities:
        database_specific = vulnerability.get("database_specific", {})

        severity = database_specific.get("severity")
        if isinstance(severity, str):
            labels.append(severity.upper())

        for severity_entry in vulnerability.get("severity", []):
            score = severity_entry.get("score", "")
            if "CRITICAL" in score.upper():
                labels.append("CRITICAL")
            elif "HIGH" in score.upper():
                labels.append("HIGH")
            elif "MEDIUM" in score.upper():
                labels.append("MEDIUM")
            elif "LOW" in score.upper():
                labels.append("LOW")

    return labels


def classify_risk(vulnerability_count, severity_labels):

    if vulnerability_count == 0:
        return "LOW"

    if "CRITICAL" in severity_labels:
        return "HIGH"

    if "HIGH" in severity_labels:
        return "HIGH"

    if vulnerability_count >= 3:
        return "HIGH"

    return "MEDIUM"


def build_osv_query(dependency):
    query = {
        "package": {
            "name": dependency["name"],
            "ecosystem": "PyPI"
        }
    }

    if dependency.get("operator") == "==" and dependency.get("version"):
        query["version"] = dependency["version"]

    return query


def query_osv_batch(dependencies):
    queries = [build_osv_query(dependency) for dependency in dependencies]

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

    unique_dependencies = {}

    for project in projects:
        for dependency in project["dependencies"]:
            unique_dependencies[dependency["name"]] = dependency

    dependency_list = list(unique_dependencies.values())
    osv_results = query_osv_batch(dependency_list)

    vulnerability_lookup = {}

    for dependency, result in zip(dependency_list, osv_results):
        vulnerabilities = result.get("vulns", [])
        severity_labels = extract_severity_labels(vulnerabilities)

        risk = classify_risk(
            vulnerability_count=len(vulnerabilities),
            severity_labels=severity_labels
        )

        vulnerability_lookup[dependency["name"]] = {
            "risk": risk,
            "vulnerability_count": len(vulnerabilities),
            "vulnerability_ids": [
                vulnerability.get("id")
                for vulnerability in vulnerabilities
            ],
            "severity_labels": severity_labels
        }

    enriched_projects = []

    for project in projects:
        enriched_dependencies = []

        for dependency in project["dependencies"]:
            vulnerability_data = vulnerability_lookup.get(
                dependency["name"],
                {
                    "risk": "LOW",
                    "vulnerability_count": 0,
                    "vulnerability_ids": [],
                    "severity_labels": []
                }
            )

            enriched_dependencies.append({
                "name": dependency["name"],
                "operator": dependency.get("operator"),
                "version": dependency.get("version"),
                "risk": vulnerability_data["risk"],
                "vulnerability_count": vulnerability_data["vulnerability_count"],
                "vulnerability_ids": vulnerability_data["vulnerability_ids"],
                "severity_labels": vulnerability_data["severity_labels"]
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