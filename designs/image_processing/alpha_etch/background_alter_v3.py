import cv2
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors

def create_blue_to_purple_cmap():
    """Create a custom colormap from blue to purple."""
    colors = [(0, 0, 1), (0.5, 0, 0.5)]  # Blue to Purple in RGB
    return mcolors.LinearSegmentedColormap.from_list('blue_purple', colors, N=256)

def cycloid_distance(h, w, a=1, b=1):
    """
    Generate a cycloid-like pattern for color distribution.
    a and b can be tuned to adjust the cycloid's shape.
    """
    y, x = np.ogrid[:h, :w]
    center_x, center_y = w // 2, h // 2
    r = np.sqrt((x - center_x)**2 + (y - center_y)**2)
    theta = np.arctan2(y - center_y, x - center_x)
    
    # Simplified cycloid equation for demonstration
    return np.sin(r / a + theta) * b

def smooth_edges(edges, kernel_size=(5, 5)):
    """Smooth the edges using Gaussian blur."""
    return cv2.GaussianBlur(edges, kernel_size, 0)

def apply_colored_engraving(bg_img, engraved_img):
    """
    Apply a colored engraving effect where color transitions from blue near edges to purple at center.
    
    :param bg_img: Background image in BGR format
    :param engraved_img: Image to be engraved in BGR format
    :return: Resulting image with colored engraving on a blue background
    """
    h, w = bg_img.shape[:2]
    
    # Detect edges with Canny and smooth them
    gray_engraved = cv2.cvtColor(engraved_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray_engraved, 100, 200)
    smooth_edges_mask = smooth_edges(edges)

    # Create blue to purple colormap
    cmap = create_blue_to_purple_cmap()

    # Generate cycloid pattern for color distribution
    distance_map = cycloid_distance(h, w)
    # Normalize to [0, 1]
    distance_map = (distance_map - distance_map.min()) / (distance_map.max() - distance_map.min())

    # Apply colormap to distance map
    color_map = cmap(distance_map)

    # Convert to BGR since OpenCV uses BGR 
    color_map_bgr = (color_map[:, :, :3] * 255).astype(np.uint8)[:, :, ::-1]

    # Create the alpha channel based on the smoothed edges
    alpha_channel = (smooth_edges_mask.astype(float) / 255.0)[..., None]

    # Blend engraved image with color_map based on alpha
    engraved_colored = (1 - alpha_channel) * engraved_img + alpha_channel * color_map_bgr
    engraved_colored = engraved_colored.astype(np.uint8)

    # Create blue background
    blue_bg = np.zeros_like(engraved_img)
    blue_bg[:, :] = [255, 0, 0]  # BGR for blue

    # Composite engraved image onto blue background
    result = (1 - alpha_channel) * blue_bg + alpha_channel * engraved_colored
    result = result.astype(np.uint8)

    return result

def main():
    # Image paths
    bg_path = "collage2 copy.png"
    engraved_path = "spicy_big.jpg"

    # Load images
    bg_img = cv2.imread(bg_path)
    engraved_img = cv2.imread(engraved_path)
    
    if bg_img is None or engraved_img is None:
        raise IOError("One or both images could not be loaded.")

    # Ensure images are the same size (resize if necessary)
    h_bg, w_bg = bg_img.shape[:2]
    h_en, w_en = engraved_img.shape[:2]
    if h_bg != h_en or w_bg != w_en:
        engraved_img = cv2.resize(engraved_img, (w_bg, h_bg), interpolation=cv2.INTER_LINEAR)

    # Apply colored engraving
    result = apply_colored_engraving(bg_img, engraved_img)

    # Save result
    out_path = "colored_engraved_on_blue.png"
    cv2.imwrite(out_path, result)
    print(f"Saved result to {out_path}")

if __name__ == "__main__":
    main()