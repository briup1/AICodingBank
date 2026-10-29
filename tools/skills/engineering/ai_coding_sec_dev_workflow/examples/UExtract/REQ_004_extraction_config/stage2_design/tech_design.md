# 技术方案设计书

**需求ID**：REQ_004_extraction_config
**需求名称**：信息抽取配置功能
**版本**：v1.0
**创建时间**：2025-12-30T02:00:00Z

---

## 0. 现有项目架构分析

### 0.1 架构模式识别

**整体架构模式**：**经典三层架构 + 分层MVC**
- **API路由层**：FastAPI路由，处理HTTP请求/响应
- **业务逻辑层**：CRUD函数 + SQLModel数据验证
- **数据访问层**：SQLAlchemy ORM Session
- **数据模型层**：SQLModel类（Pydantic + SQLAlchemy）

**架构层次结构**：
```
┌─────────────────────────────────────────────┐
│   API层 (FastAPI Routes)                    │
│   backend/app/api/routes/                   │
│   - 处理HTTP请求/响应                        │
│   - 依赖注入认证和Session                    │
│   - 调用CRUD层                              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   业务逻辑层 (CRUD Functions)                │
│   backend/app/crud.py                        │
│   - 封装业务逻辑                            │
│   - 数据验证和转换                          │
│   - 调用ORM Session                         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   数据访问层 (SQLAlchemy ORM)                │
│   backend/app/core/db.py                     │
│   - Session管理                             │
│   - 数据库事务                              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   数据模型层 (SQLModel)                      │
│   backend/app/models.py                      │
│   - 表结构定义                              │
│   - 关系映射                                │
└─────────────────────────────────────────────┘
```

### 0.2 设计模式识别

**已使用的设计模式**：
- **依赖注入模式**：`backend/app/api/deps.py` - `CurrentUser`, `SessionDep`
- **数据传输对象模式**：`*Public`, `*Create`, `*Update` 模式（如 `UserPublic`, `ItemCreate`）
- **分页模式**：`skip/limit` 参数 + `*Public` 包装类（如 `ItemsPublic`）
- **认证中间件模式**：JWT Bearer Token 认证

**数据流向分析**：
```
前端组件 → TanStack Query → OpenAPI客户端 → FastAPI路由
    ↓
依赖注入 (认证+Session)
    ↓
CRUD函数 (业务逻辑)
    ↓
SQLAlchemy Session (ORM)
    ↓
PostgreSQL数据库
```

### 0.3 架构一致性要求

**新功能必须遵循的架构规范**：
1. **API层**：新增路由放到 `backend/app/api/routes/`，遵循RESTful规范
2. **CRUD层**：新增CRUD函数放到 `backend/app/crud.py` 或新建 `crud/` 模块
3. **模型层**：新增模型放到 `backend/app/models.py`
4. **配置层**：新增配置放到 `backend/app/core/config.py` 的 `Settings` 类
5. **前端层**：新增组件放到对应的 `components/` 目录，遵循现有组件模式

---

## 1. 方案概述

### 1.1 设计目标
在现有UExtract平台基础上，新增信息抽取配置功能，包括抽取字段、列表、模板管理和信息抽取执行，严格遵循项目现有的三层架构模式和代码风格。

### 1.2 设计原则
- **架构优先**：严格遵循现有三层架构，不引入新的架构模式
- **最小侵入**：扩展现有代码而非重写，保持架构一致性
- **资产复用**：最大化复用现有的CRUD模式、认证机制、分页模式
- **一致性**：保持与现有Items功能完全一致的实现方式

---

## 2. 功能实现设计（基于架构层次）

### 2.1 数据模型层：新增抽取相关模型

**架构层次归属**：数据模型层

**实现方式**：
参考 `backend/app/models.py` 中的 `User` 和 `Item` 模型，新增 `ExtractionField`、`ExtractionList`、`ExtractionTemplate` 三个SQLModel类，遵循相同的设计模式。

**架构一致性说明**：
- 遵循现有SQLModel的设计规范（基类、关系、索引）
- 参考 `User` ↔ `Item` 的一对多关系模式
- 保持与现有模型的命名风格一致

