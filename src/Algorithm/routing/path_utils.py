from cabin.src.Algorithm.graph.structure import Graph
from cabin.src.data import (
    layer1, layer2, layer3, layer4,
    hub, device_connection
)
from cabin.src.vis.vis import remove_duplicate_nodes
from .a_star import a_star_route


def build_graph(nodes, connections, line_capacity, custom_capacity=False, custom_capacities=None, node_metadata=None):
    """根据nodes和connections建立图"""
    node_list = [(0, 0, 0)] + [nodes[key] for key in sorted(nodes.keys())]
    node_metadata_list = [None] + [node_metadata[key] for key in sorted(node_metadata.keys())] if node_metadata else None
    if node_metadata is None:
        graph = Graph(node_list)
    else:
        graph = Graph(node_list, node_metadata_list)
    node_index_map = {key: idx + 1 for idx, key in enumerate(sorted(nodes.keys()))}
    for u, v, category in connections:  # 现在connections包含类型
        u_idx = node_index_map[u]
        v_idx = node_index_map[v]
        if custom_capacity:
            from cabin.src.data.custom_capacities import custom_capacities
            # 检查用户是否提供了自定义容量
            capacity = (
                custom_capacities.get((u, v)) or
                custom_capacities.get((v, u)) or
                custom_capacities.get((u_idx, v_idx)) or
                custom_capacities.get((v_idx, u_idx)) or
                line_capacity
            )
        else:
            # 使用默认容量
            capacity = line_capacity
        # 添加双向边
        graph.add_bidirectional_edge(u_idx, v_idx, capacity, category)  # 传递隧道类型

    return graph

def get_coordinates(graph, node_list):
    """根据path的节点编号返回坐标"""
    coordinates = []
    for node in node_list:
        if 1 <= node < len(graph.nodes):
            coordinates.append(graph.nodes[node])
        else:
            coordinates.append(None)  # 如果节点编号无效，返回None
    return coordinates

def get_edge_nodes(graph, edge_index):
    """
    根据边的编号返回这条边连接的两个节点
    """
    if 0 <= edge_index < len(graph.edges):
        edge = graph.edges[edge_index]
        return graph.nodes[edge.from_node], graph.nodes[edge.to]
    return None

def update_edge_real_capacity(graph, path, load_rate, is_add=True):
    """更新路径上所有边的实际容量（新增反向边处理）"""
    sign = 1 if is_add else -1  # 标记是增加还是减少
    for i in range(len(path) - 1):
        current_node = path[i]
        next_node = path[i + 1]
        
        # 正向边
        edge_idx = graph.head[current_node]
        while edge_idx != -1:
            edge = graph.edges[edge_idx]
            if edge.to == next_node:
                edge.real_c += sign * load_rate
            edge_idx = edge.next
        
        # 反向边
        reverse_edge_idx = graph.head[next_node]
        while reverse_edge_idx != -1:
            reverse_edge = graph.edges[reverse_edge_idx]
            if reverse_edge.to == current_node:
                reverse_edge.real_c += sign * load_rate
            reverse_edge_idx = reverse_edge.next


def load_network_data():
    """统一加载所有网络层数据"""
    nodes = {**layer1.nodes, **layer2.nodes, **layer3.nodes,
             **layer4.nodes, **hub.nodes}
    connections = (layer1.connections + layer2.connections +
                   layer3.connections + layer4.connections +
                   hub.connections)
    return nodes, connections


def initialize_network():
    """初始化网络拓扑结构"""
    nodes, connections = load_network_data()
    return remove_duplicate_nodes(nodes, connections)


def process_single_connection(graph, conn, paths, device, capacity=-1):
    """处理单个设备连接的路径计算"""
    # 检查设备是否存在于 device 字典中
    if conn["device1"] not in device or conn["device2"] not in device:
        print(f"Skipping connection: {conn['device1']} -> {conn['device2']} (devices not found)")
        return None

    # 获取设备坐标
    dev1_coord = device[conn["device1"]]
    dev2_coord = device[conn["device2"]]
    # 获取设备连接需要的cable_category
    cable_category = conn["cable_category"]

    # 节点定位
    # start_node = graph.find_nearest_node(*dev1_coord)
    # end_node = graph.find_nearest_node(*dev2_coord)

    # start_node = graph.find_nearest_node_any_z(*dev1_coord)
    # end_node = graph.find_nearest_node_any_z(*dev2_coord)

    start_node, start_node_value = graph.find_nearest_node_by_layer_ptype_and_cable_category(*dev1_coord, cable_category)
    end_node, end_node_value = graph.find_nearest_node_by_layer_ptype_and_cable_category(*dev2_coord, cable_category)

    # 路径计算时传递电缆类型
    path = a_star_route(
        graph, 
        start_node, 
        end_node, 
        capacity=capacity, 
        cable_category=conn["cable_category"]  # 传递当前连接的电缆类型
    ) or []
    path = [path] if path and not isinstance(path, list) else path

    # 结果记录
    result = {
        "connection": conn,
        "path_nodes": path,
        "start_node": start_node,
        "end_node": end_node,
        "device1_coord": dev1_coord,
        "device2_coord": dev2_coord
    }

    # 输出结果
    print(f"\nConnection: {conn['device1']}[{dev1_coord}] -> {conn['device2']}[{dev2_coord}]")
    print(f"device start_node:{start_node}, device end_node:{end_node}, start_node_value:{start_node_value}, end_node_value:{end_node_value}")
    print(f"Load rate: {conn['load_rate']}")
    if path:
        print_path_details(graph, path)
        paths.append(path)
        # 更新边的容量
        update_edge_real_capacity(graph, path, conn["load_rate"])
    else:
        print("No valid path found")

    return result

def print_path_details(graph, path):
    """打印路径详细信息"""
    # 新增节点编号路径显示
    print(f"Path: {' -> '.join(map(str, path))}") 
    coordinates = get_coordinates(graph, path)
    coordinates_str = ' -> '.join(map(str, coordinates))
    print(f"Path coordinates: {coordinates_str}")

def print_capacity_report(graph):
    """生成容量统计报告"""
    print("\n线路容量统计:")
    for edge in graph.edges:
        if edge.real_c == 0:
            continue
        usage_rate = edge.real_c / edge.c * 100
        print(f"Edge {edge.to} 总容量: {edge.c} 使用量: {edge.real_c} ({usage_rate:.1f}%)")


def calculate_total_cable_length(graph, routing_results):
    """计算所有路径的总线长"""
    total_length = 0

    for result in routing_results:
        path = result['path_nodes']
        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]

            # 查找对应边的距离
            edge_idx = graph.head[current]
            while edge_idx != -1:
                edge = graph.edges[edge_idx]
                if edge.to == next_node:
                    total_length += edge.d
                    break
                edge_idx = edge.next

    return total_length