#!/usr/bin/env python3
"""
工具函数模块
提供文件操作、ID生成等通用功能
"""

import os
import re
import string
from pathlib import Path
from datetime import datetime
from typing import Optional


def generate_requirement_id(requirements_dir: Path, name: str) -> str:
    """
    生成新的需求ID

    Args:
        requirements_dir: 需求目录路径
        name: 需求名称

    Returns:
        需求ID，格式如: REQ_001_user_auth
    """
    # 查找现有的最大序号
    existing_ids = []
    if requirements_dir.exists():
        for req_dir in requirements_dir.iterdir():
            if req_dir.is_dir() and req_dir.name.startswith("REQ_"):
                match = re.match(r"REQ_(\d+)_", req_dir.name)
                if match:
                    existing_ids.append(int(match.group(1)))

    next_id = max(existing_ids) + 1 if existing_ids else 1

    # 生成简短名称（小写、下划线分隔）
    short_name = name.lower()
    short_name = re.sub(r'[^\w\s]', '', short_name)  # 移除特殊字符
    short_name = re.sub(r'\s+', '_', short_name)     # 空格转下划线
    short_name = short_name[:30]                     # 限制长度

    return f"REQ_{next_id:03d}_{short_name}"


def sanitize_filename(name: str) -> str:
    """
    清理文件名，移除非法字符

    Args:
        name: 原始文件名

    Returns:
        清理后的文件名
    """
    # 移除或替换非法字符
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # 替换空格和特殊字符为下划线
    name = re.sub(r'[\s\t]+', '_', name)
    # 只保留字母、数字、下划线、中文字符
    name = re.sub(r'[^\w\u4e00-\u9fff_-]', '', name)
    return name


def get_timestamp() -> str:
    """
    获取ISO 8601格式的UTC时间戳

    Returns:
        时间戳字符串，如: 2024-01-01T00:00:00Z
    """
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> Path:
    """
    确保目录存在，不存在则创建

    Args:
        path: 目录路径

    Returns:
        目录路径
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_yaml_file(file_path: Path) -> Optional[dict]:
    """
    读取YAML文件

    Args:
        file_path: YAML文件路径

    Returns:
        解析后的字典，失败返回None
    """
    try:
        import yaml
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
    except Exception as e:
        print(f"读取YAML文件失败 {file_path}: {e}")
    return None


def write_yaml_file(file_path: Path, data: dict) -> bool:
    """
    写入YAML文件

    Args:
        file_path: YAML文件路径
        data: 要写入的数据

    Returns:
        是否成功
    """
    try:
        import yaml
        ensure_dir(file_path.parent)
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
        return True
    except Exception as e:
        print(f"写入YAML文件失败 {file_path}: {e}")
        return False


def read_file(file_path: Path) -> Optional[str]:
    """
    读取文本文件

    Args:
        file_path: 文件路径

    Returns:
        文件内容，失败返回None
    """
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        print(f"读取文件失败 {file_path}: {e}")
    return None


def write_file(file_path: Path, content: str) -> bool:
    """
    写入文本文件

    Args:
        file_path: 文件路径
        content: 文件内容

    Returns:
        是否成功
    """
    try:
        ensure_dir(file_path.parent)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"写入文件失败 {file_path}: {e}")
        return False


def format_stage_name(stage: str) -> str:
    """
    格式化阶段名称为可读形式

    Args:
        stage: 阶段ID，如 STAGE_DETECT

    Returns:
        格式化后的名称，如 "阶段0: 项目探测"
    """
    stage_names = {
        "STAGE_DETECT": "阶段0: 项目探测",
        "STAGE_REQUIRE": "阶段1: 需求定义",
        "STAGE_DESIGN": "阶段2: 技术设计",
        "STAGE_PLAN": "阶段3: 开发计划",
        "STAGE_EXECUTE": "阶段4: 代码开发",
    }
    return stage_names.get(stage, stage)


def parse_clarify_response(response: str) -> dict:
    """
    解析用户的澄清回答

    Args:
        response: 用户回答字符串，如 "1A 2B 3C"

    Returns:
        解析后的字典，如 {"1": "A", "2": "B", "3": "C"}
    """
    result = {}
    # 匹配模式: 数字+字母
    matches = re.findall(r'(\d+)\s*([A-Za-z])', response)
    for num, option in matches:
        result[num] = option.upper()
    return result


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断字符串到指定长度

    Args:
        text: 原始字符串
        max_length: 最大长度
        suffix: 截断后缀

    Returns:
        截断后的字符串
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
