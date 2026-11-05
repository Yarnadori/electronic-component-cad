# Drawing interpretation and visual modeling decisions

## Evidence that changes geometry

| Evidence | Decision |
| --- | --- |
| A suffix/variant table differs from a common drawing | Apply the table for the requested complete part number. Preserve the stated drawing revision. |
| Several products share one PDF | Use the target's panel; adjacent outlines, pitches and pin counts may differ. |
| Mating plug, land or drill dimensions appear next to the package | Identify the feature being measured before using the value for the component itself. |
| M3 or another thread designation | It identifies a thread, not a dimensioned clearance bore. A smooth nominal-diameter abstraction must be labeled as such. |
| MIN or a parenthesized reference dimension | Preserve that status in the model notes; do not describe it as a universal measured nominal. |
| A bottom/insertion view locates terminals | Transform the drawing into the chosen axes explicitly, checking numbers to avoid mirroring. |
| Three circuits but four blades, or NC labels | Count physical metal features separately from electrical functions. NC does not mean absent. |
| A width dimension attaches to a solder toe | Do not apply that width to a broader upright stem or eyelet. |
| The body extends below its seating plane | Keep the datum at the actual mounting plane; document required edge/board clearance. |
| A public picture has a different file number from the product code | Follow the actual gallery link and confirm its part identity. Never infer the photo URL solely from the product code. |

A useful dimension record has: feature, chosen value, tolerance/reference notation, source page/figure, and **specified/calculated/approximate/unknown**. Calculated values include the equation. Photos support visible contours; perspective pixel ratios do not establish an undocumented critical mounting dimension.

## Finish the visible shape

Compare complete front/back/underside silhouettes before small decorations. Distinguish rods, stamped blades, bends, spring plates, and riveted ends. Check where a black housing stops relative to metal: a forward-open U-shaped notch is not a closed rectangular pocket. For seven-segment displays, match the stroke endpoints and parallel gaps, not only digit height. For heatsinks, verify fin count, channel depths and pin-retention grooves.

Prioritize evidence-backed external features. Omit or approximate unseen contacts, textures, plating thickness and fine molding as appropriate for KiCad placement. Label those estimates in code (for example `_approx`) and notes. Follow the user's specific requested color/section without propagating that choice to other parts.

## Resolve CAD failures without hiding them

Inspect per-part solid counts, validity, volume and bounds immediately before and after the failing boolean. Sequential cuts can isolate a failed compound subtraction. A recessed rivet used as a cutter can leave a detached plug; create the intended through-hole separately. A broad bounding box cannot distinguish a round pin from a square pin: inspect the board-insertion section. A wide upper plate must not be measured as a narrow solder toe.

Fix the offending feature before fillets/chamfers. Do not discard small solids or enlarge tolerances merely to make a failing check pass. When the intended construction changes, update only the affected baseline, keep mounting constraints and unaffected parts checked, and add a regression that detects the old defect.

## Review the exported artifact

Use the actual exported STEP as the rendering input. View orthographic details when an oblique view hides an opening. Adjust framing so all leads and fins are visible. Check material colors, reflections that obscure detail, contour mistakes, left/right reversal, missing parts and crop boundaries. A `render-validation.json` proves rendering, not visual inspection.

Record the images actually viewed, source figures/photos compared, observations, limitations and final STEP SHA-256. After regeneration, confirm the current hash and repeat relevant inspection. KiCad placement, mechanical fit, printability and thermal/electrical behavior remain separate claims requiring their own evidence.
