import matplotlib.pyplot as plt
import numpy as np
import argparse
import os
import matplotlib
matplotlib.use('AGG')

# # of points

fig = plt.figure(figsize=[10.,10])
dpi = 2400
grid_size=20
pts=14
lines=250

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--color', type=str, default='ocean', help='Particle mass')
parser.add_argument('--verity', type=bool, default=True, help='Particle mass')

args = parser.parse_args()

colormap = args.color
verity = args.verity


if verity == True:
    plt.style.use('dark_background')    
#use 9*9 grid for 4 points



# #make it only need two points, x0 and x1
# pt_number=5

# points are 3,3 4,4 5,5 6,6

#for trying large numbers of points:

start_point=[]

# arr=np.linspace(1,grid_size-1,pts)
# for n in range(pts):
#     start_point+=[[arr[n],arr[n]]]

arr=np.linspace(1,grid_size-1, pts)
for n in range(pts):
    start_point+=[[arr[n], grid_size*(1/4)+(n%2)*grid_size*(2/4)]]


def start_point_process(start_point):
    """
    fixes apparent gap in the generated image made between points

    Args:
        start_point (_type_): _description_

    Returns:
        _type_: _description_
    """
def start_point_process(start_point):
    """
    Fixes apparent gap in the generated image made between points.
    """
    length = len(start_point)
    delta = 0.8
    center = length // 2

    if length % 2 == 1:
        for i in range(center):
            start_point[i][0] *= (2 - delta)
            start_point[length - 1 - i][0] *= delta
    else:
        start_point[center - 1][0] *= ((2 - delta - 1) / 2 + 1)
        start_point[center][0] *= (1 - (1 - delta) / 2)
        for i in range(center - 1):
            start_point[i][0] *= (2 - delta)
            start_point[length - 1 - i][0] *= delta

    return start_point

delta = 1.01

start_point=[[(sublist[0] * delta)+grid_size*(1-delta),sublist[1]] for sublist in start_point]
# start_point=[[3,3],[4,4],[5,5],[6,6]]

def len_interval(slope, pt, gs):
    """
    returns the integer length value between points in the line and the first x position
    [distance,x0]

    Args:
        num_lpts (int): number of points that constitute the line
        slope (int): _description_
        pt (list): point in box
        gs (int): size of n*n box
    
    """
    #define box
    #x=0, x=9
    #y=0, y=9
 
    #scaled distances from boundary
    import math

    xl,xr,yb,yt= pt[0],-1*(pt[0]-gs),pt[1]/math.fabs(slope),(-1*(pt[1]-gs))/math.fabs(slope)

    #find intersection points:
    x0,y0,x1,y1=0,0,0,0

    if slope > 0:
        if min(xl,yb)==xl:
            x0=0
            y0=pt[1]+slope*(x0-pt[0])
        else:
            y0=0
            x0=pt[0]+(y0-pt[1])/slope
        
        if min(xr,yt)==xr:
            x1=gs
            y1=pt[1]+slope*(x1-pt[0])
        else:
            y1=gs
            x1=pt[0]+(y1-pt[1])/slope


    elif slope==0:
        y0=y1=pt[1]
        x0,x1=0,gs

    else:
        if min(xr,yb)==xr:
            x1=gs
            y1=pt[1]+slope*(x1-pt[0])
        else:
            y1=0
            x1=pt[0]+(y1-pt[1])/slope

        if min(xl,yt)==xl:
            x0=0
            y0=pt[1]+slope*(x0-pt[0])
        else:
            y0=gs
            x0=pt[0]+(y0-pt[1])/slope

    # # Define two points as numpy arrays
    # point0 = np.array([x0, y0])  # Replace x1 and y1 with actual coordinates
    # point1 = np.array([x1, y1])  # Replace x2 and y2 with actual coordinates

    # x=np.array([1,0])

    # # Calculate the x-axis distance change to evenly divide among input values

    # distance=np.dot(point1-point0,x)

    return [[x0,y0],[x1,y1]]

def line(xpos, slope, b):
    return slope*xpos+b




ypoint=[]
xpoint=[]

line_ind=[]
for p in range(pts):

    x_dat=[]
    y_dat=[]

    # lin=int(lines*(0.1+(p/pts)))
    # line_ind+=[lin]
    for l in range(lines):
        
        ypoints=[]
        xpoints=[]

        # #define variables for each line of each point

        slope=7-6*(l/lines)
        # dat=len_interval(pt_number,slope,start_point[p],grid_size)
        # len_int=dat[0]
        # x_naught=dat[1]
        # b=(slope*start_point[p][0]-start_point[p][1])

        # #assure each new line starts at y=0 by subtracting base y value from added points

        # y_scale=line(xpos=x_naught,slope=slope, b=b)

        data=len_interval(slope,start_point[p],grid_size)

        for i in range(2):

            ypoints+=[data[i][1]]
            xpoints+=[data[i][0]]

        y_dat+=[ypoints]
        x_dat+=[xpoints]
    
    ypoint+=[y_dat]
    xpoint+=[x_dat]

#fig=plt.figure(figsize=[10,10])





for p in range(pts):
    for l in range(lines):
        plt.plot(xpoint[p][l],ypoint[p][l], color=colormap(((l+p*50)**2/(2*pts*50)**2)+(1/6)), linewidth=0.75)

# #backward plotting:
# for p in range(pts-1,-1,-1):
#     for l in range(lines):
#         plt.plot(xdata1_pts[p][l],ydata1_pts[p][l], color=colormap(((l+p*lines)**2/(pts*lines)**2)+(1/6)), linewidth=0.5)

#plot bounding box

xmin, xmax = 0, grid_size
ymin, ymax = 0, grid_size

points = [[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin]]

# Closing the rectangle by connecting the last point to the first point
points.append(points[0])

x, y = zip(*points)  # Unzipping the points


white_hue=2-0.7

linecolor=(white_hue*50/255,white_hue*168/255,white_hue*157/255)

plt.plot(x, y, '-', linewidth=4, color=linecolor)

plt.axis('off')

#ask chatgpt for code to check directory and see if the file Take1 alr exists so that I dont
#accidentally override other verisions

# Get the current axis limits in plotting units

ax = plt.gca()
current_xlim = ax.get_xlim()
current_ylim = ax.get_ylim()

# print(f"Current x limits: {current_xlim}")
# print(f"Current y limits: {current_ylim}")

delta=0.97
ax.set_xlim(current_xlim[0]+delta, current_xlim[1]-delta)
ax.set_ylim(current_ylim[0]+delta, current_ylim[1]-delta)


from ScriptedStyles.Designs.Releases.ismethods.check import unique_filename
############################################################################################################

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
images_dir = os.path.join(parent_dir, 'images')

# Check if the folder exists; if not, create it.
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

# Create the filename in the images folder.
filename = unique_filename(os.path.join(images_dir, colormap + '_cool' + '.jpg'))

plt.savefig(filename, dpi=dpi, bbox_inches='tight', pad_inches=0)
plt.close()

import pandas as pd
df = pd.read_csv('product_information.csv')
df['local_path'].iloc[0] = filename
df.to_csv('product_information.csv', index=False)
