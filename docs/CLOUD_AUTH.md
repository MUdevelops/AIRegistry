# Cloudflare Authentication and Publisher

AIRegistry uses the Cloudflare Worker as the authentication and publisher boundary.

## Authentication

GitHub OAuth uses PKCE and a signed session cookie. The browser only receives the authenticated identity; GitHub access tokens and the GitHub App private key remain server-side.

## Publishing

Authenticated users submit a new component or a new immutable component version. The Worker validates the request, verifies exact dependency releases, writes the release under `registry/<name>/versions/<version>/`, updates generated registry indexes, and creates a GitHub Pull Request against `main`.

## Required Worker configuration

Configure the GitHub OAuth and GitHub App values as Cloudflare environment variables/secrets. Never commit these values.

The root `wrangler.jsonc` is the authoritative deployment configuration.
