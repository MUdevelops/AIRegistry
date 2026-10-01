# AIRegistry

<p align="center">
  <strong>Install AI capabilities, not libraries.</strong>
</p>

<p align="center">
  An open-source registry and dependency-free CLI for reusable AI components, agents, tools, workflows, and project templates.
</p>

<p align="center">
  <a href="https://github.com/MUdevelops/AIRegistry">GitHub</a>
  ·
  <a href="https://github.com/MUdevelops/AIRegistry/issues">Issues</a>
  ·
  <a href="https://github.com/MUdevelops/AIRegistry/pulls">Contributing</a>
</p>

---

## What is AIRegistry?

AI projects repeatedly rebuild the same small building blocks:

- retrieval
- memory
- agent loops
- citations
- chat starters
- reusable tools

AIRegistry packages these building blocks as **small, readable, auditable source components**.

Search one.

Inspect it.

Add it.

Own the source.

```text
search → inspect → add → build

## Versioned releases

AIRegistry v2.1 treats every component release as immutable.

```text
ai info rag
ai info rag@0.1.0
ai add rag
ai add rag@0.1.0
ai update
```

A component can have multiple releases. The registry resolves an unversioned reference to the latest stable release and an explicit `name@version` reference to exactly that release.

### Install the CLI

The CLI has no runtime third-party dependencies. For a developer checkout:

```powershell
python -m pip install .
```

Then:

```powershell
ai search rag
ai info rag@0.1.0
```

### Publishing

Authenticated publishers can submit either a new component or a new version. Every submission is validated by the Cloudflare Worker and proposed through a GitHub Pull Request. Existing releases are immutable.
