"""测试配置文件 - 使用标准库"""
import unittest
import sys
import os

# 添加项目根目录到 Python 路径,确保可以导入 cognihub_pyeffectref
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 这里可以添加全局的测试配置,但使用标准库 unittest 时通常不需要额外配置