**可复用资产**：
- 复用 `backend/app/models.py:42` 的 `User` 模型作为 `owner_id` 的关联
- 复用 `backend/app/models.py:44` 的UUID主键模式
- 复用 `backend/app/models.py:46` 的 `Relationship` 模式

**新增代码**（数据模型层）：
- `backend/app/models.py` - 在现有文件中追加三个新模型类

---

### 2.2 API层：抽取字段/列表/模板CRUD接口

**架构层次归属**：API层

**实现方式**：
完全参考 `backend/app/api/routes/items.py` 的实现模式，为抽取字段、列表、模板分别创建RESTful CRUD接口。

**架构一致性说明**：
- 遵循现有FastAPI路由的定义规范
- 使用相同的依赖注入模式 (`CurrentUser`, `SessionDep`)
- 保持与 `items.py` 一致的分页参数 (`skip`, `limit`)
- 遵循相同的错误处理方式 (`HTTPException`)

**可复用资产**：
- 复用 `backend/app/api/deps.py` 的 `CurrentUser`, `SessionDep`
- 复用 `backend/app/api/routes/items.py:13` 的分页查询模式
- 复用 `backend/app/api/routes/items.py:37` 的列表返回模式 (`*Public` 包装)
- 复用 `backend/app/api/routes/items.py:57` 的创建接口模式

**新增代码**（API层）：
- `backend/app/api/routes/extraction_fields.py` - 抽取字段CRUD接口
- `backend/app/api/routes/extraction_lists.py` - 抽取列表CRUD接口
- `backend/app/api/routes/extraction_templates.py` - 抽取模板CRUD接口
- `backend/app/api/routes/extraction.py` - 信息抽取执行接口

**修改代码**：
- `backend/app/api/main.py` - 添加新路由的引用

---

### 2.3 CRUD层：抽取相关业务逻辑

**架构层次归属**：业务逻辑层 (CRUD)

**实现方式**：
参考 `backend/app/crud.py` 中的 `create_user`, `update_user` 等函数，新增抽取字段、列表、模板的CRUD函数。

**架构一致性说明**：
- 遵循现有CRUD函数的命名规范和签名模式
- 保持相同的返回类型和错误处理方式
- 使用SQLAlchemy Session进行数据操作

**可复用资产**：
- 复用 `backend/app/crud.py:10` 的 `create_user` 模式
- 复用 `backend/app/crud.py:20` 的 `update_user` 模式
- 复用 `backend/app/crud.py:34` 的 `get_user_by_email` 查询模式

**新增代码**（CRUD层）：
- `backend/app/crud.py` - 在现有文件中追加抽取相关的CRUD函数

---

### 2.4 核心服务层：硅基流动API集成

**架构层次归属**：业务逻辑层 (新增 `core/extraction`)

**实现方式**：
在 `backend/app/core/extraction/` 目录下创建服务模块，封装硅基流动API调用、Markitdown文档转换等核心逻辑。

**架构一致性说明**：
- 遵循现有 `core/` 模块的职责定位（核心基础设施）
- 使用 `core/config.py` 的 `Settings` 管理配置
- 遵循现有的错误处理和日志记录规范

**可复用资产**：
- 复用 `backend/app/core/config.py:26` 的 `Settings` 类添加新配置
- 复用 `backend/app/core/db.py` 的Session管理

**新增代码**（业务逻辑层）：
- `backend/app/core/extraction/siliconflow_client.py` - 硅基流动API客户端
- `backend/app/core/extraction/document_processor.py` - 文档处理服务（Markitdown集成）
- `backend/app/core/extraction/extraction_service.py` - 抽取服务编排

---

### 2.5 前端组件层：抽取管理页面

**架构层次归属**：前端组件层

**实现方式**：
完全参考 `frontend/src/components/Items/` 和 `frontend/src/routes/_layout/items.tsx` 的实现模式，创建抽取字段、列表、模板、抽取执行的页面和组件。

**架构一致性说明**：
- 遵循现有前端组件的架构模式
- 使用Chakra UI v3组件库
- 使用TanStack Query进行状态管理
- 使用TanStack Router进行路由
- 使用React Hook Form进行表单验证

