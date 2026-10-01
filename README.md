<div align="center">

<img src="./readme_assets/Header.png" alt="AIRegistry — futuristic header" width="100%"/>

<br/>

<img src="./readme_assets/AIRegistry-animated-name.gif" alt="AIRegistry animated wordmark" width="760"/>

<p>
  <strong>Install AI capabilities, not libraries.</strong>
</p>

<p>
  An open-source registry and dependency-free CLI for reusable AI components,
  agents, tools, workflows, and project templates.
</p>

<p>
  <a href="https://github.com/MUdevelops/AIRegistry/releases/tag/v2.1.0"><img src="https://img.shields.io/badge/release-v2.1.0-0ea5e9?style=for-the-badge&logo=github&logoColor=white" alt="v2.1.0"></a>
  <a href="https://github.com/MUdevelops/AIRegistry/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-7c3aed?style=for-the-badge" alt="MIT License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-%3E%3D3.9-22c55e?style=for-the-badge&logo=python&logoColor=white" alt="Python >= 3.9"></a>
</p>

<p>
  <a href="https://github.com/MUdevelops/AIRegistry">GitHub</a>
  ·
  <a href="https://airegistry.instantregret96.workers.dev">Live Registry</a>
  ·
  <a href="https://github.com/MUdevelops/AIRegistry/issues">Issues</a>
  ·
  <a href="https://github.com/MUdevelops/AIRegistry/pulls">Contribute</a>
</p>

</div>

---

## ✦ What is AIRegistry?

AI projects repeatedly rebuild the same small building blocks:

`retrieval` · `memory` · `agents` · `citations` · `prompts` · `tools` · `validation`

**AIRegistry turns those building blocks into versioned, discoverable, auditable source components.**

```text
discover → inspect → verify → add → build → share
```

The goal is simple:

> **Reuse the capability. Own the source. Pin the version.**

<div align="center">
  <img src="./readme_assets/Central%20Hub.png" alt="AIRegistry central component hub" width="720"/>
</div>

---

## ⚡ Why AIRegistry?

<table>
<tr>
<td width="50%" valign="top">

### Versioned by design

Every published component release lives in an immutable version path:

```text
registry/
└── component/
    └── versions/
        └── 1.0.0/
```

Use an exact release when reproducibility matters:

```bash
ai add rag@0.1.0
```

</td>
<td width="50%" valign="top">

### Verified before use

Each release records its files and SHA-256 integrity metadata.

```text
resolve exact version
        ↓
validate source
        ↓
verify checksums
        ↓
install + lock
```

</td>
</tr>
<tr>
<td valign="top">

### Developer-first CLI

No runtime third-party dependencies.

```bash
ai search rag
ai info rag@0.1.0
ai add rag@0.1.0
ai update
```

</td>
<td valign="top">

### Community publishing

New components and releases go through the GitHub contribution workflow.

```text
submit
  ↓
branch + commit
  ↓
pull request
  ↓
CI + review
  ↓
merge
  ↓
registry release
```

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Install the CLI

From a local checkout:

```powershell
python -m pip install .
```

Then discover a component:

```bash
ai search rag
```

Inspect the latest release:

```bash
ai info rag
```

Inspect an exact release:

```bash
ai info rag@0.1.0
```

Install the exact release:

```bash
ai add rag@0.1.0
```

Preview the operation first:

```bash
ai add rag@0.1.0 --dry-run
```

See installed components:

```bash
ai list
```

Update installed components to newer stable releases:

```bash
ai update
```

---

## 🧩 Component Ecosystem

AIRegistry currently contains the following reusable components:

| Component | Latest | Category | Typical role |
|---|---:|---|---|
| `agent` | `0.1.0` | agent | Tool-calling agent loop |
| `chat` | `0.1.0` | template | Minimal chat starter |
| `citation-builder` | `1.0.0` | tool | Citation and bibliography formatting |
| `citations` | `0.1.0` | tool | Numbered source citations |
| `context-builder` | `1.0.0` | retrieval | Structured, size-limited context |
| `conversation-memory` | `1.0.0` | memory | In-memory conversation store |
| `json-validator` | `1.0.0` | validation | JSON validation and schema checks |
| `keyword-rag` | `1.0.0` | retrieval | Lightweight keyword retrieval |
| `memory` | `0.1.0` | tool | JSON-file memory store |
| `prompt-builder` | `1.0.0` | prompt | Reusable prompt construction |
| `rag` | `0.1.0` | workflow | Small retrieval workflow |
| `text-chunker` | `1.0.0` | text | Configurable text chunking |
| `tool-router` | `1.0.0` | tool | Safe tool registration and routing |

Browse the complete live catalog at:

**https://airegistry.instantregret96.workers.dev**

---

## 🔍 The Registry Model

AIRegistry v2.1 uses an immutable, versioned release model.

