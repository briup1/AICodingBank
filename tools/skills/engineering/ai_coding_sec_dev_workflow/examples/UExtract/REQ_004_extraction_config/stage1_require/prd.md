# 产品需求文档（PRD）

**需求ID**：REQ_004_extraction_config
**需求名称**：信息抽取配置功能
**需求类型**：新增功能
**版本**：v1.0
**创建时间**：2025-12-30T00:00:00Z
**最后更新**：2025-12-30T01:00:00Z

---

## 1. 需求概述

### 1.1 背景
用户需要从各种文件（图片、文档、表格等）中抽取结构化信息。当前系统缺少灵活的抽取配置功能,无法让用户自定义抽取字段、列表和模板。

### 1.2 目标
构建一套完整的信息抽取配置系统,包括:
- 抽取字段管理:定义可抽取的数据字段
- 抽取列表管理:将字段组织成列表
- 抽取模板管理:将字段和列表组合成抽取模板
- 信息抽取执行:基于模板对文件进行信息抽取

### 1.3 范围
**包含**：
- 抽取字段CRUD管理页面
- 抽取列表CRUD管理页面
- 抽取模板CRUD管理页面
- 信息抽取执行页面
- 文件上传功能（最大10MB）
- 硅基流动模型接口集成
- Markitdown文档转换集成

**不包含**：
- 抽取结果的编辑和导出功能
- 抽取历史记录管理
- 抽取模板的版本控制
- 多模态图片识别（使用文本模型替代）

---

## 2. 用户故事

### 2.1 目标用户
- **配置管理员**:负责创建和维护抽取字段、列表、模板
- **业务用户**:使用模板对文件进行信息抽取

### 2.2 使用场景
```
场景1：配置管理员创建抽取字段
配置管理员登录系统 → 进入"抽取字段管理"页面 → 点击"添加字段" → 填写字段名称、类型等信息 → 保存

场景2：配置管理员创建抽取模板
配置管理员进入"抽取模板管理"页面 → 点击"添加模板" → 选择已有字段和列表 → 保存模板

场景3：业务用户进行信息抽取
业务用户进入"信息抽取"页面 → 上传文件 → 选择模板 → 点击"开始识别" → 查看抽取结果
```

---

## 3. 功能需求

### 3.1 功能模块A：抽取字段管理

**用户故事**：作为配置管理员,我想要管理抽取字段,以便定义可从文件中抽取的数据类型。

**功能描述**：
提供抽取字段的完整CRUD功能,支持字段列表展示（每页10条）和字段的增删改查操作。

**交互规则**：
- 列表默认按创建时间倒序排列
- 每页显示10条记录,支持分页
- 删除字段前需要检查是否被列表/模板引用,如被引用则不允许删除
- 字段类型通过下拉框选择
- "是否必要"通过复选框勾选
- **所有配置数据按用户隔离,每个用户只能看到和管理自己创建的字段**

**数据字段**：
| 字段名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| field_name | string | 是 | 字段名称 | "姓名" |
| description | string | 否 | 字段说明 | "抽取人员姓名" |
| field_type | enum | 是 | 字段类型 | text / number / date / boolean |
| alias_list | array | 否 | 别名列表（多个变体名称） | ["名字", "name", "全名"] |
| is_required | boolean | 是 | 是否必要 | true / false |
| default_value | string | 否 | 默认值 | "未知" |

**字段类型枚举值**（已确认1A）：
- `text`: 文本类型
- `number`: 数字类型
- `date`: 日期类型
- `boolean`: 布尔类型

**别名列表**（已确认2B）：
- 数组类型,存储多个可能的变体名称
- 用于字段匹配时的同义词识别

**验证规则**：
- 字段名称不能为空,长度1-100字符
- 字段名称在同一用户下不能重复
- 说明长度不能超过500字符
- 别名列表每个元素长度不超过50字符

**API需求**：
- `POST /api/v1/extraction/fields/` - 创建抽取字段
- `GET /api/v1/extraction/fields/` - 获取字段列表（分页）
- `GET /api/v1/extraction/fields/{id}` - 获取字段详情
- `PUT /api/v1/extraction/fields/{id}` - 更新字段
- `DELETE /api/v1/extraction/fields/{id}` - 删除字段

---

### 3.2 功能模块B：抽取列表管理

**用户故事**：作为配置管理员,我想要管理抽取列表,以便将多个相关字段组织在一起。

**功能描述**：
提供抽取列表的完整CRUD功能,支持从已有字段中选择并组织成列表。

**交互规则**：
- 列表的子项必须从已配置的抽取字段中选择
- 同一字段在同一列表中不能重复选择
- 删除列表前需要检查是否被模板引用,如被引用则不允许删除
- 字段选择通过多选下拉框实现
- **所有配置数据按用户隔离**

