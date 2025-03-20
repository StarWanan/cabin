import ezdxf
import random
from cabin.src.vis.vis import remove_duplicate_nodes, visualize_graph


def read_dwg(file_path):
    # 读取DWG文件
    dwg = ezdxf.readfile(file_path)
    # 获取模型空间
    modelspace = dwg.modelspace()

    # 遍历所有实体并打印详细信息
    for entity in modelspace:
        print(f"实体类型: {entity.dxftype()}")
        if entity.dxftype() == 'LINE':
            print(f"  起点: {entity.dxf.start}")
            print(f"  终点: {entity.dxf.end}")
        elif entity.dxftype() == 'CIRCLE':
            print(f"  中心: {entity.dxf.center}")
            print(f"  半径: {entity.dxf.radius}")
        elif entity.dxftype() == 'ARC':
            print(f"  中心: {entity.dxf.center}")
            print(f"  半径: {entity.dxf.radius}")
            print(f"  起始角度: {entity.dxf.start_angle}")
            print(f"  终止角度: {entity.dxf.end_angle}")
        elif entity.dxftype() == 'LWPOLYLINE':
            print(f"  顶点: {entity.get_points()}")
        elif entity.dxftype() == 'MTEXT':
            print(f"  内容: {entity.text}")
        elif entity.dxftype() == 'POLYLINE':
            print(f"  顶点: {[vertex.dxf.location for vertex in entity.vertices]}")
        elif entity.dxftype() == 'INSERT':
            print(f"  块名: {entity.dxf.name}")
            print(f"  插入点: {entity.dxf.insert}")
        elif entity.dxftype() == 'TEXT':
            print(f"  内容: {entity.dxf.text}")
            print(f"  插入点: {entity.dxf.insert}")
        else:
            print(f"  未知实体类型或未处理的实体类型: {entity.dxftype()}")


def extract_nodes_and_connections(file_path, filter_y=50000):
    # 读取DWG文件
    dwg = ezdxf.readfile(file_path)
    # 获取模型空间
    modelspace = dwg.modelspace()

    nodes = {}
    connections = []
    node_counter = 1

    def add_node(point):
        nonlocal node_counter
        if point[1] < filter_y:
            node_name = f"P{node_counter}"
            truncated_point = (int(point[0]), int(point[1]), int(point[2]))
            nodes[node_name] = truncated_point
            node_counter += 1
            return node_name
        return None

    # 添加图层过滤
    TARGET_LAYER = "DM9_CABLETRAY"

    for entity in modelspace:
        if entity.dxf.layer != TARGET_LAYER:
            continue

        if entity.dxftype() == 'LINE':
            start_node = add_node(entity.dxf.start)
            end_node = add_node(entity.dxf.end)
            if start_node and end_node:
                connections.append((start_node, end_node))
        elif entity.dxftype() == 'LWPOLYLINE':
            points = entity.get_points()
            previous_node = None
            for point in points:
                current_node = add_node(point)
                if current_node:
                    if previous_node:
                        connections.append((previous_node, current_node))
                    previous_node = current_node
        elif entity.dxftype() == 'POLYLINE':
            vertices = [vertex.dxf.location for vertex in entity.vertices]
            previous_node = None
            for vertex in vertices:
                current_node = add_node(vertex)
                if current_node:
                    if previous_node:
                        connections.append((previous_node, current_node))
                    previous_node = current_node

    return nodes, connections

def extract_hubs(file_path, filter_y=50000):
    dwg = ezdxf.readfile(file_path)
    modelspace = dwg.modelspace()

    hubs = {}
    hub_counter = 1

    TARGET_LAYER = "DM9_CABLETRAY_VERTICAL"

    for entity in modelspace:
        if entity.dxf.layer != TARGET_LAYER:
            continue

        if entity.dxftype() == 'INSERT':
            insert_point = entity.dxf.insert
            if insert_point[1] < filter_y:
                hub_name = f"hub_{hub_counter}"
                truncated_point = (int(insert_point[0]), int(insert_point[1]), int(insert_point[2]))
                hubs[hub_name] = truncated_point
                hub_counter += 1

    return hubs


def is_point_on_horizontal_or_vertical_line(point, line_start, line_end):
    """检查一个点是否在水平或垂直的线段上"""
    x0, y0, z0 = point
    x1, y1, z1 = line_start
    x2, y2, z2 = line_end

    # 检查是否在水平线段上
    if y1 == y2 and y0 == y1:
        return min(x1, x2) <= x0 <= max(x1, x2) and min(z1, z2) <= z0 <= max(z1, z2)

    # 检查是否在垂直线段上
    if x1 == x2 and x0 == x1:
        return min(y1, y2) <= y0 <= max(y1, y2) and min(z1, z2) <= z0 <= max(z1, z2)

    return False


def filter_hubs_on_connections(nodes, connections, hubs):
    filtered_hubs = {}

    for hub_name, hub_point in hubs.items():
        for connection in connections:
            start_node, end_node = connection
            line_start = nodes[start_node]
            line_end = nodes[end_node]

            if is_point_on_horizontal_or_vertical_line(hub_point, line_start, line_end):
                filtered_hubs[hub_name] = hub_point
                break

    return filtered_hubs

def remove_duplicate_hubs(hubs):
    value_to_key = {}
    new_hubs = {}
    for key, value in hubs.items():
        if value not in value_to_key:
            value_to_key[value] = key
            new_hubs[key] = value

    return new_hubs

