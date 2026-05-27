import os
import subprocess
import base64
import requests
import json
import time
import pandas as pd
from PIL import Image
import uuid

# ============================================================
# GLOBAL VARIABLES 
# ============================================================
PRODUCT_INFO_PATH = "/.../Printify/Data/product_information.csv"    # CSV file with product info
ETSY_LINK = "https://www.etsy.com/shop/ScriptedStylesArt"
GITHUB_OWNER = "hschn58"
GITHUB_REPO = "ScriptedStyles"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_BRANCH = "main"
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")
# These endpoints are used for image/carousel uploads.
IG_USER_ID = os.environ.get("IG_USER_ID", "")
MEDIA_ENDPOINT = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media"
PUBLISH_ENDPOINT = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish"
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "")
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")
IMG_FOLDER_PATH = "tmp"


# Needed for Reel publishing
global info_df
info_df = pd.read_csv(PRODUCT_INFO_PATH)


# ============================================================
# 1) CAPTION & MEDIA PROCESSING HELPERS
# ============================================================
def format_hashtags(tag_list):
    """
    tag_list: list of comma-separated tags with no spaces.
    """
    tags = tag_list.split(',')
    tags = ['#' + tag.strip().replace(' ', '').replace('-','') for tag in tags]

    return ' '.join(tags) + ' #mathart'

def create_caption():
    caption = ''
    caption += info_df['description'].iloc[0] + ' \n\n'
    caption += 'Link: ' + ETSY_LINK + ' \n\n'
    caption += 'Available in 11\"x14\", 14\"x11\", 11\"x9\", 9\"x11\", 14\"x14\", 28\"x28\"' + ' \n\n'
    caption += 'Printed on high-quality satin paper with price $19-54' ' \n\n'
    caption += format_hashtags(info_df['tags'].iloc[0])
    return caption

CAPTION = create_caption()

Image.MAX_IMAGE_PIXELS = 400000000  # Disable DecompressionBombError
def compress_to_1080_square_image(input_path, quality=85):
    """
    Crops/resizes a local image to 1080x1080, saves to <filename>_1080_square.jpg.
    """
    with Image.open(input_path) as img:
        width, height = img.size
        side = min(width, height)
        left = (width - side) // 2
        top  = (height - side) // 2
        right = left + side
        bottom= top  + side

        img_cropped = img.crop((left, top, right, bottom))
        img_resized = img_cropped.resize((1080, 1080), Image.LANCZOS)

        output_path = os.path.splitext(input_path)[0] + "_1080_square.jpg"
        img_resized.save(output_path, "JPEG", quality=quality)
        return output_path


def compress_to_1080_square_video(input_path, crf=28, preset='fast', audio_bitrate='128k'):
    """
    Crops/resizes a local video to 1080x1080 using FFmpeg and adds the +faststart flag,
    saving it as <filename>_1080_square.mp4.
    
    Adjusted parameters (crf=28, preset='fast') may produce a file that is easier to decode,
    thereby reducing any playback lag.
    """
    output_path = os.path.splitext(input_path)[0] + "_1080_square.mp4"
    filter_string = (
        "crop=min(iw\\,ih):min(iw\\,ih):"
        "(iw - min(iw\\,ih))/2:(ih - min(iw\\,ih))/2,"
        "scale=1080:1080"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", filter_string,
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", preset,
        "-movflags", "+faststart",   # enables progressive download
        "-c:a", "aac",
        "-b:a", audio_bitrate,
        output_path
    ]
    subprocess.run(cmd, check=True)
    return output_path

