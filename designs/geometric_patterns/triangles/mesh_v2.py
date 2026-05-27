#!/usr/bin/env python3

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Shapely for geometry
import shapely.geometry as geom
import shapely.ops as ops
from shapely.ops import unary_union

# Triangle for meshing
import triangle as tr

###############################################
# 1) YOUR FRACTAL PARAMETERS & DATA STRUCTURES
###############################################
iter_num = 675
prog_rate = np.radians(0.3)
progression = 'counterclockwise'
delta = 2/3

# These are from your snippet:
start = [
    [
        [0, 1/np.sqrt(3)],
        [-0.5, -0.5*(1/np.sqrt(3))],
        [0.5, -0.5*(1/np.sqrt(3))]
    ],
    [
        [(1/np.sqrt(3))*(np.sqrt(3)/2), -(1/np.sqrt(3))*1/2],
        [0, 1/np.sqrt(3)],
        [-0.5, -0.5*(1/np.sqrt(3))]
    ],
    [
        [0.25*delta, -1*(0.5*(1/np.sqrt(3)) + delta*(np.sqrt(3)/2))],
        [delta, 1/np.sqrt(3)],
        [-5/6, 0.5*(1/np.sqrt(3))]
    ]
]

rotation = [
    [[np.pi/3], [5*np.pi/3], [np.pi]],
    [[2*np.pi/3], [2*np.pi], [4*np.pi/3]],
    [[np.pi], [np.pi/3], [5*np.pi/3]]
]

sizes = [1, delta, delta**2]

# Data lists to hold fractal lines
data0 = []
data1 = []
data2 = []
data3 = []
data4 = []
data5 = []
data6 = []
data7 = []
data8 = []
data9 = []

############################################################
# 2) IMPORT YOUR STARTING FUNCTIONS (start_points, triangles)
############################################################
# Adjust the import path as needed for your project:
# from ScriptedStyles.Designs.Releases.June_2024.triangles.Code.Mult.funcs import start_points, triangles

# For demonstration, define placeholders:
def start_points(size, shift, rot):
    """
    Placeholder for your real start_points() function.
    Returns a list of 3 "centroids" with angles, etc.
    Adapt this to match your real logic.
    """
    # Just a naive example: shift the given "shift" and rotate by "rot"
    # real code would differ
    results = []
    for i in range(3):
        angle = rot + i * (2*np.pi/3)
        x = shift[0] + size * np.cos(angle)
        y = shift[1] + size * np.sin(angle)
        results.append((x, y, angle))
    return results

def triangles(centroid, theta, progression, size, iter_num, prog_rate):
    """
    Placeholder for your real triangles() fractal function.
    Returns a list-of-lists of (x,y) pairs (one sub-list per iteration).
    """
    fractal_data = []
    for i in range(iter_num):
        if progression == 'clockwise':
            angle = theta - i * prog_rate
        else:
            angle = theta + i * prog_rate
        
        # Just create a single equilateral triangle
        # real code would do your fractal logic
        pts = []
        for corner in range(3):
            corner_angle = angle + 2*np.pi*corner/3
            x = centroid[0] + size*np.cos(corner_angle)*(1 - 0.6*i/iter_num)
            y = centroid[1] + size*np.sin(corner_angle)*(1 - 0.6*i/iter_num)
            pts.append((x, y))
        # close
        pts.append(pts[0])
        fractal_data.append(pts)
    return fractal_data

###########################################################
# 3) BUILD YOUR FRACTAL DATA SETS (data0, data1, etc.)
###########################################################
# data0 is one special set:
data0 += [triangles(
    centroid=[0, 0],
    theta=-5*np.pi/6,
    progression=progression,
    size=1,
    iter_num=iter_num,
    prog_rate=prog_rate*0.8
)]

def assign_data(iter_num, prog_rate):
    for siz in range(1,4,1):
        for obj in range(3):
            # get 3 "start" positions
            parameters = start_points(sizes[siz-1], start[siz-1][obj], rotation[siz-1][obj][0])
            
            x_vals = [para[0] for para in parameters]
            y_vals = [para[1] for para in parameters]
            
            # e.g. data1, data2, ...
            dset_name = f"data{siz+3*obj}"
            globals()[dset_name] = []
            
            for tri in range(3):
                if siz == 2:
                    thetaa = -5*np.pi/6
                else:
                    thetaa = 5*np.pi/6
                
                # combine signs
                thetaaa = ((-1)**tri)*thetaa + parameters[tri][-1]
                
                # call triangles() with updated iteration
                iters_mod = int(iter_num + 0.75*(3 - siz)**1.005)
                
                new_data = triangles(
                    centroid=[x_vals[tri], y_vals[tri]],
                    theta=(( -1 )**tri)*thetaa,
                    size=sizes[siz-1]*delta,
                    iter_num=iters_mod,
                    prog_rate=prog_rate,
                    progression=progression
                )
                
                globals()[dset_name].append(new_data)
    return "data has been assigned."

assign_data(iter_num, prog_rate)

##################################################
# 4) PLOT FUNCTION FOR YOUR FRACTAL (LINES)
##################################################
def triang_plot(linewid=0.5):
    """
    Plots all your fractal line data sets on the current figure.
    """
    colormap = plt.get_cmap('cool')
    
    # Plot data0
    for i in range(iter_num):
        coords = data0[0][i]
        x, y = zip(*coords)
        plt.plot(
            x, y,
            color=colormap(np.sin(4*(2*np.pi)*i/iter_num)),
            linewidth=linewid
        )
    
    # Plot data1..data9
    for dset in range(1,10):
        for triang_idx in range(3):
            # each fractal
            fractal_list = globals()[f'data{dset}'][triang_idx]
            # we don't necessarily know how many iters each has
            # but let's assume they all have the same length
            local_iter = len(fractal_list)
            for i in range(local_iter):
                coords = fractal_list[i]
                x, y = zip(*coords)
                plt.plot(
                    x, y,
                    color=colormap(np.sin(4*(2*np.pi)*i/local_iter)),
                    linewidth=linewid
                )
    
    plt.axis('off')

