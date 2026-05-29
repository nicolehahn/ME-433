"""
PONG - Two Player Pygame Zero Game
====================================
Controls:
  Player 1 (Left):  A (up) / D (down)
  Player 2 (Right): LEFT (up) / RIGHT (down)

To switch to API inputs, replace get_p1_input() and get_p2_input()
with your own logic. Return -1 = up, +1 = down, 0 = still.

── Sound setup ──────────────────────────────────────────────────────────────
Set P1_SCORE_SOUND and P2_SCORE_SOUND to the paths of your .wav files.
Set to None to disable a sound.

── Ball image setup ─────────────────────────────────────────────────────────
Set BALL_IMAGE_PATH to the path of any image file (jpg, png, etc).
It will be cropped to a circle and scaled to fit the ball.
Set to None to use a plain white circle instead.
"""

import pgzrun
import math
import random
import pygame
import os
import serial
ser = serial.Serial('COM3') # the name of your port here

# ── Window ────────────────────────────────────────────────────────────────────
WIDTH  = 900
HEIGHT = 600
TITLE  = "PONG"

# ══════════════════════════════════════════════════════════════════════════════
# USER INPUTS — change these
# ══════════════════════════════════════════════════════════════════════════════

P1_SCORE_SOUND = None   # e.g. "sounds/p1_score.wav"
P2_SCORE_SOUND = None   # e.g. "sounds/p2_score.wav"

BALL_IMAGE_PATH = 'images/face.png'  # e.g. "ball.png" or "C:/images/myimage.jpg"

# ══════════════════════════════════════════════════════════════════════════════

# ── Colours ───────────────────────────────────────────────────────────────────
C_BG     = (30,  30,  30)
C_WHITE  = (240, 240, 240)
C_GREY   = (100, 100, 100)
C_PADDLE = (240, 240, 240)
C_BALL   = (240, 240, 240)
C_SCORE  = (180, 180, 180)
C_CENTRE = (60,  60,  60)

# ── Game settings ─────────────────────────────────────────────────────────────
PADDLE_W      = 14
PADDLE_H      = 80
PADDLE_SPEED  = 6
PADDLE_MARGIN = 30

BALL_RADIUS    = 30      # radius in pixels (diameter = 24)
BALL_SPEED_INI = 5
BALL_SPEED_MAX = 13
BALL_SPEEDUP   = 0.25
PASSIVE_SPEEDUP = 0.002   # speed added every frame

SCORE_TO_WIN = 3

# ── Helpers ───────────────────────────────────────────────────────────────────
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def load_sound(path):
    """Load a wav file, return a pygame Sound or None on failure."""
    if path is None:
        return None
    if not os.path.isfile(path):
        print(f"[PONG] Sound file not found: {path}")
        return None
    try:
        return pygame.mixer.Sound(path)
    except Exception as e:
        print(f"[PONG] Could not load sound {path}: {e}")
        return None

