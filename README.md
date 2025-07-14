# 项目交接文档

具体参考：https://tcnqwpt0qa5j.feishu.cn/wiki/CPulwZ6kyiGe9OkekegcLqf4nwe

## 1. 项目概述

本项目是一个用于船舶内部线缆路由规划和优化的算法工具。它能够根据给定的船舱节点布局、预设管线和设备连接需求，自动计算出满足特定约束条件（如容量、长度）的最优或次优线缆路径，并提供三维可视化结果。

## 2. 项目结构

```
.
├── run.sh                # 项目运行脚本
├── src/
│   ├── Algorithm/
│   │   ├── main.py       # 主程序入口
│   │   ├── graph/
│   │   │   └── structure.py # 图数据结构定义 (Graph, Edge)
│   │   ├── routing/
│   │   │   ├── path_utils.py # 寻路工具函数 (A*, dijkstra等)
│   │   │   └── optimizer.py  # 优化器 (如局部搜索)
│   │   ├── real_data/
│   │   │   └── real_data_read.py # 用于读取真实数据
│   │   └── dwg/
│   │       └── dwg_read.py # 用于读取dxf文件
│   ├── data/
│   │   ├── ExportDtas/     # 真实数据存放目录
│   │   ├── device.py       # 设备信息
│   │   └── hub.py          # 节点信息
│   └── vis/
│       └── vis.py          # 可视化工具
├── log/                    # 日志和可视化结果输出目录
└── HANDOVER.md             # 本交接文档
```

## 3. 如何运行

### 3.1 环境依赖

项目依赖的Python库暂未通过`requirements.txt`管理，建议根据代码中的`import`语句手动安装，主要可能包括：
- `plotly`
- `pandas`
- `numpy`
- `ezdxf` (如果使用dxf数据源)

### 3.2 运行步骤

1.  **配置数据源**:
    打开 `src/Algorithm/main.py` 文件，根据需求设置以下布尔变量，确保只有一个为 `True`:
    - `REAL_DATA`: 使用 `src/data/ExportDtas` 中的真实数据。
    - `TEST_DXF`: 使用 `../data/test.dxf` 文件中的测试数据。
    - `MOCK_DATA`: 使用 `src/data/` 目录下的模拟数据。

2.  **执行脚本**:
    在项目根目录下运行 `run.sh` 脚本：
    ```bash
    bash run.sh
    ```
    该脚本会自动设置 `PYTHONPATH`，创建 `log` 目录，并执行主程序。

### 3.3 查看输出

- **日志**: 运行日志和路径计算结果会输出到 `log/log_YYYYMMDD_HHMMSS.txt` 文件中。
- **可视化**: 3D可视化结果会保存为 `log/graph_visualization_YYYYMMDD_HHMMSS.html` 文件，用浏览器打开即可交互式查看。

## 4. 核心逻辑

### 4.1 数据加载

- 程序通过 `src/Algorithm/main.py` 中的 `REAL_DATA`, `TEST_DXF`, `MOCK_DATA` 开关选择不同的数据源。
- `real_data_api` 函数 (`src/Algorithm/real_data/real_data_read.py`) 负责从 `src/data/ExportDtas` 目录读取和解析真实的节点、管线和设备数据。

### 4.2 图构建

- 使用 `src/Algorithm/graph/structure.py` 中定义的 `Graph` 和 `Edge` 类来表示网络拓扑。
- `Graph` 对象通过邻接表实现，存储节点坐标、元数据以及边信息。
- `Edge` 对象包含容量、距离、实际负载和类型等属性。
- `build_graph` 函数 (`src/Algorithm/routing/path_utils.py`) 负责将加载的节点和连接数据转换为 `Graph` 对象。

### 4.3 路径计算

- `process_single_connection` 函数 (`src/Algorithm/routing/path_utils.py`) 是处理单个设备连接请求的核心。
- 它首先为起点和终点设备在图中寻找最近的接入节点。
- 然后调用寻路算法（如A*）来计算满足容量限制的路径。

### 4.4 结果输出与可视化

- 计算出的路径信息（节点列表、坐标）会被打印到日志中。
- `visualize_graph` 函数 (`src/vis/vis.py`) 使用 `plotly` 库生成一个HTML文件，其中包含：
    - 节点（红色标记）
    - 管线（蓝色线条）
    - 设备（橙色标记）
    - 计算出的路径（彩色线条）

## 5. 数据格式

### 5.1 节点 (Nodes)

一个字典，`key` 为节点ID（字符串），`value` 为一个三元组 `(x, y, z)` 坐标。

### 5.2 连接 (Connections)

一个列表，每个元素是一个元组 `(node1_id, node2_id, category)`，表示两个节点之间存在一条物理连接（管线），并指定其类型。

### 5.3 设备 (Device)

一个字典，`key` 为设备ID（字符串），`value` 为一个三元组 `(x, y, z)` 坐标。

### 5.4 设备连接需求 (Device Connections)

一个列表，每个元素是一个元组 `(device1_id, device2_id, load)`，表示两个设备之间需要建立一条连接，并指定其负载需求。

## 6. 注意事项与未来工作
- **[P0]错误处理**: 确保建图和数据是正确的，然后再进行后续处理
- **[P1]优化模块**: `src/Algorithm/main.py` 中包含一个被注释掉的多阶段优化逻辑 (`multi_stage_optimizer`)，这部分功能可以作为未来优化的起点。
- **[P2]代码可读性**: 部分函数较长，可以考虑重构以提高可维护性。





