import matplotlib.pyplot as plt
import numpy as np
import math

iterations = 8000

#3000-bad
#4 better than 2
#nothing has changed the resolution quality except for changing the backend 
# tried 'TkAgg', made worse
#macosx
#WebAgg
#
#
import matplotlib
matplotlib.use('macosx')


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

#base it on numbers divisible by 3
for n in range(iterations):
	x=[]
	y=[]
	it=0	
	while True:
		y+=[n]
		x+=[it]

		if int(n*(2/3)) != n*(2/3):
			n=3*n+1
		elif math.gcd(n, n*(2/3))==1:
			n=n/2
		else:
			n=3*n+1
		if n<3:
			break
		it+=1
	datx+=[x]
	daty+=[y]

fig=plt.figure()
plt.style.use('dark_background')


colormap=plt.get_cmap('plasma')


#process:



# for n in range(len(datx)):
# 	for j in range(len(datx[n])):
# 		datx[n][j]=datx[n][j]

# for n in range(len(daty)):
# 	for j in range(len(daty[n])):
# 		daty[n][j]=daty[n][j]/logy_correction(daty[n][j],a)

mylist=[]
for n in range(iterations):	
	plt.loglog(datx[n],daty[n], linewidth=0.3, color=colormap(n**1.4/iterations**1.4))
	mylist+=[max(daty[n])]

ax=plt.gca()

ax.scatter(1,max(mylist)*10**1.5, color='black')


plt.axis('off')
plt.rcParams['lines.antialiased'] = True


# Get the size of the figure in inches
fig_size_inches = fig.get_size_inches()

# Get the DPI (dots per inch) setting
dpi = 2700

# Convert inches to pixels
fig_width_pixels = fig_size_inches[0] * dpi
fig_height_pixels = fig_size_inches[1] * dpi

print(f"Figure Dimensions (in pixels): {fig_width_pixels} x {fig_height_pixels}")



#plt.savefig("new4.png",format='png', dpi=2700)


plt.show()




