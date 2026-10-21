"""只读检查Harness正文骨架，模板是唯一结构来源。"""

import argparse
import re
from pathlib import Path


PACK = Path(__file__).resolve().parents[1]
TEMPLATES = PACK / "assets/harness-template"


def headings(text):
    """读取代码块和注释之外的Markdown标题及其正文位置。"""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    result = []
    fence = None
    for number, line in enumerate(text.splitlines()):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is not None:
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if match:
            result.append((len(match.group(1)), match.group(2), number))
    return text.splitlines(), result


def has_body(lines, start, end):
    """忽略标题和空白，判断是否存在实际正文。"""
    return any(line.strip() and not re.match(r"^#{1,6}\s", line) for line in lines[start:end])


def validate(path, template):
    """按同一模板校验单个正文，不修改文件也不回显内容。"""
    expected = template.read_text(encoding="utf-8")
    content = path.read_text(encoding="utf-8")
    _, schema = headings(expected)
    lines, actual = headings(content)
    errors = []
    for level, label in ((1, "标题"), (2, "二级章节")):
        if [h[1] for h in actual if h[0] == level] != [h[1] for h in schema if h[0] == level]:
            errors.append(f"{label}缺失、重复、改名或顺序不同")
    if "<!-- 填写：" in content or re.search(r"\{(?:项目名|RULE-ID|范围)\}", content):
        errors.append("仍有模板提示")
    for index, (level, _, line) in enumerate(actual):
        if level != 2:
            continue
        end = next((h[2] for h in actual[index + 1:] if h[0] <= 2), len(lines))
        if not has_body(lines, line + 1, end):
            errors.append("存在空二级章节")
    # 章内可用紧凑列表/表格或详细条目，不强制三级以下字段与示例数量。
    metadata = next((line for line in lines if line.startswith("范围：")), "")
    if not re.match(r"^范围：\S.+；状态：(当前|拟采用|混合)；依据：\S", metadata):
        errors.append("缺少有效范围、状态或依据")
    return list(dict.fromkeys(errors))


def check(root=None, files=()):
    """只检查存在的标准正文，支持保留原路径的显式映射。"""
    templates = sorted(TEMPLATES.glob("rules/*.md")) + sorted(TEMPLATES.glob("wiki/*.md"))
    by_name = {p.name: p for p in templates}
    pairs = []
    errors = []
    if root is not None:
        allowed = {p.relative_to(TEMPLATES).as_posix() for p in templates}
        for folder in ("rules", "wiki"):
            for target in (root / folder).rglob("*.md"):
                if target.relative_to(root).as_posix() not in allowed:
                    errors.append(f"{target}: 非标准文件名；既有Owner请用--file显式映射")
        for template in templates:
            target = root / template.relative_to(TEMPLATES)
            if target.exists():
                pairs.append((target, template))
    for name, target in files:
        if name not in by_name:
            raise ValueError(f"未知正文类型：{name}")
        pairs.append((Path(target), by_name[name]))
    for target, template in pairs:
        if not target.is_file():
            errors.append(f"{target}: 正文不存在或不是文件")
            continue
        errors.extend(f"{target}: {error}" for error in validate(target, template))
    if not pairs:
        errors.append("没有可检查的规则或Wiki正文，不算结构通过")
    return len(pairs), errors


def main():
    """输出检查数量和结构问题，以退出码表达结果。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, help="docs/harness或个人目录")
    parser.add_argument("--file", nargs=2, action="append", default=[], metavar=("标准文件名", "实际路径"))
    args = parser.parse_args()
    try:
        count, errors = check(args.root, args.file)
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(1, f"结构检查无法完成：{type(error).__name__}\n")
    print(f"检查正文：{count}；结构问题：{len(errors)}")
    for error in errors:
        print(error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
