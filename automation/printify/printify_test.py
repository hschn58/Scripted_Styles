import os
import base64
import requests
import pandas as pd
import json
import argparse

# Argument Parsing
parser = argparse.ArgumentParser(description='Upload images to Printify and create products.')
parser.add_argument('prod_info', help='Product type descriptor')
args = parser.parse_args()
prod_info = args.prod_info

# API Credentials
access_token = os.environ.get("PRINTIFY_TOKEN", "")
shop_id = os.environ.get("PRINTIFY_SHOP_ID", "")

# API Endpoints
base_url = "https://api.printify.com/v1"
upload_url = f"{base_url}/uploads/images.json"
product_url = f"{base_url}/shops/{shop_id}/products.json"

# Load CSV File
csv_path = "product_information.csv"
image_df = pd.read_csv(csv_path)

# Headers
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Function to Upload Image and Return Preview URL
def upload_image(image_path):
    """Upload the image to Printify and return its preview URL."""
    url = "https://api.printify.com/v1/uploads/images.json"
    with open(image_path, "rb") as image_file:
        image_content = base64.b64encode(image_file.read()).decode("utf-8")
        payload = {
            "file_name": os.path.basename(image_path),
            "contents": image_content,
        }
        response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        upload_data = response.json()
        print(f"Image uploaded successfully: {upload_data['preview_url']}")
        return upload_data['preview_url']
    else:
        print(f"Failed to upload image: {response.status_code} - {response.text}")
        return None

# Function to Update Product with Tags and Images
def update_product(product_id, tags, new_image_urls):
    """Update the product with new tags and images."""
    url = f"{base_url}/shops/{shop_id}/products/{product_id}.json"
    
    # Fetch Existing Product Data
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch product details: {response.status_code} - {response.text}")
        return False

    product_data = response.json()
    
    # Update Tags
    if tags:
        if "tags" not in product_data:
            product_data["tags"] = []
        # Avoid duplicating tags
        for tag in tags:
            if tag not in product_data["tags"]:
                product_data["tags"].append(tag)
    
    # Update Images
    if new_image_urls:
        if "images" not in product_data:
            product_data["images"] = []
        for image_url in new_image_urls:
            # Avoid duplicating images
            if not any(img.get("src") == image_url for img in product_data["images"]):
                product_data["images"].insert(0, {"src": image_url})
    
    # Update Product via PUT
    update_response = requests.put(url, headers=headers, json=product_data)
    if update_response.status_code == 200:
        print(f"Product {product_id} updated successfully with tags and images.")
        return True
    else:
        print(f"Failed to update product {product_id}: {update_response.status_code} - {update_response.text}")
        return False

# Function to Create Product
def create_product(row, image_id):
    """Create a product with the provided row data and image URL."""
    tags = [word.strip() for word in row['tags'].split(',')]
    data = {
        "title": row['title'],
        "description": row['description'],
        "blueprint_id": 97,
        "print_provider_id": 2,
        "tags": tags,  # Include tags during creation
        "variants": [
            {
                "id": 113155,
                "price": 1299,
                "is_enabled": True
            },
            {
                "id": 113156,
                "price": 1999,
                "is_enabled": True
            },
            # Add more variants as needed
        ],
        "print_areas": [
            {
                "variant_ids": [113155, 113156],
                "background": "#FFFFFF",
                "placeholders": [
                    {
                        "position": "front",
                        "images": [
                            {
                                "id": image_id,
                                "x": 0.5,
                                "y": 0.5,
                                "scale": 1.0,
                                "angle": 0
                            }
                        ]
                    }
                ]
            }
        ]
    }

    response = requests.post(product_url, headers=headers, json=data)
    
    if 200 <= response.status_code < 300:
        print(f"Product created successfully! Status Code: {response.status_code}")
        created_product = response.json()
        product_id = created_product["id"]
        return product_id
    else:
        print(f"Failed to create product. Status Code: {response.status_code} - {response.text}")
        return None

# Function to Upload and Add Mockups
def upload_and_add_mockups(tmp_mockups_dir, product_id):
    """Upload mockups from a directory and associate them with a product."""
    mockup_image_paths = [os.path.join(tmp_mockups_dir, file) for file in os.listdir(tmp_mockups_dir) if file.endswith('.jpg')]
    new_image_urls = []
    
    for mockup_path in mockup_image_paths:
        mockup_url = upload_image(mockup_path)
        if mockup_url:
            new_image_urls.append(mockup_url)
    
    if new_image_urls:
        success = update_product(product_id, [], new_image_urls)  # Empty tags list since tags are already set
        if success:
            print(f"Added {len(new_image_urls)} mockup images to product {product_id}.")
        else:
            print(f"Failed to add mockup images to product {product_id}.")

# Main Loop to Create and Update Products
for idx, row in image_df.iterrows():
    print(f"Processing row {idx+1}/{len(image_df)}")
    
    # Upload Image and Get Preview URL
    image_path = row['local_path']
    image_url = upload_image(image_path)
    
    if not image_url:
        print(f"Skipping product creation for row {idx+1} due to image upload failure.")
        continue
    
    # Create Product with Uploaded Image and Tags
    product_id = create_product(row, image_url)
    
    if not product_id:
        print(f"Skipping tag and image updates for row {idx+1} due to product creation failure.")
        continue
    
    # Upload Additional Mockups (if any)
    tmp_mockups = 'tmp'
    upload_and_add_mockups(tmp_mockups, product_id)
