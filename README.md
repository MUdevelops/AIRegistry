<div align="center">

<img src="./readme_assets/Animated-Header.gif" alt="AIRegistry animated header" width="100%"/>

<br/>

<p>
  <a href="https://github.com/MUdevelops/AIRegistry/releases/tag/v2.1.0">
    <img src="https://img.shields.io/badge/Release-v2.1.0-00d9ff?style=for-the-badge&logo=github&logoColor=white" alt="v2.1.0"/>
  </a>
  <a href="https://github.com/MUdevelops/AIRegistry">
    <img src="https://img.shields.io/badge/Open%20Source-MIT-8b5cf6?style=for-the-badge" alt="Open Source"/>
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-%3E%3D3.9-22c55e?style=for-the-badge&logo=python&logoColor=white" alt="Python >=3.9"/>
  </a>
  <a href="https://airegistry.instantregret96.workers.dev">
    <img src="https://img.shields.io/badge/Live%20Registry-Online-06b6d4?style=for-the-badge" alt="Live Registry"/>
  </a>
</p>

<<<<<<< HEAD
### **Install AI capabilities, not libraries.**

<p>
  AIRegistry is an open-source registry and dependency-free CLI for reusable
  AI components, workflows, tools, agents, memory, retrieval, prompts, and templates.
</p>

<p>
=======
<p align="center">
  An open-source registry and dependency-free CLI for reusable AI components, agents, tools, retrieval helpers, memory utilities, and project building blocks.
</p>

<p align="center">
  <a href="https://airegistry.instantregret96.workers.dev">Live Registry</a>
  ·
>>>>>>> b36442e (Polish AIRegistry for public launch)
  <a href="https://github.com/MUdevelops/AIRegistry">GitHub</a>
  ·
  <a href="https://airegistry.instantregret96.workers.dev">Live Registry</a>
  ·
  <a href="https://github.com/MUdevelops/AIRegistry/issues">Issues</a>
  ·
  <a href="https://github.com/MUdevelops/AIRegistry/pulls">Pull Requests</a>
<<<<<<< HEAD
=======
</p>

<p align="center">
  <a href="https://github.com/MUdevelops/AIRegistry/actions/workflows/ci.yml"><img src="https://github.com/MUdevelops/AIRegistry/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/MUdevelops/AIRegistry/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-111827.svg" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/components-13-111827.svg" alt="13 components">
>>>>>>> b36442e (Polish AIRegistry for public launch)
</p>

</div>

<img src="./readme_assets/01-overview.gif" alt="Animated overview section" width="100%"/>

<<<<<<< HEAD
## ✦ What is AIRegistry?

AI development repeatedly needs the same small building blocks: retrieval, memory,
agents, citations, prompts, tools, validation, and text processing.

**AIRegistry packages those building blocks as discoverable, versioned, auditable source components.**

<div align="center">

```text
                 ┌─────────────────────┐
                 │     AIRegistry      │
                 │  versioned source   │
                 └─────────┬───────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
      Discover           Verify             Add
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                     Build & Compose
```


<sub><strong>The Central Hub</strong> — reusable AI capabilities connected through one versioned registry.</sub>

</div>

> **Reuse the capability. Own the source. Pin the version.**

<img src="./readme_assets/02-why.gif" alt="Animated Why AIRegistry section" width="100%"/>

## ⚡ Why AIRegistry?

| Capability | What it gives developers |
|---|---|
| 🧬 **Immutable releases** | Components live under explicit version paths. |
| 🎯 **Exact resolution** | `name@version` is a first-class reference. |
| 🔐 **Integrity checks** | Release files carry SHA-256 metadata. |
| 🧱 **Composable source** | Reuse small building blocks inside your own applications. |
| 🛠️ **Dependency-free CLI** | Standard-library-first developer workflow. |
| 🤝 **Community publishing** | Contributions flow through GitHub branches and PRs. |

```text
discover
   ↓
inspect
   ↓
verify
   ↓
add
   ↓
compose
   ↓
publish
```

<img src="./readme_assets/03-quickstart.gif" alt="Animated quick start section" width="100%"/>

## 🚀 Quick Start

### Install

From a local checkout:

```powershell
python -m pip install .
```

### Search

```bash
ai search rag
```

### Inspect

```bash
ai info rag
ai info rag@0.1.0
```

### Preview

```bash
ai add rag@0.1.0 --dry-run
```

### Install

```bash
ai add rag@0.1.0
```

### Inspect local state

```bash
ai list
```

### Update

```bash
ai update
```

<div align="center">

```text
┌──────────┐     ┌────────────┐     ┌─────────┐     ┌──────────────┐
│  search  │ ──▶ │   inspect  │ ──▶ │  verify │ ──▶ │  install     │
└──────────┘     └────────────┘     └─────────┘     └──────────────┘
```

</div>

<img src="./readme_assets/04-ecosystem.gif" alt="Animated component ecosystem section" width="100%"/>

