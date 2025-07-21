# CogniHub PyEffectRef

![Coverage](https://img.shields.io/badge/coverage-77.9%25-yellowgreen)
![Tests](https://img.shields.io/badge/tests-121%20passing-brightgreen)

一个类似Vue 3组合式API的Python响应式编程库。

## 测试覆盖率 🎯

我们的代码拥有全面的测试覆盖率：

### 总体覆盖率
- **总覆盖率**: 77.89% (363行代码)
- **测试数量**: 121个测试用例
- **所有测试**: ✅ 通过

### 模块级别覆盖率

| 模块 | 覆盖率 | 状态 | 说明 |
|------|--------|------|------|
| `__init__.py` | 100.00% | ✅ | 模块入口 |
| `view.py` | **100.00%** | ✅ | ReadOnlyView系统 |
| `effect.py` | 95.38% | ✅ | Effect响应式系统 |
| `reactive_dict.py` | 94.96% | ✅ | ReactiveDict核心 |
| `local.py` | 77.78% | 🔶 | Local Storage |
| `ref.py` | 54.42% | 🔶 | Ref系统 |

### 核心功能测试

#### ReadOnlyView (100% 覆盖率)
- ✅ 39个测试用例
- ✅ 基本视图功能测试 (7个)
- ✅ 只读行为测试 (4个)
- ✅ 响应式行为测试 (3个)
- ✅ 异步行为测试 (1个)
- ✅ 复杂场景测试 (5个)
- ✅ ActionExecutor测试 (6个)
- ✅ Action注册测试 (8个)
- ✅ Action集成测试 (5个)

#### ReactiveDict (94.96% 覆盖率)
- ✅ 24个测试用例
- ✅ 基本功能测试
- ✅ 响应式行为测试
- ✅ 异步操作测试
- ✅ 错误处理测试

## 运行测试

### 运行所有测试
```bash
python -m unittest discover tests
```

### 运行覆盖率分析
```bash
# 完整覆盖率分析
python analyze_coverage.py

# ReadOnlyView专项分析
python analyze_coverage.py readonly_view

# 生成覆盖率徽章
python analyze_coverage.py badge
```

### 查看HTML覆盖率报告
```bash
# 生成HTML报告后在浏览器中打开
open htmlcov/index.html
```

## 功能特性

### ReadOnlyView - 完全覆盖 ✅
- 🔒 **只读访问**: 防止意外修改状态
- 🎯 **Action系统**: 通过注册的action安全修改状态
- 📱 **响应式更新**: 自动响应底层数据变化
- 🛡️ **类型安全**: 完整的类型注解支持
- 🔧 **灵活注册**: 支持装饰器、函数参数、lambda等多种注册方式

### ActionExecutor
- 🎮 **控制访问**: 只允许执行注册的action
- 🔍 **自动补全**: 支持IDE自动补全
- 📝 **调试友好**: 详细的执行日志
- ⚡ **高性能**: 优化的action查找和执行

### ReactiveDict
- 🔄 **自动响应**: 数据变化自动触发effect
- 📊 **深度监听**: 支持嵌套对象的响应式
- 🚀 **异步支持**: 完整的async/await支持

## 质量保证

- ✅ **121个测试用例**全部通过
- ✅ **77.89%**的总体覆盖率
- ✅ **100%**的核心模块覆盖率
- ✅ 完整的类型注解
- ✅ 全面的错误处理测试
- ✅ 异步功能测试
