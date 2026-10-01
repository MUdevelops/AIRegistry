# AIRegistry Monitoring & Operations

This document covers the small operational layer used to keep the public AIRegistry service observable without adding a separate application server or database.

## What is monitored

AIRegistry has three operational surfaces:

| Surface | What to watch |
|---|---|
| Static catalog | page availability and `/registry.json` availability |
| Cloudflare Worker | request outcomes, errors, latency, authentication routes |
| Publisher | submission failures and GitHub API failures |

The Worker emits structured console events for important request lifecycle events. Cloudflare Workers Logs can collect, filter, and analyze invocation logs, custom logs, errors, and uncaught exceptions.

## Worker observability

The Wrangler configuration should enable Workers Logs for the production Worker:

```json
"observability": {
  "enabled": true,
  "head_sampling_rate": 1
}
```

Cloudflare documents `head_sampling_rate` as a value from `0` to `1`; `1` records every request. For a low-volume public registry, full sampling is a practical default.

After deployment, view the logs in:

**Cloudflare Dashboard → Workers & Pages → AIRegistry → Observability**.

For live debugging from the project directory:

```bash
npx wrangler tail
```

Wrangler supports filtering the live stream by status, method, search text, sampling rate, and Worker version.

## Events emitted by AIRegistry

The Worker uses structured `console.log()` entries with an event name and safe operational fields.

The current deployment emits lifecycle events such as:

```text
request.complete
request.unhandled_error
auth.login.start
auth.callback.success
```

The `request.complete` event includes the HTTP method, route, response status, and duration in milliseconds. Publisher failures are also visible through their HTTP response status and any uncaught Worker error event.

Sensitive values must never be logged. Do not log OAuth codes, access tokens, GitHub App private keys, client secrets, session secrets, or raw submitted source code.

## Health endpoint

The Worker exposes:

```text
GET /api/health
```

A healthy response is a JSON object containing `ok: true` and service metadata. This endpoint is intentionally lightweight and does not call GitHub APIs, so it verifies that the Worker itself is reachable rather than claiming that the entire publisher dependency chain is healthy.

Use it for a basic uptime probe:

```bash
curl -i https://airegistry.instantregret96.workers.dev/api/health
```

For production, point your uptime monitor at `/api/health` and separately monitor `/registry.json` so static-catalog failures are visible as a distinct signal.

Cloudflare also provides health-check functionality for supported setups; its current health-check workflow is managed from **Traffic → Health Checks**.

## Incident triage

When the site is unavailable:

1. Open `/api/health`.
2. Open `/registry.json`.
3. Check Cloudflare Workers Logs.
4. Check the latest Worker deployment/version.
5. Test `/auth/me`.
6. If only publishing is broken, test `/api/publisher/status` after signing in.
7. Check the GitHub repository's Actions and open Pull Requests.

Interpret failures by surface rather than assuming the whole platform is down.

## Production domain

Use a Cloudflare Custom Domain for the canonical production hostname when the domain is available. Cloudflare recommends Custom Domains when the Worker is the application's origin, and it provisions the DNS record and certificate for the Worker.

Keep the existing `workers.dev` hostname available during migration and validation.
