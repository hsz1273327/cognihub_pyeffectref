#!/usr/bin/env python3
"""
文档演示脚本

展示 README.md 中提到的所有主要功能和使用模式:
- 底层接口 (Ref/effect) 的各种用法
- 高级接口 (ReactiveDict/ReadOnlyView) 的类型化使用
- 同步、异步、多线程支持
- 执行器配置和控制选项
"""

import asyncio
import threading
import time
import concurrent.futures
from typing import Protocol, TypedDict, cast, Any, List, Dict

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognihub_pyeffectref import Ref, ReadOnlyRef, effect, ReactiveDict, ReadOnlyView


def demo_basic_ref_usage():
    """演示底层接口的基本用法 - 泛型类型指定"""
    print("\n🔧 底层接口演示 - 基本用法")
    print("=" * 50)
    
    # 使用泛型指定类型
    count: Ref[int] = Ref(0)
    name: Ref[str] = Ref("Alice") 
    items: Ref[List[str]] = Ref(["apple", "banana"])
    user_info: Ref[Dict[str, int]] = Ref({"age": 25, "score": 100})

    # 创建副作用函数
    @effect
    def log_count() -> None:
        print(f"  📊 Count is: {count.value}")

    @effect  
    def log_greeting() -> None:
        print(f"  👋 Hello, {name.value}!")

    @effect
    def log_items() -> None:
        print(f"  🛒 Items: {', '.join(items.value)}")

    # 初始执行
    print("📋 初始状态:")
    log_count()
    log_greeting() 
    log_items()

    # 修改数据,自动触发副作用
    print("\n📝 数据变更:")
    count.value = 5
    name.value = "Bob"
    items.value = ["orange", "grape", "kiwi"]
    
    print("✅ 底层接口演示完成")


def demo_sync_async_threading():
    """演示同步、异步、多线程支持"""
    print("\n⚡ 执行模式演示")
    print("=" * 50)
    
    data: Ref[str] = Ref("initial")

    # 1. 同步使用
    print("🔄 同步执行:")
    @effect
    def sync_effect() -> None:
        print(f"  🟢 Sync: {data.value}")

    sync_effect()
    
    # 2. 多线程使用
    print("\n🧵 多线程执行:")
    def thread_worker(thread_id: int) -> None:
        @effect
        def thread_effect() -> None:
            thread_name = threading.current_thread().name
            print(f"  🔵 Thread {thread_id} ({thread_name}): {data.value}")
        
        thread_effect()  # 建立依赖

    # 在多个线程中建立依赖
    threads = []
    for i in range(3):
        thread = threading.Thread(target=thread_worker, args=(i,), name=f"Worker-{i}")
        thread.start()
        threads.append(thread)

    # 等待线程完成
    for thread in threads:
        thread.join()
    
    # 触发所有副作用
    print("\n📢 触发变更:")
    data.value = "updated_by_sync"
    
    time.sleep(0.1)  # 确保所有回调完成
    print("✅ 执行模式演示完成")


async def demo_async_support():
    """演示异步支持"""
    print("\n🚀 异步执行演示")
    print("=" * 50)
    
    async_data: Ref[str] = Ref("async_initial")

    @effect
    async def async_effect() -> None:
        print(f"  🟡 Async effect: {async_data.value}")
        await asyncio.sleep(0.05)  # 模拟异步操作
        print(f"  🟡 Async effect completed for: {async_data.value}")

    print("🔄 建立异步依赖:")
    await async_effect()
    
    print("\n📢 触发异步变更:")
    async_data.value = "async_updated"
    await asyncio.sleep(0.1)  # 等待异步回调完成
    
    print("✅ 异步演示完成")


