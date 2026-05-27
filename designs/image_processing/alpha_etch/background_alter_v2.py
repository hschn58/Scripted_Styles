import cv2
import numpy as np
import matplotlib
import matplotlib.cm as cm

def blue_purple_colormap(n=256):
    """
    Create a linear segmented colormap from blue to purple, 
    e.g. (0,0,1) -> (1,0,1).
    Return a matplotlib colormap object.
    """
    cdict = {
        'red':   [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],  # from 0 -> 1 in R
        'green': [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)],  # 0 -> 0 in G
        'blue':  [(0.0, 1.0, 1.0), (1.0, 1.0, 1.0)],  # 1 -> 1 in B
    }
    # Create a LinearSegmentedColormap from the dict
    bp_cmap = matplotlib.colors.LinearSegmentedColormap('BlueToPurple', cdict, N=n)
    return bp_cmap

def smooth_edges(edge_mask, kernel_size=3, iterations=1):
    """
    Smooth the edges via morphological operations or blur.
    - edge_mask: 0/255 result of Canny
    - kernel_size: for morphological smoothing
    - iterations: how many times to apply dilation+erosion
    """
    # Convert 255 => 1 for morphological ops
    edges_bin = (edge_mask > 0).astype(np.uint8)
    # A small kernel
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    
    # E.g. a few dilations+erosions to fill small gaps
    # or you can do cv2.morphologyEx with MORPH_CLOSE
    smoothed = edges_bin
    for _ in range(iterations):
        smoothed = cv2.dilate(smoothed, kernel, iterations=1)
        smoothed = cv2.erode(smoothed, kernel, iterations=1)
    
    # Convert back to 0/255
    return (smoothed * 255).astype(np.uint8)

def cycloid_map(distance_map):
    """
    Transform distances to [0..1] using a cycloid-based formula:
       x(t) = (t - sin(t)) / (T - sin(T))
    where T = max distance in the map.
    Return the resulting scalar map.
    """
    max_dist = distance_map.max()
    if max_dist <= 0:
        # No distances? e.g. entire image is edges => return zeros
        return np.zeros_like(distance_map, dtype=np.float32)
    
    # We'll define param t = distance_map (you could multiply by a scale factor)
    t = distance_map.astype(np.float32)
    
    # x(t) = t - sin(t)
    x = t - np.sin(t)
    
    # x(max_dist) = max_dist - sin(max_dist)
    x_max = max_dist - np.sin(max_dist)
    
    # Avoid division by zero check
    if x_max == 0:
        return np.zeros_like(distance_map, dtype=np.float32)
    
    # Normalized
    x_norm = x / x_max
    
    # Clip to [0..1]
    x_norm = np.clip(x_norm, 0, 1)
    return x_norm

def main():
    # Input image paths
    bg_path = "spicy_big.jpg"
    engraved_path =  "collage2 copy.png"

    # 1) Load images
    bg_img = cv2.imread(bg_path)       # The image where we'll find edges
    engraved_img = cv2.imread(engraved_path)
    
    if bg_img is None or engraved_img is None:
        raise IOError("One or both images could not be loaded.")
    
    # 2) Smoothly find edges in bg_img
    gray_bg = cv2.cvtColor(bg_img, cv2.COLOR_BGR2GRAY)
    # Canny
    canny_raw = cv2.Canny(gray_bg, 100, 200)
    
    # Smooth the edge mask to avoid very rough lines
    canny_smooth = smooth_edges(canny_raw, kernel_size=3, iterations=2)
    
    # 3) Distance transform
    #    We'll invert so edges=0 => dist=0, background=1 => can measure distance
    edges_inv = 1 - (canny_smooth > 0).astype(np.uint8)
    dist_map = cv2.distanceTransform(edges_inv, cv2.DIST_L2, 3)

    # 4) Cycloid-based scalar map in [0..1]
    dist_scalar = cycloid_map(dist_map)

    # 5) Build a custom "blue to purple" colormap & map each pixel
    bp_cmap = blue_purple_colormap(n=256)
    # Convert dist_scalar => RGBA in [0..1]
    colored_bp = bp_cmap(dist_scalar)  # shape: (H, W, 4), RGBA in [0..1]
    
    # We only need the RGB portion if we plan to do alpha separately
    colored_bp_rgb = (colored_bp[..., :3] * 255).astype(np.uint8)  # shape: (H, W, 3)

    # (Optional) Use dist_scalar itself as alpha as well
    # alpha in [0..1], multiply by 255 => [0..255]
    alpha_channel = (dist_scalar * 255).astype(np.uint8)
    
    # 6) Combine the color from the colormap with the alpha => BGRA
    #    We'll treat this as our "engraving" color map
    #    Resize if needed to match engraved_img
    h_bpr, w_bpr = colored_bp_rgb.shape[:2]
    h_e, w_e = engraved_img.shape[:2]
    
    if (h_bpr != h_e) or (w_bpr != w_e):
        # Resize the colored pattern & alpha to the engraved image's shape
        colored_bp_rgb = cv2.resize(colored_bp_rgb, (w_e, h_e), interpolation=cv2.INTER_LINEAR)
        alpha_channel = cv2.resize(alpha_channel, (w_e, h_e), interpolation=cv2.INTER_LINEAR)
    
    # The "engraving" is now colored_bp_rgb (blue->purple) with alpha_channel
    # If you'd rather modulate the actual engraved_img with that alpha, 
    # you can do so, but let's assume we want the final "engraved lines" 
    # to use the colored pattern directly.
    engraved_bgra = np.dstack((colored_bp_rgb, alpha_channel))  # shape: (h_e, w_e, 4)

    # 7) Create a solid background (blue in BGR = [255,0,0]) to overlay onto
    #    matching the size of 'engraved_bgra'
    blue_bg = np.zeros_like(engraved_bgra[:, :, :3], dtype=np.uint8)
    blue_bg[:] = [255, 0, 0]

    # Convert them to float for alpha blending
    fg = engraved_bgra.astype(np.float32)  # RGBA
    bg = blue_bg.astype(np.float32)        # BGR (no alpha)
    
    # Split out the alpha in [0..1]
    alpha_f = fg[..., 3] / 255.0  # shape: (h_e, w_e)
    alpha_f_3d = alpha_f[..., None]  # shape: (h_e, w_e, 1)

    fg_bgr = fg[..., :3]  # shape: (h_e, w_e, 3)
    bg_bgr = bg           # shape: (h_e, w_e, 3)

    # alpha blend: out = alpha*fg + (1 - alpha)*bg
    out = alpha_f_3d * fg_bgr + (1 - alpha_f_3d) * bg_bgr
    out = np.clip(out, 0, 255).astype(np.uint8)  # shape: (h_e, w_e, 3)

    # (Optional) Keep alpha in the final image if desired
    result_alpha = (alpha_f * 255).astype(np.uint8)
    result_bgra = np.dstack((out, result_alpha))

    # 8) Save result
    out_path = "engraved_on_blue.png"
    cv2.imwrite(out_path, result_bgra)
    print(f"Saved result to {out_path}")

if __name__ == "__main__":
    main()
