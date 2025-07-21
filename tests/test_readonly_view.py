"""ReadOnlyView的测试文件"""
import unittest
import asyncio
import sys
import os
from typing import Any, List

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognihub_pyeffectref.reactive_dict import ReactiveDict
from cognihub_pyeffectref.view import ReadOnlyView, ActionExecutor
from cognihub_pyeffectref.ref import ReadOnlyRef, Ref
from cognihub_pyeffectref.effect import effect


class TestReadOnlyView(unittest.TestCase):
    """ReadOnlyView的基本功能测试"""
    
    def setUp(self) -> None:
        """设置测试环境"""
        self.test_data = {
            'name': 'Alice',
            'age': 30,
            'nested': {
                'city': 'Shanghai',
                'score': 95
            }
        }
        self.reactive_dict = ReactiveDict(self.test_data)
        self.readonly_view = ReadOnlyView(self.reactive_dict)
    
    def test_dot_notation_access_leaf_values(self) -> None:
        """测试通过点语法访问叶子节点值"""
        name_ref = self.readonly_view.name
        age_ref = self.readonly_view.age
        
        # 应该返回 ReadOnlyRef 对象
        self.assertIsInstance(name_ref, ReadOnlyRef)
        self.assertIsInstance(age_ref, ReadOnlyRef)
        
        # 值应该正确
        self.assertEqual(name_ref.value, 'Alice')
        self.assertEqual(age_ref.value, 30)
    
    def test_bracket_notation_access_leaf_values(self) -> None:
        """测试通过字典风格访问叶子节点值"""
        name_ref = self.readonly_view['name']
        age_ref = self.readonly_view['age']
        
        # 应该返回 ReadOnlyRef 对象
        self.assertIsInstance(name_ref, ReadOnlyRef)
        self.assertIsInstance(age_ref, ReadOnlyRef)
        
        # 值应该正确
        self.assertEqual(name_ref.value, 'Alice')
        self.assertEqual(age_ref.value, 30)
    
    def test_nested_dict_access(self) -> None:
        """测试访问嵌套字典"""
        nested_view = self.readonly_view.nested
        
        # 应该返回 ReadOnlyView 对象
        self.assertIsInstance(nested_view, ReadOnlyView)
        
        # 可以继续访问嵌套的属性
        city_ref = nested_view.city  # type: ignore
        score_ref = nested_view.score  # type: ignore
        
        self.assertIsInstance(city_ref, ReadOnlyRef)
        self.assertIsInstance(score_ref, ReadOnlyRef)
        self.assertEqual(city_ref.value, 'Shanghai')
        self.assertEqual(score_ref.value, 95)
    
    def test_nested_dict_bracket_access(self) -> None:
        """测试通过字典风格访问嵌套字典"""
        nested_view = self.readonly_view['nested']
        
        # 应该返回 ReadOnlyView 对象
        self.assertIsInstance(nested_view, ReadOnlyView)
        
        # 可以继续访问嵌套的属性
        city_ref = nested_view['city']  # type: ignore
        score_ref = nested_view['score']  # type: ignore
        
        self.assertIsInstance(city_ref, ReadOnlyRef)
        self.assertIsInstance(score_ref, ReadOnlyRef)
        self.assertEqual(city_ref.value, 'Shanghai')
        self.assertEqual(score_ref.value, 95)
    
    def test_nonexistent_attribute_error(self) -> None:
        """测试访问不存在的属性"""
        with self.assertRaises(AttributeError) as cm:
            _ = self.readonly_view.nonexistent
        self.assertIn("object has no attribute 'nonexistent'", str(cm.exception))
    
    def test_nonexistent_key_error(self) -> None:
        """测试访问不存在的键"""
        with self.assertRaises(KeyError) as cm:
            _ = self.readonly_view['nonexistent']
        self.assertIn("'nonexistent' not found in ReadOnlyView", str(cm.exception))
    
    def test_to_dict(self) -> None:
        """测试 to_dict 方法"""
        result = self.readonly_view.to_dict()
        
        # 应该返回普通字典
        self.assertIsInstance(result, dict)
        self.assertEqual(result, self.test_data)
        
        # 修改返回的字典不应影响原始数据
        result['name'] = 'Bob'
        self.assertEqual(self.readonly_view.name.value, 'Alice')


