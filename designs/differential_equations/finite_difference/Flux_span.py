import matplotlib.pyplot as plt
import numpy as np
#number of trials

trials=100
trad=0.03
inc =1

#start w 3, do 10 trials, and increase by 5 each time

xdata=[]
ydata=[]
nseg=3



def finite_diff(nsys, trad):
    """
    

    Parameters
    ----------
    nsys : TYPE int
        This is the number of segments used
        for the finite difference method
    trad : TYPE float
        This is the outer tank radius 

    Returns
    -------
    soln : TYPE numpy array
        This is the solution vector describing 
        the neutron flux at every evaluation segment. 

    """
    #set numerical variables 
    srad = 0.05
    d = 1/(3*(2.20+345*(1-0.324)))
    a =2.2
    rad_points=np.linspace(srad,trad,nsys)
    h = ((trad-srad)/nsys)
    matr = np.zeros((nsys, nsys))

    #Apply second order finite difference for variable coefficients

    for i in range(1,nsys-1):
        matr[i,i-1]=-1*d*rad_points[i-1]/h**2           #  M_(i,i-1)
        matr[i,i]=2*d*rad_points[i]/h**2+rad_points[i]*a        #  M_(i,i)
        matr[i,i+1]=-1*d*rad_points[i+1]/h**2

    
    #Apply Boundary Conditions

    matr[0,0]=1

    #1st order one-sided difference for the second boundary condition

    matr[-1,-2]=(d/h)*(-1)
    matr[-1,-1]=(d/h)+0.5

    
    #create rhs vector

    rhs = np.zeros(nsys)
    rhs[0]=1
    
    soln = np.linalg.solve(matr, rhs)
    return soln





for trial in range(trials):
    xdata+=[np.linspace(0,0.03,nseg)]
    ydata+=[finite_diff(nseg, trad)]
    nseg+=inc

colormap=plt.get_cmap('plasma')

for trial in range(trials):
    plt.plot(xdata[trial], ydata[trial],color=colormap(trial/trials))

plt.show()
