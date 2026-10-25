import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / 'tools/skills/engineering/wl-design-doc/scripts/check_design_doc.py'
LEGACY = dict(requirement_id='R1', status='approved', created='2026-10-16',
              updated='2026-10-16', chosen=None, approval_evidence='user-record:1')


def delegated():
    return dict(LEGACY, status='adopted', decision_mode='delegated', approval_evidence=None,
                chosen='reuse-existing', recommendation='reuse-existing', recommendation_reason='existing contract verified',
                requirement_version='r2', design_version='d3', source_test_cases={'path': 'cases.md', 'version': 'tc2'},
                critical_validation={'status': 'verified', 'evidence': 'contract-check:1'},
                delegation_evidence=dict(record='user-record:2', requirement_version='r2', design_version='d3',
                                         scope='R1', data_boundary='fixture only', cost_boundary='no paid services',
                                         operation_boundary='local source changes only'))


class DesignHandoffTests(unittest.TestCase):
    def check(self, meta, executable=False, case_path='cases.md'):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'design.wl-design-doc.html'
            cases = Path(tmp) / case_path
            cases.parent.mkdir(parents=True, exist_ok=True)
            cases.write_text('Fixture external test cases')
            path.write_text('<html><head><meta name="generator" content="wl-design-doc">'
                            '<meta name="artifact-schema-version" content="1"></head><body>'
                            '<script type="application/json" id="wl-design-meta">' + json.dumps(meta) +
                            f'</script><a href="{case_path}">cases</a></body></html>')
            return subprocess.run([sys.executable, str(CHECK), str(path)] +
                                  (['--require-executable'] if executable else []), capture_output=True, text=True)

    def test_legacy_approved_and_draft_structure_remain_valid(self):
        self.assertEqual(self.check(LEGACY).returncode, 0)
        self.assertEqual(self.check(dict(LEGACY, status='draft', approval_evidence=None)).returncode, 0)

    def test_manual_approval_cannot_be_missing(self):
        self.assertNotEqual(self.check(dict(LEGACY, approval_evidence=None)).returncode, 0)

    def test_delegation_missing_evidence_is_rejected(self):
        meta = delegated(); meta.pop('delegation_evidence')
        self.assertNotEqual(self.check(meta).returncode, 0)

    def test_legal_delegation_is_executable_and_not_manual_approval(self):
        result = self.check(delegated(), executable=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.check(LEGACY, executable=True).returncode, 0)

    def test_new_manual_approval_is_executable_with_complete_evidence(self):
        meta = dict(delegated(), decision_mode='manual', status='approved',
                    approval_evidence='user-record:3', delegation_evidence=None)
        self.assertEqual(self.check(meta, executable=True).returncode, 0)

    def test_delegated_approved_or_forged_manual_evidence_rejected(self):
        for changes in ({'status': 'approved'}, {'approval_evidence': 'not human approval'}, {'decision_mode': 'manual'}):
            with self.subTest(changes=changes):
                self.assertNotEqual(self.check(dict(delegated(), **changes)).returncode, 0)

    def test_each_delegation_boundary_and_version_is_required(self):
        for key in delegated()['delegation_evidence']:
            meta = delegated(); meta['delegation_evidence'].pop(key)
            with self.subTest(key=key):
                self.assertNotEqual(self.check(meta).returncode, 0)
        meta = delegated(); meta['delegation_evidence']['design_version'] = 'old'
        self.assertNotEqual(self.check(meta).returncode, 0)

    def test_candidate_without_critical_evidence_cannot_execute(self):
        for changes in ({'critical_validation': {'status': 'pending', 'evidence': None}},
                        {'chosen': None}, {'recommendation_reason': ''}, {'source_test_cases': {}},
                        {'chosen': 'other'}, {'status': 'draft'}):
            with self.subTest(changes=changes):
                self.assertNotEqual(self.check(dict(delegated(), **changes), executable=True).returncode, 0)
        self.assertNotEqual(self.check(dict(LEGACY, critical_validation={'status': 'failed', 'evidence': 'failed'}), executable=True).returncode, 0)

    def test_external_confirmed_cases_do_not_require_total_flow_filenames(self):
        meta = delegated()
        meta['source_test_cases'] = {'path': 'external/confirmed-business-cases.md', 'version': 'external-v5'}
        result = self.check(meta, executable=True, case_path=meta['source_test_cases']['path'])
        self.assertEqual(result.returncode, 0, result.stderr)
        design = (ROOT / 'tools/skills/engineering/wl-design-doc/SKILL.md').read_text()
        for contract in ('已确认的外部用例', '不要求本流程文件', '根本无用例', '交接缺口', '不造来源'):
            self.assertIn(contract, design)

    def test_new_executable_design_without_cases_is_not_fabricated(self):
        meta = delegated(); meta.pop('source_test_cases')
        self.assertNotEqual(self.check(meta, executable=True).returncode, 0)

    def test_engineering_decisions_are_required_without_fixed_chapters(self):
        skill = ROOT / 'tools/skills/engineering/wl-design-doc'
        design = (skill / 'SKILL.md').read_text()
        card = (skill / 'references/scenario-template.md').read_text()
        regression = (skill / 'references/regression-scenarios.md').read_text()
        # Text contract only: independent generation must still validate actual coverage.
        for contract in ('技术底座与选型', '模块职责与状态归属', '数据与保存边界',
                         '工程运行与交付', '直接质量约束', '不是强制五个章节',
                         '不发布/不安装', '实验通过只能证明对应能力', '工程决定可接手'):
            with self.subTest(contract=contract):
                self.assertIn(contract, design)
        for contract in ('正式现状 vs 原型实验 vs 本版推荐', '谁持有权威状态',
                         '提交触发与边界', '最小交付物', '是否阻塞实施'):
            self.assertIn(contract, card)
        for contract in ('独立 Agent', '不同类型的小改动', '正文缺权威状态与交付路径',
                         '不提供协调者的五块补充正文'):
            self.assertIn(contract, regression)

    def test_metadata_must_be_object(self):
        self.assertNotEqual(self.check([]).returncode, 0)


if __name__ == '__main__':
    unittest.main()