class TestReadOnlyViewReadOnlyBehavior(unittest.TestCase):
    """测试ReadOnlyView的只读特性"""
    
    def setUp(self) -> None:
        """设置测试环境"""
        self.reactive_dict = ReactiveDict({'name': 'Alice', 'age': 30})
        self.readonly_view = ReadOnlyView(self.reactive_dict)
    
    def test_cannot_set_attribute(self) -> None:
        """测试不能通过点语法设置属性"""
        with self.assertRaises(AttributeError) as cm:
            self.readonly_view.name = 'Bob'
        self.assertIn("Cannot modify attribute 'name' on a read-only view", str(cm.exception))
    
    def test_cannot_set_item(self) -> None:
        """测试不能通过字典风格设置属性"""
        with self.assertRaises(TypeError) as cm:
            self.readonly_view['name'] = 'Bob'
        self.assertIn("Cannot set item 'name' on a read-only view", str(cm.exception))
    
    def test_private_attributes_allowed(self) -> None:
        """测试允许设置私有属性"""
        # 这应该不会抛出异常
        self.readonly_view._test_private = 'test'
        self.assertEqual(self.readonly_view._test_private, 'test')
    
    def test_readonly_ref_behavior(self) -> None:
        """测试ReadOnlyRef的只读行为"""
        name_ref = self.readonly_view.name
        
        # ReadOnlyRef 应该不允许修改
        with self.assertRaises(AttributeError):
            name_ref.value = 'Bob'  # type: ignore


class TestReadOnlyViewReactivity(unittest.TestCase):
    """测试ReadOnlyView的响应式特性"""
    
    def setUp(self) -> None:
        """设置测试环境"""
        self.reactive_dict = ReactiveDict({'count': 0, 'nested': {'value': 10}})
        self.readonly_view = ReadOnlyView(self.reactive_dict)
        self.effect_called = False
        self.effect_value: Any = None
    
    def test_watch_leaf_value_changes(self) -> None:
        """测试监听叶子节点值的变化"""
        count_ref = self.readonly_view.count
        
        @effect
        def watch_count() -> None:
            self.effect_called = True
            self.effect_value = count_ref.value
        
        # 手动调用一次以建立响应式连接
        watch_count()
        
        # 初始状态
        self.assertTrue(self.effect_called)
        self.assertEqual(self.effect_value, 0)
        
        # 重置标志
        self.effect_called = False
        
        # 修改原始数据
        self.reactive_dict.count = 5
        
        # effect 应该被触发
        self.assertTrue(self.effect_called)
        self.assertEqual(self.effect_value, 5)
    
    def test_watch_nested_value_changes(self) -> None:
        """测试监听嵌套值的变化"""
        nested_view = self.readonly_view.nested
        value_ref = nested_view.value
        
        @effect
        def watch_nested_value() -> None:
            self.effect_called = True
            self.effect_value = value_ref.value
        
        # 手动调用一次以建立响应式连接
        watch_nested_value()
        
        # 初始状态
        self.assertTrue(self.effect_called)
        self.assertEqual(self.effect_value, 10)
        
        # 重置标志
        self.effect_called = False
        
        # 修改嵌套数据
        self.reactive_dict.nested.value = 20
        
        # effect 应该被触发
        self.assertTrue(self.effect_called)
        self.assertEqual(self.effect_value, 20)
    
    def test_multiple_views_same_source(self) -> None:
        """测试多个视图访问同一数据源"""
        view1 = ReadOnlyView(self.reactive_dict)
        view2 = ReadOnlyView(self.reactive_dict)
        
        count_ref1 = view1.count
        count_ref2 = view2.count
        
        # 两个视图应该看到相同的数据
        self.assertEqual(count_ref1.value, count_ref2.value)
        
        # 修改数据后，两个视图都应该看到更新
        self.reactive_dict.count = 100
        self.assertEqual(count_ref1.value, 100)
        self.assertEqual(count_ref2.value, 100)


