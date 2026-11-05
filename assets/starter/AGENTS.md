# Electronic component CAD project

- Read README.md and docs/adding-components.md before editing. Preserve existing models and user changes.
- This directory is the agent's working environment. When workspace.json is present, keep all code, references, plans and dependencies here; only model outputs go to its configured user project. Do not expose internal paths/module names in normal user-facing notes or replies.
- Use CadQuery with the uv lock. Generate named/material-colored STEP assemblies and editable source.
- Use CPython 3.11–3.13; no minor version is pinned. Run `uv sync --locked --python ">=3.11,<3.14"` in this workspace to select a compatible runtime, then use its environment for all commands.
- Save drawings/photos in references/<part-number>/ with URLs, revision/page, date and hashes. Actually view relevant drawings and photos.
- Record specified, calculated, approximate and unknown dimensions separately. Count physical pins independently of electrical functions; distinguish package, mating and PCB-hole dimensions.
- Use mm, mounting plane Z=0, and document axes/origin. Inspect visible contours as well as the envelope.
- Add generators to component_cad/components/ and explicitly register them in catalog.py; the initial catalog is empty. The template intentionally fails until completed.
- Build with `uv run --offline python -m component_cad build PART-NUMBER`. See the project API guide for validation and rendering commands.
- Validate solids, independent mounting dimensions, overlaps, and exported STEP geometry/names/colors. Render the exported STEP and actually view the necessary images.
- Store checks in validation.json and visual observations with the current STEP hash. Rendering alone is not visual review.
- Component notes in docs/components/ are copied to the output's notes.md in background mode. Keep them self-contained with dimensions, axes, approximations and source URLs; retain technical regeneration instructions separately in this workspace.
- Report STEP, preview, source and notes with approximations and unperformed checks. KiCad placement must not be claimed without testing it.
