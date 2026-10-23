#!/usr/bin/env python3
"""Validate one atlas data file and render an offline HTML report (stdlib only)."""
import argparse
from collections import Counter
from html import escape
import json
from pathlib import Path
import re
import sys
from string import Template

STATUSES = {"已完成": "existing", "部分完成": "partial", "未完成": "missing", "尚未核实": "unknown"}
DECISIONS = ("沿用现有", "已确认要做", "当前不做", "尚未决定")
PLACEMENTS = {"main": "主链模块", "branch": "按需分支", "independent": "独立数据或辅助链", "support": "贯穿式支撑"}
RELATIONS = ("主链", "按需", "数据", "支撑")
ROOT = Path(__file__).resolve().parent.parent


def require(ok, path, message):
    if not ok:
        raise ValueError(f"{path}: {message}")


def obj(value, keys, path):
    require(isinstance(value, dict), path, "必须是对象")
    require(set(value) == set(keys.split()), path, "字段不匹配；应为 " + keys)


def text(value, path):
    require(isinstance(value, str) and bool(value.strip()), path, "必须是非空字符串")
    require(not any(ord(c) < 32 and c not in '\n\t\r' for c in value), path, "含非法控制字符")


def texts(value, path, minimum=1):
    require(isinstance(value, list) and len(value) >= minimum, path, f"必须是数组，至少 {minimum} 项")
    for index, item in enumerate(value):
        text(item, f"{path}[{index}]")


def choice(value, choices, path):
    require(isinstance(value, str) and value in choices, path, "应为 " + " / ".join(choices))


def necessity(value, path):
    obj(value, "kind reason condition", path)
    choice(value["kind"], ("必要", "条件必要", "扩展"), path + ".kind")
    text(value["reason"], path + ".reason")
    if value["kind"] == "条件必要":
        text(value["condition"], path + ".condition")
    else:
        require(value["condition"] == "", path + ".condition", "非条件必要时应为空字符串；有条件请使用条件必要")


