#!/usr/bin/env python3
"""
ReactiveDict 高级示例

演示 ReactiveDict 的高级用法，包括：
- 复杂的嵌套数据结构
- 计算属性和派生状态
- 条件响应和优化技巧
- 与多个 Effect 的协调使用
"""
import sys
import os
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognihub_pyeffectref import ReactiveDict, effect, Ref


# 定义复杂的类型结构
class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


def advanced_task_management_system() -> None:
    """演示高级任务管理系统"""
    print("📋 高级任务管理系统示例")
    print("=" * 50)
    
    # 创建任务管理系统的响应式数据
    task_system = ReactiveDict({
        'tasks': {'placeholder': 'temp'},  # 临时占位符，稍后替换
        'filters': {
            'status': 'all',
            'priority': 'all',
            'assignee': 'all'
        },
        'ui_state': {
            'current_view': 'list',
            'selected_task': None,
            'sort_by': 'created_at',
            'sort_order': 'desc'
        }
    })
    
    # 清空 tasks，准备添加真实数据
    task_system['tasks'] = {}
    
    # 统计数据
    stats = ReactiveDict({
        'total_tasks': 0,
        'completed_tasks': 0,
        'pending_tasks': 0,
        'in_progress_tasks': 0,
        'completion_rate': 0.0
    })
    
    # 创建统计计算 Effect
    @effect
    def calculate_stats() -> None:
        """计算任务统计数据"""
        tasks = task_system['tasks']
        
        total = len(tasks)
        completed = sum(1 for task in tasks.values() if task['status'] == 'completed')
        pending = sum(1 for task in tasks.values() if task['status'] == 'pending')
        in_progress = sum(1 for task in tasks.values() if task['status'] == 'in_progress')
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        # 更新统计数据
        stats['total_tasks'] = total
        stats['completed_tasks'] = completed
        stats['pending_tasks'] = pending
        stats['in_progress_tasks'] = in_progress
        stats['completion_rate'] = completion_rate
        
        print(f"  📊 任务统计更新:")
        print(f"    总任务: {total}")
        print(f"    已完成: {completed}")
        print(f"    进行中: {in_progress}")
        print(f"    待处理: {pending}")
        print(f"    完成率: {completion_rate:.1f}%")
        print()
    
    # 创建过滤器 Effect
    @effect
    def apply_filters() -> None:
        """应用过滤器"""
        filters = task_system['filters']
        tasks = task_system['tasks']
        
        status_filter = filters['status']
        priority_filter = filters['priority']
        assignee_filter = filters['assignee']
        
        filtered_count = 0
        for task in tasks.values():
            matches = True
            
            if status_filter != 'all' and task['status'] != status_filter:
                matches = False
            
            if priority_filter != 'all' and task['priority'] != int(priority_filter):
                matches = False
                
            if assignee_filter != 'all' and task['assignee'] != assignee_filter:
                matches = False
            
            if matches:
                filtered_count += 1
        
        print(f"  🔍 过滤结果: {filtered_count} 个任务匹配当前过滤条件")
        print(f"    状态过滤: {status_filter}")
        print(f"    优先级过滤: {priority_filter}")
        print(f"    负责人过滤: {assignee_filter}")
    
    print("✅ 创建了任务管理系统")
    
    # 添加初始任务
    print("\n📝 添加初始任务...")
    task_system['tasks'] = {
        'task_1': {
            'id': 'task_1',
            'title': '设计数据库架构',
            'description': '为新项目设计数据库结构',
            'status': 'completed',
            'priority': 3,
            'assignee': '张三',
            'created_at': '2024-01-01',
            'due_date': '2024-01-15',
            'tags': ['database', 'design']
        },
        'task_2': {
            'id': 'task_2', 
            'title': '实现用户认证',
            'description': '实现登录和注册功能',
            'status': 'in_progress',
            'priority': 4,
            'assignee': '李四',
            'created_at': '2024-01-02',
            'due_date': '2024-01-20',
            'tags': ['auth', 'security']
        },
        'task_3': {
            'id': 'task_3',
            'title': '编写API文档',
            'description': '为REST API编写详细文档',
            'status': 'pending',
            'priority': 2,
            'assignee': '王五',
            'created_at': '2024-01-03',
            'due_date': None,
            'tags': ['documentation', 'api']
        }
    }
    
    # 测试过滤器
    print("\n🔍 测试过滤器功能...")
    print("设置状态过滤为 'completed':")
    task_system['filters']['status'] = 'completed'
    
    print("\n设置优先级过滤为 '3':")
    task_system['filters']['priority'] = '3'
    
    print("\n清除过滤器:")
    task_system['filters']['status'] = 'all'
    task_system['filters']['priority'] = 'all'
    
    # 添加新任务
    print("\n➕ 添加新任务:")
    new_tasks = dict(task_system['tasks'])
    new_tasks['task_4'] = {
        'id': 'task_4',
        'title': '部署到生产环境',
        'description': '将应用部署到生产服务器',
        'status': 'pending',
        'priority': 4,
        'assignee': '赵六',
        'created_at': '2024-01-04',
        'due_date': '2024-01-25',
        'tags': ['deployment', 'production']
    }
    task_system['tasks'] = new_tasks
    
    # 更新任务状态
    print("\n✅ 完成一个任务:")
    updated_tasks = dict(task_system['tasks'])
    updated_tasks['task_3']['status'] = 'completed'
    task_system['tasks'] = updated_tasks


