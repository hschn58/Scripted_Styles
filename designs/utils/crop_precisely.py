from PIL import Image

def crop_to_square(image_path, output_path):
    """
    Crops the image to a square centered on the image.
    
    :param image_path: Path to the input image.
    :param output_path: Path to save the cropped image.
    """
    image = Image.open(image_path)
    width, height = image.size
    
    # Determine the size of the square crop
    new_side = min(width, height)
    
    # Calculate the coordinates to crop the image to the center
    left = (width - new_side) // 2
    top = (height - new_side) // 2
    right = left + new_side
    bottom = top + new_side
    
    # Perform the crop
    cropped_image = image.crop((left, top, right, bottom))
    cropped_image.save(output_path)
    print(f"Cropped image saved to {output_path}")

def crop_to_twice_length_as_height(image_path, output_path):
    """
    Crops the image to dimensions where the length is twice as large as the height.
    The crop is centered on the image.
    
    :param image_path: Path to the input image.
    :param output_path: Path to save the cropped image.
    """
    image = Image.open(image_path)
    width, height = image.size
    
    # Determine the size of the crop
    new_height = min(height, width // 2)
    new_width = new_height * 2
    
    # Calculate the coordinates to crop the image to the center
    left = (width - new_width) // 2
    top = (height - new_height) // 2
    right = left + new_width
    bottom = top + new_height
    
    # Perform the crop
    cropped_image = image.crop((left, top, right, bottom))
    cropped_image.save(output_path)
    print(f"Cropped image saved to {output_path}")



if __name__ == "__main__":
    path='spicy_big.jpg'
    crop_to_square(path, path)

