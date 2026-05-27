import cv2
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import os

################################################################################
# 1. Helper: Opposite Color on the Color Wheel
################################################################################
def opposite_color_rgb(r, g, b):
    """
    Given an (r,g,b) in [0..1], convert to HSV, shift the Hue by 0.5 (180 degrees),
    then convert back to RGB. Return (r',g',b') in [0..1].
    """
    # Convert to HSV
    hsv = mcolors.rgb_to_hsv([r, g, b])  # [h, s, v], each in [0..1]
    # Add 0.5 to hue (mod 1.0) => shift 180 degrees on the color wheel
    hsv[0] = (hsv[0] + 0.5) % 1.0
    # Convert back to RGB
    r_opp, g_opp, b_opp = mcolors.hsv_to_rgb(hsv)
    return r_opp, g_opp, b_opp

################################################################################
# 2. Create an Opposite-of-Plasma Colormap
################################################################################
def create_opposite_plasma_cmap(num_samples=256):
    """
    Samples the 'plasma' colormap at discrete points [0..1],
    then for each color, we shift it by 180 degrees on the color wheel.
    Returns a ListedColormap that can be used just like normal colormaps.
    """
    plasma = cm.get_cmap('plasma', num_samples)
    new_colors = []
    for i in range(num_samples):
        # plasma(i) is RGBA in [0..1]
        r, g, b, a = plasma(i)
        r_opp, g_opp, b_opp = opposite_color_rgb(r, g, b)
        new_colors.append((r_opp, g_opp, b_opp, a))
    return mcolors.ListedColormap(new_colors, name='opposite_plasma')

opposite_plasma = create_opposite_plasma_cmap()

################################################################################
# 3. Convert background to [0..1] "values" based on normal or opposite colormap
################################################################################
def background_to_values(bg_img, use_opposite=False):
    """
    Convert each pixel of the background image to a scalar in [0..1] 
    by finding the closest color in the chosen colormap (plasma or opposite_plasma).

    NOTE: This is an expensive operation if done via naive search for each pixel.
    The code below does the naive approach with caching for unique colors.
    """
    # Choose the colormap
    if not use_opposite:
        # Normal 'plasma'
        chosen_cmap = cm.get_cmap('plasma', 256)  # RGBA
    else:
        # Opposite-of-plasma
        chosen_cmap = opposite_plasma

    # Extract the colormap's RGB (ignore alpha)
    cmap_colors = chosen_cmap(np.linspace(0, 1, 256))[:, :3]  # shape (256, 3)

    # Convert BGR->RGB
    rgb_img = cv2.cvtColor(bg_img, cv2.COLOR_BGR2RGB)
    h, w, _ = rgb_img.shape
    
    # Normalize to [0..1]
    rgb_norm = rgb_img.astype(np.float32) / 255.0
    
    # Flatten from (H, W, 3) -> (H*W, 3)
    rgb_flat = rgb_norm.reshape(-1, 3)
    
    # Cache unique colors
    unique_colors, inverse = np.unique(rgb_flat, axis=0, return_inverse=True)
    M = unique_colors.shape[0]

    # For each unique color, find the index of the closest color in the chosen colormap
    color_indices = np.zeros(M, dtype=np.int32)
    
    for i in range(M):
        c = unique_colors[i]  # shape (3,)
        # Compute squared distance to each color in the colormap
        diff = cmap_colors - c
        dist = np.sum(diff*diff, axis=1)
        color_indices[i] = np.argmin(dist)

    # Map each pixel's color to index in [0..255]
    closest_idx_flat = color_indices[inverse]  # shape (N,)
    closest_idx_2d = closest_idx_flat.reshape(h, w)

    # Scale to [0..1]
    values_01 = closest_idx_2d.astype(np.float32) / 255.0
    return values_01

################################################################################
# 4. Alpha Etch Functions
################################################################################
def alpha_etch_sin_cos(w, h):
    """
    Alpha = sin(w) + cos(h).
    We'll map this to [0..1] so it doesn't go negative.
    """
    return np.sin(w) + np.cos(h)

def alpha_etch_sin_cos_shifted(w, h):
    """
    Alpha = sin(w + pi/2) + cos(h + pi/2).
    Similarly mapped to [0..1].
    """
    return np.sin(w + np.pi/2) + np.cos(h + np.pi/2)

def compute_alpha_matrix(img_shape, func):
    """
    Given an image shape (H, W), compute alpha = func(w, h).
    Then scale to [0..1].
    """
    H, W = img_shape[:2]
    # Create coordinate grids
    xs = np.arange(W)
    ys = np.arange(H)
    # We'll do meshgrid in pixel coordinates
    X, Y = np.meshgrid(xs, ys)

    # Convert X,Y to float
    Xf = X.astype(np.float32)
    Yf = Y.astype(np.float32)

    # Evaluate alpha
    alpha_vals = func(Xf, Yf)  # shape (H, W)

    # alpha can range from -2..2 (worst case). We want to clamp to [0..1].
    # Let's shift by +2, then /4.0
    # or do a min/max approach. Choose whichever you prefer:
    alpha_min = np.min(alpha_vals)
    alpha_max = np.max(alpha_vals)

    # If alpha_min != alpha_max, scale
    denom = alpha_max - alpha_min if (alpha_max != alpha_min) else 1e-6
    alpha_scaled = (alpha_vals - alpha_min) / denom  # in [0..1]

    return alpha_scaled

