#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Selecting an appropriate kernel size for a matrix
#   within the context of the HPFA image fusion technique

# Nikos Alexandris
# Trikala, October 2014

# source(s): ?

# required librairies, CONSTANTS
from random_ratio import main as ratio_random
from constants import MATRIX_PROPERTIES


# get a random ratio
rr = ratio_random()  # ; print "Random Ratio:", rr


def kernel_size(rr):
    """Select High Pass Filter Kernel size | Function returns a single integer"""
    ks = [k for ((lo, hi), k) in MATRIX_PROPERTIES if lo <= rr < hi]
    return ks[0]


# make it both a reusable module and a stand-alone utility
# make script importable and executable
if __name__ == "__main__":
    kernel_size(rr)
