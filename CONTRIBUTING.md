# Contributing

Use issues for reproducible problems and focused pull requests for fixes. Start with [README.md](README.md) or [README.ja.md](README.ja.md); the agent workflow is in [SKILL.md](SKILL.md).

## Report a problem

Include your OS/architecture, AI tool, skill version, installation method, Python version, `uv --version`, the command or request, expected result and actual error. For a shape problem, include the exact part number and a public source link or material you may share. Remove credentials, personal paths and private drawings before posting.

## Develop and test

Use uv and CPython 3.11, 3.12 or 3.13. There is no fixed Python minor version. From the repository root:

```sh
uv sync --project assets/starter --locked --python 3.13
uv run --project assets/starter --offline python -m unittest discover -s tests -v
```

The Python value above is an example; repeat with the other supported versions when changing compatibility or dependencies. Tests use temporary projects and synthetic geometry. Linux CI uses `xvfb-run -a` for rendering. Do not regenerate unrelated user models as a repository check.

- Preserve external workspace isolation: normal modeling writes only `models/<part-number>/` in the user's project.
- Preserve edited generators and existing project files. Do not introduce automatic workspace migrations or dependency upgrades.
- Keep the English/Japanese README and the project API guide consistent.
- Add a focused behavioral regression when fixing code; do not test documentation by matching its wording.
- Change `uv.lock` only when a dependency change requires it, and explain the reason.
- Keep models, downloaded manufacturer PDFs/photos, credentials, personal paths, environments and caches out of this skill distribution. Examples must be synthetic or appropriately licensed.

Describe the user-visible change, its reason, the checks actually run and remaining limitations. Changes to this repository's code and documentation are contributed under its [MIT license](LICENSE); third-party dependencies and references keep their own terms.
