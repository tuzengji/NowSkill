from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import install
import sync


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="nowskill-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.dest = self.base / "agent" / "skills"
        self.legacy = self.base / "legacy" / "skills"
        self.codex = self.base / "codex"
        self.manifest_path = self.repo / "skills.lock.json"
        patch = mock.patch.object(install, "REPO_ROOT", self.repo)
        patch.start()
        self.addCleanup(patch.stop)
        environment = mock.patch.dict(os.environ, {"CODEX_HOME": str(self.codex)})
        environment.start()
        self.addCleanup(environment.stop)
        self.manifest = {"schema_version": 1, "skills": []}
        self.save()

    def save(self):
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2) + "\n")

    def skill(self, path, content="version one", disabled=False):
        path.mkdir(parents=True, exist_ok=True)
        marker = "SKILL.md.disabled" if disabled else "SKILL.md"
        (path / marker).write_text(f"---\nname: {path.name}\ndescription: Test skill\n---\n{content}\n")
        return path

    def owned(self, name, content="version one", disabled=False):
        source = self.skill(self.repo / "owned" / name, content, disabled)
        self.manifest["skills"].append({
            "name": name, "ownership": "owned", "enabled": not disabled,
            "source": {"type": "bundled", "path": f"owned/{name}"},
        })
        self.save()
        return source

    def execute(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            result = sync.sync(self.manifest_path, self.dest, [self.legacy], **kwargs)
        self.assertEqual(result, 0)
        return output.getvalue()

    def test_reconcile_preserves_system_removes_extras_duplicates_and_nested_skills(self):
        self.owned("wanted", "upstream")
        self.skill(self.dest / "wanted", "local edits")
        self.skill(self.dest / "extra")
        self.skill(self.legacy / "wanted", "old duplicate")
        self.skill(self.legacy / "collection" / "extra-nested")
        self.skill(self.dest / ".system" / "built-in")
        (self.dest / "notes.txt").write_text("unrelated")
        output = self.execute()
        self.assertIn("upstream", (self.dest / "wanted" / "SKILL.md").read_text())
        self.assertFalse((self.dest / "extra").exists())
        self.assertFalse((self.legacy / "wanted").exists())
        self.assertFalse((self.legacy / "collection" / "extra-nested").exists())
        self.assertTrue((self.dest / ".system" / "built-in" / "SKILL.md").exists())
        self.assertEqual((self.dest / "notes.txt").read_text(), "unrelated")
        self.assertIn("3 removed", output)
        backups = list(self.base.glob("*/skill-backups/**/SKILL.md"))
        self.assertEqual(len(backups), 4)
        self.assertTrue(any("local edits" in path.read_text() for path in backups))

    def test_repeat_sync_is_idempotent(self):
        self.owned("wanted")
        self.execute()
        before = (self.dest / "wanted" / "SKILL.md").stat().st_mtime_ns
        self.assertIn("0 installed/updated, 0 removed, 1 unchanged", self.execute())
        self.assertEqual(before, (self.dest / "wanted" / "SKILL.md").stat().st_mtime_ns)
        self.assertFalse((self.dest.parent / "skill-backups").exists())

    def test_dry_run_leaves_skills_and_manifest_unchanged(self):
        self.owned("wanted")
        self.skill(self.dest / "extra")
        before = self.manifest_path.read_bytes()
        self.assertIn("(planned)", self.execute(dry_run=True))
        self.assertFalse((self.dest / "wanted").exists())
        self.assertTrue((self.dest / "extra").exists())
        self.assertEqual(before, self.manifest_path.read_bytes())
        self.assertFalse((self.dest.parent / "skill-backups").exists())

    def test_stage_failure_leaves_existing_installations_untouched(self):
        self.owned("wanted", "upstream")
        self.owned("broken")
        (self.repo / "owned" / "broken" / "SKILL.md").unlink()
        self.skill(self.dest / "wanted", "original")
        self.skill(self.dest / "extra")
        with self.assertRaisesRegex(RuntimeError, "does not contain"):
            self.execute()
        self.assertIn("original", (self.dest / "wanted" / "SKILL.md").read_text())
        self.assertTrue((self.dest / "extra").exists())
        self.assertFalse((self.dest.parent / "skill-backups").exists())

    def test_upstream_network_failure_does_not_prune(self):
        self.owned("wanted")
        self.manifest["skills"][0]["source"] = {"type": "github", "repository": "https://github.com/test/repo.git", "ref": "0" * 40, "path": "."}
        self.save()
        self.skill(self.dest / "extra")
        with mock.patch.object(sync, "latest_revision", side_effect=RuntimeError("offline")):
            with self.assertRaisesRegex(RuntimeError, "offline"):
                self.execute()
        self.assertTrue((self.dest / "extra").exists())

    def test_install_failure_rolls_back_previously_updated_skills(self):
        self.owned("first", "updated")
        self.owned("second")
        self.skill(self.dest / "first", "original")
        self.skill(self.dest / "extra")
        real_move = shutil.move

        def fail_second(source, target, *args, **kwargs):
            if Path(target) == self.dest / "second":
                raise OSError("simulated install failure")
            return real_move(source, target, *args, **kwargs)

        with mock.patch.object(shutil, "move", side_effect=fail_second):
            with self.assertRaisesRegex(OSError, "simulated"):
                self.execute()
        self.assertIn("original", (self.dest / "first" / "SKILL.md").read_text())
        self.assertFalse((self.dest / "second").exists())
        self.assertTrue((self.dest / "extra").exists())

    def test_lock_write_failure_restores_installations_and_removed_skills(self):
        self.owned("wanted")
        self.skill(self.dest / "extra")
        real_replace = os.replace

        def fail_lock(source, target):
            if Path(target) == self.manifest_path:
                raise OSError("lock is read only")
            return real_replace(source, target)

        self.manifest_path.write_text(json.dumps(self.manifest))
        original = self.manifest_path.read_bytes()
        with mock.patch.object(os, "replace", side_effect=fail_lock):
            with self.assertRaisesRegex(OSError, "lock is read only"):
                self.execute()
        self.assertFalse((self.dest / "wanted").exists())
        self.assertTrue((self.dest / "extra").exists())
        self.assertEqual(original, self.manifest_path.read_bytes())

    def test_symlink_removal_does_not_delete_original(self):
        original = self.skill(self.base / "original-source")
        self.dest.mkdir(parents=True)
        (self.dest / "extra-link").symlink_to(original, target_is_directory=True)
        self.execute()
        self.assertFalse((self.dest / "extra-link").is_symlink())
        self.assertTrue((original / "SKILL.md").exists())
        self.assertTrue(next(self.dest.parent.glob("skill-backups/**/extra-link")).is_symlink())

    def test_official_runtime_link_is_preserved(self):
        official = self.skill(self.codex / "plugins" / "cache" / "openai-bundled" / "sample" / "skills" / "sample")
        self.dest.mkdir(parents=True)
        (self.dest / "sample").symlink_to(official, target_is_directory=True)
        self.execute()
        self.assertTrue((self.dest / "sample").is_symlink())

    def test_official_name_collision_aborts_without_removing_extras(self):
        self.owned("sample")
        official = self.skill(self.codex / "skills" / ".system" / "sample")
        self.skill(self.dest / "extra")
        (self.dest / "sample").symlink_to(official, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "official skill"):
            self.execute()
        self.assertTrue((self.dest / "extra").exists())

    def test_staged_external_symlink_is_rejected(self):
        source = self.owned("wanted")
        (source / "outside").symlink_to(self.base)
        with self.assertRaisesRegex(ValueError, "symlink escapes"):
            self.execute()
        self.assertFalse(self.dest.exists())

    def test_nested_official_link_is_not_removed_with_parent(self):
        extra = self.skill(self.dest / "extra")
        official = self.skill(self.codex / "skills" / ".system" / "official")
        (extra / "official").symlink_to(official, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Protected directory nested"):
            self.execute()
        self.assertTrue((extra / "SKILL.md").exists())

    def test_linked_collection_and_broken_links_stop_before_cleanup(self):
        self.skill(self.dest / "extra")
        original = self.skill(self.base / "collection" / "nested")
        linked = self.dest / "collection-link"
        linked.symlink_to(original.parent, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Linked collection"):
            self.execute()
        linked.unlink()
        linked.symlink_to(self.base / "missing")
        with self.assertRaisesRegex(ValueError, "Broken link"):
            self.execute()
        self.assertTrue((self.dest / "extra").exists())

    def test_unrecognized_target_is_not_overwritten(self):
        self.owned("wanted")
        (self.dest / "wanted").mkdir(parents=True)
        (self.dest / "wanted" / "notes.txt").write_text("unrelated")
        with self.assertRaisesRegex(ValueError, "unrecognized"):
            self.execute()
        self.assertEqual((self.dest / "wanted" / "notes.txt").read_text(), "unrelated")

    def test_disabled_skill_is_kept_and_extra_disabled_skill_is_removed(self):
        self.owned("disabled", disabled=True)
        self.skill(self.dest / "extra", disabled=True)
        self.execute()
        self.assertTrue((self.dest / "disabled" / "SKILL.md.disabled").exists())
        self.assertFalse((self.dest / "extra").exists())

    def test_custom_dest_does_not_scan_default_roots(self):
        destination, roots = sync.skill_roots(self.dest, [], self.codex)
        self.assertEqual(destination, self.dest)
        self.assertEqual(roots, [self.dest])

    def test_default_roots_include_codex_home_and_deduplicate_aliases(self):
        with mock.patch.object(Path, "home", return_value=self.base / "fake-home"):
            destination, roots = sync.skill_roots(None, [], self.codex)
        self.assertEqual(roots, [destination, self.codex / "skills"])
        self.dest.mkdir(parents=True)
        alias = self.base / "alias"
        alias.symlink_to(self.dest, target_is_directory=True)
        self.assertEqual(sync.skill_roots(self.dest, [alias], self.codex)[1], [self.dest])

    def test_unsafe_and_overlapping_roots_are_rejected(self):
        for root in [Path("/"), Path.home(), self.repo, self.codex / "skills" / ".system", self.codex / "plugins" / "cache", Path("/etc/codex/skills")]:
            with self.subTest(root=root), self.assertRaises(ValueError):
                sync.skill_roots(root, [], self.codex)
        with self.assertRaisesRegex(ValueError, "overlap"):
            sync.skill_roots(self.dest, [self.dest / "nested"], self.codex)

    def test_backups_cannot_live_in_a_scanned_skill_root(self):
        self.dest.mkdir(parents=True)
        (self.dest.parent / "skill-backups").symlink_to(self.dest, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "outside all skill roots"):
            sync.skill_roots(self.dest, [], self.codex)

    def test_unsafe_names_case_collisions_and_vendored_third_party_are_rejected(self):
        self.owned("wanted")
        for name in ["../escape", ".system", "/tmp/escape"]:
            self.manifest["skills"][0]["name"] = name
            self.save()
            with self.subTest(name=name), self.assertRaises(ValueError):
                install.load_manifest(self.manifest_path)
        self.manifest["skills"][0]["name"] = "wanted"
        self.manifest["skills"][0]["ownership"] = "third-party"
        self.save()
        with self.assertRaisesRegex(ValueError, "links only"):
            install.load_manifest(self.manifest_path)
        self.manifest["skills"][0]["ownership"] = "owned"
        self.manifest["skills"].append({**self.manifest["skills"][0], "name": "WANTED"})
        self.save()
        with self.assertRaisesRegex(ValueError, "unique"):
            install.load_manifest(self.manifest_path)

    def test_well_known_download_records_content_hash(self):
        self.manifest["skills"] = [{"name": "remote", "ownership": "third-party", "source": {
            "type": "well-known", "base_url": "https://skills.example", "package_digest": "historical",
        }}]
        self.save()

        def download(cache, base_url, skill_name, destination):
            self.skill(destination, "latest")

        with mock.patch.object(install.SourceCache, "well_known", download):
            self.execute()
        source = json.loads(self.manifest_path.read_text())["skills"][0]["source"]
        self.assertNotIn("package_digest", source)
        self.assertEqual(source["content_sha256"], sync.tree_digest(self.dest / "remote"))
        self.assertFalse((self.repo / "remote").exists())

    def test_real_git_upstream_update_and_lockfile(self):
        upstream = self.base / "upstream"
        self.skill(upstream / "remote", "initial")
        install.run(["git", "init", "--quiet", "--initial-branch=main"], cwd=upstream)

        def commit():
            install.run(["git", "add", "."], cwd=upstream)
            install.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "--quiet", "-m", "fixture"], cwd=upstream)
            return install.run(["git", "rev-parse", "HEAD"], cwd=upstream)

        initial = commit()
        self.skill(upstream / "remote", "updated")
        latest = commit()
        self.manifest["skills"] = [{"name": "remote", "ownership": "third-party", "source": {
            "type": "github", "repository": str(upstream), "ref": initial, "path": "remote",
        }}]
        self.save()
        self.execute(dry_run=True)
        self.assertEqual(json.loads(self.manifest_path.read_text())["skills"][0]["source"]["ref"], initial)
        self.execute()
        self.assertEqual(json.loads(self.manifest_path.read_text())["skills"][0]["source"]["ref"], latest)
        self.assertIn("updated", (self.dest / "remote" / "SKILL.md").read_text())
        self.assertIn("1 unchanged", self.execute())

    def test_github_url_tracks_resolved_revision(self):
        source = {"repository": "https://github.com/example/skills.git", "path": "skills/a b"}
        sync.updated_source(source, "a" * 40)
        self.assertEqual(source["url"], f"https://github.com/example/skills/tree/{'a' * 40}/skills/a%20b")


if __name__ == "__main__":
    unittest.main()
