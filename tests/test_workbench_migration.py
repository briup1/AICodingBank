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
        verified = next(e for e in config['self'] if e['name'] == 'wl-auto-delivery')
        self.assertEqual(verified['verified'], '2026-10-19')
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

    def test_legacy_entry_paths_are_retired_without_skill_copies(self):
        for retired in ('skills', 'skills-on-demand', 'ai_coding_sec_dev_workflow'):
            self.assertFalse((ROOT / retired).exists(), retired)
        # 保留的项目级加载路径仍解析到 tools/skills，无第二份正文。
        kept = ROOT / '.agents/skills/langfuse'
        self.assertTrue(kept.is_symlink(), kept)
        self.assertTrue(kept.exists(), kept)
        self.assertTrue(str(kept.resolve()).startswith(str(ROOT / 'tools/skills')), kept)

    def test_every_mapped_package_is_present_and_old_skill_paths_are_aliases(self):
        # 2026-10-19 评估批准删除的迁入快照，目标目录按批准退役（见评估记录）。
        retired_snapshots = (
            'tools/skills/engineering/legacy-snapshots/android-native-dev',
            'tools/skills/engineering/legacy-snapshots/brainstorming',
            'tools/skills/engineering/legacy-snapshots/code-review',
            'tools/skills/engineering/legacy-snapshots/code-simplifier',
            'tools/skills/engineering/legacy-snapshots/feature-dev',
            'tools/skills/engineering/legacy-snapshots/frontend-design',
            'tools/skills/engineering/legacy-snapshots/frontend-dev',
            'tools/skills/engineering/legacy-snapshots/fullstack-dev',
            'tools/skills/engineering/legacy-snapshots/ios-application-dev',
            'tools/skills/engineering/legacy-snapshots/opencode',
            'tools/skills/engineering/legacy-snapshots/playwright-skill',
            'tools/skills/engineering/legacy-snapshots/plugin-dev',
            'tools/skills/engineering/legacy-snapshots/pr-review-toolkit',
            'tools/skills/engineering/legacy-snapshots/ralph-wiggum',
            'tools/skills/shared/legacy-snapshots/agent-browser',
        )
        manifest = json.loads((ROOT / "docs/migrations/2026-10-18-path-map.json").read_text())
        for move in manifest["moves"]:
            target = ROOT / move["to"]
            if any(move["to"] == p or move["to"].startswith(p + "/") for p in retired_snapshots):
                self.assertFalse(target.exists(), move)
                continue
            self.assertTrue(target.is_dir(), move)
            self.assertFalse(target.is_symlink(), move)
            if move["compatibility_symlink"] and not move["from"].startswith(
                    ("claudecode_guide/", "skills/", "skills-on-demand/", "ai_coding_sec_dev_workflow")):
                # claudecode_guide 内部软链与根兼容入口已按批准退役，见归位/退役记录。
                old = ROOT / move["from"]
                self.assertTrue(old.is_symlink(), move)
                self.assertEqual(old.resolve(), target.resolve(), move)

    def test_approved_cleanup_retires_duplicates_and_keeps_retained_practice(self):
        base = ROOT / 'claudecode_guide/000_examples/.claude/.claude-plugin'
        for relative in ('code-review/README.md', 'code-review/.claude-plugin/plugin.json',
                         'code-review/commands/code-review.md',
                         'code-simplifier/agents/code-simplifier.md',
                         'code-simplifier/.claude-plugin/plugin.json'):
            self.assertFalse((base / relative).exists(), relative)
            # 归位时保留的插件副本已于 2026-10-19 按评估批准删除（见评估记录）。
            self.assertFalse((ROOT / 'tools/skills/engineering/legacy-snapshots' / relative).exists(), relative)
        for folder in ('AI2AI', 'ME2AI'):
            self.assertEqual(list((ROOT / 'double_layer_spec' / folder).glob('*.md')), [])
        # 空目录已在旧入口退役时清除（2026-10-18）。
        self.assertFalse((ROOT / 'double_layer_spec').exists())
        self.assertFalse((ROOT / '.marscode').exists())
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
                'docs/reference/skills-cheatsheets/AI Coding 全场景工具地图.md',
        ):
            self.assertTrue((ROOT / relative).exists(), relative)
        self.assertFalse((ROOT / 'claudecode_guide').exists())
        # agent-definitions 候选已随 2026-10-19 评估批准删除，归位落点只剩 langfuse 在用快照。
        self.assertFalse((ROOT / 'candidates').exists())
        self.assertTrue((ROOT / 'tools/skills/engineering/legacy-snapshots/langfuse/SKILL.md').is_file())
        self.assertTrue((ROOT / 'tools/skills/media/legacy-snapshots/hot_topics/SKILL.md').is_file())
        self.assertTrue((ROOT / 'tools/skills/media/legacy-snapshots/remotion-best-practices/SKILL.md').is_file())

    def test_migration_and_cleanup_are_separate(self):
        text = (ROOT / 'docs/migrations/2026-10-18-role-workbench-migration.md').read_text()
        self.assertIn('未删除', text)
        review = (ROOT / 'docs/migrations/2026-10-18-cleanup-candidates.md').read_text()
        self.assertIn('全部有明确去向', review)
        # 归位空壳经单独批准后删除，与本次迁移、清理仍相互独立。
        self.assertFalse((ROOT / 'claudecode_guide').exists())


if __name__ == '__main__':
    unittest.main()
