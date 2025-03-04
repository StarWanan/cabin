import math
from .structure import Graph

def build_graph(nodes, connections, line_capacity):  # 添加 line_capacity 参数
    """根据nodes和connections建立图"""
    node_list = [(0, 0, 0)] + [nodes[key] for key in sorted(nodes.keys())]
    graph = Graph(node_list)
    node_index_map = {key: idx + 1 for idx, key in enumerate(sorted(nodes.keys()))}

    for u, v in connections:
        # 使用参数传入的 line_capacity 代替硬编码常量
        graph.add_bidirectional_edge(node_index_map[u], node_index_map[v], line_capacity)
    
    return graph