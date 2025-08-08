import asyncio
from cognihub_pyeffectref import effect, Ref
a = Ref(1)
b = Ref(2)


@effect
def my_effect(c: int) -> int:
    # 这里是效果的逻辑
    print(f"Effect triggered with value: a:{a.value} b:{b.value} c:{c}")
    return a.value + b.value + c


@a.subscribe
def a_change_handler(old_value: int, new_value: int) -> None:
    print(f"a changed from {old_value} to {new_value}")


my_effect(3)  # 手动调用 effect,传入 c 的值

a.value = 10  # 修改 a 的值,触发 effect
b.value = 20  # 修改 b 的值,触发 effect
my_effect(5)  # 再次手动调用 effect,传入新的 c
print(my_effect.name)  # 打印 effect 的名称
a.value = 100  # 修改 a 的值,触发 effect
b.value = 200  # 修改 b 的值,触发 effect


aa = Ref(1)
ab = Ref(2)


@effect
async def aiomy_effect(c: int) -> int:
    # 这里是效果的逻辑
    print(f"Effect triggered with value: aa:{aa.value} ab:{ab.value} c:{c}")
    await asyncio.sleep(0.1)
    print(f"after wait Effect triggered with value: aa:{aa.value} ab:{ab.value} c:{c}")
    return aa.value + ab.value + c


@aa.subscribe
async def aa_change_handler(old_value: int, new_value: int) -> None:
    print(f"aa changed from {old_value} to {new_value}")


async def main() -> None:
    await aiomy_effect(3)  # 手动调用 effect,传入 c 的值

    aa.value = 10  # 修改 a 的值,触发 effect
    ab.value = 20  # 修改 b 的值,触发 effect
    await aiomy_effect(5)  # 再次手动调用 effect,传入新的 c
    print(aiomy_effect.name)  # 打印 effect 的名称
    aa.value = 100  # 修改 a 的值,触发 effect
    ab.value = 200  # 修改 b 的值,触发 effect

if __name__ == "__main__":
    asyncio.run(main())