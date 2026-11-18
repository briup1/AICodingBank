#!/usr/bin/env python3
"""Read-only inventory of explicitly listed local skill roots."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOME = Path.home()
ROOTS = [
    ('Agents 用户目录', HOME / '.agents/skills'),
    ('Claude 用户目录', HOME / '.claude/skills'),
    ('Codex 用户目录', HOME / '.codex/skills'),
    ('Codex 系统目录', HOME / '.codex/skills/.system'),
    ('Pi 用户目录', HOME / '.pi/agent/skills'),
    ('Pi 扩展', HOME / '.pi/agent/extensions/openviking/skills'),
    ('Pi 包：agent-skills', HOME / '.pi/agent/git/github.com/addyosmani/agent-skills/skills'),
    ('Pi 包：ponytail', HOME / '.pi/agent/git/github.com/DietrichGebert/ponytail/skills'),
]
CATEGORIES = [
    ('审查与规范', ('review', '审查', '审核', 'standards', '规范')),
    ('测试与验证', ('test', '测试', '验收', 'qa', '验证')),
    ('浏览器与网页', ('browser', '浏览器', '网页', 'playwright')),
    ('开发与架构', ('coding', '开发', '代码', 'architecture', '架构', 'implementation', '接口')),
    ('项目与流程', ('git', 'worktree', '项目', 'workflow', '工作流', 'planning')),
    ('研究与文档', ('research', '调研', '文档', '搜索', 'search', 'documentation')),
    ('记忆与知识', ('memory', '记忆', '知识', 'knowledge', 'openviking')),
    ('设计与媒体', ('design', '设计', 'media', '媒体', 'ui', '视觉')),
]


def metadata(path):
    text = path.read_text(encoding='utf-8', errors='replace')[:32768]
    front = text.split('---', 2)[1] if text.startswith('---') and text.count('---') >= 2 else ''
    name = re.search(r'^name:\s*["\']?([^\n"\']+)', front, re.M)
    description = re.search(r'^description:\s*([^\n]+)', front, re.M)
    desc = description.group(1).strip().strip('"\'') if description else ''
    if desc in ('|', '>', '|-', '>-'):
        match = re.search(r'^description:\s*[|>][-+]?\s*\n((?:[ \t]+.*\n?)+)', front, re.M)
        desc = ' '.join(line.strip() for line in match.group(1).splitlines()) if match else ''
    return (name.group(1).strip() if name else path.parent.name, desc or '未识别用途说明')


def classify(name, description):
    haystack = (name + ' ' + description).lower()
    for category, terms in CATEGORIES:
        if any(term in haystack for term in terms):
            return category
    return '其他 / 待确认'


def scan(roots):
    grouped = {}
    warnings = []
    scanned = []
    for label, root in roots:
        root = Path(root)
        if not root.is_dir():
            warnings.append(f'{label}: 目录不存在或不可访问：{root}')
            continue
        scanned.append({'label': label, 'path': str(root)})
        try:
            children = sorted(root.iterdir(), key=lambda p: p.name.lower())
        except OSError as e:
            warnings.append(f'{label}: 无法读取：{e}')
            continue
        for entry in children:
            if entry.is_symlink() and not entry.exists():
                warnings.append(f'失效链接：{entry}')
                continue
            if not entry.is_dir() or entry.name.startswith('.'):
                continue
            doc = entry / 'SKILL.md'
            if not doc.is_file():
                continue
            try:
                source = str(doc.resolve(strict=True).parent)
                name, description = metadata(doc)
                stat = doc.stat()
            except (OSError, RuntimeError) as e:
                warnings.append(f'无法读取 {doc}: {e}')
                continue
            item = grouped.setdefault(source, {'id': hashlib.sha256(source.encode()).hexdigest()[:16],
                'name': name, 'description': description, 'category': classify(name, description),
                'source': source, 'entries': [], 'fingerprint': f'{stat.st_size}:{stat.st_mtime_ns}'})
            item['entries'].append({'path': str(entry), 'root': label, 'symlink': entry.is_symlink()})
    return {'generatedAt': datetime.now(timezone.utc).isoformat(), 'roots': scanned,
            'warnings': warnings, 'skills': sorted(grouped.values(), key=lambda x: (x['name'].lower(), x['source']))}


if __name__ == '__main__':
    data = scan(ROOTS)
    result = 'window.SKILL_INVENTORY = ' + json.dumps(data, ensure_ascii=False, indent=2).replace('</', '<\\/') + ';\n'
    target = HERE / 'skills.generated.js'
    temp = target.with_suffix('.tmp')
    temp.write_text(result, encoding='utf-8')
    temp.replace(target)
    print(f"扫描完成：{len(data['skills'])} 个真实来源，{sum(len(s['entries']) for s in data['skills'])} 个入口；{len(data['warnings'])} 条提示。")
    print(f'已更新 {target}，刷新 Skill 管理页面查看。')
