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

# Use non-interactive Agg backend
matplotlib.use('Agg')


#GOOD: 3*(1000/512) 6 superformula incrment 0.1
#GOOD: 20*(1000/512) 2 superformula increment 0.2
#GOOD: 9*(1000/512) 6 superformula increment 0.01
#POOR: 9*(1000/512) 6 superformula increment 0.01, base_m = 5, n_val = 0.8
#
# --------------------------------------------------------------------------
# Global parameters
# --------------------------------------------------------------------------
color_detail = 4096
freq = 3
cmap_fraction = 1
linewidth = 1 
flower_types = ['rose', 'daisy', 'spiral', 'lily', 'superformula']
size = 1000
dpi = 300

n_val = 0.8
base_m = 5
increment = 0.01

cmap_custom = None
from ScriptedStyles.Designs.Releases.ismethods.gs_copy import create_custom_gist_stern_colormap

# Example custom colormap (currently commented out)
# cmap_custom = create_custom_gist_stern_colormap("turquoise", "purple", "#04D9FF",
#                                                 name="turquoise_purple_neonblue")

# --- Particle simulation argparse parameters ---
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--colormap', type=str, default='twilight', help='Colormap name')
parser.add_argument('--sigfreq', type=float, default=11*(1000/512), help='Gaussian sigma frequency factor')
parser.add_argument('--freq', type=float, default=3, help='Frequency parameter')
parser.add_argument('--flower', type=str, default='turtle', help='Flower type (e.g., rose, daisy, spiral, lily, or superformula)')

args = parser.parse_args()

colormap = args.colormap
sigfreq = args.sigfreq
freq = args.freq
flower = args.flower

# Create a cyclic binary colormap using triangle wave modulation.
def triangle_wave(t, period=1, amplitude=1, decay=1):
    t = np.asarray(t)
    decay_rate = decay * (amplitude/np.max(t))
    amp = np.clip(amplitude - decay_rate * t, 0, None)
    wave = 2 * np.abs(2 * (t / period - np.floor(t / period + 0.5))) - 1
    return wave

def triangle_wave_tdown(t, period=1, amplitude=1, decay=1):
    t = np.asarray(t)
    wave = 1.1 * np.abs(2 * (t / period - np.floor(t / period + 0.5))) - 1*(1.1/2) + (0.45 - 0.9*(t/np.max(t)))
    return wave

if cmap_custom:
    binary_cmap = cmap_custom
else:
    binary_cmap = plt.get_cmap(colormap)

N = color_detail
x = np.linspace(0, 1, N)
cyclic_map = cmap_fraction * (0.5*(1 + triangle_wave(t=freq * np.pi * x, period=np.pi, amplitude=1)))
cyclic_colors = binary_cmap(cyclic_map)
cyclic_binary = mcolors.ListedColormap(cyclic_colors, name="cyclic_binary")

# --------------------------------------------------------------------------
# Standard flower density function.
# --------------------------------------------------------------------------
def generate_detailed_flower_density(size, flower_type='rose', petal_count=5, 
                                     thickness=0.01, scale=0.8,
                                     detail_amplitude=0.05, detail_frequency=20, detail_phase=0):
    """
    Generate a 2D density matrix encoding a flower pattern with extra fine detail.
    """
    # Create coordinate grid in [-1, 1]
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)
    
    # Convert to polar coordinates.
    R = np.sqrt(X**2 + Y**2)
    Theta = np.arctan2(Y, X)
    Theta = np.mod(Theta, 2 * np.pi)
    
    # Base target radius as a function of theta.
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
        r_base = scale * (0.4 + 0.6 * np.sin(petal_count * Theta + np.pi/6))
    elif flower_type.lower() == 'dahlia':
        r_base = scale * (0.35 + 0.65 * np.abs(np.cos(petal_count * Theta))**1.2)
    else:
        r_base = scale * np.ones_like(Theta)
    
    # High-frequency modulation for fine detail.
    detail_modulation = detail_amplitude * np.cos(detail_frequency * Theta + detail_phase)
    flower_r = r_base + detail_modulation
    flower_r = np.clip(flower_r, 0, scale)
    
    # Compute density field: high where R is near flower_r.
    density = np.exp(-((R - flower_r)**2) / (2 * thickness**2))
    density[R > scale] = 0
    return density

# --------------------------------------------------------------------------
# Superformula function.
# --------------------------------------------------------------------------

def draw_dahlia_outline(petal_count=5, scale=0.8, offsets=[0, 0.005, -0.005], 
                        color='black', line_width=0.7):
    """
    Draws outlines for the dahlia petal boundaries using multiple curves
    (with small offsets) to simulate a hand-drawn (turtle-like) effect.
    """
    theta = np.linspace(0, 2 * np.pi, 2000)
    for off in offsets:
        # Compute the petal outline based on the dahlia formula.
        r = scale * (0.35 + 0.65 * np.abs(np.cos(petal_count * (theta + off)))**1.2)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        plt.plot(x, y, color=color, linewidth=line_width)


