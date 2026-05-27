import numpy as np
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('Agg')

# Parameters for the Clifford Attractor
a = -1.4
b = 1.6
c = 1.0
d = 0.7

# Number of iterations
n = 1000000000

# Initialize arrays
x = np.zeros(n)
y = np.zeros(n)

# Generate points
for i in range(n - 1):
    x[i + 1] = np.sin(a * y[i]) + c * np.cos(a * x[i])
    y[i + 1] = np.sin(b * x[i]) + d * np.cos(b * y[i])

# Plotting
plt.figure(figsize=(10, 10), facecolor='black')
plt.scatter(x, y, s=1, c=np.arctan2(y, x), cmap='hsv', alpha=0.0001)
plt.axis('off')
plt.tight_layout()
plt.savefig('clifford_attractor.png', dpi=1200, facecolor='black')


