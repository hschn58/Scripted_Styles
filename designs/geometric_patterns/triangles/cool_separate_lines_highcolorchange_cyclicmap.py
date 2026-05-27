"""

Generates a recursive “triangle weave” on a dark background: starting from an initial equilateral
triangle, the script iteratively plots edge-connected child triangles at three scales (1, 2/3, and (2/3)²),
rotating counterclockwise by a fixed rate. Lines are colored with the reversed Turbo colormap to create a 
radial gradient as iterations progress, producing a dense geometric lattice with no axes or fill.

This script draws a fractal-like lattice of equilateral triangles on a dark background. It seeds a central
parent triangle and then, for each iteration, spawns three child trajectories at three size tiers—large 
(indices 1/4/7), medium (2/5/8), and small (3/6/9)—using precomputed start points and rotations from start_points(...) 
and vertex paths from triangles(...). The orientation advances counterclockwise by a constant angular step (prog_rate), 
while scale decreases by delta = 2/3 per tier.

To display the image on-screen immediately, remove "matplotlib.use('AGG')". However, this is added to prevent aliasing artifacts.
The image looks substantially better when rendered with AGG and viewed after being saved locally. 

"""



from funcs_triang_separate import start_points, triangles
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('AGG')   
# 1) move this ABOVE any figure creation

import numpy as np

#largest triangles data: 1,4,7
#middle triangles data: 2,5,8
#smallest triangles data: 3,6,9

iter_num=250
prog_rate=np.radians(0.80)
progression='counterclockwise'
delta=2/3
maxx=0.92

start=[[[0,1/np.sqrt(3)],[-0.5, -0.5*(1/np.sqrt(3))],[0.5, -0.5*(1/np.sqrt(3))]],[[(1/np.sqrt(3))*(np.sqrt(3)/2),-(1/np.sqrt(3))*1/2],[0, 1/np.sqrt(3)],[-0.5,-0.5*(1/np.sqrt(3))]], [[0.25*delta,-1*(0.5*(1/np.sqrt(3))+delta*(np.sqrt(3)/2))],[delta, 1/np.sqrt(3)],[-5/6, 0.5*(1/np.sqrt(3))]]]
rotation=[[[np.pi/3],[5*np.pi/3], [np.pi]], [[2*np.pi/3],[2*np.pi],[4*np.pi/3]],[[np.pi],[np.pi/3],[5*np.pi/3]]]
sizes=[1,delta,delta**2]

data0=[]
data1=[]
data2=[]
data3=[]
data4=[]
data5=[]
data6=[]
data7=[]
data8=[]
data9=[]


data0+=[triangles(centroid=[0,0], theta=-5*np.pi/6, progression=progression, size=1, iter_num=iter_num, prog_rate=prog_rate*0.8)]


def assign_data(iter_num, prog_rate):

    for siz in range(1,4,1):
        for obj in range(3):

            
            parameters=start_points(sizes[siz-1],start[siz-1][obj],rotation[siz-1][obj][0])
            
            x=[para[0] for para in parameters]
            y=[para[1] for para in parameters]
            
            dset=siz+3*obj
            globals()[f'data{dset}']=[]
            
            for tri in range(3):
                    
                if siz==2:
                    thetaa=-5*np.pi/6
                    
                else:
                    thetaa=5*np.pi/6
                    
                thetaaa=((-1)**tri)*thetaa+parameters[tri][-1]

                if dset == 1 or dset == 4 or dset == 7:
                    scale=1
                elif dset == 2 or dset == 5 or dset == 8:
                    scale=2
                else:
                    scale=3
            
                
                globals()[f'data{siz+3*obj}']+=[triangles(centroid=[x[tri], y[tri]], theta=((-1)**tri)*thetaa, size=sizes[siz-1]*delta, iter_num=int(iter_num+0.75*(3-siz)**1.005), prog_rate=prog_rate, progression=progression)]

    return "data has been assigned."

assign_data(iter_num, prog_rate)       


colormap = plt.get_cmap('turbo_r')

fig=plt.figure(figsize=(10,10))
plt.style.use('dark_background')
    
def triang_plot(linewid):

    import matplotlib
    
    
    global vert1,  vert2, vert3

    vert1=[]
    vert2=[]
    vert3=[]

    for i in range(iter_num):
        x, y = zip(*data0[0][i])

        vert1.append((x[0],y[0]))
        vert2.append((x[1],y[1]))
        vert3.append((x[2],y[2]))


        plt.plot(x, y, color=colormap(maxx-(0.0055-0.0005*((1/((0.75)+1))))*i),linewidth=linewid)
    
    # for vert in range(3):
    #             xs, ys = zip(*globals()[f'vert{vert+1}'])
    #             plt.plot(xs,ys,color='#FFA500',linewidth=linewid*delta**0.66)
        
        
    for dset in range(1,10,1):
        
        if dset == 1 or dset == 4 or dset == 7:
            scale=1
        elif dset == 2 or dset == 5 or dset == 8:
            scale=2
        else:
            scale=3

        for triang in range(3):

            vert1=[]
            vert2=[]
            vert3=[]
            for i in range(iter_num):
                
                x, y = zip(*globals()[f'data{dset}'][triang][i])
                
                vert1.append((x[0],y[0]))
                vert2.append((x[1],y[1]))
                vert3.append((x[2],y[2]))

                #increasing the contrast of the colormap (applying to all relevant terms)
                plt.plot(x, y,color=colormap((maxx+0.02-0.055*triang-(0.0055-0.0005*((1/((scale)+1))))*i-0.15*scale)),linewidth=linewid*delta**scale)

            # for vert in range(3):
            #     xs, ys = zip(*globals()[f'vert{vert+1}'])
            #     plt.plot(xs,ys,color='#FFA500',linewidth=linewid*delta**scale)


                
                
    plt.axis('off')
    return "Plotting completed"
        

from matplotlib.colors import Normalize

triang_plot(2/3)

# fig=plt.gcf()

# fig.canvas.draw()
# image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
# image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

# # Convert the image to RGBA
# rgba_image = np.dstack((image, np.ones(image.shape[:2], dtype='uint8') * 255))

# # Calculate the alpha values based on the function sin((x^2 + y^2))
# height, width = rgba_image.shape[:2]
# x = np.linspace(-1, 1, width)
# y = np.linspace(-1, 1, height)
# X, Y = np.meshgrid(x, y)
# distance_squared = X**2 + Y**2
# alpha = np.sin(distance_squared)

# # Normalize alpha values to 0-255 and apply to the image
# norm = Normalize(vmin=-1, vmax=1)
# alpha_normalized = norm(alpha) * 255
# rgba_image[:, :, 3] = alpha_normalized.astype('uint8')

# # Display the modified image
# plt.imshow(rgba_image)
# plt.axis('off')


plt.savefig('./Desktop/cool_separate_lines_highcolorchange_cyclicmap.png', dpi=1200, bbox_inches='tight', pad_inches=0)
plt.show()



