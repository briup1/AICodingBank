"""Package checks only; semantic output quality requires real session evidence."""
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'tools/skills/engineering/wl-req-change-tree'


class RequirementChangeTreePackageTests(unittest.TestCase):
    def test_registration_resolves_to_unique_canonical_package(self):
        entries = yaml.safe_load((ROOT / 'skills.yaml').read_text())['self']
        matches = [entry for entry in entries if entry['name'] == 'wl-req-change-tree']
        self.assertEqual(len(matches), 1)
        entry = matches[0]
        self.assertEqual(ROOT / entry['path'], PACKAGE)
        for field in ('capability', 'boundary', 'tags'):
            self.assertTrue(entry[field])
        text = (PACKAGE / 'SKILL.md').read_text()
        frontmatter = yaml.safe_load(text.split('---', 2)[1])
        self.assertEqual(frontmatter['name'], entry['name'])
        self.assertTrue(frontmatter['description'])

    def test_all_local_markdown_references_exist_inside_package(self):
        files = list(PACKAGE.rglob('*.md'))
        self.assertGreaterEqual(len(files), 4)
        for path in files:
            for ref in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' in ref or ref.startswith('#'):
                    continue
                target = (path.parent / ref.split('#')[0]).resolve()
                self.assertTrue(target.is_relative_to(PACKAGE.resolve()), ref)
                self.assertTrue(target.is_file(), f'{path}: {ref}')

    def test_runtime_instructions_do_not_depend_on_private_fixture(self):
        # Private business fixtures and Pi session paths belong to local evidence,
        # not to a reusable invocation or a supposedly required input.
        for relative in ('SKILL.md', 'references/output-template.md', 'references/examples.md'):
            text = (PACKAGE / relative).read_text()
            self.assertNotIn('/Users/', text)
            self.assertNotIn('01a154', text)
            self.assertNotIn('R-20261008-H001.md', text)


if __name__ == '__main__':
    unittest.main()
