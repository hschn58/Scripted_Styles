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
    
    print(f"Step {step + 1} / {num_steps} done")

#10000, 7*10, 6
# Apply Gaussian filter for line–width effect
path_density = gaussian_filter(path_density, sigma=9 * line_width)

# Normalize the density values to [0,1]
min_val = np.min(path_density)
max_val = np.max(path_density)
normalized_path_density = (path_density - min_val) / (max_val - min_val)

# --- Build a Custom Cyclic Colormap from "binary" ---
import matplotlib.colors as mcolors

binary_cmap = plt.get_cmap("binary")
N = 4096
x = np.linspace(0, 1, N)
cyclic_map = 0.5 * (1 - np.cos(28 * np.pi * x))
cyclic_colors = binary_cmap(cyclic_map)
cyclic_binary = mcolors.ListedColormap(cyclic_colors, name="cyclic_binary")

colormap_name = 'cyclic_binary'

# --- Plot and Save the Heatmap ---
plt.figure(figsize=(6, 6))

# Only show a central part of the grid (to avoid edge artifacts)
param = 0
start = int(grid_size * param)
end = int(grid_size * (1 - param))

# plt.imshow(normalized_path_density[start:end, start:end], 
#            cmap=cyclic_binary, 
#            origin='lower', 
#            extent=[0, 1, 0, 1], 
#            norm=PowerNorm(0.5))
# plt.axis('off')

# Assume unique_filename() returns a new filename each time
from ScriptedStyles.Designs.Releases.ismethods.check import unique_filename
# output_filename = unique_filename('2d_heatmap_powernorm_' +
#                                   colormap_name + '_strange' + '.jpg')
# plt.savefig(output_filename, dpi=1200, bbox_inches='tight', pad_inches=0)
# plt.close()



# --- Optional: Voronoi Tessellation Overlay ---
# --- Optional: Voronoi Tessellation Overlay ---
import cv2
import numpy as np

import cv2
import numpy as np

# def find_reference_points(image, area_threshold_ratio=5/30, threshold_val=3, min_area=200):
#     """
#     Finds reference points (centroids) of dark (black/gray) balls in the image.
    
#     Parameters:
#         image: Input image in BGR format (or grayscale).
#         area_threshold_ratio: The maximum area allowed for a blob, relative to the total image area.
#         threshold_val: Threshold value used to separate the dark objects from the background.
#         min_area: Minimum area to be considered a valid ball.
        
#     Returns:
#         points: A list of normalized (x, y) centroids (values in [0, 1]) of the detected balls.
#         avg_center: The average (x, y) position (normalized) of all detected points.
#     """
#     # If image is color, convert to grayscale.
#     if len(image.shape) == 3:
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     else:
#         gray = image.copy()
        
#     total_area = image.shape[0] * image.shape[1]
#     area_threshold = total_area * area_threshold_ratio

#     # Inverse threshold: dark balls become white blobs
#     ret, thresh = cv2.threshold(gray, threshold_val, 255, cv2.THRESH_BINARY_INV)

#     # Find external contours.
#     contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
#     points = []
#     for cnt in contours:
#         area = cv2.contourArea(cnt)
#         if min_area < area < area_threshold:
#             M = cv2.moments(cnt)
#             if M["m00"] != 0:
#                 cx = M["m10"] / M["m00"]
#                 cy = M["m01"] / M["m00"]
#                 # Normalize the coordinates (to [0,1]) for consistency
#                 norm_x = cx / image.shape[1]
#                 norm_y = cy / image.shape[0]
#                 points.append((norm_x, norm_y))
    
#     # Compute average center, or default to the image center if no points are found.
#     if points:
#         avg_x = sum(pt[0] for pt in points) / len(points)
#         avg_y = sum(pt[1] for pt in points) / len(points)
#         avg_center = (avg_x, avg_y)
#     else:
#         avg_center = (0.5, 0.5)
    
