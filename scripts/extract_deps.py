import json
import re
from pathlib import Path


RAW_DIR = Path("data/raw_requirements")
OUTPUT_DIR = Path("data/processed")


def normalize_dependency(line: str) -> str | None:

    line = line.strip()

    if not line or line.startswith("#"):
        return None

    if line.startswith("-r") or line.startswith("--"):
        return None

    line = line.split("#")[0].strip()
    line = re.sub(r"\[.*?\]", "", line)

    package_name = re.split(r"==|>=|<=|~=|>|<|!=", line)[0].strip()

    if not package_name:
        return None

    return package_name.lower()


def parse_requirements_file(file_path: Path) -> list[str]:
    dependencies = []

    with file_path.open("r", encoding="utf-8") as file:
        for line in file:
            dependency = normalize_dependency(line)
            if dependency:
                dependencies.append(dependency)

    return sorted(set(dependencies))


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_results = []

    for requirements_file in RAW_DIR.glob("*.txt"):
        project_name = requirements_file.stem.replace("_requirements", "")
        dependencies = parse_requirements_file(requirements_file)

        result = {
            "project": project_name,
            "source_file": str(requirements_file),
            "dependency_count": len(dependencies),
            "dependencies": dependencies,
        }

        all_results.append(result)

        output_file = OUTPUT_DIR / f"{project_name}_dependencies.json"
        with output_file.open("w", encoding="utf-8") as file:
            json.dump(result, file, indent=4)

        print(f"[OK] {project_name}: {len(dependencies)} dependencies extracted")

    summary_file = OUTPUT_DIR / "dependencies_summary.json"
    with summary_file.open("w", encoding="utf-8") as file:
        json.dump(all_results, file, indent=4)

    print(f"\nSummary saved to {summary_file}")


if __name__ == "__main__":
    main()