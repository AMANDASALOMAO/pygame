import random
from pgzero.builtins import Actor, Rect, sounds, music
from math import sin, cos, pi

WIDTH = 600
HEIGHT = 800

SCROLL_THRESH = 10
GRAVITY = 1
MAX_PLATFORMS = 20

game_state = "menu"

hero_images = [f'hit{i}' for i in range(1, 8)]
hero_idle_images = ['jump']
double_jump_images = [f'doublejump{i}' for i in range(1, 6)]
coin_images = [f'coins{i}' for i in range(1, 4)]
bomb_image = [f'bomb{i}' for i in range(1, 2)]

bg = Actor('bg_03', center=(WIDTH // 2, HEIGHT // 2))
platform_image = 'cloud'

music.set_volume(0.8)
music.play('bg_music')

jump_fx = sounds.jump
hit_fx = sounds.hit
coin_fx = sounds.coin

scroll = 0
bg_scroll = 0
score = 0
high_score = 0
game_over = False
hit_animation_time = 0
hit_animation_duration = 1.0

try:
    with open('score.txt', 'r') as file:
        high_score = int(file.read())
except:
    high_score = 0

class Player:
    def __init__(self, x, y):
        self.width = 30
        self.height = 50
        self.rect = Rect(x - self.width // 2, y - self.height // 2, self.width, self.height)
        self.vel_y = 0
        self.flip = False

        self.idle_frames = [Actor(name) for name in hero_idle_images]
        self.hit_frames = [Actor(name) for name in hero_images]
        self.double_jump_frames = [Actor(name) for name in double_jump_images]

        self.anim_index = 0
        self.anim_speed = 0.2
        self.image = self.idle_frames[0]

        self.is_hit = False
        self.can_jump = True
        self.jump_lock = False

    def move(self):
        global scroll
        dx, dy = 0, 0
        if self.is_hit:
            return

        moved = False 
        
        if keyboard.a or keyboard.left:
            dx = -10
            self.flip = True
            moved = True
        elif keyboard.d or keyboard.right:
            dx = 10
            self.flip = False
            moved = True

        if moved:
            self.can_jump = True

        jump_pressed = keyboard.space or keyboard.w or keyboard.up

        if jump_pressed and not self.jump_lock and self.can_jump:
            self.vel_y = -20
            jump_fx.play()

            self.can_jump = True
            self.jump_lock = True

        if not jump_pressed:
            self.jump_lock = False

        self.vel_y += GRAVITY
        dy += self.vel_y

        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > WIDTH:
            dx = WIDTH - self.rect.right

        future_rect = Rect(self.rect.x, self.rect.y + dy, self.width, self.height)

        for p in platforms:
            if p.rect.colliderect(future_rect):
                if self.rect.bottom <= p.rect.top + 10 and self.vel_y > 0:
                    self.rect.bottom = p.rect.top
                    dy = 0
                    self.vel_y = 0
                    
                    if p.moving:
                        self.rect.x += p.direction * p.speed

        if self.rect.top <= SCROLL_THRESH and self.vel_y < 0:
            scroll = -self.vel_y
        else:
            scroll = 0

        self.rect.x += dx
        self.rect.y += dy + scroll

        self.anim_index += self.anim_speed
        if self.anim_index >= len(self.idle_frames):
            self.anim_index = 0
        self.image = self.idle_frames[int(self.anim_index)]

    def update_hit_animation(self, dt):
        self.anim_index += self.anim_speed
        if self.anim_index >= len(self.hit_frames):
            self.anim_index = len(self.hit_frames) - 1
        self.image = self.hit_frames[int(self.anim_index)]

    def draw(self):
        self.image.angle = 0
        self.image.pos = self.rect.center
        self.image.draw()

class Platform:
    def __init__(self, x, y, width, moving):
        self.actor = Actor(platform_image)
        self.rect = Rect(x, y, self.actor.width, self.actor.height)
        self.moving = moving
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 2)
        self.move_counter = 0

        self.actor.topleft = (x, y)

    def update(self):
        if self.moving:
            self.move_counter += 1
            self.rect.x += self.direction * self.speed
            self.actor.x += self.direction * self.speed

        if self.move_counter >= 100 or self.rect.left < 0 or self.rect.right > WIDTH:
            self.direction *= -1
            self.move_counter = 0

        self.rect.y += scroll
        self.actor.y += scroll

    def draw(self):
        self.actor.draw()

class Coin:
    def __init__(self, x, y):
        self.anim_frames = [Actor(name) for name in coin_images]
        self.anim_index = 0
        self.anim_speed = 0.25

        self.x = x
        self.y = y
        self.image = self.anim_frames[0]
        w, h = self.image.width, self.image.height
        self.rect = Rect(x - w // 2, y - h // 2, w, h)

    def update(self):
        self.anim_index += self.anim_speed
        if self.anim_index >= len(self.anim_frames):
            self.anim_index = 0

        self.image = self.anim_frames[int(self.anim_index)]

        self.y += scroll
        self.rect.y = self.y - self.rect.height // 2

    def draw(self):
        self.image.pos = (self.x, self.y)
        self.image.draw()

class Bomb:
    def __init__(self, x, y):
        self.anim_frames = [Actor(name) for name in bomb_image]
        self.anim_index = 0
        self.anim_speed = 0.25
        self.image = self.anim_frames[0]

        self.image.pos = (x, y)
        w, h = self.image.width, self.image.height
        self.rect = Rect(x - w // 2, y - h // 2, w, h)

    def update(self):
        self.anim_index += self.anim_speed
        if self.anim_index >= len(self.anim_frames):
            self.anim_index = 0
        self.image = self.anim_frames[int(self.anim_index)]
        self.rect.y += scroll
        self.image.y += scroll

    def draw(self):
        self.image.draw()

    def off_screen(self):
        return self.rect.top > HEIGHT

    def collide(self, player_rect):
        return self.rect.colliderect(player_rect)

player = Player(WIDTH // 2, HEIGHT - 150)
platforms = [Platform(0, HEIGHT - 40, WIDTH, False)]
coins = []
bombs = []

for i in range(1, 6):
    width = random.randint(30, 50)
    x = random.randint(50, WIDTH - 50 - width)
    y = HEIGHT - 40 - i * random.randint(60, 90)
    p = Platform(x, y, width, random.choice([False, True]))
    platforms.append(p)

    if random.random() < 0.7:
        coins.append(Coin(p.rect.centerx, p.rect.y - 30))
    if random.random() < 0.1:
        bombs.append(Bomb(p.rect.centerx, p.rect.y - 20))

start_button = Rect(WIDTH // 2 - 100, 300, 200, 50)
sound_button = Rect(WIDTH // 2 - 100, 370, 200, 50)
exit_button = Rect(WIDTH // 2 - 100, 440, 200, 50)
sound_on = True

def update():
    global score, game_over, bg_scroll, game_state, hit_animation_time, scroll

    dt = 1 / 60

    if game_state == "playing":
        if not game_over:
            if not player.is_hit:
                player.move()
            else:
                player.update_hit_animation(dt)

            for coin in coins[:]:
                coin.update()
                if player.rect.colliderect(coin.rect):
                    score += 100
                    coin_fx.play()
                    coins.remove(coin)

            for bomb in bombs[:]:
                bomb.update()
                if bomb.collide(player.rect) and not player.is_hit:
                    hit_fx.play()
                    player.is_hit = True
                    hit_animation_time = 0

            if player.is_hit:
                hit_animation_time += dt
                if hit_animation_time >= hit_animation_duration:
                    game_over = True

            bg_scroll += scroll
            if bg_scroll >= 600:
                bg_scroll = 0

            while len(platforms) < MAX_PLATFORMS:
                width = random.randint(30, 50)
                usable_width = int(WIDTH * 0.8)
                min_x = int(WIDTH * 0.1)
                x = random.randint(min_x, min_x + usable_width - width)
                y = min(p.rect.y for p in platforms) - random.randint(60, 90)
                moving = score > 1000 and random.randint(0, 1) == 1
                new_platform = Platform(x, y, width, moving)
                platforms.append(new_platform)

                if random.random() < 0.7:
                    coins.append(Coin(new_platform.rect.centerx, new_platform.rect.y - 30))
                if random.random() < 0.3:
                    bombs.append(Bomb(new_platform.rect.centerx, new_platform.rect.y - 20))

            for p in platforms:
                p.update()

            platforms[:] = [p for p in platforms if p.rect.top <= HEIGHT]
            coins[:] = [b for b in coins if b.rect.top <= HEIGHT]
            bombs[:] = [s for s in bombs if s.rect.top <= HEIGHT]

            if scroll > 0:
                score += int(scroll)

            if player.rect.top > HEIGHT:
                game_over = True
                hit_fx.play()
        else:
            if keyboard.space:
                reset_game()

def draw():
    screen.clear()
    bg.draw()

    if game_state == "menu":
        screen.draw.text("Iniciar o jogo", center=start_button.center, fontsize=30, color="white")
        screen.draw.text("Musica e sons: " + ("Ligado" if sound_on else "Desligado"),
                         center=sound_button.center, fontsize=25, color="white")
        screen.draw.text("Sair", center=exit_button.center, fontsize=30, color="white")
    elif game_state == "playing":
        for p in platforms:
            p.draw()
        for coin in coins:
            coin.draw()
        for bomb in bombs:
            bomb.draw()
        player.draw()
        screen.draw.text(f"Pontos: {score}", (20, 20), fontsize=40, color="yellow")
        screen.draw.text(f"Recorde: {high_score}", (20, 60), fontsize=30, color="orange")
        if game_over:
            screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="red")
            screen.draw.text("Pressione Espaço para reiniciar", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=30,
                             color="white")

def on_mouse_down(pos):
    global game_state, sound_on

    if game_state == "menu":
        if start_button.collidepoint(pos):
            game_state = "playing"
        elif sound_button.collidepoint(pos):
            sound_on = not sound_on
            if sound_on:
                music.unpause()
            else:
                music.pause()
        elif exit_button.collidepoint(pos):
            exit()

def reset_game():
    global score, game_over, scroll, player, platforms, coins, bombs, hit_animation_time

    score = 0
    game_over = False
    scroll = 0
    hit_animation_time = 0
    player = Player(WIDTH // 2, HEIGHT - 150)

    platforms.clear()
    platforms.append(Platform(0, HEIGHT - 40, WIDTH, False))
    coins.clear()
    bombs.clear()

    for i in range(1, 6):
        width = random.randint(30, 50)
        x = random.randint(50, WIDTH - 50 - width)
        y = HEIGHT - 40 - i * random.randint(60, 90)
        p = Platform(x, y, width, random.choice([False, True]))
        platforms.append(p)

        if random.random() < 0.7:
            coins.append(Coin(p.rect.centerx, p.rect.y - 30))
        if random.random() < 0.3:
            bombs.append(Bomb(p.rect.centerx, p.rect.y - 20))