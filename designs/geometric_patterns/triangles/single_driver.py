import matplotlib.pyplot as plt
import numpy as np

import matplotlib
matplotlib.use('AGG')

def new_start(theta, vertices, prog_rate, length):
    """
    Calculates the new length for the next triangle based on the current orientation and progression rate.
    
    Args:
        theta (float): Current orientation of the triangle in radians.
        vertices (list): Vertices of the current triangle.
        prog_rate (float): Progression rate in radians.
        length (float): Side length of the current triangle.
    
    Returns:
        float: New length for the next triangle.
    """
    # Assuming the function's purpose is to adjust the triangle size based on rotation,
    # this implementation will be simplified to focus on adjusting the length directly.
    
    # For simplicity, let's assume each new triangle is scaled down by a factor related to prog_rate
    # This is a placeholder for actual logic which might involve complex calculations
    A=2*(1-0.75*(1/np.sin(prog_rate))**2)
    scale_factor = (np.sqrt(3)/(2*np.sin(prog_rate)))*(1-(A/(-1*np.sqrt(1-2*A)+A+1)))  # Simplified scaling factor
    new_length = length * scale_factor
    
    return new_length

def triangle(centroid, theta, progression, size, iter_num, prog_rate):
    """
    Generates data for a sequence of triangles, each rotated and possibly resized based on the progression rate.
    
    Args:
        centroid (list): Centroid of the initial triangle.
        theta (float): Orientation of the initial triangle in radians.
        progression (str): 'clockwise' or 'counterclockwise' progression.
        size (float): Side length of the initial triangle.
        iter_num (int): Number of triangles to generate.
        prog_rate (float): Rotation increment for each triangle in radians.
    
    Returns:
        np.array: Array containing vertices for all triangles.
    """
    if progression == 'clockwise':
        prog_rate = -prog_rate
    
    data = np.zeros([iter_num, 4, 2])  # Adjusted to include the closing point for each triangle
    
    # Initial vertices calculation based on the provided centroid, size, and theta
    for i in range(iter_num):
        for j in range(3):
            angle = theta + j * np.pi * 2 / 3  # Equilateral triangle angles
            data[i, j] = [
                centroid[0] + np.cos(angle) * size,
                centroid[1] + np.sin(angle) * size
            ]
        data[i, 3] = data[i, 0]  # Closing the triangle loop
        
        theta += prog_rate  # Adjust theta for the next triangle
        size = new_start(theta, data[i], prog_rate, size)  # Adjust size for the next triangle
    
    return data

# Example usage
centroid = [0, 0]
theta = -5*np.pi/6 # Starting orientation
progression = 'counterclockwise'
size = 1
prog_rate = np.radians(0.75)  # Progression rate in radians
iter_num = 200  # Reduced for simplicity



data1 = triangle(centroid, theta, progression, size, iter_num, prog_rate)

# Plotting
plt.figure(figsize=[7.,6.])

colormap = plt.get_cmap('plasma')

for i in range(iter_num):
    x, y = zip(*data1[i])
    plt.plot(x, y, color=colormap(i**(0.55) / iter_num**(0.55)))

plt.axis('off')

plt.savefig('Figure3.png',dpi=300)
plt.show()

