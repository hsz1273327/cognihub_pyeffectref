# CogniHub PyEffectRef 示例集合

这个目录包含了 CogniHub PyEffectRef 库的完整示例集合，演示了响应式编程的各种用法和最佳实践。

## 📁 示例文件列表

### ✅ 已完成的示例

1. **[basic_ref.py](./basic_ref.py)** - Ref 基础示例
   - Ref 的创建和使用
   - 订阅和取消订阅机制
   - 多订阅者场景
   - 复杂类型的 Ref 使用

2. **[effect_basics.py](./effect_basics.py)** - Effect 基础示例
   - Effect 的基本用法
   - 依赖追踪机制
   - Effect 清理功能
   - 条件性 Effect
   - 错误处理和性能考虑

3. **[reactive_dict_basic.py](./reactive_dict_basic.py)** - ReactiveDict 基础示例
   - ReactiveDict 基本操作
   - 与 Effect 的配合使用
   - 嵌套数据结构
   - 购物车和表单验证场景

4. **[readonly_view_example.py](./readonly_view_example.py)** - ReadOnlyView 示例
   - 只读视图的创建和使用
   - 配置管理场景
   - 仪表板数据展示
   - 权限系统实现

## 🚀 运行示例

### 运行单个示例

```bash
# 运行 Ref 基础示例
python examples/basic_ref.py

# 运行 Effect 基础示例
python examples/effect_basics.py

# 运行 ReactiveDict 基础示例
python examples/reactive_dict_basic.py

# 运行 ReadOnlyView 示例
python examples/readonly_view_example.py
```

### 运行所有示例

```bash
# 运行所有已完成的示例
for file in examples/*.py; do
    if [[ "$file" != *"__"* ]]; then
        echo "========== Running $file =========="
        python "$file"
        echo ""
    fi
done
```

## 📖 学习路径

建议按以下顺序学习示例：

1. **开始** → `basic_ref.py` - 了解响应式编程的基础概念
2. **进阶** → `effect_basics.py` - 学习副作用处理和依赖追踪
3. **应用** → `reactive_dict_basic.py` - 掌握复杂数据结构的响应式管理
4. **优化** → `readonly_view_example.py` - 理解只读视图和权限控制

## 💡 核心概念

### Ref (响应式引用)
- **用途**: 包装单个值，使其变为响应式
- **特点**: 订阅/取消订阅机制，自动通知变化
- **应用**: 状态管理、数据绑定

### Effect (响应式副作用)
- **用途**: 自动响应数据变化的函数
- **特点**: 依赖追踪、自动重新执行、清理机制
- **应用**: DOM更新、API调用、日志记录

### ReactiveDict (响应式字典)
- **用途**: 响应式的字典数据结构
- **特点**: 嵌套支持、类型推断、与Effect配合
- **应用**: 复杂状态管理、表单处理

### ReadOnlyView (只读视图)
- **用途**: 提供数据的只读访问接口
- **特点**: 类型安全、响应式监听、权限控制
- **应用**: 数据隔离、组件接口、权限系统

## 🎯 最佳实践

1. **响应式设计原则**
   - 保持数据单向流动
   - 避免循环依赖
   - 合理使用 Effect 清理

2. **性能优化技巧**
   - 避免过度响应式
   - 考虑防抖和节流
   - 合理拆分 Effect

3. **错误处理策略**
   - Effect 中加入异常处理
   - 验证数据类型和结构
   - 提供回退机制

4. **代码组织建议**
   - 按功能模块划分响应式数据
   - 创建清晰的数据结构
   - 创建专用的只读视图

## 🔧 开发环境

确保你的开发环境满足以下要求：

```bash
# Python 版本要求
python --version  # 应该是 Python 3.10 或更高版本

# 安装依赖
pip install cognihub-pyeffectref

# 或者从源码安装
pip install -e .
```

## ❓ 常见问题

### Q: Effect 没有自动重新执行？
A: 检查是否正确访问了 Ref 的 `.value` 属性，确保依赖被正确追踪。

### Q: ReactiveDict 类型相关问题？
A: ReactiveDict 现在专注于响应式功能，不再进行复杂的类型验证，更加灵活易用。

### Q: ReadOnlyView 无法访问属性？
A: 记住使用 `.value` 访问 ReadOnlyRef 的实际值。

### Q: 性能问题？
A: 考虑减少 Effect 数量，避免在 Effect 中进行重计算，使用缓存优化。

## 📚 进一步学习

- 查看 [项目文档](../README.md) 了解更多API详情
- 参考 [测试用例](../tests/) 了解边界情况处理
- 探索 [源代码](../cognihub_pyeffectref/) 理解实现原理

---

**提示**: 所有示例都包含详细的注释和类型标注，可以作为实际项目的参考模板。
