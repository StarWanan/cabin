import heapq
import math

def a_star_route(graph, start_node, end_node, capacity=-1):
    # 启发函数：欧氏距离
    def heuristic(a):
        a_coord = graph.nodes[a]
        b_coord = graph.nodes[end_node]
        return math.sqrt(
            (a_coord[0]-b_coord[0])**2 + 
            (a_coord[1]-b_coord[1])**2 + 
            (a_coord[2]-b_coord[2])**2
        )
    
    open_heap = []
    heapq.heappush(open_heap, (0, 0, start_node, -1))
    
    came_from = {}  # 记录父节点
    g_values = {start_node: 0}
    
    while open_heap:
        current_f, current_g, current_node, parent = heapq.heappop(open_heap)
        
        if current_node in came_from:
            continue
        
        came_from[current_node] = parent
        
        if current_node == end_node:
            # 回溯路径
            path = []
            while current_node != -1:
                path.append(current_node)
                current_node = came_from.get(current_node, -1)
            return path[::-1]  # 反转得到正序路径
        
        edge_idx = graph.head[current_node]
        while edge_idx != -1:
            edge = graph.edges[edge_idx]
            
            # 添加容量约束检查
            if capacity > 0:
                # 查找反向边
                reverse_edge = next(
                    (e for e in graph.edges 
                     if e.from_node == edge.to and e.to == edge.from_node),
                    None
                )
                # 计算双向总使用量
                total_usage = edge.real_c + (reverse_edge.real_c if reverse_edge else 0)
                remaining_capacity = capacity - total_usage
                
                if remaining_capacity <= 0:
                    edge_idx = edge.next
                    continue  # 跳过已满载的边
            
            neighbor = edge.to
            new_g = current_g + edge.d
            
            if neighbor not in g_values or new_g < g_values.get(neighbor, float('inf')):
                g_values[neighbor] = new_g
                h = heuristic(neighbor)
                f = new_g + h
                heapq.heappush(open_heap, (f, new_g, neighbor, current_node))
            
            edge_idx = edge.next
    
    return None  # 无可行路径

