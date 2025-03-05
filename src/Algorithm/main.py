from cabin.src.vis.vis import remove_duplicate_nodes, visualize_graph  
from cabin.src.data import (
    layer1, layer2, layer3, layer4,
    hub, device_connection
)
from cabin.src.data.device import device  # 直接导入设备字典

from cabin.src.vis.vis import remove_duplicate_nodes
from Algorithm.graph import build_graph
from Algorithm.routing import (
    a_star_route,
    get_coordinates,
    update_edge_real_capacity
)
from Algorithm.routing.optimizer import optimize_capacity

# 合并各层节点/连接的导入
def load_network_data():
    """统一加载所有网络层数据"""
    nodes = {**layer1.nodes, **layer2.nodes, **layer3.nodes, 
            **layer4.nodes, **hub.nodes}
    connections = (layer1.connections + layer2.connections +
                  layer3.connections + layer4.connections +
                  hub.connections)
    return nodes, connections

LINE_CAPACITY = 100


def initialize_network():
    """初始化网络拓扑结构"""
    nodes, connections = load_network_data()
    return remove_duplicate_nodes(nodes, connections)

def process_single_connection(graph, conn, paths):
    """处理单个设备连接的路径计算"""
    dev1_coord = device[conn["device1"]]
    dev2_coord = device[conn["device2"]]
    
    # 节点定位
    start_node = graph.find_nearest_node(*dev1_coord)
    end_node = graph.find_nearest_node(*dev2_coord)
    
    # 路径计算
    path = a_star_route(graph, start_node, end_node) or []
    path = [path] if path and not isinstance(path, list) else path
    
    # 结果记录
    result = {
        "connection": conn,
        "path_nodes": path,
        "start_node": start_node,
        "end_node": end_node
    }
    
    # 输出结果
    print(f"\nConnection: {conn['device1']} -> {conn['device2']}")
    print(f"Load rate: {conn['load_rate']}")
    if path:
        print_path_details(graph, path)
        paths.append(path)
        update_edge_real_capacity(graph, path, conn["load_rate"])
    else:
        print("No valid path found")
    
    return result

def print_path_details(graph, path):
    """打印路径详细信息"""
    print(f"Path: {' -> '.join(map(str, path))}")
    coordinates = get_coordinates(graph, path)
    coordinates_str = ' -> '.join(map(str, coordinates))
    print(f"Coordinates: {coordinates_str}")

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
        for i in range(len(path)-1):
            current = path[i]
            next_node = path[i+1]
            
            # 查找对应边的距离
            edge_idx = graph.head[current]
            while edge_idx != -1:
                edge = graph.edges[edge_idx]
                if edge.to == next_node:
                    total_length += edge.d
                    break
                edge_idx = edge.next
                
    return total_length

def main():
    # 初始化网络
    nodes, connections = initialize_network()
    graph = build_graph(nodes, connections, LINE_CAPACITY)
    
    # 生成设备连接
    device_connections = device_connection.generate_device_connections(
        seed=42, num_pairs=10
    )
    
    # 处理所有连接
    routing_results = []
    paths = []
    for conn in device_connections:
        result = process_single_connection(graph, conn, paths)
        routing_results.append(result)
    
    optimized_results = optimize_capacity(graph, routing_results)
    
    final_overload = sum(max(e.real_c - e.c, 0) for e in graph.edges)
    print(f"\n最终状态: 总超载量={final_overload}")

    print_capacity_report(graph)
    
    # 总线长计算
    total_length = calculate_total_cable_length(graph, routing_results)
    print(f"\n总线长统计: {total_length:.2f} ")
    
    # 可视化
    visualize_graph(nodes, connections, device, paths=paths)

if __name__ == "__main__":
    main()