def validate(data):
    obj(data, "title date goal scope workflows modules externals relations boundaries questions", "atlas")
    for key in ("title", "date", "goal", "scope"):
        text(data[key], key)
    texts(data["boundaries"], "boundaries")
    texts(data["questions"], "questions", 0)
    for key in ("workflows", "modules", "externals", "relations"):
        require(isinstance(data[key], list), key, "必须是数组")
    require(bool(data["modules"]) and bool(data["workflows"]), "atlas", "至少一个模块和一条操作链")
    for i, flow in enumerate(data["workflows"]):
        obj(flow, "name steps", f"workflows[{i}]")
        text(flow["name"], f"workflows[{i}].name")
        texts(flow["steps"], f"workflows[{i}].steps", 2)
    ids = set()

    def identifier(value, path):
        require(isinstance(value, str) and bool(re.fullmatch(r"[a-z][a-z0-9-]*", value)), path, "ID 只允许小写字母开头、字母数字及连字符")
        require(value not in ids, path, "ID 重复")
        ids.add(value)

    node_ids = set()
    for i, module in enumerate(data["modules"]):
        p = f"modules[{i}]"
        obj(module, "id name responsibility necessity placement capabilities", p)
        identifier(module["id"], p + ".id")
        node_ids.add(module["id"])
        for key in ("name", "responsibility"):
            text(module[key], p + "." + key)
        necessity(module["necessity"], p + ".necessity")
        choice(module["placement"], PLACEMENTS, p + ".placement")
        require(isinstance(module["capabilities"], list) and bool(module["capabilities"]), p, "模块必须含能力")
        for j, cap in enumerate(module["capabilities"]):
            q = f"{p}.capabilities[{j}]"
            obj(cap, "id name definition purpose necessity status current decision approach evidence", q)
            identifier(cap["id"], q + ".id")
            for key in ("name", "definition", "purpose", "current", "approach"):
                text(cap[key], q + "." + key)
            necessity(cap["necessity"], q + ".necessity")
            if module["necessity"]["kind"] != "必要":
                require(cap["necessity"]["kind"] != "必要", q + ".necessity", "非全局必要模块内的必需能力应写为条件必要，并明确适用条件")
            choice(cap["status"], STATUSES, q + ".status")
            choice(cap["decision"], DECISIONS, q + ".decision")
            require(isinstance(cap["evidence"], list) and bool(cap["evidence"]), q + ".evidence", "至少一条依据；未核实也需说明核对范围和缺口")
            for k, evidence in enumerate(cap["evidence"]):
                ep = f"{q}.evidence[{k}]"
                obj(evidence, "source finding", ep)
                text(evidence["source"], ep + ".source")
                text(evidence["finding"], ep + ".finding")
    for i, external in enumerate(data["externals"]):
        p = f"externals[{i}]"
        obj(external, "id name responsibility", p)
        identifier(external["id"], p + ".id")
        node_ids.add(external["id"])
        text(external["name"], p + ".name")
        text(external["responsibility"], p + ".responsibility")
    placements = {m["id"]: m["placement"] for m in data["modules"]}
    seen_relations = set()
    connected = set()
    for i, relation in enumerate(data["relations"]):
        p = f"relations[{i}]"
        obj(relation, "from to kind action", p)
        for key in ("from", "to"):
            require(isinstance(relation[key], str) and relation[key] in node_ids, p + "." + key, "必须引用已有模块或外部系统 ID")
            connected.add(relation[key])
        require(relation["from"] != relation["to"], p, "不能连接自身")
        choice(relation["kind"], RELATIONS, p + ".kind")
        text(relation["action"], p + ".action")
        source, target = placements.get(relation["from"]), placements.get(relation["to"])
        if relation["kind"] == "主链":
            require(source == target == "main", p, "主链关系两端必须是 main 模块")
        if relation["kind"] == "支撑":
            require(source == "support", p, "支撑关系必须由 support 模块指向受支撑节点")
        else:
            require("support" not in (source, target), p, "支撑节点只能使用支撑关系，不能串入请求处理顺序")
        if relation["kind"] == "数据":
            require("independent" in (source, target), p, "独立数据关系至少一端应为 independent 模块")
        edge = (relation["from"], relation["to"], relation["kind"])
        require(edge not in seen_relations, p, "关系重复；同端点同类型的动作请合并说明")
        seen_relations.add(edge)
    main_chain(data)  # Reject unsupported topology instead of inventing connectors.
    branch_ids = {m["id"] for m in data["modules"] if m["placement"] == "branch"}
    external_ids = {n["id"] for n in data["externals"]}
    parents = Counter()
    for i, relation in enumerate(data["relations"]):
        if relation["kind"] == "按需":
            require(placements.get(relation["from"]) == "main" and
                    relation["to"] in branch_ids | external_ids,
                    f"relations[{i}]", "按需子卡仅支持 main → branch/外部系统；多层或反向调用请调整职责分层，不伪造连线")
            parents[relation["to"]] += 1
    require(all(parents[n] == 1 for n in branch_ids), "relations",
            "每个 branch 必须有且仅有一个主链父节点；不支持多入、循环或悬空子卡")
    require(all(parents[n] <= 1 for n in external_ids), "relations",
            "外部系统不支持多个按需父节点；真实共享调用超出本模板范围，不得改成数据/支撑关系绕过限制")
    require(len(node_ids) == 1 or node_ids <= connected, "relations", "存在未解释协作关系的模块或外部系统")
    return data


def e(value):
    return escape(value, quote=True)


def necessity_label(value):
    if value["kind"] == "条件必要":
        return f"条件必要：{value['condition']}"
    return value["kind"]


def necessity_full(value):
    return necessity_label(value) + "；" + value["reason"]


def status_html(value):
    return f'<span class="status {STATUSES[value]}">{e(value)}</span>'


def counts(capabilities):
    status = Counter(c["status"] for c in capabilities)
    decisions = Counter(c["decision"] for c in capabilities)
    necessary = Counter(c["necessity"]["kind"] for c in capabilities)
    return (
        " · ".join(f"{k} {necessary[k]}" for k in ("必要", "条件必要", "扩展")),
        " · ".join(status_html(k) + f" {status[k]}" for k in STATUSES),
        " · ".join(f"{k} {decisions[k]}" for k in DECISIONS),
    )


