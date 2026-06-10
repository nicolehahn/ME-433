import pgzrun
import serial
import math
import pygame
import random

PORT = "COM3"
BAUD = 115200

WIDTH  = 800
HEIGHT = 550
TITLE  = "Valley Visualizer"

state = {
    "angle": 0.0,
    "connected": False,
    "error": "",
}

ser = None
try:
    ser = serial.Serial(PORT, BAUD, timeout=0)
    state["connected"] = True
except serial.SerialException as e:
    state["error"] = str(e)

_serial_buf = ""

def update():
    global _serial_buf
    if ser is None:
        return
    try:
        waiting = ser.in_waiting
        if waiting:
            _serial_buf += ser.read(waiting).decode("utf-8", errors="ignore")
            while "\n" in _serial_buf:
                line, _serial_buf = _serial_buf.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 5:
                    continue
                angle = float(parts[4])
                state["angle"] = max(-90.0, min(90.0, angle))
    except (ValueError, serial.SerialException):
        pass

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def valley_surface_y(x_norm, valley_top, valley_bottom):
    flat_zone = 20.0 / 90.0
    valley_h  = valley_bottom - valley_top
    if abs(x_norm) <= flat_zone:
        t = 0.0
    else:
        t = (abs(x_norm) - flat_zone) / (1.0 - flat_zone)
    rise = (t ** 2.2) * valley_h * 0.78
    return valley_bottom - rise

# ── pre-generate static scene elements ────────────────────────────────────────

rng = random.Random(42)

# clouds: (x, y, scale)
clouds = [(rng.randint(80, 720), rng.randint(30, 120), rng.uniform(0.7, 1.3)) for _ in range(5)]

# grass tufts along the surface (sampled at build time, drawn each frame)
grass_positions = [i / 120 for i in range(121)]  # t values 0..1

# flower positions (t along surface, color)
flower_colors = [(255,80,80),(255,200,50),(255,255,255),(255,130,200)]
flowers = [(rng.uniform(0.05, 0.95), rng.choice(flower_colors)) for _ in range(18)]

# boulder polygon shapes (offsets from center)
def make_boulder(cx, cy, w, h, seed):
    r = random.Random(seed)
    pts = []
    n = 10
    for i in range(n):
        angle = 2 * math.pi * i / n
        jitter = r.uniform(0.75, 1.0)
        px = cx + math.cos(angle) * w * jitter
        py = cy + math.sin(angle) * h * jitter
        pts.append((int(px), int(py)))
    return pts

def draw_cloud(surface, cx, cy, scale):
    col = (245, 248, 255)
    shadow = (210, 215, 230)
    for dx, dy, r in [
        (0, 0, 28), (-30, 10, 20), (30, 10, 20),
        (-15, -12, 22), (15, -12, 22), (0, -18, 18)
    ]:
        sx, sy, sr = int(cx + dx*scale), int(cy + dy*scale), int(r*scale)
        pygame.draw.circle(surface, shadow, (sx, sy+4), sr)
    for dx, dy, r in [
        (0, 0, 28), (-30, 10, 20), (30, 10, 20),
        (-15, -12, 22), (15, -12, 22), (0, -18, 18)
    ]:
        sx, sy, sr = int(cx + dx*scale), int(cy + dy*scale), int(r*scale)
        pygame.draw.circle(surface, col, (sx, sy), sr)

def draw_boulder(surface, cx, cy, w, h, seed):
    pts = make_boulder(cx, cy, w, h, seed)
    # base dark
    pygame.draw.polygon(surface, (90, 85, 80), pts)
    # mid tone
    inner = [(cx + (px-cx)*0.75, cy + (py-cy)*0.75) for px,py in pts]
    pygame.draw.polygon(surface, (130, 122, 112), [(int(x),int(y)) for x,y in inner])
    # highlight patch top-left
    hi = [(cx + (px-cx)*0.35 - w*0.15, cy + (py-cy)*0.35 - h*0.2) for px,py in pts[:5]]
    pygame.draw.polygon(surface, (175, 168, 158), [(int(x),int(y)) for x,y in hi])
    # outline
    pygame.draw.polygon(surface, (70, 65, 60), pts, 2)
    # crack lines
    r = random.Random(seed)
    for _ in range(3):
        ax = cx + r.randint(-int(w*0.4), int(w*0.4))
        ay = cy + r.randint(-int(h*0.4), int(h*0.4))
        bx = ax + r.randint(-int(w*0.3), int(w*0.3))
        by = ay + r.randint(-int(h*0.3), int(h*0.3))
        pygame.draw.line(surface, (60, 55, 50), (ax, ay), (bx, by), 1)

