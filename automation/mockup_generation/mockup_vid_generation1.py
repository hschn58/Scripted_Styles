import cv2
import numpy as np
import pandas as pd

def create_mockup_video(
    image_path,
    output_video_path,
    MOCK_NAME,
    total_frames=200,
    fps=30,
    PARAMS_PATH='params.csv'
):
    """
    Creates a video that begins with a zoom‐out (from a tight, “art‐focused” crop to a wider crop) 
    and then tilts left and right. The art piece (its center specified via params.csv) remains at 
    the center of the frame throughout.

    It expects a CSV file named 'params.csv' with at least two rows in column 
    'MOCKUP_BACKGROUND_FILENAME':
      - Row 0: a string "x,y" (for example, "350,220") giving the pixel coordinates of the art’s center.
      - Row 1: a float (for example, 0.25) giving the fraction of the base image’s area that the art should cover.
    """
    # 1. Load the base image
    base_img = cv2.imread(image_path)
    if base_img is None:
        raise IOError(f"Could not read image: {image_path}")
    H_base, W_base = base_img.shape[:2]

    # 2. Read the parameters (art center and area scale)
    params = pd.read_csv(PARAMS_PATH)
    # Expect first row: "x,y" (coordinates of art center)
    art_coords_str = params[MOCK_NAME].iloc[0]
    # Second row: area scale (e.g., 0.25 means art occupies 25% of base image area)
    area_scale = float(params[MOCK_NAME].iloc[1])
    art_x, art_y = map(float, art_coords_str.split(','))

    # 3. Decide on an output frame size (here we take a fraction of the base image)
    output_scale = 0.5
    out_w = int(W_base * output_scale)
    out_h = int(H_base * output_scale)
    dst_rect = np.float32([
        [0, 0],
        [out_w - 1, 0],
        [out_w - 1, out_h - 1],
        [0, out_h - 1]
    ])
    center_dst = ((out_w - 1) / 2.0, (out_h - 1) / 2.0)

    # 4. Compute the final crop region (source region for zoom-out end) centered on the art.
    #    We want the largest possible square (with the aspect of out_w:out_h) that stays within the base.
    max_half_w = min(art_x, W_base - art_x)
    max_half_h = min(art_y, H_base - art_y)
    # To maintain the output aspect ratio, we choose half-width as the minimum of the available half-width
    # and the half-height scaled by out_w/out_h.
    final_half_w = min(max_half_w, max_half_h * (out_w / out_h))
    final_half_h = final_half_w * (out_h / out_w)
    final_src = np.float32([
        [art_x - final_half_w, art_y - final_half_h],
        [art_x + final_half_w, art_y - final_half_h],
        [art_x + final_half_w, art_y + final_half_h],
        [art_x - final_half_w, art_y + final_half_h]
    ])

    # 5. Define an initial crop (zoomed-in view) that is smaller than the final crop.
    #    (Here we choose a factor; you might adjust zoom_factor to change how “in” the initial view is.)
    zoom_factor = 0.7  # e.g. initial crop is 70% the size of the final crop.
    init_half_w = final_half_w * zoom_factor
    init_half_h = final_half_h * zoom_factor
    initial_src = np.float32([
        [art_x - init_half_w, art_y - init_half_h],
        [art_x + init_half_w, art_y - init_half_h],
        [art_x + init_half_w, art_y + init_half_h],
        [art_x - init_half_w, art_y + init_half_h]
    ])

    # 6. Divide the total frames into three phases:
    #    Phase 1: Zoom out; Phase 2: Tilt left; Phase 3: Tilt right.
    partition = total_frames // 3

    # 7. Set up the video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_video_path, fourcc, fps, (out_w, out_h))

    # PHASE 1: Zoom Out – interpolate from the zoomed-in (initial_src) to the full final_src.
    for frame_idx in range(partition):
        t = frame_idx / float(partition - 1)  # t goes from 0 to 1
        # Linear interpolation of the four source corners
        current_src = (1 - t) * initial_src + t * final_src
        M = cv2.getPerspectiveTransform(current_src, dst_rect)
        frame = cv2.warpPerspective(
            base_img,
            M,
            (out_w, out_h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0)
        )
        writer.write(frame)

    # Helper: rotate a set of 4 points about a center by angle (in degrees)
    def rotate_points(pts, center, angle_deg):
        angle_rad = np.deg2rad(angle_deg)
        cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
        rot_matrix = np.array([[cos_a, -sin_a],
                               [sin_a,  cos_a]])
        rotated = []
        for p in pts:
            vec = np.array(p) - np.array(center)
            rvec = np.dot(rot_matrix, vec)
            rotated.append(rvec + center)
        return np.float32(rotated)

    # Choose a maximum tilt angle (in degrees) that feels “nice” (adjust as needed)
    max_angle = 5.0

    # PHASE 2: Tilt Left (animate from 0 to +max_angle then back to 0)
    half = partition // 2

    # PHASE 2: Tilt Left
    for frame_idx in range(partition):
        if frame_idx < half:
            t = frame_idx / float(half)
        else:
            t = 1.0 - (frame_idx - half) / float(partition - half)
        current_angle = max_angle * t  # positive angle: tilt left
        # Rotate the destination (old code):
        # current_dst = rotate_points(dst_rect, center_dst, current_angle)
        # M = cv2.getPerspectiveTransform(final_src, current_dst)
        
        # Instead, rotate the source:
        current_src_rotated = rotate_points(final_src, (art_x, art_y), current_angle)
        M = cv2.getPerspectiveTransform(current_src_rotated, dst_rect)
        
        frame = cv2.warpPerspective(
            base_img,
            M,
            (out_w, out_h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0)
        )
        writer.write(frame)


    # PHASE 3: Tilt Right (animate from 0 to -max_angle then back to 0)
    for frame_idx in range(partition):
        if frame_idx < half:
            t = frame_idx / float(half)
        else:
            t = 1.0 - (frame_idx - half) / float(partition - half)
        current_angle = -max_angle * t  # negative angle: tilt right

        current_dst = rotate_points(final_src, (art_x, art_y), current_angle)
        M = cv2.getPerspectiveTransform(current_dst, dst_rect)
        frame = cv2.warpPerspective(
            base_img,
            M,
            (out_w, out_h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0)
        )
        writer.write(frame)

    # 8. Cleanup
    writer.release()
    print(f"[INFO] Video saved to {output_video_path}")


create_mockup_video( 'mockup0_1080_square.jpg',
                    'mockup0_1080_square.mp4',
                    'MockBox_bedroom_12_4x5-wall')