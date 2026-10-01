#!/usr/bin/env python3
"""Generate registry.json from registry/*/component.json. `--check` only verifies."""
import argparse, hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from ai import Err, validate  # noqa: E402


def build(root):
    base = os.path.join(root, "registry")
    comps = []
    for d in sorted(os.listdir(base)):
        mf = os.path.join(base, d, "component.json")
        if not os.path.isfile(mf):
            continue
        try:
            with open(mf, encoding="utf-8") as f:
                m = json.load(f)
            validate(m)
        except ValueError as e:
            raise Err(f"{d}: invalid JSON: {e}")
        except Err as e:
            raise Err(f"{d}: {e}")
        if m["name"] != d or m["source"] != f"registry/{d}":
            raise Err(f"{d}: name must equal directory and source must be 'registry/{d}'")
        m["sha256"] = {}
        for rel in m["files"]:
            p = os.path.join(base, d, *rel.split("/"))
            if not os.path.isfile(p):
                raise Err(f"{d}: missing file {rel}")
            with open(p, "rb") as f:
                m["sha256"][rel] = hashlib.sha256(f.read()).hexdigest()
        comps.append(m)
    return {"version": 1, "components": comps}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="validate; fail if registry.json is stale")
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
        print(f"ok: {len(idx['components'])} components")
        return 0
    for t in targets:
        with open(t, "wb") as f:
            f.write(text)
        print("wrote", os.path.relpath(t, a.root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
