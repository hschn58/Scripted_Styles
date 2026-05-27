import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib

# -----------------------------
# 1) Load an image via OpenCV
#    (BGR order by default)
# -----------------------------
img_bgr = cv2.imread("spicy.jpg")
if img_bgr is None:
    raise IOError("Could not read 'spicy.jpg'. Make sure the path is correct.")

# Convert to RGB for display/processing consistency with matplotlib
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

# Optionally scale to [0,1] floats
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

# `edges` is a binary image [0 or 255]. Let's binarize it to 0/1 for convenience
edges_bin = (edges > 0).astype(np.uint8)

# -----------------------------
# 3) Step 1: Gather points ON the edges
# -----------------------------
edge_points = []
rows, cols = edges_bin.shape
for r in range(rows):
    for c in range(cols):
        if edges_bin[r, c] == 1:
            edge_points.append((r, c))

# -----------------------------
# 4) Step 2: Build a local density gradient AWAY from edges
#
#    - Distance Transform => each pixel gets dist to nearest edge
#    - local_radius => region in which density is non-zero
#    - density = 1 - (distance / local_radius), clipped to [0,1]
# -----------------------------
inv_edges_bin = 1 - edges_bin  # invert edges
dist_map = cv2.distanceTransform(inv_edges_bin, cv2.DIST_L2, 3)

local_radius = 30.0
density_map = 1.0 - (dist_map / local_radius)
density_map = np.clip(density_map, 0, 1)

# -----------------------------
# 5) Collect points INSIDE edges
#    (more points near edges = higher density)
# -----------------------------
inside_points = []
rng = np.random.default_rng()

MAX_POINTS_PER_PIXEL = 3
for r in range(rows):
    for c in range(cols):
        n_points = int(density_map[r, c] * MAX_POINTS_PER_PIXEL)
        for _ in range(n_points):
            inside_points.append((r, c))

all_points = edge_points + inside_points

# -----------------------------
# 6) Relativistic velocity addition for scalars
# -----------------------------
def relativistic_add(x, y):
    """
    Combine two values in [0..1] using the relativistic velocity formula:
        v_new = (x + y) / (1 + x*y)
    """
    return (x + y) / (1.0 + x * y)

# -----------------------------
# 7) Define the Brush class
#    returning a single scalar
# -----------------------------
class Brush:
    def __init__(self, wsize, hsize, rot, cpos, arr):
        """
        Args:
            wsize:  Brush stroke width
            hsize:  Brush stroke height
            rot:    Rotation (not used here)
            cpos:   Center position (not used here)
            arr:    The single-channel canvas array
        """
        self.wsize = wsize
        self.hsize = hsize
        self.rot = rot
        self.cpos = cpos
        self.arr = arr

    def __brush_value(self, wsize, hsize, w, h):
        """
        Compute a single scalar in [0..1] for this pixel in the brush.
        """
        # A simple sinusoidal pattern
        # range ~ [-1..1]
        val = (
            np.sin((w / wsize) * (np.pi / 2)) *
            np.sin((h / hsize) * (np.pi / 2))
        )
        # clamp to [0..1]
        val_clamped = max(0.0, min(1.0, val))
        return val_clamped

    def paint(self, arr, top_left=(0,0)):
        """
        Paint the brush stroke onto 'arr' (the single-channel canvas).
        'top_left' is the upper-left corner of the brush region in the canvas.
        For each pixel in that region, combine via relativistic addition.
        """
        row0, col0 = top_left
        max_h = min(arr.shape[0], row0 + self.hsize)
        max_w = min(arr.shape[1], col0 + self.wsize)

        for rr in range(row0, max_h):
            for cc in range(col0, max_w):
                brush_w = cc - col0
                brush_h = rr - row0

                # Compute new brush value
                new_val = self.__brush_value(self.wsize, self.hsize, brush_w, brush_h)

                # Combine with existing canvas value
                old_val = arr[rr, cc]
                combined_val = relativistic_add(old_val, new_val)
                arr[rr, cc] = combined_val

# -----------------------------
# 8) Create a single-channel “canvas”
# -----------------------------
canvas_scalar = np.zeros((rows, cols), dtype=np.float32)

# A dictionary to store brush strokes if needed
BrushStrokes = {}

# Instantiate a single Brush for simplicity
brush_w, brush_h = 10, 10
my_brush = Brush(
    wsize=brush_w,
    hsize=brush_h,
    rot=0,
    cpos=None,
    arr=canvas_scalar
)

# -----------------------------
# 9) Sample and paint
#    We’ll pick a subset to avoid performance issues
# -----------------------------
N_PAINTS = 3000
if len(all_points) > N_PAINTS:
    sampled_points = rng.choice(all_points, size=N_PAINTS, replace=False)
else:
    sampled_points = all_points

for idx, (r, c) in enumerate(sampled_points):
    # We'll treat (r, c) as the top-left corner of the stroke
    my_brush.paint(
        arr=canvas_scalar,
        top_left=(r, c)
    )
    # Optionally record stroke metadata
    BrushStrokes[idx] = (r, c, brush_w, brush_h)

# -----------------------------
# 10) Apply a colormap at the end
#     We'll use 'plasma' as requested
# -----------------------------
cmap = matplotlib.colormaps['plasma']
colored_canvas = cmap(canvas_scalar)  # shape: (rows, cols, 4)

# -----------------------------
# 11) Display the original image,
#     edge map, and final painted canvas
# -----------------------------
fig, axs = plt.subplots(1, 3, figsize=(15, 5))

axs[0].imshow(img_rgb)
axs[0].set_title("Original Image")
axs[0].axis('off')

axs[1].imshow(edges, cmap='gray')
axs[1].set_title("Canny Edges")
axs[1].axis('off')

axs[2].imshow(colored_canvas)
axs[2].set_title("Painted (Scalar + Relativistic + plasma)")
axs[2].axis('off')

plt.tight_layout()
plt.show()
