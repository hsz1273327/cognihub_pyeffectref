# API 参考

## 核心类和函数

### Ref[T]

响应式数据容器，当值发生变化时会自动通知所有订阅者。

#### 构造函数

```python
Ref(initial_value: T)
```

创建一个新的响应式引用。

**参数:**
- `initial_value: T` - 初始值

**示例:**
```python
from cognihub_pyeffectref import Ref

# 创建不同类型的响应式数据
counter = Ref(0)
name = Ref("Alice")
items = Ref([1, 2, 3])
user = Ref({"name": "Bob", "age": 30})
```

#### 属性

##### value: T

获取或设置引用的值。当设置新值时，如果值发生变化，会自动通知所有订阅者。

**示例:**
```python
counter = Ref(0)
print(counter.value)  # 0

counter.value = 5  # 触发通知
print(counter.value)  # 5
```

#### 方法

##### subscribe(callback: Callable[[T, T], None]) -> None

手动订阅值变化事件。

**参数:**
- `callback` - 回调函数，接收 `(new_value, old_value)` 参数

**示例:**
```python
def on_change(new_val, old_val):
    print(f"值从 {old_val} 变为 {new_val}")

counter = Ref(0)
counter.subscribe(on_change)
counter.value = 10  # 输出: 值从 0 变为 10
```

##### unsubscribe(callback: Callable[[T, T], None]) -> None

取消订阅值变化事件。

**参数:**
- `callback` - 要取消订阅的回调函数

**示例:**
```python
counter = Ref(0)
counter.subscribe(on_change)
counter.unsubscribe(on_change)  # 取消订阅
```

---

### effect

装饰器，用于创建响应式副作用函数。被装饰的函数会在其内部访问的 `Ref` 值发生变化时自动重新执行。

#### 语法

```python
@effect
def function_name():
    # 函数体
    pass

# 或者
@effect
async def async_function_name():
    # 异步函数体
    pass
```

#### 返回值

返回一个 `EffectWrapper` 实例。

#### 示例

**同步 effect:**
```python
from cognihub_pyeffectref import Ref, effect

counter = Ref(0)

@effect
def log_counter():
    print(f"计数器: {counter.value}")

log_counter()  # 输出: 计数器: 0
counter.value = 5  # 输出: 计数器: 5
```

**异步 effect:**
```python
import asyncio
from cognihub_pyeffectref import Ref, effect

data = Ref("初始值")

@effect
async def async_logger():
    print(f"异步日志: {data.value}")
    await asyncio.sleep(0.1)

async def main():
    await async_logger()  # 输出: 异步日志: 初始值
    data.value = "新值"  # 异步触发: 异步日志: 新值

asyncio.run(main())
```

---

### EffectWrapper

`effect` 装饰器返回的包装器类，提供对副作用函数的控制。

#### 方法

##### \_\_call\_\_(*args, **kwargs) -> Any

调用包装的函数。

**示例:**
```python
@effect
def my_effect():
    print("执行副作用")

my_effect()  # 调用副作用函数
```

##### stop() -> None

停止副作用函数，使其不再响应 `Ref` 值的变化。

**示例:**
```python
counter = Ref(0)

@effect
def stoppable_effect():
    print(f"计数器: {counter.value}")

stoppable_effect()  # 输出: 计数器: 0
counter.value = 1   # 输出: 计数器: 1

stoppable_effect.stop()  # 停止副作用
counter.value = 2   # 不会输出任何内容
```

##### name: str

获取副作用函数的名称。

**示例:**
```python
@effect
def my_effect():
    pass

print(my_effect.name)  # "my_effect_sync"
```

---

## 类型提示

本库完全支持类型提示，提供良好的 IDE 支持和类型检查。

### 基本类型

```python
from typing import List, Dict
from cognihub_pyeffectref import Ref

# 基础类型
counter: Ref[int] = Ref(0)
name: Ref[str] = Ref("Alice")
is_active: Ref[bool] = Ref(True)

# 复合类型
items: Ref[List[str]] = Ref(["a", "b", "c"])
user: Ref[Dict[str, str]] = Ref({"name": "Bob"})
```

### 自定义类型

```python
from dataclasses import dataclass
from cognihub_pyeffectref import Ref

@dataclass
class User:
    name: str
    age: int

user: Ref[User] = Ref(User("Alice", 25))
```

---

## 最佳实践

### 1. 依赖收集

只有在 `effect` 函数中访问 `Ref.value` 才会建立依赖关系：

```python
counter = Ref(0)

@effect
def good_effect():
    # ✅ 会建立依赖关系
    print(counter.value)

def bad_effect():
    # ❌ 不会建立依赖关系（没有 @effect 装饰器）
    print(counter.value)
```

### 2. 避免无限循环

不要在 effect 中修改其依赖的 Ref：

```python
counter = Ref(0)

@effect
def bad_effect():
    # ❌ 可能导致无限循环
    counter.value = counter.value + 1

# 正确的做法是使用另一个 Ref
derived = Ref(0)

@effect
def good_effect():
    # ✅ 读取一个 Ref，修改另一个 Ref
    derived.value = counter.value * 2
```

### 3. 清理资源

对于长期运行的应用，记得停止不需要的 effect：

```python
@effect
def temp_effect():
    print(f"临时效果: {data.value}")

# 在适当的时候停止
temp_effect.stop()
```

### 4. 异步最佳实践

在异步环境中，确保正确等待异步操作：

```python
@effect
async def async_effect():
    print(f"开始处理: {data.value}")
    await some_async_operation()
    print(f"处理完成: {data.value}")

# 确保等待异步 effect 完成
await async_effect()
```
