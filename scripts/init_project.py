"""Prepare a persistent CAD workspace outside the user's project by default."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys


def initialize(destination):
    """Explicit standalone mode: copy the starter without overwriting anything."""
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


def data_directory():
    override = os.environ.get("ELECTRONIC_COMPONENT_CAD_HOME")
    if override:
        return Path(override).expanduser().resolve()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()/"AppData/Local"))
    elif sys.platform == "darwin":
        base = Path.home()/"Library/Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home()/".local/share"))
    return (base/"electronic-component-cad").resolve()


def prepare_workspace(project):
    """Reuse one private workspace per resolved project path; never migrate files."""
    project = Path(project).expanduser().resolve()
    skill = Path(__file__).resolve().parents[1]
    if project == skill or skill in project.parents:
        raise ValueError("Choose a project directory outside the installed skill")
    if project.exists() and not project.is_dir():
        raise ValueError("The project path must be a directory")
    base = data_directory()
    if base == project or project in base.parents:
        raise ValueError("The CAD data directory must be outside the user project")
    identity = hashlib.sha256(os.path.normcase(str(project)).encode("utf-8")).hexdigest()[:24]
    workspace = base/"workspaces"/identity
    output = project/"models"
    settings = {"kind": "electronic-component-cad", "schema": 1,
                "project_directory": str(project), "output_directory": str(output)}
    marker = workspace/"workspace.json"
    created = not workspace.exists()
    if not created:
        if not marker.is_file() or json.loads(marker.read_text(encoding="utf-8")) != settings:
            raise ValueError("Existing workspace is unrecognized or belongs to another project; no files changed")
        if not all((workspace/name).is_file() for name in
                   ("pyproject.toml", "uv.lock", "component_cad/core.py", "component_cad/catalog.py")):
            raise ValueError("Existing workspace is incomplete; no files changed")
    else:
        initialize(workspace)
        with marker.open("x", encoding="utf-8") as stream:
            json.dump(settings, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
    project.mkdir(parents=True, exist_ok=True)
    return {"project_directory": str(project), "workspace": str(workspace),
            "output_directory": str(output), "created": created}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", help="User project directory (may contain existing files)")
    parser.add_argument("--standalone", action="store_true",
                        help="Explicitly scaffold a new/empty CAD library in the destination")
    parser.add_argument("--json", action="store_true", help="Return workspace paths for the calling agent")
    args = parser.parse_args()
    try:
        if args.standalone:
            destination, count = initialize(args.destination)
            result = {"workspace": str(destination), "output_directory": str(destination/"models"),
                      "created": True, "files_created": count}
        else:
            result = prepare_workspace(args.destination)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Initialization stopped: {exc}\n")
    if args.json:
        print(json.dumps(result, ensure_ascii=True))
    else:
        print(f"Workspace: {result['workspace']}")
        print(f"Outputs: {result['output_directory']}")
        print("Run uv sync --locked inside the workspace, then read its AGENTS.md")


if __name__ == "__main__":
    main()
