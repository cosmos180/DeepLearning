<!--
 * @Author       : bughero bughero2012@gmail.com
 * @Date         : 2025-09-29 11:20:30
 * @LastEditors  : bughero bughero2012@gmail.com
 * @LastEditTime : 2025-09-29 11:20:39
 * @FilePath     : /DeepLearning/python/investment_analyst/README.md
 * @Description  : 
 * 
 * Copyright (c) 2025 by @Me, All Rights Reserved. 
-->
# 顶级投资分析师系统

基于LLM Agent的投资分析系统，包含多个专业MCP模块协同工作。

## 系统架构

```
Client
  │
  ▼
Workflow Orchestrator (调度/依赖/异常处理)
  │
  ├─► 顶级行业分析师 MCP (定义分析维度 & 指标)
  │
  ├─► 指标对齐 MCP (财报字段映射规则)
  │
  ├─► 下载 MCP (财报/行业数据获取)
  │
  ├─► 财报阅读 MCP (指标提取)
  │
  ├─► 数据验证 MCP (校验/交叉验证/单位统一)
  │
  ├─► 外部数据 MCP (行业、宏观、同业对比)
  │
  └─► 数据整理 MCP (报告生成，带溯源)
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行系统

```bash
python main.py
