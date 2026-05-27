import cv2
import numpy as np
import time

# Load image
image = cv2.imread('188.png', cv2.IMREAD_GRAYSCALE)
image_height, image_width = image.shape

# Compute lateral slopes between neighboring pixels (horizontal gradient)
def compute_lateral_slope(image):
    slopes = np.zeros_like(image, dtype=float)
    
    print("Computing lateral slopes...")
    start_time = time.time()
    
    for i in range(image_height):
        for j in range(1, image_width):
            # Compute the slope between adjacent pixels
            slopes[i, j-1] = abs(image[i, j] - image[i, j-1])
        
        # Handle the leftmost pixel (use slope between last two pixels for the leftmost)
        slopes[i, 0] = abs(image[i, -1] - image[i, -2])

        # Progress indicator
        if i % 50 == 0:  # Print progress every 50 rows
            print(f"Processed {i}/{image_height} rows")
    
    end_time = time.time()
    print(f"Finished computing slopes in {end_time - start_time:.2f} seconds.")
    
    return slopes

# Adaptive thresholding for better boundary detection
def adaptive_filter_slope(slopes):
    print("Applying adaptive thresholding...")

    # Normalize the slopes to the range [0, 255] and convert to uint8
    slopes_normalized = cv2.normalize(slopes, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Apply Otsu's thresholding
    _, hit_pixels = cv2.threshold(slopes_normalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    hit_pixels = hit_pixels.astype(bool)
    return hit_pixels

# Using connected components to find regions
def march_connected_components(hit_pixels):
    print("Finding connected components...")
    num_labels, labels_im = cv2.connectedComponents(hit_pixels.astype(np.uint8))

    return labels_im

# Fill regions based on connected components
def fill_connected_regions(connected_regions, image):
    print("Filling interior of regions...")

    # Create an empty mask for filling
    filled_image = np.zeros_like(image)

    # Iterate through each label and fill the region
    for label in range(1, connected_regions.max() + 1):
        # Create a mask for the current region
        region_mask = (connected_regions == label).astype(np.uint8)

        # Find contours for the region
        contours, _ = cv2.findContours(region_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Fill the region with white (255) on the mask
        cv2.drawContours(filled_image, contours, -1, 255, thickness=cv2.FILLED)

    return filled_image

# Main logic
slopes = compute_lateral_slope(image)
hit_pixels = adaptive_filter_slope(slopes)
connected_regions = march_connected_components(hit_pixels)
filled_regions = fill_connected_regions(connected_regions, image)

# Display results
highlighted_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

# Overlay the filled regions in red
highlighted_image[filled_regions == 255] = [0, 0, 255]

cv2.imshow('Filled Concave Regions', highlighted_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
