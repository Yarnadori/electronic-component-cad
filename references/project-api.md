# Project setup and component API

Use an existing project's API when one is present. This document describes the **included starter**; it does not assume another repository or personal absolute path.

## Start in an empty directory

Run the initializer with any Python 3.11+ interpreter, replacing the two paths:

```text
python /path/to/electronic-component-cad/scripts/init_project.py /path/to/new-cad-project
```

Then run the following **inside the generated project**:

```powershell
uv sync --locked
uv run --offline python -c "import cadquery as cq; print(cq.__version__); print(cq.Workplane('XY').box(1, 2, 3).val().Volume())"
uv run --offline python -m akicad_3d list
```

The bundled lock uses Python 3.11 and CadQuery 2.8.0. The volume check should report 6.0. The initial catalog is intentionally empty. A first sync may download Python/dependencies; `--offline` is for an installed environment or populated cache. Do not copy another machine's `.venv` or re-run `uv init` in an existing project.

PDF rasterization needs a separate Poppler installation (`pdfinfo`, `pdftoppm`), or an available equivalent. VTK/Pillow handle STEP previews. The starter tries Arial, DejaVu Sans, then Pillow's fallback font. Headless rendering and other operating systems require verification in the target environment; the supplied workflow has been exercised on Windows only.

## Implement a part

Copy `docs/templates/component.py` to `akicad_3d/components/<module>.py` or a manufacturer subpackage with `__init__.py`. Fill the three public functions:

| Function | Contract |
| --- | --- |
| `build(part)` | Return `(cq.Assembly, {name: (cq.Workplane, (r,g,b))})`. Use `part.model_name` for the assembly name. |
| `verify_dimensions(parts, part)` | Assert independent drawing expectations, return a dictionary containing a nonempty `checks` list and relevant measurements. |
| `preview_spec(part)` | Return `PreviewSpec(title, subtitle, views, notes)`. Each view is `View(name, camera, scale, focal_point, up=(0,0,1))`. |

Part names must be unique and contain no `/`. RGB values are in 0..1. Count **all solids**, not just dictionary entries. Compound geometry is allowed when intentional and validated. The common pipeline rejects inter-part volume overlap; model cavities explicitly when a metal part sits inside a housing.

Add a `Part` to the tuple returned by `akicad_3d/catalog.py::_parts()`. The following is an illustrative registration to replace with real evidence, not a supplied part:

```python
Part(
    part_number="PART-123", manufacturer="maker", family="part123",
    model_name="PART-123", module="akicad_3d.components.part123",
    source="references/PART-123/drawing.pdf",
    source_revision="revision printed on the drawing", source_page=1,
    documentation="docs/components/part123.md", expected_solids=3,
    details={"application": "PCB connector"},
)
```

Use the actual source's revision, or explicitly record that none is printed. Source and documentation paths are project-relative. `expected_solids=3` above is only an example. Derive the real count from the target's intended construction. `export_stl=True` optionally adds STL; STEP remains primary.

Copy and complete the component-notes, reference-notes and visual-review templates. Their unfilled status is intentional. Keep editable component notes in `docs/components/`; `models/<part>/README.md` is generated and may be replaced by `build`.

## Build, validate and render

Replace `PART-123` after registration:

```powershell
uv run --offline python -m akicad_3d build PART-123
uv run --offline python -m akicad_3d validate PART-123
uv run --offline python -m akicad_3d render PART-123
```

`build` checks dimensions, exports STEP/GLB, validates STEP and renders previews. `validate` rebuilds the source geometry in memory, compares it to the existing STEP and writes a validation report. `render` reads existing STEP; it does not apply Python geometry edits.

Use `--output-dir scratch/models` on all related commands to isolate trials. The part-number directory is appended automatically. `--no-preview` skips rendering and leaves visual review outstanding. `--family` and `--all` select multiple registered parts; avoid rebuilding unrelated models without a reason.

Inspect `validation.json` for results, not only process exit status. Compare its `step_sha256` with `metadata.json`, `render-validation.json` and the written visual review. View every final image needed for the part. If a view is clipped, change its `scale`/focal point and rerun `render`; a geometry change requires `build` again.
