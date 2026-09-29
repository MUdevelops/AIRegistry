# AIRegistry

An open-source registry and CLI for reusable AI components, agents, tools, workflows and project templates.

## Why

AI projects keep re-implementing the same small pieces (retrieval, memory, agent loops, citations). AIRegistry treats them like packages: search, inspect, and copy small, readable, auditable source into your project. Components are plain files; you own them after `add`.

No paid APIs, accounts, npm/pip packages, Docker or database are needed. Python 3.11+ and a browser are enough.

## Quick start

    python ai.py search rag
    python ai.py info rag
    python ai.py add rag            # copies files to ./ai_components/rag/
    python ai.py list
    python ai.py update
    python ai.py remove rag

Optional alias: `alias ai="python /path/to/ai.py"` (Windows: `doskey ai=python C:\path\ai.py $*`).

Website: `python -m http.server -d website 8000` then open http://localhost:8000

Tests: `python -m unittest discover -s tests`

## CLI

| Command | Purpose |
|---|---|
| `ai search <query>` | Search name, description, category, tags (cached registry used if offline) |
| `ai info <name>` | Show manifest, files, dependencies |
| `ai add <name> [--dir D] [--force] [--dry-run]` | Copy component files; lists every file and dependency first |
| `ai remove <name> [--dry-run]` | Delete only the files recorded in `.airegistry/lock.json` |
| `ai list [--all]` | Installed components (or whole registry) |
| `ai update [--dry-run]` | Refresh registry, upgrade installed components (overwrites local edits) |
| `ai config [registry_url <v>]` | Show/set config |

`--offline` (search/info/add/update) uses only the cache in `~/.airegistry/` (override with `AIREGISTRY_HOME`).
Set the registry with env `REGISTRY_URL` or `ai config registry_url <path-or-https-url>`. Default: the bundled `registry.json`.
Remote example: `REGISTRY_URL=https://raw.githubusercontent.com/OWNER/REPO/main/registry.json` (files are fetched relative to it).

## Component structure

    registry/<name>/component.json   manifest
    registry/<name>/README.md
    registry/<name>/src/...

Manifest fields: `name`, `version` (MAJOR.MINOR.PATCH), `description`, `category`, `runtime`, `license`, `tags`, `files` (relative paths), `source` (`registry/<name>`), optional `dependencies` (shown, never installed automatically).

After changing components run `python scripts/build_registry.py` (regenerates `registry.json` and `website/registry.json` with SHA-256 checksums) and `python scripts/build_registry.py --check` in CI.

## Security

Components are untrusted. The CLI only writes files: no shell, no install scripts, no execution. It rejects absolute paths, `..`, backslashes, drive letters, symlink escapes and executable extensions, and verifies checksums. See SECURITY.md.

## Deploy

Cloudflare Pages: output directory `website`, no build command. Optional GitHub sign-in is described in docs/CLOUD_AUTH.md.

## Contributing

See CONTRIBUTING.md. Add a directory under `registry/`, build the index, run tests, open a PR.

## Roadmap

- Component signing and pinned versions
- `ai publish` / remote registry hosting
- Dependency resolution between components
- Per-component tests and richer categories
- Optional accounts, stars and download counts (via Worker)
