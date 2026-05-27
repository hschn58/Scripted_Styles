import numpy as np
import matplotlib.pyplot as plt
import os
import argparse

parser = argparse.ArgumentParser(description="Process the PNG path argument for always run script")
parser.add_argument("--colormap", type=str, default = 'winter', help="Additional information for the process")  # Second positional argument
parser.add_argument("--facecolor", type=str, default = 'black', help="Additional information for the process")  # Second positional argument


args = parser.parse_args()

colormap = args.colormap
facecolor = args.facecolor

dpi = 2400
DESCRIPTIVE_KEYWORD = 'beauty_of_pattern'

def draw_waves(params, colormap, facecolor, dpi=2400, num_waves=800, vertical_lines=5, base_amplitude=1.0, base_phase=0.5):
    """
    Draws a complex grid of sine waves using the provided list of parameters.
    Each parameter value 'p' is used so that the curves are drawn as:
        x = x_base + amplitude*(1/p)*sin(p*y)
    (and similarly for the negative phase shift).
    
    Parameters:
        params (list of numbers): List of frequency parameters (e.g., [1, 2, 3, 4, ...])
    """
    # Set fixed parameters
    num_waves = num_waves
    vertical_lines = vertical_lines
    base_amplitude = base_amplitude  # in units of the domain
    base_phase = base_phase # in units of pi
    dpi = dpi
    
    
    # Define decrements so amplitude and phase decrease gradually
    amp_decrement = 1 / num_waves
    phase_decrement = 1 / num_waves
    
    # Define x positions for vertical lines.
    x_start = 0  
    separation = np.pi / 2
    x_positions = [x_start + i * separation for i in range(vertical_lines)]
    
    # Determine a square domain.
    x_dom_min = x_positions[0] - base_amplitude
    x_dom_max = x_positions[-1] + base_amplitude
    y = np.linspace(x_dom_min, x_dom_max, 1000)
    
    # Create a square canvas.
    fig, ax = plt.subplots(figsize=(10, 10), dpi=dpi)
    fig.patch.set_facecolor(facecolor)


    ax.set_aspect('equal')
    
    # Set up the colormaps
    cmap1 = plt.get_cmap(colormap)

    
    # Draw the strokes.
    for i in range(num_waves,-1, -1):
        amplitude = base_amplitude - i * amp_decrement
        phase = base_phase - i * phase_decrement  # (not used in this example, but kept for potential extension)
        
        for x_base in x_positions:
            # Alternate extra phase shift based on the wave index (used here only for choosing color)
            # if i % 2 == 0:
            #     cut = 1
            #     color = cmap1(cut * (i / num_waves) + (1 - cut) * 0.5)
            # else:
            #     cut = 0.8
            #     color = cmap2(cut * (i / num_waves) + (1 - cut) * 0.5)
            
            # Loop over each parameter value provided.
            for p in params:

                # if p % 3 == 0:
                #     cut = 1
                    
                #     color = cmap1(cut * (i / num_waves) + (1 - cut) * 0.5)
                # elif p % 3 == 1:
                #     cut = 1

                #     cmap3 = plt.get_cmap('rainbow')
                #     color = cmap3(cut * (i / num_waves) + (1 - cut) * 0.5)

                # else:
                #     cut = 1
                #     color = cmap2(cut * (i / num_waves) + (1 - cut) * 0.5)

                cut = 1
                color = cmap1(cut * (i / num_waves) + (1 - cut) * 0.5)

                # --- Positive case: no extra phase shift ---
                # Vertical propagation: x oscillates about x_base, y runs over our domain.
                x_curve      = x_base + amplitude * (1 / p) * np.sin(p * y)
                x_curve_neg  = x_base - amplitude * (1 / p) * np.sin(p * y)
                # (The following duplicate variables are used in the original code; here they equal x_curve and x_curve_neg.)
                x_curve_sh   = x_curve
                x_curve_sh_n = x_curve_neg

                ax.plot(x_curve,      y, color=color, linewidth=0.1)
                ax.plot(x_curve_neg,  y, color=color, linewidth=0.1)
                ax.plot(x_curve_sh,   y, color=color, linewidth=0.1)
                ax.plot(x_curve_sh_n, y, color=color, linewidth=0.1)
                
                # Horizontal propagation: roles are swapped (y oscillates around x_base).
                ax.plot(y, x_curve,      color=color, linewidth=0.1)
                ax.plot(y, x_curve_neg,  color=color, linewidth=0.1)
                ax.plot(y, x_curve_sh,   color=color, linewidth=0.1)
                ax.plot(y, x_curve_sh_n, color=color, linewidth=0.1)
                
                # --- Negative case: add a phase shift of π ---
                x_curve      = x_base + amplitude * (1 / p) * np.sin(p * y + np.pi)
                x_curve_neg  = x_base - amplitude * (1 / p) * np.sin(p * y + np.pi)
                x_curve_sh   = x_curve
                x_curve_sh_n = x_curve_neg

                ax.plot(x_curve,      y, color=color, linewidth=0.1)
                ax.plot(x_curve_neg,  y, color=color, linewidth=0.1)
                ax.plot(x_curve_sh,   y, color=color, linewidth=0.1)
                ax.plot(x_curve_sh_n, y, color=color, linewidth=0.1)
                
                ax.plot(y, x_curve,      color=color, linewidth=0.1)
                ax.plot(y, x_curve_neg,  color=color, linewidth=0.1)
                ax.plot(y, x_curve_sh,   color=color, linewidth=0.1)
                ax.plot(y, x_curve_sh_n, color=color, linewidth=0.1)


    # Get image from axis


    #plt.imshow(ax, extent= [0, 1, 0, 1])

    delta = 0

    plt.axis('off')


    ax.set_xlim(x_dom_min-delta, x_dom_max+delta)
    ax.set_ylim(x_dom_min-delta, x_dom_max+delta)






# This will draw waves for param values 1, 2, 3, 4, 5, and 6.


draw_waves([1, 2, 3, 4], colormap = colormap, facecolor = facecolor , dpi=dpi)

from ScriptedStyles.Designs.Releases.ismethods.check import unique_filename

dirname = os.path.dirname(__file__)

# Define the path to the images folder
images_dir = os.path.join(dirname, 'images')

# Check if the folder exists; if not, create it.
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

# Create the filename in the images folder.
#"name "filename = os.path.basename(__file__).split('.')[0] + '.jpg'
code_name = DESCRIPTIVE_KEYWORD + '.jpg'

filename = unique_filename(os.path.join(images_dir, code_name))
plt.savefig(filename, dpi=dpi, bbox_inches='tight', pad_inches=0.0)

import pandas as pd

df = pd.read_csv('product_information.csv')
df['local_path'].iloc[0] = filename
df.to_csv('product_information.csv', index=False)





