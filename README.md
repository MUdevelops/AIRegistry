<div align="center">
  <a href="https://github.com/MUdevelops/AIRegistry">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=30&duration=2800&pause=900&color=00D9FF&center=true&vCenter=true&width=800&height=60&lines=Install+AI+capabilities%2C+not+libraries.;Search.+Inspect.+Add.+Build.;Reuse+the+capability.+Own+the+source." alt="AIRegistry — Install AI capabilities, not libraries" />
  </a>
  <br />
  <p><strong>A dependency-free CLI and versioned registry for reusable AI building blocks.</strong></p>
  <p>
    <a href="https://github.com/MUdevelops/AIRegistry/actions/workflows/ci.yml"><img src="https://github.com/MUdevelops/AIRegistry/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI status" /></a>
    <a href="https://pypi.org/project/airegistry-cli/"><img src="https://img.shields.io/pypi/v/airegistry-cli?style=flat-square&label=PyPI&color=3776AB" alt="PyPI version" /></a>
    <a href="https://github.com/MUdevelops/AIRegistry/blob/main/LICENSE"><img src="https://img.shields.io/github/license/MUdevelops/AIRegistry?style=flat-square&color=8B5CF6" alt="MIT license" /></a>
    <img src="https://img.shields.io/badge/Python-3.9%2B-22C55E?style=flat-square&logo=python&logoColor=white" alt="Python 3.9+" />
    <img src="https://img.shields.io/badge/components-11-111827?style=flat-square" alt="11 components" />
    <a href="https://github.com/MUdevelops/AIRegistry/stargazers"><img src="https://img.shields.io/github/stars/MUdevelops/AIRegistry?style=flat-square&color=F59E0B" alt="GitHub stars" /></a>
  </p>
  <p>
    <a href="https://airegistry.instantregret96.workers.dev"><strong>Live Registry</strong></a> ·
    <a href="#quick-start">Quick Start</a> ·
    <a href="#component-catalog">Components</a> ·
    <a href="https://github.com/MUdevelops/AIRegistry/issues">Issues</a> ·
    <a href="https://github.com/MUdevelops/AIRegistry/blob/main/CONTRIBUTING.md">Contribute</a>
  </p>
</div>

---

## ✨ What is AIRegistry?

AI projects often rebuild the same small pieces: retrievers, text chunkers, prompt builders, conversation memory, validators, citations, tool routers, and agent loops.

**AIRegistry packages these capabilities as small, readable, versioned source components** that you can inspect, add to your project, and own. Components are copied into your codebase instead of being hidden behind a runtime dependency or remote service.

```text
search  →  inspect  →  add  →  build
```

> **Reuse the capability. Own the source. Pin the version.**

## 🚀 Why AIRegistry?

| Capability | How it helps |
|---|---|
| 🧩 **Small, reusable components** | Add a focused building block instead of adopting an entire framework. |
| 📌 **Immutable, versioned releases** | Each published version lives under `registry/<name>/versions/<version>/` and is not edited in place. |
| 🎯 **Exact version pinning** | Install a specific release, such as `keyword-rag@1.1.0`, for repeatable builds. |
| 🔐 **Checksum-verified installs** | The CLI verifies SHA-256 checksums before writing component files. |
| 🐍 **Python standard library** | The CLI and catalog components are designed to run on Python 3.9+ without third-party runtime dependencies. |
| 👀 **Review-first publishing** | Community submissions are proposed through GitHub pull requests rather than committed directly to `main`. |
| 🧰 **Source ownership** | Installed code lives in your project, so you can read, test, adapt, and maintain it yourself. |

## ⚡ Quick start

### 1. Install the CLI

```bash
python -m pip install airegistry-cli
```

### 2. Search and inspect components

```bash
ai search rag
ai info keyword-rag
```

### 3. Preview an install, then add it

```bash
ai add keyword-rag --dry-run
ai add keyword-rag
```

Pin an exact version when reproducibility matters:

```bash
ai add context-builder@1.1.0
```

### 4. Manage your installed components

```bash
ai list
ai update
ai remove keyword-rag
```

### Install from source

```bash
git clone https://github.com/MUdevelops/AIRegistry.git
cd AIRegistry
python -m pip install .
```

> **No `pip` available?** From a repository checkout, you can invoke the CLI directly with `python ai.py search rag`.

## 🧪 Use a component in your Python project

By default, components are copied to `ai_components/<name>/`. Change that destination with `--dir`. Install records and integrity metadata are stored in `.airegistry/lock.json`.

For example, after adding `keyword-rag`:

```python
import sys

sys.path.insert(0, "ai_components/keyword-rag/src")

from keyword_rag import retrieve

matches = retrieve(
    ["Cats purr.", "Python is a programming language."],
    "python",
    top_k=1,
)

print(matches)
```

AIRegistry components provide building blocks, not a hosted AI model. For semantic search, model inference, or other capabilities outside a component's scope, connect the appropriate implementation in your own application.

## 🗂️ Component catalog

The registry currently documents **11 components** across retrieval, memory, agents, prompts, text processing, tools, validation, and workflow composition.

