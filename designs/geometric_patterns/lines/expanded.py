import numpy as np 
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('AGG')

eqn=lambda x,t,k=1:(1/(4*np.pi*k*t))*np.exp(-x**2/(4*k*t))

#pnum
pnum=300

rang=7
x_dat=np.linspace(-rang,rang,pnum)

t_dat=np.logspace(np.log(1),np.log(3), 777)

# colors=['r','g','b']
# linestyles=['solid','dashed','dotted']

plt.figure()

colormap=plt.get_cmap('cool')

for i in range(len(t_dat)):
    y_dat=eqn(x_dat,t_dat[i])
    plt.plot(x_dat,y_dat, color=colormap(i/len(t_dat)), linewidth=0.5)

#plt.yscale('log')


# plt.xlabel('Relative Distance From '+r'$\delta(\vec{x}=\vec{x_{0}})$', fontsize=14)
# plt.ylabel('Relative Thermal Energy Density', fontsize=14)
plt.axis('off')
plt.savefig('plot_q1_expanded.png', dpi=1200)

plt.show()

