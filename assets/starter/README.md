# Electronic component CAD project

This starter has no registered parts. Implement a target using its actual drawings and photographs; do not treat the generator template as a finished model.

```powershell
uv sync --locked
uv run --offline python -m akicad_3d list
```

Read [AGENTS.md](AGENTS.md) and `docs/adding-components.md` (the initializer adds this API guide). Start from the files in `docs/templates/`. Keep manually maintained component notes in `docs/components/`, original references in `references/<part-number>/`, and generated outputs in `models/<part-number>/`.

After registering a real part, run `uv run --offline python -m akicad_3d build PART-NUMBER`. This generates STEP, GLB, checks and previews. View those images before completing the visual-review record. Replace this introduction with the project's part index as parts are added.
