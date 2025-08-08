#!/usr/bin/env python3
"""
基础 Ref 示例

演示 Ref 的基本使用方法,包括:
- 创建和使用 Ref
- 订阅 Ref 的变化
- 基本的响应式编程概念
"""
import sys
import os
from typing import List, Any

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognihub_pyeffectref import Ref


def basic_ref_usage() -> None:
    """演示 Ref 的基本使用方法"""
    print("🔍 基础 Ref 使用示例")
    print("=" * 50)
    
    # 1. 创建一个 Ref
    counter: Ref[int] = Ref(0)
    print(f"初始值: {counter.value}")
    
    # 2. 修改 Ref 的值
    counter.value = 10
    print(f"修改后的值: {counter.value}")
    
    # 3. 创建不同类型的 Ref
    name_ref: Ref[str] = Ref("Alice")
    is_active_ref: Ref[bool] = Ref(True)
    
    print(f"字符串 Ref: {name_ref.value}")
    print(f"布尔 Ref: {is_active_ref.value}")


def ref_subscription_example() -> None:
    """演示 Ref 订阅功能"""
    print("\n📡 Ref 订阅示例")
    print("=" * 50)
    
    # 创建一个 Ref
    temperature: Ref[float] = Ref(20.0)
    
    # 用于存储变化记录的列表
    change_log: List[str] = []
    
    # 定义订阅函数
    def on_temperature_change(new_value: float, old_value: float) -> None:
        """温度变化时的回调函数"""
        change_message = f"温度从 {old_value}°C 变化到 {new_value}°C"
        print(f"  📊 {change_message}")
        change_log.append(change_message)
    
    # 订阅温度变化
    temperature.subscribe(on_temperature_change)
    print("✅ 已订阅温度变化")
    
    # 修改温度值,观察订阅效果
    print("\n🌡️ 开始修改温度...")
    temperature.value = 25.0
    temperature.value = 30.0
    temperature.value = 18.5
    
    # 显示变化记录
    print(f"\n📝 总共记录了 {len(change_log)} 次变化")


def multiple_subscribers_example() -> None:
    """演示多个订阅者的场景"""
    print("\n👥 多订阅者示例")
    print("=" * 50)
    
    # 创建一个表示用户状态的 Ref
    user_status: Ref[str] = Ref("offline")
    
    # 定义多个订阅者
    def logger(new_status: str, old_status: str) -> None:
        """日志记录器"""
        print(f"  📋 [Logger] 用户状态: {old_status} → {new_status}")
    
    def notifier(new_status: str, old_status: str) -> None:
        """通知系统"""
        if new_status == "online":
            print(f"  📢 [Notifier] 用户已上线！")
        elif new_status == "offline":
            print(f"  📢 [Notifier] 用户已下线.")
    
    def analytics(new_status: str, old_status: str) -> None:
        """分析系统"""
        print(f"  📈 [Analytics] 状态变化已记录到分析系统")
    
    # 订阅状态变化
    user_status.subscribe(logger)
    user_status.subscribe(notifier)
    user_status.subscribe(analytics)
    
    print("✅ 已设置3个订阅者(Logger、Notifier、Analytics)")
    
    # 模拟状态变化
    print("\n👤 模拟用户状态变化...")
    user_status.value = "online"
    user_status.value = "busy" 
    user_status.value = "offline"


def unsubscribe_example() -> None:
    """演示取消订阅的功能"""
    print("\n🚫 取消订阅示例")
    print("=" * 50)
    
    score: Ref[int] = Ref(0)
    
    # 定义一个临时的订阅函数
    def temporary_subscriber(new_score: int, old_score: int) -> None:
        """临时订阅者"""
        print(f"  🎯 [临时订阅] 分数变化: {old_score} → {new_score}")
    
    # 定义一个持久的订阅函数
    def permanent_subscriber(new_score: int, old_score: int) -> None:
        """持久订阅者"""
        print(f"  ⭐ [持久订阅] 分数: {new_score}")
    
    # 订阅
    score.subscribe(temporary_subscriber)
    score.subscribe(permanent_subscriber)
    
    print("✅ 添加了临时和持久两个订阅者")
    
    # 第一次修改 - 两个订阅者都会响应
    print("\n🎲 第一次修改分数:")
    score.value = 10
    
    # 取消临时订阅者
    score.unsubscribe(temporary_subscriber)
    print("\n❌ 已取消临时订阅者")
    
    # 第二次修改 - 只有持久订阅者会响应
    print("\n🎲 第二次修改分数:")
    score.value = 20


def ref_with_complex_types() -> None:
    """演示 Ref 与复杂类型的使用"""
    print("\n🔧 复杂类型 Ref 示例")
    print("=" * 50)
    
    from typing import Dict
    
    # 字典类型的 Ref
    user_data: Ref[Dict[str, Any]] = Ref({
        "name": "Alice",
        "age": 25,
        "active": True
    })
    
    def on_user_data_change(new_data: Dict[str, Any], old_data: Dict[str, Any]) -> None:
        """用户数据变化回调"""
        print(f"  👤 用户数据已更新:")
        print(f"     旧数据: {old_data}")
        print(f"     新数据: {new_data}")
    
    user_data.subscribe(on_user_data_change)
    
    print("📝 初始用户数据:", user_data.value)
    
    # 修改整个字典
    print("\n🔄 更新用户数据...")
    user_data.value = {
        "name": "Alice Smith",
        "age": 26,
        "active": True,
        "email": "alice@example.com"
    }
    
    # 列表类型的 Ref
    todo_list: Ref[List[str]] = Ref(["学习 Python", "写代码"])
    
    def on_todo_change(new_todos: List[str], old_todos: List[str]) -> None:
        """待办事项变化回调"""
        print(f"  ✅ 待办事项已更新:")
        print(f"     之前: {old_todos}")
        print(f"     现在: {new_todos}")
    
    todo_list.subscribe(on_todo_change)
    
    print(f"\n📋 初始待办事项: {todo_list.value}")
    
    # 修改列表
    print("\n➕ 添加新的待办事项...")
    todo_list.value = todo_list.value + ["阅读文档", "写测试"]


def main() -> None:
    """主函数 - 运行所有示例"""
    print("🚀 CogniHub PyEffectRef - Ref 基础示例")
    print("=" * 80)
    
    try:
        basic_ref_usage()
        ref_subscription_example()
        multiple_subscribers_example()
        unsubscribe_example()
        ref_with_complex_types()
        
        print("\n" + "=" * 80)
        print("✨ 所有示例运行完成！")
        print("\n💡 关键要点:")
        print("   1. Ref 是响应式编程的基础")
        print("   2. 可以订阅 Ref 的变化")
        print("   3. 支持多个订阅者")
        print("   4. 可以取消订阅")
        print("   5. 支持任何类型的数据")
        
    except Exception as e:
        print(f"❌ 运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
