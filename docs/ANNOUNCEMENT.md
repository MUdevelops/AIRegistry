# AIRegistry v2.2.0 — Public Launch Announcement

> **Reusable AI components. One lightweight registry. Built for developers.**

AIRegistry is an open-source registry for discovering, inspecting, installing, and contributing reusable AI components and developer tools.

With **v2.2.0**, the project enters a new public-launch stage with a polished web catalog, documented contribution workflow, production health monitoring, and a GitHub-based publishing pipeline.

## What is AIRegistry?

AI projects often rebuild the same small pieces: prompt builders, text chunkers, memory stores, retrieval helpers, validators, routers, citation utilities, and agent primitives.

AIRegistry provides a simple way to make those pieces:

**Discoverable → Inspectable → Installable → Reusable → Contributable**

The project is intentionally lightweight. Components remain small, readable, independently useful, and represented through registry metadata that can be consumed by both the CLI and web catalog.

## What's New in v2.2.0

### A polished developer experience

The AIRegistry website has been redesigned into a cleaner public catalog experience with:

- Component discovery and search
- Category-based browsing
- Component detail pages
- Install commands and metadata
- Dependency information
- GitHub integration
- Component submission flow
- Responsive presentation for modern browsers

### A real contribution workflow

AIRegistry supports community component submissions through GitHub.

The publishing flow is designed around review rather than direct repository modification:

```text
GitHub Login
     ↓
Submit Component
     ↓
Server-side validation
     ↓
GitHub App
     ↓
New branch
     ↓
Pull Request
     ↓
CI validation
     ↓
Maintainer review
     ↓
Merge
     ↓
Registry update
```

This keeps the repository reviewable while allowing contributors to submit components through the web interface.

### Registry-driven components

Each component is represented through structured metadata and source files.

A typical component contains:

```text
component/
├── README.md
├── component.json
└── src/
```

The registry index is generated from component manifests instead of being maintained as unrelated manual catalog entries.

### Lightweight building blocks

The catalog includes reusable building blocks covering areas such as:

- agents
- chat
- retrieval / RAG
- memory
- prompts
- context construction
- text chunking
- citations
- JSON validation
- tool routing
- query and retrieval utilities

The goal is not to replace large AI frameworks. The goal is to provide small building blocks that developers can inspect, combine, and adapt.

## CLI

AIRegistry also provides a lightweight Python CLI.

Search the registry:

```bash
python ai.py search rag
```

Inspect a component:

```bash
python ai.py info rag
```

Preview an installation:

```bash
python ai.py add rag --dry-run
```

Install a component:

```bash
python ai.py add rag
```

List installed components:

```bash
python ai.py list
```

The CLI is designed around offline-friendly registry access and integrity checks.

## Security and integrity

AIRegistry treats component content as untrusted input.

The project includes validation around:

- component names
- versions
- paths
- file sizes
- required files
- executable file extensions
- registry structure
- content checksums
- installation paths
- malformed metadata

The publishing service also uses authenticated GitHub integration rather than exposing repository credentials to the browser.

Security documentation:

[`SECURITY.md`](../SECURITY.md)

## Production service

The public AIRegistry catalog is deployed on Cloudflare Workers with Static Assets.

**Live catalog:**

https://airegistry.instantregret96.workers.dev

**Repository:**

https://github.com/MUdevelops/AIRegistry

**Health endpoint:**

https://airegistry.instantregret96.workers.dev/api/health

The health endpoint provides a lightweight production service check, while Cloudflare Worker observability can be used for operational monitoring.

## For contributors

AIRegistry is designed to accept useful, focused components rather than large framework-style packages.

A good component should generally be:

- focused on one clear task
- easy to understand
- independently reusable
- documented with practical usage
- represented with valid registry metadata
- covered by appropriate tests
- free of unnecessary dependencies

See:

[`CONTRIBUTING.md`](../CONTRIBUTING.md)

## For maintainers

The registry follows a review-first workflow.

Contributors submit components through GitHub pull requests, and automated validation should be treated as part of the publication process.

Before merging a component, maintainers should review:

- source code
- metadata
- dependency declarations
- README and examples
- tests
- file safety
- registry index changes

## Why AIRegistry?

The long-term vision is a developer ecosystem where useful AI building blocks are easier to discover and compose without requiring every project to adopt a large framework.

AIRegistry focuses on a simple principle:

> **Small components can become powerful systems when they are easy to discover and compose.**

## Project Status

AIRegistry v2.2.0 represents the project's public-launch phase.

The core registry, CLI, web catalog, authentication flow, GitHub publishing workflow, and production deployment are now connected into one system.

The project will continue evolving through incremental, reviewable releases while preserving the lightweight nature of its components.

## Get Started

Explore the catalog:

**https://airegistry.instantregret96.workers.dev**

Browse the source:

**https://github.com/MUdevelops/AIRegistry**

Install a component:

```bash
python ai.py search rag
python ai.py info rag
python ai.py add rag
```

Contribute a component:

**https://airegistry.instantregret96.workers.dev/#/submit**

## What's Next

The public launch is the beginning of the ecosystem, not the end of the project.

Future development can expand the registry around:

- richer dependency semantics
- additional reusable AI components
- stronger validation and automation
- improved component discovery
- version and release workflows
- ecosystem tooling
- deeper developer documentation

The direction remains the same: keep AIRegistry useful, transparent, lightweight, and easy for developers to build on.

---

### Thank You

AIRegistry is built around open-source collaboration.

Whether you are discovering a component, installing one into a project, reviewing a contribution, or publishing your own building block, every useful contribution helps make the ecosystem more reusable for the next developer.

**Welcome to AIRegistry.**

— **MUdevelops**
