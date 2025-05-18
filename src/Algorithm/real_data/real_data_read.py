import os
import json
import time

def save_data_to_file(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def real_data_api(directory_path="data/ExportDtas", reRead=False):
    # 文件路径
    nodes_file = os.path.join(directory_path, "nodes.json")
    connections_file = os.path.join(directory_path, "connections.json")
    devices_file = os.path.join(directory_path, "devices.json")
    device_connections_file = os.path.join(directory_path, "device_connections.json")

    # 检查是否需要重新读取数据
    if not reRead:
        print("load_data_from_file")
        nodes = load_data_from_file(nodes_file)
        connections = load_data_from_file(connections_file)
        devices = load_data_from_file(devices_file)
        device_connections = load_data_from_file(device_connections_file)
        return nodes, connections, devices, device_connections

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

    # 1. 获取 nodes 和 connections
    nodes = {}
    connections = []

    def find_node_id_by_coordinates(coordinates):
        """根据坐标查找节点 ID，如果不存在则返回 None"""
        for node_id, node_coords in nodes.items():
            if node_coords == coordinates:
                return node_id
        return None

    for tunnel in tunnels_data:
        path = tunnel["path"]
        connected_to = tunnel.get("connected_to", [])

        # 处理 path 中的点
        for i, point in enumerate(path):
            coordinates = (int(point["point_x"]), int(point["point_y"]), int(point["point_z"]))
            node_id = find_node_id_by_coordinates(coordinates)
            if not node_id:  # 如果节点不存在则创建
                node_id = f"P{len(nodes) + 1}"
                nodes[node_id] = coordinates

            if i > 0:  # 建立连接
                prev_coordinates = (int(path[i - 1]["point_x"]), int(path[i - 1]["point_y"]), int(path[i - 1]["point_z"]))
                prev_node_id = find_node_id_by_coordinates(prev_coordinates)
                if prev_node_id:
                    connections.append((prev_node_id, node_id))

        # 处理 connected_to 中的点
        for connected_point in connected_to:
            connected_coordinates = (
                int(connected_point["point_x"]),
                int(connected_point["point_y"]),
                int(connected_point["point_z"])
            )
            connected_node_id = find_node_id_by_coordinates(connected_coordinates)
            if not connected_node_id:  # 如果 connected_to 的点不存在于 nodes 中，则跳过
                continue

            # 确定插入位置
            for j in range(len(path) - 1):
                start_coordinates = (int(path[j]["point_x"]), int(path[j]["point_y"]), int(path[j]["point_z"]))
                end_coordinates = (int(path[j + 1]["point_x"]), int(path[j + 1]["point_y"]), int(path[j + 1]["point_z"]))

                if start_coordinates[0] <= connected_coordinates[0] <= end_coordinates[0] or \
                   start_coordinates[1] <= connected_coordinates[1] <= end_coordinates[1] or \
                   start_coordinates[2] <= connected_coordinates[2] <= end_coordinates[2]:
                    # 插入 connected_point 到 path 中
                    path.insert(j + 1, {
                        "point_x": connected_point["point_x"],
                        "point_y": connected_point["point_y"],
                        "point_z": connected_point["point_z"]
                    })
                    # 更新连接
                    start_node_id = find_node_id_by_coordinates(start_coordinates)
                    end_node_id = find_node_id_by_coordinates(end_coordinates)
                    if start_node_id and end_node_id:
                        # 移除原来的直接连接
                        if (start_node_id, end_node_id) in connections:
                            connections.remove((start_node_id, end_node_id))
                        # 添加新的连接
                        connections.append((start_node_id, connected_node_id))
                        connections.append((connected_node_id, end_node_id))
                    break

    # 2. 获取 devices
    devices = {}
    for equip in equis_data:
        device_id = equip["id"]
        devices[device_id] = (int(equip["point_x"]), int(equip["point_y"]), int(equip["point_z"]))

    # 3. 获取 device_connections
    cable_radius_map = {cable["cable_id"]: cable["cable_radius"] for cable in cables_data}
    device_connections = []
    for conn in connections_data:
        device1, device2 = conn["connection"]
        cable_id = conn["cable_id"]
        load_rate = cable_radius_map.get(cable_id, 0)  # 获取 cable_radius 作为负载率
        device_connections.append({
            "device1": device1,
            "device2": device2,
            "load_rate": load_rate
        })

    save_data_to_file(nodes, nodes_file)
    save_data_to_file(connections, connections_file)
    save_data_to_file(devices, devices_file)
    save_data_to_file(device_connections, device_connections_file)

    return nodes, connections, devices, device_connections


if __name__ == "__main__":
    directory = "../../data/ExportDtas"
    nodes, connections, devices, device_connections = real_data_api(directory)
    # print("Nodes:", nodes)
    # print("Connections:", connections)
    # print("Devices:", devices)
    # print("Device Connections:", device_connections)