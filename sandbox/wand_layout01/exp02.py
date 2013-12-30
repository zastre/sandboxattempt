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


def resize_to_percent(image, percent):
    ratio = float(percent)/100
    width = image.width
    height = image.height
    
    image.resize(int(width * ratio), int(height * ratio))
    return image     


def main():
    funky_img = Image(filename="../images/funky_illustration.png")
    funky_img = resize_to_percent(funky_img, 60)

    cropped_img = funky_img.clone()
    cropped_img.crop(top=0, left=275, width=340, height=486)

    display(funky_img)
    display(cropped_img)


if __name__ == '__main__':
    main()
