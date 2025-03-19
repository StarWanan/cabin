import ezdxf

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


def extract_nodes_and_connections(file_path, filter_y=150000):
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

def extract_hubs(file_path, filter_y=150000):
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

if __name__ == "__main__":
    file_path = "../../../test.dxf"
    nodes, connections = extract_nodes_and_connections(file_path)
    nodes, connections = remove_duplicate_nodes(nodes, connections)
    print("Nodes:")
    for key, value in nodes.items():
        print(f"{key}: {value}")
    print("\nConnections:")
    for connection in connections:
        print(connection)
    visualize_graph(nodes, connections)

    hubs = extract_hubs(file_path)
    filtered_hubs = filter_hubs_on_connections(nodes, connections, hubs)
    print("Filtered Hubs:")
    for key, value in filtered_hubs.items():
        print(f"{key}: {value}")

