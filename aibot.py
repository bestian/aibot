import pygame
import sys
import math
import random
import os
import importlib.util
from pygame.locals import *
from tkinter import Tk, filedialog

from robots.bot1 import bot_logic

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
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Sprite groups
bots = pygame.sprite.Group()
missiles = pygame.sprite.Group()
zaps = pygame.sprite.Group()
grenades = pygame.sprite.Group()
energy_mines = pygame.sprite.Group()

# Game states
STATE_MENU = 'menu'
STATE_GAME = 'game'
current_state = STATE_MENU

# Bot AI modules (initially None)
bot1_ai_module = bot_logic
bot2_ai_module = bot_logic

# Function to load AI scripts dynamically
def load_ai(bot_number):
    Tk().withdraw()  # Hide the root window
    filepath = filedialog.askopenfilename(
        initialdir='./robots',
        title=f"Select AI script for Bot{bot_number}",
        filetypes=(("Python Files", "*.py"),)
    )
    if filepath:
        module_name = f'bot{bot_number}_loaded'
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                print(f"Loaded Bot{bot_number} AI from {filepath}")
                return module.bot_logic
            except Exception as e:
                print(f"Failed to load Bot{bot_number} AI: {e}")
                return None
        else:
            print(f"Failed to load module spec for Bot{bot_number}")
            return None
    return None

# Bot class with visual enhancements
class Bot(pygame.sprite.Sprite):
    def __init__(self, x, y, color, bot_number):
        super().__init__()
        self.bot_number = bot_number
        self.base_image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.color = color
        self.draw_bot()
        self.image = self.base_image.copy()
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
        self.bot_logic = bot1_ai_module if bot_number == 1 else bot2_ai_module

    def draw_bot(self):
        # Draw body
        pygame.draw.circle(self.base_image, self.color, (20, 20), 20)
        # Draw eyes
        pygame.draw.circle(self.base_image, WHITE, (12, 14), 4)  # Left eye
        pygame.draw.circle(self.base_image, WHITE, (28, 14), 4)  # Right eye
        # Draw gun barrel (a line indicating direction)
        pygame.draw.line(self.base_image, GRAY, (20, 20), (35, 20), 3)

    def update_image(self):
        # Rotate the base image according to direction
        angle = -self.direction.angle_to(pygame.math.Vector2(1, 0))
        self.image = pygame.transform.rotate(self.base_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        # Reduce cooldowns
        for weapon in self.weapon_cooldowns:
            if self.weapon_cooldowns[weapon] > 0:
                self.weapon_cooldowns[weapon] -= 1

        # Execute bot logic
        if self.bot_logic:
            self.bot_logic(self, game_state)

        self.update_image()

    def move(self, dx, dy):
        if self.fuel <= 0:
            return
        new_x = self.rect.x + dx * self.speed
        new_y = self.rect.y + dy * self.speed
        # Prevent moving out of bounds
        new_x = max(0, min(WIDTH - self.rect.width, new_x))
        new_y = max(0, min(HEIGHT - self.rect.height, new_y))
        # Check for collision with other bots
        temp_rect = self.rect.copy()
        temp_rect.x = new_x
        temp_rect.y = new_y
        collided_bots = [bot for bot in bots if bot.rect.colliderect(temp_rect) and bot != self]
        if not collided_bots:
            self.rect.x = new_x
            self.rect.y = new_y
            self.fuel -= 0.1 * self.speed

    def turn(self, angle):
        self.direction = self.direction.rotate(angle)

    def fire_missile(self):
        if self.ammo >= 5 and self.weapon_cooldowns['missile'] <= 0:
            missile = Missile(self.rect.centerx, self.rect.centery, self.direction, self)
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

# Missile class with increased speed and fuel deduction
class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, shooter):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill((255, 0, 0))  # Red missile
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction.normalize()
        self.speed = 20  # Increased speed (twice as fast)
        self.range = 300  # Pixels missile can travel
        self.shooter = shooter

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        self.range -= self.speed
        if self.range <= 0:
            self.kill()

        # Check collision with bots
        hit_bots = pygame.sprite.spritecollide(self, bots, False)
        for bot in hit_bots:
            if bot != self.shooter:
                bot.take_damage(30)
                bot.fuel -= 10  # Deduct fuel
                print(f"Bot{bot.bot_number} hit by missile! Fuel now: {bot.fuel}")
                self.kill()
                break

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
        hit_bots = pygame.sprite.spritecollide(self, bots, False)
        for bot in hit_bots:
            if bot != self:
                bot.take_damage(15)
                self.kill()
                break

