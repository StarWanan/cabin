from cabin.src.Algorithm.routing.path_utils import *
from cabin.src.Algorithm.routing.optimizer import *
from cabin.src.vis.vis import visualize_graph

LINE_CAPACITY = 500


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
    routing_results = []
    paths = []
    for conn in device_connections:
        result = process_single_connection(graph, conn, paths, capacity=-1)
        routing_results.append(result)

    # step 3：局部搜索优化
    capacity_levels = [400, 350, 300, 290, 280, 250, 230, 200]  # 容量约束序列
    optimized_solutions = multi_stage_optimizer(graph, routing_results, capacity_levels)
    
    # 结果分析
    print("\n=== 多阶段优化结果 ===")
    for sol in optimized_solutions:
        print(f"容量限制: {sol['capacity']} | 总线长: {sol['total_length']:.2f}")
    
    # 选择最优解（示例选择最后一个合法解）
    best_solution = next((s for s in reversed(optimized_solutions) if s['solution']), None)
    if best_solution:
        routing_results = best_solution['solution']
        visualize_graph(nodes, connections, device, 
                       paths=[res['path_nodes'] for res in routing_results])

    # ==========
    # step 3：启发式优化
    # optimized_results = optimize_capacity(graph, routing_results)
    # routing_results = optimized_results

    # step 4: 输出结果与可视化
    # final_overload = sum(max(e.real_c - e.c, 0) for e in graph.edges)
    # print(f"\n最终状态: 总超载量={final_overload}")
    
    # # 优化后的结果分析
    # analyze_overload_results(graph, routing_results)
    
    # # 新增详细容量报告
    # print_capacity_report(graph)  
    
    # 总线长计算
    # total_length = calculate_total_cable_length(graph, routing_results)
    # print(f"\n总线长统计: {total_length:.2f} ")
    
    # 可视化
    # paths = []
    # for res in routing_results:
    #     conn = res['connection']
    #     print(f"\nConnection: {conn['device1']} -> {conn['device2']}")
    #     path = res['path_nodes']  
    #     for node in path:
    #         print(f"{node} ->", end="")
    #     print("")
    #     paths.append(path)
    # visualize_graph(nodes, connections, device, paths=paths) 
    
    

if __name__ == "__main__":
    main()