def make_circle_surface(image_path, diameter):
    """
    Load an image, crop the largest centered square, scale to diameter,
    then mask it into a circle. Returns an SRCALPHA pygame Surface.
    Falls back to a plain white circle if loading fails.
    """
    d = diameter
    result = pygame.Surface((d, d), pygame.SRCALPHA)

    if image_path and os.path.isfile(image_path):
        try:
            img = pygame.image.load(image_path).convert_alpha()
            iw, ih = img.get_size()
            # Crop to centered square
            side = min(iw, ih)
            crop_rect = pygame.Rect((iw - side) // 2, (ih - side) // 2, side, side)
            cropped = img.subsurface(crop_rect)
            # Scale to ball diameter
            scaled = pygame.transform.smoothscale(cropped, (d, d))
            # Apply circular mask
            mask = pygame.Surface((d, d), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.circle(mask, (255, 255, 255, 255), (d // 2, d // 2), d // 2)
            # Blit image, then mask it
            result.blit(scaled, (0, 0))
            result.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            return result
        except Exception as e:
            print(f"[PONG] Could not load ball image {image_path}: {e}")

    # Fallback: plain white circle
    pygame.draw.circle(result, C_BALL, (d // 2, d // 2), d // 2)
    return result

# ── Classes ───────────────────────────────────────────────────────────────────
class Paddle:
    def __init__(self, x):
        self.x     = x
        self.y     = HEIGHT // 2
        self.score = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - PADDLE_W // 2,
                           int(self.y) - PADDLE_H // 2,
                           PADDLE_W, PADDLE_H)

    def move(self, direction):
        self.y += direction * PADDLE_SPEED
        self.y  = clamp(self.y, PADDLE_H // 2, HEIGHT - PADDLE_H // 2)


class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x     = float(WIDTH  // 2)
        self.y     = float(HEIGHT // 2)
        angle      = random.choice([-25, -15, 0, 15, 25])
        angle     += random.choice([0, 180])
        rad        = math.radians(angle)
        self.vx    = math.cos(rad) * BALL_SPEED_INI
        self.vy    = math.sin(rad) * BALL_SPEED_INI
        self.speed = float(BALL_SPEED_INI)
        self.angle = 0.0   # visual rotation degrees
        self.spin  = 0.0   # degrees added per frame

    def update(self):
        # Passive gradual speedup
        self.speed = min(self.speed + PASSIVE_SPEEDUP, BALL_SPEED_MAX)
        mag = math.hypot(self.vx, self.vy)
        if mag > 0:
            self.vx = self.vx / mag * self.speed
            self.vy = self.vy / mag * self.speed
        self.x += self.vx
        self.y += self.vy
        self.angle += self.spin

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - BALL_RADIUS,
                           int(self.y) - BALL_RADIUS,
                           BALL_RADIUS * 2, BALL_RADIUS * 2)

# ── Initialise assets ─────────────────────────────────────────────────────────
pygame.mixer.init()

sound_p1 = load_sound(P1_SCORE_SOUND)
sound_p2 = load_sound(P2_SCORE_SOUND)

ball_surf = make_circle_surface(BALL_IMAGE_PATH, BALL_RADIUS * 2)

# ── Game state ────────────────────────────────────────────────────────────────
p1     = Paddle(PADDLE_MARGIN + PADDLE_W // 2)
p2     = Paddle(WIDTH - PADDLE_MARGIN - PADDLE_W // 2)
ball   = Ball()
frame  = 0
game_over        = False
waiting_to_start = True
winner_text      = ""

# ── Input ─────────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
# Replace these two functions to use API / AI inputs.
# Return -1 (move up), 0 (stay), or +1 (move down).
# ══════════════════════════════════════════════════════════════════════════════

#def get_p2_input():
#    if keyboard.a:
#        return -1
#    if keyboard.d:
#        return 1
#    return 0
def read_serial():
    global up1, down1, up2, down2
    try:
        if ser.in_waiting > 0:  # only read if a full line is ready
            n_bytes = ser.readline()
            s = str(n_bytes)
            result = [int(x) for x in s[s.find('(')+1:s.find(')')].split(',')]
            up1, down1, up2, down2 = result[0], result[1], result[2], result[3]
    except Exception:
        pass

def get_p1_input():
    return down1-up1

def get_p2_input():
    return down2-up2

#def get_p2_input():
#    if keyboard.left:
#        return -1
#    if keyboard.right:
#        return 1
#    return 0

# ── Game logic helpers ────────────────────────────────────────────────────────
def check_score():
    global game_over, winner_text
    if p1.score >= SCORE_TO_WIN:
        game_over   = True
        winner_text = "PLAYER 1 WINS"
    elif p2.score >= SCORE_TO_WIN:
        game_over   = True
        winner_text = "PLAYER 2 WINS"

def reset_game():
    global game_over, winner_text, waiting_to_start
    p1.score = p2.score = 0
    p1.y = p2.y = HEIGHT // 2
    ball.reset()
    game_over        = False
    waiting_to_start = True
    winner_text      = ""

# ── Update ────────────────────────────────────────────────────────────────────
def update():
    global frame, waiting_to_start

    frame += 1

    read_serial()

    if waiting_to_start:
        if keyboard.space:
            waiting_to_start = False
        return

    if game_over:
        if keyboard.space:
            reset_game()
        return

    p1.move(get_p1_input())
    p2.move(get_p2_input())

    ball.update()

    # Wall bounces
    if ball.y - BALL_RADIUS <= 0:
        ball.y  = float(BALL_RADIUS)
        ball.vy = abs(ball.vy)
        ball.spin = -ball.spin

    if ball.y + BALL_RADIUS >= HEIGHT:
        ball.y  = float(HEIGHT - BALL_RADIUS)
        ball.vy = -abs(ball.vy)
        ball.spin = -ball.spin

    # Paddle collisions
    for paddle in (p1, p2):
        if ball.rect.colliderect(paddle.rect):
            rel = clamp((ball.y - paddle.y) / (PADDLE_H / 2), -1.0, 1.0)
            ball.speed = min(ball.speed + BALL_SPEEDUP, BALL_SPEED_MAX)
            angle = rel * math.pi / 3
            ball.vx = -math.copysign(1, ball.vx) * math.cos(angle) * ball.speed
            ball.vy = math.sin(angle) * ball.speed
            # Spin: harder edge hits = faster rotation; direction from vy
            ball.spin = rel * ball.speed * 0.8
            if paddle is p1:
                ball.x = float(paddle.x + PADDLE_W // 2 + BALL_RADIUS + 1)
            else:
                ball.x = float(paddle.x - PADDLE_W // 2 - BALL_RADIUS - 1)

    # Scoring
    if ball.x < 0:
        p2.score += 1
        if sound_p2:
            sound_p2.play()
        check_score()
        if not game_over:
            ball.reset()

    if ball.x > WIDTH:
        p1.score += 1
        if sound_p1:
            sound_p1.play()
        check_score()
        if not game_over:
            ball.reset()

# ── Draw ──────────────────────────────────────────────────────────────────────
def draw():
    surf = screen.surface

    screen.fill(C_BG)

    # Centre dashes
    for y in range(0, HEIGHT, 20):
        pygame.draw.rect(surf, C_CENTRE, pygame.Rect(WIDTH // 2 - 2, y, 4, 12))

    # Ball — rotated image or plain circle
    rotated = pygame.transform.rotate(ball_surf, ball.angle)
    rw, rh = rotated.get_size()
    surf.blit(rotated, (int(ball.x) - rw // 2, int(ball.y) - rh // 2))

    # Paddles
    for paddle in (p1, p2):
        pygame.draw.rect(surf, C_PADDLE, paddle.rect, border_radius=4)

    # Scores
    screen.draw.text(str(p1.score), fontsize=64,
                     center=(WIDTH // 4, 50), color=C_SCORE)
    screen.draw.text(str(p2.score), fontsize=64,
                     center=(3 * WIDTH // 4, 50), color=C_SCORE)

    # Press space to start
    if waiting_to_start:
        screen.draw.text("PRESS SPACE TO START", fontsize=28,
                         center=(WIDTH // 2, HEIGHT // 2), color=C_WHITE)

    # Game over
    if game_over:
        screen.draw.text(winner_text, fontsize=72,
                         center=(WIDTH // 2, HEIGHT // 2 - 40), color=C_WHITE)
        screen.draw.text("PRESS SPACE TO PLAY AGAIN", fontsize=22,
                         center=(WIDTH // 2, HEIGHT // 2 + 30), color=C_GREY)

pgzrun.go()