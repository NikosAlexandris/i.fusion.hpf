# required librairies
import random
from random_ratio import random_ratio
from random_kernel_size import kernel_size
from kernel import Kernel
from filter import Filter

# Globals --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
from constants import RATIO_RANGES, KERNEL_SIZES, CENTER_CELL, CENTER_CELL_2


# Helper functions

# simulate request or recommendation for 2nd pass
def second_hpf_matrix(ratio_random, second_pass):
    """Simulate request or recommended application of 2nd High Pass Filter""" 
    
    # global
    global center_cell_level_2
    
    # if ratio > 6
    if ratio_random > 6:
        print "Resolution Ratio > 6 | 2nd pass recommended"

    # 2nd pass requested?
    if ratio_random < 6 and second_pass:
        print "Second Pass Requested:", second_pass
    center_cell_level_2 = random.choice(CENTER_CELL_2.keys())

    # inform
    print "Center cell level 2:", center_cell_level_2


print
print "--- -- User Independent Variables - ---"
print

# Ratio ------------------------------------------------------------------
ratio_random = random_ratio()
print "Ratio (Random):", ratio_random


# Kernel size ------------------------------------------------------------
kernel_size = kernel_size()
print "Kernel Size: ", kernel_size

# idx
kernel_index = KERNEL_SIZES.index(kernel_size)
print "(Index to retrieve center cell value: ", kernel_index, ")"

print
print "--- --- - Simulate User Input - --- ---"
print


# Center Cell ------------------------------------------------------------
center_cell_level = random.choice(CENTER_CELL.keys())
print "Center cell level:", center_cell_level, "| Values:", CENTER_CELL[center_cell_level]
center_cell = (CENTER_CELL[center_cell_level])[kernel_index]
print "Center cell value: ", center_cell
print

# 4. Second Pass ------------------------------------------------------------

# request second pass?
second_pass = random.choice([bool(0), bool(1)])
#print "Second Pass: ", second_pass
second_hpf_matrix(ratio_random, second_pass)
center_cell_2 = (CENTER_CELL_2[center_cell_level_2])
print "Center cell value 2: ", center_cell_2


kernel = Kernel(kernel_size, center_cell)

print
print "--- --- --- --- --- --- --- --- --- ---"
print


# High Pass Filter Matrix ---------------------------------------------------
print "High Pass Filter Matrix"
print
print Filter(kernel, center_cell).filter

print
print "--- --- --- --- --- --- --- --- --- ---"
print

# 2nd High Pass Filter Matrix -----------------------------------------------
if ratio_random > 6 or second_pass == bool(1):
    print "2nd High Pass Filter Matrix (recommended for Ratio > 6)"
    print
    k2 = Kernel(5, center_cell_2)
    print Filter(k2, center_cell_2).filter