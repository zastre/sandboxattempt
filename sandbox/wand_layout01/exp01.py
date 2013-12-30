#!/usr/bin/python

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.display import display

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


def main():
    req_width = 595
    req_height = 486
    baby_img = Image(filename="baby_cc_sh.png")
    baby_img = resize_to_height(baby_img, req_height)

    temp_img = new_blank_png(req_width, req_height)
    temp_img.composite(baby_img, 0, 0)
    baby_img = temp_img

    mask_img = new_blank_png(req_width, req_height, color=Color('rgb(32,32,32)'))
    mask_img.save(filename="mask_img.png")

    print "DEBUG baby_img", baby_img.alpha_channel
    print "DEBUG mask_img", mask_img.alpha_channel

    baby_img_masked = baby_img.clone()
    baby_img_masked.composite_channel(channel='all_channels', image=mask_img, operator='copy_opacity')

    display(baby_img)
    display(baby_img_masked)

    baby_img.save(filename="baby_img.png")
    baby_img_masked.save(filename="baby_img_masked.png")

if __name__ == '__main__':
    main()
