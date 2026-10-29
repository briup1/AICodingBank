import json
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'tools/execution-profiles/test-execution.md'


class TestExecutionContractTests(unittest.TestCase):
    def test_record_example_is_single_result_and_has_a_stable_identity(self):
        text = CONTRACT.read_text()
        example = json.loads(re.search(r'```json\n(.*?)\n```', text, re.S)[1])
        self.assertEqual(example['schemaVersion'], 1)
        for key in ('runId', 'taskId', 'cases', 'environment', 'versions', 'status',
                    'startedAt', 'updatedAt', 'endedAt', 'previousRun', 'items'):
            self.assertIn(key, example)
        self.assertEqual(set(example['cases']), {'path', 'version', 'sha256'})
        item = example['items'][0]
        for key in ('caseId', 'step', 'entry', 'variant', 'status', 'actual', 'issue', 'evidence'):
            self.assertIn(key, item)
        self.assertNotIn('expected', item)
        self.assertNotIn('summary', example)
        for rule in ('每轮只维护一份', '有截图、日志、响应摘要等证据时才建', '不增加“开始测试”按钮',
                     '原子替换', '每轮一个写入负责人', '不能盲目重放提交', '不覆盖旧失败',
                     '不把未复测项目复制成通过', '父节点只导航', '不能多进程各自覆盖整个文件'):
            self.assertIn(rule, text)

    def test_test_entrypoints_link_the_single_contract(self):
        agents = (ROOT / 'AGENTS.md').read_text()
        self.assertIn('tools/execution-profiles/test-execution.md', agents)
        entries = [
            'tools/execution-profiles/README.md',
            'roles/engineering/tester/ROLE.md',
            'tools/skills/engineering/wl-qa-test-planner/SKILL.md',
            'tools/skills/engineering/wl-ticket-run/SKILL.md',
            'tools/skills/workbench/wl-auto-delivery/SKILL.md',
            'tools/skills/workbench/wl-auto-delivery/references/execution-and-evidence.md',
            'tools/skills/shared/wl-web-auto/SKILL.md',
        ]
        for relative in entries:
            path = ROOT / relative
            links = re.findall(r'\[[^]]*\]\(([^)]+test-execution\.md)\)', path.read_text())
            if relative == 'tools/execution-profiles/README.md':
                links = re.findall(r'\[[^]]*\]\((test-execution\.md)\)', path.read_text())
            self.assertTrue(links, relative)
            for link in links:
                self.assertEqual((path.parent / link).resolve(), CONTRACT, relative)

    def test_web_execution_uses_ego_without_replacing_evidence_or_identity_gates(self):
        skill = ROOT / 'tools/skills/shared/wl-web-auto'
        web = (skill / 'SKILL.md').read_text()
        for rule in ('ego-browser skill', 'ego-browser nodejs', 'taskSpace(',
                     'task.handOff()', 'takeOverTaskSpace(', 'task.finish({ keep: [] })',
                     '账号、企业', '不能证明身份', '不静默回退',
                     '最多3个活跃网页任务', '不是 Ego 产品上限',
                     '不继承 shell 环境变量', '截图', '实际查看'):
            self.assertIn(rule, web)
        self.assertNotIn('lifecycle.mjs begin', web)
        self.assertNotIn('lifecycle.mjs exec', web)
        self.assertNotIn('lifecycle.mjs finish', web)
        lifecycle = (skill / 'references/lifecycle.md').read_text()
        for rule in ('用户接管', '异常', '不调用 `finish()`', 'finished', 'handed-off',
                     'interrupted', '不能仅凭进程退出', '旧 OpenCLI'):
            self.assertIn(rule, lifecycle)
        capabilities = (skill / 'references/capabilities.md').read_text()
        self.assertIn('Ego 未完成真实场景验证', capabilities)
        self.assertIn('不能作为 Ego 验证证据', capabilities)
        entry = next(item for item in yaml.safe_load((ROOT / 'skills.yaml').read_text())['self']
                     if item['name'] == 'wl-web-auto')
        self.assertIn('Ego', entry['capability'])
        self.assertEqual(entry['verified'], '')

    def test_web_testing_and_general_web_tasks_are_distinct(self):
        web = (ROOT / 'tools/skills/shared/wl-web-auto/SKILL.md').read_text()
        self.assertIn('--test-run <本轮绝对目录>', web)
        self.assertIn('普通网页任务仍由', web)
        self.assertIn('不要再写 `result.md/run.json`', web)
        self.assertIn('截图和日志按需放evidence/', web)
        qa = (ROOT / 'tools/skills/engineering/wl-qa-test-planner/SKILL.md').read_text()
        self.assertIn('不创建测试轮次', qa)


if __name__ == '__main__':
    unittest.main()
