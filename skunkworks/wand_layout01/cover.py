#!/usr/bin/python

#
# November 2, 2013
#
# Port of shell-script "build.sh" from October 5, 2013.
#
# A bit of a hack with a total absence of re-factoring
# effort. However, the architecture of the code closely follows
# what was in the script. Some workarounds were used to
# provide for functionality not yet in Wand.
#
# Yeah, and this long comment sucks-and-blows because
# it isn't in a Python docstring.  I get it.  Future
# version will hew more closely to PEP 8.
#
# MJZ
#

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.display import display

IMAGE_PATH = "/Users/zastre/Dev/fimsi/sandbox/images/"
FONT_PATH = "/Users/zastre/Dev/fimsi/sandbox/fonts/"

FONT_REGULAR = FONT_PATH + "arvo/Arvo-Regular.ttf"
FONT_ITALIC = FONT_PATH + "arvo/Arvo-Italic.ttf"
FONT_BOLD = FONT_PATH + "arvo/Arvo-Bold.ttf"

def slice00():
    req_width = 595
    req_height = 35
    euro_img = Image(filename = IMAGE_PATH + "euros.png")
    euro_img = resize_to_height(euro_img, req_height)

    mask_img = new_blank_png(width=req_width, height=req_height, 
        color=Color('rgb(150,150,150)'))
    background_img = new_blank_png(width=req_width, 
        height=req_height, color=Color('rgb(44,128,64)'))
   
    euro_img.composite_channel(channel='all_channels', image=mask_img, 
        operator='copy_opacity')
    background_img.composite(euro_img, 0, 0)

    return background_img

    
def slice01():
    req_width = 595
    req_height = 139
    masthead_image = new_blank_png(req_width, req_height, Color('white'))

    # Cannot yet draw a rectangle. Therefore to get the collection of boxes
    # and their colours, we create images that are then composited.
    box1 = new_blank_png(384, 139, Color('rgb(192,30,45)'))
    box2 = new_blank_png(173, 139, Color('rgb(224,137,145)'))
    masthead_image.composite(box1, 0, 0)
    masthead_image.composite(box2, 384, 0)
    
    draw = Drawing()
    draw.font = FONT_BOLD
    draw.font_size = 72
    draw.fill_color = Color('white')
    draw.text(169, 82, "entre")
    draw.text(60, 124, "preneur")
    
    draw.font = "../fonts/arvo/Arvo-Regular.ttf"
    draw.font_size = 115
    draw.fill_color = Color('black')
    draw.text(390, 125, "2.0")
    
    draw(masthead_image)

    # Cannot yet rotate the text in the same step as the drawing,
    # so draw rectangle with text and then rotate it.
    #
    box3 = new_blank_png(139, 39, Color('rgb(192,30,45)'))
    draw = Drawing()
    draw.font = "../fonts/arvo/Arvo-Regular.ttf"
    draw.font_size = 17
    draw.fill_color = Color('white')
    draw.text(5, 25, "November 2013")
    draw(box3)
    box3.rotate(-90)
    masthead_image.composite(box3, 557, 0)

    return masthead_image


def slice02():
    # Resize image to height (but do not change the aspect ratio)
    #
    req_width = 595
    req_height = 486
    baby_img = Image(filename=IMAGE_PATH + "baby_cc_sh.png")
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
    left_field = new_blank_png(230, req_height, Color('white'))
    right_field = new_blank_png(290, req_height, Color('black'))
    opacity_mask.composite(left_field, 0, 0)
    opacity_mask.composite(right_field, 230+75, 0)
    opacity_mask.composite(gradient_img, 230, 0)

    # Now take the resized baby image and have it fade to the right
    # (in order to blend with later operations).
    #
    face_img = new_blank_png(req_width, req_height)
    face_img.composite(baby_img, 0, 0)
    face_img.composite_channel(channel='all_channels', image=opacity_mask, 
        operator='copy_opacity')

    # Bring in the illustrative image that will eventually be blended in
    # with the child's face.
    #
    accent_img = Image(filename = IMAGE_PATH + "funky_illustration.png")
    accent_img = resize_to_percent(accent_img, 60)
    accent_img = resize_to_height(accent_img, 486)

    cropped_img = accent_img.clone()
    cropped_img.crop(top=0, left=275, width=340, height=486)
    screen_img = new_blank_png(340, 486, color=Color('rgb(150,150,150)'))
    cropped_img.composite_channel(channel='all_channels', image=screen_img, 
        operator='screen')

    accent_img = new_blank_png(req_width, req_height)
    accent_img.composite_channel(channel='all_channels', image=cropped_img, 
        operator='over', left=255, top=0)
    accent_img.gaussian_blur(3.0, 1.0)

    opacity_mask = new_blank_png(req_width, req_height, color=Color('white'))
    left_field = new_blank_png(260, req_height, Color('black'))
    right_field = new_blank_png(290, req_height, Color('white'))
    opacity_mask.composite(left_field, 0, 0)
    opacity_mask.composite(right_field, 260+75, 0)
    gradient_img.rotate(180)
    opacity_mask.composite(gradient_img, 260, 0)
    accent_img.composite_channel(channel='all_channels', image=opacity_mask, 
        operator='copy_opacity')

    # Now layer the accent image with the child's face
    #
    accent_img.composite_channel(channel='all_channels', image=face_img,
        operator='over')
    full_slice = accent_img 

    # Finally, add the text field on the right of the image.
    #
    text_field = new_blank_png(212, req_height, color=Color('rgb(190,30,45)'))
    text_field_mask = new_blank_png(212, req_height, color=Color('rgb(220,220,220)'))
    text_field.composite_channel(channel='all_channels', image=text_field_mask, 
        operator='copy_opacity')
    full_slice.composite(text_field, 384, 0)

    draw = Drawing()
    draw.font = FONT_BOLD
    draw.font_size = 24
    draw.fill_color = Color('white')
    draw.text(395, 175, "Liam Mulcahy")
    draw.font = FONT_REGULAR
    draw.font_size = 20
    draw.text(395, 200, "Eyes to the Future")
    draw.font = FONT_ITALIC
    draw.font_size = 20
    draw.text(395, 250, 'How dreams of')
    draw.text(395, 275, 'future enterprise')
    draw.text(395, 300, 'success are')
    draw.text(395, 325, 'starting while still')
    draw.text(395, 350, 'in nappies!')
    draw(full_slice)
   
    # Done.
    # 
    return full_slice