#     return points, avg_center

import cv2
import numpy as np

def find_black_ball_centers(image, 
                            threshold_val=50, 
                            morph_kernel_size=3, 
                            min_area=100, 
                            max_area=None):
    """
    Detects large black "balls" in an image and returns their centroids in pixel coordinates.
    
    Parameters:
        image (np.ndarray): Input image (BGR or grayscale).
        threshold_val (int): Threshold value for separating dark regions.
        morph_kernel_size (int): Size of the morphological kernel used 
                                 to reduce noise and close small holes.
        min_area (float): Minimum contour area to be considered a valid ball.
        max_area (float): Maximum contour area to be considered a valid ball.
                          If None, no upper bound check is performed.
    
    Returns:
        centers (list of tuples): List of (x, y) centroids (in pixels) for the detected balls.
    """
    # 1. Convert to grayscale if needed.
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # 2. Threshold the image so that dark regions become "white" foreground.
    #    Using THRESH_BINARY_INV: dark pixels => white (255), background => black (0).
    _, thresh = cv2.threshold(gray, threshold_val, 255, cv2.THRESH_BINARY_INV)

    # 3. Morphological closing (dilate then erode) to close holes.
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_kernel_size, morph_kernel_size))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # 4. Find contours.
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 5. Compute centroids for valid contours.
    centers = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        if max_area is not None and area > max_area:
            continue
        
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centers.append((cx, cy))
    
    return centers



# def high_res_voronoi_overlay(base_image, points, scale_factor=4, line_color=(255, 255, 255), thickness=1):
#     # Determine original dimensions
#     orig_height, orig_width = base_image.shape[:2]
#     # Create a high-resolution canvas
#     hi_res_width = orig_width * scale_factor
#     hi_res_height = orig_height * scale_factor
#     # Resize the base image to the higher resolution
#     hi_res_image = cv2.resize(base_image, (hi_res_width, hi_res_height), interpolation=cv2.INTER_CUBIC)

#     # Adjust thickness for high resolution
#     hi_res_thickness = thickness * scale_factor

#     # Create a Subdiv2D for the high-resolution image
#     subdiv = cv2.Subdiv2D((0, 0, hi_res_width, hi_res_height))
    
#     # Insert points scaled to high resolution
#     for p in points:
#         x = int(np.clip(p[0] * hi_res_width, 0, hi_res_width - 1))
#         y = int(np.clip(p[1] * hi_res_height, 0, hi_res_height - 1))
#         subdiv.insert((x, y))
    
#     # Get Voronoi facets
#     facets, centers = subdiv.getVoronoiFacetList([])
    
#     # Draw the facets with anti-aliased lines
#     for facet in facets:
#         facet_int = np.array(facet, np.int32)
#         cv2.polylines(hi_res_image, [facet_int], isClosed=True, color=line_color, thickness=hi_res_thickness, lineType=cv2.LINE_AA)
    
