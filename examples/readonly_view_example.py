#!/usr/bin/env python3
"""
ReadOnlyView 示例

演示 ReadOnlyView 的使用方法，包括：
- 创建只读视图
- 与 ReactiveDict 的配合使用
- 数据访问和监听
"""
import sys
import os
from typing import Protocol, cast, Any

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cognihub_pyeffectref import ReactiveDict, effect, ReadOnlyRef, ReadOnlyView

def basic_readonly_view_example() -> None:
    """演示基本的只读视图使用"""
    print("👁️  基本只读视图示例")
    print("=" * 50)

    # 创建用户数据
    user_data = ReactiveDict({
        'name': '张三',
        'email': 'zhangsan@example.com',
        'age': 25,
        'is_active': True
    })

    # 创建只读视图
    user_view = ReadOnlyView(user_data)

    print("📋 用户数据创建完成")
    print(f"  姓名: {user_view.name.value}")
    print(f"  邮箱: {user_view.email.value}")
    print(f"  年龄: {user_view.age.value}")
    print(f"  活跃状态: {user_view.is_active.value}")

    # 演示只读特性
    print("\n🔒 测试只读特性:")
    try:
        user_view.name = '李四'
    except AttributeError as e:
        print(f"  ✅ 正确阻止了写入操作: {e}")

    try:
        user_view['email'] = 'lisi@example.com'
    except TypeError as e:
        print(f"  ✅ 正确阻止了字典写入操作: {e}")

    # 演示响应式监听
    print("\n🔊 设置响应式监听:")

    @effect
    def watch_user_name() -> None:
        name = user_view.name.value
        print(f"  👤 用户名变化: {name}")

    @effect
    def watch_user_age() -> None:
        age = user_view.age.value
        print(f"  🎂 年龄变化: {age}")

    # 建立监听
    watch_user_name()
    watch_user_age()

    print("\n📝 修改原始数据:")
    user_data.name = '李四'
    user_data.age = 26

    print("\n📊 当前用户信息:")
    user_dict = user_view.to_dict()
    for key, value in user_dict.items():
        print(f"  {key}: {value}")


def nested_data_example() -> None:
    """演示嵌套数据的只读视图"""
    print("\n🏗️  嵌套数据示例")
    print("=" * 50)

    # 创建嵌套的配置数据
    app_config = ReactiveDict({
        'ui': {
            'theme': 'dark',
            'language': 'zh-cn',
            'font_size': 14
        },
        'api': {
            'base_url': 'https://api.example.com',
            'timeout': 30,
            'retry_count': 3
        },
        'features': {
            'debug_mode': False,
            'analytics': True,
            'notifications': True
        }
    })

    class UIConfig(Protocol):
        theme: ReadOnlyRef[str]
        language: ReadOnlyRef[str]
        font_size: ReadOnlyRef[int]

        def to_dict(self) -> dict[str, Any]:
            ...

    class ApiConfig(Protocol):
        base_url: ReadOnlyRef[str]
        timeout: ReadOnlyRef[int]
        retry_count: ReadOnlyRef[int]

        def to_dict(self) -> dict[str, Any]:
            ...

    class FeaturesConfig(Protocol):
        debug_mode: ReadOnlyRef[bool]
        analytics: ReadOnlyRef[bool]
        notifications: ReadOnlyRef[bool]

        def to_dict(self) -> dict[str, Any]:
            ...

    class AppConfig(Protocol):
        ui: UIConfig
        api: ApiConfig
        features: FeaturesConfig

        def to_dict(self) -> dict[str, Any]:
            ...

    # 创建只读视图
    config_view = cast(AppConfig, ReadOnlyView(app_config))

    print("🔧 配置数据创建完成")
    print(f"  UI主题: {config_view.ui.theme.value}")
    print(f"  API地址: {config_view.api.base_url.value}")
    print(f"  调试模式: {config_view.features.debug_mode.value}")

    # 演示嵌套访问
    print("\n🌲 演示嵌套数据访问:")
    ui_view = config_view.ui
    print(f"  UI配置类型: {type(ui_view)}")
    print(f"  字体大小: {ui_view.font_size.value}")

    # 设置嵌套监听
    print("\n🔊 设置嵌套数据监听:")

    @effect
    def watch_theme() -> None:
        theme = config_view.ui.theme.value
        print(f"  🎨 主题变更: {theme}")

    @effect
    def watch_debug_mode() -> None:
        debug = config_view.features.debug_mode.value
        status = "开启" if debug else "关闭"
        print(f"  🐛 调试模式: {status}")

    # 建立监听
    watch_theme()
    watch_debug_mode()

    print("\n📝 修改嵌套配置:")
    app_config.ui.theme = 'light'
    app_config.features.debug_mode = True

    print("\n📋 完整配置信息:")
    config_dict = config_view.to_dict()
    for section, settings in config_dict.items():
        print(f"  {section}:")
        for key, value in settings.items():
            print(f"    {key}: {value}")


