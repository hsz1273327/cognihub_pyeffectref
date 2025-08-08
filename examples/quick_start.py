#!/usr/bin/env python3
"""
CogniHub PyEffectRef - 快速入门示例

这个文件展示了库的核心功能和推荐用法:
- 🔧 底层接口:适合简单状态管理
- 🏗️ 高级接口:适合复杂数据结构
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognihub_pyeffectref import Ref, effect, ReactiveDict, ReadOnlyView, ReadOnlyRef
from typing import Protocol, TypedDict, cast, Any


def quick_start_basic():
    """🔧 底层接口快速入门 - 简单直接"""
    print("🔧 底层接口 - 简单状态管理")
    print("-" * 40)
    
    # 1. 创建响应式数据 (直接使用泛型指定类型)
    counter: Ref[int] = Ref(0)
    username: Ref[str] = Ref("Guest")
    
    # 2. 创建响应式副作用
    @effect
    def display_status() -> None:
        print(f"👤 {username.value} | 📊 Count: {counter.value}")
    
    # 3. 初始执行建立依赖
    display_status()
    
    # 4. 修改数据自动触发更新
    print("📝 更新数据...")
    username.value = "Alice"
    counter.value = 5
    
    print("✅ 底层接口演示完成\n")


def quick_start_advanced():
    """🏗️ 高级接口快速入门 - 复杂结构"""
    print("🏗️ 高级接口 - 复杂数据结构")
    print("-" * 40)
    
    # 1. 定义数据结构 (使用 TypedDict)
    class UserProfile(TypedDict):
        name: str
        email: str
        preferences: dict[str, Any]
    
    # 2. 创建响应式字典
    user_data = ReactiveDict({
        'name': 'Alice',
        'email': 'alice@example.com',
        'preferences': {
            'theme': 'dark',
            'notifications': True
        }
    })
    
    # 3. 类型转换获得完整类型提示
    user: UserProfile = cast(UserProfile, user_data)
    
    # 4. 创建响应式副作用
    @effect
    def display_user_info() -> None:
        theme = user['preferences']['theme']
        print(f"👤 {user['name']} | 📧 {user['email']} | 🎨 {theme}")
    
    # 5. 初始执行
    display_user_info()
    
    # 6. 修改嵌套数据
    print("📝 更新用户偏好...")
    user['preferences']['theme'] = 'light'
    user['name'] = 'Alice Smith'
    
    print("✅ 高级接口演示完成\n")


def quick_start_readonly():
    """👁️ 只读视图快速入门 - 数据保护"""
    print("👁️ 只读视图 - 数据访问保护") 
    print("-" * 40)
    
    # 1. 定义只读视图结构 (使用 Protocol)
    class ConfigView(Protocol):
        app_name: ReadOnlyRef[str]
        version: ReadOnlyRef[str]
        debug: ReadOnlyRef[bool]
        
        def __call__(self) -> dict[str, Any]: ...
    
    # 2. 创建原始数据
    app_config = ReactiveDict({
        'app_name': 'MyApp',
        'version': '1.0.0',
        'debug': False
    })
    
    # 3. 创建只读视图
    config_view = cast(ConfigView, ReadOnlyView(app_config))
    
    # 4. 安全的只读访问
    @effect
    def display_config() -> None:
        name = config_view.app_name.value
        version = config_view.version.value
        debug = config_view.debug.value
        print(f"🚀 {name} v{version} | 🐛 Debug: {debug}")
    
    # 5. 初始显示
    display_config()
    
    # 6. 只能通过原始数据修改
    print("📝 更新配置...")
    app_config.version = '1.1.0'
    app_config.debug = True
    
    # 7. 验证只读保护
    print("🔒 测试只读保护:")
    try:
        config_view.app_name.value = "HackedApp"  # type: ignore
    except AttributeError:
        print("✅ 只读保护生效,无法直接修改")
    
    print("✅ 只读视图演示完成\n")


def main():
    """运行快速入门示例"""
    print("🚀 CogniHub PyEffectRef - 快速入门")
    print("=" * 50)
    
    quick_start_basic()
    quick_start_advanced()
    quick_start_readonly()
    
    print("=" * 50)
    print("🎯 使用建议:")
    print("  💡 简单状态 → 使用 Ref[T] + effect")
    print("  💡 复杂数据 → 使用 ReactiveDict + TypedDict") 
    print("  💡 只读访问 → 使用 ReadOnlyView + Protocol")
    print("  💡 查看完整文档: README.md")


if __name__ == "__main__":
    main()
