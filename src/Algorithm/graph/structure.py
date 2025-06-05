import math

class Edge:
    def __init__(self, from_node, to, c, d, next_edge, category):  # 新增category参数
        self.from_node = from_node
        self.to = to
        self.c = c
        self.d = d
        self.real_c = 0
        self.next = next_edge
        self.category = category  # 记录该边所属的隧道类型

class Graph:
    def __init__(self, nodes, node_metadata=None):
        """
        :param nodes: 节点坐标列表，索引即节点ID（从1开始）
        """
        self.nodes = nodes  # 节点0位置空置
        self.node_metadata = node_metadata if node_metadata is not None else {}   # 节点元数据字典
        self.head = [-1] * len(nodes)  # 头指针数组
        self.edges = []

    def add_directed_edge(self, u, v, c, category):  # 新增category参数
        u_coord = self.nodes[u]
        v_coord = self.nodes[v]
        distance = math.sqrt(
            (u_coord[0]-v_coord[0])**2 + 
            (u_coord[1]-v_coord[1])**2 + 
            (u_coord[2]-v_coord[2])**2
        )
        self.edges.append(Edge(u, v, c, distance, self.head[u], category))  # 传递类型
        self.head[u] = len(self.edges) - 1

    def add_bidirectional_edge(self, u, v, c, category):  # 新增category参数
        self.add_directed_edge(u, v, c, category)  # 双向边使用相同类型
        self.add_directed_edge(v, u, c, category)

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

    def find_nearest_node_any_z(self, x, y, z):
        """根据坐标找最近节点（不限制z坐标），计算三维空间距离"""
        min_dist = float('inf')
        nearest = -1
        for node_id in range(1, len(self.nodes)):
            nx, ny, nz = self.nodes[node_id]
            # 计算三维欧氏距离（包含z坐标差异）
            dist = math.sqrt(
                (nx - x) ** 2 +
                (ny - y) ** 2 +
                (nz - z) ** 2  # 新增z坐标差异计算
            )
            if dist < min_dist:
                min_dist = dist
                nearest = node_id
        return nearest
    def find_nearest_node_by_layer(self, x, y, z):
        # 定义每一层的z坐标范围
        layers = [
            (0, 1000),  # 第一层
            (1000, 2900),  # 第二层
            (2900, 4800),  # 第三层
            (4800, 7500),  # 第四层
            (7500, 10200),  # 第五层
            (10200, 12700),  # 第六层
            (12700, 15200),  # 第七层
            (15200, 17800),  # 第八层
            (17800, 30000)  # 第九层
        ]

        # 找到z所在的层
        layer_index = -1
        for i, (lower, upper) in enumerate(layers):
            if lower <= z < upper:
                layer_index = i
                break

        if layer_index == -1:
            return -1, None  # 如果z不在任何层中，返回(-1, None)

        min_dist = float('inf')
        nearest = -1
        for node_id in range(1, len(self.nodes)):
            nx, ny, nz = self.nodes[node_id]
            # 检查节点是否在同一层
            if layers[layer_index][0] <= nz < layers[layer_index][1]:
                dist = math.sqrt((nx - x) ** 2 + (ny - y) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    nearest = node_id

        return nearest, self.nodes[nearest] if nearest != -1 else None

    def find_nearest_node_by_layer_and_ptype(self, x, y, z):
        # 定义每一层的z坐标范围
        layers = [
            (0, 1000),  # 第一层
            (1000, 2900),  # 第二层
            (2900, 4800),  # 第三层
            (4800, 7500),  # 第四层
            (7500, 10200),  # 第五层
            (10200, 12700),  # 第六层
            (12700, 15200),  # 第七层
            (15200, 17800),  # 第八层
            (17800, 30000)  # 第九层
        ]

        # 找到z所在的层
        layer_index = -1
        for i, (lower, upper) in enumerate(layers):
            if lower <= z < upper:
                layer_index = i
                break

        if layer_index == -1:
            print(f"[A* Route] 节点 ({x}, {y}, {z}) 找不到同层接入点，原因：z不在任何层中")
            return -1, None  # 如果z不在任何层中，返回(-1, None)

        min_dist = float('inf')
        nearest = -1
        reason = None  # 用于记录原因
        for node_id in range(1, len(self.nodes)):
            nx, ny, nz = self.nodes[node_id]
            # 检查节点是否在同一层且接入类型合法
            if layers[layer_index][0] <= nz < layers[layer_index][1]:
                if self.node_metadata[node_id]["type"] in {0,1,3,4}:
                    dist = math.sqrt((nx - x) ** 2 + (ny - y) ** 2)
                    if dist < min_dist:
                        min_dist = dist
                        nearest = node_id
                else:
                    reason = f"节点类型不符合「0,1,3,4」: {self.node_metadata[node_id]['type']}"

        if nearest == -1:
            print(f"[A* Route] 节点 ({x}, {y}, {z}) 找不到同层接入点，原因：{reason}")

        return nearest, self.nodes[nearest] if nearest != -1 else None

    def find_nearest_node_by_layer_ptype_and_cable_category(self, x, y, z, cable_category):
        # 定义每一层的z坐标范围
        layers = [
            (0, 1000),  # 第一层
            (1000, 2900),  # 第二层
            (2900, 4800),  # 第三层
            (4800, 7500),  # 第四层
            (7500, 10200),  # 第五层
            (10200, 12700),  # 第六层
            (12700, 15200),  # 第七层
            (15200, 17800),  # 第八层
            (17800, 30000)  # 第九层
        ]

        # 找到z所在的层
        layer_index = -1
        for i, (lower, upper) in enumerate(layers):
            if lower <= z < upper:
                layer_index = i
                break

        if layer_index == -1:
            print(f"[A* Route] 节点 ({x}, {y}, {z}) 找不到同层接入点，原因：z不在任何层中")
            return -1, None  # 如果z不在任何层中，返回(-1, None)

        min_dist = float('inf')
        nearest = -1
        reason = None  # 用于记录原因
        for node_id in range(1, len(self.nodes)):
            nx, ny, nz = self.nodes[node_id]
            # 检查节点是否在同一层且接入类型合法
            if layers[layer_index][0] <= nz < layers[layer_index][1]:
                if self.node_metadata[node_id]["type"] in {0,1,3,4}:
                    if self.node_metadata[node_id]["tunnel_category"] == cable_category:
                        dist = math.sqrt((nx - x) ** 2 + (ny - y) ** 2)
                        if dist < min_dist:
                            min_dist = dist
                            nearest = node_id
                    else:
                        reason = f"节点tunnel_category != cable_category: {self.node_metadata[node_id]['tunnel_category']}"
                else:
                    reason = f"节点类型不符合「0,1,3,4」: {self.node_metadata[node_id]['type']}"

        if nearest == -1:
            print(f"[A* Route] 节点 ({x}, {y}, {z}) 找不到同层接入点，原因：{reason}")

        return nearest, self.nodes[nearest] if nearest != -1 else None