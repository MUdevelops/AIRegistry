# AIRegistry 2.0 — Launch Announcement

## GitHub release / blog version

**AIRegistry 2.0 is here.**

AIRegistry is an open-source registry and dependency-free CLI for reusable AI building blocks.

Instead of pulling an entire framework into a project, AIRegistry lets you discover a focused component, inspect its source, and add it directly:

```text
search → inspect → add → build
```

The V2 catalog now contains **13 components** spanning:

- agents and chat starters
- retrieval and RAG helpers
- memory and conversation utilities
- prompt and context builders
- citation tooling
- text chunking
- JSON validation
- tool routing

The project also includes a web catalog and a review-first community publishing flow. Contributors can sign in with GitHub, submit a component, and have AIRegistry create a Pull Request for maintainer review.

### Why this project exists

AI applications repeatedly rebuild the same small pieces. AIRegistry focuses on making those pieces:

**small, readable, auditable, and reusable.**

There is no requirement to adopt a large framework just to reuse one useful capability.

### Try it

```bash
git clone https://github.com/MUdevelops/AIRegistry.git
cd AIRegistry
python ai.py search rag
python ai.py info rag
python ai.py add rag --dry-run
```

Browse the catalog:

https://airegistry.instantregret96.workers.dev

### Contribute

Component submissions are reviewed through GitHub Pull Requests. See [CONTRIBUTING.md](../CONTRIBUTING.md) for the component structure, local validation, and contribution workflow.

### Links

- Repository: https://github.com/MUdevelops/AIRegistry
- Live registry: https://airegistry.instantregret96.workers.dev
- Issues: https://github.com/MUdevelops/AIRegistry/issues
- Pull Requests: https://github.com/MUdevelops/AIRegistry/pulls

---

## Social post

🚀 **AIRegistry 2.0 is live.**

A small, open-source registry for reusable AI components — with a dependency-free Python CLI and a web catalog.

Discover a component → inspect the source → add it to your project.

The catalog now includes 13 building blocks for retrieval, memory, prompts, citations, text processing, validation, tools, agents, and chat.

Community submissions go through GitHub Pull Requests for review instead of directly modifying `main`.

🔗 https://airegistry.instantregret96.workers.dev

💻 https://github.com/MUdevelops/AIRegistry

#AI #OpenSource #Python #Developers #RAG #LLM #AIRegistry
