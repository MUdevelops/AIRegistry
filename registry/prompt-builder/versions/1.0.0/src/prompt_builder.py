"""prompt-builder: assemble reusable prompts from labelled sections."""

SECTION_ORDER = ("system", "instruction", "context", "input")


class PromptBuilder:
    def __init__(self, system="", instruction="", context="", input="", separator="\n\n"):
        self.sections = {"system": system, "instruction": instruction, "context": context, "input": input}
        self.separator = separator

    def set(self, section, text):
        if section not in self.sections:
            raise ValueError(f"unknown section {section!r}; use one of {SECTION_ORDER}")
        self.sections[section] = text or ""
        return self

    def build(self, labels=True, **variables):
        """Return the prompt text. {name} placeholders are filled from variables."""
        parts = []
        for name in SECTION_ORDER:
            text = self.sections[name].strip()
            if not text:
                continue
            for key, value in variables.items():
                text = text.replace("{" + key + "}", str(value))
            parts.append(f"## {name.capitalize()}\n{text}" if labels else text)
        return self.separator.join(parts)

    def to_messages(self, **variables):
        """Return chat-style messages: system section -> system role, rest -> user."""
        messages = []
        system = self.sections["system"].strip()
        if system:
            messages.append({"role": "system", "content": system})
        rest = PromptBuilder(**{**self.sections, "system": ""}, separator=self.separator)
        user = rest.build(labels=True, **variables)
        if user:
            messages.append({"role": "user", "content": user})
        return messages


def build_prompt(system="", instruction="", context="", input="", **variables):
    return PromptBuilder(system, instruction, context, input).build(**variables)
