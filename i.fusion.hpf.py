
# Converting i.fusion.hpf.sh into Python

### Notes:

  # Everythin between ### and ### is bash code!
  # Take a good look at: <http://stackoverflow.com/a/2840338/1172302>


# Required Librairies

import random


# Globals --- --- --- --- --- --- --- --- --- ---

# Kernel Size, Center Value & Modulation Factor,
  # depend on Resolution Ratio
RATIO_RANGES = ((1, 2.5),\
          (2.5, 3.5),\
          (3.5, 5.5),\
          (5.5, 7.5),\
          (7.5, 9.5),\
          (9.5)) # tuple? maybe list?



KERNEL_SIZES = (5, 7, 9, 11, 13, 15) # tuple?
## KERNEL_SIZES
#print "loop over KERNEL_SIZES"
#for size in KERNEL_SIZES:
#    print size
#print


CENTER_CELL = {
    'Default' : [24, 48, 80, 120, 168, 336 ], \
    'Default 2':'24', \
    'Mid' : [ 28, 56, 96, 150, 210, 392 ], \
    'Mid 2':'28', \
    'High' : [ 32, 64, 106, 180, 252, 448 ], \
    'High 2':'32'
    } # dictionary?
#print center_cell_level, "Center cell values:", CENTER_CELL[center_cell_level]
#print


# combine!
MATRIX_PROPERTIES = zip ( RATIO_RANGES, KERNEL_SIZES )
#print "Matrix Properties:", MATRIX_PROPERTIES
#print


## print-out:
#for ratio, kernel in MATRIX_PROPERTIES:
#    print "Ratio:", ratio, "Kernel Size: ", kernel


print
print "--- --- --- --- --- --- --- --- --- ---"
print



# Helper functions -----------------------------------------------------------

# required librairies
import random

# Some user input
center_cell_level = "Default"





# Example output

#   HPF_MATRIX=\
# "MATRIX    5
# -1 -1 -1 -1 -1
# -1 -1 -1 -1 -1
# -1 -1 $(echo ${!Center_Cell}) -1 -1
# -1 -1 -1 -1 -1
# -1 -1 -1 -1 -1
# DIVISOR   1
# TYPE      P"

ratio_low = min(RATIO_RANGES[0]) #; print ratio_low
ratio_high = RATIO_RANGES[-1] + 0.5 #; print ratio_high
ratio_width = ratio_high - ratio_low
ratio_random = round ( random.random() * ratio_width + ratio_low, 1)
print "Ratio (Random):", ratio_random


# select kernel size & co
kernel_index = 0
if 1 <= ratio_random < 2.5:
#    global kernel_index
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
print "Kernel size:", kernel_size
kernel_index = KERNEL_SIZES.index(kernel_size)
print "Index", kernel_index

# center cell value
center_cell_level = random.choice(CENTER_CELL.keys())
print "Center cell level:", center_cell_level

center_cell = CENTER_CELL[center_cell_level][kernel_index]
print "Center cell value: ", center_cell

## desired output
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

def hpf_row(kernel_size):
    
    # loop over columns and return row,col value
    for column in range(kernel_size):
        central_row = (kernel_size/2)
        #pseudo-code:
        # if the number of column is half of the matrix' dimension,
        ## then return the center cell value!
        if column == kernel_size/2:
            print "-1 " * central_row, center_cell, "-1 " * central_row
        else:
            print "-1 " * kernel_size
    
print "Example of hpf_row() function"
print

print hpf_row(kernel_size)


# clean up Temporary files ###################################################
function cleantemp {
\rm -f i.fusion.hpf.tmp.*
g.mremove rast=i.fusion.hpf.tmp* -f
}
##############################################################################


# what to do in case of user break: ##########################################
function exitprocedure {
  g.message -e message='User break!'
  cleanup
  exit 1
}
##############################################################################


# a High Pass Filter Matrix (of Matrix_Dimension^2) Constructor ##############
function hpf_matrix {

  # Positional Parameters
  eval Matrix_Dimension="${1}"
  eval Center_Cell_Value="${2}"

  # Define the cell value(s)
  function hpf_cell_value {
    if (( ${Row} == ${Column} )) && (( ${Column} == `echo "( ${Matrix_Dimension} + 1 ) / 2" | bc` ))
      then echo "${Center_Cell_Value} "
      else echo "-1 "
    fi
  }

  # Construct the Row for Cols 1 to "Matrix_Dimension"
  function hpf_row {
    for Column in `seq $Matrix_Dimension`
      do echo -n "$(hpf_cell_value)"
    done
  }

  # Construct the Matrix
  echo "MATRIX    $Matrix_Dimension"
  for Row in `seq $Matrix_Dimension`
    do echo "$(hpf_row)"
  done
  echo "DIVISOR   1"
  echo "TYPE      P"
}
##############################################################################


### Example output for the above *should* be like: ###########################
  # Default will be:
                      #   HPF_MATRIX=\
                      # "MATRIX    5
                      # -1 -1 -1 -1 -1
                      # -1 -1 -1 -1 -1
                      # -1 -1 $(echo ${!Center_Cell}) -1 -1
                      # -1 -1 -1 -1 -1
                      # -1 -1 -1 -1 -1
                      # DIVISOR   1
                      # TYPE      P"
##############################################################################


# Event handlers

# Frame creation

# Launch
