import plotly.graph_objects as go
from cabin.src.data.layer1 import nodes as nodes1, connections as connections1
from cabin.src.data.layer2 import nodes as nodes2, connections as connections2
from cabin.src.data.layer3 import nodes as nodes3, connections as connections3
from cabin.src.data.layer4 import nodes as nodes4, connections as connections4

nodes = {**nodes1, **nodes2, **nodes3, **nodes4}
connections = connections1 + connections2 + connections3 + connections4

# 提取节点的坐标
x_coords = [coord[0] for coord in nodes.values()]
y_coords = [coord[1] for coord in nodes.values()]
z_coords = [coord[2] for coord in nodes.values()]
node_names = list(nodes.keys())


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
        size=1,  # 节点大小
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
