#!/usr/bin/env python3

import numpy as np
import matplotlib
matplotlib.use('Agg')  # So we can save images without needing a display
import matplotlib.pyplot as plt

# Geometry libraries
import shapely.geometry as geom
import shapely.ops as ops
from shapely.ops import unary_union

# For mesh generation
import triangle as tr



###############################################
# 1) SIMPLIFIED FRACTAL FUNCTION (PLACEHOLDER)
###############################################
def triangles(centroid, theta, progression, size, iter_num, prog_rate):
    """
    A *simplified* fractal-like routine that returns a list of polygons
    (each polygon is a list of (x,y) points) for each iteration.
    
    In your real code, you'd replace this with your existing 'triangles()'
    function logic from funcs.py so that it matches your actual fractal.
    """
    fractal_data = []
    for i in range(iter_num):
        if progression == 'clockwise':
            angle = theta - i * prog_rate
        else:
            angle = theta + i * prog_rate
        
        # Example "shrink" formula
        scale = size * (1 - 0.6 * i / iter_num)
        
        pts = []
        for corner in range(3):
            corner_angle = angle + 2 * np.pi * corner / 3
            x = centroid[0] + scale * np.cos(corner_angle)
            y = centroid[1] + scale * np.sin(corner_angle)
            pts.append((x, y))
        # Close the triangle
        pts.append(pts[0])
        
        fractal_data.append(pts)
    return fractal_data

################################################
# 2) GENERATE THE BASE FRACTAL + COLLECT POLYGONS
################################################
def generate_base_fractal(iter_num=100, prog_rate=np.radians(0.3)):
    """
    Generates the main/base fractal shape. Returns:
      - a list of Shapely polygons (one per iteration)
      - the bounding union of all polygons (for convenience)
    """
    # Example: single call to fractal function
    base_data = triangles(
        centroid=[0, 0],
        theta=-5 * np.pi / 6,
        progression='counterclockwise',
        size=1.0,
        iter_num=iter_num,
        prog_rate=prog_rate
    )
    
    # Convert each iteration's points to a Shapely Polygon
    polys = []
    for iteration_pts in base_data:
        poly = geom.Polygon(iteration_pts)
        # If the iteration might produce invalid polygons, do poly.buffer(0)
        if not poly.is_valid:
            poly = poly.buffer(0)
        polys.append(poly)
    
    # Combine them into one shape
    union_poly = unary_union(polys)
    return polys, union_poly

######################################################
# 3) CREATE A BOUNDING SHAPE AND COMPUTE FREE SPACE
######################################################
def compute_available_area(base_union_poly):
    """
    Creates a bounding shape and subtracts the fractal union
    to get the "available" region.
    """
    # Example bounding shape: a circle of radius 2.0
    bounding_circle = geom.Point(0, 0).buffer(2.0, resolution=256)
    
    # Subtract the fractal shape from the bounding circle
    leftover_area = bounding_circle.difference(base_union_poly)
    
    # If leftover_area is MultiPolygon, it might have multiple parts.
    # For a simple example, we assume it's a single Polygon or you
    # handle multiple polygons below.
    
    return leftover_area

########################################################
# 4) CONVERT A SHAPELY POLYGON INTO 'triangle' DICTIONARY
########################################################
def shapely_polygon_to_triangle_input(poly):
    """
    Convert a single Shapely Polygon (no holes) into a dict
    suitable for 'triangle.triangulate'.
    
    If the polygon has holes or multiple parts, you'd adapt
    this to include 'holes' or handle each polygon ring.
    """
    # Exterior boundary
    exterior_coords = list(poly.exterior.coords)
    vertices = []
    segments = []
    for i, (x, y) in enumerate(exterior_coords[:-1]):
        vertices.append([x, y])
        segments.append([i, i+1])
    # Close the loop
    segments[-1][1] = 0
    
    A = dict(vertices=np.array(vertices), segments=np.array(segments))
    return A

###########################################################
# 5) MESH THE AVAILABLE AREA, THEN APPLY A SECOND FRACTAL
###########################################################
def fractal_fill_mesh(unoccupied_poly, base_iter=100, prog_rate=np.radians(0.3)):
    """
    1) Mesh the unoccupied polygon.
    2) For each resulting triangle, call a fractal with
       opposite rotation and fewer iterations.
    3) Plot on the current figure.
    """
    # Convert Shapely polygon -> triangle input
    mesh_input = shapely_polygon_to_triangle_input(unoccupied_poly)
    
    # Triangulate
    # 'p' = polygon, 'q' = quality mesh, 'D' = no refinement
    # Add e.g. 'a0.01' for max area if you want finer or coarser mesh
    mesh_result = tr.triangulate(mesh_input, 'pDq')
    
    # If no triangles produced, do nothing
    if 'triangles' not in mesh_result:
        return
    
    # Opposite direction
    new_progression = 'clockwise'
    # Fewer iterations
    new_iter = base_iter // 3
    
    colormap = plt.get_cmap('cool')
    
    # For each triangle in the mesh
    for tri_indices in mesh_result['triangles']:
        p0 = mesh_result['vertices'][tri_indices[0]]
        p1 = mesh_result['vertices'][tri_indices[1]]
        p2 = mesh_result['vertices'][tri_indices[2]]
        
        # Centroid of that mesh triangle
        cx = np.mean([p0[0], p1[0], p2[0]])
        cy = np.mean([p0[1], p1[1], p2[1]])
        
        # Estimate size
        corner0 = p0
        size_est = np.sqrt((corner0[0] - cx)**2 + (corner0[1] - cy)**2)
        
        # Example initial angle
        theta0 = 0.0
        
        # Call fractal again
        fractal_data = triangles(
            centroid=[cx, cy],
            theta=theta0,
            progression=new_progression,
            size=size_est,
            iter_num=new_iter,
            prog_rate=prog_rate
        )
        
        # Plot it
        for i, tri_pts_iter in enumerate(fractal_data):
            x, y = zip(*tri_pts_iter)
            color = colormap(np.sin(4 * (2*np.pi) * i / new_iter))
            plt.plot(x, y, color=color, linewidth=0.5)

##################################################
# 6) MAIN SCRIPT: PUT IT ALL TOGETHER
##################################################
def main():
    # 1) Generate the base fractal polygons
    base_polys, base_union = generate_base_fractal(
        iter_num=120,    # or 675 in your real code
        prog_rate=np.radians(0.3)
    )
    
    # 2) Compute leftover (unoccupied) area
    unoccupied_poly = compute_available_area(base_union)
    
    # 3) Plot everything
    plt.style.use('dark_background')
    fig, ax = plt.subplots()
    
    # Plot the base fractal polygons
    colormap = plt.get_cmap('cool')
    for poly_idx, poly in enumerate(base_polys):
        x, y = poly.exterior.xy
        color = colormap(np.sin(4 * (2*np.pi) * poly_idx / len(base_polys)))
        ax.fill(x, y, color=color, alpha=0.9, linewidth=0)
    
    # 4) Triangulate the leftover area & fractal-fill each triangle
    fractal_fill_mesh(
        unoccupied_poly,
        base_iter=120,  # or 675, etc.
        prog_rate=np.radians(0.3)
    )
    
    # Final formatting
    ax.axis('equal')
    ax.axis('off')
    
    # 5) Save & show
    plt.savefig('fractal_mesh_filled.png', dpi=600, transparent=True)
    plt.show()


if __name__ == '__main__':
    main()
