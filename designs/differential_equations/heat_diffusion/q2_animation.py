import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.cm as cm

# Parameters
k = 0.02
b = 2
L = 1
n = 20  # Number of terms in the Fourier series
ts = np.linspace(0.01, 15, 600)  # Time steps for the animation

def C_n0(n):
    if n == 0:
        return np.array([0])  # Avoid division by zero
    else:
        return np.array([(-1 / (2 * n * np.pi)) * 1j * (1 + (-1) ** (n + 1))])

def C_nt(n, x, t, k=0.02, b=0.1, L=1):
    soln = np.zeros(len(x), dtype=complex)
    for ns in range(-n, n + 1):
        if ns == 0:
            continue
        try:
            Cn0 = C_n0(ns)[0]
        except Exception as e:
            print(f"Error at n={ns}: {e}")
            continue
        if Cn0 == 0:
            continue
        k_term = k * (ns * np.pi / L) ** 2
        b_term = b * (ns * np.pi / L)
        exponent = 1j * (ns * np.pi / L) * x - (k_term + 1j * b_term) * t
        soln += Cn0 * np.exp(exponent)
    soln += 0.5
    return soln

# Spatial domain
x = np.linspace(-1, 1, 300)

# Initialize the figure and axis
fig, ax = plt.subplots()
ax.set_xlim(-1, 1)
ax.set_ylim(0, 1)
ax.set_xlabel('x')
ax.set_ylabel('Solution')
ax.set_title('Solution Animation Over Time')

# Generate colors from the plasma colormap
cmap = cm.get_cmap('plasma', len(ts))
colors = [cmap(i) for i in range(len(ts))]

# List to store the lines
lines = []

def init():
    return []

def animate(i):
    t = ts[i]
    soln = C_nt(n, x, t, k=k, b=b, L=L)
    line, = ax.plot(x, soln.real, color=colors[i], lw=1)
    lines.append(line)
    ax.set_title(f'Solution at Time t={t:.2f}')
    return lines

anim = FuncAnimation(fig, animate, init_func=init, frames=len(ts), interval=50, blit=False)

plt.show()
