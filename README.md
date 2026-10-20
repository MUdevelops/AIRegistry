<div align="center">

<img src="https://raw.githubusercontent.com/MUdevelops/AIRegistry/main/readme_assets/Animated-Header.gif" alt="AIRegistry animated header" width="100%"/>

<br/>

<p>
  <a href="https://github.com/MUdevelops/AIRegistry/actions/workflows/ci.yml"><img src="https://github.com/MUdevelops/AIRegistry/actions/workflows/ci.yml/badge.svg" alt="CI"/></a>
  <a href="https://github.com/MUdevelops/AIRegistry/releases"><img src="https://img.shields.io/badge/Release-v2.3.1-00d9ff?style=flat-square" alt="v2.3.0"/></a>
  <a href="https://github.com/MUdevelops/AIRegistry/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-8b5cf6?style=flat-square" alt="MIT License"/></a>
  <a href="https://pypi.org/project/airegistry-cli/"><img src="https://img.shields.io/pypi/v/airegistry-cli?style=flat-square&color=3776ab" alt="PyPI"/></a>
  <img src="https://img.shields.io/badge/Python-%3E%3D3.9-22c55e?style=flat-square&logo=python&logoColor=white" alt="Python 3.9+"/>
  <img src="https://img.shields.io/badge/components-11-111827?style=flat-square" alt="11 components"/>
</p>

### **Install AI capabilities, not libraries.**

<p>
  AIRegistry is an open-source registry and dependency-free CLI for reusable, versioned
  AI building blocks: retrieval, memory, agents, prompts, tools, citations and validation.
</p>

<p>
  <a href="https://airegistry.instantregret96.workers.dev">Live registry</a> ·
  <a href="https://github.com/MUdevelops/AIRegistry/issues">Issues</a> ·
  <a href="https://github.com/MUdevelops/AIRegistry/blob/main/CONTRIBUTING.md">Contributing</a> ·
  <a href="https://github.com/MUdevelops/AIRegistry/blob/main/CHANGELOG.md">Changelog</a>
</p>

</div>

## What is AIRegistry?

AI projects keep rebuilding the same small pieces: prompt builders, chunkers, retrievers, memory, validators, tool routers. AIRegistry packages them as **small, readable, versioned source components** that you copy into your own project and own.

```text
search -> inspect -> add -> build
```

> **Reuse the capability. Own the source. Pin the version.**

| | |
|---|---|
| **Versioned, immutable releases** | Every release lives at `registry/<name>/versions/<version>/` and is never edited afterwards. |
| **Exact references** | `ai add keyword-rag@1.1.0` installs precisely that release. |
| **Verified installs** | Every file has a SHA-256 checksum that the CLI checks before writing anything. |
| **Standard library only** | The CLI and every component run on plain Python 3.9+. |
| **Review-first publishing** | Community submissions become GitHub pull requests, never direct commits. |

## Quick start

Install the CLI from PyPI:

```bash
pip install airegistry-cli
```

Or from source: `git clone https://github.com/MUdevelops/AIRegistry.git`, then `python -m pip install .` inside the folder.

Then, in your own project:

```bash
ai search rag                       # find components
ai info keyword-rag                 # inspect: releases, files, dependencies
ai add keyword-rag --dry-run        # preview, writes nothing
ai add keyword-rag                  # install the latest release
ai add context-builder@1.1.0        # or pin an exact release
ai list                             # what is installed
ai update                           # move installed components to their latest release
ai remove keyword-rag
```

Components are copied to `ai_components/<name>/` (change it with `--dir`) and recorded in `.airegistry/lock.json`. Use one in your code:

```python
import sys
sys.path.insert(0, "ai_components/keyword-rag/src")

from keyword_rag import retrieve

print(retrieve(["Cats purr.", "Python is a language."], "python", top_k=1))
```

Without `pip`, run the CLI directly: `python ai.py search rag`. In a checkout, the CLI reads the local `registry.json`; otherwise it uses the public registry. Point it elsewhere with `ai config registry_url <path-or-https-url>`.