def demo_executor_configuration():
    """演示执行器配置"""
    print("\n🎛️ 执行器配置演示")
    print("=" * 50)
    
    # 保存原始配置
    original_config = Ref._global_sync_executor_config
    
    try:
        # 1. 默认执行 (当前线程)
        print("🔧 默认执行模式:")
        default_ref = Ref("default")
        
        @effect
        def default_effect() -> None:
            print(f"  ⚪ Default: {default_ref.value}")
        
        default_effect()
        default_ref.value = "default_changed"
        
        # 2. 强制立即同步执行
        print("\n🔧 强制立即同步执行:")
        immediate_ref = Ref("immediate", subscribe_immediate=True)
        
        @effect
        def immediate_effect() -> None:
            print(f"  🔴 Immediate: {immediate_ref.value}")
        
        immediate_effect()
        immediate_ref.value = "immediate_changed"
        
        # 3. 保证顺序执行
        print("\n🔧 顺序执行模式:")
        sequential_ref = Ref("sequential", subscribe_sequential=True)
        
        execution_order = []
        
        @effect
        def seq_effect_1() -> None:
            execution_order.append("effect_1")
            print(f"  🟦 Sequential 1: {sequential_ref.value}")
        
        @effect  
        def seq_effect_2() -> None:
            execution_order.append("effect_2")
            print(f"  🟦 Sequential 2: {sequential_ref.value}")
            
        seq_effect_1()
        seq_effect_2()
        
        sequential_ref.value = "sequential_changed"
        print(f"  📋 执行顺序: {execution_order}")
        
    finally:
        # 恢复原始配置
        Ref._global_sync_executor_config = original_config
    
    print("✅ 执行器配置演示完成")


def demo_reactive_dict_usage():
    """演示 ReactiveDict 结合 TypedDict 的用法"""
    print("\n🏗️ 高级接口演示 - ReactiveDict")
    print("=" * 50)
    
    # 1. 定义数据结构
    class UserData(TypedDict):
        name: str
        email: str  
        age: int
        is_active: bool

    # 2. 创建响应式字典
    user_dict = ReactiveDict({
        'name': 'Alice',
        'email': 'alice@example.com', 
        'age': 25,
        'is_active': True
    })

    # 3. 类型转换以获得类型提示
    user: UserData = cast(UserData, user_dict)

    # 4. 使用时享受完整类型提示
    @effect
    def watch_user() -> None:
        print(f"  👤 User: {user['name']} ({user['age']})")
        print(f"  📧 Email: {user['email']}")
        print(f"  🟢 Active: {user['is_active']}")

    print("📋 初始用户数据:")
    watch_user()

    # 5. 修改数据
    print("\n📝 修改用户数据:")
    user['name'] = 'Bob'
    user['age'] = 26
    user['is_active'] = False
    
    print("✅ ReactiveDict 演示完成")


def demo_readonly_view_usage():
    """演示 ReadOnlyView 结合 Protocol 的用法"""
    print("\n🏗️ 高级接口演示 - ReadOnlyView")
    print("=" * 50)
    
    # 1. 定义 Protocol 描述只读视图结构
    class UserViewProtocol(Protocol):
        name: ReadOnlyRef[str]
        email: ReadOnlyRef[str] 
        age: ReadOnlyRef[int]
        is_active: ReadOnlyRef[bool]
        
        def __call__(self) -> dict[str, Any]: ...

    # 2. 创建原始数据
    user_data = ReactiveDict({
        'name': 'Alice',
        'email': 'alice@example.com',
        'age': 25, 
        'is_active': True
    })

    # 3. 创建只读视图
    user_view = cast(UserViewProtocol, ReadOnlyView(user_data))

    # 4. 只读访问 - 享受完整类型提示和防护
    @effect  
    def watch_user_view() -> None:
        print(f"  👀 View Name: {user_view.name.value}")
        print(f"  👀 View Email: {user_view.email.value}")
        print(f"  👀 View Age: {user_view.age.value}")

    print("📋 初始只读视图:")
    watch_user_view()

    # 5. 验证只读特性
    print("\n🔒 测试只读特性:")
    try:
        user_view.name.value = "Bob"  # type: ignore
    except AttributeError as e:
        print(f"  ✅ 正确阻止了直接修改: {type(e).__name__}")

    # 6. 只能通过原始数据修改
    print("\n📝 通过原始数据修改:")
    user_data.name = "Bob"
    user_data.age = 26
    
    # 7. 获取快照
    print("\n📸 获取数据快照:")
    snapshot = user_view()
    print(f"  📋 快照: {snapshot}")
    
    print("✅ ReadOnlyView 演示完成")


