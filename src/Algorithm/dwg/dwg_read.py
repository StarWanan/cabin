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


def extract_nodes_and_connections(file_path):
    # 读取DWG文件
    dwg = ezdxf.readfile(file_path)
    # 获取模型空间
    modelspace = dwg.modelspace()

    nodes = {}
    connections = []
    node_counter = 1

    def add_node(point):
        nonlocal node_counter
        node_name = f"P{node_counter}"
        truncated_point = (int(point[0]), int(point[1]), int(point[2]))
        nodes[node_name] = truncated_point
        node_counter += 1
        return node_name

    # 添加图层过滤
    TARGET_LAYER = "DM9_CABLETRAY"

    for entity in modelspace:
        if entity.dxf.layer != TARGET_LAYER:
            continue

        if entity.dxftype() == 'LINE':
            start_node = add_node(entity.dxf.start)
            end_node = add_node(entity.dxf.end)
            connections.append((start_node, end_node))
        elif entity.dxftype() == 'LWPOLYLINE':
            points = entity.get_points()
            previous_node = None
            for point in points:
                current_node = add_node(point)
                if previous_node:
                    connections.append((previous_node, current_node))
                previous_node = current_node
        elif entity.dxftype() == 'POLYLINE':
            vertices = [vertex.dxf.location for vertex in entity.vertices]
            previous_node = None
            for vertex in vertices:
                current_node = add_node(vertex)
                if previous_node:
                    connections.append((previous_node, current_node))
                previous_node = current_node

    return nodes, connections

if __name__ == "__main__":
    file_path = "../../../test.dxf"
    nodes, connections = extract_nodes_and_connections(file_path)
    print("Nodes:")
    for key, value in nodes.items():
        print(f"{key}: {value}")
    print("\nConnections:")
    for connection in connections:
        print(connection)
    nodes, connections = remove_duplicate_nodes(nodes, connections)
    # visualize_graph(nodes, connections)
