import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
import install

ROOT = Path(__file__).resolve().parents[1]
FLOW = ROOT / 'tools/skills/workbench/wl-auto-delivery'


class AutoDeliveryTests(unittest.TestCase):
    def test_registration_and_catalog_are_generated_without_install(self):
        cfg = yaml.safe_load((ROOT / 'skills.yaml').read_text())
        entries = cfg['self']
        matches = [e for e in entries if e['name'] == 'wl-auto-delivery']
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['verified'], '2026-10-19')
        self.assertTrue((ROOT / matches[0]['path'] / 'SKILL.md').is_file())
        self.assertNotIn('wl-phase-routing', [e['name'] for e in entries])
        lock = json.loads((ROOT / cfg['third_party']['lock']).read_text())['skills']
        catalog_entries = [dict(e, origin='自研') for e in entries]
        for name, meta in lock.items():
            origin = f"第三方·{meta['source']}" + (f"@{meta['ref']}" if meta.get('ref') else '')
            catalog_entries.append(dict(meta, name=name, origin=origin))
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'CATALOG.md'
            install.write_catalog(catalog_entries, output)
            self.assertEqual(output.read_bytes(), (ROOT / 'CATALOG.md').read_bytes())

    def test_entry_stages_contract_and_local_links(self):
        paths = [ROOT / 'WORKBENCH.md', FLOW / 'SKILL.md', *sorted((FLOW / 'references').glob('*.md'))]
        text = (FLOW / 'SKILL.md').read_text()
        for stage in ('Observe', 'Confirm', 'Design', 'Execute', 'Verify', 'Learn'):
            self.assertIn(stage, text)
        for reference in ('test-case-review.md', 'execution-and-evidence.md', 'regression-scenarios.md'):
            self.assertTrue((FLOW / 'references' / reference).is_file())
        self.assertNotIn('wl-phase-routing', (ROOT / 'WORKBENCH.md').read_text())
        for path in paths:
            for href in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
                parts = urlsplit(href)
                if parts.scheme or parts.netloc or not parts.path:
                    continue
                self.assertTrue((path.parent / unquote(parts.path)).exists(), (path, href))

    def test_reading_artifact_handoff_is_caller_owned_and_not_qa_gate(self):
        text = (FLOW / 'references/execution-and-evidence.md').read_text()
        for contract in ('test-cases.wl-qa-test-planner.md', 'test-cases.wl-qa-test-planner.html',
                         '同源 HTML', '调用方负责', 'A/B', '相对链接', '实际存在', '历史名称',
                         '单独调用 QA', '不以 HTML 生成作为 QA 前置'):
            self.assertIn(contract, text)
        self.assertIn('test-cases.wl-qa-test-planner', (FLOW / 'SKILL.md').read_text())

    def test_defects_runs_retention_and_resume_contract(self):
        evidence = (FLOW / 'references/execution-and-evidence.md').read_text()
        for field in ('问题', '环境与数据/版本', '复现与证据', '需求范围依据', '代码确认',
                      '根因待确认', '预期引用', '修复及复测', '长期摘要', '关键证据', '临时产物',
                      'test-execution.md', 'progress.md', '当前阶段', '确认范围', '下一步'):
            self.assertIn(field, evidence)
        flow = (FLOW / 'SKILL.md').read_text()
        for contract in ('所有适用用例必须通过', '不适用须依据', '失败/阻塞/未执行不算完成',
                         '不能由 Agent 自己接受', '目标环境通过不等于发布', 'progress.md'):
            self.assertIn(contract, flow)

    def test_navigation_focused_scope_and_task_slug_contract(self):
        flow = (FLOW / 'SKILL.md').read_text()
        for contract in ('wl-git-flow', '创建/复用需求 Worktree', '记录环境结果', '写业务文档/代码前',
                         '目录和分支', 'wl-compass-local-test', '其他项目', '非生产', 'wl-prod-db',
                         '默认只读', '不默许写'):
            self.assertIn(contract, flow)
        focused = (ROOT / 'tools/skills/engineering/wl-requesting-code-review/SKILL.md').read_text().split('## Modes', 1)[1].split('## Prepare review context', 1)[0]
        for contract in ('设计偏离', '具体交付阻断问题', '建议可省略', '不做泛化改进审查'):
            self.assertIn(contract, focused)
        web = (ROOT / 'tools/skills/shared/wl-web-auto/SKILL.md').read_text()
        self.assertIn('R-123 → r-123', web)
        self.assertIn('保留原需求 ID', web)
        self.assertIn('--task r-123', web)
        self.assertNotIn('--task <requirement>', web)

    def test_qa_generation_core_and_review_full_are_preserved(self):
        qa = (ROOT / 'tools/skills/engineering/wl-qa-test-planner/SKILL.md').read_text()
        expected = {
            '## 执行链路': '2c3db85c6a1ec9b9b6bc5f7453d275a348d16aaabe12579e880da10d8e240ccd',
        }
        for heading, digest in expected.items():
            section = qa.split(heading, 1)[1].split('\n## ', 1)[0]
            self.assertEqual(hashlib.sha256(section.encode()).hexdigest(), digest)
        review = (ROOT / 'tools/skills/engineering/wl-requesting-code-review/SKILL.md').read_text()
        original = review.split('## Modes', 1)[0] + '## Prepare review context' + review.split('## Prepare review context', 1)[1]
        self.assertEqual(hashlib.sha256(original.encode()).hexdigest(),
                         'a481644352d65dddcf2334a805a52b2bcb77db74416059c3aa53f79dc70d3ffd')

    def test_qa_core_five_steps_and_fields_retained(self):
        text = (ROOT / 'tools/skills/engineering/wl-qa-test-planner/SKILL.md').read_text()
        for step in ('1. 列出已确认需求与测试范围。', '2. 按实际规则拆分正向、异常、边界和状态变化场景；',
                     '3. 按业务影响设置 P0/P1/P2；', '4. 为每个场景写出前置条件、具体测试数据、逐步操作和可观察、可判定的逐步预期。',
                     '5. 对照每条需求检查覆盖和遗漏；'):
            self.assertIn(step, text)
        for field in ('Trace', '优先级', '前置条件', '**测试场景**', '**测试数据**', '**测试步骤**', '预期：'):
            self.assertIn(field, text)
        self.assertIn('用例与缺口交付后停止', text)
        self.assertIn('不执行业务测试、业务脚本或业务写操作', text)

    def test_qa_output_uses_tree_and_separates_execution_records(self):
        text = (ROOT / 'tools/skills/engineering/wl-qa-test-planner/SKILL.md').read_text()
        for rule in ('共用动作放父节点', '每个检查点紧跟“预期”', '测试步骤与多路径不用表格',
                     '不另起“结果检查/保存检查/拦截检查”区', '生成用例时不填执行结果',
                     '保留用例 ID、需求追踪、优先级、业务预期、边界值和待确认事项'):
            self.assertIn(rule, text)
        sample = text.split('````markdown', 1)[1].split('````', 1)[0]
        self.assertIn('1.1.1', sample)
        self.assertNotIn('|', sample)
        self.assertNotIn('实际：', sample)
        self.assertNotIn('状态：', sample)
        for field in ('测试场景', '测试数据', '测试步骤'):
            self.assertIn(f'**{field}**：', sample)
            self.assertNotIn(f'**{field}：**', sample)

    def test_qa_page_entry_and_html_contract(self):
        text = (ROOT / 'tools/skills/engineering/wl-qa-test-planner/SKILL.md').read_text()
        for rule in ('完整业务页面地址', '给可点击链接', '链接放在代码块外', '不拼猜测地址',
                     '不把原型、用例阅读页', '路由来自代码、页面尚未核验',
                     '不能显示 Markdown 星号', '不维护两份业务正文'):
            self.assertIn(rule, text)
        skill_dir = ROOT / 'tools/skills/engineering/wl-qa-test-planner'
        match = re.search(r'模板：`([^`]+)`', text)
        self.assertIsNotNone(match)
        template = (skill_dir / match.group(1)).resolve()
        self.assertTrue(template.is_relative_to(ROOT / 'vendor'))
        self.assertEqual(template.name, 'test_case_templates.md')


if __name__ == '__main__':
    unittest.main()
