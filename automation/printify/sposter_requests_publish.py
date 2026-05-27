import requests
import pandas as pd
import base64
import os
import json
import requests
import argparse
import time


csv_path = "product_information.csv"
access_token = os.environ.get("PRINTIFY_TOKEN", "")
shop_id = os.environ.get("PRINTIFY_SHOP_ID", "")
save_dir = 'tmp'   # Update this to your CSV file path
variant_path = 'variant_info.csv'
image_file_path = "image_1.jpg"  # Adjust the path as needed

variant_ids = [33741, 33742, 33748, 33749, 113155, 113156]

######### -Price Per Variant (currently)
# 
# 11"x9" -1828 - 33741
#  9"x11" - 1828 - 33748
# 14"x11" - 1988 - 33742
# 11"x14" - 1988 - 33749
# 14"x14" - 3073 - 113155
# 28"x28" - 5348 - 113156



########


#clear prior stuff:
for file in os.listdir(save_dir):
    
    if file.endswith('.jpg') or file.endswith('.mp4') or file.endswith('.png') or file.endswith('.jpeg'):
        os.remove(os.path.join(save_dir, file))
    



parser = argparse.ArgumentParser(description='Upload images to Printify and create products.')
parser.add_argument('--prod_info', default='satin poster', help='Product type descriptor')
args = parser.parse_args()

prod_info = args.prod_info


from ScriptedStyles.Automation.Mockup_Generation.generate_mockups import product_mockups

#call mockup function to make mockups and video
prod_info_df = pd.read_csv(csv_path)

print('Starting mockup generation...')
product_mockups(art_piece=prod_info_df['local_path'].iloc[0] , prod_info=prod_info)
time.sleep(10)

# Set your API credentials

 
# Set the URL for the API endpoints
base_url = "https://api.printify.com/v1"
upload_url = f"{base_url}/uploads/images.json"
product_url = f"{base_url}/shops/{shop_id}/products.json"
 
# Load the CSV file


 
# Set headers for requests
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
 
class str2(str):
    def __repr__(self):
        # Allow str.__repr__() to do the hard work, then
        # remove the outer two characters, single quotes,
        # and replace them with double quotes.
        return ''.join(('"', super().__repr__()[1:-1], '"'))
    

#handle pricing:
#0.2 +0.065*12.99+0.25 + 12.99*0.03
# print(image_df.iterrows())
# for idx, row in image_df.iterrows():
#     print(idx, row)


for img_idx in range(1):
    # Convert the image to Base64
    with open(prod_info_df['local_path'].iloc[img_idx], "rb") as img_file:
        img_b64 = base64.b64encode(img_file.read()).decode('utf-8')

    # Upload the image to the Printify media library
    data = {
        "file_name": prod_info_df['file_name'].iloc[img_idx],
        "contents": img_b64
    }

    response = requests.post(upload_url, headers=headers, json=data)

# with open('tags_output.txt', 'w') as file:
    
#     file.write(str(response.json()))
#     file.write(str(response.status_code))

image_id = response.json()["id"]



#store tags - they werent being added to initial creation
tags = [str2(word) for word in prod_info_df['tags'].iloc[0].split(', ')]



# Build print_areas list, one per variant.

variant_dimensions = pd.read_csv(variant_path)
sqval = str(prod_info_df['square'].iloc[0])

# sqval = 'true'
square = False
print(sqval)
if sqval.lower() in ['yes', 'true', '1', '1.0']:
    square = True
else:
    square = False


def get_variants(square: bool) -> dict:
    # Define the variant list for a square shape
    variants_non_square = [
        {"id": 33741, "price": 1828, "is_enabled": True},
        {"id": 33742, "price": 1828, "is_enabled": True},
        {"id": 33748, "price": 1988, "is_enabled": True},
        {"id": 33749, "price": 1988, "is_enabled": True},
        {"id": 113155, "price": 3073, "is_enabled": True},
        {"id": 113156, "price": 5348, "is_enabled": True},
    ]
    
    # Define the variant list for non-square shape
    variants_square = [
        {"id": 113155, "price": 3073, "is_enabled": True},
        {"id": 113156, "price": 5348, "is_enabled": True},
    ]
    
    # Return the appropriate dictionary based on the value of 'square'
    return variants_square if square else variants_non_square


