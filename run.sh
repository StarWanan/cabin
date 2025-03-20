#!/bin/bash

# 设置Python路径
export PYTHONPATH="/Users/bytedance/WorkSpace/SmartLab/:$PYTHONPATH"


# python -m Algorithm.main > output.txt
python src/Algorithm/main.py > log/log_$(date +%Y%m%d_%H%M%S).txt


