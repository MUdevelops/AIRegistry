"""Shared test helpers: load component modules from the registry and build temporary registries."""
import contextlib
import importlib.util
import io
import json
import os
import sys
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]

import ai  # noqa: E402
import build_registry  # noqa: E402


def release_dir(name, version):
    return os.path.join(ROOT, "registry", name, "versions", version)


def latest_version(name):
    versions = os.listdir(os.path.join(ROOT, "registry", name, "versions"))
    return max(versions, key=ai.vkey)


def load_component(name, module, version=None):
    """Import registry/<name>/versions/<version>/src/<module>.py as an isolated module."""
    version = version or latest_version(name)
    path = os.path.join(release_dir(name, version), "src", module + ".py")
    spec = importlib.util.spec_from_file_location(f"{module}__{version.replace('.', '_')}", path)
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = loaded  # dataclasses look the module up by name
    spec.loader.exec_module(loaded)
    return loaded


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def make_release(root, dir_name, dir_version, files=None, **manifest):
    """Create registry/<name>/versions/<version>/ with a valid manifest under ``root``."""
    name, version = dir_name, dir_version
    files = files or {"README.md": f"# {name}\n", f"src/{name.replace('-', '_')}.py": "VALUE = 1\n"}
    d = os.path.join(root, "registry", dir_name, "versions", dir_version)
    for rel, text in files.items():
        write(os.path.join(d, *rel.split("/")), text)
    m = {
        "name": name, "version": version, "description": f"The {name} component.",
        "category": "tool", "runtime": "python", "license": "MIT", "tags": ["demo"],
        "dependencies": [], "files": sorted(files),
        "release_notes": f"Release {version}.",
        "source": f"registry/{name}/versions/{version}",
    }
    m.update(manifest)
    write(os.path.join(d, "component.json"), json.dumps(m, indent=2) + "\n")
    return d


def run_ai(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = ai.main(list(argv))
    return code, out.getvalue(), err.getvalue()


def run_builder(root, *extra):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = build_registry.main(["--root", root, *extra])
    return code, out.getvalue(), err.getvalue()


class TempProject(unittest.TestCase):
    """A temporary working directory with an isolated AIREGISTRY_HOME and no REGISTRY_URL."""

    def setUp(self):
        tmp = __import__("tempfile").TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = os.path.realpath(tmp.name)
        self.registry_root = os.path.join(self.tmp, "reg")
        self.project = os.path.join(self.tmp, "project")
        os.makedirs(self.project)
        previous = os.getcwd()
        os.chdir(self.project)
        self.addCleanup(os.chdir, previous)
        patcher = mock.patch.dict(os.environ, {"AIREGISTRY_HOME": os.path.join(self.tmp, "home")})
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("REGISTRY_URL", None)

    def build_registry(self):
        code, out, err = run_builder(self.registry_root)
        self.assertEqual(code, 0, err)
        os.environ["REGISTRY_URL"] = os.path.join(self.registry_root, "registry.json")
        return os.environ["REGISTRY_URL"]

    def read(self, rel):
        with open(os.path.join(self.project, *rel.split("/")), encoding="utf-8") as f:
            return f.read()

    def exists(self, rel):
        return os.path.exists(os.path.join(self.project, *rel.split("/")))
