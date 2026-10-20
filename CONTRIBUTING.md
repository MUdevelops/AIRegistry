# Contributing to AIRegistry

Thanks for helping improve AIRegistry.

AIRegistry is intentionally source-first: a useful component should be small enough to inspect, simple enough to understand, and specific enough to reuse.

## Ways to contribute

### Improve the core project

For changes to the CLI, registry builder, website, tests, documentation, or Cloudflare Worker:

1. Fork the repository.
2. Create a focused branch from `main`.
3. Make the complete change, including tests and documentation where applicable.
4. Run the local validation commands below.
5. Open a Pull Request against `main`.

Keep unrelated refactors out of the same PR unless they are required for the change.

### Submit a registry component

You can also use the public registry's **Submit Component** flow after signing in with GitHub.

The web publisher validates the submission and creates a Pull Request for maintainer review. The publisher does not write directly to `main`.

## Component structure

Every release lives in its own directory and is immutable once merged:

```text
registry/<name>/versions/<version>/
├── component.json
├── README.md
└── src/
    └── <implementation>.py
```

`component.json` must contain `name`, `version`, `description` (280 characters or less), `category`, `runtime`, `license`, `tags`, `dependencies`, `files`, `release_notes` and `source` (`registry/<name>/versions/<version>`). The directory names must match `name` and `version`.

Rules the builder enforces:

- lowercase name using letters, digits and hyphens; `MAJOR.MINOR.PATCH` version
- `files` lists every file in the release (nothing unlisted), including `README.md` and at least one file under `src/`
- dependencies are exact references, for example `keyword-rag@1.1.0` or `keyword-rag@1.1.0 (optional)`, and must exist in the registry
- Python sources must compile; files must not be empty
- unique, safe relative file paths and no executables, installers, credentials or build artifacts

To publish a **new version**, add a new `versions/<version>/` directory. Never edit a published release; fixes ship as a new version.

## Component quality bar

Prefer one clear responsibility over a broad framework.

- Standard library only, Python 3.9+ compatible (`from __future__ import annotations` for modern type hints).
- Module docstring, `__all__`, `__version__` matching the release, type hints and docstrings on public functions.
- Validate inputs and raise `TypeError`/`ValueError` with clear messages. No network calls or side effects at import time.
- A README with **Install**, **Quick start**, **API** and **Behavior** sections, including `ai add <name>@<version>`.
- Tests in `tests/` covering normal use, edge cases and invalid input.
- Declare AIRegistry dependencies in `component.json` instead of assuming they exist, and mark them `(optional)` when the component works without them.
- Only submit code you have the right to redistribute.

## Local validation

From the repository root:

```bash
python scripts/build_registry.py --check
python -W error -m unittest discover -s tests -v
python -m py_compile ai.py scripts/build_registry.py
node --check website/app.js
node --check cloudflare/worker.js
```

If you intentionally changed registry component metadata or files, rebuild the generated indexes before opening the PR:

```bash
python scripts/build_registry.py
python scripts/build_registry.py --check
```

## Pull Requests

A good PR should explain:

- what changed
- why the change belongs in AIRegistry
- how it was tested
- whether the registry index changed
- whether documentation changed

For a new component, include a short description of the use case and a copy-pasteable example.

Maintainers may request changes before merging. Passing CI is required, but CI passing does not by itself guarantee a component will be accepted; source quality, scope, documentation, and compatibility are also reviewed.

## Release and generated files

Do not edit `registry.json` or `website/registry.json` by hand. They are generated from the release directories.

Do not commit local deployment state such as `.wrangler/`, Python `__pycache__/` directories, compiled `.pyc` files, or local installation directories.

## Security reports

Do not publish sensitive vulnerability details in a public issue. Follow [SECURITY.md](SECURITY.md) for the supported reporting route.
