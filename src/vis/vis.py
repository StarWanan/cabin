import plotly.graph_objects as go
from cabin.src.data.layer1 import nodes as nodes1, connections as connections1
from cabin.src.data.layer2 import nodes as nodes2, connections as connections2
from cabin.src.data.layer3 import nodes as nodes3, connections as connections3
from cabin.src.data.layer4 import nodes as nodes4, connections as connections4
from cabin.src.data.hub import nodes as nodes_hub, connections as connections_hub
from cabin.src.data.device import device


def remove_duplicate_nodes(nodes, connections):
    # Create a dictionary to map node values to their first unique key
    value_to_key = {}
    new_nodes = {}
    for key, value in nodes.items():
        if value not in value_to_key:
            value_to_key[value] = key
            new_nodes[key] = value

    # Update connections to use the first unique key
    new_connections = []
    for conn in connections:
        new_conn = (value_to_key[nodes[conn[0]]], value_to_key[nodes[conn[1]]])
        new_connections.append(new_conn)

    return new_nodes, new_connections



def visualize_graph(nodes, connections, device, path=None):
    """可视化节点、连接、设备和路径"""
    import plotly.graph_objects as go

    # 提取节点的坐标
    x_coords = [coord[0] for coord in nodes.values()]
    y_coords = [coord[1] for coord in nodes.values()]
    z_coords = [coord[2] for coord in nodes.values()]
    node_names = list(nodes.keys())

    # 提取设备坐标
    x_device = [coord[0] for coord in device.values()]
    y_device = [coord[1] for coord in device.values()]
    z_device = [coord[2] for coord in device.values()]
    device_names = list(device.keys())

    # 创建 3D 散点图（节点）
    node_trace = go.Scatter3d(
        x=x_coords,
        y=y_coords,
        z=z_coords,
        mode='markers+text',
        marker=dict(
            size=1,
            color='red',
            opacity=0.8
        ),
        text=node_names,
        textposition="top center"
    )

    # 创建 3D 散点图（设备）
    device_trace = go.Scatter3d(
        x=x_device,
        y=y_device,
        z=z_device,
        mode='markers+text',
        marker=dict(
            size=3,
            color='orange',
            opacity=0.8
        ),
        text=device_names,
        textposition="top center"
    )

    # 创建线缆连接
    line_traces = []
    for start, end in connections:
        x_line = [nodes[start][0], nodes[end][0], None]
        y_line = [nodes[start][1], nodes[end][1], None]
        z_line = [nodes[start][2], nodes[end][2], None]

        line_trace = go.Scatter3d(
            x=x_line,
            y=y_line,
            z=z_line,
            mode='lines',
            line=dict(
                color='#1f77b4',  # 基础连接线颜色
                width=2
            )
        )
        line_traces.append(line_trace)

    # 添加路径可视化
    if path:
        sorted_keys = sorted(nodes.keys())
        path_coords = [nodes[sorted_keys[node_id - 1]] for node_id in path]

        # 生成路径线段
        path_x, path_y, path_z = [], [], []
        for i in range(len(path_coords) - 1):
            start = path_coords[i]
            end = path_coords[i + 1]
            path_x += [start[0], end[0], None]
            path_y += [start[1], end[1], None]
            path_z += [start[2], end[2], None]

        path_trace = go.Scatter3d(
            x=path_x,
            y=path_y,
            z=path_z,
            mode='lines',
            line=dict(
                color='red',
                width=6
            ),
            name='A* Path'
        )
        line_traces.append(path_trace)

    # 合并图形
    fig = go.Figure(data=[node_trace, device_trace] + line_traces)
    fig.update_layout(
        scene=dict(
            xaxis_title='X Axis',
            yaxis_title='Y Axis',
            zaxis_title='Z Axis',
            aspectmode='data'
        ),
        title="船舶主干线缆节点和连接示意图",
        showlegend=True
    )

    fig.show()


if __name__ == "__main__":
    # 提取节点的坐标
    nodes = {**nodes1, **nodes2, **nodes3, **nodes4, **nodes_hub}
    connections = connections1 + connections2 + connections3 + connections4 + connections_hub
    nodes, connections = remove_duplicate_nodes(nodes, connections)

    visualize_graph(nodes, connections, device)