import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
NAME = "visual-artifact-workbench"
SPEC = importlib.util.spec_from_file_location("visual_artifact_installer", ROOT / "install.py")
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


def entry():
    config = yaml.safe_load((ROOT / "skills.yaml").read_text(encoding="utf-8"))
    matches = [item for item in config["self"] if item["name"] == NAME]
    if len(matches) != 1:
        raise AssertionError("Expected exactly one skill registration")
    return matches[0]


class VisualArtifactWorkbenchTests(unittest.TestCase):
    def test_registration_resolves_to_the_canonical_skill(self):
        item = entry()
        self.assertEqual(item["path"], f"skills/{NAME}")
        skill = ROOT / item["path"] / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        metadata = yaml.safe_load(text.split("---", 2)[1])
        self.assertEqual(metadata["name"], NAME)
        self.assertTrue(metadata["description"])
        for field in ("capability", "boundary", "tags"):
            self.assertTrue(item[field])
        lock = json.loads((ROOT / "skills-lock.json").read_text(encoding="utf-8"))
        self.assertNotIn(NAME, lock["skills"])

    def test_skill_and_entry_references_resolve(self):
        skill_root = ROOT / entry()["path"]
        for doc in skill_root.rglob("*.md"):
            for target in re.findall(r"\[[^]]+\]\(([^)]+\.md)\)", doc.read_text(encoding="utf-8")):
                self.assertTrue((doc.parent / target).resolve().is_file(), (doc, target))
        workbench = (ROOT / "WORKBENCH.md").read_text(encoding="utf-8")
        targets = re.findall(r"\[[^]]+\]\(([^)]+\.md)\)", workbench)
        self.assertIn(f"skills/{NAME}/SKILL.md", targets)
        for target in targets:
            self.assertTrue((ROOT / target).is_file(), target)
        ignored = subprocess.run(
            ["git", "check-ignore", "WORKBENCH.local.md"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(ignored.returncode, 0)

    def test_real_installer_keeps_unverified_skill_uninstalled(self):
        # Execute install.py in an isolated control-plane fixture: no network or user targets.
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            (fixture / "install.py").write_bytes((ROOT / "install.py").read_bytes())
            (fixture / "skills").symlink_to(ROOT / "skills", target_is_directory=True)
            target = fixture / "agent-skills"
            target.mkdir()
            (target / NAME).symlink_to(ROOT / entry()["path"], target_is_directory=True)
            candidate = dict(entry(), verified="")
            (fixture / "skills.yaml").write_text(yaml.safe_dump({
                "targets": [str(target)], "self": [candidate],
                "third_party": {"lock": "skills-lock.json"},
            }, allow_unicode=True), encoding="utf-8")
            (fixture / "skills-lock.json").write_text(
                json.dumps({"version": 1, "skills": {}}), encoding="utf-8"
            )
            for _ in range(2):
                completed = subprocess.run(
                    [sys.executable, "install.py"], cwd=fixture,
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
                self.assertFalse(os.path.lexists(target / NAME))
                catalog = (fixture / "CATALOG.md").read_text(encoding="utf-8")
                self.assertIn(NAME, catalog)
                self.assertIn("待验证（未安装）", catalog)

    def test_catalog_without_optional_metadata_has_no_trailing_whitespace(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog = Path(tmp) / "CATALOG.md"
            installer.write_catalog([{"name": "legacy-entry", "origin": "第三方"}], catalog)
            text = catalog.read_text(encoding="utf-8")
            self.assertIn("legacy-entry", text)
            self.assertIn("待验证（未安装）", text)
            self.assertTrue(all(line == line.rstrip() for line in text.splitlines()))

    def test_repository_catalog_matches_installer_output(self):
        config = yaml.safe_load((ROOT / "skills.yaml").read_text(encoding="utf-8"))
        lock = json.loads((ROOT / config["third_party"]["lock"]).read_text(encoding="utf-8"))
        entries = [dict(item, origin="自研") for item in config["self"]]
        for name, meta in lock["skills"].items():
            ref = meta.get("ref")
            origin = f"第三方·{meta['source']}" + (f"@{ref}" if ref else "")
            entries.append(dict(meta, name=name, origin=origin))
        with tempfile.TemporaryDirectory() as tmp:
            generated = Path(tmp) / "CATALOG.md"
            installer.write_catalog(entries, generated)
            self.assertEqual(generated.read_bytes(), (ROOT / "CATALOG.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
