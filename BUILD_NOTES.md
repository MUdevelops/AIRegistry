# Build Notes

## Current V2.1 architecture

- Python CLI with no runtime third-party dependencies.
- Immutable component releases under `registry/<name>/versions/<version>/`.
- Schema v2 generated registry indexes in `registry.json` and `website/registry.json`.
- Cloudflare Worker handles GitHub OAuth, signed sessions, and GitHub App pull-request publishing.
- Website is static HTML/CSS/JavaScript.

## Validation

The release suite covers CLI behavior, version resolution, exact dependencies, registry generation, checksums, path safety, lock integrity, and component smoke tests.

Current catalog: 13 components / 13 initial releases.

## Deployment configuration

The root `wrangler.jsonc` is the authoritative Cloudflare configuration. OAuth and GitHub App secrets are configured in Cloudflare and are never committed.

For local development:

```powershell
python -m unittest discover -s tests -v
python scripts/build_registry.py --check
node --check cloudflare/worker.js
node --check website/app.js
```

For CLI installation:

```powershell
python -m pip install .
```
