#!/usr/bin/env python3
"""
ReactiveDict 基础示例

演示 ReactiveDict 的基本使用方法,包括:
- 创建和使用 ReactiveDict
- 响应式数据访问
- 与 Effect 的配合使用
- 基本的字典操作
"""
import sys
import os
from typing import  List, TypedDict

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognihub_pyeffectref import ReactiveDict, effect


# 定义类型化字典结构
class UserData(TypedDict):
    name: str
    age: int
    email: str
    active: bool


class AppSettings(TypedDict):
    theme: str
    language: str
    notifications_enabled: bool
    auto_save: bool


def basic_reactive_dict_usage() -> None:
    """演示 ReactiveDict 的基本使用方法"""
    print("📚 基础 ReactiveDict 使用示例")
    print("=" * 50)
    
    # 创建一个 ReactiveDict
    user_data = ReactiveDict({
        'name': "张三",
        'age': 25,
        'email': "zhangsan@example.com",
        'active': True
    })
    
    print("✅ 创建并初始化了 ReactiveDict")
    print(f"📊 初始数据: {dict(user_data.items())}")
    
    # 访问数据
    print(f"\n👤 用户姓名: {user_data['name']}")
    print(f"🎂 用户年龄: {user_data['age']}")
    print(f"📧 用户邮箱: {user_data['email']}")
    print(f"✅ 是否活跃: {user_data['active']}")
    
    # 修改数据
    print("\n🔄 修改用户数据...")
    user_data['name'] = "李四"
    user_data['age'] = 30
    user_data['city'] = "北京"  # 添加新字段
    
    print(f"📊 修改后的数据: {dict(user_data.items())}")
    
    # 删除数据
    print("\n🗑️  删除 email 字段...")
    if 'email' in user_data:
        del user_data['email']
    
    print(f"📊 删除后的数据: {dict(user_data.items())}")


def reactive_dict_with_effects() -> None:
    """演示 ReactiveDict 与 Effect 的配合使用"""
    print("\n⚡ ReactiveDict + Effect 示例")
    print("=" * 50)
    
    # 创建应用设置的响应式字典
    settings = ReactiveDict({
        'theme': 'light',
        'language': 'zh-CN',
        'notifications_enabled': True,
        'auto_save': False
    })

    # 记录变化历史
    changes_log: List[str] = []
    
    # 创建一个监视设置变化的 Effect
    @effect
    def settings_monitor() -> None:
        """监视设置变化的 Effect"""
        theme = settings['theme']
        language = settings['language']
        notifications = settings['notifications_enabled']
        auto_save = settings['auto_save']
        
        change_msg = f"当前设置: 主题={theme}, 语言={language}, 通知={notifications}, 自动保存={auto_save}"
        print(f"  ⚙️  {change_msg}")
        changes_log.append(change_msg)
    
    # 触发初始执行
    settings_monitor()
    print("✅ 已创建设置监视 Effect")
    
    # 修改设置,观察 Effect 的自动响应
    print("\n🎨 更改主题:")
    settings['theme'] = 'dark'
    
    print("\n🌍 更改语言:")
    settings['language'] = 'en-US'
    
    print("\n🔔 启用自动保存:")
    settings['auto_save'] = True
    
    print("\n🔕 禁用通知:")
    settings['notifications_enabled'] = False
    
    print(f"\n📊 总共记录了 {len(changes_log)} 次设置状态")


