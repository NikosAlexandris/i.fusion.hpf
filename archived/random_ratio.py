#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Nikos Alexandris | Trikala, October 2014
# source(s): missing link to stack exchange!

import random
from constants import RATIO_RANGES


def random_ratio():
    """Generate a random ratio float, ranging in (1.0, 10.0),
    for testing purposes within the context of
    the HPFA image fusion technique"""
    ratio_low = min(RATIO_RANGES[0])  # ; print ratio_low
    ratio_high = min(RATIO_RANGES[-1]) + 0.5  # ; print ratio_high
    ratio_width = ratio_high - ratio_low  # ; print ratio_width
    ratio_random = round(random.random() * ratio_width + ratio_low, 1)
    return ratio_random


if __name__ == "__main__":  # reusable module and stand-alone
    print random_ratio()
