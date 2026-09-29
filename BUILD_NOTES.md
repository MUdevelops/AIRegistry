# Build notes

- Python tested: 3.12.3 (requires 3.11+; stdlib only)
- CLI: `python ai.py search rag` (see README for all commands)
- Website: `python -m http.server -d website 8000` -> http://localhost:8000
- Tests: `python -m unittest discover -s tests` (19 tests, pass)
- Regenerate index: `python scripts/build_registry.py` (`--check` to verify)
- ZIP size: 26303 bytes

Values to configure later (none needed locally):
- `website/config/public.js`: REGISTRY_URL, AUTH_URL, GITHUB_CLIENT_ID (public values only)
- Cloudflare Worker secrets: GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, SESSION_SECRET; var SITE_URL in cloudflare/wrangler.toml
- GitHub OAuth App callback URL: https://YOUR-SITE/auth/callback
- Cloudflare Pages: output dir `website`, no build command
- SECURITY.md: add a vulnerability contact; LICENSE: set copyright holder
- Worker is not tested against live GitHub/Cloudflare.
