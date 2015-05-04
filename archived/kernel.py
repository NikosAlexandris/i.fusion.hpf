#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on Thu Oct 30 22:22:20 2014

@author: nik
"""

import os


class Kernel:
    """
    HPF compatible Kernel (size, center),
    where size is odd | Returns multi-line string
    """
    def __init__(self, size, center):
        """
        Initialise an HPF compatible kernel based on given size and a value for
        its center.
        """
        if size % 2 != 0 and 5 <= size <= 15:
            self.size = int(size)
        else:
            raise ValueError("""Size should be one of the following odd
            numbers: 5, 7, 9, 11, 13 or 15""")
        self.center = center
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
        """
        Return the size of the kernel.
        """
        return self.size

    def center(self):
        """
        Return the center value of the kernel
        """
        return self.center

    def __str__(self):
        """
        Return a string representation of the kernel.
        """
        return "Kernel:\n" + self.kernel
