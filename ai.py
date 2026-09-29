#!/usr/bin/env python3
"""AIRegistry CLI (stdlib only). Copies untrusted files; never executes anything."""
import argparse, hashlib, json, os, re, sys, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_URL = os.path.join(HERE, "registry.json")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
VER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(-[0-9A-Za-z.-]+)?$")
REQUIRED = {"name": str, "version": str, "description": str, "category": str,
            "runtime": str, "license": str, "tags": list, "files": list, "source": str}
BAD_EXT = {".exe", ".dll", ".so", ".dylib", ".bat", ".cmd", ".ps1", ".msi", ".com", ".scr", ".jar"}
MAX_BYTES = 2_000_000
LOCK = os.path.join(".airegistry", "lock.json")


class Err(Exception):
    pass


def warn(s):
    print("warning: " + s, file=sys.stderr)


# ---- validation -----------------------------------------------------------
def safe_rel(p):
    """Return path parts of a safe relative POSIX path, else raise."""
    if (not isinstance(p, str) or not p or "\0" in p or "\\" in p or ":" in p
            or p.startswith("/")):
        raise Err(f"unsafe path: {p!r}")
    parts = p.split("/")
    if any(x in ("", ".", "..") for x in parts):
        raise Err(f"unsafe path: {p!r}")
    return parts


def validate(m):
    if not isinstance(m, dict):
        raise Err("manifest must be a JSON object")
    for k, t in REQUIRED.items():
        if k not in m:
            raise Err(f"missing field '{k}'")
        if not isinstance(m[k], t):
            raise Err(f"field '{k}' must be {t.__name__}")
        if t is str and not m[k].strip():
            raise Err(f"field '{k}' is empty")
    if not NAME_RE.match(m["name"]):
        raise Err(f"invalid name {m['name']!r} (use a-z 0-9 -)")
    if not VER_RE.match(m["version"]):
        raise Err(f"invalid version {m['version']!r} (use MAJOR.MINOR.PATCH)")
    deps = m.get("dependencies", [])
    for k, v in (("tags", m["tags"]), ("files", m["files"]), ("dependencies", deps)):
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            raise Err(f"'{k}' must be a list of strings")
    if not m["files"] or len(set(m["files"])) != len(m["files"]):
        raise Err("'files' must be non-empty and unique")
    for f in m["files"]:
        safe_rel(f)
        if os.path.splitext(f)[1].lower() in BAD_EXT:
            raise Err(f"executable file type not allowed: {f}")
    safe_rel(m["source"])
    return m


def vkey(v):
    m = VER_RE.match(v) if isinstance(v, str) else None
    return (int(m[1]), int(m[2]), int(m[3]), 0 if m[4] else 1) if m else (0, 0, 0, 0)


def parse_registry(data):
    try:
        reg = json.loads(data)
    except ValueError as e:
        raise Err(f"registry is not valid JSON: {e}")
    if not isinstance(reg, dict) or not isinstance(reg.get("components"), list):
        raise Err("registry needs a 'components' list")
    out = {}
    for m in reg["components"]:
        validate(m)
        if m["name"] in out:
            raise Err(f"duplicate component {m['name']}")
        sh = m.get("sha256", {})
        if not isinstance(sh, dict) or set(sh) - set(m["files"]):
            raise Err(f"bad sha256 map for {m['name']}")
        out[m["name"]] = m
    return out


# ---- io / config ----------------------------------------------------------
def fetch(loc):
    try:
        if re.match(r"^https?://", loc):
            req = urllib.request.Request(loc, headers={"User-Agent": "airegistry"})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = r.read(MAX_BYTES + 1)
        else:
            with open(loc, "rb") as f:
                data = f.read(MAX_BYTES + 1)
    except Exception as e:
        raise Err(f"cannot fetch {loc}: {e}")
    if len(data) > MAX_BYTES:
        raise Err(f"{loc} is too large")
    return data


def join(base, rel):
    if re.match(r"^https?://", base):
        return urllib.parse.urljoin(base, rel)
    return os.path.join(os.path.dirname(base), *rel.split("/"))


def home():
    return os.environ.get("AIREGISTRY_HOME") or os.path.join(os.path.expanduser("~"), ".airegistry")


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            v = json.load(f)
        return v if isinstance(v, dict) else {}
    except (OSError, ValueError):
        return {}


def registry_url():
    return (os.environ.get("REGISTRY_URL")
            or read_json(os.path.join(home(), "config.json")).get("registry_url") or DEFAULT_URL)


