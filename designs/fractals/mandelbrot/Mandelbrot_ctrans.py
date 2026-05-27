
import numpy as np
from matplotlib.colors import ListedColormap, to_rgba
from matplotlib import cm

def ctrans(color):# Get the colormap object for the 'hsv' colormap
    cmap = cm.get_cmap(color)

    # Generate an array of values between 0 and 1
    values = np.linspace(0, 1, 512)

    # Convert the values to RGBA tuples
    colors = cmap(values)

    # Create a ListedColormap object using the list of colors
    listed_cmap = ListedColormap(colors)
    return listed_cmap