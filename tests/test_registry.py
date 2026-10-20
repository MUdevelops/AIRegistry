"""Integrity checks for the real registry in this repository."""
import json
import os
import re
import unittest

from _helpers import ROOT, ai, build_registry, run_builder

EXPECTED = {
    "agent", "citation-builder", "context-builder", "conversation-memory", "json-validator",
    "keyword-rag", "prompt-builder", "query-rewriter", "retrieval-pipeline", "text-chunker", "tool-router",
}
CONFLICT = re.compile(r"^(<{7} |={7}$|>{7} )", re.M)


class TestRealRegistry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = build_registry.build(ROOT)
        cls.components = {c["name"]: c for c in cls.index["components"]}

    def test_indexes_are_up_to_date(self):
        code, out, err = run_builder(ROOT, "--check")
        self.assertEqual(code, 0, err)

    def test_catalog_contents(self):
        self.assertEqual(set(self.components), EXPECTED)

    def test_committed_indexes_are_identical_and_parse_with_the_cli(self):
        with open(os.path.join(ROOT, "registry.json"), "rb") as a, \
                open(os.path.join(ROOT, "website", "registry.json"), "rb") as b:
            data = a.read()
            self.assertEqual(data, b.read())
        self.assertEqual(set(ai.parse_registry(data)), EXPECTED)

    def test_latest_release_is_documented_and_consistent(self):
        for name, comp in self.components.items():
            latest = comp["versions"][0]
            self.assertEqual(latest["version"], comp["latest_version"], name)
            readme = open(os.path.join(ROOT, latest["source"], "README.md"), encoding="utf-8").read()
            self.assertIn(f"ai add {name}@{latest['version']}", readme, name)
            self.assertIn(f"**Version {latest['version']}**", readme, name)
            for heading in ("## Install", "## Quick start", "## API"):
                self.assertIn(heading, readme, f"{name} README lacks {heading}")
            self.assertIn("MIT", readme)

    def test_modules_declare_matching_version_and_all(self):
        for name, comp in self.components.items():
            latest = comp["versions"][0]
            for rel in latest["files"]:
                if rel.startswith("src/") and rel.endswith(".py"):
                    source = open(os.path.join(ROOT, latest["source"], rel), encoding="utf-8").read()
                    self.assertIn(f'__version__ = "{latest["version"]}"', source, f"{name}/{rel}")
                    self.assertIn("__all__", source, f"{name}/{rel}")
                    self.assertTrue(source.lstrip().startswith('"""'), f"{name}/{rel} needs a module docstring")

    def test_components_are_stdlib_only(self):
        stdlib = set(getattr(__import__("sys"), "stdlib_module_names", ())) | {
            "__future__", "collections", "dataclasses", "importlib", "json", "math", "pathlib", "re",
            "string", "time", "typing", "unicodedata",
        }
        allowed_local = {"keyword_rag"}  # optional sibling lookup inside context-builder
        for comp in self.components.values():
            for release in comp["versions"]:
                for rel in release["files"]:
                    if not rel.endswith(".py"):
                        continue
                    tree = __import__("ast").parse(open(os.path.join(ROOT, release["source"], rel), encoding="utf-8").read())
                    for node in __import__("ast").walk(tree):
                        mods = []
                        if isinstance(node, __import__("ast").Import):
                            mods = [a.name for a in node.names]
                        elif isinstance(node, __import__("ast").ImportFrom) and node.level == 0:
                            mods = [node.module]
                        for mod in mods:
                            self.assertIn(mod.split(".")[0], stdlib | allowed_local, f"{release['source']}/{rel} imports {mod}")

    def test_no_merge_conflict_markers_or_stray_files(self):
        skip = {".git", "node_modules", "__pycache__", "readme_assets"}
        for base, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in skip]
            for f in files:
                self.assertFalse(f.endswith((".pyc", ".bak", ".orig", ".rej")), f)
                if f.endswith((".md", ".py", ".json", ".js", ".html", ".yml", ".toml", ".jsonc")):
                    text = open(os.path.join(base, f), encoding="utf-8", errors="replace").read()
                    self.assertIsNone(CONFLICT.search(text), f"merge conflict marker in {os.path.join(base, f)}")

    def test_version_numbers_agree(self):
        pyproject = open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8").read()
        self.assertIn(f'version = "{ai.__version__}"', pyproject)
        changelog = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8").read()
        self.assertIn(f"## {ai.__version__}", changelog)

    def test_every_release_directory_is_immutable_layout(self):
        for name in EXPECTED:
            versions = os.path.join(ROOT, "registry", name, "versions")
            self.assertEqual(os.listdir(os.path.join(ROOT, "registry", name)), ["versions"])
            for v in os.listdir(versions):
                self.assertTrue(os.path.isfile(os.path.join(versions, v, "component.json")))


if __name__ == "__main__":
    unittest.main()
