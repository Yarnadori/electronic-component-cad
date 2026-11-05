"""Explicit component catalog; register only implemented, documented parts."""
from .core import Part


def _parts():
    return ()


PARTS = _parts()


def get_part(number):
    matches = [p for p in PARTS if p.part_number.casefold() == number.casefold()]
    if len(matches) != 1:
        raise ValueError(f"Unknown or ambiguous part: {number}. Use 'list' for supported parts.")
    return matches[0]


def select_parts(number=None, family=None, all_parts=False):
    if sum((number is not None, family is not None, bool(all_parts))) != 1:
        raise ValueError("Select exactly one part number, --family FAMILY, or --all.")
    if number is not None:
        return (get_part(number),)
    if all_parts:
        return PARTS
    selected = tuple(p for p in PARTS if p.family.casefold() == family.casefold())
    if not selected:
        raise ValueError(f"Unknown family: {family}")
    return selected
