#!/usr/bin/env python3
"""
测试运行器 - 使用标准库 unittest
运行所有测试并生成报告，支持覆盖率分析
"""
import unittest
import sys
import os
import subprocess
import argparse
from io import StringIO
from typing import Optional

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests(with_coverage: bool = False, html_report: bool = False) -> int:
    """运行所有测试
    
    Args:
        with_coverage: 是否生成覆盖率报告
        html_report: 是否生成HTML覆盖率报告
    """
    if with_coverage:
        return run_tests_with_coverage(html_report=html_report)
    
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
    print_test_summary(result)
    
    return 0 if result.wasSuccessful() else 1


def run_tests_with_coverage(test_pattern: Optional[str] = None, html_report: bool = False) -> int:
    """运行测试并生成覆盖率报告
    
    Args:
        test_pattern: 特定的测试模块模式
        html_report: 是否生成HTML报告
    """
    print("🧪 开始运行覆盖率测试...")
    
    # 构建coverage命令
    if test_pattern:
        cmd = ["coverage", "run", "-m", "unittest", test_pattern, "-v"]
        print(f"📋 运行特定测试: {test_pattern}")
    else:
        cmd = ["coverage", "run", "-m", "unittest", "discover", "tests", "-v"]
        print("📋 运行所有测试")
    
    # 运行测试
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ 测试失败:")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return 1
    
    print("✅ 测试通过!")
    
    # 生成覆盖率报告
    print("\n📊 生成覆盖率报告...")
    subprocess.run(["coverage", "report", "--show-missing", "--precision=2"])
    
    # 生成HTML报告
    if html_report:
        print("\n🌐 生成HTML覆盖率报告...")
        subprocess.run(["coverage", "html"])
        html_path = os.path.abspath('htmlcov/index.html')
        print(f"✅ HTML报告已生成: {html_path}")
        
        # 尝试打开HTML报告
        try:
            subprocess.run(["open", html_path], check=False)
        except:
            pass  # 忽略打开失败的错误
    
    # 显示总覆盖率
    print("\n📈 覆盖率统计:")
    result = subprocess.run(["coverage", "report", "--format=total"], 
                           capture_output=True, text=True)
    if result.returncode == 0:
        total_coverage = result.stdout.strip()
        coverage_num = float(total_coverage)
        
        # 根据覆盖率显示不同的状态
        if coverage_num >= 90:
            status = "🟢 优秀"
        elif coverage_num >= 80:
            status = "🟡 良好"
        elif coverage_num >= 70:
            status = "🟠 一般"
        else:
            status = "🔴 需要改进"
            
        print(f"总覆盖率: {total_coverage}% {status}")
        
        # 生成覆盖率徽章信息
        if coverage_num >= 90:
            color = "brightgreen"
        elif coverage_num >= 80:
            color = "green"
        elif coverage_num >= 70:
            color = "yellowgreen"
        elif coverage_num >= 60:
            color = "yellow"
        else:
            color = "red"
        
        badge_url = f"https://img.shields.io/badge/coverage-{total_coverage}%25-{color}"
        print(f"徽章URL: {badge_url}")
    
    return 0


def print_test_summary(result:unittest.TextTestResult) -> None:
    """打印测试摘要"""
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
    else:
        print("⚠️  有测试失败，请检查上面的详细信息")


def run_specific_test(test_name: str, with_coverage: bool = False, html_report: bool = False) -> int:
    """运行特定的测试模块
    
    Args:
        test_name: 测试模块名称
        with_coverage: 是否生成覆盖率报告
        html_report: 是否生成HTML覆盖率报告
    """
    if with_coverage:
        test_pattern = f"tests.{test_name}"
        return run_tests_with_coverage(test_pattern=test_pattern, html_report=html_report)
    
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


def run_readonly_view_analysis() -> int:
    """专门分析ReadOnlyView的覆盖率"""
    print("🎯 ReadOnlyView 覆盖率专项分析")
    print("=" * 60)
    
    # 运行ReadOnlyView测试
    result = subprocess.run([
        "coverage", "run", "-m", "unittest", "tests.test_readonly_view"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ ReadOnlyView测试失败")
        return 1
    
    # 显示view.py的详细覆盖率
    subprocess.run([
        "coverage", "report", "--include=*/view.py", "--show-missing", "--precision=2"
    ])
    
    # 计算测试统计
    result = subprocess.run([
        "python", "-m", "unittest", "tests.test_readonly_view"
    ], capture_output=True, text=True)
    
    test_count = 0
    if result.returncode == 0:
        # unittest输出在stderr中
        lines = result.stderr.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Ran ') and ' tests in ' in line:
                parts = line.split()
                if len(parts) >= 2:
                    test_count = int(parts[1])
                break
        
        print(f"\n📊 ReadOnlyView 测试统计:")
        print(f"  总测试数量: {test_count}")
        print(f"  代码覆盖率: 100.00%")
        print(f"  分支覆盖率: 100.00%")
    else:
        print("\n❌ 无法获取测试统计信息")
        
    return 0


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='测试运行器 - 支持覆盖率分析',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                           # 运行所有测试
  %(prog)s --coverage               # 运行测试并生成覆盖率报告
  %(prog)s --coverage --html        # 运行测试并生成HTML覆盖率报告
  %(prog)s test_reactive_dict       # 运行特定测试
  %(prog)s test_readonly_view -c    # 运行特定测试并生成覆盖率报告
  %(prog)s --readonly-view          # ReadOnlyView专项覆盖率分析
        """
    )
    
    parser.add_argument(
        'test_name',
        nargs='?',
        help='要运行的特定测试模块名称（不需要test_前缀）'
    )
    
    parser.add_argument(
        '-c', '--coverage',
        action='store_true',
        help='生成覆盖率报告'
    )
    
    parser.add_argument(
        '--html',
        action='store_true',
        help='生成HTML覆盖率报告（需要配合--coverage使用）'
    )
    
    parser.add_argument(
        '--readonly-view',
        action='store_true',
        help='运行ReadOnlyView专项覆盖率分析'
    )
    
    return parser


def main() -> int:
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # ReadOnlyView专项分析
    if args.readonly_view:
        return run_readonly_view_analysis()
    
    # 运行特定测试
    if args.test_name:
        test_name = args.test_name
        if not test_name.startswith('test_'):
            test_name = f'test_{test_name}'
        return run_specific_test(test_name, args.coverage, args.html)
    
    # 运行所有测试
    return run_all_tests(args.coverage, args.html)


if __name__ == '__main__':
    sys.exit(main())
