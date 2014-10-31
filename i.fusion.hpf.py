# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 20:03:06 2014

@author: nik
"""

############################################################################
#
# MODULE:       i.fusion.hpf
#
# AUTHOR(S):    Nikos Alexandris <nik@nikosalexandris.net>
#               Based on the bash shell script i.fusion.hpf
#
#
# PURPOSE:      HPF Resolution Merge -- Algorithm Replication in GRASS GIS
#
#               Module to combine high-resolution panchromatic data with
#               lower resolution multispectral data, resulting in an output
#               with both excellent detail and a realistic representation of
#               original multispectral scene colors.
#
# 				 The process involves a convolution using a High Pass Filter
# 				 (HPF) on the high resolution data, then combining this with
# 				 the lower resolution multispectral data.
#
#               Optionally, a linear histogram matching technique is performed
#               in a  way that matches the resulting Pan-Sharpened imaged to
#               them statistical mean and standard deviation of the original
#               multi-spectral image. Credits for how to implement this
#               technique go to GRASS-GIS developer Moritz Lennert.
#
#               Source: "Optimizing the High-Pass Filter Addition Technique for
#               Image Fusion", Ute G. Gangkofner, Pushkar S. Pradhan,
#               and Derrold W. Holcomb (2008)
#
# COPYRIGHT:    (C) 2013 by the GRASS Development Team
#
#               This program is free software under the GNU General Public
#               License (>=v2). Read the file COPYING that comes with GRASS
#               for details.
#
#############################################################################

#%Module
#%  description: Fuses a High-Resolution Panchromatic with its corresponding Low Resolution Multi-Spectral image based on the High-Pass Filter Addition technique
#%  keywords: imagery, fusion, HPF, HPFA
#%End
#%flag
#%  key: l
#%  description: Linearly match histograms of the HPF Pan-sharpened output(s) to the Multi-Spectral input(s)
#%end
#%flag
#%  key: 2
#%  description: 2-Pass Processing (recommended) for large Resolution Ratio (>=5.5)
#%end
#%option
#% key: pan
#% type: string
#% gisprompt: old,double,raster
#% description: High resolution panchromatic image
#% required : yes
#%end
#%option
#% key: msx
#% type: string
#% gisprompt: old,double,raster
#% description: Low resolution multi-spectral image(s)
#% required: yes
#% multiple: yes
#%end
#%option
#% key: outputprefix
#% type: string
#% gisprompt: old,double,raster
#% description: Prefix for the Pan-Sharpened Multi-Spectral image(s)
#% required: yes
#% answer: hpf
#%end
#%option
#% key: ratio
#% type: double
#% description: Custom defined ratio to override standard calculation 
#% options: 1-10
#% guisection: High Pass Filter Options
#% required: no
#%end
#%option
#% key: center
#% type: string
#% description: Center cell value of the High-Pass-Filter 
#% descriptions: Level of center value (low, mid, high)
#% options: low,mid,high
#% required: no
#% answer: low
#% guisection: High Pass Filter Options
#% multiple : no
#%end
#%option
#% key: center2
#% type: string
#% description: Center cell value for the second pass of the High-Pass-Filter 
#% descriptions: Level of center value for second pass
#% options: low,mid,high
#% required: no
#% answer: low
#% guisection: High Pass Filter Options
#% multiple : no
#%end
#%option
#% key: modulator
#% type: string
#% description: Level of modulating factor weighting the HPF image to determine crispness
#% descriptions: Levels of modulating factors
#% options: min,mid,max
#% required: no
#% answer: mid
#% guisection: High Pass Filter Options
#% multiple : no
#%end
#%option
#% key: modulator2
#% type: string
#% description: Level of modulating factor weighting the HPF image in the second pass to determine crispness
#% descriptions: mid;Mid modulating factor (0.35) for the 2nd pass;min;Minimum modulating factor (0.25) for the 2nd pass;max;Maximum modulating factor (0.5) for 2nd pass;
#% options: min,mid,max
#% required: no
#% answer: mid
#% guisection: High Pass Filter Options
#% multiple : no
#%end

from grass.pygrass.modules.shortcuts import raster as r, vector as v, general as g, display as d
from grass.pygrass.modules import Module
from grass.script import core as grass


# get resolution first
def main():
    pan = options['pan']
    msx = options['msx']
    outputprefix = options['outputprefix']
    center = options['center']
    center2 = options['center2']
    modulator = options['modulator']
    modulator2 = options['modulator2']
    full = flags['l']
    preserve = flags['2']
    
# resolution of msx
    msxinfo = r.info(msx, quiet = True)
#    print msxinfo
    
if __name__ == "__main__":
    options, flags = grass.parser()
    main()
