#!/usr/bin/env python3
"""Migrate a V2.0 flat registry to AIRegistry V2.1 immutable releases.

Run once from the repository root. The script is idempotent and refuses to
overwrite an existing release directory.
"""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    registry = os.path.join(ROOT, "registry")
    if not os.path.isdir(registry):
        print("error: registry directory not found", file=sys.stderr)
        return 1
    migrated = 0
    for name in sorted(os.listdir(registry)):
        d = os.path.join(registry, name)
        manifest_path = os.path.join(d, "component.json")
        if not os.path.isfile(manifest_path):
            continue
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        version = manifest["version"]
        target = os.path.join(d, "versions", version)
        if os.path.exists(target):
            print(f"skip {name}@{version}: target already exists")
            continue
        os.makedirs(target, exist_ok=False)
        os.replace(manifest_path, os.path.join(target, "component.json"))
        for rel in manifest["files"]:
            src = os.path.join(d, *rel.split("/"))
            dst = os.path.join(target, *rel.split("/"))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            os.replace(src, dst)
        migrated += 1
        print(f"migrated {name}@{version}")
    print(f"migrated {migrated} components")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
