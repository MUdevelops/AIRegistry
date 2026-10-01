# Architecture

AIRegistry v2.1 is a static-first, Git-backed component registry with a dependency-free Python CLI, a vanilla static website, and a Cloudflare Worker publisher/authentication adapter.

## Source of truth

```text
registry/<component>/versions/<version>/
  component.json
  README.md
  src/...
```

Each release is immutable. A new change creates a new semantic version directory; existing releases are never overwritten.

`scripts/build_registry.py` validates every release, calculates SHA-256 checksums, determines the latest release, and generates:

- `registry.json`
- `website/registry.json`

The generated registry uses schema version 2:

```text
component
  ├── latest_version
  └── versions[]
```

## CLI

The CLI loads the registry from a local path or HTTPS URL, validates the schema, caches it, resolves `name` or `name@version`, verifies every downloaded file with SHA-256, and records the exact installed version in `.airegistry/lock.json`.

Examples:

```text
ai search rag
ai info rag
ai info rag@0.1.0
ai add rag
ai add rag@0.1.0
ai update
ai remove rag
```

The CLI has no runtime third-party dependencies. It can be installed as a console script with:

```text
python -m pip install .
```

## Publisher

The website sends authenticated submissions to the Cloudflare Worker. The Worker is authoritative for validation and creates a GitHub branch, commit, and pull request.

Two release modes are supported:

- New Component
- New Version

A new version must be greater than the current latest release and must not already exist. Dependencies use exact `name@version` references. The Worker verifies that referenced component releases exist.

The Worker writes the immutable release under:

```text
registry/<name>/versions/<version>/
```

and updates both generated registry indexes in the proposed pull request.

## Security boundaries

- Browser validation is UX only.
- Worker validation is authoritative.
- Published release files are checksum protected.
- File paths are restricted to safe relative paths.
- Public submissions never write directly to `main`.
- OAuth uses PKCE, signed sessions, secure cookies, and security headers.
- Secrets remain server-side.

## Deployment

Cloudflare deployment uses the root `wrangler.jsonc`. `cloudflare/wrangler.toml` is obsolete and should not be used.
