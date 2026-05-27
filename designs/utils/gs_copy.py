import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colors as mcolors

def blend_colors(c1, c2, t):
    return tuple((1 - t) * a + t * b for a, b in zip(c1, c2))

def create_custom_gist_stern_colormap(bump_color, center_color, highend_color, name=None):
    black = (0, 0, 0)
    white = (1, 1, 1)
    
    bump_rgb   = mcolors.to_rgb(bump_color)
    center_rgb = mcolors.to_rgb(center_color)
    highend_rgb = mcolors.to_rgb(highend_color)
    
    dark_center  = blend_colors(center_rgb, black, 0.5)
    light_center = blend_colors(center_rgb, white, 0.5)
    
    high_intermediate1 = blend_colors(light_center, highend_rgb, 0.4)
    high_intermediate2 = blend_colors(light_center, highend_rgb, 0.8)
    
    # Original bump region was: (0.09, black) -> (0.13, bump_rgb) -> (0.17, black)
    # To make the descent half as steep, we extend it so that:
    # (0.09, black) -> (0.13, bump_rgb) remains unchanged (rise over 0.04)
    # But then (0.13, bump_rgb) -> (0.21, black) spans 0.08 (half the slope)
    stops = [
        (0.00, black),
        (0.09, black),
        (0.13, bump_rgb),      # Peak of the bump (e.g. turquoise)
        (0.21, black),         # Extended descent to black (instead of 0.17)
        (0.30, dark_center),
        (0.50, center_rgb),    # Center color (e.g. purple)
        (0.70, light_center),
        (0.82, high_intermediate1),
        (0.92, high_intermediate2),
        (1.00, highend_rgb)    # High end (e.g. neon blue)
    ]
    
    if name is None:
        name = "custom_gist_stern"
    
    # Increase N to get a smoother colormap.
    cmap = LinearSegmentedColormap.from_list(name, stops, N=4096)
    return cmap

# Create the custom colormap using your specified colors:
# # - Bump: turquoise
# # - Center: purple
# # - High end: neon blue (hex "#04D9FF")
# cmap_custom = create_custom_gist_stern_colormap("turquoise", "purple", "#04D9FF",
#                                                 name="turquoise_purple_neonblue")

# # Create a gradient image for demonstration.
# gradient = np.linspace(0, 1, 4096)
# gradient = np.outer(np.ones(10), gradient)

# plt.figure(figsize=(6, 2))
# plt.imshow(gradient, aspect="auto", cmap=cmap_custom, interpolation="bilinear")
# plt.title("Custom Colormap: Turquoise Bump, Purple Center, Neon Blue High End")
# plt.axis("off")
# plt.show()
