# Validation scope

This file describes the package's verification scope, not a certification of any component model.

The starter is validated on Windows with uv-managed CPython 3.11.14 and CadQuery 2.8.0. FreeCAD is not required. The current suite contains **9 tests** covering workspace isolation and the CAD pipeline; run the commands below or in README.md for current results.

On 2026-11-05, all **9 tests passed with 0 skips**. Skill structure, Python syntax, local links and the uv lock check passed. A fresh uv environment in an external workspace imported the renamed package and generated a volume-6 unit-test solid while leaving the user project empty. Its default cache path also resolved inside the workspace. Dependency package versions are unchanged.

Installation verification uses skills CLI **1.7.6** on Node.js **24.16.0** to discover the skill from `Yarnadori/electronic-component-cad` and install it in an isolated project for **Codex, Claude Code, Gemini CLI, Cursor, GitHub Copilot and Windsurf**. Check that the entire skill, including starter assets, arrives intact while local environments and caches are excluded. Installation checks verify file delivery and bundled code, not execution by each AI product.

To reproduce discovery and installation, run these in a new scratch project:

```sh
npx skills@1.7.6 add Yarnadori/electronic-component-cad --list
npx skills@1.7.6 add Yarnadori/electronic-component-cad -a codex claude-code gemini-cli cursor github-copilot windsurf -y
```

Then run the initializer and development checks using the installed skill's path. The CLI writes a project `skills-lock.json` and chooses shared or tool-specific directories. No global installation is needed for this test.

- Structural validation: skill frontmatter/name, relative references, Python syntax, and the optional UI metadata.
- Workspace tests: default setup leaves an existing user project untouched, preserves edited sources on reuse, separates equal folder names at different paths, rejects internal/unavailable state locations without falling back to the project, and refuses an unrecognized workspace. Explicit standalone setup still refuses occupied destinations and the skill installation itself.
- CAD integration: a synthetic two-solid model is exported/reimported/rendered from an external workspace into the user's models folder. Only models is added to the user project; notes are copied without exposing workspace paths. Validation and explicit output overrides use the same destination rules. The empty catalog and unfilled-template guards also run.
- The synthetic CAD check exercises positive solids, colors, STEP identity/roundtrip, output hashes and deliberate overlap rejection. Its generated previews are test artifacts, not a shipped manufacturer's model.
- Real component measurements and visual acceptance remain the responsibility of each invocation. The starter cannot infer dimensions or confirm that an agent actually viewed an image.
- Windows / Python 3.11 / CadQuery 2.8.0 is the execution target used for local validation. Other OS rendering backends have not been exercised here.
- Claude Code and Gemini CLI installation instructions follow their published skill documentation; their complete CAD workflows have not been run for this release.

Reproduce the package tests using the commands in README.md. Do not interpret successful script tests as evidence of end-to-end behavioral equivalence across AI products.
