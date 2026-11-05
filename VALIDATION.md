# Validation scope

This file describes the package's verification scope, not a certification of any component model.

The starter supports **CPython 3.11–3.13** with CadQuery 2.8.0. It has no fixed Python minor-version pin. FreeCAD is not required. The suite contains **9 tests** covering workspace isolation and the CAD pipeline.

Local verification on 2026-11-05 used separate uv environments on Windows x86-64:

| Python | Result |
| --- | --- |
| 3.11.14 | 9 passed, 0 skipped |
| 3.12.12 | 9 passed, 0 skipped |
| 3.13.9 | 9 passed, 0 skipped |

Each version exercised STEP export/reimport, geometry and overlap checks, preview rendering, external workspace isolation and output overrides. The dependency lock is unchanged. See [GitHub Actions](https://github.com/Yarnadori/electronic-component-cad/actions/workflows/ci.yml) for the current Ubuntu/Python matrix results; the committed workflow alone is not evidence of a passing run.

For v0.1.2 (`33153df`), [Ubuntu CI run 41982995763](https://github.com/Yarnadori/electronic-component-cad/actions/runs/41982995763) completed successfully on all three Python versions. Each job ran all 9 tests with no skips. A fresh installation from the public repository also delivered all 34 tracked files to the six targets listed below, allowing only Git's line-ending normalization. The installed initializer created and reused an external workspace without changing the existing user-project file.

The documented range-based bootstrap was also exercised after removing the pin: uv selected Python 3.13.9, created an external workspace/environment, and generated a volume-6 CAD smoke solid without adding files to the user's project.

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
- Windows x86-64 is the local verification platform. CI uses Ubuntu with a virtual display and software rendering support. macOS and other OS/architecture combinations have not been exercised here.
- Claude Code and Gemini CLI installation instructions follow their published skill documentation; their complete CAD workflows have not been run for this release.

Reproduce the package tests using the commands in README.md. Do not interpret successful script tests as evidence of end-to-end behavioral equivalence across AI products.
