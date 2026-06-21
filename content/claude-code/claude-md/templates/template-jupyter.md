---
title: "Template Jupyter"
date: 2026-06-21
category: claude-code
tags: []
status: published
description: "Notes on Template Jupyter."
---

# CLAUDE.md

## 项目概述
数据分析项目，包含数据清洗、特征工程、模型训练和可视化报告。

## 技术栈
- 语言：Python 3.12
- 数据处理：pandas 2.x
- 可视化：matplotlib + seaborn
- 机器学习：scikit-learn
- Notebook：Jupyter Lab
- 环境：python3 -m venv venv
- 任务运行：make
- 版本控制：Git + Git LFS

## 项目结构
.
├── data/            # 数据文件（不提交 Git）
│   ├── raw/         # 原始数据
│   ├── processed/   # 处理后数据
│   └── external/    # 外部数据源
├── notebooks/       # Jupyter Notebooks
│   ├── 01_eda.ipynb
│   ├── 02_cleaning.ipynb
│   └── 03_modeling.ipynb
├── src/             # 可复用代码
│   ├── data/        # 数据加载和处理
│   ├── features/    # 特征工程
│   ├── models/      # 模型定义和训练
│   └── visualization/ # 可视化函数
├── configs/         # 配置文件
├── requirements.txt
└── Makefile         # 常用命令快捷方式

## 编码规范
- 所有函数必须有 type hints 和 docstring
- 数据处理代码放在 src/ 中，Notebook 只做调用和展示
- Notebook 按"探索→清洗→建模→评估"顺序编号
- 随机种子统一设置为 42（确保可复现）
- 图表统一使用中文标签和标题
- 数据路径使用 pathlib.Path，不用字符串拼接

## 工作流
- 创建虚拟环境：python3 -m venv venv
- 激活环境：source venv/bin/activate
- 安装依赖：pip install -r requirements.txt
- 启动 Jupyter：jupyter lab
- 运行全流程：make all
- 导出依赖：pip freeze > requirements.txt

## 注意事项
- 不要提交 data/ 目录到 Git（已在 .gitignore 中）
- 不要提交 .ipynb_checkpoints/
- 大文件使用 Git LFS 管理
- 模型文件保存在 models/ 目录，不提交 Git
