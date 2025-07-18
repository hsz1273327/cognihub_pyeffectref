#!/usr/bin/env python3
"""
测试运行器 - 使用标准库 unittest
运行所有测试并生成报告
"""
import unittest
import sys
import os
from io import StringIO

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests() -> int:
    """运行所有测试"""
    # 发现并加载所有测试
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')

    # 创建测试运行器
    stream = StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2,
        descriptions=True,
        failfast=False
    )

    # 运行测试
    print("🧪 开始运行测试...")
    result = runner.run(suite)

    # 输出结果
    output = stream.getvalue()
    print(output)

    # 生成摘要
    print("\n" + "=" * 50)
    print("📊 测试摘要")
    print("=" * 50)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")

    # 显示失败的测试
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")

    # 显示错误的测试
    if result.errors:
        print("\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")
            print(f"    {traceback.split('Exception:')[-1].strip()}")

    # 返回结果
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n✅ 成功率: {success_rate:.1f}%")

    if result.wasSuccessful():
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️  有测试失败，请检查上面的详细信息")
        return 1


def run_specific_test(test_name: str) -> int:
    """运行特定的测试模块"""
    try:
        # 导入测试模块
        module = __import__(f'tests.{test_name}', fromlist=[test_name])

        # 创建测试套件
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)

        # 运行测试
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return 0 if result.wasSuccessful() else 1

    except ImportError as e:
        print(f"❌ 无法导入测试模块 '{test_name}': {e}")
        return 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 运行特定测试
        test_name = sys.argv[1]
        if not test_name.startswith('test_'):
            test_name = f'test_{test_name}'
        exit_code = run_specific_test(test_name)
    else:
        # 运行所有测试
        exit_code = run_all_tests()

    sys.exit(exit_code)
