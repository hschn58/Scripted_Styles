import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import matplotlib
from matplotlib.colors import LogNorm, PowerNorm
import cv2  # OpenCV for the tessellation overlay
import argparse
import os
import pandas as pd

cmap_custom = None
from ScriptedStyles.Designs.Releases.ismethods.gs_copy import create_custom_gist_stern_colormap


# cmap_custom = create_custom_gist_stern_colormap("turquoise", "purple", "#04D9FF",
#                                                 name="turquoise_purple_neonblue")
# Use Agg backend for non-interactive plotting
matplotlib.use('Agg')

# --- Particle simulation classes & functions ---

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--color', type=str, default='twilight', help='Particle mass')
parser.add_argument('--num_particles', type=int, default=3, help='Particle mass')
parser.add_argument('--param', type=float, default=0, help='Number of particles')
parser.add_argument('--sigfreq', type=float, default=7, help='Number of particles')
parser.add_argument('--pnorm', type=float, default=0.5, help='Number of particles')
parser.add_argument('--freq', type=float, default=3, help='Number of particles')


# if cmap_custom:



#(period is pi)

args = parser.parse_args()

colormapp = args.color
num_particles = args.num_particles
param = args.param
sigfreq = args.sigfreq
freq = args.freq
pnorm = args.pnorm


grid_size = 1000
dpi = 2400
#SIGFREQ

# --- Simulation Parameters ---
mass = 1.0
time_step = 0.001
num_steps = 20000 #get normal modes by going way higher
force = np.array([0, 0])  # no external force
  # You can increase this for a finer simulation grid
line_width =1   # affects the Gaussian spread
hi_speed = 10
lo_speed = 3
p_rad = 0.014
figure_size = (10, 10)
color_detail = 4096
truncation = 8
nv_assigned = 1
cmap_fraction = 1



def triangle_wave(t, period=1, amplitude=1, decay = 1): #Never posted any good ones!
  
    t = np.asarray(t)
    decay_rate = decay*(amplitude/np.max(t))

    # Linearly decaying amplitude
    # Use np.clip to avoid negative amplitudes
    amp = np.clip(amplitude - decay_rate * t, 0, None)

    # Compute the triangular shape
    wave = 2 * np.abs(2 * (t / period - np.floor(t / period + 0.5))) - 1

    return wave

def triangle_wave_tdown(t, period=1, amplitude=1, decay = 1):

    t = np.asarray(t)

    # Compute the triangular shape
    wave = 1.1 * np.abs(2 * (t / period - np.floor(t / period + 0.5))) - 1*(1.1/2) + (0.45 - 0.9*(t/np.max(t)))
    return wave


N = color_detail
x = np.linspace(0, 1, N)
cyclic_map = 0.5 * (1 - triangle_wave_tdown(t = freq * np.pi * x,
                                       period = np.pi,
                                       amplitude = 1))


# if num_particles == 5:
#     freq = 20*10

# else:
#     freq = 14*10

# if num_particles == 30:
#     if param == 0:
#         freq = 28
#     else:
#         freq = 6

# if num_particles == 100:
#     if param == 0:
#         freq = 28
#     else:
#         freq = 6


class Particle:
    def __init__(self, mass, position, velocity, i):
        self.mass = mass
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.i = i

    def update_position(self, time_step):
        # Update position based on the current velocity.
        self.position += self.velocity * time_step

        # Reflect off boundaries (domain is [0, 1] in both x and y).
        for idx in range(2):
            if self.position[idx] < 0:
                self.position[idx] = -self.position[idx]
                self.velocity[idx] = -self.velocity[idx]
            elif self.position[idx] > 1:
                self.position[idx] = 2 - self.position[idx]
                self.velocity[idx] = -self.velocity[idx]

    def apply_force(self, force, time_step):
        # Update velocity based on F = m * a, so a = F/m.
        acceleration = force / self.mass
        self.velocity += acceleration * time_step





