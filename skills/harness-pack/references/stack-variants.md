# 技术栈变体参考（技能步骤适配用）

模板技能（尤其 `skills/编码实现/SKILL.md`）中的分层名与步骤顺序是 **Java/Spring 视角** 的默认值。生成草案时**按目标技术栈选用本节对应变体替换**，方法论顺序不变（模型 → 数据访问 → 业务 → 消息 → 入口），名词跟着项目实际分层走。项目栈不在下表时，按同样思路自拟并标 ❓。

## Java / Spring Boot（模板默认，无需替换）

- 分层：`Model(entity/dto/vo) → Repository → Service(+impl) → MQ(producer/consumer) → Controller`
- 依赖注入：构造器注入，禁字段注入
- 事务：`@Transactional` 显式 `rollbackFor`
- 响应：统一 `{code, message, data}`

## Python / FastAPI（不用 Django）

- 分层：`schemas(Pydantic) → repository → service → MQ(如适用) → router(APIRouter)`
- 依赖注入：FastAPI `Depends`，禁全局单例里藏请求状态
- 事务：service 层显式管理（session commit/rollback 边界清晰），禁路由函数里直接写库
- 响应：统一响应模型（Pydantic BaseModel 包裹 code/message/data）
- 异步：路由/服务可 async，但**阻塞 IO 必须丢线程池**（`run_in_threadpool`），禁在 event loop 里直接调阻塞客户端
- 类型：全量类型标注，禁裸 `dict` 传业务数据（用 Pydantic 模型）

## TypeScript / Next.js 全栈（或 Node 后端）

- 前端分层：`types → api 封装层 → composables/stores → components/views`
- 后端分层（如项目含 Node 后端）：`types(zod) → repository → service → router(路由处理器)`
- 类型：全量严格模式，未知结构用 `unknown` + 收窄，禁 `any` 逃逸
- 数据校验：边界处用 zod（或等价库）校验外部输入，禁信任前端传来的结构
- 响应：统一 `{code, message, data}`，前端 api 层统一解包与错误处理

## 适配规则

1. bootstrap 生成草案时，只把**目标栈对应的一套**写入项目技能文件，其余栈内容不复制进项目（保持生成物精简）。
2. 步骤名替换后通读一遍该技能，删除栈不适用的小节（如纯前端项目删除后端步骤、无 MQ 的项目删 MQ 步）。
3. 混合栈（如 Next.js + Python 后端）：前后端分别适配，技能里前后段落各取对应变体。
