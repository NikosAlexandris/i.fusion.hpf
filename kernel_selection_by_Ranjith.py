#
# Function to select kernel size depending of resolution ratio
#

# provided by Ranjith, 26 Oct. 2014-------------------------------------------
  # <https://class.coursera.org/interactivepython-005/forum/profile?user_id=9361576>
# ----------------------------------------------------------------------------

# requires librairies
import random

# Resolution Ratio
RATIO_RANGES = ((1, 2.5),\
          (2.5, 3.5),\
          (3.5, 5.5),\
          (5.5, 7.5),\
          (7.5, 9.5),\
          (9.5, float("inf"))) # <http://stackoverflow.com/q/7781260/1172302>

# Kernel Size, depends on Resolution Ratio
KERNEL_SIZES = (5, 7, 9, 11, 13, 15)

# zip'em
MATRIX_PROPERTIES = zip ( RATIO_RANGES, KERNEL_SIZES )

### Simulate user input ###
ratio_low = min(RATIO_RANGES[0]) #; print ratio_low
ratio_high = min(RATIO_RANGES[-1]) + 0.5 #; print ratio_high
ratio_width = ratio_high - ratio_low #; print ratio_width
ratio_random = round ( random.random() * ratio_width + ratio_low, 1)
print "Ratio (Random):", ratio_random

# function to select kernel size
def kernel_selection_R(ratio_random):
    kernel_size = 0
    for l in MATRIX_PROPERTIES:
        if l[0][0] <= ratio_random < l[0][1]:
            kernel_size = l[1]
    print "Kernel size set to", str(kernel_size)

# demo
kernel_selection_R(ratio_random)
