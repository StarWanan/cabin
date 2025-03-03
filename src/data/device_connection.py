import random
import itertools
from device import device

def generate_device_connections(seed, num_pairs=10):
    random.seed(seed)

    device_names = list(device.keys())
    all_pairs = list(itertools.combinations(device_names, 2))  # 生成所有两两组合
    selected_pairs = random.sample(all_pairs, num_pairs)       # 随机选取指定数量的组合

    device_connection = []
    for pair in selected_pairs:
        device1, device2 = pair
        load_rate = random.choice([10, 20, 30, 40, 50])       # 随机选择负载率
        device_connection.append({
            "device1": device1,
            "device2": device2,
            "load_rate": load_rate
        })

    return device_connection

if __name__ == "__main__":
    connections = generate_device_connections(seed=42, num_pairs=10)
    for connection in connections:
        print(connection)