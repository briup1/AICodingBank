"""Review prompts must flag risks without changing independent dimensions."""
from contextlib import redirect_stdout
from copy import deepcopy
import io
from unittest.mock import patch
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('atlas_content', ROOT / 'scripts/check_content.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class ContentTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'assets/example.json').read_text())
        self.cap = self.data['modules'][0]['capabilities'][0]

    def test_decision_reason_is_flagged_but_not_reclassified(self):
        self.cap['necessity']['reason'] = '已确认建设，负责人选择人工方式。'
        before = deepcopy(self.data)
        self.assertTrue(any('职责理由' in x for x in checker.content_warnings(self.data)))
        self.assertEqual(self.data, before)
        self.cap['necessity']['reason'] = '没有申请就无法确定谁需要哪本书。'
        self.assertFalse(any('职责理由' in x for x in checker.content_warnings(self.data)))

    def test_technical_name_only_after_plain_effect(self):
        self.cap['definition'] = 'ready FIFO manifest lease 处理。'
        self.assertTrue(any('.definition' in x for x in checker.content_warnings(self.data)))
        self.cap['definition'] = '任务按接收顺序等待执行（FIFO）。'
        self.assertFalse(any('.definition' in x for x in checker.content_warnings(self.data)))
        self.cap['evidence'][0]['finding'] = '源码有 ready/FIFO/manifest/lease 符号。'
        self.assertFalse(any('.definition' in x for x in checker.content_warnings(self.data)))

    def test_no_retest_is_a_review_prompt_not_a_status_downgrade(self):
        for status in ('部分完成', '尚未核实'):
            for limit in ('本轮未验证', '本轮未重验全部格式', '未覆盖全部组合'):
                with self.subTest(status=status, limit=limit):
                    self.cap.update(status=status, current='已有实现；' + limit)
                    before = deepcopy(self.data)
                    self.assertTrue(any('未复测降级风险' in x for x in checker.content_warnings(self.data)))
                    self.assertEqual(self.data, before)
        self.cap['status'] = '已完成'
        self.assertFalse(any('未复测降级风险' in x for x in checker.content_warnings(self.data)))

    def test_evidence_retest_limit_also_prompts_without_overriding_real_gaps(self):
        self.cap.update(status='部分完成', current='已有导入实现，但目标所需的删除行为尚缺。')
        self.cap['evidence'][0]['finding'] = '本轮未复测。'
        before = deepcopy(self.data)
        self.assertTrue(any('未复测降级风险' in x for x in checker.content_warnings(self.data)))
        self.assertEqual(self.data, before)
        self.cap.update(name='实际恢复演练', definition='证明备份能恢复借还记录。', current='已有恢复脚本；本轮未验证，目标所需的实际恢复记录尚缺。')
        warnings = checker.content_warnings(self.data)
        self.assertTrue(any('目标本身要求的验证' in x for x in warnings))
        self.assertEqual(self.cap['status'], '部分完成')
        self.cap['current'] = '缺少目标要求的删除行为。'
        self.cap['evidence'][0]['finding'] = '代码入口尚未接入删除处理。'
        self.assertFalse(any('未复测降级风险' in x for x in checker.content_warnings(self.data)))

    def test_review_prompts_cover_inventory_scope_and_meaning_without_mutation(self):
        before = deepcopy(self.data)
        output = io.StringIO()
        with patch.object(sys, 'argv', ['check_content.py', str(ROOT / 'assets/example.json')]), redirect_stdout(output):
            self.assertEqual(checker.main(), 0)
        for required in ('已存在但不扩建', '主链标题不能代替能力定义', '可选领域保留来源中的具体职责与未决项',
                         '不自动变必建', '对象、动作、结果', '不用新 UI 替换原职责', '不自动裁决'):
            self.assertIn(required, output.getvalue())
        self.assertEqual(self.data, before)

    def test_example_partial_status_has_a_target_behavior_gap(self):
        self.assertIn('目标要求的重复申请拦截尚未接入', self.cap['current'])
        self.assertIn('实现依据尚缺', self.data['modules'][0]['capabilities'][1]['evidence'][0]['finding'])

    def test_manual_method_does_not_erase_quality_gap(self):
        self.cap.update(decision='沿用现有', approach='沿用人工检查。', current='还需补齐开放前质量核对。')
        self.assertTrue(any('质量补齐' in x for x in checker.content_warnings(self.data)))
        self.cap['decision'] = '已确认要做'
        self.assertFalse(any('质量补齐' in x for x in checker.content_warnings(self.data)))


if __name__ == '__main__':
    unittest.main()
