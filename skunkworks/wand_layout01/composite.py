#!/usr/bin/python

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.display import display


# Only way to create a blank image in PNG format it seems. Without the
# "convert", crap happens.
#

def main():

    # Resize image to height (but do not change the aspect ratio)
    #
    req_width = 595
    req_height = 486
    baby_img = Image(filename="baby_cc_sh.png")
    baby_img = resize_to_height(baby_img, req_height)

    # For this particular image, reflect image along vertical
    # axis to have face directed towards right of page.
    #
    baby_img.flop()

    # Create the the gradient transition that will later be used
    # in the opacity mask.
    #
    gradient_blob = create_gradient_blob(req_height, 75, gradient([
        (1.0, (0x00, 0x00, 0x00), (0xFF, 0xFF, 0xFF)), # top
    ]))
    gradient_img = Image(blob=gradient_blob)
    gradient_img.rotate(90.0)

    # When building the opacity mask, must start with an image
    # having a solid colour (i.e., begin as a "matte" image).
    # Without this, the later "composite_channel" operations
    # will simply not work.
    #
    opacity_mask = new_blank_png(req_width, req_height, color=Color('white'))
    white_field = new_blank_png(230, req_height, Color('white'))
    black_field = new_blank_png(290, req_height, Color('black'))
    opacity_mask.composite(white_field, 0, 0)
    opacity_mask.composite(black_field, 230+75, 0)
    opacity_mask.composite(gradient_img, 230, 0)

    # Now take the resized baby image and have it fade to the right
    # (in order to blend with later operations).
    #
    full_img = new_blank_png(req_width, req_height)
    full_img.composite(baby_img, 0, 0)
    full_img.composite_channel(channel='all_channels', image=opacity_mask, operator='copy_opacity')


def new_blank_png(new_width, new_height, color=None):
    if color:
        new_img = Image(width=new_width, height=new_height, background=color)
    else:
        new_img = Image(width=new_width, height=new_height)

    return new_img.convert('png')
   
 
def resize_to_height(source_img, new_h):
    source_h = source_img.height
    source_w = source_img.width
    scale_factor = float(new_h) / float(source_h)
    new_w = int(source_w * scale_factor)

    result_img = source_img.clone()
    result_img.resize(new_w, new_h)
    return result_img


def resize_to_width(source_img, new_w):
    source_h = source_img.height
    source_w = source_img.width
    scale_factor = float(new_w) / float(source_w)
    new_h = int(source_h * scale_factor)

    result_img = source_img.clone()
    result_img.resize(new_w, new_h)
    return result_img


#
# Some code for creating a gradient images.
# Largely based on James Tauber's code from 2008.
# http://jtauber.com/blog/2008/05/18/creating_gradients_programmatically_in_python/
#

import sys
import zlib
import struct
import array

def stringify_chunk(chunk_type, data):
    temp = struct.pack("!I", len(data))
    temp = temp + chunk_type
    temp = temp + data
    checksum = (zlib.crc32(data, zlib.crc32(chunk_type))) & 0xffffffff
    temp = temp + struct.pack("!I", checksum)
    return temp


def get_data(width, height, rgb_func):
    fw = float(width)
    fh = float(height)
    compressor = zlib.compressobj()
    data = array.array("B")
    for y in range(height):
        data.append(0)
        fy = float(y)
        for x in range(width):
            fx = float(x)
            data.extend([int(v * 255) for v in rgb_func(fx / fw, fy / fh)])
    compressed = compressor.compress(data.tostring())
    flushed = compressor.flush()
    return compressed + flushed


def create_gradient_blob(width, height, rgb_func):
    temp = struct.pack("8B", 137, 80, 78, 71, 13, 10, 26, 10)
    temp = temp + stringify_chunk("IHDR", struct.pack("!2I5B", width, height, 8, 2, 0, 0, 0))
    temp = temp + stringify_chunk("IDAT", get_data(width, height, rgb_func))
    temp = temp + stringify_chunk("IEND", "")
    return temp


def linear_gradient(start_value, stop_value, start_offset=0.0, stop_offset=1.0):
    return lambda offset: (start_value + ((offset - start_offset) / (stop_offset - start_offset) * (stop_value - start_value))) / 255.0


def gradient(DATA):
    def gradient_function(x, y):
        initial_offset = 0.0
        for offset, start, end in DATA:
            if y < offset:
                r = linear_gradient(start[0], end[0], initial_offset, offset)(y)
                g = linear_gradient(start[1], end[1], initial_offset, offset)(y)
                b = linear_gradient(start[2], end[2], initial_offset, offset)(y)
                return r, g, b
            initial_offset = offset
    return gradient_function


if __name__ == "__main__":
    main()