def dashboard_data_example() -> None:
    """演示仪表板数据的多视图访问"""
    print("\n📊 仪表板数据示例")
    print("=" * 50)

    # 创建后端数据存储
    backend_data = ReactiveDict({
        'user_stats': {
            'total_users': 1250,
            'active_users': 892,
            'new_signups': 45
        },
        'sales_stats': {
            'total_revenue': 125000.50,
            'orders_count': 234,
            'avg_order_value': 534.19
        },
        'system_status': {
            'cpu_usage': 45.2,
            'memory_usage': 67.8,
            'disk_usage': 34.5
        }
    })

    class UserStats(Protocol):
        total_users: ReadOnlyRef[int]
        active_users: ReadOnlyRef[int]
        new_signups: ReadOnlyRef[int]

        def to_dict(self) -> dict[str, Any]:
            ...

    class SalesStats(Protocol):
        total_revenue: ReadOnlyRef[float]
        orders_count: ReadOnlyRef[int]
        avg_order_value: ReadOnlyRef[float]

        def to_dict(self) -> dict[str, Any]:
            ...

    class SystemStatus(Protocol):
        cpu_usage: ReadOnlyRef[float]
        memory_usage: ReadOnlyRef[float]
        disk_usage: ReadOnlyRef[float]

        def to_dict(self) -> dict[str, Any]:
            ...

    class BackendData(Protocol):
        user_stats: UserStats
        sales_stats: SalesStats
        system_status: SystemStatus

        def to_dict(self) -> dict[str, Any]:
            ...

    print("🎯 创建专门的数据视图:")

    # 创建专门的视图
    user_stats_view = cast(BackendData, ReadOnlyView(backend_data))
    sales_stats_view = cast(BackendData, ReadOnlyView(backend_data))
    system_status_view = cast(BackendData, ReadOnlyView(backend_data))

    print(f"  👥 总用户数: {user_stats_view.user_stats.total_users.value}")
    print(f"  💰 总收入: ¥{sales_stats_view.sales_stats.total_revenue.value}")
    print(f"  💻 CPU使用率: {system_status_view.system_status.cpu_usage.value}%")

    # 演示实时数据更新
    print("\n🔄 模拟实时数据更新:")

    @effect
    def watch_user_growth() -> None:
        total = user_stats_view.user_stats.total_users.value
        active = user_stats_view.user_stats.active_users.value
        print(f"  📈 用户统计 - 总数: {total}, 活跃: {active}")

    @effect
    def watch_sales_performance() -> None:
        revenue = sales_stats_view.sales_stats.total_revenue.value
        orders = sales_stats_view.sales_stats.orders_count.value
        print(f"  💼 销售统计 - 收入: ¥{revenue}, 订单: {orders}")

    # 建立监听
    watch_user_growth()
    watch_sales_performance()

    # 模拟数据更新
    print("\n📝 更新数据:")
    backend_data.user_stats.total_users = 1255
    backend_data.user_stats.active_users = 895
    backend_data.sales_stats.total_revenue = 126500.75
    backend_data.sales_stats.orders_count = 238


