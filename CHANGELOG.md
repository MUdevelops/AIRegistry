# Changelog

## 2.3.1

- Publishing: the CLI is published to PyPI (`pip install airegistry-cli`) with Trusted Publishing.
- Packaging: SPDX license expression (`license = "MIT"`), as required by current setuptools.
- Tests: complete the standard-library fallback list so the suite passes on Python 3.9.
- README: absolute links so the page renders correctly on PyPI.

## 2.3.0

Catalog and tooling refresh.

### Components

- **Every component is now released at 1.1.0 or later** with type hints, docstrings, input validation, a consistent README (install, quick start, API, behavior, changes) and a full test suite. The 1.0.0 releases of the eight existing components are kept unchanged, so `name@1.0.0` pins keep working.
- **agent 1.0.0** replaces the 0.1.0 prototype with `run_agent()`, structured `Step`/`AgentRun` records, error capture and `tool-router` support.
- **query-rewriter 1.1.0** and **retrieval-pipeline 1.1.0** are the first working releases. Their 1.0.0 releases were withdrawn: `retrieval_pipeline.py` contained a stray markdown fence (SyntaxError) and `query-rewriter` imported a module it never shipped.
- **Removed** the prototype and placeholder components `chat`, `citations`, `memory`, `rag` and `example`. Use `citation-builder`, `conversation-memory` and `keyword-rag` instead.
- Behavior fixes: `prompt-builder` no longer re-expands substituted values; `conversation-memory` ids are never reused after trimming; `context-builder` no longer mutates `sys.path` and `keyword-rag` is now optional; `keyword-rag` computes document frequencies once per query.

### CLI (`ai`)

- `name@version` references work in `info`, `add` and `update`, backed by the versioned registry format.
- The CLI no longer breaks when installed with `pip install .`: without a `registry.json` next to `ai.py` it uses the public registry instead of a path inside `site-packages`.
- Registry caches are kept per registry URL, so switching registries can no longer serve stale data.
- Clearer messages for already-installed components, unknown versions and invalid registries; aligned tables; `--version`; `ai update <component>`.
- Optional dependencies are shown separately from required ones.

### Registry and tooling

- One layout: `registry/<name>/versions/<version>/`. The duplicated flat copies and the migration script were removed.
- `scripts/build_registry.py` validates every release (metadata, listed files, SHA-256, dependency targets, Python syntax) and fails on unlisted files.
- New test suite covering the CLI, the builder, registry integrity and every component.
- CI runs on Python 3.9, 3.11 and 3.13.

### Website and publisher

- The catalog reads the versioned registry and lists every release of a component.
- The publisher accepts new releases of existing components and `name@version` dependencies (plain names are resolved to the latest release).

### Documentation

- README rewritten; unresolved merge-conflict markers removed.
- `SECURITY.md` now points to GitHub private vulnerability reporting.

## 2.2.0

Public launch: redesigned catalog, documented contribution flow, monitoring, GitHub-based publisher.

## 2.1.0

Versioned, immutable releases and `name@version` references.

## 2.0.0

New professional component catalog; development components removed from the production registry.
