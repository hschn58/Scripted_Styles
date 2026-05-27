import matplotlib.pyplot as plt
import numpy as np
from Euler2 import Eulers_Method
import matplotlib

matplotlib.use('AGG')

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
# Compute solutions using Euler's Method
for i in range(len(yinit)):
    soln = Eulers_Method(np.fabs(xfinal - xinitial), xinitial, yinit[i], 10000)
    if soln[0] and soln[1]:  # Check if the solution is not empty
        soln_list.append(soln)

# Plotting
colormap = plt.get_cmap('plasma')
length = len(soln_list)

for i in range(length):
    x_data = soln_list[i][0]
    y_data = soln_list[i][1]
    plt.plot(x_data, y_data, linewidth=0.3, color=colormap(i / length))

plt.yscale('symlog')
#plt.xscale('symlog')
plt.axis('off')

# Save the plot
plt.savefig('solpdown2.png', transparent=True, dpi=1200)