```text
Component
│
├── metadata
│
└── releases
    │
    ├── 0.1.0
    │   ├── component.json
    │   ├── README.md
    │   └── src/
    │
    ├── 0.2.0
    │   ├── component.json
    │   ├── README.md
    │   └── src/
    │
    └── 1.0.0
        ├── component.json
        ├── README.md
        └── src/
```

Each release contains:

- exact version metadata;
- dependency references;
- release notes;
- source file list;
- SHA-256 checksums;
- immutable source path.

That makes `name@version` a first-class developer primitive.

---

## 🛠️ Example Workflow

Imagine you are building a retrieval application.

### 1. Find a retriever

```bash
ai search keyword-rag
```

### 2. Inspect the release

```bash
ai info keyword-rag@1.0.0
```

### 3. Add it

```bash
ai add keyword-rag@1.0.0
```

### 4. Add supporting context construction

```bash
ai add context-builder@1.0.0
```

### 5. Build your application

```text
documents
    ↓
keyword-rag
    ↓
context-builder
    ↓
prompt-builder
    ↓
your AI application
```

AIRegistry provides the components; your application owns the final composition.

---

## 🤝 Publish a Component

AIRegistry is designed for community contribution.

Authenticated publishers can submit:

- a new component;
- a new release of an existing component;
- exact dependency references;
- release notes and file metadata.

The publishing workflow prepares a **branch, commit, and pull request** rather than writing directly to `main`.

```text
Developer
   │
   ▼
AIRegistry Publisher
   │
   ├── validate manifest
   ├── validate version
   ├── validate dependencies
   ├── prepare release tree
   └── create Pull Request
            │
            ▼
       CI + Review
            │
            ▼
         main
```

Start here:

**https://airegistry.instantregret96.workers.dev**

---

## 🔐 Security & Integrity

AIRegistry is built around a few simple trust boundaries:

```text
untrusted submission
        ↓
manifest validation
        ↓
version validation
        ↓
dependency validation
        ↓
path / file safety checks
        ↓
SHA-256 generation
        ↓
pull request review
        ↓
published release
```

The CLI also protects installs against unsafe paths and verifies release files
against recorded SHA-256 metadata.

Read the project's security guidance in [`SECURITY.md`](./SECURITY.md).

---

## 🧱 Architecture

```text
┌───────────────────────┐
│       Developer       │
└───────────┬───────────┘
            │
     search / info / add
            │
            ▼
┌───────────────────────┐
│   AIRegistry CLI      │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│     Registry v2       │
│ versions + checksums  │
└───────────┬───────────┘
            │
            ├───────────────┐
            ▼               ▼
      Static Web UI     Publisher API
                            │
                            ▼
                     GitHub Pull Request
```

Production deployment uses Cloudflare Workers + Static Assets.

More detail: [`ARCHITECTURE.md`](./ARCHITECTURE.md)

---

## 🧪 Validation

The project release process validates:

```text
registry freshness
      +
automated test suite
      +
Python syntax
      +
Worker / website syntax
      +
Git whitespace checks
      +
deployment dry-run
```

For a local development checkout:

```bash
python .\scripts\build_registry.py --check
python -m unittest discover -s tests -v
git diff --check
```

---

## 📦 Release

### v2.1.0

AIRegistry v2.1 introduced the immutable versioned release model:

- registry schema v2;
- exact component references;
- exact dependency references;
- SHA-256 file integrity metadata;
- version-aware lockfiles;
- `ai update`;
- community publishing for new components and new releases;
- version history and release selection in the web UI;
- migration tooling for the V2.0 → V2.1 layout.

**Released:** `v2.1.0`

**Commit:** `116af78`

**Tag:** `v2.1.0`

---

## 📚 Documentation

| Document | Purpose |
|---|---|
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | System design and production architecture |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md) | Contribution and publishing workflow |
| [`SECURITY.md`](./SECURITY.md) | Security model and reporting |
| [`CHANGELOG.md`](./CHANGELOG.md) | Release history |
| [`BUILD_NOTES.md`](./BUILD_NOTES.md) | Build and release notes |
| [`docs/CLOUD_AUTH.md`](./docs/CLOUD_AUTH.md) | GitHub / Cloudflare authentication details |

---

## 🌌 Vision

AIRegistry is intentionally modular.

The long-term direction is to make reusable AI building blocks easier to:

**discover → understand → verify → install → compose → publish**

The registry should stay readable and developer-owned: small components, explicit
versions, transparent source, and a contribution path that fits normal GitHub
development.

---

<div align="center">

<img src="./readme_assets/Footer.png" alt="AIRegistry futuristic footer" width="100%"/>

<br/>

### AIRegistry

**Discover. Build. Share.**

<sub>Open-source infrastructure for reusable AI components.</sub>

</div>
