import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import matplotlib
from matplotlib.colors import LogNorm, PowerNorm
from matplotlib.colors import hsv_to_rgb


matplotlib.use('Agg')

#heatmap through the frames
grid_size = 3000
line_width = 2
sigmacoeff = 0.9 * (grid_size/100)*1.5*1.3

# ==== physics from your completed version + pool layout ====
BALL_RAD = 0.01470588  # must match wall/collision math
def are_particles_approaching(rel_pos, vel1, vel2):
    rel_vel = np.array(vel2) - np.array(vel1)
    return np.dot(rel_pos, rel_vel) > 0

class Particle:
    def __init__(self, mass, position, velocity, i):
        self.mass = mass
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.i = i

    def __delta_check(self, time_step, p_rad):
        """Prevent rail tunneling by reflecting if a large step would cross."""
        pad_size = 3 * p_rad
        for ax in range(2):
            delta = self.velocity[ax] * time_step
            # near left/bottom rail
            if self.position[ax] < pad_size and delta < -3 * p_rad:
                self.position[ax] = delta - self.position[ax]
                self.position[1-ax] += self.velocity[1-ax] * time_step
                self.velocity[ax] = -self.velocity[ax]
                return True
            # near right/top rail
            if self.position[ax] > 1 - pad_size and delta > 3 * p_rad:
                self.position[ax] = 1 - (delta - self.position[ax])
                self.position[1-ax] += self.velocity[1-ax] * time_step
                self.velocity[ax] = -self.velocity[ax]
                return True
        return False

    def update_position(self, time_step):
        p_rad = BALL_RAD
        if self.__delta_check(time_step, p_rad):
            return
        self.position += self.velocity * time_step
        # simple reflective rails with clearance to avoid jitter
        for ax in range(2):
            if self.position[ax] < 2*p_rad and self.velocity[ax] < 0:
                self.velocity[ax] = -self.velocity[ax]
                self.position[ax] = 2*p_rad
            if self.position[ax] > 1-2*p_rad and self.velocity[ax] > 0:
                self.velocity[ax] = -self.velocity[ax]
                self.position[ax] = 1-2*p_rad

    def apply_force(self, force, time_step):
        self.velocity += (force / self.mass) * time_step

    def check_collision(self, other, col_mat, i, k):
        r = self.position - other.position
        d2 = float(np.dot(r, r))
        min_d = 2.0 * BALL_RAD
        min_d2 = (min_d + 1e-4) ** 2  # small tolerance

        if d2 <= min_d2 and d2 > 0.0:
            v_rel = self.velocity - other.velocity
            # approaching if d/dt(|r|^2) = 2 r·(v_rel) < 0
            if np.dot(r, v_rel) < 0.0:
                d = np.sqrt(d2)
                n = r / d

                # swap normal components (equal masses, e=1)
                u1 = np.dot(self.velocity, n)
                u2 = np.dot(other.velocity,  n)
                self.velocity += (u2 - u1) * n
                other.velocity += (u1 - u2) * n

                # positional de-overlap to exactly tangential contact
                overlap = min_d - d
                if overlap > 0.0:
                    corr = 0.5 * overlap * n
                    self.position += corr
                    other.position -= corr

                col_mat[i, k] = True
                col_mat[k, i] = True


# --- pool layout (10-ball rack + cue) ---
def rack_10ball_positions(apex_center=(0.20, 0.50), r=BALL_RAD):
    ax, ay = apex_center
    dx = np.sqrt(3.0) * r  # horizontal spacing in a close-packed triangle
    pos = []
    for c in range(4):                 # columns: 1,2,3,4 -> total 10
        x = ax - c * dx                # apex points RIGHT (toward +x)
        for k in range(c + 1):
            y = ay + (k - c / 2.0) * (2.0 * r)
            pos.append((x, y))
    return pos  # len == 10

# Parameters (you can keep your originals above these if you like)
mass = 1.0
time_step = 0.0001
num_steps = 1000
last_frames = 60  # tweakable window for non-cue balls
force = np.array([0.0, 0.0])

rgb_accum = np.zeros((grid_size, grid_size, 3), dtype=float)



# Tunables for the glaze
LOCAL_SIGMA = sigmacoeff * 0.5      # per-frame softening (smaller than final blur)
SAT_MIN, SAT_MAX = 0.25, 1.0       # saturation range (ends ≈ binary)
VAL_MIN, VAL_MAX = 0.9, 1.00       # keep bright; ends near-white when S≈0
ALPHA_SCALE = 1.2                   # global opacity scaler for the glaze
HUE_SPAN = 0.75                     # fraction of HSV wheel to traverse
HUE_CENTER = 0.65                   # base hue (≈magenta/blue); tweak to taste

# --- performance/quality knobs ---
glaze_every   = 5         # glaze every Nth frame
glaze_scale   = 4         # glaze grid is (grid_size // glaze_scale)
min_alpha     = 0.2      # floor for glaze opacity
gamma_out     = 1.0      # final gamma (<1 brightens)
contrast_gain = 1.0      # gentle contrast lift

