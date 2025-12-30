#!/usr/bin/env python3
"""
AI驱动二开工作流 - 主入口
"""

import sys
import argparse
from pathlib import Path
from state_manager import (
    StateManager,
    STAGE_DETECT,
    STAGE_REQUIRE,
    STAGE_DESIGN,
    STAGE_PLAN,
    STAGE_EXECUTE
)
from utils import format_stage_name, truncate_string


def cmd_status(args, manager: StateManager):
    """查看当前状态"""
    project_state = manager.get_project_state()
    if not project_state:
        print("❌ 项目未初始化")
        return

    print("\n" + "=" * 50)
    print("📋 项目状态")
    print("=" * 50)
    print(f"项目名称: {project_state['project']['name']}")
    print(f"项目路径: {project_state['project']['root_path']}")
    print(f"创建时间: {project_state['project']['created_at']}")
    print(f"总需求数: {len(project_state.get('requirements', []))}")

    current_req_id = project_state.get('current_requirement_id')
    if current_req_id:
        print(f"\n当前需求: {current_req_id}")

        req_state = manager.get_requirement_state(current_req_id)
        if req_state:
            req = req_state['requirement']
            workflow = req_state['workflow']

            print(f"需求名称: {req['name']}")
            print(f"需求状态: {req['status']}")
            print(f"当前阶段: {workflow['current_stage']} ({format_stage_name(workflow['current_stage'])})")
            print(f"已完成阶段: {', '.join(workflow['completed_stages']) if workflow['completed_stages'] else '无'}")

            # 显示产出物
            artifacts = req_state.get('artifacts', {})
            if artifacts:
                print(f"\n📁 产出物:")
                for name, path in artifacts.items():
                    print(f"  - {name}: {path}")
    else:
        print("\n当前无活跃需求")

    # 列出所有需求
    requirements = project_state.get('requirements', [])
    if requirements:
        print(f"\n📋 所有需求:")
        for req in requirements:
            status_icon = "✅" if req['status'] == "completed" else "🔄" if req['status'] == "developing" else "📝"
            print(f"  {status_icon} {req['id']}: {req['name']} [{req['status']}]")

    print("\n" + "=" * 50)


def cmd_start(args, manager: StateManager):
    """启动新需求"""
    requirement = args.requirement if args.requirement else input("请描述您的需求: ")

    if not requirement:
        print("❌ 需求描述不能为空")
        return

    print(f"\n🚀 创建新需求: {requirement}")
    req_id = manager.create_requirement(requirement)

    if req_id:
        print(f"✅ 需求已创建: {req_id}")
        print(f"📁 工作空间: .workflow/requirements/{req_id}/")
        print(f"\n📍 当前阶段: {format_stage_name(STAGE_DETECT)}")
        print(f"📝 下一步: Claude 将开始执行项目探测，生成 project_snapshot.md")
    else:
        print("❌ 需求创建失败")


def cmd_continue(args, manager: StateManager):
    """继续下一阶段"""
    current_req_id = manager.get_current_requirement_id()
    if not current_req_id:
        print("❌ 当前无活跃需求，请先使用 'start' 命令创建需求")
        return

    req_state = manager.get_requirement_state(current_req_id)
    if not req_state:
        print("❌ 无法读取需求状态")
        return

    current_stage = req_state['workflow']['current_stage']
    print(f"\n📍 当前阶段: {current_stage} ({format_stage_name(current_stage)})")

    # 确定下一阶段
    stage_order = [STAGE_DETECT, STAGE_REQUIRE, STAGE_DESIGN, STAGE_PLAN, STAGE_EXECUTE]
    try:
        current_index = stage_order.index(current_stage)
        if current_index < len(stage_order) - 1:
            next_stage = stage_order[current_index + 1]
            print(f"➡️  下一阶段: {next_stage} ({format_stage_name(next_stage)})")
            print(f"\n📝 请确认当前阶段产出物后，回复 '确认' 进入下一阶段")
        else:
            print(f"✅ 所有阶段已完成！需求 {current_req_id} 已完成")
    except ValueError:
        print(f"⚠️  未知阶段: {current_stage}")


