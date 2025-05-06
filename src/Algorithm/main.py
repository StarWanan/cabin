from cabin.src.Algorithm.routing.path_utils import *
from cabin.src.Algorithm.routing.optimizer import *
from cabin.src.vis.vis import visualize_graph
from cabin.src.Algorithm.dwg.dwg_read import dwg_api
from cabin.src.Algorithm.real_data import real_data_api

LINE_CAPACITY = 500
MOCK_DATA = True
TEST_DXF = False
REAL_DATA = False


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
        nodes, connections, device, device_connections = dwg_api(file_path="../../test.dxf")
    elif REAL_DATA:
        nodes, connections, device, device_connections = real_data_api(directory_path="ExportDtas")

    graph = build_graph(nodes, connections, LINE_CAPACITY, custom_capacity=True)

    if REAL_DATA:
        routing_results = []
        paths = []
        for conn in device_connections:
            result = process_single_connection(graph, conn, paths, device, capacity=-1)
            routing_results.append(result)

        # 可视化结果
        visualize_graph(nodes, connections, device,
                        paths=[res['path_nodes'] for res in routing_results])
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
        visualize_graph(nodes, connections, device,
                        paths=[res['path_nodes'] for res in routing_results])


if __name__ == "__main__":
    main()
