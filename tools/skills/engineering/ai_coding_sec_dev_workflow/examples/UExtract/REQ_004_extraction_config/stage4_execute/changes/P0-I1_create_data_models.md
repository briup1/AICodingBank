# 创建数据模型 变更记录

**任务ID**: [P0-I1]
**完成时间**: 2025-12-30T04:30:00Z
**文件路径**: backend/app/models.py

## 变更内容

### 修改文件
- `backend/app/models.py`: 追加了信息抽取功能的数据模型

### 新增模型类

#### 1. ExtractionField（抽取字段模型）
- **Base**: `ExtractionFieldBase` - 包含字段的基本属性
  - `field_name`: 字段名称（indexed, max_length=100）
  - `description`: 字段说明（可选, max_length=500）
  - `field_type`: 字段类型（text, number, date, boolean）
  - `alias_list`: 别名列表（数组类型）
  - `is_required`: 是否必要（默认true）
  - `default_value`: 默认值（可选, max_length=255）

- **Create**: `ExtractionFieldCreate` - 创建字段时接收的数据
- **Update**: `ExtractionFieldUpdate` - 更新字段时接收的数据（所有字段可选）
- **Table**: `ExtractionField` - 数据库表模型
  - `id`: UUID主键
  - `owner_id`: 用户外键（CASCADE删除）
  - `owner`: 关联到User模型

- **Public**: `ExtractionFieldPublic` - API返回数据（包含id和owner_id）
- **Public**: `ExtractionFieldsPublic` - 分页列表包装类

#### 2. ExtractionList（抽取列表模型）
- **Base**: `ExtractionListBase` - 包含列表的基本属性
  - `list_name`: 列表名称（indexed, max_length=100）
  - `description`: 列表说明（可选, max_length=500）

- **Create**: `ExtractionListCreate` - 包含 `field_ids` 字段
- **Update**: `ExtractionListUpdate` - 包含可选的 `field_ids` 字段
- **Table**: `ExtractionList` - 数据库表模型
- **Public**: `ExtractionListPublic` - API返回数据（包含id, owner_id, field_ids）
- **Public**: `ExtractionListsPublic` - 分页列表包装类

#### 3. ExtractionTemplate（抽取模板模型）
- **Base**: `ExtractionTemplateBase` - 包含模板的基本属性
  - `template_name`: 模板名称（indexed, max_length=100）
  - `description`: 模板说明（可选, max_length=500）

- **Create**: `ExtractionTemplateCreate` - 包含 `field_ids` 和 `list_ids`
- **Update**: `ExtractionTemplateUpdate` - 包含可选的 `field_ids` 和 `list_ids`
- **Table**: `ExtractionTemplate` - 数据库表模型
- **Public**: `ExtractionTemplatePublic` - API返回数据
- **Public**: `ExtractionTemplatesPublic` - 分页列表包装类

### 修改现有模型
- **User模型**: 追加了三个关系字段
  - `extraction_fields`: 用户创建的抽取字段列表
  - `extraction_lists`: 用户创建的抽取列表列表
  - `extraction_templates`: 用户创建的抽取模板列表
  - 所有关系都设置了 `cascade_delete=True`

## 关键代码

```python
# ExtractionField - 抽取字段
class ExtractionField(ExtractionFieldBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="extraction_fields")

# ExtractionList - 抽取列表
class ExtractionList(ExtractionListBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="extraction_lists")

# ExtractionTemplate - 抽取模板
class ExtractionTemplate(ExtractionTemplateBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="extraction_templates")
```

## 设计说明

### 遵循的模式
1. **完全参考Item模型的模式**：Base → Create → Update → Table → Public → Publics
2. **用户级数据隔离**：通过 `owner_id` 外键实现，删除用户时自动级联删除相关数据
3. **UUID主键**：使用UUID作为主键，避免自增ID的暴露问题
4. **索引优化**：在 `field_name`, `list_name`, `template_name` 上添加索引以优化查询
5. **字段验证**：使用SQLModel的Field进行字段级别验证（max_length等）

### 数据隔离实现
- 所有抽取相关数据都通过 `owner_id` 关联到User
- 在API层查询时必须添加 `owner_id` 过滤条件
- 设置 `ondelete="CASCADE"` 确保用户删除时相关数据自动清理

## 验证结果

- [x] 代码可编译/运行（Python语法检查通过）
- [ ] 单元测试通过（待[P0-R1]阶段进行完整测试）
- [x] 类型检查通过（mypy strict模式通过）

### 验证细节

1. **类型检查修复**:
   - 问题：Update类继承Base类导致类型不兼容
   - 解决：将Update类改为直接继承`SQLModel`而非Base类
   - 结果：mypy strict模式通过，无类型错误

2. **代码编译验证**:
   - Python语法检查通过
   - 所有模型类正确定义

## 遗留问题

无。数据模型已按照PRD和技术设计书完成实现。

## 下一步

执行任务 [P0-I2]: 创建数据库迁移脚本
