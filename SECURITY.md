# Security

Registry components are untrusted source code. AIRegistry copies files and never executes component code during installation.

## CLI protections

- No shell execution or install scripts.
- Executable and installer file extensions are rejected.
- Absolute, traversal, drive-letter, backslash, and symlink-escaping paths are rejected.
- Download size is capped.
- Every published release has SHA-256 file checksums.
- Installed versions and checksums are recorded in `.airegistry/lock.json`.
- Dependencies are displayed and are not installed automatically.

Checksums protect against content corruption or tampering after a registry entry is published. They do not make arbitrary third-party source trustworthy; review component source before using it.

## Publisher protections

- GitHub OAuth uses PKCE and signed server-side sessions.
- Secure, HttpOnly cookies and security headers are enabled.
- Browser validation is not trusted; the Worker validates submissions independently.
- Public submissions are proposed through GitHub Pull Requests rather than direct writes to `main`.
- Existing component releases are immutable.
- New releases must use an exact semantic version and exact dependency versions.
- Publisher secrets and GitHub App credentials remain server-side.

## Reporting a vulnerability

For a security issue, use the repository's GitHub Security Advisory/private vulnerability reporting mechanism when available. Do not disclose credentials, private keys, session tokens, or exploitable details in a public issue.

Security-sensitive configuration belongs in Cloudflare Worker environment variables/secrets, never in `website/` or committed source.
