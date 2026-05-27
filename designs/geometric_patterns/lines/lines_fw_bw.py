from funcs import sq_interval, split_data
import numpy as np
import matplotlib.pyplot as plt

def plot_func(pts, lines, frame):

    
    """
    grid_size-int
    pts-int
    lines-int
    frame-list- tells program where it is plotting in the frame [xmin, xmax, ymin, ymax]
    """

    
    
    
    # # of points





    xmin=frame[0]
    xmax=frame[1]
    ymin=frame[2]
    ymax=frame[3]

    
    pts=pts

    lines=lines

    #make it only need two points, x0 and x1


    # points are 3,3 4,4 5,5 6,6

    #for trying large numbers of points:

    start_point=[]

    arr=np.linspace(1+xmin,(xmax-xmin)-1,pts)
    for n in range(pts):
        start_point+=[[arr[n],(ymax-ymin)/2 + ymin]]


    ypoint=[]
    xpoint=[]
    for p in range(pts):

        x_dat=[]
        y_dat=[]
        for l in range(lines):
            
            ypoints=[]
            xpoints=[]

            # #define variables for each line of each point

            slope=6-5*(l**2/lines**2)

            data=sq_interval(slope,start_point[p],frame)

            for i in range(2):

                ypoints+=[data[i][1]]
                xpoints+=[data[i][0]]

            y_dat+=[ypoints]
            x_dat+=[xpoints]
        
        ypoint+=[y_dat]
        xpoint+=[x_dat]



    #backward plotting

    data_tot=split_data(xpoint,ypoint,start_point,lines,pts)

    xdata1_pts=data_tot[0]
    ydata1_pts=data_tot[1]
    xdata2_pts=data_tot[2]
    ydata2_pts=data_tot[3]

    return [xdata1_pts,ydata1_pts,xdata2_pts,ydata2_pts]



frame=[0,10,0,10]
pts=10
lines=125


data=plot_func(pts,lines,frame)

xdata1_pts=data[0]
ydata1_pts=data[1]
xdata2_pts=data[2]
ydata2_pts=data[3]

figure=plt.figure(figsize=[10,10])
colormap=plt.get_cmap('plasma')
plt.axis('off')

#forward plotting:
for p in range(pts):
    for l in range(lines):
        plt.plot(xdata2_pts[p][l],ydata2_pts[p][l], color=colormap(((l+p*lines)**2/(pts*lines)**2)+(1/6)), linewidth=0.5)

#backward plotting:
for p in range(pts-1,-1,-1):
    for l in range(lines):
        plt.plot(xdata1_pts[p][l],ydata1_pts[p][l], color=colormap(((l+p*lines)**2/(pts*lines)**2)+(1/6)), linewidth=0.5)

# #plot bounding box


# points = [[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin]]

# # Closing the rectangle by connecting the last point to the first point
# points.append(points[0])

# x, y = zip(*points)  # Unzipping the points

# plt.plot(x, y, '-', linewidth=0.3, color='white')

# #ask chatgpt for code to check directory and see if the file Take1 alr exists so that I dont
# #accidentally override other verisions
        
# #plt.savefig('Take11.png', dpi=1200)

plt.show()

