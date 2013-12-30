#!/usr/bin/python

import argparse
import sys
import yaml
import re

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.display import display

#full_text = ["The first line", "and a second line", "... finally a third line."]
full_text = ["The first line"]
FONT_SIZE = 48

dummy_image = Image(width=100, height=100, background=Color('black'))
draw = Drawing()
draw.font = '/Users/zastre/Dev/fimsi/sandbox/fonts/LatoOFL/TTF/Lato-Reg.ttf'
draw.font_size = FONT_SIZE
draw.fill_color = Color('black')


rendered_segments = []
for text in full_text:
    metrics = draw.get_font_metrics(dummy_image, text, False)
    yMax = int(metrics.y2)
    yMin = -1 * int(metrics.y1)
    segment_width = int(metrics.text_width)
    draw = Drawing()
    draw.font = '/Users/zastre/Dev/fimsi/sandbox/fonts/LatoOFL/TTF/Lato-Reg.ttf'
    draw.font_size = FONT_SIZE
    draw.fill_color = Color('black')
    draw.text(0, yMax, text)
    image = Image(width=segment_width, height=yMax+yMin, background=None)
    draw(image)
    rendered_segments.append((image, yMax, yMin))

line_spacing = FONT_SIZE * 1.1
(_, yMax, _) = rendered_segments[0]
(_, _, yMin) = rendered_segments[-1]
final_height = (len(rendered_segments) - 1) * line_spacing + yMax + yMin
final_width  = max([i.width for (i, _, _) in rendered_segments])

final_image = Image(width=int(final_width), height=int(final_height),
    background=Color('white'))

(_,top_offset,_) = rendered_segments[0]
for segment in rendered_segments:
    (image, yMax, _) = segment
    final_image.composite(image, 0, int(top_offset - yMax))
    top_offset = top_offset + line_spacing 

final_image.save(filename="_00.png")
