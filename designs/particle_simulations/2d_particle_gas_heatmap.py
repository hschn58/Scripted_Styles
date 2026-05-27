import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import matplotlib
from matplotlib.colors import LogNorm, PowerNorm

matplotlib.use('Agg')

#heatmap through the frames

grid_size = 1000000
sigmacoeff = 7/1000 * (grid_size/100)*1.5

class Particle:
    def __init__(self, mass, position, velocity, i):
        #define all class attributes
        self.mass = mass
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.i=i
        
    def update_position(self, time_step):
        # Update position based on velocity
        p_rad=0.01470588
        
        self.position += self.velocity * time_step
        
        # Check for collisions with the grid edges
        for i in range(2):  # Check x and y components
            if self.position[i] <= 0+p_rad or self.position[i] >= 1-p_rad:
                # if ##############wall condition
                self.velocity[i] = -self.velocity[i]  # Reflect the velocity

    def apply_force(self, force, time_step):
        # Update velocity based on force (F = ma)
        acceleration = force / self.mass
        self.velocity += acceleration * time_step
        # Update position after applying force
        self.update_position(time_step)

    def check_collision(self,other,col_mat,i,k):
        
        col_axis=self.position-other.position
        magnitude=np.linalg.norm(col_axis)
        p_rad=0.01470588
        
        if (magnitude <= 2*p_rad):
            if np.dot(col_axis,self.velocity)*np.dot(col_axis,other.velocity)<0:
        
                ucol_axis=col_axis/magnitude
    
                #self component
                #smag+omag=(smag-omag)/v_2,1 +v_2,1
                
                #mv_1,0 + mv_2,0 = mv_1,1 + mv_2,1
                #coefficient of restitution set to 1
                #thus, smag-vmag=-(v_1,1-v_2,1)
        
                smag=np.dot(ucol_axis,self.velocity)
                omag=np.dot(ucol_axis,other.velocity)
                
                omag_out=smag
                smag_out=omag
        
                self.velocity, other.velocity = (smag_out*(ucol_axis)+(self.velocity-smag*ucol_axis)), (omag_out*(ucol_axis)+(other.velocity-omag*ucol_axis))
                # Mark the collision as handled
                col_mat[i, k] = True
                col_mat[k, i] = True  # S
        return
        
# Parameters
mass = 1.0
num_particles = 100
time_step = 0.1
num_steps = 500
force = np.array([0, 0])  # No external force applied
grid_size = 3000 # Higher resolution grid
line_width = 2  # Adjust this for the effective "line width"

# Initialize particles
particles = {}
for i in range(num_particles):
    particles[f"x{i}"] = Particle(
        mass=mass, 
        position=np.random.rand(2), 
        velocity=10 * (np.random.rand(2) - 0.5),
        i=i
    )

# Initialize the grid to accumulate path densities
path_density = np.zeros((grid_size, grid_size))

# Simulate particle movement
for j in range(num_steps):
    for i in range(num_particles):
        cvar = particles[f"x{i}"]
        cvar.apply_force(force, time_step)
        loc = cvar.position.copy()
        
        # Convert particle position to grid coordinates
        grid_x = min(max(int(loc[0] * grid_size), 0), grid_size - 1)
        grid_y = min(max(int(loc[1] * grid_size), 0), grid_size - 1)
        
        # Apply a Gaussian distribution around the point to simulate line width
        path_density[grid_y, grid_x] += 1

# Apply Gaussian filter to simulate line width effect
path_density = gaussian_filter(path_density, sigma=sigmacoeff*line_width)

# Min-Max Normalization
min_val = np.min(path_density)
max_val = np.max(path_density)

# Apply min-max normalization
normalized_path_density = (path_density - min_val) / (max_val - min_val)


######
import matplotlib.colors as mcolors
# 1. Get the "binary" colormap
binary_cmap = plt.get_cmap("binary")

# 2. Create a cyclic version by mapping the colormap to a sine wave pattern
N = 256  # Number of color levels
x = np.linspace(0, 1, N)  # Linear mapping from 0 to 1
cyclic_map = 0.5 * (1 - np.cos(6 * np.pi * x))  # Smooth cyclic function

# 3. Apply this mapping to the original "binary" colormap
cyclic_colors = binary_cmap(cyclic_map)

# 4. Create a new colormap from this transformed data
cyclic_binary = mcolors.ListedColormap(cyclic_colors, name="cyclic_binary")

#####
from ScriptedStyles.Designs.Releases.ismethods.check import unique_filename

#26:974,26:974
colormap='cyclic_binary'
# Plot the heatmap with increased spatial resolution and line width effect
plt.figure(figsize=(6, 6))
plt.imshow(normalized_path_density, cmap=cyclic_binary, origin='lower', extent=[0, 1, 0, 1], norm=PowerNorm(0.5))
plt.axis('off')
plt.savefig(unique_filename('2d_heatmap_powernorm_'+colormap+'_strange'+'.jpg'), dpi=1200)
plt.close()


