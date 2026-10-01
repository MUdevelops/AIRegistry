#!/usr/bin/env python3
"""Generate the schema-v2 AIRegistry index from immutable component releases."""
import argparse, hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from ai import Err, validate, vkey  # noqa: E402


def build(root):
    base = os.path.join(root, "registry")
    if not os.path.isdir(base):
        raise Err("registry directory is missing")
    components = []
    for name in sorted(os.listdir(base)):
        comp_dir = os.path.join(base, name)
        versions_dir = os.path.join(comp_dir, "versions")
        if not os.path.isdir(versions_dir):
            continue
        releases = []
        for version in sorted(os.listdir(versions_dir), key=vkey, reverse=True):
            release_dir = os.path.join(versions_dir, version)
            mf = os.path.join(release_dir, "component.json")
            if not os.path.isfile(mf):
                raise Err(f"{name}@{version}: component.json is missing")
            try:
                with open(mf, encoding="utf-8") as f:
                    m = json.load(f)
                validate(m)
            except ValueError as e:
                raise Err(f"{name}@{version}: invalid JSON: {e}")
            except Err as e:
                raise Err(f"{name}@{version}: {e}")
            if m["name"] != name or m["version"] != version:
                raise Err(f"{name}@{version}: name/version must match directory")
            expected_source = f"registry/{name}/versions/{version}"
            if m["source"] != expected_source:
                raise Err(f"{name}@{version}: source must be {expected_source!r}")
            m["sha256"] = {}
            for rel in m["files"]:
                p = os.path.join(release_dir, *rel.split("/"))
                if not os.path.isfile(p):
                    raise Err(f"{name}@{version}: missing file {rel}")
                with open(p, "rb") as f:
                    m["sha256"][rel] = hashlib.sha256(f.read()).hexdigest()
            releases.append(m)
        if not releases:
            raise Err(f"{name}: no releases")
        releases.sort(key=lambda x: vkey(x["version"]), reverse=True)
        latest = releases[0]
        components.append({
            "name": name,
            "description": latest["description"],
            "category": latest["category"],
            "runtime": latest["runtime"],
            "license": latest["license"],
            "tags": latest["tags"],
            "latest_version": latest["version"],
            "versions": releases,
        })
    return {"schema_version": 2, "components": components}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
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
    if a.check:
        if stale:
            print("stale or missing:", *stale, file=sys.stderr)
            return 1
        print(f"ok: {len(idx['components'])} components, {sum(len(c['versions']) for c in idx['components'])} releases")
        return 0
    for t in targets:
        with open(t, "wb") as f:
            f.write(text)
        print("wrote", os.path.relpath(t, a.root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
