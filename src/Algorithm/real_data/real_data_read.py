import json
import os


def real_data_api(directory_path="/Users/bytedance/pycharm/cabin/ExportDtas"):
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
    for tunnel in tunnels_data:
        path = tunnel["path"]
        for i, point in enumerate(path):
            node_id = f"P{len(nodes) + 1}"  # 生成唯一节点 ID
            nodes[node_id] = (point["point_x"], point["point_y"], point["point_z"])
            if i > 0:  # 建立连接
                prev_node_id = f"P{len(nodes) - 1}"
                connections.append((prev_node_id, node_id))

    # 2. 获取 devices
    devices = {}
    for equip in equis_data:
        device_id = equip["id"]
        devices[device_id] = (equip["point_x"], equip["point_y"], equip["point_z"])

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

    return nodes, connections, devices, device_connections


if __name__ == "__main__":
    directory = "/Users/bytedance/pycharm/cabin/ExportDtas"
    nodes, connections, devices, device_connections = real_data_api(directory)
    print("Nodes:", nodes)
    print("Connections:", connections)
    print("Devices:", devices)
    print("Device Connections:", device_connections)
