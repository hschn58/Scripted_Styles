import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import argparse
import os
import matplotlib
from matplotlib.colors import LogNorm, PowerNorm
import matplotlib.colors as mcolors
import time
import pandas as pd

# For turtle integration and image conversion:
import io
from PIL import Image

start = time.time()

# Use non-interactive Agg backend for saving the Matplotlib figure.
#matplotlib.use('Agg')

# --------------------------------------------------------------------------
# Global parameters
# --------------------------------------------------------------------------
color_detail = 4096
freq = 3
cmap_fraction = 1
linewidth = 1 
flower_types = ['rose', 'daisy', 'spiral', 'lily', 'dahlia', 'superformula']
size = 1000
dpi = 300


#plasma daisy is a keeper


cmap_custom = None
from ScriptedStyles.Designs.Releases.ismethods.gs_copy import create_custom_gist_stern_colormap

# --------------------------------------------------------------------------
# Argparse for command-line parameters.
# --------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Generate a fun quilt with different flower types.')
parser.add_argument('--color', type=str, default='Accent_r', help='Colormap name')
parser.add_argument('--sigfreq', type=float, default=8.5*(1000/512), help='Gaussian sigma frequency factor')
parser.add_argument('--freq', type=float, default=5, help='Frequency parameter')
parser.add_argument('--flower', type=str, default='turtle', help='Flower type (e.g., rose, daisy, spiral, lily, dahlia, or superformula)')
# New flag to overlay turtle‐drawn symmetric shapes.
parser.add_argument('--turtle', action='store_true', default = True, help='Overlay a turtle-drawn symmetric shape')
args = parser.parse_args()

colormapp = args.color
sigfreq = args.sigfreq
freq = args.freq
flower = args.flower


# --------------------------------------------------------------------------
# Colormap setup using a cyclic triangle wave modulation.
# --------------------------------------------------------------------------
def triangle_wave(t, period=1, amplitude=1, decay=1):
    t = np.asarray(t)
    decay_rate = decay * (amplitude/np.max(t))
    wave = 2 * np.abs(2 * (t / period - np.floor(t / period + 0.5))) - 1
    return wave

def triangle_wave_tdown(t, period=1, amplitude=1, decay=1):
    t = np.asarray(t)
    wave = 1.1 * np.abs(2 * (t / period - np.floor(t / period + 0.5))) - (1.1/2) + (0.45 - 0.9*(t/np.max(t)))
    return wave

if cmap_custom:
    binary_cmap = cmap_custom
else:
    binary_cmap = plt.get_cmap(colormapp)

N = color_detail
x_vals = np.linspace(0, 1, N)
cyclic_map = cmap_fraction * (0.5*(1 + triangle_wave(t=freq * np.pi * x_vals, period=np.pi, amplitude=1)))
cyclic_colors = binary_cmap(cyclic_map)
cyclic_binary = mcolors.ListedColormap(cyclic_colors, name="cyclic_binary")

# --------------------------------------------------------------------------
# Standard flower density generation function.
# --------------------------------------------------------------------------
def generate_detailed_flower_density(size, flower_type='rose', petal_count=5, 
                                     thickness=0.01, scale=0.8,
                                     detail_amplitude=0.05, detail_frequency=20, detail_phase=0):
    """
    Generate a 2D density matrix encoding a flower pattern with extra fine detail.
    """
    # Create coordinate grid in [-1, 1] for both x and y.
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)
    
    # Convert to polar coordinates.
    R = np.sqrt(X**2 + Y**2)
    Theta = np.arctan2(Y, X)
    Theta = np.mod(Theta, 2 * np.pi)
    
    # Compute base target radius (r_base) as a function of theta.
    if flower_type.lower() == 'rose':
        r_base = scale * np.abs(np.cos(petal_count * Theta))
    elif flower_type.lower() == 'daisy':
        r_base = scale * (0.5 + 0.5 * np.cos(petal_count * Theta))
    elif flower_type.lower() == 'spiral':
        r_base = scale * Theta / (2 * np.pi)
    elif flower_type.lower() == 'lily':
        sigma = np.pi / 8
        r_base = scale * (0.3 + 0.7 * np.exp(-((Theta - np.pi)**2) / (2 * sigma**2)))
    elif flower_type.lower() == 'tulip':
        r_base = scale * (0.4 + 0.6 * np.abs(np.sin(petal_count * Theta + np.pi/6))**0.8)
    elif flower_type.lower() == 'dahlia':
        r_base = scale * (0.35 + 0.65 * np.abs(np.cos(petal_count * Theta))**1.2)
    else:
        r_base = scale * np.ones_like(Theta)
    
    # Add high-frequency modulation for petal detail.
    detail_modulation = detail_amplitude * np.cos(detail_frequency * Theta + detail_phase)
    flower_r = r_base + detail_modulation
    flower_r = np.clip(flower_r, 0, scale)
    
    # Create density field: high where R is near flower_r.
    density = np.exp(-((R - flower_r)**2) / (2 * thickness**2))
    density[R > scale] = 0
    return density

# --------------------------------------------------------------------------
# Superformula function (for the superformula flower option).
# --------------------------------------------------------------------------
def superformula(m, n1, n2, n3, points=5000):
    """
    Generate (x, y) points using the superformula.
    """
    phi = np.linspace(0, 2 * np.pi, points)
    n1_safe = np.where(np.abs(n1) < 1e-10, 1e-10, n1)
    r = (np.abs(np.cos(m * phi / 4))**n2 + np.abs(np.sin(m * phi / 4))**n3)**(-1 / n1_safe)
    x = r * np.cos(phi)
    y = r * np.sin(phi)
    return x, y

