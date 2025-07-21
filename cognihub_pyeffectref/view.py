"""ReactiveDict的视图"""
from cognihub_pyeffectref.ref import ReadOnlyRef
from cognihub_pyeffectref.reactive_dict import ReactiveDict
from typing import Any, Dict, NoReturn, Union, Callable, Optional


class ActionExecutor:
    """当 view()不带参数调用时返回的对象。
    允许通过点语法执行已注册的 action(例如 config().action_name()).
    """

    def __init__(self, allowed_actions: Dict[str, Callable[..., Any]]):
        self._allowed_actions = allowed_actions

    def __getattr__(self, name: str) -> Callable[..., Any]:
        """允许通过点语法调用 action。"""
        if name in self._allowed_actions:
            # 包装原始函数以确保调用时行为正确
            def action_wrapper(*args: Any, **kwargs: Any) -> Any:
                print(f"[ActionExecutor] 执行 action '{name}'...")
                return self._allowed_actions[name](*args, **kwargs)
            # 确保包装函数的 __doc__ 和 __name__ 匹配原始函数
            action_wrapper.__doc__ = self._allowed_actions[name].__doc__
            action_wrapper.__name__ = name
            return action_wrapper
        raise AttributeError(f"Action '{name}' 不可用或未被授权。")

    def __dir__(self) -> list[str]:
        """用于 Tab 自动补全和 dir()。"""
        return list(super().__dir__()) + list(self._allowed_actions.keys())

    def __repr__(self) -> str:
        return f"ActionExecutor(可用 action={list(self._allowed_actions.keys())})"


class ReadOnlyView:
    """提供 ReactiveDict 的只读视图.

    插件使用此视图.当访问叶子节点时,返回 ReadOnlyRef.
    当访问嵌套的 ReactiveDict 时,返回 ReadOnlyView.
    """

    def __init__(self, reactive_dict: ReactiveDict):
        self._reactive_dict = reactive_dict
        # _allowed_actions 现在直接存储函数，用于此特定实例
        self._allowed_actions: Dict[str, Callable[..., Any]] = {}

    def __getattr__(self, name: str) -> Union['ReadOnlyView', ReadOnlyRef]:
        """
        通过点语法访问属性.
        如果结果是嵌套的 ReactiveDict,则返回 ReadOnlyView.
        如果结果是叶子 Ref,则返回 ReadOnlyRef.
        否则返回原始值.
        """
        if name not in self._reactive_dict._data_refs:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        # 获取底层 ReactiveDict 中对应的 Ref
        target_ref = self._reactive_dict._data_refs[name]
        value_in_ref = target_ref.value

        if isinstance(value_in_ref, ReactiveDict):
            # 如果是嵌套的 ReactiveDict,递归返回 ReadOnlyView
            return ReadOnlyView(value_in_ref)
        else:
            # 如果是叶子节点 Ref,返回 ReadOnlyRef
            return ReadOnlyRef(target_ref)

    def __getitem__(self, key: str) -> Union['ReadOnlyView', ReadOnlyRef]:
        """
        通过字典风格访问属性.
        逻辑同 __getattr__.
        """
        if key not in self._reactive_dict._data_refs:
            raise KeyError(f"'{key}' not found in ReadOnlyView.")

        target_ref = self._reactive_dict._data_refs[key]
        value_in_ref = target_ref.value

        if isinstance(value_in_ref, ReactiveDict):
            return ReadOnlyView(value_in_ref)
        else:
            return ReadOnlyRef(target_ref)

    def __setattr__(self, name: str, value: Any) -> None:
        # 严格禁止在只读视图上进行设置
        if name.startswith('_'):  # 允许设置视图自身的私有属性
            super().__setattr__(name, value)
        else:
            raise AttributeError(f"Cannot modify attribute '{name}' on a read-only view.")

    def __setitem__(self, key: str, value: Any) -> NoReturn:
        # 严格禁止在只读视图上进行设置
        raise TypeError(f"Cannot set item '{key}' on a read-only view.")

    def to_dict(self) -> Dict[str, Any]:
        """将当前状态转换为普通字典(调用时拷贝)."""
        return self._reactive_dict.to_dict()


    def __call__(self, func: Optional[ Union[str,Callable[..., Any]]]=None) -> Union[Callable[[Callable[..., Any]], Callable[..., Any]], 'ActionExecutor']:
        """根据调用方式处理 action 注册或返回 ActionExecutor.

        行为模式：
        1. config(): 返回 ActionExecutor 实例。
        2. config(func): 注册 func,使用 func.__name__ 作为 action 名.
                        如果 func 是匿名函数，会报错，因为它没有有意义的 __name__.
        3. config("action_name"): 返回一个内部装饰器，该装饰器将接收函数并注册为 'action_name'.
        """
        # 案例 1：config() -> 返回 ActionExecutor
        if func is None:
            return ActionExecutor(self._allowed_actions)
        else:
            # 尝试处理注册逻辑
            # 案例 2：config(func) 或 @config
            if callable(func):
                action_name = func.__name__
                if action_name == '<lambda>':
                    raise TypeError(
                        "直接使用 @config 注册匿名函数是不允许的,请使用 @config('action_name') 形式为匿名函数指定名称."
                    )
                self._allowed_actions[action_name] = func
                return func
            else:

                # 案例 3：config("action_name") 或 @config("action_name")
                if isinstance(func, str):
                    action_name_str = func
                    def decorator_with_name(func: Callable[..., Any]) -> Callable[..., Any]:
                        # if func.__name__ == '<lambda>':
                        #     raise TypeError(
                        #         "匿名函数不能直接注册为 action,请使用 @config('action_name') 形式为匿名函数指定名称."
                        #     )
                        self._allowed_actions[action_name_str] = func
                        return func
                    return decorator_with_name  # 返回一个接受函数并注册它的装饰器
                else:
                    # 如果走到这里，说明调用方式不符合预期
                    raise TypeError(
                        "ReadOnlyView 只能以下列方式调用：\n"
                        "1. config() -> 获取 action 执行器。\n"
                        "2. @config def my_action(): ... -> 注册一个名为 'my_action' 的 action。\n"
                        "3. @config('custom_name') def my_func_or_lambda(): ... -> 注册一个带指定名称的 action。"
                    )
