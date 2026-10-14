<div align="center">

<img src="./readme_assets/Animated-Header.gif" alt="AIRegistry — futuristic animated header" width="100%"/>

<br/>

<h1>AIRegistry <sup>v2.1.0</sup></h1>

### Install AI capabilities, not libraries.

<p>
  <strong>An open-source registry and dependency-free Python CLI for reusable, versioned AI components.</strong>
</p>

<p>
  <a href="https://airegistry.instantregret96.workers.dev/"><img src="https://img.shields.io/badge/Explore-Live%20Registry-00D9FF?style=for-the-badge&logo=cloudflare&logoColor=white" alt="Explore live registry"/></a>
  <a href="https://youtu.be/WVhWfGo2Bi4"><img src="https://img.shields.io/badge/▶_Watch-Product%20Demo-FF0033?style=for-the-badge&logo=youtube&logoColor=white" alt="Watch AIRegistry demo"/></a>
  <a href="https://github.com/MUdevelops/AIRegistry"><img src="https://img.shields.io/badge/GitHub-Open%20Source-8B5CF6?style=for-the-badge&logo=github&logoColor=white" alt="GitHub repository"/></a>
  <a href="https://github.com/MUdevelops/AIRegistry/releases/tag/v2.1.0"><img src="https://img.shields.io/badge/Release-v2.1.0-2563EB?style=for-the-badge" alt="v2.1.0 release"/></a>
</p>

<p>
  <a href="https://github.com/MUdevelops/AIRegistry/actions/workflows/ci.yml"><img src="https://github.com/MUdevelops/AIRegistry/actions/workflows/ci.yml/badge.svg" alt="CI status"/></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.9+"/>
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=flat-square" alt="MIT License"/>
  <img src="https://img.shields.io/badge/Components-13-06B6D4?style=flat-square" alt="13 components"/>
  <img src="https://img.shields.io/badge/Release%20model-Versioned-8B5CF6?style=flat-square" alt="Versioned release model"/>
</p>

<p>
  <a href="https://airegistry.instantregret96.workers.dev/">🌐 Website</a> ·
  <a href="https://youtu.be/WVhWfGo2Bi4">▶️ Watch the demo</a> ·
  <a href="https://github.com/MUdevelops/AIRegistry">⭐ Source code</a> ·
  <a href="https://github.com/MUdevelops/AIRegistry/issues">🐛 Issues</a> ·
  <a href="https://github.com/MUdevelops/AIRegistry/pulls">🤝 Pull requests</a>
</p>

</div>

---

<div align="center">

## ▶️ See AIRegistry in action

<a href="https://youtu.be/WVhWfGo2Bi4">
  <img src="https://img.youtube.com/vi/WVhWfGo2Bi4/maxresdefault.jpg" alt="Watch the AIRegistry v2.1.0 demo on YouTube" width="88%"/>
</a>

**Discover → Inspect → Verify → Install → Compose**