def product_price_calculator_example() -> None:
    """演示用 ReactiveDict 和 Effect 计算产品价格"""
    print("\n💰 产品价格计算示例")
    print("=" * 50)
    
    # 创建产品信息的响应式字典
    product = ReactiveDict({
        'name': "笔记本电脑",
        'price': 5999.0,
        'discount': 0.0,  # 折扣率
        'tax_rate': 0.13  # 税率
    })
    
    # 创建一个计算最终价格的 Effect
    @effect
    def calculate_final_price() -> None:
        """计算最终价格的 Effect"""
        base_price = product['price']
        discount = product['discount']
        tax_rate = product['tax_rate']
        
        # 计算折后价格
        discounted_price = base_price * (1 - discount)
        
        # 计算含税最终价格
        final_price = discounted_price * (1 + tax_rate)
        
        print(f"  💰 产品: {product['name']}")
        print(f"      原价: ¥{base_price:.2f}")
        print(f"      折扣: {discount * 100:.1f}%")
        print(f"      税率: {tax_rate * 100:.1f}%")
        print(f"      最终价格: ¥{final_price:.2f}")
        print()
    
    # 触发初始计算
    calculate_final_price()
    print("✅ 创建了价格计算 Effect")
    
    # 修改产品信息,观察 Effect 的自动重新计算
    print("🏷️  应用 20% 折扣:")
    product['discount'] = 0.2
    
    print("💸 降低基础价格:")
    product['price'] = 4999.0
    
    print("📈 调整税率:")
    product['tax_rate'] = 0.15
    
    print("🏷️  更换产品:")
    product['name'] = "台式电脑"
    product['price'] = 3999.0
    product['discount'] = 0.1


def nested_reactive_dict_example() -> None:
    """演示嵌套的 ReactiveDict 使用"""
    print("\n🔧 嵌套 ReactiveDict 示例")
    print("=" * 50)
    
    # 创建用户配置文件的响应式字典
    user_profile = ReactiveDict({
        'personal': {
            'name': '王五',
            'age': 28,
            'city': '上海'
        },
        'preferences': {
            'theme': 'dark',
            'language': 'zh-CN',
            'timezone': 'Asia/Shanghai'
        },
        'security': {
            'two_factor_enabled': False,
            'password_last_changed': '2024-01-15'
        }
    })
    
    print("✅ 创建了嵌套的用户配置文件")
    print("📊 初始配置:")
    for section, data in user_profile.items():
        print(f"  {section}: {data}")
    
    # 创建一个监控配置变化的 Effect
    @effect
    def profile_monitor() -> None:
        """配置文件监控 Effect"""
        personal = user_profile['personal']
        preferences = user_profile['preferences']
        security = user_profile['security']
        
        print(f"  🔄 配置文件状态:")
        print(f"    个人信息: {personal}")
        print(f"    偏好设置: {preferences}")
        print(f"    安全设置: {security}")
    
    print("\n📡 创建配置监控 Effect:")
    profile_monitor()
    
    # 修改嵌套数据
    print("\n🔄 更新个人信息:")
    user_profile['personal'] = {
        'name': '王五',
        'age': 29,  # 年龄增长
        'city': '深圳',  # 迁移城市
        'phone': '13800138000'  # 新增电话
    }
    
    print("\n🔄 更新偏好设置:")
    user_profile['preferences'] = {
        'theme': 'light',  # 改变主题
        'language': 'en-US',  # 改变语言
        'timezone': 'Asia/Shanghai',
        'font_size': 'medium'  # 新增字体大小
    }


def shopping_cart_example() -> None:
    """演示购物车的 ReactiveDict 操作"""
    print("\n🛠️  购物车操作示例")
    print("=" * 50)
    
    # 创建一个购物车的响应式字典
    shopping_cart = ReactiveDict({})  # 空字典开始
    
    # 记录操作历史
    operations: List[str] = []
    
    # 创建购物车监控 Effect
    @effect
    def cart_monitor() -> None:
        """购物车监控 Effect"""
        if len(shopping_cart) == 0:
            status = "购物车为空"
        else:
            items = []
            total_items = 0
            for item, quantity in shopping_cart.items():
                items.append(f"{item}: {quantity}")
                total_items += quantity
            status = f"购物车 ({len(shopping_cart)} 种商品, 共 {total_items} 件): {', '.join(items)}"
        
        print(f"  🛒 {status}")
        operations.append(status)
    
    print("✅ 创建了购物车监控 Effect")
    cart_monitor()  # 初始状态
    
    # 添加商品
    print("\n🛍️  添加商品到购物车:")
    shopping_cart['苹果'] = 3
    shopping_cart['香蕉'] = 2
    shopping_cart['橙子'] = 5
    
    # 更新商品数量
    print("\n📈 增加苹果数量:")
    shopping_cart['苹果'] = 5
    
    print("\n📉 减少香蕉数量:")
    shopping_cart['香蕉'] = 1
    
    # 删除商品
    print("\n🗑️  移除橙子:")
    del shopping_cart['橙子']
    
    # 清空购物车
    print("\n🧹 清空购物车:")
    shopping_cart.clear()
    
    print(f"\n📊 总共记录了 {len(operations)} 次购物车状态")


