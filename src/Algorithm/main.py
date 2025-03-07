from cabin.src.Algorithm.routing.path_utils import *
from cabin.src.Algorithm.routing.optimizer import optimize_capacity
from cabin.src.vis.vis import visualize_graph

LINE_CAPACITY = 100


def main():
    # step 1：环境初始化
    # 初始化网络
    nodes, connections = initialize_network()
    graph = build_graph(nodes, connections, LINE_CAPACITY)
    
    # 生成设备连接
    device_connections = device_connection.generate_device_connections(
        seed=42, num_pairs=10
    )

    # step 2：初始化路径
    # 处理所有连接
    routing_results = []
    paths = []
    for conn in device_connections:
        result = process_single_connection(graph, conn, paths)
        routing_results.append(result)

    # step 3：启发式优化
    optimize_capacity(graph, routing_results)

    # step 4: 输出结果与可视化
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
