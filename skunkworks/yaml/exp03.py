#!/usr/bin/python

import argparse
import sys
import yaml
import re

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.display import display

weight_sequence = ['ultralight', 'light',
    'regular', 'bold', 'black']

image_width = 400
image_height = 60

dummy_image = Image(width=image_width, height=image_height, background=Color('white'))

draw = Drawing()
draw.font = '/Users/zastre/Dev/fimsi/sandbox/fonts/LatoOFL/TTF/Lato-Reg.ttf'
draw.font_size = 36
draw.fill_color = Color('black')
metrics_01 = draw.get_font_metrics(dummy_image, "21", False)

draw.font = '/Users/zastre/Dev/fimsi/sandbox/fonts/LatoOFL/TTF/Lato-Bla.ttf'
draw.font_size = 36
draw.fill_color = Color('black')
metrics_02 = draw.get_font_metrics(dummy_image, "CV", False)

image_01 = Image(width=int(metrics_01.text_width),
    height=int(metrics_01.text_height), background=None)
draw_01 = Drawing()
draw_01.font = '/Users/zastre/Dev/fimsi/sandbox/fonts/LatoOFL/TTF/Lato-Reg.ttf'
draw_01.font_size = 36
draw_01.fill_color = Color('black')
draw_01.text(0, int(metrics_01.text_height), "21")
draw_01(image_01)

image_02 = Image(width=int(metrics_02.text_width),
    height=int(metrics_02.text_height), background=None)
draw_02 = Drawing()
draw_02.font = '/Users/zastre/Dev/fimsi/sandbox/fonts/LatoOFL/TTF/Lato-Bla.ttf'
draw_02.font_size = 36
draw_02.fill_color = Color('black')
draw_02.text(0, int(metrics_02.text_height), "CV")
draw_02(image_02)

image = Image(width=int(metrics_01.text_width + metrics_02.text_width),
    height=int(metrics_02.text_height), background=None)
image.composite(image_01, 0, 0)
image.composite(image_02, int(metrics_01.text_width), 0)

image.save(filename="_00.png")
