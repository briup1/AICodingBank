"""Check the documentation scaffold, not live Agent scheduling or permissions."""
import re
import subprocess
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ROLE_PATHS = (
    'roles/project-manager/ROLE.md',
    'roles/engineering/architect/ROLE.md',
    'roles/engineering/developer/ROLE.md',
    'roles/engineering/tester/ROLE.md',
    'roles/media/editor/ROLE.md',
    'roles/shared/researcher/ROLE.md',
    'roles/engineering/ui/ROLE.md',
    'roles/engineering/frontend/ROLE.md',
)


class RoleWorkbenchStructureTests(unittest.TestCase):
    def test_roles_have_explicit_enablement(self):
        self.assertEqual(
            {str(p.relative_to(ROOT)) for p in (ROOT / 'roles').rglob('ROLE.md')},
            set(ROLE_PATHS),
        )
        for relative in ROLE_PATHS:
            text = (ROOT / relative).read_text(encoding='utf-8')
            for heading in ('角色定位', '边界与协作', '工作方法'):
                self.assertIn(f'## {heading}', text, relative)
            self.assertIn('首次承担岗位时必读[共用协作约定]', text, relative)
        pm = (ROOT / ROLE_PATHS[0]).read_text(encoding='utf-8')
        self.assertIn('status: active\n', pm)
        self.assertIn('enabled: true\n', pm)
        self.assertIn('## 开工开场', pm)
        self.assertIn('项目经理', pm)
        researcher = (ROOT / 'roles/shared/researcher/ROLE.md').read_text(encoding='utf-8')
        self.assertIn('status: active\n', researcher)
        self.assertIn('enabled: true\n', researcher)
        self.assertIn('enabled_scope:', researcher)
        active = {'roles/shared/researcher/ROLE.md', 'roles/engineering/ui/ROLE.md',
                  'roles/engineering/frontend/ROLE.md', 'roles/engineering/tester/ROLE.md'}
        for relative in active:
            text = (ROOT / relative).read_text(encoding='utf-8')
            self.assertIn('enabled: true\n', text)
            self.assertIn('enabled_scope:', text)
        for relative in (p for p in ROLE_PATHS[1:] if p not in active):
            text = (ROOT / relative).read_text(encoding='utf-8')
            self.assertIn('status: draft\n', text, relative)
            self.assertIn('enabled: false\n', text, relative)
        for directory in ('roles', 'personal', 'tools/execution-profiles'):
            self.assertEqual(list((ROOT / directory).rglob('SKILL.md')), [])

    def test_categories_and_supporting_directories_exist(self):
        paths = ['roles', 'personal', 'tools', '.local']
        paths += [f'tools/skills/{name}' for name in
                  ('engineering', 'media', 'shared', 'workbench')]
        paths += [f'tools/{name}' for name in
                  ('execution-profiles', 'integrations', 'scripts', 'templates')]
        for path in paths:
            self.assertTrue((ROOT / path / 'README.md').is_file(), path)

    def test_new_documentation_links_resolve(self):
        paths = [ROOT / name for name in ('README.md', 'WORKBENCH.md', 'EXTENDING.md')]
        for directory in ('roles', 'personal', '.local'):
            paths += list((ROOT / directory).rglob('*.md'))
        paths += list((ROOT / 'tools').glob('README.md'))
        paths += list((ROOT / 'tools').glob('*/README.md'))
        paths += list((ROOT / 'tools/skills').glob('*/README.md'))
        paths += [ROOT / 'best_practices' / name for name in ('README.md', 'STANDARD.md', 'TEMPLATE.md')]
        paths += list((ROOT / 'best_practices').glob('20*/README.md'))
        paths += [ROOT / 'docs/wl-ai-skills/specs/2026-10-18-role-workbench-structure-design.md']
        for path in paths:
            text = path.read_text(encoding='utf-8')
            for href in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
                parts = urlsplit(href)
                if parts.scheme or parts.netloc or not parts.path:
                    continue
                self.assertTrue((path.parent / unquote(parts.path)).exists(), (path, href))

    def test_private_files_and_runtime_data_are_ignored(self):
        private_paths = (
            'personal/profile.local.md',
            '.local/sessions/probe.json',
            '.local/records/probe.md',
        )
        for path in private_paths:
            result = subprocess.run(['git', 'check-ignore', '-q', path], cwd=ROOT)
            self.assertEqual(result.returncode, 0, path)
        result = subprocess.run(['git', 'check-ignore', '-q', '.local/README.md'], cwd=ROOT)
        self.assertEqual(result.returncode, 1)


if __name__ == '__main__':
    unittest.main()
