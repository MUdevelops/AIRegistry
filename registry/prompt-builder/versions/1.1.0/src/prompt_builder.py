"""prompt-builder: assemble reusable LLM prompts from labelled sections.

A prompt is made of up to four sections, always rendered in this order:
``system``, ``instruction``, ``context`` and ``input``. Sections may contain
``{name}`` placeholders that are filled from keyword variables in a single
pass, so substituted values are never re-interpreted as placeholders.

Standard library only. Python 3.9+.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Mapping, Optional

__all__ = ["PromptBuilder", "build_prompt", "SECTION_ORDER", "__version__"]
__version__ = "1.1.0"

SECTION_ORDER = ("system", "instruction", "context", "input")

_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _fill(text: str, variables: Mapping[str, Any], strict: bool) -> str:
    """Replace ``{name}`` placeholders in one pass.

    Unknown placeholders are left untouched unless ``strict`` is true, in which
    case a ``ValueError`` naming the missing variable is raised.
    """

    def replace(match: "re.Match[str]") -> str:
        key = match.group(1)
        if key in variables:
            return str(variables[key])
        if strict:
            raise ValueError(f"missing value for placeholder {{{key}}}")
        return match.group(0)

    return _PLACEHOLDER.sub(replace, text)


def _clean(section: str, text: Optional[str]) -> str:
    if text is None:
        return ""
    if not isinstance(text, str):
        raise TypeError(f"section {section!r} must be a string, got {type(text).__name__}")
    return text


class PromptBuilder:
    """Collect prompt sections and render them as text or chat messages."""

    def __init__(
        self,
        system: str = "",
        instruction: str = "",
        context: str = "",
        input: str = "",  # noqa: A002 - mirrors the section name
        separator: str = "\n\n",
    ) -> None:
        if not isinstance(separator, str):
            raise TypeError("separator must be a string")
        self._sections: Dict[str, str] = {
            "system": _clean("system", system),
            "instruction": _clean("instruction", instruction),
            "context": _clean("context", context),
            "input": _clean("input", input),
        }
        self.separator = separator

    @property
    def sections(self) -> Dict[str, str]:
        """A copy of the current sections."""
        return dict(self._sections)

    def set(self, section: str, text: Optional[str]) -> "PromptBuilder":
        """Set one section and return ``self`` for chaining."""
        if section not in self._sections:
            raise ValueError(f"unknown section {section!r}; use one of {SECTION_ORDER}")
        self._sections[section] = _clean(section, text)
        return self

    def render(
        self,
        variables: Optional[Mapping[str, Any]] = None,
        *,
        labels: bool = True,
        strict: bool = False,
    ) -> str:
        """Render the prompt text.

        Args:
            variables: Values for ``{name}`` placeholders.
            labels: Prefix each section with a ``## Heading`` line.
            strict: Raise ``ValueError`` for placeholders without a value.
        """
        variables = variables or {}
        parts: List[str] = []
        for name in SECTION_ORDER:
            text = self._sections[name].strip()
            if not text:
                continue
            text = _fill(text, variables, strict)
            parts.append(f"## {name.capitalize()}\n{text}" if labels else text)
        return self.separator.join(parts)

    def build(self, labels: bool = True, strict: bool = False, **variables: Any) -> str:
        """Keyword-variable form of :meth:`render`.

        Variables named ``labels`` or ``strict`` collide with the options; use
        :meth:`render` with a mapping for those.
        """
        return self.render(variables, labels=labels, strict=strict)

    def to_messages(
        self,
        variables: Optional[Mapping[str, Any]] = None,
        *,
        strict: bool = False,
    ) -> List[Dict[str, str]]:
        """Return chat messages: ``system`` becomes the system role, the rest one user message."""
        variables = variables or {}
        messages: List[Dict[str, str]] = []
        system = self._sections["system"].strip()
        if system:
            messages.append({"role": "system", "content": _fill(system, variables, strict)})
        rest = PromptBuilder(**{**self._sections, "system": ""}, separator=self.separator)
        user = rest.render(variables, labels=True, strict=strict)
        if user:
            messages.append({"role": "user", "content": user})
        return messages


def build_prompt(
    system: str = "",
    instruction: str = "",
    context: str = "",
    input: str = "",  # noqa: A002
    **variables: Any,
) -> str:
    """One-call helper: ``build_prompt(instruction="Say {x}", x="hi")``."""
    return PromptBuilder(system, instruction, context, input).build(**variables)
