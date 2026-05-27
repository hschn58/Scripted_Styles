from PIL import Image
#import colorsys
import os
width = 1000; height = 1000
img = Image.new('RGBA', (width, height), color = 'black')
pixels = img.load()
for i in range(width):
    pixels[i, :]=tuple([int((x/width)*255) for x in [i, i, i, i]])
img.save('output.png')
os.system('open output.png')