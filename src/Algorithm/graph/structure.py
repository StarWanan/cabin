import math

class Edge:
    def __init__(self, from_node, to, c, d, next_edge):
        self.from_node = from_node  # 起始节点编号
        self.to = to                # 目标节点编号
        self.c = c                  # 边容量
        self.d = d                  # 边距离
        self.real_c = 0             # 边目前实际容量
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
        u_coord = self.nodes[u]
        v_coord = self.nodes[v]
        distance = math.sqrt(
            (u_coord[0]-v_coord[0])**2 + 
            (u_coord[1]-v_coord[1])**2 + 
            (u_coord[2]-v_coord[2])**2
        )
        self.edges.append(Edge(u, v, c, distance, self.head[u]))
        self.head[u] = len(self.edges) - 1

    def add_bidirectional_edge(self, u, v, c):
        """添加无向边（双向边）"""
        self.add_directed_edge(u, v, c)
        self.add_directed_edge(v, u, c)

    def find_nearest_node(self, x, y, z):
        """根据坐标找最近节点（用于设备定位），只考虑z坐标相同的节点"""
        min_dist = float('inf')
        nearest = -1
        for node_id in range(1, len(self.nodes)):
            nx, ny, nz = self.nodes[node_id]
            if nz == z:  # 只考虑z坐标相同的节点
                dist = math.sqrt(
                    (nx - x) ** 2 +
                    (ny - y) ** 2
                )
                if dist < min_dist:
                    min_dist = dist
                    nearest = node_id
        return nearest