import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import matplotlib
from matplotlib.colors import LogNorm, PowerNorm
import cv2  # OpenCV for the tessellation overlay
import pandas as pd

# Use Agg backend for non-interactive plotting
matplotlib.use('Agg')

# --- Particle simulation classes & functions ---
num_particles = 100
param = 0.0
pnorm = 1
freq = 2
prad =0.8
sigfreq = 17


# if num_particles == 5:
#     if param == 0.05:
#         freq = 10
#     else:
#         freq = 28
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
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.i = i

    def update_position(self, time_step):
        p_rad = 0.01470588  # particle radius
        self.position += self.velocity * time_step

        # Reflect off boundaries (assumes a [0,1] box)
        for i in range(2):  # x and y
            if self.position[i] <= 0 + p_rad or self.position[i] >= 1 - p_rad:
                self.velocity[i] = -self.velocity[i]

    def apply_force(self, force, time_step):
        acceleration = force / self.mass
        self.velocity += acceleration * time_step
        self.update_position(time_step)

    def check_collision(self, other, col_mat, i, k):
        col_axis = self.position - other.position
        magnitude = np.linalg.norm(col_axis)
        p_rad = p_rad

        if magnitude <= 2 * p_rad:
            if np.dot(col_axis, self.velocity) * np.dot(col_axis, other.velocity) < 0:
                ucol_axis = col_axis / magnitude
                smag = np.dot(ucol_axis, self.velocity)
                omag = np.dot(ucol_axis, other.velocity)

                # Perfectly elastic collision: swap the projected velocity components
                self.velocity = omag * ucol_axis + (self.velocity - smag * ucol_axis)
                other.velocity = smag * ucol_axis + (other.velocity - omag * ucol_axis)

                # Mark collision as handled
                col_mat[i, k] = True
                col_mat[k, i] = True
        return

# --- Simulation Parameters ---
mass = 1.0
num_particles = 5
time_step = 0.1
num_steps = 2000
force = np.array([0, 0])  # no external force
grid_size = 1000  # You can increase this for a finer simulation grid
line_width = 1   # affects the Gaussian spread
hi_speed = 10
lo_speed =1

# --- Initialize Particles ---

val = np.random.rand()
if num_particles == 5:
    val += 0.1


particles = {}
for i in range(num_particles):
    if i == 1 or i == 0:
        if float(val) < 1/5:
            particles[f"x{i}"] = Particle(
                                    mass=mass, 
                                    position=np.random.rand(2), 
                                    velocity=lo_speed*np.array([0.99, 0.2*np.random.rand(1)[0]]),
                                    i=i
                                )
        elif val>= 1/5 and val < 2/5:
            particles[f"x{i}"] = Particle(
                                    mass=mass, 
                                    position=np.random.rand(2), 
                                    velocity=lo_speed*np.array([0.2*np.random.rand(1)[0], 0.99]),
                                    i=i
                                )
            
        elif val >= 2/5 and val < 3/5:

            particles[f"x{i}"] = Particle(
                mass=mass, 
                position=np.random.rand(2), 
                velocity=lo_speed*np.array([0.5*np.sqrt(2), 0.5*np.sqrt(2)]),
                i=i
            )

        elif val >= 3/5 and val < 4/5:

            particles[f"x{i}"] = Particle(
                mass=mass, 
                position=np.random.rand(2), 
                velocity=lo_speed * (np.random.rand(2) - 0.5),
                i=i
            )
        elif val >= 4/5:

            particles[f"x{i}"] = Particle(
                mass=mass, 
                position=np.random.rand(2), 
                velocity=lo_speed * (np.random.rand(2) - 0.5),
                i=i
            )
        else:
            particles[f"x{i}"] = Particle(
                mass=mass, 
                position=np.random.rand(2), 
                velocity=lo_speed*np.array([np.random.rand(1)[0], np.random.rand(1)[0]]),
                i=i
            )
    else:
        particles[f"x{i}"] = Particle(
            mass=mass, 
            position=np.random.rand(2), 
            velocity=lo_speed*np.array([np.random.rand(1)[0], np.random.rand(1)[0]]),
            i=i
        )
                    
    



# --- Create Path Density Grid ---
path_density = np.zeros((grid_size, grid_size))

for step in range(num_steps):
    for i in range(num_particles):
        p = particles[f"x{i}"]
        p.apply_force(force, time_step)
        loc = p.position.copy()
        
        # Convert position in [0,1] to grid coordinates:
        grid_x = min(max(int(loc[0] * grid_size), 0), grid_size - 1)
        grid_y = min(max(int(loc[1] * grid_size), 0), grid_size - 1)
        path_density[grid_y, grid_x] += 1
    
    if step % 1000 == 0:
        print(f"Steps done")

#10000, 7*10, 6
# Apply Gaussian filter for line–width effect
path_density = gaussian_filter(path_density, sigma=sigfreq* line_width, mode='wrap', cval=0)


print("min value: ", np.min(path_density))
print("max value: ", np.max(path_density))

pd.DataFrame(path_density).to_csv('2Dgasprocessdensity.csv')


