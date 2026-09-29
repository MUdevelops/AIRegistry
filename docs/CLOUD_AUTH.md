# Optional GitHub sign-in / Cloudflare

The core app needs neither. Nothing here is required for local use.

GitHub OAuth needs a client SECRET, which must never be in browser code. Use a server-side endpoint: `cloudflare/worker.js` implements `/login`, `/callback` (code exchange with the secret, CSRF `state`) and `/me` (HMAC-signed HttpOnly cookie). It is untested against live GitHub; review before use.

Setup:
1. Create a GitHub OAuth App; callback URL `https://YOUR-SITE/auth/callback`.
2. `cd cloudflare && wrangler secret put GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `SESSION_SECRET` (long random string); set `SITE_URL` in `wrangler.toml`.
3. Route `YOUR-SITE/auth/*` to the Worker (same origin keeps the cookie first-party).
4. Edit `website/config/public.js`: `AUTH_URL: "https://YOUR-SITE/auth"`, `GITHUB_CLIENT_ID: "<public id>"`. A "Sign in" link then appears.

Pages: build output directory `website`, no build command. Host the registry by publishing `registry/` and `registry.json` next to the site (or point `REGISTRY_URL` at a raw URL). Note the CLI resolves files relative to `registry.json`.
