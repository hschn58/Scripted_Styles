import cv2
import numpy as np



# def apply_wave_effect(image, amplitude=5, frequency=4, phase=0):
#     """
#     Applies a horizontal sine-wave distortion to an image.
    
#     :param image: Input image.
#     :param amplitude: Maximum pixel displacement.
#     :param frequency: Number of sine cycles over the image height.
#     :param phase: Phase shift for the sine wave.
#     :return: Distorted image.
#     """
#     h, w = image.shape[:2]
#     # Create a meshgrid of (x, y) coordinates.
#     x_indices, y_indices = np.meshgrid(np.arange(w), np.arange(h))
#     # Compute horizontal displacement based on a sine wave along the y axis.
#     displacement = amplitude * np.sin(2 * np.pi * frequency * y_indices / h + phase)
#     # Build mapping arrays for remap (must be float32).
#     map_x = (x_indices + displacement).astype(np.float32)
#     map_y = y_indices.astype(np.float32)
#     # Remap the image using the computed displacement.
#     distorted = cv2.remap(image, map_x, map_y, interpolation=cv2.INTER_LINEAR, 
#                           borderMode=cv2.BORDER_REFLECT)
#     return distorted

# def crop_center_square(image):
#     """
#     Crops the input image to a centered square based on its smallest dimension.
    
#     :param image: Input image.
#     :return: Square-cropped image.
#     """
#     h, w = image.shape[:2]
#     square_size = min(h, w)
#     margin_x = (w - square_size) // 2
#     margin_y = (h - square_size) // 2
#     return image[margin_y:margin_y+square_size, margin_x:margin_x+square_size]


# def max_static_alpha(t):
#     """ t is valued from 0 to 1

#     Args:
#         t (_type_): _description_
#     """
#     factor = 1/(1+np.exp(-10*(t-0.5)))

#     return 1/(1+np.exp(-10*((1/factor)*t-0.9)))

# def create_mockup_video(
#     image_path,
#     output_video_path,
#     final_image_path,
#     total_frames=500,   # Number of zoom frames.
#     fps=50,
#     zoom_duration_frames=200,  # For dynamic zoom
#     output_scale=1.0  # We will output the full square (so set to 1.0)
# ):
#     """
#     Creates a square video that starts with a dynamic zoom from a square crop
#     of a base image and then transitions into a final image (also square cropped)
#     with an abstract, tech-y effect.
    
#     The video structure is:
#       - Dynamic Zoom frames (from an initial offset crop to the full square)
#       - A creative 7-second transition (with wave distortion, rotation, scaling, color shift,
#         and a dynamic static overlay).
#       - A 1-second hold of the final image.
    
#     :param image_path: Path to the base image.
#     :param final_image_path: Path to the final image.
#     :param output_video_path: Path to save the .mp4 video.
#     :param total_frames: Number of frames for the zoom sequence.
#     :param fps: Frames per second.
#     :param zoom_duration_frames: Number of frames for the dynamic zoom.
#     :param output_scale: Scale factor for output relative to the base square crop (1.0 = full square).
#     """
#     # 1. Load and crop the base image to a square.
#     base_img = cv2.imread(image_path)
#     if base_img is None:
#         raise IOError(f"Could not read image: {image_path}")
#     base_square = crop_center_square(base_img)
#     S = base_square.shape[0]  # Base square side length
    
#     # 2. Define the output size. We want a square video.
#     out_size = int(S * output_scale)  # Here output_scale=1.0 means full resolution of the square crop.
#     out_w = out_h = out_size

#     # 3. Set up the video writer.
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     writer = cv2.VideoWriter(output_video_path, fourcc, fps, (out_w, out_h))
    
#     # 4. Generate dynamic zoom frames.
#     # Define initial crop parameters:
#     # Initial crop size is 60% of S.
#     init_crop_size = 0.6 * S
#     # Initial crop center is shifted to the right by 10% of S.
#     init_center = (S/2 + 0.1 * S, S/2)
#     # Final crop: full square with center at (S/2, S/2) and size S.
#     final_crop_size = S
#     final_center = (S/2, S/2)
    
