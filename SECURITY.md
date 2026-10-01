# Security

Registry components are untrusted code. AIRegistry copies files and never executes them; review what you add before running it.

The CLI: no shell/exec, no install scripts, no binaries (`.exe .dll .so .dylib .bat .cmd .ps1 .msi .com .scr .jar` rejected), no absolute, `..`, backslash, drive-letter or symlink-escaping paths, 2 MB fetch cap, SHA-256 verification when the registry provides hashes. Dependencies are displayed, never installed. Checksums detect corruption/tampering of files, not a malicious registry: only use registries you trust.

Secrets never belong in `website/`. See docs/CLOUD_AUTH.md.

Report vulnerabilities privately to the maintainers (add a contact address here before publishing).
