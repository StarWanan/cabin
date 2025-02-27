class Path:
    def __init__(self, path_type):
        self.type = path_type  # "main" 或 "branch"
        self.key_points = []  # 路径转折点列表
        self.segments = []  # 分解后的线段集合

    def add_point(self, x, y):
        """添加路径关键点"""
        self.key_points.append((x, y))
        self._update_segments()

    def _update_segments(self):
        """私有函数：自动更新线段分解"""
        self.segments = []
        for i in range(1, len(self.key_points)):
            prev = self.key_points[i - 1]
            curr = self.key_points[i]

            # 判断线段方向
            if prev == curr:  # 垂直
                direction = "vertical"
            else:  # 水平
                direction = "horizontal"

            self.segments.append({
                "start": prev,
                "end": curr,
                "direction": direction,
                "break_rate": 0
            })


# 测试
main = Path("main")
main.add_point(2, 4)    # 起点
main.add_point(40, 4)   # 水平
main.add_point(40, 28)  # 垂直

print("主线:", main.segments)


