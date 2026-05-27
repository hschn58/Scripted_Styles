import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# ---------------------------
# 1. Load a real image
# ---------------------------
img = mpimg.imread("spicy.jpg")

# If image is stored with integer 0–255, convert to float range [0,1]
if img.dtype == np.uint8:
    img = img.astype(np.float32) / 255.0

# If there's an alpha channel, ignore it for distance calculations
if img.shape[-1] == 4:
    rgb = img[..., :3]  # just R, G, B
else:
    rgb = img[..., :3]
# ---------------------------
# 2. Compute distance from black
#    Distance = sqrt(R^2 + G^2 + B^2)
#    Range is [0, sqrt(3)] if rgb in [0..1].
#    Normalize to [0,1] by dividing by sqrt(3).
# ---------------------------
dist_from_black = np.linalg.norm(rgb, axis=-1)  # shape: (height, width)
dist_from_black /= np.sqrt(3)                  # now in [0..1]

# ---------------------------
# 3. Gather points
#    We'll create "points" in proportion to the distance from black.
#    e.g. A pixel that is fully black (distance=0) => 0 points
#         A pixel that is fully white => some maximum number of points
# ---------------------------
points = []
rows, cols = dist_from_black.shape
rng = np.random.default_rng()

# Let's define how many points max to place at a fully white pixel
MAX_POINTS_PER_PIXEL = 3

for r in range(rows):
    for c in range(cols):
        # dist_from_black[r,c] is in [0..1]
        # scale how many points to place
        n_points = int(dist_from_black[r, c] * MAX_POINTS_PER_PIXEL)
        for _ in range(n_points):
            points.append((r, c))

# ---------------------------
# 4. Define the Brush class
#    (Essentially the same as in your snippet)
# ---------------------------
class Brush:
    def __init__(self, color, wsize, hsize, rot, cpos, arr):
        """
        Args:
            color:  A colormap or function returning RGBA
            wsize:  Brush stroke width
            hsize:  Brush stroke height
            rot:    Rotation (not used in this basic example)
            cpos:   Center position (not used directly in 'paint' below)
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
        texture = (
            np.sin((w / wsize) * (np.pi / 2)) * 
            np.sin((h / hsize) * (np.pi / 2))
        )
        # Clamp texture to [0..1] before calling colormap
        t_clamped = max(0.0, min(1.0, texture))

        # 'intcol' is the RGBA from the colormap at 'texture'
        intcol = color(t_clamped)  # returns (R, G, B, A) in [0..1]

        return np.array([
            intcol[0],  # R
            intcol[1],  # G
            intcol[2],  # B
            abs(texture)  # alpha (we just take the absolute value)
        ])

    def paint(self, color, wsize, hsize, arr, top_left=(0,0)):
        """
        Paint the brush stroke onto 'arr' (the RGBA canvas).
        'top_left' is the upper-left corner of the brush area in the canvas.
        """
        row0, col0 = top_left
        # Ensure we don't paint outside the canvas
        max_h = min(arr.shape[0], row0 + hsize)
        max_w = min(arr.shape[1], col0 + wsize)

        for rr in range(row0, max_h):
            for cc in range(col0, max_w):
                # Local coordinates inside the brush
                brush_w = cc - col0
                brush_h = rr - row0
                arr[rr, cc, :] = self.__brush(color, wsize, hsize, brush_w, brush_h)

# ---------------------------
# 5. Create an RGBA canvas
#    We'll match the size of the loaded image for convenience
# ---------------------------
canvas = np.zeros((rows, cols, 4), dtype=np.float32)

# Use a Matplotlib colormap
cmap = plt.get_cmap("viridis")

# If you want to store brush stroke data, keep a dict
BrushStrokes = {}

# Instantiate one Brush for simplicity
brush_w, brush_h = 10, 10
my_brush = Brush(
    color=cmap,
    wsize=brush_w,
    hsize=brush_h,
    rot=0,
    cpos=None,
    arr=canvas
)

# ---------------------------
# 6. Apply paintbrush
#    For demonstration, let's randomly sample a subset of points
#    to avoid painting absolutely everything.
# ---------------------------
N_PAINTS = 3000  # number of points to actually paint
if len(points) > N_PAINTS:
    sampled_points = rng.choice(points, size=N_PAINTS, replace=False)
else:
    sampled_points = points

for idx, (r, c) in enumerate(sampled_points):
    # We'll treat (r,c) as the top-left corner for this example
    my_brush.paint(
        color=my_brush.color,
        wsize=my_brush.wsize,
        hsize=my_brush.hsize,
        arr=canvas,
        top_left=(r, c)
    )
    # Store info if needed
    BrushStrokes[idx] = (r, c, brush_w, brush_h)

# ---------------------------
# 7. Display the final painted canvas
# ---------------------------
plt.figure(figsize=(8, 8))
plt.imshow(canvas)
plt.title("Brush Painting (density by distance from black)")
plt.axis("off")
plt.show()
