#!/usr/bin/env python3
"""
Effect 基础示例

演示 Effect 的基本使用方法，包括：
- 创建和使用 Effect
- Effect 的自动执行和依赖追踪
- Effect 的清理和取消
- 副作用处理的最佳实践
"""
import sys
import os
from typing import List, Optional, Callable

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognihub_pyeffectref import Ref, effect


def basic_effect_usage() -> None:
    """演示 Effect 的基本使用方法"""
    print("⚡ 基础 Effect 使用示例")
    print("=" * 50)
    
    # 创建一些响应式数据
    count: Ref[int] = Ref(0)
    multiplier: Ref[int] = Ref(2)
    
    # 用于记录 Effect 执行次数
    effect_runs: List[str] = []
    
    # 创建一个 Effect 来计算和显示结果
    @effect
    def compute_and_display() -> None:
        """计算并显示结果的 Effect"""
        result = count.value * multiplier.value
        message = f"计算结果: {count.value} × {multiplier.value} = {result}"
        print(f"  📊 {message}")
        effect_runs.append(message)
    
    # 触发初始执行
    compute_and_display()
    print("✅ 创建了 Effect，会自动执行一次")
    
    # 修改依赖的值，Effect 会自动重新执行
    print("\n🔄 修改 count 值:")
    count.value = 5
    
    print("\n🔄 修改 multiplier 值:")
    multiplier.value = 3
    
    print("\n🔄 同时修改两个值:")
    count.value = 10
    multiplier.value = 4
    
    print(f"\n📈 Effect 总共执行了 {len(effect_runs)} 次")


def effect_dependency_tracking() -> None:
    """演示 Effect 的依赖追踪"""
    print("\n🔍 Effect 依赖追踪示例")
    print("=" * 50)
    
    # 创建多个响应式数据
    first_name: Ref[str] = Ref("张")
    last_name: Ref[str] = Ref("三")
    age: Ref[int] = Ref(25)
    show_age: Ref[bool] = Ref(True)
    
    # Effect 只会依赖它实际访问的 Ref
    @effect
    def display_user_info() -> None:
        """显示用户信息的 Effect"""
        full_name = first_name.value + last_name.value
        
        if show_age.value:
            info = f"{full_name}，{age.value}岁"
        else:
            info = full_name
        
        print(f"  👤 用户信息: {info}")
    
    # 触发初始执行
    display_user_info()
    print("✅ 创建了用户信息显示 Effect")
    
    # 测试不同的修改对 Effect 的影响
    print("\n🔄 修改 first_name (应该触发 Effect):")
    first_name.value = "李"
    
    print("\n🔄 修改 age (应该触发 Effect，因为 show_age 是 True):")
    age.value = 30
    
    print("\n🔄 将 show_age 设为 False:")
    show_age.value = False
    
    print("\n🔄 再次修改 age (不应该触发 Effect，因为 show_age 是 False):")
    age.value = 35
    print("  ⚠️  注意：由于 show_age 为 False，age 不再是依赖项")
    
    print("\n🔄 修改 last_name (仍然会触发 Effect):")
    last_name.value = "四"


def effect_cleanup_example() -> None:
    """演示 Effect 的清理功能"""
    print("\n🧹 Effect 清理示例")
    print("=" * 50)
    
    # 模拟一个定时器场景
    timer_active: Ref[bool] = Ref(False)
    timer_interval: Ref[float] = Ref(1.0)
    
    # 用于存储定时器状态
    timer_status: List[str] = []
    
    @effect
    def timer_effect() -> Optional[Callable[[], None]]:
        """定时器 Effect，返回清理函数"""
        if not timer_active.value:
            print("  ⏹️  定时器已停止")
            return None
        
        print(f"  ⏰ 启动定时器，间隔: {timer_interval.value}秒")
        timer_status.append("started")
        
        # 返回清理函数
        def cleanup() -> None:
            print("  🧹 清理定时器资源")
            timer_status.append("cleaned")
        
        return cleanup
    
    # 触发初始执行
    timer_effect()
    print("✅ 创建了定时器 Effect")
    
    # 启动定时器
    print("\n▶️  启动定时器:")
    timer_active.value = True
    
    # 修改间隔（会触发清理和重新创建）
    print("\n🔄 修改定时器间隔:")
    timer_interval.value = 0.5
    
    # 停止定时器
    print("\n⏹️  停止定时器:")
    timer_active.value = False
    
    print(f"\n📊 定时器状态记录: {timer_status}")