**数据字段**：
| 字段名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| list_name | string | 是 | 列表名称 | "联系人信息" |
| description | string | 否 | 列表说明 | "包含姓名、电话等字段" |
| field_ids | array | 是 | 包含的字段ID列表 | [uuid1, uuid2] |

**验证规则**：
- 列表名称不能为空,长度1-100字符
- 列表名称在同一用户下不能重复
- 字段ID列表不能为空
- 所有字段ID必须对应已存在的字段且属于当前用户

**API需求**：
- `POST /api/v1/extraction/lists/` - 创建抽取列表
- `GET /api/v1/extraction/lists/` - 获取列表列表（分页）
- `GET /api/v1/extraction/lists/{id}` - 获取列表详情
- `PUT /api/v1/extraction/lists/{id}` - 更新列表
- `DELETE /api/v1/extraction/lists/{id}` - 删除列表

---

### 3.3 功能模块C：抽取模板管理

**用户故事**：作为配置管理员,我想要管理抽取模板,以便组合字段和列表形成完整的抽取方案。

**功能描述**：
提供抽取模板的完整CRUD功能,支持从已有字段和列表中组合成模板。

**交互规则**：
- 模板的子项必须从已配置的字段和列表中选择
- 同一字段/列表在同一模板中不能重复选择
- 删除模板前需要检查是否有抽取任务在使用
- 字段永远排在列表的前面展示
- 通过拖拽或序号调整字段和列表的显示顺序
- **所有配置数据按用户隔离**

**数据字段**：
| 字段名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| template_name | string | 是 | 模板名称 | "身份证信息抽取" |
| description | string | 否 | 模板说明 | "从身份证中抽取关键字段" |
| field_ids | array | 是 | 包含的字段ID列表 | [uuid1, uuid2] |
| list_ids | array | 是 | 包含的列表ID列表 | [uuid3, uuid4] |

**验证规则**：
- 模板名称不能为空,长度1-100字符
- 模板名称在同一用户下不能重复
- 字段ID列表和列表ID列表不能同时为空
- 所有ID必须对应已存在的字段/列表且属于当前用户
- 字段/列表不能重复选择

**API需求**：
- `POST /api/v1/extraction/templates/` - 创建抽取模板
- `GET /api/v1/extraction/templates/` - 获取模板列表（分页）
- `GET /api/v1/extraction/templates/{id}` - 获取模板详情
- `PUT /api/v1/extraction/templates/{id}` - 更新模板
- `DELETE /api/v1/extraction/templates/{id}` - 删除模板

---

### 3.4 功能模块D：信息抽取执行

**用户故事**：作为业务用户,我想要上传文件并使用模板进行信息抽取,以便快速获得结构化数据。

**功能描述**：
提供文件上传、模板选择、执行抽取、展示结果、清空状态的完整流程。

**交互规则**：
- 文件上传后显示文件名和大小
- 模板选择下拉框仅显示当前用户创建的模板
- 点击"开始识别"后显示加载状态
- 抽取结果以列表形式展示,字段在前、列表在后
- 点击"清空识别结果"重置所有组件状态

