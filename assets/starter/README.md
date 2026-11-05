# Electronic component CAD project

This starter has no registered parts. Implement a target using its actual drawings and photographs; do not treat the generator template as a finished model.

```powershell
uv sync --locked --python ">=3.11,<3.14"
uv run --offline python -m component_cad list
```

uv and CPython 3.11–3.13 are required. Any supported minor version can be used; this starter does not include a fixed `.python-version`. The lock records dependencies, including CadQuery 2.8.0. uv can install a compatible Python when permitted.

Read [AGENTS.md](AGENTS.md) and `docs/adding-components.md` (the initializer adds this API guide). Start from the files in `docs/templates/`. Keep manually maintained component notes in `docs/components/` and original references in `references/<part-number>/` here. If `workspace.json` is present, generated outputs go to its configured user project's `models/<part-number>/`; otherwise they go to this standalone library's `models/<part-number>/`.

After registering a real part, run `uv run --offline python -m component_cad build PART-NUMBER`. This generates STEP, GLB, checks and previews. View those images before completing the visual-review record. Replace this introduction with the project's part index as parts are added.
