import contextlib, io, json, os, sys, tempfile, unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import ai, build_registry  # noqa: E402

M = dict(name="demo", version="1.0.0", description="d", category="tool", runtime="python",
         license="MIT", tags=["x"], files=["a.py"], source="registry/demo")


def w(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def run(*argv):
    o, e = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
        code = ai.main(list(argv))
    return code, o.getvalue(), e.getvalue()


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
    def bad(self, **kw):
        with self.assertRaises(ai.Err):
            ai.validate({**M, **kw})

    def test_valid(self):
        self.assertEqual(ai.validate(dict(M))["name"], "demo")

    def test_missing_and_invalid(self):
        for k in ai.REQUIRED:
            m = dict(M)
            del m[k]
            with self.assertRaises(ai.Err):
                ai.validate(m)
        self.bad(name="Bad Name")
        self.bad(version="1.0")
        self.bad(tags="x")
        self.bad(files=[])
        self.bad(files=["run.exe"])
        self.bad(dependencies=[1])
        with self.assertRaises(ai.Err):
            ai.validate([])

    def test_versions(self):
        self.assertGreater(ai.vkey("1.10.0"), ai.vkey("1.9.9"))
        self.assertGreater(ai.vkey("1.0.0"), ai.vkey("1.0.0-beta"))

    def test_path_traversal_rejected(self):
        for p in ["../x", "/etc/passwd", "a/../b", "C:x", "a\\b", "", "a//b", "./a"]:
            with self.assertRaises(ai.Err, msg=p):
                ai.safe_rel(p)
            self.bad(files=[p])
        self.bad(source="../registry")


class TestRegistry(Base):
    def test_load_and_cache_offline(self):
        _, comps = ai.load_registry()
        self.assertTrue(
    		{"chat", "rag", "agent", "memory", "citations"}.issubset(set(comps))
	)	
        os.environ["REGISTRY_URL"] = os.path.join(self.tmp, "missing.json")
        code, out, err = run("search", "rag")  # falls back to cache
        self.assertEqual(code, 0)
        self.assertIn("cached", err)
        self.assertEqual(run("search", "--offline", "memory")[0], 0)

    def test_malformed_registry(self):
        p = os.path.join(self.tmp, "r.json")
        w(p, "{nope")
        os.environ["REGISTRY_URL"] = p
        self.assertEqual(run("search", "x")[0], 1)
        w(p, json.dumps({"components": [{"name": "x"}]}))
        self.assertEqual(run("search", "x")[0], 1)

    def test_search(self):
        comps = ai.load_registry()[1]
        self.assertEqual(ai.search(comps, "rag")[0]["name"], "rag")
        self.assertEqual(ai.search(comps, "zzzz"), [])
        code, out, _ = run("search", "agent", "tools")
        self.assertIn("agent", out)

    def test_info(self):
        self.assertIn("ai add rag", run("info", "rag")[1])
        self.assertEqual(run("info", "nope")[0], 1)


class TestAddRemove(Base):
    def test_add_list_remove(self):
        code, out, _ = run("add", "rag")
        self.assertEqual(code, 0)
        self.assertIn("+ src/rag.py", out)
        self.assertTrue(os.path.isfile("ai_components/rag/src/rag.py"))
        self.assertIn("rag", run("list")[1])
        self.assertEqual(run("add", "rag")[0], 1)  # already installed
        self.assertEqual(run("remove", "rag")[0], 0)
        self.assertFalse(os.path.exists("ai_components/rag"))
        self.assertEqual(run("remove", "rag")[0], 1)

    def test_dry_run_and_unknown(self):
        self.assertEqual(run("add", "chat", "--dry-run")[0], 0)
        self.assertFalse(os.path.exists("ai_components"))
        self.assertEqual(run("add", "nope")[0], 1)

    def test_dependencies_displayed(self):
        self.assertIn("NOT installed automatically", run("add", "rag", "--dry-run")[1])

    def test_traversal_dir(self):
        for d in ["../out", "/tmp/out", "a/../../b"]:
            self.assertEqual(run("add", "chat", "--dir", d)[0], 1)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "..", "out", "chat")))

    def test_tampered_lock(self):
        victim = os.path.join(self.tmp, "victim.txt")
        w(victim, "keep")
        os.makedirs(".airegistry")
        w(ai.LOCK, json.dumps({"components": {"x": {"version": "1.0.0", "dir": "ai_components/x",
                                                    "files": ["../../victim.txt"]}}}))
        self.assertEqual(run("remove", "x")[0], 1)
        self.assertTrue(os.path.exists(victim))

    def test_checksum_mismatch(self):
        reg = os.path.join(self.tmp, "reg")
        os.makedirs(os.path.join(reg, "registry", "demo"))
        w(os.path.join(reg, "registry", "demo", "a.py"), "x=1\n")
        w(os.path.join(reg, "registry.json"), json.dumps({"components": [{**M, "sha256": {"a.py": "0" * 64}}]}))
        os.environ["REGISTRY_URL"] = os.path.join(reg, "registry.json")
        code, _, err = run("add", "demo")
        self.assertEqual(code, 1)
        self.assertIn("checksum", err)
        self.assertFalse(os.path.exists("ai_components/demo"))

    def test_update(self):
        run("add", "chat")
        with open(ai.LOCK) as f:
            lock = json.load(f)
        lock["components"]["chat"]["version"] = "0.0.1"
        w(ai.LOCK, json.dumps(lock))
        self.assertIn("0.0.1 -> 0.1.0", run("update")[1])
        self.assertIn("up to date", run("update")[1])

    def test_config(self):
        self.assertEqual(run("config", "registry_url", "/x/registry.json")[0], 0)
        self.assertIn("/x/registry.json", run("config")[1])
        self.assertEqual(run("config", "other", "v")[0], 1)


class TestIndex(unittest.TestCase):
    def test_repo_index_is_fresh(self):
        self.assertEqual(build_registry.main(["--check"]), 0)

    def make(self, manifest, files=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        d = os.path.join(tmp.name, "registry", "demo")
        os.makedirs(d)
        w(os.path.join(d, "component.json"), manifest if isinstance(manifest, str) else json.dumps(manifest))
        for n in files or []:
            w(os.path.join(d, n), "x=1\n")
        return tmp.name

    def test_generate_and_check(self):
        root = self.make(M, ["a.py"])
        idx = build_registry.build(root)
        self.assertEqual(len(idx["components"][0]["sha256"]["a.py"]), 64)
        self.assertEqual(build_registry.main(["--check", "--root", root]), 1)  # not written yet
        self.assertEqual(build_registry.main(["--root", root]), 0)
        self.assertEqual(build_registry.main(["--check", "--root", root]), 0)
        w(os.path.join(root, "registry", "demo", "a.py"), "changed\n")
        self.assertEqual(build_registry.main(["--check", "--root", root]), 1)

    def test_malformed_manifests(self):
        with self.assertRaises(ai.Err):
            build_registry.build(self.make("{not json"))
        with self.assertRaises(ai.Err):
            build_registry.build(self.make({"name": "demo"}))
        with self.assertRaises(ai.Err):
            build_registry.build(self.make({**M, "name": "other", "source": "registry/other"}, ["a.py"]))
        with self.assertRaises(ai.Err):
            build_registry.build(self.make(M))  # listed file missing


if __name__ == "__main__":
    unittest.main()
