import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "tools/skills/engineering/harness-pack"
SPEC = importlib.util.spec_from_file_location("harness_structure", ROOT / "scripts/check_structure.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)

# 独立固定批准的章节契约，模板变更必须显式审阅此预期，测试不生成oracle。
SECTIONS = {
    "rules/工程结构.md": ["目录与模块职责", "依赖与运行链路", "常见改动落点", "来源与未覆盖"],
    "rules/编码规范.md": ["工具与已有约定", "组件规则", "测试代码约定", "来源与未覆盖"],
    "rules/开发流程规范.md": ["需求与资料归宿", "从需求到交付", "确认与操作边界", "完成与资料回写", "来源与未覆盖"],
    "rules/测试规范.md": ["按改动选择验证", "执行入口与证据", "环境与副作用边界", "结果与未覆盖", "来源与未覆盖"],
    "wiki/业务模型.md": ["角色与能力边界", "能力与流程", "实现与验证落点", "来源与未覆盖"],
    "wiki/领域术语.md": ["术语与名称对应", "易混淆边界", "来源与未覆盖"],
    "wiki/数据模型.md": ["数据所有权总览", "对象与状态", "修改与验证落点", "来源与未覆盖"],
    "wiki/接口协议.md": ["范围与权威契约", "通用约定", "接口与消息条目", "来源与未覆盖"],
}

# 两个不同技术栈的手写正文，不用模板产生或更新预期结果。
PROJECT_A = """# 工程结构

范围：报价CLI；状态：当前；依据：cli.py与pyproject.toml。

## 目录与模块职责

cli.py处理输入，quote.py计算报价，不提供HTTP服务。

## 依赖与运行链路

命令参数→cli.main→quote.calculate→标准输出；核心计算不反向依赖CLI。

## 常见改动落点

金额算法改quote.calculate，用已有test_quote.py核对结果。

## 来源与未覆盖

依据上述入口和测试；尚未核验打包后的命令安装。
"""
PROJECT_B = """# 工程结构

范围：文档站；状态：当前；依据：package.json和src/routes。

## 目录与模块职责

src/routes拥有页面，src/components承载复用展示；无业务数据库。

## 依赖与运行链路

URL→页面路由→组件→DOM；不存在后端队列。

## 常见改动落点

导航改src/routes，验证目标页面DOM与声明的构建命令。

## 来源与未覆盖

依据路由实现；移动端页面未做真实浏览器核验。
"""


class HarnessPackContentTests(unittest.TestCase):
    def test_templates_match_approved_structure(self):
        self.assertEqual({p.relative_to(checker.TEMPLATES).as_posix() for p in checker.TEMPLATES.glob("*/*.md")}, set(SECTIONS))
        for relative, expected in SECTIONS.items():
            _, actual = checker.headings((checker.TEMPLATES / relative).read_text())
            self.assertEqual([h[1] for h in actual if h[0] == 1], [Path(relative).stem])
            self.assertEqual([h[1] for h in actual if h[0] == 2], expected)
        self.assertFalse((checker.TEMPLATES / "CLAUDE.md").exists())
        self.assertFalse((checker.TEMPLATES / "agents").exists())
        self.assertFalse((checker.TEMPLATES / "skills").exists())
        self.assertFalse((checker.TEMPLATES / "changes").exists())

    def test_two_projects_and_sync_preserve_structure_and_user_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, text in (("A", PROJECT_A), ("B", PROJECT_B)):
                project = root / name
                target = project / "rules/工程结构.md"
                target.parent.mkdir(parents=True)
                target.write_text(text)
                private = project / "testing.md"
                private.write_bytes(b"\xff")  # checker不得读取账号卡。
                before = target.read_bytes()
                self.assertEqual(checker.check(project), (1, []))
                self.assertEqual(target.read_bytes(), before)
                updated = text.replace("尚未核验打包后的命令安装。", "已核验命令安装；本需求无接口变化。")
                target.write_text(updated)
                self.assertEqual(checker.check(project), (1, []))
                stable = target.read_bytes()
                self.assertEqual(checker.check(project), (1, []))
                self.assertEqual(target.read_bytes(), stable)

    def test_heading_drift_fails_for_correct_reason(self):
        variants = {
            "missing": PROJECT_A.replace("## 常见改动落点", "常见改动落点"),
            "renamed": PROJECT_A.replace("## 常见改动落点", "## 开发地图"),
            "duplicate": PROJECT_A + "\n## 来源与未覆盖\n重复内容。\n",
        }
        # 显式交换两章标题，不能因字符串逐步替换误还原。
        variants["order"] = PROJECT_A.replace("## 目录与模块职责", "## 临时").replace("## 依赖与运行链路", "## 目录与模块职责").replace("## 临时", "## 依赖与运行链路")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "工程结构.md"
            for name, text in variants.items():
                with self.subTest(name=name):
                    target.write_text(text)
                    errors = checker.validate(target, checker.TEMPLATES / "rules/工程结构.md")
                    self.assertIn("二级章节缺失、重复、改名或顺序不同", errors)

    def test_body_hints_title_metadata_and_fences(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "工程结构.md"
            template = checker.TEMPLATES / "rules/工程结构.md"
            for text, reason in (
                (PROJECT_A.replace("金额算法改quote.calculate，用已有test_quote.py核对结果。", ""), "存在空二级章节"),
                (PROJECT_A + "\n<!-- 填写：未处理 -->\n", "仍有模板提示"),
                (PROJECT_A.replace("# 工程结构", "# 项目结构", 1), "标题缺失、重复、改名或顺序不同"),
                (PROJECT_A.replace("状态：当前", "状态：完成"), "缺少有效范围、状态或依据"),
            ):
                target.write_text(text)
                self.assertIn(reason, checker.validate(target, template))
            target.write_text(PROJECT_A + "\n```markdown\n## 不是正文标题\n```\n")
            self.assertEqual(checker.validate(target, template), [])

    def test_all_templates_have_valid_major_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in SECTIONS:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                text = (checker.TEMPLATES / relative).read_text()
                target.write_text(re.sub(r"<!-- 填写：.*?-->", "已核实的条目正文。", text, flags=re.S))
            self.assertEqual(checker.check(root), (8, []))

    def test_compact_and_detailed_entries_use_same_major_structure(self):
        compact = """# 编码规范

范围：命令行工具；状态：当前；依据：项目AGENTS及pyproject.toml。

## 工具与已有约定

格式化使用pyproject.toml声明的工具。

## 组件规则

- 已确认：CLI错误只写stderr，结构化结果只写stdout；依据根AGENTS。

## 测试代码约定

无额外约定，使用现有tests中的写法。

## 来源与未覆盖

上述项目指令和配置；未验证跨平台终端。
"""
        detailed = compact.replace(
            "- 已确认：CLI错误只写stderr，结构化结果只写stdout；依据根AGENTS。",
            "### 输出流\n\n#### 行为与依据\n\n已确认：错误输出到stderr；依据根AGENTS。\n\n"
            "#### 最小例子\n\n正确：stderr接收错误；错误：将错误混入stdout破坏JSON消费者。",
        )
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "编码规范.md"
            template = checker.TEMPLATES / "rules/编码规范.md"
            for text in (compact, detailed):
                target.write_text(text)
                self.assertEqual(checker.validate(target, template), [])
                target.write_text(text.replace("## 组件规则", "## 自定规则"))
                self.assertIn("二级章节缺失、重复、改名或顺序不同", checker.validate(target, template))
                target.write_text(text.replace(text.split("## 组件规则\n\n")[1].split("\n\n## 测试代码约定")[0], ""))
                self.assertIn("存在空二级章节", checker.validate(target, template))

    def test_no_files_is_not_success_and_explicit_owner_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertTrue(checker.check(root)[1])
            target = root / "旧架构.md"
            target.write_text(PROJECT_B)
            self.assertEqual(checker.check(files=[("工程结构.md", target)]), (1, []))
            result = subprocess.run([sys.executable, str(ROOT / "scripts/check_structure.py"), "--file", "工程结构.md", str(target)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            target.write_text(PROJECT_B.replace("## 来源与未覆盖", "## 其他"))
            result = subprocess.run([sys.executable, str(ROOT / "scripts/check_structure.py"), "--file", "工程结构.md", str(target)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)

    def test_renamed_files_are_not_silently_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "rules/项目结构.md"
            target.parent.mkdir()
            target.write_text(PROJECT_A)
            self.assertTrue(any("非标准文件名" in error for error in checker.check(root)[1]))
            self.assertEqual(checker.check(files=[("工程结构.md", target)]), (1, []))

    def test_only_two_registered_skills_share_the_same_protocol(self):
        config = yaml.safe_load((REPO / "skills.yaml").read_text())
        entries = [e for e in config["self"] if "harness" in e["name"]]
        self.assertEqual({e["name"] for e in entries}, {"wl-harness-setup", "wl-harness-sync"})
        for entry in entries:
            self.assertEqual(entry["verified"], "")
            skill = REPO / entry["path"] / "SKILL.md"
            text = skill.read_text()
            self.assertEqual(entry["path"], f"tools/skills/engineering/{entry['name']}")
            self.assertIn("../harness-pack/references/shared-protocol.md", text)
            self.assertIn("../harness-pack/assets/harness-template/", text)
        self.assertFalse((ROOT / "skills").exists())
        self.assertEqual(list(ROOT.rglob("SKILL.md")), [])
        protocol = (ROOT / "references/shared-protocol.md").read_text()
        self.assertIn("docs/changes/", protocol)
        self.assertNotIn("docs/harness/changes/0001", protocol)

    def test_active_resource_links_exist(self):
        for folder in (ROOT.parent / "wl-harness-setup", ROOT.parent / "wl-harness-sync", ROOT / "references"):
            for path in folder.rglob("*.md"):
                text = path.read_text()
                for target in re.findall(r"\[[^]]+]\(([^)]+)\)", text):
                    if "://" not in target:
                        self.assertTrue((path.parent / target.split("#")[0]).resolve().exists(), f"{path}: {target}")


if __name__ == "__main__":
    unittest.main()
