import copy
from .a_star import a_star_route
from .path_utils import update_edge_real_capacity, get_edge_nodes, calculate_total_cable_length


def optimize_capacity(graph, routing_results, max_no_improve=50, initial_alpha=1.0, alpha_decay=0.9):
    """带目标函数的容量优化器"""

    # 目标函数 - 总超载量
    def calculate_total_overload():
        return sum(max(e.real_c - e.c, 0) for e in graph.edges)

    history_overload = []
    history_cable_length = []
    iteration = 0
    alpha = initial_alpha

    # 已超限边
    overload_edges = {edge.to: edge for edge in graph.edges if edge.real_c > edge.c}
    # 反向边映射表生成
    reverse_edge_map = build_reverse_edge_map(graph)

    current_overload = calculate_total_overload()
    current_cable_length = calculate_total_cable_length(graph, routing_results)

    while True:
        new_overload = calculate_total_overload()
        new_cable_length = calculate_total_cable_length(graph, routing_results)

        aim1 = new_overload
        aim2 = new_cable_length
        current_aim = aim1 + alpha * aim2

        if current_overload == new_overload:
            history_overload.append(current_overload)
        else:
            history_overload.clear()

        if current_cable_length == new_cable_length:
            history_cable_length.append(current_cable_length)
        else:
            history_cable_length.clear()

        current_overload = new_overload
        current_cable_length = new_cable_length

        # 终止条件判断
        if current_overload == 0:
            if len(history_cable_length) > max_no_improve:
                print(f"\n✅总超载量归零且总线长连续{max_no_improve}次无改进 @ iteration {iteration}")
                break
        else:
            if len(history_overload) > max_no_improve and (min(history_overload[-max_no_improve:]) >= current_overload):
                print(f"\n⛔总超载量连续{max_no_improve}次无改进 @ iteration {iteration}")
                break

        for result in routing_results:
            if needs_optimization(result['path_nodes'], overload_edges):
                new_path = reroute_connection(
                    graph,
                    result,
                    reverse_edge_map,
                    overload_edges
                )
                if validate_new_path(graph, new_path, result['connection']['load_rate']):
                    update_routing_result(graph, result, new_path, result['connection']['load_rate'])

        # 更新超限边集合
        overload_edges = {edge.to: edge for edge in graph.edges if edge.real_c > edge.c}

        iteration += 1
        alpha *= alpha_decay

    analyze_overload_results(graph, routing_results)
    return routing_results

def analyze_overload_results(graph, routing_results):
    """分析并打印超载边及其路径"""
    overload_edges = {i: e for i, e in enumerate(graph.edges) if e.real_c > e.c}
    if not overload_edges:
        print("\n所有线路容量正常")
        return
    
    print("\n超载线路报告:")
    # 打印超载边
    for edge_index, edge in overload_edges.items():
        from_node, to_node = get_edge_nodes(graph, edge_index)
        print(f"边 {edge_index} ({from_node} -> {to_node}): 容量 {edge.c} -> 使用量 {edge.real_c} (超载 {edge.real_c - edge.c})")
    
    # 查找涉及超载边的路径
    print("\n涉及超载边的路径:")
    for result in routing_results:
        path = result['path_nodes']
        load = result['connection']['load_rate']
        overload_segments = find_overload_segments(graph, path, overload_edges)
        
        if overload_segments:
            print(f"设备: {result['connection']['device1']} -> {result['connection']['device2']}, 负载率: {load}, 涉及超载边: {overload_segments}")

def find_overload_segments(graph, path, overload_edges):
    """找出路径中的超载边并返回包含节点坐标的信息"""
    segments = []
    for i in range(len(path) - 1):
        current = path[i]
        next_node = path[i + 1]
        edge_idx = graph.head[current]
        while edge_idx != -1:
            edge = graph.edges[edge_idx]
            if edge.to == next_node and edge_idx in overload_edges:
                current_coord = graph.nodes[current]
                next_coord = graph.nodes[next_node]
                segments.append({
                    "segment": f"{current}->{next_node}",
                    "current_coord": current_coord,
                    "next_coord": next_coord
                })
            edge_idx = edge.next
    return segments

def build_reverse_edge_map(graph):
    """构建反向边映射表"""
    reverse_map = {}
    for idx, edge in enumerate(graph.edges):
        if edge.to not in reverse_map:
            reverse_map[edge.to] = []
        reverse_map[edge.to].append((idx, edge))
    return reverse_map

def reroute_connection(graph, original_result, reverse_edge_map, forbidden_edges):
    """重新路由连接"""
    # 临时禁止使用超限边
    original_edges = copy.deepcopy(graph.edges)
    for edge_id in forbidden_edges:
        graph.edges[edge_id].d *= 100  # 通过增大距离权重使算法避开
        
    # 尝试重新寻路
    new_path = a_star_route(
        graph,
        original_result['start_node'],
        original_result['end_node']
    )
    
    # 恢复原始图数据
    graph.edges = original_edges
    return new_path or original_result['path_nodes']


def needs_optimization(path, overload_edges):
    """判断路径是否需要优化"""
    return any(node in overload_edges for node in path)

def update_routing_result(graph, result, new_path, load_rate):
    """更新路由结果并调整容量"""
    # 回退旧路径容量
    update_edge_real_capacity(graph, result['path_nodes'], load_rate)
    
    # 应用新路径
    result['path_nodes'] = new_path
    update_edge_real_capacity(graph, new_path, load_rate)
    
def validate_new_path(graph, new_path, load_rate):
    """验证新路径的容量有效性"""
    if not new_path:
        return False
        
    for i in range(len(new_path)-1):
        current = new_path[i]
        next_node = new_path[i+1]
        edge_idx = graph.head[current]
        while edge_idx != -1:
            edge = graph.edges[edge_idx]
            if edge.to == next_node and (edge.real_c + load_rate) > edge.c:
                return False
            edge_idx = edge.next
    return True