def superformula(m, n1, n2, n3, points=5000):
    """
    Generate (x, y) points using the superformula.
    """
    phi = np.linspace(0, 2 * np.pi, points)
    n1_safe = np.where(np.abs(n1) < 1e-10, 1e-10, n1)
    r = (np.abs(np.cos(m * phi / 4))**n2 + np.abs(np.sin(m * phi / 4))**n3)**(-1 / n1_safe)
    x = r * np.cos(phi)
    y = r * np.sin(phi)
    return x, y

# --------------------------------------------------------------------------
# Generate the density field (path density) based on the flower option.
# --------------------------------------------------------------------------
fig = plt.figure(figsize=(10, 10))

if flower.lower() == 'superformula':
    # Define superformula base parameters.
    base_m  = base_m
    base_n1 = n_val
    base_n2 = n_val
    base_n3 = n_val
    increment = increment
    iterations = int(base_n1 / increment)  # For example, 9 iterations if base_n1=0.9
    
    # Collect all (x,y) points from the superformula curves.
    all_x_list = []
    all_y_list = []
    for i in range(iterations):
        m = base_m
        n1 = base_n1 - i * increment  # gradually vary n1
        n2 = base_n2
        n3 = base_n3
        x, y = superformula(m, n1, n2, n3)
        all_x_list.append(x)
        all_y_list.append(y)
    
    all_x = np.concatenate(all_x_list)
    all_y = np.concatenate(all_y_list)
    
    # Determine the range for the 2D histogram.
    buffer = 0.1
    x_min, x_max = all_x.min() - buffer, all_x.max() + buffer
    y_min, y_max = all_y.min() - buffer, all_y.max() + buffer
    
    # Create a 2D histogram (density grid) from the superformula points.
    bins = size  # you can adjust the bin count (resolution) here.
    heatmap, xedges, yedges = np.histogram2d(all_x, all_y, bins=bins, 
                                              range=[[x_min, x_max], [y_min, y_max]])
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    
    # Optionally, smooth the histogram with a Gaussian filter.
    path_density = gaussian_filter(heatmap, sigma=sigfreq * linewidth * linewidth, 
                                   truncate=6, mode='wrap')
    
    # Normalize density to [0, 1]
    min_val = np.min(path_density)
    max_val = np.max(path_density)
    normalized_path_density = (path_density - min_val) / (max_val - min_val)
    
    plt.imshow(normalized_path_density, cmap=cyclic_binary, origin='lower', extent=extent)
    
else:
    # Use the standard flower density generation.
    density = generate_detailed_flower_density(
        size,
        flower_type=flower,
        petal_count=5,
        thickness=0.01,
        scale=0.8,
        detail_amplitude=0.05,
        detail_frequency=20,
        detail_phase=0
    )
    path_density = gaussian_filter(density, sigma=sigfreq * linewidth * linewidth, 
                                   truncate=6, mode='wrap')
    
    # Normalize the density values to [0, 1]

    #normalized_path_density = (path_density - min_val) / (max_val - min_val)
    epsilon = 10e-6
    path_density = path_density + epsilon
    min_val = np.min(path_density)
    max_val = np.max(path_density)
    
    plt.imshow(path_density, cmap=cyclic_binary, origin='lower', extent=[-1, 1, -1, 1], norm=PowerNorm(gamma = 1, vmin=min_val, vmax=max_val))

print("Raw data min, max:", np.min(path_density), np.max(path_density))

# if flower.lower() == 'dahlia':
#     draw_dahlia_outline(petal_count=5, scale=0.8, offsets=[0, 0.005, -0.005],
#                         color='black', line_width=0.7)
    

plt.axis('off')

# --------------------------------------------------------------------------
# Save the image to the images folder.
# --------------------------------------------------------------------------
from ScriptedStyles.Designs.Releases.ismethods.check import unique_filename

dirname = os.path.dirname(__file__)
images_dir = os.path.join(dirname, 'images')
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

code_name = os.path.basename(__file__).split('.')[0] + f' {colormap}' + '.jpg'

filename = unique_filename(os.path.join(images_dir, code_name))
plt.savefig(filename, dpi=dpi, bbox_inches='tight', pad_inches=0.0)

end = time.time()
print('Time taken:', end - start)

plt.axis('off')
plt.tight_layout()

# --------------------------------------------------------------------------
# Update the product information CSV.
# --------------------------------------------------------------------------
df = pd.read_csv('product_information.csv')
df['local_path'].iloc[0] = filename
df.to_csv('product_information.csv', index=False)


