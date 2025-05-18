from cabin.src.data.layer1 import nodes as nodes1, connections as connections1
from cabin.src.data.layer2 import nodes as nodes2, connections as connections2
from cabin.src.data.layer3 import nodes as nodes3, connections as connections3
from cabin.src.data.layer4 import nodes as nodes4, connections as connections4
from cabin.src.data.hub import nodes as nodes_hub, connections as connections_hub
from cabin.src.data.device import device
import random
import os


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

def visualize_graph(nodes, connections, device=None, paths=None,
                    sample_ratio_nodes=1.0, sample_ratio_connections=1.0,
                    max_paths_to_display=None, show_node_labels=True,
                    show_device_labels=False, # 新增参数，默认为False
                    node_marker_size=1, device_marker_size=1,
                    connection_line_width=1.5, path_line_width=3):
    """可视化节点、连接、设备和路径，并支持采样和自定义样式"""
    import plotly.graph_objects as go

    # 1. 节点采样
    sampled_nodes = nodes
    if sample_ratio_nodes < 1.0 and len(nodes) > 0:
        num_sampled_nodes = int(len(nodes) * sample_ratio_nodes)
        if num_sampled_nodes == 0 and len(nodes) > 0: # 确保至少采样一个节点（如果存在）
            num_sampled_nodes = 1
        sampled_node_keys = random.sample(list(nodes.keys()), num_sampled_nodes)
        sampled_nodes = {key: nodes[key] for key in sampled_node_keys}

    # 提取采样后节点的坐标
    x_coords = [coord[0] for coord in sampled_nodes.values()]
    y_coords = [coord[1] for coord in sampled_nodes.values()]
    z_coords = [coord[2] for coord in sampled_nodes.values()]
    node_names = list(sampled_nodes.keys()) if show_node_labels else None # 根据参数决定是否显示标签

    # 创建 3D 散点图（节点）
    node_trace = go.Scatter3d(
        x=x_coords,
        y=y_coords,
        z=z_coords,
        mode='markers+text' if show_node_labels and node_names else 'markers',
        marker=dict(
            size=node_marker_size, # 可配置
            color='red',
            opacity=0.8
        ),
        text=node_names,
        textposition="top center"
    )
    traces = [node_trace]

    # 2. 设备可视化
    if device:
        x_device = [coord[0] for coord in device.values()]
        y_device = [coord[1] for coord in device.values()]
        z_device = [coord[2] for coord in device.values()]
        device_names = list(device.keys())

        device_trace = go.Scatter3d(
            x=x_device,
            y=y_device,
            z=z_device,
            mode='markers+text' if show_device_labels else 'markers', # 根据参数决定是否固定显示文本
            marker=dict(
                size=device_marker_size,
                color='orange',
                opacity=0.8
            ),
            text=device_names, # 文本内容，用于悬停提示或固定显示
            hoverinfo='text',   # 明确指定悬停时显示文本
            textposition="top center" # 文本标签的位置（如果显示）
        )
        traces.append(device_trace)

    # 3. 连接线采样和批量绘制
    sampled_connections = connections
    if sample_ratio_connections < 1.0 and len(connections) > 0:
        num_sampled_connections = int(len(connections) * sample_ratio_connections)
        if num_sampled_connections == 0 and len(connections) > 0: # 确保至少采样一个连接
             num_sampled_connections = 1
        sampled_connections_indices = random.sample(range(len(connections)), num_sampled_connections)
        sampled_connections = [connections[i] for i in sampled_connections_indices]

    # 过滤掉那些端点不在 sampled_nodes 中的连接
    valid_sampled_connections = []
    if sampled_nodes: # 只有在有采样节点时才进行连接过滤
        for start_node_key, end_node_key in sampled_connections:
            if start_node_key in sampled_nodes and end_node_key in sampled_nodes:
                valid_sampled_connections.append((start_node_key, end_node_key))
    else: # 如果没有采样节点，则不显示任何连接
        valid_sampled_connections = []

    all_lines_x = []
    all_lines_y = []
    all_lines_z = []
    if sampled_nodes: # 确保 sampled_nodes 不为空
        for start, end in valid_sampled_connections:
            # 确保连接的节点在采样后的节点列表中
            if start in sampled_nodes and end in sampled_nodes:
                all_lines_x.extend([sampled_nodes[start][0], sampled_nodes[end][0], None])
                all_lines_y.extend([sampled_nodes[start][1], sampled_nodes[end][1], None])
                all_lines_z.extend([sampled_nodes[start][2], sampled_nodes[end][2], None])

    if all_lines_x:
        connections_trace = go.Scatter3d(
            x=all_lines_x,
            y=all_lines_y,
            z=all_lines_z,
            mode='lines',
            line=dict(
                color='#1f77b4',
                width=connection_line_width # 可配置
            ),
            name='Connections'
        )
        traces.append(connections_trace)
    
    # 4. 路径可视化（直接绘制所有路径，不考虑节点采样）
    path_colors = [
        'red', 'green', 'blue', 'purple', 'orange', 'brown', 'pink', 'gray', 'cyan', 'magenta'
    ]

    # 4. 路径采样和可视化
    sampled_paths = paths
    print(f"总共可视化的路径数量：{len(sampled_paths)}条")

    if paths and max_paths_to_display is not None and len(paths) > max_paths_to_display:
        sampled_paths = random.sample(paths, max_paths_to_display)

    print(f"采样可视化的路径数量：{len(sampled_paths)}条")
        
    if sampled_paths:  # 仅检查路径是否存在，不依赖节点采样
        # 使用原始节点字典解析路径坐标
        original_node_keys_sorted = sorted(nodes.keys())  
        node_id_to_key = {i+1: key for i, key in enumerate(original_node_keys_sorted)}  # 节点ID到key的映射

        for idx, path in enumerate(sampled_paths):
            # 新增：打印当前路径的节点ID/坐标及对应坐标
            print(f"路径{idx+1}经过的节点ID/坐标及对应坐标：")
            path_coords = []  # 提前初始化坐标列表
            for item in path:
                if isinstance(item, int):  # 处理节点ID
                    node_id = item
                    if 0 < node_id <= len(original_node_keys_sorted):  
                        node_key = node_id_to_key[node_id]
                        coord = nodes[node_key]
                        print(f"  节点ID: {node_id}, 坐标: ({coord[0]}, {coord[1]}, {coord[2]})")
                        path_coords.append(coord)
                    else:
                        print(f"  节点ID: {node_id}（超出范围，无坐标）")
                elif isinstance(item, tuple) and len(item) == 3:  # 处理坐标元组
                    coord = item
                    print(f"  直接坐标: ({coord[0]}, {coord[1]}, {coord[2]})")
                    path_coords.append(coord)
                else:
                    print(f"  无效元素类型: {type(item)}（跳过）")
    
            if not path_coords:  # 仅跳过完全无坐标的路径
                print(f"路径{idx+1}无有效坐标，跳过绘制")
                continue

            # 提取路径坐标（相邻节点连线）
            path_x, path_y, path_z = [], [], []
            for i in range(len(path_coords) - 1):
                start_coord = path_coords[i]
                end_coord = path_coords[i+1]
                path_x.extend([start_coord[0], end_coord[0], None])
                path_y.extend([start_coord[1], end_coord[1], None])
                path_z.extend([start_coord[2], end_coord[2], None])
            
            if path_x:
                path_trace = go.Scatter3d(
                    x=path_x,
                    y=path_y,
                    z=path_z,
                    mode='lines',
                    line=dict(
                        color=path_colors[idx % len(path_colors)],
                        width=path_line_width  # 保持配置的线宽
                    ),
                    name=f'Path {idx + 1}'  # 图例显示路径编号
                )
                traces.append(path_trace)
            else:
                print(f"路径{idx+1}无有效坐标x，跳过绘制")

    # 合并图形
    fig = go.Figure(data=traces)
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

    # 新增：保存可视化结果到log目录（带时间戳）
    import datetime  # 新增导入
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # 生成时间戳（与log目录格式一致）
    if not os.path.exists("log"):
        os.makedirs("log")
    save_path = f"log/vis_{timestamp}.html"  # 保存路径
    fig.write_html(save_path)  # 保存为交互式HTML文件（保留交互功能）
    print(f"可视化结果已保存至：{save_path}")  # 控制台提示保存路径

    fig.show()


if __name__ == "__main__":
    # 提取节点的坐标
    nodes_data = {**nodes1, **nodes2, **nodes3, **nodes4, **nodes_hub}
    connections_data = connections1 + connections2 + connections3 + connections4 + connections_hub
    nodes_data, connections_data = remove_duplicate_nodes(nodes_data, connections_data)

    # 示例：使用采样参数
    visualize_graph(
        nodes_data, 
        connections_data, 
        device,
        paths=None, 
        sample_ratio_nodes=0.5,       
        sample_ratio_connections=0.3, 
        max_paths_to_display=10,      
        show_node_labels=False,       
        show_device_labels=False, # 示例：设备标签默认不固定显示，悬停可见
        node_marker_size=0.5,
        connection_line_width=1
    )