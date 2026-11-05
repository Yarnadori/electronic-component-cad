# Validation scope

This file describes the package's verification scope, not a certification of any component model.

Local verification on 2026-11-05 passed: **4 tests, 0 failures, 0 skips**, using a newly created uv environment with managed CPython 3.11.14 and CadQuery 2.8.0. The dependency lock check and skill structure check also passed. FreeCAD was not required for this run.

Installation verification used skills CLI **1.7.6** on Node.js **24.16.0** to discover the skill from `Yarnadori/electronic-component-cad` and install it in an isolated project for **Codex, Claude Code, Gemini CLI, Cursor, GitHub Copilot and Windsurf**. All 32 tracked files arrived intact (allowing Git's newline conversion); local environments and caches were excluded. The installed initializer created a working empty catalog, and all four starter tests passed from the installed package. This verifies installation and bundled code, not execution by each AI product.

To reproduce discovery and installation, run these in a new scratch project:

```sh
npx skills@1.7.6 add Yarnadori/electronic-component-cad --list
npx skills@1.7.6 add Yarnadori/electronic-component-cad -a codex claude-code gemini-cli cursor github-copilot windsurf -y
```

Then run the initializer and development checks using the installed skill's path. The CLI writes a project `skills-lock.json` and chooses shared or tool-specific directories. No global installation is needed for this test.

- Structural validation: skill frontmatter/name, relative references, Python syntax, and the optional UI metadata.
- Starter tests: new-directory creation, refusal to overwrite files or write inside the skill, empty catalog, unfilled-template rejection, and a synthetic two-solid model exported/reimported/rendered in a temporary project.
- The synthetic CAD check exercises positive solids, colors, STEP identity/roundtrip, output hashes and deliberate overlap rejection. Its generated previews are test artifacts, not a shipped manufacturer's model.
- Real component measurements and visual acceptance remain the responsibility of each invocation. The starter cannot infer dimensions or confirm that an agent actually viewed an image.
- Windows / Python 3.11 / CadQuery 2.8.0 is the execution target used for local validation. Other OS rendering backends have not been exercised here.
- Claude Code and Gemini CLI installation instructions follow their published skill documentation; their complete CAD workflows have not been run for this release.

Reproduce the package tests using the commands in README.md. Do not interpret successful script tests as evidence of end-to-end behavioral equivalence across AI products.
