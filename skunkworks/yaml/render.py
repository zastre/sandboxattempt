#!/usr/bin/python

import argparse
import sys
import yaml
import re

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.display import display

#
# There must be a better way to do this than to place it within the
# script itself. I'll refactor...
#

FONT_DIR = "/home/zastre/Dev/fimsi/sandbox/fonts/"
IMAGE_DIR = "/home/zastre/Dev/fimsi/sandbox/images/"
FONT_INFO = {
    'LatoOFL' : {
        'ultralight':FONT_DIR+'LatoOFL/TTF/Lato-Hai.ttf',
        'ultralight-italic':FONT_DIR+'LatoOFL/TTF/Lato-HaiIta.ttf',
        'light':FONT_DIR+'LatoOFL/TTF/Lato-Lig.ttf',
        'light-italic':FONT_DIR+'LatoOFL/TTF/Lato-LigIta.ttf',
        'regular':FONT_DIR+'LatoOFL/TTF/Lato-Reg.ttf',
        'regular-italic':FONT_DIR+'LatoOFL/TTF/Lato-RegIta.ttf',
        'bold':FONT_DIR+'LatoOFL/TTF/Lato-Bol.ttf',
        'bold-italic':FONT_DIR+'LatoOFL/TTF/Lato-BolIta.ttf',
        'black':FONT_DIR+'LatoOFL/TTF/Lato-Bla.ttf',
        'black-italic':FONT_DIR+'LatoOFL/TTF/Lato-BlaIta.ttf'
    },
    'Arvo' : {
        'ultralight':FONT_DIR+'arvo/Arvo-Regular.ttf',
        'ultralight-italic':FONT_DIR+'arvo/Arvo-Italic.ttf',
        'light':FONT_DIR+'arvo/Arvo-Regular.ttf',
        'light-italic':FONT_DIR+'arvo/Arvo-Italic.ttf',
        'regular':FONT_DIR+'arvo/Arvo-Regular.ttf',
        'regular-italic':FONT_DIR+'arvo/Arvo-Italic.ttf',
        'bold':FONT_DIR+'arvo/Arvo-Bold.ttf',
        'bold-italic':FONT_DIR+'arvo/Arvo-BoldItalic.ttf',
        'black':FONT_DIR+'arvo/Arvo-Bold.ttf',
        'black-italic':FONT_DIR+'arvo/Arvo-BoldItalic.ttf'
    }
}
PAGE_SIZE = {'a4':(595,842), 'letter':(612,792), 'default':(0,0)}
DUMMY_IMAGE = Image(width=1000, height=1000, background=Color('white'))
WEIGHT_SEQUENCE = ["(sentinel)", "ultralight", "light", "regular", "bold", "black"]
ESCAPE_CHAR = "^"
DEFAULT_FONT_SIZE = 18


def read_yaml(stream):
    try:
        layout_graph = yaml.load(stream)
        stream.close()
        return layout_graph
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
        return None
    except yaml.parser.ParserError as ype:
        mark = ype.problem_mark
        print "Error position (YAML parser): (%s:%s)" % (mark.line+1, mark.column+1)
        return None
    except yaml.scanner.ScannerError as yse:
        mark = yse.problem_mark
        print "Error position (YAML scanner): (%s:%s)" % (mark.line+1, mark.column+1)
        return None
    except:
        print "Unexpected error:", sys.exc_info()[0]
        return None


def new_blank_png(width, height, color=None):
    if color:
        new_img = Image(width=width, height=height, background=color)
    else:
        new_img = Image(width=width, height=height)
    return new_img.convert('png')


#
# This function depends heavily upon values returned by get_font_metrics
# * y2 == yMax for the given text
# * y1 == yMin for the given text (negative number)
# * therefore y2-y1 == the height in pixels for the given text.
# These are floating point numbers and must be converted into ints
# before being passed to image-creation routines.
#
# Each segment of the text will be in its own image, and different y2 and
# y1 values may have been involved for each. Therefore to compute the
# height of the final image, we need the largest yMax and the largest
# yMin and use these compute the final height.
#
# We must also keep track of the individual yMax values for each image
# and use it -- along with the maximum yMax of all the text segments --
# to determine far down the final image to composite the given text-segment
# image.
#
# For a bit more about ImageMagick and font metrics, look at:
#    http://www.imagemagick.org/Usage/text/#font_info
#
#
 
