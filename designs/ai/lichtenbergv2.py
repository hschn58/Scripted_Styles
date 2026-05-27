import numpy as np
import matplotlib.pyplot as plt

# Parameters
width, height = 500, 500       # Size of the canvas
num_electrodes = 5             # Number of starting points
sigma = 50                     # Standard deviation for the Gaussian probability function
max_iterations = 100000        # Maximum number of iterations
fill_percentage = 20           # Stop after X% of the grid has been filled

# Initialize the canvas and labels
canvas = np.zeros((height, width), dtype=int)  # Use int type for cluster labels

# Generate random starting points (electrodes)
np.random.seed(42)  # For reproducibility
electrodes = []
sum_x = 0
sum_y = 0
num_filled_pixels = 0
for idx in range(1, num_electrodes + 1):
    x = np.random.randint(0, width)
    y = np.random.randint(0, height)
    electrodes.append((x, y))
    canvas[y, x] = idx  # Mark the starting points with cluster labels
    sum_x += x
    sum_y += y
    num_filled_pixels += 1

# Create a probability function (Gaussian centered at each electrode)
P0 = np.zeros_like(canvas, dtype=float)
X, Y = np.meshgrid(np.arange(width), np.arange(height))
for x0, y0 in electrodes:
    P0 += np.exp(-((X - x0)**2 + (Y - y0)**2) / (2 * sigma**2))

# Normalize the probability function
P0 /= P0.max()

# Initialize clusters as sets of pixels
clusters = {}
for idx, (x0, y0) in enumerate(electrodes, start=1):
    clusters[idx] = set()
    clusters[idx].add((x0, y0))

# Directions for neighboring pixels (8-connectivity)
directions = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),         (0, 1),
              (1, -1),  (1, 0), (1, 1)]

# Initialize set of filled pixels
filled_pixels = set(electrodes)

# Total number of pixels and fill threshold
total_pixels = width * height
fill_threshold = (fill_percentage / 100) * total_pixels

# Iterative growth process
for iteration in range(1, max_iterations + 1):
    # Get the frontier pixels
    frontier = set()
    for x, y in filled_pixels:
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and canvas[ny, nx] == 0:
                frontier.add((nx, ny))
    frontier = list(frontier)

    if not frontier:
        print("No more frontier pixels. Stopping simulation.")
        break

    # Compute the overall COM
    overall_COM = (sum_x / num_filled_pixels, sum_y / num_filled_pixels)

    # Compute probabilities for frontier pixels
    probs = []
    adjacency_clusters = []
    for x, y in frontier:
        # Probability based on the initial probability function
        P_init = P0[y, x]

        # Distance to the overall COM
        dx, dy = x - overall_COM[0], y - overall_COM[1]
        distance = np.hypot(dx, dy)
        # Avoid division by zero
        distance = max(distance, 1e-5)
        # Probability inversely proportional to distance
        P_COM = 1 / distance

        # Combined probability
        P = P_init * P_COM
        probs.append(P)

        # Determine which clusters are adjacent to this frontier pixel
        adjacent_clusters = set()
        for dx_adj, dy_adj in directions:
            nx_adj, ny_adj = x + dx_adj, y + dy_adj
            if 0 <= nx_adj < width and 0 <= ny_adj < height:
                label = canvas[ny_adj, nx_adj]
                if label != 0:
                    adjacent_clusters.add(label)
        adjacency_clusters.append(adjacent_clusters)

    # Normalize probabilities
    probs = np.array(probs)
    probs_sum = probs.sum()
    if probs_sum == 0:
        probs = np.ones_like(probs) / len(probs)
    else:
        probs /= probs_sum

    # Choose a pixel to add based on probabilities
    chosen_idx = np.random.choice(len(frontier), p=probs)
    x_new, y_new = frontier[chosen_idx]
    clusters_adjacent = adjacency_clusters[chosen_idx]

    # Determine the cluster label for the new pixel
    if clusters_adjacent:
        # If adjacent to clusters, merge them
        cluster_ids = list(clusters_adjacent)
        cluster_id = cluster_ids[0]  # Use the first cluster ID
        # If more than one cluster, merge them
        if len(cluster_ids) > 1:
            # Merge clusters
            for cid in cluster_ids[1:]:
                clusters[cluster_id].update(clusters[cid])
                # Update labels in canvas
                for px, py in clusters[cid]:
                    canvas[py, px] = cluster_id
                # Remove merged cluster
                del clusters[cid]
    else:
        # Create a new cluster if not adjacent to any (unlikely but handled)
        cluster_id = max(clusters.keys()) + 1
        clusters[cluster_id] = set()

    # Add the new pixel to the cluster
    clusters[cluster_id].add((x_new, y_new))
    canvas[y_new, x_new] = cluster_id
    filled_pixels.add((x_new, y_new))

    # Update sums and filled pixels count
    sum_x += x_new
    sum_y += y_new
    num_filled_pixels += 1

    # Print progress every 1000 iterations
    if iteration % 1000 == 0:
        percent_filled = (num_filled_pixels / total_pixels) * 100
        print(f"Iteration {iteration}: {percent_filled:.2f}% of the grid filled.")

    # Check if the fill threshold has been reached
    if num_filled_pixels >= fill_threshold:
        print(f"Stopping simulation at iteration {iteration}: {fill_percentage}% of the grid filled.")
        break


# Visualization
plt.figure(figsize=(10, 10))
plt.imshow(canvas, cmap='inferno')
plt.axis('off')
plt.title('Lichtenberg Figures Simulation')
plt.savefig("lichtenberg.png",transparent=True,format='png',bbox_inches='tight',dpi=1200)
plt.show()
