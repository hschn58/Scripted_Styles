import matplotlib.pyplot as plt
import numpy as np
import random


prob=0.5

random.seed(1)
rang = 1000000
packet=6

list=[]

data=0
for x in range(0,rang):
    if random.random()>=prob:
        data+=1
    else:
        data-=1
    list +=[data]

final_data = np.zeros(rang+1)

# for x in range(rang):
#     final_data[x+1]=list[x]+final_data[x]

plt.figure(figsize=[6.0,6.0])
#plt.plot(np.array([np.linspace(0, rang, rang+1)]).reshape(rang+1,1), np.array([final_data]).reshape(rang+1,1))
plt.plot(np.linspace(1,rang, rang), list)
plt.xlabel(f"Trial (Out of {rang})", fontsize=13)
plt.ylabel("R.W value", fontsize=13)
plt.subplots_adjust(left=0.15)
plt.title(f"Random Walk With p={prob}", fontsize=16)
plt.show()