# low-res per-frame deposit reused only on glazed frames
H_small = grid_size // glaze_scale
W_small = grid_size // glaze_scale
frame_deposit_small = np.zeros((H_small, W_small), dtype=np.float32)

# low-res blur sigma
LOCAL_SIGMA_SMALL = (sigmacoeff * 0.5) / glaze_scale

# Report apparent size on the grid (helps tune sigma/linewidth)
px_rad = int(round(BALL_RAD * grid_size))
print(f"[pool] ball radius ≈ {px_rad}px (diam ≈ {2*px_rad}px) on {grid_size}x{grid_size}")

# === initialize particles as a pool break ===
rack_apex = (0.20, 0.50)
rack_xy = rack_10ball_positions(apex_center=rack_apex, r=BALL_RAD)

# centroid of the 10-ball rack (for later centering the crop)
rack_centroid = np.mean(np.array(rack_xy), axis=0)

# Slightly offset the cue ball vertically so rebound isn't along the same line
CUE_Y_OFFSET = 3 * BALL_RAD
cue_x = min(0.85, 1.0 - BALL_RAD - 1e-3)  # keep it near the right
cue_y = np.clip(rack_apex[1] + CUE_Y_OFFSET, 1.5*(BALL_RAD + 1e-3), 1.5*(1.0 - BALL_RAD - 1e-3))
cue_pos = (cue_x, cue_y)


# Aim directly at the apex from the offset start
v_break = 15.0
cue_dir = np.array(rack_apex) - np.array(cue_pos)
cue_vel = v_break * (cue_dir / np.linalg.norm(cue_dir))


# --- contact estimate + temporal weighting ---

# cue speed and straight-line distance to the apex (centers)
cue_speed = float(np.linalg.norm(cue_vel))
dist_cue_to_apex = float(np.linalg.norm(np.array(rack_apex) - np.array(cue_pos)))

# simple ETA to contact (no interactions assumed): t = d / v
if cue_speed <= 1e-12:
    contact_step = 0
else:
    t_contact = dist_cue_to_apex / cue_speed
    contact_step = int(round(t_contact / time_step))

# center the importance a few frames *after* contact
PEAK_OFFSET = 5
mu = contact_step + PEAK_OFFSET

# wide std-dev so early/late frames still contribute
SIGMA_FRAC = 0.30          # 30% of the whole sim length
sigma = max(2.0, SIGMA_FRAC * num_steps)

# precompute per-frame weights (not normalized; relative weights matter)
frame_idx = np.arange(num_steps, dtype=float)
frame_weight = np.exp(-0.5 * ((frame_idx - mu) / sigma) ** 2)

# clamp contact peak in range
contact_step = int(np.clip(contact_step, 0, num_steps-1))
mu = int(np.clip(mu, 0, num_steps-1))

# precompute HSV & weights per step (for glazing)
frame_weight = np.exp(-0.5 * ((frame_idx - mu) / sigma) ** 2).astype(np.float32)
t_norm = ((frame_idx - mu) / (sigma + 1e-9)).astype(np.float32)
H_vec = (HUE_CENTER + 0.5 * HUE_SPAN * np.tanh(t_norm)) % 1.0
S_vec = (SAT_MIN + (SAT_MAX - SAT_MIN) * frame_weight).astype(np.float32)
V_vec = (VAL_MIN + (VAL_MAX - VAL_MIN) * (0.6 + 0.4*frame_weight)).astype(np.float32)
HSV_vec = np.stack([H_vec, S_vec, V_vec], axis=1)  # (num_steps, 3)


particles = {}
# 10 racked balls at rest
for i, pos in enumerate(rack_xy):
    particles[f"x{i}"] = Particle(mass=mass, position=pos, velocity=(0.0, 0.0), i=i)
# cue ball moving toward apex
particles["x10"] = Particle(mass=mass, position=cue_pos, velocity=cue_vel, i=10)
num_particles = 11

# === simulation with collisions ===
path_density = np.zeros((grid_size, grid_size))
cue_index = num_particles - 1  # cue ball is last (x10)
cue_index   = 10  # last particle (x10)

keys = [f"x{i}" for i in range(num_particles)]

keys = [f"x{i}" for i in range(num_particles)]  # move outside loop