################################################################################
# 5. Blend Two Images with Separate Alpha Channels
################################################################################
def alpha_blend_two_images(imgA, alphaA, imgB, alphaB):
    """
    Perform additive blend:
        out = (alphaA * imgA + alphaB * imgB) / (alphaA + alphaB)
    for each pixel, provided alphaA + alphaB != 0.
    Otherwise, out = 0 (or 0 color) if alpha sums to zero.

    imgA, imgB in shape (H, W, 3) in [0..255].
    alphaA, alphaB in shape (H, W) in [0..1].
    """
    # Convert to float
    A = imgA.astype(np.float32)
    B = imgB.astype(np.float32)
    alphaA_3d = alphaA[..., None]  # shape (H, W, 1)
    alphaB_3d = alphaB[..., None]  # shape (H, W, 1)

    sum_alpha = alphaA_3d + alphaB_3d  # shape (H, W, 1)
    # Avoid divide-by-zero by adding a small epsilon
    epsilon = 1e-8
    out = (alphaA_3d * A + alphaB_3d * B) / (sum_alpha + epsilon)
    # Where sum_alpha=0, out becomes 0. That's typically fine.

    out_clamped = np.clip(out, 0, 255).astype(np.uint8)
    return out_clamped

################################################################################
# 6. MAIN
################################################################################

from Releases.ismethods.check import unique_filename
def main():

    ############################################################################
    # A. Create two versions (normal plasma & opposite plasma)
    ############################################################################
    # 1. Load collage2 copy.png
    bg_path = "collage2 copy.png"  # <-- Update your path here
    bg_img = cv2.imread(bg_path)
    if bg_img is None:
        raise IOError(f"Could not load background image at {bg_path}")

    H, W = bg_img.shape[:2]
    print(f"Background image shape: {H} x {W}")

    # 2. Convert background to plasma-based grayscale in [0..1]
    plasma_values = background_to_values(bg_img, use_opposite=False)

    # 3. Convert background to opposite-of-plasma-based grayscale in [0..1]
    opposite_values = background_to_values(bg_img, use_opposite=True)

    # 4. Convert those grayscale values into actual colors using the respective colormaps
    plasma_cmap = cm.get_cmap('plasma', 256)
    opp_plasma_cmap = opposite_plasma

    # We’ll map each pixel's value to an RGB color
    # values_01 -> colormap(values_01) -> [R,G,B,A]
    # Then discard alpha
    plasma_img = (plasma_cmap(plasma_values)[:, :, :3] * 255).astype(np.uint8)
    opposite_img = (opp_plasma_cmap(opposite_values)[:, :, :3] * 255).astype(np.uint8)

    # Save intermediate results (optional)
    cv2.imwrite("plasma_version.png", cv2.cvtColor(plasma_img, cv2.COLOR_RGB2BGR))
    cv2.imwrite("opposite_plasma_version.png", cv2.cvtColor(opposite_img, cv2.COLOR_RGB2BGR))

    ############################################################################
    # B. Generate a second version using a different random seed in shape code
    #    (if you have a procedural shape or transform to incorporate).
    ############################################################################
    # For example, you might have some shape-generation code that depends on
    # np.random.seed(...). We show just a small placeholder below:
    import numpy.random as rng
    rng.seed(9999)  # Different seed than your first script
    # (Put your shape-plotting or generation code here, if relevant)

    # If you only needed to do the colormap step with a different seed,
    # just do your normal generation steps or transformations here.
    #
    # [ ... your second random-seed-based transformations ... ]

    ############################################################################
    # C. Apply the alpha-etch maps and blend
    ############################################################################
    # alpha1 = sin(w) + cos(h) for the first (plasma_img)
    alpha1 = compute_alpha_matrix(plasma_img.shape, alpha_etch_sin_cos)
    # alpha2 = sin(w + pi/2) + cos(h + pi/2) for the second (opposite_img)
    alpha2 = compute_alpha_matrix(opposite_img.shape, alpha_etch_sin_cos_shifted)

    # Now blend
    blended_out = alpha_blend_two_images(plasma_img, alpha1, opposite_img, alpha2)

    
    # Save final
    out_path = os.path.dirname(os.path.abspath(__file__))+"/merged_alpha_etch_result.png"
    out_path = unique_filename(out_path)

    cv2.imwrite(out_path, cv2.cvtColor(blended_out, cv2.COLOR_RGB2BGR))
    print(f"Saved final blended result to {out_path}")


if __name__ == "__main__":
    main()
