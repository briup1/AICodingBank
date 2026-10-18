# 创建CRUD函数 变更记录

**任务ID**: [P0-I3]
**完成时间**: 2025-12-30T14:50:00Z
**文件路径**: backend/app/crud.py

## 变更内容

### 修改文件
- `backend/app/crud.py`: 追加了信息抽取功能的CRUD函数

### 新增函数

#### 1. ExtractionField CRUD函数（5个）
- `create_extraction_field(session, field_in, owner_id)` - 创建抽取字段
- `get_extraction_fields(session, owner_id, skip, limit)` - 分页获取字段列表
- `get_extraction_field_by_id(session, field_id, owner_id)` - 根据ID获取字段（带用户隔离）
- `update_extraction_field(session, db_field, field_in)` - 更新字段
- `delete_extraction_field(session, db_field)` - 删除字段

#### 2. ExtractionList CRUD函数（5个）
- `create_extraction_list(session, list_in, owner_id)` - 创建抽取列表
- `get_extraction_lists(session, owner_id, skip, limit)` - 分页获取列表
- `get_extraction_list_by_id(session, list_id, owner_id)` - 根据ID获取列表（带用户隔离）
- `update_extraction_list(session, db_list, list_in)` - 更新列表
- `delete_extraction_list(session, db_list)` - 删除列表

#### 3. ExtractionTemplate CRUD函数（5个）
- `create_extraction_template(session, template_in, owner_id)` - 创建抽取模板
- `get_extraction_templates(session, owner_id, skip, limit)` - 分页获取模板
- `get_extraction_template_by_id(session, template_id, owner_id)` - 根据ID获取模板（带用户隔离）
- `update_extraction_template(session, db_template, template_in)` - 更新模板
- `delete_extraction_template(session, db_template)` - 删除模板

## 设计说明

### 遵循的模式
1. **完全参考create_item的模式**：使用 `model_validate()` + `update` 参数
2. **用户级数据隔离**：所有查询函数都强制传入 `owner_id` 进行过滤
3. **分页支持**：所有列表查询函数支持 `skip` 和 `limit` 参数
4. **更新模式**：使用 `model_dump(exclude_unset=True)` 只更新提供的字段

### 用户隔离实现
```python
# 创建时自动设置owner_id
db_obj = ExtractionField.model_validate(field_in, update={"owner_id": owner_id})

# 查询时过滤owner_id
statement = select(ExtractionField).where(
    ExtractionField.id == field_id,
    ExtractionField.owner_id == owner_id  # 用户隔离
)
```

## 关键代码

```python
def create_extraction_field(*, session: Session, field_in: ExtractionFieldCreate, owner_id: uuid.UUID) -> ExtractionField:
    """创建抽取字段"""
    db_obj = ExtractionField.model_validate(field_in, update={"owner_id": owner_id})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_extraction_fields(*, session: Session, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[ExtractionField]:
    """获取用户的所有抽取字段（分页）"""
    statement = select(ExtractionField).where(ExtractionField.owner_id == owner_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_extraction_field_by_id(*, session: Session, field_id: uuid.UUID, owner_id: uuid.UUID) -> ExtractionField | None:
    """根据ID获取抽取字段（带用户隔离）"""
    statement = select(ExtractionField).where(
        ExtractionField.id == field_id,
        ExtractionField.owner_id == owner_id
    )
    return session.exec(statement).first()


def update_extraction_field(*, session: Session, db_field: ExtractionField, field_in: ExtractionFieldUpdate) -> ExtractionField:
    """更新抽取字段"""
    field_data = field_in.model_dump(exclude_unset=True)
    db_field.sqlmodel_update(field_data)
    session.add(db_field)
    session.commit()
    session.refresh(db_field)
    return db_field
```

## 验证结果

- [x] 代码可编译/运行（Python语法检查通过）
- [x] 类型检查通过（mypy strict模式通过，无错误）
- [ ] 单元测试通过（待[P0-R1]阶段进行完整测试）

### 验证命令输出
```bash
$ python -m py_compile app/crud.py
✓ Syntax check passed!

$ uv run mypy app/crud.py --no-error-summary
# 无输出，表示类型检查通过
```

## 遗留问题

无。CRUD函数已按照PRD和技术设计书完成实现。

## 下一步

执行任务 [P0-I4]: 更新配置文件
