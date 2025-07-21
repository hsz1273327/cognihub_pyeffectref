#!/usr/bin/env python3
"""ReactiveDict 示例演示"""

import asyncio
import json
from cognihub_pyeffectref import Ref, ReactiveDict, effect


from typing import Any


def demo_basic_usage() -> None:
    """基本用法演示"""
    print("=== ReactiveDict 基本用法演示 ===")
    
    # 从字典创建
    data = {
        "user": {
            "name": "Alice",
            "age": 30,
            "preferences": {
                "theme": "dark",
                "language": "zh-cn"
            }
        },
        "settings": {
            "debug": False,
            "max_connections": 100
        }
    }
    
    rd = ReactiveDict(data)
    
    # 点语法访问
    print(f"用户名: {rd.user.name}")
    print(f"年龄: {rd.user.age}")
    print(f"主题: {rd.user.preferences.theme}")
    
    # 字典风格访问
    print(f"调试模式: {rd['settings']['debug']}")
    print(f"最大连接数: {rd.settings['max_connections']}")
    
    # 修改值
    rd.user.name = "Bob"
    rd.user.preferences.theme = "light"
    rd.settings.debug = True
    
    print(f"修改后用户名: {rd.user.name}")
    print(f"修改后主题: {rd.user.preferences.theme}")
    print(f"修改后调试模式: {rd.settings.debug}")


def demo_json_integration():
    """JSON 集成演示"""
    print("\n=== JSON 集成演示 ===")
    
    json_data = '''
    {
        "app": {
            "name": "MyApp",
            "version": "1.0.0",
            "config": {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "name": "mydb"
                },
                "cache": {
                    "enabled": true,
                    "ttl": 3600
                }
            }
        },
        "features": {
            "authentication": true,
            "logging": true,
            "monitoring": false
        }
    }
    '''
    
    # 从JSON创建
    rd = ReactiveDict.from_json(json_data)
    
    print(f"应用名称: {rd.app.name}")
    print(f"数据库配置: {rd.app.config.database.host}:{rd.app.config.database.port}")
    print(f"缓存启用: {rd.app.config.cache.enabled}")
    
    # 修改配置
    rd.app.config.database.host = "production.db.com"
    rd.features.monitoring = True
    
    # 转换回字典
    result = rd.to_dict()
    print(f"修改后的配置: {json.dumps(result, indent=2, ensure_ascii=False)}")


def demo_reactive_effects():
    """响应式效果演示"""
    print("\n=== 响应式效果演示 ===")
    
    # 创建状态管理
    state = ReactiveDict({
        "counter": 0,
        "user": {
            "name": "Alice",
            "online": False
        },
        "stats": {
            "clicks": 0,
            "visits": 0
        }
    })
    
    # Effect 1: 监听计数器变化
    @effect
    def track_counter():
        print(f"计数器更新: {state.counter}")
    
    # Effect 2: 监听用户状态
    @effect
    def track_user_status():
        status = "在线" if state.user.online else "离线"
        print(f"用户 {state.user.name} 状态: {status}")
    
    # Effect 3: 计算总活动数
    @effect
    def track_total_activity():
        total = state.stats.clicks + state.stats.visits
        print(f"总活动数: {total}")
    
    # 初始化effects
    track_counter()
    track_user_status()
    track_total_activity()
    
    print("\n开始修改状态...")
    
    # 修改计数器
    state.counter = 5
    state.counter = 10
    
    # 修改用户状态
    state.user.online = True
    state.user.name = "Bob"
    
    # 修改统计数据
    state.stats.clicks = 100
    state.stats.visits = 50