# Normalize the density values to [0,1]
min_val = np.min(path_density)
max_val = np.max(path_density)
normalized_path_density = (path_density - min_val) / (max_val - min_val)

# --- Build a Custom Cyclic Colormap from "binary" ---
import matplotlib.colors as mcolors
def triangle_wave_shrink(t, period=1, amplitude=1, decay = 1):
    """
    Generate an isosceles triangular waveform with linear amplitude decay.
    
    Parameters:
    -----------
    t : float or array-like
        Time input (can be scalar or numpy array).
    period : float, optional
        The period of the triangle wave. Default is 1.
    amplitude : float, optional
        The initial amplitude of the wave. Default is 1.
    decay_rate : float, optional
        The rate at which the amplitude linearly decays per unit time. Default is 0.1.
        
    Returns:
    --------
    float or numpy array
        The evaluated triangle wave at time t.
    """

    # Ensure t is a numpy array to handle scalar or array inputs uniformly
    
    t = np.asarray(t)
    decay_rate = decay*(amplitude/np.max(t))

    # Linearly decaying amplitude
    # Use np.clip to avoid negative amplitudes
    amp = np.clip(amplitude - decay_rate * t, 0, None)

    # Compute the triangular shape
    wave = 2 * np.abs(2 * (t / period - np.floor(t / period + 0.5))) - 1

    return amp * wave
def triangle_wave(t, period=1, amplitude=1, decay = 1):
    """
    Generate an isosceles triangular waveform with linear amplitude decay.
    
    Parameters:
    -----------
    t : float or array-like
        Time input (can be scalar or numpy array).
    period : float, optional
        The period of the triangle wave. Default is 1.
    amplitude : float, optional
        The initial amplitude of the wave. Default is 1.
    decay_rate : float, optional
        The rate at which the amplitude linearly decays per unit time. Default is 0.1.
        
    Returns:
    --------
    float or numpy array
        The evaluated triangle wave at time t.
    """

    # Ensure t is a numpy array to handle scalar or array inputs uniformly
    
    t = np.asarray(t)
    decay_rate = decay*(amplitude/np.max(t))

    # Linearly decaying amplitude
    # Use np.clip to avoid negative amplitudes
    amp = np.clip(amplitude - decay_rate * t, 0, None)

    # Compute the triangular shape
    wave = 2 * np.abs(2 * (t / period - np.floor(t / period + 0.5))) - 1

    return wave


def triangle_wave_tdown(t, period=1, amplitude=1, decay = 1):
    """
    Generate an isosceles triangular waveform with linear amplitude decay.
    
    Parameters:
    -----------
    t : float or array-like
        Time input (can be scalar or numpy array).
    period : float, optional
        The period of the triangle wave. Default is 1.
    amplitude : float, optional
        The initial amplitude of the wave. Default is 1.
    decay_rate : float, optional
        The rate at which the amplitude linearly decays per unit time. Default is 0.1.
        
    Returns:
    --------
    float or numpy array
        The evaluated triangle wave at time t.
    """

    # Ensure t is a numpy array to handle scalar or array inputs uniformly
    
    t = np.asarray(t)
    decay_rate = decay*(amplitude/np.max(t))

    # Linearly decaying amplitude
    # Use np.clip to avoid negative amplitudes
    amp = np.clip(amplitude - decay_rate * t, 0, None)

    # Compute the triangular shape
    wave = 1.1 * np.abs(2 * (t / period - np.floor(t / period + 0.5))) - 1*(1.1/2) + (0.45 - 0.9*(t/np.max(t)))

    return wave


# # Generate time values
# t = np.linspace(0, 4*np.pi, 1000)  # 2 seconds, 1000 points
# period = np.pi  # Triangle wave period (adjust for frequency)
# amplitude = 1  # Peak amplitude

# # Generate the waveform
# tri_wave = triangle_wave(t, period, amplitude)


import matplotlib.colors as mcolors

binary_cmap = plt.get_cmap('cool')
N = 4096
x = np.linspace(0, 1, N)
cyclic_map = 0.5 * (1 - triangle_wave_tdown(t = freq*np.pi* x,
                                       period = np.pi,
                                       amplitude = 1))
cyclic_colors = binary_cmap(cyclic_map)
cyclic_binary = mcolors.ListedColormap(cyclic_colors, name="cyclic_binary")

colormap_name = 'cyclic_binary'

# --- Plot and Save the Heatmap ---
plt.figure(figsize=(10, 10))

# Only show a central part of the grid (to avoid edge artifacts)
param = 0.0
start = int(grid_size * param)
end = int(grid_size * (1 - param))

plt.imshow(normalized_path_density[start:end, start:end], 
           cmap=cyclic_binary, 
           origin='lower', 
           extent=[0, 1, 0, 1], 
           norm=PowerNorm(pnorm))
plt.axis('off')

# Assume unique_filename() returns a new filename each time
from ScriptedStyles.Designs.Releases.ismethods.check import unique_filename
output_filename = unique_filename('2d_heatmap_powernorm_' +
                                  colormap_name + '_strange' + '.jpg')
plt.savefig(output_filename, dpi=600, bbox_inches='tight', pad_inches=0)
plt.close()
