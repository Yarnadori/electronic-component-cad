"""Export, validate and document any catalog part using its family generator."""
import hashlib
import importlib
import json
import os
from pathlib import Path
from .core import ROOT
from .validation import verify_step
import cadquery as cq


def _report(part, family, parts, step):
    geometry = verify_step(parts, step, part.expected_solids, part.model_name)
    dimensions = family.verify_dimensions(parts, part)
    return {**geometry, **dimensions, "checks": geometry["checks"]+dimensions["checks"],
            "part_number": part.part_number, "model": part.model_name, "units": "mm",
            "cadquery_version": cq.__version__, "source": part.source,
            "source_revision": part.source_revision, "source_page": part.source_page,
            "source_sha256": hashlib.sha256((ROOT / part.source).read_bytes()).hexdigest(),
            "variant": part.details}


def _write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")


def _step_path(part, output_root):
    return part.output_dir(output_root) / (part.model_name+".step")


def _require_step(part, output_root):
    step = _step_path(part, output_root)
    if not step.is_file():
        raise FileNotFoundError(f"STEP not found: {step}. Run build for {part.part_number} first.")
    return step


def build_part(part, output_root=None, *, preview=True):
    family = importlib.import_module(part.module)
    assembly, parts = family.build(part)
    # Check dimensions before writing; roundtrip checks necessarily follow export.
    family.verify_dimensions(parts, part)
    out = part.output_dir(output_root)
    out.mkdir(parents=True, exist_ok=True)
    step = _step_path(part, output_root)
    assembly.export(str(step), "STEP")
    report = _report(part, family, parts, step)
    _write_json(out / "validation.json", report)
    _write_json(out / "metadata.json", {**part.to_dict(), "units": "mm", "step_sha256": report["step_sha256"]})
    assembly.export(str(out / (part.model_name+".glb")), "GLTF", tolerance=0.02)
    if part.export_stl:
        cq.exporters.export(assembly.toCompound(), str(out / (part.model_name+".stl")), tolerance=0.02)
    source = ROOT / (part.module.replace(".", "/")+".py")
    def link(path):
        try:
            return Path(os.path.relpath(path, out)).as_posix()
        except ValueError:  # Different Windows drives: keep a valid absolute file path.
            return Path(path).resolve().as_posix()
    preview_line = "- [STEPから描画したプレビュー](preview.png)\n" if preview else ""
    readme = (f"# {part.part_number}\n\n"
              f"- [色付きSTEP]({step.name})\n"
              f"- [色付きGLB]({part.model_name}.glb)\n"+preview_line+
              f"- [寸法・座標・近似範囲]({link(ROOT / part.documentation)})\n"
              f"- [CadQueryソース]({link(source)})\n"
              "- [型番情報](metadata.json) / [検証結果](validation.json)\n\n"
              f"出典：{part.source_revision}、{part.source_page}ページ。"
              f"{report['solid_count']}ソリッド、{len(report['checks'])}項目を検証。単位mm、倍率1。\n\n"
              f"再生成：`uv run --offline python -m akicad_3d build {part.part_number}`\n")
    (out / "README.md").write_text(readme, encoding="utf-8")
    if preview:
        render_part(part, output_root)
    return {"part": part.part_number, "step": str(step), "solid_count": report["solid_count"],
            "checks_passed": len(report["checks"]), "preview": preview}


def validate_part(part, output_root=None):
    step = _require_step(part, output_root)
    family = importlib.import_module(part.module)
    _, parts = family.build(part)
    report = _report(part, family, parts, step)
    _write_json(step.parent / "validation.json", report)
    return {"part": part.part_number, "solid_count": report["solid_count"],
            "checks_passed": len(report["checks"]), "step_sha256": report["step_sha256"]}


def render_part(part, output_root=None):
    step = _require_step(part, output_root)
    from .rendering import render_previews
    family = importlib.import_module(part.module)
    return render_previews(part, step, family.preview_spec(part))
