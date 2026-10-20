import json
import os
import unittest

from _helpers import TempProject, make_release, run_builder, write


class BuilderCase(TempProject):
    def fails(self, fragment):
        code, _, err = run_builder(self.registry_root)
        self.assertEqual(code, 1, "expected the build to fail")
        self.assertIn(fragment, err)

    def load(self):
        with open(os.path.join(self.registry_root, "registry.json"), encoding="utf-8") as f:
            return json.load(f)


class TestBuild(BuilderCase):
    def test_builds_versioned_index_with_checksums(self):
        make_release(self.registry_root, "demo", "1.0.0")
        make_release(self.registry_root, "demo", "1.1.0", description="Newer description.")
        self.assertEqual(run_builder(self.registry_root)[0], 0)
        idx = self.load()
        self.assertEqual(idx["version"], 2)
        entry = idx["components"][0]
        self.assertEqual(entry["latest_version"], "1.1.0")
        self.assertEqual(entry["description"], "Newer description.")
        self.assertEqual([v["version"] for v in entry["versions"]], ["1.1.0", "1.0.0"])
        self.assertEqual(sorted(entry["versions"][0]["sha256"]), ["README.md", "src/demo.py"])
        self.assertEqual(len(entry["versions"][0]["sha256"]["README.md"]), 64)

    def test_is_deterministic_and_check_detects_staleness(self):
        make_release(self.registry_root, "demo", "1.0.0")
        self.assertEqual(run_builder(self.registry_root)[0], 0)
        self.assertEqual(run_builder(self.registry_root, "--check")[0], 0)
        write(os.path.join(self.registry_root, "registry", "demo", "versions", "1.0.0", "README.md"), "# changed\n")
        code, _, err = run_builder(self.registry_root, "--check")
        self.assertEqual(code, 1)
        self.assertIn("stale", err)

    def test_writes_website_copy_when_website_exists(self):
        make_release(self.registry_root, "demo", "1.0.0")
        os.makedirs(os.path.join(self.registry_root, "website"))
        run_builder(self.registry_root)
        self.assertTrue(os.path.exists(os.path.join(self.registry_root, "website", "registry.json")))

    def test_prerelease_is_never_latest_when_a_stable_release_exists(self):
        make_release(self.registry_root, "demo", "1.0.0")
        make_release(self.registry_root, "demo", "2.0.0-beta.1")
        run_builder(self.registry_root)
        self.assertEqual(self.load()["components"][0]["latest_version"], "1.0.0")

    def test_dependencies_resolve_across_components(self):
        make_release(self.registry_root, "base", "1.0.0")
        make_release(self.registry_root, "app", "1.0.0", dependencies=["base@1.0.0"])
        self.assertEqual(run_builder(self.registry_root)[0], 0)


class TestRejections(BuilderCase):
    def test_missing_release_notes(self):
        make_release(self.registry_root, "demo", "1.0.0", release_notes="")
        self.fails("release_notes")

    def test_name_and_version_must_match_directory(self):
        make_release(self.registry_root, "demo", "1.0.0", name="other")
        self.fails("name must equal its directory")

    def test_version_mismatch(self):
        make_release(self.registry_root, "demo", "1.0.0", version="1.0.1")
        self.fails("version must equal its directory")

    def test_source_must_be_canonical(self):
        make_release(self.registry_root, "demo", "1.0.0", source="registry/demo")
        self.fails("source must be")

    def test_unlisted_file_is_rejected(self):
        d = make_release(self.registry_root, "demo", "1.0.0")
        write(os.path.join(d, "src", "extra.py"), "X = 1\n")
        self.fails("not listed")

    def test_missing_listed_file(self):
        d = make_release(self.registry_root, "demo", "1.0.0")
        os.remove(os.path.join(d, "src", "demo.py"))
        self.fails("missing file")

    def test_readme_and_src_are_required(self):
        make_release(self.registry_root, "demo", "1.0.0", files={"src/demo.py": "X = 1\n"})
        self.fails("README.md")

    def test_src_file_required(self):
        make_release(self.registry_root, "demo", "1.0.0", files={"README.md": "# x\n"})
        self.fails("src/")

    def test_python_syntax_errors_are_caught(self):
        make_release(self.registry_root, "demo", "1.0.0",
                     files={"README.md": "# x\n", "src/demo.py": "```python\nX = 1\n"})
        self.fails("syntax error")

    def test_empty_files_are_rejected(self):
        make_release(self.registry_root, "demo", "1.0.0", files={"README.md": "# x\n", "src/demo.py": "\n"})
        self.fails("empty")

    def test_dependency_format_and_targets(self):
        make_release(self.registry_root, "demo", "1.0.0", dependencies=["other"])
        self.fails("must look like")

    def test_missing_dependency_target(self):
        make_release(self.registry_root, "demo", "1.0.0", dependencies=["other@1.0.0"])
        self.fails("not in the registry")

    def test_self_dependency(self):
        make_release(self.registry_root, "demo", "1.0.0", dependencies=["demo@1.0.0"])
        self.fails("depend on itself")

    def test_stray_entries_next_to_versions(self):
        make_release(self.registry_root, "demo", "1.0.0")
        write(os.path.join(self.registry_root, "registry", "demo", "component.json"), "{}")
        self.fails("unexpected entries")

    def test_flat_layout_is_rejected(self):
        write(os.path.join(self.registry_root, "registry", "flat", "component.json"), "{}")
        self.fails("versions")

    def test_bad_version_directory_name(self):
        make_release(self.registry_root, "demo", "1.0")
        self.fails("MAJOR.MINOR.PATCH")

    def test_invalid_manifest_json(self):
        d = make_release(self.registry_root, "demo", "1.0.0")
        write(os.path.join(d, "component.json"), "{oops")
        self.fails("invalid JSON")

    def test_description_length(self):
        make_release(self.registry_root, "demo", "1.0.0", description="x" * 281)
        self.fails("280")


if __name__ == "__main__":
    unittest.main()