# ============================================================
# 2) GITHUB HELPERS
# ============================================================
def get_github_file_sha(repo_filepath):
    """
    Returns the 'sha' for an existing file on GitHub, or None if it doesn't exist.
    """
    api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{repo_filepath}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    resp = requests.get(api_url, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("sha")
    return None

def upload_image_to_github(local_filepath, repo_filepath):
    """
    Upload or overwrite local media (image or video) on GitHub (branch=GITHUB_BRANCH).
    Returns the raw GitHub URL if successful, otherwise None.
    """
    with open(local_filepath, "rb") as f:
        content_bytes = f.read()
    content_b64 = base64.b64encode(content_bytes).decode("utf-8")

    api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{repo_filepath}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    sha = get_github_file_sha(repo_filepath)
    payload = {
        "message": "Add/Update media for IG post",
        "content": content_b64,
        "branch":  GITHUB_BRANCH
    }
    if sha:
        payload["sha"] = sha  # needed to overwrite

    response = requests.put(api_url, json=payload, headers=headers)
    if response.status_code in [200, 201]:
        raw_url = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{repo_filepath}"
        print(f"Uploaded to GitHub: {raw_url}")
        return raw_url
    else:
        print("GitHub upload error:", response.text)
        return None

def delete_github_file(repo_filepath):
    """
    Deletes a file from GitHub if it exists.
    """
    api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{repo_filepath}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    # Must get the existing SHA first
    resp = requests.get(api_url, headers=headers)
    if resp.status_code == 200:
        sha = resp.json()["sha"]
        del_payload = {
            "message": "Delete media after posting",
            "sha": sha,
            "branch": GITHUB_BRANCH
        }
        del_resp = requests.delete(api_url, json=del_payload, headers=headers)
        if del_resp.status_code == 200:
            print(f"Deleted {repo_filepath} from GitHub.")
        else:
            print("Error deleting file:", del_resp.text)
    else:
        print(f"No existing file {repo_filepath} to delete.")

# ============================================================
# 3) INSTAGRAM API HELPERS
# ============================================================
def create_ig_image_container(image_url):
    """
    Creates an IG image container from a public 'image_url'.
    """
    params = {
        "image_url": image_url,
        "caption": CAPTION,       # Using the same caption for every image
        "access_token": PAGE_ACCESS_TOKEN
    }
    resp = requests.post(MEDIA_ENDPOINT, params=params)
    if resp.status_code == 200:
        c_id = resp.json().get("id")
        print("Created IG image container:", c_id)
        return c_id
    else:
        print("Error creating IG image container:", resp.text)
        return None

def create_ig_reel_container(video_url):
    """
    Creates an IG reel container from a public 'video_url'.
    """
    reel_endpoint = f"https://graph.facebook.com/v16.0/{IG_USER_ID}/media"
    params = {
         "media_type": "REELS",
         "video_url": video_url,
         "caption": CAPTION,
         "access_token": PAGE_ACCESS_TOKEN,
    }
    resp = requests.post(reel_endpoint, data=params)
    if resp.status_code == 200:
         container_id = resp.json().get("id")
         print("Created IG reel container:", container_id)
         return container_id
    else:
         print("Error creating IG reel container:", resp.text)
         return None

def publish_reel_container(container_id):
    """
    Publishes an IG reel container.
    """
    publish_endpoint = f"https://graph.facebook.com/v16.0/{IG_USER_ID}/media_publish"
    params = {
         "creation_id": container_id,
         "access_token": PAGE_ACCESS_TOKEN
    }
    resp = requests.post(publish_endpoint, data=params)
    if resp.status_code == 200:
         post_id = resp.json().get("id")
         print("Instagram Reel published! Post ID:", post_id)
         return post_id
    else:
         print("Error publishing IG reel container:", resp.text)
         return None

# (The existing video upload helper for carousel remains unchanged.)
def upload_local_video_to_ig(file_path):
    """
    Use the IG 'Resumable Upload' flow to upload a local video file
    (for a carousel item). Returns the container ID.
    """
    file_size = os.path.getsize(file_path)
    
    # Step 1: START
    start_params = {
        "upload_phase": "start",
        "file_size": file_size,
        "media_type": "VIDEO", 
        "access_token": PAGE_ACCESS_TOKEN
    }
    start_resp = requests.post(MEDIA_ENDPOINT, data=start_params)
    if start_resp.status_code != 200:
        print("Error (start phase):", start_resp.text)
        return None
    
    start_data = start_resp.json()
    upload_session_id = start_data.get("upload_session_id")
    if not upload_session_id:
        print("Missing upload_session_id in start phase:", start_resp.text)
        return None
    
    # Step 2: TRANSFER (single-chunk upload)
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    transfer_params = {
        "upload_phase": "transfer",
        "upload_session_id": upload_session_id,
        "access_token": PAGE_ACCESS_TOKEN
    }
    files = {
        "video_file_chunk": (os.path.basename(file_path), file_data)
    }
    transfer_resp = requests.post(MEDIA_ENDPOINT, params=transfer_params, files=files)
    if transfer_resp.status_code != 200:
        print("Error (transfer phase):", transfer_resp.text)
        return None
    
    # Step 3: FINISH
    finish_params = {
        "upload_phase": "finish",
        "upload_session_id": upload_session_id,
        "is_carousel_item": "true",   # IMPORTANT for carousel videos!
        "access_token": PAGE_ACCESS_TOKEN
    }
    finish_resp = requests.post(MEDIA_ENDPOINT, data=finish_params)
    if finish_resp.status_code != 200:
        print("Error (finish phase):", finish_resp.text)
        return None
    
    finish_data = finish_resp.json()
    container_id = finish_data.get("id")
    if container_id:
        print(f"Created IG video container (carousel): {container_id}")
    return container_id

def create_carousel_parent(child_ids):
    """
    Creates the parent container referencing multiple child IDs, returning parent container ID.
    """
    payload = {
        "media_type": "CAROUSEL",
        "children": ",".join(child_ids),
        "caption": CAPTION,
        "access_token": PAGE_ACCESS_TOKEN
    }
    resp = requests.post(MEDIA_ENDPOINT, data=payload)
    if resp.status_code == 200:
        p_id = resp.json().get("id")
        print("Parent carousel container:", p_id)
        return p_id
    else:
        print("Error creating carousel container:", resp.text)
        return None

def publish_container(container_id):
    """
    Publishes the parent container to IG feed.
    """
    data = {
        "creation_id": container_id,
        "access_token": PAGE_ACCESS_TOKEN
    }
    resp = requests.post(PUBLISH_ENDPOINT, data=data)
    if resp.status_code == 200:
        post_id = resp.json().get("id")
        print("Instagram post published! Post ID:", post_id)
    else:
        print("Error publishing IG container:", resp.text)

# ============================================================
# 4) FACEBOOK PAGE POSTING FUNCTIONS
# ============================================================
def get_unique_repo_filepath(local_filepath, folder):
    """
    Returns a unique repository filepath by appending a UUID to the original filename.
    """
    filename = os.path.basename(local_filepath)
    base, ext = os.path.splitext(filename)
    unique_name = f"{base}_{uuid.uuid4().hex}{ext}"
    return f"{folder}/{unique_name}"

def upload_photo_to_facebook(local_filepath):
    """
    Uploads a photo to the Facebook page as unpublished.
    Returns the photo's ID if successful, otherwise None.
    """
    fb_url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    with open(local_filepath, "rb") as photo_file:
        files = {
            "source": photo_file
        }
        data = {
            "published": "false",
            "access_token": FB_PAGE_ACCESS_TOKEN
        }
        resp = requests.post(fb_url, data=data, files=files)
    if resp.status_code == 200:
        photo_id = resp.json().get("id")
        print(f"Uploaded photo to Facebook, ID: {photo_id}")
        return photo_id
    else:
        print("Error uploading photo to Facebook:", resp.text)
        return None

def create_facebook_post(photo_ids, message):
    """
    Creates a Facebook page post with the uploaded photos attached.
    Expects photo_ids as a list.
    """
    attached_media = [{"media_fbid": pid} for pid in photo_ids]
    fb_feed_url = f"https://graph.facebook.com/{FB_PAGE_ID}/feed"
    data = {
        "message": message,
        "attached_media": json.dumps(attached_media),
        "access_token": FB_PAGE_ACCESS_TOKEN,
    }
    resp = requests.post(fb_feed_url, data=data)
    if resp.status_code == 200:
        post_id = resp.json().get("id")
        print(f"Facebook post created with ID: {post_id}")
        return post_id
    else:
        print("Error creating Facebook post:", resp.text)
        return None
    
def upload_video_to_facebook_reel(local_filepath, title, description=CAPTION):
    """
    Uploads a video as a Facebook Reel using the Graph API.
    Returns the video ID if successful, otherwise None.

    Note: Facebook’s support for Reels via the Graph API may require the parameter 
    "content_category" (set to "REELS") or a similar flag. Check the latest Facebook API docs.
    """
    fb_video_url = f"https://graph-video.facebook.com/{FB_PAGE_ID}/videos"
    with open(local_filepath, "rb") as video_file:
        files = {
            "source": video_file
        }
        data = {
            "title": title,
            "description": description,
            "content_category": "HOME",  # This flag tells Facebook to treat the video as a Reel.
            "access_token": FB_PAGE_ACCESS_TOKEN,
        }
        resp = requests.post(fb_video_url, data=data, files=files)
    if resp.status_code == 200:
        video_id = resp.json().get("id")
        print("Uploaded Facebook Reel video, ID:", video_id)
        return video_id
    else:
        print("Error uploading Facebook Reel video:", resp.text)
        return None


# ============================================================
# 5) MAIN WORKFLOW
# ============================================================
def main():
    # 1) Compress images/videos in folder (for all images/videos in the designated folder)
    for f in os.listdir(IMG_FOLDER_PATH):
        fullpath = os.path.join(IMG_FOLDER_PATH, f)
        if f.lower().endswith(".jpg") and "_1080_square" not in f:
            compress_to_1080_square_image(fullpath, quality=95)
        # elif f.lower().endswith(".mp4") and "_1080_square" not in f:
        #     compress_to_1080_square_video(fullpath, crf=23, preset="medium", audio_bitrate="128k")
    
    # --------------------------------------------------
    # NEW: Process the featured image (clearest representation)
    product_df = pd.read_csv(PRODUCT_INFO_PATH)
    featured_local_path = product_df['local_path'].iloc[0]
    
    featured_processed_path = compress_to_1080_square_image(featured_local_path, quality=95)
    featured_filename = os.path.basename(featured_processed_path)
    # --------------------------------------------------
    
    # 2) Gather the processed files that contain "_1080_square" in the IMG_FOLDER_PATH
    processed_files = []
    for f in os.listdir(IMG_FOLDER_PATH):
        # Only add files that are processed images or MP4 videos.
        if "_1080_square" in f or f.lower().endswith(".mp4"):
            processed_files.append(f)
    
    # Remove featured image from list so it is uploaded only once.
    if featured_filename in processed_files:
        processed_files.remove(featured_filename)
    
    # 3) For each processed file, create Instagram containers and also upload to Facebook.
    all_ig_container_ids = []
    fb_photo_ids = []
    
    # --- First: Upload the featured image so it appears first ---
    if featured_processed_path:
        # Instagram: Upload the featured image to GitHub and create an IG container.
        repo_filepath_featured = get_unique_repo_filepath(featured_processed_path, "images")
        raw_url_featured = upload_image_to_github(featured_processed_path, repo_filepath_featured)
        if raw_url_featured:
            ig_featured_id = create_ig_image_container(raw_url_featured)
            if ig_featured_id:
                all_ig_container_ids.append(ig_featured_id)
            delete_github_file(repo_filepath_featured)
        
        # Facebook: Upload the featured image directly.
        fb_featured_photo_id = upload_photo_to_facebook(featured_processed_path)
        if fb_featured_photo_id:
            fb_photo_ids.append(fb_featured_photo_id)
    
    # --- Then: Process the other files ---
    for pf in processed_files:
        fullpath = os.path.join(IMG_FOLDER_PATH, pf)
        if pf.lower().endswith(".jpg"):
            # For images: upload to GitHub using a unique repo filepath and create an IG container.
            repo_filepath = get_unique_repo_filepath(fullpath, "images")
            raw_url = upload_image_to_github(fullpath, repo_filepath)
            if raw_url:
                ig_container_id = create_ig_image_container(raw_url)
                if ig_container_id:
                    all_ig_container_ids.append(ig_container_id)
                delete_github_file(repo_filepath)
            
            # Facebook: Upload the local image.
            fb_photo_id = upload_photo_to_facebook(fullpath)
            if fb_photo_id:
                fb_photo_ids.append(fb_photo_id)
        
        elif pf.lower().endswith(".mp4") and "_1080_square" not in pf:
            # Facebook Reel

            processed_video_path = compress_to_1080_square_video(fullpath)

            fb_reel_id = upload_video_to_facebook_reel(processed_video_path, title=info_df['title'].iloc[0], description=CAPTION)
            time.sleep(15)
            if fb_reel_id:
                print("Facebook Reel Published!")
            else:
                print("No Facebook Reels uploaded; nothing to post on Facebook.")
            
            # For videos: process and upload to GitHub for an IG Reel.
            repo_filepath = get_unique_repo_filepath(fullpath, "videos")  # Use a unique filepath for videos.
            # IG requires a specific format so re-process the video.
            #processed_video_path = #compress_to_1080_square_video(fullpath)
            
            
            raw_url = upload_image_to_github(processed_video_path, repo_filepath)
            if raw_url:
                ig_reel_container_id = create_ig_reel_container(raw_url)
                time.sleep(45)
                time.sleep(15)
                if ig_reel_container_id:
                    publish_reel_container(ig_reel_container_id)
                delete_github_file(repo_filepath)
    
    # 4) Create and publish an IG carousel if there is at least one image container.
    if all_ig_container_ids:
        ig_parent_id = create_carousel_parent(all_ig_container_ids)
        if ig_parent_id:
            publish_container(ig_parent_id)
    else:
        print("No Instagram image containers created; nothing to post on Instagram for images.")
    
    # 5) Create a Facebook page post if we have at least one photo.
    if fb_photo_ids:
        create_facebook_post(fb_photo_ids, CAPTION)
    else:
        print("No Facebook photos uploaded; nothing to post on Facebook.")



if __name__ == "__main__":
    main()
