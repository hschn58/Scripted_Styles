

#functions for lines art. 
"""
The changeable parameters are:

start point array
padding for start point arry
number of points
number of lines 
color scheme
plotting frame (so that multiple sets can be displayed in the same figure)
"""






def sq_interval(slope, pt, frame):
    """
    returns the integer length value between points in the line and the first x position
    [distance,x0]

    Args:
        num_lpts (int): number of points that constitute the line
        slope (int): _description_
        pt (list): point in box
        gs (int): size of n*n box
    
    """
    
    xmin=frame[0]
    xmax=frame[1]
    ymin=frame[2]
    ymax=frame[3]
    
    
    #define box
    #x=0, x=9
    #y=0, y=9
 
    #scaled distances from boundary
    import math

    xl,xr,yb,yt= pt[0]-xmin,-1*(pt[0]-xmax),((pt[1]-ymin)/math.fabs(slope)),(-1*(pt[1]-ymax))/math.fabs(slope)

    #find intersection points:
    # x0,y0,x1,y1=0,0,0,0

    if slope > 0:
        if min(xl,yb)==xl:
            x0=xmin
            y0=pt[1]+slope*(x0-pt[0])
        else:
            y0=ymin
            x0=pt[0]+(y0-pt[1])/slope
        
        if min(xr,yt)==xr:
            x1=xmax
            y1=pt[1]+slope*(x1-pt[0])
        else:
            y1=ymax
            x1=pt[0]+(y1-pt[1])/slope


    elif slope==0:
        y0=y1=pt[1]
        x0,x1=xmin,xmax

    else:
        if min(xr,yb)==xr:
            x1=xmax
            y1=pt[1]+slope*(x1-pt[0])
        else:
            y1=ymin
            x1=pt[0]+(y1-pt[1])/slope

        if min(xl,yt)==xl:
            x0=xmin
            y0=pt[1]+slope*(x0-pt[0])
        else:
            y0=ymax
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


def split_data(xdata,ydata, split_axis, line_num, pt_num):
    """ splits the nth dataset contained in xdata, ydata along the nth
        split_axis point
    
    xdata1_pts,ydata1_pts is the bottom half, xdata2_pts,ydata2_pts is the top half

    Args:
        xdata (list): _description_
        ydata (list): _description_
        split_axis (list): start_points
        line_num (int): number of lines per point
        pts_num (int): number of points at which lines are made

    Returns:
        _type_: _description_
    """
    xdata1_pts=[]
    ydata1_pts=[]
    xdata2_pts=[]
    ydata2_pts=[]

    
    point_num=len(split_axis)


    for point in range(point_num):

        pcurrx= split_axis[point][0] 
        pcurry= split_axis[point][1]

        
        xdata_line1=[]
        ydata_line1=[]
        xdata_line2=[]
        ydata_line2=[]

        for line in range(line_num):

            xdata_pt1=[]
            ydata_pt1=[]
            xdata_pt2=[]
            ydata_pt2=[]
            
            pt=0
            while True:
                if pt==2:
                    break
                yvar=ydata[point][line][pt]
                xvar=xdata[point][line][pt]
                

                if yvar<=pcurry:
                    ydata_pt1+=[yvar]
                    xdata_pt1+=[xvar]
                    pt+=1
                else:
                    ydata_pt2+=[ydata[point][line][pt]]
                    xdata_pt2+=[xdata[point][line][pt]]
                    pt+=1 
                
            if ydata_pt1[-1] != pcurry:
                ydata_pt1+=[pcurry]
            if ydata_pt2[0] != pcurry:
                ydata_pt2=[pcurry]+ydata_pt2
            if xdata_pt1[-1] != pcurrx:
                xdata_pt1+=[pcurrx]
            if xdata_pt2[0] != pcurrx:
                xdata_pt2=[pcurrx]+xdata_pt2
                              

            xdata_line1+=[xdata_pt1]
            ydata_line1+=[ydata_pt1]
            xdata_line2+=[xdata_pt2]
            ydata_line2+=[ydata_pt2]
            
                        
        xdata1_pts+=[xdata_line1]
        ydata1_pts+=[ydata_line1]
        xdata2_pts+=[xdata_line2]
        ydata2_pts+=[ydata_line2]


    return [xdata1_pts,ydata1_pts,xdata2_pts,ydata2_pts]