## Component catalog

| Component | Latest | Category | What it does |
|---|---:|---|---|
| [`agent`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/agent/versions/1.0.0/README.md) | `1.0.0` | agent | Deterministic tool-calling agent loop with a pluggable planner, step records and bounded execution. |
| [`citation-builder`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/citation-builder/versions/1.1.0/README.md) | `1.1.0` | tool | Format numbered source citations and bibliographies with duplicate merging and stable numbering. |
| [`context-builder`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/context-builder/versions/1.1.0/README.md) | `1.1.0` | retrieval | Combine retrieved passages into a numbered, size-limited context block for prompts. |
| [`conversation-memory`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/conversation-memory/versions/1.1.0/README.md) | `1.1.0` | memory | In-process conversation store with size limit, keyword search, character-budget windows and snapshots. |
| [`json-validator`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/json-validator/versions/1.1.0/README.md) | `1.1.0` | validation | Validate JSON text and return error position, type, keys and readable schema violations. |
| [`keyword-rag`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/keyword-rag/versions/1.1.0/README.md) | `1.1.0` | retrieval | Dependency-free keyword retrieval that ranks documents and returns relevant passages. |
| [`prompt-builder`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/prompt-builder/versions/1.1.0/README.md) | `1.1.0` | prompt | Build reusable prompts from system, instruction, context and input sections with safe placeholder filling. |
| [`query-rewriter`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/query-rewriter/versions/1.1.0/README.md) | `1.1.0` | retrieval | Deterministic query normalization, stopword removal and keyword variants for retrieval workflows. |
| [`retrieval-pipeline`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/retrieval-pipeline/versions/1.1.0/README.md) | `1.1.0` | workflow | Compose a retriever and a context builder into one validated workflow that returns bounded AI-ready context. |
| [`text-chunker`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/text-chunker/versions/1.1.0/README.md) | `1.1.0` | text | Split text into overlapping chunks by characters or words, with optional source offsets. |
| [`tool-router`](https://github.com/MUdevelops/AIRegistry/blob/main/registry/tool-router/versions/1.1.0/README.md) | `1.1.0` | tool | Register Python functions as named tools and execute calls safely, returning errors as data. |

Every component is stdlib-only, typed, documented and covered by tests. Dependencies between components are optional and exact; `ai add` shows them but never installs them automatically. Typical composition:

```text
query-rewriter --> keyword-rag --> context-builder --> prompt-builder
                        \______ retrieval-pipeline ______/
conversation-memory      tool-router --> agent        citation-builder
```

Browse the full catalog at the [live registry](https://airegistry.instantregret96.workers.dev).

## Registry model

```text
registry/
  keyword-rag/
    versions/
      1.0.0/   component.json  README.md  src/keyword_rag.py
      1.1.0/   component.json  README.md  src/keyword_rag.py
```

`python scripts/build_registry.py` validates every release and generates `registry.json` and `website/registry.json`; `--check` fails when they are stale. A release is never changed after it is published: fixes ship as a new version. See [ARCHITECTURE.md](ARCHITECTURE.md).

## Community publishing

```text
GitHub sign-in -> Submit Component -> Worker validation -> GitHub App -> branch + commit -> Pull Request -> CI + review -> merge
```

The publisher accepts new components and new releases of existing ones. Nothing is written to `main` directly. Read [CONTRIBUTING.md](CONTRIBUTING.md) for the format and rules.

## Security

Registry content and submissions are untrusted input. The CLI validates paths and checksums, rejects executable file types and never runs what it installs. See [SECURITY.md](SECURITY.md) for details and how to report a vulnerability.

## Development

```bash
python scripts/build_registry.py --check
python -W error -m unittest discover -s tests -v
python -m py_compile ai.py scripts/build_registry.py
node --check website/app.js
node --check cloudflare/worker.js
```

Deployment and operations: [docs/CLOUD_AUTH.md](docs/CLOUD_AUTH.md), [docs/MONITORING.md](docs/MONITORING.md).

## License

MIT. See [LICENSE](LICENSE).
