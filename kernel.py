# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 22:22:20 2014

@author: nik
"""

import os
import random
from random_ratio import main as ratio_random
from constants import RATIO_RANGES, KERNEL_SIZES, CENTER_CELL, MATRIX_PROPERTIES


# random ratio

# kernel size
def kernel_size(ratio):
        """Kernel size based on resolution ratio"""
        kernel_size = [ks for ((lo, hi), ks) in MATRIX_PROPERTIES
                            if lo <= ratio < hi]
        return kernel_size[0]

# request second pass?
second_pass = random.choice([bool(0), bool(1)])


class Kernel:
    """Kernel of size n^2, where n is odd"""
    def __init__(self, size, center=333):
        if size % 2 != 0:
            self.size = size
        else:
            raise ValueError("Parameter <size> should be an odd number!")
        self.center = center
        self.kernel = ''
        
        # loop over columns, return value for column, row
        for row in range(self.size):

            # middle row
            midrow = (self.size/2)
            
            # fill rows
            if row != self.size/2:
                self.kernel += "-1 " * self.size + "\n"
            else:
                if len(str(self.center)) == 1:
                    self.center = " " + str(self.center) + " "
                self.kernel += "-1 " * midrow + str(self.center) + " " + "-1 " * midrow + "\n"
        
        # remove line trailing whitespaces
        self.kernel = os.linesep.join([s.rstrip() for s in self.kernel.splitlines() if s])

    def size(self):
        return self.size

    def center(self):
        return self.center

    def __str__(self):
        return "Kernel:\n" + str(self.kernel)
#
#print Kernel(3, 3)
#print Kernel(5, 66)
#print Kernel(4, 44)