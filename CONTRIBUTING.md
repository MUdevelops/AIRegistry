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

A component must live at:

```text
registry/<name>/
├── component.json
├── README.md
└── src/
    └── <implementation>
```

The current publisher expects:

- a lowercase component name using letters, digits, and hyphens
- a `MAJOR.MINOR.PATCH` version
- a description of 280 characters or less
- a valid category, runtime, and license
- up to 12 tags
- up to 20 dependencies
- at least two files total
- `README.md`
- at least one file under `src/`
- unique, safe relative file paths
- text files within the publisher size limits

Do not include executable installers, shell scripts, credentials, tokens, private keys, or generated build/cache artifacts.

## Component design guidelines

Prefer one clear responsibility over a broad framework.

Avoid network calls during import unless the component's documented purpose requires them.

Avoid install scripts and hidden side effects.

Use the Python standard library when it keeps the component portable and understandable.

Document the public API and provide a minimal usage example.

Declare AIRegistry component dependencies in `component.json` rather than silently assuming they exist.

Only submit code and assets that you have the right to redistribute.

## Local validation

From the repository root:

```bash
python scripts/build_registry.py --check
python -m unittest discover -s tests -v
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

Do not manually edit `registry.json` or `website/registry.json` to add a component. These indexes are generated from the component directories.

Do not commit local deployment state such as `.wrangler/`, Python `__pycache__/` directories, compiled `.pyc` files, or local installation directories.

## Security reports

Do not publish sensitive vulnerability details in a public issue. Follow [SECURITY.md](SECURITY.md) for the supported reporting route.