#     # Downsample back to original size
#     final_image = cv2.resize(hi_res_image, (orig_width, orig_height), interpolation=cv2.INTER_AREA)
#     return final_image
def high_res_voronoi_overlay(base_image, points, scale_factor=4, 
                             line_color=(255, 255, 255), thickness=1,
                             normalized_points=True):
    """
    Overlays a Voronoi tessellation onto a high-resolution version of the base image.
    
    Parameters:
        base_image (np.ndarray): The background image (BGR).
        points (list/array of tuples): The point locations.
            • If normalized_points is True (default), each point is assumed to be in [0,1]×[0,1].
            • If False, each point is assumed to be given in pixel coordinates.
        scale_factor (int): Factor to scale up the image for high-res rendering.
        line_color (tuple): Color of the Voronoi lines (in BGR).
        thickness (int): Base line thickness (will be scaled up).
        normalized_points (bool): Whether the input points are normalized (default True).
    
    Returns:
        final_image (np.ndarray): The base image with the Voronoi overlay.
    """
    # Get original dimensions.
    orig_height, orig_width = base_image.shape[:2]
    
    # Create a high-resolution version of the image.
    hi_res_width = orig_width * scale_factor
    hi_res_height = orig_height * scale_factor
    hi_res_image = cv2.resize(base_image, (hi_res_width, hi_res_height), interpolation=cv2.INTER_CUBIC)
    
    # Scale up the line thickness.
    hi_res_thickness = thickness * scale_factor
    
    # Create a Subdiv2D object for computing the tessellation.
    subdiv = cv2.Subdiv2D((0, 0, hi_res_width, hi_res_height))
    
    # Insert each point into the Subdiv2D.
    for p in points:
        if normalized_points:
            # Convert normalized coordinate to pixel coordinate,
            # then apply the high-res scale factor.
            x = int(np.clip(p[0] * orig_width * scale_factor, 0, hi_res_width - 1))
            y = int(np.clip(p[1] * orig_height * scale_factor, 0, hi_res_height - 1))
        else:
            # Points are already in pixel coordinates.
            x = int(np.clip(p[0] * scale_factor, 0, hi_res_width - 1))
            y = int(np.clip(p[1] * scale_factor, 0, hi_res_height - 1))
        subdiv.insert((x, y))
    
    # Retrieve Voronoi facets.
    facets, _ = subdiv.getVoronoiFacetList([])
    
    # Draw each facet as an anti-aliased polygon.
    for facet in facets:
        facet_int = np.array(facet, np.int32)
        cv2.polylines(hi_res_image, [facet_int], isClosed=True,
                      color=line_color, thickness=hi_res_thickness, lineType=cv2.LINE_AA)
    
    # Downsample back to the original image size.
    final_image = cv2.resize(hi_res_image, (orig_width, orig_height), interpolation=cv2.INTER_AREA)
    return final_image



# Convert the heatmap to a colored background using the custom cyclic colormap.


heatmap_data = normalized_path_density[start:end, start:end]
colored_heatmap = cyclic_binary(heatmap_data)  # returns RGBA values in [0,1]
colored_heatmap_rgb = (colored_heatmap[:, :, :3] * 255).astype(np.uint8)
heatmap_bgr = cv2.cvtColor(colored_heatmap_rgb, cv2.COLOR_RGB2BGR)
heatmap_bgr = cv2.bitwise_not(heatmap_bgr)

# To overlay the Voronoi, obtain the final particle positions (still normalized [0,1]).
particle_positions = np.array([p.position for p in particles.values()])
# Example usage:
# Assume `heatmap_bgr` is your colored background image (BGR, e.g., 900x900).


# Example usage:

# Suppose 'image.jpg' is similar to the one you attached

ball_centers = find_black_ball_centers(
    image=heatmap_bgr,
    threshold_val=50,       # Adjust if your black circles are darker or lighter
    morph_kernel_size=5,    # Increase if you need more smoothing/closing
    min_area=50,            # Filter out small specks
    max_area=50000          # You can remove or adjust as needed
)
print("Detected ball centers:", ball_centers)

# # For visualization, draw circles at the detected centers
# for (x, y) in ball_centers:
#     cv2.circle(img, (x, y), 5, (0, 0, 255), -1)

# # Show or save the result
# cv2.imwrite("annotated_image.jpg", img)
# reference_points, avg_center = find_reference_points(heatmap_bgr)


# Apply the Voronoi tessellation overlay.
heatmap_with_voronoi = high_res_voronoi_overlay(heatmap_bgr, particle_positions, line_color=(255, 255, 255), thickness=1, normalized_points=True)

# Save the final image with the overlay.
output_filename_voronoi = unique_filename('2d_heatmap_powernorm_' +
                                            colormap_name + '_with_voronoi.jpg')
cv2.imwrite(output_filename_voronoi, heatmap_with_voronoi)