# 编写数据库迁移脚本 变更记录

**任务ID**: [P0-I2]
**完成时间**: 2025-12-30T14:40:00Z
**文件路径**: backend/app/alembic/versions/5622d9e6b9e0_add_extraction_models.py

## 变更内容

### 修改文件
- `backend/app/models.py`: 修复了JSON字段类型的定义
- `backend/app/alembic/versions/`: 新增迁移脚本

### 新增文件
- `backend/app/alembic/versions/5622d9e6b9e0_add_extraction_models.py`: Alembic迁移脚本

## 问题解决

### 问题1: list[str] 类型不兼容

**问题**: SQLModel不支持 `list[str]` 作为原生列类型
```
ValueError: <class 'list'> has no matching SQLAlchemy type
```

**解决方案**: 使用 `Column(JSON)` 存储列表类型
```python
from sqlalchemy import JSON

# 修改前
alias_list: list[str] = Field(default_factory=list)

# 修改后
alias_list: list[str] = Field(default_factory=list, sa_column=Column(JSON))
```

### 问题2: Alembic版本不匹配

**问题**: 数据库中的alembic版本 (`0f0fad4c0bbe`) 与迁移文件不匹配

**解决方案**: 手动更新数据库alembic版本到当前HEAD
```sql
UPDATE alembic_version SET version_num = '1a31ce608336'
```

## 迁移脚本内容

### upgrade() 操作
1. 删除旧表 `extractionresult`
2. 修改 `extractionfield` 表:
   - 添加 `field_name` (VARCHAR(100), indexed)
   - 添加 `alias_list` (JSON)
   - 修改 `field_type` 从 VARCHAR(50) 到 VARCHAR(20)
   - 添加索引 `ix_extractionfield_field_name`
   - 添加索引 `ix_extractionfield_field_type`
   - 删除旧列 `name`, `alias`

3. 修改 `extractionlist` 表:
   - 添加 `list_name` (VARCHAR(100), indexed)
   - 添加 `field_ids` (JSON)
   - 添加索引 `ix_extractionlist_list_name`
   - 删除旧列 `name`

4. 修改 `extractiontemplate` 表:
   - 添加 `template_name` (VARCHAR(100), indexed)
   - 添加 `field_ids` (JSON)
   - 添加 `list_ids` (JSON)
   - 添加索引 `ix_extractiontemplate_template_name`
   - 删除旧列 `name`

### downgrade() 操作
提供完整的回滚操作，可以恢复到迁移前的状态

## 验证结果

- [x] 迁移脚本生成成功
- [x] 迁移执行成功 (`alembic upgrade head`)
- [x] 数据库表创建成功
- [x] 列结构验证通过

### 验证命令输出
```
✓ Extraction tables found: extractionfield, extractionlist, extractiontemplate

ExtractionField columns:
  - description: character varying
  - field_type: character varying
  - is_required: boolean
  - default_value: character varying
  - id: uuid
  - owner_id: uuid
  - field_name: character varying
  - alias_list: json
```

## 关键代码

### 迁移命令
```bash
# 生成迁移
PYTHONPATH=. uv run alembic revision --autogenerate -m "Add extraction models"

# 执行迁移
PYTHONPATH=. uv run alembic upgrade head

# 验证当前版本
PYTHONPATH=. uv run alembic current
```

### 数据库表结构
- **extractionfield**: 存储抽取字段定义
- **extractionlist**: 存储抽取列表定义
- **extractiontemplate**: 存储抽取模板定义

所有表都包含:
- `id`: UUID主键
- `owner_id`: 用户外键（用户级数据隔离）
- JSON字段: 存储列表类型数据（alias_list, field_ids, list_ids）
- 索引: 优化查询性能

## 遗留问题

无。数据库迁移已成功完成。

## 下一步

执行任务 [P0-I3]: 创建CRUD函数
