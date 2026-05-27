import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps
import matplotlib
import time
import argparse

start = time.time()
matplotlib.use('Agg')

parser = argparse.ArgumentParser(description="Process the PNG path argument for always run script.")
parser.add_argument("--colormap", type=str, help="Additional information for the process")  # Second positional argument

args = parser.parse_args()

colormap = args.colormap

###
DESCRIPTIVE_KEYWORD = 'KEYWORD'
###

#plasma = colormaps['plasma']


















from ScriptedStyles.Designs.Releases.ismethods.check import unique_filename
import os


dirname = os.path.dirname(__file__)

# Define the path to the images folder
images_dir = os.path.join(dirname, 'images')

# Check if the folder exists; if not, create it.
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

# Create the filename in the images folder.
#"name "filename = os.path.basename(__file__).split('.')[0] + '.jpg'
code_name = os.path.basename(__file__).split('.')[0] + f' {colormap}' + '.jpg'

filename = unique_filename(os.path.join(images_dir, code_name))
plt.savefig(filename, dpi=200, bbox_inches='tight', pad_inches=0.0)


end = time.time()
print('Time taken:', end - start)
