#!/usr/bin/python

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.display import display


# Only way to create a blank image in PNG format it seems. Without the
# "convert", crap happens.
#

def new_blank_png(new_width, new_height):
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


def main():
    req_width = 595
    req_height = 486
    baby_img = Image(filename="baby_cc_sh.png")
    baby_img = resize_to_height(baby_img, req_height)

    baby_img.flop()

    full_img = new_blank_png(req_width, req_height)
    full_img.composite(baby_img, 0, 0)

    display(full_img)


if __name__ == "__main__":
    main()
