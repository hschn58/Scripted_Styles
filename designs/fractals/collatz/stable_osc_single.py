import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import pandas as pd

# Create some data
iter = 1000000000
x = np.linspace(0, iter, iter + 1)

daty = []

for dec in range(1):
    y = []
    ncur = 1.01

    for iteration in range(iter + 1):  # Ensure y has the same length as x
        y.append(ncur)

        if int(str(ncur)[-1]) % 2 == 0:
            ncur /= 2
        else:
            ncur = 3 * ncur

    daty.append(y)

y = np.array(daty[0])

# # Create segments
# points = np.array([x, y]).T.reshape(-1, 1, 2)
# segments = np.concatenate([points[:-1], points[1:]], axis=1)

# # Normalize the x values to the range [0, 1] for colormap
# norm = Normalize(x.min(), x.max())
# colors = cm.plasma(norm(x))

# # Create the LineCollection object
# lc = LineCollection(segments, cmap='plasma', norm=norm)
# lc.set_array(x)
# lc.set_linewidth(2)

# # Create the plot
# fig, ax = plt.subplots()
# ax.add_collection(lc)
# ax.set_xlim(x.min(), x.max())
# ax.set_ylim(y.min(), y.max())
# ax.autoscale()

# # print(y.shape())
# # print(type(x))
# # print(type(y))

data=np.column_stack((x,y))	

pd.DataFrame(data=data,columns=['x','y']).to_csv('ftdata.csv')




plt.axis('off')
plt.show()




# fig=plt.figure(figsize=[5.,5.])
# #plt.style.use('dark_background')


# colormap=plt.get_cmap('plasma')


# #process:



# # for n in range(len(datx)):
# # 	for j in range(len(datx[n])):
# # 		datx[n][j]=datx[n][j]

# # for n in range(len(daty)):
# # 	for j in range(len(daty[n])):
# # 		daty[n][j]=daty[n][j]/logy_correction(daty[n][j],a)

# mylist=[]
# for n in range(num):	
# 	plt.plot(datx[n][::-1],daty[n][::-1], linewidth=0.1, color=colormap((n%delta)**5/delta**5))
# 	mylist+=[max(daty[n])]


# import pandas as pd

# pd.DataFrame(daty[0], columns=['y']).to_csv('collatz.csv')

# ax=plt.gca()

# #ax.scatter(1,max(mylist)*10**1.5, color='black')


# plt.axis('off')
# plt.rcParams['lines.antialiased'] = True


# # Get the size of the figure in inches
# fig_size_inches = fig.get_size_inches()

# dpi=9000

# # Convert inches to pixels
# fig_width_pixels = fig_size_inches[0] * dpi
# fig_height_pixels = fig_size_inches[1] * dpi

# print(f"Figure Dimensions (in pixels): {fig_width_pixels} x {fig_height_pixels}")


# plt.yscale('symlog')
# #plt.xscale('symlog')


# plt.savefig("dcollatz2_150.png",transparent=True,format='png',bbox_inches='tight',dpi=dpi)


# plt.show()




