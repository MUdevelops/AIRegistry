# Contributing

1. Create `registry/<name>/` with `component.json`, `README.md`, `src/`.
2. Keep components tiny, readable, dependency-light, with no network calls at import and no install scripts.
3. Use a permissive license (MIT/Apache-2.0/BSD) and only code you may share.
4. Run `python scripts/build_registry.py` then `python -m unittest discover -s tests`.
5. Open a PR with a short description. Changes to `ai.py` need tests.

Names: lowercase letters, digits, hyphens (max 40). Versions: `MAJOR.MINOR.PATCH`; bump on any change.