def demo_raw_ref_subscription():
    """原始Ref订阅演示"""
    print("\n=== 原始Ref订阅演示 ===")
    
    config = ReactiveDict({
        "server": {
            "host": "localhost",
            "port": 8080,
            "ssl": False
        },
        "database": {
            "url": "sqlite:///app.db",
            "pool_size": 10
        }
    })
    
    # 获取特定字段的Ref并订阅
    port_ref = config.get_raw_ref("server.port")
    ssl_ref = config.get_raw_ref("server.ssl")
    
    def on_port_change(new_port, old_port):
        print(f"服务器端口变更: {old_port} -> {new_port}")
        if new_port == 443:
            print("  检测到HTTPS端口，建议启用SSL")
    
    def on_ssl_change(new_ssl, old_ssl):
        status = "启用" if new_ssl else "禁用"
        print(f"SSL状态变更: {status}")
    
    # 订阅变化
    port_ref.subscribe(on_port_change)
    ssl_ref.subscribe(on_ssl_change)
    
    # 修改配置
    print("修改服务器配置...")
    config.server.port = 3000
    config.server.port = 443
    config.server.ssl = True


async def demo_async_reactive():
    """异步响应式演示"""
    print("\n=== 异步响应式演示 ===")
    
    app_state = ReactiveDict({
        "loading": False,
        "data": None,
        "error": None,
        "progress": 0
    })
    
    # 异步effect监听加载状态
    @effect
    async def handle_loading_state():
        if app_state.loading:
            print("开始加载数据...")
            await asyncio.sleep(0.1)  # 模拟异步操作
        else:
            print("数据加载完成")
    
    # 异步effect监听进度
    @effect
    async def handle_progress():
        if app_state.progress > 0:
            print(f"加载进度: {app_state.progress}%")
            await asyncio.sleep(0.05)
    
    # 初始化
    await handle_loading_state()
    
    # 模拟数据加载过程
    app_state.loading = True
    await asyncio.sleep(0.2)
    
    app_state.progress = 25
    await asyncio.sleep(0.1)
    
    app_state.progress = 50
    await asyncio.sleep(0.1)
    
    app_state.progress = 75
    await asyncio.sleep(0.1)
    
    app_state.progress = 100
    app_state.data = {"result": "success", "count": 42}
    app_state.loading = False
    
    await asyncio.sleep(0.2)


def demo_complex_operations() -> None:
    """复杂操作演示"""
    print("\n=== 复杂操作演示 ===")
    
    # 模拟电商购物车
    cart = ReactiveDict({
        "cart_items": {},  # 重命名避免与dict.items()冲突
        "user": {"id": 1, "name": "Alice"},
        "totals": {"subtotal": 0, "tax": 0, "total": 0}
    })
    
    # 添加商品的函数
    def add_item(item_id: str, name: str, price: float, quantity: int = 1) -> None:
        cart.cart_items[item_id] = ReactiveDict({
            "name": name,
            "price": price,
            "quantity": quantity,
            "subtotal": price * quantity
        })
        update_totals()
    
    def update_totals() -> None:
        subtotal = 0
        items_dict = cart.to_dict()["cart_items"]
        for item in items_dict.values():
            subtotal += item.get("subtotal", 0)
        
        tax = subtotal * 0.1  # 10% 税率
        total = subtotal + tax
        
        cart.totals.subtotal = round(subtotal, 2)
        cart.totals.tax = round(tax, 2)
        cart.totals.total = round(total, 2)
    
    # 监听总计变化
    @effect
    def display_cart_total() -> None:
        print(f"购物车总计: ¥{cart.totals.total} (含税 ¥{cart.totals.tax})")
    
    display_cart_total()
    
    # 添加商品
    print("添加商品到购物车...")
    add_item("book1", "Python编程", 89.90, 2)
    add_item("laptop", "编程笔记本", 5999.00, 1)
    add_item("mouse", "无线鼠标", 199.00, 1)
    
    # 修改数量
    cart.cart_items.book1.quantity = 3
    cart.cart_items.book1.subtotal = cart.cart_items.book1.price * cart.cart_items.book1.quantity
    update_totals()
    
    print(f"最终购物车内容: {json.dumps(cart.to_dict(), indent=2, ensure_ascii=False)}")


def main():
    """主函数"""
    demo_basic_usage()
    demo_json_integration()
    demo_reactive_effects()
    demo_raw_ref_subscription()
    demo_complex_operations()
    
    # 运行异步演示
    print("\n运行异步演示...")
    asyncio.run(demo_async_reactive())
    
    print("\n演示完成！")


if __name__ == "__main__":
    main()
