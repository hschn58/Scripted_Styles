import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os

matplotlib.use('Agg')


def plot_color_gradients(category, cmap_list):
    """
    Create a figure showing a horizontal gradient for each colormap in cmap_list.
    
    Parameters:
        category (str): Name of the colormap group.
        cmap_list (list): List of colormap names (strings).
    
    Returns:
        fig (Figure): The Matplotlib figure containing the gradients.
    """
    n_maps = len(cmap_list)
    # Create a gradient array that goes from 0 to 1.
    # We use a 2-row array so the image is visible; the subplot height is controlled by figsize.
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))
    
    # Create a figure with one subplot per colormap.
    # Here, we set the width to 8 inches and the height to n_maps inches (~1 inch per map).
    fig, axes = plt.subplots(n_maps, 1, figsize=(8, n_maps))
    
    # If there's only one colormap in the group, wrap the axis in a list.
    if n_maps == 1:
        axes = [axes]
    
    # Adjust the subplot layout so there's room for the colormap names on the left.
    fig.subplots_adjust(left=0.25, right=0.99, top=0.95, bottom=0.05)
    
    # Plot each colormap as an image
    for ax, cmap_name in zip(axes, cmap_list):
        ax.imshow(gradient, aspect='auto', cmap=plt.get_cmap(cmap_name))
        # Label the colormap; place the name to the left of the gradient.
        ax.text(-0.01, 0.5, cmap_name, va='center', ha='right',
                transform=ax.transAxes, fontsize=10)
        ax.set_axis_off()
    
    # Give the entire figure a title corresponding to the colormap group.
    fig.suptitle(category, fontsize=14, y=1.02)
    
    return fig

# Define colormap groups and their colormap names.
# (This grouping is similar to Matplotlib’s documentation.)
cmaps = {
    "Perceptually Uniform Sequential": ['viridis', 'plasma', 'inferno', 'magma', 'cividis'],
    "Sequential": ['Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'binary',
                   'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu',
                   'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'],
    "Sequential (2)": ['afmhot', 'gist_heat', 'hot', 'cool', 'spring', 'summer',
                         'autumn', 'winter'],
    "Diverging": ['PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',
                  'RdYlGn', 'Spectral', 'coolwarm'],
    "Cyclic": ['twilight', 'twilight_shifted', 'hsv'],
    "Qualitative": ['Pastel1', 'Pastel2', 'Paired', 'Accent',
                    'Dark2', 'Set1', 'Set2', 'Set3'],
    "Miscellaneous": ['flag', 'prism', 'ocean', 'gist_earth', 'terrain',
                      'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix',
                      'brg', 'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar']
}

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# --- 1) Black -> Green -> Violet ---
# This will smoothly blend from black at low values to green in the midpoint, 
# then to violet at high values.



if __name__ == "__main__":
    dirname = os.path.dirname(__file__)
    for group_name, cmap_names in cmaps.items():
        fig = plot_color_gradients(group_name, cmap_names)
        plt.savefig(os.path.join(dirname, f'colormaps_{group_name}.jpg'), dpi=600)
