import sys
from pathlib import Path

# 把项目根目录加入模块搜索路径，否则pytest找不到app.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))