
import numpy as np
import matplotlib.pyplot as plt
import math

def diff_eq(x, y, beta):
    scaler = lambda y, x: 1.5*((1 / (1 + math.exp(-0.1*x)))) * (y - 1.5)
    y = scaler(y, x)
    return (math.log(4.5 - y)) * (1.5 * (math.sin((math.pi / 4) * y)**2)) * beta - y * math.cosh(x) - 2 * y * math.sin(y) + 3 * (math.sin(2 * math.pi * x))**2

def Eulers_Method(x_len, initial_x, initial_y, h, beta):
    diff = x_len - initial_x
    xval = [initial_x]
    yval = [initial_y]

    for i in range(1, h + 1):
        try:
            x0 = ((i - 1) / h) * diff + initial_x
            yprime = diff_eq(x0, initial_y, beta)

            if not math.isfinite(yprime):
                break

            initial_y += yprime * (diff / h)

            xval.append(x0)
            yval.append(initial_y)

        except (OverflowError, ZeroDivisionError, ValueError):
            break

    return [xval, yval]

def generate_slope_field(xrange, yrange, beta, density=20):
    x_vals = np.linspace(xrange[0], xrange[1], density)
    y_vals = np.linspace(yrange[0], yrange[1], density)
    slope_field = []

    for x in x_vals:
        for y in y_vals:
            slope = diff_eq(x, y, beta)
            slope_field.append((x, y, slope))

    return slope_field

# Function to get input values
def get_input(prompt):
    return input(prompt).split(',')

# Get user input for ranges
yrange = list(map(float, get_input('Enter y range to plot solutions (start y, end y):')))
xrange = list(map(float, get_input('Enter x range to plot solutions (start x, end x):')))

xinitial = xrange[0]
xfinal = xrange[1]

yinitial = yrange[0]
yfinal = yrange[1]

soln_number = int(input("How many solns?"))

# Generate initial y values
yinit = np.linspace(yinitial, yfinal, soln_number)

soln_list = []
# Compute solutions using Euler's Method
for i in range(len(yinit)):
    dat = Eulers_Method(np.fabs(xfinal - xinitial), xinitial, yinit[i], 10000, beta=yinit[i]/yfinal)
    soln_list.append(dat)

# Plotting
colormap = plt.get_cmap('plasma')
length = len(soln_list)

fig = plt.figure(figsize=[5,5])
for soln in soln_list:
    x_data, ysoln_data = soln
    plt.plot(x_data[:1600], ysoln_data[:1600], linewidth=0.15, color=colormap(soln_list.index(soln) / length), antialiased=True)

plt.title('Solutions')
plt.axis('off')
# Generate slope field
slope_field = generate_slope_field(xrange, yrange, beta=1)  # Adjust beta if necessary

fig = plt.figure(figsize=[5,5])
for x, y, slope in slope_field:
    plt.quiver(x, y, 1, slope, angles='xy', scale_units='xy', scale=0.1, color=colormap(slope_field.index((x, y, slope)) / len(slope_field)))

plt.axis('off')

plt.xscale('symlog')

plt.title('Slope Field')
plt.show()
