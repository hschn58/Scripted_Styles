import cv2
import numpy as np

name='file'
ext='png'
# Load the image
image_path = f'{name}.{ext}'  # Update this to the path of your image
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Enhance contrast via Histogram Equalization
image_eq = cv2.equalizeHist(image)

# Apply adaptive thresholding to preserve details
adaptive_thresholded_image = cv2.adaptiveThreshold(image_eq, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                                   cv2.THRESH_BINARY, 11, 2)

# In case the writing is still white and the background is black, invert the image colors
# This step might not be necessary depending on your image, so adjust accordingly


final_image = cv2.bitwise_not(adaptive_thresholded_image)
#final_image=adaptive_thresholded_image
# Save the result
output_path = f'{name}_out.{ext}'  # Update this to where you want to save the modified image
cv2.imwrite(output_path, final_image)
# Optionally, display the image (for testing purposes)
# cv2.imshow('Enhanced and Thresholded Image', final_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

