# Electronic Component CAD

[日本語](README.ja.md) · [Skill instructions](SKILL.md) · [MIT license](LICENSE)

An [Agent Skills](https://agentskills.io/specification) package for creating and correcting electronic-component 3D models from product URLs, part numbers, drawings and photographs. It guides a coding agent through **CadQuery + uv**, colored STEP export, independent dimension checks, STEP roundtrip checks and visual review.

The package includes an isolated background workspace with an empty component catalog, generator templates, a locked environment, STEP validation and VTK preview rendering. The agent still implements the target's geometry from evidence; this is not an automatic image-to-CAD converter.

## Install in your AI tool

Use the [skills CLI](https://github.com/vercel-labs/skills) with Node.js 22.20+ and Git:

```sh
npx skills add Yarnadori/electronic-component-cad -g
```

Select the AI tools in the installer. The recommended `-g` installs to your personal skill directories, keeping skill files out of the working project. Omit it only when you deliberately want a project-scoped skill installation. To choose several tools explicitly:

```sh
npx skills add Yarnadori/electronic-component-cad -g -a codex claude-code gemini-cli cursor github-copilot windsurf
```

| Tool | `--agent` value |
| --- | --- |
| Codex | `codex` |
| Claude Code | `claude-code` |
| Gemini CLI | `gemini-cli` |
| Cursor | `cursor` |
| GitHub Copilot | `github-copilot` |
| Windsurf | `windsurf` |

The CLI supports [additional agents](https://github.com/vercel-labs/skills/blob/main/docs/agents.md) and chooses their directories, including shared `.agents/skills` directories. Use `--list` to preview this repository's skill without installing, or `--copy` to copy files instead of using symlinks. The repository contains one root-level skill, including its scripts and starter assets; no separate package publication is needed for this GitHub install command. See the [CLI reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) for update and removal commands.

### Manual alternatives

Choose one installation method per tool. For manual installation, keep the folder name `electronic-component-cad` and clone **the whole folder**, including assets. These commands work in a POSIX shell or PowerShell; a custom Codex home may require a different destination.

**Codex**, default personal location:

```sh
git clone https://github.com/Yarnadori/electronic-component-cad.git "$HOME/.codex/skills/electronic-component-cad"
```

**Claude Code**, [personal skills location](https://code.claude.com/docs/en/skills):

```sh
git clone https://github.com/Yarnadori/electronic-component-cad.git "$HOME/.claude/skills/electronic-component-cad"
```

**Gemini CLI**, [skill installation](https://geminicli.com/docs/cli/skills/):

```sh
gemini skills install https://github.com/Yarnadori/electronic-component-cad.git
```

Other Agent Skills hosts can load the same `SKILL.md` from their supported skill directory. Without automatic skill discovery, explicitly ask the agent to read `SKILL.md` and follow its linked references. `agents/openai.yaml` is optional Codex UI metadata; the core workflow uses no Codex-specific APIs. Do not clone over an existing installation; update it deliberately. Reload/restart the host if it does not discover the new skill.

## Use it

In Codex:

```text
Use $electronic-component-cad to create a KiCad STEP model for this product:
<product URL>
```

In Claude Code, invoke `/electronic-component-cad` with the product URL. In other hosts, request the skill by name or provide its `SKILL.md` path. You can also request a correction to an existing model, with the target part and observed defect.

Your project receives only `models/<part-number>/`, containing the colored STEP, previews, validation records and model notes. Source code, downloaded references, environments and caches stay in a persistent workspace outside your project. The same project reuses its workspace for corrections and regeneration; editable source remains available on request. The agent handles this setup in the background.

## Requirements and boundaries

- File read/write, shell execution, and an image-viewing capability in the agent environment.
- uv and Python 3.11. The bundled lock selects CadQuery 2.8.0 and its dependencies.
- Poppler (`pdfinfo`, `pdftoppm`) or another PDF renderer for supplied drawings.
- Network access for original sources and initial dependencies, or locally supplied references and a populated package cache.

The skill respects the current host's permissions and existing project conventions. It does not disable download restrictions, publish a user's drawings, or add unrelated components. Manufacturer PDFs/photos and previously generated component models are **not included** in this distribution. Dependencies retain their own licenses.

Windows CAD export/rendering and the standalone starter are exercised by the package tests. Other OS backends and end-to-end operation in Claude Code/Gemini CLI have not been tested. The agent must still inspect the actual drawings and final images. KiCad placement, printability and mechanical/thermal/electrical performance require their own checks.

## Workspace setup for agents

```sh
python /path/to/electronic-component-cad/scripts/init_project.py /path/to/user-project --json
```

The initializer returns a workspace outside the user project. Existing project files and edited workspace sources are preserved. Follow [the project API guide](references/project-api.md) for internal commands, storage locations and an optional override. Keep setup commands and workspace paths out of routine user-facing output.

`--standalone` is an explicit alternative for creating an editable CAD library directly in a new/empty directory; it refuses an occupied destination. Existing CAD libraries should reuse their pipeline. Files created in a project by older versions are not automatically moved or deleted.

## Development checks

From this repository root, install the starter's locked dependencies and run the tests:

```sh
uv sync --project assets/starter --locked
uv run --project assets/starter --offline python -m unittest discover -s tests -v
```

Tests exercise external workspace creation/reuse, project isolation, refusal to overwrite unrecognized workspaces, no fallback into the project on setup failure, explicit standalone setup, incomplete-template guards, colored STEP export/reimport, output overrides, overlap rejection and previews in temporary projects. Rendering is checked for output creation; human/agent visual inspection remains a separate step. See [validation notes](VALIDATION.md) for the recorded verification scope.

When contributing, keep the skill vendor-neutral, keep sample geometry synthetic or appropriately licensed, and test any scripts in isolation. Do not include downloaded datasheets, product photos, credentials, local environments or personal paths.
