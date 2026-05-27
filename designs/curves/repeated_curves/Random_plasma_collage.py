import numpy as np
import matplotlib.pyplot as plt

# def base_shape(num_points=200):
#     """
#     Returns x, y_top, y_bottom for a lobed shape.
#     In this example, we use a Gaussian-like shape: y = exp(-x^2).
#     """
#     x = np.linspace(-2, 2, num_points)
#     y = np.exp(-x**2)
#     return x, y

def base_shape(num_points=200):
    x = np.linspace(-2, 2, num_points)
    y = np.zeros_like(x)
    return x, y

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
fig, ax = plt.subplots(figsize=(10, 10))

# Get our base shape
x_base, y_base = base_shape(num_points=300)



# Number of shapes to plot
n_shapes = 2000
freq = 4
tau = n_shapes // freq

# Use a color map across all shapes
from matplotlib import colormaps

my_cmap = colormaps['plasma']
colors = plt.cm.plasma(np.linspace(0, 1, n_shapes))

# Track the overall min/max for x and y so we can set the axis limits
min_x, max_x = float('inf'), float('-inf')
min_y, max_y = float('inf'), float('-inf')

num=7
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
        offset_y = 2 * np.sin(2*2*np.pi * (i / n_shapes +phasephs[inum])) +num-3*inum
        scale_x  = 0.75 + 0.25*np.sin(6*np.pi*(i/tau+phasecol[inum]))
        scale_y  = 1.0 + 0.25*np.sin(6*np.pi*(i/tau+phasecol[inum]))
        rotation_deg = 20*np.sin(6*np.pi*(i/tau+phasecol[inum]))

        # Apply transform to top and bottom curves
        x, y = transform(x_base, y_base,
                        offset_x, offset_y,
                        scale_x, scale_y,
                        rotation_deg)
        
        # If the shape got flipped in x, reorder so fill_between works properly
        
        # Fill between the top and bottom curves
        plt.plot(x, y, color=my_cmap(0.7*abs(np.sin(2*np.pi*(i/tau+phasecol[inum])))+0.3), linewidth=1)


        #int((int((n_shapes-1)*np.sin((i/tau)*np.pi))+1)*0.5)
        # Track min/max of all x and y


# Now set the axis limits based on min/max values

# ax.set_aspect('equal', 'datalim')
plt.axis('off')

import os

os.path.dirname(os.path.abspath(__file__))

grid_size=num+0.1
ax = plt.gca()
# ax.set_xlim(0.0, grid_size)
# ax.set_ylim(0,grid_size)
# ax.set_aspect('equal', adjustable='box')

plt.savefig(os.path.dirname(os.path.abspath(__file__))+'/lines.jpg', transparent=True, dpi=1200, bbox_inches='tight', pad_inches=0.0)
