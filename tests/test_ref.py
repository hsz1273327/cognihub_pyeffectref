"""测试 Ref 类的功能"""
import unittest
import threading
import time
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognihub_pyeffectref import Ref, ReadOnlyRef, effect


class TestRef(unittest.TestCase):
    """Ref 类的测试"""

    def test_ref_creation(self) -> None:
        """测试 Ref 创建"""
        ref = Ref(42)
        self.assertEqual(ref.value, 42)

    def test_ref_assignment(self) -> None:
        """测试 Ref 赋值"""
        ref = Ref(10)
        ref.value = 20
        self.assertEqual(ref.value, 20)

    def test_ref_type_annotation(self) -> None:
        """测试类型注解"""
        str_ref: Ref[str] = Ref("hello")
        self.assertEqual(str_ref.value, "hello")
        
        int_ref: Ref[int] = Ref(100)
        self.assertEqual(int_ref.value, 100)

    def test_ref_with_effect(self) -> None:
        """测试 Ref 与 effect 的配合"""
        counter = Ref(0)
        call_count = 0

        @effect
        def track_counter() -> None:
            nonlocal call_count
            call_count += 1
            _ = counter.value  # 建立依赖

        track_counter()
        self.assertEqual(call_count, 1)

        counter.value = 1
        self.assertEqual(call_count, 2)

        counter.value = 2
        self.assertEqual(call_count, 3)

    def test_manual_subscription(self) -> None:
        """测试手动订阅"""
        ref = Ref("initial")
        changes = []

        def on_change(new_val: str, old_val: str) -> None:
            changes.append((old_val, new_val))

        ref.subscribe(on_change)
        ref.value = "changed"
        ref.value = "final"

        self.assertEqual(len(changes), 2)
        self.assertEqual(changes[0], ("initial", "changed"))
        self.assertEqual(changes[1], ("changed", "final"))

    def test_unsubscribe(self) -> None:
        """测试取消订阅"""
        ref = Ref(0)
        call_count = 0

        def callback(new_val: int, old_val: int) -> None:
            nonlocal call_count
            call_count += 1

        ref.subscribe(callback)
        ref.value = 1
        self.assertEqual(call_count, 1)

        ref.unsubscribe(callback)
        ref.value = 2
        self.assertEqual(call_count, 1)  # 应该不再增加

    def test_thread_safety(self) -> None:
        """测试线程安全性"""
        ref = Ref(0)
        
        def worker() -> None:
            for i in range(100):
                current = ref.value
                ref.value = current + 1

        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 由于线程安全的实现，最终值应该是 500
        self.assertEqual(ref.value, 500)

    def test_ref_no_change_no_notify(self) -> None:
        """测试值未改变时不通知"""
        ref = Ref(42)
        call_count = 0

        def callback(new_val: int, old_val: int) -> None:
            nonlocal call_count
            call_count += 1

        ref.subscribe(callback)
        
        # 设置相同的值
        ref.value = 42
        self.assertEqual(call_count, 0)

        # 设置不同的值
        ref.value = 43
        self.assertEqual(call_count, 1)

    def test_ref_repr(self) -> None:
        """测试 __repr__ 方法"""
        ref = Ref("test")
        self.assertEqual(repr(ref), "Ref('test')")
        
        ref_int = Ref(123)
        self.assertEqual(repr(ref_int), "Ref(123)")

    def test_subscriber_type_validation(self) -> None:
        """测试订阅者类型验证"""
        ref = Ref(0)
        
        # 测试无效的订阅者
        with self.assertRaises(TypeError):
            ref.subscribe("not_callable")  # type: ignore

    def test_complex_data_types(self) -> None:
        """测试复杂数据类型"""
        # 测试列表
        list_ref = Ref([1, 2, 3])
        self.assertEqual(list_ref.value, [1, 2, 3])
        
        list_ref.value = [4, 5, 6]
        self.assertEqual(list_ref.value, [4, 5, 6])
        
        # 测试字典
        dict_ref = Ref({"a": 1, "b": 2})
        self.assertEqual(dict_ref.value, {"a": 1, "b": 2})
        
        dict_ref.value = {"c": 3, "d": 4}
        self.assertEqual(dict_ref.value, {"c": 3, "d": 4})

    def test_multiple_subscribers(self) -> None:
        """测试多个订阅者"""
        ref = Ref(0)
        calls = []

        def subscriber1(new_val: int, old_val: int) -> None:
            calls.append(f"sub1: {old_val}->{new_val}")

        def subscriber2(new_val: int, old_val: int) -> None:
            calls.append(f"sub2: {old_val}->{new_val}")

        ref.subscribe(subscriber1)
        ref.subscribe(subscriber2)
        
        ref.value = 5
        
        # 两个订阅者都应该被调用
        self.assertEqual(len(calls), 2)
        self.assertIn("sub1: 0->5", calls)
        self.assertIn("sub2: 0->5", calls)


