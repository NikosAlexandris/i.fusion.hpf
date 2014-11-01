#
# Function to select kernel size depending of resolution ratio
#

# suggested by Anoynmous, 26 Oct. 2014 --------------------------------------
# ---------------------------------------------------------------------------

# requires librairies
import random

# Resolution Ratio
#   source for use of "inf": <http://stackoverflow.com/q/7781260/1172302>
RATIO_RANGES = ((1, 2.5),
                (2.5, 3.5),
                (3.5, 5.5),
                (5.5, 7.5),
                (7.5, 9.5),
                (9.5, float("inf")))

# Kernel Size, depends on Resolution Ratio
KERNEL_SIZES = (5, 7, 9, 11, 13, 15)


# Simulate user input
ratio_low = min(RATIO_RANGES[0])  # ; print ratio_low
ratio_high = min(RATIO_RANGES[-1]) + 0.5  # ; print ratio_high
ratio_width = ratio_high - ratio_low  # ; print ratio_width
ratio_random = round(random.random() * ratio_width + ratio_low, 1)
print "Ratio (Random):", ratio_random

# copy list of ratio ranges
ratios = list(RATIO_RANGES)


def kernel_selection(ratio_random):
    """Implementation of a binary search function,
    suggested by an Anonymous in a Coursera discussion forum."""

    # Set two integer indices to zero and the length of the list.
    i = 0
    j = len(ratios)  # ; print i, j

    # zero the variable of interest
    kernel_size = 0

    # while the kernel is zero
    while kernel_size == 0:

        # do/repeat: check middle range (pointed by mid of indices!)
        print ratios[(i+j)/2][0], "<=", \
            ratio_random, \
            "<", ratios[(i+j)/2][1], "| True?"
        if ratios[(i+j)/2][0] <= ratio_random < ratios[(i+j)/2][1]:
            kernel_size = KERNEL_SIZES[(i+j)/2]
            print "Yes, kernel size set to", kernel_size

        # if target is lower, set higher index to current
        elif ratio_random < ratios[(i+j)/2][0]:
            print "No"
            print
            j = (i+j)/2

        # if target is higher, set lower index to current
        elif ratio_random >= ratios[(i+j)/2][1]:
            print "No"
            print
            i = (i+j)/2

# demo
kernel_selection(ratio_random)
