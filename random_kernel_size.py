#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Nikos Alexandris | Trikala, October 2014

from random_ratio import random_ratio
from constants import MATRIX_PROPERTIES


def kernel_size():
    """High Pass Filter Additive image fusion compatible kernel size.
    Based on a random ratio float ranging in (1.0, 10.0).
    Returns a single integer"""
    rr = random_ratio()
    ks = [k for ((lo, hi), k) in MATRIX_PROPERTIES if lo <= rr < hi]
    return ks[0]


# reusable & stand-alone
if __name__ == "__main__":
    print kernel_size()