#     for frame_idx in range(zoom_duration_frames):
#         alpha = frame_idx / (zoom_duration_frames - 1)  # Goes from 0 to 1.
#         # Interpolate crop size and center.
#         current_size = (1 - alpha) * init_crop_size + alpha * final_crop_size
#         current_center_x = (1 - alpha) * init_center[0] + alpha * final_center[0]
#         current_center_y = (1 - alpha) * init_center[1] + alpha * final_center[1]
#         # Calculate crop rectangle (make sure coordinates are integers).
#         x0 = int(current_center_x - current_size/2)
#         y0 = int(current_center_y - current_size/2)
#         x1 = int(x0 + current_size)
#         y1 = int(y0 + current_size)
#         # Ensure the crop rectangle is within base_square boundaries.
#         x0 = max(0, x0)
#         y0 = max(0, y0)
#         x1 = min(S, x1)
#         y1 = min(S, y1)
#         # Crop and resize to output size.
#         crop_frame = base_square[y0:y1, x0:x1]
#         frame = cv2.resize(crop_frame, (out_w, out_h), interpolation=cv2.INTER_LINEAR)
#         writer.write(frame)
#         final_zoom_frame = frame.copy()  # Save the last zoom frame.

#     # 5. Load, crop, and resize the final image.
#     final_img = cv2.imread(final_image_path)
#     if final_img is None:
#         raise IOError(f"Could not read final image: {final_image_path}")
#     final_square = crop_center_square(final_img)
#     final_square = cv2.resize(final_square, (out_w, out_h), interpolation=cv2.INTER_AREA)

#     # Precompute a coordinate grid for the dynamic alpha map (values 0 to 16*pi).
#     w_vals = np.linspace(0, 16 * np.pi, out_w)
#     h_vals = np.linspace(0, 16 * np.pi, out_h)
#     W_grid, H_grid = np.meshgrid(w_vals, h_vals)
    
#     # 6. Create a creative 7-second transition.
#     transition_frames = int(3 * fps)
#     max_wave_amp = 30   # Maximum wave amplitude in pixels.
#     max_angle = 15      # Maximum rotation (degrees) at the end of the transition.
#     start_scale = 1.1   # Start with a slight zoom.
#     end_scale = 1.0     # End at normal scale.

    
#     for i in range(transition_frames):
#         t = i / (transition_frames - 1)  # t moves from 0 to 1.
#         # Calculate creative parameters.
#         amplitude = max_wave_amp * np.sin(9*np.pi * t)  # Peaks mid-transition.
#         phase = 4 * np.pi * t                           # Evolving phase.
#         # Smooth rotation starting at 0 degrees and gradually increasing.
#         angle = max_angle * t                          
#         scale = start_scale - (start_scale - end_scale) * t  # Scale from start_scale to 1.0.
        
#         # (a) Apply a sine-wave distortion to the final zoom frame.
#         creative_frame = apply_wave_effect(final_zoom_frame, amplitude=amplitude, frequency=6, phase=phase)
        
#         # (b) Apply rotation and scaling.
#         center = (out_w / 2, out_h / 2)
#         rotM = cv2.getRotationMatrix2D(center, angle, scale)
#         creative_frame = cv2.warpAffine(
#             creative_frame,
#             rotM,
#             (out_w, out_h),
#             flags=cv2.INTER_LINEAR,
#             borderMode=cv2.BORDER_REFLECT
#         )
        
#         # (c) Apply a slight color shift for extra tech-y flair.
#         shifted_frame = creative_frame.copy()
#         shifted_frame[..., 0] = cv2.add(shifted_frame[..., 0], int(20 * (1 - t)))
        
#         # (d) Blend the creatively transformed frame with the final image.
#         blended = cv2.addWeighted(shifted_frame, 1 - t, final_square, t, 0)
        
#         # (e) Generate a noise layer (static).
#         noise = np.random.randint(0, 256, (out_h, out_w, 3), dtype=np.uint8)
        
#         # (f) Create a dynamic per-pixel alpha map for the static overlay.
#         # Formula: max_static_alpha*sin(t)*0.25*(2 - (cos(w) + sin(h)))
#         alpha_map = np.abs( max_static_alpha(t) * np.sin(1.6*np.pi*t-1.3*np.pi) * 0.25 * (2 - (np.cos(W_grid) + np.sin(H_grid))) )
#         # Expand alpha_map to 3 channels.
#         alpha_map_3 = np.repeat(alpha_map[:, :, np.newaxis], 3, axis=2)
        
