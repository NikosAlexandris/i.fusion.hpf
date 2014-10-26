#!/usr/bin/env python
#-*- coding:utf-8 -*-

# ratio ranges
RATIO_RANGES = (
    (1, 2.5),\
    (2.5, 3.5),\
    (3.5, 5.5),\
    (5.5, 7.5),\
    (7.5, 9.5),\
    (9.5, float('inf'))
    )

# kernel sizes
KERNEL_SIZES = (5, 7, 9, 11, 13, 15)

# center cell values per kernel sizes 
CENTER_CELL = {
    'Default' : [24, 48, 80, 120, 168, 336 ], \
    'Default 2':'24', \
    'Mid' : [ 28, 56, 96, 150, 210, 392 ], \
    'Mid 2':'28', \
    'High' : [ 32, 64, 106, 180, 252, 448 ], \
    'High 2':'32'
    }

MODULATOR = {
    'Min': [ 0.20, 0.35, 0.35, 0.50, 0.65, 1.00], \
    'Min 2':'0.25', \
    'Default': [ 0.25, 0.50, 0.50, 0.65, 1.00, 1.35], \
    'Default 2':'0.35', \
    'Max': [ 0.30, 0.65, 0.65, 1.00, 1.40, 2.00], \
    'Max 2': '0.50'
    }

#def main():
    #pass


# make script reusable and stand-alone utility
if __name__ == "__main__":
    main()