def reactive_shopping_system() -> None:
    """演示响应式购物系统"""
    print("\n🛒 响应式购物系统示例")
    print("=" * 50)
    
    # 商品数据
    products = ReactiveDict({
        'laptop': {'name': '笔记本电脑', 'price': 5999, 'stock': 10, 'category': 'electronics'},
        'mouse': {'name': '无线鼠标', 'price': 199, 'stock': 50, 'category': 'electronics'},
        'book': {'name': 'Python编程书籍', 'price': 89, 'stock': 20, 'category': 'books'}
    })
    
    # 购物车
    cart = ReactiveDict({'placeholder': 0})  # 临时占位符
    cart.clear()  # 清空，变成真正的空购物车
    
    # 用户信息
    user = ReactiveDict({
        'name': '张三',
        'vip_level': 'gold',  # bronze, silver, gold
        'points': 1500
    })
    
    # 优惠规则
    discount_rules = ReactiveDict({
        'vip_discounts': {'bronze': 0.05, 'silver': 0.10, 'gold': 0.15},
        'bulk_discount_threshold': 5,  # 超过5件商品打9折
        'bulk_discount_rate': 0.10,
        'free_shipping_threshold': 299  # 满299免邮
    })
    
    # 订单汇总
    order_summary = ReactiveDict({
        'subtotal': 0.0,
        'discount_amount': 0.0,
        'shipping_fee': 20.0,
        'total': 0.0,
        'items_count': 0
    })
    
    # 创建购物车计算 Effect
    @effect
    def calculate_order() -> None:
        """计算订单汇总"""
        # 计算小计
        subtotal = 0.0
        items_count = 0
        
        for product_id, quantity in cart.items():
            if product_id in products:
                price = products[product_id]['price']
                subtotal += price * quantity
                items_count += quantity
        
        # 计算VIP折扣
        vip_level = user['vip_level']
        vip_discount_rate = discount_rules['vip_discounts'].get(vip_level, 0)
        vip_discount = subtotal * vip_discount_rate
        
        # 计算批量折扣
        bulk_discount = 0.0
        if items_count >= discount_rules['bulk_discount_threshold']:
            bulk_discount = subtotal * discount_rules['bulk_discount_rate']
        
        # 总折扣（取较大值）
        discount_amount = max(vip_discount, bulk_discount)
        
        # 运费计算
        shipping_fee = 0.0 if subtotal >= discount_rules['free_shipping_threshold'] else 20.0
        
        # 最终总价
        total = subtotal - discount_amount + shipping_fee
        
        # 更新订单汇总
        order_summary['subtotal'] = subtotal
        order_summary['discount_amount'] = discount_amount
        order_summary['shipping_fee'] = shipping_fee
        order_summary['total'] = total
        order_summary['items_count'] = items_count
        
        print(f"  💰 订单汇总更新:")
        print(f"    商品小计: ¥{subtotal:.2f}")
        print(f"    优惠金额: ¥{discount_amount:.2f} (VIP: ¥{vip_discount:.2f}, 批量: ¥{bulk_discount:.2f})")
        print(f"    运费: ¥{shipping_fee:.2f}")
        print(f"    总计: ¥{total:.2f}")
        print(f"    商品数量: {items_count} 件")
        print()
    
    # 创建库存预警 Effect
    @effect
    def stock_alert() -> None:
        """库存预警"""
        for product_id, product_info in products.items():
            stock = product_info['stock']
            if stock <= 5:
                print(f"  ⚠️  库存预警: {product_info['name']} 仅剩 {stock} 件")
    
    print("✅ 创建了购物系统")
    
    # 模拟购物流程
    print("\n🛍️  开始购物...")
    cart['laptop'] = 1
    cart['mouse'] = 2
    
    print("\n📈 增加购买数量:")
    cart['laptop'] = 2  # VIP折扣应用
    
    print("\n➕ 添加更多商品:")
    cart['book'] = 3  # 触发批量折扣
    
    print("\n🎖️  升级VIP等级:")
    user['vip_level'] = 'gold'  # 更高的VIP折扣
    
    print("\n📦 减少库存(模拟其他用户购买):")
    updated_products = dict(products)
    updated_products['mouse']['stock'] = 3  # 触发库存预警
    products.update(updated_products)


