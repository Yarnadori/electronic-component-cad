"""VTK previews of exported STEP; camera and captions supplied by each family."""
import hashlib
import json
import math
import os
from pathlib import Path
from .validation import load_parts
import vtk
from PIL import Image, ImageDraw, ImageFont


def render_step(step_path, output, position, size=(1200, 900), *, expected_parts,
                focal_point, view_up=(0, 0, 1), parallel_scale, expected_name=None):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.955, 0.966, 0.980)
    renderer.SetUseDepthPeeling(True)
    loaded = load_parts(step_path, expected_name)
    solid_count = sum(len(shape.Solids()) for shape, _ in loaded.values())
    if solid_count != expected_parts:
        raise AssertionError(f"Rendered solid count {solid_count} != {expected_parts}")
    colours = []
    for shape, colour in loaded.values():
        if colour is None:
            raise AssertionError("STEP part is missing its colour")
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(shape.toVtkPolyData(0.015, 0.08, True))
        mapper.ScalarVisibilityOff()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        rgb = colour.toTuple()[:3]
        colours.append(tuple(round(v, 4) for v in rgb))
        prop = actor.GetProperty()
        prop.SetColor(*rgb)
        prop.SetInterpolationToPhong()
        prop.SetAmbient(0.24)
        prop.SetDiffuse(0.72)
        prop.SetSpecular(0.35 if min(rgb) > 0.5 else 0.17)
        prop.SetSpecularPower(38)
        renderer.AddActor(actor)
    camera = renderer.GetActiveCamera()
    camera.SetPosition(*position)
    camera.SetFocalPoint(*focal_point)
    camera.SetViewUp(*view_up)
    camera.ParallelProjectionOn()
    camera.SetParallelScale(parallel_scale)
    for pos, intensity in [((-25,-30,45), .85), ((12,25,28), .65), ((35,-12,18), .4)]:
        light = vtk.vtkLight()
        light.SetLightTypeToSceneLight()
        light.SetPosition(*pos)
        light.SetFocalPoint(*focal_point)
        light.SetIntensity(intensity)
        renderer.AddLight(light)
    window = vtk.vtkRenderWindow()
    try:
        window.SetOffScreenRendering(1)
        window.SetMultiSamples(8)
        window.SetSize(*size)
        window.AddRenderer(renderer)
        renderer.ResetCameraClippingRange()
        window.Render()
        capture = vtk.vtkWindowToImageFilter()
        capture.SetInput(window)
        capture.SetInputBufferTypeToRGB()
        capture.ReadFrontBufferOff()
        capture.Update()
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(str(output))
        writer.SetInputConnection(capture.GetOutputPort())
        writer.Write()
    finally:
        window.Finalize()
    return colours


def font(size, bold=False):
    windows = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    candidates = [str(windows / ("arialbd.ttf" if bold else "arial.ttf")),
                  "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def render_previews(part, step, spec):
    out = step.parent
    width, height = 1500, 950
    for view in spec.views:
        render_step(step, out / f"preview-{view.name}.png", view.camera, (width, height),
                    expected_parts=part.expected_solids, focal_point=view.focal_point,
                    view_up=view.up, parallel_scale=view.scale, expected_name=part.model_name)
    cells = len(spec.views)+1  # Last cell contains family-specific notes.
    rows = math.ceil(cells/2)
    canvas = Image.new("RGB", (width*2, 170+rows*(height+70)), "#f4f7fa")
    draw = ImageDraw.Draw(canvas)
    draw.text((60, 25), spec.title, font=font(58, True), fill="#183146")
    draw.text((63, 105), spec.subtitle, font=font(34), fill="#506175")
    for i, view in enumerate(spec.views):
        x, y = (i%2)*width, 170+(i//2)*(height+70)
        with Image.open(out / f"preview-{view.name}.png") as im:
            canvas.paste(im, (x, y))
        draw.text((x+65, y+height), view.name.upper(), font=font(36, True), fill="#183146")
    i = len(spec.views)
    x, y = (i%2)*width+65, 170+(i//2)*(height+70)+230
    for j, note in enumerate((*spec.notes, "Rendered from the exported STEP")):
        draw.text((x, y+j*70), note, font=font(34), fill="#354a60")
    canvas.save(out / "preview.png")
    result = {"part": part.part_number, "step_sha256": hashlib.sha256(step.read_bytes()).hexdigest(),
              "rendered_STEP_parts": len(load_parts(step)), "rendered_STEP_solids": part.expected_solids,
              "views": [v.name for v in spec.views],
              "visual_inspection": "Rendering only; manual image review is recorded separately."}
    (out / "render-validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def render_gallery(parts, output_root=None):
    """Contact sheet of already rendered STEP images; not a substitute for rendering."""
    if not parts or len({(p.manufacturer, p.family) for p in parts}) != 1:
        raise ValueError("A gallery requires exactly one component family")
    # Pair I/L versions of each emission colour; stable fallback for other families.
    ordered = sorted(parts, key=lambda p: (p.details.get("colour_code", p.part_number), p.part_number))
    width, height = 1000, 740
    canvas = Image.new("RGB", (width*2, 110+height*math.ceil(len(ordered)/2)), "#f4f7fa")
    draw = ImageDraw.Draw(canvas)
    appearance = "unlit " if all(p.details.get("appearance") == "unlit" for p in parts) else ""
    draw.text((45, 25), f"{parts[0].family.upper()} / {len(parts)} models / {appearance}STEP previews", font=font(40, True), fill="#183146")
    hashes = {}
    for i, part in enumerate(ordered):
        out = part.output_dir(output_root)
        record = json.loads((out / "render-validation.json").read_text(encoding="utf-8"))
        if record["part"] != part.part_number:
            raise ValueError(f"Render identity mismatch for {part.part_number}")
        step_hash = hashlib.sha256((out / (part.model_name+".step")).read_bytes()).hexdigest()
        if step_hash != record["step_sha256"]:
            raise ValueError(f"Stale render for {part.part_number}; run render first")
        path = out / "preview-front.png"
        if not path.is_file():
            path = out / f"preview-{record['views'][0]}.png"
        x, y = (i%2)*width, 110+(i//2)*height
        with Image.open(path) as im:
            im.thumbnail((width, 620), Image.Resampling.LANCZOS)
            canvas.paste(im, (x+(width-im.width)//2, y))
        draw.text((x+40, y+625), part.part_number, font=font(35, True), fill="#183146")
        detail = " / ".join(str(part.details[k]) for k in ("emission_colour", "common") if k in part.details)
        detail = detail or part.details.get("connector", part.manufacturer)
        draw.text((x+40, y+680), detail, font=font(28), fill="#506175")
        hashes[part.part_number] = step_hash
    directory = parts[0].output_dir(output_root).parent
    # Different families now share the output root; include the family in the filename.
    gallery_path = directory / f"preview-{parts[0].family}.png"
    canvas.save(gallery_path)
    (directory / f"gallery-{parts[0].family}.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")
    return {"gallery": str(gallery_path), "parts": len(ordered)}
