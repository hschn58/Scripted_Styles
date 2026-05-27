import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# set the parameters
iterations = 35
num = 2000
siz = 17
delta = num/siz
dec_data = np.logspace(np.log(10**17.01), np.log(10**51.0), num, base=np.e)

# define colormap
colormap = plt.get_cmap('plasma')

# initialize data storage lists for x and y
datx = []
daty = []

# iteration over range specified by dec_data
for dec in range(num):
    x = []
    y = []

    ncur = dec_data[dec]

    for iter in range(iterations):

        y.append(ncur)
        x.append(iter)

        # rule for updating ncur
        if int((str(ncur))[-1]) % 2 == 0:
            ncur /= 2
        else:   
            ncur = 3 * ncur

    datx.append(x)
    daty.append(y)

fig = plt.figure(figsize=[5.,5.])

# plot data and save max value of each y
mylist = []
for n in range(num):    
    plt.plot(datx[n][::-1], daty[n][::-1], linewidth=0.1, color=colormap((n % delta) ** 5 / delta ** 5))
    mylist.append(max(daty[n]))

# save the y data for the first plot as a .csv
pd.DataFrame(daty[0], columns=['y']).to_csv('collatz.csv')

# make plot look better
plt.axis('off')

# apply symmetrical log scaling in y-direction
plt.yscale('symlog')

# save the figure as a .png
plt.savefig("collatz_plot.png", transparent=True, format='png', bbox_inches='tight')

plt.show()