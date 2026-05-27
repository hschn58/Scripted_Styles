import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import argparse
import os
import matplotlib
from matplotlib.colors import LogNorm, PowerNorm
import matplotlib.colors as mcolors
import time
import pandas as pd
from matplotlib.colors import LogNorm, PowerNorm

start = time.time()

matplotlib.use('Agg')


color_detail = 4096
freq = 3
cmap_fraction = 1
linewidth = 1 
flower_types = ['rose', 'daisy', 'spiral', 'lily']
size = 10000
dpi = 2400

cmap_custom = None
from ScriptedStyles.Designs.Releases.ismethods.gs_copy import create_custom_gist_stern_colormap


# cmap_custom = create_custom_gist_stern_colormap("turquoise", "purple", "#04D9FF",
#                                                 name="turquoise_purple_neonblue")
# Use Agg backend for non-interactive plotting

# 7, 512

# --- Particle simulation classes & functions ---
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--color', type=str, default='twilight', help='Particle mass')
parser.add_argument('--sigfreq', type=float, default=8.5*(10000/512), help='Number of particles')
parser.add_argument('--freq', type=float, default=3, help='Number of particles')
parser.add_argument('--flower', type=str, default='rose', help='Number of particles')

args = parser.parse_args()

colormapp = args.color
sigfreq = args.sigfreq
freq = args.freq
flower = args.flower


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


if cmap_custom:
    binary_cmap = cmap_custom

else:
    binary_cmap = plt.get_cmap(colormapp)

N = color_detail
x = np.linspace(0, 1, N)
cyclic_map = 0.5 * (1 - triangle_wave_tdown(t = freq * np.pi * x,
                                       period = np.pi,
                                       amplitude = 1))

cyclic_map =  cmap_fraction*(0.5*(1 + triangle_wave(t = freq * np.pi * x,  period = np.pi, amplitude = 1)))
                                      
cyclic_colors = binary_cmap(cyclic_map)
cyclic_binary = mcolors.ListedColormap(cyclic_colors, name="cyclic_binary")

def generate_detailed_flower_density(size, flower_type='rose', petal_count=5, 
                                     thickness=0.01, scale=0.8,
                                     detail_amplitude=0.05, detail_frequency=20, detail_phase=0):
    """
    Generate a 2D density matrix encoding a flower pattern with extra fine detail.
    
    Parameters:
      size (int): Width and height of the square matrix.
      flower_type (str): Type of flower pattern. Options include:
                         - 'rose':  r = scale * |cos(petal_count * theta)|
                         - 'daisy': r = scale * (0.5 + 0.5*cos(petal_count * theta))
                         - 'spiral': r = scale * theta/(2*pi)
                         - 'lily':  an arbitrary variant using a Gaussian bump
                         - 'tulip': a sine-based function to flatten the petals
                         - 'dahlia': a modified rose with fuller petals (new)
                         - Otherwise: a circle of constant radius.
      petal_count (int): Controls the number of petals or oscillation frequency.
      thickness (float): Standard deviation for the Gaussian “penalty” defining petal width.
      scale (float): Maximum radius (in normalized coordinates) for the flower.
      detail_amplitude (float): Amplitude of the fine (high-frequency) modulation on the petal boundary.
      detail_frequency (float): Frequency of the fine modulation (higher values give finer detail).
      detail_phase (float): Phase offset for the fine modulation.
      
    Returns:
      density (2D np.array): A matrix of shape (size, size) with high values
                             where the petals are (including fine detail).
    """
    # Create coordinate grid in [-1, 1] in both x and y.
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)
    
    # Convert to polar coordinates.
    R = np.sqrt(X**2 + Y**2)
    Theta = np.arctan2(Y, X)  # range: [-pi, pi]
    Theta = np.mod(Theta, 2 * np.pi)  # convert to [0, 2*pi]
    
    # Compute the base target radius, r_base, as a function of theta.
    if flower_type.lower() == 'rose':
        r_base = scale * np.abs(np.cos(petal_count * Theta))
    elif flower_type.lower() == 'daisy':
        r_base = scale * (0.5 + 0.5 * np.cos(petal_count * Theta))
    elif flower_type.lower() == 'spiral':
        r_base = scale * Theta / (2 * np.pi)
    elif flower_type.lower() == 'lily':
        sigma = np.pi / 8
        r_base = scale * (0.3 + 0.7 * np.exp(-((Theta - np.pi)**2) / (2 * sigma**2)))
    elif flower_type.lower() == 'tulip':
        # A sine-based modulation with an offset to yield a "cup"-shaped petal.
        r_base = scale * (0.4 + 0.6 * np.abs(np.sin(petal_count * Theta + np.pi/6))**0.8)
    elif flower_type.lower() == 'dahlia':
        # New flower type "dahlia": similar to a rose but with an offset and an exponent
        # to produce fuller, rounder petals.
        r_base = scale * (0.35 + 0.65 * np.abs(np.cos(petal_count * Theta))**1.2)
    else:
        r_base = scale * np.ones_like(Theta)
    
    # Add a high-frequency modulation to capture fine detail.
    detail_modulation = detail_amplitude * np.cos(detail_frequency * Theta + detail_phase)
    
    # Combine the base function with the fine detail.
    flower_r = r_base + detail_modulation
    # Ensure the target radius is within physical bounds.
    flower_r = np.clip(flower_r, 0, scale)
    
    # Compute the density field:
    # High density where the actual radius R is close to the modulated target radius flower_r.
    density = np.exp(-((R - flower_r)**2) / (2 * thickness**2))
    
    # Optionally, mask out the region outside the intended flower area.
    density[R > scale] = 0
    
    return density

# --------------------------------------------------------------------------
# Demonstration: Generate and show detailed flower patterns.
# --------------------------------------------------------------------------




fig = plt.figure( figsize=(10,10))

    # You can experiment with the detail parameters:
density = generate_detailed_flower_density(
    size,
    flower_type=flower,
    petal_count=5,
    thickness=0.01,
    scale=0.8,
    detail_amplitude=0.05,   # increase for more pronounced detail
    detail_frequency=20,     # higher frequency = finer detail
    detail_phase=0
)
path_density = gaussian_filter(density, sigma=sigfreq * linewidth * linewidth, truncate = 6, mode='wrap')

# Normalize the density values to [0,1]
min_val = np.min(path_density)
max_val = np.max(path_density)
normalized_path_density = (path_density - min_val) / (max_val - min_val)


plt.axis('off')
im = plt.imshow(normalized_path_density, cmap=cyclic_binary, origin='lower', extent=[-1,1,-1,1])

from ScriptedStyles.Designs.Releases.ismethods.check import unique_filename
import os


dirname = os.path.dirname(__file__)

# Define the path to the images folder
images_dir = os.path.join(dirname, 'images')
# Check if the folder exists; if not, create it.
if not os.path.exists(images_dir):
    os.makedirs(images_dir)
# Create the filename in the images folder.
filename = unique_filename(os.path.join(images_dir, 'fun_quilt.jpg'))
plt.savefig(filename, dpi=dpi, bbox_inches='tight', pad_inches=0.0)


end = time.time()
print('Time taken:', end - start)

plt.axis('off')
plt.tight_layout()


df = pd.read_csv('product_information.csv')
df['local_path'].iloc[0] = filename
df.to_csv('product_information.csv', index=False)

plt.close()
