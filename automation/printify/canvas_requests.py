import requests
import pandas as pd
import base64
import os

"""
dependencies:

product_information.csv.

    path to file
    title
    description
    tags

price
product id
"blueprint_id": 50,  # Replace with the actual blueprint ID (This is the canvas base variation labeled by printify)

"""
# Set your API credentials
access_token = os.environ.get("PRINTIFY_TOKEN", "")
shop_id = os.environ.get("PRINTIFY_SHOP_ID", "")
 
# Set the URL for the API endpoints
base_url = "https://api.printify.com/v1"
upload_url = f"{base_url}/uploads/images.json"
product_url = f"{base_url}/shops/{shop_id}/products.json"
 
# Load the CSV file
csv_path = "product_information.csv"  # Update this to your CSV file path
image_df = pd.read_csv(csv_path)
 
# Set headers for requests
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
 
for idx, row in image_df.iterrows():
    # Convert the image to Base64
    with open(row['local_path'], "rb") as img_file:
        img_b64 = base64.b64encode(img_file.read()).decode('utf-8')
 
    # Upload the image to the Printify media library
    data = {
        "file_name": row['file_name'],
        "contents": img_b64
    }
    response = requests.post(upload_url, headers=headers, json=data)
    image_id = response.json()["id"]
 
    # Create the product with the uploaded image
    data = {
        "title": row['title'],
        "description": row['description'],
        "tags": row['tags'].split(', '),  # Assuming tags are comma-separated in the CSV
        "blueprint_id": 50,  # Replace with the actual blueprint ID (This is the canvas base variation labeled by printify (the type of canvas))
        "print_provider_id": 2,  # Replace with the actual print provider ID (find this from url link on a fulfillment providers page)
        "variants": [
            {
                "id": 34244,  # Replace with the actual variant ID (canvas background color)
                "price": 1999,  #formatted as $XX.XX
                "is_enabled": True
            }
        ],
        "print_areas": [
            {
                "variant_ids": [34244],  # Replace with the actual variant ID (canvas background color)
                "placeholders": [
                    {
                        "position": "front",   #location on shirt, check options on printify
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
    if response.status_code >= 200 and response.status_code < 300:
        print(f"Product {idx+1} created successfully!")
    else:
        print(f"Failed to create product {idx+1}. Server responded with: {response.text}")