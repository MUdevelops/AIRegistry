# Security

Registry components are untrusted code. AIRegistry copies files and never executes them; review what you add before running it.

## What the CLI enforces

No shell or exec, no install scripts, no binaries (`.exe .dll .so .dylib .bat .cmd .ps1 .msi .com .scr .jar` are rejected), no absolute, `..`, backslash, drive-letter or symlink-escaping paths, a 2 MB fetch cap, and SHA-256 verification when the registry provides hashes. Dependencies are displayed, never installed.

Checksums detect corruption or tampering of files, not a malicious registry: only use registries you trust.

Secrets never belong in `website/`. See [docs/CLOUD_AUTH.md](docs/CLOUD_AUTH.md).

## Reporting a vulnerability

Please report vulnerabilities privately through GitHub: open the repository's **Security** tab and choose **Report a vulnerability** ([github.com/MUdevelops/AIRegistry/security/advisories/new](https://github.com/MUdevelops/AIRegistry/security/advisories/new)). Do not open a public issue for security problems.

Include the affected version, steps to reproduce and the impact. Reports about the CLI, the registry builder, the Cloudflare Worker or a published component are all in scope.
