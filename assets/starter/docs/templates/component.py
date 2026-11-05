"""Unregistered component template, not a finished model.

Copy into component_cad/components/<manufacturer>/<component>.py, then replace
every TODO using the actual drawing and photos. See docs/adding-components.md.
No CadQuery geometry is created and no file is written by importing this file.
"""
from dataclasses import asdict, dataclass
import cadquery as cq
from component_cad.core import PreviewSpec, View
from component_cad.validation import near


@dataclass(frozen=True)
class Dimensions:
    # TODO: extend/rename for the real package, including mounting dimensions.
    # Document cosmetic estimates with _approx names. Units: mm.
    body_length: float
    body_width: float
    body_height: float


# TODO: values read from the target drawing, with sources in component notes.
D: Dimensions | None = None

# TODO: independent drawing expectations, NOT calculated from D or the model.
# Required keys: xmin, xmax, ymin, ymax, zmin, zmax (including leads/pegs).
EXPECTED_ENVELOPE_MM: dict[str, float] | None = None


def _build_shapes(d):
    """Return {unique_name: (cq.Workplane, (red, green, blue))}.

    TODO: use the target's real geometry. Separate materials into parts,
    avoid unintended volume overlaps, keep the seating plane at Z=0.
    Parts can touch without sharing positive volume. Do not export here.
    """
    raise NotImplementedError("TODO: implement the drawing-based component geometry")


def build(part):
    if D is None:
        raise NotImplementedError("TODO: set Dimensions from the target drawing")
    parts = _build_shapes(D)
    if not parts:
        raise ValueError("The model must contain named parts")
    assembly = cq.Assembly(name=part.model_name)
    for name, (wp, colour) in parts.items():
        assembly.add(wp, name=name, color=cq.Color(*colour))
    return assembly, parts


def _verify_part_features(parts):
    """Assert the target's independent mechanical expectations; return check IDs.

    TODO: check actual centres, diameters, section width/thickness, projection,
    opening clearance, physical pin count and any visual feature being fixed.
    Read nominal expectations from the drawing, not just constructor values.
    The shared pipeline handles validity, overlaps, STEP roundtrip and colours.
    """
    raise NotImplementedError("TODO: implement independent part-specific checks")


def verify_dimensions(parts, part):
    if D is None or EXPECTED_ENVELOPE_MM is None:
        raise NotImplementedError("TODO: set dimensions and independent drawing expectations")
    axes = {"xmin", "xmax", "ymin", "ymax", "zmin", "zmax"}
    if set(EXPECTED_ENVELOPE_MM) != axes:
        raise ValueError("Expected envelope must contain all six drawing bounds")
    solids = [s for wp, _ in parts.values() for s in wp.solids().vals()]
    if not solids:
        raise ValueError("The model contains no solids")
    bb = cq.Compound.makeCompound(solids).BoundingBox()
    for axis, expected in EXPECTED_ENVELOPE_MM.items():
        near(getattr(bb, axis), expected, "drawing envelope " + axis)
    feature_checks = _verify_part_features(parts)
    if not feature_checks:
        raise ValueError("Envelope alone is not a complete mechanical check")
    return {"parameters": asdict(D),
            "checks": ["drawing_envelope", *feature_checks]}


def preview_spec(part):
    """Return PreviewSpec(title, subtitle, views, notes) for the actual part.

    TODO: use View(name, camera, scale, focal_point, up=(0,0,1)). Include the
    front/back and any necessary underside/detail. Match the real coordinate
    axes and frame the entire model. Inspect the PNGs before claiming review.
    PreviewSpec and View are imported above for the implementation.
    """
    raise NotImplementedError("TODO: select part-specific cameras and captions")