**文件处理逻辑**：
- **图片文件（image/*）**：先使用OCR或图片处理工具提取文本,再调用文本模型抽取
- **其他文件（docx, pdf, excel等）**：使用Markitdown包转换为文本后再抽取
- **文件大小限制：10MB**（已确认6）
- **支持的文件格式**：jpg, png, pdf, docx, xlsx, txt

**硅基流动API集成**（已确认4）：

**API端点**：
```
POST https://api.siliconflow.cn/v1/chat/completions
```

**请求头**：
```http
Authorization: Bearer <your_api_key>
Content-Type: application/json
```

**请求体示例**：
```json
{
  "model": "deepseek-ai/DeepSeek-R1",
  "messages": [
    {
      "role": "user",
      "content": "从以下文本中抽取字段：{text}\n请抽取以下字段：{fields}"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 512
}
```

**响应体示例**：
```json
{
  "id": "chatcmpl-1234567890abcdef",
  "choices": [
    {
      "message": {
        "content": "根据文本内容，抽取结果如下..."
      }
    }
  ]
}
```

**数据字段**：
| 字段名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| file | file | 是 | 上传的文件（最大10MB） | file.jpg |
| template_id | uuid | 是 | 选择的模板ID | uuid |

**抽取结果展示**（已确认5B - 嵌套结构）：
```json
{
  "fields": [
    {
      "name": "姓名",
      "value": "张三",
      "type": "text",
      "confidence": 0.95
    },
    {
      "name": "年龄",
      "value": "25",
      "type": "number",
      "confidence": 0.88
    }
  ],
  "lists": [
    {
      "name": "联系人信息",
      "items": [
        {
          "name": "电话",
          "value": "123456789",
          "confidence": 0.92
        },
        {
          "name": "邮箱",
          "value": "example@email.com",
          "confidence": 0.85
        }
      ]
    }
  ],
  "metadata": {
    "model": "deepseek-ai/DeepSeek-R1",
    "processing_time": 1.23,
    "file_type": "pdf"
  }
}
```

**API需求**：
- `POST /api/v1/extraction/extract/` - 执行信息抽取
- 请求体：multipart/form-data 包含 file 和 template_id
- 返回：抽取结果的嵌套JSON结构

---

## 4. 非功能需求

### 4.1 性能要求
- 抽取字段/列表/模板列表加载时间：< 500ms
- 文件上传响应：< 1s (开始上传)
- 文件大小限制：最大10MB
- 抽取执行时间：取决于硅基流动API,需显示加载状态

### 4.2 安全要求
- **所有配置数据按用户隔离**（已确认3A）
- 文件上传需验证文件类型和大小
- 抽取API调用需要认证
- API Key通过环境变量管理,不暴露到前端

### 4.3 兼容性要求
- **支持的文件格式**：jpg, png, pdf, docx, xlsx, txt
- **文件大小限制**：10MB（已确认6）
- 浏览器：Chrome 90+, Firefox 88+

### 4.4 可靠性要求
- 硅基流动API调用失败时增加重试机制（最多3次）
- 文件上传失败时提供明确的错误提示
- 抽取超时设置为60秒

---

## 5. 用户体验设计

### 5.1 页面流程
```
侧边栏导航:
├── 抽取字段管理
├── 抽取列表管理
├── 抽取模板管理
└── 信息抽取
```

### 5.2 关键交互
- 添加/编辑操作：使用弹出对话框（Dialog）
- 删除操作：弹出确认对话框
- 列表展示：使用表格（Table）组件
- 字段/列表选择：使用多选下拉框（MultiSelect）
- 文件上传：拖拽上传 + 点击上传,显示进度条

### 5.3 错误处理
- 删除被引用的字段/列表/模板：提示"该XX正在被使用,无法删除"
- 文件上传失败：提示"上传失败:文件过大或格式不支持"
- 抽取失败：提示"抽取失败:请稍后重试或联系管理员"
- 网络错误：提示"网络连接失败,请检查网络设置"

### 5.4 加载状态
- 文件上传时显示上传进度
- 抽取执行时显示"正在抽取,请稍候..."动画
- API调用失败时显示重试按钮

---

## 6. 数据模型

### 6.1 数据实体

```yaml
ExtractionField:
  id: uuid
  owner_id: uuid  # 关联到user表,实现用户级隔离
  field_name: string
  description: string
  field_type: enum  # text, number, date, boolean
  alias_list: array[string]  # 多个别名
  is_required: boolean
  default_value: string
  created_at: datetime
  updated_at: datetime

ExtractionList:
  id: uuid
  owner_id: uuid  # 关联到user表,实现用户级隔离
  list_name: string
  description: string
  field_ids: array[uuid]
  created_at: datetime
  updated_at: datetime

ExtractionTemplate:
  id: uuid
  owner_id: uuid  # 关联到user表,实现用户级隔离
  template_name: string
  description: string
  field_ids: array[uuid]
  list_ids: array[uuid]
  created_at: datetime
  updated_at: datetime
```

### 6.2 数据关系
- User → ExtractionField (一对多, 级联删除)
- User → ExtractionList (一对多, 级联删除)
- User → ExtractionTemplate (一对多, 级联删除)
- ExtractionField ← ExtractionList (多对多, 通过 field_ids)
- ExtractionField ← ExtractionTemplate (多对多, 通过 field_ids)
- ExtractionList ← ExtractionTemplate (多对多, 通过 list_ids)

### 6.3 索引设计
- owner_id: 所有表都需要索引（用于用户数据隔离查询）
- field_name: 唯一索引（同一用户下唯一）
- list_name: 唯一索引（同一用户下唯一）
- template_name: 唯一索引（同一用户下唯一）
- created_at: 普通索引（用于分页排序）

---

## 7. 外部依赖

### 7.1 硅基流动API
- **文档路径**：`tasks/技术选型-ai大模型接口说明.md`
- **API端点**：`https://api.siliconflow.cn/v1/chat/completions`
- **认证方式**：Bearer Token (API Key)
- **推荐模型**：
  - `deepseek-ai/DeepSeek-R1`: 中文强、推理快
  - `Qwen/Qwen2-7B-Instruct`: 阿里开源、免费可用
- **请求格式**：OpenAI兼容格式
- **响应格式**：标准JSON响应

### 7.2 Markitdown包
- **用途**：将文档（pdf, docx, xlsx等）转换为文本
- **Python包**：`markitdown`
- **安装方式**：`uv add markitdown`

### 7.3 环境变量配置
```bash
# .env 文件添加
SILICONFLOW_API_KEY=sk-xxxxx  # 硅基流动API密钥
SILICONFLOW_MODEL=deepseek-ai/DeepSeek-R1  # 默认模型
MAX_UPLOAD_SIZE=10485760  # 10MB
```

---

## 8. 测试验收标准

### 8.1 功能测试
- [ ] 能成功创建、编辑、删除抽取字段
- [ ] 能成功创建、编辑、删除抽取列表
- [ ] 能成功创建、编辑、删除抽取模板
- [ ] 能成功上传文件（<10MB）并执行抽取
- [ ] 能成功上传文件（>10MB）并被拒绝
- [ ] 分页功能正常工作
- [ ] 引用检查正常工作（被引用的不能删除）
- [ ] 用户数据隔离正常（用户A看不到用户B的数据）

### 8.2 边界测试
- [ ] 字段名称长度边界测试（1字符、100字符、101字符）
- [ ] 字段/列表选择为空的验证
- [ ] 文件大小限制测试（9MB、10MB、11MB）
- [ ] 不支持的文件格式测试

### 8.3 异常测试
- [ ] 网络错误处理
- [ ] 硅基流动API调用失败处理
- [ ] API Key无效时的错误处理
- [ ] 并发创建同名字段的冲突处理

### 8.4 集成测试
- [ ] 端到端测试：创建字段 → 创建列表 → 创建模板 → 上传文件 → 抽取 → 查看结果
- [ ] Markitdown转换功能测试（pdf, docx, xlsx）

---

## 9. 优先级

| 优先级 | 功能点 | 说明 |
|--------|--------|------|
| P0 | 抽取字段CRUD | 基础功能,必须实现 |
| P0 | 抽取列表CRUD | 基础功能,必须实现 |
| P0 | 抽取模板CRUD | 基础功能,必须实现 |
| P0 | 文件上传功能 | 核心功能,必须实现 |
| P0 | 硅基流动API集成 | 核心功能,必须实现 |
| P0 | 用户数据隔离 | 安全要求,必须实现 |
| P1 | 引用检查 | 数据完整性,应该实现 |
| P1 | Markitdown集成 | 文件处理增强,应该实现 |
| P1 | 错误处理和重试 | 可靠性要求,应该实现 |
| P2 | 拖拽排序 | 用户体验增强,可以延后 |
| P2 | 抽取历史记录 | 功能增强,可以延后 |

---

## 10. 风险与依赖

### 10.1 技术风险
- **风险1**：硅基流动API稳定性未知
  - **应对措施**：增加3次重试机制,设置60秒超时,提供明确的错误提示
- **风险2**：大文件上传可能超时
  - **应对措施**：限制文件大小为10MB,增加上传进度显示
- **风险3**：图片OCR准确率可能不高
  - **应对措施**：先实现基础功能,图片OCR作为P2功能延后
- **风险4**：LLM抽取结果可能不准确
  - **应对措施**：在prompt中明确字段说明和别名,提供示例

### 10.2 业务风险
- **风险1**：用户配置复杂度高
  - **应对措施**：提供清晰的UI引导和示例模板,简化操作流程

### 10.3 外部依赖
- **依赖1**：Markitdown包（Python库）用于文档转文本
- **依赖2**：硅基流动模型API用于信息抽取
- **依赖3**：硅基流动API Key需要用户自行申请

---

## 11. 附录

### 11.1 参考文档
- 项目现状快照：`.workflow/requirements/REQ_004_extraction_config/stage0_detect/project_snapshot.md`
- 硅基流动API文档：`tasks/技术选型-ai大模型接口说明.md`

### 11.2 相关需求
- REQ_001: 初始项目设置
- REQ_002: 用户认证系统
- REQ_003: 基础数据模型

### 11.3 澄清问题汇总（已解决）
| 问题编号 | 问题描述 | 用户选择 | 说明 |
|---------|---------|---------|------|
| 1 | 字段类型枚举值 | 1A | text, number, date, boolean |
| 2 | 别名列表数据结构 | 2B | 数组类型,多个别名 |
| 3 | 数据隔离级别 | 3A | 用户级隔离 |
| 4 | 硅基流动API信息 | 已提供 | OpenAI兼容格式 |
| 5 | 抽取结果结构 | 5B | 嵌套结构 |
| 6 | 文件上传限制 | 6 | 最大10MB |

---

**PRD版本历史**：
- v1.0-draft (2025-12-30): 初始版本,包含6个澄清问题
- v1.0 (2025-12-30): 所有澄清问题已解决,PRD完成
