import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import LinearSegmentedColormap, hsv_to_rgb, rgb_to_hsv

matplotlib.use('AGG')

dpi = 600
figlen = 10
def create_opposite_colormap(original_cmap):
    # Same as before
    n_samples = 256
    original_colors = original_cmap(np.linspace(0, 1, n_samples))
    hsv_colors = rgb_to_hsv(original_colors[:, :3])
    hsv_colors[:, 0] = (hsv_colors[:, 0] + 0.5) % 1.0
    opposite_colors = hsv_to_rgb(hsv_colors)
    opposite_cmap = LinearSegmentedColormap.from_list("opposite_cmap", opposite_colors)
    return opposite_cmap

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


def base_shape(num_points=200):
    x = np.linspace(-2, 2, num_points)
    y = np.exp(-x**2)
    return x, y, -y

def transform(x, y, offset_x=0.0, offset_y=0.0, scale_x=1.0, scale_y=1.0, rotation_deg=0.0):
    theta = np.radians(rotation_deg)
    x_s = x * scale_x
    y_s = y * scale_y
    x_r = x_s * np.cos(theta) - y_s * np.sin(theta)
    y_r = x_s * np.sin(theta) + y_s * np.cos(theta)
    x_t = x_r + offset_x
    y_t = y_r + offset_y
    return x_t, y_t

def render_quilt_image(colormap, seed, dpi, num=14, n_shapes=2000, figlen=figlen):
    """
    Renders one set of shapes with the specified colormap/seed and returns the RGBA array.
    """
    np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(figlen, figlen), dpi=dpi)
    ax.set_position([0, 0, 1, 1])  # Fill the entire figure

    x_base, y_top_base, y_bot_base = base_shape(num_points=300)
    freq = 4
    tau = n_shapes // freq

    phasecol = [np.pi *0.5* np.random.rand() for _ in range(num)]
    phasephs = [np.pi *0.5* np.random.rand() for _ in range(num)]

    for inum in range(num):
        if inum % 2 == 0:
            rng = range(0, n_shapes, 1)
        else:
            rng = range(n_shapes - 1, -1, -1)

        for i in rng:
            offset_x = num * (i / n_shapes)
            offset_y = (1 * np.sin(5*2*np.pi*(i/n_shapes + phasephs[inum])) 
                        + num - 1*inum)
            scale_x  = 0.75 + 0.25*np.sin(6*np.pi*(i/tau + phasecol[inum]))
            scale_y  = 1.0 + 0.25*np.sin(6*np.pi*(i/tau + phasecol[inum]))
            rotation_deg = 5*np.sin(6*np.pi*(i/tau + phasecol[inum]))

            x_top, y_top = transform(x_base, y_top_base,
                                     offset_x, offset_y,
                                     scale_x, scale_y,
                                     rotation_deg)
            x_bot, y_bot = transform(x_base, y_bot_base,
                                     offset_x, offset_y,
                                     scale_x, scale_y,
                                     rotation_deg)

            # Ensure fill_between works (left-to-right)
            if x_top[0] > x_top[-1]:
                x_top, y_top = x_top[::-1], y_top[::-1]
                x_bot, y_bot = x_bot[::-1], y_bot[::-1]

            c = colormap(0.7*abs(np.sin(2*np.pi*(i/tau+phasecol[inum]))) + 0.3)
            ax.fill_between(x_top, y_top, y_bot, color=c, alpha=1, linewidth=0)

    ax.set_xlim(0.0, num)
    ax.set_ylim(0, num)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')

    # Get image from axis
    axis_image = get_axis_image_as_array(fig, ax)

    plt.close(fig)  # Close the figure so it doesn't display
    return axis_image

# ---------------------------------------------------------------------
# Example usage: produce two images, then combine them
# ---------------------------------------------------------------------

original_cmap = plt.cm.plasma
opposite_cmap = create_opposite_colormap(original_cmap)
final_cmap = matplotlib.colormaps['turbo']

# Render the first set
axis_image1 = render_quilt_image(colormap=original_cmap, seed=2183, dpi=dpi)
# Render the second set
axis_image2 = render_quilt_image(colormap=opposite_cmap, seed=2183, dpi=dpi)

axis_image3 = render_quilt_image(colormap=final_cmap, seed=2183, dpi=dpi)

# Combine via some pattern
pattern = lambda x, y: np.sin(x) + np.cos(y)

h, w, _ = axis_image1.shape
axis_image_product = np.zeros_like(axis_image1)


pattern = lambda x,y: np.sin(x) + np.cos(y)

param=1
freq=10

witer, hiter, _ = axis_image1.shape


#var = add_rgba_colors_255(plain_blue[wi,hi],axis_image1[wi,hi])
for wi in range(witer):
    for hi in range(hiter):

        x = (wi/witer)*freq*np.pi
        y = (hi/hiter)*freq*np.pi

        if (pattern(x, y) > 0) and (pattern(x, y) <= param):
            axis_image_product[wi, hi, :] = axis_image1[wi, hi]

        elif (pattern(x, y) <= 0) and (pattern(x, y) >= -param):
            axis_image_product[wi, hi, :] = axis_image2[wi,hi]

        else:
            axis_image_product[wi, hi, :] = axis_image3[wi,hi]
        
from Releases.ismethods.check import unique_filename

import os

dirname = os.path.dirname(__file__)
filename = unique_filename( os.path.join(dirname, 'quilt_test.png'))
# Display or save
plt.imshow(axis_image_product)
plt.axis('off')
plt.savefig(
    filename,
    dpi=1200,
    bbox_inches='tight',
    pad_inches=0.0,
    transparent=True
)