for step in range(num_steps):
    col_mat = np.zeros((num_particles, num_particles), dtype=bool)

    # collisions
    for i in range(num_particles):
        pi = particles[keys[i]]
        for k in range(i + 1, num_particles):
            pk = particles[keys[k]]
            if not col_mat[i, k]:
                pi.check_collision(pk, col_mat, i, k)

    # --- deposit passes ---
    # Only create a small deposit map on glazed frames
    do_glaze = (step % glaze_every == 0)
    if do_glaze:
        frame_deposit_small.fill(0.0)

    for i in range(num_particles):
        p = particles[keys[i]]
        p.apply_force(force, time_step)
        p.update_position(time_step)

        gx = min(max(int(p.position[0] * grid_size), 0), grid_size - 1)
        gy = min(max(int(p.position[1] * grid_size), 0), grid_size - 1)

        # density (cue always; others only in last_frames)
        if i == cue_index:
            path_density[gy, gx] += frame_weight[step]
        else:
            if step >= num_steps - last_frames:
                path_density[gy, gx] += frame_weight[step]

        # per-frame color deposit (always localized to this frame)
        if do_glaze:
            sx = gx // glaze_scale
            sy = gy // glaze_scale
            frame_deposit_small[sy, sx] += 1.0

    # glaze compositing (only on glazed frames)
    if do_glaze:
        frame_blur_small = gaussian_filter(frame_deposit_small, sigma=LOCAL_SIGMA_SMALL)
        m = frame_blur_small.max()
        if m > 1e-12:
            frame_blur_small /= m
            # upsample once for this frame (bilinear)
            # note: order=1 is fast; output size matches full-res
            from scipy.ndimage import zoom
            frame_blur = zoom(frame_blur_small, zoom=glaze_scale, order=1, prefilter=False)
            frame_blur = frame_blur[:grid_size, :grid_size]  # guard

            w_t = max(float(frame_weight[step]), 1e-3)
            H, S, V = HSV_vec[step]
            rgb_color = hsv_to_rgb([H, S, V]).astype(np.float32)

            alpha = ALPHA_SCALE * (w_t * glaze_every) * np.maximum(frame_blur, min_alpha)

            # rgb_accum = (1-alpha)*rgb_accum + alpha*color
            rgb_accum[:] = rgb_accum * (1.0 - alpha[..., None]) + rgb_color * alpha[..., None]



# Apply Gaussian filter to simulate line width effect
path_density = gaussian_filter(path_density, sigma=sigmacoeff*line_width)

# Min-Max Normalization
min_val = np.min(path_density)
max_val = np.max(path_density)

# Apply min-max normalization
normalized_path_density = (path_density - min_val) / (max_val - min_val)


######
import matplotlib.colors as mcolors
# 1. Get the "binary" colormap (binary_r)
binary_cmap = plt.get_cmap("hsv")

# 2. Create a cyclic version by mapping the colormap to a sine wave pattern
N = 256  # Number of color levels
x = np.linspace(0, 1, N)  # Linear mapping from 0 to 1
cyclic_map = 0.5 * (1 - np.cos(9 * np.pi * x))  # Smooth cyclic function

# 3. Apply this mapping to the original "binary" colormap
cyclic_colors = binary_cmap(cyclic_map)

# 4. Create a new colormap from this transformed data
cyclic_binary = mcolors.ListedColormap(cyclic_colors, name="cyclic_binary")

#####
from ScriptedStyles.Designs.Releases.ismethods.check import unique_filename

rgb_accum = np.clip(rgb_accum, 0.0, 1.0)
hybrid = 0.7*rgb_accum + 0.3*(rgb_accum * normalized_path_density[..., None])
hybrid = np.clip(hybrid, 0.0, 1.0)

#26:974,26:974
colormap='cyclic_binary'

# Midpoint between cue start and rack centroid (in unit [0..1] coords)
mid_uv = 0.5 * (np.array(cue_pos) + rack_centroid)

yy, xx = np.nonzero(path_density > 0)
pad = 20
y0b, y1b = max(0, yy.min()-pad), min(grid_size, yy.max()+pad)
x0b, x1b = max(0, xx.min()-pad), min(grid_size, xx.max()+pad)

# Square window size that covers all activity
L = int(np.ceil(max(x1b - x0b, y1b - y0b)))
cx = int(round(mid_uv[0] * grid_size))
cy = int(round(mid_uv[1] * grid_size))
half = L // 2

# Centered square around the midpoint, clamped to image
x0 = max(0, cx - half); x1 = min(grid_size, cx + half)
y0 = max(0, cy - half); y1 = min(grid_size, cy + half)

# If clamped, shift to keep the window size (when possible)
if (x1 - x0) < L:
    if x0 == 0: x1 = min(grid_size, L)
    elif x1 == grid_size: x0 = max(0, grid_size - L)
if (y1 - y0) < L:
    if y0 == 0: y1 = min(grid_size, L)
    elif y1 == grid_size: y0 = max(0, grid_size - L)


rgb_accum = np.clip(rgb_accum, 0.0, 1.0).astype(np.float32)
hybrid = rgb_accum * normalized_path_density[..., None]
# tone map
hybrid = np.clip(hybrid, 0.0, 1.0)
hybrid = np.power(hybrid, gamma_out) * contrast_gain
hybrid = np.clip(hybrid, 0.0, 1.0)

plt.figure(figsize=(6,6))
plt.imshow(hybrid[y0:y1, x0:x1], origin='lower',
           extent=[x0/grid_size, x1/grid_size, y0/grid_size, y1/grid_size])
plt.axis('off')
plt.savefig(unique_filename('pool_break_hybrid.jpg'),
            dpi=1200, bbox_inches='tight', pad_inches=0.0)
plt.close()

#DO VORONOI TESSELATION ON TOP of BINARY!