def demo_complex_nested_structure():
    """演示复杂嵌套数据结构"""
    print("\n🌲 复杂嵌套结构演示")
    print("=" * 50)
    
    # 1. 定义嵌套的 Protocol 结构
    class DatabaseConfig(Protocol):
        host: ReadOnlyRef[str]
        port: ReadOnlyRef[int]
        name: ReadOnlyRef[str]

    class ApiConfig(Protocol):  
        base_url: ReadOnlyRef[str]
        timeout: ReadOnlyRef[int]
        retry_count: ReadOnlyRef[int]

    class AppConfig(Protocol):
        database: DatabaseConfig
        api: ApiConfig
        debug_mode: ReadOnlyRef[bool]
        
        def __call__(self) -> dict[str, Any]: ...

    # 2. 创建嵌套数据
    config_data = ReactiveDict({
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'myapp'
        },
        'api': {
            'base_url': 'https://api.example.com',
            'timeout': 30,
            'retry_count': 3
        },
        'debug_mode': False
    })

    # 3. 创建类型化的只读视图
    config_view = cast(AppConfig, ReadOnlyView(config_data))

    # 4. 访问嵌套数据 - 完整类型提示
    @effect
    def watch_config() -> None:
        db_host = config_view.database.host.value
        api_url = config_view.api.base_url.value  
        debug = config_view.debug_mode.value
        
        print(f"  🗄️ Database: {db_host}:{config_view.database.port.value}")
        print(f"  🌐 API: {api_url}")
        print(f"  🐛 Debug: {debug}")

    print("📋 初始配置:")
    watch_config()

    # 5. 修改原始数据触发变更
    print("\n📝 更新配置:")
    config_data.database.host = 'production-db'
    config_data.api.timeout = 60
    config_data.debug_mode = True
    
    print("✅ 复杂嵌套结构演示完成")


def demo_mixed_usage_pattern():
    """演示混合使用模式"""
    print("\n🎨 混合使用模式演示")
    print("=" * 50)
    
    # 底层:核心应用状态
    app_state: Ref[str] = Ref("initializing")
    user_count: Ref[int] = Ref(0)

    # 高级:复杂配置管理
    config_data = ReactiveDict({
        'ui': {'theme': 'dark', 'language': 'en'},
        'api': {'timeout': 30, 'retries': 3}
    })

    class ConfigProtocol(Protocol):
        ui: dict[str, str]
        api: dict[str, int]

    config = cast(ConfigProtocol, config_data)

    @effect
    def sync_state() -> None:
        state = app_state.value
        count = user_count.value
        theme = config['ui']['theme']
        timeout = config['api']['timeout']
        print(f"  🎯 App [{state}] Users: {count} | Theme: {theme} | Timeout: {timeout}s")

    print("📋 初始状态:")
    sync_state()
    
    print("\n📝 底层状态变更:")
    app_state.value = "running"
    user_count.value = 42
    
    print("\n📝 配置变更:")
    config['ui']['theme'] = 'light'
    config['api']['timeout'] = 60
    
    print("✅ 混合使用模式演示完成")


async def main():
    """运行所有演示"""
    print("🚀 CogniHub PyEffectRef - 文档功能演示")
    print("=" * 60)
    
    # 底层接口演示
    demo_basic_ref_usage()
    demo_sync_async_threading()
    await demo_async_support()
    demo_executor_configuration()
    
    # 高级接口演示  
    demo_reactive_dict_usage()
    demo_readonly_view_usage()
    demo_complex_nested_structure()
    
    # 混合使用演示
    demo_mixed_usage_pattern()
    
    print("\n" + "=" * 60)
    print("✨ 所有演示完成!")
    print("\n📚 主要特性:")
    print("  🔧 底层接口: Ref[T] + effect - 简单直接,泛型类型")
    print("  🏗️ 高级接口: ReactiveDict + ReadOnlyView - 复杂结构,Protocol类型")
    print("  ⚡ 执行模式: 同步/异步/多线程,可配置执行器")
    print("  🔒 线程安全: 内部锁机制,上下文隔离")
    print("  🎯 类型提示: 完整 TypeScript 风格类型支持")


if __name__ == "__main__":
    asyncio.run(main())
