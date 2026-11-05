"""Copy the portable CAD starter into a new or empty directory; never overwrite."""
import argparse
from pathlib import Path
import shutil


def initialize(destination):
    skill = Path(__file__).resolve().parents[1]
    source = skill / "assets" / "starter"
    destination = Path(destination).expanduser().resolve()
    if destination == skill or skill in destination.parents:
        raise ValueError("Choose a project directory outside the installed skill")
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError("Destination must be new or empty; existing projects must keep their own pipeline")
    files = [p for p in source.rglob("*") if p.is_file()
             and not any(part in (".git", ".venv", ".uv-cache", "__pycache__") for part in p.relative_to(source).parts)
             and p.suffix != ".pyc"]
    if not files or not (source / "uv.lock").is_file():
        raise ValueError("Starter assets are incomplete")
    destination.mkdir(parents=True, exist_ok=True)
    for path in files:
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        with path.open("rb") as src, target.open("xb") as dst:
            shutil.copyfileobj(src, dst)
    for origin, relative in ((skill / "references/project-api.md", "docs/adding-components.md"),
                             (skill / "LICENSE", "LICENSE")):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with origin.open("rb") as src, target.open("xb") as dst:
            shutil.copyfileobj(src, dst)
    return destination, len(files)+2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", help="New or empty CAD project directory")
    args = parser.parse_args()
    try:
        destination, count = initialize(args.destination)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Initialization stopped: {exc}\n")
    print(f"Created {count} starter files in {destination}")
    print("Next: cd into that directory, run uv sync --locked, then read AGENTS.md")


if __name__ == "__main__":
    main()