class TestReadOnlyViewAsyncBehavior(unittest.TestCase):
    """测试ReadOnlyView的异步行为"""
    
    def setUp(self) -> None:
        """设置测试环境"""
        self.reactive_dict = ReactiveDict({'async_value': 'initial'})
        self.readonly_view = ReadOnlyView(self.reactive_dict)
    
    async def test_async_effect_watching(self) -> None:
        """测试异步effect监听"""
        async_value_ref = self.readonly_view.async_value
        effect_calls: List[Any] = []
        
        @effect
        async def async_watch() -> None:
            effect_calls.append(async_value_ref.value)
            await asyncio.sleep(0.01)  # 模拟异步操作
        
        # 手动调用一次以建立响应式连接
        await async_watch()
        
        # 等待初始effect执行
        await asyncio.sleep(0.02)
        self.assertEqual(len(effect_calls), 1)
        self.assertEqual(effect_calls[0], 'initial')
        
        # 修改值
        self.reactive_dict.async_value = 'updated'
        
        # 等待异步effect执行
        await asyncio.sleep(0.02)
        self.assertEqual(len(effect_calls), 2)
        self.assertEqual(effect_calls[1], 'updated')


class TestReadOnlyViewComplexScenarios(unittest.TestCase):
    """测试ReadOnlyView的复杂场景"""
    
    def setUp(self) -> None:
        """设置测试环境"""
        self.complex_data = {
            'user': {
                'profile': {
                    'name': 'Alice',
                    'settings': {
                        'theme': 'dark',
                        'notifications': True
                    }
                },
                'stats': {
                    'login_count': 5
                }
            },
            'config': {
                'version': '1.0.0'
            }
        }
        self.reactive_dict = ReactiveDict(self.complex_data)
        self.readonly_view = ReadOnlyView(self.reactive_dict)
    
    def test_deep_nested_access(self) -> None:
        """测试深层嵌套访问"""
        # 通过点语法访问深层数据
        theme_ref = self.readonly_view.user.profile.settings.theme  # type: ignore
        self.assertIsInstance(theme_ref, ReadOnlyRef)
        self.assertEqual(theme_ref.value, 'dark')
        
        # 通过字典风格访问深层数据
        notifications_ref = self.readonly_view['user']['profile']['settings']['notifications']  # type: ignore
        self.assertIsInstance(notifications_ref, ReadOnlyRef)
        self.assertEqual(notifications_ref.value, True)
    
    def test_mixed_access_patterns(self) -> None:
        """测试混合访问模式"""
        # 混合使用点语法和字典访问
        login_count_ref = self.readonly_view.user['stats'].login_count  # type: ignore
        self.assertIsInstance(login_count_ref, ReadOnlyRef)
        self.assertEqual(login_count_ref.value, 5)
        
        version_ref = self.readonly_view['config'].version  # type: ignore
        self.assertIsInstance(version_ref, ReadOnlyRef)
        self.assertEqual(version_ref.value, '1.0.0')
    
    def test_untrusted_component_simulation(self) -> None:
        """模拟不受信任组件的使用场景"""
        # 模拟插件或不受信任组件只能读取数据
        plugin_view = ReadOnlyView(self.reactive_dict)
        
        # 插件可以读取数据
        user_name = plugin_view.user.profile.name.value  # type: ignore
        self.assertEqual(user_name, 'Alice')
        
        # 插件不能修改数据
        with self.assertRaises(AttributeError):
            plugin_view.user.profile.name = 'Hacker'  # type: ignore
        
        with self.assertRaises(TypeError):
            plugin_view['user']['profile']['name'] = 'Hacker'  # type: ignore
        
        # 插件可以监听数据变化
        effect_calls: List[Any] = []
        name_ref = plugin_view.user.profile.name  # type: ignore
        
        @effect
        def plugin_effect() -> None:
            effect_calls.append(name_ref.value)
        
        # 手动调用一次以建立响应式连接
        plugin_effect()
        
        # 初始调用
        self.assertEqual(len(effect_calls), 1)
        self.assertEqual(effect_calls[0], 'Alice')
        
        # 从原始数据源修改
        self.reactive_dict.user.profile.name = 'Bob'
        
        # 插件应该能感知到变化
        self.assertEqual(len(effect_calls), 2)
        self.assertEqual(effect_calls[1], 'Bob')
    
    def test_view_isolation(self) -> None:
        """测试视图隔离性"""
        # 创建多个视图
        view1 = ReadOnlyView(self.reactive_dict)
        view2 = ReadOnlyView(self.reactive_dict.user)
        
        # view1 可以访问全部数据
        self.assertEqual(view1.user.profile.name.value, 'Alice')  # type: ignore
        self.assertEqual(view1.config.version.value, '1.0.0')  # type: ignore
        
        # view2 只能访问user部分
        self.assertEqual(view2.profile.name.value, 'Alice')  # type: ignore
        
        # view2 不能访问config部分
        with self.assertRaises(AttributeError):
            _ = view2.config
    
    def test_to_dict_deep_copy(self) -> None:
        """测试深层数据的字典转换"""
        user_view = self.readonly_view.user
        user_dict = user_view.to_dict()  # type: ignore
        
        # 应该是完整的用户数据副本
        expected_user_data = self.complex_data['user']
        self.assertEqual(user_dict, expected_user_data)
        
        # 修改副本不应影响原始数据
        user_dict['profile']['name'] = 'Modified'
        self.assertEqual(self.readonly_view.user.profile.name.value, 'Alice')  # type: ignore


