import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

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

    def test_unlink_disabled_only_removes_symlink(self):
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

            installer.unlink_disabled([str(target)], "linked", report)
            installer.unlink_disabled([str(target)], "real", report)

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
            finally:
                installer.ROOT, installer.VENDOR = old_root, old_vendor


if __name__ == "__main__":
    unittest.main()
