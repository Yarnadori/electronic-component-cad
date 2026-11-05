# Electronic Component CAD

[日本語](README.ja.md) · [Skill instructions](SKILL.md) · [Changelog](CHANGELOG.md) · [MIT license](LICENSE)

An [Agent Skills](https://agentskills.io/specification) package that helps coding agents create and correct electronic-component 3D models from product URLs, part numbers, drawings and photographs. It uses **CadQuery + uv** to produce colored STEP files, check dimensions and geometry, and render previews for visual review.

Your project receives only `models/<part-number>/`. Code, references, environments and caches stay in a persistent background workspace. The agent implements each part from evidence; this is not an automatic image-to-CAD converter.

## Requirements

**Python and uv are required to generate models.** Installing the skill's instructions alone does not install the CAD environment.

| Requirement | Purpose |
| --- | --- |
| CPython **3.11, 3.12 or 3.13** | Runs the model generator. No fixed minor-version pin. |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | Manages Python environments and locked dependencies; can also install Python. |
| [Node.js](https://nodejs.org/en/download) **22.20+** and [Git](https://git-scm.com/install/) | Needed for the recommended [skills CLI](https://github.com/vercel-labs/skills) installation. |
| An AI tool with file, shell and image-viewing access | Reads evidence, creates the model and inspects previews. |
| Poppler or another PDF renderer | Needed when drawings are supplied as PDFs. |

The bundled lock selects CadQuery **2.8.0**, whose [package requirement](https://pypi.org/project/cadquery/2.8.0/) is Python 3.11 or newer. This project's supported range is `>=3.11,<3.14`; Python 3.14+ is not enabled yet. CadQuery, VTK and other Python dependencies are installed by uv in the background workspace. FreeCAD is not required.

## Install

### 1. Prepare uv and Python

If uv is missing, install it using the [official instructions](https://docs.astral.sh/uv/getting-started/installation/). For example, on Windows with WinGet:

```powershell
winget install --id=astral-sh.uv -e
```

On macOS with Homebrew:

```sh
brew install uv
```

For Linux and other installation methods, use the official instructions above. Reopen your terminal if the command is not found after installation.

If you do not already have a supported Python, [uv can install it](https://docs.astral.sh/uv/guides/install-python/):

```sh
uv python install 3.13
```

3.13 is an example, not a required pin; 3.11 and 3.12 also work. You do not need a separate Python installer when using uv. Check the environment:

```sh
uv --version
uv python find ">=3.11,<3.14"
node --version
git --version
```

### 2. Install the skill

```sh
npx skills add Yarnadori/electronic-component-cad -g
```

Select your AI tools. `-g` installs to personal skill directories so installer files stay out of the working project. To select tools explicitly:

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

See [additional supported tools](https://github.com/vercel-labs/skills/blob/main/docs/agents.md). `--list` lists the available skill without installing; `--copy` avoids symlinks. Reload the AI tool if the skill is not discovered. These are installation targets; end-to-end modeling behavior in every AI product is not certified.

### Manual alternatives

Choose one installation method per tool. Clone/copy the **whole folder**, including assets, using the name `electronic-component-cad`:

| Tool | Manual personal location |
| --- | --- |
| Codex | `~/.codex/skills/electronic-component-cad/` (or the configured Codex home) |
| Claude Code | `~/.claude/skills/electronic-component-cad/` ([documentation](https://code.claude.com/docs/en/skills)) |
| Gemini CLI | `gemini skills install https://github.com/Yarnadori/electronic-component-cad.git` ([documentation](https://geminicli.com/docs/cli/skills/)) |

Other tools can use their supported Agent Skills directory or read `SKILL.md` explicitly. `agents/openai.yaml` is optional Codex display metadata; the workflow uses no vendor-specific API. A manual clone does not require Node.js, but model generation still requires Python and uv.

## Use

In Codex, supply a product URL or part number:

```text
$electronic-component-cad
Create a KiCad STEP model for this product: <product URL>
```

Claude Code uses `/electronic-component-cad`. You can also request corrections to an existing model. The agent checks drawings/photos, writes CadQuery geometry, reimports the exported STEP, checks dimensions/solids/colors/overlaps, and inspects rendered images.

Outputs include the STEP, previews, validation records and notes under `models/<part-number>/`. Editable code and provenance remain in the background workspace and can be provided on request. The same resolved project path reuses the same workspace. Moving the project to a different path creates a separate workspace.

## Update

Updates are **manual**. For a personal skills CLI installation:

```sh
npx skills update electronic-component-cad -g
```

For a manual Git clone, run `git pull --ff-only` inside that clone. Follow the relevant tool's method for other installation types. See the [skills CLI reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) and [changelog](CHANGELOG.md).

Updating instructions does not automatically overwrite edited workspaces, switch their Python version, regenerate models or remove files created by older versions. Existing workspaces may retain their earlier Python selection; changing it is a separate explicit operation.

## Troubleshooting and limits

| Symptom | Action |
| --- | --- |
| `uv` or another command is missing | Install it and restart the terminal/AI tool so its PATH is refreshed. |
| No compatible Python is found | Use `uv python install 3.13`, then check the supported range above. |
| Dependencies cannot be downloaded | First-time setup needs network access; `--offline` requires installed/cached dependencies. |
| A PDF cannot be inspected | Install a PDF renderer or supply usable drawing images; do not claim visual review from text alone. |
| Preview rendering fails | Check the rendering backend in the actual OS/headless environment; see [validation scope](VALIDATION.md). |

The skill respects host permissions. It does not disable download/write restrictions. Manufacturer PDFs, photos and component models are not distributed in this package. KiCad placement, printability, thread fit and thermal/electrical performance require their own checks.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for reporting issues and testing changes, [VALIDATION.md](VALIDATION.md) for recorded checks, and the [project API guide](references/project-api.md) for internal workspace commands and explicit standalone-library mode.

Code and instructions are [MIT licensed](LICENSE). Dependencies and externally obtained references retain their own licenses.