print_areas = []
for v_id in variant_ids:
    # Get the dimension string for this variant (e.g., "8x10")
    dims = variant_dimensions[variant_dimensions['variant'] == v_id]['dimensions'].iloc[0]
    try:
        # Parse the dimensions
        w_str, h_str = dims.lower().split('x')
        width = float(w_str)
        height = float(h_str)
    except Exception as e:
        print(f"Error parsing dimensions for variant {v_id}: {dims}. Using 1x1. Error: {e}")
        width, height = 1, 1

    # For a square image that must cover a rectangular print area,
    # one simple approach is to use the ratio of the longer side to the shorter side.
    # (For a square print area the ratio will be 1.0.)
    scale = max(width, height) / min(width, height) if width != height else 1.0

    # Optionally, you might want to tweak this formula. For example, you could
    # multiply by a constant factor to have a bit more overlap.
    # scale = (max(width, height) / min(width, height)) * 1.1

    # Create a print area object for this variant.
    pa = {
        "variant_ids": [v_id],
        "background": "#FFFFFF",
        "placeholders": [
            {
                "position": "front",
                "images": [
                    {
                        "id": image_id,
                        "x": 0.5,    # center horizontally; adjust if needed
                        "y": 0.5,    # center vertically; adjust if needed
                        "scale": scale,
                        "angle": 0
                    }
                ]
            }
        ]
    }
    print_areas.append(pa)

data = {
    "title": prod_info_df['title'].iloc[0],
    "description": prod_info_df['description'].iloc[0],                        #[str2(word) for word in row['tags'].split(', ')],  
    "blueprint_id": 97,  
    "print_provider_id": 2,  
    "tags": ["true"],
    "variants": get_variants(square),
    "print_areas": print_areas,
    "shipping": {"free_shipping": True}
     
}



response = requests.post(product_url, headers=headers, json=data)

if response.status_code >= 200 and response.status_code < 300:
    print(response.status_code)
    print("Product created successfully!")
    created_product = response.json()     # Parse the response JSON into a Python dict
    product_id = created_product["id"]      # Extract the new product's ID

    # Try the shop-based mockup generation endpoint:
    mockup_generate_url = f"https://api.printify.com/v1/shops/{shop_id}/products/{product_id}/mockups/generate.json"
    payload = {
        "variant_ids": [113156]
    }
    
    print("Requesting mockup generation for variant 113156...")   #doesn't work
    generate_response = requests.post(mockup_generate_url, headers=headers, json=payload)
    if generate_response.status_code == 200:
         print("Successfully triggered mockup generation for variant 113156.")
         print(generate_response.json())
    else:
         print("Failed to trigger mockup generation:", generate_response.text)

else:
    print(f"Failed to create product. Server responded with: {response.text}")


########################################################################################################################################
update_url = f"https://api.printify.com/v1/shops/{shop_id}/products/{product_id}.json"

update_data = {
    "tags": tags + ["mathart"]  # Add more tags as needed
}

update_response = requests.put(update_url, headers=headers, json=update_data)

if update_response.status_code >= 200 and update_response.status_code < 300:
    print("Updated product with tags")

else:
    print("Tags update failed:")
########################################################################################################################################

#remove duplicate mockups- doesn't work

import csv
import os
import math


dirname = os.path.dirname(__file__)


# --------------------
# STEP 1: Load your CSV mapping: variant ID -> dimension string
# --------------------
vds = {}
for row in range(len(variant_dimensions)):
    v_id = variant_dimensions['variant'].iloc[row]
    dimension_str = variant_dimensions['dimensions'].iloc[row]
    vds[v_id] = dimension_str


