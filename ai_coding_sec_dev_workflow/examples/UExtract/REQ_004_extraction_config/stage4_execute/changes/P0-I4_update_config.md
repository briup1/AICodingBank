# 更新配置文件 变更记录

**任务ID**: [P0-I4]
**完成时间**: 2025-12-30T15:00:00Z
**文件路径**: backend/app/core/config.py

## 变更内容

### 修改文件
- `backend/app/core/config.py`: 追加了硅基流动API和文件上传配置

### 新增配置项

#### 1. 硅基流动API配置
```python
SILICONFLOW_API_KEY: str = ""
SILICONFLOW_MODEL: str = "deepseek-ai/DeepSeek-R1"
```

#### 2. 文件上传配置
```python
MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES: list[str] = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # docx
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # xlsx
    "text/plain",
]
```

## 配置说明

### 环境变量设置
需要在 `.env` 文件中设置：
```bash
# 硅基流动API配置
SILICONFLOW_API_KEY=your_api_key_here
SILICONFLOW_MODEL=deepseek-ai/DeepSeek-R1
```

### 支持的文件类型
- 图片：JPEG, PNG, GIF, WebP
- 文档：PDF, DOCX, XLSX
- 文本：TXT

### 文件大小限制
- 单个文件最大：10MB
- 可通过 `MAX_UPLOAD_SIZE` 配置调整

## 验证结果

- [x] 代码可编译/运行（Python语法检查通过）
- [x] 类型检查通过（mypy strict模式通过）

## 下一步

执行任务 [P0-R1]: 数据模块集成测试与重构
