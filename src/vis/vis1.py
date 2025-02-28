import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 定义节点坐标
# 每个节点的格式为：节点名称: (x, y, z)
# z 表示甲板层数，0 为底层甲板，1 为上层甲板
nodes = {
    "A1": (0, 0, 0),
    "A2": (5, 0, 0),
    "A3": (10, 0, 0),
    "A4": (15, 5, 1),
    "A5": (5, -5, 0),
    "A6": (10, -5, 0),
    "A7": (15, -5, 1),
    "B2": (20, 10, 1),
    "B3": (25, 0, 1),
}

# 定义线缆连接关系
# 每个连接的格式为：(起点, 终点)
connections = [
    ("A1", "A2"),
    ("A2", "A3"),
    ("A3", "A4"),
    ("A2", "A5"),
    ("A5", "A6"),
    ("A6", "A7"),
    ("A4", "B2"),
    ("A4", "B3"),
]

# 创建 3D 图形
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# 绘制节点
for node, (x, y, z) in nodes.items():
    ax.scatter(x, y, z, c='r', marker='o')  # 绘制节点
    ax.text(x, y, z, node, color='blue')  # 标注节点名称

# 绘制线缆
for start, end in connections:
    x_coords = [nodes[start][0], nodes[end][0]]
    y_coords = [nodes[start][1], nodes[end][1]]
    z_coords = [nodes[start][2], nodes[end][2]]
    ax.plot(x_coords, y_coords, z_coords, c='purple')  # 绘制线缆

# 设置坐标轴标签
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')

# 显示图形
plt.show()