def load_registry(offline=False):
    url, cache = registry_url(), os.path.join(home(), "registry.json")
    data, fresh = None, False
    if not offline:
        try:
            data, fresh = fetch(url), True
        except Err as e:
            if not os.path.exists(cache):
                raise
            warn(f"{e}; using cached registry")
    if data is None:
        try:
            with open(cache, "rb") as f:
                data = f.read()
        except OSError:
            raise Err("no cached registry yet; run once without --offline")
    comps = parse_registry(data)
    if fresh:
        os.makedirs(home(), exist_ok=True)
        with open(cache, "wb") as f:
            f.write(data)
    return url, comps


def read_lock(root):
    p = os.path.join(root, LOCK)
    if not os.path.exists(p):
        return {"components": {}}
    try:
        with open(p, encoding="utf-8") as f:
            lock = json.load(f)
        ok = isinstance(lock.get("components"), dict)
    except (OSError, ValueError, AttributeError):
        ok = False
    if not ok:
        raise Err(f"corrupt lock file {LOCK}")
    return lock


def write_lock(root, lock):
    p = os.path.join(root, LOCK)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(lock, f, indent=1, sort_keys=True)


def safe_dest(root, rel_dir, f):
    """Resolve rel_dir/f under root; reject traversal and symlink escapes."""
    parts = safe_rel(rel_dir) + safe_rel(f)
    real = os.path.realpath(root)
    p = os.path.realpath(os.path.join(real, *parts))
    if os.path.commonpath([real, p]) != real:
        raise Err(f"path escapes project: {'/'.join(parts)}")
    return os.path.join(root, *parts)


# ---- core ops -------------------------------------------------------------
def search(comps, q):
    terms, res = q.lower().split(), []
    for m in comps.values():
        hay = " ".join([m["name"], m["description"], m["category"], *m["tags"]]).lower()
        if all(t in hay for t in terms):
            score = sum(3 if t in m["name"] else 2 if t in m["tags"] else 1 for t in terms)
            res.append((-score, m["name"], m))
    return [r[2] for r in sorted(res, key=lambda r: r[:2])]


def get_file(url, m, f):
    data = fetch(join(url, m["source"] + "/" + f))
    h = m.get("sha256", {}).get(f)
    if h and hashlib.sha256(data).hexdigest() != h:
        raise Err(f"checksum mismatch for {f}")
    return data


def prune(top):
    for d, _, _ in os.walk(top, topdown=False):
        try:
            os.rmdir(d)
        except OSError:
            pass


def install(m, url, root, rel_dir, lock, dry, force):
    d = f"{rel_dir}/{m['name']}"
    targets = [(f, safe_dest(root, d, f)) for f in m["files"]]
    if not force:
        for _, p in targets:
            if os.path.exists(p):
                raise Err(f"{p} exists; use --force to overwrite")
    print(f"{'would add' if dry else 'add'} {m['name']} {m['version']} -> {d}/")
    for f, _ in targets:
        print("  + " + f)
    if m.get("dependencies"):
        print("  dependencies (NOT installed automatically): " + ", ".join(m["dependencies"]))
    if not m.get("sha256"):
        warn("registry provides no checksums; files are unverified")
    blobs = [get_file(url, m, f) for f, _ in targets]
    if dry:
        return
    for (_, p), b in zip(targets, blobs):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(b)
    old = lock["components"].get(m["name"])
    if isinstance(old, dict) and isinstance(old.get("files"), list):
        for f in old["files"]:
            if f not in m["files"]:
                p = safe_dest(root, d, f)
                if os.path.isfile(p):
                    os.remove(p)
                    print("  - " + f + " (no longer in component)")
        prune(os.path.join(root, *safe_rel(d)))
    lock["components"][m["name"]] = {"version": m["version"], "dir": d, "files": list(m["files"])}
    write_lock(root, lock)


# ---- commands -------------------------------------------------------------
def cmd_search(a):
    _, comps = load_registry(a.offline)
    res = search(comps, " ".join(a.query))
    for m in res:
        print(f"{m['name']:<12}{m['version']:<9}{m['category']:<10}{m['description']}")
    if not res:
        print("no matches")


def cmd_info(a):
    _, comps = load_registry(a.offline)
    m = comps.get(a.component)
    if not m:
        raise Err(f"unknown component '{a.component}' (try: ai search {a.component})")
    for k in ("name", "version", "description", "category", "runtime", "license", "source"):
        print(f"{k:<13}{m[k]}")
    print(f"{'tags':<13}{', '.join(m['tags'])}")
    print(f"{'dependencies':<13}{', '.join(m.get('dependencies', [])) or 'none'}")
    print(f"{'files':<13}{', '.join(m['files'])}")
    print(f"\ninstall: ai add {m['name']}")


