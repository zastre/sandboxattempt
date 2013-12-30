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

dummy_image = Image(width=image_width, height=image_height, background=Color('white'))

draw = Drawing()
draw.font = '/Users/zastre/Dev/fimsi/sandbox/fonts/LatoOTF/TTF/Lato-Reg.ttf'
draw.font_size = 36
draw.fill_color = Color('red')
metrics = draw.get_font_metrics(dummy_image, "losing photos", False)

image = Image(width=int(metrics.text_width), height=int(metrics.text_height),
    background=None)

draw.text(0, int(metrics.ascender), "losing photos")
draw(image)

image.save(filename="_00.png")