def conditional_effect_example() -> None:
    """演示条件性 Effect"""
    print("\n🔀 条件性 Effect 示例")
    print("=" * 50)
    
    # 用户偏好设置
    theme: Ref[str] = Ref("light")
    notifications_enabled: Ref[bool] = Ref(True)
    user_logged_in: Ref[bool] = Ref(False)
    
    # 记录应用的各种状态更新
    app_updates: List[str] = []
    
    @effect
    def app_state_effect() -> None:
        """应用状态 Effect"""
        if not user_logged_in.value:
            update = "用户未登录 - 显示登录页面"
            print(f"  🔐 {update}")
            app_updates.append(update)
            return
        
        # 用户已登录时的处理
        theme_update = f"应用主题: {theme.value}"
        print(f"  🎨 {theme_update}")
        app_updates.append(theme_update)
        
        if notifications_enabled.value:
            notification_update = "通知已启用"
            print(f"  🔔 {notification_update}")
            app_updates.append(notification_update)
        else:
            notification_update = "通知已禁用"
            print(f"  🔕 {notification_update}")
            app_updates.append(notification_update)
    
    # 触发初始执行
    app_state_effect()
    print("✅ 创建了应用状态 Effect")
    
    # 模拟用户登录
    print("\n👤 用户登录:")
    user_logged_in.value = True
    
    # 修改主题
    print("\n🌙 切换到暗色主题:")
    theme.value = "dark"
    
    # 禁用通知
    print("\n🔕 禁用通知:")
    notifications_enabled.value = False
    
    # 用户登出
    print("\n👋 用户登出:")
    user_logged_in.value = False
    
    print(f"\n📝 应用状态更新记录（共 {len(app_updates)} 次）:")
    for i, update in enumerate(app_updates, 1):
        print(f"   {i}. {update}")


def effect_with_error_handling() -> None:
    """演示 Effect 中的错误处理"""
    print("\n⚠️  Effect 错误处理示例")
    print("=" * 50)
    
    # 模拟可能出错的数据
    dividend: Ref[int] = Ref(10)
    divisor: Ref[int] = Ref(2)
    
    error_count: int = 0
    
    @effect
    def safe_division_effect() -> None:
        """安全除法 Effect"""
        nonlocal error_count
        
        try:
            if divisor.value == 0:
                raise ValueError("除数不能为零")
            
            result = dividend.value / divisor.value
            print(f"  ✅ 计算结果: {dividend.value} ÷ {divisor.value} = {result:.2f}")
        
        except ValueError as e:
            error_count += 1
            print(f"  ❌ 计算错误: {e}")
        
        except Exception as e:
            error_count += 1
            print(f"  ❌ 未知错误: {e}")
    
    # 触发初始执行
    safe_division_effect()
    print("✅ 创建了安全除法 Effect")
    
    # 正常计算
    print("\n🔄 修改被除数:")
    dividend.value = 20
    
    # 触发除零错误
    print("\n💥 设置除数为零:")
    divisor.value = 0
    
    # 恢复正常
    print("\n🔄 恢复除数:")
    divisor.value = 5
    
    print(f"\n📊 总计出现 {error_count} 次错误")


def effect_performance_example() -> None:
    """演示 Effect 性能相关的概念"""
    print("\n⚡ Effect 性能示例")
    print("=" * 50)
    
    # 模拟一个计算密集的场景
    base_value: Ref[int] = Ref(1)
    computation_count: int = 0
    
    @effect
    def expensive_computation_effect() -> None:
        """模拟计算密集型 Effect"""
        nonlocal computation_count
        computation_count += 1
        
        # 模拟复杂计算
        result = sum(i * base_value.value for i in range(1000))
        print(f"  🔢 复杂计算结果: {result} (执行第 {computation_count} 次)")
    
    # 触发初始执行
    expensive_computation_effect()
    print("✅ 创建了计算密集型 Effect")
    
    # 快速连续修改值
    print("\n⚡ 快速连续修改值:")
    for i in range(2, 6):
        print(f"   设置值为 {i}")
        base_value.value = i
        # 注意：每次修改都会立即触发 Effect
    
    print(f"\n📈 计算总共执行了 {computation_count} 次")
    print("💡 在实际应用中，可能需要考虑防抖(debounce)或节流(throttle)技术")


def main() -> None:
    """主函数 - 运行所有示例"""
    print("🚀 CogniHub PyEffectRef - Effect 基础示例")
    print("=" * 80)
    
    try:
        basic_effect_usage()
        effect_dependency_tracking()
        effect_cleanup_example()
        conditional_effect_example()
        effect_with_error_handling()
        effect_performance_example()
        
        print("\n" + "=" * 80)
        print("✨ 所有示例运行完成！")
        print("\n💡 关键要点:")
        print("   1. Effect 会自动追踪依赖的 Ref")
        print("   2. 依赖变化时 Effect 会自动重新执行")
        print("   3. Effect 可以返回清理函数")
        print("   4. 条件逻辑会影响依赖追踪")
        print("   5. 需要考虑错误处理和性能优化")
        
    except Exception as e:
        print(f"❌ 运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