def cmd_add(a):
    url, comps = load_registry(a.offline)
    m = comps.get(a.component)
    if not m:
        raise Err(f"unknown component '{a.component}' (try: ai search {a.component})")
    safe_rel(a.dir)
    root = os.getcwd()
    lock = read_lock(root)
    if m["name"] in lock["components"] and not a.force:
        raise Err(f"{m['name']} already installed; use 'ai update' or --force")
    install(m, url, root, a.dir, lock, a.dry_run, a.force)


def cmd_remove(a):
    root = os.getcwd()
    lock = read_lock(root)
    e = lock["components"].get(a.component)
    if e is None:
        raise Err(f"'{a.component}' is not installed")
    if not (isinstance(e, dict) and isinstance(e.get("dir"), str) and isinstance(e.get("files"), list)):
        raise Err("corrupt lock entry")
    paths = [safe_dest(root, e["dir"], f) for f in e["files"]]
    print(f"{'would remove' if a.dry_run else 'remove'} {a.component}:")
    for p in paths:
        print("  - " + os.path.relpath(p, root))
    if a.dry_run:
        return
    for p in paths:
        if os.path.isfile(p):
            os.remove(p)
    prune(os.path.join(root, *safe_rel(e["dir"])))
    del lock["components"][a.component]
    write_lock(root, lock)


def cmd_list(a):
    if a.all:
        _, comps = load_registry(a.offline)
        for m in comps.values():
            print(f"{m['name']:<12}{m['version']:<9}{m['description']}")
        return
    comps = read_lock(os.getcwd())["components"]
    for n, e in sorted(comps.items()):
        print(f"{n:<12}{e.get('version', '?'):<9}{e.get('dir', '?')}")
    if not comps:
        print("nothing installed (try: ai search <query>)")


def cmd_update(a):
    url, comps = load_registry(a.offline)
    root = os.getcwd()
    lock = read_lock(root)
    n = 0
    for name, e in sorted(lock["components"].items()):
        m = comps.get(name)
        if not m:
            warn(f"{name} is no longer in the registry")
            continue
        if not (isinstance(e, dict) and isinstance(e.get("dir"), str) and "/" in e["dir"]):
            raise Err("corrupt lock entry")
        if vkey(m["version"]) > vkey(e.get("version")):
            print(f"{name}: {e.get('version')} -> {m['version']} (overwrites local edits)")
            install(m, url, root, e["dir"].rsplit("/", 1)[0], lock, a.dry_run, True)
            n += 1
    if not n:
        print("everything is up to date")


def cmd_config(a):
    p = os.path.join(home(), "config.json")
    if a.key:
        if a.key != "registry_url" or not a.value:
            raise Err("usage: ai config registry_url <path-or-https-url>")
        cfg = read_json(p)
        cfg["registry_url"] = a.value
        os.makedirs(home(), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=1)
        print(f"wrote {p}")
    print(f"registry_url  {registry_url()}\nhome          {home()}\nconfig file   {p}")


def build_parser():
    p = argparse.ArgumentParser("ai", description="AIRegistry: reusable AI components.")
    s = p.add_subparsers(dest="cmd", required=True)

    def sub(name, fn, help, offline=True, dry=False):
        sp = s.add_parser(name, help=help)
        sp.set_defaults(fn=fn, dry_run=False, offline=False)
        if offline:
            sp.add_argument("--offline", action="store_true", help="use cached registry only")
        if dry:
            sp.add_argument("--dry-run", action="store_true", help="show changes, write nothing")
        return sp

    sub("search", cmd_search, "search components").add_argument("query", nargs="*")
    sub("info", cmd_info, "show component details").add_argument("component")
    sp = sub("add", cmd_add, "add a component to this project", dry=True)
    sp.add_argument("component")
    sp.add_argument("--dir", default="ai_components", help="relative target dir")
    sp.add_argument("--force", action="store_true", help="overwrite existing files")
    sub("remove", cmd_remove, "remove an installed component", offline=False, dry=True).add_argument("component")
    sub("list", cmd_list, "list installed components").add_argument("--all", action="store_true")
    sub("update", cmd_update, "refresh registry and update components", dry=True)
    sp = sub("config", cmd_config, "show or set config", offline=False)
    sp.add_argument("key", nargs="?")
    sp.add_argument("value", nargs="?")
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    try:
        a.fn(a)
        return 0
    except Err as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
