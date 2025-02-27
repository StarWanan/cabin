class UndirectedGraph:
    def __init__(self):
        self.adjacency_list = {}
        # 邻接表结构示例：
        # {
        #   (x1,y1): [((xn,yn), 'horizontal', 0), ...],
        #   (x2,y2): [((xm,ym), 'vertical', 0), ...]
        # }

    def add_edge(self, point_a, point_b):
        """添加边并自动判断方向"""
        if not self._is_valid_edge(point_a, point_b):
            raise ValueError("边必须是水平或垂直的")

        direction = 'horizontal' if point_a[1] == point_b[1] else 'vertical'

        # 双向添加边信息
        self._add_to_adjacency(point_a, point_b, direction)
        self._add_to_adjacency(point_b, point_a, direction)

    def _is_valid_edge(self, a, b):
        """验证边是否符合水平/垂直要求"""
        return (a[0] == b[0] and a[1] != b[1]) or (a[1] == b[1] and a[0] != b[0])

    def _add_to_adjacency(self, src, dest, direction):
        """更新邻接表"""
        if src not in self.adjacency_list:
            self.adjacency_list[src] = []
        # 避免重复添加
        if not any(dest == entry[0] for entry in self.adjacency_list[src]):
            self.adjacency_list[src].append((dest, direction, 0))

    def get_neighbors(self, node):
        """获取节点的所有邻居及边信息"""
        return self.adjacency_list.get(node, [])

    def get_all_edges(self):
        """获取所有不重复的边（辅助函数）"""
        edges = set()
        for node, neighbors in self.adjacency_list.items():
            for neighbor in neighbors:
                # 使用排序后的元组避免重复
                edge = tuple(sorted([node, neighbor[0]]))
                edges.add((edge, neighbor[1], neighbor[2]))
        return list(edges)


g = UndirectedGraph()

g.add_edge((2, 4), (40, 4))
g.add_edge((40, 4), (40, 28))
g.add_edge((40, 28), (40, 40))

# 获取节点邻居
print("节点 (40,4) 的邻居：")
for neighbor in g.get_neighbors((40, 4)):
    print(f"坐标: {neighbor[0]}, 方向: {neighbor[1]}, 爆仓率: {neighbor[2]}")
# 输出所有边
print("\n所有边：")
for edge in g.get_all_edges():
    print(f"端点: {edge[0]}, 方向: {edge[1]}, 爆仓率: {edge[2]}")