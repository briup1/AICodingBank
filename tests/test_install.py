import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("skill_installer", REPO_ROOT / "install.py")
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class LocalDisableTests(unittest.TestCase):
    def test_load_disabled_missing_file_returns_empty_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(installer.load_disabled(Path(tmp) / "missing.yaml"), set())

    def test_load_disabled_rejects_invalid_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "skills.local.yaml"
            path.write_text("disabled: agent-dag-reporting\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "disabled"):
                installer.load_disabled(path)

    def test_unlink_skill_only_removes_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target"
            source = root / "source"
            target.mkdir()
            source.mkdir()
            link = target / "linked"
            link.symlink_to(source, target_is_directory=True)
            real = target / "real"
            real.mkdir()
            report = []

            installer.unlink_skill([str(target)], "linked", report)
            installer.unlink_skill([str(target)], "real", report)

            self.assertFalse(link.exists())
            self.assertTrue(real.is_dir())
            self.assertTrue(any("存在真实目录" in line for line in report))

    def test_end_to_end_local_disable_then_enable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "skills" / "demo"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: demo\n---\n", encoding="utf-8")
            target = root / "loaded"
            target.mkdir()
            (target / "demo").symlink_to(skill, target_is_directory=True)
            (root / "skills.yaml").write_text(
                yaml.safe_dump(
                    {
                        "targets": [str(target)],
                        "self": [
                            {
                                "name": "demo",
                                "path": "skills/demo",
                                "capability": "测试本机禁用",
                                "boundary": "仅测试",
                                "tags": ["测试"],
                                "verified": "2026-08-24",
                            }
                        ],
                        "third_party": {"lock": "skills-lock.json"},
                    },
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            (root / "skills-lock.json").write_text(
                json.dumps({"version": 1, "skills": {}}), encoding="utf-8"
            )
            (root / "skills.local.yaml").write_text(
                "disabled:\n  - demo\n", encoding="utf-8"
            )

            old_root, old_vendor = installer.ROOT, installer.VENDOR
            installer.ROOT, installer.VENDOR = str(root), str(root / "vendor")
            try:
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    with self.assertRaises(SystemExit) as exit_info:
                        installer.main()
                self.assertEqual(exit_info.exception.code, 0)
                self.assertFalse(os.path.lexists(target / "demo"))
                self.assertIn("本机禁用未安装: demo", output.getvalue())
                self.assertIn("**demo**", (root / "CATALOG.md").read_text(encoding="utf-8"))

                (root / "skills.local.yaml").unlink()
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(SystemExit) as exit_info:
                        installer.main()
                self.assertEqual(exit_info.exception.code, 0)
                self.assertTrue((target / "demo").is_symlink())
                self.assertEqual((target / "demo").resolve(), skill.resolve())

                config = yaml.safe_load((root / "skills.yaml").read_text(encoding="utf-8"))
                config["self"][0]["verified"] = ""
                (root / "skills.yaml").write_text(
                    yaml.safe_dump(config, allow_unicode=True, sort_keys=False),
                    encoding="utf-8",
                )
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(SystemExit) as exit_info:
                        installer.main()
                self.assertEqual(exit_info.exception.code, 0)
                self.assertFalse(os.path.lexists(target / "demo"))
            finally:
                installer.ROOT, installer.VENDOR = old_root, old_vendor


class ThirdPartyIntegrityTests(unittest.TestCase):
    def test_verified_skill_with_matching_hash_is_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "loaded"
            target.mkdir()
            vendor = root / "vendor" / installer.vendor_dir_name("owner/repo", "v1")
            skill = vendor / "skills" / "demo"
            skill.mkdir(parents=True)
            skill_file = skill / "SKILL.md"
            skill_file.write_text("---\nname: demo\n---\n", encoding="utf-8")
            digest = installer.hash_file(skill_file)

            (root / "skills.yaml").write_text(
                yaml.safe_dump(
                    {
                        "targets": [str(target)],
                        "self": [],
                        "third_party": {"lock": "skills-lock.json"},
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            (root / "skills-lock.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "skills": {
                            "demo": {
                                "source": "owner/repo",
                                "sourceType": "github",
                                "ref": "v1",
                                "skillPath": "skills/demo/SKILL.md",
                                "computedHash": digest,
                                "verified": "2026-09-03",
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            old_root, old_vendor = installer.ROOT, installer.VENDOR
            installer.ROOT, installer.VENDOR = str(root), str(root / "vendor")
            try:
                with mock.patch.object(installer, "sync_github_repo", return_value=True):
                    with contextlib.redirect_stdout(io.StringIO()):
                        with self.assertRaises(SystemExit) as exit_info:
                            installer.main()
                self.assertEqual(exit_info.exception.code, 0)
                self.assertEqual((target / "demo").resolve(), skill.resolve())

                lock = json.loads((root / "skills-lock.json").read_text(encoding="utf-8"))
                lock["skills"]["demo"].pop("ref")
                lock["skills"]["demo"]["computedHash"] = "0" * 64
                (root / "skills-lock.json").write_text(json.dumps(lock), encoding="utf-8")
                (target / "demo").unlink()
                unpinned_vendor = root / "vendor" / installer.vendor_dir_name("owner/repo")
                unpinned_skill = unpinned_vendor / "skills" / "demo"
                unpinned_skill.mkdir(parents=True)
                (unpinned_skill / "SKILL.md").write_text("floating upstream\n", encoding="utf-8")
                with mock.patch.object(installer, "sync_github_repo", return_value=True):
                    with contextlib.redirect_stdout(io.StringIO()):
                        with self.assertRaises(SystemExit) as exit_info:
                            installer.main()
                self.assertEqual(exit_info.exception.code, 0)
                self.assertEqual((target / "demo").resolve(), unpinned_skill.resolve())
            finally:
                installer.ROOT, installer.VENDOR = old_root, old_vendor

    def test_hash_mismatch_removes_existing_link_and_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "loaded"
            target.mkdir()
            vendor = root / "vendor" / installer.vendor_dir_name("owner/repo", "v1")
            skill = vendor / "skills" / "demo"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("changed upstream\n", encoding="utf-8")
            (target / "demo").symlink_to(skill, target_is_directory=True)

            (root / "skills.yaml").write_text(
                yaml.safe_dump(
                    {
                        "targets": [str(target)],
                        "self": [],
                        "third_party": {"lock": "skills-lock.json"},
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            (root / "skills-lock.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "skills": {
                            "demo": {
                                "source": "owner/repo",
                                "sourceType": "github",
                                "ref": "v1",
                                "skillPath": "skills/demo/SKILL.md",
                                "computedHash": "0" * 64,
                                "verified": "2026-09-03",
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            old_root, old_vendor = installer.ROOT, installer.VENDOR
            installer.ROOT, installer.VENDOR = str(root), str(root / "vendor")
            try:
                with mock.patch.object(installer, "sync_github_repo", return_value=False):
                    with contextlib.redirect_stdout(io.StringIO()) as output:
                        with self.assertRaises(SystemExit) as exit_info:
                            installer.main()
                self.assertEqual(exit_info.exception.code, 1)
                self.assertFalse(os.path.lexists(target / "demo"))
                self.assertIn("同步失败", output.getvalue())
                self.assertIn("哈希不匹配", output.getvalue())
            finally:
                installer.ROOT, installer.VENDOR = old_root, old_vendor


class ThirdPartyRefTests(unittest.TestCase):
    def test_vendor_dir_name_distinguishes_pinned_ref(self):
        self.assertEqual(
            installer.vendor_dir_name("herdrdev/herdr", "v0.8.2"),
            "herdrdev__herdr__ref__v0.8.2",
        )
        self.assertEqual(
            installer.vendor_dir_name("herdrdev/herdr", "release/v0.8.2"),
            "herdrdev__herdr__ref__release__v0.8.2",
        )
        self.assertEqual(
            installer.vendor_dir_name("herdrdev/herdr"),
            "herdrdev__herdr",
        )

    def test_sync_github_repo_clones_requested_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            vendor_dir = str(Path(tmp) / "herdrdev__herdr__ref__v0.8.2")
            completed = mock.Mock(returncode=0)
            with mock.patch.object(installer.subprocess, "run", return_value=completed) as run:
                self.assertTrue(
                    installer.sync_github_repo(
                        "herdrdev/herdr", "v0.8.2", vendor_dir
                    )
                )

            run.assert_called_once_with(
                [
                    "git",
                    "clone",
                    "-q",
                    "--depth",
                    "1",
                    "--branch",
                    "v0.8.2",
                    "https://github.com/herdrdev/herdr.git",
                    vendor_dir,
                ]
            )

    def test_sync_github_repo_refreshes_existing_pinned_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            vendor_dir = Path(tmp) / "herdrdev__herdr__ref__v0.8.2"
            (vendor_dir / ".git").mkdir(parents=True)
            completed = mock.Mock(returncode=0)
            with mock.patch.object(
                installer.subprocess, "run", side_effect=[completed, completed]
            ) as run:
                self.assertTrue(
                    installer.sync_github_repo(
                        "herdrdev/herdr", "v0.8.2", str(vendor_dir)
                    )
                )

            self.assertEqual(
                run.call_args_list,
                [
                    mock.call(
                        [
                            "git",
                            "-C",
                            str(vendor_dir),
                            "fetch",
                            "-q",
                            "--depth",
                            "1",
                            "origin",
                            "v0.8.2",
                        ]
                    ),
                    mock.call(
                        [
                            "git",
                            "-C",
                            str(vendor_dir),
                            "checkout",
                            "-q",
                            "--detach",
                            "FETCH_HEAD",
                        ]
                    ),
                ],
            )

    def test_sync_github_repo_keeps_default_branch_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            vendor_dir = str(Path(tmp) / "owner__repo")
            completed = mock.Mock(returncode=0)
            with mock.patch.object(installer.subprocess, "run", return_value=completed) as run:
                self.assertTrue(installer.sync_github_repo("owner/repo", None, vendor_dir))

            run.assert_called_once_with(
                [
                    "git",
                    "clone",
                    "-q",
                    "--depth",
                    "1",
                    "https://github.com/owner/repo.git",
                    vendor_dir,
                ]
            )


if __name__ == "__main__":
    unittest.main()
