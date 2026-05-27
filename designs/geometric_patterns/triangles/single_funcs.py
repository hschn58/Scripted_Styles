


import numpy as np


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

#finds start point for triangle pattern that I drew

#debug using jupyter just see which part is wrong-could be equations or rotation matrix or both
def start_points(theta, l_0, start):
    """
    find the points of the triangle pattern that I drew-equilateral triangles
    finding them by thinking about coordinate grid as having been rotated

    Args:
        theta (radians (float)): clockwise rotation of cartesian coordinate plane about z axis
        l_0 (float): length of prior triangle side
        start (list or array): start point (furthest left point with respect to the positive rotated x axis), of iteration

    
        returns the centroids of the next progression and the theta to rotate them
    """

    theta*=-1

    rot_matrix=np.array([[np.cos(theta), np.sin(theta)],[-np.sin(theta),np.cos(theta)]])

    start_prime=np.dot(start,rot_matrix)

    delta=2/3
    centroids=[list(np.dot([start_prime[0]+0.5*(delta)*l_0, start_prime[1]+(l_0-((2/(3*np.sqrt(3)))*l_0))],rot_matrix))+[0],
               list(np.dot([start_prime[0]+delta*l_0, start_prime[1]+(2/(3*np.sqrt(3)))*l_0],rot_matrix))+[np.pi/3],
               list(np.dot([start_prime[0]+l_0,start_prime[1]+(l_0-((2/(3*np.sqrt(3)))*l_0))],rot_matrix))+[0]]

    return centroids


