import subprocess


SCRIPTS = [
    "scripts/extract_deps.py",
    "scripts/enrich.py",
    "scripts/score_risk.py",
    "scripts/build_graph.py",
    "scripts/generate_stats.py"
]


def run_script(script_path):
    print(f"\n[RUNNING] {script_path}")

    result = subprocess.run(
        ["python", script_path],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.stderr:
        print("[ERROR]")
        print(result.stderr)


def main():
    print("=== SCA RISK VISUALIZATION PIPELINE ===")

    for script in SCRIPTS:
        run_script(script)

    print("\n[OK] Pipeline execution completed.")


if __name__ == "__main__":
    main()