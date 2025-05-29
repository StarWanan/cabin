import json

# 定义文件路径（根据实际环境调整）
file_path = "src/data/ExportDtas/devices.json"

# 读取并解析JSON文件
with open(file_path, 'r') as f:
    devices = json.load(f)

# 筛选z坐标超过20400的设备
filtered_devices = []
for device_name, coordinates in devices.items():
    # 确保坐标数组有3个元素（x, y, z）
    if len(coordinates) == 3:
        x, y, z = coordinates
        if z > 20400:
            filtered_devices.append({
                "设备名称": device_name,
                "坐标(x, y, z)": coordinates
            })

# 输出结果
print("z坐标超过20400的设备列表：")
for device in filtered_devices:
    print(f"{device['设备名称']}: {device['坐标(x, y, z)']}")