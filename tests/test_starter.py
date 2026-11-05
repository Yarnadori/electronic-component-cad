"""Portable starter smoke checks; all generated geometry is synthetic test data."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
INITIALIZER = ROOT / "scripts/init_project.py"


def run(*args, cwd=None, env=None):
    return subprocess.run([sys.executable,"-X","utf8",*map(str,args)],cwd=cwd,
                          capture_output=True,text=True,encoding="utf-8",env=env)


class StarterTests(unittest.TestCase):
    def test_default_initialization_keeps_user_project_untouched(self):
        with tempfile.TemporaryDirectory() as scratch:
            project=Path(scratch)/"my pcb project"
            project.mkdir()
            note=project/"board.kicad_pro"
            note.write_text("user project")
            env=dict(os.environ,ELECTRONIC_COMPONENT_CAD_HOME=str(Path(scratch)/"state"))
            result=run(INITIALIZER,project,env=env)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual({p.name for p in project.iterdir()},{"board.kicad_pro"})
            record=json.loads(run(INITIALIZER,project,"--json",env=env).stdout)
            workspace=Path(record["workspace"])
            self.assertFalse(workspace.is_relative_to(project))
            self.assertTrue((workspace/"component_cad/catalog.py").is_file())
            self.assertEqual(Path(record["output_directory"]),project/"models")
            source=workspace/"component_cad/components/user_part.py"
            source.write_text("# keep my edited generator\n")
            again=run(INITIALIZER,project/".","--json",env=env)
            self.assertEqual(again.returncode,0,again.stderr)
            self.assertEqual(json.loads(again.stdout)["workspace"],str(workspace))
            self.assertFalse(json.loads(again.stdout)["created"])
            self.assertEqual(source.read_text(),"# keep my edited generator\n")
            self.assertEqual(note.read_text(),"user project")
            catalog=run("-m","component_cad","list","--json",cwd=workspace)
            self.assertEqual(catalog.returncode,0,catalog.stderr)
            self.assertEqual(json.loads(catalog.stdout),[])

    def test_projects_with_same_name_keep_separate_workspaces(self):
        with tempfile.TemporaryDirectory() as scratch:
            env=dict(os.environ,ELECTRONIC_COMPONENT_CAD_HOME=str(Path(scratch)/"state"))
            records=[]
            for parent in ("one","two"):
                project=Path(scratch)/parent/"board"
                result=run(INITIALIZER,project,"--json",env=env)
                self.assertEqual(result.returncode,0,result.stderr)
                records.append(json.loads(result.stdout))
            self.assertNotEqual(records[0]["workspace"],records[1]["workspace"])
            self.assertNotEqual(records[0]["output_directory"],records[1]["output_directory"])

    def test_state_directory_inside_project_is_rejected(self):
        with tempfile.TemporaryDirectory() as scratch:
            project=Path(scratch)/"board"
            project.mkdir()
            env=dict(os.environ,ELECTRONIC_COMPONENT_CAD_HOME=str(project/"hidden-state"))
            result=run(INITIALIZER,project,env=env)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(list(project.iterdir()),[])

    def test_unrecognized_workspace_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as scratch:
            project=Path(scratch)/"board"
            env=dict(os.environ,ELECTRONIC_COMPONENT_CAD_HOME=str(Path(scratch)/"state"))
            result=run(INITIALIZER,project,"--json",env=env)
            self.assertEqual(result.returncode,0,result.stderr)
            workspace=Path(json.loads(result.stdout)["workspace"])
            (workspace/"workspace.json").unlink()
            source=workspace/"component_cad/catalog.py"
            source.write_text("# user changes must survive\n")
            result=run(INITIALIZER,project,env=env)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(source.read_text(),"# user changes must survive\n")
            self.assertFalse((workspace/"workspace.json").exists())
            self.assertEqual(list(project.iterdir()),[])

    def test_unavailable_state_location_does_not_fall_back_to_project(self):
        with tempfile.TemporaryDirectory() as scratch:
            project=Path(scratch)/"board"
            project.mkdir()
            state=Path(scratch)/"not-a-directory"
            state.write_text("keep")
            result=run(INITIALIZER,project,env=dict(os.environ,ELECTRONIC_COMPONENT_CAD_HOME=str(state)))
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(state.read_text(),"keep")
            self.assertEqual(list(project.iterdir()),[])

    def test_init_and_refuse_occupied_destination(self):
        with tempfile.TemporaryDirectory() as scratch:
            target=Path(scratch)/"project"
            result=run(INITIALIZER,target,"--standalone")
            self.assertEqual(result.returncode,0,result.stderr)
            original=(target/"uv.lock").read_bytes()
            sentinel=target/"user-note.txt"
            sentinel.write_text("keep this")
            result=run(INITIALIZER,target,"--standalone")
            self.assertNotEqual(result.returncode,0)
            self.assertIn("new or empty",result.stderr)
            self.assertEqual(sentinel.read_text(),"keep this")
            self.assertEqual((target/"uv.lock").read_bytes(),original)
            self.assertTrue((target/"docs/adding-components.md").is_file())
            self.assertIn("AGENTS.md",(target/"CLAUDE.md").read_text())
            self.assertEqual(run("-m","component_cad","list","--json",cwd=target).stdout.strip(),"[]")

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
            self.assertEqual(run(INITIALIZER,target,"--standalone").returncode,0)
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
            project=Path(scratch)/"user board"
            env=dict(os.environ,ELECTRONIC_COMPONENT_CAD_HOME=str(Path(scratch)/"state"))
            result=run(INITIALIZER,project,"--json",env=env)
            self.assertEqual(result.returncode,0,result.stderr)
            target=Path(json.loads(result.stdout)["workspace"])
            module=target/"component_cad/components/synthetic.py"
            module.write_text(textwrap.dedent('''
                import cadquery as cq
                from component_cad.core import PreviewSpec,View
                from component_cad.validation import near
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
from component_cad.core import Part
from component_cad.pipeline import build_part,validate_part
from component_cad.validation import verify_step
from component_cad.components.synthetic import build
part=Part("TEST-PART","synthetic","test","TEST-PART", "component_cad.components.synthetic",
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
            out=project/"models/TEST-PART"
            digest=hashlib.sha256((out/"TEST-PART.step").read_bytes()).hexdigest()
            for name in ("validation.json","metadata.json","render-validation.json"):
                self.assertEqual(json.loads((out/name).read_text())["step_sha256"],digest)
            self.assertTrue((out/"preview.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual({p.name for p in project.iterdir()},{"models"})
            self.assertEqual((out/"notes.md").read_bytes(),(target/"docs/components/test.md").read_bytes())
            self.assertNotIn(str(target),(out/"README.md").read_text(encoding="utf-8"))
            self.assertFalse((target/"models").exists())
            override=Path(scratch)/"alternate-output"
            result=run("-c",code.replace("result=build_part(part)",f"result=build_part(part,Path({str(override)!r}))").replace("validate_part(part)",f"validate_part(part,Path({str(override)!r}))"),cwd=target)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue((override/"TEST-PART/TEST-PART.step").is_file())


if __name__=="__main__":
    unittest.main()
