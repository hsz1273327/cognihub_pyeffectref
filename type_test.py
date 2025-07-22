#!/usr/bin/env python3
"""简单的类型推断测试"""

from typing import TypedDict
from cognihub_pyeffectref import ReactiveDict, ReadOnlyView

class UserSchema(TypedDict):
    name: str
    age: int
    score: float
    active: bool

# 创建测试数据
user_data = ReactiveDict({
    'name': '张三',
    'age': 25,
    'score': 95.5,
    'active': True
}, schema=UserSchema)

# 创建只读视图
user_view = ReadOnlyView(user_data, schema=UserSchema)

# 演示改进后的类型推断
def demonstrate_type_inference():
    """演示 MyPy 现在能够更好地推断类型"""
    
    # 1. 直接访问 .value，MyPy 现在应该能推断出正确的类型
    total: int = user_view.age.value  # 这里不再需要显式类型标注!
    name: str = user_view.name.value  # MyPy 应该能够推断这是 str
    score: float = user_view.score.value  # MyPy 应该能够推断这是 float
    active: bool = user_view.active.value  # MyPy 应该能够推断这是 bool
    
    # 2. 进行类型安全的操作
    next_year = total + 1  # int + int
    upper_name = name.upper()  # str.upper()
    rounded_score = round(score)  # round(float)
    negated_active = not active  # not bool
    
    print(f"名字: {name} -> {upper_name}")
    print(f"年龄: {total} -> {next_year}")
    print(f"分数: {score} -> {rounded_score}")
    print(f"活跃: {active} -> {negated_active}")
    
    return total, name, score, active

if __name__ == "__main__":
    demonstrate_type_inference()
    print("✅ 类型推断测试完成！")



"""各种帮助函数.

这些函数用于处理函数列表转换为字典,以及从数据推断 TypedDict Schema.
"""
import warnings
from typing import Callable, Any, TypedDict, Type, Optional


def create_actions_dict(
    functions: list[Callable[..., Any]]
) -> dict[str, Callable[..., Any]]:
    """将一个函数列表转换为一个字典.

    其中键是函数名,值是函数本身.

    注意匿名函数不被支持

    此函数不执行任何类型或名称校验,假设所有函数都是有效的.
    """
    def is_valid_function(func: Any) -> tuple[bool, Optional[str]]:
        """检查函数是否有效,返回 (是否有效, 错误信息)"""
        if not callable(func):
            return False, f"对象 '{func}' 不是可调用对象,已跳过."

        if not hasattr(func, '__name__') or not func.__name__ or func.__name__ == '<lambda>':
            return False, f"对象 '{func}' 匿名,已跳过."

        return True, None

    result: dict[str, Callable[..., Any]] = {}
    for func in functions:
        is_valid, error_msg = is_valid_function(func)
        if not is_valid and error_msg:
            warnings.warn(
                error_msg,
                UserWarning,
                stacklevel=2
            )
            continue
        result[func.__name__] = func
    return result


# ---  ---


def infer_schema_from_data(
    data: dict[str, Any],
    type_name: str = "InferredSchema",
    _schema_cache: Optional[dict[str, Type[TypedDict]]] = None  # type: ignore
) -> Type[TypedDict]:  # type: ignore
    """动态 Schema 推断函数.

    从字典数据中递归推断并创建 TypedDict Schema.

    Args:
        data: 要推断 schema 的字典数据
        type_name: 生成的 TypedDict 类型名称
        _schema_cache: 内部使用的缓存,避免重复推断相同结构

    Returns:
        动态生成的 TypedDict 类型

    局限性：
        - 无法推断 Literal, Union 等复杂类型.
        - 列表元素类型推断:默认推断为列表中第一个非None元素的类型,或Any.
        - 空字典/列表的推断:默认推断为 Dict[str, Any] 或 List[Any].
    """
    if _schema_cache is None:
        _schema_cache = {}

    # 生成缓存键用于避免重复推断相同结构
    cache_key = _generate_cache_key(data)
    if cache_key in _schema_cache:
        return _schema_cache[cache_key]

    annotations: dict[str, Any] = {}

    for key, value in data.items():
        annotations[key] = _infer_field_type(value, type_name, key, _schema_cache)

    # 使用 type() 函数动态创建 TypedDict
    # total=False 表示所有字段都是可选的,这在推断时更安全
    dynamic_typed_dict = TypedDict(type_name, annotations, total=False)  # type: ignore
    _schema_cache[cache_key] = dynamic_typed_dict
    return dynamic_typed_dict


def _generate_cache_key(data: dict[str, Any]) -> str:
    """生成数据结构的缓存键"""
    def get_structure(obj: Any) -> str:
        if isinstance(obj, dict):
            # 对于字典,生成键和值类型的字符串表示
            items = []
            for k, v in sorted(obj.items()):
                items.append(f"{k}:{get_structure(v)}")
            return f"dict({','.join(items)})"
        elif isinstance(obj, list):
            if not obj:
                return "list(empty)"
            # 取前几个元素的类型结构
            sample_size = min(3, len(obj))
            structures = [get_structure(obj[i]) for i in range(sample_size)]
            return f"list({','.join(set(structures))})"
        else:
            return type(obj).__name__

    return get_structure(data)


def _infer_field_type(
    value: Any,
    type_name: str,
    key: str,
    schema_cache: dict[str, Type[TypedDict]]  # type: ignore
) -> Any:
    """推断单个字段的类型"""
    if isinstance(value, dict):
        if not value:
            # 空字典推断为 Dict[str, Any]
            return dict[str, Any]
        # 递归推断嵌套字典的 Schema
        return infer_schema_from_data(
            value,
            f"{type_name}_{key.capitalize()}",
            schema_cache
        )
    elif isinstance(value, list):
        return _infer_list_type(value, type_name, key, schema_cache)
    else:
        # 基本类型直接使用其 Python 类型
        return type(value)