#!/usr/bin/env python3
"""
状态管理模块
负责工作流状态的读取、写入和更新
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List

# 添加当前目录到路径以支持相对导入
sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    write_yaml_file,
    read_yaml_file,
    ensure_dir,
    get_timestamp,
    generate_requirement_id
)


# 阶段常量
STAGE_DETECT = "STAGE_DETECT"
STAGE_REQUIRE = "STAGE_REQUIRE"
STAGE_DESIGN = "STAGE_DESIGN"
STAGE_PLAN = "STAGE_PLAN"
STAGE_EXECUTE = "STAGE_EXECUTE"

ALL_STAGES = [STAGE_DETECT, STAGE_REQUIRE, STAGE_DESIGN, STAGE_PLAN, STAGE_EXECUTE]

# 需求状态常量
STATUS_DRAFTING = "drafting"
STATUS_CLARIFYING = "clarifying"
STATUS_DESIGNING = "designing"
STATUS_PLANNING = "planning"
STATUS_DEVELOPING = "developing"
STATUS_COMPLETED = "completed"
STATUS_CANCELLED = "cancelled"


class StateManager:
    """工作流状态管理器"""

    def __init__(self, project_root: Optional[Path] = None):
        """
        初始化状态管理器

        Args:
            project_root: 项目根目录，默认为当前工作目录
        """
        if project_root is None:
            project_root = Path.cwd()
        self.project_root = Path(project_root)
        self.workflow_dir = self.project_root / ".workflow"
        self.requirements_dir = self.workflow_dir / "requirements"
        self.project_state_file = self.workflow_dir / "project_state.yaml"

    def init_project(self) -> bool:
        """
        初始化项目工作流目录

        Returns:
            是否成功
        """
        try:
            # 创建目录结构
            ensure_dir(self.workflow_dir)
            ensure_dir(self.requirements_dir)

            # 如果项目状态文件不存在，创建初始文件
            if not self.project_state_file.exists():
                initial_state = {
                    "project": {
                        "name": self.project_root.name,
                        "root_path": str(self.project_root.absolute()),
                        "created_at": get_timestamp()
                    },
                    "requirements": [],
                    "current_requirement_id": None
                }
                write_yaml_file(self.project_state_file, initial_state)

            return True
        except Exception as e:
            print(f"初始化项目失败: {e}")
            return False

    def get_project_state(self) -> Optional[dict]:
        """
        获取项目状态

        Returns:
            项目状态字典
        """
        return read_yaml_file(self.project_state_file)

    def update_project_state(self, updates: dict) -> bool:
        """
        更新项目状态

        Args:
            updates: 要更新的字段

        Returns:
            是否成功
        """
        state = self.get_project_state() or {}
        state.update(updates)
        return write_yaml_file(self.project_state_file, state)

    def get_current_requirement_id(self) -> Optional[str]:
        """
        获取当前需求ID

        Returns:
            当前需求ID，如果没有则返回None
        """
        state = self.get_project_state()
        return state.get("current_requirement_id") if state else None

    def set_current_requirement(self, req_id: str) -> bool:
        """
        设置当前需求ID

        Args:
            req_id: 需求ID

        Returns:
            是否成功
        """
        return self.update_project_state({"current_requirement_id": req_id})

    def create_requirement(self, name: str, description: str = "") -> Optional[str]:
        """
        创建新需求

        Args:
            name: 需求名称
            description: 需求描述

        Returns:
            新创建的需求ID，失败返回None
        """
        try:
            # 确保目录存在
            self.init_project()

            # 生成需求ID
            req_id = generate_requirement_id(self.requirements_dir, name)

            # 创建需求目录结构
            req_dir = self.requirements_dir / req_id
            ensure_dir(req_dir)
            for stage_dir in [
                "stage0_detect",
                "stage1_require",
                "stage2_design",
                "stage3_plan",
                "stage4_execute/changes"
            ]:
                ensure_dir(req_dir / stage_dir)

            # 创建需求状态文件
            req_state = {
                "requirement": {
                    "id": req_id,
                    "name": name,
                    "description": description,
                    "created_at": get_timestamp(),
                    "status": STATUS_DRAFTING
                },
                "workflow": {
                    "current_stage": STAGE_DETECT,
                    "completed_stages": [],
                    "stage_history": []
                },
                "artifacts": {},
                "pending_clarifications": []
            }
            req_state_file = req_dir / "requirement_state.yaml"
            write_yaml_file(req_state_file, req_state)

            # 更新项目状态
            project_state = self.get_project_state() or {}
            requirements = project_state.get("requirements", [])
            requirements.append({
                "id": req_id,
                "name": name,
                "status": STATUS_DRAFTING,
                "created_at": get_timestamp(),
                "artifacts_path": f".workflow/requirements/{req_id}"
            })
            self.update_project_state({
                "requirements": requirements,
                "current_requirement_id": req_id
            })

            return req_id

        except Exception as e:
            print(f"创建需求失败: {e}")
            return None

    def get_requirement_state(self, req_id: Optional[str] = None) -> Optional[dict]:
        """
        获取需求状态

        Args:
            req_id: 需求ID，为None时使用当前需求

        Returns:
            需求状态字典
        """
        if req_id is None:
            req_id = self.get_current_requirement_id()

        if req_id is None:
            return None

        req_state_file = self.requirements_dir / req_id / "requirement_state.yaml"
        return read_yaml_file(req_state_file)

    def update_requirement_state(self, updates: dict, req_id: Optional[str] = None) -> bool:
        """
        更新需求状态

        Args:
            updates: 要更新的字段
            req_id: 需求ID，为None时使用当前需求

        Returns:
            是否成功
        """
        if req_id is None:
            req_id = self.get_current_requirement_id()

        if req_id is None:
            return False

        req_state_file = self.requirements_dir / req_id / "requirement_state.yaml"
        state = read_yaml_file(req_state_file) or {}

        # 递归更新
        def deep_update(base: dict, updates: dict):
            for key, value in updates.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_update(base[key], value)
                else:
                    base[key] = value

        deep_update(state, updates)
        return write_yaml_file(req_state_file, state)

    def advance_stage(self, next_stage: str, req_id: Optional[str] = None) -> bool:
        """
        推进到下一阶段

        Args:
            next_stage: 下一阶段ID
            req_id: 需求ID，为None时使用当前需求

        Returns:
            是否成功
        """
        if req_id is None:
            req_id = self.get_current_requirement_id()

        state = self.get_requirement_state(req_id)
        if not state:
            return False

        current_stage = state["workflow"]["current_stage"]
        completed_stages = state["workflow"]["completed_stages"]

        # 记录阶段历史
        stage_history = state["workflow"]["stage_history"]
        stage_history.append({
            "stage": current_stage,
            "timestamp": get_timestamp(),
            "status": "completed"
        })

        # 更新阶段
        completed_stages.append(current_stage)

        # 更新需求状态
        status_map = {
            STAGE_DETECT: STATUS_CLARIFYING,
            STAGE_REQUIRE: STATUS_DESIGNING,
            STAGE_DESIGN: STATUS_PLANNING,
            STAGE_PLAN: STATUS_DEVELOPING,
            STAGE_EXECUTE: STATUS_COMPLETED
        }

        return self.update_requirement_state({
            "workflow": {
                "current_stage": next_stage,
                "completed_stages": completed_stages,
                "stage_history": stage_history
            },
            "requirement": {
                "status": status_map.get(next_stage, STATUS_DEVELOPING)
            }
        }, req_id)

    def backtrack_to_stage(self, target_stage: str, req_id: Optional[str] = None) -> bool:
        """
        回溯到指定阶段

        Args:
            target_stage: 目标阶段ID
            req_id: 需求ID，为None时使用当前需求

        Returns:
            是否成功
        """
        if req_id is None:
            req_id = self.get_current_requirement_id()

        state = self.get_requirement_state(req_id)
        if not state:
            return False

        # 更新当前阶段
        return self.update_requirement_state({
            "workflow": {
                "current_stage": target_stage
            }
        }, req_id)

    def list_requirements(self) -> List[dict]:
        """
        列出所有需求

        Returns:
            需求列表
        """
        project_state = self.get_project_state()
        if not project_state:
            return []

        return project_state.get("requirements", [])

    def get_requirement_dir(self, req_id: Optional[str] = None) -> Optional[Path]:
        """
        获取需求目录路径

        Args:
            req_id: 需求ID，为None时使用当前需求

        Returns:
            需求目录路径
        """
        if req_id is None:
            req_id = self.get_current_requirement_id()

        if req_id is None:
            return None

        req_dir = self.requirements_dir / req_id
        return req_dir if req_dir.exists() else None

    def get_artifact_path(self, artifact_name: str, req_id: Optional[str] = None) -> Optional[Path]:
        """
        获取产出物文件路径

        Args:
            artifact_name: 产出物名称，如 "project_snapshot.md"
            req_id: 需求ID，为None时使用当前需求

        Returns:
            产出物文件路径
        """
        req_dir = self.get_requirement_dir(req_id)
        if not req_dir:
            return None

        # 根据文件名确定阶段目录
        stage_map = {
            "project_snapshot.md": "stage0_detect",
            "prd.md": "stage1_require",
            "tech_design.md": "stage2_design",
            "todo_list.md": "stage3_plan"
        }

        stage = stage_map.get(artifact_name)
        if stage:
            return req_dir / stage / artifact_name

        return None
