import json
import os
import unittest
from unittest import mock

from _helpers import TempProject, ai, make_release, run_ai, write


class CliCase(TempProject):
    def setUp(self):
        super().setUp()
        make_release(self.registry_root, "demo", "1.0.0",
                     files={"README.md": "# demo 1\n", "src/demo.py": "VALUE = 1\n", "src/old.py": "OLD = 1\n"},
                     description="Demo retrieval helper", tags=["rag", "demo"], category="retrieval")
        make_release(self.registry_root, "demo", "1.1.0",
                     files={"README.md": "# demo 1.1\n", "src/demo.py": "VALUE = 2\n"},
                     description="Demo retrieval helper", tags=["rag", "demo"], category="retrieval")
        make_release(self.registry_root, "other", "1.0.0", description="Something else", tags=["misc"],
                     dependencies=["demo@1.1.0"])
        self.url = self.build_registry()


class TestSearchInfoList(CliCase):
    def test_search_matches_name_tags_and_description(self):
        code, out, _ = run_ai("search", "rag")
        self.assertEqual(code, 0)
        self.assertIn("demo", out)
        self.assertIn("1.1.0", out)
        self.assertNotIn("other", out)

    def test_search_requires_all_terms_and_reports_no_matches(self):
        self.assertIn("no matches", run_ai("search", "rag", "zzz")[1])

    def test_search_ranks_name_matches_first(self):
        _, out, _ = run_ai("search", "demo")
        self.assertLess(out.index("demo"), out.index("other") if "other" in out else len(out))

    def test_info_shows_latest_releases_and_install_hint(self):
        code, out, _ = run_ai("info", "demo")
        self.assertEqual(code, 0)
        self.assertIn("1.1.0", out)
        self.assertIn("1.1.0, 1.0.0", out)
        self.assertIn("install: ai add demo@1.1.0", out)

    def test_info_for_pinned_version(self):
        _, out, _ = run_ai("info", "demo@1.0.0")
        self.assertIn("install: ai add demo@1.0.0", out)
        self.assertIn("src/old.py", out)

    def test_info_errors(self):
        code, _, err = run_ai("info", "missing")
        self.assertEqual(code, 1)
        self.assertIn("unknown component", err)
        code, _, err = run_ai("info", "demo@9.9.9")
        self.assertEqual(code, 1)
        self.assertIn("available: 1.1.0, 1.0.0", err)
        self.assertEqual(run_ai("info", "Bad Name")[0], 1)

    def test_list_all_shows_latest_only(self):
        _, out, _ = run_ai("list", "--all")
        self.assertIn("demo", out)
        self.assertNotIn("1.0.0  Demo", out.replace("   ", "  "))

    def test_list_installed_empty(self):
        self.assertIn("nothing installed", run_ai("list")[1])

    def test_version_flag(self):
        with self.assertRaises(SystemExit) as ctx:
            run_ai("--version")
        self.assertEqual(ctx.exception.code, 0)


