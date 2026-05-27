


import numpy as np


def scaled_sigmoid(input_val, domain, max_val, min_val):
    """
    Scaled sigmoid function for normalizing input values.
    
    Args:
        input_val (float): Input value to be normalized.
    
    Returns:
        float: Normalized value between min_val and max_val.
    """
    return min_val+(max_val-min_val)*(1 / (1 + np.exp((input_val*0.05-(domain/2))*0.05)))

def new_tri(theta, vertices, prog_rate, length):
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


def triangles(centroid, theta, progression, size, iter_num, prog_rate):
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
    
    initial_prog_rate=prog_rate
    
    data = np.zeros([iter_num, 4, 2])  # Adjusted to include the closing point for each triangle
    
    #the scale is the component of size that translates to the points 
    #creating a triangle of side length size
    
    scale=(1/np.sqrt(3))
    
    # Initial vertices calculation based on the provided centroid, size, and theta
    for i in range(iter_num):
        for j in range(3):
            angle = theta + j * np.pi * 2 / 3  # Equilateral triangle angles
            data[i, j] = [
                centroid[0] + np.cos(angle) * size*scale,
                centroid[1] + np.sin(angle) * size*scale
            ]
        data[i, 3] = data[i, 0]  # Closing the triangle loop
        
        prog_rate=scaled_sigmoid(i, iter_num, initial_prog_rate, 0.4)
        theta += prog_rate  # Adjust theta for the next triangle
        size = new_tri(theta, data[i], prog_rate, size)  # Adjust size for the next triangle
    

    
    return data

#finds start point for triangle pattern that I drew

def start_points(l_0, start, rotation):
    """
    find the points of the triangle pattern that I drew-equilateral triangles
    finding them by thinking about coordinate grid as having been rotated

    Args:
        theta (radians (float)): clockwise rotation of cartesian coordinate plane about z axis
        l_0 (float): length of prior triangle side
        start (list or array): start point (furthest left point), of iteration
        
        
        start is 0,0 in rotated space
    """
    theta=rotation

    #rotation matrix for clockwise theta progression
    #this function by default uses clockwise progresssion for the 
    #assignment of triangle positions 
    
    rot_matrix=np.array([[np.cos(theta), np.sin(theta)],[-np.sin(theta),np.cos(theta)]])
    inv_matrix=np.array([[np.cos(theta), -np.sin(theta)],[np.sin(theta),np.cos(theta)]])

    start_prime=np.dot(start, rot_matrix)

    delta=2/3
    centroids=[list(np.dot([start_prime[0]+0.5*(delta)*l_0, start_prime[1]+l_0*delta*((0.5/(np.sqrt(3))))],inv_matrix))+[0],
               list(np.dot([start_prime[0]+delta*l_0, start_prime[1]+l_0*delta*(1/np.sqrt(3))],inv_matrix))+[np.pi/3],
               list(np.dot([start_prime[0]+l_0,start_prime[1]+l_0*delta*((0.5/(np.sqrt(3))))],inv_matrix))+[0]]

    return centroids


