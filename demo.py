# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 14:52:49 2014

@author: nik
"""

# 1. get a random ratio
ratio = ratio_random() ; print "1. Random Ratio:", ratio

# 2. select kernel size
kernel_size = kernel_size(ratio) ; print "2. Kernel size:", kernel_size

# 3. select center cell value
kernel_index = KERNEL_SIZES.index(kernel_size)  # retrieve center cell
center_cell_level = random.choice(CENTER_CELL.keys()) ; print "2a. Center cell level:", center_cell_level
center_cell = (CENTER_CELL[center_cell_level])[kernel_index] ; print "2b. Center cell value: ", center_cell

# demo
print "--------------------------"
print Kernel(kernel_size, center_cell)