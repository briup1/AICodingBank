"""Focused migration contracts; never install to the user's Agent directories."""
import json
import re
import unittest
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class WorkbenchMigrationTests(unittest.TestCase):
    def test_registered_skills_have_one_canonical_home_and_keep_verification(self):
        config = yaml.safe_load((ROOT / 'skills.yaml').read_text())
        paths = []
        for entry in config['self']:
            path = ROOT / entry['path']
            self.assertTrue(entry['path'].startswith('tools/skills/'), entry)
            self.assertTrue((path / 'SKILL.md').is_file(), entry)
            self.assertFalse(path.is_symlink(), entry)
            paths.append(path.resolve())
        self.assertEqual(len(paths), len(set(paths)))
        pending = next(e for e in config['self'] if e['name'] == 'wl-auto-delivery')
        self.assertEqual(pending['verified'], '')
        # Historical packages move without being silently promoted/installed.
        self.assertNotIn('software-architect-restructure', [e['name'] for e in config['self']])
        lock = json.loads((ROOT / 'skills-lock.json').read_text())
        self.assertTrue(lock['skills'])

    def test_practice_records_are_dated_and_keep_historical_status(self):
        base = ROOT / 'best_practices'
        records = [p for p in base.iterdir() if p.is_dir() and not p.is_symlink()]
        self.assertGreaterEqual(len(records), 4)
        for record in records:
            self.assertRegex(record.name, r'^\d{4}-\d{2}-\d{2}-.+-.+$')
            date.fromisoformat(record.name[:10])
            metadata = yaml.safe_load((record / 'README.md').read_text().split('---', 2)[1])
            self.assertIn(metadata['status'], ('historical-unverified', 'verified', 'partial', 'superseded'))
            self.assertIn(metadata['date_basis'], ('first-repository-record', 'practice-date', 'recorded-date'))
            self.assertTrue(metadata['source'])
        self.assertTrue((base / 'STANDARD.md').is_file())
        self.assertTrue((base / 'TEMPLATE.md').is_file())

    def test_compatibility_paths_resolve_without_skill_copies(self):
        for old in ('skills/wl-git-flow', 'skills/wl-herdrs',
                    'skills-on-demand/hgj-codex', '.agents/skills/langfuse'):
            path = ROOT / old
            self.assertTrue(path.is_symlink(), old)
            self.assertTrue(path.exists(), old)
            self.assertTrue(str(path.resolve()).startswith(str(ROOT / 'tools/skills')), old)

    def test_every_mapped_package_is_present_and_old_skill_paths_are_aliases(self):
        manifest = json.loads((ROOT / "docs/migrations/2026-10-18-path-map.json").read_text())
        for move in manifest["moves"]:
            target = ROOT / move["to"]
            self.assertTrue(target.is_dir(), move)
            self.assertFalse(target.is_symlink(), move)
            if move["compatibility_symlink"] and not move["from"].startswith("claudecode_guide/"):
                # claudecode_guide 内部软链已随归位空壳按批准删除，见归位记录。
                old = ROOT / move["from"]
                self.assertTrue(old.is_symlink(), move)
                self.assertEqual(old.resolve(), target.resolve(), move)

    def test_approved_cleanup_keeps_canonical_plugins_and_retained_practice(self):
        base = ROOT / 'claudecode_guide/000_examples/.claude/.claude-plugin'
        for relative in ('code-review/README.md', 'code-review/.claude-plugin/plugin.json',
                         'code-review/commands/code-review.md',
                         'code-simplifier/agents/code-simplifier.md',
                         'code-simplifier/.claude-plugin/plugin.json'):
            self.assertFalse((base / relative).exists(), relative)
            self.assertTrue((ROOT / 'tools/skills/engineering/legacy-snapshots' / relative).is_file())
        for folder in ('AI2AI', 'ME2AI'):
            self.assertEqual(list((ROOT / 'double_layer_spec' / folder).glob('*.md')), [])
        removed = (
            'double_layer_spec/project_rule.md', '.marscode/deviceInfo.json',
            '.wl-ai-skills/browse/browse-audit.jsonl',
            '.wl-ai-skills/browse/browse-console.log',
            '.wl-ai-skills/browse/browse-network.log',
            'claudecode_guide/agent_guide/agents_store/code-reviewer_zh.md',
            'tools/skills/engineering/ai_coding_sec_dev_workflow/examples/UExtract/claude-conversation-2025-12-30-ca46e2b9.md',
        )
        for relative in removed:
            self.assertFalse((ROOT / relative).exists(), relative)
        self.assertTrue((ROOT / 'tools/skills/engineering/ai_coding_sec_dev_workflow/SKILL.md').is_file())
        self.assertTrue((ROOT / 'best_practices/2026-03-24-历史项目学习-生成系统学习文档/prompt.md').is_file())
        review = (ROOT / 'docs/migrations/2026-10-18-cleanup-candidates.md').read_text()
        self.assertIn('本轮删除 7 个文件', review)
        self.assertIn('C04 已按用户要求保留并提炼', review)

    def test_claudecode_guide_content_relocated_to_canonical_homes(self):
        for relative in (
                'best_practices/2026-06-16-任务编排-目标驱动的多角色任务提示词/prompt.md',
                'best_practices/2026-10-09-任务描述-轻量化任务描述模板/prompt.md',
                'best_practices/2026-06-10-项目入口规则-生成CLAUDE.md与AGENTS.md提示词/生成AGENTS.md提示词-分层优化版.md',
                'tools/templates/project-entry/template-java-springboot.md',
                'tools/templates/project-entry/samples/用户级-claude.md',
                'tools/templates/project-entry/rules',
                'tools/integrations/插件收录登记.md',
                'tools/integrations/subagent-配置指南.md',
                'tools/integrations/examples/opencode/opencode.json',
                'tools/integrations/examples/claude-code/settings-permissions.json',
                'candidates/agent-definitions/debugger.md',
                'docs/reference/skills-cheatsheets/AI Coding 全场景工具地图.md',
        ):
            self.assertTrue((ROOT / relative).exists(), relative)
        self.assertFalse((ROOT / 'claudecode_guide').exists())

    def test_migration_and_cleanup_are_separate(self):
        text = (ROOT / 'docs/migrations/2026-10-18-role-workbench-migration.md').read_text()
        self.assertIn('未删除', text)
        review = (ROOT / 'docs/migrations/2026-10-18-cleanup-candidates.md').read_text()
        self.assertIn('全部有明确去向', review)
        # 归位空壳经单独批准后删除，与本次迁移、清理仍相互独立。
        self.assertFalse((ROOT / 'claudecode_guide').exists())


if __name__ == '__main__':
    unittest.main()
