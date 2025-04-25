#!/bin/bash

# 设置Python路径
export PYTHONPATH="../:$PYTHONPATH"

mkdir -p log
# python -m Algorithm.main > output.txt
python src/Algorithm/main.py > log/log_$(date +%Y%m%d_%H%M%S).txt


