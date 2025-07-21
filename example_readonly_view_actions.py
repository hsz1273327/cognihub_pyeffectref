"""ReadOnlyView 的 Action 功能示例"""
import sys
import os
import time

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cognihub_pyeffectref import ReactiveDict, effect
from cognihub_pyeffectref.view import ReadOnlyView

def main() -> None:
    print("=== ReadOnlyView Action 功能示例 ===\n")
    
    # 1. 创建应用状态
    print("1. 创建游戏状态数据")
    game_state = ReactiveDict({
        'player': {
            'name': 'Player1',
            'health': 100,
            'score': 0,
            'level': 1
        },
        'game': {
            'status': 'playing',
            'enemies_defeated': 0
        }
    })
    print(f"初始状态: {game_state.to_dict()}")
    
    # 2. 创建只读视图
    print("\n2. 创建只读视图(给插件使用)")
    plugin_view = ReadOnlyView(game_state)
    
    # 3. 为插件注册受控的action
    print("\n3. 注册插件可用的action")
    
    @plugin_view
    def heal_player() -> str:
        """治疗玩家"""
        current_health = game_state.player.health
        if current_health < 100:
            game_state.player.health = min(current_health + 20, 100)
            return f"治疗成功！生命值: {current_health} -> {game_state.player.health}"
        return "生命值已满，无需治疗"
    
    @plugin_view('gain_score')
    def increase_score() -> str:
        """增加分数"""
        old_score = game_state.player.score
        game_state.player.score = old_score + 10
        return f"获得分数！{old_score} -> {game_state.player.score}"
    
    @plugin_view('level_up')
    def advance_level() -> str:
        """升级"""
        if game_state.player.score >= game_state.player.level * 50:
            old_level = game_state.player.level
            game_state.player.level += 1
            game_state.player.health = 100  # 升级回满血
            return f"恭喜升级！等级: {old_level} -> {game_state.player.level}"
        return f"分数不够升级(需要 {game_state.player.level * 50} 分)"
    
    # 4. 注册带参数的action
    @plugin_view('take_damage')
    def damage_player(damage: int) -> str:
        """玩家受伤"""
        current_health = game_state.player.health
        new_health = max(current_health - damage, 0)
        game_state.player.health = new_health
        
        if new_health == 0:
            game_state.game.status = 'game_over'
            return f"玩家阵亡！生命值: {current_health} -> 0"
        return f"玩家受伤！生命值: {current_health} -> {new_health}"
    
    # 5. 注册lambda函数action
    debug_action = plugin_view('debug_info')(lambda: f"调试信息: {game_state.to_dict()}")
    
    # 6. 设置监听器
    print("\n4. 设置状态监听")
    health_ref = plugin_view.player.health
    score_ref = plugin_view.player.score
    game_status_ref = plugin_view.game.status
    
    @effect
    def health_watcher() -> None:
        health = health_ref.value
        if health <= 20:
            print(f"⚠️  警告：生命值危险！({health})")
        elif health == 100:
            print(f"💚 生命值满血！({health})")
    
    @effect  
    def score_watcher() -> None:
        score = score_ref.value
        if score > 0 and score % 50 == 0:
            print(f"🏆 里程碑达成：{score} 分！")
    
    @effect
    def game_status_watcher() -> None:
        status = game_status_ref.value
        if status == 'game_over':
            print("💀 游戏结束！")
    
    # 手动调用一次建立监听
    health_watcher()
    score_watcher() 
    game_status_watcher()
    
    # 7. 模拟插件使用action
    print("\n5. 插件开始使用action")
    
    # 插件获取action执行器
    actions = plugin_view()
    print(f"插件可用actions: {list(actions._allowed_actions.keys())}")
    
    print("\n开始游戏模拟...")
    time.sleep(0.5)
    
    # 获得分数
    print(f"- {actions.gain_score()}")
    time.sleep(0.3)
    
    # 再次获得分数
    print(f"- {actions.gain_score()}")
    time.sleep(0.3)
    
    # 受到伤害
    print(f"- {actions.take_damage(30)}")
    time.sleep(0.3)
    
    # 治疗
    print(f"- {actions.heal_player()}")
    time.sleep(0.3)
    
    # 继续获得分数
    for i in range(4):
        print(f"- {actions.gain_score()}")
        time.sleep(0.2)
    
    # 尝试升级
    print(f"- {actions.level_up()}")
    time.sleep(0.3)
    
    # 受到致命伤害
    print(f"- {actions.take_damage(150)}")
    time.sleep(0.5)
    
    # 显示调试信息
    print(f"\n📊 {actions.debug_info()}")
    
    # 8. 验证只读性质
    print("\n6. 验证插件无法直接修改状态")
    try:
        plugin_view.player.health = 999
        print("❌ 错误：应该无法直接修改")
    except AttributeError as e:
        print(f"✅ 正确阻止直接修改: {e}")
    
    # 9. 测试action隔离
    print("\n7. 测试action隔离")
    another_view = ReadOnlyView(game_state)
    
    @another_view
    def another_action() -> str:
        return "另一个视图的action"
    
    another_actions = another_view()
    print(f"原视图actions: {len(plugin_view()._allowed_actions)}")
    print(f"新视图actions: {len(another_actions._allowed_actions)}")
    
    try:
        plugin_view().another_action()
        print("❌ 错误：不应该能访问其他视图的action")
    except AttributeError:
        print("✅ 正确：action隔离工作正常")
    
    print("\n=== 示例完成 ===")

if __name__ == "__main__":
    main()
