import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import measurements

# Parameters
width, height = 500, 500       # Size of the canvas
num_electrodes = 5             # Number of starting points
sigma = 50                     # Standard deviation for the Gaussian probability function
max_iterations = 100000        # Maximum number of iterations
fill_percentage = 20           # Stop after X% of the grid has been filled

# Initialize the canvas
canvas = np.zeros((height, width))

# Generate random starting points (electrodes)
np.random.seed(42)  # For reproducibility
electrodes = []
for _ in range(num_electrodes):
    x = np.random.randint(0, width)
    y = np.random.randint(0, height)
    electrodes.append((x, y))
    canvas[y, x] = 1  # Mark the starting points

# Create a probability function (Gaussian centered at each electrode)
P0 = np.zeros_like(canvas)
X, Y = np.meshgrid(np.arange(width), np.arange(height))
for x0, y0 in electrodes:
    P0 += np.exp(-((X - x0)**2 + (Y - y0)**2) / (2 * sigma**2))

# Normalize the probability function
P0 /= P0.max()

# Initialize clusters for each electrode
clusters = {}
for idx, (x0, y0) in enumerate(electrodes):
    clusters[idx] = {'pixels': [(x0, y0)], 'COM': (x0, y0)}

# Directions for neighboring pixels (8-connectivity)
directions = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),         (0, 1),
              (1, -1),  (1, 0), (1, 1)]

# Function to get frontier pixels
def get_frontier(pixels):
    frontier = set()
    for x, y in pixels:
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and canvas[ny, nx] == 0:
                frontier.add((nx, ny))
    return list(frontier)

# Iterative growth process
total_pixels = width * height
filled_pixels = np.count_nonzero(canvas)
fill_threshold = (fill_percentage / 100) * total_pixels

for iteration in range(1, max_iterations + 1):
    for idx in clusters:
        # Get the current cluster data
        cluster = clusters[idx]
        pixels = cluster['pixels']
        COM = cluster['COM']

        # Get frontier pixels
        frontier = get_frontier(pixels)
        if not frontier:
            continue  # No more pixels to add

        # Compute probabilities for frontier pixels
        probs = []
        for x, y in frontier:
            # Probability based on the initial probability function
            P_init = P0[y, x]

            # Distance to the COM of the cluster
            dx, dy = x - COM[0], y - COM[1]
            distance = np.hypot(dx, dy)
            # Avoid division by zero
            distance = max(distance, 1e-5)
            # Probability inversely proportional to distance
            P_COM = 1 / distance

            # Combined probability
            P = P_init * P_COM
            probs.append(P)

        # Normalize probabilities
        probs = np.array(probs)
        probs /= probs.sum()

        # Choose a pixel to add based on probabilities
        chosen_idx = np.random.choice(len(frontier), p=probs)
        x_new, y_new = frontier[chosen_idx]

        # Add the new pixel to the cluster
        canvas[y_new, x_new] = idx + 1  # Mark with cluster index
        pixels.append((x_new, y_new))

        # Update the COM
        xs, ys = zip(*pixels)
        COM = (np.mean(xs), np.mean(ys))
        cluster['COM'] = COM

        # Update filled pixels count
        filled_pixels += 1

    # Print progress every 1000 iterations
    if iteration % 1000 == 0:
        percent_filled = (filled_pixels / total_pixels) * 100
        print(f"Iteration {iteration}: {percent_filled:.2f}% of the grid filled.")

    # Check if the fill threshold has been reached
    if filled_pixels >= fill_threshold:
        print(f"Stopping simulation at iteration {iteration}: {fill_percentage}% of the grid filled.")
        break

# Visualization
plt.figure(figsize=(10, 10))
plt.imshow(canvas, cmap='inferno')
plt.axis('off')
plt.title('Lichtenberg Figures Simulation')
plt.show()
