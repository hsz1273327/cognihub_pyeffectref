"""ReadOnlyView的测试文件"""
import unittest
import asyncio
import sys
import os
from typing import Any, List

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognihub_pyeffectref.reactive_dict import ReactiveDict
from cognihub_pyeffectref.view import ReadOnlyView
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
        self.assertIn("没有属性 'nonexistent'", str(cm.exception))

    def test_nonexistent_key_error(self) -> None:
        """测试访问不存在的键"""
        with self.assertRaises(AttributeError) as cm:
            _ = self.readonly_view['nonexistent']
        self.assertIn("没有属性 'nonexistent'", str(cm.exception))

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
        self.assertIn("只读的,不允许设置属性 'name'", str(cm.exception))
    
    def test_cannot_set_item(self) -> None:
        """测试不能通过字典风格设置属性"""
        with self.assertRaises(TypeError) as cm:
            self.readonly_view['name'] = 'Bob'
        self.assertIn("只读的,不允许通过键设置项", str(cm.exception))
    
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
        # 访问深层嵌套的数据
        theme_ref = self.readonly_view.user.profile.settings.theme  # type: ignore
        self.assertIsInstance(theme_ref, ReadOnlyRef)
        self.assertEqual(theme_ref.value, 'dark')
        
        # 修改数据并验证响应式更新
        self.reactive_dict.user.profile.settings.theme = 'light'
        self.assertEqual(theme_ref.value, 'light')

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


if __name__ == '__main__':
    unittest.main()
