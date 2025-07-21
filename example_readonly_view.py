"""ReadOnlyView 使用示例"""
import sys
import os
import time

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cognihub_pyeffectref import ReactiveDict, effect
from cognihub_pyeffectref.view import ReadOnlyView

def main():
    print("=== ReadOnlyView 使用示例 ===\n")
    
    # 1. 创建响应式数据
    print("1. 创建应用状态数据")
    app_state = ReactiveDict({
        'user': {
            'name': 'Alice',
            'profile': {
                'age': 25,
                'city': 'Shanghai'
            },
            'settings': {
                'theme': 'dark',
                'notifications': True
            }
        },
        'app': {
            'version': '1.0.0',
            'features': ['auth', 'dashboard', 'settings']
        }
    })
    print(f"应用状态: {app_state.to_dict()}")
    
    # 2. 创建只读视图
    print("\n2. 创建只读视图(用于插件或不受信任组件)")
    readonly_view = ReadOnlyView(app_state)
    
    # 3. 通过只读视图读取数据
    print("\n3. 通过只读视图读取数据")
    print("用户名:", readonly_view.user.name.value)
    print("年龄:", readonly_view.user.profile.age.value)
    print("主题:", readonly_view.user.settings.theme.value)
    print("版本:", readonly_view.app.version.value)
    
    # 4. 测试只读特性
    print("\n4. 测试只读特性")
    try:
        readonly_view.user.name = "Hacker"
        print("❌ 错误: 应该不能修改只读视图")
    except AttributeError as e:
        print(f"✅ 正确: {e}")
    
    try:
        readonly_view['user']['name'] = "Hacker"
        print("❌ 错误: 应该不能通过字典方式修改")
    except TypeError as e:
        print(f"✅ 正确: {e}")
    
    # 5. 监听数据变化
    print("\n5. 设置数据监听 (插件监听模式)")
    
    # 模拟插件监听用户名变化
    user_name_ref = readonly_view.user.name
    theme_ref = readonly_view.user.settings.theme
    
    @effect
    def plugin_user_watcher():
        print(f"🔍 插件检测到用户名变化: {user_name_ref.value}")
    
    @effect
    def plugin_theme_watcher():
        print(f"🎨 插件检测到主题变化: {theme_ref.value}")
    
    # 手动调用一次以建立监听
    plugin_user_watcher()
    plugin_theme_watcher()
    
    print("\n6. 从主应用修改数据")
    # 从原始数据源修改
    print("修改用户名...")
    app_state.user.name = "Bob"
    
    time.sleep(0.1)  # 给异步通知一点时间
    
    print("修改主题...")
    app_state.user.settings.theme = "light"
    
    time.sleep(0.1)
    
    # 7. 创建子视图
    print("\n7. 创建受限子视图")
    user_only_view = ReadOnlyView(app_state.user)
    print("用户子视图 - 姓名:", user_only_view.name.value)
    print("用户子视图 - 城市:", user_only_view.profile.city.value)
    
    try:
        # 尝试访问不在子视图范围内的数据
        _ = user_only_view.app.version.value
        print("❌ 错误: 应该无法访问app数据")
    except AttributeError:
        print("✅ 正确: 子视图正确隔离了访问范围")
    
    # 8. 转换为普通字典
    print("\n8. 转换为普通字典")
    user_dict = user_only_view.to_dict()
    print("用户数据字典:", user_dict)
    
    # 修改字典不影响原始数据
    user_dict['name'] = 'Modified'
    print("修改字典后, 原始用户名仍为:", user_only_view.name.value)
    
    # 9. 嵌套视图访问
    print("\n9. 深层嵌套访问")
    profile_view = readonly_view.user.profile
    settings_view = readonly_view.user.settings
    
    print("个人资料视图 - 年龄:", profile_view.age.value)
    print("设置视图 - 通知:", settings_view.notifications.value)
    
    print("\n=== 示例完成 ===")

if __name__ == "__main__":
    main()
