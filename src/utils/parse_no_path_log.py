def parse_no_path_connections(log_path):
    """解析日志文件，提取未找到路径的连接信息（含load_rate）"""
    no_path_connections = []
    current_connection = None

    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            # 捕获连接信息行
            if line.startswith("Connection:"):
                # 格式示例: "Connection: /J13-3-9[(71658, 6111, 19624)] -> /J13-3-10[(71653, -6149, 19624)]"
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
                    "load_rate": None  # 初始化load_rate字段
                }
            
            # 捕获负载率行
            if line.startswith("Load rate:") and current_connection:
                load_rate = float(line.split(": ")[1].strip())
                current_connection["load_rate"] = load_rate  # 填充load_rate
            
            # 捕获无路径结果行
            if "No valid path found" in line and current_connection:
                # 确保load_rate已被捕获（避免日志格式异常导致缺失）
                if current_connection["load_rate"] is None:
                    print(f"警告：连接 {current_connection['device1']}->{current_connection['device2']} 未找到load_rate，已跳过")
                    current_connection = None
                    continue
                no_path_connections.append(current_connection)
                current_connection = None  # 重置避免重复捕获

    return no_path_connections

if __name__ == "__main__":
    import json
    log_file = "log/log_20250527_192740.txt"  # 根据实际日志路径调整
    result = parse_no_path_connections(log_file)
    
    print(f"共找到 {len(result)} 条未找到路径的连接：")
    for idx, conn in enumerate(result, 1):
        print(f"{idx}. {conn['device1']} -> {conn['device2']} (load_rate: {conn['load_rate']})")
    
    # 输出为JSON文件（与device_connections.json结构一致）
    with open("src/data/ExportDtas/no_path_connections.json", "w", encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)