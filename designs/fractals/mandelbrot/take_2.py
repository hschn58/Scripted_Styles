from PIL import Image
import colorsys
import math
import os

#frame parameters
pixels=1000
width = pixels #pixels
height = pixels #pixels
x = 0.3669884
y = 0.59084548
xRange = 0.00001 
yRange = 0.00001

precision = 1000

minX = x - xRange / 2
maxX = x + xRange / 2
minY = y - yRange / 2
maxY = y + yRange / 2

img = Image.new('RGBA', (width, height), color = 'black')
pixels = img.load()

def logColor(distance, base, const, scale):
    color = -1 * math.log(distance, base)
    rgb = colorsys.hsv_to_rgb(const + scale * color,0.5,0.9)
    return tuple(round(i * 255) for i in rgb)

def powerColor(distance, exp, const, scale):
    color = distance**exp
    rgb = colorsys.hsv_to_rgb(const + scale * color,1 - 0.4 * color,0.9)
    return tuple(round(i * 255) for i in rgb)
def sinColor(distance, theta, const, scale):
    color = math.sin(distance*(math.pi*theta))+1
    rgb = colorsys.hsv_to_rgb(const+scale*color,0.999*color,0.999)
    return tuple(round(i*255) for i in rgb) 
for row in range(height):
    for col in range(width):
        x = minX + col * xRange / (width)
        y = maxY - row * yRange / (height)
        oldX = x
        oldY = y
        for i in range(precision + 1):
            a = x*x - y*y #real component of z^2
            b = 2 * x * y #imaginary component of z^2
            x = a + oldX #real component of new z
            y = b + oldY #imaginary component of new z
            if x*x + y*y > 4:
                break
        if i < precision:
            distance = (i + 1) / (precision + 1)
            rgb = sinColor(distance, 20, 0.3, 1)
            pixels[col,row] = rgb
        index = row * width + col + 1
        print("{} / {}, {}%".format(index, width * height, round(index / width / height * 100 * 10) / 10))

img.save('output.png')
os.system('open output.png')


# TODO: boundary problem, finite difference (stub removed)