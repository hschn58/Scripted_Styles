import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# =======================
# STYLE (tweakables)
# =======================
BG               = "white"          # background
STAR_CMAP        = cm.plasma        # central 5-arm ribs
RING_CMAP        = cm.magma         # outer ring glaze
FOAM_COLOR       = (1.0, 1.0, 1.0)  # thin foam streaks
SAND_TINT        = (0.98, 0.92, 0.78, 0.08)   # translucent sand glaze
FIGSIZE          = (10, 7)

# Geometry
FREQ             = 5          # arms / exits
R_OUTER          = 9.5        # radius of outer ring center path
PARTITION        = 420        # strokes per sector on the ring
RIBS_PER_ARM     = 900        # number of “inward” ribs per arm
BASE_WIDTH       = 2.4        # base half-width of the Gaussian lobe (x-range [-w, w])
GAUSS_HEIGHT     = 1.0        # gaussian amplitude before scaling
RING_THICKNESS   = 0.55       # thickness of the outer sandbar ring “glaze”

# Rib shape “character”
RIB_OSC_HI       = 3.2        # sets sharpness of the rib waviness
RIB_OSC_LO       = 0.18
TWIST_TURNS      = 0.0        # add gentle twist along the inward path (0..1 turns)

# Color cycling
OUTER_COLOR_FREQ = 8.0
INNER_COLOR_FREQ = 22.0

# =======================
# Shape primitives
# =======================
def base_shape(num=300, half_width=BASE_WIDTH, amp=GAUSS_HEIGHT):
    """Return (x, y_top, y_bot) for y = amp * exp(-x^2) over [-half_width, half_width]."""
    x = np.linspace(-half_width, half_width, num)
    y = amp * np.exp(-x**2)
    return x, y, -y

def transform(x, y, ox=0.0, oy=0.0, sx=1.0, sy=1.0, theta=0.0):
    """Scale -> Rotate -> Translate."""
    xs, ys = x*sx, y*sy
    c, s   = np.cos(theta), np.sin(theta)
    xr     = xs*c - ys*s
    yr     = xs*s + ys*c
    return xr + ox, yr + oy

# =======================
# Canvas
# =======================
fig, ax = plt.subplots(figsize=FIGSIZE)
ax.set_facecolor(BG)

# Base lobe
x0, y_top0, y_bot0 = base_shape(num=360)

# Track bounds
min_x, max_x = +np.inf, -np.inf
min_y, max_y = +np.inf, -np.inf

def paint_between(x_top, y_top, y_bot, color, alpha=1.0, z=1):
    global min_x, max_x, min_y, max_y
    if x_top[0] > x_top[-1]:
        x_top, y_top = x_top[::-1], y_top[::-1]
        _,    y_bot = x_top, y_bot[::-1]  # x_top reused intentionally
    ax.fill_between(x_top, y_top, y_bot, color=color, alpha=alpha, linewidth=0, zorder=z)
    min_x = min(min_x, x_top.min())
    max_x = max(max_x, x_top.max())
    min_y = min(min_y, y_top.min(), y_bot.min())
    max_y = max(max_y, y_top.max(), y_bot.max())

# =======================
# 1) Soft “sandbar ring” underlay
# =======================
inc = 2*np.pi / FREQ
for i in range(PARTITION):
    phase = i / PARTITION
    theta_local = 2*np.pi * phase
    for j in range(FREQ):
        ang   = theta_local + inc*j
        cx    = (R_OUTER + 0.8*np.sin(3*ang)) * np.cos(ang)
        cy    = (R_OUTER + 0.8*np.sin(3*ang)) * np.sin(ang)

        # lobe scales & tiny rotation for movement
        sx = 1.0 + 0.28*np.sin(2*np.pi*phase) + 0.06*np.sin(12*np.pi*phase)
        sy = RING_THICKNESS*(1.0 + 0.22*np.cos(2*np.pi*phase))
        rot= 0.25*np.sin(2*np.pi*phase)

        xt, yt = transform(x0, y_top0, cx, cy, sx, sy, rot)
        xb, yb = transform(x0, y_bot0, cx, cy, sx, sy, rot)

        c = RING_CMAP( 0.5 + 0.5*np.sin(OUTER_COLOR_FREQ*np.pi*phase + 0.6*j) )
        paint_between(xt, yt, yb, c, alpha=0.9, z=1)

# subtle sand glaze inside the ring
xt, yt = transform(x0, y_top0, 0, 0, 10.8, 0.18, 0)
xb, yb = transform(x0, y_bot0, 0, 0, 10.8, 0.18, 0)

paint_between(xt, yt, yb, color=SAND_TINT, alpha=SAND_TINT[3], z=0)


# =======================
# 2) Five inward ribbed “starfish” arms
# =======================
for j in range(FREQ):
    phi = inc*j
    for k in range(RIBS_PER_ARM):
        t = k/(RIBS_PER_ARM-1)  # 0..1 outward->center

        # Center slides inward along the exit ray; optional twist
        twist = 2*np.pi*TWIST_TURNS*t
        cx = R_OUTER*np.cos(phi + twist) * (1 - t)
        cy = R_OUTER*np.sin(phi + twist) * (1 - t)

        # Rib width/height evolution + ripples to make fins
        # wide at outer ring, tighter near center
        sx = 0.65 + 0.45*(1 - t) + 0.25*np.sin(RIB_OSC_HI*2*np.pi*t) * np.sin(5*phi + 12*np.pi*t)
        sy = 0.30 + 0.55*(1 - t) + 0.20*np.cos(RIB_OSC_LO*2*np.pi*t + 0.8*np.sin(3*phi))
        rot= 0.06*np.sin(10*np.pi*t) + 0.18*np.sin(2*phi) * (1 - t)

        xt, yt = transform(x0, y_top0, cx, cy, abs(sx), abs(sy), rot)
        xb, yb = transform(x0, y_bot0, cx, cy, abs(sx), abs(sy), rot)

        c = STAR_CMAP( 0.5 + 0.5*np.sin(INNER_COLOR_FREQ*np.pi*t + 0.7*j) )
        paint_between(xt, yt, yb, c, alpha=1.0, z=3)

        # occasional thin foam-like highlight every ~N ribs near outer third
        if k % 55 == 0 and t < 0.36:
            xt2, yt2 = transform(x0, y_top0, cx, cy, abs(sx)*0.88, abs(sy)*0.88, rot)
            xb2, yb2 = transform(x0, y_bot0, cx, cy, abs(sx)*0.88, abs(sy)*0.88, rot)
            paint_between(xt2, yt2*0.998, yb2*0.998, FOAM_COLOR, alpha=0.08, z=4)

# =======================
# Finish
# =======================
ax.set_aspect('equal', 'box')
pad = 1.2
ax.set_xlim(min_x - pad, max_x + pad)
ax.set_ylim(min_y - pad, max_y + pad)
ax.axis('off')
plt.tight_layout()
plt.show()
