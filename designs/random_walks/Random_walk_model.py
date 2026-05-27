from func import get_iter
import matplotlib.pyplot as plt
import numpy as np


rang = 100000
prob=0.5
num=1000

data=[]

for n in range(num):
    data+=[get_iter(rang,prob+(n/num),n)]

fig=plt.figure()

x_vals=np.linspace(1,rang, rang)

colormap=plt.get_cmap('plasma')


y_vals=[]
for j in range(num):
    final_data=np.zeros(rang)
    for x in range(rang-1):
        final_data[x+1]=data[j][x]+final_data[x]
    y_vals+=[final_data]

for n in range(num):
    plt.plot(x_vals,y_vals[n], color=colormap(n/num))

plt.axis('off')


plt.subplots_adjust(left=0.15)

plt.show()