#         # Blend the noise with the current blended frame using the dynamic alpha map.
#         blended = (blended.astype(np.float32) * (1 - alpha_map_3) + 
#                    noise.astype(np.float32) * alpha_map_3).astype(np.uint8)
        
#         writer.write(blended)
    
#     # 7. Hold the final image on screen for 1 second.
#     final_hold_frames = int(1 * fps)
#     for i in range(final_hold_frames):
#         writer.write(final_square)
    
#     # 8. Cleanup: release the video writer.
#     writer.release()
#     print(f"[INFO] Video saved to {output_video_path}")

# # Optional helper: compress/convert video to a 1080x1080 square using FFmpeg.
# def compress_to_1080_square_video(input_path, crf=23, preset='medium', audio_bitrate='128k'):
#     """
#     Crops/resizes a local video to 1080x1080 using FFmpeg, saving it as <filename>_1080_square.mp4.
#     """
#     output_path = os.path.splitext(input_path)[0] + "_1080_square.mp4"
#     filter_string = (
#         "crop=min(iw\\,ih):min(iw\\,ih):"
#         "(iw - min(iw\\,ih))/2:(ih - min(iw\\,ih))/2,"
#         "scale=1080:1080"
#     )
#     cmd = [
#         "ffmpeg", "-y",
#         "-i", input_path,
#         "-vf", filter_string,
#         "-c:v", "libx264",
#         "-crf", str(crf),
#         "-preset", preset,
#         "-c:a", "aac",
#         "-b:a", audio_bitrate,
#         output_path
#     ]
#     subprocess.run(cmd, check=True)
#     return output_path

def apply_wave_effect(image, amplitude=5, frequency=4, phase=0):
    """
    Applies a horizontal sine-wave distortion to an image.
    """
    h, w = image.shape[:2]
    x_indices, y_indices = np.meshgrid(np.arange(w), np.arange(h))
    displacement = amplitude * np.sin(2 * np.pi * frequency * y_indices / h + phase)
    map_x = (x_indices + displacement).astype(np.float32)
    map_y = y_indices.astype(np.float32)
    distorted = cv2.remap(image, map_x, map_y, interpolation=cv2.INTER_LINEAR, 
                          borderMode=cv2.BORDER_REFLECT)
    return distorted

def crop_center_square(image):
    """
    Crops the input image to a centered square based on its smallest dimension.
    """
    h, w = image.shape[:2]
    square_size = min(h, w)
    margin_x = (w - square_size) // 2
    margin_y = (h - square_size) // 2
    return image[margin_y:margin_y+square_size, margin_x:margin_x+square_size]

def t_static_fix(t):
    if t <= 1.3/1.6:
        return t
    elif t >= 1.3/1.6 and t <= 1.45/1.6:
        return 1.3/1.6 + (t-1.3/1.6)*2
    else:
        return 1 - (t-1.45/1.6)*2
    

# def max_static_alpha(t):
#     """ t is valued from 0 to 1 """
#     factor = 1/(1+np.exp(-10*(t-0.5)))
#     return 1/(1+np.exp(-10*((1/(factor**2))*t-0.9)))

def max_static_alpha(t):
    """ t is valued from 0 to 1 """
    return 0.4