def cmd_switch(args, manager: StateManager):
    """切换需求"""
    req_id = args.req_id
    if not req_id:
        print("❌ 请指定需求ID")
        return

    # 检查需求是否存在
    req_state = manager.get_requirement_state(req_id)
    if not req_state:
        print(f"❌ 需求 {req_id} 不存在")
        return

    # 设置为当前需求
    if manager.set_current_requirement(req_id):
        req = req_state['requirement']
        workflow = req_state['workflow']
        print(f"\n✅ 已切换到需求: {req_id}")
        print(f"📝 需求名称: {req['name']}")
        print(f"📍 当前阶段: {workflow['current_stage']} ({format_stage_name(workflow['current_stage'])})")
        print(f"📊 需求状态: {req['status']}")
    else:
        print(f"❌ 切换失败")


def cmd_backtrack(args, manager: StateManager):
    """回溯到指定阶段"""
    target_stage = args.stage.upper()
    current_req_id = manager.get_current_requirement_id()

    if not current_req_id:
        print("❌ 当前无活跃需求")
        return

    valid_stages = [STAGE_REQUIRE, STAGE_DESIGN, STAGE_PLAN]
    if target_stage not in valid_stages:
        print(f"❌ 无效的目标阶段。可选: {', '.join(valid_stages)}")
        return

    if manager.backtrack_to_stage(target_stage):
        print(f"\n↩️  已回溯到阶段: {target_stage} ({format_stage_name(target_stage)})")
        print(f"📝 请根据发现的问题修改对应产出物")
    else:
        print("❌ 回溯失败")


def cmd_list(args, manager: StateManager):
    """列出所有需求"""
    requirements = manager.list_requirements()

    if not requirements:
        print("📋 暂无需求")
        return

    print(f"\n📋 所有需求 (共 {len(requirements)} 个):\n")

    for i, req in enumerate(requirements, 1):
        status_icon = {
            "completed": "✅",
            "developing": "🔄",
            "drafting": "📝",
            "clarifying": "❓",
            "designing": "🎨",
            "planning": "📋",
            "cancelled": "❌"
        }.get(req['status'], "📌")

        is_current = req['id'] == manager.get_current_requirement_id()
        current_mark = " ← 当前" if is_current else ""

        print(f"{i}. {status_icon} {req['id']}: {truncate_string(req['name'], 40)} [{req['status']}]{current_mark}")
        print(f"   创建时间: {req['created_at']}")


def cmd_init(args, manager: StateManager):
    """初始化项目工作流"""
    if manager.init_project():
        print("✅ 项目工作流已初始化")
        print(f"📁 工作流目录: {manager.workflow_dir}")
    else:
        print("❌ 初始化失败")


def main():
    parser = argparse.ArgumentParser(
        description="AI驱动二开工作流 - 状态管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查看当前状态
  python workflow.py status

  # 启动新需求
  python workflow.py start "添加用户权限管理功能"

  # 继续下一阶段
  python workflow.py continue

  # 切换到指定需求
  python workflow.py switch REQ_001_user_auth

  # 回溯到需求定义阶段
  python workflow.py backtrack STAGE_REQUIRE

  # 列出所有需求
  python workflow.py list
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # status 命令
    subparsers.add_parser('status', help='查看当前状态')

    # start 命令
    parser_start = subparsers.add_parser('start', help='启动新需求')
    parser_start.add_argument('requirement', nargs='?', help='需求描述')

    # continue 命令
    subparsers.add_parser('continue', help='继续下一阶段')

    # switch 命令
    parser_switch = subparsers.add_parser('switch', help='切换到指定需求')
    parser_switch.add_argument('req_id', help='需求ID')

    # backtrack 命令
    parser_backtrack = subparsers.add_parser('backtrack', help='回溯到指定阶段')
    parser_backtrack.add_argument('stage', help='目标阶段 (STAGE_REQUIRE/STAGE_DESIGN/STAGE_PLAN)')

    # list 命令
    subparsers.add_parser('list', help='列出所有需求')

    # init 命令
    subparsers.add_parser('init', help='初始化项目工作流')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 创建状态管理器
    manager = StateManager()

    # 执行对应命令
    commands = {
        'status': cmd_status,
        'start': cmd_start,
        'continue': cmd_continue,
        'switch': cmd_switch,
        'backtrack': cmd_backtrack,
        'list': cmd_list,
        'init': cmd_init
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        try:
            cmd_func(args, manager)
        except KeyboardInterrupt:
            print("\n\n⚠️  操作已取消")
        except Exception as e:
            print(f"\n❌ 执行命令时出错: {e}")
            import traceback
            traceback.print_exc()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
