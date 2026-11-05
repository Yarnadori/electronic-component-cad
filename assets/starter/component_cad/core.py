"""Shared model descriptors; no CAD imports required to inspect the catalog."""
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import os
import json

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".uv-cache"))


def default_output_root():
    marker = ROOT / "workspace.json"
    if not marker.is_file():
        return ROOT / "models"
    settings = json.loads(marker.read_text(encoding="utf-8"))
    if settings.get("kind") != "electronic-component-cad" or settings.get("schema") != 1:
        raise ValueError("Unsupported workspace configuration")
    output = Path(settings["output_directory"])
    if not output.is_absolute():
        raise ValueError("Workspace output directory must be absolute")
    return output


@dataclass(frozen=True)
class Part:
    part_number: str
    manufacturer: str
    family: str
    model_name: str
    module: str
    source: str
    source_revision: str
    source_page: int
    documentation: str
    expected_solids: int
    details: dict[str, Any] = field(default_factory=dict)
    export_stl: bool = False

    @property
    def output_subdir(self):
        return Path(self.part_number)

    def output_dir(self, root=None):
        return Path(root if root is not None else default_output_root()) / self.output_subdir

    def to_dict(self):
        return {**asdict(self), "output_subdir": self.output_subdir.as_posix()}


@dataclass(frozen=True)
class View:
    name: str
    camera: tuple[float, float, float]
    scale: float
    focal_point: tuple[float, float, float]
    up: tuple[float, float, float] = (0, 0, 1)


@dataclass(frozen=True)
class PreviewSpec:
    title: str
    subtitle: str
    views: tuple[View, ...]
    notes: tuple[str, ...]
