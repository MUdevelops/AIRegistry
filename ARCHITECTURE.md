# Architecture

    registry/<name>/   source of truth (component.json + files)
    scripts/build_registry.py  validate + hash -> registry.json (+ website/registry.json)
    ai.py              stdlib CLI: fetch registry (path or http/https), validate, cache, copy files
    website/           static site; reads registry.json; config/public.js holds browser-safe config
    cloudflare/        optional OAuth Worker adapter
    tests/             unittest

Flow: `ai add x` -> load registry (network, else cache) -> validate every manifest -> resolve file URLs relative to the registry location -> fetch all files, verify SHA-256 -> write under `ai_components/x/` -> record files in `.airegistry/lock.json`. `remove` and `update` act only on files in the lock, re-validating each path.

Validation lives in `ai.py` and is reused by the index builder, so CLI and generator cannot disagree. State is plain JSON; there is no database. External services are adapters configured in `website/config/public.js` and `cloudflare/`.
