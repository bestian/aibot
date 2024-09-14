import math
import pygame

def bot_logic(bot, game_state):
    # 寻找最近的敌方机器人
    nearest_bot = None
    min_distance = float('inf')
    for other_bot in game_state['bots']:
        if other_bot != bot:
            distance = math.hypot(other_bot.rect.centerx - bot.rect.centerx,
                                  other_bot.rect.centery - bot.rect.centery)
            if distance < min_distance:
                min_distance = distance
                nearest_bot = other_bot

    if nearest_bot:
        # 调整方向朝向目标
        dx = nearest_bot.rect.centerx - bot.rect.centerx
        dy = nearest_bot.rect.centery - bot.rect.centery
        desired_direction = pygame.math.Vector2(dx, dy).normalize()
        angle_diff = bot.direction.angle_to(desired_direction)

        # 调整机器人方向
        if angle_diff > 5:
            bot.turn(-5)
        elif angle_diff < -5:
            bot.turn(5)
        else:
            # 如果面向目标则前进
            bot.move(bot.direction.x, bot.direction.y)

        # 根据距离决定攻击方式
        if min_distance < 100 and bot.weapon_cooldowns['zap'] <= 0:
            bot.fire_zap()
        elif min_distance < 200 and bot.weapon_cooldowns['grenade'] <= 0:
            bot.throw_grenade()
        elif min_distance < 300 and bot.weapon_cooldowns['missile'] <= 0:
            bot.fire_missile()
        elif bot.weapon_cooldowns['energy_mine'] <= 0:
            bot.place_energy_mine()
