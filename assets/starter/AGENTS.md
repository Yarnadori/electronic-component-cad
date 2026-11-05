# Electronic component CAD project

- Read README.md and docs/adding-components.md before editing. Preserve existing models and user changes.
- Use CadQuery with the uv lock. Generate named/material-colored STEP assemblies and editable source.
- Save drawings/photos in references/<part-number>/ with URLs, revision/page, date and hashes. Actually view relevant drawings and photos.
- Record specified, calculated, approximate and unknown dimensions separately. Count physical pins independently of electrical functions; distinguish package, mating and PCB-hole dimensions.
- Use mm, mounting plane Z=0, and document axes/origin. Inspect visible contours as well as the envelope.
- Add generators to akicad_3d/components/ and explicitly register them in catalog.py; the initial catalog is empty. The template intentionally fails until completed.
- Build with `uv run --offline python -m akicad_3d build PART-NUMBER`. See the project API guide for validation and rendering commands.
- Validate solids, independent mounting dimensions, overlaps, and exported STEP geometry/names/colors. Render the exported STEP and actually view the necessary images.
- Store checks in validation.json and visual observations with the current STEP hash. Rendering alone is not visual review.
- Report STEP, preview, source and notes with approximations and unperformed checks. KiCad placement must not be claimed without testing it.
