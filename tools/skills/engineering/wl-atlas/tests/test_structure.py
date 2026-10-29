"""Small HTML topology checks: cards are the architecture, not a second directory."""
from copy import deepcopy
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('atlas_structure', ROOT / 'scripts/render.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


def fixture():
    data = json.loads((ROOT / 'assets/example.json').read_text())
    base = data['modules'][0]
    data['modules'] = []
    for id_, placement in [('execute', 'main'), ('entry', 'main'), ('knowledge', 'branch'),
                           ('model', 'branch'), ('documents', 'independent'), ('audit', 'support')]:
        module = deepcopy(base)
        module.update(id=id_, name=id_, placement=placement)
        for i, cap in enumerate(module['capabilities']):
            cap['id'] = f'{id_}-cap-{i}'
        data['modules'].append(module)
    data['externals'] = [{'id': 'business', 'name': '外部业务系统', 'responsibility': '保管正式记录'}]
    data['relations'] = [
        {'from': 'entry', 'to': 'execute', 'kind': '主链', 'action': '接收并派发任务'},
        {'from': 'execute', 'to': 'knowledge', 'kind': '按需', 'action': '检索获准资料'},
        {'from': 'execute', 'to': 'business', 'kind': '按需', 'action': '查询正式业务记录'},
        {'from': 'execute', 'to': 'model', 'kind': '按需', 'action': '请求推理'},
        {'from': 'documents', 'to': 'knowledge', 'kind': '数据', 'action': '解析并建立索引'},
        {'from': 'audit', 'to': 'execute', 'kind': '支撑', 'action': '保存运行线索'},
        {'from': 'audit', 'to': 'entry', 'kind': '支撑', 'action': '检查访问范围'},
    ]
    return data


class Structure(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.steps, self.children, self.cards, self.edges = [], {}, [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'data-step' in a:
            self.steps.append(a['data-step'])
        if 'data-child' in a:
            self.children[a['data-child']] = a['data-parent']
        if a.get('id', '').startswith('node-'):
            self.cards.append(a['id'][5:])
        if 'data-from' in a:
            self.edges.append((a['data-from'], a['data-to'], a['class']))


class StructureTests(unittest.TestCase):
    def test_main_order_and_children_are_driven_by_relations(self):
        data = fixture()
        result = renderer.render(data)
        structure = Structure(result)
        self.assertEqual(structure.steps, ['entry', 'execute'])
        self.assertEqual(structure.children, {'knowledge': 'execute', 'business': 'execute', 'model': 'execute'})
        self.assertEqual(len(structure.edges), len(data['relations']))
        self.assertEqual(len(structure.cards), len(set(structure.cards)))
        self.assertEqual(set(structure.cards), {n['id'] for n in data['modules'] + data['externals']})
        self.assertEqual(result.count('<details class="module">'), len(data['modules']))
        self.assertNotIn('<svg', result)
        self.assertNotIn('graph-scroll', result)
        self.assertNotIn('position:absolute', result.split('.main-chain')[0])
        self.assertLess(result.index('node-entry'), result.index('node-execute'))
        self.assertIn('接收并派发任务', result)
        self.assertIn('数据关系补充 · 非处理顺序连线', result)
        self.assertIn('支撑关系补充 · 非处理顺序连线', result)

    def test_changing_from_moves_the_actual_child_card(self):
        data = fixture()
        data['relations'][2]['from'] = 'entry'
        result = renderer.render(data)
        self.assertEqual(Structure(result).children['business'], 'entry')
        self.assertLess(result.index('id="node-business"'), result.index('id="node-execute"'))
        data['relations'][1]['to'], data['relations'][3]['to'] = 'model', 'knowledge'
        result = renderer.render(data)
        self.assertLess(result.index('id="node-model"'), result.index('id="node-knowledge"'))

    def test_reversed_main_edge_reorders_cards(self):
        data = fixture()
        data['relations'][0].update({'from': 'execute', 'to': 'entry'})
        self.assertEqual(Structure(renderer.render(data)).steps, ['execute', 'entry'])

    def test_unsupported_or_false_relations_fail(self):
        changes = [
            (lambda d: d['relations'][0].update(to='knowledge'), '主链.*main'),
            (lambda d: d['relations'][1].update(to='audit'), '支撑节点'),
            (lambda d: d['relations'][5].update({'from': 'execute', 'to': 'audit'}), '支撑关系.*support'),
            (lambda d: d['relations'][4].update({'from': 'entry', 'to': 'model'}), '数据关系.*independent'),
            (lambda d: d['relations'].append({'from': 'execute', 'to': 'entry', 'kind': '主链', 'action': '循环'}), '循环'),
            (lambda d: d['relations'][1].update({'from': 'knowledge', 'to': 'execute'}), '按需子卡仅支持'),
            (lambda d: d['relations'][2].update({'from': 'knowledge'}), '按需子卡仅支持'),
            (lambda d: d['relations'].append({'from': 'entry', 'to': 'knowledge', 'kind': '按需', 'action': '第二父节点'}), '有且仅有一个'),
            (lambda d: d['relations'].append({'from': 'entry', 'to': 'business', 'kind': '按需', 'action': '共享外部调用'}), '多个按需父节点'),
            (lambda d: d['relations'].append({'from': 'entry', 'to': 'execute', 'kind': '主链', 'action': '重复端点'}), '关系重复'),
            (lambda d: d['relations'].__delitem__(0), 'main.*连成一条'),
            (lambda d: d['relations'].__delitem__(1), '有且仅有一个'),
        ]
        for change, message in changes:
            with self.subTest(message=message):
                data = fixture()
                change(data)
                with self.assertRaisesRegex(ValueError, message):
                    renderer.render(data)

    def test_single_module_and_auxiliary_only_project(self):
        data = fixture()
        data['modules'] = [data['modules'][0]]
        data['externals'], data['relations'] = [], []
        self.assertEqual(Structure(renderer.render(data)).steps, ['execute'])
        data['modules'][0]['placement'] = 'independent'
        self.assertEqual(Structure(renderer.render(data)).cards, ['execute'])


if __name__ == '__main__':
    unittest.main()
