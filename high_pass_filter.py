#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Nikos Alexandris | Created on 13:02:59, Nov 3 2014
"""

import os
from constants import MATRIX_PROPERTIES, CENTER_CELL, MODULATOR, MODULATOR_2


def get_kernel_size(ratio):
    """
    High Pass Filter Additive image fusion compatible kernel size.
    Based on a float ratio, ranging in (1.0, 10.0).
    Returns a single integer
    """
    kernel_size = [k for ((lo, hi), k) in MATRIX_PROPERTIES if lo <= ratio < hi][0]
    return kernel_size


def get_center_cell(level, kernel_size):
    """
    High Pass Filter Additive image fusion compatible kernel center
    cell value.
    """
    level = level.capitalize()
    kernel_size_idx = [k for ((lo, hi), k) in MATRIX_PROPERTIES].index(kernel_size)
    center = [cc for cc in CENTER_CELL[level]][kernel_size_idx]
    return center


def get_modulator_factor(modulation, ratio):
    """
    Return the modulation factor for the first pass of the
    HPFA Image Fusion Technique.

    The modulation factor determines the image's Cripsness.

    Parameters
    ----------
    modulation: str
        Possible values are: `"min", "mid", max"`.
    ratio: int
        The resolution ratio between the high resolution pancrhomatic data
        and the lower resolution spectral data.

    Returns
    -------
    modulation_factor: float

    """
    kernel_size = get_kernel_size(ratio)
    kernel_size_idx = [k for ((lo, hi), k) in MATRIX_PROPERTIES].index(kernel_size)
    modulation = modulation.capitalize()
    modulation_factor = [mf for mf in MODULATOR[modulation]][kernel_size_idx]
    return modulation_factor


def get_modulator_factor2(modulation):
    """
    Return the modulation factor for the second pass of the HPFA Image Fusion Technique.

    The modulation factor determines the image's Cripsness.

    Parameters
    ----------
    modulation: str
        Possible values are: `"min", "mid", max"`.

    Returns
    -------
    modulation_factor: float

    """
    modulation = modulation.capitalize()
    modulation_factor = MODULATOR_2[modulation]
    return modulation_factor



class Kernel(object):
    """
    HPF compatible Kernel (size), where size is odd | Returns multi-line string
    """
    def __init__(self, size, level):
        self.size = int(size)
        self.center = get_center_cell(level, self.size)
        self.kernel = ''

        # middle row
        midrow = (self.size/2)

        # loop over columns, return value for column, row
        for row in range(self.size):

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

    def __str__(self):
        return "Kernel:\n" + self.kernel


class High_Pass_Filter(object):
    """
    Based on a suitable Kernel string, this class creates a
    filter suitable for GRASS-GIS' r.mfilter module.
    Returns a *NIX ASCII multi-line string whose contents is
    a matrix defining the way in which raster data will be filtered
    by r.mfilter. The format of this file is described in r.mfilter's
    manual.
    """
    def __init__(self, ratio, level='Low', divisor=1, type='P'):

        # parameters
        self.ratio = ratio
        self.size = get_kernel_size(self.ratio)

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
