
"""
Created on Tue Dec  7  2022

@author: schnieders scheibach

This program uses the finite differencing method to solve a 
second order flux boundary value problem.

*Phi(r(t)) crosses the 0.02% of its initial value threshold
for a tank radius of about 0.19820m.
"""

# Part A

import numpy as np

#Create loop to ensure valid user inputs
while True:
    nsys = int(input("Please enter the number of segments:"))
    if nsys <= 0:
        print("Please enter a positive integer.")
    else:
        break

while True:
    trad = float(input("Please enter a tank radius (in m):"))
    if trad <= 0.05:
        print("Please enter a radius greater than 0.05 m.")
    else:
        break
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
    
#Create the plot 
import matplotlib.pyplot as plt

plt.figure(1, figsize=[6.,6.])
plt.plot(np.linspace(0.05, trad, nsys),finite_diff(nsys, trad), linewidth=2)
plt.title("Neutron Flux at distance R", fontsize=16)
plt.ylabel("$\Phi(r)$",fontsize=13)
plt.xlabel("R", fontsize=13)

# Part B
plt.figure(2, figsize=[6.,6.])

#Loop over all 4 n values
#Create plot 
plt.plot(np.array([(0.1-0.05)/x for x in [16,32,64,128]]),np.array([finite_diff(x, 0.1)[-1] for x in [16,32,64,128]]), linewidth=2)
plt.ylabel("$\Phi(r_{t})$", fontsize=13)
plt.title("$\phi(r_{t})$ For Varying H", fontsize=16)
plt.xlabel("H size", fontsize=13)
plt.subplots_adjust(left=0.15)


#Part C:

N=25

#loop over 200 trials to ensure enough data is obtained
ydata=[]
xdata=[]
for x in range(200):
    dist = x/1000
    xdata+=[dist+0.05]
    var = finite_diff(N, trad=float(0.1+dist))[-1]
    ydata+=[var]

#create the plot 
plt.figure(3, figsize=[6.,6.])
plt.plot(xdata, ydata, linewidth=2)
plt.xlabel('Tank Radius', fontsize=13)
plt.ylabel('$\phi(r_{t})$', fontsize=13)
plt.title('$\phi(r_{t})$ at $r_{t}$', fontsize=16)
plt.subplots_adjust(left=0.15)
plt.show()
