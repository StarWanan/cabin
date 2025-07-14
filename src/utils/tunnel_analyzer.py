import json
import math
from collections import defaultdict
from pprint import pprint

class TunnelNetworkAnalyzer:
    """
    一个用于分析和验证通道数据连通性的工具。

    它会加载Tunnels.json数据，执行以下操作：
    1. 标准化所有坐标点（四舍五入到整数）。
    2. 为每个通道创建一个包含其所有节点的统一列表。
    3. 构建一个全局的坐标->通道映射，以识别连接点。
    4. 创建一个通道连接图（邻接表）。
    5. 识别并划分所有独立的子网络（连通分量）。
    6. 提供接口来验证给定的电缆路径是否在通道网络中连通，并包含category匹配检查。
    """
    def __init__(self, tunnels_data):
        print("--- 开始初始化通道网络分析器 ---")
        if not tunnels_data:
            raise ValueError("输入的通道数据为空。")
            
        self.tunnels = {}
        self.node_id_to_tunnel_map = {}
        self.coord_to_tunnels_map = defaultdict(list)
        self.graph = defaultdict(set)
        self.components = []
        self.tunnel_to_component_id_map = {}

        self._process_tunnels(tunnels_data)
        self._build_connectivity_graph()
        self._find_connected_components()
        
        print("--- 初始化完成 ---")
        print(f"总共处理了 {len(self.tunnels)} 条通道。")
        print(f"发现了 {len(self.coord_to_tunnels_map)} 个独特的节点坐标。")
        print(f"构建了包含 {len(self.graph)} 个节点和 {sum(len(v) for v in self.graph.values()) // 2} 条边的连接图。")
        print(f"网络被划分为 {len(self.components)} 个独立的子网络（孤岛）。")

    def _normalize_coord(self, point):
        """将坐标四舍五入到最近的整数，并返回一个元组。"""
        if not all(k in point for k in ['point_x', 'point_y', 'point_z']):
            return None
        return (
            round(point['point_x']),
            round(point['point_y']),
            round(point['point_z'])
        )

    def _process_tunnels(self, tunnels_data):
        """
        处理原始通道数据：
        1. 统一每个通道的所有节点。
        2. 填充 self.tunnels, self.node_id_to_tunnel_map, 和 self.coord_to_tunnels_map。
        """
        print("步骤 1/3: 正在处理通道数据并建立坐标映射...")
        for tunnel_data in tunnels_data:
            tunnel_id = tunnel_data.get('id')
            if not tunnel_id: continue

            all_nodes_in_tunnel = []
            if tunnel_data.get('Href'): all_nodes_in_tunnel.append(tunnel_data['Href'])
            if tunnel_data.get('Tref'): all_nodes_in_tunnel.append(tunnel_data['Tref'])
            all_nodes_in_tunnel.extend(tunnel_data.get('path', []))
            all_nodes_in_tunnel.extend(tunnel_data.get('connected_to', []))

            unique_coords = set()
            for node in all_nodes_in_tunnel:
                if not node or 'id' not in node: continue
                self.node_id_to_tunnel_map[node['id']] = tunnel_id
                norm_coord = self._normalize_coord(node)
                if norm_coord: unique_coords.add(norm_coord)

            self.tunnels[tunnel_id] = {
                'id': tunnel_id,
                'category': tunnel_data.get('category'),
                'nodes': list(unique_coords)
            }
            
            for coord in unique_coords:
                self.coord_to_tunnels_map[coord].append(tunnel_id)


    def is_category_equivalent(self, cat1, cat2):
        """判断两个category是否等价（0和3互通）"""
        eq_set = {0, 3}
        if cat1 in eq_set and cat2 in eq_set:
            return True
        return cat1 == cat2

    def _build_connectivity_graph(self):
        """
        根据坐标映射构建通道之间的连接图。
        如果多个等价category的通道在同一点相交，则它们是连通的。
        """
        print("步骤 2/3: 正在构建通道连接图...")
        for coord, tunnel_ids in self.coord_to_tunnels_map.items():
            if len(tunnel_ids) > 1:
                for i in range(len(tunnel_ids)):
                    for j in range(i + 1, len(tunnel_ids)):
                        t1_id, t2_id = tunnel_ids[i], tunnel_ids[j]
                        t1_category = self.tunnels[t1_id].get('category')
                        t2_category = self.tunnels[t2_id].get('category')
                        if self.is_category_equivalent(t1_category, t2_category):
                            self.graph[t1_id].add(t2_id)
                            self.graph[t2_id].add(t1_id)


    def _find_connected_components(self):
        """
        使用广度优先搜索(BFS)或深度优先搜索(DFS)来找到图中的所有连通分量（孤岛）。
        """
        print("步骤 3/3: 正在识别独立的子网络...")
        visited = set()
        component_id = 0
        for tunnel_id in self.tunnels:
            if tunnel_id not in visited:
                component = []
                q = [tunnel_id]
                visited.add(tunnel_id)
                head = 0
                while head < len(q):
                    current_tunnel = q[head]
                    head += 1
                    component.append(current_tunnel)
                    self.tunnel_to_component_id_map[current_tunnel] = component_id
                    for neighbor in self.graph.get(current_tunnel, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            q.append(neighbor)
                self.components.append(component)
                component_id += 1

    # --- 函数已修改 ---
    def check_cable_path_connectivity(self, cable_node_ids, cable_category):
        """
        验证电缆路径：
        1. 检查电缆category是否与其经过的所有通道的category等价。
        2. 检查所有通道是否在同一个连通的通道网络中。
        """
        if not cable_node_ids:
            return {"is_connected": True, "reason": "电缆路径为空，无需检查。"}

        tunnels_on_path = sorted(list(set(
            self.node_id_to_tunnel_map.get(node_id)
            for node_id in cable_node_ids if self.node_id_to_tunnel_map.get(node_id)
        )))
        
        if not tunnels_on_path:
            return {"is_connected": True, "reason": "电缆路径未经过任何已知通道，默认连通。"}

        # --- Category等价检查 ---
        mismatched_tunnels = []
        for tunnel_id in tunnels_on_path:
            tunnel_info = self.tunnels.get(tunnel_id)
            if not tunnel_info: continue
            
            tunnel_category = tunnel_info.get('category')
            if not self.is_category_equivalent(tunnel_category, cable_category):
                mismatched_tunnels.append({
                    'tunnel_id': tunnel_id,
                    'tunnel_category': tunnel_category
                })
        
        if mismatched_tunnels:
            return {
                "is_connected": False,
                "reason": "Category不匹配",
                "details": {
                    "cable_category": cable_category,
                    "mismatched_tunnels": mismatched_tunnels
                }
            }
        
        # --- 原有步骤：网络连通性检查 ---
        if len(tunnels_on_path) <= 1:
            return {
                "is_connected": True, 
                "reason": "路径仅经过一条通道且Category匹配，默认连通。",
                "tunnels_on_path": tunnels_on_path
            }

        first_tunnel_id = tunnels_on_path[0]
        target_component_id = self.tunnel_to_component_id_map.get(first_tunnel_id)

        disconnected_pairs = []
        for i in range(1, len(tunnels_on_path)):
            current_tunnel_id = tunnels_on_path[i]
            current_component_id = self.tunnel_to_component_id_map.get(current_tunnel_id)
            if current_component_id != target_component_id:
                disconnected_pairs.append({
                    'from_tunnel': first_tunnel_id,
                    'from_component': target_component_id,
                    'to_tunnel': current_tunnel_id,
                    'to_component': current_component_id
                })

        if disconnected_pairs:
             return {
                "is_connected": False,
                "reason": "网络中断",
                "details": {
                    "tunnels_on_path": tunnels_on_path,
                    "disconnected_pairs": disconnected_pairs,
                    "component_map": {t: self.tunnel_to_component_id_map.get(t, '孤立') for t in tunnels_on_path}
                }
            }

        return {
            "is_connected": True,
            "reason": f"路径上所有 {len(tunnels_on_path)} 条通道Category匹配且均属于同一个子网络 (ID: {target_component_id})。",
            "tunnels_on_path": tunnels_on_path,
            "component_id": target_component_id
        }


# --- 主程序入口 ---
if __name__ == "__main__":
    # --- 1. 加载数据 ---
    try:
        # 使用您提供的路径
        with open('../ExportDtas/Tunnels.json', 'r', encoding='utf-8') as f:
            tunnels_data = json.load(f)
        with open('../ExportDtas/Cables.json', 'r', encoding='utf-8') as f:
            cables_data = json.load(f)
    except FileNotFoundError as e:
        print(f"错误: 找不到文件 {e.filename}。请确保JSON文件路径正确。")
        exit()
    except json.JSONDecodeError as e:
        print(f"错误: JSON文件格式错误 - {e}")
        exit()

    # --- 2. 初始化分析器并构建网络 ---
    analyzer = TunnelNetworkAnalyzer(tunnels_data)
    
    # --- 3. 批量检查所有电缆 ---
    print("\n--- 开始批量检查所有电缆的路径连通性 ---")
    
    if cables_data:
        failure_count = 0
        f1_count = 0
        total_cables = len(cables_data)

        for i, cable_data in enumerate(cables_data):
            cable_id = cable_data.get('cable_id')
            cable_category = cable_data.get('cable_category')
            cable_node_ids = [p.get('id') for p in cable_data.get('cWBranPoints', [])]
            
            # 如果电缆没有定义category，我们无法检查，可以选择跳过或标记为错误
            if cable_category is None:
                print(f"警告: 电缆 '{cable_id}' 没有 'cable_category' 字段，跳过检查。")
                continue

            # --- 调用已更新的检查函数 ---
            connectivity_result = analyzer.check_cable_path_connectivity(cable_node_ids, cable_category)
            
            if not connectivity_result['is_connected']:
                failure_count += 1
                print(f"\n❌ 第 {i+1}/{total_cables} 条电缆 '{cable_id}' 的路径验证失败！")
                # print(f"   失败原因: {connectivity_result['reason']}")
                if (connectivity_result['reason'] == 'Category不匹配'):
                    f1_count += 1
                # print("   详细信息:")
                pprint(connectivity_result['details'], indent=4)
        
        print("\n--- 检查完毕 ---")
        if failure_count == 0:
            print(f"✅ 所有 {total_cables} 条电缆的路径均验证通过！")
        else:
            print(f"总计: {total_cables} 条电缆中，有 {failure_count} 条路径不连通或不合规。其中有{f1_count}条是因为Category不匹配")
    else:
        print("Cables.json为空或加载失败，无法进行电缆路径Debug。")