def slice03():
    full_slice = new_blank_png(595, 182)

    # Two solid-colour areas, one on left and one on right
    #
    left_field = new_blank_png(299, 182, color=Color('rgb(44,128,64)'))
    right_field = new_blank_png(297, 182, color=Color('rgb(127,184,141)'))
    full_slice.composite(left_field, 0, 0)
    full_slice.composite(right_field, 299, 0)
   
    draw = Drawing()

    # Text on the left field
    #
    draw.font = FONT_BOLD
    draw.font_size = 18
    draw.fill_color = Color('white')
    draw.text(30, 85, "Smartphone Babyproofing")

    # Unfortunately don't yet have strokewidth
    #
    draw.line((29,95), (298,95))
    draw.line((29,96), (298,96))
    draw.line((29,97), (298,97))

    draw.font = FONT_REGULAR
    draw.font_size = 18
    draw.text(30, 125, "Tips on how to use those")
    draw.text(30, 147, "safety features you")
    draw.text(30, 169, "always forget to enable...")

    # Text on the right field
    #
    draw.font = FONT_BOLD
    draw.font_size = 18
    draw.fill_color = Color('black')
    draw.text(328, 85, "School savings")

    # Yada yada yada ...
    #
    draw.line((328,95), (595,95))
    draw.line((328,96), (595,96))
    draw.line((328,97), (595,97))

    draw.font = FONT_REGULAR
    draw.font_size = 18
    draw.text(328, 125, "Successful $$$ strategies")  ## Still have euro-symbol issues
    draw.text(328, 147, "for getting junior into the")
    draw.text(328, 169, "best business school")

    # ... and now drawing the text 
    #
    draw(full_slice)

    # Add the accent images on top
    #
    graphics_slice = new_blank_png(595, 182)
    
    left_image = Image(filename = IMAGE_PATH + "smartphone.png")
    left_image = resize_to_width(left_image, 299)

    right_image = Image(filename = IMAGE_PATH + "building.png")
    right_image = resize_to_width(right_image, 298)

    graphics_slice.composite(left_image, 0, 0)
    graphics_slice.composite(right_image, 299, 0)
    opacity_mask = new_blank_png(595, left_image.height, color=Color('rgb(75,75,75)'))
    graphics_slice.composite_channel(channel='all_channels', image=opacity_mask, 
        operator='copy_opacity')

    full_slice.composite_channel(channel='all_channels', image=graphics_slice, 
        operator='over', top=0, left=0)
 
    # Done.
    #
    return full_slice


# Only way to create a blank image in PNG format it seems. Without the
# "convert", crap happens.
#
def new_blank_png(width, height, color=None):
    if color:
        new_img = Image(width=width, height=height, background=color)
    else:
        new_img = Image(width=width, height=height)

    return new_img.convert('png')
   

# Resize to match the new height, but keep the original
# aspect ratio of the image the same as the old.
# 
def resize_to_height(source_img, new_h):
    source_h = source_img.height
    source_w = source_img.width
    scale_factor = float(new_h) / float(source_h)
    new_w = int(source_w * scale_factor)

    result_img = source_img.clone()
    result_img.resize(new_w, new_h)
    return result_img


# Resize to match the new width, but keep the original
# aspect ratio of the image the same as the old.
# 
def resize_to_width(source_img, new_w):
    source_h = source_img.height
    source_w = source_img.width
    scale_factor = float(new_w) / float(source_w)
    new_h = int(source_h * scale_factor)

    result_img = source_img.clone()
    result_img.resize(new_w, new_h)
    return result_img


def resize_to_percent(image, percent):
    ratio = float(percent)/100
    width = image.width
    height = image.height

    image.resize(int(width * ratio), int(height * ratio))
    return image


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
    temp = temp + stringify_chunk("IHDR", struct.pack("!2I5B", width, 
        height, 8, 2, 0, 0, 0))
    temp = temp + stringify_chunk("IDAT", get_data(width, height, rgb_func))
    temp = temp + stringify_chunk("IEND", "")
    return temp


def linear_gradient(start_value, stop_value, start_offset=0.0, stop_offset=1.0):
    return lambda offset: (start_value + ((offset - start_offset) / 
        (stop_offset - start_offset) * (stop_value - start_value))) / 255.0


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

#
# End of gradient code
#


def debug_image(image, text):
    print "DEBUG ", text, image.width, image.height


def main():
    slice00_img = slice00()
    slice01_img = slice01()
    slice02_img = slice02()
    slice03_img = slice03()

    full_image = new_blank_png(595, 842)
    full_image.composite(slice00_img, 0, 0)
    full_image.composite(slice01_img, 0, 35)
    full_image.composite(slice02_img, 0, 174)
    full_image.composite(slice03_img, 0, 660)

    full_image.save(filename="final.png")


if __name__ == "__main__":
    main()
