import os
import json

def save_data_to_file(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def is_point_on_segment(start, end, point):
    """判断点是否在线段上"""
    # 计算方向向量
    segment_vector = (end[0] - start[0], end[1] - start[1], end[2] - start[2])
    point_vector = (point[0] - start[0], point[1] - start[1], point[2] - start[2])

    # 计算向量的点积
    dot_product = (segment_vector[0] * point_vector[0] +
                   segment_vector[1] * point_vector[1] +
                   segment_vector[2] * point_vector[2])

    # 计算向量的长度
    segment_length_squared = (segment_vector[0] ** 2 +
                              segment_vector[1] ** 2 +
                              segment_vector[2] ** 2)
    point_length_squared = (point_vector[0] ** 2 +
                            point_vector[1] ** 2 +
                            point_vector[2] ** 2)

    # print(f"Start: {start}, End: {end}, Point: {point}")
    # print(f"Dot Product: {dot_product}, Segment Length Squared: {segment_length_squared}, Point Length Squared: {point_length_squared}")

    # 判断点是否在线段上
    return dot_product >= 0 and point_length_squared <= segment_length_squared

def insert_connected_points(path, connected_to):
    """插入 connected_to 的点到 path 中"""
    for connected_point in connected_to:
        connected_coordinates = (
            connected_point["point_x"],
            connected_point["point_y"],
            connected_point["point_z"]
        )

        # 找到插入位置
        for j in range(len(path) - 1):
            start_coordinates = (
                path[j]["point_x"],
                path[j]["point_y"],
                path[j]["point_z"]
            )
            end_coordinates = (
                path[j + 1]["point_x"],
                path[j + 1]["point_y"],
                path[j + 1]["point_z"]
            )

            if is_point_on_segment(start_coordinates, end_coordinates, connected_coordinates):
                # 插入 connected_point 到 path 中
                # print("insert node: ", connected_coordinates)
                path.insert(j + 1, {
                    "point_x": connected_point["point_x"],
                    "point_y": connected_point["point_y"],
                    "point_z": connected_point["point_z"]
                })
                break

    return path

def real_data_api(directory_path="data/ExportDtas", reRead=False):
    # 处理后的文件路径
    nodes_file = os.path.join(directory_path, "nodes.json")
    nodes_connections_file = os.path.join(directory_path, "nodes_connections.json")
    devices_file = os.path.join(directory_path, "devices.json")
    device_connections_file = os.path.join(directory_path, "device_connections.json")
    # device_no_path_connections_file = os.path.join(directory_path, "no_path_connections.json")
    node_metadata_file = os.path.join(directory_path, "node_metadata.json")

    # 检查是否需要重新读取数据
    if not reRead:
        print("load_data_from_file")
        nodes = load_data_from_file(nodes_file)
        connections = load_data_from_file(nodes_connections_file)
        devices = load_data_from_file(devices_file)
        # device_connections = load_data_from_file(device_connections_file)
        device_connections = load_data_from_file(device_connections_file)
        # device_connections = load_data_from_file(device_no_path_connections_file)
        node_metadata = load_data_from_file(node_metadata_file)
        return nodes, connections, devices, device_connections, node_metadata

    # 文件路径
    tunnels_file = os.path.join(directory_path, "Tunnels.json")
    equis_file = os.path.join(directory_path, "Equis.json")
    connections_file = os.path.join(directory_path, "Connections.json")
    cables_file = os.path.join(directory_path, "Cables.json")

    # 读取 JSON 数据
    with open(tunnels_file, "r", encoding="utf-8") as f:
        tunnels_data = json.load(f)
    with open(equis_file, "r", encoding="utf-8") as f:
        equis_data = json.load(f)
    with open(connections_file, "r", encoding="utf-8") as f:
        connections_data = json.load(f)
    with open(cables_file, "r", encoding="utf-8") as f:
        cables_data = json.load(f)

    # 1. 获取 nodes 和 connections（增加tunnel类型记录）
    nodes = {}  # 仅存储坐标：{node_id: (x, y, z)}
    node_metadata = {}  # 新增：存储元数据 {node_id: {"type": ..., "pointr_radius": ...}}
    connections = []  # 格式：(from_node, to_node, tunnel_category)

    def find_node_id_by_coordinates(coordinates):
        """根据坐标查找节点 ID，如果不存在则返回 None"""
        for node_id, node_coords in nodes.items():
            if node_coords == coordinates:
                return node_id
        return None
    
    def find_cwb_point_id_by_coordinates(coordinates):
        """根据坐标查找 CWBranPoint ID，如果不存在则返回 None"""
        for point_id, point_coords in cwbranpoint_map.items():
            if point_coords["point_x"] == coordinates[0] and \
               point_coords["point_y"] == coordinates[1] and \
               point_coords["point_z"] == coordinates[2]:
                return point_id
        return None

    # 新增：读取 CWBranPoint 数据
    cwbranpoint_file = os.path.join(directory_path, "CWBranPoint.json")
    with open(cwbranpoint_file, "r", encoding="utf-8") as f:
        cwbranpoint_data = json.load(f)
    cwbranpoint_map = {item["id"]: item for item in cwbranpoint_data}  # 按 id 映射

    for tunnel in tunnels_data:
        path = tunnel["path"]
        connected_to = tunnel.get("connected_to", [])
        tunnel_category = tunnel["category"]
        path = insert_connected_points(path, connected_to)

        # 处理 path 中的点并建立连接
        for i, point in enumerate(path):
            coordinates = (round(point["point_x"]), round(point["point_y"]), round(point["point_z"]))
            node_id = find_node_id_by_coordinates(coordinates)
            cwb_coordinates = (point["point_x"], point["point_y"], point["point_z"])
            cwb_point_id = find_cwb_point_id_by_coordinates(cwb_coordinates)
            if not node_id:  # 如果节点不存在则创建
                node_id = f"P{len(nodes) + 1}"
                # 从 CWBranPoint 获取类型和弯曲半径
                cw_info = cwbranpoint_map.get(cwb_point_id, {"type": -1, "pointr_radius": 0})
                nodes[node_id] = coordinates  # 仅存储坐标
                node_metadata[node_id] = {  # 元数据存入新字典
                    "type": cw_info["type"],
                    "pointr_radius": cw_info["pointr_radius"]
                }
            else:
                # 已有节点，补充元数据（如果未存在）
                if node_id not in node_metadata:
                    cw_info = cwbranpoint_map.get(node_id, {"type": -1, "pointr_radius": 0})
                    node_metadata[node_id] = {
                        "type": cw_info["type"],
                        "pointr_radius": cw_info["pointr_radius"]
                    }

            if i > 0:  # 建立连接
                prev_coordinates = (round(path[i - 1]["point_x"]), round(path[i - 1]["point_y"]), round(path[i - 1]["point_z"]))
                prev_node_id = find_node_id_by_coordinates(prev_coordinates)
                if prev_node_id:
                    # 记录连接时保存隧道类型
                    connection = (prev_node_id, node_id, tunnel_category)
                    if connection[:2] not in [c[:2] for c in connections]:  # 避免重复连接（不检查类型）
                        connections.append(connection)
    # 2. 获取 devices
    devices = {}
    for equip in equis_data:
        device_id = equip["id"]
        devices[device_id] = (round(equip["point_x"]), round(equip["point_y"]), round(equip["point_z"]))
    
    # 3. 获取 device_connections（增加电缆类型记录）
    # 改为存储完整电缆信息（包含类型）
    cable_info_map = {
        cable["cable_id"]: {
            "radius": cable["cable_radius"],  # 对应Cables.json中的cable_radius字段
            "bendR": cable["cable_bendR"],
            "category": cable["cable_category"]  # 对应Cables.json中的cable_category字段（数字类型）
        } for cable in cables_data
    }
    device_connections = []
    for conn in connections_data:
        device1, device2 = conn["connection"]
        cable_id = conn["cable_id"]
        # 调整默认值类型与原始数据一致（Cables.json中cable_category为数字，默认值改为0）
        cable_info = cable_info_map.get(cable_id, {"radius": 0, "bendR": 0, "category": 0})  # 关键修正：默认值类型匹配
        device_connections.append({
            "device1": device1,
            "device2": device2,
            "load_rate": cable_info["radius"],  # 使用cable_radius作为负载率
            "bendR": cable_info["bendR"],
            "cable_category": cable_info["category"]  # 使用cable_category作为电缆类型（数字）
        })

    # 保存时需要包含类型信息
    save_data_to_file(nodes, nodes_file)
    save_data_to_file(connections, nodes_connections_file)  # 现在connections包含类型
    save_data_to_file(devices, devices_file)
    save_data_to_file(device_connections, device_connections_file)  # 现在包含cable_category
    save_data_to_file(node_metadata, node_metadata_file)  # 新增保存元数据

    return nodes, connections, devices, device_connections, node_metadata

if __name__ == "__main__":
    directory = "../../data/ExportDtas"
    nodes, connections, devices, device_connections = real_data_api(directory)
    # print("Nodes:", nodes)
    # print("Connections:", connections)
    # print("Devices:", devices)
    # print("Device Connections:", device_connections)