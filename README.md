# CogniHub PyEffectRef

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/cognihub-pyeffectref.svg)](https://badge.fury.io/py/cognihub-pyeffectref)

CogniHub 项目用到的类似 Vue 3 中 effect/ref 的简化版实现。这个库提供了一个响应式编程模型，允许您创建响应式数据容器并自动响应数据变化。

## 特性

- 🔄 **响应式编程**: 类似 Vue 3 Composition API 的响应式系统
- 🔒 **线程安全**: 支持多线程环境下的安全操作
- ⚡ **异步支持**: 完整支持 asyncio 协程环境
- 🎯 **类型提示**: 完整的 TypeScript 风格类型提示支持
- 🧩 **简单易用**: 简洁直观的 API 设计

## 安装

```bash
pip install cognihub-pyeffectref
```

或从源码安装：

```bash
git clone https://github.com/hsz1273327/cognihub_pyeffectref.git
cd cognihub_pyeffectref
pip install -e .
```

## 快速开始

### 基本用法

```python
from cognihub_pyeffectref import Ref, effect

# 创建响应式数据
count = Ref(0)
name = Ref("Alice")

# 创建副作用函数
@effect
def log_count():
    print(f"Count is: {count.value}")

@effect
def log_greeting():
    print(f"Hello, {name.value}!")

# 初始执行
log_count()  # 输出: Count is: 0
log_greeting()  # 输出: Hello, Alice!

# 修改数据，自动触发副作用
count.value = 5  # 输出: Count is: 5
name.value = "Bob"  # 输出: Hello, Bob!
```

### 异步支持

```python
import asyncio
from cognihub_pyeffectref import Ref, effect

data = Ref("initial")

@effect
async def async_effect():
    print(f"Async effect: {data.value}")
    # 可以在这里执行异步操作
    await asyncio.sleep(0.1)

async def main():
    await async_effect()  # 输出: Async effect: initial
    data.value = "updated"  # 自动触发异步副作用

asyncio.run(main())
```

### 类型提示支持

```python
from typing import List
from cognihub_pyeffectref import Ref

# 泛型类型支持
numbers: Ref[List[int]] = Ref([1, 2, 3])
user_id: Ref[int] = Ref(42)
is_active: Ref[bool] = Ref(True)

print(numbers.value)  # [1, 2, 3]
print(user_id.value)  # 42
print(is_active.value)  # True
```

### 手动订阅和取消订阅

```python
from cognihub_pyeffectref import Ref

counter = Ref(0)

def on_counter_change(new_value, old_value):
    print(f"Counter changed from {old_value} to {new_value}")

# 手动订阅
counter.subscribe(on_counter_change)

counter.value = 1  # 输出: Counter changed from 0 to 1
counter.value = 2  # 输出: Counter changed from 1 to 2

# 取消订阅
counter.unsubscribe(on_counter_change)
counter.value = 3  # 不会触发回调
```

## API 参考

### Ref[T]

响应式数据容器类。

#### 构造函数
- `Ref(initial_value: T)`: 创建一个新的响应式引用

#### 属性
- `value: T`: 获取或设置引用的值

#### 方法
- `subscribe(callback: Callable[[T, T], None])`: 订阅值变化
- `unsubscribe(callback: Callable[[T, T], None])`: 取消订阅

### effect

副作用装饰器，用于创建响应式副作用函数。

```python
@effect
def my_effect():
    # 访问 Ref.value 会自动建立依赖关系
    pass

# 或手动调用
effect_wrapper = effect(my_function)
effect_wrapper()
```

### EffectWrapper

effect 装饰器返回的包装器类。

#### 方法
- `stop()`: 停止副作用，使其不再响应数据变化

## 线程安全

本库在设计时考虑了线程安全：

- `Ref` 使用内部锁来保护订阅者集合的并发修改
- 支持在多线程环境中安全地读写响应式数据
- 异步环境使用 `contextvars` 来隔离上下文

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black .
isort .
```

### 类型检查

```bash
mypy cognihub_pyeffectref
```

## 贡献

欢迎贡献代码！请确保：

1. 所有测试通过
2. 代码符合项目风格规范
3. 添加适当的类型提示
4. 更新相关文档

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 变更日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本变更历史。