def render_text_line(text, font, size, weight, color=Color('none'), background=None):
    match = re.match("(\w+)(-\w+)?", weight)
    italic = None
    if match:
        weight = match.group(1)
        italic = match.group(2)
    if not italic:
        italic = ""

    #
    # Special case: blank line
    #
    if text == "":
        graphic = new_blank_png(width=5, height=5)
        return (5, 5, graphic)
    
    sequence = lex_line(text, weight)

    images = []
    dummy_image = Image(width=100, height=100, background=None)
    for (level, text) in sequence:
        draw = Drawing()
        draw.font = FONT_INFO[font][level+italic]
        draw.font_size = size
        draw.fill_color = color
        metrics = draw.get_font_metrics(dummy_image, text, False)
        image = new_blank_png(width=int(metrics.text_width), height=int(metrics.y2-metrics.y1))
        draw.text(0, int(metrics.y2), text)
        draw(image)
        images.append((metrics.y2, metrics.y1, image))

    if images == []:
        return None

    max_ascender = max([y2 for (y2,_,_) in images])
    max_descender = -1 * min([y1 for (_,y1,_) in images])
    final_image_width = sum([i.width for (_,_,i) in images])
    final_image_height = int(max_ascender + max_descender)
    final_image = new_blank_png(width=final_image_width, height=final_image_height,
        color=background)

    top_offset = 0
    for (y2,y1,i) in images:
        final_image.composite(i, top_offset, int(max_ascender-y2))
        top_offset = top_offset + i.width

    return (max_ascender, max_descender, final_image)


def lex_line(source_text, weight):
    weight_index = 0
    if weight in WEIGHT_SEQUENCE:
        weight_index = WEIGHT_SEQUENCE.index(weight)
    if weight_index == 0:
        return [(weight, source_text)]

    result = []
    level = weight_index
    incrementing = decrementing = escaped = False
    sequence = ""

    for letter in source_text:
        if letter != ESCAPE_CHAR:
            sequence = sequence + letter
            if incrementing:
                (incrementing, escaped) = (False, True)
            if decrementing:
                (decrementing, escaped) = (False, False)
            continue

        # If we reach this point, it is because the current
        # letter is the escape char...
        #

        if not incrementing and not decrementing and sequence != "":
            result.append((level, sequence))

        sequence = ""
        if not escaped:
            incrementing = True
        else:
            decrementing = True

        if incrementing:
            level = level + 1
            continue

        if decrementing:
            level = level - 1
            continue

    if sequence != "":
        result.append((level, sequence)) 

    result = [(min(level, len(WEIGHT_SEQUENCE)-1), text) 
                for (level, text) in result]
    result = [(WEIGHT_SEQUENCE[level], text) for (level, text) in result]

    return result


def render_multiple_textlines(textlines, font, size, weight, color=None, background=None):
    rendered_segments = [ render_text_line(t, font, size, weight, color, None) 
        for t in textlines ]
    line_spacing = size * 1.1
    (yMax, _, _) = rendered_segments[0]
    (_, yMin, _) = rendered_segments[-1]
    final_height = (len(rendered_segments) - 1) * line_spacing + yMax + yMin
    final_width  = max([i.width for (_, _, i) in rendered_segments])

    graphic = new_blank_png(width=int(final_width), height=int(final_height),
        color=background)

    (top_offset,_,  _) = rendered_segments[0]
    for segment in rendered_segments:
        (yMax, _, image) = segment
        graphic.composite(image, 0, int(top_offset - yMax))
        top_offset = top_offset + line_spacing

    return graphic


def make_layer_text(layer_info, font_family):
    text = layer_info['text']

    if text == None:
        text = ""

    if ('text-color' in layer_info.keys()):
        text_color = layer_info['text-color']
    else:
        text_color = 'black'

    if ('text-size' in layer_info.keys()):
        text_size = int(layer_info['text-size'])
    else:
        text_size = DEFAULT_FONT_SIZE

    if ('text-weight' in layer_info.keys()):
        text_weight = layer_info['text-weight']
    else:
        text_weight = 'regular'

    if ('box-size' in layer_info.keys() and 'box-color' in layer_info.keys()):
        box_color = Color(layer_info['box-color'])
    else:
        box_color = None


    text = text.split("\n")
    if len(text) > 1 and text[-1] == "":
        text = text[:-1]

    text_graphic = render_multiple_textlines(text, font_family, text_size,
        text_weight, Color(text_color), None) 

    if ('box-size' in layer_info.keys()):
        seq = layer_info['box-size'].split()
        seq = [int(num) for num in seq]
        (box_width, box_height) = tuple(seq)
        if ('box-color' in layer_info.keys()):
            graphic = new_blank_png(box_width, box_height, Color(layer_info['box-color']))
        else:
            graphic = new_blank_png(box_width, box_height)
        left_offset = int((box_width - text_graphic.width)/2)
        top_offset = int((box_height - text_graphic.height)/2)
        if (left_offset < 0):
            left_offset = 0
            print "WARNING: overfull layer --", layer_info['name']
        if (top_offset < 0):
            top_offset = 0
            print "WARNING: overfull layer --", layer_info['name']
        graphic.composite(text_graphic, left_offset, top_offset)
    else:
        graphic = text_graphic

    return graphic

    
