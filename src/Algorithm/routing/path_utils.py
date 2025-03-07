def get_coordinates(graph, node_list):
    """根据path的节点编号返回坐标"""
    coordinates = []
    for node in node_list:
        if 1 <= node < len(graph.nodes):
            coordinates.append(graph.nodes[node])
        else:
            coordinates.append(None)  # 如果节点编号无效，返回None
    return coordinates

def get_edge_nodes(graph, edge_index):
    """
    根据边的编号返回这条边连接的两个节点
    """
    if 0 <= edge_index < len(graph.edges):
        edge = graph.edges[edge_index]
        return graph.nodes[edge.from_node], graph.nodes[edge.to]
    return None

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
