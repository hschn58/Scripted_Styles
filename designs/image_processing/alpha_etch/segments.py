import cv2
import numpy as np
import matplotlib.cm as cm


def background_to_plasma_value(bg_img):
    """
    Convert each pixel of the background image to a scalar in [0..1] 
    by finding the closest color in the 'plasma' colormap.
    This version caches by unique colors to reduce computation.
    """
    # Convert BGR->RGB
    rgb_img = cv2.cvtColor(bg_img, cv2.COLOR_BGR2RGB)
    h, w, _ = rgb_img.shape
    
    # Normalize to [0..1]
    rgb_norm = rgb_img.astype(np.float32) / 255.0
    
    # Flatten from (H, W, 3) -> (H*W, 3)
    rgb_flat = rgb_norm.reshape(-1, 3)
    
    # Get unique colors and the 'inverse' map
    unique_colors, inverse = np.unique(rgb_flat, axis=0, return_inverse=True)
    # unique_colors has shape (M, 3)
    # inverse has shape (N,)

    # Prepare the plasma colormap (256 discrete steps)
    plasma_cmap = cm.get_cmap('plasma', 256)  # RGBA
    colors = plasma_cmap(np.linspace(0, 1, 256))[:, :3]  # shape (256, 3)

    # For each unique color, find index of closest color in plasma
    # We'll do a naive distance approach, but only M times, not N times.
    M = unique_colors.shape[0]
    
    # We'll store results here
    color_indices = np.zeros(M, dtype=np.int32)
    
    for i in range(M):
        # shape (3,)
        c = unique_colors[i]  # normalized color in [0..1]
        # shape (256, 3)
        # compute distances to each colormap color
        diff = colors - c
        dist = np.sum(diff*diff, axis=1)  # squared distance
        # argmin
        color_indices[i] = np.argmin(dist)

    # Now map back from (M,) to (N,)
    # i.e., for each pixel => color_indices[ inverse[pixel_idx] ]
    closest_idx_flat = color_indices[inverse]  # shape (N,)

    # Reshape to (H, W)
    closest_idx_2d = closest_idx_flat.reshape(h, w)

    # Scale to [0..1] by dividing by 255
    # (closest_idx_2d is in [0..255])
    plasma_values = closest_idx_2d.astype(np.float32) / 255.0
    return plasma_values


def apply_opacity(opacity_matrix):
    """
    Applies the opacity from opacity_matrix [0..1] to the engraved image.
    Returns a BGRA image (adds alpha channel).
    
    :param engraved_img: Image to be engraved (BGR)
    :param opacity_matrix: 2D array of opacity values [0..1], same size as engraved_img
    :return: BGRA image with alpha channel
    """
    # If sizes differ, resize the opacity matrix to match the engraved_img
    # (Alternatively, raise an error or handle differently.)
    
    h_o, w_o = opacity_matrix.shape[:2]
    
    engraved_img=np.zeros((w_o, h_o, 3))
    # Convert to alpha channel [0..255]
    alpha_channel = (opacity_matrix * 255).astype(np.uint8)  # shape: (H, W)
    bgra_img = np.dstack((engraved_img, alpha_channel))      # shape: (H, W, 4)

    return bgra_img


def main():
    # Image paths (set to your own)
    bg_path = "collage2 copy.png"
    engraved_path = "spicy_big.jpg"

    # Load images
    bg_img = cv2.imread(bg_path)        # BGR
    
    if bg_img is None:
        raise IOError("One or both images could not be loaded.")

    # Convert background to plasma values in [0..1]
    opacity_matrix = background_to_plasma_value(bg_img)

    # Apply opacity to engraved image
    engraved_with_opacity = apply_opacity(opacity_matrix)

    # Create a solid blue background (BGR=255,0,0)
    # matching the size of 'engraved_with_opacity'
    h_ew, w_ew = engraved_with_opacity.shape[:2]
    blue_bg = np.zeros((h_ew, w_ew, 3), dtype=np.uint8)
    blue_bg[:] = [255, 0, 0]  # BGR for blue

    # Overlay engraved image onto blue background
    # Since 'engraved_with_opacity' has an alpha channel, 
    # we can do alpha blending manually, or use cv2.addWeighted in a pinch.
    # But 'addWeighted' doesn't directly use the alpha channel from the second input.
    # If you want actual alpha compositing, we must do it manually. 
    # For demonstration, let's do manual compositing:
    
    # Split the alpha
    alpha_channel = engraved_with_opacity[..., 3].astype(np.float32) / 255.0
    alpha_channel_3d = alpha_channel[..., None]  # shape (H, W, 1)

    fg_bgr = engraved_with_opacity[..., :3].astype(np.float32)
    bg_bgr = blue_bg.astype(np.float32)

    # alpha blend:  out = alpha * FG + (1 - alpha) * BG
    out = (alpha_channel_3d * fg_bgr) + ((1.0 - alpha_channel_3d) * bg_bgr)
    out = out.astype(np.uint8)

    # (Optional) Re-attach alpha if you want final as BGRA
    out_alpha = (alpha_channel * 255).astype(np.uint8)
    result_bgra = np.dstack((out, out_alpha))

    # Save result
    out_path = "engraved_on_blue1.png"
    cv2.imwrite(out_path, result_bgra)
    print(f"Saved result to {out_path}")

if __name__ == "__main__":
    main()






