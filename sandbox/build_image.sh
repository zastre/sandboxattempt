#!/bin/bash

CONVERT_BIN=/opt/local/bin/convert

$CONVERT_BIN -size 400x100 xc:black \
    -fill red1 -draw 'rectangle 0,0 50,100' \
    -fill red2 -draw 'rectangle 50,0, 100,100' \
    -fill red3 -draw 'rectangle 100,0, 150,100' \
    -fill red4 -draw 'rectangle 150,0 200,100' \
    -fill red1 -draw 'rectangle 200,0 250,100' \
    -fill red2 -draw 'rectangle 250,0 300,100' \
    -fill red3 -draw 'rectangle 300,0 350,100' \
    -fill red4 -draw 'rectangle 350,0 400,100' \
    image.png
