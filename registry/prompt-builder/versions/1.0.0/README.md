# prompt-builder

Build reusable prompts from system, instruction, context and input sections.

## Install

```bash
ai add prompt-builder
```

Python standard library only.

## API

`PromptBuilder(system, instruction, context, input)` with `.set(section, text)`, `.build(labels=True, **vars)` and `.to_messages(**vars)`; helper `build_prompt(...)`. `{name}` placeholders are filled from `vars`.

## Example

```python
from prompt_builder import PromptBuilder

p = PromptBuilder(system="You are concise.", instruction="Answer in {n} sentence.", input="What is RAG?")
print(p.build(n=1))
print(p.to_messages(n=1))
```
