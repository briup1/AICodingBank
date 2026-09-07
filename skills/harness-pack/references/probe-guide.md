# 项目探查手册（harness-bootstrap-legacy 专用）

探查目标：从老项目代码库中反推出事实，供生成 harness 草案使用。**只读，不改任何文件。**

## 一、探查什么（四层事实）

| 层 | 内容 | 主要信号源 |
|----|------|-----------|
| 技术栈 | 语言、框架、依赖、存储/中间件 | 依赖清单、构建配置 |
| 工程结构 | 目录组织、分层方式、模块划分 | 目录树、入口文件 |
| 编码惯例 | 命名、异常处理、日志、注释风格 | 代表性源文件、lint 配置 |
| 红线候选 | 项目反复遵守/反复出事的模式 | grep 模式扫描、TODO/FIXME、CR 记录 |

## 二、技术栈信号文件（按优先级读）

`package.json` / `pom.xml` / `build.gradle` / `go.mod` / `requirements.txt` / `pyproject.toml` / `Cargo.toml` / `Gemfile` + `docker-compose.yml` / `Dockerfile` / CI 配置 + `README*` / `AGENTS.md` / `CLAUDE.md` / `docs/`。

## 三、惯例挖掘通用清单

1. 读 3-5 个**代表性源文件**（一个接口/路由、一个核心业务、一个工具类），归纳命名、分层、错误处理、日志风格。
2. 读 lint / formatter 配置（`.eslintrc` / `checkstyle` / `ruff.toml` / `.editorconfig`），配置里已有的硬规则直接进 `rules/编码规范.md`。
3. 搜 `TODO|FIXME|HACK|XXX`，高频出现处往往是规则缺失区。
4. 搜代码评审遗留：`review` / `CR` 相关文档或注释。

## 四、红线候选挖掘（grep 模式，按栈选用）

| 关注点 | 搜索模式（示例） |
|--------|------------------|
| 浮点金额 | `float|double|Float|Double|BigDecimal`（结合字段名 `amount\|price\|money`） |
| 字段注入 | `@Autowired`（非构造器位置）/ `@Inject` 字段 |
| 缓存键 | Redis/Cache 调用点的字符串前缀是否统一 |
| 危险命令 | `KEYS \*` / `FLUSHALL` / `rm -rf` |
| 异常透出 | `throw new Exception` / `e.printStackTrace` / 裸 `raise` |
| 硬编码 | 魔法数字/字符串、硬编码 IP/密钥痕迹 |
| 事务 | `@Transactional` 是否声明回滚范围 |

命中有两种解读，生成红线时分好类：到处都遵守 → ✅ 写成规则；到处都违反 → ⚠️ 写成规则并标技术债。

## 五、多目标并发探查（重要）

**触发条件**：出现以下任一情况时，不要单线程逐个探查，改用并发子 Agent：

- 前后端分离为**多个仓库/目录**（如 `xxx-frontend/` + `xxx-backend/`）
- monorepo 中**多个相对独立的包/模块**
- 项目含**异构技术栈**（如 Java 后端 + Python 脚本 + TS 前端）

**协调方式**（使用宿主支持的子 Agent / Task 机制）：

1. 主 Agent 按目标拆分，每个子 Agent 分配**一个探查目标**。
2. 所有子 Agent 使用**同一份探查清单**（本文二~四节），输出**统一格式**：
   ```markdown
   ## 目标：<路径>
   - 技术栈：<...>
   - 结构：<目录分层 + 一句话职责>
   - 惯例：<命名/异常/日志等，附文件证据>
   - 红线候选：<模式 → 遵守|违反，附出现次数>
   - 问题：<规则缺失区、债务点>
   ```
3. 主 Agent 合并各报告：统一技术栈表、归并同类红线（冲突时保留冲突并标注，交给用户在确认阶段裁决）。
4. 子 Agent 只读探查，明确禁止修改文件。

**单目标项目**：直接按本文清单顺序探查，不拆子 Agent（省开销）。

**宿主不支持子 Agent 时**：退回串行逐目标探查（一个目标探查完再下一个），各目标输出格式与主 Agent 合并方式不变。
