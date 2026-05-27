import matplotlib.pyplot as plt
import numpy as np


iterations = 500
num=2000
siz=17

delta=num/siz

dec_data=np.logspace(np.log(10**17.01),np.log(10**51.0),num,base=np.e)



#3000-bad
#4 better than 2
#nothing has changed the resolution quality except for changing the backend 
# tried 'TkAgg', made worse
#macosx
#WebAgg
#

import matplotlib
matplotlib.use('AGG')


#exponential cutoff with cycloidial properties, the larger the number, the more it is reduced, proportioal to the 
#curve of a cycloid, with the lowest point being at the origin 

frac=1

eqnx=lambda x,a:np.pi*a*(x-frac*np.sin(x))


eqny=lambda y,a:2*a-(2*a*(1-frac*np.cos(y)))


def logx_correction(iteration, a):
	c=2
	return np.exp(c*(iteration))


def logy_correction(iteration, a):
	c=6
	b=0.172171875
	return np.exp(c*(b*eqny(iteration,a)*iteration**2)**2)


datx=[]
daty=[]

for dec in range(num):
	x=[]
	y=[]
	
	ncur=dec_data[dec]

	for iter in range(iterations):

		y+=[ncur]
		x+=[iter]

		if int((str(ncur))[-1])%2==0:
			ncur/=2
		else:	
			ncur=3*ncur

	datx+=[x]
	daty+=[y]

fig=plt.figure(figsize=[2.5,5.])
#plt.style.use('dark_background')


colormap=plt.get_cmap('plasma')


#process:



# for n in range(len(datx)):
# 	for j in range(len(datx[n])):
# 		datx[n][j]=datx[n][j]

# for n in range(len(daty)):
# 	for j in range(len(daty[n])):
# 		daty[n][j]=daty[n][j]/logy_correction(daty[n][j],a)

mylist=[]
for n in range(num):	
	plt.plot(datx[n][::-1],daty[n][::-1], linewidth=0.1, color=colormap((n%delta)**5/delta**5))
	mylist+=[max(daty[n])]


# import pandas as pd

# pd.DataFrame(daty[0], columns=['y']).to_csv('collatz.csv')

ax=plt.gca()

#ax.scatter(1,max(mylist)*10**1.5, color='black')


plt.axis('off')
plt.rcParams['lines.antialiased'] = True


# Get the size of the figure in inches
fig_size_inches = fig.get_size_inches()

dpi=9000

# Convert inches to pixels
fig_width_pixels = fig_size_inches[0] * dpi
fig_height_pixels = fig_size_inches[1] * dpi

print(f"Figure Dimensions (in pixels): {fig_width_pixels} x {fig_height_pixels}")


plt.yscale('symlog')
plt.xscale('symlog')


plt.savefig("dcollatz_logscale.png",transparent=True,format='png',bbox_inches='tight',dpi=dpi)


plt.show()




