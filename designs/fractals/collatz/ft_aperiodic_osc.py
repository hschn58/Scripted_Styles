
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')

# Increase the chunksize and adjust the simplify threshold
plt.rcParams['agg.path.chunksize'] = 10000  # You can adjust this value as needed
plt.rcParams['path.simplify_threshold'] = 1.0  #

# Load the data
data_path = 'ftdata.csv'
data = pd.read_csv(data_path)

# Extract the x and y values
x = data['x'].values
y = data['y'].values

# Perform the Fourier transform on the y values
y_fft = np.fft.fft(y)
freq = np.fft.fftfreq(len(y), d=(x[1] - x[0]))  # Use the difference between consecutive x values for the sampling rate

# Plot the Fourier transform
plt.figure()
plt.plot(freq, y_fft,linewidth=0.01, color='blue')

plt.yscale('symlog')

#plt.title('Fourier Transform')
plt.xlabel('Frequency')
plt.ylabel('Magnitude')
plt.axis('off')
plt.savefig('ftplot.png',transparent=True, dpi=2700)
#plt.show()
