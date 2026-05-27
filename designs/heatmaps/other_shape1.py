import numpy as np
import matplotlib.pyplot as plt


# Base parameters (Example 1)
base_m = 7
base_n1 = 0.9
base_n2 = 0.9
base_n3 = 0.9

def base_shape(m, n1, n2, n3, num_points=1000):
    pad=int(0.05*num_points)
    phi = np.linspace(0, 2 * np.pi, num_points)
    n1_safe = np.where(np.abs(n1) < 1e-10, 1e-10, n1)
    r = (np.abs(np.cos(m * phi / 4) / 1) ** n2 + np.abs(np.sin(m * phi / 4) / 1) ** n3) ** (-1 / n1_safe)
    x = r * np.cos(phi)
    y = r * np.sin(phi)
    return x[pad:(num_points-pad)], y[pad:(num_points-pad)]

def transform(x, y, 
              offset_x=0.0, 
              offset_y=0.0, 
              scale_x=1.0, 
              scale_y=1.0, 
              rotation_deg=0.0):
    """
    Applies translation, scaling, and rotation to an array of coordinates.
    x, y should be 1D arrays of the same length.
    """
    theta = np.radians(rotation_deg)
    # Scale
    x_s = x * scale_x
    y_s = y * scale_y
    # Rotate
    x_r = x_s * np.cos(theta) - y_s * np.sin(theta)
    y_r = x_s * np.sin(theta) + y_s * np.cos(theta)
    # Translate
    x_t = x_r + offset_x
    y_t = y_r + offset_y
    return x_t, y_t

# --- Main plotting routine ---

fig, ax = plt.subplots(figsize=(8, 4))



# Get our base shape
x_base, y_top_base = base_shape(base_m, base_n1, base_n2, base_n3, num_points=300)

# Number of shapes to plot
n_shapes = 2000
freq = 4
tau = n_shapes // freq

# Use a color map across all shapes
from matplotlib import colormaps

my_cmap = colormaps['PuRd']
colors = plt.cm.plasma(np.linspace(0, 1, n_shapes))

# Track the overall min/max for x and y so we can set the axis limits
min_x, max_x = float('inf'), float('-inf')
min_y, max_y = float('inf'), float('-inf')

num=14
from numpy.random import rand

np.random.seed(2183)



phasecol=[np.pi*0.5*rand() for _ in range(num)]
phasephs=[np.pi*0.5*rand() for _ in range(num)]


for inum in range(num):

    if inum % 2 == 0:
        # Even inum: forwards
        rng = range(0, n_shapes, 1)
    else:
        # Odd inum: backwards
        rng = range(n_shapes - 1, -1, -1)

    for i in rng:

        # Define how the offset, scaling, and rotation vary with i
        offset_x = num * (i / n_shapes)
        offset_y = 1 * np.sin(5*2*np.pi * (i / n_shapes +phasephs[inum])) +num-4*inum
        scale_x  = 0.75 + 0.25*np.sin(6*np.pi*(i/tau+phasecol[inum]))
        scale_y  = 1.0 + 0.25*np.sin(6*np.pi*(i/tau+phasecol[inum]))
        rotation_deg = 20*np.sin(6*np.pi*(i/tau+phasecol[inum]))

        # Apply transform to top and bottom curves
        x_top, y_top = transform(x_base, y_top_base,
                                offset_x, offset_y,
                                scale_x, scale_y,
                                rotation_deg)
       
        
        # If the shape got flipped in x, reorder so fill_between works properly
        if x_top[0] > x_top[-1]:
            x_top, y_top = x_top[::-1], y_top[::-1]
            

        # Fill between the top and bottom curves
        ax.fill(x_top, y_top, color=my_cmap(0.7*abs(np.sin(2*np.pi*(i/tau+phasecol[inum])))+0.3), alpha=1, linewidth=0)


        #int((int((n_shapes-1)*np.sin((i/tau)*np.pi))+1)*0.5)
        # Track min/max of all x and y
        min_x = min(min_x, x_top.min() )
        max_x = max(max_x, x_top.max() )
        min_y = min(min_y, y_top.min() )
        max_y = max(max_y, y_top.max() )

# Now set the axis limits based on min/max values
# ax.set_xlim(min_x, max_x)
# ax.set_ylim(min_y, max_y)
# ax.set_aspect('equal', 'datalim')
plt.axis('off')

from Releases.ismethods.check import unique_filename

import os

os.path.dirname(os.path.abspath(__file__))

grid_size=num+0.1
ax = plt.gca()
ax.set_xlim(0.0, grid_size)
ax.set_ylim(0,grid_size)
ax.set_aspect('equal', adjustable='box')

plt.savefig(unique_filename(os.path.dirname(os.path.abspath(__file__))+'/superformula_baseshape.png'), transparent=True, dpi=1200, bbox_inches='tight', pad_inches=0.0)
