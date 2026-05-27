import numpy as np
import matplotlib.pyplot as plt

# Set parameters
num_waves = 1000
vertical_lines = 4
base_amplitude = 1.0
base_phase = 0.5  # in radians

# Define decrements so amplitude and phase decrease gradually
amp_decrement = 1 / num_waves
phase_decrement = 1 / num_waves

# Define x positions for vertical lines.
x_start = 2  
separation = 2
x_positions = [x_start + i * separation for i in range(vertical_lines)]

# Determine a square domain:
# Assume maximum horizontal deviation is ~base_amplitude, so let the x-domain be:
x_dom_min = x_positions[0] - base_amplitude
x_dom_max = x_positions[-1] + base_amplitude

# Now choose y to cover the same interval, making a square coordinate system.
y = np.linspace(x_dom_min, x_dom_max, 1000)

# Create a square canvas.
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_aspect('equal')

# Set up two colormaps (here using the reversed plasma)
cmap1 = plt.get_cmap("plasma_r")
cmap2 = plt.get_cmap("plasma_r")
cut = 1

# Draw the strokes.
for i in range(num_waves, 0, -1):
    amplitude = base_amplitude - i * amp_decrement
    phase = base_phase - i * phase_decrement
    
    for x_base in x_positions:
        # Alternate extra phase shift based on the wave index.
        if i % 2 == 0:
            add = 0
            color = cmap1(cut*(i / num_waves) + (1-cut)*0.5)
        else:
            add = np.pi/4
            color = cmap2(cut*(i / num_waves) + (1-cut)*0.5)
        
        # Vertical propagation: x oscillates around x_base, y runs over our square domain.
        x_curve      = x_base + amplitude * np.sin(y + phase + add)
        x_curve_neg  = x_base - amplitude * np.sin(y + phase + add)
        x_curve_sh   = x_base + amplitude * np.sin(y + phase + np.pi/4 + add)
        x_curve_sh_n = x_base - amplitude * np.sin(y + phase + np.pi/4 + add)
        
        ax.plot(x_curve,      y, color=color, linewidth=1)
        ax.plot(x_curve_neg,  y, color=color, linewidth=1)
        ax.plot(x_curve_sh,   y, color=color, linewidth=1)
        ax.plot(x_curve_sh_n, y, color=color, linewidth=1)
        
        # Horizontal propagation: now the roles are swapped.
        # x runs over our square domain and y oscillates around x_base.
        ax.plot(y, x_curve,      color=color, linewidth=1)
        ax.plot(y, x_curve_neg,  color=color, linewidth=1)
        ax.plot(y, x_curve_sh,   color=color, linewidth=1)
        ax.plot(y, x_curve_sh_n, color=color, linewidth=1)

ax.set_title("Abstract Vertical Lines on a Square Canvas")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.axis("off")
plt.show()