[**Watch the full demo on YouTube ↗**](https://youtu.be/WVhWfGo2Bi4) · [**Open the live registry ↗**](https://airegistry.instantregret96.workers.dev/)

</div>

<img src="./readme_assets/01-overview.gif" alt="Animated AIRegistry overview" width="100%"/>

## ✨ What is AIRegistry?

AI development repeatedly needs the same building blocks: retrieval, memory, agents, citations, prompts, tools, validation, and text processing.

**AIRegistry packages these capabilities as discoverable, versioned source components** that developers can inspect and add to their own projects.

<div align="center">

<img src="./readme_assets/Central%20Hub.png" alt="AIRegistry central hub connecting reusable AI components" width="82%"/>

<br/>

<table>
<tr>
<td align="center">🔎<br/><strong>Discover</strong></td>
<td align="center">🧾<br/><strong>Inspect</strong></td>
<td align="center">🛡️<br/><strong>Verify</strong></td>
<td align="center">📦<br/><strong>Install</strong></td>
<td align="center">🧩<br/><strong>Compose</strong></td>
<td align="center">🌍<br/><strong>Publish</strong></td>
</tr>
</table>

> **Reuse the capability. Own the source. Pin the version.**

</div>

<img src="./readme_assets/02-why.gif" alt="Animated reasons to use AIRegistry" width="100%"/>

## ⚡ Why AIRegistry?

<table>
<tr>
<td width="50%" valign="top">

### 🧬 Immutable releases
Each component release lives in its own versioned directory, preserving a clear source snapshot.

### 🎯 Exact version references
Use `component@version` to request a specific release instead of relying on an ambiguous latest version.

### 🔐 Integrity metadata
Release manifests include SHA-256 checksums so file integrity can be verified.

</td>
<td width="50%" valign="top">

### 🧱 Composable source
Use focused building blocks in your own applications and workflows.

### 🛠️ Lightweight CLI
A standard-library-first Python CLI keeps the core workflow dependency-light.

### 🤝 Review-first publishing
Community submissions go through a GitHub branch and Pull Request workflow before merging.

</td>
</tr>
</table>

```text
      DISCOVER
         │
         ▼
       INSPECT
         │
         ▼
        VERIFY
         │
         ▼
        INSTALL
         │
         ▼
       COMPOSE
         │
         ▼
        SHARE
```

<img src="./readme_assets/03-quickstart.gif" alt="Animated AIRegistry quick start" width="100%"/>

## 🚀 Quick Start

### 1. Get the project

```powershell
git clone https://github.com/MUdevelops/AIRegistry.git
cd AIRegistry
```

### 2. Run the CLI

Use Python directly from the repository:

```powershell
python ai.py search rag
python ai.py info rag
python ai.py info rag@0.1.0
```

### 3. Preview an installation

```powershell
python ai.py add rag@0.1.0 --dry-run
```

### 4. Install a specific release

```powershell
python ai.py add rag@0.1.0
```

### 5. Inspect and manage installed components

```powershell
python ai.py list
python ai.py update
python ai.py remove rag
```

> **Note:** If you install the CLI as a package, use `ai ...` commands. From a repository checkout, `python ai.py ...` works without requiring the `ai` executable to be on your PATH. Component dependencies are metadata and are not automatically installed by `ai add`.

<div align="center">

| Command | Purpose |
|:---|:---|
| `ai search <query>` | Search the component catalog |
| `ai info <name>` | Inspect component details |
| `ai info <name>@<version>` | Inspect a specific release |
| `ai add <name>@<version> --dry-run` | Preview an installation |
| `ai add <name>@<version>` | Install an exact release |
| `ai list` | List installed components |
| `ai update` | Update installed components where a newer release is available |
| `ai remove <name>` | Remove an installed component |

</div>

<img src="./readme_assets/04-ecosystem.gif" alt="Animated AIRegistry component ecosystem" width="100%"/>

## 🧩 Component Ecosystem

AIRegistry v2.1.0 includes **13 reusable components**.

| Component | Latest version | Category | What it does |
|---|---:|---|---|
| `agent` | `0.1.0` | Agent | Tool-calling agent loop |
| `chat` | `0.1.0` | Template | Minimal chat starter |
| `citation-builder` | `1.0.0` | Tool | Citation and bibliography formatting |
| `citations` | `0.1.0` | Tool | Numbered source citations |
| `context-builder` | `1.0.0` | Retrieval | Structured, size-limited context |
| `conversation-memory` | `1.0.0` | Memory | In-memory conversation store |
| `json-validator` | `1.0.0` | Validation | JSON validation and schema checks |
| `keyword-rag` | `1.0.0` | Retrieval | Lightweight keyword retrieval |
| `memory` | `0.1.0` | Tool | JSON-file memory store |
| `prompt-builder` | `1.0.0` | Prompt | Reusable prompt construction |
| `rag` | `0.1.0` | Workflow | Small keyword retrieval workflow |
| `text-chunker` | `1.0.0` | Text | Configurable text chunking |
| `tool-router` | `1.0.0` | Tool | Safe tool registration and routing |

<div align="center">

`RAG` · `Agents` · `Memory` · `Tools` · `Prompts` · `Citations` · `Validation`

[**Explore all components in the live registry →**](https://airegistry.instantregret96.workers.dev/)

</div>

<img src="./readme_assets/05-registry.gif" alt="Animated versioned registry model" width="100%"/>

## 🗂️ Versioned Registry Model

AIRegistry v2.1 uses an immutable, versioned release layout:

```text
registry/
└── rag/
    └── versions/
        ├── 0.1.0/
        │   ├── component.json
        │   ├── README.md
        │   └── src/
        └── ...
```

Each release records its:

- Exact version and component metadata
- Dependency references
- Release notes
- File list
- SHA-256 checksums
- Version-specific source path

For example:

```bash
ai info rag@0.1.0
ai add rag@0.1.0
```

An exact reference makes the requested release explicit and easier to audit.

<img src="./readme_assets/06-publish.gif" alt="Animated community publishing workflow" width="100%"/>

## 🤝 Community Publishing

AIRegistry is designed for developer participation. Contributors can submit new components, publish new versions, declare exact dependency references, and include release notes.

<div align="center">

```text
Developer
   │
   ▼
Publisher website
   │
   ▼
Manifest + version validation
   │
   ▼
GitHub branch + commit
   │
   ▼
Pull Request
   │
   ▼
CI checks + maintainer review
   │
   ▼
Merge and registry release
```

</div>

The web publisher prepares a Pull Request rather than writing community submissions directly to `main`.

- 🌐 [Open the live registry and publisher](https://airegistry.instantregret96.workers.dev/)
- 📘 [Read contribution guidelines](./CONTRIBUTING.md)
- 🔀 [Browse open Pull Requests](https://github.com/MUdevelops/AIRegistry/pulls)

<img src="./readme_assets/07-security.gif" alt="Animated security and integrity section" width="100%"/>

## 🔐 Security & Integrity

Registry content and community submissions should be treated as untrusted input. AIRegistry uses validation and review steps to reduce risk.

```text
Submission
   ↓
Manifest validation
   ↓
Version + dependency validation
   ↓
Path and file safety checks
   ↓
SHA-256 integrity metadata
   ↓
Pull Request review
   ↓
Published release
```

The CLI checks path safety, release source paths, blocked executable extensions, and checksum consistency. Review the project's security guidance before changing authentication or publishing behavior.

- [Security policy](./SECURITY.md)
- [Report a vulnerability](https://github.com/MUdevelops/AIRegistry/security/advisories/new)
- [Report a bug or request a feature](https://github.com/MUdevelops/AIRegistry/issues)

<img src="./readme_assets/08-release.gif" alt="Animated AIRegistry v2.1.0 release section" width="100%"/>

## 📦 What's New in v2.1.0?

AIRegistry v2.1.0 introduces the versioned-release foundation:

- 🗂️ Registry schema v2 and immutable version directories
- 🎯 Exact component and dependency references
- 🔐 SHA-256 file integrity metadata
- 🧾 Version-aware lockfiles
- 🔄 `ai update`
- 🤝 Community publishing for new components and releases
- 🕘 Version history and release selection in the web interface
- 🧰 V2.0 → V2.1 migration tooling

<div align="center">

<a href="https://github.com/MUdevelops/AIRegistry/releases/tag/v2.1.0"><img src="https://img.shields.io/badge/Read%20Release%20Notes-v2.1.0-00D9FF?style=for-the-badge&logo=github&logoColor=white" alt="Read v2.1.0 release notes"/></a>

</div>

<img src="./readme_assets/09-docs.gif" alt="Animated documentation section" width="100%"/>

## 📚 Documentation

| Document | What you'll find |
|---|---|
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | System design and production architecture |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md) | Component format, validation, and contribution workflow |
| [`SECURITY.md`](./SECURITY.md) | Security model and reporting guidance |
| [`CHANGELOG.md`](./CHANGELOG.md) | Release history |
| [`BUILD_NOTES.md`](./BUILD_NOTES.md) | Build and release notes |
| [`docs/CLOUD_AUTH.md`](./docs/CLOUD_AUTH.md) | GitHub / Cloudflare authentication details |

<img src="./readme_assets/10-vision.gif" alt="Animated AIRegistry vision section" width="100%"/>

## 🌌 Vision

AIRegistry aims to make reusable AI infrastructure easier to discover, understand, verify, install, and share.

<div align="center">

<table>
<tr>
<td align="center">🧩<br/><strong>Small components</strong></td>
<td align="center">🔎<br/><strong>Readable source</strong></td>
<td align="center">📌<br/><strong>Explicit releases</strong></td>
<td align="center">🔍<br/><strong>Auditable installs</strong></td>
<td align="center">🤝<br/><strong>Open collaboration</strong></td>
</tr>
</table>

### Discover. Build. Share.

**Open-source infrastructure for reusable AI components.**

<a href="https://airegistry.instantregret96.workers.dev/"><img src="https://img.shields.io/badge/OPEN-LIVE%20REGISTRY-00D9FF?style=for-the-badge&logo=cloudflare&logoColor=white" alt="Open live registry"/></a>
<a href="https://youtu.be/WVhWfGo2Bi4"><img src="https://img.shields.io/badge/WATCH-PRODUCT%20DEMO-FF0033?style=for-the-badge&logo=youtube&logoColor=white" alt="Watch product demo"/></a>
<a href="https://github.com/MUdevelops/AIRegistry"><img src="https://img.shields.io/badge/CONTRIBUTE-ON%20GITHUB-8B5CF6?style=for-the-badge&logo=github&logoColor=white" alt="Contribute on GitHub"/></a>

<br/>

<img src="./readme_assets/Footer.png" alt="AIRegistry futuristic transparent footer" width="100%"/>

</div>

---

<div align="center">

<sub>Built in the open by <a href="https://github.com/MUdevelops">MUdevelops</a> · Licensed under MIT · <a href="https://github.com/MUdevelops/AIRegistry/releases/tag/v2.1.0">v2.1.0</a></sub>

</div>
