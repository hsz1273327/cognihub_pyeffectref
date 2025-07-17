import asyncio
import cognihub_pyeffectref.local as local
from typing import Callable, Any


class EffectWrapper:
    """
    封装 effect 函数，提供 __call__ 使其可调用，并管理其 stop 行为。
    """

    def __init__(self, func: Callable, is_async: bool):
        self._func = func
        self._is_async = is_async
        self._is_active = True  # 控制 effect 是否应该执行

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not self._is_active:
            # 如果 effect 已停止，则不执行
            return

        if self._is_async:
            return self._run_async_effect(*args, **kwargs)
        else:
            return self._run_sync_effect(*args, **kwargs)

    def _run_sync_effect(self, *args: Any, **kwargs: Any) -> Any:
        old_effect = getattr(local._thread_local_current_effect, 'value', None)
        local._thread_local_current_effect.value = self  # 设置线程局部变量为自身实例

        try:
            return self._func(*args, **kwargs)
        finally:
            local._thread_local_current_effect.value = old_effect  # 恢复线程局部变量

    async def _run_async_effect(self, *args: Any, **kwargs: Any) -> Any:
        token = local._async_local_current_effect.set(self)  # 设置 contextvar 为自身实例
        try:
            return await self._func(*args, **kwargs)
        finally:
            local._async_local_current_effect.reset(token)  # 恢复 contextvar

    def stop(self) -> None:
        """停止这个 effect,使其不再响应 Ref 变化。"""
        self._is_active = False
        # 在这里，如果 Ref 内部存储的是 EffectWrapper 实例，
        # 则可以遍历 Ref 的 _subscribers 并移除 self。
        # 但这需要 Ref 暴露一个 API 或 EffectWrapper 持有 Ref 的引用，
        # 为了简化，我们只设置 _is_active。
        print(f"Effect '{self._func.__name__}' stopped.")

    @property
    def name(self) -> str:
        return self._func.__name__ + ("_async" if self._is_async else "_sync")

# --- 2. 装饰器 factory，返回一个 EffectWrapper 实例 ---
def effect(func: Callable) -> EffectWrapper:
    """
    一个通用的装饰器，返回一个 EffectWrapper 实例。
    """
    is_async = asyncio.iscoroutinefunction(func)
    return EffectWrapper(func, is_async)
