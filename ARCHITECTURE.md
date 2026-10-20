# Architecture

```text
registry/<name>/versions/<version>/   source of truth (component.json, README.md, src/)
scripts/build_registry.py             validate + hash -> registry.json (+ website/registry.json)
ai.py                                 stdlib CLI: fetch registry, validate, cache, copy files
website/                              static catalog; reads registry.json
cloudflare/worker.js                  OAuth + publisher API (GitHub App -> pull request)
tests/                                unittest suite
```

## Registry format

Each release is immutable and lives in its own directory. `component.json` describes it:

```json
{
  "name": "keyword-rag",
  "version": "1.1.0",
  "description": "...",
  "category": "retrieval",
  "runtime": "python",
  "license": "MIT",
  "tags": ["rag"],
  "dependencies": ["context-builder@1.1.0 (optional)"],
  "files": ["README.md", "src/keyword_rag.py"],
  "release_notes": "...",
  "source": "registry/keyword-rag/versions/1.1.0"
}
```

`build_registry.py` turns all releases into `registry.json`:

```json
{
  "version": 2,
  "components": [
    {
      "name": "keyword-rag", "description": "...", "category": "...", "runtime": "...", "license": "...", "tags": [],
      "latest_version": "1.1.0",
      "versions": [ { "...full release manifest with sha256...": "" } ]
    }
  ]
}
```

The entry-level fields come from the latest stable release. `versions` is ordered newest first. Dependencies are exact (`name@MAJOR.MINOR.PATCH`, optionally followed by ` (optional)`) and must exist in the registry.

## Install flow

`ai add name[@version]` -> load the registry (network, else per-URL cache) -> validate every manifest -> resolve file URLs relative to the registry location -> fetch all files and verify SHA-256 -> write under `ai_components/<name>/` -> record the files in `.airegistry/lock.json`. `remove` and `update` act only on files recorded in the lock and re-validate each path.

## Rules

- A release is never edited after publication. Fixes ship as a new version; a defective release may be withdrawn.
- Validation lives in `ai.py` and is reused by the builder, so the CLI and the generator cannot disagree.
- State is plain JSON; there is no database. External services are adapters configured in `website/config/public.js` and `cloudflare/`.
- Registry content is untrusted: the CLI copies files and never executes them.
