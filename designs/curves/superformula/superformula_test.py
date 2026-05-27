import numpy as np
import matplotlib.pyplot as plt

# Define the nested cosine function
def nested_cosine(pos, iterations):
    for i in range(iterations):
        if i==0:
      	    x = np.cos(pos * np.sqrt(2))
        else:
            x= np.cos(pos*np.sqrt(2)-x)
    return x

# Set up the x values and the number of iterations
x_values = np.linspace(0, np.pi*2*2, 300)
iterations = 50000  # You can change this to a larger number for more nesting

# Compute the y values for the nested cosine function
y_values = [nested_cosine(x, iterations) for x in x_values]

# Plot the function
plt.figure(figsize=(8, 6))
plt.plot(x_values, y_values, label=f'{iterations} Nested Cosines')
plt.title('Nested Cosine Function')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True)
plt.legend()
plt.show()

