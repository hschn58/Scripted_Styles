from mandelbrot import MandelbrotSet
mandelbrot_set = MandelbrotSet(max_iterations=20, escape_radius=1000)
from viewport import Viewport


GRAYSCALE = "L"

from PIL import Image

mandelbrot_set = MandelbrotSet(max_iterations=512, escape_radius=1000)
image = Image.new(mode=GRAYSCALE, size=(512, 512))
viewport = Viewport(image, center=-0.7437 + 0.1314j, width=0.002)

for pixel in Viewport(image, center=-0.7437 + 0.1314j, width=0.002):
    c = complex(pixel)
    instability = 1 - mandelbrot_set.stability(c, smooth=True)
    pixel.color = int(instability * 255)

image.show()