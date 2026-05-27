from funcs import sq_interval
import matplotlib.pyplot as plt
import numpy as np
# # of points

#use 9*9 grid for 4 points

grid_size=20
pts=15

lines=500

#make it only need two points, x0 and x1
pt_number=5

# points are 3,3 4,4 5,5 6,6

#for trying large numbers of points:

start_point=[]

arr=np.linspace(1,grid_size-1,pts)
for n in range(pts):
    start_point+=[[arr[n],arr[n]]]


frame=[0,grid_size,0,grid_size]



ypoint=[]
xpoint=[]
for p in range(pts):

    x_dat=[]
    y_dat=[]
    for l in range(lines):
        
        ypoints=[]
        xpoints=[]

        # #define variables for each line of each point

        slope=7-4*(l/lines)
        # dat=len_interval(pt_number,slope,start_point[p],grid_size)
        # len_int=dat[0]
        # x_naught=dat[1]
        # b=(slope*start_point[p][0]-start_point[p][1])

        # #assure each new line starts at y=0 by subtracting base y value from added points

        # y_scale=line(xpos=x_naught,slope=slope, b=b)

        data=sq_interval(pt_number,slope,start_point[p],frame)

        for i in range(2):

            ypoints+=[data[i][1]]
            xpoints+=[data[i][0]]

        y_dat+=[ypoints]
        x_dat+=[xpoints]
    
    ypoint+=[y_dat]
    xpoint+=[x_dat]


plt.style.use('dark_background')
colormap=plt.get_cmap('plasma')
plt.axis('off')


for p in range(pts):
    for l in range(lines):
        plt.plot(xpoint[p][l],ypoint[p][l], color=colormap(((l+p*50)**2/(2*pts*50)**2)+(1/6)), linewidth=0.5)



#ask chatgpt for code to check directory and see if the file Take1 alr exists so that I dont
#accidentally override other verisions
        
plt.savefig('Take12.png', dpi=1200)

plt.show()