# required librairies
import random
import kernel

# Globals --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
from constants import RATIO_RANGES, KERNEL_SIZES, CENTER_CELL, CENTER_CELL_2

# Combine -- What for?
MATRIX_PROPERTIES = zip ( RATIO_RANGES, KERNEL_SIZES )

print
print "--- -- User Independent Variables - ---"
print

# 1. Ratio ------------------------------------------------------------------

### Simulate user input
ratio_low = min(RATIO_RANGES[0]) #; print ratio_low
ratio_high = min(RATIO_RANGES[-1]) + 0.5 #; print ratio_high
ratio_width = ratio_high - ratio_low #; print ratio_width
ratio_random = round ( random.random() * ratio_width + ratio_low, 1)
print "Ratio (Random):", ratio_random


# 2. Kernel size ------------------------------------------------------------

hpfk1 = Kernel(5,33)
kernel_size = hpfk1.size
print "Kernel Size: ", kernel_size

print
print "--- --- - Simulate User Input - --- ---"
print


# 3. Center Cell Level ------------------------------------------------------

# center cell level
center_cell_level = random.choice(CENTER_CELL.keys())
print "Center cell level:", center_cell_level#, "| Values:", CENTER_CELL[center_cell_level]
print

# request second pass?
second_pass = random.choice([bool(0), bool(1)])

# simulate request or recommendation for 2nd pass
def second_hpf_matrix(ratio_random, second_pass):
    '''
    Simulate request or recommended application of 2nd High Pass Filter
    ''' 
    
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


# center cell level for 2nd pass
second_hpf_matrix(ratio_random, second_pass)

## select kernel size & co


## function to select kernel size
#kernel_size = kernel_size(ratio_random)

# position -- use to retrieve center cell value
kernel_index = KERNEL_SIZES.index(kernel_size)
#print "Index", kernel_index

center_cell = (CENTER_CELL[center_cell_level])[kernel_index]
print "Center cell value: ", center_cell

center_cell_2 = (CENTER_CELL_2[center_cell_level_2])
print "Center cell value 2: ", center_cell_2




print
print "--- --- --- --- --- --- --- --- --- ---"
print


# construct rows for kernel
def hpf_kernel(kernel_size, center_cell):
    
    # loop over columns, return value for column, row
    for column in range(kernel_size):
        
        # middle row
        middle_row = (kernel_size/2)
        # then return the center cell value!
        if column == kernel_size/2:
            print "-1 " * middle_row, center_cell, "-1 " * middle_row
        else:
            print "-1 " * kernel_size

# build a kernel
def hpf_matrix(kernel_size, center_cell):
    '''
    Function that builds an (Kernel Size)^2 matrix. Example output:

     MATRIX   5
     -1 -1 -1 -1 -1
     -1 -1 -1 -1 -1
     -1 -1 $(echo ${!Center_Cell}) -1 -1
     -1 -1 -1 -1 -1
     -1 -1 -1 -1 -1
     DIVISOR   1
     TYPE      P
    '''
    
    # header
    print "MATRIX   ", kernel_size
    
    # kernel
    hpf_kernel(kernel_size, center_cell)
    
    # footer
    print "DIVISOR   1"
    print "TYPE      P"


# High Pass Filter Matrix
print "High Pass Filter Matrix"
print
hpf_matrix(kernel_size, center_cell)
print


# 2nd High Pass Filter Matrix
if ratio_random > 6 or second_pass == bool(1):
    print "2nd High Pass Filter Matrix (recommended for Ratio > 6)"
    print
    hpf_matrix(5, center_cell_2)