def reactive_form_validation_system() -> None:
    """演示复杂表单验证系统"""
    print("\n📝 复杂表单验证系统示例")  
    print("=" * 50)
    
    # 表单数据
    form = ReactiveDict({
        'personal': {
            'first_name': '',
            'last_name': '', 
            'email': '',
            'phone': '',
            'birth_date': ''
        },
        'account': {
            'username': '',
            'password': '',
            'confirm_password': ''
        },
        'preferences': {
            'newsletter': False,
            'notifications': True,
            'theme': 'light'
        }
    })
    
    # 验证状态
    validation = ReactiveDict({
        'personal': {
            'first_name_valid': False,
            'last_name_valid': False,
            'email_valid': False,
            'phone_valid': False,
            'birth_date_valid': False,
            'section_valid': False
        },
        'account': {
            'username_valid': False,
            'password_valid': False,
            'confirm_password_valid': False,
            'section_valid': False
        },
        'preferences': {
            'section_valid': True  # 偏好设置总是有效
        },
        'form_valid': False
    })
    
    # 错误信息
    errors = ReactiveDict({
        'personal': {},
        'account': {},
        'preferences': {}
    })
    
    # 个人信息验证 Effect
    @effect
    def validate_personal() -> None:
        """验证个人信息"""
        personal = form['personal']
        personal_errors = {}
        
        # 姓名验证
        first_name_valid = len(personal['first_name']) >= 2
        if not first_name_valid and personal['first_name']:
            personal_errors['first_name'] = '姓氏至少2个字符'
            
        last_name_valid = len(personal['last_name']) >= 2
        if not last_name_valid and personal['last_name']:
            personal_errors['last_name'] = '名字至少2个字符'
        
        # 邮箱验证
        email = personal['email']
        email_valid = '@' in email and '.' in email.split('@')[-1] and len(email) >= 5
        if not email_valid and email:
            personal_errors['email'] = '请输入有效的邮箱地址'
        
        # 手机验证
        phone = personal['phone']
        phone_valid = phone.isdigit() and len(phone) == 11 and phone.startswith('1')
        if not phone_valid and phone:
            personal_errors['phone'] = '请输入有效的手机号码'
        
        # 生日验证
        birth_date = personal['birth_date']
        birth_date_valid = len(birth_date) == 10 and birth_date.count('-') == 2
        if not birth_date_valid and birth_date:
            personal_errors['birth_date'] = '请使用 YYYY-MM-DD 格式'
        
        section_valid = (first_name_valid and last_name_valid and 
                        email_valid and phone_valid and birth_date_valid)
        
        # 更新验证状态
        validation['personal']['first_name_valid'] = first_name_valid
        validation['personal']['last_name_valid'] = last_name_valid
        validation['personal']['email_valid'] = email_valid
        validation['personal']['phone_valid'] = phone_valid
        validation['personal']['birth_date_valid'] = birth_date_valid
        validation['personal']['section_valid'] = section_valid
        
        errors['personal'] = personal_errors
        
        print(f"  👤 个人信息验证: {'✅' if section_valid else '❌'}")
        if personal_errors:
            for field, error in personal_errors.items():
                print(f"    - {field}: {error}")
    
    # 账户信息验证 Effect
    @effect  
    def validate_account() -> None:
        """验证账户信息"""
        account = form['account']
        account_errors = {}
        
        # 用户名验证
        username = account['username']
        username_valid = len(username) >= 3 and username.isalnum()
        if not username_valid and username:
            account_errors['username'] = '用户名至少3个字符，只能包含字母和数字'
        
        # 密码验证
        password = account['password']
        password_valid = (len(password) >= 8 and 
                         any(c.isupper() for c in password) and
                         any(c.islower() for c in password) and
                         any(c.isdigit() for c in password))
        if not password_valid and password:
            account_errors['password'] = '密码至少8位，包含大小写字母和数字'
        
        # 确认密码验证
        confirm_password = account['confirm_password']
        confirm_password_valid = confirm_password == password and password_valid
        if not confirm_password_valid and confirm_password:
            account_errors['confirm_password'] = '两次密码输入不一致'
        
        section_valid = username_valid and password_valid and confirm_password_valid
        
        # 更新验证状态
        validation['account']['username_valid'] = username_valid
        validation['account']['password_valid'] = password_valid
        validation['account']['confirm_password_valid'] = confirm_password_valid
        validation['account']['section_valid'] = section_valid
        
        errors['account'] = account_errors
        
        print(f"  🔐 账户信息验证: {'✅' if section_valid else '❌'}")
        if account_errors:
            for field, error in account_errors.items():
                print(f"    - {field}: {error}")
    
    # 整体表单验证 Effect
    @effect
    def validate_form() -> None:
        """验证整个表单"""
        personal_valid = validation['personal']['section_valid']
        account_valid = validation['account']['section_valid']
        preferences_valid = validation['preferences']['section_valid']
        
        form_valid = personal_valid and account_valid and preferences_valid
        validation['form_valid'] = form_valid
        
        print(f"  📋 整体表单: {'✅ 有效' if form_valid else '❌ 无效'}")
        print(f"    个人信息: {'✅' if personal_valid else '❌'}")
        print(f"    账户信息: {'✅' if account_valid else '❌'}")
        print(f"    偏好设置: {'✅' if preferences_valid else '❌'}")
        print()
    
    print("✅ 创建了表单验证系统")
    
    # 模拟用户填写表单
    print("\n📝 用户开始填写表单...")
    
    print("\n输入个人信息:")
    form['personal']['first_name'] = '张'
    form['personal']['last_name'] = '三'
    form['personal']['email'] = 'zhangsan@example.com'
    form['personal']['phone'] = '13800138000'
    form['personal']['birth_date'] = '1990-01-01'
    
    print("\n输入账户信息:")
    form['account']['username'] = 'zhangsan123'
    form['account']['password'] = 'MyPassword123'
    form['account']['confirm_password'] = 'MyPassword123'
    
    print("\n🎉 表单填写完成！")


def main() -> None:
    """主函数 - 运行所有高级示例"""
    print("🚀 CogniHub PyEffectRef - ReactiveDict 高级示例")
    print("=" * 80)
    
    try:
        advanced_task_management_system()
        reactive_shopping_system()
        reactive_form_validation_system()
        
        print("\n" + "=" * 80)
        print("✨ 所有高级示例运行完成！")
        print("\n💡 高级技巧要点:")
        print("   1. 多个 Effect 可以协调工作处理复杂逻辑")
        print("   2. 响应式数据结构适合状态管理")
        print("   3. 嵌套数据和条件验证的强大组合")
        print("   4. 实时计算和自动更新提升用户体验")
        print("   5. 复杂业务逻辑可以拆分为多个小的Effect")
        
    except Exception as e:
        print(f"❌ 运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
