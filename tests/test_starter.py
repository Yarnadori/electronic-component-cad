"""Portable starter smoke checks; all generated geometry is synthetic test data."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
INITIALIZER = ROOT / "scripts/init_project.py"


def run(*args, cwd=None):
    return subprocess.run([sys.executable,*map(str,args)],cwd=cwd,
                          capture_output=True,text=True,encoding="utf-8")


class StarterTests(unittest.TestCase):
    def test_init_and_refuse_occupied_destination(self):
        with tempfile.TemporaryDirectory() as scratch:
            target=Path(scratch)/"project"
            result=run(INITIALIZER,target)
            self.assertEqual(result.returncode,0,result.stderr)
            original=(target/"uv.lock").read_bytes()
            sentinel=target/"user-note.txt"
            sentinel.write_text("keep this")
            result=run(INITIALIZER,target)
            self.assertNotEqual(result.returncode,0)
            self.assertIn("new or empty",result.stderr)
            self.assertEqual(sentinel.read_text(),"keep this")
            self.assertEqual((target/"uv.lock").read_bytes(),original)
            self.assertTrue((target/"docs/adding-components.md").is_file())
            self.assertIn("AGENTS.md",(target/"CLAUDE.md").read_text())
            self.assertEqual(run("-m","akicad_3d","list","--json",cwd=target).stdout.strip(),"[]")

    def test_initializer_refuses_inside_skill(self):
        target=ROOT/"should-not-exist-test-project"
        result=run(INITIALIZER,target)
        self.assertNotEqual(result.returncode,0)
        self.assertIn("outside the installed skill",result.stderr)
        self.assertFalse(target.exists())

    @unittest.skipUnless(importlib.util.find_spec("cadquery"),"Install starter dependencies to run CAD checks")
    def test_template_refuses_unfilled_model(self):
        with tempfile.TemporaryDirectory() as scratch:
            target=Path(scratch)/"project"
            self.assertEqual(run(INITIALIZER,target).returncode,0)
            code='''
import importlib.util,sys
spec=importlib.util.spec_from_file_location("template","docs/templates/component.py")
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)
for name,args in (("build",(None,)),("verify_dimensions",({},None)),("preview_spec",(None,))):
    try: getattr(module,name)(*args)
    except NotImplementedError: pass
    else: raise AssertionError(name+" should reject an unfilled template")
'''
            result=run("-c",code,cwd=target)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertFalse((target/"models").exists())

    @unittest.skipUnless(importlib.util.find_spec("cadquery"),"Install starter dependencies to run CAD checks")
    def test_colored_step_checks_and_render_in_isolated_project(self):
        with tempfile.TemporaryDirectory() as scratch:
            target=Path(scratch)/"project"
            self.assertEqual(run(INITIALIZER,target).returncode,0)
            module=target/"akicad_3d/components/synthetic.py"
            module.write_text(textwrap.dedent('''
                import cadquery as cq
                from akicad_3d.core import PreviewSpec,View
                from akicad_3d.validation import near
                def build(part):
                    body=cq.Workplane("XY").box(4,3,2).translate((0,0,1))
                    pin=cq.Workplane("XY",origin=(.5,0,-1)).circle(.25).extrude(1)
                    parts={"Body":(body,(.15,.16,.17)),"Pin":(pin,(.7,.75,.8))}
                    assembly=cq.Assembly(name=part.model_name)
                    for name,(shape,rgb) in parts.items():
                        assembly.add(shape,name=name,color=cq.Color(*rgb))
                    return assembly,parts
                def verify_dimensions(parts,part):
                    near(parts["Body"][0].val().BoundingBox().xlen,4,"body width")
                    near(parts["Pin"][0].val().BoundingBox().zmin,-1,"pin projection")
                    return {"checks":["synthetic_dimensions"]}
                def preview_spec(part):
                    return PreviewSpec("Synthetic starter test","Not a real component",
                        (View("front",(10,-15,12),4,(0,0,.5)),
                         View("rear",(-10,15,12),4,(0,0,.5))),())
                '''),encoding="utf-8")
            reference=target/"references/TEST-PART"
            reference.mkdir(parents=True)
            (reference/"dimensions.txt").write_text("Synthetic test: body 4 x 3 x 2, pin diameter .5, projection 1.")
            (target/"docs/components").mkdir()
            (target/"docs/components/test.md").write_text("# Synthetic test fixture\nNot a real component.")
            code='''
from pathlib import Path
from akicad_3d.core import Part
from akicad_3d.pipeline import build_part,validate_part
from akicad_3d.validation import verify_step
from akicad_3d.components.synthetic import build
part=Part("TEST-PART","synthetic","test","TEST-PART", "akicad_3d.components.synthetic",
          "references/TEST-PART/dimensions.txt","synthetic fixture",1,"docs/components/test.md",2)
result=build_part(part)
assert result["solid_count"]==2 and result["checks_passed"]==7
assert validate_part(part)["solid_count"]==2
_,parts=build(part)
shape,rgb=parts["Pin"]
parts["Pin"]=shape.translate((0,0,.25)),rgb
try: verify_step(parts,Path(result["step"]),2,"TEST-PART")
except AssertionError as exc: assert "overlaps" in str(exc),str(exc)
else: raise AssertionError("Intentional pin/body overlap was not detected")
'''
            result=run("-c",code,cwd=target)
            self.assertEqual(result.returncode,0,result.stderr)
            out=target/"models/TEST-PART"
            digest=hashlib.sha256((out/"TEST-PART.step").read_bytes()).hexdigest()
            for name in ("validation.json","metadata.json","render-validation.json"):
                self.assertEqual(json.loads((out/name).read_text())["step_sha256"],digest)
            self.assertTrue((out/"preview.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))


if __name__=="__main__":
    unittest.main()