**可复用资产**：
- 复用 `frontend/src/components/Items/AddItem.tsx` 的对话框模式
- 复用 `frontend/src/components/Items/DeleteItem.tsx` 的删除确认模式
- 复用 `frontend/src/routes/_layout/items.tsx` 的列表页面模式
- 复用 `frontend/src/hooks/useCustomToast.ts` 的通知处理
- 复用 `frontend/src/components/ui/` 的UI基础组件

**新增代码**（前端组件层）：
- `frontend/src/components/ExtractionFields/AddExtractionField.tsx`
- `frontend/src/components/ExtractionFields/EditExtractionField.tsx`
- `frontend/src/components/ExtractionFields/DeleteExtractionField.tsx`
- `frontend/src/components/ExtractionLists/` (类似结构)
- `frontend/src/components/ExtractionTemplates/` (类似结构)
- `frontend/src/components/ExtractionExtract/ExtractForm.tsx`
- `frontend/src/routes/_layout/extraction-fields.tsx`
- `frontend/src/routes/_layout/extraction-lists.tsx`
- `frontend/src/routes/_layout/extraction-templates.tsx`
- `frontend/src/routes/_layout/extraction-extract.tsx`

**修改代码**：
- `frontend/src/components/Common/SidebarItems.tsx` - 添加新的导航项
- `frontend/src/routes/_layout.tsx` - 添加新的路由配置

---

## 3. 数据模型设计

### 3.1 新增数据模型

**可复用资产**：
- 继承 `backend/app/models.py:43` 的 `User` 模型的关系模式
- 复用 `backend/app/models.py:44` 的UUID主键模式

**新增模型**：
```python
# backend/app/models.py (追加)

from typing import List
from sqlmodel import Field, Relationship, SQLModel

class ExtractionFieldBase(SQLModel):
    field_name: str = Field(index=True, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    field_type: str  # text, number, date, boolean
    alias_list: List[str] = Field(default_factory=list)
    is_required: bool = True
    default_value: str | None = Field(default=None, max_length=255)

class ExtractionField(ExtractionFieldBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: User | None = Relationship(back_populates="extraction_fields")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ExtractionFieldPublic(ExtractionFieldBase):
    id: uuid.UUID

class ExtractionFieldsPublic(SQLModel):
    data: List[ExtractionFieldPublic]
    count: int

# ExtractionList 和 ExtractionTemplate 类似...
```

### 3.2 数据库迁移

**可复用资产**：
- 参考 `backend/app/alembic/versions/` 的现有迁移文件模式

**迁移脚本**：
```bash
# 生成迁移
uv run alembic revision --autogenerate -m "Add extraction models"

# 执行迁移
uv run alembic upgrade head
```

---

## 4. API接口设计（API层）

### 4.1 接口清单

| 方法 | 路径 | 功能 | 架构层 | 可复用资产 |
|------|------|------|--------|-----------|
| POST | /api/v1/extraction/fields/ | 创建字段 | API层 | 复用 `items.py:57` |
| GET | /api/v1/extraction/fields/ | 字段列表 | API层 | 复用 `items.py:37` |
| GET | /api/v1/extraction/fields/{id} | 字段详情 | API层 | 复用 `items.py:44` |
| PUT | /api/v1/extraction/fields/{id} | 更新字段 | API层 | 复用 `items.py:71` |
| DELETE | /api/v1/extraction/fields/{id} | 删除字段 | API层 | 复用 `items.py:95` |
| POST | /api/v1/extraction/lists/ | 创建列表 | API层 | 同上 |
| ... | ... | ... | ... | ... |
| POST | /api/v1/extraction/extract/ | 执行抽取 | API层 | 新增 |

### 4.2 接口实现

**架构一致性说明**：
- 遵循现有API层的路由定义规范
- 使用 `backend/app/api/deps.py` 的中间件进行权限校验
- 遵循现有的请求/响应格式规范 (`*Public` 包装)

**可复用资产**：
- 复用 `backend/app/api/routes/items.py` 的完整路由模式
- 复用 `backend/app/api/deps.py` 的 `CurrentUser`, `SessionDep`
- 复用 `backend/app/models.py` 的 `*Create`, `*Update`, `*Public` 模式

