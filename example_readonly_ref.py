#!/usr/bin/env python3
"""
ReadOnlyRef 示例演示

此示例演示了如何使用 ReadOnlyRef 作为 Ref 的只读代理。
ReadOnlyRef 可以追踪底层 Ref 的变化，但不允许修改。
"""

from cognihub_pyeffectref import Ref, ReadOnlyRef, effect


def main():
    print("=== ReadOnlyRef 基本功能演示 ===")
    
    # 创建一个基础的 Ref
    counter = Ref(0)
    print(f"原始 counter: {counter.value}")
    
    # 创建只读代理
    readonly_counter: ReadOnlyRef[int] = ReadOnlyRef(counter)
    print(f"readonly_counter: {readonly_counter.value}")
    
    # 修改原始 Ref，只读代理会自动跟踪变化
    counter.value = 10
    print(f"修改后 counter: {counter.value}")
    print(f"readonly_counter 自动跟踪: {readonly_counter.value}")
    
    print("\n=== ReadOnlyRef 与 Effect 配合 ===")
    
    # 创建一个状态 Ref
    name = Ref("Alice")
    readonly_name: ReadOnlyRef[str] = ReadOnlyRef(name)
    
    @effect
    def watch_name():
        print(f"名字变化了: {readonly_name.value}")
    
    # 首次运行 effect
    watch_name()
    
    # 修改原始值，effect 会自动触发
    name.value = "Bob"
    name.value = "Charlie"
    
    print("\n=== ReadOnlyRef 订阅功能 ===")
    
    # 创建一个数据 Ref
    data = Ref([1, 2, 3])
    readonly_data: ReadOnlyRef[list[int]] = ReadOnlyRef(data)
    
    def on_data_change(new_val: list[int], old_val: list[int]) -> None:
        print(f"数据变化: {old_val} -> {new_val}")
    
    # 订阅只读代理的变化
    readonly_data.subscribe(on_data_change)
    
    # 修改原始数据
    data.value = [4, 5, 6]
    data.value = [7, 8, 9, 10]
    
    print("\n=== ReadOnlyRef 安全性演示 ===")
    
    # 尝试修改只读代理（这会失败）
    try:
        readonly_counter.value = 999  # type: ignore
        print("错误：不应该能够修改只读代理！")
    except AttributeError as e:
        print(f"正确：只读代理无法修改 - {type(e).__name__}")
    
    print("\n=== ReadOnlyRef 类型保持 ===")
    
    # 演示类型保持
    str_ref = Ref("Hello")
    readonly_str: ReadOnlyRef[str] = ReadOnlyRef(str_ref)
    print(f"字符串类型: {repr(readonly_str)}")
    
    int_ref = Ref(42)
    readonly_int: ReadOnlyRef[int] = ReadOnlyRef(int_ref)
    print(f"整数类型: {repr(readonly_int)}")
    
    dict_ref = Ref({"key": "value"})
    readonly_dict: ReadOnlyRef[dict[str, str]] = ReadOnlyRef(dict_ref)
    print(f"字典类型: {repr(readonly_dict)}")
    
    print("\n=== ReadOnlyRef 多订阅者演示 ===")
    
    temperature = Ref(20.0)
    readonly_temp: ReadOnlyRef[float] = ReadOnlyRef(temperature)
    
    def celsius_monitor(new_temp: float, old_temp: float) -> None:
        print(f"摄氏度监控: {old_temp}°C -> {new_temp}°C")
    
    def fahrenheit_monitor(new_temp: float, old_temp: float) -> None:
        old_f = old_temp * 9/5 + 32
        new_f = new_temp * 9/5 + 32
        print(f"华氏度监控: {old_f:.1f}°F -> {new_f:.1f}°F")
    
    # 多个订阅者
    readonly_temp.subscribe(celsius_monitor)
    readonly_temp.subscribe(fahrenheit_monitor)
    
    # 温度变化
    temperature.value = 25.0
    temperature.value = 30.0
    
    print("\n演示完成！")


if __name__ == "__main__":
    main()
