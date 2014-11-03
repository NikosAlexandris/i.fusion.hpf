# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 16:35:35 2014

@author: nik
"""


class Filter:
    """Based on a suitable Kernel string, this class creates a
    filter suitable for GRASS-GIS' r.mfilter module.
    A UNIX ASCII file whose contents is a matrix defining the way
    in which the input file (for r.mfilter) will be filtered. The
    format of this file is described in r.mfilter's manual."""
    def __init__(self, kernel, divisor=1, type='P'):
        self.header = 'MATRIX    ' + str(kernel.size)
        self.kernel = kernel.kernel
        self.size = kernel.size
        self.divisor = 'DIVISOR   ' + str(divisor)
        self.type = 'TYPE      ' + str(type)
        self.footer = str(self.divisor) + '\n' + self.type

        self.filter = ''
        self.filter += self.header + '\n'
        self.filter += self.kernel + '\n'
        self.filter += self.footer

    def set_divisor(self, divisor):
        self.divisor = divisor

    def set_type_(self, type):
        self.type = type

    def __str__(self):
        return "Filter:\n" + self.filter
