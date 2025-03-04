def get_coordinates(graph, node_list):
    coordinates = []
    for node in node_list:
        if 1 <= node < len(graph.nodes):
            coordinates.append(graph.nodes[node])
        else:
            coordinates.append(None)  # 如果节点编号无效，返回None
    return coordinates

def update_edge_real_capacity(graph, path, load_rate):
    """更新路径上所有边的实际容量"""
    for i in range(len(path) - 1):
        current_node = path[i]
        next_node = path[i + 1]
        edge_idx = graph.head[current_node]
        while edge_idx != -1:
            edge = graph.edges[edge_idx]
            if edge.to == next_node:
                edge.real_c += load_rate
                break
            edge_idx = edge.next
