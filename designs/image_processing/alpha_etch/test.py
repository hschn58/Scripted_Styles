import cv2
import numpy as np

def engrave_and_smooth(bg_rgba, engrave_img, canny_thresholds=(100, 200), blur_kernel=(30, 30), sigma=100):
    """
    Engraves an image onto a background by modifying the alpha channel where edges are detected.

    - bg_rgba: Background image in BGRA format.
    - engrave_img: Image to be engraved in grayscale.
    - canny_thresholds: Thresholds for Canny edge detection (low, high).
    - blur_kernel: Size of the Gaussian blur kernel for smoothing edges.
    - sigma: Gaussian sigma value for blur.

    Returns the modified BGRA background image.
    """
    # Detect edges with Canny
    edges = cv2.Canny(engrave_img, canny_thresholds[0], canny_thresholds[1])
    
    # Smooth the edges
    smooth_edges = cv2.GaussianBlur(edges, blur_kernel, sigma)
    
    # Normalize smooth_edges to 0-255 range (since Gaussian Blur can give floating-point values)
    smooth_edges = cv2.normalize(smooth_edges, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    # Ensure smooth_edges matches the background's height & width
    h_bg, w_bg = bg_rgba.shape[:2]
    h_ed, w_ed = smooth_edges.shape[:2]
    if h_bg != h_ed or w_bg != w_ed:
        smooth_edges = cv2.resize(smooth_edges, (w_bg, h_bg), interpolation=cv2.INTER_LINEAR)

    # Modify alpha channel: Reduce alpha where there are edges (smoothly)
    alpha = bg_rgba[..., 3]
    # Here we're subtracting from alpha to simulate engraving; the strength can be adjusted
    alpha_out = np.clip((alpha - smooth_edges+0.5), 0, 255).astype(np.uint8)
    bg_rgba[..., 3] = alpha_out

    return bg_rgba

def main():
    bg_path = "collage2 copy.png"
    engrave_path = "spicy.jpg"

    # Load background in BGRA format
    bg_rgba = cv2.imread(bg_path, cv2.IMREAD_UNCHANGED)
    if bg_rgba is None:
        raise IOError(f"Could not load background: {bg_path}")
    
    # Ensure BGRA format
    if bg_rgba.shape[2] == 3:  # BGR image
        alpha = np.full((bg_rgba.shape[0], bg_rgba.shape[1], 1), 255, dtype=bg_rgba.dtype)
        bg_rgba = np.concatenate([bg_rgba, alpha], axis=2)
    elif bg_rgba.shape[2] == 1:  # Grayscale image
        bg_rgba = np.concatenate([np.repeat(bg_rgba, 3, axis=2), np.full_like(bg_rgba, 255)], axis=2)

    # Load engrave image in grayscale for Canny
    engrave_img = cv2.imread(engrave_path, cv2.IMREAD_GRAYSCALE)
    if engrave_img is None:
        raise IOError(f"Could not load engraving image: {engrave_path}")

    # Apply engraving effect
    result = engrave_and_smooth(bg_rgba, engrave_img, canny_thresholds=(100, 200), blur_kernel=(5, 5), sigma=0)

    # Save result
    out_path = "engraved_out.png"
    cv2.imwrite(out_path, result)
    print(f"Saved engraved result to {out_path}")

if __name__ == "__main__":
    main()