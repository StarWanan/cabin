from cabin.src.Algorithm.routing.path_utils import *
from cabin.src.Algorithm.routing.optimizer import *
from cabin.src.vis.vis import visualize_graph
from cabin.src.Algorithm.dwg.dwg_read import dwg_api
from cabin.src.Algorithm.real_data.real_data_read import real_data_api

LINE_CAPACITY = 500
MOCK_DATA = False
TEST_DXF = False
REAL_DATA = True


def main():
    data_sources = {
        "MOCK_DATA": MOCK_DATA,
        "TEST_DXF": TEST_DXF,
        "REAL_DATA": REAL_DATA,  # 添加到数据源字典
    }
    active_sources = [name for name, is_active in data_sources.items() if is_active]
    if len(active_sources) == 0:
        raise ValueError("必须至少启用一个数据源！")
    if len(active_sources) > 1:
        raise ValueError(f"只能启用一个数据源，但目前多个数据源被启用：{', '.join(active_sources)}")

    # step 1：环境初始化
    # 初始化网络
    if MOCK_DATA:
        nodes, connections = initialize_network()
        from cabin.src.data.device import device
    elif TEST_DXF:
        nodes, connections, device, device_connections = dwg_api(file_path="../data/test.dxf")
    elif REAL_DATA:
        nodes, connections, device, device_connections = real_data_api(directory_path="../data/ExportDtas")

    graph = build_graph(nodes, connections, LINE_CAPACITY, custom_capacity=True)

    if MOCK_DATA:
         from cabin.src.data import device_connection
         device_connections = device_connection.generate_device_connections(
             seed=42, num_pairs=10
         )

    if REAL_DATA:
        routing_results = []
        paths_for_viz = [] # Renamed to avoid conflict if 'paths' is used elsewhere
        for conn in device_connections:
            result = process_single_connection(graph, conn, paths_for_viz, device, capacity=-1)
            if result: #确保 result 不是 None
                 routing_results.append(result)
        
        extracted_paths = [
            # 补充起点和终点到路径中（避免重复检查：如果path_nodes已包含起点/终点则跳过）
            [res['device1_coord']] + res['path_nodes'] + [res['device2_coord']] 
            # [res['start_node']] + res['path_nodes'] + [res['end_node']] 
            # if (res['path_nodes'] and res['path_nodes'][0] != res['start_node'] and res['path_nodes'][-1] != res['end_node'])
            # else res['path_nodes']
            for res in routing_results 
            if res and 'path_nodes' in res and res['path_nodes']
        ]
        print(f"可视化的路径数量：{len(extracted_paths)}条")

        # 可视化结果
        visualize_graph(
            nodes, 
            connections, 
            device,
            paths=extracted_paths, # 使用从 routing_results 提取的路径
            sample_ratio_nodes=1,           # 显示节点率
            sample_ratio_connections=1,     # 显示连接率
            max_paths_to_display=30,      # 显示路径数量上限
            show_node_labels=False,       # 关闭节点标签以提高性能
            node_marker_size=0.8,         # 较小的节点标记
            device_marker_size=1,         # 较小的设备标记
            connection_line_width=1.3       # 较细的连接线
        )
        return

    # step 2：初始化路径
    routing_results = []
    paths = []
    for conn in device_connections:
        result = process_single_connection(graph, conn, paths, device, capacity=-1)
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
        visualize_graph(
            nodes, 
            connections, 
            device,
            paths=[res['path_nodes'] for res in routing_results if res and 'path_nodes' in res and res['path_nodes']],
            sample_ratio_nodes=1.0, # 或者根据需要调整
            show_node_labels=True   # 在最终优化结果中可以考虑显示标签
        )


if __name__ == "__main__":
    main()
