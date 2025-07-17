import threading
import asyncio
import cognihub_pyeffectref.local as local
from typing import Callable, Generic, TypeVar
# --- 1. 定义线程局部和上下文变量来存储当前的 effect ---

T = TypeVar('T')


class Ref(Generic[T]):
    """
    一个通用的响应式数据容器，同时支持异步和多线程安全。
    当其值改变时，会通知所有订阅者。
    """

    def __init__(self, initial_value: T) -> None:
        self._value = initial_value
        # 使用 threading.Lock 来保护 _subscribers 集合的并发修改
        self._subscribers_lock = threading.Lock()
        self._subscribers: set[Callable[[T, T], None]] = set()  # 存储订阅此Ref的副作用函数或回调

    def __repr__(self) -> str:
        return f"Ref({repr(self._value)})"

    @property
    def value(self) -> T:
        """
        获取Ref的值。
        根据当前执行环境（同步线程或异步协程）获取 effect,并进行依赖收集。
        """
        current_effect = None
        # 优先从 asyncio contextvar 获取（如果在 asyncio 环境中）
        if asyncio.current_task(None):  # 检查是否在 asyncio 任务中
            current_effect = local._async_local_current_effect.get()
        # 否则尝试从 threading.local 获取 (普通线程中)
        else:
            current_effect = getattr(local._thread_local_current_effect, 'value', None)  # 使用 .value 约定

        if current_effect:
            with self._subscribers_lock:
                self._subscribers.add(current_effect)
        return self._value

    @value.setter
    def value(self, new_value: T) -> None:
        """
        设置Ref的值。
        如果新旧值不同，则更新值并通知所有订阅者。
        """
        if self._value != new_value:
            old_value = self._value
            self._value = new_value
            self._notify_subscribers(old_value, new_value)

    def subscribe(self, callback_func: Callable[[T, T], None]) -> None:
        if not callable(callback_func):
            raise TypeError("Subscriber must be a callable function.")
        with self._subscribers_lock:
            self._subscribers.add(callback_func)

    def unsubscribe(self, callback_func: Callable[[T, T], None]) -> None:
        with self._subscribers_lock:
            self._subscribers.discard(callback_func)

    def _notify_subscribers(self, old_value: T, new_value: T) -> None:
        """
        通知所有订阅者值已改变。
        异步回调会被调度，同步回调会直接执行。
        """
        subscribers_to_notify = []
        with self._subscribers_lock:
            subscribers_to_notify = list(self._subscribers)  # 获取副本进行迭代

        for callback in subscribers_to_notify:
            try:
                if asyncio.iscoroutinefunction(callback):
                    # 如果当前在 asyncio 事件循环中，调度异步回调
                    try:
                        loop = asyncio.get_running_loop()
                        loop.call_soon_threadsafe(lambda: asyncio.create_task(callback(new_value, old_value)))
                    except RuntimeError:  # 如果不在运行中的循环，则无法调度，直接报错或警告
                        print(f"[ERROR] Cannot schedule async callback {callback.__name__} outside of an asyncio event loop.")
                else:
                    # 同步回调直接执行
                    callback(new_value, old_value)
            except Exception as e:
                print(f"[ERROR] Error notifying subscriber {getattr(callback, '__name__', str(callback))}: {e}")
