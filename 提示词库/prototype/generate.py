#!/usr/bin/env python3
"""Generate prototype data from the workbench's Markdown prompt library."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = {'sdd': 'Spec 驱动开发', 'deepen': '更深入而不是更大', 'project-delivery': '项目经理交付', 'codex-handoff': 'Codex 交接与审计'}
records = []
for folder, category in CATEGORIES.items():
    for path in sorted((ROOT / folder).glob('*.md')):
        if path.name == 'README.md':
            continue
        text = path.read_text(encoding='utf-8')
        title = re.search(r'^#\s+(.+)$', text, re.M)
        block = re.search(r'^```(?:text|markdown)\s*\n(.*?)^```\s*$', text, re.M | re.S)
        if not title or not block:
            raise SystemExit(f'无法识别标题或正文：{path}')
        def field(name):
            match = re.search(r'^\*\*' + name + r'\*\*：(.+)$', text, re.M)
            return match.group(1).strip() if match else ''
        status = field('状态')
        records.append({'id': f'{folder}/{path.stem}', 'title': title.group(1),
                        'description': field('什么时候用'), 'category': category,
                        'status': status or '未标注', 'tags': [], 'content': block.group(1).rstrip('\n'),
                        'source': str(path.relative_to(ROOT.parent)),
                        'kind': '结构模板' if folder == 'sdd' and path.name.startswith('02-') else '提示词'})
output = 'window.WORKBENCH_PROMPTS = ' + json.dumps(records, ensure_ascii=False, indent=2) + ';\n'
(Path(__file__).parent / 'prompts.generated.js').write_text(output, encoding='utf-8')
print(f'已生成 {len(records)} 条，包含 1 条结构模板。')
