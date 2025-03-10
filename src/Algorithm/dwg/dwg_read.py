import ezdxf

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

if __name__ == "__main__":
    file_path = "../../../test.dxf"
    read_dwg(file_path)