class TestActionExecutor(unittest.TestCase):
    """测试ActionExecutor类的功能"""
    
    def setUp(self) -> None:
        """设置测试环境"""
        self.actions = {
            'increment': lambda x: x + 1,
            'double': lambda x: x * 2,
            'greet': lambda name: f"Hello, {name}!"
        }
        self.executor = ActionExecutor(self.actions)
    
    def test_action_executor_creation(self) -> None:
        """测试ActionExecutor的创建"""
        self.assertIsInstance(self.executor, ActionExecutor)
        self.assertEqual(len(self.executor._allowed_actions), 3)
    
    def test_action_execution_via_dot_notation(self) -> None:
        """测试通过点语法执行action"""
        result1 = self.executor.increment(5)
        self.assertEqual(result1, 6)
        
        result2 = self.executor.double(4)
        self.assertEqual(result2, 8)
        
        result3 = self.executor.greet("Alice")
        self.assertEqual(result3, "Hello, Alice!")
    
    def test_action_not_available_error(self) -> None:
        """测试访问不存在的action"""
        with self.assertRaises(AttributeError) as cm:
            _ = self.executor.nonexistent_action
        self.assertIn("Action 'nonexistent_action' 不可用或未被授权", str(cm.exception))
    
    def test_action_wrapper_properties(self) -> None:
        """测试包装的action函数保持原始属性"""
        increment_wrapper = self.executor.increment
        self.assertEqual(increment_wrapper.__name__, 'increment')
        # lambda函数没有文档字符串，所以应该是None
        self.assertIsNone(increment_wrapper.__doc__)
    
    def test_dir_functionality(self) -> None:
        """测试__dir__方法用于自动补全"""
        dir_result = dir(self.executor)
        self.assertIn('increment', dir_result)
        self.assertIn('double', dir_result)
        self.assertIn('greet', dir_result)
    
    def test_repr_method(self) -> None:
        """测试__repr__方法"""
        repr_str = repr(self.executor)
        self.assertIn('ActionExecutor', repr_str)
        self.assertIn('increment', repr_str)
        self.assertIn('double', repr_str)
        self.assertIn('greet', repr_str)


