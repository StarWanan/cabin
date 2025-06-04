import heapq
import math


def a_star_route(graph, start_node, end_node, capacity=-1, cable_category=-1, cable_radius=0, check_bend_radius=True):
    def heuristic(a):
        a_coord = graph.nodes[a]
        b_coord = graph.nodes[end_node]
        return math.sqrt(
            (a_coord[0] - b_coord[0]) ** 2 +
            (a_coord[1] - b_coord[1]) ** 2 +
            (a_coord[2] - b_coord[2]) ** 2
        )

    open_heap = []
    heapq.heappush(open_heap, (0, 0, start_node, -1))

    came_from = {}
    g_values = {start_node: 0}

    while open_heap:
        current_f, current_g, current_node, parent = heapq.heappop(open_heap)

        if current_node in came_from:
            continue

        came_from[current_node] = parent

        if current_node == end_node:
            path = []
            while current_node != -1:
                path.append(current_node)
                current_node = came_from.get(current_node, -1)
            return path[::-1]

        edge_idx = graph.head[current_node]
        no_valid_edges = True  # 用于判断是否有有效边

        while edge_idx != -1:
            edge = graph.edges[edge_idx]
            reason = None  # 用于记录跳过的原因

            if cable_category != -1 and edge.category != cable_category:
                reason = f"类型不匹配：边类型{edge.category}，要求类型{cable_category}"
                edge_idx = edge.next
                continue

            if capacity > 0:
                reverse_edge = next(
                    (e for e in graph.edges
                     if e.from_node == edge.to and e.to == edge.from_node),
                    None
                )
                total_usage = edge.real_c + (reverse_edge.real_c if reverse_edge else 0)
                remaining_capacity = capacity - total_usage

                if remaining_capacity <= 0:
                    reason = f"总容量={capacity}, 已使用={total_usage}, 剩余={remaining_capacity}"
                    edge_idx = edge.next
                    continue

            if check_bend_radius:
                from_node_r = graph.node_metadata[edge.from_node]["pointr_radius"]
                to_node_r = graph.node_metadata[edge.to]["pointr_radius"]

                if (from_node_r != 0 and cable_radius > from_node_r) or (to_node_r != 0 and cable_radius > to_node_r):
                    reason = f"弯曲半径不满足要求：from_node_r={from_node_r}, to_node_r={to_node_r}, cable_radius={cable_radius}"
                    edge_idx = edge.next
                    continue

            no_valid_edges = False  # 找到有效边
            neighbor = edge.to
            new_g = current_g + edge.d

            if neighbor not in g_values or new_g < g_values.get(neighbor, float('inf')):
                g_values[neighbor] = new_g
                h = heuristic(neighbor)
                f = new_g + h
                heapq.heappush(open_heap, (f, new_g, neighbor, current_node))

            edge_idx = edge.next

        if no_valid_edges:
            print(f"[A* Route] 节点 {current_node} 无法继续扩展，原因：{reason}")

    return None