# A helper to reduce "14x14" to "1x1", but keep "11x14" distinct from "14x11"
def reduce_dimension_to_shape(dimension_str):
    # parse "WxH" into integers
    w_str, h_str = dimension_str.lower().split('x')
    w, h = int(w_str), int(h_str)
    gcd_wh = math.gcd(w, h)
    w_reduced = w // gcd_wh
    h_reduced = h // gcd_wh
    # keep orientation: "11x14" != "14x11"
    return f"{w_reduced}x{h_reduced}"

# --------------------
# STEP 2: Fetch product data from Printify
# --------------------
api_key = access_token

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

get_url = f"https://api.printify.com/v1/shops/{shop_id}/products/{product_id}.json"
response = requests.get(get_url, headers=headers)
if not response.ok:
    raise Exception(f"Failed to get product: {response.text}")
product_data = response.json()

# The product JSON has an "images" array
images = product_data.get("images", [])
if not images:
    print("No images found in product data (or empty).")
    # You could decide to exit or handle differently
    # exit()

# --------------------
# STEP 3: Filter to get at most one image per distinct shape
# --------------------
used_shapes = set()
filtered_images = []

for image in images:
    variant_ids = image.get("variant_ids", [])
    
    # If no variants, decide whether to keep it (optional).
    # For example, if it is "is_default", you might keep it as fallback.
    if not variant_ids:
        if image.get("is_default", False):
            filtered_images.append(image)
        continue

    keep_this_image = False
    new_shapes_for_this_image = []

    for v_id in variant_ids:
        if v_id in vds:
            shape_str = reduce_dimension_to_shape(vds[v_id])
            # If we find at least one "new" shape we haven't seen,
            # we will keep this entire image.
            if shape_str not in used_shapes:
                keep_this_image = True
                new_shapes_for_this_image.append(shape_str)

    # If this image references at least one shape that we haven't used before,
    # we keep it and mark those shapes as used.
    if keep_this_image:
        for shape in new_shapes_for_this_image:
            used_shapes.add(shape)
        filtered_images.append(image)

# --------------------
# STEP 4: Ensure at least 1 mockup remains
# --------------------
if not filtered_images:
    # No images survived the filtering, so pick a fallback
    default_mockup = next((img for img in images if img.get("is_default")), None)
    if default_mockup:
        filtered_images.append(default_mockup)
    elif images:
        filtered_images.append(images[0])  # or whatever fallback logic you prefer

# Overwrite the product’s images
product_data["images"] = filtered_images

# --------------------
# STEP 5: De-duplicate SKUs (important for Printify's full product update)
# --------------------
variants = product_data.get("variants", [])
if variants:
    seen_skus = {}
    for variant in variants:
        sku = variant.get("sku", "") or ""
        if sku in seen_skus:
            seen_skus[sku] += 1
            variant["sku"] = f"{sku}_{seen_skus[sku]}"
        else:
            seen_skus[sku] = 0

product_data["variants"] = variants

# --------------------
# STEP 6: Update the product (PUT) to Printify
# --------------------
update_url = f"https://api.printify.com/v1/shops/{shop_id}/products/{product_id}.json"
put_response = requests.put(update_url, headers=headers, data=json.dumps(product_data))
if not put_response.ok:
    print("Error updating product:", put_response.text)
else:
    print("Successfully updated product: 1 mockup per distinct geometric shape!")

########################################################################################################################################

