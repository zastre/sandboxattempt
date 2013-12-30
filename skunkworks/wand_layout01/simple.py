#!/usr/bin/python

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing

# Create a blank image
image_width = 300
image_height = 400
img = Image(width=image_width, height=image_height, background=Color('rgb(44,128,64)'))

# Need a drawing object for rendering.
# Here there are some canvas (?) settings being established
d = Drawing()
d.fill_color = Color('rgb(255,255,255)')
d.font = 'Arvo-Regular.ttf'
d.font_size = 48

# Want some info on how big the text will be
# when drawn, then use it for calculations
#
fm = d.get_font_metrics(img, 'Hello!')
height = fm.text_height
width = fm.text_width
pos_x = int((image_width - width) / 2)
pos_y = int((image_height) / 2)

# Specify the coordinate of the lower-left
# position of the text (where 0,0 is the
# upper-left hand corner o the canvas).
#
d.text(pos_x, pos_y, 'Hello!')
d(img)

# Save the result
#
img.save(filename='300x400-red.png')

# For debugging / peeking
#
fm = d.get_font_metrics(img, "H!")
print fm