# Grenade class
class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (7,7), 7)
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
        hit_bots = pygame.sprite.spritecollide(self, bots, False)
        for bot in hit_bots:
            if bot != self:
                bot.take_damage(25)
                self.kill()
                break

# Function to display buttons
def draw_button(text, rect, inactive_color, active_color, font, mouse_pos):
    if rect.collidepoint(mouse_pos):
        color = active_color
    else:
        color = inactive_color
    pygame.draw.rect(screen, color, rect)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

# Function to create bots ensuring they don't overlap initially
def create_bots():
    global bot1, bot2
    positions = [
        (100, HEIGHT // 2),
        (WIDTH - 100, HEIGHT // 2)
    ]
    bot1 = Bot(*positions[0], BLUE, bot_number=1)
    bot2 = Bot(*positions[1], GREEN, bot_number=2)
    bots.add(bot1, bot2)

# Game state
game_state = {
    'bots': bots,
    'missiles': missiles,
    'zaps': zaps,
    'grenades': grenades,
    'energy_mines': energy_mines
}

# Create initial bots
create_bots()

# Main game loop
running = True
turn_timer = 0  # 用于控制回合时间
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

while running:
    clock.tick(60)  # Limit to 60 FPS
    turn_timer += clock.get_time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if current_state == STATE_MENU:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                # Define button rectangles
                start_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50)
                load_bot1_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 50)
                load_bot2_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 50)

                if start_button.collidepoint(mouse_pos):
                    current_state = STATE_GAME
                elif load_bot1_button.collidepoint(mouse_pos):
                    bot1_ai_module = load_ai(1)
                    bot1.bot_logic = bot1_ai_module
                elif load_bot2_button.collidepoint(mouse_pos):
                    bot2_ai_module = load_ai(2)
                    bot2.bot_logic = bot2_ai_module

    if current_state == STATE_MENU:
        # Draw menu
        screen.fill(BLACK)
        title_surf = font.render("AIBots Battle", True, WHITE)
        title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 150))
        screen.blit(title_surf, title_rect)

        # Define button rectangles
        start_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50)
        load_bot1_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 50)
        load_bot2_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 50)

        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Draw buttons
        draw_button("Start", start_button, GREEN, (0, 200, 0), font, mouse_pos)
        draw_button("Load Robot1 AI", load_bot1_button, BLUE, (0, 0, 200), font, mouse_pos)
        draw_button("Load Robot2 AI", load_bot2_button, BLUE, (0, 0, 200), font, mouse_pos)

    elif current_state == STATE_GAME:
        # Handle game updates every 0.5 seconds
        if turn_timer >= 500:  # 500 milliseconds
            turn_timer = 0

            # Update bots
            bots.update()

            # Update weapons
            missiles.update()
            zaps.update()
            grenades.update()
            energy_mines.update()

            # Check if any bots are dead
            if len(bots) <= 1:
                current_state = 'end_game'
                end_game_winner = None
                if len(bots) == 1:
                    end_game_winner = bots.sprites()[0].bot_number
                elif len(bots) == 0:
                    end_game_winner = None  # Draw

        # Draw everything
        screen.fill(BLACK)
        bots.draw(screen)
        missiles.draw(screen)
        zaps.draw(screen)
        grenades.draw(screen)
        energy_mines.draw(screen)

        # Display bot health and ammo
        status_font = pygame.font.SysFont(None, 24)
        if bot1.alive():
            bot1_status = status_font.render(
                f'Bot1 (Blue) Health: {bot1.health} Ammo: {bot1.ammo} Fuel: {int(bot1.fuel)}',
                True, WHITE)
            screen.blit(bot1_status, (10, 10))
        if bot2.alive():
            bot2_status = status_font.render(
                f'Bot2 (Green) Health: {bot2.health} Ammo: {bot2.ammo} Fuel: {int(bot2.fuel)}',
                True, WHITE)
            screen.blit(bot2_status, (WIDTH - 300, 10))

    elif current_state == 'end_game':
        # Display victory information
        screen.fill(BLACK)
        font_large = pygame.font.SysFont(None, 48)
        if end_game_winner == 1:
            victory_text = font_large.render('Bot1 (Blue) Wins!', True, WHITE)
        elif end_game_winner == 2:
            victory_text = font_large.render('Bot2 (Green) Wins!', True, WHITE)
        else:
            victory_text = font_large.render('Draw!', True, WHITE)
        victory_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(victory_text, victory_rect)
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

    pygame.display.flip()

pygame.quit()
sys.exit()
