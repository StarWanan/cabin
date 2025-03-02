# Layer 1 devices
layer1_devices = {
    "device_1_1": (360, 20, 100),
    "device_1_2": (180, 40, 100),
    "device_1_3": (120, 100, 100),
    "device_1_4": (130, 20, 100),
    "device_1_5": (240, 80, 100)
}

# Layer 2 devices
layer2_devices = {
    "device_2_1": (40, 40, 200),
    "device_2_2": (50, 80, 200),
    "device_2_3": (60, 60, 200),
    "device_2_4": (100, 70, 200),
    "device_2_5": (80, 80, 200)
}

# Layer 3 devices
layer3_devices = {
    "device_3_1": (300, 20, 300),
    "device_3_2": (110, 70, 300),
    "device_3_3": (120, 50, 300),
    "device_3_4": (130, 70, 300),
    "device_3_5": (140, 20, 300)
}

# Layer 4 devices
layer4_devices = {
    "device_4_1": (10, 30, 400),
    "device_4_2": (110, 40, 400),
    "device_4_3": (220, 50, 400),
    "device_4_4": (330, 60, 400),
    "device_4_5": (440, 70, 400)
}

device = {**layer1_devices, **layer2_devices, **layer3_devices, **layer4_devices}