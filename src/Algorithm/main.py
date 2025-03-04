# 导入数据
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

def main():
    # 主逻辑封装为函数
    nodes, connections = load_network_data()
    nodes, connections = remove_duplicate_nodes(nodes, connections)
    graph = build_graph(nodes, connections, LINE_CAPACITY)

    # 生成设备连接
    device_connections = device_connection.generate_device_connections(
        seed=42, num_pairs=10
    )

    routing_results = []
    paths = [] # 可视化用

    for conn in device_connections:
        dev1_coord = device[conn["device1"]]
        dev2_coord = device[conn["device2"]]

        # 定位最近网络节点
        start_node = graph.find_nearest_node(*dev1_coord)
        end_node = graph.find_nearest_node(*dev2_coord)

        # 计算路径
        path = a_star_route(graph, start_node, end_node)

        result = {
            "connection": conn,
            "path_nodes": path,
            "start_node": start_node,
            "end_node": end_node
        }
        routing_results.append(result)

        print(f"\nConnection: {conn['device1']} -> {conn['device2']}")
        print(f"Load rate: {conn['load_rate']}")
        if path:
            print(f"Path: {' -> '.join(map(str, path))}")
            coordinates = get_coordinates(graph, path)
            coordinates_str = ' -> '.join(map(str, coordinates))
            print(f"Coordinates: {coordinates_str}")
            paths.append(path)

            update_edge_real_capacity(graph, path, conn["load_rate"])
        else:
            print("No valid path found")

    # visualize_graph(nodes, connections, device, paths=paths)

    # for edge in graph.edges:
    #     print(f"Edge to {edge.to}, real capacity: {edge.real_c}")


if __name__ == "__main__":
    main()
