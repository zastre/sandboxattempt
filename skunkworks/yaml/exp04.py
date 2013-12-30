#!/usr/bin/python

word = "21^^CV^^baby^you think?^"
#word = "^^21CV^^"

result = []
level = 0
incrementing = False
decrementing = False
escaped = False
sequence = ""
for letter in word:
    if letter != "^":
        sequence = sequence + letter
        if incrementing:
            incrementing = False
            escaped = True
        if decrementing:
            decrementing = False
            escaped = False
        continue

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
    if decrementing :
        level = level - 1
        continue

if sequence != "":
    result.append((level, sequence)) 

print result