# ---------------------- Particle Initialization ---------------------- #
particles = {}
for i in range(num_particles):
    # Random initial position in [0, 1] for both x and y.
    position = np.random.rand(2)
    # Random initial velocity; the value of lo_speed controls the magnitude.
    if i < nv_assigned:
        v = (np.random.rand(2) - 0.5)
        velocity = lo_speed * ( v / np.linalg.norm(v))
    else:
        v = (np.random.rand(2) - 0.5)
        velocity = lo_speed * ( v / np.linalg.norm(v))
    particles[f"x{i}"] = Particle(mass, position, velocity, i)


# ---------------------- Create the Path Density Grid ---------------------- #
path_density = np.zeros((grid_size, grid_size))


# ---------------------- Simulation Loop ---------------------- #
for step in range(num_steps):
    for i in range(num_particles):
        p = particles[f"x{i}"]
        # (Optional) apply a force if needed
        p.apply_force(force, time_step)
        # Update the particle's position.
        p.update_position(time_step)
        
        # Convert the position (in [0, 1]) to grid indices.
        loc = p.position
        grid_x = min(max(int(loc[0] * grid_size), 0), grid_size - 1)
        grid_y = min(max(int(loc[1] * grid_size), 0), grid_size - 1)
        path_density[grid_y, grid_x] += 1

    if step % 2000 == 0:
        print(f"Step {step + 1} / {num_steps} done")



#10000, 7*10, 6
# Apply Gaussian filter for line–width effect
path_density = gaussian_filter(path_density, sigma=sigfreq* line_width * line_width, truncate = truncation, mode='wrap')

# Normalize the density values to [0,1]
min_val = np.min(path_density)
max_val = np.max(path_density)
normalized_path_density = (path_density - min_val) / (max_val - min_val)

print('below normalized_path_density and gaussian_filter')
# --- Build a Custom Cyclic Colormap from "binary" ---

# def triangle_wave(t, period=1, amplitude=1):
#     """Generate an isosceles triangular waveform."""
#     amp = lambda t: amplitude - 
#     return amplitude * (2 * np.abs(2 * (t / period - np.floor(t / period + 0.5))) - 1)


import numpy as np




# # Generate time values
# t = np.linspace(0, 4*np.pi, 1000)  # 2 seconds, 1000 points
# period = np.pi  # Triangle wave period (adjust for frequency)
# amplitude = 1  # Peak amplitude

# # Generate the waveform
# tri_wave = triangle_wave(t, period, amplitude)


import matplotlib.colors as mcolors
#from matplotlib.colors import LinearSegmentedColormap
if cmap_custom:
    binary_cmap = cmap_custom

else:
    binary_cmap = plt.get_cmap(colormapp)

# # Extract only the first half
# half_cmap_colors = binary_cmap(np.linspace(0, 0.5, 256))  # Adjust resolution if needed

# # Create a new colormap
# half_cmap = LinearSegmentedColormap.from_list("half_viridis", half_cmap_colors)


# print('above binary_cmap')

cyclic_map =  cmap_fraction*(0.5*(1 + triangle_wave(t = freq * np.pi * x,  period = np.pi, amplitude = 1)))
                                      
cyclic_colors = binary_cmap(cyclic_map)
cyclic_binary = mcolors.ListedColormap(cyclic_colors, name="cyclic_binary")

# --- Plot and Save the Heatmap ---
plt.figure(figsize=figure_size)

# Only show a central part of the grid (to avoid edge artifacts)
param = 0
start = int(grid_size * param)
end = int(grid_size * (1 - param))

print('aboveshow') 
plt.imshow(normalized_path_density[start:end, start:end], 
           cmap=cyclic_binary, 
           origin='lower', 
           extent=[0, 1, 0, 1], 
           norm=PowerNorm(pnorm))
plt.axis('off')

# Assume unique_filename() returns a new filename each time
from ScriptedStyles.Designs.Releases.ismethods.check import unique_filename
############################################################################################################

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
images_dir = os.path.join(parent_dir, 'images')

# Check if the folder exists; if not, create it.
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

# Create the filename in the images folder.
filename = unique_filename(os.path.join(images_dir, colormapp + '_modern' + '.jpg'))
print(filename)
plt.savefig(filename, dpi=dpi, bbox_inches='tight', pad_inches=0)


df = pd.read_csv('product_information.csv')
df['local_path'].iloc[0] = filename
df.to_csv('product_information.csv', index=False)

plt.close()

