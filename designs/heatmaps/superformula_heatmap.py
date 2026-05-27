import numpy as np
import matplotlib.pyplot as plt
import os

import matplotlib
#matplotlib.use('AGG')

current_directory = os.path.dirname(os.path.abspath(__file__))


def superformula(m, n1, n2, n3, points=5000):
    phi = np.linspace(0, 2 * np.pi, points)
    n1_safe = np.where(np.abs(n1) < 1e-10, 1e-10, n1)
    r = (np.abs(np.cos(m * phi / 4) / 1) ** n2 + np.abs(np.sin(m * phi / 4) / 1) ** n3) ** (-1 / n1_safe)
    x = r * np.cos(phi)
    y = r * np.sin(phi)
    return x, y

# Base parameters (Example 1)
base_m = 7
base_n1 = 0.9
base_n2 = 0.9
base_n3 = 0.9

# Number of iterations
increment = 0.1
iterations = int(base_n1 / increment)


# Create a figure
plt.figure(figsize=(12, 12))

# Generate colors for each iteration

colormap = plt.get_cmap('plasma')

colors = [colormap(i / iterations) for i in range(iterations)]

# Iterate over a range of 'n1' values to create variation
for i in range(iterations):
    # Modify parameters slightly in each iteration
    m = base_m
    n1 = base_n1 - i * increment      # Increment n1
    n2 = base_n2
    n3 = base_n3

    # Generate points
    x, y = superformula(m, n1, n2, n3)

    # Plot each shape with varying transparency and color
    plt.plot(x, y, color=colors[i], linewidth=0.1, alpha=0.6)

from ScriptedStyles.Designs.Releases.ismethods.check import unique_filename

plt.title('base_m'+' = 'f'{base_m}'+','+'base_n1'+' = 'f'{base_n1}'+','+'base_n2'+' = 'f'{base_n2}'+','+'base_n3'+' = 'f'{base_n3}')

# Adjust plot settings
plt.axis('equal')
plt.axis('off')
plt.tight_layout()
plt.show()


#plt.savefig(unique_filename(os.path.join(current_directory, 'superformula.png')), dpi=600)