def reactive_dict_data_binding_example() -> None:
    """演示数据绑定场景"""
    print("\n🔗 数据绑定示例")
    print("=" * 50)
    
    # 模拟表单数据
    form_data = ReactiveDict({
        'username': '',
        'email': '',
        'age': 0,
        'terms_accepted': False
    })
    
    # 表单验证状态
    validation_status = ReactiveDict({
        'username_valid': False,
        'email_valid': False,
        'age_valid': False,
        'form_valid': False
    })
    
    # 创建表单验证 Effect
    @effect
    def form_validator() -> None:
        """表单验证 Effect"""
        username = form_data['username']
        email = form_data['email']
        age = form_data['age']
        terms = form_data['terms_accepted']
        
        # 验证规则
        username_valid = len(username) >= 3
        email_valid = '@' in email and '.' in email
        age_valid = 18 <= age <= 120
        
        # 更新验证状态
        validation_status['username_valid'] = username_valid
        validation_status['email_valid'] = email_valid
        validation_status['age_valid'] = age_valid
        validation_status['form_valid'] = username_valid and email_valid and age_valid and terms
        
        print(f"  📝 表单验证状态:")
        print(f"    用户名 ({username}): {'✅' if username_valid else '❌'}")
        print(f"    邮箱 ({email}): {'✅' if email_valid else '❌'}")
        print(f"    年龄 ({age}): {'✅' if age_valid else '❌'}")
        print(f"    条款接受: {'✅' if terms else '❌'}")
        print(f"    表单整体: {'✅ 有效' if validation_status['form_valid'] else '❌ 无效'}")
        print()
    
    print("✅ 创建了表单验证 Effect")
    form_validator()  # 初始验证
    
    # 模拟用户输入
    print("👤 用户开始填写表单:")
    form_data['username'] = 'alice'
    
    print("📧 输入邮箱:")
    form_data['email'] = 'alice@example.com'
    
    print("🎂 输入年龄:")
    form_data['age'] = 25
    
    print("📋 接受条款:")
    form_data['terms_accepted'] = True
    
    print(f"🎉 表单最终状态: {'提交就绪' if validation_status['form_valid'] else '需要修正'}")


def main() -> None:
    """主函数 - 运行所有示例"""
    print("🚀 CogniHub PyEffectRef - ReactiveDict 基础示例")
    print("=" * 80)
    
    try:
        basic_reactive_dict_usage()
        reactive_dict_with_effects()
        product_price_calculator_example()
        nested_reactive_dict_example()
        shopping_cart_example()
        reactive_dict_data_binding_example()
        
        print("\n" + "=" * 80)
        print("✨ 所有示例运行完成！")
        print("\n💡 关键要点:")
        print("   1. ReactiveDict 提供响应式的字典功能")
        print("   2. 与 Effect 完美配合,实现自动响应")
        print("   3. 支持嵌套数据结构")
        print("   4. 支持所有标准字典操作")
        print("   5. 适用于复杂的状态管理和数据绑定场景")
        
    except Exception as e:
        print(f"❌ 运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
