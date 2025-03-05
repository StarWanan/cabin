import copy
from . import a_star_route

def optimize_capacity(graph, routing_results, max_no_improve=50):
    """带目标函数的容量优化器"""
    # 目标函数 - 总超载量
    def calculate_total_overload():
        return sum(max(e.real_c - e.c, 0) for e in graph.edges)
    
    history = []
    iteration = 0
    overload_edges = set()
    
    # 已超限边
    overload_edges = {edge.to: edge for edge in graph.edges if edge.real_c > edge.c}
    # 反向边映射表生成
    reverse_edge_map = build_reverse_edge_map(graph)

    current_overload = calculate_total_overload()
    while True:
        new_overload = calculate_total_overload()
        if current_overload == new_overload:
            history.append(current_overload)
        else:
            history.clear()
        
        current_overload = new_overload
        # 终止条件判断
        if current_overload == 0:
            print(f"✅ 总超载量归零 @ iteration {iteration}")
            break
        if len(history) > max_no_improve and (min(history[-max_no_improve:]) >= current_overload):
            print(f"⛔ 连续{max_no_improve}次无改进")
            break

        # # 没有过载边
        # if not overload_edges:
        #     break
            
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
    
    analyze_overload_results(graph, routing_results)
    return routing_results


def analyze_overload_results(graph, routing_results):
    """分析并打印超载边及其路径"""
    overload_edges = {e.to: e for e in graph.edges if e.real_c > e.c}
    if not overload_edges:
        print("\n所有线路容量正常")
        return
    
    print("\n超载线路报告:")
    # 打印超载边
    for to, edge in overload_edges.items():
        print(f"边 {to}: 容量 {edge.c} -> 使用量 {edge.real_c} (超载 {edge.real_c - edge.c})")
    
    # 查找涉及超载边的路径
    print("\n涉及超载边的路径:")
    for result in routing_results:
        path = result['path_nodes']
        load = result['connection']['load_rate']
        overload_segments = find_overload_segments(graph, path, overload_edges)
        
        if overload_segments:
            print(f"路径: {'->'.join(map(str, path))}")
            print(f"设备: {result['connection']['device1']} -> {result['connection']['device2']}")
            print(f"负载率: {load}, 涉及超载边: {overload_segments}")

def find_overload_segments(graph, path, overload_edges):
    """找出路径中的超载边"""
    segments = []
    for i in range(len(path)-1):
        current = path[i]
        next_node = path[i+1]
        edge_idx = graph.head[current]
        while edge_idx != -1:
            edge = graph.edges[edge_idx]
            if edge.to == next_node and edge.to in overload_edges:
                segments.append(f"{current}->{next_node}")
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
    from .path_utils import update_edge_real_capacity
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