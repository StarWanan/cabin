import heapq
import math
from cabin.src.data.layer1 import nodes as nodes1, connections as connections1
from cabin.src.data.layer2 import nodes as nodes2, connections as connections2
from cabin.src.data.layer3 import nodes as nodes3, connections as connections3
from cabin.src.data.layer4 import nodes as nodes4, connections as connections4
from cabin.src.data.hub import nodes as nodes_hub, connections as connections_hub
from cabin.src.data.device import device
from cabin.src.vis.vis import remove_duplicate_nodes

LINE_CAPACITY = 100


class Edge:
    def __init__(self, to, c, d, next_edge):
        self.to = to        # 目标节点编号
        self.c = c          # 边容量
        self.d = d          # 边距离（新增属性）
        self.next = next_edge

class Graph:
    def __init__(self, nodes):
        """
        :param nodes: 节点坐标列表，索引即节点ID（从1开始）
        """
        self.nodes = nodes  # 节点0位置空置
        self.head = [-1] * len(nodes)  # 头指针数组
        self.edges = []

    def add_directed_edge(self, u, v, c):
        """添加有向边并自动计算距离"""
        # 计算三维欧氏距离
        u_coord = self.nodes[u]
        v_coord = self.nodes[v]
        distance = math.sqrt(
            (u_coord[0]-v_coord[0])**2 + 
            (u_coord[1]-v_coord[1])**2 + 
            (u_coord[2]-v_coord[2])**2
        )
        self.edges.append(Edge(v, c, distance, self.head[u]))
        self.head[u] = len(self.edges) - 1

    def add_bidirectional_edge(self, u, v, c):
        """添加无向边（双向边）"""
        self.add_directed_edge(u, v, c)
        self.add_directed_edge(v, u, c)

    def find_nearest_node(self, x, y, z):
        """根据坐标找最近节点（用于设备定位）"""
        min_dist = float('inf')
        nearest = -1
        for node_id in range(1, len(self.nodes)):
            nx, ny, nz = self.nodes[node_id]
            dist = math.sqrt(
                (nx-x)**2 + 
                (ny-y)**2 + 
                (nz-z)**2
            )
            if dist < min_dist:
                min_dist = dist
                nearest = node_id
        return nearest



def a_star_route(graph, start_node, end_node):
    """A*算法实现路径规划"""
    # 启发函数：欧氏距离估计
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
            neighbor = edge.to
            new_g = current_g + edge.d
            
            if neighbor not in g_values or new_g < g_values.get(neighbor, float('inf')):
                g_values[neighbor] = new_g
                h = heuristic(neighbor)
                f = new_g + h
                heapq.heappush(open_heap, (f, new_g, neighbor, current_node))
            
            edge_idx = edge.next
    
    return None  # 无可行路径


def build_graph(nodes, connections):
    """根据nodes和connections建立图"""
    node_list = [(0, 0, 0)] + [nodes[key] for key in sorted(nodes.keys())]
    graph = Graph(node_list)
    node_index_map = {key: idx + 1 for idx, key in enumerate(sorted(nodes.keys()))}

    # 容量
    for u, v in connections:
        graph.add_bidirectional_edge(node_index_map[u], node_index_map[v], LINE_CAPACITY)

    # print("Nodes:")
    # for idx, coord in enumerate(node_list):
    #     print(f"Node {idx}: {coord}")
    #
    # print("\nEdges:")
    # for edge in graph.edges:
    #     print(f"Edge from {edge.to} with distance {edge.d}")

    return graph


if __name__ == "__main__":
    nodes = {**nodes1, **nodes2, **nodes3, **nodes4, **nodes_hub}
    connections = connections1 + connections2 + connections3 + connections4 + connections_hub

    nodes, connections = remove_duplicate_nodes(nodes, connections)

    graph = build_graph(nodes, connections)

    device_3_1 = device["device_3_1"]
    device_4_3 = device["device_4_3"]

    print("Device 3_1:", device_3_1)
    print("Device 4_3:", device_4_3)

    s_node = graph.find_nearest_node(*device_3_1)
    t_node = graph.find_nearest_node(*device_4_3)

    print(f"Device 3_1 is located at node {s_node} with position {device_3_1}")
    print(f"Device 4_3 is located at node {t_node} with position {device_4_3}")

    path = a_star_route(graph, s_node, t_node)

    print(f"Route from {device_3_1} to {device_4_3}:")
    print(" -> ".join(f"Node {n}" for n in path) if path else "No path found")



