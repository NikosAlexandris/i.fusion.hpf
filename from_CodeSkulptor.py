# required librairies
import random


# Globals --- --- --- --- --- --- --- --- --- ---

# Resolution Ratio
RATIO_RANGES = ((1, 2.5),\
          (2.5, 3.5),\
          (3.5, 5.5),\
          (5.5, 7.5),\
          (7.5, 9.5),\
          (9.5, float("inf"))) # tuple? maybe list?

# Kernel Size, depends on Resolution Ratio
KERNEL_SIZES = (5, 7, 9, 11, 13, 15) # tuple or list?


# Center Value, , depends on Resolution Ratio
CENTER_CELL = {
    'Default' : [ 24, 48, 80, 120, 168, 336 ], \
    'Mid' : [ 28, 56, 96, 150, 210, 392 ], \
    'High' : [ 32, 64, 106, 180, 252, 448 ], \
    }

CENTER_CELL_2 = { # values for 2nd pass
    'Default': 24, \
    'Mid': 28, \
    'High': 32 
    }

# Modulation Factor, depends on Resolution Ratio
MODULATOR = {
    'Min': [ 0.20, 0.35, 0.35, 0.50, 0.65, 1.00], \
    'Default': [ 0.25, 0.50, 0.50, 0.65, 1.00, 1.35], \
    'Max': [ 0.30, 0.65, 0.65, 1.00, 1.40, 2.00]
    }

MODULATOR_2 = {
    'Min 2': 0.25, \
    'Default 2': 0.35, \
    'Max 2': 0.50
    }


# Combine -- What for?
MATRIX_PROPERTIES = zip ( RATIO_RANGES, KERNEL_SIZES )
print "Matrix Properties:", MATRIX_PROPERTIES
#print

print
print "--- --- - Simulate User Input - --- ---"
print


### Simulate user input ###
ratio_low = min(RATIO_RANGES[0]) #; print ratio_low
ratio_high = min(RATIO_RANGES[-1]) + 0.5 #; print ratio_high
ratio_width = ratio_high - ratio_low #; print ratio_width
ratio_random = round ( random.random() * ratio_width + ratio_low, 1)
print "Ratio (Random):", ratio_random

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


# select kernel size & co
kernel_index = 0
if 1 <= ratio_random < 2.5:
    kernel_size = 5    
elif 2.5 <= ratio_random < 3.5:
    kernel_size = 7
elif 3.5 <= ratio_random < 5.5:
    kernel_size = 9
elif 5.5 <= ratio_random < 7.5:
    kernel_size = 11
elif 7.5 <= ratio_random < 9.5:
    kernel_size = 13
elif 9.5 <= ratio_random:
    kernel_size = 15
print "Kernel size:", kernel_size#, "[ Type:", type(kernel_size), "]"


# position -- use to retrieve center cell value
kernel_index = KERNEL_SIZES.index(kernel_size)
#print "Index", kernel_index

center_cell = (CENTER_CELL[center_cell_level])[kernel_index]
print "Center cell value: ", center_cell

center_cell_2 = (CENTER_CELL_2[center_cell_level_2])
print "Center cell value 2: ", center_cell_2


## desired output
#print
#print "Desired output (following is hard-coded):"
#print
#print "MATRIX    5"
#print "-1 " * 5 #print "-1 -1 -1 -1 -1"
#print "-1 " * 5 #print "-1 -1 -1 -1 -1"
#print "-1 -1 ", center_cell, "-1 -1"
#print "-1 " * 5 #print "-1 -1 -1 -1 -1"
#print "-1 " * 5 #print "-1 -1 -1 -1 -1"
#print "DIVISOR   1"
#print "TYPE      P"

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
    
    
    

print
print "--- --- --- --- --- --- --- --- --- ---"
print

# By Anonymous
print "Solution by Anonymous"
print

# Sort list of tuples by the first float.
ratios = list(RATIO_RANGES) ### already sorted!
ratios[5] = (9.5, 999) ### modified!
print "List of ranges:"
print ratios ; print

# Ratio of in question
print "Resolution Ratio ="
print ratio_random ; print

# binary search function, by Anonymous
def kernel_selection(ratio_random):
    
    # Set two integer indices to zero and the length of the list.
    i = 0 ; j = len(ratios) #; print i, j

    # zero the variable of interest
    kernel_size = 0
    
    # while the kernel is zero
    while kernel_size == 0:
        
        # do/repeat: check middle range
          # the one in the middle of the indices!
        print ratios[(i+j)/2][0], "<=", ratio_random, "<", ratios[(i+j)/2][1], "| True?"
        if ratios[(i+j)/2][0] <= ratio_random < ratios[(i+j)/2][1]:
            kernel_size = KERNEL_SIZES[(i+j)/2]
            print "Yes, kernel size set to", kernel_size
            
        # if target is lower, set higher index to current
        elif ratio_random < ratios[(i+j)/2][0]:
            print "No"; print
            j = (i+j)/2
            
        # if target is higher, set lower index to current
        elif ratio_random >= ratios[(i+j)/2][1]:
            print "No"; print
            i = (i+j)/2

kernel_selection(ratio_random)

print
print "--- --- --- --- --- --- --- --- --- ---"
print

print "Solution by Ranjith"


t = [\
     [ (  1, 2.5), 5 ],\
     [ (2.5, 3.5), 7 ],\
     [ (3.5, 5.5), 9 ],\
     [ (5.5, 7.5), 11],\
     [ (7.5, 9.5), 13],\
     [ (9.5, float("inf")), 15]\
    ]

def kernel_selection_R(ratio_random):
    kernel_size = 0
    for l in MATRIX_PROPERTIES:
        if l[0][0] <= ratio_random < l[0][1]:
            kernel_size = l[1]
    print "Kernel size set to", str(kernel_size)

kernel_selection_R(ratio_random)