#############################################################
# 5) CONVERT THE FRACTAL LINES INTO SHAPELY POLYGONS + UNION
#############################################################
def gather_fractal_polygons():
    """
    Convert each iteration's line-based triangle into a Shapely Polygon
    and unify them. Returns one big Polygon (or MultiPolygon).
    """
    from shapely.geometry import Polygon
    
    all_polys = []
    
    # data0
    for i in range(iter_num):
        coords = data0[0][i]
        poly = Polygon(coords)
        if not poly.is_valid:
            poly = poly.buffer(0)
        all_polys.append(poly)
    
    # data1..data9
    for dset in range(1,10):
        for triang_idx in range(3):
            fractal_list = globals()[f'data{dset}'][triang_idx]
            for coords in fractal_list:
                poly = Polygon(coords)
                if not poly.is_valid:
                    poly = poly.buffer(0)
                all_polys.append(poly)
    
    # Combine them all
    fractal_union = unary_union(all_polys)
    return fractal_union

###############################################################
# 6) MESH THE LEFTOVER SPACE AND FILL WITH SECOND FRACTAL PASS
###############################################################
def shapely_polygon_to_triangle_input(poly):
    """
    Convert a single Shapely Polygon (without holes) into the dictionary
    needed by triangle.triangulate(). If you have holes or a MultiPolygon,
    you'll need to adapt.
    """
    exterior_coords = list(poly.exterior.coords)
    vertices = []
    segments = []
    
    for i, (x, y) in enumerate(exterior_coords[:-1]):
        vertices.append([x, y])
        segments.append([i, i+1])
    # close loop
    if segments:
        segments[-1][1] = 0
    
    A = dict(vertices=np.array(vertices), segments=np.array(segments))
    return A

def fractal_fill_mesh(geometry, base_iter=675, prog_rate=np.radians(0.3)):
    """
    Triangulate the leftover polygon and apply a second fractal pass
    (opposite rotation, fewer iterations) inside each mesh triangle.

    """
    if geometry.is_empty:
        return
    

    # If it's a MultiPolygon, loop over each polygon
    if geometry.geom_type == 'MultiPolygon':
        for subpoly in geometry.geoms:
            fractal_fill_mesh(subpoly, base_iter, prog_rate)
        return
    

    # Convert leftover to triangle input
    # Otherwise, it's a single Polygon; mesh it
    mesh_input = shapely_polygon_to_triangle_input(geometry)
    if 'vertices' not in mesh_input or not mesh_input['vertices'].size:
        return
    
    
    # Triangulate
    mesh_result = tr.triangulate(mesh_input, 'pDq')  # add 'a0.01' etc. for finer mesh
    
    if 'triangles' not in mesh_result:
        return
    
    # We'll do a new fractal pass
    new_progression = 'clockwise'
    new_iter = base_iter // 3
    colormap = plt.get_cmap('cool')
    
    for tri_indices in mesh_result['triangles']:
        p0 = mesh_result['vertices'][tri_indices[0]]
        p1 = mesh_result['vertices'][tri_indices[1]]
        p2 = mesh_result['vertices'][tri_indices[2]]
        
        cx = np.mean([p0[0], p1[0], p2[0]])
        cy = np.mean([p0[1], p1[1], p2[1]])
        
        # approximate size from centroid to first corner
        size_est = np.sqrt((p0[0] - cx)**2 + (p0[1] - cy)**2)
        
        # call your fractal with opposite rotation
        data2 = triangles(
            centroid=[cx, cy],
            theta=0.0,
            progression=new_progression,
            size=size_est,
            iter_num=new_iter,
            prog_rate=prog_rate
        )
        
        # plot lines for the second fractal pass
        for i, coords in enumerate(data2):
            x, y = zip(*coords)
            color = colormap(np.sin(4*(2*np.pi)*i/new_iter))
            plt.plot(x, y, color=color, linewidth=0.5)

##################################################
# 7) MAIN SCRIPT
##################################################
def main():
    # 1) Create the figure
    plt.figure(figsize=(8,8))
    plt.style.use('dark_background')
    
    # 2) Plot the primary fractal
    triang_plot(linewid=0.5)
    
    # 3) Convert fractal lines to polygons & unify
    fractal_shape = gather_fractal_polygons()
    
    # 4) Create a bounding circle (center at 0,0 radius=2.5)
    bounding_circle = geom.Point(0,0).buffer(2.5, resolution=256)
    
    # 5) Subtract fractal shape from bounding shape to get leftover
    leftover = bounding_circle.difference(fractal_shape)
    
    # If leftover is MultiPolygon, you may need to loop over leftover.geoms
    # For simplicity, assume it's a single polygon or we unify them.
    if leftover.is_empty:
        print("No leftover area to mesh!")
    elif leftover.geom_type == 'Polygon':
        fractal_fill_mesh(leftover, base_iter=iter_num, prog_rate=prog_rate)
    elif leftover.geom_type == 'MultiPolygon':
        for poly in leftover.geoms:
            fractal_fill_mesh(poly, base_iter=iter_num, prog_rate=prog_rate)
    
    # 7) Finalize & save
    plt.axis('equal')
    plt.axis('off')
    plt.savefig('fractal_with_leftover_mesh.png', dpi=600, transparent=True)
    plt.show()

if __name__ == '__main__':
    main()