| Component | Version | Category | Purpose |
|---|---:|---|---|
| [`agent`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/agent/versions/1.0.0/README.md) | `1.0.0` | Agent | A bounded tool-calling loop with a pluggable planner and step records. |
| [`citation-builder`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/citation-builder/versions/1.1.0/README.md) | `1.1.0` | Tool | Formats numbered citations and bibliographies, merges duplicates, and preserves stable numbering. |
| [`context-builder`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/context-builder/versions/1.1.0/README.md) | `1.1.0` | Retrieval | Combines retrieved passages into a numbered, size-limited context block. |
| [`conversation-memory`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/conversation-memory/versions/1.1.0/README.md) | `1.1.0` | Memory | Stores conversation history with size limits, keyword search, budgeted windows, and snapshots. |
| [`json-validator`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/json-validator/versions/1.1.0/README.md) | `1.1.0` | Validation | Validates JSON text and reports parsing details and readable schema violations. |
| [`keyword-rag`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/keyword-rag/versions/1.1.0/README.md) | `1.1.0` | Retrieval | Ranks documents with dependency-free keyword retrieval and returns relevant passages. |
| [`prompt-builder`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/prompt-builder/versions/1.1.0/README.md) | `1.1.0` | Prompt | Combines system instructions, context, and input with safe placeholder filling. |
| [`query-rewriter`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/query-rewriter/versions/1.1.0/README.md) | `1.1.0` | Retrieval | Normalizes queries, removes stopwords, and produces keyword variants. |
| [`retrieval-pipeline`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/retrieval-pipeline/versions/1.1.0/README.md) | `1.1.0` | Workflow | Composes a retriever and context builder into a validated, bounded workflow. |
| [`text-chunker`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/text-chunker/versions/1.1.0/README.md) | `1.1.0` | Text | Splits text into overlapping character- or word-based chunks, with optional source offsets. |
| [`tool-router`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/tool-router/versions/1.1.0/README.md) | `1.1.0` | Tool | Registers Python functions as named tools and returns execution results or errors as data. |

Every component is documented and typed, and the project includes tests. Component dependencies are optional and explicit: `ai add` shows them but does not install them automatically.

Browse the full catalog in the **[Live Registry](https://airegistry.instantregret96.workers.dev)**.

## 🔗 Compose components into a workflow

Combine small pieces into a larger pipeline while keeping each part independently inspectable:

```text
query-rewriter ──▶ keyword-rag ──▶ context-builder ──▶ prompt-builder
                       │                  ▲
                       └── retrieval-pipeline ──────┘

conversation-memory       tool-router ──▶ agent       citation-builder
```

This is a conceptual composition map; each component can also be installed and used independently.

## 📦 How the registry is structured

Each component has a versioned directory containing its manifest, documentation, and source code:

```text
registry/
└── keyword-rag/
    └── versions/
        ├── 1.0.0/
        │   ├── component.json
        │   ├── README.md
        │   └── src/keyword_rag.py
        └── 1.1.0/
            ├── component.json
            ├── README.md
            └── src/keyword_rag.py
```

Run the registry builder to validate published components and regenerate the registry indexes:

```bash
python scripts/build_registry.py
```

Use `--check` in CI to fail when generated files are stale:

```bash
python scripts/build_registry.py --check
```

Published releases are immutable. Bug fixes and improvements should be released as a new version. See [`ARCHITECTURE.md`](https://github.com/MUdevelops/AIRegistry/blob/main/ARCHITECTURE.md) for the design details.

## 🤝 Community publishing

AIRegistry uses a review-first submission path:

```text
GitHub sign-in
      ↓
Submit component or release
      ↓
Worker validation
      ↓
Branch and pull request
      ↓
CI checks + maintainer review
      ↓
Merge
```

Submissions can introduce a new component or publish another version of an existing one. The publishing flow is designed to avoid direct writes to `main`.

Read [`CONTRIBUTING.md`](https://github.com/MUdevelops/AIRegistry/blob/main/CONTRIBUTING.md) for contribution rules and the component format. Questions and bug reports belong in [GitHub Issues](https://github.com/MUdevelops/AIRegistry/issues).

## 🛡️ Security model

Registry entries and community submissions must be treated as **untrusted input**. The CLI is designed to validate paths and checksums, reject executable file types, and avoid running installed component code.

Before using a component in a sensitive environment, review its source and permissions as you would any code dependency. Report suspected vulnerabilities according to [`SECURITY.md`](https://github.com/MUdevelops/AIRegistry/blob/main/SECURITY.md).

## 🧑‍💻 Development and checks

Run the project checks from the repository root:

```bash
python scripts/build_registry.py --check
python -W error -m unittest discover -s tests -v
python -m py_compile ai.py scripts/build_registry.py
node --check website/app.js
node --check cloudflare/worker.js
```

Useful operational documentation:

- [Cloud authentication and deployment](https://github.com/MUdevelops/AIRegistry/blob/main/docs/CLOUD_AUTH.md)
- [Monitoring](https://github.com/MUdevelops/AIRegistry/blob/main/docs/MONITORING.md)
- [Architecture](https://github.com/MUdevelops/AIRegistry/blob/main/ARCHITECTURE.md)
- [Changelog](https://github.com/MUdevelops/AIRegistry/blob/main/CHANGELOG.md)

## 📄 License

AIRegistry is released under the **MIT License**. See [`LICENSE`](https://github.com/MUdevelops/AIRegistry/blob/main/LICENSE) for the complete text.

---

<div align="center">
  <p><strong>Build AI applications from small, understandable building blocks.</strong></p>
  <p>
    <a href="https://airegistry.instantregret96.workers.dev">Explore the registry</a> ·
    <a href="https://github.com/MUdevelops/AIRegistry/issues">Report an issue</a> ·
    <a href="https://github.com/MUdevelops/AIRegistry/blob/main/CONTRIBUTING.md">Contribute</a>
  </p>
  <sub>Made for developers who want reusable AI capabilities without giving up source ownership.</sub>
</div>
