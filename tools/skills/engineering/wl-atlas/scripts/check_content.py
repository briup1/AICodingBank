#!/usr/bin/env python3
"""Heuristic review prompts, not a semantic approval or a necessity classifier."""
import argparse
from pathlib import Path
import re
import sys

from render import load, validate


def content_warnings(data):
    validate(data)
    warnings = []
    for module in data['modules']:
        for item in [module] + module['capabilities']:
            id_ = item['id']
            reason = item['necessity']['reason']
            if re.search(r'已确认|已选择|决定建设|选择人工|负责人选择|已开发|已实现', reason):
                warnings.append(f'{id_}.necessity.reason：可能用决定/现状替代职责理由，请独立核对必要性，勿自动升降级。')
            for field in ('name', 'definition', 'purpose', 'responsibility'):
                value = item.get(field, '')
                # English technical terms outside explanatory parentheses need a human look.
                plain = re.sub(r'（[^）]*）|\([^)]*\)', '', value)
                if re.search(r'\b[A-Za-z][A-Za-z0-9_-]{2,}\b', plain):
                    warnings.append(f'{id_}.{field}：存在括号外英文词，请先写白话操作效果，技术名放括号或依据；产品名可人工放行。')
            evidence = '；'.join(entry['finding'] for entry in item.get('evidence', []))
            implementation = item.get('current', '') + '；' + evidence
            if item.get('status') in ('部分完成', '尚未核实') and re.search(r'已有|已实现|已开发', implementation) and re.search(r'本轮.{0,8}(?:未|没)|未(?:复测|重验|覆盖全部)', implementation):
                warnings.append(f'{id_}.status：未复测降级风险；请按目标范围的实现依据核对，验证限制另记。真实行为缺口或目标本身要求的验证缺失仍可为差距；不自动升为已完成。')
            if item.get('decision') == '沿用现有' and re.search(r'人工', item.get('approach', '')) and re.search(r'缺|待补|还需|不完整|未齐', item.get('current', '')):
                warnings.append(f'{id_}：沿用人工方式但仍有缺口，请对照决定来源，确认是否另有质量补齐能力，勿抹掉已确认工作。')
    for index, relation in enumerate(data['relations']):
        plain = re.sub(r'（[^）]*）|\([^)]*\)', '', relation['action'])
        if re.search(r'\b[A-Za-z][A-Za-z0-9_-]{2,}\b', plain):
            warnings.append(f'relations[{index}].action：先说谁对什么做什么，技术名放括号或依据。')
    return warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data', type=Path)
    args = parser.parse_args()
    try:
        warnings = content_warnings(load(args.data))
    except (ValueError, OSError) as exc:
        print(f'错误：{exc}', file=sys.stderr)
        return 1
    print('人工必查：先盘点已存在但不扩建的入口/调度/人工确认/用量归属；主链标题不能代替能力定义。')
    print('人工必查：可选领域保留来源中的具体职责与未决项；按成立条件核对生命周期/权限/失败/质量/责任，不自动变必建。')
    print('人工必查：合并后逐义映射来源，核对对象、动作、结果；不靠同名词合并，不用新 UI 替换原职责。')
    print('人工必查：必要性来自职责；人工采用方式与已确认质量补齐分别核对；定义先白话后术语。')
    for warning in warnings:
        print('提示：' + warning)
    print(f'共 {len(warnings)} 条启发式提示；零提示不代表语义完整或审核通过，不修改数据、不自动裁决。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
