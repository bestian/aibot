import pygame
import sys
import math
import random
import os

# 加载bot1.py中的逻辑
import sys
sys.path.append('./robots')
from bot1 import bot_logic

# Initialize PyGame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AIBots with Advanced Weapons")

# Clock to control the frame rate
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Bot class
class Bot(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.direction = pygame.math.Vector2(1, 0)  # Facing right initially
        self.health = 100
        self.ammo = 50
        self.fuel = 100
        self.weapon_cooldowns = {
            'missile': 0,
            'zap': 0,
            'grenade': 0,
            'energy_mine': 0
        }

    def update(self):
        # Reduce cooldowns
        for weapon in self.weapon_cooldowns:
            if self.weapon_cooldowns[weapon] > 0:
                self.weapon_cooldowns[weapon] -= 1

        # 执行机器人逻辑
        bot_logic(self, game_state)

    def move(self, dx, dy):
        if self.fuel <= 0:
            return
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.fuel -= 0.1 * self.speed

    def turn(self, angle):
        self.direction = self.direction.rotate(angle)

    def fire_missile(self):
        if self.ammo >= 5 and self.weapon_cooldowns['missile'] <= 0:
            missile = Missile(self.rect.centerx, self.rect.centery, self.direction)
            missiles.add(missile)
            self.ammo -= 5
            self.weapon_cooldowns['missile'] = 60  # Cooldown in frames

    def fire_zap(self):
        if self.ammo >= 2 and self.weapon_cooldowns['zap'] <= 0:
            zap = Zap(self.rect.centerx, self.rect.centery, self.direction)
            zaps.add(zap)
            self.ammo -= 2
            self.weapon_cooldowns['zap'] = 30

    def throw_grenade(self):
        if self.ammo >= 3 and self.weapon_cooldowns['grenade'] <= 0:
            grenade = Grenade(self.rect.centerx, self.rect.centery, self.direction)
            grenades.add(grenade)
            self.ammo -= 3
            self.weapon_cooldowns['grenade'] = 90

    def place_energy_mine(self):
        if self.ammo >= 4 and self.weapon_cooldowns['energy_mine'] <= 0:
            energy_mine = EnergyMine(self.rect.centerx, self.rect.centery)
            energy_mines.add(energy_mine)
            self.ammo -= 4
            self.weapon_cooldowns['energy_mine'] = 120

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

# Missile class
class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill((255, 0, 0))  # Red missile
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction.normalize()
        self.speed = 10
        self.range = 300  # Pixels missile can travel

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        self.range -= self.speed
        if self.range <= 0:
            self.kill()

        # Check collision with bots
        if pygame.sprite.spritecollideany(self, bots):
            bot_hit = pygame.sprite.spritecollideany(self, bots)
            if bot_hit != self:
                bot_hit.take_damage(30)
                self.kill()

# Zap class
class Zap(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill((0, 255, 255))  # Cyan zap
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction.normalize()
        self.speed = 15
        self.range = 100

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        self.range -= self.speed
        if self.range <= 0:
            self.kill()

        # Check collision with bots
        if pygame.sprite.spritecollideany(self, bots):
            bot_hit = pygame.sprite.spritecollideany(self, bots)
            if bot_hit != self:
                bot_hit.take_damage(15)
                self.kill()

# Grenade class
class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((7, 7))
        self.image.fill((0, 255, 0))  # Green grenade
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction.normalize()
        self.speed = 7
        self.range = 200

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        self.range -= self.speed
        if self.range <= 0:
            self.explode()

    def explode(self):
        # Damage nearby bots
        for bot in bots:
            distance = math.hypot(bot.rect.centerx - self.rect.centerx,
                                  bot.rect.centery - self.rect.centery)
            if distance <= 50:
                bot.take_damage(20)
        self.kill()

# EnergyMine class
class EnergyMine(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 255, 0))  # Yellow energy mine
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        # Check for bots stepping on the mine
        if pygame.sprite.spritecollideany(self, bots):
            bot_hit = pygame.sprite.spritecollideany(self, bots)
            if bot_hit != self:
                bot_hit.take_damage(25)
                self.kill()

# Sprite groups
bots = pygame.sprite.Group()
missiles = pygame.sprite.Group()
zaps = pygame.sprite.Group()
grenades = pygame.sprite.Group()
energy_mines = pygame.sprite.Group()

# Create bots
bot1 = Bot(100, HEIGHT // 2, (0, 0, 255))
bot2 = Bot(WIDTH - 100, HEIGHT // 2, (255, 0, 0))

bots.add(bot1)
bots.add(bot2)

# Game state
game_state = {
    'bots': bots,
    'missiles': missiles,
    'zaps': zaps,
    'grenades': grenades,
    'energy_mines': energy_mines
}

# Main game loop
running = True
turn_timer = 0  # 用于控制回合时间

while running:
    clock.tick(60)  # Limit to 60 FPS
    turn_timer += clock.get_time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 每0.5秒进行一次更新
    if turn_timer >= 500:  # 500毫秒
        turn_timer = 0

        # Update bots
        bots.update()

        # Update weapons
        missiles.update()
        zaps.update()
        grenades.update()
        energy_mines.update()

        # 检查是否有机器人被消灭
        if len(bots) <= 1:
            running = False

    # Draw everything
    screen.fill(BLACK)
    bots.draw(screen)
    missiles.draw(screen)
    zaps.draw(screen)
    grenades.draw(screen)
    energy_mines.draw(screen)

    # Display bot health and ammo
    font = pygame.font.SysFont(None, 24)
    if bot1.alive():
        bot1_status = font.render(f'Bot1 Health: {bot1.health} Ammo: {bot1.ammo} Fuel: {int(bot1.fuel)}', True, WHITE)
        screen.blit(bot1_status, (10, 10))
    if bot2.alive():
        bot2_status = font.render(f'Bot2 Health: {bot2.health} Ammo: {bot2.ammo} Fuel: {int(bot2.fuel)}', True, WHITE)
        screen.blit(bot2_status, (WIDTH - 300, 10))

    pygame.display.flip()

# 显示胜利信息
screen.fill(BLACK)
font = pygame.font.SysFont(None, 48)
if bot1.alive():
    victory_text = font.render('Bot1 Wins!', True, WHITE)
elif bot2.alive():
    victory_text = font.render('Bot2 Wins!', True, WHITE)
else:
    victory_text = font.render('Draw!', True, WHITE)
screen.blit(victory_text, (WIDTH // 2 - 100, HEIGHT // 2))
pygame.display.flip()
pygame.time.wait(3000)

pygame.quit()
sys.exit()
