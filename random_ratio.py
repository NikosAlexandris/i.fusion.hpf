#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Generate random ratio for testing purposes
within the context of the HPFA image fusion technique
"""

# Nikos Alexandris
# Trikala, October 2014

# source(s):
    # missing link to stack exchange!

# import required librairies, CONSTANTS
import random
from constants import RATIO_RANGES


def main():
    """helper function, generating a random ratio"""
    ratio_low = min(RATIO_RANGES[0])  # ; print ratio_low
    ratio_high = min(RATIO_RANGES[-1]) + 0.5  # ; print ratio_high
    ratio_width = ratio_high - ratio_low  # ; print ratio_width
    ratio_random = round(random.random() * ratio_width + ratio_low, 1)
    return ratio_random  # ; print "Ratio (Random):", ratio_random

# make it both a reusable module and a stand-alone utility
# make script importable and executable
if __name__ == "__main__":
    main()

## demo?
#print main()
