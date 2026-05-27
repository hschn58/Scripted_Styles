import argparse
import csv
import time
import os
from openai import OpenAI
import json
import pandas as pd
from PIL import Image

# ============================
# Command-line argument setup
# ============================
parser = argparse.ArgumentParser(description="Process the PNG path argument for always run script.")
parser.add_argument("--prod_info", type=str, help="Additional information for the process")  # Second positional argument
parser.add_argument("--square", type=str, default = 'true', help="Additional information for the process")  # Second positional argument


args = parser.parse_args()


prod_info = args.prod_info
square = args.square



csv_file_path = "product_information.csv"
csv_file = pd.read_csv(csv_file_path)
png_path = csv_file['local_path'].iloc[0] 
# ===============================
# OpenAI configuration
# Replace 'KEY' with your API key
# ===============================
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

# Constants if you still need them for chunked file reading/writing (can remove if not used)
MAX_TOKENS_PER_REQUEST = 30000
MAX_TOKENS_PER_CHUNK = 25000
RATE_LIMIT_TOKENS_PER_MINUTE = 30000
SECONDS_PER_MINUTE = 60

# ============================================================
# 0) Process photos: ensure they aren't too big
# ============================================================
Image.MAX_IMAGE_PIXELS = 400000000  # Disable DecompressionBombError


def compress_to_1080_square_image(input_path, quality=85):
    """
    Crops/resizes a local image to 1080x1080 and saves it as
    <original_filename_without_extension>_1080_square.jpg
    into a subfolder named "compressed_images" (created if not existing)
    in the same directory as the input file.

    Returns:
        The output file path of the compressed image.
    """
    # Extract filename and directory from the input path
    file_name = os.path.basename(input_path)  # e.g., "photo.jpg"
    original_directory = os.path.dirname(input_path)
    
    # Create a "compressed_images" subfolder in the same directory (if necessary)
    compressed_folder = os.path.join(original_directory, 'compressed_images')
    os.makedirs(compressed_folder, exist_ok=True)
    
    # Build the output filename (e.g., "photo_1080_square.jpg")
    file_base, _ = os.path.splitext(file_name)
    output_file_name = f"{file_base}_1080_square.jpg"
    output_path = os.path.join(compressed_folder, output_file_name)

    # Open, crop, resize, and save the image
    with Image.open(input_path) as img:
        width, height = img.size
        side = min(width, height)
        left   = (width - side) // 2
        top    = (height - side) // 2
        right  = left + side
        bottom = top  + side

        img_cropped = img.crop((left, top, right, bottom))
        img_resized = img_cropped.resize((1080, 1080), Image.LANCZOS)

        img_resized.save(output_path, "JPEG", quality=quality)
    
    return output_path

# ============================================================
# 1) Update CSV: local_path, title, description, and tags
# ============================================================


# Read the single-row CSV into a dictionary
with open(csv_file_path, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

if not rows:
    raise ValueError("No data found in product_information.csv")

row = rows[0]  # We assume only one row


print(f"Processing image at '{png_path}'")
# -----------------------------
# Update local_path from png_path
# -----------------------------


# -----------------------------
# Generate a Title
# -----------------------------
def generate_metadata_single_call(png_path: str):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a creative helpful assistant that generates product metadata for an e-commerce listing."
                "Please respond in valid JSON format with keys 'title', 'description', and 'tags' designed to enhance SEO."
                "Do not include any additional commentary."
            )
        },
        {
            "role": "user",
            "content": (
                "Create the following, with an emphasis on text to evoke the feeling of the work. Do not include the image file name."
                "Specifically consider popular tag names in the appropriate field below."
                f"Given an image at '{png_path}' to be used for a {prod_info}, please generate:\n"
                "- A short, catchy title that doesn't include the file name\n"
                "- A short product description that doesn't include the file name\n"
                "- A comma-separated list of approx. 12 relevant tags that don't include the file name\n\n"
                "Return them as JSON, e.g.:\n"
                '{\n'
                '  "title": "...",\n'
                '  "description": "...",\n'
                '  "tags": "..."\n'
                '}'
            )
        }
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o-2024-05-13",  # or whichever model you're using
        messages=messages,
        max_tokens=350
    )
    
    content = response.choices[0].message.content.strip()
    return content


metadata_json = generate_metadata_single_call(png_path)

parsed = json.loads(metadata_json)
row['title'] = parsed.get("title", "")
row['description'] = parsed.get("description", "")
row['tags'] = parsed.get("tags", "")
row['square'] = square

# Write the updated row back to the CSV
with open(csv_file_path, mode="w", encoding="utf-8", newline="") as f:
    fieldnames = list(row.keys())
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow(row)
    