def make_layer_image(layer_info):
    image_name = layer_info['image']
    graphic = Image(filename = IMAGE_DIR + image_name)
    return graphic


def make_layer(layer_info, font_family):
    if ('text' in layer_info.keys()):
        graphic = make_layer_text(layer_info, font_family)
    elif ('image' in layer_info.keys()):
        graphic = make_layer_image(layer_info)
    else:
        graphic = new_blank_png(100, 100, Color('blue'))

    # Was there any padding??
    #
    if ('padding' in layer_info.keys()):
        seq = layer_info['padding'].split()
        (top_offset, pad_r, pad_b, left_offset) = tuple([int(num) for num in seq])
        old_graphic = graphic
        old_width  = old_graphic.width
        new_width  = old_width + pad_r + left_offset
        old_height = old_graphic.height
        new_height = old_height + top_offset + pad_b
        if 'box-color' in layer_info.keys():
            new_graphic = Image(width=new_width, height=new_height,
                background=Color(layer_info['box-color']))
        else:
            new_graphic = Image(width=new_width, height=new_height,
                background=None)
        new_graphic.composite(old_graphic, left_offset, top_offset)
        graphic = new_graphic

    # Was there an opacity setting??
    #
    if ('opacity' in layer_info.keys()):
        val = layer_info['opacity']
        match = re.match(r"(\d*(\.d*)?)%$", val)
        if match:
            p = float(match.group(1))
            p = p / 100.0
            gs = int(255 * p)
            color_string = "rgb(%d,%d,%d)" % (gs, gs, gs)
            opacity_mask = Image(width=graphic.width, height=graphic.height,
                background=Color(color_string))
            graphic.composite_channel(channel='all_channels', image=opacity_mask,
                operator='copy_opacity')
                
    return graphic


def make_layers(layout):
    if ('size' in layout.keys() and layout['size'] in PAGE_SIZE.keys()):
        (width, height) = PAGE_SIZE[layout['size']]
    else:
        (width, height) = PAGE_SIZE['default']

    if ('font-family' in layout.keys() and layout['font-family'] in FONT_INFO.keys()):
        font_family = layout['font-family']
    else:
        font_family = None

    images = []

    layers = layout['layers']

    for l in layers:
        image = make_layer(l, font_family)
        if not ('position' in l.keys()):
            image_info = ((width - image.width)/2, (height - image.height)/2)
            images.append((image_info, image))
            continue


        position = l['position'] 
        if position == 'bottom-left':
            row = height - image.height
            col = 0
        elif position == 'bottom-right':
            row = height - image.height
            col = width - image.width
        elif position == 'top-left':
            row = 0
            col = 0
        elif position == 'top-right':
            row = 0
            col = width - image.width
        elif re.match(r"\d+\s+\d+", position):
            seq = position.split()
            seq = [int(num) for num in seq]
            (row, col) = tuple(seq)
        else:
            col = (width - image.width)/2
            row = (height - image.height)/2
            
        image_info = (col, row)
        images.append((image_info, image))

    return ((width, height), images)


def composite_layers(dimensions, layers):
    (width, height) = dimensions
    final_image = new_blank_png(width, height, Color('black'))
    # final_image = new_blank_png(width, height)

    for l in layers:
        ((left_offset, top_offset), image) = l
        final_image.composite(image, left_offset, top_offset)

    return final_image


def save_image(final_image, output_stream):
    final_image.save(output_stream)


def main():
    parser = argparse.ArgumentParser(description="Render a fimsi layout.")
    parser.add_argument('infile', nargs='?', metavar='FILENAME', 
        type=argparse.FileType('r'), default=sys.stdin,
        help="YAML file with layout instructions")
    parser.add_argument('outfile', nargs='?', metavar='FILENAME', 
        type=argparse.FileType('w'), default=sys.stdout,
        help="Image file for output")
    args = parser.parse_args() 

    layout = read_yaml(args.infile)
    if not layout:
        print "Stopped processing..."
        sys.exit(1)
  
    (dims, layers) = make_layers(layout)
    final_image = composite_layers(dims, layers)
    save_image(final_image, args.outfile)
    

if __name__ == "__main__":
    main()