def download_printify_mockups(shop_id, product_id, access_token, save_dir=save_dir):
    """
    Downloads the generated mockup images for a given Printify product.
    Instead of looking for print areas on variants, this function uses the 
    product's top-level "images" array (which contains a "src" key for the mockup URL
    and a "variant_ids" list).
    
    Parameters:
      - shop_id: The ID of the Printify shop.
      - product_id: The ID of the product.
      - access_token: Your Printify API access token.
      - save_dir: Local directory where the images will be saved.
    """
    
    # Ensure the save directory exists
    os.makedirs(save_dir, exist_ok=True)
    
    # Construct the API endpoint URL for product details
    url = f"https://api.printify.com/v1/shops/{shop_id}/products/{product_id}.json"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"Requesting product details from: {url}")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching product details: {response.status_code} - {response.text}")
        return
    
    product_data = response.json()
    
    # Instead of looking for print areas on variants, we use the "images" array.
    images = product_data.get("images", [])
    if not images:
        print("No images found in product data.")
        return
    
    for idx, image in enumerate(images):
        # The image URL is under "src" (as per Printify's response format)
        mockup_url = image.get("src")
        if not mockup_url:
            print(f"No 'src' found for image at index {idx}. Skipping.")
            continue

        # Use the variant_ids (if available) to help name the file.
        variant_ids = image.get("variant_ids", [])
        if variant_ids:
            image_name = "variant_" + "_".join(str(vid) for vid in variant_ids)
        else:
            image_name = f"image_{idx}"
        
        # Remove query parameters from the URL for extension determination.
        clean_url = mockup_url.split('?')[0]
        file_ext = os.path.splitext(clean_url)[1] or ".png"
        file_path = os.path.join(save_dir, f"{image_name}{file_ext}")
        
        print(f"Downloading mockup for variant(s) {variant_ids} from {mockup_url}...")
        img_response = requests.get(mockup_url)
        if img_response.status_code == 200:
            with open(file_path, "wb") as img_file:
                img_file.write(img_response.content)
            print(f"Downloaded mockup to {file_path}")
        else:
            print(f"Failed to download mockup from {mockup_url} (status code {img_response.status_code}).")

# Example usage:

download_printify_mockups(shop_id, product_id, access_token)

########################################################################################################################################
#UPLOAD OTHER IMAGES TO PRINTIFY-DOESNT WORK

variant_ids_for_image = [113156]

# Path to the image you want to upload

# ---------------------------
# Set up headers for API calls
# ---------------------------
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# ---------------------------
# Step 1: Upload Image to Media Library
# ---------------------------
upload_url = "https://api.printify.com/v1/uploads/images.json"

# Read the image and encode it to Base64
with open(image_file_path, "rb") as img_file:
    img_b64 = base64.b64encode(img_file.read()).decode("utf-8")

file_name = os.path.basename(image_file_path)
upload_payload = {
    "file_name": file_name,
    "contents": img_b64
}

print("Uploading image to Printify media library...")
upload_response = requests.post(upload_url, headers=headers, json=upload_payload)

if upload_response.status_code == 200:
    upload_result = upload_response.json()
    uploaded_image_id = upload_result["id"]
    print(f"Image uploaded successfully. Image ID: {uploaded_image_id}")
else:
    print("Image upload failed:", upload_response.text)
    exit(1)

# ---------------------------
# Step 2: Retrieve the Existing Product Data
# ---------------------------
get_product_url = f"https://api.printify.com/v1/shops/{shop_id}/products/{product_id}.json"
print("Fetching current product data...")
get_product_response = requests.get(get_product_url, headers=headers)
if get_product_response.status_code == 200:
    product_data = get_product_response.json()
else:
    print("Failed to fetch product data:", get_product_response.text)
    exit(1)

# ---------------------------
# Step 3: Append the New Image to the Product's Images Array
# ---------------------------
# Construct the new image object. When updating a product, each image object can include:
#  - "id": the media library image id
#  - "variant_ids": a list of variant IDs to which the image applies
new_image = {
    "id": uploaded_image_id,
    "variant_ids": variant_ids_for_image
}

# If the product already has images, append the new image.
# Otherwise, create the images list.
if "images" in product_data and isinstance(product_data["images"], list):
    product_data["images"].append(new_image)
else:
    product_data["images"] = [new_image]

