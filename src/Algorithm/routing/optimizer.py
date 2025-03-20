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

    # 修改超限边判定逻辑（关键修改点）
    edge_map = {(e.from_node, e.to): idx for idx, e in enumerate(graph.edges)}
    overload_edges = {}
    processed = set()
    
    for idx, edge in enumerate(graph.edges):
        if idx in processed:
            continue
            
        # 查找反向边
        reverse_key = (edge.to, edge.from_node)
        reverse_idx = edge_map.get(reverse_key, None)
        
        if reverse_idx is not None and reverse_idx != idx:
            reverse_edge = graph.edges[reverse_idx]
            processed.add(idx)
            processed.add(reverse_idx)
            # 合并双向边容量判断
            total_c = edge.c + reverse_edge.c
            total_real_c = edge.real_c + reverse_edge.real_c
            if total_real_c > total_c:
                overload_edges[idx] = edge
                overload_edges[reverse_idx] = reverse_edge
        else:
            # 单向边独立判断
            if edge.real_c > edge.c:
                overload_edges[idx] = edge

    # 生成用于路径检测的节点集合
    overload_nodes = {edge.to for edge in overload_edges.values()}
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

        # 新增迭代日志
        print(f"\n=== 迭代 {iteration} [α={alpha:.2f}] ===")
        print(f"当前目标值: 超载量={new_overload} 线长={new_cable_length} 综合={current_aim}")

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
        # 错误：恢复旧判定方式 ↓
        # overload_edges = {edge.to: edge for edge in graph.edges if edge.real_c > edge.c}
        
        # 正确：应保持双向边合并判定 ↓
        # 重新生成 edge_map 和 overload_edges（与初始判定逻辑一致）
        edge_map = {(e.from_node, e.to): idx for idx, e in enumerate(graph.edges)}
        overload_edges = {}
        processed = set()
        
        for idx, edge in enumerate(graph.edges):
            if idx in processed:
                continue
                
            # 查找反向边
            reverse_key = (edge.to, edge.from_node)
            reverse_idx = edge_map.get(reverse_key, None)
            
            if reverse_idx is not None and reverse_idx != idx:
                reverse_edge = graph.edges[reverse_idx]
                processed.add(idx)
                processed.add(reverse_idx)
                # 合并双向边容量判断
                total_c = edge.c + reverse_edge.c
                total_real_c = edge.real_c + reverse_edge.real_c
                if total_real_c > total_c:
                    overload_edges[idx] = edge
                    overload_edges[reverse_idx] = reverse_edge
            else:
                # 单向边独立判断
                if edge.real_c > edge.c:
                    overload_edges[idx] = edge

        iteration += 1
        alpha *= alpha_decay

    analyze_overload_results(graph, routing_results)
    return routing_results

def analyze_overload_results(graph, routing_results):
    """分析并打印超载边及其路径"""
    def print_capacity_report():
        print("\n物理链路容量统计:")
        edge_map = {(e.from_node, e.to): idx for idx, e in enumerate(graph.edges)}
        processed = set()
        
        # 新增：按物理链路聚合数据
        physical_links = {}
        
        for idx, edge in enumerate(graph.edges):
            if idx in processed:
                continue
                
            reverse_key = (edge.to, edge.from_node)
            reverse_idx = edge_map.get(reverse_key, -1)
            
            if reverse_idx != -1 and reverse_idx != idx:  # 找到反向边
                reverse_edge = graph.edges[reverse_idx]
                processed.add(idx)
                processed.add(reverse_idx)
                
                # 计算物理链路总容量和使用量
                total_c = edge.c + reverse_edge.c
                total_real = edge.real_c + reverse_edge.real_c
                status = "超载" if total_real > total_c else "正常"
                
                # 生成唯一链路标识
                link_key = tuple(sorted([(edge.from_node, edge.to), (reverse_edge.from_node, reverse_edge.to)]))
                physical_links[link_key] = {
                    'total_c': total_c,
                    'total_real': total_real,
                    'status': status
                }
            else:
                # 处理单向边
                status = "超载" if edge.real_c > edge.c else "正常"
                link_key = ((edge.from_node, edge.to),)
                physical_links[link_key] = {
                    'total_c': edge.c,
                    'total_real': edge.real_c,
                    'status': status
                }

        # 打印聚合后的物理链路信息
        for link, data in physical_links.items():
            if len(link) == 2:  # 双向链路
                (u, v), (v_, u_) = link
                print(f"物理链路 {u}-{v}:")
                print(f"  总容量={data['total_c']}, 总使用量={data['total_real']} ({data['status']})")
            else:  # 单向链路
                (u, v), = link
                print(f"单向边 {u}->{v}:")
                print(f"  容量={data['total_c']}, 使用量={data['total_real']} ({data['status']})")

    # 原有超载分析逻辑保持不变
    overload_edges = {i: e for i, e in enumerate(graph.edges) if e.real_c > e.c}
    
    # 打印容量报告
    print_capacity_report()
    
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
        original_result['end_node'],
        capacity_constraint=True
    )
    
    # 恢复原始图数据
    graph.edges = original_edges
    return new_path or original_result['path_nodes']