def capability_html(cap):
    fields = (
        ("是什么", cap["definition"]), ("有什么用", cap["purpose"]),
        ("是否必要", necessity_full(cap["necessity"])),
        ("完成情况", cap["status"] + "；" + cap["current"]),
        ("建设决定／采用方式", cap["decision"] + "；" + cap["approach"]),
    )
    terms = "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in fields)
    evidence = "".join(f'<li><span>{e(item["source"])}</span>：{e(item["finding"])}</li>' for item in cap["evidence"])
    return f'''<details class="capability" id="cap-{cap['id']}"><summary><span class="cap-name">{e(cap['name'])}</span>{status_html(cap['status'])}<span class="decision">{e(cap['decision'])}</span></summary>
<dl>{terms}<dt>依据与限制</dt><dd><ul>{evidence}</ul></dd></dl></details>'''


def module_html(module, number):
    caps = module["capabilities"]
    necessary, status, decisions = counts(caps)
    groups = []
    for kind in ("必要", "条件必要", "扩展"):
        members = [c for c in caps if c["necessity"]["kind"] == kind]
        if members:
            groups.append(f'<h4>{kind}能力</h4>' + "".join(capability_html(c) for c in members))
    return f'''<div class="module-shell" id="node-{module['id']}"><details class="module"><summary>
<span class="number">{number:02d}</span><span class="module-heading"><strong>{e(module['name'])}</strong><span class="scope">{e(necessity_label(module['necessity']))}</span>
<span class="responsibility">{e(module['responsibility'])}</span><span class="necessity-reason">{e(module['necessity']['reason'])}</span>
<span class="module-count">{necessary}</span><span class="module-progress">{status}</span><span class="module-decisions">{decisions}</span></span></summary>
<div class="module-content">{''.join(groups)}</div></details></div>'''


