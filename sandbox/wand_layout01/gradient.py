#!/usr/bin/python

import sys
import zlib
import struct
import array

def output_chunk(out, chunk_type, data):
    out.write(struct.pack("!I", len(data)))
    out.write(chunk_type)
    out.write(data)
    checksum = (zlib.crc32(data, zlib.crc32(chunk_type))) & 0xffffffff
    out.write(struct.pack("!I", checksum))


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


def write_png(filename, width, height, rgb_func):
    out = open(filename, "w")
    out.write(struct.pack("8B", 137, 80, 78, 71, 13, 10, 26, 10))
    output_chunk(out, "IHDR", struct.pack("!2I5B", width, height, 8, 2, 0, 0, 0))
    output_chunk(out, "IDAT", get_data(width, height, rgb_func))
    output_chunk(out, "IEND", "")
    out.close()


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


write_png("test2.png", 500, 200, gradient([
    (0.43, (0xBF, 0x94, 0xC0), (0x4C, 0x26, 0x4C)), # top
    (0.83, (0x4C, 0x26, 0x4C), (0x27, 0x13, 0x27)), # bottom
    (1.0,  (0x66, 0x66, 0x66), (0xFF, 0xFF, 0xFF)), # shadow
]))

write_png("test3.png", 500, 200, gradient([
    (1.0, (0x00, 0x00, 0x00), (0xFF, 0xFF, 0xFF)), # top
    (1.0, (0x4C, 0x26, 0x4C), (0x27, 0x13, 0x27)), # bottom
    (1.0,  (0x66, 0x66, 0x66), (0xFF, 0xFF, 0xFF)), # shadow
]))