## 🧩 Component Ecosystem

AIRegistry v2.1 includes 13 reusable components:

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
| `rag` | `0.1.0` | workflow | Small keyword retrieval workflow |
| `text-chunker` | `1.0.0` | text | Configurable text chunking |
| `tool-router` | `1.0.0` | tool | Safe tool registration and routing |

<div align="center">

`RAG` · `Agents` · `Memory` · `Tools` · `Prompts` · `Citations` · `Validation`

</div>

<img src="./readme_assets/05-registry.gif" alt="Animated registry model section" width="100%"/>

## 🔍 Registry Model

AIRegistry v2.1 uses an immutable, versioned release model:

```text
registry/
└── component/
    └── versions/
        ├── 0.1.0/
        │   ├── component.json
        │   ├── README.md
        │   └── src/
        │
        ├── 0.2.0/
        │   ├── component.json
        │   ├── README.md
        │   └── src/
        │
        └── 1.0.0/
            ├── component.json
            ├── README.md
            └── src/
```

Each release records:

- exact version metadata;
- dependency references;
- release notes;
- file list;
- SHA-256 checksums;
- immutable source path.

So:

```bash
ai add rag@0.1.0
```

is not merely "install the current RAG component"; it is an explicit release selection.

<img src="./readme_assets/06-publish.gif" alt="Animated community publishing section" width="100%"/>

## 🤝 Community Publishing

AIRegistry is built for developer participation.

Contributors can submit:

- new components;
- new releases;
- exact dependency references;
- release notes and metadata.

The publisher workflow prepares a branch, commit, and pull request instead of writing
directly to `main`.

```text
Developer
    │
    ▼
Publisher UI
    │
    ├── manifest validation
    ├── version validation
    ├── dependency validation
    ├── path / file checks
    └── release preparation
            │
            ▼
      GitHub Pull Request
            │
         CI + Review
            │
            ▼
           main
            │
            ▼
        registry release
```

Live publisher entry point:

**https://airegistry.instantregret96.workers.dev**

<img src="./readme_assets/07-security.gif" alt="Animated security section" width="100%"/>

## 🔐 Security & Integrity

AIRegistry treats published source as an explicit trust boundary.

```text
submission
    ↓
manifest validation
    ↓
version validation
    ↓
dependency validation
    ↓
path / file safety
    ↓
SHA-256 metadata
    ↓
PR review
    ↓
published release
```

The CLI also checks:

- unsafe/traversal paths;
- blocked executable extensions;
- release source paths;
- checksum consistency.

See [`SECURITY.md`](./SECURITY.md).

<img src="./readme_assets/08-release.gif" alt="Animated release section" width="100%"/>

## 📦 V2.1.0 Release

**AIRegistry v2.1.0** introduced the versioned-release foundation:

- Registry schema v2.
- Immutable version directories.
- Exact component references.
- Exact dependency references.
- SHA-256 file integrity metadata.
- Version-aware lockfiles.
- `ai update`.
- Community publishing for new components and releases.
- Version history and release selection in the web interface.
- V2.0 → V2.1 migration tooling.

**Release:** `v2.1.0`  
**Commit:** `116af78`  
**Tag:** `v2.1.0`

<a href="https://github.com/MUdevelops/AIRegistry/releases/tag/v2.1.0">
<img src="https://img.shields.io/badge/View%20Release-v2.1.0-00d9ff?style=for-the-badge&logo=github&logoColor=white" alt="View release"/>
</a>

<img src="./readme_assets/09-docs.gif" alt="Animated documentation section" width="100%"/>

## 📚 Documentation

| Document | Purpose |
|---|---|
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | System design and production architecture |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md) | Contribution and publishing workflow |
| [`SECURITY.md`](./SECURITY.md) | Security model and reporting |
| [`CHANGELOG.md`](./CHANGELOG.md) | Release history |
| [`BUILD_NOTES.md`](./BUILD_NOTES.md) | Build and release notes |
| [`docs/CLOUD_AUTH.md`](./docs/CLOUD_AUTH.md) | GitHub / Cloudflare authentication details |

<img src="./readme_assets/10-vision.gif" alt="Animated vision section" width="100%"/>

## 🌌 Vision

AIRegistry is intentionally modular:

**discover → understand → verify → install → compose → publish**

The direction is developer-owned AI infrastructure:

- small components;
- explicit releases;
- transparent source;
- reproducible installation;
- GitHub-native contribution.

<div align="center">

### **AIRegistry**

**Discover. Build. Share.**

<sub>Open-source infrastructure for reusable AI components.</sub>

<br/><br/>

<img src="./readme_assets/Footer.png" alt="AIRegistry futuristic transparent footer" width="100%"/>

</div>
=======
AIRegistry is a small, source-first catalog for reusable AI building blocks.

Instead of installing another large framework, you can discover a focused component, inspect its source, and add it directly to your project.

```text
search → inspect → add → build
```