class TestAdd(CliCase):
    def test_add_installs_latest_and_writes_lock(self):
        code, out, _ = run_ai("add", "demo")
        self.assertEqual(code, 0)
        self.assertIn("add demo@1.1.0", out)
        self.assertEqual(self.read("ai_components/demo/src/demo.py"), "VALUE = 2\n")
        lock = json.loads(self.read(".airegistry/lock.json"))
        self.assertEqual(lock["components"]["demo"]["version"], "1.1.0")
        self.assertEqual(sorted(lock["components"]["demo"]["files"]), ["README.md", "src/demo.py"])

    def test_add_pinned_version(self):
        self.assertEqual(run_ai("add", "demo@1.0.0")[0], 0)
        self.assertEqual(self.read("ai_components/demo/src/demo.py"), "VALUE = 1\n")
        self.assertTrue(self.exists("ai_components/demo/src/old.py"))

    def test_add_dry_run_writes_nothing(self):
        code, out, _ = run_ai("add", "demo", "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("would add demo@1.1.0", out)
        self.assertFalse(self.exists("ai_components"))
        self.assertFalse(self.exists(".airegistry"))

    def test_add_custom_directory(self):
        self.assertEqual(run_ai("add", "demo", "--dir", "vendor/ai")[0], 0)
        self.assertTrue(self.exists("vendor/ai/demo/src/demo.py"))

    def test_add_rejects_unsafe_directory(self):
        for bad in ("../x", "/abs", "a/../b"):
            self.assertEqual(run_ai("add", "demo", "--dir", bad)[0], 1)

    def test_add_twice_explains_what_to_do(self):
        run_ai("add", "demo@1.0.0")
        code, _, err = run_ai("add", "demo@1.0.0")
        self.assertEqual(code, 1)
        self.assertIn("already installed", err)
        self.assertIn("--force", err)
        code, _, err = run_ai("add", "demo")
        self.assertIn("ai update", err)

    def test_force_reinstalls(self):
        run_ai("add", "demo")
        write(os.path.join(self.project, "ai_components", "demo", "src", "demo.py"), "EDITED\n")
        self.assertEqual(run_ai("add", "demo", "--force")[0], 0)
        self.assertEqual(self.read("ai_components/demo/src/demo.py"), "VALUE = 2\n")

    def test_existing_files_are_not_overwritten_without_force(self):
        write(os.path.join(self.project, "ai_components", "demo", "src", "demo.py"), "MINE\n")
        code, _, err = run_ai("add", "demo")
        self.assertEqual(code, 1)
        self.assertIn("exists", err)
        self.assertEqual(self.read("ai_components/demo/src/demo.py"), "MINE\n")

    def test_dependencies_are_listed_not_installed(self):
        code, out, _ = run_ai("add", "other")
        self.assertEqual(code, 0)
        self.assertIn("requires (not installed automatically): demo@1.1.0", out)
        self.assertFalse(self.exists("ai_components/demo"))

    def test_checksum_mismatch_aborts_before_writing(self):
        path = os.path.join(self.registry_root, "registry", "demo", "versions", "1.1.0", "src", "demo.py")
        write(path, "TAMPERED = True\n")
        code, _, err = run_ai("add", "demo")
        self.assertEqual(code, 1)
        self.assertIn("checksum mismatch", err)
        self.assertFalse(self.exists("ai_components"))


class TestUpdateRemove(CliCase):
    def test_update_moves_to_latest_and_drops_removed_files(self):
        run_ai("add", "demo@1.0.0")
        code, out, _ = run_ai("update")
        self.assertEqual(code, 0)
        self.assertIn("demo: 1.0.0 -> 1.1.0", out)
        self.assertEqual(self.read("ai_components/demo/src/demo.py"), "VALUE = 2\n")
        self.assertFalse(self.exists("ai_components/demo/src/old.py"))
        self.assertEqual(json.loads(self.read(".airegistry/lock.json"))["components"]["demo"]["version"], "1.1.0")

    def test_update_when_current(self):
        run_ai("add", "demo")
        self.assertIn("up to date", run_ai("update")[1])

    def test_update_dry_run(self):
        run_ai("add", "demo@1.0.0")
        run_ai("update", "--dry-run")
        self.assertEqual(self.read("ai_components/demo/src/demo.py"), "VALUE = 1\n")

    def test_update_named_component_and_unknown(self):
        run_ai("add", "demo@1.0.0")
        self.assertEqual(run_ai("update", "demo")[0], 0)
        code, _, err = run_ai("update", "other")
        self.assertEqual(code, 1)
        self.assertIn("not installed", err)

    def test_remove_deletes_files_and_empty_directories(self):
        run_ai("add", "demo")
        code, out, _ = run_ai("remove", "demo")
        self.assertEqual(code, 0)
        self.assertFalse(self.exists("ai_components/demo"))
        self.assertEqual(json.loads(self.read(".airegistry/lock.json"))["components"], {})

    def test_remove_dry_run_and_unknown(self):
        run_ai("add", "demo")
        self.assertIn("would remove", run_ai("remove", "demo", "--dry-run")[1])
        self.assertTrue(self.exists("ai_components/demo/src/demo.py"))
        self.assertEqual(run_ai("remove", "nothing")[0], 1)

    def test_remove_keeps_user_files_it_did_not_install(self):
        run_ai("add", "demo")
        write(os.path.join(self.project, "ai_components", "demo", "notes.txt"), "mine\n")
        run_ai("remove", "demo")
        self.assertTrue(self.exists("ai_components/demo/notes.txt"))

    def test_list_installed(self):
        run_ai("add", "demo")
        _, out, _ = run_ai("list")
        self.assertIn("demo", out)
        self.assertIn("1.1.0", out)

    def test_corrupt_lock_is_reported(self):
        write(os.path.join(self.project, ".airegistry", "lock.json"), "{not json")
        code, _, err = run_ai("list")
        self.assertEqual(code, 1)
        self.assertIn("corrupt lock", err)

    def test_lock_entry_with_traversal_is_rejected_on_remove(self):
        write(os.path.join(self.project, ".airegistry", "lock.json"),
              json.dumps({"components": {"demo": {"version": "1.0.0", "dir": "ai_components/demo", "files": ["../../x"]}}}))
        code, _, err = run_ai("remove", "demo")
        self.assertEqual(code, 1)
        self.assertIn("unsafe path", err)


class TestRegistryLoading(TempProject):
    def setUp(self):
        super().setUp()
        make_release(self.registry_root, "demo", "1.0.0")
        self.url = self.build_registry()

    def test_cache_is_used_when_registry_is_unreachable(self):
        self.assertEqual(run_ai("search", "demo")[0], 0)
        os.environ["REGISTRY_URL"] = os.path.join(self.tmp, "gone", "registry.json")
        code, _, err = run_ai("search", "demo")
        self.assertEqual(code, 1)
        os.environ["REGISTRY_URL"] = self.url
        os.rename(self.url, self.url + ".bak")
        code, out, err = run_ai("search", "demo")
        self.assertEqual(code, 0)
        self.assertIn("using cached registry", err)
        self.assertIn("demo", out)

    def test_caches_are_separate_per_registry_url(self):
        run_ai("search", "demo")
        other = os.path.join(self.tmp, "other-registry.json")
        write(other, json.dumps({"version": 2, "components": []}))
        os.environ["REGISTRY_URL"] = other
        self.assertIn("no matches", run_ai("search", "demo")[1])
        os.environ["REGISTRY_URL"] = self.url
        self.assertIn("demo", run_ai("search", "demo")[1])
        self.assertNotEqual(ai.cache_path(self.url), ai.cache_path(other))

    def test_offline_requires_a_cache(self):
        code, _, err = run_ai("search", "demo", "--offline")
        self.assertEqual(code, 1)
        self.assertIn("no cached registry", err)
        run_ai("search", "demo")
        self.assertEqual(run_ai("search", "demo", "--offline")[0], 0)

    def test_invalid_registry_reports_url(self):
        write(self.url, "{\"components\": [{\"name\": \"x\"}]}")
        code, _, err = run_ai("search", "x")
        self.assertEqual(code, 1)
        self.assertIn("is invalid", err)
        self.assertIn("missing field", err)

    def test_config_sets_registry_url(self):
        code, out, _ = run_ai("config", "registry_url", self.url)
        self.assertEqual(code, 0)
        os.environ.pop("REGISTRY_URL")
        self.assertIn(self.url, run_ai("config")[1])
        self.assertEqual(run_ai("config", "bogus", "x")[0], 1)

    def test_default_registry_prefers_checkout_then_public_url(self):
        with mock.patch.object(ai, "HERE", self.tmp):
            self.assertEqual(ai.default_registry(), ai.PUBLIC_REGISTRY_URL)
            write(os.path.join(self.tmp, "registry.json"), "{}")
            self.assertEqual(ai.default_registry(), os.path.join(self.tmp, "registry.json"))
        self.assertTrue(ai.PUBLIC_REGISTRY_URL.startswith("https://raw.githubusercontent.com/MUdevelops/AIRegistry/"))


class TestParseRegistry(unittest.TestCase):
    def manifest(self, **kw):
        m = dict(name="demo", version="1.0.0", description="d", category="tool", runtime="python",
                 license="MIT", tags=["x"], files=["README.md"], source="registry/demo/versions/1.0.0")
        m.update(kw)
        return m

    def parse(self, components):
        return ai.parse_registry(json.dumps({"components": components}))

    def test_accepts_versioned_entries(self):
        reg = self.parse([{"name": "demo", "latest_version": "1.0.0", "versions": [self.manifest()]}])
        self.assertEqual(reg["demo"]["latest"], "1.0.0")

    def test_accepts_legacy_flat_entries(self):
        reg = self.parse([self.manifest(source="registry/demo")])
        self.assertEqual(ai.latest(reg["demo"])["version"], "1.0.0")

    def test_latest_defaults_to_highest_version(self):
        reg = self.parse([{"name": "demo", "versions": [self.manifest(version="1.0.0"), self.manifest(version="1.2.0"), self.manifest(version="1.10.0")]}])
        self.assertEqual(reg["demo"]["latest"], "1.10.0")

    def test_rejects_bad_registries(self):
        bad = [
            [{"name": "demo", "latest_version": "2.0.0", "versions": [self.manifest()]}],
            [{"name": "demo", "versions": [self.manifest(), self.manifest()]}],
            [{"name": "demo", "versions": []}],
            [{"name": "demo", "versions": [self.manifest(name="other")]}],
            [self.manifest(), self.manifest()],
            [self.manifest(files=["../evil.py"])],
            [self.manifest(files=["run.ps1"])],
            [self.manifest(source="/abs")],
            [self.manifest(sha256={"nope.py": "0" * 64})],
            [self.manifest(version="1.0")],
            [self.manifest(name="Bad_Name")],
            ["not an object"],
        ]
        for components in bad:
            with self.assertRaises(ai.Err, msg=components):
                self.parse(components)

    def test_rejects_non_registry_json(self):
        for text in ("not json", "[]", "{}"):
            with self.assertRaises(ai.Err):
                ai.parse_registry(text)

    def test_vkey_orders_prereleases_below_releases(self):
        order = sorted(["1.0.0", "1.0.0-beta.1", "0.9.9", "1.10.0", "1.2.0"], key=ai.vkey)
        self.assertEqual(order, ["0.9.9", "1.0.0-beta.1", "1.0.0", "1.2.0", "1.10.0"])

    def test_parse_ref(self):
        self.assertEqual(ai.parse_ref("rag"), ("rag", None))
        self.assertEqual(ai.parse_ref("rag@1.2.3"), ("rag", "1.2.3"))
        for bad in ("", "Rag", "rag@1", "rag@@1.0.0", "../x"):
            with self.assertRaises(ai.Err):
                ai.parse_ref(bad)

    def test_safe_rel(self):
        self.assertEqual(ai.safe_rel("src/a.py"), ["src", "a.py"])
        for bad in ("", "/a", "a/../b", "a\\b", "C:/x", "a//b", "./a", "a\0b"):
            with self.assertRaises(ai.Err):
                ai.safe_rel(bad)


if __name__ == "__main__":
    unittest.main()
