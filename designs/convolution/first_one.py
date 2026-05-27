import numpy as np
from sympy import symbols, integrate, lambdify, exp, sin, cos
import matplotlib.pyplot as plt

def function_convolution(f1, f2, t, tau):
    """
    Returns the convolution of two functions f1 and f2 over a finite interval.

    Parameters:
    f1 : sympy function
        The first input function.
    f2 : sympy function
        The second input function.
    t : sympy symbol
        The variable of the input functions.
    tau : sympy symbol
        The dummy variable for the convolution integral.

    Returns:
    sympy function
        The convolution of f1 and f2.
    """
    # Define a finite range for integration
    lower_limit = 0
    upper_limit = 10
    return integrate(f1.subs(t, tau) * f2.subs(t, t - tau), (tau, lower_limit, upper_limit))

# Define the variables
t, tau = symbols('t tau')

# Initial input functions
f1 = t
f2 = -t

# Number of recursive convolutions
depth_no = 7

# Define a set of x-values
x_values = np.linspace(0, 10, 100)

# Create a plot
plt.figure(figsize=(10, 6))

# Plot the initial functions
conv_func1 = lambdify(t, f1, 'numpy')
conv_func2 = lambdify(t, f2, 'numpy')
y_values1 = conv_func1(x_values)
y_values2 = conv_func2(x_values)
plt.plot(x_values, y_values1, label='f1=exp(-t)', linewidth=1)
plt.plot(x_values, y_values2, label='f2=sin(t)', linewidth=1)

# Perform recursive convolution and plot
for depth in range(depth_no):
    # Compute the convolution of the current functions
    convolution_result = function_convolution(f1, f2, t, tau)
    
    # Convert the convolution result to a numerical function
    conv_func = lambdify(t, convolution_result, 'numpy')
    
    # Evaluate the convolution function over the x-values
    y_values = np.array([conv_func(x) for x in x_values])
    
    # Plot the result
    plt.plot(x_values, y_values, label=f'Convolution {depth+1}', linewidth=1)
    
    # Update f1 and f2 for the next iteration
    f1 = f2
    f2 = convolution_result

# Set plot labels and title
plt.xlabel('x')
plt.ylabel('Convolution Value')
plt.title('Recursive Convolution of Functions')
plt.legend()
plt.show()