The project has two parts:

- **CLI + registry:** dependency-free Python tooling for discovering, validating, installing, updating, and removing components.
- **Web catalog + publisher:** a static component catalog with GitHub authentication and a review-first submission workflow powered by a Cloudflare Worker.

The catalog currently contains **13 components** covering agents, chat starters, retrieval, memory, prompting, text processing, citations, validation, and tools.

## Why AIRegistry?

AIRegistry is designed around a few simple principles:

**Small.** Components should solve one clear problem.

**Readable.** Source should be understandable before it is installed.

**Auditable.** Registry metadata, file lists, and SHA-256 checksums make what is installed explicit.

**Offline-friendly.** The core CLI does not require an AI provider or a runtime service just to inspect and install registry content.

**Review-first.** Community submissions go through GitHub Pull Requests instead of writing directly to `main`.

## Quick start

Clone the repository and use the CLI directly with Python 3.11+:

```bash
git clone https://github.com/MUdevelops/AIRegistry.git
cd AIRegistry
python ai.py search rag
python ai.py info rag
python ai.py add rag --dry-run
python ai.py add rag
python ai.py list
```

Remove an installed component with:

```bash
python ai.py remove rag
```

The CLI keeps installed components separate from the registry source tree.

## Current component catalog

| Component | Purpose |
|---|---|
| `agent` | Small agent/planning starter |
| `chat` | Minimal chat-oriented template |
| `citation-builder` | Numbered citations and bibliographies |
| `citations` | Lightweight citation helpers |
| `context-builder` | Build structured prompt context from retrieved passages |
| `conversation-memory` | Small local conversation store |
| `json-validator` | Validate JSON and report useful diagnostics |
| `keyword-rag` | Lightweight keyword retrieval |
| `memory` | Simple local persistent memory |
| `prompt-builder` | Compose reusable prompt sections |
| `rag` | Minimal retrieval workflow starter |
| `text-chunker` | Character/word chunking with overlap |
| `tool-router` | Register and safely route named tools |

Browse the complete catalog at the [live registry](https://airegistry.instantregret96.workers.dev).

## Registry format

Each component lives under `registry/<name>/` and contains:

```text
registry/<name>/
├── component.json
├── README.md
└── src/
    └── ...
```

`component.json` provides the machine-readable metadata used to build the registry index. The generated indexes are:

```text
registry.json
website/registry.json
```

Run the index builder with:

```bash
python scripts/build_registry.py
python scripts/build_registry.py --check
```

`--check` verifies that committed registry indexes match the component directories.

## Dependencies

Components may declare other AIRegistry components as dependencies. Dependencies are metadata and are **not automatically installed** by `ai add`.

For example:

```text
context-builder
└── keyword-rag
```

Optional dependencies are marked explicitly in the component manifest and displayed by the CLI/catalog.

## Community publishing

The website includes a review-first publisher:

```text
GitHub sign-in
      ↓
Submit Component
      ↓
AIRegistry Worker validation
      ↓
GitHub App
      ↓
branch + commit
      ↓
Pull Request
      ↓
CI + maintainer review
      ↓
merge
```

No submitted component is written directly to `main` by the web form.

Read [CONTRIBUTING.md](CONTRIBUTING.md) for the component format, validation rules, testing workflow, and Pull Request process.

## Architecture

```text
                    GitHub Repository
                           │
                 registry/ + tests/ + CLI
                           │
                    build_registry.py
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
        registry.json            website/registry.json
              │                         │
              ▼                         ▼
           CLI                        Web Catalog
                                        │
                              Cloudflare Worker
                                ┌───────┴───────┐
                                ▼               ▼
                              OAuth         Publisher
                                                │
                                            GitHub PR
```

The public catalog is static. The Worker is used for authentication and the GitHub-backed publishing API.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the repository-level design.

## Development

Run the complete local validation suite:

```bash
python scripts/build_registry.py --check
python -m unittest discover -s tests -v
python -m py_compile ai.py scripts/build_registry.py
node --check website/app.js
node --check cloudflare/worker.js
```

For the website/Worker deployment configuration, see [docs/CLOUD_AUTH.md](docs/CLOUD_AUTH.md).

For production monitoring and operational checks, see [docs/MONITORING.md](docs/MONITORING.md).

## Security

AIRegistry treats registry content and community submissions as untrusted input. The CLI validates paths and checksums before installation, while the publisher validates component metadata and file layout before opening a Pull Request.

Please read [SECURITY.md](SECURITY.md) before reporting a vulnerability or changing the publishing/authentication code.

## License

MIT. See [LICENSE](LICENSE).

## Project status

AIRegistry is an actively developed open-source project. The current V2 catalog focuses on a small number of composable building blocks rather than a large dependency-heavy framework.

The preferred way to improve the project is through focused, reviewable Pull Requests with tests and documentation updates included in the same change.
>>>>>>> b36442e (Polish AIRegistry for public launch)