class TestRefAsync(unittest.IsolatedAsyncioTestCase):
    """Ref 异步测试"""

    async def test_async_effect_basic(self) -> None:
        """测试基本异步 effect"""
        counter = Ref(0)
        call_count = 0

        @effect
        async def async_track_counter() -> None:
            nonlocal call_count
            call_count += 1
            _ = counter.value
            await asyncio.sleep(0.01)

        await async_track_counter()
        self.assertEqual(call_count, 1)

        counter.value = 1
        await asyncio.sleep(0.1)  # 等待异步回调
        self.assertEqual(call_count, 2)

    async def test_mixed_sync_async_effects(self) -> None:
        """测试混合同步异步 effects"""
        data = Ref("initial")
        sync_calls = []
        async_calls = []

        @effect
        def sync_effect() -> None:
            sync_calls.append(data.value)

        @effect
        async def async_effect() -> None:
            async_calls.append(data.value)
            await asyncio.sleep(0.01)

        sync_effect()
        await async_effect()

        self.assertEqual(len(sync_calls), 1)
        self.assertEqual(len(async_calls), 1)

        data.value = "changed"
        await asyncio.sleep(0.1)  # 等待异步回调

        self.assertEqual(len(sync_calls), 2)
        self.assertEqual(sync_calls[1], "changed")
        self.assertEqual(len(async_calls), 2)
        self.assertEqual(async_calls[1], "changed")


class TestReadOnlyRef(unittest.TestCase):
    """ReadOnlyRef 类的测试"""

    def test_readonly_ref_creation(self) -> None:
        """测试 ReadOnlyRef 创建"""
        base_ref = Ref(42)
        readonly_ref: ReadOnlyRef[int] = ReadOnlyRef(base_ref)
        self.assertEqual(readonly_ref.value, 42)

    def test_readonly_ref_invalid_creation(self) -> None:
        """测试 ReadOnlyRef 创建时类型验证"""
        with self.assertRaises(TypeError):
            ReadOnlyRef("not_a_ref")  # type: ignore

    def test_readonly_ref_tracks_changes(self) -> None:
        """测试 ReadOnlyRef 追踪底层 Ref 的变化"""
        base_ref = Ref("initial")
        readonly_ref: ReadOnlyRef[str] = ReadOnlyRef(base_ref)
        
        self.assertEqual(readonly_ref.value, "initial")
        
        # 修改底层 Ref
        base_ref.value = "changed"
        self.assertEqual(readonly_ref.value, "changed")
        
        # 再次修改
        base_ref.value = "final"
        self.assertEqual(readonly_ref.value, "final")

    def test_readonly_ref_no_setter(self) -> None:
        """测试 ReadOnlyRef 不能修改值"""
        base_ref = Ref(10)
        readonly_ref: ReadOnlyRef[int] = ReadOnlyRef(base_ref)
        
        # ReadOnlyRef 不应该有 value.setter
        with self.assertRaises(AttributeError):
            readonly_ref.value = 20  # type: ignore

    def test_readonly_ref_subscription(self) -> None:
        """测试 ReadOnlyRef 的订阅功能"""
        base_ref = Ref(0)
        readonly_ref: ReadOnlyRef[int] = ReadOnlyRef(base_ref)
        changes = []

        def on_change(new_val: int, old_val: int) -> None:
            changes.append((old_val, new_val))

        readonly_ref.subscribe(on_change)
        
        # 通过底层 Ref 修改值
        base_ref.value = 1
        base_ref.value = 2
        
        self.assertEqual(len(changes), 2)
        self.assertEqual(changes[0], (0, 1))
        self.assertEqual(changes[1], (1, 2))

    def test_readonly_ref_with_effect(self) -> None:
        """测试 ReadOnlyRef 与 effect 的配合"""
        base_ref = Ref(0)
        readonly_ref: ReadOnlyRef[int] = ReadOnlyRef(base_ref)
        call_count = 0
        tracked_values = []

        @effect
        def track_readonly() -> None:
            nonlocal call_count
            call_count += 1
            tracked_values.append(readonly_ref.value)

        track_readonly()
        self.assertEqual(call_count, 1)
        self.assertEqual(tracked_values[0], 0)

        # 通过底层 Ref 修改值
        base_ref.value = 5
        self.assertEqual(call_count, 2)
        self.assertEqual(tracked_values[1], 5)

        base_ref.value = 10
        self.assertEqual(call_count, 3)
        self.assertEqual(tracked_values[2], 10)

    def test_readonly_ref_multiple_subscriptions(self) -> None:
        """测试 ReadOnlyRef 的多个订阅"""
        base_ref = Ref("start")
        readonly_ref: ReadOnlyRef[str] = ReadOnlyRef(base_ref)
        calls1 = []
        calls2 = []

        def subscriber1(new_val: str, old_val: str) -> None:
            calls1.append(f"sub1: {old_val}->{new_val}")

        def subscriber2(new_val: str, old_val: str) -> None:
            calls2.append(f"sub2: {old_val}->{new_val}")

        readonly_ref.subscribe(subscriber1)
        readonly_ref.subscribe(subscriber2)
        
        base_ref.value = "middle"
        base_ref.value = "end"
        
        self.assertEqual(len(calls1), 2)
        self.assertEqual(len(calls2), 2)
        self.assertEqual(calls1[0], "sub1: start->middle")
        self.assertEqual(calls1[1], "sub1: middle->end")
        self.assertEqual(calls2[0], "sub2: start->middle")
        self.assertEqual(calls2[1], "sub2: middle->end")

    def test_readonly_ref_repr(self) -> None:
        """测试 ReadOnlyRef 的 __repr__ 方法"""
        base_ref = Ref("test")
        readonly_ref: ReadOnlyRef[str] = ReadOnlyRef(base_ref)
        self.assertEqual(repr(readonly_ref), "ReadOnlyRef('test')")
        
        readonly_ref_int: ReadOnlyRef[int] = ReadOnlyRef(Ref(123))
        self.assertEqual(repr(readonly_ref_int), "ReadOnlyRef(123)")

    def test_readonly_ref_type_preservation(self) -> None:
        """测试 ReadOnlyRef 保持类型一致性"""
        # 测试字符串类型
        str_ref = Ref("hello")
        readonly_str_ref: ReadOnlyRef[str] = ReadOnlyRef(str_ref)
        self.assertEqual(readonly_str_ref.value, "hello")
        
        # 测试整数类型
        int_ref = Ref(42)
        readonly_int_ref: ReadOnlyRef[int] = ReadOnlyRef(int_ref)
        self.assertEqual(readonly_int_ref.value, 42)
        
        # 测试列表类型
        list_ref = Ref([1, 2, 3])
        readonly_list_ref: ReadOnlyRef[list[int]] = ReadOnlyRef(list_ref)
        self.assertEqual(readonly_list_ref.value, [1, 2, 3])
        
        # 修改底层 Ref 并验证类型
        list_ref.value = [4, 5, 6]
        self.assertEqual(readonly_list_ref.value, [4, 5, 6])

    def test_readonly_ref_independent_subscriptions(self) -> None:
        """测试 ReadOnlyRef 和底层 Ref 的独立订阅"""
        base_ref = Ref(0)
        readonly_ref: ReadOnlyRef[int] = ReadOnlyRef(base_ref)
        
        base_calls = []
        readonly_calls = []

        def base_subscriber(new_val: int, old_val: int) -> None:
            base_calls.append(f"base: {old_val}->{new_val}")

        def readonly_subscriber(new_val: int, old_val: int) -> None:
            readonly_calls.append(f"readonly: {old_val}->{new_val}")

        # 分别订阅
        base_ref.subscribe(base_subscriber)
        readonly_ref.subscribe(readonly_subscriber)
        
        base_ref.value = 1
        
        # 两个订阅都应该被触发
        self.assertEqual(len(base_calls), 1)
        self.assertEqual(len(readonly_calls), 1)
        self.assertEqual(base_calls[0], "base: 0->1")
        self.assertEqual(readonly_calls[0], "readonly: 0->1")


