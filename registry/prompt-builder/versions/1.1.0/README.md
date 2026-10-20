# prompt-builder

**Version 1.1.0** · Python 3.9+ · standard library only · MIT

Assemble reusable LLM prompts from labelled sections, with safe `{placeholder}` substitution and chat-message output.

## Install

```bash
ai add prompt-builder@1.1.0
```

## Quick start

```python
from prompt_builder import PromptBuilder

prompt = PromptBuilder(
    system="You are a concise assistant.",
    instruction="Answer in {language}.",
    context="AIRegistry installs reusable AI components.",
    input="What is AIRegistry?",
)

print(prompt.build(language="English"))
messages = prompt.to_messages({"language": "English"})   # [{"role": "system", ...}, {"role": "user", ...}]
```

## API

| Name | Description |
|---|---|
| `PromptBuilder(system="", instruction="", context="", input="", separator="\n\n")` | Holds the four sections. Sections must be strings (or `None`). |
| `.set(section, text)` | Replace one section; returns the builder for chaining. Unknown sections raise `ValueError`. |
| `.sections` | Copy of the current sections. |
| `.render(variables=None, *, labels=True, strict=False)` | Render text. `labels=False` omits the `## Heading` lines. |
| `.build(labels=True, strict=False, **variables)` | Keyword-variable form of `render`. |
| `.to_messages(variables=None, *, strict=False)` | Chat messages: system role plus one user message. |
| `build_prompt(system, instruction, context, input, **variables)` | One-call helper. |

## Behavior

- Sections render in a fixed order: `system`, `instruction`, `context`, `input`. Empty sections are skipped.
- Placeholders match `{name}` with `name` a Python identifier. Substitution is single-pass, so a value that itself contains `{other}` is **not** expanded again.
- Unknown placeholders are left as written. Pass `strict=True` to raise `ValueError` instead.
- `to_messages` also fills placeholders in the system section.

## Changes in 1.1.0

Single-pass substitution (fixes re-expansion of substituted values), `strict` mode, `render()` for variables that clash with option names, type checks on sections, and placeholder filling for the system message.
