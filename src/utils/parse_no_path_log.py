import re


def parse_no_path_connections(log_path):
    """解析日志文件，提取未找到路径的连接信息（含load_rate）"""
    no_path_connections = []
    current_connection = None

    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            # 捕获连接信息行
            if line.startswith("Connection:"):
                parts = line.split("->")
                device1 = parts[0].split(": ")[1].split("[")[0].strip()
                device2 = parts[1].split("[")[0].strip()
                coord1 = parts[0].split("[")[1].split("]")[0]
                coord2 = parts[1].split("[")[1].split("]")[0]
                current_connection = {
                    "device1": device1,
                    "device2": device2,
                    "coord1": coord1,
                    "coord2": coord2,
                    "start_node": None,
                    "end_node": None,
                    "load_rate": None
                }

            if line.startswith("device start_node:") and current_connection:
                # 匹配所有带方括号的坐标值（包含start和end）
                coord_pattern = r'(\w+_node_value):\[([^\]]+)\]'
                matches = re.findall(coord_pattern, line)

                if len(matches) >= 2:
                    # matches结构示例: [('start_node_value', '5456, -6500, 5918'), ('end_node_value', '5050, -7345, 6822')]
                    current_connection["start_node"] = matches[0][1]  # 取第一个坐标值
                    current_connection["end_node"] = matches[1][1]  # 取第二个坐标值
                else:
                    print(f"无法解析节点坐标: {line.strip()}")
                    current_connection = None
                    continue

            # 捕获负载率行
            if line.startswith("Load rate:") and current_connection:
                load_rate = float(line.split(": ")[1].strip())
                current_connection["load_rate"] = load_rate

            # 捕获无路径结果行
            if "No valid path found" in line and current_connection:
                if current_connection["load_rate"] is None:
                    print(
                        f"警告：连接 {current_connection['device1']}->{current_connection['device2']} 未找到load_rate，已跳过")
                    current_connection = None
                    continue
                no_path_connections.append(current_connection)
                current_connection = None

    return no_path_connections


if __name__ == "__main__":
    import json

    log_file = "log/log_20250620_151854.txt"  # 根据实际日志路径调整
    result = parse_no_path_connections(log_file)

    print(f"共找到 {len(result)} 条未找到路径的连接：")
    for idx, conn in enumerate(result, 1):
        print(f"{idx}. {conn['device1']} -> {conn['device2']} (load_rate: {conn['load_rate']})")

    # 输出为JSON文件（与device_connections.json结构一致）
    with open("log/no_path_connections.json", "w", encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)