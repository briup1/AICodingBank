"""Check the documentation scaffold, not live Agent scheduling or permissions."""
import re
import subprocess
import tempfile
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
            self.assertNotIn('首次承担岗位时必读', text, relative)
            if relative != ROLE_PATHS[0]:
                self.assertIn('## 交付与停止', text, relative)
                for guard in ('按派单范围执行', '返回PM', '不再次委派', '未验证不能报为通过',
                              '工具可用不等于已获操作授权'):
                    self.assertIn(guard, text, relative)
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

    def test_roles_have_distinct_work_chains_and_handoffs(self):
        expectations = {
            'roles/engineering/architect/ROLE.md': ('比较必要选项', '事实、假设和待确认决定', '实现者能据此行动'),
            'roles/engineering/developer/ROLE.md': ('最小改法', '先复现', '没有专用Skill不等于不能开工'),
            'roles/engineering/frontend/ROLE.md': ('用户操作', '加载、空态、失败和恢复', '构建通过不等于交互正确'),
            'roles/engineering/tester/ROLE.md': ('通过、失败、阻塞或未覆盖', '不从当前实现反推正确答案', '不为通过修改预期'),
            'roles/engineering/ui/ROLE.md': ('用户操作 → 页面变化', '前端能落实、测试能判断', '设计自查不是独立审阅'),
            'roles/media/editor/ROLE.md': ('读者', '核心主张和结构', '成稿不等于获准发布'),
            'roles/shared/researcher/ROLE.md': ('实际阅读关键原文', '区分事实、推断与建议', '不把未命中当作不存在'),
        }
        for relative, phrases in expectations.items():
            text = (ROOT / relative).read_text(encoding='utf-8')
            steps = re.findall(r'^\d+\. ', text, re.M)
            self.assertGreaterEqual(len(steps), 4, relative)
            for phrase in phrases:
                self.assertIn(phrase, text, relative)
        roles = (ROOT / 'roles/README.md').read_text(encoding='utf-8')
        self.assertIn('不是执行者接单前必须通读的前言', roles)
        self.assertIn('没有专用Skill不等于不能执行', roles)

    def test_pm_can_execute_without_delegation(self):
        pm = (ROOT / ROLE_PATHS[0]).read_text(encoding='utf-8')
        for rule in ('你自己完成', '不要委派', '不启动其他 Agent', '不把自己验证称为独立验证'):
            self.assertIn(rule, pm)
        self.assertIn('自己调查、设计、实现和验证', pm)
        for step in ('明确目标', '查清现状', '拆出工作包', '选择执行方式', '持续推进', '核验交付'):
            self.assertIn(step, pm)
        self.assertNotIn('首次承担岗位时必读', pm)
        self.assertNotRegex(pm, r'\[[^\]]+\]\([^)]+\.md[^)]*\)')
        self.assertIn('## 委派场景命令', pm)
        self.assertIn('herdr agent start', pm)

    def test_pm_discovers_roles_outside_workbench(self):
        pm = (ROOT / ROLE_PATHS[0]).read_text(encoding='utf-8')
        self.assertNotIn('候选岗位包括', pm)
        self.assertIn('文件数量不等于可委派数量', pm)
        command = re.search(r'```bash\n(WORKBENCH_ROOT=.*?)\n```', pm, re.S)
        self.assertIsNotNone(command)
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(['bash', '-c', command.group(1)], cwd=directory,
                                    capture_output=True, text=True, check=True)
        expected = []
        for manual in (ROOT / 'roles').rglob('ROLE.md'):
            expected.extend(f'{manual}:{line}' for line in manual.read_text(encoding='utf-8').splitlines()
                            if re.match(r'^(name|status|enabled|enabled_scope):', line))
        self.assertCountEqual(result.stdout.splitlines(), expected)
        self.assertEqual(result.stderr, '')

    def test_delegation_contract_and_temporary_roles(self):
        strategy = (ROOT / 'tools/skills/workbench/wl-herdrs/SKILL.md').read_text(encoding='utf-8')
        pm = (ROOT / ROLE_PATHS[0]).read_text(encoding='utf-8')
        for rule in ('三段式派单', '你是〔角色〕', '你的任务是', '成功标准是',
                     '可按需读取直接依赖', '未验证不能报为通过', '不再次委派',
                     '没有匹配岗位时', '不要求先有 ROLE.md'):
            self.assertIn(rule, pm)
        self.assertIn('ROLE.md#三段式派单', strategy)
        self.assertNotIn('> 你是〔角色〕', strategy)
        self.assertNotIn('### 三段式派单接口', strategy)
        roles = (ROOT / 'roles/README.md').read_text(encoding='utf-8')
        for rule in ('临时职责与交付', '不要求先有 ROLE.md', '不自动写入岗位名册',
                     '不能改称临时角色来绕过', '角色称谓不创造专业能力或权限'):
            self.assertIn(rule, roles)
        extending = (ROOT / 'EXTENDING.md').read_text(encoding='utf-8')
        self.assertIn('roles/README.md#临时职责与交付', extending)

    def test_pm_inline_commands_keep_required_guards(self):
        pm = (ROOT / ROLE_PATHS[0]).read_text(encoding='utf-8')
        for rule in ('HERDR_ENV', '--no-focus', '--kind pi', '-- --thinking high',
                     '.result.root_pane.pane_id', '实际启动 `argv`', '不重复发送prompt',
                     'blocked', 'unknown', '未运行真实启动验证', '只有用户明确要求才关闭',
                     '同一上下文已完整加载且未变化', '更高优先级要求仍须遵守',
                     '不另建速查文件', '其他操作查当前可用清单中 `herdr` Skill 的原始文件'):
            self.assertIn(rule, pm)
        self.assertNotIn('herdr pane split --', pm)
        self.assertNotIn('herdr tab close', pm)
        removed = ROOT / 'tools/skills/workbench/wl-herdrs/references/pm-quick-reference.md'
        self.assertFalse(removed.exists())
        for relative in (ROLE_PATHS[0], 'tools/skills/workbench/wl-herdrs/SKILL.md',
                         'tools/execution-profiles/delegation.md'):
            self.assertNotIn(removed.name, (ROOT / relative).read_text(encoding='utf-8'))

    def test_reasoning_check_stays_out_of_worker_prompt(self):
        config = (ROOT / 'tools/execution-profiles/delegation.md').read_text(encoding='utf-8')
        self.assertIn('high，启动时显式指定，由项目经理核对启动参数', config)
        self.assertIn('派单正文不要求执行者检查 `PI_REASONING_LEVEL`、确认或回报 high', config)
        self.assertIn('执行者收到具体任务后直接开工', config)
        pm = (ROOT / ROLE_PATHS[0]).read_text(encoding='utf-8')
        self.assertIn('不塞入派单或要求执行者回执', pm)
        self.assertIn('-- --thinking high', pm)
        strategy = (ROOT / 'tools/skills/workbench/wl-herdrs/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('执行者不再确认思考级别', strategy)

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
        paths += [ROOT / 'tools/execution-profiles/delegation.md']
        paths += list((ROOT / 'tools/skills/workbench/wl-herdrs').rglob('*.md'))
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
