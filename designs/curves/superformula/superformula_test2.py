import numpy as np
import matplotlib.pyplot as plt

# Initial values
s_1 = np.sqrt(2)
n_values = 20  # You can adjust this to any maximum n

# Calculate the sequence
s = [s_1]
for i in range(1, n_values):
    s_next = np.sqrt(2 + np.sqrt(s[-1]))
    s.append(s_next)

# Plot the sequence
plt.figure(figsize=(10, 6))
plt.loglog(range(1, n_values + 1), s, marker='o', linestyle='-')
plt.xlabel(r'$n$')
plt.ylabel(r'$s_n$')
plt.title(r'Sequence $\{s_n\}$ where $s_{n+1} = \sqrt{2 + \sqrt{s_n}}$')
plt.grid()
plt.show()