# (Optional) Print the updated images list for verification
print("Updated images list:")
print(json.dumps(product_data["images"], indent=2))

# ---------------------------
# Step 4: Update the Product Listing with the New Image
# ---------------------------
update_product_url = f"https://api.printify.com/v1/shops/{shop_id}/products/{product_id}.json"
print("Updating product with the new image...")
update_response = requests.put(update_product_url, headers=headers, json=product_data)
if update_response.status_code == 200:
    print("Product updated successfully with the new image.")
else:
    print("Failed to update product:", update_response.text)
########################################################################################################################################
# Build the Etsy-specific payload to set free shipping and add personalisation instructions.
etsy_payload = {
    "sales_channel_properties": {
        "free_shipping": True,  # Set free shipping to true for your Etsy listing.
        
    }
}

# Construct the URL for updating the product (or the Etsy listing) on Printify.
update_url = f"{base_url}/shops/{shop_id}/products/{product_id}.json"

# Perform the update call.
response = requests.put(update_url, headers=headers, json=etsy_payload)
if response.status_code == 200:
    print("Etsy-specific properties updated successfully!")
else:
    print("Failed to update Etsy properties:", response.text)


########################################################################################################################################
#Publish the draft to Etsy

publish_url = f"{base_url}/shops/{shop_id}/products/{product_id}/publish.json"
publish_payload = {
    "title": True,
    "description": True,
    "images": True,
    "variants": True,
    "tags": True,
    "keyFeatures": True,
    "shipping_template": True
}

publish_response = requests.post(publish_url, headers=headers, json=publish_payload)
if publish_response.status_code == 200:
    print("Product published successfully!")
else:
    raise Exception("Failed to publish product: " + publish_response.text)

#upload mockups to printify
# import os
# import base64
# import requests

# # Replace these placeholders with your details
# tmp_mockups = 'tmp'

# image_paths = []
# for file in os.listdir(tmp_mockups):
#     if file.endswith('.jpg'):
#         image_paths.append(os.path.join(tmp_mockups, file))

# # Headers for the API requests
# HEADERS = {
#     "Authorization": f"Bearer {access_token}",
#     "Content-Type": "application/json",
# }

# def upload_image(image_path):
#     """Upload the image to Printify and return its URL."""
#     url = "https://api.printify.com/v1/uploads/images.json"
#     with open(image_path, "rb") as image_file:
#         # Read and encode the file in Base64
#         image_content = base64.b64encode(image_file.read()).decode("utf-8")
#         payload = {
#             "file_name": os.path.basename(image_path),
#             "contents": image_content,
#         }
#         response = requests.post(url, headers=HEADERS, json=payload)

#     if response.status_code == 200:
#         upload_data = response.json()
#         print(f"Image uploaded successfully: {upload_data['preview_url']}")
#         return upload_data['preview_url']  # Use the URL instead of ID
#     else:
#         print(f"Failed to upload image: {response.text}")
#         return None


# def update_product_images(product_id, image_url):
#     """Update the product images using the image URL."""
#     url = f"https://api.printify.com/v1/shops/{shop_id}/products/{product_id}.json"
    
#     # Fetch the existing product details
#     response = requests.get(url, headers=HEADERS)
#     if response.status_code != 200:
#         print(f"Failed to fetch product details: {response.text}")
#         return

#     product_data = response.json()
    
#     # Insert the new image as the first photo
#     product_data["images"].insert(0, {"src": image_url})  # Use URL here

#     # Update the product
#     update_response = requests.put(url, headers=HEADERS, json=product_data)
#     if update_response.status_code == 200:
#         print("Product images updated successfully.")
#     else:
#         print(f"Failed to update product images: {update_response.text}")


# for image in image_paths:
#     # Upload the image
#     image_id = upload_image(image)

#     # Update the product listing if the upload succeeded
#     if image_id:
#         update_product_images(product_id, image_id)




