import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "skills" / "harness-pack"


class HarnessPackContentTests(unittest.TestCase):
    def test_developer_manual_contract(self):
        required = {
            "assets/harness-template/rules/工程结构.md": ["变更落点地图", "运行时链路", "前端", "后端"],
            "assets/harness-template/rules/编码规范.md": ["代码落点", "默认实现方式", "禁止平行机制", "测试代码规范"],
            "assets/harness-template/wiki/接口协议.md": ["鉴权与前置条件", "请求或事件", "成功响应或结果", "错误与关闭语义", "副作用与时序", "最小合法示例"],
            "assets/harness-template/wiki/业务模型.md": ["调用方实现", "提供方实现", "状态所有者", "错误路径与不变量"],
            "assets/harness-template/wiki/数据模型.md": ["权威所有者", "一致性与并发", "状态机与枚举", "未知值处理"],
            "references/content-standard.md": ["有限契约：全量枚举", "开放惯例：按范围抽样", "任务型验收"],
        }
        for relative, tokens in required.items():
            text = (ROOT / relative).read_text(encoding="utf-8")
            for token in tokens:
                self.assertIn(token, text, f"{relative} 缺少 {token}")

    def test_skill_references_exist(self):
        for skill in (ROOT / "skills").glob("*/SKILL.md"):
            text = skill.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^]]+]\(([^)]+\.md)\)", text):
                self.assertTrue((skill.parent / target).resolve().is_file(), f"{skill}: {target}")

    def test_legacy_requires_complete_contracts_and_task_walkthroughs(self):
        text = (ROOT / "skills/harness-bootstrap-legacy/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("发现数、文档化数和排除数", text)
        self.assertIn("三类代表性任务的静态推演", text)
        self.assertNotIn("Harness 只写缺口和最薄引用", text)


if __name__ == "__main__":
    unittest.main()