#get the two sets based on y. If y[i] <split_axis[point], then x[i],y[i] are below, go to x2,y2
def plot_func(pts, lines, frame):

    
    """
    grid_size-int
    pts-int
    lines-int
    frame-list- tells program where it is plotting in the frame [xmin, xmax, ymin, ymax]
    """

    
    
    
    # # of points
    import numpy as np





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

    padding=(xmax-xmin)*0.1
    
    arr=np.linspace(padding+xmin,xmax-padding,pts)
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

            slope=6-5.75*(l**2/lines**2)

            data=sq_interval(slope,start_point[p],frame)

            for i in range(2):
                

                
                ypoints+=[data[i][1]]
                xpoints+=[data[i][0]]
                
            y_dat+=[ypoints]
            x_dat+=[xpoints]
        
        ypoint+=[y_dat]
        xpoint+=[x_dat]


    return [xpoint,ypoint]


def plot_func_rev(pts, lines, frame):

    
    """
    grid_size-int
    pts-int
    lines-int
    frame-list- tells program where it is plotting in the frame [xmin, xmax, ymin, ymax]
    """

    
    
    
    # # of points
    import numpy as np





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

    padding=(xmax-xmin)*0.1
    
    arr=np.linspace(padding+xmin,xmax-padding,pts)
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

            slope=6-5.75*(l**2/lines**2)

            data=sq_interval(slope,start_point[p],frame)

            for i in range(2):
                

                
                ypoints+=[data[i][1]]
                xpoints+=[data[i][0]]
                
            y_dat+=[ypoints]
            x_dat+=[xpoints]
        
        ypoint+=[y_dat]
        xpoint+=[x_dat]



    #backward plotting

    data_tot=split_data(xpoint,ypoint,start_point,lines,2)

    xdata1_pts=data_tot[0]
    ydata1_pts=data_tot[1]
    xdata2_pts=data_tot[2]
    ydata2_pts=data_tot[3]

    return [xdata1_pts,ydata1_pts,xdata2_pts,ydata2_pts]


# from sympy import Symbol
# from sympy.solvers import solve
# import numpy as np
# x = Symbol('x')

# #uses sympy, could be useful if I ever did more complex shapes

# def sq_interval_2(slope, pt, frame):

#     xmin=frame[0]
#     xmax=frame[1]
#     ymin=frame[2]
#     ymax=frame[3]
    
#     b=solve(slope*pt[0]-pt[1]+x,x)[0]
    
#     #find intersection points
#     points=np.zeros([2,2])
    
#     #bottom line
#     soln=solve(slope*x+b-ymin,x)[0]
#     if soln<=xmax and soln>=xmin:
#         points[0,0]=soln
#         points[0,1]=ymin
    
    
#     #right side
#     soln=solve(slope*xmax+b-x,x)[0]
#     if soln<=ymax and soln>=ymin:
        
#         slot=get_slot(points)
            
#         points[slot[0,0],slot[0,1]]=xmax
#         points[slot[1,0],slot[1,1]]=soln
    
    
#     #left side
#     soln=solve(slope*xmin+b-x,x)[0]
#     if soln<=ymax and soln>=ymin:
        
#         slot=get_slot(points)
            
#         points[slot[0,0],slot[0,1]]=xmin
#         points[slot[1,0],slot[1,1]]=soln
    
    
#     #top side
#     soln=solve(slope*x+b-ymax,x)[0]
#     if soln<=xmax and soln>=xmin:
        
#         slot=get_slot(points)
            
#         points[slot[0,0],slot[0,1]]=soln
#         points[slot[1,0],slot[1,1]]=ymax
    

#     return points