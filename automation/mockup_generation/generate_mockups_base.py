import cv2
import numpy as np
import math



def place_art_on_background(
    background_path,
    art_path,
    center_x,
    center_y,
    fraction_of_background_area=0.1
):
    """
    1. Reads the background and art images.
    2. Scales the art so that its area is 'fraction_of_background_area'
       of the background's area.
    3. Places the center of the scaled art at (center_x, center_y).
    4. Optionally adjusts brightness via a local brightness map around that region.
    5. Returns the resulting composite image.
    """

    # --- 1. Read images ---
    background = cv2.imread(background_path)
    art_piece = cv2.imread(art_path)

    if background is None:
        raise IOError(f"Could not read background image: {background_path}")
    if art_piece is None:
        raise IOError(f"Could not read art image: {art_path}")

    # Dimensions of background
    H_bg, W_bg = background.shape[:2]
    # Dimensions of art
    H_art, W_art = art_piece.shape[:2]

    # --- 2. Scale art piece based on fraction of background area ---
    background_area = W_bg * H_bg
    target_area = background_area * fraction_of_background_area  # e.g. 0.1 -> 10%

    # Maintain aspect ratio of the art piece
    art_aspect = W_art / float(H_art)

    # Solve for new width/height so that (new_w * new_h) ~ target_area
    #    new_w / new_h = art_aspect
    # => new_w = sqrt(target_area * art_aspect)
    # => new_h = new_w / art_aspect
    new_w = int(math.sqrt(target_area * art_aspect))
    new_h = int(new_w / art_aspect)

    # Handle edge cases if target_area is too small/big, or if new_w/new_h = 0
    new_w = max(1, new_w)
    new_h = max(1, new_h)

    # Resize the art piece
    resized_art = cv2.resize(art_piece, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # --- 3. Compute the top-left corner so that the art’s center is at (center_x, center_y) ---
    tl_x = center_x - (new_w // 2)
    tl_y = center_y - (new_h // 2)

    # --- 4. Create a local brightness map for a more realistic placement (optional) ---
    #       We'll take a local patch from the background in grayscale and blend.
    #       You can skip or simplify this if you don’t need brightness blending.

    # Convert background to grayscale
    gray_bg = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)

    # For local brightness, we need at least the patch the size of the new art
    # centered at (center_x, center_y).
    # We'll clamp to image boundaries below anyway.

    # Ensure bounding coords don’t exceed the background
    # (We also handle partial overlap in case the art extends out of bounds)
    final_tl_x = max(0, tl_x)
    final_tl_y = max(0, tl_y)
    final_br_x = min(W_bg, tl_x + new_w)
    final_br_y = min(H_bg, tl_y + new_h)

    # If the bounding region is completely outside the background, skip
    if final_tl_x >= W_bg or final_tl_y >= H_bg or final_br_x <= 0 or final_br_y <= 0:
        # The art is completely out of bounds. You could either skip or bail out.
        print("Art placement is completely out of background bounds.")
        return background

    # Crop the portion of the art piece that fits in the background
    # in case part of it goes outside the image.
    fit_w = final_br_x - final_tl_x
    fit_h = final_br_y - final_tl_y

    # Resize the art piece to the portion that actually fits
    art_roi = resized_art[0:fit_h, 0:fit_w]

    # Get local grayscale patch from the background
    local_bg_patch = gray_bg[final_tl_y:final_br_y, final_tl_x:final_br_x]

    # To avoid noise, blur that patch a bit
    local_bg_patch = cv2.GaussianBlur(local_bg_patch, (21, 21), 0)

    # Compute average brightness of that patch
    mean_brightness = max(1.0, np.mean(local_bg_patch))  # avoid /0

    # Convert to float
    art_roi_float = art_roi.astype(np.float32)
    local_bg_patch_float = local_bg_patch.astype(np.float32)

    # Make local_bg_patch 3-channel for direct multiply
    local_bg_patch_3ch = cv2.merge([local_bg_patch_float,
                                    local_bg_patch_float,
                                    local_bg_patch_float])

    # brightness ratio map
    ratio_map = local_bg_patch_3ch / mean_brightness  # shape: (fit_h, fit_w, 3)

    # Scale the art piece by that ratio map
    adjusted_art_roi = art_roi_float * ratio_map
    adjusted_art_roi = np.clip(adjusted_art_roi, 0, 255).astype(np.uint8)

    # --- 5. Overlay the adjusted art onto the background ---
    # (Just a hard overwrite; if you want alpha blending, see commented lines below)

    # Hard overwrite
    background[final_tl_y:final_br_y, final_tl_x:final_br_x] = adjusted_art_roi

    # # Example for alpha blending:
    # alpha = 0.8
    # orig_bg_roi = background[final_tl_y:final_br_y, final_tl_x:final_br_x].astype(np.float32)
    # blend_result = cv2.addWeighted(orig_bg_roi, 1 - alpha,
    #                                adjusted_art_roi.astype(np.float32), alpha, 0)
    # background[final_tl_y:final_br_y, final_tl_x:final_br_x] = blend_result.astype(np.uint8)

    return background


if __name__ == "__main__":

    # Example usage:
    background_path = 'AdobeStock_303028184.jpeg'
    art_path = '1quilt_real__real_real.jpg'

    xy = input(f'Background dimensions are {cv2.imread(background_path).shape[1]}x{cv2.imread(background_path).shape[0]}. \n Enter the center x and y for center, with (0,0) at top left (x,y): ')

    user_center_x = int(xy.split(',')[0])
    user_center_y = int(xy.split(',')[1])

    fraction = 0.1165  # e.g. 15% of background's total pixel area

    result = place_art_on_background(
        background_path=background_path, 
        art_path=art_path,  
        center_x=user_center_x,
        center_y=user_center_y,
        fraction_of_background_area=fraction
    )

    # Show or save result
    if result is not None:
        cv2.imwrite("placed_art.jpg", result)
