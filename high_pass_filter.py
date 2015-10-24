#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Nikos Alexandris | Created on 13:02:59, Nov 3 2014
"""

import os
from constants import MATRIX_PROPERTIES, CENTER_CELL, MODULATOR, MODULATOR_2


def kernel_size(ratio):
    """
    High Pass Filter Additive image fusion compatible kernel size.
    Based on a float ratio, ranging in (1.0, 10.0).
    Returns a single integer
    """
    ks = [k for ((lo, hi), k) in MATRIX_PROPERTIES if lo <= ratio < hi]
    return ks[0]  # ks: kernel size, as integer?


def center_cell(level, ks):
    """
    High Pass Filter Additive image fusion compatible kernel center
    cell value.
    """
    level = level.capitalize()
    ks_idx = [k for ((lo, hi), k) in MATRIX_PROPERTIES].index(ks)
    center = [cc for cc in CENTER_CELL[level]][ks_idx]
    return center


def modulator(modulation, modulation2, ks, second_pass):
    """
    Returning a modulation factor determining image Cripsness
    """
    ks_idx = [k for ((lo, hi), k) in MATRIX_PROPERTIES].index(ks)
    if second_pass:
        modulation2 = modulation2.capitalize()
        modfac = MODULATOR_2[modulation2]
    else:
        modulation = modulation.capitalize()
        modfac = [mf for mf in MODULATOR[modulation]][ks_idx]
    return modfac


class Kernel:
    """
    HPF compatible Kernel (size), where size is odd | Returns multi-line string
    """
    def __init__(self, size, level):
        self.size = int(size)
        self.center = center_cell(level, self.size)
        self.kernel = ''

        # loop over columns, return value for column, row
        for row in range(self.size):

            # middle row
            midrow = (self.size/2)

            # fill rows
            if row != self.size/2:
                self.kernel += "-1 " * self.size + "\n"

            # fill mid row
            else:

                # single-digit center?
                if len(str(self.center)) == 1:
                    self.center = " " + str(self.center)

                # prettier output for double-digit or larger center
                self.kernel += "-1 " * midrow + str(self.center) + \
                    " " + "-1 " * midrow + "\n"

        # remove trailing spaces
        self.kernel = os.linesep.join([s.rstrip()
                                       for s in self.kernel.splitlines()
                                       if s])

    def size(self):
        return self.size

    def center(self):
        return self.center

    def __str__(self):
        return "Kernel:\n" + self.kernel


class High_Pass_Filter:
    """
    Based on a suitable Kernel string, this class creates a
    filter suitable for GRASS-GIS' r.mfilter module.
    Returns a *NIX ASCII multi-line string whose contents is
    a matrix defining the way in which raster data will be filtered
    by r.mfilter. The format of this file is described in r.mfilter's
    manual.
    """
    def __init__(self,
                 ratio,
                 level='Low',
                 modulation='Mid',
                 second_pass=False,
                 modulation2='Min',
                 divisor=1,
                 type='P'):

        # parameters
        self.ratio = ratio
        self.size = kernel_size(self.ratio)

        if second_pass:
            self.modulator_2 = modulator(None, modulation2, self.size, True)
        else:
            self.modulator = modulator(modulation, None, self.size, False)

        # build kernel
        self.kernel = Kernel(self.size, level).kernel
        self.header = 'MATRIX    ' + str(self.size)
        self.divisor = 'DIVISOR   ' + str(divisor)
        self.type = 'TYPE      ' + str(type)
        self.footer = str(self.divisor) + '\n' + self.type

        # build filter
        self.filter = ''
        self.filter += self.header + '\n'
        self.filter += self.kernel + '\n'
        self.filter += self.footer

    def __str__(self):
        return "Filter:\n" + self.filter

# reusable & stand-alone
if __name__ == "__main__":
    print "Constructing a Filter for the HPFA Image Fusion Technique"
    print "    (Running as stand-alone tool)\n"
