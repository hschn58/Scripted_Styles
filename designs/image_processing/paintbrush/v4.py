import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import random



# -----------------------------
# 1) Load an image via OpenCV
#    (BGR order by default)
# -----------------------------
img_bgr = cv2.imread("spicy.jpg")  
if img_bgr is None:
    raise IOError("Could not read 'some_image.jpg'. Make sure the path is correct.")

# Convert to RGB for display/processing consistency with matplotlib
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

# Optionally scale to [0,1] floats:
img_rgb = img_rgb.astype(np.float32) / 255.0

# We'll also make a grayscale for edge detection
gray = cv2.cvtColor((img_rgb * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)

# -----------------------------
# 2) Detect edges (Canny)
#    Tweak thresholds as needed
# -----------------------------
low_threshold  = 100
high_threshold = 200
edges = cv2.Canny(gray, low_threshold, high_threshold)

# `edges` is a binary image [0 or 255]. Let's binarize it to 0/1 for convenience:
edges_bin = (edges > 0).astype(np.uint8)

# -----------------------------
# 3) Step 1: Gather points ON the edges
#    We'll pick every pixel that is marked as edge.
# -----------------------------
edge_points = []
rows, cols = edges_bin.shape
for r in range(rows):
    for c in range(cols):
        if edges_bin[r, c] == 1:
            # Collect this as an "edge" brush point
            edge_points.append((r, c))

# -----------------------------
# 4) Step 2: Build a local density gradient AWAY from edges
#
#    We do this by:
#    - Distance Transform: each pixel gets the distance
#      to the nearest edge pixel.
#    - We define a local radius, e.g. 30. 
#    - We create a density = 1 - (distance / radius), clipped to [0,1].
#
#    This is a simple "circle of influence" approach around edges.
#    For exact radius-of-curvature-based radius, you'd need more
#    advanced geometry to measure local curvature of contours.
# -----------------------------

# Invert edges: edges=1 => we want distance=0 there
# so we do distance transform on the "background" of edges
# => we invert the binarized edges (1 => 0, 0 => 1)
inv_edges_bin = 1 - edges_bin

dist_map = cv2.distanceTransform(inv_edges_bin, cv2.DIST_L2, 3)
# Note: DIST_L2 => Euclidean distance to nearest 0 pixel in 'inv_edges_bin'

# Let’s define a local radius
local_radius = 30.0

# "Density" = 1 - distance/radius, clipped to [0,1]
density_map = 1.0 - (dist_map / local_radius)
density_map = np.clip(density_map, 0, 1)

# Optional: If you wanted to factor in curvature, you'd
# compute local curvature around each edge pixel, and
# set local_radius = curvature_radius * some_constant
# in that area. That is an advanced approach not shown here.

# -----------------------------
# 5) Collect points INSIDE edges
#    (Gradient-based sampling: more points near edges)
# -----------------------------
inside_points = []
rng = np.random.default_rng()

# The maximum number of points per pixel, or use a fractional approach
MAX_POINTS_PER_PIXEL = 3

for r in range(rows):
    for c in range(cols):
        # density_map[r, c] is in [0,1]
        # scale how many points to place
        n_points = int(density_map[r, c] * MAX_POINTS_PER_PIXEL)
        for _ in range(n_points):
            inside_points.append((r, c))

# Combine them: edges + inside
all_points = edge_points + inside_points

# -----------------------------
# 6) Define your Brush class
#    (same structure as before)
# -----------------------------
class Brush:
    def __init__(self, color, wsize, hsize, rot, cpos, arr):
        """
        Args:
            color:  A colormap or function returning RGBA
            wsize:  Brush stroke width
            hsize:  Brush stroke height
            rot:    Rotation (not used in this example)
            cpos:   Center position (not used directly below)
            arr:    The RGBA canvas
        """
        self.color = color
        self.wsize = wsize
        self.hsize = hsize
        self.rot = rot
        self.cpos = cpos
        self.arr = arr
  
    def __brush(self, color, wsize, hsize, w, h):
        """
        Compute the color for a single pixel in the brush-stroke area
        using a simple sinusoidal texture, colored by 'color' (a colormap).
        """
        # Simple sinusoidal pattern
        texture = ( int(np.random.rand()+0.5)
            
        )
        # Clamp to [0..1] before calling colormap
        t_clamped = max(0.0, min(1.0, texture))
        #intcol = color(t_clamped)  # returns (R, G, B, A) in [0..1]

        return np.array([
            255*(1-t_clamped),  
            255*(1-t_clamped),  
            255*(1-t_clamped),  
            abs(texture) # alpha
        ])

    def paint(self, color, wsize, hsize, arr, top_left=(0,0)):
        """
        Paint the brush stroke onto 'arr' (the RGBA canvas).
        'top_left' is the upper-left corner of the brush region in the canvas.
        """
        row0, col0 = top_left
        max_h = min(arr.shape[0], row0 + hsize)
        max_w = min(arr.shape[1], col0 + wsize)

        for rr in range(row0, max_h):
            for cc in range(col0, max_w):
                brush_w = cc - col0
                brush_h = rr - row0

                if sum(arr[rr, cc, :]) !=0:
                    print(sum(arr[rr, cc,:]))
                    continue
                else:
                    arr[rr, cc, :] = self.__brush(color, wsize, hsize, brush_w, brush_h)

# -----------------------------
# 7) Create an RGBA “canvas”
#    We'll match the image size
# -----------------------------
canvas = np.zeros((rows, cols, 4), dtype=np.float32)

# Colormap for the brush
import matplotlib
cmap = matplotlib.colormaps['plasma_r']

# A dictionary to store brush strokes if desired
BrushStrokes = {}

# We'll instantiate a single Brush for simplicity
brush_w, brush_h = 20, 20
my_brush = Brush(
    color=cmap,
    wsize=brush_w,
    hsize=brush_h,
    rot=0,
    cpos=None,
    arr=canvas
)

# -----------------------------
# 8) Sample and paint
#    We’ll pick a subset so we don’t spam too many strokes.
# -----------------------------
N_PAINTS = 7000
if len(all_points) > N_PAINTS:
    sampled_points = rng.choice(all_points, size=N_PAINTS, replace=False)
else:
    sampled_points = all_points

for idx, (r, c) in enumerate(sampled_points):
    # We'll treat (r, c) as the top-left corner of the stroke
    my_brush.paint(
        color=my_brush.color,
        wsize=my_brush.wsize,
        hsize=my_brush.hsize,
        arr=canvas,
        top_left=(r, c)
    )
    # Optionally record stroke metadata
    BrushStrokes[idx] = (r, c, brush_w, brush_h)

# -----------------------------
# 9) Display the original image,
#    edge map, and final painted canvas
# -----------------------------
fig, axs = plt.subplots(1, 3, figsize=(15, 5))
axs[0].imshow(img_rgb)
axs[0].set_title("Original Image")
axs[0].axis('off')

axs[1].imshow(edges, cmap='gray')
axs[1].set_title("Canny Edges")
axs[1].axis('off')

axs[2].imshow(canvas)
axs[2].set_title("Painted Canvas\n(High density near edges)")
axs[2].axis('off')

plt.tight_layout()
plt.show()




"""
One with moving shapes-adjust a value by gaussian from canny method
"""


