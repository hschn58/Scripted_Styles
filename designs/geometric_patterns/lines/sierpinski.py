from funcs import plot_func_rev
import matplotlib.pyplot as plt



#debug by printing data and filtering for points whose slope != slope
##################
#########
#########
#########
#########
#########
#########
#########


pts=9
lines=200
gs=9

# (pts, lines, frame)

data_tot=[]
box_points=[]



start_pos=[[0,gs/2,0,gs/2],[gs/2,gs,gs/2,gs],[gs/2,gs*(3/4),0, gs*(1/4)], [0,gs*(1/4),gs/2,gs*(3/4)],[gs*(3/4),gs*(7/8),gs*(1/8),gs*(1/4)],[gs*(1/4),gs*(3/8),gs*(5/8) ,gs*(3/4)]]

# start_pos = [[gs/2,gs,gs/2,gs],[0,gs/2,0,gs/2],[gs/2,gs*(3/4),gs*(1/4), gs*(1/2)]]


num_iterations= len(start_pos)

for iteration in range(num_iterations):
    data_tot+=[plot_func_rev(pts,lines,start_pos[iteration])]
    box_points+=[[[start_pos[iteration][0], start_pos[iteration][2]], [start_pos[iteration][0], start_pos[iteration][3]], [start_pos[iteration][1], start_pos[iteration][3]], [start_pos[iteration][1], start_pos[iteration][2]]]]

plt.style.use('dark_background')
colormap=plt.get_cmap('plasma')


for graph in range(num_iterations):

    

    xdata1_pts=data_tot[graph][0]
    ydata1_pts=data_tot[graph][1]
    xdata2_pts=data_tot[graph][2]
    ydata2_pts=data_tot[graph][3]


    #forward plotting:
    for p in range(pts):
        for l in range(lines):

            if min(ydata2_pts[p][l]) < start_pos[graph][2]:
                continue

            plt.plot(xdata2_pts[p][l],ydata2_pts[p][l], color=colormap(((l+p*lines)**2/(pts*lines)**2)+(1/6)), linewidth=0.5)

    #backward plotting:
    for p in range(pts-1,-1,-1):
        for l in range(lines):

            if min(xdata1_pts[p][l]) < start_pos[graph][0]:
                continue

            plt.plot(xdata1_pts[p][l],ydata1_pts[p][l], color=colormap(((l+p*lines)**2/(pts*lines)**2)+(1/6)), linewidth=0.5)


    #plot bounding box
            
    points = box_points[graph]


    # Closing the rectangle by connecting the last point to the first point
    points.append(points[0])

    x, y = zip(*points)  # Unzipping the points

    plt.plot(x, y, '-', linewidth=0.3, color='white')

    #ask chatgpt for code to check directory and see if the file Take1 alr exists so that I dont
    #accidentally override other verisions
            
    plt.savefig('Error.png', dpi=1200)

    # plt.show()

plt.axis('off')
plt.show()