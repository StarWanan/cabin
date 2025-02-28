import plotly.graph_objects as go

# 定义节点坐标 (x, y, z)
nodes = {
    "A1": (0, 0, 0),
    "A2": (5, 0, 0),
    "A3": (10, 0, 0),
    "A4": (15, 5, 5),
    "A5": (5, 10, 0),
    "A6": (10, 10, 0),
    "A7": (10, 10, 5),
    "B2": (20, 5, 5),
    "B3": (25, 5, 5),
}

# 定义线缆连接关系
connections = [
    ("A1", "A2"),
    ("A2", "A3"),
    ("A3", "A4"),
    ("A2", "A5"),
    ("A5", "A6"),
    ("A6", "A7"),
    ("A4", "B2"),
    ("A4", "B3"),
]

# 提取节点的坐标
x_coords = [coord[0] for coord in nodes.values()]
y_coords = [coord[1] for coord in nodes.values()]
z_coords = [coord[2] for coord in nodes.values()]
node_names = list(nodes.keys())

# 创建 3D 散点图（节点）
node_trace = go.Scatter3d(
    x=x_coords,
    y=y_coords,
    z=z_coords,
    mode='markers+text',
    marker=dict(
        size=5,  # 节点大小
        color='red',  # 节点颜色
        opacity=0.8
    ),
    text=node_names,  # 节点名称
    textposition="top center"
)

# 创建线缆（连接）
line_traces = []
for start, end in connections:
    # 获取起点和终点的坐标
    x_line = [nodes[start][0], nodes[end][0], None]  # None 用于分隔线段
    y_line = [nodes[start][1], nodes[end][1], None]
    z_line = [nodes[start][2], nodes[end][2], None]
    
    # 创建线缆
    line_trace = go.Scatter3d(
        x=x_line,
        y=y_line,
        z=z_line,
        mode='lines',
        line=dict(
            color='purple',  # 线缆颜色
            width=3
        )
    )
    line_traces.append(line_trace)

# 合并节点和线缆
fig = go.Figure(data=[node_trace] + line_traces)

# 设置图形布局
fig.update_layout(
    scene=dict(
        xaxis_title='X Axis',
        yaxis_title='Y Axis',
        zaxis_title='Z Axis',
        aspectmode='data'  # 保持比例
    ),
    title="船舶主干线缆节点和连接示意图",
    showlegend=False
)

# 显示图形
fig.show()
