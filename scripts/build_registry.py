#!/usr/bin/env python3
"""Generate registry.json from registry/<name>/versions/<version>/component.json.

Every release is validated (metadata, files, dependencies, Python syntax) and hashed.
`--check` only verifies, and fails if the committed registry indexes are stale.
"""
import argparse
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from ai import DEP_RE, VER_RE, Err, validate, vkey  # noqa: E402

REGISTRY_FORMAT = 2
IGNORED = {"__pycache__"}


def _read_manifest(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except ValueError as e:
        raise Err(f"invalid JSON in {path}: {e}")


def _release_files(release_dir):
    found = set()
    for base, dirs, files in os.walk(release_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED]
        for name in files:
            rel = os.path.relpath(os.path.join(base, name), release_dir).replace(os.sep, "/")
            if rel != "component.json" and not name.endswith(".pyc"):
                found.add(rel)
    return found


def _check_release(name, version, release_dir, m):
    where = f"{name}@{version}"
    validate(m)
    if m["name"] != name:
        raise Err(f"{where}: name must equal its directory '{name}'")
    if m["version"] != version:
        raise Err(f"{where}: version must equal its directory '{version}'")
    if m["source"] != f"registry/{name}/versions/{version}":
        raise Err(f"{where}: source must be 'registry/{name}/versions/{version}'")
    if not str(m.get("release_notes", "")).strip():
        raise Err(f"{where}: 'release_notes' is required")
    if len(m["description"]) > 280:
        raise Err(f"{where}: description is longer than 280 characters")
    if "README.md" not in m["files"]:
        raise Err(f"{where}: 'files' must include README.md")
    if not any(f.startswith("src/") for f in m["files"]):
        raise Err(f"{where}: 'files' must include at least one file under src/")
    listed = set(m["files"])
    extra = _release_files(release_dir) - listed
    if extra:
        raise Err(f"{where}: files on disk but not listed in 'files': {', '.join(sorted(extra))}")
    sha = {}
    for rel in m["files"]:
        path = os.path.join(release_dir, *rel.split("/"))
        if not os.path.isfile(path):
            raise Err(f"{where}: missing file {rel}")
        with open(path, "rb") as f:
            data = f.read()
        if not data.strip():
            raise Err(f"{where}: {rel} is empty")
        if m["runtime"] == "python" and rel.endswith(".py"):
            try:
                compile(data, path, "exec")
            except SyntaxError as e:
                raise Err(f"{where}: {rel} has a syntax error on line {e.lineno}: {e.msg}")
        sha[rel] = hashlib.sha256(data).hexdigest()
    m = dict(m)
    m.setdefault("dependencies", [])
    m["sha256"] = sha
    return m


def _check_dependencies(releases):
    for comp in releases.values():
        for m in comp.values():
            where = f"{m['name']}@{m['version']}"
            seen = set()
            for dep in m["dependencies"]:
                parsed = DEP_RE.match(dep)
                if not parsed:
                    raise Err(f"{where}: dependency {dep!r} must look like name@MAJOR.MINOR.PATCH or 'name@x.y.z (optional)'")
                dname, dver = parsed[1], parsed[2]
                if dname == m["name"]:
                    raise Err(f"{where}: a component cannot depend on itself")
                if dname in seen:
                    raise Err(f"{where}: duplicate dependency {dname}")
                seen.add(dname)
                if dver not in releases.get(dname, {}):
                    raise Err(f"{where}: dependency {dname}@{dver} is not in the registry")


def build(root):
    base = os.path.join(root, "registry")
    if not os.path.isdir(base):
        raise Err("registry/ directory not found")
    releases = {}
    for name in sorted(os.listdir(base)):
        comp_dir = os.path.join(base, name)
        if not os.path.isdir(comp_dir) or name in IGNORED:
            continue
        versions_dir = os.path.join(comp_dir, "versions")
        if not os.path.isdir(versions_dir):
            raise Err(f"{name}: expected registry/{name}/versions/<version>/")
        stray = [f for f in os.listdir(comp_dir) if f != "versions" and f not in IGNORED]
        if stray:
            raise Err(f"{name}: unexpected entries next to versions/: {', '.join(sorted(stray))}")
        releases[name] = {}
        for version in sorted(os.listdir(versions_dir)):
            release_dir = os.path.join(versions_dir, version)
            if not os.path.isdir(release_dir):
                continue
            if not VER_RE.match(version):
                raise Err(f"{name}: '{version}' is not a MAJOR.MINOR.PATCH directory name")
            manifest_path = os.path.join(release_dir, "component.json")
            if not os.path.isfile(manifest_path):
                raise Err(f"{name}@{version}: component.json is missing")
            releases[name][version] = _check_release(name, version, release_dir, _read_manifest(manifest_path))
        if not releases[name]:
            raise Err(f"{name}: no releases found")
    _check_dependencies(releases)

    components = []
    for name in sorted(releases):
        versions = sorted(releases[name], key=vkey, reverse=True)
        stable = [v for v in versions if not VER_RE.match(v)[4]]
        newest = (stable or versions)[0]
        head = releases[name][newest]
        components.append({
            "name": name,
            "description": head["description"],
            "category": head["category"],
            "runtime": head["runtime"],
            "license": head["license"],
            "tags": head["tags"],
            "latest_version": newest,
            "versions": [releases[name][v] for v in versions],
        })
    return {"version": REGISTRY_FORMAT, "components": components}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="validate; fail if the registry indexes are stale")
    ap.add_argument("--root", default=ROOT)
    a = ap.parse_args(argv)
    try:
        idx = build(a.root)
    except Err as e:
        print("error:", e, file=sys.stderr)
        return 1
    text = (json.dumps(idx, indent=1, sort_keys=True) + "\n").encode()
    targets = [os.path.join(a.root, "registry.json")]
    if os.path.isdir(os.path.join(a.root, "website")):
        targets.append(os.path.join(a.root, "website", "registry.json"))

    def current(t):
        try:
            with open(t, "rb") as f:
                return f.read()
        except OSError:
            return None

    stale = [t for t in targets if current(t) != text]
    releases = sum(len(c["versions"]) for c in idx["components"])
    if a.check:
        if stale:
            print("stale or missing (run: python scripts/build_registry.py):", *stale, file=sys.stderr)
            return 1
        print(f"ok: {len(idx['components'])} components, {releases} releases")
        return 0
    for t in targets:
        with open(t, "wb") as f:
            f.write(text)
        print("wrote", os.path.relpath(t, a.root))
    print(f"{len(idx['components'])} components, {releases} releases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
