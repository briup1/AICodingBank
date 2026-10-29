"""Core regression tests; no browser or third-party packages required."""
from copy import deepcopy
from html import escape
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("atlas_render", ROOT / "scripts/render.py")
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.scripts = []
        self.tables = []
        self.details = {}
        self.module_summaries = []
        self.active_details = []
        self.row = None
        self.cell = None
        self.field = None
        self.term = None
        self.summary = None
        self.in_script = False
        self.script = ""
        self.external_resources = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a':
            self.links.append(attrs['href'])
        if tag in ('script', 'img', 'iframe', 'link') and ('src' in attrs or 'href' in attrs):
            self.external_resources.append(attrs)
        if tag == 'script':
            self.in_script = True
            self.script = ""
        if tag == 'details':
            self.active_details.append(attrs.get('id'))
            if attrs.get('class') == 'capability':
                self.details[attrs['id']] = {}
        if tag == 'summary':
            self.summary = []
        if tag == 'tr' and 'data-row' in attrs:
            self.row = {'id': attrs['data-row'], 'cells': []}
        if tag == 'td':
            self.cell = []
        if tag in ('dt', 'dd'):
            self.field = []

    def handle_data(self, data):
        if self.in_script:
            self.script += data
        if self.summary is not None:
            self.summary.append(data)
        if self.cell is not None:
            self.cell.append(data)
        if self.field is not None:
            self.field.append(data)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.scripts.append(self.script)
            self.in_script = False
        if tag == 'summary' and self.summary is not None:
            if self.active_details and self.active_details[-1] is None:
                self.module_summaries.append(''.join(self.summary))
            self.summary = None
        if tag == 'details':
            self.active_details.pop()
        if tag == 'dt':
            self.term = ''.join(self.field)
            self.field = None
        if tag == 'dd':
            if self.active_details and self.active_details[-1] in self.details:
                self.details[self.active_details[-1]][self.term] = ''.join(self.field)
            self.field = None
        if tag == 'td':
            if self.row is not None:
                self.row['cells'].append(''.join(self.cell))
            self.cell = None
        if tag == 'tr' and self.row is not None:
            self.tables.append(self.row)
            self.row = None


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'assets/example.json').read_text())

    def test_example_valid_and_counts(self):
        doc = Document(renderer.render(self.data))
        self.assertEqual(len(doc.details), 3)
        self.assertEqual(len(doc.tables), 3)
        self.assertEqual(len(doc.module_summaries), 2)
        self.assertIn('必要 2 · 条件必要 0 · 扩展 0', doc.module_summaries[0])
        self.assertIn('已完成 0 · 部分完成 1 · 未完成 0 · 尚未核实 1', doc.module_summaries[0])
        self.assertIn('沿用现有 1 · 已确认要做 1 · 当前不做 0 · 尚未决定 0', doc.module_summaries[0])
        self.assertIn('必要 0 · 条件必要 1 · 扩展 0', doc.module_summaries[1])
        self.assertIn('2 个模块 · 3 项能力', renderer.render(self.data))

    def test_table_and_details_share_every_semantic_field(self):
        doc = Document(renderer.render(self.data))
        capabilities = {c['id']: c for m in self.data['modules'] for c in m['capabilities']}
        for row in doc.tables:
            c = capabilities[row['id']]
            fields = doc.details['cap-' + c['id']]
            self.assertEqual(row['cells'], [c['name'], fields['有什么用'], fields['是否必要'], c['status'], fields['建设决定／采用方式'], c['current']])
            self.assertEqual(fields['是什么'], c['definition'])
            self.assertEqual(fields['完成情况'], c['status'] + '；' + c['current'])
            self.assertIn(c['evidence'][0]['source'], fields['依据与限制'])

    def test_condition_not_lost_in_table_or_detail(self):
        doc = Document(renderer.render(self.data))
        row = doc.tables[-1]
        condition = self.data['modules'][1]['capabilities'][0]['necessity']['condition']
        self.assertIn('条件必要：' + condition, row['cells'][2])
        self.assertEqual(row['cells'][2], doc.details['cap-message-reminder']['是否必要'])

    def test_conditional_module_summary_retains_its_condition(self):
        module = self.data['modules'][1]
        module['necessity'] = {'kind': '条件必要', 'condition': '有自动提醒产品时', 'reason': '提醒产品需要明确发送职责。'}
        doc = Document(renderer.render(self.data))
        self.assertIn('条件必要：有自动提醒产品时', doc.module_summaries[1])
        self.assertIn('提醒产品需要明确发送职责。', doc.module_summaries[1])

    def test_status_decision_combinations_are_independent(self):
        for status in renderer.STATUSES:
            for decision in renderer.DECISIONS:
                with self.subTest(status=status, decision=decision):
                    cap = self.data['modules'][0]['capabilities'][0]
                    cap.update(status=status, decision=decision)
                    self.assertIs(renderer.validate(self.data), self.data)

    def test_all_project_text_is_escaped_and_script_is_constant(self):
        baseline_script = Document(renderer.render(self.data)).scripts
        payload = '</script><img src=x onerror="alert(1)"> & \' " $title ${modules} \u2028\u2029'

        def replace_text(value, key=''):
            # Keep the structural fields valid; attack all free-text fields.
            fixed = {'id', 'from', 'to', 'kind', 'placement', 'status', 'decision', 'condition'}
            if isinstance(value, dict):
                return {k: replace_text(v, k) for k, v in value.items()}
            if isinstance(value, list):
                return [replace_text(v, key) for v in value]
            if isinstance(value, str) and key not in fixed:
                return payload
            return value

        self.data = replace_text(self.data)
        self.data['modules'][1]['capabilities'][0]['necessity']['condition'] = payload
        result = renderer.render(self.data)
        doc = Document(result)
        self.assertIn(escape(payload, quote=True), result)
        self.assertNotIn('<img', result)
        self.assertEqual(doc.scripts, baseline_script)
        self.assertEqual(len(doc.scripts), 1)
        self.assertNotIn(payload, doc.scripts[0])
        self.assertNotIn('innerHTML', doc.scripts[0].replace('no inline project JSON or innerHTML', ''))

    def test_anchors_are_unique_and_resolved(self):
        doc = Document(renderer.render(self.data))
        self.assertEqual(len(doc.ids), len(set(doc.ids)))
        for link in doc.links:
            self.assertTrue(link.startswith('#'))
            self.assertIn(link[1:], doc.ids)
        self.assertEqual({r['id'] for r in doc.tables}, {i[4:] for i in doc.details})

    def test_no_network_and_no_script_fallback_has_content(self):
        result = renderer.render(self.data)
        doc = Document(result)
        self.assertEqual(doc.external_resources, [])
        self.assertIn("default-src 'none'", result)
        self.assertIn('<noscript>', result)
        self.assertIn('手动展开', result)
        self.assertIn('class="tools" hidden', result)
        without_script = re.sub(r'<script>.*?</script>', '', result, flags=re.S)
        fallback = Document(without_script)
        self.assertEqual(len(fallback.tables), 3)
        self.assertEqual(len(fallback.details), 3)
        self.assertEqual(len(fallback.module_summaries), 2)

    def test_layout_not_fixed_to_example_number_or_groups(self):
        base = deepcopy(self.data['modules'][0])
        for count in (1, 4, 11):
            with self.subTest(count=count):
                self.data['externals'] = []
                self.data['modules'] = []
                for i in range(count):
                    module = deepcopy(base)
                    module['id'] = f'mod-{i}'
                    module['placement'] = list(renderer.PLACEMENTS)[i % 4]
                    for j, cap in enumerate(module['capabilities']):
                        cap['id'] = f'ability-{i}-{j}'
                    self.data['modules'].append(module)
                mains = [m['id'] for m in self.data['modules'] if m['placement'] == 'main']
                self.data['relations'] = [{'from': a, 'to': b, 'kind': '主链', 'action': '派发任务'} for a, b in zip(mains, mains[1:])]
                for m in self.data['modules']:
                    if m['placement'] == 'main':
                        continue
                    support = m['placement'] == 'support'
                    self.data['relations'].append({'from': m['id'] if support else 'mod-0', 'to': 'mod-0' if support else m['id'], 'kind': '支撑' if support else '数据' if m['placement'] == 'independent' else '按需', 'action': '按职责配合'})
                result = renderer.render(self.data)
                doc = Document(result)
                self.assertEqual(len(doc.module_summaries), count)
                self.assertEqual(len(doc.tables), count * 2)
                self.assertIn(f'{count} 个模块 · {count * 2} 项能力', result)
                self.assertIn('repeat(auto-fit,minmax(min(100%,300px),1fr))', result)
                self.assertNotIn('<svg', result)
                self.assertNotIn('viewBox', result)
                self.assertIn('overflow-x:auto', result)
                self.assertIn('@media(max-width:700px)', result)

    def test_invalid_inputs_fail_explicitly(self):
        mutations = [
            (lambda d: d.update(title=''), 'title'),
            (lambda d: d.update(extra='typo'), '字段不匹配'),
            (lambda d: d.update(modules=[]), '至少一个模块'),
            (lambda d: d.update(workflows={}), 'workflows'),
            (lambda d: d['workflows'][0].update(steps=['alone']), '至少 2'),
            (lambda d: d['modules'][0].update(capabilities=[]), '模块必须含能力'),
            (lambda d: d['modules'][0].update(placement='nonsense'), 'placement'),
            (lambda d: d['modules'][0].update(id='borrow-request'), 'ID 重复'),
            (lambda d: d['modules'][0].update(id='\" onclick=bad'), 'ID 只允许'),
            (lambda d: d['modules'][0]['capabilities'][0].update(status=[]), 'status'),
            (lambda d: d['modules'][0]['capabilities'][0].update(decision='默认要做'), 'decision'),
            (lambda d: d['modules'][0]['capabilities'][0].update(evidence=[]), '至少一条依据'),
            (lambda d: d['modules'][0]['capabilities'][0].pop('definition'), '字段不匹配'),
            (lambda d: d['modules'][0]['capabilities'][0].update(current='\u0000'), '控制字符'),
            (lambda d: d['modules'][1]['capabilities'][0]['necessity'].update(condition=''), 'condition'),
            (lambda d: d['modules'][0]['capabilities'][0]['necessity'].update(condition='只在某时'), '非条件必要'),
            (lambda d: d['modules'][1]['capabilities'][0]['necessity'].update(kind='必要', condition=''), '非全局必要模块'),
            (lambda d: d['relations'][0].update(to='absent'), '引用已有'),
            (lambda d: d['relations'][0].update(to='lending'), '不能连接自身'),
            (lambda d: d['relations'].append(deepcopy(d['relations'][0])), '关系重复'),
            (lambda d: d.update(relations=[]), '悬空子卡'),
            (lambda d: d['externals'][0].update(id='lending'), 'ID 重复'),
        ]
        for mutate, message in mutations:
            with self.subTest(message=message):
                data = deepcopy(self.data)
                mutate(data)
                with self.assertRaisesRegex(ValueError, message):
                    renderer.validate(data)
        for wrong in (None, [], 'text', 12):
            with self.assertRaisesRegex(ValueError, '必须是对象'):
                renderer.validate(wrong)

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory(prefix='wl-atlas-test-', dir='/tmp') as tmp:
            path = Path(tmp) / 'duplicate.json'
            path.write_text('{"title":"a", "title":"b"}')
            with self.assertRaisesRegex(ValueError, '字段重复'):
                renderer.load(path)

    def test_cli_valid_check_render_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory(prefix='wl-atlas-test-', dir='/tmp') as tmp:
            source = Path(tmp) / 'data.json'
            source.write_text(json.dumps(self.data, ensure_ascii=False))
            report = Path(tmp) / 'candidate.html'
            cmd = [sys.executable, '-B', str(ROOT / 'scripts/render.py'), str(source)]
            checked = subprocess.run(cmd + ['--check'], capture_output=True, text=True)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertFalse(report.exists())
            first = subprocess.run(cmd + [str(report)], capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            original = report.read_bytes()
            second = subprocess.run(cmd + [str(report)], capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(report.read_bytes(), original)
            self.assertEqual(json.loads(source.read_text()), self.data)

    def test_cli_invalid_json_or_model_does_not_create_output(self):
        with tempfile.TemporaryDirectory(prefix='wl-atlas-test-', dir='/tmp') as tmp:
            source, report = Path(tmp) / 'data.json', Path(tmp) / 'out.html'
            for content in ('{"title":', '[]', '{"title": "a", "title": "b"}'):
                with self.subTest(content=content):
                    source.write_text(content)
                    result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/render.py'), str(source), str(report)], capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('错误：', result.stderr)
                    self.assertFalse(report.exists())


if __name__ == '__main__':
    unittest.main()
