import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import matplotlib
from matplotlib.colors import LogNorm, PowerNorm
import cv2  # OpenCV for the tessellation overlay

# Use Agg backend for non-interactive plotting
matplotlib.use('Agg')

# --- Particle simulation classes & functions ---

class Particle:
    def __init__(self, mass, position, velocity, i):
        self.mass = mass
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.i = i

    def update_position(self, time_step):
        p_rad = 0.01470588  # particle radius
        self.position += self.velocity * time_step

        # Reflect off boundaries (assumes a [0,1] box)
        for i in range(2):  # x and y
            if self.position[i] <= 0 + p_rad or self.position[i] >= 1 - p_rad:
                self.velocity[i] = -self.velocity[i]

    def apply_force(self, force, time_step):
        acceleration = force / self.mass
        self.velocity += acceleration * time_step
        self.update_position(time_step)

    def check_collision(self, other, col_mat, i, k):
        col_axis = self.position - other.position
        magnitude = np.linalg.norm(col_axis)
        p_rad = 0.01470588

        if magnitude <= 2 * p_rad:
            if np.dot(col_axis, self.velocity) * np.dot(col_axis, other.velocity) < 0:
                ucol_axis = col_axis / magnitude
                smag = np.dot(ucol_axis, self.velocity)
                omag = np.dot(ucol_axis, other.velocity)

                # Perfectly elastic collision: swap the projected velocity components
                self.velocity = omag * ucol_axis + (self.velocity - smag * ucol_axis)
                other.velocity = smag * ucol_axis + (other.velocity - omag * ucol_axis)

                # Mark collision as handled
                col_mat[i, k] = True
                col_mat[k, i] = True
        return

# --- Simulation Parameters ---
mass = 1.0
num_particles = 100
time_step = 0.1
num_steps = 500
force = np.array([0, 0])  # no external force
grid_size = 1000  # You can increase this for a finer simulation grid
line_width = 2   # affects the Gaussian spread

# --- Initialize Particles ---
particles = {}
for i in range(num_particles):
    particles[f"x{i}"] = Particle(
        mass=mass, 
        position=np.random.rand(2), 
        velocity=10 * (np.random.rand(2) - 0.5),
        i=i
    )

# --- Create Path Density Grid ---
path_density = np.zeros((grid_size, grid_size))

for step in range(num_steps):
    for i in range(num_particles):
        p = particles[f"x{i}"]
        p.apply_force(force, time_step)
        loc = p.position.copy()
        
        # Convert position in [0,1] to grid coordinates:
        grid_x = min(max(int(loc[0] * grid_size), 0), grid_size - 1)
        grid_y = min(max(int(loc[1] * grid_size), 0), grid_size - 1)
        path_density[grid_y, grid_x] += 1

# Apply Gaussian filter for line–width effect
path_density = gaussian_filter(path_density, sigma=7 * line_width)

# Normalize the density values to [0,1]
min_val = np.min(path_density)
max_val = np.max(path_density)
normalized_path_density = (path_density - min_val) / (max_val - min_val)

# --- Build a Custom Cyclic Colormap from "binary" ---
import matplotlib.colors as mcolors

binary_cmap = plt.get_cmap("binary")
N = 256
x = np.linspace(0, 1, N)
cyclic_map = 0.5 * (1 - np.cos(6 * np.pi * x))
cyclic_colors = binary_cmap(cyclic_map)
cyclic_binary = mcolors.ListedColormap(cyclic_colors, name="cyclic_binary")

colormap_name = 'cyclic_binary'

# --- Plot and Save the Heatmap ---
plt.figure(figsize=(6, 6))
# Only show a central part of the grid (to avoid edge artifacts)
plt.imshow(normalized_path_density[50:950, 50:950], 
           cmap=cyclic_binary, 
           origin='lower', 
           extent=[0, 1, 0, 1], 
           norm=PowerNorm(0.5))
plt.axis('off')

# Assume unique_filename() returns a new filename each time
from ScriptedStyles.Designs.Releases.ismethods.check import unique_filename
output_filename = unique_filename('2d_heatmap_powernorm_' +
                                  colormap_name + '_strange' + '.jpg')
plt.savefig(output_filename, dpi=3600)
plt.close()

# --- Optional: Voronoi Tessellation Overlay ---
def apply_voronoi_tessellation(image, points, line_color=(0, 0, 0), thickness=None):
    """
    Overlays a Voronoi tessellation on the given image.
    
    Parameters:
      image: NumPy array in BGR format.
      points: Array-like of points in normalized [0,1] coordinates.
      line_color: BGR tuple for the line color (default black).
      thickness: Optional line thickness. If not provided, a default is computed.
    Returns:
      image: The image with Voronoi lines drawn.
    """
    height, width = image.shape[:2]
    
    # If thickness is not provided, choose a default small value.
    if thickness is None:
        # For example, choose a thickness corresponding to a circle whose area is <= 1/30th of image area.
        # (For a 900x900 image, total area = 810000 pixels, 1/30th ~ 27000.
        # A circle of radius r has area pi*r^2, so r ~ sqrt(27000/pi) ~ 92.
        # In practice, a line thickness of 3 to 5 pixels is usually visually appealing.)
        thickness = 3

    # Create a Subdiv2D over the whole image.
    subdiv = cv2.Subdiv2D((0, 0, width, height))
    
    # Insert points (scale from [0,1] to image coordinates).
    for p in points:
        x = int(p[0] * width)
        y = int(p[1] * height)
        subdiv.insert((x, y))
    
    # Obtain Voronoi facets.
    (facets, centers) = subdiv.getVoronoiFacetList([])
    
    for facet in facets:
        # Convert facet vertices to a numpy array of type int32.
        facet_int = np.array(facet, np.int32)
        # Draw the polygonal boundary (solid line).
        cv2.polylines(image, [facet_int], isClosed=True, color=line_color, thickness=thickness)
    
    return image

# To overlay the Voronoi tessellation on the heatmap, first obtain the final particle positions:
particle_positions = np.array([p.position for p in particles.values()])

# For the overlay, we want a 2D image (e.g. the same [50:950,50:950] region)
# Convert the normalized density (a float image in [0,1]) into an 8-bit grayscale image.
# Then convert to BGR so that we can draw colored lines.
heatmap_data = normalized_path_density[50:950, 50:950]
heatmap_8bit = (heatmap_data * 255).astype(np.uint8)
heatmap_bgr = cv2.cvtColor(heatmap_8bit, cv2.COLOR_GRAY2BGR)

# Apply the Voronoi tessellation overlay.
heatmap_with_voronoi = apply_voronoi_tessellation(heatmap_bgr, particle_positions, line_color=(0, 0, 0), thickness=3)

# Save the final image with the overlay.
output_filename_voronoi = unique_filename('2d_heatmap_powernorm_' +
                                            colormap_name + '_with_voronoi.jpg')
cv2.imwrite(output_filename_voronoi, heatmap_with_voronoi)
