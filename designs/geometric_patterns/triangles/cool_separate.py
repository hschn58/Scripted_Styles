from funcs_triang_separate import start_points, triangles
import matplotlib.pyplot as plt
import numpy as np

#largest triangles data: 1,4,7
#middle triangles data: 2,5,8
#smallest triangles data: 3,6,9

iter_num=250
prog_rate=np.radians(0.95)
progression='counterclockwise'
delta=2/3


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


colormap = plt.get_cmap('cool')
    
def triang_plot(linewid):

    import matplotlib
    matplotlib.use('AGG')
    plt.style.use('dark_background')
    
    
    for i in range(iter_num):
        x, y = zip(*data0[0][i])
        plt.plot(x, y, color=colormap(0.85-(0.00105-0.0005*((1/((0.75)+1))))*i),linewidth=linewid)
        
        
    for dset in range(1,10,1):
        
        if dset == 1 or dset == 4 or dset == 7:
            scale=1
        elif dset == 2 or dset == 5 or dset == 8:
            scale=2
        else:
            scale=3

        
        for triang in range(3):
            for i in range(iter_num):
                
                x, y = zip(*globals()[f'data{dset}'][triang][i])

                #increasing the contrast of the colormap (applying to all relevant terms)
                plt.plot(x, y,color=colormap((0.895-0.055*triang-(0.00105-0.0005*((1/((scale)+1))))*i-0.1*scale)),linewidth=linewid*delta**scale)
                
                
    plt.axis('off')
    return "Plotting completed"
        
    
triang_plot(2/3)
plt.savefig('cool_separate3.png', transparent=True, dpi=1200)