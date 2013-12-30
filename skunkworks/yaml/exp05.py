#!/usr/bin/python

import argparse
import sys
import yaml
import re

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.display import display

image_width = 400
image_height = 60

image = Image(width=image_width, height=image_height, background=Color('white'))

draw = Drawing()
draw.font = '/Users/zastre/Dev/fimsi/sandbox/fonts/LatoOTF/TTF/Lato-Reg.ttf'
draw.font_size = 36
draw.fill_color = Color('black')
metrics = draw.get_font_metrics(image, "losing\nphotos", True)

pos_col = int((image_width - metrics.text_width)/2)
pos_row = int(metrics.ascender + (image_height - metrics.text_height)/2) 

print "DEBUG ", pos_col, pos_row

draw.text(pos_col, pos_row, "losing\nphotos")
draw(image)

image.save(filename="_00.png")
