from PIL import Image
from mandelbrot import MandelbrotSet
from PIL.ImageColor import getrgb
from viewport import Viewport
from PIL import ImageEnhance
import matplotlib.cm
import numpy as np
from Mandelbrot_ctrans import ctrans
mandelbrot_set = MandelbrotSet(max_iterations=200, escape_radius=10000)
image = Image.new(mode="RGB", size=(1024, 1024))
viewport = Viewport(image, center=0.36699 + 0.59084j, width=0.000075)

def paint(mandelbrot_set, viewport, palette, smooth):
     for pixel in viewport:
         stability = mandelbrot_set.stability(complex(pixel), smooth)
         index = int(min(stability * len(palette), len(palette) - 1))
         pixel.color = palette[index % len(palette)]
def denormalize(palette):
     return [
         tuple(int(channel * 255) for channel in color)
         for color in palette
     ]

colormap = ctrans('hsv').colors
palette = denormalize(colormap)
for pixel in Viewport(image, center=1.12 + 0.75j, width=0.000075):
    c = complex(pixel)
    instability = 1 - mandelbrot_set.stability(c, smooth=True)
    pixel.color = int(instability * 255)
paint(mandelbrot_set, viewport, palette, smooth=True)
image.show()