def update_z_coordinates(nodes, hubs, layer12=-200000, layer23=-135000, layer34=-90000, layer45=-40000):
    def update_z(point):
        x, y, z = point
        if y < layer12:
            new_z = 0
        elif layer12 < y <= layer23:
            new_z = 2525
        elif layer23 < y <= layer34:
            new_z = 2525 * 2
        elif layer34 < y <= layer45:
            new_z = 2525 * 3
        else:
            new_z = 2525 * 4
        return (x, y, new_z)

    updated_nodes = {key: update_z(value) for key, value in nodes.items()}
    updated_hubs = {key: update_z(value) for key, value in hubs.items()}

    return updated_nodes, updated_hubs


def normalize_y_coordinates(nodes, hubs, layer12=-200000, layer23=-135000, layer34=-90000, layer45=-40000):
    def get_layer(y):
        if y < layer12:
            return 1
        elif layer12 < y <= layer23:
            return 2
        elif layer23 < y <= layer34:
            return 3
        elif layer34 < y <= layer45:
            return 4
        else:
            return 5

    def calculate_layer_center(layer_points):
        min_y = min(layer_points)
        max_y = max(layer_points)
        return (min_y + max_y) / 2

    layer_points = {1: [], 2: [], 3: [], 4: [], 5: []}
    for point in nodes.values():
        layer = get_layer(point[1])
        layer_points[layer].append(point[1])
    for point in hubs.values():
        layer = get_layer(point[1])
        layer_points[layer].append(point[1])

    # 计算每一层的中心
    layer_centers = {layer: calculate_layer_center(points) for layer, points in layer_points.items()}

    # 计算总中心
    total_center = sum(layer_centers.values()) / len(layer_centers)

    def normalize_y(point):
        x, y, z = point
        layer = get_layer(y)
        layer_center = layer_centers[layer]
        normalized_y = y + (total_center - layer_center)
        return (x, normalized_y, z)

    normalized_nodes = {key: normalize_y(value) for key, value in nodes.items()}
    normalized_hubs = {key: normalize_y(value) for key, value in hubs.items()}

    return normalized_nodes, normalized_hubs

def generate_hubs_connections(hubs):
    connections = []
    z_difference = 2525

    hubs_list = list(hubs.items())
    hubs_list.sort(key=lambda item: item[1])  # 按照坐标排序，便于查找

    for i, (hub_name1, hub_point1) in enumerate(hubs_list):
        for j in range(i + 1, len(hubs_list)):
            hub_name2, hub_point2 = hubs_list[j]
            if hub_point1[0] == hub_point2[0] and hub_point1[1] == hub_point2[1]:
                if abs(hub_point1[2] - hub_point2[2]) == z_difference:
                    connections.append((hub_name1, hub_name2))
                elif hub_point1[2] + z_difference < hub_point2[2]:
                    # 由于 hubs_list 是按 z 坐标排序的，如果 hub_point1 和 hub_point2 的 z 坐标差值超过 2525，
                    # 则后续的 hub_point3, hub_point4, ... 的 z 坐标差值只会更大，可以提前终止内层循环
                    break

    return connections

def generate_devices_and_connections(nodes, seed, layers=5, devices_per_layer=2, z_difference=2525):
    random.seed(seed)

    devices = {}
    device_connections = []

    # 将 nodes 按层分组
    layer_nodes = {layer: [] for layer in range(1, layers + 1)}
    for node_name, point in nodes.items():
        x, y, z = point
        layer = z // z_difference + 1
        if layer in layer_nodes:
            layer_nodes[layer].append(point)

    # 生成设备
    for layer in range(1, layers + 1):
        for i in range(devices_per_layer):
            if not layer_nodes[layer]:
                raise ValueError(f"No nodes available for layer {layer}")
            base_point = random.choice(layer_nodes[layer])
            x, y, z = base_point
            device_name = f"device_{layer}_{i+1}"
            devices[device_name] = (x + 10000, y + 10000, z)

    # 生成设备连接
    for layer in range(1, layers + 1):
        device1 = f"device_{layer}_1"
        device2 = f"device_{layer}_2"
        load_rate = random.choice([10, 20, 30, 40, 50])  # 随机选择负载率
        device_connections.append({
            "device1": device1,
            "device2": device2,
            "load_rate": load_rate
        })

    return devices, device_connections

def dwg_api(file_path, seed=42):
    nodes, connections = extract_nodes_and_connections(file_path)
    nodes, connections = remove_duplicate_nodes(nodes, connections)

    hubs = extract_hubs(file_path)
    hubs = remove_duplicate_hubs(hubs)
    filtered_hubs = filter_hubs_on_connections(nodes, connections, hubs)

    updated_nodes, updated_hubs = update_z_coordinates(nodes, filtered_hubs)

    normalized_nodes, normalized_hubs = normalize_y_coordinates(updated_nodes, updated_hubs)

    devices, device_connections = generate_devices_and_connections(normalized_nodes, seed=seed)

    return normalized_nodes, connections, devices, device_connections


if __name__ == "__main__":
    file_path = "src/data/test.dxf"
    nodes, connections, devices, device_connections = dwg_api(file_path, seed=42)

    print("\nNodes:")
    for key, value in nodes.items():
        print(f"{key}: {value}")
    print("\nConnections:")
    for connection in connections:
        print(connection)
    print("\nDevices:")
    for key, value in devices.items():
        print(f"{key}: {value}")
    print("\nDevice Connections:")
    for connection in device_connections:
        print(connection)
