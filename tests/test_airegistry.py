import contextlib, io, json, os, sys, tempfile, unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import ai, build_registry  # noqa: E402


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def run(*argv):
    o, e = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
        code = ai.main(list(argv))
    return code, o.getvalue(), e.getvalue()


def manifest(name="demo", version="1.0.0", deps=None, source=None):
    return {
        "name": name, "version": version, "description": "demo", "category": "tool",
        "runtime": "python", "license": "MIT", "tags": ["x"], "files": ["README.md", "src/main.py"],
        "source": source or f"registry/{name}/versions/{version}",
        "dependencies": deps or [], "release_notes": "release"
    }


class Base(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name
        old = os.getcwd()
        self.addCleanup(os.chdir, old)
        os.chdir(self.tmp)
        p = mock.patch.dict(os.environ, {"AIREGISTRY_HOME": os.path.join(self.tmp, "home")})
        p.start()
        self.addCleanup(p.stop)
        os.environ.pop("REGISTRY_URL", None)


class TestValidation(unittest.TestCase):
    def test_versions(self):
        self.assertGreater(ai.vkey("1.10.0"), ai.vkey("1.9.9"))
        self.assertEqual(ai.parse_ref("rag"), ("rag", None))
        self.assertEqual(ai.parse_ref("rag@1.2.3"), ("rag", "1.2.3"))
        with self.assertRaises(ai.Err):
            ai.parse_ref("rag@1.0")
        with self.assertRaises(ai.Err):
            ai.validate({**manifest(), "version": "1.0"})

    def test_paths(self):
        for p in ["../x", "/etc/passwd", "a/../b", "C:x", "a\\b", "", "a//b", "./a"]:
            with self.assertRaises(ai.Err):
                ai.safe_rel(p)

    def test_dependency_versions(self):
        self.assertIsNotNone(ai.validate(manifest(deps=["memory@1.0.0 (optional)"])))
        with self.assertRaises(ai.Err):
            ai.validate(manifest(deps=["memory"]))
        with self.assertRaises(ai.Err):
            ai.validate(manifest(deps=["memory@1.0"]))


class TestRegistry(Base):
    def make_registry(self):
        root = self.tmp
        for ver, content in [("1.0.0", "one"), ("1.1.0", "two")]:
            d = os.path.join(root, "registry", "demo", "versions", ver)
            w(os.path.join(d, "README.md"), "# Demo")
            w(os.path.join(d, "src", "main.py"), content)
            m = manifest(version=ver)
            w(os.path.join(d, "component.json"), json.dumps(m))
        build_registry.main(["--root", root])
        return os.path.join(root, "registry.json")

    def test_generation_and_resolution(self):
        path = self.make_registry()
        with open(path, encoding="utf8") as f:
            data = f.read()
        comps = ai.parse_registry(data)
        c, latest = ai.resolve(comps, "demo")
        self.assertEqual(c["latest_version"], "1.1.0")
        self.assertEqual(latest["version"], "1.1.0")
        _, exact = ai.resolve(comps, "demo@1.0.0")
        self.assertEqual(exact["version"], "1.0.0")

    def test_duplicate_release_rejected(self):
        root = self.tmp
        d = os.path.join(root, "registry", "demo", "versions", "1.0.0")
        w(os.path.join(d, "component.json"), json.dumps(manifest()))
        w(os.path.join(d, "README.md"), "# Demo")
        w(os.path.join(d, "src", "main.py"), "x")
        # duplicate is structurally impossible as two directories with the same version;
        # validate duplicate detection at index level instead.
        idx = build_registry.build(root)
        idx["components"][0]["versions"].append(idx["components"][0]["versions"][0])
        with self.assertRaises(ai.Err):
            ai.parse_registry(json.dumps(idx))

    def test_repo_index_fresh(self):
        self.assertEqual(build_registry.main(["--check", "--root", ROOT]), 0)


class TestCLI(Base):
    def test_info_exact_and_search(self):
        url, comps = ai.load_registry()
        c, m = ai.resolve(comps, "rag@0.1.0")
        self.assertEqual(m["name"], "rag")
        self.assertEqual(run("info", "rag@0.1.0")[0], 0)
        self.assertIn("latest", run("info", "rag")[1])
        self.assertEqual(run("info", "rag@9.9.9")[0], 1)
        self.assertEqual(run("search", "rag")[0], 0)

    def test_add_exact_and_lock(self):
        self.assertEqual(run("add", "rag@0.1.0")[0], 0)
        with open(ai.LOCK, encoding="utf8") as f:
            lock = json.load(f)
        self.assertEqual(lock["components"]["rag"]["version"], "0.1.0")
        self.assertTrue(lock["components"]["rag"]["source"].endswith("/0.1.0"))
        self.assertEqual(run("add", "rag@0.1.0")[0], 1)

    def test_dry_run_unknown_and_update(self):
        self.assertEqual(run("add", "rag@0.1.0", "--dry-run")[0], 0)
        self.assertFalse(os.path.exists("ai_components"))
        self.assertEqual(run("add", "rag@9.9.9")[0], 1)
        self.assertEqual(run("add", "chat", "--dry-run")[0], 0)

    def test_offline_cache(self):
        ai.load_registry()
        os.environ["REGISTRY_URL"] = os.path.join(self.tmp, "missing.json")
        self.assertEqual(run("search", "--offline", "memory")[0], 0)

    def test_checksum_mismatch(self):
        root = self.tmp
        d = os.path.join(root, "registry", "demo", "versions", "1.0.0")
        w(os.path.join(d, "README.md"), "# Demo")
        w(os.path.join(d, "src", "main.py"), "x")
        m = manifest()
        m["sha256"] = {"README.md": "0"*64, "src/main.py": "0"*64}
        reg = {"schema_version": 2, "components": [{
            "name": "demo", "description": "demo", "category": "tool", "runtime": "python",
            "license": "MIT", "tags": ["x"], "latest_version": "1.0.0", "versions": [m]
        }]}
        p = os.path.join(root, "registry.json")
        w(p, json.dumps(reg))
        os.environ["REGISTRY_URL"] = p
        self.assertEqual(run("add", "demo@1.0.0")[0], 1)
        self.assertFalse(os.path.exists("ai_components/demo"))

    def test_tampered_lock_path(self):
        victim = os.path.join(self.tmp, "victim.txt")
        w(victim, "keep")
        os.makedirs(".airegistry")
        w(ai.LOCK, json.dumps({"schema_version": 2, "components": {
            "x": {"version": "1.0.0", "dir": "ai_components/x", "files": ["../../victim.txt"]}
        }}))
        self.assertEqual(run("remove", "x")[0], 1)
        self.assertTrue(os.path.exists(victim))


    def test_list_and_remove(self):
        self.assertEqual(run("add", "chat@0.1.0")[0], 0)
        self.assertIn("chat", run("list")[1])
        self.assertEqual(run("remove", "chat")[0], 0)
        self.assertEqual(run("remove", "chat")[0], 1)

    def test_update_latest(self):
        self.assertEqual(run("add", "rag@0.1.0")[0], 0)
        # The current catalog has only one release; update must be stable and idempotent.
        self.assertIn("up to date", run("update")[1])

    def test_force_replaces_installed_release(self):
        self.assertEqual(run("add", "rag@0.1.0")[0], 0)
        self.assertEqual(run("add", "rag@0.1.0", "--force")[0], 0)

    def test_info_versions_are_sorted(self):
        out = run("info", "rag")[1]
        self.assertIn("versions     0.1.0", out)

    def test_malformed_registry(self):
        p = os.path.join(self.tmp, "bad.json")
        w(p, "{bad")
        os.environ["REGISTRY_URL"] = p
        self.assertEqual(run("search", "rag")[0], 1)
        w(p, json.dumps({"components": []}))
        self.assertEqual(run("search", "rag")[0], 1)

    def test_invalid_release_source(self):
        root = self.tmp
        d = os.path.join(root, "registry", "demo", "versions", "1.0.0")
        w(os.path.join(d, "README.md"), "# Demo")
        w(os.path.join(d, "src", "main.py"), "x")
        m = manifest(source="registry/demo")
        w(os.path.join(d, "component.json"), json.dumps(m))
        with self.assertRaises(ai.Err):
            build_registry.build(root)

    def test_generated_registry_contains_all_components(self):
        _, comps = ai.load_registry()
        self.assertEqual(len(comps), 13)
        self.assertIn("rag", comps)
        self.assertEqual(comps["rag"]["latest_version"], "0.1.0")
        self.assertEqual(len(comps["rag"]["versions"]), 1)

    def test_exact_dependency_references(self):
        _, comps = ai.load_registry()
        _, rag = ai.resolve(comps, "rag@0.1.0")
        self.assertEqual(rag["dependencies"], ["citations@0.1.0 (optional)"])

    def test_unknown_component_reference(self):
        self.assertEqual(run("info", "does-not-exist@1.0.0")[0], 1)

    def test_add_traversal_dir(self):
        for d in ["../out", "/tmp/out", "a/../../b"]:
            self.assertEqual(run("add", "chat@0.1.0", "--dir", d)[0], 1)

    def test_dry_run_does_not_write_lock(self):
        self.assertEqual(run("add", "chat@0.1.0", "--dry-run")[0], 0)
        self.assertFalse(os.path.exists(".airegistry/lock.json"))


if __name__ == "__main__":
    unittest.main()