def permission_based_views_example() -> None:
    """演示基于权限的视图访问"""
    print("\n🔐 权限控制视图示例")
    print("=" * 50)

    # 创建用户权限数据
    user_permissions = ReactiveDict({
        'read_permissions': {
            'can_read_posts': True,
            'can_read_comments': True,
            'can_read_profiles': False
        },
        'admin_permissions': {
            'can_manage_users': False,
            'can_manage_content': True,
            'can_view_analytics': True
        },
        'publish_permissions': {
            'can_create_posts': True,
            'can_edit_posts': False,
            'can_delete_posts': False
        }
    })

    class ReadPermissions(Protocol):
        can_read_posts: ReadOnlyRef[bool]
        can_read_comments: ReadOnlyRef[bool]
        can_read_profiles: ReadOnlyRef[bool]

        def to_dict(self) -> dict[str, Any]:
            ...

    class AdminPermissions(Protocol):
        can_manage_users: ReadOnlyRef[bool]
        can_manage_content: ReadOnlyRef[bool]
        can_view_analytics: ReadOnlyRef[bool]

        def to_dict(self) -> dict[str, Any]:
            ...

    class PublishPermissions(Protocol):
        can_create_posts: ReadOnlyRef[bool]
        can_edit_posts: ReadOnlyRef[bool]
        can_delete_posts: ReadOnlyRef[bool]

        def to_dict(self) -> dict[str, Any]:
            ...

    class UserPermissions(Protocol):
        read_permissions: ReadPermissions
        admin_permissions: AdminPermissions
        publish_permissions: PublishPermissions

        def to_dict(self) -> dict[str, Any]:
            ...

    print("🎭 创建基于权限的视图:")

    # 创建不同权限级别的视图
    read_permission_view = cast(UserPermissions, ReadOnlyView(user_permissions))
    admin_permission_view = cast(UserPermissions, ReadOnlyView(user_permissions))
    publish_permission_view = cast(UserPermissions, ReadOnlyView(user_permissions))

    print("  📖 读取权限:")
    print(f"    阅读帖子: {read_permission_view.read_permissions.can_read_posts.value}")
    print(f"    阅读评论: {read_permission_view.read_permissions.can_read_comments.value}")

    print("  👑 管理权限:")
    print(f"    用户管理: {admin_permission_view.admin_permissions.can_manage_users.value}")
    print(f"    内容管理: {admin_permission_view.admin_permissions.can_manage_content.value}")

    print("  ✍️  发布权限:")
    print(f"    创建帖子: {publish_permission_view.publish_permissions.can_create_posts.value}")
    print(f"    编辑帖子: {publish_permission_view.publish_permissions.can_edit_posts.value}")

    # 演示权限变更监听
    print("\n🔊 监听权限变更:")

    @effect
    def watch_admin_permissions() -> None:
        can_manage = admin_permission_view.admin_permissions.can_manage_users.value
        status = "拥有" if can_manage else "无"
        print(f"  👥 用户管理权限状态: {status}")

    # 建立监听
    watch_admin_permissions()

    print("\n📝 升级用户权限:")
    user_permissions.admin_permissions.can_manage_users = True
    user_permissions.publish_permissions.can_edit_posts = True

    print("\n🎯 最终权限状态:")
    for permission_type, permissions in user_permissions.to_dict().items():
        print(f"  {permission_type}:")
        for perm, value in permissions.items():
            status = "✅" if value else "❌"
            print(f"    {status} {perm}")


