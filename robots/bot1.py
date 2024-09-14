# bot1.py (Module)

import math
import pygame

bot_name = 'Drone #1'

def bot_logic(bot, game_state):
    """
    机器人逻辑：通过寻找最近的敌人，调整方向并根据距离发动攻击。
    
    :param bot: 当前机器人对象
    :param game_state: 包含当前游戏状态的字典，包括所有机器人和武器
    """
    # 寻找最近的敌方机器人
    nearest_bot = None
    min_distance = float('inf')  # 将最小距离初始化为无穷大
    
    # 遍历所有机器人以找到最近的敌人
    for other_bot in game_state['bots']:
        if other_bot != bot:
            distance = math.hypot(other_bot.rect.centerx - bot.rect.centerx,
                                  other_bot.rect.centery - bot.rect.centery)
            if distance < min_distance:
                min_distance = distance
                nearest_bot = other_bot

    # 如果找到最近的机器人，调整方向并决定行为
    if nearest_bot:
        # 计算目标与当前机器人之间的方向向量
        dx = nearest_bot.rect.centerx - bot.rect.centerx
        dy = nearest_bot.rect.centery - bot.rect.centery
        desired_direction = pygame.math.Vector2(dx, dy).normalize()  # 规范化方向向量
        angle_diff = bot.direction.angle_to(desired_direction)  # 计算角度差

        # 调整机器人的朝向，角度差超过5度时逐渐旋转
        if angle_diff > 5:
            bot.turn(-5)
        elif angle_diff < -5:
            bot.turn(5)
        else:
            # 如果已经面向目标且距离大于 50，则向前移动
            if min_distance > 50:
                bot.move(bot.direction.x, bot.direction.y)

        # 根据距离选择合适的攻击方式
        if min_distance < 100 and bot.weapon_cooldowns['zap'] <= 0:
            bot.fire_zap()
        elif min_distance < 200 and bot.weapon_cooldowns['grenade'] <= 0:
            bot.throw_grenade()
        elif min_distance < 300 and bot.weapon_cooldowns['missile'] <= 0:
            bot.fire_missile()
        elif bot.weapon_cooldowns['energy_mine'] <= 0:
            bot.place_energy_mine()
