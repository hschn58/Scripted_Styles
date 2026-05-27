from funcs import split_data
import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
# # of points
dpi = 2400
fig=plt.figure(figsize=[10.,10])

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--color', type=str, default='ocean', help='Particle mass')
parser.add_argument('--verity', type=int, default=True, help='Particle mass')



args = parser.parse_args()

colormap = args.color
verity = args.verity


import matplotlib
matplotlib.use('AGG')

#use 9*9 grid for 4 points

grid_size=20
pts=7
color_power=2

lines=250

# #make it only need two points, x0 and x1
# pt_number=5

# points are 3,3 4,4 5,5 6,6

#for trying large numbers of points:

start_point=[]

# arr=np.linspace(1,grid_size-1,pts)
# for n in range(pts):
#     start_point+=[[arr[n],arr[n]]]

arr=np.linspace(1,grid_size-1,pts)
for n in range(pts):
    start_point+=[[arr[n], grid_size*(1/4)+1*grid_size*(1/4)]]

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



xpointb=[]
ypointb=[]

for b in range(2):

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
            
            # if b==0:
            #     if p>list(range(pts))[int(pts/2)]:
            #         slope_form=(7-6*(1-l/lines))*(-1)**b

            # if b==1:
            #     if p<list(range(pts))[int(pts/2)]:
            #         slope_form=(7-6*(1-l/lines))*(-1)**b

            slope=(7-6*(l/lines))*(-1)**b
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
    xpointb+=[xpoint]
    ypointb+=[ypoint]   



#plt.style.use('dark_background')





if verity == True:
    plt.style.use('dark_background')
plt.axis('off')


# print('ive made it here')

data_totb1=split_data(xpointb[0],ypointb[0],start_point,lines,pts)

# print("\n")
# print("\n")
# print("\n")

# print(ypointb[1])

# print("\n")
# print("\n")
# print("\n")

data_totb2=split_data(xpointb[1],ypointb[1],start_point,lines,pts)
# print('ive made it here2')



xdata1_ptsb1=data_totb1[0]
ydata1_ptsb1=data_totb1[1]
xdata2_ptsb1=data_totb1[2]
ydata2_ptsb1=data_totb1[3]

xdata1_ptsb2=data_totb2[0]
ydata1_ptsb2=data_totb2[1]
xdata2_ptsb2=data_totb2[2]
ydata2_ptsb2=data_totb2[3]


#plot the bottom


colormap1=plt.get_cmap(colormap)
colormap2=plt.get_cmap(colormap + '_r')

depth=1
bias=0.35
lenght=1.2

# def abs_color_func(l,p,lines,pts,rangee,center):
#     #max =center+range
#     #min =center-range
    
    
    
    
color_func=lambda l,p,lines,pts:(((l+p*lines)-(lines*pts/2))**color_power/(depth*(pts*lines/2)**color_power))/2+bias

color_func2=lambda l,p,pts:(((l+p*50)**2/(2*pts*50)**2))

#plot bottom
# #b2 needs to be plotted in reverse order
# xdata1_ptsb2_r=[pt[::-1] for pt in xdata1_ptsb2[::-1]]
# ydata1_ptsb2_r=[pt[::-1] for pt in ydata1_ptsb2[::-1]]

for l in range(lines):
    
    
#for top and bottom, order is reversed for one of them (pts[-1] is plotted at pts[0]) for desired effect.

    
    #bottom
    for p in range(pts):
        
        #print(f"color_func2 is {color_func2(l,p,lines,pts)} when 1={l},p={p}.")
        #blue
        
        plt.plot(xdata1_ptsb1[p][l],ydata1_ptsb1[p][l], color=colormap1(color_func2(l,pts-p-1,pts)), linewidth=0.5)
        
        #red
        plt.plot(xdata1_ptsb2[p][l],ydata1_ptsb2[p][l], color=colormap2(color_func2(l,pts-p-1,pts)), linewidth=0.5)
        
    #top
    for p in range(pts):
    
        #blue
        plt.plot(xdata2_ptsb1[p][l],ydata2_ptsb1[p][l], color=colormap1(color_func2(l,p,pts)), linewidth=0.5)
        
        #red
        plt.plot(xdata2_ptsb2[p][l],ydata2_ptsb2[p][l], color=colormap2(color_func2(l,p,pts)), linewidth=0.5)
   
        
          
# #backward plotting:
# for p in range(pts-1,-1,-1):
#     for l in range(lines):
#         plt.plot(xdata1_pts[p][l],ydata1_pts[p][l], color=colormap(((l+p*lines)**2/(pts*lines)**2)+(1/6)), linewidth=0.5)

#plot bounding box

# xmin, xmax = 0, grid_size
# ymin, ymax = 0, grid_size

# points = [[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin]]

# # Closing the rectangle by connecting the last point to the first point
# points.append(points[0])

# x, y = zip(*points)  # Unzipping the points

# plt.plot(x, y, '-', linewidth=0.3, color='white')
        

#ask chatgpt for code to check directory and see if the file Take1 alr exists so that I dont
#accidentally override other verisions


ax = plt.gca()
ax.set_xlim(0.0, grid_size)
ax.set_ylim(grid_size, 0.0)
ax.set_aspect('equal', adjustable='box')

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
#plt.show()