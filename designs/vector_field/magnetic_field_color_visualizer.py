


import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
import colorsys

# Constants
a = 1.0  # Radius of the loop
mu0_I_over_4pi = 1.0  # Normalized constant (mu_0 * I / (4 * pi))

# Define a finer grid in the x-z plane
x = np.linspace(-2, 2, 1200)
z = np.linspace(-2, 2, 1200)
X, Z = np.meshgrid(x, z)

# Initialize magnetic field components
Bx = np.zeros_like(X)
Bz = np.zeros_like(Z)

# Compute the magnetic field using numerical integration
def integrand(phi, x, z, component):
    r = np.sqrt(a**2 + x**2 + z**2 - 2 * a * x * np.cos(phi))
    if component == 'x':
        return a * z * np.cos(phi) / r**3
    elif component == 'z':
        return a * (a - x * np.cos(phi)) / r**3

for i in range(len(x)):
    for j in range(len(z)):
        x_val, z_val = X[i, j], Z[i, j]
        if z_val == 0 and abs(x_val) == a:  # Avoid singularity at the loop
            Bx[i, j] = 0
            Bz[i, j] = 0
            continue
        # Integrate over phi from 0 to 2pi
        Bx[i, j] = mu0_I_over_4pi * quad(lambda phi: integrand(phi, x_val, z_val, 'x'), 0, 2*np.pi)[0]
        Bz[i, j] = mu0_I_over_4pi * quad(lambda phi: integrand(phi, x_val, z_val, 'z'), 0, 2*np.pi)[0]

# Compute the angle theta = arctan(Bx / Bz) and magnitude |B|
theta = np.arctan2(Bx, Bz)  # Angle from vertical
magnitude = np.sqrt(Bx**2 + Bz**2)

# Logarithmic normalization for magnitude to enhance dynamic range
# Add a small constant to avoid log(0)
magnitude_log = np.log10(magnitude + 1e-10)
magnitude_normalized = (magnitude_log - magnitude_log.min()) / (magnitude_log.max() - magnitude_log.min())
magnitude_normalized = np.nan_to_num(magnitude_normalized)  # Handle any NaNs

# Direction factor: |theta| / (pi/2) for deviation from vertical
direction_factor = np.abs(theta) / (np.pi / 2)  # 0 to 1 as theta goes from 0 to pi/2
direction_factor = np.clip(direction_factor, 0, 1)

# Define colors in HSV for better blending
# Base color (vertical field): Blue (hue = 240/360 in HSV)
# Color 1 (horizontal field): Red (hue = 0/360 in HSV)
# Color 2 (magnitude max): Yellow (hue = 60/360 in HSV)
def rgb_to_hsv(rgb):
    return np.array(colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2]))

def hsv_to_rgb(hsv):
    return np.array(colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2]))

color_base_rgb = np.array([0, 0, 1])  # Blue
color1_rgb = np.array([1, 0, 0])  # Red
color2_rgb = np.array([1, 1, 0])  # Yellow

color_base_hsv = rgb_to_hsv(color_base_rgb)
color1_hsv = rgb_to_hsv(color1_rgb)
color2_hsv = rgb_to_hsv(color2_rgb)

# Initialize the final color array in HSV
final_color_hsv = np.zeros((len(x), len(z), 3))

# Direction-based hue: interpolate hue from blue (240) to red (0)
# If direction_factor = 0 (vertical), hue = 240; if direction_factor = 1 (horizontal), hue = 0
hue_direction = (1 - direction_factor) * color_base_hsv[0] + direction_factor * color1_hsv[0]
# Handle hue wrapping (since 240 to 0 crosses the 360/0 boundary)
hue_direction = np.where(hue_direction > 0.5, hue_direction - 1, hue_direction)
hue_direction = np.where(hue_direction < 0, hue_direction + 1, hue_direction)

# Set saturation and value for direction
sat_direction = np.ones_like(hue_direction)  # Full saturation
val_direction = np.ones_like(hue_direction)  # Full value

# Magnitude-based value: interpolate value from 0.3 (dim) to 1 (bright)
val_magnitude = 0.3 + 0.7 * magnitude_normalized  # Range from 0.3 to 1
hue_magnitude = np.full_like(hue_direction, color2_hsv[0])  # Yellow hue
sat_magnitude = np.ones_like(hue_direction)  # Full saturation

# Combine in HSV space
# Use direction for hue, magnitude for value, keep saturation high
final_color_hsv[:, :, 0] = hue_direction  # Hue from direction
final_color_hsv[:, :, 1] = 1.0  # Full saturation
final_color_hsv[:, :, 2] = val_magnitude  # Value from magnitude

# Convert back to RGB for display
final_color_rgb = np.zeros_like(final_color_hsv)
for i in range(len(x)):
    for j in range(len(z)):
        final_color_rgb[i, j] = hsv_to_rgb(final_color_hsv[i, j])

final_color_rgb = np.clip(final_color_rgb, 0, 1)  # Ensure RGB values are between 0 and 1

# Plot the result
plt.figure(figsize=(8, 8))
plt.imshow(final_color_rgb, extent=(-2, 2, -2, 2), origin='lower')
plt.xlabel('x')
plt.ylabel('z')
plt.title('Magnetic Field (Direction and Magnitude) for a Current Loop of Radius 1')
plt.grid(False)
plt.savefig("mag_fig.png", dpi = 300)
plt.show()
