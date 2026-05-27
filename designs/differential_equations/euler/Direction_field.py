from Euler import Eulers_Method
import numpy as np
import matplotlib.pyplot as plt
# import matplotlib

# matplotlib.use('AGG')

# Function to get input values
def get_input(prompt):
    return input(prompt).split(',')

# Get user input for ranges
yrange = get_input('Enter y range to plot solutions (start y, end y):')
xrange = get_input('Enter x range to plot solutions (start x, end x):')

xinitial = float(xrange[0])
xfinal = float(xrange[1])

yinitial = float(yrange[0])
yfinal = float(yrange[1])

soln_number = int(input("How many solns?"))

# Generate initial y values
yinit = np.linspace(yinitial, yfinal, soln_number)

soln_list = []
slope_list = []
# Compute solutions using Euler's Method
for i in range(len(yinit)):
    
    dat= Eulers_Method(np.fabs(xfinal - xinitial), xinitial, yinit[i], 10000)
    soln_list.append(dat[0])
    slope_list.append(dat[1])   


# Plotting
colormap = plt.get_cmap('plasma')
length = len(soln_list)

#filter the data
#from standard_filter import upper_bound_filter

#soln_list=upper_bound_filter(soln_list)

fig=plt.figure(figsize=[5,5])
for i in range(len(soln_list)):
    x_data = soln_list[i][0]
    ysoln_data = soln_list[i][1]
    plt.plot(x_data, ysoln_data, linewidth=0.15, color=colormap(i / length), antialiased=True)

# plt.axis('off')
plt.title('Solutions')

# fig=plt.figure(figsize=[5,5])
# for i in range(len(slope_list)):
#     x_data = soln_list[i][0]
#     yslop_data = slope_list[i]
#     plt.plot(x_data, yslop_data, linewidth=0.15, color=colormap(i / length), antialiased=True)

# plt.title('Slope Field')

#plt.yscale('symlog')
# #plt.xscale('symlog')
# plt.axis('off')

plt.show()

# # Save the plot
# plt.savefig('rectish_4_log_higherdpi.png', transparent=True, dpi=5400)
