
from turtle import *
import turtle

# pensize(3)
# speed(0)
# bgcolor("white")
# color("black")

# for i in range(255):
#     for j in range(4):
#         circle(200-i, steps = 200-i)


import turtle as t
from turtle import Screen
import random as rn



#torus ish
# t.colormode(255)

# def rand_color():
#     r = rn.randint(0,255)
#     g = rn.randint(0,255)
#     b = rn.randint(0,255)
#     return (r, g, b)

# def til_circle(angle):
#     for i in range(int(360/angle)):
#         t.pensize(2)
#         t.speed('fastest')
#         t.color('black')
#         t.circle(200)
#         t.setheading(t.heading() + angle)

# til_circle(1)

# screen = Screen()
# screen.exitonclick()
 
# t.speed('fastest')

# for i in range(10):
#     for j in range(4):
#         t.right(90)
#         t.circle(200-15*i, steps = 90)
#         t.left(90)
#         t.circle(200-15*i, steps = 90)
#         t.right(180)
#         t.circle(50, 24)


# t.speed('fastest')


# # for steps in range(200):
# #     forward(steps)
# #     right(45)


# #max size for getscreen is like 200

# for I in range(100):
#     forward(200)
#     right(150)
#     forward(200)
#     left(20)


# # forward(100)
# # left(150)
# # forward(100)


# # Grab the canvas from the screen
# t.hideturtle()


# screen = t.Screen()

# screen.update()




# # Grab the canvas

# canvas = screen.getcanvas()

# # Larger or custom dimensions (in postscript points, 1 point ~ 1/72 inch)
# canvas.postscript(
#     file="turtle_density_feed.eps",
#     colormode="color",
#     x=0,
#     y=0,
#     width=800,      # the drawing area width in points
#     height=800,     # the drawing area height in points
#     pagewidth=800,  # the page width in points
#     pageheight=800  # the page height in points
# )

import turtle as t
from turtle import Screen

# Create the screen and turtle
screen = Screen()
screen.setup(width=800, height=800)  # sets the window size
t.speed('fastest')

# Example drawing

# for steps in range(200):
#     forward(steps)
#     right(45)



# import turtle

import math

# Draw concentric rings with increasing radii
for radius in range(20, 301, 20):
    t.penup()
    # Move to the starting point: (0, -radius) so that the circle will be centered at (0, 0)
    t.setposition(0, -radius)
    t.pendown()
    t.circle(radius, steps=8)


# Draw concentric octagons ("rings") with increasing radii
for radius in range(20, 301, 20):
    t.penup()
    # Move to (0, -radius) so that t.circle() draws a polygon centered at (0, 0)
    t.setposition(0, -radius)
    t.pendown()
    t.circle(radius, steps=8)

# Draw radial lines from the center to the vertices of the largest octagon (radius=300)
for i in range(8):
    angle_deg = i * 45  # 8 vertices: 0, 45, 90, ... 315 degrees
    
    # Compute the vertex coordinate on the largest ring (radius 300)
    x = 300 * math.sin(math.radians(angle_deg))
    y = -300 * math.cos(math.radians(angle_deg))
    
    # Draw a line from the center to the vertex
    t.penup()
    t.goto(0, 0)
    t.pendown()
    t.goto(x, y)
    
    # OPTIONAL: Mark the intersection on each ring with a red dot.
    # This loop goes through each ring's radius and places a dot at the corresponding vertex.
    for r in range(20, 301, 20):
        xi = r * math.sin(math.radians(angle_deg))
        yi = -r * math.cos(math.radians(angle_deg))
        t.penup()
        t.goto(xi, yi)
        t.dot(5, "red")




t.hideturtle()


screen.update()

# Get the canvas and compute the bounding box of all items
canvas = screen.getcanvas()
bbox = canvas.bbox("all")  # returns (xmin, ymin, xmax, ymax)
print("Bounding Box:", bbox)

if bbox:
    x, y, x2, y2 = bbox
    width = x2 - x
    height = y2 - y

    canvas.postscript(
        file="turtle_density_feed.eps",
        colormode="color",
        x=x,
        y=y,
        width=width,
        height=height,
        pagewidth=width,
        pageheight=height
    )
