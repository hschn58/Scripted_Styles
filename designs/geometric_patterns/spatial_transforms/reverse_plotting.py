import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# Shapely for merging polygons
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

def base_shape(num_points=200):
    """
    Returns x, y_top, y_bottom for a lobed shape.
    In this example, we use a Gaussian-like shape: y = exp(-x^2).
    """
    x = np.linspace(-2, 2, num_points)
    y = np.exp(-x**2)
    return x, y, -y

def transform(x, y, 
              offset_x=0.0, 
              offset_y=0.0, 
              scale_x=1.0, 
              scale_y=1.0, 
              theta=0.0):
    """
    Applies translation, scaling, and rotation to an array of coordinates.
    x, y should be 1D arrays of the same length.
    """
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


# ------------------------------------------------------------------------
# Main plotting routine
# ------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 6))

# Get base shape
x_base, y_top_base, y_bot_base = base_shape(num_points=300)

# Set up
freq = 5           # number of shapes around the circle
R = 10             # radial distance
n_shapes = 2000    
partition = n_shapes // freq

# Color map
my_cmap = cm.get_cmap("plasma")

# Track overall min/max to set axis bounds later
min_x = float("inf")
max_x = float("-inf")
min_y = float("inf")
max_y = float("-inf")

# ------------------------------------------------------------------
# (1) PLOT THE SPIRAL FIRST
# ------------------------------------------------------------------
num1 = 1500
inc = 2*np.pi/freq

for j in range(freq):
    for iter in range(num1):
        # Spiral transform
        offset_x = R * np.cos(2*np.pi*(iter/num1) + inc*j) * (1 - (iter/num1))
        offset_y = R * np.sin(2*np.pi*(iter/num1) + inc*j) * (1 - (iter/num1))
        scale_x  = abs(0.2*np.sin(abs(freq*3)*2*np.pi*(iter/num1)) + 1)
        scale_y  = abs(0.2*np.sin(abs(freq*3)*2*np.pi*(iter/num1)) + 1)
        rotation_deg = (np.pi/9)*np.sin(2*np.pi*(iter/num1))

        x_top2, y_top2 = transform(x_base, y_top_base,
                                   offset_x, offset_y,
                                   scale_x, scale_y,
                                   rotation_deg)
        x_bot2, y_bot2 = transform(x_base, y_bot_base,
                                   offset_x, offset_y,
                                   scale_x, scale_y,
                                   rotation_deg)

        # Reorder if flipped in x
        if x_top2[0] > x_top2[-1]:
            x_top2, y_top2 = x_top2[::-1], y_top2[::-1]
            x_bot2, y_bot2 = x_bot2[::-1], y_bot2[::-1]

        # Fill
        ax.fill_between(
            x_top2*(1 - (iter/num1)),
            y_top2*(1 - (iter/num1)),
            y_bot2*(1 - (iter/num1)),
            color=my_cmap(
                (1 - (iter/num1)) + 0.1*np.sin(10*np.pi*(iter/num1))
            ),
            alpha=1, linewidth=0
        )

        # Update min/max
        min_x = min(min_x, x_top2.min(), x_bot2.min())
        max_x = max(max_x, x_top2.max(), x_bot2.max())
        min_y = min(min_y, y_top2.min(), y_bot2.min())
        max_y = max(max_y, y_top2.max(), y_bot2.max())


# ------------------------------------------------------------------
# (2) BUILD A SINGLE, CONTINUOUS OUTER RIM
# ------------------------------------------------------------------

outer_polys = []

# We'll again use freq and partition to position shapes around the circle
inc = 2*np.pi / freq
for i in range(partition):
    for j in range(freq):
        offset_x = R * np.cos(2*np.pi*(i/n_shapes) + inc*j)
        offset_y = R * np.sin(2*np.pi*(i/n_shapes) + inc*j)
        scale_x  = 0.5 * np.sin((freq+0.25)*2*np.pi*(i/partition)) + 1
        scale_y  = 0.5 * np.sin((freq+0.25)*2*np.pi*(i/partition)) + 1
        rotation_deg = (np.pi/9)*np.sin(2*np.pi*(i/partition))

        # Transform top/bottom
        x_top, y_top = transform(x_base, y_top_base,
                                 offset_x, offset_y,
                                 scale_x, scale_y,
                                 rotation_deg)
        x_bot, y_bot = transform(x_base, y_bot_base,
                                 offset_x, offset_y,
                                 scale_x, scale_y,
                                 rotation_deg)
        
        # Reorder if flipped
        if x_top[0] > x_top[-1]:
            x_top, y_top = x_top[::-1], y_top[::-1]
            x_bot, y_bot = x_bot[::-1], y_bot[::-1]

        # Build a polygon from top curve forward, bottom curve backward
        top_coords = np.column_stack((x_top, y_top)) 
        bot_coords = np.column_stack((x_bot[::-1], y_bot[::-1]))
        boundary_coords = np.vstack((top_coords, bot_coords))

        # Make a Shapely polygon
        poly = Polygon(boundary_coords)
        outer_polys.append(poly)

# Union all those polygons into one continuous shape
outer_union = unary_union(outer_polys)

# The union can be a MultiPolygon if it somehow breaks into multiple pieces,
# but likely it's just one. We'll handle both cases anyway.
if isinstance(outer_union, MultiPolygon):
    # Plot each piece
    for subpoly in outer_union:
        x_, y_ = subpoly.exterior.xy
        ax.fill(x_, y_, color="white")  # or any color
        # Update bounds
        min_x = min(min_x, np.min(x_))
        max_x = max(max_x, np.max(x_))
        min_y = min(min_y, np.min(y_))
        max_y = max(max_y, np.max(y_))
else:
    # Single polygon
    x_, y_ = outer_union.exterior.xy
    ax.fill(x_, y_, color="white")  
    # ^ you can replace "white" with something else if you prefer
    min_x = min(min_x, np.min(x_))
    max_x = max(max_x, np.max(x_))
    min_y = min(min_y, np.min(y_))
    max_y = max(max_y, np.max(y_))


# ------------------------------------------------------------------
# Final axis limits
# ------------------------------------------------------------------
ax.set_xlim(min_x, max_x)
ax.set_ylim(min_y, max_y)
ax.set_aspect("equal", "datalim")
plt.axis("off")
plt.show()