def table_html(module):
    rows = []
    for cap in module["capabilities"]:
        cells = [f'<a href="#cap-{cap["id"]}" data-cap="cap-{cap["id"]}">{e(cap["name"])}</a>',
                 e(cap["purpose"]), e(necessity_full(cap["necessity"])), status_html(cap["status"]),
                 e(cap["decision"] + "；" + cap["approach"]), e(cap["current"])]
        rows.append(f'<tr data-row="{cap["id"]}">' + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    headings = "".join(f'<th scope="col">{h}</th>' for h in ("能力", "用途", "必要性", "完成情况", "建设决定／采用方式", "已有基础与差距"))
    return f'''<section class="table-module"><h3 id="table-{module['id']}">{e(module['name'])}</h3><p>{e(module['responsibility'])}</p>
<div class="table-scroll" tabindex="0" role="region" aria-labelledby="table-{module['id']}"><table><caption>{e(module['name'])}能力表</caption><thead><tr>{headings}</tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>'''


def main_chain(data):
    """Order one simple chain; no coordinates, graph engine or guessed edges."""
    ids = [m["id"] for m in data["modules"] if m["placement"] == "main"]
    edges = [r for r in data["relations"] if r["kind"] == "主链"]
    incoming = Counter(r["to"] for r in edges)
    outgoing = Counter(r["from"] for r in edges)
    require(len(edges) == max(0, len(ids) - 1) and
            all(incoming[n] <= 1 and outgoing[n] <= 1 for n in ids),
            "relations", "main 必须连成一条主链，不支持多入、分叉或循环")
    starts = [n for n in ids if not incoming[n]]
    require(not ids or len(starts) == 1, "relations", "主链含循环或断裂")
    next_node = {r["from"]: r["to"] for r in edges}
    ordered = []
    node = starts[0] if starts else None
    while node is not None and node not in ordered:
        ordered.append(node)
        node = next_node.get(node)
    require(len(ordered) == len(ids) and node is None, "relations", "主链含循环或断裂")
    return ordered


def architecture_html(data):
    nodes = {n["id"]: n for n in data["modules"] + data["externals"]}
    numbers = {m["id"]: i for i, m in enumerate(data["modules"], 1)}
    relations = data["relations"]

    def card(id_):
        node = nodes[id_]
        if id_ in numbers:
            return module_html(node, numbers[id_])
        return f'<article id="node-{id_}" class="external"><h4>{e(node["name"])}</h4><p>{e(node["responsibility"])}</p><small>外部系统 · 不计入本项目能力</small></article>'

    def connection(r, style):
        return f'<div class="{style}" data-from="{r["from"]}" data-to="{r["to"]}"><a href="#node-{r["from"]}">{e(nodes[r["from"]]["name"])}</a> → {e(r["action"])} → <a href="#node-{r["to"]}">{e(nodes[r["to"]]["name"])}</a></div>'

    parts = ['<div class="main-chain">']
    for id_ in main_chain(data):
        incoming = next((r for r in relations if r["kind"] == "主链" and r["to"] == id_), None)
        if incoming:
            parts.append(connection(incoming, "connector"))
        parts.append(f'<section class="chain-step" data-step="{id_}">{card(id_)}')
        children = [r for r in relations if r["kind"] == "按需" and r["from"] == id_]
        if children:
            parts.append(f'<div class="branches" aria-label="{e(nodes[id_]["name"])}的按需分支">')
            for r in children:
                parts.append(f'<div class="branch" data-parent="{id_}" data-child="{r["to"]}">{connection(r, "branch-action")}{card(r["to"])}</div>')
            parts.append('</div>')
        parts.append('</section>')
    parts.append('</div>')
    for placement in ("independent", "support"):
        members = [m for m in data["modules"] if m["placement"] == placement]
        if members:
            parts.append(f'<section class="placement {placement}"><h3>{PLACEMENTS[placement]} · 非请求处理顺序</h3>' + ''.join(card(m['id']) for m in members) + '</section>')
    attached = {r["to"] for r in relations if r["kind"] == "按需"}
    others = [x for x in data["externals"] if x["id"] not in attached]
    if others:
        parts.append('<section class="placement"><h3>独立数据/支撑关联的外部系统 · 见下方关系行</h3>' + ''.join(card(x['id']) for x in others) + '</section>')
    for kind in ("数据", "支撑"):
        rows = [connection(r, "relation-row") for r in relations if r["kind"] == kind]
        if rows:
            parts.append(f'<aside class="relation-notes"><h3>{kind}关系补充 · 非处理顺序连线</h3>{"".join(rows)}</aside>')
    return ''.join(parts)


def render(data):
    validate(data)
    modules = data["modules"]
    caps = [c for m in modules for c in m["capabilities"]]
    workflows = "".join(f'<p><strong>{e(w["name"])}</strong> {" → ".join(e(s) for s in w["steps"])}</p>' for w in data["workflows"])
    question_items = "".join(f'<li>{e(q)}</li>' for q in data["questions"])
    values = dict(
        title=e(data["title"]), date=e(data["date"]), goal=e(data["goal"]), scope=e(data["scope"]),
        count=f"{len(modules)} 个模块 · {len(caps)} 项能力", workflows=workflows,
        legend=" · ".join(status_html(s) for s in STATUSES),
        architecture=architecture_html(data),
        tables="".join(table_html(m) for m in modules),
        boundaries="".join(f'<li>{e(b)}</li>' for b in data["boundaries"]),
        questions=question_items or '<li>当前没有记录待确认问题；不代表所有场景都已验收。</li>',
    )
    return Template((ROOT / "assets" / "report.html").read_text(encoding="utf-8")).substitute(values)


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"JSON 字段重复：{key}")
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path)
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--check", action="store_true", help="仅验证数据，不生成报告")
    args = parser.parse_args()
    if not args.check and args.output is None:
        parser.error("生成报告时必须指定 output")
    try:
        data = load(args.data)
        validate(data)
        if args.check:
            print("数据校验通过（不代表语义审核或运行验收通过）")
        else:
            report = render(data)
            # Never overwrite an approved report or the input, even accidentally.
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(report)
            print(f"已生成：{args.output}")
    except (ValueError, OSError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