def complex_dashboard_example() -> None:
    """演示复杂仪表板的数据管理"""
    print("\n🎛️  复杂仪表板示例")
    print("=" * 50)

    # 创建复杂的仪表板数据
    dashboard_data = ReactiveDict({
        'overview': {
            'total_visits': 15420,
            'unique_visitors': 8930,
            'bounce_rate': 0.342,
            'avg_session_duration': 185.6
        },
        'geographic': {
            'top_countries': ['中国', '美国', '日本', '德国', '英国'],
            'country_stats': {
                '中国': {'visits': 5680, 'percentage': 36.8},
                '美国': {'visits': 3210, 'percentage': 20.8},
                '日本': {'visits': 1890, 'percentage': 12.3}
            }
        },
        'device_stats': {
            'mobile': 8450,
            'desktop': 5120,
            'tablet': 1850
        },
        'conversion': {
            'signup_rate': 0.045,
            'purchase_rate': 0.023,
            'cart_abandonment_rate': 0.687
        }
    })

    class Overview(Protocol):
        total_visits: ReadOnlyRef[int]
        unique_visitors: ReadOnlyRef[int]
        bounce_rate: ReadOnlyRef[float]
        avg_session_duration: ReadOnlyRef[float]

        def to_dict(self) -> dict[str, Any]:
            ...

    class Geographic(Protocol):
        top_countries: ReadOnlyRef[list[str]]
        country_stats: ReadOnlyRef[dict[str, dict[str, Any]]]

        def to_dict(self) -> dict[str, Any]:
            ...

    class DeviceStats(Protocol):
        mobile: ReadOnlyRef[int]
        desktop: ReadOnlyRef[int]
        tablet: ReadOnlyRef[int]

        def to_dict(self) -> dict[str, Any]:
            ...

    class Conversion(Protocol):
        signup_rate: ReadOnlyRef[float]
        purchase_rate: ReadOnlyRef[float]
        cart_abandonment_rate: ReadOnlyRef[float]

        def to_dict(self) -> dict[str, Any]:
            ...

    class DashboardData(Protocol):
        overview: Overview
        geographic: Geographic
        device_stats: DeviceStats
        conversion: Conversion

        def to_dict(self) -> dict[str, Any]:
            ...

    # 创建专门的视图
    overview_view = cast(DashboardData, ReadOnlyView(dashboard_data))

    print("📊 仪表板概览:")
    print(f"  总访问量: {overview_view.overview.total_visits.value:,}")
    print(f"  独立访客: {overview_view.overview.unique_visitors.value:,}")
    print(f"  跳出率: {overview_view.overview.bounce_rate.value:.1%}")

    print("\n🌍 地理分布统计:")
    top_countries = overview_view.geographic.top_countries.value
    for i, country in enumerate(top_countries[:3], 1):
        print(f"  {i}. {country}")

    print("\n📱 设备统计:")
    device_stats = overview_view.device_stats
    mobile_count = device_stats.mobile.value
    desktop_count = device_stats.desktop.value
    tablet_count = device_stats.tablet.value
    total_devices = mobile_count + desktop_count + tablet_count

    print(f"  移动端: {mobile_count:,} ({mobile_count/total_devices:.1%})")
    print(f"  桌面端: {desktop_count:,} ({desktop_count/total_devices:.1%})")
    print(f"  平板端: {tablet_count:,} ({tablet_count/total_devices:.1%})")

    # 设置关键指标监听
    print("\n🎯 监听关键指标变化:")

    @effect
    def watch_conversion_metrics() -> None:
        conversion = overview_view.conversion
        signup_rate = conversion.signup_rate.value
        purchase_rate = conversion.purchase_rate.value
        print(f"  📈 转化率监控 - 注册: {signup_rate:.1%}, 购买: {purchase_rate:.1%}")

    @effect
    def watch_traffic_metrics() -> None:
        overview = overview_view.overview
        total_visits = overview.total_visits.value
        unique_visitors = overview.unique_visitors.value
        repeat_rate = (total_visits - unique_visitors) / total_visits
        print(f"  🚦 流量监控 - 总访问: {total_visits:,}, 重访率: {repeat_rate:.1%}")

    # 建立监听
    watch_conversion_metrics()
    watch_traffic_metrics()

    print("\n📝 模拟实时数据更新:")
    dashboard_data.overview.total_visits = 15487
    dashboard_data.overview.unique_visitors = 8942
    dashboard_data.conversion.signup_rate = 0.048
    dashboard_data.conversion.purchase_rate = 0.025


def main() -> None:
    """运行所有示例"""
    basic_readonly_view_example()
    nested_data_example()
    dashboard_data_example()
    permission_based_views_example()
    complex_dashboard_example()

    print("\n" + "=" * 50)
    print("✨ ReadOnlyView 示例运行完成!")
    print("主要特性:")
    print("  🔒 提供数据的只读访问")
    print("  🔄 保持响应式特性")
    print("  🌲 支持嵌套数据结构")
    print("  👁️  简化数据访问接口")


if __name__ == "__main__":
    main()
