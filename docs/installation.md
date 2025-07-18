# 安装指南

## 系统要求

- Python 3.8 或更高版本
- 支持的操作系统：Linux、macOS、Windows

## 使用 pip 安装

### 从 PyPI 安装（推荐）

```bash
pip install cognihub-pyeffectref
```

### 从源码安装

1. 克隆仓库：
```bash
git clone https://github.com/hsz1273327/cognihub_pyeffectref.git
cd cognihub_pyeffectref
```

2. 安装包：
```bash
pip install -e .
```

## 验证安装

创建一个简单的测试文件 `test_install.py`：

```python
from cognihub_pyeffectref import Ref, effect

# 创建一个简单的响应式数据
counter = Ref(0)

@effect
def log_counter():
    print(f"Counter: {counter.value}")

# 测试
log_counter()  # 输出: Counter: 0
counter.value = 5  # 输出: Counter: 5

print("✅ 安装成功！")
```

运行测试：
```bash
python test_install.py
```

如果看到正确的输出，说明安装成功！

## 开发环境设置

如果您想为项目贡献代码，请按照以下步骤设置开发环境：

### 1. 克隆仓库
```bash
git clone https://github.com/hsz1273327/cognihub_pyeffectref.git
cd cognihub_pyeffectref
```

### 2. 运行设置脚本
```bash
./setup-dev.sh
```

或者手动设置：

### 3. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

### 4. 安装开发依赖
```bash
pip install -e ".[dev]"
```

### 5. 设置 pre-commit hooks
```bash
pre-commit install
```

### 6. 运行测试
```bash
pytest
```

## 故障排除

### 常见问题

**Q: ImportError: No module named 'cognihub_pyeffectref'**

A: 确保您在正确的虚拟环境中，并且包已正确安装：
```bash
pip list | grep cognihub-pyeffectref
```

**Q: Python 版本不兼容**

A: 检查您的 Python 版本：
```bash
python --version
```
确保版本 >= 3.8

**Q: 测试失败**

A: 确保安装了测试依赖：
```bash
pip install -e ".[test]"
```

### 获取帮助

如果遇到问题，可以：

1. 查看 [GitHub Issues](https://github.com/hsz1273327/cognihub_pyeffectref/issues)
2. 创建新的 Issue 描述问题
3. 查看示例代码在 `examples/` 目录中
