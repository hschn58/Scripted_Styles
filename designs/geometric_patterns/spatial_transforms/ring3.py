import numpy as np
import matplotlib.pyplot as plt

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

# --- Main plotting routine ---
fig, ax = plt.subplots(figsize=(8, 4))

# Get our base shape
x_base, y_top_base, y_bot_base = base_shape(num_points=300)

# Number of shapes to plot
n_shapes = 2000

# Use a color map across all shapes
import matplotlib.cm as cm
my_cmap = cm.get_cmap('plasma')
colors = plt.cm.plasma(np.linspace(0, 1, n_shapes))

# Track the overall min/max for x and y so we can set the axis limits
min_x, max_x = float('inf'), float('-inf')
min_y, max_y = float('inf'), float('-inf')

R = 10
freq = 5
inc = 2 * np.pi / freq
partition = n_shapes // freq

# First transform: forms the ring.
for i in range(partition):
    for j in range(freq):
        # Define parameters for the ring
        angle = 2 * np.pi * (i / n_shapes) + inc * j
        offset_x = R * np.cos(angle) - 0.75
        offset_y = R * np.sin(angle)
        scale_x = 0.5 * np.sin((freq + 0.25) * 2 * np.pi * (i / partition)) + 1
        scale_y = 0.5 * np.sin((freq + 0.25) * 2 * np.pi * (i / partition)) + 1
        rotation = (np.pi / 9) * np.sin(2 * np.pi * (i / partition))

        # Transform both top and bottom curves
        x_top, y_top = transform(x_base, y_top_base,
                                 offset_x, offset_y,
                                 scale_x, scale_y,
                                 rotation)
        x_bot, y_bot = transform(x_base, y_bot_base,
                                 offset_x, offset_y,
                                 scale_x, scale_y,
                                 rotation)
        
        # If the shape got flipped in x, reorder so fill_between works properly
        if x_top[0] > x_top[-1]:
            x_top, y_top = x_top[::-1], y_top[::-1]
            x_bot, y_bot = x_bot[::-1], y_bot[::-1]

        ax.fill_between(x_top, y_top, y_bot, color=my_cmap(np.sin(10 * np.pi * (i / partition))), alpha=1, linewidth=0)

        # Update overall min/max for later axis limits
        min_x = min(min_x, x_top.min(), x_bot.min())
        max_x = max(max_x, x_top.max(), x_bot.max())
        min_y = min(min_y, y_top.min(), y_bot.min())
        max_y = max(max_y, y_top.max(), y_bot.max())

# Second transform: draw 5 inward-spiraling paths that start exactly at the endpoints.
# For each endpoint (one per j), we know the endpoint from the last iteration of the ring (i == partition - 1).
for j in range(freq):
    # Compute the endpoint position exactly as in the first transform for i = partition-1.
    endpoint_angle = 2 * np.pi * ((partition - 1) / n_shapes) + inc * j
    endpoint_x = R * np.cos(endpoint_angle) - 0.75
    endpoint_y = R * np.sin(endpoint_angle)
    
    # For each path, iterate over a new parameter "iter" that goes from 0 to n_shapes.
    for iter in range(n_shapes):
        t = iter / n_shapes  # t goes from 0 (start) to 1 (end)
        
        # For a smooth spiral:
        # 1. Let the radial distance shrink linearly from the endpoint's distance to zero.
        # 2. Add extra rotation (e.g., one full extra turn) over the course of the spiral.
        r_endpoint = np.hypot(endpoint_x, endpoint_y)
        r = r_endpoint * (1 - t)
        extra_angle = 2 * np.pi * t  # change this multiplier to adjust the twist
        # The spiral angle is the original endpoint angle plus the extra rotation.
        spiral_angle = endpoint_angle + extra_angle
        
        # Use these as the offsets.
        spiral_offset_x = r * np.cos(spiral_angle)
        spiral_offset_y = r * np.sin(spiral_angle)
        
        # You can also vary scale and rotation if desired.
        scale_x = 0.5 * np.sin(freq * 3 * 2 * np.pi * t) + 1
        scale_y = 0.5 * np.sin(freq * 3 * 2 * np.pi * t) + 1
        rotation = (np.pi / 9) * np.sin(2 * np.pi * t + 2 * np.pi * ((n_shapes - 1) / n_shapes))
        
        # Apply transform with the spiral offset.
        x_top, y_top = transform(x_base, y_top_base,
                                 spiral_offset_x, spiral_offset_y,
                                 scale_x, scale_y,
                                 rotation)
        x_bot, y_bot = transform(x_base, y_bot_base,
                                 spiral_offset_x, spiral_offset_y,
                                 scale_x, scale_y,
                                 rotation)
        
        if x_top[0] > x_top[-1]:
            x_top, y_top = x_top[::-1], y_top[::-1]
            x_bot, y_bot = x_bot[::-1], y_bot[::-1]
        
        # Draw the shape along the spiral.
        # (Now we no longer multiply the coordinates by (1-t) because the offset already interpolates the path.)
        ax.fill_between(x_top, y_top, y_bot, 
                        color=my_cmap((1 - t) + 0.1 * np.sin(10 * np.pi * t)), 
                        alpha=1, linewidth=0, zorder=2)
        
        # Update overall min/max values if needed.
        min_x = min(min_x, x_top.min(), x_bot.min())
        max_x = max(max_x, x_top.max(), x_bot.max())
        min_y = min(min_y, y_top.min(), y_bot.min())
        max_y = max(max_y, y_top.max(), y_bot.max())

ax.set_xlim(min_x, max_x)
ax.set_ylim(min_y, max_y)
ax.set_aspect('equal', 'datalim')
plt.axis('off')
plt.show()
