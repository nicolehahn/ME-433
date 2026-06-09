import pgzrun
import serial
import math

PORT = "COM3"
BAUD = 115200

WIDTH  = 700
HEIGHT = 700
TITLE  = "Handle Visualizer"

state = {
    "angle": 0.0,
    "force": 0.0,
    "connected": False,
    "error": "",
}

FORCE_SCALE    = 0.005
ARM_BASE_LEN   = 180
ARM_MAX_EXTEND = 120
FORCE_DEADBAND = 500

ser = None
try:
    ser = serial.Serial(PORT, BAUD, timeout=0)  # non-blocking
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
                iir   = float(parts[3])
                angle = float(parts[4])
                state["force"] = -iir if abs(iir) > FORCE_DEADBAND else 0.0
                state["angle"] = angle
    except (ValueError, serial.SerialException):
        pass

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def angle_color(force):
    if force > FORCE_DEADBAND:
        intensity = clamp(force * FORCE_SCALE / ARM_MAX_EXTEND, 0, 1)
        r = int(80  + 175 * intensity)
        g = int(180 - 160 * intensity)
        b = int(220 - 180 * intensity)
    elif force < -FORCE_DEADBAND:
        intensity = clamp(-force * FORCE_SCALE / ARM_MAX_EXTEND, 0, 1)
        r = int(80  + 175 * intensity)
        g = 80
        b = int(220 - 180 * intensity)
    else:
        r, g, b = 200, 210, 220
    return (r, g, b)

def draw():
    screen.fill((18, 20, 26))
    cx, cy = WIDTH // 2, HEIGHT // 2

    # grid rings
    for r in range(50, 320, 50):
        screen.draw.circle((cx, cy), r, (35, 40, 52))

    # spokes
    for a in range(0, 360, 30):
        rad = math.radians(a)
        ex = cx + int(310 * math.cos(rad))
        ey = cy + int(310 * math.sin(rad))
        screen.draw.line((cx, cy), (ex, ey), (35, 40, 52))

    # degree labels
    for a in range(0, 360, 30):
        rad = math.radians(a)
        lx = cx + int(280 * math.cos(rad))
        ly = cy + int(280 * math.sin(rad))
        screen.draw.text(f"{a}°", center=(lx, ly), fontsize=14, color=(80, 90, 110))

    # arm
    angle = state["angle"]
    force = state["force"]
    rad = math.radians(-angle)
    # arm length uses magnitude only, always extends outward
    force_extend = clamp(abs(force) * FORCE_SCALE, 0, ARM_MAX_EXTEND)
    arm_len = ARM_BASE_LEN + force_extend
    tip_x = cx + int(arm_len * math.cos(rad))
    tip_y = cy + int(arm_len * math.sin(rad))
    col = angle_color(force)

    screen.draw.line((cx+2, cy+2), (tip_x+2, tip_y+2), (0, 0, 0))
    screen.draw.line((cx, cy), (tip_x, tip_y), col)
    screen.draw.filled_circle((tip_x, tip_y), 10, col)
    screen.draw.circle((tip_x, tip_y), 10, (255, 255, 255))
    screen.draw.filled_circle((cx, cy), 8, (200, 210, 220))

    # force bar
    bar_x      = WIDTH - 55
    bar_center = HEIGHT // 2
    bar_h      = 260
    bar_w      = 20

    screen.draw.filled_rect(Rect(bar_x - bar_w//2, bar_center - bar_h//2, bar_w, bar_h), (30, 35, 48))
    screen.draw.rect(Rect(bar_x - bar_w//2, bar_center - bar_h//2, bar_w, bar_h), (60, 70, 90))
    screen.draw.line((bar_x - bar_w//2 - 4, bar_center), (bar_x + bar_w//2 + 4, bar_center), (100, 110, 130))

    fill_h = int(clamp(abs(force) * FORCE_SCALE, 0, bar_h // 2))
    if fill_h > 0:
        if force >= 0:
            screen.draw.filled_rect(Rect(bar_x - bar_w//2 + 2, bar_center - fill_h, bar_w - 4, fill_h), (80, 180, 220))
        else:
            screen.draw.filled_rect(Rect(bar_x - bar_w//2 + 2, bar_center, bar_w - 4, fill_h), (220, 80, 100))

    screen.draw.text("FORCE", center=(bar_x, bar_center + bar_h//2 + 16), fontsize=13, color=(80, 90, 110))
    screen.draw.text(f"{int(force):+d}", center=(bar_x, bar_center - bar_h//2 - 14), fontsize=14, color=(160, 170, 185))

    # angle readout
    screen.draw.text(f"{angle:+.1f}°", center=(cx, HEIGHT - 38), fontsize=28, color=(200, 210, 220))
    screen.draw.text("ANGLE", center=(cx, HEIGHT - 16), fontsize=13, color=(80, 90, 110))

    # status
    if state["error"]:
        screen.draw.text(f"Serial error: {state['error']}", topleft=(10, 10), fontsize=14, color=(220, 80, 80))
    elif not state["connected"]:
        screen.draw.text("Connecting...", topleft=(10, 10), fontsize=14, color=(200, 180, 80))
    else:
        screen.draw.text(f"● {PORT}", topleft=(10, 10), fontsize=14, color=(80, 200, 120))

pgzrun.go()