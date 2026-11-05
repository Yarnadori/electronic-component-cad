"""Shared solid checks and name/colour/geometry-preserving STEP roundtrip."""
from itertools import combinations
import hashlib
import cadquery as cq


def bounds(shape):
    b = shape.BoundingBox()
    return {k: round(getattr(b, k), 7) for k in
            ("xmin", "xmax", "ymin", "ymax", "zmin", "zmax", "xlen", "ylen", "zlen")}


def near(actual, expected, label, tolerance=1e-6):
    if abs(actual-expected) > tolerance:
        raise AssertionError(f"{label}: {actual} != {expected} (tolerance {tolerance})")


def load_parts(step_file, expected_name=None):
    parts = {}
    assembly = cq.Assembly.load(str(step_file))
    if expected_name is not None and assembly.name != expected_name:
        raise AssertionError(f"STEP identity {assembly.name!r} != {expected_name!r}")
    for shape, name, location, colour in assembly:
        if isinstance(shape, cq.Workplane):
            shape = shape.val()
        if not isinstance(shape, cq.Shape):
            continue
        key = name.split("/")[-1]
        if key in parts:
            raise AssertionError(f"Duplicate STEP part name: {key}")
        parts[key] = (shape.moved(location), colour)
    return parts


def verify_step(parts, step_file, expected_solids, expected_name):
    all_solids, part_report = [], {}
    for name, (wp, _) in parts.items():
        solids = wp.solids().vals()
        if not solids or not all(s.isValid() and s.Volume() > 0 for s in solids):
            raise AssertionError(f"Invalid or empty solid: {name}")
        all_solids.extend(solids)
        part_report[name] = {"valid": True, "solids": len(solids),
                             "volume_mm3": sum(s.Volume() for s in solids), "bounds_mm": bounds(wp.val())}
    if len(all_solids) != expected_solids:
        raise AssertionError(f"Solid count {len(all_solids)} != {expected_solids}")
    original = cq.Compound.makeCompound(all_solids)
    overlaps, tested = [], 0
    for (n1, (wp1, _)), (n2, (wp2, _)) in combinations(parts.items(), 2):
        b1, b2 = wp1.val().BoundingBox(), wp2.val().BoundingBox()
        if any(min(getattr(b1, k+"max"), getattr(b2, k+"max")) -
               max(getattr(b1, k+"min"), getattr(b2, k+"min")) <= 1e-7 for k in "xyz"):
            continue
        tested += 1
        volume = wp1.val().intersect(wp2.val()).Volume()
        if volume > 1e-7:
            overlaps.append((n1, n2, volume))
    if overlaps:
        raise AssertionError(f"Component overlaps: {overlaps}")
    imported = cq.importers.importStep(str(step_file)).solids().vals()
    if len(imported) != expected_solids or not all(s.isValid() and s.Volume() > 0 for s in imported):
        raise AssertionError("STEP roundtrip lost solids or produced invalid geometry")
    roundtrip = cq.Compound.makeCompound(imported)
    near(roundtrip.Volume(), original.Volume(), "STEP total volume", 1e-4)
    for axis in ("xmin", "xmax", "ymin", "ymax", "zmin", "zmax"):
        near(getattr(roundtrip.BoundingBox(), axis), getattr(original.BoundingBox(), axis), "STEP "+axis)
    loaded = load_parts(step_file, expected_name)
    if set(loaded) != set(parts):
        raise AssertionError(f"STEP names differ: missing={set(parts)-set(loaded)}, extra={set(loaded)-set(parts)}")
    for name, (shape, colour) in loaded.items():
        if colour is None:
            raise AssertionError(f"STEP colour missing: {name}")
        for actual, expected in zip(colour.toTuple()[:3], parts[name][1]):
            near(actual, expected, name+" colour", 2e-5)
        near(shape.Volume(), parts[name][0].val().Volume(), name+" STEP volume", 1e-5)
        for axis in ("xmin", "xmax", "ymin", "ymax", "zmin", "zmax"):
            near(getattr(shape.BoundingBox(), axis), getattr(parts[name][0].val().BoundingBox(), axis), name+axis)
    return {"checks": ["all_solids_valid_positive", "expected_solid_count", "no_component_overlaps",
                       "STEP_validity_and_count", "STEP_volume_and_bounds", "STEP_names_colours_and_geometry"],
            "parts": part_report, "solid_count": len(imported), "bounds_mm": bounds(roundtrip),
            "volume_mm3": roundtrip.Volume(), "overlaps": overlaps, "boolean_overlap_pairs_checked": tested,
            "step_sha256": hashlib.sha256(step_file.read_bytes()).hexdigest()}
