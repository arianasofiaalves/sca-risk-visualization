import json
import re
from pathlib import Path


RAW_DIR = Path("data/raw_requirements")
OUTPUT_DIR = Path("data/processed")


VERSION_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)\s*(==|>=|<=|~=|>|<|!=)?\s*([^;\s]+)?")


def parse_dependency(line: str):
    line = line.strip()

    if not line or line.startswith("#"):
        return None

    if line.startswith("-r") or line.startswith("--"):
        return None

    line = line.split("#")[0].strip()
    line = re.sub(r"\[.*?\]", "", line)

    match = VERSION_PATTERN.match(line)

    if not match:
        return None

    name = match.group(1).lower()
    operator = match.group(2)
    version = match.group(3)

    return {
        "name": name,
        "operator": operator,
        "version": version
    }


def parse_requirements_file(file_path: Path):
    dependencies = []
    seen = set()

    with file_path.open("r", encoding="utf-8") as file:
        for line in file:
            dependency = parse_dependency(line)

            if dependency and dependency["name"] not in seen:
                dependencies.append(dependency)
                seen.add(dependency["name"])

    return dependencies


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    for req_file in RAW_DIR.glob("*.txt"):
        project_name = req_file.stem.replace("_requirements", "")
        dependencies = parse_requirements_file(req_file)

        project_result = {
            "project": project_name,
            "source_file": str(req_file),
            "dependency_count": len(dependencies),
            "dependencies": dependencies
        }

        results.append(project_result)

        output_file = OUTPUT_DIR / f"{project_name}_dependencies.json"

        with output_file.open("w", encoding="utf-8") as file:
            json.dump(project_result, file, indent=4)

        print(f"[OK] {project_name}: {len(dependencies)} dependencies extracted")

    summary_file = OUTPUT_DIR / "dependencies_summary.json"

    with summary_file.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    print(f"\nSummary saved to {summary_file}")


if __name__ == "__main__":
    main()