**新增代码**（API层）：
```python
# backend/app/api/routes/extraction_fields.py
from fastapi import APIRouter, Depends
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import ExtractionField, ExtractionFieldCreate, ExtractionFieldsPublic

router = APIRouter(prefix="/extraction/fields", tags=["extraction-fields"])

@router.get("/", response_model=ExtractionFieldsPublic)
def read_fields(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 10
):
    """完全参考 items.py:13 的实现模式"""
    count_statement = (
        select(func.count())
        .select_from(ExtractionField)
        .where(ExtractionField.owner_id == current_user.id)
    )
    count = session.exec(count_statement).one()

    statement = (
        select(ExtractionField)
        .where(ExtractionField.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    fields = session.exec(statement).all()

    return ExtractionFieldsPublic(data=fields, count=count)

# 其他接口类似...
```

---

## 5. 前端实现设计

### 5.1 组件设计

**架构一致性说明**：
- 遵循现有前端组件的架构模式（对话框、表单、列表）
- 保持与现有UI/UX风格一致（Chakra UI v3）

**可复用资产**：
- 复用 `frontend/src/components/Items/AddItem.tsx` 的完整组件模式
- 复用 `frontend/src/routes/_layout/items.tsx` 的页面布局模式
- 复用 `frontend/src/components/ui/` 的所有UI基础组件

**新增组件**：
- `frontend/src/components/ExtractionFields/AddExtractionField.tsx` - 参考 `AddItem.tsx`
- `frontend/src/routes/_layout/extraction-fields.tsx` - 参考 `items.tsx`

### 5.2 状态管理

**架构一致性说明**：
- 使用TanStack Query进行服务端状态管理
- 保持数据流与现有功能一致

**可复用资产**：
- 复用 `frontend/src/client/sdk.gen.ts` 的OpenAPI客户端
- API调用通过OpenAPI自动生成，类型安全

---

## 6. 关键技术点

### 6.1 技术难点：硅基流动API集成

**问题描述**：需要调用外部LLM API进行信息抽取，涉及API认证、请求构建、响应解析、错误重试等。

**解决方案**：
- 参考 `backend/app/core/config.py:26` 的 `Settings` 类添加API配置
- 创建独立的Service层封装API调用逻辑
- 使用Python的 `requests` 库或 `httpx` 进行HTTP调用

**实现代码**：
```python
# backend/app/core/extraction/siliconflow_client.py
import requests
from app.core.config import settings

class SiliconFlowClient:
    def __init__(self):
        self.api_key = settings.SILICONFLOW_API_KEY
        self.base_url = "https://api.siliconflow.cn/v1"
        self.model = settings.SILICONFLOW_MODEL

    def extract(self, text: str, template: ExtractionTemplate) -> dict:
        """调用硅基流动API进行信息抽取"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": self._build_messages(text, template),
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }
        response = requests.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=60
        )
        return response.json()
```

### 6.2 技术难点：Markitdown文档转换

**问题描述**：需要将各种格式文档（PDF、DOCX、XLSX）转换为文本，供LLM处理。

**解决方案**：
- 使用 `markitdown` Python库进行转换
- 封装统一的文档处理接口

**实现代码**：
```python
# backend/app/core/extraction/document_processor.py
from markitdown import MarkItDown

def convert_document_to_text(file_path: str, file_type: str) -> str:
    """将文档转换为文本"""
    md = MarkItDown()
    result = md.convert(file_path)
    return result.text_content
```

### 6.3 技术难点：文件上传

**问题描述**：需要支持文件上传，限制大小为10MB，验证文件类型。

**解决方案**：
- 使用FastAPI的 `UploadFile` 处理文件上传
- 添加文件大小和类型验证中间件

**实现代码**：
```python
# backend/app/api/routes/extraction.py
from fastapi import UploadFile, File

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/extract/")
async def extract_from_file(
    file: UploadFile = File(...),
    template_id: uuid.UUID = Form(...),
    current_user: CurrentUser = ...,
    session: SessionDep = ...
):
    # 验证文件大小
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(400, "文件大小超过10MB限制")

    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "application/pdf", ...]
    if file.content_type not in allowed_types:
        raise HTTPException(400, "不支持的文件类型")
```

---

## 7. 部署配置

**可复用资产**：
- 复用现有的 `backend/app/core/config.py` 配置模式
- 复用现有的 `.env` 环境变量管理

