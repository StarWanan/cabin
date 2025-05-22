from real_data_read import insert_connected_points


def test_insert_connected_points():
    # 定义路径
    path = [
        {"point_x": 41304.55, "point_y": 8330.0, "point_z": 19775.9648},
        {"point_x": 41304.55, "point_y": 5026.179, "point_z": 19775.9648},
        {"point_x": 41304.55, "point_y": 4882.827, "point_z": 19675.5879},
        {"point_x": 41304.55, "point_y": 4262.827, "point_z": 19675.5879},
        {"point_x": 41304.55, "point_y": 4105.072, "point_z": 19786.0488},
        {"point_x": 41304.55, "point_y": -1644.928, "point_z": 19786.0488},
        {"point_x": 41304.55, "point_y": -1792.649, "point_z": 19812.0957},
        {"point_x": 41304.55, "point_y": -3392.649, "point_z": 19812.0957},
        {"point_x": 41304.55, "point_y": -3437.965, "point_z": 19790.9648},
        {"point_x": 41304.55, "point_y": -4037.965, "point_z": 19790.9648},
        {"point_x": 41304.55, "point_y": -4201.795, "point_z": 19676.25},
        {"point_x": 41304.55, "point_y": -4986.795, "point_z": 19676.25},
        {"point_x": 41304.55, "point_y": -5160.0, "point_z": 19776.25},
        {"point_x": 41304.55, "point_y": -8610.0, "point_z": 19776.25},
        {"point_x": 41304.55, "point_y": -8745.0, "point_z": 19776.25},
        {"point_x": 41304.55, "point_y": -8745.0, "point_z": 19776.25}
    ]

    # 定义需要插入的连接点
    connected_to = [
        {"point_x": 41304.55, "point_y": -995.0, "point_z": 19786.0488},
        {"point_x": 41304.55, "point_y": 1996.002, "point_z": 19786.0488},
        {"point_x": 41304.55, "point_y": 3497.502, "point_z": 19786.0488},
        {"point_x": 41304.55, "point_y": -3497.505, "point_z": 19790.9648},
        {"point_x": 41304.55, "point_y": -1995.999, "point_z": 19812.0957},
        {"point_x": 41304.55, "point_y": 1996.002, "point_z": 19786.0488},
        {"point_x": 41304.55, "point_y": 3497.502, "point_z": 19786.0488},
        {"point_x": 41304.55, "point_y": 8230.0, "point_z": 19775.9648},
        {"point_x": 41304.55, "point_y": 5378.0, "point_z": 19775.9648},
        {"point_x": 41304.55, "point_y": 5378.0, "point_z": 19775.9648},
        {"point_x": 41304.55, "point_y": 4710.0, "point_z": 19675.5879},
        {"point_x": 41304.55, "point_y": 2750.0, "point_z": 19786.0488},
        {"point_x": 41304.55, "point_y": -225.0, "point_z": 19786.0488},
        {"point_x": 41304.55, "point_y": -2750.0, "point_z": 19812.0957},
        {"point_x": 41304.55, "point_y": -4715.76, "point_z": 19676.25},
        {"point_x": 41304.55, "point_y": -4715.76, "point_z": 19676.25},
        {"point_x": 41304.55, "point_y": -225.0, "point_z": 19786.0488},
        {"point_x": 41304.55, "point_y": -4715.76, "point_z": 19676.25}
    ]

    # 调用函数
    print("len path:", len(path))
    updated_path = insert_connected_points(path, connected_to)

    print("Updated Path:")
    print("len Updated Path:", len(updated_path))
    for point in updated_path:
        print(point)

# 执行测试
test_insert_connected_points()