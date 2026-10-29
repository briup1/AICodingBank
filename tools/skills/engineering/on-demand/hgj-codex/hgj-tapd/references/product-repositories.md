# HGJ TAPD 产品知识库登记表

本表只登记 TAPD 项目与本机产品 Git 知识库的只读关联，不包含凭证。

| workspace_id | TAPD 项目 | 产品知识库 | 本地映射 | 仓库级说明 |
|---|---|---|---|---|
| `44973445` | 询报价项目 | `/home/weilan/workdir/remote_project/ai-agent` | `.agents/automation/.project02-tapd-map.json` | `AGENTS.md` |

## 使用规则

- 只有 workspace 命中本表时，才访问对应产品知识库。
- 产品知识库默认只读：不执行 `git pull/fetch/checkout/switch/merge`，不修改文件，不运行写入型自动化。
- 进入仓库后先读取根 `AGENTS.md`，遵守仓库中的事实优先级、文档边界和冻结规则。
- TAPD 提供当前进度、负责人、优先级、评论和外部来源；产品仓库提供详细业务规则、验收标准、原型和需求演进。
- 两侧冲突时分别报告，不用 TAPD 状态覆盖产品业务规则，也不用本地草稿状态覆盖 TAPD 当前进度。
- 本机路径不存在、映射失败或仓库结构不符合预期时，只返回 TAPD 信息并说明未关联成功，不猜测。

## 读取顺序（workspace 44973445）

```text
TAPD 需求详情与评论
  ↓
隐藏映射：TAPD 数字 ID → 本地 R-* 需求 ID
  ↓
对应单条需求 PRD
  ↓
所属周 PRD 总览
  ↓
根 PRD-总览中的需求行与演进关系
  ↓
单条 PRD 明确关联的需求
  ↓
仅在判断存量规则时读取 PRD-当前线上完整版
```

禁止把隐藏映射中的数字 ID 写入产品 PRD、总览或工作记忆。