class TestReadOnlyRefAsync(unittest.IsolatedAsyncioTestCase):
    """ReadOnlyRef 异步测试"""

    async def test_readonly_ref_async_effect(self) -> None:
        """测试 ReadOnlyRef 与异步 effect 的配合"""
        base_ref = Ref(0)
        readonly_ref: ReadOnlyRef[int] = ReadOnlyRef(base_ref)
        call_count = 0
        tracked_values = []

        @effect
        async def async_track_readonly() -> None:
            nonlocal call_count
            call_count += 1
            tracked_values.append(readonly_ref.value)
            await asyncio.sleep(0.01)

        await async_track_readonly()
        self.assertEqual(call_count, 1)
        self.assertEqual(tracked_values[0], 0)

        base_ref.value = 5
        await asyncio.sleep(0.1)  # 等待异步回调
        self.assertEqual(call_count, 2)
        self.assertEqual(tracked_values[1], 5)

    async def test_readonly_ref_async_subscription(self) -> None:
        """测试 ReadOnlyRef 的异步订阅"""
        base_ref = Ref("initial")
        readonly_ref: ReadOnlyRef[str] = ReadOnlyRef(base_ref)
        async_calls = []

        async def async_subscriber(new_val: str, old_val: str) -> None:
            async_calls.append(f"async: {old_val}->{new_val}")
            await asyncio.sleep(0.01)

        readonly_ref.subscribe(async_subscriber)
        
        base_ref.value = "changed"
        await asyncio.sleep(0.1)  # 等待异步回调
        
        self.assertEqual(len(async_calls), 1)
        self.assertEqual(async_calls[0], "async: initial->changed")


if __name__ == '__main__':
    unittest.main()