# --------------------------------------------------------------------------
# (Optional) Dahlia petal outlines function.
# --------------------------------------------------------------------------
def draw_dahlia_outline(petal_count=5, scale=0.8, offsets=[0, 0.005, -0.005], 
                        color='black', line_width=0.7):
    theta = np.linspace(0, 2 * np.pi, 2000)
    for off in offsets:
        r = scale * (0.35 + 0.65 * np.abs(np.cos(petal_count * (theta + off)))**1.2)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        plt.plot(x, y, color=color, linewidth=line_width)

# --------------------------------------------------------------------------
# Function to generate a turtle-drawn symmetric shape and return it as a PIL image.
# --------------------------------------------------------------------------
def get_turtle_drawing_as_image():
    import turtle  # local import
    # Create a turtle screen and hide the window (we'll capture its canvas).
    ts = turtle.Screen()
    ts.setup(width=400, height=400)
    ts.bgcolor("white")
    t = turtle.Turtle()
    t.speed(0)
    t.hideturtle()
    # Example symmetric drawing: draw a flower-like shape by drawing many circles.
    for i in range(36):
        t.circle(100)
        t.left(10)
    ts.update()
    # Capture the canvas as PostScript.
    canvas = ts.getcanvas()
    ps = canvas.postscript(colormode='color')
    # Convert the PostScript image to a PIL Image.
    image = Image.open(io.BytesIO(ps.encode('utf-8')))
    # Convert white background to transparent.
    image = image.convert("RGBA")
    data = np.array(image)
    r, g, b, a = data.T
    white_areas = (r > 240) & (g > 240) & (b > 240)
    data[..., 3][white_areas] = 0
    image = Image.fromarray(data)
    ts.bye()
    return image

# --------------------------------------------------------------------------
# Main image generation.
# --------------------------------------------------------------------------
fig = plt.figure(figsize=(10, 10))

if flower.lower() == 'superformula':
    # --- Generate heatmap using superformula curves ---
    base_m  = 7
    base_n1 = 0.9
    base_n2 = 0.9
    base_n3 = 0.9
    increment = 0.1
    iterations = int(base_n1 / increment)
    
    all_x_list = []
    all_y_list = []
    for i in range(iterations):
        m = base_m
        n1 = base_n1 - i * increment
        n2 = base_n2
        n3 = base_n3
        x, y = superformula(m, n1, n2, n3)
        all_x_list.append(x)
        all_y_list.append(y)
    
    all_x = np.concatenate(all_x_list)
    all_y = np.concatenate(all_y_list)
    
    buffer = 0.1
    x_min, x_max = all_x.min() - buffer, all_x.max() + buffer
    y_min, y_max = all_y.min() - buffer, all_y.max() + buffer
    
    bins = size
    heatmap, xedges, yedges = np.histogram2d(all_x, all_y, bins=bins, 
                                              range=[[x_min, x_max], [y_min, y_max]])
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    
    path_density = gaussian_filter(heatmap, sigma=sigfreq * linewidth * linewidth, 
                                   truncate=6, mode='wrap')
    plt.imshow(path_density, cmap=cyclic_binary, origin='lower', extent=extent,
               norm=LogNorm(vmin=np.min(path_density[path_density > 0]), vmax=np.max(path_density)))
else:
    # --- Generate heatmap using standard flower density ---
    density = generate_detailed_flower_density(
        size,
        flower_type=flower,
        petal_count=5,
        thickness=0.01,
        scale=0.8,
        detail_amplitude=0.05,
        detail_frequency=20,
        detail_phase=0
    )
    path_density = gaussian_filter(density, sigma=sigfreq * linewidth * linewidth, 
                                   truncate=6, mode='wrap')
    plt.imshow(path_density, cmap=cyclic_binary, origin='lower', extent=[-1, 1, -1, 1],
               norm=PowerNorm(gamma=0.7, vmin=np.min(path_density), vmax=np.max(path_density)))

plt.axis('off')

# Optionally overlay additional outlines for "dahlia"
if flower.lower() == 'dahlia':
    draw_dahlia_outline(petal_count=5, scale=0.8, offsets=[0, 0.005, -0.005],
                        color='black', line_width=0.7)

# --------------------------------------------------------------------------
# If --turtle flag is provided, overlay a turtle-drawn symmetric shape.
# --------------------------------------------------------------------------
if args.turtle:
    turtle_img = get_turtle_drawing_as_image()
    # Convert the PIL image to a numpy array.
    turtle_np = np.array(turtle_img)
    # Overlay the turtle image on the same coordinate extent.
    # (Adjust extent and alpha as needed.)
    plt.imshow(turtle_np, extent=[-1, 1, -1, 1], alpha=0.6)

# --------------------------------------------------------------------------
# Save the final image.
# --------------------------------------------------------------------------
from ScriptedStyles.Designs.Releases.ismethods.check import unique_filename

dirname = os.path.dirname(__file__)
images_dir = os.path.join(dirname, 'images')
if not os.path.exists(images_dir):
    os.makedirs(images_dir)
filename = unique_filename(os.path.join(images_dir, 'fun_quilt.jpg'))
#filename = 'fig.jpg'
plt.savefig(filename, dpi=dpi, bbox_inches='tight', pad_inches=0.0)

end = time.time()
print('Time taken:', end - start)

plt.axis('off')
plt.tight_layout()

# --------------------------------------------------------------------------
# Update the product information CSV.
# --------------------------------------------------------------------------
df = pd.read_csv('product_information.csv')
df['local_path'].iloc[0] = filename
df.to_csv('product_information.csv', index=False)

plt.show()