class TestReadOnlyViewActionRegistration(unittest.TestCase):
    """测试ReadOnlyView的action注册功能"""
    
    def setUp(self) -> None:
        """设置测试环境"""
        self.reactive_dict = ReactiveDict({'count': 0, 'name': 'Alice'})
        self.readonly_view = ReadOnlyView(self.reactive_dict)
    
    def test_register_action_with_decorator_no_param(self) -> None:
        """测试使用@config装饰器注册action（不带参数）"""
        @self.readonly_view
        def increment_count():
            current = self.reactive_dict.count
            self.reactive_dict.count = current + 1
            return current + 1
        
        # action应该被注册
        self.assertIn('increment_count', self.readonly_view._allowed_actions)
        
        # 通过ActionExecutor执行action
        executor = self.readonly_view()
        result = executor.increment_count()
        
        self.assertEqual(result, 1)
        self.assertEqual(self.reactive_dict.count, 1)
    
    def test_register_action_with_decorator_with_name(self) -> None:
        """测试使用@config('name')装饰器注册action（带名称）"""
        @self.readonly_view('custom_increment')
        def some_function():
            current = self.reactive_dict.count
            self.reactive_dict.count = current + 10
            return current + 10
        
        # action应该以指定名称被注册
        self.assertIn('custom_increment', self.readonly_view._allowed_actions)
        self.assertNotIn('some_function', self.readonly_view._allowed_actions)
        
        # 执行action
        executor = self.readonly_view()
        result = executor.custom_increment()
        
        self.assertEqual(result, 10)
        self.assertEqual(self.reactive_dict.count, 10)
    
    def test_register_action_direct_function_call(self) -> None:
        """测试直接传入函数注册action"""
        def decrement_count():
            current = self.reactive_dict.count
            self.reactive_dict.count = current - 1
            return current - 1
        
        # 直接注册函数
        returned_func = self.readonly_view(decrement_count)
        self.assertEqual(returned_func, decrement_count)  # 应该返回原函数
        
        # action应该被注册
        self.assertIn('decrement_count', self.readonly_view._allowed_actions)
        
        # 执行action
        self.reactive_dict.count = 5  # 先设置初始值
        executor = self.readonly_view()
        result = executor.decrement_count()
        
        self.assertEqual(result, 4)
        self.assertEqual(self.reactive_dict.count, 4)
    
    def test_lambda_function_registration_error(self) -> None:
        """测试lambda函数直接注册时的错误"""
        with self.assertRaises(TypeError) as cm:
            self.readonly_view(lambda: None)
        self.assertIn("直接使用 @config 注册匿名函数是不允许的", str(cm.exception))
    
    def test_lambda_function_with_name_registration_success(self) -> None:
        """测试lambda函数通过指定名称可以成功注册"""
        decorator = self.readonly_view('lambda_action')
        
        # 创建一个lambda函数并注册
        lambda_func = lambda x: x * 2
        result_func = decorator(lambda_func)
        
        # 应该成功注册并返回原函数
        self.assertEqual(result_func, lambda_func)
        self.assertIn('lambda_action', self.readonly_view._allowed_actions)
        
        # 执行lambda action
        executor = self.readonly_view()
        result = executor.lambda_action(5)
        self.assertEqual(result, 10)
    
    def test_get_action_executor_without_params(self) -> None:
        """测试无参数调用返回ActionExecutor"""
        executor = self.readonly_view()
        self.assertIsInstance(executor, ActionExecutor)
        self.assertEqual(len(executor._allowed_actions), len(self.readonly_view._allowed_actions))
    
    def test_invalid_call_parameter_error(self) -> None:
        """测试无效调用参数的错误"""
        with self.assertRaises(TypeError) as cm:
            self.readonly_view(123)  # 传入非函数非字符串的参数
        self.assertIn("ReadOnlyView 只能以下列方式调用", str(cm.exception))
    
    def test_multiple_actions_registration(self) -> None:
        """测试注册多个action"""
        @self.readonly_view
        def action1():
            return "action1 executed"
        
        @self.readonly_view('custom_action')
        def action2():
            return "action2 executed"
        
        def action3():
            return "action3 executed"
        
        self.readonly_view(action3)
        
        # 所有action都应该被注册
        self.assertIn('action1', self.readonly_view._allowed_actions)
        self.assertIn('custom_action', self.readonly_view._allowed_actions)
        self.assertIn('action3', self.readonly_view._allowed_actions)
        
        # 执行所有action
        executor = self.readonly_view()
        self.assertEqual(executor.action1(), "action1 executed")
        self.assertEqual(executor.custom_action(), "action2 executed")
        self.assertEqual(executor.action3(), "action3 executed")


