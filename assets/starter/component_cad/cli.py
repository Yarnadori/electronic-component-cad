"""Uniform commands for any registered component family."""
import argparse
import json
import sys
from .catalog import PARTS, select_parts


def main(argv=None):
    parser = argparse.ArgumentParser(description="CadQuery electronic component model library")
    commands = parser.add_subparsers(dest="command")
    listing = commands.add_parser("list", help="List supported part numbers")
    listing.add_argument("--family")
    listing.add_argument("--json", action="store_true")
    gallery = commands.add_parser("gallery", help="Contact sheet of rendered models in a family")
    gallery.add_argument("--family", required=True)
    gallery.add_argument("--output-dir")
    for action in ("build", "validate", "render"):
        sub = commands.add_parser(action)
        sub.add_argument("part", nargs="?")
        sub.add_argument("--family")
        sub.add_argument("--all", action="store_true")
        sub.add_argument("--output-dir", help="Output root; part number is appended")
        if action == "build":
            sub.add_argument("--no-preview", action="store_true", help="Generate and validate without rendering")
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    try:
        if args.command == "list":
            parts = select_parts(family=args.family) if args.family else PARTS
            if args.json:
                print(json.dumps([p.to_dict() for p in parts], indent=2))
            else:
                for p in parts:
                    detail = " / ".join(str(p.details[k]) for k in ("emission_colour", "common", "appearance") if k in p.details)
                    print(f"{p.part_number:18} {p.manufacturer:12} {p.family:14} {detail}")
            return 0
        parts = select_parts(family=args.family) if args.command == "gallery" else select_parts(args.part, args.family, args.all)
    except ValueError as exc:
        parser.error(str(exc))
    # Import CadQuery/VTK only for commands that need them.
    from . import pipeline
    try:
        if args.command == "gallery":
            from .rendering import render_gallery
            print(json.dumps(render_gallery(parts, args.output_dir)))
            return 0
        for part in parts:
            if args.command == "build":
                result = pipeline.build_part(part, args.output_dir, preview=not args.no_preview)
            elif args.command == "validate":
                result = pipeline.validate_part(part, args.output_dir)
            else:
                result = pipeline.render_part(part, args.output_dir)
            print(json.dumps(result, ensure_ascii=True), flush=True)
    except (OSError, ValueError, AssertionError, RuntimeError) as exc:
        print(f"{args.command} failed: {exc}", file=sys.stderr)
        return 1
    return 0
