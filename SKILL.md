---
name: electronic-component-cad
description: Use when creating or correcting a dimensioned 3D CAD model of an electronic component from a product URL, part number, datasheet, or drawing, especially CadQuery STEP models for KiCad. Includes connectors, displays, switches, packages, and heatsinks. Not for PCB routing, footprint-only work, or illustrative 3D images.
license: MIT
metadata:
  version: "0.1.1"
---

# Electronic Component CAD

Deliver a colored STEP, dimensional notes, and previews rendered from the exported STEP. Retain editable CadQuery source and evidence in the background workspace. Use **CadQuery + uv** unless the user explicitly selects another workflow. This skill needs file/shell access, a CAD-capable Python environment, and a way to inspect images. Use the host's available tools; no vendor-specific plugin is required.

## Choose the project route

- **Normal use in a user's project:** read applicable project instructions, then run [scripts/init_project.py](scripts/init_project.py) with the user project path and `--json`. It creates/reuses a persistent workspace in OS user data, outside the project. Use the returned `workspace` for ALL code, downloads, planning notes, uv commands, dependencies and caches. The user's project receives only `models/<part-number>/` when building. Read [references/project-api.md](references/project-api.md) for commands.
- **Existing CAD library:** reuse its current generator interfaces and preserve unrelated models. Do not scaffold over it, silently migrate its files or delete previously generated code. An explicit `--standalone` mode is available only when the user asks for an editable library directly in a new/empty directory.
- Do not copy the starter, environment files or source packages into the user project or the shared skill installation. If the workspace location is unavailable, report the specific problem; do not silently fall back to the project root.
- Store original references under the workspace's `references/<part-number>/`. Keep the complete manufacturer identity in metadata. Use safe single-directory identifiers for filenames; document any mapping from a part number containing slashes or other path characters.

## Establish the evidence

1. Resolve the full part number and suffix from the requested URL or supplied material. Follow actual links to manufacturer drawings and product photographs. Save originals, source URLs, retrieval date, revision/page and SHA-256. HTTP success alone does not establish that a PDF/image is valid.
2. Open the PDF and render relevant pages with `pdfinfo`/`pdftoppm` or an available equivalent. **Actually view** the complete drawing, its variant table and necessary crops. View front/back/underside photos relevant to the geometry. If image inspection is unavailable, record that gap instead of claiming visual review.
3. Record a dimension table with the value, measurement feature, source/page, tolerance or MIN/reference notation, and category: **specified, calculated, approximate, or unknown**. Keep physical leads, electrical poles, NC pins, and CAD solids distinct. Consult [references/modeling-decisions.md](references/modeling-decisions.md) for drawing traps and appearance checks.
4. Resolve important mounting dimensions from evidence before finalizing them. Ask a targeted question only when the missing value cannot be recovered. A supplied local source is usable without downloading it again. Respect current network permissions; this skill does not remove download or filesystem restrictions.

## Model and verify

- Use mm. Put the mounting plane at Z=0 and the component upward along +Z. Match the requested footprint origin/rotation; otherwise document a sensible XY origin and insertion/display direction.
- Group dimensions in a dataclass or similar structure. Separate geometry, export, checks and camera definitions. Name/color materials in `cq.Assembly`. Mark undimensioned estimates in code and documentation.
- Establish envelope, openings, leads and mounting features first; then match visible contours, bends, slots, rivets and display strokes to the images. A shared color or rounded-pin request for one part is not a rule for other parts.
- Check positive valid solids, important mounting dimensions, actual lead sections, opening clearance and unintended inter-part intersection volumes. Set expectations independently from the drawing, not by copying the generator's constants.
- Export and reimport the **final STEP**. Check solid count, bounds, volume, names and colors against the source assembly; inspect important sections of the imported shape. Add focused regressions for new mounting geometry or a corrected feature.
- Render that STEP from front/back and whichever underside/detail views explain the part. **View the final images**; fix clipping, blocked openings, reversed features, wrong contours and missing parts. Rendering success does not constitute visual review. Re-render after geometry changes and tie the review to the current STEP hash.

The starter supplies common validity, overlap, STEP roundtrip and rendering functions. It does not know the target's dimensions, implement its shape, or perform image review. The unfilled generator template deliberately raises errors.

## Finish the requested work

Save source, STEP, previews, `validation.json`, dimension/coordinate notes and a visual-review record. Associate metadata, validation and rendered images with the same STEP SHA-256. In an existing project, check that unrelated artifacts remain unchanged. Do not regenerate existing models for a documentation-only change.

Report links to STEP, preview and the model's README/notes; summarize verified checks and meaningful approximations. Keep internal package names, workspace paths and setup commands out of normal user-facing replies. Provide source or regeneration details when requested, without deleting the retained source. Write model notes for the user, using source URLs and measurements rather than links into the internal workspace. Say which checks, visual inspections or KiCad placement steps were not performed. A KiCad display model is not automatically a printable, thermal, electrical-contact or thread-fit model.