**新增配置**：
```python
# backend/app/core/config.py (追加)

class Settings(BaseSettings):
    # ... 现有配置 ...

    # 硅基流动API配置
    SILICONFLOW_API_KEY: str = ""
    SILICONFLOW_MODEL: str = "deepseek-ai/DeepSeek-R1"

    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list[str] = [
        "image/jpeg", "image/png",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # docx
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # xlsx
        "text/plain"
    ]
```

**新增依赖**：
```bash
# backend/pyproject.toml
dependencies = [
    # ... 现有依赖 ...
    "markitdown>=0.0.1",
]
```

---

## 8. 风险评估

| 风险项 | 影响程度 | 应对措施 |
|--------|----------|----------|
| 硅基流动API稳定性 | 中 | 增加重试机制(最多3次)、超时控制(60秒)、降级处理 |
| 大文件上传超时 | 中 | 限制文件大小(10MB)、提供上传进度反馈 |
| LLM抽取准确性 | 中 | 优化prompt工程、添加字段别名、提供人工校验功能 |
| 用户数据隔离 | 高 | 严格遵循owner_id过滤、添加数据库索引优化查询性能 |

---

## 9. 架构一致性验证

### 9.1 架构层次检查

**新增代码层次归属验证**：

| 新增文件 | 架构层 | 验证结果 | 说明 |
|----------|--------|----------|------|
| `backend/app/models.py` (追加) | 数据模型层 | ✅ | 遵循SQLModel模式 |
| `backend/app/crud.py` (追加) | 业务逻辑层 | ✅ | 遵循CRUD函数模式 |
| `backend/app/api/routes/extraction_*.py` | API层 | ✅ | 遵循FastAPI路由模式 |
| `backend/app/core/extraction/` | 业务逻辑层 | ✅ | 遵循core模块职责 |
| `frontend/src/components/Extraction*/` | 前端组件层 | ✅ | 遵循React组件模式 |
| `frontend/src/routes/_layout/extraction-*.tsx` | 前端页面层 | ✅ | 遵循路由页面模式 |

**依赖方向验证**：
- ✅ API层 → CRUD层 → ORM层（单向依赖）
- ✅ 前端组件 → OpenAPI客户端 → API层（单向依赖）
- ✅ 业务逻辑层不依赖API层
- ✅ 数据模型层不依赖任何上层

### 9.2 设计模式一致性验证

**设计模式使用验证**：

| 设计模式 | 现有使用 | 新增使用 | 一致性 |
|----------|----------|----------|--------|
| 依赖注入 | `api/deps.py` | `api/routes/extraction_*.py` | ✅ |
| DTO模式 | `*Public`, `*Create` | `ExtractionFieldPublic` 等 | ✅ |
| 分页模式 | `skip/limit` | 所有列表接口 | ✅ |
| 认证中间件 | `CurrentUser` | 所有抽取接口 | ✅ |

---

## 10. 实施建议

### 10.1 开发顺序（按架构层次）

1. **数据模型层** - 在 `models.py` 中新增三个SQLModel类
   - 复用 `User` ↔ `Item` 的关系模式
   - 执行数据库迁移

2. **CRUD层** - 在 `crud.py` 中新增抽取相关的CRUD函数
   - 复用 `create_user`, `update_user` 的实现模式

3. **业务逻辑层** - 创建 `core/extraction/` 服务模块
   - 实现硅基流动API客户端
   - 集成Markitdown文档转换

4. **API层** - 创建 `api/routes/extraction_*.py` 路由文件
   - 完全参考 `items.py` 的实现模式
   - 添加到 `api/main.py` 的路由注册

5. **前端层** - 创建组件和页面
   - 完全参考 `Items/` 的组件模式
   - 添加路由配置和导航项

6. **集成测试** - 端到端验证
   - 测试完整的数据流
   - 验证用户数据隔离

### 10.2 注意事项

- **架构优先**：始终遵循现有三层架构，不引入新的架构模式
- **层次清晰**：每个组件明确属于哪个架构层
- **依赖单向**：避免循环依赖，保持单向依赖
- **接口统一**：遵循现有的接口定义规范（RESTful + *Public包装）
- **命名一致**：保持与现有代码的命名风格一致
- **资产复用**：最大化复用现有代码，避免重复实现

---

**技术方案设计完成** ✅

本方案严格遵循现有项目架构，最大化复用现有资产，确保架构一致性。