def draw():
    # ── sky gradient ──────────────────────────────────────────────────────
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(135 + (180-135)*t)
        g = int(195 + (220-195)*t)
        b = int(235 + (245-235)*t)
        pygame.draw.line(screen.surface, (r, g, b), (0, y), (WIDTH, y))

    valley_top    = 110
    valley_bottom = 390
    wall_x_left   = 70
    wall_x_right  = WIDTH - 70
    steps         = 300

    angle         = state["angle"]
    at_left_wall  = angle <= -89.5
    at_right_wall = angle >=  89.5

    # ── sun ───────────────────────────────────────────────────────────────
    sun_x, sun_y = 680, 65
    for ring in range(5, 0, -1):
        alpha_col = (255, 245, 180 - ring*15)
        pygame.draw.circle(screen.surface, alpha_col, (sun_x, sun_y), 22 + ring*7)
    pygame.draw.circle(screen.surface, (255, 252, 200), (sun_x, sun_y), 26)
    pygame.draw.circle(screen.surface, (255, 255, 230), (sun_x, sun_y), 20)

    # ── clouds ────────────────────────────────────────────────────────────
    for cx, cy, sc in clouds:
        draw_cloud(screen.surface, cx, cy, sc)

    # ── build surface points ───────────────────────────────────────────────
    surface_pts = []
    for i in range(steps + 1):
        t      = i / steps
        x_norm = t * 2.0 - 1.0
        x_px   = wall_x_left + t * (wall_x_right - wall_x_left)
        y_px   = valley_surface_y(x_norm, valley_top, valley_bottom)
        surface_pts.append((x_px, y_px))
    surface_int = [(int(x), int(y)) for x, y in surface_pts]

    # ── dirt fill ─────────────────────────────────────────────────────────
    dirt_poly = surface_int + [(wall_x_right, HEIGHT+10), (wall_x_left, HEIGHT+10)]
    pygame.draw.polygon(screen.surface, (160, 110, 65), dirt_poly)

    # ── grass layer (slightly above surface) ──────────────────────────────
    grass_poly = [(x, y+4) for x,y in surface_int]
    grass_poly = grass_poly + [(wall_x_right, HEIGHT+10), (wall_x_left, HEIGHT+10)]
    pygame.draw.polygon(screen.surface, (72, 155, 52), grass_poly)

    # ── bright grass top strip ────────────────────────────────────────────
    pygame.draw.lines(screen.surface, (100, 185, 68), False, surface_int, 4)
    pygame.draw.lines(screen.surface, (130, 210, 90), False, surface_int, 2)

    # ── grass tufts ───────────────────────────────────────────────────────
    rng2 = random.Random(7)
    for t_pos in grass_positions[::2]:
        x_norm = t_pos * 2.0 - 1.0
        gx = int(wall_x_left + t_pos * (wall_x_right - wall_x_left))
        gy = int(valley_surface_y(x_norm, valley_top, valley_bottom))
        jitter = rng2.randint(-3, 3)
        h_tuft = rng2.randint(4, 9)
        col = (rng2.randint(80,120), rng2.randint(170,210), rng2.randint(50,80))
        pygame.draw.line(screen.surface, col,
                         (gx+jitter, gy), (gx+jitter-1, gy-h_tuft), 1)
        pygame.draw.line(screen.surface, col,
                         (gx+jitter+2, gy), (gx+jitter+3, gy-h_tuft+2), 1)

    # ── flowers ───────────────────────────────────────────────────────────
    for t_pos, fcol in flowers:
        x_norm = t_pos * 2.0 - 1.0
        fx = int(wall_x_left + t_pos * (wall_x_right - wall_x_left))
        fy = int(valley_surface_y(x_norm, valley_top, valley_bottom))
        pygame.draw.line(screen.surface, (60,140,40), (fx, fy), (fx, fy-10), 1)
        pygame.draw.circle(screen.surface, fcol, (fx, fy-11), 4)
        pygame.draw.circle(screen.surface, (255,245,150), (fx, fy-11), 2)

    # ── boulders at walls ─────────────────────────────────────────────────
    left_surf_y  = int(valley_surface_y(-1.0, valley_top, valley_bottom))
    right_surf_y = int(valley_surface_y( 1.0, valley_top, valley_bottom))

    draw_boulder(screen.surface, wall_x_left,  left_surf_y  - 38, 44, 52, seed=1)
    draw_boulder(screen.surface, wall_x_left-8, left_surf_y - 12, 28, 28, seed=2)
    draw_boulder(screen.surface, wall_x_right,  right_surf_y - 38, 44, 52, seed=3)
    draw_boulder(screen.surface, wall_x_right+8, right_surf_y - 12, 28, 28, seed=4)

    # wall flash when at limit
    if at_left_wall:
        screen.draw.text("BONK!", center=(wall_x_left + 10, left_surf_y - 110),
                         fontsize=26, color=(220, 60, 40))
    if at_right_wall:
        screen.draw.text("BONK!", center=(wall_x_right - 10, right_surf_y - 110),
                         fontsize=26, color=(220, 60, 40))

    # ── flat zone ticks ────────────────────────────────────────────────────
    flat_norm    = 20.0 / 90.0
    flat_left_x  = int(wall_x_left + (1.0 - flat_norm) / 2.0 * (wall_x_right - wall_x_left))
    flat_right_x = int(wall_x_left + (1.0 + flat_norm) / 2.0 * (wall_x_right - wall_x_left))
    for fx, label in [(flat_left_x, "-20°"), (flat_right_x, "+20°")]:
        fy = int(valley_surface_y((fx - wall_x_left) / (wall_x_right - wall_x_left) * 2 - 1,
                                   valley_top, valley_bottom))
        pygame.draw.line(screen.surface, (80, 60, 30), (fx, fy-4), (fx, fy+8), 2)
        screen.draw.text(label, center=(fx, fy + 20), fontsize=12, color=(80, 60, 30))

    # ── ball (as a wooden/rubber ball) ────────────────────────────────────
    x_norm_c  = clamp(angle / 90.0, -1.0, 1.0)
    t_ball    = (x_norm_c + 1.0) / 2.0
    ball_x    = int(wall_x_left + t_ball * (wall_x_right - wall_x_left))
    surface_y = int(valley_surface_y(x_norm_c, valley_top, valley_bottom))
    ball_r    = 20
    ball_y    = surface_y - ball_r

    # shadow on grass
    shadow_surf = pygame.Surface((ball_r*4, ball_r), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, ball_r*4, ball_r))
    screen.surface.blit(shadow_surf, (ball_x - ball_r*2, surface_y - ball_r//2 + 4))

    # ball: warm red rubber
    pygame.draw.circle(screen.surface, (160, 30, 20), (ball_x, ball_y), ball_r)   # dark base
    pygame.draw.circle(screen.surface, (220, 55, 40), (ball_x, ball_y), ball_r-2) # mid
    # highlight
    pygame.draw.circle(screen.surface, (255, 130, 110),
                       (ball_x - ball_r//3, ball_y - ball_r//3), ball_r//4)
    pygame.draw.circle(screen.surface, (255, 220, 210),
                       (ball_x - ball_r//3 - 2, ball_y - ball_r//3 - 2), ball_r//8)

    # ── angle readout panel ────────────────────────────────────────────────
    panel = pygame.Surface((160, 44), pygame.SRCALPHA)
    panel.fill((255, 255, 255, 100))
    screen.surface.blit(panel, (WIDTH//2 - 80, HEIGHT - 54))
    screen.draw.text(f"{angle:+.1f}°", center=(WIDTH//2, HEIGHT - 38),
                     fontsize=30, color=(50, 80, 30))
    screen.draw.text("ENCODER POSITION", center=(WIDTH//2, HEIGHT - 18),
                     fontsize=12, color=(80, 110, 50))

    # ── status ────────────────────────────────────────────────────────────
    if state["error"]:
        screen.draw.text(f"Serial error: {state['error']}", topleft=(12, 12),
                         fontsize=13, color=(180, 40, 40))
    elif not state["connected"]:
        screen.draw.text("Connecting...", topleft=(12, 12),
                         fontsize=13, color=(180, 140, 30))
    else:
        screen.draw.text(f"● {PORT}", topleft=(12, 12),
                         fontsize=13, color=(50, 130, 60))

pgzrun.go()