#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  3 12:47:42 2014

@author: Nikos Alexandris | Trikala, November 2014
"""

from constants import MATRIX_PROPERTIES, CENTER_CELL


def kernel_size(ratio):
    """High Pass Filter Additive image fusion compatible kernel size.
    Based on a random ratio float ranging in [1.0, inf).
    Returns a single integer"""
    ks = [k for ((lo, hi), k) in MATRIX_PROPERTIES if lo <= ratio < hi]
    return ks[0]

def center_cell(level, ks):
    """ """
    ks_idx = [k for ((lo, hi), k) in MATRIX_PROPERTIES].index(ks)
    center = [cc for cc in CENTER_CELL[level]][ks_idx]
    return center

def input_parameters():
    ratio = input("Provide a  <Ratio>  ranging in [1.0, inf): ")
    level = 'Default'
    level = raw_input("Set level for center cell value (Default, Mid or High): ")
    
    ks = kernel_size(ratio)
    center = center_cell(level, ks)
    
    print
    print "Kernel Size: ", ks
    print "Center Cell value: ", center 


# reusable & stand-alone
if __name__ == "__main__":
    print "Selecting an appropriate High Pass Filter kernel size"
    print "    (Running as stand-alone tool)\n"
    input_parameters()
