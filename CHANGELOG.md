# Changelog

## 2.1.0

- Introduced immutable versioned component releases under `registry/<name>/versions/<version>/`.
- Added schema v2 generated registry indexes with latest-version resolution and release history.
- Added exact `name@version` CLI references, version-aware locks, installs, info, search, and updates.
- Added exact version dependencies.
- Added publisher support for new components and new releases with duplicate/version-order validation.
- Added website release history and version selection.
- Added migration tooling and expanded automated validation.

## 2.0.0

- New professional component catalog: prompt-builder, text-chunker, json-validator, citation-builder, conversation-memory, keyword-rag, context-builder, tool-router (all 1.0.0, MIT, stdlib only).
- Removed development/test components `hello-ai` and `publisher-demo` from the production registry.
- Added tests for the new components.
