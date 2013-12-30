#!/usr/bin/python

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.display import display

IMAGE_PATH = "/home/zastre/Dev/fimsi/sandbox/images/"
FONT_PATH = "/home/zastre/Dev/fimsi/sandbox/fonts/"

FONT_HAIRLINE = FONT_PATH + "LatoOFL/TTF/Lato-Hai.ttf"
FONT_LIGHT    = FONT_PATH + "LatoOFL/TTF/Lato-Lig.ttf"
FONT_REGULAR  = FONT_PATH + "LatoOFL/TTF/Lato-Reg.ttf"
FONT_ITALIC   = FONT_PATH + "LatoOFL/TTF/Lato-RegIta.ttf"
FONT_BOLD     = FONT_PATH + "LatoOFL/TTF/Lato-Bol.ttf"
FONT_BLACK    = FONT_PATH + "LatoOFL/TTF/Lato-Bla.ttf"


def layer00():
    req_width = 595
    req_height = 842 
    galaxies_image = Image(filename=IMAGE_PATH + "galaxies_resized.png")
    return galaxies_image


def layer01():
    req_width = 360
    req_height = 541
    subject_image = Image(filename=IMAGE_PATH + "baby_liam_masked_resized.png")
    subject_image = resize_to_height(subject_image, req_height)
    return subject_image 

def layer02():
    draw = Drawing()
    draw.font = FONT_REGULAR
    draw.font_size = 144
    draw.fill_color = Color('rgb(216,224,34)')
    draw.text(0, 120, "21")

    draw.font = FONT_BLACK
    draw.text(170, 120, "CA")

    draw.font = FONT_BOLD
    draw.font_size = 18
    draw.text(480, 30, "2014/01")
   
    draw.font = FONT_REGULAR
    draw.font_size = 36
    draw.fill_color = Color('white')
    draw.text(0, 160, "twenty-first century astronomer")
 
    req_width = 570
    req_height = 170
    masthead_image = new_blank_png(req_width, req_height)
    draw(masthead_image)

#    opacity_mask = new_blank_png(570, 170, Color('rgb(200,200,200'))
#    masthead_image.composite_channel(channel='alpha', image=opacity_mask, operator='copy_opacity')

    return masthead_image


def layer03():
    draw = Drawing()
    draw.font = FONT_HAIRLINE
    draw.font_size = 69
    draw.fill_color = Color('white')
    draw.text(0, 69, "Liam Mulcahy")

    draw.font = FONT_LIGHT
    draw.font_size =50 
    draw.text(0, 125, "Our next Einstein?")
 
    req_width = 570
    req_height = 130
    blurb_image = new_blank_png(req_width, req_height)
    draw(blurb_image)

    return blurb_image


def layer04():
    req_width = 240
    req_height = 240
    contents_panel = new_blank_png(req_width, req_height,
        color=Color('rgb(254,233,229)'))

    opacity_mask = new_blank_png(req_width, req_height,
        Color('rgb(200,200,200'))
    contents_panel.composite_channel(channel='all_channels', 
        image=opacity_mask, operator='copy_opacity')

    return contents_panel
    

def layer05():
    req_width = 240
    req_height = 240
    contents_panel_text = new_blank_png(req_width, req_height)

    draw = Drawing()

    draw.font = FONT_BOLD
    draw.font_size = 18
    draw.fill_color = Color('black')
    draw.text(20, 45, "In this issue:")

    draw.font = FONT_ITALIC
    draw.font_size = 18
    draw.fill_color = Color('black')

    line_spacing = int(float(draw.font_size) * 1.22)
    (line_x, line_y) = (20, 81)
    lines = ["How to keep", "your toddler safe from",
        "unwanted event horizons",
        " ",
        "Best five telescopes", "for kids under six"]
    for l in lines:
        draw.text(line_x, line_y, l)
        line_y = line_y + line_spacing 

    draw(contents_panel_text)
    return contents_panel_text


def new_blank_png(width, height, color=None):
    if color:
        new_img = Image(width=width, height=height, background=color)
    else:
        new_img = Image(width=width, height=height)
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
    layer00_img = layer00()
    layer01_img = layer01()
    layer02_img = layer02()
    layer03_img = layer03()
    layer04_img = layer04()
    layer05_img = layer05()

    full_image = new_blank_png(595, 842)
    full_image.composite(layer00_img, 0, 0)
    full_image.composite(layer04_img, 0, 842-240+7)
    full_image.composite(layer05_img, 0, 842-240+7)
    full_image.composite(layer01_img, 237, 302)
    full_image.composite(layer02_img, 20, 20)
    full_image.composite(layer03_img, 20, 240)

    full_image.save(filename="final.png")

if __name__ == "__main__":
    main()