class TestReadOnlyViewActionIntegration(unittest.TestCase):
    """测试ReadOnlyView的action与响应式系统的集成"""
    
    def setUp(self) -> None:
        """设置测试环境"""
        self.reactive_dict = ReactiveDict({
            'user': {
                'name': 'Alice',
                'score': 0
            },
            'settings': {
                'theme': 'light'
            }
        })
        self.readonly_view = ReadOnlyView(self.reactive_dict)
        self.effect_calls: List[Any] = []
    
    def test_action_triggers_effect(self) -> None:
        """测试action执行会触发effect"""
        # 注册action
        @self.readonly_view
        def increase_score():
            current = self.reactive_dict.user.score
            self.reactive_dict.user.score = current + 10
            return current + 10
        
        # 设置effect监听
        score_ref = self.readonly_view.user.score
        
        @effect
        def watch_score():
            self.effect_calls.append(score_ref.value)
        
        # 手动调用一次以建立响应式连接
        watch_score()
        
        # 初始状态
        self.assertEqual(len(self.effect_calls), 1)
        self.assertEqual(self.effect_calls[0], 0)
        
        # 通过action修改数据
        executor = self.readonly_view()
        result = executor.increase_score()
        
        # effect应该被触发
        self.assertEqual(result, 10)
        self.assertEqual(len(self.effect_calls), 2)
        self.assertEqual(self.effect_calls[1], 10)
    
    def test_action_with_parameters(self) -> None:
        """测试带参数的action"""
        @self.readonly_view('set_name')
        def change_name(new_name: str):
            old_name = self.reactive_dict.user.name
            self.reactive_dict.user.name = new_name
            return f"Changed from {old_name} to {new_name}"
        
        executor = self.readonly_view()
        result = executor.set_name("Bob")
        
        self.assertEqual(result, "Changed from Alice to Bob")
        self.assertEqual(self.reactive_dict.user.name, "Bob")
    
    def test_action_with_complex_logic(self) -> None:
        """测试复杂逻辑的action"""
        @self.readonly_view
        def toggle_theme_and_increase_score():
            # 复杂的action：同时修改多个值
            current_theme = self.reactive_dict.settings.theme
            new_theme = 'dark' if current_theme == 'light' else 'light'
            self.reactive_dict.settings.theme = new_theme
            
            current_score = self.reactive_dict.user.score
            self.reactive_dict.user.score = current_score + 5
            
            return {
                'theme_changed_to': new_theme,
                'score_increased_to': current_score + 5
            }
        
        executor = self.readonly_view()
        result = executor.toggle_theme_and_increase_score()
        
        expected_result = {
            'theme_changed_to': 'dark',
            'score_increased_to': 5
        }
        self.assertEqual(result, expected_result)
        self.assertEqual(self.reactive_dict.settings.theme, 'dark')
        self.assertEqual(self.reactive_dict.user.score, 5)
    
    def test_action_error_handling(self) -> None:
        """测试action中的错误处理"""
        @self.readonly_view
        def failing_action()->None:
            raise ValueError("Intentional test error in action")
        
        executor = self.readonly_view()
        
        # action中的错误应该正常抛出
        with self.assertRaises(ValueError) as cm:
            executor.failing_action()
        self.assertIn("Intentional test error in action", str(cm.exception))
    
    def test_action_isolation_between_views(self) -> None:
        """测试不同视图之间action的隔离"""
        # 创建另一个视图
        another_reactive_dict = ReactiveDict({'counter': 0})
        another_view = ReadOnlyView(another_reactive_dict)
        
        # 在第一个视图注册action
        @self.readonly_view
        def first_view_action():
            return "first view"
        
        # 在第二个视图注册action
        @another_view
        def second_view_action():
            return "second view"
        
        # 各自的action应该是隔离的
        executor1 = self.readonly_view()
        executor2 = another_view()
        
        self.assertEqual(executor1.first_view_action(), "first view")
        self.assertEqual(executor2.second_view_action(), "second view")
        
        # 第一个视图不能访问第二个视图的action
        with self.assertRaises(AttributeError):
            executor1.second_view_action()
        
        # 第二个视图不能访问第一个视图的action
        with self.assertRaises(AttributeError):
            executor2.first_view_action()


if __name__ == '__main__':
    # 运行所有测试
    unittest.main()