def needs_optimization(path, overload_nodes):
    """判断逻辑，检查路径是否经过超限节点"""
    return any(node in overload_nodes for node in path)

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


#  ======================= Local Search =======================

def multi_stage_optimizer(graph, routing_results, capacity_levels):
    """改进后的多阶段容量约束优化器"""
    solutions = []
    original_capacities = [edge.c for edge in graph.edges]  # 保存原始容量
    
    try:
        previous_solution = copy.deepcopy(routing_results)  # 保存初始解
        
        for c in sorted(capacity_levels, reverse=True):
            print(f"\n=== [容量约束={c}] ===")
            # 继承上一阶段的优化结果
            if solutions:
                previous_solution = copy.deepcopy(solutions[-1]['solution'])
                
            # 应用当前阶段约束（不重置路径）
            current_solution = copy.deepcopy(previous_solution)
             
            # 成功
            if optimize_stage(graph, current_solution, c):
                total_length = calculate_total_cable_length(graph, current_solution)
                solutions.append({
                    'capacity': c,
                    'solution': copy.deepcopy(current_solution),
                    'total_length': total_length
                })
                print(f"Solution @ C={c} total_length={total_length}")
            # 失败
            else:
                break
        return solutions
    finally:
        # 始终恢复原始容量
        for idx, edge in enumerate(graph.edges):
            edge.c = original_capacities[idx]

def optimize_stage(graph, routing_results, c):
    """单阶段优化逻辑"""
    overload_edges = detect_overload_edges(graph, c)
    
    if not overload_edges:
        # print(f"阶段成功 @ 迭代{iteration}")
        print(f"阶段成功")
        return routing_results
        
    # TODO 按超载严重程度排序路径
    # sorted_results = sorted(
    #     routing_results,
    #     key=lambda res: calculate_path_overload(graph, res['path_nodes'], c),
    #     reverse=True
    # )
    
    # 优化所有路径
    # for result in sorted_results:
    for result in routing_results:
        # new_path = smart_reroute(
        #     graph=graph,
        #     start=result['start_node'],
        #     end=result['end_node'],
        #     load_rate=result['connection']['load_rate'],
        #     capacity_limit=c,
        #     forbidden_edges=overload_edges
        # )
        new_path = a_star_route(
            graph=graph,
            start_node=result['start_node'],
            end_node=result['end_node'],
            capacity=c
            # current_load=load_rate
        )
        
        if new_path:
            result['path_nodes'] = new_path
        else:
            print("阶段未收敛")
            return False
    return True

def detect_overload_edges(graph, c):
    """检测超载边"""
    overload_edges = set()
    edge_map = {}
    
    # 建立边映射关系
    for idx, edge in enumerate(graph.edges):
        edge_map[(edge.from_node, edge.to)] = idx
    
    # 检测双向边超载
    processed = set()
    for idx, edge in enumerate(graph.edges):
        if idx in processed:
            continue
            
        # 查找反向边
        reverse_idx = edge_map.get((edge.to, edge.from_node), -1)
        
        if reverse_idx != -1:
            # 处理双向边
            total_usage = edge.real_c + graph.edges[reverse_idx].real_c
            if total_usage > c:
                overload_edges.add(idx)
                overload_edges.add(reverse_idx)
            processed.add(reverse_idx)
        else:
            # 处理单向边
            if edge.real_c > c:
                overload_edges.add(idx)
                
        processed.add(idx)
    
    return overload_edges

def smart_reroute(graph, start, end, load_rate, capacity_limit, forbidden_edges):
    """重新路由算法"""
    # 临时图副本操作
    temp_graph = copy.deepcopy(graph)
    
    # 动态调整边权重
    for idx in forbidden_edges:
        edge = temp_graph.edges[idx]
        edge.d *= 100  # 惩罚权重
        edge.c = capacity_limit  # 应用当前阶段容量约束
        
    # 使用改进的A*算法寻路
    return a_star_route(
        graph=temp_graph,
        start_node=start,
        end_node=end,
        capacity=capacity_limit
        # current_load=load_rate
    )

def validate_new_path(graph, path, load_rate, c):
    """改进的路径验证"""
    if not path:
        return False
        
    # 预计算路径容量需求
    required_capacity = {}
    for i in range(len(path)-1):
        from_node = path[i]
        to_node = path[i+1]
        key = tuple(sorted([from_node, to_node]))
        required_capacity[key] = required_capacity.get(key, 0) + load_rate
    
    # 验证所有边容量
    for link, required in required_capacity.items():
        if required > c:
            return False
            
    return True