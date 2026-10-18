# 项目入口文件模板索引（CLAUDE.md / AGENTS.md）

快速选择适合你的项目的模板：

| 模板 | 适用场景 |
|------|---------|
| [Java / Spring Boot](template-java-springboot.md) | 企业级 RESTful API 后端 |
| [React / Next.js](template-react-nextjs.md) | 全栈 Web 应用（App Router） |
| [Python / FastAPI](template-python-fastapi.md) | 高性能 Python API 服务 |
| [Go 微服务](template-go-microservice.md) | Go 语言微服务后端 |
| [Vue 3](template-vue3.md) | 企业管理后台前端 |
| [Node.js / Express](template-node-express.md) | Node.js RESTful API |
| [Monorepo 全栈](template-monorepo.md) | 前后端同仓库的全栈项目 |
| [Flutter](template-flutter.md) | 跨平台移动应用 |
| [数据分析 / Jupyter](template-jupyter.md) | 数据科学、机器学习项目 |
| [极简通用](template-minimal.md) | 任何项目快速起步 |

## 目录结构

- `template-*.md` — 10 个技术栈模板（历史材料，未在本轮验证）
- [samples/](samples) — 用户级 / 项目级入口文件样例
- [rules/](rules) — 按文件路径触发的分层规则样例（`.claude/rules/`）
- 配套生成提示词与四层 steering 方法见 [best_practices 记录](../../best_practices/2026-06-10-项目入口规则-生成CLAUDE.md与AGENTS.md提示词/README.md)

## 使用方式

1. 根据项目类型选择对应模板
2. 复制到项目根目录，重命名为 `CLAUDE.md`（或 `AGENTS.md`）
3. 按需修改技术栈版本号、目录结构等细节
4. 随着项目发展持续更新；路径专属约束建议下沉到项目的 `.claude/rules/`，样例见本目录 `rules/`