def create_mockup_video(
    image_path,
    output_video_path,
    final_image_path,
    intro_image_path=None,      # NEW: Intro image path (if None, use the base image),           # Number of zoom frames.
    fps=50,
    zoom_duration_frames=200,   # For dynamic zoom
    output_scale=1.0,           # Full square output.
    zoom_intensity=0.2          # Fraction of the full image used in the initial crop.
):
    """
    Creates a square video that begins with a creative hook that smoothly transforms
    an introductory image into the starting zoom frame, then continues with a dynamic zoom,
    a creative 7-second transition, and a final hold.
    
    Parameters:
      - intro_image_path: Path to an image to use in the introductory hook. If not provided,
                          the base image will be used.
      - zoom_intensity: Fraction (0 < zoom_intensity <= 1) representing the size of the 
                        initial crop relative to the full image. A lower value means a 
                        more intense zoom (i.e. starting from a smaller portion of the image).
    """
    import cv2
    import numpy as np

    # A helper function for center cropping.
    def crop_center_square(img):
        h, w = img.shape[:2]
        min_dim = min(w, h)
        start_x = (w - min_dim) // 2
        start_y = (h - min_dim) // 2
        return img[start_y:start_y+min_dim, start_x:start_x+min_dim]
    
    # A helper function for applying a wavy effect.
    # (Assumes you already have one; if not, substitute your implementation.)
    def apply_wave_effect(img, amplitude, frequency, phase):
        # Create a meshgrid of coordinates.
        h, w = img.shape[:2]
        X, Y = np.meshgrid(np.arange(w), np.arange(h))
        # Create a displacement map based on a sine wave.
        displacement = amplitude * np.sin(2 * np.pi * frequency * Y / h + phase)
        # For each x coordinate, shift by displacement (wrap-around via border reflection).
        map_x = (X + displacement).astype(np.float32)
        map_y = np.float32(Y)
        return cv2.remap(img, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    
    # Optional: a function used in the transition (as in your original code).

    # 1. Load and crop the base image to a square.
    base_img = cv2.imread(image_path)
    if base_img is None:
        raise IOError(f"Could not read image: {image_path}")
    base_square = crop_center_square(base_img)
    S = base_square.shape[0]  # Side length of the square

    # 1.5. Load and crop the intro image.
    # If no intro_image_path is provided, fall back to base_square.
    if intro_image_path is not None:
        intro_img = cv2.imread(intro_image_path)
        if intro_img is None:
            raise IOError(f"Could not read intro image: {intro_image_path}")
        intro_square = crop_center_square(intro_img)
    else:
        intro_square = base_square.copy()

    # 2. Define the output size.
    out_size = int(S * output_scale)
    out_w = out_h = out_size

    # 3. Set up the video writer using a compressed codec.
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    writer = cv2.VideoWriter(output_video_path, fourcc, fps, (out_w, out_h))

    # 4. Compute the first dynamic zoom frame (zoom_start)
    init_crop_size = zoom_intensity * S
    init_center = (S/2 + 0.1 * S, S/2)
    x0 = int(init_center[0] - init_crop_size/2)
    y0 = int(init_center[1] - init_crop_size/2)
    x1 = int(x0 + init_crop_size)
    y1 = int(y0 + init_crop_size)
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(S, x1)
    y1 = min(S, y1)
    crop_zoom_start = base_square[y0:y1, x0:x1]
    zoom_start = cv2.resize(crop_zoom_start, (out_w, out_h), interpolation=cv2.INTER_LINEAR)

    # 5. Generate the introductory hook that transitions from the intro image to zoom_start.
    intro_frames = int(3 * fps)
    max_intro_amp = 400  # Maximum amplitude for the wave effect during intro.
    max_intro_angle = 0
    for i in range(intro_frames):
        t = i / (intro_frames - 1)
        amplitude = max_intro_amp 
        phase = (28/4) * np.pi * t
        angle = max_intro_angle * t  # Rotate up to 10 degrees.

        intro_square = crop_center_square(intro_img)
        intro_square = cv2.resize(intro_square, (out_w, out_h), interpolation=cv2.INTER_AREA)
        
        center = (out_w / 2, out_h / 2)
        # First, rotate the intro image.
        rotM = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            intro_square,
            rotM,
            (out_w, out_h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT
        )
        # Then apply the wavy effect on the rotated image.
        creative = apply_wave_effect(rotated, amplitude=amplitude, frequency=4, phase=phase)
        # Blend the creative frame with the zoom_start frame.
        hook_frame = cv2.addWeighted(creative, 1 - t, zoom_start, t, 0)
        writer.write(hook_frame)
    
    # 6. Generate dynamic zoom frames using subpixel sampling.
    final_zoom_frame = None
    for frame_idx in range(1, zoom_duration_frames):
        alpha = frame_idx / (zoom_duration_frames - 1)
        current_size = (1 - alpha) * init_crop_size + alpha * S
        current_center_x = (1 - alpha) * init_center[0] + alpha * (S/2)
        current_center_y = (1 - alpha) * init_center[1] + alpha * (S/2)
        
        # Use cv2.getRectSubPix for subpixel-accurate cropping.
        crop_size = int(round(current_size))
        crop_frame = cv2.getRectSubPix(base_square, (crop_size, crop_size), (current_center_x, current_center_y))
        
        frame = cv2.resize(crop_frame, (out_w, out_h), interpolation=cv2.INTER_LINEAR)
        writer.write(frame)
        final_zoom_frame = frame.copy()
    
    # 7. Load and prepare the final image.
    final_img = cv2.imread(final_image_path)
    if final_img is None:
        raise IOError(f"Could not read image: {final_image_path}")
    final_square = crop_center_square(final_img)
    final_square = cv2.resize(final_square, (out_w, out_h), interpolation=cv2.INTER_AREA)

    # Precompute a coordinate grid for the dynamic alpha map used in the transition.
    w_vals = np.linspace(0, 16 * np.pi, out_w)
    h_vals = np.linspace(0, 16 * np.pi, out_h)
    W_grid, H_grid = np.meshgrid(w_vals, h_vals)
    
    # 8. Create a creative 7-second transition.
    transition_frames = int(4 * fps)
    max_wave_amp = 100
    max_angle = 15
    start_scale = 1.1
    end_scale = 1.0
    
    for i in range(transition_frames):
        t = i / (transition_frames - 1)
        amplitude = max_wave_amp * np.sin(4 * np.pi * t)
        phase = 4 * np.pi * t
        angle = max_angle * t                          
        scale = start_scale - (start_scale - end_scale) * t  
        creative_frame = apply_wave_effect(final_zoom_frame, amplitude=amplitude, frequency=4, phase=phase)
        center = (out_w / 2, out_h / 2)
        rotM = cv2.getRotationMatrix2D(center, angle, scale)
        creative_frame = cv2.warpAffine(
            creative_frame,
            rotM,
            (out_w, out_h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT
        )
        shifted_frame = creative_frame.copy()
        shifted_frame[..., 0] = cv2.add(shifted_frame[..., 0], int(20 * (1 - t)))
        blended = cv2.addWeighted(shifted_frame, 1 - t, final_square, t, 0)
        noise = np.random.randint(0, 256, (out_h, out_w, 3), dtype=np.uint8)
        alpha_map = np.abs( max_static_alpha(t) * np.sin(1.6*np.pi*t_static_fix(t) - 1.3*np.pi) * 0.25 * ( (2 - (np.cos(W_grid*(1+3*(t-0.5))) + np.sin(H_grid))) + (2 - (np.cos((np.max(W_grid)-W_grid)*(1+3*(t-0.5))) + np.sin(H_grid)))) ) #add it for all other sides!
        alpha_map_3 = np.repeat(alpha_map[:, :, np.newaxis], 3, axis=2)
        blended = (blended.astype(np.float32) * (1 - alpha_map_3) + 
                   noise.astype(np.float32) * alpha_map_3).astype(np.uint8)
        
        writer.write(blended)
    
    # 9. Hold the final image on screen for 1 second.
    final_hold_frames = int(1 * fps)
    for i in range(final_hold_frames):
        writer.write(final_square)
    
    writer.release()
    print(f"[INFO] Video saved to {output_video_path}")



# create_mockup_video(image_path = 'placed_art.jpg',
#                     output_video_path = 'binary_cool111111_1080_square.mp4',
#                     final_image_path = 'logo.png')


# Example usage:

# base_image = 'mockup0.jpg'
# final_image = 'logo.png'  # Final image path.
# output_video = 'mockup0_afterdone.mp4'

# create_mockup_video(
#     image_path=base_image,
#     final_image_path=final_image,
#     output_video_path=output_video,
#     total_frames=200,          # Total frames for zoom sequence.
#     fps=30,
#     zoom_duration_frames=200,  # Dynamic zoom duration.
#     output_scale=1.0           # Full square output.
# )

    # Optionally, compress the video to a 1080x1080 square.
    # compressed_video = compress_to_1080_square_video(output_video)
    # print(f"[INFO] Compressed video saved to {compressed_video}")

