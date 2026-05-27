import numpy as np
import matplotlib.pyplot as plt




def get_axis_image_as_array(fig, ax):
    """
    Extract the color values of each pixel in the axis area as a 3D numpy array (RGBA).
    This version handles HiDPI/retina backends by using the renderer's actual pixel size.
    """
    # Force a draw so that fig.canvas and its renderer are up-to-date
    fig.canvas.draw()

    # Get bounding box of the axis in figure (nominal) pixel units
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    x0, y0, x1, y1 = [int(v) for v in bbox.extents * fig.dpi]
    
    # Get the actual rendered size from the renderer (often bigger on HiDPI screens)
    renderer = fig.canvas.get_renderer()
    real_width, real_height = int(renderer.width), int(renderer.height)

    # Also get the nominal width/height from fig.canvas
    nominal_w, nominal_h = fig.canvas.get_width_height()

    # Compute how much bigger the real buffer is vs. the nominal size
    scale_x = real_width / float(nominal_w)
    scale_y = real_height / float(nominal_h)

    # Now read the real RGBA buffer (already in RGBA order)
    buf = fig.canvas.buffer_rgba()
    image = np.frombuffer(buf, dtype=np.uint8).reshape((real_height, real_width, 4))

    # Scale the bounding box coords to match the real pixel buffer
    rx0 = int(x0 * scale_x)
    rx1 = int(x1 * scale_x)
    ry0 = int(y0 * scale_y)
    ry1 = int(y1 * scale_y)

    # Crop the axis region from the big RGBA image
    axis_image = image[ry0:ry1, rx0:rx1, :]
    return axis_image

def draw_waves(params):
    """
    Draws a complex grid of sine waves using the provided list of parameters.
    Each parameter value 'p' is used so that the curves are drawn as:
        x = x_base + amplitude*(1/p)*sin(p*y)
    (and similarly for the negative phase shift).
    
    Parameters:
        params (list of numbers): List of frequency parameters (e.g., [1, 2, 3, 4, ...])
    """
    # Set fixed parameters
    num_waves = 150
    vertical_lines = 5
    base_amplitude = 1.0
    base_phase = 0.5  # in radians
    dpi = 1200
    cmapp = "Greys"
    
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
    ax.set_aspect('equal')
    
    # Set up the colormaps
    cmap1 = plt.get_cmap(cmapp)
    cmap2 = plt.get_cmap(cmapp+"_r")
    cut = 1



    
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

                if p % 3 == 0:
                    cut = 1
                    
                    color = cmap1(cut * (i / num_waves) + (1 - cut) * 0.5)
                elif p % 3 == 1:
                    cut = 1

                    cmap3 = plt.get_cmap('rainbow')
                    color = cmap3(cut * (i / num_waves) + (1 - cut) * 0.5)


                else:
                    cut = 1
                    color = cmap2(cut * (i / num_waves) + (1 - cut) * 0.5)



                # --- Positive case: no extra phase shift ---
                # Vertical propagation: x oscillates about x_base, y runs over our domain.
                x_curve      = x_base + amplitude * (1 / p) * np.sin(p * y)
                x_curve_neg  = x_base - amplitude * (1 / p) * np.sin(p * y)
                # (The following duplicate variables are used in the original code; here they equal x_curve and x_curve_neg.)
                x_curve_sh   = x_curve
                x_curve_sh_n = x_curve_neg

                ax.plot(x_curve,      y, color=color, linewidth=0.5)
                ax.plot(x_curve_neg,  y, color=color, linewidth=0.5)
                ax.plot(x_curve_sh,   y, color=color, linewidth=0.5)
                ax.plot(x_curve_sh_n, y, color=color, linewidth=0.5)
                
                # Horizontal propagation: roles are swapped (y oscillates around x_base).
                ax.plot(y, x_curve,      color=color, linewidth=0.5)
                ax.plot(y, x_curve_neg,  color=color, linewidth=0.5)
                ax.plot(y, x_curve_sh,   color=color, linewidth=0.5)
                ax.plot(y, x_curve_sh_n, color=color, linewidth=0.5)
                
                # --- Negative case: add a phase shift of π ---
                x_curve      = x_base + amplitude * (1 / p) * np.sin(p * y + np.pi)
                x_curve_neg  = x_base - amplitude * (1 / p) * np.sin(p * y + np.pi)
                x_curve_sh   = x_curve
                x_curve_sh_n = x_curve_neg

                ax.plot(x_curve,      y, color=color, linewidth=0.5)
                ax.plot(x_curve_neg,  y, color=color, linewidth=0.5)
                ax.plot(x_curve_sh,   y, color=color, linewidth=0.5)
                ax.plot(x_curve_sh_n, y, color=color, linewidth=0.5)
                
                ax.plot(y, x_curve,      color=color, linewidth=0.5)
                ax.plot(y, x_curve_neg,  color=color, linewidth=0.5)
                ax.plot(y, x_curve_sh,   color=color, linewidth=0.5)
                ax.plot(y, x_curve_sh_n, color=color, linewidth=0.5)


    # Get image from axis




    #plt.imshow(ax, extent= [0, 1, 0, 1])

    delta = 0

    plt.axis('off')


    ax.set_xlim(x_dom_min-delta, x_dom_max+delta)
    ax.set_ylim(x_dom_min-delta, x_dom_max+delta)

    axis_image = get_axis_image_as_array(fig, ax)

    return axis_image
    
    #plt.savefig("sine_add_better.png", dpi=dpi, bbox_inches='tight', pad_inches=0)




# Combine via some pattern
pattern = lambda x, y: np.sin(x+y - np.pi/2) + np.cos(y-x)

h, w, _ = axis_image1.shape
axis_image_product = np.zeros_like(axis_image1)


pattern = lambda x,y: np.sin(x) + np.cos(y)

witer, hiter, _ = axis_image1.shape
param=1
freq=10
#var = add_rgba_colors_255(plain_blue[wi,hi],axis_image1[wi,hi])
for wi in range(witer):
    for hi in range(hiter):

        x = (wi/witer)*freq*2*np.pi
        y = (hi/hiter)*freq*2*np.pi

        if (pattern(x, y) >= 0) and (pattern(x, y) <= param) and (pattern(x+0.01, y+0.01) >= 0):
            axis_image_product[wi, hi, :] = axis_image1[wi, hi]

        elif (pattern(x, y) <= 0) and (pattern(x, y) >= -param) and (pattern(x+0.01, y+0.01) <= 0):
            axis_image_product[wi, hi, :] = axis_image2[wi,hi]

        else:
            axis_image_product[wi, hi, :] = axis_image3[wi,hi]


# Example usage:
if __name__ == "__main__":
    # This will draw waves for param values 1, 2, 3, 4, 5, and 6.
    draw_waves([1, 2, 3, 4, 5, 6])
